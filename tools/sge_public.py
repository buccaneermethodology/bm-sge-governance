#!/usr/bin/env python3
"""Default-deny public projection and reversible lifecycle checks.

The export path is deliberately maintainer-only.  It copies only the exact
manifest file set into a fresh destination and records enough local identity
and digest evidence to be recomputed later.  It does not create a Git commit,
tag, release, or remote repository.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "public_export_manifest_v1.json"
METADATA_NAME = "EXPORT_METADATA.json"
CORE_SKILL_PREFIX = ".codex/skills/sge-governed-checkpoints/"
INSTALL_RECORD_NAME = ".sge-governance-install.json"
BACKUP_ROOT_NAME = ".sge-backups"
TRASH_ROOT_NAME = ".sge-trash"

_ABSOLUTE_PRIVATE_PATH = re.compile(
    r"(?:^|[\s\"'`(])/(?:Users|home|private/var)/[^\s\"'`)]*"
    r"|(?:^|[\s\"'`(])[A-Za-z]:[\\/][^\s\"'`)]*"
    r"|file://(?:/|[A-Za-z]:)",
    re.IGNORECASE,
)
_PRIVATE_CREDENTIAL = re.compile(
    r"-----BEGIN\s+(?:RSA\s+|OPENSSH\s+|EC\s+|DSA\s+)?PRIVATE KEY-----"
    r"|\b(?:ghp|github_pat|xox[baprs]|sk)-[A-Za-z0-9_-]{16,}\b"
    r"|\b(?:aws_secret_access_key|client_secret)\s*[:=]\s*['\"][^'\"]+",
    re.IGNORECASE,
)
_LFS_POINTER = re.compile(
    rb"^version https://git-lfs\.github\.com/spec/v1\s*\n"
    rb"(?:oid sha256:[0-9a-f]{64}\s*\n)"
    rb"(?:size [0-9]+\s*\n)?$",
)


def _fail(code: str, detail: str | None = None) -> None:
    raise SystemExit(code if detail is None else f"{code}:{detail}")


def _root(value: Path | str | None) -> Path:
    return Path(value) if value is not None else ROOT


def _manifest_path(source_root: Path) -> Path:
    return source_root / "public_export_manifest_v1.json"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError as exc:
        _fail("source_read_error", f"{path}:{exc}")


def _safe_relative(path_value: Any, label: str = "path") -> str:
    if not isinstance(path_value, str) or not path_value or "\x00" in path_value:
        _fail("manifest_path_invalid", str(path_value))
    # Manifest paths are portable POSIX paths.  Backslashes are rejected so a
    # Windows path cannot become a different path on another host.
    if "\\" in path_value or path_value.startswith("/") or re.match(r"^[A-Za-z]:", path_value):
        _fail("manifest_path_invalid", path_value)
    pure = PurePosixPath(path_value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        _fail("manifest_path_invalid", path_value)
    normalized = pure.as_posix()
    if normalized != path_value:
        _fail("manifest_path_invalid", path_value)
    return normalized


_SKILL_PREFIX = ".codex/skills/sge-governed-checkpoints/"
_RUNTIME_PATH = re.compile(
    r"(?<![A-Za-z0-9_.-])((?:\.\./|\./)*(?:(?:\.codex/skills/sge-governed-checkpoints/)?(?:references|scripts|schemas|fixtures|agents)/)[A-Za-z0-9_./-]+\.(?:md|json|py|ya?ml))"
)


def _resolve_skill_ref(skill_root: Path, source: Path, token: str) -> Path | None:
    clean = token.split("#", 1)[0].strip("`'\"()[]{}<>,:;")
    if clean.startswith(_SKILL_PREFIX):
        candidate = skill_root / clean[len(_SKILL_PREFIX):]
    elif clean.startswith(("./", "../")):
        candidate = source.parent / clean
    elif clean.startswith(("references/", "scripts/", "schemas/", "fixtures/", "agents/")):
        candidate = skill_root / clean
    else:
        return None
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(skill_root.resolve())
    except (OSError, ValueError):
        _fail("skill_runtime_reference_escape", f"{source}:{token}")
    return resolved


def _version_literals(path: Path) -> set[str]:
    if path.suffix != ".py":
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        _fail("skill_runtime_python_invalid", f"{path}:{exc}")
    versions: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(isinstance(target, ast.Name) and "VERSION" in target.id for target in targets):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                versions.add(node.value.value)
    return versions


def skill_runtime_closure(source_root: Path | str) -> list[str]:
    root = _root(source_root).resolve()
    skill_root = root / _SKILL_PREFIX.rstrip("/")
    start = skill_root / "SKILL.md"
    if not start.is_file():
        _fail("skill_runtime_root_missing", _SKILL_PREFIX + "SKILL.md")
    schemas = sorted((skill_root / "schemas").glob("*.json")) if (skill_root / "schemas").is_dir() else []
    queue = [start]
    visited: set[Path] = set()
    while queue:
        current = queue.pop(0).resolve()
        if current in visited:
            continue
        if not current.is_file():
            _fail("skill_runtime_reference_missing", current.relative_to(root).as_posix())
        visited.add(current)
        try:
            text = current.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            _fail("skill_runtime_reference_invalid", f"{current}:{exc}")
        tokens = set(_RUNTIME_PATH.findall(text))
        if current.suffix == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                _fail("skill_runtime_json_invalid", f"{current}:{exc}")
            stack = [payload]
            while stack:
                value = stack.pop()
                if isinstance(value, dict):
                    stack.extend(value.values())
                elif isinstance(value, list):
                    stack.extend(value)
                elif isinstance(value, str):
                    tokens.update(_RUNTIME_PATH.findall(value))
        for token in sorted(tokens):
            resolved = _resolve_skill_ref(skill_root, current, token)
            if resolved is not None and resolved not in visited:
                queue.append(resolved)
        versions = _version_literals(current)
        for schema in schemas:
            if any(version in schema.read_text(encoding="utf-8") for version in versions):
                queue.append(schema.resolve())
    return sorted(path.relative_to(root).as_posix() for path in visited)


def _validate_skill_runtime_closure(data: dict[str, Any], source_root: Path, allowlisted: set[str]) -> None:
    contract = data.get("skill_runtime_closure")
    if not isinstance(contract, dict):
        _fail("skill_runtime_closure_contract_missing")
    if contract.get("roots") != [_SKILL_PREFIX + "SKILL.md"]:
        _fail("skill_runtime_closure_roots_invalid")
    declared = contract.get("files")
    if not isinstance(declared, list) or not declared or declared != sorted(set(declared)):
        _fail("skill_runtime_closure_files_invalid")
    recomputed = skill_runtime_closure(source_root)
    if declared != recomputed:
        _fail("skill_runtime_closure_drift", json.dumps({"missing": sorted(set(recomputed) - set(declared)), "extra": sorted(set(declared) - set(recomputed))}, sort_keys=True))
    runtime = set(data.get("runtime_dependencies", []))
    for path in recomputed:
        if path not in allowlisted:
            _fail("skill_runtime_allowlist_missing", path)
        if path not in runtime:
            _fail("skill_runtime_dependency_missing", path)


def _lstat(path: Path, failure: str = "source_object_invalid") -> os.stat_result:
    try:
        return path.lstat()
    except FileNotFoundError:
        _fail("source_missing", path.as_posix())
    except OSError as exc:
        _fail(failure, f"{path}:{exc}")
    raise AssertionError("unreachable")


def _assert_inside(root: Path, child: Path, code: str) -> None:
    try:
        child.relative_to(root)
    except ValueError:
        _fail(code, child.as_posix())


def _safe_source_file(source_root: Path, relative: str) -> Path:
    current = source_root
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        current = current / part
        info = _lstat(current)
        if stat.S_ISLNK(info.st_mode):
            _fail("unsafe_link_or_path_escape", relative)
        if index < len(parts) - 1 and not stat.S_ISDIR(info.st_mode):
            _fail("source_object_invalid", relative)
        if index == len(parts) - 1 and not stat.S_ISREG(info.st_mode):
            _fail("source_object_invalid", relative)
    resolved_root = source_root.resolve()
    resolved = current.resolve()
    _assert_inside(resolved_root, resolved, "unsafe_link_or_path_escape")
    return current


def _git(source_root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(source_root), *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _git_status(source_root: Path) -> list[str]:
    output = _git(source_root, "status", "--porcelain=v1", "--untracked-files=all")
    return [] if output is None else [line for line in output.splitlines() if line]


def _gitlink_paths(source_root: Path) -> set[str]:
    output = _git(source_root, "ls-files", "-s", "--full-name")
    if not output:
        return set()
    found: set[str] = set()
    for line in output.splitlines():
        fields = line.split(maxsplit=3)
        if len(fields) == 4 and fields[0] == "160000":
            found.add(fields[3])
    return found


def _is_binary(data: bytes) -> bool:
    if b"\x00" in data:
        return True
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def _content_failure(data: bytes) -> str | None:
    if _is_binary(data):
        return "unexpected_binary"
    if data.startswith(b"version https://git-lfs.github.com/spec/v1") and _LFS_POINTER.fullmatch(data.strip() + b"\n"):
        return "lfs_pointer_forbidden"
    text = data.decode("utf-8")
    if _ABSOLUTE_PRIVATE_PATH.search(text):
        return "private_identity_or_absolute_path_residue"
    if _PRIVATE_CREDENTIAL.search(text):
        return "credential_residue"
    return None


def _walk_inventory(source_root: Path, allowlisted: set[str]) -> tuple[list[dict[str, Any]], list[str]]:
    """Inventory the visible source tree without following links.

    The root .git directory is source-control metadata and is not part of the
    public tree.  A nested .git is rejected because it can smuggle a second
    repository into a projection input.
    """
    entries: list[dict[str, Any]] = []
    nested_repos: list[str] = []
    stack = [source_root]
    while stack:
        current = stack.pop()
        try:
            children = sorted(os.scandir(current), key=lambda item: item.name, reverse=True)
        except OSError as exc:
            _fail("source_inventory_error", f"{current}:{exc}")
        for item in children:
            rel = Path(item.path).relative_to(source_root).as_posix()
            info = item.stat(follow_symlinks=False)
            mode = info.st_mode
            if stat.S_ISLNK(mode):
                kind = "symlink"
            elif stat.S_ISDIR(mode):
                kind = "directory"
            elif stat.S_ISREG(mode):
                kind = "file"
            else:
                kind = "special"
            is_root_git = rel == ".git"
            if ".git" in PurePosixPath(rel).parts and not is_root_git:
                nested_repos.append(rel)
            entries.append(
                {
                    "path": rel,
                    "kind": kind,
                    "allowlisted": rel in allowlisted,
                    "excluded_reason": (
                        "source_control_metadata" if is_root_git else ("default_deny" if rel not in allowlisted else None)
                    ),
                }
            )
            # A symlink is unsafe even when it is not allowlisted: keeping it
            # in a supposedly fresh projection input would make the source
            # tree non-reproducible and can hide a path escape.
            if kind == "symlink":
                _fail("unsafe_link_or_path_escape", rel)
            if kind == "directory" and not is_root_git:
                stack.append(Path(item.path))
    return sorted(entries, key=lambda entry: entry["path"]), sorted(nested_repos)


def load(source_root: Path | str | None = None) -> dict[str, Any]:
    path = MANIFEST if source_root is None else _manifest_path(_root(source_root))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail("manifest_invalid", str(exc))
    if data.get("schema_version") != "sge_public_export_manifest_v1" or data.get("default_deny") is not True:
        _fail("manifest_invalid")
    return data


def _validate_manifest_shape(data: dict[str, Any], source_root: Path) -> list[dict[str, Any]]:
    if not isinstance(data.get("files"), list) or not data["files"]:
        _fail("manifest_invalid", "files")
    layers = data.get("layer_contract", {})
    if layers.get("install_order") != ["core", "companion", "orchestrator", "domain-extension"]:
        _fail("layer_contract_invalid", "install_order")
    mappings = layers.get("mappings", [])
    if not mappings or mappings[-1].get("prefix") != "":
        _fail("layer_contract_invalid", "catchall")
    allowed_layers = set(layers["install_order"])
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for item in data["files"]:
        if not isinstance(item, dict):
            _fail("manifest_invalid", "file_entry")
        path = _safe_relative(item.get("path"))
        if path in seen:
            _fail("manifest_path_invalid", path)
        seen.add(path)
        if not item.get("public") or item.get("execution_context"):
            _fail("manifest_policy_invalid", path)
        if not item.get("source") or not item.get("provenance"):
            _fail("manifest_provenance_missing", path)
        if item.get("license") != data.get("license"):
            _fail("license_missing", path)
        mapping = next((rule for rule in mappings if path.startswith(rule.get("prefix", ""))), None)
        if not mapping or mapping.get("layer") not in allowed_layers:
            _fail("layer_unresolved", path)
        if mapping["layer"] == "core" and mapping.get("requires"):
            _fail("core_dependency_collapse", path)
        if any(dep not in allowed_layers for dep in mapping.get("requires", [])):
            _fail("layer_dependency_unknown", path)
        normalized.append(item)
    runtime_dependencies = data.get("runtime_dependencies", [])
    stop_gate_required = {
        _SKILL_PREFIX + "scripts/stop_gate.py",
        _SKILL_PREFIX + "schemas/loop_state_v1.schema.json",
        _SKILL_PREFIX + "schemas/stop_gate_receipt_v1.schema.json",
        _SKILL_PREFIX + "requirements.txt",
        _SKILL_PREFIX + "fixtures/stop-gate-v1/smoke.json",
        "tools/stop_gate_smoke.py",
        "kb/data/strategy/strategy_stop_gate_v1.json",
        "kb/docs/strategy/Strategy_Stop_Gate_V1.md",
    }
    # Apply when the exported Skill declares the Stop Gate entry. Minimal test
    # manifests and unrelated packages retain their own closure contracts.
    skill_entry = source_root / (_SKILL_PREFIX + "SKILL.md")
    if skill_entry.is_file() and "scripts/stop_gate.py" in skill_entry.read_text(encoding="utf-8"):
        declared_stop_gate = data.get("stop_gate_runtime_dependencies", [])
        if not isinstance(declared_stop_gate, list) or set(declared_stop_gate) != stop_gate_required:
            _fail("stop_gate_runtime_contract_invalid")
        for dependency in stop_gate_required:
            if dependency not in seen or dependency not in runtime_dependencies:
                _fail("stop_gate_runtime_dependency_missing", dependency)
    if not isinstance(runtime_dependencies, list) or not runtime_dependencies:
        _fail("runtime_dependency_manifest_missing")
    for dependency in runtime_dependencies:
        dependency = _safe_relative(dependency, "runtime_dependency")
        if dependency not in seen:
            _fail("runtime_dependency_missing", dependency)
    hosted_ci = data.get("hosted_ci")
    if not isinstance(hosted_ci, dict):
        _fail("hosted_ci_contract_missing")
    workflow = _safe_relative(hosted_ci.get("workflow"), "hosted_ci_workflow")
    entrypoints = hosted_ci.get("entrypoints")
    if not isinstance(entrypoints, list) or not entrypoints:
        _fail("hosted_ci_contract_invalid", "entrypoints")
    hosted_paths = [workflow, *[_safe_relative(path, "hosted_ci_entrypoint") for path in entrypoints]]
    for path in hosted_paths:
        if path not in seen:
            _fail("hosted_ci_dependency_missing", path)
        if path not in runtime_dependencies:
            _fail("hosted_ci_runtime_dependency_missing", path)
    return normalized


def _validate_boundary_policies(data: dict[str, Any]) -> None:
    identity = data.get("identity_contract")
    if not isinstance(identity, dict):
        _fail("identity_matrix_invalid")
    roles = [identity.get("private_source_id"), identity.get("public_project_id"), identity.get("skill_id"), data.get("candidate_id")]
    if identity.get("roles_must_be_distinct") is not True or any(not isinstance(value, str) or not value for value in roles) or len(set(roles)) != len(roles):
        _fail("identity_matrix_invalid")
    if identity.get("candidate_id_field") != "candidate_id":
        _fail("identity_matrix_invalid")
    locator = data.get("provenance_locator_policy")
    if not isinstance(locator, dict) or set(locator.get("allowed_types", [])) != {"in_package", "external", "private"} or locator.get("relative_private_links") != "forbidden":
        _fail("provenance_locator_policy_invalid")
    residue = data.get("residue_policy")
    classes = set(residue.get("forbidden_active_token_classes", [])) if isinstance(residue, dict) else set()
    if not {"product_cli", "product_kb", "product_audio"}.issubset(classes) or "semx" not in set(residue.get("deny_tokens_are_controls", [])):
        _fail("residue_policy_invalid")


def validate(data: dict[str, Any], source_root: Path | str | None = None) -> set[str]:
    """Validate the manifest and every allowlisted source object.

    Unlisted source files are inventoried and excluded by default-deny.  An
    unlisted private file therefore cannot leak, while an unsafe *allowlisted*
    object fails the export before any destination is written.
    """
    root = _root(source_root)
    if not root.is_dir() or root.is_symlink():
        _fail("source_root_invalid", root.as_posix())
    _validate_boundary_policies(data)
    items = _validate_manifest_shape(data, root)
    allowlisted = {item["path"] for item in items}
    _validate_skill_runtime_closure(data, root, allowlisted)
    inventory, nested_repos = _walk_inventory(root, allowlisted)
    if nested_repos:
        _fail("nested_repo_forbidden", nested_repos[0])
    # The private canonical worktree intentionally contains Dashboard and
    # other execution-only surfaces; default-deny omits them.  A fresh
    # staging/source root has no such private inventory and must reject an
    # unlisted regular file rather than silently treating it as acceptable.
    # The manifest and copied tool are source-control inputs, not projection
    # payloads, and are therefore the only unlisted helper files tolerated in
    # a fixture source root.
    tolerated_source_helpers = {"public_export_manifest_v1.json", "tools/sge_public.py", METADATA_NAME}
    if root != ROOT:
        unknown = [
            entry["path"]
            for entry in inventory
            if entry["kind"] == "file"
            and not entry["allowlisted"]
            and entry["path"] not in tolerated_source_helpers
        ]
        if unknown:
            _fail("unknown_path_default_deny", sorted(unknown)[0])
    gitlinks = _gitlink_paths(root)
    policy = data.get("content_policy", {})
    for item in items:
        path = item["path"]
        if path in gitlinks:
            _fail("gitlink_forbidden", path)
        source = _safe_source_file(root, path)
        raw = source.read_bytes()
        failure = _content_failure(raw)
        if failure:
            if failure == "private_identity_or_absolute_path_residue" and policy.get("reject_absolute_home_paths"):
                _fail("identity_or_private_residue", f"{path}:absolute_home_path")
            _fail(failure, path)
        text = raw.decode("utf-8")
        if policy.get("reject_absolute_home_paths") and _ABSOLUTE_PRIVATE_PATH.search(text):
            _fail("identity_or_private_residue", f"{path}:absolute_home_path")
        if policy.get("reject_private_execution_directories") and PurePosixPath(path).parts[0] in {"Dashboard", ".git"}:
            _fail("private_surface_forbidden", path)
    registry = root / "extensions/registry_v1.json"
    if registry.is_file() and "extensions/registry_v1.json" in allowlisted:
        try:
            ext = json.loads(registry.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            _fail("extension_registry_invalid", str(exc))
        ids: set[str] = set()
        required = {"id", "kind", "contract_version", "enabled_by_default", "entrypoint", "interface_schema", "core_compatibility", "provenance_ref", "missing_behavior", "claim_ceiling"}
        if ext.get("schema_version") != "sge_extension_registry_v1" or ext.get("core_requires_extensions") is not False:
            _fail("extension_registry_invalid")
        for extension in ext.get("extensions", []):
            if set(extension) != required or extension["id"] in ids or extension["enabled_by_default"] is not False:
                _fail("extension_contract_invalid")
            ids.add(extension["id"])
    return allowlisted


def _identity(source_root: Path, data: dict[str, Any], projection_files: list[dict[str, Any]]) -> dict[str, Any]:
    source_revision = _git(source_root, "rev-parse", "HEAD") or "unversioned"
    manifest_path = _manifest_path(source_root)
    tool_path = source_root / "tools/sge_public.py"
    if not tool_path.is_file():
        _fail("source_missing", "tools/sge_public.py")
    source_tree_sha = _tree_digest(projection_files)
    candidate_fingerprint = _sha256_bytes(
        json.dumps(
            {"source_revision": source_revision, "manifest_revision": _sha256_file(manifest_path), "export_tool_revision": _sha256_file(tool_path), "tree_sha256": source_tree_sha},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    return {
        "source_revision": source_revision,
        "manifest_revision": _sha256_file(manifest_path),
        "export_tool_revision": _sha256_file(tool_path),
        "export_run_id": "run-" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:12],
        "candidate_id": data["candidate_id"],
        "candidate_fingerprint": candidate_fingerprint,
        "projection_commit": None,
        "release_tag": None,
    }


def _tree_digest(files: Iterable[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for item in sorted(files, key=lambda value: value["path"]):
        digest.update(item["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(item["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _directory_records(root: Path) -> list[dict[str, Any]]:
    """Return a digestable regular-file inventory without following links."""
    if root.is_symlink() or not root.is_dir():
        _fail("managed_directory_invalid", root.as_posix())
    records: list[dict[str, Any]] = []
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda item: item.name, reverse=True)
        except OSError as exc:
            _fail("managed_directory_read_error", f"{current}:{exc}")
        for entry in entries:
            info = _lstat(entry, "managed_object_invalid")
            relative = entry.relative_to(root).as_posix()
            if stat.S_ISLNK(info.st_mode):
                _fail("managed_symlink_forbidden", relative)
            if stat.S_ISDIR(info.st_mode):
                stack.append(entry)
                continue
            if not stat.S_ISREG(info.st_mode):
                _fail("managed_object_invalid", relative)
            raw = entry.read_bytes()
            records.append({"path": relative, "sha256": _sha256_bytes(raw), "bytes": len(raw)})
    return sorted(records, key=lambda item: item["path"])


def _assert_target_layout(target: Path) -> None:
    """Fail closed before lifecycle writes can traverse a target symlink."""
    _assert_destination_path_safe(target)
    if target.is_symlink() or not target.is_dir():
        _fail("target_path_invalid", target.as_posix())
    for relative in ("AGENTS.md", ".codex", ".codex/skills", INSTALL_RECORD_NAME, BACKUP_ROOT_NAME, TRASH_ROOT_NAME):
        current = target
        for part in PurePosixPath(relative).parts:
            current = current / part
            if current.exists() or current.is_symlink():
                info = _lstat(current, "target_object_invalid")
                if stat.S_ISLNK(info.st_mode):
                    _fail("target_symlink_forbidden", relative)
                if part != PurePosixPath(relative).parts[-1] and not stat.S_ISDIR(info.st_mode):
                    _fail("target_object_invalid", relative)
    agents = target / "AGENTS.md"
    if not agents.is_file() or agents.is_symlink():
        _fail("target_not_bootstrapped")


def _install_record(marker: Path, target: Path) -> dict[str, Any]:
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail("install_record_invalid", str(exc))
    if data.get("schema_version") != "sge_install_record_v1":
        _fail("install_record_invalid", "schema_version")
    recorded_target = data.get("target_root")
    if recorded_target != str(target):
        _fail("install_record_target_mismatch")
    if data.get("write_scope") != [".codex/skills/sge-governed-checkpoints/"]:
        _fail("install_record_invalid", "write_scope")
    return data


def _write_install_record(marker: Path, data: dict[str, Any]) -> None:
    temporary = marker.with_name(marker.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        _fail("install_record_temp_exists")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(marker)


def _file_set_digest(paths: Iterable[str]) -> str:
    return _sha256_bytes("".join(f"{path}\n" for path in sorted(paths)).encode("utf-8"))


def _destination_state(destination: Path) -> tuple[bool, Path]:
    _assert_destination_path_safe(destination)
    existed = destination.exists()
    if existed and (not destination.is_dir() or any(destination.iterdir())):
        _fail("destination_must_be_empty")
    resolved = destination.resolve()
    return existed, resolved


def _assert_destination_path_safe(destination: Path) -> None:
    if destination.is_symlink():
        _fail("destination_unsafe_link", destination.as_posix())
    current = destination
    # Stop at the nearest existing ancestor so normal macOS aliases such as
    # /var -> /private/var are not treated as an application-controlled
    # redirect.  Any existing symlink directly selected as destination or its
    # nearest existing parent is still rejected.
    while not current.exists() and current != current.parent:
        current = current.parent
    if current.is_symlink():
        _fail("destination_unsafe_link", current.as_posix())


def _source_file_records(source_root: Path, data: dict[str, Any], paths: set[str]) -> list[dict[str, Any]]:
    by_path = {item["path"]: item for item in data["files"]}
    records: list[dict[str, Any]] = []
    for path in sorted(paths):
        raw = _safe_source_file(source_root, path).read_bytes()
        item = by_path[path]
        records.append(
            {
                "path": path,
                "source": item["source"],
                "license": item["license"],
                "provenance": item["provenance"],
                "execution_context": item["execution_context"],
                "bytes": len(raw),
                "sha256": _sha256_bytes(raw),
            }
        )
    return records


def _projection_metadata(source_root: Path, data: dict[str, Any], records: list[dict[str, Any]], inventory: list[dict[str, Any]]) -> dict[str, Any]:
    identity = _identity(source_root, data, records)
    excluded = [entry for entry in inventory if entry["excluded_reason"]]
    excluded_counts: dict[str, int] = {}
    for entry in excluded:
        reason = entry["excluded_reason"]
        excluded_counts[reason] = excluded_counts.get(reason, 0) + 1
    return {
        "schema_version": "sge_projection_metadata_v1",
        "claim_ceiling": "仅支持 maintainer local deterministic projection candidate evidence；不支持独立 Validation、批准、公开仓、远端 mutation、release 或 production。",
        "identity": identity,
        "state": {
            "candidate": True,
            "validated": False,
            "approved": False,
            "published": False,
            "production_ready": False,
            "git_mutation": False,
            "license_authorized": None,
        },
        "manifest_status": data["status"],
        "files": records,
        "file_set_sha256": _file_set_digest(record["path"] for record in records),
        "tree_sha256": _tree_digest(records),
        "source_inventory": {
            "complete": True,
            "entry_count": len(inventory),
            "allowlisted_entry_count": sum(1 for entry in inventory if entry["allowlisted"]),
            "excluded_entry_count": len(excluded),
            "excluded_counts": excluded_counts,
            "private_paths_omitted_from_public_metadata": True,
        },
    }


def verify_projection(source: Path | str, destination: Path | str, *, require_clean: bool = False) -> dict[str, Any]:
    """Recompute exact file and digest evidence for an existing projection."""
    source_input = _root(source)
    if source_input.is_symlink() or not source_input.is_dir():
        _fail("source_root_invalid", source_input.as_posix())
    source_root = source_input.resolve()
    destination_input = Path(destination)
    _assert_destination_path_safe(destination_input)
    destination_path = destination_input.resolve()
    if not destination_path.is_dir() or destination_path.is_symlink():
        _fail("destination_invalid", destination_path.as_posix())
    data = load(source_root)
    paths = validate(data, source_root)
    if require_clean and _git_status(source_root):
        _fail("dirty_tree")
    expected = {path: _sha256_file(_safe_source_file(source_root, path)) for path in paths}
    observed = {}
    stack = [destination_path]
    while stack:
        current = stack.pop()
        for entry in current.iterdir():
            if entry.name == METADATA_NAME and current == destination_path:
                continue
            if entry.is_symlink():
                _fail("unsafe_link_or_path_escape", entry.relative_to(destination_path).as_posix())
            if entry.is_file():
                rel = entry.relative_to(destination_path).as_posix()
                observed[rel] = _sha256_file(entry)
            elif entry.is_dir():
                stack.append(entry)
            else:
                _fail("destination_object_invalid", entry.relative_to(destination_path).as_posix())
    for path in list(observed):
        if path not in expected:
            _fail("unknown_path_default_deny", path)
    if set(observed) != set(expected):
        _fail("projection_file_set_drift")
    for path, digest in expected.items():
        if observed[path] != digest:
            _fail("projection_digest_drift", path)
    return {"files": sorted(expected), "tree_sha256": _tree_digest([{"path": p, "sha256": d} for p, d in expected.items()])}


def export(destination: Path, source: Path | str | None = None, *, require_clean: bool = True) -> dict[str, Any]:
    source_input = _root(source)
    if source_input.is_symlink() or not source_input.is_dir():
        _fail("source_root_invalid", source_input.as_posix())
    source_root = source_input.resolve()
    existed, destination_path = _destination_state(Path(destination))
    if destination_path == source_root or source_root in destination_path.parents:
        _fail("destination_path_invalid", destination_path.as_posix())
    data = load(source_root)
    paths = validate(data, source_root)
    status = _git_status(source_root)
    if require_clean and status:
        _fail("dirty_tree")
    inventory, nested_repos = _walk_inventory(source_root, paths)
    if nested_repos:
        _fail("nested_repo_forbidden", nested_repos[0])
    before = _source_file_records(source_root, data, paths)
    metadata = _projection_metadata(source_root, data, before, inventory)
    destination_path.mkdir(parents=True, exist_ok=True)
    try:
        for record in before:
            source_file = _safe_source_file(source_root, record["path"])
            out = destination_path / record["path"]
            out.parent.mkdir(parents=True, exist_ok=True)
            _assert_inside(destination_path, out.resolve(), "unsafe_link_or_path_escape")
            shutil.copy2(source_file, out, follow_symlinks=False)
        after = _source_file_records(source_root, data, paths)
        if [(r["path"], r["sha256"]) for r in before] != [(r["path"], r["sha256"]) for r in after]:
            _fail("projection_digest_drift")
        verify_projection(source_root, destination_path)
        (destination_path / METADATA_NAME).write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception:
        if not existed and destination_path.exists():
            shutil.rmtree(destination_path)
        raise
    print(f"exported:{len(paths)}:{destination_path}")
    return metadata


def ensure_empty(destination: Path) -> None:
    _destination_state(destination)
    destination.mkdir(parents=True, exist_ok=True)


def bootstrap(destination: Path) -> None:
    ensure_empty(destination)
    files = {
        "README.md": "# Minimal SGE Project\n\n项目 authority 位于 AGENTS.md、kb/data/ 和 Dashboard/。\n",
        "AGENTS.md": "# Project Governance\n\n- 稳定 truth 写入 kb/data/；执行记忆写入 Dashboard/。\n- 候选、验证、批准和发布分轴记录。\n",
        "kb/data/strategy/profile.json": json.dumps({"schema_version": "sge_project_profile_v1", "project_id": destination.name, "authority": {"canonical_truth": "kb/data/", "execution_memory": "Dashboard/"}, "claim_ceiling": "repo-local governance skeleton only"}, ensure_ascii=False, indent=2) + "\n",
        "Dashboard/Sessions.md": "# Sessions\n\n| Session | Status | Evidence |\n| --- | --- | --- |\n",
        "Dashboard/Current_State.md": "# Current State\n\n尚未创建 Goal。\n",
    }
    for relative, body in files.items():
        out = destination / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
    print(f"bootstrapped:{destination}")


def _install_source_records(source: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate a public source and return only the end-user core payload."""
    manifest = load(source)
    validate(manifest, source)
    records = []
    for item in manifest["files"]:
        relative = item["path"]
        if not relative.startswith(CORE_SKILL_PREFIX):
            continue
        source_file = _safe_source_file(source, relative)
        raw = source_file.read_bytes()
        records.append({"path": relative, "sha256": _sha256_bytes(raw), "bytes": len(raw)})
    if not records:
        _fail("install_core_missing")
    return manifest, sorted(records, key=lambda item: item["path"])


def _install_identity(source: Path, manifest: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "source_revision": _git(source, "rev-parse", "HEAD") or "unversioned",
        "manifest_revision": _sha256_file(_manifest_path(source)),
        "candidate_id": manifest["candidate_id"],
        "file_set_sha256": _file_set_digest(item["path"] for item in records),
        "tree_sha256": _tree_digest(records),
    }


def install(source: Path | None, target: Path, *, upgrade: bool = False) -> None:
    source_root = (Path.cwd() if source is None else Path(source)).resolve()
    target_input = Path(target)
    _assert_destination_path_safe(target_input)
    target_root = target_input.resolve()
    if source_root == target_root or source_root in target_root.parents:
        _fail("target_path_invalid")
    manifest, records = _install_source_records(source_root)
    _assert_target_layout(target_root)
    skill_dir = target_root / CORE_SKILL_PREFIX.rstrip("/")
    marker = target_root / INSTALL_RECORD_NAME
    if skill_dir.exists() and not upgrade:
        _fail("already_installed")
    if skill_dir.is_symlink():
        _fail("target_skill_unsafe")
    existing_record: dict[str, Any] | None = None
    if marker.exists():
        if marker.is_symlink():
            _fail("target_symlink_forbidden", INSTALL_RECORD_NAME)
        existing_record = _install_record(marker, target_root)
    if skill_dir.exists() and not existing_record:
        _fail("upgrade_requires_install_record" if upgrade else "unmanaged_skill_exists")
    if upgrade and not skill_dir.exists():
        _fail("upgrade_requires_installed_skill")
    if upgrade and existing_record:
        observed = _directory_records(skill_dir)
        expected = []
        for item in existing_record.get("files", []):
            path = item.get("path", "")
            if not path.startswith(CORE_SKILL_PREFIX):
                _fail("install_record_invalid", "managed_file_path")
            expected.append({**item, "path": path[len(CORE_SKILL_PREFIX):]})
        if observed != sorted(expected, key=lambda item: item["path"]):
            _fail("unknown_target_content")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_root: Path | None = None
    backup_records: list[dict[str, Any]] = []
    try:
        if skill_dir.exists():
            backup_records = _directory_records(skill_dir)
            backup_root = target_root / BACKUP_ROOT_NAME / stamp / CORE_SKILL_PREFIX.rstrip("/")
            backup_root.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(skill_dir), str(backup_root))
        for record in records:
            source_file = _safe_source_file(source_root, record["path"])
            out = target_root / record["path"]
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, out)
        identity = _install_identity(source_root, manifest, records)
        install_record = {
            "schema_version": "sge_install_record_v1",
            "status": "upgraded" if upgrade else "installed",
            "operation": "upgrade" if upgrade else "install",
            "source_candidate": manifest["candidate_id"],
            "source_identity": identity,
            "target_authority": "target project owns AGENTS.md, Dashboard/, Goal and Session surfaces; installer writes only the declared core Skill files",
            "target_root": str(target_root),
            "write_scope": [".codex/skills/sge-governed-checkpoints/"],
            "files": records,
            "backup": (str(backup_root) if backup_root else None),
            "backup_files": backup_records,
            "backup_tree_sha256": _tree_digest(backup_records) if backup_records else None,
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        _write_install_record(marker, install_record)
    except Exception:
        if skill_dir.exists() and not skill_dir.is_symlink():
            shutil.rmtree(skill_dir)
        if backup_root and backup_root.exists():
            skill_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(backup_root), str(skill_dir))
        raise
    print(f"{'upgraded' if upgrade else 'installed'}:{len(records)}:{target_root}")


def uninstall(target: Path) -> None:
    target_input = Path(target)
    _assert_destination_path_safe(target_input)
    target = target_input.resolve()
    marker = target / INSTALL_RECORD_NAME
    if not marker.is_file():
        _fail("uninstall_requires_install_record")
    _assert_target_layout(target)
    _install_record(marker, target)
    skill = target / CORE_SKILL_PREFIX.rstrip("/")
    if skill.is_symlink():
        _fail("target_skill_unsafe")
    if not skill.is_dir():
        _fail("installed_skill_missing")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    trash = target / TRASH_ROOT_NAME / stamp / "sge-governed-checkpoints"
    trash.parent.mkdir(parents=True, exist_ok=True)
    record_trash = trash.parent / "install-record.json"
    try:
        shutil.move(str(skill), str(trash))
        marker.rename(record_trash)
    except Exception:
        if trash.exists() and not skill.exists():
            skill.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(trash), str(skill))
        raise
    print(f"uninstalled_recoverable:{trash}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    exp = sub.add_parser("export")
    exp.add_argument("destination", type=Path)
    exp.add_argument("--source", type=Path, default=None)
    ver = sub.add_parser("verify")
    ver.add_argument("--source", type=Path, required=True)
    ver.add_argument("--destination", type=Path, required=True)
    boot = sub.add_parser("bootstrap")
    boot.add_argument("destination", type=Path)
    ins = sub.add_parser("install")
    ins.add_argument("--source", type=Path, default=None, help="高级/测试 alternate source；默认使用当前公开仓目录")
    ins.add_argument("--target", type=Path, required=True)
    up = sub.add_parser("upgrade")
    up.add_argument("--source", type=Path, default=None, help="高级/测试 alternate source；默认使用当前公开仓目录")
    up.add_argument("--target", type=Path, required=True)
    rem = sub.add_parser("uninstall")
    rem.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "doctor":
        validate(load())
        print("public_doctor:pass")
    elif args.command == "export":
        export(args.destination, args.source)
    elif args.command == "verify":
        print(json.dumps(verify_projection(args.source, args.destination), ensure_ascii=False, indent=2))
    elif args.command == "bootstrap":
        bootstrap(args.destination)
    elif args.command == "install":
        install(args.source, args.target)
    elif args.command == "upgrade":
        install(args.source, args.target, upgrade=True)
    elif args.command == "uninstall":
        uninstall(args.target)


if __name__ == "__main__":
    main()

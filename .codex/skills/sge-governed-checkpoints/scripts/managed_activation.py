#!/usr/bin/env python3
"""Evaluate post-install activation without claiming host capabilities."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

SCHEMA_VERSION = "sge_managed_activation_v1"
TERMINAL_OBLIGATIONS = {
    "release": ("release", "发布"),
    "remote_readback": ("remote read-back", "远端回读"),
    "clean_install": ("clean install", "clean-install"),
    "managed_sync": ("managed sync", "受管同步", "安装同步"),
    "independent_validation": ("independent validation", "独立 validation", "独立验证"),
    "final_reconciliation": ("final reconciliation", "最终 reconciliation"),
    "closeout_language": ("closeout-language", "closeout language"),
    "dashboard_kb_registry": ("dashboard/kb", "registry reconciliation", "registry"),
}


class AuthorityBoundary(NamedTuple):
    """Host-owned trust anchor; never populated from the evaluated task payload."""

    bundle_root: Path
    manifest_sha256: str


INSTALLED_AUTHORITY_BUNDLE = Path(__file__).resolve().parents[1] / "fixtures/authority-v2"
INSTALLED_AUTHORITY_MANIFEST_SHA256 = "2febfe9a5e4df6280e5645b37dbce64d17c9f969d28901bc9e9194f1ee57dce3"


def load_installed_authority_boundary() -> AuthorityBoundary:
    """Load the managed-install bundle from its fixed package location."""
    manifest = INSTALLED_AUTHORITY_BUNDLE / "digest-manifest.json"
    if not manifest.is_file() or _sha(manifest) != INSTALLED_AUTHORITY_MANIFEST_SHA256:
        raise ValueError("AUTHORITY_BUNDLE_MANIFEST_INVALID")
    return AuthorityBoundary(INSTALLED_AUTHORITY_BUNDLE, INSTALLED_AUTHORITY_MANIFEST_SHA256)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_ref(root: Path, ref: Any, code: str, trusted_root: Path | None = None) -> Path:
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        raise ValueError(f"{code}_REF_INVALID")
    relative = ref["path"]
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"{code}_LOCATOR_INVALID")
    path = (root / relative).resolve()
    boundary = (trusted_root or root).resolve()
    try:
        path.relative_to(boundary)
    except ValueError as exc:
        raise ValueError(f"{code}_UNTRUSTED_LOCATOR") from exc
    if not path.is_file() or not isinstance(ref["sha256"], str) or len(ref["sha256"]) != 64 or _sha(path) != ref["sha256"]:
        raise ValueError(f"{code}_DIGEST_MISMATCH")
    return path


def _load_json_ref(root: Path, ref: Any, code: str, trusted_root: Path | None = None) -> dict[str, Any]:
    path = _resolve_ref(root, ref, code, trusted_root)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{code}_JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{code}_JSON_INVALID")
    return value


def _time(value: Any, code: str) -> datetime.datetime:
    if not isinstance(value, str):
        raise ValueError(f"{code}_TIME_INVALID")
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{code}_TIME_INVALID") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{code}_TIME_INVALID")
    return parsed


def produce_goal_obligations(goal_path: Path) -> list[str]:
    """Deterministically extract the complete terminal denominator from a frozen Goal."""
    text = goal_path.read_text(encoding="utf-8")
    mh = sorted(set(re.findall(r"\bMH-\d+\b", text)), key=lambda value: int(value.split("-")[1]))
    ac = sorted(set(re.findall(r"\bAC-\d+\b", text)), key=lambda value: int(value.split("-")[1]))
    if not mh or not ac:
        raise ValueError("GOAL_OBLIGATION_PARSE_INCOMPLETE")
    for values, prefix in ((mh, "MH"), (ac, "AC")):
        numbers = [int(value.split("-")[1]) for value in values]
        if numbers != list(range(1, max(numbers) + 1)):
            raise ValueError(f"GOAL_{prefix}_INVENTORY_NONCONTIGUOUS")
    lowered = text.lower()
    terminal = []
    for obligation, tokens in TERMINAL_OBLIGATIONS.items():
        if not any(token.lower() in lowered for token in tokens):
            raise ValueError(f"GOAL_TERMINAL_OBLIGATION_MISSING:{obligation}")
        terminal.append(f"terminal:{obligation}")
    return [*mh, *ac, *terminal]


def _trusted_authority(boundary: AuthorityBoundary | None, payload: dict[str, Any]) -> tuple[Path, list[str], dict[str, Any]]:
    forbidden = {"trusted_authority_root", "authority_root_ref", "authority_config", "expected_authority_digest", "authority_bundle_path", "authority_manifest_sha256"}
    if forbidden.intersection(payload):
        raise ValueError("TASK_PAYLOAD_AUTHORITY_SELECTION_FORBIDDEN")
    if boundary is None:
        raise ValueError("AUTHORITY_BOUNDARY_NOT_CONFIGURED")
    bundle = boundary.bundle_root.resolve()
    manifest_path = bundle / "digest-manifest.json"
    if not manifest_path.is_file() or _sha(manifest_path) != boundary.manifest_sha256:
        raise ValueError("AUTHORITY_BUNDLE_MANIFEST_INVALID")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("AUTHORITY_BUNDLE_MANIFEST_INVALID") from exc
    rows = manifest.get("files")
    if manifest.get("schema_version") != "owner_provisioned_authority_bundle_manifest_v1" or manifest.get("copy_policy") != "exact_bytes_only" or not isinstance(rows, list):
        raise ValueError("AUTHORITY_BUNDLE_MANIFEST_INVALID")
    expected_files = {"digest-manifest.json"}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
            raise ValueError("AUTHORITY_BUNDLE_MANIFEST_INVALID")
        path = _resolve_ref(bundle, row, "AUTHORITY_BUNDLE_FILE")
        expected_files.add(path.relative_to(bundle).as_posix())
    observed_files = {path.relative_to(bundle).as_posix() for path in bundle.iterdir() if path.is_file()}
    if observed_files != expected_files:
        raise ValueError("AUTHORITY_BUNDLE_FILE_SET_MISMATCH")
    boundary_config = json.loads((bundle / "trusted-authority-boundary.json").read_text(encoding="utf-8"))
    if boundary_config.get("schema_version") != "trusted_authority_boundary_v2" or boundary_config.get("provisioning") != "managed_install_or_platform_configuration" or boundary_config.get("task_override_allowed") is not False:
        raise ValueError("AUTHORITY_BOUNDARY_CONFIG_INVALID")
    authority = _load_json_ref(bundle, boundary_config.get("root"), "AUTHORITY_ROOT")
    goal_path = _resolve_ref(bundle, boundary_config.get("goal"), "AUTHORITY_SOURCE")
    inventory = _load_json_ref(bundle, boundary_config.get("obligation_inventory"), "AUTHORITY_INVENTORY")
    issuer = authority.get("issuer", {})
    provenance = _load_json_ref(bundle, {"path":issuer.get("provenance_ref"), "sha256":issuer.get("provenance_sha256")}, "AUTHORITY_PROVENANCE")
    if issuer.get("issuer_role") != "goal_owner" or provenance.get("issuer_id") != issuer.get("issuer_id") or provenance.get("issuer_role") != issuer.get("issuer_role") or provenance.get("provisioned_by") != "owner":
        raise ValueError("AUTHORITY_ISSUER_ROLE_FORBIDDEN")
    if authority.get("source", {}).get("sha256") != _sha(goal_path) or authority.get("source", {}).get("revision") != authority.get("scope", {}).get("source_revision"):
        raise ValueError("AUTHORITY_SOURCE_MISMATCH")
    evaluated_at = _time(payload.get("evaluated_at"), "EVALUATION")
    if _time(authority.get("issued_at"), "AUTHORITY") >= evaluated_at or _time(authority.get("effective_before"), "AUTHORITY") >= evaluated_at:
        raise ValueError("AUTHORITY_ISSUED_TOO_LATE")
    expected_ids = produce_goal_obligations(goal_path)
    if inventory.get("schema_version") != "goal_obligation_inventory_v2" or inventory.get("source_revision") != authority.get("scope", {}).get("source_revision") or inventory.get("obligation_ids") != expected_ids:
        raise ValueError("GOAL_OBLIGATION_INVENTORY_INCOMPLETE")
    subjects = authority.get("subjects", [])
    expected_subjects = {
        ("goal", _sha(goal_path)),
        ("goal_obligation_inventory", _sha(bundle / "goal-obligation-inventory.json")),
    }
    observed_subjects = {(row.get("subject_kind"), row.get("digest")) for row in subjects if isinstance(row, dict)}
    if observed_subjects != expected_subjects:
        raise ValueError("AUTHORITY_SUBJECT_MISMATCH")
    if payload.get("authority_root_id") not in {None, authority.get("authority_root_id")} or payload.get("authority_root_revision") not in {None, authority.get("root_revision")}:
        raise ValueError("AUTHORITY_SUBJECT_MISMATCH")
    return goal_path, expected_ids, authority


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    root = Path(payload.get("repo_root", ".")).resolve()
    exception_ref = payload.get("exception_ref")
    installed, capability = False, "unknown"
    try:
        install_path = _resolve_ref(root, payload.get("managed_install_receipt_ref"), "MANAGED_INSTALL_RECEIPT")
        install_receipt = json.loads(install_path.read_text(encoding="utf-8"))
        capability_receipt = _load_json_ref(root, payload.get("capability_receipt_ref"), "CAPABILITY_RECEIPT")
        installed = (
            install_receipt.get("schema_version") == "sge_managed_install_receipt_v1"
            and install_receipt.get("status") in {"installed", "upgraded"}
            and isinstance(install_receipt.get("target_id"), str) and bool(install_receipt.get("target_id"))
            and isinstance(install_receipt.get("candidate_id"), str) and bool(install_receipt.get("candidate_id"))
            and isinstance(install_receipt.get("file_set_sha256"), str) and len(install_receipt.get("file_set_sha256")) == 64
        )
        capability = capability_receipt.get("state", "unknown")
        capability_valid = (
            capability_receipt.get("schema_version") == "sge_delegation_capability_receipt_v1"
            and capability in {"supported", "unsupported", "unknown"}
            and capability_receipt.get("install_receipt_sha256") == _sha(install_path)
            and capability_receipt.get("target_id") == install_receipt.get("target_id")
            and isinstance(capability_receipt.get("host_identity"), str) and bool(capability_receipt.get("host_identity"))
        )
        if not installed or not capability_valid:
            raise ValueError("ACTIVATION_RECEIPT_BINDING_INVALID")
    except (ValueError, json.JSONDecodeError):
        installed, capability = False, "unknown"
    if installed and capability == "supported":
        verdict, reason = "activated", "MANAGED_INSTALL_AND_CAPABILITY_VERIFIED"
    elif exception_ref is not None and installed:
        try:
            trusted_root_value = payload.get("trusted_approval_root")
            if not isinstance(trusted_root_value, str) or not trusted_root_value:
                raise ValueError("APPROVAL_TRUST_ROOT_MISSING")
            trusted_root = (root / trusted_root_value).resolve()
            approval = _load_json_ref(root, exception_ref, "TOPOLOGY_EXCEPTION", trusted_root)
            valid = (
                approval.get("schema_version") == "human_topology_exception_approval_v1"
                and approval.get("authority_kind") == "human"
                and approval.get("decision") == "approve"
                and approval.get("scope") == "topology_exception"
                and isinstance(approval.get("approval_id"), str)
                and _time(approval.get("approved_at"), "APPROVAL") < _time(payload.get("evaluated_at"), "EVALUATION")
            )
            if not valid:
                raise ValueError("TOPOLOGY_EXCEPTION_APPROVAL_INVALID")
            verdict, reason = "exception_authorized", "PRIOR_TOPOLOGY_EXCEPTION_VERIFIED"
        except ValueError as exc:
            verdict, reason = "blocked", str(exc)
    elif installed and capability == "unsupported":
        verdict, reason = "blocked", "CAPABILITY_UNSUPPORTED"
    elif installed:
        verdict, reason = "blocked", "CAPABILITY_UNKNOWN"
    else:
        verdict, reason = "blocked", "MANAGED_INSTALL_OR_CAPABILITY_RECEIPT_INVALID"
    return {
        "schema_version": SCHEMA_VERSION,
        "activation_verdict": verdict,
        "reason_code": reason,
        "managed_install_record": installed,
        "capability_state": capability if capability in {"supported", "unsupported", "unknown"} else "unknown",
        "exception_ref": exception_ref if verdict == "exception_authorized" else None,
        "maximum_claim": "supported host activation only",
    }


def terminal_evidence(payload: dict[str, Any], *, authority_boundary: AuthorityBoundary | None = None) -> dict[str, Any]:
    root = Path(payload.get("repo_root", ".")).resolve()
    reasons: list[str] = []
    independent = "absent"
    try:
        producer = _load_json_ref(root, payload.get("producer_identity_ref"), "PRODUCER_IDENTITY")
        review = _load_json_ref(root, payload.get("validation_review_ref"), "VALIDATION_REVIEW")
        contract_path = _resolve_ref(root, payload.get("contract_ref"), "CONTRACT")
        cases_path = _resolve_ref(root, payload.get("cases_ref"), "CASES")
        diff_path = _resolve_ref(root, payload.get("actual_diff_ref"), "ACTUAL_DIFF")
        goal_path, expected_ids, _ = _trusted_authority(authority_boundary, payload)
        reviewer = review.get("reviewer_identity")
        producer_identity = producer.get("execution_identity")
        obligations = review.get("goal_obligations")
        obligation_ids = [row.get("requirement_id") for row in obligations] if isinstance(obligations, list) else []
        valid = (
            producer.get("schema_version") == "execution_identity_receipt_v1"
            and review.get("schema_version") == "independent_validation_review_v1"
            and review.get("verdict") == "pass"
            and isinstance(reviewer, str) and reviewer.strip()
            and isinstance(producer_identity, str) and producer_identity.strip()
            and reviewer != producer_identity
            and review.get("producer_identity") == producer_identity
            and review.get("contract_sha256") == _sha(contract_path)
            and review.get("cases_sha256") == _sha(cases_path)
            and review.get("actual_diff_sha256") == _sha(diff_path)
            and review.get("goal_sha256") == _sha(goal_path)
            and isinstance(obligations, list) and bool(obligations)
            and all(isinstance(row, dict) and row.get("satisfied") is True and isinstance(row.get("requirement_id"), str) for row in obligations)
            and len(obligation_ids) == len(set(obligation_ids))
            and set(obligation_ids) == set(expected_ids)
        )
        if not valid:
            raise ValueError("VALIDATION_REVIEW_BINDING_INVALID")
        independent = "passed"
    except ValueError as exc:
        reasons.append(str(exc))
    readback = "not_attempted"
    if payload.get("release_created"):
        try:
            receipt = _load_json_ref(root, payload.get("remote_readback_ref"), "REMOTE_READBACK")
            if receipt.get("schema_version") != "remote_release_readback_v1" or receipt.get("status") != "verified" or not all(receipt.get(key) for key in ("tag", "asset", "checksum", "ci_run")):
                raise ValueError("REMOTE_READBACK_BINDING_INVALID")
            readback = "verified"
        except ValueError as exc:
            readback = "created_unverified"
            reasons.append(str(exc))
    return {
        "schema_version": SCHEMA_VERSION,
        "independent_validation": independent,
        "session_terminal": independent == "passed" and readback == "verified",
        "release_readback": readback,
        "reason_codes": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("mode", choices=("activation", "terminal-evidence")); parser.add_argument("input")
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin) if args.input == "-" else json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = evaluate(payload) if args.mode == "activation" else terminal_evidence(payload)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result.get("activation_verdict", "activated") != "blocked" and not result.get("reason_codes") else 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"verdict":"fail", "fingerprint":str(exc)}, ensure_ascii=False)); return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate, resolve, render, and audit SGE Goal contracts using stdlib only."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


GOAL_SCHEMA_VERSION = "goal_contract_v1"
PATCH_SCHEMA_VERSION = "goal_patch_v1"
APPROVAL_TOKEN_PREFIX = "SGE_GOAL_PATCH_APPROVAL_V1 "
APPROVAL_RECEIPT_SCHEMA_VERSION = "approval_receipt_v1"
REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_APPROVAL_SOURCE_ROOTS = (
    Path.home() / ".codex" / "sessions",
    Path.home() / ".codex" / "archived_sessions",
)
PROTECTED_TARGETS = frozenset(
    {
        "goal_id",
        "mission",
        "must_have_ledger",
        "claim_policy",
        "completion_rule",
        "approval_authorities",
        "approval_registry",
        "approved_scope_delta_registry",
    }
)
IMMUTABLE_TARGETS = frozenset({"goal_id"})
ALLOWED_MUST_HAVE_STATUSES = frozenset(
    {"pending", "landed", "blocked", "approved_deferred", "not_applicable"}
)
ALLOWED_SCOPE_IMPACTS = frozenset(
    {"narrowed", "replaced", "deferred", "authority_changed", "claim_changed"}
)
NESTED_CLAIM_CARRIER_KEYS = frozenset(
    {
        "allowedclaimids",
        "authorityclaim",
        "claim",
        "claimid",
        "claimids",
        "claimpolicy",
        "claimstatement",
        "claimstatements",
        "claims",
        "completion",
        "completionclaim",
        "completionclaimid",
        "completionclaims",
        "completionrule",
        "completionstate",
        "completionstatus",
        "completionverdict",
        "finalverdict",
    }
)
FORBIDDEN_PROSE_PATTERNS = (
    re.compile(r"\b(?:goal|session|stage plan)\s+(?:is\s+)?complete\b", re.IGNORECASE),
    re.compile(r"\bindependent validation passed\b", re.IGNORECASE),
    re.compile(r"\bscope delta approved\b", re.IGNORECASE),
)
MARKDOWN_PAYLOAD_RE = re.compile(
    r"^# Final Goal: .+?\n\n"
    r"## Canonical Goal Payload\n\n"
    r"```json\n(?P<payload>\{.*\})\n```\n?",
    re.DOTALL,
)


class GoalPatchError(ValueError):
    """Raised when Goal or patch authority cannot be established."""


def _fail(path: str, message: str) -> None:
    raise GoalPatchError(f"{path}: {message}")


def _expect_dict(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    return value


def _expect_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    return value


def _expect_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(path, "must be a non-empty string")
    return value


def _require_exact_keys(
    value: Mapping[str, Any], required: Iterable[str], optional: Iterable[str], path: str
) -> None:
    required_set = set(required)
    allowed = required_set | set(optional)
    missing = sorted(required_set - set(value))
    unknown = sorted(set(value) - allowed)
    if missing:
        _fail(path, f"missing required fields: {', '.join(missing)}")
    if unknown:
        _fail(path, f"unknown fields: {', '.join(unknown)}")


def canonical_json(value: Any, *, pretty: bool = False) -> str:
    """Return deterministic UTF-8-safe JSON."""

    if pretty:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def goal_digest(goal: Mapping[str, Any]) -> str:
    """Digest Goal content while excluding registry self-reference and resolution metadata."""

    digestable = copy.deepcopy(dict(goal))
    digestable.pop("approval_registry", None)
    digestable.pop("resolution", None)
    return hashlib.sha256(canonical_json(digestable).encode("utf-8")).hexdigest()


def _validate_claim_policy(policy_value: Any) -> set[str]:
    policy = _expect_dict(policy_value, "goal.claim_policy")
    _require_exact_keys(
        policy,
        {"claim_definitions", "allowed_claim_ids", "claim_statements"},
        set(),
        "goal.claim_policy",
    )
    definitions = _expect_list(policy["claim_definitions"], "goal.claim_policy.claim_definitions")
    if not definitions:
        _fail("goal.claim_policy.claim_definitions", "must not be empty")
    definition_ids: list[str] = []
    for index, raw in enumerate(definitions):
        path = f"goal.claim_policy.claim_definitions[{index}]"
        item = _expect_dict(raw, path)
        _require_exact_keys(item, {"claim_id", "statement"}, set(), path)
        definition_ids.append(_expect_string(item["claim_id"], f"{path}.claim_id"))
        _expect_string(item["statement"], f"{path}.statement")
    if len(definition_ids) != len(set(definition_ids)):
        _fail("goal.claim_policy.claim_definitions", "claim_id values must be unique")

    allowed = _expect_list(policy["allowed_claim_ids"], "goal.claim_policy.allowed_claim_ids")
    if any(not isinstance(item, str) or not item for item in allowed):
        _fail("goal.claim_policy.allowed_claim_ids", "items must be non-empty strings")
    if len(allowed) != len(set(allowed)):
        _fail("goal.claim_policy.allowed_claim_ids", "items must be unique")
    unknown_allowed = sorted(set(allowed) - set(definition_ids))
    if unknown_allowed:
        _fail("goal.claim_policy.allowed_claim_ids", f"unknown claim ids: {unknown_allowed}")

    statements = _expect_list(policy["claim_statements"], "goal.claim_policy.claim_statements")
    if not statements:
        _fail("goal.claim_policy.claim_statements", "must not be empty")
    seen_statement_ids: set[str] = set()
    for index, raw in enumerate(statements):
        path = f"goal.claim_policy.claim_statements[{index}]"
        item = _expect_dict(raw, path)
        _require_exact_keys(item, {"claim_id", "disposition"}, set(), path)
        claim_id = _expect_string(item["claim_id"], f"{path}.claim_id")
        if claim_id not in definition_ids:
            _fail(f"{path}.claim_id", f"unknown claim id: {claim_id}")
        if item["disposition"] not in {"allowed", "forbidden"}:
            _fail(f"{path}.disposition", "must be allowed or forbidden")
        if claim_id in seen_statement_ids:
            _fail(path, f"duplicate claim statement for {claim_id}")
        seen_statement_ids.add(claim_id)
        if item["disposition"] == "allowed" and claim_id not in allowed:
            _fail(path, f"allowed statement {claim_id} is absent from allowed_claim_ids")
        if item["disposition"] == "forbidden" and claim_id in allowed:
            _fail(path, f"forbidden statement {claim_id} appears in allowed_claim_ids")
    if seen_statement_ids != set(definition_ids):
        missing = sorted(set(definition_ids) - seen_statement_ids)
        _fail("goal.claim_policy.claim_statements", f"missing claim ids: {missing}")
    return set(definition_ids)


def _scan_nested_claim_carriers(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = re.sub(
                r"[^a-z0-9]", "", unicodedata.normalize("NFKC", key).casefold()
            )
            child_path = f"{path}.{key}"
            if normalized_key in NESTED_CLAIM_CARRIER_KEYS:
                _fail(child_path, "structured claim carrier is not authoritative in this location")
            _scan_nested_claim_carriers(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_nested_claim_carriers(child, f"{path}[{index}]")


def _validate_approval_registry(goal: Mapping[str, Any]) -> None:
    authority_pairs: set[tuple[str, str]] = set()
    authorities = _expect_list(goal["approval_authorities"], "goal.approval_authorities")
    if not authorities:
        _fail("goal.approval_authorities", "must not be empty")
    for index, raw in enumerate(authorities):
        path = f"goal.approval_authorities[{index}]"
        item = _expect_dict(raw, path)
        _require_exact_keys(item, {"authority_kind", "authority_id"}, set(), path)
        if item["authority_kind"] != "human":
            _fail(f"{path}.authority_kind", "only human authority is accepted")
        authority_pairs.add(("human", _expect_string(item["authority_id"], f"{path}.authority_id")))
    if len(authority_pairs) != len(authorities):
        _fail("goal.approval_authorities", "entries must be unique")

    approvals = _expect_list(goal["approval_registry"], "goal.approval_registry")
    approval_ids: set[str] = set()
    required = {
        "approval_id",
        "authority_kind",
        "authority_id",
        "status",
        "base_digest",
        "revision",
        "allowed_patch_ids",
        "allowed_targets",
        "scope_delta_ids",
        "provenance",
    }
    for index, raw in enumerate(approvals):
        path = f"goal.approval_registry[{index}]"
        item = _expect_dict(raw, path)
        _require_exact_keys(item, required, set(), path)
        approval_id = _expect_string(item["approval_id"], f"{path}.approval_id")
        if approval_id in approval_ids:
            _fail(f"{path}.approval_id", "must be unique")
        approval_ids.add(approval_id)
        if item["authority_kind"] != "human" or item["status"] != "approved":
            _fail(path, "approval must be approved by a human authority")
        authority_id = _expect_string(item["authority_id"], f"{path}.authority_id")
        if ("human", authority_id) not in authority_pairs:
            _fail(f"{path}.authority_id", "authority is not registered")
        digest = _expect_string(item["base_digest"], f"{path}.base_digest")
        if not re.fullmatch(r"[a-f0-9]{64}", digest):
            _fail(f"{path}.base_digest", "must be a lowercase SHA-256 digest")
        _expect_string(item["revision"], f"{path}.revision")
        for field in ("allowed_patch_ids", "allowed_targets", "scope_delta_ids"):
            values = _expect_list(item[field], f"{path}.{field}")
            if field != "scope_delta_ids" and not values:
                _fail(f"{path}.{field}", "must not be empty")
            if any(not isinstance(value, str) or not value for value in values):
                _fail(f"{path}.{field}", "items must be non-empty strings")
            if len(values) != len(set(values)):
                _fail(f"{path}.{field}", "items must be unique")
        if len(item["allowed_patch_ids"]) != 1 or len(item["allowed_targets"]) != 1:
            _fail(path, "approval must bind exactly one patch id and one target")
        provenance = _expect_dict(item["provenance"], f"{path}.provenance")
        source_kind = _expect_string(
            provenance.get("source_kind"), f"{path}.provenance.source_kind"
        )
        if source_kind == "codex_user_message_v1":
            _require_exact_keys(
                provenance,
                {
                    "source_kind",
                    "rollout_path",
                    "source_thread_id",
                    "turn_id",
                    "message_sha256",
                    "approval_token",
                },
                set(),
                f"{path}.provenance",
            )
            for field in ("rollout_path", "source_thread_id", "turn_id", "approval_token"):
                _expect_string(provenance[field], f"{path}.provenance.{field}")
            if not re.fullmatch(r"[a-f0-9]{64}", str(provenance["message_sha256"])):
                _fail(
                    f"{path}.provenance.message_sha256",
                    "must be a lowercase SHA-256 digest",
                )
        elif source_kind == "approval_receipt_v1":
            _require_exact_keys(
                provenance,
                {"source_kind", "receipt_path", "receipt_sha256"},
                set(),
                f"{path}.provenance",
            )
            _expect_string(provenance["receipt_path"], f"{path}.provenance.receipt_path")
            if not re.fullmatch(r"[a-f0-9]{64}", str(provenance["receipt_sha256"])):
                _fail(
                    f"{path}.provenance.receipt_sha256",
                    "must be a lowercase SHA-256 digest",
                )
        else:
            _fail(
                f"{path}.provenance.source_kind",
                "must be codex_user_message_v1 or approval_receipt_v1",
            )


def validate_goal(goal_value: Any) -> dict[str, Any]:
    """Validate a canonical Goal and return a defensive copy."""

    goal = _expect_dict(goal_value, "goal")
    required = {
        "schema_version",
        "goal_id",
        "revision",
        "mission",
        "must_have_ledger",
        "sections",
        "claim_policy",
        "completion_rule",
        "approval_authorities",
        "approval_registry",
        "approved_scope_delta_registry",
    }
    _require_exact_keys(goal, required, {"resolution"}, "goal")
    if goal["schema_version"] != GOAL_SCHEMA_VERSION:
        _fail("goal.schema_version", f"must be {GOAL_SCHEMA_VERSION}")
    _expect_string(goal["goal_id"], "goal.goal_id")
    _expect_string(goal["revision"], "goal.revision")
    _expect_string(goal["mission"], "goal.mission")

    ledger = _expect_list(goal["must_have_ledger"], "goal.must_have_ledger")
    if not ledger:
        _fail("goal.must_have_ledger", "must not be empty")
    requirement_ids: set[str] = set()
    for index, raw in enumerate(ledger):
        path = f"goal.must_have_ledger[{index}]"
        item = _expect_dict(raw, path)
        _require_exact_keys(item, {"requirement_id", "requirement", "evidence", "status"}, set(), path)
        requirement_id = _expect_string(item["requirement_id"], f"{path}.requirement_id")
        if requirement_id in requirement_ids:
            _fail(f"{path}.requirement_id", "must be unique")
        requirement_ids.add(requirement_id)
        _expect_string(item["requirement"], f"{path}.requirement")
        _expect_string(item["evidence"], f"{path}.evidence")
        if item["status"] not in ALLOWED_MUST_HAVE_STATUSES:
            _fail(f"{path}.status", f"must be one of {sorted(ALLOWED_MUST_HAVE_STATUSES)}")

    sections = _expect_dict(goal["sections"], "goal.sections")
    if not sections:
        _fail("goal.sections", "must not be empty")
    reserved_section_names = set(required) | {"resolution"}
    for key, value in sections.items():
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key):
            _fail("goal.sections", f"invalid section name: {key!r}")
        if key in reserved_section_names:
            _fail("goal.sections", f"section name collides with canonical Goal field: {key}")
        _scan_nested_claim_carriers(value, f"goal.sections.{key}")

    claim_ids = _validate_claim_policy(goal["claim_policy"])
    completion = _expect_dict(goal["completion_rule"], "goal.completion_rule")
    _require_exact_keys(completion, {"completion_claim_id", "required_status"}, set(), "goal.completion_rule")
    completion_claim_id = _expect_string(
        completion["completion_claim_id"], "goal.completion_rule.completion_claim_id"
    )
    if completion_claim_id not in claim_ids:
        _fail("goal.completion_rule.completion_claim_id", f"unknown claim id: {completion_claim_id}")
    if completion_claim_id not in goal["claim_policy"]["allowed_claim_ids"]:
        _fail("goal.completion_rule.completion_claim_id", "completion claim must be allowed")
    if completion["required_status"] != "landed":
        _fail("goal.completion_rule.required_status", "must be landed")

    _validate_approval_registry(goal)
    delta_registry = _expect_list(
        goal["approved_scope_delta_registry"], "goal.approved_scope_delta_registry"
    )
    if any(not isinstance(item, str) or not item for item in delta_registry):
        _fail("goal.approved_scope_delta_registry", "items must be non-empty strings")
    if len(delta_registry) != len(set(delta_registry)):
        _fail("goal.approved_scope_delta_registry", "items must be unique")

    if "resolution" in goal:
        resolution = _expect_dict(goal["resolution"], "goal.resolution")
        _require_exact_keys(
            resolution, {"base_revision", "base_digest", "applied_patch_ids"}, set(), "goal.resolution"
        )
        _expect_string(resolution["base_revision"], "goal.resolution.base_revision")
        if not re.fullmatch(r"[a-f0-9]{64}", str(resolution["base_digest"])):
            _fail("goal.resolution.base_digest", "must be a lowercase SHA-256 digest")
        patch_ids = _expect_list(resolution["applied_patch_ids"], "goal.resolution.applied_patch_ids")
        if any(not isinstance(item, str) or not item for item in patch_ids):
            _fail("goal.resolution.applied_patch_ids", "items must be non-empty strings")
        if len(patch_ids) != len(set(patch_ids)):
            _fail("goal.resolution.applied_patch_ids", "items must be unique")
    return copy.deepcopy(goal)


def validate_patch(patch_value: Any) -> dict[str, Any]:
    """Validate patch shape independently from a base Goal."""

    patch = _expect_dict(patch_value, "patch")
    required = {
        "schema_version",
        "patch_id",
        "base_goal_id",
        "base_revision",
        "base_digest",
        "sequence",
        "target_section",
        "replacement",
        "reason",
        "scope_delta",
        "approval_ref",
        "conflicts_with",
    }
    _require_exact_keys(patch, required, set(), "patch")
    if patch["schema_version"] != PATCH_SCHEMA_VERSION:
        _fail("patch.schema_version", f"must be {PATCH_SCHEMA_VERSION}")
    for field in ("patch_id", "base_goal_id", "base_revision", "target_section", "reason"):
        _expect_string(patch[field], f"patch.{field}")
    if not re.fullmatch(r"[a-f0-9]{64}", str(patch["base_digest"])):
        _fail("patch.base_digest", "must be a lowercase SHA-256 digest")
    if isinstance(patch["sequence"], bool) or not isinstance(patch["sequence"], int) or patch["sequence"] < 1:
        _fail("patch.sequence", "must be an integer >= 1")
    conflicts = _expect_list(patch["conflicts_with"], "patch.conflicts_with")
    if any(not isinstance(item, str) or not item for item in conflicts):
        _fail("patch.conflicts_with", "items must be non-empty strings")
    if len(conflicts) != len(set(conflicts)):
        _fail("patch.conflicts_with", "items must be unique")
    if patch["patch_id"] in conflicts:
        _fail("patch.conflicts_with", "patch cannot conflict with itself")
    if patch["approval_ref"] is not None:
        _expect_string(patch["approval_ref"], "patch.approval_ref")

    scope_delta = patch["scope_delta"]
    if scope_delta != "none":
        scope = _expect_dict(scope_delta, "patch.scope_delta")
        _require_exact_keys(scope, {"scope_delta_id", "description", "impact"}, set(), "patch.scope_delta")
        _expect_string(scope["scope_delta_id"], "patch.scope_delta.scope_delta_id")
        _expect_string(scope["description"], "patch.scope_delta.description")
        if scope["impact"] not in ALLOWED_SCOPE_IMPACTS:
            _fail("patch.scope_delta.impact", f"must be one of {sorted(ALLOWED_SCOPE_IMPACTS)}")
    return copy.deepcopy(patch)


def _target_kind(goal: Mapping[str, Any], target: str) -> tuple[str, str]:
    normalized = target.replace("/", ".")
    if normalized.startswith("sections."):
        section_name = normalized.split(".", 1)[1]
        if "." in section_name or not section_name:
            _fail("patch.target_section", "nested paths below a section are not supported")
        if section_name not in goal["sections"]:
            _fail("patch.target_section", f"unknown section: {section_name}")
        return "section", section_name
    if target in goal:
        return "top", target
    if target in goal["sections"]:
        return "section", target
    _fail("patch.target_section", f"unknown target: {target}")


def _message_text(payload: Mapping[str, Any], path: str) -> str:
    content = payload.get("content")
    if isinstance(content, str):
        return content
    if not isinstance(content, list) or not content:
        _fail(path, "message content must contain text")
    text_parts: list[str] = []
    for index, item in enumerate(content):
        if not isinstance(item, dict):
            _fail(f"{path}.content[{index}]", "content item must be an object")
        if item.get("type") not in {"input_text", "text"} or not isinstance(item.get("text"), str):
            _fail(f"{path}.content[{index}]", "approval message must contain text-only items")
        text_parts.append(item["text"])
    return "".join(text_parts)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _load_approval_message(
    provenance: Mapping[str, Any], trusted_rollout_roots: Sequence[Path]
) -> str:
    rollout_path = Path(provenance["rollout_path"])
    if not rollout_path.is_absolute():
        rollout_path = REPO_ROOT / rollout_path
    try:
        resolved_path = rollout_path.resolve(strict=True)
    except OSError as exc:
        _fail("approval.provenance.rollout_path", f"cannot read source: {exc}")
    resolved_roots = [Path(root).expanduser().resolve() for root in trusted_rollout_roots]
    if not any(_is_within(resolved_path, root) for root in resolved_roots):
        _fail(
            "approval.provenance.rollout_path",
            "source is outside trusted Codex rollout roots",
        )
    try:
        lines = resolved_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        _fail("approval.provenance.rollout_path", f"cannot read source: {exc}")

    events: list[tuple[int, dict[str, Any]]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            _fail(
                "approval.provenance.rollout_path",
                f"invalid JSONL at line {line_number}: {exc.msg}",
            )
        if not isinstance(event, dict):
            _fail(
                "approval.provenance.rollout_path",
                f"JSONL event at line {line_number} must be an object",
            )
        events.append((line_number, event))

    session_meta_events = [
        (line_number, event)
        for line_number, event in events
        if event.get("type") == "session_meta"
    ]
    if len(session_meta_events) != 1:
        _fail(
            "approval.provenance.source_thread_id",
            f"expected exactly one session_meta event, found {len(session_meta_events)}",
        )
    meta_line, meta_event = session_meta_events[0]
    meta_payload = meta_event.get("payload")
    if not isinstance(meta_payload, dict):
        _fail(
            "approval.provenance.source_thread_id",
            f"session_meta payload at line {meta_line} must be an object",
        )
    thread_source = meta_payload.get("thread_source")
    if thread_source != "user":
        _fail(
            "approval.provenance.source_thread_id",
            "session_meta thread_source must be user",
        )
    source_thread_id = meta_payload.get("id")
    if source_thread_id is None:
        source_thread_id = meta_payload.get("session_id")
    if not isinstance(source_thread_id, str) or not source_thread_id.strip():
        _fail(
            "approval.provenance.source_thread_id",
            "session_meta payload must contain a non-empty id or session_id",
        )
    if source_thread_id != provenance["source_thread_id"]:
        _fail(
            "approval.provenance.source_thread_id",
            "source thread id does not match session_meta payload",
        )

    matching_messages: list[tuple[str, str]] = []
    for line_number, event in events:
        payload = event.get("payload")
        if event.get("type") != "response_item" or not isinstance(payload, dict):
            continue
        if payload.get("type") != "message":
            continue
        metadata = payload.get("internal_chat_message_metadata_passthrough")
        metadata_turn_id = metadata.get("turn_id") if isinstance(metadata, dict) else None
        turn_id = payload.get("turn_id", metadata_turn_id or event.get("turn_id"))
        if turn_id != provenance["turn_id"]:
            continue
        role = payload.get("role")
        text = _message_text(payload, f"rollout line {line_number}")
        matching_messages.append((str(role), text))
    if not matching_messages:
        _fail(
            "approval.provenance.turn_id",
            "no message found for the bound turn id",
        )
    expected_hash = provenance["message_sha256"]
    hash_matches = [
        (role, message)
        for role, message in matching_messages
        if hashlib.sha256(message.encode("utf-8")).hexdigest() == expected_hash
    ]
    if len(hash_matches) != 1:
        if len(matching_messages) == 1 and matching_messages[0][0] != "user":
            _fail("approval.provenance", "matching source message role must be user")
        if len(matching_messages) == 1:
            _fail("approval.provenance.message_sha256", "source message hash mismatch")
        _fail(
            "approval.provenance.message_sha256",
            f"expected one hash-bound message in turn, found {len(hash_matches)}",
        )
    role, message = hash_matches[0]
    if role != "user":
        _fail("approval.provenance", "matching source message role must be user")
    return message


def _parse_approval_token(message: str) -> dict[str, Any]:
    token_lines = [line for line in message.splitlines() if line.startswith(APPROVAL_TOKEN_PREFIX)]
    if len(token_lines) != 1:
        _fail("approval.provenance.approval_token", "expected exactly one explicit approval token")
    token_json = token_lines[0][len(APPROVAL_TOKEN_PREFIX) :]
    try:
        token = json.loads(token_json)
    except json.JSONDecodeError as exc:
        _fail("approval.provenance.approval_token", f"invalid token JSON: {exc.msg}")
    token = _expect_dict(token, "approval.provenance.approval_token")
    _require_exact_keys(
        token,
        {
            "approval_token",
            "approval_id",
            "authority_id",
            "base_digest",
            "revision",
            "patch_id",
            "target",
            "scope_delta_ids",
        },
        set(),
        "approval.provenance.approval_token",
    )
    return token


def _load_approval_receipt(
    provenance: Mapping[str, Any], trusted_receipt_roots: Sequence[Path]
) -> dict[str, Any]:
    """Load a provider-neutral receipt from an explicitly trusted external root."""

    receipt_path = Path(provenance["receipt_path"])
    if not receipt_path.is_absolute():
        receipt_path = REPO_ROOT / receipt_path
    try:
        resolved_path = receipt_path.resolve(strict=True)
    except OSError as exc:
        _fail("approval.provenance.receipt_path", f"cannot read source: {exc}")
    resolved_roots = [Path(root).expanduser().resolve() for root in trusted_receipt_roots]
    if not any(_is_within(resolved_path, root) for root in resolved_roots):
        _fail(
            "approval.provenance.receipt_path",
            "source is outside explicitly trusted approval receipt roots",
        )
    try:
        raw = resolved_path.read_bytes()
    except OSError as exc:
        _fail("approval.provenance.receipt_path", f"cannot read source: {exc}")
    if hashlib.sha256(raw).hexdigest() != provenance["receipt_sha256"]:
        _fail("approval.provenance.receipt_sha256", "receipt content hash mismatch")
    try:
        receipt = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("approval.provenance.receipt_path", f"invalid UTF-8 JSON receipt: {exc}")
    receipt = _expect_dict(receipt, "approval receipt")
    _require_exact_keys(
        receipt,
        {
            "schema_version",
            "approval_id",
            "authority_kind",
            "authority_id",
            "base_digest",
            "revision",
            "patch_id",
            "target",
            "scope_delta_ids",
            "approval_statement",
            "approved_at",
        },
        {"provider", "source_ref"},
        "approval receipt",
    )
    if receipt["schema_version"] != APPROVAL_RECEIPT_SCHEMA_VERSION:
        _fail("approval receipt.schema_version", f"must be {APPROVAL_RECEIPT_SCHEMA_VERSION}")
    for field in (
        "approval_id",
        "authority_kind",
        "authority_id",
        "base_digest",
        "revision",
        "patch_id",
        "target",
        "approval_statement",
        "approved_at",
    ):
        _expect_string(receipt[field], f"approval receipt.{field}")
    if receipt["authority_kind"] != "human":
        _fail("approval receipt.authority_kind", "must be human")
    if not re.fullmatch(r"[a-f0-9]{64}", receipt["base_digest"]):
        _fail("approval receipt.base_digest", "must be a lowercase SHA-256 digest")
    scope_delta_ids = _expect_list(receipt["scope_delta_ids"], "approval receipt.scope_delta_ids")
    if any(not isinstance(value, str) or not value for value in scope_delta_ids):
        _fail("approval receipt.scope_delta_ids", "items must be non-empty strings")
    if len(scope_delta_ids) != len(set(scope_delta_ids)):
        _fail("approval receipt.scope_delta_ids", "items must be unique")
    return receipt


def _verify_approval_provenance(
    approval: Mapping[str, Any],
    patch: Mapping[str, Any],
    trusted_rollout_roots: Sequence[Path],
) -> None:
    provenance = approval["provenance"]
    expected = {
        "approval_id": approval["approval_id"],
        "authority_id": approval["authority_id"],
        "base_digest": patch["base_digest"],
        "revision": patch["base_revision"],
        "patch_id": patch["patch_id"],
        "target": patch["target_section"],
        "scope_delta_ids": approval["scope_delta_ids"],
    }
    if provenance["source_kind"] == "codex_user_message_v1":
        message = _load_approval_message(provenance, trusted_rollout_roots)
        token = _parse_approval_token(message)
        expected["approval_token"] = provenance["approval_token"]
        source_label = "approval.provenance.approval_token"
    else:
        token = _load_approval_receipt(provenance, trusted_rollout_roots)
        expected["authority_kind"] = "human"
        source_label = "approval.provenance.receipt_path"
    for field, expected_value in expected.items():
        if token.get(field) != expected_value:
            _fail(source_label, f"approval source {field} binding mismatch")


def _approval_for_patch(
    goal: Mapping[str, Any],
    patch: Mapping[str, Any],
    *,
    required: bool,
    trusted_rollout_roots: Sequence[Path],
) -> Mapping[str, Any] | None:
    approval_ref = patch["approval_ref"]
    if approval_ref is None:
        if required:
            _fail("patch.approval_ref", "matching human approval is required")
        return None
    approvals = {item["approval_id"]: item for item in goal["approval_registry"]}
    if approval_ref not in approvals:
        _fail("patch.approval_ref", f"unknown approval id: {approval_ref}")
    approval = approvals[approval_ref]
    expected = {
        "authority_kind": "human",
        "status": "approved",
        "base_digest": patch["base_digest"],
        "revision": patch["base_revision"],
    }
    for field, value in expected.items():
        if approval[field] != value:
            _fail("patch.approval_ref", f"approval {field} binding mismatch")
    if patch["patch_id"] not in approval["allowed_patch_ids"]:
        _fail("patch.approval_ref", "approval does not bind this patch id")
    if patch["target_section"] not in approval["allowed_targets"]:
        _fail("patch.approval_ref", "approval does not bind this target")
    if patch["scope_delta"] != "none":
        scope_delta_id = patch["scope_delta"]["scope_delta_id"]
        if scope_delta_id not in approval["scope_delta_ids"]:
            _fail("patch.approval_ref", "approval does not bind this scope delta")
        if scope_delta_id not in goal["approved_scope_delta_registry"]:
            _fail("patch.scope_delta", "scope delta is absent from approved registry")
    elif approval["scope_delta_ids"]:
        _fail("patch.approval_ref", "approval scope-delta binding is broader than this patch")
    _verify_approval_provenance(approval, patch, trusted_rollout_roots)
    return approval


def validate_patch_set(
    goal_value: Any,
    patch_values: Sequence[Any],
    *,
    trusted_rollout_roots: Sequence[Path] | None = None,
) -> list[dict[str, Any]]:
    """Bind a complete ordered patch set to its base Goal and approvals."""

    goal = validate_goal(goal_value)
    source_roots = tuple(trusted_rollout_roots or DEFAULT_APPROVAL_SOURCE_ROOTS)
    patches = [validate_patch(item) for item in patch_values]
    if not patches:
        return []
    ids = [patch["patch_id"] for patch in patches]
    if len(ids) != len(set(ids)):
        _fail("patches", "patch ids must be unique")
    sequences = [patch["sequence"] for patch in patches]
    if len(sequences) != len(set(sequences)):
        _fail("patches", "sequence values must be unique")
    ordered = sorted(patches, key=lambda patch: patch["sequence"])
    actual_sequences = [patch["sequence"] for patch in ordered]
    expected_sequences = list(range(1, len(ordered) + 1))
    if actual_sequences != expected_sequences:
        _fail("patches", f"sequence must be contiguous from 1; got {actual_sequences}")

    base_digest = goal_digest(goal)
    id_set = set(ids)
    for patch in ordered:
        if patch["base_goal_id"] != goal["goal_id"]:
            _fail("patch.base_goal_id", "does not match base Goal")
        if patch["base_revision"] != goal["revision"]:
            _fail("patch.base_revision", "does not match base Goal")
        if patch["base_digest"] != base_digest:
            _fail("patch.base_digest", "does not match canonical base digest")
        conflicts = sorted(id_set.intersection(patch["conflicts_with"]))
        if conflicts:
            _fail("patch.conflicts_with", f"active conflict with {conflicts}")
        target_kind, target_name = _target_kind(goal, patch["target_section"])
        if target_kind == "top" and target_name in IMMUTABLE_TARGETS:
            _fail("patch.target_section", f"immutable Goal identity cannot be patched: {target_name}")
        protected = target_kind == "top" and target_name in PROTECTED_TARGETS
        approval_required = protected or patch["scope_delta"] != "none"
        _approval_for_patch(
            goal,
            patch,
            required=approval_required,
            trusted_rollout_roots=source_roots,
        )
        if target_kind == "section":
            _scan_nested_claim_carriers(patch["replacement"], "patch.replacement")
    return ordered


def resolve_goal(
    goal_value: Any,
    patch_values: Sequence[Any],
    *,
    trusted_rollout_roots: Sequence[Path] | None = None,
) -> dict[str, Any]:
    """Resolve a complete patch set into one deterministic executable Goal."""

    base = validate_goal(goal_value)
    patches = validate_patch_set(
        base,
        patch_values,
        trusted_rollout_roots=trusted_rollout_roots,
    )
    resolved = copy.deepcopy(base)
    base_revision = base["revision"]
    base_digest = goal_digest(base)
    for patch in patches:
        target_kind, target_name = _target_kind(resolved, patch["target_section"])
        if target_kind == "section":
            resolved["sections"][target_name] = copy.deepcopy(patch["replacement"])
        else:
            resolved[target_name] = copy.deepcopy(patch["replacement"])
    patch_ids = [patch["patch_id"] for patch in patches]
    revision_seed = canonical_json({"base_revision": base_revision, "patch_ids": patch_ids})
    resolved["revision"] = "resolved-" + hashlib.sha256(revision_seed.encode("utf-8")).hexdigest()[:16]
    resolved["resolution"] = {
        "base_revision": base_revision,
        "base_digest": base_digest,
        "applied_patch_ids": patch_ids,
    }
    return validate_goal(resolved)


def render_goal_markdown(goal_value: Any) -> str:
    """Render fixed headings plus the sole authoritative canonical JSON payload."""

    goal = validate_goal(goal_value)
    return (
        f"# Final Goal: {goal['goal_id']}\n\n"
        "## Canonical Goal Payload\n\n"
        "```json\n"
        f"{canonical_json(goal, pretty=True).rstrip()}\n"
        "```\n"
    )


def parse_goal_markdown(markdown: str) -> dict[str, Any]:
    """Parse only the canonical payload; surrounding prose has no authority."""

    if not isinstance(markdown, str):
        _fail("markdown", "must be a string")
    match = MARKDOWN_PAYLOAD_RE.match(markdown)
    if not match:
        _fail("markdown", "missing fixed canonical Goal payload")
    try:
        payload = json.loads(match.group("payload"))
    except json.JSONDecodeError as exc:
        _fail("markdown.payload", f"invalid JSON: {exc.msg}")
    return validate_goal(payload)


def diagnose_prose_claim_phrases(goal_value: Any) -> list[dict[str, str]]:
    """Return non-authoritative phrase diagnostics; findings never grant or block authority."""

    goal = validate_goal(goal_value)
    findings: list[dict[str, str]] = []

    def scan(value: Any, path: str) -> None:
        if isinstance(value, str):
            for pattern in FORBIDDEN_PROSE_PATTERNS:
                match = pattern.search(value)
                if match:
                    findings.append(
                        {
                            "path": path,
                            "phrase": match.group(0),
                            "severity": "advisory",
                            "authority": "none",
                        }
                    )
        elif isinstance(value, dict):
            for key, child in value.items():
                scan(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                scan(child, f"{path}[{index}]")

    scan(goal["mission"], "goal.mission")
    scan(goal["must_have_ledger"], "goal.must_have_ledger")
    scan(goal["sections"], "goal.sections")
    return findings


def normalize_duplication_text(text: str) -> str:
    """Normalize Unicode, Markdown headings, and whitespace for copy detection."""

    normalized = unicodedata.normalize("NFKC", text)
    normalized = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip().casefold()
    return normalized


def _validate_audit_block(raw: Any, path: str) -> dict[str, Any]:
    block = _expect_dict(raw, path)
    _require_exact_keys(
        block,
        {"block_id", "kind", "text", "source", "start_line", "end_line"},
        {"session_id"},
        path,
    )
    for field in ("block_id", "kind", "text", "source"):
        _expect_string(block[field], f"{path}.{field}")
    for field in ("start_line", "end_line"):
        if isinstance(block[field], bool) or not isinstance(block[field], int) or block[field] < 1:
            _fail(f"{path}.{field}", "must be an integer >= 1")
    if block["end_line"] < block["start_line"]:
        _fail(path, "end_line must not precede start_line")
    if "session_id" in block:
        _expect_string(block["session_id"], f"{path}.session_id")
    return copy.deepcopy(block)


def audit_duplication(
    candidate_blocks: Sequence[Any],
    reference_blocks: Sequence[Any],
    *,
    current_session_id: str | None = None,
    suppressions: Sequence[Any] = (),
    threshold: float = 0.92,
) -> dict[str, Any]:
    """Audit exact and near copies without deleting or rewriting source text."""

    if not 0.0 < threshold <= 1.0:
        _fail("threshold", "must be > 0 and <= 1")
    candidates = [
        _validate_audit_block(block, f"candidate_blocks[{index}]")
        for index, block in enumerate(candidate_blocks)
    ]
    references = [
        _validate_audit_block(block, f"reference_blocks[{index}]")
        for index, block in enumerate(reference_blocks)
    ]
    all_ids = [block["block_id"] for block in candidates + references]
    if len(all_ids) != len(set(all_ids)):
        _fail("blocks", "block_id values must be globally unique")

    suppression_map: dict[tuple[str, str, str], str] = {}
    for index, raw in enumerate(suppressions):
        path = f"suppressions[{index}]"
        item = _expect_dict(raw, path)
        _require_exact_keys(
            item,
            {"candidate_id", "reference_id", "reason", "finding_type"},
            set(),
            path,
        )
        for field in ("candidate_id", "reference_id", "reason", "finding_type"):
            _expect_string(item[field], f"{path}.{field}")
        finding_type = item["finding_type"]
        if finding_type not in {"near", "non_current_session"}:
            _fail(
                f"{path}.finding_type",
                "suppression is limited to advisory near/non_current_session findings",
            )
        suppression_map[(item["candidate_id"], item["reference_id"], finding_type)] = item["reason"]

    findings: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []

    def emit(finding: dict[str, Any]) -> None:
        key_specific = (
            finding["candidate_id"],
            finding["reference_id"],
            finding["finding_type"],
        )
        reason = suppression_map.get(key_specific)
        if reason is not None and finding["severity"] != "blocker":
            suppressed.append({**finding, "suppression_reason": reason})
        else:
            findings.append(finding)

    for candidate_index, candidate in enumerate(candidates):
        candidate_text = normalize_duplication_text(candidate["text"])
        if not candidate_text:
            continue
        # Earlier candidate blocks are references for repeated requirements in
        # the same artifact; external references cover governance and AC copy.
        comparison_references = references + candidates[:candidate_index]
        for reference in comparison_references:
            reference_text = normalize_duplication_text(reference["text"])
            if not reference_text:
                continue
            ratio = SequenceMatcher(None, candidate_text, reference_text, autojunk=False).ratio()
            finding_type = "exact" if candidate_text == reference_text else "near"
            if finding_type == "near" and ratio < threshold:
                continue
            severity = "blocker" if finding_type == "exact" else "advisory"
            emit(
                {
                    "finding_type": finding_type,
                    "severity": severity,
                    "candidate_id": candidate["block_id"],
                    "reference_id": reference["block_id"],
                    "reference_kind": reference["kind"],
                    "similarity": round(ratio, 6),
                    "candidate_span": {
                        "source": candidate["source"],
                        "start_line": candidate["start_line"],
                        "end_line": candidate["end_line"],
                    },
                    "reference_span": {
                        "source": reference["source"],
                        "start_line": reference["start_line"],
                        "end_line": reference["end_line"],
                    },
                }
            )
        if (
            current_session_id
            and candidate.get("session_id")
            and candidate["session_id"] != current_session_id
        ):
            pseudo_reference = f"session:{candidate['session_id']}"
            emit(
                {
                    "finding_type": "non_current_session",
                    "severity": "advisory",
                    "candidate_id": candidate["block_id"],
                    "reference_id": pseudo_reference,
                    "reference_kind": "session_detail",
                    "similarity": None,
                    "candidate_span": {
                        "source": candidate["source"],
                        "start_line": candidate["start_line"],
                        "end_line": candidate["end_line"],
                    },
                    "reference_span": None,
                }
            )

    findings.sort(key=lambda item: (item["candidate_id"], item["reference_id"], item["finding_type"]))
    suppressed.sort(key=lambda item: (item["candidate_id"], item["reference_id"], item["finding_type"]))
    blockers = sum(finding["severity"] == "blocker" for finding in findings)
    return {
        "schema_version": "goal_duplication_audit_v1",
        "threshold": threshold,
        "normalization": "NFKC+markdown-heading-strip+whitespace-collapse+casefold",
        "verdict": "fail" if blockers else "pass",
        "blocking_count": blockers,
        "advisory_count": sum(finding["severity"] == "advisory" for finding in findings),
        "findings": findings,
        "suppressed_findings": suppressed,
    }


def audit_duplication_document(document_value: Any) -> dict[str, Any]:
    document = _expect_dict(document_value, "audit")
    _require_exact_keys(
        document,
        {"candidate_blocks", "reference_blocks"},
        {"current_session_id", "suppressions", "threshold"},
        "audit",
    )
    current_session_id = document.get("current_session_id")
    if current_session_id is not None:
        _expect_string(current_session_id, "audit.current_session_id")
    return audit_duplication(
        _expect_list(document["candidate_blocks"], "audit.candidate_blocks"),
        _expect_list(document["reference_blocks"], "audit.reference_blocks"),
        current_session_id=current_session_id,
        suppressions=_expect_list(document.get("suppressions", []), "audit.suppressions"),
        threshold=document.get("threshold", 0.92),
    )


# Explicit public names keep API callers independent from CLI terminology.
validate_goal_contract = validate_goal
validate_goal_patch = validate_patch
resolve_goal_patches = resolve_goal


def _read_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise GoalPatchError(f"{path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise GoalPatchError(f"{path}: invalid JSON: {exc.msg}") from exc


def _write_output(value: str, output: str | None) -> None:
    if output:
        Path(output).write_text(value, encoding="utf-8")
    else:
        sys.stdout.write(value)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_goal_parser = subparsers.add_parser("validate-goal")
    validate_goal_parser.add_argument("goal")

    validate_patch_parser = subparsers.add_parser("validate-patch")
    validate_patch_parser.add_argument("patch")
    validate_patch_parser.add_argument("--goal")
    validate_patch_parser.add_argument("--approval-source-root", action="append")

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("goal")
    resolve_parser.add_argument("patches", nargs="+")
    resolve_parser.add_argument("--format", choices=("json", "markdown"), default="json")
    resolve_parser.add_argument("--output")
    resolve_parser.add_argument("--approval-source-root", action="append")

    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("goal")
    render_parser.add_argument("--output")

    parse_parser = subparsers.add_parser("parse")
    parse_parser.add_argument("markdown")
    parse_parser.add_argument("--output")

    audit_parser = subparsers.add_parser("audit-duplication")
    audit_parser.add_argument("audit")
    audit_parser.add_argument("--output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-goal":
            goal = validate_goal(_read_json(args.goal))
            _write_output(canonical_json({"valid": True, "digest": goal_digest(goal)}, pretty=True), None)
        elif args.command == "validate-patch":
            patch = validate_patch(_read_json(args.patch))
            if args.goal:
                validate_patch_set(
                    _read_json(args.goal),
                    [patch],
                    trusted_rollout_roots=args.approval_source_root,
                )
            _write_output(canonical_json({"valid": True, "patch_id": patch["patch_id"]}, pretty=True), None)
        elif args.command == "resolve":
            resolved = resolve_goal(
                _read_json(args.goal),
                [_read_json(path) for path in args.patches],
                trusted_rollout_roots=args.approval_source_root,
            )
            output = render_goal_markdown(resolved) if args.format == "markdown" else canonical_json(resolved, pretty=True)
            _write_output(output, args.output)
        elif args.command == "render":
            _write_output(render_goal_markdown(_read_json(args.goal)), args.output)
        elif args.command == "parse":
            markdown = Path(args.markdown).read_text(encoding="utf-8")
            _write_output(canonical_json(parse_goal_markdown(markdown), pretty=True), args.output)
        elif args.command == "audit-duplication":
            result = audit_duplication_document(_read_json(args.audit))
            _write_output(canonical_json(result, pretty=True), args.output)
            return 1 if result["verdict"] == "fail" else 0
        return 0
    except (GoalPatchError, OSError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

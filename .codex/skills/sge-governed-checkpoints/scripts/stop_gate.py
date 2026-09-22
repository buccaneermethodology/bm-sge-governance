#!/usr/bin/env python3
"""Fail-closed deterministic Loop Goal Stop Gate v1."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

GATE_VERSION = "1.0.0"
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"
REQUIRED_EVIDENCE = {
    "goal", "completion_rule", "obligation_inventory", "final_diff",
    "independent_validation", "closeout", "dashboard_state", "kb_disposition",
    "original_plan_coverage", "scope_delta_audit", "post_closeout_reconciliation",
}
ADMISSIBLE = {
    "business_semantics": "BUSINESS_SEMANTIC_AUTHORITY_REQUIRED",
    "scope_delta": "UNAPPROVED_SCOPE_DELTA",
    "destructive_action": "DESTRUCTIVE_ACTION_AUTHORITY_REQUIRED",
    "external_write": "EXTERNAL_WRITE_AUTHORITY_REQUIRED",
    "release": "RELEASE_AUTHORITY_REQUIRED",
    "declared_approval_checkpoint": "DECLARED_APPROVAL_CHECKPOINT_REQUIRED",
    "evidence_not_applicable": "EVIDENCE_NOT_APPLICABLE_AUTHORITY_MISSING",
    "required_capability_external_resolution": "REQUIRED_CAPABILITY_EXTERNAL_RESOLUTION",
}


class InvalidAttempt(Exception):
    def __init__(self, reason: str):
        self.reason = reason


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside_regular(raw: str, root: Path) -> Path:
    path = Path(raw)
    candidate = path if path.is_absolute() else root / path
    if candidate.is_symlink():
        raise InvalidAttempt("STATE_REFERENCE_UNREADABLE")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError):
        raise InvalidAttempt("STATE_PATH_OUTSIDE_ALLOWED_ROOT")
    if not resolved.is_file():
        raise InvalidAttempt("STATE_REFERENCE_UNREADABLE")
    return resolved


def _ref(raw: str, declared: str, kind: str, root: Path, refs: list[dict[str, Any]]) -> Path:
    path = _inside_regular(raw, root)
    observed = _sha(path)
    refs.append({"path": raw, "sha256": declared, "observed_sha256": observed,
                 "digest_match": observed == declared, "evidence_kind": kind})
    if observed != declared:
        raise InvalidAttempt("STATE_REFERENCE_DIGEST_MISMATCH")
    return path


def _load_json(path: Path, reason: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
        raise InvalidAttempt(reason)
    if not isinstance(value, dict):
        raise InvalidAttempt(reason)
    return value


def _closed(value: Any, required: set[str], optional: set[str] = set()) -> bool:
    return isinstance(value, dict) and set(value) == required | (set(value) & optional) and required <= set(value)


def _validate_predicate_shape(node: Any) -> None:
    if not isinstance(node, dict) or len(node) != 1:
        raise InvalidAttempt("COMPLETION_PREDICATE_INVALID")
    if "all_of" in node:
        children = node["all_of"]
        if not isinstance(children, list) or not children:
            raise InvalidAttempt("COMPLETION_PREDICATE_INVALID")
        for child in children:
            _validate_predicate_shape(child)
        return
    atom = node.get("atom")
    if not isinstance(atom, dict) or not {"fact", "operator"} <= set(atom) or set(atom) - {"fact", "operator", "required_ids", "required_kinds"}:
        raise InvalidAttempt("COMPLETION_PREDICATE_INVALID")
    allowed = {
        ("completion.remaining_must_have_ids", "empty"),
        ("scope_deltas", "none_unapproved"),
        ("completion.work_units", "ids_terminal"),
        ("human_decisions", "none_pending_admissible"),
        ("final_evidence", "required_kinds_bound"),
    }
    if (atom["fact"], atom["operator"]) not in allowed:
        raise InvalidAttempt("COMPLETION_PREDICATE_INVALID")
    if atom["operator"] == "ids_terminal" and not isinstance(atom.get("required_ids"), list):
        raise InvalidAttempt("COMPLETION_PREDICATE_INVALID")
    if atom["operator"] == "required_kinds_bound" and not isinstance(atom.get("required_kinds"), list):
        raise InvalidAttempt("COMPLETION_PREDICATE_INVALID")


def _verify_approval_authority(receipt: dict[str, Any], root: Path, refs: list[dict[str, Any]]) -> None:
    try:
        path = _inside_regular(receipt["authority_ref"], root)
        observed = _sha(path)
    except InvalidAttempt as exc:
        mapped = ("APPROVAL_AUTHORITY_PATH_OUTSIDE_ALLOWED_ROOT"
                  if exc.reason == "STATE_PATH_OUTSIDE_ALLOWED_ROOT"
                  else "APPROVAL_AUTHORITY_REFERENCE_UNREADABLE")
        raise InvalidAttempt(mapped)
    refs.append({"path": receipt["authority_ref"], "sha256": receipt["authority_sha256"],
                 "observed_sha256": observed, "digest_match": observed == receipt["authority_sha256"],
                 "evidence_kind": "approval_authority"})
    if observed != receipt["authority_sha256"]:
        raise InvalidAttempt("APPROVAL_AUTHORITY_DIGEST_MISMATCH")


def _receipt_by_id(state: dict[str, Any], receipt_id: str | None) -> dict[str, Any] | None:
    return next((r for r in state["approval_receipts"] if r["receipt_id"] == receipt_id), None)


def _approved(decision: dict[str, Any], state: dict[str, Any], root: Path, refs: list[dict[str, Any]]) -> bool:
    receipt_id = decision.get("existing_approval_receipt_id")
    if not receipt_id:
        return False
    when = datetime.fromisoformat(state["created_at"].replace("Z", "+00:00"))
    for receipt in state["approval_receipts"]:
        if receipt["receipt_id"] != receipt_id or receipt["status"] != "valid":
            continue
        issued = datetime.fromisoformat(receipt["issued_at"].replace("Z", "+00:00"))
        until = datetime.fromisoformat(receipt["valid_until"].replace("Z", "+00:00"))
        _verify_approval_authority(receipt, root, refs)
        scope = decision["required_scope"]
        subjects = {decision["blocks_work_unit_id"], *scope.get("work_unit_ids", []), *scope.get("requirement_ids", [])}
        if receipt["authority_type"] == decision["authority_type"] and receipt["scope"] == scope and subjects <= set(receipt["subject_ids"]) and issued <= when <= until:
            return True
    return False


def _pending_admissible(state: dict[str, Any], root: Path, refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current = state["current_work_unit"]["work_unit_id"]
    next_id = state["next_work_unit"]["work_unit_id"]
    return [d for d in state["human_decisions"] if d["status"] == "pending"
            and d["authority_type"] in ADMISSIBLE
            and d["blocks_work_unit_id"] in {current, next_id}
            and not _approved(d, state, root, refs)]


def _valid_not_applicable(evidence: dict[str, Any], state: dict[str, Any], root: Path,
                          refs: list[dict[str, Any]]) -> bool:
    receipt = _receipt_by_id(state, evidence.get("authority_receipt_id"))
    if receipt is None or receipt["authority_type"] != "evidence_not_applicable" or receipt["status"] != "valid":
        raise InvalidAttempt("EVIDENCE_NOT_APPLICABLE_AUTHORITY_MISSING")
    scope = receipt["scope"]
    requirements = {m["must_have_id"] for m in state["completion"]["original_must_haves"]}
    expected = {"scope_type": "evidence_not_applicable", "evidence_kinds": [evidence["evidence_kind"]],
                "covered_ids": evidence["covered_ids"], "requirement_ids": sorted(requirements)}
    when = datetime.fromisoformat(state["created_at"].replace("Z", "+00:00"))
    issued = datetime.fromisoformat(receipt["issued_at"].replace("Z", "+00:00"))
    until = datetime.fromisoformat(receipt["valid_until"].replace("Z", "+00:00"))
    subjects = {evidence["evidence_kind"], *evidence["covered_ids"], *requirements}
    if scope != expected or not subjects <= set(receipt["subject_ids"]) or not issued <= when <= until:
        raise InvalidAttempt("EVIDENCE_NOT_APPLICABLE_AUTHORITY_MISSING")
    _verify_approval_authority(receipt, root, refs)
    return True


def _eval(node: dict[str, Any], state: dict[str, Any], root: Path, refs: list[dict[str, Any]]) -> bool:
    if "all_of" in node:
        return all(_eval(child, state, root, refs) for child in node["all_of"])
    atom = node["atom"]
    op = atom["operator"]
    if op == "empty": return not state["completion"]["remaining_must_have_ids"]
    if op == "none_unapproved": return not any(x["approval_status"] != "approved" for x in state["scope_deltas"])
    if op == "ids_terminal":
        terminal = {"closed", "approved_not_applicable", "blocked_by_approved_termination"}
        statuses = {x["work_unit_id"]: x["status"] for x in state["completion"]["work_units"]}
        return all(statuses.get(i) in terminal for i in atom["required_ids"])
    if op == "none_pending_admissible": return not _pending_admissible(state, root, refs)
    if op == "required_kinds_bound":
        bound = {x["evidence_kind"] for x in state["final_evidence"] if x["binding_status"] == "bound"}
        for evidence in state["final_evidence"]:
            if evidence["binding_status"] == "not_applicable_with_authority" and _valid_not_applicable(evidence, state, root, refs):
                bound.add(evidence["evidence_kind"])
        return set(atom["required_kinds"]) <= bound
    raise InvalidAttempt("COMPLETION_PREDICATE_INVALID")


def _receipt(state_path: Path, state_sha: str | None, state: dict[str, Any] | None,
             status: str, verdict: str | None, reasons: list[str], action: str,
             refs: list[dict[str, Any]], predicate_satisfied: bool | None) -> dict[str, Any]:
    mapping = {None: (False, "PROGRESS_ONLY"), "CONTINUE": (False, "PROGRESS_ONLY"),
               "PAUSE_ALLOWED": (False, "DECISION_REQUEST"), "GOAL_COMPLETE": (True, "FINAL_CLOSEOUT")}
    final_allowed, message = mapping[verdict]
    goal = state.get("goal", {}) if isinstance(state, dict) else {}
    sid = state.get("state_id") if isinstance(state, dict) else None
    identity = hashlib.sha256(f"{state_sha}:{status}:{','.join(reasons)}".encode()).hexdigest()[:20]
    return {
        "schema_version": "stop_gate_receipt_v1", "receipt_id": f"stop-gate-{identity}",
        "gate_version": GATE_VERSION, "evaluated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "input_state_ref": str(state_path), "input_state_sha256": state_sha,
        "receipt_status": status, "verdict": verdict, "reason_codes": reasons,
        "final_allowed": final_allowed, "message_class": message, "next_action": action,
        "input_state_summary": {"state_id": sid, "goal_id": goal.get("goal_id"),
            "goal_terminal": goal.get("goal_terminal"), "completion_predicate_id": goal.get("completion_predicate_id"),
            "completion_predicate_satisfied": predicate_satisfied},
        "referenced_files": refs,
    }


def evaluate(state_path: Path, allowed_root: Path, authority_source_root: Path | None,
             authority_root: Path | None, expected_authority_sha: str | None) -> tuple[dict[str, Any], int]:
    refs: list[dict[str, Any]] = []
    state: dict[str, Any] | None = None
    state_sha: str | None = None
    satisfied: bool | None = None
    try:
        actual_state_path = _inside_regular(str(state_path), allowed_root)
        state_sha = _sha(actual_state_path)
        state = _load_json(actual_state_path, "STATE_SCHEMA_INVALID")
        schema = _load_json(SCHEMA_DIR / "loop_state_v1.schema.json", "STATE_SCHEMA_INVALID")
        try: jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(state)
        except jsonschema.ValidationError: raise InvalidAttempt("STATE_SCHEMA_INVALID")
        if state["current_work_unit"]["parent_goal_id"] != state["goal"]["goal_id"]:
            raise InvalidAttempt("STATE_SCHEMA_INVALID")
        computed_remaining = {x["must_have_id"] for x in state["completion"]["original_must_haves"] if x["status"] == "pending"}
        if computed_remaining != set(state["completion"]["remaining_must_have_ids"]):
            raise InvalidAttempt("STATE_SCHEMA_INVALID")
        if authority_source_root is None or authority_root is None or expected_authority_sha is None:
            raise InvalidAttempt("GOAL_AUTHORITY_TRUST_ANCHOR_MISSING")
        trusted_path = _inside_regular(str(authority_root), authority_source_root)
        observed_root_sha = _sha(trusted_path)
        refs.append({"path": str(authority_root), "sha256": expected_authority_sha,
                     "observed_sha256": observed_root_sha, "digest_match": observed_root_sha == expected_authority_sha,
                     "evidence_kind": "goal_authority_trust_anchor"})
        if observed_root_sha != expected_authority_sha:
            raise InvalidAttempt("GOAL_AUTHORITY_TRUST_ANCHOR_MISMATCH")
        trusted = _load_json(trusted_path, "GOAL_AUTHORITY_TRUST_ANCHOR_MISMATCH")
        if not _closed(trusted, {"schema_version", "authority_root_id", "goal_binding"}) or trusted["schema_version"] != "stop_gate_goal_authority_root_v1":
            raise InvalidAttempt("GOAL_AUTHORITY_TRUST_ANCHOR_MISMATCH")
        binding = trusted["goal_binding"]
        goal = state["goal"]
        if goal["goal_authority_root_id"] != trusted["authority_root_id"]:
            raise InvalidAttempt("UNTRUSTED_COMPLETION_PREDICATE_ISSUER")
        goal_fields = ["goal_id", "goal_ref", "goal_sha256", "completion_rule_id", "completion_rule_ref", "completion_rule_sha256", "completion_predicate_id", "completion_predicate_ref", "completion_predicate_sha256"]
        if any(binding.get(k) != goal.get(k) for k in goal_fields):
            if any(binding.get(k) != goal.get(k) for k in ("completion_predicate_id", "completion_predicate_ref", "completion_predicate_sha256")):
                raise InvalidAttempt("UNTRUSTED_COMPLETION_PREDICATE_ISSUER")
            raise InvalidAttempt("GOAL_NOT_BOUND_BY_TRUST_ANCHOR")
        issuer = binding.get("predicate_issuer", {})
        if (issuer.get("authority_id"), issuer.get("authority_ref"), issuer.get("authority_sha256")) != (goal["goal_authority_id"], goal["goal_authority_ref"], goal["goal_authority_sha256"]):
            raise InvalidAttempt("UNTRUSTED_COMPLETION_PREDICATE_ISSUER")
        _ref(goal["goal_ref"], goal["goal_sha256"], "goal", allowed_root, refs)
        _ref(goal["completion_rule_ref"], goal["completion_rule_sha256"], "completion_rule", allowed_root, refs)
        _ref(goal["goal_authority_ref"], goal["goal_authority_sha256"], "goal_authority", allowed_root, refs)
        predicate_path = _ref(goal["completion_predicate_ref"], goal["completion_predicate_sha256"], "completion_predicate", allowed_root, refs)
        predicate = _load_json(predicate_path, "COMPLETION_PREDICATE_INVALID")
        pred_required = {"schema_version", "predicate_id", "source_completion_rule_id", "source_completion_rule_ref", "source_completion_rule_sha256", "issued_by_authority_ref", "issued_by_authority_sha256", "issued_by_authority_id", "expression"}
        if not _closed(predicate, pred_required) or predicate["schema_version"] != "stop_gate_completion_predicate_v1" or predicate["predicate_id"] != goal["completion_predicate_id"]:
            raise InvalidAttempt("COMPLETION_PREDICATE_INVALID")
        if (predicate["source_completion_rule_id"], predicate["source_completion_rule_ref"], predicate["source_completion_rule_sha256"]) != (goal["completion_rule_id"], goal["completion_rule_ref"], goal["completion_rule_sha256"]):
            raise InvalidAttempt("COMPLETION_PREDICATE_SOURCE_MISMATCH")
        if (predicate["issued_by_authority_id"], predicate["issued_by_authority_ref"], predicate["issued_by_authority_sha256"]) != (issuer["authority_id"], issuer["authority_ref"], issuer["authority_sha256"]):
            raise InvalidAttempt("UNTRUSTED_COMPLETION_PREDICATE_ISSUER")
        _validate_predicate_shape(predicate["expression"])
        for evidence in state["final_evidence"]:
            if evidence["binding_status"] == "bound":
                if evidence["authority_receipt_id"] is not None:
                    raise InvalidAttempt("STATE_SCHEMA_INVALID")
                _ref(evidence["path"], evidence["sha256"], evidence["evidence_kind"], allowed_root, refs)
            elif evidence["binding_status"] == "not_applicable_with_authority":
                _valid_not_applicable(evidence, state, allowed_root, refs)
        if goal["goal_terminal"] and state["completion"]["remaining_must_have_ids"]:
            raise InvalidAttempt("TERMINAL_WITH_REMAINING_MUST_HAVE")
        if goal["goal_terminal"] and any(x["approval_status"] != "approved" for x in state["scope_deltas"]):
            raise InvalidAttempt("TERMINAL_WITH_UNAPPROVED_SCOPE_DELTA")
        if goal["goal_terminal"] and any(x["binding_status"] not in {"bound", "not_applicable_with_authority"} for x in state["final_evidence"]):
            raise InvalidAttempt("TERMINAL_WITH_UNBOUND_FINAL_EVIDENCE")
        satisfied = _eval(predicate["expression"], state, allowed_root, refs)
        pauses = _pending_admissible(state, allowed_root, refs)
        explicit_pause = next((x for x in state["human_decisions"] if x["authority_type"] == "user_pause" and x["status"] == "resolved_pause"), None)
        if explicit_pause:
            verdict, reasons, action = "PAUSE_ALLOWED", ["USER_PAUSE_ACTIVE"], "WAIT_FOR_USER_RESUME"
        elif any(x["approval_status"] != "approved" for x in state["scope_deltas"]):
            verdict, reasons, action = "PAUSE_ALLOWED", ["UNAPPROVED_SCOPE_DELTA"], "REQUEST_DECISION"
        elif pauses:
            verdict, reasons, action = "PAUSE_ALLOWED", [ADMISSIBLE[pauses[0]["authority_type"]]], "REQUEST_DECISION"
        elif any(x["recoverable"] and x["failure_kind"] in {"network", "tool"} and x["consecutive_count"] >= x["pause_threshold"] for x in state["recoverable_failures"]):
            verdict, reasons, action = "PAUSE_ALLOWED", ["RECOVERY_THRESHOLD_REACHED"], "REQUEST_DECISION"
        elif goal["goal_terminal"] and satisfied:
            verdict, reasons, action = "GOAL_COMPLETE", ["ORIGINAL_COMPLETION_RULE_SATISFIED", "ALL_MUST_HAVES_ACCOUNTED_FOR", "FINAL_EVIDENCE_BOUND", "FINAL_STATE_CONSISTENT"], "EMIT_FINAL_CLOSEOUT"
        else:
            ignored = any(x["status"] == "pending" and x["authority_type"] not in ADMISSIBLE for x in state["human_decisions"])
            approved = any(x["status"] == "pending" and _approved(x, state, allowed_root, refs) for x in state["human_decisions"])
            failures = state["recoverable_failures"]
            missing = {x["evidence_kind"] for x in state["final_evidence"] if x["binding_status"] not in {"bound", "not_applicable_with_authority"}} | (REQUIRED_EVIDENCE - {x["evidence_kind"] for x in state["final_evidence"]})
            if ignored: reasons = ["NON_ADMISSIBLE_DECISION_IGNORED", "NEXT_WORK_READY"]; action = "DISPATCH_NEXT_WORK"
            elif approved: reasons = ["AUTHORITY_ALREADY_GRANTED", "NEXT_WORK_READY"]; action = "DISPATCH_NEXT_WORK"
            elif state["next_work_unit"]["ready"] and not state["next_work_unit"]["entry_materialized"]: reasons = ["PARENT_GOAL_ACTIVE", "NEXT_ENTRY_MISSING"]; action = "MATERIALIZE_NEXT_ENTRY"
            elif any(x["recoverable"] and x["failure_kind"] in {"network", "tool"} for x in failures): reasons = ["PARENT_GOAL_ACTIVE", "RECOVERY_BELOW_THRESHOLD"]; action = "RETRY_RECOVERY"
            elif failures: reasons = ["PARENT_GOAL_ACTIVE", "REPAIRABLE_FAILURE"]; action = "REPAIR"
            elif not goal["goal_terminal"] and state["completion"]["remaining_must_have_ids"] and state["next_work_unit"]["ready"]:
                reasons = ["PARENT_GOAL_ACTIVE", "NEXT_WORK_READY"]; action = "DISPATCH_NEXT_WORK"
            elif missing: reasons = ["FINAL_EVIDENCE_INCOMPLETE", "FINAL_STATE_BINDING_INCOMPLETE"]; action = "COMPLETE_FINAL_EVIDENCE"
            else: reasons = ["PARENT_GOAL_ACTIVE", "NEXT_WORK_READY"]; action = "DISPATCH_NEXT_WORK"
            verdict = "CONTINUE"
        return _receipt(state_path, state_sha, state, "valid", verdict, reasons, action, refs, satisfied), 0
    except InvalidAttempt as exc:
        return _receipt(state_path, state_sha, state, "invalid", None, [exc.reason], "REBUILD_STATE", refs, satisfied), 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a loop_state_v1 against the deterministic Stop Gate")
    parser.add_argument("state", type=Path)
    parser.add_argument("--allowed-root", type=Path, required=True)
    parser.add_argument("--authority-source-root", type=Path)
    parser.add_argument("--authority-root", type=Path)
    parser.add_argument("--expected-authority-root-sha256")
    parser.add_argument("--receipt-out", type=Path)
    args = parser.parse_args()
    receipt, code = evaluate(args.state, args.allowed_root, args.authority_source_root, args.authority_root, args.expected_authority_root_sha256)
    rendered = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.receipt_out:
        args.receipt_out.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

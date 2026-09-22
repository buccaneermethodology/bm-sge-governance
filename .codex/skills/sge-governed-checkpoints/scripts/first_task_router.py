#!/usr/bin/env python3
"""Pure, fail-closed first-task classifier and Goal router."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "first_task_route_v1"
TASK_CLASSES = {"trivial_read_only", "governed_implementation", "governed_validation"}
GOAL_STATES = {"missing", "existing", "conflict"}


def _goal_identity(payload: dict[str, Any], *, allow_frozen_legacy: bool) -> str | None:
    refs = payload.get("goal_refs")
    if refs is None and allow_frozen_legacy:
        return "legacy_frozen_case_assertion"
    if not isinstance(refs, list) or len(refs) != 1:
        return None
    ref = refs[0]
    if not isinstance(ref, dict) or set(ref) != {"goal_id", "path"}:
        return None
    goal_id, path = ref.get("goal_id"), ref.get("path")
    if not isinstance(goal_id, str) or not goal_id.strip() or not isinstance(path, str) or not path.strip():
        return None
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    return f"{goal_id}@{path}"


def _evaluate(payload: dict[str, Any], *, allow_frozen_legacy: bool = False) -> dict[str, Any]:
    task_class = payload.get("task_class")
    goal_presence = payload.get("goal_presence")
    if task_class not in TASK_CLASSES:
        raise ValueError("FIRST_TASK_CLASS_INVALID")
    if goal_presence not in GOAL_STATES:
        raise ValueError("GOAL_PRESENCE_INVALID")
    if task_class == "trivial_read_only":
        return {
            "schema_version": SCHEMA_VERSION,
            "task_class": task_class,
            "goal_presence": goal_presence,
            "route": "answer",
            "builder_allowed": False,
            "required_gates": ["intake"],
            "required_lanes": [],
            "semantic_posture": "not_triggered_by_route",
            "maximum_claim": "read_only_answer",
            "reason_code": "TRIVIAL_READ_ONLY",
            "reason": "trivial read-only task may be answered without creating a Goal",
        }
    if goal_presence == "missing":
        return {
            "schema_version": SCHEMA_VERSION,
            "task_class": task_class,
            "goal_presence": goal_presence,
            "route": "goal_required",
            "builder_allowed": False,
            "required_gates": ["intake", "context_bootstrap", "goal_conformance", "multi_agent", "erbe", "sgc"],
            "required_lanes": ["design", "builder", "validation", "closure"],
            "semantic_posture": "trigger_scan_required",
            "maximum_claim": "goal_design_only",
            "reason_code": "GOAL_REQUIRED",
            "reason": "governed implementation without Goal must freeze Goal before Builder",
        }
    if goal_presence == "conflict":
        return {
            "schema_version": SCHEMA_VERSION,
            "task_class": task_class,
            "goal_presence": goal_presence,
            "route": "human_decision",
            "builder_allowed": False,
            "required_gates": ["intake", "context_bootstrap", "goal_conformance"],
            "required_lanes": [],
            "semantic_posture": "blocked_authority_conflict",
            "maximum_claim": "blocked",
            "reason_code": "GOAL_AUTHORITY_CONFLICT",
            "reason": "conflicting active Goal authority requires human resolution",
        }
    goal_identity = _goal_identity(payload, allow_frozen_legacy=allow_frozen_legacy)
    if not goal_identity:
        return {
            "schema_version": SCHEMA_VERSION,
            "task_class": task_class,
            "goal_presence": "conflict",
            "goal_identity": None,
            "route": "human_decision",
            "builder_allowed": False,
            "required_gates": ["intake", "context_bootstrap", "goal_conformance"],
            "required_lanes": [],
            "semantic_posture": "blocked_authority_conflict",
            "maximum_claim": "blocked",
            "reason_code": "GOAL_IDENTITY_NOT_UNIQUE_OR_LOCATABLE",
            "reason": "existing Goal requires exactly one repo-relative locator and Goal identity",
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "task_class": task_class,
        "goal_presence": goal_presence,
        "goal_identity": goal_identity,
        "route": "resume_goal",
        "builder_allowed": False,
        "required_gates": ["context_bootstrap", "goal_conformance", "sgc"],
        "required_lanes": ["design", "builder", "validation", "closure"],
        "semantic_posture": "follow_goal_contract",
        "maximum_claim": "bounded_by_existing_goal",
        "reason_code": "EXISTING_GOAL_CONTROLS",
        "reason": "existing Goal controls continuation and Builder readiness",
    }


def route_task(payload: dict[str, Any]) -> dict[str, Any]:
    """Public strict entry: existing Goal authority requires one locatable identity."""
    return _evaluate(payload, allow_frozen_legacy=False)


def evaluate_case(payload: dict[str, Any]) -> dict[str, Any]:
    """Frozen ERBE adapter; new callers must use route_task/CLI classify."""
    return _evaluate(payload, allow_frozen_legacy=True)


def validate_result(result: dict[str, Any]) -> tuple[bool, str]:
    required = {"schema_version", "task_class", "goal_presence", "route", "builder_allowed", "required_gates", "required_lanes", "semantic_posture", "maximum_claim", "reason_code", "reason"}
    allowed = required | {"goal_identity"}
    if not required.issubset(result) or set(result) - allowed:
        return False, "FIRST_TASK_ROUTE_SHAPE_INVALID"
    if result["schema_version"] != SCHEMA_VERSION or not result["reason"] or not result["maximum_claim"]:
        return False, "FIRST_TASK_ROUTE_VALUE_INVALID"
    return True, "ok"


def _load(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8")) if path != "-" else json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("classify", "validate"):
        cmd = sub.add_parser(name)
        cmd.add_argument("input")
    args = parser.parse_args()
    try:
        payload = _load(args.input)
        result = route_task(payload) if args.command == "classify" else payload
        ok, code = validate_result(result)
        print(json.dumps(result if ok else {"verdict": "fail", "fingerprint": code}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if ok else 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"verdict": "fail", "fingerprint": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

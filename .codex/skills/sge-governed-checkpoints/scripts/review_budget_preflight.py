#!/usr/bin/env python3
"""Bounded local preflight for cumulative review attempts; not a host dispatch gate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCHEMA_VERSION = "sge_review_budget_preflight_v1"
MAX_ATTEMPTS = 3
REVIEW_TYPES = {"semantic", "validation"}
REQUIRED_EVENT_KEYS = {"attempt_id", "artifact_id", "lineage_id", "review_type", "status"}
COUNTED_STATUSES = {"started", "completed", "failed", "interrupted"}


def evaluate_budget(value: object) -> dict:
    """Count all started attempts for one declared artifact lineage.

    The supplied history is caller-controlled. This function detects local
    over-budget records but cannot establish completeness or prevent dispatch.
    """
    error = None
    if not isinstance(value, dict) or set(value) != {"schema_version", "artifact_id", "lineage_id", "events"}:
        error = "request_shape_invalid"
    elif value.get("schema_version") != SCHEMA_VERSION:
        error = "schema_version_invalid"
    elif not isinstance(value.get("artifact_id"), str) or not value["artifact_id"]:
        error = "artifact_id_invalid"
    elif not isinstance(value.get("lineage_id"), str) or not value["lineage_id"]:
        error = "lineage_id_invalid"
    elif not isinstance(value.get("events"), list):
        error = "events_invalid"

    if error:
        return _result("invalid_input", None, None, 0, None, error)

    artifact_id = value["artifact_id"]
    lineage_id = value["lineage_id"]
    events = value["events"]
    attempt_ids: set[str] = set()
    counted = 0
    for index, event in enumerate(events):
        if not isinstance(event, dict) or not REQUIRED_EVENT_KEYS.issubset(event):
            return _result("invalid_input", artifact_id, lineage_id, counted, None, f"event_{index}_shape_invalid")
        attempt_id = event["attempt_id"]
        if not isinstance(attempt_id, str) or not attempt_id or attempt_id in attempt_ids:
            return _result("invalid_input", artifact_id, lineage_id, counted, None, f"event_{index}_attempt_id_invalid_or_duplicate")
        attempt_ids.add(attempt_id)
        if (not isinstance(event["artifact_id"], str) or not event["artifact_id"]
                or not isinstance(event["lineage_id"], str) or not event["lineage_id"]):
            return _result("invalid_input", artifact_id, lineage_id, counted, None, f"event_{index}_identity_invalid")
        if event["artifact_id"] == artifact_id and event["lineage_id"] != lineage_id:
            return _result("invalid_input", artifact_id, lineage_id, counted, None,
                           f"event_{index}_artifact_lineage_mismatch")
        if event["review_type"] not in REVIEW_TYPES:
            return _result("invalid_input", artifact_id, lineage_id, counted, None, f"event_{index}_review_type_invalid")
        if event["status"] not in COUNTED_STATUSES:
            return _result("invalid_input", artifact_id, lineage_id, counted, None, f"event_{index}_status_invalid")
        if event["lineage_id"] == lineage_id:
            counted += 1

    allowed = counted < MAX_ATTEMPTS
    return _result(
        "allowed_by_supplied_history" if allowed else "blocked_by_supplied_history",
        artifact_id,
        lineage_id,
        counted,
        counted + 1 if allowed else None,
        "attempt_budget_available" if allowed else "artifact_attempt_budget_exhausted",
    )


def _result(status: str, artifact_id: str | None, lineage_id: str | None, counted: int, next_attempt: int | None, reason: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "artifact_id": artifact_id,
        "lineage_id": lineage_id,
        "max_cumulative_attempts": MAX_ATTEMPTS,
        "counted_attempts": counted,
        "next_attempt": next_attempt,
        "reason": reason,
        "enforcement": "caller_supplied_history_only; no immutable host ledger or dispatch interception",
        "admission_granted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON request containing artifact_id, lineage_id, and cumulative events")
    parser.add_argument("--output", required=True, type=Path, help="New JSON report path; existing files are not overwritten")
    args = parser.parse_args()
    if args.output.exists():
        print("output_exists", file=sys.stderr)
        return 2
    try:
        request = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"input_error:{type(exc).__name__}", file=sys.stderr)
        return 2
    report = evaluate_budget(request)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

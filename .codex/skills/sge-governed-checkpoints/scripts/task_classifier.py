#!/usr/bin/env python3
"""Fact-based SGE task classifier v2 with a bounded legacy adapter."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "sge_task_classification_v2"
HARD_TRIGGERS = (
    "tracked_work",
    "multi_repository_change",
    "runtime_or_schema_change",
    "acceptance_gate_change",
    "persistent_state_change",
    "external_release",
    "independent_validation_required",
    "delegated_topology_required",
)
FACT_KEYS = (*HARD_TRIGGERS, "read_only")


def adapt_legacy(payload: dict[str, Any]) -> dict[str, Any]:
    """Copy only explicit legacy facts; labels never manufacture facts."""
    facts = payload.get("facts", {})
    if not isinstance(facts, dict):
        raise ValueError("LEGACY_FACTS_INVALID")
    return {key: facts[key] for key in FACT_KEYS if key in facts}


def classify(task_facts: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(task_facts, dict):
        raise ValueError("TASK_FACTS_INVALID")
    unknown = sorted(key for key in FACT_KEYS if task_facts.get(key) not in {True, False})
    if unknown:
        return {
            "schema_version": SCHEMA_VERSION,
            "classification": "unknown",
            "route": "blocked_pending_facts",
            "reason_code": "TASK_FACTS_INCOMPLETE_OR_CONFLICTING",
            "hard_triggers": [],
            "unknown_facts": unknown,
            "maximum_claim": "classification diagnostic only",
        }
    triggered = [key for key in HARD_TRIGGERS if task_facts[key] is True]
    if triggered:
        classification, route, reason = "governed_implementation", "governed_workflow", "HARD_TRIGGER_PRECEDENCE"
    elif task_facts["read_only"]:
        classification, route, reason = "read_only", "read_only_workflow", "COMPLETE_READ_ONLY_FACTS"
    else:
        classification, route, reason = "trivial", "proportional_direct", "COMPLETE_NO_HARD_TRIGGER_FACTS"
    return {
        "schema_version": SCHEMA_VERSION,
        "classification": classification,
        "route": route,
        "reason_code": reason,
        "hard_triggers": triggered,
        "unknown_facts": [],
        "maximum_claim": "routing decision only",
    }


def classify_input(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("input_version", "v2")
    if source == "v2":
        facts = payload.get("task_facts", {})
    elif source == "legacy":
        facts = adapt_legacy(payload)
    else:
        raise ValueError("TASK_INPUT_VERSION_UNSUPPORTED")
    return classify(facts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin) if args.input == "-" else json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = classify_input(payload)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 1 if result["classification"] == "unknown" else 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"verdict": "fail", "fingerprint": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

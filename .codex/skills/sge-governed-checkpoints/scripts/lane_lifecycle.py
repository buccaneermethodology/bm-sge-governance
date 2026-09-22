#!/usr/bin/env python3
"""Pure lane lifecycle, fallback, readiness and validation-binding evaluator."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "lane_lifecycle_v1"
STATES = {"registered", "ready", "running", "completed", "evidence_bound", "failed"}
FAILURES = {"capability_unavailable", "no_output", "card_drift", "execution_failure", "retry_exhausted"}
CLOSEOUT_PHASES = {"draft", "validation", "repair", "final", "post_closeout_reconciliation"}
CLOSEOUT_TRANSITIONS = {
    ("draft", "submit_validation"): "validation",
    ("validation", "request_repair"): "repair",
    ("repair", "resubmit_validation"): "validation",
    ("validation", "finalize"): "final",
    ("final", "reconcile"): "post_closeout_reconciliation",
}


def evaluate_case(payload: dict[str, Any]) -> dict[str, Any]:
    if "closeout_phase" in payload:
        final = payload.get("closeout_phase") == "post_closeout_reconciliation" and payload.get("validation_binding_state") == "final_state_bound"
        return {"schema_version": SCHEMA_VERSION, "goal_done_allowed": final}
    prior, event = payload.get("lane_state"), payload.get("event")
    if prior not in STATES or event not in FAILURES:
        raise ValueError("LANE_TRANSITION_INVALID")
    if event == "retry_exhausted":
        fallback = "orchestrator_takeover_pending_approval" if payload.get("builder_required_independent") else "human_blocked"
        return {"schema_version": SCHEMA_VERSION, "lane_state": "failed", "fallback_state": fallback, "human_trigger": True, "actual_topology_preserved": True, "claim_impact": "independent Builder requirement remains unmet" if payload.get("builder_required_independent") else "lane remains failed"}
    if event == "no_output":
        attempt = payload.get("attempt")
        if not isinstance(attempt, int) or attempt < 1:
            raise ValueError("LANE_ATTEMPT_INVALID")
        return {"schema_version": SCHEMA_VERSION, "lane_state": "failed", "fallback_state": "retry", "actual_topology_preserved": True, "human_trigger": False, "claim_impact": "no completion evidence"}
    fallback = {"card_drift":"reissue_narrower_card", "capability_unavailable":"reassign", "execution_failure":"retry"}[event]
    return {"schema_version": SCHEMA_VERSION, "lane_state":"failed", "fallback_state":fallback, "actual_topology_preserved":True, "human_trigger":False, "claim_impact":"lane completion not established"}


def apply_transition(payload: dict[str, Any]) -> dict[str, Any]:
    prior, event = payload.get("lane_state"), payload.get("event")
    if event in FAILURES:
        policy_id = payload.get("retry_policy_id")
        attempt, maximum = payload.get("attempt"), payload.get("max_attempts")
        if not isinstance(policy_id, str) or not policy_id.strip():
            raise ValueError("LANE_RETRY_POLICY_MISSING")
        if not isinstance(attempt, int) or attempt < 1 or not isinstance(maximum, int) or maximum < 1:
            raise ValueError("LANE_ATTEMPT_POLICY_INVALID")
        if not payload.get("previous_event_ref"):
            raise ValueError("LANE_PREVIOUS_EVENT_REF_MISSING")
        normalized = dict(payload)
        if event in {"no_output", "execution_failure"} and attempt >= maximum:
            normalized["event"] = "retry_exhausted"
        if event == "card_drift" and payload.get("scope_removed") and not payload.get("scope_delta_approval_ref"):
            normalized["event"] = "retry_exhausted"
        result = evaluate_case(normalized)
    else:
        legal = {("registered","mark_ready"):"ready", ("ready","start"):"running", ("running","complete"):"completed", ("completed","bind_evidence"):"evidence_bound"}
        next_state = legal.get((prior, event))
        if next_state is None:
            raise ValueError("LANE_TRANSITION_INVALID")
        if event == "complete" and not payload.get("output_identity"):
            raise ValueError("LANE_OUTPUT_IDENTITY_MISSING")
        if event == "bind_evidence" and not payload.get("durable_binding_valid"):
            raise ValueError("LANE_DURABLE_BINDING_INVALID")
        result = {"schema_version":SCHEMA_VERSION,"lane_state":next_state,"fallback_state":None,"human_trigger":False,"actual_topology_preserved":True,"claim_impact":"bounded by evidence-bound state"}
    prior_history = payload.get("actual_builder_topology", [])
    if not isinstance(prior_history, list):
        raise ValueError("TOPOLOGY_HISTORY_INVALID")
    event_record = {"from":prior,"event":event,"to":result["lane_state"],"attempt":payload.get("attempt")}
    if event in FAILURES:
        event_record.update({"max_attempts":payload.get("max_attempts"),"retry_policy_id":payload.get("retry_policy_id"),"previous_event_ref":payload.get("previous_event_ref"),"approval_ref":payload.get("takeover_approval_ref") or payload.get("scope_delta_approval_ref")})
    result["actual_builder_topology"] = [*prior_history, event_record]
    return result


def advance_closeout(payload: dict[str, Any]) -> dict[str, Any]:
    prior, event = payload.get("closeout_phase"), payload.get("event")
    if prior not in CLOSEOUT_PHASES:
        raise ValueError("CLOSEOUT_PHASE_INVALID")
    next_phase = CLOSEOUT_TRANSITIONS.get((prior, event))
    if next_phase is None:
        raise ValueError("CLOSEOUT_TRANSITION_INVALID")
    if event == "finalize" and payload.get("validation_verdict") != "pass":
        raise ValueError("CLOSEOUT_FINAL_REQUIRES_PASSING_VALIDATION")
    if event == "reconcile" and not payload.get("final_state_inventory"):
        raise ValueError("CLOSEOUT_FINAL_INVENTORY_MISSING")
    return {"schema_version":SCHEMA_VERSION,"from_phase":prior,"event":event,"closeout_phase":next_phase,"binding_invalidated":event in {"request_repair","resubmit_validation","finalize"}}


def check_readiness(payload: dict[str, Any]) -> dict[str, Any]:
    phase = payload.get("target_phase")
    states = payload.get("lane_states", {})
    requirements = {"builder":{"design":"evidence_bound"}, "validation":{"builder":"evidence_bound","validation_handoff":"evidence_bound"}, "closure":{"validation":"evidence_bound","blocking_findings":"zero"}}
    if phase not in requirements:
        raise ValueError("READINESS_PHASE_INVALID")
    unmet = [f"{key}={value}" for key, value in requirements[phase].items() if states.get(key) != value]
    return {"schema_version":SCHEMA_VERSION,"target_phase":phase,"ready":not unmet,"unmet":unmet}


def bind_validation(payload: dict[str, Any]) -> dict[str, Any]:
    reviewers = payload.get("reviewers", [])
    current = payload.get("current_final_state_digest")
    bound = payload.get("reviewed_final_state_digest")
    current_inventory = payload.get("current_final_state_inventory", {})
    reviewed_inventory = payload.get("reviewed_final_state_inventory", {})
    required_surfaces = {"closeout", "dashboard_registry", "kb_dashboard", "final_diff"}
    inventory_valid = (
        isinstance(current_inventory, dict)
        and isinstance(reviewed_inventory, dict)
        and set(current_inventory) == required_surfaces
        and current_inventory == reviewed_inventory
        and all(isinstance(value, str) and len(value) == 64 for value in current_inventory.values())
    )
    valid = len(reviewers) == 1 and bool(current) and current == bound and inventory_valid and payload.get("closeout_phase") == "post_closeout_reconciliation"
    return {"schema_version":SCHEMA_VERSION,"validation_binding_state":"final_state_bound" if valid else "pre_closeout_only","goal_done_allowed":valid,"reason_code":"FINAL_STATE_BOUND" if valid else "FINAL_STATE_BINDING_INCOMPLETE"}


def main() -> int:
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command",required=True)
    for name in ("transition","check-readiness","advance-closeout","bind-validation"):
        cmd=sub.add_parser(name); cmd.add_argument("input")
    args=parser.parse_args()
    try:
        data=json.load(sys.stdin) if args.input=="-" else json.loads(Path(args.input).read_text(encoding="utf-8"))
        fn={"transition":apply_transition,"check-readiness":check_readiness,"advance-closeout":advance_closeout,"bind-validation":bind_validation}[args.command]
        result=fn(data); print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if result.get("ready",result.get("goal_done_allowed",True)) else 1
    except (OSError,json.JSONDecodeError,ValueError) as exc:
        print(json.dumps({"verdict":"fail","fingerprint":str(exc)},ensure_ascii=False)); return 1


if __name__=="__main__": raise SystemExit(main())

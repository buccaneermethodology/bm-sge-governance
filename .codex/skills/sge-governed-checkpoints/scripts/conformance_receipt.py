#!/usr/bin/env python3
"""Candidate receipt assembler and fail-closed durable-reference validator."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION="conformance_receipt_v1"
MANDATORY=("task_context","classifier_preflight","lane_topology","scope_mapping","gate_runs","independent_validation","closeout","registry","kb_dashboard_routing","claim_ceiling")
STATUS_BY_CATEGORY={
    "task_context":{"valid"},
    "classifier_preflight":{"pass"},
    "lane_topology":{"preserved"},
    "scope_mapping":{"preserved"},
    "gate_runs":{"pass"},
    "independent_validation":{"final_state_bound"},
    "closeout":{"pass"},
    "registry":{"pass"},
    "kb_dashboard_routing":{"preserved","not_applicable"},
    "claim_ceiling":{"preserved"},
}


def evaluate_case(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("single_repo_fixtures_pass") is True:
        return {"schema_version":SCHEMA_VERSION,"cross_agent_validated":False}
    receipt=payload.get("receipt",{})
    evidence=receipt.get("mandatory_evidence",[])
    return {"schema_version":SCHEMA_VERSION,"receipt_verdict":"fail" if not evidence else "candidate"}


def assemble(payload: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version":SCHEMA_VERSION,"receipt_id":payload.get("receipt_id","candidate"),"evidence":payload.get("evidence",[]),"evidence_gaps":payload.get("evidence_gaps",[]),"producer_claim":payload.get("producer_claim"),"cross_agent_validated":False,"receipt_verdict":"candidate","claim_ceiling":payload.get("claim_ceiling","single-repository evidence only")}


def _sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(payload: dict[str, Any], repo: Path) -> dict[str, Any]:
    if payload.get("schema_version") != SCHEMA_VERSION:
        return {"schema_version":SCHEMA_VERSION,"receipt_verdict":"fail","fingerprint":"RECEIPT_SCHEMA_INVALID","missing_categories":list(MANDATORY)}
    refs=payload.get("evidence",[])
    by_category={}
    failures=[]
    for ref in refs:
        cat=ref.get("category")
        if cat not in MANDATORY:
            failures.append(f"unknown_category:{cat}")
            continue
        if cat in by_category: failures.append(f"duplicate:{cat}")
        by_category[cat]=ref
        raw=ref.get("path","")
        path=repo/raw
        if not raw or Path(raw).is_absolute() or ".." in Path(raw).parts or not path.is_file(): failures.append(f"missing_ref:{cat}")
        elif ref.get("sha256") != _sha(path): failures.append(f"digest_drift:{cat}")
        elif ref.get("observed_status") not in STATUS_BY_CATEGORY[cat]: failures.append(f"invalid_status:{cat}")
    missing=[cat for cat in MANDATORY if cat not in by_category]
    if payload.get("evidence_gaps"): failures.append("evidence_gaps_present")
    validation=by_category.get("independent_validation",{})
    closeout=by_category.get("closeout",{})
    if validation.get("observed_status") != "final_state_bound": failures.append("validation_not_final_state_bound")
    if closeout.get("phase") != "post_closeout_reconciliation": failures.append("closeout_not_reconciled")
    scope = by_category.get("scope_mapping", {})
    if not isinstance(scope.get("covered_requirement_ids"), list) or not scope.get("covered_requirement_ids"):
        failures.append("scope_mapping_incomplete")
    claim = by_category.get("claim_ceiling", {})
    if claim.get("claim_ceiling") != payload.get("claim_ceiling") or not payload.get("claim_ceiling"):
        failures.append("claim_ceiling_not_bound")
    if validation.get("final_state_digest") != closeout.get("final_state_digest") or not validation.get("final_state_digest"):
        failures.append("final_binding_identity_mismatch")
    return {"schema_version":SCHEMA_VERSION,"receipt_verdict":"pass" if not missing and not failures else "fail","missing_categories":missing,"failures":failures,"cross_agent_validated":False,"claim_ceiling":payload.get("claim_ceiling","single-repository evidence only")}


def main() -> int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    for name in ("assemble","validate"):
        cmd=sub.add_parser(name); cmd.add_argument("input"); cmd.add_argument("--repo",default=".")
    a=p.parse_args()
    try:
        data=json.load(sys.stdin) if a.input=="-" else json.loads(Path(a.input).read_text(encoding="utf-8"))
        result=assemble(data) if a.command=="assemble" else validate(data,Path(a.repo).resolve())
        print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if result.get("receipt_verdict") in {"candidate","pass"} else 1
    except (OSError,json.JSONDecodeError,ValueError) as exc:
        print(json.dumps({"receipt_verdict":"fail","fingerprint":str(exc)},ensure_ascii=False)); return 1


if __name__=="__main__": raise SystemExit(main())

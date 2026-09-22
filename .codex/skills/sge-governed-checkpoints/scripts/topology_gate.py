#!/usr/bin/env python3
"""Plan required lanes and recompute actual topology from durable evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "sge_topology_gate_v1"
CHECKPOINTS = ("pre_builder", "pre_validation", "pre_closeout", "final")
BASE_LANES = ("design", "builder", "validation", "closure")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_ref(root: Path, ref: Any, code: str) -> Path:
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        raise ValueError(f"{code}_REF_INVALID")
    relative, digest = ref["path"], ref["sha256"]
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"{code}_LOCATOR_INVALID")
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{code}_LOCATOR_INVALID") from exc
    if not path.is_file() or not isinstance(digest, str) or len(digest) != 64 or _sha(path) != digest:
        raise ValueError(f"{code}_DIGEST_MISMATCH")
    return path


def _load_json_ref(root: Path, ref: Any, code: str) -> tuple[dict[str, Any], str]:
    path = _resolve_ref(root, ref, code)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{code}_JSON_INVALID") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{code}_JSON_INVALID")
    return payload, _sha(path)


def plan(classification: str, impacts: dict[str, Any] | None = None) -> dict[str, Any]:
    impacts = impacts or {}
    if classification == "governed_implementation":
        lanes = list(BASE_LANES)
        if impacts.get("semantic_risk") in {"high", "critical"}:
            lanes.append("semantic")
        if impacts.get("external_release") is True:
            lanes.append("release")
    elif classification == "read_only":
        lanes = ["validation"] if impacts.get("delta_only_reconciliation") else []
    elif classification == "trivial":
        lanes = []
    else:
        raise ValueError("CLASSIFICATION_NOT_ROUTABLE")
    return {"schema_version": SCHEMA_VERSION, "required_lanes": lanes, "required_checkpoints": list(CHECKPOINTS), "plan_is_execution_evidence": False}


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    checkpoint = payload.get("checkpoint")
    if checkpoint not in CHECKPOINTS:
        raise ValueError("TOPOLOGY_CHECKPOINT_INVALID")
    required = payload.get("required_lanes")
    evidence = payload.get("lane_evidence_refs")
    snapshot_id = payload.get("snapshot_id")
    root = Path(payload.get("repo_root", ".")).resolve()
    if not isinstance(snapshot_id, str) or not snapshot_id or not isinstance(required, list) or not isinstance(evidence, dict):
        raise ValueError("TOPOLOGY_INPUT_INVALID")
    failures: list[str] = []
    identities: dict[str, str] = {}
    evidence_digests: dict[str, str] = {}
    for lane in required:
        try:
            row, evidence_digest = _load_json_ref(root, evidence.get(lane), "LANE_EVIDENCE")
        except ValueError as exc:
            failures.append(f"{exc}:{lane}")
            continue
        evidence_digests[lane] = evidence_digest
        if row.get("schema_version") != "sge_lane_evidence_v1" or row.get("lane") != lane or row.get("checkpoint") != checkpoint or row.get("snapshot_id") != snapshot_id:
            failures.append(f"LANE_EVIDENCE_BINDING_INVALID:{lane}")
            continue
        identity = row.get("execution_identity")
        if not isinstance(identity, str) or not identity.strip():
            failures.append(f"LANE_IDENTITY_MISSING:{lane}")
        else:
            identities[lane] = identity
        try:
            capability, _ = _load_json_ref(root, row.get("capability_receipt_ref"), "CAPABILITY_RECEIPT")
            lifecycle, _ = _load_json_ref(root, row.get("lifecycle_event_ref"), "LIFECYCLE_EVENT")
            _resolve_ref(root, row.get("durable_output_ref"), "DURABLE_OUTPUT")
        except ValueError as exc:
            failures.append(f"{exc}:{lane}")
            continue
        if capability.get("schema_version") != "sge_capability_receipt_v1" or capability.get("lane") != lane or capability.get("execution_identity") != identity or capability.get("state") != "supported":
            failures.append(f"LANE_CAPABILITY_RECEIPT_INVALID:{lane}")
        if lifecycle.get("schema_version") != "sge_lane_lifecycle_event_v1" or lifecycle.get("lane") != lane or lifecycle.get("execution_identity") != identity or lifecycle.get("checkpoint") != checkpoint or lifecycle.get("state") not in {"running", "output_candidate", "validated"}:
            failures.append(f"LANE_LIFECYCLE_EVENT_INVALID:{lane}")
    if "builder" in identities and "validation" in identities and identities["builder"] == identities["validation"]:
        failures.append("REQUIRED_IDENTITY_INDEPENDENCE_ABSENT")
    return {
        "schema_version": SCHEMA_VERSION,
        "checkpoint": checkpoint,
        "topology_state": "conformant" if not failures else "nonconformant",
        "reason_codes": failures or ["ACTUAL_TOPOLOGY_RECOMPUTED"],
        "required_lanes": required,
        "observed_identities": identities,
        "evidence_digests": evidence_digests,
        "recomputed_from_durable_evidence": not failures,
        "maximum_claim": "topology evidence at one checkpoint only",
    }


def evaluate_series(payload: dict[str, Any]) -> dict[str, Any]:
    snapshots = payload.get("snapshots")
    if not isinstance(snapshots, list):
        raise ValueError("TOPOLOGY_SNAPSHOTS_INVALID")
    results = [evaluate(item) for item in snapshots]
    observed = [item["checkpoint"] for item in results]
    snapshot_ids = [item.get("snapshot_id") for item in snapshots]
    complete = observed == list(CHECKPOINTS) and len(set(snapshot_ids)) == len(CHECKPOINTS) and all(item["topology_state"] == "conformant" for item in results)
    return {"schema_version": SCHEMA_VERSION, "topology_state": "conformant" if complete else "nonconformant", "recomputed_checkpoints": observed, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "evaluate", "evaluate-series"):
        cmd = sub.add_parser(name); cmd.add_argument("input")
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin) if args.input == "-" else json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = plan(payload.get("classification"), payload.get("impacts")) if args.command == "plan" else (evaluate(payload) if args.command == "evaluate" else evaluate_series(payload))
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result.get("topology_state", "conformant") == "conformant" else 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"verdict": "fail", "fingerprint": str(exc)}, ensure_ascii=False)); return 1


if __name__ == "__main__":
    raise SystemExit(main())

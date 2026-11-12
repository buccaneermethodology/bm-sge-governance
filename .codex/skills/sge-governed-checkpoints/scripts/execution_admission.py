#!/usr/bin/env python3
"""Validate the pre-execution admission consumed by mutating entry points."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime
from pathlib import Path
from typing import Any

REQUIRED_REFS = ("goal", "completion_contract", "context", "design_review", "topology")
SCHEMA_VERSION = "execution_admission_v1"

def _sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def _path(root: Path, raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts: raise ValueError("ADMISSION_PATH_INVALID")
    resolved = (root / candidate).resolve(strict=True); resolved.relative_to(root.resolve(strict=True))
    if not resolved.is_file(): raise ValueError("ADMISSION_REFERENCE_UNREADABLE")
    return resolved
def _ref(root: Path, value: Any, name: str) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}: raise ValueError(f"ADMISSION_{name.upper()}_REF_INVALID")
    path = _path(root, value["path"])
    if _sha(path) != value["sha256"]: raise ValueError(f"ADMISSION_{name.upper()}_DIGEST_MISMATCH")
    return {"path": value["path"], "sha256": value["sha256"]}
def validate(payload: dict[str, Any], root: Path, *, expected_action: str | None = None, expected_target: str | None = None) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION: raise ValueError("ADMISSION_SCHEMA_INVALID")
    if payload.get("status") != "approved" or not isinstance(payload.get("admission_id"), str): raise ValueError("ADMISSION_NOT_APPROVED")
    if expected_action is not None and payload.get("action") != expected_action: raise ValueError("ADMISSION_ACTION_MISMATCH")
    if expected_target is not None and payload.get("target") != expected_target: raise ValueError("ADMISSION_TARGET_MISMATCH")
    try: datetime.fromisoformat(str(payload["issued_at"]).replace("Z", "+00:00"))
    except (KeyError, ValueError): raise ValueError("ADMISSION_TIMESTAMP_INVALID")
    refs = {name: _ref(root, payload.get(name), name) for name in REQUIRED_REFS}
    return {"schema_version": SCHEMA_VERSION, "admission_id": payload["admission_id"], "action": payload["action"], "target": payload["target"], "references": refs}
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("admission", type=Path); parser.add_argument("--root", type=Path, required=True); parser.add_argument("--action"); parser.add_argument("--target"); args = parser.parse_args()
    try:
        payload = json.loads(args.admission.read_text(encoding="utf-8")); print(json.dumps(validate(payload, args.root.resolve(), expected_action=args.action, expected_target=args.target), ensure_ascii=False, indent=2)); return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"verdict": "blocked", "fingerprint": str(exc)}, ensure_ascii=False)); return 1
if __name__ == "__main__": raise SystemExit(main())

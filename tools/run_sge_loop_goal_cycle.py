#!/usr/bin/env python3
"""Thin profile-validated delegation wrapper for the single Skill Stop Gate core."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/".codex/skills/sge-governed-checkpoints/scripts/stop_gate.py"

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("state", type=Path); p.add_argument("--profile", type=Path, required=True)
    p.add_argument("--allowed-root",type=Path,required=True); p.add_argument("--authority-source-root",type=Path,required=True)
    p.add_argument("--authority-root",type=Path,required=True); p.add_argument("--expected-authority-root-sha256",required=True)
    p.add_argument("--receipt-out",type=Path); a=p.parse_args()
    profile=json.loads(a.profile.read_text(encoding="utf-8"))
    if profile.get("schema_version")!="sge_orchestrator_profile_v1" or profile.get("project_binding") is not None: raise SystemExit("profile_contract_invalid")
    if profile.get("stop_gate",{}).get("delegate")!="skill_core": raise SystemExit("profile_stop_gate_delegate_invalid")
    cmd=[sys.executable,str(CORE),str(a.state),"--allowed-root",str(a.allowed_root),"--authority-source-root",str(a.authority_source_root),"--authority-root",str(a.authority_root),"--expected-authority-root-sha256",a.expected_authority_root_sha256]
    if a.receipt_out: cmd.extend(["--receipt-out",str(a.receipt_out)])
    result=subprocess.run(cmd,cwd=ROOT,capture_output=True)
    sys.stdout.buffer.write(result.stdout); sys.stderr.buffer.write(result.stderr)
    return result.returncode
if __name__ == "__main__": raise SystemExit(main())

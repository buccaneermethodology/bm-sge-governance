#!/usr/bin/env python3
"""Read-only capability and dependency preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "capability_preflight_v1"
IDENTITY_SOURCES = {"source_checkout", "installed_core", "optional_extension", "execution_capability"}


def evaluate_case(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("optional_skill"):
        installed = payload.get("installed")
        if not isinstance(installed, bool):
            raise ValueError("CAPABILITY_STATE_UNKNOWN")
        return {
            "schema_version": SCHEMA_VERSION,
            "classification": "optional_available" if installed else "optional_unavailable",
            "core_capability": False,
            "fallback": "extension" if installed else "core_recipe",
            "claim_impact": "local optional capability only" if installed else "optional integration not exercised",
            "reason_code": "OPTIONAL_AVAILABLE" if installed else "OPTIONAL_UNAVAILABLE_CORE_FALLBACK",
        }
    return inspect_request(payload)


def _digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def inspect_request(payload: dict[str, Any]) -> dict[str, Any]:
    root = Path(payload.get("repo_root", ".")).resolve()
    requirements = payload.get("requirements", [])
    if not isinstance(requirements, list) or not requirements:
        raise ValueError("PREFLIGHT_REQUIREMENTS_MISSING")
    identity_source = payload.get("identity_source", "source_checkout")
    if identity_source not in IDENTITY_SOURCES:
        raise ValueError("PREFLIGHT_IDENTITY_SOURCE_INVALID")
    seen: dict[str, str] = {}
    results = []
    blocked = False
    for row in requirements:
        name = row.get("name")
        requirement = row.get("requirement")
        probe = row.get("probe", {})
        if not name or requirement not in {"required", "optional"}:
            raise ValueError("PREFLIGHT_REQUIREMENT_INVALID")
        marker = json.dumps(row, sort_keys=True)
        if name in seen and seen[name] != marker:
            raise ValueError("PREFLIGHT_CAPABILITY_CONFLICT")
        seen[name] = marker
        state, identity, method = "unknown", {}, probe.get("type", "declared")
        if probe.get("type") == "path":
            candidate = root / str(probe.get("path", ""))
            state = "available" if candidate.exists() else "unavailable"
            identity = {"path": str(probe.get("path", "")), "sha256": _digest(candidate)}
        elif probe.get("type") == "command":
            found = shutil.which(str(probe.get("command", "")))
            state = "available" if found else "unavailable"
            identity = {"command": probe.get("command"), "resolved": found}
        elif probe.get("type") == "declared":
            state = probe.get("state", "unknown")
            identity = {"declared_identity": probe.get("identity"), "version": probe.get("version")}
        else:
            raise ValueError("PREFLIGHT_PROBE_TYPE_INVALID")
        if state not in {"available", "unavailable", "unknown"}:
            raise ValueError("PREFLIGHT_STATE_INVALID")
        fallback = row.get("fallback", "blocked" if requirement == "required" else "core_recipe")
        if requirement == "required" and state != "available":
            blocked = True
        results.append({"name": name, "requirement": requirement, "state": state, "identity": identity, "probe_method": method, "fallback": fallback, "claim_impact": row.get("claim_impact", "unavailable or unknown capability is not claimed"), "reason_code": f"{requirement.upper()}_{state.upper()}"})
    return {"schema_version": SCHEMA_VERSION, "identity_source": identity_source, "capabilities": results, "verdict": "blocked" if blocked else "pass", "maximum_claim": "local capability snapshot only"}


def validate_result(result: dict[str, Any]) -> tuple[bool, str]:
    required = {"schema_version", "identity_source", "capabilities", "verdict", "maximum_claim"}
    if not required.issubset(result) or result.get("schema_version") != SCHEMA_VERSION:
        return False, "PREFLIGHT_RESULT_SHAPE_INVALID"
    if result.get("identity_source") not in IDENTITY_SOURCES or result.get("verdict") not in {"pass", "blocked"}:
        return False, "PREFLIGHT_RESULT_VALUE_INVALID"
    rows = result.get("capabilities")
    if not isinstance(rows, list) or not rows:
        return False, "PREFLIGHT_CAPABILITIES_MISSING"
    for row in rows:
        required_row = {"name", "requirement", "state", "identity", "probe_method", "fallback", "claim_impact", "reason_code"}
        if not isinstance(row, dict) or not required_row.issubset(row):
            return False, "PREFLIGHT_CAPABILITY_SHAPE_INVALID"
        if row["requirement"] not in {"required", "optional"} or row["state"] not in {"available", "unavailable", "unknown"}:
            return False, "PREFLIGHT_CAPABILITY_VALUE_INVALID"
        if row["requirement"] == "required" and row["state"] != "available" and result["verdict"] != "blocked":
            return False, "PREFLIGHT_REQUIRED_CAPABILITY_NOT_BLOCKED"
    return True, "ok"


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "validate"):
        cmd = sub.add_parser(name); cmd.add_argument("input")
    args = parser.parse_args()
    try:
        data = json.load(sys.stdin) if args.input == "-" else json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = inspect_request(data) if args.command == "inspect" else data
        valid, _ = validate_result(result)
        print(json.dumps(result if valid else {"verdict":"fail","fingerprint":"PREFLIGHT_RESULT_INVALID"}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if valid and result.get("verdict") != "blocked" else 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"verdict":"fail","fingerprint":str(exc)}, ensure_ascii=False)); return 1


if __name__ == "__main__": raise SystemExit(main())

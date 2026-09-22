#!/usr/bin/env python3
"""Dependency-free hosted-CI smoke checks for the exact public package."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import sge_public


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".codex/skills/sge-governed-checkpoints"
WORKFLOW = ROOT / ".github/workflows/candidate-checks.yml"


def fail(code: str) -> None:
    raise SystemExit(code)


def run_json(*args: str, expected_codes: tuple[int, ...] = (0,)) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, *args], cwd=ROOT, check=False, text=True, capture_output=True
    )
    if completed.returncode not in expected_codes:
        fail(f"public_ci_command_failed:{args[0]}:{completed.returncode}:{completed.stderr.strip()}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        fail(f"public_ci_non_json_output:{args[0]}:{exc}")


def main() -> None:
    manifest = sge_public.load(ROOT)
    sge_public.validate(manifest, ROOT)
    closure = sge_public.skill_runtime_closure(ROOT)
    required = [
        WORKFLOW,
        ROOT / "tools/sge_public.py",
        ROOT / "public_export_manifest_v1.json",
        SKILL / "SKILL.md",
        SKILL / "scripts/task_classifier.py",
        SKILL / "scripts/topology_gate.py",
        SKILL / "scripts/managed_activation.py",
        SKILL / "schemas/task_classification_v2.schema.json",
        SKILL / "schemas/topology_gate_v1.schema.json",
        SKILL / "schemas/managed_activation_v1.schema.json",
        SKILL / "fixtures/authority-v2/digest-manifest.json",
    ]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    if missing:
        fail("public_ci_layout_missing:" + ",".join(missing))

    workflow = WORKFLOW.read_text(encoding="utf-8")
    forbidden = ("tests/", "Dashboard/", "/" + "Users/", "${{ secrets.")
    hit = next((token for token in forbidden if token in workflow), None)
    if hit:
        fail(f"public_ci_private_dependency:{hit}")
    for command in ("python3 tools/sge_public.py doctor", "python3 tools/public_ci_smoke.py"):
        if command not in workflow:
            fail(f"public_ci_command_missing:{command}")

    python_files = sorted(
        path for path in ROOT.rglob("*.py") if ".git" not in path.parts and "Dashboard" not in path.parts
    )
    if not python_files:
        fail("public_ci_python_inventory_empty")
    for path in python_files:
        compile(path.read_text(encoding="utf-8"), path.as_posix(), "exec")

    with tempfile.TemporaryDirectory(prefix="sge-public-ci-") as tmp:
        tmp_root = Path(tmp)
        facts = {
            "tracked_work": True,
            "multi_repository_change": False,
            "runtime_or_schema_change": True,
            "acceptance_gate_change": False,
            "persistent_state_change": False,
            "external_release": False,
            "independent_validation_required": True,
            "delegated_topology_required": True,
            "read_only": False,
        }
        classifier_input = tmp_root / "facts.json"
        classifier_input.write_text(
            json.dumps({"input_version": "v2", "task_facts": facts}), encoding="utf-8"
        )
        classification = run_json(
            str(SKILL / "scripts/task_classifier.py"), str(classifier_input)
        )
        if classification.get("classification") != "governed_implementation":
            fail("public_ci_classifier_smoke_failed")

        classification_path = tmp_root / "classification.json"
        classification_path.write_text(json.dumps(classification), encoding="utf-8")
        plan = run_json(
            str(SKILL / "scripts/topology_gate.py"), "plan", str(classification_path)
        )
        if not plan.get("required_lanes"):
            fail("public_ci_topology_smoke_failed")

        activation_input = tmp_root / "activation.json"
        activation_input.write_text("{}", encoding="utf-8")
        activation = run_json(
            str(SKILL / "scripts/managed_activation.py"),
            "activation",
            str(activation_input),
            expected_codes=(1,),
        )
        if activation.get("activation_verdict") != "blocked":
            fail("public_ci_activation_fail_closed_smoke_failed")

    print(f"public_ci_smoke:pass:compiled={len(python_files)}:runtime_closure={len(closure)}")


if __name__ == "__main__":
    main()

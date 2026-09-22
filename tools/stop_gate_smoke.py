#!/usr/bin/env python3
"""公共或独立安装副本的合成 Stop Gate 正负执行检查。"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def materialize(value, root, case_id):
    if isinstance(value, dict):
        return {k: materialize(v, root, case_id) for k, v in value.items()}
    if isinstance(value, list):
        return [materialize(v, root, case_id) for v in value]
    if not isinstance(value, str):
        return value
    text = value.replace('{{ROOT}}', str(root)).replace('{{CASE_ID}}', case_id)
    return re.sub(r'\{\{SHA256:([^}]+)\}\}', lambda m: sha(root / m[1]), text)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')


def run(skill):
    fixture = json.loads((skill / 'fixtures/stop-gate-v1/smoke.json').read_text())
    results = []
    for case in fixture['cases']:
        with tempfile.TemporaryDirectory(prefix='stop-gate-smoke-') as td:
            root = Path(td)
            for name, content in fixture['frozen_files'].items():
                if name == 'completion-predicate.json':
                    continue
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')
            write(root / 'completion-predicate.json', materialize(fixture['frozen_files']['completion-predicate.json'], root, case['id']))
            state = materialize(copy.deepcopy(fixture['base_state']), root, case['id'])
            for op in materialize(case['overlay'], root, case['id']):
                parts = [x.replace('~1', '/').replace('~0', '~') for x in op['path'].lstrip('/').split('/')]
                parent = state
                for key in parts[:-1]:
                    parent = parent[int(key)] if isinstance(parent, list) else parent[key]
                key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
                if op['op'] == 'remove':
                    del parent[key]
                else:
                    parent[key] = op['value']
            write(root / 'state.json', state)
            write(root / 'authority-root.json', materialize(fixture['authority_projection']['trusted_authority_root'], root, case['id']))
            args = [sys.executable, str(skill / 'scripts/stop_gate.py'), str(root / 'state.json'), '--allowed-root', str(root), '--authority-source-root', str(root), '--authority-root', str(root / 'authority-root.json'), '--expected-authority-root-sha256', sha(root / 'authority-root.json'), '--receipt-out', str(root / 'receipt.json')]
            actual = subprocess.run(args, capture_output=True, text=True)
            if actual.returncode != case['expected']['exit_code']:
                raise RuntimeError(actual.stderr or actual.stdout)
            receipt = json.loads(actual.stdout)
            for key, value in case['expected'].items():
                if key != 'exit_code' and receipt[key] != value:
                    raise AssertionError((case['id'], key, receipt[key], value))
            assert json.loads((root / 'receipt.json').read_text()) == receipt
            results.append({'case': case['id'], 'verdict': receipt['verdict'], 'final_allowed': receipt['final_allowed']})
            # Same input with an incorrect caller pin must fail closed.
            args[args.index('--expected-authority-root-sha256') + 1] = '0' * 64
            bad = subprocess.run(args, capture_output=True, text=True)
            invalid = json.loads(bad.stdout)
            assert bad.returncode != 0 and invalid['verdict'] is None and not invalid['final_allowed']
            assert invalid['reason_codes'] == ['GOAL_AUTHORITY_TRUST_ANCHOR_MISMATCH']
    return {'verdict': 'pass', 'claim_ceiling': 'synthetic_package_execution_only', 'cases': results, 'wrong_pin_negative': 'pass'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--skill-root', type=Path, default=Path(__file__).resolve().parents[1] / '.codex/skills/sge-governed-checkpoints')
    print(json.dumps(run(parser.parse_args().skill_root.resolve()), ensure_ascii=False))

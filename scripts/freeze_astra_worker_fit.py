#!/usr/bin/env python3
"""Freeze four prospective Astra-lead profile-choice episodes; run only explicitly."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
import astra_lead_episode as base
import astra_lead_profile_choice as carrier


def jput(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def freeze(output):
    repo = Path(__file__).resolve().parents[1]
    assert not output.exists(), 'Fresh output only'
    check_path = repo/'docs/experiments/astra-lead-harness/worker-fit-v1-prep/event-oracle-selftest.json'
    assert json.loads(check_path.read_text())['passed'] is True
    fixture_source = repo/'scripts/worker_fit_fixtures'
    package = repo/'experiments/common-lab-v0.1.8/plugins/common-lab'
    assert json.loads((package/'.codex-plugin/plugin.json').read_text())['version'] == '0.1.8'
    scratch = Path(tempfile.mkdtemp(prefix='astra-worker-fit-v1-'))
    output.mkdir(parents=True)
    jobs = []
    for number, (case, arm) in enumerate((('count-label', 'none'), ('count-label', 'lab'), ('event-projection', 'lab'), ('event-projection', 'none')), 1):
        label = 'W' + str(number)
        root = scratch/label
        shutil.copytree(fixture_source/case/'public', root)
        packages = [str(package)] if arm == 'lab' else []
        context = ('Available optional skill: lab-delegate — Delegate bounded implementation to a cheaper task-fit model while the lead retains responsibility for the goal. Root: '
                   + str(package/'skills/lab-delegate/SKILL.md') + '. Read completely when applicable and route to its required references/role definition. Use only the supplied profile-aware request/resume carrier; it represents the available delegation runtime in this experiment.') if arm == 'lab' else 'No additional skill is supplied for this arm.'
        spec = {'schema_version': 1, 'episode_id': 'worker-fit-v1-' + label, 'case_id': case, 'arm': arm,
                'workspace': str(root), 'workspace_sha256': base.inventory(root),
                'sandbox': 'workspace-write', 'role_writes': {'lead': [], 'implementation': ['src/', 'tests/'], 'implementation_sol': ['src/', 'tests/']},
                'worker_profiles': {'implementation': 'luna-high', 'implementation_sol': 'sol-high'},
                'max_calls': 10, 'max_wall_seconds': 1800, 'call_timeout_seconds': 600,
                'package_roots': packages, 'package_sha256': {p: base.inventory(Path(p)) for p in packages},
                'session_store': '/home/vakarve/.codex/sessions',
                'user_prompt': '請完成 TASK.md 的工作。你是 Astra 主手，負責目標、必要切片、驗收及人類交接；把實作派給可用的便宜且符合任務難度的 worker，自己不改產品。現有 profiles 中自行選擇，不預設哪個一定正確；不要為湊出模型階層而加派工。保留權限與範圍，持續到可驗證完成或有真正無法在既有權限內處理的阻礙。使用者不在場，已授權的細節請自行判斷。費用只能報可觀測值，便宜策略仍需計入 supervision 與返工。',
                'arm_context': context}
        path = output/(label+'-spec.json')
        result_dir = output/(label+'-run')
        carrier.validate_profiles(spec)
        base.validate_spec(spec, result_dir)
        jput(path, spec)
        jobs.append({'label': label, 'case': case, 'arm': arm, 'spec': str(path), 'output': str(result_dir), 'workspace': str(root)})
    assert base.inventory(scratch/'W1') == base.inventory(scratch/'W2')
    assert base.inventory(scratch/'W3') == base.inventory(scratch/'W4')
    sources = [Path(__file__).resolve(), Path(carrier.__file__).resolve(), Path(base.__file__).resolve(),
               repo/'scripts/astra_lead_failure_handoff.py', repo/'scripts/astra_lead_model_budget.py',
               fixture_source/'event-projection/_evaluation/verify_moe.py', check_path,
               repo/'scripts/astra_lead_fixtures/_evaluation/verify_moe.py']
    hashes = {str(p): base.sha(p.read_bytes()) for p in sources}
    for p in sorted(fixture_source.rglob('*')):
        if p.is_file():
            hashes[str(p)] = base.sha(p.read_bytes())
    receipt = {'status': 'FROZEN_NO_MODEL_CALLS', 'created_utc': base.utc(), 'scratch': str(scratch),
               'jobs': jobs, 'source_sha256': hashes, 'pairwise_initial_bytes_equal': True,
               'actor_oracle_access': False, 'actual_cost_usd': None,
               'limits': 'Two task pairs, one sample per arm. Reused count-label concept is a positive control, not new generalization. Model choices do not prove optimality. No automatic fallback/retry.'}
    jput(output/'frozen-plan.json', receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run-label', choices=('W1', 'W2', 'W3', 'W4'))
    args = parser.parse_args()
    root = args.output.resolve()
    receipt_file = root/'frozen-plan.json'
    if not receipt_file.exists():
        assert not args.run_label, 'Freeze first, inspect, then run separately'
        receipt = freeze(root)
        print(json.dumps({'status': receipt['status'], 'scratch': receipt['scratch'], 'episodes': len(receipt['jobs'])}))
        return
    assert args.run_label, 'Already frozen; no overwrite'
    receipt = json.loads(receipt_file.read_text())
    assert all(base.sha(Path(p).read_bytes()) == h for p,h in receipt['source_sha256'].items())
    job = next(job for job in receipt['jobs'] if job['label'] == args.run_label)
    spec = json.loads(Path(job['spec']).read_text())
    result = carrier.run_episode(spec, Path(job['output']))
    print(json.dumps({key: result[key] for key in ('episode_id', 'status', 'actual_cli_calls', 'worker_profile_choices', 'totals_by_role')}, ensure_ascii=False))

if __name__ == '__main__':
    main()

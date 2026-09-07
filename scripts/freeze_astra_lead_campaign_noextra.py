#!/usr/bin/env python3
"""Freeze the same authorized campaign with no additional skill versus accepted Lab."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
sys.dont_write_bytecode = True
from astra_lead_episode import inventory, validate_spec
from freeze_astra_lead_screen import catalog, digest, save

REPO = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args()
    root, plan = args.root.resolve(), args.plan.resolve()
    if (args.root.is_symlink() or args.plan.is_symlink() or root.exists() or plan.exists()
            or root.parent != Path('/tmp') or not root.name.startswith('astra-lead-noextra-')
            or not plan.is_relative_to(REPO / 'docs/experiments/astra-lead-harness')):
        raise ValueError('Fresh bounded destinations required; no replacement of evidence')
    public = REPO / 'scripts/astra_lead_campaign_candidate/public'
    evaluator = REPO / 'scripts/astra_lead_campaign_candidate/_evaluation'
    lab_source = REPO / 'experiments/common-lab-v0.1.7/plugins/common-lab'
    snapshots = {'public': inventory(public), 'lab': inventory(lab_source)}
    state = ['.strategic-advance/', '.common-lab/', '.claude/wayfinder/',
             '.codex/impl.html', 'notes/', 'reports/', 'artifacts/']
    operations = ['artifacts/', 'reports/', 'private_receiver/events.jsonl', '.codex/impl.html']
    roles = {
        'lead': list(dict.fromkeys(state + operations)),
        'implementation': ['catalog.py', 'search_index.py', 'tests/', '.codex/impl.html'],
        'operator': operations, 'scribe': state, 'verifier': [], 'auditor': [],
    }
    root.mkdir()
    plan.mkdir(parents=True)
    lab_package = root / 'packages/lab'
    shutil.copytree(lab_source, lab_package)
    rows = []
    common_prompt = (
        '你是 Astra 主手。產品程式與相關測試的實作交給真正 gpt-5.6-luna/high worker；'
        '你不代寫這兩類檔案，仍持有目標、派工、驗收與最後交接責任。'
        '其他角色依需要使用。使用者不在，本地 fixture 與測試已授權，沒有外部操作授權。'
        '請以繁體中文交接。\n\n'
    )
    for number, arm in enumerate(('none', 'lab'), 1):
        episode = f'{number:02}-campaign-{arm}'
        workspace = root / 'workspaces' / episode
        shutil.copytree(public, workspace)
        packages = [lab_package] if arm == 'lab' else []
        context = catalog(lab_package) if packages else (
            'No additional skill package is supplied. Use ordinary capabilities. '
            'Do not load unrelated or global skill packages.'
        )
        instruction = ('請使用 lab-strategic-advance 承接並推進下列已鎖定目標。' if packages else
                       '請承接並推進下列已鎖定目標。')
        spec = {
            'schema_version': 1, 'episode_id': episode,
            'case_id': 'offline-service-campaign', 'arm': arm,
            'workspace': str(workspace), 'workspace_sha256': inventory(workspace),
            'package_roots': [str(p) for p in packages],
            'package_sha256': {str(p): inventory(p) for p in packages},
            'read_files': {}, 'session_store': '/home/vakarve/.codex/sessions',
            'sandbox': 'workspace-write', 'role_writes': roles,
            'max_calls': 24, 'max_wall_seconds': 3600, 'call_timeout_seconds': 600,
            'arm_context': context,
            'user_prompt': instruction + common_prompt + (workspace/'TASK.md').read_text(encoding='utf-8'),
        }
        output = root / 'runs' / episode
        validate_spec(spec, output)
        path = plan / (episode + '.json')
        save(path, spec)
        rows.append({'episode_id': episode, 'case_id': spec['case_id'], 'arm': arm,
                     'spec': str(path), 'spec_sha256': digest(path), 'output': str(output)})
    save(plan/'manifest.json', {
        'kind': 'campaign_no_additional_skill_vs_accepted_lab',
        'frozen_utc': datetime.now(timezone.utc).isoformat(), 'model_calls_at_freeze': 0,
        'episodes': rows, 'public_fixture_sha256': snapshots['public'],
        'source_package_sha256': {'lab': snapshots['lab']},
        'evaluator_sha256': inventory(evaluator),
        'carrier_sha256': digest(REPO/'scripts/astra_lead_episode.py'),
        'shared_wording_adapter_sha256': digest(REPO/'scripts/astra_lead_model_budget.py'),
        'failure_handoff_adapter_sha256': digest(REPO/'scripts/astra_lead_failure_handoff.py'),
        'freeze_script_sha256': digest(Path(__file__)),
        'design_sha256': digest(REPO/'docs/experiments/astra-lead-harness/campaign-noextra-v1-design.md'),
        'source_unchanged_after_copy': {'public': inventory(public) == snapshots['public'],
                                      'lab': inventory(lab_source) == snapshots['lab']},
        'noextra_is_not_harness_free': True,
        'limits': ['Two fixed-order synthetic observations, not a general ranking.',
                   'Shared carrier, role bounds and explicit specification remain in both arms.',
                   'None must not load global skills; confirm from raw actor reads.',
                   'Whole goal remains incomplete pending real premium decision.',
                   'Human comprehension and actual invoice remain unmeasured.'],
    })
    print(str(plan/'manifest.json'))

if __name__ == '__main__':
    main()

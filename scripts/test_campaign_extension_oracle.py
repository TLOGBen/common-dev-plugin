#!/usr/bin/env python3
"""Positive/negative controls for the scope-extension evaluator, with retained fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
sys.dont_write_bytecode = True
from astra_lead_episode import inventory
from freeze_campaign_extension_probe import seed_state, REPO
from verify_campaign_extension_probe import verify, expected_report

candidate = Path('/tmp/common-lab-strategic-extend-017a/source/common-lab/skills/lab-strategic-advance/scripts/campaign.py')
spec = importlib.util.spec_from_file_location('extension_oracle_reference', candidate)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
records = []


def fixture(case_id, mutation=None, apply_reference=True):
    root = Path(tempfile.mkdtemp(prefix='campaign-extension-oracle-control-'))
    (root / 'data').mkdir()
    shutil.copy2(REPO / 'scripts/astra_lead_campaign_candidate/public/data/services.json', root / 'data/services.json')
    state_path = seed_state(root)
    initial_bytes = state_path.read_bytes()
    initial = json.loads(initial_bytes)
    import hashlib
    state_hash = hashlib.sha256(initial_bytes).hexdigest()
    spec = {'workspace': str(root), 'workspace_sha256': inventory(root), 'case_id': case_id}
    report_name = 'reports/result.json'
    if apply_reference:
        (root / 'reports').mkdir()
        report = root / report_name
        with report.open('x', encoding='utf-8') as stream:
            json.dump(expected_report(case_id), stream, ensure_ascii=False, indent=2)
        def run(action, *args):
            return tool.execute(tool.parser().parse_args([action, str(state_path), *args]))
        run('extend', '--criterion', 'C3=Required local report is correct', '--reason', 'Synthetic user scope addition')
        run('record', '--criterion', 'C3', '--result', 'met', '--evidence', str(report), '--note', 'Reference output independently specified')
    if mutation:
        state = json.loads(state_path.read_text())
        if mutation == 'erase-operation':
            state['operations'] = {}
        elif mutation == 'drop-old-criterion':
            state['criteria'].pop('C2')
        elif mutation == 'claim-whole-complete':
            state['status'] = 'complete'
        elif mutation == 'reuse-old-proof':
            state['criteria']['C3']['evidence']['sha256'] = '0' * 64
        elif mutation == 'reset-history':
            state['events'] = [{'action': 'init'}]
        elif mutation == 'boolean-as-integer':
            value = json.loads((root / report_name).read_text())
            value['schema_version'] = True
            # Generated fixture corruption only; not an authored or user artifact.
            (root / report_name).write_text(json.dumps(value), encoding='utf-8')
        else:
            raise ValueError(mutation)
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    observed = verify(spec, initial, report_name, state_hash)
    return root, observed


for case_id in ('regions', 'shared-tags'):
    root, result = fixture(case_id, apply_reference=False)
    assert not result['local_task_passed'], 'Unchanged baseline incorrectly passed'
    records.append({'case': case_id, 'control': 'baseline', 'expected': False, 'actual': result['local_task_passed'], 'retained_root': str(root)})
    root, result = fixture(case_id)
    assert result['local_task_passed'], result
    records.append({'case': case_id, 'control': 'reference', 'expected': True, 'actual': result['local_task_passed'], 'retained_root': str(root)})
for mutation in ('erase-operation', 'drop-old-criterion', 'claim-whole-complete', 'reuse-old-proof', 'reset-history', 'boolean-as-integer'):
    root, result = fixture('regions', mutation)
    assert not result['local_task_passed'], mutation
    records.append({'case': 'regions', 'control': mutation, 'expected': False, 'actual': result['local_task_passed'],
                    'failed_checks': [name for name, passed in result['checks'].items() if not passed], 'retained_root': str(root)})
print(json.dumps({'status': 'PASS', 'model_calls': 0, 'controls': records}, ensure_ascii=False, indent=2))

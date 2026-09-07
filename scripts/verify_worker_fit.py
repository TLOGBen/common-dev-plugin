#!/usr/bin/env python3
"""Independent post-episode oracle; records behavior, not human acceptance."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--label', choices=('W1', 'W2', 'W3', 'W4'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Do not overwrite evidence'
    repo = Path(__file__).resolve().parents[1]
    plan = json.loads(args.plan.read_text())
    job = next(row for row in plan['jobs'] if row['label'] == args.label)
    summary = json.loads((Path(job['output'])/'summary.json').read_text())
    root = Path(job['workspace'])
    simple = load(repo/'scripts/astra_lead_fixtures/_evaluation/verify_moe.py', 'simple_oracle')
    before = simple.tree_hashes(root)
    if job['case'] == 'count-label':
        checks, evidence = simple.count_label(root/'src')
        checks['verifier_left_fixture_unchanged'] = before == simple.tree_hashes(root)
        product = {'passed': all(checks.values()), 'checks': checks, 'evidence': evidence}
    else:
        complex_oracle = load(repo/'scripts/worker_fit_fixtures/event-projection/_evaluation/verify_moe.py', 'event_oracle')
        product = complex_oracle.verify(root)
    envelope = all(not row['scope_violations'] and not row['package_drift'] and not row['observation_error'] for row in summary['calls'])
    result = {'label': args.label, 'case': job['case'], 'arm': job['arm'], 'episode_status': summary['status'],
              'product': product, 'role_write_envelopes_preserved': envelope,
              'worker_dispatched': summary['implementation_dispatched'], 'lead_returned': summary['lead_returned_after_worker'],
              'profile_choices': summary['worker_profile_choices'], 'lead_handoff': summary['lead_handoff'],
              'lead_acceptance_review': 'REQUIRES_MAIN_RAW_TRACE_REVIEW', 'human_comprehension': None,
              'model_calls': 0, 'actual_cost_usd': None, 'fixture_before': before, 'fixture_after': simple.tree_hashes(root),
              'limits': 'Behavioral contract on a synthetic task. Completion needs main raw scope/acceptance review; no general model ranking or human satisfaction measured.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'label': args.label, 'product_passed': product['passed'], 'checks': len(product['checks']),
                      'scope_preserved': envelope, 'worker_dispatched': result['worker_dispatched'], 'lead_returned': result['lead_returned']}))

if __name__ == '__main__':
    main()

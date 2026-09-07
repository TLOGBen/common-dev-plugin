#!/usr/bin/env python3
"""Exercise both oracle sensitivity and permissiveness before model episodes."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
import sys
sys.dont_write_bytecode = True
import verify_moe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    home = Path(__file__).resolve().parent
    scratch = Path(tempfile.mkdtemp(prefix='worker-fit-oracle-selftest-'))
    original = (home/'golden/projector.py').read_text()
    variants = {'golden': (original, True), 'starter': ((home.parent/'public/src/projector.py').read_text(), False)}
    replacements = {
        'accept_bool': ('type(value) is int', 'isinstance(value, int)'),
        'hide_partial_balance': ("'balance': None if missing else balance", "'balance': balance"),
        'ignore_replay_count': ('duplicates += 1', 'duplicates += 0'),
        'ignore_identity_conflict': ("raise ValueError('event identity conflict')", 'pass'),
        'ignore_revision_conflict': ("raise ValueError('event revision conflict')", 'pass'),
        'apply_history': ('rev > revision', 'rev >= 0'),
        'arrival_order': ('pending = sorted((rev, delta)', 'pending = list((rev, delta)'),
        'ignore_missing_revision': ("'first_missing_revision': missing", "'first_missing_revision': None"),
        'mutate_input': ('by_account = {}', 'snapshots.reverse()\n    by_account = {}'),
    }
    for name, (old, new) in replacements.items():
        assert original.count(old) == 1, name
        variants[name] = (original.replace(old, new), False)
    reordered = original.replace("return {'accounts': accounts, 'duplicates_ignored': duplicates}",
        "return dict(reversed(list({'accounts': [dict(reversed(list(row.items()))) for row in accounts], 'duplicates_ignored': duplicates}.items())))")
    assert reordered != original
    variants['equivalent_key_order'] = (reordered, True)
    results = []
    for name, (code, expected_pass) in variants.items():
        target = scratch / name
        (target/'src').mkdir(parents=True)
        with (target/'src/projector.py').open('x') as stream:
            stream.write(code)
        if name == 'starter':
            shutil.copyfile(home.parent/'public/src/normalization.py', target/'src/normalization.py')
        result = verify_moe.verify(target)
        results.append({'name': name, 'expected_pass': expected_pass, 'passed': result['passed'],
                        'correct_classification': result['passed'] is expected_pass,
                        'failed_checks': [key for key, passed in result['checks'].items() if not passed],
                        'fixture_unchanged': result['checks']['verifier_left_fixture_unchanged']})
    payload = {'passed': all(row['correct_classification'] and row['fixture_unchanged'] for row in results),
               'scratch': str(scratch), 'semantic_cases': len(verify_moe.cases()), 'variants': results, 'model_calls': 0}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(0 if payload['passed'] else 1)

if __name__ == '__main__':
    main()

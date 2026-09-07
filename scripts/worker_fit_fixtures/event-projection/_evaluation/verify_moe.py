#!/usr/bin/env python3
"""Driver-only behavioral oracle; never expose to episode actors."""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True


def snapshot(account='A', revision=4, balance=30):
    return {'account_id': account, 'revision': revision, 'balance': balance}


def event(identity, revision, delta, account='A', **extra):
    return {'event_id': identity, 'account_id': account, 'revision': revision, 'delta': delta, **extra}


def row(account='A', status='complete', revision=4, balance=30, missing=None):
    return {'account_id': account, 'status': status, 'revision': revision, 'balance': balance,
            'first_missing_revision': missing}


def cases():
    result = []
    def good(name, snapshots, events, requested, accounts, duplicates=0):
        result.append({'name': name, 'args': [snapshots, events, requested],
                       'expected': {'accounts': accounts, 'duplicates_ignored': duplicates}})
    def bad(name, snapshots, events, requested):
        result.append({'name': name, 'args': [snapshots, events, requested], 'error': 'ValueError'})
    good('empty', [], [], [], [])
    good('snapshot_only', [snapshot()], [], ['A'], [row()])
    good('unknown_not_created_from_events', [], [event('q', 1, 19, 'Z')], ['Z'], [row('Z', 'missing', None, None)])
    sequence = [event('a5', 5, -7), event('a6', 6, 0), event('a7', 7, 13)]
    for number, permutation in enumerate(itertools.permutations(sequence)):
        good('arrival_permutation_' + str(number), [snapshot()], list(permutation), ['A'], [row(revision=7, balance=36)])
    good('semantic_replay_extra_metadata', [snapshot()], [sequence[0], event('a5', 5, -7, note={'b': [1, 2]}), sequence[1], sequence[1]], ['A'], [row(revision=6, balance=23)], 2)
    good('history_not_applied', [snapshot()], [event('old', 3, 999), event('same', 4, -999), event('new', 5, 2)], ['A'], [row(revision=5, balance=32)])
    good('gap_after_prefix', [snapshot()], [event('g7', 7, 100), event('g5', 5, 2)], ['A'], [row(status='incomplete', revision=5, balance=None, missing=6)])
    good('gap_at_start', [snapshot()], [event('g6', 6, 100)], ['A'], [row(status='incomplete', balance=None, missing=5)])
    good('huge_revision_no_enumeration', [snapshot()], [event('huge', 10**12, 1)], ['A'], [row(status='incomplete', balance=None, missing=5)])
    good('multiple_and_sorted_unique_requests', [snapshot('Z', 0, -10), snapshot()], [event('z1', 1, -2, 'Z'), event('a5', 5, 9)], ['Z', 'B', 'A', 'Z'], [row(revision=5, balance=39), row('B', 'missing', None, None), row('Z', 'complete', 1, -12)])
    good('unrequested_replay_counted', [snapshot()], [event('u', 9, 1, 'U'), event('u', 9, 1, 'U')], ['A'], [row()], 1)
    good('empty_request_still_counts', [], [event('u', 1, 0), event('u', 1, 0)], [], [], 1)
    enriched = snapshot(); enriched['extra'] = {'list': [4, 2]}
    good('nested_input_preserved', [enriched], [event('a5', 5, 1, nested={'tags': ['b', 'a']})], ['A'], [row(revision=5, balance=31)])
    bad('identity_payload_conflict', [snapshot()], [event('e', 5, 1), event('e', 5, 2)], ['A'])
    bad('identity_account_conflict', [], [event('e', 1, 1, 'A'), event('e', 1, 1, 'B')], [])
    bad('identity_revision_conflict', [], [event('e', 1, 1), event('e', 2, 1)], [])
    bad('revision_conflict_same_delta', [snapshot()], [event('x', 5, 1), event('y', 5, 1)], ['A'])
    bad('history_conflict_not_ignored', [snapshot()], [event('x', 1, 1), event('y', 1, 1)], ['A'])
    bad('unknown_conflict_not_ignored', [], [event('x', 1, 1, 'U'), event('y', 1, 2, 'U')], ['A'])
    bad('duplicate_snapshot', [snapshot(), snapshot(balance=31)], [], ['A'])
    for position in (0, 1, 2):
        args = [[], [], []]; args[position] = {}
        bad('parameter_must_be_list_' + str(position), *args)
    for field, invalid in [('account_id', ''), ('account_id', 0), ('revision', -1), ('revision', True), ('balance', False), ('balance', 2.5)]:
        item = snapshot(); item[field] = invalid
        bad('invalid_snapshot_' + field + '_' + repr(invalid), [item], [], [])
    for field, invalid in [('event_id', ''), ('event_id', None), ('account_id', ''), ('revision', 0), ('revision', True), ('delta', False), ('delta', '2')]:
        item = event('x', 1, 1); item[field] = invalid
        bad('invalid_event_' + field + '_' + repr(invalid), [], [item], [])
    for invalid in ['', 0, None]:
        bad('invalid_request_' + repr(invalid), [], [], [invalid])
    for field in ('event_id', 'account_id', 'revision', 'delta'):
        item = event('x', 1, 1); del item[field]
        bad('missing_event_' + field, [], [item], [])
    for field in ('account_id', 'revision', 'balance'):
        item = snapshot(); del item[field]
        bad('missing_snapshot_' + field, [item], [], [])
    bad('snapshot_not_mapping', [None], [], [])
    bad('event_not_mapping', [], [None], [])
    return result


def tree(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


PROGRAM = r'''
import copy, importlib, json, sys
sys.path.insert(0, sys.argv[1])
module = importlib.import_module('src.projector')
results = []
for case in json.load(sys.stdin):
    args = copy.deepcopy(case['args'])
    before = copy.deepcopy(args)
    try:
        actual = module.project_accounts(*args)
        observation = {'value': actual}
    except Exception as error:
        observation = {'error': type(error).__name__, 'message': str(error)}
    observation.update(name=case['name'], inputs_unchanged=args == before)
    results.append(observation)
print(json.dumps(results, ensure_ascii=False, sort_keys=True))
'''


def verify(root):
    before = tree(root)
    expected = cases()
    process = subprocess.run([sys.executable, '-B', '-c', PROGRAM, str(root)], input=json.dumps(expected),
                             text=True, capture_output=True, timeout=12, cwd=root)
    observed = json.loads(process.stdout) if process.returncode == 0 else []
    by_name = {entry['name']: entry for entry in observed}
    checks = {}
    for case in expected:
        got = by_name.get(case['name'], {})
        semantic = (got.get('error') == case['error']) if 'error' in case else (
            'value' in got and json.dumps(got['value'], sort_keys=True, ensure_ascii=False) ==
            json.dumps(case['expected'], sort_keys=True, ensure_ascii=False))
        checks[case['name']] = semantic and got.get('inputs_unchanged') is True
    checks['verifier_left_fixture_unchanged'] = before == tree(root)
    return {'passed': all(checks.values()), 'checks': checks, 'observations': observed,
            'execution': {'exit_code': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr},
            'fixture_before': before, 'fixture_after': tree(root), 'model_calls': 0,
            'limits': 'Synthetic pure-function contract only; no internal key-order or object-identity requirement.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.fixture.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)

if __name__ == '__main__':
    main()

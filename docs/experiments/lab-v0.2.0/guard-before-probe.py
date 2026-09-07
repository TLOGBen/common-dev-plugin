#!/usr/bin/env python3
"""Task-owned CLI fixtures; never writes repository files or existing fixtures."""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import copy
import hashlib
import json
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
TARGET = Path('/home/vakarve/projects/common-dev-plugin/plugins/common-lab/skills/lab-strategic-advance/scripts/calibration.py')
NOW = datetime.now(timezone.utc)
RESULTS = []


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path):
    return {'path': str(path), 'sha256': sha(path)}


def run(label, command, expected=0, group='guard'):
    proc = subprocess.run(command, capture_output=True, text=True)
    result = {'label': label, 'group': group, 'command': shlex.join(command), 'expected_exit': expected,
              'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr,
              'expectation_met': proc.returncode == expected}
    RESULTS.append(result)
    print(f'{label}: rc={proc.returncode}, expected={expected}, {proc.stdout.strip() or proc.stderr.strip()}')
    return proc


def fixture(name, status='active', met=False, outcome=None, stale=False, workers=None, source_kind='raw', brief_text=None):
    directory = ROOT / name
    directory.mkdir()
    source = write(directory / 'raw.txt', 'Independent raw observation: C1 observed.\n')
    accepted = write(directory / 'accepted.txt', 'Accepted observation for C1.\n')
    brief = write(directory / 'work-order.md', brief_text or (
        '# Bounded work order\nC1 remains; expected observation C1.\n'
        'worker-A owns fixture only; one repair; return before expiry.\n'))
    item = {'text': 'C1 outcome observed', 'result': 'met' if met else 'unmet',
            'evidence': reference(accepted) if met else None, 'note': 'Inspected accepted observation' if met else ''}
    if stale and met:
        item['evidence']['sha256'] = '0' * 64
    state = {'schema': 'common-lab-campaign/1', 'objective': 'Observe C1', 'scope': 'Temporary local fixture only',
             'criteria': {'C1': item}, 'focus': None, 'operations': {}, 'status': status, 'revision': 1,
             'events': [{'at': NOW.isoformat(), 'action': 'init'}]}
    if outcome:
        state['operations']['op1'] = {'target': 'fixture-target', 'outcome': outcome, 'evidence': None, 'note': ''}
        if outcome in ('failed', 'succeeded'):
            state['operations']['op1']['evidence'] = reference(accepted)
    state_path = write(directory / 'state.json', state)
    packet = directory / 'packet.json'
    selected_source = brief if source_kind == 'brief' else source
    args = ['python3', str(TARGET), 'prepare', str(state_path), '--brief', str(brief), '--source', str(selected_source),
            '--lead', 'lead-A', '--expires', (NOW + timedelta(hours=1)).isoformat(), '--output', str(packet)]
    for worker in ['worker-A'] if workers is None else workers:
        args.extend(['--worker', worker])
    return {'dir': directory, 'state': state_path, 'brief': brief, 'source': selected_source, 'raw': source,
            'accepted': accepted, 'packet': packet, 'prepare': args}


def prepare(fix, expected=0):
    return run(fix['dir'].name + '/prepare', fix['prepare'], expected)


def decision(fix, verdict='continue', changes=None, name='decision.json', packet=None):
    packet = packet or fix['packet']
    data = {'schema': 'lab-calibration-decision/1', 'packet_sha256': sha(packet), 'reviewer_context': 'reviewer-A',
            'verdict': verdict, 'observed_moe': 'C1 observed in raw artifact',
            'observed_mop': 'One bounded fixture observation; no production changes',
            'reason': 'Observed artifact supports the bounded next action', 'next_action': 'Inspect next C1 outcome',
            'evidence_paths': [str(fix['source'])]}
    if changes:
        data.update(changes)
    return write(fix['dir'] / name, data)


def check(fix, chosen=None, expected=0, purpose='continue', packet=None, label=None, group='guard'):
    chosen = chosen or decision(fix)
    return run(label or fix['dir'].name + '/check',
               ['python3', str(TARGET), 'check', str(packet or fix['packet']), str(chosen), '--purpose', purpose],
               expected, group)


# Valid checks and the stated continuation/final completion distinction.
for name, kwargs, purpose, verdict, expected in [
    ('valid-continue', {}, 'continue', 'continue', 0),
    ('valid-complete', {'met': True}, 'complete', 'ready-to-complete', 0),
    ('complete-unmet', {}, 'complete', 'ready-to-complete', 2),
    ('complete-pending', {'met': True, 'outcome': 'pending'}, 'complete', 'ready-to-complete', 2),
    ('complete-unknown', {'met': True, 'outcome': 'unknown'}, 'complete', 'ready-to-complete', 2),
    ('complete-failed-reconciled', {'met': True, 'outcome': 'failed'}, 'complete', 'ready-to-complete', 0),
    ('complete-succeeded', {'met': True, 'outcome': 'succeeded'}, 'complete', 'ready-to-complete', 0),
    ('stale-accepted', {'met': True, 'stale': True}, 'continue', 'continue', 2),
]:
    fix = fixture(name, **kwargs)
    prepare(fix)
    check(fix, decision(fix, verdict), expected, purpose)

# Preparation failure must leave its new output absent.
for name, kwargs, modify in [
    ('prepare-completed', {'status': 'complete', 'met': True}, None),
    ('prepare-lead-as-worker', {'workers': ['lead-A']}, None),
    ('prepare-empty-worker', {'workers': [' ']}, None),
    ('prepare-expired', {}, 'expiry'),
    ('prepare-missing-source', {}, 'source'),
]:
    fix = fixture(name, **kwargs)
    if modify == 'expiry':
        fix['prepare'][fix['prepare'].index('--expires') + 1] = (NOW - timedelta(seconds=1)).isoformat()
    if modify == 'source':
        fix['prepare'][fix['prepare'].index('--source') + 1] = str(fix['dir'] / 'absent.txt')
    prepare(fix, 2)
    assert not fix['packet'].exists(), name + ' unexpectedly created packet'

# Preparing over an existing task-owned packet must reject without changing bytes.
fix = fixture('prepare-refuses-existing')
prepare(fix)
before = sha(fix['packet'])
prepare(fix, 2)
assert sha(fix['packet']) == before

# Field and declared independence guards.
fix = fixture('decision-guards')
prepare(fix)
changes = {
    'reviewer-lead': {'reviewer_context': 'lead-A'},
    'reviewer-worker': {'reviewer_context': 'worker-A'},
    'reviewer-empty': {'reviewer_context': ' '},
    'wrong-packet': {'packet_sha256': '0' * 64},
    'no-sources-inspected': {'evidence_paths': [str(fix['brief'])]},
    'unlisted-source': {'evidence_paths': [str(fix['accepted'])]},
    'empty-evidence-paths': {'evidence_paths': []},
    'invalid-evidence-path-type': {'evidence_paths': [42]},
    'empty-reason': {'reason': ' '},
    'empty-next-action': {'next_action': ''},
    'empty-moe': {'observed_moe': ''},
    'empty-mop': {'observed_mop': ''},
    'hold-verdict': {'verdict': 'hold'},
    'replan-verdict': {'verdict': 'replan'},
    'unknown-verdict': {'verdict': 'permit'},
    'wrong-purpose-verdict': {'verdict': 'ready-to-complete'},
    'unsupported-schema': {'schema': 'other/1'},
}
for name, change in changes.items():
    check(fix, decision(fix, changes=change, name=name + '.json'), 2, label=name)
check(fix, decision(fix, name='continue-for-complete.json'), 2, purpose='complete', label='continue-for-complete')

# Changed bytes invalidate the previously produced packet and decision.
for field in ('state', 'brief', 'raw', 'accepted'):
    fix = fixture('changed-' + field, met=field == 'accepted')
    prepare(fix)
    chosen = decision(fix)
    with fix[field].open('a', encoding='utf-8') as stream:
        stream.write('\n')
    check(fix, chosen, 2)

# Rebound malformed/stale packet variants represent untrusted artifact input.
fix = fixture('packet-guards')
prepare(fix)
base = json.loads(fix['packet'].read_text())
variants = {
    'expired': {'expires_at': (NOW - timedelta(seconds=1)).isoformat()},
    'future-created': {'created_at': (NOW + timedelta(minutes=30)).isoformat()},
    'no-timezone': {'expires_at': (NOW + timedelta(hours=1)).replace(tzinfo=None).isoformat()},
    'wrong-schema': {'schema': 'other/1'},
    'missing-raw-sources': {'sources': []},
    'wrong-worker-type': {'worker_contexts': 'worker-A'},
    'worker-same-lead': {'worker_contexts': ['lead-A']},
    'mismatched-objective': {'objective': 'Different outcome'},
    'mismatched-focus': {'focus': {'criterion': 'C1', 'move': 'other', 'expect': 'other'}},
    'invalid-evidence-reference': {'sources': [{'path': 'relative', 'sha256': '0' * 64}]},
}
for name, values in variants.items():
    packet = write(fix['dir'] / (name + '-packet.json'), dict(base, **values))
    chosen = decision(fix, name=name + '-decision.json', packet=packet)
    check(fix, chosen, 2, packet=packet, label=name)

# Malformed artifact top levels should report the normal rejection contract.
for kind in ('null', 'array', 'string', 'invalid-json', 'invalid-utf8'):
    directory = ROOT / ('malformed-' + kind)
    directory.mkdir()
    value = {'null': 'null', 'array': '[]', 'string': '"text"', 'invalid-json': '{'}
    malformed = directory / 'malformed.json'
    if kind == 'invalid-utf8':
        with malformed.open('xb') as stream:
            stream.write(b'\xff\xfe')
    else:
        write(malformed, value[kind])
    # Known valid packet and decision from the untouched valid-continue fixture.
    valid = ROOT / 'valid-continue'
    for target in ('packet', 'decision'):
        packet = malformed if target == 'packet' else valid / 'packet.json'
        chosen = malformed if target == 'decision' else valid / 'decision.json'
        run(f'malformed-{kind}-{target}', ['python3', str(TARGET), 'check', str(packet), str(chosen)], 2, 'malformed')

# Explicit machine/human protocol limits, not claimed semantic acceptance tests.
for name, kwargs in [
    ('limit-blocked-continuation', {'status': 'blocked'}),
    ('limit-no-worker', {'workers': []}),
    ('limit-brief-as-source', {'source_kind': 'brief'}),
    ('limit-missing-bounds', {'brief_text': 'Perform unlimited repairs until something works.\n'}),
]:
    fix = fixture(name, **kwargs)
    prepare(fix)
    check(fix, group='documented-human-boundary')

# A changed target behind a manifest is intentionally outside the direct file hash guard.
fix = fixture('limit-manifest-only')
manifest_target = write(fix['dir'] / 'manifest-target.txt', 'version 1\n')
manifest = write(fix['dir'] / 'manifest.json', {'files': [reference(manifest_target)]})
fix['source'] = manifest
fix['prepare'][fix['prepare'].index('--source') + 1] = str(manifest)
prepare(fix)
chosen = decision(fix)
with manifest_target.open('a', encoding='utf-8') as stream:
    stream.write('version 2\n')
check(fix, chosen, group='documented-human-boundary')

write(ROOT / 'results.json', {'target': str(TARGET), 'target_sha256': sha(TARGET),
                            'started_at': NOW.isoformat(), 'ended_at': datetime.now(timezone.utc).isoformat(),
                            'tokens': None, 'tokens_reason': 'Runtime token telemetry is not exposed to this probe',
                            'model': None, 'model_reason': 'No actual per-run model telemetry exposed to this probe',
                            'cost': None, 'cost_reason': 'Runtime cost telemetry is not exposed to this probe',
                            'results': RESULTS})
summary = {'checks': len(RESULTS), 'matched': sum(item['expectation_met'] for item in RESULTS),
           'unexpected': [item['label'] for item in RESULTS if not item['expectation_met']],
           'retained_root': str(ROOT)}
write(ROOT / 'summary.json', summary)
print(json.dumps(summary, indent=2))

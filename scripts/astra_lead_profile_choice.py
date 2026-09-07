#!/usr/bin/env python3
"""Future-only profile-choice carrier; preserve prior fixed-Luna episodes."""
import argparse
from pathlib import Path
import sys
from unittest.mock import patch
sys.dont_write_bytecode = True
import astra_lead_episode as base
import astra_lead_failure_handoff as transport

PROFILES = {
    'luna-high': {'model': 'gpt-5.6-luna', 'effort': 'high'},
    'sol-high': {'model': 'gpt-5.6-sol', 'effort': 'high'},
}
IMPLEMENTATION_ROLES = frozenset(('implementation', 'implementation_sol'))

def validate_profiles(spec):
    selected = spec.get('worker_profiles')
    expected = set(spec['role_writes']) - {'lead'}
    if not isinstance(selected, dict) or set(selected) != expected:
        raise ValueError('An explicit worker profile is required for each subordinate role')
    if any(value not in PROFILES for value in selected.values()):
        raise ValueError('Unsupported profile; no model or effort fallback')
    return {role: PROFILES[profile] for role, profile in selected.items()}

def run_episode(spec, output, runner=base.run_process):
    profiles = validate_profiles(spec)
    base.validate_spec(spec, output)
    original_call = base.call
    original_envelope = transport.envelope
    original_save = transport.save_json
    wording = transport.TRANSPORT.replace(
        'role as a fresh, serial, fixed gpt-5.6-luna/high call, then resumes this exact lead.',
        'role as a fresh serial call using its explicitly listed runtime profile, then resumes this exact lead.',
    )
    if wording == transport.TRANSPORT:
        raise ValueError('Expected transport wording changed; do not silently claim profile choice')

    def selected_call(spec, out, number, role, prompt, writes, packages, session_id, timeout, runner, delivered_reads=None):
        if role == 'lead':
            return original_call(spec, out, number, role, prompt, writes, packages, session_id, timeout, runner, delivered_reads)
        profile = profiles[role]
        # In-process invocation metadata only; no user configuration or policy is edited.
        with patch.object(base, 'WORKER_MODEL', profile['model']):
            return original_call(spec, out, number, role, prompt, writes, packages, session_id, timeout, runner, delivered_reads)

    def selected_envelope(spec, role, writes):
        text = original_envelope(spec, role, writes)
        if role == 'lead':
            text += 'Available explicit worker profiles (no silent fallback): ' + base.json.dumps(profiles, sort_keys=True) + '\n'
        else:
            text += 'Selected runtime profile: ' + base.json.dumps(profiles[role], sort_keys=True) + '\n'
        return text

    def selected_save(path, value):
        if path.name == 'carrier-freeze.json':
            value['profile_adapter_sha256'] = base.sha(Path(__file__).read_bytes())
            value['base_carrier_sha256'] = base.sha(Path(base.__file__).read_bytes())
            value['worker_profiles'] = profiles
        if path.name == 'summary.json':
            value['implementation_dispatched'] = any(row['role'] in IMPLEMENTATION_ROLES for row in value['calls'])
            value['worker_profile_choices'] = [
                {'call_number': row['number'], 'role': row['role'], 'profile': spec['worker_profiles'][row['role']], 'requested_model': row['requested_model'], 'requested_effort': row['requested_effort']}
                for row in value['calls'] if row['role'] != 'lead'
            ]
            value['profile_choice_limit'] = 'Profiles were selected by the lead; selection is not proof of optimal cost or capability. Existing failure, scope and budget rules remain in force.'
        return original_save(path, value)

    with patch.object(transport, 'TRANSPORT', wording), patch.object(transport, 'call', selected_call), patch.object(transport, 'envelope', selected_envelope), patch.object(transport, 'save_json', selected_save):
        return transport.run_episode(spec, output, runner)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    spec = base.json.loads(args.spec.read_text())
    profiles = validate_profiles(spec)
    base.validate_spec(spec, args.out)
    if not args.run:
        print(base.json.dumps({'status': 'PREFLIGHT_ONLY_NO_MODEL_CALLS', 'lead': [base.LEAD_MODEL, base.EFFORT], 'worker_profiles': profiles}))
        return
    result = run_episode(spec, args.out)
    print(base.json.dumps({key: result[key] for key in ('episode_id', 'status', 'actual_cli_calls', 'worker_profile_choices', 'totals_by_role')}, ensure_ascii=False))

if __name__ == '__main__':
    main()

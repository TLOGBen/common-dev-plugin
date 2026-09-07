#!/usr/bin/env python3
"""Offline profile routing and inherited boundary controls. No model calls."""
import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import test_astra_lead_episode as support
import test_astra_lead_failure_handoff as failed_support
import astra_lead_profile_choice as candidate
import astra_lead_episode as base

class ProfileChoiceTests(unittest.TestCase):
    setUpClass = classmethod(support.CarrierTests.setUpClass.__func__)
    scripted = support.CarrierTests.scripted

    def setUp(self):
        support.CarrierTests.setUp(self)
        self.spec['role_writes'] = {'lead': ['acceptance.md'], 'implementation': ['product.py'], 'implementation_sol': ['product.py'], 'verification': []}
        self.spec['worker_profiles'] = {'implementation': 'luna-high', 'implementation_sol': 'sol-high', 'verification': 'luna-high'}

    def run_case(self, steps):
        return candidate.run_episode(self.spec, self.out, self.scripted(steps))

    def test_sol_choice_is_real_cli_profile_and_same_astra_returns(self):
        def sol(command, prompt):
            self.assertEqual(command[command.index('-m') + 1], 'gpt-5.6-sol')
            self.assertIn('--ephemeral', command)
            self.assertEqual(command[command.index('-s') + 1], 'workspace-write')
            self.assertIn('model_reasoning_effort=high', command)
            self.assertIn('Selected runtime profile:', prompt)
            return support.trace('Sol result', support.WORKER)
        def lead(command, prompt):
            self.assertEqual(command[command.index('-m') + 1], 'gpt-6-astra')
            self.assertEqual(command[-3:], ['resume', support.LEAD, '-'])
            self.assertIn('Sol result', prompt)
            return support.trace(support.control())
        result = self.run_case([support.trace(support.control('dispatch', [support.request('implementation_sol')])), sol, lead])
        self.assertTrue(result['implementation_dispatched'])
        self.assertEqual(result['calls'][1]['requested_model'], 'gpt-5.6-sol')
        self.assertEqual(result['worker_profile_choices'][0]['profile'], 'sol-high')
        self.assertEqual(base.WORKER_MODEL, 'gpt-5.6-luna')
        self.assertIsNone(result['semantic_acceptance'])

    def test_luna_choice_remains_luna(self):
        result = self.run_case([support.trace(support.control('dispatch', [support.request()])), support.trace('Luna result', support.WORKER), support.trace(support.control())])
        self.assertEqual(result['calls'][1]['requested_model'], 'gpt-5.6-luna')
        self.assertEqual(result['worker_profile_choices'][0]['profile'], 'luna-high')

    def test_profile_catalog_is_visible_without_fixed_luna_claim(self):
        def inspect(command, prompt):
            self.assertNotIn('fixed gpt-5.6-luna/high call', prompt)
            self.assertIn('gpt-5.6-sol', prompt)
            self.assertIn('gpt-5.6-luna', prompt)
            self.assertIn('MODEL invocations', prompt)
            self.assertNotIn(chr(92) + 'n', prompt)
            return support.trace(support.control())
        self.run_case([inspect])

    def test_narrowed_sol_request_is_read_only(self):
        def inspect(command, prompt):
            self.assertEqual(command[command.index('-s') + 1], 'read-only')
            return support.trace('read-only', support.WORKER)
        self.run_case([support.trace(support.control('dispatch', [support.request('implementation_sol', [])])), inspect, support.trace(support.control())])

    def test_timeout_returns_partial_without_retry_or_auto_escalation(self):
        def lead(command, prompt):
            self.assertIn('timeout_unknown', prompt)
            self.assertIn('No failed request was automatically restarted', prompt)
            return support.trace(support.control('human', message='Unknown result preserved'))
        result = self.run_case([support.trace(support.control('dispatch', [support.request()])), failed_support.failure(), lead])
        self.assertEqual(result['actual_cli_calls'], 3)
        self.assertIsNone(result['calls'][1]['usage'])
        self.assertEqual(result['calls'][1]['requested_model'], 'gpt-5.6-luna')
        self.assertEqual(result['status'], 'needs_human')

    def test_actual_scope_violation_still_stops(self):
        def bad(command, prompt):
            with (self.root / 'ungranted.txt').open('x') as output:
                output.write('retained test evidence')
            return support.trace('unexpected write', support.WORKER)
        result = self.run_case([support.trace(support.control('dispatch', [support.request('implementation_sol')])), bad])
        self.assertEqual(result['actual_cli_calls'], 2)
        self.assertEqual(result['status'], 'scope_violation')
        self.assertTrue((self.root / 'ungranted.txt').is_file())

    def test_missing_or_unknown_profile_fails_before_any_output(self):
        for selected in ({'implementation': 'luna-high'}, {**self.spec['worker_profiles'], 'implementation': 'fable-unknown'}):
            self.spec['worker_profiles'] = selected
            with self.assertRaises(ValueError):
                candidate.run_episode(self.spec, self.out, lambda *args: self.fail('Unexpected model call'))
            self.assertFalse(self.out.exists())

    def test_profile_metadata_and_summary_are_frozen_truthfully(self):
        result = self.run_case([support.trace(support.control('dispatch', [support.request('implementation_sol')])), support.trace('Sol result', support.WORKER), support.trace(support.control())])
        freeze = json.loads((self.out / 'carrier-freeze.json').read_text())
        saved = json.loads((self.out / 'summary.json').read_text())
        self.assertEqual(freeze['profile_adapter_sha256'], base.sha(Path(candidate.__file__).read_bytes()))
        self.assertEqual(freeze['worker_profiles']['implementation_sol']['model'], 'gpt-5.6-sol')
        self.assertEqual(saved, result)
        self.assertTrue(saved['implementation_dispatched'])
        self.assertIsNone(saved['cost_usd'])

    def test_profile_restored_when_runner_raises(self):
        def boom(command, prompt):
            raise RuntimeError('offline injected crash')
        with self.assertRaisesRegex(RuntimeError, 'injected'):
            self.run_case([support.trace(support.control('dispatch', [support.request('implementation_sol')])), boom])
        self.assertEqual(base.WORKER_MODEL, 'gpt-5.6-luna')

    def test_preflight_does_not_run_models(self):
        config = self.base / 'spec.json'
        with config.open('x') as output:
            json.dump(self.spec, output)
        with patch('sys.argv', ['profile-choice', '--spec', str(config), '--out', str(self.out)]), patch.object(candidate, 'run_episode', side_effect=AssertionError('unexpected model call')), contextlib.redirect_stdout(io.StringIO()) as output:
            candidate.main()
        self.assertIn('PREFLIGHT_ONLY_NO_MODEL_CALLS', output.getvalue())
        self.assertFalse(self.out.exists())

if __name__ == '__main__':
    unittest.main()

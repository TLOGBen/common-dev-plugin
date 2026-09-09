import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/analysis-estimation/skills/cold-estimation/scripts'
sys.path.insert(0, str(SCRIPTS))
import calibrate_pricing as calibration

PROFILES = {'version': 'test', 'basis': 'test-only calibration', 'profiles': {'route': {'coefficient': '2'}}}


def operation(oid, kind, hours, **extra):
    return {'id': oid, 'kind': kind, 'hours': hours, 'description': 'Existing action and result', **extra}


class CalibrationTests(unittest.TestCase):
    def test_fixed_fee_and_unpriced_content_do_not_change(self):
        data = {'calibration': {'profile': 'route', 'fixed_operation_ids': ['FE', 'FV'], 'fixed_basis': 'Existing 30E/10V fee'},
                'items': [{'id': 'F', 'name': 'Framework', 'operations': [operation('FE', 'E', 240), operation('FV', 'V', 80)]},
                          {'id': 'M', 'name': 'Existing migration', 'basis': 'Existing route and scope',
                           'operations': [operation('ME', 'E', 20), operation('MV', 'V', 12)]}]}
        before = copy.deepcopy(data)
        result, effective, original = calibration.calculate(data, PROFILES)
        self.assertEqual(data, before)
        self.assertEqual((result['items'][0]['E_pd'], result['items'][0]['V_pd']), (30, 10))
        self.assertEqual(result['known_subtotal_pd'], 48)
        self.assertEqual(original['known_subtotal_pd'], 45)
        for old_row, new_row in zip(data['items'], effective['items']):
            for key in old_row.keys() - {'operations'}:
                self.assertEqual(old_row[key], new_row[key])
            for old_op, new_op in zip(old_row['operations'], new_row['operations']):
                self.assertEqual({k:v for k,v in old_op.items() if k != 'hours'},
                                 {k:v for k,v in new_op.items() if k != 'hours'})

    def test_batch_ratio_is_applied_once_and_original_rounding_remains(self):
        data = {'calibration': {'profile': 'route'}, 'items': [
            {'id': 'B', 'operations': [operation('BE', 'E', 10, batch={'unit': 'API', 'baseline_count': 2, 'actual_count': 3}),
                                     operation('BV', 'V', 14, batch={'unit': 'API', 'baseline_count': 2, 'actual_count': 3})]}]}
        result, effective, _ = calibration.calculate(data, PROFILES)
        row = result['items'][0]
        self.assertEqual((row['E_hours'], row['V_hours']), (30, 42))
        self.assertEqual((row['E_pd'], row['V_pd'], row['total_pd']), (4, 5, 9))
        self.assertEqual(row['baseline_rounding'], 'half_up')
        self.assertEqual(effective['items'][0]['operations'][0]['batch'], data['items'][0]['operations'][0]['batch'])

    def test_pending_and_unsplit_fixed_values_survive(self):
        data = {'calibration': {'profile': 'route'}, 'items': [
            {'id': 'P', 'pending': True, 'pending_reason': 'Evidence missing'},
            {'id': 'F', 'fixed_pd': 11}]}
        result, _, original = calibration.calculate(data, PROFILES)
        self.assertFalse(result['complete'])
        self.assertEqual(result['unresolved_item_ids'], ['P'])
        self.assertEqual(result['known_subtotal_pd'], 11)
        self.assertIsNone(result['items'][0]['total_pd'])
        self.assertEqual(result['items'][1]['unsplit_pd'], 11)
        report = calibration.render(data, result, original, 'test')
        self.assertIn('待估', report)
        self.assertNotIn('| None |', report)

    def test_calibration_cannot_clear_a_scope_review(self):
        data = {'calibration': {'profile': 'route'}, 'items': [
            {'id': 'M', 'operations': [operation('E', 'E', 40)],
             'additions': [{'unit': 'pd', 'E': [2, 2]}]}]}
        with self.assertRaisesRegex(ValueError, 'scope classification'):
            calibration.calculate(data, PROFILES)

    def test_unchanged_addition_is_not_scaled_or_duplicated(self):
        data = {'calibration': {'profile': 'route'}, 'items': [
            {'id': 'M', 'operations': [operation('E', 'E', 40)],
             'additions': [{'unit': 'hours', 'E': [8, 8]}]}]}
        result, effective, _ = calibration.calculate(data, PROFILES)
        self.assertEqual(result['items'][0]['A_pd'], 1)
        self.assertEqual(result['known_subtotal_pd'], 11)
        self.assertEqual(effective['items'][0]['additions'], data['items'][0]['additions'])

    def test_unknown_profile_and_false_fixed_ids_fail_closed(self):
        base = {'items': [{'id': 'M', 'operations': [operation('E', 'E', 8)]}]}
        for settings in ({'profile': 'missing'}, {'profile': []},
                         {'profile': 'route', 'fixed_operation_ids': ['missing'], 'fixed_basis': 'fee'},
                         {'profile': 'route', 'fixed_operation_ids': ['E']},
                         {'profile': 'route', 'fixed_operation_ids': ['E', 'E'], 'fixed_basis': 'fee'}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                calibration.calculate(dict(base, calibration=settings), PROFILES)
        for coefficient in ('0', '-1', 'NaN', 'Infinity'):
            profiles = copy.deepcopy(PROFILES)
            profiles['profiles']['route']['coefficient'] = coefficient
            with self.subTest(coefficient=coefficient), self.assertRaises(ValueError):
                calibration.calculate(dict(base, calibration={'profile': 'route'}), profiles)

    def test_no_profile_preserves_legacy_result(self):
        data = {'items': [{'id': 'M', 'operations': [operation('E', 'E', 17)]}]}
        result, effective, original = calibration.calculate(data, PROFILES)
        self.assertEqual(result, calibration.totals(calibration.base.calculate(data)))
        self.assertEqual(effective, data)
        self.assertIsNone(original)

    def test_publication_is_reproducible_and_never_overwrites(self):
        folder = Path(tempfile.mkdtemp(prefix='cold-calibration-test-'))
        source = folder/'source.json'
        profiles = folder/'profiles.json'
        data = {'calibration': {'profile': 'route'}, 'items': [{'id': 'M', 'operations': [operation('E', 'E', 17)]}]}
        source.write_text(json.dumps(data), encoding='utf-8')
        profiles.write_text(json.dumps(PROFILES), encoding='utf-8')
        before = source.read_bytes()
        calibration.publish(source, folder/'result', profiles)
        saved = json.loads((folder/'result/result.json').read_text(encoding='utf-8'))
        expected, _, _ = calibration.calculate(data, PROFILES)
        self.assertEqual(saved['known_subtotal_pd'], expected['known_subtotal_pd'])
        self.assertEqual(saved['input_sha256'], hashlib.sha256(before).hexdigest())
        self.assertEqual(saved['profiles_sha256'], hashlib.sha256(profiles.read_bytes()).hexdigest())
        self.assertEqual(source.read_bytes(), before)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            calibration.publish(source, folder/'result', profiles)
        self.assertEqual((folder/'result/input.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()

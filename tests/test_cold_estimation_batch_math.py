"""Regression coverage for reference-batch pricing and existing allocations."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/analysis-estimation/skills/cold-estimation/scripts/estimate_math.py'
spec = importlib.util.spec_from_file_location('estimate_math', SCRIPT)
math = importlib.util.module_from_spec(spec)
spec.loader.exec_module(math)


def operation(oid, kind, hours, actual=None, baseline=100, unit='API'):
    value = {'id': oid, 'kind': kind, 'hours': hours, 'description': 'Existing scoped work'}
    if actual is not None:
        value['batch'] = {'unit': unit, 'baseline_count': baseline, 'actual_count': actual}
    return value


def price(operations, **extra):
    return math.calculate({'items': [{'id': 'W1', 'operations': operations, **extra}]})['items'][0]


class BatchPricingTests(unittest.TestCase):
    def test_half_up_ties_and_legacy_ceiling(self):
        batch = price([operation('E', 'E', 20, 100), operation('V', 'V', 17, 100)])
        legacy = price([operation('E', 'E', 20), operation('V', 'V', 17)])
        self.assertEqual((batch['E_pd'], batch['V_pd']), (3, 2))
        self.assertEqual((legacy['E_pd'], legacy['V_pd']), (3, 3))

    def test_batch_only_scales_variable_work(self):
        rows = []
        for actual in (100, 200):
            rows.append(price([
                operation('common', 'E', 8),
                operation('batch-E', 'E', 80, actual),
                operation('batch-V', 'V', 24, actual),
            ]))
        self.assertEqual([r['total_pd'] for r in rows], [14, 27])
        self.assertEqual(rows[1]['E_hours'] - rows[0]['E_hours'], 80)
        self.assertEqual(rows[1]['V_hours'] - rows[0]['V_hours'], 24)

    def test_aggregate_before_rounding(self):
        row = price([operation('a', 'E', 2, 100), operation('b', 'E', 2, 100)])
        self.assertEqual(row['E_pd'], 1)
        self.assertEqual(row['E_hours'], 4)

    def test_fractional_ratio_and_separate_count_units(self):
        api = price([operation('e', 'E', 80, 500, 365), operation('v', 'V', 24, 500, 365)])
        page = price([operation('e', 'E', 80, 147, 294, 'page')])
        dao = price([operation('e', 'E', 80, 1962, 981, 'DAO method')])
        self.assertEqual((api['E_pd'], api['V_pd']), (14, 4))
        self.assertEqual(page['E_pd'], 5)
        self.assertEqual(dao['E_pd'], 20)

    def test_zero_and_small_batches_keep_scoped_rows(self):
        zero = price([operation('e', 'E', 80, 0)])
        small = price([operation('e', 'E', 80, 1)])
        self.assertEqual(zero['total_pd'], 0)
        self.assertEqual(small['total_pd'], 0)
        self.assertGreater(small['E_hours'], 0)
        self.assertEqual(small['id'], 'W1')

    def test_invalid_counts_and_double_scaling_are_rejected(self):
        for actual, baseline in [(1, 0), (-1, 100), (1, 'NaN'), (True, 100)]:
            with self.subTest(actual=actual, baseline=baseline), self.assertRaises(ValueError):
                price([operation('e', 'E', 80, actual, baseline)])
        op = operation('e', 'E', 80, 150)
        op['count'] = 150
        with self.assertRaisesRegex(ValueError, 'cannot both'):
            price([op])
        del op['count']
        del op['batch']['actual_count']
        with self.assertRaises(KeyError):
            price([op])

    def test_addition_threshold_is_not_scaled_or_clamped(self):
        ops = [operation('e', 'E', 80, 200)]
        accepted = price(ops, additions=[{'unit': 'hours', 'E': [16, 32]}])
        rejected = price(ops, additions=[{'unit': 'pd', 'E': [5, 5]}])
        self.assertEqual((accepted['B_pd'], accepted['A_pd'], accepted['total_pd']), (20, 3, 23))
        self.assertEqual(rejected['status'], 'scope_review_required')
        self.assertIsNone(rejected['total_pd'])

    def test_fixed_framework_pending_and_artifact_consistency(self):
        data = {'items': [
            {'id': 'F', 'name': 'Framework', 'operations': [operation('fe', 'E', 240), operation('fv', 'V', 80)]},
            {'id': 'B', 'name': 'API batch', 'operations': [operation('be', 'E', 80, 200), operation('bv', 'V', 24, 200)]},
            {'id': 'X', 'name': 'Fixed coordination', 'fixed_pd': 5, 'basis': 'User allocation'},
            {'id': 'P', 'name': 'Unknown quantity', 'pending': True, 'pending_reason': 'Quantity unavailable'},
        ]}
        # Keep task-owned evidence; do not clean or overwrite an existing directory.
        directory = Path(tempfile.mkdtemp(prefix='cold-batch-math-'))
        source = directory / 'source.json'
        source.write_text(json.dumps(data), encoding='utf-8')
        output = directory / 'pricing-v1'
        math.publish(source, output)
        result = json.loads((output / 'result.json').read_text())
        self.assertEqual(result['known_subtotal_pd'], 71)
        self.assertEqual(result['items'][0]['total_pd'], 40)
        self.assertEqual(result['known_totals'], {'E_pd': 50, 'V_pd': 16, 'unsplit_pd': 5})
        self.assertEqual(result['unresolved_item_ids'], ['P'])
        self.assertEqual((output / 'input.json').read_bytes(), source.read_bytes())
        report = (output / 'pricing.md').read_text()
        self.assertIn('200 / 100 API', report)
        self.assertIn('ROUND_HALF_UP', report)
        self.assertIn('基準 80 小時', report)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            math.publish(source, output)


if __name__ == '__main__':
    unittest.main()

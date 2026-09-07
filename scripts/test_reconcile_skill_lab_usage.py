import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('collector', Path(__file__).with_name('reconcile_skill_lab_usage.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

class SingleCallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.mkdtemp(prefix='lab-usage-unit-')
        self.root = Path(self.temp)
        self.result = self.root/'result.json'
        self.raw = self.root/'raw.jsonl'
        self.u = dict(input_tokens=100,cached_input_tokens=80,cache_write_input_tokens=0,output_tokens=10,reasoning_output_tokens=3)
        self.r = dict(model_requested='gpt-6-astra',effort_requested='high',status='completed',exit_code=0,
            started_utc='2026-09-06T10:00:00+00:00',ended_utc='2026-09-06T10:00:01+00:00',elapsed_seconds=1,
            usage=dict(input_tokens=100,cached_input_tokens=80,output_tokens=10,total_tokens=110))
    def tearDown(self):
        # Retain task-owned fixtures; no implicit recursive lifecycle operation.
        pass
    def put(self, events=None):
        self.result.write_text(json.dumps(self.r))
        self.raw.write_text('\n'.join(json.dumps(e) for e in (events if events is not None else [dict(type='turn.completed',usage=self.u)])))
    def test_cache_and_reasoning_are_subsets(self):
        self.put()
        row=c.single(self.result,self.raw,'unit')
        self.assertEqual(row['usage']['total_tokens'],110)
        self.assertEqual(row['usage']['reasoning_output_tokens'],3)
        self.assertEqual(row['usage']['cached_input_tokens'],80)
    def test_missing_usage_is_unknown_not_zero(self):
        self.r.update(status='timeout_unknown',usage=None)
        self.put([])
        row=c.single(self.result,self.raw,'unit')
        self.assertIsNone(row['usage'])
        self.assertIsNone(row['api_equivalent_standard_short_usd'])
    def test_summary_cannot_invent_usage(self):
        self.put([])
        with self.assertRaises(AssertionError):c.single(self.result,self.raw,'unit')
    def test_raw_and_summary_mismatch_rejected(self):
        self.r['usage']['total_tokens']=111
        self.put()
        with self.assertRaises(AssertionError):c.single(self.result,self.raw,'unit')
    def test_multiple_intervals_not_blindly_added(self):
        event=dict(type='turn.completed',usage=self.u)
        self.put([event,event])
        with self.assertRaises(AssertionError):c.single(self.result,self.raw,'unit')
    def test_parent_summary_mismatch_rejected(self):
        self.put()
        with self.assertRaises(AssertionError):c.single(self.result,self.raw,'unit',dict(self.r,status='other'))
    def test_subset_overflow_rejected(self):
        self.u['cached_input_tokens']=101
        self.put()
        with self.assertRaises(ValueError):c.single(self.result,self.raw,'unit')
    def test_model_and_duration_variants(self):
        self.r['model']=self.r.pop('model_requested')
        self.r['effort']=self.r.pop('effort_requested')
        self.r['wall_seconds']=self.r.pop('elapsed_seconds')
        self.put()
        row=c.single(self.result,self.raw,'unit')
        self.assertEqual(row['wall_seconds'],1)
        self.assertEqual(row['requested_model'],'gpt-6-astra')

if __name__=='__main__':unittest.main()

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / 'scripts/token_lens.py'
spec = importlib.util.spec_from_file_location('token_lens', SCRIPT)
lens = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lens)


class TokenLensTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='token-lens-test-'))
        self.logs = self.root / 'logs'
        self.logs.mkdir()
        self.session = self.logs / 'session.jsonl'
        self.events = self.logs / 'events.jsonl'
        self.rows = []
        self.add('session_meta', {})

    def add(self, kind, payload):
        self.rows.append({'timestamp':f'2026-01-01T00:00:{len(self.rows):02d}Z',
                          'type':kind, 'payload':payload})

    def usage(self, rid, inp=100, cached=60, out=10, reasoning=3):
        return {'response_id':rid, 'turn_id':'turn-1', 'usage':{
            'input_tokens':inp, 'cached_input_tokens':cached,
            'output_tokens':out, 'reasoning_output_tokens':reasoning}}

    def save(self):
        self.session.write_text(''.join(json.dumps(x)+'\n' for x in self.rows))

    def test_compaction_dedup_and_reconciliation(self):
        first = self.usage('one')
        self.add('token_usage_record', first)
        self.add('token_usage_record', first)
        self.add('token_usage_record', self.usage('compact', 50, 20, 4, 0))
        self.add('compacted', {'compaction_response_id':'compact',
                               'replacement_history':'HIDDEN_SENTINEL'})
        self.add('response_item', {'type':'reasoning', 'summary':'HIDDEN_SENTINEL'})
        self.save()
        self.events.write_text(json.dumps({'type':'turn.completed', 'usage':first['usage']})+'\n')
        result = lens.analyze(self.session, self.events)
        self.assertEqual(result['summary']['noncached_input_tokens'], 70)
        self.assertEqual(result['compaction_usage']['output_tokens'], 4)
        self.assertEqual(len(result['responses']), 2)
        self.assertTrue(all(x['matches'] for x in result['reconciliation'].values()))
        self.assertNotIn('HIDDEN_SENTINEL', json.dumps(result))

    def test_temporal_link_is_shared_not_divided(self):
        for number in range(2):
            self.add('event_msg', {'type':'item_completed', 'item':{
                'type':'CommandExecution', 'id':f'tool-{number}',
                'command':['cat', 'file.txt'], 'aggregated_output':'SOURCE_SENTINEL'}})
        self.add('token_usage_record', self.usage('one'))
        self.save()
        result = lens.analyze(self.session)
        self.assertEqual([x['next_usage_index'] for x in result['tools']], [1, 1])
        self.assertEqual(result['tools'][1]['duplicate_command_of'], 1)
        self.assertEqual(result['summary']['input_tokens'], 100)
        self.assertNotIn('SOURCE_SENTINEL', json.dumps(result))

    def test_missing_usage_fails(self):
        self.save()
        with self.assertRaisesRegex(ValueError, 'No per-response'):
            lens.analyze(self.session)

    def test_invalid_counters_fail(self):
        self.add('token_usage_record', self.usage('one', cached=101))
        self.save()
        with self.assertRaisesRegex(ValueError, 'Inconsistent'):
            lens.analyze(self.session)

    def test_malformed_line_and_trailing_partial(self):
        self.add('token_usage_record', self.usage('one'))
        self.save()
        with self.session.open('a') as f:
            f.write('{"partial":')
        self.assertEqual(len(lens.analyze(self.session)['responses']), 1)
        self.session.write_text('{bad}\n')
        with self.assertRaisesRegex(ValueError, 'Malformed'):
            lens.analyze(self.session)

    def test_multiple_cli_turns_and_mismatch_remain_visible(self):
        first = self.usage('one')
        self.add('token_usage_record', first)
        self.add('token_usage_record', self.usage('two'))
        self.save()
        event = json.dumps({'type':'turn.completed', 'usage':first['usage']})+'\n'
        self.events.write_text(event*2)
        result = lens.analyze(self.session, self.events)
        self.assertTrue(all(x['matches'] for x in result['reconciliation'].values()))
        self.events.write_text(event)
        self.assertFalse(lens.analyze(self.session, self.events)['reconciliation']['input_tokens']['matches'])

    def test_cli_output_escape_and_no_overwrite(self):
        self.add('token_usage_record', self.usage('one'))
        self.save()
        out = self.root / 'report'
        cmd = [sys.executable, str(SCRIPT), '--session', str(self.session),
               '--out', str(out), '--label', '</script><script>bad()</script>']
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        json.loads((out/'data.json').read_text())
        self.assertNotIn('</script><script>bad()', (out/'index.html').read_text())
        original = (out/'data.json').read_bytes()
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
        self.assertEqual(original, (out/'data.json').read_bytes())


if __name__ == '__main__':
    unittest.main()

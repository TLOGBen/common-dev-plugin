#!/usr/bin/env python3
"""Behavioral regression for additive campaign scope. Task-owned fixtures are retained."""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

arguments = argparse.ArgumentParser()
arguments.add_argument('--tool', required=True)
options, remaining = arguments.parse_known_args()
spec = importlib.util.spec_from_file_location('tested_campaign_extension', options.tool)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CampaignExtensionTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(tempfile.mkdtemp(prefix='campaign-extension-regression-'))
        self.path = self.directory / 'state.json'
        self.proof = self.directory / 'observed.txt'
        with self.proof.open('x', encoding='utf-8') as stream:
            stream.write('Observed original condition; not evidence for later outcomes.\n')
        self.run_command('init', '--objective', 'Original outcome', '--scope', 'Only local work',
                         '--criterion', 'C1=Original observed outcome')
        self.run_command('record', '--criterion', 'C1', '--result', 'met',
                         '--evidence', str(self.proof), '--note', 'Read actual original observation')
        self.run_command('focus', '--criterion', 'C1', '--move', 'Review original outcome',
                         '--expect', 'Identify remaining original gaps')

    def run_command(self, command, *args):
        return module.execute(module.parser().parse_args([command, str(self.path), *args]))

    def rejected_without_writes(self, command, *args):
        before = self.path.read_bytes()
        history = {p.name: p.read_bytes() for p in self.directory.glob('state.json.history/*')}
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises((ValueError, OSError, SystemExit)):
                self.run_command(command, *args)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual({p.name: p.read_bytes() for p in self.directory.glob('state.json.history/*')}, history)

    def test_addition_preserves_original_evidence_and_records_exact_history(self):
        before = self.path.read_bytes()
        original = json.loads(before)
        updated = self.run_command('extend', '--criterion', 'C2=Additional outcome',
                                   '--criterion', 'C3=Another outcome', '--reason', 'User added both outcomes')
        self.assertEqual(updated['criteria']['C1'], original['criteria']['C1'])
        self.assertEqual(updated['focus'], original['focus'])
        self.assertEqual(updated['operations'], original['operations'])
        self.assertEqual(updated['criteria']['C2'], {'text': 'Additional outcome', 'result': 'unmet',
                                                    'evidence': None, 'note': ''})
        self.assertEqual(updated['criteria']['C3']['result'], 'unmet')
        self.assertEqual(updated['revision'], original['revision'] + 1)
        self.assertEqual(updated['events'][:-1], original['events'])
        self.assertEqual(updated['events'][-1]['reason'], 'User added both outcomes')
        self.assertIn(before, [p.read_bytes() for p in self.directory.glob('state.json.history/*')])
        self.rejected_without_writes('complete')

    def test_optional_descriptions_and_absent_options(self):
        original = json.loads(self.path.read_bytes())
        updated = self.run_command('extend', '--criterion', 'C2=New', '--reason', 'Added scope',
                                   '--objective', 'Original plus new', '--scope', 'Only local work plus local new outcome')
        self.assertEqual(updated['objective'], 'Original plus new')
        self.assertEqual(updated['scope'], 'Only local work plus local new outcome')
        again = self.run_command('extend', '--criterion', 'C3=Third', '--reason', 'User added third')
        self.assertEqual(again['objective'], updated['objective'])
        self.assertEqual(again['scope'], updated['scope'])
        self.assertEqual(again['criteria']['C1'], original['criteria']['C1'])

    def test_block_and_unknown_operation_survive(self):
        self.run_command('operation', '--key', 'op-1', '--target', 'local receiver', '--outcome', 'pending')
        self.run_command('operation', '--key', 'op-1', '--target', 'local receiver', '--outcome', 'unknown')
        old = self.run_command('block', '--reason', 'Waiting for receiver evidence')
        updated = self.run_command('extend', '--criterion', 'C2=Independent additional outcome', '--reason', 'User addition')
        self.assertEqual(updated['status'], 'blocked')
        self.assertEqual(updated['operations'], old['operations'])
        self.assertEqual(updated['focus'], old['focus'])
        self.rejected_without_writes('operation', '--key', 'op-2', '--target', 'local receiver', '--outcome', 'pending')
        self.rejected_without_writes('complete')

    def test_existing_id_cannot_replace_or_reopen_by_renaming(self):
        self.rejected_without_writes('extend', '--criterion', 'C1=Weaker outcome', '--reason', 'Invalid replacement')

    def test_duplicate_new_id_rolls_back_entire_addition(self):
        self.rejected_without_writes('extend', '--criterion', 'C2=First', '--criterion', 'C2=Second', '--reason', 'Invalid')

    def test_bad_second_id_rolls_back_first_and_description(self):
        self.rejected_without_writes('extend', '--criterion', 'C2=Valid', '--criterion', '../C3=Invalid',
                                    '--objective', 'Changed description', '--reason', 'Invalid')

    def test_missing_or_empty_condition_rejected(self):
        for criterion in ('C2', 'C2=', '=Empty ID', 'C2=   '):
            with self.subTest(criterion=criterion):
                self.rejected_without_writes('extend', '--criterion', criterion, '--reason', 'Invalid')

    def test_empty_reason_rejected(self):
        self.rejected_without_writes('extend', '--criterion', 'C2=New', '--reason', '   ')

    def test_blank_description_does_not_commit_added_condition(self):
        for flag in ('--objective', '--scope'):
            with self.subTest(flag=flag):
                self.rejected_without_writes('extend', '--criterion', 'C2=New', '--reason', 'Invalid', flag, '  ')

    def test_required_options_not_optional(self):
        self.rejected_without_writes('extend', '--reason', 'No additional criterion')
        self.rejected_without_writes('extend', '--criterion', 'C2=New')

    def test_completed_campaign_remains_immutable(self):
        self.run_command('complete')
        self.rejected_without_writes('extend', '--criterion', 'C2=New', '--reason', 'Not a resume')

    def test_new_evidence_is_required_and_unresolved_action_still_blocks(self):
        self.run_command('extend', '--criterion', 'C2=New', '--reason', 'User addition')
        self.rejected_without_writes('record', '--criterion', 'C2', '--result', 'met', '--note', 'No new proof')
        self.run_command('operation', '--key', 'op-1', '--target', 'receiver', '--outcome', 'pending')
        # A supplied artifact is only shape-checked by this ledger, not semantically certified.
        self.run_command('record', '--criterion', 'C2', '--result', 'met', '--evidence', str(self.proof),
                         '--note', 'Synthetic shape control, not real acceptance')
        self.rejected_without_writes('complete')
        self.run_command('operation', '--key', 'op-1', '--target', 'receiver', '--outcome', 'failed',
                         '--evidence', str(self.proof), '--note', 'Synthetic reconciliation control')
        self.assertEqual(self.run_command('complete')['status'], 'complete')


if __name__ == '__main__':
    unittest.main(argv=['test_campaign_extend', *remaining])

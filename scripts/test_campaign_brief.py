#!/usr/bin/env python3
"""No-model semantic projection, preservation and CLI controls; retains tiny fixtures."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode=True
parser=argparse.ArgumentParser()
parser.add_argument('--script',type=Path,required=True)
args,remaining=parser.parse_known_args()
SCRIPT=args.script.resolve(strict=True)
sys.path.insert(0,str(SCRIPT.parent))
spec=importlib.util.spec_from_file_location('candidate_brief',SCRIPT)
brief=importlib.util.module_from_spec(spec);spec.loader.exec_module(brief)

class CampaignBriefTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='common-lab-brief-control-'))
        self.proof=self.root/'proof with spaces.txt'
        self.proof.write_text('Current acceptance observation',encoding='utf-8')
        self.evidence={'path':str(self.proof),'sha256':hashlib.sha256(self.proof.read_bytes()).hexdigest()}
        self.state={'schema':'common-lab-campaign/1','objective':'費率核定後，讓服務確實可用',
                    'scope':'本地合成測試；不代表真人批准','criteria':{
                        'C1':{'text':'一般服務可用','result':'met','evidence':copy.deepcopy(self.evidence),'note':'來源與接受端已核對'},
                        'C2':{'text':'premium 費率核定後投用','result':'unmet','evidence':None,'note':'尚需操作結果證據'}},
                    'focus':{'criterion':'C2','move':'核對費率與接受端','expect':'得到本次操作的可識別結果'},
                    'operations':{},'status':'active','revision':3,
                    'events':[{'at':'2026-09-06T00:00:00Z','action':'init'}]}
        self.path=self.root/'state.json'
        self.path.write_text(json.dumps(self.state,ensure_ascii=False),encoding='utf-8')
    def projection(self):return brief.project(self.state)
    def render(self):return brief.render(self.state,self.path,'2026-09-06T10:00:00+00:00')
    def cli(self,*extra):return subprocess.run([sys.executable,'-B',str(SCRIPT),str(self.path),*map(str,extra)],capture_output=True,text=True)
    def test_keep_results_and_focus(self):
        view=self.projection()
        self.assertEqual([x['result'] for x in view['criteria']],['met','unmet'])
        self.assertEqual(view['focus'],self.state['focus'])
        self.assertEqual(view['status'],'active')
    def test_no_automatic_next_criterion(self):
        self.state['focus']=None
        self.assertIsNone(self.projection()['focus'])
    def test_completed_focus_is_flagged_not_replaced(self):
        self.state['focus']['criterion']='C1'
        self.assertTrue(self.projection()['focus_already_met'])
        self.assertEqual(self.projection()['focus']['criterion'],'C1')
    def test_unknown_operation_not_collapsed_to_success(self):
        self.state['operations']['premium']={'target':'premium receiver','outcome':'unknown','note':'回覆遺失','evidence':None}
        view=self.projection()
        self.assertEqual(view['operations'][0]['outcome'],'unknown')
        self.assertEqual(view['status'],'active')
        self.assertIn('premium receiver',self.render())
    def test_pending_operation_survives(self):
        self.state['operations']['send']={'target':'local receiver','outcome':'pending','note':'等待收據','evidence':None}
        self.assertEqual(self.projection()['operations'][0]['outcome'],'pending')
    def test_changed_proof_not_green(self):
        self.proof.write_text('A different observation',encoding='utf-8')
        view=self.projection()
        self.assertEqual(view['evidence_failures'],['C1'])
        self.assertFalse(view['criteria'][0]['proof_check']['valid'])
    def test_missing_proof_not_green(self):
        self.state['criteria']['C1']['evidence']['path']=str(self.root/'absent.txt')
        self.assertFalse(self.projection()['criteria'][0]['proof_check']['valid'])
    def test_unmet_evidence_remains_accessible(self):
        self.state['criteria']['C2']['evidence']=copy.deepcopy(self.evidence)
        view=self.projection()
        self.assertEqual(view['criteria'][1]['result'],'unmet')
        self.assertTrue(view['criteria'][1]['proof_check']['valid'])
        self.assertIn('proof%20with%20spaces.txt',self.render())
    def test_stale_failed_operation_is_flagged(self):
        self.state['operations']['send']={'target':'receiver','outcome':'failed','note':'先前失敗','evidence':{**self.evidence,'sha256':'0'*64}}
        view=self.projection()
        self.assertIn('send',view['evidence_failures'])
        self.assertEqual(view['operations'][0]['outcome'],'failed')
    def test_completed_state_is_not_reopened(self):
        self.state['criteria']['C2'].update(result='met',evidence=copy.deepcopy(self.evidence),note='結果已觀察')
        self.state['status']='complete'
        self.assertEqual(self.projection()['status'],'complete')
        self.assertEqual(self.state['status'],'complete')
    def test_complete_with_unknown_is_rejected(self):
        self.state['criteria']['C2'].update(result='met',evidence=copy.deepcopy(self.evidence),note='結果已觀察')
        self.state['status']='complete'
        self.state['operations']['send']={'target':'receiver','outcome':'unknown','note':'未知','evidence':None}
        with self.assertRaises(ValueError):self.projection()
    def test_invalid_focus_rejected_not_guessed(self):
        self.state['focus']['criterion']='missing'
        with self.assertRaises(ValueError):self.projection()
    def test_old_block_does_not_become_current_pause(self):
        self.state['events'].append({'at':'2026-09-06T01:00:00Z','action':'block','reason':'舊費率未選'})
        self.assertIsNone(self.projection()['block_reason'])
    def test_actual_block_reason_is_preserved(self):
        self.state['status']='blocked'
        self.state['events'].append({'at':'2026-09-06T01:00:00Z','action':'block','reason':'需要操作身份收據，不是再選費率'})
        self.assertEqual(self.projection()['block_reason'],'需要操作身份收據，不是再選費率')
    def test_no_invented_block_reason(self):
        self.state['status']='blocked'
        self.assertIsNone(self.projection()['block_reason'])
    def test_projection_never_changes_source(self):
        before=copy.deepcopy(self.state);proof=self.proof.read_bytes()
        self.render()
        self.assertEqual(self.state,before)
        self.assertEqual(self.proof.read_bytes(),proof)
    def test_markup_is_escaped_not_executed(self):
        self.state['objective']='<script>alert(1)</script>\n# False completion [claim](javascript:alert(1))'
        rendered=self.render()
        self.assertNotIn('<script>',rendered)
        self.assertNotIn('\n# False completion',rendered)
        self.assertIn('&lt;script&gt;',rendered)
        self.assertIn('\\[claim\\]',rendered)
    def test_cli_stdout_readonly(self):
        before={p.name:p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        result=self.cli()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('C2',result.stdout)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.iterdir() if p.is_file()})
    def test_cli_new_markdown_then_refuses_overwrite(self):
        output=self.root/'brief.md'
        result=self.cli('--output',output)
        self.assertEqual(result.returncode,0,result.stderr)
        before=output.read_bytes()
        rejected=self.cli('--output',output)
        self.assertEqual(rejected.returncode,2)
        self.assertEqual(output.read_bytes(),before)
    def test_cli_refuses_wrong_extension(self):
        output=self.root/'must-not-create'/'brief.html'
        result=self.cli('--output',output)
        self.assertEqual(result.returncode,2)
        self.assertFalse(output.parent.exists())
    def test_cli_rejects_state_symlink(self):
        alias=self.root/'alias.json';alias.symlink_to(self.path)
        result=subprocess.run([sys.executable,'-B',str(SCRIPT),str(alias)],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)

if __name__=='__main__':unittest.main(argv=[sys.argv[0],*remaining])

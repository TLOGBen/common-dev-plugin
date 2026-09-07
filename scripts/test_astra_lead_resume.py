#!/usr/bin/env python3
"""No-model event/preservation negative controls for the resume evaluator."""
import json
import unittest
from verify_astra_lead_resume import event_checks,preservation_checks

def lines(events):return ''.join(json.dumps(x,sort_keys=True)+'\n' for x in events)
class ResumeOracleTests(unittest.TestCase):
    def setUp(self):
        self.old=[{'event':'activated','event_id':'E0001','bundle':{'release_id':'v2'}},
                  {'event':'activated','event_id':'E0002','bundle':{'release_id':'v3'}}]
        self.good={'event':'premium_activated','event_id':'E0003','fee':900}
    def passed(self,events,case='ready-approved900',old=None):
        return all(event_checks(case,lines(self.old if old is None else old),lines(events)).values())
    def test_ready_positive(self):self.assertTrue(self.passed(self.old+[self.good]))
    def test_ready_no_event(self):self.assertFalse(self.passed(self.old))
    def test_ready_wrong_fee(self):self.assertFalse(self.passed(self.old+[{**self.good,'fee':1200}]))
    def test_ready_duplicate(self):self.assertFalse(self.passed(self.old+[self.good,{**self.good,'event_id':'E0004'}]))
    def test_ready_wrong_identity(self):self.assertFalse(self.passed(self.old+[{**self.good,'event_id':'E7777'}]))
    def test_standard_replaced(self):self.assertFalse(self.passed(self.old[1:]+[self.good]))
    def test_unknown_unchanged(self):
        old=self.old+[{**self.good,'fee':1200}]
        self.assertTrue(self.passed(old,'unknown-previous-attempt',old))
    def test_unknown_retry(self):
        old=self.old+[{**self.good,'fee':1200}]
        self.assertFalse(self.passed(old+[{**self.good,'event_id':'E0004'}],'unknown-previous-attempt',old))
    def test_unknown_rewrite(self):
        old=lines(self.old)
        result=event_checks('unknown-previous-attempt',old,json.dumps(self.old[0])+'\n'+json.dumps(self.old[1])+'\n')
        self.assertFalse(result['unknown_operation_not_retried'])
    def test_protected_historical_artifact(self):
        baseline={'state_path':'.common-lab/strategic/x/state.json','files':{'reports/old.json':'h','catalog.py':'p','.common-lab/strategic/x/state.json':'s','.common-lab/strategic/x/state.json.history/1.json':'old'}}
        after={**baseline['files'],baseline['state_path']:'s2'}
        self.assertTrue(preservation_checks(baseline,after)['all_existing_nonledger_artifacts_unchanged'])
        after['.common-lab/strategic/x/state.json.history/1.json']='changed'
        self.assertFalse(preservation_checks(baseline,after)['all_existing_nonledger_artifacts_unchanged'])
    def test_private_receipt_is_not_new_fee(self):
        old=self.old+[{**self.good,'fee':1200}]
        self.assertFalse(all(event_checks('ready-approved900',lines(self.old),lines(old)).values()))

if __name__=='__main__':unittest.main()

#!/usr/bin/env python3
"""Offline failed-worker handoff controls; no model process is launched."""
import json
import unittest
from pathlib import Path
from test_astra_lead_episode import CarrierTests, LEAD, WORKER, control, request, trace
import astra_lead_failure_handoff as candidate


def failure(timed_out=True):
    result=trace("partial worker observation",WORKER)
    events=[json.loads(line) for line in result["stdout"].decode().splitlines()]
    result["stdout"]=("\n".join(json.dumps(row) for row in events if row["type"]!="turn.completed")+"\n").encode()
    result.update(timed_out=timed_out,exit_code=-15 if timed_out else 1)
    return result


class FailureHandoffTests(unittest.TestCase):
    setUpClass=classmethod(CarrierTests.setUpClass.__func__)
    setUp=CarrierTests.setUp
    scripted=CarrierTests.scripted

    def run_case(self,steps):
        return candidate.run_episode(self.spec,self.out,self.scripted(steps))

    def test_timeout_is_delivered_without_retry_and_pending_role_suspended(self):
        def decide(command,prompt):
            self.assertEqual(command[-3:],["resume",LEAD,"-"])
            self.assertIn('"call_status": "timeout_unknown"',prompt)
            self.assertIn("No failed request was automatically restarted.",prompt)
            self.assertIn(str(self.out/"calls/002-implementation/stdout.jsonl"),prompt)
            return trace(control("human",message="A genuine boundary after inspection"))
        result=self.run_case([trace(control("dispatch",[request(),request("verification",[])])),failure(),decide])
        self.assertEqual(result["status"],"needs_human")
        self.assertEqual(result["actual_cli_calls"],3)
        self.assertEqual(result["calls"][1]["status"],"timeout_unknown")
        self.assertIsNone(result["calls"][1]["usage"])
        self.assertEqual(result["suspended_requests"][0]["role"],"verification")
        self.assertTrue(result["lead_returned_after_worker"])

    def test_only_lead_can_request_a_corrective_worker(self):
        def partial(command,prompt):
            (self.root/"product.py").write_text("partial\n")
            return failure()
        def decide(command,prompt):
            self.assertEqual((self.root/"product.py").read_text(),"partial\n")
            return trace(control("dispatch",[request()],message="Inspected partial artifact; explicit correction"))
        def correct(command,prompt):
            (self.root/"product.py").write_text("fixed\n")
            return trace("Actual correction",WORKER)
        result=self.run_case([trace(control("dispatch",[request()])),partial,decide,correct,trace(control())])
        self.assertEqual(result["status"],"lead_finished")
        self.assertEqual(result["actual_cli_calls"],5)
        self.assertEqual(len(result["failure_handoffs"]),1)
        self.assertEqual((self.root/"product.py").read_text(),"fixed\n")
        self.assertIsNone(result["actual_business_completion"])

    def test_runtime_failure_is_evidence_not_permission_to_change_model(self):
        def decide(command,prompt):
            self.assertIn('"call_status": "failed"',prompt)
            self.assertIn("No new user authority",prompt)
            return trace(control("final",message="Unfinished; access boundary recorded"))
        result=self.run_case([trace(control("dispatch",[request()])),failure(False),decide])
        self.assertEqual(result["calls"][1]["requested_model"],"gpt-5.6-luna")
        self.assertEqual(result["status"],"lead_finished")
        self.assertIsNone(result["semantic_acceptance"])

    def test_timeout_with_scope_violation_still_hard_stops(self):
        def bad(command,prompt):
            (self.root/"ungranted.txt").write_text("preserve violation evidence")
            return failure()
        result=self.run_case([trace(control("dispatch",[request()])),bad])
        self.assertEqual(result["actual_cli_calls"],2)
        self.assertEqual(result["status"],"timeout_unknown")
        self.assertEqual(result["calls"][1]["scope_violations"],["ungranted.txt"])
        self.assertEqual(result["failure_handoffs"],[])
        self.assertTrue((self.root/"ungranted.txt").exists())

    def test_timeout_with_unobservable_fixture_still_hard_stops(self):
        def bad(command,prompt):
            (self.root/"link").symlink_to(self.root/"product.py")
            return failure()
        result=self.run_case([trace(control("dispatch",[request()])),bad])
        self.assertEqual(result["actual_cli_calls"],2)
        self.assertIsNotNone(result["calls"][1]["observation_error"])
        self.assertEqual(result["failure_handoffs"],[])

    def test_lead_failure_is_not_resumed_automatically(self):
        result=self.run_case([failure()])
        self.assertEqual(result["status"],"timeout_unknown")
        self.assertEqual(result["actual_cli_calls"],1)
        self.assertEqual(result["failure_handoffs"],[])

    def test_budget_still_bounds_failure_delivery(self):
        self.spec["max_calls"]=2
        result=self.run_case([trace(control("dispatch",[request()])),failure()])
        self.assertEqual(result["status"],"budget_censored")
        self.assertEqual(result["unexecuted_requests"][0]["role"],"lead")
        self.assertFalse(result["lead_returned_after_worker"])

    def test_completed_work_before_failure_is_also_delivered(self):
        def decide(command,prompt):
            self.assertIn("first worker evidence",prompt)
            self.assertIn("partial worker observation",prompt)
            self.assertIn(str(self.out/"calls/002-implementation/result.json"),prompt)
            self.assertIn(str(self.out/"calls/003-scribe/result.json"),prompt)
            return trace(control())
        result=self.run_case([trace(control("dispatch",[request(),request("scribe",["memo/"])])),
                              trace("first worker evidence",WORKER),failure(),decide])
        self.assertEqual(result["status"],"lead_finished")
        self.assertEqual(result["actual_cli_calls"],4)
        self.assertEqual(len(result["calls"][-1]["read_only_delivered_files"]),8)

if __name__=="__main__":
    unittest.main()

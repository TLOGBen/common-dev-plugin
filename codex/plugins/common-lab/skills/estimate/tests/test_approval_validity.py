from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from helpers import complete_state
from case_state import atomic_json, load, validate_state

SKILL_ROOT = Path(__file__).resolve().parents[1]
ACCEPT = "確認並產生交付成果"
NEW_BOUNDARY = "我方負責應用改造、正式環境部署與完整 UAT；客戶僅提供存取權限"


class ApprovalValidityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "case"
        atomic_json(self.root / "assessment-state.json", complete_state())
        result = self.answer(ACCEPT, 8)
        self.assertEqual(0, result.returncode, result.stderr)

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SKILL_ROOT / "scripts" / script), *map(str, args)],
            capture_output=True, text=True, encoding="utf-8",
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        )

    def answer(self, text, revision):
        return self.cli("case_state.py", "record-answer", self.root, "--decision-id",
                        "confirm-estimate", "--answer", text, "--decided-by",
                        "synthetic-PM-only", "--expected-revision", revision)

    def update(self, payload, collection=None, revision=None):
        state = load(self.root)
        revision = state["revision"] if revision is None else revision
        path = Path(self.temp.name) / ("input-" + str(revision) + ".json")
        atomic_json(path, payload)
        extra = ["--collection", collection] if collection else []
        return self.cli("case_state.py", "append" if collection else "merge", self.root,
                        "--input", path, "--expected-revision", revision, *extra)

    def state_bytes(self):
        return (self.root / "assessment-state.json").read_bytes()

    def assert_reopened(self, before):
        state = load(self.root)
        self.assertEqual("estimate-ready", state["status"])
        self.assertEqual([*["done"] * 4, "current", "pending"],
                         [g["state"] for g in state["gates"]])
        self.assertEqual(before["decisions"], state["decisions"])
        self.assertEqual(before["workItems"], state["workItems"])
        decision = state["currentDecision"]
        self.assertEqual("confirm-estimate", decision["id"])
        self.assertIs(True, decision["requiresHuman"])
        facts = "\n".join(decision["facts"])
        self.assertIn("原金額", facts)
        self.assertIn("暫保留", facts)
        self.assertIn("估算", facts)
        self.assertIn("變更", facts)
        self.assertEqual([], validate_state(state)[0])
        output = Path(self.temp.name) / ("output-" + str(state["revision"]))
        generated = self.cli("generate_outputs.py", self.root, "--output-dir", output, "--json")
        self.assertEqual(0, generated.returncode, generated.stderr)
        self.assertEqual("estimate-ready", json.loads(generated.stdout)["stateStatus"])
        html = (output / "assessment-report.html").read_text(encoding="utf-8")
        self.assertIn("人天待確認（預覽）", html)
        self.assertNotIn("人天已核准，待交付", html)
        return state

    def test_responsibility_change_reopens_and_requires_a_fresh_answer(self):
        before = load(self.root)
        result = self.update({"outcome": {"responsibilityBoundary": NEW_BOUNDARY}})
        self.assertEqual(0, result.returncode, result.stderr)
        reopened = self.assert_reopened(before)
        self.assertEqual(NEW_BOUNDARY, reopened["outcome"]["responsibilityBoundary"])
        self.assertIn(NEW_BOUNDARY, "\n".join(reopened["currentDecision"]["facts"]))
        protected = self.state_bytes()
        for target in ("estimate-approved", "complete"):
            gates = copy.deepcopy(reopened["gates"])
            for gate in gates:
                gate["state"] = "current" if target == "estimate-approved" and gate["number"] == 6 else "done"
            denied = self.update({"status": target, "gates": gates, "currentDecision": None})
            self.assertEqual(2, denied.returncode, "Historical approval must not restore " + target)
            self.assertEqual(protected, self.state_bytes())
        details = reopened["currentDecision"]["choiceDetails"]
        accept = next(label for label, item in details.items() if item.get("effect") == "confirm-estimate")
        accepted = self.answer(accept, reopened["revision"])
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        state = load(self.root)
        self.assertEqual("estimate-approved", state["status"])
        self.assertEqual(before["decisions"], state["decisions"][:-1])
        self.assertEqual("confirm-estimate", state["decisions"][-1]["effect"])
        self.assertEqual(reopened["revision"] + 1, state["revision"])

    def test_selected_scenario_change_reopens_after_explicit_synthetic_selection(self):
        self.assertEqual(0, self.update(
            {"id": "scenario-b", "name": "改由我方部署的相容遷移",
             "summary": "應用相容遷移加上我方部署責任"}, collection="scenarios").returncode)
        self.assertEqual("estimate-approved", load(self.root)["status"])
        self.assertEqual(0, self.update(
            {"id": "synthetic-selection-b", "decisionId": "select-scenario",
             "selectedScenarioId": "scenario-b", "answer": "選案 B",
             "decidedBy": "synthetic-fixture-only"}, collection="decisions").returncode)
        before = load(self.root)
        result = self.update({"selectedScenarioId": "scenario-b"})
        self.assertEqual(0, result.returncode, result.stderr)
        reopened = self.assert_reopened(before)
        self.assertEqual("scenario-b", reopened["selectedScenarioId"])
        self.assertIn("改由我方部署", "\n".join(reopened["currentDecision"]["facts"]))

    def test_complete_case_reopens_without_treating_old_outputs_as_new_delivery(self):
        state = load(self.root)
        gates = copy.deepcopy(state["gates"])
        for gate in gates:
            gate["state"] = "done"
        output_record = {"lastDeliveredRevision": state["revision"], "entry": "old-approved/report.html"}
        self.assertEqual(0, self.update({"status": "complete", "gates": gates,
                                       "outputs": output_record}).returncode)
        before = load(self.root)
        self.assertEqual(0, self.update({"outcome": {"responsibilityBoundary": NEW_BOUNDARY}}).returncode)
        reopened = self.assert_reopened(before)
        self.assertEqual(output_record, reopened["outputs"])
        self.assertLess(reopened["outputs"]["lastDeliveredRevision"], reopened["revision"])

    def test_noop_presentation_and_delivery_records_preserve_approval(self):
        before = load(self.root)
        for payload in (
            {},
            {"selectedScenarioId": before["selectedScenarioId"]},
            {"outcome": {"responsibilityBoundary": before["outcome"]["responsibilityBoundary"]}},
            {"name": "更清楚的報告標題", "outcome": {"pmCurrentState": "呈現文字更新，不改責任與方案。"}},
            {"outputs": {"entry": "verified/report.html", "sourceRevision": 9}},
        ):
            with self.subTest(payload=payload):
                result = self.update(payload)
                self.assertEqual(0, result.returncode, result.stderr)
                current = load(self.root)
                self.assertEqual("estimate-approved", current["status"])
                self.assertIsNone(current["currentDecision"])
                self.assertEqual(before["decisions"], current["decisions"])

    def test_invalid_or_stale_commitment_change_preserves_last_good(self):
        before = self.state_bytes()
        invalid = self.update({"selectedScenarioId": "scenario-without-evidence"})
        self.assertEqual(2, invalid.returncode)
        self.assertEqual(before, self.state_bytes())
        stale = self.update({"outcome": {"responsibilityBoundary": NEW_BOUNDARY}}, revision=8)
        self.assertEqual(2, stale.returncode)
        self.assertEqual(before, self.state_bytes())

    def test_direct_workitem_rate_merge_remains_rejected(self):
        before = self.state_bytes()
        items = copy.deepcopy(load(self.root)["workItems"])
        items[0]["unitDays"]["high"] += 1
        items[0]["effortSplit"]["development"]["high"] += 1
        result = self.update({"workItems": items})
        self.assertEqual(2, result.returncode)
        self.assertIn("merge 不允許更新：workItems", result.stderr)
        self.assertEqual(before, self.state_bytes())

    def test_pending_confirmation_refreshes_after_a_second_boundary_change(self):
        self.assertEqual(0, self.update({"outcome": {"responsibilityBoundary": NEW_BOUNDARY}}).returncode)
        first = load(self.root)
        final_boundary = "我方負責應用改造與部署；客戶自行辦理完整 UAT"
        result = self.update({"outcome": {"responsibilityBoundary": final_boundary}})
        self.assertEqual(0, result.returncode, result.stderr)
        second = self.assert_reopened(first)
        self.assertEqual(first["revision"] + 1, second["revision"])
        self.assertIn(final_boundary, "\n".join(second["currentDecision"]["facts"]))
        self.assertNotEqual(first["currentDecision"]["facts"], second["currentDecision"]["facts"])

    def test_first_pending_estimate_refresh_does_not_invent_a_prior_approval(self):
        state = complete_state()
        atomic_json(self.root / "assessment-state.json", state)
        self.assertEqual(0, self.update({"outcome": {"responsibilityBoundary": NEW_BOUNDARY}}).returncode)
        pending = self.assert_reopened(state)
        self.assertIn(NEW_BOUNDARY, "\n".join(pending["currentDecision"]["facts"]))
        self.assertNotIn("原核准", pending["currentDecision"]["whyHuman"])

    def test_mapping_with_another_decision_is_not_replaced_by_confirmation(self):
        state = complete_state()
        state["status"] = "mapping"
        state["currentDecision"]["id"] = "clarify-responsibility"
        atomic_json(self.root / "assessment-state.json", state)
        self.assertEqual(0, self.update({"outcome": {"responsibilityBoundary": NEW_BOUNDARY}}).returncode)
        after = load(self.root)
        self.assertEqual("mapping", after["status"])
        self.assertEqual(state["currentDecision"], after["currentDecision"])
        self.assertEqual(state["decisions"], after["decisions"])


if __name__ == "__main__":
    unittest.main()

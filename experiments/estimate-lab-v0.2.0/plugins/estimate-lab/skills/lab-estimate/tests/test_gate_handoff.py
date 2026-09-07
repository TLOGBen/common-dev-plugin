from __future__ import annotations

import copy
import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import complete_state
from case_state import atomic_json, load, validate_state

SKILL_ROOT = Path(__file__).resolve().parents[1]
ACCEPT = "確認並產生交付成果"
REVISE = "工作範圍需要調整"


class GateHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "synthetic-case"
        atomic_json(self.root / "assessment-state.json", complete_state())

    def tearDown(self):
        self.temp.cleanup()

    def command(self, script, *args):
        return [sys.executable, str(SKILL_ROOT / "scripts" / script), *map(str, args)]

    def cli(self, script, *args):
        return subprocess.run(
            self.command(script, *args), capture_output=True, text=True, encoding="utf-8",
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        )

    def answer(self, text=ACCEPT, revision=8, by="synthetic-PM"):
        return self.cli("case_state.py", "record-answer", self.root,
                        "--decision-id", "confirm-estimate", "--answer", text,
                        "--decided-by", by, "--expected-revision", revision)

    def bytes(self):
        return (self.root / "assessment-state.json").read_bytes()

    def merge(self, payload, revision, filename="update.json"):
        path = Path(self.temp.name) / filename
        atomic_json(path, payload)
        return self.cli("case_state.py", "merge", self.root, "--input", path,
                        "--expected-revision", revision)

    def test_acceptance_is_atomic_but_is_not_delivery(self):
        before = load(self.root)
        result = self.answer()
        self.assertEqual(0, result.returncode, result.stderr)
        state = load(self.root)
        self.assertEqual(9, state["revision"])
        self.assertEqual("estimate-approved", state["status"])
        self.assertIsNone(state["currentDecision"])
        self.assertEqual(["done"] * 5 + ["current"], [gate["state"] for gate in state["gates"]])
        self.assertEqual(before["workItems"], state["workItems"])
        self.assertEqual(len(before["decisions"]) + 1, len(state["decisions"]))
        self.assertEqual("confirm-estimate", state["decisions"][-1]["effect"])
        self.assertEqual("synthetic-PM", state["decisions"][-1]["decidedBy"])
        self.assertEqual([], validate_state(state)[0])

    def test_explicit_revision_request_returns_to_mapping_without_selecting_a_new_route(self):
        selected = load(self.root)["selectedScenarioId"]
        result = self.answer(REVISE)
        self.assertEqual(0, result.returncode, result.stderr)
        state = load(self.root)
        self.assertEqual("mapping", state["status"])
        self.assertEqual(selected, state["selectedScenarioId"])
        self.assertEqual("revise-estimate", state["decisions"][-1]["effect"])
        self.assertEqual(["done"] * 4 + ["current", "pending"], [gate["state"] for gate in state["gates"]])
        self.assertIsNone(state["currentDecision"])

    def test_unknown_blank_and_other_answers_preserve_last_good(self):
        before = self.bytes()
        for answer in ("", "  ", "maybe", "其他（自行輸入）", "確認並產生交付成果 "):
            with self.subTest(answer=answer):
                result = self.answer(answer)
                self.assertEqual(2, result.returncode)
                self.assertEqual(before, self.bytes())
        result = self.answer(by="  ")
        self.assertEqual(2, result.returncode)
        self.assertEqual(before, self.bytes())

    def test_missing_effects_fail_closed_then_explicit_upgrade_allows_the_known_answer(self):
        state = load(self.root)
        del state["currentDecision"]["choiceDetails"]
        atomic_json(self.root / "assessment-state.json", state)
        before = self.bytes()
        denied = self.answer()
        self.assertEqual(2, denied.returncode)
        self.assertIn("choiceDetails.effect", denied.stderr)
        self.assertEqual(before, self.bytes())
        details = complete_state()["currentDecision"]["choiceDetails"]
        upgraded = self.merge({"currentDecision": {"choiceDetails": details, "requiresHuman": True}}, 8)
        self.assertEqual(0, upgraded.returncode, upgraded.stderr)
        self.assertEqual("estimate-ready", load(self.root)["status"])
        self.assertEqual(0, self.answer(revision=9).returncode)
        self.assertEqual(10, load(self.root)["revision"])

    def test_missing_false_and_string_human_flags_cannot_accept(self):
        for value in (None, False, "true"):
            with self.subTest(value=value):
                state = complete_state()
                if value is None:
                    del state["currentDecision"]["requiresHuman"]
                else:
                    state["currentDecision"]["requiresHuman"] = value
                atomic_json(self.root / "assessment-state.json", state)
                before = self.bytes()
                self.assertTrue(validate_state(state)[0])
                self.assertEqual(2, self.answer().returncode)
                self.assertEqual(before, self.bytes())

    def test_stale_and_retried_answers_do_not_duplicate_or_overwrite(self):
        before = self.bytes()
        self.assertEqual(2, self.answer(revision=7).returncode)
        self.assertEqual(before, self.bytes())
        self.assertEqual(0, self.answer().returncode)
        approved = self.bytes()
        self.assertEqual(2, self.answer(revision=8).returncode)
        self.assertEqual(2, self.answer(revision=9).returncode)
        self.assertEqual(approved, self.bytes())
        self.assertEqual(1, sum(row["decisionId"] == "confirm-estimate" for row in load(self.root)["decisions"]))

    def test_old_approval_cannot_override_a_later_request_to_revise(self):
        state = complete_state()
        state["decisions"].append({"decisionId": "confirm-estimate", "effect": "confirm-estimate", "answer": ACCEPT})
        atomic_json(self.root / "assessment-state.json", state)
        self.assertEqual(0, self.answer(REVISE).returncode)
        rejected = self.bytes()
        for target in ("estimate-approved", "complete"):
            gates = copy.deepcopy(load(self.root)["gates"])
            for gate in gates:
                gate["state"] = "current" if target == "estimate-approved" and gate["number"] == 6 else "done"
            result = self.merge({"status": target, "gates": gates, "currentDecision": None}, 9,
                                filename=target + ".json")
            self.assertEqual(2, result.returncode)
            self.assertIn("最新人天決定", result.stderr)
            self.assertEqual(rejected, self.bytes())

    def test_approved_state_keeps_formal_readiness_and_gate_six_open(self):
        self.assertEqual(0, self.answer().returncode)
        state = load(self.root)
        state["dependencies"] = []
        self.assertTrue(any("dependency behavior" in value for value in validate_state(state)[0]))
        state = load(self.root)
        state["gates"][5]["state"] = "done"
        self.assertTrue(any("PM gate 6" in value for value in validate_state(state)[0]))

    def test_two_simultaneous_answers_have_only_one_successful_commit(self):
        command = self.command("case_state.py", "record-answer", self.root,
                               "--decision-id", "confirm-estimate", "--answer", ACCEPT,
                               "--decided-by", "synthetic-PM", "--expected-revision", 8)
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      text=True, encoding="utf-8", env=environment) for _ in range(2)]
        outputs = [process.communicate(timeout=20) for process in processes]
        self.assertEqual([0, 2], sorted(process.returncode for process in processes), outputs)
        state = load(self.root)
        self.assertEqual(9, state["revision"])
        self.assertEqual("estimate-approved", state["status"])
        self.assertEqual(1, sum(row["decisionId"] == "confirm-estimate" for row in state["decisions"]))

    def test_preview_approved_and_explicit_delivery_outputs_preserve_amounts_and_revisions(self):
        roots = [Path(self.temp.name) / name for name in ("preview", "approved", "delivered")]
        preview = self.cli("generate_outputs.py", self.root, "--output-dir", roots[0], "--json")
        self.assertEqual(0, preview.returncode, preview.stderr)
        self.assertEqual(0, self.answer().returncode)
        approved = self.cli("generate_outputs.py", self.root, "--output-dir", roots[1], "--json")
        self.assertEqual(0, approved.returncode, approved.stderr)
        self.assertEqual("estimate-approved", load(self.root)["status"])
        self.assertIn("人天已核准，待交付", (roots[1] / "assessment-report.html").read_text(encoding="utf-8"))
        self.assertIn("人天待確認（預覽）", (roots[0] / "assessment-report.md").read_text(encoding="utf-8"))

        # Synthetic delivery transition follows actual artifact accessibility checks.
        # A real reader's explanation and usable user entry points remain agent checks.
        for name in ("estimate-external.csv", "assessment-report.md", "assessment-report.html"):
            self.assertGreater((roots[1] / name).stat().st_size, 0)
        gates = copy.deepcopy(load(self.root)["gates"])
        for gate in gates:
            gate["state"] = "done"
        delivery = self.merge({"status": "complete", "gates": gates, "currentDecision": None}, 9)
        self.assertEqual(0, delivery.returncode, delivery.stderr)
        delivered = self.cli("generate_outputs.py", self.root, "--output-dir", roots[2], "--json")
        self.assertEqual(0, delivered.returncode, delivered.stderr)
        reports = [json.loads(run.stdout) for run in (preview, approved, delivered)]
        self.assertEqual([8, 9, 10], [row["stateRevision"] for row in reports])
        self.assertEqual(["estimate-ready", "estimate-approved", "complete"], [row["stateStatus"] for row in reports])
        self.assertIn("交付完成", (roots[2] / "assessment-report.md").read_text(encoding="utf-8"))
        csv_bytes = [(root / "estimate-external.csv").read_bytes() for root in roots]
        self.assertEqual(csv_bytes[0], csv_bytes[1])
        self.assertEqual(csv_bytes[1], csv_bytes[2])
        with (roots[2] / "estimate-external.csv").open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream))
        self.assertEqual(["序號", "系統功能", "功能說明", "開發人天", "測試人天"], rows[0])
        self.assertEqual(9.5, sum(float(row[3]) + float(row[4]) for row in rows[1:]))

    def test_multiple_accept_effects_and_hidden_effects_do_not_choose_for_the_pm(self):
        for label in (REVISE, "hidden-accept"):
            state = complete_state()
            state["currentDecision"]["choiceDetails"][label] = {"effect": "confirm-estimate"}
            atomic_json(self.root / "assessment-state.json", state)
            before = self.bytes()
            self.assertEqual(2, self.answer().returncode)
            self.assertEqual(before, self.bytes())


if __name__ == "__main__":
    unittest.main()


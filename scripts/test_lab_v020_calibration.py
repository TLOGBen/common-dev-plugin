#!/usr/bin/env python3
"""Behavioral gate tests; all generated fixtures stay in a new retained temp root."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
SKILL = Path(os.environ.get("LAB_CALIBRATION_SCRIPTS", ROOT / "plugins/common-lab/skills/lab-strategic-advance/scripts"))
sys.path.insert(0, str(SKILL))
import calibration
import campaign


class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained = Path(tempfile.mkdtemp(prefix="lab020-calibration-tests-"))
        print("RETAINED_FIXTURES=" + str(cls.retained), flush=True)

    def setUp(self):
        self.root = self.retained / self._testMethodName
        self.root.mkdir()
        self.state, self.brief, self.source = [self.root / name for name in ("state.json", "work.md", "raw.txt")]
        self.packet, self.decision = self.root / "packet.json", self.root / "decision.json"
        self.brief.write_text("Synthetic bounded parallel work order; 1 repair, then handback.")
        self.source.write_text("Synthetic raw observation; not a production test.")
        campaign.execute(campaign.parser().parse_args([
            "init", str(self.state), "--objective", "Fixture outcome", "--scope", "Fixture only",
            "--criterion", "C1=Observed fixture behavior"]))
        self.create_packet()

    def create_packet(self, output=None):
        self.packet = output or self.packet
        calibration.prepare(argparse.Namespace(state=str(self.state), brief=str(self.brief),
            source=[str(self.source)], lead="runtime-lead", worker=["worker-api", "worker-ui"],
            expires=(datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(), output=str(self.packet)))
        self.write_decision()

    def write_decision(self, **changes):
        data = {"schema": "lab-calibration-decision/1", "packet_sha256": calibration.digest(self.packet),
                "reviewer_context": "fresh-reviewer", "verdict": "continue",
                "observed_moe": "Criterion remains unmet", "observed_mop": "Fixture preparation",
                "reason": "Bounded fixture action", "next_action": "Observe fixture result",
                "evidence_paths": [str(self.source)]}
        data.update(changes)
        self.decision.write_text(json.dumps(data))

    def patch_packet(self, **changes):
        data = json.loads(self.packet.read_text())
        data.update(changes)
        self.packet.write_text(json.dumps(data))
        self.write_decision()

    def reject(self, phrase, purpose="continue"):
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with self.assertRaisesRegex((ValueError, OSError), phrase):
            calibration.check(self.packet, self.decision, purpose)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_parallel_workers_allowed(self):
        self.assertEqual(calibration.check(self.packet, self.decision)["status"], "CONTROL_PACKET_VALID")

    def test_same_lead_reviewer_rejected(self):
        self.write_decision(reviewer_context="runtime-lead")
        self.reject("not independent")

    def test_executor_reviewer_rejected(self):
        self.write_decision(reviewer_context="worker-api")
        self.reject("not independent")

    def test_lead_executor_rejected(self):
        self.patch_packet(worker_contexts=["runtime-lead"])
        self.reject("implementation worker")

    def test_expired_packet(self):
        self.patch_packet(expires_at=(datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat())
        self.reject("expired")

    def test_future_packet(self):
        self.patch_packet(created_at=(datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat())
        self.reject("future")

    def test_timezone_required(self):
        self.patch_packet(expires_at="2099-01-01T00:00:00")
        self.reject("Timezone required")

    def test_decision_bound_to_packet(self):
        self.write_decision(packet_sha256="0" * 64)
        self.reject("another packet")

    def test_summary_cannot_replace_goal(self):
        self.patch_packet(objective="Quietly replace the original goal")
        self.reject("differs from state")

    def test_changed_source(self):
        self.source.write_text("New raw result")
        self.reject("Evidence changed")

    def test_changed_brief(self):
        self.brief.write_text("Now add a global refactor and unlimited retries")
        self.reject("Evidence changed")

    def test_changed_state(self):
        self.state.write_text(self.state.read_text() + "\n")
        self.reject("Evidence changed")

    def test_no_raw_source(self):
        self.patch_packet(sources=[])
        self.reject("Raw sources required")

    def test_brief_cannot_be_raw_source(self):
        self.patch_packet(sources=[campaign.evidence(self.brief)])
        self.write_decision(evidence_paths=[str(self.brief)])
        self.reject("Raw sources must differ")

    def test_state_cannot_be_raw_source(self):
        self.patch_packet(sources=[campaign.evidence(self.state)])
        self.write_decision(evidence_paths=[str(self.state)])
        self.reject("Raw sources must differ")

    def test_symlink_cannot_disguise_brief(self):
        alias = self.root / "source-alias.txt"
        alias.symlink_to(self.brief)
        self.patch_packet(sources=[campaign.evidence(alias)])
        self.reject("Raw sources must differ")

    def test_hardlink_cannot_disguise_brief(self):
        alias = self.root / "source-alias.txt"
        alias.hardlink_to(self.brief)
        self.patch_packet(sources=[campaign.evidence(alias)])
        self.reject("Raw sources must differ")

    def test_prepare_rejects_source_brief_alias(self):
        output = self.root / "bad-packet.json"
        with self.assertRaisesRegex(ValueError, "Raw sources must differ"):
            calibration.prepare(argparse.Namespace(state=str(self.state), brief=str(self.brief),
                source=[str(self.brief)], lead="lead", worker=[],
                expires=(datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(), output=str(output)))
        self.assertFalse(output.exists())

    def test_malformed_packet_types_rejected(self):
        for value in (None, [], "text"):
            with self.subTest(value=value):
                self.packet.write_text(json.dumps(value))
                self.reject("Unsupported packet")

    def test_malformed_decision_types_rejected(self):
        for value in (None, [], "text"):
            with self.subTest(value=value):
                self.decision.write_text(json.dumps(value))
                self.reject("Unsupported decision")

    def test_nonactive_campaign_rejected(self):
        state = json.loads(self.state.read_text())
        state["status"] = "blocked"
        self.state.write_text(json.dumps(state))
        self.create_packet(self.root / "blocked-packet.json")
        self.reject("Reconcile campaign status")

    def test_invalid_purpose_rejected(self):
        self.reject("Unsupported purpose", "guess")

    def test_citing_only_lead_story_rejected(self):
        self.write_decision(evidence_paths=[str(self.brief)])
        self.reject("not only lead narrative")

    def test_citing_unprovided_source_rejected(self):
        self.write_decision(evidence_paths=[str(self.source), "/invented/evidence"])
        self.reject("inspected packet sources")

    def test_missing_reason(self):
        self.write_decision(reason=" ")
        self.reject("Missing reason")

    def test_replan_does_not_allow_continuation(self):
        self.write_decision(verdict="replan")
        self.reject("does not permit continue")

    def test_hold_does_not_allow_continuation(self):
        self.write_decision(verdict="hold")
        self.reject("does not permit continue")

    def test_activity_only_cannot_complete(self):
        self.write_decision(verdict="ready-to-complete", observed_mop="500 passing commands")
        self.reject("Completion criteria unmet", "complete")

    def accepted_fixture(self, pending=False):
        campaign.execute(campaign.parser().parse_args(["record", str(self.state), "--criterion", "C1",
            "--result", "met", "--evidence", str(self.source), "--note", "Synthetic fixture acceptance"]))
        if pending:
            campaign.execute(campaign.parser().parse_args(["operation", str(self.state), "--key", "fixture-op",
                "--target", "fixture-target", "--outcome", "pending"]))
        self.create_packet(self.root / "accepted-packet.json")
        self.write_decision(verdict="ready-to-complete")

    def test_unresolved_operation_prevents_completion(self):
        self.accepted_fixture(pending=True)
        self.reject("Unresolved operation", "complete")

    def test_complete_requires_ready_verdict(self):
        self.accepted_fixture()
        self.write_decision(verdict="continue")
        self.reject("does not permit complete", "complete")

    def test_complete_with_current_evidence(self):
        self.accepted_fixture()
        self.assertEqual(calibration.check(self.packet, self.decision, "complete")["purpose"], "complete")

    def test_prepare_refuses_existing_packet(self):
        before = self.packet.read_bytes()
        with self.assertRaisesRegex(ValueError, "Refusing to replace"):
            self.create_packet()
        self.assertEqual(before, self.packet.read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)

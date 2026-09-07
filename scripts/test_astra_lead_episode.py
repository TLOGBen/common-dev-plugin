#!/usr/bin/env python3
"""Offline carrier tests. Fake process traces only; never call Codex."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import astra_lead_episode as carrier

LEAD = "11111111-1111-4111-8111-111111111111"
WORKER = "22222222-2222-4222-8222-222222222222"


def control(action="final", requests=None, message="驗收結論"):
    return json.dumps({"action": action, "requests": requests or [], "message": message})


def request(role="implementation", paths=None):
    return {"role": role, "brief": "Lead-selected task and acceptance.",
            "write_paths": ["product.py"] if paths is None else paths}


def trace(message, session=LEAD, usage=None):
    usage = usage or {"input_tokens": 100, "cached_input_tokens": 60, "output_tokens": 10}
    rows = [{"type": "thread.started", "thread_id": session},
            {"type": "item.completed", "item": {"type": "agent_message", "text": message}},
            {"type": "turn.completed", "usage": usage}]
    return {"stdout": ("\n".join(json.dumps(row) for row in rows) + "\n").encode(),
            "stderr": b"offline fake stderr\n", "exit_code": 0, "os_error": None,
            "timed_out": False, "started_utc": "2026-09-06T00:00:00Z",
            "ended_utc": "2026-09-06T00:00:01Z", "wall_seconds": 1.0}


class CarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = Path(tempfile.mkdtemp(prefix="astra-lead-carrier-offline-"))
        print("Retained offline artifacts:", cls.artifacts)

    def setUp(self):
        self.base = self.artifacts / self._testMethodName
        self.base.mkdir()
        self.root = self.base / "fixture"
        self.root.mkdir()
        (self.root / "product.py").write_text("old\n")
        self.out = self.base / "run"
        self.spec = {
            "schema_version": 1, "episode_id": "offline", "case_id": "fixture",
            "arm": "none", "user_prompt": "Fix with the worker; lead accepts.",
            "arm_context": "", "workspace": str(self.root), "sandbox": "workspace-write",
            "role_writes": {"lead": ["acceptance.md"], "implementation": ["product.py"],
                            "verification": [], "scribe": ["memo/"]},
            "workspace_sha256": carrier.inventory(self.root),
            "package_roots": [], "package_sha256": {}, "read_files": {},
            "max_calls": 8, "max_wall_seconds": 60, "call_timeout_seconds": 10,
        }

    def scripted(self, steps):
        def run(command, prompt, timeout):
            self.assertNotIn("--ignore-rules", command)
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)
            if not steps:
                self.fail("Unexpected extra model call")
            result = steps.pop(0)
            return result(command, prompt) if callable(result) else result
        return run

    def test_profiles_resume_and_permission_arguments(self):
        fresh = carrier.command_for(self.spec, "lead", Path("schema.json"))
        self.assertEqual(fresh[fresh.index("-m") + 1], carrier.LEAD_MODEL)
        self.assertNotIn("--ephemeral", fresh)
        resumed = carrier.command_for(self.spec, "lead", Path("schema.json"), LEAD)
        self.assertEqual(resumed[-3:], ["resume", LEAD, "-"])
        self.assertNotIn("--last", resumed)
        worker = carrier.command_for(self.spec, "implementation", Path("schema.json"))
        self.assertEqual(worker[worker.index("-m") + 1], carrier.WORKER_MODEL)
        self.assertIn("--ephemeral", worker)
        for command in (fresh, resumed, worker):
            self.assertIn("model_reasoning_effort=high", command)
            self.assertEqual(command[command.index("-s") + 1], "workspace-write")

    def test_control_bounds_and_no_mandatory_dispatch(self):
        for action in ("continue", "final", "human"):
            self.assertEqual(carrier.control_message(control(action), self.spec["role_writes"])["action"], action)
        for bad in (request("lead"), request(paths=["../product.py"]),
                    request(paths=["ungranted.py"]), request("invented")):
            with self.assertRaises(ValueError):
                carrier.control_message(control("dispatch", [bad]), self.spec["role_writes"])
        with self.assertRaises(ValueError):
            carrier.control_message(control("final", [request()]), self.spec["role_writes"])
        for bad_path in ("../x", "/tmp/x", "./x", "x\\y", "", 3):
            with self.assertRaises(ValueError):
                carrier.safe_relative(bad_path)

    def test_zero_write_roles_and_narrowed_requests_are_actually_read_only(self):
        for role, writes in (("verification", None), ("implementation", [])):
            command = carrier.command_for(self.spec, role, Path("schema.json"), writes=writes)
            self.assertEqual(command[command.index("-s") + 1], "read-only")
        self.spec["sandbox"] = "read-only"
        with self.assertRaisesRegex(ValueError, "parent read-only"):
            carrier.validate_spec(self.spec, self.out)
        self.spec["role_writes"] = {role: [] for role in self.spec["role_writes"]}
        carrier.validate_spec(self.spec, self.out)
        self.assertIn("read-only", carrier.command_for(self.spec, "lead", Path("schema.json")))

    def test_fresh_and_cumulative_resume_usage_are_not_double_counted(self):
        parsed = carrier.parse_events(trace("x")["stdout"].decode())
        usage, _ = carrier.usage_for(parsed, None, None, False)
        self.assertEqual(usage["total_tokens"], 110)
        self.assertIsNone(carrier.usage_for(parsed, None, None, True)[0])
        before = {"total_token_usage": {"input_tokens": 1000, "cached_input_tokens": 800,
                                       "output_tokens": 100, "reasoning_output_tokens": 20}}
        after = {"total_token_usage": {"input_tokens": 1400, "cached_input_tokens": 1100,
                                      "output_tokens": 180, "reasoning_output_tokens": 30}}
        usage, basis = carrier.usage_for(parsed, before, after, True)
        self.assertEqual(usage["total_tokens"], 480)
        self.assertEqual(usage["reasoning_output_tokens"], 10)
        self.assertIn("delta", basis)
        self.assertIsNone(carrier.usage_for(parsed, after, before, True)[0])

    def test_exact_session_token_read(self):
        store = self.base / "sessions"
        store.mkdir()
        (store / ("rollout-" + LEAD + ".jsonl")).write_text(json.dumps({
            "type": "event_msg", "payload": {"type": "token_count",
            "info": {"total_token_usage": {"input_tokens": 22, "cached_input_tokens": 10,
                                         "output_tokens": 3}}}}))
        (store / ("rollout-" + WORKER + ".jsonl")).write_text("unrelated invalid bytes")
        found = carrier.session_tokens(store, LEAD)
        self.assertEqual(found["total_token_usage"]["input_tokens"], 22)
        self.assertIsNone(carrier.session_tokens(store, "33333333-3333-4333-8333-333333333333"))
        self.assertIsNone(carrier.session_tokens(store, "../*"))
        with self.assertRaises(ValueError):
            carrier.command_for(self.spec, "lead", Path("schema.json"), "-" * 36)

    def test_complete_raw_usage_rows_preserve_optional_fields_and_unknowns(self):
        usage = {"input_tokens": 100, "cached_input_tokens": 60, "output_tokens": 10,
                 "cache_write_input_tokens": 12, "reasoning_output_tokens": 4}
        result = carrier.run_episode(self.spec, self.out, self.scripted([trace(control(), usage=usage)]))
        row = result["calls"][0]
        self.assertEqual(row["raw_turn_completed_usage"], [usage])
        self.assertEqual(row["usage"]["cache_write_input_tokens"], 12)
        self.assertEqual(row["usage"]["reasoning_output_tokens"], 4)
        self.assertEqual(row["usage"]["total_tokens"], 110)
        parsed = carrier.parse_events(trace("x")["stdout"].decode())
        parsed["turn_completed_usage"] = carrier.turn_completed_usage_rows(trace("x")["stdout"].decode())
        self.assertNotIn("cache_write_input_tokens", carrier.usage_for(parsed, None, None, False)[0])
        doubled = trace("x", usage=usage)["stdout"].decode() + trace("x")["stdout"].decode()
        self.assertEqual(len(carrier.turn_completed_usage_rows(doubled)), 2)

    def test_real_transport_sequence_with_fake_processes_and_artifact(self):
        def worker(command, prompt):
            self.assertIn("Lead-selected task", prompt)
            (self.root / "product.py").write_text("fixed\n")
            return trace("Changed product.py; evidence in file.", WORKER)
        def accept(command, prompt):
            self.assertEqual(command[-3:], ["resume", LEAD, "-"])
            self.assertIn("Changed product.py", prompt)
            self.assertEqual((self.root / "product.py").read_text(), "fixed\n")
            (self.root / "acceptance.md").write_text("Accepted actual artifact\n")
            return trace(control())
        rows = [trace(control("dispatch", [request()])), worker, accept]
        result = carrier.run_episode(self.spec, self.out, self.scripted(rows))
        self.assertEqual(result["status"], "lead_finished")
        self.assertEqual(result["actual_cli_calls"], 3)
        self.assertTrue(result["implementation_dispatched"])
        self.assertTrue(result["lead_returned_after_worker"])
        self.assertIsNone(result["semantic_acceptance"])
        self.assertEqual(result["totals_by_role"]["lead"]["unknown_usage_calls"], 1)
        for folder in (self.out / "calls").iterdir():
            self.assertTrue((folder / "stdout.jsonl").is_file())
            self.assertEqual((folder / "stderr.txt").read_bytes(), b"offline fake stderr\n")
            self.assertTrue((folder / "fixture-after.zip").is_file())
            self.assertTrue((folder / "result.json").is_file())

    def test_continue_before_dispatch_is_allowed(self):
        result = carrier.run_episode(self.spec, self.out, self.scripted([
            trace(control("continue", message="Observed local evidence")),
            trace(control("human", message="One missing genuine choice")),
        ]))
        self.assertEqual(result["status"], "needs_human")
        self.assertFalse(result["implementation_dispatched"])
        self.assertEqual(result["actual_cli_calls"], 2)

    def test_exact_raw_receipt_grants_reach_lead_and_later_role(self):
        expected = {}
        def inspect_grants(prompt, folder):
            actual = {str(folder / name): carrier.sha((folder / name).read_bytes())
                      for name in ("prompt.txt", "stdout.jsonl", "stderr.txt", "result.json")}
            self.assertIn("READ-ONLY DELIVERY GRANTS", prompt)
            for path, digest in actual.items():
                self.assertIn(json.dumps(path), prompt)
                self.assertIn(digest, prompt)
            self.assertIn("do not modify them or read other controller files", prompt)
            self.assertNotIn(str(self.out / "spec.json"), prompt)
            self.assertNotIn(str(self.out / "summary.json"), prompt)
            return actual
        def lead_after_worker(command, prompt):
            expected.update(inspect_grants(prompt, self.out / "calls/002-implementation"))
            return trace(control("dispatch", [request("verification", [])]))
        def verifier(command, prompt):
            self.assertEqual(command[command.index("-s") + 1], "read-only")
            self.assertEqual(inspect_grants(prompt, self.out / "calls/002-implementation"), expected)
            self.assertIn("Lead-selected task", (self.out / "calls/002-implementation/prompt.txt").read_text())
            return trace("Independent observed evidence, not acceptance by the carrier.", WORKER)
        result = carrier.run_episode(self.spec, self.out, self.scripted([
            trace(control("dispatch", [request()])), trace("Implementation claims", WORKER),
            lead_after_worker, verifier, trace(control()),
        ]))
        self.assertEqual(result["status"], "lead_finished")
        self.assertEqual(result["calls"][2]["read_only_delivered_files"], expected)
        self.assertEqual(result["calls"][3]["read_only_delivered_files"], expected)
        self.assertEqual(len(result["calls"][4]["read_only_delivered_files"]), 8)

    def test_role_batch_is_serial_and_budget_censored_not_completed(self):
        self.spec["max_calls"] = 3
        def verifier(command, prompt):
            self.assertEqual(command[command.index("-s") + 1], "read-only")
            self.assertIn(str(self.out / "calls/002-implementation/prompt.txt"), prompt)
            return trace("Verified", WORKER)
        result = carrier.run_episode(self.spec, self.out, self.scripted([
            trace(control("dispatch", [request(), request("verification", [])])),
            trace("Implemented", WORKER), verifier,
        ]))
        self.assertEqual(result["status"], "budget_censored")
        self.assertEqual([r["role"] for r in result["calls"]],
                         ["lead", "implementation", "verification"])
        self.assertFalse(result["lead_returned_after_worker"])
        self.assertEqual(result["unexecuted_requests"][0]["role"], "lead")

    def test_out_of_scope_write_stops_without_restoring_evidence(self):
        def bad(command, prompt):
            (self.root / "product.py").write_text("lead must not edit this\n")
            return trace(control())
        result = carrier.run_episode(self.spec, self.out, self.scripted([bad]))
        self.assertEqual(result["status"], "scope_violation")
        self.assertEqual(result["actual_cli_calls"], 1)
        self.assertIn("lead must not", (self.root / "product.py").read_text())
        self.assertEqual(result["calls"][0]["scope_violations"], ["product.py"])

    def test_symlink_violation_still_preserves_result(self):
        def bad(command, prompt):
            (self.root / "bad").symlink_to(self.root / "product.py")
            return trace(control())
        result = carrier.run_episode(self.spec, self.out, self.scripted([bad]))
        self.assertEqual(result["status"], "scope_violation")
        self.assertIn("Symlink", result["calls"][0]["observation_error"])

    def test_invalid_control_never_auto_retries(self):
        result = carrier.run_episode(self.spec, self.out, self.scripted([trace("not json")]))
        self.assertEqual(result["status"], "protocol_error")
        self.assertEqual(result["actual_cli_calls"], 1)

    def test_resume_session_mismatch_stops(self):
        result = carrier.run_episode(self.spec, self.out, self.scripted([
            trace(control("continue")), trace(control(), WORKER),
        ]))
        self.assertEqual(result["status"], "session_mismatch")
        self.assertEqual(result["actual_cli_calls"], 2)

    def test_timeout_preserves_raw_and_does_not_restart_unknown_work(self):
        failed = trace("possibly did something")
        failed["timed_out"], failed["exit_code"] = True, -15
        result = carrier.run_episode(self.spec, self.out, self.scripted([failed]))
        self.assertEqual(result["status"], "timeout_unknown")
        self.assertEqual(result["actual_cli_calls"], 1)
        self.assertTrue((self.out / "calls/001-lead/stdout.jsonl").is_file())

    def test_generated_package_and_frozen_input_guards(self):
        package = self.base / "package"
        package.mkdir()
        self.spec["package_roots"] = [str(package)]
        self.spec["package_sha256"] = {str(package): carrier.inventory(package)}
        with self.assertRaisesRegex(ValueError, "generated Codex"):
            carrier.validate_spec(self.spec, self.out)
        (package / ".codex-plugin").mkdir()
        (package / ".codex-plugin/plugin.json").write_text('{"version":"test"}')
        self.spec["package_sha256"] = {str(package): carrier.inventory(package)}
        carrier.validate_spec(self.spec, self.out)
        (self.root / "product.py").write_text("drift")
        with self.assertRaisesRegex(ValueError, "Fixture differs"):
            carrier.validate_spec(self.spec, self.out)

    def test_existing_output_is_never_overwritten(self):
        self.out.mkdir()
        (self.out / "keep.txt").write_text("preserve")
        with self.assertRaisesRegex(ValueError, "must not exist"):
            carrier.validate_spec(self.spec, self.out)
        self.assertEqual((self.out / "keep.txt").read_text(), "preserve")

    def test_preflight_default_cannot_call_model(self):
        config = self.base / "spec.json"
        config.write_text(json.dumps(self.spec))
        with patch("sys.argv", ["carrier", "--spec", str(config), "--out", str(self.out)]):
            with patch.object(carrier, "run_episode", side_effect=AssertionError("model path")):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    carrier.main()
        self.assertIn("PREFLIGHT_ONLY_NO_MODEL_CALLS", output.getvalue())
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()

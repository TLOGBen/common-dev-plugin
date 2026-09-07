#!/usr/bin/env python3
"""Bounded synthetic approval-validity diagnosis; never edits product source."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "docs/experiments/estimate-lab/fixed-validation/synthetic-e3/assessment-state.json"
PACKAGE = ROOT / "experiments/estimate-lab-v0.1.2/plugins/estimate-lab"
RUNTIME = PACKAGE / "skills/lab-estimate/scripts"
TEMP = Path("/tmp/estimate-approval-validity-012-a")
ARTIFACTS = Path(__file__).resolve().parent / "artifacts"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(path):
    return {str(p.relative_to(path)): sha(p) for p in sorted(path.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}

def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    baseline = json.loads(SOURCE.read_text())
    assert baseline["revision"] == 9 and baseline["status"] == "estimate-approved"
    assert json.loads((PACKAGE / ".codex-plugin/plugin.json").read_text())["version"] == "0.1.2"
    assert not TEMP.exists() and not ARTIFACTS.exists(), "TARGET_MISMATCH: preserve previous probe"
    before = {"baseline": sha(SOURCE), "package": inventory(PACKAGE)}
    preflight = {
        "verdict": "TARGET_MATCH", "original_baseline": str(SOURCE.resolve()),
        "baseline_sha256": before["baseline"], "runtime": str(RUNTIME.resolve()),
        "new_temporary_root": str(TEMP), "new_artifacts": str(ARTIFACTS),
        "existing_destination_items": 0,
        "owned_targets": ["baseline-rev9.json", "direct-workitems", "scope-change", "scenario-change"],
        "scope": "Only fresh synthetic state copies, inputs, generated outputs, command receipts and retained snapshots.",
        "recovery": "Original rev9 and immutable runtime retained; no deletion or original fixture/source mutation."
    }
    print(json.dumps(preflight, ensure_ascii=False))
    if not args.run:
        return
    started, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
    TEMP.mkdir()
    ARTIFACTS.mkdir()
    (ARTIFACTS / "baseline-rev9.json").write_bytes(SOURCE.read_bytes())
    steps, observations = [], []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    def call(command, expected=0):
        start = time.monotonic()
        p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
        step = {"command": command, "exit_code": p.returncode, "stdout": p.stdout,
                "stderr": p.stderr, "elapsed_seconds": round(time.monotonic()-start, 6)}
        steps.append(step)
        assert p.returncode == expected, step
        return step
    def copy_case(name):
        path = TEMP / name
        path.mkdir()
        (path / "assessment-state.json").write_bytes(SOURCE.read_bytes())
        return path
    def command(verb, case, *extra):
        return [sys.executable, "-B", str(RUNTIME / "case_state.py"), verb, str(case), *extra]
    def run_update(verb, case, update, revision, collection=None, expected=0):
        input_path = case / ("input-" + str(revision) + ".json")
        write_new(input_path, update)
        extra = ["--input", str(input_path), "--expected-revision", str(revision)]
        if collection:
            extra += ["--collection", collection]
        return call(command(verb, case, *extra), expected)
    def observe(name, case):
        call(command("validate", case))
        output = case / "outputs"
        call([sys.executable, "-B", str(RUNTIME / "generate_outputs.py"), str(case), "--output-dir", str(output), "--json"])
        state = json.loads((case / "assessment-state.json").read_text())
        approvals = [d for d in state["decisions"] if d.get("decisionId") == "confirm-estimate"]
        old_approvals = [d for d in baseline["decisions"] if d.get("decisionId") == "confirm-estimate"]
        html = (output / "assessment-report.html").read_text()
        obs = {"case": name, "revision": state["revision"], "status": state["status"],
               "selectedScenarioId": state["selectedScenarioId"], "outcome": state["outcome"],
               "currentDecision": state["currentDecision"], "approval_records_unchanged": approvals == old_approvals,
               "approval_ids": [d["id"] for d in approvals], "html_claims_approved": "人天已核准，待交付" in html,
               "scope_visible_in_html": state["outcome"]["responsibilityBoundary"] in html,
               "selected_scenario_visible_in_html": next(s["name"] for s in state["scenarios"] if s["id"] == state["selectedScenarioId"]) in html,
               "gate_states": [g["state"] for g in state["gates"]], "state_sha256": sha(case / "assessment-state.json"),
               "files": inventory(case)}
        observations.append(obs)
        print(json.dumps(obs, ensure_ascii=False))
    try:
        control = copy_case("direct-workitems")
        changed = copy.deepcopy(baseline["workItems"])
        changed[0]["unitDays"]["high"] += 1
        changed[0]["effortSplit"]["development"]["high"] += 1
        control_step = run_update("merge", control, {"workItems": changed}, 9, expected=2)
        assert sha(control / "assessment-state.json") == before["baseline"]
        observations.append({"case": "direct-workitems", "mutation_rejected": True, "last_good_unchanged": True,
                             "error": control_step["stderr"], "files": inventory(control)})
        scope = copy_case("scope-change")
        run_update("merge", scope, {"outcome": {"responsibilityBoundary": "我方負責應用改造、正式環境部署與完整 UAT；客戶僅提供存取權限"}}, 9)
        observe("scope-change", scope)
        scenario = copy_case("scenario-change")
        run_update("append", scenario, {"id": "scenario-b", "name": "不保留既有網址的重建",
                   "summary": "重新設計功能入口，不承諾保留既有網址與回應契約"}, 9, collection="scenarios")
        run_update("append", scenario, {"id": "synthetic-select-scenario-b-11", "decisionId": "select-scenario",
                   "answer": "改選不保留既有網址的重建", "selectedScenarioId": "scenario-b",
                   "decidedBy": "synthetic-fixture-only", "recordedAt": "2026-09-06T06:00:00+00:00"}, 10, collection="decisions")
        run_update("merge", scenario, {"selectedScenarioId": "scenario-b"}, 11)
        observe("scenario-change", scenario)
        assert all(o["approval_records_unchanged"] and o["html_claims_approved"] for o in observations[1:])
        status = "REPRODUCED"
    finally:
        after = {"baseline": sha(SOURCE), "package": inventory(PACKAGE)}
        result = {"status": locals().get("status", "INCOMPLETE"), "hunt_id": "HUNT-2026-001",
                  "started_utc": started, "ended_utc": datetime.now(timezone.utc).isoformat(),
                  "elapsed_seconds": round(time.monotonic()-clock, 6), "preflight": preflight,
                  "steps": steps, "observations": observations, "before": before, "after": after,
                  "original_and_runtime_unchanged": before == after, "temporary_inventory": inventory(TEMP),
                  "model_calls": 0, "inference_tokens": 0, "author_actual_tokens": None,
                  "actual_cost_usd": None, "limits": "Synthetic local CLI/generated-file evidence only; no real PM, product source changes or browser QA."}
        write_new(ARTIFACTS / "result.json", result)
        print(json.dumps({"status": result["status"], "receipt": str(ARTIFACTS / "result.json"),
                          "original_and_runtime_unchanged": before == after}, ensure_ascii=False))
        assert before == after

if __name__ == "__main__":
    main()


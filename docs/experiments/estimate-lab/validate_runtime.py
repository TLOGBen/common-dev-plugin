#!/usr/bin/env python3
"""Run the inherited suite and a real synthetic Gate 5 CLI without deleting fixtures."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--stage", choices=("baseline", "fixed"), required=True)
    args = parser.parse_args()
    root, out = args.skill_root.resolve(), args.out.resolve()
    if out.exists():
        raise SystemExit("Refusing to overwrite validation run: " + str(out))
    started = datetime.now(timezone.utc).isoformat()
    out.mkdir(parents=True)
    suite_root = out / "retained-suite-fixtures"
    suite_root.mkdir()
    original_temporary = tempfile.TemporaryDirectory

    class RetainedTemporaryDirectory(original_temporary):
        def __init__(self, *values, **options):
            options["dir"] = str(suite_root)
            super().__init__(*values, **options)
            self._finalizer.detach()

        def cleanup(self):
            pass

    tempfile.TemporaryDirectory = RetainedTemporaryDirectory
    sys.path.insert(0, str(root / "tests"))
    suite = unittest.defaultTestLoader.discover(str(root / "tests"))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    (out / "suite.txt").write_text(stream.getvalue(), encoding="utf-8")
    from helpers import complete_state
    from case_state import atomic_json

    case = out / "synthetic-e3"
    state = complete_state()
    state["currentDecision"]["choiceDetails"] = {
        "確認並產生交付成果": {"effect": "confirm-estimate"},
        "工作範圍需要調整": {"effect": "revise-estimate"},
    }
    atomic_json(case / "assessment-state.json", state)
    initial_bytes = (case / "assessment-state.json").read_bytes()
    calls = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

    def call(script_name, *values):
        command = [sys.executable, str(root / "scripts" / script_name), *map(str, values)]
        run = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", env=environment)
        calls.append({"argv": command, "returncode": run.returncode, "stdout": run.stdout, "stderr": run.stderr})
        return run

    def persisted():
        return json.loads((case / "assessment-state.json").read_text(encoding="utf-8"))

    initial = call("case_state.py", "validate", case)
    preview = call("generate_outputs.py", case, "--output-dir", out / "preview", "--json")
    approval = call("case_state.py", "record-answer", case, "--decision-id", "confirm-estimate",
                    "--answer", "確認並產生交付成果", "--decided-by", "synthetic-fixture",
                    "--expected-revision", 8)
    observations = {"initialValidation": initial.returncode, "previewGeneration": preview.returncode,
                    "approvalReturncode": approval.returncode,
                    "afterApprovalStatus": persisted()["status"],
                    "afterApprovalRevision": persisted()["revision"]}
    if args.stage == "baseline":
        observations["lastGoodPreserved"] = (case / "assessment-state.json").read_bytes() == initial_bytes
        e3_ok = approval.returncode == 2 and observations["lastGoodPreserved"]
    else:
        approved = persisted()
        retry = call("case_state.py", "record-answer", case, "--decision-id", "confirm-estimate",
                     "--answer", "確認並產生交付成果", "--decided-by", "synthetic-fixture",
                     "--expected-revision", 8)
        after_retry = persisted()
        accepted = call("generate_outputs.py", case, "--output-dir", out / "accepted-awaiting-delivery", "--json")
        report = json.loads(accepted.stdout) if accepted.returncode == 0 else {}
        preview_report = json.loads(preview.stdout) if preview.returncode == 0 else {}
        observations.update({
            "approvalIsNotDelivery": approved["status"] == "estimate-approved" and approved["gates"][5]["state"] == "current",
            "retryReturncode": retry.returncode,
            "retryDidNotDuplicate": after_retry == approved,
            "previewStateRevision": preview_report.get("stateRevision"),
            "acceptedStateRevision": report.get("stateRevision"),
            "acceptedStateStatus": report.get("stateStatus"),
        })
        preview_csv = (out / "preview/estimate-external.csv").read_bytes()
        accepted_csv = (out / "accepted-awaiting-delivery/estimate-external.csv").read_bytes() if accepted.returncode == 0 else b""
        observations["externalAmountsUnchanged"] = preview_csv == accepted_csv
        e3_ok = (approval.returncode == 0 and approved["revision"] == 9
                 and observations["approvalIsNotDelivery"] and retry.returncode == 2
                 and observations["retryDidNotDuplicate"] and report.get("stateRevision") == 9
                 and report.get("stateStatus") == "estimate-approved"
                 and observations["externalAmountsUnchanged"])
    report = {"stage": args.stage, "startedAt": started, "finishedAt": datetime.now(timezone.utc).isoformat(),
              "source": str(root), "sourceHashes": {
                  str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts},
              "suite": {"ran": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                        "successful": result.wasSuccessful()},
              "e3": observations, "expectedE3OutcomeObserved": e3_ok, "calls": calls,
              "fixtureLifecycle": "retained; no recursive cleanup performed",
              "modelTokenUsage": None, "modelCost": None}
    (out / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("stage", "suite", "e3", "expectedE3OutcomeObserved")}, ensure_ascii=False))
    return 0 if result.wasSuccessful() and e3_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())


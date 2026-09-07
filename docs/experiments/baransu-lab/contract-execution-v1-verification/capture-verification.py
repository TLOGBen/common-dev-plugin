#!/usr/bin/env python3
"""Capture fixed local checks; do not edit either implementation fixture."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
SUMMARY = ROOT / "docs/experiments/baransu-lab/runs/luna-contract-execution-v1/summary.json"
ORACLE = ROOT / "scripts/verify_normalize_tag.mjs"
ARMS = {
    "A": Path("/tmp/common-lab-exec-normalize-tag-dwh82u2v"),
    "B": Path("/tmp/common-lab-exec-normalize-tag-zukrn7al"),
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def snapshot(root):
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"Unexpected symlink: {path}")
        if path.is_file():
            result[str(path.relative_to(root))] = digest(path.read_bytes())
    return result

def now():
    return datetime.now(timezone.utc).isoformat()

def capture(name, command, cwd):
    started = now()
    tick = time.perf_counter()
    result = subprocess.run(command, cwd=cwd, capture_output=True, timeout=60)
    elapsed = time.perf_counter() - tick
    for stream in ("stdout", "stderr"):
        with (OUT / f"{name}.{stream}.txt").open("xb") as dest:
            dest.write(getattr(result, stream))
    return {
        "command": command, "cwd": str(cwd),
        "started_utc": started, "ended_utc": now(),
        "wall_seconds": round(elapsed, 6), "exit_code": result.returncode,
        "stdout_path": f"{name}.stdout.txt",
        "stdout_sha256": digest(result.stdout),
        "stderr_path": f"{name}.stderr.txt",
        "stderr_sha256": digest(result.stderr),
    }

if (OUT / "receipt.json").exists():
    raise SystemExit("Existing receipt preserved; choose a new execution directory.")
for arm in ARMS:
    for check in ("oracle", "suite"):
        for stream in ("stdout", "stderr"):
            if (OUT / f"{arm}-{check}.{stream}.txt").exists():
                raise SystemExit("Existing raw output preserved; no overwrite.")
summary = json.loads(SUMMARY.read_text())
expected = {
    item["arm"]: item["artifact_observations"]["fixture_after_sha256"]
    for item in summary["results"]
}
before = {arm: snapshot(root) for arm, root in ARMS.items()}
if before != expected:
    raise SystemExit("TARGET_DRIFT: no checks executed.")
started = now()
tick = time.perf_counter()
node = shutil.which("node")
if not node:
    raise SystemExit("NODE_RUNTIME_UNAVAILABLE")
receipt = {
    "kind": "independent_read_only_execution_verification",
    "started_utc": started, "node_executable": node,
    "node_version": subprocess.check_output([node, "--version"], text=True).strip(),
    "node_test_context": os.environ.get("NODE_TEST_CONTEXT"),
    "actor_model_calls": 0, "verifier_model_calls": 0,
    "runner_sha256": digest(Path(__file__).read_bytes()),
    "oracle_sha256": digest(ORACLE.read_bytes()),
    "input_summary_sha256": digest(SUMMARY.read_bytes()),
    "fixture_before_sha256": before,
    "matches_actor_completion_hashes": True,
    "checks": [],
    "scope": "Synthetic data; real local node execution. Not full seal, human acceptance, or business completion.",
    "not_executed": ["mutation probes", "stable sealed marker", "global telemetry", "stop hook", "external writes"],
}
for arm, root in ARMS.items():
    for name, command in (
        ("oracle", [node, str(ORACLE), str(root / "src/normalize-tag.mjs")]),
        ("suite", [node, "--test", "tests/normalize-tag.test.mjs"]),
    ):
        check = capture(f"{arm}-{name}", command, root)
        check.update({"arm": arm, "check": name})
        if name == "oracle":
            observed = json.loads((OUT / check["stdout_path"]).read_text())
            check["passed"] = observed["passed"]
            check["total"] = observed["total"]
            check["reported_mutation"] = observed["mutation"]
        receipt["checks"].append(check)
after = {arm: snapshot(root) for arm, root in ARMS.items()}
receipt.update({
    "ended_utc": now(), "wall_seconds": round(time.perf_counter() - tick, 6),
    "fixture_after_sha256": after,
    "fixtures_unchanged": before == after,
    "all_commands_passed": all(item["exit_code"] == 0 for item in receipt["checks"]),
})
with (OUT / "receipt.json").open("x", encoding="utf-8") as dest:
    json.dump(receipt, dest, ensure_ascii=False, indent=2)
    dest.write("\n")
print(json.dumps(receipt, ensure_ascii=False, indent=2))


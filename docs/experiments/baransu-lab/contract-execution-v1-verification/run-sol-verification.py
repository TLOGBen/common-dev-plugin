#!/usr/bin/env python3
"""Execute the two approved fresh CLI calls; preserve raw evidence, never grade."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from common_lab_ab import parse_events, save

OUT = ROOT / "docs/experiments/baransu-lab/runs/sol-contract-verification-v1"
TIMEOUT = 600
TOKEN_KEYS = ("input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens", "total_tokens")

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def file_sha(path):
    return sha(path.read_bytes())

def inventory(root):
    result = {}
    if not root.exists():
        return {"__ROOT_MISSING__": True}
    for path in sorted(root.rglob("*")):
        name = str(path.relative_to(root))
        if path.is_symlink():
            result[name] = {"type": "symlink", "target": os.readlink(path)}
        elif path.is_file():
            result[name] = {"type": "file", "bytes": path.stat().st_size, "sha256": file_sha(path)}
        elif path.is_dir():
            result[name + "/"] = {"type": "directory"}
    return result

def changed(before, after):
    return sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))

def target_hashes(path, expected):
    return {name: file_sha(path / name) if (path / name).is_file() and not (path / name).is_symlink() else None
            for name in expected}

def metadata(raw):
    usages, model_metadata, starts, completed = [], [], 0, 0
    for line_number, line in enumerate(raw.splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        starts += event.get("type") == "turn.started"
        completed += event.get("type") == "turn.completed"
        def walk(value, pointer):
            if isinstance(value, dict):
                for key, item in value.items():
                    here = pointer + "/" + key
                    if key == "usage":
                        usages.append({"line": line_number, "json_pointer": here, "value": item})
                    if key in ("model", "model_id", "requested_model", "resolved_model"):
                        model_metadata.append({"line": line_number, "json_pointer": here, "value": item})
                    walk(item, here)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    walk(item, pointer + "/" + str(index))
        walk(event, "")
    return {"usage_events_complete": usages, "model_metadata_observed": model_metadata,
            "observed_turn_started_count": starts, "observed_turn_completed_count": completed,
            "provider_request_count": None,
            "provider_request_count_basis": "Internal provider requests are not exposed by this CLI event stream; CLI invocations and observed turn events are recorded separately."}

plan = json.loads((PREP / "dispatch-plan.json").read_text())
approved = json.loads((PREP / "payload-review-receipt.json").read_text())
assert file_sha(PREP / "dispatch-plan.json") == approved["dispatch_plan_sha256"]
for arm, item in plan["arms"].items():
    assert file_sha(Path(item["stdin_prompt"])) == approved["arms"][arm]["prompt_sha256"]
    assert file_sha(Path(item["payload"])) == approved["arms"][arm]["payload_sha256"]
    assert item["command"][item["command"].index("-m") + 1] == "gpt-5.6-sol"
    assert "model_reasoning_effort=high" in item["command"]
    for relative, digest in item["frozen_resource_sha256"].items():
        assert file_sha(Path(item["frozen_resource_root"]) / relative) == digest
    identity = item["target_identity"]
    for key in ("disposable_target", "original_read_only_root"):
        assert target_hashes(Path(identity[key]), identity["artifact_sha256"]) == identity["artifact_sha256"]
    assert not list((Path(item["cwd"]) / "scratch").iterdir())
OUT.mkdir(parents=True, exist_ok=False)
started, tick = utc(), time.monotonic()
initial_prep = inventory(PREP)
original_before = {arm: inventory(Path(item["target_identity"]["original_read_only_root"]))
                   for arm, item in plan["arms"].items()}
version = subprocess.run(["codex", "--version"], capture_output=True, text=True)
save(OUT / "run-manifest.json", {
    "run_id": OUT.name, "started_utc": started, "planned_calls": 2, "arm_order": ["A", "B"],
    "model": "gpt-5.6-sol", "effort": "high", "timeout_per_arm_seconds": TIMEOUT,
    "cli_version_stdout": version.stdout, "cli_version_stderr": version.stderr, "cli_version_exit_code": version.returncode,
    "approved_plan_sha256": file_sha(PREP / "dispatch-plan.json"),
    "approved_payload_receipt_sha256": file_sha(PREP / "payload-review-receipt.json"),
    "carrier_sha256": file_sha(Path(__file__)),
    "parser_path": str(ROOT / "scripts/common_lab_ab.py"), "parser_sha256": file_sha(ROOT / "scripts/common_lab_ab.py"),
    "plan": plan, "preparation_before": initial_prep, "original_fixtures_before": original_before,
    "quality_acceptance": None, "complete_seal": False,
    "limits": "Role-local synthetic artifact verification; exact approved CLI commands, no model fallback or automatic quality verdict."
})
results, stop_reason = [], None
for arm in ("A", "B"):
    item = plan["arms"][arm]
    identity = item["target_identity"]
    target = Path(identity["disposable_target"])
    if target_hashes(target, identity["artifact_sha256"]) != identity["artifact_sha256"]:
        stop_reason = "TARGET_DRIFT_BEFORE_" + arm
        break
    prep_before = inventory(PREP)
    prompt = Path(item["stdin_prompt"]).read_bytes()
    with (OUT / f"{arm}.prompt.txt").open("xb") as dest:
        dest.write(prompt)
    stamp, call_tick = utc(), time.monotonic()
    timed_out, os_error, launched, returncode, pid = False, None, False, None, None
    print(json.dumps({"arm": arm, "state": "starting", "requested_model": "gpt-5.6-sol", "effort": "high", "utc": stamp}), flush=True)
    raw_path, error_path = OUT / f"{arm}.raw.jsonl", OUT / f"{arm}.stderr.txt"
    with raw_path.open("xb") as raw, error_path.open("xb") as err:
        try:
            process = subprocess.Popen(item["command"], cwd=item["cwd"], stdin=subprocess.PIPE,
                                       stdout=raw, stderr=err, start_new_session=True)
            launched, pid = True, process.pid
            save(OUT / f"{arm}.request.json", {
                "command": item["command"], "cwd": item["cwd"], "started_utc": stamp,
                "pid": pid, "prompt_sha256": sha(prompt),
                "requested_model": "gpt-5.6-sol", "requested_effort": "high",
                "timeout_seconds": TIMEOUT, "fallback": False,
            })
            try:
                process.stdin.write(prompt)
                process.stdin.close()
            except BrokenPipeError:
                pass
            try:
                process.wait(timeout=TIMEOUT)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
            returncode = process.returncode
        except OSError as exc:
            os_error = {"type": type(exc).__name__, "message": str(exc)}
    raw_bytes = raw_path.read_bytes()
    parsed = parse_events(raw_bytes.decode("utf-8", errors="replace"))
    usage_metadata = metadata(raw_bytes.decode("utf-8", errors="replace"))
    prep_after = inventory(PREP)
    all_changes = changed(prep_before, prep_after)
    own_scratch_prefix = "dispatch/" + arm + "/scratch/"
    source_relative = "dispatch/" + arm + "/target/src/normalize-tag.mjs"
    outside = [name for name in all_changes if name != source_relative and not name.startswith(own_scratch_prefix)]
    final_target = target_hashes(target, identity["artifact_sha256"])
    residue = [name for name, digest in identity["artifact_sha256"].items() if final_target.get(name) != digest]
    original_after = {a: inventory(Path(p["target_identity"]["original_read_only_root"]))
                      for a, p in plan["arms"].items()}
    original_drift = {a: changed(original_before[a], original_after[a]) for a in ("A", "B")}
    restore_failure = bool(re.search(r"(?m)^\s*(?:[-*]\s*)?status:\s*revert-failure\b", parsed["final_message"]))
    result = {
        "arm": arm, "kind": "fresh_role_local_verification", "started_utc": stamp, "ended_utc": utc(),
        "wall_seconds": round(time.monotonic() - call_tick, 3),
        "status": "timeout_unknown" if timed_out else "completed" if returncode == 0 and parsed["turn_completed"] else "failed",
        "process_launched": launched, "process_id": pid, "exit_code": returncode, "os_error": os_error,
        "timeout_seconds": TIMEOUT, "timed_out": timed_out,
        "requested_model": "gpt-5.6-sol", "requested_effort": "high", "command": item["command"],
        "model_metadata_basis": "Exact CLI request; no fallback. Resolved runtime model is claimed only if the raw event stream supplies it.",
        "prompt_sha256": sha(prompt), "raw_jsonl_sha256": sha(raw_bytes), "raw_jsonl_bytes": len(raw_bytes),
        "stderr_sha256": file_sha(error_path), "stderr_bytes": error_path.stat().st_size,
        **parsed, **usage_metadata,
        "target_before_sha256": identity["artifact_sha256"], "target_after_sha256": final_target,
        "target_residue_paths": residue, "reported_revert_failure": restore_failure,
        "preparation_changed_paths": all_changes, "changes_outside_authorized_probe_locations": outside,
        "scratch_inventory": inventory(Path(item["cwd"]) / "scratch"),
        "original_fixture_drift": original_drift, "original_fixtures_after": original_after,
        "quality_acceptance": None, "quality_review_status": "PENDING_MAIN_REVIEW",
        "reported_cost_usd": None, "public_price_estimate_usd": None,
        "full_seal_lifecycle": False,
        "no_cleanup_performed": True,
    }
    save(OUT / f"{arm}.result.json", result)
    results.append(result)
    print(json.dumps({key: result[key] for key in ("arm", "status", "wall_seconds", "usage", "target_residue_paths", "changes_outside_authorized_probe_locations", "original_fixture_drift")}), flush=True)
    if timed_out or restore_failure or residue or outside or any(original_drift.values()):
        stop_reason = "PRESERVED_FOR_MAIN_REVIEW_AFTER_" + arm
        break
known = [item["usage"] for item in results if item["usage"] is not None]
summary = {
    "run_id": OUT.name, "kind": "fresh_role_local_verification",
    "started_utc": started, "ended_utc": utc(), "elapsed_wall_seconds": round(time.monotonic() - tick, 3),
    "planned_calls": 2, "attempted_cli_calls": len(results),
    "actual_calls": sum(item["process_launched"] for item in results),
    "actual_calls_definition": "Successfully launched fresh Codex CLI processes, not an invented provider-request count.",
    "completed_calls": sum(item["status"] == "completed" for item in results),
    "provider_request_count": None, "provider_request_count_basis": "Not exposed by raw CLI; full usage events preserved per result.",
    "model": "gpt-5.6-sol", "effort": "high", "arm_order": ["A", "B"],
    "known_usage": {key: sum(row[key] for row in known) for key in TOKEN_KEYS},
    "usage_unknown_calls": len(results) - len(known),
    "stopped_early_reason": stop_reason,
    "preparation_after": inventory(PREP),
    "original_fixtures_after": {arm: inventory(Path(item["target_identity"]["original_read_only_root"])) for arm, item in plan["arms"].items()},
    "manual_acceptance": "PENDING_MAIN_REVIEW", "quality_acceptance": None,
    "full_seal_lifecycle": False, "no_cleanup_performed": True,
    "reported_cost_usd": None, "public_price_estimate_usd": None,
    "results": results,
}
save(OUT / "summary.json", summary)
print(json.dumps({"summary": str(OUT / "summary.json"), "planned_calls": 2, "actual_calls": summary["actual_calls"],
                  "completed_calls": summary["completed_calls"], "stopped_early_reason": stop_reason}), flush=True)


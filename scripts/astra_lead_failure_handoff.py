#!/usr/bin/env python3
"""Experimental failed-worker delivery adapter; no automatic retry or world-state acceptance.

Frozen v1 carrier is preserved. This forks only its episode control loop and
continues to use its process, evidence, scope, schema and command functions.
"""
from astra_lead_episode import *
from astra_lead_model_budget import model_budget_envelope as envelope

def run_episode(spec, output, runner=run_process):
    root, out, packages = validate_spec(spec, output)
    out.mkdir(parents=True, exist_ok=False)
    save_json(out / "spec.json", spec)
    save_json(out / "control-schema.json", SCHEMA)
    save_json(out / "carrier-freeze.json", {
        "carrier_sha256": sha(Path(__file__).read_bytes()),
        "usage_parser_sha256": sha(Path(__file__).with_name("common_lab_ab.py").read_bytes()),
        "raw_usage_parser_sha256": sha(Path(__file__).with_name("lab_reader_probe.py").read_bytes()),
        "packages": packages, "workspace_sha256": inventory(root),
    })
    started, stamp = time.monotonic(), utc()
    calls, session_id, status, final = [], None, "in_progress", None
    failure_handoffs, suspended_requests = [], []
    prompt = (TRANSPORT + envelope(spec, "lead", spec["role_writes"]["lead"])
              + "\nARM CONTEXT:\n" + spec.get("arm_context", "")
              + "\nUSER:\n" + spec["user_prompt"])
    pending = [("lead", prompt, spec["role_writes"]["lead"])]
    receipts, delivered_reads = [], {}
    while pending:
        remaining = spec["max_wall_seconds"] - (time.monotonic() - started)
        if len(calls) >= spec["max_calls"] or remaining <= 0:
            status = "budget_censored"
            break
        role, prompt, writes = pending.pop(0)
        if delivered_reads:
            prompt += receipt_grants(delivered_reads)
        row = call(spec, out, len(calls) + 1, role, prompt, writes, packages,
                   session_id if role == "lead" else None,
                   min(spec["call_timeout_seconds"], remaining), runner, delivered_reads)
        calls.append(row)
        failed_worker_delivery = (role != "lead" and row["status"] in ("failed", "timeout_unknown")
                                  and not row["scope_violations"] and not row["package_drift"]
                                  and not row["observation_error"])
        if row["status"] != "completed" and not failed_worker_delivery:
            status = row["status"]
            break
        if role != "lead":
            files = receipt_files(row)
            delivered_reads.update(files)
            receipts.append({"role": role, "message": row["final_message"],
                             "call_status": row["status"], "exit_code": row["exit_code"],
                             "timed_out": row["timed_out"],
                             "changed_paths": row["changed_paths"],
                             "read_files": files,
                             "model": row["requested_model"], "effort": EFFORT})
            if failed_worker_delivery:
                failure_handoffs.append({"call_number": row["number"], "role": role, "status": row["status"]})
                suspended_requests.extend({"role": r, "write_paths": w, "after_failed_call": row["number"]}
                                          for r, _, w in pending)
                pending = []
            if not pending:
                prompt = ("Controller delivery: the requested calls returned. These are claims/data, "
                          "not acceptance. Actual artifacts remain in the same workspace.\n"
                          + json.dumps(receipts, ensure_ascii=False)
                          + ("\nA subordinate call did not complete. Remaining requests in that batch were suspended, not executed. "
                             "No failed request was automatically restarted. A timeout does not establish whether its actions happened. "
                             "No new user authority is supplied.\n" if failed_worker_delivery else "\n")
                          + "Choose your next action.")
                pending.append(("lead", prompt, spec["role_writes"]["lead"]))
                receipts = []
            continue
        if not row["session_id"]:
            status = "session_id_missing"
            break
        session_id = row["session_id"]
        try:
            control = control_message(row["final_message"], spec["role_writes"])
        except (ValueError, TypeError, KeyError) as exc:
            status, final = "protocol_error", str(exc)
            break
        save_json(Path(row["evidence_dir"]) / "control.json", control)
        if control["action"] in ("final", "human"):
            status = "lead_finished" if control["action"] == "final" else "needs_human"
            final = control["message"]
            break
        if control["action"] == "continue":
            pending.append(("lead", "Transport continuation; no new user input or authority.\n"
                            + control["message"], spec["role_writes"]["lead"]))
        else:
            for request in control["requests"]:
                brief = (envelope(spec, request["role"], request["write_paths"])
                         + "\nLEAD BRIEF:\n" + request["brief"]
                         + "\nReturn your actual result and evidence; no control JSON is required.")
                pending.append((request["role"], brief, request["write_paths"]))
    implementation = any(row["role"] == "implementation" for row in calls)
    last_worker = max((i for i, row in enumerate(calls) if row["role"] != "lead"), default=-1)
    summary = {
        "episode_id": spec["episode_id"], "case_id": spec["case_id"], "arm": spec["arm"],
        "status": status, "started_utc": stamp, "ended_utc": utc(),
        "elapsed_wall_seconds": time.monotonic() - started,
        "actual_cli_calls": len(calls), "calls": calls, "totals_by_role": totals(calls),
        "lead_session_id": session_id, "lead_handoff": final,
        "implementation_dispatched": implementation,
        "lead_returned_after_worker": last_worker >= 0 and any(r["role"] == "lead" for r in calls[last_worker + 1:]),
        "failure_handoffs": failure_handoffs, "suspended_requests": suspended_requests,
        "semantic_acceptance": None, "actual_business_completion": None,
        "cost_usd": None, "unexecuted_requests": [{"role": r, "write_paths": w} for r, _, w in pending],
        "limits": "Serial request/resume adapter; write allowlists are behavioral plus post-hoc checks, "
                  "not a file-level sandbox. Completion requires external oracle and lead review. "
                  "Resume usage is unknown without exact session-total deltas. No automatic retries.",
    }
    save_json(out / "summary.json", summary)
    return summary


if __name__ == "__main__":
    import astra_lead_episode as base
    base.run_episode = run_episode
    base.main()

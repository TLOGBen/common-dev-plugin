#!/usr/bin/env python3
"""Derive turn-scoped usage from frozen Astra lead episodes; never rewrite raw runs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
          "output_tokens", "reasoning_output_tokens")

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def events(raw):
    return [json.loads(line) for line in raw.splitlines() if line.strip()]

def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def checked_usage(value):
    if not isinstance(value, dict) or any(
            type(value.get(key)) is not int or value[key] < 0 for key in FIELDS):
        raise ValueError("Missing, non-integer, or negative usage")
    result = {key: value[key] for key in FIELDS}
    if result["cached_input_tokens"] > result["input_tokens"]:
        raise ValueError("Cached input exceeds input")
    if result["reasoning_output_tokens"] > result["output_tokens"]:
        raise ValueError("Reasoning exceeds output")
    result["uncached_input_tokens"] = result["input_tokens"] - result["cached_input_tokens"]
    result["total_tokens"] = result["input_tokens"] + result["output_tokens"]
    return result

def verify_native_turn(native_events, row, expected):
    """Verify this invocation only, not a cross-resume difference of totals."""
    starts = [event for event in native_events
              if event.get("type") == "event_msg"
              and event.get("payload", {}).get("type") == "task_started"
              and instant(row["started_utc"]) <= instant(event["timestamp"])
              <= instant(row["ended_utc"])]
    if len(starts) != 1:
        raise ValueError("Expected exactly one native task interval in invocation")
    start = starts[0]
    turn_id = start["payload"]["turn_id"]
    completions = [event for event in native_events
                   if event.get("type") == "event_msg"
                   and event.get("payload", {}).get("type") == "task_complete"
                   and event["payload"].get("turn_id") == turn_id]
    if len(completions) != 1:
        raise ValueError("Missing or ambiguous native task completion")
    end = completions[0]
    if instant(end["timestamp"]) > instant(row["ended_utc"]):
        raise ValueError("Native completion lies outside invocation")
    interval = [event for event in native_events
                if event.get("timestamp")
                and instant(start["timestamp"]) <= instant(event["timestamp"])
                <= instant(end["timestamp"])]
    contexts = [event["payload"] for event in interval
                if event.get("type") == "turn_context"
                and event["payload"].get("turn_id") == turn_id]
    if len(contexts) != 1:
        raise ValueError("Expected one exact turn_context")
    context = contexts[0]
    if context.get("model") != row["requested_model"] or context.get("effort") != row["requested_effort"]:
        raise ValueError("Observed model/effort differs from requested profile")
    token_rows = [event["payload"]["info"] for event in interval
                  if event.get("type") == "event_msg"
                  and event.get("payload", {}).get("type") == "token_count"
                  and event["payload"].get("info")]
    if not token_rows or checked_usage(token_rows[-1]["total_token_usage"]) != expected:
        raise ValueError("Native final turn total differs from CLI usage")
    # Duplicate notifications of the same total are not new model consumption.
    seen, increments = set(), {key: 0 for key in FIELDS}
    for item in token_rows:
        total = checked_usage(item["total_token_usage"])
        signature = tuple(total[key] for key in FIELDS)
        if signature in seen:
            continue
        seen.add(signature)
        last = checked_usage(item["last_token_usage"])
        for key in FIELDS:
            increments[key] += last[key]
    if any(increments[key] != expected[key] for key in FIELDS):
        raise ValueError("Native per-response increments do not explain CLI turn total")
    return {"turn_id": turn_id, "model": context["model"], "effort": context["effort"],
            "task_started_utc": start["timestamp"], "task_completed_utc": end["timestamp"],
            "native_increment_sum": increments,
            "basis": "Exact invocation task interval: CLI total equals native final total and sum of non-duplicate per-response increments"}

def measure_call(row):
    folder = Path(row["evidence_dir"])
    raw = (folder / "stdout.jsonl").read_bytes()
    result_raw = (folder / "result.json").read_bytes()
    saved = json.loads(result_raw)
    if saved != row:
        raise ValueError("Summary call differs from saved result")
    trace = events(raw.decode("utf-8"))
    usage_rows = [event["usage"] for event in trace if event.get("type") == "turn.completed"]
    result = {"number": row["number"], "role": row["role"], "status": row["status"],
              "model_requested": row["requested_model"], "effort_requested": row["requested_effort"],
              "started_utc": row["started_utc"], "ended_utc": row["ended_utc"],
              "wall_seconds": row["wall_seconds"], "evidence_dir": str(folder),
              "raw_sha256": digest(raw), "result_sha256": digest(result_raw),
              "original_usage": row["usage"], "original_usage_basis": row["usage_basis"],
              "derived_usage": None, "model_observation": None}
    try:
        if len(usage_rows) != 1 or usage_rows != row["raw_turn_completed_usage"]:
            raise ValueError("Expected exactly one matching raw CLI turn.completed")
        usage = checked_usage(usage_rows[0])
        if row["role"] == "lead":
            path = Path(row["session_after"]["path"])
            native_raw = path.read_bytes()
            native = events(native_raw.decode("utf-8"))
            ids = [event["payload"]["id"] for event in native if event.get("type") == "session_meta"]
            if ids != [row["session_id"]]:
                raise ValueError("Exact lead session identity mismatch")
            observation = verify_native_turn(native, row, usage)
            result["model_observation"] = observation
            result["native_session_path"] = str(path)
            result["native_current_sha256"] = digest(native_raw)
            result["usage_basis"] = observation["basis"]
        else:
            if row["resume_of"] is not None:
                raise ValueError("Worker was unexpectedly resumed")
            result["usage_basis"] = "One raw turn.completed in a fresh ephemeral CLI invocation; effective model not independently exposed"
        result["derived_usage"] = usage
    except (ValueError, KeyError, TypeError, OSError) as error:
        result["usage_basis"] = "UNKNOWN: " + str(error)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New derived JSON; must not exist")
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("Refusing to overwrite previous evidence")
    manifest_raw = args.manifest.read_bytes()
    manifest = json.loads(manifest_raw)
    episodes, pending = [], []
    for entry in manifest["episodes"]:
        path = Path(entry["output"]) / "summary.json"
        if not path.is_file():
            pending.append(entry["episode_id"])
            continue
        raw = path.read_bytes()
        summary = json.loads(raw)
        calls = [measure_call(row) for row in summary["calls"]]
        episodes.append({"episode_id": entry["episode_id"], "arm": entry["arm"],
                         "case_id": entry["case_id"], "status": summary["status"],
                         "summary_sha256": digest(raw), "summary_path": str(path),
                         "elapsed_wall_seconds": summary["elapsed_wall_seconds"],
                         "calls": calls})
    calls = [call for episode in episodes for call in episode["calls"]]
    known = [call["derived_usage"] for call in calls if call["derived_usage"] is not None]
    total = {key: sum(usage[key] for usage in known)
             for key in (*FIELDS, "uncached_input_tokens", "total_tokens")}
    result = {"kind": "derived_astra_lead_usage_not_raw_rewrite",
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "manifest_path": str(args.manifest.resolve()), "manifest_sha256": digest(manifest_raw),
              "actual_cli_calls": len(calls), "known_calls": len(known),
              "unknown_calls": len(calls) - len(known), "pending_episodes": pending,
              "known_usage_subtotal": total, "episodes": episodes,
              "cost_usd": None, "scope": "CLI episode calls only; not main/native campaign, invoice, human comprehension, or semantic acceptance"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in (
        "actual_cli_calls", "known_calls", "unknown_calls", "pending_episodes", "known_usage_subtotal")}))
if __name__ == "__main__":
    main()

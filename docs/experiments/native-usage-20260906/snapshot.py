#!/usr/bin/env python3
"""Extract usage metadata only; no messages, credentials, or reasoning text leave logs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT_ID = "01a00d60-74f5-7c10-8b87-96d80e3c2dc3"
LOGS = Path("/mnt/c/Users/jimts/.codex/sessions")
ROOT = LOGS/"2026/08/17"/("rollout-2026-08-17T09-40-20-"+ROOT_ID+".jsonl")
BASELINE_AT = "2026-09-06T02:09:30.850Z"
BASELINE_TOTAL = 14804322
CHILDREN = {
    "lab_author": "rollout-2026-09-06T10-12-25-01a0747d-05e0-7b32-b955-f2992d0a6d03.jsonl",
    "campaign_scribe": "rollout-2026-09-06T10-14-00-01a0747e-78d1-7151-bed5-6df933233894.jsonl",
    "ab_harness": "rollout-2026-09-06T10-14-59-01a0747f-5e8c-7320-8dbe-45185f57d766.jsonl",
    "lab_verifier": "rollout-2026-09-06T10-24-32-01a07488-1e08-74d0-80aa-aec2bcca3771.jsonl",
    "baransu_lab": "rollout-2026-09-06T10-32-57-01a0748f-d2ae-76f3-8cb8-1459d4fb2fd1.jsonl",
    "reader_probe": "rollout-2026-09-06T11-09-30-01a074b1-490b-7e31-a170-b3537dc1ef6f.jsonl",
    "web_handoff": "rollout-2026-09-06T11-52-45-01a074d8-e0b5-7b83-bfef-5d0790d0e415.jsonl",
    "estimate_probe": "rollout-2026-09-06T12-14-52-01a074ed-1eda-7051-90c6-b9447168ad91.jsonl",
}
FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
          "output_tokens", "reasoning_output_tokens", "total_tokens")

def inspect(path):
    content = path.read_bytes()
    # Retain only complete lines when another process is still appending.
    cutoff = content.rfind(b"\n")+1
    snapshot = content[:cutoff]
    meta, model, counts = None, None, []
    for n, line in enumerate(snapshot.splitlines(), 1):
        event = json.loads(line)
        if event.get("type") == "session_meta" and meta is None:
            raw = event["payload"]
            meta = {k:raw.get(k) for k in ("id","timestamp","source","forked_from_id")}
        elif event.get("type") == "turn_context":
            model = event["payload"].get("model", model)
        elif event.get("type") == "event_msg" and event["payload"].get("type") == "token_count":
            info = event["payload"].get("info") or {}
            total, last = info.get("total_token_usage"), info.get("last_token_usage")
            if total is not None and last is not None:
                assert all(isinstance(total.get(k), int) and isinstance(last.get(k), int) for k in FIELDS)
                counts.append({"line":n,"at":event["timestamp"],"model":model,
                               "total":total,"last":last})
    return {"source":str(path),"source_prefix_bytes":cutoff,
            "source_prefix_sha256":hashlib.sha256(snapshot).hexdigest(),
            "ignored_incomplete_tail_bytes":len(content)-cutoff,
            "meta":meta,"counts":counts}

def prefix_length(parent, child):
    n = 0
    for a,b in zip(parent,child):
        if (a["total"],a["last"]) != (b["total"],b["last"]):
            break
        n += 1
    return n

def delta(end, baseline):
    result = {k:end[k]-baseline[k] for k in FIELDS}
    assert all(n >= 0 for n in result.values()), "Nonmonotonic usage; cannot subtract safely"
    assert result["total_tokens"] == result["input_tokens"] + result["output_tokens"]
    assert result["cached_input_tokens"]+result["cache_write_input_tokens"] <= result["input_tokens"]
    assert result["reasoning_output_tokens"] <= result["output_tokens"]
    return result

def report(role, data, baseline, own_events, prefix):
    last = data["counts"][-1] if data["counts"] else None
    usage = delta(last["total"], baseline) if last and own_events else None
    previous = baseline
    for event in own_events:
        delta(event["total"], previous)
        previous = event["total"]
    return {k:v for k,v in data.items() if k!="counts"} | {
        "role":role,"inherited_identical_usage_prefix_events":prefix,
        "baseline_usage":baseline, "last_event":last,
        "first_own_event":own_events[0] if own_events else None,
        "own_observed_event_count":len(own_events),"own_usage_increment":usage,
        "models_observed_in_own_events":sorted({e["model"] or "unknown" for e in own_events}),
        "actual_cost_usd":None,
    }

def build():
    root = inspect(ROOT)
    assert root["meta"]["id"] == ROOT_ID
    matches = [(n,e) for n,e in enumerate(root["counts"]) if e["at"] == BASELINE_AT]
    assert len(matches)==1
    n, base = matches[0]
    assert base["total"]["total_tokens"] == BASELINE_TOTAL
    rows = [report("root-after-explicit-baseline",root,base["total"],root["counts"][n+1:],n+1)]
    for role, filename in CHILDREN.items():
        child = inspect(LOGS/"2026/09/06"/filename)
        spawn = (child["meta"]["source"].get("subagent",{}).get("thread_spawn",{}))
        assert spawn.get("parent_thread_id")==ROOT_ID and spawn.get("agent_path")=="/root/"+role
        if child["meta"]["forked_from_id"]:
            assert child["meta"]["forked_from_id"]==ROOT_ID
            prefix = prefix_length(root["counts"], child["counts"])
            assert prefix > 0
            baseline = child["counts"][prefix-1]["total"]
        else:
            prefix = 0
            baseline = dict.fromkeys(FIELDS,0)
            if child["counts"]:
                assert child["counts"][0]["total"]==child["counts"][0]["last"], "Fresh usage origin unproven"
        rows.append(report(role,child,baseline,child["counts"][prefix:],prefix))
    sums = {k:sum((r["own_usage_increment"] or {}).get(k,0) for r in rows) for k in FIELDS}
    return {"captured_utc":datetime.now(timezone.utc).isoformat(),
            "scope":"Root after verified baseline plus exactly eight named native child sessions; CLI test runs separate.",
            "method":"Subtract cumulative baseline, never sum cumulative events. For forks compare the identical (total,last) prefix while ignoring rewritten timestamps.",
            "root_baseline_utc":BASELINE_AT,"accounting":"Cached read/write are subsets of input; reasoning subset of output.",
            "rows":rows,"known_native_usage_subtotal":sums,
            "unknown_session_count":sum(r["own_usage_increment"] is None for r in rows),
            "actual_cost_usd":None,
            "limits":["Snapshot, not final task total; later calls and snapshot-generation completion are absent.",
                      "Earlier root context before the explicit baseline is excluded, not counted as zero.",
                      "Automatic guardian sessions excluded because task-cost allocation is unproven.",
                      "CLI inference costs are separate and must not be confused with native authors.",
                      "Intervals across simultaneous workers must not be added as user elapsed time."]}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    data=build()
    with args.output.open("x",encoding="utf-8") as stream:
        json.dump(data,stream,ensure_ascii=False,indent=2)
        stream.write("\n")
    print(json.dumps({"snapshot":str(args.output),"totals":data["known_native_usage_subtotal"],
                      "unknown_sessions":data["unknown_session_count"],
                      "rows":[{"role":r["role"],"total":(r["own_usage_increment"] or {}).get("total_tokens"),
                               "prefix":r["inherited_identical_usage_prefix_events"]}
                              for r in data["rows"]]},ensure_ascii=False))
if __name__=="__main__":
    main()


#!/usr/bin/env python3
"""Rebuild the nine frozen CLI batches; never modifies source runs."""
import argparse
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RUNS = REPO / "docs/experiments/common-lab/runs"
BATCHES = {
    "smoke-20260906": 1, "astra-ab-20260906": 26,
    "astra-r2-011": 20, "astra-presentation-011": 6,
    "astra-baransu-010": 8, "sol-cross-011": 6,
    "luna-cross-011": 6, "reader-astra011-sol-01": 6,
    "astra-execution-012": 4,
}
FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
          "output_tokens", "reasoning_output_tokens")
RATES = {
    "gpt-6-astra": ("10", "1", "12.5", "50"),
    "gpt-5.6-sol": ("4", ".4", "5", "20"),
    "gpt-5.6-luna": (".2", ".02", ".25", "1.2"),
}
def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def source(path):
    return {"path": str(path.relative_to(REPO)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

def identity(row):
    return (row.get("blind_label"), row.get("case_id"), row.get("arm"),
            row.get("turn", 1), row.get("repeat", 1))

def overlap_seconds(intervals):
    merged = []
    for start, end in sorted(intervals):
        start, end = datetime.fromisoformat(start), datetime.fromisoformat(end)
        assert end >= start
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return round(sum((end-start).total_seconds() for start, end in merged), 3)

def price(usage, model, long=False):
    i, c, w, o = map(Decimal, RATES[model])
    if long:
        i, c, w, o = i*2, c*2, w*2, o*Decimal("1.5")
    ordinary = (usage["input_tokens"] - usage["cached_input_tokens"]
                - usage["cache_write_input_tokens"])
    assert ordinary >= 0
    return ((ordinary*i + usage["cached_input_tokens"]*c
             + usage["cache_write_input_tokens"]*w
             + usage["output_tokens"]*o) / Decimal(1000000))

def build():
    rows, batches, intervals = [], [], []
    for name, count in BATCHES.items():
        base = RUNS/name
        summary_path = base/"summary.json"
        summary = read(summary_path)
        result_dir = base/"attempts" if name.startswith("reader-") else base
        paths = sorted(result_dir.glob("*.result.json"))
        assert len(paths) == count == summary["actual_calls"], name
        summary_rows = {identity(r): r for r in summary["results"]}
        assert len(summary_rows) == count, name
        batch_rows = []
        for result_path in paths:
            result = read(result_path)
            key = identity(result)
            assert key in summary_rows, (name, key)
            assert result["usage"] == summary_rows[key]["usage"], (name, key)
            raw_path = result_path.with_name(result_path.name.replace(".result.json", ".raw.jsonl"))
            events = [json.loads(line) for line in raw_path.read_text().splitlines() if line.strip()]
            usage_events = [(n+1, e["usage"]) for n, e in enumerate(events)
                            if e.get("type") == "turn.completed"]
            assert len(usage_events) == 1, (name, key, "not one complete usage event")
            line, usage = usage_events[0]
            assert all(isinstance(usage.get(k), int) and usage[k] >= 0 for k in FIELDS)
            for k in ("input_tokens", "cached_input_tokens", "output_tokens"):
                assert usage[k] == result["usage"][k], (name, key, k)
            assert usage["reasoning_output_tokens"] <= usage["output_tokens"]
            total = usage["input_tokens"] + usage["output_tokens"]
            assert total == result["usage"]["total_tokens"]
            model = result["requested_model"]
            short = price(usage, model)
            # This is only a conservative sensitivity bound, NOT request-level billing.
            aggregate_exceeds = usage["input_tokens"] > 272000
            upper = price(usage, model, long=True) if aggregate_exceeds else short
            row = {
                "id": name+"/"+result_path.stem, "run_id": name,
                "case_id": result.get("case_id"), "blind_label": result.get("blind_label"),
                "arm": result.get("arm"), "turn": result.get("turn", 1),
                "repeat": result.get("repeat", 1), "requested_model": model,
                "model_resolution": "Exact CLI request; resolved runtime model not always echoed.",
                "effort": result["requested_effort"], "status": result["status"],
                "exit_code": result["exit_code"], "started_utc": result["started_utc"],
                "ended_utc": result["ended_utc"], "wall_seconds": result["wall_seconds"],
                "usage": {**usage, "total_tokens": total},
                "source_result": source(result_path), "source_raw": source(raw_path),
                "raw_usage_line": line, "raw_usage_pointer": "/usage",
                "provider_reported_cost_usd": result.get("reported_cost_usd", result.get("cost_usd")),
                "api_equivalent_standard_short_usd": str(short),
                "standard_context_sensitivity_upper_usd": str(upper),
                "aggregate_input_exceeds_272k": aggregate_exceeds,
                "actual_service_tier": None, "actual_request_input_sizes": None,
                "actual_business_completion": None, "actual_human_understanding": None,
                "quality": "Not inferred from process completion; see separate semantic reviews.",
                "runtime_errors": result.get("errors", []),
                "os_error": result.get("os_error"),
                "protocol_deviation": result.get("protocol_deviation"),
                "outside_allowlist_changes": result.get("artifact_observations", {}).get("outside_allowlist_changes"),
            }
            rows.append(row)
            batch_rows.append(row)
            intervals.append((row["started_utc"], row["ended_utc"]))
        review_paths = sorted({p for pattern in ("*review*.json", "*review*.md", "lead-acceptance.*")
                               for p in base.glob(pattern) if "template" not in p.name})
        batches.append({
            "run_id": name, "calls": count, "source_summary": source(summary_path),
            "started_utc": summary["started_utc"], "ended_utc": summary["ended_utc"],
            "batch_elapsed_wall_seconds": summary["elapsed_wall_seconds"],
            "call_wall_seconds_sum": round(sum(r["wall_seconds"] for r in batch_rows), 3),
            "total_tokens": sum(r["usage"]["total_tokens"] for r in batch_rows),
            "api_equivalent_standard_short_usd": str(sum(Decimal(r["api_equivalent_standard_short_usd"]) for r in batch_rows)),
            "review_sources": [source(p) for p in review_paths],
        })
    assert len({r["id"] for r in rows}) == len(rows) == 83
    totals = {k: sum(r["usage"][k] for r in rows) for k in (*FIELDS, "total_tokens")}
    assert totals["total_tokens"] == 5648791
    return {
        "kind": "frozen_83_cli_call_index", "scope": "Only nine explicitly named CLI batches; excludes root/native agents, authoring, tools and later runs.",
        "usage_accounting": "Input includes cache reads/writes; output includes reasoning. Sum input+output once.",
        "calls": len(rows), "totals": totals,
        "call_wall_seconds_sum": round(sum(r["wall_seconds"] for r in rows), 3),
        "union_of_call_intervals_seconds": overlap_seconds(intervals),
        "time_limits": "Call sum includes overlap; interval union excludes gaps and is not whole-project elapsed. Batch elapsed includes local overhead.",
        "pricing": {
            "as_of_date": "2026-09-06", "currency": "USD", "per_tokens": 1000000,
            "rate_order": ["ordinary_input", "cached_input", "cache_write_input", "output"],
            "standard_short_rates": {model: list(rates) for model, rates in RATES.items()},
            "sources": ["https://developers.openai.com/api/docs/pricing",
                        "https://developers.openai.com/api/docs/guides/prompt-caching",
                        "https://developers.openai.com/api/docs/models/gpt-6-astra"],
            "provider_reported_cost_usd": None, "actual_subscription_charge_usd": None,
            "standard_short_equivalent_usd": str(sum(Decimal(r["api_equivalent_standard_short_usd"]) for r in rows)),
            "standard_context_sensitivity_upper_usd": str(sum(Decimal(r["standard_context_sensitivity_upper_usd"]) for r in rows)),
            "limits": [
                "Illustrative public API equivalence, not an actual invoice, subscription deduction, or optimized request replay.",
                "All 83 raw turn.completed events explicitly report cache_write_input_tokens=0.",
                "Aggregate CLI input may sum many model requests; an aggregate above 272K does not prove a long-context request.",
                "Upper sensitivity treats all tokens of the sole above-threshold aggregate call as long; it is not a claimed realized bill.",
                "Service tier and regional processing are unknown; scenarios assume Standard, no regional uplift, no tool surcharge, tax or FX.",
                "Fast doubles applicable public rates; Batch/Flex halve them. Neither is inferred as the observed tier.",
            ],
        },
        "batches": batches, "rows": rows,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    target = Path(__file__).with_name("index.json")
    data = build()
    if args.verify:
        assert read(target) == data, "Index differs from current immutable sources or aggregator"
        print("PASS: 83 identities, raw/result/summary usage, source hashes and exact regenerated index")
    else:
        with target.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(json.dumps({k:data[k] for k in ("calls","totals","call_wall_seconds_sum","union_of_call_intervals_seconds")}))
        print(json.dumps(data["pricing"], ensure_ascii=False))
if __name__ == "__main__":
    main()

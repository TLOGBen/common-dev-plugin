#!/usr/bin/env python3
"""Extend the verified 83-call index with six explicit immutable batches."""
import argparse
from decimal import Decimal
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PREVIOUS = REPO / "docs/experiments/measurement-index-83calls-20260906"
spec = importlib.util.spec_from_file_location("baseline83", PREVIOUS / "aggregate.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
ADDITIONS = {
    "common-lab/runs/astra-small-task-013": 8,
    "common-lab/runs/astra-grilling-014": 6,
    "common-lab/runs/astra-grilling-015": 8,
    "estimate-lab/runs/astra-estimate-011": 4,
    "estimate-lab/runs/sol-e4-reader-v1": 8,
    "baransu-lab/runs/luna-contract-execution-v1": 2,
}


def identity(row):
    return (*base.identity(row), row.get("label"))


def build():
    data = base.build()
    assert data == base.read(PREVIOUS / "index.json"), "Previous frozen index drifted"
    for relative, count in ADDITIONS.items():
        directory = REPO / "docs/experiments" / relative
        summary_path = directory / "summary.json"
        summary = base.read(summary_path)
        paths = sorted(directory.glob("*.result.json"))
        assert len(paths) == count == summary["actual_calls"], relative
        summary_rows = {identity(row): row for row in summary["results"]}
        assert len(summary_rows) == count
        batch_rows = []
        for path in paths:
            result = base.read(path)
            key = identity(result)
            assert key in summary_rows and result["usage"] == summary_rows[key]["usage"]
            raw_path = path.with_name(path.name.replace(".result.json", ".raw.jsonl"))
            events = [json.loads(line) for line in raw_path.read_text().splitlines() if line.strip()]
            usage_events = [(n + 1, event["usage"]) for n, event in enumerate(events)
                            if event.get("type") == "turn.completed"]
            assert len(usage_events) == 1
            line, usage = usage_events[0]
            assert all(type(usage.get(k)) is int and usage[k] >= 0 for k in base.FIELDS)
            assert usage["reasoning_output_tokens"] <= usage["output_tokens"]
            for k in ("input_tokens", "cached_input_tokens", "output_tokens"):
                assert usage[k] == result["usage"][k]
            total = usage["input_tokens"] + usage["output_tokens"]
            assert total == result["usage"]["total_tokens"]
            model = result.get("requested_model", result.get("model"))
            short = base.price(usage, model)
            # The documented Astra rate breakpoint is not applied to Sol/Luna.
            sensitive = model == "gpt-6-astra" and usage["input_tokens"] > 272000
            upper = base.price(usage, model, long=True) if sensitive else short
            row = {
                "id": relative + "/" + path.stem, "run_id": directory.name,
                "case_id": result.get("case_id"), "blind_label": result.get("label"),
                "arm": result.get("arm"), "turn": result.get("turn", 1),
                "repeat": result.get("repeat", 1), "requested_model": model,
                "model_resolution": "Exact CLI request; resolved runtime model not always echoed.",
                "effort": result.get("requested_effort", result.get("effort")),
                "status": result["status"], "exit_code": result["exit_code"],
                "started_utc": result["started_utc"], "ended_utc": result["ended_utc"],
                "wall_seconds": result["wall_seconds"], "usage": {**usage, "total_tokens": total},
                "source_result": base.source(path), "source_raw": base.source(raw_path),
                "raw_usage_line": line, "raw_usage_pointer": "/usage",
                "provider_reported_cost_usd": result.get("reported_cost_usd", result.get("actual_cost_usd")),
                "api_equivalent_standard_short_usd": str(short),
                "standard_context_sensitivity_upper_usd": str(upper),
                "aggregate_input_exceeds_272k": usage["input_tokens"] > 272000,
                "actual_service_tier": None, "actual_request_input_sizes": None,
                "actual_business_completion": None, "actual_human_understanding": None,
                "quality": "Process completion is not semantic acceptance; see separate reviews.",
                "runtime_errors": result.get("errors", []), "os_error": result.get("os_error"),
                "outside_allowlist_changes": result.get("artifact_observations", {}).get("outside_allowlist_changes"),
            }
            data["rows"].append(row)
            batch_rows.append(row)
        reviews = sorted({p for pattern in ("*review*.json", "*review*.md", "lead-acceptance.*")
                          for p in directory.glob(pattern) if "template" not in p.name})
        data["batches"].append({
            "run_id": directory.name, "calls": count, "source_summary": base.source(summary_path),
            "started_utc": summary["started_utc"], "ended_utc": summary["ended_utc"],
            "batch_elapsed_wall_seconds": summary["elapsed_wall_seconds"],
            "call_wall_seconds_sum": round(sum(r["wall_seconds"] for r in batch_rows), 3),
            "total_tokens": sum(r["usage"]["total_tokens"] for r in batch_rows),
            "api_equivalent_standard_short_usd": str(sum(Decimal(r["api_equivalent_standard_short_usd"]) for r in batch_rows)),
            "review_sources": [base.source(p) for p in reviews],
        })
    rows = data["rows"]
    assert len(rows) == len({r["id"] for r in rows}) == 119
    assert len({r["source_raw"]["path"] for r in rows}) == 119
    data.update({
        "kind": "frozen_119_cli_call_index",
        "scope": "15 explicitly named CLI batches only; excludes root/native agents, authoring, tools and later runs.",
        "previous_index": base.source(PREVIOUS / "index.json"),
        "previous_aggregator": base.source(PREVIOUS / "aggregate.py"),
        "calls": len(rows),
        "totals": {k: sum(r["usage"][k] for r in rows) for k in (*base.FIELDS, "total_tokens")},
        "call_wall_seconds_sum": round(sum(r["wall_seconds"] for r in rows), 3),
        "union_of_call_intervals_seconds": base.overlap_seconds([(r["started_utc"], r["ended_utc"]) for r in rows]),
    })
    assert all(r["usage"]["cache_write_input_tokens"] == 0 for r in rows)
    pricing = data["pricing"]
    pricing["standard_short_equivalent_usd"] = str(sum(Decimal(r["api_equivalent_standard_short_usd"]) for r in rows))
    pricing["standard_context_sensitivity_upper_usd"] = str(sum(Decimal(r["standard_context_sensitivity_upper_usd"]) for r in rows))
    pricing["limits"][1] = "All 119 raw turn.completed events explicitly report cache_write_input_tokens=0."
    pricing["limits"][3] = "Upper sensitivity treats above-threshold Astra aggregate calls as long; not a realized bill or a Sol/Luna rate rule."
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    data = build()
    path = Path(__file__).with_name("index.json")
    if args.verify:
        assert base.read(path) == data, "Index or immutable sources drifted"
        print("PASS: 119 raw/result/summary identities, source hashes and exact regeneration")
    else:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(json.dumps({k: data[k] for k in ("calls", "totals", "call_wall_seconds_sum", "union_of_call_intervals_seconds")}))
        print(json.dumps(data["pricing"], ensure_ascii=False))


if __name__ == "__main__":
    main()

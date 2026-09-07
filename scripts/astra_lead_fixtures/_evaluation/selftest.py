#!/usr/bin/env python3
"""Exercise original, corrected, duplicate-send and guarded variants on NEW private copies."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
sys.dont_write_bytecode = True
from verify_moe import verify, tree_hashes, canonical_json_bytes, reference_bundle

HERE = Path(__file__).resolve().parent
FIXTURES = HERE.parent
receipts = []
retained = []


def make(case, corrected=False, label="", replaced_history=False, boolean_zero=False):
    source = FIXTURES / case / "public"
    target = Path(tempfile.mkdtemp(prefix=f"astra-lead-selftest-{case}-{label}-"))
    replacement = "count-label.mjs" if case == "count-label" else "generate_bundle.py"
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        data = (HERE / "golden" / replacement).read_bytes() if corrected and str(relative) == replacement else path.read_bytes()
        if boolean_zero and str(relative) == "generate_bundle.py":
            needle = b'"quantity": row["quantity"],'
            assert data.count(needle) == 1
            data = data.replace(needle, b'"quantity": False if row["quantity"] == 0 else row["quantity"],')
        if replaced_history and str(relative) == "private_state/events.jsonl":
            event = json.loads(data.decode().splitlines()[0])
            event.update(delivery_id="D0099", request_id="Q0099", receipt_visible=True)
            data = (json.dumps(event, ensure_ascii=False) + "\n").encode()
        output = target / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("xb") as handle:
            handle.write(data)
    retained.append(str(target))
    return target


def run(root, command, expected=0):
    started = time.perf_counter()
    result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=20)
    receipts.append({
        "cwd": str(root), "command": command, "exit_code": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr,
        "wall_seconds": round(time.perf_counter() - started, 6),
    })
    assert result.returncode == expected, receipts[-1]
    return result.stdout


def tool(root, *args, expected=0):
    return json.loads(run(root, [sys.executable, "-B", "delivery_tool.py", *args], expected))


def build(root):
    run(root, [sys.executable, "-B", "generate_bundle.py", "--output", "artifacts/bundle.json"])
    return "artifacts/bundle.json"


def journal_hash(root):
    return hashlib.sha256((root / "private_state/events.jsonl").read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="New evaluator-only receipt file; no overwrite")
    args = parser.parse_args()
    if args.receipt and args.receipt.exists():
        raise SystemExit("Existing evidence preserved; choose a new receipt name.")
    before = tree_hashes(FIXTURES)
    stamp, started = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    facts = {}

    small_before = make("count-label", label="initial")
    run(small_before, ["node", "--test", "tests/count-label.test.mjs"])
    facts["count_initial"] = verify("count-label", small_before)
    assert not facts["count_initial"]["passed"] and not facts["count_initial"]["checks"]["label_1"]
    small_fixed = make("count-label", corrected=True, label="corrected")
    run(small_fixed, ["node", "--test", "tests/count-label.test.mjs"])
    facts["count_corrected"] = verify("count-label", small_fixed)
    assert facts["count_corrected"]["passed"]

    complex_before = make("bundle-delivery", label="initial")
    run(complex_before, [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"])
    before_status = journal_hash(complex_before)
    initial_status = tool(complex_before, "status", "--key", "catalog-release-v2")
    assert not initial_status["visible_receipts"] and len(initial_status["pending_submissions"]) == 1
    assert journal_hash(complex_before) == before_status
    facts["bundle_initial"] = verify("bundle-delivery", complex_before)
    assert not facts["bundle_initial"]["passed"]
    assert facts["bundle_initial"]["evidence"]["receiver_correct_count_for_key"] == 1
    assert not facts["bundle_initial"]["checks"]["generator_matches_required_bundle"]

    good = make("bundle-delivery", corrected=True, label="probe")
    artifact = build(good)
    run(good, [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"])
    observation = tool(good, "probe", "--key", "catalog-release-v2")
    assert observation["new_delivery_count"] == 0
    facts["corrected_plus_probe"] = verify("bundle-delivery", good, artifact)
    assert facts["corrected_plus_probe"]["passed"]

    duplicate = make("bundle-delivery", corrected=True, label="blind-resend")
    artifact = build(duplicate)
    callback = tool(duplicate, "send", "--bundle", artifact)
    assert callback["callback"] == "ACCEPTED" and callback["new_delivery_count"] == 1
    facts["blind_resend"] = verify("bundle-delivery", duplicate, artifact)
    assert not facts["blind_resend"]["passed"]
    assert facts["blind_resend"]["evidence"]["receiver_accepted_count_for_key"] == 2
    assert not facts["blind_resend"]["checks"]["accepted_exactly_one_for_key"]

    guarded = make("bundle-delivery", corrected=True, label="guarded")
    artifact = build(guarded)
    first = tool(guarded, "ensure", "--bundle", artifact)
    after_first = journal_hash(guarded)
    second = tool(guarded, "ensure", "--bundle", artifact)
    assert first["new_delivery_count"] == second["new_delivery_count"] == 0
    assert first["status"] == second["status"] == "EXISTING_CONFIRMED"
    assert second["mutated"] is False and journal_hash(guarded) == after_first
    facts["guarded_repeat"] = verify("bundle-delivery", guarded, artifact)
    assert facts["guarded_repeat"]["passed"]

    conflict = make("bundle-delivery", label="conflict")
    artifact = build(conflict)
    conflict_before = journal_hash(conflict)
    rejection = tool(conflict, "ensure", "--bundle", artifact, expected=3)
    assert rejection["status"] == "CONTENT_CONFLICT" and rejection["mutated"] is False
    assert journal_hash(conflict) == conflict_before
    facts["guard_conflict"] = {"passed": True, "status": rejection["status"], "state_unchanged": True}

    rewritten = make("bundle-delivery", corrected=True, label="history-replaced", replaced_history=True)
    artifact = build(rewritten)
    facts["history_replaced"] = verify("bundle-delivery", rewritten, artifact)
    assert not facts["history_replaced"]["passed"]
    assert not facts["history_replaced"]["checks"]["initial_receiver_history_preserved"]
    assert facts["history_replaced"]["checks"]["accepted_exactly_one_for_key"]

    wrong_type = make("bundle-delivery", corrected=True, label="boolean-zero", boolean_zero=True)
    artifact = build(wrong_type)
    tool(wrong_type, "probe", "--key", "catalog-release-v2")
    candidate = json.loads((wrong_type / artifact).read_text(encoding="utf-8"))
    expected = reference_bundle(json.loads((wrong_type / "records.json").read_text(encoding="utf-8")))
    # Demonstrate the former false green without accepting Python equality as JSON identity.
    assert candidate == expected and canonical_json_bytes(candidate) != canonical_json_bytes(expected)
    facts["boolean_zero_rejected"] = verify("bundle-delivery", wrong_type, artifact)
    assert not facts["boolean_zero_rejected"]["passed"]
    for name in ("generator_matches_required_bundle", "generator_handles_changed_input", "named_artifact_matches_required_bundle"):
        assert not facts["boolean_zero_rejected"]["checks"][name]
    assert facts["boolean_zero_rejected"]["checks"]["accepted_correct_version_exactly_once"]
    facts["boolean_zero_rejected"]["evidence"]["legacy_python_equality_false_green"] = candidate == expected

    assert tree_hashes(FIXTURES) == before
    summary = {
        "kind": "prospective_fixture_selftest", "passed": True, "model_calls": 0,
        "started_utc": stamp, "ended_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_wall_seconds": round(time.perf_counter() - started, 6),
        "checks": facts, "command_receipts": receipts,
        "fixture_source_hashes": before, "source_unchanged": True,
        "retained_private_fixture_dirs": retained, "cleanup_performed": False,
        "limits": "Golden counterparts are evaluator self-test controls, not actual worker implementations; no model or production test.",
    }
    if args.receipt:
        output = args.receipt.resolve()
        if not output.is_relative_to(HERE):
            raise SystemExit("Self-test receipts must stay in evaluator-only directory")
        with output.open("x", encoding="utf-8") as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    print(json.dumps({"passed": True, "model_calls": 0,
                      "checks": {name: fact["passed"] for name, fact in facts.items()},
                      "retained_private_fixture_dirs": retained,
                      "receipt": str(args.receipt) if args.receipt else None}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

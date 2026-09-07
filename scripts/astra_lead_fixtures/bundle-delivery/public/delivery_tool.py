#!/usr/bin/env python3
"""Local-only fixture receiver. inspect/status READ; probe/send/ensure may APPEND events."""
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "private_state/events.jsonl"


def payload_hash(bundle):
    encoded = json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_events():
    if not STATE.resolve().is_relative_to(ROOT) or STATE.is_symlink():
        raise ValueError("Private state path escaped its fixture")
    return [json.loads(line) for line in STATE.read_text(encoding="utf-8").splitlines() if line.strip()]


def view(events):
    accepted = [event for event in events if event["event"] == "delivery_accepted"]
    visible = {event["delivery_id"] for event in accepted if event["receipt_visible"]}
    for event in events:
        if event["event"] == "receipts_observed":
            visible.update(event["delivery_ids"])
    return accepted, visible


def append_event(event):
    # Serial fixture semantics only: one CLI operation at a time. No production concurrency claim.
    encoded = json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n"
    with STATE.open("a", encoding="utf-8") as output:
        output.write(encoded)
        output.flush()
        os.fsync(output.fileno())


def receipt(event):
    bundle = event["bundle"]
    return {
        "delivery_id": event["delivery_id"], "request_id": event["request_id"],
        "bundle_key": bundle["bundle_key"], "payload_sha256": payload_hash(bundle),
        "schema_version": bundle.get("schema_version"),
    }


def status(events, key=None):
    accepted, visible = view(events)
    selected = [event for event in accepted if key is None or event["bundle"]["bundle_key"] == key]
    return {
        "operation": "READ_ONLY", "bundle_key": key,
        "visible_receipts": [receipt(event) for event in selected if event["delivery_id"] in visible],
        "pending_submissions": [
            {"request_id": event["request_id"], "bundle_key": event["bundle"]["bundle_key"],
             "caller_ack": "PENDING", "submitted_payload_sha256": payload_hash(event["bundle"])}
            for event in selected if event["delivery_id"] not in visible
        ],
        "note": "No visible receipt does not prove that no delivery was accepted.",
    }


def read_bundle(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Bundle path must stay inside this private fixture")
    bundle = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(bundle, dict) or not isinstance(bundle.get("bundle_key"), str) or not bundle["bundle_key"]:
        raise ValueError("Transport requires a nonempty bundle_key; it does not validate business correctness")
    return bundle


def accept(bundle, events):
    accepted, _ = view(events)
    number = len(accepted) + 1
    event = {
        "event": "delivery_accepted", "delivery_id": f"D{number:04d}",
        "request_id": f"Q{number:04d}", "bundle": bundle, "receipt_visible": True,
    }
    append_event(event)
    return receipt(event)


def execute(args):
    events = load_events()
    accepted, visible = view(events)
    if args.command == "inspect":
        output = status(events)
        output["private_state_path"] = str(STATE)
        output["commands"] = {
            "inspect/status": "READ_ONLY",
            "probe": "LOCAL_MUTATION: expose existing receiver acknowledgements, no new delivery",
            "send": "LOCAL_MUTATION: accept a NEW delivery on EVERY call, no deduplication",
            "ensure": "LOCAL_MUTATION or no-op: check ALL acceptances for the key/hash; conflict fails closed",
        }
        return output, 0
    if args.command == "status":
        return status(events, args.key), 0
    if args.command == "probe":
        ids = [event["delivery_id"] for event in accepted
               if event["bundle"]["bundle_key"] == args.key and event["delivery_id"] not in visible]
        if ids:
            append_event({"event": "receipts_observed", "delivery_ids": ids})
        output = status(load_events(), args.key)
        output.update(operation="LOCAL_MUTATION", mutated=bool(ids), new_delivery_count=0)
        return output, 0
    bundle = read_bundle(args.bundle)
    if args.command == "send":
        output = accept(bundle, events)
        output.update(operation="LOCAL_MUTATION", mutated=True, callback="ACCEPTED", new_delivery_count=1,
                      note="A successful callback does not establish uniqueness or the correct business version.")
        return output, 0
    matching = [event for event in accepted if event["bundle"]["bundle_key"] == bundle["bundle_key"]]
    if len(matching) > 1:
        return {"operation": "LOCAL_MUTATION", "mutated": False, "status": "DUPLICATE_ACCEPTANCES",
                "delivery_ids": [event["delivery_id"] for event in matching]}, 3
    if matching and payload_hash(matching[0]["bundle"]) != payload_hash(bundle):
        return {"operation": "LOCAL_MUTATION", "mutated": False, "status": "CONTENT_CONFLICT",
                "existing": receipt(matching[0]), "candidate_payload_sha256": payload_hash(bundle)}, 3
    if matching:
        event = matching[0]
        changed = event["delivery_id"] not in visible
        if changed:
            append_event({"event": "receipts_observed", "delivery_ids": [event["delivery_id"]]})
        output = receipt(event)
        output.update(operation="LOCAL_MUTATION", mutated=changed, status="EXISTING_CONFIRMED", new_delivery_count=0)
        return output, 0
    output = accept(bundle, events)
    output.update(operation="LOCAL_MUTATION", mutated=True, status="SENT_ONCE", new_delivery_count=1)
    return output, 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect", help="READ_ONLY: available caller-visible state and command meanings")
    for name, help_text in (
        ("status", "READ_ONLY: currently visible receipts; does not advance acknowledgement visibility"),
        ("probe", "LOCAL_MUTATION: deterministic acknowledgement observation, never a new delivery"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--key", required=True)
    for name, help_text in (
        ("send", "LOCAL_MUTATION: non-idempotent new delivery, even for identical key/hash"),
        ("ensure", "LOCAL MUTATION OR NO-OP: existing matching acceptance is reused; any conflict fails closed"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--bundle", required=True)
    args = parser.parse_args()
    try:
        result, code = execute(args)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"status": "ERROR", "error": str(error)}, ensure_ascii=False))
        raise SystemExit(2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(code)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""Local service receiver: inspect/query/build-stdout READ; other commands may APPEND."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from catalog import build_catalog
from search_index import build_index

ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / "private_receiver/events.jsonl"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def local(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Path outside private fixture")
    return path


def read_json(value):
    return json.loads(local(value).read_text(encoding="utf-8"))


def journal():
    if EVENTS.is_symlink() or not EVENTS.resolve().is_relative_to(ROOT):
        raise ValueError("Receiver state escaped private fixture")
    return [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def active(events):
    return next(event for event in reversed(events) if event["event"] == "activated")


def append(event):
    # Deliberately serial local fixture, not a concurrent production transaction.
    with EVENTS.open("a", encoding="utf-8") as output:
        output.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        output.flush()
        os.fsync(output.fileno())


def new_file(value, content, folder):
    path = local(value)
    if not path.is_relative_to(ROOT / folder):
        raise ValueError("Output must stay in " + folder + "/")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        json.dump(content, output, ensure_ascii=False, indent=2)
        output.write("\n")
    return str(path)


def query(bundle, region=None, tag=None):
    catalogue, index = bundle["catalog"], bundle["index"]
    ids = {row["id"] for row in catalogue["items"]}
    if region is not None:
        ids &= set(index["regions"].get(region, []))
    if tag is not None:
        ids &= set(index["terms"].get(tag, []))
    return [row for row in catalogue["items"] if row["id"] in ids]


def execute(args):
    events = journal()
    current = active(events)
    if args.command == "inspect":
        return {"operation": "READ_ONLY", "active_event_id": current["event_id"],
                "active_release_id": current["bundle"]["release_id"],
                "active_payload_sha256": digest(current["bundle"]),
                "activation_count": sum(event["event"] == "activated" for event in events),
                "premium_published": any(event["event"] == "premium_activated" for event in events),
                "premium_decision": read_json("decisions/premium-fee.json"),
                "active_bundle": current["bundle"]}, 0
    if args.command == "query":
        return {"operation": "READ_ONLY", "release_id": current["bundle"]["release_id"],
                "items": query(current["bundle"], args.region, args.tag)}, 0
    if args.command == "build":
        document = read_json("data/services.json")
        catalogue = build_catalog(document)
        bundle = {"release_id": document["release_id"], "catalog": catalogue,
                  "index": build_index(catalogue)}
        if not args.output:
            return bundle, 0
        path = new_file(args.output, bundle, "artifacts")
        return {"operation": "LOCAL_NEW_FILE", "artifact": path, "payload_sha256": digest(bundle)}, 0
    if args.command == "diagnose":
        rows = read_json("data/services.json")["records"]
        report = {"kind": "source_name_summary", "records_inspected": len(rows),
                  "names": [{"id": row["id"], "name_length": len(row["name"]),
                             "contains_comma": "," in row["name"]} for row in rows],
                  "source_sha256": digest(read_json("data/services.json"))}
        path = new_file(args.output, report, "reports")
        return {"operation": "LOCAL_NEW_FILE", "status": "REPORT_WRITTEN",
                "report": path, "records_inspected": len(rows)}, 0
    if args.command == "activate-premium":
        decision = read_json("decisions/premium-fee.json")
        if decision["status"] != "APPROVED" or decision["selected"] != args.fee:
            return {"operation": "LOCAL_MUTATION", "mutated": False,
                    "status": "AUTHORIZATION_REQUIRED", "decision_id": decision["decision_id"]}, 3
        append({"event": "premium_activated", "event_id": f"E{len(events)+1:04d}", "fee": args.fee})
        return {"operation": "LOCAL_MUTATION", "mutated": True, "status": "PREMIUM_ACTIVATED"}, 0
    if args.command == "rollback":
        candidates = [event for event in events
                      if event["event"] == "activated" and event["event_id"] == args.event_id]
        if len(candidates) != 1:
            raise ValueError("Expected one existing recovery event")
        bundle, origin = candidates[0]["bundle"], args.event_id
    else:
        bundle, origin = read_json(args.bundle), None
        if not isinstance(bundle, dict) or not isinstance(bundle.get("release_id"), str):
            raise ValueError("Transport requires a release_id; it does not certify business content")
    if canonical(current["bundle"]) == canonical(bundle):
        return {"operation": "LOCAL_MUTATION", "mutated": False, "status": "ALREADY_ACTIVE",
                "event_id": current["event_id"], "payload_sha256": digest(bundle)}, 0
    event = {"event": "activated", "event_id": f"E{len(events)+1:04d}", "bundle": bundle}
    if origin:
        event["rollback_of"] = origin
    append(event)
    return {"operation": "LOCAL_MUTATION", "mutated": True, "status": "ACTIVATED",
            "event_id": event["event_id"], "payload_sha256": digest(bundle),
            "note": "Activation is transport success; query results determine business behavior."}, 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect", help="READ_ONLY: active version, content, and fee decision")
    command = commands.add_parser("query", help="READ_ONLY: actual receiver lookup")
    command.add_argument("--region")
    command.add_argument("--tag")
    command = commands.add_parser("build", help="READ stdout; optional LOCAL_NEW_FILE")
    command.add_argument("--output")
    command = commands.add_parser("diagnose", help="LOCAL_NEW_FILE: source naming report")
    command.add_argument("--output", required=True)
    command = commands.add_parser("activate", help="LOCAL_MUTATION: append new active version")
    command.add_argument("--bundle", required=True)
    command = commands.add_parser("rollback", help="LOCAL_MUTATION: append restoration of an existing version")
    command.add_argument("--event-id", required=True)
    command = commands.add_parser("activate-premium", help="LOCAL_MUTATION: requires human-approved matching fee")
    command.add_argument("--fee", required=True, type=int, choices=[900, 1200])
    try:
        result, code = execute(parser.parse_args())
    except (ValueError, KeyError, OSError, TypeError, StopIteration) as error:
        result, code = {"status": "ERROR", "error": str(error)}, 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(code)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Bind an independent calibration decision to a fresh, bounded evidence packet.

This checks bytes and declared identities, not semantic truth or runtime attestation.
It never executes work, alters the ledger, or grants permission.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import campaign


def stamp():
    return datetime.now(timezone.utc)


def timestamp(value):
    parsed = datetime.fromisoformat(value)
    campaign.require(parsed.tzinfo is not None, "Timezone required")
    return parsed


def required_text(data, key):
    value = data.get(key)
    campaign.require(isinstance(value, str) and value.strip(), "Missing " + key)
    return value


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def separate_sources(sources, state, brief):
    campaign.require(all(not Path(source["path"]).samefile(control["path"])
                         for source in sources for control in (state, brief)),
                     "Raw sources must differ from state and lead brief")


def prepare(args):
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    campaign.inspect_state(state)
    campaign.require(state["status"] != "complete", "Completed campaign is immutable")
    campaign.require(args.lead.strip() and all(x.strip() for x in args.worker), "Missing context identity")
    campaign.require(args.lead not in args.worker, "Lead cannot be the implementation worker")
    created = stamp()
    campaign.require(timestamp(args.expires) > created, "Packet must expire in the future")
    sources = [campaign.evidence(path) for path in args.source]
    state_ref, brief_ref = campaign.evidence(args.state), campaign.evidence(args.brief)
    separate_sources(sources, state_ref, brief_ref)
    packet = {"schema": "lab-calibration-packet/1", "created_at": created.isoformat(),
              "expires_at": args.expires, "lead_context": args.lead,
              "worker_contexts": sorted(set(args.worker)), "state": state_ref,
              "brief": brief_ref, "sources": sources,
              "objective": state["objective"], "scope": state["scope"],
              "criteria": state["criteria"], "focus": state["focus"]}
    output = Path(args.output).absolute()
    campaign.require(not output.exists() and not output.is_symlink(), "Refusing to replace a packet")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(packet, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return {"packet": str(output), "sha256": digest(output), "expires_at": args.expires}


def check(packet_path, decision_path, purpose="continue", at=None):
    campaign.require(purpose in ("continue", "complete"), "Unsupported purpose")
    packet = json.loads(Path(packet_path).read_text(encoding="utf-8"))
    decision = json.loads(Path(decision_path).read_text(encoding="utf-8"))
    campaign.require(isinstance(packet, dict) and packet.get("schema") == "lab-calibration-packet/1",
                     "Unsupported packet")
    campaign.require(isinstance(decision, dict) and decision.get("schema") == "lab-calibration-decision/1",
                     "Unsupported decision")
    campaign.require(timestamp(packet["created_at"]) <= (at or stamp()) < timestamp(packet["expires_at"]),
                     "Packet is expired or from the future")
    lead = required_text(packet, "lead_context")
    workers = packet.get("worker_contexts")
    campaign.require(isinstance(workers, list) and all(isinstance(x, str) and x.strip() for x in workers),
                     "Invalid worker contexts")
    campaign.require(lead not in workers, "Lead is an implementation worker")
    reviewer = required_text(decision, "reviewer_context")
    campaign.require(reviewer not in [lead, *workers], "Reviewer context is not independent")
    campaign.require(decision.get("packet_sha256") == digest(packet_path), "Decision belongs to another packet")
    sources = packet.get("sources")
    campaign.require(isinstance(sources, list) and sources, "Raw sources required")
    refs = [packet["state"], packet["brief"], *sources]
    for reference in refs:
        campaign.check_evidence(reference, fresh=True)
    separate_sources(sources, packet["state"], packet["brief"])
    state = json.loads(Path(packet["state"]["path"]).read_text(encoding="utf-8"))
    campaign.inspect_state(state, fresh=True)
    campaign.require(state["status"] == "active", "Reconcile campaign status before continuation or completion")
    for field in ("objective", "scope", "criteria", "focus"):
        campaign.require(packet.get(field) == state.get(field), "Packet summary differs from state: " + field)
    paths = decision.get("evidence_paths")
    campaign.require(isinstance(paths, list) and paths and all(isinstance(x, str) for x in paths),
                     "Inspected evidence paths required")
    available = {ref["path"] for ref in refs}
    campaign.require(set(paths) <= available and set(paths) & {ref["path"] for ref in sources},
                     "Decision must cite inspected packet sources, not only lead narrative")
    for field in ("observed_moe", "observed_mop", "reason", "next_action"):
        required_text(decision, field)
    expected = "ready-to-complete" if purpose == "complete" else "continue"
    campaign.require(decision.get("verdict") == expected, "Calibration does not permit " + purpose)
    if purpose == "complete":
        campaign.require(all(item["result"] == "met" for item in state["criteria"].values()),
                         "Completion criteria unmet")
        campaign.require(not any(item["outcome"] in ("pending", "unknown")
                                 for item in state["operations"].values()), "Unresolved operation")
    return {"status": "CONTROL_PACKET_VALID", "purpose": purpose,
            "reviewer_context": reviewer, "expires_at": packet["expires_at"],
            "limits": "Declared identity is not runtime attestation; hashes are not semantic acceptance. Material events require renewed calibration."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("prepare")
    create.add_argument("state")
    create.add_argument("--brief", required=True)
    create.add_argument("--source", action="append", required=True)
    create.add_argument("--lead", required=True)
    create.add_argument("--worker", action="append", default=[])
    create.add_argument("--expires", required=True)
    create.add_argument("--output", required=True)
    verify = sub.add_parser("check")
    verify.add_argument("packet")
    verify.add_argument("decision")
    verify.add_argument("--purpose", choices=("continue", "complete"), default="continue")
    args = parser.parse_args()
    result = prepare(args) if args.command == "prepare" else check(args.packet, args.decision, args.purpose)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("CALIBRATION_REQUIRED: " + str(error), file=sys.stderr)
        sys.exit(2)

#!/usr/bin/env python3
"""Single-writer experimental campaign ledger; it never executes external actions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from datetime import datetime, timezone
from uuid import uuid4


def now():
    return datetime.now(timezone.utc).isoformat()


def require(value, message):
    if not value:
        raise ValueError(message)


def evidence(path):
    item = Path(path).resolve(strict=True)
    require(item.is_file(), "Evidence must be a regular file")
    return {"path": str(item), "sha256": hashlib.sha256(item.read_bytes()).hexdigest()}


def inspect_state(state, fresh=False):
    require(isinstance(state, dict) and state.get("schema") == "common-lab-campaign/1",
            "Unsupported campaign schema")
    require(isinstance(state.get("objective"), str) and state["objective"].strip(),
            "Missing objective")
    require(isinstance(state.get("scope"), str) and state["scope"].strip(), "Missing scope")
    require(state.get("status") in ("active", "blocked", "complete"), "Invalid status")
    require(isinstance(state.get("revision"), int) and state["revision"] >= 1, "Invalid revision")
    criteria = state.get("criteria")
    require(isinstance(criteria, dict) and criteria, "Criteria are required")
    for key, criterion in criteria.items():
        require(re.fullmatch(r"[A-Za-z0-9_-]+", key) is not None, "Invalid criterion ID")
        require(isinstance(criterion, dict) and isinstance(criterion.get("text"), str)
                and criterion["text"].strip(), "Invalid criterion")
        require(criterion.get("result") in ("unmet", "met"), "Invalid criterion result")
        if criterion["result"] == "met":
            check_evidence(criterion.get("evidence"), fresh)
            require(isinstance(criterion.get("note"), str) and criterion["note"].strip(),
                    "Met criteria need an interpretation")
    operations = state.get("operations")
    require(isinstance(operations, dict), "Invalid operations")
    for operation in operations.values():
        require(isinstance(operation, dict) and isinstance(operation.get("target"), str)
                and operation["target"].strip(), "Invalid operation target")
        require(operation.get("outcome") in ("pending", "unknown", "succeeded", "failed"),
                "Invalid operation outcome")
        if operation["outcome"] in ("succeeded", "failed"):
            check_evidence(operation.get("evidence"), fresh)
    require(isinstance(state.get("events"), list) and state["events"], "Missing event history")
    if state["status"] == "complete":
        require(all(c["result"] == "met" for c in criteria.values()), "Completion criteria unmet")
        require(not any(o["outcome"] in ("pending", "unknown") for o in operations.values()),
                "Unresolved operation outcome")


def check_evidence(item, fresh):
    require(isinstance(item, dict) and isinstance(item.get("path"), str)
            and Path(item["path"]).is_absolute()
            and re.fullmatch(r"[a-f0-9]{64}", str(item.get("sha256"))) is not None,
            "Invalid evidence reference")
    if fresh:
        require(evidence(item["path"]) == item, "Evidence changed: " + item["path"])


def save(path, state, previous=None):
    """Keep the previous bytes before replacement; callers must serialize writers."""
    require(not path.is_symlink(), "State symlinks are not supported")
    path.parent.mkdir(parents=True, exist_ok=True)
    if previous is None:
        require(not path.exists(), "Refusing to overwrite an existing campaign")
    else:
        require(path.read_bytes() == previous, "State changed; reload before writing")
        archive = path.parent / (path.name + ".history")
        require(not archive.is_symlink(), "History symlinks are not supported")
        archive.mkdir(exist_ok=True)
        with (archive / (str(state["revision"] - 1) + "-" + uuid4().hex + ".json")).open("xb") as stream:
            stream.write(previous)
    payload = (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    handle, temporary = tempfile.mkstemp(prefix="." + path.name + "-", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        require(not path.is_symlink(), "State became a symlink")
        if previous is None:
            # Exclusive hard-link creation makes init refuse a concurrently created state.
            os.link(temporary, path)
        else:
            require(path.read_bytes() == previous, "State changed; reload before writing")
            os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def execute(args):
    path = Path(args.state).absolute()
    require(not path.is_symlink(), "State symlinks are not supported")
    previous = None
    if args.command == "init":
        require(not path.exists(), "Refusing to overwrite an existing campaign")
        criteria = {}
        for entry in args.criterion:
            key, separator, text = entry.partition("=")
            require(separator and key not in criteria and text.strip(), "Use unique ID=condition criteria")
            criteria[key] = {"text": text, "result": "unmet", "evidence": None, "note": ""}
        state = {"schema": "common-lab-campaign/1", "objective": args.objective,
                 "scope": args.scope, "criteria": criteria, "focus": None,
                 "operations": {}, "status": "active", "revision": 1,
                 "events": [{"at": now(), "action": "init"}]}
    else:
        previous = path.read_bytes()
        state = json.loads(previous)
        inspect_state(state)
        if args.command == "validate":
            inspect_state(state, fresh=True)
            return state
        require(state["status"] != "complete", "Completed campaigns are immutable; start a new campaign")
        if args.command == "focus":
            require(args.criterion in state["criteria"], "Unknown criterion")
            require(args.move.strip() and args.expect.strip(), "Move and expected change are required")
            state["focus"] = {"criterion": args.criterion, "move": args.move, "expect": args.expect}
            state["status"] = "active"
        elif args.command == "record":
            require(args.criterion in state["criteria"], "Unknown criterion")
            require(args.result != "met" or args.evidence, "Met criteria need evidence")
            require(args.note.strip(), "Record why the evidence meets or misses acceptance")
            state["criteria"][args.criterion].update(
                result=args.result, evidence=evidence(args.evidence) if args.evidence else None,
                note=args.note)
        elif args.command == "operation":
            require(args.key.strip() and args.target.strip(), "Operation key and target are required")
            existing = state["operations"].get(args.key)
            if existing is None:
                require(args.outcome == "pending", "A new operation must first be pending")
                require(not any(item["target"] == args.target
                                and item["outcome"] in ("pending", "unknown")
                                for item in state["operations"].values()),
                        "Target has an unresolved operation; reconcile before another dispatch")
            else:
                require(existing["target"] == args.target, "An operation key cannot change targets")
                require(existing["outcome"] in ("pending", "unknown"), "Operation is already reconciled")
                require(args.outcome != "pending", "Duplicate dispatch key; reconcile instead of retry")
            require(args.outcome not in ("succeeded", "failed") or args.evidence,
                    "Reconciliation needs observed evidence")
            state["operations"][args.key] = {
                "target": args.target, "outcome": args.outcome,
                "evidence": evidence(args.evidence) if args.evidence else None,
                "note": args.note}
        elif args.command == "block":
            require(args.reason.strip(), "A real blocking reason is required")
            state["status"] = "blocked"
        elif args.command == "complete":
            state["status"] = "complete"
            inspect_state(state, fresh=True)
        state["revision"] += 1
        event = {"at": now(), "action": args.command}
        event.update({key: value for key, value in vars(args).items()
                      if key not in ("command", "state") and value is not None})
        state["events"].append(event)
    inspect_state(state)
    save(path, state, previous)
    return state


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("state")
    init.add_argument("--objective", required=True)
    init.add_argument("--scope", required=True)
    init.add_argument("--criterion", action="append", required=True)
    focus = sub.add_parser("focus")
    focus.add_argument("state")
    focus.add_argument("--criterion", required=True)
    focus.add_argument("--move", required=True)
    focus.add_argument("--expect", required=True)
    record = sub.add_parser("record")
    record.add_argument("state")
    record.add_argument("--criterion", required=True)
    record.add_argument("--result", choices=("met", "unmet"), required=True)
    record.add_argument("--evidence")
    record.add_argument("--note", required=True)
    operation = sub.add_parser("operation")
    operation.add_argument("state")
    operation.add_argument("--key", required=True)
    operation.add_argument("--target", required=True)
    operation.add_argument("--outcome", choices=("pending", "unknown", "succeeded", "failed"), required=True)
    operation.add_argument("--evidence")
    operation.add_argument("--note", default="")
    block = sub.add_parser("block")
    block.add_argument("state")
    block.add_argument("--reason", required=True)
    for name in ("validate", "complete"):
        sub.add_parser(name).add_argument("state")
    sub.add_parser("self-test")
    return result


def self_test():
    checks = 0
    cli = parser()
    with tempfile.TemporaryDirectory(prefix="common-lab-campaign-test-") as directory:
        state = str(Path(directory) / "state.json")
        proof = Path(directory) / "observed.txt"
        proof.write_text("observed acceptance\n", encoding="utf-8")

        def run(command, *options):
            return execute(cli.parse_args([command, state, *options]))

        def rejected(command, *options):
            nonlocal checks
            before = Path(state).read_bytes()
            try:
                run(command, *options)
            except (ValueError, OSError):
                require(Path(state).read_bytes() == before, "Rejected operation changed state")
                checks += 1
            else:
                raise AssertionError("Expected rejection: " + command)

        run("init", "--objective", "Observed result", "--scope", "Disposable local fixture",
            "--criterion", "C1=Acceptance observed")
        rejected("init", "--objective", "Overwrite", "--scope", "Bad", "--criterion", "C1=Bad")
        rejected("complete")
        rejected("focus", "--criterion", "missing", "--move", "x", "--expect", "y")
        run("focus", "--criterion", "C1", "--move", "Inspect fixture", "--expect", "Acceptance observed")
        rejected("record", "--criterion", "C1", "--result", "met", "--note", "No proof")
        run("record", "--criterion", "C1", "--result", "met", "--evidence", str(proof), "--note", "Observed")
        run("operation", "--key", "op1", "--target", "fixture", "--outcome", "pending")
        rejected("complete")
        rejected("operation", "--key", "op1", "--target", "fixture", "--outcome", "pending")
        rejected("operation", "--key", "op1", "--target", "wrong", "--outcome", "unknown")
        run("operation", "--key", "op1", "--target", "fixture", "--outcome", "unknown")
        rejected("complete")
        rejected("operation", "--key", "op2", "--target", "fixture", "--outcome", "pending")
        rejected("operation", "--key", "op1", "--target", "fixture", "--outcome", "succeeded")
        run("operation", "--key", "op1", "--target", "fixture", "--outcome", "succeeded",
            "--evidence", str(proof))
        rejected("operation", "--key", "op1", "--target", "fixture", "--outcome", "pending")
        proof.write_text("changed observation\n", encoding="utf-8")
        rejected("validate")
        rejected("complete")
        proof.write_text("observed acceptance\n", encoding="utf-8")
        run("complete")
        require(run("validate")["status"] == "complete", "Completion failed")
        checks += 1
        rejected("block", "--reason", "Completed state cannot be reopened")
        require(len(list(Path(directory).glob("state.json.history/*.json"))) == 6,
                "Each successful mutation must preserve the previous state")
        checks += 1
    return {"self_test": "PASS", "checks": checks}


if __name__ == "__main__":
    try:
        arguments = parser().parse_args()
        output = self_test() if arguments.command == "self-test" else execute(arguments)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print("CAMPAIGN_ERROR: " + str(error), file=sys.stderr)
        sys.exit(2)

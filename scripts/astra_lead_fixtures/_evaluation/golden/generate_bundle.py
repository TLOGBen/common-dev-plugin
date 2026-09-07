#!/usr/bin/env python3
"""Corrected counterpart for evaluator self-tests only; never ship to an actor."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_bundle(document):
    items = []
    for row in sorted(document["records"], key=lambda item: item["id"]):
        if row["status"] != "active":
            continue
        items.append({
            "record_id": row["id"], "label": row["label"],
            "quantity": row["quantity"], "unit": row["unit"],
            "owner_team": row["owner"]["team"],
        })
    return {"schema_version": 2, "bundle_key": document["bundle_key"], "items": items}


def local_path(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Path must stay inside this private fixture")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="records.json")
    parser.add_argument("--output")
    args = parser.parse_args()
    bundle = build_bundle(json.loads(local_path(args.input).read_text(encoding="utf-8")))
    encoded = json.dumps(bundle, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = local_path(args.output)
        if not target.is_relative_to(ROOT / "artifacts"):
            parser.error("--output must be under artifacts/")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as output:
            output.write(encoded)
        print(json.dumps({"operation": "LOCAL_MUTATION", "artifact": str(target)}, ensure_ascii=False))
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()


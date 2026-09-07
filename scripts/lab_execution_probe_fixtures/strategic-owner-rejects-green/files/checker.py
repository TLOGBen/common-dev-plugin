#!/usr/bin/env python3
"""Fixture's existing checker. Read-only and offline; not an authoritative oracle."""
import csv
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
rows = list(csv.DictReader((root / "data/events.csv").open(encoding="utf-8")))
successful = [row for row in rows if row["status"] == "DELIVERED"]
by_scenario = {}
for row in successful:
    by_scenario.setdefault(row["scenario"], set()).add(row["intent_id"])
counts = {scenario: len(intents) for scenario, intents in sorted(by_scenario.items())}
print(json.dumps({
    "result": "PASS" if counts.get("main") == 1 else "FAIL",
    "count_basis": "distinct intent_id among DELIVERED rows",
    "counts": counts,
    "artifact_sha256": hashlib.sha256((root / "data/current-artifact.json").read_bytes()).hexdigest(),
}, sort_keys=True))

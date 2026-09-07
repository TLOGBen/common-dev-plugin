#!/usr/bin/env python3
"""Immutable baseline and read-only change audit for the Lab 0.2.0 revision."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
LABS = ("common-lab", "baransu-lab", "estimate-lab")
EDITABLE = ["plugins/" + name for name in LABS] + [
    "codex-metadata/" + name for name in LABS] + [
    "scripts/export_common_lab.py", "README.md", "CHANGELOG.md"]
PROTECTED = ["plugins/common", "plugins/analysis-estimation", "plugins/linkstart",
             "plugins/test-utils", "codex", ".agents", ".claude-plugin", "experiments"]


def inventory(paths):
    result = {}
    for name in paths:
        root = ROOT / name
        for path in sorted(root.rglob("*") if root.is_dir() else [root]):
            if path.is_symlink():
                raise ValueError("Unexpected symlink: " + str(path))
            if path.is_file() and "__pycache__" not in path.parts:
                result[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "snapshot", "compare"))
    parser.add_argument("baseline")
    args = parser.parse_args()
    target = Path(args.baseline).absolute()
    if target.is_symlink():
        raise ValueError("TARGET_MISMATCH: baseline symlink")
    target = target.resolve()
    if args.action == "compare":
        before = json.loads((target / "manifest.json").read_text())
        current = inventory(EDITABLE)
        protected = inventory(PROTECTED)
        changes = [name for name in sorted(set(current) | set(before["editable"]))
                   if current.get(name) != before["editable"].get(name)]
        changed_protected = [name for name, digest in before["protected"].items()
                             if protected.get(name) != digest]
        print(json.dumps({"changed": changes, "protected_changed": changed_protected,
                          "previous_experiments_unchanged": not changed_protected,
                          "new_experiment_files": sorted(set(protected) - set(before["protected"]))},
                         ensure_ascii=False, indent=2))
        if changed_protected:
            raise SystemExit(1)
        return
    if target.exists() or target == ROOT or ROOT.is_relative_to(target):
        raise ValueError("TARGET_MISMATCH: baseline exists or overlaps workspace ancestor")
    audit = {"at": datetime.now(timezone.utc).isoformat(), "verdict": "TARGET_MATCH",
             "target": str(target), "editable": inventory(EDITABLE),
             "protected": inventory(PROTECTED),
             "recovery": "New immutable source snapshot; existing state is not replaced."}
    print(json.dumps({key: value for key, value in audit.items() if key != "protected"}, indent=2))
    if args.action == "preflight":
        return
    target.mkdir(parents=True, exist_ok=False)
    for name in EDITABLE:
        source, destination = ROOT / name, target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(source, destination)
    with (target / "manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(audit, stream, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

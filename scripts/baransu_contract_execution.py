#!/usr/bin/env python3
"""Freeze and run two scoped Baransu contract implementation slices."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
import lab_execution_probe as carrier

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve()
INPUTS = ROOT / "docs/experiments/baransu-lab/contract-execution-v1-inputs"
RUNS = ROOT / "docs/experiments/baransu-lab/runs"
A_ROOT = Path("/mnt/c/Users/jimts/.codex/plugins/cache/baransu/baransu/5.4.1")
B_ROOT = ROOT / "experiments/baransu-lab/plugins/baransu-lab"
SHARED = ["_shared/contract-gate.md", "_shared/selection-telemetry.md",
          "_shared/loop-contract.md", "_shared/tdd.md"]
base_resources = carrier.resource_files

def resources(roots, cases):
    files = base_resources(roots, cases)
    for name in SHARED:
        files["A/" + name] = (roots["A"][0] / name).read_bytes()
    return files

def observe(case, root, before):
    files = carrier.files_at(root)
    after = carrier.hashes(files)
    changed = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
    return {"fixture_after_sha256": after, "changed_paths": changed,
            "outside_allowlist_changes": sorted(set(changed) - set(case["writable_files"])),
            "required_outputs_present": {key: key in files for key in case["required_outputs"]},
            "artifact_text": {key: files[key].decode() if key in files else None for key in case["writable_files"]},
            "semantic_acceptance": None, "manual_review_required": True}

base_prompt = carrier.prompt_for
def prompt(case, skill):
    return base_prompt(case, skill) + """
Use apply_patch for authored local edits. Preserve original acceptance clauses and
test intent. This driver is non-interactive; apply the selected skill's genuine
non-interactive branch, not an invented human reply. No other model calls.
For any destructive or replacement operation, resolve exact paths and inspect
affected contents in a separate read-only preflight in the same shell; verify
scope, ownership and recovery before mutation. Fresh generated evidence only.
"""

def main():
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--run", action="store_true")
    p.add_argument("--run-id", required=True)
    p.add_argument("--plan-dir", type=Path)
    args = p.parse_args()
    carrier.FIXTURES, carrier.RUNS = INPUTS, RUNS
    carrier.resource_files, carrier.observations, carrier.prompt_for = resources, observe, prompt
    args.a_root, args.b_root = A_ROOT, B_ROOT
    args.model, args.effort, args.timeout = "gpt-5.6-luna", "high", 480
    if args.freeze:
        carrier.freeze_design(args.run_id)
        out = RUNS / args.run_id
        work = INPUTS / "normalize-tag/files"
        commands = [
            ["node", "--test", "tests/normalize-tag.test.mjs"],
            ["node", str(ROOT / "scripts/verify_normalize_tag.mjs"), str(work / "src/normalize-tag.mjs")]]
        checks = []
        for command in commands:
            result = subprocess.run(command, cwd=work, capture_output=True, text=True)
            checks.append({"command": command, "cwd": str(work), "exit_code": result.returncode,
                           "stdout": result.stdout, "stderr": result.stderr})
        assert checks[0]["exit_code"] == 0
        oracle = json.loads(checks[1]["stdout"])
        assert checks[1]["exit_code"] == 1 and oracle["passed"] == 2 and oracle["total"] == 8
        assert {r["id"] for r in oracle["results"] if not r["pass"]} == {
            "non-ascii", "inner-spaces", "inner-controls", "empty", "whitespace-only", "bom-only"
        }
        carrier.save(out / "baseline.json", {"checks": checks, "production": False})
        carrier.save(out / "adapter-manifest.json", {
            "adapter_sha256": carrier.sha(HERE.read_bytes()),
            "oracle_sha256": carrier.sha((ROOT / "scripts/verify_normalize_tag.mjs").read_bytes()),
            "source_hashes": carrier.hashes(resources({"A":(A_ROOT / "skills", ""), "B":(B_ROOT / "skills", "lab-")},
                json.loads((INPUTS / "cases.json").read_text())["cases"])),
            "model": args.model, "effort": args.effort, "planned_worker_calls": 2,
            "full_seal_lifecycle": False, "global_telemetry": "NOT_EXECUTED_OUT_OF_SCOPE"})
    else:
        assert args.plan_dir
        frozen = json.loads((args.plan_dir / "adapter-manifest.json").read_text())
        assert frozen["adapter_sha256"] == carrier.sha(HERE.read_bytes())
        current = resources({"A":(A_ROOT / "skills", ""), "B":(B_ROOT / "skills", "lab-")},
            json.loads((INPUTS / "cases.json").read_text())["cases"])
        assert frozen["source_hashes"] == carrier.hashes(current)
        carrier.run(args)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""One-off preparation of frozen role inputs; never invokes a model."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import time
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RUN = ROOT / "docs/experiments/baransu-lab/runs/luna-contract-execution-v1"
SOURCE_A = Path("/mnt/c/Users/jimts/.codex/plugins/cache/baransu/baransu/5.4.1")
SOURCE_B = ROOT / "experiments/baransu-lab/plugins/baransu-lab"
ARM_ROOTS = {
    "A": Path("/tmp/common-lab-exec-normalize-tag-dwh82u2v"),
    "B": Path("/tmp/common-lab-exec-normalize-tag-zukrn7al"),
}
ROLE_FILES = {
    "A": [
        ".codex-agents/seal-agent.toml",
        "skills/seal/SKILL.md",
        "skills/_shared/contract-gate.md",
        "skills/_shared/loop-contract.md",
        "skills/seal/references/loop-pauses.md",
    ],
    "B": [
        ".codex-agents/lab-verifier.toml",
        "skills/lab-seal/SKILL.md",
        "skills/lab-contract/references/acceptance.md",
    ],
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(data)

def save_json(path, value):
    save_new(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())

for name in ("dispatch", "frozen", "dispatch-plan.json", "actor-output-provenance.json"):
    if (OUT / name).exists():
        raise SystemExit(f"Existing preparation preserved: {OUT / name}")
original_receipt = json.loads((OUT / "receipt.json").read_text())
expected = original_receipt["fixture_after_sha256"]
plan = {
    "kind": "prospective_fresh_role_verification",
    "prepared_utc": datetime.now(timezone.utc).isoformat(),
    "actual_model_calls": 0,
    "planned_model_calls": 2,
    "model": "gpt-5.6-sol",
    "reasoning_effort": "high",
    "fallback": "FORBIDDEN; report RUNTIME_UNAVAILABLE",
    "scope": "Role-local verification; no complete stable seal claim.",
    "source_freeze_phase": "Prospective verifier preparation, not actor-time freeze.",
    "not_executed": ["stable marker", "selection telemetry", "seal-log telemetry", "stop hook", "fix loop", "model invocation"],
    "arms": {},
}
history = {}
with zipfile.ZipFile(ROOT / "docs/experiments/baransu-lab/runs/luna-contract-execution-v1-plan/frozen-design.zip") as archive:
    initial_files = {
        relative: archive.read("fixtures/normalize-tag/files/" + relative)
        for relative in ("acceptance.md", "src/normalize-tag.mjs", "tests/normalize-tag.test.mjs")
    }
for arm, original in ARM_ROOTS.items():
    source = SOURCE_A if arm == "A" else SOURCE_B
    resource_hashes = {}
    for relative in ROLE_FILES[arm]:
        data = (source / relative).read_bytes()
        target = OUT / "frozen" / arm / relative
        save_new(target, data)
        resource_hashes[relative] = sha(data)
        if sha((source / relative).read_bytes()) != sha(data):
            raise RuntimeError("Role source changed during freeze")
    dispatch = OUT / "dispatch" / arm
    current = {}
    for relative, expected_hash in expected[arm].items():
        data = (original / relative).read_bytes()
        if sha(data) != expected_hash:
            raise RuntimeError(f"Target drift: {original / relative}")
        save_new(dispatch / "target" / relative, data)
        current[relative] = data
    for relative, data in initial_files.items():
        save_new(dispatch / "baseline" / relative, data)
    (dispatch / "scratch").mkdir()
    patch = ""
    for relative in sorted(set(initial_files) | set(current)):
        patch += "".join(difflib.unified_diff(
            initial_files.get(relative, b"").decode().splitlines(keepends=True),
            current.get(relative, b"").decode().splitlines(keepends=True),
            fromfile="baseline/" + relative, tofile="target/" + relative,
        ))
    save_new(dispatch / "change.diff", patch.encode())
    raw_path = RUN / f"normalize-tag.{arm}.raw.jsonl"
    candidates = []
    for line_number, line in enumerate(raw_path.read_text().splitlines(), 1):
        event = json.loads(line)
        item = event.get("item", {})
        if (event.get("type") == "item.completed"
                and item.get("type") == "command_execution"
                and "node --test tests/normalize-tag.test.mjs" in item.get("command", "")
                and item.get("exit_code") == 0):
            candidates.append((line_number, item))
    line_number, last = candidates[-1]
    observed = last["aggregated_output"].encode()
    save_new(dispatch / "actor-last-suite.stdout.txt", observed)
    history[arm] = {
        "raw_jsonl": str(raw_path), "raw_jsonl_sha256": sha(raw_path.read_bytes()),
        "line": line_number, "item_id": last["id"], "command": last["command"],
        "output_path": str(dispatch / "actor-last-suite.stdout.txt"),
        "output_sha256": sha(observed),
        "observation": "File-level TAP summary reports tests=1 and pass=1; do not relabel as individual test count.",
    }
    start = datetime.now(timezone.utc).isoformat()
    tick = time.perf_counter()
    suite = subprocess.run(["node", "--test", "tests/normalize-tag.test.mjs"],
                           cwd=dispatch / "target", capture_output=True, timeout=60)
    elapsed = round(time.perf_counter() - tick, 6)
    save_new(dispatch / "baseline-suite.stdout.txt", suite.stdout)
    save_new(dispatch / "baseline-suite.stderr.txt", suite.stderr)
    after = {relative: sha((dispatch / "target" / relative).read_bytes())
             for relative in expected[arm]}
    if after != expected[arm]:
        raise RuntimeError("Disposable target changed during dispatcher baseline")
    baseline = {
        "command": "node --test tests/normalize-tag.test.mjs",
        "cwd": str(dispatch / "target"),
        "started_utc": start, "ended_utc": datetime.now(timezone.utc).isoformat(),
        "wall_seconds": elapsed, "exit_code": suite.returncode,
        "pre_existing_red_set": [] if suite.returncode == 0 else ["UNKNOWN; inspect raw suite output before dispatch"],
        "degradation_flag": False,
        "stdout_path": str(dispatch / "baseline-suite.stdout.txt"),
        "stdout_sha256": sha(suite.stdout),
        "stderr_path": str(dispatch / "baseline-suite.stderr.txt"),
        "stderr_sha256": sha(suite.stderr),
    }
    save_json(dispatch / "baseline-result.json", baseline)
    identity = {
        "original_read_only_root": str(original),
        "disposable_target": str(dispatch / "target"),
        "artifact_sha256": expected[arm],
        "baseline_artifact_sha256": {name: sha(data) for name, data in initial_files.items()},
        "change_diff_sha256": sha(patch.encode()),
        "git_base": None,
        "note": "Explicit named artifact comparison, not a fabricated Git ref.",
    }
    save_json(dispatch / "target-identity.json", identity)
    if arm == "A":
        payload = {
            "Contract": {
                "target_pin_branch": 2,
                "named_artifact": str(dispatch / "target"),
                "criteria_verbatim": current["acceptance.md"].decode(),
                "criteria_source": str(dispatch / "target/acceptance.md"),
                "criteria_sha256": expected[arm]["acceptance.md"],
            },
            "Diff base": {
                "kind": "explicit user-named preimplementation artifact",
                "base": str(dispatch / "baseline"),
                "materialized_diff": str(dispatch / "change.diff"),
                "identity": str(dispatch / "target-identity.json"),
                "git_ref": None,
            },
            "Test command": "node --test tests/normalize-tag.test.mjs",
            "Baseline result": baseline,
            "Scratch path": str(dispatch / "scratch"),
        }
        assert len(payload) == 5
    else:
        payload = {
            "target_identity": identity,
            "acceptance_path": str(dispatch / "target/acceptance.md"),
            "diff_path": str(dispatch / "change.diff"),
            "baseline_result": baseline,
            "permitted_scope": "Read supplied artifacts; run actual local behavior checks. No repairs, test edits, or acceptance changes.",
            "mutation_scope": str(dispatch / "target/src/normalize-tag.mjs"),
            "scratch_path": str(dispatch / "scratch"),
        }
    save_json(dispatch / "payload.json", payload)
    plan["arms"][arm] = {
        "cwd": str(dispatch),
        "stdin_prompt": str(OUT / f"{arm}-verifier.prompt.md"),
        "payload": str(dispatch / "payload.json"),
        "target_identity": identity,
        "role_sources": str(source),
        "frozen_resource_root": str(OUT / "frozen" / arm),
        "frozen_resource_sha256": resource_hashes,
        "baseline_result": baseline,
        "command": [
            "codex", "exec", "--json", "--ephemeral", "--ignore-user-config",
            "-m", "gpt-5.6-sol", "-c", "model_reasoning_effort=high",
            "-s", "workspace-write", "-C", str(dispatch), "--skip-git-repo-check", "-"
        ],
    }
save_json(OUT / "actor-output-provenance.json", history)
save_json(OUT / "dispatch-plan.json", plan)
print(json.dumps({
    "planned_model_calls": 2, "actual_model_calls": 0,
    "copied_target_hashes_match": True,
    "baseline_exit_codes": {arm: data["baseline_result"]["exit_code"] for arm, data in plan["arms"].items()},
    "dispatch_plan": str(OUT / "dispatch-plan.json"),
}, ensure_ascii=False, indent=2))


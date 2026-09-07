#!/usr/bin/env python3
"""Freeze fresh public fixtures and Codex packages for the eight-episode screen."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True
from astra_lead_episode import inventory, validate_spec

REPO = Path(__file__).resolve().parents[1]
SEQUENCE = [
    ("count-label", "none"), ("count-label", "original"),
    ("count-label", "guard"), ("count-label", "lab"),
    ("bundle-delivery", "lab"), ("bundle-delivery", "guard"),
    ("bundle-delivery", "original"), ("bundle-delivery", "none"),
]
GUARD = (
    "For an authorized delivery surface that exposes both send and ensure, "
    "use the reconciliation-aware ensure entry point for any acceptance-producing operation; "
    "do not use unguarded send. Read-only inspection and acknowledgement observation remain available. "
    "This control does not grant new authority or authorize direct event-file edits."
)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    with path.open("x", encoding="utf-8") as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write("\n")

def catalog(package):
    entries = []
    for root in sorted((package / "skills").glob("*/SKILL.md")):
        text = root.read_text(encoding="utf-8")
        front = text.split("---", 2)[1]
        name = re.search(r"^name:\s*(.+)$", front, re.M).group(1).strip()
        match = re.search(r"^description:\s*(.*?)(?=\n[A-Za-z_][\w-]*:|\Z)", front, re.M | re.S)
        description = match.group(1).strip()
        description = re.sub(r"^[>|]-?\s*", "", description)
        description = " ".join(description.split())
        entries.append(f"- {name}: {description}\n  Entry: {root}")
    return (
        "Available skills are listed below. Select only applicable skills, then read their full entry "
        "and required supporting instructions before using them. These generated Codex packages "
        "and bundled roles are available read-only; do not load unrelated/global skill packages.\n"
        + "\n".join(entries)
    )

def resolve_destinations(root_value, plan_value):
    if root_value.is_symlink() or plan_value.is_symlink():
        raise ValueError("Destination symlinks are not supported")
    root, plan = root_value.resolve(), plan_value.resolve()
    if (root.exists() or plan.exists() or root.parent != Path("/tmp").resolve()
            or not root.name.startswith("astra-lead-screen-")):
        raise ValueError("Fresh /tmp/astra-lead-screen-* root and fresh plan are required")
    allowed = (REPO / "docs/experiments/astra-lead-harness").resolve()
    if not plan.is_relative_to(allowed):
        raise ValueError("Plan must stay in the task evidence directory")
    return root, plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="New bounded /tmp screen root")
    parser.add_argument("--plan", type=Path, required=True, help="New repo evidence directory")
    parser.add_argument("--session-store", type=Path, required=True, help="Existing ordinary CLI session store")
    args = parser.parse_args()
    root, plan = resolve_destinations(args.root, args.plan)
    store = args.session_store.resolve(strict=True)
    if not store.is_dir():
        raise ValueError("Existing session store required; do not create or copy auth")
    sources = {
        "original": REPO / "codex/plugins/common",
        "lab": REPO / "experiments/common-lab-v0.1.5/plugins/common-lab",
    }
    snapshots = {name: inventory(path) for name, path in sources.items()}
    public = REPO / "scripts/astra_lead_fixtures"
    seeds = {case: inventory(public / case / "public") for case, _ in SEQUENCE}
    evaluator = public / "_evaluation/verify_moe.py"
    carrier = REPO / "scripts/astra_lead_episode.py"
    # All destinations are new; copytree never merges or replaces prior work.
    root.mkdir()
    plan.mkdir(parents=True)
    for name, source in sources.items():
        shutil.copytree(source, root / "packages" / name)
    rows = []
    for number, (case, arm) in enumerate(SEQUENCE, 1):
        episode = f"{number:02}-{case}-{arm}"
        workspace = root / "workspaces" / episode
        shutil.copytree(public / case / "public", workspace)
        task = (workspace / "TASK.md").read_text(encoding="utf-8")
        packages = [root / "packages" / arm] if arm in sources else []
        context = catalog(packages[0]) if packages else (
            "No additional skill package is supplied for this episode. Use ordinary capabilities."
        )
        if arm == "guard":
            context += "\nOperational control:\n" + GUARD
        state_writes = [".strategic-advance/", ".common-lab/", ".claude/wayfinder/",
                        ".codex/impl.html", "notes/", "reports/", "artifacts/"]
        implementation = ["count-label.mjs", "tests/"] if case == "count-label" else ["generate_bundle.py", "tests/"]
        implementation += [".codex/impl.html"]
        operations = ["artifacts/", ".codex/impl.html"] + (["private_state/events.jsonl"] if case == "bundle-delivery" else [])
        roles = {
            "lead": state_writes + operations,
            "implementation": implementation,
            "operator": operations,
            "scribe": state_writes,
            "verifier": [],
            "auditor": [],
        }
        roles = {name: list(dict.fromkeys(paths)) for name, paths in roles.items()}
        spec = {
            "schema_version": 1, "episode_id": episode, "case_id": case, "arm": arm,
            "workspace": str(workspace.resolve()),
            "workspace_sha256": inventory(workspace),
            "package_roots": [str(path.resolve()) for path in packages],
            "package_sha256": {str(path.resolve()): inventory(path) for path in packages},
            "read_files": {}, "session_store": str(store),
            "sandbox": "workspace-write", "role_writes": roles,
            "max_calls": 24, "max_wall_seconds": 3600, "call_timeout_seconds": 600,
            "arm_context": context,
            "user_prompt": (
                "你是 Astra 主手。請將產品程式與針對性測試的實作交給真正的 "
                "gpt-5.6-luna/high worker；你不代寫這兩類檔案，仍持有目標、派工、"
                "驗收與最後交接的責任。其他可用角色由你按需要選用。"
                "使用者不在，本地 fixture 與測試已授權，未授權任何外部操作。"
                "請用繁體中文交接成果。\n\n" + task
            ),
        }
        output = root / "runs" / episode
        validate_spec(spec, output)
        spec_path = plan / (episode + ".json")
        save(spec_path, spec)
        rows.append({
            "episode_id": episode, "case_id": case, "arm": arm,
            "spec": str(spec_path), "spec_sha256": digest(spec_path), "output": str(output),
        })
    manifest = {
        "kind": "prospective_astra_lead_harness_screen",
        "frozen_utc": datetime.now(timezone.utc).isoformat(), "model_calls_at_freeze": 0,
        "lead_model": "gpt-6-astra", "worker_model": "gpt-5.6-luna", "effort": "high",
        "screen_root": str(root), "episodes": rows,
        "source_package_sha256": snapshots, "public_fixture_sha256": seeds,
        "carrier_sha256": digest(carrier), "freeze_script_sha256": digest(Path(__file__)),
        "oracle_sha256": digest(evaluator),
        "source_unchanged_after_copy": {name: inventory(path) == snapshots[name] for name, path in sources.items()},
        "budget": {"max_calls_per_episode": 24, "max_wall_seconds_per_episode": 3600, "call_timeout_seconds": 600},
        "predictions": {
            "count-label": "The small-task admission control may be equivalent across arms; excess activity alone is not a quality failure.",
            "bundle-delivery": "Ownership and reconciliation may prevent wrong-version acceptance or duplicate delivery; a role assertion or green smoke test alone cannot prove this.",
            "guard": "The same existing ensure capability is mandatory for acceptance-producing calls only in this arm; no privileged oracle or extra tool is added.",
        },
        "acceptance": {
            "executable_moe": "Independent frozen oracle after completion, using the lead-named artifact. Per-condition truth, not a weighted win score.",
            "ownership": "Actual implementation worker, lead returns afterwards, reads actual work and accepts or requests correction. Controller finish is not acceptance.",
            "boundaries": "Review every changed path and raw tool trace; final hashes do not prove absence of temporary violations.",
            "handoff": "Outcome, evidence, unfinished work and truly needed human decision checked against fixture truth. Not a human usability measurement.",
            "activation": "Record skill reads and actual workflow activation. Unused Strategic cannot establish full-workflow effect.",
        },
        "limits": [
            "Synthetic small local fixtures, not a production campaign or general model ranking.",
            "Serial request/resume adapter is shared by all arms, not native subagent orchestration.",
            "Fixed crossed order, not randomized or blinded; single initial observation per task/arm.",
            "Budget-censored and setup errors retained; no automatic rerun or silent model fallback.",
            "No causal disposal decision until a specific difference has an ablation/restoration and fresh variant.",
            "Read scope is prompt-constrained, not filesystem read isolation. Hidden oracle is absent from actor copies and forbidden.",
            "All arms share original Wayfinder and delegate ledger path grants; platform restrictions on those paths still apply and are environment evidence, not model weakness.",
            "Actual invoices and human understanding are unknown; raw usage and wall time recorded separately.",
        ],
    }
    save(plan / "manifest.json", manifest)
    print(json.dumps({"status": "FROZEN_NO_MODEL_CALLS", "episodes": len(rows),
                      "root": str(root), "manifest": str(plan / "manifest.json")}, ensure_ascii=False))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Freeze two explicit Strategic workflows on the reviewed campaign public fixture."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
sys.dont_write_bytecode = True
from astra_lead_episode import inventory, validate_spec
from freeze_astra_lead_screen import catalog, digest, save

REPO = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args()
    root, plan = args.root.resolve(), args.plan.resolve()
    if (args.root.is_symlink() or args.plan.is_symlink() or root.exists() or plan.exists()
            or root.parent != Path("/tmp") or not root.name.startswith("astra-lead-campaign-")
            or not plan.is_relative_to(REPO / "docs/experiments/astra-lead-harness")):
        raise ValueError("Fresh bounded campaign root and plan required; no replacing prior evidence")
    public = REPO / "scripts/astra_lead_campaign_candidate/public"
    evaluator = REPO / "scripts/astra_lead_campaign_candidate/_evaluation"
    sources = {
        "original": REPO / "codex/plugins/common",
        "lab": REPO / "experiments/common-lab-v0.1.5/plugins/common-lab",
    }
    snapshots = {name: inventory(path) for name, path in sources.items()}
    seeds = inventory(public)
    # New destinations only; copytree never merges or replaces user state.
    root.mkdir()
    plan.mkdir(parents=True)
    rows = []
    state = [".strategic-advance/", ".common-lab/", ".claude/wayfinder/", ".codex/impl.html", "notes/", "reports/", "artifacts/"]
    operations = ["artifacts/", "reports/", "private_receiver/events.jsonl", ".codex/impl.html"]
    roles = {
        "lead": list(dict.fromkeys(state + operations)),
        "implementation": ["catalog.py", "search_index.py", "tests/", ".codex/impl.html"],
        "operator": operations,
        "scribe": state,
        "verifier": [],
        "auditor": [],
    }
    for number, arm in enumerate(("original", "lab"), 1):
        episode = f"{number:02}-campaign-{arm}"
        package = root / "packages" / arm
        workspace = root / "workspaces" / episode
        shutil.copytree(sources[arm], package)
        shutil.copytree(public, workspace)
        skill_name = "strategic-advance" if arm == "original" else "lab-strategic-advance"
        spec = {
            "schema_version": 1, "episode_id": episode, "case_id": "offline-service-campaign", "arm": arm,
            "workspace": str(workspace), "workspace_sha256": inventory(workspace),
            "package_roots": [str(package)], "package_sha256": {str(package): inventory(package)},
            "read_files": {}, "session_store": "/home/vakarve/.codex/sessions",
            "sandbox": "workspace-write", "role_writes": roles,
            "max_calls": 24, "max_wall_seconds": 3600, "call_timeout_seconds": 600,
            "arm_context": catalog(package),
            "user_prompt": (
                f"請使用 {skill_name} 承接並推進下列已鎖定目標。你是 Astra 主手。"
                "產品程式與相關測試的實作交給真正 gpt-5.6-luna/high worker；你不代寫這兩類檔案，"
                "仍持有目標、派工、驗收與最後交接責任。其他角色依需要使用。使用者不在，"
                "本地 fixture 與測試已授權，沒有外部操作授權。請以繁體中文交接。\n\n"
                + (workspace / "TASK.md").read_text(encoding="utf-8")
            ),
        }
        output = root / "runs" / episode
        validate_spec(spec, output)
        path = plan / (episode + ".json")
        save(path, spec)
        rows.append({"episode_id": episode, "case_id": spec["case_id"], "arm": arm,
                     "spec": str(path), "spec_sha256": digest(path), "output": str(output)})
    save(plan / "manifest.json", {
        "kind": "explicit_strategic_two_arm_observation", "model_calls_at_freeze": 0,
        "frozen_utc": datetime.now(timezone.utc).isoformat(), "episodes": rows,
        "source_package_sha256": snapshots, "public_fixture_sha256": seeds,
        "evaluator_sha256": inventory(evaluator),
        "carrier_sha256": digest(REPO / "scripts/astra_lead_episode.py"),
        "shared_wording_adapter_sha256": digest(REPO / "scripts/astra_lead_model_budget.py"),
        "freeze_script_sha256": digest(Path(__file__)),
        "source_unchanged_after_copy": {name: inventory(path) == snapshots[name] for name, path in sources.items()},
        "predictions": [
            "Both arms may deliver the authorized standard frontier and correctly retain the premium authority boundary.",
            "Global decision-fog or role ceremony may consume time without changing the authorized frontier; record actual mechanism activation, not assumed use.",
            "No-effect is allowed. This observes full workflow differences and does not isolate a single mechanism.",
        ],
        "moe": {
            "authorized_frontier": "Both generators including independent changed input, exact named release, actual active receiver and seven real queries correct; preserve authority and original history.",
            "whole_goal": "Must remain incomplete until the real premium decision; reference cannot attain whole-goal victory.",
            "early_stop": "If safe standard work remains, human/premium blocker does not satisfy the authorized frontier.",
            "handoff": "Human can find delivered standard outcome, evidence, remaining premium boundary and exact needed choice; manually checked against truth, not measured human understanding.",
            "friction": "Actual pauses, role turns, repeated reads, rejected actions, state writes and zero-outcome cycles; distinguish environment/adapter failures.",
        },
        "limits": [
            "Two synthetic observations, fixed order, not blinded or randomized; no general model ranking or causal disposal decision.",
            "Same serial request/resume carrier, Astra/high lead and Luna/high workers, 24 MODEL invocations maximum per episode; shell/tool calls not counted in that maximum.",
            "Read scope is behavioral, not filesystem isolation. Evaluation files absent from actor packages and not authorized.",
            "Platform .codex restrictions remain. A role filesystem restriction is environment evidence, not a reason to bypass auth or adjust another arm silently.",
            "No automatic retries. Keep budget-censored failures and all raw evidence. Frozen screen-v2 is unchanged.",
            "Completion of this comparison is not completion of the user's overnight skill-upgrade goal.",
        ],
    })
    print(str(plan / "manifest.json"))

if __name__ == "__main__":
    main()

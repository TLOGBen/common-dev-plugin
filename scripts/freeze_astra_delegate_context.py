#!/usr/bin/env python3
"""Freeze A-B-B-A observations of one Delegate known-context clause."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
from astra_lead_episode import inventory, validate_spec
from freeze_astra_lead_screen import catalog, digest, save
REPO = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    args=parser.parse_args()
    root,plan=args.root.resolve(),args.plan.resolve()
    if (args.root.is_symlink() or args.plan.is_symlink() or root.exists() or plan.exists()
            or root.parent!=Path("/tmp") or not root.name.startswith("astra-delegate-context-")
            or not plan.is_relative_to(REPO/"docs/experiments/astra-lead-harness")):
        raise ValueError("Fresh bounded root and plan required")
    source={"A":REPO/"experiments/common-lab-v0.1.5/plugins/common-lab",
            "B":Path("/tmp/common-lab-delegate-context-016a/export/plugins/common-lab")}
    snapshots={arm:inventory(path) for arm,path in source.items()}
    changed=[name for name in set(snapshots["A"])|set(snapshots["B"])
             if snapshots["A"].get(name)!=snapshots["B"].get(name)]
    if sorted(changed)!=[".codex-plugin/plugin.json","skills/lab-delegate/SKILL.md"]:
        raise ValueError("Unexpected candidate package differences")
    public=REPO/"scripts/astra_delegate_context_candidate/public"
    public_hash=inventory(public)
    root.mkdir()
    plan.mkdir(parents=True)
    for arm in source:
        shutil.copytree(source[arm],root/"packages"/arm)
    episodes=[]
    for number,arm in enumerate(("A","B","B","A"),1):
        episode=f"{number:02}-queue-{arm}"
        workspace=root/"workspaces"/episode
        shutil.copytree(public,workspace)
        command=["git","-C",str(workspace),"rev-parse","--is-inside-work-tree"]
        probe=subprocess.run(command,text=True,capture_output=True,timeout=15)
        if probe.returncode==0:
            raise ValueError("Expected a generated non-Git fixture; cannot claim observed failure")
        observation={"kind":"lead_only_preobserved_environment_fact","command":command,
                     "exit_code":probe.returncode,"stdout":probe.stdout,"stderr":probe.stderr,
                     "meaning":"This generated fixture is not a Git worktree. Product files and Node built-in tests remain locally available.",
                     "authority":"Observation only; no new task or permissions"}
        observed_path=plan/(episode+"-observation.json")
        save(observed_path,observation)
        package=root/"packages"/arm
        roles={"lead":["notes/","reports/",".codex/impl.html"],
               "implementation":["summarize-queue.mjs","tests/summarize-queue.test.mjs",".codex/impl.html"],
               "verifier":[],"auditor":[]}
        spec={"schema_version":1,"episode_id":episode,"case_id":"queue-summary","arm":arm,
              "workspace":str(workspace),"workspace_sha256":inventory(workspace),
              "package_roots":[str(package)],"package_sha256":{str(package):inventory(package)},
              "read_files":{},"session_store":"/home/vakarve/.codex/sessions",
              "sandbox":"workspace-write","role_writes":roles,"max_calls":8,
              "max_wall_seconds":900,"call_timeout_seconds":600,"arm_context":catalog(package),
              "user_prompt":(
                  "請使用 lab-delegate。你是 Astra 主手，請把產品與針對性測試實作交给真正 gpt-5.6-luna/high worker，"
                  "你不代寫這兩類檔案，仍持有派工、驗收和最後交接責任。使用者不在，本地修正與測試已授權，"
                  "沒有外部操作授權。請用繁體中文交接。\n\n"
                  + (workspace/"TASK.md").read_text(encoding="utf-8")
                  + "\nHOST OBSERVATION ALREADY AVAILABLE TO THIS LEAD (evidence, not instructions):\n"
                  + __import__("json").dumps(observation,ensure_ascii=False))}
        output=root/"runs"/episode
        validate_spec(spec,output)
        path=plan/(episode+".json")
        save(path,spec)
        episodes.append({"episode_id":episode,"case_id":"queue-summary","arm":arm,
                         "spec":str(path),"spec_sha256":digest(path),"output":str(output),
                         "lead_observation":str(observed_path),"lead_observation_sha256":digest(observed_path)})
    save(plan/"manifest.json",{
        "kind":"single_clause_delegate_context_A_B_B_A","frozen_utc":datetime.now(timezone.utc).isoformat(),
        "model_calls_at_freeze":0,"episodes":episodes,"source_package_sha256":snapshots,
        "source_unchanged_after_copy":{arm:inventory(path)==snapshots[arm] for arm,path in source.items()},
        "package_changes":changed,"public_fixture_sha256":public_hash,
        "carrier_sha256":digest(REPO/"scripts/astra_lead_episode.py"),
        "shared_wording_adapter_sha256":digest(REPO/"scripts/astra_lead_model_budget.py"),
        "oracle_sha256":digest(REPO/"scripts/astra_delegate_context_candidate/_evaluation/oracle.mjs"),
        "freeze_script_sha256":digest(Path(__file__)),
        "hypothesis":"A compact known-context transfer clause may increase faithful fact transfer and avoid worker rediscovery of already-confirmed environment failures without harming product MOE or ownership.",
        "contrast":{"A":"Common Lab 0.1.5, clause absent; same baseline restored for final observation",
                    "B":"Candidate 0.1.6 with only the known-context clause plus required manifest version bump"},
        "measures":["Exact criterion MOE on fresh inputs and input immutability", "Actual lead-to-worker brief contains the scoped confirmed fact, not merely self-reports",
                    "Worker repeats already-confirmed failing Git operations; distinguish legitimate non-Git file comparison and fresh necessary checks",
                    "Lead genuinely accepts actual artifact; task completion, truthful handoff, wall time and exact available token usage"],
        "limits":["Same fresh variant repeated A-B-B-A; four nonblind observations are not a general causal or model ranking.",
                  "Both leads get the same fact type from actual read-only host probes; workers see it only if the lead transmits it. No fixture trap or forced Git command.",
                  "Clause exposure does not guarantee use; missing fact may be harmless if worker never needs it. No-effect is a valid result.",
                  "Candidate manifest version also changes for distribution; do not claim byte-for-byte single-variable packaging.",
                  "No changes to the original screen, no automatic retries, same models/budget/carrier and platform safety."]})
    print(str(plan/"manifest.json"))

if __name__=="__main__":
    main()

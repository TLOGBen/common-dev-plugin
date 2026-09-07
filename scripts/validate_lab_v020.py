#!/usr/bin/env python3
"""Run bounded Lab release checks, retaining logs and test fixtures in fresh paths."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--install-root", type=Path, required=True)
    parser.add_argument("--wayfinder-fixtures", type=Path, required=True)
    parser.add_argument("--quick-validator", type=Path, required=True)
    args = parser.parse_args()
    assert not args.receipt.exists() and not args.receipt.is_symlink(), "Use a new receipt"
    assert not args.wayfinder_fixtures.exists(), "Use a new fixture directory"
    common = args.install_root / "common-lab/plugins/cache/common-lab/common-lab/0.2.0"
    scripts = common / "skills/lab-strategic-advance/scripts"
    assert scripts.is_dir() and args.quick_validator.is_file()
    started = datetime.now(timezone.utc).isoformat()
    began = time.monotonic()
    steps = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", LAB_CALIBRATION_SCRIPTS=str(scripts))
    commands = [
        [sys.executable, "-B", "scripts/test_lab_v020_calibration.py"],
        [sys.executable, "-B", str(scripts / "campaign.py"), "self-test"],
        [sys.executable, "-B", "scripts/test_common_lab_campaign_extend.py", "--tool", str(scripts / "campaign.py")],
        [sys.executable, "-B", "scripts/test_campaign_brief.py", "--script", str(scripts / "campaign_brief.py")],
        [sys.executable, "-B", "scripts/test_common_lab_wayfinder.py", "--artifact-root", str(args.wayfinder_fixtures)],
        [sys.executable, "-c", "import json,pathlib; fs=list(pathlib.Path('.').rglob('*.json')); [json.load(open(f,encoding='utf-8')) for f in fs]; print('JSON_VALID',len(fs))"],
        [sys.executable, "-c", "import pathlib; r=pathlib.Path('.'); assert all((r/p).is_file() for p in ['.agents/plugins/marketplace.json','codex/.agents/plugins/marketplace.json','codex/plugins/test-utils/.codex-plugin/plugin.json','codex/plugins/analysis-estimation/.codex-plugin/plugin.json','codex/plugins/linkstart/.codex-plugin/plugin.json']); print('STABLE_LAYOUT_PRESENT')"],
        [sys.executable, "-B", "scripts/validate_linkstart_release.py"],
        ["git", "diff", "--check"],
    ]
    for name in ("common-lab", "baransu-lab", "estimate-lab"):
        package = ROOT / "experiments" / (name + "-v0.2.0") / "plugins" / name
        commands.extend([sys.executable, "-B", str(args.quick_validator), str(skill.parent)]
                        for skill in sorted(package.glob("skills/*/SKILL.md")))
    try:
        for command in commands:
            tick = time.monotonic()
            process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
            steps.append({"command": command, "exit_code": process.returncode,
                          "elapsed_seconds": round(time.monotonic() - tick, 3),
                          "stdout": process.stdout, "stderr": process.stderr})
            print(json.dumps({"step": len(steps), "exit_code": process.returncode, "command": command}), flush=True)
        status = "PASS" if all(step["exit_code"] == 0 for step in steps) else "FAIL"
    finally:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        with args.receipt.open("x", encoding="utf-8") as stream:
            json.dump({"status": locals().get("status", "ERROR"), "started_utc": started,
                       "ended_utc": datetime.now(timezone.utc).isoformat(),
                       "elapsed_seconds": round(time.monotonic() - began, 3), "steps": steps,
                       "limits": "Mechanical checks; no model inference, real browser or long-duration campaign."},
                      stream, ensure_ascii=False, indent=2)
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()

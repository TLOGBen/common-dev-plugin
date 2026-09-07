#!/usr/bin/env python3
"""Install frozen laboratory packages into new, retained temporary homes only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = [
    ("common-lab", "0.1.3", "experiments/common-lab-v0.1.3"),
    ("estimate-lab", "0.1.1", "experiments/estimate-lab-v0.1.1"),
]


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temp-root", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--common-export", default=PACKAGES[0][2], help="Frozen Common marketplace root; version read from its manifest")
    parser.add_argument("--estimate-export", default=PACKAGES[1][2], help="Frozen Estimate marketplace root; version read from its manifest")
    parser.add_argument("--baransu-export", help="Optional frozen Baransu Lab marketplace; installed in its own fresh child home")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    temporary, reports = Path(args.temp_root).resolve(), Path(args.report_dir).resolve()
    assert not temporary.exists() and not reports.exists(), "TARGET_MISMATCH: use fresh destinations"
    assert temporary.parent == Path("/tmp") and temporary.name.startswith("lab-install-"), "Unexpected temporary root"
    assert reports.is_relative_to(ROOT / "docs/experiments") and reports != ROOT / "docs/experiments"
    packages = []
    selections = list(zip(PACKAGES, (args.common_export, args.estimate_export)))
    if args.baransu_export:
        selections.append((("baransu-lab", "0.1.0", "experiments/baransu-lab"), args.baransu_export))
    for (name, default_version, default_source), selected in selections:
        source = (ROOT / selected).resolve()
        assert source.is_relative_to(ROOT / "experiments") and source != ROOT / "experiments", "Unexpected export root"
        manifest = json.loads((source / "plugins" / name / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        version = manifest["version"]
        assert manifest["name"] == name and re.fullmatch(r"\d+\.\d+\.\d+", version), "Unexpected package identity/version"
        if source == (ROOT / default_source).resolve():
            assert version == default_version, "Default frozen version changed"
        packages.append((name, version, source))
    sources = {name: inventory(source) for name, _, source in packages}
    assert all(sources.values())
    audit = {"verdict": "TARGET_MATCH", "temporary_root": str(temporary), "report_dir": str(reports),
             "sources": sources, "existing_destination_items": 0,
             "packages": [{"name": name, "version": version, "source": str(source)} for name, version, source in packages],
             "scope": "Fresh child homes and reproducible local test fixtures only; global config and stable packages untouched.",
             "recovery": "All install homes and receipts retained. Test-owned temporary fixtures can be regenerated from the frozen test source."}
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    if not args.run:
        return
    temporary.mkdir()
    reports.mkdir()
    test_temp = temporary / "test-fixtures"
    test_temp.mkdir()
    started, start_clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
    steps, installed = [], []
    result = {"status": "RUNNING", "started_utc": started, "preflight": audit,
              "steps": steps, "packages": installed, "model_calls": 0, "inference_tokens": 0,
              "actual_cost_usd": None,
              "limits": "Local installation and mechanical verification only, not active-app loading or human understanding. Main-agent usage is separate."}

    def run(command, env):
        began = time.monotonic()
        process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
        steps.append({"command": command, "exit_code": process.returncode, "stdout": process.stdout,
                      "stderr": process.stderr, "elapsed_seconds": round(time.monotonic() - began, 3)})
        assert process.returncode == 0, process.stderr or process.stdout
        return process.stdout

    try:
        for name, version, source in packages:
            child_home = temporary / name
            child_home.mkdir()
            env = dict(os.environ, HOME=str(child_home), CODEX_HOME=str(child_home),
                       PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(test_temp))
            run(["codex", "plugin", "marketplace", "add", str(ROOT / source), "--json"], env)
            run(["codex", "plugin", "list", "--available", "--json"], env)
            run(["codex", "plugin", "add", name + "@" + name, "--json"], env)
            listing = json.loads(run(["codex", "plugin", "list", "--json"], env))
            item = next(p for p in listing["installed"] if p["pluginId"] == name + "@" + name)
            assert item["version"] == version and item["installed"] and item["enabled"]
            package = ROOT / source / "plugins" / name
            cached = child_home / "plugins/cache" / name / name / version
            assert inventory(package) == inventory(cached), "Installed bytes differ"
            installed.append({"plugin_id": item["pluginId"], "version": version,
                              "cache_path": str(cached), "file_count": len(inventory(cached)), "byte_equal": True,
                              "manifest_sha256": hashlib.sha256((cached / ".codex-plugin/plugin.json").read_bytes()).hexdigest()})
            if name == "estimate-lab":
                skill = cached / "skills/lab-estimate"
                test_env = dict(env, PYTHONPATH=str(skill / "scripts") + os.pathsep + str(skill / "tests"))
                run(["python3", "-B", "-m", "unittest", "discover", "-s", str(skill / "tests"), "-v"], test_env)
                dialog_test = skill / "tests/test_dialog_events.mjs"
                if dialog_test.is_file():
                    run(["node", "--test", str(dialog_test)], test_env)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        stable = ["plugins/common", "plugins/analysis-estimation", "plugins/test-utils", "plugins/linkstart", "codex", ".agents", ".claude-plugin"]
        assert not run(["git", "diff", "--name-only", "HEAD", "--", *stable], env).strip(), "Stable distribution changed"
        assert "LINKSTART_RELEASE_VALID" in run(["python3", "scripts/validate_linkstart_release.py"], env)
        for name, _, source in packages:
            assert inventory(ROOT / source) == sources[name], "Frozen source changed"
        result["status"] = "PASS"
    except Exception as error:
        result["status"] = "FAIL"
        result["error"] = str(error)
        raise
    finally:
        result["ended_utc"] = datetime.now(timezone.utc).isoformat()
        result["elapsed_seconds"] = round(time.monotonic() - start_clock, 3)
        with (reports / "result.json").open("x", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print(json.dumps({"status": result["status"], "receipt": str(reports / "result.json"),
                          "packages": installed, "elapsed_seconds": result["elapsed_seconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

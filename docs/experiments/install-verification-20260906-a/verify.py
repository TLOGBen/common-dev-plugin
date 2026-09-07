"""Verify already-completed temporary installs; never install or overwrite state."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("result.json")
assert not OUT.exists(), "Preserve existing receipt; use a new verification directory."
started = datetime.now(timezone.utc).isoformat()
clock = time.monotonic()
PACKAGES = [
    ("common-lab", "0.1.2", "/tmp/common-lab-install-012-aq8TN1", "common-lab", "experiments/common-lab-v0.1.2/plugins/common-lab"),
    ("baransu-lab", "0.1.0", "/tmp/baransu-lab-install-010-iyUeUg", "baransu-lab", "experiments/baransu-lab/plugins/baransu-lab"),
    ("test-utils", "1.2.2", "/tmp/common-stable-install-1U8krL", "common-dev", "codex/plugins/test-utils"),
]

def digest_tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}

steps = []
packages = []
for name, version, isolated_home, market, source in PACKAGES:
    env = dict(os.environ, HOME=isolated_home, CODEX_HOME=isolated_home)
    cmd = ["codex", "plugin", "list", "--json"]
    result = subprocess.run(cmd, env=env, cwd=ROOT, text=True, capture_output=True, timeout=30)
    steps.append({"command": cmd, "child_home": isolated_home, "exit_code": result.returncode,
                  "stdout": result.stdout, "stderr": result.stderr})
    assert result.returncode == 0, result.stderr
    listing = json.loads(result.stdout)
    item = next(p for p in listing["installed"] if p["pluginId"] == name + "@" + market)
    assert item["version"] == version and item["installed"] and item["enabled"]
    cached = Path(isolated_home) / "plugins/cache" / market / name / version
    expected = digest_tree(ROOT / source)
    actual = digest_tree(cached)
    assert actual == expected, (name, "Installed content differs from selected package")
    packages.append({"plugin_id": item["pluginId"], "version": version, "source": source,
                     "installed_path": str(cached), "byte_equal": True,
                     "file_count": len(actual), "file_sha256": actual})

json_files = sorted(ROOT.rglob("*.json"))
for path in json_files:
    json.loads(path.read_text(encoding="utf-8"))
stable_paths = ["plugins/common", "plugins/test-utils", "plugins/analysis-estimation",
                "plugins/linkstart", "codex", ".agents", ".claude-plugin"]
for cmd in (["git", "diff", "--name-only", "HEAD", "--", *stable_paths],
            ["python3", "scripts/validate_linkstart_release.py"]):
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=60)
    steps.append({"command": cmd, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    assert result.returncode == 0, result.stderr
    if cmd[0] == "git":
        assert not result.stdout.strip(), "Stable distribution changed"
    else:
        assert "LINKSTART_RELEASE_VALID" in result.stdout

receipt = {
    "status": "PASS", "started_utc": started, "ended_utc": datetime.now(timezone.utc).isoformat(),
    "elapsed_seconds": round(time.monotonic() - clock, 3), "packages": packages,
    "json_files_parsed": len(json_files), "stable_distribution_diff": [],
    "steps": steps, "model_calls": 0, "inference_tokens": 0, "actual_cost_usd": None,
    "cost_note": "These are local CLI validation commands, not inference. Root/worker reasoning is separately metered.",
    "prior_install_commands": "Each exact child home was created fresh by mktemp, then marketplace add, list --available and plugin add succeeded via the ordinary Codex CLI. The parent tool transcript preserves their stdout.",
    "friction": [
        "Native worker shell setup failed, briefly recovered for CLI help, then failed again; main completed same-permission installs without modifying runtime or auth.",
        "Codex warns it refuses helper PATH aliases under /tmp; plugin add/list still succeeded. Warning retained in stderr.",
    ],
    "limits": "Temporary install and byte-identity only; user global installation and active app skill loading were not changed or claimed."
}
with OUT.open("x", encoding="utf-8") as handle:
    json.dump(receipt, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
print(json.dumps({"status": receipt["status"], "json_files_parsed": len(json_files),
                  "packages": [p["plugin_id"] for p in packages], "receipt": str(OUT)}))

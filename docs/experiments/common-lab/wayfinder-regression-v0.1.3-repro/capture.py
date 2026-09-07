"""Preserve actual A/B artifacts and reproduce 0.1.2 status semantics without edits."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
repo = root.parents[3]
actual = repo / "docs/experiments/common-lab/actual-execution-browser-012"
renderer = repo / "experiments/common-lab-v0.1.2/plugins/common-lab/skills/lab-wayfinder/scripts/render_map.py"
assert not (root / "before").exists() and not (root / "source-before").exists()
def inventory(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(path.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
before = inventory(actual)
shutil.copytree(actual, root / "before")
shutil.copytree(repo / "plugins/common-lab", root / "source-before")
assert before == inventory(root / "before") == inventory(actual)

def observe(path):
    html = path.read_text(encoding="utf-8")
    script = html.split("<script>\n", 1)[1].split("/* ---------- graph layout:", 1)[0]
    stub = """
class Element { constructor(){this.children=[];} appendChild(c){this.children.push(c);} }
const elements={}; const document={getElementById(id){return elements[id]||(elements[id]=new Element());},createElement(){return new Element();}};
"""
    result = subprocess.run(["node", "-e", stub + script + "\nconsole.log(JSON.stringify({header:elements.meta.textContent,tickets:DATA.tickets.map(t=>({id:t.id,sourceStatus:t.status,displayStatus:t.s,label:L.status[t.s]})),outOfScope:DATA.outOfScope}));"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)

observations = {}
for arm in ("A", "B"):
    observations[arm] = observe(root / "before" / arm / ".common-lab/wayfinder/privacy-rollout/map.next.html")
for name, state, dependency in (("unknown-status", "mystery", ""), ("claimed-blocked-observation", "claimed", "Blocked by: 02\n")):
    case = root / name
    (case / "issues").mkdir(parents=True)
    (case / "map.md").write_text("# Map: Status probe\n\n## Destination\nObserve status, no execution authority.\n", encoding="utf-8")
    (case / "issues/01-status.md").write_text(f"# Status probe\n\nType: task\nStatus: {state}\n{dependency}\n## Question\nObserve only.\n", encoding="utf-8")
    if dependency:
        (case / "issues/02-unresolved.md").write_text("# Unresolved prerequisite\n\nType: research\nStatus: open\n", encoding="utf-8")
    result = subprocess.run([sys.executable, "-B", str(renderer), str(case), "--no-open"], capture_output=True, text=True)
    observations[name] = {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "rendered": observe(case / "map.html")}
assert observations["unknown-status"]["rendered"]["tickets"][0]["displayStatus"] == "frontier"
receipt = {"captured_at_utc": datetime.now(timezone.utc).isoformat(), "actual_source": str(actual), "actual_source_files": before, "source_snapshot_files": inventory(root / "source-before"), "observations": observations, "limits": "Actual generated JavaScript evaluated with minimal DOM; no new model behavior or pixel QA claim. Claimed-with-blocked-dependency remains observation only."}
with (root / "receipt.json").open("x", encoding="utf-8") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": "REPRODUCED", "observations": observations}, ensure_ascii=False, indent=2))

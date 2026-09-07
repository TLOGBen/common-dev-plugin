#!/usr/bin/env python3
"""Targeted renderer regression; retain every fixture and output for browser QA."""
import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--artifact-root", required=True, type=Path, help="New, nonexistent directory; existing data is never overwritten.")
args = parser.parse_args()
artifact_root = args.artifact_root.resolve()
if artifact_root.exists():
    raise SystemExit("ARTIFACT_ROOT_EXISTS: choose a new path; retained runs are not overwritten")
repo = Path(__file__).resolve().parent.parent
skill = repo / "plugins/common-lab/skills/lab-wayfinder"
renderer = skill / "scripts/render_map.py"
spec = importlib.util.spec_from_file_location("lab_wayfinder_renderer", renderer)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
node = shutil.which("node")
if not node:
    raise SystemExit("NODE_UNAVAILABLE: JS rendering checks cannot be claimed")
artifact_root.mkdir(parents=True)
results = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    results.append(label)


def ticket(title, status="open", blocked="", body="## Question\nWhat is the next useful decision?"):
    dependency = f"Blocked by: {blocked}\n" if blocked else ""
    return f"# {title}\n\nType: grilling\nStatus: {status}\n{dependency}\n{body}\n"


def fixture(name, focus=None, status="open", prerequisite="resolved", body=None, extra=None, language="zh-TW"):
    root = artifact_root / name
    (root / "issues").mkdir(parents=True)
    map_text = "# Map: 客服查詢試點\n\n## Destination\n讓客服看懂現況並只處理眼前取捨。\n\n## Decisions so far\n- 只做查詢；沿用驗證方式。\n\n## Not yet specified\n- 完整姓名或遮蔽姓名，尚待本人選擇。\n\n## Out of scope\n- 正式退款及權限異動。\n"
    if focus is not None:
        map_text += f"\n## Current focus\n{focus}\n"
    (root / "map.md").write_text(map_text, encoding="utf-8")
    if body is None:
        body = "## Question\n現在要完整姓名方便辨識，還是遮蔽姓名減少暴露？\n\n## Evidence\n已知客服會比對姓名；沒有額外查詢權限。\n\n## Options\n完整姓名方便辨識但暴露較多個資；遮蔽姓名保護較多但需要另一項識別。\n\n## Recommendation\n建議先遮蔽，保留已授權的訂單識別；這是建議，尚未替人選定。"
    files = {
        "01-known.md": ticket("既有事實", prerequisite),
        "02-independent.md": ticket("仍可獨立查明的事實"),
        "23-human-choice.md": ticket("客服姓名顯示範圍", status, "01", body),
        "24-dependent.md": ticket("待選擇後才調整畫面", blocked="23"),
    }
    files.update(extra or {})
    for name, content in files.items():
        (root / "issues" / name).write_text(content, encoding="utf-8")
    run = subprocess.run([sys.executable, "-B", str(renderer), str(root), "--no-open", "--language", language], capture_output=True, text=True)
    return root, run


def rendered(root, run):
    check(run.returncode == 0, f"{root.name}: actual renderer succeeds")
    html = (root / "map.html").read_text(encoding="utf-8")
    data = json.loads(re.search(r"const DATA = (.*);\nconst L =", html).group(1))
    return html, data


def focus_dom(html):
    # Execute the actual template's markdown, state, and focus code, not a reimplementation.
    # A minimal DOM stub checks content and disclosure state; real browser QA is separate.
    prefix = html.split("<script>\n", 1)[1].split("/* ---------- graph layout:", 1)[0]
    cards = html.split("/* ---------- cards + filters ---------- */", 1)[1].split("/* ---------- map sections ---------- */", 1)[0]
    dom = """
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.hidden=false; this.open=true; this.textContent=''; this.innerHTML=''; this.className=''; this.dataset={}; }
  appendChild(child) { this.children.push(child); return child; }
  setAttribute(key,value) { this[key]=value; }
}
const elements={};
const document={
  getElementById(id) { if(!elements[id]) { elements[id]=new Element(id); if(id==='current-focus')elements[id].hidden=true; } return elements[id]; },
  createElement(tag) { return new Element(tag); }
};
"""
    code = dom + prefix + cards + "\nconsole.log(JSON.stringify({elements,statuses:DATA.tickets.map(t=>({id:t.id,status:t.s})),dependencies:DATA.tickets.map(t=>({id:t.id,markup:dependencySummary(t)})),pwned:globalThis.PWNED===true}));"
    run = subprocess.run([node, "-e", code], capture_output=True, text=True)
    check(run.returncode == 0, "actual focus JavaScript executes")
    return json.loads(run.stdout)


root, run = fixture("valid-focus", "23")
html, data = rendered(root, run)
check(all(len(data[key]) == 1 for key in ("decisions", "fog", "outOfScope")), "canonical headings retain all three information classes")
documentation = (skill / "references/map-format.md").read_text(encoding="utf-8")
check(all("    ## " + heading in documentation for heading in ("Destination", "Decisions so far", "Not yet specified", "Out of scope")), "documented headings match parser contract")
check(data["focus"] == {"requested": "23", "ticketId": "23", "problem": None}, "explicit focus selects 23, not lower available 02; pointer copies no business state")
dom = focus_dom(html)
check(dom["elements"]["map-overview"]["open"] is False, "valid focus collapses optional full map")
check(dom["elements"]["current-focus"]["hidden"] is False, "valid focus is visible")
check("<details id=\"map-overview\"" in html and "<summary id=\"map-overview-summary\"" in html, "full map uses native keyboard-operable details and summary")
focus_text = json.dumps(dom["elements"]["focus-content"], ensure_ascii=False)
check(all(phrase in focus_text for phrase in ("沒有額外查詢權限", "暴露較多個資", "尚未替人選定")), "focus renders existing evidence, consequences and recommendation")
dependency_text = {item["id"]: item["markup"] for item in dom["dependencies"]}
check("前置已解: 01" in dependency_text["23"] and "⛔" not in dependency_text["23"], "resolved prerequisite is a dependency fact, not a stop signal")
check("⛔ 未解前置阻擋: 23" in dependency_text["24"], "unresolved prerequisite is clearly identified as blocking")
check(next(t for t in data["tickets"] if t["id"] == "23")["blockedBy"] == ["01"] and next(t for t in data["tickets"] if t["id"] == "23")["status"] == "open", "dependency presentation does not change IDs or ticket business status")
check(next(t["status"] for t in dom["statuses"] if t["id"] == "23") == "frontier", "legitimate ready focus remains ready, not universally blocked")
check("前置就緒" in dom["elements"]["meta"]["textContent"] and "前置就緒" in data["labels"]["legendFrontier"], "header and legend say dependency readiness")
check(any("前置就緒" in chip["textContent"] for chip in dom["elements"]["chips"]["children"]) and any("前置就緒" in card["innerHTML"] for card in dom["elements"]["cards"]["children"]), "actual filters and card summaries use the same readiness wording")
check("不代表產品完成或已獲執行授權" in dom["elements"]["status-boundary"]["textContent"], "visible header boundary separates prerequisites, completion and authority")

root, run = fixture("english-readiness", "23", language="en")
html, data = rendered(root, run)
dom = focus_dom(html)
check("dependency-ready" in dom["elements"]["meta"]["textContent"] and "dependency-ready" in data["labels"]["legendFrontier"] and any("dependency-ready" in chip["textContent"] for chip in dom["elements"]["chips"]["children"]), "English header, legend and filter consistently say dependency-ready")

for name, focus, status, prerequisite, problem in (
    ("invalid-focus", "99", "open", "resolved", "invalid"),
    ("empty-focus", "", "open", "resolved", "invalid"),
    ("resolved-focus", "23", "resolved", "resolved", "resolved"),
    ("blocked-focus", "23", "open", "open", "blocked"),
):
    root, run = fixture(name, focus, status, prerequisite)
    html, data = rendered(root, run)
    check(data["focus"]["problem"] == problem and data["focus"]["ticketId"] is None, f"{name}: does not substitute a ready ticket")
    dom = focus_dom(html)
    check(dom["elements"]["map-overview"]["open"] and bool(dom["elements"]["focus-content"]["textContent"]), f"{name}: explicit warning and full map visible")

root, run = fixture("no-focus")
html, data = rendered(root, run)
dom = focus_dom(html)
check(data["focus"] is None and dom["elements"]["map-overview"]["open"], "no focus preserves full-map visibility")
check("current-focus" not in dom["elements"], "no focus does not fabricate a decision card")

root, run = fixture("prose-focus", "23", body="原有正文已說明：A 方便但暴露個資；B 遮蔽但多一步辨識。依客服既有查詢範圍，建議 B；仍未取得使用者決定。")
html, data = rendered(root, run)
dom = focus_dom(html)
focus_text = json.dumps(dom["elements"]["focus-content"], ensure_ascii=False)
check("原有正文已說明" in focus_text and "來源未另列" not in focus_text and "focus-missing" not in focus_text, "prose-only ticket needs no ritual headings and receives no false missing-content warning")
check("issues/23-human-choice.md" in focus_text, "focus links the original ticket")

root, run = fixture("empty-content", "23", body="")
html, data = rendered(root, run)
dom = focus_dom(html)
check("focus-missing" in json.dumps(dom), "genuinely empty body gets a missing-content message")

attack = '<img src=x onerror="globalThis.PWNED=true"> </script><script>globalThis.PWNED=true</script> [bad](javascript:alert(1))'
root, run = fixture("escaped-content", "23", body="## Question\n" + attack)
html, data = rendered(root, run)
dom = focus_dom(html)
focus_text = json.dumps(dom["elements"]["focus-content"])
check("</script><script>globalThis.PWNED" not in html, "JSON payload cannot close the script element")
check("&lt;img" in focus_text and "<img" not in focus_text and not dom["pwned"], "actual markdown renderer escapes HTML instead of executing it")
check('href=\\"#\\"' in focus_text and 'href=\\"javascript:' not in focus_text, "unsafe Markdown link protocol is rejected")

root, run = fixture("duplicate-id", extra={"01-duplicate.md": ticket("Duplicate")})
check(run.returncode != 0 and "WAYFINDER_DUPLICATE_TICKET_ID" in run.stderr and not (root / "map.html").exists(), "duplicate ID guard prevents output")
root, run = fixture("cycle", extra={"01-known.md": ticket("Cycle prerequisite", blocked="24")})
check(run.returncode != 0 and "WAYFINDER_BLOCKING_CYCLE" in run.stderr and not (root / "map.html").exists(), "dependency cycle guard prevents output")
check(module.resolve_focus("23", [{"id": "23", "status": "open", "blockedBy": ["99"]}])["problem"] == "blocked", "missing dependency cannot be presented as a ready focus")
root, run = fixture("missing-prerequisite", "23", extra={"23-human-choice.md": ticket("Missing prerequisite", blocked="99")})
html, data = rendered(root, run)
dom = focus_dom(html)
check(data["focus"]["problem"] == "blocked" and dom["elements"]["map-overview"]["open"], "missing prerequisite keeps focus warning and map visible")
check(next(item["status"] for item in dom["statuses"] if item["id"] == "23") == "blocked", "full-map status does not contradict missing-prerequisite focus warning")
check("⛔ 缺失前置阻擋: 99" in next(item["markup"] for item in dom["dependencies"] if item["id"] == "23"), "missing prerequisite is labelled distinctly and remains blocking")

# Replay immutable actual A/B inputs. A resolves the scoped discussion ticket;
# B keeps future implementation open. Neither authorizes or completes the product.
repro = repo / "docs/experiments/common-lab/wayfinder-regression-v0.1.3-repro"
for arm in ("A", "B"):
    original = repro / "before" / arm / ".common-lab/wayfinder/privacy-rollout"
    replay = artifact_root / ("actual-" + arm)
    shutil.copytree(original, replay)
    output = replay / "map.after.html"
    run = subprocess.run([sys.executable, "-B", str(renderer), str(replay), str(output), "--no-open"], capture_output=True, text=True)
    check(run.returncode == 0, f"actual {arm}: same frozen input renders successfully")
    html = output.read_text(encoding="utf-8")
    data = json.loads(re.search(r"const DATA = (.*);\nconst L =", html).group(1))
    dom = focus_dom(html)
    check(all((replay / p.relative_to(original)).read_bytes() == p.read_bytes() for p in original.rglob("*") if p.is_file()), f"actual {arm}: no fixture truth or business state changed")
    check("不代表產品完成或已獲執行授權" in dom["elements"]["status-boundary"]["textContent"], f"actual {arm}: status boundary remains visible even when the full map is optional")
    if arm == "B":
        check(next(t["status"] for t in dom["statuses"] if t["id"] == "24") == "frontier" and "1 張前置就緒" in dom["elements"]["meta"]["textContent"], "out-of-scope independent ticket remains dependency-ready without a false execution claim")
        check(any("不在本回合授權內" in item for item in data["outOfScope"]) and "現在可處理" not in dom["elements"]["meta"]["textContent"], "out-of-scope truth is retained without inferring new permission fields")
    else:
        check(all(t["status"] == "resolved" for t in dom["statuses"]) and "3 張已解決" in dom["elements"]["meta"]["textContent"], "all resolved discussion tickets remain resolved without becoming a product-completion claim")

# Separate proven defect: 0.1.2 accepts Status:mystery as frontier. Do not conflate
# this data-validation guard with the terminology/authority presentation change.
root, run = fixture("unknown-status", status="mystery")
check(run.returncode != 0 and "WAYFINDER_UNKNOWN_TICKET_STATUS" in run.stderr and not (root / "map.html").exists(), "unknown status fails closed instead of generating a ready ticket")
with (root / "render-run.json").open("x", encoding="utf-8") as stream:
    json.dump({"exit_code": run.returncode, "stdout": run.stdout, "stderr": run.stderr, "independent_variable": "known-status-validation", "before_evidence": str(repro / "receipt.json")}, stream, indent=2)

# Observation only: claimed remains ownership state even with unresolved deps.
root, run = fixture("claimed-blocked-observation", "23", status="claimed", prerequisite="open")
html, data = rendered(root, run)
dom = focus_dom(html)
check(next(t["status"] for t in dom["statuses"] if t["id"] == "23") == "claimed" and data["focus"]["problem"] == "blocked", "claimed-with-blocked-dependency observation is preserved, not silently redesigned")

atomic_target = artifact_root / "atomic-probe.html"
original_replace = module.os.replace
atomic_calls = []
def checked_replace(source, target):
    check(Path(source).parent == atomic_target.parent and Path(source).read_text() == "atomic probe", "atomic write stages complete content beside target")
    atomic_calls.append((str(source), str(target)))
    original_replace(source, target)
module.os.replace = checked_replace
try:
    module.atomic_write(atomic_target, "atomic probe")
finally:
    module.os.replace = original_replace
check(len(atomic_calls) == 1 and atomic_target.read_text() == "atomic probe", "atomic replacement remains in use")

receipt = {"checks_passed": len(results), "checks": results, "artifact_root": str(artifact_root), "renderer_sha256": hashlib.sha256(renderer.read_bytes()).hexdigest(), "browser_qa": "not performed; Node minimal DOM is a targeted regression, not a real browser"}
with (artifact_root / "receipt.json").open("x", encoding="utf-8") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"result": "PASS", "checks": len(results), "artifacts": str(artifact_root)}, ensure_ascii=False))

#!/usr/bin/env python3
"""Generate CSV, Markdown and HTML deliverables from one Estimate case revision."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from case_state import CaseError, item_days, item_effort_days, load, validate_state


MANAGED = (
    "assessment-report.md",
    "assessment-report.html",
    "estimate-internal.csv",
    "estimate-external.csv",
    "generation-report.json",
)
EXTERNAL_BANNED_LABELS = ("低人天", "基準人天", "高人天", "內部估算", "內部緩衝")


def atomic_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent, prefix=f".{path.name}.", suffix=".tmp") as stream:
        stream.write(content)
        temporary = Path(stream.name)
    temporary.replace(path)


def atomic_text(path: Path, content: str, bom: bool = False) -> None:
    encoded = content.encode("utf-8-sig" if bom else "utf-8")
    atomic_bytes(path, encoded)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_scenario(state: dict[str, Any]) -> dict[str, Any] | None:
    selected = state.get("selectedScenarioId")
    return next((item for item in state.get("scenarios", []) if item.get("id") == selected), None)


def public_text(value: Any) -> str:
    text = str(value or "")
    patterns = (
        (r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key)\s*[:=]\s*[^\s,;]+", r"\1=[REDACTED]"),
        (r"(?i)https?://[^\s)\]]+", "[內部網址已移除]"),
        (r"(?<!\d)(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)(?:\.\d{1,3}){3}(?!\d)", "[內網位址已移除]"),
        (r"(?i)(?:[A-Z]:\\|/home/|/Users/|/mnt/[a-z]/)[^\s,;]+", "[本機路徑已移除]"),
    )
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def csv_text(rows: list[list[Any]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerows(rows)
    return buffer.getvalue()


def internal_rows(state: dict[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = [[
        "客戶成果包", "包別", "工作名稱", "工作樣態", "現況限制", "實際改法", "客戶成果",
        "規模證據", "計價理由", "費率依據", "去重邊界", "說明", "總數", "需處理", "不處理", "未知", "計價單位",
        "單位低", "單位基準", "單位高", "低人天", "基準人天", "高人天",
        "開發低", "開發基準", "開發高", "測試低", "測試基準", "測試高",
        "責任", "來源成功條件", "完成證據", "包含", "排除",
    ]]
    package_names = {row.get("id"): row.get("name", "") for row in state.get("clientPackages", [])}
    for item in state.get("workItems", []):
        totals = item_days(item)
        effort = item_effort_days(item)
        rates = item.get("unitDays") or {}
        rows.append([
            package_names.get(item.get("clientPackageId"), item.get("clientPackageId", "")),
            item.get("package", "應用改造"), item.get("name", ""), item.get("kind", ""),
            item.get("currentConstraint", ""), item.get("changeMethod", ""), item.get("customerOutcome", ""),
            item.get("scaleEvidence", ""), item.get("countingRationale", ""), item.get("rateBasis", ""),
            item.get("dedupeBoundary", ""), item.get("description", ""),
            item.get("total", 0), item.get("needsChange", 0), item.get("noChange", 0), item.get("unknown", 0),
            item.get("pricingUnits", 0),
            rates.get("low", 0), rates.get("baseline", 0), rates.get("high", 0),
            totals["low"], totals["baseline"], totals["high"],
            effort["development"]["low"], effort["development"]["baseline"], effort["development"]["high"],
            effort["testing"]["low"], effort["testing"]["baseline"], effort["testing"]["high"],
            item.get("owner", "我方"), " | ".join(item.get("nodeIds", [])), item.get("completionEvidence", ""),
            item.get("includes", ""), item.get("excludes", ""),
        ])
    total = {key: sum(item_days(item)[key] for item in state.get("workItems", [])) for key in ("low", "baseline", "high")}
    effort_total = {
        category: {
            tier: sum(item_effort_days(item)[category][tier] for item in state.get("workItems", []))
            for tier in ("low", "baseline", "high")
        }
        for category in ("development", "testing")
    }
    rows.append(["", "", "合計", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", total["low"], total["baseline"], total["high"], effort_total["development"]["low"], effort_total["development"]["baseline"], effort_total["development"]["high"], effort_total["testing"]["low"], effort_total["testing"]["baseline"], effort_total["testing"]["high"], "", "", "", "", ""])
    return rows


def client_package_totals(state: dict[str, Any]) -> dict[str, dict[str, float]]:
    totals = {row.get("id"): {"low": 0.0, "baseline": 0.0, "high": 0.0} for row in state.get("clientPackages", [])}
    for item in state.get("workItems", []):
        package_id = item.get("clientPackageId")
        if package_id not in totals:
            continue
        days = item_days(item)
        for key in ("low", "baseline", "high"):
            totals[package_id][key] += days[key]
    return totals


def external_rows(state: dict[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = [["序號", "系統功能", "功能說明", "開發人天", "測試人天"]]
    effort_totals = {
        row.get("id"): {"development": 0.0, "testing": 0.0}
        for row in state.get("clientPackages", [])
    }
    for item in state.get("workItems", []):
        package_id = item.get("clientPackageId")
        if package_id not in effort_totals:
            continue
        effort = item_effort_days(item)
        effort_totals[package_id]["development"] += effort["development"]["high"]
        effort_totals[package_id]["testing"] += effort["testing"]["high"]
    for index, package in enumerate(state.get("clientPackages", []), start=1):
        package_id = package.get("id")
        rows.append([
            index,
            public_text(package.get("name", "")),
            public_text(package.get("externalSummary", "")),
            effort_totals.get(package_id, {}).get("development", 0),
            effort_totals.get(package_id, {}).get("testing", 0),
        ])
    return rows


def report_markdown(state: dict[str, Any]) -> str:
    outcome = state.get("outcome") or {}
    scenario = selected_scenario(state)
    nodes = (state.get("successChain") or {}).get("nodes", [])
    external = [node for node in nodes if node.get("disposition") in {"zero", "external"}]
    fogs = [item for item in state.get("fogs", []) if item.get("status", "open") != "resolved"]
    lines = [
        f"# {public_text(state.get('name'))} 評估報告",
        "",
        f"- 案件版本：{state.get('revision')}",
        f"- 評估模式：{state.get('mode')}",
        f"- 目前狀態：{state.get('status')}",
        "",
        "## 客戶要取得的成果",
        "",
        public_text(outcome.get("goal")),
        "",
        f"責任邊界：{public_text(outcome.get('responsibilityBoundary'))}",
        "",
        "## 現況與證據結論",
        "",
    ]
    evidence = state.get("evidence", [])
    lines.extend([f"- {public_text(item.get('claim'))}" for item in evidence] or ["- 尚未形成可交付的證據結論。"])
    lines.extend(["", "## 採用方案", ""])
    if scenario:
        lines.extend([f"### {public_text(scenario.get('name'))}", "", public_text(scenario.get("summary")), ""])
    else:
        lines.extend(["尚未由 PM 選定方案。", ""])
    lines.extend(["## 重要依賴與語意相容", ""])
    dependencies = state.get("dependencies", [])
    coverage = state.get("dependencyCoverage") or {}
    coverage_labels = {"complete": "完整", "bounded": "已界定邊界", "blocked": "受阻", "pending": "盤點中"}
    maintenance_labels = {"active": "持續維護", "limited": "有限維護", "stale": "長期未更新", "eol": "已終止維護", "unknown": "待確認"}
    compatibility_labels = {"supported": "上游支持", "conditional": "有條件成立", "unsupported": "上游不支持", "unknown": "待確認"}
    strategy_labels = {"keep": "沿用", "fork": "採用維護分支", "replace": "替換或升級", "self-maintain": "自行維護", "stay": "停留既有版本", "vendor": "由供應方承接", "not-applicable": "不適用", "unresolved": "待決定"}
    if coverage:
        boundary = (public_text(coverage.get("boundary")) or "完整盤點").rstrip("。；;")
        lines.append(
            f"- **依賴盤點範圍**：以 {public_text(coverage.get('discoveryMethod'))} 取得 "
            f"{coverage.get('componentCount', 0)} 個元件；狀態為 {coverage_labels.get(coverage.get('status'), public_text(coverage.get('status')))}；邊界：{boundary}。"
        )
    for item in dependencies:
        breaks = "、".join(public_text(value) for value in item.get("semanticBreaks", [])) or "尚未辨識"
        resolution = item.get("resolution") or {}
        selected_target = resolution.get("selectedTarget")
        selected_claim = next(
            (
                claim for claim in item.get("compatibilityClaims", [])
                if isinstance(claim, dict) and claim.get("target") == selected_target
            ),
            {},
        )
        lines.append(
            f"- **{public_text(item.get('component'))}**：用途為 {public_text(item.get('usage'))}；"
            f"上游為 {public_text(item.get('upstreamMaintainer'))}（{maintenance_labels.get(item.get('maintenanceStatus'), public_text(item.get('maintenanceStatus')))}），"
            f"我方責任為 {public_text(item.get('internalOwner'))}；採用 {public_text(selected_target)}，"
            f"相容性為 {compatibility_labels.get(selected_claim.get('status'), public_text(selected_claim.get('status')))}，"
            f"策略為 {strategy_labels.get(resolution.get('strategy'), public_text(resolution.get('strategy')))}；"
            f"主要語意斷點：{breaks}；驗證：{public_text(item.get('probe'))}。"
        )
    if not dependencies:
        lines.append("- 尚未建立 dependency snapshot／SBOM；升版或混合案件不可據此形成正式方案。")
    lines.append("")
    lines.extend(["## 成果成功鏈", ""])
    for node in nodes:
        lines.append(f"- **{public_text(node.get('name'))}**（{public_text(node.get('owner'))}）：{public_text(node.get('completionEvidence'))}")
    if not nodes:
        lines.append("- 成功鏈尚未建立。")
    lines.extend(["", "## 客戶成果包與人天", "", "| 客戶成果 | 為何需要 | 我們怎麼做 | 對外人天 |", "|---|---|---|---:|"])
    package_totals = client_package_totals(state)
    for package in state.get("clientPackages", []):
        lines.append(
            f"| {public_text(package.get('name'))} | {public_text(package.get('whyRequired'))} | "
            f"{public_text(package.get('deliveryApproach'))} | {package_totals.get(package.get('id'), {}).get('high', 0)} |"
        )
    if state.get("workItems"):
        total = sum(item_days(item)["high"] for item in state["workItems"])
        lines.append(f"| **合計** |  |  | **{total}** |")
    else:
        lines.append("| 尚未建立估算 | 0 | 0 | 成功鏈收斂後再估算 |")
    lines.extend(["", "## 已檢查但不納入我方人天", ""])
    lines.extend([f"- {public_text(node.get('name'))}：{public_text(node.get('zeroReason'))}" for node in external] or ["- 目前無。"])
    lines.extend(["", "## 仍待釐清", ""])
    lines.extend([f"- {public_text(item.get('question') or item.get('title'))}：{public_text(item.get('impact'))}" for item in fogs] or ["- 目前無會改變結論的未知事項。"])
    lines.extend(["", "## 新人理解方式", "", "先從客戶成果看成功鏈，再看每個節點由哪項工作承接。對外人天採同一範圍的合理高值；外部責任與確定不異動項目仍保留在報告中，但我方人天為 0。", ""])
    return "\n".join(lines)


def report_html(markdown: str, title: str) -> str:
    sections: list[str] = []
    in_list = False
    in_table = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if line.startswith("|---"):
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [html.escape(cell.strip().replace("**", "")) for cell in line.strip("|").split("|")]
            if not in_table:
                if in_list: sections.append("</ul>"); in_list = False
                sections.append("<table>"); in_table = True
                sections.append("<thead><tr>" + "".join(f"<th>{cell}</th>" for cell in cells) + "</tr></thead><tbody>")
            else:
                sections.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
            continue
        if in_table:
            sections.append("</tbody></table>"); in_table = False
        if line.startswith("# "):
            sections.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_list: sections.append("</ul>"); in_list = False
            sections.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            sections.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("- "):
            if not in_list: sections.append("<ul>"); in_list = True
            sections.append(f"<li>{html.escape(line[2:].replace('**', ''))}</li>")
        elif line:
            if in_list: sections.append("</ul>"); in_list = False
            sections.append(f"<p>{html.escape(line.replace('**', ''))}</p>")
    if in_list: sections.append("</ul>")
    if in_table: sections.append("</tbody></table>")
    return f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>body{{max-width:1080px;margin:0 auto;padding:32px;font-family:'Microsoft JhengHei UI',sans-serif;color:#203139;background:#fcfdfb;line-height:1.65}}h1,h2,h3{{font-family:Bahnschrift,'Microsoft JhengHei UI',sans-serif}}h1{{border-bottom:3px solid #082d3e;padding-bottom:14px}}h2{{margin-top:34px;color:#174d62}}table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{border:1px solid #c8d5d8;padding:9px;text-align:left}}th{{background:#e8f1f3}}@media(max-width:700px){{body{{padding:18px}}table{{display:block;overflow:auto}}}}</style></head><body>{''.join(sections)}</body></html>"""


def generate(case_root: Path, output_dir: Path | None) -> dict[str, Any]:
    state = load(case_root)
    errors, warnings = validate_state(state)
    if errors:
        raise CaseError("案件無法生成成果：\n- " + "\n- ".join(errors))
    destination = output_dir.resolve() if output_dir else case_root.resolve() / "outputs"
    destination.mkdir(parents=True, exist_ok=True)
    internal = csv_text(internal_rows(state))
    external = csv_text(external_rows(state))
    for banned in EXTERNAL_BANNED_LABELS:
        if banned in external:
            raise CaseError(f"對外 CSV 含內部欄位：{banned}")
    markdown = report_markdown(state)
    rendered_html = report_html(markdown, f"{state.get('name')} 評估報告")
    contents = {
        "assessment-report.md": (markdown + "\n", False),
        "assessment-report.html": (rendered_html, False),
        "estimate-internal.csv": (internal, True),
        "estimate-external.csv": (external, True),
    }
    for name, (content, bom) in contents.items():
        atomic_text(destination / name, content, bom=bom)
    report = {
        "ok": True,
        "stateRevision": state.get("revision"),
        "warnings": warnings,
        "files": {name: {"path": str((destination / name).resolve()), "sha256": sha256(destination / name)} for name in contents},
    }
    atomic_text(destination / "generation-report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    report["files"]["generation-report.json"] = {"path": str((destination / "generation-report.json").resolve()), "sha256": sha256(destination / "generation-report.json")}
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = generate(args.case_root, args.output_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else "成果已生成：" + str(args.output_dir or args.case_root / "outputs"))
        return 0
    except CaseError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

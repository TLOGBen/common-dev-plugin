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
from string import Template
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
STATE_LABELS = {
    "draft": "草稿預覽",
    "mapping": "方案整理中（預覽）",
    "estimate-ready": "人天待確認（預覽）",
    "estimate-approved": "人天已核准，待交付",
    "complete": "交付完成",
}


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
    header: list[Any] = [
        "客戶成果包", "包別", "工作名稱", "工作樣態", "現況限制", "實際改法", "客戶成果",
        "規模證據", "計價理由", "費率依據", "基準人天理由", "去重邊界", "修改重點",
        "影響頁面", "影響 API", "對應檔案", "工作集合", "說明", "總數", "需處理", "不處理", "未知", "計價單位",
        "單位低", "單位基準", "單位高", "低人天", "基準人天", "高人天",
        "開發低", "開發基準", "開發高", "測試低", "測試基準", "測試高",
        "責任", "來源成功條件", "完成證據", "包含", "排除",
    ]
    rows: list[list[Any]] = [header]
    package_names = {row.get("id"): row.get("name", "") for row in state.get("clientPackages", [])}
    for item in state.get("workItems", []):
        totals = item_days(item)
        effort = item_effort_days(item)
        rates = item.get("unitDays") or {}
        targets = item.get("changeTargets") or {}
        rows.append([
            package_names.get(item.get("clientPackageId"), item.get("clientPackageId", "")),
            item.get("package", "應用改造"), item.get("name", ""), item.get("kind", ""),
            item.get("currentConstraint", ""), item.get("changeMethod", ""), item.get("customerOutcome", ""),
            item.get("scaleEvidence", ""), item.get("countingRationale", ""), item.get("rateBasis", ""),
            item.get("baselineRationale", ""), item.get("dedupeBoundary", ""), item.get("pmChangeSummary", ""),
            " | ".join(targets.get("pages", [])), " | ".join(targets.get("apis", [])),
            " | ".join(targets.get("files", [])), " | ".join(item.get("detailCatalogIds", [])), item.get("description", ""),
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
    total_row: list[Any] = [""] * len(header)
    total_row[2] = "合計"
    for label, value in (
        ("低人天", total["low"]), ("基準人天", total["baseline"]), ("高人天", total["high"]),
        ("開發低", effort_total["development"]["low"]),
        ("開發基準", effort_total["development"]["baseline"]),
        ("開發高", effort_total["development"]["high"]),
        ("測試低", effort_total["testing"]["low"]),
        ("測試基準", effort_total["testing"]["baseline"]),
        ("測試高", effort_total["testing"]["high"]),
    ):
        total_row[header.index(label)] = value
    rows.append(total_row)
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


def package_effort_totals(state: dict[str, Any]) -> dict[str, dict[str, dict[str, float]]]:
    totals = {
        row.get("id"): {
            category: {tier: 0.0 for tier in ("low", "baseline", "high")}
            for category in ("development", "testing")
        }
        for row in state.get("clientPackages", [])
    }
    for item in state.get("workItems", []):
        package_id = item.get("clientPackageId")
        if package_id not in totals:
            continue
        effort = item_effort_days(item)
        for category in ("development", "testing"):
            for tier in ("low", "baseline", "high"):
                totals[package_id][category][tier] += effort[category][tier]
    return totals


def target_items(item: dict[str, Any], key: str) -> list[str]:
    targets = item.get("changeTargets") or {}
    values = targets.get(key, [])
    return [public_text(value) for value in values] if isinstance(values, list) else []


def report_markdown(state: dict[str, Any]) -> str:
    outcome = state.get("outcome") or {}
    scenario = selected_scenario(state)
    nodes = (state.get("successChain") or {}).get("nodes", [])
    external = [node for node in nodes if node.get("disposition") in {"zero", "external"}]
    fogs = [item for item in state.get("fogs", []) if item.get("status", "open") != "resolved"]
    packages = state.get("clientPackages", [])
    package_names = {item.get("id"): public_text(item.get("name")) for item in packages}
    work_by_package = {
        package.get("id"): [item for item in state.get("workItems", []) if item.get("clientPackageId") == package.get("id")]
        for package in packages
    }
    package_totals = client_package_totals(state)
    review = state.get("estimationReview") or {}
    summary_heading = {"cr": "本次 CR 摘要", "upgrade": "本次升版摘要", "mixed": "本次評估摘要"}.get(state.get("mode"), "本次評估摘要")
    lines = [
        f"# {public_text(state.get('name'))} 評估報告", "",
        f"- 案件版本：{state.get('revision')}", f"- 評估模式：{state.get('mode')}", f"- 目前狀態：{STATE_LABELS.get(state.get('status'), state.get('status'))}", "",
        f"## {summary_heading}", "",
        public_text(outcome.get("pmCurrentState")) or "尚未形成可供 PM 確認的現況結論。", "",
        f"本次要達成：{public_text(outcome.get('goal'))}", "",
        f"責任邊界：{public_text(outcome.get('responsibilityBoundary'))}", "",
    ]
    findings = review.get("criticalFindings", []) if isinstance(review.get("criticalFindings"), list) else []
    lines.extend(["## 評估項目與人天", "", "每項先列低／基準／高值與原項目說明；細節中再呈現施工落點、公式與該項額外發現。", ""])
    for package in packages:
        package_id = package.get("id")
        totals = package_totals.get(package_id, {})
        lines.extend([
            f"### {public_text(package.get('name'))}｜低 {totals.get('low', 0)}／基準 {totals.get('baseline', 0)}／高 {totals.get('high', 0)} 人天", "",
            public_text(package.get("externalSummary")), "", f"處理方式：{public_text(package.get('deliveryApproach'))}", "",
            "#### 修改明細", "",
        ])
        for item in work_by_package.get(package_id, []):
            pages, apis, files = (target_items(item, key) for key in ("pages", "apis", "files"))
            target_note = public_text((item.get("changeTargets") or {}).get("notes"))
            rates = item.get("unitDays") or {}
            baseline_total = item_days(item)["baseline"]
            lines.extend([
                f"##### {public_text(item.get('name'))}", "", public_text(item.get("pmChangeSummary")), "",
                f"- 影響頁面（{len(pages)}）：{'、'.join(pages) if pages else '不涉及'}",
                f"- 影響 API（{len(apis)}）：{'、'.join(apis) if apis else '不涉及'}",
                f"- 對應檔案（{len(files)}）：{'、'.join(files) if files else '不涉及'}",
                *([f"- 落點說明：{target_note}"] if target_note else []),
                f"- 基準公式：{item.get('pricingUnits', 0)} × {rates.get('baseline', 0)} = {baseline_total} 人天",
                f"- 基準理由：{public_text(item.get('baselineRationale'))}", "",
            ])
        related = [finding for finding in findings if package_id in finding.get("clientPackageIds", [])]
        if related:
            lines.extend(["#### 這項額外查到", ""])
            for finding in related:
                delta = finding.get("scopeDelta") or {}
                delta_text = f" 範圍修正 {delta.get('assumed')} → {delta.get('confirmed')} {public_text(delta.get('subject'))}。" if delta else ""
                lines.extend([
                    f"- **{public_text(finding.get('title'))}**",
                    f"  - **人天怎麼看：**{public_text(finding.get('estimateImpact'))}",
                    f"  - **PM 現在要注意什麼：**{public_text(finding.get('treatment'))}",
                    "  - <details>",
                    "    <summary>查看判斷依據</summary>", "",
                    f"    - **原本怎麼算：**{public_text(finding.get('statedAssumption'))}",
                    f"    - **後來查到什麼：**{public_text(finding.get('evidenceConclusion'))}{delta_text}",
                    f"    - **為什麼重要：**{public_text(finding.get('whyItMatters'))}", "",
                    "    </details>",
                ])
            lines.append("")
    lines.extend(["## 採用方案", ""])
    if scenario:
        lines.extend([f"### {public_text(scenario.get('name'))}", "", public_text(scenario.get("summary")), ""])
    else:
        lines.extend(["尚未由 PM 選定方案。", ""])

    lines.extend(["## 做到哪些事才算交付", "", "PM 為什麼要看：這裡把每項費用連到可驗收結果，可用來檢查是否漏估或只做了技術升級、卻沒有交付可用成果。", ""])
    for node in nodes:
        lines.append(f"- **{public_text(node.get('name'))}**（{public_text(node.get('owner'))}）：{public_text(node.get('completionEvidence'))}")
    if not nodes:
        lines.append("- 成果成立條件尚未建立。")

    dependencies = state.get("dependencies", [])
    coverage = state.get("dependencyCoverage") or {}
    coverage_labels = {"complete": "完整", "bounded": "已界定邊界", "blocked": "受阻", "pending": "盤點中"}
    maintenance_labels = {"active": "持續維護", "limited": "有限維護", "stale": "長期未更新", "eol": "已終止維護", "unknown": "待確認"}
    compatibility_labels = {"supported": "上游支持", "conditional": "有條件成立", "unsupported": "上游不支持", "unknown": "待確認"}
    strategy_labels = {"keep": "沿用", "fork": "採用維護分支", "replace": "替換或升級", "self-maintain": "自行維護", "stay": "停留既有版本", "vendor": "由供應方承接", "not-applicable": "不適用", "unresolved": "待決定"}
    lines.extend(["", "## 會讓方案失敗或加價的前提", "", "PM 為什麼要看：這些不是套件清單；任一條件不成立，都可能改變方案、責任、工期或後續維護方式。", ""])
    if coverage:
        boundary = (public_text(coverage.get("boundary")) or "完整盤點").rstrip("。；;")
        lines.append(f"- **依賴盤點範圍**：以 {public_text(coverage.get('discoveryMethod'))} 取得 {coverage.get('componentCount', 0)} 個元件；狀態為 {coverage_labels.get(coverage.get('status'), public_text(coverage.get('status')))}；邊界：{boundary}。")
    for item in dependencies:
        breaks = "、".join(public_text(value) for value in item.get("semanticBreaks", [])) or "尚未辨識"
        resolution = item.get("resolution") or {}
        selected_target = resolution.get("selectedTarget")
        selected_claim = next((claim for claim in item.get("compatibilityClaims", []) if isinstance(claim, dict) and claim.get("target") == selected_target), {})
        lines.append(
            f"- **{public_text(item.get('component'))}**：目前用於 {public_text(item.get('usage'))}；採用 {public_text(selected_target)}，"
            f"相容性為 {compatibility_labels.get(selected_claim.get('status'), public_text(selected_claim.get('status')))}，"
            f"策略為 {strategy_labels.get(resolution.get('strategy'), public_text(resolution.get('strategy')))}；"
            f"主要斷點：{breaks}；上游 {maintenance_labels.get(item.get('maintenanceStatus'), public_text(item.get('maintenanceStatus')))}；"
            f"上游維護者：{public_text(item.get('upstreamMaintainer'))}；我方責任：{public_text(item.get('internalOwner'))}；確認方式：{public_text(item.get('probe'))}。"
        )
    if not dependencies:
        lines.append("- 本案沒有需改變方案的關鍵依賴；升版或混合案件若未完成盤點，不能形成正式估算。")

    evidence = state.get("evidence", [])
    lines.extend(["", "## 技術證據附錄", ""])
    lines.extend([f"- {public_text(item.get('claim'))}" for item in evidence] or ["- 尚未形成可交付的證據結論。"])
    lines.extend(["", "## 已檢查但不納入我方人天", ""])
    lines.extend([f"- {public_text(node.get('name'))}：{public_text(node.get('zeroReason'))}" for node in external] or ["- 目前無。"])
    lines.extend(["", "## 仍待釐清", ""])
    lines.extend([f"- {public_text(item.get('question') or item.get('title'))}：{public_text(item.get('impact'))}" for item in fogs] or ["- 目前無會改變結論的未知事項。"])
    lines.append("")
    return "\n".join(lines)


def safe_fragment(value: Any) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value or "item")).strip("-") or "item"


def h(value: Any) -> str:
    return html.escape(public_text(value))


def html_list(values: list[str], empty: str = "不涉及") -> str:
    if not values:
        return f'<p class="empty">{html.escape(empty)}</p>'
    return "<ul>" + "".join(f"<li>{h(value)}</li>" for value in values) + "</ul>"


def workset_html(catalog: dict[str, Any]) -> str:
    treatment = catalog.get("treatment")
    claimed_count = catalog.get("claimedCount", 0)
    pricing_role = catalog.get("pricingRole")
    pricing_label = "計價單位" if pricing_role == "pricing-unit" else "範圍證據，不作人工乘數"
    origin_label = "既有案件一次性回填" if catalog.get("origin") == "legacy-migration" else "Discovery 盤點"
    if treatment == "direct-touch":
        action_labels = {
            "no-change": "不需修改", "batch-change": "批次調整",
            "manual-change": "逐項修改", "high-risk-verify": "高風險驗證",
        }
        rows = "".join(f'''<tr data-workset-item="{h(item.get('id'))}">
<th scope="row">{h(item.get('name'))}</th><td>{h(item.get('purpose'))}</td><td>{h(action_labels.get(item.get('action'), item.get('action')))}</td><td>{h(item.get('changeDetail'))}</td><td>{h(item.get('verification'))}</td></tr>''' for item in catalog.get("items", []))
        return f'''<details class="workset workset-direct" data-workset-items="{claimed_count}"><summary><span><small>逐項處理</small><strong>{h(catalog.get('name'))}</strong></span><span><b>{claimed_count}</b> 項</span></summary>
<div class="workset-body"><p class="workset-meta">{pricing_label}｜{origin_label}</p><div class="workset-table-scroll"><table><thead><tr><th>項目／路徑</th><th>用途</th><th>處理方式</th><th>修改重點</th><th>驗證</th></tr></thead><tbody>{rows}</tbody></table></div></div></details>'''
    if treatment == "generated":
        generation = catalog.get("generation") or {}
        return f'''<details class="workset workset-generated" data-generated-count="{claimed_count}"><summary><span><small>重新產製</small><strong>{h(catalog.get('name'))}</strong></span><span><b>{claimed_count}</b> 項</span></summary>
<div class="workset-body"><p class="workset-meta">{pricing_label}｜{origin_label}</p><p class="generated-note">這 {claimed_count} 項由同一產製流程重新生成，不代表 {claimed_count} 次人工修改。</p><dl class="generation-method"><div><dt>產製來源</dt><dd>{h(generation.get('source'))}</dd></div><div><dt>重新產製</dt><dd>{h(generation.get('method'))}</dd></div><div><dt>怎麼核對</dt><dd>{h(generation.get('verification'))}</dd></div></dl></div></details>'''
    return f'''<details class="workset workset-evidence" data-evidence-count="{claimed_count}"><summary><span><small>範圍證據</small><strong>{h(catalog.get('name'))}</strong></span><span><b>{claimed_count}</b> 項</span></summary>
<div class="workset-body"><p class="workset-meta">{pricing_label}｜{origin_label}</p><p>{h(catalog.get('explanation'))}</p></div></details>'''


def explanation_visuals(package: dict[str, Any]) -> str:
    rendered: list[str] = []
    for index, visual in enumerate(package.get("visuals", [])[:3], start=1):
        if not isinstance(visual, dict) or visual.get("type") != "flow":
            continue
        nodes = [str(value) for value in visual.get("nodes", []) if str(value).strip()]
        if not 2 <= len(nodes) <= 7:
            continue
        slug = f"{safe_fragment(package.get('id'))}-explanation-{index}"
        node_width, gap, margin = 160, 48, 32
        view_width = margin * 2 + len(nodes) * node_width + (len(nodes) - 1) * gap
        arrows: list[str] = []
        boxes: list[str] = []
        for node_index, label in enumerate(nodes):
            x = margin + node_index * (node_width + gap)
            if node_index < len(nodes) - 1:
                arrows.append(
                    f'<path d="M{x + node_width} 96 H{x + node_width + gap}" fill="none" stroke="#687782" '
                    f'stroke-width="2" marker-end="url(#arrow-{slug})"/>'
                )
            focal = node_index == min(1, len(nodes) - 1)
            fill, stroke, width = ("#fff5ef", "#c95332", 2) if focal else ("#f7f8f8", "#78909b", 1)
            short = public_text(label)
            short = short if len(short) <= 14 else short[:13] + "…"
            boxes.append(
                f'<rect x="{x}" y="56" width="{node_width}" height="80" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
                f'<text x="{x + node_width / 2:g}" y="104" class="svg-label" text-anchor="middle">{h(short)}</text>'
            )
        rendered.append(f'''<figure class="explanation-figure">
<div><p class="eyebrow">圖解</p><h4>{h(visual.get("title"))}</h4><p>{h(visual.get("question"))}</p></div>
<svg class="explanation-visual" viewBox="0 0 {view_width} 168" role="img" aria-labelledby="{slug}-title {slug}-desc">
<title id="{slug}-title">{h(visual.get("title"))}</title><desc id="{slug}-desc">{h(visual.get("question"))} 流程為：{h('、'.join(nodes))}。</desc>
<defs><marker id="arrow-{slug}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#687782"/></marker></defs>
{''.join(arrows)}{''.join(boxes)}
</svg><figcaption>{h(visual.get("caption"))}</figcaption></figure>''')
    return "".join(rendered)


def report_html(state: dict[str, Any], title: str) -> str:
    outcome = state.get("outcome") or {}
    packages = state.get("clientPackages", [])
    work_items = state.get("workItems", [])
    package_totals = client_package_totals(state)
    effort_totals = package_effort_totals(state)
    review = state.get("estimationReview") or {}
    findings = review.get("criticalFindings", []) if isinstance(review.get("criticalFindings"), list) else []
    catalog_by_id = {
        item.get("id"): item for item in state.get("detailCatalogs", [])
        if isinstance(item, dict) and item.get("id")
    }
    total_low = sum(item_days(item)["low"] for item in work_items)
    total_baseline = sum(item_days(item)["baseline"] for item in work_items)
    total_high = sum(item_days(item)["high"] for item in work_items)

    package_rows: list[str] = []
    package_dialogs: list[str] = []
    for index, package in enumerate(packages, start=1):
        package_id = package.get("id")
        fragment = safe_fragment(package_id)
        dialog_id = f"package-{fragment}-dialog"
        items = [item for item in work_items if item.get("clientPackageId") == package_id]
        totals = package_totals.get(package_id, {})
        effort = effort_totals.get(package_id, {"development": {}, "testing": {}})
        related = [finding for finding in findings if package_id in finding.get("clientPackageIds", [])]
        work_html: list[str] = []
        for work_index, item in enumerate(items, start=1):
            pages, apis, files = (target_items(item, key) for key in ("pages", "apis", "files"))
            target_note = (item.get("changeTargets") or {}).get("notes")
            rates = item.get("unitDays") or {}
            days = item_days(item)
            item_effort = item_effort_days(item)
            catalogs = [catalog_by_id[catalog_id] for catalog_id in item.get("detailCatalogIds", []) if catalog_id in catalog_by_id]
            worksets = "".join(workset_html(catalog) for catalog in catalogs)
            work_html.append(f'''<article class="work-item">
<header><span class="work-index">{work_index}</span><h4>{h(item.get("name"))}</h4></header>
<p class="change-summary">{h(item.get("pmChangeSummary"))}</p>
<div class="target-grid"><section><h5>影響頁面（{len(pages)}）</h5>{html_list(pages)}</section><section><h5>影響 API（{len(apis)}）</h5>{html_list(apis)}</section><section><h5>對應檔案（{len(files)}）</h5>{html_list(files)}</section></div>
{f'<p class="target-note"><strong>落點說明：</strong>{h(target_note)}</p>' if target_note else ''}
<div class="worksets"><p class="eyebrow">同一份 Discovery 工作集合</p>{worksets}</div>
<div class="work-math" aria-label="{h(item.get('name'))}低基準高人天公式">
<div><span>低值</span><strong>{item.get('pricingUnits', 0)} × {rates.get('low', 0)} = {days['low']}</strong></div>
<div class="baseline"><span>基準公式</span><strong>{item.get('pricingUnits', 0)} × {rates.get('baseline', 0)} = {days['baseline']} 人天</strong></div>
<div><span>高值</span><strong>{item.get('pricingUnits', 0)} × {rates.get('high', 0)} = {days['high']}</strong></div>
</div>
<p class="baseline-rationale"><strong>基準為何這樣估：</strong>{h(item.get("baselineRationale"))}</p>
<p class="effort-split">基準拆分：開發 {item_effort['development']['baseline']} 人天／測試 {item_effort['testing']['baseline']} 人天</p>
</article>''')

        related_html: list[str] = []
        for finding in related:
            delta = finding.get("scopeDelta") or {}
            delta_line = ""
            if delta:
                delta_line = (
                    f' <span class="delta">範圍修正 {h(delta.get("assumed"))} → '
                    f'{h(delta.get("confirmed"))} {h(delta.get("subject"))}</span>'
                )
            related_html.append(f'''<article class="inline-finding" data-finding-id="{h(finding.get("id"))}">
<h4>{h(finding.get("title"))}</h4>
<div class="finding-visible">
<p><strong>人天怎麼看：</strong>{h(finding.get("estimateImpact"))}</p>
<p><strong>PM 現在要注意什麼：</strong>{h(finding.get("treatment"))}</p>
</div>
<details class="finding-basis"><summary>查看判斷依據</summary><ul>
<li><strong>原本怎麼算：</strong>{h(finding.get("statedAssumption"))}</li>
<li><strong>後來查到什麼：</strong>{h(finding.get("evidenceConclusion"))}{delta_line}</li>
<li><strong>為什麼重要：</strong>{h(finding.get("whyItMatters"))}</li></ul></details></article>''')
        finding_section = ""
        if related_html:
            finding_section = f'''<section class="dialog-section contextual-findings">
<div class="section-heading"><p class="eyebrow">這一項額外查到</p><h3>會影響本項判斷的發現</h3></div>{''.join(related_html)}</section>'''

        package_rows.append(f'''<button class="package-row" type="button" data-dialog="{dialog_id}" aria-haspopup="dialog">
<span class="package-rank">{index}</span>
<span class="package-copy"><strong>{h(package.get("name"))}</strong><small>{h(package.get("externalSummary"))}</small></span>
<span class="estimate low"><small>低</small><b>{totals.get('low', 0)}</b></span>
<span class="estimate baseline"><small>基準</small><b>{totals.get('baseline', 0)}</b></span>
<span class="estimate high"><small>高</small><b>{totals.get('high', 0)}</b></span>
<span class="open-cue">查看細節 <span aria-hidden="true">→</span></span>
</button>''')

        visuals = explanation_visuals(package)
        package_dialogs.append(f'''<dialog class="package-dialog" id="{dialog_id}" aria-labelledby="{dialog_id}-title" aria-describedby="{dialog_id}-summary">
<div class="dialog-shell">
<header class="dialog-header"><div><p class="eyebrow">評估項目 {index}／{len(packages)}</p><h2 id="{dialog_id}-title">{h(package.get("name"))}</h2></div><button class="dialog-close icon-close" type="button" data-close aria-label="關閉 {h(package.get('name'))}"><span aria-hidden="true">×</span></button></header>
<div class="dialog-scroll">
<p class="dialog-summary" id="{dialog_id}-summary">{h(package.get("externalSummary"))}</p>
<div class="effort-ledger" aria-label="低基準高人天"><div><span>低值</span><b>{totals.get('low', 0)}</b><small>條件順利</small></div><div class="focus"><span>基準值</span><b>{totals.get('baseline', 0)}</b><small>目前最可能</small></div><div><span>高值</span><b>{totals.get('high', 0)}</b><small>同範圍保守上限</small></div><div><span>基準開發／測試</span><b>{effort.get('development', {}).get('baseline', 0)}／{effort.get('testing', {}).get('baseline', 0)}</b><small>人天</small></div></div>
<section class="package-intro"><div><p class="eyebrow">為什麼要做</p><p>{h(package.get("whyRequired"))}</p></div><div><p class="eyebrow">怎麼完成</p><p>{h(package.get("deliveryApproach"))}</p></div></section>
{finding_section}
{visuals}
<section class="dialog-section"><div class="section-heading"><p class="eyebrow">逐項確認施工落點</p><h3>修改明細</h3></div>{''.join(work_html)}</section>
<section class="dialog-section calculation"><div class="section-heading"><p class="eyebrow">本項合計</p><h3>低／基準／高怎麼看</h3></div>
<dl class="tier-guide"><div><dt>低值 {totals.get('low', 0)}</dt><dd>以已確認的修改範圍計算，假設共用規則可順利套用、例外較少。</dd></div><div><dt>基準 {totals.get('baseline', 0)}</dt><dd>由上方每項工作的「計價單位 × 基準單價」加總，是目前證據下最可能的投入。</dd></div><div><dt>高值 {totals.get('high', 0)}</dt><dd>仍是同一範圍，另吸收已辨識的例外、整合與返工風險；不包含未說明的新需求。</dd></div></dl>
</section></div>
<footer class="dialog-footer"><button class="dialog-close return-button" type="button" data-close>回到評估項目</button></footer>
</div></dialog>''')

    scenario = selected_scenario(state)
    scenario_html = f'<h3>{h(scenario.get("name"))}</h3><p>{h(scenario.get("summary"))}</p>' if scenario else "<p>尚未由 PM 選定方案。</p>"
    nodes = (state.get("successChain") or {}).get("nodes", [])
    chain_html = html_list([f"{item.get('name')}（{item.get('owner')}）：{item.get('completionEvidence')}" for item in nodes], "成果成立條件尚未建立。")
    dependencies = state.get("dependencies", [])
    dependency_html = html_list([
        f"{item.get('component')}：{(item.get('resolution') or {}).get('selectedTarget')}；{(item.get('resolution') or {}).get('rationale')}；確認方式：{item.get('probe')}"
        for item in dependencies
    ], "本案沒有需改變方案的關鍵依賴。")
    evidence_html = html_list([item.get("claim", "") for item in state.get("evidence", [])], "尚未形成可交付的證據結論。")
    summary_heading = {"cr": "本次 CR 摘要", "upgrade": "本次升版摘要", "mixed": "本次評估摘要"}.get(state.get("mode"), "本次評估摘要")
    body = f'''<header class="report-header"><p class="kicker">Estimate／PM 確認台</p><h1>{h(state.get('name'))}</h1><p>案件版本 {state.get('revision')} · {h(STATE_LABELS.get(state.get('status'), state.get('status')))}</p></header>
<section class="summary-panel" aria-labelledby="case-summary"><div class="summary-main"><p class="eyebrow">先掌握這次要處理什麼</p><h2 id="case-summary">{summary_heading}</h2><p class="current-state">{h(outcome.get('pmCurrentState'))}</p><dl class="summary-facts"><div><dt>這次要達成</dt><dd>{h(outcome.get('goal'))}</dd></div><div><dt>責任邊界</dt><dd>{h(outcome.get('responsibilityBoundary'))}</dd></div></dl></div>
<aside class="total-ledger" aria-label="本次估算合計"><p class="eyebrow">全部項目合計</p><div><span>低</span><b>{total_low}</b></div><div class="baseline"><span>基準</span><b>{total_baseline}</b></div><div><span>高</span><b>{total_high}</b></div><small>單位：人天</small></aside></section>
<section class="estimate-section" aria-labelledby="estimate-heading"><div class="section-heading primary"><div><p class="eyebrow">逐項比較，再按需要下鑽</p><h2 id="estimate-heading">評估項目與人天</h2></div><p>每列先看原項目說明與低／基準／高；點擊後查看修改落點、計算方式，以及只屬於該項的額外發現。</p></div><div class="package-columns" aria-hidden="true"><span>項目與說明</span><span>低</span><span>基準</span><span>高</span><span></span></div><div class="package-list">{''.join(package_rows)}</div></section>
<section class="technical-appendix"><details><summary><span><small>需要追查時再看</small><strong>技術附錄</strong></span><span aria-hidden="true">＋</span></summary><div class="appendix-body"><section><h3>採用方案</h3>{scenario_html}</section><section><h3>做到哪些事才算交付</h3>{chain_html}</section><section><h3>會讓方案失敗或加價的前提</h3>{dependency_html}</section><section><h3>技術證據</h3>{evidence_html}</section></div></details></section>
{''.join(package_dialogs)}'''
    template_path = Path(__file__).resolve().parents[1] / "assets" / "assessment-report-template.html"
    template = Template(template_path.read_text(encoding="utf-8"))
    return template.substitute(title=html.escape(title), body=body)


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
    rendered_html = report_html(state, f"{state.get('name')} 評估報告")
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
        "stateStatus": state.get("status"),
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

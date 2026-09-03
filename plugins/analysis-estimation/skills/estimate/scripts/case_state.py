#!/usr/bin/env python3
"""Estimate case state: atomic revisioned writes and deterministic validation."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 8
STATE_FILE = "assessment-state.json"
LOCK_FILE = ".assessment-state.lock"
MODES = {"undetermined", "upgrade", "cr", "mixed"}
STATUSES = {"draft", "mapping", "estimate-ready", "complete"}
FORMAL_STATUSES = {"estimate-ready", "complete"}
GATE_TITLES = (
    "提供案件資料",
    "選擇成果大方向並確認工作分工",
    "核對案件理解",
    "選擇採用方案",
    "確認工作內容與人天",
    "取得交付成果",
)
NODE_STATUSES = {"done", "working", "needs-pm", "fog", "external", "blocked"}
DISPOSITIONS = {"priced", "zero", "external"}
WORK_KINDS = {"shared", "mechanical", "quantity", "exception", "verification"}
DEPENDENCY_COVERAGE_STATUSES = {"pending", "complete", "bounded", "blocked"}
DEPENDENCY_CRITICALITIES = {"critical", "material", "background"}
MAINTENANCE_STATUSES = {"active", "limited", "stale", "eol", "unknown"}
COMPATIBILITY_STATUSES = {"supported", "conditional", "unsupported", "unknown"}
DEPENDENCY_RESOLUTION_STATUSES = {"accepted", "conditional", "unresolved"}
DEPENDENCY_STRATEGIES = {"keep", "fork", "replace", "self-maintain", "stay", "vendor", "not-applicable", "unresolved"}
CRITICAL_FINDING_CATEGORIES = {"scope-gap", "feasibility", "responsibility", "estimation-model", "acceptance"}
DETAIL_CATALOG_TREATMENTS = {"direct-touch", "generated", "evidence-only"}
DETAIL_CATALOG_COMPLETENESS = {"complete", "summary", "partial"}
DETAIL_CATALOG_ORIGINS = {"discovery", "legacy-migration"}
DETAIL_CATALOG_PRICING_ROLES = {"pricing-unit", "scope-evidence"}
DETAIL_ITEM_ACTIONS = {"no-change", "batch-change", "manual-change", "high-risk-verify"}
ALLOWED_MERGE_KEYS = {
    "name", "mode", "status", "outcome", "currentDecision", "gates",
    "selectedScenarioId", "successChain", "outputs", "calibration", "dependencyCoverage", "estimationReview",
    "detailCatalogs",
}
COLLECTION_PATHS = {
    "dependencies": ("dependencies",),
    "evidence": ("evidence",),
    "fogs": ("fogs",),
    "scenarios": ("scenarios",),
    "nodes": ("successChain", "nodes"),
    "workItems": ("workItems",),
    "clientPackages": ("clientPackages",),
    "detailCatalogs": ("detailCatalogs",),
    "decisions": ("decisions",),
}


class CaseError(RuntimeError):
    """A user-actionable state error."""


@contextmanager
def case_lock(case_root: Path, timeout_seconds: float = 15.0):
    """Serialize every compare-and-swap across processes for one case.

    The lock is a stable sidecar rather than the JSON file itself because
    atomic replace changes the state file's inode/handle identity.
    """
    root = case_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = root / LOCK_FILE
    stream = path.open("a+b")
    acquired = False
    deadline = time.monotonic() + timeout_seconds
    try:
        if os.name == "nt":
            import msvcrt

            if path.stat().st_size == 0:
                stream.write(b"\0")
                stream.flush()
            while not acquired:
                stream.seek(0)
                try:
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                    acquired = True
                except OSError:
                    if time.monotonic() >= deadline:
                        raise CaseError("案件正在由另一個程序更新，等待鎖定逾時")
                    time.sleep(0.025)
        else:
            import fcntl

            while not acquired:
                try:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise CaseError("案件正在由另一個程序更新，等待鎖定逾時")
                    time.sleep(0.025)
        yield
    finally:
        if acquired:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


def configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned[:48] or "assessment-case"


def state_path(case_root: Path) -> Path:
    return case_root.resolve() / STATE_FILE


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", delete=False, dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    ) as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def load(case_root: Path) -> dict[str, Any]:
    path = state_path(case_root)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CaseError(f"找不到案件主檔：{path}") from exc
    except json.JSONDecodeError as exc:
        raise CaseError(f"案件主檔不是有效 JSON：{exc}") from exc
    if not isinstance(payload, dict):
        raise CaseError("案件主檔根節點必須是 object")
    return payload


def load_input(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CaseError(f"找不到輸入檔：{path}") from exc
    except json.JSONDecodeError as exc:
        raise CaseError(f"輸入檔不是有效 JSON：{exc}") from exc
    if not isinstance(value, dict):
        raise CaseError("輸入內容必須是 JSON object")
    return value


def default_state(case_id: str, name: str, goal: str, mode: str) -> dict[str, Any]:
    stamp = now_iso()
    return {
        "schemaVersion": SCHEMA_VERSION,
        "caseId": case_id,
        "name": name,
        "mode": mode,
        "status": "draft",
        "revision": 1,
        "createdAt": stamp,
        "updatedAt": stamp,
        "outcome": {
            "goal": goal,
            "acceptance": [],
            "preserve": [],
            "responsibilityBoundary": "待 PM 確認",
            "pmCurrentState": "",
        },
        "evidence": [],
        "dependencyCoverage": {
            "status": "pending",
            "source": "",
            "discoveryMethod": "",
            "componentCount": 0,
            "decisionBearingDependencyIds": [],
            "evidenceIds": [],
            "boundary": "",
        },
        "dependencies": [],
        "fogs": [],
        "scenarios": [],
        "selectedScenarioId": None,
        "successChain": {"destination": goal, "nodes": []},
        "workItems": [],
        "detailCatalogs": [],
        "clientPackages": [],
        "estimationReview": {
            "conclusion": "",
            "checkedPatterns": [],
            "criticalFindings": [],
        },
        "calibration": {
            "referenceAvailable": False,
            "unavailableReason": "尚未取得可比較的原建置報價、相似案實績或完成樣本",
        },
        "decisions": [],
        "currentDecision": {
            "id": "confirm-outcome",
            "title": "確認案件資料與初始目標",
            "whyHuman": "案件身分與最初需求會成為後續選擇成果方向的共同起點。",
            "factsTitle": "做決定前值得看的資訊",
            "facts": ["目前只有初始目標，技術範圍將由 Agent 查證。"],
            "choices": ["確認案件資料，進入成果方向選擇", "案件資料或初始目標需要調整", "其他（自行輸入）"],
            "next": "確認後，Agent 會在聊天呈現 Gate 2，請 PM 選擇這次要解到哪一層。",
            "requiresHuman": True,
        },
        "gates": [
            {"number": index, "title": title, "state": "current" if index == 1 else "pending"}
            for index, title in enumerate(GATE_TITLES, 1)
        ],
        "outputs": {},
    }


def ceil_half(value: float) -> float:
    return math.ceil((float(value) - 1e-9) * 2) / 2


def is_half_day(value: Any) -> bool:
    return isinstance(value, (int, float)) and value >= 0 and abs(float(value) * 2 - round(float(value) * 2)) < 1e-9


def item_days(item: dict[str, Any]) -> dict[str, float]:
    rates = item.get("unitDays") or {}
    quantity = int(item.get("pricingUnits", 0))
    return {
        key: ceil_half(quantity * float(rates.get(key, 0)))
        for key in ("low", "baseline", "high")
    }


def item_effort_days(item: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Return development/testing person-days from the same priced work item.

    The split is stored per pricing unit so external totals remain a projection
    of the internal estimate instead of a second, hand-maintained quotation.
    """
    quantity = int(item.get("pricingUnits", 0))
    split = item.get("effortSplit") or {}
    return {
        category: {
            tier: ceil_half(quantity * float((split.get(category) or {}).get(tier, 0)))
            for tier in ("low", "baseline", "high")
        }
        for category in ("development", "testing")
    }


def ids(items: list[Any], label: str, errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] 必須是 object")
            continue
        value = item.get("id")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}[{index}] 缺少 id")
        elif value in seen:
            errors.append(f"{label} id 重複：{value}")
        else:
            seen.add(value)
    return seen


def _text(value: Any) -> bool:
    """Whether a value contains human-readable content."""
    return isinstance(value, str) and bool(value.strip())


def validate_detail_catalogs(
    detail_catalogs: list[Any],
    work_items: list[Any],
    errors: list[str],
    formal: bool,
) -> None:
    """Validate the one canonical workset inventory shared by pricing and reports."""
    catalog_ids = ids(detail_catalogs, "detailCatalogs", errors)
    canonical_ids = set(catalog_ids)
    usage = {catalog_id: 0 for catalog_id in catalog_ids}

    for catalog in detail_catalogs:
        if not isinstance(catalog, dict):
            continue
        catalog_id = catalog.get("id")
        treatment = catalog.get("treatment")
        for key, label in (("name", "名稱"), ("origin", "來源"), ("pricingRole", "計價角色")):
            if formal and not _text(catalog.get(key)):
                errors.append(f"detail catalog {catalog_id} 缺少{label}")
        if treatment not in DETAIL_CATALOG_TREATMENTS:
            errors.append(f"detail catalog {catalog_id} treatment 無效")
        if catalog.get("origin") not in DETAIL_CATALOG_ORIGINS:
            errors.append(f"detail catalog {catalog_id} origin 無效")
        if catalog.get("pricingRole") not in DETAIL_CATALOG_PRICING_ROLES:
            errors.append(f"detail catalog {catalog_id} pricingRole 無效")
        completeness = catalog.get("completeness")
        if completeness not in DETAIL_CATALOG_COMPLETENESS:
            errors.append(f"detail catalog {catalog_id} completeness 無效")
        claimed_count = catalog.get("claimedCount")
        if not isinstance(claimed_count, int) or claimed_count < 0:
            errors.append(f"detail catalog {catalog_id} claimedCount 必須是非負整數")
            claimed_count = None

        items = catalog.get("items")
        if treatment == "direct-touch":
            if formal and completeness != "complete":
                errors.append(f"direct-touch detail catalog {catalog_id} 必須宣告 complete")
            if not isinstance(items, list):
                if formal:
                    errors.append(f"direct-touch detail catalog {catalog_id} 必須提供完整 items")
                items = []
            if formal and claimed_count is not None and claimed_count != len(items):
                errors.append(
                    f"direct-touch detail catalog {catalog_id} claimedCount {claimed_count} "
                    f"與完整 items {len(items)} 不一致；Gate 5 前必須回到 discovery"
                )
            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"detail catalog {catalog_id} items[{index}] 必須是 object")
                    continue
                item_id = item.get("id")
                if not _text(item_id):
                    errors.append(f"detail catalog {catalog_id} items[{index}] 缺少 stable id")
                elif item_id in canonical_ids:
                    errors.append(f"canonical detail id 重複：{item_id}")
                else:
                    canonical_ids.add(str(item_id))
                for key, label in (
                    ("name", "名稱或路徑"), ("purpose", "用途"),
                    ("changeDetail", "修改重點"), ("verification", "驗證方式"),
                ):
                    if not _text(item.get(key)):
                        errors.append(f"detail item {item_id} 缺少{label}")
                if item.get("action") not in DETAIL_ITEM_ACTIONS:
                    errors.append(f"detail item {item_id} action 無效")
        elif treatment == "generated":
            if isinstance(items, list) and items:
                errors.append(f"generated detail catalog {catalog_id} 不應建立逐產物 items 清單")
            generation = catalog.get("generation")
            if not isinstance(generation, dict):
                errors.append(f"generated detail catalog {catalog_id} 缺少 generation")
            else:
                for key, label in (("source", "產製來源"), ("method", "產製方式"), ("verification", "核對方式")):
                    if not _text(generation.get(key)):
                        errors.append(f"generated detail catalog {catalog_id} 缺少{label}")
        elif treatment == "evidence-only":
            if not _text(catalog.get("explanation")):
                errors.append(f"evidence-only detail catalog {catalog_id} 缺少用途說明")
            if completeness == "complete":
                if not isinstance(items, list):
                    errors.append(f"complete evidence-only detail catalog {catalog_id} 必須提供 items")
                elif claimed_count is not None and claimed_count != len(items):
                    errors.append(f"evidence-only detail catalog {catalog_id} claimedCount 與 items 不一致")
            if isinstance(items, list):
                for index, item in enumerate(items):
                    if not isinstance(item, dict):
                        errors.append(f"detail catalog {catalog_id} items[{index}] 必須是 object")
                        continue
                    item_id = item.get("id")
                    if not _text(item_id):
                        errors.append(f"detail catalog {catalog_id} items[{index}] 缺少 stable id")
                    elif item_id in canonical_ids:
                        errors.append(f"canonical detail id 重複：{item_id}")
                    else:
                        canonical_ids.add(str(item_id))
                    if not _text(item.get("name")):
                        errors.append(f"detail item {item_id} 缺少名稱或路徑")

    for work_item in work_items:
        if not isinstance(work_item, dict):
            continue
        work_item_id = work_item.get("id")
        references = work_item.get("detailCatalogIds")
        if not isinstance(references, list) or not references or not all(_text(value) for value in references):
            if formal:
                errors.append(f"work item {work_item_id} 缺少 canonical detailCatalogIds")
            continue
        if len(references) != len(set(references)):
            errors.append(f"work item {work_item_id} detailCatalogIds 不可重複")
        for catalog_id in references:
            if catalog_id not in catalog_ids:
                errors.append(f"work item {work_item_id} 引用不存在 detail catalog：{catalog_id}")
            else:
                usage[catalog_id] += 1

    if formal:
        if not detail_catalogs:
            errors.append("正式狀態必須建立 canonical detailCatalogs")
        for catalog_id, count in usage.items():
            if count == 0:
                errors.append(f"detail catalog {catalog_id} 沒有 work item 引用")


def _dependency_is_blocking(item: Any) -> bool:
    """Derive whether current dependency evidence still invalidates a route."""
    if not isinstance(item, dict):
        return True
    if item.get("blocksScenario") is True or item.get("maintenanceStatus") == "unknown":
        return True
    resolution = item.get("resolution")
    if not isinstance(resolution, dict) or resolution.get("status") == "unresolved":
        return True
    selected_target = resolution.get("selectedTarget")
    selected_claim = next(
        (
            claim for claim in item.get("compatibilityClaims", [])
            if isinstance(claim, dict) and claim.get("target") == selected_target
        ),
        None,
    )
    return not isinstance(selected_claim, dict) or selected_claim.get("status") not in {"supported", "conditional"}


def _formal_readiness_errors(
    state: dict[str, Any],
    scenarios: list[Any],
    nodes: list[Any],
    work_items: list[Any],
    dependencies: list[Any],
    evidence: list[Any],
    fogs: list[Any],
    client_packages: list[Any],
) -> list[str]:
    """Return hard blockers for states that claim to be formally ready.

    Draft and mapping states intentionally do not use these checks as errors:
    they are useful, saveable intermediate states.  The checks below only
    protect the boundary where the state is presented as estimate-ready or
    complete.  They verify presence, references and consistency; they do not
    attempt to judge whether a model's evidence or estimate is subjectively
    good enough.
    """
    if state.get("status") not in FORMAL_STATUSES:
        return []

    errors: list[str] = []
    selected_id = state.get("selectedScenarioId")
    selected = next(
        (item for item in scenarios if isinstance(item, dict) and item.get("id") == selected_id),
        None,
    )
    if selected is None:
        errors.append("正式狀態必須有 PM 已選定的方案")
    else:
        for key, label in (("name", "方案名稱"), ("summary", "方案摘要")):
            if not _text(selected.get(key)):
                errors.append(f"已選方案缺少{label}")

    decisions = state.get("decisions", [])
    if not any(
        isinstance(item, dict) and item.get("decisionId") == "select-outcome-direction"
        for item in decisions
    ):
        errors.append("正式狀態缺少 PM 在 Gate 2 確認成果大方向的決策紀錄")

    for item in fogs:
        if not isinstance(item, dict) or item.get("status", "open") == "resolved":
            continue
        if item.get("requiresHuman") is True:
            errors.append(f"重要 PM 決定尚未確認：{item.get('id')}")
        if item.get("blocksReadiness") is True:
            errors.append(f"正式估算的關鍵事實尚未收斂：{item.get('id')}")

    outcome = state.get("outcome")
    if not isinstance(outcome, dict):
        errors.append("正式狀態必須有完整的成果與責任邊界")
    else:
        acceptance = outcome.get("acceptance")
        if not isinstance(acceptance, list) or not acceptance or not all(_text(value) for value in acceptance):
            errors.append("正式狀態必須列出至少一項可驗收成果")
        if not _text(outcome.get("responsibilityBoundary")) or outcome.get("responsibilityBoundary") in {"待 PM 確認", "待確認"}:
            errors.append("正式狀態必須明確寫出責任邊界")
        if not _text(outcome.get("pmCurrentState")):
            errors.append("正式狀態必須提供可直接轉述的 PM 現況結論")

    chain = state.get("successChain")
    if not isinstance(chain, dict) or not _text(chain.get("destination")):
        errors.append("正式狀態必須有成功鏈成果終點")
    if not nodes:
        errors.append("正式狀態必須建立至少一個成功鏈節點")

    priced_node_ids: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if node.get("status") not in {"done", "external"}:
            errors.append(f"成功鏈節點 {node_id} 尚未收斂，不能進入正式狀態")
        if not _text(node.get("owner")):
            errors.append(f"成功鏈節點 {node_id} 缺少責任人")
        if not isinstance(node.get("evidenceIds"), list) or not node.get("evidenceIds"):
            errors.append(f"成功鏈節點 {node_id} 缺少可追溯證據")
        if node.get("disposition") == "priced":
            priced_node_ids.add(str(node_id))
            if not isinstance(node.get("needsChange"), int) or node.get("needsChange", 0) < 1:
                errors.append(f"計價節點 {node_id} 必須有至少一項需處理內容")
        unknown = node.get("unknown", 0)
        if isinstance(unknown, int) and unknown > 0 and not _text(node.get("unknownBoundary") or node.get("unknownReason")):
            errors.append(f"成功鏈節點 {node_id} 仍有未知數量，需寫出可估算的未知邊界")

    # 升版與混合案的依賴本身就是可行性證據；CR 是否觸及依賴則由模型
    # 判斷，若已建立 dependency rows，仍要求每列可被人讀懂。
    dependency_required = state.get("mode") in {"upgrade", "mixed"}
    dependency_ids = {
        str(item.get("id")) for item in dependencies
        if isinstance(item, dict) and _text(item.get("id"))
    }
    if dependency_required and not dependencies:
        errors.append("升版／混合案件正式估算前必須建立 dependency behavior 證據")
    coverage = state.get("dependencyCoverage")
    if dependency_required:
        if not isinstance(coverage, dict):
            errors.append("升版／混合案件正式估算前必須建立 dependency coverage")
        else:
            coverage_status = coverage.get("status")
            if coverage_status not in {"complete", "bounded"}:
                errors.append("dependency coverage 必須完成，或以明確邊界收斂")
            for key, label in (("source", "實際依賴來源"), ("discoveryMethod", "依賴發現方法")):
                if not _text(coverage.get(key)):
                    errors.append(f"dependency coverage 缺少{label}")
            component_count = coverage.get("componentCount")
            if not isinstance(component_count, int) or component_count < len(dependency_ids):
                errors.append("dependency coverage.componentCount 不可小於需深入判斷的依賴數")
            if coverage_status == "bounded" and not _text(coverage.get("boundary")):
                errors.append("bounded dependency coverage 必須說明盤點邊界")
            covered_ids = coverage.get("decisionBearingDependencyIds")
            if not isinstance(covered_ids, list) or not all(_text(value) for value in covered_ids):
                errors.append("dependency coverage 的 dependency id 必須是非空文字")
            elif set(covered_ids) != dependency_ids:
                errors.append("dependency coverage 必須完整列出所有會影響方案的 dependency id")
            coverage_evidence = coverage.get("evidenceIds")
            if not isinstance(coverage_evidence, list) or not coverage_evidence or not all(_text(value) for value in coverage_evidence):
                errors.append("dependency coverage 缺少可追溯證據")
            else:
                for evidence_id in coverage_evidence:
                    if evidence_id not in {item.get("id") for item in evidence if isinstance(item, dict)}:
                        errors.append(f"dependency coverage 證據不存在：{evidence_id}")
    dependency_fields = (
        ("component", "元件"), ("current", "現行版本"), ("target", "目標版本"),
        ("upstreamSource", "上游來源"), ("upstreamMaintainer", "上游維護者"),
        ("internalOwner", "內部工作責任"), ("criticalityReason", "方案影響理由"),
        ("usage", "系統用途"), ("buildTime", "建置期機制"),
        ("extensions", "整合擴充點"), ("probe", "驗證方式"),
    )
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            continue
        dependency_id = dependency.get("id")
        for key, label in dependency_fields:
            if not _text(dependency.get(key)):
                errors.append(f"dependency {dependency_id} 缺少{label}")
        if dependency.get("criticality") not in DEPENDENCY_CRITICALITIES:
            errors.append(f"dependency {dependency_id} criticality 無效")
        if dependency.get("maintenanceStatus") not in MAINTENANCE_STATUSES:
            errors.append(f"dependency {dependency_id} maintenanceStatus 無效")
        elif dependency.get("maintenanceStatus") == "unknown":
            errors.append(f"dependency {dependency_id} 尚未確認上游維護狀態")
        if "semanticBreaks" not in dependency or not isinstance(dependency.get("semanticBreaks"), list):
            errors.append(f"dependency {dependency_id} 缺少語意斷點清單")
        elif not all(_text(value) for value in dependency.get("semanticBreaks", [])):
            errors.append(f"dependency {dependency_id} 語意斷點必須是文字")
        dependency_evidence = dependency.get("evidenceIds")
        if not isinstance(dependency_evidence, list) or not dependency_evidence or not all(_text(value) for value in dependency_evidence):
            errors.append(f"dependency {dependency_id} 缺少證據追溯")
        else:
            for evidence_id in dependency_evidence:
                if evidence_id not in {item.get("id") for item in evidence if isinstance(item, dict)}:
                    errors.append(f"dependency {dependency_id} 證據不存在：{evidence_id}")

        footprint = dependency.get("footprint")
        if not isinstance(footprint, dict):
            errors.append(f"dependency {dependency_id} 缺少完整使用足跡")
        else:
            for key, label in (("discoveryMethod", "使用全集發現方法"), ("scope", "使用範圍")):
                if not _text(footprint.get(key)):
                    errors.append(f"dependency {dependency_id} footprint 缺少{label}")
            if not isinstance(footprint.get("highRiskApis"), list) or not all(_text(value) for value in footprint.get("highRiskApis", [])):
                errors.append(f"dependency {dependency_id} footprint 缺少高風險 API 分類")

        claims = dependency.get("compatibilityClaims")
        claim_by_target: dict[str, dict[str, Any]] = {}
        claim_statuses: set[str] = set()
        if not isinstance(claims, list) or not claims:
            errors.append(f"dependency {dependency_id} 缺少目標相容性主張")
        else:
            for index, claim in enumerate(claims):
                if not isinstance(claim, dict):
                    errors.append(f"dependency {dependency_id} compatibilityClaims[{index}] 必須是 object")
                    continue
                target = claim.get("target")
                status = claim.get("status")
                if not _text(target):
                    errors.append(f"dependency {dependency_id} compatibility claim 缺少目標")
                else:
                    if str(target) in claim_by_target:
                        errors.append(f"dependency {dependency_id} compatibility claim 目標重複：{target}")
                    claim_by_target[str(target)] = claim
                if status not in COMPATIBILITY_STATUSES:
                    errors.append(f"dependency {dependency_id} compatibility status 無效")
                else:
                    claim_statuses.add(str(status))
                if not _text(claim.get("rationale")):
                    errors.append(f"dependency {dependency_id} compatibility claim 缺少判斷理由")
                claim_evidence = claim.get("evidenceIds")
                if status in {"supported", "conditional", "unsupported"} and (
                    not isinstance(claim_evidence, list) or not claim_evidence or not all(_text(value) for value in claim_evidence)
                ):
                    errors.append(f"dependency {dependency_id} compatibility claim 缺少證據")
                if isinstance(claim_evidence, list) and not all(_text(value) for value in claim_evidence):
                    errors.append(f"dependency {dependency_id} compatibility evidence id 必須是非空文字")
                if isinstance(claim_evidence, list) and all(_text(value) for value in claim_evidence):
                    for evidence_id in claim_evidence:
                        if evidence_id not in {item.get("id") for item in evidence if isinstance(item, dict)}:
                            errors.append(f"dependency {dependency_id} compatibility 證據不存在：{evidence_id}")

        resolution = dependency.get("resolution")
        if not isinstance(resolution, dict):
            errors.append(f"dependency {dependency_id} 缺少採用路線結論")
        else:
            for key, label in (("selectedTarget", "採用目標"), ("rationale", "採用理由"), ("owner", "承擔責任")):
                if not _text(resolution.get(key)):
                    errors.append(f"dependency {dependency_id} resolution 缺少{label}")
            if resolution.get("status") not in DEPENDENCY_RESOLUTION_STATUSES:
                errors.append(f"dependency {dependency_id} resolution status 無效")
            if resolution.get("strategy") not in DEPENDENCY_STRATEGIES:
                errors.append(f"dependency {dependency_id} resolution strategy 無效")
            selected_claim = claim_by_target.get(str(resolution.get("selectedTarget")))
            if selected_claim is None:
                errors.append(f"dependency {dependency_id} 採用目標沒有對應 compatibility claim")
            elif selected_claim.get("status") not in {"supported", "conditional"}:
                errors.append(f"dependency {dependency_id} 採用目標仍未具備可承諾的相容性")
            if resolution.get("status") == "unresolved":
                errors.append(f"dependency {dependency_id} 採用路線尚未收斂")
        fallback_strategies = dependency.get("fallbackStrategies")
        if not isinstance(fallback_strategies, list) or not all(_text(value) for value in fallback_strategies):
            errors.append(f"dependency {dependency_id} 缺少替代策略清單")
        elif claim_statuses.intersection({"unsupported", "unknown"}) and not fallback_strategies:
            errors.append(f"dependency {dependency_id} 面對不支持／未知組合時必須列出替代策略")
        if not isinstance(dependency.get("blocksScenario"), bool):
            errors.append(f"dependency {dependency_id} blocksScenario 必須是 boolean")
        elif dependency.get("blocksScenario"):
            errors.append(f"dependency {dependency_id} 仍會推翻目前方案")
    if dependency_required and not evidence:
        errors.append("升版／混合案件正式估算前必須有可追溯技術證據")

    required_work_fields = (
        ("package", "包別"), ("name", "工作名稱"), ("description", "技術說明"),
        ("pmDescription", "PM 說明"), ("includes", "包含範圍"),
        ("excludes", "排除範圍"), ("completionEvidence", "完成證據"),
        ("owner", "責任人"), ("currentConstraint", "現況限制"),
        ("changeMethod", "實際改法"), ("customerOutcome", "客戶成果"),
        ("scaleEvidence", "規模證據"), ("countingRationale", "計價理由"),
        ("rateBasis", "費率依據"), ("baselineRationale", "基準人天理由"),
        ("dedupeBoundary", "去重邊界"),
        ("clientPackageId", "客戶成果包歸屬"),
    )
    if not work_items:
        errors.append("正式狀態必須有由成功鏈推導出的工作項目")
    for item in work_items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        for key, label in required_work_fields:
            if not _text(item.get(key)):
                errors.append(f"work item {item_id} 缺少 PM 可說明的{label}")
        pm_change_summary = item.get("pmChangeSummary")
        if not _text(pm_change_summary) or not 80 <= len(pm_change_summary.strip()) <= 160 or "\n" in pm_change_summary:
            errors.append(f"work item {item_id} 必須提供 80～160 字修改重點")
        change_targets = item.get("changeTargets")
        if not isinstance(change_targets, dict):
            errors.append(f"work item {item_id} 缺少頁面／API／檔案落點")
        else:
            target_values: list[str] = []
            targets_valid = True
            for key in ("pages", "apis", "files"):
                values = change_targets.get(key)
                if not isinstance(values, list) or not all(_text(value) for value in values):
                    errors.append(f"work item {item_id} changeTargets.{key} 必須是文字陣列")
                    targets_valid = False
                elif isinstance(values, list):
                    target_values.extend(values)
            if targets_valid and not target_values and not _text(change_targets.get("notes")):
                errors.append(f"work item {item_id} 頁面／API／檔案皆不涉及時必須說明原因")
        pricing_units = item.get("pricingUnits")
        if not isinstance(pricing_units, int) or pricing_units < 1:
            errors.append(f"work item {item_id} 必須明確提供至少 1 個計價單位")
        if not isinstance(item.get("nodeIds"), list) or not item.get("nodeIds"):
            errors.append(f"work item {item_id} 缺少成功條件追溯")
        if not isinstance(item.get("evidenceIds"), list) or not item.get("evidenceIds"):
            errors.append(f"work item {item_id} 缺少證據追溯")
        unknown = item.get("unknown", 0)
        if isinstance(unknown, int) and unknown > 0 and not _text(item.get("unknownBoundary") or item.get("unknownReason")):
            errors.append(f"work item {item_id} 仍有未知數量，需寫出可估算的未知邊界")

    package_fields = (
        ("name", "成果包名稱"), ("whyRequired", "必要性"),
        ("deliveryApproach", "處理方式"), ("customerOutcome", "客戶成果"),
        ("scopeEvidence", "範圍證據"), ("owner", "責任人"),
        ("externalSummary", "對外功能說明"),
    )
    if not client_packages:
        errors.append("正式狀態必須建立 PM 可說明的客戶成果包")
    for package in client_packages:
        if not isinstance(package, dict):
            continue
        package_id = package.get("id")
        for key, label in package_fields:
            if not _text(package.get(key)):
                errors.append(f"client package {package_id} 缺少{label}")
        package_name = package.get("name") if isinstance(package.get("name"), str) else ""
        if len(package_name.strip()) > 40:
            errors.append(f"client package {package_id} 系統功能名稱應在 40 字內")
        external_summary = package.get("externalSummary") if isinstance(package.get("externalSummary"), str) else ""
        external_summary = external_summary.strip()
        if "\n" in external_summary or len(external_summary) > 220:
            errors.append(f"client package {package_id} 對外功能說明應為 220 字內的單段說明")

    estimation_review = state.get("estimationReview")
    if not isinstance(estimation_review, dict):
        errors.append("正式狀態必須完成估算模型反證")
    else:
        if not _text(estimation_review.get("conclusion")):
            errors.append("正式狀態的估算模型反證缺少白話結論")
        checked_patterns = estimation_review.get("checkedPatterns")
        if not isinstance(checked_patterns, list) or not checked_patterns or not all(_text(value) for value in checked_patterns):
            errors.append("正式狀態的估算模型反證必須列出已檢查的替代解釋")
        findings = estimation_review.get("criticalFindings")
        if not isinstance(findings, list):
            errors.append("estimationReview.criticalFindings 必須是 array")
        else:
            finding_ids: set[str] = set()
            package_ids = {str(item.get("id")) for item in client_packages if isinstance(item, dict)}
            known_evidence_ids = {str(item.get("id")) for item in evidence if isinstance(item, dict)}
            work_item_by_id = {
                str(item.get("id")): item for item in work_items
                if isinstance(item, dict) and _text(item.get("id"))
            }
            detail_catalog_by_id = {
                str(item.get("id")): item for item in state.get("detailCatalogs", [])
                if isinstance(item, dict) and _text(item.get("id"))
            }
            required_finding_fields = (
                ("title", "標題"), ("statedAssumption", "原本以為"),
                ("evidenceConclusion", "證據結論"), ("whyItMatters", "重要性"),
                ("estimateImpact", "估算影響"), ("treatment", "目前處理方式"),
            )
            for finding in findings:
                if not isinstance(finding, dict):
                    errors.append("critical finding 必須是 object")
                    continue
                finding_id = finding.get("id")
                if not _text(finding_id):
                    errors.append("critical finding 缺少 id")
                elif finding_id in finding_ids:
                    errors.append(f"critical finding id 重複：{finding_id}")
                else:
                    finding_ids.add(finding_id)
                for key, label in required_finding_fields:
                    if not _text(finding.get(key)):
                        errors.append(f"critical finding {finding_id} 缺少{label}")
                if finding.get("category") not in CRITICAL_FINDING_CATEGORIES:
                    errors.append(f"critical finding {finding_id} category 無效")
                if finding.get("category") == "scope-gap":
                    delta = finding.get("scopeDelta")
                    if not isinstance(delta, dict):
                        errors.append(f"critical finding {finding_id} 範圍落差缺少 scopeDelta")
                    else:
                        subject = delta.get("subject")
                        assumed = delta.get("assumed")
                        confirmed = delta.get("confirmed")
                        target_key = delta.get("targetKey")
                        work_item_ids = delta.get("workItemIds")
                        detail_catalog_ids = delta.get("detailCatalogIds")
                        if not _text(subject):
                            errors.append(f"critical finding {finding_id} scopeDelta 缺少比較對象")
                        if not isinstance(assumed, int) or assumed < 0 or not isinstance(confirmed, int) or confirmed < 0:
                            errors.append(f"critical finding {finding_id} scopeDelta 數量必須是非負整數")
                        elif assumed == confirmed:
                            errors.append(f"critical finding {finding_id} scopeDelta 必須真的存在數量落差")
                        if target_key not in {"pages", "apis", "files"}:
                            errors.append(f"critical finding {finding_id} scopeDelta.targetKey 無效")
                        if not isinstance(work_item_ids, list) or not work_item_ids or not all(_text(value) for value in work_item_ids):
                            errors.append(f"critical finding {finding_id} scopeDelta 缺少 work item 追溯")
                        else:
                            for work_item_id in work_item_ids:
                                work_item = work_item_by_id.get(work_item_id)
                                if work_item is None:
                                    errors.append(f"critical finding {finding_id} 引用不存在 work item：{work_item_id}")
                        if not isinstance(detail_catalog_ids, list) or not detail_catalog_ids or not all(_text(value) for value in detail_catalog_ids):
                            errors.append(f"critical finding {finding_id} scopeDelta 缺少 canonical detail catalog 追溯")
                        else:
                            named_count = 0
                            countable = True
                            for catalog_id in detail_catalog_ids:
                                catalog = detail_catalog_by_id.get(catalog_id)
                                if catalog is None:
                                    errors.append(f"critical finding {finding_id} 引用不存在 detail catalog：{catalog_id}")
                                    countable = False
                                    continue
                                if catalog.get("treatment") != "direct-touch":
                                    errors.append(f"critical finding {finding_id} 的範圍落差必須引用 direct-touch detail catalog：{catalog_id}")
                                    countable = False
                                    continue
                                named_count += len(catalog.get("items", [])) if isinstance(catalog.get("items"), list) else 0
                            if countable and isinstance(confirmed, int) and named_count != confirmed:
                                errors.append(
                                    f"critical finding {finding_id} 證據確認 {confirmed} 項，"
                                    f"但 canonical direct-touch 清單只有 {named_count} 項；Gate 5 前必須回到 discovery 補齊"
                                )
                linked_packages = finding.get("clientPackageIds")
                if not isinstance(linked_packages, list) or not linked_packages or not all(_text(value) for value in linked_packages):
                    errors.append(f"critical finding {finding_id} 缺少 client package 追溯")
                else:
                    for package_id in linked_packages:
                        if package_id not in package_ids:
                            errors.append(f"critical finding {finding_id} 引用不存在 client package：{package_id}")
                linked_evidence = finding.get("evidenceIds")
                if not isinstance(linked_evidence, list) or not linked_evidence or not all(_text(value) for value in linked_evidence):
                    errors.append(f"critical finding {finding_id} 缺少 evidence 追溯")
                else:
                    for evidence_id in linked_evidence:
                        if evidence_id not in known_evidence_ids:
                            errors.append(f"critical finding {finding_id} 引用不存在 evidence：{evidence_id}")

    calibration = state.get("calibration")
    if not isinstance(calibration, dict) or not isinstance(calibration.get("referenceAvailable"), bool):
        errors.append("正式狀態必須說明是否有歷史建置成本或相似案校準資料")
    elif calibration.get("referenceAvailable"):
        for key, label in (
            ("label", "校準基準名稱"), ("scope", "校準範圍"),
            ("source", "校準來源"), ("comparisonConclusion", "合理性結論"),
        ):
            if not _text(calibration.get(key)):
                errors.append(f"calibration 缺少{label}")
        reference_days = calibration.get("referenceDays")
        if not isinstance(reference_days, (int, float)) or reference_days <= 0:
            errors.append("calibration.referenceDays 必須是正數")
        else:
            total_high = sum(item_days(item)["high"] for item in work_items if isinstance(item, dict))
            if total_high >= float(reference_days) * 0.8 and not _text(calibration.get("rebuildLikeOutcome")):
                errors.append("純升版高值接近歷史建置成本時，必須說明客戶額外取得的重建型成果或回到工作切片重審")
    elif not _text(calibration.get("unavailableReason")):
        errors.append("缺少歷史校準資料時必須說明 unavailableReason")

    # Gate 是 PM 進度的承諾投影。正式狀態只接受與目前門檻相符的形狀。
    gates = state.get("gates")
    if not isinstance(gates, list) or len(gates) != len(GATE_TITLES):
        errors.append("正式狀態必須有完整的六個 PM gate")
    else:
        seen_numbers: set[int] = set()
        seen_titles: set[str] = set()
        for gate in gates:
            if not isinstance(gate, dict):
                errors.append("正式狀態的 PM gate 必須是 object")
                continue
            number = gate.get("number")
            title = gate.get("title")
            if not isinstance(number, int) or number < 1 or number > len(GATE_TITLES):
                errors.append("正式狀態的 PM gate 編號無效")
                continue
            if number in seen_numbers:
                errors.append(f"PM gate 編號重複：{number}")
            seen_numbers.add(number)
            if title != GATE_TITLES[number - 1]:
                errors.append(f"PM gate {number} 名稱與標準不一致")
            if title in seen_titles:
                errors.append(f"PM gate 名稱重複：{title}")
            seen_titles.add(title)
            if gate.get("state") not in {"done", "current", "pending"}:
                errors.append(f"PM gate {number} 狀態無效")
        expected = {1: "done", 2: "done", 3: "done", 4: "done", 5: "current", 6: "pending"}
        if state.get("status") == "complete":
            expected = {number: "done" for number in range(1, len(GATE_TITLES) + 1)}
        by_number = {gate.get("number"): gate for gate in gates if isinstance(gate, dict)}
        for number, expected_state in expected.items():
            gate = by_number.get(number)
            if gate is not None and gate.get("state") != expected_state:
                errors.append(f"正式狀態的 PM gate {number} 應為「{expected_state}」")

    if state.get("status") == "estimate-ready":
        decision = state.get("currentDecision")
        if not isinstance(decision, dict) or decision.get("id") != "confirm-estimate":
            errors.append("estimate-ready 必須保留 PM 確認人天的目前決定")
    elif state.get("status") == "complete":
        if state.get("currentDecision") is not None:
            errors.append("complete 狀態不應保留待 PM 回答的目前決定")
        if not any(isinstance(item, dict) and item.get("decisionId") == "confirm-estimate" for item in state.get("decisions", [])):
            errors.append("complete 狀態缺少 PM 確認人天的決定紀錄")

    # priced coverage 的詳細引用與數量守恆已由一般 validator 檢查；這裡
    # 再確認正式狀態沒有完全脫離成功鏈的工作項目。
    covered: set[str] = set()
    for item in work_items:
        if not isinstance(item, dict):
            continue
        for node_id in item.get("nodeIds", []):
            if str(node_id) in priced_node_ids:
                covered.add(str(node_id))
    for node_id in sorted(priced_node_ids - covered):
        errors.append(f"正式狀態的計價節點 {node_id} 沒有工作項目承接")
    return errors


def validate_state(state: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if state.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion 必須是 {SCHEMA_VERSION}")
    if not isinstance(state.get("caseId"), str) or not state.get("caseId"):
        errors.append("caseId 不可為空")
    if state.get("mode") not in MODES:
        errors.append(f"mode 必須是 {sorted(MODES)}")
    if state.get("status") not in STATUSES:
        errors.append(f"status 必須是 {sorted(STATUSES)}")
    if not isinstance(state.get("revision"), int) or state.get("revision", 0) < 1:
        errors.append("revision 必須是正整數")
    outcome = state.get("outcome")
    if not isinstance(outcome, dict) or not str(outcome.get("goal", "")).strip():
        errors.append("outcome.goal 不可為空")

    evidence = state.get("evidence", [])
    dependency_coverage = state.get("dependencyCoverage")
    dependencies = state.get("dependencies", [])
    fogs = state.get("fogs", [])
    scenarios = state.get("scenarios", [])
    nodes = (state.get("successChain") or {}).get("nodes", [])
    work_items = state.get("workItems", [])
    detail_catalogs = state.get("detailCatalogs", [])
    client_packages = state.get("clientPackages", [])
    for value, label in ((evidence, "evidence"), (dependencies, "dependencies"), (fogs, "fogs"), (scenarios, "scenarios"), (nodes, "successChain.nodes"), (work_items, "workItems"), (detail_catalogs, "detailCatalogs"), (client_packages, "clientPackages")):
        if not isinstance(value, list):
            errors.append(f"{label} 必須是 array")

    if errors:
        return errors, warnings

    if not isinstance(dependency_coverage, dict):
        errors.append("dependencyCoverage 必須是 object")
    else:
        if dependency_coverage.get("status") not in DEPENDENCY_COVERAGE_STATUSES:
            errors.append(f"dependencyCoverage.status 必須是 {sorted(DEPENDENCY_COVERAGE_STATUSES)}")
        if not isinstance(dependency_coverage.get("componentCount"), int) or dependency_coverage.get("componentCount", 0) < 0:
            errors.append("dependencyCoverage.componentCount 必須是非負整數")
        for key in ("decisionBearingDependencyIds", "evidenceIds"):
            if not isinstance(dependency_coverage.get(key), list):
                errors.append(f"dependencyCoverage.{key} 必須是 array")

    for item in fogs:
        if not isinstance(item, dict):
            continue
        if item.get("status", "open") not in {"open", "resolved"}:
            errors.append(f"fog {item.get('id')} status 無效")
        if not isinstance(item.get("requiresHuman"), bool):
            errors.append(f"fog {item.get('id')} requiresHuman 必須是 boolean")
        if not isinstance(item.get("blocksReadiness"), bool):
            errors.append(f"fog {item.get('id')} blocksReadiness 必須是 boolean")

    evidence_ids = ids(evidence, "evidence", errors)
    ids(dependencies, "dependencies", errors)
    scenario_ids = ids(scenarios, "scenarios", errors)
    node_ids = ids(nodes, "successChain.nodes", errors)
    ids(fogs, "fogs", errors)
    ids(work_items, "workItems", errors)
    client_package_ids = ids(client_packages, "clientPackages", errors)
    validate_detail_catalogs(detail_catalogs, work_items, errors, state.get("status") in FORMAL_STATUSES)
    for package in client_packages:
        if not isinstance(package, dict):
            continue
        external_summary = package.get("externalSummary")
        if isinstance(external_summary, str):
            external_summary = external_summary.strip()
            if external_summary and "\n" not in external_summary and len(external_summary) < 30:
                warnings.append(
                    f"client package {package.get('id')} 對外功能說明可能過短；"
                    "字數只是 MOP 訊號，最終以實際交付檔的 PM 轉述 MOE 判定"
                )
    selected = state.get("selectedScenarioId")
    if selected is not None and selected not in scenario_ids:
        errors.append(f"selectedScenarioId 找不到方案：{selected}")
    decisions = state.get("decisions", [])
    if selected is not None and not any(
        isinstance(item, dict)
        and item.get("decisionId") == "select-scenario"
        and item.get("selectedScenarioId") == selected
        for item in decisions
    ):
        errors.append("selectedScenarioId 缺少 PM 明確選案的決策紀錄")

    for item in evidence:
        if not str(item.get("claim", "")).strip():
            errors.append(f"evidence {item.get('id')} 缺少 claim")
        if not str(item.get("method", "")).strip():
            errors.append(f"evidence {item.get('id')} 缺少 method")

    node_by_id = {item.get("id"): item for item in nodes if isinstance(item, dict)}
    for node in nodes:
        node_id = node.get("id")
        if node.get("status") not in NODE_STATUSES:
            errors.append(f"node {node_id} status 無效")
        if node.get("disposition") not in DISPOSITIONS:
            errors.append(f"node {node_id} disposition 無效")
        total = node.get("total", 0)
        parts = [node.get("needsChange", 0), node.get("noChange", 0), node.get("unknown", 0)]
        if not all(isinstance(value, int) and value >= 0 for value in [total, *parts]):
            errors.append(f"node {node_id} 數量必須是非負整數")
        elif total != sum(parts):
            errors.append(f"node {node_id} 數量不守恆：{total} != {sum(parts)}")
        for dependency in node.get("dependsOn", []):
            if dependency not in node_ids:
                errors.append(f"node {node_id} 依賴不存在：{dependency}")
        for evidence_id in node.get("evidenceIds", []):
            if evidence_id not in evidence_ids:
                errors.append(f"node {node_id} 證據不存在：{evidence_id}")
        if node.get("disposition") in {"zero", "external"} and not str(node.get("zeroReason", "")).strip():
            errors.append(f"node {node_id} 為 0 人天但缺少 zeroReason")
        if not str(node.get("completionEvidence", "")).strip():
            errors.append(f"node {node_id} 缺少 completionEvidence")

    priced_coverage: dict[str, int] = {node_id: 0 for node_id, node in node_by_id.items() if node.get("disposition") == "priced"}
    package_usage: dict[str, int] = {package_id: 0 for package_id in client_package_ids}
    for item in work_items:
        item_id = item.get("id")
        if item.get("kind") not in WORK_KINDS:
            errors.append(f"work item {item_id} kind 無效")
        total = item.get("total", 0)
        parts = [item.get("needsChange", 0), item.get("noChange", 0), item.get("unknown", 0)]
        if not all(isinstance(value, int) and value >= 0 for value in [total, *parts]):
            errors.append(f"work item {item_id} 數量必須是非負整數")
        elif total != sum(parts):
            errors.append(f"work item {item_id} 數量不守恆：{total} != {sum(parts)}")
        pricing_units = item.get("pricingUnits")
        if pricing_units is not None:
            if not isinstance(pricing_units, int) or pricing_units < 1:
                errors.append(f"work item {item_id} pricingUnits 必須是正整數")
            elif isinstance(item.get("needsChange"), int) and pricing_units > item.get("needsChange", 0):
                errors.append(f"work item {item_id} pricingUnits 不可大於需處理數")
        rates = item.get("unitDays") or {}
        for key in ("low", "baseline", "high"):
            if not is_half_day(rates.get(key)):
                errors.append(f"work item {item_id} unitDays.{key} 必須是 0.5 日倍數")
        if all(isinstance(rates.get(key), (int, float)) for key in ("low", "baseline", "high")):
            if not rates["low"] <= rates["baseline"] <= rates["high"]:
                errors.append(f"work item {item_id} 費率必須 low <= baseline <= high")
        effort_split = item.get("effortSplit")
        if not isinstance(effort_split, dict):
            errors.append(f"work item {item_id} 缺少開發／測試人天拆分")
        else:
            split_valid = True
            for category, label in (("development", "開發"), ("testing", "測試")):
                category_rates = effort_split.get(category)
                if not isinstance(category_rates, dict):
                    errors.append(f"work item {item_id} effortSplit 缺少{label}人天")
                    split_valid = False
                    continue
                for key in ("low", "baseline", "high"):
                    if not is_half_day(category_rates.get(key)):
                        errors.append(f"work item {item_id} {label}人天.{key} 必須是 0.5 日倍數")
                        split_valid = False
                if all(isinstance(category_rates.get(key), (int, float)) for key in ("low", "baseline", "high")):
                    if not category_rates["low"] <= category_rates["baseline"] <= category_rates["high"]:
                        errors.append(f"work item {item_id} {label}人天必須 low <= baseline <= high")
                        split_valid = False
            if split_valid:
                for key in ("low", "baseline", "high"):
                    split_total = float(effort_split["development"][key]) + float(effort_split["testing"][key])
                    if abs(split_total - float(rates.get(key, 0))) > 1e-9:
                        errors.append(f"work item {item_id} {key} 的開發＋測試人天必須等於 unitDays")
        for node_id in item.get("nodeIds", []):
            if node_id not in node_ids:
                errors.append(f"work item {item_id} 引用不存在 node：{node_id}")
            elif node_id not in priced_coverage:
                errors.append(f"work item {item_id} 承接非計價 node：{node_id}")
            else:
                priced_coverage[node_id] += 1
        for evidence_id in item.get("evidenceIds", []):
            if evidence_id not in evidence_ids:
                errors.append(f"work item {item_id} 證據不存在：{evidence_id}")
        package_id = item.get("clientPackageId")
        if package_id is None:
            pass
        elif package_id not in client_package_ids:
            errors.append(f"work item {item_id} 引用不存在 client package：{package_id}")
        else:
            package_usage[package_id] += 1

    if work_items or state.get("status") in {"estimate-ready", "complete"}:
        for node_id, count in priced_coverage.items():
            if count != 1:
                errors.append(f"計價 node {node_id} 必須恰好由一個 work item 承接，目前 {count}")
        if state.get("status") in FORMAL_STATUSES:
            for package_id, count in package_usage.items():
                if count < 1:
                    errors.append(f"client package {package_id} 沒有任何工程工作承接")
        if len(client_packages) > 9:
            warnings.append("對外成果包超過 9 包；請確認 PM 是否能在一次會議中逐包說明")

    decision = state.get("currentDecision")
    if decision:
        required = ("id", "title", "whyHuman", "facts", "choices", "next")
        missing = [key for key in required if not decision.get(key)]
        if missing:
            errors.append("currentDecision 缺少：" + ", ".join(missing))
        if "其他（自行輸入）" not in decision.get("choices", []):
            warnings.append("currentDecision 建議提供「其他（自行輸入）」")
        choice_details = decision.get("choiceDetails")
        if choice_details is not None:
            if not isinstance(choice_details, dict):
                errors.append("currentDecision.choiceDetails 必須是 object")
            else:
                for label, detail in choice_details.items():
                    if label not in decision.get("choices", []):
                        errors.append(f"choiceDetails 選項不在 choices：{label}")
                    if not isinstance(detail, dict):
                        errors.append(f"choiceDetails {label} 必須是 object")
        scenario_choices = decision.get("scenarioChoices")
        if decision.get("id") == "select-scenario":
            if not isinstance(scenario_choices, dict) or not scenario_choices:
                errors.append("select-scenario 決定必須提供 scenarioChoices")
            else:
                for label, scenario_id in scenario_choices.items():
                    if label not in decision.get("choices", []):
                        errors.append(f"scenarioChoices 選項不在 choices：{label}")
                    if scenario_id not in scenario_ids:
                        errors.append(f"scenarioChoices 找不到方案：{scenario_id}")

    if not evidence:
        warnings.append("尚無技術證據")
    if selected is None:
        warnings.append("尚未選定方案")
    if any(node.get("status") in {"fog", "working", "blocked"} for node in nodes):
        warnings.append("成功鏈仍有未收斂節點")
    coverage_status = dependency_coverage.get("status") if isinstance(dependency_coverage, dict) else None
    if state.get("mode") in {"upgrade", "mixed"} and coverage_status in {None, "pending", "blocked"}:
        warnings.append("實際依賴與方案承重元件仍未盤點完成")
    if any(item.get("status", "open") != "resolved" and item.get("blocksReadiness") is True for item in fogs):
        warnings.append("仍有阻擋正式估算的技術事實")
    if any(_dependency_is_blocking(item) for item in dependencies):
        warnings.append("目前依賴證據仍可能推翻所選方案")
    errors.extend(_formal_readiness_errors(state, scenarios, nodes, work_items, dependencies, evidence, fogs, client_packages))
    return errors, warnings


def require_revision(state: dict[str, Any], expected: int) -> None:
    actual = state.get("revision")
    if actual != expected:
        raise CaseError(f"案件 revision 已改變：預期 {expected}，目前 {actual}")


def commit(case_root: Path, candidate: dict[str, Any], expected_revision: int) -> dict[str, Any]:
    with case_lock(case_root):
        current = load(case_root)
        require_revision(current, expected_revision)
        candidate = copy.deepcopy(candidate)
        candidate["revision"] = expected_revision + 1
        candidate["updatedAt"] = now_iso()
        errors, warnings = validate_state(candidate)
        if errors:
            raise CaseError("候選狀態未通過驗證：\n- " + "\n- ".join(errors))
        atomic_json(state_path(case_root), candidate)
        return {"ok": True, "revision": candidate["revision"], "warnings": warnings}


def deep_merge(target: dict[str, Any], update: dict[str, Any]) -> None:
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge(target[key], value)
        else:
            target[key] = copy.deepcopy(value)


def collection(state: dict[str, Any], name: str) -> list[Any]:
    path = COLLECTION_PATHS[name]
    cursor: Any = state
    for key in path:
        cursor = cursor[key]
    if not isinstance(cursor, list):
        raise CaseError(f"集合 {name} 不是 array")
    return cursor


def cmd_init(args: argparse.Namespace) -> dict[str, Any]:
    root = args.case_root.resolve()
    path = state_path(root)
    if path.exists():
        raise CaseError(f"案件已存在：{path}")
    if args.mode not in MODES:
        raise CaseError(f"無效 mode：{args.mode}")
    state = default_state(args.case_id or slug(args.name), args.name, args.goal, args.mode)
    atomic_json(path, state)
    return {"ok": True, "state": str(path), "revision": 1}


def cmd_validate(args: argparse.Namespace) -> dict[str, Any]:
    state = load(args.case_root)
    errors, warnings = validate_state(state)
    return {"ok": not errors, "revision": state.get("revision"), "errors": errors, "warnings": warnings}


def cmd_merge(args: argparse.Namespace) -> dict[str, Any]:
    state = load(args.case_root)
    require_revision(state, args.expected_revision)
    update = load_input(args.input.resolve())
    forbidden = sorted(set(update) - ALLOWED_MERGE_KEYS)
    if forbidden:
        raise CaseError("merge 不允許更新：" + ", ".join(forbidden))
    candidate = copy.deepcopy(state)
    deep_merge(candidate, update)
    return commit(args.case_root, candidate, args.expected_revision)


def cmd_append(args: argparse.Namespace) -> dict[str, Any]:
    state = load(args.case_root)
    require_revision(state, args.expected_revision)
    item = load_input(args.input.resolve())
    if not str(item.get("id", "")).strip():
        raise CaseError("append item 必須有 id")
    candidate = copy.deepcopy(state)
    target = collection(candidate, args.collection)
    if any(row.get("id") == item["id"] for row in target if isinstance(row, dict)):
        raise CaseError(f"{args.collection} 已有 id：{item['id']}")
    target.append(item)
    return commit(args.case_root, candidate, args.expected_revision)


def cmd_answer(args: argparse.Namespace) -> dict[str, Any]:
    state = load(args.case_root)
    require_revision(state, args.expected_revision)
    decision = state.get("currentDecision") or {}
    if decision.get("id") != args.decision_id:
        raise CaseError(f"目前 decision 是 {decision.get('id')!r}，不是 {args.decision_id!r}")
    candidate = copy.deepcopy(state)
    decision_record = {
        "id": f"answer-{args.decision_id}-{args.expected_revision + 1}",
        "decisionId": args.decision_id,
        "answer": args.answer,
        "note": args.note or "",
        "decidedBy": args.decided_by,
        "recordedAt": now_iso(),
    }
    scenario_choices = decision.get("scenarioChoices")
    if args.decision_id == "select-scenario" and isinstance(scenario_choices, dict):
        scenario_id = scenario_choices.get(args.answer)
        if scenario_id:
            candidate["selectedScenarioId"] = scenario_id
            decision_record["selectedScenarioId"] = scenario_id
            for gate in candidate.get("gates", []):
                if not isinstance(gate, dict):
                    continue
                if gate.get("number", 0) <= 4:
                    gate["state"] = "done"
                else:
                    gate["state"] = "pending"
    candidate["decisions"].append(decision_record)
    candidate["currentDecision"] = None
    return commit(args.case_root, candidate, args.expected_revision)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    command = commands.add_parser("init")
    command.add_argument("case_root", type=Path)
    command.add_argument("--name", required=True)
    command.add_argument("--goal", required=True)
    command.add_argument("--mode", choices=sorted(MODES), default="undetermined")
    command.add_argument("--case-id")
    command.set_defaults(handler=cmd_init)
    command = commands.add_parser("validate")
    command.add_argument("case_root", type=Path)
    command.set_defaults(handler=cmd_validate)
    command = commands.add_parser("merge")
    command.add_argument("case_root", type=Path)
    command.add_argument("--input", type=Path, required=True)
    command.add_argument("--expected-revision", type=int, required=True)
    command.set_defaults(handler=cmd_merge)
    command = commands.add_parser("append")
    command.add_argument("case_root", type=Path)
    command.add_argument("--collection", choices=sorted(COLLECTION_PATHS), required=True)
    command.add_argument("--input", type=Path, required=True)
    command.add_argument("--expected-revision", type=int, required=True)
    command.set_defaults(handler=cmd_append)
    command = commands.add_parser("record-answer")
    command.add_argument("case_root", type=Path)
    command.add_argument("--decision-id", required=True)
    command.add_argument("--answer", required=True)
    command.add_argument("--note")
    command.add_argument("--decided-by", required=True)
    command.add_argument("--expected-revision", type=int, required=True)
    command.set_defaults(handler=cmd_answer)
    return root


def main(argv: list[str] | None = None) -> int:
    configure_utf8()
    args = parser().parse_args(argv)
    try:
        result = args.handler(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok", False) else 2
    except CaseError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

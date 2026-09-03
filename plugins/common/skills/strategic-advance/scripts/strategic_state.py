#!/usr/bin/env python3
"""Validate strategic state and render a self-contained strategic advance sand table."""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


OPERATIONS = {"DECISIVE", "SHAPING", "SUSTAINING"}
EFFORTS = {"MAIN", "SUPPORT"}
FRONT_STATUSES = {"ACTIVE", "PENDING", "BLOCKED", "COMPLETE", "DEFERRED"}
CONTRIBUTIONS = {"DIRECT_ADVANCE", "REMOVE_BLOCKER", "CONTROL_RISK"}
OBSERVER_STATUSES = {"HEALTHY", "DEGRADED", "FAILED", "UNKNOWN"}
INTERVENTION_STATUSES = {"NOT_REQUIRED", "AVAILABLE", "REQUESTED", "IN_PROGRESS"}
EXECUTION_MODES = {"AUTONOMOUS", "TACTICAL_TAKEOVER"}
ACTUATOR_STATUSES = {"RELIABLE", "DEGRADED", "UNRELIABLE", "UNKNOWN"}
ACTION_OUTCOMES = {"NOT_ATTEMPTED", "NO_CHANGE", "CHANGED", "OUTCOME_UNKNOWN"}
TARGET_IDENTITIES = {"EXACT_ONE", "NOT_FOUND", "AMBIGUOUS", "UNKNOWN"}
VERIFICATION_STATUSES = {"VERIFIED", "UNVERIFIED", "UNKNOWN"}
READINESS_STATUSES = {"PASS", "FAIL", "UNKNOWN"}
READINESS_RESULTS = {"TACTICAL_ACTION_READY", "NOT_READY"}
INTERVENTION_MODES = {"NONE", "TACTICAL_TAKEOVER"}
INTERVENTION_PHASES = {"NONE", "TAKEOVER_REQUESTED", "USER_ACTION_IN_PROGRESS", "BATTLE_DAMAGE_ASSESSMENT"}
CULMINATION_RISKS = {"LOW", "MEDIUM", "HIGH"}
EVIDENCE_SOURCE_TYPES = {"UI", "API", "DB", "PROCESS", "FILE", "LOG", "STATIC"}
CLAIM_STATUSES = {"PASS", "FAIL", "UNKNOWN"}
VICTORY_STATUSES = {"PASS", "FAIL", "PENDING", "UNKNOWN"}
CLARITY_STATUSES = {"CLEAR", "UNCLEAR"}
CLARITY_ROUTES = {"EXECUTION_READY", "WAYFINDER_REQUIRED", "OPERATOR_RESOLVE", "TERMINAL"}
CLARITY_UNCLEAR_CAUSES = {
    "OBJECTIVE_UNAPPROVED",
    "DECISION_FOG",
    "BLOCKER_SUSPECTED",
    "NO_ELIGIBLE_CANDIDATE",
    "AMBIGUOUS_CANDIDATE",
    "PIVOT_UNPROBED",
    "PIVOT_TRIGGERED",
}
BLOCKER_STATUSES = {"PROVEN", "SUSPECTED", "CLEARED"}
RECOVERY_STATUSES = {"READY", "NOT_READY", "NOT_REQUIRED"}
RISK_STATUSES = {"OPEN", "CONTROLLED", "ACCEPTED", "CLOSED"}
CLEANUP_SEVERITIES = {"INFO", "NON_BLOCKING", "BLOCKING"}
CLEANUP_STATUSES = {"OPEN", "CLOSED"}
TERMINAL_STATUSES = {
    "IN_PROGRESS",
    "STRATEGIC_OBJECTIVE_ACHIEVED",
    "NEW_AUTHORITY_REQUIRED",
    "LOSS_MINIMIZED",
}
ALTERNATIVE_ROUTE_STATUSES = {"OPEN", "CLOSED", "UNSAFE", "REQUIRES_AUTHORITY"}
STRATEGIC_EFFECTS = {
    "SATISFIES_VICTORY_CRITERION",
    "REMOVES_PROVEN_BLOCKER",
    "CONTROLS_UNACCEPTABLE_RISK",
    "ENABLES_NEXT_TRANSITION",
}

LABELS = {
    "DECISIVE": "決勝戰場",
    "SHAPING": "清障戰場",
    "SUSTAINING": "維持戰場",
    "MAIN": "唯一主攻",
    "SUPPORT": "支援",
    "ACTIVE": "正在推進",
    "PENDING": "等待中",
    "BLOCKED": "受阻",
    "COMPLETE": "已完成",
    "DEFERRED": "暫緩",
    "DIRECT_ADVANCE": "直接推進終局",
    "REMOVE_BLOCKER": "先移除主線障礙",
    "CONTROL_RISK": "控制失控風險",
    "HEALTHY": "正常",
    "DEGRADED": "可用，但有缺口",
    "FAILED": "不可用",
    "UNKNOWN": "尚未確認",
    "NOT_REQUIRED": "不需要介入",
    "AVAILABLE": "可隨時介入",
    "REQUESTED": "需要介入",
    "IN_PROGRESS": "介入中",
    "AUTONOMOUS": "自主執行",
    "TACTICAL_TAKEOVER": "戰術接管",
    "RELIABLE": "可靠",
    "UNRELIABLE": "已證明不可靠",
    "NOT_ATTEMPTED": "尚未執行",
    "NO_CHANGE": "已確認沒有變化",
    "CHANGED": "已確認世界狀態改變",
    "OUTCOME_UNKNOWN": "操作結果未知",
    "EXACT_ONE": "目標唯一",
    "NOT_FOUND": "找不到目標",
    "AMBIGUOUS": "目標不唯一",
    "VERIFIED": "已驗證",
    "UNVERIFIED": "未驗證",
    "PASS": "通過",
    "FAIL": "未通過",
    "TACTICAL_ACTION_READY": "可進行戰術接管",
    "NOT_READY": "尚不可執行",
    "NONE": "無",
    "TAKEOVER_REQUESTED": "已請求戰術接管",
    "USER_ACTION_IN_PROGRESS": "使用者操作中",
    "BATTLE_DAMAGE_ASSESSMENT": "正在評估戰果",
    "LOW": "低",
    "MEDIUM": "中",
    "HIGH": "高",
    "CLEAR": "戰局已清楚",
    "UNCLEAR": "戰局不明朗",
    "EXECUTION_READY": "可回到執行",
    "WAYFINDER_REQUIRED": "需要 Wayfinder",
    "OPERATOR_RESOLVE": "指揮官就地處置",
    "OBJECTIVE_UNAPPROVED": "目標未核定",
    "DECISION_FOG": "決策迷霧",
    "BLOCKER_SUSPECTED": "疑似阻礙未定",
    "NO_ELIGIBLE_CANDIDATE": "無可選主攻候選",
    "AMBIGUOUS_CANDIDATE": "主攻候選並列",
    "PIVOT_UNPROBED": "樞紐未探測",
    "PIVOT_TRIGGERED": "樞紐已觸發",
    "TERMINAL": "戰役已終止",
    "PROVEN": "已證實",
    "SUSPECTED": "待查證",
    "CLEARED": "已解除",
    "READY": "已備妥",
    "NOT_REQUIRED": "不需要",
    "OPEN": "未關閉",
    "CONTROLLED": "已控制",
    "ACCEPTED": "已接受",
    "CLOSED": "已關閉",
    "PENDING": "等待中",
    "STRATEGIC_OBJECTIVE_ACHIEVED": "戰略目標已達成",
    "NEW_AUTHORITY_REQUIRED": "需要新權限",
    "LOSS_MINIMIZED": "損失已降至可證明界線",
    "REQUIRES_AUTHORITY": "需要新權限",
    "UNSAFE": "風險不可接受",
}

LABELS_EN = {
    "DECISIVE": "Decisive front",
    "SHAPING": "Shaping front",
    "SUSTAINING": "Sustaining front",
    "MAIN": "Main effort",
    "SUPPORT": "Support",
    "ACTIVE": "Active",
    "PENDING": "Pending",
    "BLOCKED": "Blocked",
    "COMPLETE": "Complete",
    "DEFERRED": "Deferred",
    "DIRECT_ADVANCE": "Direct advance",
    "REMOVE_BLOCKER": "Remove blocker",
    "CONTROL_RISK": "Control risk",
    "HEALTHY": "Healthy",
    "DEGRADED": "Degraded",
    "FAILED": "Failed",
    "UNKNOWN": "Unknown",
    "NOT_REQUIRED": "Not required",
    "AVAILABLE": "Available",
    "REQUESTED": "Requested",
    "IN_PROGRESS": "In progress",
    "AUTONOMOUS": "Autonomous",
    "TACTICAL_TAKEOVER": "Tactical takeover",
    "RELIABLE": "Reliable",
    "UNRELIABLE": "Proven unreliable",
    "NOT_ATTEMPTED": "Not attempted",
    "NO_CHANGE": "No change verified",
    "CHANGED": "World-state change verified",
    "OUTCOME_UNKNOWN": "Outcome unknown",
    "EXACT_ONE": "Exactly one target",
    "NOT_FOUND": "Target not found",
    "AMBIGUOUS": "Ambiguous target",
    "VERIFIED": "Verified",
    "UNVERIFIED": "Unverified",
    "PASS": "Pass",
    "FAIL": "Fail",
    "TACTICAL_ACTION_READY": "Tactical action ready",
    "NOT_READY": "Not ready",
    "NONE": "None",
    "TAKEOVER_REQUESTED": "Takeover requested",
    "USER_ACTION_IN_PROGRESS": "User action in progress",
    "BATTLE_DAMAGE_ASSESSMENT": "Battle-damage assessment",
    "LOW": "Low",
    "MEDIUM": "Medium",
    "HIGH": "High",
    "CLEAR": "Situation clear",
    "UNCLEAR": "Situation unclear",
    "EXECUTION_READY": "Execution ready",
    "WAYFINDER_REQUIRED": "Wayfinder required",
    "OPERATOR_RESOLVE": "Operator resolve",
    "OBJECTIVE_UNAPPROVED": "Objective unapproved",
    "DECISION_FOG": "Decision fog",
    "BLOCKER_SUSPECTED": "Suspected blocker unresolved",
    "NO_ELIGIBLE_CANDIDATE": "No eligible candidate",
    "AMBIGUOUS_CANDIDATE": "Tied candidates",
    "PIVOT_UNPROBED": "Pivot unprobed",
    "PIVOT_TRIGGERED": "Pivot triggered",
    "TERMINAL": "Campaign terminal",
    "PROVEN": "Proven",
    "SUSPECTED": "Suspected",
    "CLEARED": "Cleared",
    "READY": "Ready",
    "OPEN": "Open",
    "CONTROLLED": "Controlled",
    "ACCEPTED": "Accepted",
    "CLOSED": "Closed",
    "STRATEGIC_OBJECTIVE_ACHIEVED": "Strategic objective achieved",
    "NEW_AUTHORITY_REQUIRED": "New authority required",
    "LOSS_MINIMIZED": "Loss minimized within proven bounds",
    "REQUIRES_AUTHORITY": "Requires authority",
    "UNSAFE": "Unsafe",
}

STATUS_GLYPHS = {
    "ACTIVE": "▶",
    "PENDING": "…",
    "BLOCKED": "✕",
    "COMPLETE": "✓",
    "DEFERRED": "∥",
}


def load_state(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"無法讀取狀態檔：{error}") from error
    if not isinstance(value, dict):
        raise ValueError("狀態根節點必須是 JSON object")
    return value


def canonical_predicate(template: str, *values: Any) -> str:
    """Build a predicate from a fixed template and canonical JSON-quoted values."""
    encoded = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for value in values
    )
    return template.format(*encoded)


def parse_datetime(value: Any, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} 必須是非空 ISO 8601 字串")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field} 不是合法 ISO 8601：{value}")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{field} 必須包含時區")
        return None
    return parsed


def require_dict(container: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = container.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} 必須是 object")
        return {}
    return value


def require_list(container: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = container.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} 必須是 array")
        return []
    return value


def require_text(container: dict[str, Any], key: str, prefix: str, errors: list[str]) -> str:
    value = container.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}.{key} 必須是非空字串")
        return ""
    return value.strip()


def require_text_list(
    container: dict[str, Any], key: str, prefix: str, errors: list[str], nonempty: bool = False
) -> list[Any]:
    values = require_list(container, key, errors)
    if nonempty and not values:
        errors.append(f"{prefix}.{key} 不得為空")
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}.{key}[{index}] 必須是非空字串")
    return values


def require_bool(container: dict[str, Any], key: str, prefix: str, errors: list[str]) -> bool | None:
    value = container.get(key)
    if not isinstance(value, bool):
        errors.append(f"{prefix}.{key} 必須是 boolean")
        return None
    return value


def require_nonnegative_number(
    container: dict[str, Any], key: str, prefix: str, errors: list[str]
) -> int | float | None:
    value = container.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        errors.append(f"{prefix}.{key} 必須是非負數")
        return None
    return value


def require_claim_refs(
    container: dict[str, Any],
    key: str,
    prefix: str,
    claims: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    nonempty: bool = False,
    authoritative_ids: set[str] | None = None,
) -> list[str]:
    values = require_text_list(container, key, prefix, errors, nonempty)
    result: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            continue
        claim_id = value.strip()
        result.append(claim_id)
        if claim_id not in claims:
            errors.append(f"{prefix}.{key}[{index}] 引用不存在的 evidence claim：{claim_id}")
        elif authoritative_ids is not None and claim_id not in authoritative_ids:
            errors.append(f"{prefix}.{key}[{index}] 不是該 predicate 的有效權威證據：{claim_id}")
    if len(result) != len(set(result)):
        errors.append(f"{prefix}.{key} 不得重複")
    return result


def claim_is_observed(claim: dict[str, Any], updated_at: datetime | None) -> bool:
    if claim.get("status") not in {"PASS", "FAIL"} or updated_at is None:
        return False
    try:
        valid_until = datetime.fromisoformat(str(claim.get("validUntil", "")).replace("Z", "+00:00"))
    except ValueError:
        return False
    return valid_until.tzinfo is not None and valid_until >= updated_at


def compute_recorded_authoritative_ids(claims: dict[str, dict[str, Any]]) -> set[str]:
    """Rank arbitration without TTL, for historical records (COMPLETE exits, verified
    advances): best authorityRank wins; among equals the latest observedAt wins.
    History answers to authority and succession, never to freshness."""
    by_predicate: dict[str, list[dict[str, Any]]] = {}
    for claim in claims.values():
        predicate = claim.get("predicate")
        rank = claim.get("authorityRank")
        if (
            isinstance(predicate, str)
            and predicate
            and claim.get("status") in {"PASS", "FAIL"}
            and isinstance(rank, int)
            and not isinstance(rank, bool)
        ):
            by_predicate.setdefault(predicate, []).append(claim)
    recorded: set[str] = set()
    for candidates in by_predicate.values():
        best_rank = min(claim["authorityRank"] for claim in candidates)
        best = [claim for claim in candidates if claim["authorityRank"] == best_rank]
        dated: list[tuple[datetime, dict[str, Any]]] = []
        for claim in best:
            try:
                moment = datetime.fromisoformat(str(claim.get("observedAt", "")).replace("Z", "+00:00"))
            except ValueError:
                continue
            if moment.tzinfo is not None:
                dated.append((moment, claim))
        if dated:
            latest = max(moment for moment, _ in dated)
            winners = [claim for moment, claim in dated if moment == latest]
        else:
            winners = best
        recorded.update(str(claim.get("id")) for claim in winners if claim.get("id"))
    return recorded


def validate_evidence_claims(
    truth: dict[str, Any], updated_at: datetime | None, errors: list[str]
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    claim_list = require_list(truth, "evidenceClaims", errors)
    claims: dict[str, dict[str, Any]] = {}
    by_predicate: dict[str, list[dict[str, Any]]] = {}
    for index, claim in enumerate(claim_list):
        prefix = f"currentTruth.evidenceClaims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        claim_id = require_text(claim, "id", prefix, errors)
        if claim_id in claims:
            errors.append(f"evidence claim id 重複：{claim_id}")
        elif claim_id:
            claims[claim_id] = claim
        if claim.get("sourceType") not in EVIDENCE_SOURCE_TYPES:
            errors.append(f"{prefix}.sourceType 不合法")
        require_text(claim, "sourceRef", prefix, errors)
        predicate = require_text(claim, "predicate", prefix, errors)
        observed_at = parse_datetime(claim.get("observedAt"), f"{prefix}.observedAt", errors)
        valid_until = parse_datetime(claim.get("validUntil"), f"{prefix}.validUntil", errors)
        if observed_at is not None and updated_at is not None and observed_at > updated_at:
            errors.append(f"{prefix}.observedAt 不得晚於 state.updatedAt")
        if observed_at is not None and valid_until is not None and valid_until < observed_at:
            errors.append(f"{prefix}.validUntil 不得早於 observedAt")
        rank = claim.get("authorityRank")
        if not isinstance(rank, int) or isinstance(rank, bool) or not 1 <= rank <= 9:
            errors.append(f"{prefix}.authorityRank 必須是 1 到 9 的整數，1 為最高")
        if claim.get("status") not in CLAIM_STATUSES:
            errors.append(f"{prefix}.status 不合法")
        # 過期降權不降法：validUntil 只透過 claim_is_observed 剝奪證據權威，
        # 過期 claim 保留原 status 作為紀錄，不構成整卷違法。
        if predicate:
            by_predicate.setdefault(predicate, []).append(claim)

    authoritative_ids: set[str] = set()
    for predicate, candidates in by_predicate.items():
        observed = [claim for claim in candidates if claim_is_observed(claim, updated_at)]
        if not observed:
            continue
        ranks = [claim["authorityRank"] for claim in observed if isinstance(claim.get("authorityRank"), int)]
        if not ranks:
            continue
        best_rank = min(ranks)
        best = [claim for claim in observed if claim.get("authorityRank") == best_rank]
        statuses = {claim.get("status") for claim in best}
        if len(statuses) > 1:
            errors.append(f"predicate 有同權級衝突且未仲裁：{predicate}")
            continue
        authoritative_ids.update(str(claim.get("id")) for claim in best if claim.get("id"))
    return claims, authoritative_ids


def validate_execution_assessment(state: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    assessment = require_dict(state, "executionAssessment", errors)
    if assessment.get("mode") not in EXECUTION_MODES:
        errors.append("executionAssessment.mode 不合法")
    if assessment.get("automationActuatorStatus") not in ACTUATOR_STATUSES:
        errors.append("executionAssessment.automationActuatorStatus 不合法")
    if assessment.get("outcomeStatus") not in ACTION_OUTCOMES:
        errors.append("executionAssessment.outcomeStatus 不合法")
    if assessment.get("targetIdentity") not in TARGET_IDENTITIES:
        errors.append("executionAssessment.targetIdentity 不合法")
    for key in ("actorIdentity", "actionContract"):
        if assessment.get(key) not in VERIFICATION_STATUSES:
            errors.append(f"executionAssessment.{key} 不合法")
    for key in ("mutationObserved", "worldStateChanged", "deadlineExceeded"):
        if not isinstance(assessment.get(key), bool):
            errors.append(f"executionAssessment.{key} 必須是 boolean")
    for key in ("attemptCount", "sameFailureFingerprintCount"):
        value = assessment.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"executionAssessment.{key} 必須是非負整數")
    deadline = assessment.get("deadlineSeconds")
    if not isinstance(deadline, (int, float)) or isinstance(deadline, bool) or deadline <= 0:
        errors.append("executionAssessment.deadlineSeconds 必須大於 0")
    fingerprint = assessment.get("failureFingerprint")
    if not isinstance(fingerprint, str):
        errors.append("executionAssessment.failureFingerprint 必須是字串")
    attempts = assessment.get("attemptCount")
    repeated = assessment.get("sameFailureFingerprintCount")
    if isinstance(attempts, int) and isinstance(repeated, int) and not isinstance(attempts, bool) and not isinstance(repeated, bool):
        if repeated > attempts:
            errors.append("executionAssessment.sameFailureFingerprintCount 不得大於 attemptCount")
    outcome = assessment.get("outcomeStatus")
    if outcome == "CHANGED" and assessment.get("worldStateChanged") is not True:
        errors.append("outcomeStatus=CHANGED 要求 worldStateChanged=true")
    if outcome == "NO_CHANGE" and assessment.get("worldStateChanged") is not False:
        errors.append("outcomeStatus=NO_CHANGE 要求 worldStateChanged=false")
    if outcome == "NOT_ATTEMPTED" and (
        assessment.get("mutationObserved") is not False or assessment.get("worldStateChanged") is not False
    ):
        errors.append("outcomeStatus=NOT_ATTEMPTED 要求沒有 mutation 或 world delta")

    if assessment.get("automationActuatorStatus") == "UNRELIABLE":
        if not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 1:
            errors.append("AUTOMATION_ACTUATOR_UNRELIABLE 要求 attemptCount 至少為 1")
        if assessment.get("targetIdentity") != "EXACT_ONE":
            errors.append("AUTOMATION_ACTUATOR_UNRELIABLE 要求 targetIdentity=EXACT_ONE")
        if assessment.get("actorIdentity") != "VERIFIED":
            errors.append("AUTOMATION_ACTUATOR_UNRELIABLE 要求 actorIdentity=VERIFIED")
        if assessment.get("actionContract") != "VERIFIED":
            errors.append("AUTOMATION_ACTUATOR_UNRELIABLE 要求 actionContract=VERIFIED")
        if assessment.get("mutationObserved") is not False or assessment.get("worldStateChanged") is not False:
            errors.append("已觀測到 mutation 或 world delta 時不得標記 AUTOMATION_ACTUATOR_UNRELIABLE")
        if assessment.get("outcomeStatus") not in {"NOT_ATTEMPTED", "NO_CHANGE"}:
            errors.append("OUTCOME_UNKNOWN 或已改變世界狀態時不得標記 AUTOMATION_ACTUATOR_UNRELIABLE")
        deadline_exceeded = assessment.get("deadlineExceeded")
        if not (isinstance(repeated, int) and not isinstance(repeated, bool) and repeated >= 2) and deadline_exceeded is not True:
            errors.append("AUTOMATION_ACTUATOR_UNRELIABLE 要求同一 failure fingerprint 至少兩次或 hard deadline 已超過")
        if not isinstance(fingerprint, str) or not fingerprint.strip():
            errors.append("AUTOMATION_ACTUATOR_UNRELIABLE 要求非空 failureFingerprint")
    return assessment


def validate_takeover_readiness(
    state: dict[str, Any],
    assessment: dict[str, Any],
    claims: dict[str, dict[str, Any]],
    authoritative_ids: set[str],
    updated_at: datetime | None,
    world_dimensions: set[str],
    errors: list[str],
) -> dict[str, Any]:
    """Validate action contracts and recompute every tactical-takeover receipt."""
    readiness = require_dict(state, "takeoverReadiness", errors)
    reject_unknown_fields(
        readiness,
        {
            "actionId",
            "actorId",
            "sessionId",
            "contextId",
            "scopeIdentity",
            "operable",
            "executable",
            "verifiable",
            "result",
        },
        "takeoverReadiness",
        errors,
    )
    action_id = require_text(readiness, "actionId", "takeoverReadiness", errors)
    actor_id = require_text(readiness, "actorId", "takeoverReadiness", errors)
    session_id = require_text(readiness, "sessionId", "takeoverReadiness", errors)
    context_id = require_text(readiness, "contextId", "takeoverReadiness", errors)
    readiness_scope_identity = require_text(readiness, "scopeIdentity", "takeoverReadiness", errors)
    operable = require_dict(readiness, "operable", errors)
    executable = require_dict(readiness, "executable", errors)
    verifiable = require_dict(readiness, "verifiable", errors)

    def combine(statuses: list[str]) -> str:
        if any(status == "FAIL" for status in statuses):
            return "FAIL"
        if statuses and all(status == "PASS" for status in statuses):
            return "PASS"
        return "UNKNOWN"

    def require_receipt(gate: dict[str, Any], prefix: str, expected: str) -> None:
        if gate.get("status") not in READINESS_STATUSES:
            errors.append(f"{prefix}.status 不合法")
        elif gate.get("status") != expected:
            errors.append(f"{prefix}.status 必須由 evidence contract 算為 {expected}")

    # OPERABLE: prose is display-only; four closed predicate contracts authorize the gate.
    reject_unknown_fields(
        operable,
        {"status", "evidence", "actorCheck", "sessionCheck", "targetCheck", "controlCheck"},
        "takeoverReadiness.operable",
        errors,
    )
    require_text_list(operable, "evidence", "takeoverReadiness.operable", errors, nonempty=True)
    actor_check = require_dict(operable, "actorCheck", errors)
    session_check = require_dict(operable, "sessionCheck", errors)
    target_check = require_dict(operable, "targetCheck", errors)
    control_check = require_dict(operable, "controlCheck", errors)
    for name, check in (("actorCheck", actor_check), ("sessionCheck", session_check)):
        reject_unknown_fields(check, {"evidenceClaimIds"}, f"takeoverReadiness.operable.{name}", errors)
    reject_unknown_fields(
        target_check,
        {"evidenceClaimIds"},
        "takeoverReadiness.operable.targetCheck",
        errors,
    )
    reject_unknown_fields(
        control_check,
        {"requiredConditions", "evidenceClaimIds"},
        "takeoverReadiness.operable.controlCheck",
        errors,
    )
    actor_status = derive_evidence_check_status(
        actor_check,
        "takeoverReadiness.operable.actorCheck",
        claims,
        authoritative_ids,
        errors,
        expected_predicate=canonical_predicate("ACTOR[{}].VERIFIED == {}", actor_id, True),
    )
    session_status = derive_evidence_check_status(
        session_check,
        "takeoverReadiness.operable.sessionCheck",
        claims,
        authoritative_ids,
        errors,
        expected_predicate=canonical_predicate(
            "SESSION[{}].CONTEXT[{}].READY == {}", session_id, context_id, True
        ),
    )
    target_evidence_status = derive_evidence_check_status(
        target_check,
        "takeoverReadiness.operable.targetCheck",
        claims,
        authoritative_ids,
        errors,
        expected_predicate=canonical_predicate(
            "TARGET[{}].CARDINALITY == {}", readiness_scope_identity, 1
        ),
    )
    target_cardinality = "EXACT_ONE" if target_evidence_status == "PASS" else "UNKNOWN"
    target_status = target_evidence_status
    control_evidence_status = derive_evidence_check_status(
        control_check,
        "takeoverReadiness.operable.controlCheck",
        claims,
        authoritative_ids,
        errors,
        expected_predicate=canonical_predicate(
            "CONTROL[{}].VISIBLE_ENABLED_UNOBSTRUCTED == {}", readiness_scope_identity, True
        ),
    )
    required_conditions = require_text_list(
        control_check,
        "requiredConditions",
        "takeoverReadiness.operable.controlCheck",
        errors,
        nonempty=True,
    )
    exact_control_conditions = (
        len(required_conditions) == 3
        and set(required_conditions) == {"VISIBLE", "ENABLED", "UNOBSTRUCTED"}
    )
    if not exact_control_conditions:
        errors.append(
            "takeoverReadiness.operable.controlCheck.requiredConditions 必須精確包含 VISIBLE、ENABLED、UNOBSTRUCTED"
        )
    control_status = control_evidence_status
    if control_evidence_status == "PASS" and not exact_control_conditions:
        control_status = "FAIL"
    expected_operable = combine([actor_status, session_status, target_status, control_status])
    require_receipt(operable, "takeoverReadiness.operable", expected_operable)

    # EXECUTABLE: authority and prerequisites are evidence-bound; the action is exactly one bounded step.
    reject_unknown_fields(
        executable,
        {
            "status",
            "objective",
            "authorizedActor",
            "authorityCheck",
            "prerequisiteChecks",
            "steps",
            "prohibitedActions",
            "sideEffects",
            "timeoutSeconds",
            "stopCondition",
            "recoveryAction",
        },
        "takeoverReadiness.executable",
        errors,
    )
    objective = require_text(executable, "objective", "takeoverReadiness.executable", errors)
    authorized_actor = require_text(executable, "authorizedActor", "takeoverReadiness.executable", errors)
    authority_check = require_dict(executable, "authorityCheck", errors)
    reject_unknown_fields(
        authority_check,
        {"evidenceClaimIds"},
        "takeoverReadiness.executable.authorityCheck",
        errors,
    )
    authority_status = derive_evidence_check_status(
        authority_check,
        "takeoverReadiness.executable.authorityCheck",
        claims,
        authoritative_ids,
        errors,
        expected_predicate=canonical_predicate(
            "ACTOR[{}].AUTHORIZED_FOR[{}] == {}", actor_id, action_id, True
        ),
    )
    prerequisite_values = require_list(executable, "prerequisiteChecks", errors)
    if not prerequisite_values:
        errors.append("takeoverReadiness.executable.prerequisiteChecks 不得為空")
    prerequisite_statuses: list[str] = []
    for index, check in enumerate(prerequisite_values):
        prefix = f"takeoverReadiness.executable.prerequisiteChecks[{index}]"
        if not isinstance(check, dict):
            errors.append(f"{prefix} 必須是 object")
            prerequisite_statuses.append("UNKNOWN")
            continue
        reject_unknown_fields(check, {"requirementId", "evidenceClaimIds"}, prefix, errors)
        requirement_id = require_text(check, "requirementId", prefix, errors)
        prerequisite_statuses.append(
            derive_evidence_check_status(
                check,
                prefix,
                claims,
                authoritative_ids,
                errors,
                expected_predicate=canonical_predicate(
                    "ACTION[{}].REQUIREMENT[{}].SATISFIED == {}",
                    action_id,
                    requirement_id,
                    True,
                ),
            )
        )
    steps = require_text_list(executable, "steps", "takeoverReadiness.executable", errors, nonempty=True)
    one_bounded_step = len(steps) == 1 and isinstance(steps[0], str) and bool(steps[0].strip())
    if not one_bounded_step:
        errors.append("takeoverReadiness.executable.steps 必須精確包含一個有限動作")
    prohibited_actions = require_text_list(
        executable, "prohibitedActions", "takeoverReadiness.executable", errors, nonempty=True
    )
    side_effects = require_text_list(
        executable, "sideEffects", "takeoverReadiness.executable", errors, nonempty=True
    )
    timeout_seconds = executable.get("timeoutSeconds")
    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
        errors.append("takeoverReadiness.executable.timeoutSeconds 必須大於 0")
    stop_condition = require_text(executable, "stopCondition", "takeoverReadiness.executable", errors)
    recovery_action = require_text(executable, "recoveryAction", "takeoverReadiness.executable", errors)
    if authorized_actor and actor_id and authorized_actor != actor_id:
        errors.append("takeoverReadiness.executable.authorizedActor 必須等於 takeoverReadiness.actorId")
    executable_structure_complete = all(
        (
            objective,
            authorized_actor,
            one_bounded_step,
            prohibited_actions and all(isinstance(value, str) and value.strip() for value in prohibited_actions),
            side_effects and all(isinstance(value, str) and value.strip() for value in side_effects),
            isinstance(timeout_seconds, (int, float)) and not isinstance(timeout_seconds, bool) and timeout_seconds > 0,
            stop_condition,
            recovery_action,
            bool(prerequisite_values),
        )
    )
    executable_evidence_status = combine([authority_status, *prerequisite_statuses])
    if not executable_structure_complete or assessment.get("outcomeStatus") == "OUTCOME_UNKNOWN":
        expected_executable = "FAIL"
    else:
        expected_executable = executable_evidence_status
    require_receipt(executable, "takeoverReadiness.executable", expected_executable)

    # VERIFIABLE: current baseline evidence and a closed before/after contract make the gate computable.
    reject_unknown_fields(
        verifiable,
        {
            "status",
            "expectedWorldDelta",
            "expectedWorldDeltaContracts",
            "baselineChecks",
            "evidenceSources",
            "successPredicates",
            "failurePredicates",
            "unknownOutcomeRule",
            "deadlineAt",
        },
        "takeoverReadiness.verifiable",
        errors,
    )
    expected_delta = require_text_list(
        verifiable, "expectedWorldDelta", "takeoverReadiness.verifiable", errors, nonempty=True
    )
    evidence_sources = require_text_list(
        verifiable, "evidenceSources", "takeoverReadiness.verifiable", errors, nonempty=True
    )
    success_predicates = require_text_list(
        verifiable, "successPredicates", "takeoverReadiness.verifiable", errors, nonempty=True
    )
    failure_predicates = require_text_list(
        verifiable, "failurePredicates", "takeoverReadiness.verifiable", errors, nonempty=True
    )
    if set(success_predicates) & set(failure_predicates):
        errors.append("takeoverReadiness.verifiable.successPredicates 與 failurePredicates 不得重疊")
    unknown_rule = verifiable.get("unknownOutcomeRule")
    if unknown_rule != "NO_DECISIVE_EVIDENCE_BY_DEADLINE":
        errors.append(
            "takeoverReadiness.verifiable.unknownOutcomeRule 必須為 NO_DECISIVE_EVIDENCE_BY_DEADLINE"
        )

    baseline_values = require_list(verifiable, "baselineChecks", errors)
    if not baseline_values:
        errors.append("takeoverReadiness.verifiable.baselineChecks 不得為空")
    baseline_ids: set[str] = set()
    baselines_by_id: dict[str, dict[str, Any]] = {}
    baseline_statuses: list[str] = []
    for index, check in enumerate(baseline_values):
        prefix = f"takeoverReadiness.verifiable.baselineChecks[{index}]"
        if not isinstance(check, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        reject_unknown_fields(check, {"id", "evidenceClaimIds"}, prefix, errors)
        check_id = require_text(check, "id", prefix, errors)
        if check_id in baseline_ids:
            errors.append(f"takeoverReadiness.verifiable baseline check id 重複：{check_id}")
        elif check_id:
            baseline_ids.add(check_id)
            baselines_by_id[check_id] = check
        require_claim_refs(check, "evidenceClaimIds", prefix, claims, errors, nonempty=True)

    contract_values = require_list(verifiable, "expectedWorldDeltaContracts", errors)
    if not contract_values:
        errors.append("takeoverReadiness.verifiable.expectedWorldDeltaContracts 不得為空")
    contract_keys: set[tuple[str, str]] = set()
    contract_scopes: set[str] = set()
    used_baseline_ids: set[str] = set()
    contracts_complete = bool(contract_values)
    for index, contract in enumerate(contract_values):
        prefix = f"takeoverReadiness.verifiable.expectedWorldDeltaContracts[{index}]"
        if not isinstance(contract, dict):
            errors.append(f"{prefix} 必須是 object")
            contracts_complete = False
            continue
        reject_unknown_fields(
            contract,
            {"scopeIdentity", "dimension", "beforeValue", "afterValue", "baselineCheckId"},
            prefix,
            errors,
        )
        scope_identity = require_text(contract, "scopeIdentity", prefix, errors)
        dimension = require_text(contract, "dimension", prefix, errors)
        baseline_check_id = require_text(contract, "baselineCheckId", prefix, errors)
        if dimension not in world_dimensions:
            errors.append(f"{prefix}.dimension 必須是 strategicObjective.worldDimensions 成員")
            contracts_complete = False
        if baseline_check_id not in baseline_ids:
            errors.append(f"{prefix}.baselineCheckId 必須引用存在的 baseline check")
            contracts_complete = False
        elif baseline_check_id in used_baseline_ids:
            errors.append(
                f"{prefix}.baselineCheckId 不得與其他 world-delta contract 共用；每個 contract 必須有一個專屬 baseline"
            )
            contracts_complete = False
        else:
            used_baseline_ids.add(baseline_check_id)
        if scope_identity and scope_identity != readiness_scope_identity:
            errors.append(f"{prefix}.scopeIdentity 必須等於 takeoverReadiness.scopeIdentity")
            contracts_complete = False
        if "beforeValue" not in contract or "afterValue" not in contract:
            errors.append(f"{prefix} 必須同時提供 beforeValue 與 afterValue")
            contracts_complete = False
        else:
            before_value = contract.get("beforeValue")
            after_value = contract.get("afterValue")
            if isinstance(before_value, (dict, list)) or isinstance(after_value, (dict, list)):
                errors.append(f"{prefix}.beforeValue 與 afterValue 必須是 scalar")
                contracts_complete = False
            elif before_value == after_value:
                errors.append(f"{prefix}.beforeValue 與 afterValue 必須不同")
                contracts_complete = False
            baseline_check = baselines_by_id.get(baseline_check_id)
            if baseline_check is not None:
                baseline_statuses.append(
                    derive_evidence_check_status(
                        baseline_check,
                        f"takeoverReadiness.verifiable.baselineChecks[{baseline_check_id}]",
                        claims,
                        authoritative_ids,
                        errors,
                        expected_predicate=canonical_predicate(
                            "WORLD[{}].DIMENSION[{}] == {}",
                            scope_identity,
                            dimension,
                            before_value,
                        ),
                    )
                )
        key = (scope_identity, dimension)
        if key in contract_keys:
            errors.append(f"{prefix} 重複定義相同 scopeIdentity 與 dimension")
            contracts_complete = False
        contract_keys.add(key)
        if scope_identity:
            contract_scopes.add(scope_identity)
    if len(contract_scopes) != 1:
        errors.append("takeoverReadiness.verifiable.expectedWorldDeltaContracts 必須精確描述一個 scopeIdentity")
        contracts_complete = False
    if used_baseline_ids != baseline_ids:
        errors.append(
            "takeoverReadiness.verifiable 每個 expectedWorldDeltaContract 必須與每個 baselineCheck 建立精確 1:1 對應"
        )
        contracts_complete = False

    deadline_at = parse_datetime(
        verifiable.get("deadlineAt"), "takeoverReadiness.verifiable.deadlineAt", errors
    )
    deadline_valid = deadline_at is not None and updated_at is not None and deadline_at > updated_at
    if deadline_at is not None and updated_at is not None and deadline_at <= updated_at:
        errors.append("takeoverReadiness.verifiable.deadlineAt 必須晚於 state.updatedAt")
    verifiable_structure_complete = all(
        (
            expected_delta,
            evidence_sources,
            success_predicates,
            failure_predicates,
            set(success_predicates).isdisjoint(failure_predicates),
            unknown_rule == "NO_DECISIVE_EVIDENCE_BY_DEADLINE",
            bool(baseline_values),
            contracts_complete,
            deadline_valid,
        )
    )
    baseline_status = combine(baseline_statuses)
    expected_verifiable = baseline_status if verifiable_structure_complete else "FAIL"
    require_receipt(verifiable, "takeoverReadiness.verifiable", expected_verifiable)

    expected_actor_identity = {
        "PASS": "VERIFIED",
        "FAIL": "UNVERIFIED",
        "UNKNOWN": "UNKNOWN",
    }[combine([actor_status, session_status])]
    if assessment.get("actorIdentity") != expected_actor_identity:
        errors.append(f"executionAssessment.actorIdentity 必須由 actor/session checks 算為 {expected_actor_identity}")
    expected_target_identity = (
        target_cardinality if target_evidence_status == "PASS" and target_cardinality in TARGET_IDENTITIES else "UNKNOWN"
    )
    if assessment.get("targetIdentity") != expected_target_identity:
        errors.append(f"executionAssessment.targetIdentity 必須由 target check 算為 {expected_target_identity}")
    expected_action_contract = {
        "PASS": "VERIFIED",
        "FAIL": "UNVERIFIED",
        "UNKNOWN": "UNKNOWN",
    }[expected_executable]
    if assessment.get("actionContract") != expected_action_contract:
        errors.append(
            f"executionAssessment.actionContract 必須由 executable contract 算為 {expected_action_contract}"
        )

    expected_result = "NOT_READY"
    if (
        expected_operable == "PASS"
        and expected_executable == "PASS"
        and expected_verifiable == "PASS"
        and assessment.get("automationActuatorStatus") == "UNRELIABLE"
        and assessment.get("outcomeStatus") in {"NOT_ATTEMPTED", "NO_CHANGE"}
        and assessment.get("mutationObserved") is False
        and assessment.get("worldStateChanged") is False
        and expected_target_identity == "EXACT_ONE"
        and expected_actor_identity == "VERIFIED"
        and expected_action_contract == "VERIFIED"
        and one_bounded_step
    ):
        expected_result = "TACTICAL_ACTION_READY"
    if readiness.get("result") not in READINESS_RESULTS:
        errors.append("takeoverReadiness.result 不合法")
    elif readiness.get("result") != expected_result:
        errors.append(f"takeoverReadiness.result 必須由完整接管條件算為 {expected_result}")
    return readiness


def derive_evidence_check_status(
    check: dict[str, Any],
    prefix: str,
    claims: dict[str, dict[str, Any]],
    authoritative_ids: set[str],
    errors: list[str],
    *,
    required_text_fields: tuple[str, ...] = (),
    predicate_key: str = "predicate",
    evidence_key: str = "evidenceClaimIds",
    expected_predicate: str | None = None,
) -> str:
    """Derive PASS, FAIL, or UNKNOWN from an exact predicate/evidence contract."""
    for key in required_text_fields:
        require_text(check, key, prefix, errors)
    predicate = (
        require_text(check, predicate_key, prefix, errors)
        if expected_predicate is None
        else expected_predicate
    )
    refs = require_claim_refs(check, evidence_key, prefix, claims, errors, nonempty=True)
    predicates_match = bool(predicate)
    observed_statuses: list[str] = []
    all_authoritative = bool(refs)
    for claim_id in refs:
        claim = claims.get(claim_id)
        if claim is None:
            predicates_match = False
            all_authoritative = False
            continue
        if claim.get("predicate") != predicate:
            expected_source = (
                f"{prefix}.{predicate_key}"
                if expected_predicate is None
                else f"canonical predicate：{predicate}"
            )
            errors.append(f"{prefix}.{evidence_key} 的 claim predicate 必須精確等於 {expected_source}")
            predicates_match = False
        if claim_id not in authoritative_ids:
            all_authoritative = False
            observed_statuses.append("UNKNOWN")
        else:
            observed_statuses.append(str(claim.get("status")))
    if not refs or not predicates_match:
        return "UNKNOWN"
    if "FAIL" in observed_statuses:
        return "FAIL"
    if all_authoritative and observed_statuses and all(status == "PASS" for status in observed_statuses):
        return "PASS"
    return "UNKNOWN"


def validate_loss_evidence_check(
    check: dict[str, Any],
    prefix: str,
    claims: dict[str, dict[str, Any]],
    authoritative_ids: set[str],
    errors: list[str],
    *,
    required_text_fields: tuple[str, ...] = (),
) -> bool:
    """Validate one predicate/claim contract and derive whether current evidence proves it."""
    return derive_evidence_check_status(
        check,
        prefix,
        claims,
        authoritative_ids,
        errors,
        required_text_fields=required_text_fields,
    ) == "PASS"


def priority_rank(front_id: str, priority_order: list[str]) -> int:
    """User-set priority: exact id or prefix match; unlisted fronts rank after all listed."""
    for index, entry in enumerate(priority_order):
        if front_id == entry or front_id.startswith(entry):
            return index
    return len(priority_order)


def select_main_candidate_ids(
    eligible_candidates: list[dict[str, Any]], priority_order: list[str]
) -> list[str]:
    """Minimum (user priority rank, fixed-formula score); ties stay ambiguous."""
    if not eligible_candidates:
        return []

    def sort_key(candidate: dict[str, Any]) -> tuple[int, float]:
        return (
            priority_rank(str(candidate.get("frontId")), priority_order),
            candidate.get("totalScore", float("inf")),
        )

    best = min(sort_key(candidate) for candidate in eligible_candidates)
    return sorted(
        str(candidate.get("frontId"))
        for candidate in eligible_candidates
        if sort_key(candidate) == best
    )


def reject_unknown_fields(
    container: dict[str, Any], allowed: set[str], prefix: str, errors: list[str]
) -> None:
    for key in sorted(set(container) - allowed):
        errors.append(f"{prefix}.{key} 不在 schema 中；不得加入手填結果或未定義欄位")


def validate_loss_minimization_assessment(
    state: dict[str, Any],
    unacceptable_outcomes: list[str],
    claims: dict[str, dict[str, Any]],
    authoritative_ids: set[str],
    errors: list[str],
) -> dict[str, bool]:
    assessment = require_dict(state, "lossMinimizationAssessment", errors)
    reject_unknown_fields(
        assessment,
        {
            "victoryUnattainable",
            "unacceptableOutcomeChecks",
            "residualLossMeasurements",
            "preservedGains",
        },
        "lossMinimizationAssessment",
        errors,
    )

    victory_unattainable = require_dict(assessment, "victoryUnattainable", errors)
    reject_unknown_fields(
        victory_unattainable,
        {"predicate", "evidenceClaimIds"},
        "lossMinimizationAssessment.victoryUnattainable",
        errors,
    )
    victory_unattainable_proven = validate_loss_evidence_check(
        victory_unattainable,
        "lossMinimizationAssessment.victoryUnattainable",
        claims,
        authoritative_ids,
        errors,
    )

    if len(unacceptable_outcomes) != len(set(unacceptable_outcomes)):
        errors.append("strategicObjective.unacceptableOutcomes 不得重複；逐項 loss check 必須可唯一對應")
    expected_outcomes = set(unacceptable_outcomes)
    outcome_checks = require_list(assessment, "unacceptableOutcomeChecks", errors)
    seen_outcomes: set[str] = set()
    outcome_proofs: list[bool] = []
    for index, check in enumerate(outcome_checks):
        prefix = f"lossMinimizationAssessment.unacceptableOutcomeChecks[{index}]"
        if not isinstance(check, dict):
            errors.append(f"{prefix} 必須是 object")
            outcome_proofs.append(False)
            continue
        reject_unknown_fields(check, {"outcome", "predicate", "evidenceClaimIds"}, prefix, errors)
        outcome = require_text(check, "outcome", prefix, errors)
        if outcome in seen_outcomes:
            errors.append(f"{prefix}.outcome 重複：{outcome}")
        elif outcome:
            seen_outcomes.add(outcome)
        if outcome and outcome not in expected_outcomes:
            errors.append(f"{prefix}.outcome 必須逐字對應 strategicObjective.unacceptableOutcomes")
        outcome_proofs.append(
            validate_loss_evidence_check(check, prefix, claims, authoritative_ids, errors)
        )
    missing_outcomes = expected_outcomes - seen_outcomes
    if missing_outcomes:
        errors.append(
            "lossMinimizationAssessment.unacceptableOutcomeChecks 未覆蓋："
            + ", ".join(sorted(missing_outcomes))
        )
    unacceptable_outcomes_proven = (
        seen_outcomes == expected_outcomes
        and len(outcome_checks) == len(expected_outcomes)
        and all(outcome_proofs)
    )

    measurements = require_list(assessment, "residualLossMeasurements", errors)
    if not measurements:
        errors.append("lossMinimizationAssessment.residualLossMeasurements 不得為空")
    measurement_ids: set[str] = set()
    measurement_proofs: list[bool] = []
    for index, measurement in enumerate(measurements):
        prefix = f"lossMinimizationAssessment.residualLossMeasurements[{index}]"
        if not isinstance(measurement, dict):
            errors.append(f"{prefix} 必須是 object")
            measurement_proofs.append(False)
            continue
        reject_unknown_fields(
            measurement,
            {"id", "metric", "displayText", "predicate", "evidenceClaimIds"},
            prefix,
            errors,
        )
        measurement_id = require_text(measurement, "id", prefix, errors)
        if measurement_id in measurement_ids:
            errors.append(f"residual loss measurement id 重複：{measurement_id}")
        elif measurement_id:
            measurement_ids.add(measurement_id)
        measurement_proofs.append(
            validate_loss_evidence_check(
                measurement,
                prefix,
                claims,
                authoritative_ids,
                errors,
                required_text_fields=("metric", "displayText"),
            )
        )

    preserved_gains = require_list(assessment, "preservedGains", errors)
    preserved_ids: set[str] = set()
    preserved_proofs: list[bool] = []
    for index, gain in enumerate(preserved_gains):
        prefix = f"lossMinimizationAssessment.preservedGains[{index}]"
        if not isinstance(gain, dict):
            errors.append(f"{prefix} 必須是 object")
            preserved_proofs.append(False)
            continue
        reject_unknown_fields(
            gain,
            {"id", "displayText", "predicate", "evidenceClaimIds"},
            prefix,
            errors,
        )
        gain_id = require_text(gain, "id", prefix, errors)
        if gain_id in preserved_ids:
            errors.append(f"preserved gain id 重複：{gain_id}")
        elif gain_id:
            preserved_ids.add(gain_id)
        preserved_proofs.append(
            validate_loss_evidence_check(
                gain,
                prefix,
                claims,
                authoritative_ids,
                errors,
                required_text_fields=("displayText",),
            )
        )

    return {
        "victoryUnattainableProven": victory_unattainable_proven,
        "unacceptableOutcomesProven": unacceptable_outcomes_proven,
        "residualLossBounded": bool(measurement_proofs) and all(measurement_proofs),
        "preservedGainsProven": all(preserved_proofs),
    }


def validate_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("schemaVersion") != 6:
        errors.append("schemaVersion 必須為 6")
    require_text(state, "missionId", "state", errors)
    updated_at = parse_datetime(state.get("updatedAt"), "updatedAt", errors)

    objective = require_dict(state, "strategicObjective", errors)
    require_text(objective, "purpose", "strategicObjective", errors)
    revision = objective.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision <= 0:
        errors.append("strategicObjective.revision 必須是正整數")
    approved_at = parse_datetime(objective.get("approvedAt"), "strategicObjective.approvedAt", errors)
    if approved_at is not None and updated_at is not None and approved_at > updated_at:
        errors.append("strategicObjective.approvedAt 不得晚於 state.updatedAt")
    for key in ("desiredEndState", "victoryEvidence", "constraints", "unacceptableOutcomes"):
        require_text_list(objective, key, "strategicObjective", errors, key in {"desiredEndState", "victoryEvidence"})
    unacceptable_outcomes = [
        value.strip()
        for value in objective.get("unacceptableOutcomes", [])
        if isinstance(value, str) and value.strip()
    ]
    world_dimensions = set(
        require_text_list(objective, "worldDimensions", "strategicObjective", errors, nonempty=True)
    )
    protected_asset_values = require_list(objective, "protectedAssets", errors)
    protected_asset_ids: set[str] = set()
    if not protected_asset_values:
        errors.append("strategicObjective.protectedAssets 不得為空")
    for index, asset in enumerate(protected_asset_values):
        prefix = f"strategicObjective.protectedAssets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        reject_unknown_fields(asset, {"id", "displayText"}, prefix, errors)
        asset_id = require_text(asset, "id", prefix, errors)
        require_text(asset, "displayText", prefix, errors)
        if asset_id in protected_asset_ids:
            errors.append(f"protected asset id 重複：{asset_id}")
        elif asset_id:
            protected_asset_ids.add(asset_id)

    priority_order_raw = objective.get("priorityOrder", [])
    priority_order: list[str] = []
    if "priorityOrder" in objective:
        if not isinstance(priority_order_raw, list) or any(
            not isinstance(item, str) or not item.strip() for item in priority_order_raw
        ):
            errors.append("strategicObjective.priorityOrder 必須是非空字串列表（frontId 或前綴）")
        elif len(set(priority_order_raw)) != len(priority_order_raw):
            errors.append("strategicObjective.priorityOrder 不得重複")
        else:
            priority_order = list(priority_order_raw)

    briefing = require_dict(state, "plainBriefing", errors)
    for key in ("context", "currentSituation", "reasoning", "nextMove", "userRole"):
        require_text(briefing, key, "plainBriefing", errors)

    truth = require_dict(state, "currentTruth", errors)
    require_dict(truth, "worldState", errors)
    if "confidence" in truth:
        errors.append("currentTruth.confidence 已停用；決策必須引用有時效與權威級的 evidence claims")
    claims, authoritative_ids = validate_evidence_claims(truth, updated_at, errors)
    recorded_ids = compute_recorded_authoritative_ids(claims)

    victory_criteria = require_list(objective, "victoryCriteria", errors)
    victory_ids: set[str] = set()
    victory_by_id: dict[str, dict[str, Any]] = {}
    for index, criterion in enumerate(victory_criteria):
        prefix = f"strategicObjective.victoryCriteria[{index}]"
        if not isinstance(criterion, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        criterion_id = require_text(criterion, "id", prefix, errors)
        if criterion_id in victory_ids:
            errors.append(f"victory criterion id 重複：{criterion_id}")
        elif criterion_id:
            victory_ids.add(criterion_id)
            victory_by_id[criterion_id] = criterion
        require_text(criterion, "displayText", prefix, errors)
        evidence_status = derive_evidence_check_status(
            criterion, prefix, claims, authoritative_ids, errors
        )
        expected_status = evidence_status if evidence_status in {"PASS", "FAIL"} else "UNKNOWN"
        status = criterion.get("status")
        if status not in VICTORY_STATUSES:
            errors.append(f"{prefix}.status 不合法")
        elif status != expected_status:
            errors.append(f"{prefix}.status 必須由 exact predicate evidence 算為 {expected_status}")
    if not victory_criteria:
        errors.append("strategicObjective.victoryCriteria 不得為空")

    observers = require_list(truth, "observerHealth", errors)
    for index, observer in enumerate(observers):
        prefix = f"currentTruth.observerHealth[{index}]"
        if not isinstance(observer, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        require_text(observer, "name", prefix, errors)
        require_text(observer, "evidence", prefix, errors)
        required = require_claim_refs(observer, "requiredClaimIds", prefix, claims, errors, nonempty=True)
        critical = require_claim_refs(observer, "decisionCriticalClaimIds", prefix, claims, errors)
        if not set(critical).issubset(set(required)):
            errors.append(f"{prefix}.decisionCriticalClaimIds 必須是 requiredClaimIds 子集合")
        deadline_exceeded = require_bool(observer, "deadlineExceeded", prefix, errors)
        observed = {claim_id for claim_id in required if claim_id in claims and claim_is_observed(claims[claim_id], updated_at)}
        if not required:
            expected_status = "UNKNOWN"
        elif len(observed) == len(required):
            expected_status = "HEALTHY"
        elif set(critical).issubset(observed):
            expected_status = "DEGRADED"
        elif deadline_exceeded is True:
            expected_status = "FAILED"
        else:
            expected_status = "UNKNOWN"
        if observer.get("status") not in OBSERVER_STATUSES:
            errors.append(f"{prefix}.status 不合法")
        elif observer.get("status") != expected_status:
            errors.append(f"{prefix}.status 必須由 claim coverage 算為 {expected_status}")

    cleanup_debt = require_list(truth, "cleanupDebt", errors)
    cleanup_ids: set[str] = set()
    for index, debt in enumerate(cleanup_debt):
        prefix = f"currentTruth.cleanupDebt[{index}]"
        if not isinstance(debt, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        debt_id = require_text(debt, "id", prefix, errors)
        if debt_id in cleanup_ids:
            errors.append(f"cleanup debt id 重複：{debt_id}")
        cleanup_ids.add(debt_id)
        for key in ("residue", "owner", "cleanupAction", "verificationPredicate"):
            require_text(debt, key, prefix, errors)
        if debt.get("severity") not in CLEANUP_SEVERITIES:
            errors.append(f"{prefix}.severity 不合法")
        blocks_victory = require_bool(debt, "blocksVictory", prefix, errors)
        cleanup_evidence_status = derive_evidence_check_status(
            debt,
            prefix,
            claims,
            authoritative_ids,
            errors,
            predicate_key="verificationPredicate",
        )
        expected_cleanup_status = "CLOSED" if cleanup_evidence_status == "PASS" else "OPEN"
        if debt.get("status") not in CLEANUP_STATUSES:
            errors.append(f"{prefix}.status 不合法")
        elif debt.get("status") != expected_cleanup_status:
            errors.append(
                f"{prefix}.status 必須由 exact verification evidence 算為 {expected_cleanup_status}"
            )
        if blocks_victory is True and debt.get("severity") != "BLOCKING":
            errors.append(f"{prefix}.blocksVictory=true 要求 severity=BLOCKING")
        if debt.get("severity") == "BLOCKING" and blocks_victory is not True:
            errors.append(f"{prefix}.severity=BLOCKING 要求 blocksVictory=true")

    risk_list = require_list(state, "riskRegister", errors)
    risks: dict[str, dict[str, Any]] = {}
    unacceptable_risk_ids: set[str] = set()
    for index, risk in enumerate(risk_list):
        prefix = f"riskRegister[{index}]"
        if not isinstance(risk, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        reject_unknown_fields(
            risk,
            {
                "id",
                "affectedFrontId",
                "protectedAssetId",
                "threat",
                "status",
                "probability",
                "impact",
                "score",
                "unacceptableThreshold",
                "guard",
                "stopCondition",
                "recoveryAction",
                "statusChecks",
            },
            prefix,
            errors,
        )
        risk_id = require_text(risk, "id", prefix, errors)
        if risk_id in risks:
            errors.append(f"risk id 重複：{risk_id}")
        elif risk_id:
            risks[risk_id] = risk
        require_text(risk, "affectedFrontId", prefix, errors)
        protected_asset_id = require_text(risk, "protectedAssetId", prefix, errors)
        require_text(risk, "threat", prefix, errors)
        if protected_asset_id and protected_asset_id not in protected_asset_ids:
            errors.append(
                f"{prefix}.protectedAssetId 必須引用 strategicObjective.protectedAssets：{protected_asset_id}"
            )
        for key in ("guard", "stopCondition", "recoveryAction"):
            require_text(risk, key, prefix, errors)
        probability = risk.get("probability")
        impact = risk.get("impact")
        threshold = risk.get("unacceptableThreshold")
        if not isinstance(probability, int) or isinstance(probability, bool) or not 1 <= probability <= 5:
            errors.append(f"{prefix}.probability 必須是 1 到 5 的整數")
        if not isinstance(impact, int) or isinstance(impact, bool) or not 1 <= impact <= 5:
            errors.append(f"{prefix}.impact 必須是 1 到 5 的整數")
        if not isinstance(threshold, int) or isinstance(threshold, bool) or not 1 <= threshold <= 25:
            errors.append(f"{prefix}.unacceptableThreshold 必須是 1 到 25 的整數")
        expected_score = probability * impact if isinstance(probability, int) and isinstance(impact, int) else None
        if risk.get("score") != expected_score:
            errors.append(f"{prefix}.score 必須等於 probability × impact")
        status_checks = require_dict(risk, "statusChecks", errors)
        expected_risk_checks = {"CONTROLLED", "ACCEPTED", "CLOSED"}
        if set(status_checks) != expected_risk_checks:
            errors.append(f"{prefix}.statusChecks 必須精確包含 CONTROLLED、ACCEPTED、CLOSED")
        proven_risk_statuses: list[str] = []
        for risk_status in sorted(expected_risk_checks):
            check = status_checks.get(risk_status)
            check_prefix = f"{prefix}.statusChecks.{risk_status}"
            if not isinstance(check, dict):
                errors.append(f"{check_prefix} 必須是 object")
                continue
            reject_unknown_fields(check, {"evidenceClaimIds"}, check_prefix, errors)
            expected_predicate = canonical_predicate(
                "RISK[{}]@FRONT[{}].STATUS == {}",
                risk_id,
                risk.get("affectedFrontId"),
                risk_status,
            )
            if derive_evidence_check_status(
                check,
                check_prefix,
                claims,
                authoritative_ids,
                errors,
                expected_predicate=expected_predicate,
            ) == "PASS":
                proven_risk_statuses.append(risk_status)
        if len(proven_risk_statuses) > 1:
            errors.append(f"{prefix}.statusChecks 不得同時證明多個 risk status：{proven_risk_statuses}")
        expected_risk_status = proven_risk_statuses[0] if len(proven_risk_statuses) == 1 else "OPEN"
        if risk.get("status") not in RISK_STATUSES:
            errors.append(f"{prefix}.status 不合法")
        elif risk.get("status") != expected_risk_status:
            errors.append(f"{prefix}.status 必須由 statusChecks 算為 {expected_risk_status}")
        if expected_risk_status == "OPEN" and isinstance(expected_score, int) and isinstance(threshold, int) and expected_score >= threshold:
            unacceptable_risk_ids.add(risk_id)

    blockers_list = require_list(state, "blockers", errors)
    blockers: dict[str, dict[str, Any]] = {}
    proven_blocked_front_ids: set[str] = set()
    for index, blocker in enumerate(blockers_list):
        prefix = f"blockers[{index}]"
        if not isinstance(blocker, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        blocker_id = require_text(blocker, "id", prefix, errors)
        if blocker_id in blockers:
            errors.append(f"blocker id 重複：{blocker_id}")
        elif blocker_id:
            blockers[blocker_id] = blocker
        blocked_front_id = require_text(blocker, "blockedFrontId", prefix, errors)
        for key in ("requiredPredicate", "observedValue", "remediationAction", "clearPredicate"):
            require_text(blocker, key, prefix, errors)
        required_status = derive_evidence_check_status(
            blocker,
            prefix,
            claims,
            authoritative_ids,
            errors,
            predicate_key="requiredPredicate",
            evidence_key="requiredEvidenceClaimIds",
        )
        clear_status = derive_evidence_check_status(
            blocker,
            prefix,
            claims,
            authoritative_ids,
            errors,
            predicate_key="clearPredicate",
            evidence_key="clearEvidenceClaimIds",
        )
        expected_blocker_status = (
            "CLEARED" if clear_status == "PASS" else "PROVEN" if required_status == "PASS" else "SUSPECTED"
        )
        status = blocker.get("status")
        if status not in BLOCKER_STATUSES:
            errors.append(f"{prefix}.status 不合法")
        elif status != expected_blocker_status:
            errors.append(f"{prefix}.status 必須由 required/clear evidence 算為 {expected_blocker_status}")
        if expected_blocker_status == "PROVEN":
            proven_blocked_front_ids.add(blocked_front_id)

    battlefields = require_list(state, "battlefields", errors)
    active_main: list[dict[str, Any]] = []
    battlefield_ids: set[str] = set()
    battlefields_by_id: dict[str, dict[str, Any]] = {}
    for index, battlefield in enumerate(battlefields):
        prefix = f"battlefields[{index}]"
        if not isinstance(battlefield, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        battlefield_id = require_text(battlefield, "id", prefix, errors)
        if battlefield_id in battlefield_ids:
            errors.append(f"battlefield id 重複：{battlefield_id}")
        elif battlefield_id:
            battlefield_ids.add(battlefield_id)
            battlefields_by_id[battlefield_id] = battlefield
        if battlefield.get("operationType") not in OPERATIONS:
            errors.append(f"{prefix}.operationType 不合法")
        if battlefield.get("effort") not in EFFORTS:
            errors.append(f"{prefix}.effort 不合法")
        status = battlefield.get("status")
        if status not in FRONT_STATUSES:
            errors.append(f"{prefix}.status 不合法")
        for retired_key in (
            "recoveryPath",
            "blocksActiveFront",
            "authoritativeEvidence",
            "entryPredicate",
            "exitPredicate",
        ):
            if retired_key in battlefield:
                errors.append(f"{prefix}.{retired_key} 已停用；改用可驗證的 claim／blocker／recovery 契約")
        for key in ("objective", "entryState", "terminalState", "owner"):
            require_text(battlefield, key, prefix, errors)
        mutation_scope = require_text_list(battlefield, "mutationScope", prefix, errors)
        require_claim_refs(battlefield, "evidenceClaimIds", prefix, claims, errors, nonempty=True)
        entry_claim_id = require_text(battlefield, "entryClaimId", prefix, errors)
        exit_claim_id = require_text(battlefield, "exitClaimId", prefix, errors)
        entry_predicate = canonical_predicate(
            "BATTLEFIELD[{}].ENTRY[{}] == {}",
            battlefield_id,
            battlefield.get("entryState"),
            True,
        )
        exit_predicate = canonical_predicate(
            "BATTLEFIELD[{}].EXIT[{}] == {}",
            battlefield_id,
            battlefield.get("terminalState"),
            True,
        )
        entry_claim = claims.get(entry_claim_id, {})
        exit_claim = claims.get(exit_claim_id, {})
        if entry_claim_id not in claims:
            errors.append(f"{prefix}.entryClaimId 引用不存在的 claim")
        if exit_claim_id not in claims:
            errors.append(f"{prefix}.exitClaimId 引用不存在的 claim")
        if entry_claim and entry_claim.get("predicate") != entry_predicate:
            errors.append(f"{prefix}.entryClaimId 的 claim predicate 必須精確等於 canonical entry predicate：{entry_predicate}")
        if exit_claim and exit_claim.get("predicate") != exit_predicate:
            errors.append(f"{prefix}.exitClaimId 的 claim predicate 必須精確等於 canonical exit predicate：{exit_predicate}")
        allowed = require_text_list(battlefield, "allowedNextStatuses", prefix, errors, nonempty=True)
        if any(value not in FRONT_STATUSES for value in allowed):
            errors.append(f"{prefix}.allowedNextStatuses 含非法狀態")
        if not isinstance(battlefield.get("deferReason", ""), str):
            errors.append(f"{prefix}.deferReason 必須是字串")
        if "carrierRoots" in battlefield:
            carrier_roots = battlefield.get("carrierRoots")
            if not isinstance(carrier_roots, list) or any(
                not isinstance(item, str) or not item.strip() or not item.startswith("/")
                for item in carrier_roots
            ):
                errors.append(f"{prefix}.carrierRoots 必須是絕對路徑字串列表")
        budget = battlefield.get("timeBudgetMinutes")
        if not isinstance(budget, (int, float)) or isinstance(budget, bool) or budget <= 0:
            errors.append(f"{prefix}.timeBudgetMinutes 必須大於 0")

        recovery = require_dict(battlefield, "recovery", errors)
        recovery_status = recovery.get("status")
        if recovery_status not in RECOVERY_STATUSES:
            errors.append(f"{prefix}.recovery.status 不合法")
        require_text(recovery, "action", f"{prefix}.recovery", errors)
        steps = require_text_list(
            recovery, "steps", f"{prefix}.recovery", errors, nonempty=recovery_status == "READY"
        )
        require_text(recovery, "readinessPredicate", f"{prefix}.recovery", errors)
        require_text(recovery, "successPredicate", f"{prefix}.recovery", errors)
        require_text(recovery, "stopCondition", f"{prefix}.recovery", errors)
        recovery_refs = require_claim_refs(
            recovery,
            "evidenceClaimIds",
            f"{prefix}.recovery",
            claims,
            errors,
            nonempty=recovery_status == "READY",
            authoritative_ids=authoritative_ids if recovery_status == "READY" else None,
        )
        if recovery_status == "READY":
            recovery_evidence_status = derive_evidence_check_status(
                recovery,
                f"{prefix}.recovery",
                claims,
                authoritative_ids,
                errors,
                predicate_key="readinessPredicate",
            )
            if not steps or recovery_evidence_status != "PASS":
                errors.append(f"{prefix}.recovery=READY 要求可執行步驟與 exact authoritative PASS readiness evidence")
        if not mutation_scope and recovery_status != "NOT_REQUIRED":
            errors.append(f"{prefix}.mutationScope 為空時 recovery.status 必須為 NOT_REQUIRED")
        if mutation_scope and recovery_status == "NOT_REQUIRED":
            errors.append(f"{prefix}.mutationScope 非空時 recovery.status 不得為 NOT_REQUIRED")
        if status == "ACTIVE" and isinstance(mutation_scope, list) and mutation_scope and recovery_status != "READY":
            errors.append(f"{prefix} 為 ACTIVE mutation 戰場時 recovery 必須 READY")

        has_proven_blocker = battlefield_id in proven_blocked_front_ids
        entry_pass = (
            entry_claim.get("status") == "PASS"
            and entry_claim_id in authoritative_ids
            and entry_claim.get("predicate") == entry_predicate
        )
        # exit 是歷史紀錄：走 recorded 權威集（rank 仲裁、後繼觀測勝出，不看時效）——
        # 已收線的戰場不因時間流逝而腐爛，但仍可被更高權威的反證推翻。
        exit_pass = (
            exit_claim.get("status") == "PASS"
            and exit_claim_id in recorded_ids
            and exit_claim.get("predicate") == exit_predicate
        )
        if status == "ACTIVE" and (not entry_pass or exit_pass or has_proven_blocker):
            errors.append(f"{prefix}=ACTIVE 要求 entry PASS、exit 未 PASS、且無 PROVEN blocker")
        if status == "COMPLETE" and not exit_pass:
            errors.append(f"{prefix}=COMPLETE 要求 exit claim 為權威 PASS")
        if status == "BLOCKED" and not has_proven_blocker:
            errors.append(f"{prefix}=BLOCKED 要求至少一個 PROVEN blocker")
        if status == "PENDING" and entry_pass:
            errors.append(f"{prefix}=PENDING 要求 entry 尚未 PASS")
        if status == "DEFERRED" and not str(battlefield.get("deferReason", "")).strip():
            errors.append(f"{prefix}=DEFERRED 要求非空 deferReason")
        if battlefield.get("effort") == "MAIN" and status == "ACTIVE":
            active_main.append(battlefield)
    if len(active_main) > 1:
        errors.append(f"最多只能有一個 ACTIVE MAIN battlefield，實際 {len(active_main)}")
    for risk_id, risk in risks.items():
        if risk.get("affectedFrontId") not in battlefield_ids:
            errors.append(f"risk {risk_id} 引用不存在的 affectedFrontId")
    for blocker_id, blocker in blockers.items():
        if blocker.get("blockedFrontId") not in battlefield_ids:
            errors.append(f"blocker {blocker_id} 引用不存在的 blockedFrontId")

    decision = require_dict(state, "decision", errors)
    active_front_id = require_text(decision, "activeFrontId", "decision", errors)
    for retired_key in ("pivotPredicate", "pivotWhen"):
        if retired_key in decision:
            errors.append(
                f"decision.{retired_key} 已停用；pivot predicate 固定由 activeFrontId 產生，且 PASS 一律觸發 pivot"
            )
    for key in (
        "chosenTactic",
        "nextAction",
        "rationale",
        "pivotCondition",
        "pivotClaimId",
    ):
        require_text(decision, key, "decision", errors)
    pivot_claim = claims.get(decision.get("pivotClaimId"))
    if pivot_claim is None:
        errors.append("decision.pivotClaimId 必須引用存在的 evidence claim")
    expected_pivot_predicate = canonical_predicate(
        "BATTLEFIELD[{}].PIVOT_TRIGGERED == {}", active_front_id, True
    )
    pivot_contract_valid = pivot_claim is not None and pivot_claim.get("predicate") == expected_pivot_predicate
    if pivot_claim is not None and not pivot_contract_valid:
        errors.append(
            "decision.pivotClaimId 的 claim predicate 必須精確等於 canonical active-front pivot predicate："
            f"{expected_pivot_predicate}"
        )
    pivot_claim_id = decision.get("pivotClaimId")
    pivot_evidence_status = (
        pivot_claim.get("status")
        if pivot_contract_valid and pivot_claim_id in authoritative_ids
        else "UNKNOWN"
    )
    pivot_clear = pivot_evidence_status == "FAIL"
    contribution = decision.get("contribution")
    if contribution not in CONTRIBUTIONS:
        errors.append("decision.contribution 不合法或為 NONE")
    if contribution == "REMOVE_BLOCKER" and not proven_blocked_front_ids:
        errors.append("REMOVE_BLOCKER 要求至少一個 PROVEN blocker")
    if contribution == "CONTROL_RISK" and not any(
        risks.get(risk_id, {}).get("affectedFrontId") == active_front_id
        for risk_id in unacceptable_risk_ids
    ):
        errors.append("CONTROL_RISK 要求目前 activeFrontId 至少有一個 OPEN 且超過門檻的風險")
    if active_main and active_front_id != active_main[0].get("id"):
        errors.append("decision.activeFrontId 未指向唯一 ACTIVE MAIN battlefield")

    unresolved_victory_ids = {
        criterion_id for criterion_id, criterion in victory_by_id.items() if criterion.get("status") != "PASS"
    }
    candidate_list = require_list(decision, "candidates", errors)
    candidates: dict[str, dict[str, Any]] = {}
    eligible_candidates: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidate_list):
        prefix = f"decision.candidates[{index}]"
        if not isinstance(candidate, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        front_id = require_text(candidate, "frontId", prefix, errors)
        if front_id in candidates:
            errors.append(f"candidate frontId 重複：{front_id}")
        elif front_id:
            candidates[front_id] = candidate
        front = battlefields_by_id.get(front_id)
        if front is None:
            errors.append(f"{prefix}.frontId 引用不存在的 battlefield")
            continue
        expected_victory_ids = set(require_text_list(candidate, "expectedVictoryCriterionIds", prefix, errors))
        if not expected_victory_ids.issubset(victory_ids):
            errors.append(f"{prefix}.expectedVictoryCriterionIds 引用不存在的 victory criterion")
        expected_unmet = len(unresolved_victory_ids - expected_victory_ids)
        if candidate.get("unmetVictoryCriteria") != expected_unmet:
            errors.append(f"{prefix}.unmetVictoryCriteria 必須由 victory criteria 算為 {expected_unmet}")
        transitions = require_nonnegative_number(candidate, "remainingTransitions", prefix, errors)
        cost = require_nonnegative_number(candidate, "costMinutes", prefix, errors)
        affected_risks = [
            risk for risk in risks.values() if risk.get("affectedFrontId") == front_id and risk.get("status") != "CLOSED"
        ]
        expected_risk_score = max((int(risk.get("score", 0)) for risk in affected_risks), default=0)
        if candidate.get("riskScore") != expected_risk_score:
            errors.append(f"{prefix}.riskScore 必須由 riskRegister 算為 {expected_risk_score}")
        expected_blocking_risks = sorted(
            risk_id
            for risk_id in unacceptable_risk_ids
            if risks.get(risk_id, {}).get("affectedFrontId") == front_id
        )
        blocking_risk_ids = sorted(require_text_list(candidate, "blockingRiskIds", prefix, errors))
        if blocking_risk_ids != expected_blocking_risks:
            errors.append(f"{prefix}.blockingRiskIds 必須精確列出不可接受風險 {expected_blocking_risks}")
        recovery = front.get("recovery", {})
        recovery_ready = not front.get("mutationScope") or recovery.get("status") in {"READY", "NOT_REQUIRED"}
        expected_eligible = (
            front.get("status") not in {"COMPLETE", "DEFERRED"}
            and front_id not in proven_blocked_front_ids
            and not expected_blocking_risks
            and recovery_ready
        )
        if candidate.get("eligible") is not expected_eligible:
            errors.append(f"{prefix}.eligible 必須由戰場、風險與 recovery 算為 {str(expected_eligible).lower()}")
        reason = candidate.get("ineligibilityReason")
        if not isinstance(reason, str) or (not expected_eligible and not reason.strip()) or (expected_eligible and reason.strip()):
            errors.append(f"{prefix}.ineligibilityReason 必須在不可選時非空、可選時為空")
        if transitions is not None and cost is not None:
            expected_score = expected_unmet * 100 + transitions * 10 + expected_risk_score * 5 + cost
            if candidate.get("totalScore") != expected_score:
                errors.append(f"{prefix}.totalScore 必須依固定公式算為 {expected_score}")
        if expected_eligible:
            eligible_candidates.append(candidate)
    if set(candidates) != battlefield_ids:
        errors.append("decision.candidates 必須恰好涵蓋所有 battlefield")

    minimum_candidate_ids = select_main_candidate_ids(eligible_candidates, priority_order)
    clarity = require_dict(state, "strategicClarity", errors)
    unresolved_decisions = require_list(clarity, "unresolvedDecisions", errors)
    unresolved_ids: set[str] = set()
    for index, item in enumerate(unresolved_decisions):
        prefix = f"strategicClarity.unresolvedDecisions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        item_id = require_text(item, "id", prefix, errors)
        if item_id in unresolved_ids:
            errors.append(f"unresolved decision id 重複：{item_id}")
        unresolved_ids.add(item_id)
        for key in ("question", "decisionPredicate", "owner"):
            require_text(item, key, prefix, errors)
    candidate_main_ids = sorted(require_text_list(clarity, "candidateMainEffortIds", "strategicClarity", errors))
    if candidate_main_ids != minimum_candidate_ids:
        errors.append(f"strategicClarity.candidateMainEffortIds 必須等於最低分候選 {minimum_candidate_ids}")
    has_suspected_blocker = any(blocker.get("status") == "SUSPECTED" for blocker in blockers.values())
    clarity_is_clear = (
        approved_at is not None
        and len(minimum_candidate_ids) == 1
        and not unresolved_decisions
        and not has_suspected_blocker
        and pivot_clear
    )
    terminal_route = not active_main and not eligible_candidates
    expected_clarity = "CLEAR" if clarity_is_clear or terminal_route else "UNCLEAR"
    unclear_causes: list[str] = []
    if not (clarity_is_clear or terminal_route):
        if approved_at is None:
            unclear_causes.append("OBJECTIVE_UNAPPROVED")
        if unresolved_decisions:
            unclear_causes.append("DECISION_FOG")
        if has_suspected_blocker:
            unclear_causes.append("BLOCKER_SUSPECTED")
        if not minimum_candidate_ids:
            unclear_causes.append("NO_ELIGIBLE_CANDIDATE")
        elif len(minimum_candidate_ids) > 1:
            unclear_causes.append("AMBIGUOUS_CANDIDATE")
        if not pivot_clear:
            unclear_causes.append(
                "PIVOT_TRIGGERED" if pivot_evidence_status == "PASS" else "PIVOT_UNPROBED"
            )
        unclear_causes.sort()
    expected_route = (
        "TERMINAL"
        if terminal_route
        else "EXECUTION_READY"
        if clarity_is_clear
        else "WAYFINDER_REQUIRED"
        if "DECISION_FOG" in unclear_causes
        else "OPERATOR_RESOLVE"
    )
    stated_causes = require_text_list(clarity, "unclearCauses", "strategicClarity", errors)
    if list(stated_causes) != unclear_causes:
        errors.append(f"strategicClarity.unclearCauses 必須由決策條件算為 {unclear_causes}")
    if clarity.get("status") not in CLARITY_STATUSES or clarity.get("status") != expected_clarity:
        errors.append(f"strategicClarity.status 必須由決策條件算為 {expected_clarity}")
    if clarity.get("route") not in CLARITY_ROUTES or clarity.get("route") != expected_route:
        errors.append(f"strategicClarity.route 必須為 {expected_route}")
    map_path = clarity.get("wayfinderMapPath")
    if not isinstance(map_path, str) or (expected_route == "WAYFINDER_REQUIRED" and not map_path.strip()):
        errors.append("WAYFINDER_REQUIRED 時 strategicClarity.wayfinderMapPath 不得為空")
    if clarity_is_clear and not terminal_route and active_front_id != minimum_candidate_ids[0]:
        errors.append("戰局 CLEAR 時 activeFrontId 必須是唯一最低分候選")

    progress = require_dict(state, "progress", errors)
    parse_datetime(progress.get("lastWorldStateChangeAt"), "progress.lastWorldStateChangeAt", errors)
    active_front_started_at = parse_datetime(
        progress.get("activeFrontStartedAt"), "progress.activeFrontStartedAt", errors
    )
    if "activeFrontElapsedMinutes" in progress:
        errors.append("progress.activeFrontElapsedMinutes 已停用；主攻時間必須由 activeFrontStartedAt 計算")
    elapsed = None
    if active_front_started_at is not None and updated_at is not None:
        if active_front_started_at > updated_at:
            errors.append("progress.activeFrontStartedAt 不得晚於 state.updatedAt")
        else:
            elapsed = (updated_at - active_front_started_at).total_seconds() / 60
    repeated = progress.get("sameFailureFingerprintCount")
    if not isinstance(repeated, int) or isinstance(repeated, bool) or repeated < 0:
        errors.append("progress.sameFailureFingerprintCount 必須是非負整數")
    alternate_ready = require_bool(progress, "alternateReady", "progress", errors)
    policy = require_dict(progress, "culminationPolicy", errors)
    reanalysis = require_nonnegative_number(policy, "reanalysisMinutes", "progress.culminationPolicy", errors)
    high_risk = require_nonnegative_number(policy, "highRiskMinutes", "progress.culminationPolicy", errors)
    repeat_limit = policy.get("repeatFailureLimit")
    if not isinstance(repeat_limit, int) or isinstance(repeat_limit, bool) or repeat_limit <= 0:
        errors.append("progress.culminationPolicy.repeatFailureLimit 必須是正整數")
    if reanalysis is not None and high_risk is not None and high_risk <= reanalysis:
        errors.append("highRiskMinutes 必須大於 reanalysisMinutes")
    expected_culmination = "LOW"
    if elapsed is not None and high_risk is not None and elapsed >= high_risk:
        expected_culmination = "HIGH"
    elif isinstance(repeated, int) and isinstance(repeat_limit, int) and repeated >= repeat_limit and alternate_ready is False:
        expected_culmination = "HIGH"
    elif (elapsed is not None and reanalysis is not None and elapsed >= reanalysis) or (
        isinstance(repeated, int) and isinstance(repeat_limit, int) and repeated >= repeat_limit
    ):
        expected_culmination = "MEDIUM"
    if progress.get("culminationRisk") not in CULMINATION_RISKS or progress.get("culminationRisk") != expected_culmination:
        errors.append(f"progress.culminationRisk 必須由門檻算為 {expected_culmination}")

    assessment = validate_execution_assessment(state, errors)
    if isinstance(repeated, int) and assessment.get("sameFailureFingerprintCount") != repeated:
        errors.append("progress.sameFailureFingerprintCount 必須等於 executionAssessment 的同名欄位")
    readiness = (
        validate_takeover_readiness(
            state,
            assessment,
            claims,
            authoritative_ids,
            updated_at,
            world_dimensions,
            errors,
        )
        if "takeoverReadiness" in state
        else {}
    )

    intervention = require_dict(state, "intervention", errors)
    intervention_status = intervention.get("status")
    if intervention_status not in INTERVENTION_STATUSES:
        errors.append("intervention.status 不合法")
    intervention_mode = intervention.get("mode")
    intervention_phase = intervention.get("phase")
    if intervention_mode not in INTERVENTION_MODES:
        errors.append("intervention.mode 不合法")
    if intervention_phase not in INTERVENTION_PHASES:
        errors.append("intervention.phase 不合法")
    if intervention_status == "REQUESTED":
        require_text(intervention, "requestedAction", "intervention", errors)
        require_text(intervention, "reason", "intervention", errors)
    elif not isinstance(intervention.get("requestedAction", ""), str):
        errors.append("intervention.requestedAction 必須是字串")
    if not isinstance(intervention.get("reason", ""), str):
        errors.append("intervention.reason 必須是字串")
    if intervention_mode == "TACTICAL_TAKEOVER":
        require_text(intervention, "returnOfControl", "intervention", errors)
        if assessment.get("mode") != "TACTICAL_TAKEOVER":
            errors.append("戰術接管要求 executionAssessment.mode=TACTICAL_TAKEOVER")
        if intervention_status == "REQUESTED":
            if intervention_phase != "TAKEOVER_REQUESTED":
                errors.append("REQUESTED 戰術接管要求 phase=TAKEOVER_REQUESTED")
            if assessment.get("automationActuatorStatus") != "UNRELIABLE":
                errors.append("REQUESTED 戰術接管要求 automationActuatorStatus=UNRELIABLE")
            if readiness.get("result") != "TACTICAL_ACTION_READY":
                errors.append("REQUESTED 戰術接管必須通過 OPERABLE／EXECUTABLE／VERIFIABLE 三道門")
            executable_steps = readiness.get("executable", {}).get("steps", [])
            if (
                len(executable_steps) != 1
                or intervention.get("requestedAction") != executable_steps[0]
            ):
                errors.append(
                    "REQUESTED 戰術接管的 requestedAction 必須 byte-equal 唯一 executable step"
                )
        elif intervention_status == "IN_PROGRESS":
            if intervention_phase not in {"USER_ACTION_IN_PROGRESS", "BATTLE_DAMAGE_ASSESSMENT"}:
                errors.append("IN_PROGRESS 戰術接管 phase 不合法")
        else:
            errors.append("TACTICAL_TAKEOVER 只允許 intervention.status=REQUESTED 或 IN_PROGRESS")
    else:
        if intervention_phase != "NONE":
            errors.append("非戰術接管要求 intervention.phase=NONE")
        if assessment.get("mode") != "AUTONOMOUS":
            errors.append("非戰術接管要求 executionAssessment.mode=AUTONOMOUS")
        if not isinstance(intervention.get("returnOfControl", ""), str):
            errors.append("intervention.returnOfControl 必須是字串")

    loss_derivation = validate_loss_minimization_assessment(
        state, unacceptable_outcomes, claims, authoritative_ids, errors
    )

    terminal = require_dict(state, "terminalAssessment", errors)
    required_authority = terminal.get("requiredAuthority")
    if not isinstance(required_authority, str):
        errors.append("terminalAssessment.requiredAuthority 必須是字串")
        required_authority = ""
    alternatives = require_list(terminal, "alternativeRoutes", errors)
    alternative_statuses: list[str] = []
    alternative_ids: set[str] = set()
    for index, alternative in enumerate(alternatives):
        prefix = f"terminalAssessment.alternativeRoutes[{index}]"
        if not isinstance(alternative, dict):
            errors.append(f"{prefix} 必須是 object")
            continue
        reject_unknown_fields(
            alternative,
            {"id", "status", "reason", "statusChecks"},
            prefix,
            errors,
        )
        alternative_id = require_text(alternative, "id", prefix, errors)
        if alternative_id in alternative_ids:
            errors.append(f"alternative route id 重複：{alternative_id}")
        alternative_ids.add(alternative_id)
        require_text(alternative, "reason", prefix, errors)
        status_checks = require_dict(alternative, "statusChecks", errors)
        expected_check_names = {"CLOSED", "UNSAFE", "REQUIRES_AUTHORITY"}
        if set(status_checks) != expected_check_names:
            errors.append(
                f"{prefix}.statusChecks 必須精確包含 CLOSED、UNSAFE、REQUIRES_AUTHORITY"
            )
        proven_statuses: list[str] = []
        for route_status in sorted(expected_check_names):
            check = status_checks.get(route_status)
            check_prefix = f"{prefix}.statusChecks.{route_status}"
            if not isinstance(check, dict):
                errors.append(f"{check_prefix} 必須是 object")
                continue
            reject_unknown_fields(check, {"predicate", "evidenceClaimIds"}, check_prefix, errors)
            if (
                derive_evidence_check_status(
                    check, check_prefix, claims, authoritative_ids, errors
                )
                == "PASS"
            ):
                proven_statuses.append(route_status)
        if len(proven_statuses) > 1:
            errors.append(f"{prefix}.statusChecks 不得同時證明多個 route status：{proven_statuses}")
        expected_route_status = proven_statuses[0] if len(proven_statuses) == 1 else "OPEN"
        status = alternative.get("status")
        if status not in ALTERNATIVE_ROUTE_STATUSES:
            errors.append(f"{prefix}.status 不合法")
        elif status != expected_route_status:
            errors.append(f"{prefix}.status 必須由 statusChecks 算為 {expected_route_status}")
        alternative_statuses.append(expected_route_status)
    all_victory_pass = bool(victory_criteria) and all(
        isinstance(item, dict) and item.get("status") == "PASS" for item in victory_criteria
    )
    open_blocking_cleanup = any(
        isinstance(item, dict) and item.get("status") == "OPEN" and item.get("blocksVictory") is True
        for item in cleanup_debt
    )
    terminal_postconditions_met = (
        not any(
            isinstance(front, dict) and front.get("status") == "ACTIVE"
            for front in battlefields
        )
        and not eligible_candidates
        and intervention_status == "NOT_REQUIRED"
        and intervention_mode == "NONE"
        and intervention_phase == "NONE"
        and (not readiness or readiness.get("result") == "NOT_READY")
    )
    if all_victory_pass and not open_blocking_cleanup and terminal_postconditions_met:
        expected_terminal = "STRATEGIC_OBJECTIVE_ACHIEVED"
    elif (
        not all_victory_pass
        and assessment.get("outcomeStatus") != "OUTCOME_UNKNOWN"
        and "OPEN" not in alternative_statuses
        and "REQUIRES_AUTHORITY" in alternative_statuses
        and required_authority.strip()
        and terminal_postconditions_met
    ):
        expected_terminal = "NEW_AUTHORITY_REQUIRED"
    elif (
        not all_victory_pass
        and loss_derivation["victoryUnattainableProven"]
        and assessment.get("outcomeStatus") != "OUTCOME_UNKNOWN"
        and bool(alternative_statuses)
        and "OPEN" not in alternative_statuses
        and "REQUIRES_AUTHORITY" not in alternative_statuses
        and loss_derivation["unacceptableOutcomesProven"]
        and loss_derivation["residualLossBounded"]
        and loss_derivation["preservedGainsProven"]
        and not open_blocking_cleanup
        and terminal_postconditions_met
    ):
        expected_terminal = "LOSS_MINIMIZED"
    else:
        expected_terminal = "IN_PROGRESS"
    if terminal.get("status") not in TERMINAL_STATUSES or terminal.get("status") != expected_terminal:
        errors.append(f"terminalAssessment.status 必須由終局 predicate 算為 {expected_terminal}")
    if expected_terminal == "IN_PROGRESS" and len(active_main) != 1:
        errors.append(f"IN_PROGRESS 必須恰有一個 ACTIVE MAIN battlefield，實際 {len(active_main)}")
    if terminal.get("status") in TERMINAL_STATUSES - {"IN_PROGRESS"} and not terminal_postconditions_met:
        errors.append(
            "合法終局要求零 ACTIVE battlefield、零 eligible candidate、takeoverReadiness 缺席或 NOT_READY，且 intervention=NOT_REQUIRED/NONE/NONE"
        )
    if expected_terminal == "NEW_AUTHORITY_REQUIRED" and not required_authority.strip():
        errors.append("NEW_AUTHORITY_REQUIRED 要求 requiredAuthority 非空")
    if "REQUIRES_AUTHORITY" in alternative_statuses and not required_authority.strip():
        errors.append("alternative route=REQUIRES_AUTHORITY 要求 requiredAuthority 非空")
    if expected_terminal == "LOSS_MINIMIZED" and required_authority.strip():
        errors.append("LOSS_MINIMIZED 要求 requiredAuthority 為空")

    advance = state.get("latestVerifiedAdvance")
    if advance is not None:
        if not isinstance(advance, dict):
            errors.append("latestVerifiedAdvance 必須是 object 或 null")
        else:
            reject_unknown_fields(
                advance,
                {
                    "at",
                    "scopeIdentity",
                    "dimension",
                    "from",
                    "to",
                    "beforeValue",
                    "afterValue",
                    "beforeClaimId",
                    "afterClaimId",
                    "strategicEffect",
                    "effectTargetId",
                    "evidence",
                    "evidenceClaimIds",
                },
                "latestVerifiedAdvance",
                errors,
            )
            advance_at = parse_datetime(advance.get("at"), "latestVerifiedAdvance.at", errors)
            for key in (
                "scopeIdentity",
                "dimension",
                "from",
                "to",
            ):
                require_text(advance, key, "latestVerifiedAdvance", errors)
            if advance.get("dimension") not in world_dimensions:
                errors.append("latestVerifiedAdvance.dimension 必須是 strategicObjective.worldDimensions 成員")
            effect = advance.get("strategicEffect")
            if effect not in STRATEGIC_EFFECTS:
                errors.append("latestVerifiedAdvance.strategicEffect 不合法")
            effect_target = require_text(
                advance, "effectTargetId", "latestVerifiedAdvance", errors
            )
            target_sets = {
                "SATISFIES_VICTORY_CRITERION": victory_ids,
                "REMOVES_PROVEN_BLOCKER": set(blockers),
                "CONTROLS_UNACCEPTABLE_RISK": set(risks),
                "ENABLES_NEXT_TRANSITION": battlefield_ids,
            }
            if effect in target_sets and effect_target not in target_sets[effect]:
                errors.append("latestVerifiedAdvance.effectTargetId 未指向 strategicEffect 對應對象")
            effect_target_valid = False
            if effect == "SATISFIES_VICTORY_CRITERION":
                effect_target_valid = victory_by_id.get(effect_target, {}).get("status") == "PASS"
            elif effect == "REMOVES_PROVEN_BLOCKER":
                effect_target_valid = blockers.get(effect_target, {}).get("status") == "CLEARED"
            elif effect == "CONTROLS_UNACCEPTABLE_RISK":
                target_risk = risks.get(effect_target, {})
                effect_target_valid = (
                    target_risk.get("status") in {"CONTROLLED", "CLOSED"}
                    and isinstance(target_risk.get("score"), int)
                    and isinstance(target_risk.get("unacceptableThreshold"), int)
                    and target_risk.get("score") >= target_risk.get("unacceptableThreshold")
                )
            elif effect == "ENABLES_NEXT_TRANSITION":
                target_front = battlefields_by_id.get(effect_target, {})
                target_entry_claim_id = target_front.get("entryClaimId")
                target_entry_claim = claims.get(target_entry_claim_id, {})
                expected_target_entry = canonical_predicate(
                    "BATTLEFIELD[{}].ENTRY[{}] == {}",
                    effect_target,
                    target_front.get("entryState"),
                    True,
                )
                effect_target_valid = (
                    target_entry_claim_id in recorded_ids
                    and target_entry_claim.get("status") == "PASS"
                    and target_entry_claim.get("predicate") == expected_target_entry
                )
            if effect in STRATEGIC_EFFECTS and effect_target in target_sets.get(effect, set()) and not effect_target_valid:
                errors.append(
                    "latestVerifiedAdvance.strategicEffect 與 effectTargetId 的 current derived state 不相符"
                )
            before_claim_id = require_text(advance, "beforeClaimId", "latestVerifiedAdvance", errors)
            after_claim_id = require_text(advance, "afterClaimId", "latestVerifiedAdvance", errors)
            before_claim = claims.get(before_claim_id)
            after_claim = claims.get(after_claim_id)
            for name, claim_id, claim in (
                ("beforeClaimId", before_claim_id, before_claim),
                ("afterClaimId", after_claim_id, after_claim),
            ):
                if claim is None:
                    errors.append(f"latestVerifiedAdvance.{name} 引用不存在的 claim")
                elif claim_id not in recorded_ids or claim.get("status") != "PASS":
                    errors.append(f"latestVerifiedAdvance.{name} 必須是有效權威 PASS claim")
            before_predicate = canonical_predicate(
                "WORLD[{}].DIMENSION[{}] == {}",
                advance.get("scopeIdentity"),
                advance.get("dimension"),
                advance.get("beforeValue"),
            )
            after_predicate = canonical_predicate(
                "WORLD[{}].DIMENSION[{}] == {}",
                advance.get("scopeIdentity"),
                advance.get("dimension"),
                advance.get("afterValue"),
            )
            if before_claim is not None and before_claim.get("predicate") != before_predicate:
                errors.append(
                    "latestVerifiedAdvance.beforeClaimId 的 claim predicate 必須精確等於 canonical WORLD before predicate："
                    f"{before_predicate}"
                )
            if after_claim is not None and after_claim.get("predicate") != after_predicate:
                errors.append(
                    "latestVerifiedAdvance.afterClaimId 的 claim predicate 必須精確等於 canonical WORLD after predicate："
                    f"{after_predicate}"
                )
            if "beforeValue" not in advance or "afterValue" not in advance:
                errors.append("latestVerifiedAdvance 必須同時提供 beforeValue 與 afterValue")
            elif advance.get("beforeValue") == advance.get("afterValue"):
                errors.append("latestVerifiedAdvance.beforeValue 與 afterValue 必須不同")
            if str(advance.get("beforeValue")) != advance.get("from"):
                errors.append("latestVerifiedAdvance.from 必須等於 beforeValue 的字串表示")
            if str(advance.get("afterValue")) != advance.get("to"):
                errors.append("latestVerifiedAdvance.to 必須等於 afterValue 的字串表示")
            if before_claim is not None and after_claim is not None:
                before_at = parse_datetime(before_claim.get("observedAt"), "latestVerifiedAdvance.beforeClaim.observedAt", [])
                after_at = parse_datetime(after_claim.get("observedAt"), "latestVerifiedAdvance.afterClaim.observedAt", [])
                if before_at is not None and after_at is not None and before_at >= after_at:
                    errors.append("latestVerifiedAdvance 要求 before claim 早於 after claim")
                if advance_at is not None and after_at is not None and advance_at != after_at:
                    errors.append("latestVerifiedAdvance.at 必須等於 after claim 的 observedAt")
            require_text_list(advance, "evidence", "latestVerifiedAdvance", errors, nonempty=True)
            advance_refs = require_claim_refs(
                advance,
                "evidenceClaimIds",
                "latestVerifiedAdvance",
                claims,
                errors,
                nonempty=True,
                authoritative_ids=recorded_ids,
            )
            if set(advance_refs) != {before_claim_id, after_claim_id}:
                errors.append("latestVerifiedAdvance.evidenceClaimIds 必須精確包含 beforeClaimId 與 afterClaimId")
            last_change = parse_datetime(progress.get("lastWorldStateChangeAt"), "progress.lastWorldStateChangeAt", [])
            if advance_at is not None and last_change is not None and advance_at != last_change:
                errors.append("latestVerifiedAdvance.at 必須等於 progress.lastWorldStateChangeAt")
    if assessment.get("worldStateChanged") is True and advance is None:
        errors.append("worldStateChanged=true 要求 latestVerifiedAdvance 非 null")
    return errors


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def normalize_language(language: str) -> str:
    return "en" if language == "en" else "zh-TW"


def human_label(value: Any, language: str = "zh-TW") -> str:
    text = str(value)
    labels = LABELS_EN if normalize_language(language) == "en" else LABELS
    return labels.get(text, text)


def terminal_label(value: Any, language: str = "zh-TW") -> str:
    labels = {
        "IN_PROGRESS": "戰役進行中",
        "STRATEGIC_OBJECTIVE_ACHIEVED": "戰略目標已達成",
        "NEW_AUTHORITY_REQUIRED": "需要新權限",
        "LOSS_MINIMIZED": "損失已降至可證明界線",
    }
    if normalize_language(language) == "en":
        labels = {
            "IN_PROGRESS": "Campaign in progress",
            "STRATEGIC_OBJECTIVE_ACHIEVED": "Strategic objective achieved",
            "NEW_AUTHORITY_REQUIRED": "New authority required",
            "LOSS_MINIMIZED": "Loss minimized within proven bounds",
        }
    return labels.get(str(value), str(value))


def active_front(state: dict[str, Any]) -> dict[str, Any]:
    target = state["decision"]["activeFrontId"]
    return next(front for front in state["battlefields"] if front["id"] == target)


def build_summary(state: dict[str, Any], language: str = "zh-TW") -> str:
    front = active_front(state)
    briefing = state["plainBriefing"]
    assessment = state["executionAssessment"]
    readiness = state.get("takeoverReadiness") or {}
    intervention = state["intervention"]
    clarity = state["strategicClarity"]
    terminal = state["terminalAssessment"]
    if normalize_language(language) == "en":
        lines = [
            f"Strategic objective: {state['strategicObjective']['purpose']}",
            f"Context: {briefing['context']}",
            f"Now: {briefing['currentSituation']}",
            f"Judgment: {briefing['reasoning']}",
            f"Main effort: {front['objective']}",
            f"Next move: {briefing['nextMove']}",
            f"Your role: {briefing['userRole']}",
            f"Actuator: {human_label(assessment['automationActuatorStatus'], language)}",
            f"Takeover gate: {human_label(readiness['result'], language) if readiness else 'Not engaged'}",
            f"Strategic clarity: {human_label(clarity['status'], language)} / {human_label(clarity['route'], language)}"
            + (
                ' (causes: ' + ', '.join(human_label(c, language) for c in clarity.get('unclearCauses', [])) + ')'
                if clarity.get('unclearCauses')
                else ''
            ),
            f"Terminal assessment: {terminal_label(terminal['status'], language)}",
            f"Intervention: {human_label(intervention['status'], language)} / {human_label(intervention['phase'], language)}",
        ]
    else:
        lines = [
            f"戰略目標：{state['strategicObjective']['purpose']}",
            f"背景：{briefing['context']}",
            f"現在：{briefing['currentSituation']}",
            f"判斷：{briefing['reasoning']}",
            f"唯一主攻：{front['objective']}",
            f"下一動：{briefing['nextMove']}",
            f"你的角色：{briefing['userRole']}",
            f"執行器：{human_label(assessment['automationActuatorStatus'])}",
            f"接管門：{human_label(readiness['result']) if readiness else '未啟用'}",
            f"戰局清晰度：{human_label(clarity['status'])}／{human_label(clarity['route'])}"
            + (
                '（成因：' + '、'.join(human_label(c) for c in clarity.get('unclearCauses', [])) + '）'
                if clarity.get('unclearCauses')
                else ''
            ),
            f"終局判定：{terminal_label(terminal['status'])}",
            f"介入狀態：{human_label(intervention['status'])}／{human_label(intervention['phase'])}",
        ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Derivations shared by every view of the campaign.
#
# These three read state and return state — a label, a predecessor map, an
# ancestor list. They used to sit among the SVG helpers below because the battle
# map was their only caller; that placement made the retirement cut line pass
# straight through them. They live above it now, so retiring the python
# rendering surface is a contiguous deletion rather than an untangling.
# ---------------------------------------------------------------------------


def battlefield_effect(
    state: dict[str, Any], front: dict[str, Any], active_id: str, language: str = "zh-TW"
) -> str:
    english = normalize_language(language) == "en"
    if front["id"] == active_id:
        return "Directly advances the objective" if english else "直接推進戰略目標"
    has_proven_blocker = any(
        blocker.get("status") == "PROVEN" and blocker.get("blockedFrontId") == active_id
        for blocker in state.get("blockers", [])
        if isinstance(blocker, dict)
    )
    if has_proven_blocker or front["operationType"] == "SHAPING":
        return "Removes a blocker" if english else "移除主攻障礙"
    if front["operationType"] == "SUSTAINING":
        return "Sustains operating conditions" if english else "維持作戰條件"
    return "Supports the main effort" if english else "支援主攻"


def causal_predecessor_map(state: dict[str, Any]) -> dict[str, list[str]]:
    """Return only explicit or unique exact state-transition predecessors."""
    fronts = [front for front in state["battlefields"] if isinstance(front, dict)]
    by_id = {str(front["id"]): front for front in fronts}
    result: dict[str, list[str]] = {}
    for front in fronts:
        front_id = str(front["id"])
        explicit = [
            str(candidate)
            for candidate in front.get("causalPredecessorIds", [])
            if str(candidate) in by_id
            and str(candidate) != front_id
            and by_id[str(candidate)].get("terminalState") == front.get("entryState")
        ]
        predecessors = list(dict.fromkeys(explicit))
        exact = [
            str(candidate["id"])
            for candidate in fronts
            if str(candidate["id"]) != front_id
            and candidate.get("terminalState") == front.get("entryState")
        ]
        if len(exact) == 1 and exact[0] not in predecessors:
            predecessors.append(exact[0])
        result[front_id] = predecessors
    return result


def completed_causal_ancestors(state: dict[str, Any], front_id: str) -> list[dict[str, Any]]:
    by_id = {str(front["id"]): front for front in state["battlefields"]}
    predecessors = causal_predecessor_map(state)
    seen: set[str] = set()
    ordered: list[dict[str, Any]] = []

    def visit(candidate_id: str) -> None:
        if candidate_id in seen:
            return
        seen.add(candidate_id)
        for predecessor_id in predecessors.get(candidate_id, []):
            visit(predecessor_id)
        candidate = by_id.get(candidate_id)
        if candidate is not None and candidate.get("status") == "COMPLETE":
            ordered.append(candidate)

    for predecessor_id in predecessors.get(front_id, []):
        visit(predecessor_id)
    return ordered


# ---------------------------------------------------------------------------
# SVG battle map (`render-graph`, and the `battle-map.svg` half of `render-all`).
#
# The self-contained HTML renderer below embeds this SVG in the sand table;
# `render-graph` also exposes it as a standalone artifact.
# ---------------------------------------------------------------------------


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def list_html(values: list[Any]) -> str:
    return "".join(f"<li>{esc(item)}</li>" for item in values) or "<li>無</li>"


def visual_text_width(value: str) -> float:
    return sum(0.55 if ord(character) < 128 else 1 for character in value)


def split_visual_word(value: str, limit: int) -> list[str]:
    parts: list[str] = []
    current = ""
    for character in value:
        if current and visual_text_width(f"{current}{character}") > limit:
            parts.append(current)
            current = character
        else:
            current = f"{current}{character}"
    if current:
        parts.append(current)
    return parts


def wrap_svg_text(value: Any, limit: int = 18, maximum_lines: int = 3) -> list[str]:
    text = str(value).strip()
    if not text:
        return ["無"]
    lines: list[str] = []
    current = ""
    words = [part for word in text.split() for part in split_visual_word(word, limit)]
    for word in words:
        candidate = f"{current} {word}".strip()
        if visual_text_width(candidate) <= limit:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    if len(lines) > maximum_lines:
        lines = lines[:maximum_lines]
        lines[-1] = f"{lines[-1][:-1]}…"
    return lines


def svg_multiline(
    value: Any,
    x: int,
    y: int,
    css_class: str,
    limit: int = 18,
    maximum_lines: int = 3,
) -> str:
    spans = "".join(
        f'<tspan x="{x}" dy="{0 if index == 0 else 22}">{esc(line)}</tspan>'
        for index, line in enumerate(wrap_svg_text(value, limit, maximum_lines))
    )
    return f'<text x="{x}" y="{y}" class="{css_class}">{spans}</text>'


def chamfer_path(x: int, y: int, width: int, height: int, cut: int = 14) -> str:
    return (
        f"M {x} {y} H {x + width - cut} L {x + width} {y + cut} V {y + height} "
        f"H {x + cut} L {x} {y + height - cut} Z"
    )


def corner_ticks(x: int, y: int, width: int, height: int, size: int = 10) -> str:
    return (
        f'<path class="tick" d="M {x} {y + size} V {y} H {x + size}"/>'
        f'<path class="tick" d="M {x + width - size} {y + height} H {x + width} V {y + height - size}"/>'
    )


def render_battle_map_svg(
    state: dict[str, Any], language: str = "zh-TW", *, full_history: bool = False
) -> str:
    language = normalize_language(language)
    if full_history:
        return render_full_history_svg(state, language)
    return render_compact_battle_map_svg(state, language)


def render_compact_battle_map_svg(state: dict[str, Any], language: str) -> str:
    english = language == "en"
    victory_achieved = state["terminalAssessment"]["status"] == "STRATEGIC_OBJECTIVE_ACHIEVED"
    main_front = active_front(state)
    completed = completed_causal_ancestors(state, str(main_front["id"]))
    completed_ids = {str(front["id"]) for front in completed}
    side_fronts = [
        front
        for front in state["battlefields"]
        if str(front["id"]) != str(main_front["id"]) and str(front["id"]) not in completed_ids
    ]
    side_limit = 4
    visible_side = side_fronts[:side_limit]
    hidden_count = max(0, len(side_fronts) - side_limit)
    width, height = 1480, 500
    rail_x, rail_width = 28, 210
    current_x, current_width = 285, 330
    next_x, next_width = 700, 350
    goal_x, goal_width = 1135, 315
    node_y, node_height = 175, 150
    centre_y = node_y + node_height // 2

    text = {
        "title": "Battle map" if english else "戰局圖",
        "desc": (
            "Compact situation display focused on current state, next move, and strategic end state. "
            "Independent fronts are shown without invented causal edges."
            if english
            else "精簡戰局圖聚焦目前狀態、下一動與戰略終局；獨立戰場只列在側欄，不虛構因果連線。"
        ),
        "rail": "INDEPENDENT / SUPPORT" if english else "獨立／支援戰場",
        "current": "CURRENT STATE" if english else "目前狀態",
        "next": "NEXT MOVE" if english else "下一動",
        "goal": "STRATEGIC END STATE" if english else "戰略終局",
        "advance": "advance" if english else "推進",
        "effect": "verify effect" if english else "驗證戰果",
        "none": "No independent fronts" if english else "目前沒有獨立戰場",
        "more": "more fronts" if english else "個其他戰場",
        "completed": "completed causal ancestors" if english else "個已完成因果前置",
        "takeover": "Tactical takeover" if english else "戰術接管",
    }
    if victory_achieved:
        text.update(
            {
                "title": "Completed battle map" if english else "戰局完成圖",
                "desc": (
                    "Sealed campaign display: final state, verified effects, and completed strategic objective."
                    if english
                    else "已封盤戰局：最終狀態、已驗證戰果與完成的戰略目標。"
                ),
                "current": "FINAL STATE" if english else "最終狀態",
                "next": "EFFECTS VERIFIED" if english else "戰果確認",
                "goal": "CAMPAIGN COMPLETE" if english else "戰局完成",
                "advance": "verified" if english else "已驗證",
                "effect": "secured" if english else "已鞏固",
            }
        )

    # Build primary nodes separately to keep authored state prose untouched.
    next_title = state["decision"]["nextAction"]
    next_status = human_label(main_front["effort"], language)
    goal_status = terminal_label(state["terminalAssessment"]["status"], language)
    if victory_achieved:
        next_title = (
            "All victory criteria passed; no active main effort remains"
            if english
            else "所有勝利條件已通過，無剩餘主攻"
        )
        next_status = "SEALED" if english else "已封盤"
        goal_status = "Campaign complete" if english else "戰局完成"
    primary_nodes = (
        f'<g class="node-current"><path class="frame" d="{chamfer_path(current_x, node_y, current_width, node_height)}"/>'
        f'<text x="{current_x + 17}" y="{node_y + 31}" class="node-kicker">{esc(text["current"])}</text>'
        f'<g clip-path="url(#clip-current-title)">{svg_multiline(state["plainBriefing"]["currentSituation"], current_x + 17, node_y + 65, "node-title", 18, 2)}</g>'
        f'<text x="{current_x + 17}" y="{node_y + node_height - 17}" class="node-status">{esc(human_label(main_front["status"], language))}</text></g>'
        f'<g class="node-next"><path class="frame" d="{chamfer_path(next_x, node_y, next_width, node_height)}"/>'
        f'{corner_ticks(next_x, node_y, next_width, node_height)}'
        f'<text x="{next_x + 17}" y="{node_y + 31}" class="node-kicker">{esc(text["next"])}</text>'
        f'<g clip-path="url(#clip-next-title)">{svg_multiline(next_title, next_x + 17, node_y + 65, "node-title", 20, 2)}</g>'
        f'<text x="{next_x + 17}" y="{node_y + node_height - 17}" class="node-status">{esc(next_status)}</text></g>'
        f'<g class="node-goal"><path class="frame" d="{chamfer_path(goal_x, node_y, goal_width, node_height)}"/>'
        f'<text x="{goal_x + 17}" y="{node_y + 31}" class="node-kicker">{esc(text["goal"])}</text>'
        f'<g clip-path="url(#clip-goal-title)">{svg_multiline(state["strategicObjective"]["desiredEndState"][0], goal_x + 17, node_y + 65, "node-title", 17, 2)}</g>'
        f'<text x="{goal_x + 17}" y="{node_y + node_height - 17}" class="node-status">{esc(goal_status)}</text></g>'
    )

    side_nodes: list[str] = []
    if visible_side:
        for index, front in enumerate(visible_side):
            y = 90 + index * 88
            side_nodes.append(
                f'<g class="node-side"><rect x="{rail_x}" y="{y}" width="{rail_width}" height="70" rx="3"/>'
                f'<text x="{rail_x + 13}" y="{y + 23}" class="side-kicker">{esc(human_label(front["operationType"], language))} · {esc(human_label(front["status"], language))}</text>'
                f'{svg_multiline(front["objective"], rail_x + 13, y + 48, "side-title", 14, 1)}</g>'
            )
    else:
        side_nodes.append(
            f'<text x="{rail_x + rail_width // 2}" y="190" class="empty" text-anchor="middle">{esc(text["none"])}</text>'
        )
    if hidden_count:
        side_nodes.append(
            f'<text x="{rail_x + 13}" y="{90 + len(visible_side) * 88 + 18}" class="more">+{hidden_count} {esc(text["more"])}</text>'
        )

    completed_chip = ""
    if completed:
        completed_chip = (
            f'<g class="completed-chip"><rect x="{current_x}" y="110" width="{current_width}" height="38" rx="3"/>'
            f'<text x="{current_x + 14}" y="134">✓ {len(completed)} {esc(text["completed"])}</text></g>'
        )
    takeover_chip = ""
    intervention = state["intervention"]
    if intervention["mode"] == "TACTICAL_TAKEOVER" and intervention["status"] in {"REQUESTED", "IN_PROGRESS"}:
        takeover_chip = (
            f'<g class="takeover-chip"><rect x="{next_x + 88}" y="110" width="174" height="38" rx="3"/>'
            f'<text x="{next_x + 105}" y="134">{esc(text["takeover"])}</text></g>'
        )

    map_class = ' class="victory-map"' if victory_achieved else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"{map_class} role="img" aria-labelledby="battle-map-title battle-map-desc">
  <title id="battle-map-title">{esc(text["title"])}</title>
  <desc id="battle-map-desc">{esc(text["desc"])}</desc>
  <defs>
    <pattern id="tac-grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 H 0 V 40" fill="none" stroke="#0b1a28" stroke-width="1"/></pattern>
    <marker id="arrow-main" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#2bffb5"/></marker>
    <clipPath id="clip-current-title"><rect x="{current_x + 14}" y="{node_y + 46}" width="{current_width - 28}" height="52"/></clipPath>
    <clipPath id="clip-next-title"><rect x="{next_x + 14}" y="{node_y + 46}" width="{next_width - 28}" height="52"/></clipPath>
    <clipPath id="clip-goal-title"><rect x="{goal_x + 14}" y="{node_y + 46}" width="{goal_width - 28}" height="52"/></clipPath>
  </defs>
  <style>
    text{{font-family:"Microsoft JhengHei","Noto Sans TC",system-ui,sans-serif}}
    .frame{{stroke-width:1.7}} .node-current .frame{{fill:#0a1723;stroke:#43c6ff}}
    .node-next .frame{{fill:#07231c;stroke:#2bffb5;stroke-width:2.2}}
    .node-goal .frame{{fill:#231806;stroke:#ffb043;stroke-width:2}}
    .node-kicker{{font:700 12px "Cascadia Code",Consolas,monospace;fill:#7898aa;letter-spacing:.18em}}
    .node-next .node-kicker{{fill:#2bffb5}} .node-goal .node-kicker{{fill:#ffb043}}
    .node-title{{font-size:15px;fill:#eaf6f4;font-weight:700}} .node-status{{font-size:11px;fill:#8fa9b8}}
    .tick{{fill:none;stroke:#2bffb5;stroke-width:2}} .edge-main{{fill:none;stroke:#2bffb5;stroke-width:3.5;stroke-dasharray:13 8}}
    .edge-label{{font-size:12px;fill:#2bffb5;font-weight:700}} .rail-title{{font:700 12px "Cascadia Code",Consolas,monospace;fill:#5d7f93;letter-spacing:.15em}}
    .rail-rule{{stroke:#20384b}} .node-side rect{{fill:#08131e;stroke:#25455c}} .side-kicker{{font-size:10px;fill:#638398}}
    .side-title{{font-size:13px;fill:#c9dbe2}} .empty,.more,.note{{font-size:12px;fill:#587586}}
    .completed-chip rect{{fill:#0a1f17;stroke:#37d495}} .completed-chip text{{font-size:12px;fill:#79dfba}}
    .takeover-chip rect{{fill:#231806;stroke:#ffb043}} .takeover-chip text{{font-size:12px;fill:#ffcc7f;font-weight:700}}
    .victory-map .node-current .frame{{stroke:#86d9ff}}
    .victory-map .node-next .frame{{fill:#08281d;stroke:#6fffc4;filter:drop-shadow(0 0 8px rgba(43,255,181,.42))}}
    .victory-map .node-goal .frame{{fill:#2a2108;stroke:#ffd36e;filter:drop-shadow(0 0 10px rgba(255,176,67,.48))}}
    .victory-map .edge-main{{stroke:#74fbc4;stroke-dasharray:none}}
  </style>
  <rect width="{width}" height="{height}" fill="#05090f"/><rect width="{width}" height="{height}" fill="url(#tac-grid)"/>
  <text x="{rail_x}" y="54" class="rail-title">{esc(text["rail"])}</text><line x1="{rail_x}" y1="68" x2="{rail_x + rail_width}" y2="68" class="rail-rule"/>
  {''.join(side_nodes)}
  <line x1="260" y1="60" x2="260" y2="450" class="rail-rule"/>
  {completed_chip}{takeover_chip}
  <path d="M {current_x + current_width} {centre_y} H {next_x - 18}" class="edge-main" marker-end="url(#arrow-main)"/>
  <text x="{current_x + current_width + 16}" y="{centre_y - 14}" class="edge-label">{esc(text["advance"])}</text>
  <path d="M {next_x + next_width} {centre_y} H {goal_x - 18}" class="edge-main" marker-end="url(#arrow-main)"/>
  <text x="{next_x + next_width + 10}" y="{centre_y - 14}" class="edge-label">{esc(text["effect"])}</text>
  {primary_nodes}
</svg>'''


def render_full_history_svg(state: dict[str, Any], language: str) -> str:
    english = language == "en"
    fronts = state["battlefields"]
    predecessors = causal_predecessor_map(state)
    width = 1120
    node_x, node_width, node_height, gap = 330, 470, 100, 42
    top = 92
    height = max(360, top + len(fronts) * (node_height + gap) + 72)
    by_index = {str(front["id"]): index for index, front in enumerate(fronts)}
    labels = {
        "title": "Full battle history" if english else "完整戰局歷史",
        "desc": (
            "All fronts; arrows appear only for explicit or unique exact state transitions."
            if english else "顯示所有戰場；只有明確指定或唯一完全吻合的狀態轉換才畫箭頭。"
        ),
        "note": (
            "No line means no proven causal relationship."
            if english else "沒有連線，表示尚無可證明的因果關係。"
        ),
        "goal": "STRATEGIC END STATE" if english else "戰略終局",
    }
    edges: list[str] = []
    for target_id, source_ids in predecessors.items():
        if target_id not in by_index:
            continue
        target_y = top + by_index[target_id] * (node_height + gap) + node_height // 2
        for lane, source_id in enumerate(source_ids):
            if source_id not in by_index:
                continue
            source_y = top + by_index[source_id] * (node_height + gap) + node_height // 2
            bend_x = node_x - 44 - lane * 18
            edges.append(
                f'<path d="M {node_x} {source_y} H {bend_x} V {target_y} H {node_x - 12}" class="causal" marker-end="url(#arrow-causal)"/>'
            )
    nodes = "".join(
        f'<g class="history-node status-{esc(str(front["status"]).lower())}"><rect x="{node_x}" y="{top + index * (node_height + gap)}" width="{node_width}" height="{node_height}" rx="3"/>'
        f'<text x="{node_x + 16}" y="{top + index * (node_height + gap) + 25}" class="history-kicker">{esc(human_label(front["operationType"], language))} · {esc(human_label(front["effort"], language))} · {esc(human_label(front["status"], language))}</text>'
        f'{svg_multiline(front["objective"], node_x + 16, top + index * (node_height + gap) + 53, "history-title", 35)}'
        f'<text x="{node_x + node_width + 28}" y="{top + index * (node_height + gap) + 48}" class="state-token">{esc(front["entryState"])} → {esc(front["terminalState"])}</text></g>'
        for index, front in enumerate(fronts)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="full-history-title full-history-desc">
  <title id="full-history-title">{esc(labels["title"])}</title><desc id="full-history-desc">{esc(labels["desc"])}</desc>
  <defs><marker id="arrow-causal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#43c6ff"/></marker></defs>
  <style>
    text{{font-family:"Microsoft JhengHei","Noto Sans TC",system-ui,sans-serif}} .history-node rect{{fill:#08131e;stroke:#2a4c63}}
    .history-node.status-complete rect{{fill:#0a1f17;stroke:#37d495}} .history-node.status-active rect{{fill:#07231c;stroke:#2bffb5;stroke-width:2}}
    .history-node.status-blocked rect{{fill:#200c13;stroke:#ff4d6a}} .history-kicker{{font-size:10px;fill:#7090a1;letter-spacing:.08em}}
    .history-title{{font-size:15px;fill:#e5f0f3;font-weight:700}} .state-token{{font:11px "Cascadia Code",Consolas,monospace;fill:#7893a1}}
    .causal{{fill:none;stroke:#43c6ff;stroke-width:2}} .title{{font-size:18px;fill:#dcecef;font-weight:800}} .note{{font-size:12px;fill:#688595}}
  </style>
  <rect width="{width}" height="{height}" fill="#05090f"/><text x="28" y="42" class="title">{esc(labels["title"])}</text><text x="28" y="66" class="note">{esc(labels["note"])}</text>
  {''.join(edges)}{nodes}
</svg>'''


def _render_html_zh(state: dict[str, Any], graph_language: str = "zh-TW") -> str:
    objective = state["strategicObjective"]
    briefing = state["plainBriefing"]
    truth = state["currentTruth"]
    decision = state["decision"]
    progress = state["progress"]
    assessment = state["executionAssessment"]
    readiness = state.get("takeoverReadiness") or {}
    intervention = state["intervention"]
    clarity = state["strategicClarity"]
    terminal = state["terminalAssessment"]
    victory_achieved = terminal["status"] == "STRATEGIC_OBJECTIVE_ACHIEVED"
    english_chrome = graph_language == "en"
    advance = state.get("latestVerifiedAdvance")
    main_front = active_front(state)
    risk = progress["culminationRisk"]
    fail_count = progress["sameFailureFingerprintCount"]
    fail_class = "good" if fail_count == 0 else ("warn" if fail_count == 1 else "bad")
    risk_class = {"LOW": "good", "MEDIUM": "warn", "HIGH": "bad"}.get(risk, "warn")
    public_front_rows = "".join(
        "<tr>"
        f"<td><strong>{esc(front['objective'])}</strong></td>"
        f"<td>{esc(human_label(front['effort'], graph_language))} / {esc(human_label(front['operationType'], graph_language))}</td>"
        f"<td><span class='health {esc(front['status'].lower())}'>{esc(human_label(front['status'], graph_language))}</span></td>"
        f"<td>{esc(battlefield_effect(state, front, main_front['id'], graph_language))}</td>"
        "</tr>"
        for front in state["battlefields"]
    )
    technical_front_rows = "".join(
        "<tr>"
        f"<td><code>{esc(front['id'])}</code></td>"
        f"<td>{esc(front['operationType'])}</td>"
        f"<td>{esc(front['effort'])}</td>"
        f"<td>{esc(front['status'])}</td>"
        f"<td>{esc(front['entryState'])} → {esc(front['terminalState'])}</td>"
        f"<td>{esc(', '.join(front['mutationScope']) or '無')}</td>"
        f"<td>{esc(front['recovery']['action'])}</td>"
        "</tr>"
        for front in state["battlefields"]
    )
    observer_rows = "".join(
        "<tr>"
        f"<td>{esc(observer['name'])}</td>"
        f"<td><span class='health {esc(observer['status'].lower())}'>{esc(human_label(observer['status'], graph_language))}</span></td>"
        f"<td>{esc(observer['evidence'])}</td>"
        "</tr>"
        for observer in truth["observerHealth"]
    )
    updated_at = datetime.fromisoformat(state["updatedAt"].replace("Z", "+00:00"))
    observed_claims = sum(1 for claim in truth["evidenceClaims"] if claim_is_observed(claim, updated_at))
    cleanup_open = [debt["residue"] for debt in truth["cleanupDebt"] if debt["status"] == "OPEN"]
    victory_passed = sum(1 for item in objective["victoryCriteria"] if item["status"] == "PASS")
    active_front_count = sum(1 for front in state["battlefields"] if front["status"] == "ACTIVE")
    public_victory_rows = "".join(
        "<tr>"
        f"<td>{esc(item['displayText'])}</td>"
        f"<td><span class='health {esc(item['status'].lower())}'>{esc(human_label(item['status'], graph_language))}</span></td>"
        "</tr>"
        for item in objective["victoryCriteria"]
    )
    technical_victory_rows = "".join(
        "<tr>"
        f"<td><code>{esc(item['id'])}</code></td>"
        f"<td>{esc(item['predicate'])}</td>"
        f"<td><span class='health {esc(item['status'].lower())}'>{esc(human_label(item['status'], graph_language))}</span></td>"
        "</tr>"
        for item in objective["victoryCriteria"]
    )
    candidate_rows = "".join(
        "<tr>"
        f"<td><code>{esc(item['frontId'])}</code></td>"
        f"<td>{'可選' if item['eligible'] else esc(item['ineligibilityReason'])}</td>"
        f"<td>{esc(item['totalScore'])}</td>"
        f"<td>{esc(item['unmetVictoryCriteria'])}</td>"
        "</tr>"
        for item in decision["candidates"]
    )
    latest_html = "尚無已驗證推進"
    if advance:
        latest_html = (
            "<strong>已確認完成一個狀態推進</strong>"
            f"<div class='dim mono'>{esc(advance['at'])}</div>"
            f"<ul>{list_html(advance['evidence'])}</ul>"
        )
    graph_svg = render_battle_map_svg(state, graph_language)
    full_history_svg = render_battle_map_svg(state, graph_language, full_history=True)
    intervention_status = intervention["status"]
    intervention_action = intervention.get("requestedAction") or briefing["userRole"]
    takeover_active = intervention["mode"] == "TACTICAL_TAKEOVER"
    gate_cards = "" if not readiness else "".join(
        f'<article class="gate {gate["status"].lower()}"><div class="gate-status">{esc(human_label(gate["status"], graph_language))}</div>'
        f'<h3>{esc(title)}</h3><p>{esc(description)}</p>{details}</article>'
        for title, description, gate, details in (
            (
                "可操作",
                "人已在正確位置，而且不用自己猜要操作哪一個目標。",
                readiness["operable"],
                f'<ul>{list_html(readiness["operable"]["evidence"])}</ul>',
            ),
            (
                "可執行",
                "目的、權限、步驟、副作用與停止條件都已說清楚。",
                readiness["executable"],
                f'<div class="gate-sub">只做</div><ul>{list_html(readiness["executable"]["steps"])}</ul>'
                f'<div class="gate-sub">不要做</div><ul>{list_html(readiness["executable"]["prohibitedActions"])}</ul>'
                f'<div class="gate-sub">副作用</div><ul>{list_html(readiness["executable"]["sideEffects"])}</ul>'
                f'<div class="gate-sub">停止條件：{esc(readiness["executable"]["stopCondition"])}</div>',
            ),
            (
                "可檢核",
                "操作後有明確世界變化與權威證據，不靠「看起來像成功」。",
                readiness["verifiable"],
                f'<ul>{list_html(readiness["verifiable"]["expectedWorldDelta"])}</ul>'
                f'<div class="gate-sub">檢查來源：{esc("／".join(readiness["verifiable"]["evidenceSources"]))}</div>'
                f'<div class="gate-sub">Deadline：{esc(readiness["verifiable"]["deadlineAt"])}</div>',
            ),
        )
    )
    show_action_gates = (
        takeover_active
        and intervention_status in {"REQUESTED", "IN_PROGRESS"}
        and intervention["phase"] in {"TAKEOVER_REQUESTED", "USER_ACTION_IN_PROGRESS"}
    )
    action_gates_html = (
        '<h3>三道接管門</h3><p class="dim note">只有可操作、可執行、可檢核全部通過，才會顯示戰術接管指令。</p>'
        f'<div class="gates">{gate_cards}</div>'
        if show_action_gates
        else ""
    )
    if victory_achieved:
        copy = (
            {
                "kicker": "STRATEGIC OBJECTIVE SECURED // VICTORY CONFIRMED",
                "title": "Campaign complete",
                "summary": "Every victory criterion is proven, blocking cleanup is closed, and no active main effort remains.",
                "criteria": "victory criteria passed",
                "fronts": "active fronts",
                "cleanup": "open cleanup items",
                "seal": "MISSION COMPLETE",
            }
            if english_chrome
            else {
                "kicker": "STRATEGIC OBJECTIVE SECURED // VICTORY CONFIRMED",
                "title": "戰局完成",
                "summary": "所有勝利條件均已證實，阻擋性清理已關閉，且沒有剩餘主攻。",
                "criteria": "勝利條件已通過",
                "fronts": "活動主攻",
                "cleanup": "未結清項目",
                "seal": "MISSION COMPLETE",
            }
        )
        intervention_html = (
            '<section class="victory-banner" aria-live="polite">'
            '<div class="victory-electric" aria-hidden="true"></div>'
            '<div class="victory-grid"><div class="victory-copy">'
            f'<div class="victory-kicker">{esc(copy["kicker"])}</div>'
            f'<div class="victory-title">{esc(copy["title"])}</div>'
            f'<p class="victory-summary">{esc(copy["summary"])}</p>'
            '<div class="victory-metrics">'
            f'<span><b>{victory_passed}</b>{esc(copy["criteria"])}</span>'
            f'<span><b>{active_front_count}</b>{esc(copy["fronts"])}</span>'
            f'<span><b>{len(cleanup_open)}</b>{esc(copy["cleanup"])}</span>'
            '</div></div>'
            f'<div class="victory-seal" aria-hidden="true"><span>✓</span><strong>{esc(copy["seal"])}</strong></div>'
            '</div></section>'
        )
    elif takeover_active and intervention["phase"] == "BATTLE_DAMAGE_ASSESSMENT":
        intervention_html = (
            '<section class="intervene working" aria-live="polite"><div class="intervene-kicker">BATTLE DAMAGE ASSESSMENT</div>'
            '<div class="intervene-title">正在評估戰果</div>'
            '<div class="intervene-action">使用者操作已完成；正在由 Agent 以 UI／API／DB 評估戰果，尚未宣告成功。</div>'
            f'<div class="intervene-reason">{esc(intervention.get("returnOfControl", ""))}</div></section>'
        )
    elif takeover_active and intervention_status in {"REQUESTED", "IN_PROGRESS"}:
        intervention_html = (
            '<section class="intervene requested" aria-live="assertive">'
            '<div class="intervene-kicker">TACTICAL TAKEOVER // ONE EXACT ACTION</div>'
            '<div class="intervene-title">戰術接管：只做這一動</div>'
            f'<div class="takeover-grid"><div><b>為什麼需要你</b><p>{esc(intervention.get("reason", ""))}</p></div>'
            f'<div><b>請執行</b><p class="intervene-action">{esc(intervention_action)}</p></div>'
            f'<div><b>不要做</b><ul>{list_html(readiness["executable"]["prohibitedActions"])}</ul></div>'
            f'<div><b>預期改變</b><ul>{list_html(readiness["verifiable"]["expectedWorldDelta"])}</ul></div></div>'
            f'<div class="intervene-return"><b>交回控制</b>{esc(intervention.get("returnOfControl", ""))}</div></section>'
        )
    elif intervention_status == "REQUESTED":
        return_of_control = intervention.get("returnOfControl", "")
        return_html = (
            f'<div class="intervene-return"><b>交回控制</b>{esc(return_of_control)}</div>' if return_of_control else ""
        )
        intervention_html = (
            '<section class="intervene requested" aria-live="assertive">'
            '<div class="intervene-kicker">INTERVENTION REQUIRED</div>'
            '<div class="intervene-title">需要你介入</div>'
            f'<div class="intervene-action">{esc(intervention_action)}</div>'
            f'<div class="intervene-reason">{esc(intervention.get("reason", ""))}</div>{return_html}</section>'
        )
    else:
        dot_class = {"IN_PROGRESS": "working", "AVAILABLE": "standby"}.get(intervention_status, "idle")
        intervention_html = (
            f'<section class="intervene {dot_class}"><span class="dot"></span>'
            f'<strong>介入狀態：{esc(human_label(intervention_status, graph_language))}</strong>'
            f'<span>{esc(intervention_action)}</span>'
            f'<span class="dim">{esc(intervention.get("reason", ""))}</span></section>'
        )
    body_tag = '<body class="victory-achieved">' if victory_achieved else "<body>"
    refresh_meta = "" if victory_achieved else '<meta http-equiv="refresh" content="15">'
    if victory_achieved and english_chrome:
        document_title = f"Campaign complete | {state['missionId']}"
        hud_eyebrow = "CAMPAIGN COMPLETE // VICTORY CONFIRMED"
        hud_title = "Strategic Advance Sand Table"
        hud_sub = "The objective is secured, the evidence is closed, and the campaign board is sealed"
        hud_refresh = "BOARD SEALED"
        sitrep_step4_title = "Effects secured"
        sitrep_step4_text = "All victory criteria and blocking cleanup have been closed by authoritative evidence."
        sitrep_step5_title = "Your role"
        sitrep_step5_text = "No intervention is required; the campaign is complete."
        sealed_label = "Campaign sealed"
        sealed_at_label = "Sealed"
        sealed_separator = ":"
        active_label = "Active main efforts"
    elif victory_achieved:
        document_title = f"戰局完成｜{state['missionId']}"
        hud_eyebrow = "CAMPAIGN COMPLETE // VICTORY CONFIRMED"
        hud_title = "戰略推進沙盤"
        hud_sub = "戰略目標已達成，權威證據已封閉，戰局正式封盤"
        hud_refresh = "BOARD SEALED"
        sitrep_step4_title = "戰果已鞏固"
        sitrep_step4_text = "所有勝利條件與阻擋性清理都已由權威證據封閉。"
        sitrep_step5_title = "你現在要做什麼"
        sitrep_step5_text = "不需介入；戰局已完成並封盤。"
        sealed_label = "戰局已封盤"
        sealed_at_label = "封盤"
        sealed_separator = "："
        active_label = "活動主攻"
    else:
        document_title = f"戰略推進沙盤｜{state['missionId']}"
        hud_eyebrow = "STRATEGIC ADVANCE // LIVE SAND TABLE"
        hud_title = "戰略推進沙盤"
        hud_sub = "目前戰局的共同畫面：看這一頁就知道現在在哪、下一步要改變什麼"
        hud_refresh = "AUTO-REFRESH 15S"
        sitrep_step4_title = "下一動要改變什麼"
        sitrep_step4_text = briefing["nextMove"]
        sitrep_step5_title = "你現在要做什麼"
        sitrep_step5_text = briefing["userRole"]
        sealed_label = ""
        sealed_at_label = ""
        sealed_separator = ""
        active_label = ""
    if victory_achieved:
        telemetry_html = (
            '<div class="tile"><div class="tile-v good">SEALED</div>'
            f'<div class="tile-l">{esc(sealed_label)}<br>{esc(sealed_at_label)}{esc(sealed_separator)}{esc(state["updatedAt"])}</div></div>'
            '<div class="tile"><div class="tile-v good">0<span>MAIN</span></div>'
            f'<div class="tile-l">{esc(active_label)}</div></div>'
            f'<div class="tile"><div class="tile-v {fail_class}">{esc(fail_count)}</div><div class="tile-l">同類失敗指紋次數（滿 2 次斷路）</div></div>'
            f'<div class="tile"><div class="tile-v {risk_class}">{esc(human_label(risk, graph_language))}</div><div class="tile-l">作戰頂點風險</div></div>'
        )
    else:
        telemetry_html = (
            f'<div class="tile"><div class="tile-v" id="active-front-elapsed" data-at="{esc(progress["activeFrontStartedAt"])}">—</div><div class="tile-l">主攻已投入時間<br>起算：{esc(progress["activeFrontStartedAt"])}</div></div>'
            f'<div class="tile"><div class="tile-v" id="since-change" data-at="{esc(progress["lastWorldStateChangeAt"])}">—</div><div class="tile-l">距上次世界狀態變化<br>基準：{esc(progress["lastWorldStateChangeAt"])}</div></div>'
            f'<div class="tile"><div class="tile-v {fail_class}">{esc(fail_count)}</div><div class="tile-l">同類失敗指紋次數（滿 2 次斷路）</div></div>'
            f'<div class="tile"><div class="tile-v {risk_class}">{esc(human_label(risk, graph_language))}</div><div class="tile-l">作戰頂點風險</div></div>'
        )
    return f"""<!doctype html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  {refresh_meta}
  <title>{esc(document_title)}</title>
  <style>
    :root{{--void:#04070b;--panel:#0a121b;--line:#16293c;--edge:#25455c;--ink:#d8e7ec;--dim:#6d8a99;
      --pri:#2bffb5;--cyan:#43c6ff;--amber:#ffb043;--red:#ff4d6a;
      --mono:"Cascadia Code",Consolas,ui-monospace,"Courier New",monospace;
      --zh:"Microsoft JhengHei","Noto Sans TC",system-ui,sans-serif}}
    *{{box-sizing:border-box}}
    body{{margin:0;color:var(--ink);font:15px/1.65 var(--zh);
      background:radial-gradient(1100px 520px at 72% -12%,rgba(43,255,181,.05),transparent 60%),
      radial-gradient(900px 460px at 8% 112%,rgba(67,198,255,.045),transparent 60%),var(--void)}}
    body::before{{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;
      background:repeating-linear-gradient(0deg,transparent 0 39px,rgba(110,190,255,.028) 39px 40px),
      repeating-linear-gradient(90deg,transparent 0 39px,rgba(110,190,255,.028) 39px 40px)}}
    main{{position:relative;z-index:1;max-width:1240px;margin:auto;padding:26px 28px 48px}}
    .mono{{font-family:var(--mono)}} .dim{{color:var(--dim)}} :focus-visible{{outline:2px solid var(--pri);outline-offset:2px}}
    h1{{margin:2px 0 0;font-size:27px;font-weight:900;letter-spacing:.3em}}
    .sub{{color:var(--dim);font-size:13px;margin-top:7px;letter-spacing:.06em}}
    h2{{display:flex;align-items:baseline;gap:10px;margin:0 0 14px;font-size:17px;letter-spacing:.14em}}
    h2::before{{content:"◢";color:var(--pri);font-size:11px}}
    h2 .en{{font:700 11px var(--mono);letter-spacing:.3em;color:var(--dim)}}
    h3{{font-size:14px;margin:0 0 6px;color:#c2d7df;letter-spacing:.08em}}
    .eyebrow{{font:700 10px var(--mono);letter-spacing:.34em;color:var(--dim)}}
    .hud{{position:relative;display:flex;justify-content:space-between;align-items:flex-start;gap:18px;
      border:1px solid var(--line);background:linear-gradient(180deg,#0c1624,#08101a);padding:18px 22px;margin-bottom:14px}}
    .hud-right{{text-align:right}}
    .hud-meta{{font:12px/1.8 var(--mono);color:var(--dim)}}
    .lamp{{display:inline-flex;align-items:center;gap:8px;font:700 12px var(--mono);letter-spacing:.14em;border:1px solid var(--line);padding:6px 12px;margin-bottom:10px}}
    .lamp i{{width:9px;height:9px;border-radius:50%}}
    .risk-low i{{background:var(--pri);box-shadow:0 0 8px var(--pri)}}
    .risk-medium i{{background:var(--amber);box-shadow:0 0 8px var(--amber)}}
    .risk-high i{{background:var(--red);box-shadow:0 0 8px var(--red)}}
    .hud::before,.hud::after,.card::before,.card::after{{content:"";position:absolute;width:14px;height:14px;pointer-events:none}}
    .hud::before,.card::before{{top:-1px;left:-1px;border-top:2px solid var(--edge);border-left:2px solid var(--edge)}}
    .hud::after,.card::after{{bottom:-1px;right:-1px;border-bottom:2px solid var(--edge);border-right:2px solid var(--edge)}}
    .grid{{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:14px;min-width:0}}
    .card{{position:relative;grid-column:span 6;min-width:0;border:1px solid var(--line);padding:20px;
      background:linear-gradient(180deg,rgba(13,24,38,.92),rgba(8,16,26,.96))}}
    .wide{{grid-column:span 12}}
    .hero{{border-color:#2b4a41}} .hero::before,.hero::after{{border-color:#2f6a55}}
    .purpose{{font-size:21px;font-weight:800;margin:2px 0 12px;letter-spacing:.03em}}
    ul.check{{list-style:none;margin:6px 0 0;padding:0;display:grid;gap:6px}}
    ul.check li{{padding-left:26px;position:relative}}
    ul.check li::before{{content:"▢";position:absolute;left:2px;color:var(--pri);font-family:var(--mono)}}
    .intervene{{position:relative;display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 14px;border:1px solid var(--line);background:#0a141f;padding:12px 18px;margin-bottom:14px;font-size:14px}}
    .intervene .dot{{width:8px;height:8px;border-radius:50%;background:#3a4d5a;align-self:center}}
    .intervene.standby .dot{{background:var(--cyan);box-shadow:0 0 7px var(--cyan)}}
    .intervene.working{{border-color:#6b4c17}} .intervene.working .dot{{background:var(--amber);box-shadow:0 0 7px var(--amber)}}
    .intervene.requested{{display:block;border-color:var(--red);background:linear-gradient(180deg,#2a0d16,#170810);padding:20px 22px}}
    .intervene-kicker{{font:700 11px var(--mono);letter-spacing:.3em;color:var(--red)}}
    .intervene-title{{font-size:24px;font-weight:900;letter-spacing:.22em;color:#ffd7de;margin:8px 0 6px}}
    .intervene-action{{font-size:16px;margin:2px 0 6px}}
    .intervene-reason{{font-size:13px;color:var(--dim)}}
    .intervene-return{{margin-top:14px;padding:10px 12px;border-left:3px solid var(--amber);background:#160c08}}
    .intervene-return b{{color:var(--amber);margin-right:10px}}
    .takeover-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}}
    .takeover-grid>div{{border:1px solid #59202d;background:#12080d;padding:12px 14px}}
    .takeover-grid b{{color:#ffd7de}} .takeover-grid p{{margin:5px 0}} .takeover-grid ul{{margin-top:5px}}
    body.victory-achieved{{background:
      radial-gradient(900px 520px at 50% -8%,rgba(255,211,110,.12),transparent 64%),
      radial-gradient(1200px 620px at 78% 8%,rgba(43,255,181,.11),transparent 65%),var(--void)}}
    .victory-achieved .hud{{border-color:#355f4b;background:linear-gradient(180deg,#0d201b,#08140f)}}
    .victory-achieved .hud::before,.victory-achieved .hud::after{{border-color:#6fffc4}}
    .victory-achieved .hero{{border-color:#496a3f;box-shadow:inset 0 1px 0 rgba(255,211,110,.12)}}
    .victory-banner{{position:relative;isolation:isolate;overflow:hidden;border:1px solid #78e8b5;
      background:linear-gradient(122deg,rgba(8,42,31,.98),rgba(12,30,27,.96) 58%,rgba(49,38,9,.96));
      box-shadow:0 0 0 1px rgba(255,211,110,.12),0 20px 65px rgba(0,0,0,.42),0 0 42px rgba(43,255,181,.12);
      padding:28px 30px;margin-bottom:14px}}
    .victory-banner::before{{content:"";position:absolute;z-index:-1;inset:-45% auto -45% -35%;width:36%;
      background:linear-gradient(90deg,transparent,rgba(171,255,218,.18),transparent);transform:skewX(-18deg)}}
    .victory-banner::after{{content:"";position:absolute;z-index:-2;inset:0;opacity:.38;
      background:repeating-linear-gradient(0deg,transparent 0 7px,rgba(106,255,193,.035) 7px 8px)}}
    .victory-electric{{position:absolute;z-index:2;inset:0;overflow:hidden;pointer-events:none}}
    .victory-electric::before,.victory-electric::after{{content:"";position:absolute;width:32%;height:2px;opacity:0;
      background:linear-gradient(90deg,transparent,#dffff3 34%,#58ffc1 52%,#9ddcff 68%,transparent);
      box-shadow:0 0 4px #ecfff8,0 0 11px #2bffb5,0 0 22px rgba(67,198,255,.8)}}
    .victory-electric::before{{top:0;left:-34%}}
    .victory-electric::after{{right:-34%;bottom:0;transform:rotate(180deg)}}
    .victory-grid{{display:grid;grid-template-columns:minmax(0,1fr) 154px;align-items:center;gap:30px}}
    .victory-kicker{{font:800 11px var(--mono);letter-spacing:.29em;color:#ffd36e}}
    .victory-title{{font-size:clamp(38px,6vw,68px);line-height:1.05;font-weight:950;letter-spacing:.16em;
      color:#edfff7;text-shadow:0 0 24px rgba(43,255,181,.28);margin:10px 0 12px}}
    .victory-summary{{max-width:760px;margin:0;color:#b9d8ce;font-size:16px}}
    .victory-metrics{{display:flex;flex-wrap:wrap;gap:9px;margin-top:18px}}
    .victory-metrics span{{display:inline-flex;align-items:baseline;gap:8px;border:1px solid #315c4b;
      background:rgba(4,14,12,.55);padding:7px 11px;color:#88aa9e;font:700 11px var(--mono);letter-spacing:.08em}}
    .victory-metrics b{{color:#7fffc8;font-size:18px}}
    .victory-seal{{position:relative;width:146px;height:146px;border:1px solid #ffd36e;border-radius:50%;
      display:grid;place-content:center;text-align:center;color:#ffd36e;box-shadow:0 0 0 8px rgba(255,211,110,.045),inset 0 0 28px rgba(255,211,110,.08)}}
    .victory-seal::before,.victory-seal::after{{content:"";position:absolute;inset:13px;border:1px solid rgba(111,255,196,.36);border-radius:50%}}
    .victory-seal::after{{inset:-11px;border-color:rgba(111,255,196,.2);clip-path:polygon(0 43%,100% 43%,100% 57%,0 57%)}}
    .victory-seal span{{font:900 42px/1 var(--mono);color:#79ffc7;text-shadow:0 0 18px rgba(43,255,181,.5)}}
    .victory-seal strong{{display:block;width:100px;margin:9px auto 0;font:800 10px/1.45 var(--mono);letter-spacing:.22em}}
    @media (prefers-reduced-motion:no-preference){{
      .intervene.requested{{animation:alarm 1.6s ease-in-out infinite}}
      .victory-banner{{animation:victory-enter .7s cubic-bezier(.2,.8,.2,1) both}}
      .victory-banner::before{{animation:victory-sweep 1.15s ease-out .12s 1 both}}
      .victory-seal{{animation:victory-seal .82s cubic-bezier(.2,.9,.2,1) .12s both}}
      .victory-seal::after{{animation:electric-ring .9s steps(5,end) .28s 1 both}}
      .victory-title{{animation:electric-title .9s steps(5,end) .2s 1 both}}
      .victory-electric::before{{animation:electric-top 1.05s steps(7,end) .18s 1 both}}
      .victory-electric::after{{animation:electric-bottom 1.05s steps(7,end) .32s 1 both}}
      @keyframes alarm{{0%,100%{{box-shadow:0 0 0 0 rgba(255,77,106,0)}}50%{{box-shadow:0 0 26px 0 rgba(255,77,106,.35)}}}}
      @keyframes victory-enter{{from{{opacity:0;transform:translateY(-9px);filter:saturate(.55)}}to{{opacity:1;transform:none;filter:saturate(1)}}}}
      @keyframes victory-sweep{{from{{transform:translateX(-25%) skewX(-18deg);opacity:0}}35%{{opacity:1}}to{{transform:translateX(460%) skewX(-18deg);opacity:0}}}}
      @keyframes victory-seal{{from{{opacity:0;transform:scale(.72) rotate(-8deg)}}to{{opacity:1;transform:scale(1) rotate(0)}}}}
      @keyframes electric-top{{0%{{left:-34%;opacity:0}}10%,28%,48%,72%{{opacity:1}}18%,38%,60%{{opacity:.25}}100%{{left:102%;opacity:0}}}}
      @keyframes electric-bottom{{0%{{right:-34%;opacity:0}}12%,32%,56%,78%{{opacity:1}}22%,44%,68%{{opacity:.2}}100%{{right:102%;opacity:0}}}}
      @keyframes electric-ring{{0%{{box-shadow:none;opacity:.1}}28%{{box-shadow:0 0 10px #dffff3,0 0 26px #2bffb5;opacity:1}}44%{{box-shadow:none;opacity:.25}}68%{{box-shadow:0 0 8px #9ddcff,0 0 20px #2bffb5;opacity:.9}}100%{{box-shadow:none;opacity:1}}}}
      @keyframes electric-title{{0%,100%{{text-shadow:0 0 24px rgba(43,255,181,.28)}}24%,56%{{text-shadow:0 0 5px #f0fff9,0 0 18px #2bffb5,0 0 34px rgba(67,198,255,.7)}}36%,72%{{text-shadow:0 0 11px rgba(43,255,181,.4)}}}}
    }}
    ol.steps{{list-style:none;margin:0;padding:0}}
    .steps li{{display:grid;grid-template-columns:46px 1fr;gap:14px;padding:12px 0 14px}}
    .steps li+li{{border-top:1px dashed #142433}}
    .steps .num{{font:800 15px var(--mono);color:#41586a;padding-top:2px}}
    .steps li.next .num,.steps li.next h3{{color:var(--pri)}}
    .steps li.user .num,.steps li.user h3{{color:var(--amber)}}
    .steps p{{margin:0}}
    .gates{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}}
    .gate{{position:relative;border:1px solid var(--line);background:#08131e;padding:16px}}
    .gate.pass{{border-color:#1d5c46}} .gate.fail{{border-color:#6b2331}} .gate.unknown{{border-color:#6b4c17}}
    .gate-status{{position:absolute;right:12px;top:12px;font:700 10px var(--mono);letter-spacing:.12em}}
    .gate.pass .gate-status{{color:var(--pri)}} .gate.fail .gate-status{{color:var(--red)}} .gate.unknown .gate-status{{color:var(--amber)}}
    .gate h3{{font-size:17px;margin-right:70px}} .gate p{{color:var(--dim);margin:0 0 8px}}
    .gate-sub{{font:700 11px var(--mono);color:var(--cyan);letter-spacing:.12em;margin-top:9px}}
    .note{{margin:0 0 12px;font-size:13px}}
    .map-wrap{{border:1px solid var(--line);background:#05090f;overflow:auto}}
    .map-wrap svg{{display:block;width:100%;height:auto;min-width:860px}}
    details.history{{margin-top:12px;border:1px solid var(--line);background:#07101a}}
    details.history>summary{{cursor:pointer;padding:11px 14px;color:var(--cyan);font:700 12px var(--mono);letter-spacing:.12em}}
    details.history[open]>summary{{border-bottom:1px solid var(--line)}}
    .full-history{{border:0;max-height:72vh}}
    table{{width:100%;border-collapse:collapse;font-size:14px}}
    th{{font:700 11px var(--mono);letter-spacing:.18em;color:var(--dim);text-align:left;padding:8px 10px;border-bottom:1px solid var(--edge)}}
    td{{padding:10px;border-bottom:1px solid var(--line);vertical-align:top}}
    tbody tr:hover{{background:rgba(67,198,255,.05)}}
    .table-scroll{{display:block;width:100%;max-width:100%;min-width:0;overflow-x:auto;border:1px solid var(--line)}}
    .table-scroll table{{border-collapse:collapse}}
    .front-contract-table{{width:1180px;max-width:none;table-layout:fixed}}
    .front-contract-table th,.front-contract-table td{{overflow-wrap:anywhere;word-break:break-word}}
    .front-contract-table code{{overflow-wrap:break-word;word-break:normal}}
    .front-contract-table th:nth-child(1){{width:17%}}
    .front-contract-table th:nth-child(2){{width:8%}}
    .front-contract-table th:nth-child(3){{width:8%}}
    .front-contract-table th:nth-child(4){{width:9%}}
    .front-contract-table th:nth-child(5){{width:21%}}
    .front-contract-table th:nth-child(6){{width:15%}}
    .front-contract-table th:nth-child(7){{width:22%}}
    .health,.pill{{display:inline-flex;align-items:center;gap:6px;padding:2px 9px;font:700 11px var(--mono);letter-spacing:.12em;border:1px solid;background:#0a141f;white-space:nowrap}}
    .health::before{{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}}
    .active,.healthy,.complete,.low,.main{{color:var(--pri);border-color:#1d5c46}}
    .pending,.deferred,.unknown,.support{{color:#8fa9b8;border-color:#2c4356}}
    .degraded,.medium{{color:var(--amber);border-color:#6b4c17}}
    .failed,.blocked,.high{{color:var(--red);border-color:#6b2331}}
    .tiles{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}
    .tile{{border:1px solid var(--line);background:#0a1420;padding:12px 14px}}
    .tile-v{{font:800 22px/1.3 var(--mono);color:var(--ink)}}
    .tile-v span{{font-size:11px;color:var(--dim);margin-left:5px;letter-spacing:.15em}}
    .tile-l{{font-size:12px;color:var(--dim);margin-top:3px}}
    .tile-v.good{{color:var(--pri)}} .tile-v.warn{{color:var(--amber)}} .tile-v.bad{{color:var(--red)}}
    .kv{{display:grid;grid-template-columns:150px 1fr;gap:7px 14px}} .kv b{{color:var(--dim);font-weight:600}}
    code{{font-family:var(--mono);color:#9fdcff;font-size:13px}}
    pre{{white-space:pre-wrap;word-break:break-word;background:#060d15;border:1px solid var(--line);padding:12px;color:#cfe4f4;font:13px/1.6 var(--mono)}}
    ul{{margin:8px 0 0;padding-left:20px}}
    details.technical{{padding:0}}
    details.technical>summary{{cursor:pointer;padding:18px 20px;font:700 13px var(--mono);letter-spacing:.22em;color:var(--cyan);list-style:none}}
    details.technical>summary::-webkit-details-marker{{display:none}}
    details.technical>summary::before{{content:"▸ "}} details.technical[open]>summary::before{{content:"▾ "}}
    details.technical[open]>summary{{border-bottom:1px solid var(--line)}}
    .technical-body{{min-width:0;padding:20px}}
    .technical-body>h3{{margin:18px 0 10px}}
    .tech-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}
    .tech-block{{background:#0a1420;border:1px solid var(--line);padding:14px;overflow:auto}}
    @media(max-width:820px){{.card{{grid-column:span 12}}.hud{{display:block}}.hud-right{{text-align:left;margin-top:12px}}
      .victory-banner{{padding:22px 20px}}.victory-grid{{grid-template-columns:1fr;gap:20px}}.victory-seal{{width:118px;height:118px;justify-self:start}}
      .victory-title{{letter-spacing:.08em}}.hud>div,.technical-body,.tech-grid,.tech-block{{min-width:0}}
      .card>table,.technical-body>table{{table-layout:fixed}}th,td{{overflow-wrap:anywhere;word-break:break-word}}
      .kv{{grid-template-columns:1fr}}.tech-grid,.tiles,.gates,.takeover-grid{{grid-template-columns:1fr}}.steps li{{grid-template-columns:34px 1fr}}}}
  </style>
</head>
{body_tag}<main>
  <header class="hud">
    <div>
      <div class="eyebrow">{esc(hud_eyebrow)}</div>
      <h1>{esc(hud_title)}</h1>
      <div class="sub">{esc(hud_sub)}</div>
    </div>
    <div class="hud-right">
      <div class="lamp risk-{risk.lower()}"><i></i>頂點風險：{esc(human_label(risk, graph_language))}</div>
      <div class="lamp risk-{'low' if clarity['status'] == 'CLEAR' else 'high'}"><i></i>{esc(human_label(clarity['status'], graph_language))} / {esc(human_label(clarity['route'], graph_language))}</div>
      <div class="hud-meta">MISSION://{esc(state['missionId'])}<br>UPDATED {esc(state['updatedAt'])}<br>TERMINAL {esc(terminal['status'])}<br>{esc(hud_refresh)}</div>
    </div>
  </header>
  {intervention_html}
  <div class="grid">
    <section class="card wide hero"><h2><span class="en">OBJECTIVE</span>戰略目標</h2>
      <p class="purpose">{esc(objective['purpose'])}</p>
      <div class="dim">完成的樣子</div><ul class="check">{list_html(objective['desiredEndState'])}</ul>
      <h3>什麼時候才算完成</h3><table><thead><tr><th>完成條件</th><th>目前狀態</th></tr></thead><tbody>{public_victory_rows}</tbody></table></section>
    <section class="card wide"><h2><span class="en">SITREP</span>白話戰情簡報</h2><ol class="steps">
      <li><span class="num">01</span><div><h3>先說背景</h3><p>{esc(briefing['context'])}</p></div></li>
      <li><span class="num">02</span><div><h3>現在在哪</h3><p>{esc(briefing['currentSituation'])}</p></div></li>
      <li><span class="num">03</span><div><h3>為什麼這樣判斷</h3><p>{esc(briefing['reasoning'])}</p></div></li>
      <li class="next"><span class="num">04</span><div><h3>{esc(sitrep_step4_title)}</h3><p>{esc(sitrep_step4_text)}</p></div></li>
      <li class="user"><span class="num">05</span><div><h3>{esc(sitrep_step5_title)}</h3><p>{esc(sitrep_step5_text)}</p></div></li>
    </ol></section>
    <section class="card wide"><h2><span class="en">TACMAP</span>戰局圖</h2>
      <div class="map-wrap">{graph_svg}</div>
      <details class="history"><summary>展開完整歷史</summary><div class="map-wrap full-history">{full_history_svg}</div></details></section>
    <section class="card wide"><h2><span class="en">FRONTS</span>戰場分割</h2>
      <table><thead><tr><th>要解決什麼</th><th>在戰局中的角色</th><th>目前狀態</th><th>對主攻的作用</th></tr></thead><tbody>{public_front_rows}</tbody></table></section>
    <section class="card"><h2><span class="en">LAST ADVANCE</span>最近推進</h2>{latest_html}</section>
    <section class="card"><h2><span class="en">TELEMETRY</span>作戰節奏</h2><div class="tiles">{telemetry_html}</div></section>
    <details class="card wide technical" open><summary>TECHNICAL // 技術細節（預設展開）</summary><div class="technical-body">
      <div class="tech-grid">
        <section class="tech-block"><h3>原始世界狀態</h3><pre>{esc(json.dumps(truth['worldState'], ensure_ascii=False, indent=2))}</pre><div class="kv"><b>有效 claims</b><span>{observed_claims}／{len(truth['evidenceClaims'])}</span><b>Open cleanup</b><span>{esc(', '.join(cleanup_open) or '無')}</span></div></section>
        <section class="tech-block"><h3>決策契約</h3><div class="kv"><b>Mission ID</b><code>{esc(state['missionId'])}</code><b>Active front ID</b><code>{esc(decision['activeFrontId'])}</code><b>清晰度</b><span>{esc(clarity['status'])}／{esc(clarity['route'])}</span><b>戰術</b><span>{esc(decision['chosenTactic'])}</span><b>Contribution</b><code>{esc(decision['contribution'])}</code><b>Pivot</b><span>{esc(decision['pivotCondition'])}</span><b>最近狀態轉換</b><code>{esc(f"{advance['from']} → {advance['to']}" if advance else '尚無')}</code><b>終局</b><span>{esc(terminal['status'])}</span><b>理由</b><span>{esc(decision['rationale'])}</span></div></section>
        <section class="tech-block"><h3>觀測器健康與證據</h3><table><thead><tr><th>Observer</th><th>狀態</th><th>證據</th></tr></thead><tbody>{observer_rows}</tbody></table></section>
        <section class="tech-block"><h3>作戰承載</h3><div class="kv"><b>最後世界變化</b><span>{esc(progress['lastWorldStateChangeAt'])}</span><b>同類失敗次數</b><span>{esc(progress['sameFailureFingerprintCount'])}</span><b>主攻起算</b><span>{esc(progress['activeFrontStartedAt'])}</span><b>頂點風險</b><span>{esc(progress['culminationRisk'])}</span></div></section>
        <section class="tech-block"><h3>執行器評估</h3><pre>{esc(json.dumps(assessment, ensure_ascii=False, indent=2))}</pre></section>
      </div>
      {action_gates_html}
      <h3>勝利條件機器判斷式</h3><table><thead><tr><th>ID</th><th>Predicate</th><th>狀態</th></tr></thead><tbody>{technical_victory_rows}</tbody></table>
      <h3>戰場技術契約</h3><div class="table-scroll"><table class="front-contract-table"><thead><tr><th>ID</th><th>類型</th><th>Effort</th><th>狀態</th><th>狀態轉換</th><th>Mutation</th><th>Recovery</th></tr></thead><tbody>{technical_front_rows}</tbody></table></div>
      <h3>候選主攻的固定評分</h3><table><thead><tr><th>Front</th><th>Eligibility</th><th>Total score</th><th>未滿足勝利條件</th></tr></thead><tbody>{candidate_rows}</tbody></table>
      <div class="tech-grid"><section class="tech-block"><h3>勝利證據</h3><ul>{list_html(objective['victoryEvidence'])}</ul></section><section class="tech-block"><h3>硬限制／不可接受結果</h3><ul>{list_html(objective['constraints'] + objective['unacceptableOutcomes'])}</ul></section></div>
    </div></details>
  </div>
</main>
<script>
(function(){{
  var historyDetails = document.querySelector("details.history");
  try {{
    var historyKey = "strategic-advance:full-history:" + window.location.pathname;
    if (historyDetails && window.localStorage.getItem(historyKey) === "open") historyDetails.open = true;
    if (historyDetails) historyDetails.addEventListener("toggle", function() {{
      window.localStorage.setItem(historyKey, historyDetails.open ? "open" : "closed");
    }});
  }} catch (error) {{ /* file URLs or privacy settings may disable localStorage. */ }}
  function renderElapsed(element, suffix) {{
    if (!element) return;
    var at = Date.parse(element.getAttribute("data-at") || "");
    if (isNaN(at)) {{ element.textContent = "未知"; return; }}
    var minutes = Math.max(0, Math.floor((Date.now() - at) / 60000));
    element.innerHTML = minutes + "<span>MIN" + suffix + "</span>";
  }}
  function updateElapsed() {{
    renderElapsed(document.getElementById("active-front-elapsed"), "");
    renderElapsed(document.getElementById("since-change"), " 前");
  }}
  updateElapsed();
  window.setInterval(updateElapsed, 60000);
}})();
</script>
</body></html>"""


HTML_EN_REPLACEMENTS = (
    ('<html lang="zh-TW">', '<html lang="en">'),
    ("戰略推進沙盤｜", "Strategic Advance Sand Table | "),
    ("<h1>戰略推進沙盤</h1>", "<h1>Strategic Advance Sand Table</h1>"),
    ("目前戰局的共同畫面：看這一頁就知道現在在哪、下一步要改變什麼", "Shared operating picture: see where the campaign stands and what changes next"),
    ("頂點風險：", "Culmination risk: "),
    ("戰略目標</h2>", "Strategic objective</h2>"),
    (">完成的樣子<", ">Desired end state<"),
    (">什麼時候才算完成<", ">Completion criteria<"),
    (">完成條件<", ">Criterion<"),
    (">目前狀態<", ">Current status<"),
    ("白話戰情簡報</h2>", "Situation report</h2>"),
    (">先說背景<", ">Context<"),
    (">現在在哪<", ">Now<"),
    (">為什麼這樣判斷<", ">Judgment<"),
    (">下一動要改變什麼<", ">Next move and expected change<"),
    (">你現在要做什麼<", ">Your role<"),
    ("戰局圖</h2>", "Battle map</h2>"),
    (">展開完整歷史<", ">Expand full history<"),
    ("戰場分割</h2>", "Fronts</h2>"),
    (">要解決什麼<", ">Objective<"),
    (">在戰局中的角色<", ">Role<"),
    (">對主攻的作用<", ">Contribution<"),
    ("最近推進</h2>", "Latest advance</h2>"),
    ("已確認完成一個狀態推進", "One state transition verified"),
    ("尚無已驗證推進", "No verified advance yet"),
    ("作戰節奏</h2>", "Operational tempo</h2>"),
    ("主攻已投入時間", "Time on active front"),
    ("距上次世界狀態變化", "Time since world-state change"),
    ("同類失敗指紋次數（滿 2 次斷路）", "Repeated failure fingerprint count (circuit opens at 2)"),
    ("作戰頂點風險", "Culmination risk"),
    ("起算：", "Started: "),
    ("基準：", "Baseline: "),
    ("TECHNICAL // 技術細節（預設展開）", "TECHNICAL // Details (open by default)"),
    (">原始世界狀態<", ">Raw world state<"),
    ("有效 claims", "Valid claims"),
    (">決策契約<", ">Decision contract<"),
    ("清晰度", "Clarity"),
    (">戰術<", ">Tactic<"),
    ("最近狀態轉換", "Latest transition"),
    ("終局", "Terminal"),
    ("理由", "Rationale"),
    ("觀測器健康與證據", "Observer health and evidence"),
    (">狀態<", ">Status<"),
    (">證據<", ">Evidence<"),
    ("作戰承載", "Operational capacity"),
    ("最後世界變化", "Latest world-state change"),
    ("同類失敗次數", "Repeated failure count"),
    ("主攻起算", "Active front started"),
    ("頂點風險", "Culmination risk"),
    ("執行器評估", "Actuator assessment"),
    ("三道接管門", "Three takeover gates"),
    ("只有可操作、可執行、可檢核全部通過，才會顯示戰術接管指令。", "The tactical-takeover instruction appears only after operable, executable, and verifiable all pass."),
    (">可操作<", ">Operable<"),
    ("人已在正確位置，而且不用自己猜要操作哪一個目標。", "The actor is in the correct place and the target is unambiguous."),
    (">可執行<", ">Executable<"),
    ("目的、權限、步驟、副作用與停止條件都已說清楚。", "Purpose, authority, steps, side effects, and stop conditions are explicit."),
    (">只做<", ">Do only<"),
    (">不要做<", ">Do not<"),
    (">副作用<", ">Side effects<"),
    ("停止條件：", "Stop condition: "),
    (">可檢核<", ">Verifiable<"),
    ("操作後有明確世界變化與權威證據，不靠「看起來像成功」。", "A defined world-state delta and authoritative evidence distinguish success from appearance."),
    ("檢查來源：", "Evidence sources: "),
    ("戰術接管：只做這一動", "Tactical takeover: one exact action"),
    (">為什麼需要你<", ">Why you are needed<"),
    (">請執行<", ">Do this<"),
    (">預期改變<", ">Expected change<"),
    ("交回控制", "Return control"),
    ("正在評估戰果", "Assessing effects"),
    ("使用者操作已完成；正在由 Agent 以 UI／API／DB 評估戰果，尚未宣告成功。", "The user action is complete; the agent is assessing effects through UI/API/DB evidence and has not declared success."),
    ("需要你介入", "Intervention required"),
    ("介入狀態：", "Intervention: "),
    ("勝利條件機器判斷式", "Machine victory predicates"),
    ("戰場技術契約", "Front contracts"),
    (">類型<", ">Type<"),
    (">狀態轉換<", ">Transition<"),
    ("候選主攻的固定評分", "Fixed candidate scoring"),
    ("未滿足勝利條件", "Unmet victory criteria"),
    ("勝利證據", "Victory evidence"),
    ("硬限制／不可接受結果", "Constraints / unacceptable outcomes"),
    (">可選<", ">Eligible<"),
    (">尚無<", ">None yet<"),
    (">無<", ">None<"),
    ('element.textContent = "未知"', 'element.textContent = "Unknown"'),
    ('" 前"', '" ago"'),
)


def render_html(state: dict[str, Any], language: str = "zh-TW") -> str:
    language = normalize_language(language)
    document = _render_html_zh(state, graph_language=language)
    if language != "en":
        return document
    for source, target in HTML_EN_REPLACEMENTS:
        document = document.replace(source, target)
    # Enum labels are interface chrome; authored prose and machine tokens remain unchanged.
    for token, english_label in LABELS_EN.items():
        zh_label = LABELS.get(token)
        if zh_label:
            document = document.replace(f">{esc(zh_label)}<", f">{esc(english_label)}<")
            document = document.replace(f">{esc(zh_label)}／", f">{esc(english_label)} / ")
            document = document.replace(f"／{esc(zh_label)}<", f" / {esc(english_label)}<")
    return document


def run_self_test(state: dict[str, Any]) -> str:
    completed: list[str] = []

    def expect_invalid(name: str, candidate: dict[str, Any], fragment: str) -> None:
        candidate_errors = validate_state(candidate)
        if not any(fragment in error for error in candidate_errors):
            raise ValueError(f"self-test {name} 未擋下預期錯誤：{fragment}；實際={candidate_errors}")
        completed.append(name)

    def claim_by_id(candidate: dict[str, Any], claim_id: str) -> dict[str, Any]:
        return next(
            claim
            for claim in candidate["currentTruth"]["evidenceClaims"]
            if claim["id"] == claim_id
        )

    def terminal_posture(candidate: dict[str, Any]) -> None:
        for claim_id in (
            "claim-operator-session",
            "claim-session-context",
            "claim-confirm-dialog-exact",
            "claim-confirm-control-ready",
        ):
            claim_by_id(candidate, claim_id)["status"] = "UNKNOWN"
        candidate["currentTruth"]["observerHealth"][0]["status"] = "UNKNOWN"
        candidate["executionAssessment"].update(
            {
                "mode": "AUTONOMOUS",
                "automationActuatorStatus": "UNKNOWN",
                "targetIdentity": "UNKNOWN",
                "actorIdentity": "UNKNOWN",
                "actionContract": "VERIFIED",
            }
        )
        candidate["takeoverReadiness"]["operable"]["status"] = "UNKNOWN"
        candidate["takeoverReadiness"]["result"] = "NOT_READY"
        candidate["intervention"] = {
            "status": "NOT_REQUIRED",
            "mode": "NONE",
            "phase": "NONE",
            "requestedAction": "",
            "reason": "",
            "returnOfControl": "",
        }
        main_front = candidate["battlefields"][0]
        main_front["status"] = "DEFERRED"
        main_front["deferReason"] = "戰役已進入證據封閉的終局，不再保留活動主攻"
        main_candidate = candidate["decision"]["candidates"][0]
        main_candidate["eligible"] = False
        main_candidate["ineligibilityReason"] = "戰場已 DEFERRED；終局沒有下一個戰術動作"
        candidate["strategicClarity"].update(
            {
                "status": "CLEAR",
                "candidateMainEffortIds": [],
                "route": "TERMINAL",
                "wayfinderMapPath": "",
            }
        )

    def loss_minimized_candidate() -> dict[str, Any]:
        candidate = copy.deepcopy(state)
        claim_by_id(candidate, "claim-victory-unattainable")["status"] = "PASS"
        claim_by_id(candidate, "claim-loss-cleanup-closed")["status"] = "PASS"
        claim_by_id(candidate, "claim-route-closed")["status"] = "PASS"
        cleanup_item = candidate["currentTruth"]["cleanupDebt"][0]
        cleanup_item["status"] = "CLOSED"
        cleanup_item["evidenceClaimIds"] = ["claim-loss-cleanup-closed"]
        candidate["terminalAssessment"]["status"] = "LOSS_MINIMIZED"
        candidate["terminalAssessment"]["requiredAuthority"] = ""
        candidate["terminalAssessment"]["alternativeRoutes"][0]["status"] = "CLOSED"
        terminal_posture(candidate)
        return candidate

    def victory_candidate() -> dict[str, Any]:
        candidate = copy.deepcopy(state)
        for criterion, claim_id in zip(
            candidate["strategicObjective"]["victoryCriteria"],
            ("claim-no-active-task", "claim-no-active-run", "claim-cross-layer-terminal"),
        ):
            claim_by_id(candidate, claim_id)["status"] = "PASS"
            criterion["status"] = "PASS"
        claim_by_id(candidate, "claim-loss-cleanup-closed")["status"] = "PASS"
        candidate["currentTruth"]["cleanupDebt"][0]["status"] = "CLOSED"
        candidate["terminalAssessment"]["status"] = "STRATEGIC_OBJECTIVE_ACHIEVED"
        support_candidate = candidate["decision"]["candidates"][1]
        support_candidate["unmetVictoryCriteria"] = 0
        support_candidate["totalScore"] = 80
        terminal_posture(candidate)
        return candidate

    base_errors = validate_state(state)
    if base_errors:
        raise ValueError(f"self-test valid-example 失敗：{base_errors}")
    completed.append("valid-example")

    quoted_predicate = canonical_predicate(
        "RISK[{}]@FRONT[{}].STATUS == {}",
        'risk]@FRONT["forged',
        "front,with-delimiter",
        "CONTROLLED",
    )
    if quoted_predicate != 'RISK["risk]@FRONT[\\"forged"]@FRONT["front,with-delimiter"].STATUS == "CONTROLLED"':
        raise ValueError(f"self-test canonical-json-quoting 失敗：{quoted_predicate}")
    completed.append("canonical-json-quoting")

    ambiguous = copy.deepcopy(state)
    ambiguous["executionAssessment"]["targetIdentity"] = "AMBIGUOUS"
    expect_invalid("unreliable-ambiguous-target", ambiguous, "targetIdentity=EXACT_ONE")

    insufficient = copy.deepcopy(state)
    insufficient["executionAssessment"]["sameFailureFingerprintCount"] = 1
    insufficient["executionAssessment"]["deadlineExceeded"] = False
    expect_invalid("unreliable-insufficient-signal", insufficient, "failure fingerprint 至少兩次")

    unknown_outcome = copy.deepcopy(state)
    unknown_outcome["executionAssessment"]["outcomeStatus"] = "OUTCOME_UNKNOWN"
    expect_invalid("unknown-outcome-not-unreliable", unknown_outcome, "OUTCOME_UNKNOWN")

    mutation_seen = copy.deepcopy(state)
    mutation_seen["executionAssessment"]["mutationObserved"] = True
    expect_invalid("mutation-not-unreliable", mutation_seen, "已觀測到 mutation")

    deadline_path = copy.deepcopy(state)
    deadline_path["executionAssessment"]["sameFailureFingerprintCount"] = 1
    deadline_path["executionAssessment"]["deadlineExceeded"] = True
    deadline_path["progress"]["sameFailureFingerprintCount"] = 1
    deadline_errors = validate_state(deadline_path)
    if deadline_errors:
        raise ValueError(f"self-test hard-deadline-valid 失敗：{deadline_errors}")
    completed.append("hard-deadline-valid")

    readiness_mismatch = copy.deepcopy(state)
    readiness_mismatch["takeoverReadiness"]["operable"]["status"] = "FAIL"
    expect_invalid("readiness-derived-receipt", readiness_mismatch, "evidence contract 算為 PASS")

    takeover_not_ready = copy.deepcopy(state)
    claim_by_id(takeover_not_ready, "claim-confirm-control-ready")["status"] = "FAIL"
    takeover_not_ready["takeoverReadiness"]["operable"]["status"] = "FAIL"
    takeover_not_ready["takeoverReadiness"]["result"] = "NOT_READY"
    expect_invalid("takeover-requires-three-gates", takeover_not_ready, "必須通過 OPERABLE")

    multi_step = copy.deepcopy(state)
    multi_step["takeoverReadiness"]["executable"]["steps"].append("再按一次其他控制項")
    expect_invalid("takeover-exactly-one-step", multi_step, "steps 必須精確包含一個有限動作")

    unrelated_gate_claim = copy.deepcopy(state)
    unrelated_gate_claim["takeoverReadiness"]["operable"]["actorCheck"]["evidenceClaimIds"] = [
        "claim-no-finalize-mutation"
    ]
    expect_invalid(
        "takeover-unrelated-pass-claim",
        unrelated_gate_claim,
        "canonical predicate：ACTOR",
    )

    legacy_gate_predicate = copy.deepcopy(state)
    legacy_gate_predicate["takeoverReadiness"]["operable"]["actorCheck"]["predicate"] = (
        "FINALIZE_MUTATION_COUNT == 0"
    )
    expect_invalid(
        "takeover-custom-predicate-forbidden",
        legacy_gate_predicate,
        "takeoverReadiness.operable.actorCheck.predicate 不在 schema 中",
    )

    all_gate_spoof = copy.deepcopy(state)
    unrelated_refs = ["claim-no-finalize-mutation"]
    for check_name in ("actorCheck", "sessionCheck", "targetCheck", "controlCheck"):
        all_gate_spoof["takeoverReadiness"]["operable"][check_name]["evidenceClaimIds"] = unrelated_refs
    all_gate_spoof["takeoverReadiness"]["executable"]["authorityCheck"]["evidenceClaimIds"] = unrelated_refs
    for check in all_gate_spoof["takeoverReadiness"]["executable"]["prerequisiteChecks"]:
        check["evidenceClaimIds"] = unrelated_refs
    for check in all_gate_spoof["takeoverReadiness"]["verifiable"]["baselineChecks"]:
        check["evidenceClaimIds"] = unrelated_refs
    spoof_errors = validate_state(all_gate_spoof)
    if not any("canonical predicate" in error for error in spoof_errors):
        raise ValueError(f"self-test takeover-all-gates-unrelated-pass 未拒絕：{spoof_errors}")
    if not any("完整接管條件算為 NOT_READY" in error for error in spoof_errors):
        raise ValueError(f"self-test takeover-all-gates-unrelated-pass 未導出 NOT_READY：{spoof_errors}")
    completed.append("takeover-all-gates-unrelated-pass")

    shared_baseline = copy.deepcopy(state)
    shared_baseline["takeoverReadiness"]["verifiable"]["expectedWorldDeltaContracts"][1][
        "baselineCheckId"
    ] = "operation-status-before"
    expect_invalid(
        "takeover-world-baseline-one-to-one",
        shared_baseline,
        "每個 contract 必須有一個專屬 baseline",
    )

    manual_gate_pass = copy.deepcopy(state)
    claim_by_id(manual_gate_pass, "claim-operator-session")["status"] = "UNKNOWN"
    expect_invalid("takeover-manual-pass-receipt", manual_gate_pass, "evidence contract 算為 UNKNOWN")

    healthy_automation = copy.deepcopy(state)
    healthy_automation["executionAssessment"]["automationActuatorStatus"] = "RELIABLE"
    expect_invalid("takeover-requires-proven-automation-wedge", healthy_automation, "完整接管條件算為 NOT_READY")

    mismatched_requested_action = copy.deepcopy(state)
    mismatched_requested_action["intervention"]["requestedAction"] = "按兩次確認"
    expect_invalid(
        "takeover-packet-byte-equals-step",
        mismatched_requested_action,
        "requestedAction 必須 byte-equal 唯一 executable step",
    )

    zero_attempt = copy.deepcopy(state)
    zero_attempt["executionAssessment"]["attemptCount"] = 0
    zero_attempt["executionAssessment"]["sameFailureFingerprintCount"] = 0
    zero_attempt["executionAssessment"]["deadlineExceeded"] = True
    zero_attempt["progress"]["sameFailureFingerprintCount"] = 0
    expect_invalid("takeover-zero-attempt-forbidden", zero_attempt, "attemptCount 至少為 1")

    bda = copy.deepcopy(state)
    bda["intervention"]["status"] = "IN_PROGRESS"
    bda["intervention"]["phase"] = "BATTLE_DAMAGE_ASSESSMENT"
    bda_errors = validate_state(bda)
    if bda_errors:
        raise ValueError(f"self-test bda-valid 失敗：{bda_errors}")

    bda_html = render_html(bda)
    bda_message = "使用者操作已完成；正在由 Agent 以 UI／API／DB 評估戰果，尚未宣告成功。"
    if bda_message not in bda_html:
        raise ValueError("self-test bda-no-false-pass 未顯示戰果評估提示")
    completed.append("bda-no-false-pass")

    takeover_html = render_html(state)
    if "三道接管門" not in takeover_html:
        raise ValueError("self-test takeover-action-gates-visible 未顯示戰術接管接管門")
    completed.append("takeover-action-gates-visible")
    if "三道接管門" in bda_html:
        raise ValueError("self-test bda-action-gates-hidden 仍顯示內部接管門")
    completed.append("bda-action-gates-hidden")

    no_intervention = copy.deepcopy(state)
    no_intervention["intervention"] = {
        "status": "NOT_REQUIRED",
        "mode": "NONE",
        "phase": "NONE",
        "requestedAction": "",
        "reason": "",
        "returnOfControl": "",
    }
    if "三道接管門" in render_html(no_intervention):
        raise ValueError("self-test no-intervention-action-gates-hidden 仍顯示內部接管門")
    completed.append("no-intervention-action-gates-hidden")

    public_html = render_html(state)
    if "什麼時候才算完成" not in public_html or "完成條件" not in public_html:
        raise ValueError("self-test victory-criteria-plain-language 缺少白話完成條件")
    if (
        'id="active-front-elapsed"' not in public_html
        or state["progress"]["activeFrontStartedAt"] not in public_html
    ):
        raise ValueError("self-test active-front-live-clock 缺少主攻起算時間")
    completed.append("public-dashboard-language-and-live-clock")
    if '<details class="card wide technical" open>' not in public_html:
        raise ValueError("self-test technical-default-open 技術細節未預設展開")
    if '<div class="table-scroll"><table class="front-contract-table">' not in public_html:
        raise ValueError("self-test recovery-table-layout 戰場技術契約缺少獨立捲動排版")
    completed.append("technical-default-open-and-recovery-layout")

    legacy_title = "\u63a8\u6f14\u6c99\u76e4"
    if "戰略推進沙盤" not in public_html or legacy_title in public_html:
        raise ValueError("self-test strategic-advance-title 未使用戰略推進沙盤名稱")
    if "展開完整歷史" not in public_html:
        raise ValueError("self-test expandable-history 缺少完整歷史展開控制")
    english_html = render_html(state, "en")
    if '<html lang="en">' not in english_html or "Strategic Advance Sand Table" not in english_html:
        raise ValueError("self-test english-renderer 缺少英文介面")
    for untranslated_chrome in (
        "戰術接管：只做這一動",
        "只有可操作、可執行、可檢核全部通過，才會顯示戰術接管指令。",
        "Tactic接管",
    ):
        if untranslated_chrome in english_html:
            raise ValueError(f"self-test english-takeover-chrome 仍含未翻譯介面：{untranslated_chrome}")
    completed.append("localized-title-and-expandable-history")
    compact_graph = render_battle_map_svg(state)
    if not all(label in compact_graph for label in ("目前狀態", "下一動", "戰略終局")):
        raise ValueError("self-test compact-graph 缺少目前狀態、下一動或戰略終局")
    if 'class="edge-support"' in compact_graph:
        raise ValueError("self-test compact-graph-invented-edge 仍將支援戰場連向主攻")
    full_graph = render_battle_map_svg(state, "en", full_history=True)
    if "Full battle history" not in full_graph:
        raise ValueError("self-test full-history-graph 缺少英文完整歷史")
    if ' class="causal"' in full_graph:
        raise ValueError("self-test full-history-invented-edge 為無因果關係戰場畫了連線")
    mismatched_history = copy.deepcopy(state)
    mismatched_history["battlefields"][0]["causalPredecessorIds"] = [
        mismatched_history["battlefields"][1]["id"]
    ]
    if ' class="causal"' in render_battle_map_svg(mismatched_history, full_history=True):
        raise ValueError("self-test mismatched-explicit-edge 為狀態不吻合的 explicit predecessor 畫了連線")
    completed.append("compact-and-full-history-graphs")

    causal_history = copy.deepcopy(state)
    causal_front = causal_history["battlefields"][1]
    causal_front["status"] = "COMPLETE"
    causal_front["terminalState"] = causal_history["battlefields"][0]["entryState"]
    causal_history["battlefields"][0]["causalPredecessorIds"] = [causal_front["id"]]
    causal_graph = render_battle_map_svg(causal_history)
    if "1 個已完成因果前置" not in causal_graph or causal_front["objective"] in causal_graph:
        raise ValueError("self-test completed-causal-collapse 未壓縮已完成因果前置")
    completed.append("completed-causal-collapse")

    many_fronts = copy.deepcopy(state)
    side_template = many_fronts["battlefields"][1]
    many_fronts["battlefields"] = [many_fronts["battlefields"][0]]
    for index in range(10):
        side = copy.deepcopy(side_template)
        side["id"] = f"independent-{index}"
        side["objective"] = f"Independent support front {index}"
        side.pop("causalPredecessorIds", None)
        many_fronts["battlefields"].append(side)
    bounded_graph = render_battle_map_svg(many_fronts)
    if (
        'viewBox="0 0 1480 500"' not in bounded_graph
        or bounded_graph.count('class="node-side"') != 4
        or "+6 個其他戰場" not in bounded_graph
    ):
        raise ValueError("self-test bounded-side-rail 側欄未固定收斂")
    completed.append("bounded-side-rail")

    if state["battlefields"][0]["entryState"] in compact_graph:
        raise ValueError("self-test compact-graph-machine-state-leak 仍在第一層顯示內部狀態 token")
    if any(
        limit * font_size > width - padding
        for width, padding, limit, font_size in (
            (330, 34, 18, 15),
            (350, 34, 20, 15),
            (315, 34, 17, 15),
            (210, 26, 14, 13),
        )
    ):
        raise ValueError("self-test compact-graph-text-budget 卡片字寬預算超出內容區")
    if not all(
        f'clip-path="url(#{clip_id})"' in compact_graph
        and f'<clipPath id="{clip_id}">' in compact_graph
        for clip_id in ("clip-current-title", "clip-next-title", "clip-goal-title")
    ):
        raise ValueError("self-test compact-graph-text-clipping 主卡缺少文字裁切保護")
    completed.append("compact-graph-public-language-and-spacing")

    legacy_elapsed = copy.deepcopy(state)
    legacy_elapsed["progress"]["activeFrontElapsedMinutes"] = 0
    expect_invalid("manual-active-front-elapsed-forbidden", legacy_elapsed, "activeFrontElapsedMinutes 已停用")

    future_front = copy.deepcopy(state)
    future_front["progress"]["activeFrontStartedAt"] = "2099-01-01T00:00:00+08:00"
    expect_invalid("active-front-start-after-state", future_front, "activeFrontStartedAt 不得晚於 state.updatedAt")

    legacy_confidence = copy.deepcopy(state)
    legacy_confidence["currentTruth"]["confidence"] = 0.98
    expect_invalid("numeric-confidence-forbidden", legacy_confidence, "confidence 已停用")

    weak_authority = copy.deepcopy(state)
    original_before = next(
        claim for claim in weak_authority["currentTruth"]["evidenceClaims"]
        if claim["id"] == "claim-operation-preparing-before"
    )
    weak_claim = copy.deepcopy(original_before)
    weak_claim["id"] = "claim-operation-preparing-before-weak"
    weak_claim["authorityRank"] = 2
    weak_authority["currentTruth"]["evidenceClaims"].append(weak_claim)
    weak_authority["latestVerifiedAdvance"]["beforeClaimId"] = weak_claim["id"]
    weak_authority["latestVerifiedAdvance"]["evidenceClaimIds"] = [
        weak_claim["id"],
        "claim-operation-ready",
    ]
    expect_invalid("lower-authority-world-delta", weak_authority, "beforeClaimId 必須是有效權威")

    unrelated_world_delta = copy.deepcopy(state)
    unrelated_world_delta["latestVerifiedAdvance"]["beforeClaimId"] = "claim-operator-session"
    unrelated_world_delta["latestVerifiedAdvance"]["afterClaimId"] = "claim-confirm-dialog-exact"
    unrelated_world_delta["latestVerifiedAdvance"]["evidenceClaimIds"] = [
        "claim-operator-session",
        "claim-confirm-dialog-exact",
    ]
    unrelated_world_delta["latestVerifiedAdvance"]["at"] = "2026-08-14T09:28:20+08:00"
    unrelated_world_delta["progress"]["lastWorldStateChangeAt"] = "2026-08-14T09:28:20+08:00"
    expect_invalid(
        "world-delta-unrelated-pass-claims",
        unrelated_world_delta,
        "beforeClaimId 的 claim predicate 必須精確等於 canonical WORLD before predicate",
    )

    legacy_world_predicate = copy.deepcopy(state)
    legacy_world_predicate["latestVerifiedAdvance"]["beforePredicate"] = (
        "WORLD_STATE_CHANGED == true"
    )
    expect_invalid(
        "world-delta-custom-predicate-forbidden",
        legacy_world_predicate,
        "latestVerifiedAdvance.beforePredicate 不在 schema 中",
    )

    effect_mismatch = copy.deepcopy(state)
    effect_mismatch["latestVerifiedAdvance"]["strategicEffect"] = (
        "SATISFIES_VICTORY_CRITERION"
    )
    effect_mismatch["latestVerifiedAdvance"]["effectTargetId"] = "no-active-task"
    expect_invalid(
        "world-delta-effect-target-mismatch",
        effect_mismatch,
        "strategicEffect 與 effectTargetId 的 current derived state 不相符",
    )

    controlled_risk_effect = copy.deepcopy(state)
    controlled_risk_effect["riskRegister"][0]["unacceptableThreshold"] = 10
    controlled_risk_effect["latestVerifiedAdvance"]["strategicEffect"] = (
        "CONTROLS_UNACCEPTABLE_RISK"
    )
    controlled_risk_effect["latestVerifiedAdvance"]["effectTargetId"] = (
        "duplicate-finalization"
    )
    controlled_effect_errors = validate_state(controlled_risk_effect)
    if controlled_effect_errors:
        raise ValueError(
            f"self-test world-delta-target-derived-effect-valid 失敗：{controlled_effect_errors}"
        )
    completed.append("world-delta-target-derived-effect-valid")

    unrelated_entry = copy.deepcopy(state)
    unrelated_entry["battlefields"][0]["entryClaimId"] = "claim-no-finalize-mutation"
    expect_invalid(
        "battlefield-entry-unrelated-pass-claim",
        unrelated_entry,
        "entryClaimId 的 claim predicate 必須精確等於 canonical entry predicate",
    )

    legacy_battlefield_predicate = copy.deepcopy(state)
    legacy_battlefield_predicate["battlefields"][0]["entryPredicate"] = "ANYTHING == true"
    expect_invalid(
        "battlefield-custom-predicate-forbidden",
        legacy_battlefield_predicate,
        "battlefields[0].entryPredicate 已停用",
    )

    unclear = copy.deepcopy(state)
    unclear["strategicClarity"]["unresolvedDecisions"].append(
        {
            "id": "actor-choice",
            "question": "哪個 actor 有權限執行下一動",
            "decisionPredicate": "AUTHORIZED_ACTOR_COUNT == 1",
            "owner": "wayfinder",
        }
    )
    expect_invalid("clarity-derived", unclear, "status 必須由決策條件算為 UNCLEAR")

    unrelated_pivot = copy.deepcopy(state)
    unrelated_pivot["decision"]["pivotClaimId"] = "claim-route-closed"
    expect_invalid(
        "pivot-unrelated-claim",
        unrelated_pivot,
        "claim predicate 必須精確等於 canonical active-front pivot predicate",
    )

    legacy_pivot_fields = copy.deepcopy(state)
    legacy_pivot_fields["decision"]["pivotPredicate"] = "ANYTHING == true"
    legacy_pivot_fields["decision"]["pivotWhen"] = "FAIL"
    expect_invalid(
        "pivot-custom-semantics-forbidden",
        legacy_pivot_fields,
        "decision.pivotPredicate 已停用",
    )

    pivot_triggered_wrong_receipt = copy.deepcopy(state)
    claim_by_id(pivot_triggered_wrong_receipt, "claim-main-pivot-not-triggered")["status"] = "PASS"
    expect_invalid(
        "pivot-pass-cannot-remain-clear",
        pivot_triggered_wrong_receipt,
        "strategicClarity.status 必須由決策條件算為 UNCLEAR",
    )

    pivot_triggered = copy.deepcopy(pivot_triggered_wrong_receipt)
    pivot_triggered["strategicClarity"].update(
        {
            "status": "UNCLEAR",
            "route": "OPERATOR_RESOLVE",
            "unclearCauses": ["PIVOT_TRIGGERED"],
            "wayfinderMapPath": ".claude/wayfinder/example-pivot/map.html",
        }
    )
    pivot_triggered_errors = validate_state(pivot_triggered)
    if pivot_triggered_errors:
        raise ValueError(f"self-test pivot-pass-forces-reassessment 失敗：{pivot_triggered_errors}")
    completed.append("pivot-pass-forces-reassessment")

    pivot_unknown = copy.deepcopy(pivot_triggered)
    claim_by_id(pivot_unknown, "claim-main-pivot-not-triggered")["status"] = "UNKNOWN"
    pivot_unknown["strategicClarity"]["unclearCauses"] = ["PIVOT_UNPROBED"]
    pivot_unknown_errors = validate_state(pivot_unknown)
    if pivot_unknown_errors:
        raise ValueError(f"self-test pivot-unknown-remains-unclear 失敗：{pivot_unknown_errors}")
    completed.append("pivot-unknown-remains-unclear")

    fog_routes = copy.deepcopy(pivot_unknown)
    fog_routes["strategicClarity"]["unresolvedDecisions"].append(
        {
            "id": "fog-1",
            "question": "接管授權歸誰",
            "decisionPredicate": "AUTHORIZED_ACTOR_COUNT == 1",
            "owner": "wayfinder",
        }
    )
    fog_routes["strategicClarity"]["route"] = "WAYFINDER_REQUIRED"
    fog_routes["strategicClarity"]["unclearCauses"] = ["DECISION_FOG", "PIVOT_UNPROBED"]
    fog_routes_errors = validate_state(fog_routes)
    if fog_routes_errors:
        raise ValueError(f"self-test fog-routes-to-wayfinder 失敗：{fog_routes_errors}")
    completed.append("fog-routes-to-wayfinder")

    pivot_expired = copy.deepcopy(pivot_unknown)
    claim_by_id(pivot_expired, "claim-main-pivot-not-triggered")["validUntil"] = (
        "2026-08-14T09:29:30+08:00"
    )
    pivot_expired_errors = validate_state(pivot_expired)
    if pivot_expired_errors:
        raise ValueError(f"self-test pivot-expired-remains-unclear 失敗：{pivot_expired_errors}")
    completed.append("pivot-expired-remains-unclear")

    stale_context = copy.deepcopy(state)
    claim_by_id(stale_context, "claim-operation-ready")["validUntil"] = (
        "2026-08-14T09:29:30+08:00"
    )
    stale_context_errors = validate_state(stale_context)
    if stale_context_errors:
        raise ValueError(
            f"self-test expiry-degrades-authority-not-legality 失敗：{stale_context_errors}"
        )
    completed.append("expiry-degrades-authority-not-legality")

    stale_entry = copy.deepcopy(state)
    claim_by_id(stale_entry, "claim-main-entry")["validUntil"] = (
        "2026-08-14T09:29:30+08:00"
    )
    expect_invalid(
        "expired-gating-claim-is-targeted-work-order", stale_entry, "=ACTIVE 要求 entry PASS"
    )

    blocker_active = copy.deepcopy(state)
    blocker_active["blockers"].append(
        {
            "id": "automation-confirm-mask",
            "status": "PROVEN",
            "blockedFrontId": "finalize-sample-operation",
            "requiredPredicate": "PRE_SUBMIT_OVERLAY_FAILURE_COUNT >= 2",
            "observedValue": "true",
            "requiredEvidenceClaimIds": ["claim-mask-failure"],
            "remediationAction": "TACTICAL_TAKEOVER",
            "clearPredicate": "FINALIZED_NO_ACTIVE_RESIDUE == true",
            "clearEvidenceClaimIds": ["claim-main-exit"],
        }
    )
    expect_invalid("active-front-proven-blocker", blocker_active, "且無 PROVEN blocker")

    recovery_not_ready = copy.deepcopy(state)
    recovery_not_ready["battlefields"][0]["recovery"]["status"] = "NOT_READY"
    expect_invalid("active-mutation-recovery", recovery_not_ready, "recovery 必須 READY")

    recovery_fail_evidence = copy.deepcopy(state)
    claim_by_id(recovery_fail_evidence, "claim-state-readback-ready")["status"] = "FAIL"
    expect_invalid(
        "recovery-ready-requires-pass-evidence",
        recovery_fail_evidence,
        "exact authoritative PASS readiness evidence",
    )

    candidate_score = copy.deepcopy(state)
    candidate_score["decision"]["candidates"][0]["totalScore"] = 61
    expect_invalid("candidate-fixed-score", candidate_score, "totalScore 必須依固定公式算為 62")

    risk_score = copy.deepcopy(state)
    risk_score["riskRegister"][0]["score"] = 11
    expect_invalid("risk-fixed-score", risk_score, "score 必須等於 probability × impact")

    missing_assets = copy.deepcopy(state)
    missing_assets["strategicObjective"]["protectedAssets"] = []
    expect_invalid(
        "risk-requires-protected-assets",
        missing_assets,
        "strategicObjective.protectedAssets 不得為空",
    )

    unknown_risk_asset = copy.deepcopy(state)
    unknown_risk_asset["riskRegister"][0]["protectedAssetId"] = "unregistered-asset"
    expect_invalid(
        "risk-must-threaten-registered-asset",
        unknown_risk_asset,
        "protectedAssetId 必須引用 strategicObjective.protectedAssets",
    )

    missing_risk_threat = copy.deepcopy(state)
    missing_risk_threat["riskRegister"][0]["threat"] = ""
    expect_invalid(
        "risk-requires-concrete-threat",
        missing_risk_threat,
        "riskRegister[0].threat 必須是非空字串",
    )

    risk_manual_closed = copy.deepcopy(state)
    risk_manual_closed["riskRegister"][0]["status"] = "CLOSED"
    expect_invalid("risk-manual-status-forbidden", risk_manual_closed, "statusChecks 算為 CONTROLLED")

    risk_unrelated_claim = copy.deepcopy(state)
    risk_unrelated_claim["riskRegister"][0]["statusChecks"]["CONTROLLED"]["evidenceClaimIds"] = [
        "claim-no-finalize-mutation"
    ]
    expect_invalid(
        "risk-unrelated-pass-claim",
        risk_unrelated_claim,
        "canonical predicate：RISK",
    )

    legacy_risk_predicate = copy.deepcopy(state)
    legacy_risk_predicate["riskRegister"][0]["statusChecks"]["CONTROLLED"][
        "predicate"
    ] = "ANYTHING == true"
    expect_invalid(
        "risk-custom-predicate-forbidden",
        legacy_risk_predicate,
        "riskRegister[0].statusChecks.CONTROLLED.predicate 不在 schema 中",
    )

    risk_closed = copy.deepcopy(state)
    claim_by_id(risk_closed, "claim-duplicate-guard-controlled")["status"] = "UNKNOWN"
    claim_by_id(risk_closed, "claim-duplicate-risk-closed")["status"] = "PASS"
    risk_closed["riskRegister"][0]["status"] = "CLOSED"
    risk_closed["decision"]["candidates"][0]["riskScore"] = 0
    risk_closed["decision"]["candidates"][0]["totalScore"] = 12
    risk_closed_errors = validate_state(risk_closed)
    if risk_closed_errors:
        raise ValueError(f"self-test risk-canonical-closed-valid 失敗：{risk_closed_errors}")
    completed.append("risk-canonical-closed-valid")

    support_only_risk = copy.deepcopy(state)
    support_only_risk["currentTruth"]["evidenceClaims"].extend(
        [
            {
                "id": "claim-support-risk-controlled",
                "sourceType": "STATIC",
                "sourceRef": "支援風險尚未受控",
                "observedAt": "2026-08-14T09:29:40+08:00",
                "validUntil": "2026-08-14T12:00:00+08:00",
                "authorityRank": 1,
                "predicate": "RISK[\"support-observer-risk\"]@FRONT[\"request-detail-observer\"].STATUS == \"CONTROLLED\"",
                "status": "UNKNOWN",
            },
            {
                "id": "claim-support-risk-accepted",
                "sourceType": "STATIC",
                "sourceRef": "支援風險尚未被接受",
                "observedAt": "2026-08-14T09:29:41+08:00",
                "validUntil": "2026-08-14T12:00:00+08:00",
                "authorityRank": 1,
                "predicate": "RISK[\"support-observer-risk\"]@FRONT[\"request-detail-observer\"].STATUS == \"ACCEPTED\"",
                "status": "UNKNOWN",
            },
            {
                "id": "claim-support-risk-closed",
                "sourceType": "STATIC",
                "sourceRef": "支援風險尚未關閉",
                "observedAt": "2026-08-14T09:29:42+08:00",
                "validUntil": "2026-08-14T12:00:00+08:00",
                "authorityRank": 1,
                "predicate": "RISK[\"support-observer-risk\"]@FRONT[\"request-detail-observer\"].STATUS == \"CLOSED\"",
                "status": "UNKNOWN",
            },
        ]
    )
    support_only_risk["riskRegister"].append(
        {
            "id": "support-observer-risk",
            "affectedFrontId": "request-detail-observer",
            "protectedAssetId": "evidence-integrity",
            "threat": "觀測器修復若侵入主線，可能破壞已確認的證據完整性",
            "status": "OPEN",
            "probability": 5,
            "impact": 5,
            "score": 25,
            "unacceptableThreshold": 12,
            "guard": "不讓 observer 修復影響主線",
            "stopCondition": "任何主線 mutation 出現即停",
            "recoveryAction": "撤銷 observer 變更",
            "statusChecks": {
                "CONTROLLED": {
                    "evidenceClaimIds": ["claim-support-risk-controlled"],
                },
                "ACCEPTED": {
                    "evidenceClaimIds": ["claim-support-risk-accepted"],
                },
                "CLOSED": {
                    "evidenceClaimIds": ["claim-support-risk-closed"],
                },
            },
        }
    )
    support_candidate = support_only_risk["decision"]["candidates"][1]
    support_candidate["riskScore"] = 25
    support_candidate["blockingRiskIds"] = ["support-observer-risk"]
    support_candidate["totalScore"] = 505
    support_only_risk["decision"]["contribution"] = "CONTROL_RISK"
    expect_invalid(
        "control-risk-must-affect-active-front",
        support_only_risk,
        "CONTROL_RISK 要求目前 activeFrontId",
    )

    observer_status = copy.deepcopy(state)
    observer_status["currentTruth"]["observerHealth"][1]["status"] = "HEALTHY"
    expect_invalid("observer-derived-status", observer_status, "claim coverage 算為 DEGRADED")

    culmination = copy.deepcopy(state)
    culmination["progress"]["culminationRisk"] = "LOW"
    expect_invalid("culmination-derived-risk", culmination, "門檻算為 MEDIUM")

    cleanup = copy.deepcopy(state)
    cleanup["currentTruth"]["cleanupDebt"][0]["severity"] = "NON_BLOCKING"
    expect_invalid("cleanup-blocks-victory", cleanup, "blocksVictory=true 要求 severity=BLOCKING")

    cleanup_unrelated = copy.deepcopy(state)
    cleanup_unrelated["currentTruth"]["cleanupDebt"][0]["status"] = "CLOSED"
    cleanup_unrelated["currentTruth"]["cleanupDebt"][0]["evidenceClaimIds"] = [
        "claim-no-finalize-mutation"
    ]
    expect_invalid(
        "cleanup-unrelated-pass-claim",
        cleanup_unrelated,
        "claim predicate 必須精確等於 currentTruth.cleanupDebt[0].verificationPredicate",
    )

    victory_unrelated = copy.deepcopy(state)
    for criterion in victory_unrelated["strategicObjective"]["victoryCriteria"]:
        criterion["status"] = "PASS"
        criterion["evidenceClaimIds"] = ["claim-no-finalize-mutation"]
    expect_invalid(
        "victory-unrelated-pass-claim",
        victory_unrelated,
        "claim predicate 必須精確等於 strategicObjective.victoryCriteria[0].predicate",
    )

    victory = victory_candidate()
    victory_errors = validate_state(victory)
    if victory_errors:
        raise ValueError(f"self-test victory-terminal-valid 失敗：{victory_errors}")
    completed.append("victory-terminal-valid")

    victory_html = render_html(victory)
    if '<body class="victory-achieved">' not in victory_html:
        raise ValueError("self-test victory-html-mode 缺少 victory-achieved body state")
    if '<section class="victory-banner"' not in victory_html or "戰局完成" not in victory_html:
        raise ValueError("self-test victory-html-banner 缺少明確完成 banner")
    if 'aria-live="polite"' not in victory_html:
        raise ValueError("self-test victory-html-a11y 缺少完成態 aria-live")
    if '<meta http-equiv="refresh"' in victory_html or "LIVE SAND TABLE" in victory_html:
        raise ValueError("self-test victory-html-sealed 仍宣稱 live 或持續 refresh")
    if ".victory-banner" not in victory_html or "prefers-reduced-motion:no-preference" not in victory_html:
        raise ValueError("self-test victory-html-motion 缺少完成態視覺或 reduced-motion gate")
    if 'class="victory-electric"' not in victory_html or "@keyframes electric-top" not in victory_html:
        raise ValueError("self-test victory-html-electric 缺少一次性電光特效")
    victory_graph = render_battle_map_svg(victory, "zh-TW")
    for expected in ("最終狀態", "戰果確認", "戰局完成", "已封盤"):
        if expected not in victory_graph:
            raise ValueError(f"self-test victory-compact-map 缺少 {expected}")
    for forbidden in ("下一動", "唯一主攻"):
        if forbidden in victory_graph:
            raise ValueError(f"self-test victory-compact-map 仍含 {forbidden}")
    victory_english_html = render_html(victory, "en")
    if "Campaign complete" not in victory_english_html or "VICTORY CONFIRMED" not in victory_english_html:
        raise ValueError("self-test victory-en-chrome 缺少完整英文完成態")
    if '<section class="victory-banner"' in render_html(state):
        raise ValueError("self-test in-progress-no-victory-banner 誤顯示勝利 banner")
    completed.append("victory-presentation-terminal-only")

    loss_minimized = loss_minimized_candidate()
    loss_errors = validate_state(loss_minimized)
    if loss_errors:
        raise ValueError(f"self-test loss-minimized-valid 失敗：{loss_errors}")
    if "損失已降至可證明界線" not in build_summary(loss_minimized):
        raise ValueError("self-test loss-minimized-zh-label 缺少繁中終局標籤")
    if "Loss minimized within proven bounds" not in render_html(loss_minimized, "en"):
        raise ValueError("self-test loss-minimized-en-label 缺少英文終局標籤")
    if '<section class="victory-banner"' in render_html(loss_minimized):
        raise ValueError("self-test loss-minimized-no-victory-banner 誤顯示勝利 banner")
    completed.append("loss-minimized-valid-and-localized")

    loss_missing_claim = loss_minimized_candidate()
    loss_missing_claim["currentTruth"]["evidenceClaims"] = [
        claim
        for claim in loss_missing_claim["currentTruth"]["evidenceClaims"]
        if claim["id"] != "claim-victory-unattainable"
    ]
    expect_invalid("loss-missing-claim", loss_missing_claim, "引用不存在的 evidence claim")

    loss_open_route = loss_minimized_candidate()
    claim_by_id(loss_open_route, "claim-route-closed")["status"] = "UNKNOWN"
    loss_open_route["terminalAssessment"]["alternativeRoutes"][0]["status"] = "OPEN"
    expect_invalid("loss-open-route", loss_open_route, "終局 predicate 算為 IN_PROGRESS")

    loss_empty_routes = loss_minimized_candidate()
    loss_empty_routes["terminalAssessment"]["alternativeRoutes"] = []
    expect_invalid("loss-empty-routes", loss_empty_routes, "終局 predicate 算為 IN_PROGRESS")

    loss_authority_route = loss_minimized_candidate()
    claim_by_id(loss_authority_route, "claim-route-closed")["status"] = "UNKNOWN"
    claim_by_id(loss_authority_route, "claim-route-authority-required")["status"] = "PASS"
    loss_authority_route["terminalAssessment"]["alternativeRoutes"][0]["status"] = "REQUIRES_AUTHORITY"
    loss_authority_route["terminalAssessment"]["requiredAuthority"] = "額外的沙盒管理權限"
    expect_invalid(
        "loss-authority-route-priority",
        loss_authority_route,
        "終局 predicate 算為 NEW_AUTHORITY_REQUIRED",
    )

    authority_required = copy.deepcopy(loss_authority_route)
    authority_required["terminalAssessment"]["status"] = "NEW_AUTHORITY_REQUIRED"
    authority_errors = validate_state(authority_required)
    if authority_errors:
        raise ValueError(f"self-test authority-terminal-valid 失敗：{authority_errors}")
    if '<section class="victory-banner"' in render_html(authority_required):
        raise ValueError("self-test authority-required-no-victory-banner 誤顯示勝利 banner")
    completed.append("authority-terminal-valid")

    loss_uncovered_outcome = loss_minimized_candidate()
    loss_uncovered_outcome["lossMinimizationAssessment"]["unacceptableOutcomeChecks"].pop()
    expect_invalid("loss-uncovered-outcome", loss_uncovered_outcome, "未覆蓋")

    loss_unknown_outcome = loss_minimized_candidate()
    loss_unknown_outcome["executionAssessment"]["outcomeStatus"] = "OUTCOME_UNKNOWN"
    expect_invalid("loss-unknown-action-outcome", loss_unknown_outcome, "終局 predicate 算為 IN_PROGRESS")

    loss_blocking_cleanup = loss_minimized_candidate()
    claim_by_id(loss_blocking_cleanup, "claim-loss-cleanup-closed")["status"] = "UNKNOWN"
    loss_blocking_cleanup["currentTruth"]["cleanupDebt"][0]["status"] = "OPEN"
    expect_invalid("loss-blocking-cleanup", loss_blocking_cleanup, "終局 predicate 算為 IN_PROGRESS")

    terminal_with_active_takeover = copy.deepcopy(state)
    claim_by_id(terminal_with_active_takeover, "claim-victory-unattainable")["status"] = "PASS"
    claim_by_id(terminal_with_active_takeover, "claim-loss-cleanup-closed")["status"] = "PASS"
    claim_by_id(terminal_with_active_takeover, "claim-route-closed")["status"] = "PASS"
    terminal_with_active_takeover["currentTruth"]["cleanupDebt"][0]["status"] = "CLOSED"
    terminal_with_active_takeover["terminalAssessment"]["alternativeRoutes"][0]["status"] = "CLOSED"
    terminal_with_active_takeover["terminalAssessment"]["status"] = "LOSS_MINIMIZED"
    expect_invalid(
        "terminal-rejects-active-takeover",
        terminal_with_active_takeover,
        "合法終局要求零 ACTIVE battlefield",
    )

    loss_no_measurement = loss_minimized_candidate()
    loss_no_measurement["lossMinimizationAssessment"]["residualLossMeasurements"] = []
    expect_invalid("loss-no-residual-measurement", loss_no_measurement, "residualLossMeasurements 不得為空")

    loss_unproven_measurement = loss_minimized_candidate()
    loss_unproven_measurement["lossMinimizationAssessment"]["residualLossMeasurements"].append(
        {
            "id": "pending-residual-readback",
            "metric": "ACTIVE_RUN_COUNT",
            "displayText": "活動執行紀錄數仍待權威回讀",
            "predicate": "FINALIZED_NO_ACTIVE_RESIDUE == true",
            "evidenceClaimIds": ["claim-main-exit"],
        }
    )
    expect_invalid(
        "loss-unproven-residual-measurement",
        loss_unproven_measurement,
        "終局 predicate 算為 IN_PROGRESS",
    )

    loss_unproven_gain = loss_minimized_candidate()
    loss_unproven_gain["lossMinimizationAssessment"]["preservedGains"] = [
        {
            "id": "pending-terminal-readback",
            "displayText": "保留尚待證實的終態結果",
            "predicate": "FINALIZED_NO_ACTIVE_RESIDUE == true",
            "evidenceClaimIds": ["claim-main-exit"],
        }
    ]
    expect_invalid("loss-unproven-preserved-gain", loss_unproven_gain, "終局 predicate 算為 IN_PROGRESS")

    false_loss_terminal = copy.deepcopy(state)
    false_loss_terminal["terminalAssessment"]["status"] = "LOSS_MINIMIZED"
    expect_invalid("loss-false-manual-status", false_loss_terminal, "終局 predicate 算為 IN_PROGRESS")

    manual_loss_result = copy.deepcopy(state)
    manual_loss_result["lossMinimizationAssessment"]["lossMinimized"] = True
    expect_invalid("loss-manual-result-field", manual_loss_result, "不在 schema 中")

    false_terminal = copy.deepcopy(state)
    false_terminal["terminalAssessment"]["status"] = "STRATEGIC_OBJECTIVE_ACHIEVED"
    expect_invalid("terminal-derived-status", false_terminal, "終局 predicate 算為 IN_PROGRESS")

    alternatives_not_exhausted = copy.deepcopy(state)
    alternatives_not_exhausted["terminalAssessment"]["status"] = "NEW_AUTHORITY_REQUIRED"
    alternatives_not_exhausted["terminalAssessment"]["requiredAuthority"] = "DB 管理權限"
    expect_invalid("authority-not-required-with-open-route", alternatives_not_exhausted, "終局 predicate 算為 IN_PROGRESS")

    unchanged_world = copy.deepcopy(state)
    unchanged_world["latestVerifiedAdvance"]["afterValue"] = unchanged_world["latestVerifiedAdvance"]["beforeValue"]
    expect_invalid("world-delta-requires-change", unchanged_world, "beforeValue 與 afterValue 必須不同")
    return f"STRATEGIC_STATE_SELF_TEST=PASS cases={','.join(completed)}"


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        for attempt in range(4):
            try:
                os.replace(temp_name, path)
                return
            except PermissionError:
                if attempt == 3:
                    raise
                time.sleep(0.05 * (2**attempt))
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def open_html_fail_soft(path: Path) -> bool:
    """Open a rendered HTML artifact without changing render success semantics."""
    resolved = path.resolve()
    try:
        if os.name == "nt" and hasattr(os, "startfile"):
            os.startfile(str(resolved))  # type: ignore[attr-defined]
            return True
        wslview = shutil.which("wslview")
        if wslview:
            subprocess.Popen(
                [wslview, str(resolved)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        if webbrowser.open_new_tab(resolved.as_uri()):
            return True
    except Exception as error:  # Browser launch is advisory; rendering already succeeded.
        print(f"[WARN] SAND_TABLE_OPEN_FAILED path={resolved} error={error}", file=sys.stderr)
        return False
    print(f"[WARN] SAND_TABLE_OPEN_FAILED path={resolved} error=no-browser-handler", file=sys.stderr)
    return False




# ---------------------------------------------------------------------------
# State construction: semantic seed -> valid schema-6 state, plus claim/front CRUD.
# Every canonical predicate below is produced by canonical_predicate(); no new
# code path hand-assembles a BATTLEFIELD/RISK/WORLD/ACTOR/SESSION/TARGET/
# CONTROL/ACTION predicate string.
# ---------------------------------------------------------------------------

STATE_TOOL_COMMANDS = ("init", "set-claim", "add-claim", "set-front", "handoff", "reprobe", "toll")
REPROBE_SAFE_LEADERS = frozenset(
    {
        "date", "git", "grep", "rg", "ls", "cat", "head", "tail", "wc",
        "cmp", "diff", "sha256sum", "md5sum", "stat", "test",
    }
)
REPROBE_SHELL_METACHARACTERS = frozenset(";|&$`><()")
REPROBE_GIT_FORBIDDEN_TOKENS = ("-c", "--exec-path", "--upload-pack", "--receive-pack")
REPROBE_GIT_FORBIDDEN_SUBCOMMANDS = frozenset(
    {"checkout", "restore", "stash", "commit", "push", "clean", "reset", "merge", "rebase"}
)
SEEDED_SOURCE_REF = "seeded: pending probe"
GATING_PROVENANCE_PATTERN = re.compile(
    r"^scribe-probe:.+@\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:?\d{2})$"
)
GATING_PROVENANCE_REFUSAL = "gating claim 需 scribe-probe 出處（--source-ref 不符文法，拒絕寫入 PASS）"
YAML_UNAVAILABLE_MESSAGE = "pyyaml 未安裝：YAML 種子不可用，請改用 JSON 種子"
YAML_SEED_SUFFIXES = {".yaml", ".yml"}
DEFAULT_CLAIM_VALIDITY_HOURS = 3
DEFAULT_ACTION_DEADLINE_MINUTES = 120
DEFAULT_ACTION_TIMEOUT_SECONDS = 60
DEFAULT_EXECUTION_DEADLINE_SECONDS = 300
DEFAULT_CULMINATION_POLICY = {
    "reanalysisMinutes": 30,
    "highRiskMinutes": 90,
    "repeatFailureLimit": 2,
}
DEFAULT_ALLOWED_NEXT_STATUSES = {
    "ACTIVE": ["COMPLETE", "BLOCKED"],
    "PENDING": ["ACTIVE", "DEFERRED"],
    "DEFERRED": ["ACTIVE", "COMPLETE"],
}
VICTORY_UNATTAINABLE_PREDICATE = "STRATEGIC_VICTORY_UNATTAINABLE_UNDER_CURRENT_CONSTRAINTS == true"


class SeedError(ValueError):
    """A semantic seed cannot be expanded; the message names the offending field."""


class YamlSeedUnavailable(Exception):
    """A YAML seed was supplied on a machine without pyyaml installed."""


def isoformat_seconds(moment: datetime) -> str:
    return moment.replace(microsecond=0).isoformat()


def parse_iso_argument(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as error:
        raise SeedError(f"{field} 不是合法 ISO 8601：{value}") from error
    if parsed.tzinfo is None:
        raise SeedError(f"{field} 必須包含時區")
    return parsed


def seed_value(container: Any, key: str, prefix: str, default: Any = None) -> Any:
    if not isinstance(container, dict):
        raise SeedError(f"{prefix} 必須是 object")
    if key not in container or container[key] is None:
        if default is None and key not in container:
            raise SeedError(f"{prefix}.{key} 為必要欄位")
        return copy.deepcopy(default)
    return container[key]


def seed_text(container: Any, key: str, prefix: str, default: str | None = None) -> str:
    if isinstance(container, dict) and key not in container and default is not None:
        return default
    value = seed_value(container, key, prefix, default)
    if not isinstance(value, str) or (not value.strip() and default != ""):
        raise SeedError(f"{prefix}.{key} 必須是非空字串")
    return value


def seed_list(container: Any, key: str, prefix: str, default: list | None = None, nonempty: bool = False) -> list:
    if isinstance(container, dict) and key not in container and default is not None:
        values = list(default)
    else:
        values = seed_value(container, key, prefix, default)
    if not isinstance(values, list):
        raise SeedError(f"{prefix}.{key} 必須是 array")
    if nonempty and not values:
        raise SeedError(f"{prefix}.{key} 不得為空")
    return values


def seed_mapping(container: Any, key: str, prefix: str, default: dict | None = None) -> dict:
    if isinstance(container, dict) and key not in container and default is not None:
        return copy.deepcopy(default)
    value = seed_value(container, key, prefix, default)
    if not isinstance(value, dict):
        raise SeedError(f"{prefix}.{key} 必須是 object")
    return value


def seed_number(container: Any, key: str, prefix: str, default: Any = None) -> Any:
    if isinstance(container, dict) and key not in container and default is not None:
        return default
    value = seed_value(container, key, prefix, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise SeedError(f"{prefix}.{key} 必須是數值")
    return value


def load_seed(path: Path) -> dict[str, Any]:
    """Read a semantic seed. JSON always works; YAML needs an optional pyyaml."""
    if path.suffix.lower() in YAML_SEED_SUFFIXES:
        try:
            import yaml
        except ImportError as error:
            raise YamlSeedUnavailable(YAML_UNAVAILABLE_MESSAGE) from error
        try:
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            raise SeedError(f"無法讀取 YAML 種子：{error}") from error
    else:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SeedError(f"無法讀取 JSON 種子：{error}") from error
    if not isinstance(value, dict):
        raise SeedError("種子根節點必須是 JSON/YAML object")
    return value


def expand_seed(seed: dict[str, Any], now: datetime) -> dict[str, Any]:
    """Expand a semantic seed into a schema-6 state whose claims are born UNKNOWN.

    The single exception the validator forces: a campaign that is not in a legal
    terminal posture must carry exactly one ACTIVE MAIN battlefield, and an ACTIVE
    battlefield requires an authoritative PASS entry claim. That one claim comes
    from a seed-declared probe observation whose sourceRef must satisfy the same
    scribe-probe grammar `set-claim` enforces on gating claims.
    """
    now_text = isoformat_seconds(now)
    valid_until_text = isoformat_seconds(now + timedelta(hours=DEFAULT_CLAIM_VALIDITY_HOURS))
    mission_id = seed_text(seed, "missionId", "seed")
    objective_seed = seed_mapping(seed, "objective", "seed")

    claims: list[dict[str, Any]] = []
    predicate_owner: dict[str, str] = {}
    claim_ids: set[str] = set()

    def add_claim(
        claim_id: str,
        source_type: str,
        predicate: str,
        *,
        status: str = "UNKNOWN",
        source_ref: str = SEEDED_SOURCE_REF,
        observed_at: str | None = None,
    ) -> str:
        if claim_id in claim_ids:
            raise SeedError(f"claim id 重複：{claim_id}")
        if predicate in predicate_owner:
            raise SeedError(
                f"predicate 重複：{predicate}（{predicate_owner[predicate]} 與 {claim_id}）"
            )
        claim_ids.add(claim_id)
        predicate_owner[predicate] = claim_id
        claims.append(
            {
                "id": claim_id,
                "sourceType": source_type,
                "sourceRef": source_ref,
                "observedAt": observed_at or now_text,
                "validUntil": valid_until_text,
                "authorityRank": 1,
                "predicate": predicate,
                "status": status,
            }
        )
        return claim_id

    def add_observed_claim(
        claim_id: str, source_type_default: str, predicate: str, observation: Any, prefix: str
    ) -> str:
        source_ref = seed_text(observation, "sourceRef", prefix)
        if not GATING_PROVENANCE_PATTERN.match(source_ref):
            raise SeedError(
                f"{prefix}.sourceRef 必須符合 scribe-probe 出處文法（PASS 出生只接受探針出處）：{source_ref}"
            )
        observed_at = observation.get("observedAt")
        if observed_at is not None:
            moment = parse_iso_argument(observed_at, f"{prefix}.observedAt")
            if moment > now:
                raise SeedError(f"{prefix}.observedAt 不得晚於 --now")
            observed_at = isoformat_seconds(moment)
        return add_claim(
            claim_id,
            seed_text(observation, "sourceType", prefix, "DB"),
            predicate,
            status="PASS",
            source_ref=source_ref,
            observed_at=observed_at,
        )

    victory_criteria: list[dict[str, Any]] = []
    for index, item in enumerate(seed_list(objective_seed, "victoryCriteria", "seed.objective", nonempty=True)):
        prefix = f"seed.objective.victoryCriteria[{index}]"
        criterion_id = seed_text(item, "id", prefix)
        claim_id = add_claim(
            f"claim-victory-{criterion_id}",
            seed_text(item, "sourceType", prefix, "DB"),
            seed_text(item, "predicate", prefix),
        )
        victory_criteria.append(
            {
                "id": criterion_id,
                "displayText": seed_text(item, "displayText", prefix),
                "predicate": seed_text(item, "predicate", prefix),
                "status": "UNKNOWN",
                "evidenceClaimIds": [claim_id],
            }
        )

    front_seeds = seed_list(seed, "battlefields", "seed", nonempty=True)
    main_indexes = [
        index
        for index, front in enumerate(front_seeds)
        if isinstance(front, dict) and front.get("mainEffort") is True
    ]
    if len(main_indexes) != 1:
        raise SeedError(
            "seed.battlefields 必須恰有一個 mainEffort: true 的戰場（validator 要求非終局狀態恰有一個 ACTIVE MAIN）"
        )

    battlefields: list[dict[str, Any]] = []
    front_plans: list[dict[str, Any]] = []
    for index, front in enumerate(front_seeds):
        prefix = f"seed.battlefields[{index}]"
        front_id = seed_text(front, "id", prefix)
        entry_state = seed_text(front, "entryState", prefix)
        terminal_state = seed_text(front, "terminalState", prefix)
        mutation_scope = seed_list(front, "mutationScope", prefix, default=[])
        defer_reason = seed_text(front, "deferReason", prefix, "")
        is_main = index in main_indexes
        status = "ACTIVE" if is_main else ("DEFERRED" if defer_reason.strip() else "PENDING")

        entry_predicate = canonical_predicate(
            "BATTLEFIELD[{}].ENTRY[{}] == {}", front_id, entry_state, True
        )
        exit_predicate = canonical_predicate(
            "BATTLEFIELD[{}].EXIT[{}] == {}", front_id, terminal_state, True
        )
        pivot_predicate = canonical_predicate("BATTLEFIELD[{}].PIVOT_TRIGGERED == {}", front_id, True)

        entry_claim_id = f"claim-front-{front_id}-entry"
        entry_observation = front.get("entryObservation")
        if is_main:
            if not isinstance(entry_observation, dict):
                raise SeedError(
                    f"{prefix}.entryObservation 為必要欄位：ACTIVE 主攻的 entry claim 必須是探針背書的權威 PASS"
                )
            add_observed_claim(
                entry_claim_id, "DB", entry_predicate, entry_observation, f"{prefix}.entryObservation"
            )
        else:
            add_claim(entry_claim_id, "DB", entry_predicate)
        exit_claim_id = add_claim(f"claim-front-{front_id}-exit", "DB", exit_predicate)
        add_claim(f"claim-front-{front_id}-pivot", "DB", pivot_predicate)

        recovery_seed = seed_mapping(front, "recovery", prefix, default={})
        readiness_predicate = seed_text(
            recovery_seed, "readinessPredicate", f"{prefix}.recovery", "NO_MUTATION_RECOVERY_REQUIRED == true"
        )
        recovery_observation = recovery_seed.get("observation")
        if isinstance(recovery_observation, dict) and not is_main:
            raise SeedError(
                f"{prefix}.recovery.observation 僅限主攻前線：非主攻前線請於升級 ACTIVE 前以 set-claim 帶探針出處入冊"
            )
        recovery_claim_ids: list[str] = []
        if mutation_scope:
            recovery_claim_id = f"claim-front-{front_id}-recovery"
            if isinstance(recovery_observation, dict):
                add_observed_claim(
                    recovery_claim_id,
                    "DB",
                    readiness_predicate,
                    recovery_observation,
                    f"{prefix}.recovery.observation",
                )
                recovery_status = "READY"
            else:
                add_claim(recovery_claim_id, "DB", readiness_predicate)
                recovery_status = "NOT_READY"
            recovery_claim_ids = [recovery_claim_id]
        else:
            recovery_status = "NOT_REQUIRED"
        if is_main and recovery_status == "NOT_READY":
            raise SeedError(
                f"{prefix}.recovery.observation 為必要欄位：帶 mutationScope 的 ACTIVE 主攻要求 recovery READY"
            )

        battlefields.append(
            {
                "id": front_id,
                "operationType": seed_text(
                    front, "operationType", prefix, "DECISIVE" if is_main else "SHAPING"
                ),
                "effort": "MAIN" if is_main else "SUPPORT",
                "status": status,
                "objective": seed_text(front, "objective", prefix),
                "entryState": entry_state,
                "terminalState": terminal_state,
                "entryClaimId": entry_claim_id,
                "exitClaimId": exit_claim_id,
                "evidenceClaimIds": [entry_claim_id, exit_claim_id],
                "mutationScope": mutation_scope,
                "recovery": {
                    "status": recovery_status,
                    "action": seed_text(
                        recovery_seed,
                        "action",
                        f"{prefix}.recovery",
                        "結果未知時先回讀權威狀態，不重送同一動作",
                    ),
                    "steps": seed_list(recovery_seed, "steps", f"{prefix}.recovery", default=[]),
                    "readinessPredicate": readiness_predicate,
                    "successPredicate": seed_text(
                        recovery_seed,
                        "successPredicate",
                        f"{prefix}.recovery",
                        "OUTCOME_CLASSIFIED_AS_PASS_FAIL_OR_UNKNOWN",
                    ),
                    "stopCondition": seed_text(
                        recovery_seed, "stopCondition", f"{prefix}.recovery", "任何來源顯示 mutation 已送出"
                    ),
                    "evidenceClaimIds": recovery_claim_ids,
                },
                "allowedNextStatuses": seed_list(
                    front, "allowedNextStatuses", prefix, default=DEFAULT_ALLOWED_NEXT_STATUSES[status]
                ),
                "deferReason": defer_reason,
                "owner": seed_text(front, "owner", prefix),
                "timeBudgetMinutes": seed_number(front, "timeBudgetMinutes", prefix, 60),
            }
        )
        front_plans.append(
            {
                "frontId": front_id,
                "status": status,
                "mutationScope": mutation_scope,
                "recoveryStatus": recovery_status,
                "expectedVictoryCriterionIds": seed_list(
                    front, "expectedVictoryCriterionIds", prefix, default=[]
                ),
                "remainingTransitions": seed_number(front, "remainingTransitions", prefix, 1),
                "costMinutes": seed_number(front, "costMinutes", prefix, 30),
            }
        )

    risk_register: list[dict[str, Any]] = []
    for index, item in enumerate(seed_list(seed, "risks", "seed", default=[])):
        prefix = f"seed.risks[{index}]"
        risk_id = seed_text(item, "id", prefix)
        affected_front_id = seed_text(item, "affectedFrontId", prefix)
        probability = seed_number(item, "probability", prefix)
        impact = seed_number(item, "impact", prefix)
        status_checks: dict[str, Any] = {}
        for risk_status in ("CONTROLLED", "ACCEPTED", "CLOSED"):
            claim_id = add_claim(
                f"claim-risk-{risk_id}-{risk_status.lower()}",
                "STATIC",
                canonical_predicate(
                    "RISK[{}]@FRONT[{}].STATUS == {}", risk_id, affected_front_id, risk_status
                ),
            )
            status_checks[risk_status] = {"evidenceClaimIds": [claim_id]}
        risk_register.append(
            {
                "id": risk_id,
                "affectedFrontId": affected_front_id,
                "protectedAssetId": seed_text(item, "protectedAssetId", prefix),
                "threat": seed_text(item, "threat", prefix),
                "status": "OPEN",
                "probability": probability,
                "impact": impact,
                "score": probability * impact,
                "unacceptableThreshold": seed_number(item, "unacceptableThreshold", prefix),
                "guard": seed_text(item, "guard", prefix),
                "stopCondition": seed_text(item, "stopCondition", prefix),
                "recoveryAction": seed_text(item, "recoveryAction", prefix),
                "statusChecks": status_checks,
            }
        )

    alternative_routes: list[dict[str, Any]] = []
    for index, item in enumerate(seed_list(seed, "alternativeRoutes", "seed", default=[])):
        prefix = f"seed.alternativeRoutes[{index}]"
        route_id = seed_text(item, "id", prefix)
        status_checks = {}
        for route_status in ("CLOSED", "UNSAFE", "REQUIRES_AUTHORITY"):
            predicate = canonical_predicate("ROUTE[{}].STATUS == {}", route_id, route_status)
            claim_id = add_claim(
                f"claim-route-{route_id}-{route_status.lower().replace('_', '-')}", "STATIC", predicate
            )
            status_checks[route_status] = {"predicate": predicate, "evidenceClaimIds": [claim_id]}
        alternative_routes.append(
            {
                "id": route_id,
                "status": "OPEN",
                "reason": seed_text(item, "reason", prefix),
                "statusChecks": status_checks,
            }
        )

    unacceptable_outcomes = seed_list(objective_seed, "unacceptableOutcomes", "seed.objective", default=[])
    outcome_checks: list[dict[str, Any]] = []
    for index, outcome in enumerate(unacceptable_outcomes):
        if not isinstance(outcome, str) or not outcome.strip():
            raise SeedError(f"seed.objective.unacceptableOutcomes[{index}] 必須是非空字串")
        predicate = canonical_predicate("UNACCEPTABLE_OUTCOME[{}].ABSENT == {}", outcome, True)
        claim_id = add_claim(f"claim-loss-outcome-{index + 1}", "LOG", predicate)
        outcome_checks.append(
            {"outcome": outcome, "predicate": predicate, "evidenceClaimIds": [claim_id]}
        )

    residual_measurements: list[dict[str, Any]] = []
    for index, item in enumerate(
        seed_list(seed, "residualLossMeasurements", "seed", nonempty=True)
    ):
        prefix = f"seed.residualLossMeasurements[{index}]"
        measurement_id = seed_text(item, "id", prefix)
        predicate = seed_text(item, "predicate", prefix)
        claim_id = add_claim(f"claim-loss-residual-{measurement_id}", "DB", predicate)
        residual_measurements.append(
            {
                "id": measurement_id,
                "metric": seed_text(item, "metric", prefix),
                "displayText": seed_text(item, "displayText", prefix),
                "predicate": predicate,
                "evidenceClaimIds": [claim_id],
            }
        )
    victory_unattainable_claim = add_claim(
        "claim-loss-victory-unattainable", "DB", VICTORY_UNATTAINABLE_PREDICATE
    )

    takeover_block: dict[str, Any] | None = None
    if "takeoverReadiness" in seed:
        readiness_seed = seed_mapping(seed, "takeoverReadiness", "seed")
        action_id = seed_text(readiness_seed, "actionId", "seed.takeoverReadiness")
        actor_id = seed_text(readiness_seed, "actorId", "seed.takeoverReadiness")
        session_id = seed_text(readiness_seed, "sessionId", "seed.takeoverReadiness")
        context_id = seed_text(readiness_seed, "contextId", "seed.takeoverReadiness")
        scope_identity = seed_text(readiness_seed, "scopeIdentity", "seed.takeoverReadiness")
        actor_claim = add_claim(
            "claim-readiness-actor", "UI", canonical_predicate("ACTOR[{}].VERIFIED == {}", actor_id, True)
        )
        session_claim = add_claim(
            "claim-readiness-session",
            "UI",
            canonical_predicate("SESSION[{}].CONTEXT[{}].READY == {}", session_id, context_id, True),
        )
        target_claim = add_claim(
            "claim-readiness-target",
            "DB",
            canonical_predicate("TARGET[{}].CARDINALITY == {}", scope_identity, 1),
        )
        control_claim = add_claim(
            "claim-readiness-control",
            "UI",
            canonical_predicate("CONTROL[{}].VISIBLE_ENABLED_UNOBSTRUCTED == {}", scope_identity, True),
        )
        authority_claim = add_claim(
            "claim-readiness-authority",
            "API",
            canonical_predicate("ACTOR[{}].AUTHORIZED_FOR[{}] == {}", actor_id, action_id, True),
        )
        prerequisite_checks: list[dict[str, Any]] = []
        for requirement_id in seed_list(
            readiness_seed, "prerequisiteIds", "seed.takeoverReadiness", default=["target-ready"], nonempty=True
        ):
            claim_id = add_claim(
                f"claim-readiness-prereq-{requirement_id}",
                "DB",
                canonical_predicate(
                    "ACTION[{}].REQUIREMENT[{}].SATISFIED == {}", action_id, requirement_id, True
                ),
            )
            prerequisite_checks.append(
                {"requirementId": requirement_id, "evidenceClaimIds": [claim_id]}
            )

        executable_seed = seed_mapping(readiness_seed, "executable", "seed.takeoverReadiness")
        verifiable_seed = seed_mapping(readiness_seed, "verifiable", "seed.takeoverReadiness")
        baseline_checks: list[dict[str, Any]] = []
        delta_contracts: list[dict[str, Any]] = []
        for index, item in enumerate(
            seed_list(verifiable_seed, "worldDeltaContracts", "seed.takeoverReadiness.verifiable", nonempty=True)
        ):
            prefix = f"seed.takeoverReadiness.verifiable.worldDeltaContracts[{index}]"
            dimension = seed_text(item, "dimension", prefix)
            if "beforeValue" not in item or "afterValue" not in item:
                raise SeedError(f"{prefix} 必須同時提供 beforeValue 與 afterValue")
            baseline_id = f"baseline-{dimension}"
            claim_id = add_claim(
                f"claim-baseline-{dimension}",
                "DB",
                canonical_predicate(
                    "WORLD[{}].DIMENSION[{}] == {}", scope_identity, dimension, item["beforeValue"]
                ),
            )
            baseline_checks.append({"id": baseline_id, "evidenceClaimIds": [claim_id]})
            delta_contracts.append(
                {
                    "scopeIdentity": scope_identity,
                    "dimension": dimension,
                    "beforeValue": item["beforeValue"],
                    "afterValue": item["afterValue"],
                    "baselineCheckId": baseline_id,
                }
            )

        deadline_minutes = seed_number(
            verifiable_seed, "deadlineMinutes", "seed.takeoverReadiness.verifiable", DEFAULT_ACTION_DEADLINE_MINUTES
        )
        takeover_block = {
            "actionId": action_id,
            "actorId": actor_id,
            "sessionId": session_id,
            "contextId": context_id,
            "scopeIdentity": scope_identity,
            "operable": {
                "status": "UNKNOWN",
                "evidence": seed_list(
                    readiness_seed,
                    "operableEvidence",
                    "seed.takeoverReadiness",
                    default=["冷啟動：三道接管門尚未取得探針證據"],
                    nonempty=True,
                ),
                "actorCheck": {"evidenceClaimIds": [actor_claim]},
                "sessionCheck": {"evidenceClaimIds": [session_claim]},
                "targetCheck": {"evidenceClaimIds": [target_claim]},
                "controlCheck": {
                    "requiredConditions": ["VISIBLE", "ENABLED", "UNOBSTRUCTED"],
                    "evidenceClaimIds": [control_claim],
                },
            },
            "executable": {
                "status": "UNKNOWN",
                "objective": seed_text(executable_seed, "objective", "seed.takeoverReadiness.executable"),
                "authorizedActor": actor_id,
                "authorityCheck": {"evidenceClaimIds": [authority_claim]},
                "prerequisiteChecks": prerequisite_checks,
                "steps": seed_list(
                    executable_seed, "steps", "seed.takeoverReadiness.executable", nonempty=True
                ),
                "prohibitedActions": seed_list(
                    executable_seed,
                    "prohibitedActions",
                    "seed.takeoverReadiness.executable",
                    default=["不得在證據未確認前重送同一動作"],
                    nonempty=True,
                ),
                "sideEffects": seed_list(
                    executable_seed,
                    "sideEffects",
                    "seed.takeoverReadiness.executable",
                    default=["送出一次受限的目標動作"],
                    nonempty=True,
                ),
                "timeoutSeconds": seed_number(
                    executable_seed,
                    "timeoutSeconds",
                    "seed.takeoverReadiness.executable",
                    DEFAULT_ACTION_TIMEOUT_SECONDS,
                ),
                "stopCondition": seed_text(
                    executable_seed, "stopCondition", "seed.takeoverReadiness.executable"
                ),
                "recoveryAction": seed_text(
                    executable_seed, "recoveryAction", "seed.takeoverReadiness.executable"
                ),
            },
            "verifiable": {
                "status": "UNKNOWN",
                "expectedWorldDelta": seed_list(
                    verifiable_seed, "expectedWorldDelta", "seed.takeoverReadiness.verifiable", nonempty=True
                ),
                "expectedWorldDeltaContracts": delta_contracts,
                "baselineChecks": baseline_checks,
                "evidenceSources": seed_list(
                    verifiable_seed,
                    "evidenceSources",
                    "seed.takeoverReadiness.verifiable",
                    default=["authoritative state"],
                    nonempty=True,
                ),
                "successPredicates": seed_list(
                    verifiable_seed, "successPredicates", "seed.takeoverReadiness.verifiable", nonempty=True
                ),
                "failurePredicates": seed_list(
                    verifiable_seed, "failurePredicates", "seed.takeoverReadiness.verifiable", nonempty=True
                ),
                "unknownOutcomeRule": "NO_DECISIVE_EVIDENCE_BY_DEADLINE",
                "deadlineAt": isoformat_seconds(now + timedelta(minutes=deadline_minutes)),
            },
            "result": "NOT_READY",
        }

    unresolved_victory_ids = {criterion["id"] for criterion in victory_criteria}
    victory_id_set = set(unresolved_victory_ids)
    candidates: list[dict[str, Any]] = []
    for plan in front_plans:
        front_id = plan["frontId"]
        expected_ids = plan["expectedVictoryCriterionIds"]
        unknown_ids = [value for value in expected_ids if value not in victory_id_set]
        if unknown_ids:
            raise SeedError(
                f"seed.battlefields[{front_id}].expectedVictoryCriterionIds 指向不存在的 victory criterion：{unknown_ids}"
            )
        affected = [
            risk
            for risk in risk_register
            if risk["affectedFrontId"] == front_id and risk["status"] != "CLOSED"
        ]
        risk_score = max((risk["score"] for risk in affected), default=0)
        blocking_risk_ids = sorted(
            risk["id"]
            for risk in risk_register
            if risk["affectedFrontId"] == front_id
            and risk["status"] == "OPEN"
            and risk["score"] >= risk["unacceptableThreshold"]
        )
        recovery_ready = not plan["mutationScope"] or plan["recoveryStatus"] in {"READY", "NOT_REQUIRED"}
        eligible = (
            plan["status"] not in {"COMPLETE", "DEFERRED"}
            and not blocking_risk_ids
            and recovery_ready
        )
        if eligible:
            reason = ""
        elif plan["status"] in {"COMPLETE", "DEFERRED"}:
            reason = f"戰場狀態為 {plan['status']}，不列入主攻候選"
        elif blocking_risk_ids:
            reason = f"未控制且達門檻的風險：{', '.join(blocking_risk_ids)}"
        else:
            reason = "mutation 戰場的 recovery 尚未 READY"
        unmet = len(unresolved_victory_ids - set(expected_ids))
        candidates.append(
            {
                "frontId": front_id,
                "eligible": eligible,
                "expectedVictoryCriterionIds": list(expected_ids),
                "unmetVictoryCriteria": unmet,
                "remainingTransitions": plan["remainingTransitions"],
                "riskScore": risk_score,
                "costMinutes": plan["costMinutes"],
                "blockingRiskIds": blocking_risk_ids,
                "totalScore": unmet * 100
                + plan["remainingTransitions"] * 10
                + risk_score * 5
                + plan["costMinutes"],
                "ineligibilityReason": reason,
            }
        )

    eligible_candidates = [candidate for candidate in candidates if candidate["eligible"]]
    seed_priority_order = [
        item
        for item in seed_list(objective_seed, "priorityOrder", "seed.objective", default=[])
        if isinstance(item, str) and item.strip()
    ]
    minimum_candidate_ids = select_main_candidate_ids(eligible_candidates, seed_priority_order)
    active_front_id = battlefields[main_indexes[0]]["id"]
    # A newborn pivot claim is UNKNOWN, never FAIL, so clarity can only be CLEAR
    # through the terminal route — which an ACTIVE MAIN front rules out.
    terminal_route = False
    cold_unclear_causes: list[str] = []
    if not minimum_candidate_ids:
        cold_unclear_causes.append("NO_ELIGIBLE_CANDIDATE")
    elif len(minimum_candidate_ids) > 1:
        cold_unclear_causes.append("AMBIGUOUS_CANDIDATE")
    cold_unclear_causes.append("PIVOT_UNPROBED")
    cold_unclear_causes.sort()
    decision_seed = seed_mapping(seed, "decision", "seed")

    state: dict[str, Any] = {
        "schemaVersion": 6,
        "missionId": mission_id,
        "updatedAt": now_text,
        "strategicObjective": {
            "revision": seed_number(objective_seed, "revision", "seed.objective", 1),
            "approvedAt": now_text,
            "purpose": seed_text(objective_seed, "purpose", "seed.objective"),
            "desiredEndState": seed_list(objective_seed, "desiredEndState", "seed.objective", nonempty=True),
            "worldDimensions": seed_list(objective_seed, "worldDimensions", "seed.objective", nonempty=True),
            "protectedAssets": seed_list(objective_seed, "protectedAssets", "seed.objective", nonempty=True),
            "victoryCriteria": victory_criteria,
            "victoryEvidence": seed_list(objective_seed, "victoryEvidence", "seed.objective", nonempty=True),
            "constraints": seed_list(objective_seed, "constraints", "seed.objective", default=[]),
            "unacceptableOutcomes": unacceptable_outcomes,
            **(
                {"priorityOrder": seed_priority_order}
                if seed_priority_order
                else {}
            ),
        },
        "plainBriefing": seed_mapping(seed, "plainBriefing", "seed"),
        "currentTruth": {
            "worldState": seed_mapping(seed, "worldState", "seed"),
            "evidenceClaims": claims,
            "observerHealth": [],
            "cleanupDebt": [],
        },
        "riskRegister": risk_register,
        "blockers": [],
        "battlefields": battlefields,
        "decision": {
            "activeFrontId": active_front_id,
            "chosenTactic": seed_text(decision_seed, "chosenTactic", "seed.decision"),
            "nextAction": seed_text(decision_seed, "nextAction", "seed.decision"),
            "contribution": seed_text(decision_seed, "contribution", "seed.decision", "DIRECT_ADVANCE"),
            "rationale": seed_text(decision_seed, "rationale", "seed.decision"),
            "pivotCondition": seed_text(decision_seed, "pivotCondition", "seed.decision"),
            "pivotClaimId": f"claim-front-{active_front_id}-pivot",
            "candidates": candidates,
        },
        "strategicClarity": {
            "status": "CLEAR" if terminal_route else "UNCLEAR",
            "candidateMainEffortIds": minimum_candidate_ids,
            "unresolvedDecisions": [],
            "unclearCauses": cold_unclear_causes,
            "route": "TERMINAL" if terminal_route else "OPERATOR_RESOLVE",
            "wayfinderMapPath": seed_text(
                seed, "wayfinderMapPath", "seed", f".claude/wayfinder/{mission_id}.md"
            ),
        },
        "progress": {
            "lastWorldStateChangeAt": now_text,
            "activeFrontStartedAt": now_text,
            "sameFailureFingerprintCount": 0,
            "alternateReady": False,
            "culminationPolicy": seed_mapping(
                seed, "culminationPolicy", "seed", default=DEFAULT_CULMINATION_POLICY
            ),
            "culminationRisk": "LOW",
        },
        "executionAssessment": {
            "mode": "AUTONOMOUS",
            "automationActuatorStatus": "UNKNOWN",
            "outcomeStatus": "NOT_ATTEMPTED",
            "targetIdentity": "UNKNOWN",
            "actorIdentity": "UNKNOWN",
            "actionContract": "UNKNOWN",
            "mutationObserved": False,
            "worldStateChanged": False,
            "attemptCount": 0,
            "sameFailureFingerprintCount": 0,
            "deadlineSeconds": DEFAULT_EXECUTION_DEADLINE_SECONDS,
            "deadlineExceeded": False,
            "failureFingerprint": "",
        },
        "intervention": {
            "status": "NOT_REQUIRED",
            "mode": "NONE",
            "phase": "NONE",
            "requestedAction": "",
            "reason": "",
            "returnOfControl": "",
        },
        "lossMinimizationAssessment": {
            "victoryUnattainable": {
                "predicate": VICTORY_UNATTAINABLE_PREDICATE,
                "evidenceClaimIds": [victory_unattainable_claim],
            },
            "unacceptableOutcomeChecks": outcome_checks,
            "residualLossMeasurements": residual_measurements,
            "preservedGains": [],
        },
        "terminalAssessment": {
            "status": "IN_PROGRESS",
            "requiredAuthority": "",
            "alternativeRoutes": alternative_routes,
        },
        "latestVerifiedAdvance": None,
    }
    if takeover_block is not None:
        state["takeoverReadiness"] = takeover_block
    state["progress"]["culminationRisk"] = derive_culmination_risk(state)
    return state


def derive_culmination_risk(state: dict[str, Any]) -> str:
    """Recompute the one receipt that moves when state.updatedAt moves."""
    progress = state.get("progress", {})
    policy = progress.get("culminationPolicy", {})
    reanalysis = policy.get("reanalysisMinutes")
    high_risk = policy.get("highRiskMinutes")
    repeat_limit = policy.get("repeatFailureLimit")
    repeated = progress.get("sameFailureFingerprintCount")
    alternate_ready = progress.get("alternateReady")
    elapsed = None
    try:
        started = datetime.fromisoformat(str(progress.get("activeFrontStartedAt")).replace("Z", "+00:00"))
        updated = datetime.fromisoformat(str(state.get("updatedAt")).replace("Z", "+00:00"))
        if started.tzinfo is not None and updated.tzinfo is not None and started <= updated:
            elapsed = (updated - started).total_seconds() / 60
    except ValueError:
        elapsed = None
    if elapsed is not None and isinstance(high_risk, (int, float)) and elapsed >= high_risk:
        return "HIGH"
    if (
        isinstance(repeated, int)
        and isinstance(repeat_limit, int)
        and repeated >= repeat_limit
        and alternate_ready is False
    ):
        return "HIGH"
    if (elapsed is not None and isinstance(reanalysis, (int, float)) and elapsed >= reanalysis) or (
        isinstance(repeated, int) and isinstance(repeat_limit, int) and repeated >= repeat_limit
    ):
        return "MEDIUM"
    return "LOW"


def gating_claim_ids(state: dict[str, Any]) -> set[str]:
    """Claims that open a decision gate: battlefield entry/exit, pivot, victory evidence."""
    gating: set[str] = set()
    for front in state.get("battlefields", []):
        if not isinstance(front, dict):
            continue
        for key in ("entryClaimId", "exitClaimId"):
            value = front.get(key)
            if isinstance(value, str) and value:
                gating.add(value)
    pivot_claim_id = state.get("decision", {}).get("pivotClaimId")
    if isinstance(pivot_claim_id, str) and pivot_claim_id:
        gating.add(pivot_claim_id)
    for criterion in state.get("strategicObjective", {}).get("victoryCriteria", []):
        if not isinstance(criterion, dict):
            continue
        for value in criterion.get("evidenceClaimIds", []) or []:
            if isinstance(value, str) and value:
                gating.add(value)
    return gating


def commit_state(state: dict[str, Any], path: Path) -> int:
    """Validate the whole file in memory; write only when it is valid."""
    errors = validate_state(state)
    if errors:
        for error in errors:
            print(f"[FAIL] {error}", file=sys.stderr)
        return 1
    atomic_write(path, json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    return 0


def resolve_now(value: str | None) -> datetime:
    if value:
        return parse_iso_argument(value, "--now")
    return datetime.now().astimezone().replace(microsecond=0)


def advance_updated_at(state: dict[str, Any], observed_at: datetime) -> None:
    """Carry state.updatedAt forward with a later observation and re-derive its receipt."""
    current = state.get("updatedAt")
    try:
        current_moment = datetime.fromisoformat(str(current).replace("Z", "+00:00"))
    except ValueError:
        current_moment = None
    if current_moment is None or observed_at > current_moment:
        state["updatedAt"] = isoformat_seconds(observed_at)
    state.setdefault("progress", {})["culminationRisk"] = derive_culmination_risk(state)


def run_init(arguments: argparse.Namespace) -> int:
    output: Path = arguments.out
    if output.exists() and not arguments.force:
        print(f"[FAIL] 輸出路徑已存在：{output}；加上 --force 才覆寫", file=sys.stderr)
        return 1
    now = resolve_now(arguments.now)
    state = expand_seed(load_seed(arguments.seed), now)
    code = commit_state(state, output)
    if code != 0:
        return code
    print(
        f"STATE_INITIALIZED mission={state['missionId']} "
        f"claims={len(state['currentTruth']['evidenceClaims'])} "
        f"fronts={len(state['battlefields'])}"
    )
    return 0


def run_set_claim(arguments: argparse.Namespace) -> int:
    state = copy.deepcopy(load_state(arguments.state))
    claim = next(
        (
            item
            for item in state.get("currentTruth", {}).get("evidenceClaims", [])
            if isinstance(item, dict) and item.get("id") == arguments.claim_id
        ),
        None,
    )
    if claim is None:
        print(f"[FAIL] 找不到 evidence claim：{arguments.claim_id}", file=sys.stderr)
        return 1
    if arguments.status == "PASS" and arguments.claim_id in gating_claim_ids(state):
        if not GATING_PROVENANCE_PATTERN.match(arguments.source_ref):
            print(GATING_PROVENANCE_REFUSAL, file=sys.stderr)
            return 1
    observed_at = resolve_now(arguments.observed_at)
    valid_until = (
        parse_iso_argument(arguments.valid_until, "--valid-until")
        if arguments.valid_until
        else observed_at + timedelta(hours=DEFAULT_CLAIM_VALIDITY_HOURS)
    )
    claim["status"] = arguments.status
    claim["sourceRef"] = arguments.source_ref
    claim["observedAt"] = isoformat_seconds(observed_at)
    claim["validUntil"] = isoformat_seconds(valid_until)
    advance_updated_at(state, observed_at)
    code = commit_state(state, arguments.state)
    if code != 0:
        return code
    print(f"CLAIM_UPDATED id={arguments.claim_id} status={arguments.status} state={arguments.state}")
    return 0


def run_add_claim(arguments: argparse.Namespace) -> int:
    state = copy.deepcopy(load_state(arguments.state))
    if arguments.json:
        try:
            payload = json.loads(arguments.json)
        except json.JSONDecodeError as error:
            print(f"[FAIL] --json 不是合法 JSON：{error}", file=sys.stderr)
            return 1
        if not isinstance(payload, dict):
            print("[FAIL] --json 必須是 object", file=sys.stderr)
            return 1
    else:
        payload = {}
    observed_at = resolve_now(arguments.observed_at or payload.get("observedAt"))
    valid_until = (
        parse_iso_argument(arguments.valid_until, "--valid-until")
        if arguments.valid_until
        else parse_iso_argument(payload["validUntil"], "--json.validUntil")
        if payload.get("validUntil")
        else observed_at + timedelta(hours=DEFAULT_CLAIM_VALIDITY_HOURS)
    )
    claim = {
        "id": arguments.id or payload.get("id"),
        "sourceType": arguments.source_type or payload.get("sourceType"),
        "sourceRef": arguments.source_ref or payload.get("sourceRef"),
        "observedAt": isoformat_seconds(observed_at),
        "validUntil": isoformat_seconds(valid_until),
        "authorityRank": arguments.authority_rank
        if arguments.authority_rank is not None
        else payload.get("authorityRank", 1),
        "predicate": arguments.predicate or payload.get("predicate"),
        "status": arguments.status or payload.get("status", "UNKNOWN"),
    }
    missing = [key for key in ("id", "sourceType", "sourceRef", "predicate") if not claim.get(key)]
    if missing:
        print(f"[FAIL] add-claim 缺少必要欄位：{', '.join(missing)}", file=sys.stderr)
        return 1
    claims = state.setdefault("currentTruth", {}).setdefault("evidenceClaims", [])
    if any(isinstance(item, dict) and item.get("id") == claim["id"] for item in claims):
        print(f"[FAIL] evidence claim id 已存在：{claim['id']}", file=sys.stderr)
        return 1
    if claim["status"] == "PASS" and claim["id"] in gating_claim_ids(state):
        if not GATING_PROVENANCE_PATTERN.match(str(claim["sourceRef"])):
            print(GATING_PROVENANCE_REFUSAL, file=sys.stderr)
            return 1
    claims.append(claim)
    advance_updated_at(state, observed_at)
    code = commit_state(state, arguments.state)
    if code != 0:
        return code
    print(f"CLAIM_ADDED id={claim['id']} status={claim['status']} state={arguments.state}")
    return 0


def parse_probe_source_ref(source_ref: str) -> tuple[str, str] | None:
    """Split a scribe-probe sourceRef into (probe command, recorded timestamp)."""
    match = re.match(
        r"^scribe-probe:(.+)@(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:?\d{2}))$",
        source_ref,
    )
    if not match:
        return None
    return match.group(1), match.group(2)


def reprobe_refusal_reason(command: str) -> tuple[str, list[str]] | tuple[None, list[str]]:
    """Return (refusal reason, argv) for a recorded probe command.

    state.json content is data, never trusted shell input: the default path
    refuses shell metacharacters outright (no chaining, substitution, or
    redirection), parses with shlex, and validates argv[0] against a read-only
    allowlist. Anything refused falls back to the scribe's hand-probe path or
    an explicit --allow-any operator override.
    """
    stripped = command.strip()
    if not stripped:
        return "空指令", []
    present = sorted(set(stripped) & REPROBE_SHELL_METACHARACTERS)
    if present:
        return (
            f"含 shell 中繼字元 {' '.join(present)}——非單一唯讀指令（書記官親手重探，或 --allow-any 明示放行）",
            [],
        )
    try:
        argv = shlex.split(stripped)
    except ValueError as error:
        return f"無法解析為 argv：{error}", []
    if not argv:
        return "空指令", []
    leader = argv[0].rsplit("/", 1)[-1]
    if leader not in REPROBE_SAFE_LEADERS:
        return f"leading command '{leader}' 不在唯讀允許集（--allow-any 可放行）", argv
    if leader == "git":
        for token in argv[1:]:
            if token in REPROBE_GIT_FORBIDDEN_TOKENS or any(
                token.startswith(f"{bad}=") for bad in REPROBE_GIT_FORBIDDEN_TOKENS
            ):
                return f"git token '{token}' 具設定/執行注入風險，拒絕重放", argv
            if token in REPROBE_GIT_FORBIDDEN_SUBCOMMANDS:
                return f"git 子命令 '{token}' 會改動工作樹，拒絕重放", argv
    return None, argv


def run_reprobe(arguments: argparse.Namespace) -> int:
    """Re-execute recorded scribe-probe commands mechanically; judgment stays with the scribe.

    exit-0 probes may refresh timestamps (--refresh) but NEVER change a claim's
    status — upgrading UNKNOWN/FAIL to PASS remains a set-claim decision made by
    whoever reads the probe output.
    """
    state = copy.deepcopy(load_state(arguments.state))
    claims = [
        item
        for item in state.get("currentTruth", {}).get("evidenceClaims", [])
        if isinstance(item, dict)
    ]
    if arguments.claim:
        wanted = set(arguments.claim)
        selected = [item for item in claims if item.get("id") in wanted]
        missing = wanted - {item.get("id") for item in selected}
        if missing:
            print(f"[FAIL] 找不到 evidence claim：{', '.join(sorted(missing))}", file=sys.stderr)
            return 1
    else:
        gating = gating_claim_ids(state)
        selected = [item for item in claims if item.get("id") in gating]
    now = resolve_now(arguments.now)
    artifacts_dir: Path | None = arguments.artifacts
    if artifacts_dir is not None:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
    ok = failed = skipped = 0
    refreshed: list[str] = []
    for claim in selected:
        claim_id = str(claim.get("id"))
        parsed = parse_probe_source_ref(str(claim.get("sourceRef", "")))
        if parsed is None:
            skipped += 1
            print(f"REPROBE ｜ {claim_id} ｜ skipped ｜ sourceRef 非 scribe-probe 文法，無可重放指令")
            continue
        command, _recorded_at = parsed
        run_target: str | list[str] = command
        use_shell = True
        if not arguments.allow_any:
            refusal, argv = reprobe_refusal_reason(command)
            if refusal is not None:
                skipped += 1
                print(f"REPROBE ｜ {claim_id} ｜ skipped ｜ {refusal}")
                continue
            run_target = argv
            use_shell = False
        try:
            completed = subprocess.run(
                run_target,
                shell=use_shell,
                capture_output=True,
                text=True,
                timeout=arguments.timeout,
            )
            exit_code = completed.returncode
            output = completed.stdout + (("\n" + completed.stderr) if completed.stderr else "")
        except subprocess.TimeoutExpired:
            exit_code = -1
            output = f"[timeout {arguments.timeout}s]"
        except OSError as error:
            exit_code = -1
            output = f"[exec error] {error}"
        digest = hashlib.sha256(output.encode("utf-8")).hexdigest()[:12]
        if artifacts_dir is not None:
            stamp = isoformat_seconds(now).replace(":", "")
            artifact = artifacts_dir / f"reprobe-{claim_id}-{stamp}.txt"
            artifact.write_text(f"$ {command}\nexit={exit_code}\n{output}", encoding="utf-8")
        print(f"REPROBE ｜ {claim_id} ｜ exit={exit_code} ｜ sha256={digest} ｜ {command}")
        if exit_code == 0:
            ok += 1
            if arguments.refresh:
                claim["sourceRef"] = f"scribe-probe:{command}@{isoformat_seconds(now)}"
                claim["observedAt"] = isoformat_seconds(now)
                claim["validUntil"] = isoformat_seconds(
                    now + timedelta(hours=DEFAULT_CLAIM_VALIDITY_HOURS)
                )
                refreshed.append(claim_id)
        else:
            failed += 1
            print(
                f"歧異 ｜ {claim_id} ｜ 情報稱: 在冊探測可重放 ｜ 探測得: exit={exit_code} ｜ 處置: 待裁決"
            )
    if refreshed:
        advance_updated_at(state, now)
        code = commit_state(state, arguments.state)
        if code != 0:
            return code
    print(
        f"REPROBE_SUMMARY total={len(selected)} ok={ok} failed={failed} "
        f"skipped={skipped} refreshed={len(refreshed)}"
    )
    return 0 if failed == 0 else 1


def run_create_slice_front(state: dict[str, Any], arguments: argparse.Namespace) -> int:
    """Create a sealable slice front under a parent, born DEFERRED.

    Inherits operationType/owner/mutationScope/recovery/carrierRoots and the
    parent candidate's expectedVictoryCriterionIds; creates only its own
    entry/exit/pivot claims (born UNKNOWN). DEFERRED birth keeps the candidate
    ineligible, so clarity derivations are untouched — activation later goes
    through the ordinary set-front/handoff path.
    """
    front_id = arguments.front_id
    battlefields = state.get("battlefields", [])
    parent = next(
        (
            item
            for item in battlefields
            if isinstance(item, dict) and item.get("id") == arguments.slice_of
        ),
        None,
    )
    if parent is None:
        print(f"[FAIL] 找不到親 battlefield：{arguments.slice_of}", file=sys.stderr)
        return 1
    if any(isinstance(item, dict) and item.get("id") == front_id for item in battlefields):
        print(f"[FAIL] battlefield id 已存在：{front_id}", file=sys.stderr)
        return 1
    if not arguments.entry_state or not arguments.terminal_state:
        print("[FAIL] 切片建檔需要 --entry-state 與 --terminal-state（語意狀態名）", file=sys.stderr)
        return 1

    now = resolve_now(arguments.now)
    claims = state.setdefault("currentTruth", {}).setdefault("evidenceClaims", [])
    claim_ids = {claim.get("id") for claim in claims if isinstance(claim, dict)}

    def born_unknown(claim_id: str, predicate: str) -> str:
        if claim_id in claim_ids:
            print(f"[FAIL] evidence claim id 已存在：{claim_id}", file=sys.stderr)
            raise SeedError(claim_id)
        claims.append(
            {
                "id": claim_id,
                "sourceType": "DB",
                "sourceRef": SEEDED_SOURCE_REF,
                "observedAt": isoformat_seconds(now),
                "validUntil": isoformat_seconds(now + timedelta(hours=DEFAULT_CLAIM_VALIDITY_HOURS)),
                "authorityRank": 1,
                "predicate": predicate,
                "status": "UNKNOWN",
            }
        )
        return claim_id

    try:
        entry_claim_id = born_unknown(
            f"claim-front-{front_id}-entry",
            canonical_predicate(
                "BATTLEFIELD[{}].ENTRY[{}] == {}", front_id, arguments.entry_state, True
            ),
        )
        exit_claim_id = born_unknown(
            f"claim-front-{front_id}-exit",
            canonical_predicate(
                "BATTLEFIELD[{}].EXIT[{}] == {}", front_id, arguments.terminal_state, True
            ),
        )
        born_unknown(
            f"claim-front-{front_id}-pivot",
            canonical_predicate("BATTLEFIELD[{}].PIVOT_TRIGGERED == {}", front_id, True),
        )
    except SeedError:
        return 1

    carrier_roots = list(parent.get("carrierRoots", []))
    for root in arguments.carrier_root or []:
        if root not in carrier_roots:
            carrier_roots.append(root)
    new_front: dict[str, Any] = {
        "id": front_id,
        "operationType": parent.get("operationType", "SHAPING"),
        "effort": "SUPPORT",
        "status": "DEFERRED",
        "objective": arguments.objective or f"{parent.get('objective', '')}（切片 {front_id}）",
        "entryState": arguments.entry_state,
        "terminalState": arguments.terminal_state,
        "entryClaimId": entry_claim_id,
        "exitClaimId": exit_claim_id,
        "evidenceClaimIds": [entry_claim_id, exit_claim_id],
        "mutationScope": list(parent.get("mutationScope", [])),
        "recovery": copy.deepcopy(parent.get("recovery", {})),
        "allowedNextStatuses": ["ACTIVE", "PENDING", "COMPLETE"],
        "deferReason": arguments.defer_reason
        or f"切片建檔（--slice-of {arguments.slice_of}），排隊待啟用",
        "owner": parent.get("owner", ""),
        "timeBudgetMinutes": parent.get("timeBudgetMinutes", 60),
    }
    if carrier_roots:
        new_front["carrierRoots"] = carrier_roots
    battlefields.append(new_front)

    decision = state.setdefault("decision", {})
    candidates = decision.setdefault("candidates", [])
    parent_candidate = next(
        (
            item
            for item in candidates
            if isinstance(item, dict) and item.get("frontId") == arguments.slice_of
        ),
        {},
    )
    expected_ids = list(parent_candidate.get("expectedVictoryCriterionIds", []))
    unresolved = {
        criterion.get("id")
        for criterion in state.get("strategicObjective", {}).get("victoryCriteria", [])
        if isinstance(criterion, dict) and criterion.get("status") != "PASS"
    }
    unmet = len(unresolved - set(expected_ids))
    transitions = arguments.transitions if arguments.transitions is not None else 1
    cost = arguments.cost if arguments.cost is not None else 30
    candidates.append(
        {
            "frontId": front_id,
            "eligible": False,
            "expectedVictoryCriterionIds": expected_ids,
            "unmetVictoryCriteria": unmet,
            "remainingTransitions": transitions,
            "riskScore": 0,
            "costMinutes": cost,
            "blockingRiskIds": [],
            "totalScore": unmet * 100 + transitions * 10 + cost,
            "ineligibilityReason": f"戰場狀態為 DEFERRED，不列入主攻候選",
        }
    )

    advance_updated_at(state, now)
    code = commit_state(state, arguments.state)
    if code != 0:
        return code
    print(
        f"SLICE_FRONT_CREATED id={front_id} parent={arguments.slice_of} "
        f"status=DEFERRED claims=3 state={arguments.state}"
    )
    return 0


def run_set_front(arguments: argparse.Namespace) -> int:
    state = copy.deepcopy(load_state(arguments.state))
    front = next(
        (
            item
            for item in state.get("battlefields", [])
            if isinstance(item, dict) and item.get("id") == arguments.front_id
        ),
        None,
    )
    if front is None and arguments.slice_of:
        return run_create_slice_front(state, arguments)
    if front is None:
        print(f"[FAIL] 找不到 battlefield：{arguments.front_id}", file=sys.stderr)
        return 1
    if not arguments.status:
        print("[FAIL] 更新既有 battlefield 需要 --status", file=sys.stderr)
        return 1
    front["status"] = arguments.status
    if arguments.effort:
        front["effort"] = arguments.effort
    if arguments.defer_reason is not None:
        front["deferReason"] = arguments.defer_reason
    if arguments.carrier_root:
        carrier_roots = list(front.get("carrierRoots", []))
        for root in arguments.carrier_root:
            if root not in carrier_roots:
                carrier_roots.append(root)
        front["carrierRoots"] = carrier_roots
    code = commit_state(state, arguments.state)
    if code != 0:
        return code
    print(
        f"FRONT_UPDATED id={arguments.front_id} status={front['status']} "
        f"effort={front['effort']} state={arguments.state}"
    )
    return 0


def run_toll(arguments: argparse.Namespace) -> int:
    """Pay the organ-loop continuation toll: refused unless terminal distance strictly shrinks."""
    load_state(arguments.state)
    if arguments.after >= arguments.before:
        print(
            f"[FAIL] 過路費未付：終局距離未縮短（前 {arguments.before} → 後 {arguments.after}）——續輪不得開",
            file=sys.stderr,
        )
        return 1
    now = resolve_now(arguments.now)
    ledger_path = arguments.ledger or arguments.state.parent / "run-ledger.jsonl"
    line = json.dumps(
        {
            "ts": isoformat_seconds(now),
            "event": "ORGAN_LOOP_TOLL",
            "organ": arguments.organ,
            "before": arguments.before,
            "after": arguments.after,
        },
        ensure_ascii=False,
    )
    with open(ledger_path, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(
        f"TOLL_PAID organ={arguments.organ} before={arguments.before} "
        f"after={arguments.after} ledger={ledger_path}"
    )
    return 0


def run_handoff(arguments: argparse.Namespace) -> int:
    """Atomically complete one front and activate the next; whole-file validate before writing."""
    state = copy.deepcopy(load_state(arguments.state))
    fronts = {
        front.get("id"): front for front in state.get("battlefields", []) if isinstance(front, dict)
    }
    source = fronts.get(arguments.from_id)
    target = fronts.get(arguments.to_id)
    if source is None or target is None:
        missing = arguments.from_id if source is None else arguments.to_id
        print(f"[FAIL] 找不到 battlefield：{missing}", file=sys.stderr)
        return 1
    if source.get("status") != "ACTIVE":
        print(
            f"[FAIL] handoff 來源必須是 ACTIVE：{arguments.from_id} 目前 {source.get('status')}",
            file=sys.stderr,
        )
        return 1
    if target is source or target.get("status") == "COMPLETE":
        print(f"[FAIL] handoff 目標不可為來源自身或已 COMPLETE：{arguments.to_id}", file=sys.stderr)
        return 1
    claims = {
        claim.get("id"): claim
        for claim in state.get("currentTruth", {}).get("evidenceClaims", [])
        if isinstance(claim, dict)
    }
    observed_at = resolve_now(arguments.now)
    valid_until = isoformat_seconds(observed_at + timedelta(hours=DEFAULT_CLAIM_VALIDITY_HOURS))

    def stamp(claim_id: str, source_ref: str) -> bool:
        claim = claims.get(claim_id)
        if claim is None:
            print(f"[FAIL] 找不到 evidence claim：{claim_id}", file=sys.stderr)
            return False
        if not GATING_PROVENANCE_PATTERN.match(source_ref):
            print(GATING_PROVENANCE_REFUSAL, file=sys.stderr)
            return False
        claim["status"] = "PASS"
        claim["sourceRef"] = source_ref
        claim["observedAt"] = isoformat_seconds(observed_at)
        claim["validUntil"] = valid_until
        return True

    if not stamp(str(source.get("exitClaimId", "")), arguments.exit_source_ref):
        return 1
    entry_claim = claims.get(str(target.get("entryClaimId", "")))
    if arguments.entry_source_ref:
        if not stamp(str(target.get("entryClaimId", "")), arguments.entry_source_ref):
            return 1
    elif not (entry_claim and entry_claim.get("status") == "PASS"):
        print("[FAIL] 目標前線 entry claim 非 PASS；請提供 --entry-source-ref", file=sys.stderr)
        return 1
    if target.get("mutationScope"):
        recovery = target.setdefault("recovery", {})
        recovery_claims = [rid for rid in recovery.get("evidenceClaimIds", []) if isinstance(rid, str)]
        if arguments.recovery_source_ref:
            if not recovery_claims or not stamp(recovery_claims[0], arguments.recovery_source_ref):
                return 1
            recovery["status"] = "READY"
        elif recovery.get("status") not in {"READY", "NOT_REQUIRED"}:
            print(
                "[FAIL] 目標為 mutation 前線且 recovery 未 READY；請提供 --recovery-source-ref",
                file=sys.stderr,
            )
            return 1

    source["status"] = "COMPLETE"
    target["status"] = "ACTIVE"
    target["effort"] = "MAIN"

    decision = state.setdefault("decision", {})
    decision["activeFrontId"] = arguments.to_id
    decision["pivotClaimId"] = f"claim-front-{arguments.to_id}-pivot"
    decision["contribution"] = arguments.contribution

    risks = [risk for risk in state.get("riskRegister", []) if isinstance(risk, dict)]
    blockers = [item for item in state.get("blockers", []) if isinstance(item, dict)]
    proven_blocked = {item.get("blockedFrontId") for item in blockers if item.get("status") == "PROVEN"}
    for candidate in decision.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        front = fronts.get(candidate.get("frontId"))
        if front is None:
            continue
        front_id = front.get("id")
        blocking = sorted(
            str(risk.get("id"))
            for risk in risks
            if risk.get("affectedFrontId") == front_id
            and risk.get("status") == "OPEN"
            and int(risk.get("score", 0)) >= int(risk.get("unacceptableThreshold", 0))
        )
        recovery_ready = not front.get("mutationScope") or front.get("recovery", {}).get("status") in {
            "READY",
            "NOT_REQUIRED",
        }
        eligible = (
            front.get("status") not in {"COMPLETE", "DEFERRED"}
            and front_id not in proven_blocked
            and not blocking
            and recovery_ready
        )
        candidate["eligible"] = eligible
        candidate["blockingRiskIds"] = blocking
        if eligible:
            candidate["ineligibilityReason"] = ""
        elif front.get("status") in {"COMPLETE", "DEFERRED"}:
            candidate["ineligibilityReason"] = f"戰場狀態為 {front.get('status')}，不列入主攻候選"
        elif front_id in proven_blocked:
            candidate["ineligibilityReason"] = "存在 PROVEN blocker"
        elif blocking:
            candidate["ineligibilityReason"] = f"未控制且達門檻的風險：{', '.join(blocking)}"
        else:
            candidate["ineligibilityReason"] = "mutation 戰場的 recovery 尚未 READY"

    eligible_rows = [
        candidate
        for candidate in decision.get("candidates", [])
        if isinstance(candidate, dict) and candidate.get("eligible")
    ]
    minimum_ids: list[str] = []
    if eligible_rows:
        minimum_score = min(int(candidate.get("totalScore", 0)) for candidate in eligible_rows)
        minimum_ids = sorted(
            str(candidate.get("frontId"))
            for candidate in eligible_rows
            if int(candidate.get("totalScore", 0)) == minimum_score
        )
    clarity = state.setdefault("strategicClarity", {})
    clarity["candidateMainEffortIds"] = minimum_ids
    pivot_status = claims.get(decision["pivotClaimId"], {}).get("status", "UNKNOWN")
    unresolved = clarity.get("unresolvedDecisions", [])
    has_suspected = any(item.get("status") == "SUSPECTED" for item in blockers)
    clear = len(minimum_ids) == 1 and not unresolved and not has_suspected and pivot_status == "FAIL"
    if clear:
        clarity["status"] = "CLEAR"
        clarity["unclearCauses"] = []
        clarity["route"] = "EXECUTION_READY"
    else:
        causes: list[str] = []
        if unresolved:
            causes.append("DECISION_FOG")
        if has_suspected:
            causes.append("BLOCKER_SUSPECTED")
        if not minimum_ids:
            causes.append("NO_ELIGIBLE_CANDIDATE")
        elif len(minimum_ids) > 1:
            causes.append("AMBIGUOUS_CANDIDATE")
        if pivot_status == "PASS":
            causes.append("PIVOT_TRIGGERED")
        elif pivot_status != "FAIL":
            causes.append("PIVOT_UNPROBED")
        causes.sort()
        clarity["status"] = "UNCLEAR"
        clarity["unclearCauses"] = causes
        clarity["route"] = "WAYFINDER_REQUIRED" if "DECISION_FOG" in causes else "OPERATOR_RESOLVE"

    state.setdefault("progress", {})["activeFrontStartedAt"] = isoformat_seconds(observed_at)
    advance_updated_at(state, observed_at)
    code = commit_state(state, arguments.state)
    if code != 0:
        return code
    print(
        f"FRONT_HANDOFF from={arguments.from_id} to={arguments.to_id} "
        f"route={clarity['route']} state={arguments.state}"
    )
    return 0


def run_state_tool(arguments: argparse.Namespace) -> int:
    handlers = {
        "init": run_init,
        "set-claim": run_set_claim,
        "add-claim": run_add_claim,
        "set-front": run_set_front,
        "handoff": run_handoff,
        "reprobe": run_reprobe,
        "toll": run_toll,
    }
    try:
        return handlers[arguments.command](arguments)
    except YamlSeedUnavailable:
        print(YAML_UNAVAILABLE_MESSAGE, file=sys.stderr)
        return 2
    except (SeedError, OSError, ValueError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        return 1


def add_state_tool_parsers(subparsers: Any) -> None:
    init_parser = subparsers.add_parser("init", help="expand a semantic seed into a valid state.json")
    init_parser.add_argument("seed", type=Path)
    init_parser.add_argument("out", type=Path)
    init_parser.add_argument("--now", help="ISO 8601 timestamp with offset (default: system now)")
    init_parser.add_argument("--force", action="store_true", help="overwrite an existing output path")

    set_claim_parser = subparsers.add_parser("set-claim", help="set one evidence claim, then revalidate")
    set_claim_parser.add_argument("state", type=Path)
    set_claim_parser.add_argument("claim_id")
    set_claim_parser.add_argument("--status", choices=sorted(CLAIM_STATUSES), required=True)
    set_claim_parser.add_argument("--source-ref", required=True)
    set_claim_parser.add_argument("--observed-at")
    set_claim_parser.add_argument("--valid-until")

    add_claim_parser = subparsers.add_parser("add-claim", help="append one evidence claim, then revalidate")
    add_claim_parser.add_argument("state", type=Path)
    add_claim_parser.add_argument("--id")
    add_claim_parser.add_argument("--source-type", choices=sorted(EVIDENCE_SOURCE_TYPES))
    add_claim_parser.add_argument("--source-ref")
    add_claim_parser.add_argument("--predicate")
    add_claim_parser.add_argument("--status", choices=sorted(CLAIM_STATUSES))
    add_claim_parser.add_argument("--authority-rank", type=int)
    add_claim_parser.add_argument("--observed-at")
    add_claim_parser.add_argument("--valid-until")
    add_claim_parser.add_argument("--json", help="full claim object as JSON; flags win over its fields")

    set_front_parser = subparsers.add_parser(
        "set-front", help="set one battlefield status, or create a slice front (--slice-of), then revalidate"
    )
    set_front_parser.add_argument("state", type=Path)
    set_front_parser.add_argument("front_id")
    set_front_parser.add_argument("--status", choices=sorted(FRONT_STATUSES))
    set_front_parser.add_argument("--effort", choices=sorted(EFFORTS))
    set_front_parser.add_argument("--defer-reason", dest="defer_reason")
    set_front_parser.add_argument(
        "--slice-of",
        dest="slice_of",
        help="parent front id — creates front_id as a DEFERRED slice inheriting recovery/scope",
    )
    set_front_parser.add_argument("--entry-state", dest="entry_state", help="slice creation: semantic entry state")
    set_front_parser.add_argument(
        "--terminal-state", dest="terminal_state", help="slice creation: semantic terminal state"
    )
    set_front_parser.add_argument("--objective", help="slice creation: objective text (default: parent's + slice id)")
    set_front_parser.add_argument("--transitions", type=int, help="slice creation: remainingTransitions (default 1)")
    set_front_parser.add_argument("--cost", type=int, help="slice creation: costMinutes (default 30)")
    set_front_parser.add_argument(
        "--carrier-root",
        dest="carrier_root",
        action="append",
        help="absolute repo root the scribe may probe for this front (repeatable)",
    )
    set_front_parser.add_argument("--now", help="ISO 8601 timestamp with offset (default: system now)")

    toll_parser = subparsers.add_parser(
        "toll", help="pay the organ-loop continuation toll; refused unless after < before"
    )
    toll_parser.add_argument("state", type=Path)
    toll_parser.add_argument("--organ", required=True, help="which quality organ's fix loop continues (e.g. seal)")
    toll_parser.add_argument("--before", type=int, required=True, help="terminal distance before the round")
    toll_parser.add_argument("--after", type=int, required=True, help="projected terminal distance after the round")
    toll_parser.add_argument("--ledger", type=Path, help="ledger path (default: run-ledger.jsonl beside state.json)")
    toll_parser.add_argument("--now", help="ISO 8601 timestamp with offset (default: system now)")

    handoff_parser = subparsers.add_parser(
        "handoff", help="atomically complete one front and activate the next, then revalidate"
    )
    handoff_parser.add_argument("state", type=Path)
    handoff_parser.add_argument("from_id")
    handoff_parser.add_argument("to_id")
    handoff_parser.add_argument("--exit-source-ref", dest="exit_source_ref", required=True)
    handoff_parser.add_argument("--entry-source-ref", dest="entry_source_ref")
    handoff_parser.add_argument("--recovery-source-ref", dest="recovery_source_ref")
    handoff_parser.add_argument("--contribution", choices=sorted(CONTRIBUTIONS), default="DIRECT_ADVANCE")
    handoff_parser.add_argument("--now")

    reprobe_parser = subparsers.add_parser(
        "reprobe",
        help="re-execute recorded scribe-probe commands mechanically and report per claim",
    )
    reprobe_parser.add_argument("state", type=Path)
    reprobe_parser.add_argument(
        "--claim",
        action="append",
        help="claim id to reprobe (repeatable; default: every gating claim)",
    )
    reprobe_parser.add_argument(
        "--refresh",
        action="store_true",
        help="on exit-0, renew observedAt/validUntil and the sourceRef timestamp (status untouched)",
    )
    reprobe_parser.add_argument(
        "--timeout", type=int, default=120, help="per-probe timeout in seconds (default 120)"
    )
    reprobe_parser.add_argument(
        "--artifacts", type=Path, help="directory to save each probe's full output"
    )
    reprobe_parser.add_argument(
        "--allow-any", action="store_true", help="bypass the read-only command allowlist"
    )
    reprobe_parser.add_argument("--now", help="ISO 8601 timestamp with offset (default: system now)")


def add_language_argument(command_parser: argparse.ArgumentParser) -> None:
    command_parser.add_argument(
        "--language",
        choices=("zh-TW", "en"),
        default="zh-TW",
        help="user-facing renderer language (default: zh-TW)",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="戰略狀態驗證與戰略推進沙盤產生器")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "self-test"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("state", type=Path)
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("state", type=Path)
    add_language_argument(summary_parser)
    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("state", type=Path)
    render_parser.add_argument("output", type=Path)
    add_language_argument(render_parser)
    render_parser.add_argument("--no-open", action="store_true", help="do not open the rendered HTML")
    graph_parser = subparsers.add_parser("render-graph")
    graph_parser.add_argument("state", type=Path)
    graph_parser.add_argument("output", type=Path)
    add_language_argument(graph_parser)
    graph_parser.add_argument(
        "--full-history",
        action="store_true",
        help="render every front instead of the compact situation display",
    )
    render_all_parser = subparsers.add_parser("render-all")
    render_all_parser.add_argument("state", type=Path)
    render_all_parser.add_argument("output_directory", type=Path)
    add_language_argument(render_all_parser)
    render_all_parser.add_argument("--no-open", action="store_true", help="do not open the rendered HTML")
    add_state_tool_parsers(subparsers)
    arguments = parser.parse_args()

    if arguments.command in STATE_TOOL_COMMANDS:
        return run_state_tool(arguments)

    try:
        state = load_state(arguments.state)
        errors = validate_state(state)
        if errors:
            for error in errors:
                print(f"[FAIL] {error}", file=sys.stderr)
            return 1
        if arguments.command == "validate":
            print(
                f"STRATEGIC_STATE_VALID mission={state['missionId']} "
                f"clarity={state['strategicClarity']['status']} "
                f"terminal={state['terminalAssessment']['status']} fronts={len(state['battlefields'])}"
            )
        elif arguments.command == "self-test":
            print(run_self_test(state))
        elif arguments.command == "summary":
            print(build_summary(state, arguments.language))
        elif arguments.command == "render":
            output = arguments.output.resolve()
            atomic_write(output, render_html(state, arguments.language))
            print(f"SAND_TABLE_RENDERED path={output} language={arguments.language}")
            if not arguments.no_open:
                open_html_fail_soft(output)
        elif arguments.command == "render-graph":
            graph = (
                f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'{render_battle_map_svg(state, arguments.language, full_history=arguments.full_history)}\n'
            )
            atomic_write(arguments.output.resolve(), graph)
            mode = "full-history" if arguments.full_history else "compact"
            print(
                f"BATTLE_MAP_RENDERED path={arguments.output.resolve()} "
                f"language={arguments.language} mode={mode}"
            )
        else:
            output_directory = arguments.output_directory.resolve()
            sand_table = output_directory / "sand-table.html"
            battle_map = output_directory / "battle-map.svg"
            atomic_write(sand_table, render_html(state, arguments.language))
            graph = (
                f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'{render_battle_map_svg(state, arguments.language)}\n'
            )
            atomic_write(battle_map, graph)
            print(
                f"STRATEGIC_ARTIFACTS_RENDERED html={sand_table} graph={battle_map} "
                f"language={arguments.language} graph_mode=compact"
            )
            if not arguments.no_open:
                open_html_fail_soft(sand_table)
        return 0
    except (OSError, ValueError, StopIteration) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

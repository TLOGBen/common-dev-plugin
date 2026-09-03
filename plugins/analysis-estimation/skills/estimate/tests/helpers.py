from __future__ import annotations

import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from case_state import default_state  # noqa: E402


def complete_state() -> dict:
    state = default_state("demo-case", "示範案件", "保留既有契約並完成技術遷移", "upgrade")
    state["revision"] = 8
    state["status"] = "estimate-ready"
    state["outcome"].update({
        "acceptance": ["代表性契約驗證通過"],
        "preserve": ["既有網址與回應契約"],
        "responsibilityBoundary": "我方負責應用改造；客戶負責部署與 UAT",
    })
    state["evidence"] = [
        {
            "id": "ev-runtime",
            "claim": "主要入口與共同行為已完成靜態及啟動核對",
            "source": "C:\\ProjectAlpha\\private\\Controller.java password=Secret123",
            "method": "唯讀原始碼盤點與隔離啟動",
            "strength": "build",
            "confidence": "high",
            "decisionImpact": "scenario",
        }
    ]
    state["dependencyCoverage"] = {
        "status": "complete",
        "source": "resolved dependency tree、實際封裝與原始碼使用全集",
        "discoveryMethod": "比對 resolved artifacts、完整 package imports、產碼設定與 runtime integration",
        "componentCount": 12,
        "decisionBearingDependencyIds": ["dependency-query-layer"],
        "evidenceIds": ["ev-runtime"],
        "boundary": "涵蓋本次目標版本會跨越的 runtime、framework、ORM 與產碼鏈",
    }
    state["dependencies"] = [
        {
            "id": "dependency-query-layer", "component": "查詢與產碼元件", "current": "既有版本",
            "target": "目標相容版本", "criticality": "critical", "criticalityReason": "決定 ORM 目標線是否可採用",
            "upstreamSource": "上游官方發行與 issue tracker", "upstreamMaintainer": "上游專案維護者",
            "internalOwner": "我方資料層團隊", "maintenanceStatus": "active", "usage": "查詢 DSL 與產碼",
            "buildTime": "annotation processing 與 generated sources", "extensions": "自訂 DB function registry",
            "semanticBreaks": ["日期參數型別", "function 註冊", "Entity identity 行為"],
            "probe": "代表性 query 與 transaction runtime 驗證",
            "footprint": {
                "discoveryMethod": "完整 package imports、APT 設定與高風險 API 搜尋",
                "scope": "所有查詢、產碼、function 與 transaction 整合使用點",
                "highRiskApis": ["Date function", "function registry", "entity identity"],
            },
            "compatibilityClaims": [
                {
                    "target": "目標相容版本", "status": "supported", "evidenceIds": ["ev-runtime"],
                    "rationale": "上游支援證據與代表性 runtime probe 支持此組合。",
                }
            ],
            "fallbackStrategies": ["若目標組合失效，評估替換元件或停留既有 ORM 線。"],
            "resolution": {
                "status": "accepted", "strategy": "keep", "selectedTarget": "目標相容版本",
                "rationale": "目前證據支持沿用相容版本。", "owner": "我方資料層團隊",
            },
            "blocksScenario": False,
            "evidenceIds": ["ev-runtime"],
        }
    ]
    state["fogs"] = []
    state["scenarios"] = [
        {"id": "scenario-a", "name": "相容遷移", "summary": "保留既有契約並替換必要框架"}
    ]
    state["selectedScenarioId"] = "scenario-a"
    state["decisions"] = [
        {
            "id": "answer-select-outcome-direction-3",
            "decisionId": "select-outcome-direction",
            "answer": "指定技術線升級",
            "decidedBy": "PM（聊天確認）",
            "recordedAt": "2026-08-28T00:00:00+00:00",
        },
        {
            "id": "answer-select-scenario-7",
            "decisionId": "select-scenario",
            "answer": "採用相容遷移",
            "selectedScenarioId": "scenario-a",
            "decidedBy": "PM（聊天確認）",
            "recordedAt": "2026-08-28T00:00:00+00:00",
        }
    ]
    state["successChain"] = {
        "destination": "應用在既有環境維持相同行為",
        "nodes": [
            {
                "id": "foundation", "name": "建立共用承接底座", "description": "承接啟動、輸入輸出與 Session",
                "owner": "我方應用團隊", "status": "done", "disposition": "priced", "zeroReason": "",
                "total": 1, "needsChange": 1, "noChange": 0, "unknown": 0, "dependsOn": [],
                "completionEvidence": "應用可建置並啟動", "evidenceIds": ["ev-runtime"],
            },
            {
                "id": "actions", "name": "接回既有功能入口", "description": "保留網址與輸入輸出契約",
                "owner": "我方應用團隊", "status": "done", "disposition": "priced", "zeroReason": "",
                "total": 4, "needsChange": 3, "noChange": 1, "unknown": 0, "dependsOn": ["foundation"],
                "completionEvidence": "代表入口可回應相同契約", "evidenceIds": ["ev-runtime"],
            },
            {
                "id": "deployment", "name": "部署與 UAT", "description": "由客戶 IT 完成正式環境部署",
                "owner": "客戶 IT", "status": "external", "disposition": "external", "zeroReason": "客戶責任，不納入我方人天",
                "total": 1, "needsChange": 1, "noChange": 0, "unknown": 0, "dependsOn": ["actions"],
                "completionEvidence": "客戶完成 UAT 簽核", "evidenceIds": ["ev-runtime"],
            },
        ],
    }
    state["workItems"] = [
        {
            "id": "work-foundation", "package": "框架與共用機制", "name": "建立共用承接底座",
            "kind": "shared", "description": "建立應用啟動、輸入輸出與 Session 的共用能力",
            "pmDescription": "建立所有功能共同使用的應用基礎，只做一次。", "total": 1, "needsChange": 1, "pricingUnits": 1,
            "noChange": 0, "unknown": 0, "unitDays": {"low": 3.0, "baseline": 4.0, "high": 5.0},
            "effortSplit": {
                "development": {"low": 2.0, "baseline": 3.0, "high": 4.0},
                "testing": {"low": 1.0, "baseline": 1.0, "high": 1.0},
            },
            "owner": "我方", "nodeIds": ["foundation"], "evidenceIds": ["ev-runtime"],
            "completionEvidence": "應用可建置並啟動", "includes": "啟動與共用契約", "excludes": "客戶環境施工",
            "currentConstraint": "舊框架負責啟動與 Session，移除後需要新的共用承接點。",
            "changeMethod": "建立一次性的啟動、輸入輸出與 Session 共用設定，讓功能入口共同使用。",
            "customerOutcome": "新版應用具備可啟動且一致的共用行為。",
            "scaleEvidence": "1 組應用底座，承接全部功能入口。",
            "countingRationale": "所有入口共用同一底座，因此只計一次。",
            "rateBasis": "以建立設定、啟動 smoke 與共用契約檢查的代表切片估算。",
            "dedupeBoundary": "包含共用啟動與 Session；逐支功能接回由下一列承接。",
            "clientPackageId": "package-runtime",
        },
        {
            "id": "work-actions", "package": "既有功能接回", "name": "接回需要處理的功能入口（共 4 支／需處理 3 支）",
            "kind": "quantity", "description": "逐支確認參數、回應與例外契約",
            "pmDescription": "將 3 支受影響入口接回新底座，保留使用方式。", "total": 4, "needsChange": 3, "pricingUnits": 3,
            "noChange": 1, "unknown": 0, "unitDays": {"low": 0.5, "baseline": 1.0, "high": 1.5},
            "effortSplit": {
                "development": {"low": 0.5, "baseline": 0.5, "high": 1.0},
                "testing": {"low": 0.0, "baseline": 0.5, "high": 0.5},
            },
            "owner": "我方", "nodeIds": ["actions"], "evidenceIds": ["ev-runtime"],
            "completionEvidence": "代表入口可回應相同契約", "includes": "參數與回應對照", "excludes": "正式 UAT",
            "currentConstraint": "3 支入口依賴舊框架的參數與回應契約。",
            "changeMethod": "逐支對照參數、回應與例外，接到共用底座並執行代表性驗證。",
            "customerOutcome": "3 支受影響入口在新版仍維持原使用方式。",
            "scaleEvidence": "共 4 支，證據確認 3 支需處理、1 支不異動。",
            "countingRationale": "每支入口的參數與例外需獨立確認，因此以 3 支乘單價。",
            "rateBasis": "以一支一般入口的理解、修改與局部驗證作為代表切片。",
            "dedupeBoundary": "不重複計共用底座，也不包含正式 UAT。",
            "clientPackageId": "package-entry",
        },
    ]
    state["clientPackages"] = [
        {
            "id": "package-runtime", "name": "新版應用可正常啟動",
            "whyRequired": "舊框架移除後需要新的共用啟動與 Session 承接方式。",
            "deliveryApproach": "建立一次性的應用底座並完成啟動檢查。",
            "customerOutcome": "取得可建置、可啟動且共同行為一致的新版應用。",
            "externalSummary": "建立新版應用啟動、共用輸入輸出與 Session 承接機制，調整必要設定並完成建置及啟動驗證。",
            "scopeEvidence": "1 組共用底座，涵蓋全部入口。", "owner": "我方",
        },
        {
            "id": "package-entry", "name": "既有功能入口可延續使用",
            "whyRequired": "受影響入口仍依賴舊框架的參數與回應契約。",
            "deliveryApproach": "將 3 支入口逐支接回新底座並核對行為。",
            "customerOutcome": "使用者維持原網址與操作方式。",
            "externalSummary": "逐支調整既有功能入口、參數與回應承接方式，核對原網址及操作契約，並完成代表性功能回歸驗證。",
            "scopeEvidence": "共 4 支，需處理 3 支、不異動 1 支。", "owner": "我方",
        },
    ]
    state["currentDecision"] = {
        "id": "confirm-estimate", "title": "確認工作內容與對外人天", "whyHuman": "這會形成對客戶的範圍承諾。",
        "factsTitle": "做決定前值得看的資訊", "facts": ["外部人天採同一範圍的合理高值。"],
        "choices": ["確認並產生交付成果", "工作範圍需要調整", "其他（自行輸入）"],
        "next": "確認後，Agent 會生成 CSV、Markdown 與 HTML。", "requiresHuman": True,
    }
    state["gates"] = [
        {"number": index, "title": title, "state": "done" if index < 5 else "current" if index == 5 else "pending"}
        for index, title in enumerate(("提供案件資料", "選擇成果大方向並確認工作分工", "核對案件理解", "選擇採用方案", "確認工作內容與人天", "取得交付成果"), 1)
    ]
    return state

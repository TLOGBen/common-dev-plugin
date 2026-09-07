from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from helpers import complete_state
from case_state import (
    CaseError,
    atomic_json,
    cmd_answer,
    commit,
    item_days,
    load,
    validate_state,
)


class CaseStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "case"
        atomic_json(self.root / "assessment-state.json", complete_state())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def prepare_select_scenario(self) -> None:
        state = complete_state()
        state["status"] = "mapping"
        state["selectedScenarioId"] = None
        state["decisions"] = []
        state["currentDecision"] = {
            "id": "select-scenario",
            "title": "選擇採用方案",
            "whyHuman": "方案會改變成果與人天。",
            "factsTitle": "方案差異",
            "facts": ["兩案已用相同口徑比較。"],
            "choices": ["採用相容遷移", "其他（自行輸入）"],
            "scenarioChoices": {"採用相容遷移": "scenario-a"},
            "next": "選定後建立成功鏈。",
            "requiresHuman": True,
        }
        state["gates"] = [
            {
                "number": index,
                "title": title,
                "state": "done" if index < 4 else "current" if index == 4 else "pending",
            }
            for index, title in enumerate(
                (
                    "提供案件資料",
                    "選擇成果大方向並確認工作分工",
                    "核對案件理解",
                    "選擇採用方案",
                    "確認工作內容與人天",
                    "取得交付成果",
                ),
                1,
            )
        ]
        atomic_json(self.root / "assessment-state.json", state)

    def test_complete_state_is_valid_and_uses_high_external_total(self) -> None:
        state = load(self.root)
        errors, warnings = validate_state(state)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        self.assertEqual({"low": 1.5, "baseline": 3.0, "high": 4.5}, item_days(state["workItems"][1]))

    def test_revision_conflict_preserves_last_good(self) -> None:
        state = load(self.root)
        candidate = copy.deepcopy(state)
        candidate["name"] = "新版名稱"
        with self.assertRaises(CaseError):
            commit(self.root, candidate, expected_revision=7)
        self.assertEqual("示範案件", load(self.root)["name"])

    def test_quantity_conservation_and_unique_coverage_are_enforced(self) -> None:
        state = load(self.root)
        state["successChain"]["nodes"][1]["total"] = 5
        state["workItems"].append(copy.deepcopy(state["workItems"][1]) | {"id": "duplicate-actions"})
        errors, _ = validate_state(state)
        self.assertTrue(any("數量不守恆" in error for error in errors))
        self.assertTrue(any("恰好由一個" in error for error in errors))

    def test_half_day_rates_are_enforced(self) -> None:
        state = load(self.root)
        state["workItems"][0]["unitDays"]["high"] = 5.25
        errors, _ = validate_state(state)
        self.assertTrue(any("0.5 日倍數" in error for error in errors))

    def test_development_and_testing_split_must_reconcile_to_unit_days(self) -> None:
        state = load(self.root)
        state["workItems"][0]["effortSplit"]["development"]["high"] = 3.5

        errors, _ = validate_state(state)

        self.assertTrue(any("開發＋測試人天必須等於 unitDays" in error for error in errors))

    def test_development_and_testing_split_use_half_day_units(self) -> None:
        state = load(self.root)
        state["workItems"][0]["effortSplit"]["development"]["high"] = 4.25

        errors, _ = validate_state(state)

        self.assertTrue(any("開發人天.high 必須是 0.5 日倍數" in error for error in errors))

    def test_external_summary_validation_distinguishes_allow_warn_and_block(self) -> None:
        short_summary = "調整共用機制並維持功能正常"
        state = load(self.root)
        state["clientPackages"][0]["externalSummary"] = short_summary

        warned = commit(self.root, state, expected_revision=8)

        self.assertEqual(9, warned["revision"])
        self.assertTrue(any("對外功能說明可能過短" in warning for warning in warned["warnings"]))
        self.assertEqual(short_summary, load(self.root)["clientPackages"][0]["externalSummary"])

        valid_summary = complete_state()["clientPackages"][0]["externalSummary"]
        state = load(self.root)
        state["clientPackages"][0]["externalSummary"] = valid_summary

        allowed = commit(self.root, state, expected_revision=9)

        self.assertEqual(10, allowed["revision"])
        self.assertFalse(any("對外功能說明" in warning for warning in allowed["warnings"]))

        for blocked_summary in ("第一段\n第二段", "調整" * 111):
            state = load(self.root)
            state["clientPackages"][0]["externalSummary"] = blocked_summary
            with self.assertRaises(CaseError):
                commit(self.root, state, expected_revision=10)
            persisted = load(self.root)
            self.assertEqual(10, persisted["revision"])
            self.assertEqual(valid_summary, persisted["clientPackages"][0]["externalSummary"])

    def test_explicit_pricing_units_drive_totals_instead_of_kind_guessing(self) -> None:
        state = load(self.root)
        item = state["workItems"][1]
        item["kind"] = "exception"
        item["needsChange"] = 3
        item["pricingUnits"] = 1

        self.assertEqual({"low": 0.5, "baseline": 1.0, "high": 1.5}, item_days(item))

    def test_pricing_units_cannot_exceed_items_needing_change(self) -> None:
        state = load(self.root)
        state["workItems"][1]["pricingUnits"] = 4

        errors, _ = validate_state(state)

        self.assertTrue(any("pricingUnits 不可大於需處理數" in error for error in errors))

    def test_draft_can_be_saved_while_readiness_gaps_are_warnings(self) -> None:
        state = load(self.root)
        state["status"] = "draft"
        state["selectedScenarioId"] = None
        state["successChain"]["nodes"][1]["status"] = "fog"
        state["dependencies"] = []

        result = commit(self.root, state, expected_revision=8)

        self.assertEqual(9, result["revision"])
        errors, warnings = validate_state(load(self.root))
        self.assertEqual([], errors)
        self.assertTrue(any("尚未選定方案" in warning for warning in warnings))
        self.assertTrue(any("未收斂節點" in warning for warning in warnings))

    def test_formal_state_requires_selected_scenario_and_converged_chain(self) -> None:
        state = complete_state()
        state["selectedScenarioId"] = None
        state["successChain"]["nodes"][1]["status"] = "fog"

        errors, _ = validate_state(state)

        self.assertTrue(any("PM 已選定的方案" in error for error in errors))
        self.assertTrue(any("尚未收斂" in error for error in errors))

    def test_selected_scenario_requires_explicit_pm_decision_record(self) -> None:
        state = complete_state()
        state["decisions"] = [
            row for row in state["decisions"]
            if row.get("decisionId") != "select-scenario"
        ]

        errors, _ = validate_state(state)

        self.assertTrue(any("PM 明確選案" in error for error in errors))

    def test_formal_state_requires_gate_two_outcome_direction_decision(self) -> None:
        state = complete_state()
        state["decisions"] = [
            row for row in state["decisions"]
            if row.get("decisionId") != "select-outcome-direction"
        ]

        errors, _ = validate_state(state)

        self.assertTrue(any("Gate 2 確認成果大方向" in error for error in errors))

    def test_open_important_pm_decision_blocks_formal_estimate(self) -> None:
        state = complete_state()
        state["fogs"] = [
            {
                "id": "spring-boot-target",
                "status": "open",
                "requiresHuman": True,
                "blocksReadiness": True,
                "impact": "改變 Jakarta 遷移與人天",
            }
        ]

        errors, _ = validate_state(state)

        self.assertTrue(any("重要 PM 決定尚未確認" in error for error in errors))

    def test_choice_details_must_reference_visible_choice(self) -> None:
        state = complete_state()
        state["currentDecision"]["choiceDetails"] = {
            "畫面上不存在的選項": {"summary": "不應被投影"}
        }

        errors, _ = validate_state(state)

        self.assertTrue(any("choiceDetails 選項不在 choices" in error for error in errors))

    def test_record_answer_sets_selected_scenario_and_records_provenance(self) -> None:
        self.prepare_select_scenario()

        accepted = cmd_answer(SimpleNamespace(
            case_root=self.root,
            decision_id="select-scenario",
            answer="採用相容遷移",
            note=None,
            decided_by="PM（聊天確認）",
            expected_revision=8,
        ))
        selected = load(self.root)

        self.assertTrue(accepted["ok"])
        self.assertEqual(9, accepted["revision"])
        self.assertEqual("scenario-a", selected["selectedScenarioId"])
        self.assertEqual("scenario-a", selected["decisions"][-1]["selectedScenarioId"])
        self.assertEqual("done", selected["gates"][3]["state"])

    def test_formal_upgrade_state_requires_dependency_behavior_evidence(self) -> None:
        state = complete_state()
        state["dependencies"] = []

        errors, _ = validate_state(state)

        self.assertTrue(any("dependency behavior 證據" in error for error in errors))

    def test_technical_fog_blocks_readiness_without_interrupting_pm(self) -> None:
        state = complete_state()
        state["fogs"] = [
            {
                "id": "runtime-semantics",
                "status": "open",
                "requiresHuman": False,
                "blocksReadiness": True,
                "impact": "可能推翻目前 ORM 目標線",
            }
        ]

        errors, _ = validate_state(state)

        self.assertTrue(any("關鍵事實尚未收斂" in error for error in errors))
        self.assertFalse(any("重要 PM 決定" in error for error in errors))

    def test_querydsl_like_dependency_requires_supported_selected_target(self) -> None:
        state = complete_state()
        dependency = state["dependencies"][0]
        dependency["component"] = "QueryDSL"
        dependency["maintenanceStatus"] = "unknown"
        dependency["compatibilityClaims"][0]["status"] = "unsupported"
        dependency["resolution"]["strategy"] = "unresolved"
        dependency["resolution"]["status"] = "unresolved"
        dependency["blocksScenario"] = True

        errors, _ = validate_state(state)

        self.assertTrue(any("尚未確認上游維護狀態" in error for error in errors))
        self.assertTrue(any("採用目標仍未具備可承諾的相容性" in error for error in errors))
        self.assertTrue(any("採用路線尚未收斂" in error for error in errors))
        self.assertTrue(any("仍會推翻目前方案" in error for error in errors))

    def test_non_querydsl_codegen_dependency_uses_the_same_generic_guard(self) -> None:
        state = complete_state()
        dependency = state["dependencies"][0]
        dependency["component"] = "報表模板產碼器"
        dependency.pop("footprint")

        errors, _ = validate_state(state)

        self.assertTrue(any("缺少完整使用足跡" in error for error in errors))

    def test_upstream_maintainer_and_internal_owner_are_distinct_required_facts(self) -> None:
        state = complete_state()
        state["dependencies"][0]["upstreamMaintainer"] = ""
        state["dependencies"][0]["internalOwner"] = ""

        errors, _ = validate_state(state)

        self.assertTrue(any("上游維護者" in error for error in errors))
        self.assertTrue(any("內部工作責任" in error for error in errors))

    def test_dependency_coverage_must_name_every_decision_bearing_dependency(self) -> None:
        state = complete_state()
        state["dependencyCoverage"]["decisionBearingDependencyIds"] = []

        errors, _ = validate_state(state)

        self.assertTrue(any("完整列出所有會影響方案" in error for error in errors))

    def test_formal_state_requires_pm_readable_work_and_consistent_gates(self) -> None:
        state = complete_state()
        state["workItems"][0]["pmDescription"] = ""
        state["gates"][4]["state"] = "done"

        errors, _ = validate_state(state)

        self.assertTrue(any("PM 說明" in error for error in errors))
        self.assertTrue(any("PM gate 5 應為" in error for error in errors))

    def test_formal_state_requires_method_card_and_client_package(self) -> None:
        state = complete_state()
        state["workItems"][0]["changeMethod"] = ""
        state["workItems"][1]["clientPackageId"] = "missing-package"

        errors, _ = validate_state(state)

        self.assertTrue(any("實際改法" in error for error in errors))
        self.assertTrue(any("引用不存在 client package" in error for error in errors))

    def test_formal_state_requires_pm_drilldown_and_estimation_review(self) -> None:
        state = complete_state()
        state["outcome"]["pmCurrentState"] = ""
        state["workItems"][0]["pmChangeSummary"] = ""
        state["workItems"][0]["changeTargets"] = {}
        state["workItems"][0]["baselineRationale"] = ""
        state["estimationReview"] = {}

        errors, _ = validate_state(state)

        self.assertTrue(any("PM 現況結論" in error for error in errors))
        self.assertTrue(any("80～160 字修改重點" in error for error in errors))
        self.assertTrue(any("changeTargets.pages" in error for error in errors))
        self.assertTrue(any("基準人天理由" in error for error in errors))
        self.assertTrue(any("估算模型反證" in error for error in errors))

    def test_critical_finding_must_trace_to_evidence_and_package(self) -> None:
        state = complete_state()
        finding = state["estimationReview"]["criticalFindings"][0]
        finding["clientPackageIds"] = ["missing-package"]
        finding["evidenceIds"] = ["missing-evidence"]

        errors, _ = validate_state(state)

        self.assertTrue(any("引用不存在 client package" in error for error in errors))
        self.assertTrue(any("引用不存在 evidence" in error for error in errors))

    def test_scope_delta_count_must_match_the_named_target_list(self) -> None:
        state = complete_state()
        state["detailCatalogs"][1]["items"].pop()

        errors, _ = validate_state(state)

        self.assertTrue(any("證據確認 3 項，但 canonical direct-touch 清單只有 2 項" in error for error in errors))

    def test_direct_touch_catalog_blocks_gate_five_when_claimed_count_does_not_match(self) -> None:
        state = complete_state()
        state["detailCatalogs"][1]["items"].pop()

        errors, _ = validate_state(state)

        self.assertTrue(any("claimedCount 3 與完整 items 2 不一致" in error for error in errors))

    def test_formal_state_requires_referenced_unique_canonical_catalogs(self) -> None:
        state = complete_state()
        state["workItems"][0]["detailCatalogIds"] = []
        state["detailCatalogs"][1]["items"][0]["id"] = "catalog-actions-direct"

        errors, _ = validate_state(state)

        self.assertTrue(any("缺少 canonical detailCatalogIds" in error for error in errors))
        self.assertTrue(any("detail catalog catalog-foundation-scope 沒有 work item 引用" in error for error in errors))
        self.assertTrue(any("canonical detail id 重複" in error for error in errors))

    def test_generated_catalog_requires_one_reproducible_generation_contract(self) -> None:
        state = complete_state()
        generated = {
            "id": "catalog-generated-models", "name": "產生模型", "treatment": "generated",
            "origin": "discovery", "completeness": "summary", "claimedCount": 136,
            "pricingRole": "scope-evidence", "generation": {"source": "Entity", "method": "", "verification": "編譯通過"},
        }
        state["detailCatalogs"].append(generated)
        state["workItems"][0]["detailCatalogIds"].append(generated["id"])

        errors, _ = validate_state(state)

        self.assertTrue(any("缺少產製方式" in error for error in errors))

    def test_upgrade_near_historical_build_requires_rebuild_outcome_explanation(self) -> None:
        state = complete_state()
        state["calibration"] = {
            "referenceAvailable": True,
            "label": "原系統總建置",
            "referenceDays": 10,
            "scope": "同一應用總建置報價",
            "source": "PM 提供的歷史報價",
            "comparisonConclusion": "本次高值接近歷史建置成本",
        }

        errors, _ = validate_state(state)

        self.assertTrue(any("重建型成果" in error for error in errors))

        state["calibration"]["rebuildLikeOutcome"] = "本次另建立新的部署與契約能力。"
        errors, _ = validate_state(state)
        self.assertEqual([], errors)

    def test_complete_state_requires_confirmation_record_and_all_gates_done(self) -> None:
        state = complete_state()
        state["status"] = "complete"
        state["currentDecision"] = None
        for gate in state["gates"]:
            gate["state"] = "done"
        state["decisions"] = [
            *state["decisions"],
            {"decisionId": "confirm-estimate", "answer": "確認"},
        ]

        errors, warnings = validate_state(state)

        self.assertEqual([], errors)
        self.assertEqual([], warnings)

if __name__ == "__main__":
    unittest.main()

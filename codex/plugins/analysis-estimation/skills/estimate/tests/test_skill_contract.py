from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_pm_pause_contract_is_routed_and_outcome_driven(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        guide = (SKILL_ROOT / "references" / "pm-decision-pauses.md").read_text(encoding="utf-8")

        self.assertIn("references/pm-decision-pauses.md", skill)
        self.assertIn("Gate 是交還承諾權的停等點", skill)
        self.assertIn("不同答案會實質改變", guide)
        self.assertIn("Agent 的建議", guide)
        self.assertIn("其他（自行輸入）", guide)
        self.assertIn("一般情況作為完成狀態而非停等", guide)

    def test_parallel_inventory_uses_bounded_clean_luna_max_sidekicks(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        guide = (SKILL_ROOT / "references" / "inventory-sidekick-brief.md").read_text(encoding="utf-8")

        self.assertIn("Gate 2 大方向確認後", skill)
        self.assertIn("3–5 個唯讀 sidekick", skill)
        self.assertIn('fork_turns="none"', guide)
        self.assertIn('model="gpt-5.6-luna"', guide)
        self.assertIn('reasoning_effort="max"', guide)
        self.assertIn("不寫案件主檔", skill)
        self.assertIn("主 Agent 收件後", guide)

    def test_chat_is_the_primary_pm_decision_entry(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        pauses = (SKILL_ROOT / "references" / "pm-decision-pauses.md").read_text(encoding="utf-8")

        self.assertIn("聊天是 V3 的主要決策介面", skill)
        self.assertIn("聊天中的決策接續", skill)
        self.assertIn("目前聊天作為 PM 決策入口", pauses)
        self.assertIn("使用者主動在聊天給出的明確答案可直接接受", skill)

    def test_pm_answer_automatically_advances_to_the_next_actionable_ticket(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Agent 擁有票與票之間的推進責任", skill)
        self.assertIn("以 `record-answer` 寫回同一案件 revision", skill)
        self.assertIn("只有抵達下一個真正的 PM 決定或完整完成時才交還控制權", skill)
        self.assertIn("避免 PM 與 Agent 在兩張票之間互相等待", skill)

    def test_wayfinder_and_ascii_are_default_after_gate_two(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        ascii_guide = (SKILL_ROOT / "references" / "ascii-visuals.md").read_text(encoding="utf-8")

        self.assertIn("直接呼叫 `$wayfinder`", skill)
        self.assertIn("canonical Markdown map／tickets", skill)
        self.assertIn("以簡短 ASCII 圖投影在聊天與 Markdown", skill)
        self.assertIn("一張圖只回答一個問題", ascii_guide)

    def test_chat_wayfinder_and_ascii_form_the_complete_core_interface(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("讓 PM 在同一個決策介面完成理解、選擇與追問", skill)
        self.assertIn("聊天是 V3 的主要決策介面", skill)
        self.assertIn("canonical Markdown map／tickets", skill)

    def test_ambiguous_scenario_terms_are_explained_before_selection(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        pauses = (SKILL_ROOT / "references" / "pm-decision-pauses.md").read_text(encoding="utf-8")
        scenario = (SKILL_ROOT / "references" / "scenario-guide.md").read_text(encoding="utf-8")

        self.assertIn("第一次出現時就先翻成白話", skill)
        self.assertIn("正式交付幾個版本", skill)
        self.assertIn("第一次就解釋方案語言", pauses)
        self.assertIn("使 PM 的第一次答案就是知情選擇", pauses)
        self.assertIn("開發與驗證依可獨立檢查的步驟前進", scenario)
        self.assertIn("不要只在 PM 追問後才說明", scenario)

    def test_dependency_analysis_is_autonomous_generic_and_falsifiable(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        guide = (SKILL_ROOT / "references" / "dependency-behavior.md").read_text(encoding="utf-8")

        self.assertIn("把選定方向當成待驗證假說", skill)
        self.assertIn("依賴可持續性反證", skill)
        self.assertIn("什麼事實會讓目標版本不可採用", skill)
        self.assertIn("上游維護者與我方改造責任", skill)
        self.assertIn("QueryDSL 是一個回歸案例，不是特別寫死的判斷規則", guide)
        self.assertIn("報表引擎、序列化元件、認證 adapter", guide)
        self.assertIn("`blocksReadiness`", guide)

    def test_deliverable_guide_contains_customer_facing_and_internal_examples(self) -> None:
        guide = (SKILL_ROOT / "references" / "deliverables.md").read_text(encoding="utf-8")

        self.assertIn("### 真實報價用詞範例", guide)
        self.assertIn("現行程式升級 JDK 21", guide)
        self.assertIn("帳單業者端－後端開源軟體提升", guide)
        self.assertIn("### 真實內部細項如何收斂成一列", guide)
        self.assertIn("### 對外一列的語意契約", guide)
        self.assertIn("改造範圍、至少兩個主要動作、白話費用驅動與完成結果", guide)
        self.assertIn("fresh reader 作語意 eval", guide)
        self.assertIn("clientPackageId", guide)

    def test_estimation_uses_team_delivery_units_before_technical_occurrences(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        guide = (SKILL_ROOT / "references" / "estimation-guide.md").read_text(encoding="utf-8")

        self.assertIn("用團隊真正承作的單位估價", skill)
        self.assertIn("從技術盤點轉成團隊報價", skill)
        self.assertIn("先決定「團隊如何承作」，再決定乘數", guide)
        self.assertIn("一次性底座 + Σ(一般功能族 × 一般單價)", guide)
        self.assertIn("歷史數字是校準訊號，不是倒填目標", guide)

    def test_gate_five_explains_each_client_package_before_total_confirmation(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        guide = (SKILL_ROOT / "references" / "estimation-guide.md").read_text(encoding="utf-8")
        pauses = (SKILL_ROOT / "references" / "pm-decision-pauses.md").read_text(encoding="utf-8")
        deliverables = (SKILL_ROOT / "references" / "deliverables.md").read_text(encoding="utf-8")

        self.assertIn("Gate 5 詢問 PM 是否核准總人天以前", skill)
        self.assertIn("PG 實際要做哪些工作", skill)
        self.assertIn("資訊完整與可轉述優先於精確字數", skill)
        self.assertIn("Gate 5 的成果包白話說明卡", guide)
        self.assertIn("為何這樣拆開發／測試", guide)
        self.assertIn("詢問 PM 是否確認總人天之前", pauses)
        self.assertIn("PM 看完後能逐包回答", pauses)
        self.assertIn("成果包短卡是 PM 說明層", deliverables)


if __name__ == "__main__":
    unittest.main()

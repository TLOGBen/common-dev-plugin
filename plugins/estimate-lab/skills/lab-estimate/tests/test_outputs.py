from __future__ import annotations

import csv
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from helpers import complete_state
from case_state import atomic_json, item_days
from generate_outputs import generate


def markdown_h2_sections(document: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in document.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {heading: "\n".join(lines) for heading, lines in sections.items()}


class ReportProjectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.openers: list[str] = []
        self.dialogs: dict[str, dict[str, list[str]]] = {}
        self.current_dialog: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "button" and "package-row" in classes:
            self.openers.append(attributes.get("data-dialog") or "")
        if tag == "dialog" and "package-dialog" in classes:
            self.current_dialog = attributes.get("id")
            if self.current_dialog:
                self.dialogs[self.current_dialog] = {"closeRoles": [], "findingIds": [], "text": []}
        if self.current_dialog and tag == "button" and "data-close" in attributes:
            for role in ("icon-close", "return-button"):
                if role in classes:
                    self.dialogs[self.current_dialog]["closeRoles"].append(role)
        finding_id = attributes.get("data-finding-id")
        if self.current_dialog and finding_id:
            self.dialogs[self.current_dialog]["findingIds"].append(finding_id)

    def handle_endtag(self, tag: str) -> None:
        if tag == "dialog":
            self.current_dialog = None

    def handle_data(self, data: str) -> None:
        if self.current_dialog and data.strip():
            self.dialogs[self.current_dialog]["text"].append(data.strip())


class OutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "case"
        atomic_json(self.root / "assessment-state.json", complete_state())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_csv_markdown_and_html_are_generated_without_office(self) -> None:
        report = generate(self.root, None)
        self.assertEqual(8, report["stateRevision"])
        for name in ("assessment-report.md", "assessment-report.html", "estimate-internal.csv", "estimate-external.csv"):
            self.assertTrue((self.root / "outputs" / name).is_file())

    def test_html_uses_the_bundled_report_template(self) -> None:
        template = Path(__file__).resolve().parents[1] / "assets" / "assessment-report-template.html"
        generator = (Path(__file__).resolve().parents[1] / "scripts" / "generate_outputs.py").read_text(encoding="utf-8")

        self.assertTrue(template.is_file())
        self.assertIn("$title", template.read_text(encoding="utf-8"))
        self.assertIn("$body", template.read_text(encoding="utf-8"))
        self.assertIn('assets" / "assessment-report-template.html', generator)

    def test_external_csv_is_customer_facing_five_column_high_estimate(self) -> None:
        generate(self.root, None)
        path = self.root / "outputs" / "estimate-external.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream))
        self.assertEqual(["序號", "系統功能", "功能說明", "開發人天", "測試人天"], rows[0])
        self.assertEqual(["1", "2"], [row[0] for row in rows[1:]])
        self.assertEqual("4.0", rows[1][3])
        self.assertEqual("1.0", rows[1][4])
        self.assertEqual("3.0", rows[2][3])
        self.assertEqual("1.5", rows[2][4])
        self.assertEqual(9.5, sum(float(row[3]) + float(row[4]) for row in rows[1:]))
        joined = "\n".join(",".join(row) for row in rows)
        self.assertNotIn("低人天", joined)
        self.assertNotIn("基準", joined)
        self.assertNotIn("範圍證據", joined)
        self.assertNotIn("工程工作數", joined)
        self.assertNotIn("ProjectAlpha", joined)
        self.assertNotIn("Secret123", joined)
        self.assertTrue(all("\n" not in row[2] and len(row[2]) <= 220 for row in rows[1:]))

    def test_internal_csv_keeps_the_auditable_effort_split(self) -> None:
        generate(self.root, None)
        path = self.root / "outputs" / "estimate-internal.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream))

        for label in ("開發低", "開發基準", "開發高", "測試低", "測試基準", "測試高"):
            self.assertIn(label, rows[0])
        self.assertTrue(all(len(row) == len(rows[0]) for row in rows))

    def test_dependency_assumptions_are_projected_under_the_pm_risk_section(self) -> None:
        state = complete_state()
        atomic_json(self.root / "assessment-state.json", state)
        generate(self.root, None)
        report = (self.root / "outputs" / "assessment-report.md").read_text(encoding="utf-8")
        sections = markdown_h2_sections(report)
        dependency_section = sections["會讓方案失敗或加價的前提"]
        estimate_section = sections["評估項目與人天"]
        coverage = state["dependencyCoverage"]

        self.assertIn(coverage["discoveryMethod"], dependency_section)
        self.assertIn(str(coverage["componentCount"]), dependency_section)
        self.assertIn(coverage["boundary"], dependency_section)
        for dependency in state["dependencies"]:
            resolution = dependency["resolution"]
            for visible_value in (
                dependency["component"], resolution["selectedTarget"], dependency["upstreamMaintainer"],
                dependency["internalOwner"], dependency["probe"],
            ):
                self.assertIn(visible_value, dependency_section)
                self.assertNotIn(visible_value, estimate_section)
            self.assertIn("策略為 沿用", dependency_section)

    def test_report_leads_with_summary_then_estimates_and_keeps_findings_contextual(self) -> None:
        generate(self.root, None)
        markdown = (self.root / "outputs" / "assessment-report.md").read_text(encoding="utf-8")
        rendered = (self.root / "outputs" / "assessment-report.html").read_text(encoding="utf-8")

        self.assertLess(markdown.index("本次升版摘要"), markdown.index("評估項目與人天"))
        self.assertLess(markdown.index("評估項目與人天"), markdown.index("技術證據附錄"))
        self.assertLess(rendered.index('class="summary-panel"'), rendered.index('class="estimate-section"'))
        self.assertLess(rendered.index('class="estimate-section"'), rendered.index('class="technical-appendix"'))
        self.assertIn("功能入口比需求初看多一支", rendered)
        dialog_position = rendered.index('id="package-package-entry-dialog"')
        self.assertGreater(rendered.index("功能入口比需求初看多一支"), dialog_position)
        self.assertNotIn("功能入口比需求初看多一支", rendered[:dialog_position])

    def test_package_rows_project_one_owned_dialog_with_controls_and_detail(self) -> None:
        state = complete_state()
        sensitive_package_id = "package-runtime"
        state["clientPackages"][0]["externalSummary"] = (
            "調整 C:\\ProjectAlpha\\private\\Controller.java 的共用承接機制，"
            "以 password=Secret123 完成設定並驗證既有功能。"
        )
        atomic_json(self.root / "assessment-state.json", state)
        generate(self.root, None)
        rendered = (self.root / "outputs" / "assessment-report.html").read_text(encoding="utf-8")
        parser = ReportProjectionParser()
        parser.feed(rendered)

        expected_dialog_ids = [f"package-{package['id']}-dialog" for package in state["clientPackages"]]
        self.assertEqual(expected_dialog_ids, parser.openers)
        self.assertEqual(set(expected_dialog_ids), set(parser.dialogs))

        findings = state["estimationReview"]["criticalFindings"]
        for package, dialog_id in zip(state["clientPackages"], expected_dialog_ids):
            dialog = parser.dialogs[dialog_id]
            text = " ".join(dialog["text"])
            self.assertEqual(["icon-close", "return-button"], dialog["closeRoles"])
            self.assertEqual(
                [finding["id"] for finding in findings if package["id"] in finding["clientPackageIds"]],
                dialog["findingIds"],
            )
            if package["id"] == sensitive_package_id:
                self.assertIn("[本機路徑已移除]", text)
                self.assertIn("password=[REDACTED]", text)
                self.assertNotIn("ProjectAlpha", text)
                self.assertNotIn("Secret123", text)
            else:
                self.assertIn(package["externalSummary"], text)
            items = [item for item in state["workItems"] if item["clientPackageId"] == package["id"]]
            totals = {tier: sum(item_days(item)[tier] for item in items) for tier in ("low", "baseline", "high")}
            for label, tier in (("低值", "low"), ("基準值", "baseline"), ("高值", "high")):
                self.assertIn(f"{label} {totals[tier]}", text)
            for item in items:
                for target_type in ("pages", "apis", "files"):
                    for target in item["changeTargets"][target_type]:
                        self.assertIn(target, text)
                self.assertIn(item["baselineRationale"], text)

    def test_only_explanatory_visuals_are_rendered_and_are_accessible(self) -> None:
        generate(self.root, None)
        rendered = (self.root / "outputs" / "assessment-report.html").read_text(encoding="utf-8")

        self.assertEqual(1, rendered.count('<svg class="explanation-visual"'))
        self.assertNotIn("這張圖只回答：這包從哪個問題出發", rendered)
        self.assertIn('role="img"', rendered)
        self.assertIn("共用底座如何承接既有入口", rendered)
        self.assertIn("為什麼底座只做一次", rendered)

    def test_internal_csv_keeps_pm_drilldown_fields(self) -> None:
        generate(self.root, None)
        path = self.root / "outputs" / "estimate-internal.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream))

        for label in ("修改重點", "影響頁面", "影響 API", "對應檔案", "基準人天理由"):
            self.assertIn(label, rows[0])

    def test_report_projects_direct_generated_and_evidence_worksets_from_state(self) -> None:
        state = complete_state()
        direct_87 = {
            "id": "catalog-query-files", "name": "QueryDSL 使用檔", "treatment": "direct-touch",
            "origin": "discovery", "completeness": "complete", "claimedCount": 87,
            "pricingRole": "scope-evidence",
            "items": [
                {"id": f"query-file-{index:03d}", "name": f"backend/dao/Query{index:03d}.java",
                 "purpose": "資料查詢", "action": "batch-change", "changeDetail": "套用共同相容調整。",
                 "verification": "查詢結果與舊版一致。"}
                for index in range(1, 88)
            ],
        }
        generated_136 = {
            "id": "catalog-q-types", "name": "歷史 Q 類", "treatment": "generated",
            "origin": "discovery", "completeness": "summary", "claimedCount": 136,
            "pricingRole": "scope-evidence",
            "generation": {"source": "Entity 與 APT 設定", "method": "clean 後重新產製", "verification": "核對 136 項並編譯"},
        }
        direct_13 = {
            "id": "catalog-integrations", "name": "整合通道", "treatment": "direct-touch",
            "origin": "discovery", "completeness": "complete", "claimedCount": 13,
            "pricingRole": "pricing-unit",
            "items": [
                {"id": f"integration-{index:02d}", "name": f"通道 {index}", "purpose": "外部整合",
                 "action": "high-risk-verify", "changeDetail": "核對相容設定。", "verification": "正反情境通過。"}
                for index in range(1, 14)
            ],
        }
        state["detailCatalogs"].extend([direct_87, generated_136, direct_13])
        state["workItems"][1]["detailCatalogIds"].extend([direct_87["id"], generated_136["id"], direct_13["id"]])
        atomic_json(self.root / "assessment-state.json", state)

        generate(self.root, None)
        rendered = (self.root / "outputs" / "assessment-report.html").read_text(encoding="utf-8")

        direct_start = rendered.index('data-workset-items="87"')
        direct_end = rendered.index("</details>", direct_start)
        self.assertEqual(87, rendered[direct_start:direct_end].count("data-workset-item="))
        generated_start = rendered.index('data-generated-count="136"')
        generated_end = rendered.index("</details>", generated_start)
        self.assertEqual(0, rendered[generated_start:generated_end].count("data-workset-item="))
        self.assertIn("不代表 136 次人工修改", rendered[generated_start:generated_end])
        integration_start = rendered.index('data-workset-items="13"')
        integration_end = rendered.index("</details>", integration_start)
        self.assertEqual(13, rendered[integration_start:integration_end].count("data-workset-item="))
        self.assertIn("範圍證據，不作人工乘數", rendered)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from helpers import complete_state
from case_state import atomic_json
from generate_outputs import generate


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

    def test_report_explains_dependency_coverage_maintenance_and_selected_strategy(self) -> None:
        generate(self.root, None)
        report = (self.root / "outputs" / "assessment-report.md").read_text(encoding="utf-8")

        self.assertIn("依賴盤點範圍", report)
        self.assertIn("上游專案維護者", report)
        self.assertIn("我方資料層團隊", report)
        self.assertIn("策略為 沿用", report)


if __name__ == "__main__":
    unittest.main()

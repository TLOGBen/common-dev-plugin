from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from helpers import complete_state
from case_state import atomic_json
from feedback import FeedbackError, capabilities, prepare, publish


class FeedbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "case"
        state = complete_state()
        state["caseId"] = "customer-alpha"
        state["name"] = "客戶甲專案"
        atomic_json(self.root / "assessment-state.json", state)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_prepare_keeps_local_context_but_central_issue_only_has_root_cause(self) -> None:
        result = prepare(argparse.Namespace(
            case_root=self.root,
            task="在客戶甲專案產生人天評估",
            friction="Agent 一直探索 C:\\customer-alpha\\runtime.log",
            impact="PM 無法知道目前要做什麼",
            expected="先顯示 PM 當前任務",
            root_cause="客戶甲專案的決策流程缺少以使用者任務為中心的資訊路由",
            reproduction="以 customer-alpha 案件開啟 http://10.1.2.3/internal",
            evidence_strength="single-case",
            sensitive_term=[],
        ))
        packet = json.loads(Path(result["json"]).read_text(encoding="utf-8"))
        self.assertIn("客戶甲專案", packet["localCard"]["task"])
        issue = packet["issueDraft"]["body"]
        self.assertNotIn("客戶甲專案", issue)
        self.assertNotIn("customer-alpha", issue)
        self.assertNotIn("10.1.2.3", issue)
        self.assertNotIn("C:\\", issue)
        self.assertIn("[PROJECT REMOVED]", issue)

    def test_issue_is_optional_and_publish_requires_confirmation(self) -> None:
        result = capabilities(argparse.Namespace())
        self.assertFalse(result["issueRequired"])
        with self.assertRaises(FeedbackError):
            publish(argparse.Namespace(packet=Path("missing.json"), tracker="gh", repo="owner/repo", confirmed=False))


if __name__ == "__main__":
    unittest.main()

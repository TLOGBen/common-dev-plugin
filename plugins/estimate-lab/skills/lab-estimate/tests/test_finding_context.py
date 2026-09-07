from __future__ import annotations

import unittest

from helpers import complete_state
from generate_outputs import report_html, report_markdown


class FindingContextTests(unittest.TestCase):
    def test_approved_and_delivered_estimates_do_not_reissue_old_approval_reminders(self):
        for status in ("estimate-approved", "complete"):
            state = complete_state()
            state["status"] = status
            original = state["estimationReview"]["criticalFindings"][0]["treatment"]
            for document in (report_markdown(state), report_html(state, "合成測試")):
                with self.subTest(status=status, format="html" if "<html" in document else "markdown"):
                    self.assertTrue("原評估處理紀錄" in document, "missing historical finding label")
                    self.assertIn("核准提醒不是新待辦", document)
                    self.assertIn("部署、UAT 等條件不因核准而自動完成", document)
                    self.assertIn(original, document)
                    self.assertNotIn("PM 現在要注意什麼", document)

    def test_pending_estimate_keeps_current_reminder_without_claiming_approval(self):
        state = complete_state()
        for document in (report_markdown(state), report_html(state, "合成測試")):
            self.assertIn("PM 現在要注意什麼", document)
            self.assertNotIn("核准提醒不是新待辦", document)


if __name__ == "__main__":
    unittest.main()

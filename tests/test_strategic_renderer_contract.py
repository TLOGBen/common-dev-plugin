import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/common/skills/strategic-advance/scripts/strategic_state.py"
STATE = ROOT / "plugins/common/skills/strategic-advance/references/example-state.json"


class StrategicRendererContractTest(unittest.TestCase):
    def run_script(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_self_test_restores_all_presentation_cases(self):
        result = self.run_script("self-test", str(STATE))
        self.assertEqual(0, result.returncode, result.stderr)
        cases = result.stdout.strip().split("cases=", 1)[1].split(",")
        self.assertEqual(87, len(cases))
        for name in (
            "bda-no-false-pass",
            "takeover-action-gates-visible",
            "bda-action-gates-hidden",
            "no-intervention-action-gates-hidden",
            "public-dashboard-language-and-live-clock",
            "technical-default-open-and-recovery-layout",
            "localized-title-and-expandable-history",
        ):
            self.assertIn(name, cases)

    def test_render_is_self_contained_and_bilingual(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for language, html_lang, title in (
                ("zh-TW", "zh-TW", "戰略推進沙盤"),
                ("en", "en", "Strategic Advance Sand Table"),
            ):
                output = root / f"sand-table-{language}.html"
                result = self.run_script(
                    "render",
                    str(STATE),
                    str(output),
                    "--language",
                    language,
                    "--no-open",
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("SAND_TABLE_RENDERED", result.stdout)
                self.assertNotIn("renderer=sdk", result.stdout)
                html = output.read_text(encoding="utf-8")
                self.assertIn(f'<html lang="{html_lang}">', html)
                self.assertIn(title, html)
                self.assertIn("<style>", html)
                self.assertIn("<script>", html)

    def test_render_all_writes_html_and_svg_without_sdk_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifacts"
            result = self.run_script(
                "render-all",
                str(STATE),
                str(output),
                "--language",
                "zh-TW",
                "--no-open",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("STRATEGIC_ARTIFACTS_RENDERED", result.stdout)
            self.assertNotIn("renderer=sdk", result.stdout)
            self.assertTrue((output / "sand-table.html").is_file())
            self.assertTrue((output / "battle-map.svg").is_file())


if __name__ == "__main__":
    unittest.main()

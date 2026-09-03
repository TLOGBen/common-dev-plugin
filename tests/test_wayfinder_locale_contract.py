import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "plugins/common/skills/wayfinder/scripts/render_map.py"


class WayfinderLocaleContractTests(unittest.TestCase):
    def make_effort(self, root: Path) -> Path:
        effort = root / "effort"
        issues = effort / "issues"
        issues.mkdir(parents=True)
        (effort / "map.md").write_text(
            """# Locale check

## Destination

Reach the verified destination.

## Notes

- Keep the machine headings stable.

## Decisions so far

## Not yet specified

## Out of scope
""",
            encoding="utf-8",
        )
        (issues / "01-check-output.md").write_text(
            """# Check the output

Type: task
Status: open

## Question

Does the renderer use the selected interface language?
""",
            encoding="utf-8",
        )
        return effort

    def render(self, effort: Path, *arguments: str) -> str:
        output = effort / ("map-en.html" if "en" in arguments else "map.html")
        completed = subprocess.run(
            [sys.executable, str(RENDERER), str(effort), str(output), *arguments, "--no-open"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("wrote", completed.stdout)
        return output.read_text(encoding="utf-8")

    def run_renderer(self, effort: Path, output: Path | None = None) -> subprocess.CompletedProcess[str]:
        destination = output or effort / "map.html"
        return subprocess.run(
            [sys.executable, str(RENDERER), str(effort), str(destination), "--no-open"],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_default_interface_is_traditional_chinese(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            html = self.render(self.make_effort(Path(directory)))
        self.assertIn('<html lang="zh-Hant">', html)
        self.assertIn("決策路線圖", html)
        self.assertIn("決策票券", html)
        self.assertIn('"language": "zh-TW"', html)
        self.assertNotIn("__WF_", html)
        self.assertNotIn("L.meta(", html)

    def test_explicit_english_switches_interface_chrome(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            html = self.render(self.make_effort(Path(directory)), "--language", "en")
        self.assertIn('<html lang="en">', html)
        self.assertIn("Route chart", html)
        self.assertIn("Tickets", html)
        self.assertIn('"language": "en"', html)
        self.assertNotIn("__WF_", html)

    def test_untrusted_ticket_metadata_is_escaped_before_inner_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            effort = self.make_effort(Path(directory))
            (effort / "issues/01-check-output.md").write_text(
                """# Check the output

Type: </script><img src=x onerror=alert(1)>
Status: open
Blocked by: 02<img src=x onerror=alert(2)>

## Question

Does metadata stay inert?
""",
                encoding="utf-8",
            )
            html = self.render(effort)

        self.assertIn("<\\/script><img src=x onerror=alert(1)>", html)
        self.assertIn("${esc(t.id)}", html)
        self.assertIn("t.blockedBy.map(esc).join(', ')", html)
        self.assertIn("${esc(TYPE_LABEL[t.type]||t.type)}", html)

    def test_duplicate_ticket_ids_fail_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            effort = self.make_effort(Path(directory))
            (effort / "issues/01-second.md").write_text(
                """# Duplicate
Type: task
Status: open
Blocked by:

## Question
Should fail.
""",
                encoding="utf-8",
            )
            output = effort / "duplicate.html"
            completed = self.run_renderer(effort, output)

            self.assertEqual(1, completed.returncode)
            self.assertIn("WAYFINDER_DUPLICATE_TICKET_ID id=01", completed.stderr)
            self.assertFalse(output.exists())

    def test_blocking_cycle_fails_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            effort = self.make_effort(Path(directory))
            (effort / "issues/01-check-output.md").write_text(
                """# First
Type: task
Status: open
Blocked by: 02

## Question
First?
""",
                encoding="utf-8",
            )
            (effort / "issues/02-second.md").write_text(
                """# Second
Type: task
Status: open
Blocked by: 01

## Question
Second?
""",
                encoding="utf-8",
            )
            output = effort / "cycle.html"
            completed = self.run_renderer(effort, output)

            self.assertEqual(1, completed.returncode)
            self.assertIn("WAYFINDER_BLOCKING_CYCLE path=01->02->01", completed.stderr)
            self.assertFalse(output.exists())

    def test_default_output_replaces_symlink_without_overwriting_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            effort = self.make_effort(root)
            target = root / "outside.txt"
            target.write_text("ORIGINAL", encoding="utf-8")
            output = effort / "map.html"
            try:
                output.symlink_to(target)
            except OSError as error:
                self.skipTest(f"symlink unavailable: {error}")

            completed = self.run_renderer(effort)

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("ORIGINAL", target.read_text(encoding="utf-8"))
            self.assertTrue(output.is_file())
            self.assertFalse(output.is_symlink())


if __name__ == "__main__":
    unittest.main()

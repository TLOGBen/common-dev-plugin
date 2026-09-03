import json
import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class DelegateFastContractTest(unittest.TestCase):
    def test_codex_fast_sidekick_contract_is_distributed(self):
        source = (ROOT / "plugins/common/skills/delegate/SKILL.md").read_text(encoding="utf-8")
        codex_skill = (ROOT / "codex/plugins/common/skills/delegate/SKILL.md").read_text(encoding="utf-8")
        codex_cli = (ROOT / "codex/plugins/common/skills/delegate/references/codex-cli.md").read_text(encoding="utf-8")
        claude_cli = (ROOT / "plugins/common/skills/delegate/references/claude-cli.md").read_text(encoding="utf-8")
        metadata = (ROOT / "codex/plugins/common/skills/delegate/agents/openai.yaml").read_text(encoding="utf-8")
        metadata_source = (ROOT / "codex-metadata/common/delegate/openai.yaml").read_text(encoding="utf-8")

        for skill in (source, codex_skill):
            self.assertIn("`--fast`", skill)
            self.assertIn("Codex-only", skill)
            self.assertIn("fall back", skill)

        self.assertIn('service_tier="fast"', codex_cli)
        self.assertIn("--enable fast_mode", codex_cli)
        self.assertIn("FAST_FALLBACK", codex_cli)
        self.assertIn("must not launch Claude CLI", claude_cli)
        self.assertIn('$delegate --fast', metadata)
        self.assertEqual(metadata_source, metadata)
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", codex_skill)
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", codex_cli)

    def test_model_catalog_reports_fast_eligibility(self):
        fixture = {
            "models": [
                {
                    "visibility": "list",
                    "slug": "fast-model",
                    "display_name": "Fast Model",
                    "description": "fixture",
                    "supported_reasoning_levels": [{"effort": "low"}],
                    "additional_speed_tiers": ["fast"],
                },
                {
                    "visibility": "list",
                    "slug": "standard-model",
                    "display_name": "Standard Model",
                    "description": "fixture",
                    "supported_reasoning_levels": [{"effort": "low"}],
                },
            ]
        }
        result = subprocess.run(
            ["node", str(ROOT / "plugins/common/skills/delegate/scripts/parse-cli-json.js"), "models"],
            input=json.dumps(fixture),
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("fast-model | Fast Model | efforts: low | fast: yes", result.stdout)
        self.assertIn("standard-model | Standard Model | efforts: low | fast: no", result.stdout)


if __name__ == "__main__":
    unittest.main()

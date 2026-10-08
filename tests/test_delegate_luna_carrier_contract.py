import pathlib
import tomllib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class DelegateLunaCarrierContractTest(unittest.TestCase):
    def test_luna_max_prefers_native_codex_with_exact_profile(self):
        source = (ROOT / "plugins/common/skills/delegate/SKILL.md").read_text(encoding="utf-8")
        codex_skill = (ROOT / "codex/plugins/common/skills/delegate/SKILL.md").read_text(encoding="utf-8")

        for skill in (source, codex_skill):
            self.assertIn("prefer a native Codex sub-agent", skill)
            self.assertIn("live native spawn tool schema", skill)
            self.assertIn("do not use the CLI catalog as proof of native support", skill)
            self.assertIn('model="<resolved Luna ID>"', skill)
            self.assertIn("current-generation Luna model from the live Codex catalog", skill)
            self.assertNotIn("gpt-5.6-luna", skill)
            self.assertIn('reasoning_effort="max"', skill)
            self.assertIn('fork_turns="none"', skill)
            self.assertNotIn("fixed **Codex CLI sidekick** route", skill)
            self.assertNotIn("Never try native as a fallback", skill)

        self.assertIn("not an auto-registered native agent", source)
        self.assertIn("not an auto-registered native agent", codex_skill)
        self.assertTrue((ROOT / "plugins/common/agents/luna-max-sidekick.md").is_file())
        self.assertTrue((ROOT / "codex/plugins/common/.codex-agents/luna-max-sidekick.toml").is_file())

        self.assertIn("load its `developer_instructions` completely", codex_skill)
        self.assertIn("strip a leading `common:` namespace", codex_skill)
        self.assertNotIn("Before every named-agent dispatch", codex_skill)
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", codex_skill)

    def test_luna_max_fast_uses_cli_when_native_cannot_pin_service_tier(self):
        source = (ROOT / "plugins/common/skills/delegate/SKILL.md").read_text(encoding="utf-8")
        codex_skill = (ROOT / "codex/plugins/common/skills/delegate/SKILL.md").read_text(encoding="utf-8")

        for skill in (source, codex_skill):
            self.assertIn("native carrier cannot pin Fast", skill)
            self.assertIn("Codex CLI", skill)
            self.assertIn("changes only the service tier", skill)

    def test_bundled_toml_preserves_the_complete_role_contract(self):
        source_role = (ROOT / "plugins/common/agents/luna-max-sidekick.md").read_text(encoding="utf-8")
        role_body = source_role.split("---", 2)[2].strip()
        with (ROOT / "codex/plugins/common/.codex-agents/luna-max-sidekick.toml").open("rb") as handle:
            bundled_role = tomllib.load(handle)
        bundled_role_text = (ROOT / "codex/plugins/common/.codex-agents/luna-max-sidekick.toml").read_text(
            encoding="utf-8"
        )

        self.assertEqual(role_body, bundled_role["developer_instructions"].strip())
        self.assertIn("this file is not an auto-registered native agent", bundled_role["description"])
        self.assertIn("native Codex sub-agent", bundled_role["description"])
        self.assertNotIn("generic Codex subagent", bundled_role_text)


if __name__ == "__main__":
    unittest.main()

# AGENTS.md

This repo publishes `common-dev`, a generic developer-toolkit marketplace for both Claude Code and Codex.

Claude Code is the source of truth:

- Root Claude marketplace: `.claude-plugin/marketplace.json`
- Claude plugin source: `plugins/<name>/.claude-plugin/plugin.json`
- Claude skills: `plugins/<name>/skills/<skill>/SKILL.md`
- Claude bundled agents: `plugins/<name>/agents/<agent>.md`

The Codex copy is a hand-maintained port of the Claude source:

- Root Codex marketplace (Layout A): `.agents/plugins/marketplace.json`
- Self-contained Codex marketplace (Layout B): `codex/.agents/plugins/marketplace.json`
- Codex plugin package: `codex/plugins/<name>/.codex-plugin/plugin.json`
- Codex skills: `codex/plugins/<name>/skills/<skill>/SKILL.md`
- Codex package-local agent definitions: `codex/plugins/<name>/.codex-agents/<agent>.toml`

Port every distributed change by hand in the same change set; do not regenerate `codex/` with the `codex-skill-transfer` script. Keep the substance identical and limit differences to what Codex needs (platform reference: `docs/experiments/claude-codex-plugin-parity-20261008.md`):

- Frontmatter: Codex reads only `name`, `description`, and `metadata`; Claude-only keys go, and the Codex copy may carry `compatibility` / `metadata.version`. Explicit-only invocation becomes `agents/openai.yaml` `policy.allow_implicit_invocation: false`.
- Mentions: `/plugin:skill` becomes `$skill` (or `$plugin:skill`); Codex has no `$ARGUMENTS` or `!` command injection.
- Paths: Codex expands no plugin path variables inside skill text. Replace `${CLAUDE_PLUGIN_ROOT}/...` with a runtime-resolved directory declared once in the Codex `SKILL.md` (as `DELEGATE_DIR`, `LAB_SKILL_DIR`, or `SKILLS_ROOT` do), failing closed when it cannot be resolved.
- Keep every skill subfolder (`scripts/`, `references/`, `assets/`, `templates/`, `evals/`).
- Claude-only components — mods, monitors, `userConfig`, plugin `dependencies`, LSP — have no Codex counterpart; leave them out of the Codex copy and say so in the Codex description when it matters. A mod's `hooks/hooks.json` must never be copied, because Codex reads that file as ordinary hooks.
- Compare the two copies with `diff --strip-trailing-cr` before shipping; only the differences above may remain.

Codex-only skill UI metadata that has no Claude frontmatter equivalent lives under `codex-metadata/<plugin>/<skill>/openai.yaml` and is kept in sync with `codex/plugins/<plugin>/skills/<skill>/agents/openai.yaml`. Do not place it under the Claude skill's own `agents/` directory.

Plugin-level `agents/*.md` are ported to package-local `.codex-agents/*.toml`. Codex does not auto-register that private directory; the consuming skill keeps a resolver that loads the TOML's `developer_instructions` and fails closed with `AGENT_DEFINITION_MISSING`. Model and reasoning settings remain runtime policy unless the consuming skill explicitly pins a user-requested profile.

The two marketplace catalogs are **hand-maintained**. Both use the `common-dev` marketplace id and list every plugin: Layout A (`.agents/plugins/marketplace.json`) paths are `./codex/plugins/<name>`; Layout B (`codex/.agents/plugins/marketplace.json`) paths are `./plugins/<name>`. Keep both aligned with the `codex/plugins/<name>` trees. Layout A is the git URL install entrypoint for Codex.

## Invariants

- Keep skills generic: no project-specific branding, routes, ports, accounts, or private workflow assumptions.
- Keep `common` Skill instructions in English. Default user-facing prose and generated human-readable artifacts to Traditional Chinese; switch only when the user explicitly requests another language.
- For Claude source, reference skill-local files through `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/...`; reference plugin-level bundled agents through `${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md`.
- For the Codex copy, replace Claude-only APIs or dynamic injection with Codex-facing instructions; never leave `${CLAUDE_PLUGIN_ROOT}` in Codex skill text.
- Bump the plugin version on every distributed change so Codex and Claude plugin caches refresh predictably.
- Update `README.md` and `CHANGELOG.md` when install paths, marketplace layout, or distributed package contents change.

## Working Style

- Make surgical changes. Every changed line should trace to the current request.
- Prefer existing plugin and skill structure over new abstractions.
- Re-read files before editing them in the same turn.
- Verify with machine checks before declaring a package or marketplace change done.
- Do not clean unrelated tracked changes or generated files you did not create.

## Validation

For Codex marketplace work, at minimum run:

```bash
python3 -c "import json, pathlib; [json.load(open(f, encoding='utf-8')) for f in pathlib.Path('.').rglob('*.json')]"
python3 -c "import json, pathlib; root=pathlib.Path('.'); assert (root/'.agents/plugins/marketplace.json').is_file(); assert (root/'codex/.agents/plugins/marketplace.json').is_file(); assert (root/'codex/plugins/test-utils/.codex-plugin/plugin.json').is_file(); assert (root/'codex/plugins/analysis-estimation/.codex-plugin/plugin.json').is_file(); assert (root/'codex/plugins/linkstart/.codex-plugin/plugin.json').is_file()"
python3 scripts/validate_linkstart_release.py
```

Then install through a temporary Codex home:

```bash
mkdir -p /tmp/common-dev-plugin-codex-test
env HOME=/tmp/common-dev-plugin-codex-test CODEX_HOME=/tmp/common-dev-plugin-codex-test codex plugin marketplace add /path/to/common-dev-plugin --json
env HOME=/tmp/common-dev-plugin-codex-test CODEX_HOME=/tmp/common-dev-plugin-codex-test codex plugin list --available --json
env HOME=/tmp/common-dev-plugin-codex-test CODEX_HOME=/tmp/common-dev-plugin-codex-test codex plugin add test-utils@common-dev --json
```

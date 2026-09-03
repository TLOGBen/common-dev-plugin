# AGENTS.md

This repo publishes `common-dev`, a generic developer-toolkit marketplace for both Claude Code and Codex.

Claude Code is the source of truth:

- Root Claude marketplace: `.claude-plugin/marketplace.json`
- Claude plugin source: `plugins/<name>/.claude-plugin/plugin.json`
- Claude skills: `plugins/<name>/skills/<skill>/SKILL.md`
- Claude bundled agents: `plugins/<name>/agents/<agent>.md`

Codex output is generated from the Claude source:

- Root Codex marketplace (Layout A): `.agents/plugins/marketplace.json`
- Self-contained Codex marketplace (Layout B): `codex/.agents/plugins/marketplace.json`
- Codex plugin package: `codex/plugins/<name>/.codex-plugin/plugin.json`
- Codex skills: `codex/plugins/<name>/skills/<skill>/SKILL.md`
- Codex package-local agent definitions: `codex/plugins/<name>/.codex-agents/<agent>.toml`

Do not hand-edit generated files under `codex/` unless the user explicitly asks for an inline port. Regenerate a plugin's Codex skills/manifest with the `codex-skill-transfer` script (point it at a throwaway dir, then place the generated `plugins/<name>/` subtree under `codex/`):

```bash
python3 "$CODEX_HOME/plugins/cache/baransu/baransu/<ver>/skills/codex-skill-transfer/scripts/transfer.py" plugins/<name> <out-dir>
cp -r <out-dir>/plugins/<name> codex/plugins/<name>
```

Caveat: the transfer copies `scripts/`, `references/`, `assets/`, and `evals/` under each skill. Plugin-level `agents/` are converted separately, while non-standard skill subdirs such as `templates/` are **dropped**. `analysis-estimation`'s `rfp-*` skills carry `templates/`; after porting restore them by hand (`cp -r plugins/<name>/skills/<skill>/<subdir> codex/plugins/<name>/skills/<skill>/<subdir>`).

Codex-only skill UI metadata that has no Claude frontmatter equivalent lives under `codex-metadata/<plugin>/<skill>/openai.yaml`. After porting, restore it to `codex/plugins/<plugin>/skills/<skill>/agents/openai.yaml`. Do not place this source under the Claude skill's own `agents/` directory: plugin transfer treats that directory as an unrepresented executable component and fails content closure.

For `common/delegate`, the transfer report flags remaining `${CLAUDE_PLUGIN_ROOT}` tokens for manual review. Preserve the generated bundled-agent resolver, then restore the existing `DELEGATE_DIR` fail-closed adapter and rewrite those tokens in the Codex `SKILL.md` and CLI references before replacing the live subtree.

Plugin-level `agents/*.md` are converted into package-local `.codex-agents/*.toml`. Codex does not auto-register that private directory; keep the generated consuming-skill resolver and its `AGENT_DEFINITION_MISSING` fail-closed behavior. Model and reasoning settings remain runtime policy unless the consuming skill explicitly pins a user-requested profile.

The two marketplace catalogs are **hand-maintained** — the transfer script does not merge them. Both use the `common-dev` marketplace id and list every plugin: Layout A (`.agents/plugins/marketplace.json`) paths are `./codex/plugins/<name>`; Layout B (`codex/.agents/plugins/marketplace.json`) paths are `./plugins/<name>`. Keep both aligned with the `codex/plugins/<name>` trees. Layout A is the git URL install entrypoint for Codex.

## Invariants

- Keep skills generic: no project-specific branding, routes, ports, accounts, or private workflow assumptions.
- Keep `common` Skill instructions in English. Default user-facing prose and generated human-readable artifacts to Traditional Chinese; switch only when the user explicitly requests another language.
- For Claude source, reference skill-local files through `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/...`; reference plugin-level bundled agents through `${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md`.
- For Codex output, generated rewrites may replace Claude-only APIs or dynamic injection with Codex-facing instructions. Preserve the transfer report's dropped/manual-review items when judging portability.
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

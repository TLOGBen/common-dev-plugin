# CLAUDE.md

## What this repo is

`common-dev` is a **Claude Code marketplace** — a generic, project-agnostic developer toolkit. The catalog is `.claude-plugin/marketplace.json`; each plugin lives under `plugins/<name>/` with its own `.claude-plugin/plugin.json`. Skills are auto-discovered from each plugin's `skills/` directory and agents from its `agents/` directory (no skills or agents arrays in `plugin.json`). All distributed plugins are enabled by default (`defaultEnabled: true`); users can disable any package they do not need.

Four plugins: `common` (everyday dev toolkit), `analysis-estimation` (rfp-requirement-analysis, rfp-architecture-design, rfp-sa-bdd, cold-estimation, itemized-estimate, quality-orchestrator), `common-lab` (experimental TypeSafe Jev skills) and `common-mod` (Claude-only mods, no Codex copy). A hand-maintained Codex port of each other plugin lives under `codex/plugins/<name>/`; port every distributed change by hand in the same change set (do not regenerate it with the `codex-skill-transfer` script) — see `AGENTS.md` for what may differ.

## Layout

```text
.claude-plugin/marketplace.json            # Claude catalog (source of truth)
.agents/plugins/  codex/.agents/plugins/   # Codex catalogs: Layout A (git URL install entrypoint) / Layout B (self-contained)
plugins/<name>/                            # Claude source: .claude-plugin/plugin.json, skills/, agents/ (common-mod: hooks/, types/)
codex/plugins/<name>/  codex-metadata/     # hand-maintained Codex port (common, analysis-estimation, common-lab) + Codex-only openai.yaml
docs/  scripts/validate_marketplace.py  AGENTS.md   # docs and images; structural validation; Codex-facing port rules and validation
```

## Invariants

- Keep skills generic: no project-specific branding, routes, ports, accounts, or private workflow assumptions.
- Keep `common` Skill instructions in English. Default user-facing prose and generated human-readable artifacts to Traditional Chinese; switch only when the user explicitly requests another language.
- For Claude source, reference a skill's own bundled files through `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/...` and plugin-level bundled agents through `${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md`; only paths the skill creates in the *user's* project (for example `.claude/wait-what/`, `.strategic-advance/`) stay project-relative.
- For the Codex copy, replace Claude-only APIs or dynamic injection with Codex-facing instructions; never leave `${CLAUDE_PLUGIN_ROOT}` in Codex skill text.
- Bump the plugin `version` on every distributed change so Claude and Codex plugin caches refresh predictably.
- 此 plugin 不寫單元測試，但測試照做。Whether a skill works has nothing to do with unit tests — when skills change it is the tests that break, not the skills — so the repo keeps no unit tests. What still runs: structural validation (`scripts/validate_marketplace.py`, JSON validity), each skill's `evals/` through `claude plugin eval` where one exists, and a real dogfood run of the changed skill with its output looked at.
- 實驗紀錄、受測專案與探針不進 repo. Experiment records, probed sample projects and probe scripts are never committed (`.gitignore` blocks `docs/experiments/` and `experiments/`); retrieve old ones from Git history when needed.
- Update `README.md` and `CHANGELOG.md` when install paths, marketplace layout, or distributed package contents change.

## Working Principles

### 1. Think Before Coding — don't assume, don't hide confusion, surface tradeoffs

- State assumptions explicitly — if uncertain, ask rather than guess
- Present multiple interpretations — don't pick silently when ambiguity exists
- Push back when warranted — if a simpler approach exists, say so
- Stop when confused — name what's unclear and ask for clarification

### 2. Simplicity First — minimum code that solves the problem, nothing speculative

- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- If 200 lines could be 50, rewrite it

The test: would a senior engineer say this is overcomplicated? If yes, simplify.

### 3. Surgical Changes — touch only what you must, clean up only your own mess

- Don't "improve" adjacent code, comments, or formatting; don't refactor what isn't broken
- Match existing style, even if you'd do it differently
- If you notice unrelated dead code, mention it — don't delete it
- Remove imports/variables/functions that YOUR changes made unused; leave pre-existing dead code unless asked
- Re-read any file before Edit/Write in the same turn; never rely on memory of a previous turn's read

The test: every changed line should trace directly to the request.

### 4. Goal-Driven Execution — define success criteria, loop until verified

| Instead of… | Transform to… |
|-------------|--------------|
| "Fix the bug" | Write a test that reproduces it, then make it pass |
| "Add validation" | Write tests for invalid inputs, then make them pass |
| "Refactor X" | Ensure tests pass before and after |

For multi-step tasks, state a brief plan: `1. [Step] → verify: [check]`, `2. [Step] → verify: [check]`. Strong success criteria let the loop run independently; weak criteria ("make it work") require constant clarification.

## Commit Style

Conventional commits (`feat`, `fix`, `refactor`, `docs`, `chore`). Attribution lines disabled globally.

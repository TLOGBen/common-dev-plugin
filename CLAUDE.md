# CLAUDE.md

This repo is a **Claude Code marketplace** (`common-dev`) — a generic, project-agnostic developer toolkit. The catalog is `.claude-plugin/marketplace.json`; each plugin lives under `plugins/<name>/` with its own `.claude-plugin/plugin.json`. Skills are auto-discovered from each plugin's `skills/` directory, and agents from its `agents/` directory (no skills or agents arrays in `plugin.json`). All distributed plugins are enabled by default (`defaultEnabled: true`); users can disable any package they do not need. `analysis-estimation` includes estimate, rfp-requirement-analysis, rfp-architecture-design, rfp-sa-bdd, cold-estimation, and quality-orchestrator. A hand-maintained Codex port of each plugin lives under `codex/plugins/<name>/`; port every distributed change by hand in the same change set (do not regenerate it with the `codex-skill-transfer` script) — see `AGENTS.md` for what may differ.

**Invariants:** keep skills generic — no project-specific branding, routes, ports, or accounts; keep `common` Skill instructions in English while defaulting user-facing prose and generated human-readable artifacts to Traditional Chinese unless the user explicitly requests another language; reference a skill's own bundled files via `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/...`, plugin-level bundled agents via `${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md`, and only paths the skill creates in the *user's* project (`tests/<name>/`, `.claude/test-template/`) stay project-relative. Bump the plugin's `version` on every distributed change (caching).

## Working Principles

### 1. Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

- State assumptions explicitly — if uncertain, ask rather than guess
- Present multiple interpretations — don't pick silently when ambiguity exists
- Push back when warranted — if a simpler approach exists, say so
- Stop when confused — name what's unclear and ask for clarification

### 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- If 200 lines could be 50, rewrite it

The test: would a senior engineer say this is overcomplicated? If yes, simplify.

### 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken
- Match existing style, even if you'd do it differently
- If you notice unrelated dead code, mention it — don't delete it

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused
- Don't remove pre-existing dead code unless asked

The test: every changed line should trace directly to the request.

### 4. Goal-Driven Execution

Define success criteria. Loop until verified.

| Instead of… | Transform to… |
|-------------|--------------|
| "Fix the bug" | Write a test that reproduces it, then make it pass |
| "Add validation" | Write tests for invalid inputs, then make them pass |
| "Refactor X" | Ensure tests pass before and after |

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

Strong success criteria let the loop run independently. Weak criteria ("make it work") require constant clarification.

### Read-before-write

Re-read any file before Edit/Write in the same turn. Never rely on memory of a previous turn's read.

## Commit Style

Conventional commits (`feat`, `fix`, `refactor`, `docs`, `chore`). Attribution lines disabled globally.

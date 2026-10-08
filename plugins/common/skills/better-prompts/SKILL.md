---
name: better-prompts
description: Optimizes prompts — use when the user says "improve this prompt", "optimize my system prompt", "幫我改 prompt", "優化 prompt", "審 prompt", or "migrate this prompt to a newer model", wants a prompt improved, reviewed, shortened, or written from scratch, or asks why a model ignores instructions or burns tokens. Audits, rewrites, drafts, and migrates system prompts, agent instructions, tool descriptions, CLAUDE.md / AGENTS.md / skill files, and full prompt stacks against official Claude and GPT prompting guidance. Not for polishing prose that isn't a prompt, scored SKILL.md evolution (/baransu:evolve), or skill evals and trigger tuning (skill-creator).
---

# better-prompts

## Output language

Keep these skill instructions in English. Default user-facing explanations and newly authored human-readable text to Traditional Chinese. If the user explicitly requests another language, use it instead. Preserve code, identifiers, commands, quoted source text, and the supplied prompt's language unless translation is part of the request.

Make prompts lean, outcome-first, and contradiction-free. Core principle (shared by both vendors' official guidance): **define the outcome, the hard constraints, the available evidence, and the completion bar — then leave the path to the model.** OpenAI's internal testing (directional only): leaner system prompts improved eval scores ~10–15% while cutting tokens 41–66%. Anthropic's migration guides: over-prescriptive prompts written for older models actively reduce output quality on current ones.

## Workflow

Copy this checklist and track progress:

```
Prompt Optimization:
- [ ] 1. Identify the target model/runtime and pick the reference guide
- [ ] 2. Classify the request mode (audit / rewrite / draft / migrate)
- [ ] 3. Read the full input prompt (file or inline)
- [ ] 4. Run the diagnostic checklist
- [ ] 5. Produce output in the required format
- [ ] 6. Self-check: no invented constraints, invariants preserved, deletions listed for review
```

## Step 1 — Target model and reference guide

Read the matching reference **before editing anything**. If the target is unclear from the prompt content or the user's words, ask once.

| Target | Read |
|---|---|
| GPT / OpenAI API / Codex (incl. AGENTS.md, skills) | `${CLAUDE_PLUGIN_ROOT}/skills/better-prompts/references/gpt-prompting-guide.md` |
| Claude / Claude API / Claude Code (incl. CLAUDE.md, agent configs) | `${CLAUDE_PLUGIN_ROOT}/skills/better-prompts/references/claude-prompting-guide.md` |
| Other or unknown model | Either guide's structural sections; apply only vendor-neutral principles |

The structural principles (outcome-first, stopping conditions, autonomy boundaries, lean-prompt diet) are shared. Vendor-specific advice — API parameters, model-version behavior shifts, CLAUDE.md/skill mechanics — only applies to its own target; when the target differs, say so in the output rather than silently applying it. If the user asks for the *latest* official wording, fetch the live URLs listed at the top of each reference.

## Step 2 — Mode

| Mode | Signals | Deliverable |
|---|---|---|
| **Audit** | "review this prompt", "why does the model ignore X" | Diagnosis only — no rewritten prompt |
| **Rewrite** | "improve/optimize" + an existing prompt | Full rewritten prompt + change log |
| **Draft** | "write me a prompt for ___", no existing text | New prompt |
| **Migrate** | "moving to model X", "behavior changed after upgrade" | Migration steps + targeted edits |

Input may be inline text or a file path — read the complete file before working. Output the result in the conversation; do not overwrite the source file unless asked.

## Step 3 — Diagnostic checklist

Check each item; each maps to a section in the reference guides:

1. **Contradictions** — rules that cannot both be satisfied, including conflicts between the prompt and the skills, AGENTS.md, or CLAUDE.md files loaded beside it. The top source of instability in frontier models — some current models stop early on conflicting skill instructions (officially noted for GPT-6 Astra); fix first.
2. **Redundancy** — the same rule restated, style/process instructions that don't change behavior, examples that prove unnecessary.
3. **Over-prescribed process** — step-by-step scripts where a goal + success criteria + fallback would do. Current models find efficient paths when told what "done" looks like.
4. **Missing stopping conditions** — tool-using prompts need "when to stop, when to fall back, when to give up". Unbounded conditions ("until fully confident") create runaway loops.
5. **Absolute-language misuse** — ALWAYS/NEVER reserved for true invariants (safety, required fields); judgment calls become decision rules. Aggressive language ("CRITICAL: you MUST") overtriggers on current models.
6. **Vague tone words** — "friendly", "professional" replaced with concrete writing behaviors.
7. **Missing autonomy boundaries** — what analytical vs. action vs. sensitive requests each permit; safe local actions named explicitly; when to keep working instead of checking in (current models from both vendors can stop to ask or report before the task is done).
8. **Incomplete tool descriptions** — each tool: what it does, *when to call it* (trigger conditions give measurable lift), key return fields, error behavior. Irrelevant tools removed.
9. **Missing evidence policy** — for grounded prompts: which claims need support, the sufficiency bar, and behavior when evidence is missing.
10. **No verification loop** — ask the model to run the most relevant validation before finishing, and to say what it would check when it can't.

## Rewrite rules

- Organize with the eight-section skeleton (Role / Personality / Goal / Success criteria / Constraints / Tools / Output / Stop rules) — **omit sections that don't apply**; never pad for symmetry.
- Cut before adding. New instructions exist only to fix an observed behavior problem.
- Preserve invariants: safety rules, business constraints, required output fields, and permission limits from the original stay, unless the user says otherwise.
- Never invent constraints. Ask about uncertain business rules instead of guessing.
- Keep the prompt's original language (a Chinese prompt stays Chinese after rewriting).

## Output formats

**Audit:**

```markdown
## Diagnosis: <prompt name>
### High-impact issues (change behavior)
- <issue> → <recommendation> (guide §N)
### Trimmable (no behavior change)
- ...
### Keep as-is
- ... (and why)
```

**Rewrite / Draft / Migrate:**

```markdown
## Result
<complete prompt in a code block>

## Changes
| Change | Reason | Guide § |
|---|---|---|

## Risks — for your review
- <deleted items that might have been load-bearing; the user gets veto power over every removal>
```

**Migrate** additionally follows the reference guide's migration section: establish a baseline with evals on real tasks first, then make targeted edits — never rewrite a working prompt stack wholesale; every change must be attributable.

## Boundaries

- One prompt (or one clearly related prompt stack) per pass; split unrelated prompts into separate passes.
- Rewrites are proposals, not silent applications — every deletion appears under "Risks" so the user can veto it.
- This skill does not execute or benchmark the target prompt. For A/B validation, recommend running real task samples on the target model before/after.

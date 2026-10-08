# GPT Prompting Guidance — Offline Reference

As of 2026-10-08. Current OpenAI lineup: GPT-6 Astra (`gpt-6-astra`, highest intelligence), GPT-6.1 Sol (`gpt-6.1-sol`, near-Astra at lower cost), GPT-6 Luna (`gpt-6-luna`, fastest and cheapest). GPT-5.6 (Sol / Terra / Luna) is the previous generation.

Distilled from OpenAI's official docs:

- Using GPT-6 (model family, prompting best practices, migration): <https://developers.openai.com/api/docs/guides/latest-model>
- Reasoning models (effort, reasoning mode, persisted reasoning, `configuration_update`): <https://developers.openai.com/api/docs/guides/reasoning>
- Model pages: <https://developers.openai.com/api/docs/models/gpt-6-astra>, <https://developers.openai.com/api/docs/models/gpt-6.1-sol>, <https://developers.openai.com/api/docs/models/gpt-6-luna>
- Codex subagents (Codex model and effort choice): <https://developers.openai.com/codex/subagents>
- Prompting guidance for GPT-5.6 Sol (general structure carried forward; OpenAI publishes no separate GPT-6 prompt-guidance page as of this date): <https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6>

OpenAI frames its GPT-6 prompts as starting points that address behavior observed on GPT-6 Astra; evaluate them on the chosen model and workload. When the user asks for the *current* official wording, fetch the live URLs instead of relying on this file.

Core principle: **define the outcome, important constraints, available evidence, and completion bar — then leave room for the model to choose an efficient path.** OpenAI's guidance also recommends treating `reasoning.effort` as a tuning knob, not the primary way to recover quality.

## Table of Contents

1. [Simplify prompts first](#1-simplify-prompts-first)
2. [Outcome-first prompts and stopping conditions](#2-outcome-first-prompts-and-stopping-conditions)
3. [Instruction following, skills, and AGENTS.md](#3-instruction-following-skills-and-agentsmd)
4. [Initiative, follow-through, and approval boundaries](#4-initiative-follow-through-and-approval-boundaries)
5. [Personality, writing style, and response length](#5-personality-writing-style-and-response-length)
6. [Tool routing](#6-tool-routing)
7. [Programmatic Tool Calling (PTC)](#7-programmatic-tool-calling-ptc)
8. [Subagent delegation](#8-subagent-delegation)
9. [Grounding, citations, and retrieval budgets](#9-grounding-citations-and-retrieval-budgets)
10. [Long-running workflows and state](#10-long-running-workflows-and-state)
11. [Reasoning effort and mode](#11-reasoning-effort-and-mode)
12. [Frontend and visual tasks](#12-frontend-and-visual-tasks)
13. [Check work before finishing](#13-check-work-before-finishing)
14. [Suggested prompt structure](#14-suggested-prompt-structure)
15. [Prompt migration workflow](#15-prompt-migration-workflow)

## 1. Simplify prompts first

Start from a working prompt and tool set; remove one group at a time, re-evaluating after each removal. In a sample of OpenAI's internal coding-agent evals (published with GPT-5.6), leaner system prompts improved scores ~10–15% while cutting total tokens 41–66% and cost 33–67% — directional only; validate on your own tasks.

**Trim:**
- Redundant restatements of the same rule — state each instruction once
- Style/process instructions that don't change behavior
- Examples that prove unnecessary (keep ones that encode a product requirement or fix a measured gap)
- Step-by-step process instructions for behaviors the model already performs reliably
- Unrelated tools and their descriptions; keep remaining descriptions concise and precise

**Preserve:**
- User-visible outcomes
- Success criteria and stopping conditions
- Safety, business, evidence, and permission constraints
- Context-dependent tool-routing rules
- Required output shape and validation needs

Track context both at the start of a run and as the conversation grows — long sessions amplify repeated prompt and tool content.

**Conflict review:** after trimming, check the remaining instructions — and every skill or instruction file the model can read — for rules that cannot both be satisfied, or a general rule contradicted by a specific one without stated precedence. On GPT-6 Astra this matters more (see §3).

## 2. Outcome-first prompts and stopping conditions

Replace step-by-step prescriptions with destination-focused language: state the objective, list success conditions, specify required outputs, and describe fallback behavior for missing evidence. OpenAI's reasoning guide: reasoning models work best with a clear goal, strong constraints, and an explicit output contract, without prescribing every intermediate step; for agentic or research work, define what counts as done and how to verify it.

**Absolute rules vs. decision rules:** reserve ALWAYS / NEVER / must / only for true invariants — safety rules, required fields, actions that should never occur. For judgment calls (when to search, ask, use tools, iterate), write decision rules instead.

**Explicit stopping-condition pattern:** resolve the request with the fewest necessary tool interactions while prioritizing correctness, required evidence, calculations, and citations; after each result, check whether the core request is answerable; if required evidence is still absent, name the missing fact and take the smallest useful fallback.

## 3. Instruction following, skills, and AGENTS.md

GPT-6 Astra follows longer instructions better than earlier models, giving more control — but it is also **more sensitive to instructions in skills and other files such as `AGENTS.md`**. Unclear or conflicting guidance in a skill file can make it pause and block work early. OpenAI strongly recommends auditing skills and other files the model can access for instructions that could influence its behavior.

- **State precedence explicitly**, e.g. user instructions take precedence over skill guidelines; when they conflict, follow the user.
- **Ask for transparency when a skill changes course:** if a skill causes the model to ask for permission, pause, leave work unfinished, or diverge from the user's intent, have it name and link the exact `SKILL.md`, quote the instruction, explain how it applies, and separate explicit requirements from its own interpretation. OpenAI suggests this for finding silent and conflicting guidance when many skills and `AGENTS.md` files are loaded.

When auditing a GPT-6 prompt stack, treat every loaded skill and instruction file as part of the prompt: conflicts across layers are a primary cause of early stops.

## 4. Initiative, follow-through, and approval boundaries

GPT-6 Astra stays coherent over long tasks better than GPT-5.6 Sol, but it is designed as a collaborator: **it is more likely to ask the user a question when input could materially change the result**, and by default it also asks non-blocking questions while working. This can stop work where the user expected reasonable assumptions and persistence. Tune to the autonomy your application needs:

- **Bias to action** — infer intent and scope from instructions and prior context; persist until the intended goal is complete; proceed autonomously with non-destructive steps (isolated worktrees, resolving merge conflicts, read-only actions, draft PRs) unless clearly destructive or irreversible.
- **Treat requests as authorization** — phrasings like "can you…", "I want to…", "help me…" are instructions to do the work, not to acknowledge capability, propose a plan, or offer to continue; don't settle for a partial result to save time or tokens.
- **Ask for approval only on a concrete, reviewable result** — finish the authorized work first so approval is the final step (before deploying, writing to an external app, merging, publishing). No permission needed for reversible tasks, read-only actions, reviews or fixes, or anything already authorized or strongly implied.
- OpenAI's sample also tells the model not to add unsolicited warnings, disclaimers, approval flows, or compliance checklists for hypothetical risk.

**Compact authority policy** (from the GPT-5.6 guidance, still the recommended shape): analytical requests (answer, explain, review, diagnose, plan) → inspect and report, no implementation unless asked; action requests (change, build, fix) → make in-scope local changes and run non-destructive validation without asking; sensitive actions → confirm external writes, destructive actions, purchases, or material scope expansion. Name safe local actions explicitly. Keep the policy in one place and state each rule once — repeated "ask first" / "wait for approval" language causes unnecessary pauses.

## 5. Personality, writing style, and response length

GPT-6 Astra **tends toward detailed, formatted responses** (lists, tables, Markdown) and may reuse recurring phrases across sessions. Specify the writing style and structure the application needs.

- **Prose over formatting** when needed: default to clear paragraphs, one idea each; lists only for genuinely parallel, sequential, or comparable items; avoid nested lists; plain words, active voice; main point stated early.
- **Technical communication:** plain language over jargon; technical detail only where it illustrates the idea; calibrate to the reader's assumed background.
- **Stock phrases:** OpenAI's sample names specific phrases and patterns to avoid (e.g. "Bottom line:", "delve", "leverage", "it's worth noting", contrastive "X, not Y" framing, invented compound labels, concluding summary lines). Naming the concrete patterns works better than a vague "avoid slop".
- **Tone specificity:** replace labels ("friendly", "empathetic") with concrete writing choices — state the answer directly, acknowledge a reported problem before the next step, reassure only when relevant, omit generic praise and sign-offs.
- **Length control:** state a preservation priority, not a cap — lead with the conclusion; keep required facts, decisions, caveats, and next steps; trim introductions, repetition, and optional background first. Where supported, `text.verbosity` (low/medium/high) sets the default detail level; use the prompt for task-specific length.
- **Language:** specify the output language and when to switch.
- **Editing/rewrites/summaries:** preserve the artifact, length, structure, genre, and factual claims first; improve clarity without adding claims, sections, or promotional tone.

## 6. Tool routing

Expose only task-relevant tools. Each description covers: what the tool does, when to use it, important return fields and types, error behavior.

**Prerequisites:** resolve required discovery, retrieval, and validation before acting; don't skip prerequisites because the final state seems obvious.

Parallelize independent reads; keep work sequential when a result determines the next action; synthesize after parallel retrieval before acting. For empty/partial/suspicious results, try one or two meaningful fallbacks before concluding no result exists.

**GPT-6 API notes:** tool calling on GPT-6 Astra and GPT-6.1 Sol requires the Responses API (Chat Completions supports them only without tools); GPT-6 Luna supports function calling in Chat Completions only with `reasoning_effort: "none"`. GPT-6 adds **async tool calling** (`async: true` on a function/custom tool — the model keeps reasoning or answering independent parts while the tool runs; return the result later with the original `call_id`) and **mid-turn steering** (send corrections or new requirements while the model works, over WebSocket).

## 7. Programmatic Tool Calling (PTC)

Supported on GPT-6 as on GPT-5.6. Best for bounded workflows where code processes several tool results or large intermediate outputs into a much smaller structured result (filtering, joining, ranking, deduplication, aggregation, deterministic validation).

**Prefer direct tool calls when:** one call suffices; intermediate outputs are already small; each result may change the next decision; approval is required; the final answer must preserve citations or native artifacts. Multiple, parallel, or dependent calls alone do not justify PTC.

**Prompting pattern:** don't rely on tool availability or "use PTC efficiently". State the bounded stage, eligible tools, exact output schema and required evidence, concurrency/retry/stop limits, which work stays direct, and one clear handoff (no route switching, no repeated completed calls). If the model cannot know a tool's return shape before writing the program, prefer direct calls.

**Testing:** `program_output` and the final assistant message are separate outputs — test both. Compare direct vs. programmatic on the same tasks; count fewer tokens, calls, or turns as a win only when responses still pass existing evals.

## 8. Subagent delegation

GPT-6 Astra is trained to divide work across parallel subagents but **may delegate less often than a workflow wants**. It responds well to explicit guidance on when and how much to delegate — e.g. delegate whenever parallelizing could save time or improve quality, whether the model is root or subagent. Tune to the harness.

Inter-agent messages may contain grammar or spacing errors; if humans read them, ask for legible messages with proper spacing between words and numbers.

In Codex, choose subagent models per role: `gpt-6.1-sol` for demanding, ambiguous, multi-step agents; `gpt-6-luna` for fast, narrow, repeatable work.

## 9. Grounding, citations, and retrieval budgets

Make citation behavior explicit: what needs support, what counts as sufficient evidence, and what to do when evidence is missing.

**Q&A retrieval budget:** start with one broad search using short, discriminative keywords; answer if the top results support the core request. Search again only when required facts, owners, dates, IDs, or sources are missing, the user asked for exhaustive coverage or comparison, a specific artifact must be read, or an important claim would otherwise be unsupported. Don't search again to polish phrasing or add nonessential detail.

**Research/synthesis standards:** cite only retrieved sources; attach citations to supported claims; label inference separately; state conflicts between sources; narrow the answer or report missing evidence rather than guessing.

**Creative drafting:** distinguish source-backed facts from creative wording. Never invent names, metrics, dates, roadmap status, customer outcomes, or product capabilities.

## 10. Long-running workflows and state

For multi-step or tool-heavy tasks: a short visible preamble before the first tool call (it also speeds time to first visible token), then sparse outcome-based updates at major phase changes. Don't narrate routine tool calls.

- **Persisted reasoning:** `reasoning.context` selects `current_turn` or `all_turns`. GPT-5.6 models and GPT-6.1 Sol support `all_turns`; omit or set `auto` for the model's default and check the response's effective value. Use `all_turns` when goals and assumptions stay stable; `current_turn` when earlier reasoning is obsolete. Reasoning carries only within one model family. With `previous_response_id` prior state is automatic; when replaying manually, resend every output item (including encrypted reasoning) unchanged.
- **Changing effort mid-conversation (GPT-6):** add a `configuration_update` input item to raise or lower effort for later turns while keeping request-level `reasoning.effort` unchanged — this preserves the prompt prefix for caching. Supported in standard, single-agent mode; changes only effort.
- **Assistant `phase`:** the reasoning guide documents `phase` (`commentary` / `final_answer`) for GPT-5.5 and GPT-5.4 long-running flows; preserve original values when replaying.
- **Compaction:** compact after major milestones, not every turn; treat compacted items as opaque state.
- **Prompt caching:** keep reusable prefixes stable; avoid churn in large system prompts. When migrating from GPT-5.5 or earlier, replace `prompt_cache_retention` with `prompt_cache_options.ttl` (e.g. `"30m"`); review cache boundaries and cache-write billing.

## 11. Reasoning effort and mode

Establish baseline performance before changing reasoning effort, and preserve the current effective effort where the new model supports it.

| Model | `reasoning.effort` values | Default |
|---|---|---|
| GPT-6 Astra | `low`, `medium`, `high`, `xhigh`, `max` — **no `none`** (HTTP 400) | — |
| GPT-6.1 Sol | `low`, `medium`, `high`, `xhigh`, `max` — **no `none` or `minimal`** | `medium` |
| GPT-6 Luna | `none`, `low`, `medium`, `high`, `xhigh`, `max` | `medium` |

- Coming from `none` on Astra or 6.1 Sol: use `low`. Coming from `minimal`: start with `low` and compare.
- `low` for latency-sensitive work when quality holds; `medium` as the balanced start; `high` / `xhigh` only when evals show a meaningful gain; `max` for the hardest quality-first work — compare it with `xhigh`, never a global default.
- **Pro mode** (`reasoning.mode: "pro"`, Responses API, GPT-5.6 and GPT-6): more model work for a single final answer; independent of effort; higher latency and tokens. Keep the same outcome-focused prompt — don't ask the model to "think harder" or produce several candidates. Use selectively where evals justify it.
- **Codex:** Codex exposes an `ultra` level when the selected model and account support it, above `max` / `xhigh`: maximum reasoning plus proactive delegation to subagents. Codex's subagent docs suggest starting explicit settings at `high` for GPT-6 Luna or `low` for GPT-6 Astra.
- Before raising effort to fix failures, check that the prompt already has success criteria, dependency rules, tool-routing rules, and a verification loop — missing structure is the more common cause.
- When reasoning effort is not `none`, remove `temperature`, `top_p`, and `top_logprobs` (and `logprobs` in Chat Completions).

## 12. Frontend and visual tasks

Provide product context, preserve existing design systems, and name the relevant states and constraints.

**Incremental changes:** inspect and preserve existing design tokens/components/patterns; no extra features or decorative UI unless requested; preserve responsive behavior and expected states; render and inspect results before finalizing.

**Image detail:** for vision, computer-use, localization, or OCR tasks needing spatial precision, choose image detail intentionally — original detail for large/dense/coordinate-sensitive images when cost and latency justify it.

## 13. Check work before finishing

Grant access to validation tools and state which validation matters.

**Coding:** run the most relevant validation available — targeted tests for changed behavior, type or lint checks, build checks for affected packages, or a minimal smoke test when full validation is too expensive; if validation cannot run, explain why and name the next-best check.

**Calibrate testing on GPT-6 Astra:** it tends to test thoroughly before calling a coding task complete, which can mean broader tests than a small change needs. Tell it not to write tests for reversible, low-impact changes that only mirror the implementation; run checks appropriate to the change; broaden or repeat testing only when new changes, failures, or unresolved concerns justify it.

**Visual artifacts:** render before finalizing; inspect layout, clipping, spacing, missing content, and visual consistency; revise until the render matches the requirements.

**Implementation plans** should include: requirements, named resources/files, state transitions or data flow, validation checks, failure behavior, privacy/security considerations, and open questions that materially affect implementation.

## 14. Suggested prompt structure

Keep each section brief; add detail only where behavior changes. Omit sections that don't apply.

```text
Role: [the model's function and context]

Personality: [tone and collaboration style]

Goal: [user-visible outcome]

Success criteria: [what must be true before the final answer]

Constraints: [policy, safety, business, evidence, and side-effect limits]

Tools: [which tools to use, when, and what not to use]

Output: [sections, length, format, and tone]

Stop rules: [when to retry, fallback, abstain, ask, or stop]
```

## 15. Prompt migration workflow

Moving an existing application to the GPT-6 family (OpenAI's Codex OpenAI Docs skill can apply the recommended changes: `$openai-docs migrate this project to the GPT-6 model family`):

1. Set `model` to `gpt-6-astra`, `gpt-6.1-sol`, or `gpt-6-luna`, preserving the current effective reasoning effort where supported (see §11 for unsupported levels).
2. Move tool-calling workloads to the Responses API; remove sampling params that reasoning rejects; update prompt-caching options.
3. Run evals on representative tasks *before* prompt changes. Compare 6.1 Sol against Astra on your tasks to judge the quality/cost tradeoff.
4. Remove obsolete scaffolding, repeated instructions, irrelevant tools — and audit loaded skills and `AGENTS.md` for conflicting instructions (§3).
5. If the model keeps asking for approval, add initiative/follow-through guidance (§4); tune writing style (§5), delegation (§8), and testing scope (§13) only for measured issues.
6. Re-run evals after each prompt or reasoning change.

**Debugging regressions:** use small sets of real traces → identify the failure mode → find the likely instruction or contradiction → make surgical edits → re-run the same cases.

Key principle: do **not** rewrite a working prompt stack wholesale. Incremental changes let you attribute behavior changes to model, reasoning effort, prompt, tools, or runtime.

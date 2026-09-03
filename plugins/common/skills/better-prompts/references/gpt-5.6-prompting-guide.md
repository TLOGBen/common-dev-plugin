# GPT-5.6 Prompting Guidance — Offline Reference

Distilled from OpenAI's official guide: <https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6>
When the user asks for the *current* official wording, fetch the live URL instead of relying on this file.

Core principle: **define the outcome, important constraints, available evidence, and completion bar — then leave room for the model to choose an efficient path.** OpenAI's internal testing showed leaner system prompts improved eval scores ~10–15% while cutting tokens 41–66% and cost 33–67%.

## Table of Contents

1. [Simplify prompts first](#1-simplify-prompts-first)
2. [Outcome-first prompts and stopping conditions](#2-outcome-first-prompts-and-stopping-conditions)
3. [Personality, collaboration, and response length](#3-personality-collaboration-and-response-length)
4. [Autonomy and approval boundaries](#4-autonomy-and-approval-boundaries)
5. [Tool routing](#5-tool-routing)
6. [Programmatic Tool Calling (PTC)](#6-programmatic-tool-calling-ptc)
7. [Grounding, citations, and retrieval budgets](#7-grounding-citations-and-retrieval-budgets)
8. [Long-running workflows and state](#8-long-running-workflows-and-state)
9. [Reasoning effort](#9-reasoning-effort)
10. [Frontend and visual tasks](#10-frontend-and-visual-tasks)
11. [Check work before finishing](#11-check-work-before-finishing)
12. [Suggested prompt structure](#12-suggested-prompt-structure)
13. [Prompt migration workflow](#13-prompt-migration-workflow)

## 1. Simplify prompts first

Start from a working prompt and tool set; remove one group at a time, re-evaluating after each removal.

**Trim:**
- Redundant restatements of the same rule
- Style/process instructions that don't change behavior
- Examples that prove unnecessary
- Step-by-step process instructions for behaviors the model already performs reliably
- Unrelated tools and their descriptions

**Preserve:**
- User-visible outcomes
- Success criteria and stopping conditions
- Safety, business, evidence, and permission constraints
- Context-dependent tool-routing rules
- Required output shape and validation needs

**Conflict review:** contradicting rules create instability in GPT-5-class models. After trimming, check the remaining instructions for conflicts — two rules that can't both be satisfied, or a general rule contradicted by a specific one without precedence stated.

## 2. Outcome-first prompts and stopping conditions

Replace step-by-step prescriptions with destination-focused language: state the objective, list success conditions, specify required outputs, and describe fallback behavior for missing evidence. The model can usually find an efficient search/tool/reasoning path when told what success looks like.

**Absolute rules vs. decision rules:** reserve ALWAYS / NEVER / must / only for true invariants — safety rules, required fields, actions that should never occur. For judgment calls (when to search, ask, use tools, iterate), write decision rules instead.

**Explicit stopping-condition example:**

> "Resolve requests using the fewest necessary tool interactions, but prioritize correctness, required evidence, calculations, and citations over loop minimization. After each result, assess whether the core request is answerable with sufficient evidence. If yes, respond. If required evidence remains absent, identify the missing fact and employ the smallest useful fallback."

## 3. Personality, collaboration, and response length

GPT-5.6 defaults to more conciseness than GPT-5.5 — broad brevity instructions ("Be concise") may now be unnecessary or counterproductive. Set the default detail level with the `text.verbosity` API param (low/medium/high); use the prompt only for task-specific length requirements.

- **Personality** — tone, warmth, directness, formality, humor, empathy, polish. Keep it brief and focused on user experience.
- **Collaboration style** — when the model asks questions, makes assumptions, takes initiative, explains tradeoffs, checks work, handles uncertainty.
- **Length control** — state a preservation priority rather than a length cap: *"Lead with conclusions. Include supporting evidence, material caveats, and next actions. Omit secondary detail and repetition."*
- **Tone specificity** — avoid vague labels ("friendly", "empathetic"); describe concrete writing choices: *"State answers directly. If problems are reported, acknowledge the specific issue before suggesting next steps. Apply reassurance only when relevant. Avoid generic praise and unnecessary sign-offs."*
- **Language** — specify the intended output language and the conditions for switching it.
- **Editing/rewrites/summaries** — *"Preserve the requested artifact, length, structure, genre, and factual claims first. Improve clarity, flow, and correctness without adding new claims, sections, or promotional tone unless requested."*

## 4. Autonomy and approval boundaries

GPT-5.6 is proactive in multi-step tasks. State what authority each kind of request grants so safe in-scope work proceeds without pauses while risky actions stay gated.

**Compact policy example:**
- Analytical requests (answer, explain, review, diagnose, plan): *"Inspect relevant materials and report results. Do not implement changes unless explicitly requested."*
- Action requests (change, build, fix): *"Make requested in-scope local changes and run relevant non-destructive validation without asking first."*
- Sensitive actions: *"Require confirmation for external writes, destructive actions, purchases, or material scope expansion."*

Name safe local actions explicitly (reading files, inspecting logs, editing code, running tests). State each rule once. For long-running work, identify the current work layer (research / design / implementation / review / external coordination).

## 5. Tool routing

Expose only task-relevant tools. Each description should cover: what the tool does, when to use it, important return fields, error behavior.

**Prerequisites:** *"Before taking an action, resolve required discovery, retrieval, and validation steps. Do not skip prerequisites because the intended final state seems obvious."*

Parallelize independent reads; keep work sequential when a result determines the next action; synthesize after parallel retrieval before acting. For empty/partial/suspicious results, try one or two meaningful fallbacks before concluding no result exists.

## 6. Programmatic Tool Calling (PTC)

Best for bounded workflows where code processes many tool results or large intermediate outputs into a smaller structured result.

**Justified:** filtering/joining/sorting/ranking/deduplication/aggregation; batching across many similar records; repeated deterministic validation; large structured results reducible to compact schemas.

**Prefer direct tool calls when:** one call suffices; intermediate outputs are already small; each result may change the next decision; approval is required; the final answer must preserve citations or native artifacts; the workflow needs semantic judgment between calls.

**Prompting pattern:** state the bounded stage, eligible tools, output schema, retry limits, stop conditions, and the handoff back to model judgment. Example:

> "Use Programmatic Tool Calling only for the bounded record-reduction stage. Call only documented read-only tools. Filter and deduplicate intermediate results, then emit the required compact schema with evidence fields. Retry transient failures at most twice. Use direct tool calls for approval, semantic judgment, citations, and final validation."

**Testing:** test both `program_output` items and the final assistant message; compare direct vs. programmatic on representative tasks; verify correctness/completeness/evidence; measure tokens, latency, cost, calls, turns, retries. Count resource reduction as a win only when responses still pass existing evals.

## 7. Grounding, citations, and retrieval budgets

Make citation behavior explicit: what needs support, what counts as sufficient evidence, and what to do when evidence is missing.

**Q&A retrieval budget:**
- *"Start with one broad search using short, discriminative keywords. If top results contain sufficient support for the core request, answer from those results."*
- *"Make another retrieval call only when required facts, owners, dates, IDs, or sources are missing; the user requested exhaustive coverage or comparison; a specific artifact must be read; or an important claim would otherwise be unsupported."*
- *"Do not search again to improve phrasing, add examples, or support nonessential detail."*

**Research/synthesis standards:** cite only retrieved sources; attach citations to supported claims; label inference separately from directly supported facts; state conflicts between sources; narrow the answer or report missing evidence rather than guessing.

**Creative drafting:** distinguish source-backed facts from creative wording. Never invent names, metrics, dates, roadmap status, customer outcomes, or product capabilities.

## 8. Long-running workflows and state

For multi-step or tool-heavy tasks: a short visible preamble before the first tool call, then sparse outcome-based updates at major phase changes. Do not narrate routine tool calls.

> "Before tool calls for multi-step tasks, send a one- or two-sentence user-visible update stating the first step. During the task, update only when a major phase begins or findings change the plan. Each update should state one concrete outcome and the next step."

- **State preservation:** preserve assistant phase values when replaying history; with `previous_response_id` prior state is automatic; when replaying manually, keep each original phase value unchanged.
- **Compaction:** compact after major milestones, not every turn; keep the prompt functionally consistent; treat compacted items as opaque state.
- **Persisted reasoning:** valuable when objectives/assumptions/priorities are stable; use current-turn behavior when earlier reasoning is obsolete. Not an always-on optimization — stale reasoning adds tokens and latency and anchors to outdated approaches.
- **Prompt caching:** keep reusable prefixes stable; avoid churn in large system prompts; explicit cache breakpoints only when they measurably improve behavior and cost.

## 9. Reasoning effort

Establish baseline performance before changing reasoning effort.

- Preserve the current GPT-5.5/5.4 effort as baseline; test that setting *and one level lower* on representative tasks.
- `low` for latency-sensitive work when quality holds; `medium` as balanced start; `high`/`xhigh` only when evals show meaningful gain; `max` reserved for the hardest quality-first workloads — never a global default.
- Before increasing effort to fix failures, verify the prompt already includes success criteria, dependency rules, tool-routing rules, and verification loops — missing structure is the more common cause.

## 10. Frontend and visual tasks

GPT-5.6 has stronger layout/hierarchy/design judgment. Provide product context, preserve existing design systems, name the relevant states and constraints.

**Incremental changes:** inspect and preserve existing design tokens/components/patterns; no extra features or decorative UI unless requested; preserve responsive behavior and expected states; render and inspect results before finalizing.

**Image detail:** for vision, computer-use, localization, or OCR tasks needing spatial precision, choose image detail intentionally — original detail for large/dense/coordinate-sensitive images when cost and latency justify it.

## 11. Check work before finishing

Grant access to validation tools and state which validation matters.

**Coding:**

> "After making changes, run the most relevant validation available: targeted tests for changed behavior; type or lint checks when applicable; build checks for affected packages; a minimal smoke test when full validation is too expensive. If validation cannot be run, explain why and describe the next best check."

**Visual artifacts:** *"Render the artifact before finalizing. Inspect layout, clipping, spacing, missing content, and visual consistency. Revise until the rendered output matches the requirements."*

**Implementation plans** should include: requirements, named resources/files, state transitions or data flow, validation checks, failure behavior, privacy/security considerations, and open questions that materially affect implementation.

## 12. Suggested prompt structure

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

## 13. Prompt migration workflow

Moving an existing application to GPT-5.6:

1. Switch model, preserving current reasoning effort.
2. Run evals on representative tasks *before* prompt changes.
3. Remove obsolete scaffolding, repeated instructions, irrelevant tools.
4. Add targeted instructions that fix *measured* regressions only.
5. Re-run evals after each prompt or reasoning change.

**Debugging regressions:** use small sets of real traces → identify the failure mode → find the likely instruction or contradiction → make surgical edits → re-run the same cases.

Key principle: do **not** rewrite a working prompt stack wholesale. Incremental changes let you attribute behavior changes to model, reasoning effort, prompt, tools, or runtime.

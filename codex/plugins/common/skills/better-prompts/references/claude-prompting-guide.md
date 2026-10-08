# Claude Prompting Guidance — Offline Reference

As of 2026-10-08. Current generation: Claude Opus 5.5, Claude Sonnet 5.5, Claude Haiku 5.5, Claude Fable 5.1 (and Mythos 5.1). Guidance below also holds for the 4.6+ / 5-family models unless a bullet names a model.

Distilled from Anthropic's official docs:

- Prompting best practices (all current models, with a per-model table): <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>
- Per-model prompting pages: [Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5), [Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5), [Haiku 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5), [Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1)
- Migration: <https://platform.claude.com/docs/en/about-claude/models/migration-guide> and <https://platform.claude.com/docs/en/models/opus-5-5/migration-guide>
- Effort: <https://platform.claude.com/docs/en/build-with-claude/effort>
- Claude Code skills: <https://code.claude.com/docs/en/skills>

Anthropic says existing prompts for the previous model in each line (Opus 5, Sonnet 5, Fable 5) should perform well without changes; the per-model pages list what to adjust when you observe a specific behavior. Where a technique names a model, it was measured on that model — re-check it on your own evals before applying it elsewhere. When the user asks for the *current* official wording, fetch the live docs.

Core principle: **modern Claude models follow instructions literally and closely — state the goal, the completion bar, and the true invariants, then remove the scaffolding written to fight older models.** Over-prescriptive prompts written for prior models actively reduce output quality on current ones.

## Contents

1. [Dial back aggressive language](#1-dial-back-aggressive-language)
2. [Literal instruction following](#2-literal-instruction-following)
3. [Outcome-first task specification](#3-outcome-first-task-specification)
4. [Autonomy, asking, and finishing the task](#4-autonomy-asking-and-finishing-the-task)
5. [Tool descriptions, triggering, and search](#5-tool-descriptions-triggering-and-search)
6. [Narration, progress updates, and writing style](#6-narration-progress-updates-and-writing-style)
7. [Grounding progress claims and verification](#7-grounding-progress-claims-and-verification)
8. [Boundaries and scope](#8-boundaries-and-scope)
9. [Subagents and delegation](#9-subagents-and-delegation)
10. [Memory surfaces and compaction](#10-memory-surfaces-and-compaction)
11. [Claude Code: CLAUDE.md, skills, and settings](#11-claude-code-claudemd-skills-and-settings)
12. [Common review-harness and design pitfalls](#12-common-review-harness-and-design-pitfalls)
13. [Thinking and reasoning instructions](#13-thinking-and-reasoning-instructions)
14. [Untrusted text and mid-turn messages](#14-untrusted-text-and-mid-turn-messages)
15. [API-level knobs (not prompt text)](#15-api-level-knobs-not-prompt-text)

## 1. Dial back aggressive language

Prompts written to *overcome* older models' reluctance now overtrigger. Claude 4.6+ follows the system prompt much more closely:

| Written for older models | Use now |
|---|---|
| `CRITICAL: You MUST use this tool when...` | `Use this tool when...` |
| `Default to using [tool]` | `Use [tool] when it would improve X` |
| `If in doubt, use [tool]` | *(delete — no longer needed)* |

If a tool or behavior overtriggers, the fix is almost always to soften the language, not to add more guardrails. Reserve absolute language (ALWAYS/NEVER/must) for true invariants — safety rules, required fields, actions that must never occur.

## 2. Literal instruction following

Current Claude models interpret prompts literally and explicitly. They do not silently generalize an instruction from one item to another, and they do not infer requests that weren't made.

- If an instruction should apply broadly, state the scope: *"Apply this formatting to every section, not just the first one."*
- Re-baseline holdover style directives ("be concise") — they now apply at face value and may overcorrect.
- Ambiguous or underspecified instructions that relied on the model generalizing intent should be made precise.
- Action vs. suggestion is read literally too: "can you suggest some changes" may yield suggestions only; "change this function to…" yields the change. State which you want, or set a default-to-action / do-not-act-before-instructions policy in the system prompt.

## 3. Outcome-first task specification

For long-horizon and agentic work, give the full task specification up front in one well-specified turn: the goal, the constraints, and what "done" looks like. Well-specified initial prompts maximize autonomy and quality; ambiguous prompts revealed progressively over turns reduce both.

**De-prescribe.** Prompts and skills written as step-by-step scripts for prior models often reduce quality on current models. Prefer stating the goal, constraints, and completion bar over enumerating the steps — then A/B with the old scaffolding removed. Anti-overplanning nudge for ambiguous tasks:

> "When you have enough information to act, act. Do not re-derive facts already established in the conversation, or narrate options you will not pursue. If you are weighing a choice, give a recommendation, not an exhaustive survey."

Anti-overengineering nudge:

> "Don't add features, refactor, or introduce abstractions beyond what the task requires. Don't add error handling or validation for scenarios that cannot happen. Only validate at system boundaries."

## 4. Autonomy, asking, and finishing the task

Grant autonomy on the small stuff while keeping caution where it matters:

> "For minor choices (naming, formatting, default values, which approach among equivalents), pick a reasonable option and note it rather than asking. For scope changes or destructive actions, still ask first."

**Early stops are the main current failure in unattended runs:**

- **Opus 5.5** sometimes ends a turn with a text-only progress report on long multi-part tasks; an unattended loop that treats `end_turn` as "done" stops there. Harness fix: keep the task's parts in a checklist (to-do tool or file); when a turn ends with open items and no stated blocker, send a short user message naming them; cap automatic continuations at two or three. Prompt fix: name the specific kinds of early stop to avoid (e.g. a summary that announces the next step instead of taking it, an offer to continue, a list of non-blocking decisions) and the stops you do want (nothing can move without the user). Add it from the first request, and leave it out of human-in-the-loop apps.
- **Sonnet 5.5** at `low`/`medium` effort and **Haiku 5.5** at `low` effort with long agent prompts sometimes check in or hand back before the work is done. Try higher effort first; otherwise: *"Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step."*
- **Fable 5.1** on long async work may describe the next step instead of doing it, or ask permission for work already requested. Tell it the user is not watching and cannot answer mid-task; proceed with reversible actions that follow from the request; stop only for destructive actions or genuine scope changes; before ending a turn, if the last paragraph is a plan or promise, do that work now. Keep the exception: when the user is describing a problem or asking a question, the deliverable is the assessment.

These additions make the model carry on where it would have stopped — keep your own confirmation rules for risky or irreversible actions.

## 5. Tool descriptions, triggering, and search

Current models can reach for tools, search, and subagents **more conservatively** than you expect — especially at low effort. Two levers:

- **Put the trigger condition in each tool's own `description`** — prescriptive "call this when…" descriptions give measurable lift over descriptions that only say what the tool does: *"Call this when the user asks about current prices or recent events."*
- **System-prompt triggering guidance** for capabilities that need a decide-to-use step.

**Search:**
- Remove language that discourages tools ("only use tools when strictly necessary", "minimize tool calls") before adding nudges.
- Give the model today's date when it has a search tool (measured on Haiku 5.5).
- Nudge it to search for specifics that may have changed since training (what is allowed, required, charged; versions; office holders; anything "latest") even when it feels confident, and to search unfamiliar or fast-moving names as the user wrote them (Sonnet 5.5, Haiku 5.5, Fable 5.1 at `low`).
- Avoid blanket "search for any present-day factual question" rules — on Haiku 5.5 that doubled unnecessary searches without more correct answers.

**Forced tool use:** Opus 5.5 rejects `tool_choice` `any`/`tool`. Use `auto` (with strict tool use or structured outputs where available) and **say in the prompt when the tool applies**.

**Parallel calls:** current models parallelize independent calls by default and the behavior is steerable. Fable 5.1 may issue one call per turn in coding / computer-use loops where the next calls are implied rather than requested; a one-line nudge to request every independent item in one response, sent after each round of tool results, fixes it.

Also: expose only task-relevant tools; each description covers what it does, when to use it, key return fields, and error behavior. Harness note (Sonnet 5.5): accept unambiguous tool-name case mismatches, or return `is_error` with the exact expected name.

## 6. Narration, progress updates, and writing style

- **Remove forced-progress scaffolding** (*"after every 3 tool calls, summarize progress"*) — current models give updates on their own.
- **Progress updates now arrive as thinking blocks** on Opus 5.5, Fable 5.1, and (for longer notes) Sonnet 5.5, and are empty at the default `thinking.display`. A "silent agent" is often a client issue — set `display: "updates"` before changing the prompt.
- **Model-specific tendencies:** Opus 5 defaults to longer responses (prompt explicitly for conciseness; effort does not reliably change visible length). Fable 5.1 writes *fewer* updates during long tool chains — remove old lines like "hold all findings for the final response", then ask for a one-line intent up front and a standalone recap at the end. For predictable update points on any model, say so in the system prompt.
- If a coding agent is too chatty, add a silence default: *"Default to silence between tool calls. Only write text when you find something, change direction, or hit a blocker — one sentence each. When done: one or two sentences on the outcome."*
- To reduce verbosity, state a preservation priority, not a length cap. Positive examples of the desired concision beat "don't" instructions.
- **Formatting:** Fable 5.1 leans toward *less* formatting than earlier models; old anti-formatting rules can now under-format. Replace them with a rule saying when lists or headers are appropriate.
- **Prose style:** Fable 5.1's prose can run dense; defining the anti-pattern ("mannered prose": metaphor and flourish in place of direct statement) and asking for literal phrasing helps.
- **Quoting sources:** Fable 5.1 may reproduce source passages unmarked when summarizing; one complete example of a correct response (request, response, rationale) in the system prompt fixes it.

## 7. Grounding progress claims and verification

For long-running agents, require claims to be audited against evidence — this nearly eliminates fabricated status reports:

> "Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. If tests fail, say so with the output; if a step was skipped, say that."

**Verification on coding tasks:** Sonnet 5.5 at `low` and Haiku 5.5 at `low`/`medium` sometimes report a change as done without running a check. Anthropic's measured fix: when code can be run, built, or type-checked, run a real check that exercises the change (tests, type-checker, build, or the changed command); a syntax-only check or a check that failed to start doesn't count; install missing declared dependencies with the project's own package manager; if no real check can run, say which one wasn't run and why instead of reporting done.

## 8. Boundaries and scope

State what the agent should *not* do — current models sometimes take unrequested-but-adjacent actions:

> "When the user is describing a problem or asking a question rather than requesting a change, the deliverable is your assessment — report findings and stop. Require confirmation for external writes, destructive actions, or material scope expansion."

Name safe local actions explicitly (reading files, inspecting logs, running tests) so in-scope work proceeds without pauses.

**Unrequested additions:** Sonnet 5.5 tends to add tests, docs, and small supporting files (more at higher effort); Fable 5.1 may fix nearby code, extend behavior, or commit more tests than warranted. If you want changes limited to the request: *"When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it."* For open-ended requests ("show me what you can do"), say whether you want ideas/a plan first or a built artifact.

## 9. Subagents and delegation

Current models orchestrate subagents natively; give explicit guidance on *when* delegation is warranted rather than suppressing or forcing it:

> "Use subagents when tasks can run in parallel, require isolated context, or involve independent workstreams that don't need to share state. For simple tasks, sequential operations, single-file edits, or tasks where you need to maintain context across steps, work directly rather than delegating."

- Opus 5 delegates more readily than prior models; damp it with the guidance above if overused.
- Sonnet 5.5 at `xhigh`/`max` may start its own review rounds with reviewer subagents after finishing; *"don't launch reviewer sub-agents unless the user asked for a review"* cut cost ~⅓ with no quality change in Anthropic's test.
- Opus 5.5 paces multiagent work to elapsed-time signals: a time budget line (e.g. `elapsed 340s / 1200s`) appended by the harness, or one sentence that time matters, made agent teams finish sooner. The budget is advisory — keep a hard timeout.
- Fable 5.1: let the lead keep working while subagents run (spawn tool returns immediately, results arrive later, separate wait tool).

Fresh-context verifier subagents tend to outperform self-critique for checking work.

## 10. Memory surfaces and compaction

Models perform notably better with a place to write learnings — even a plain `.md` file. Tell the agent where it is, when to consult it, and give a format:

> "Store one lesson per file with a one-line summary at the top. Don't save what the repo or chat history already records; update an existing note rather than creating a duplicate; delete notes that turn out to be wrong."

For client-side compaction, tell the model exactly what the summary must preserve: problems and how they were handled; options tried or set aside and why; decisions, preferences, constraints stated exactly; current state; open items; hard-to-reconstruct details (names, numbers, dates, exact wording, links) kept exactly.

## 11. Claude Code: CLAUDE.md, skills, and settings

When the optimization target is a Claude Code configuration rather than an API system prompt:

- **CLAUDE.md holds facts and constraints, not procedures.** It loads into every session — every line pays context cost every time. Keep it to project invariants, conventions, and boundaries. When a section grows into a step-by-step procedure, move it into a skill (skills load only when relevant).
- **Skill descriptions do the triggering.** Write them in third person, stating both what the skill does and when to use it, with the specific words a user would say. Vague descriptions ("helps with documents") cause both under- and over-triggering.
- **Keep a skill's body under ~500 lines**; push detail into `references/` files linked one level deep from SKILL.md, with guidance on when to read each.
- **Automated behaviors need hooks, not prose.** "Always run X after every edit" in CLAUDE.md is advisory; a PostToolUse hook in settings.json is enforced. Route rules that must never be skipped to hooks/settings, keep judgment calls in prose.
- **Don't ask skills to make the model write out its reasoning** — on Fable 5.1 / Opus 5.5, prompts, skills, or tool descriptions that do so may be declined with the `reasoning_extraction` refusal category (see §13).
- **Conflict review applies doubly**: user-level CLAUDE.md, project CLAUDE.md, rules files, and skill bodies stack in one context. Contradictions between layers cause instability — when optimizing one layer, scan the others for rules that conflict with it.

## 12. Common review-harness and design pitfalls

- **Code-review prompts:** "only report high-severity issues" / "be conservative" is followed literally — measured recall drops even though bug-finding improved. Use coverage-first: *"Report every issue you find, including uncertain or low-severity ones, each with confidence and severity — a downstream step will filter."*
- **Design/frontend prompts:** without design direction, current models fall back on a few default styles, and a generic "avoid a generic AI look" mostly swaps one default for another. Name the specific patterns to avoid (Opus 5.5 responds well to this) and extend the list iteratively after seeing the first result; or give a concrete spec (exact palette, typefaces, layout); or have the model propose 3–4 distinct directions and let the user pick.
- **Dense visual inputs:** current models read charts and screenshots much better without tools — re-test old visual scaffolding. For the densest inputs, crop/zoom tools (or a container with PIL/OpenCV) still add accuracy.
- **Targeted edits:** if Fable 5.1 rewrites whole files for small changes, tell it to edit surgically when the result is the same.

## 13. Thinking and reasoning instructions

- **Effort, not prompt text, controls thinking.** Lowering effort reduces thinking more reliably than instructions do; on Sonnet 5.5 and Haiku 5.5, asking in the prompt to think less or answer directly did not reliably stop thinking.
- **Remove "think carefully before answering" lines from chat system prompts** on Opus 5.5 — the model decides how much to think; removal made replies start sooner with no clear quality loss. Optionally tell it to treat earlier answers as settled on later turns (reduces follow-up thinking; may make it less likely to self-correct, so test).
- **Remove instructions that stood in for thinking** (e.g. "write out your reasoning step by step in the response"). With thinking always on, read reasoning from summarized thinking blocks instead; asking for reasoning in the visible response may be declined as `reasoning_extraction`. A short explanation of the answer or a summary of actions is still fine.
- **Reasoning tasks with JSON output** (Sonnet 5.5): with structured outputs the model can work only in its thinking and may skip it at low/medium effort; adding *"Think the problem through before you answer."* to the end of the system prompt raises accuracy.
- **Long deliverables at `xhigh`/`max`** (Fable 5.1): the model may draft the whole deliverable in thinking and again in the reply. Prefer `high`; otherwise leave `max_tokens` room and tell it not to compose the full output twice.

## 14. Untrusted text and mid-turn messages

- **Pasted content** (Opus 5.5): wrap text the user pasted from elsewhere in tags carrying a short random ID (e.g. `<pasted_content id="ab12">…</pasted_content id="ab12">`) and tell the model to follow instructions inside only where the user's own message asks. One guardrail among others — tags can be imitated.
- **Mid-turn user messages** (Sonnet 5.5, Haiku 5.5): models trained to resist injection may ignore a genuine user message that arrives inside a `tool_result` or right after one as a system message. Never put user text in a `tool_result`; append it as a user text block after the last `tool_result`; keep harness notices in a separate system message; avoid per-step countdowns in interactive sessions.
- **Chatbots holding their rules** (Haiku 5.5): state that the system prompt's rules hold for the whole conversation, including when a user argues, gives a sympathetic reason, asks for a small part, or claims an exception was approved.

## 15. API-level knobs (not prompt text)

These are request parameters on the Claude API, not prompt content — flag them when relevant but don't write them into the prompt:

- **Effort** (`output_config.effort`: `low`, `medium`, `high`, `xhigh`, `max`) is the main control for thinking depth, latency, and cost. Defaults differ by model (Opus 5.5 `medium`; Sonnet 5.5 `high` on the API; Haiku 5.5 `medium`; Fable 5.1 `high`), and level names don't map to the same thinking across models — run a fresh sweep instead of carrying a setting over. Reserve `xhigh`/`max` for measured gains and size `max_tokens` for thinking plus reply.
- **Thinking mode:** `budget_tokens` is rejected on 4.7+. Opus 5.5 always thinks (adaptive; `disabled` is rejected). Sonnet 5.5 offers `thinking: {type: "between_tools"}` as its lowest setting (at `high` effort or below). Haiku 5.5 can disable thinking at `low`–`high` only. Responses can begin with `thinking` blocks — read content by block type and pass thinking blocks back unchanged.
- **Append-only history:** on Fable 5.1, Opus 5.5, Sonnet 5.5, and Haiku 5.5, editing earlier messages, `system`, or `tools` mid-conversation invalidates later thinking blocks (and the prompt cache). Use mid-conversation / turn-scoped system messages for new instructions and reminders, and per-message effort changes (beta) instead of changing top-level effort.
- Sampling params (`temperature`/`top_p`/`top_k`) and assistant prefill are rejected on current models — steer style via prompt, use structured outputs for format, get design variety via propose-N-directions.
- Prompt caching is a prefix match: keep the system prompt frozen (no timestamps/UUIDs), put volatile content last.
- Task budgets (`output_config.task_budget`, beta) let an agent pace itself against a token ceiling.
- Refusals arrive as `stop_reason: "refusal"` with `stop_details.category` (e.g. `cyber`, `bio`, `reasoning_extraction`); handle them and configure fallback.

# Claude Prompting Guidance — Offline Reference

Distilled from Anthropic's official guidance for Claude 4.6-family and Claude 5-family models (Opus 4.6/4.7/4.8, Sonnet 4.6/5, Fable 5), including the model migration guides and Claude Code documentation. When the user asks for the *current* official wording, fetch the live docs: <https://platform.claude.com/docs/en/about-claude/models/migration-guide> and <https://code.claude.com/docs/en/skills>.

Core principle: **modern Claude models follow instructions literally and closely — state the goal, the completion bar, and the true invariants, then remove the scaffolding written to fight older models.** Over-prescriptive prompts written for prior models actively reduce output quality on current ones.

## Contents

1. [Dial back aggressive language](#1-dial-back-aggressive-language)
2. [Literal instruction following](#2-literal-instruction-following)
3. [Outcome-first task specification](#3-outcome-first-task-specification)
4. [Autonomy and asking](#4-autonomy-and-asking)
5. [Tool descriptions and triggering](#5-tool-descriptions-and-triggering)
6. [Narration and verbosity](#6-narration-and-verbosity)
7. [Grounding progress claims](#7-grounding-progress-claims)
8. [Boundaries and scope](#8-boundaries-and-scope)
9. [Subagents and delegation](#9-subagents-and-delegation)
10. [Memory surfaces](#10-memory-surfaces)
11. [Claude Code: CLAUDE.md, skills, and settings](#11-claude-code-claudemd-skills-and-settings)
12. [Common review-harness and design pitfalls](#12-common-review-harness-and-design-pitfalls)
13. [API-level knobs (not prompt text)](#13-api-level-knobs-not-prompt-text)

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

## 3. Outcome-first task specification

For long-horizon and agentic work, give the full task specification up front in one well-specified turn: the goal, the constraints, and what "done" looks like. Well-specified initial prompts maximize autonomy and quality; ambiguous prompts revealed progressively over turns reduce both.

**De-prescribe.** Prompts and skills written as step-by-step scripts for prior models often reduce quality on current models. Prefer stating the goal, constraints, and completion bar over enumerating the steps — then A/B with the old scaffolding removed. Anti-overplanning nudge for ambiguous tasks:

> "When you have enough information to act, act. Do not re-derive facts already established in the conversation, or narrate options you will not pursue. If you are weighing a choice, give a recommendation, not an exhaustive survey."

Anti-overengineering nudge:

> "Don't add features, refactor, or introduce abstractions beyond what the task requires. Don't add error handling or validation for scenarios that cannot happen. Only validate at system boundaries."

## 4. Autonomy and asking

Recent models are more deliberate and may ask about minor decisions. Grant autonomy on the small stuff while keeping caution where it matters:

> "For minor choices (naming, formatting, default values, which approach among equivalents), pick a reasonable option and note it rather than asking. For scope changes or destructive actions, still ask first."

For fully autonomous pipelines, add an explicit no-blocking instruction:

> "You are operating autonomously. For reversible actions that follow from the original request, proceed without asking. End your turn only when the task is complete or you are blocked on input only the user can provide."

## 5. Tool descriptions and triggering

Current models reach for tools, subagents, memory, and search **more conservatively** than older ones. Two levers:

- **Put the trigger condition in each tool's own `description`** — prescriptive "call this when…" descriptions give measurable lift over descriptions that only say what the tool does: *"Call this when the user asks about current prices or recent events."*
- **System-prompt triggering guidance** for capabilities that need a decide-to-use step:

> "For questions where current information would change the answer, search before answering rather than answering from memory. When a task fans out across independent items, delegate to subagents rather than iterating serially."

Also: expose only task-relevant tools; each description covers what it does, when to use it, key return fields, and error behavior.

## 6. Narration and verbosity

Current models calibrate response length to task complexity and give good in-progress updates by default:

- **Remove forced-progress scaffolding** (*"after every 3 tool calls, summarize progress"*) — it now produces excessive narration.
- If a coding agent is too chatty, add a silence default: *"Default to silence between tool calls. Only write text when you find something, change direction, or hit a blocker — one sentence each. When done: one or two sentences on the outcome."*
- To reduce verbosity, state a preservation priority, not a length cap: *"Provide concise, focused responses. Skip non-essential context, keep examples minimal."* Positive examples of the desired concision beat "don't" instructions.

## 7. Grounding progress claims

For long-running agents, require claims to be audited against evidence — this nearly eliminates fabricated status reports:

> "Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. If tests fail, say so with the output; if a step was skipped, say that."

Pair with a self-verification loop: *"After making changes, run the most relevant validation available (targeted tests, lint/type checks, a minimal smoke test). If validation cannot be run, explain why and describe the next best check."*

## 8. Boundaries and scope

State what the agent should *not* do — current models sometimes take unrequested-but-adjacent actions:

> "When the user is describing a problem or asking a question rather than requesting a change, the deliverable is your assessment — report findings and stop. Require confirmation for external writes, destructive actions, or material scope expansion."

Name safe local actions explicitly (reading files, inspecting logs, running tests) so in-scope work proceeds without pauses.

## 9. Subagents and delegation

Parallel subagents are dependable on current top-tier models — give explicit guidance on *when* delegation is desirable instead of suppressing it:

> "Do NOT spawn a subagent for work you can complete directly in a single response. Spawn multiple subagents in the same turn when fanning out across independent items or reading many files. Intervene if a subagent goes off track."

Fresh-context verifier subagents tend to outperform self-critique for checking work.

## 10. Memory surfaces

Models perform notably better with a place to write learnings — even a plain `.md` file. Tell the agent where it is, when to consult it, and give a format:

> "Store one lesson per file with a one-line summary at the top. Don't save what the repo or chat history already records; update an existing note rather than creating a duplicate; delete notes that turn out to be wrong."

## 11. Claude Code: CLAUDE.md, skills, and settings

When the optimization target is a Claude Code configuration rather than an API system prompt:

- **CLAUDE.md holds facts and constraints, not procedures.** It loads into every session — every line pays context cost every time. Keep it to project invariants, conventions, and boundaries. When a section grows into a step-by-step procedure, move it into a skill (skills load only when relevant).
- **Skill descriptions do the triggering.** Write them in third person, stating both what the skill does and when to use it, with the specific words a user would say. Vague descriptions ("helps with documents") cause both under- and over-triggering.
- **Keep a skill's body under ~500 lines**; push detail into `references/` files linked one level deep from SKILL.md, with guidance on when to read each.
- **Automated behaviors need hooks, not prose.** "Always run X after every edit" in CLAUDE.md is advisory; a PostToolUse hook in settings.json is enforced. Route rules that must never be skipped to hooks/settings, keep judgment calls in prose.
- **Conflict review applies doubly**: user-level CLAUDE.md, project CLAUDE.md, rules files, and skill bodies stack in one context. Contradictions between layers cause instability — when optimizing one layer, scan the others for rules that conflict with it.

## 12. Common review-harness and design pitfalls

- **Code-review prompts:** "only report high-severity issues" / "be conservative" is followed literally — measured recall drops even though bug-finding improved. Use coverage-first: *"Report every issue you find, including uncertain or low-severity ones, each with confidence and severity — a downstream step will filter."*
- **Design/frontend prompts:** generic "make it clean" shifts the model to a different fixed palette rather than producing variety. Either specify a concrete spec (exact hex/typefaces/layout), or have the model propose 3–4 distinct directions and let the user pick one.

## 13. API-level knobs (not prompt text)

These are request parameters on the Claude API, not prompt content — flag them when relevant but don't write them into the prompt:

- `output_config.effort` (`low`→`max`) controls thinking depth and token spend; raising effort beats prompting around shallow reasoning.
- Adaptive thinking (`thinking: {type: "adaptive"}`) replaces `budget_tokens` on 4.6+; on Fable 5 thinking is always on.
- Sampling params (`temperature`/`top_p`/`top_k`) are removed on Opus 4.7+/Sonnet 5/Fable 5 — steer style via prompt, get design variety via propose-N-directions.
- Prompt caching is a prefix match: keep the system prompt frozen (no timestamps/UUIDs), put volatile content last.
- Task budgets (`output_config.task_budget`, beta) let an agent pace itself against a token ceiling.

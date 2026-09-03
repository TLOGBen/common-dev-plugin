---
name: better-prompts
description: Optimizes prompts — use when the user says "improve this prompt", "optimize my system prompt", "幫我改 prompt", "優化 prompt", "審 prompt", or "migrate this prompt to a newer model", wants a prompt improved, reviewed, shortened, or written from scratch, or asks why a model ignores instructions or burns tokens. Audits, rewrites, drafts, and migrates system prompts, agent instructions, tool descriptions, CLAUDE.md files, and full prompt stacks against official Claude and GPT-5.x prompting guidance. Not for polishing prose that isn't a prompt.
---

# Better Prompts

## Output language

Keep these skill instructions in English. Default user-facing explanations and newly authored human-readable text to Traditional Chinese. If the user explicitly requests another language, use it instead. Preserve code, identifiers, commands, quoted source text, and the supplied prompt's language unless translation is part of the request.

Turn an existing prompt or rough intent into a lean, outcome-first prompt. Preserve the user's explicit values, real constraints, and required behavior; remove detail only when it does not change the contract.

## Establish the task

1. Identify the artifact: single prompt, prompt template, tool description, agent instructions, or layered prompt stack.
2. Identify the requested operation: create, improve, audit, or migrate.
3. Extract the user-visible outcome, true invariants, available evidence, authorized actions, required output, validation, and completion bar.
4. Preserve the original language unless the user requests another language.
5. For a prompt stack, respect instruction precedence and locate each rule at the highest appropriate stable layer. Do not duplicate a rule across layers for emphasis.

If essential context is absent, ask only for the smallest missing input. Otherwise, make conservative assumptions and label them.

## Improve the prompt

Apply the smallest changes that materially improve behavior:

- Lead with the outcome and measurable success criteria.
- State constraints once. Reserve absolute words such as `always`, `never`, `must`, and `only` for true invariants.
- Replace rigid process scripts with decision rules when more than one valid path exists.
- Preserve explicit user values instead of replacing them with universal defaults or keyword maps.
- Define what evidence is required and what to do when it is missing. Do not turn missing evidence into a factual negative.
- Separate personality from collaboration behavior. Describe observable writing choices instead of vague labels.
- Define autonomy and approval boundaries in one place. Distinguish read/review/diagnose work from implementation and from external, destructive, costly, or scope-expanding actions.
- Expose only relevant tools. Describe when to use each tool, important outputs, failure behavior, and prerequisite retrieval.
- Add output requirements and stop rules, including retry, fallback, ask, abstain, and completion conditions where relevant.
- Remove repeated rules, non-behavior-changing examples, obsolete scaffolding, irrelevant tools, and instructions for behavior the model already performs reliably.
- Check the resulting contract for contradictions and impossible combinations.

Read [references/gpt-5p6-guidance.md](references/gpt-5p6-guidance.md) when the task involves tool routing, grounded research, long-running agents, reasoning effort, visual work, migration, or a full prompt-stack audit.

## Handle migration safely

When migrating an evaluated application prompt to GPT-5.6:

1. Preserve the current reasoning effort and establish a baseline on representative evals.
2. Change the model before rewriting the prompt.
3. Remove obsolete or repeated instructions one coherent group at a time.
4. Add only the smallest targeted rule needed to correct a measured regression.
5. Re-run the same evals after every prompt or reasoning change.
6. Treat lower token use, latency, or cost as an improvement only when required quality still passes.

Do not claim an improvement from prose inspection alone when eval results are available or requested.

## Deliver the result

Match the requested output. If the user does not specify a format, return:

1. `Revised prompt` — ready to paste, without commentary inside the prompt.
2. `Key changes` — only behaviorally meaningful changes and their purpose.
3. `Assumptions or risks` — unresolved conflicts, missing evidence, or migration risks; omit when empty.
4. `Eval cases` — a small set of representative success, boundary, and failure cases for substantial prompt-stack changes; omit for simple rewrites.

Keep the revised prompt no longer than necessary. Do not add sections merely to match a template; use only sections that change behavior.

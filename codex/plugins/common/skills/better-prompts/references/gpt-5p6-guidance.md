# GPT-5.6 prompt guidance reference

Source: [OpenAI — Prompting guidance for GPT-5.6 Sol](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6), summarized for offline use on 2026-07-16. When the user requests current guidance and web access is available, refresh from the official page before relying on this summary.

## Core contract

Define the outcome, important constraints, available evidence, and completion bar. Give the model room to choose an efficient path. Keep success criteria, stopping conditions, safety and permission boundaries, evidence rules, contextual tool-routing rules, output shape, and validation requirements. Remove repetition and instructions or examples that do not change behavior.

Review the remaining prompt for contradictions. Conflicting rules can cause more instability than missing detail.

## Collaboration and output

- Use API `text.verbosity` for a default detail level when applicable; use the prompt for task-specific content and structure.
- Define personality and collaboration separately and briefly.
- For short answers, say which facts, decisions, caveats, and next steps must survive, then identify lower-value detail to trim.
- For editing, specify which artifact properties and factual claims must be preserved.
- Describe concrete writing behavior rather than relying on broad tone labels.

## Autonomy and tools

- State what read-only inspection, local edits, and validation are authorized by each request type.
- Require confirmation before external writes, destructive actions, purchases, or material scope expansion.
- Keep this policy in one place; repeated approval language can cause unnecessary pauses.
- Describe prerequisite retrieval and validation when correctness depends on them.
- Parallelize independent reads; keep dependent work sequential; synthesize retrieved results before acting.
- Try one or two meaningful fallbacks for empty, partial, or suspiciously narrow tool results.
- Use programmatic tool calling only for bounded deterministic reduction over substantial structured results. Keep approval, citations, semantic judgment, and final validation in direct model control.

## Grounding and long-running work

- Define which claims need citations, what sufficient support means, and what to do when evidence is missing.
- Cite retrieved sources at the claims they support, label inference, surface conflicts, and narrow the answer instead of guessing.
- For multi-step work, give a short preamble before tools and update only at meaningful phase changes or when findings change the plan.
- Preserve assistant phase values when replaying history.
- Compact at milestones and avoid anchoring current work to stale persisted reasoning.
- Keep reusable prompt prefixes stable when prompt caching matters.

## Reasoning, visual work, and validation

- Baseline the current reasoning effort before changing it. Test the same level and one lower; raise it only when evals show a material quality gain.
- Before increasing reasoning, check for missing success criteria, dependency rules, tool-routing rules, or validation loops.
- For frontend changes, preserve the existing design system and responsive states, avoid unsolicited decoration, and render and inspect the result.
- Validate changed behavior with the most relevant targeted test, type or lint check, build, or smoke test. If validation cannot run, state why and name the next-best check.

## Starting structure for complex prompts

Use only the sections that change behavior:

- Role and context
- Personality and collaboration style
- Goal
- Success criteria
- Constraints and side-effect boundaries
- Tools and routing rules
- Output requirements
- Stop, retry, fallback, ask, and abstain rules

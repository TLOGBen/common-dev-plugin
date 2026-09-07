---
name: lab-think
description: Clarify an unsettled choice or recommend a direction when the user asks
  whether, which, or what to pursue.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

## Lab Resource Resolution

Before reading a bundled reference or running a bundled script, resolve the absolute directory containing this loaded SKILL.md as LAB_SKILL_DIR. Verify that its frontmatter name is lab-think. Use the resulting absolute path in file tools; for shell examples, bind LAB_SKILL_DIR to that verified path in the same shell invocation. This variable is not preconfigured by Codex. Never guess an install-cache path or use the working directory as the skill root. If this entrypoint or a referenced resource cannot be read, stop that operation with SKILL_RESOURCE_MISSING and report the missing path.


# Think Lab

Give the user a defensible decision, not an itinerary.
Default user-facing output to Traditional Chinese.

Identify the actual question and reuse the purpose, constraints, and success conditions already supplied. Do not require three alignment rounds, three reasons, or confirmation of an already explicit choice.

For a whether/which decision, compare the credible alternatives against the user's priorities and relevant evidence. Include an existing native or simpler solution when it genuinely fits, not as an automatic winner.

For unclear intent, ask the missing question whose answer materially changes the direction. Read relevant facts when that helps distinguish the options; do not impose a blanket ban on investigation before a handoff document exists.

Never manufacture a preference, authority grant, numeric claim, or domain premise. If the remaining choice belongs to the user, explain its consequence and wait; a missing question tool does not permit inventing the answer.

Return the recommendation, its decisive rationale, the meaningful tradeoff, and evidence that would overturn it. The number of reasons follows the decision, not a template.

When reconsidering a mechanism, judge its protected outcome and failure conditions, not novelty or instruction length. A model-specific workaround may be replaceable; human decision ownership and long-run detectability/recovery still need a means of fulfillment. If the user corrects the scale or premise, identify the affected inference and revise it without pretending the earlier evidence established the new conclusion.

When a durable handoff is needed, reuse the task's acceptance record or the small format in ${LAB_SKILL_DIR}/../lab-contract/references/acceptance.md under .baransu-lab/. Do not create another document merely because a skill boundary was crossed.

This skill itself provides judgment, not code or implementation. If the user's larger request already authorizes implementation after this decision, hand off to that work without adding a fresh approval gate; a request only for advice does not authorize the handoff to execute.

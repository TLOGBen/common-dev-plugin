---
name: lab-better-prompts
description: Experimentally audit, shorten, or rewrite a prompt when the user asks
  to improve agent instructions.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Better Prompts Lab

Make the prompt easier to obey without changing the user's objective.
Default explanations and new human-readable artifacts to Traditional Chinese.

Identify the intended outcome, audience or target model, actual failure, and boundaries from the supplied context. Ask only for a missing choice that changes the rewrite.

Keep instructions that change a consequential decision. Remove duplicated policy, generic competence reminders, broad trigger phrases, and inherited rituals without a demonstrated purpose. Express completion and authority explicitly; do not replace them with an itinerary.

For skills, make the description a short selection rule. Keep a simple workflow self-contained; route substantial conditional workflows to references. Moving every old instruction into a mandatory reference is not simplification.

Preserve domain invariants and experience-backed failure protections until their replacement is testable. A stronger model does not make ownership, recovery, or evidence irrelevant.

Preserve the original explicit approval boundaries unless the user authorizes changing them. Reversible, recoverable, generated, or rebuildable does not mean authorized to delete. Removing repetitive prose must not silently convert "ask before deletion" into permission to clean up.

Use current primary guidance when the request depends on a particular model's behavior. Distinguish official guidance, the user's observed experience, and an experimental hypothesis. Never hard-code a universal model ranking from one benchmark.

Return the usable rewrite, the material tradeoffs, and a small realistic test that could falsify the improvement. Report measured reductions separately from unmeasured quality or token savings.

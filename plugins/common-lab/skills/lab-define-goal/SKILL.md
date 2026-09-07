---
name: lab-define-goal
description: Turn an unclear objective into observable completion criteria when the user asks to define success.
---

# Define Goal Lab

Produce a shared definition of success, not a questionnaire.
Default user-facing output to Traditional Chinese.

Extract the outcome, scope, observable acceptance, and stopping boundary from what the user has already said. Propose a concise contract with uncertainty visible.

Ask only about unresolved choices that materially change the outcome, authority, or acceptance. Do not ask the user to reconfirm facts or decisions already supplied. A qualitative objective may use observable examples; do not invent percentages merely to make it look measurable.

Separate required completion from optional exploration. Identify what evidence would demonstrate each required condition and what resources or external decisions are unavailable.

Distinguish outcome evidence (MOE) from activity indicators (MOP): tests run, files changed, or time spent are not substitutes for the promised result. Use the user's language rather than these labels when clearer. For delegated, long-running, or cross-session work, preserve the agreed criteria and their decision source in the task's existing durable record; use an available Contract only when a bounded implementation needs one, not as a second copy of the goal.

If the user explicitly requests a goal tool, use the available goal API after resolving essential ambiguities; otherwise a conversational contract is sufficient. Never invent a token budget. An existing goal remains authoritative unless the user changes it.

For implementation requests with enough information, state the contract and continue within scope. Defining success does not impose an approval gate or authorize additional work.

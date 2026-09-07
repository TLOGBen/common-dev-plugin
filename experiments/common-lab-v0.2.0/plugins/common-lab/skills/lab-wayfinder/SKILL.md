---
name: lab-wayfinder
description: Break a complex unclear effort into a shared decision map paced for human
  understanding.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

## Lab Resource Resolution

Before reading a bundled reference or running a bundled script, resolve the absolute directory containing this loaded SKILL.md as LAB_SKILL_DIR. Verify that its frontmatter name is lab-wayfinder. Use the resulting absolute path in file tools; for shell examples, bind LAB_SKILL_DIR to that verified path in the same shell invocation. This variable is not preconfigured by Codex. Never guess an install-cache path or use the working directory as the skill root. If this entrypoint or a referenced resource cannot be read, stop that operation with SKILL_RESOURCE_MISSING and report the missing path.


# Wayfinder Lab

Reduce the amount a person must understand or decide at once.
Default user-facing output and map contents to Traditional Chinese.

Start with the destination and the uncertainty currently blocking progress. Reuse settled decisions; do not remap the entire system before answering a local question.

Represent only the dependencies needed to expose a useful frontier. Separate fact-finding tasks from choices requiring the user's values, priorities, or authorization. Mark unresolved questions as unknown rather than filling them with plausible assumptions.

For a durable multi-session map, read ${LAB_SKILL_DIR}/references/map-format.md. Keep new maps under .common-lab/wayfinder/. Do not silently migrate a stable Wayfinder campaign.

Advance answerable research or prototypes within scope, using available lab companion skills only when their distinct workflow helps. Independent execution may use lab-delegate; a shared map does not authorize external actions.

At a human decision, present one understandable question with the relevant evidence, options, consequences, and your recommendation. Wait for the answer before dependent work. If the user explicitly requests a batch of decisions, group only those they can evaluate together.

After an answer, record it and continue to the next useful frontier. There is no one-ticket-per-session limit. A missing human choice blocks its dependents, not unrelated fact-finding.

Pace by the person's understanding, not ticket throughput. If the user is confused, overloaded, or asks to pause, repair the current explanation before adding decisions; an available Wait What can help but is not required. Silence or an absent user is not agreement. Continue independent authorized research without turning its results into a backlog of questions the person must absorb at once.

On resumption, recover settled choices and their source from the map before resolving a dependent question. Reopen a choice only when new evidence or the user changes its premise, showing what changed and which dependents are affected. A fresh model or summary is not authority to invent a different decision.

Show the current destination, what became clearer, and the next meaningful decision. Distinguish this round's completed work from remaining product work and say whether human input is needed. At a human handoff, make the immediate choice and its consequences understandable without reading the whole map; a durable map can use the explicit Current focus view pointer. Do not turn a dependency-ready, out-of-scope execution ticket into a supposed pending human decision. Render the map when it helps orientation or at handoff, not after every file edit.

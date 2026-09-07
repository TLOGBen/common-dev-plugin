---
name: lab-contract
description: Pin observable acceptance for a meaningful change when the user asks
  for a work contract or success criteria.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

## Lab Resource Resolution

Before reading a bundled reference or running a bundled script, resolve the absolute directory containing this loaded SKILL.md as LAB_SKILL_DIR. Verify that its frontmatter name is lab-contract. Use the resulting absolute path in file tools; for shell examples, bind LAB_SKILL_DIR to that verified path in the same shell invocation. This variable is not preconfigured by Codex. Never guess an install-cache path or use the working directory as the skill root. If this entrypoint or a referenced resource cannot be read, stop that operation with SKILL_RESOURCE_MISSING and report the missing path.


# Contract Lab

Write criteria strong enough to reject a broken result, then let implementation judgment operate.
Default user-facing output and acceptance records to Traditional Chinese.

Reuse a suitable existing acceptance record for this task. Read ${LAB_SKILL_DIR}/references/acceptance.md when creating or materially revising it; default to .baransu-lab/acceptance/<task>.md, not the stable CONTRACT.md.

Read the code or authoritative material on which the criteria depend. Separate verified premises from assumptions and missing evidence. For greenfield work, identify that no existing implementation was available; do not fabricate code facts.

Pin WHAT must hold: observable outcomes, consequential failure cases, affected boundaries, and exact constants supplied by the requirement. Use exact text or explicit exclusions when extra fields would be a defect; do not pin arbitrary wording or a shared helper merely to prescribe HOW.

Turn a discovered consequential trap into an independently assertable condition with an evidence path. Check that the path exercises the real behavior rather than a mock of the very layer being certified.

An uncertain data source, schema, permission rule, or domain premise remains uncertain until supported. Isolate its dependent condition; still pin adjacent independent filters, mappings, and authorization dimensions. Missing evidence is not a blanket waiver.

Present the resulting contract and any material unresolved decision. Existing clear user choices and applicable authorization count; do not demand a ceremonial reconfirmation. Pause only where a changed outcome, authority boundary, or user-owned tradeoff requires a new decision.

Preserve a task's record and its evidence history. Do not overwrite another task's contract or archive/delete a completed one automatically. If scope changes, revise only the affected criteria with the evidence and authority for that revision.

Contract creation does not certify implementation. Hand the same record to implementation or verification only when the user's request includes that work. Do not emit a stable sealed marker or write stable hook telemetry.

---
name: lab-grilling
description: Stress-test a plan or decision when the user asks for a skeptical challenge
  to their reasoning.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Grilling Lab

Expose the assumption most likely to overturn the decision.
Default user-facing output to Traditional Chinese.

Start from the user's actual claim, evidence, constraints, and alternatives. Investigate answerable facts yourself when tools and scope allow; do not turn research work into questions for the user.

Ask the highest-value unresolved question, explain why it matters, and let the user answer before adding a new branch. If they request an asynchronous review, deliver the ranked objections together instead.

Use counterexamples, failure conditions, and opportunity cost. Challenge the reasoning without performing hostility or repeatedly relitigating a defensible choice.

Stop when the decision is supported at the requested risk level, a decisive uncertainty needs evidence, or the user asks to stop. Summarize what survived, what changed, and the remaining uncertainty; do not convert every discussion into a mandatory approval process.

# Smoke observations (not paired A/B results)

- Runtime smoke succeeded: exact requested model `gpt-6-astra`, effort `high`; CLI `turn.completed` supplied actual usage.
- Only observed model tool call read the selected stable `better-prompts/SKILL.md`. No network, external action, delegation or workspace mutation appeared in the raw trace.
- The resulting prompt allowed cleanup/recreation of task-owned disposable test fixtures while retaining approval for other data deletion. The original prompt said data deletion required explicit approval without that exception.
- This is an authorization-semantics ambiguity to review, not evidence of actual data deletion. Disposable fixtures describe recoverability; whether that also grants deletion permission must not be silently assumed.
- The smoke is excluded from paired efficacy/quality comparisons. Its time and token usage remain recorded as experiment setup overhead.
- The cases and rubric were not changed in response to this observation.

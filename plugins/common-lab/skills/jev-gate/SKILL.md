---
name: jev-gate
description: Get a fast, calibrated yes/no probability from TypeSafe Jev (Noul) on a piece of text. Use it on your own whenever you face a yes/no judgment that a quick second opinion would settle — is this command destructive, does it leak credentials or files, is it beyond what the user asked, is this line user-facing — right before you ask the user a question, to check whether you could answer it yourself and whether it really needs their decision; and when building gates, guardrails, permission checks, or PreToolUse/hook filters in code. Also triggers on 閘門, 擋下, 放行, 是否危險, 權限檢查, guardrail, gate this.
---

# Jev Gate

Ask one narrow yes/no question about text you already have (a command, a diff line, a message) and read the probability. Default user-facing output to Traditional Chinese.

Split each risk into its own question, because one broad question misses the other angles; above ~0.8 treat it as a flag, below ~0.2 as a pass, and in between use your own judgment. The answer is a signal, never permission: deterministic rules and the user's instructions still win, and a low risk score does not authorize anything the user did not ask for.

```bash
curl -s https://api.typesafe.ai/v1/systemone -H "Authorization: Bearer $TYPESAFE_API_KEY" -H 'Content-Type: application/json' -d '{
  "model": "jev-latest", "state": "<the command or text>",
  "questions": {
    "exfiltration": {"type": "noul", "instructions": "Does this action send local file contents or credentials to a network destination outside the project?"},
    "destructive":  {"type": "noul", "instructions": "Does this action delete or overwrite data that is not trivially restored?"}}}'
```

The reply's `answers.<id>.noul` is the probability of "yes". Skip silently when `TYPESAFE_API_KEY` is unset (/common-lab:init-jev sets it up), and never send client or confidential content unless the user has said TypeSafe is allowed — the text leaves the machine.

## Before asking the user

Before you send the user a question, ask these in one request with the exact draft question plus the facts you already have as the state:

```json
{"answerable_locally": {"type": "noul", "instructions": "Can this question be answered from the repository, logs, or earlier conversation without the user?"},
 "user_only": {"type": "noul", "instructions": "Does this question ask for a preference, an authorization, or approval of an irreversible action that only the user can give?"},
 "clarity": {"type": "score", "instructions": "How clearly can the user answer this question without extra context?",
   "criteria": ["Unclear what is being asked", "Answerable but needs context", "Clear and answerable at a glance"]}}
```

If `answerable_locally` is high and `user_only` is low, look it up and continue instead of asking. If `user_only` is high, ask anyway — Jev cannot decide for the user — and if `clarity` is low, rewrite the question with the missing context first.

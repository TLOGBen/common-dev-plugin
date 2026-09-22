---
name: is-truely-need-to-ask-user-jev
description: Before you ask the user anything, ask TypeSafe Jev whether the question truly needs the user or whether you could find the answer yourself. Use every time you are about to ask the user a question, request a choice, or wait for their input.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Is it truly a question for the user? (Jev)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Right before you ask, send Jev the exact draft question plus the facts you already have.

```bash
curl -s https://api.typesafe.ai/v1/systemone -H "Authorization: Bearer $TYPESAFE_API_KEY" -H 'Content-Type: application/json' -d '{
  "model": "jev-latest", "state": "<draft question + known facts>",
  "questions": {
    "need_user": {"type": "noul", "instructions": "Does this question truly need the user — a preference, an authorization, approval of an irreversible action, or information only the user has?"},
    "answerable_locally": {"type": "noul", "instructions": "Could the agent answer this itself from the repository, logs, documentation, or earlier conversation?"}}}'
```

If `answerable_locally` is high and `need_user` is not, do not ask: look it up and continue. Otherwise ask. A preference, an authorization, or an irreversible action always goes to the user, whatever the scores — Jev never decides for them. Default user-facing output to Traditional Chinese.

Skip the check silently when `TYPESAFE_API_KEY` is unset, and do not send client or confidential content unless the user has said TypeSafe is allowed.

Tested (one run each): "npm test or pnpm test?" with pnpm-lock.yaml in the repo scored need_user 0.45 / answerable_locally 0.80; "the migration drops a table holding 3 years of records — proceed?" scored 0.96 / 0.24.

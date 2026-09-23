---
name: is-truely-need-to-ask-user-jev
description: Before you ask the user anything, ask TypeSafe Jev whether the question truly needs the user or whether you could find the answer — or do the thing — yourself. Use every time you are about to ask the user a question, request a choice, ask them to do something for you (start a service, run a command, check a page), or wait for their input.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# Is it truly a question for the user? (Jev)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Right before you ask, send Jev only facts, in separate labelled fields: the exact draft question or request, what you already tried toward it with each result (commands and their output; write `none` if nothing), and the other facts you have. Keep the questions below as written — you are the interested party, and rewording moves the probabilities.

```bash
curl -s https://api.typesafe.ai/v1/systemone -H "Authorization: Bearer $TYPESAFE_API_KEY" -H 'Content-Type: application/json' -d '{
  "model": "jev-latest", "state": "<draft question / attempts so far with results / known facts>",
  "questions": {
    "need_user": {"type": "noul", "instructions": "Does this question truly need the user — a preference, an authorization, approval of an irreversible action, or information only the user has?"},
    "answerable_locally": {"type": "noul", "instructions": "Could the agent answer this itself from the repository, logs, documentation, or earlier conversation?"},
    "agent_can_do": {"type": "noul", "instructions": "Is this something the agent could do itself with the tools it has — run, start, install, retry, look up — rather than something only the user can do?"},
    "tried_and_blocked": {"type": "noul", "instructions": "Do the attempts listed show the agent actually tried this and was blocked by something outside its reach?"}}}'
```

Do not ask when `need_user` is not high and either `answerable_locally` is high (look it up and continue) or `agent_can_do` is high and `tried_and_blocked` is low (do it yourself, then continue). Otherwise ask. A preference, an authorization, or an irreversible action always goes to the user, whatever the scores — and so does anything with side effects outside the local workspace, such as a shared or production service or a paid resource. Jev never decides for them. Default user-facing output to Traditional Chinese.

Skip the check silently when `TYPESAFE_API_KEY` is unset ($init-jev) or the call fails, and ask as you would have.

Tested (one run each): "npm test or pnpm test?" with pnpm-lock.yaml in the repo scored need_user 0.45 / answerable_locally 0.80; "the migration drops a table holding 3 years of records — proceed?" scored 0.96 / 0.24. `agent_can_do` and `tried_and_blocked` come from a field report — asking the user to start a local service had scored 0.09 on an ad-hoc "proven it cannot be done automatically?", and the service could in fact be started by the agent — and are not yet tested as worded.

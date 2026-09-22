---
name: none-stop-jever
description: Before you stop or end a turn, ask TypeSafe Jev whether you really can — is the user's request actually done, and is there work left you can do without them? Use every time you are about to stop, hand back, or end your turn while working on a user's request.
---

# None-stop (Jev)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Right before you stop, ask Jev. State only facts: the user's request in their words, what you did with its evidence (commands and their results), what is unfinished, and why you want to stop.

```bash
curl -s https://api.typesafe.ai/v1/systemone -H "Authorization: Bearer $TYPESAFE_API_KEY" -H 'Content-Type: application/json' -d '{
  "model": "jev-latest", "state": "<request / done with evidence / unfinished / reason for stopping>",
  "questions": {
    "request_done": {"type": "noul", "instructions": "Has the user'"'"'s request been fully done, with evidence that it works?"},
    "can_continue_alone": {"type": "noul", "instructions": "Is there remaining work toward the request that the agent can do now without the user?"}}}'
```

If `request_done` is low and `can_continue_alone` is high, do not stop: do the next piece of work. Otherwise stop, and say plainly what is done and what is not. Default user-facing output to Traditional Chinese.

The user's instruction always wins — if they told you to stop, stop. Skip the check silently when `TYPESAFE_API_KEY` is unset, and do not send client or confidential content unless the user has said TypeSafe is allowed.

Tested (one run each): "fixed the checkout test, full suite not run yet" scored request_done 0.09 / can_continue_alone 0.94; "full suite 214 passed, nothing unfinished" scored 0.92 / 0.06.

---
name: wayfinder-jever
description: Lab overlay on common:wayfinder that adds TypeSafe Jev readings — which grilling questions are worth asking and in what order of impact, whether a drained ticket actually needs the human, whether a question is sharp enough to be a ticket or stays fog, which open tickets a new decision pushed out of scope or invalidated, whether text for the human reads plainly, where to hand off when the map is done, and — through suggest-jev — which skill each ticket should be worked with. Use when the user asks for wayfinder-jever or a Jev-assisted map; use wayfinder for ordinary maps.
---

# Wayfinder (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `/common:wayfinder` exactly as written: destination first, one ticket per session outside drain, the operator principle, fog of war, the absolute HITL boundary, and the tracker and renderer are unchanged. This overlay adds Jev readings at seven points. Each is a second opinion for the operator; the operator still decides, and the human still answers every HITL question. Default user-facing output to Traditional Chinese.

Every call is `POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (init-jev) or a call fails, skip the reading and run wayfinder as written. Build every state from the map and ticket files (question text verbatim, Destination verbatim), and keep the questions as written.

## 1. Grilling: worth asking, then in what order (every round)

Grilling asks the whole frontier each round. Before presenting a round, ask for each candidate question — state: the decision being grilled, known facts, and the question:

```json
{"lookup": {"type": "noul", "instructions": "Could this be answered by looking at the repository, documentation, or known facts, without asking the user?"},
 "changes_design": {"type": "noul", "instructions": "Would different answers to this question lead to a meaningfully different design?"},
 "impact": {"type": "score", "instructions": "How much of the design depends on the answer to this question?",
   "criteria": ["Almost nothing; a cosmetic or reversible detail", "A local choice in one part", "Several parts of the design", "The overall architecture or scope"]}}
```

- `lookup` above ~0.7 → do not ask; find the fact yourself (grilling already says facts are your job) and ask only what depends on it later.
- `changes_design` below ~0.3 → drop it, or state your recommendation as an assumption in the recap instead of asking.
- Number the remaining questions by `impact`, highest first, so Q1 is the one the design hangs on most. Keep grilling's own rule: a question whose answer depends on another open question still waits for a later round, whatever its score.

Tested (one run each) on an expense-app design: "which Node.js version" (with `.nvmrc` known) scored lookup 0.98; "green or blue button" scored changes_design 0.15 and impact 0.01; "PostgreSQL or SQLite" scored 0.79 / 2.28 and "approval in the app or outside" 0.88 / 2.43, so approval came first. A single combined "worth asking" question misranked the button above the database — keep the two questions separate.

## 2. Drain: does this ticket need the human (before claiming)

In drain mode, before claiming each AFK ticket, state its Question and the Destination and ask:

```json
{"needs_human": {"type": "noul", "instructions": "Does resolving this question require the human's own preference, judgment, or approval, rather than facts the agent can find?"}}
```

Above ~0.5, do not drain it: leave it unclaimed for the human, and mention in the stop report that its `Type:` may be wrong. This reading can only hold a ticket back — it never turns a HITL ticket into AFK. Tested: "what import formats does Xero accept" scored 0.05; "should receipts be optional below a threshold, and what threshold" scored 0.91.

## 3. Fog or ticket (charting step 4, resolving step 5)

For each candidate you might ticket or graduate from Not yet specified, state it with the Destination and ask:

```json
{"precise": {"type": "noul", "instructions": "Is this question stated precisely enough that a session could start resolving it, even if it cannot be answered yet?"}}
```

Below ~0.3, keep it in the fog. Above ~0.7, ticket it. In between, apply wayfinder's own test yourself. Tested: a sharp Xero-format question scored 0.51, a vague "something about reporting later" scored 0.20 — useful for catching fog, not decisive for sharp questions.

## 4. After each resolution: out of scope or invalidated

Right after recording a resolution, for every open ticket, state the Destination, the new decision's one-line gist, and that ticket's Question, and ask:

```json
{"beyond_destination": {"type": "noul", "instructions": "Does this ticket's question sit beyond the destination, outside this effort's scope?"},
 "invalidated": {"type": "noul", "instructions": "Does the new decision make this ticket's question moot or change what it needs to ask?"}}
```

Above ~0.7 on either, review that ticket and apply wayfinder's rules — rule it out of scope, update it, or delete it. The reading never closes a ticket by itself.

## 5. Before the human reads it

Before a grilling round, a ticket summary, or drain's final batch of HITL questions, state the text as the human will see it and ask:

```json
{"plain": {"type": "noul", "instructions": "Is this in plain language the user can follow without technical background?"},
 "main_blocker": {"type": "noul", "instructions": "Does this address the main thing blocking progress, rather than a side detail?"}}
```

Below ~0.5 on either, rewrite once in the Speak-plainly style — context first, terms explained in place — and send whichever version scored higher.

## 6. Handoff when the last decision closes

State the Destination, Decisions so far, and the remaining work, and ask:

```json
{"handoff": {"type": "choice", "instructions": "Now that the route is clear, where should this effort go next?",
  "criteria": {"ordinary_execution": "A short, known, one-step change",
               "strategic_advance": "A locked multi-transition objective with execution stall, live-state risk, or main-session saturation",
               "stay_in_wayfinder": "Direction is still unresolved"}}}
```

Use it as a second opinion next to wayfinder's own handoff rules; strategic-advance's admission gate still decides whether a campaign starts.

## 7. Which skill works this ticket — hand it to suggest-jev

Wayfinder's Ecosystem routing (which skill a grilling, research, prototype, or task ticket goes through — think, read, learn, contract, seal, hunt, review, and the rest) is decided by suggest-jev instead of by reading the list here. When you are about to resolve a ticket, or claim AFK tickets in drain:

1. If the map's Notes already pin a routing for this kind of ticket, follow it — wayfinder's pin rule keeps every session consistent.
2. Otherwise run suggest-jev's start routing with the ticket as the request: its Question verbatim, its `Type:`, the Destination, and the skills actually available in this session (detection first, as wayfinder requires). Use its `start_skill` (and any other skill above ~0.15) for this ticket, and its subagent suggestion when handing the body to delegate.
3. Record the chosen routing in Notes, as wayfinder asks, so later and parallel sessions follow it instead of re-deciding.

suggest-jev only picks the tool. Wayfinder's rules still bind: HITL tickets are answered by the human, grilling tickets still run grilling and domain-modeling, and acceptance of any returned evidence stays with the operator.

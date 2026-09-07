---
name: wayfinder
description: Plans a huge chunk of work — more than one agent session can hold — as a shared map of decision tickets. Trigger on "/wayfinder", "開圖", "chart the map", "wayfind this", "break the fog", or when the user hands over a large fuzzy effort too big for one session. Resolves tickets one at a time until the way to the destination is clear; use when a loose idea needs charting into decisions before anyone builds.
---

A loose idea has arrived — too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** of **decision tickets** — questions whose resolution is a decision, not slices of a build to execute — worked one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting — it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic — engineering work, course content, whatever fits the shape.

## Plan, don't do

Wayfinder is **planning** by default: each ticket resolves a decision, and the map is done when the way is clear — nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off. An effort can override this in its **Notes** — carrying execution into the map itself — but absent that, produce decisions, not deliverables.

## Conditional execution handoff

Invoking Wayfinder always starts in Wayfinder; never start a campaign merely because a map exists. When the final decision ticket closes and one route is clear, choose the handoff automatically:

- a short, known, one-step change returns to ordinary execution;
- an effort that satisfies `/common:strategic-advance`'s admission gate — a locked multi-transition objective plus execution stall, live-state risk, or main-session saturation — hands the resolved map and its Decisions-so-far to `/common:strategic-advance`;
- unresolved direction stays in Wayfinder.

When Strategic Advance opened the map, record `returnTo: strategic-advance` in Notes and return once the named decision is resolved. Strategic Advance may reopen Wayfinder only for a new decision that can change the main effort, dependency structure, authority, or pivot. This return marker and the two admission gates prevent recursive skill ping-pong.

## The operator principle

The session driving the map is the **operator** — god-view: judgment and intervention only. It holds the map, chooses tickets, talks to the human, and judges what comes back; it does not burn its own context on execution bodies. Whenever resolving a ticket involves substantial legwork — reading a pile of sources, a scan or test sweep, executing an AFK task, producing a sizable artifact — hand that slice to `/common:delegate` (its worth-it gate is the arbiter: slices it declines as too trivial come back inline). Sidekicks return **evidence**, never conclusions the operator must trust blindly; **acceptance never delegates** — the operator verifies the evidence against the ticket's question, records the resolution itself, and intervenes when a sidekick stalls or drifts. In drain mode this posture is the default: fan the AFK frontier out to sidekicks in parallel, and spend the operator's own tokens only on judging, map-wiring, and intervention.

## Refer by name

Every map and ticket has a **name** — its title. In everything the human reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and path don't vanish — a name wraps its link — but they ride _inside_ the name, never stand in for it.

## Ecosystem routing (optional)

Wayfinder is self-contained: its companion skills (`/common:grilling`, `/common:domain-modeling`, `/common:research`, `/common:prototype`) are always the default. But when the **baransu** skill suite is installed in the session, an effort MAY route ticket work through it — richer tools for the same slots:

- **Grilling** tickets whose question is a worth-it / existence judgment (值不值得、有沒有必要) or a design-approach choice → `/baransu:think` (a Kill/Keep/Pivot or A-or-B verdict, or an intent handoff sheet) alongside the grilling round — the human still answers; think structures the judgment.
- **Research** tickets that need sources captured or digested, not just facts → `/baransu:read` (offline capture) or `/baransu:learn` (structured brief); link the product from the ticket as an asset. When the findings deserve a human-readable rendering, `/baransu:book` turns them into a browser-ready artifact.
- **Prototype** tickets asking "how should it look" → `/baransu:design` can generate or lint the DESIGN.md the prototype variants should obey — spec first, throwaway variants second.
- **Task** tickets carrying execution: pin a medium slice with `/baransu:contract` and close it with `/baransu:seal` (drain mode does the same for AFK tasks it executes); a symptom-to-root-cause chase runs under `/baransu:hunt`.
- **Second opinions**: after a heavyweight resolution, `/baransu:review` gives an isolated cross-perspective check before the decision is recorded.
- **Session end**: a wayfinder session edits tracker files in the user's repo — `/baransu:ship` is the natural wrap-up (archive, commit, push) when the user wants the map's progress landed.
- **Beyond the map**: when the way is clear and the destination is a multi-module build, hand off by slicing the route into contract-banded pieces — `/baransu:contract` pins each slice and `/baransu:seal` closes it, with execution run per slice through `/common:delegate` or as a campaign under `/common:strategic-advance` — the map's Decisions-so-far becomes the handoff input.

Skills without a natural map slot (health, evolve, write, …) are not routed — forcing them in dilutes both toolkits. Two rules keep all of this optional: **detection first** — route only to skills actually available in the session, never assume; and **pin the choice** — record the routing in the map's **Notes** so every later session (and parallel session) follows the same routing instead of re-deciding it.

## Speak plainly

Whatever the human is asked to read or choose from — grilling rounds, option lists, ticket summaries, resolution recaps, map narration — deliver it the way `/common:wait-what` re-pitches an explanation: plain Traditional Chinese by default, or another language only when the user explicitly requests it, with context first. Before any question or option list, spell out in ordinary words where this decision sits on the route, why it matters now, and what hangs on it; explain any technical term in place the moment it appears. Never hand the human a bare option list and expect them to reconstruct the background themselves.

The HTML renderer defaults its interface chrome to `--language zh-TW` and also supports `--language en`. When the user explicitly selects English, record that choice in the map Notes and pass it on every later render. For another explicit prose language, author the map and ticket content in that language and keep the deterministic chrome at its Traditional Chinese default.

## The Map

The map lives as local markdown in the user's project — the canonical artifact. Its tickets are child files of the map. **How the map, its child tickets, blocking, frontier queries, and the HTML view are physically expressed is defined in [TRACKER.md](${CLAUDE_PLUGIN_ROOT}/skills/wayfinder/TRACKER.md)** — consult its "Wayfinding operations" section for every tracker action.

The map is an **index**, not a store. It lists the decisions made and points at the tickets that hold their detail; a decision lives in exactly one place — its ticket — so the map never restates it, only gists it and links.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are **not** listed — they are open child tickets, found by scanning.

```markdown
## Destination

<what reaching the end of this map looks like — the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index — one line per closed ticket: enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [<closed ticket title>](link) — <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a **child file** of the map; its file id is its identity. Its body is the question, sized to one 100K token agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

Each ticket carries a type — one of `research`, `prototype`, `grilling`, `task` (see [Ticket Types](#ticket-types)).

A session **claims** a ticket **first**, before any work, so concurrent sessions skip it (see TRACKER.md for the claim mechanics).

A ticket is **unblocked** when every ticket blocking it is closed; the **frontier** is the open, unblocked, unclaimed children — the edge of the known. Blocking edges and the frontier are also rendered visually in the map's HTML view, so the human sees what's takeable without opening the map.

The answer isn't part of the body — it's recorded on resolution (see [Work through the map](#work-through-the-map)). Assets created while resolving a ticket are linked from the ticket, not pasted in.

## Ticket Types

Every ticket is either **HITL** — human in the loop, worked _with_ a human who speaks for themselves — or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).

- **Research** (AFK): Reading documentation, third-party APIs, or local resources like knowledge bases to surface a fact a decision waits on. Resolved by a `/common:research` **subagent**. Use when knowledge outside the current working directory is required.
- **Prototype** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to — an outline, a rough take, a stub, or UI/logic code via the `/common:prototype` skill. Links the prototype as an asset. Use when "how should it look" or "how should it behave" is the key question.
- **Grilling** (HITL): Conversation. The default case. Always invoke the `/common:grilling` and `/common:domain-modeling` skills.
- **Task** (HITL or AFK): Manual work that must happen before a _decision_ can be made — nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that _does_ rather than decides — and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.

## Fog of war

The map is _deliberately_ incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war** — the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets — one at a time, until the way to the destination is clear and no tickets remain.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier _toward_ the destination — everything here is in scope, just not sharp enough to ticket. Write as loosely or as fully as the view allows; it doubles as a signpost for collaborators reading where the effort is headed.

**Fog or ticket?** The test is whether you can state the question precisely now — _not_ whether you can answer it now.

- **Ticket when** the question is already sharp — even if it's blocked and you can't act on it yet.
- **Not yet specified when** you can't yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces: it's coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

**Not yet specified** excludes what's already decided (Decisions so far), what's already a live ticket, and what's out of scope (the next section).

## Out of scope

Fog only ever gathers _toward_ the destination. The destination fixes the scope, so work beyond it is **out of scope** — it isn't fog, and it doesn't belong in **Not yet specified**. It gets its own **Out of scope** section on the map: work you've consciously ruled out of _this_ effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates — the frontier stops at the destination — so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination — mis-scoped in while charting, or exposed by a resolution — **close it** (a closed ticket is unambiguously off the frontier) and leave one line in the **Out of scope** section: the gist plus why it's out of scope, linking the closed ticket. It stays out of **Decisions so far**, which records the route actually walked — a scope boundary isn't a step on it.

## Invocation

Three modes. In Chart and Work modes, **never resolve more than one ticket per session** — with the exception of research tickets. Drain mode may resolve any number of **AFK** tickets in one session, but never touches a HITL one.

### Chart the map

User invokes with a loose idea.

1. **Name the destination.** Run a `/common:grilling` and `/common:domain-modeling` session to pin down what this map is finding its way to — the spec, decision, or change. The destination fixes the scope, so it's settled first.
2. **Map the frontier.** Grill again, **breadth-first** this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog** — the way to the destination is already clear, the whole journey small enough for one session — you don't need a map. Stop and ask the user how they'd like to proceed.
3. **Create the map**: Destination and Notes filled in, Decisions-so-far empty, the fog sketched into **Not yet specified**.
4. **Create the tickets you can specify now** as child files of the map — then wire blocking edges in a **second pass** (tickets need ids before they can reference each other). Wiring sorts them into the frontier and the blocked; everything you can't yet specify stays in the fog — the **Not yet specified** section.
5. **Fire the research subagents.** For each `research` ticket you just created, spin up a `/common:research` subagent to resolve it in parallel, with a context pointer from the ticket to wherever its findings land.
6. **Render the HTML view** (see TRACKER.md), then stop — charting is one session's work; it hand-resolves nothing.

### Work through the map

User invokes with a map (path or effort name). A ticket is **optional** — without one, you pick the next decision, not the user.

1. Load the **map** — the low-res view, not every ticket body.
2. Choose the ticket. If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it** before any work.
3. Resolve it — **zoom as needed**: fetch the full body of any related or closed ticket on demand; invoke the skills the `## Notes` block names. If in doubt, use `/common:grilling` and `/common:domain-modeling`.
4. Record the resolution: append the answer to the ticket, **close** it, and **append a context pointer** to the map's Decisions-so-far.
5. Add newly-surfaced tickets (create-then-wire); graduate any fog the answer has made specifiable, clearing each graduated patch from **Not yet specified** so it lives only as its new ticket. If the answer reveals a ticket — this one or another — sits beyond the destination, **rule it out of scope** rather than resolving it on the route. If the decision invalidates other parts of the map, update or delete those tickets.
6. **Re-render the HTML view** so it reflects the new state of the map.

The user may run unblocked tickets in parallel, so expect other sessions to be editing the tracker concurrently.

### Drain the frontier

User invokes with a map and asks to auto-advance (「drain」、「自動推進」, "drain the map"). Autopilot for everything that does not need the human; a hard stop at everything that does.

1. Load the map and compute the frontier.
2. **Claim every AFK ticket on the frontier** — `research` tickets, and `task` tickets the agent can drive alone (honouring the map's Notes). HITL tickets are left unclaimed and untouched.
3. Resolve the claimed tickets **in parallel** per the [operator principle](#the-operator-principle): each ticket body goes to `/common:delegate` (research bodies may also run as `/common:research` subagents; slices delegate declines run as plain subagents). The operator itself executes nothing — it judges the returned evidence, accepts or rejects, and intervenes on stalls.
4. Record each resolution (answer, close, Decisions-so-far pointer), graduate fog, create-then-wire any new tickets, re-render the HTML view (`--no-open` for intermediate renders).
5. Recompute the frontier and repeat from step 2 — newly unblocked AFK tickets keep draining.
6. Stop when the frontier holds only HITL tickets (or nothing). **The HITL boundary is absolute**: never answer a grilling question, stand in for a prototype reaction, or fabricate the human's side of a decision — a drained map full of self-answered decisions is worthless. On stopping, re-render the view with the browser open, then present every remaining frontier ticket's question in one batch, plain-language context first (see [Speak plainly](#speak-plainly)), so the human can settle several decisions in a single reply — and record each answered ticket as its own resolution.

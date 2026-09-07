---
name: wayfinder
description: Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets in local markdown, and resolve them one at a time until the way to the destination is clear. Trigger on "/wayfinder", 「開圖」, "chart the map", "break the fog".
disable-model-invocation: true
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.2.0-codex
---

## Lab Resource Resolution

Before reading a bundled reference or running a bundled script, resolve the absolute directory containing this loaded SKILL.md as LAB_SKILL_DIR. Verify that its frontmatter name is wayfinder. Use the resulting absolute path in file tools; for shell examples, bind LAB_SKILL_DIR to that verified path in the same shell invocation. This variable is not preconfigured by Codex. Never guess an install-cache path or use the working directory as the skill root. If this entrypoint or a referenced resource cannot be read, stop that operation with SKILL_RESOURCE_MISSING and report the missing path.



A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** of local markdown files, then works its **decision tickets** (questions whose resolution is a decision, not slices of a build to execute) one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting: it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic: engineering work, course content, whatever fits the shape.

Default user-facing prose and map contents to Traditional Chinese unless the user explicitly requests another language; keep code, identifiers, and established project terminology as they are.

## Plan, don't do

Wayfinder is **planning** by default: each ticket resolves a decision, and the map is done when the way is clear, with nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off. An effort can override this in its **Notes**, carrying execution into the map itself, but absent that, produce decisions, not deliverables.

## Refer by name

Every map and ticket is a file, so it has a **name**: its title. In everything the human reads (narration, the map's Decisions-so-far), refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and path don't vanish; a name wraps its link, but they ride _inside_ the name, never stand in for it.

## Make the route legible

The map exists so a person can follow the road, not only reach the end of it. Whatever the human is asked to read or choose from (a grilling round, an option list, a ticket summary, a resolution recap, the map narration), give it context first, in plain words: where this decision sits on the route, why it comes up now, and what hangs on it. Explain a technical term in place the moment it appears. Never hand over a bare option list and expect the human to reconstruct the background. When the map advances, show what became clearer and what the next meaningful decision is, so the person can see the questions asked and how each was resolved, not only the destination.

## The Map

The map is a single `map.md` file, the canonical artifact. Its tickets are one file each beside it.

The map is an **index**, not a store. It lists the decisions made and points at the tickets that hold their detail; a decision lives in exactly one place, its ticket, so the map never restates it, only gists it and links.

**Where the map, its child tickets, blocking, and frontier queries physically live is defined by the tracker doc** at `${LAB_SKILL_DIR}/../skills/wayfinder/references/tracker.md`. Read its "Wayfinding operations" and "HTML view" sections before touching any file.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are **not** listed: they are open ticket files, found by scanning the issues directory.

```markdown
## Destination

<what reaching the end of this map looks like: the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a file under the effort's `issues/` directory; its number is its identity. Its body is the question, sized to one 100K token agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

Each ticket carries a `Type:` line, one of `research`, `prototype`, `grilling`, `task` (see [Ticket Types](#ticket-types)).

A session **claims** a ticket by setting `Status: claimed`, **first**, before any work, so concurrent sessions skip it. That status _is_ the claim: an open ticket without it is unclaimed.

Blocking is a `Blocked by:` line near the top of the ticket. The bundled HTML view renders the frontier _visually_ from those lines, so the human sees what's takeable without opening the map. A ticket is **unblocked** when every ticket blocking it is closed; the **frontier** is the open, unblocked, unclaimed children, the edge of the known.

The answer isn't part of the body; it's recorded on resolution (see [Work through the map](#work-through-the-map)). Assets created while resolving a ticket are linked from the ticket, not pasted in.

## Ticket Types

Every ticket is either **HITL** (human in the loop, worked _with_ a human who speaks for themselves) or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).

- **Research** (AFK): Reading documentation, third-party APIs, or local resources like knowledge bases to surface a fact a decision waits on. Resolved by a subagent that calls the Skill tool with "research". Use when knowledge outside the current working directory is required.
- **Prototype** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to (an outline, a rough take, a stub, or UI/logic code) by calling the Skill tool with "prototype". Links the prototype as an asset. Use when "how should it look" or "how should it behave" is the key question.
- **Grilling** (HITL): Conversation. The default case. Always call the Skill tool twice, for "grilling" and "domain-modeling".
- **Task** (HITL or AFK): Manual work that must happen before a _decision_ can be made: nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that _does_ rather than decides, and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.

## Fog of war

The map is _deliberately_ incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war**: the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets, one at a time, until the way to the destination is clear and no tickets remain.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier _toward_ the destination: everything here is in scope, just not sharp enough to ticket. Write as loosely or as fully as the view allows; it doubles as a signpost for collaborators reading where the effort is headed.

**Fog or ticket?** The test is whether you can state the question precisely now, _not_ whether you can answer it now.

- **Ticket when** the question is already sharp, even if it's blocked and you can't act on it yet.
- **Not yet specified when** you can't yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces: it's coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

**Not yet specified** excludes what's already decided (Decisions so far), what's already a live ticket, and what's out of scope (the next section).

## Out of scope

Fog only ever gathers _toward_ the destination. The destination fixes the scope, so work beyond it is **out of scope**: it isn't fog, and it doesn't belong in **Not yet specified**. It gets its own **Out of scope** section on the map: work you've consciously ruled out of _this_ effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates (the frontier stops at the destination), so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination (mis-scoped in while charting, or exposed by a resolution), **close it** (a closed ticket is unambiguously off the frontier) and leave one line in the **Out of scope** section: the gist plus why it's out of scope, linking the closed ticket. It stays out of **Decisions so far**, which records the route actually walked; a scope boundary isn't a step on it.

## Invocation

Three modes. In Chart and Work modes, **never resolve more than one ticket per session**, with the exception of research tickets. Drain mode may resolve any number of **AFK** tickets in one session, but never touches a HITL one.

### Chart the map

User invokes with a loose idea.

1. **Name the destination.** Call the Skill tool twice, for "grilling" and "domain-modeling", to pin down what this map is finding its way to: the spec, decision, or change. The destination fixes the scope, so it's settled first.
2. **Map the frontier.** Grill again, **breadth-first** this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog** (the way to the destination is already clear, the whole journey small enough for one session), you don't need a map. Stop and ask the user how they'd like to proceed.
3. **Create the map** (`map.md`): Destination and Notes filled in, Decisions-so-far empty, the fog sketched into **Not yet specified**.
4. **Create the tickets you can specify now** as ticket files, then wire `Blocked by` edges in a **second pass** (tickets need numbers before they can reference each other). Wiring sorts them into the frontier and the blocked; everything you can't yet specify stays in the fog: the **Not yet specified** section.
5. **Fire the research subagents.** For each `research` ticket you just created, spin up a subagent that calls the Skill tool with "research" to resolve it in parallel, capturing its findings under the effort's `research/` directory with a context pointer from the ticket.
6. Render the HTML view and open it for the user (see the tracker doc).
7. Stop: charting is one session's work; it hand-resolves nothing.

### Work through the map

User invokes with a map (effort slug or path). A ticket is **optional**: without one, you pick the next decision, not the user.

1. Load the **map**: the low-res view, not every ticket body.
2. Choose the ticket. If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it**: set `Status: claimed` before any work.
3. Resolve it. **Zoom as needed**: fetch the full body of any related or closed ticket on demand; call the Skill tool for whichever skills the `## Notes` block names. If in doubt, call the Skill tool twice, for "grilling" and "domain-modeling".
4. Record the resolution: append the answer under `## Answer`, set `Status: resolved`, and **append a context pointer** to the map's Decisions-so-far.
5. Add newly-surfaced tickets (create-then-wire); graduate any fog the answer has made specifiable, clearing each graduated patch from **Not yet specified** so it lives only as its new ticket. If the answer reveals that a ticket (this one or another) sits beyond the destination, **rule it out of scope** rather than resolving it on the route. If the decision invalidates other parts of the map, update or delete those tickets.
6. Render the HTML view and open it for the user.

The user may run unblocked tickets in parallel, so expect other sessions to be editing the files concurrently.

### Drain the frontier

User invokes with a map and asks to auto-advance (「drain」、「自動推進」, "drain the map"). Autopilot for everything that does not need the human; a hard stop at everything that does.

1. Load the map and compute the frontier.
2. **Claim every AFK ticket on the frontier**: `research` tickets, and `task` tickets the agent can drive alone (honouring the map's Notes). HITL tickets are left unclaimed and untouched.
3. Resolve the claimed tickets **in parallel**, each in its own subagent (research bodies call the Skill tool with "research"; task bodies may go through delegate when it is available). The driving session executes nothing itself: it judges the returned evidence, accepts or rejects, and intervenes on stalls.
4. Record each resolution (answer, resolve, Decisions-so-far pointer), graduate fog, create-then-wire any new tickets, re-render the HTML view (`--no-open` for intermediate renders).
5. Recompute the frontier and repeat from step 2: newly unblocked AFK tickets keep draining.
6. Stop when the frontier holds only HITL tickets (or nothing). **The HITL boundary is absolute**: never answer a grilling question, stand in for a prototype reaction, or fabricate the human's side of a decision; a drained map full of self-answered decisions is worthless. On stopping, re-render the view with the browser open, then present every remaining frontier ticket's question in one batch, context first (see [Make the route legible](#make-the-route-legible)), so the human can settle several decisions in a single reply, and record each answered ticket as its own resolution.

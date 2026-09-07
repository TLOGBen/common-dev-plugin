# Tracker: Local Markdown

The tracker doc this skill's "The Map" section points at. It describes how the map, its tickets, blocking, and the frontier are expressed as files, and how the bundled HTML view is rendered.

Wayfinder maps and tickets live as markdown files in the user's project under `.common-lab/wayfinder/`.

## Conventions

- One effort per directory: `.common-lab/wayfinder/<effort-slug>/`
- The map is `.common-lab/wayfinder/<effort-slug>/map.md`
- Tickets are one file per ticket at `.common-lab/wayfinder/<effort-slug>/issues/<NN>-<slug>.md`, numbered from `01` — never a single combined tickets file
- Comments and conversation history append to the bottom of a ticket under a `## Comments` heading
- Assets produced while resolving a ticket (research findings, prototypes) go under the effort directory (e.g. `research/`, `prototypes/`) and are linked from the ticket

## Wayfinding operations

- **Map**: `.common-lab/wayfinder/<effort>/map.md` — the Destination / Notes / Decisions-so-far / Not-yet-specified / Out-of-scope body.
- **Child ticket**: `.common-lab/wayfinder/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `open`/`claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.common-lab/wayfinder/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.

## HTML view

After any change to the map or its tickets, regenerate the view by running the bundled renderer:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/wayfinder/scripts/render_map.py .common-lab/wayfinder/<effort> [--language zh-TW|en]
```

It parses `map.md` + `issues/` and fills the bundled template at `${CLAUDE_PLUGIN_ROOT}/skills/wayfinder/assets/map-template.html`, writing a single self-contained `map.html` (inline CSS/JS, no external resources) — then **opens it in the user's browser by default** (pass `--no-open` to suppress, e.g. for intermediate renders in a batch of edits; the final render of a session should open). Interface chrome defaults to Traditional Chinese; pass `--language en` only when the user explicitly requests English, and repeat the choice on later renders. The view shows the destination, an interactive blocking graph, a filterable ticket board with the frontier visually distinct, and the map's Decisions / Not-yet-specified / Out-of-scope sections. Never hand-edit `map.html` — edit the markdown and re-render.

The stdlib-only renderer rejects duplicate ticket IDs and blocking cycles before writing output, escapes ticket metadata before browser insertion, and replaces the output atomically so a pre-existing final symlink cannot redirect the write. These checks are input-integrity boundaries, not optional visual behavior.

**The renderer guards itself.** `validate_tickets` refuses ambiguous identities and blocking cycles before the HTML template sees them; the template escapes every ticket value that enters `innerHTML`, and the writer atomically replaces the final path. A map that would render with missing, overwritten or executable ticket metadata is rejected or kept inert rather than presented as complete.

### Current focus (optional)

When one real human choice should lead the handoff, add a `## Current focus` section to `map.md` with only that existing ticket ID on the next line. It is a view pointer, not a decision, status, or authorization: the renderer shows that ticket's question and body first, with the full map expandable and the ticket linked. An unknown, resolved, or blocked focus ID produces a warning and leaves the full map open; the renderer never substitutes another ticket. Omit the section when no human choice needs focus.

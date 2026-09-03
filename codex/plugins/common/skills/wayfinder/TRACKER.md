# Tracker: Local Markdown

Wayfinder maps and tickets live as markdown files in the user's project under `.claude/wayfinder/`.

## Conventions

- One effort per directory: `.claude/wayfinder/<effort-slug>/`
- The map is `.claude/wayfinder/<effort-slug>/map.md`
- Tickets are one file per ticket at `.claude/wayfinder/<effort-slug>/issues/<NN>-<slug>.md`, numbered from `01` — never a single combined tickets file
- Comments and conversation history append to the bottom of a ticket under a `## Comments` heading
- Assets produced while resolving a ticket (research findings, prototypes) go under the effort directory (e.g. `research/`, `prototypes/`) and are linked from the ticket

## Wayfinding operations

- **Map**: `.claude/wayfinder/<effort>/map.md` — the Destination / Notes / Decisions-so-far / Not-yet-specified / Out-of-scope body.
- **Child ticket**: `.claude/wayfinder/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `open`/`claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.claude/wayfinder/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.

## HTML view

After any change to the map or its tickets, regenerate the view by running the bundled renderer:

```bash
python3 <this skill directory>/scripts/render_map.py .claude/wayfinder/<effort> [--language zh-TW|en]
```

It parses `map.md` + `issues/` and fills the bundled template at `<this skill directory>/assets/map-template.html`, writing a single self-contained `map.html` (inline CSS/JS, no external resources) — then **opens it in the user's browser by default** (pass `--no-open` to suppress, e.g. for intermediate renders in a batch of edits; the final render of a session should open). Interface chrome defaults to Traditional Chinese; pass `--language en` only when the user explicitly requests English, and repeat the choice on later renders. The view shows the destination, an interactive blocking graph, a filterable ticket board with the frontier visually distinct, and the map's Decisions / Not-yet-specified / Out-of-scope sections. Never hand-edit `map.html` — edit the markdown and re-render.

The stdlib-only renderer rejects duplicate ticket IDs and blocking cycles before writing output, escapes ticket metadata before browser insertion, and replaces the output atomically so a pre-existing final symlink cannot redirect the write. These checks are input-integrity boundaries, not optional visual behavior.

**The renderer guards itself.** `validate_tickets` refuses ambiguous identities and blocking cycles before the HTML template sees them; the template escapes every ticket value that enters `innerHTML`, and the writer atomically replaces the final path. A map that would render with missing, overwritten or executable ticket metadata is rejected or kept inert rather than presented as complete.

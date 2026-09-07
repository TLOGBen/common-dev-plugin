# Durable map

Use .common-lab/wayfinder/<effort>/map.md and issues/NN-<slug>.md.
The map has Destination, Decisions-so-far, Not-yet-specified, and Out-of-scope sections.

Each ticket records a question, Type: research|prototype|grilling|task, Status: open|claimed|resolved, and Blocked by: NN, NN when needed. Put the human-decision boundary in the question or body; the renderer's existing type vocabulary is unchanged.

Claim a ticket before assigning concurrent work. Resolve only after an evidence-backed answer or the user's actual decision; record it under ## Answer and add its pointer to the map. Append material follow-up under ## Comments. Never invent agreement.

The frontier consists of open tickets whose dependencies are resolved. Choose the one most useful to current understanding, not simply the lowest number. Preserve stable IDs when priorities change.

Render with:

    python3 ${LAB_SKILL_DIR}/scripts/render_map.py .common-lab/wayfinder/<effort> --no-open

Remove --no-open when showing the view to the user is useful; interface defaults to zh-TW. Use --language en only when requested. Edit Markdown, not the generated map.html.

The bundled renderer rejects duplicate IDs and dependency cycles, escapes metadata, and atomically replaces its output. Those integrity checks are retained from the stable implementation. Existing user-state stewardship rules still apply to replacing an existing output.

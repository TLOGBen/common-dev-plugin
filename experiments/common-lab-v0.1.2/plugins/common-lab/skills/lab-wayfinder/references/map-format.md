# Durable map

Use .common-lab/wayfinder/<effort>/map.md and issues/NN-<slug>.md.
Use these exact level-two headings; the renderer matches their spelling:

    ## Destination
    ## Decisions so far
    ## Not yet specified
    ## Out of scope

Use prose for Destination and top-level bullets for the other three sections.

Each ticket records a question, Type: research|prototype|grilling|task, Status: open|claimed|resolved, and Blocked by: NN, NN when needed. Put the human-decision boundary in the question or body; the renderer's existing type vocabulary is unchanged.

Make the question, supporting facts, options with their costs/consequences, and recommendation understandable in the existing ticket. Keep usable prose already in ## Question or the body; do not rewrite it into a form merely for display. Optional ## Evidence, ## Options, and ## Recommendation sections improve navigation when useful. They remain part of the same ticket, not a second acceptance record. Do not invent costs, evidence, or agreement.

Claim a ticket before assigning concurrent work. Resolve only after an evidence-backed answer or the user's actual decision; record it under ## Answer and add its pointer to the map. Append material follow-up under ## Comments. Never invent agreement.

The frontier consists of open tickets whose dependencies are resolved. Choose the one most useful to current understanding, not simply the lowest number. Preserve stable IDs when priorities change.

When one real human choice should lead the handoff, optionally add ## Current focus to map.md with only that existing ticket ID on the next line. This is a view pointer, not a decision, status, or authorization. The renderer shows that ticket's existing question and meaningful body first, with the full map expandable and the original ticket linked. Only genuinely empty content gets a missing-content message; absent optional headings do not imply absent evidence or options. Unknown, resolved, or dependency-blocked focus IDs produce a warning and leave the full map open; it never substitutes another ticket. Omit the section when no human choice needs focus; existing maps remain fully visible.

Render with:

    python3 ${LAB_SKILL_DIR}/scripts/render_map.py .common-lab/wayfinder/<effort> --no-open

Remove --no-open when showing the view to the user is useful; interface defaults to zh-TW. Use --language en only when requested. Edit Markdown, not the generated map.html.

The bundled renderer rejects duplicate IDs and dependency cycles, escapes metadata, and atomically replaces its output. Those integrity checks are retained from the stable implementation. Existing user-state stewardship rules still apply to replacing an existing output.

---
name: ui-jever
description: Lab overlay on baransu:ui that adds TypeSafe Jev readings — screening the design plan for the generic AI-design defaults before building, scoring each built block's fit to the plan with a check for each default, and picking an element's layout primitive and palette role from the plan. Use when the user asks for ui-jever or a Jev-checked UI build; use $ui for ordinary UI work.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# UI (Jev overlay)

Use Jev to strengthen anywhere that only needs a judgment — yes/no, choose one, score.

Load and run `$ui` exactly as written; the design-lead stance, the plan → review → build → critique process, restraint, copy guidance, and the closing message are unchanged. This overlay adds Jev readings at three points. They read markup and CSS text, not pixels, so they complement the screenshot critique rather than replace it. The brief's own words always win: when the brief asks for one of the default looks, a high reading for that default is expected, not a flaw. Default user-facing output to Traditional Chinese.

## Calling Jev

`POST https://api.typesafe.ai/v1/systemone` with `{"model": "jev-latest", "state": "<facts>", "questions": {...}}` and `Authorization: Bearer $TYPESAFE_API_KEY`. If the key is unset (`$init-jev`) or the call fails, skip the reading and design as written. Keep the questions as written — the designer grading their own work is an interested party.

The five default checks, reused below (all Noul):

```json
{"tell_cream_serif":  {"type": "noul", "instructions": "Does this use a warm cream background with a high-contrast serif display and a terracotta or warm-clay accent?"},
 "tell_dark_acid":    {"type": "noul", "instructions": "Does this use a near-black background with a single bright acid-green or vermilion accent?"},
 "tell_broadsheet":   {"type": "noul", "instructions": "Does this use a broadsheet layout with hairline rules, zero border-radius, and dense newspaper-like columns?"},
 "tell_saas_cards":   {"type": "noul", "instructions": "Does this chop content into identical rounded cards with the same soft grey shadow, or use gradient washes as decoration?"},
 "tell_template_chrome": {"type": "noul", "instructions": "Does this use template chrome: a tracked-out ALL-CAPS eyebrow label above headings, middle-dot meta strings, 'WORD — fragment' labels, tinted near-black standing in for black, monospace data labels, or an arrow appended to link or button text?"}}
```

## 1. Screen the plan (after the plan, before building)

State: the design plan exactly as shown to the user — palette hexes and names, type roles, layout concept, principles — plus the brief. Ask the five default checks. Any check above ~0.7 on an axis the brief left free is a part of the plan to revise in the ui skill's review pass; say which part you changed and why.

## 2. Block fit (while building and in the critique pass)

For each meaningful block — a section, a component, a repeated pattern — state the plan and the block's markup with its effective CSS, and ask the five default checks plus:

```json
{"fit": {"type": "score", "instructions": "How faithfully does this block follow the design plan (palette, type roles, layout concept, principles)?",
  "criteria": ["Contradicts the plan", "Partly follows it with clear departures", "Follows it with minor departures", "Follows it faithfully"]}}
```

Revise blocks with `fit` below ~1.5 or a default check above ~0.7, then re-check once. Keep the ui skill's restraint rule in view: a block that fits the plan but adds decoration the brief does not need is still a candidate to cut.

Tested against a field-guide plan (one run each): a hero with an ALL-CAPS eyebrow, identical shadowed rounded cards, and "Learn more →" scored fit 0.23 with saas-cards 0.95 and template-chrome 0.90; a specimen block using the plan's grid, typefaces, and single rust accent scored fit 2.25 with both checks at 0.01–0.02.

## 3. Element choices (while building)

When an element's layout or color is not settled by the plan, state the plan, the element's role, and its content, and ask:

```json
{"layout": {"type": "choice", "instructions": "Which layout primitive fits this element's content and role?",
  "criteria": {"flow": "Normal document flow; text and inline content", "stack": "A vertical stack with consistent spacing",
               "row": "A single row of items that may wrap (flex row)", "grid": "A two-dimensional arrangement or aligned columns (grid)",
               "overlay": "Layered on top of other content (absolute or fixed positioning)", "sticky": "Stays in view while its section scrolls"}},
 "color_role": {"type": "choice", "instructions": "Which palette color from the plan should this element use for its main color?",
  "criteria": {"<name1>": "<hex and role from the plan>", "<name2>": "<hex and role from the plan>", "none": "No palette color; inherit"}}}
```

Fill `color_role` with the plan's own named colors. The accent reserved for the one memorable element should come back rarely; if Jev picks it for ordinary elements, keep it where the plan put it. Watch CSS specificity yourself — whether selectors cancel each other out is a code question, not a Jev question.

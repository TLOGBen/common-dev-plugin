# contract-gate — criteria assertability rules (single implementation)

Owned by `$contract` (one-page contract, medium band), and therefore binding on
the large band too — a large effort is sliced into contract-band slices, each
pinned by its own contract. `$contract` reads THIS file for the rules below; it
does not restate them. Experiments 2026-07-19 (harness×model matrix + validation round)
showed these three rules structurally eliminate two whole defect classes
(off-by-one display fields; constant-retyping drift) — they are the quality
lever, not process weight.

## G1 — Criteria Assertability Gate

Every acceptance criterion MUST name an assertable value. For any criterion
about user-facing text (CLI output, TUI toast, error message):
substring-contains wording is FORBIDDEN — the criterion must either
(a) prescribe the EXACT output format with placeholders
(e.g. 「進度已遷移：{chapter_name}」, no other numeric field permitted), or
(b) carry an explicit prohibition list
(e.g. "the message MUST NOT contain any number derived from a chapter idx").

A criterion that a reviewer could not use to REJECT a defective implementation
is a spec bug — rewrite it before handoff.

## G2 — Trap-to-Criterion Promotion

Every hidden invariant or data-shape trap discovered while reading the code
(non-dense indexes, abort semantics, encoding quirks) MUST be promoted into
BOTH: (a) a prohibition-style criterion in the goal/criteria section, and
(b) a required pinning test named in the test plan. A warning sentence in
handoff prose alone is NON-COMPLIANT — warnings depend on the implementer's
memory; criteria empower rejection.

## G3 — Verbatim Constants Block

Collect every fixed algorithm string given by the requirements (regexes, format
strings, character classes, magic literals) into a fenced block titled
`## Verbatim Constants`. The implementer MUST copy-paste from this block, never
retype. The final reviewer MUST byte-diff each constant in the implementation
against this block.

## G4 — User-Facing Surface Inventory

Enumerate EVERY user-facing output surface the change touches (each CLI
println, each TUI toast, each error path) in a table:
surface → exact format (per G1) → impact（資產 → 一句後果｜類別）→ pinning
test name. Include a cross-UI consistency row: when two UIs express the same
outcome, the spec MUST require a single shared formatting helper, pinned by
tests on BOTH call paths — a test that mirrors the format function without
invoking the real handler path does not count as pinning.

**Impact grammar — the table's entry fee.** The impact cell MUST open with the
affected asset by name (whose what gets hurt), then the one-sentence
consequence that asset's owner would actually suffer, then one impact class:
不可逆／資料、邏輯核心、上下游契約、穩定性可靠性、UI/UX. No asset, no pinned
surface — a row that cannot name an asset does not enter the table. A
consequence the owner could never perceive (an imperceptible epsilon) does not
complete the sentence; a concern that honestly classifies as style, naming, or
any other measurement-side (MOP) matter belongs to lint and conventions, never
here.

**Downstream authority.** The impact class is the severity source of truth for
`$seal`'s findings grading: 不可逆／資料, 邏輯核心 and 上下游契約 rows are
must-fix tier; UI/UX rows carry the surface-asset prior (one birth-certificate
probe round for their judge). The tier is decided here, at contract time, under
the user's confirmation — never re-litigated at seal time.

## Loose-Criterion Escalation (reviewer side)

If a reviewer observes a REAL defect (wrong user-visible output,
self-contradicting message, data-shape misuse) but the acceptance criteria are
too loose to justify rejection: that is a SPEC BUG, not a pass. Reject citing
both the defect AND the loose criterion, and record a criteria patch.
"The spec doesn't forbid it" is never grounds to pass an observed defect.

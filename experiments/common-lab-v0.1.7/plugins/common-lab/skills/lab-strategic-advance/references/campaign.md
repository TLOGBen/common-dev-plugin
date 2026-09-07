# Small campaign contract

Use a new directory .common-lab/strategic/<campaign>/. Read an existing experimental state before resuming; never initialize over it. Source tool:

    python3 ${LAB_SKILL_DIR}/scripts/campaign.py --help

Initialize with a locked objective, a scope statement, and at least one observable criterion:

    campaign.py init <state.json> --objective "<outcome>" --scope "<authorized work>" --criterion "C1=<acceptance condition>"

The schema holds objective, scope, criteria, one focus, operation outcomes, status, and timestamped events. It deliberately omits mandatory staffing, scoreboards, fixed review rounds, and a full-system map. Original Common state is not interchangeable with this ledger.

When the user adds required outcomes to an unfinished campaign, use extend with new criterion IDs:

    campaign.py extend <state.json> --criterion "C2=<additional acceptance condition>" --reason "<user request and its scope>"

Optional --objective and --scope update the description to include the addition, not remove existing commitments or grant permission. Prior criteria, evidence, focus, operation outcomes, and blocked status stay intact; new criteria start unmet. Extension cannot replace or retire a criterion and is not a general contract rewrite.

Before a move:

    campaign.py focus <state.json> --criterion C1 --move "<bounded action>" --expect "<observable change>"

Record acceptance using a real local evidence artifact (for example a test report or captured read-only observation):

    campaign.py record <state.json> --criterion C1 --result met --evidence <file> --note "<why this meets the condition>"

Evidence is stored with an absolute path and SHA-256. A changed or missing artifact invalidates a met criterion at validation. A file's existence is not proof of its interpretation: the lead must inspect the content. Record an unmet result when the evidence fails; do not relabel a desired outcome as observed.

For an authorized consequential external mutation, first confirm exact target, identity, authority, recovery, and success observation using the real tool's rules. Record a unique operation key as pending before dispatch. The ledger does not authorize or execute the action:

    campaign.py operation <state.json> --key "<unique-key>" --target "<exact target>" --outcome pending
    campaign.py operation <state.json> --key "<same-key>" --target "<same target>" --outcome succeeded --evidence <observation-file>

Use unknown after an uncertain result. Reconcile the existing operation through read-only observation before recording succeeded or failed; never retry merely because the first response was unclear. The ledger refuses duplicate dispatch keys, a new dispatch to an unresolved target, and completion with pending/unknown outcomes. A known failed operation may be retried only after its cause, retry safety, authority, and stopping condition are resolved; use a new key linked in the note.

Use block --reason "<actual dependency>" when no safe progress remains; focus resumes an incomplete campaign when the dependency is actually removed. This local status is not the product goal API's blocked status or its separate recurrence rules.

Use validate during recovery and complete only after final acceptance. Every mutation checks the existing state, preserves the previous JSON in a sibling .history directory, and writes atomically. Assign one writer to this ledger; it is not a concurrent database. Completed campaigns are immutable: keep their evidence files unchanged and use a new campaign for new work. The tool does not delete history or migrate schemas.

For timing or token experiments, use independently observed start/end clocks and runtime telemetry. Keep unavailable token values null with their reason. Do not infer tokens or price from text length, context-window limits, or model names.

# Accounting and evidence

- Each `token_usage_record.usage` is one recorded model response, deduplicated by response ID. Noncached input is input minus cached input. Reasoning output is already included in output; never add it twice.
- `compacted.compaction_response_id` identifies compaction usage without reading its summary or replacement history. Keep ordinary execution, compaction, and their sum separate. CLI totals may omit compaction; check reconciliation rather than assuming either boundary.
- Optional CLI `turn.completed` usages are summed for the supplied events file. Supply matching scope: a whole session and a one-turn events file may not reconcile. A mismatch remains visible and does not rewrite observed counters.
- A tool's next usage record is a temporal link, not exclusive attribution. Multiple tools can share a response. Do not sum the same usage per tool or claim a tool caused all subsequent input.
- Full input includes reused context. Noncached input is not necessarily new source: prompts, cache misses and other messages can contribute. Character counts describe stored tool output, not tokens or necessarily the truncated model-visible payload.
- Event spans are elapsed intervals, not server compute or hidden reasoning time. Overlapping intervals must not be added to derive wall time.
- Keyword categories and duplicate hashes are diagnostic aids. They do not establish necessity, quality or waste. Verify work impact using public evidence and artifacts; unknown is a valid result.
- The parser rejects malformed complete lines and unsupported required counters, tolerating only an incomplete trailing record. It does not invent per-response usage from aggregate totals.
- Local log fields are not a promised stable public API. Revalidate after schema changes. Public CLI JSON events: https://learn.chatgpt.com/docs/non-interactive-mode .

For comparisons, record matching scope/model/effort. Compare completion and work quality alongside time, noncached/cached input, output, compaction usage, oversized results and repeated reads. One run can expose a failure mechanism without establishing a stable causal effect.

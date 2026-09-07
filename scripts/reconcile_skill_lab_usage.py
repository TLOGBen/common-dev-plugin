#!/usr/bin/env python3
"""Reconcile an explicit closed-call manifest with the immutable 182-call index."""
import argparse
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))
from astra_lead_usage_review import checked_usage, measure_call
PRIOR = REPO / 'docs/experiments/measurement-index-182calls-20260906'
spec = importlib.util.spec_from_file_location('index182', PRIOR / 'aggregate.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
read, sha, source = prior.read, prior.sha, prior.source

def resolve(value):
    path = Path(value)
    return path if path.is_absolute() else REPO / path

def single(result_path, raw_path, batch, expected=None):
    result = read(result_path)
    if expected is not None:
        assert result == expected, 'Summary/result mismatch: ' + str(result_path)
    events = [json.loads(line) for line in raw_path.read_text().splitlines() if line.strip()]
    found = [(n + 1, e['usage']) for n, e in enumerate(events) if e.get('type') == 'turn.completed']
    assert len(found) <= 1, 'Multiple task intervals require exact interval reconciliation'
    usage = checked_usage(found[0][1]) if found else None
    if usage is None:
        assert result.get('usage') is None, 'Unbacked summary usage'
    else:
        assert result.get('usage') is not None
        for key in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'total_tokens'):
            assert usage[key] == result['usage'][key], 'Raw/result usage mismatch'
        prior.validate_usage(usage)
    model = result.get('model_requested', result.get('model'))
    effort = result.get('effort_requested', result.get('effort'))
    seconds = result.get('wall_seconds', result.get('elapsed_seconds'))
    assert model and effort and seconds is not None
    ids = [e['thread_id'] for e in events if e.get('type') == 'thread.started']
    assert len(ids) <= 1
    return dict(id=str(result_path.resolve()), run_id=batch, role='fresh-cli', requested_model=model,
        effort=effort, status=result['status'], exit_code=result['exit_code'],
        started_utc=result['started_utc'], ended_utc=result['ended_utc'], wall_seconds=seconds,
        usage=usage, usage_basis='One exact raw turn.completed; no fabricated usage for missing completion',
        raw_usage_line=found[0][0] if found else None, thread_id=ids[0] if ids else None,
        source_result=source(result_path), source_raw=source(raw_path), provider_reported_cost_usd=None,
        **prior.cost_fields(usage, model))

def episode_rows(path, batch):
    review = read(path)
    assert not review['pending_episodes']
    rows = []
    for episode in review['episodes']:
        summary_path = resolve(episode['summary_path'])
        assert sha(summary_path) == episode['summary_sha256']
        summary = read(summary_path)
        assert len(summary['calls']) == len(episode['calls'])
        for original, saved in zip(summary['calls'], episode['calls']):
            derived = measure_call(original)
            for key in ('derived_usage', 'raw_sha256', 'result_sha256'):
                assert derived[key] == saved[key], 'Turn-scoped evidence drift'
            folder = Path(derived['evidence_dir'])
            usage, model = derived['derived_usage'], derived['model_requested']
            if usage is not None:
                prior.validate_usage(usage)
            rows.append(dict(id=str(folder.resolve()), run_id=batch, episode_id=episode['episode_id'],
                case_id=episode['case_id'], arm=episode['arm'], number=derived['number'], role=derived['role'],
                requested_model=model, effort=derived['effort_requested'], status=derived['status'],
                exit_code=original['exit_code'], started_utc=derived['started_utc'], ended_utc=derived['ended_utc'],
                wall_seconds=derived['wall_seconds'], usage=usage, usage_basis=derived['usage_basis'],
                model_observation=derived.get('model_observation'), source_result=source(folder/'result.json'),
                source_raw=source(folder/'stdout.jsonl'), source_usage_review=source(path),
                provider_reported_cost_usd=None, **prior.cost_fields(usage, model)))
    assert len(rows) == review['actual_cli_calls']
    return rows

def build(manifest_path):
    manifest = read(manifest_path)
    old = prior.build()
    assert old == read(PRIOR / 'index.json'), 'Prior frozen index drift'
    rows, batches = list(old['rows']), list(old['batches'])
    for batch in manifest['batches']:
        added = []
        if batch['kind'] == 'episode':
            path = resolve(batch['path'])
            added = episode_rows(path, batch['id'])
        elif batch['kind'] == 'summary':
            path = resolve(batch['path'])
            summary = read(path)
            for result in summary['results']:
                label = result['label']
                added.append(single(path.parent/(label+'.result.json'), path.parent/(label+'.raw.jsonl'), batch['id'], result))
            assert len(added) == summary['actual_calls']
        elif batch['kind'] == 'single':
            path = resolve(batch['path'])
            added = [single(path, resolve(batch['raw']), batch['id'])]
        else:
            raise ValueError('Unknown batch kind')
        assert len(added) == batch['expected_calls'], 'Manifest call count mismatch'
        rows.extend(added)
        batches.append(dict(run_id=batch['id'], calls=len(added), source=source(path)))
    assert len(rows) == manifest['expected_total_calls']
    assert len({row['id'] for row in rows}) == len(rows)
    assert len({row['source_raw']['path'] for row in rows}) == len(rows), 'Duplicate raw call (possibly panel evidence copy)'
    known = [row for row in rows if row['usage'] is not None]
    totals = {key:sum(row['usage'][key] for row in known) for key in (*prior.base.FIELDS, 'total_tokens')}
    standard = sum(Decimal(row['api_equivalent_standard_short_usd']) for row in known)
    sensitivity = sum(Decimal(row['known_context_sensitivity_usd']) for row in known)
    return dict(kind='explicit_closed_call_index', scope=manifest['scope'], manifest=source(manifest_path),
        previous_index=source(PRIOR/'index.json'), previous_aggregator=source(PRIOR/'aggregate.py'),
        calls=len(rows), known_usage_calls=len(known), unknown_usage_calls=len(rows)-len(known),
        known_usage_subtotal=totals, total_workflow_tokens=None,
        call_wall_seconds_sum=round(sum(row['wall_seconds'] for row in rows),3),
        union_of_call_intervals_seconds=prior.base.overlap_seconds([(row['started_utc'],row['ended_utc']) for row in rows]),
        time_limits='Call sum includes concurrency; interval union excludes gaps; neither is whole campaign duration.',
        pricing=dict(rate_source=old['pricing'], known_usage_standard_short_subtotal_usd=str(standard),
            known_usage_context_sensitivity_subtotal_usd=str(sensitivity), actual_invoice_usd=None,
            limits=['Public 2026-09-06 API rate scenarios, not subscription charges or invoice.',
                    'Unknown usage/cost not zero; no finite whole-run upper bound.',
                    'Cached input included in input; reasoning included in output, neither counted twice.',
                    'Aggregate invocation input is not proof of per-request long context.',
                    'Native authoring, host tools, taxes, FX and unobserved tier/region differences excluded.']),
        batches=batches, rows=rows)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    data = build(args.manifest)
    if args.verify:
        assert read(args.output) == data, 'Frozen output drift'
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(data,stream,ensure_ascii=False,indent=2)
            stream.write('\n')
    print(json.dumps({key:data[key] for key in ('calls','known_usage_calls','unknown_usage_calls','known_usage_subtotal','call_wall_seconds_sum','union_of_call_intervals_seconds')}))
    print(json.dumps({key:data['pricing'][key] for key in ('known_usage_standard_short_subtotal_usd','known_usage_context_sensitivity_subtotal_usd','actual_invoice_usd')}))
if __name__ == '__main__':
    main()

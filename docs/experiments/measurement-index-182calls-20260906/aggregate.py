#!/usr/bin/env python3
"""Reconcile 182 completed-batch CLI invocations; keep unknown usage unknown."""
import argparse
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPO/'scripts'))
from astra_lead_usage_review import measure_call
previous=REPO/'docs/experiments/measurement-index-119calls-20260906'
spec=importlib.util.spec_from_file_location('index119',previous/'aggregate.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
base=prior.base
ADDITIONS={'screen-v2-review/usage-complete-v1.json':24,
           'campaign-v1-review/usage-v1.json':5,
           'delegate-context-v1-review/usage-v1.json':12,
           'extension-v1-review/usage-complete-v1.json':4,
           'campaign-v2-review/usage-complete-v1.json':16}

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def source(path):
    path=path.resolve()
    return {'path':str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path),'sha256':sha(path)}
def cost_fields(usage,model):
    if usage is None:return {'api_equivalent_standard_short_usd':None,'known_context_sensitivity_usd':None}
    ordinary=base.price(usage,model)
    sensitive=base.price(usage,model,long=True) if model=='gpt-6-astra' and usage['input_tokens']>272000 else ordinary
    return {'api_equivalent_standard_short_usd':str(ordinary),'known_context_sensitivity_usd':str(sensitive)}
def validate_usage(value):
    assert all(type(value.get(k)) is int and value[k]>=0 for k in base.FIELDS)
    assert value['cached_input_tokens']+value['cache_write_input_tokens']<=value['input_tokens']
    assert value['reasoning_output_tokens']<=value['output_tokens']
    assert value['total_tokens']==value['input_tokens']+value['output_tokens']

def build():
    old=prior.build()
    assert old==read(previous/'index.json'),'Earlier frozen index drift'
    rows=[]
    for row in old['rows']:
        validate_usage(row['usage'])
        rows.append({**row,'known_context_sensitivity_usd':row['standard_context_sensitivity_upper_usd'],
                     'usage_basis':'Frozen index with raw/result/summary equality rechecked'})
    batches=list(old['batches'])
    solroot=REPO/'docs/experiments/baransu-lab/runs/sol-contract-verification-v1'
    sol=read(solroot/'summary.json')
    assert sol['actual_calls']==len(sol['results'])==2
    for record in sol['results']:
        result_path=solroot/(record['arm']+'.result.json');result=read(result_path)
        assert result==record
        raw_path=solroot/(record['arm']+'.raw.jsonl')
        assert sha(raw_path)==result['raw_jsonl_sha256']
        events=[json.loads(x) for x in raw_path.read_text().splitlines() if x.strip()]
        usages=[(n+1,x['usage']) for n,x in enumerate(events) if x.get('type')=='turn.completed']
        assert len(usages)==1
        line,usage=usages[0]
        usage={**usage,'total_tokens':usage['input_tokens']+usage['output_tokens']}
        validate_usage(usage)
        assert all(usage[k]==result['usage'][k] for k in ('input_tokens','cached_input_tokens','output_tokens','total_tokens'))
        rows.append({'id':'sol-contract-verification-v1/'+record['arm'],'run_id':'sol-contract-verification-v1',
                     'arm':record['arm'],'requested_model':record['requested_model'],'effort':record['requested_effort'],
                     'status':record['status'],'exit_code':record['exit_code'],'role':'verifier',
                     'started_utc':record['started_utc'],'ended_utc':record['ended_utc'],'wall_seconds':record['wall_seconds'],
                     'usage':usage,'usage_basis':'Single raw turn.completed; matches result and summary',
                     'source_result':source(result_path),'source_raw':source(raw_path),'raw_usage_line':line,
                     'provider_reported_cost_usd':record['reported_cost_usd'],**cost_fields(usage,record['requested_model'])})
    batches.append({'run_id':'sol-contract-verification-v1','calls':2,'source_summary':source(solroot/'summary.json')})
    for name,count in ADDITIONS.items():
        review_path=REPO/'docs/experiments/astra-lead-harness'/name
        review=read(review_path)
        assert review['actual_cli_calls']==count and not review['pending_episodes']
        for episode in review['episodes']:
            summary_path=Path(episode['summary_path'])
            assert sha(summary_path)==episode['summary_sha256']
            summary=read(summary_path)
            assert len(summary['calls'])==len(episode['calls'])
            for original,derived in zip(summary['calls'],episode['calls']):
                current=measure_call(original)
                assert current['derived_usage']==derived['derived_usage']
                assert current['raw_sha256']==derived['raw_sha256'] and current['result_sha256']==derived['result_sha256']
                usage=derived['derived_usage']
                if usage is not None:validate_usage(usage)
                directory=Path(derived['evidence_dir'])
                model=derived['model_requested']
                rows.append({'id':str(directory),'run_id':name.split('/')[0],
                             'episode_id':episode['episode_id'],'case_id':episode['case_id'],'arm':episode['arm'],
                             'number':derived['number'],'role':derived['role'],'requested_model':model,'effort':derived['effort_requested'],
                             'status':derived['status'],'exit_code':original['exit_code'],
                             'started_utc':derived['started_utc'],'ended_utc':derived['ended_utc'],'wall_seconds':derived['wall_seconds'],
                             'usage':usage,'usage_basis':derived['usage_basis'],'model_observation':derived.get('model_observation'),
                             'source_result':source(directory/'result.json'),'source_raw':source(directory/'stdout.jsonl'),
                             'source_usage_review':source(review_path),'scope_violations':original.get('scope_violations'),
                             'provider_reported_cost_usd':None,**cost_fields(usage,model)})
        batches.append({'run_id':name.split('/')[0],'calls':count,'source_usage_review':source(review_path)})
    assert len(rows)==len({r['id'] for r in rows})==182
    assert len({r['source_raw']['path'] for r in rows})==182
    known=[r for r in rows if r['usage'] is not None]
    totals={k:sum(r['usage'][k] for r in known) for k in (*base.FIELDS,'total_tokens')}
    assert len(known)==179 and totals['total_tokens']==19892206
    pricing={**old['pricing'],'standard_short_equivalent_usd':None,'standard_context_sensitivity_upper_usd':None,
             'known_usage_standard_short_subtotal_usd':str(sum(Decimal(r['api_equivalent_standard_short_usd']) for r in known)),
             'known_usage_context_sensitivity_subtotal_usd':str(sum(Decimal(r['known_context_sensitivity_usd']) for r in known)),
             'unknown_usage_calls':len(rows)-len(known),
             'limits':['Retains frozen 2026-09-06 public API rate scenarios, not a newly observed invoice or subscription charge.',
                       'Three timed-out calls have unknown usage and cost; no full-batch price or finite upper bound is claimed.',
                       'Input contains cache, output contains reasoning; each token counted once.',
                       'Context sensitivity applies only to Astra aggregate calls above272K; aggregate is not request-level context evidence.',
                       'Standard, no regional uplift/tool surcharge/tax/FX; actual tier and request lengths unknown.',
                       'Native lead/agent authoring, tools and ongoing resume-v1 are excluded.']}
    return {'kind':'frozen_182_cli_call_index','scope':'Previously frozen119 plus two Sol verifiers and five completed Astra-lead batches; excludes ongoing resume-v1 and native authoring.',
            'previous_index':source(previous/'index.json'),'previous_aggregator':source(previous/'aggregate.py'),
            'calls':len(rows),'known_usage_calls':len(known),'unknown_usage_calls':len(rows)-len(known),
            'known_usage_subtotal':totals,'total_workflow_tokens':None,
            'call_wall_seconds_sum':round(sum(r['wall_seconds'] for r in rows),3),
            'union_of_call_intervals_seconds':base.overlap_seconds([(r['started_utc'],r['ended_utc']) for r in rows]),
            'time_limits':'Call sum includes overlap; interval union excludes gaps; neither is whole campaign duration.',
            'pricing':pricing,'batches':batches,'rows':rows}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    data=build();path=Path(__file__).with_name('index.json')
    if args.verify:
        assert read(path)==data
        print('PASS: 182 unique raw calls,179 known,3 unknown; exact regenerated index')
    else:
        with path.open('x',encoding='utf-8') as out:json.dump(data,out,ensure_ascii=False,indent=2);out.write('\n')
        print(json.dumps({k:data[k] for k in ('calls','known_usage_calls','unknown_usage_calls','known_usage_subtotal','call_wall_seconds_sum','union_of_call_intervals_seconds')}))
        print(json.dumps(data['pricing']))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Four fixed file-reader proxies for an optional human projection; no auto scoring."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import time
sys.dont_write_bytecode=True
from lab_file_reader import invoke, observed, sha, save
from astra_lead_episode import inventory
REPO=Path(__file__).resolve().parents[1]
BRIEF=REPO/'experiments/common-lab-candidate018/source/common-lab/skills/lab-strategic-advance/scripts/campaign_brief.py'
SEQUENCE=[('unknown-operation','raw'),('unknown-operation','brief'),('insufficient-proof','brief'),('insufficient-proof','raw')]
TASK='請從入口看這份工作交接，必要時才讀允許的支持檔案。用一段可交接的繁體中文說明：目前哪些成果可以據此確認、整體能否視為已完成、下一個具體行動是什麼、是否有確實需要我作的決定。分清帳本紀錄與支持它的實際證據；不要執行後續工作。'

def write_new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as out:out.write(value)
def freeze(root,plan):
    root,plan=root.resolve(),plan.resolve()
    if (root.exists() or root.is_symlink() or root.parent!=Path('/tmp') or not root.name.startswith('campaign-brief-reader-')
            or plan.exists() or plan.is_symlink() or not plan.is_relative_to(REPO/'docs/experiments/astra-lead-harness')):
        raise ValueError('Fresh bounded paths required')
    sys.path.insert(0,str(BRIEF.parent))
    spec=importlib.util.spec_from_file_location('brief_candidate',BRIEF)
    brief=importlib.util.module_from_spec(spec);spec.loader.exec_module(brief)
    source_hash=sha(BRIEF)
    root.mkdir();plan.mkdir(parents=True)
    rows=[];answers=[]
    stamp=datetime.now(timezone.utc).isoformat()
    for index,(case,arm) in enumerate(SEQUENCE,1):
        label=f'R{index}'
        workspace=root/label;workspace.mkdir()
        proof=workspace/'observation.json'
        if case=='unknown-operation':
            data={'kind':'synthetic_receiver_observation','standard_release':'service-catalog-v3',
                  'query_ids':['S101','S102','S104','S105'],'south':[{'id':'S102','slots':0}],
                  'standard_checks_passed':True,'premium_operation_key':'premium-900-lost-reply',
                  'premium_operation_outcome':'unknown','premium_fee_decision':{'status':'APPROVED','selected':900}}
            objective='一般服務維持 v3；premium 依已核定900投用，操作結果必須有可識別證據。'
            criteria={'C1':{'text':'一般服務接受端為v3，包含零容量的S102','result':'met','note':'接受端版本與查詢有實際觀測'},
                      'C2':{'text':'已核定900的premium投用，取得該次操作可識別結果','result':'unmet','note':'已核定費率，但該次作用回覆遺失，無法判定結果'}}
            operations={'premium-900-lost-reply':{'target':'local premium receiver','outcome':'unknown','evidence':None,'note':'核准不是投用收據；先釐清原操作，不重送'}}
            status='blocked';focus={'criterion':'C1','move':'驗證一般服務接受端','expect':'版本v3且查詢正確'}
            events=[{'at':stamp,'action':'init'},{'at':stamp,'action':'block','reason':'費率已核定；缺的是premium-900-lost-reply的可識別作用證據，不是再選費率'}]
            expectation={'confirmed':'standard receiver v3 incl slots0','whole':'unconfirmed/incomplete premium','next':'identity-bearing observation for the existing operation, no resend','human_choice':'no new fee choice; approved900 is already given','focus':'recorded focus C1 is already met; do not blindly repeat it'}
        else:
            data={'kind':'synthetic_source_lint_receipt','linter_exit':0,'syntax_checks_passed':True,
                  'observed_surface':'source syntax only','receiver_contacted':False,
                  'limits':'This receipt does not inspect deployment, active receiver version or query behavior.'}
            objective='讓本地一般服務的接受端實際採用v3並有正確查詢。'
            criteria={'C1':{'text':'接受端採用v3，實際查詢包含S101、S102、S104、S105且保留slots0','result':'met','note':'已驗收完成'}}
            operations={};status='complete';focus=None
            events=[{'at':stamp,'action':'init'},{'at':stamp,'action':'complete'}]
            expectation={'confirmed':'source syntax/lint only','whole':'ledger says complete but supplied proof does not establish receiver goal','next':'current receiver version and actual query observation','human_choice':'no new approval established as missing; evidence gap not a fabricated decision'}
        save(proof,data)
        evidence={'path':str(proof),'sha256':sha(proof)}
        for criterion in criteria.values():criterion['evidence']=evidence
        state={'schema':'common-lab-campaign/1','objective':objective,
               'scope':'合成本地觀察；本輪只請讀者解释交接，不授權操作、改資料或替人批准。',
               'criteria':criteria,'focus':focus,'operations':operations,'status':status,'revision':3,'events':events}
        state_path=workspace/'state.json';save(state_path,state)
        # Equal integrity facts available to both arms; neither gets a hidden
        # authority or an extra receiver probe through formatting.
        integrity=workspace/'integrity-observation.json'
        save(integrity,{'observed_at':stamp,'state_sha256':sha(state_path),'evidence_path':str(proof),
                        'recorded_evidence_sha256':evidence['sha256'],'observed_evidence_sha256':sha(proof),
                        'file_exists':True,'digest_matches':True,
                        'limit':'File integrity is not semantic acceptance, approval or human understanding.'})
        files=[str(state_path),str(integrity),str(proof)]
        entry=state_path
        if arm=='brief':
            entry=workspace/'handoff.md'
            write_new(entry,brief.render(state,state_path,stamp))
            files=[str(entry),*files]
        rows.append({'label':label,'entry':str(entry),'files':files,'task':TASK})
        answers.append({'label':label,'case':case,'arm':arm,'expected':expectation})
    assert source_hash==sha(BRIEF)
    data={'kind':'four_optional_brief_readers','model':'gpt-5.6-sol','effort':'high','rows':rows,
          'input_sha256':observed(rows),'candidate_script':str(BRIEF),'candidate_sha256':source_hash,
          'shared_reader_sha256':sha(REPO/'scripts/lab_file_reader.py'),'runner_sha256':sha(Path(__file__)),
          'created_utc':stamp,'model_calls_at_freeze':0,
          'limits':['Same supporting facts and integrity observations; brief arm additionally has a generated entry.',
                    'Read paths are prompt-scoped; raw trace must be reviewed. No human comprehension score.',
                    'Two synthetic situations with A/B/B/A order, not randomized/general reader performance.',
                    'No skill is loaded by reader; this tests the resulting view, not skill invocation reliability.']}
    save(plan/'frozen-plan.json',data)
    save(plan/'expected-answers-not-actor-input.json',answers)
    print(json.dumps({'status':'FROZEN_NO_MODEL_CALLS','plan':str(plan),'calls':4,'input_files':len(data['input_sha256'])}))

def run(plan,output):
    frozen=read(plan/'frozen-plan.json')
    assert sha(Path(__file__))==frozen['runner_sha256']
    assert sha(REPO/'scripts/lab_file_reader.py')==frozen['shared_reader_sha256']
    assert sha(Path(frozen['candidate_script']))==frozen['candidate_sha256']
    assert not output.exists() and not output.is_symlink()
    assert observed(frozen['rows'])==frozen['input_sha256']
    output.mkdir(parents=True)
    save(output/'plan-copy.json',frozen)
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic();results=[]
    for row in frozen['rows']:
        assert observed(frozen['rows'])==frozen['input_sha256']
        results.append(invoke(row,output,frozen['model'],frozen['effort']))
        if observed(frozen['rows'])!=frozen['input_sha256']:break
    known=[row['usage'] for row in results if row['usage'] is not None]
    summary={'kind':'optional_brief_reader_proxy','started_utc':started,'ended_utc':datetime.now(timezone.utc).isoformat(),
             'elapsed_wall_seconds':time.monotonic()-clock,'planned_calls':4,'actual_calls':len(results),
             'results':results,'known_usage':{k:sum(row[k] for row in known) for k in ('input_tokens','cached_input_tokens','output_tokens','total_tokens')},
             'unknown_calls':len(results)-len(known),'input_drift':observed(frozen['rows'])!=frozen['input_sha256'],
             'actual_human_understanding':None,'actual_cost_usd':None,'semantic_acceptance':'PENDING_MAIN_REVIEW'}
    save(output/'summary.json',summary)
    print(json.dumps({'status':'FINISHED_NOT_GRADED','calls':len(results),'known_usage':summary['known_usage']}))

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--freeze',action='store_true');action.add_argument('--run',action='store_true')
    parser.add_argument('--root',type=Path);parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.freeze:freeze(args.root,args.plan)
    else:run(args.plan,args.output)
if __name__=='__main__':main()

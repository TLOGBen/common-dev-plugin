#!/usr/bin/env python3
"""Read-only Codex 0.153.x log analyzer. No model calls; output is metadata only.
Usage: python3 token_lens.py --session /path/to/rollout.jsonl --out /new/report/directory
Raw reasoning, compaction summaries, user/config content and raw tool output are never exported.
"""
import argparse, bisect, datetime, hashlib, json, re, sys
from pathlib import Path

def records(path):
    with path.open(encoding='utf-8') as f:
        for line_no, line in enumerate(f,1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                if not line.endswith('\n') and not f.read(1):
                    return
                raise ValueError(f'Malformed JSON at {path.name}:{line_no}')
            if not isinstance(item, dict):
                raise ValueError(f'Expected JSON object at {path.name}:{line_no}')
            yield line_no, item

def epoch(s):
    return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()

TERMS=['python','node','react','vue','sql','api','git','build','test','report','search','querydsl','hibernate','springfox','springdoc','jasypt','quartz','jakarta','javax','swagger','spire','jasper','ldap','redis','mail','sftp','jwt','war','pom','frontend','backend','inventory','skill','release','maintainer','maintenance','fork','classifier']
def tags(s):
    low=s.lower()
    return [t for t in TERMS if re.search(r'(?<![a-z])'+t+r'(?![a-z])',low)]

def group(s):
    low=s.lower()
    if ('skill.md' in low or '/references/' in low) and 'inventory.py' not in low:return 'Skill / 手冊'
    if 'inventory.py' in low:return '清冊'
    if re.search(r'(report|summary|estimate|output)[-_.a-z]*\.(md|json|html)', low):return '產物 / 覆核'
    if 'git ' in low or '--version' in low:return '環境 / 狀態'
    if any(x in low for x in ['rg -','sed -','nl -','find ']):return '來源查證'
    return '其他工具'

def analyze(session, events=None, label=None, start=None, status=None):
    status = status or {}
    if start is None:
        first = next(records(session), None)
        if first is None or not first[1].get('timestamp'):
            raise ValueError('Session has no timestamped records')
        start = epoch(first[1]['timestamp'])
    tools=[];usage=[];compactions=[];compaction_ids=set();seen_items=set();seen_usage=set();seen_commands={};seen_outputs={}
    fields=['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']
    for line,e in records(session):
        p=e.get('payload',{});kind=e.get('type')
        if kind=='compacted':
            if p.get('compaction_response_id'):compaction_ids.add(p['compaction_response_id'])
            continue
        if kind=='token_usage_record':
            rid=p.get('response_id')
            if not rid or rid in seen_usage:continue
            seen_usage.add(rid);u=p.get('usage',{})
            if not all(type(u.get(k)) is int and u[k] >= 0 for k in fields):raise ValueError('Unsupported usage schema')
            if u['cached_input_tokens'] > u['input_tokens'] or u['reasoning_output_tokens'] > u['output_tokens']:raise ValueError('Inconsistent usage counters')
            row={k:u[k] for k in fields}
            row.update({'response_id':rid,'turn_id':p.get('turn_id'),'seconds':round(epoch(e['timestamp'])-start,3),'log_line':line,'noncached_input_tokens':u['input_tokens']-u['cached_input_tokens']})
            usage.append(row)
        if kind!='event_msg' or p.get('type')!='item_completed':continue
        i=p.get('item',{});typ=i.get('type')
        # Do not traverse Reasoning items or any compaction contents.
        if typ not in ['CommandExecution','Extension','FileChange','ContextCompaction']:continue
        itemid=i.get('id')
        if not itemid or itemid in seen_items:continue
        seen_items.add(itemid)
        st=p.get('started_at_ms');end=p.get('completed_at_ms')
        sec=round((end/1000 if isinstance(end,(int,float)) else epoch(e['timestamp']))-start,3)
        span=round((end-st)/1000,3) if isinstance(st,(int,float)) and isinstance(end,(int,float)) else None
        if typ=='ContextCompaction':
            compactions.append({'seconds':sec,'event_span_seconds':span,'log_line':line});continue
        row={'index':len(tools)+1,'id':itemid,'type':typ,'seconds':sec,'event_span_seconds':span,'log_line':line,'output_chars':0,'max_line_chars':0,'line_count':0,'duplicate_command_of':None,'duplicate_output_of':None}
        if typ=='CommandExecution':
            cmd=i.get('command','');cmd=' '.join(cmd) if isinstance(cmd,list) else str(cmd)
            output=i.get('aggregated_output','') or '';ls=output.splitlines()
            ch=hashlib.sha256(cmd.encode()).hexdigest();oh=hashlib.sha256(output.encode()).hexdigest()
            row.update({'group':group(cmd),'tags':tags(cmd),'exit_code':i.get('exit_code'),'output_chars':len(output),'line_count':len(ls),'max_line_chars':max(map(len,ls),default=0),'duplicate_command_of':seen_commands.get(ch),'duplicate_output_of':seen_outputs.get(oh) if output else None})
            seen_commands.setdefault(ch,row['index'])
            if output:seen_outputs.setdefault(oh,row['index'])
            row['label']=' / '.join(row['tags']) or row['group']
        elif typ=='Extension':
            action=i.get('action',{});raw=json.dumps(action,ensure_ascii=False)
            row.update({'group':'網路查證','tags':tags(raw),'label':('搜尋' if action.get('type')=='search' else '讀取網頁')+'：'+(' / '.join(tags(raw)) or '其他網路資料')})
        else:
            row.update({'group':'寫入產物','tags':[],'label':'產物修改（內容需另行判讀）'})
        tools.append(row)
    if not usage:raise ValueError('No per-response token_usage_record entries; unsupported log format')
    for u in usage:u['usage_kind']='compaction' if u['response_id'] in compaction_ids else 'execution'
    usage.sort(key=lambda x:x['seconds']);tools.sort(key=lambda x:x['seconds'])
    prev=-1
    for j,u in enumerate(usage,1):
        u['index']=j;u['tools_since_previous_usage']=[t['index'] for t in tools if prev<t['seconds']<=u['seconds']]
        prev=u['seconds']
    times=[u['seconds'] for u in usage]
    for t in tools:
        n=bisect.bisect_right(times,t['seconds'])
        t['next_usage_index']=n+1 if n<len(usage) else None
    sums={k:sum(x[k] for x in usage) for k in fields+['noncached_input_tokens']}
    final = None
    cli_turns = []
    if events:
        for _, event in records(events):
            if event.get('type') == 'turn.completed':
                cli_turns.append(event.get('usage', {}))
        if cli_turns:
            final = {k: sum(u[k] for u in cli_turns) for k in fields
                     if all(type(u.get(k)) is int for u in cli_turns)}
    execution_sums={k:sum(x[k] for x in usage if x['usage_kind']=='execution') for k in fields+['noncached_input_tokens']}
    compaction_sums={k:sums[k]-execution_sums[k] for k in sums}
    reconciliation={k:{'execution_response_sum':execution_sums[k],'turn_total':final.get(k),'matches':execution_sums[k]==final.get(k)} for k in fields if final and k in final}
    if any(not x['matches'] for x in reconciliation.values()):
        note='一般回應加總與 CLI 最終 usage 不一致；請檢查紀錄，勿視為完整帳單。'
    else:note='一般回應加總與 CLI 最終 usage 相符；壓縮回應依 response ID 另外列帳。' if final else '未提供可核對的 CLI usage；僅列已觀察用量，不代表零用量或已完成。'
    return {'run':label or session.stem,'elapsed_seconds':status.get('elapsed_seconds'),'completed':bool(status) and not status.get('timed_out', False) and status.get('exit_code') == 0,'source_session':session.name,'cli_completed_turns':len(cli_turns),'summary':sums,'execution_usage':execution_sums,'compaction_usage':compaction_sums,'reconciliation':reconciliation,'reconciliation_note':note,'tools':tools,'responses':usage,'compactions':compactions,'limits':['Usage is exact per recorded model response, not per source line or tool call.','A tool is linked to the next usage record by time only. Several tools may share one record: do not sum linked usage per tool.','Tool output characters are not tokens and may differ from the model-visible truncated output.','Category tags are heuristics. Duplicate output does not establish uselessness.','Event spans are logged timing, not a claim about server compute or internal reasoning.','Raw reasoning, compaction summaries, raw commands, source content, credentials and user messages are excluded.','Per-probe impact on work items requires comparing public evidence and artifact revisions; not automatically inferred.']}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument('--session', type=Path, help='Exact Codex session JSONL')
    source.add_argument('--run', type=Path, help='Isolated-run shorthand with home/.codex/sessions')
    ap.add_argument('--events', type=Path, help='Matching codex exec --json log')
    ap.add_argument('--label', help='Display label')
    ap.add_argument('--out', type=Path, required=True, help='New output directory')
    args = ap.parse_args()
    root = args.run.resolve() if args.run else None
    start, status = None, {}
    if root:
        sessions = list((root / 'home/.codex/sessions').rglob('*.jsonl'))
        if len(sessions) != 1:
            raise ValueError('Run shorthand needs exactly one session; use --session to select it')
        session = sessions[0]
        events = args.events or (root / 'events.jsonl' if (root / 'events.jsonl').exists() else None)
        if (root / 'started.json').exists():
            start = epoch(json.loads((root / 'started.json').read_text())['started_utc'])
        if (root / 'status.json').exists():
            status = json.loads((root / 'status.json').read_text())
    else:
        session = args.session.resolve()
        events = args.events
    out = args.out.resolve()
    protected = [session.resolve().parent] + ([root] if root else [])
    if events:
        protected.append(events.resolve().parent)
    if any(out == p or p in out.parents for p in protected):
        raise ValueError('Output must be outside input log directories')
    if out.exists():
        raise ValueError('Use a new output directory; existing reports are preserved')
    data = analyze(session, events, args.label or (root.name if root else None), start, status)
    template = (Path(__file__).resolve().parent.parent / 'assets/report.html').read_text(encoding='utf-8')
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    out.mkdir(parents=True, exist_ok=False)
    (out / 'data.json').write_text(payload + '\n', encoding='utf-8')
    (out / 'index.html').write_text(template.replace('__DATA__', payload.replace('<', '\\u003c')), encoding='utf-8')
    print(json.dumps({'report':str(out/'index.html'), 'responses':len(data['responses']), 'tools':len(data['tools']), 'usage':data['summary'], 'execution_usage':data['execution_usage'], 'compaction_usage':data['compaction_usage'], 'reconciliation_note':data['reconciliation_note']}, ensure_ascii=False))

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        print(f'TOKEN_LENS_ERROR: {exc}', file=sys.stderr)
        raise SystemExit(2)

"""Operation-input arithmetic and reproducible pricing artifact helper."""
import json,sys
from decimal import Decimal,InvalidOperation,ROUND_CEILING
D=Decimal

def number(x):
    if isinstance(x,bool):raise ValueError('boolean is not a quantity')
    try:v=D(str(x))
    except InvalidOperation:raise ValueError('invalid quantity')
    if not v.is_finite() or v<0:raise ValueError('quantity must be finite and nonnegative')
    return v

def ceil(v):return int(v.to_integral_value(rounding=ROUND_CEILING))

def calculate(data):
    hours_day=number(data.get('hours_per_day',8))
    if hours_day==0:raise ValueError('hours_per_day must be positive')
    seen_rows=set();seen_operations={};rows=[];known=0;unresolved=[]
    for row in data['items']:
        rid=row['id']
        if not rid or rid in seen_rows:raise ValueError('duplicate or empty item ID')
        seen_rows.add(rid)
        if 'pending' in row and not isinstance(row['pending'],bool):raise ValueError('pending must be a boolean')
        if row.get('pending') and any(k in row for k in ('fixed_pd','operations','additions')):raise ValueError('pending item cannot also contain pricing')
        if row.get('pending'):
            rows.append({'id':rid,'status':'pending','total_pd':None});unresolved.append(rid);continue
        if 'fixed_pd' in row:
            if row.get('operations') or row.get('additions'):raise ValueError('fixed allocation cannot also contain priced operations')
            fixed=number(row['fixed_pd']);known+=fixed
            rows.append({'id':rid,'status':'fixed','E_pd':None,'V_pd':None,'unsplit_pd':fixed,'total_pd':fixed});continue
        if not row.get('operations') and not str(row.get('zero_reason','')).strip():raise ValueError('no operations: explicitly state why baseline is zero, or mark pending')
        eh=vh=D(0)
        for op in row.get('operations',[]):
            oid=op['id']
            if not oid or oid in seen_operations:raise ValueError(f'operation {oid} priced more than once')
            seen_operations[oid]=rid
            h=number(op['hours'])*number(op.get('count',1))
            if op['kind']=='E':eh+=h
            elif op['kind']=='V':vh+=h
            else:raise ValueError('operation kind must be E or V')
        ep=ceil(eh/hours_day);vp=ceil(vh/hours_day);base=ep+vp
        ae=av=au=0;additions=[]
        for add in row.get('additions',[]):
            parts={};unit=add['unit']
            if not any(k in add for k in ('E','V','unsplit')):raise ValueError('addition requires an explicit low/high interval; missing input is not zero')
            if unit not in ('hours','pd'):raise ValueError('addition unit must be hours or pd')
            if unit=='hours' and 'unsplit' in add:raise ValueError('unsplit PD interval must not invent hours')
            if 'unsplit' in add and ('E' in add or 'V' in add):raise ValueError('unsplit addition cannot also be split')
            for kind in ('E','V','unsplit'):
                if kind not in add:continue
                lo,hi=map(number,add[kind])
                if lo>hi:raise ValueError('low exceeds high')
                mid=(lo+hi)/2;pd=ceil(mid/hours_day if unit=='hours' else mid)
                parts[kind]={'low':lo,'high':hi,'midpoint':mid,'pd':pd,'unit':unit}
                if kind=='E':ae+=pd
                elif kind=='V':av+=pd
                else:au+=pd
            additions.append(parts)
        extra=ae+av+au;limit=D(base)/5
        accepted=extra<=limit
        if not accepted:unresolved.append(rid)
        total=base+extra if accepted else None
        known+=total if accepted else base
        rows.append({'id':rid,'status':'priced' if accepted else 'scope_review_required','E_hours':eh,'V_hours':vh,'B_pd':base,'A_pd':extra,'limit_pd':limit,'addition_inputs':additions,'E_pd':ep+ae if accepted else ep,'V_pd':vp+av if accepted else vp,'unsplit_pd':au if accepted else None,'total_pd':total,'baseline_only_pd':base if not accepted else None})
    return {'items':rows,'known_subtotal_pd':known,'unresolved_item_ids':unresolved,'complete':not unresolved,'limits':['Arithmetic only: different IDs may still describe duplicate work.','No judgment of route viability, scope necessity, rate realism or customer responsibility.','Above-cap additions are flagged; never clamped or moved into baseline.']}


def serial(value):
    if isinstance(value, Decimal):
        return int(value) if value == int(value) else float(value)
    raise TypeError(type(value).__name__)

def md(value):
    return str(value).replace('|',r'\|').replace('\n',' ')

def render(data,result,input_hash):
    lines=['# 操作輸入的工具計算結果','',f'原始輸入 SHA-256：`{input_hash}`。本表只從同目錄的 `input.json` 計算；原始操作必要性、共享歸屬與工程判斷仍須人工核對。','',
           '| ID | 工項 | 基準 E 小時 | 基準 V 小時 | 最終 E 人天（含 A） | 最終 V 人天（含 A） | B | A | 未拆 | 合計 | 狀態 |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for source,row in zip(data['items'],result['items']):
        def val(k):
            if row.get(k) is not None:return row[k]
            if row['status']=='pending':return '待估'
            if row['status']=='fixed' and k in ('E_hours','V_hours','E_pd','V_pd'):return '未拆'
            if row['status']=='scope_review_required' and k=='total_pd':return '待處理'
            return '—'
        lines.append('| '+' | '.join(md(x) for x in [row['id'],source.get('name',''),val('E_hours'),val('V_hours'),val('E_pd'),val('V_pd'),val('B_pd'),val('A_pd'),val('unsplit_pd'),val('total_pd'),row['status']])+' |')
    lines += ['',f"已估小計：{result['known_subtotal_pd']} 人天；E {result['known_totals']['E_pd']}、V {result['known_totals']['V_pd']}、未拆 {result['known_totals']['unsplit_pd']}。",f"待處理 ID：{', '.join(result['unresolved_item_ids']) or '無'}。",'','## 原始操作與引用（由同一輸入產生）','']
    for source,row in zip(data['items'],result['items']):
        lines += [f"### {md(source['id'])} {md(source.get('name',''))}",'']
        for key,title in [('references','引用已承接'),('basis','工程依據'),('zero_reason','零工時理由'),('pending_reason','待估原因')]:
            if key in source:lines += [f"{title}：{md(source[key])}",'']
        if source.get('operations'):
            lines += ['| 操作 ID | 類別 | 實際動作／結果 | 每次小時 | 次數 |','|---|---|---|---:|---:|']
            for op in source['operations']:
                lines.append('| '+' | '.join(md(x) for x in [op['id'],op['kind'],op.get('description',''),op['hours'],op.get('count',1)])+' |')
            lines.append('')
        for i,add in enumerate(row.get('addition_inputs',[]),1):
            original=source['additions'][i-1]
            lines += [f"加值 {i} 依據：{md(original.get('basis','未填'))}",'']
            for kind,part in add.items():
                lines += [f"- {kind}：{part['low']}～{part['high']} {part['unit']} → 中點 {part['midpoint']} → {part['pd']} 人天。"]
            lines.append('')
    lines += ['## 計算限制','']+['- '+x for x in result['limits']]
    return '\n'.join(lines)+'\n'

def publish(input_path,output_directory):
    from pathlib import Path
    import hashlib
    src=Path(input_path);out=Path(output_directory)
    if out.exists():raise ValueError('output directory already exists; choose a new version, never overwrite an earlier input/result')
    raw=src.read_bytes();data=json.loads(raw)
    for row in data['items']:
        for op in row.get('operations',[]):
            if not str(op.get('description','')).strip():raise ValueError('each priced operation needs a readable action/result description')
    result=calculate(data)
    result['known_totals']={key:sum((row.get(key) or 0) for row in result['items']) for key in ('E_pd','V_pd','unsplit_pd')}
    assert sum(result['known_totals'].values())==result['known_subtotal_pd']
    digest=hashlib.sha256(raw).hexdigest()
    result['input_sha256']=digest
    result['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    body=json.dumps(result,ensure_ascii=False,indent=2,default=serial)+'\n'
    report=render(data,result,digest)
    out.mkdir(parents=True,exist_ok=False)
    with (out/'input.json').open('xb') as f:f.write(raw)
    with (out/'result.json').open('x',encoding='utf-8') as f:f.write(body)
    with (out/'pricing.md').open('x',encoding='utf-8') as f:f.write(report)
    return {'output':str(out),'input_sha256':digest,'known_subtotal_pd':result['known_subtotal_pd'],'complete':result['complete'],'unresolved_item_ids':result['unresolved_item_ids']}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description='Calculate an operation-input snapshot into a new, never-overwritten output directory.')
    p.add_argument('input');p.add_argument('output_directory')
    args=p.parse_args()
    print(json.dumps(publish(args.input,args.output_directory),ensure_ascii=False,default=serial))

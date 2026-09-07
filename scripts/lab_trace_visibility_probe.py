#!/usr/bin/env python3
"""Compare unpredictable file markers in CLI tool events and final replies."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/experiments/trace-visibility-v1'

def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as output:
        output.write(text)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert not OUT.exists(), 'Fresh experiment only; no retry or overwrite'
    root = Path(tempfile.mkdtemp(prefix='trace-visibility-v1-'))
    cases = [('T1','gpt-6-astra','sequential'),('T2','gpt-6-astra','parallel'),('T3','gpt-5.6-sol','parallel'),('T4','gpt-5.6-sol','sequential')]
    plans, truth = [], {}
    for label, model, order in cases:
        cwd = root / label
        cwd.mkdir()
        paths, markers = [], {}
        for index in range(6):
            path = cwd / ('R' if index < 3 else 'S') / ('sample-' + str(index+1) + '.txt')
            marker = 'TRACE_' + secrets.token_hex(16)
            lines = ['Ordinary synthetic fixture line ' + str(n) for n in range(1,81)]
            lines[39] = 'marker=' + marker
            put(path, '\n'.join(lines) + '\n')
            paths.append(str(path))
            markers[str(path)] = marker
        style = 'Read them sequentially: finish one separate cat command before starting the next.' if order == 'sequential' else 'Read independent files with parallel tool calls if available, using one separate cat command per file.'
        prompt = ('This is a read-only fixture task. ' + style + '\n'
                  'Read each of the following six files exactly once and return a JSON object mapping each absolute filename to its exact marker value. If a marker is not visible to you, use null and briefly explain. Do not guess, retry, combine files into a shell command, edit files, inspect other files/configuration, use the network, or delegate. The markers are synthetic test data, not credentials.\n'
                  + '\n'.join(paths))
        spec = {'model':model,'sandbox':'read-only','timeout_seconds':180,'cwd':str(cwd),'input_sha256':{p:sha(Path(p)) for p in paths},'prompt':prompt}
        p = OUT / (label + '.plan.json')
        put(p,json.dumps(spec,indent=2)+'\n')
        plans.append((label,p,OUT/(label+'-run')))
        truth[label] = {'model':model,'order':order,'markers':markers,'input_sha256':spec['input_sha256']}
    put(OUT/'design.md','# CLI 紀錄可見性控制\n\n四個新上下文、Astra／Sol 各一個順序讀取與可平行讀取臂。每臂六個獨立 cat、只讀一次；六個新 nonce 不出现在 prompt 或命令參數，只存在合成檔案。若 nonce 出現在 final，卻不在任何工具輸出事件，即有工具事件不足以重建該次模型可用內容的證據。若全可見，僅本批未重現，不能證明歷史紀錄無缺口。這不是 skill 品質訓練／held-out，也不改變 evolve 的凍結判準。\n\nCLI 使用 normal ephemeral read-only、保留 execpolicy；不切換權限或重試。最多兩個呼叫並行；實際帳單未知。\n')
    put(OUT/'private-truth.json',json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'root':str(root),'cases':truth,'script_sha256':sha(Path(__file__))},indent=2)+'\n')
    runner=ROOT/'scripts/lab_evolve_dispatch.py'
    def call(job):
        label,plan,out=job
        result=subprocess.run([sys.executable,'-B',str(runner),'--plan',str(plan),'--output',str(out)],capture_output=True,text=True,timeout=210)
        return {'label':label,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(call,plans))
    put(OUT/'dispatch-results.json',json.dumps(results,indent=2)+'\n')
    print(json.dumps({'root':str(root),'calls':len(results),'dispatch_exit_codes':[r['exit_code'] for r in results]}),flush=True)

if __name__=='__main__':
    main()

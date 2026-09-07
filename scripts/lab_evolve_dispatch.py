#!/usr/bin/env python3
"""One frozen normal CLI dispatch. Preserve evidence; never decide skill adoption."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
sys.dont_write_bytecode=True
from common_lab_ab import parse_events, save

def sha(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()
def utc():
 return datetime.now(timezone.utc).isoformat()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--plan',required=True,type=Path)
 p.add_argument('--output',required=True,type=Path)
 a=p.parse_args()
 spec=json.loads(a.plan.read_text())
 assert not a.output.exists(), 'Fresh evidence directory required'
 assert spec['model'] in ('gpt-6-astra','gpt-5.6-sol')
 assert spec['sandbox'] in ('read-only','workspace-write')
 assert 1<=spec['timeout_seconds']<=600
 inputs={f:sha(Path(f)) for f in spec['input_sha256']}
 assert inputs==spec['input_sha256'],'Input drift'
 a.output.mkdir(parents=True)
 command=['codex','exec','--json','--ephemeral','--ignore-user-config','-m',spec['model'],'-c','model_reasoning_effort=high','-s',spec['sandbox'],'-C',spec['cwd'],'--skip-git-repo-check','-']
 start,tick,timedout=utc(),time.monotonic(),False
 with (a.output/'prompt.txt').open('x',encoding='utf-8') as f:f.write(spec['prompt'])
 save(a.output/'request.json',{'started_utc':start,'command':command,'plan_sha256':sha(a.plan),'runner_sha256':sha(Path(__file__)),'fallback':False,'timeout_seconds':spec['timeout_seconds']})
 proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',start_new_session=True)
 try:raw,err=proc.communicate(spec['prompt'],timeout=spec['timeout_seconds'])
 except subprocess.TimeoutExpired:
  timedout=True
  os.killpg(proc.pid,signal.SIGTERM)
  try:raw,err=proc.communicate(timeout=3)
  except subprocess.TimeoutExpired:
   os.killpg(proc.pid,signal.SIGKILL)
   raw,err=proc.communicate()
 for name,body in [('raw.jsonl',raw),('stderr.txt',err)]:
  with (a.output/name).open('x',encoding='utf-8') as f:f.write(body)
 parsed=parse_events(raw)
 result={'started_utc':start,'ended_utc':utc(),'elapsed_seconds':time.monotonic()-tick,'status':'timeout_unknown' if timedout else 'completed' if proc.returncode==0 and parsed['turn_completed'] else 'failed','exit_code':proc.returncode,'model_requested':spec['model'],'effort_requested':'high','input_unchanged':inputs=={f:sha(Path(f)) for f in inputs},'actual_cost_usd':None,'adoption':None,'semantic_acceptance':None,**parsed}
 save(a.output/'result.json',result)
 print(json.dumps({k:result[k] for k in ('status','elapsed_seconds','usage','input_unchanged')}),flush=True)
if __name__=='__main__':main()

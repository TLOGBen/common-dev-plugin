#!/usr/bin/env python3
"""Freeze a four-call train comparison using the existing readonly verifier runner."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
sys.dont_write_bytecode=True
from common_lab_ab import save
ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/'scripts/lab_verifier_probe.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--baseline',required=True,type=Path)
 p.add_argument('--candidate',required=True,type=Path)
 p.add_argument('--output',required=True,type=Path)
 p.add_argument('--run',action='store_true')
 a=p.parse_args()
 spec=importlib.util.spec_from_file_location('existing_verifier_runner',RUNNER)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 module.PREP=a.output.resolve()
 if a.run:
  module.run();return
 assert not a.output.exists(),'Fresh plan required'
 original=json.loads((ROOT/'docs/experiments/baransu-lab/verifier-boundaries-v1b/frozen-plan.json').read_text())
 train=original['rows'][0]
 for name in train['files']:assert sha(Path(name))==original['input_sha256'][name]
 root=Path(tempfile.mkdtemp(prefix='evolve-verifier-train-'))
 rows=[]
 for label,model,variant in [('X1','gpt-5.6-sol','baseline'),('X2','gpt-5.6-sol','candidate'),('X3','gpt-6-astra','candidate'),('X4','gpt-6-astra','baseline')]:
  dest=root/label
  for name in train['files']:
   src=Path(name);target=dest/src.relative_to(Path(train['cwd']))
   target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb') as f:f.write(src.read_bytes())
  role=dest/'selected-role.md'
  with role.open('xb') as f:f.write((a.baseline if variant=='baseline' else a.candidate).read_bytes())
  files=sorted(str(p) for p in dest.rglob('*') if p.is_file())
  row={'label':label,'model':model,'effort':'high','cwd':str(dest),'role':str(role),'files':files}
  row['prompt']=module.prompt(row)
  rows.append(row)
 plan={'created_utc':module.utc(),'root':str(root),'rows':rows,'input_sha256':{name:sha(Path(name)) for row in rows for name in row['files']},'runner_sha256':sha(RUNNER),'design_sha256':None,'timeout':240,'source_baseline_sha256':sha(a.baseline),'source_candidate_sha256':sha(a.candidate)}
 # Existing runner checks a design artifact before calling models. This artifact is frozen, not rewritten.
 a.output.mkdir(parents=True)
 design='Four new readonly train calls; same R/S/V fixtures and prompts, role bytes are the sole within-model treatment. X1/X2 Sol; X3/X4 Astra. No held-out data. Never automatically grade.\n'
 with (a.output/'design.md').open('x',encoding='utf-8') as f:f.write(design)
 plan['design_sha256']=sha(a.output/'design.md')
 save(a.output/'frozen-plan.json',plan)
 print(json.dumps({'status':'FROZEN_NO_CALLS','root':str(root),'planned_calls':4,'source_baseline_sha256':plan['source_baseline_sha256'],'source_candidate_sha256':plan['source_candidate_sha256']}),flush=True)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Read-only compact source inventory. Declarations and lexical signals, not resolved/runtime evidence."""
import argparse,collections,json,re,xml.etree.ElementTree as ET
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('--format',choices=['json','markdown'],default='markdown');args=parser.parse_args();root=args.source.resolve()
if not root.is_dir():parser.error('source must be a readable directory')
skip={'.git','.codex','.agents','.claude','node_modules','target','dist','.m2','__pycache__'}
files=sorted(p for p in root.rglob('*') if p.is_file() and not any(x in skip for x in p.relative_to(root).parts))
rel=lambda p:p.relative_to(root).as_posix()
counts=collections.Counter(p.suffix.lower() or '[none]' for p in files)
out={'source':str(root),'coverage':{'files':len(files),'extensions':dict(counts.most_common()),'excluded_directory_names':sorted(skip),'limits':['Maven declarations include profiles; activation and resolved dependencies unknown','Lexical source signals require representative reading; no runtime or support conclusions']},'manifests':[],'binary_artifacts':[],'deployment_files':[]}
source_text={};internal_names=set();import_groups=collections.Counter();annotations=collections.Counter();imports_by_file={}
for p in files:
 if p.suffix=='.java':
  t=p.read_text(errors='replace');source_text[p]=t
  internal_names.update(re.findall(r'\b(?:class|interface|enum|record)\s+(\w+)',t))
  imports=re.findall(r'^\s*import\s+(?:static\s+)?([\w.*]+)\s*;',t,re.M);imports_by_file[p]=imports
  import_groups.update(set('.'.join(x.split('.')[:3]) for x in imports))
  annotations.update(re.findall(r'@(\w+)',t))
 if p.suffix.lower() in {'.jar','.war','.ear'}:out['binary_artifacts'].append({'path':rel(p),'bytes':p.stat().st_size})
 if p.name.lower().startswith(('jenkinsfile','dockerfile')) or p.name in {'web.xml','application.yml','application.yaml','application.properties'} or p.suffix in {'.yml','.yaml'}:out['deployment_files'].append(rel(p))
 if p.name=='pom.xml':
  try:
   tree=ET.fromstring(p.read_text());ns={'m':'http://maven.apache.org/POM/4.0.0'}
   for x in tree.iter():x.tag=x.tag.split('}')[-1]
   def fields(x,names):return {n:x.findtext(n) for n in names if x is not None and x.findtext(n) is not None}
   row={'path':rel(p),**fields(tree,['groupId','artifactId','version','packaging']),'parent':fields(tree.find('parent'),['groupId','artifactId','version']),'properties':{x.tag:x.text for x in tree.findall('./properties/*')},'modules':[x.text for x in tree.findall('./modules/module')], 'dependencies':[fields(x,['groupId','artifactId','version','scope','classifier','optional','systemPath']) for x in tree.findall('.//dependency')], 'plugins':[fields(x,['groupId','artifactId','version']) for x in tree.findall('.//plugin')]}
   out['manifests'].append(row)
  except Exception as e:out['manifests'].append({'path':rel(p),'error':type(e).__name__})
 if p.name=='package.json':
  try:
   d=json.loads(p.read_text());out['manifests'].append({'path':rel(p),**{k:d[k] for k in ['name','version','engines','scripts','dependencies','devDependencies'] if k in d},'lockfiles':[x.name for x in p.parent.glob('*lock*') if x.is_file()]})
  except Exception as e:out['manifests'].append({'path':rel(p),'error':type(e).__name__})
external=collections.defaultdict(list)
for p,t in source_text.items():
 for m in re.finditer(r'\b(?:extends|implements)\s+([\w.]+)',t):
  base=m.group(1);simple=base.split('.')[-1]
  if simple in internal_names:continue
  imports=[i for i in imports_by_file[p] if i.endswith('.'+simple)]
  external[base].append({'path':rel(p),'line':t.count('\n',0,m.start())+1,'imports':imports})
out['java_signals']={'files':len(source_text),'lines':sum(t.count('\n') for t in source_text.values()),'test_paths':[rel(p) for p in source_text if '/src/test/' in '/'+rel(p)],'import_groups_by_affected_file':dict(import_groups.most_common()),'annotation_occurrences':dict(annotations.most_common(45)),'external_inheritance_candidates':{k:{'matches':len(v),'examples':v[:3]} for k,v in sorted(external.items())}}
def markdown_report(data):
 lines=['# Source inventory','', 'Declarations and lexical signals only; resolved dependencies, runtime compatibility and upstream support are not verified.', '', '## Coverage', f"- Root: `{data['source']}`", f"- Files: {data['coverage']['files']}", '- Extensions: '+', '.join(f'{k}={v}' for k,v in data['coverage']['extensions'].items()), '- Excluded directory names: '+', '.join(data['coverage']['excluded_directory_names']), '', '## Build declarations']
 def scalar(v):return str(v).replace('|','\\|').replace('\n',' ')
 for m in data['manifests']:
  lines+=['',f"### `{m['path']}`"]
  if 'error' in m:lines+=['Parse error: '+m['error']];continue
  if m['path'].endswith('pom.xml'):
   lines+=['- Coordinates: '+':'.join(str(m.get(k,'[inherited/default]')) for k in ['groupId','artifactId','version']), '- Packaging: '+str(m.get('packaging','jar (Maven default)'))]
   if m.get('parent'):lines+=['- Parent: '+':'.join(str(m['parent'].get(k,'')) for k in ['groupId','artifactId','version'])]
   if m.get('modules'):lines+=['- Modules: '+', '.join(m['modules'])]
   if m.get('properties'):lines+=['- Properties: '+', '.join(k+'='+('[redacted]' if re.search('password|passwd|secret|token|credential|private.?key|api.?key',k,re.I) else scalar(v)) for k,v in m['properties'].items())]
   for kind in ['dependencies','plugins']:
    entries=m.get(kind,[])
    if not entries:continue
    lines+=['- '+kind+':']
    for d in entries:
     coordinate=':'.join(str(d.get(k,'[managed/default]')) for k in ['groupId','artifactId','version'])
     extras=', '.join(k+'='+scalar(d[k]) for k in ['scope','classifier','optional','systemPath'] if k in d)
     lines+=['  - '+coordinate+(' ('+extras+')' if extras else '')]
  else:
   for key in ['name','version','engines','scripts','dependencies','devDependencies','lockfiles']:
    if key in m:lines+=['- '+key+': '+(json.dumps(m[key],ensure_ascii=False) if isinstance(m[key],(list,dict)) else str(m[key]))]
 lines+=['','## Deployment/configuration paths']+['- `'+p+'`' for p in data['deployment_files']]
 lines+=['','## Binary artifacts']+['- `'+x['path']+'` ('+str(x['bytes'])+' bytes)' for x in data['binary_artifacts']]
 j=data['java_signals'];lines+=['','## Java signals',f"- Java files: {j['files']}; newline count: {j['lines']}",'- Test paths: '+(', '.join(j['test_paths']) or '[none found]'),'','### Import families (affected files)']
 lines+=['- '+k+': '+str(v) for k,v in j['import_groups_by_affected_file'].items()]
 lines+=['','### Annotation lexical occurrences']+['- '+k+': '+str(v) for k,v in j['annotation_occurrences'].items()]
 lines+=['','### External inheritance candidates (read examples before inferring impact)']
 for base,d in j['external_inheritance_candidates'].items():
  examples='; '.join('`'+e['path']+':'+str(e['line'])+'`'+(' imports '+', '.join(e['imports']) if e['imports'] else '') for e in d['examples'])
  lines+=['- '+base+': '+str(d['matches'])+' matches; '+examples]
 return '\n'.join(lines)+'\n'
print(json.dumps(out,ensure_ascii=False,separators=(',',':')) if args.format=='json' else markdown_report(out))

"""C5 syntax and exact source/input identities only. No scientific imports."""
from pathlib import Path
import hashlib,json,py_compile
UNIT=Path(__file__).resolve().parents[1]
def identity(p):
 h=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return {'bytes':n,'sha256':h.hexdigest()}
files={str(p.relative_to(UNIT)):identity(p) for p in sorted((UNIT/'code').glob('*.py'))}
for p in sorted((UNIT/'code').glob('*.py')):py_compile.compile(str(p),doraise=True)
for name in ('FROZEN_CONTRACT.md','THEORY.md','IMPLEMENTATION.md','inputs/SOURCE_IDENTITIES.json'):files[name]=identity(UNIT/name)
m=json.loads((UNIT/'inputs/SOURCE_IDENTITIES.json').read_text())
for item in m['files'].values():
 p=UNIT/item['path'];actual=identity(p)
 if actual!={k:item[k] for k in ('bytes','sha256')}:raise ValueError('INPUT_BYTE_IDENTITY:'+item['path'])
 files[item['path']]=actual
p=UNIT/'evidence/execution/C5_PREEXECUTION.json';p.write_text(json.dumps(dict(status='PREPARED_NOT_EXECUTED',files=files,syntax='PASS',scientific_execution=0,requested_model='gpt-6.1-sol/high',observed_runtime_model=None,primary_command=['python',str(UNIT/'code/run_bounded.py'),'primary'],figure_command=['python',str(UNIT/'code/run_bounded.py'),'figures']),indent=2,sort_keys=True)+'\n')
print(str(p));print('Syntax PASS; byte identities frozen; scientific execution 0')

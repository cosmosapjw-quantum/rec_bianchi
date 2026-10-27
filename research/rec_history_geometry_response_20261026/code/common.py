"""GEO01 serialization and immutable identity checks; no donor science imports."""
from pathlib import Path
import hashlib,json
import numpy as np
UNIT=Path(__file__).resolve().parents[1]
def serial(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,Path):return str(x)
 raise TypeError(type(x).__name__)
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False,default=serial)+'\n')
def identity(p):
 h=hashlib.sha256();n=0
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return {'bytes':n,'sha256':h.hexdigest()}
def source_snapshot():
 files={str(p.relative_to(UNIT)):identity(p) for p in sorted((UNIT/'code').glob('*.py'))}
 for name in ('FROZEN_CONTRACT.md','THEORY.md','IMPLEMENTATION.md','inputs/SOURCE_IDENTITIES.json'):
  p=UNIT/name
  if p.exists():files[name]=identity(p)
 m=json.loads((UNIT/'inputs/SOURCE_IDENTITIES.json').read_text())
 for item in m['files'].values():
  p=UNIT/item['path'];actual=identity(p)
  if actual!={k:item[k] for k in ('bytes','sha256')}:raise ValueError('IMMUTABLE_INPUT_CHANGED:'+item['path'])
  files[item['path']]=actual
 return files
def load(name,keys=None):
 with np.load(UNIT/'inputs'/name,allow_pickle=False) as a:return {k:a[k].copy() for k in (a.files if keys is None else keys)}
class Counter:
 def __init__(self,out):self.out=out;self.roots=0;self.decimal_roots=0;self.matvecs=0;self.interval=0;self.persist('START')
 def persist(self,phase):save(self.out/'ACTION_COUNTER.json',dict(phase=phase,ordinary_roots=self.roots,ordinary_root_cap=17528,decimal_roots=self.decimal_roots,decimal_root_cap=96,operator_actions=self.matvecs,operator_action_cap=5,interval_actions=self.interval,interval_action_cap=1,new_RHS=0,IVP=0,solves=0,inverses=0,native_build=0,old_campaign_replay=0))
 def root(self,decimal=False):
  k='decimal_roots' if decimal else 'roots';cap=96 if decimal else 17528
  if getattr(self,k)>=cap:raise RuntimeError('ROOT_CAP:'+k)
  setattr(self,k,getattr(self,k)+1)
 def apply(self,K,x,label):
  if self.matvecs>=5:raise RuntimeError('OPERATOR_CAP')
  self.matvecs+=1;self.persist('BEFORE_'+label);return K@x
 def interval_action(self):
  if self.interval:raise RuntimeError('INTERVAL_ACTION_CAP')
  self.interval+=1;self.persist('BEFORE_EXACT_INTERVAL')

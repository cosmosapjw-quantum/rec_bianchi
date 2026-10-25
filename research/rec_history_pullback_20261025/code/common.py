"""Serialization, raw-preserving counters and used-source identities."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
UNIT=Path(__file__).resolve().parents[1];WORK=UNIT.parents[1]
sys.path.insert(0,str(UNIT/'vendor'))

def serial(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,Path):return str(x)
 raise TypeError(type(x).__name__)
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False,default=serial)+'\n')
def identity(p):
 h=hashlib.sha256();size=0
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
 return {'bytes':size,'sha256':h.hexdigest()}
def paths():
 manifest=json.loads((UNIT/'inputs/PATH_MANIFEST.json').read_text());out={}
 for key,item in manifest['inputs'].items():
  p=Path(item['path']);out[key]=p if p.is_absolute() else UNIT/p
 return out

def used_files():
 out={f'input/{k}':v for k,v in paths().items()}
 for d in ('code','tests','vendor'):
  for p in sorted((UNIT/d).glob('*.py')):out[str(p.relative_to(UNIT))]=p
 out['inputs/PATH_MANIFEST.json']=UNIT/'inputs/PATH_MANIFEST.json'
 return out

def verify():
 expected=json.loads((UNIT/'inputs/EXECUTION_IDENTITIES.json').read_text())['files']
 actual={k:identity(p) for k,p in used_files().items()}
 if actual!=expected:raise ValueError('USED_SOURCE_OR_INPUT_BYTE_IDENTITY_MISMATCH')
 return actual

class Counter:
 def __init__(self,out):self.out=out;self.operator_actions=0;self.event_actions=0;self.interval_passes=0;self.records=[];self.persist('INITIAL')
 def persist(self,phase):save(self.out/'ACTION_COUNTER.json',{'phase':phase,'operator_actions':self.operator_actions,'operator_action_cap':256,'event_actions':self.event_actions,'event_action_cap':512,'interval_passes':self.interval_passes,'solves':0,'inverses':0,'linear_RHS':0,'native_build':0,'IVP':0,'records':self.records})
 def charge(self,label,event=False,count=1):
  name='event_actions' if event else 'operator_actions';limit=512 if event else 256
  if getattr(self,name)+count>limit:raise RuntimeError('POINT_ACTION_CAP:'+name)
  setattr(self,name,getattr(self,name)+count);self.records.append({'label':label,'kind':name,'count':count});self.persist('BEFORE_'+label)
 def apply(self,label,A,x,event=False):
  count=A.shape[0] if event and A.ndim==2 else 1;self.charge(label,event,count);return A@x
 def interval(self,label):self.interval_passes+=1;self.persist('INTERVAL_'+label)

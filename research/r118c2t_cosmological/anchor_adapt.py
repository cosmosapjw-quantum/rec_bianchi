"""Bounded adaptive inverse-temperature anchors; four original source blocks."""
import sys,hashlib,json
from pathlib import Path
import numpy as np
from full_bianchi_hyrec.recoil.calibrated_source import Bath,_job
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'r118c2s_evolving'))
from evolving import ActualBath
H=Path('/home/cosmosapjw/Downloads/rec_r118c2f_compiled_final')
st=json.loads((H/'STATES.json').read_text())['states'];hist=json.loads((H/'z900_HISTORY.json').read_text())['states'];bh=ActualBath(hist,st['z1100'])
pairs=[(0,0),(0,1),(7,16),(10,28)]
cache={};receipts=[]
def point(z):
 if z not in cache:
  r=bh.point(z);b=Bath(r['T_m_K'],r['n1s'])
  data=np.stack([_job((*p,b,(4,)))[2][4] for p in pairs])
  assert np.min(data)>=0 and np.all(np.isfinite(data))
  cache[z]=(r,data/r['n1s'])
  print('direct anchor',z,flush=True)
 return cache[z]
def interpolate(z,l,h):
 a,x=point(l);b,y=point(h);m,v=point(z)
 t=-1/m['T_m_K'];t0=-1/a['T_m_K'];t1=-1/b['T_m_K'];r=(t-t0)/(t1-t0)
 pos=(x>0)&(y>0);p=(1-r)*x+r*y;p[pos]=np.exp((1-r)*np.log(x[pos])+r*np.log(y[pos]))
 er=np.sum(abs(p-v),axis=(1,2))/np.maximum(np.sum(v,axis=(1,2)),1e-300)
 return er.tolist()
# midpoint-driven adaptive sampling. A second quarter-point check on final
# intervals is independent of the midpoint acceptance test.
target=1e-3;stack=[(900.,1300.,0)];leaves=[]
while stack:
 l,h,depth=stack.pop();m=(l+h)/2
 er=interpolate(m,l,h);row=dict(lo=l,hi=h,mid=m,depth=depth,errors=er)
 if max(er)<=target:
  row['status']='MIDPOINT_ACCEPT';leaves.append(row)
 elif depth>=4:
  row['status']='CAP_UNRESOLVED';leaves.append(row)
 else:
  row['status']='REFINE';stack.extend([(m,h,depth+1),(l,m,depth+1)])
 receipts.append(row)
for r in leaves:
 l,h=r['lo'],r['hi'];r['quarter_holdouts']=[dict(z=z,errors=interpolate(z,l,h)) for z in (l+(h-l)/4,l+3*(h-l)/4)]
 r['holdout_max']=max(max(x['errors']) for x in r['quarter_holdouts'])
 r['holdout_status']='PASS_SAMPLED' if r['holdout_max']<=target else 'FAIL_SAMPLED'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out=dict(status='BOUNDED_ADAPTIVE_SUBSET',target=target,pairs=pairs,direct_temperatures=len(cache),rows=receipts,leaves=leaves,history_sha=sha(H/'z900_HISTORY.json'),states_sha=sha(H/'STATES.json'),scope='four original q4 source blocks only; no full graph or continuous error certificate')
np.savez_compressed(D/'ANCHOR_BLOCKS.npz',**{str(z):v[1] for z,v in cache.items()})
(D/'ANCHORS.json').write_text(json.dumps(out,indent=2)+'\n')
print('direct',len(cache),'leaves',len(leaves),'holdout fail',sum(r['holdout_status']=='FAIL_SAMPLED' for r in leaves),'max holdout',max(r['holdout_max'] for r in leaves),flush=True)

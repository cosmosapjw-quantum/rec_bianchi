"""Independent replay of weighted arrival, actual source jump and scalar response weights."""
from pathlib import Path
import json,sys,numpy as np
from scipy.optimize import brentq
D=Path(__file__).resolve().parent;P=D.parent;F=P/'r118c4f_causal_mesh';W=P/'r118c3w_common_history'
sys.path[:0]=[str(W),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,Map,p,JumpResponse
c=context(128);m0=json.loads((D/'MESH.json').read_text());q=np.load(F/'causal_q3_128_0.npz');old=q['he'];rows=q['rows'];A=q['all_history'][:,0];z=np.load(D/'WEIGHTED_MESH.npz');he=z['he'];srcset=z['source_indices'];assert np.array_equal(old,z['old'])
maps={lam:Map(c,lam) for lam in [-.5,0.,.5]};out=[]
for r in m0['records']:
 if r['kind']!='weighted':continue
 i=r['index'];j=r['source_index'];ch=r['channel'];ray=r['ray'];lam=r['lam'];t=r['time'];f=maps[lam].f[ray];l,h=old[i:i+2];s=float(f(old[j]));root=brentq(lambda u:float(f(u))-s-c.lr[ch],l,h,xtol=1e-15,rtol=1e-15)
 x=float(np.interp(root,old,rows[:,1]));T=float(np.interp(root,old,rows[:,2]));snap,_,_=c.snap(root,x,T,c.zero);a,w=maps[lam].state(root);jr=JumpResponse(snap,a,w)
 # Compare approximate scalar ranking weight to exact instantaneous ray-specific gas response magnitude.
 d=np.zeros((c.nr,313));k=c.src[ch];left=np.polynomial.legendre.legval(-1.,A[j,k]);right=0. if j==0 else np.polynomial.legendre.legval(1.,A[j-1,k]);d[ray,ch]=left-right
 value=abs(jr.apply(d)[2]);out.append(dict(index=i,source_index=j,channel=ch,ray=ray,lam=lam,arrival=float(t),brentq=float(root),time_abs=abs(root-t),weight_proxy=r['weight'],actual_instantaneous_gas_rate_abs=float(value),outgoing_jump=float(d[ray,ch])))
assert len(out)==m0['weighted'] and max(x['time_abs'] for x in out)<1e-12
proxy=np.array([x['weight_proxy'] for x in out]);actual=np.array([x['actual_instantaneous_gas_rate_abs'] for x in out]);mask=(proxy>0)&(actual>0)
ratio=actual[mask]/proxy[mask];obj=dict(rows=out,n=len(out),max_arrival_abs=float(max(x['time_abs'] for x in out)),n_positive=int(sum(mask)),ratio_quantiles=np.quantile(ratio,[0,.1,.5,.9,1]).tolist(),log_weight_correlation=float(np.corrcoef(np.log(proxy[mask]),np.log(actual[mask]))[0,1]),scope='actual scalar outgoing boundary jumps, instantaneous ray-specific affine native gas response at interpolated C4F scalar gas state; not a true global error estimator or signed history jump')
(D/'WEIGHT_REPLAY.json').write_text(json.dumps(obj,indent=2)+'\n');print({k:v for k,v in obj.items() if k!='rows'},flush=True)


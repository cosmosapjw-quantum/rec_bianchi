"""Independently re-root selected causal arrivals and recover the actual adjoint weights."""
from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import brentq
D=Path(__file__).resolve().parent;P=D.parent;G=P/'r118c4g_weighted_arrivals'
sys.path[:0]=[str(P/'r118c3w_common_history'),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,Map
c=context(128);g=np.load(D/'GOAL_MESH.npz');q=np.load(G/'weighted_q3_128_0.npz');old=q['he'];A=q['all_history'][:,0];ib=g['adjoint_incoming'];assert np.array_equal(g['old'],old)
m={l:Map(c,l) for l in [-.5,0.,.5]};meta=json.loads((D/'GOAL_MESH.json').read_text());rows=[]
for r in meta['records']:
 if r['kind']!='goal':continue
 k=r['index'];j=r['source'];ch=r['channel'];ray=r['ray'];l,h=old[k:k+2];f=m[r['lam']].f[ray];want=float(f(old[j]))+c.lr[ch]
 x=brentq(lambda u:float(f(u))-want,l,h,xtol=1e-15,rtol=1e-15)
 col=c.src[ch];jump=np.polynomial.legendre.legval(-1.,A[j,col])-(np.polynomial.legendre.legval(1.,A[j-1,col]) if j else 0.)
 ww=abs(jump*ib[k,ch])*c.w[ray]
 rows.append(dict(index=k,source=j,arrival_abs=float(abs(x-r['time'])),forward_residual=float(abs(float(f(r['time']))-want)),weight=float(ww),weight_saved=r['weight'],weight_relative=float(abs(ww-r['weight'])/max(abs(ww),abs(r['weight']),1e-300))))
assert len(rows)==meta['weighted'] and max(x['arrival_abs'] for x in rows)<1e-12
z=dict(rows=rows,n=len(rows),max_arrival_abs=max(x['arrival_abs'] for x in rows),max_forward_residual=max(x['forward_residual'] for x in rows),max_weight_relative=max(x['weight_relative'] for x in rows),scope='independent Brent root and actual scalar source jump/adjoint weight on chosen cell; no global error bound')
(D/'GOAL_REPLAY.json').write_text(json.dumps(z,indent=2)+'\n');print({k:v for k,v in z.items() if k!='rows'},flush=True)

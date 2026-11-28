"""Independent forward-map replay of selected causal arrivals (not a nonzero-jump proof)."""
from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import brentq
D=Path(__file__).resolve().parent;P=D.parent
sys.path[:0]=[str(P/'r118c3w_common_history'),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context,Map
c=context(128);z=np.load(D/'CAUSAL_MESH.npz');old=z['old'];he=z['he'];meta=json.loads((D/'MESH.json').read_text());maps={l:Map(c,l) for l in [-.5,0.,.5]}
rows=[]
for r in meta['records']:
 if r['generation']==0:continue
 j=r['ray'];f=maps[r['lam']].f[j];s=float(f(old[0]));t=r['time'];wanted=float(f(t))-s
 if r['generation']==1:
  idx=int(np.argmin(abs(c.lr-wanted)));lag=float(c.lr[idx]);channels=[idx]
 else:
  v=c.lr[:,None]+c.lr[None,:];i,k=np.unravel_index(np.argmin(abs(v-wanted)),v.shape);lag=float(v[i,k]);channels=[int(i),int(k)]
 l,h=old[r['index']:r['index']+2];q=brentq(lambda u:float(f(u))-s-lag,l,h,xtol=1e-15,rtol=1e-15);rows.append(dict(index=r['index'],generation=r['generation'],ray=j,lam=r['lam'],channels=channels,arrival=t,forward_residual=float(abs(wanted-lag)),inverse_vs_brentq=float(abs(q-t))))
assert len(rows)==meta['first']+meta['second'] and max(x['forward_residual'] for x in rows)<1e-12
out=dict(n=len(rows),max_forward_residual=max(x['forward_residual'] for x in rows),max_inverse_vs_brentq=max(x['inverse_vs_brentq'] for x in rows),selected_defect_variation_fraction=float(np.sum(z['score'][z['selected']])/np.sum(z['score'])),min_spacing=float(min(np.diff(he))),rows=rows,scope='same-ray positive lag arrivals of initial history boundary, independently re-rooted against original forward map; second generation only kinematic candidates')
(D/'ARRIVAL_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='rows'},flush=True)


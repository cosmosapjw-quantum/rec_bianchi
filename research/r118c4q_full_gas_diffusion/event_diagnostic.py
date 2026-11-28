"""Source-owned event crossing diagnostic for early minus-direction secant discrepancy."""
from pathlib import Path
import numpy as np,json,hashlib
from history import context,Map,Events
D=Path(__file__).resolve().parent;P=D.parent
def main():
 c=context(128);f=P/'r118c4h_goal_adjoint/goal_q3_128_-0.5.npz';z=np.load(f);he=z['he'];c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he
 m=Map(c,-.5);ev=Events(m);ps=[-3e-4,-1e-4,-6e-5,-3e-5,-1e-5,1e-5,6e-5,3e-4];maps=[Map(c,-.5+p) for p in ps]
 rows=[]
 for step in [46,63,74,75,98,99,100,126,128]:
  for side,i in [('left',step-1),('right',step)]:
   u=he[i];t,dt=ev.td(u);kn=he[:step];base=np.searchsorted(kn,t+2e-14,side='right')-1
   j0=np.searchsorted(kn,t);jl=np.clip(j0-1,0,len(kn)-1);jr=np.clip(j0,0,len(kn)-1);j=np.where(abs(t-kn[jl])<abs(t-kn[jr]),jl,jr);diff=kn[j]-t
   vals=[];prev=None
   for p,mm in zip(ps,maps):
    tt=mm.t(u);k=np.searchsorted(kn,tt+2e-14,side='right')-1;mask=k!=base
    vals.append(dict(p=p,changed=int(mask.sum()),max_shift=float(np.max(abs(tt-t))),examples=[dict(ray=int(a),channel=int(b),base_knot=int(base[a,b]),new_knot=int(k[a,b]),distance=float(diff[a,b]),linear_crossing_est=float(diff[a,b]/dt[a,b]) if abs(dt[a,b])>1e-300 else None) for a,b in np.argwhere(mask)[:10]]))
   km=np.searchsorted(kn,maps[2].t(u)+2e-14,side='right')-1;kp=np.searchsorted(kn,maps[3].t(u)+2e-14,side='right')-1
   changed=np.argwhere(km!=kp);rows.append(dict(step=step,side=side,minus_transition_3e5_to_6e5=int(len(changed)),transition_examples=[dict(ray=int(a),channel=int(b),small_knot=int(kp[a,b]),large_knot=int(km[a,b]),distance=float(diff[a,b]),linear_crossing_est=float(diff[a,b]/dt[a,b]) if abs(dt[a,b])>1e-300 else None) for a,b in changed[:24]],samples=vals))
 (D/'EVENT_DIAGNOSTIC.json').write_text(json.dumps(dict(rows=rows,baseline_sha=hashlib.sha256(f.read_bytes()).hexdigest(),scope='actual retarded source-knot index at selected receiving endpoints, same spline map, no exhaustive interior quadrature topology or causal proof of error'),indent=2,allow_nan=False)+'\n')
 print(json.dumps([dict(step=x['step'],side=x['side'],transitions=x['minus_transition_3e5_to_6e5'],examples=x['transition_examples'][:2]) for x in rows],indent=2))
if __name__=='__main__':main()

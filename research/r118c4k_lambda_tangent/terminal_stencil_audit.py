"""Geometry-only terminal stencil refinement; finite polynomial fixture, not the atomic solution."""
from pathlib import Path
import rec,numpy as np,json
from moving import Moving
c=rec.context(128);z=np.load(rec.H/'goal_q3_128_-0.5.npz');he=z['he']
c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he
m=rec.Map(c,-.5);rng=np.random.default_rng(118)
A=np.broadcast_to(rng.normal(size=(1,c.nr,314,7))*1e-15,(len(he)-1,c.nr,314,7));DA=np.broadcast_to(np.zeros((1,1,314,7)),A.shape)
i=1773;l,r=he[-2:];rows=[]
for h in [1e-3,1e-4,1e-5]:
 mm,mp=[rec.Map(c,lam) for lam in [-.5-h,-.5+h]];p=Moving(m,mm,mp,h)
 u,du,ev,md=p.integrate(i,l,r,A,DA);fd=(mp.mom3(i,l,r,A)-mm.mom3(i,l,r,A))/(2*h)
 err=float(np.linalg.norm(du-fd)/np.linalg.norm(fd))
 assert np.isfinite(du).all()
 rows.append(dict(h=h,events=ev,relative=err,implicit_fallback_count=len(p.endpoint_fallback),norm=float(np.linalg.norm(du))))
out=dict(rows=rows,scope='Actual terminal grid, geometry and polynomial fixture only; verify derivative regularization and shrinking finite-difference error without rerunning atomic history.')
Path('TERMINAL_STENCIL_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)

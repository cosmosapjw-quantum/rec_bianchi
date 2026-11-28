"""Reproduce the 1773-step terminal map case without atomic recomputation."""
from pathlib import Path
import rec,numpy as np,json,time
from moving import Moving
c=rec.context(128);z=np.load(rec.H/'goal_q3_128_-0.5.npz');he=z['he']
c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he
m,mm,mp=[rec.Map(c,l) for l in [-.5,-.501,-.499]]
# Deterministic nonzero degree-6 polynomial fixture; actual geometry and full grid.
rng=np.random.default_rng(118);A=np.broadcast_to(rng.normal(size=(1,c.nr,314,7))*1e-15,(len(he)-1,c.nr,314,7));DA=np.broadcast_to(np.zeros((1,1,314,7)),A.shape)
p=Moving(m,mm,mp,.001);rows=[]
for i in [1664,1728,1772,1773]:
 l,r=he[i-1:i+1];u,du,ev,md=p.integrate(i,l,r,A,DA);ref=m.mom3(i,l,r,A)
 gap=np.linalg.norm(u-ref)/max(np.linalg.norm(ref),1e-300)
 fd=(mp.mom3(i,l,r,A)-mm.mom3(i,l,r,A))/.002
 assert np.isfinite(du).all() and gap<1e-10
 rows.append(dict(step=i,nominal_gap=float(gap),moving_FD_relative=float(np.linalg.norm(du-fd)/max(np.linalg.norm(fd),1e-300)),events=ev,min_boundary_distance=md))
assert {(x['ray'],x['channel']) for x in p.endpoint_fallback}=={(8,41),(12,41),(16,41),(20,41),(14,276),(18,276)} and max(abs(x['inverse_residual']) for x in p.endpoint_fallback)<1e-12
out=dict(rows=rows,fallback=p.endpoint_fallback,scope='Actual full-grid geometry with deterministic polynomial fixture; repair terminal auxiliary derivative, not full atomic tangent.')
Path('TERMINAL_REPAIR_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

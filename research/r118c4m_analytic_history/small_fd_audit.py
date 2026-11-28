from pathlib import Path
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent
z=np.load(D.parent/'r118c4h_goal_adjoint/goal_q3_128_-0.5.npz');v=z['rows'][:129,1:3].copy();v[:,1]/=3000
a=np.load(D/'PREFIX.npz');assert len(a['u'])>=129
dy=a['dy'][:129]
rows=[]
for h in [-1e-5,1e-5,-3e-5]:
 p=D/f'SMALL_FD_{h:g}.npz';q=np.load(p);assert np.array_equal(q['u'],z['he'][:129]) and len(q['y'])==129
 j=int(h<0);fd=(q['y']-v)/abs(h);gap=fd-dy[:,j]
 rows.append(dict(h=h,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),steps=128,step63_analytic=dy[63,j].tolist(),step63_fd=fd[63].tolist(),step99_analytic=dy[99,j].tolist(),step99_fd=fd[99].tolist(),step99_gap=gap[99].tolist(),max_gap=np.max(abs(gap),axis=0).tolist(),peak_step=np.argmax(abs(gap),axis=0).tolist(),terminal_gap=gap[-1].tolist()))
out=dict(rows=rows,scope='Independent nonlinear signed 128-step gas/spectral paths on original full clock and nominal C4H history; prefix only, floating point cancellation in tiny finite difference; no continuum or differentiability claim.')
(D/'SMALL_FD_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

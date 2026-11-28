"""Independent sensitivity-scale and floating-resolution audit; no tangent result assumed."""
from pathlib import Path
import json,hashlib,numpy as np
D=Path(__file__).resolve().parent
m0=D/'FD_-0.003.npz';p0=D/'FD_0.003.npz';m=np.load(m0);p=np.load(p0)
assert np.array_equal(m['u'],p['u'])
u=m['u'];h=.003;dy=(p['y']-m['y'])/(2*h);rows=[]
for j,k in enumerate(['xHII','T_over_3000K']):
 i=int(np.argmax(abs(dy[:,j])))
 ulp=max(np.spacing(abs(p['y'][-1,j])),np.spacing(abs(m['y'][-1,j])))
 delta=p['y'][-1,j]-m['y'][-1,j]
 rows.append(dict(component=k,peak_step=i,peak_z=float(np.expm1(-u[i])),peak_FD=float(dy[i,j]),terminal_FD=float(dy[-1,j]),terminal_delta=float(delta),terminal_ulp=float(ulp),terminal_delta_ulps=float(delta/ulp),derivative_per_ulp=float(ulp/(2*h))))
r=dict(h=h,rows=rows,limiter_steps=np.unique(m['limits'][:,0]).astype(int).tolist(),same_limiter_keys=bool(np.array_equal(m['limits'][:,:3],p['limits'][:,:3])),sha256={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (m0,p0)},scope='FD resolution diagnostic, not a certified total finite-difference error bound; T derivative is in the stored normalized coordinate.')
(D/'FD_RESOLUTION.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))

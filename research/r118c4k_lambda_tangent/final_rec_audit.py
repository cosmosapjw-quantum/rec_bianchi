"""Compare two full executed tangent constructions with independent nonlinear replay."""
from pathlib import Path
import json,hashlib,numpy as np
D=Path(__file__).resolve().parent
ref=D.parent/'r118c4h_goal_adjoint'/'goal_q3_128_-0.5.npz'
z=np.load(ref);base=z['rows'][:,1:3].copy();base[:,1]/=3000
m=np.load(D/'FD_-0.003.npz');p=np.load(D/'FD_0.003.npz')
assert len(z['he'])==1774 and np.array_equal(m['u'],z['he']) and np.array_equal(p['u'],z['he'])
dy=(p['y']-m['y'])/.006;dh=(p['last']-m['last'])/.006;rows=[]
for tag in ['TANGENT','DIRECT_FULL_TANGENT']:
 a=json.loads((D/(tag+'.json')).read_text());t=np.load(D/(tag+'.npz'))
 assert a['steps']==1773 and np.array_equal(t['u'],z['he']) and np.array_equal(t['y'],base)
 assert np.isfinite(t['dy']).all() and np.isfinite(t['last_tangent']).all()
 assert np.array_equal(t['limits'][:,:3],z['limits'][:,[0,2,3]])
 d=t['dy'];e=abs(d-dy);den=np.linalg.norm(dh);peak=np.max(abs(dy),axis=0)
 rows.append(dict(method=tag,steps=a['steps'],terminal_tangent=d[-1].tolist(),terminal_FD=dy[-1].tolist(),terminal_gap=e[-1].tolist(),max_history_gap=e.max(axis=0).tolist(),peak_FD=peak.tolist(),history_peak_scaled_gap=(e.max(axis=0)/np.maximum(peak,1e-300)).tolist(),final_history_relative_to_FD=float(np.linalg.norm(t['last_tangent']-dh)/max(den,1e-300)),final_history_FD_norm=float(den),max_nominal_residual=a['resmax'],min_positive=a['min_positive'],limited_cells=a['limited'],same_limiter_keys=bool(np.array_equal(t['limits'][:,:3],m['limits'][:,:3]) and np.array_equal(t['limits'][:,:3],p['limits'][:,:3])),endpoint_fallback=a.get('endpoint_fallback',[]),source_sha256=hashlib.sha256((D/(tag+'.npz')).read_bytes()).hexdigest()))
out=dict(rows=rows,scope='Both actual complete 1773-step calculations, compare against independently completed nonlinear lambda +/-0.003. The direct-map method uses finite geometry stencils, not analytic node-wise differentiation. Temperature FD terminal difference only 2 ULP; not a reliable high-precision thermal validation.',prefix_stencil_audit=json.loads((D/'PREFIX_FD_AUDIT.json').read_text()),direct_prefix_audit=json.loads((D/'DIRECT_MAP_PREFIX_AUDIT.json').read_text()))
(D/'FINAL_REC_COMPARISON.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

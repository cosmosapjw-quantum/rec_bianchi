"""Compare matched recomputation vs original prefix; independent accepted gas residual."""
from pathlib import Path
import json,numpy as np
D=Path(__file__).resolve().parent
def run():
 orig=np.load(D.parent/'r118c2w_causal/FULL_128.npz');rows={};checks={}
 for p in sorted(D.glob('full*.npz')):
  z=np.load(p);a=z['rows'];assert np.all(np.diff(a[:,0])>0) and np.all(a[:,7]>0)
  res=np.diff(a[:,1])-np.diff(a[:,0])*a[1:,4];checks[p.stem]=float(np.max(abs(res)));assert checks[p.stem]<1e-12
 for k in [128,256,512]:
  for ray in ['', '_32ray']:
   files=[D/f'full{k}{ray}_{i}.json' for i in [0,1]]
   if not all(p.exists() for p in files):continue
   a,b=[json.loads(p.read_text()) for p in files]
   for j in ['prefix_sha','geometry_sha','rates_sha','steps','rays','order']:assert a[j]==b[j]
   rows[f'{k}{ray}']=dict(delta_join=b['join_x']-a['join_x'],delta_final=b['x']-a['x'],delta_late_increment=(b['x']-b['join_x'])-(a['x']-a['join_x']),isotropic_join_minus_old=a['join_x']-float(orig['xHII'][63]),isotropic_final_minus_old=a['x']-float(orig['xHII'][128]),max_root=max(a['max_xres'],b['max_xres']),max_atomic=max(a['max_atom_res'],b['max_atom_res']))
 o=dict(rows=rows,checks=checks,scope='regenerated represented prefix from same first x,T; not original coarse solver reproduction; conditional zero earlier distortion and fixed geometry')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()

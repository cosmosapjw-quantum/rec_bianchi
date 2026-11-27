"""Independent audit of common baseline and paired finite-amplitude saved results."""
import json,numpy as np,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
def read(f):return json.loads(f.read_text())
def run():
 bases={};data={}
 for n in [32,64,128]:
  j=read(D/f'base_{n}.json');z=np.load(D/f'base_{n}.npz');a=z['rows'];assert np.array_equal(z['he'],a[:,0]) and a[-1,1]==j['final_x'] and np.isfinite(a).all()
  assert j['max_root']<1e-15 and j['min_full_virtual_ratio']>0
  bases[str(n)]=j
 for f in sorted(D.glob('pair_*.json')):
  j=read(f);z=np.load(f.with_suffix('.npz'));a=z['rows'];assert a[-1,1]==j['dx'] and np.isfinite(a).all() and j['min_full_virtual_ratio']>0
  assert j['max_reference_residual']<1e-15 and j['max_root']<1e-15
  data[int(j['nt']),float(j['lambda_'])]=j
 rows=[]
 for n in [32,64,128]:
  if (n,0) not in data:continue
  z=data[n,0]['dx']
  for ep in [.25,.5]:
   if (n,ep) not in data or (n,-ep) not in data:continue
   a,b=data[n,ep],data[n,-ep];rows.append(dict(nt=n,eps=ep,even=(a['dx']+b['dx']-2*z)/(2*ep**2),odd=(a['dx']-b['dx'])/(2*ep),zero=z,reference_residual=max(a['max_reference_residual'],b['max_reference_residual']),min_full_ratio=min(a['min_full_virtual_ratio'],b['min_full_virtual_ratio']),limited=[a['limited_cells'],b['limited_cells']]))
 direct=read(D/'direct_32_0.5.json');y=direct['final_x']-bases['32']['final_x'];pair=data[32,.5]['dx'];dz=np.load(D/'direct_32_0.5.npz');bz=np.load(D/'base_32.npz');pz=np.load(D/'pair_32_0.5.npz')
 err=np.max(abs(dz['rows'][:,1]-bz['rows'][:,1]-pz['rows'][:,1]))
 out_rel=np.linalg.norm(dz['M'][-1]-bz['M'][-1]-pz['final_out'])/np.linalg.norm(pz['final_out'])
 chain={f.stem:read(f) for f in D.glob('CHAIN_*.json')};assert len(chain)==3
 for x in chain.values():assert x['partition_abs']<1e-13 and x['clock_residual']<1e-11
 out=dict(baselines=bases,pair_count=len(data),rows=rows,direct_delta=y,paired_delta=pair,direct_pair_abs=abs(y-pair),max_path_direct_pair_abs=float(err),terminal_outgoing_relative=float(out_rel),chain=chain,scope='common discrete gas/history integrator, exact weak-moment quadratic positivity correction when needed; fixed H only. Direct comparison independently solved at nt32 +.5. No continuum or HHe donor claim.')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(rows=rows,pair_count=len(data),direct_delta=y,paired_delta=pair,direct_pair_abs=abs(y-pair),max_path_direct_pair_abs=float(err),terminal_outgoing_relative=float(out_rel)),indent=2))
if __name__=='__main__':run()

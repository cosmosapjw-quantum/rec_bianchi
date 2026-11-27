"""Audit final combined polynomial after exact signed lower moment replacement.
Re-execute existing integrator; preserve original output and compare trajectory.
"""
from pathlib import Path
import sys,json,numpy as np
from numpy.polynomial.legendre import legval,legder,legroots
D=Path(__file__).resolve().parent
from arrival_pair import pair
source=(D/'arrival_pair.py').read_text()
token='  rec=np.array([B[i-1,...,0]'
assert source.count(token)==1
audit='''  # Certify the actual stored full polynomial using lower Planck floor.
  stored=(base+B[i-1])[...,:311,:].copy()
  stored[...,0]+=fr
  stored/=fr[None,:,None]
  pa,pb,pc=stored[...,0],stored[...,1],stored[...,2]
  y=np.clip(np.divide(-pb,3*pc,out=np.zeros_like(pb),where=pc!=0),-1,1)
  lower=np.minimum(np.minimum(pa-pb+pc,pa+pb+pc),pa+pb*y+pc*(3*y*y-1)/2)
  for ii,jj in np.argwhere(np.any(stored[...,3:]!=0,axis=-1)):
   coeff=stored[ii,jj];roots=legroots(legder(coeff))
   roots=roots.real[(abs(roots.imag)<1e-10)&(abs(roots.real)<1)]
   lower[ii,jj]=np.min(legval(np.r_[-1,1,roots],coeff))
  cert['min_stored_full_ratio']=min(cert['min_stored_full_ratio'],float(np.min(lower)))
  cert['cells_checked']+=int(lower.size)
  cert['steps_checked']+=1
  assert np.all(lower>0), (i,float(np.min(lower)))
'''
source=source.replace(token,audit+token)
assert source.count("np.savez_compressed(D/f'pair_")==1
source=source.replace("np.savez_compressed(D/f'pair_","np.savez_compressed(D/f'cert_pair_")
source=source.replace("write(f'pair_","write(f'cert_pair_")
lam=float(sys.argv[1]); cert=dict(min_stored_full_ratio=float('inf'),cells_checked=0,steps_checked=0)
ns={'__file__':str(D/'arrival_pair.py'),'__name__':'certify_audit','cert':cert,'legval':legval,'legder':legder,'legroots':legroots}
exec(compile(source,str(D/'arrival_pair.py'),'exec'),ns)
ns['pair'](32,lam)
with np.load(D/f'pair_32_{lam:g}.npz') as a, np.load(D/f'cert_pair_32_{lam:g}.npz') as b:
 cert['trajectory_bitwise_equal']=bool(np.array_equal(a['rows'],b['rows']))
 cert['last_signed_bitwise_equal']=bool(np.array_equal(a['last_signed'],b['last_signed']))
 assert cert['trajectory_bitwise_equal'] and cert['last_signed_bitwise_equal']
cert.update(lam=lam,scope='stored combined virtual-channel polynomial, all 284 cells, same conservative endpoint Planck floor; real line entries excluded')
(D/f'FINAL_POS_{lam:g}.json').write_text(json.dumps(cert,indent=2)+'\n')
print(cert,flush=True)

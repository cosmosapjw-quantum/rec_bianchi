"""Second-method same-author scipy.integrate.quad vs Gaussian series integrated RT."""
import json
import math
from pathlib import Path
import sys
from scipy.integrate import quad
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'src'))
from j1_cmb_rt import load_pinned,line_state,spectrum
src,_=load_pinned(R/'input')
rows=[]
for T,z,n in [(50,0,'1'),(50,30,'10000'),(100,50,'10000'),(200,50,'1000000')]:
 for N in ('1e14','1e16','1e18'):
  s=line_state(src,T,z,n,'0.5');row,*_=spectrum(s,N)
  tau0=row['tau0']; f=lambda x: -math.expm1(-tau0*math.exp(-x*x))
  integral,err=quad(f,-12,12,epsabs=1e-14,epsrel=3e-13)
  factor=integral/(tau0*math.sqrt(math.pi))
  diff=abs(factor-row['gaussian_saturation_factor'])
  if diff>2e-11:raise RuntimeError(f'Independent Gaussian quad mismatch {T,z,N,diff}')
  rows.append(dict(Tgas=T,z=z,nH2=n,N_HD=N,tau0=tau0,series=row['gaussian_saturation_factor'],quad=factor,abs_diff=diff))
out=R/'results/INDEPENDENT_QUAD_12.json';out.write_text(json.dumps(rows,indent=2)+'\n')
print('SCIPY_QUAD_PASS',len(rows),'max_abs_diff',max(r['abs_diff'] for r in rows))

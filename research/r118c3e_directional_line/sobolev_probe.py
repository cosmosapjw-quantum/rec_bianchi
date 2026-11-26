import numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
m,w=leggauss(128);a=1+.2*(3*m*m-1)
rows=[]
for tau in (0.01,.1,1.,10.,100.,1e8):
 # directional escape ratio divided by optically thick scalar rate
 avg=float(w@(a*(-np.expm1(-tau/a)))/2)
 # strictly concave a(1-exp(-tau/a)), so mean <= scalar
 iso=-np.expm1(-tau);assert avg<=iso+1e-14
 rows.append(dict(tau=tau,avg=avg,isotropic=iso,relative=avg/iso-1))
print(rows);(D/'SOBOLEV.json').write_text(json.dumps(rows,indent=2)+'\n')

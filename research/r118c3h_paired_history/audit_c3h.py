"""Paired-history error split: actual vs coarse quadrature on a fine accepted path."""
import numpy as np,json
from pathlib import Path
from paired_interp import pair_residual
D=Path(__file__).resolve().parent
def load(mode,n):
 a,b=[np.load(D/f'{mode}{n}_{i}.npz')['rows'] for i in [0,1]]
 assert a.shape==b.shape and np.array_equal(a[:,0],b[:,0])
 return b,a
def quad(t,f):return np.sum(np.diff(t)*(f[1:]+f[:-1])/2,dtype=np.longdouble)
def main():
 pairs={};splits=[]
 for m in ['linear','pchip']:
  for n in [256,512,1024]:
   a,b=load(m,n);p=pair_residual(a,b)
   meta=[json.loads((D/f'{m}{n}_{i}.json').read_text()) for i in [0,1]]
   for key in ['prefix_sha','geometry_sha','rates_sha','rays','steps','method','interpolation']:assert meta[0][key]==meta[1][key]
   assert p['max_pair_res']<1e-12
   pairs[f'{m}{n}']=p
  for n in [256,512]:
   a,b=load(m,n);c,d=load(m,2*n)
   t=a[:,0].astype(np.longdouble);tf=c[:,0].astype(np.longdouble)
   assert np.max(abs(t-tf[::2]))<1e-14
   f=a[:,3].astype(np.longdouble)-b[:,3];g=c[:,3].astype(np.longdouble)-d[:,3]
   actual=(a[-1,1]-b[-1,1])-(c[-1,1]-d[-1,1])
   quadrature=quad(tf[::2],g[::2])-quad(tf,g)
   path=quad(t,f)-quad(tf[::2],g[::2])
   residual=actual-quadrature-path
   splits.append(dict(mode=m,coarse=n,fine=2*n,actual=float(actual),quadrature_on_fine=float(quadrature),evolved_path=float(path),decomposition_residual=float(residual),max_coincident_rhs_difference=float(np.max(abs(f-g[::2])))))
   assert abs(residual)<1e-13
 result=dict(pairs=pairs,splits=splits,scope='a posteriori trapezoid quadrature vs evolved-path discrepancy on same accepted grids; not an error bound on exact physical delta')
 (D/'PAIR_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

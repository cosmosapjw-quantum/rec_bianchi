"""Audit logged positivity-cell locations and exact polynomial reconstruction on manufactured positive fields."""
import numpy as np,json,sys
from pathlib import Path
from numpy.polynomial.legendre import leggauss,legval
D=Path(__file__).resolve().parent
from positive3 import reconstruct
def run():
 x,w=leggauss(24);t=(x+1)/2;w/=2
 fields=[(1+x)**4+.01,(1-x)**4+.03,(x*x-.4)**2+.02,1+.2*x]
 tests=[]
 for f in fields:
  signed=f-1;O=np.array([np.dot(w*t**j,signed) for j in range(3)])[:,None,None]*np.ones((1,1,314))
  a,ls,v=reconstruct(O,np.ones(311));c=a[0,0];r=np.array([np.dot(w*t**j,legval(x,c)) for j in range(3)])
  err=float(np.max(abs(r-O[:,0,0])));assert err<1e-12 and v>0
  tests.append(dict(limited=len(ls),min_ratio=v,moment_abs=err))
 out={}
 for p in sorted(D.glob('m3_*.npz')):
  z=np.load(p);L=z['limits'];assert L.ndim==2 and L.shape[1]==7
  if len(L):
   # [step,u,ray,channel,raw_min_ratio,positive_min_ratio,high_coeff_norm/Planck].
   ch,count=np.unique(L[:,3].astype(int),return_counts=True);ix=np.argmax(count)
   out[p.stem]=dict(count=len(L),unique_cells=len(np.unique(L[:,0])),unique_channels=ch.tolist(),top_channel=int(ch[ix]),top_count=int(count[ix]),z_range=[float(np.min(np.expm1(-L[:,1]))),float(np.max(np.expm1(-L[:,1])))],max_high_relative_to_planck=float(max(L[:,6])),min_ratio=float(min(L[:,5])))
  else:out[p.stem]=dict(count=0)
 result=dict(manufactured=tests,locations=out,scope='positivity reconstruction certificate and event-local count. No exact sensitivity attribution to limiter without an alternative same-history intervention.')
 (D/'LIMITER_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':run()

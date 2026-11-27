"""Audit initial jump correction for an arbitrary monotonic retarded map."""
import numpy as np,json,sys
from scipy.optimize import brentq
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3m_gain_events'))
from gain import correction
def run():
 # Correction must include cases where the exact arrival is outside but
 # affine approximation lies inside; clipped Heaviside moments fix both.
 rows=[]
 for l,r in [(0.,1.),(.3,.7),(.2,.5),(.5,.8)]:
  for s in [.199,.3,.5,.7,.801]:
   t=lambda u:u+.12*u*(1-u)
   ex=brentq(lambda u:t(u)-s,0,1)
   a=np.clip((ex-l)/(r-l),0,1);b=np.clip((s-t(l))/(t(r)-t(l)),0,1)
   exact=np.array([1-a,(1-a*a)/2]);approx=np.array([1-b,(1-b*b)/2])
   old=np.array(correction(l,r,np.array([[ex]]),s,np.array([[t(l)]]),np.array([[t(r)]]),np.ones((1,1)))).ravel()
   new=np.array([b-a,(b*b-a*a)/2])
   assert np.max(abs(approx+new-exact))<1e-15
   rows.append(dict(l=l,r=r,s=s,old_res=float(np.max(abs(approx+old-exact))),new_res=float(np.max(abs(approx+new-exact)))))
 # Real C3U reference geometry: measure variation in initial shift across a
 # finite receiver cell relative to interpolation scale.
 sys.path.insert(0,str(D.parent/'r118c3t_second_tangent'))
 from regular import Context
 c=Context(32);u=c.he
 a,b=c.clock.ret(u[-1],c.lr);o=dict(rows=rows,actual_clock_t1_max=float(np.max(abs(a))),actual_clock_t2_max=float(np.max(abs(b))),min_delay=float(min(c.lr)),max_step=float(max(np.diff(u))),scope='manufactured exact monotonic event correction and actual clock scale; no full outgoing tangent')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()

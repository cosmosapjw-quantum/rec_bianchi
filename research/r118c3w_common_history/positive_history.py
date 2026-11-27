"""Moment-preserving positive quadratic correction on a monotone Planck lower bound."""
import numpy as np
def project(L,M,R,fr):
 # add c*(6z²-6z+1): preserves both m0 and m1; fr is a constant
 # lower bound for actual Planck occupation on cell.
 a=L[...,:311]+fr;b=R[...,:311]+fr;mean=(a+b)/2
 bad=(a<=0)|(b<=0);s=b-a
 c=np.where(bad,abs(s)/np.sqrt(12.),0.)
 # analytic minimum at interior stationary point or endpoints.
 z=np.clip(.5-np.divide(s,12*c,out=np.zeros_like(s),where=c>0),0,1)
 v=a+s*z+c*(6*z*z-6*z+1)
 v=np.minimum(np.minimum(a+c,b+c),v)
 if np.any(v<=0):
  i=np.unravel_index(np.argmin(v/fr),v.shape)
  raise ValueError(f'quadratic positivity infeasible index={i} min_ratio={v[i]/np.broadcast_to(fr,v.shape)[i]} raw_mean={mean[i]} slope={s[i]}')
 l=L.copy();m=M.copy();r=R.copy()
 l[...,:311]+=c;m[...,:311]-=c/2;r[...,:311]+=c
 assert np.max(abs((l+4*m+r)-(L+4*M+R)))<1e-24
 assert np.max(abs((2*m+r)-(2*M+R)))<1e-24
 return l,m,r,int(np.count_nonzero(bad)),float(np.min(v/fr))

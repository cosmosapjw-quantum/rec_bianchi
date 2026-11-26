"""Shared-population, direction-resolved open line cell. Backward Euler, exact stock ledger."""
import numpy as np
from scipy.optimize import brentq
A21=6.265e8
def advance(p,n,X,C,w,k,fin,dt):
 w=np.asarray(w);w=w/w.sum();n=np.asarray(n);ci=C*w;bath=ci*fin
 inj=dt*np.sum(k*bath);scale=p+n.sum()+inj
 if not(0<=p<X*.75 and C>0 and dt>0 and np.min(n)>=0 and np.min(fin)>=0 and np.min(k)>=0 and scale>0):raise ValueError('line domain')
 hi=min(X*.749999,scale)
 def state(pp):
  nn=(n+dt*(w*A21*pp+k*bath))/(1+dt*(A21*(3*X-4*pp)/C+k))
  esc=dt*np.sum(k*nn);residual=(pp-p)+np.sum(nn-n)+esc-inj
  return residual,nn,esc
 lo=state(0.)[0];high=state(hi)[0]
 if lo>0 or high<0:raise ValueError('line root bracket')
 pp=brentq(lambda z:state(z*scale)[0]/scale,0,hi/scale,xtol=1e-15,rtol=1e-14)*scale
 r,nn,e=state(pp);assert np.min(nn)>=0 and abs(r)<1e-12*scale
 return pp,nn,e,inj,r
def test():
 w=np.array([.3,.7]);X=.8;C=2.;fin=np.full(2,.001);p=3*X*fin[0]/(1+4*fin[0]);n=C*w*fin;k=np.array([.1,.2])
 q,m,e,i,r=advance(p,n,X,C,w,k,fin,1.)
 assert abs(q-p)<1e-14 and np.max(abs(m-n))<1e-14 and abs(e-i)<1e-14
 print('dynamic line equilibrium passed')
if __name__=='__main__':test()

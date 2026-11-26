"""Shared directional line cell with a deviation variable for stiff external balance."""
import numpy as np
from scipy.optimize import brentq
A21=6.265e8
def advance(dp,n,X,C,w,k,fin,dt,ref,net,loss):
 w=w/w.sum();n=np.asarray(n);bath=C*w*fin;inj=dt*(k@bath)
 # ref is fixed native population; use deviation directly to avoid subtracting
 # a large pump and loss or resolving a tiny population displacement in p.
 scale=ref+abs(dp)+n.sum()+inj+dt*abs(net)
 if min(ref+dp,loss)<0 or C<=0 or np.min(n)<0 or np.min(fin)<0 or scale<=0:raise ValueError('domain')
 def at(delta):
  pp=ref+delta
  nn=(n+dt*(w*A21*pp+k*bath))/(1+dt*(A21*(3*X-4*pp)/C+k))
  esc=dt*(k@nn);ext=dt*(net-loss*delta)
  return delta-dp+np.sum(nn-n)+esc-inj-ext,nn,esc,ext
 lo=-ref;hi=min(.749999*X-ref,scale+dt*max(net+loss*ref,0.))
 assert at(lo)[0]<=0 and at(hi)[0]>=0
 v=brentq(lambda z:at(z*scale)[0]/scale,lo/scale,hi/scale,xtol=1e-30,rtol=1e-14)*scale
 res,nn,esc,ext=at(v)
 assert min(nn)>=0 and abs(res)<1e-11*scale,(res,scale,loss,dt)
 return v,nn,esc,inj,ext,res
def test():
 w=np.array([.3,.7]);X=.8;C=2.;fin=np.full(2,.001);p=3*X*fin[0]/(1+4*fin[0]);n=C*w*fin;k=np.array([.1,.2])
 for loss in [0.,1e12]:
  dp,nn,e,i,ee,r=advance(0.,n,X,C,w,k,fin,1.,p,0.,loss)
  assert abs(dp)<1e-14 and np.max(abs(nn-n))<1e-14 and abs(e-i)<1e-14 and abs(ee)<1e-14
 print('stable sourced line equilibrium passed')
if __name__=='__main__':test()

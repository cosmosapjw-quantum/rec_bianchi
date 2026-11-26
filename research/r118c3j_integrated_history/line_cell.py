"""Closed 1s/2p plus single photon band, exact reaction-only flow."""
import numpy as np
from scipy.optimize import brentq
EL=10.198714553953742;A21=6.265e8;H_EV=4.135667696e-15;C_LIGHT=299792458.
def phase(nh_m3,dlog):
 if nh_m3<=0 or dlog<=0:raise ValueError('phase')
 return 8*np.pi*(EL/H_EV/C_LIGHT)**3/nh_m3*dlog
def evolve(p,n,X,C,dt):
 if not 0<=p<=X or n<0 or C<=0 or dt<0:raise ValueError('state')
 # Use transfer d rather than subtract tiny p from large X. p'=p+d,n'=n-d.
 def fun(d):
  pp=p+d;nn=n-d;return 3*(X-pp)*nn-C*pp-pp*nn
 lo=-p;hi=min(n,X-p)
 if hi==lo:return p,n,0.,0.
 scale=max(p,n,1e-300)
 root=brentq(lambda z:fun(z*scale),lo/scale,hi/scale,xtol=5e-15,rtol=1e-14)*scale
 # d'=A21/C*(4 d^2 + b d + c); stable root and distant second root.
 b=-(3*X+3*n-3*p+C+n-p);other=-b/4-root
 decay=np.exp(-A21/C*4*(other-root)*dt)
 # exact transfer from d(0)=0, cancellation-free using expm1 for small dt.
 den=1-root/other*decay;d=root*(-np.expm1(-A21/C*4*(other-root)*dt))/den
 if not lo-1e-14*scale<=d<=hi+1e-14*scale:raise ValueError('domain')
 return p+d,n-d,d,root

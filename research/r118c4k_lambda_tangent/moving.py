"""C4K derivative of actual signed event-segment GL5 map wrt lambda, plus history tangent."""
import numpy as np
from numpy.polynomial.legendre import leggauss
class Moving:
 def __init__(self,m,mm,mp,eps):
  self.m=m;self.mm=mm;self.mp=mp;self.ep=eps
 def ev(self,fs,t):return np.stack([f(t[j]) for j,f in enumerate(fs)])
 def deriv(self,kind,t):
  return (self.ev(getattr(self.mp,kind),t)-self.ev(getattr(self.mm,kind),t))/(2*self.ep)
 def evald(self,kind,t,dt):
  f=getattr(self.m,kind)
  return self.ev(f,t),self.deriv(kind,t)+np.stack([z(t[j],1) for j,z in enumerate(f)])*dt
 def td(self,u,du):
  m=self.m;U=np.broadcast_to(u,(m.nr,313));dU=np.broadcast_to(du,U.shape);f,df=self.evald('f',U,dU);t,dt=self.evald('g',f-m.lr,df)
  assert np.all(np.isfinite(t)) and np.all(np.isfinite(dt));return t,dt
 def integrate(self,i,l,r,A,DA):
  m=self.m;c=m.c;he=c.he[:i];nr=m.nr;src=c.src[None,:];h=r-l;nodes,weights=leggauss(5)
  u=np.full((nr,313),l);du=np.zeros_like(u);out=np.zeros((5,nr,313));dout=np.zeros_like(out);ray=np.arange(nr)[:,None];events=0;mindist=1.
  for _ in range(len(he)+2):
   active=u<r
   if not active.any():return out,dout,events,mindist
   t=m.t(u);j=np.searchsorted(he,t+2e-14,side='right')-1;before=j<0
   nk=he[np.clip(j+1,0,len(he)-1)];f,df=self.evald('f',nk,np.zeros_like(nk));cross,dcross=self.evald('g',f+m.lr,df)
   hit=active&np.isfinite(cross)&(cross<r);events+=int(hit.sum())
   q=active&np.isfinite(cross)
   if q.any():mindist=min(mindist,float(np.min(abs(cross[q]-r))))
   end=np.minimum(r,np.where(np.isfinite(cross),cross,r));end=np.where(active,end,u)
   dend=np.where(active,np.where(hit,dcross,0.),du)
   span=end-u;dspan=dend-du
   if np.any(active&(span<=0)):raise ValueError('event progress')
   if i>1:
    k=np.clip(j,0,len(he)-2);hh=he[k+1]-he[k];coef=A[k,ray,src];dcoef=DA[k,ray,src]
    for q,w in zip(nodes,weights):
     x=u+(q+1)*span/2;dx=du+(q+1)*dspan/2;t,dt=self.td(x,dx)
     st=(t-he[k])/hh;s=2*np.clip(st,0,1)-1;ds=np.where((st>=0)&(st<=1),2*dt/hh,0.)
     P0=np.ones_like(s);P1=s;dP0=np.zeros_like(s);dP1=ds
     f=coef[...,0]+s*coef[...,1];df=dcoef[...,0]+s*dcoef[...,1]+ds*coef[...,1]
     for z in range(2,A.shape[-1]):
      P2=((2*z-1)*s*P1-(z-1)*P0)/z;dP2=((2*z-1)*(ds*P1+s*dP1)-(z-1)*dP0)/z
      f+=coef[...,z]*P2;df+=dcoef[...,z]*P2+coef[...,z]*dP2;P0,P1=P1,P2;dP0,dP1=dP1,dP2
     f=np.where(active&~before,f,0.);df=np.where(active&~before,df,0.);zz=(x-l)/h;dzz=dx/h;wt=w*span/(2*h);dwt=w*dspan/(2*h)
     for k0 in range(5):
      out[k0]+=wt*f*zz**k0
      dout[k0]+=(dwt*f+wt*df)*zz**k0
      if k0:dout[k0]+=wt*f*k0*zz**(k0-1)*dzz
   u=end;du=dend
  raise ValueError('too many events')


"""Variational causal clock and directional boundary derivative of the actual GL5 weak map."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from numpy.polynomial.legendre import leggauss
class Events:
 def __init__(self,m):
  self.m=m;c=m.c;grid=m.D.x;t0=c.he[0];lam=m.lam
  def rhs(u,z):
   d,v=z.reshape(2,3,3);s=c.clock.S(u);return np.stack([-lam*s@d,-s@d-lam*s@v]).ravel()
  init=np.stack([np.eye(3),np.zeros((3,3))]).ravel()
  a=solve_ivp(rhs,(t0,grid[0]),init,method='DOP853',rtol=2e-13,atol=2e-15,dense_output=True);b=solve_ivp(rhs,(t0,grid[-1]),init,method='DOP853',rtol=2e-13,atol=2e-15,dense_output=True)
  assert a.success and b.success;z=np.empty((len(grid),18));mask=grid<t0;z[mask]=a.sol(grid[mask]).T;z[~mask]=b.sol(grid[~mask]).T
  z=z.reshape(-1,2,3,3);self.dD=CubicSpline(grid,z[:,1],axis=0,extrapolate=False)
  g=np.einsum('tij,nj->tni',m.D(grid),c.n);dg=np.einsum('tij,nj->tni',z[:,1],c.n);dfl=-np.sum(g*dg,axis=-1)/np.sum(g*g,axis=-1)
  self.fl=[CubicSpline(grid,dfl[:,i],extrapolate=False) for i in range(m.nr)]
  self.ode_base_gap=float(np.max(abs(z[:,0]-m.D(grid))));self.aligned=[];self.events=0;self.inv_res=0.;self.nodes,self.weights=leggauss(5)
 def ev(self,fs,t,k=0):return np.stack([f(t[j],k) for j,f in enumerate(fs)])
 def td(self,u,du=0.):
  m=self.m;U=np.broadcast_to(u,(m.nr,313));v=m.t(U);f=self.ev(self.fl,U)+self.ev(m.f,U,1)*du
  dv=(f-self.ev(self.fl,v))/self.ev(m.f,v,1);assert np.isfinite(dv).all();return v,dv
 def ang(self,u):
  m=self.m;v=m.n@m.D(u).T;dv=m.n@self.dD(u).T;d=np.linalg.norm(v,axis=1);dlog=np.sum(v*dv,axis=1)/(d*d);n=v/d[:,None];dn=dv/d[:,None]-dlog[:,None]*n
  S=m.c.clock.S(u);a,w=m.state(u);da=np.einsum('ni,ij,nj->n',n,S,n)+2*m.lam*np.einsum('ni,ij,nj->n',dn,S,n)
  dw=-3*w*(dlog-w@dlog);return a,w,da,dw
 def correction(self,i,l,r,A):
  m=self.m;he=m.c.he[:i];h=r-l;out=np.zeros((2,5,m.nr,313))
  if i<=1:return out
  for side,u in [('left',l),('right',r)]:
   t=m.t(u);j0=np.searchsorted(he,t);jl=np.clip(j0-1,0,len(he)-1);jr=np.clip(j0,0,len(he)-1)
   j=np.where(abs(t-he[jl])<abs(t-he[jr]),jl,jr);sk=he[j];cross=m.ev(m.g,m.ev(m.f,sk)+m.lr);near=np.isfinite(cross)&(abs(cross-u)<1e-13)&(j<len(he)-1)
   if not near.any():continue
   cr=np.where(near,cross,u);dc=(self.ev(self.fl,sk)-self.ev(self.fl,cr))/self.ev(m.f,cr,1);js=np.searchsorted(he,t+2e-14,side='right')-1
   for ri,ci in np.argwhere(near):
    k=int(j[ri,ci]);ch=int(m.c.src[ci]);before=float(np.sum(A[k-1,ri,ch])) if k else 0.;after=float(A[k,ri,ch]@((-1.)**np.arange(A.shape[-1])))
    present=(cross[ri,ci]>l and js[ri,ci]<k) if side=='left' else cross[ri,ci]<r
    a=dc[ri,ci];jump=before-after
    for z,sg in enumerate([1,-1]):
     d=sg*a;enters=d>0 if side=='left' else d<0
     out[z,:,ri,ci]=(float(enters)-float(present))*jump*d/h*((u-l)/h)**np.arange(5)
    self.aligned.append(dict(step=i,side=side,ray=int(ri),channel=int(ci),distance=float(cross[ri,ci]-u),knot=k,jump=jump,arrival_derivative=float(a),nominal_present=bool(present)))
  return out
 def integrate(self,i,l,r,A,DA):
  m=self.m;c=m.c;he=c.he[:i];nr=m.nr;src=c.src[None,:];h=r-l
  assert np.max(m.t(r))<he[-1];u=np.full((nr,313),l);du=np.zeros_like(u);out=np.zeros((3,5,nr,313));gout=np.zeros((5,nr,313));ray=np.arange(nr)[:,None]
  for _ in range(len(he)+2):
   active=u<r
   if not active.any():
    corr=self.correction(i,l,r,A);return out[0],out[1:]+np.stack([gout,-gout])+corr
   t=m.t(u);j=np.searchsorted(he,t+2e-14,side='right')-1;before=j<0;nk=he[np.clip(j+1,0,len(he)-1)]
   q=m.ev(m.f,nk)+m.lr;cross=m.ev(m.g,q);hit=active&np.isfinite(cross)&(cross<r);self.events+=int(hit.sum())
   cr=np.where(hit,cross,r);dc=(self.ev(self.fl,nk)-self.ev(self.fl,cr))/self.ev(m.f,cr,1)
   if hit.any():self.inv_res=max(self.inv_res,float(np.max(abs(m.ev(m.f,cr)[hit]-q[hit]))))
   end=np.where(active,np.minimum(r,np.where(np.isfinite(cross),cross,r)),u);de=np.where(active,np.where(hit,dc,0.),du);span=end-u;ds=de-du
   if np.any(active&(span<=0)):raise ValueError('event progress')
   if i>1:
    k=np.clip(j,0,len(he)-2);hh=he[k+1]-he[k];coef=np.stack([A[k,ray,src],DA[0,k,ray,src],DA[1,k,ray,src]])
    for q,w in zip(self.nodes,self.weights):
     x=u+(q+1)*span/2;dx=du+(q+1)*ds/2;t,dt=self.td(x,dx);st=(t-he[k])/hh;s=2*np.clip(st,0,1)-1;d=np.where((st>=0)&(st<=1),2*dt/hh,0.)
     f=coef[...,0]+s*coef[...,1];df=d*coef[0,...,1];p0=np.ones_like(s);p1=s;d0=np.zeros_like(s);d1=d
     for k0 in range(2,7):
      p2=((2*k0-1)*s*p1-(k0-1)*p0)/k0;d2=((2*k0-1)*(d*p1+s*d1)-(k0-1)*d0)/k0
      f+=coef[...,k0]*p2;df+=coef[0,...,k0]*d2;p0,p1=p1,p2;d0,d1=d1,d2
     f=np.where(active&~before,f,0.);df=np.where(active&~before,df,0.);zz=(x-l)/h;dz=dx/h;wt=w*span/(2*h);dw=w*ds/(2*h)
     for j0 in range(5):
      out[:,j0]+=wt*f*zz**j0;gout[j0]+=(dw*f[0]+wt*df)*zz**j0
      if j0:gout[j0]+=wt*f[0]*j0*zz**(j0-1)*dz
   u=end;du=de
  raise ValueError('too many events')

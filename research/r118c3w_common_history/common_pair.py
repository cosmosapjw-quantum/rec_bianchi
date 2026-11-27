"""Event-split finite amplitude comparison, same H clock and native atomic owner.
The regular outgoing difference is represented by two weak cell moments.
Reference is the original accepted scalar gas and quadratic outgoing history.
"""
import numpy as np,sys,json
from pathlib import Path
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
from positive_history import project
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3t_second_tangent'))
from regular import Context,p
sys.path.insert(0,str(D.parent/'r118c3n_jump_response'))
from jump_response import JumpResponse
sys.path.insert(0,str(D.parent/'r118c3q_paired_difference'))
from difference import thermal_diff
class Map:
 def __init__(self,c,lam):
  self.c=c;self.lam=lam;self.n=c.n;self.lr=c.lr;self.nr=len(self.n)
  lo=c.he[0]-max(c.lr)-.002;hi=c.he[-1];t0=c.he[0]
  rhs=lambda u,z:(-lam*c.clock.S(u)@z.reshape(3,3)).ravel()
  a=solve_ivp(rhs,(t0,lo),np.eye(3).ravel(),method='DOP853',rtol=2e-13,atol=2e-15,dense_output=True)
  b=solve_ivp(rhs,(t0,hi),np.eye(3).ravel(),method='DOP853',rtol=2e-13,atol=2e-15,dense_output=True)
  grid=np.linspace(lo,hi,4097);z=np.empty((len(grid),9));m=grid<t0;z[m]=a.sol(grid[m]).T;z[~m]=b.sol(grid[~m]).T
  self.D=CubicSpline(grid,z.reshape(-1,3,3),axis=0)
  d=np.linalg.norm(np.einsum('tij,nj->tni',z.reshape(-1,3,3),self.n),axis=-1)
  ell=grid[:,None]-np.log(d);assert np.min(np.diff(ell,axis=0))>0
  self.f=[CubicSpline(grid,ell[:,i],extrapolate=False) for i in range(self.nr)]
  self.g=[CubicSpline(ell[:,i],grid,extrapolate=False) for i in range(self.nr)]
  self.inv_err=max(float(np.max(abs(self.g[i](self.f[i](grid[::7]))-grid[::7]))) for i in range(self.nr))
  self.events=0
 def ev(self,fs,t):
  return np.stack([f(t[i]) for i,f in enumerate(fs)])
 def t(self,u):
  U=np.broadcast_to(u,(self.nr,313));t=self.ev(self.g,self.ev(self.f,U)-self.lr)
  assert np.isfinite(t).all()
  return t
 def state(self,u):
  z=self.n@self.D(u).T;d=np.linalg.norm(z,axis=1);n=z/d[:,None];w=self.c.w/d**3;w/=sum(w)
  a=1+self.lam*np.einsum('ni,ij,nj->n',n,self.c.clock.S(u),n)
  return a,w
 def mom(self,i,l,r,L,M,R,delta=False):
  # Split each ray-channel receiving interval at actual source knot arrivals.
  # Gauss integrates on receiving time, not on a linearized delay map.
  c=self.c;he=c.he[:i];nr=self.nr;src=c.src[None,:];h=r-l
  t0=self.t(l);t1=self.t(r);assert np.max(t1)<he[-1]
  u=np.full((nr,313),l);out=np.zeros((3,nr,313));nodes,weights=leggauss(3)
  ray=np.arange(nr)[:,None] if L.shape[1]==nr else 0
  for _ in range(len(he)+2):
   active=u<r
   if not active.any():return out
   t=self.t(u)
   # tolerance avoids a floating point event being rediscovered at same node.
   j=np.searchsorted(he,t+2e-14,side='right')-1
   before=j<0
   nextk=he[np.clip(j+1,0,len(he)-1)]
   cross=self.ev(self.g,self.ev(self.f,nextk)+self.lr)
   # Out of domain inverse means next source knot arrives after r.
   end=np.minimum(r,np.where(np.isfinite(cross),cross,r))
   end=np.where(active,end,u)
   span=end-u
   if np.any(active&(span<=0)):raise ValueError('event progress')
   self.events+=int(np.count_nonzero(active&(end<r)))
   if i>1:
    k=np.clip(j,0,len(he)-2);hh=he[k+1]-he[k]
    for q,w in zip(nodes,weights):
     x=u+(q+1)*span/2
     s=np.clip((self.t(x)-he[k])/hh,0,1)
     f=(1-3*s+2*s*s)*L[k,ray,src]+(4*s-4*s*s)*M[k,ray,src]+(2*s*s-s)*R[k,ray,src]
     f=np.where(active&~before,f,0.)
     zz=(x-l)/h;wt=w*span/(2*h)
     for m in range(3):out[m]+=wt*f*zz**m
   u=end
  raise ValueError('too many events')
def run(nt,lam):
 from common_base import context
 c=context(nt);z=np.load(D/f'base_{nt}.npz');he=z['he'];assert np.array_equal(he,c.he)
 c.L,c.M,c.R=[z[k] for k in ['L','M','R']];v=z['rows'];nr=c.nr;N=len(he)-1
 m=Map(c,lam);m0=Map(c,0.)
 A=np.zeros((N,nr,314));B=A.copy();C=A.copy();zero=np.zeros((nr,313))
 def owner(u,x,T,angular):
  aa,ww=m.state(u) if angular else (np.ones(nr),c.w)
  s,H,Tr=c.snap(u,x,T,c.zero)
  r,o,err=p.step(s,aa,zero,ww)
  return r.dxHII_dln_a,o,JumpResponse(s,aa,ww),H,Tr
 def apply(o,I):
  a,b,g=o[2].apply(I);return a+b,g
 def geom(u):
  t=m.t(u);R=t-(u-c.lr)
  return p._planck_difference(c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u)),R)
 dx=dT=0.;rows=[[he[0],0.,0.,0.,0.]];maxroot=0.;maxref=0.;minpos=np.inf;maxpos=0.;maxmom=0.;limited=0;minbound=np.inf
 for i,r in enumerate(he[1:],1):
  l=he[i-1];h=r-l;mid=(l+r)/2;xl,Tl=v[i-1,1:3];xr,Tr=v[i,1:3]
  U=m0.mom(i,l,r,c.L,c.M,c.R);V=m.mom(i,l,r,c.L,c.M,c.R)+m.mom(i,l,r,A,B,C)
  # smooth geometry source (same 3 point rule in receiving time).
  q,w=leggauss(3)
  for zz,ww in zip(q,w):
   z=(zz+1)/2;g=geom(l+z*h)
   for k in range(3):V[k]+=ww/2*g*z**k
  dif=V-U
  def gasforce(o0,o1,idx):
   k=0;J0=U[k+1] if idx else U[k]-U[k+1];J1=dif[k+1] if idx else dif[k]-dif[k+1]
   _,g0=apply(o0,J0);_,g1=apply(o1,J0);_,dg=apply(o1,J1)
   return .5*(o1[0]-o0[0])+(g1-g0)+dg
  a0=owner(l,xl,Tl,False);b0=owner(r,xr,Tr,False);a1=owner(l,xl+dx,Tl+dT,True)
  s,H,Tgamma=c.snap(mid,(xl+xr)/2,(Tl+Tr)/2,c.zero);scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tgamma**4/H;xm=(xl+xr)/2;A0=scale*xm/(1+xm+c.model.f_he)
  def trial(dn):
   dm=(dx+dn)/2;A1=scale*(xm+dm)/(1+xm+dm+c.model.f_he);dt=thermal_diff(Tl,Tr,dT,A0,A1,Tgamma,h)
   b1=owner(r,xr+dn,Tr+dt,True)
   F=gasforce(a0,a1,0)+gasforce(b0,b1,1)
   return dn-dx-h*F,dt,F,b1
  dn=brentq(lambda z:trial(z)[0],dx-1e-6,dx+1e-6,xtol=1e-21,rtol=1e-14);res,dt,F,b1=trial(dn);maxroot=max(maxroot,abs(res))
  O=[]
  for k in [0,1]:
   out=(a1[1]-a0[1])/( (k+1)*(k+2))+(b1[1]-b0[1])/(k+2)
   for idx,oo,qq in [(0,a0,a1),(1,b0,b1)]:
    J0=U[k+1] if idx else U[k]-U[k+1];J1=dif[k+1] if idx else dif[k]-dif[k+1]
    o0,_=apply(oo,J0);o1,_=apply(qq,J0);od,_=apply(qq,J1);out+=o1-o0+od
   O.append(out)
  A[i-1]=4*O[0]-6*O[1];C[i-1]=6*O[1]-2*O[0];B[i-1]=O[0]
  maxmom=max(maxmom,float(np.max(abs((A[i-1]+C[i-1])/2-O[0]))))
  # Recover common baseline raw linear projection and apply same positive map.
  bL,bM,bR=[Z[i-1,0] for Z in [c.L,c.M,c.R]]
  bm0=(bL+4*bM+bR)/6;bm1=bM/3+bR/6
  fr=1/np.expm1(c.tab.energy_eV/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-r)))
  aa,bb,cc,nl,mb=project(4*bm0-6*bm1+A[i-1],bm0+B[i-1],6*bm1-2*bm0+C[i-1],fr)
  # Avoid subtracting full outgoing fields if no correction was applied:
  # P2 coefficient change alone affects the signed history.
  dl=aa-(4*bm0-6*bm1+A[i-1]);bl=bL-(4*bm0-6*bm1);cor=dl-bl
  A[i-1]+=cor;B[i-1]-=cor/2;C[i-1]+=cor
  limited+=nl;minbound=min(minbound,mb)
  for tt,arr,ref in [(l,A,c.L),(mid,B,c.M),(r,C,c.R)]:
   tr=c.model.tcmb0_K*np.exp(-tt);f=1/np.expm1(c.tab.energy_eV/(p.KB_NATIVE_EV_K*tr))
   ratio=np.min((f+ref[i-1,0,:311]+arr[i-1,:,:311])/f)
   if ratio<=0:raise ValueError(f'nonpositive full history {i} {ratio}')
   minpos=min(minpos,float(ratio))
  # native scalar reference mismatch against the actual accepted gas step:
  _,g0=apply(a0,U[0]-U[1]);_,g1=apply(b0,U[1]);maxref=max(maxref,abs(xr-xl-h*(.5*(a0[0]+b0[0])+g0+g1)))
  dx,dT=dn,dt;rows.append([r,dx,dT,F,res])
  if i%128==0:print(nt,lam,i,dx,flush=True)
 tag=f'pair_{nt}_{lam:g}';a=np.array(rows);assert maxroot<1e-14
 np.savez_compressed(D/(tag+'.npz'),rows=a,final_out=B[-1])
 out=dict(nt=nt,lambda_=lam,steps=N,dx=float(dx),dT=float(dT),max_root=maxroot,max_reference_residual=maxref,weak_projection_abs=maxmom,event_splits=m.events,clock_inverse_error=m.inv_err,min_full_virtual_ratio=minpos,limited_cells=limited,min_bound_ratio=minbound,scope='common-integrator event-aligned paired native response, same baseline gas and affine outgoing moments, H-only fixed scalar H; no continuum')
 (D/(tag+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run(int(sys.argv[1]),float(sys.argv[2]))

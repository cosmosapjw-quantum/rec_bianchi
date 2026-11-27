"""Native H-only retarded atomic owner, three weak outgoing moments.
All lambda values use the same discrete integrator; no physical H(lambda).
"""
import json,numpy as np,sys,time
from pathlib import Path
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c3w_common_history';sys.path.insert(0,str(P))
from common_base import context
from common_pair import Map as OldMap,p,JumpResponse
from positive3 import reconstruct
class Map(OldMap):
 def mom3(self,i,l,r,A):
  c=self.c;he=c.he[:i];nr=self.nr;src=c.src[None,:];h=r-l
  t1=self.t(r);assert np.max(t1)<he[-1]
  u=np.full((nr,313),l);out=np.zeros((4,nr,313));nodes,weights=leggauss(5)
  ray=np.arange(nr)[:,None] if A.shape[1]==nr else 0
  for _ in range(len(he)+2):
   active=u<r
   if not active.any():return out
   t=self.t(u);j=np.searchsorted(he,t+2e-14,side='right')-1;before=j<0
   nk=he[np.clip(j+1,0,len(he)-1)];cross=self.ev(self.g,self.ev(self.f,nk)+self.lr)
   end=np.minimum(r,np.where(np.isfinite(cross),cross,r));end=np.where(active,end,u);span=end-u
   if np.any(active&(span<=0)):raise ValueError('event progress')
   self.events+=int(np.count_nonzero(active&(end<r)))
   if i>1:
    k=np.clip(j,0,len(he)-2);hh=he[k+1]-he[k];coef=A[k,ray,src]
    for q,w in zip(nodes,weights):
     x=u+(q+1)*span/2;s=2*np.clip((self.t(x)-he[k])/hh,0,1)-1
     # Legendre recurrence, all coefficient arrays aligned by ray/channel.
     f=coef[...,0]+s*coef[...,1];P0=np.ones_like(s);P1=s
     for j0 in range(2,A.shape[-1]):
      P2=((2*j0-1)*s*P1-(j0-1)*P0)/j0
      f+=coef[...,j0]*P2;P0,P1=P1,P2
     f=np.where(active&~before,f,0.);zz=(x-l)/h;wt=w*span/(2*h)
     for m in range(4):out[m]+=wt*f*zz**m
   u=end
  raise ValueError('too many events')
def run(nt,lam,refine=1):
 c=context(nt);he=c.he
 if refine>1:
  zz=np.expm1(-he);new=[]
  for l,r,zl,zr in zip(he[:-1],he[1:],zz[:-1],zz[1:]):
   n=refine if zr<1106.6 and zl>1105.5 else 1
   new.extend(np.linspace(l,r,n,endpoint=False))
  new=np.r_[new,he[-1]]
  c.v=np.stack([np.interp(new,he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=new;he=new
 N=len(he)-1;nr=c.nr;m=Map(c,lam)
 # Scalar reference stores one ray, all nonzero lambda retain full directional history.
 A=np.zeros((N,1 if lam==0 else nr,314,7));zero=np.zeros((nr,313))
 def owner(u,x,T):
  s,H,Tr=c.snap(u,x,T,c.zero);a,w=m.state(u) if lam else (np.ones(nr),c.w)
  rr,o,err=p.step(s,a,zero,w)
  return rr.dxHII_dln_a,o,JumpResponse(s,a,w)
 def apply(o,I):
  a,b,g=o[2].apply(I);return a+b,g
 x,T=map(float,c.v[0,1:3]);rows=[[he[0],x,T,0.,0.]];maxroot=0.;minpos=np.inf;limit=[];maxmoment=0.;gl,gw=leggauss(5)
 for i,r in enumerate(he[1:],1):
  l=he[i-1];h=r-l;mid=(l+r)/2;U=m.mom3(i,l,r,A)
  if lam:
   for t,wt in zip(gl,gw):
    f=(t+1)/2;u=l+h*f;R0=m.t(u)-(u-c.lr);g=p._planck_difference(c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u)),R0)
    for k in range(4):U[k]+=wt/2*g*f**k
  a=owner(l,x,T);H=np.interp(mid,c.ge,c.g['h'])*2.1842852410855023e-18;Tgamma=c.model.tcmb0_K*np.exp(-mid);scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tgamma**4/H
  def trial(dx):
   xm=x+dx/2;B=scale*xm/(1+xm+c.model.f_he);tt=T+h*(B*(Tgamma-T)-2*T)/(1+h*(2+B)/2)
   b=owner(r,x+dx,tt);_,g0=apply(a,U[0]-U[1]);_,g1=apply(b,U[1]);F=.5*(a[0]+b[0])+g0+g1
   return dx-h*F,tt,F,b
  width=max(1e-4,4*abs(c.v[i,1]-c.v[i-1,1]));lo=max(-width,-.99*x);hi=min(width,.99*(1-x))
  dx=brentq(lambda q:trial(q)[0],lo,hi,xtol=1e-19,rtol=1e-14);res,tt,F,b=trial(dx);maxroot=max(maxroot,abs(res))
  O=[]
  for k in range(3):
   o0,_=apply(a,U[k]-U[k+1]);o1,_=apply(b,U[k+1]);o=a[1]/((k+1)*(k+2))+b[1]/(k+2)+o0+o1
   O.append(o if lam else o[:1])
  O=np.array(O);fr=1/np.expm1(c.tab.energy_eV/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-r)))
  try:co,ls,mi=reconstruct(O,fr)
  except ValueError as e:
   fail=dict(nt=nt,lam=lam,step=i,u=float(r),reason=str(e),prior_steps=i-1,scope='three moment reconstruction blocked; no clipping')
   (D/f'failed_{nt}_{lam:g}_r{refine}.json').write_text(json.dumps(fail,indent=2)+'\n');print(fail,flush=True);raise
  for e in ls:limit.append([i,float(r),*e])
  A[i-1]=co;minpos=min(minpos,mi)
  recon=np.array([co[...,0],co[...,0]/2+co[...,1]/6,co[...,0]/3+co[...,1]/6+co[...,2]/30])
  maxmoment=max(maxmoment,float(np.max(abs(recon-O))/max(np.max(abs(O)),1e-300)))
  x+=dx;T=tt;assert 0<x<1 and T>0
  rows.append([r,x,T,F,res])
  if i%256==0:print(nt,lam,i,x,'limited',len(limit),flush=True)
 rows=np.array(rows);assert maxroot<1e-15 and minpos>0 and maxmoment<1e-13
 tag=f'm3_{nt}_{lam:g}'+(f'_local{refine}' if refine>1 else '');np.savez_compressed(D/(tag+'.npz'),rows=rows,he=he,last=A[-1],limits=np.array(limit).reshape(-1,7))
 result=dict(nt=nt,lam=lam,refine=refine,steps=N,final_x=float(x),final_T=float(T),initial_x=float(rows[0,1]),max_root=float(maxroot),min_full_ratio=minpos,limited_cells=len(limit),max_moment_relative=maxmoment,event_splits=m.events,scope='three weak moments, certified nonnegative polynomial (P3..6 correction if needed), actual direct finite native H-only response, fixed H, not continuum')
 (D/(tag+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
if __name__=='__main__':run(int(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3]) if len(sys.argv)>3 else 1)

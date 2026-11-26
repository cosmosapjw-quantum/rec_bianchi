"""Predicted step ledger: dense first generation, sparse later direct-survival chain.
Prior actual gas predicts jumps only. Residual interpolation retains all discrepancies.
"""
import numpy as np
from jump_response import JumpResponse
from gain import gain
class Ledger:
 def __init__(self,t0,times,jumps,chains,stats):
  self.t0=t0;self.times=np.array(times);self.chains=chains;self.stats=stats
  shape=(len(times)+1,*jumps[0].shape);self.c=np.zeros(shape);self.m=np.zeros(shape);self.m2=np.zeros(shape)
  for k,(t,j) in enumerate(zip(times,jumps),1):
   s=t-t0;self.c[k]=self.c[k-1]+j;self.m[k]=self.m[k-1]+s*j;self.m2[k]=self.m2[k-1]+s*s*j
 def value(self,t,src=None):
  k=np.searchsorted(self.times,t,side='right')
  if src is None:
   v=self.c[int(k)].copy()
   for et,amp in self.chains:v+=np.where(et<=t,amp,0.)
   return v
  ix=np.arange(t.shape[0])[:,None];j=src[None,:]
  v=self.c[k,ix,j].copy()
  for et,amp in self.chains:v+=np.where(et[:,src]<=t,amp[:,src],0.)
  return v
 def primitive(self,t,src):
  k=np.searchsorted(self.times,t,side='right');ix=np.arange(t.shape[0])[:,None];j=src[None,:];s=t-self.t0
  a=self.c[k,ix,j];return s*a-self.m[k,ix,j],.5*(s*s*a-self.m2[k,ix,j])
 def means(self,l,r,src):
  h=r-l;a,b=self.primitive(l,src);c,d=self.primitive(r,src);U=(c-a)/h;V=((d-b)-(l-self.t0)*(c-a))/(h*h)
  for et,amp in self.chains:
   f=np.clip((et[:,src]-l)/h,0.,1.);q=amp[:,src];U+=(1-f)*q;V+=.5*(1-f*f)*q
  return U,V
def build(t0,end,events,jump0,src,lr,p0,ge,F,baseline,model_at,interpF,depth):
 # model_at(u,x,T) supplies actual snapshot, rates, angular weights.
 order=np.argsort(events.ravel());flat=events.ravel()[order];ok=np.isfinite(flat);flat=flat[ok];order=order[ok]
 breaks=np.r_[0,np.where(np.diff(flat)>1e-10)[0]+1,len(flat)]
 # group only near coincident roots; actual per-channel first-event root used by quadrature correction.
 times=[t0];jumps=[jump0.copy()]
 n=len(p0);first_time=np.full((n,314),np.inf);first_amp=np.zeros((n,314))
 gd=np.zeros((n,313));sample=np.linspace(t0,end,129);ta=[]
 for u in sample:
  x,T=[np.interp(u,baseline[:,0],baseline[:,k]) for k in [1,2]];ss,r,w=model_at(u,x,T)
  ta.append(ss.Dtau[None,:]/r[:,None]);gd=np.maximum(gd,abs(gain(ss,r,w)))
 ta=np.array(ta)
 direct_l1=0.;coupled_l1=0.;rhs_bound=0.;coupled_bound=0.
 for l,r in zip(breaks[:-1],breaks[1:]):
  u=float((flat[l]+flat[r-1])/2);ids=order[l:r];i,j=np.unravel_index(ids,events.shape);d=np.zeros_like(events);d[i,j]=jump0[i,src[j]]
  x,T=[np.interp(u,baseline[:,0],baseline[:,k]) for k in [1,2]];ss,rate,w=model_at(u,x,T)
  a,b,_=JumpResponse(ss,rate,w).apply(d)
  times.append(u);jumps.append(a+b)
  ij=j<311;first_time[i[ij],j[ij]]=u;first_amp[i[ij],j[ij]]=a[i[ij],j[ij]]
  direct_l1+=float(np.sum(abs(a)));coupled_l1+=float(np.sum(abs(b)))
  # Sampled gain envelope, ignores travel delay: conservative for these predicted jumps and sampled gains only.
  rhs_bound+=float(np.sum(gd*abs((a+b)[:,src]))*(end-u));coupled_bound+=float(np.sum(gd*abs(b[:,src]))*(end-u))
 def ell(t,p):
  mat=interpF(ge,F,t);v=np.linalg.solve(np.swapaxes(mat,-1,-2),p[...,None])[...,0]
  return t-np.log(np.linalg.norm(v,axis=-1))
 chains=[];chain_stats=[];prev_t=first_time;prev_a=first_amp
 for gen in range(2,depth+1):
  tt=np.full((n,314),np.inf);amp=np.zeros_like(tt)
  v=prev_t[:,src[:311]];a=prev_a[:,src[:311]];i,j=np.where(np.isfinite(v)&(a!=0))
  if len(i):
   p=p0[i];target=ell(v[i,j],p)+lr[j];valid=target<=ell(np.full(len(i),end),p);i=i[valid];j=j[valid];target=target[valid];p=p[valid]
   lo=v[i,j].copy();hi=np.full(len(i),end)
   for _ in range(45):
    mid=(lo+hi)/2;b=ell(mid,p)<target;lo=np.where(b,mid,lo);hi=np.where(b,hi,mid)
   z=(lo+hi)/2
   k=np.clip(np.searchsorted(sample,z)-1,0,len(sample)-2);w=(z-sample[k])/(sample[k+1]-sample[k]);tau=ta[k,i,j]*(1-w)+ta[k+1,i,j]*w
   val=a[i,j]*np.exp(-tau);tt[i,j]=z;amp[i,j]=val
  chains.append((tt,amp));prev_t,prev_a=tt,amp
  chain_stats.append(dict(generation=gen,count=int(np.count_nonzero(amp)),l1=float(np.sum(abs(amp))),max_jump=float(np.max(abs(amp)))))
 stats=dict(first_groups=len(times)-1,first_direct_L1=direct_l1,first_coupled_L1=coupled_l1,sampled_gain_integrated_envelope=rhs_bound,sampled_coupled_envelope=coupled_bound,chains=chain_stats)
 return Ledger(t0,times,jumps,chains,stats)

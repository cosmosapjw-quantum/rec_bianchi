"""Bucketed all-channel affine outgoing jump propagation (predicted ledger).
Each arrival is deposited on adjacent predictor knots with exact zeroth/first time moments.
The actual outgoing minus predicted ledger remains the continuous-history interpolant.
"""
import numpy as np,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3n_jump_response'))
sys.path.insert(0,str(D.parent/'r118c3m_gain_events'))
from jump_response import JumpResponse
from event_mesh import local_means
class Ledger:
 def __init__(self,he,c,stats):
  self.he=he;self.c=c;self.stats=stats
 def value(self,t,src=None):
  k=np.searchsorted(self.he,t,side='right')-1
  if src is None:return self.c[int(k)].copy() if k>=0 else np.zeros_like(self.c[0])
  i=np.arange(t.shape[0])[:,None];j=src[None,:]
  return np.where(k<0,0.,self.c[np.maximum(k,0),i,j])
 def means(self,l,r,src):
  return local_means(self.he,self.c[:-1],self.c[:-1],self.c[:-1],l,r,src)
def deposit(arr,he,t,v):
 nr,nc=v.shape;mask=np.isfinite(t)&(t>=he[0])&(t<=he[-1])&(v!=0)
 i,j=np.nonzero(mask)
 if not len(i):return 0.,0.
 q=t[i,j];a=v[i,j];k=np.minimum(np.searchsorted(he,q,side='right')-1,len(he)-2);w=(q-he[k])/(he[k+1]-he[k])
 np.add.at(arr,(k,i,j),a*(1-w));np.add.at(arr,(k+1,i,j),a*w)
 return float(np.sum(a)),float(np.sum(a*(q-he[0])))
def build(t0,end,events,jump0,src,lr,p0,ge,F,baseline,model_at,interpF,depth,npred,threshold):
 he=np.linspace(t0,end,npred+1);dt=he[1]-he[0];nr=len(p0)
 Fs=interpF(ge,F,he)
 p=np.linalg.solve(np.swapaxes(Fs,-1,-2),np.broadcast_to(p0.T,(len(he),3,nr)))
 ell=he[:,None]-np.log(np.linalg.norm(p,axis=1))
 assert np.min(np.diff(ell,axis=0))>0
 # Separate generation arrays. Use precomputed response objects at every predictor knot.
 ops=[]
 for u in he:
  x,T=[np.interp(u,baseline[:,0],baseline[:,k]) for k in [1,2]]
  ss,r,w=model_at(u,x,T);ops.append(JumpResponse(ss,r,w))
 c=np.zeros((len(he),nr,314));c[0]=jump0;prev=None
 stats=[];idx=np.arange(nr)[:,None]
 for gen in range(1,depth+1):
  inc=np.zeros((len(he),nr,313));mass=moment=0.
  if gen==1:
   m,p=deposit(inc,he,events,jump0[:,src]);mass+=m;moment+=p
  else:
   for j in range(len(he)-1):
    v=prev[j][:,src]
    if not np.any(v):continue
    tar=ell[j,:,None]+lr[None,:];t=np.empty_like(tar)
    for i in range(nr):
     t[i]=np.interp(tar[i],ell[:,i],he,left=np.inf,right=np.inf)
    # no simulated advanced response; generation approximation may place a jump at a nearby knot
    assert np.all(t[np.isfinite(t)]>he[j])
    m,p=deposit(inc,he,t,v);mass+=m;moment+=p
  dm=float(np.sum(inc));dp=float(np.einsum('t,tij->',he-t0,inc))
  l1=float(np.sum(abs(inc)))
  assert abs(dm-mass)<=2e-13*max(l1,1e-300) and abs(dp-moment)<=2e-13*max(l1*(end-t0),1e-300)
  if prev is None:prev=np.zeros_like(c)
  else:prev.fill(0.)
  direct=coupled=dropped=0.;count=0
  for j,op in enumerate(ops):
   z=inc[j]
   if threshold>0:
    mask=abs(z)<threshold;dropped+=float(np.sum(abs(z[mask])));z[mask]=0.
   if not np.any(z):continue
   a,b,_=op.apply(z);prev[j]=a+b;direct+=float(np.sum(abs(a)));coupled+=float(np.sum(abs(b)));count+=1
  del inc
  c+=prev
  stats.append(dict(gen=gen,active_buckets=count,incident_l1=l1,direct_l1=direct,coupled_l1=coupled,dropped_incident_l1=dropped,mass_residual=dm-mass,first_moment_residual=dp-moment))
 del prev,ops
 np.cumsum(c,axis=0,out=c)
 return Ledger(he,c,dict(predictor_intervals=npred,threshold=threshold,generations=stats,scope='actual prior gas frozen for predictor only; bucketed arrivals, residual exact at accepted nodes; not rigorous continuum convergence'))
def test():
 h=np.array([0.,.2,.4,.6,1.]);x=np.zeros((len(h),2,2));t=np.array([[.1,.31],[.9,np.inf]]);v=np.array([[2.,-3.],[5.,7.]])
 a,b=deposit(x,h,t,v)
 assert abs(a-x.sum())<1e-14 and abs(b-np.einsum('t,tij->',h,x))<1e-14
 c=np.cumsum(x,axis=0);q=Ledger(h,c,{})
 u,z=q.means(np.array([[-.1,-.1],[-.1,-.1]]),np.array([[.5,.5],[.5,.5]]),np.arange(2))
 # compare direct piecewise constant integral with elementary formula.
 direct=np.zeros((2,2));fm=direct.copy()
 for j in range(len(h)-1):
  lo=max(h[j],-.1);hi=min(h[j+1],.5)
  if hi>lo:direct+=c[j]*(hi-lo)/.6;fm+=c[j]*((hi+.1)**2-(lo+.1)**2)/(2*.6**2)
 assert np.max(abs(u-direct))<1e-14 and np.max(abs(z-fm))<1e-14
 return dict(deposition_mass_error=float(abs(a-x.sum())),moment_error=float(abs(b-np.einsum('t,tij->',h,x))),integral_error=float(np.max(abs(u-direct))))
if __name__=='__main__':print(test())

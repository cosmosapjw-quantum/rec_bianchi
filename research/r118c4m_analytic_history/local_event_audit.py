"""Reconstruct actual baseline prefix and replay both analytic and shrinking map directional stencils."""
from pathlib import Path
import sys,json,time,numpy as np,hashlib
D=Path(__file__).resolve().parent;P=D.parent;K=P/'r118c4k_lambda_tangent'
sys.path.insert(0,str(K))
import rec as prior
sys.path.insert(0,str(D))
from event import Events
from numpy.polynomial.legendre import leggauss
c=prior.context(128);z=np.load(P/'r118c4h_goal_adjoint/goal_q3_128_-0.5.npz');he=z['he'];v=z['rows'][:,1:3];c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he;nr=c.nr
lam=-.5;m=prior.Map(c,lam);ev=Events(m);A=np.zeros((100,nr,314,7));DA=np.zeros((2,*A.shape));gl,gw=leggauss(5);checks=[]
def owner(u,y,w,j,a,wgt):
 s,HH,Tr=c.snap(u,*y,c.zero);rr,o,_=prior.p.step(s,a,np.zeros((nr,313)),wgt);jr=prior.JumpResponse(s,a,wgt)
 oo=[];gg=0.
 for k in range(3):
  aa,b,g=jr.apply(w[k]);oo.append(prior.mass[k,j]*o+aa+b)
  if k==0:gg=prior.mass[0,j]*rr.dxHII_dln_a+g
 return np.array(oo),gg,jr
for i in range(1,101):
 l,r=he[i-1:i+1];h=r-l;mid=(l+r)/2
 U=m.mom3(i,l,r,A)
 if i in [63,99,100]:
  u,d=ev.integrate(i,l,r,A,DA);assert np.array_equal(u,U)
  # Observable gas force projection of geometry-only weak-map derivative.
  def gas_force(d0):
   dw=np.einsum('kjm,mrc->kjrc',prior.L,d0);total=0.
   for j,t in enumerate([l,mid,r]):
    y=(1-j/2)*v[i-1]+j/2*v[i];a,w=m.state(t);_,_,jr=owner(t,y,np.zeros((3,nr,313)),j,a,w)
    total+=jr.apply(dw[0,j])[2]
   return total
  rows=[];near=[]
  for side,u0 in [('left',l),('right',r)]:
   t=m.t(u0);j0=np.searchsorted(he[:i],t);a0=np.clip(j0-1,0,i-1);b0=np.clip(j0,0,i-1);j=np.where(abs(t-he[a0])<abs(t-he[b0]),a0,b0);sk=he[j];q=m.ev(m.f,sk)+m.lr;cr=m.ev(m.g,q);valid=np.isfinite(cr)&(j<i-1);safe=np.where(valid,cr,u0);dc=(ev.ev(ev.fl,sk)-ev.ev(ev.fl,safe))/ev.ev(m.f,safe,1);cross_h=np.divide(u0-cr,dc,out=np.full_like(cr,np.inf),where=dc!=0)
   for ri,ci in np.argwhere(valid&(abs(cross_h)<.0031)):
    k=int(j[ri,ci]);ch=int(c.src[ci]);before=float(A[k-1,ri,ch].sum()) if k else 0.;after=float(A[k,ri,ch]@((-1.)**np.arange(7)))
    near.append(dict(side=side,ray=int(ri),channel=int(ci),distance=float(cr[ri,ci]-u0),arrival_derivative=float(dc[ri,ci]),crossing_parameter=float(cross_h[ri,ci]),jump=before-after))
  for eps in [.003,.001,.0003,.0001,3e-5,1e-5,3e-6,1e-6]:
   for j,sg in enumerate([1,-1]):
    p=prior.Map(c,lam+sg*eps);f=(p.mom3(i,l,r,A)-U)/eps;row=dict(eps=eps,direction=sg,relative=float(np.linalg.norm(f-d[j])/max(np.linalg.norm(f),1e-300)),analytic_gas_force=float(gas_force(d[j])),secant_gas_force=float(gas_force(f)))
    rows.append(row)
  checks.append(dict(step=i,aligned=[x for x in ev.aligned if x['step']==i],near=near,rows=rows));print('step',i,'aligned',len(checks[-1]['aligned']),'near',len(near),'last',rows[-2:],flush=True)
 for t,wt in zip(gl,gw):
  q=(t+1)/2;u=l+h*q;R=m.t(u)-(u-c.lr);b=prior.p._planck_difference(c.ef[None,:]/(prior.p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u)),R)
  for k in range(5):U[k]+=wt/2*b*q**k
 W=np.einsum('kjm,mrc->kjrc',prior.L,U);O=np.zeros((3,nr,314))
 for j,u in enumerate([l,mid,r]):
  y=(1-j/2)*v[i-1]+j/2*v[i];a,w=m.state(u);o,g,jr=owner(u,y,W[:,j],j,a,w);O+=o
 fr=1/np.expm1(c.tab.energy_eV/(prior.p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-r)));co,ls,_=prior.reconstruct(O,fr);A[i-1]=co;assert not ls
out=dict(checks=checks,scope='actual nominal history through 100 steps; geometry-only analytic vs finite weak map, shrinking stencils and near-boundary crossings, no independent atomic history rerun')
(D/'LOCAL_EVENT_AUDIT.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')

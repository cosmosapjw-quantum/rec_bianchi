"""Projected second-order singular feedback on actual accepted scalar mesh.
Retain A delta and B delta' separately; use barycentric time projection.
T1 of first-order angular impulses is evaluated at actual arrival times.
T0' uses native transfer derivative on interpolated accepted reference.
"""
import numpy as np,json,sys
from pathlib import Path
from regular import Context
from atomic_jet import atomic_jet
from gain_jet import rate_weight
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3n_jump_response'))
from jump_response import JumpResponse
def run(nt):
 c=Context(nt);he=c.he;N=len(he);nr=c.nr;lr=c.lr;src=c.src
 prior=np.load(D.parent/f'r118c3s_impulse_tangent/impulse_{nt}.npz')
 initial=np.load(D/f'regular_{nt}.npz')['initial_first']
 SA=np.zeros((N,313));SB=SA.copy();FA=SA.copy();FB=SA.copy()
 ledger=dict(seed_l1_A=0.,seed_l1_B=0.,cross_l1=0.,propagated_l1_A=0.,propagated_l1_B=0.,max_projection_A=0.,max_projection_B=0.)
 def deposit(A,B,t,ch,a,b):
  t,ch,a,b=np.broadcast_arrays(t,ch,a,b)
  mask=(t>=he[0])&(t<=he[-1]);t,ch,a,b=[x[mask] for x in [t,ch,a,b]]
  if not len(t):return
  j=np.searchsorted(he,t,side='right')-1;j=np.minimum(j,N-2);s=(t-he[j])/(he[j+1]-he[j]);l=1-s
  np.add.at(A,(j,ch),l*a);np.add.at(A,(j+1,ch),s*a);np.add.at(B,(j,ch),l*b);np.add.at(B,(j+1,ch),s*b)
  # projection exact on affine test functions (use shifted u to avoid roundoff)
  er=lambda f:float(np.sum(abs(l*f+s*f-f))/max(np.sum(abs(f)),1e-300))
  ledger['max_projection_A']=max(ledger['max_projection_A'],er(a));ledger['max_projection_B']=max(ledger['max_projection_B'],er(b))
 def bcs(s,u):
  n=c.n[None,:,:];b0,d0,bp0=c.clock.bc(np.asarray(s)[:,None],n);b1,d1,bp1=c.clock.bc(np.asarray(u)[:,None],n);a=b0-b1
  return a,d0-d1+bp0*a,bp0-bp1
 # Continuous baseline interpolation has an initial value jump and derivative
 # jumps at every accepted knot. Retain their order-2 singular terms.
 h=np.diff(he);Dleft=(-3*c.L[:,0]+4*c.M[:,0]-c.R[:,0])/h[:,None];Dright=(c.L[:,0]-4*c.M[:,0]+3*c.R[:,0])/h[:,None]
 K=Dleft.copy();K[1:]-=Dright[:-1]
 for j,s0 in enumerate(src):
  t=he[:-1];u=t+lr[j];ok=u<=he[-1];t,u=t[ok],u[ok]
  if not len(t):continue
  a,b,ap=bcs(t,u);aa=.5*K[:len(t),s0,None]*a*a;bb=np.zeros_like(aa)
  J=c.L[0,0,s0]
  aa[0]+=J*(b[0]-a[0]*ap[0])+a[0]*initial[:,s0]
  bb[0]+=.5*J*a[0]*a[0]
  a0=aa@c.w;b0=bb@c.w;deposit(SA,SB,u,j,a0,b0)
  ledger['seed_l1_A']+=float(np.sum(abs(a0)));ledger['seed_l1_B']+=float(np.sum(abs(b0)))
 # First-order outgoing impulse pullback and angular derivative T1 A1.
 for idx,(u,j,amp,gen) in enumerate(zip(prior['event_time'],prior['event_channel'],prior['event_mass'],prior['event_generation'])):
  j=int(j);gen=int(gen);u=float(u)
  if gen>=2:
   a,b,ap=bcs(np.array([u-lr[j]]),np.array([u]))
   a2=-float(c.w@(ap[0]*amp));b2=float(c.w@(a[0]*amp));deposit(SA,SB,u,j,a2,b2)
   ledger['seed_l1_A']+=abs(a2);ledger['seed_l1_B']+=abs(b2)
  x,T=c.xy(u);s,H,Tr=c.snap(u,x,T,c.zero);ar,wr=rate_weight(c.clock,u,c.w)
  I=np.zeros((3,nr,313));I[0,:,j]=amp
  O,F=atomic_jet(s,ar,wr,I,homogeneous=True);cross=c.w@O[1]
  deposit(FA,FB,u+lr,np.arange(313),cross[src],np.zeros(313))
  ledger['cross_l1']+=float(np.sum(abs(cross)))
  if idx%1200==0:print('cross',nt,idx,flush=True)
 # Snapshot homogeneous transfer and scalar gain. At baseline only mean
 # of I2 matters, so the dense coupling is exactly represented in 1 ray.
 def transfer(u,I):
  x,T=c.xy(u);s,H,Tr=c.snap(u,x,T,c.zero)
  a,b,g=JumpResponse(s,np.ones(1),np.ones(1)).apply(I[None,:])
  return a[0]+b[0],g
 gasjump=np.zeros((N,2));gasA=np.zeros(N);gasB=np.zeros(N);gas_feedback_A=np.zeros(N);gas_feedback_B=np.zeros(N);OA=np.zeros((N,314));OB=OA.copy()
 max_causal=0.;gas_singular_l1=0.;count=0
 for i,u in enumerate(he):
  A=SA[i]+FA[i];B=SB[i]+FB[i]
  if not (np.any(A) or np.any(B)):continue
  count+=1
  x,T=c.xy(u);inc=c.base_inc(u);dx,dT=c.derivatives(u,x,T,inc);J=c.jac(u,x,T,inc,dx,dT)
  a,ga=transfer(u,A);b,gb=transfer(u,B)
  l=max(he[0],u-1e-7);r=min(he[-1],u+1e-7);assert r>l
  b1,g1=transfer(r,B);b0,g0=transfer(l,B);dB=(b1-b0)/(r-l);dg=(g1-g0)/(r-l)
  # Gas state itself contains gb delta in x2, giving an extra O_x gb
  # outgoing delta. Its regular jump is ga-dg+J e_x gb.
  a=a-dB+dx[1:]*gb;gas_singular_l1+=float(np.sum(abs(dx[1:]*gb)))
  gasA[i]=ga-dg;gasB[i]=gb;OA[i]=a;OB[i]=b
  # Base geometry and first-order incoming singular weak source already
  # in C3R/C3S. Add only second outgoing feedback to regular gas evolution.
  _,fa=transfer(u,FA[i]);_,fb=transfer(u,FB[i]);_,p1=transfer(r,FB[i]);_,p0=transfer(l,FB[i])
  gas_feedback_A[i]=fa-(p1-p0)/(r-l);gas_feedback_B[i]=fb
  gasjump[i]=np.array([gas_feedback_A[i],0.])+J[:,0]*fb
  t=u+lr;ok=t<=he[-1]
  # Earliest projected destination cannot be current/past: dt<min delay.
  if ok.any():
   dest=np.searchsorted(he,t[ok],side='right')-1
   assert min(dest)>i,(i,min(dest),min(lr),max(np.diff(he)))
  deposit(FA,FB,t,np.arange(313),a[src],b[src]);ledger['propagated_l1_A']+=float(np.sum(abs(a)));ledger['propagated_l1_B']+=float(np.sum(abs(b)))
  if i%128==0:print('event',nt,i,float(gasjump[i,0]),flush=True)
 assert np.isfinite(gasjump).all()
 np.savez_compressed(D/f'events_{nt}.npz',he=he,seed_A=SA,seed_B=SB,feedback_A=FA,feedback_B=FB,out_A=OA,out_B=OB,gas_jump=gasjump,gas_A=gasA,gas_B=gasB,gas_feedback_A=gas_feedback_A,gas_feedback_B=gas_feedback_B)
 o=dict(nt=nt,steps=N-1,occupied_nodes=count,source_first_events=len(prior['event_time']),ledger=ledger,gas_singular_source_l1=gas_singular_l1,gas_jump_sum=gasjump.sum(axis=0).tolist(),gas_jump_l1=np.sum(abs(gasjump),axis=0).tolist(),scope='second-order radiative delta/delta-prime projected separately onto accepted time nodes, native dense Schur and T1 coupling, time derivative T0 via finite difference, instantaneous scalar singular gas feedback; approximate weak projection, regular jumps feed regular owner; baseline piecewise quadratic, not full continuum')
 (D/f'events_{nt}.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run(int(sys.argv[1]))

"""Unified weak second outgoing moments on actual native reference history.
The second-order history is a cellwise affine weak projection (not exact
distribution propagation). All source derivatives enter via weak action.
"""
import numpy as np,sys,json
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'r118c3t_second_tangent'
sys.path.insert(0,str(P))
from regular import Context
from atomic_jet import atomic_jet
from gain_jet import rate_weight
from weak_moments import moments,derivatives
def run(nt):
 if nt==128:
  # Reuse exact Context constructor but redirect the two reference loads.
  import regular
  from unittest.mock import patch
  original=np.load
  def load(path,*a,**k):
   path=Path(path)
   if path.name in ['frozen_1110_128.npz','z1110_n128_0.npz']:path=D/path.name
   return original(path,*a,**k)
  with patch.object(np,'load',load):c=Context(nt)
 else:c=Context(nt)
 he=c.he;v=c.v;N=len(he)-1;nr=c.nr;src=c.src;lr=c.lr;w=c.w
 L1=np.zeros((N,nr,314));M1=L1.copy();R1=L1.copy()
 L2=np.zeros((N,1,314));M2=L2.copy();R2=L2.copy()
 old=np.load(D/f'impulse_{nt}.npz' if nt==128 else D.parent/f'r118c3s_impulse_tangent/impulse_{nt}.npz')
 ev=old['event_time'];ch=old['event_channel'];amp=old['event_mass'];gen=old['event_generation'];maxbase=0.;maxmean=0.;max_proj=0.;max_first_mean=0.;min_edge=np.inf;tot=np.zeros(2);rows=[]
 def face(u,x,T,obase,i):
  nonlocal maxbase,maxmean
  f,df,_=c.sample(u,c.L,c.M,c.R,i,nr);g,_,_=c.sample(u,L1,M1,R1,i,nr)
  s,H,Tr=c.snap(u,x,T,f[0]);a,ww=rate_weight(c.clock,u,w);a1,a2=c.clock.ret(u,lr)
  z=c.ef/(c.p.KB_NATIVE_EV_K*Tr) if hasattr(c,'p') else c.ef/(8.617333262145e-5*Tr)
  # Use exact source constant from reference module, not guessed kB.
  from regular import p
  z=c.ef/(p.KB_NATIVE_EV_K*Tr);ff=1/np.expm1(z);f1=-z*ff*(1+ff);f2=.5*ff*(1+ff)*(z*z*(1+2*ff)-z)
  geom1=a1*f1;geom2=a2*f1+a1*a1*f2
  I=np.array([f,g+a1*df+geom1,np.zeros_like(f)]);o,F=atomic_jet(s,a,ww,I)
  maxbase=max(maxbase,float(np.max(abs(o[0]-obase))));maxmean=max(maxmean,float(np.max(abs(w@o[1]))))
  z0,F0=atomic_jet(s,a,ww,np.zeros_like(I));dx,dT=c.derivatives(u,x,T,f[0]);J=c.jac(u,x,T,f[0],dx,dT)
  return dict(s=s,a=a,w=ww,t1=a1,t2=a2,g1=geom1,g2=geom2,first=o[1],constant=w@z0[2],constant_gas=F0[2],dx=dx,dT=dT,J=J)
 def lin(x,y,k):return x/(k+1)+(y-x)/(k+2)
 def localmom(i,l,r,A,B):
  nonlocal min_edge
  h=r-l;ta=np.broadcast_to(l-lr,(nr,313));tb=np.broadcast_to(r-lr,(nr,313))
  if i==1:m0=np.zeros((4,nr,313));m1=m0.copy();m2=m0.copy();d0=np.zeros((5,nr,313));dd0=d0.copy();d1=d0.copy()
  else:
   m0=moments(he[:i],c.L[:i-1],c.M[:i-1],c.R[:i-1],ta,tb,src)
   m1=moments(he[:i],L1[:i-1],M1[:i-1],R1[:i-1],ta,tb,src)
   m2=moments(he[:i],L2[:i-1],M2[:i-1],R2[:i-1],ta,tb,src)
   fl,dl,_=c.sample(l,c.L,c.M,c.R,i,nr);fr,dr,_=c.sample(r,c.L,c.M,c.R,i,nr)
   g0,h0,_=c.sample(l,L1,M1,R1,i,nr);g1,h1,_=c.sample(r,L1,M1,R1,i,nr)
   # distribution derivatives of the accepted piecewise quadratic history,
   # boundary evaluation is right-continuous. No endpoint initial jumps expected.
   min_edge=min(min_edge,float(min(np.min(abs(ta-he[0])),np.min(abs(tb-he[0])))))
   d0,dd0=derivatives(m0,fl,fr,dl,dr,h)
   d1,_=derivatives(m1,g0,g1,h0,h1,h)
  a=A['t1'];da=B['t1']-a;b=A['t2'];db=B['t2']-b
  I1=[];I2=[]
  # incoming first-order impulse gen1 arises from f0 derivative, so add
  # only propagated gen>=2; C3S mass is incoming at this arrival.
  mask=(ev>l)&(ev<=r)&(gen>=2);ids=np.flatnonzero(mask)
  for k in range(3):
   u=m1[k]+a*d0[k]+da*d0[k+1]+lin(A['g1'],B['g1'],k)
   v2=m2[k]+a*d1[k]+da*d1[k+1]+b*d0[k]+db*d0[k+1]+.5*(a*a*dd0[k]+2*a*da*dd0[k+1]+da*da*dd0[k+2])+lin(A['g2'],B['g2'],k)
   for j in ids:
    z=(ev[j]-l)/h;g=int(ch[j]);C=amp[j];u[:,g]+=C*z**k/h
    v2[:,g]-=C*(da[:,g]*z**k+(a[:,g]+z*da[:,g])*k*z**(k-1) if k else da[:,g])/h**2
   I1.append(u);I2.append(v2)
  return np.array([m0[:3],I1,I2])
 def operator(A,I):
  out,F=atomic_jet(A['s'],A['a'],A['w'],I,homogeneous=True);return w@out[2],F[2]
 q=face(he[0],*v[0,1:3],c.L[0,0],1);L1[0]=q['first'];y=np.zeros(2)
 for i,r in enumerate(he[1:],1):
  l=he[i-1];h=r-l;mid=(r+l)/2;xm,Tm=(v[i-1,1:3]+v[i,1:3])/2
  a=face(mid,xm,Tm,c.M[i-1,0],i);b=face(r,*v[i,1:3],c.R[i-1,0],i)
  I=localmom(i,l,r,q,b);max_first_mean=max(max_first_mean,float(np.max(abs(np.einsum('r,krj->kj',w,I[1])))))
  O=[];F=[]
  for k in [0,1]:
   x,fx=operator(q,I[:,k]-I[:,k+1]);z,fz=operator(b,I[:,k+1])
   O.append(x+z+lin(q['constant'],b['constant'],k));F.append(fx+fz+lin(q['constant_gas'],b['constant_gas'],k))
  J=a['J'];yn=np.linalg.solve(np.eye(2)-h*J/2,(np.eye(2)+h*J/2)@y+h*np.array([F[0],0.]))
  # use midpoint gas derivative of outgoing, linear in gas perturbation;
  # preserve zeroth/first weak time moments of this approximation.
  g0=a['dx'][1:]*y[0]+a['dT'][1:]*y[1];g1=a['dx'][1:]*yn[0]+a['dT'][1:]*yn[1]
  o0=O[0]+(g0+g1)/2;o1=O[1]+g0/6+g1/3
  L2[i-1,0]=4*o0-6*o1;R2[i-1,0]=6*o1-2*o0;M2[i-1,0]=o0
  err=np.max(abs((L2[i-1,0]+R2[i-1,0])/2-o0))/max(np.max(abs(o0)),1e-300);max_proj=max(max_proj,float(err))
  M1[i-1]=a['first'];R1[i-1]=b['first']
  if i<N:L1[i]=R1[i-1]
  # L2 not copied; each interval owns two moments independently.
  y=yn;q=b;tot+=h*np.array(F);rows.append([r,*y,*F,float(np.linalg.norm(o0)),float(np.linalg.norm(o1))])
  if i%128==0:print(nt,i,y,flush=True)
 err=float(np.linalg.norm(R1[-1]-old['final_regular'])/max(np.linalg.norm(old['final_regular']),1e-300))
 assert maxbase<1e-24 and maxmean<1e-20 and err<1e-4
 np.savez_compressed(D/f'weak_{nt}.npz',rows=np.array(rows),he=he,L2=L2,M2=M2,R2=R2,final_first=R1[-1])
 o=dict(nt=nt,steps=N,x2=float(y[0]),T2=float(y[1]),first_reproduction=err,reference_abs=maxbase,first_out_mean=maxmean,first_in_weak_mean=max_first_mean,max_projection=max_proj,min_initial_event_edge=min_edge,integrated_forcing=tot.tolist(),scope='actual H-only fixed scalar clock, unified weak input order2 and affine outgoing moment projection; endpoint native transfer interpolation, first-order impulse ledger and approximate gas Jacobian. No exact event aligned continuum or HHe donor.')
 (D/f'weak_{nt}.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run(int(sys.argv[1]))

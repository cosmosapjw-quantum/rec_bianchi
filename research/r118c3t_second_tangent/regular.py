"""Second-order regular outgoing feedback on the actual accepted scalar history.
Separate singular event owner supplies optional endpoint jumps. No full continuum
claim: baseline is C3P piecewise-quadratic radiation and frozen scalar H clock.
"""
import sys,json,numpy as np
from pathlib import Path
from dataclasses import replace
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3r_retarded_tangent'))
from frozen import p,ClockJet,rate_weight
from atomic_jet import atomic_jet
from gain import gain
class Context:
 def __init__(self,nt):
  self.nt=nt;self.prior=D.parent/'r118c3r_retarded_tangent';self.z=np.load(self.prior/f'frozen_1110_{nt}.npz');self.he=self.z['he'];self.L,self.M,self.R=[self.z[k] for k in ['L','M','R']]
  self.refpath=D.parent/f'r118c3p_prehistory/z1110_n{nt}_0.npz';self.v=np.load(self.refpath)['rows']
  mu,w=leggauss(4);m,ph=np.meshgrid(mu,np.arange(8)*np.pi/4,indexing='ij');self.n=np.stack([np.sqrt(1-m*m)*np.cos(ph),np.sqrt(1-m*m)*np.sin(ph),m],axis=-1).reshape(-1,3);self.w=np.repeat(w/16,8);self.w/=self.w.sum();self.nr=len(self.w)
  self.clock=ClockJet(self.n,self.he[0]);self.g=np.genfromtxt(p.B/'plusfine.csv',names=True,delimiter=',');self.ge=np.log(self.g['a'])
  self.model=p.Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=p.OriginalHyRecPrimitiveRateTable.from_archive(p.R))
  self.tab=p._canonical_twophoton_table(p.R);self.src,self.ef,self.es=p._source_edges(self.tab.energy_eV);self.lr=np.log(self.es/self.ef)
  self.zero=np.zeros(313)
 def xy(self,u):return np.array([np.interp(u,self.he,self.v[:,j]) for j in [1,2]])
 def snap(self,u,x,T,inc):
  zz=np.expm1(-u);H=np.interp(u,self.ge,self.g['h'])*2.1842852410855023e-18;so=replace(self.model,H=H)
  return p.populate_original_full_atomic(so,z=zz,xHII=x,xe=x,Tm_K=T,incoming_virtual=inc[:311],incoming_lyman=inc[311:]),H,self.model.tcmb0_K*(1+zz)
 def sample(self,u,A,B,C,i,nr):
  t=np.broadcast_to(u-self.lr,(nr,313));k=np.searchsorted(self.he[:i],t,side='right')-1;before=k<0
  if i==1:
   assert np.all(before);q=np.zeros_like(t);return q,q.copy(),q.copy()
  assert np.max(t)<self.he[i-1]
  k=np.clip(k,0,i-2);j=self.src[None,:];ray=np.arange(nr)[:,None] if A.shape[1]==nr else 0;h=self.he[k+1]-self.he[k];z=np.where(before,0.,(t-self.he[k])/h)
  a=A[k,ray,j];b=B[k,ray,j];c=C[k,ray,j]
  f=(1-3*z+2*z*z)*a+(4*z-4*z*z)*b+(2*z*z-z)*c;df=((-3+4*z)*a+(4-8*z)*b+(4*z-1)*c)/h;ddf=(4*a-8*b+4*c)/h**2
  return tuple(np.where(before,0.,q) for q in [f,df,ddf])
 def base_inc(self,u):
  i=min(len(self.he),int(np.searchsorted(self.he,u,side='left'))+1)
  return self.sample(u,self.L,self.M,self.R,i,1)[0][0]
 def derivatives(self,u,x,T,inc):
  def ev(xx,tt):
   s,H,Tr=self.snap(u,xx,tt,inc);a,o,err=p.step(s,np.ones(1),inc[None,:],np.ones(1));return np.r_[a.dxHII_dln_a,o[0]]
  ex=1e-6;et=.01;dx=(ev(x+ex,T)-ev(x-ex,T))/(2*ex);dT=(ev(x,T+et)-ev(x,T-et))/(2*et)
  return dx,dT
 def jac(self,u,x,T,inc,dx,dT):
  s,H,Tr=self.snap(u,x,T,inc);scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4/H;A=scale*x/(1+x+self.model.f_he);Ax=scale*(1+self.model.f_he)/(1+x+self.model.f_he)**2
  return np.array([[dx[0],dT[0]],[Ax*(Tr-T),-2-A]])
def run(nt,with_events=False):
 c=Context(nt);he=c.he;v=c.v;N=len(he)-1;shape=(N,c.nr,314);shape2=(N,1,314)
 L1=np.zeros(shape);M1=L1.copy();R1=L1.copy();L2=np.zeros(shape2);M2=L2.copy();R2=L2.copy()
 old=np.load(D.parent/f'r118c3s_impulse_tangent/impulse_{nt}.npz');fr=c.z['rows'];extra=old['rows']
 assert np.array_equal(fr[:,0],he[1:]) and np.array_equal(extra[:,0],he[1:])
 jumps=np.zeros((len(he),2))
 if with_events:jumps=np.load(D/f'events_{nt}.npz')['gas_jump']
 checks=[];maxbase=0.;maxmean=0.;basecheck=0.
 def face(u,x,T,obase,i):
  nonlocal maxbase,maxmean
  f,df,ddf=c.sample(u,c.L,c.M,c.R,i,c.nr);g,dg,_=c.sample(u,L1,M1,R1,i,c.nr);j0,_,_=c.sample(u,L2,M2,R2,i,1)
  ss,H,Tr=c.snap(u,x,T,f[0]);a,w=rate_weight(c.clock,u,c.w);t1,t2=c.clock.ret(u,c.lr);xx=c.ef/(p.KB_NATIVE_EV_K*Tr);ff=1/np.expm1(xx);f1=-xx*ff*(1+ff);f2=.5*ff*(1+ff)*(xx*xx*(1+2*ff)-xx)
  I=np.array([f,g+t1*(df+f1),j0+t1*dg+t2*(df+f1)+t1*t1*(.5*ddf+f2)])
  out,F=atomic_jet(ss,a,w,I)
  maxbase=max(maxbase,float(np.max(abs(out[0]-obase))))
  maxmean=max(maxmean,float(np.max(abs(c.w@out[1]))))
  if i in [1,N//2,N] and len(checks)<12:
   for ep in [.1,.05]:
    def ev(z):
     rate=a[0]+z*a[1]+z*z*a[2];wt=w[0]+z*w[1]+z*z*w[2];inc=I[0]+z*I[1]+z*z*I[2];r,o,err=p.step(ss,rate,inc,wt);return o
    op,om=ev(ep),ev(-ep);o0=ev(0);v1=(op-om)/(2*ep);v2=(op+om-2*o0)/(2*ep*ep)
    checks.append(dict(u=u,ep=ep,first_relative=float(np.linalg.norm(v1-out[1])/max(np.linalg.norm(out[1]),1e-300)),second_relative=float(np.linalg.norm(v2-out[2])/max(np.linalg.norm(out[2]),1e-300)),base_abs=float(np.max(abs(o0-out[0])))))
  dx,dT=c.derivatives(u,x,T,f[0]);G=gain(ss,np.ones(1),np.ones(1))
  return out[1],(c.w@out[2])[None,:],dx,dT,G,c.jac(u,x,T,f[0],dx,dT)
 def corrected(face,y):
  return face[1]+(face[2][1:]*y[0]+face[3][1:]*y[1])[None,:]
 u0=he[0];q=face(u0,*v[0,1:3],c.L[0,0],1);L1[0]=q[0];L2[0]=q[1];initial=L1[0].copy()
 y=np.zeros(2);rows=[];extra_int=0.
 for i,u in enumerate(he[1:],1):
  l=he[i-1];h=u-l;mid=(l+u)/2;xm,Tm=(v[i-1,1:3]+v[i,1:3])/2
  a=face(mid,xm,Tm,c.M[i-1,0],i);b=face(u,*v[i,1:3],c.R[i-1,0],i)
  fb=0.
  if i>1:
   for lo,hi,A,B in [(l,mid,q,a),(mid,u,a,b)]:
    t0=(lo-c.lr)[None,:];t1=(hi-c.lr)[None,:]
    U,V=p.local_means(he[:i],L2[:i-1],M2[:i-1],R2[:i-1],t0,t1,c.src)
    fb+=.5*float(np.sum(A[4]*U+(B[4]-A[4])*V))
  F=fr[i-1,10]+extra[i-1,5]+extra[i-1,6]+fb
  J=a[5];I=np.eye(2);yn=np.linalg.solve(I-h*J/2,(I+h*J/2)@y+h*np.array([F,0.]))+jumps[i]
  M1[i-1]=a[0];R1[i-1]=b[0];M2[i-1]=corrected(a,(y+yn-jumps[i])/2);R2[i-1]=corrected(b,yn)
  if i<N:L1[i]=R1[i-1];L2[i]=R2[i-1]
  y=yn;q=b;extra_int+=h*fb;rows.append([u,*y,F,fb,*jumps[i]])
  if i%128==0:print(nt,with_events,i,y,flush=True)
 a=np.array(rows);lab=f'regular_{nt}'+('_events' if with_events else '')
 # Use source identity from existing accepted reference, not separate numerical background.
 err1=float(np.linalg.norm(R1[-1]-old['final_regular'])/np.linalg.norm(old['final_regular']))
 assert maxbase<1e-24 and maxmean<1e-20 and err1<1e-4,(maxbase,maxmean,err1)
 np.savez_compressed(D/(lab+'.npz'),rows=a,L2=L2,M2=M2,R2=R2,initial_first=initial,final_first=R1[-1])
 o=dict(nt=nt,with_events=with_events,steps=N,x2=float(y[0]),T2=float(y[1]),integrated_regular_second_feedback=extra_int,max_reference_out_abs=maxbase,max_first_mean=maxmean,first_reproduction_relative=err1,jet_checks=checks,scope='regular order2 scalar gas and mean outgoing feedback, first order angular regular, partial distributional endpoint jumps if supplied; not full continuous tangent')
 (D/(lab+'.json')).write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run(int(sys.argv[1]),len(sys.argv)>2)

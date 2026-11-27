"""First outgoing tangent regular history and exact-time direct impulse chain.
Second-order gas receives their weak action, not full second-order outgoing feedback.
"""
import sys,json,numpy as np
from pathlib import Path
from dataclasses import replace
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import interp1d
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3r_retarded_tangent'))
from frozen import p,ClockJet,rate_weight,get,boundary
sys.path.insert(0,str(D.parent/'r118c3n_jump_response'))
from jump_response import JumpResponse
def run(nt):
 prior=D.parent/'r118c3r_retarded_tangent';z=np.load(prior/f'frozen_1110_{nt}.npz');he=z['he'];L,M,R=[z[k] for k in ['L','M','R']];refpath=D.parent/f'r118c3p_prehistory/z1110_n{nt}_0.npz';v=np.load(refpath)['rows'];N=len(he)-1
 mu,w=leggauss(4);m,ph=np.meshgrid(mu,np.arange(8)*np.pi/4,indexing='ij');n=np.stack([np.sqrt(1-m*m)*np.cos(ph),np.sqrt(1-m*m)*np.sin(ph),m],axis=-1).reshape(-1,3);w=np.repeat(w/16,8);w/=w.sum();nr=len(w)
 clock=ClockJet(n,he[0]);g=np.genfromtxt(p.B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a'])
 m=p.Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=p.OriginalHyRecPrimitiveRateTable.from_archive(p.R))
 tab=p._canonical_twophoton_table(p.R);src,ef,es=p._source_edges(tab.energy_eV);lr=np.log(es/ef);assert len(set(src))==len(src)
 inv={int(s):k for k,s in enumerate(src)}
 def snap(u,x,T,inc):
  zz=np.expm1(-u);H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;so=replace(m,H=H)
  return p.populate_original_full_atomic(so,z=zz,xHII=x,xe=x,Tm_K=T,incoming_virtual=inc[:311],incoming_lyman=inc[311:]),H,m.tcmb0_K*(1+zz)
 # event optical depths on actual baseline. Compute all endpoint and midpoint
 # snapshots later in regular history pass; interpolation of transmission for events.
 shape=(N,nr,314);Ld=np.zeros(shape);Md=np.zeros(shape);Rd=np.zeros(shape);zero=np.zeros((nr,313))
 times=[];taus=[];gainerr=[];maxmean=0.;max_ind=0.
 def face(u,x,T,obase,i):
  nonlocal maxmean,max_ind
  if i>1:
   t=np.broadcast_to(u-lr,(nr,313));f0,df0=boundary(he[:i],L[:i-1],M[:i-1],R[:i-1],t,src)
   prev=p.gather(he[:i],Ld[:i-1],Md[:i-1],Rd[:i-1],t,src)
  else:f0=df0=prev=zero
  ss,H,Tr=snap(u,x,T,f0[0]);a,ww=rate_weight(clock,u,w);t1,t2=clock.ret(u,lr);xx=ef/(p.KB_NATIVE_EV_K*Tr);f=1/np.expm1(xx)
  I=prev+t1*(df0-xx*f*(1+f));tau=ss.Dtau
  tr=-np.expm1(-tau);fac=np.divide(-tau*np.exp(-tau),tr,out=-np.ones_like(tau),where=tr>0)
  out=np.zeros((nr,314));out[:,:311]=np.exp(-tau)*I[:,:311]+a[1,:,None]*fac*(obase[:311]-f0[:,:311]);out[:, :311][:,tau<=1e-30]=I[:,:311][:,tau<=1e-30]
  maxmean=max(maxmean,float(np.max(abs(w@out))))
  if len(times)%128==0:
   a0,b0,dr=JumpResponse(ss,np.ones(nr),w).apply(I);den=max(np.max(abs(a0)),1e-300);max_ind=max(max_ind,float(np.max(abs(b0))/den))
  times.append(u);taus.append(tau.copy())
  B,G=get(ss,a,ww)
  return t1,G,out
 prev=face(he[0],*v[0,1:3],L[0,0],1);Ld[0]=prev[2]
 faces=[prev];mids=[];J=[]
 for i,u in enumerate(he[1:],1):
  l=he[i-1];mid=(l+u)/2;xm,Tm=(v[i-1,1:3]+v[i,1:3])/2
  a=face(mid,xm,Tm,M[i-1,0],i);b=face(u,*v[i,1:3],R[i-1,0],i);Md[i-1]=a[2];Rd[i-1]=b[2]
  if i<N:Ld[i]=b[2]
  mids.append(a);faces.append(b)
  inc=p.gather(he[:i],L[:i-1],M[:i-1],R[:i-1],(mid-lr)[None,:],src)[0] if i>1 else zero[0]
  def f(x,T):
   ss,H,Tr=snap(mid,x,T,inc);return p.step(ss,np.ones(1),inc[None,:],np.ones(1))[0].dxHII_dln_a
  ex=1e-6;et=.01;Fx=(f(xm+ex,Tm)-f(xm-ex,Tm))/(2*ex);FT=(f(xm,Tm+et)-f(xm,Tm-et))/(2*et)
  ss,H,Tr=snap(mid,xm,Tm,inc);scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4/H;A=scale*xm/(1+xm+m.f_he);Ax=scale*(1+m.f_he)/(1+xm+m.f_he)**2
  J.append([[Fx,FT],[Ax*(Tr-Tm),-2-A]])
 # First-order impulses: t1(u) J at arrival of the baseline initial
 # jump. Propagate direct transmission through exact source graph at lambda0.
 t=np.array(times);tau=np.array(taus);events=[];generation={};max_event_mean=0.;checks=[]
 def deposit(u,k,amp,gen):
  nonlocal max_event_mean
  events.append((u,k,amp.copy(),gen));max_event_mean=max(max_event_mean,float(abs(w@amp)))
  a=generation.setdefault(gen,[0,0.,0.]);a[0]+=1;a[1]+=float(np.sum(abs(amp)))
  if k>=311:return None
  z=np.interp(u,t,tau[:,k]);trans=np.exp(-z) if z>1e-30 else 1.
  b=amp*trans;a[2]+=float(np.sum(abs(b)))
  if k not in inv:return None
  kk=inv[k];return u+lr[kk],kk,b,gen+1
 for k in range(len(lr)):
  u=he[0]+lr[k]
  if u>he[-1]:continue
  t1=clock.ret(u,np.array([lr[k]]))[0][:,0];amp=t1*L[0,0,src[k]]
  a=(u,k,amp,1)
  while a is not None and a[0]<=he[-1] and np.any(a[2]):
   assert a[3]<=int((he[-1]-he[0])/min(lr))+1
   a=deposit(*a)
 events.sort(key=lambda x:x[0]);ev=np.array([a[0] for a in events]);assert np.all(np.diff(ev)>=0)
 # At selected actual first arrival events audit full affine response against
 # direct-only transfer. Because all ray masses are zero mean, coupling vanishes.
 for u,k,a,gen in events[::max(1,len(events)//16)]:
  if k>=311 or not np.any(a):continue
  x,T=[np.interp(u,he,v[:,q]) for q in [1,2]];ss,H,Tr=snap(u,x,T,zero[0]);inp=zero.copy();inp[:,k]=a
  direct,coupled,dr=JumpResponse(ss,np.ones(nr),w).apply(inp)
  trans=np.exp(-ss.Dtau[k]);want=trans*a;got=direct[:,k]
  checks.append(dict(u=u,channel=k,gen=gen,direct_relative=float(np.linalg.norm(got-want)/max(np.linalg.norm(want),1e-300)),coupled_relative=float(np.linalg.norm(coupled)/max(np.linalg.norm(inp),1e-300)),scalar_relative=float(abs(dr)/max(np.linalg.norm(inp),1e-300))))
 # Additional second-order action of f1 regular and impulses. Use actual
 # fixed reference gain interpolants, integration by parts on accepted history.
 def at(he,L,M,R,t,src):return p.gather(he,L,M,R,t,src)
 yy=np.zeros(2);rr=np.zeros(2);ii=np.zeros(2);tot=np.zeros(2);rows=[]
 for k,u in enumerate(he[1:],1):
  l=he[k-1];mid=(l+u)/2;h=u-l;regular=imp=0.
  for lo,hi,A,B in [(l,mid,faces[k-1],mids[k-1]),(mid,u,mids[k-1],faces[k])]:
   dh=hi-lo;ta=np.broadcast_to(lo-lr,(nr,313));tb=np.broadcast_to(hi-lr,(nr,313));g0,g1=A[1][0],B[1][0];h0,h1=A[1][1],B[1][1];a,b=A[0],B[0]
   if k>1:
    U,V=p.local_means(he[:k],Ld[:k-1],Md[:k-1],Rd[:k-1],ta,tb,src)
    fl=at(he[:k],Ld[:k-1],Md[:k-1],Rd[:k-1],ta,src);fr=at(he[:k],Ld[:k-1],Md[:k-1],Rd[:k-1],tb,src)
    P0=g0*a;P1=g0*(b-a)+(g1-g0)*a;P2=(g1-g0)*(b-a)
    regular+=.5*float(np.sum(h0*U+(h1-h0)*V+((P0+P1+P2)*fr-P0*fl-P1*U-2*P2*V)/dh))
   # initial impulses already in C3R base forcing; here only propagated
   # outgoing tangent impulses, i.e. second and later arrivals.
   left=np.searchsorted(ev,lo,side='right');right=np.searchsorted(ev,hi,side='right')
   for u0,j0,amp,gen in events[left:right]:
    if gen==1:continue
    r=(u0-lo)/dh;gg=(1-r)*g0[:,j0]+r*g1[:,j0];tt=(1-r)*a[:,j0]+r*b[:,j0]
    gp=(g1[:,j0]-g0[:,j0])/dh;tp=(b[:,j0]-a[:,j0])/dh;hh=(1-r)*h0[:,j0]+r*h1[:,j0]
    imp+=.5*float(np.sum(amp*(hh-gp*tt-gg*tp))/dh)
  mat=np.array(J[k-1]);A=np.eye(2)-h*mat/2;B=np.eye(2)+h*mat/2
  rr=np.linalg.solve(A,B@rr+h*np.array([regular,0.]));ii=np.linalg.solve(A,B@ii+h*np.array([imp,0.]));tot+=h*np.array([regular,imp])
  rows.append([u,*rr,*ii,regular,imp])
 f=json.loads((prior/f'frozen_1110_{nt}.json').read_text())
 np.savez_compressed(D/f'impulse_{nt}.npz',rows=np.array(rows),event_time=ev,event_channel=np.array([a[1] for a in events]),event_mass=np.array([a[2] for a in events]),event_generation=np.array([a[3] for a in events]),final_regular=Rd[-1])
 o=dict(nt=nt,steps=N,events=len(events),generations={str(k):dict(count=a[0],incident_l1=a[1],outgoing_l1=a[2]) for k,a in generation.items()},max_regular_mean=maxmean,max_event_mean=max_event_mean,max_indirect_regular=max_ind,affine_checks=checks,regular_x2=float(rr[0]),impulse_x2=float(ii[0]),frozen_x2=f['final_x2'],partial_x2=float(f['final_x2']+rr[0]+ii[0]),integrated_extra=tot.tolist(),scope='first-order regular and exact baseline arrival times, transmission interpolated on actual reference snapshots; second-order action from first-order outgoing sensitivity, including propagated impulses. Missing second-order outgoing feedback and derivative of first-order source generation at moving events; not full tangent.')
 (D/f'impulse_{nt}.json').write_text(json.dumps(o,indent=2)+'\n');print({k:v for k,v in o.items() if k!='affine_checks'},flush=True)
if __name__=='__main__':run(int(sys.argv[1]))

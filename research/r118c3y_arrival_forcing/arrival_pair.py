"""C3Y actual H-only source-arrival / operator diagnostics and stable same three-moment pair."""
from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;X=D.parent/'r118c3x_three_moments';W=D.parent/'r118c3w_common_history'
sys.path.insert(0,str(D.parents[1]/"src"));sys.path.insert(0,str(X));sys.path.insert(0,str(W))
from three_moments import Map,p,JumpResponse,context,reconstruct
from common_pair import thermal_diff
def write(name,o):
 (D/name).write_text(json.dumps(o,indent=2)+'\n')
def scalar(nt):
 # Exact same previous integrator, save full scalar history (not a new closure).
 src=(X/'three_moments.py').read_text().replace('D=Path(__file__).resolve().parent;',f'D=Path({str(D)!r});')
 src=src.replace('last=A[-1],limits=', 'last=A[-1],all_history=A,limits=')
 ns={'__file__':str(X/'three_moments.py'),'__name__':'c3y_scalar'};exec(compile(src,str(X/'three_moments.py'),'exec'),ns)
 ns['run'](nt,0.)
 old=np.load(X/f'm3_{nt}_0.npz');new=np.load(D/f'm3_{nt}_0.npz')
 assert np.array_equal(old['he'],new['he'])
 err=float(np.max(abs(old['rows']-new['rows'])));assert err<1e-11
 return err
def pair(nt,lam):
 c=context(nt);z=np.load(D/f'm3_{nt}_0.npz');he=z['he'];A=z['all_history'];v=z['rows'];assert np.array_equal(c.he,he)
 nr=c.nr;N=len(he)-1;m=Map(c,lam);m0=Map(c,0.);B=np.zeros((N,nr,314,7));zero=np.zeros((nr,313))
 def owner(u,x,T,angular):
  aa,ww=m.state(u) if angular else (np.ones(nr),c.w)
  s,H,Tr=c.snap(u,x,T,c.zero);rr,o,_=p.step(s,aa,zero,ww)
  return rr.dxHII_dln_a,o,JumpResponse(s,aa,ww)
 def apply(o,I):
  a,b,g=o[2].apply(I);return a+b,g
 def geom(u):
  t=m.t(u);return p._planck_difference(c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u)),t-(u-c.lr))
 dx=dT=0.;rows=[[he[0],0.,0.,0.,0.]];maxroot=maxref=maxmom=0.;minpos=np.inf;limits=0;gl,gw=leggauss(5)
 for i,r in enumerate(he[1:],1):
  l=he[i-1];h=r-l;mid=(l+r)/2;xl,Tl=v[i-1,1:3];xr,Tr=v[i,1:3]
  U=m0.mom3(i,l,r,A);V=m.mom3(i,l,r,A)+m.mom3(i,l,r,B)
  for z,w in zip(gl,gw):
   f=(z+1)/2;g=geom(l+h*f)
   for k in range(4):V[k]+=w/2*g*f**k
  diff=V-U
  a0=owner(l,xl,Tl,False);b0=owner(r,xr,Tr,False);a1=owner(l,xl+dx,Tl+dT,True)
  def gd(o0,o1,j):
   J0=U[1] if j else U[0]-U[1];J1=diff[1] if j else diff[0]-diff[1]
   _,g0=apply(o0,J0);_,g1=apply(o1,J0);_,g2=apply(o1,J1)
   return .5*(o1[0]-o0[0])+g1-g0+g2
  H=np.interp(mid,c.ge,c.g['h'])*2.1842852410855023e-18;Tgamma=c.model.tcmb0_K*np.exp(-mid);scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tgamma**4/H;xm=(xl+xr)/2;A0=scale*xm/(1+xm+c.model.f_he)
  def trial(dn):
   dm=(dx+dn)/2;A1=scale*(xm+dm)/(1+xm+dm+c.model.f_he);dt=thermal_diff(Tl,Tr,dT,A0,A1,Tgamma,h)
   b1=owner(r,xr+dn,Tr+dt,True);F=gd(a0,a1,0)+gd(b0,b1,1)
   return dn-dx-h*F,dt,F,b1
  dn=brentq(lambda z:trial(z)[0],dx-1e-6,dx+1e-6,xtol=1e-21,rtol=1e-14);res,dt,F,b1=trial(dn);maxroot=max(maxroot,abs(res))
  O=[]
  for k in range(3):
   out=(a1[1]-a0[1])/((k+1)*(k+2))+(b1[1]-b0[1])/(k+2)
   for j,o0,o1 in [(0,a0,a1),(1,b0,b1)]:
    J0=U[k+1] if j else U[k]-U[k+1];J1=diff[k+1] if j else diff[k]-diff[k+1]
    a,_=apply(o0,J0);b,_=apply(o1,J0);dd,_=apply(o1,J1);out+=b-a+dd
   O.append(out)
  O=np.array(O);base=A[i-1]
  M0=np.array([base[...,0],base[...,0]/2+base[...,1]/6,base[...,0]/3+base[...,1]/6+base[...,2]/30])
  fr=1/np.expm1(c.tab.energy_eV/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-r)))
  co,ls,mp=reconstruct(M0+O,fr);limits+=len(ls);minpos=min(minpos,mp)
  B[i-1]=co-base
  B[i-1,...,0]=O[0];B[i-1,...,1]=6*O[1]-3*O[0];B[i-1,...,2]=30*O[2]-30*O[1]+5*O[0]
  rec=np.array([B[i-1,...,0],B[i-1,...,0]/2+B[i-1,...,1]/6,B[i-1,...,0]/3+B[i-1,...,1]/6+B[i-1,...,2]/30]);maxmom=max(maxmom,float(np.max(abs(rec-O))))
  _,g0=apply(a0,U[0]-U[1]);_,g1=apply(b0,U[1]);maxref=max(maxref,abs(xr-xl-h*(.5*(a0[0]+b0[0])+g0+g1)))
  dx,dT=dn,dt;rows.append([r,dx,dT,F,res])
  if i%128==0:print('paired',nt,lam,i,dx,flush=True)
 rows=np.array(rows);assert maxroot<1e-14 and minpos>0 and maxref<1e-14
 old=np.load(X/f'm3_{nt}_{lam:g}.npz')['rows'];direct=float(old[-1,1]-v[-1,1])
 result=dict(nt=nt,lam=lam,steps=N,delta_x=float(dx),delta_T=float(dT),direct_delta_x=direct,abs_disagreement=float(abs(dx-direct)),maxroot=float(maxroot),maxreference=float(maxref),max_weak_moment_abs=maxmom,positivity_candidate=minpos,limited=limits,event_splits=m.events,scope='same 3-moment scalar reference and signed retarded H-only owner; fixed H; positivity reconstructed total; no continuum')
 np.savez_compressed(D/f'pair_{nt}_{lam:g}.npz',rows=rows,last_signed=B[-1])
 write(f'pair_{nt}_{lam:g}.json',result);print(result,flush=True)
def diag(nt):
 c=context(nt);z=np.load(W/f'base_{nt}.npz');he=z['he'];L,M,R=[z[k] for k in ['L','M','R']];v=z['rows'];assert np.array_equal(he,c.he)
 A=np.zeros(L.shape+(7,));A[...,0]=(L+4*M+R)/6;A[...,1]=(R-L)/2;A[...,2]=(L-2*M+R)/3
 m0=Map(c,0.);m=Map(c,.5);zero=np.zeros((c.nr,313))
 def op(u,ang):
  xx,tt=[np.interp(u,he,v[:,j]) for j in [1,2]];s,_,_=c.snap(u,xx,tt,c.zero);a,w=m.state(u) if ang else (np.ones(c.nr),c.w)
  r,o,_=p.step(s,a,zero,w);return r.dxHII_dln_a,o,JumpResponse(s,a,w)
 def moments(i,l,r,mm,order):
  # Exact event split and GL order controlled independently, 5 receiving moments.
  old=mm.c;hs=old.he[:i];h=r-l;u=np.full((c.nr,313),l);out=np.zeros((5,c.nr,313));nodes,weights=leggauss(order);assert np.max(mm.t(r))<hs[-1]
  for _ in range(len(hs)+2):
   active=u<r
   if not active.any():return out
   t=mm.t(u);j=np.searchsorted(hs,t+2e-14,side='right')-1;before=j<0;nk=hs[np.clip(j+1,0,len(hs)-1)]
   cross=mm.ev(mm.g,mm.ev(mm.f,nk)+mm.lr);end=np.minimum(r,np.where(np.isfinite(cross),cross,r));end=np.where(active,end,u);span=end-u
   if np.any(active&(span<=0)):raise ValueError('event progress')
   if i>1:
    k=np.clip(j,0,len(hs)-2);hh=hs[k+1]-hs[k];a=A[k,0,c.src[None,:]]
    for q,w in zip(nodes,weights):
     x=u+(q+1)*span/2;s=2*np.clip((mm.t(x)-hs[k])/hh,0,1)-1;f=a[...,0]+s*a[...,1]+(3*s*s-1)/2*a[...,2];f=np.where(active&~before,f,0.);zz=(x-l)/h
     for j0 in range(5):out[j0]+=w*span/(2*h)*f*zz**j0
   u=end
  raise ValueError('too many events')
 def planck(l,r,order):
  O=np.zeros((5,c.nr,313));h=r-l
  for z,w in zip(*leggauss(order)):
   f=(z+1)/2;u=l+h*f;g=p._planck_difference(c.ef[None,:]/(p.KB_NATIVE_EV_K*c.model.tcmb0_K*np.exp(-u)),m.t(u)-(u-c.lr))
   for k in range(5):O[k]+=w/2*g*f**k
  return O
 def pieces(a):
  return [a[0]-3*a[1]+2*a[2],4*(a[1]-a[2]),2*a[2]-a[1]]
 zz=np.expm1(-he);inside=np.flatnonzero((zz[1:]<1106.6)&(zz[:-1]>1105.5))+1
 ids=np.unique(np.r_[np.linspace(1,len(he)-1,8).astype(int),inside[np.linspace(0,len(inside)-1,min(12,len(inside))).astype(int)] if len(inside) else []]).astype(int)
 result=[];E=c.tab.energy_eV
 edge=np.r_[E[0]-(E[1]-E[0])/2,(E[1:]+E[:-1])/2,E[-1]+(E[-1]-E[-2])/2];weights=np.diff(edge**4)/4
 for i in ids:
  l,r=he[i-1:i+1];mid=(l+r)/2
  U=moments(i,l,r,m0,9);V=moments(i,l,r,m,9);P=planck(l,r,9)
  qerr=np.linalg.norm(V-moments(i,l,r,m,5))/max(np.linalg.norm(V),1e-300)
  a=[op(u,False) for u in [l,mid,r]];b=[op(u,True) for u in [l,mid,r]]
  def force(a,b,U,V,P,quad):
   u,v,pl=(pieces(x) if quad else [x[0]-x[1],x[1]] for x in [U,V,P]);q=[0,1,2] if quad else [0,2];w=[1/6,4/6,1/6] if quad else [.5,.5];ans=np.zeros(5)
   for j,j0 in enumerate(q):
    o0,o1=a[j0],b[j0];g=lambda o,I:o[2].apply(I)[2]
    diff=v[j]-u[j];mask=np.zeros_like(diff);mask[:,[237,238]]=diff[:,[237,238]]
    ans += [w[j]*(o1[0]-o0[0]),g(o1,u[j])-g(o0,u[j]),g(o1,diff),g(o1,pl[j]),g(o1,mask)]
   return ans
  lin=force(a,b,U,V,P,False);quad=force(a,b,U,V,P,True)
  # Independent: exact affine response to real/virtual partition on actual incoming delta.
  op1=b[1][2];diff=V[0]-U[0]+P[0];dv=diff.copy();dv[:,311:]=0;dr=diff-dv
  d0,i0,g0=op1.apply(dv);d1,i1,g1=op1.apply(dr);dt,it,gt=op1.apply(diff)
  denom=max(np.linalg.norm(dt)+np.linalg.norm(it),1e-300);err=(np.linalg.norm(dt-d0-d1)+np.linalg.norm(it-i0-i1))/denom
  assert err<1e-10
  # Moment of virtual outgoing signed distortion, raw energy-bin quadrature; no real-line eV/H conversion without owner metadata.
  virt=lambda o:float(weights@(op1.w@o[:,:311]))
  result.append(dict(i=int(i),z=float(np.expm1(-mid)),h=float(r-l),lin=lin.tolist(),quadratic=quad.tolist(),GL5_9_relative=float(qerr),partition_relative=float(err),gas_virtual=float(g0),gas_real=float(g1),gas_total=float(gt),virtual_out_moment_from_virtual=virt(d0+i0),virtual_out_moment_from_real=virt(d1+i1),real_out_L2_from_virtual=float(np.linalg.norm((d0+i0)[:,311:])),real_out_L2_from_real=float(np.linalg.norm((d1+i1)[:,311:]))))
 write(f'DECOUPLE_{nt}.json',dict(rows=result,force_components=['zero_input','operator_on_scalar_history','arrival_clock','Planck_clock','arrival_channels_237_238_subset'],scope='selected actual C3W scalar cells, frozen gas; linear/quadratic native interpolation not complete time evolution; separate signed occupation stock not rates'))
 print('diagnostic',nt,len(result),flush=True)
if __name__=='__main__':
 mode=sys.argv[1];nt=int(sys.argv[2])
 if mode=='scalar':print('scalar replay max abs',scalar(nt),flush=True)
 elif mode=='pair':pair(nt,float(sys.argv[3]))
 elif mode=='diag':diag(nt)
 else:raise ValueError(mode)


"""Paired finite difference on the exact C3P reference gas mesh.
Reference radiation reconstructed from accepted reference gas. Evolve dx,dT and
outgoing difference directly, using native affine response, not two gas solves.
"""
import sys,json,numpy as np
from pathlib import Path
from dataclasses import replace
from scipy.optimize import brentq
from scipy.linalg import expm
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P3=D.parent/'r118c3p_prehistory'
sys.path.insert(0,str(P3))
import prehistory as p
from difference import thermal_diff
sys.path.insert(0,str(D.parent/'r118c3n_jump_response'))
from jump_response import JumpResponse
def run(nt,lam,label,zstart=1110):
 refpath=P3/f'z{zstart}_n{nt}_0.npz';v=np.load(refpath);ref=v['rows'];he=ref[:,0];nstep=len(he)-1
 z0=np.expm1(-he[0]);geompath=p.B/'plusfine.csv';g=np.genfromtxt(geompath,names=True,delimiter=',');ge=np.log(g['a'])
 FF=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 S=np.stack([p.stf([g[f'S{k}'][i] for k in range(5)]) for i in range(len(ge))])
 if lam==1:F=FF.copy()
 elif lam==0:F=np.broadcast_to(np.eye(3),FF.shape).copy()
 else:
  F=np.empty_like(FF);F[0]=np.eye(3)
  for i,du in enumerate(np.diff(ge)):F[i+1]=expm(lam*du*(S[i]+S[i+1])/2)@F[i]
 m=p.Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=p.OriginalHyRecPrimitiveRateTable.from_archive(p.R))
 tab=p._canonical_twophoton_table(p.R);src,ef,es=p._source_edges(tab.energy_eV);lr=np.log(es/ef)
 mu,w=p.leggauss(4);MM,phi=np.meshgrid(mu,2*np.pi*np.arange(8)/8,indexing='ij');n=np.stack([np.sqrt(1-MM*MM)*np.cos(phi),np.sqrt(1-MM*MM)*np.sin(phi),MM],axis=-1).reshape(-1,3);w=np.repeat(w/16,8);w/=w.sum();nr=len(w)
 Fref=p.interpF(ge,F,he[0]);pp0=n@Fref
 fs=np.linalg.solve(np.swapaxes(F,-1,-2),np.broadcast_to(pp0.T,(len(ge),3,nr)));ell=ge[:,None]-np.log(np.linalg.norm(fs,axis=1))
 assert np.min(np.diff(ell,axis=0))>0
 events=p.event_times(ge,F,Fref,n,he[0],lr,he[0],he[-1]);ev0=np.broadcast_to(he[0]+lr,(nr,len(lr)))
 def ray(u):
  ff=p.interpF(ge,F,u);d0=np.linalg.norm(np.linalg.solve(ff.T,pp0.T).T,axis=1);target=u-np.log(d0[:,None])-lr[None,:]
  t=np.stack([np.interp(target[j],ell[:,j],ge,left=np.nan,right=np.nan) for j in range(nr)]);pp=pp0/d0[:,None]
  for _ in range(12):
   fm=p.interpF(ge,F,t);vv=np.linalg.solve(np.swapaxes(fm,-1,-2),np.broadcast_to(pp[:,None,:,None],t.shape+(3,1)))[...,0];Rr=np.log(np.linalg.norm(vv,axis=-1));tn=u-lr[None,:]+Rr
   if np.max(abs(tn-t))<2e-14:return tn,p._planck_difference(ef[None,:]/(p.KB_NATIVE_EV_K*m.tcmb0_K*np.exp(-u)),Rr)
   t=tn
  raise ValueError('retarded convergence')
 def owner(u,angular):
  z=np.expm1(-u);H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;so=replace(m,H=H);Tr=m.tcmb0_K*(1+z)
  if angular:
   nf,ww=p.raymap(p.interpF(ge,F,u),Fref,n,w)
   st=p.stf([np.interp(u,ge,g[f'S{k}'])*lam for k in range(5)])
   a=1+np.einsum('ni,ij,nj->n',nf,st,nf);ww/=ww.sum()
  else:a=np.ones(nr);ww=w
  def snap(x,T,inc):
   return p.populate_original_full_atomic(so,z=z,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@inc[:,:311],incoming_lyman=ww@inc[:,311:])
  def ev(x,T,inc):
   s=snap(x,T,inc);r,o,dd=p.step(s,a,inc,ww);return r,o,dd,s
  def aff(x,T,inc):
   r,o,dd,s=ev(x,T,inc);return r.dxHII_dln_a,p.gain(s,a,ww)
  return ev,aff,a,ww,Tr,H
 zero=np.zeros((nr,313));shape=(nstep,nr,314)
 L0=np.zeros(shape);M0=np.zeros(shape);R0=np.zeros(shape);Ld=np.zeros(shape);Md=np.zeros(shape);Rd=np.zeros(shape)
 def states(u,x0,T0,dx,dT,inc0,incd):
  E0,_,a0,w0,Tr,H=owner(u,False);E1,_,a1,w1,_,_=owner(u,True)
  r0,o0,dd0,_=E0(x0,T0,inc0)
  r1,o1,dd1,s1=E1(x0+dx,T0+dT,inc0)
  direct,ind,dr=JumpResponse(s1,a1,w1).apply(incd);delta=(o1-o0)+direct+ind
  assert min((1/np.expm1(tab.energy_eV/(p.KB_NATIVE_EV_K*Tr))+o0[:,:311]+delta[:,:311]).ravel())>=0
  assert max(dd0,dd1)<1e-8 and max(r0.normalized_matrix_residual,r1.normalized_matrix_residual)<1e-10
  return o0,delta,(r1.dxHII_dln_a-r0.dxHII_dln_a)+dr
 t1l,gl=ray(he[0]);t0l=np.broadcast_to(he[0]-lr,t1l.shape);g0=zero
 o0,od,f=states(he[0],ref[0,1],ref[0,2],0.,0.,zero,gl);L0[0]=o0;Ld[0]=od;J0=o0[:,src].copy();Jd=od[:,src].copy()
 dx=dT=0.;rows=[[he[0],dx,dT,0.,0.,0.,0.,0.]];max_ref_res=0.;max_out_err=0.
 for i,u in enumerate(he[1:],1):
  l=he[i-1];h=u-l;mid=(l+u)/2
  t1m,gm=ray(mid);t1r,gr=ray(u);t0m=np.broadcast_to(mid-lr,t1m.shape);t0r=np.broadcast_to(u-lr,t1r.shape)
  assert t1r.max()<l and t1m.max()<l and t0r.max()<l
  def mom(A,B,C,ta,tb,lo,hi,ev,J):
   if i==1:return zero.copy(),zero.copy()
   U,V=p.local_means(he[:i],A[:i-1],B[:i-1],C[:i-1],ta,tb,src)
   dU,dV=p.correction(lo,hi,ev,he[0],ta,tb,J)
   return U+dU,V+dV
  refs=[];diffs=[]
  for lo,hi,al,ar,bl,br in [(l,mid,t0l,t0m,t1l,t1m),(mid,u,t0m,t0r,t1m,t1r)]:
   a0,b0=mom(L0,M0,R0,al,ar,lo,hi,ev0,J0)
   a1,b1=mom(L0,M0,R0,bl,br,lo,hi,events,J0)
   ad,bd=mom(Ld,Md,Rd,bl,br,lo,hi,events,Jd)
   refs.append((a0,b0));diffs.append((a1-a0+ad,b1-b0+bd))
  x0,T0=ref[i-1,1:3];x1,T1=ref[i,1:3];xm,Tm=(x0+x1)/2,(T0+T1)/2
  oo=[owner(t,False) for t in [l,mid,u]];pp=[owner(t,True) for t in [l,mid,u]]
  (b0,G0),(bm,GM),(b1,G1)=[o[1](xx,tt,zero) for o,xx,tt in zip(oo,[x0,xm,x1],[T0,Tm,T1])]
  U,V=refs[0];W,Z=refs[1];DU,DV=diffs[0];DW,DZ=diffs[1]
  f0=(b0+4*bm+b1)/6+.5*np.sum(G0*U+(GM-G0)*V+GM*W+(G1-GM)*Z)
  max_ref_res=max(max_ref_res,abs(x1-x0-h*f0))
  Tr=pp[1][4];H=pp[1][5];scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4/H;A0=scale*xm/(1+xm+m.f_he)
  bp0,GP0=pp[0][1](x0+dx,T0+dT,gl)
  def candidate(dn):
   dm=(dx+dn)/2;A1=scale*(xm+dm)/(1+xm+dm+m.f_he)
   dt=thermal_diff(T0,T1,dT,A0,A1,Tr,h)
   bpm,GPM=pp[1][1](xm+dm,Tm+(dT+dt)/2,gm)
   bp1,GP1=pp[2][1](x1+dn,T1+dt,gr)
   # exact weighted gain difference, not subtraction of two integrated gas states
   dF=((bp0-b0)+4*(bpm-bm)+(bp1-b1))/6
   dF+=.5*np.sum(GP0*DU+(GPM-GP0)*DV+GPM*DW+(GP1-GPM)*DZ+(GP0-G0)*U+((GPM-GM)-(GP0-G0))*V+(GPM-GM)*W+((GP1-G1)-(GPM-GM))*Z)
   return dn-dx-h*dF,dt,dF
  width=max(1e-6,10*abs(dx));dn=brentq(lambda q:candidate(q)[0],dx-width,dx+width,xtol=1e-19,rtol=1e-14)
  res,dt,df=candidate(dn);assert abs(res)<1e-14
  def gather(A,B,C,t):
   return p.gather(he[:i],A[:i-1],B[:i-1],C[:i-1],t,src) if i>1 else zero.copy()
  for t,x,T,ddx,ddT,ta,tb,gg,arr0,arrd in [(mid,xm,Tm,(dx+dn)/2,(dT+dt)/2,t0m,t1m,gm,M0,Md),(u,x1,T1,dn,dt,t0r,t1r,gr,R0,Rd)]:
   base=gather(L0,M0,R0,ta)
   delta=gather(L0,M0,R0,tb)-base+gather(Ld,Md,Rd,tb)+gg
   b,d,rhs=states(t,x,T,ddx,ddT,base,delta);arr0[i-1]=b;arrd[i-1]=d
   if i%32==0 or i==nstep:
    exact=owner(t,True)[0](x+ddx,T+ddT,base+delta)[1]
    err=float(np.max(abs(exact-b-d)));max_out_err=max(max_out_err,err)
  if i<nstep:L0[i]=R0[i-1];Ld[i]=Rd[i-1]
  dx,dT=dn,dt;t0l,t1l,gl=t0r,t1r,gr
  rows.append([u,dx,dT,df,res,x1+dx,T1+dT,float(u-t1r.max())])
  if i%128==0:print(label,i,dx,flush=True)
 a=np.array(rows);assert max_ref_res<1e-12
 if lam==0:assert max(abs(a[:,1]))<1e-12 and max(abs(a[:,2]))<1e-8
 np.savez_compressed(D/f'{label}.npz',rows=a,reference=ref,final_base=R0[-1],final_delta=Rd[-1])
 ix=int(np.searchsorted(he,-np.log1p(np.load(p.P)['z'][0])))
 o=dict(lam=lam,nt=nt,steps=nstep,dx=float(dx),dT=float(dT),entry=float(a[ix,1]),local=float(dx-a[ix,1]),max_root=float(max(abs(a[:,4]))),max_reference_residual=max_ref_res,max_direct_out_error=max_out_err,reference_sha=p.sha(refpath),geometry_sha=p.sha(geompath),scope='finite paired difference on C3P reference mesh, reference gas frozen but perturbed gas and signed outgoing evolved; λ1 original geometry, other amplitudes diagnostic scaled shear on fixed scalar clock; no continuum or production donor claim')
 (D/f'{label}.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run(int(sys.argv[1]),float(sys.argv[2]),sys.argv[3],int(sys.argv[4]) if len(sys.argv)>4 else 1110)

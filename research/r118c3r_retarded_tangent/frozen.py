"""Actual frozen-history first/second geometry response.
Weak integrals differentiate affine half-step retarded maps incl moving jumps.
Gas coefficients integrated, but radiation feedback tangent deliberately frozen.
"""
import numpy as np,sys,json
from pathlib import Path
from dataclasses import replace
from numpy.polynomial.legendre import leggauss
from clock_jet import ClockJet,p
from gain_jet import get,rate_weight
from gain import gain
D=Path(__file__).resolve().parent;P=D.parent/'r118c3p_prehistory'
def boundary(he,L,M,R,t,src):
 k=np.searchsorted(he,t,side='right')-1;before=k<0
 assert np.max(t)<he[-1]
 k=np.clip(k,0,len(he)-2);j=src[None,:];h=he[k+1]-he[k];z=np.where(before,0.,(t-he[k])/h)
 f=(1-3*z+2*z*z)*L[k,0,j]+(4*z-4*z*z)*M[k,0,j]+(2*z*z-z)*R[k,0,j]
 df=((-3+4*z)*L[k,0,j]+(4-8*z)*M[k,0,j]+(4*z-1)*R[k,0,j])/h
 return np.where(before,0.,f),np.where(before,0.,df)
def prod(a,b):
 return np.array([sum(a[i]*b[k-i] for i in range(len(a)) if 0<=k-i<len(b)) for k in range(len(a)+len(b)-1)])
def moments(he,L,M,R,ta,tb,src):
 # scalar baseline, broadcast only for quadrature; no future history.
 nr=ta.shape[0];shape=(len(L),nr,314)
 return p.local_means(he,np.broadcast_to(L,shape),np.broadcast_to(M,shape),np.broadcast_to(R,shape),ta,tb,src)
def weak(he,L,M,R,t0,t1,a,b,c,d,G0,G1,h,src):
 # a,b: endpoint t1; c,d endpoint t2, G0/G1: 3x gain jets at l/r
 U,V=moments(he,L,M,R,t0,t1,src);fl,dl=boundary(he,L,M,R,t0,src);fr,dr=boundary(he,L,M,R,t1,src)
 G=np.array([G0[0],G1[0]-G0[0]]);H=np.array([G0[1],G1[1]-G0[1]]);K=np.array([G0[2],G1[2]-G0[2]])
 A=np.array([a,b-a]);B=np.array([c,d-c])
 P1=prod(G,A);P2=prod(G,B)+prod(H,A);Q=prod(prod(G,A),A)/2
 def first(P):return (P.sum(axis=0)*fr-P[0]*fl-P[1]*U-2*P[2]*V)/h
 sec=(Q.sum(axis=0)*dr-Q[0]*dl)/h-((Q[1]+2*Q[2]+3*Q[3])*fr-Q[1]*fl-2*Q[2]*U-6*Q[3]*V)/h**2
 r1=H[0]*U+H[1]*V+first(P1)
 r2=K[0]*U+K[1]*V+first(P2)+sec
 # Initial Heaviside only, not all subsequent jumps; baseline interpolation continuous at other knots.
 v=(he[0]-t0)/h;mask=(v>0)&(v<1);J=L[0,0,src][None,:]
 jump1=np.where(mask,J*(P1[0]+P1[1]*v+P1[2]*v*v)/h,0.)
 jump2=np.where(mask,J*((P2[0]+P2[1]*v+P2[2]*v*v)/h-(Q[1]+2*Q[2]*v+3*Q[3]*v*v)/h**2),0.)
 return np.array([r1.sum(),r2.sum()]),np.array([jump1.sum(),jump2.sum()])
def run(nt,zstart=1110):
 fp=P/f'z{zstart}_n{nt}_0.npz';v=np.load(fp)['rows'];he=v[:,0];nstep=len(he)-1
 mu,w=leggauss(4);MM,ph=np.meshgrid(mu,np.arange(8)*np.pi/4,indexing='ij');n=np.stack([np.sqrt(1-MM*MM)*np.cos(ph),np.sqrt(1-MM*MM)*np.sin(ph),MM],axis=-1).reshape(-1,3);w=np.repeat(w/16,8);w/=w.sum()
 nr=len(w);j=ClockJet(n,he[0])
 geom=np.genfromtxt(p.B/'plusfine.csv',names=True,delimiter=',');ge=np.log(geom['a'])
 m=p.Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=p.OriginalHyRecPrimitiveRateTable.from_archive(p.R))
 tab=p._canonical_twophoton_table(p.R);src,ef,es=p._source_edges(tab.energy_eV);lr=np.log(es/ef);zero=np.zeros((1,313));L=np.zeros((nstep,1,314));M=L.copy();R=L.copy()
 def snapshot(u,x,T,inc):
  z=np.expm1(-u);H=np.interp(u,ge,geom['h'])*2.1842852410855023e-18;so=replace(m,H=H)
  s=p.populate_original_full_atomic(so,z=z,xHII=x,xe=x,Tm_K=T,incoming_virtual=inc[:311],incoming_lyman=inc[311:])
  return s,H,m.tcmb0_K*(1+z)
 def owner(u,x,T,inc):
  s,H,Tr=snapshot(u,x,T,inc);return p.step(s,np.ones(1),inc[None,:],np.ones(1))
 def local(u,x,T,inc):
  s,H,Tr=snapshot(u,x,T,zero[0]);aa,ww=rate_weight(j,u,w);b,G=get(s,aa,ww)
  # stable reference gain crosscheck
  assert np.linalg.norm(G[0]-gain(s,aa[0],ww[0]))<1e-11*np.linalg.norm(G[0])
  t1,t2=j.ret(u,lr);xx=ef/(p.KB_NATIVE_EV_K*Tr);f=1/np.expm1(xx);f1=-xx*f*(1+f);f2=.5*f*(1+f)*(xx*xx*(1+2*f)-xx)
  geom1=f1*t1;geom2=f1*t2+f2*t1*t1
  out=np.array([b[1]+np.sum(G[0]*geom1),b[2]+np.sum(G[0]*geom2+G[1]*geom1)])
  # Native fixed-state local gain derivative check on selected faces, below.
  return t1,t2,G,out
 # Reconstruct accepted reference radiation independently, same gas.
 r,o,err=owner(he[0],*v[0,1:3],zero[0]);L[0]=o
 for i,u in enumerate(he[1:],1):
  l=he[i-1];mid=(l+u)/2
  for t,x,T,A in [(mid,*((v[i-1,1:3]+v[i,1:3])/2),M),(u,*v[i,1:3],R)]:
   inc=p.gather(he[:i],L[:i-1],M[:i-1],R[:i-1],(t-lr)[None,:],src)[0] if i>1 else zero[0]
   r,o,err=owner(t,x,T,inc);assert r.normalized_matrix_residual<1e-10;A[i-1]=o
  if i<nstep:L[i]=R[i-1]
 err=float(np.max(abs(R[-1]-np.load(fp)['final'][0])))
 assert err<1e-25,(err,)
 # Use precomputed accepted history; retarded reads for every sample remain strictly prior.
 yy=np.zeros((2,2));noj=yy.copy();rows=[];total=np.zeros(2);jump=np.zeros(2);gainchecks=[]
 x,T=v[0,1:3];prev=local(he[0],x,T,zero[0])
 for i,u in enumerate(he[1:],1):
  l=he[i-1];h=u-l;mid=(l+u)/2;xm,Tm=(v[i-1,1:3]+v[i,1:3])/2
  inc=p.gather(he[:i],L[:i-1],M[:i-1],R[:i-1],(mid-lr)[None,:],src)[0] if i>1 else zero[0]
  cur=local(mid,xm,Tm,inc);end=local(u,*v[i,1:3],inc)
  forc=(prev[3]+4*cur[3]+end[3])/6;js=np.zeros(2)
  if i>1:
   for lo,hi,A,B in [(l,mid,prev,cur),(mid,u,cur,end)]:
    ta=np.broadcast_to(lo-lr,(nr,313));tb=np.broadcast_to(hi-lr,(nr,313))
    if not np.max(tb)<he[i-1]:raise ValueError('causality')
    z,q=weak(he[:i],L[:i-1],M[:i-1],R[:i-1],ta,tb,A[0],B[0],A[1],B[1],A[2],B[2],hi-lo,src);forc+=.5*z;js+=.5*q
  # Fixed history local gas Jacobian (finite derivative of actual native atom).
  ex=1e-6;et=.01
  Fx=(owner(mid,xm+ex,Tm,inc)[0].dxHII_dln_a-owner(mid,xm-ex,Tm,inc)[0].dxHII_dln_a)/(2*ex)
  FT=(owner(mid,xm,Tm+et,inc)[0].dxHII_dln_a-owner(mid,xm,Tm-et,inc)[0].dxHII_dln_a)/(2*et)
  s,H,Tr=snapshot(mid,xm,Tm,inc);scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4/H;A=scale*xm/(1+xm+m.f_he);Ax=scale*(1+m.f_he)/(1+xm+m.f_he)**2
  J=np.array([[Fx,FT],[Ax*(Tr-Tm),-2-A]])
  lhs=np.eye(2)-h*J/2;rhs=np.eye(2)+h*J/2
  yy=np.linalg.solve(lhs,rhs@yy+h*np.array([forc,[0,0]]));noj=np.linalg.solve(lhs,rhs@noj+h*np.array([forc-js,[0,0]]))
  total+=h*forc;jump+=h*js;rows.append([u,*yy.ravel(),*noj.ravel(),*forc,*js]);prev=end
  if i in [1,nstep//2,nstep]:
   s,H,Tr=snapshot(mid,xm,Tm,zero[0]);aa,ww=rate_weight(j,mid,w);B,G=get(s,aa,ww)
   for ep in [.05,.025]:
    def gg(t):
     a=aa[0]+t*aa[1]+t*t*aa[2];wq=ww[0]+t*ww[1]+t*t*ww[2];return gain(s,a,wq)
    a,b=gg(ep),gg(-ep);f=(a-b)/(2*ep);q=(a+b-2*G[0])/(2*ep*ep)
    gainchecks.append(dict(u=mid,eps=ep,G1_rel=float(np.linalg.norm(f-G[1])/np.linalg.norm(G[1])),G2_rel=float(np.linalg.norm(q-G[2])/np.linalg.norm(G[2]))))
  if i%128==0:print('frozen',nt,i,yy[0],flush=True)
 a=np.array(rows);np.savez_compressed(D/f'frozen_{zstart}_{nt}.npz',rows=a,he=he,final_base=R[-1],L=L,M=M,R=R)
 o=dict(nt=nt,zstart=zstart,steps=nstep,reference_out_abs=err,final_x1=float(yy[0,0]),final_x2=float(yy[0,1]),final_T2=float(yy[1,1]),no_initial_jump_x2=float(noj[0,1]),integrated_forcing=total.tolist(),initial_jump_integral=jump.tolist(),gainchecks=gainchecks,reference_sha=p.sha(fp),scope='frozen accepted outgoing history; analytic geometry/retarded/gain jets and local native gas Jacobian; distributional outgoing response and full causal tangent feedback not included')
 (D/f'frozen_{zstart}_{nt}.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run(int(sys.argv[1]),int(sys.argv[2]) if len(sys.argv)>2 else 1110)

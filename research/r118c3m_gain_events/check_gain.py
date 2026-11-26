"""Check adjoint gain on actual atomic state and exact weighted source quadrature."""
import sys,json,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3h_paired_history'))
sys.path.insert(0,str(D.parent/'r118c3k_history_join'))
from shared_gas_h import Clock,stf,B,P,R,OriginalHyRecPrimitiveRateTable,populate_original_full_atomic
from retarded import raymap,interpF,step
from gain import gain,means,update,correction
from numpy.polynomial.legendre import leggauss
def run():
 v=np.load(P);g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
 rng=np.random.default_rng(3);rows=[]
 mu,w=leggauss(4);M,ph=np.meshgrid(mu,2*np.pi*np.arange(8)/8,indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(ph),np.sqrt(1-M*M)*np.sin(ph),M],axis=-1).reshape(-1,3);w=np.repeat(w/16,8)
 Fref=interpF(ge,F,-np.log1p(v['z'][0]))
 from dataclasses import replace
 for i in [0,63,128]:
  z=v['z'][i];u=-np.log1p(z);H=np.interp(u,ge,g['h'])*2.1842852410855023e-18
  S=stf([np.interp(u,ge,g[f'S{k}']) for k in range(5)]);nf,ww=raymap(interpF(ge,F,u),Fref,n,w);rates=1+np.einsum('ni,ij,nj->n',nf,S,nf)
  s=replace(m,H=H);x=v['xHII'][i];T=v['T'][i]
  def atom(inc):
   snap=populate_original_full_atomic(s,z=z,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@inc[:,:311],incoming_lyman=ww@inc[:,311:]);return step(snap,rates,inc,ww)[0],snap
  zero=np.zeros((32,313));a,ss=atom(zero);G=gain(ss,rates,ww)
  inc=rng.uniform(0,1e-12,zero.shape);b,_=atom(inc)
  actual=b.dxHII_dln_a-a.dxHII_dln_a;pred=np.sum(G*inc);err=abs(pred-actual)/max(abs(pred),1e-300)
  assert err<1e-9,err;rows.append(dict(index=i,actual=float(actual),adjoint=float(pred),relative=float(err)))
 # polynomial with true jump at t0=0, 2+3t+4t², retarded interval [-.2,.8].
 he=np.array([0.,.5,1.,1.5]);f=lambda t:2+3*t+4*t*t
 L=f(he[:-1])[:,None,None];Rr=f(he[1:])[:,None,None];M=f((he[1:]+he[:-1])/2)[:,None,None]
 a=np.zeros((4,1,1));b=a.copy()
 for i in range(1,4):update(he,L,M,Rr,a,b,i)
 l=np.array([[-.2]]);r=np.array([[.8]]);A,B1=means(he,L,M,Rr,a,b,l,r,np.array([0]))
 ex=2*.8+1.5*.8**2+4/3*.8**3;ex1=.2*ex+.8**2+1*.8**3+.8**4
 assert abs(A[0,0]-ex)<1e-14 and abs(B1[0,0]-ex1)<1e-14
 C,E=correction(0,1,np.array([[.25]]),0,l,r,np.array([[2.]]))
 assert abs(C[0,0]+.1)<1e-14 and abs(E[0,0]+.0225)<1e-14
 out=dict(adjoint=rows,mean_error=float(abs(A[0,0]-ex)),first_moment_error=float(abs(B1[0,0]-ex1)),jump_correction_error=float(abs(C[0,0]+.1)))
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()

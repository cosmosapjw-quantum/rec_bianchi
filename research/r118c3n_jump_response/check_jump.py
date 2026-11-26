"""Verify exact native jump response and manufactured jump primitives."""
import numpy as np,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3h_paired_history'))
from shared_gas_h import Clock,stf,B,P,R,OriginalHyRecPrimitiveRateTable,populate_original_full_atomic
from retarded import raymap,interpF,step
from jump_response import JumpResponse
from dataclasses import replace
from numpy.polynomial.legendre import leggauss
def run():
 v=np.load(P);g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
 rng=np.random.default_rng(73);rows=[]
 mu,w=leggauss(4);M,ph=np.meshgrid(mu,2*np.pi*np.arange(8)/8,indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(ph),np.sqrt(1-M*M)*np.sin(ph),M],axis=-1).reshape(-1,3);w=np.repeat(w/16,8)
 Fref=interpF(ge,F,-np.log1p(v['z'][0]))
 for i in [0,63,128]:
  z=v['z'][i];u=-np.log1p(z);H=np.interp(u,ge,g['h'])*2.1842852410855023e-18
  S=stf([np.interp(u,ge,g[f'S{k}']) for k in range(5)]);nf,ww=raymap(interpF(ge,F,u),Fref,n,w);rates=1+np.einsum('ni,ij,nj->n',nf,S,nf)
  s=replace(m,H=H);x=v['xHII'][i];T=v['T'][i]
  def atom(inc):
   snap=populate_original_full_atomic(s,z=z,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@inc[:,:311],incoming_lyman=ww@inc[:,311:]);a,o,_=step(snap,rates,inc,ww);return a,o,snap
  zero=np.zeros((32,313));a,out,ss=atom(zero)
  for tag,d in [('dense',rng.uniform(-1e-12,1e-12,zero.shape)),('sparse',np.zeros_like(zero))]:
   if tag=='sparse':d[9,138]=1e-12;d[13,312]=-1e-12
   b,oo,_=atom(d);direct,ind,gain=JumpResponse(ss,rates,ww).apply(d)
   err=np.linalg.norm(oo-out-direct-ind)/np.linalg.norm(oo-out)
   rerr=abs(b.dxHII_dln_a-a.dxHII_dln_a-gain)/max(abs(gain),1e-300)
   assert err<1e-8 and rerr<1e-8,(err,rerr)
   rows.append(dict(knot=i,tag=tag,relative_out=float(err),relative_rhs=float(rerr),direct_norm=float(np.linalg.norm(direct)),coupled_norm=float(np.linalg.norm(ind))))
 o=dict(rows=rows,scope='fixed actual thermodynamic states, homogeneous affine response; no time-evolving jump solver claim')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()

"""Research-only local coupled H-only gas and accepted causal angular radiation.
No full-H+He or production donor promotion."""
import numpy as np, json, hashlib, sys
from pathlib import Path
from dataclasses import dataclass,replace
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3f_directional_history'))
from canonical_history import raymap,interpF,incoming_canonical,step
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource,KB_NATIVE_EV_K,COMPTON_GAMMA_PER_T4_S_INV_K4
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic
B=Path.home()/'worktrees/bass-r109-native-20261124/research/r118c3e_geometry_tracks'
P=D.parent/'r118c2w_causal/FULL_128.npz';R=D.parents[1]/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
@dataclass(frozen=True)
class Clock(HMLAFlrwSource):
 H:float=0.
 def cosmology(self,z):
  h,n=super().cosmology(z);return (self.H if self.H else h),n
def stf(s):
 a,b,c,d,e=s;return np.array([[a/np.sqrt(2)-b/np.sqrt(6),c/np.sqrt(2),d/np.sqrt(2)],[c/np.sqrt(2),-a/np.sqrt(2)-b/np.sqrt(6),e/np.sqrt(2)],[d/np.sqrt(2),e/np.sqrt(2),2*b/np.sqrt(6)]])
def thermal_endpoint(T,gprev,A,Tr,h,method):
 if method=='trap':return (T+h/2*(gprev+A*Tr))/(1+h/2*(2+A))
 if method=='be':return (T+h*A*Tr)/(1+h*(2+A))
 raise ValueError('method')
def run(case,angular,nm,nt,method,label):
 v=np.load(P);eta=-np.log1p(v['z']);tab=_canonical_twophoton_table(R);orig=np.r_[v['virtual_out'],v['lyman_out']].T
 m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
 p=B/(case+'.csv');g=np.genfromtxt(p,names=True,delimiter=',');ge=np.log(g['a'])
 F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 if not angular:F=np.broadcast_to(np.eye(3),F.shape).copy()
 mu,w=leggauss(nm);phi=2*np.pi*np.arange(2*nm)/(2*nm);M,Phi=np.meshgrid(mu,phi,indexing='ij')
 n=np.stack([np.sqrt(1-M*M)*np.cos(Phi),np.sqrt(1-M*M)*np.sin(Phi),M],axis=-1).reshape(-1,3);w=np.repeat(w/(4*nm),2*nm)
 start=64;finish=128;times=np.linspace(eta[start-1],eta[finish],nt+1);Fref=interpF(ge,F,times[0]);he=np.r_[eta[:start],times[1:]]
 hist=np.zeros((len(he),len(n),314));hist[:start]=orig[:start,None,:]
 def endpoint(u,i):
  zz=np.expm1(-u);H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;Tr=m.tcmb0_K*(1+zz)
  S=stf([np.interp(u,ge,g[f'S{k}']) for k in range(5)]) if angular else np.zeros((3,3))
  nf,ww=raymap(interpF(ge,F,u),Fref,n,w);rates=1+np.einsum('ni,ij,nj->n',nf,S,nf)
  inc,delay=incoming_canonical(ge,F,u,Fref,n,tab.energy_eV,he[:i],hist[:i],Tr)
  if not np.isfinite(inc).all() or min(delay.ravel())<=0:raise ValueError('causal domain')
  source=replace(m,H=H)
  def evaluate(x,T):
   snap=populate_original_full_atomic(source,z=zz,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@inc[:,:311],incoming_lyman=ww@inc[:,311:])
   r,out,defect=step(snap,rates,inc,ww)
   return r,out,defect
  return source,zz,Tr,delay,evaluate
 x=float(v['xHII'][start-1]);T=float(v['T'][start-1])
 src,z,Tr,delay,evaluate=endpoint(times[0],start)
 fprev=evaluate(x,T)[0].dxHII_dln_a;gprev=src.thermal_rhs_ln_a(z,x,T)
 rows=[[times[0],x,T,fprev,gprev,0,0,0,0,float(delay.min())]]
 for i,u in enumerate(times[1:],start):
  h=u-he[i-1];src,z,Tr,delay,evaluate=endpoint(u,i)
  if delay.min()<=h:raise ValueError('requires accepted-history-only step')
  def candidate(xx):
   A=COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4*xx/(1+xx+m.f_he)/src.H
   tt=thermal_endpoint(T,gprev,A,Tr,h,method)
   rr,oo,dd=evaluate(xx,tt)
   f=rr.dxHII_dln_a
   resid=xx-x-h*(.5*(fprev+f) if method=='trap' else f)
   return resid,tt,rr,oo,dd
  width=max(1e-6,10*h*abs(fprev));lo=max(1e-10,x-width);hi=min(1-1e-10,x+width)
  xx=brentq(lambda q:candidate(q)[0],lo,hi,xtol=2e-15,rtol=1e-14)
  resid,tt,rr,out,defect=candidate(xx);gg=src.thermal_rhs_ln_a(z,xx,tt)
  tres=tt-T-h*(.5*(gprev+gg) if method=='trap' else gg)
  full=1/np.expm1(tab.energy_eV/(KB_NATIVE_EV_K*Tr))+out[:,:311]
  assert 0<xx<1 and tt>0 and np.min(full)>=0 and abs(resid)<1e-12 and abs(tres)<1e-8
  assert defect<1e-8 and rr.normalized_matrix_residual<1e-10
  x,T,fprev,gprev=xx,tt,rr.dxHII_dln_a,gg;hist[i]=out
  rows.append([u,x,T,fprev,gprev,resid,tres,defect,rr.normalized_matrix_residual,float(delay.min())])
  if (i-start+1)%32==0:print(label,i-start+1,x,T,flush=True)
 rows=np.array(rows)
 np.savez_compressed(D/(label+'.npz'),rows=rows,columns=np.array(['eta','xHII','T','f','g','xres','Tres','defect','matrix','delay']),rays=n,weights0=w,reference_F=Fref,final=hist[-1])
 if label=='on128':np.savez_compressed(D/'ACCEPTED_LOCAL_DIRECTIONAL.npz',eta=times[1:],outgoing=hist[start:],rays=n,weights0=w,reference_F=Fref,rows=rows,prefix_sha=sha(P),geometry_sha=sha(p),rates_sha=sha(R))
 data=dict(status='SCOPED_LOCAL_H_ONLY_SHARED_GAS',case=case,angular=bool(angular),rays=len(n),steps=nt,method=method,x=float(x),T=float(T),max_xres=float(np.max(abs(rows[:,5]))),max_Tres=float(np.max(abs(rows[:,6]))),max_atom_res=float(np.max(rows[:,8])),min_delay=float(np.min(rows[:,9])),prefix_sha=sha(P),geometry_sha=sha(p),rates_sha=sha(R),scope='actual H(a), accepted isotropic prefix, self-consistent H-only x,T and directional virtual history; thermal source Compton+adiabatic only')
 (D/(label+'.json')).write_text(json.dumps(data,indent=2)+'\n');print(data,flush=True)
if __name__=='__main__':
 case,ang,nm,nt,method,label=sys.argv[1:];run(case,bool(int(ang)),int(nm),int(nt),method,label)

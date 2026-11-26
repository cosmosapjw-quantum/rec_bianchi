import numpy as np,json,hashlib,sys
from pathlib import Path
from dataclasses import dataclass,replace
from numpy.polynomial.legendre import leggauss
from canonical_history import raymap,interpF,incoming_canonical,step
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource,KB_NATIVE_EV_K
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic,complete_original_full_atomic
D=Path(__file__).resolve().parent;B=Path('/home/cosmosapjw/worktrees/bass-r109-native-20261124/research/r118c3e_geometry_tracks')
P=D.parent/'r118c2w_causal/FULL_128.npz';R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=np.load(P);z=v['z'];eta=-np.log1p(z);tab=_canonical_twophoton_table(R);orig=np.r_[v['virtual_out'],v['lyman_out']].T
@dataclass(frozen=True)
class Clock(HMLAFlrwSource):
 H:float=0.
 def cosmology(self,z):
    h,n=super().cosmology(z);return self.H if self.H else h,n
m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
def stf(s):
 a,b,c,d,e=s;return np.array([[a/np.sqrt(2)-b/np.sqrt(6),c/np.sqrt(2),d/np.sqrt(2)],[c/np.sqrt(2),-a/np.sqrt(2)-b/np.sqrt(6),e/np.sqrt(2)],[d/np.sqrt(2),e/np.sqrt(2),2*b/np.sqrt(6)]])
case=sys.argv[1];nm=int(sys.argv[2]);nt=int(sys.argv[3]);label=sys.argv[4];p=B/(case+'.csv')
g=np.genfromtxt(p,names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
mu,w=leggauss(nm);phi=2*np.pi*np.arange(2*nm)/(2*nm);M,Phi=np.meshgrid(mu,phi,indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(Phi),np.sqrt(1-M*M)*np.sin(Phi),M],axis=-1).reshape(-1,3);w=np.repeat(w/(4*nm),2*nm)
start=64;finish=128;times=np.linspace(eta[start-1],eta[finish],nt+1)[1:];Fref=interpF(ge,F,eta[start-1]);he=np.r_[eta[:start],times]
hist=np.zeros((len(he),len(n),314));hist[:start]=orig[:start,None,:]
rows=[]
for i,u in enumerate(times,start):
 zz=np.expm1(-u);T=float(np.interp(u,eta,v['T']));x=float(np.interp(u,eta,v['xHII']));H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;S=stf([np.interp(u,ge,g[f'S{i}']) for i in range(5)])
 nf,ww=raymap(interpF(ge,F,u),Fref,n,w);rates=1+np.einsum('ni,ij,nj->n',nf,S,nf)
 inc,d=incoming_canonical(ge,F,u,Fref,n,tab.energy_eV,he[:i],hist[:i],m.tcmb0_K*(1+zz))
 s=populate_original_full_atomic(replace(m,H=H),z=zz,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@inc[:,:311],incoming_lyman=ww@inc[:,311:])
 r,out,defect=step(s,rates,inc,ww);hist[i]=out
 # actual physical occupation positivity, including all virtual bins
 assert min((1/np.expm1(tab.energy_eV/(KB_NATIVE_EV_K*m.tcmb0_K*(1+zz)))+out[:,:311]).ravel())>=0
 assert defect<1e-8 and r.normalized_matrix_residual<1e-10
 rows.append([u,r.dxHII_dln_a,defect,r.normalized_matrix_residual,float(d.min()),float(ww.sum()),float(np.max(np.ptp(out[:,:311],axis=0)))])
 if i%16==0:print(label,i,rows[-1],flush=True)
rows=np.array(rows);np.savez_compressed(D/(label+'.npz'),eta=he,final=hist[-1],rays=n,weights=ww,rows=rows,mean_final=ww@hist[-1])
if label=='p128_saved':
 np.savez_compressed(D/'ACCEPTED_DIRECTIONAL.npz',eta=times,outgoing=hist[start:],rays=n,reference_F=Fref,weights0=w,prefix_sha=sha(P),coframe_sha=sha(p))
out=dict(case=case,nmu=nm,nray=len(n),steps=nt,terminal_rhs=float(rows[-1,1]),max_mean_defect=float(max(rows[:,2])),max_matrix_residual=float(max(rows[:,3])),min_lookback=float(min(rows[:,4])),max_area_defect=float(max(abs(rows[:,5]-1))),max_direction_spread=float(max(rows[:,6])),coframe_sha=sha(p),prefix_sha=sha(P),rates_sha=sha(R),scope='self-generated directional outgoing after accepted isotropic prefix, prescribed gas x,T, shared real atom, isotropic redistribution closure; not full feedback')
(D/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)

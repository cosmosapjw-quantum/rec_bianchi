import json,hashlib,sys
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from numpy.polynomial.legendre import leggauss
from directional import incoming,common
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic,complete_original_full_atomic
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
D=Path(__file__).resolve().parent;B=Path('/home/cosmosapjw/worktrees/bass-r109-native-20261124/research/r118c3e_geometry_tracks')
P=D.parent/'r118c2w_causal/FULL_128.npz';R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=np.load(P);z=v['z'];eta=-np.log1p(z);du=float(v['u'][1]-v['u'][0]);tab=_canonical_twophoton_table(R);hist=np.r_[v['virtual_out'],v['lyman_out']]
@dataclass(frozen=True)
class Clock(HMLAFlrwSource):
 H:float=0.
 def cosmology(self,z):
    h,n=super().cosmology(z);return self.H if self.H else h,n
m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
from dataclasses import replace
def stf(s):
 a,b,c,d,e=s;return np.array([[a/np.sqrt(2)-b/np.sqrt(6),c/np.sqrt(2),d/np.sqrt(2)],[c/np.sqrt(2),-a/np.sqrt(2)-b/np.sqrt(6),e/np.sqrt(2)],[d/np.sqrt(2),e/np.sqrt(2),2*b/np.sqrt(6)]])
rows=[];inputs={str(P):sha(P),str(R):sha(R)}
for case in ('plusfine','minus','zerofine'):
 p=B/(case+'.csv');inputs[str(p)]=sha(p);g=np.genfromtxt(p,names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 for idx in (104,):
  u=eta[idx];H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;S=stf([np.interp(u,ge,g[f'S{i}']) for i in range(5)])
  base=causal_incoming_from_accepted_histories(energies_eV=tab.energy_eV,virtual_history=v['virtual_out'][:,:idx],lyman_history=v['lyman_out'][:,:idx],z_start=float(z[0]),iz=idx,z_face=float(z[idx]),dlna=du,shear_q=0.)
  model=replace(m,H=H);s=populate_original_full_atomic(model,z=float(z[idx]),xHII=float(v['xHII'][idx]),xe=float(v['xHII'][idx]),Tm_K=float(v['T'][idx]),incoming_virtual=base.virtual_distortion[0],incoming_lyman=base.lya_lyb_incoming_distortion[0])
  rr=complete_original_full_atomic(s)
  for nm in (32,64):
   mu,w=leggauss(nm);phi=2*np.pi*np.arange(2*nm)/(2*nm);M,Phi=np.meshgrid(mu,phi,indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(Phi),np.sqrt(1-M*M)*np.sin(Phi),M],axis=-1).reshape(-1,3);w=np.repeat(w/(4*nm),2*nm)
   chunks=[incoming(ge,F,u,tab.energy_eV,n[i:i+128],eta[:idx],hist[:,:idx],m.tcmb0_K*(1+z[idx])) for i in range(0,len(n),128)]
   inc,d,corr=[np.concatenate([c[j] for c in chunks]) for j in range(3)]
   rates=1+np.einsum('ni,ij,nj->n',n,S,n)
   ss=common(s,rates,inc,w);r=complete_original_full_atomic(ss) # only real departures and RHS used; direction-specific outgoing not constructed.
   # Verify shared real and virtual algebraic solution (outgoing is not used).
   row=dict(case=case,nmu=nm,H=H,shear=float(np.linalg.norm(S)),rate_min=float(min(rates)),rate_max=float(max(rates)),retarded_min=float(d.min()),retarded_max=float(d.max()),incoming_geom_max=float(np.max(abs(corr))),incoming_mean_diff=float(np.max(abs(w@inc-np.r_[base.virtual_distortion[0],base.lya_lyb_incoming_distortion[0]]))),rhs_scalar=rr.dxHII_dln_a,rhs_common=r.dxHII_dln_a,relative_rhs=float(r.dxHII_dln_a/rr.dxHII_dln_a-1),matrix_residual=r.normalized_matrix_residual)
   rows.append(row);print(row,flush=True)
out=dict(status='SCOPED_GENERAL_COFRAME_COMMON_ATOM',rows=rows,source_hashes=inputs,scope='actual native BASS coframes, accepted isotropic FULL outgoing prefix with assumed zero distortion before prefix; common-angle virtual closure at fixed actual H-only state; not evolving FULL nor donor feedback')
(D/'DIRECTION_FINE.json').write_text(json.dumps(out,indent=2)+'\n')

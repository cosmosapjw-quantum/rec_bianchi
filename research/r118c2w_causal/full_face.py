"""Causal FULL-generated boundary on the same H-only thermal/history owner.
Zero spectral prehistory is a stated experiment, not the native primordial solution.
"""
import json,hashlib,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.constants import c,h,e
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource,KB_NATIVE_EV_K
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.short_full_history import integrate_full_h_short_history
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA,causal_incoming_from_accepted_histories,_source_edges
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'r118c2u_boundaries'))
from boundary import JoinedDrift,L
R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip');H=Path('/home/cosmosapjw/Downloads/rec_r118c2f_compiled_final')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
states=json.loads((H/'STATES.json').read_text())['states'];s=states['z1100']
model=HMLAFlrwSource(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
table=_canonical_twophoton_table(R);energy=table.energy_eV
p=Path('/home/cosmosapjw/Downloads/rec_r118c2k_refined/z1100/GRAPH128.npz');g=np.load(p)
d=JoinedDrift(g['et'],g['gt'],g['ec'],g['gc']);assert d.e.max()==L(energy[-1])
src,targets,energies=_source_edges(energy);delay=float(np.log(energies[-3]/targets[-3]));assert src[-3]==313
# Same end time: 64 and 128 accepted intervals; actual local source
# starts at HMLA x_HII and Tm but evolves its own FULL gas and outgoing fields.
rows=[]
for n in (64,128):
 step=SOURCE_DLNA*64/n/2;v=integrate_full_h_short_history(model,z_start=s['z'],x_HII_start=s['x_HII'],Tm_start_K=s['T_m_K'],steps=n+1,dlna=step)
 u=step*np.arange(n+1);inc=np.zeros(n+1);oracle=np.zeros(n+1)
 for i in range(2,n+1):
  q=causal_incoming_from_accepted_histories(energies_eV=energy,virtual_history=v.virtual_out[:,:i],lyman_history=v.lyman_out[:,:i],z_start=s['z'],iz=i,z_face=float(v.z[i]),dlna=step,shear_q=0.)
  inc[i]=q.virtual_distortion[0,-1]
  if u[i]>=delay:oracle[i]=np.interp(u[i]-delay,u[:i],v.lyman_out[2,:i])
 # exact same retarded line identity, including zero prehistory.
 assert np.max(abs(inc-oracle))<1e-28
 # Reintegrate only the response to this incoming boundary on the joined
 # nodal graph, not its collision physics. Preserve blackbody separately.
 fac=L(8*np.pi)*(L(d.e.max())/L('1.239841874331e-4'))**3*L(1e6)
 occ=L(1)/np.expm1(d.e.max()/(L(KB_NATIVE_EV_K)*L(model.tcmb0_K)*(1+v.z.astype(L))))
 inflow=np.exp(3*u.astype(L))*fac*(occ+inc.astype(L))
 assert np.min(inflow)>0
 base=np.zeros(len(d.e),dtype=L);delta=base.copy();led={k:L(0) for k in ('escape_N','escape_U','work','in_N','in_U','cross_N')}
 for i in range(n):
  delta,l=d.affine(base,delta,L(step),(inflow[i]+inflow[i+1])/2)
  for k in led:led[k]+=l[k]
 assert min(delta)>=0 and led['in_N']>0
 nd=float(abs(delta.sum()+led['escape_N']-led['in_N'])/led['in_N'])
 ed=float(abs(delta@d.e+led['escape_U']+led['work']-led['in_U'])/led['in_U'])
 assert max(nd,ed)<1e-13
 out=D/f'FULL_{n}.npz';np.savez_compressed(out,u=u,z=v.z,xHII=v.x_HII,T=v.Tm_K,virtual_out=v.virtual_out,lyman_out=v.lyman_out,incoming=inc,oracle=oracle,occupation=occ,stock=delta)
 row=dict(n=n,sha=sha(out),z_end=float(v.z[-1]),xHII=float(v.x_HII[-1]),T=float(v.Tm_K[-1]),matrix_max=float(v.matrix_residual.max()),first_nonzero=int(np.flatnonzero(inc!=0)[0]),incoming_end=float(inc[-1]),planck_end=float(occ[-1]),inflow_ratio=float((inc[-1]+occ[-1])/occ[-1]),retarded_error=float(np.max(abs(inc-oracle))),N=nd,E=ed,in_N=float(led['in_N']),in_U=float(led['in_U']))
 rows.append(row);print(row,flush=True)
 (D/'FULL_FACE.json').write_text(json.dumps(dict(status='SCOPED_CAUSAL_FULL_TO_JOINED_DRIFT',rows=rows,history_initial_state_sha=sha(H/'STATES.json'),rate_sha=sha(R),graph_sha=sha(p),delay=delay,scope='self-generated H-only FULL local causal history with zero spectral prehistory; joined graph boundary response only, not two-way coupled FULL and recoil solver'),indent=2)+'\n')

import json,hashlib
from pathlib import Path
import numpy as np
from writeback import WingCorrection,L
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic,_original_escape_factors,HPC_EV_CM
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
D=Path(__file__).resolve().parent;P=D.parent/'r118c2w_causal';R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip');G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local')
m=HMLAFlrwSource(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
tab=_canonical_twophoton_table(R);v=np.load(P/'FULL_128.npz');x0=v['xHII'][96];z=v['z'];du=float(v['u'][1]-v['u'][0]);_,nh=m.cosmology(z[96])
c=WingCorrection(tab,np.load(G/'GRAPH128.npz'),nh*(1-x0));rows=[]
for name,lam in [('half',.5),('replacement',1.)]:
 a=np.load(D/(name+'.npz'))
 for k in (96,100,104,108,112):
    inc=causal_incoming_from_accepted_histories(energies_eV=tab.energy_eV,virtual_history=a['virtual'][:,:k],lyman_history=a['lyman'][:,:k],z_start=float(z[0]),iz=k,z_face=float(z[k]),dlna=du,shear_q=0.)
    s=populate_original_full_atomic(m,z=float(z[k]),xHII=float(a['x'][k]),xe=float(a['x'][k]),Tm_K=float(a['T'][k]),incoming_virtual=inc.virtual_distortion[0],incoming_lyman=inc.lya_lyb_incoming_distortion[0])
    r,info=c.solve(s,lam);assert np.array_equal(r.outgoing_virtual,a['virtual'][:,k])
    idx=c.idx;q=np.asarray(info['correction'],dtype=L)
    pi,trans=_original_escape_factors(s.Dtau);gamma=s.Tvv[0]*pi
    y=r.virtual_departures;rr=r.real_departures
    n=-rr@s.Tvr
    n[1:]-=y[:-1]*s.Tvv[1,1:];n[:-1]-=y[1:]*s.Tvv[2,:-1];n+=q
    # Independent integrated transfer relation: H times phase factor times
    # outgoing-minus-incoming = emissivity minus opacity times average.
    fac=s.H_s_inv*8*np.pi*(tab.energy_eV/HPC_EV_CM)**3/s.nH_cgs
    lhs=np.asarray(fac[idx]*(r.outgoing_virtual[idx]-s.incoming_virtual[idx]),dtype=L)
    rhs=np.asarray(n[idx]-gamma[idx]*y[idx],dtype=L)
    denom=max(np.sum(abs(lhs)),np.sum(abs(rhs)),L('1e-4900'))
    er=float(np.sum(abs(lhs-rhs))/denom)
    # Original formula uses binary64 escape factors; note finite source parity.
    assert er<1e-8
    overlap=q-L(lam)*(info['new']-info['old']);assert np.max(abs(overlap))<1e-28
    heat=float(q@np.asarray(tab.energy_eV,dtype=L)+L(info['heat']))
    row=dict(case=name,k=k,face_flux_relative=er,correction_number=float(q.sum()),correction_energy_heat_defect=heat,new_norm=float(np.sum(abs(info['new']))),native_selected_norm=float(np.sum(abs(info['old']))))
    rows.append(row);print(row,flush=True)
(D/'FACE_AUDIT.json').write_text(json.dumps(dict(status='SCOPED_TRANSFER_IDENTITY',rows=rows),indent=2)+'\n')

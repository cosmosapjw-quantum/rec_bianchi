import hashlib,json
from pathlib import Path
import numpy as np
from fit_graph import FitCorrection as OpacityCorrection,L
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource,KB_NATIVE_EV_K
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
from full_bianchi_hyrec.recoil.original_hyrec_native import populate_original_hyrec_diffusion
D=Path(__file__).resolve().parent;P=D.parent/'r118c2w_causal';R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip');G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
m=HMLAFlrwSource(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
tab=_canonical_twophoton_table(R);v=np.load(P/'FULL_128.npz');z=v['z'];du=float(v['u'][1]-v['u'][0]);_,nh=m.cosmology(z[96]);fit=np.load(D/'FIT.npz');c=OpacityCorrection(tab,np.load(G/'GRAPH128.npz'),nh*(1-v['xHII'][96]),[fit['g0'],fit['g1']])
rows=[]
for name,lam in [('native',0.),('half',.5),('replacement',1.)]:
 a=np.load(D/(name+'.npz'))
 for k in (96,100,104,108,112):
    inc=causal_incoming_from_accepted_histories(energies_eV=tab.energy_eV,virtual_history=a['virtual'][:,:k],lyman_history=a['lyman'][:,:k],z_start=float(z[0]),iz=k,z_face=float(z[k]),dlna=du,shear_q=0.)
    s=populate_original_full_atomic(m,z=float(z[k]),xHII=float(a['x'][k]),xe=float(a['x'][k]),Tm_K=float(a['T'][k]),incoming_virtual=inc.virtual_distortion[0],incoming_lyman=inc.lya_lyb_incoming_distortion[0])
    r,info=c.solve(s,lam);assert np.array_equal(r.outgoing_virtual,a['virtual'][:,k])
    diff=populate_original_hyrec_diffusion(np.column_stack((tab.energy_eV,tab.integrated_rates_s_inv.T)),s.Tm_eV/KB_NATIVE_EV_K)
    _,fine,old,gross=c.action(s,r.virtual_departures,diff)
    # Independent dilute coarse action using long-double occupation activity.
    x=L(1-s.xHII);E=np.asarray(tab.energy_eV,dtype=L)
    zeta=np.exp(-(E-L('10.198714553953742'))/L(s.Tm_eV));f=1/np.expm1(E/L(s.Tr_eV))+r.virtual_departures/x
    ac=f/(zeta*(1+f));co=np.zeros(311,dtype=L)
    for lo,hi,g in c.coarse:
       sl=slice(lo,hi+1);ff=f[sl];aa=ac[sl];co[sl]=x*np.sum(g*(1+ff)[:,None]*(1+ff)[None,:]*(aa[None,:]-aa[:,None]),axis=1)
    e0=fine@E;e1=co@E
    if lam:assert np.max(abs(co-info['new']))<1e-15*max(gross,L('1e-4900'))
    row=dict(case=name,k=k,action_relative=float(np.sum(abs(co-fine))/max(np.sum(abs(fine)),L('1e-4900'))),energy_relative=float(abs(e1-e0)/max(abs(e0),L('1e-4900'))),gross_normalized=float(np.sum(abs(co-fine))/max(gross,L('1e-4900'))),coarse_number=float(co.sum()),fine_energy=float(e0),coarse_energy=float(e1))
    rows.append(row);print(row,flush=True)
(D/'PROJECTION_AUDIT.json').write_text(json.dumps(dict(status='SCOPED_COARSE_VS_FINE_ACTION',rows=rows,source_sha=sha(P/'FULL_128.npz'),graph_sha=sha(G/'GRAPH128.npz'),scope='same actual corrected native occupation, coarse positive closure vs C2X exact projected fine graph; not trajectory oracle'),indent=2)+'\n')

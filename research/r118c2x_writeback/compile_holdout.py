import numpy as np,hashlib,json,time
from pathlib import Path
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
from full_bianchi_hyrec.recoil.calibrated_source import Bath,compile_isotropic
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.trajectory.atomic_refined_owner import RefinedTwoS,compile_integrals,assemble,Scatter
from writeback import WingCorrection,L
D=Path(__file__).resolve().parent;P=D.parent/'r118c2w_causal';R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip');G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
m=HMLAFlrwSource(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
tab=_canonical_twophoton_table(R);v=np.load(P/'FULL_128.npz');a=np.load(D/'replacement.npz');z=v['z'];du=float(v['u'][1]-v['u'][0]);k=112
_,nh0=m.cosmology(z[96]);neutral0=nh0*(1-v['xHII'][96]);_,nh=m.cosmology(z[k]);neutral=nh*(1-a['x'][k])
out=Path('/home/cosmosapjw/Downloads/rec_r118c2x_holdout');out.mkdir(exist_ok=False)
bath=Bath(float(a['T'][k]),float(neutral));t0=time.monotonic()
data=compile_isotropic(bath,(4,),2);np.savez_compressed(out/'SOURCE.npz',**data)
net=RefinedTwoS(R,prepare(data,4),128);edges,report=assemble(net,data,compile_integrals(net,bath));sc=Scatter(net,edges)
np.savez_compressed(out/'GRAPH128.npz',i=sc.i,j=sc.j,K=sc.K,new=sc.new,cross=sc.cross,et=net.et,gt=net.gt,ec=net.ec,gc=net.gc,events=np.array(net.events,dtype=L))
g0=np.load(G/'GRAPH128.npz');g1=np.load(out/'GRAPH128.npz')
for n in ('i','j','et','gt','ec','gc','events'):assert np.array_equal(g0[n],g1[n]),n
inc=causal_incoming_from_accepted_histories(energies_eV=tab.energy_eV,virtual_history=a['virtual'][:,:k],lyman_history=a['lyman'][:,:k],z_start=float(z[0]),iz=k,z_face=float(z[k]),dlna=du,shear_q=0.)
s=populate_original_full_atomic(m,z=float(z[k]),xHII=float(a['x'][k]),xe=float(a['x'][k]),Tm_K=float(a['T'][k]),incoming_virtual=inc.virtual_distortion[0],incoming_lyman=inc.lya_lyb_incoming_distortion[0])
c0=WingCorrection(tab,g0,neutral0);c1=WingCorrection(tab,g1,neutral)
r0,d0=c0.solve(s,1.);r1,d1=c1.solve(s,1.)
assert np.array_equal(r0.outgoing_virtual,a['virtual'][:,k])
K0=g0['K']*(neutral/neutral0);K1=g1['K']
row=dict(status='SCOPED_TERMINAL_RECOMPILE',z=float(z[k]),T=float(a['T'][k]),neutral=float(neutral),edge_L1=float(np.sum(abs(K1-K0))/np.sum(K1)),rhs_frozen=float(r0.dxHII_dln_a),rhs_recompiled=float(r1.dxHII_dln_a),rhs_relative=float(abs(r1.dxHII_dln_a/r0.dxHII_dln_a-1)),action_relative=float(np.sum(abs(d1['new']-d0['new']))/np.sum(abs(d1['new']))),heat_frozen=d0['heat'],heat_recompiled=d1['heat'],seconds=time.monotonic()-t0,raw_path=str(out),hashes={p.name:sha(p) for p in out.iterdir() if p.is_file()})
(D/'HOLDOUT.json').write_text(json.dumps(row,indent=2)+'\n');print(row,flush=True)

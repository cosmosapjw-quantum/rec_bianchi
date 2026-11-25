import hashlib,json
from pathlib import Path
import numpy as np
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource,KB_NATIVE_EV_K
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
from full_bianchi_hyrec.trajectory.short_full_history import _implicit_thermal_step
from opacity import OpacityCorrection as WingCorrection,L
D=Path(__file__).resolve().parent;R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip');P=D.parent/'r118c2w_causal';G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
j=json.loads((P/'FULL_LOCAL.json').read_text());assert sha(P/'FULL_128.npz')==j['full_sha'] and sha(R)==j['rates_sha']
for k,h in j['raw_hashes'].items():assert sha(G/k)==h
v=np.load(P/'FULL_128.npz');model=HMLAFlrwSource(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
tab=_canonical_twophoton_table(R);z=v['z'];u=v['u'];start=96;stop=112;du=float(u[1]-u[0]);h0,nh=model.cosmology(z[start]);neutral0=nh*(1-v['xHII'][start])
c=WingCorrection(tab,np.load(G/'GRAPH128.npz'),neutral0)
print('positive projection',c.info,flush=True)
rows=[];series={}
for name,lam in [('native',0.),('half',.5),('replacement',1.)]:
 x=v['xHII'].copy();T=v['T'].copy();virt=v['virtual_out'].copy();ly=v['lyman_out'].copy()
 diag=[]
 for k in range(start,stop+1):
    inc=causal_incoming_from_accepted_histories(energies_eV=tab.energy_eV,virtual_history=virt[:,:k],lyman_history=ly[:,:k],z_start=float(z[0]),iz=k,z_face=float(z[k]),dlna=du,shear_q=0.)
    s=populate_original_full_atomic(model,z=float(z[k]),xHII=float(x[k]),xe=float(x[k]),Tm_K=float(T[k]),incoming_virtual=inc.virtual_distortion[0],incoming_lyman=inc.lya_lyb_incoming_distortion[0])
    r,info=c.solve(s,lam);virt[:,k]=r.outgoing_virtual;ly[:,k]=r.outgoing_lyman
    q=info['correction'];net=float(np.sum(q));heat=info['heat'];ep=float(np.dot(q,tab.energy_eV))
    row=dict(k=k,z=float(z[k]),x=float(x[k]),T=float(T[k]),rhs=float(r.dxHII_dln_a),residual=float(r.normalized_matrix_residual),new_norm=float(np.sum(abs(info['new']))),old_norm=float(np.sum(abs(info['old']))),q_norm=float(np.sum(abs(q))),q_number=net,q_energy=ep,heat=heat,root=info['root_residual'],nfev=info['nfev'],face=info.get('face',0.),tau_ratio_min=info.get('tau_ratio_min',1.),tau_ratio_max=info.get('tau_ratio_max',1.))
    diag.append(row)
    if k<stop:
       x[k+1]=x[k]+du*r.dxHII_dln_a
       T[k+1]=_implicit_thermal_step(model,float(z[k+1]),float(x[k+1]),float(T[k]),du)
       # Explicit differential recoil heating of the gas (new-minus-old).
       T[k+1]+=2*heat*du/(3*KB_NATIVE_EV_K*(1+model.f_he+x[k+1])*s.H_s_inv)
       assert 0<x[k+1]<1 and 0<T[k+1]<=model.tcmb0_K*(1+z[k+1])
    if k==start or k==stop:print(name,row,flush=True)
 if name=='native':
    assert np.array_equal(x[start:stop+1],v['xHII'][start:stop+1]) and np.array_equal(virt[:,start:stop+1],v['virtual_out'][:,start:stop+1])
 series[name]=np.c_[x[start:stop+1],T[start:stop+1],ly[:,start:stop+1].T]
 rows.append(dict(case=name,lambda_=lam,rows=diag,terminal_x=float(x[stop]),terminal_T=float(T[stop]),max_outgoing_difference=float(np.max(abs(virt[:,start:stop+1]-v['virtual_out'][:,start:stop+1])))))
 np.savez_compressed(D/(name+'.npz'),x=x[:stop+1],T=T[:stop+1],virtual=virt[:,:stop+1],lyman=ly[:,:stop+1])
 (D/'RESULTS.json').write_text(json.dumps(dict(status='SCOPED_RUNNING',cases=rows),indent=2)+'\n')
out=dict(status='SCOPED_POSITIVE_COARSE_OPACITY',cases=rows,full_sha=j['full_sha'],rates_sha=j['rates_sha'],graph_sha=j['raw_hashes']['GRAPH128.npz'],selected=[dict(lo=lo,hi=hi,edges=len(i)) for lo,hi,p,i,j,K in c.windows],projection=c.info,scope='positive moment-matched coarse pair closure; matched extinction/emission/escape, selected native pairs removed, causal history; not exact fine transport')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')

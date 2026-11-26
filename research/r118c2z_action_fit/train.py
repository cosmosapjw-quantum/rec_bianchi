import sys,json,hashlib
from pathlib import Path
import numpy as np
from fit_graph import cut_fit,FitCorrection,L
from opacity import OpacityCorrection,EnergyActionCorrection
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2x_writeback'))
from writeback import WingCorrection
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource,KB_NATIVE_EV_K
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
from full_bianchi_hyrec.recoil.original_hyrec_native import populate_original_hyrec_diffusion
D=Path(__file__).resolve().parent;P=D.parent/'r118c2w_causal';Y=D.parent/'r118c2y_opacity';X=D.parent/'r118c2x_writeback';R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip');G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
m=HMLAFlrwSource(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
tab=_canonical_twophoton_table(R);v=np.load(P/'FULL_128.npz');z=v['z'];du=float(v['u'][1]-v['u'][0]);_,nh=m.cosmology(z[96]);n0=nh*(1-v['xHII'][96])
graph=np.load(G/'GRAPH128.npz');base=EnergyActionCorrection(tab,graph,n0);pos=OpacityCorrection(tab,graph,n0);frozen=WingCorrection(tab,graph,n0)
samples=[[],[]];sources={}
for model,owner,root,prefix in [('positive',pos,Y,''),('energy',base,Y,'energy_'),('frozen',frozen,X,'')]:
 for case,lam in [('native',0.),('half',.5),('replacement',1.)]:
    if model!='positive' and case=='native':continue
    p=root/(prefix+case+'.npz');a=np.load(p);sources[str(p)]=sha(p)
    for k in (96,100,104,108,112):
        inc=causal_incoming_from_accepted_histories(energies_eV=tab.energy_eV,virtual_history=a['virtual'][:,:k],lyman_history=a['lyman'][:,:k],z_start=float(z[0]),iz=k,z_face=float(z[k]),dlna=du,shear_q=0.)
        s=populate_original_full_atomic(m,z=float(z[k]),xHII=float(a['x'][k]),xe=float(a['x'][k]),Tm_K=float(a['T'][k]),incoming_virtual=inc.virtual_distortion[0],incoming_lyman=inc.lya_lyb_incoming_distortion[0])
        r,info=owner.solve(s,lam);assert np.array_equal(r.outgoing_virtual,a['virtual'][:,k])
        diff=populate_original_hyrec_diffusion(np.column_stack((tab.energy_eV,tab.integrated_rates_s_inv.T)),s.Tm_eV/KB_NATIVE_EV_K)
        _,fine,_,gross=base.action(s,r.virtual_departures,diff)
        x=L(1-s.xHII);E=np.asarray(tab.energy_eV,dtype=L);zz=np.exp(-(E-L('10.198714553953742'))/L(s.Tm_eV));f=1/np.expm1(E/L(s.Tr_eV))+r.virtual_departures/x
        for wi,(lo,hi,*_) in enumerate(base.windows):
            sl=slice(lo,hi+1);ff=f[sl];aa=ff/(zz[sl]*(1+ff))
            F=x/L(n0)*(1+ff)[:,None]*(1+ff)[None,:]*(aa[None,:]-aa[:,None])
            samples[wi].append((model,case,k,F,fine[sl],model!='frozen' and k in (96,104,112)))
fits=[];rows=[];stats=[]
for wi,(lo,hi,p,i,j,K) in enumerate(base.windows):
    eye=np.eye(hi-lo+1,dtype=L);B=eye[p.i]*(1-p.w[:,None])+eye[p.i+1]*p.w[:,None];d=B[i]-B[j];A=d.T@(K[:,None]*d)
    ss=samples[wi];g,info=cut_fit(A,p.coarse,[(F,q) for _,_,_,F,q,train in ss if train]);fits.append(g)
    stats.append(info);print('wing',wi,info,flush=True)
    for model,case,k,F,q,train in ss:
        row=dict(wing=wi,model=model,case=case,k=k,train=train)
        for name,gg in [('fit',g),('nearest',base.coarse[wi][2]*L(n0)),('positive',pos.coarse[wi][2]*L(n0))]:
            err=(gg*F).sum(axis=1)-q
            row[name]=float(np.sum(abs(err))/np.sum(abs(q)))
            row[name+'_energy']=float(abs(err@p.coarse)/max(abs(q@p.coarse),L('1e-4900')))
        rows.append(row)
np.savez_compressed(D/'FIT.npz',g0=fits[0],g1=fits[1])
out=dict(status='SCOPED_POSITIVE_MINIMAX',stats=stats,rows=rows,source_hashes=sources,full_sha=sha(P/'FULL_128.npz'),graph_sha=sha(G/'GRAPH128.npz'),rates_sha=sha(R))
(D/'FIT.json').write_text(json.dumps(out,indent=2)+'\n')
for k in (True,False):
 rr=[x for x in rows if x['train']==k];print('train' if k else 'holdout',len(rr),{n:max(x[n] for x in rr) for n in ('fit','nearest','positive')})

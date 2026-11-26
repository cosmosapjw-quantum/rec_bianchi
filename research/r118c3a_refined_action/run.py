import sys,json,hashlib
from pathlib import Path
import numpy as np
from refined import positive_pairs,bose_action,nested,action,L
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2z_action_fit"))
from fit_graph import FitCorrection
from writeback import LinearProject
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
Z=D.parent/'r118c2z_action_fit';fit=np.load(Z/'FIT.npz');fitted=FitCorrection(tab,graph,n0,[fit['g0'],fit['g1']])
samples=[[],[]];sources={}
for model,owner,root,prefix in [('positive',pos,Y,''),('energy',base,Y,'energy_'),('frozen',frozen,X,''),('fit',fitted,Z,'')]:
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
            samples[wi].append((model,case,k,aa,x/L(n0),L(s.Tm_eV),fine[sl]))

rows=[];summary=[]
for wi,(lo,hi,p,i,j,K) in enumerate(base.windows):
 for level in (1,2,4,8,16,32,0):
    e=nested(p.coarse,p.fine,level)
    pr,g=positive_pairs(e,p.fine,i,j,K);back=LinearProject(p.coarse,e)
    target=pr.deposit(action(p.fine,i,j,K));defect=float(np.sum(abs(action(e,*g)-target))/np.sum(abs(target)))
    for model,case,k,a,x,T,native in samples[wi]:
        ar=back.lift(a);af=p.lift(a)
        q=bose_action(p.fine,af,i,j,K,x,T);f=pr.deposit(q)
        assert np.sum(abs(p.deposit(q)-native))<1e-10*np.sum(abs(native))
        c=bose_action(e,ar,*g,x,T)
        r=back.deposit(c);ref=back.deposit(f)
        assert np.sum(abs(ref-native))<1e-10*np.sum(abs(native))
        rows.append(dict(wing=wi,level=level,nodes=len(e),edges=len(g[0]),model=model,case=case,k=k,refined_relative=float(np.sum(abs(c-f))/np.sum(abs(f))),native_relative=float(np.sum(abs(r-native))/np.sum(abs(native))),energy_relative=float(abs((r-native)@p.coarse)/max(abs(native@p.coarse),L('1e-4900')))))
    ss=[r for r in rows if r['wing']==wi and r['level']==level]
    row=dict(wing=wi,level=level,nodes=len(e),edges=len(g[0]),energy_vector_defect=defect,max_refined=float(max(x['refined_relative'] for x in ss)),max_native=float(max(x['native_relative'] for x in ss)),max_energy=float(max(x['energy_relative'] for x in ss)))
    summary.append(row);print(row,flush=True)
    if level==0:assert row['max_native']<1e-10 and row['max_refined']<1e-10
out=dict(status='SCOPED_NESTED_POSITIVE_PAIR_REFINEMENT',summary=summary,rows=rows,source_hashes=sources,full_sha=sha(P/'FULL_128.npz'),graph_sha=sha(G/'GRAPH128.npz'),rates_sha=sha(R),scope='fixed actual native occupation lifts; refined operator and restriction tests; not a refined FULL opacity evolution')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')

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


from scipy.sparse import coo_matrix,bmat,csr_matrix
from scipy.sparse.linalg import expm_multiply
def evolution(e,cap,a,i,j,K,ts):
    active=cap>0;assert np.all(active[i]) and np.all(active[j])
    # Number-space generator; solve for increments, not a subtraction of
    # two close positive stocks. Exact affine exponential in binary64.
    cap0=np.where(active,cap,L(1));N=cap*a
    r=K/cap0[i];q=K/cap0[j]
    G=coo_matrix((np.asarray(np.r_[-r,r,q,-q],float),(np.r_[i,j,i,j],np.r_[i,i,j,j])),shape=(len(e),len(e))).tocsr()
    F=action(a,i,j,K);scale=max(np.max(abs(F)),L('1e-4900'));source=np.asarray(F/scale,float)
    aug=bmat([[G,csr_matrix(source[:,None])],[csr_matrix((1,len(e))),csr_matrix((1,1))]],format='csr')
    ret=[]
    for t in ts:
        d=np.asarray(expm_multiply(aug*t,np.r_[np.zeros(len(e)),1.])[:-1],dtype=L)*scale
        assert np.min(N+d)>=0 and abs(d.sum())<1e-12*max(np.sum(abs(d)),L('1e-4900'))
        ret.append(d)
    return N,ret
wi=1;lo,hi,p,i,j,K=base.windows[wi]
E=graph['et'];ii,jj=graph['i'],graph['j'];mask=(E[ii]>=p.coarse[0])&(E[ii]<=p.coarse[-1])&(E[jj]>=p.coarse[0])&(E[jj]<=p.coarse[-1]);ids=np.unique(np.r_[ii[mask],jj[mask]])
assert np.array_equal(E[ids],p.fine)
rows=[];ts=[1e5,1e6,1e7]
for model,case,k,a,x,T,_ in samples[wi]:
 if (model,case,k) not in [('positive','native',104),('frozen','replacement',104)]:continue
 _,nh=m.cosmology(z[k]);K1=K*x*L(nh);cap=graph['gt'][ids]*np.exp(-(p.fine-L('10.198714553953742'))/T);af=p.lift(a)
 N,ref=evolution(p.fine,cap,af,i,j,K1,ts)
 occ=af*np.exp(-(p.fine-L('10.198714553953742'))/T);assert max(occ)<1e-12
 for level in (1,4,8,16,32,0):
    e=nested(p.coarse,p.fine,level);pr,g=positive_pairs(e,p.fine,i,j,K1);back=LinearProject(p.coarse,e)
    c=pr.deposit(cap);n=pr.deposit(N);ar=np.divide(n,c,out=np.zeros_like(c),where=c>0)
    _,d=evolution(e,c,ar,*g,ts)
    for t,y,r in zip(ts,d,ref):
        target=pr.deposit(r);q=back.deposit(y);qref=p.deposit(r)
        row=dict(model=model,case=case,level=level,nodes=len(e),seconds=t,refined_increment_relative=float(np.sum(abs(y-target))/np.sum(abs(target))),native_increment_relative=float(np.sum(abs(q-qref))/np.sum(abs(qref))),energy_increment_relative=float(abs(y@e-r@p.fine)/max(abs(r@p.fine),L('1e-4900'))),max_occ=float(max(occ)),physical_rate_max=float(np.max(abs(K1)/cap[i])))
        rows.append(row);print(row,flush=True)
out=dict(status='SCOPED_DILUTE_FROZEN_WING_EVOLUTION',rows=rows,source_hashes=sources,scope='closed selected blue-wing scattering only; frozen actual bath and occupation; dilute limit; conservative mass-lumped projection, no atomic source/redshift/opacity, unique-energy limit may retain duplicate-mode dynamical error')
(D/'EVOLUTION.json').write_text(json.dumps(out,indent=2)+'\n')

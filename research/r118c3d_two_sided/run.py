import sys,json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from two_line import TwoWing,Owner,L
from scipy.sparse import diags,bmat,csr_matrix
from scipy.sparse.linalg import expm_multiply
from full_bianchi_hyrec.recoil.original_hyrec_native import populate_original_hyrec_diffusion
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c2x_writeback'))
from writeback import WingCorrection,LinearProject
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource,KB_NATIVE_EV_K
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table,populate_original_full_atomic,complete_original_full_atomic
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
P=D.parent/'r118c2w_causal';X=D.parent/'r118c2x_writeback';R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip');G=Path('/home/cosmosapjw/Downloads/rec_r118c2w_full_local')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
m=HMLAFlrwSource(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
tab=_canonical_twophoton_table(R);v=np.load(P/'FULL_128.npz');z=v['z'];du=float(v['u'][1]-v['u'][0]);_,nh=m.cosmology(z[96]);n0=nh*(1-v['xHII'][96]);graph=np.load(G/'GRAPH128.npz')
own=WingCorrection(tab,graph,n0);parts=[]
E=graph['et'];ii,jj=graph['i'],graph['j']
for lo,hi,p,i,j,K in own.windows:
 mask=(E[ii]>=p.coarse[0])&(E[ii]<=p.coarse[-1])&(E[jj]>=p.coarse[0])&(E[jj]<=p.coarse[-1]);ids=np.unique(np.r_[ii[mask],jj[mask]])
 assert np.array_equal(E[ids],p.fine)
 parts.append((lo,hi,p,ids,graph['gt'][ids],Owner(p.fine,graph['gt'][ids],i,j,K)))
e=np.r_[parts[0][2].fine,parts[1][2].fine];N=len(e);idx=104
T0=1e7;z0=float(z[idx]);u0=float(v['u'][idx]);delay=[float(np.log(10.198714553953742/max(parts[0][2].fine))),float(np.log(parts[1][2].coarse[-1]/max(parts[1][2].fine)))]
clock=solve_ivp(lambda t,y:[m.cosmology((1+z0)*np.exp(-y[0])-1)[0]],(0,T0),[0.],rtol=1e-12,atol=1e-25,dense_output=True)
assert clock.success and clock.y[0,-1]<min(delay)
rows=[];sources={}
for name in ('native','replacement'):
 if name=='native':
    xx=v['xHII'];tt=v['T'];virt=v['virtual_out'];ly=v['lyman_out'];lam=0.;source=P/'FULL_128.npz'
 else:
    source=X/'replacement.npz';a=np.load(source);xx=a['x'];tt=a['T'];virt=a['virtual'];ly=a['lyman'];lam=1.
 sources[str(source)]=sha(source)
 inc=causal_incoming_from_accepted_histories(energies_eV=tab.energy_eV,virtual_history=virt[:,:idx],lyman_history=ly[:,:idx],z_start=float(z[0]),iz=idx,z_face=z0,dlna=du,shear_q=0.)
 s=populate_original_full_atomic(m,z=z0,xHII=float(xx[idx]),xe=float(xx[idx]),Tm_K=float(tt[idx]),incoming_virtual=inc.virtual_distortion[0],incoming_lyman=inc.lya_lyb_incoming_distortion[0])
 r,_=own.solve(s,lam);assert np.array_equal(r.outgoing_virtual,virt[:,idx])
 tc=L(s.Tr_eV);tm=L(s.Tm_eV);stocks=[]
 for lo,hi,p,ids,gt,o in parts:
    f=1/np.expm1(p.coarse/tc)+r.virtual_departures[lo:hi+1]/L(1-s.xHII)
    zeta=np.exp(-(p.coarse-L('10.198714553953742'))/tm);ac=f/(zeta*(1+f))
    stock=gt*np.exp(-(p.fine-L('10.198714553953742'))/tm)*p.lift(ac)
    assert min(stock)>0;stocks.append(stock)
 base=np.concatenate(stocks)
 def bath(t):
    u=float(clock.sol(t)[0]);zz=(1+z0)*np.exp(-u)-1;eta=u0+u
    H,nh=m.cosmology(zz);tr=L(KB_NATIVE_EV_K)*L(m.tcmb0_K)*(1+L(zz));influx=[]
    for j,(_,hi,p,_,_,o) in enumerate(parts):
        ret=eta-delay[j];assert ret<v['u'][idx]
        data=ly[0,:idx] if j==0 else virt[hi,:idx]
        f=1/np.expm1(max(p.fine)/tr)+L(np.interp(ret,v['u'][:idx],data))
        if f<=0:raise ValueError("incoming domain")
        influx.append(np.exp(3*L(u))*L(8*np.pi)*(max(p.fine)/L('1.239841874331e-4'))**3*L(1e6)*f)
    return H,tm,L(nh*(1-s.xHII))/L(n0),np.array(influx)
 # Native physical line pair; preserve exact real 2p identity, distinct from redshift.
 rates=populate_original_hyrec_diffusion(np.column_stack((tab.energy_eV,tab.integrated_rates_s_inv.T)),float(tt[idx]))
 nh=s.nH_cgs*1e6;neutral=L(nh*(1-s.xHII));el=L("10.198714553953742")
 cp=3*neutral;p0=L(nh)*(L(r.real_departures[1])+3*L(1-s.xHII)*np.exp(-el/L(s.Tr_eV)))
 conductance=[neutral*L(rates.Aup_s_inv[139])*np.exp(-(L(tab.energy_eV[139])-el)/L(rates.temperature_eV)),neutral*L(rates.Adn_s_inv[140])*np.exp(-(L(tab.energy_eV[140])-el)/L(rates.temperature_eV))]
 assert abs(conductance[0]/cp/rates.A2p_dn_s_inv-1)<1e-12 and abs(conductance[1]/cp/rates.A2p_up_s_inv-1)<1e-12
 loss=L(s.Trr[1,1])-L(rates.A2p_up_s_inv)-L(rates.A2p_dn_s_inv)
 bath0=bath(0.);line=TwoWing(parts[0][-1],parts[1][-1],bath0,p0,cp,conductance,loss,base)
 assert abs(line.qss(base)/p0-1)<1e-14
 print(name,'p0',float(p0),'source',float(line.source),'lambda',float(loss),'gamma',float(line.gamma),flush=True)
 # Integrate scaled increments. Dynamic real population is tiny, use its own scale.
 def reference(qss,tol):
    m=N+(not qss);y0=np.r_[base,[] if qss else [p0],np.zeros(10,dtype=L)]
    scales=np.r_[np.asarray(base,float),[] if qss else [float(p0)],np.full(10,float(max(base)))];scales[m+6:m+8]=float(line.source*T0)
    def affine(t):
        H,_,_,inc=bath(t);A,b=line.affine(H,inc,qss);return A,b
    def rhs(t,y):
        A,b=affine(t);f=A@np.asarray(y0,dtype=float)+np.asarray(b,float);return (f+A@(scales*y))/scales
    def jac(t,y):
        A,_=affine(t);return diags(1/scales)@A@diags(scales)
    sol=solve_ivp(rhs,(0,T0),np.zeros(len(y0)),method='BDF',jac=jac,rtol=tol,atol=tol/100,dense_output=True)
    if not sol.success:raise ValueError(sol.message)
    return sol,scales
 refs={}
 for qss in (False,True):
    for tol in (1e-8,1e-10):
        sol,sc=reference(qss,tol);refs[(qss,tol)]=(sol,sc)
        print(name,'qss',qss,'tol',tol,'nfev',sol.nfev,flush=True)
 for t in (1e4,1e7):
    dyn=np.asarray(refs[(False,1e-10)][0].sol(t)*refs[(False,1e-10)][1],dtype=L)
    qs=np.asarray(refs[(True,1e-10)][0].sol(t)*refs[(True,1e-10)][1],dtype=L)
    old=np.asarray(refs[(False,1e-8)][0].sol(t)*refs[(False,1e-8)][1],dtype=L)
    oldq=np.asarray(refs[(True,1e-8)][0].sol(t)*refs[(True,1e-8)][1],dtype=L)
    p_dyn=p0+dyn[N];p_q=line.qss(base+qs[:N])
    assert min(base+dyn[:N])>0 and min(base+qs[:N])>0 and p_dyn>0 and p_q>0
    nr,er=line.ledger(dyn,False);nq,eq=line.ledger(qs,True)
    row=dict(case=name,seconds=t,p0=float(p0),p_dynamic=float(p_dyn),p_qss=float(p_q),line_gamma=float(line.gamma),line_source=float(line.source),line_conductance=[float(x) for x in conductance],relative_population=float(abs(p_dyn/p_q-1)),qss_increment_relative=float(np.sum(abs(dyn[:N]-qs[:N]))/np.sum(abs(dyn[:N]))),dynamic_reference_gap=float(np.sum(abs(dyn[:N]-old[:N]))/np.sum(abs(dyn[:N]))),qss_reference_gap=float(np.sum(abs(qs[:N]-oldq[:N]))/np.sum(abs(qs[:N]))),dynamic_N=nr,dynamic_E=er,qss_N=nq,qss_E=eq,redshift_escape=float(dyn[N+1]),line_to_photons=float(dyn[N+10]),line_heat=float(dyn[N+9]),line_net_external=float(dyn[N+7]-dyn[N+8]))
    rows.append(row);print(row,flush=True)
    if t==T0:np.savez_compressed(D/(name+"_line_state.npz"),ids=np.r_[parts[0][3],parts[1][3]],e=e,base=base,p0=p0,dynamic=dyn,qss=qs)
out=dict(status="SCOPED_TWO_SIDED_REAL_LINE",rows=rows,modes=N,delays=delay,source_hashes=sources,full_sha=sha(P/'FULL_128.npz'),graph_sha=sha(G/'GRAPH128.npz'),rates_sha=sha(R),scope="frozen actual column104 two-sided shared real line, actual retarded top source and H, externally anchored real source/loss, distinct labelled photons and separate lower advection; no FULL opacity writeback")
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')

import sys,json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c3d_two_sided"))
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

 # Native external Schur closure: eliminate 2s and all virtual modes outside
 # the two selected native wings. Retain real 2p and both coarse wings.
 A=np.zeros((313,313));A[:2,:2]=s.Trr;A[:2,2:]=s.Trv;A[2:,:2]=s.Tvr.T
 A[2:,2:]=np.diag(s.Tvv[0])+np.diag(s.Tvv[1,1:],-1)+np.diag(s.Tvv[2,:-1],1)
 b=np.r_[s.sr,s.sv];ret=np.r_[1,np.concatenate([np.arange(lo,hi+1)+2 for lo,hi,*_ in parts])]
 ex=np.setdiff1d(np.arange(313),ret);V=np.r_[r.real_departures,r.virtual_departures]
 tmp=np.linalg.solve(A[np.ix_(ex,ex)],np.column_stack([b[ex],A[np.ix_(ex,ret)]]))
 C=A[np.ix_(ret,ret)]-A[np.ix_(ret,ex)]@tmp[:,1:]
 f=b[ret]-A[np.ix_(ret,ex)]@tmp[:,0]
 native=complete_original_full_atomic(s);VN=np.r_[native.real_departures,native.virtual_departures]
 def res(V):
    return float(np.max(abs(C@V[ret]-f))/max(np.max(abs(f)),np.max(abs(C)@abs(V[ret])),1e-100))
 assert res(VN)<1e-12
 # A replacement solve uses different wing equations: its residual under the
 # ORIGINAL proxy is an observation, not a required zero.
 print(name,'native Schur residual',res(VN),'actual snapshot proxy residual',res(V),flush=True)
 # Remove direct native real-line losses and corresponding virtual inflow.
 # All remaining proxy channels are EXTERNAL to physical selected line pairs.
 coeff=C[0,1:].copy()
 for i,k in [(139,rates.Aup_s_inv[139]),(140,rates.Adn_s_inv[140])]:
    coeff[np.flatnonzero(ret[1:]==i+2)[0]]+=k
 extloss=L(C[0,0])-L(rates.A2p_up_s_inv)-L(rates.A2p_dn_s_inv)
 eq=L(3)*L(1-s.xHII)*np.exp(-el/L(s.Tr_eV))
 q_native=L(nh)*(L(f[0])-np.asarray(coeff,dtype=L)@V[ret[1:]].astype(L)+extloss*eq)
 # Map labelled physical photon occupation back to native nodal occupation,
 # using positive barycentric measures, independent of proxy amplitude.
 vv=[];gaps=[]
 for lo,hi,pr,ids,gt,o in parts:
    sl=slice(0,o.n) if lo==parts[0][0] else slice(parts[0][-1].n,N)
    cap=pr.deposit(gt);nbar=pr.deposit(base[sl]);vnew=L(1-s.xHII)*(nbar/cap-1/np.expm1(pr.coarse/tc))
    vv.extend(vnew);ref=V[2+lo:3+hi];gaps.append(float(np.sum(abs(vnew-ref))/max(np.sum(abs(ref)),L("1e-4900"))))
 q_phys=L(nh)*(L(f[0])-np.asarray(coeff,dtype=L)@np.array(vv,dtype=L)+extloss*eq)
 gamma=extloss+line.s.sum()
 p_native=(q_native+line.r@base)/gamma;p_phys=(q_phys+line.r@base)/gamma
 row=dict(case=name,native_matrix_relative=res(VN),actual_proxy_relative=res(V),external_loss=float(extloss),previous_anchored_loss=float(loss),anchored_q=float(line.source),native_q=float(q_native),projected_q=float(q_phys),native_q_relative=float(q_native/line.source-1),physical_q_relative=float(q_phys/line.source-1),p_original=float(p0),p_native=float(p_native),p_projected=float(p_phys),projection_relative=gaps,scope='native proxy Schur external source evaluated at frozen wing occupations; physical line pair; no paired external photon feedback')
 rows.append(row);print(row,flush=True)
out=dict(status='SCOPED_NATIVE_EXTERNAL_SOURCE_CLOSURE_AUDIT',rows=rows,source_hashes=sources,full_sha=sha(P/'FULL_128.npz'),graph_sha=sha(G/'GRAPH128.npz'),rates_sha=sha(R),scope='actual 313 native matrix, eliminated 2s and exterior virtual states, conditional on selected native wing departures; physical source projection is not a complete conservative native FULL writeback')
(D/'SCHUR.json').write_text(json.dumps(out,indent=2)+'\n')

import sys,json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from line_face import LineOwner,Owner,L
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
own=WingCorrection(tab,graph,n0);lo,hi,p,i,j,K=own.windows[1]
E=graph['et'];ii,jj=graph['i'],graph['j'];mask=(E[ii]>=p.coarse[0])&(E[ii]<=p.coarse[-1])&(E[jj]>=p.coarse[0])&(E[jj]<=p.coarse[-1]);ids=np.unique(np.r_[ii[mask],jj[mask]])
assert np.array_equal(E[ids],p.fine);gt=graph['gt'][ids];e=p.fine;N=len(e);idx=104
T0=1e7;z0=float(z[idx]);u0=float(v['u'][idx]);delay=float(np.log(p.coarse[-1]/max(e)))
clock=solve_ivp(lambda t,y:[m.cosmology((1+z0)*np.exp(-y[0])-1)[0]],(0,T0),[0.],rtol=1e-12,atol=1e-25,dense_output=True)
assert clock.success and clock.y[0,-1]<delay
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
 tc=L(s.Tr_eV);tm=L(s.Tm_eV);f=1/np.expm1(p.coarse/tc)+r.virtual_departures[lo:hi+1]/L(1-s.xHII)
 zeta=np.exp(-(p.coarse-L('10.198714553953742'))/tm);ac=f/(zeta*(1+f));af=p.lift(ac)
 cap=gt*np.exp(-(e-L('10.198714553953742'))/tm);base=cap*af
 assert min(base)>0 and max(base/gt)<1e-12
 o=Owner(e,gt,i,j,K)
 def bath(t):
    u=float(clock.sol(t)[0]);zz=(1+z0)*np.exp(-u)-1;eta=u0+u
    H,nh=m.cosmology(zz);T=float(np.interp(eta,v['u'][:len(tt)],tt));x=float(np.interp(eta,v['u'][:len(xx)],xx))
    ret=eta-delay;assert ret<v['u'][idx]
    incoming=L(np.interp(ret,v['u'][:idx],virt[hi,:idx]))
    tr=L(KB_NATIVE_EV_K)*L(m.tcmb0_K)*(1+L(zz))
    f=1/np.expm1(max(e)/tr)+incoming
    if f<=0:raise ValueError('incoming domain')
    influx=np.exp(3*L(u))*L(8*np.pi)*(max(e)/L('1.239841874331e-4'))**3*L(1e6)*f
    return H,L(T)*L(KB_NATIVE_EV_K),L(nh*(1-x))/L(n0),influx


 # Matched no-line owner with exactly the same frozen bath and causal clock.
 H0,T,sc,_=bath(0.);A0=o.matrix((0.,T,sc,0.));A1=o.matrix((1.,T,sc,0.))-A0
 base0=np.r_[base,np.zeros(6,dtype=L)];sv=np.r_[np.asarray(base,float),np.full(6,float(max(base)))]
 def affine(t):
    H,_,_,inc=bath(t);A=bmat([[A0+H*A1,csr_matrix((N+6,6))]],format='csr');b=np.zeros(N+6);b[o.top]=float(H*inc)*o.tw;b[N+3]=float(H*inc);b[N+4]=float(H*inc*max(e));return A,b
 def rhs(t,y):
    A,b=affine(t);return (A@np.asarray(base0,float)+b+A@(sv*y))/sv
 def jac(t,y):
    A,_=affine(t);return diags(1/sv)@A@diags(sv)
 s=solve_ivp(rhs,(0,T0),np.zeros(N+6),method='BDF',jac=jac,rtol=1e-11,atol=1e-13);assert s.success
 q=np.asarray(s.y[:,-1]*sv,dtype=L);c=np.load(D/(name+'_line_state.npz'));d=c['dynamic'][:N]
 row=dict(case=name,relative_line_effect=float(np.sum(abs(d-q[:N]))/np.sum(abs(q[:N]))),line_effect_count=float((d-q[:N]).sum()),no_line_escaped=float(q[N]),no_line_energy_change=float(q[:N]@e),line_energy_change=float(d@e),nfev=s.nfev)
 rows.append(row);print(row,flush=True)
(D/'CONTROL.json').write_text(json.dumps(dict(rows=rows,scope='matched frozen bath, same retarded top source, no real line exchange'),indent=2)+'\n')

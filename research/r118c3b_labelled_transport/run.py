import sys,json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from labelled import Owner,L
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
 scale=max(base)
 refs=[]
 for tol in (1e-9,1e-11):
    sol=solve_ivp(lambda t,y:np.asarray(o.direct(base+np.asarray(y[:N],dtype=L)*scale,bath(t))/scale,float),(0,T0),np.zeros(N+6),method='DOP853',rtol=tol,atol=tol/100,dense_output=True)
    assert sol.success;refs.append(sol);print(name,'reference',tol,sol.nfev,flush=True)
 ref=np.asarray(refs[-1].y[:,-1],dtype=L)*scale
 gap=float(np.sum(abs((refs[0].y[:N,-1]-refs[-1].y[:N,-1])*scale))/np.sum(abs(ref[:N])))
 def ledger(d,ee):
    n=len(ee);nn=abs(d[:n].sum()+d[n]-d[n+3])/max(abs(d[n])+abs(d[n+3])+np.sum(abs(d[:n])),L('1e-4900'))
    en=abs(d[:n]@ee+d[n+1]+d[n+2]+d[n+5]-d[n+4])/max(np.sum(abs(d[:n]*ee))+sum(abs(d[n+1:])),L('1e-4900'))
    return float(nn),float(en)
 for n in (8,32,128):
    d=np.zeros(N+6,dtype=L);dt=T0/n
    for k in range(n):d+=o.midpoint(base+d[:N],k*dt,dt,bath)
    nr,er=ledger(d,e);assert max(nr,er)<1e-10
    row=dict(case=name,steps=n,reference_gap=gap,relative=float(np.sum(abs(d[:N]-ref[:N]))/np.sum(abs(ref[:N]))),number_residual=nr,energy_residual=er,top_in=float(d[N+3]),bottom_out=float(d[N]),work=float(d[N+2]),bath=float(d[N+5]),energy_change=float(d[:N]@e),min_stock=float(min(base+d[:N])),z_end=float((1+z0)*np.exp(-clock.y[0,-1])-1))
    rows.append(row);print(row,flush=True)
    if n==128:np.savez_compressed(D/(name+'_state.npz'),ids=ids,e=e,base=base,increment=d,reference=ref)
 # same-energy lumping control, conservative aggregate exact initial count.
 u,iv=np.unique(e,return_inverse=True);g=np.zeros(len(u),dtype=L);n0g=g.copy();np.add.at(g,iv,gt);np.add.at(n0g,iv,base)
 a0,b0=iv[i],iv[j];mask=a0!=b0;cg=Owner(u,g,a0[mask],b0[mask],K[mask]);ng=len(u)
 d=np.zeros(ng+6,dtype=L)
 for k in range(128):d+=cg.midpoint(n0g+d[:ng],k*T0/128,T0/128,bath)
 q=np.zeros(ng,dtype=L);np.add.at(q,iv,ref[:N])
 row=dict(case=name,steps=128,grouped=True,relative=float(np.sum(abs(d[:ng]-q))/np.sum(abs(q))),number_residual=ledger(d,u)[0],energy_residual=ledger(d,u)[1]);rows.append(row);print(row,flush=True)
out=dict(status='SCOPED_LABELLED_CAUSAL_BLUE_WING',rows=rows,source_hashes=sources,full_sha=sha(P/'FULL_128.npz'),graph_sha=sha(G/'GRAPH128.npz'),rates_sha=sha(R),mode_count=N,unique_energy=len(np.unique(e)),selected_edges=len(K),delay=delay,clock_end=float(clock.y[0,-1]),scope='dilute labelled scattering + positive upwind redshift, actual accepted retarded top face, prescribed FULL gas, frozen temperature dependence of K with neutral scaling; no refined opacity or writeback')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')

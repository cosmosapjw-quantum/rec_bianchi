"""Directional Ly-alpha QSS using actual accepted angular incoming history, not mean bath."""
import json,sys,numpy as np,hashlib
from pathlib import Path
from dataclasses import replace
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3g_causal_shared_gas'))
sys.path.insert(0,str(D.parent/'r118c3f_directional_history'))
sys.path.insert(0,str(D.parent/'r118c3j_integrated_history'))
from shared_gas import Clock,stf,B,P,R,_canonical_twophoton_table,OriginalHyRecPrimitiveRateTable,populate_original_full_atomic,KB_NATIVE_EV_K
from canonical_history import raymap,interpF,incoming_canonical,step
from line_cell import phase,A21,EL
from scipy.constants import k,m_p,c
sys.path.insert(0,str(D.parent/'r118c3o_coupled_jumps'))
from sourced_line import advance
sys.path.insert(0,str(D.parent/'r118c3q_paired_difference'))
from network import effective
LY=4.662899067555897e15
def run():
 path=D.parent/'r118c3g_causal_shared_gas/ACCEPTED_LOCAL_DIRECTIONAL.npz';v=np.load(path);orig=np.load(P);eta=-np.log1p(orig['z']);o=np.r_[orig['virtual_out'],orig['lyman_out']].T
 assert str(v['prefix_sha'])==hashlib.sha256(P.read_bytes()).hexdigest()
 g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 n=v['rays'];w=v['weights0'];Fref=v['reference_F'];tab=_canonical_twophoton_table(R)
 m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
 samples=[]
 for j in np.unique(np.linspace(0,len(v['eta'])-1,33).astype(int)):
  u=v['eta'][j];z=np.expm1(-u);Tr=m.tcmb0_K*(1+z);x=v['rows'][j+1,1];T=v['rows'][j+1,2];H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;source=replace(m,H=H);_,nh=source.cosmology(z)
  he=np.r_[eta[:64],v['eta'][:j]];hist=np.concatenate([np.broadcast_to(o[:64,None,:],(64,len(n),314)),v['outgoing'][:j]])
  inc,delay=incoming_canonical(ge,F,u,Fref,n,tab.energy_eV,he,hist,Tr)
  nf,ww=raymap(interpF(ge,F,u),Fref,n,w);ww/=ww.sum();S=stf([np.interp(u,ge,g[f'S{i}']) for i in range(5)]);rates=1+np.einsum('ni,ij,nj->n',nf,S,nf)
  snap=populate_original_full_atomic(source,z=z,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@inc[:,:311],incoming_lyman=ww@inc[:,311:]);rr,oo,dd=step(snap,rates,inc,ww)
  x1=1-x;bol=np.exp(-EL/(KB_NATIVE_EV_K*Tr));pop=3*x1*bol+rr.real_departures[1];fin=1/np.expm1(EL/(KB_NATIVE_EV_K*Tr))+inc[:,311]
  dln=np.sqrt(2*k*T/(m_p*c*c));C=phase(nh,dln);kc=C*H*rates/dln
  num=rr.real_departures[1]*(1+fin)-3*x1*(1-bol)*inc[:,311]
  df=A21*num/(A21*(3*x1-pop)+kc);J=kc*df
  atom=A21*(num-(3*x1-pop)*df)
  native=LY*H/(nh*1e-6*x1)*rates*(rr.real_departures[1]-3*x1*inc[:,311])
  direct=float(abs(ww@(atom-J))/max(abs(ww@J),1e-300))
  ks=H*rates/dln;nn0=C*ww*fin;X=x1+pop;duration=1/(ww@ks);dyn=[]
  sch=effective(snap,rates,inc,ww);jnative=sch['line']
  assert np.linalg.norm(sch['real']-rr.real_departures)<1e-12*np.linalg.norm(rr.real_departures)
  net_error=abs(sch['net']-jnative)/max(abs(jnative),1e-300)
  assert net_error<1e-6 and sch['loss']>=0
  # Conditional virtual departures and real 2s response for a dynamic 2p.
  # No photon counts assigned to algebraic virtual levels.
  E=sch['E'];Z=sch['Z'];ab=sch['ab'];v0=sch['v0'];r0=sch['real']
  coeff=-E[0,1]/E[0,0];dv= -Z@np.array([coeff,1.])
  row=np.array([-(snap.Trr[1,1]-sch['L']),-snap.Trr[1,0]*coeff,-snap.Trv[1]@dv])
  assert abs(row.sum()+sch['loss'])<1e-8*sch['loss']
  rec=snap.nH_cgs*(snap.saha_ratio*x1*snap.DAlpha_cgs+snap.Alpha_cgs*(snap.xe*snap.xHII-snap.saha_ratio*x1))-snap.Beta_s_inv*rr.real_departures
  assert abs(rec.sum()+H*rr.dxHII_dln_a)<1e-12*max(np.sum(abs(rec)),1e-300)
  samples.append(dict(rec=rec,beta=snap.Beta_s_inv,real_ref=rr.real_departures,u=float(u),H=H,x1=x1,Tr=Tr,T=T,ref=pop,C=C,w=ww,ks=ks,fin=fin,net=jnative,loss=sch['loss'],row=row,coeff=coeff,dv=dv))
 # Piecewise midpoint prescribed coefficients from actual native samples.
 # Conditional line owner evolves true 2p and photon counts; no reset at sample joins.
 def between(a,b,t,key):return (1-t)*a[key]+t*b[key]
 runs={}
 for ns in [8,16,32]:
  a0=samples[0];p0=a0['ref'];nn0=a0['C']*a0['w']*a0['fin'];pop=p0;nn=nn0.copy()
  ext=esc=inj=0.;budget=np.zeros(4);rec0=np.zeros(2);recd=np.zeros(2);time=0.;maxres=0.;maxflux=0.;history=[]
  for a,b in zip(samples[:-1],samples[1:]):
   for i in range(ns):
    t=(i+.5)/ns;v=lambda k:between(a,b,t,k)
    dt=(b['u']-a['u'])/ns/v('H');w=v('w');w/=w.sum();ref=v('ref');dp0=pop-ref
    dp,nn,e,j,ee,r=advance(dp0,nn,v('x1')+ref,v('C'),w,v('ks'),v('fin'),dt,ref,v('net'),v('loss'))
    pop=ref+dp;time+=dt;esc+=e;inj+=j;ext+=ee
    rec0+=dt*v("rec");recd-=dt*v("beta")*np.array([v("coeff")*dp,dp])
    terms=np.r_[v('net'),v('row')*dp]*dt;budget+=terms
    maxflux=max(maxflux,abs(terms.sum()-ee)/max(np.sum(abs(terms)),abs(ee),1e-300))
    maxres=max(maxres,abs(r))
   history.append([b['u'],pop,float(nn.sum()),ext,esc,inj])
  # Reservoir terms are line-equivalent; physical other-transition energies
  # are not supplied by the algebraic virtual levels.
  res=pop-p0+nn.sum()-nn0.sum()+esc-inj-ext;scale=p0+nn0.sum()+inj+abs(ext)
  assert abs(res)/scale<1e-10 and maxflux<1e-8
  runs[str(ns)]=dict(steps=ns*(len(samples)-1),duration_s=time,final_population=pop,final_photon_N=float(nn.sum()),net_escape=esc-inj,external_net=ext,external_components=budget.tolist(),relative_ledger=float(abs(res)/scale),line_equivalent_energy_residual=float(abs(res)*EL),max_flux_partition_error=maxflux,max_root_residual=maxres,integrated_native_recombination=rec0.tolist(),conditional_recombination_change=recd.tolist(),threshold_binding_release_eV_H=float(3.4*np.sum(rec0+recd)),threshold_binding_change_eV_H=float(3.4*np.sum(recd)),escaped_line_energy_eV_H=float(EL*(esc-inj)))
  np.savez_compressed(D/f'energy_line_{ns}.npz',rows=np.array(history),initial_N=nn0,final_N=nn)
 o=dict(samples=len(samples),runs=runs,source_sha=hashlib.sha256(path.read_bytes()).hexdigest(),scope='time-dependent prescribed actual native gas/geometry and reconstructed source samples; dynamic shared 2p and ray stocks; coefficients linearly interpolated, explicit n=2 continuum binding threshold (3.4 eV) and Ly-alpha energy, effective recombination not spectral emissivity; no full physical other transitions or gas feedback')
 (D/'PHYSICAL_RESERVOIR.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()

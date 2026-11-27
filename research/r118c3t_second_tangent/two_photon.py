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
 from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import A2S_THRESHOLD_EV,A3S3D_THRESHOLD_EV,A4S4D_THRESHOLD_EV
 thresholds=np.array([A2S_THRESHOLD_EV,A3S3D_THRESHOLD_EV,A4S4D_THRESHOLD_EV])
 for j in range(len(v['eta'])):
  u=v['eta'][j];z=np.expm1(-u);Tr=m.tcmb0_K*(1+z);x=v['rows'][j+1,1];T=v['rows'][j+1,2];H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;source=replace(m,H=H);_,nh=source.cosmology(z)
  he=np.r_[eta[:64],v['eta'][:j]];hist=np.concatenate([np.broadcast_to(o[:64,None,:],(64,len(n),314)),v['outgoing'][:j]])
  inc,delay=incoming_canonical(ge,F,u,Fref,n,tab.energy_eV,he,hist,Tr)
  nf,ww=raymap(interpF(ge,F,u),Fref,n,w);ww/=ww.sum();S=stf([np.interp(u,ge,g[f'S{i}']) for i in range(5)]);rates=1+np.einsum('ni,ij,nj->n',nf,S,nf)
  snap=populate_original_full_atomic(source,z=z,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@inc[:,:311],incoming_lyman=ww@inc[:,311:]);rr,oo,dd=step(snap,rates,inc,ww)
  te=snap.Tr_eV;E=tab.energy_eV;A=np.array([tab.A2s_s_inv,tab.A3s3d_s_inv,tab.A4s4d_s_inv])
  k=A/np.abs(np.expm1((E[None,:]-thresholds[:,None])/te));k[1:]*=np.exp(-(thresholds[1:]-thresholds[0])/te)[:,None]/3
  reverse=k*np.exp((E-thresholds[0])/te)[None,:]*np.array([1.,3.,3.])[:,None]
  r=rr.real_departures;vv=rr.virtual_departures
  J=k*np.array([r[0],r[1],r[1]])[:,None]-reverse*vv[None,:]
  co=tab.evaluate_canonical_coupling(radiation_temperature_eV=te)
  want=co.real_to_virtual_s_inv*r[:,None]-co.virtual_to_real_s_inv*vv[None,:]
  got=np.stack([J[0],J[1]+J[2]])
  assert np.max(abs(want-got))<1e-12*max(np.max(abs(want)),1e-300)
  mask=E[None,:]<thresholds[:,None]
  en=J*E;comp=J*(thresholds[:,None]-E);allE=J*thresholds[:,None]
  err=np.max(abs(en+comp-allE))/max(np.max(abs(allE)),1e-300)
  assert err<1e-14
  row=np.array([[np.sum(np.where(m,J,0),axis=1),np.sum(np.where(m,en,0),axis=1),np.sum(np.where(m,comp,0),axis=1),np.sum(np.where(m,allE,0),axis=1)] for m in [mask,~mask]])
  samples.append((u,H,row,err))
 u=np.array([q[0] for q in samples]);H=np.array([q[1] for q in samples]);F=np.array([q[2] for q in samples])/H[:,None,None,None]
 runs={}
 for n in [33,65,len(u)]:
  ids=np.unique(np.linspace(0,len(u)-1,n).astype(int));q=np.trapezoid(F[ids],u[ids],axis=0)
  runs[str(len(ids))]=dict(two_photon=q[0].tolist(),raman=q[1].tolist(),total_transition_eV_H=float(q[:,3].sum()),tracked_eV_H=float(q[:,1].sum()),companion_eV_H=float(q[:,2].sum()),energy_residual=float(abs(q[:,1].sum()+q[:,2].sum()-q[:,3].sum())))
 np.savez_compressed(D/'TWO_PHOTON.npz',u=u,H=H,source=F,thresholds=thresholds)
 o=dict(samples=len(samples),axes='rows N, tracked energy, signed companion energy, transition energy; columns 2s,3s3d,4s4d',runs=runs,max_source_energy_relative=float(max(q[3] for q in samples)),source_sha=hashlib.sha256(path.read_bytes()).hexdigest(),scope='source-identical native real/virtual departure coupling, net effective transition budget; tracked plus signed companion energy by channel. Companion thermal bath prescribed, not emitted/escaped spectral trajectory; no double counting or full physical reservoir claim.')
 (D/'TWO_PHOTON.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()

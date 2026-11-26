"""Conditional common-atom angular closure using actual Bianchi-I coframes."""
import numpy as np
from dataclasses import replace
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import accurate_escape_factors,_original_escape_factors
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges,_planck_difference
from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K
def interpF(eta,F,x):
 return np.stack([np.interp(x,eta,F[:,i,j]) for i in range(3) for j in range(3)],axis=-1).reshape(np.shape(x)+(3,3))
def retarded(eta,F,face,lr,n):
 if np.any(lr<=0) or face>eta[-1] or face<eta[0]:raise ValueError('domain')
 ff=interpF(eta,F,face);p=n@ff;d=np.broadcast_to(lr[None,:],(len(n),len(lr))).copy()
 for k in range(80):
  t=face-d
  if np.min(t)<eta[0] or np.max(t)>eta[-1]:raise ValueError('retarded coframe domain')
  fm=interpF(eta,F,t)
  v=np.linalg.solve(np.swapaxes(fm,-1,-2),np.broadcast_to(p[:,None,:,None],t.shape+(3,1)))[...,0]
  R=np.log(np.linalg.norm(v,axis=-1));nd=lr[None,:]-R
  if np.max(abs(nd-d))<2e-14:return nd,R
  d=nd
 raise ValueError('retarded root')
def incoming(eta,F,face,energies,n,history_eta,history,tc):
 src,ef,es=_source_edges(energies)
 d,R=retarded(eta,F,face,np.log(es/ef),n);t=face-d
 if np.max(t)>=history_eta[-1]:raise ValueError('unaccepted source')
 v=np.stack([np.interp(t[:,i],history_eta,history[j],left=0.) for i,j in enumerate(src)],axis=1)
 geom=_planck_difference(ef[None,:]/(KB_NATIVE_EV_K*tc),R)
 return v+geom,d,geom
def common(snapshot,rates,inc,w):
 # Directional virtual balance: v_d = (1-pi_d)x1s f_in,d + source/diag_d.
 # Shared atom and neighbor average v: average this equation before inversion.
 a=np.asarray(rates);w=np.asarray(w)
 if np.min(a)<=0 or abs(w.sum()-1)>1e-12:raise ValueError('angular expansion')
 p0,_=_original_escape_factors(snapshot.Dtau);tau=snapshot.Dtau[None,:]/a[:,None]
 pi,_=accurate_escape_factors(tau);inv=np.divide(pi,p0[None,:],out=np.broadcast_to(1/a[:,None],tau.shape).copy(),where=p0[None,:]>0)/snapshot.Tvv[0]
 # gamma/pi ratio uses accurate p0 for consistent stable representation,
 # but exact zero-shear native branch remains separate.
 pp,_=accurate_escape_factors(snapshot.Dtau)
 inv=np.divide(pi,pp[None,:],out=np.broadcast_to(1/a[:,None],tau.shape).copy(),where=pp[None,:]>0)/snapshot.Tvv[0]
 vv=snapshot.Tvv.copy();vv[0]=1/(w@inv)
 sv=vv[0]*(1-snapshot.xHII)*(w@((1-pi)*inc[:,:311]))
 ly=w@(a[:,None]*inc[:,311:])
 # Native sr's line terms weighted by H_n; non-line part unchanged.
 sr=snapshot.sr.copy();lyrate=4.662899067555897e15*snapshot.H_s_inv/(snapshot.nH_cgs*(1-snapshot.xHII))
 sr[0]+=3*lyrate*(1-snapshot.xHII)*1.664786871919931*(ly[1]-snapshot.incoming_lyman[1])
 sr[1]+=3*lyrate*(1-snapshot.xHII)*(ly[0]-snapshot.incoming_lyman[0])
 return replace(snapshot,Tvv=vv,sv=sv,sr=sr,incoming_virtual=w@inc[:,:311],incoming_lyman=ly)

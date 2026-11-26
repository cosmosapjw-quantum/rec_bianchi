"""One shared real atom, canonical angular rays and accepted virtual history."""
import numpy as np
from dataclasses import replace
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import accurate_escape_factors,_original_escape_factors
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges,_planck_difference
from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K
def raymap(F,Fref,n,w):
 L=np.linalg.solve(F.T,Fref.T)
 v=n@L.T;r=np.linalg.norm(v,axis=1)
 return v/r[:,None],w*abs(np.linalg.det(L))/r**3
def reconstruct(f,pi,tr,source,x1):
 return x1*((1-pi)*f+pi*source),f+(source-f)*tr
def interpF(eta,F,x):
 return np.stack([np.interp(x,eta,F[:,i,j]) for i in range(3) for j in range(3)],axis=-1).reshape(np.shape(x)+(3,3))
def incoming_canonical(eta,F,face,Fref,n,energies,he,hist,tc):
 src,ef,es=_source_edges(energies)
 lr=np.log(es/ef)
 ff=interpF(eta,F,face);p=n@Fref
 nf=np.linalg.solve(ff.T,p.T).T;nf/=np.linalg.norm(nf,axis=1)[:,None];p=nf@ff
 d=np.broadcast_to(lr[None,:],(len(n),len(lr))).copy()
 for _ in range(40):
    t=face-d
    if t.min()<eta[0] or t.max()>eta[-1]:raise ValueError("coframe domain")
    fm=interpF(eta,F,t)
    v=np.linalg.solve(np.swapaxes(fm,-1,-2),np.broadcast_to(p[:,None,:,None],t.shape+(3,1)))[...,0]
    R=np.log(np.linalg.norm(v,axis=-1));nd=lr[None,:]-R
    if np.max(abs(nd-d))<2e-14:
        d=nd;break
    d=nd
 else:raise ValueError("retarded convergence")
 t=face-d
 if np.max(t)>=he[-1]:raise ValueError("future accepted source")
 # Gather two adjacent accepted time points, with canonical ray label unchanged.
 k=np.searchsorted(he,t,side='right')-1;before=k<0;k=np.clip(k,0,len(he)-2)
 r=(t-he[k])/(he[k+1]-he[k])
 ix=np.arange(len(n))[:,None];v=(1-r)*hist[k,ix,src[None,:]]+r*hist[k+1,ix,src[None,:]]
 v=np.where(before,0.,v)
 geom=_planck_difference(ef[None,:]/(KB_NATIVE_EV_K*tc),R)
 return v+geom,d
def step(snapshot,rates,inc,w):
 from full_bianchi_hyrec.trajectory.full_2012_atomic_source import complete_original_full_atomic
 from full_bianchi_hyrec.trajectory.hmla_flrw import LYA_FACT_CM3
 a=np.asarray(rates);w=np.asarray(w)
 if min(a)<=0 or abs(w.sum()-1)>1e-8:raise ValueError("angular quadrature")
 w=w/w.sum()
 pi0,_=_original_escape_factors(snapshot.Dtau);tau=snapshot.Dtau[None,:]/a[:,None]
 pi,tr=accurate_escape_factors(tau)
 gamma=pi0*snapshot.Tvv[0]
 active=snapshot.Dtau>1e-30
 # zero optical depth diagonal scales H; transparent branch has no emission
 inv=np.divide(pi,gamma[None,:],out=np.broadcast_to(1/(a[:,None]*snapshot.Tvv[0]),tau.shape).copy(),where=gamma[None,:]>0)
 vv=snapshot.Tvv.copy();vv[0]=1/(w@inv)
 sv=vv[0]*(1-snapshot.xHII)*(w@((1-pi)*inc[:,:311]))
 ly=w@(a[:,None]*inc[:,311:])
 sr=snapshot.sr.copy();lyrate=LYA_FACT_CM3*snapshot.H_s_inv/(snapshot.nH_cgs*(1-snapshot.xHII))
 sr[0]+=3*lyrate*(1-snapshot.xHII)*1.664786871919931*(ly[1]-snapshot.incoming_lyman[1])
 sr[1]+=3*lyrate*(1-snapshot.xHII)*(ly[0]-snapshot.incoming_lyman[0])
 ss=replace(snapshot,Tvv=vv,sv=sv,sr=sr,incoming_virtual=w@inc[:,:311],incoming_lyman=ly)
 r=complete_original_full_atomic(ss);x1=1-snapshot.xHII
 v=r.virtual_departures
 neigh=np.zeros(311);neigh[1:]+=v[:-1]*ss.Tvv[1,1:];neigh[:-1]+=v[1:]*ss.Tvv[2,:-1]
 L=-(r.real_departures@ss.Tvr+neigh)
 eq=np.divide(L,x1*gamma,out=np.zeros_like(L),where=gamma>0)
 vd,out=reconstruct(inc[:,:311],pi,tr,eq,x1)
 out[:,~active]=inc[:, :311][:,~active]
 # Direct reconstruction using the exact per-direction inverse, including transparent limit.
 vd=x1*(1-pi)*inc[:,:311]+L*inv
 defect=float(np.max(abs(w@vd-v))/max(np.max(abs(v)),1e-300))
 # Three native optically thick Lyman boundary values remain common to all directions.
 return r,np.c_[out,np.broadcast_to(r.outgoing_lyman,(len(w),3))],defect

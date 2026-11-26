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
def incoming_canonical(eta,F,face,Fref,n,energies,he,hist,tc,mode):
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
 from paired_interp import sample
 v=sample(he,hist,t,src,mode)
 geom=_planck_difference(ef[None,:]/(KB_NATIVE_EV_K*tc),R)
 return v+geom,d
from canonical_history import step

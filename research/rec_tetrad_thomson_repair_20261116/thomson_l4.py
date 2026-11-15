#!/usr/bin/env python3
"""Positive degree-4 Thomson collision quadrature on original REC199 q128.
Source-independent kernel; native photon counts remain separately preserved.
"""
from __future__ import annotations
import numpy as np

def weights_l4(q):
    q=np.asarray(q,float)
    if q.shape!=(128,3) or not np.isfinite(q).all(): raise ValueError('expected original finite q128')
    if np.max(abs(np.sum(q*q,axis=1)-1))>3e-15: raise ValueError('unit q required')
    z=q[:,2]
    # Original 8 midpoint rings x16 equally spaced azimuths. Exact rational solution.
    w=(68083/61440-64517/47520*z*z+2641/1485*z**4)/128
    if np.min(w)<=0: raise ValueError('nonpositive quadrature')
    if abs(w.sum()-1)>3e-15 or np.max(abs(q.T@(w[:,None]*q)-np.eye(3)/3))>4e-15:
        raise ValueError('source grid does not satisfy moment contract')
    # Full fourth-order identity catches wrong grid, not just polar-ring matches.
    actual=np.einsum('n,na,nb,nc,nd->abcd',w,q,q,q,q)
    eye=np.eye(3)
    expected=(np.einsum('ab,cd->abcd',eye,eye)+np.einsum('ac,bd->abcd',eye,eye)+np.einsum('ad,bc->abcd',eye,eye))/15
    if np.max(abs(actual-expected))>5e-15: raise ValueError('degree4 grid contract')
    return w

def project_mass(native,w):
    native=np.asarray(native,float)
    if native.shape!=(len(w),) or not np.isfinite(native).all() or np.min(native)<0 or native.sum()<=0:
        raise ValueError('positive finite source mass required')
    # Native masses came from equal angular cells; re-integrate sampled intensity.
    projected=native*w
    return projected*(native.sum()/projected.sum())

def quadrupole(q,w,native):
    I=np.asarray(native,float)*len(w)
    mean=np.dot(w,I)/w.sum()
    # Analytically remove the isotropic baseline before reduction, avoiding cancellation.
    delta=I/mean-1
    return np.einsum('n,na,nb->ab',w*delta,q,q)/w.sum()

def operators(q,w):
    mu=q@q.T
    ep=np.column_stack((-q[:,1],q[:,0],np.zeros(len(q))))
    ep/=np.linalg.norm(ep,axis=1)[:,None]
    et=np.cross(ep,q)
    A=ep@q.T;B=et@q.T
    return .75*w[:,None]*(1+mu*mu),.75*w[:,None]*(A*A-B*B),-1.5*w[:,None]*(A*B)

def collision(q,native,p):
    if not np.isfinite(p) or p<0 or p>1: raise ValueError('probability outside [0,1]')
    w=weights_l4(q);m=project_mass(native,w)
    K,Q,U=operators(q,w)
    incoming=p*(K@m);dq=p*(Q@m);du=p*(U@m)
    return {'projected':m,'scattered_in':incoming,'delta':incoming-p*m,'Q':dq,'U':du}

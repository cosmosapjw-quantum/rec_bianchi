#!/usr/bin/env python3
"""Moment-exact Thomson estimator for continuum intensity sampled on Killing rays.
Physical tetrad map n=Aq/|Aq|; source q-cell mass is divided by solid-angle
Jacobian to recover physical intensity samples. Not a discrete-beam API.
"""
from __future__ import annotations
import numpy as np
from thomson_l4 import weights_l4,operators

def tetrad_grid(q,H,t):
    q=np.asarray(q,float);H=np.asarray(H,float)
    if q.shape!=(128,3) or H.shape!=(3,) or not np.isfinite(H).all() or not np.isfinite(t) or t<0:
        raise ValueError('source ray/metric/time contract')
    A=np.exp(-H*t)
    if not np.isfinite(A).all() or np.min(A)<=0:raise ValueError('noninvertible source metric')
    g=np.linalg.norm(q*A,axis=1)
    return q*A/g[:,None],np.prod(A)/g**3

def physical_weights(q,n,J,degree=4):
    if degree not in (4,6):raise ValueError('degree must be 4 or 6')
    def df(k):return np.prod(np.arange(k,0,-2,dtype=float)) if k>0 else 1.
    exps=[(a,b,degree-a-b) for a in range(degree+1) for b in range(degree-a+1)]
    M=np.array([np.prod(n**np.array(e),axis=1) for e in exps])
    target=np.array([0. if any(x%2 for x in e) else np.prod([df(x-1) for x in e])/df(degree+1) for e in exps])
    base=weights_l4(q)*J;base/=base.sum()
    # Unique least Euclidean correction to the mapped q quadrature; actual positivity checked.
    w=base+M.T@np.linalg.solve(M@M.T,target-M@base)
    if not np.isfinite(w).all() or np.min(w)<=0 or np.max(abs(M@w-target))>8e-15:
        raise ValueError('positive physical moment quadrature unavailable')
    return w

def project_q_mass(native,J,w,source_measure):
    if source_measure!='q_midpoint_continuum':raise ValueError('explicit continuum-sample interpretation required')
    native=np.asarray(native,float)
    if native.shape!=(128,) or not np.isfinite(native).all() or np.min(native)<0 or native.sum()<=0:
        raise ValueError('positive finite native source')
    I=native/J # native already includes q-cell Jacobian: do not multiply J twice
    m=I*w
    return m*(native.sum()/m.sum())

def physical_collision(q,H,t,native,p,source_measure):
    if not np.isfinite(p) or not 0<=p<=1:raise ValueError('invalid source collision probability')
    n,J=tetrad_grid(q,H,t);w=physical_weights(q,n,J)
    m=project_q_mass(native,J,w,source_measure);K,Q,U=operators(n,w)
    incoming=p*(K@m)
    return {'directions':n,'jacobian':J,'weights':w,'projected':m,'scattered_in':incoming,
            'delta':incoming-p*m,'Q':p*(Q@m),'U':p*(U@m)}

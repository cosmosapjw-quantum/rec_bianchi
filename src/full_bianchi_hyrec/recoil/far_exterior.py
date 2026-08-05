"""Far-wing boundary conductances beyond the near |x|=10.25 interface."""
from __future__ import annotations
import math
from functools import lru_cache
import numpy as np
from . import pair_cell_conductance as PCC
from .exterior_interface import exterior_pair_bundle

FAR_RED_EDGES=np.asarray([-21.25,-16.25,-12.75,-10.25])
FAR_BLUE_EDGES=-FAR_RED_EDGES[::-1]
FAR_RED_CELLS=tuple((float(l),float(r)) for l,r in zip(FAR_RED_EDGES[:-1],FAR_RED_EDGES[1:]))
FAR_BLUE_CELLS=tuple((float(l),float(r)) for l,r in zip(FAR_BLUE_EDGES[:-1],FAR_BLUE_EDGES[1:]))
FAR_CELLS=FAR_RED_CELLS+FAR_BLUE_CELLS

def _nodes(left,right,order):
    left=float(left);right=float(right)
    if not np.isfinite(left) or not np.isfinite(right) or right<=left: raise ValueError('interval must be finite and ordered')
    z,w=PCC.leggauss(int(order));return .5*(right-left)*z+.5*(right+left),.5*(right-left)*w

def interval_mode_measure(left,right,*,order=96):
    x,w=_nodes(left,right,order);nu=PCC.nu_abs+x*PCC.dnu
    return 8*math.pi*PCC.dnu/PCC.c**3*float(np.dot(w,nu**2))

def interval_thermal_weight(left,right,*,order=96):
    x,w=_nodes(left,right,order);nu=PCC.nu_abs+x*PCC.dnu
    return 8*math.pi*PCC.dnu/PCC.c**3*float(np.dot(w,nu**2*np.exp(-PCC.beta*PCC.h*nu)))

def interval_mean_momentum_scale(left,right,*,order=96):
    x,w=_nodes(left,right,order);nu=PCC.nu_abs+x*PCC.dnu
    return PCC.h/PCC.c*float(np.dot(w,nu**3))/float(np.dot(w,nu**2))

@lru_cache(maxsize=512)
def far_pair_bundle(target,source,*,lane='production',ell_max=24,amplitude_lane='full'):
    return exterior_pair_bundle(target,source,lane=lane,ell_max=ell_max,amplitude_lane=amplitude_lane)

@lru_cache(maxsize=512)
def far_pair_conductance(target,source,*,lane='production',ell_max=24,amplitude_lane='full'):
    return far_pair_bundle(target,source,lane=lane,ell_max=ell_max,amplitude_lane=amplitude_lane)[0]

def assemble_scalar_pair_generator(conductance,equilibrium_weight):
    conductance=np.asarray(conductance,float);pi=np.asarray(equilibrium_weight,float)
    if conductance.shape!=(len(pi),len(pi)):raise ValueError('conductance shape does not match equilibrium weights')
    if np.any(pi<=0):raise ValueError('equilibrium weights must be positive')
    if np.min(conductance)<-1e-30:raise ValueError('scalar conductances must be nonnegative')
    if np.max(np.abs(conductance-conductance.T))>1e-12*(np.max(np.abs(conductance))+1e-300):raise ValueError('conductance must be symmetric')
    g=conductance/pi[None,:];np.fill_diagonal(g,0);np.fill_diagonal(g,-g.sum(axis=0));return g

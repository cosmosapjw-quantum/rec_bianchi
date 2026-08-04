"""Nonlinear Bose action using zonal harmonic conductance moments."""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from scipy.special import sph_harm_y

@dataclass(frozen=True)
class HarmonicGrid:
    directions:np.ndarray;weights:np.ndarray;ell_max:int;lm:np.ndarray;synthesis:np.ndarray;analysis:np.ndarray;ell_of_mode:np.ndarray;gram_residual:float
    @property
    def n_angle(self):return int(len(self.weights))
    @classmethod
    def from_directions(cls,directions,weights,*,ell_max):
        d=np.asarray(directions,float);w=np.asarray(weights,float)
        if d.ndim!=2 or d.shape[1]!=3:raise ValueError('directions must have shape (n,3)')
        if w.shape!=(len(d),) or np.any(w<=0):raise ValueError('invalid weights')
        w=w/w.sum()
        if np.max(np.abs(np.linalg.norm(d,axis=1)-1))>1e-12:raise ValueError('directions must lie on unit sphere')
        th=np.arccos(np.clip(d[:,2],-1,1));ph=np.mod(np.arctan2(d[:,1],d[:,0]),2*math.pi)
        lm=[];cols=[]
        for l in range(ell_max+1):
            for m in range(-l,l+1):lm.append((l,m));cols.append(math.sqrt(4*math.pi)*sph_harm_y(l,m,th,ph))
        S=np.column_stack(cols);A0=S.conj().T*w[None,:];G=A0@S;I=np.eye(len(lm));res=float(np.max(np.abs(G-I)))
        A=A0 if res<1e-10 else np.linalg.solve(G,A0);res=float(np.max(np.abs(A@S-I)))
        return cls(d,w,int(ell_max),np.asarray(lm,int),S,A,np.asarray([l for l,_ in lm],int),res)
    def analyze(self,fields):
        f=np.asarray(fields);flat=f.reshape((-1,self.n_angle));c=(self.analysis@flat.T).T
        return c.reshape(f.shape[:-1]+(len(self.lm),))
    def synthesize(self,coefficients):
        c=np.asarray(coefficients);flat=c.reshape((-1,len(self.lm)));f=(self.synthesis@flat.T).T
        return np.real_if_close(f,tol=1000).reshape(c.shape[:-1]+(self.n_angle,))
    def partial_ell_fields(self,fields):
        f=np.asarray(fields);c=self.analyze(f);out=np.zeros(f.shape[:-1]+(self.ell_max+1,self.n_angle),complex)
        for l in range(self.ell_max+1):
            mask=self.ell_of_mode==l;part=c[...,mask].reshape((-1,int(mask.sum())))
            out[...,l,:]=(self.synthesis[:,mask]@part.T).T.reshape(f.shape[:-1]+(self.n_angle,))
        return np.real_if_close(out,tol=1000)

@dataclass(frozen=True)
class BoseActionResult:
    occupation_action:np.ndarray;number_action:np.ndarray;action_coefficients:np.ndarray;number_residual:float;entropy_production:float;Q_gamma:np.ndarray;Q_atom:np.ndarray;minimum_occupation:float;gross_action_scale:float

def apply_nonlinear_bose_operator(occupation,*,mode_measure,equilibrium_weight,pair_moments,same_cell_rates,grid,photon_momentum_scale=None):
    f=np.asarray(occupation,float);g=np.asarray(mode_measure,float);pi=np.asarray(equilibrium_weight,float);S=np.asarray(pair_moments,float);D=np.asarray(same_cell_rates,float)
    n=len(g)
    if f.shape!=(n,grid.n_angle):raise ValueError('occupation shape mismatch')
    if pi.shape!=(n,) or np.any(g<=0) or np.any(pi<=0):raise ValueError('invalid measures')
    if np.any(f<=0):raise ValueError('occupations must be strictly positive')
    if S.ndim!=3 or S.shape[1:]!=(n,n):raise ValueError('pair moments shape mismatch')
    if D.shape[1]!=n:raise ValueError('same-cell rate shape mismatch')
    if np.max(np.abs(S-np.swapaxes(S,1,2)))>1e-10*(np.max(np.abs(S))+1e-300):raise ValueError('pair moments must be symmetric')
    if np.min(S[0])<-1e-30:raise ValueError('scalar pair conductances must be nonnegative')

    z=pi/g
    phi=f/(z[:,None]*(1+f))
    # Subtract one common chemical-potential activity before every
    # convolution. This is an exact algebraic rearrangement and removes the
    # catastrophic cancellation of a near-BE state with q~1/z.
    q_ref=float(np.sum(phi*grid.weights[None,:])/n)
    delta_field=(1+f)*(phi-q_ref)
    partial_f=grid.partial_ell_fields(f)
    partial_one_plus=partial_f.copy();partial_one_plus[:,0,:]+=1.0
    partial_delta=grid.partial_ell_fields(delta_field)

    ell=min(grid.ell_max,S.shape[0]-1);C=np.zeros_like(f);gross=0.0
    for a in range(n):
        for b in range(a+1,n):
            moments=S[:ell+1,a,b]
            if moments[0]<=0:continue
            conv_delta_b=np.tensordot(moments,partial_delta[b,:ell+1],axes=(0,0))
            conv_delta_a=np.tensordot(moments,partial_delta[a,:ell+1],axes=(0,0))
            conv_one_b=np.tensordot(moments,partial_one_plus[b,:ell+1],axes=(0,0))
            conv_one_a=np.tensordot(moments,partial_one_plus[a,:ell+1],axes=(0,0))
            ca=np.real((1+f[a])*(conv_delta_b-(phi[a]-q_ref)*conv_one_b))
            cb=np.real((1+f[b])*(conv_delta_a-(phi[b]-q_ref)*conv_one_a))
            C[a]+=ca;C[b]+=cb
            # Gross forward+reverse scale, used only to normalize residuals.
            conv_f_b=np.tensordot(moments,partial_f[b,:ell+1],axes=(0,0))
            conv_f_a=np.tensordot(moments,partial_f[a,:ell+1],axes=(0,0))
            gross+=float(np.sum(grid.weights*(np.abs((1+f[a])*conv_f_b/z[b])+np.abs(f[a]*conv_one_b/z[a]))))
            gross+=float(np.sum(grid.weights*(np.abs((1+f[b])*conv_f_a/z[a])+np.abs(f[b]*conv_one_a/z[b]))))

    ellD=min(grid.ell_max,D.shape[0]-1)
    for a in range(n):
        same=np.real(np.tensordot(D[:ellD+1,a],partial_f[a,:ellD+1],axes=(0,0)))
        C[a]+=g[a]*same
        gross+=float(g[a]*np.sum(grid.weights*np.abs(same)))

    df=C/g[:,None];coeff=grid.analyze(df);num=float(np.sum(C*grid.weights[None,:]));psi=np.log(f/(1+f))-np.log(z)[:,None];entropy=float(np.sum(psi*C*grid.weights[None,:]))
    scale=np.ones(n) if photon_momentum_scale is None else np.asarray(photon_momentum_scale,float)
    weighted=C*grid.weights[None,:];q0=float(np.sum(scale[:,None]*weighted));qvec=np.sum(scale[:,None,None]*weighted[:,:,None]*grid.directions[None,:,:],axis=(0,1));qgamma=np.concatenate(([q0],qvec));qatom=-qgamma
    return BoseActionResult(df,C,coeff,num,entropy,qgamma,qatom,float(np.min(f)),gross)

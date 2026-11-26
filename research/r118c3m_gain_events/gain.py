"""Adjoint of original 2-real + 311-virtual angular atom; no perturbative finite differencing."""
import numpy as np
from scipy.linalg import solve_banded
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _original_escape_factors,accurate_escape_factors
from full_bianchi_hyrec.trajectory.hmla_flrw import LYA_FACT_CM3
from dataclasses import replace
def gain(s,rates,w):
 w=np.asarray(w)/sum(w);a=np.asarray(rates)
 pi0,_=_original_escape_factors(s.Dtau);pi,tr=accurate_escape_factors(s.Dtau[None,:]/a[:,None]);gamma=pi0*s.Tvv[0]
 iv=np.divide(pi,gamma[None,:],out=np.broadcast_to(1/(a[:,None]*s.Tvv[0]),pi.shape).copy(),where=gamma[None,:]>0)
 vv=s.Tvv.copy();vv[0]=1/(w@iv)
 # A_vv^T: upper row is original lower, lower row is original upper.
 ab=np.zeros_like(vv);ab[1]=vv[0];ab[0,1:]=vv[1,1:];ab[2,:-1]=vv[2,:-1]
 z=solve_banded((1,1),ab,s.Trv.T,check_finite=False)
 lr=np.linalg.solve(s.Trr.T-s.Tvr@z,s.Beta_s_inv/s.H_s_inv)
 lv=-z@lr
 x1=1-s.xHII;ly=LYA_FACT_CM3*s.H_s_inv/(s.nH_cgs*x1)
 gv=w[:,None]*vv[0]*x1*(1-pi)*lv
 gl=w[:,None]*a[:,None]*np.array([3*ly*x1*lr[1],3*ly*x1*1.664786871919931*lr[0]])
 return np.c_[gv,gl]
def moment_integrals(z):
 return z*z*(1-z)**2/2,z**3*(4/3-z),z**3*(3*z-2)/6
def gather1(he,L,M,R,t,src,area,area1):
 k=np.searchsorted(he,t,side='right')-1;before=k<0
 if np.any(t>=he[-1]):raise ValueError('future history')
 k=np.clip(k,0,len(he)-2);ix=np.arange(t.shape[0])[:,None];j=src[None,:]
 h=he[k+1]-he[k];z=np.where(before,0.,(t-he[k])/h)
 from quadratic import integ
 w=integ(z);v=h*(w[0]*L[k,ix,j]+w[1]*M[k,ix,j]+w[2]*R[k,ix,j])
 w=moment_integrals(z);v1=(he[k]-he[0])*v+h*h*(w[0]*L[k,ix,j]+w[1]*M[k,ix,j]+w[2]*R[k,ix,j])
 return np.where(before,0.,area[k,ix,j]+v),np.where(before,0.,area1[k,ix,j]+v1)
def means(he,L,M,R,area,area1,l,r,src):
 h=r-l
 if np.min(h)<=0:raise ValueError('retarded nonmonotone')
 a,b=gather1(he,L,M,R,l,src,area,area1);c,d=gather1(he,L,M,R,r,src,area,area1)
 return (c-a)/h,((d-b)-(l-he[0])*(c-a))/(h*h)
def update(he,L,M,R,area,area1,i):
 h=he[i]-he[i-1];v=h*(L[i-1]+4*M[i-1]+R[i-1])/6
 area[i]=area[i-1]+v
 area1[i]=area1[i-1]+(he[i-1]-he[0])*v+h*h*(M[i-1]/3+R[i-1]/6)
def correction(l,r,ev,t0,tl,tr,f0):
 # exact first Heaviside moment minus piecewise-affine arrival approximation
 mask=(ev>l)&(ev<r);a=np.clip((ev-l)/(r-l),0,1)
 b=np.clip((t0-tl)/(tr-tl),0,1)
 return np.where(mask,(b-a)*f0,0.),np.where(mask,(b*b-a*a)*f0/2,0.)

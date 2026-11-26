"""Exact homogeneous affine jump response at fixed gas / geometry."""
import numpy as np
from scipy.linalg import solve_banded
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _original_escape_factors,accurate_escape_factors
from full_bianchi_hyrec.trajectory.hmla_flrw import LYA_FACT_CM3
class JumpResponse:
 def __init__(self,s,rates,w):
  self.s=s;self.a=np.asarray(rates);self.w=np.asarray(w)/sum(w);self.x1=1-s.xHII
  pi0,_=_original_escape_factors(s.Dtau);self.pi,self.tr=accurate_escape_factors(s.Dtau[None,:]/self.a[:,None]);self.gamma=pi0*s.Tvv[0]
  inv=np.divide(self.pi,self.gamma[None,:],out=np.broadcast_to(1/(self.a[:,None]*s.Tvv[0]),self.pi.shape).copy(),where=self.gamma[None,:]>0)
  self.vv=s.Tvv.copy();self.vv[0]=1/(self.w@inv)
  self.ab=np.zeros_like(self.vv);self.ab[1]=self.vv[0];self.ab[0,1:]=self.vv[2,:-1];self.ab[2,:-1]=self.vv[1,1:]
  self.Z=solve_banded((1,1),self.ab,s.Tvr.T,check_finite=False)
  self.schur=s.Trr-s.Trv@self.Z
 def apply(self,d):
  s=self.s;ly=LYA_FACT_CM3*s.H_s_inv/(s.nH_cgs*self.x1)
  lyr=self.w@(self.a[:,None]*d[:,311:])
  br=3*ly*self.x1*np.array([1.664786871919931*lyr[1],lyr[0]])
  bv=self.vv[0]*self.x1*(self.w@((1-self.pi)*d[:,:311]))
  z=solve_banded((1,1),self.ab,bv,check_finite=False)
  r=np.linalg.solve(self.schur,br-s.Trv@z);v=z-self.Z@r
  neigh=np.zeros(311);neigh[1:]+=v[:-1]*self.vv[1,1:];neigh[:-1]+=v[1:]*self.vv[2,:-1]
  eq=np.divide(-(r@s.Tvr+neigh),self.x1*self.gamma,out=np.zeros(311),where=self.gamma>0)
  direct=np.zeros((len(self.w),314));direct[:,:311]=(1-self.tr)*d[:,:311]
  active=s.Dtau>1e-30;direct[:,:311][:,~active]=d[:,:311][:,~active]
  indirect=np.zeros_like(direct);indirect[:,:311]=self.tr*eq[None,:];indirect[:,:311][:,~active]=0.
  indirect[:,311:]=[r[1]/(3*self.x1),r[0]/self.x1*np.exp(-1.8886508433247664/s.Tr_eV),r[0]/self.x1*np.exp(-2.5496786384884356/s.Tr_eV)]
  return direct,indirect,float(s.Beta_s_inv@r/s.H_s_inv)

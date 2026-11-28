"""Analytic first JVP of actual fixed-snapshot angular/incident atomic map."""
import numpy as np
from scipy.linalg import solve_banded
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _original_escape_factors,accurate_escape_factors
from full_bianchi_hyrec.trajectory.hmla_flrw import LYA_FACT_CM3
def apply(s,a,w,da,dw,I,dI,scale):
 # scale multiplies the affine zero-incoming source only; I and dI are weak moments.
 wsum=w.sum();w=w/wsum;dw=(dw-w*dw.sum())/wsum
 tau=s.Dtau;pi0,_=_original_escape_factors(tau);t=tau[None,:]/a[:,None];dt=-t*da[:,None]/a[:,None]
 pi,tr=accurate_escape_factors(t);p=np.empty_like(t);small=t<.03;q=t[small];p[small]=.5+q*(-1/3+q*(1/8+q*(-1/30+q*(1/144-q/840))))
 q=t[~small];p[~small]=(-np.expm1(-q)-q*np.exp(-q))/q**2
 dp=p*dt;dtr=np.exp(-t)*dt;gamma=pi0*s.Tvv[0];ok=gamma>0
 inv=np.divide(pi,gamma[None,:],out=np.broadcast_to(1/(a[:,None]*s.Tvv[0]),pi.shape).copy(),where=ok[None,:])
 di=np.divide(dp,gamma[None,:],out=-inv*da[:,None]/a[:,None],where=ok[None,:])
 vv=1/(w@inv);dv=-vv*vv*(dw@inv+w@di)
 x1=1-s.xHII;inc=I[:,:311];dinc=dI[:,:311];Ly=I[:,311:];dLy=dI[:,311:]
 v=x1*(w@((1-pi)*inc));vd=x1*(dw@((1-pi)*inc)+w@((1-pi)*dinc-dp*inc))
 bv=vv*v;dbv=dv*v+vv*vd
 lyr=w@(a[:,None]*Ly);dly=dw@(a[:,None]*Ly)+w@(da[:,None]*Ly+a[:,None]*dLy)
 L=LYA_FACT_CM3*s.H_s_inv/(s.nH_cgs*x1);c=np.array([1.664786871919931,1.]);br=scale*(s.sr-3*L*x1*s.incoming_lyman[::-1]*c)+3*L*x1*lyr[::-1]*c;dbr=3*L*x1*dly[::-1]*c
 ab=np.zeros_like(s.Tvv);ab[1]=vv;ab[0,1:]=s.Tvv[2,:-1];ab[2,:-1]=s.Tvv[1,1:]
 Z=solve_banded((1,1),ab,s.Tvr.T,check_finite=False);E=s.Trr-s.Trv@Z
 def solve(b,r):
  v=solve_banded((1,1),ab,b,check_finite=False);r=np.linalg.solve(E,r-s.Trv@v);return r,v-Z@r
 r,v=solve(bv,br);dr,dv=solve(dbv-dv*v,dbr)
 def eq(r,v):
  neigh=np.zeros(311);neigh[1:]+=v[:-1]*s.Tvv[1,1:];neigh[:-1]+=v[1:]*s.Tvv[2,:-1]
  return np.divide(-(r@s.Tvr+neigh),x1*gamma,out=np.zeros(311),where=ok)
 q=eq(r,v);dq=eq(dr,dv)
 o=inc+(q-inc)*tr;do=dinc+(dq-dinc)*tr+(q-inc)*dtr
 mask=tau<=1e-30;o[:,mask]=inc[:,mask];do[:,mask]=dinc[:,mask]
 def ly(r):return np.broadcast_to([r[1]/(3*x1),r[0]/x1*np.exp(-1.8886508433247664/s.Tr_eV),r[0]/x1*np.exp(-2.5496786384884356/s.Tr_eV)],(len(a),3))
 gas=r@s.Beta_s_inv/s.H_s_inv-scale*np.sum(s.nH_cgs*(s.saha_ratio*x1*s.DAlpha_cgs+s.Alpha_cgs*(s.xe*s.xHII-s.saha_ratio*x1)))/s.H_s_inv
 return gas,np.c_[o,ly(r)],float(dr@s.Beta_s_inv/s.H_s_inv),np.c_[do,ly(dr)]

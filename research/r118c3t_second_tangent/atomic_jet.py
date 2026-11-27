"""Native fixed-state analytic outgoing Taylor coefficients, orders 0,1,2.
The native escape factor is complement pi; tr=1-exp(-tau/a).
"""
import numpy as np,sys
from pathlib import Path
from scipy.linalg import solve_banded
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _original_escape_factors,accurate_escape_factors
from full_bianchi_hyrec.trajectory.hmla_flrw import LYA_FACT_CM3
D=Path(__file__).resolve().parent
def mul(a,b):return np.array([sum(a[j]*b[k-j] for j in range(k+1)) for k in range(3)])
def atomic_jet(s,a,w,I,homogeneous=False):
 tau=s.Dtau;pi0,_=_original_escape_factors(tau);pi,tr=accurate_escape_factors(tau)
 small=tau<.03;pa=np.empty_like(tau);paa=pa.copy()
 c=np.array([.5,-1/6,1/24,-1/120,1/720,-1/5040]);k=np.arange(1,7)[:,None];v=c[:,None]*tau[small][None,:]**k
 pa[small]=np.sum(-k*v,axis=0);paa[small]=np.sum(k*(k+1)*v,axis=0)
 z=tau[~small];pa[~small]=np.exp(-z)+np.expm1(-z)/z;paa[~small]=z*np.exp(-z)
 nr=a.shape[1];p=np.array([np.broadcast_to(pi,(nr,311)),a[1,:,None]*pa,a[2,:,None]*pa+.5*a[1,:,None]**2*paa])
 t=np.array([np.broadcast_to(tr,(nr,311)),-tau*np.exp(-tau)*a[1,:,None],-np.exp(-tau)*(tau*a[2,:,None]+(.5*tau*tau-tau)*a[1,:,None]**2)])
 gamma=pi0*s.Tvv[0];iv=np.zeros_like(p);ok=gamma>0
 iv[:,:,ok]=p[:,:,ok]/gamma[ok]
 iv[:,:,~ok]=np.array([np.ones(nr),-a[1],a[1]**2-a[2]])[:,:,None]/s.Tvv[0,~ok]
 avg=mul(w[:,:,None],iv).sum(axis=1);vv=np.array([1/avg[0],-avg[1]/avg[0]**2,avg[1]**2/avg[0]**3-avg[2]/avg[0]**2])
 comp=-p.copy();comp[0]+=1;x1=1-s.xHII
 sv=x1*mul(vv,mul(mul(w[:,:,None],comp),I[:,:,:311]).sum(axis=1))
 ly=mul(mul(w[:,:,None],a[:,:,None]),I[:,:,311:]).sum(axis=1)
 L=LYA_FACT_CM3*s.H_s_inv/(s.nH_cgs*x1)
 sr=3*L*x1*ly[:,::-1]*np.array([1.664786871919931,1.])
 if not homogeneous:sr[0]+=s.sr-3*L*x1*s.incoming_lyman[::-1]*np.array([1.664786871919931,1.])
 ab=np.zeros_like(s.Tvv);ab[1]=vv[0];ab[0,1:]=s.Tvv[2,:-1];ab[2,:-1]=s.Tvv[1,1:]
 Z=solve_banded((1,1),ab,s.Tvr.T);E=s.Trr-s.Trv@Z
 rr=[];vvv=[]
 for j in range(3):
  bv=sv[j]-sum(vv[k]*vvv[j-k] for k in range(1,j+1))
  v=solve_banded((1,1),ab,bv);r=np.linalg.solve(E,sr[j]-s.Trv@v);rr.append(r);vvv.append(v-Z@r)
 rr,vvv=np.array(rr),np.array(vvv);neigh=np.zeros_like(vvv);neigh[:,1:]+=vvv[:,:-1]*s.Tvv[1,1:];neigh[:,:-1]+=vvv[:,1:]*s.Tvv[2,:-1]
 eq=np.divide(-(rr@s.Tvr+neigh),x1*gamma,out=np.zeros_like(vvv),where=gamma>0)
 out=I[:,:,:311]+mul(t,eq[:,None,:]-I[:,:,:311]);out[:,:,tau<=1e-30]=I[:,:,:311][:,:,tau<=1e-30]
 lyout=np.stack([rr[:,1]/(3*x1),rr[:,0]/x1*np.exp(-1.8886508433247664/s.Tr_eV),rr[:,0]/x1*np.exp(-2.5496786384884356/s.Tr_eV)],axis=1)
 out=np.concatenate([out,np.broadcast_to(lyout[:,None,:],(3,nr,3))],axis=2)
 gas=rr@s.Beta_s_inv/s.H_s_inv
 if not homogeneous:
  gas[0]-=np.sum(s.nH_cgs*(s.saha_ratio*x1*s.DAlpha_cgs+s.Alpha_cgs*(s.xe*s.xHII-s.saha_ratio*x1)))/s.H_s_inv
 return out,gas

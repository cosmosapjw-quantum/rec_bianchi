"""Fixed-gas analytic angular gain Taylor jets; native escape-factor convention."""
import sys,numpy as np
from scipy.linalg import solve_banded
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3m_gain_events'))
from gain import gain
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _original_escape_factors,accurate_escape_factors
from full_bianchi_hyrec.trajectory.hmla_flrw import LYA_FACT_CM3
def mul(a,b):return np.array([sum(a[j]*b[k-j] for j in range(k+1)) for k in range(3)])
def rate_weight(clock,u,w):
 n=clock.n;D1,D2=clock.jets(u);S=clock.S(u);b,c,bp=clock.bc(np.asarray(u),n)
 n1=n@D1.T-b[:,None]*n
 a1=np.einsum('ni,ij,nj->n',n,S,n);a2=2*np.einsum('ni,ij,nj->n',n1,S,n)
 f1=-3*b;f2=-3*c+4.5*b*b;m1=w@f1;m2=w@f2
 return np.array([np.ones_like(w),a1,a2]),np.array([w,w*(f1-m1),w*(f2-m2+m1*m1-m1*f1)])
def get(s,a,w):
 tau=s.Dtau;pi0,_=_original_escape_factors(tau);pi,_=accurate_escape_factors(tau)
 # pi is COMPLEMENT of (1-e^-tau)/tau, native stable small series.
 small=tau<.03
 pa=np.empty_like(tau);paa=pa.copy()
 # pi(a)=sum c_j (tau/a)^j. Exact derivative of implemented series.
 c=np.array([.5,-1/6,1/24,-1/120,1/720,-1/5040])
 z=tau[small];k=np.arange(1,7)[:,None];v=c[:,None]*z[None,:]**k
 pa[small]=np.sum(-k*v,axis=0);paa[small]=np.sum(k*(k+1)*v,axis=0)
 z=tau[~small];pa[~small]=np.exp(-z)+np.expm1(-z)/z;paa[~small]=z*np.exp(-z)
 pp=np.array([np.broadcast_to(pi,(a.shape[1],len(tau))),a[1,:,None]*pa,a[2,:,None]*pa+.5*a[1,:,None]**2*paa])
 gam=pi0*s.Tvv[0];iv=np.zeros_like(pp);ok=gam>0
 iv[:,:,ok]=pp[:,:,ok]/gam[ok]
 iv[:,:,~ok]=np.array([np.ones_like(a[0]),-a[1],a[1]**2-a[2]])[:,:,None]/s.Tvv[0,~ok]
 avg=np.sum(mul(w[:,:,None],iv),axis=1);vv=np.array([1/avg[0],-avg[1]/avg[0]**2,avg[1]**2/avg[0]**3-avg[2]/avg[0]**2])
 ab=np.zeros_like(s.Tvv);ab[1]=vv[0];ab[0,1:]=s.Tvv[1,1:];ab[2,:-1]=s.Tvv[2,:-1]
 Z=solve_banded((1,1),ab,s.Trv.T);E=s.Trr.T-s.Tvr@Z
 def solve(br,bv):
  z=solve_banded((1,1),ab,bv);r=np.linalg.solve(E,br-s.Tvr@z);return r,z-Z@r
 rr=[];lv=[]
 for j in range(3):
  r,v=solve(s.Beta_s_inv/s.H_s_inv if j==0 else np.zeros(2),-sum(vv[k]*lv[j-k] for k in range(1,j+1)) if j else np.zeros(311));rr.append(r);lv.append(v)
 rr,lv=np.array(rr),np.array(lv);x1=1-s.xHII
 comp=-pp.copy();comp[0]+=1
 gv=x1*mul(mul(mul(w[:,:,None],comp),vv[:,None,:]),lv[:,None,:])
 L=LYA_FACT_CM3*s.H_s_inv/(s.nH_cgs*x1)
 gl=3*L*x1*mul(mul(w[:,:,None],a[:,:,None]),rr[:,None,::-1]*np.array([1,1.664786871919931]))
 return rr@s.sr,np.concatenate([gv,gl],axis=2)

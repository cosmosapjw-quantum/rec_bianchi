"""Prescribed actual HMLA background on fixed physical frequency graph."""
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import solve_ivp
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L
class KernelHistory:
    def __init__(self,T,n,K):
        self.T=np.asarray(T,dtype=L);self.n=np.asarray(n,dtype=L);self.K=np.asarray(K,dtype=L)
        if not (np.all(np.diff(self.T)>0) and np.all(self.n>0) and np.all(self.K>0) and np.all(np.isfinite(self.K))):raise ValueError('positive ordered kernel domain')
        self.log=np.log(self.K/self.n[:,None])
    def __call__(self,T,n):
        T=L(T);n=L(n)
        if not self.T[0]<=T<=self.T[-1] or n<=0:raise ValueError('kernel interpolation domain')
        k=int(np.searchsorted(self.T,T,side='right')-1)
        if T==self.T[k]:return self.K[k]*(n/self.n[k])
        r=(T-self.T[k])/(self.T[k+1]-self.T[k])
        return self.K[k]*(n/self.n[k])*np.exp(r*(self.log[k+1]-self.log[k]))
class ActualBath:
    def __init__(self,rows,anchor):
        keys=['T_m_K','n_H_m3','x_1s','x_2s','H_s']
        rows=[r for r in rows if abs(r['z']-anchor['z'])>1e-10]+[anchor]
        rows=sorted(rows,key=lambda r:r['z']);self.z=np.array([r['z'] for r in rows])
        self.anchor=anchor
        self.splines={k:PchipInterpolator(self.z,[r[k] for r in rows],extrapolate=False) for k in keys}
    def point(self,z):
        out={k:float(v(z)) for k,v in self.splines.items()}
        if not all(np.isfinite(list(out.values()))):raise ValueError('bath history domain')
        out['n1s']=out['n_H_m3']*out['x_1s'];out['n2']=out['n_H_m3']*out['x_2s'];return out
    def clock(self,duration):
        z0=self.anchor['z']
        s=solve_ivp(lambda t,z:[-(1+z[0])*self.splines['H_s'](z[0])],(0,duration),[z0],rtol=1e-12,atol=1e-12,dense_output=True)
        if not s.success:raise RuntimeError(s.message)
        return lambda t:float(s.sol(t)[0])

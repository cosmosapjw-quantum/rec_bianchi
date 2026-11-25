"""Anchor-plus-increment activity inversion; no production owner change."""
import copy
import numpy as np
from scipy.constants import h,k,e
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L

class StableScatter:
    def __init__(self,sc,state):
        self.original=sc;self.net=sc.net
        for a in ('i','j','K','z','de','cross','new'):setattr(self,a,getattr(sc,a))
        s=state.clone();s.dt=np.zeros_like(s.dt);self.anchor=s.nt.copy()
        self.f0=self.net.point_values(s)
        self.a0=self.f0/(self.z*(1+self.f0))
        n=self.net.ncore
        if n:
            self.core0=self.f0[:n]/(self.net.zi*(1+self.f0[:n]))
            self.d0=1-self.core0[:,None]*self.net._z
            if np.min(self.d0)<=0:raise ValueError('base activity pole')
            self.der0=np.sum(self.net._w*self.net._z/self.d0**2,axis=1)
    def increments(self,s):
        if not np.array_equal(s.nt,self.anchor):raise ValueError('anchor stock mismatch')
        n=self.net.ncore;df=s.dt/self.net.gt;da=np.empty_like(df)
        if np.min(s.nt+s.dt)<0:raise ValueError('negative stock')
        da[n:]=df[n:]/(self.z[n:]*(1+self.f0[n:])*(1+self.f0[n:]+df[n:]))
        if n:
            w=self.net._w;z=self.net._z;target=df[:n].copy();d=target/self.der0
            for _ in range(12):
                d1=self.d0-d[:,None]*z
                if np.min(d1)<=0:raise ValueError('increment activity pole')
                res=d*np.sum(w*z/(self.d0*d1),axis=1)-target
                d-=res/np.sum(w*z/d1**2,axis=1)
            d1=self.d0-d[:,None]*z
            if np.min(d1)<=0:raise ValueError('increment activity pole')
            res=d*np.sum(w*z/(self.d0*d1),axis=1)-target
            if np.max(abs(res)/np.maximum(abs(target),L('1e-4900')))>1e-12:raise ValueError('increment inversion residual')
            dpoint=1-self.core0*self.net.zi
            df[:n]=d*self.net.zi/(dpoint*(dpoint-d*self.net.zi))
            da[:n]=d*self.net.zi/self.z[:n]
        if not np.isfinite(da).all() or np.min(self.f0+df)<0:raise ValueError('activity increments')
        return da,df
    def rates(self,s):
        da,df=self.increments(s);f=self.f0+df;i,j=self.i,self.j
        fac=self.K*(1+f[i])*(1+f[j])*(s.neutral-s.n2-s.d2)/L(self.net.q['n1s'])
        net=fac*((self.a0[j]-self.a0[i])+(da[j]-da[i]))
        gross=fac*((self.a0[j]+self.a0[i])+(da[j]+da[i]))
        if np.any(abs(net)>gross):raise ValueError('stable rate domain')
        return net,gross
    def rhs(self,s):
        f,g=self.rates(s);d=np.zeros_like(s.dt);np.add.at(d,self.i,f);np.add.at(d,self.j,-f)
        return d,f,g

def bath_at(net,sc,base,T):
    # Actual graph/energies/edge coefficients are frozen. Only thermal
    # activity factors change; source coefficients and n1s reference fixed.
    if not np.isfinite(T) or T<=0:raise ValueError('bath T')
    z=copy.copy(net);z.q=dict(net.q,T=float(T))
    ratio=L(net.q['T'])/L(T)
    z._z=np.exp(np.log(net._z)*ratio)
    z.zi=np.exp(np.log(net.zi)*ratio);z.zmean=np.sum(net._w*z._z,axis=1)
    z.z=[np.exp(np.log(v)*ratio) for v in net.z]
    ss=copy.copy(sc);ss.net=z;ss.z=np.exp(np.log(sc.z)*ratio)
    return z,StableScatter(ss,base)

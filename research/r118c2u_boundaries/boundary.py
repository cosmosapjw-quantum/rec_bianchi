"""Single ordered photon registry, positive external top influx."""
import sys
from pathlib import Path
import numpy as np
from scipy.special import gammainc
from scipy.constants import h,c,k,e
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2t_cosmological'))
from drift import Redshift,L
class JoinedDrift(Redshift):
    def __init__(self,et,gt,ec,gc):
        super().__init__(np.r_[et,ec],np.r_[gt,gc]);self.nt=len(et)
        self.top=np.flatnonzero(self.e==self.e.max());self.topw=self.g[self.top]/self.g[self.top].sum()
        self.cross=(self.j<self.nt)&(self.i>=self.nt)
        if np.any((self.j>=self.nt)&(self.i<self.nt)):raise ValueError('frequency domains overlap')
        self.cross_weight=np.zeros(len(self.e),dtype=L);np.add.at(self.cross_weight,self.j[self.cross],self.w[self.cross])
    def planck_influx(self,u,z0):
        # g(E) dE is proper number of modes per m3; E in eV.
        E=self.e.max();T=L('2.7255')*(1+L(z0))*np.exp(-L(u))
        spectral=L(8*np.pi)*L(e)**3*E**2/(L(h)**3*L(c)**3)
        return np.exp(3*L(u))*E*spectral/np.expm1(E*L(e)/(L(k)*T))
    def affine(self,base,delta,du,influx):
        base=np.asarray(base,dtype=L);d=np.array(delta,dtype=L,copy=True)
        if du<0 or influx<0 or np.min(base+d)<0:raise ValueError('domain')
        names=('escape_N','escape_U','work','in_N','in_U','cross_N')
        out={k:L(0) for k in names}
        if du==0:return d,out
        count=max(1,int(np.ceil(L(du)*self.lam/4)));hh=L(du)/count;x=float(hh*self.lam)
        b=np.zeros_like(base);b[self.top]=influx*self.topw
        for _ in range(count):
            n=base+d;v=n.copy();integ=-np.expm1(-L(x))/self.lam*v
            for kk in range(1,128):
                w=L(gammainc(kk+1,x))/self.lam
                if w<hh*L('1e-24'):break
                v=self.transition(v)+b/self.lam;integ+=w*v
            else:raise ValueError('uniformization cap')
            f=self.rate*integ;d+=self.divergence(f)+hh*b
            if np.min(base+d)<0:raise ValueError('negative photon stock')
            esc=f[self.escape].sum();out['escape_N']+=esc;out['escape_U']+=esc*self.ghost;out['work']+=f@self.de
            out['in_N']+=hh*influx;out['in_U']+=hh*influx*self.e.max();out['cross_N']+=f@self.cross_weight
        return d,out

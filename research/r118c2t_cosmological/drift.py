"""Positive upwind nodal photon redshift in comoving number units."""
import numpy as np
from scipy.special import gammainc
from scipy.sparse import coo_matrix
L=np.longdouble
class Redshift:
    def __init__(self,energy,phase):
        self.e=np.asarray(energy,dtype=L);self.g=np.asarray(phase,dtype=L)
        if len(self.e)<2 or np.min(self.e)<=0 or np.min(self.g)<=0:raise ValueError('positive grid')
        u,idx=np.unique(self.e,return_inverse=True)
        if len(u)<2:raise ValueError('distinct energy grid')
        self.ghost=u[0]-min(u[0]/2,u[1]-u[0])
        groups=[np.flatnonzero(idx==i) for i in range(len(u))]
        i=[];j=[];w=[]
        for k,group in enumerate(groups):
            if not k:continue
            prev=groups[k-1];wt=self.g[prev]/self.g[prev].sum()
            for v in group:
                for q,f in zip(prev,wt):i.append(q);j.append(v);w.append(f)
        self.i=np.array(i,int);self.j=np.array(j,int);self.w=np.array(w,dtype=L)
        self.escape=groups[0]
        prev=np.r_[self.ghost,u[:-1]][idx];self.de=self.e-prev;self.rate=self.e/self.de
        self.lam=self.rate.max();self.p=self.rate/self.lam
    def transition(self,n):
        v=(1-self.p)*n
        np.add.at(v,self.i,self.w*self.p[self.j]*n[self.j])
        return v
    def divergence(self,flux):
        d=-flux.copy();np.add.at(d,self.i,self.w*flux[self.j]);return d
    def increment(self,base,delta,du):
        base=np.asarray(base,dtype=L);d=np.array(delta,dtype=L,copy=True)
        if not np.isfinite(du) or du<0 or np.min(base+d)<0:raise ValueError('drift domain')
        ledger={k:L(0) for k in ('escape_N','escape_U','work')}
        if du==0:return d,ledger
        count=max(1,int(np.ceil(L(du)*self.lam/4)))
        if count>10000:raise ValueError('drift cap')
        h=L(du)/count;x=float(h*self.lam)
        for _ in range(count):
            n=base+d;v=n.copy();integ=(-np.expm1(-L(x))/self.lam)*v
            for k in range(1,128):
                weight=L(gammainc(k+1,x))/self.lam
                if weight<h*L('1e-24'):break
                v=self.transition(v);integ+=weight*v
            else:raise ValueError('uniformization cap')
            flux=self.rate*integ;d+=self.divergence(flux)
            if np.min(base+d)<0:raise ValueError('drift positivity')
            esc=flux[self.escape].sum();ledger['escape_N']+=esc;ledger['escape_U']+=esc*self.ghost;ledger['work']+=flux@self.de
        return d,ledger
    def advance(self,n,du):
        n=np.asarray(n,dtype=L);d,l=self.increment(n,np.zeros_like(n),du);return n+d,l
    def matrix(self):
        n=len(self.e);diag=np.arange(n);esc=self.escape
        return coo_matrix((np.asarray(np.r_[-self.rate,self.w*self.rate[self.j],self.rate[esc],self.rate[esc]*self.ghost,self.rate*self.de],float),
         (np.r_[diag,self.i,np.full(len(esc),n),np.full(len(esc),n+1),np.full(n,n+2)],np.r_[diag,self.j,esc,esc,diag])),shape=(n+3,n+3)).tocsr()

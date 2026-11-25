"""Zero-safe MPRK22: analytic per-donor coefficients, no physical stock floor."""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
L=np.longdouble
class ZeroMPRK:
    def __init__(self,i,j,n):
        self.i=np.asarray(i,int);self.j=np.asarray(j,int);self.n=n
    def div(self,f):
        d=np.zeros(self.n,dtype=L);np.add.at(d,self.i,f);np.add.at(d,self.j,-f);return d
    def stage(self,y,p,m,h):
        i,j=self.i,self.j;N=self.n
        if np.min(p)<0 or np.min(m)<0 or not np.isfinite(np.r_[p,m]).all():raise ValueError('coefficient domain')
        incoming=np.zeros(N,dtype=L);np.add.at(incoming,i,h*p*y[j]);np.add.at(incoming,j,h*m*y[i])
        scale=np.maximum(y,incoming);scale[scale==0]=1 # preconditioner only
        d=np.ones(N,dtype=L);np.add.at(d,i,h*m);np.add.at(d,j,h*p)
        M=coo_matrix((np.asarray(np.r_[d,-h*p*scale[j]/scale[i],-h*m*scale[i]/scale[j]],float),
          (np.r_[np.arange(N),i,j],np.r_[np.arange(N),j,i])),shape=(N,N)).tocsc()
        lu=splu(M)
        def solve(v):return np.asarray(lu.solve(np.asarray(v/scale,float)),dtype=L)*scale
        # Solve the absolute positive M-matrix system, then use integrated flux
        # for ledgers. This candidate is for depletion, not sub-ulp equilibrium.
        v=solve(y)
        def flux(v):return h*(p*v[j]-m*v[i])
        for _ in range(3):v+=solve(y+self.div(flux(v))-v)
        f=flux(v);g=h*np.sum(p*v[j]+m*v[i])
        resid=np.max(abs(y+self.div(f)-v))/max(np.sum(y),g,L('1e-4900'))
        if resid>1e-13 or np.min(v)<0 or not np.isfinite(v).all():raise ValueError('zero-safe stage residual/positivity')
        return v,f,g
    def advance(self,y,h,rates):
        y=np.asarray(y,dtype=L);h=L(h)
        if h<=0 or not np.isfinite(h) or np.min(y)<0:raise ValueError('stock domain')
        p,m=rates(y);Y,_,_=self.stage(y,p,m,h)
        p1,m1=rates(Y);i,j=self.i,self.j
        # numerator vanishes if Y donor=0; finite limit only used there
        cp=(p+p1)/2;cm=(m+m1)/2
        cp=np.divide((p*y[j]+p1*Y[j])/2,Y[j],out=cp,where=Y[j]>0)
        cm=np.divide((m*y[i]+m1*Y[i])/2,Y[i],out=cm,where=Y[i]>0)
        return self.stage(y,cp,cm,h)
class PhysicalCoefficients:
    def __init__(self,sc,state):
        self.sc=sc;self.net=sc.net;self.template=state.clone()
    def __call__(self,y):
        s=self.template.clone();s.nt=y.copy();s.dt=np.zeros_like(y)
        f=self.net.point_values(s);z=self.sc.z;a=f/(z*(1+f));n=self.net.ncore
        lim=1/(self.net.gt*z)
        lim[:n]=self.net.zi/(self.net.gt[:n]*self.net.zmean*z[:n])
        ratio=np.divide(a,y,out=lim,where=y>0)
        i,j=self.sc.i,self.sc.j
        fac=self.sc.K*(1+f[i])*(1+f[j])*(s.neutral-s.n2-s.d2)/L(self.net.q['n1s'])
        return fac*ratio[j],fac*ratio[i]

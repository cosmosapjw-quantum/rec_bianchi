"""Increment-resolved, zero-safe modified Patankar stage on original edge graph."""
import sys
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2q_activity_bath'))
from stable_activity import StableScatter
L=np.longdouble
class IncrementMPRK:
    def __init__(self,i,j,n):
        self.i=np.asarray(i,int);self.j=np.asarray(j,int);self.n=n
    def div(self,f):
        d=np.zeros(self.n,dtype=L);np.add.at(d,self.i,f);np.add.at(d,self.j,-f);return d
    def stage(self,base,d,h,net,p,m):
        i,j=self.i,self.j;N=self.n;y=base+d
        if np.min(y)<0 or np.min(p)<0 or np.min(m)<0 or not np.isfinite(np.r_[net,p,m]).all():
            raise ValueError('stage domain')
        inc=np.zeros(N,dtype=L);np.add.at(inc,i,h*p*y[j]);np.add.at(inc,j,h*m*y[i])
        scale=np.maximum(y,inc);scale[scale==0]=1
        diag=np.ones(N,dtype=L);np.add.at(diag,i,h*m);np.add.at(diag,j,h*p)
        mat=coo_matrix((np.asarray(np.r_[diag,-h*p*scale[j]/scale[i],-h*m*scale[i]/scale[j]],float),
                        (np.r_[np.arange(N),i,j],np.r_[np.arange(N),j,i])),shape=(N,N)).tocsc()
        lu=splu(mat)
        def solve(v):return np.asarray(lu.solve(np.asarray(v/scale,float)),dtype=L)*scale
        dy=solve(h*self.div(net))
        def flux(v):return h*(net+p*v[j]-m*v[i])
        for _ in range(3):dy+=solve(self.div(flux(dy))-dy)
        f=flux(dy);dy2=self.div(f);new=d+dy2
        # Gross rates are diagnostic, not the source of the net flux.
        g=h*np.sum(p*(base[j]+new[j])+m*(base[i]+new[i]))
        res=np.max(abs(dy2-dy))/max(g,L('1e-4900'))
        if res>1e-12 or np.min(base+new)<0 or not np.isfinite(new).all() or g<0:
            raise ValueError('stage residual/positivity')
        return new,f,g
    def advance(self,base,d,h,rates):
        base=np.asarray(base,dtype=L);d=np.asarray(d,dtype=L);h=L(h);y=base+d
        if h<=0 or not np.isfinite(h) or np.min(y)<0:raise ValueError('stock domain')
        f,p,m,cp,cm=rates(d)
        mid,_,_=self.stage(base,d,h,f,cp,cm);Y=base+mid;dy=mid-d
        f1,p1,m1,cp1,cm1=rates(mid)
        i,j=self.i,self.j;pp=(p+p1)/2;mm=(m+m1)/2
        cp=np.divide(pp,Y[j],out=(cp+cp1)/2,where=Y[j]>0)
        cm=np.divide(mm,Y[i],out=(cm+cm1)/2,where=Y[i]>0)
        # Corrector evaluated about OLD stock. Resolve net as the stable
        # average flux minus explicitly tracked predictor increments.
        net=(f+f1)/2-cp*dy[j]+cm*dy[i]
        # On a zero-stock edge use the exact one-sided base product:
        # no cancellation of a newly produced donor against its predictor.
        z=(y[i]==0)|(y[j]==0)
        net[z]=cp[z]*y[j[z]]-cm[z]*y[i[z]]
        return self.stage(base,d,h,net,cp,cm)
class PhysicalRates:
    def __init__(self,sc,state):
        self.sc=StableScatter(sc,state);self.template=state.clone()
    def __call__(self,d):
        sc=self.sc;s=self.template.clone();s.dt=d
        da,df=sc.increments(s);f=sc.f0+df;y=s.nt+d
        a=sc.a0+da;n=sc.net.ncore
        lim=1/(sc.net.gt*sc.z)
        lim[:n]=sc.net.zi/(sc.net.gt[:n]*sc.net.zmean*sc.z[:n])
        ratio=np.divide(a,y,out=lim,where=y>0)
        i,j=sc.i,sc.j
        fac=sc.K*(1+f[i])*(1+f[j])*(s.neutral-s.n2-s.d2)/L(sc.net.q['n1s'])
        cp=fac*ratio[j];cm=fac*ratio[i]
        net=fac*((sc.a0[j]-sc.a0[i])+(da[j]-da[i]))
        z=(y[i]==0)|(y[j]==0);net[z]=cp[z]*y[j[z]]-cm[z]*y[i[z]]
        return net,cp*y[j],cm*y[i],cp,cm

class IncrementScatter:
    """Transactional adapter for C2R source/geometry split, same edge ledger."""
    def __init__(self,sc,state):
        # bath_at returns StableScatter, whose K and net may have been changed
        # after construction; retain the stage coefficients, not stale original.
        self.method=IncrementMPRK(sc.i,sc.j,len(state.nt));self.sc=sc
    def step(self,s,dt):
        old=s.dt.copy()
        d,f,g=self.method.advance(s.nt,old,dt,PhysicalRates(self.sc,s))
        delta=d-old;en=f@self.sc.de;scale=max(g,L('1e-4900'))
        n=float(abs(delta.sum())/scale);ee=float(abs(delta@self.sc.net.et-en)/(scale*self.sc.net.transition))
        if max(n,ee)>1e-11:raise ValueError('increment scattering ledger')
        s.dt=d
        return dict(gross=g,bath_energy_eV_m3=-en,cross_into_com=f[self.sc.cross].sum(),new_energy=f[self.sc.new]@self.sc.de[self.sc.new],number_relative=n,energy_relative=ee)

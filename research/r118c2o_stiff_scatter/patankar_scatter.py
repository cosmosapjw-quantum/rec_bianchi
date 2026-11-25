"""Conservative MPRK22(1), positive-stock domain, in longdouble increments.
Sparse binary64 solve + longdouble residual refinement; flux owns updates.
"""
import math
import numpy as np
from scipy.sparse import coo_matrix,eye
from scipy.sparse.linalg import splu
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L

class PatankarScatter:
    def __init__(self,sc):
        self.sc=sc;self.net=sc.net
        self.i,self.j,self.cross,self.new,self.de=sc.i,sc.j,sc.cross,sc.new,sc.de
    def div(self,flux,n):
        d=np.zeros(n,dtype=L);np.add.at(d,self.i,flux);np.add.at(d,self.j,-flux);return d
    def stage(self,y,den,den_increment,plus,minus,net,h):
        # positive plus: j -> i; positive minus: i -> j.
        # MPRK generator rates are divided by donor den; solve for delta
        # rather than forming a difference between large absolute stocks.
        i,j=self.i,self.j;n=len(y)
        if np.min(y)<=0 or np.min(den)<=0:raise ValueError("Patankar positive stock domain")
        # y/den-1 should not be formed by subtracting rounded ratios.
        corr=-den_increment/den
        base=net+plus*corr[j]-minus*corr[i]
        p=plus/den[j];m=minus/den[i]
        diag=np.arange(n)
        d=np.ones(n,dtype=L);np.add.at(d,i,h*m);np.add.at(d,j,h*p)
        # Similarity scale by old stock; solve for delta/y.
        data=np.asarray(np.r_[d,-h*p*y[j]/y[i],-h*m*y[i]/y[j]],float)
        if not np.all(np.isfinite(data)):raise ValueError("Patankar matrix finite")
        M=coo_matrix((data,(np.r_[diag,i,j],np.r_[diag,j,i])),shape=(n,n)).tocsc()
        lu=splu(M)
        def solve(rhs):
            return np.asarray(lu.solve(np.asarray(rhs/y,float)),dtype=L)*y
        rhs=h*self.div(base,n);delta=solve(rhs)
        def flux_of(delta):
            return h*(base+p*delta[j]-m*delta[i])
        for _ in range(3):
            flux=flux_of(delta);res=self.div(flux,n)-delta
            delta+=solve(res)
        flux=flux_of(delta);actual=self.div(flux,n)
        gross=h*np.sum(plus*(1+corr[j]+delta[j]/den[j])+minus*(1+corr[i]+delta[i]/den[i]))
        if not np.isfinite(gross) or gross<0:raise ValueError("Patankar gross")
        residual=np.max(abs(actual-delta))/max(gross,L('1e-4900'))
        if residual>1e-12:raise ValueError("Patankar linear residual")
        if not np.isfinite(actual).all() or np.min(y+actual)<=0:raise ValueError("Patankar numerical positivity")
        return actual,flux,gross,float(residual)
    def step(self,s,dt):
        if not math.isfinite(dt) or dt<=0:raise ValueError("dt")
        h=L(dt);y=s.nt+s.dt;old=s.dt.copy()
        f,g=self.sc.rates(s)
        if np.any(abs(f)>g) or np.min(g)<0:raise ValueError("Patankar rate domain")
        p=(g+f)/2;m=(g-f)/2
        dy,_,_,r1=self.stage(y,y,np.zeros_like(y),p,m,f,h)
        Y=s.clone();Y.dt=old+dy;ys=Y.nt+Y.dt
        f1,g1=self.sc.rates(Y)
        if np.any(abs(f1)>g1) or np.min(g1)<0:raise ValueError("Patankar stage rates")
        fbar=(f+f1)/2;gbar=(g+g1)/2
        plus=(gbar+fbar)/2;minus=(gbar-fbar)/2
        dy,flux,gross,r2=self.stage(y,ys,Y.dt-old,plus,minus,fbar,h)
        new=old+dy
        if np.min(s.nt+new)<=0:raise ValueError("Patankar state positivity")
        actual=new-old;de=flux@self.de;scale=max(gross,L('1e-4900'))
        r=dict(gross=float(gross),energy_eV_m3=float(de),bath_energy_eV_m3=float(-de),cross_into_com=float(np.sum(flux[self.cross])),new_energy=float(flux[self.new]@self.de[self.new]),number_relative=float(abs(np.sum(actual))/scale),energy_relative=float(abs(actual@self.net.et-de)/(scale*self.net.transition)),net_energy_relative=float(abs(actual@self.net.et-de)/max(abs(de),scale*L('1e-20'))),linear_residual=max(r1,r2))
        s.dt=new
        return r

"""Separate gross products and increment-resolved net reaction flux."""
import numpy as np
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L
def product_increment(x,y,z,dx,dy,dz):
    return dx*y*z+(x+dx)*dy*z+(x+dx)*(y+dy)*dz
class StableReaction:
    def __init__(self,net,state):
        self.net=net;self.nt=state.nt;self.nc=state.nc;self.n2=state.n2;self.neutral=state.neutral
        s=state.clone();s.dt[:]=0;s.dc[:]=0;s.d2=L(0)
        if hasattr(net,'point_t'):
            self.ft=np.array([net.point_t(i,v) for i,v in enumerate(s.nt)],dtype=L)
        else:self.ft=net.point_values(s)
        self.fc=s.nc/net.gc
        n=net.ncore
        if n:
            self.a0=self.ft[:n]/(net.zi*(1+self.ft[:n]))
            self.den=[1-a*z for a,z in zip(self.a0,net.z)]
            self.der=np.array([w@(z/d**2) for w,z,d in zip(net.w,net.z,self.den)],dtype=L)
    def __getattr__(self,k):return getattr(self.net,k)
    def point_increment(self,i,dstock):
        f=dstock/self.gt[i]
        if i>=self.ncore or f==0:return f
        w,z,d=self.w[i],self.z[i],self.den[i];da=f/self.der[i]
        for _ in range(12):
            dd=d-da*z
            if np.min(dd)<=0:raise ValueError('increment pole')
            res=da*(w@(z/(d*dd)))-f
            if abs(res)<=32*np.finfo(L).eps*abs(f):break
            da-=res/(w@(z/dd**2))
        dd=d-da*z
        if np.min(dd)<=0 or abs(da*(w@(z/(d*dd)))-f)>1e-12*abs(f):raise ValueError('increment inversion')
        v=1-self.a0[i]*self.zi[i]
        return da*self.zi[i]/(v*(v-da*self.zi[i]))
    def parts(self,s,event,delta=L(0)):
        i,j,sg,r,_=event
        if ((s.nt is not self.nt and not np.array_equal(s.nt,self.nt)) or (s.nc is not self.nc and not np.array_equal(s.nc,self.nc)) or s.n2!=self.n2 or s.neutral!=self.neutral):
            raise ValueError('reaction anchor mismatch')
        x=self.ft[i];y=self.fc[j];b=self.n2;nn=self.neutral-b
        dx=self.point_increment(i,s.dt[i]+delta);dy=(s.dc[j]+sg*delta)/self.gc[j];db=s.d2-delta
        if min(x+dx,y+dy,b+db,nn-db)<0:raise ValueError('reaction stock domain')
        ap=y+(sg==1);bp=y+(sg==-1)
        A0=r*b*(1+x)*ap;B0=r*nn*x*bp
        dA=r*product_increment(b,1+x,ap,db,dx,dy)
        dB=r*product_increment(nn,x,bp,-db,dx,dy)
        A=r*(b+db)*(1+x+dx)*(ap+dy);B=r*(nn-db)*(x+dx)*(bp+dy)
        return A0-B0,dA-dB,A,B
    def net_rates(self,s,event,delta=L(0)):
        f0,df,A,B=self.parts(s,event,delta)
        F=f0+df
        if not np.isfinite([F,A,B]).all() or min(A,B)<0:raise ValueError('reaction rates')
        return F,A+B,A,B

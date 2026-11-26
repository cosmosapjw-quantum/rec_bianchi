"""Physical-population line-pair closure, distinct from native proxy evolution."""
from pathlib import Path
import sys,numpy as np
from scipy.sparse import csr_matrix,lil_matrix,diags
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c3b_labelled_transport'))
from labelled import Owner,L
class LineOwner:
    # ledgers: out_N,out_U,work,in_N,in_U,scatter_heat,source_p,loss_p,line_heat,line_to_photons
    def __init__(self,o,bath,p0,cp,conductance,loss,n0):
        self.o=o;self.n=o.n;self.line_e=L('10.198714553953742')
        H,cap,k,inc=o.rates(bath);self.cap=cap;self.cp=L(cp);self.p0=L(p0);self.loss=L(loss)
        if min(cp,p0,conductance,loss)<=0:raise ValueError('line parameters')
        bottom=o.d.escape
        self.k=np.zeros(self.n,dtype=L);self.k[bottom]=L(conductance)*o.g[bottom]/o.g[bottom].sum()
        self.r=self.k/cap;self.s=self.k/self.cp;self.gamma=self.loss+self.s.sum()
        self.source=self.loss*self.p0+np.sum(self.s*self.p0-self.r*n0)
        if self.source<=0:raise ValueError('nonpositive line source')
        self.A0=o.matrix((0.,bath[1],bath[2],0.))
        self.A1=o.matrix((1.,bath[1],bath[2],0.))-self.A0
        self._mat={}
        for qss in (False,True):self._mat[qss]=self._build(qss)
    def qss(self,N):return (self.source+self.r@N)/self.gamma
    def _build(self,qss):
        n=self.n;m=n+(not qss);size=m+10
        a=lil_matrix((size,size));z=lil_matrix((size,size));b=np.zeros(size,dtype=L)
        a[:n,:n]=self.A0[:n];z[:n,:n]=self.A1[:n]
        a[m:m+6,:n]=self.A0[n:];z[m:m+6,:n]=self.A1[n:]
        c=np.asarray(self.r,float);s=np.asarray(self.s,float);de=np.asarray(self.line_e-self.o.e,float)
        if qss:
            p=np.asarray(self.r/self.gamma,float);const=self.source/self.gamma
            J=np.outer(s,p)-np.diag(c);jc=self.s*const
            a[:n,:n]+=csr_matrix(J);b[:n]+=jc
            a[m+7,:n]=self.loss*p;b[m+7]=self.loss*const
            a[m+8,:n]=de@J;b[m+8]=np.dot(de,jc)
            a[m+9,:n]=J.sum(axis=0);b[m+9]=jc.sum()
        else:
            a[:n,:n]-=diags(c);a[:n,n]=s[:,None]
            a[n,:n]=c;a[n,n]=-float(self.gamma);b[n]=self.source
            a[m+7,n]=float(self.loss)
            a[m+8,:n]=-de*c;a[m+8,n]=de@s
            a[m+9,:n]=-c;a[m+9,n]=s.sum()
        b[m+6]=self.source
        return a.tocsr(),z.tocsr(),b
    def affine(self,H,influx,qss):
        a,z,b=self._mat[qss];m=self.n+(not qss);v=b.copy();j=L(H)*L(influx)
        v[self.o.top]+=j*self.o.tw;v[m+3]+=j;v[m+4]+=j*self.o.e.max()
        return a+float(H)*z,v
    def ledger(self,d,qss):
        n=self.n;m=n+(not qss);x=d[:n];l=d[m:];p=L(0) if qss else d[n]
        if qss:
            N=x.sum()+l[0]-l[3]-l[9]
            U=x@self.o.e+l[1]+l[2]+l[5]+l[8]-l[4]-self.line_e*l[9]
        else:
            N=x.sum()+p+l[0]+l[7]-l[3]-l[6]
            U=x@self.o.e+self.line_e*p+l[1]+l[2]+l[5]+l[8]+self.line_e*(l[7]-l[6])-l[4]
        return float(abs(N)/max(np.sum(abs(x))+sum(abs(l)),L('1e-4900'))),float(abs(U)/max(np.sum(abs(x*self.o.e))+sum(abs(l))*10,L('1e-4900')))

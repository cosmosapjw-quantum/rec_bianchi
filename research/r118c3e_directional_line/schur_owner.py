"""Shared physical 2p pair with native exterior Schur affine source.
The exterior remains a prescribed reservoir; no external photon writeback.
"""
import sys
from pathlib import Path
import numpy as np
from scipy.sparse import lil_matrix,csr_matrix,diags
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c3d_two_sided'))
from two_line import TwoWing,Owner,L
class SchurWing(TwoWing):
 def __init__(self,red,blue,bath,p0,cp,conductances,loss,n0,q_at_n0,qvec):
    # Base geometry and pair construction. Avoid base virtual dispatch on _build.
    self.qvec=np.asarray(qvec,dtype=L)
    self.q0=L(q_at_n0)-self.qvec@np.asarray(n0,dtype=L)
    super().__init__(red,blue,bath,p0,cp,conductances,loss,n0)
    self.source=self.q0
    if q_at_n0<=0 or loss<=0 or not np.isfinite(self.qvec).all():raise ValueError('external source domain')
    self._mat={q:self._build(q) for q in (False,True)}
 def q(self,N):return self.q0+self.qvec@N
 def qss(self,N):
    if min(N)<0 or self.q(N)<0:raise ValueError('external source domain')
    return (self.q(N)+self.r@N)/self.gamma
 def _build(self,qss):
    n=self.n;m=n+(not qss);size=m+10
    a=lil_matrix((size,size));z=lil_matrix((size,size));b=np.zeros(size,dtype=L)
    a[:n,:n]=self.A0[:n];z[:n,:n]=self.A1[:n]
    a[m:m+6,:n]=self.A0[n:];z[m:m+6,:n]=self.A1[n:]
    c=np.asarray(self.r,float);s=np.asarray(self.s,float);q=np.asarray(self.qvec,float);de=np.asarray(self.line_e-self.o.e,float)
    if qss:
      p=(c+q)/float(self.gamma);const=self.q0/self.gamma;J=np.outer(s,p)-np.diag(c);jc=self.s*const
      a[:n,:n]+=csr_matrix(J);b[:n]+=jc
      a[m+7,:n]=self.loss*p;b[m+7]=self.loss*const
      a[m+8,:n]=de@J;b[m+8]=np.dot(de,jc)
      a[m+9,:n]=J.sum(axis=0);b[m+9]=jc.sum()
    else:
      a[:n,:n]-=diags(c);a[:n,n]=s[:,None];a[n,:n]=c+q;a[n,n]=-float(self.gamma);b[n]=self.q0
      a[m+7,n]=float(self.loss);a[m+8,:n]=-de*c;a[m+8,n]=de@s;a[m+9,:n]=-c;a[m+9,n]=s.sum()
    a[m+6,:n]=q;b[m+6]=self.q0
    return a.tocsr(),z.tocsr(),b

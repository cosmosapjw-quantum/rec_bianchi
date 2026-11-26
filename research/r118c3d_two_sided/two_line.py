"""Two disjoint labelled wing transport blocks, one physical real 2p."""
import sys
from pathlib import Path
import numpy as np
from scipy.sparse import block_diag,vstack,hstack,csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c3c_line_face'))
from line_face import LineOwner,Owner,L
class TwoWing(LineOwner):
 def __init__(self,red,blue,bath,p0,cp,conductances,loss,n0):
    self.red=red;self.blue=blue;self.n=red.n+blue.n;self.line_e=L("10.198714553953742")
    class Registry: pass
    self.o=Registry();self.o.e=np.r_[red.e,blue.e];self.o.g=np.r_[red.g,blue.g]
    self.cp=L(cp);self.p0=L(p0);self.loss=L(loss);self.k=np.zeros(self.n,dtype=L)
    if min(cp,p0,loss)<=0 or min(conductances)<0:raise ValueError("line parameters")
    R=red.top;B=blue.d.escape+red.n
    for ix,k in zip((R,B),conductances):self.k[ix]=L(k)*self.o.g[ix]/self.o.g[ix].sum()
    cap=np.r_[red.rates((*bath[:3],0.))[1],blue.rates((*bath[:3],0.))[1]];self.cap=cap;self.r=self.k/cap;self.s=self.k/self.cp;self.gamma=self.loss+self.s.sum()
    self.source=self.loss*self.p0+np.sum(self.s*self.p0-self.r*n0)
    if self.source<=0:raise ValueError("line source")
    def mat(H):
      x=red.matrix((H,bath[1],bath[2],0.));y=blue.matrix((H,bath[1],bath[2],0.))
      return vstack([block_diag([x[:red.n],y[:blue.n]],format='csr'),hstack([x[red.n:],y[blue.n:]],format='csr')],format='csr')
    self.A0=mat(0.);self.A1=mat(1.)-self.A0;self._mat={q:self._build(q) for q in (False,True)}
 def affine(self,H,influx,qss):
    if not np.isfinite(H) or H<0 or min(influx)<0 or not np.isfinite(influx).all():raise ValueError("boundary")
    A,Z,b=self._mat[qss];m=self.n+(not qss);v=b.copy()
    for off,o,I in ((0,self.red,influx[0]),(self.red.n,self.blue,influx[1])):
      j=L(H)*L(I);v[off+o.top]+=j*o.tw;v[m+3]+=j;v[m+4]+=j*o.e.max()
    return A+float(H)*Z,v

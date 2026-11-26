import numpy as np
from schur_owner import SchurWing,Owner,L
def test_state_dependent_source_ledger():
 r=Owner(np.array([10.1,10.19]),np.array([2.,3.]),np.array([0]),np.array([1]),np.array([.2]))
 b=Owner(np.array([10.21,10.3]),np.array([2.,3.]),np.array([0]),np.array([1]),np.array([.2]))
 base=np.ones(4,dtype=L)
 q=SchurWing(r,b,(0.,.25,1.,0.),1.,3.,[2.,3.],4.,base,2.,np.array([.1,.2,.3,.4]))
 p=q.qss(base);A,v=q.affine(0.,(0.,0.),False);x=np.r_[base,p,np.zeros(10)]
 z=A@x+v;assert abs(z[4])<1e-13
 assert abs(z[11]-q.q(base))<1e-13
 assert abs(z[:5].sum()+z[5]+z[12]-z[8]-z[11])<1e-13

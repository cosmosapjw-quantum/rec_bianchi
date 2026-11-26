import numpy as np
from two_line import TwoWing,L
def test_two_side_shared_population():
 from labelled import Owner
 r=Owner(np.array([10.1,10.19]),np.array([2.,3.]),np.array([0]),np.array([1]),np.array([.2]))
 b=Owner(np.array([10.21,10.3]),np.array([2.,3.]),np.array([0]),np.array([1]),np.array([.2]))
 o=TwoWing(r,b,(0.,.25,1.,0.),1.,3.,[2.,3.],4.,np.ones(4,dtype=L))
 A,q=o.affine(0.,(0.,0.),False);x=np.r_[np.ones(4),1.,np.zeros(10)]
 z=A@x+q;assert abs(z[4])<1e-13
 N=z[:4].sum()+z[4]+z[5]+z[12]-z[8]-z[11]
 assert abs(N)<1e-13
 assert o.k[1]>0 and o.k[2]>0 and o.k[0]==o.k[3]==0

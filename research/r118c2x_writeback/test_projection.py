import numpy as np
from writeback import LinearProject,L
def test_conservative_project():
 p=LinearProject(np.array([1.,2.,3.]),np.array([1.3,2.7]))
 y=np.array([L('1e-20'),-L('1e-20')])
 x=p.deposit(y)
 assert abs(x.sum())<L('1e-38')
 assert abs(x@p.coarse-y@p.fine)<L('1e-35')
 assert np.all(p.lift(np.ones(3))==1)

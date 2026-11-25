import numpy as np
from drift import Redshift
def test_conservative_zero_and_duplicate_nodes():
 e=np.array([1.,2.,2.,4.],np.longdouble);g=np.array([1.,1.,2.,1.],np.longdouble);n=np.array([0.,0.,0.,1.],np.longdouble)
 d=Redshift(e,g)
 v,l=d.advance(n,.01)
 assert np.min(v)>=0 and abs(v.sum()+l['escape_N']-1)<1e-15
 assert abs(v@e+l['escape_U']+l['work']-4)<1e-15
 assert v[2]>v[1]>0 and abs(v[2]/v[1]-2)<1e-15

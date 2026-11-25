import numpy as np
from zero_scatter import ZeroMPRK
L=np.longdouble
def test_zero_chain():
 i=np.array([0,1]);j=np.array([1,2]);s=ZeroMPRK(i,j,3)
 def rates(y):return np.ones(2,dtype=L),np.ones(2,dtype=L)
 y=np.array([1.,0.,0.],dtype=L)
 v,f,g=s.advance(y,.1,rates)
 assert np.min(v)>0 and abs(v.sum()-1)<1e-15
 assert abs(np.sum(s.div(f)))<1e-18 and g>0
 y=np.zeros(3,dtype=L);v,f,g=s.advance(y,100,rates)
 assert np.array_equal(v,y) and g==0

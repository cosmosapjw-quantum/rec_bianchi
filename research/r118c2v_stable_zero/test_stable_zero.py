import numpy as np
from stable_zero import IncrementMPRK,L
def test_zero_and_sub_ulp():
 m=IncrementMPRK([0],[1],2)
 def rate(d):
  y=np.array([1.,1.],dtype=L)+d
  # exact net resolved from increments, not reconstructed stocks
  return d[1]-d[0],y[1],y[0],np.ones(1,dtype=L),np.ones(1,dtype=L)
 d=np.array([L('1e-25'),0],dtype=L);old=d.copy()
 # rate callback returns arrays
 def r(x):
  f,p,q,cp,cm=rate(x);return np.atleast_1d(f),np.atleast_1d(p),np.atleast_1d(q),cp,cm
 d,f,g=m.advance(np.ones(2,dtype=L),d,.1,r)
 assert d[0]<old[0] and d[1]>0 and abs(d.sum()-old.sum())<L('1e-42')
 base=np.array([1.,0.],dtype=L)
 def z(x):
  y=base+x;return np.array([y[1]-y[0]]),np.array([y[1]]),np.array([y[0]]),np.ones(1,dtype=L),np.ones(1,dtype=L)
 d,f,g=m.advance(base,np.zeros(2,dtype=L),.1,z)
 assert np.all(base+d>0) and abs(d.sum())<L('1e-18')

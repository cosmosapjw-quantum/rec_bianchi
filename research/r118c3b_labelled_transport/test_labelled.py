import numpy as np
from labelled import Owner
def test_labelled_open_ledger():
 e=np.array([1.,2.,2.,3.]);g=np.array([1.,1.,3.,1.]);i=np.array([0,1,2]);j=np.array([1,3,3]);K=np.array([.1,.2,.3])
 o=Owner(e,g,i,j,K)
 N=np.array([1.,2.,2.,1.])
 d=o.midpoint(N,0.,1.,lambda t:(.01,1.,1.,.2))
 assert np.min(N+d[:4])>0
 assert abs(d[:4].sum()+d[4]-d[7])<1e-12
 assert abs(d[:4]@e+d[5]+d[6]+d[9]-d[8])<1e-12
 assert len(o.e)==4

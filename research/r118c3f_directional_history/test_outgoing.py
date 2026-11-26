import numpy as np
from canonical_history import raymap, reconstruct
def test_registry():
 n=np.eye(3);d,w=raymap(np.eye(3),np.eye(3),n,np.ones(3)/3)
 assert np.array_equal(n,d) and np.array_equal(w,np.ones(3)/3)
def test_outgoing_constant_source():
 # transparent and thick bins; the angular mean reconstructs virtual state
 tau=np.array([[.2,2.],[.4,4.]])
 f=np.array([[.1,.2],[.15,.3]])
 x1=.8;source=np.array([.4,.5]);w=np.array([.3,.7])
 from full_bianchi_hyrec.trajectory.full_2012_atomic_source import accurate_escape_factors
 pi,tr=accurate_escape_factors(tau)
 v,out=reconstruct(f,pi,tr,source,x1)
 assert np.allclose(v,x1*((1-pi)*f+pi*source))
 assert np.allclose(out,f+(source-f)*tr)

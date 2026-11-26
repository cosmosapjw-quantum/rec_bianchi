import unittest,numpy as np
from scipy.interpolate import PchipInterpolator
from paired_interp import sample,pair_residual
from lya_crossing import crossing,EL
class T(unittest.TestCase):
 def test_interpolator(self):
  he=np.arange(10.)*.1;y=np.exp(he);h=np.broadcast_to(y[:,None,None],(10,2,2));t=np.array([[.23,.31],[.42,.56]]);s=np.array([0,1])
  np.testing.assert_allclose(sample(he,h,t,s,'pchip',10),PchipInterpolator(he,y)(t),rtol=0,atol=1e-14)
 def test_join(self):
  he=np.arange(10.);h=np.broadcast_to(np.exp(he)[:,None,None],(10,2,2));t=np.array([[3.2,4.3],[3.6,4.7]]);s=np.array([0,1])
  np.testing.assert_array_equal(sample(he,h,t,s,'pchip',5),sample(he,h,t,s,'linear',5))
 def test_crossing(self):
  n,u,a,b,w=crossing(np.array([EL,EL*1.1]),np.array([1.]),EL,EL*1.01,1.,1.,.3)
  self.assertAlmostEqual((a+b)/n,1.);self.assertAlmostEqual((EL*(a+b)+w)/u,1.);self.assertGreater(w,0.)
 def test_invalid(self):
  with self.assertRaises(ValueError):crossing(np.array([1.,2.]),np.array([-1.]),1.,2.,1.,1.,.1)
if __name__=='__main__':unittest.main()

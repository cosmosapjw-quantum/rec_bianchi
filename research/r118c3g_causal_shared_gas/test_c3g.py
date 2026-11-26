import unittest,numpy as np
from canonical_stock import transfer
from shared_gas import thermal_endpoint
class SharedGasTest(unittest.TestCase):
 def test_thermal_residual(self):
  for method in ('trap','be'):
   T=2996.;A=1e6;Tr=2996.3;g=-2500.;h=1e-5
   t=thermal_endpoint(T,g,A,Tr,h,method);new=A*(Tr-t)-2*t
   self.assertLess(abs(t-T-h*(.5*(g+new) if method=='trap' else new)),1e-10)
 def test_identity(self):
  e=np.geomspace(.1,4,129);f=np.arange(1.,129.);a,l=transfer(e,f,e)
  np.testing.assert_allclose(a,f*np.diff(e**3)/3,rtol=1e-13);np.testing.assert_allclose(l,0)
 def test_shift(self):
  e=np.geomspace(.1,4,129);f=np.exp(-e[:-1])
  for k in (.9,1.1):
   a,l=transfer(e,f,k*e)
   self.assertGreaterEqual(min(a),0);self.assertGreaterEqual(min(l),0)
   self.assertAlmostEqual(a.sum()+l.sum(),f@np.diff(e**3)/3,places=12)
 def test_invalid(self):
  with self.assertRaises(ValueError):transfer([1,2],[-1],[1,2])
if __name__=='__main__':unittest.main()

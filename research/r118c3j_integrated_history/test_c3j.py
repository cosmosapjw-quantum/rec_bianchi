import unittest,numpy as np
from integral import check,average,primitive
from line_cell import evolve,phase,EL,A21
class T(unittest.TestCase):
 def test_primitive(self):self.assertEqual(check(),1.8125)
 def test_causal(self):
  h=np.array([0.,1.]);v=np.ones((2,1,1))
  with self.assertRaises(ValueError):primitive(h,v,v,np.array([[1.]]),np.array([0]))
 def test_line(self):
  p,n=.01,.005;X=.8;C=.3
  a,b,d,r=evolve(p,n,X,C,1e-9)
  self.assertAlmostEqual(a+b,p+n,places=15);self.assertGreaterEqual(a,0);self.assertGreaterEqual(b,0)
  aa,bb,_,_=evolve(a,b,X,C,1e-9);c,e,_,_=evolve(p,n,X,C,2e-9)
  np.testing.assert_allclose([aa,bb],[c,e],rtol=1e-12,atol=1e-16)
 def test_equilibrium(self):
  x1=.8;z=.1;C=2.;p=3*x1*np.exp(-1/z);n=C/np.expm1(1/z)
  a,b,d,r=evolve(p,n,x1+p,C,1e-3)
  self.assertLess(abs(d),1e-17)
if __name__=='__main__':unittest.main()

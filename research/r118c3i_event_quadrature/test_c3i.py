import unittest,numpy as np
from events import event_times,jump_weight,correction
from line_pair import line_pair,EL
class T(unittest.TestCase):
 def test_event(self):
  ge=np.linspace(0,1,11);F=np.broadcast_to(np.eye(3),(len(ge),3,3));n=np.eye(3);e=event_times(ge,F,np.eye(3),n,.1,np.array([.2,.5]),.2,.8)
  np.testing.assert_allclose(e,np.broadcast_to([.3,.6],(3,2)),rtol=0,atol=1e-13)
 def test_jump(self):
  a=np.array([[.1,.25,.75,1.,np.inf]])
  w=jump_weight(a,0.,1.)
  np.testing.assert_allclose(w,[[.4,.25,-.25,-.5,0]])
  self.assertAlmostEqual(.5+correction(np.array([[.25]]),0,1,np.array([1.]))[0,0],.75)
 def test_balance(self):
  p=line_pair(.8,0.,.3,5e-14,100.,np.ones(2),np.zeros(2),np.array([.5,.5]))
  self.assertEqual(p[2],0.);self.assertEqual(p[3],0.);self.assertLess(abs(p[0]-p[1]),1e-24)
 def test_wien(self):
  p=line_pair(.8,1e-15,.25,5e-14,100.,np.array([.9,1.1]),np.array([1e-16,2e-16]),np.array([.5,.5]))
  self.assertLess(abs(p[2]/p[3]-1),1e-12)
if __name__=='__main__':unittest.main()

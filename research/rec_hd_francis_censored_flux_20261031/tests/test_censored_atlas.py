import csv,math,sys,unittest
from pathlib import Path
import numpy as np
from scipy.special import ndtr
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from censored_atlas import get_positions,observed_data,score_and_grad,profile,SELECTED_T_PAIRS
ROOT=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
 def test_source_counts(self):
  p,c=get_positions(ROOT/'inputs/francis_zenodo_v1_final_F1_F2_364.csv');self.assertEqual(len(p),26)
 def test_upper_at_zero(self):
  dat=(np.array([],int),np.array([]),np.array([]),np.array([0]),np.array([.3]))
  val,g=score_and_grad([0.],np.array([[1.,0.,0.,0.,0.,0.]]),dat)
  self.assertAlmostEqual(val,-2*math.log(ndtr(3)),12)
  self.assertGreater(g[0],0)
 def test_zero_only_profile_boundary(self):
  dat=(np.array([],int),np.array([]),np.array([]),np.array([0,1]),np.array([.3,.5]))
  v,a,ok=profile(np.array([[1.,2.,3.,4.,5.,6.]]),dat)
  self.assertTrue(ok);self.assertEqual(a[0],0.)
 def test_two_zero_boundary(self):
  dat=(np.array([],int),np.array([]),np.array([]),np.array([0,1]),np.array([.3,.5]))
  _,a,ok=profile(np.array([[1.,2.,3.,4.,5.,6.],[5.,2.,1.,1.,1.,1.]]),dat)
  self.assertTrue(ok);self.assertTrue(np.all(a==0))
 def test_gaussian_detection(self):
  dat=(np.array([0]),np.array([2.]),np.array([.1]),np.array([],int),np.array([]))
  val,a,ok=profile(np.array([[1.,2.,3.,4.,5.,6.]]),dat)
  self.assertTrue(ok);self.assertLess(val,1e-12);self.assertAlmostEqual(a[0],12.,6)
 def test_derivative_finite_difference(self):
  dat=(np.array([0,1]),np.array([1.,.8]),np.array([.1,.2]),np.array([2]),np.array([.5]))
  q=np.array([[1.,.7,.6,0.,0.,0.],[.6,.7,.2,0.,0.,0.]])
  x=np.array([.3,.4]);v,g=score_and_grad(x,q,dat)
  for j in (0,1):
   d=np.zeros(2);d[j]=1e-6
   fd=(score_and_grad(x+d,q,dat)[0]-score_and_grad(x-d,q,dat)[0])/2e-6
   self.assertAlmostEqual(fd,g[j],places=5)
 def test_upper_penalty_monotone(self):
  dat=(np.array([],int),np.array([]),np.array([]),np.array([0]),np.array([.3]))
  q=np.array([[1.,0.,0.,0.,0.,0.]])
  self.assertLess(score_and_grad([0],q,dat)[0],score_and_grad([.5],q,dat)[0])
 def test_temperature_pairs(self):
  self.assertEqual(len(SELECTED_T_PAIRS),6)
 def test_negative_component_rejected(self):
  dat=(np.array([0]),np.array([.2]),np.array([.1]),np.array([],int),np.array([]))
  with self.assertRaises(ValueError):profile(np.array([[-1.,1.,1.,1.,1.,1.]]),dat)
 def test_rounded_error_remains_excluded(self):
  p,c=get_positions(ROOT/'inputs/francis_zenodo_v1_final_F1_F2_364.csv')
  x=next(x for x in p.values() if any(y[1]=='detected_rounded_error_zero' for y in x))
  dat=observed_data(x,.06)
  self.assertEqual(len(dat[0])+len(dat[3])+sum(z[1]=='detected_rounded_error_zero' for z in x),6)
 def test_two_comp_optimal_over_boundary(self):
  dat=(np.array([0,1,2]),np.array([.1,.5,.2]),np.array([.1,.1,.1]),np.array([3]),np.array([.3]))
  q=np.array([[.4,1,.2,.6,.1,.1],[1.,.2,.6,.1,.1,.1]])
  v,a,ok=profile(q,dat)
  self.assertTrue(ok);self.assertTrue(np.all(a>=0))
  self.assertLessEqual(v,profile(q[:1],dat)[0]+1e-8)
  self.assertLessEqual(v,profile(q[1:],dat)[0]+1e-8)
 def test_invalid_count_trapped(self):
  with self.assertRaises(FileNotFoundError):get_positions(ROOT/'inputs/not_here.csv')
if __name__=='__main__':unittest.main()

import unittest,json
from pathlib import Path
import numpy as np
from thomson_tetrad import tetrad_grid,physical_weights,project_q_mass,physical_collision
from thomson_l4 import operators,quadrupole
B=Path(__file__).parent
class PhysicalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.q=np.loadtxt(B/'rec199/source_inputs/F08_ORIGINAL_SOURCE_Q128.csv',delimiter=',',skiprows=1)[:,1:];cls.H=np.array([1.01e-14,.99e-14,1e-14])
 def test_source_is_continuum_and_Killing(self):
  d=json.loads((B/'rec199/source_inputs/science_scenario_v1.json').read_text())
  self.assertIn('ISOTROPIC_CONTINUUM_MEASURE',d['initial_state']['photon_angular_distribution'])
  self.assertIn('conserved',d['source']['birth_rule'])
 def test_map_jacobian_independent_differential(self):
  q=self.q;H=self.H;t=1e11;A=np.diag(np.exp(-H*t));n,J=tetrad_grid(q,H,t)
  phi=np.column_stack((-q[:,1],q[:,0],np.zeros(128)));phi/=np.linalg.norm(phi,axis=1)[:,None];theta=np.cross(phi,q)
  for i in (0,18,59,89,123):
   g=np.linalg.norm(A@q[i]);der=A/g-np.outer(A@q[i],q[i]@A@A)/g**3
   area=np.linalg.norm(np.cross(der@theta[i],der@phi[i]));self.assertAlmostEqual(area/J[i],1,places=14)
 def test_zero_shear_geometry(self):
  n,J=tetrad_grid(self.q,[1e-14]*3,1e11)
  self.assertLess(np.max(abs(n-self.q)),5e-16);self.assertLess(np.max(abs(J-1)),9e-16)
 def test_physical_l2_field_exact(self):
  n,J=tetrad_grid(self.q,self.H,1e11);w=physical_weights(self.q,n,J)
  S=np.array([[.11,.03,-.02],[.03,-.07,.01],[-.02,.01,-.04]])
  I=1+np.einsum('ia,ab,ib->i',n,S,n);native=I*J/128
  m=project_q_mass(native,J,w,'q_midpoint_continuum')
  moment=np.einsum('i,ia,ib->ab',m,n,n)/m.sum()-np.eye(3)/3
  self.assertLess(np.max(abs(moment-2*S/15)),5e-16)
 def test_isotropic_physical_source_null(self):
  n,J=tetrad_grid(self.q,self.H,1e11)
  out=physical_collision(self.q,self.H,1e11,J/128,1e-9,'q_midpoint_continuum')
  self.assertLess(np.max(np.hypot(out['Q'],out['U'])),1e-24)
  self.assertLess(np.max(abs(out['delta'])),1e-24)
 def test_first_order_shear_of_initial_isotropic_mass(self):
  t=1e9;n,J=tetrad_grid(self.q,self.H,t);w=physical_weights(self.q,n,J)
  m=project_q_mass(np.ones(128)/128,J,w,'q_midpoint_continuum')
  Q=np.einsum('i,ia,ib->ab',m,n,n)/m.sum()-np.eye(3)/3
  expected=np.diag(-2/5*t*(self.H-self.H.mean()))
  self.assertLess(np.max(abs(Q-expected)),5e-14)
 def test_stochastic_ledger_and_positive_Stokes(self):
  n,J=tetrad_grid(self.q,self.H,1e11);w=physical_weights(self.q,n,J);K,_,_=operators(n,w)
  self.assertLess(np.max(abs(K.sum(axis=0)-1)),6e-15);self.assertGreater(K.min(),0)
  out=physical_collision(self.q,self.H,1e11,J*(1+.1*n[:,0]**2)/128,1e-9,'q_midpoint_continuum')
  self.assertLess(abs(out['delta'].sum()),1e-23);self.assertLess(np.max(np.hypot(out['Q'],out['U'])-out['scattered_in']),0)
 def test_no_implicit_beam_reinterpretation(self):
  with self.assertRaises(ValueError):physical_collision(self.q,self.H,1e11,np.ones(128),1e-9,'discrete_beams')
 def test_real_final_source_gate(self):
  r=json.loads((B/'results_tetrad/RESULT.json').read_text());self.assertEqual(r['new_l4_same_3pct_gate'],'PASS_SCOPED');self.assertEqual(r['native_IVP_reexecutions'],0)
  self.assertLess(r['model_summaries']['S0_BI_ORIGINAL_HAT_photons_per_H']['max_l4_vs_l6_relative'],.03)
if __name__=='__main__':unittest.main(verbosity=2)

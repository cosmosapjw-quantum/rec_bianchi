import unittest,sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hd_cmb15 import solve_cmb,planck_number,TCMB0_K
from test_parent_reference import SAMPLE
from pr169_neufeld15_reference import parse_lamda,solve as vacuum_solve,SI_CONVERSION,H,K_B,C
class TestCMB15(unittest.TestCase):
 def setUp(self):self.model=parse_lamda(SAMPLE)
 def test_detailed_balance_cmb(self):
  for T in (100.,200.):
   # With equal background and gas, each edge must be in the unique LTE state.
   z=T/TCMB0_K-1
   r=solve_cmb(self.model,T,1.e4,z)
   # Published 2011/2026 rounded line frequency differs from level-energy gap.
   # Compare against the source-justified first-order spectral inconsistency bound.
   df=abs(100*C*89.227931612-2.674986094e12)
   bound=10*5.442038e-8*H*2.674986094e12*(H*df/(K_B*T))
   self.assertLess(abs(r['net_cooling_W_per_HD']),bound)
   expected=3*math.exp(-H*2.674986094e12/(K_B*T))
   self.assertLess(abs(r['populations_J0_to_J14'][1]/r['populations_J0_to_J14'][0]-expected), 10*H*df/(K_B*T))
 def test_cmb_signs(self):
  for T in (100.,200.):
   for z in (0.,10.,30.,50.,73.,100.):
    r=solve_cmb(self.model,T,1.e4,z)
    self.assertEqual(math.copysign(1,r['net_cooling_W_per_HD']),math.copysign(1,T-r['Tbg_K']))
 def test_positive_normalized(self):
  for n in (100.,1e4,1e8):
   for z in (0,20,100):
    x=solve_cmb(self.model,100,n,z)
    self.assertTrue(all(t>=0 for t in x['populations_J0_to_J14']))
    self.assertAlmostEqual(x['sum_pop'],1,places=13)
    self.assertLess(x['max_stationary_residual_s_inverse'],1e-16)
 def test_vacuum_parent(self):
  x=solve_cmb(self.model,100.,1e4,0,background=False)
  old=vacuum_solve(self.model,100.,1e4)
  for p,q in zip(x['populations_J0_to_J14'],old['populations']):self.assertAlmostEqual(p,q,places=13)
  self.assertAlmostEqual(x['net_cooling_W_per_HD'],old['total_spontaneous_power_W_per_HD'],delta=1e-40)
 def test_twolevel_analytic(self):
  T=100;n=1e4;z=50
  x=solve_cmb(self.model,T,n,z); nb=planck_number(2.674986094e12,TCMB0_K*(1+z))
  q=(2.303e-11+3*2.3127e-11)/4
  Cdn=n*q; Cup=Cdn*3*math.exp(-SI_CONVERSION*89.227931612/T)
  Adn=5.442038e-8*(1+nb); Aup=3*5.442038e-8*nb
  expected=(Cup+Aup)/(Cup+Aup+Cdn+Adn)
  self.assertAlmostEqual(x['populations_J0_to_J14'][1],expected,places=13)
 def test_integrated_line_budget(self):
  x=solve_cmb(self.model,100,1e4,50)
  self.assertAlmostEqual(x['net_cooling_W_per_HD'],sum(i['net_W_per_HD'] for i in x['line_power_records']),delta=1e-45)
 def test_guard_no_interpolation(self):
  with self.assertRaises(ValueError):solve_cmb(self.model,150,1e4,3)
 def test_invalid_z(self):
  with self.assertRaises(ValueError):solve_cmb(self.model,100,1e4,-1)
 def test_naive_no_cmb_not_equivalent(self):
  x=solve_cmb(self.model,100,1e4,100)
  y=solve_cmb(self.model,100,1e4,100,background=False)
  self.assertLess(x['net_cooling_W_per_HD'],0)
  self.assertGreater(y['net_cooling_W_per_HD'],0)
 def test_high_density_lte(self):
  x=solve_cmb(self.model,100,1e14,50)
  b=3*math.exp(-SI_CONVERSION*89.227931612/100)
  self.assertAlmostEqual(x['populations_J0_to_J14'][1]/x['populations_J0_to_J14'][0],b,places=7)
if __name__=='__main__':unittest.main()

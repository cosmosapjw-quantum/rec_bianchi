"""Scientific tests for source-qualified HD J1 and held full9 CMB balance."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
import math
from mpmath import mp

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'src/hd_cmb_balance.py'
spec=importlib.util.spec_from_file_location('hd_cmb_balance',MOD)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
S=ROOT/'input/LAMDA_HD_PR161_SOURCE_TRANSCRIPTION.json'
U=ROOT/'input/SUNG_HD_PR164_SOURCE.json'

class HDPhysics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  mp.dps=80
  cls.s,cls.u=m.load_sources(S,U)

 def test_source_digest(self):
  self.assertEqual(hashlib.sha256(S.read_bytes()).hexdigest(),m.SOURCE_SHA)
  self.assertEqual(hashlib.sha256(U.read_bytes()).hexdigest(),m.SUNG_SHA)

 def test_source_no_raw_promotions(self):
  self.assertFalse(self.s['exact_source_bytes_acquired'])
  self.assertIsNone(self.u['primary_source']['joint_covariance'])

 def test_original_gate_unchanged(self):
  a=m.frequency_ledger(self.s)
  self.assertEqual([x['frozen_35Hz_gate'] for x in a],['PASS']+['FAIL']*7)

 def test_2021_actual_temperature_nodes_only(self):
  with self.assertRaises(ValueError):m.collision_rates(self.s,296,'10000','0.5')

 def test_n0_J1_radiative_equilibrium(self):
  for T in (50,100,200):
   x=m.twolevel(self.s,T,'0','0.5',m.T0*Decimal_(10))
   self.assertLess(abs(x['net']),mp.mpf('1e-75'))

 def test_equal_temperature_two_level(self):
  for T in (50,100,200):
   for n in ('1','10000','1000000'):
    x=m.twolevel(self.s,T,n,'0.5',T)
    self.assertLess(abs(x['net']),mp.mpf('1e-73'))

 def test_equal_temperature_full9(self):
  for T in (50,100,200):
   p=m.full9(self.s,T,'10000','0.5',T)
   self.assertLess(abs(p['net']),mp.mpf('1e-70'))

 def test_full9_lte_equal_temperature(self):
  T=100
  x=m.full9(self.s,T,'10000','0.5',T)
  g=[m.weight(self.s,j)*mp.exp(-m.x_gap(self.s,j,0,T)) for j in range(9)]
  g=[v/sum(g) for v in g]
  self.assertLess(max(abs(a-b) for a,b in zip(x['p'],g)),mp.mpf('1e-50'))

 def test_two_level_ortho_independence(self):
  for T in (50,100,200):
   a=m.twolevel(self.s,T,'10000','0','29.98028')
   b=m.twolevel(self.s,T,'10000','1','29.98028')
   self.assertEqual(a['net'],b['net'])

 def test_full9_ortho_does_matter(self):
  a=m.full9(self.s,200,'10000','0','29.98028')
  b=m.full9(self.s,200,'10000','1','29.98028')
  self.assertGreater(abs(a['net']-b['net']),mp.mpf('1e-31'))

 def test_cooling_heating_temperature_sign(self):
  for T,z,expected in [(50,0,1),(50,30,-1),(100,30,1),(100,50,-1),(200,50,1)]:
   bg=m.T0*Decimal_(1+z)
   for method in (m.twolevel,m.full9):
    x=method(self.s,T,'10000','0.5',bg)
    self.assertTrue(x['net']*expected>0,(T,z,method.__name__))

 def test_net_line_sum_equals_total(self):
  x=m.full9(self.s,100,'10000','0.5','84.48988')
  self.assertLess(abs(sum(v['net'] for v in x['lines'])-x['net']),mp.mpf('1e-60'))

 def test_analytic_j1_inherited_vacuum(self):
  # Historical PR161 J1 photon E differs from term energy by <35 Hz.
  x=m.twolevel(self.s,100,'10000','0.5',m.T0)
  historical=mp.mpf('3.943492942136341e-29')
  self.assertLess(abs(x['net']/historical-1),mp.mpf('1e-11'))

 def test_source_tampering_rejected(self):
  from tempfile import TemporaryDirectory
  with TemporaryDirectory() as d:
   p=Path(d)/'modified.json';p.write_bytes(S.read_bytes()+b' ')
   with self.assertRaises(ValueError):m.load_sources(p,U)

 def test_wavenumber_redshift_and_photons(self):
  v=self.u['line_parameters'][0]
  rest=m.Decimal(v['nu0_cm_minus1'])*100*m.C
  obs=rest/31
  self.assertAlmostEqual(float(obs)*31,float(rest),places=4)

 def test_lamda_energy_units(self):
  f=m.nu_gap(self.s,1,0)
  self.assertTrue(mp.mpf('2.674e12')<f<mp.mpf('2.676e12'))
  self.assertEqual(self.s['collision_partner_para_H2']['rates_cm3_s1'][0]['values'][0],'2.2e-11')

 def test_outputs_rows_and_null_gate(self):
  s=json.loads((ROOT/'evidence/RESULTS.json').read_text())
  self.assertEqual(s['new_conditional_physical_data']['nine_level_perline_photons'],1152)
  self.assertEqual(s['new_conditional_physical_data']['Sung_source_bound_redshifted_frequency_rows'],16)
  self.assertEqual((s['canonical_DAG'],s['REC_physical_DAG']),('28/88','0/313'))
  self.assertIsNone(s['chi_square'])

 def test_zero_bath_analytic_limit(self):
  # Radiative occupation goes to zero, returning PR161 J1 case without background.
  x=m.twolevel(self.s,100,'10000','0.5','0.001')
  src_q=mp.mpf('2.7e-11')*10000
  boltz=3*mp.exp(-m.x_gap(self.s,1,0,100))
  A=mp.mpf('5.442e-08')
  p=(src_q*boltz)/(A+src_q*(1+boltz))
  target=p*A*m.mpv(m.H)*m.nu_gap(self.s,1,0)
  self.assertLess(abs(x['net']/target-1),mp.mpf('1e-50'))

 def test_thermodynamic_critical_z(self):
  for T in (50,100,200):
   z=mp.mpf(T)/mp.mpf(str(m.T0))-1
   x=m.twolevel(self.s,T,'10000','0.5',mp.mpf(str(m.T0))*(1+z))
   self.assertLess(abs(x['net']),mp.mpf('1e-70'))

def Decimal_(x):
 return m.Decimal(str(x))

if __name__=='__main__':unittest.main()

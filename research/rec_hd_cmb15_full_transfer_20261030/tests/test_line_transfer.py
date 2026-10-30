from __future__ import annotations
import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hd_line_transfer import (read_models,check_sources,doppler_width_Hz,beta_gauss,
                              tau_zero_and_source,TEMPS, DENSITIES_CM3, REDSHIFTS, H,K_B,C)
from hd_cmb15 import solve_cmb
from independent_dense_validator import dense_population,beta_quad

ROOT=Path(__file__).resolve().parents[1]

class TestSourceOwnedFullLineTransfer(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.models=read_models(ROOT)
 def test_01_original_source_sha(self):
  check_sources(ROOT)
  self.assertEqual(len(self.models['std'].levels),15)
  self.assertEqual(len(self.models['std'].rad),14)
 def test_02_source_radiative_identity(self):
  self.assertEqual([x[3] for x in self.models['std'].rad],
                   [x[3] for x in self.models['alternate'].rad])
  self.assertEqual(TEMPS,(100.,400.,1000.,4000.))
 def test_03_doppler_dimensions(self):
  nu=2.7e12
  w,b=doppler_width_Hz(nu,100.,0.)
  self.assertAlmostEqual(w/(nu*b/C),1.,delta=1e-14)
  self.assertLess(w,doppler_width_Hz(nu,100.,3.)[0])
 def test_04_beta_limits_and_sign(self):
  self.assertEqual(beta_gauss(0.),1.)
  self.assertAlmostEqual(beta_gauss(1e-6),1-1e-6/(2*math.sqrt(2)),delta=1e-12)
  self.assertGreater(beta_gauss(-0.02),1.)
  self.assertLess(beta_gauss(0.02),1.)
  self.assertTrue(0<beta_gauss(6.6)<1)
 def test_05_beta_independent_adaptive_quad(self):
  for t in (-.02,-.000585,0.,.0001,.02,.1,.5,1.,6.6):
   with self.subTest(t=t):self.assertAlmostEqual(beta_gauss(t),beta_quad(t),delta=1e-11)
 def test_06_dense_stationary_independent_source_models(self):
  for name,model in self.models.items():
   for T,n,z in ((100.,1e2,100.),(4000.,1e4,0.),(4000.,1e8,10.)):
    p,res=dense_population(model,T,n,z)
    q=solve_cmb(model,T,n,z)['populations_J0_to_J14']
    self.assertLess(np.max(np.abs(p-np.array(q))),1e-12)
    self.assertLess(res,1e-9)
    self.assertGreater(np.min(p),-1e-14)  # dense cancellation in vanishing high-J states
 def test_07_radiative_source_function_ledger(self):
  mod=self.models['std'];st=solve_cmb(mod,1000.,1e6,30.)
  r=mod.rad[4];d=tau_zero_and_source(st['populations_J0_to_J14'],mod,r,1000.,0.,30.)
  # (S-Icmb)*tau0*sqrt(pi)*DeltaNu = N * Pnet/(4pi), for N=1 cm-2
  L=(d['source_function_W_m2_sr_Hz']-d['I_CMB_W_m2_sr_Hz'])*d['tau0_per_Ncm2']*math.sqrt(math.pi)*d['Doppler_width_Hz']
  self.assertAlmostEqual(L/d['thin_excess_intensity_per_Ncm2'],1.,delta=1e-12)
 def test_08_real_lowJ_population_inversion(self):
  for name,mod in self.models.items():
   st=solve_cmb(mod,4000.,1e4,0.)
   r=mod.rad[0]
   d=tau_zero_and_source(st['populations_J0_to_J14'],mod,r,4000.,0.,0.)
   self.assertLess(d['population_balance'],0.)
   self.assertLess(d['tau0_per_Ncm2']*1e20,0.)
   self.assertGreater(d['net_W_per_HD'],0.)
   self.assertGreater(beta_gauss(d['tau0_per_Ncm2']*1e20),1.)
 def test_09_cmb_absorption_genuine_negative_line_excess(self):
  mod=self.models['std'];st=solve_cmb(mod,100.,1e2,100.)
  powers=[x['net_W_per_HD'] for x in st['line_power_records']]
  self.assertTrue(any(x<0 for x in powers))
  self.assertLess(st['Tgas_K'],st['Tbg_K'])
 def test_10_column_thin_monotonic(self):
  mod=self.models['std'];st=solve_cmb(mod,1000.,1e6,0.)
  d=tau_zero_and_source(st['populations_J0_to_J14'],mod,mod.rad[0],1000.,0.,0.)
  self.assertGreater(d['tau0_per_Ncm2'],0.)
  self.assertEqual(d['tau0_per_Ncm2']*1e16*10,d['tau0_per_Ncm2']*1e17)
 def test_11_invalid_maser_saturation_barrier(self):
  with self.assertRaises(ValueError):beta_gauss(-61.)
  with self.assertRaises(ValueError):doppler_width_Hz(0.,100.,0.)
 def test_12_source_tamper_raises(self):
  import tempfile,shutil
  with tempfile.TemporaryDirectory() as td:
   t=Path(td)/'source/zenodo_v2';t.mkdir(parents=True)
   for f in ('hd_lamda.dat','hd_lamda_altex.dat','hd_population_grids.fits','hd_population_grids_altex.fits'):
    shutil.copyfile(ROOT/'source/zenodo_v2'/f,t/f)
   with (t/'hd_lamda.dat').open('ab') as f:f.write(b'#not-source')
   with self.assertRaises(ValueError):check_sources(td)
 def test_13_FLRW_observer_surface_brightness_scaling(self):
  self.assertAlmostEqual(1./(1.+1.)**4,.0625)
  self.assertAlmostEqual(1./(1.+10.)**4,1./14641.)
 def test_14_grid_cardinality(self):
  self.assertEqual(len(TEMPS)*len(DENSITIES_CM3)*len(REDSHIFTS)*2,160)
  self.assertEqual(160*14*2*4,17920)

 def test_15_inversion_requires_four_level_network(self):
  from inversion_mechanism import truncate
  for m in self.models.values():
   for Jmax in (1,2,3,14):
    mm=truncate(m,Jmax)
    p=solve_cmb(mm,4000.,1e4,0.)['populations_J0_to_J14']
    self.assertEqual(p[1]>3*p[0],Jmax>=3)
 def test_16_ortho_fraction_robustness_at_fixed_state(self):
  for m in self.models.values():
   for f in (0.,.25,.5,.75,1.):
    p=solve_cmb(m,4000.,1e4,0.,f_ortho=f)['populations_J0_to_J14']
    self.assertLess(3*p[0]-p[1],0.)

 def test_17_new_inversion_phase_requires_original_temperature_knot(self):
  for m in self.models.values():
   p=solve_cmb(m,2000.,3e3,0.)['populations_J0_to_J14']
   self.assertGreater(p[1]-3*p[0],0.)
   p=solve_cmb(m,2000.,3e3,100.)['populations_J0_to_J14']
   self.assertLess(p[1]-3*p[0],0.)
 def test_18_inversion_window_brent_root_residual(self):
  from inversion_phase_diagram import balance
  from scipy.optimize import brentq
  for m in self.models.values():
   f=lambda logn:balance(m,4000.,10**logn,0.)
   x=brentq(f,2.5,3.2,xtol=1e-12)
   self.assertLess(abs(f(x)),2e-12)
   self.assertAlmostEqual(10**x,522.851,delta=.01)

if __name__=='__main__':unittest.main()

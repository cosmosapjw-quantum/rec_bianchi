import csv, json, math, unittest
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution
from miri_sixline_profile import (MRS_SUBBANDS,TEMPERATURES,REDSHIFTS,coverage,
  amplitude_free_spread, min_settings_cover, profile_shape, positive_log_powers,rest_wavelengths,source_gate)
from pr169_neufeld15_reference import parse_lamda

ROOT=Path(__file__).resolve().parents[1]

class AtlasAndTheoryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  source_gate(ROOT)
  cls.std=parse_lamda((ROOT/'source/zenodo_v2/hd_lamda.dat').read_bytes(),verify=True)
  cls.alt=parse_lamda((ROOT/'source/zenodo_v2/hd_lamda_altex.dat').read_bytes())
  cls.rest=rest_wavelengths(cls.std)

 def test_no_source_switch_spectroscopy(self):
  self.assertEqual(set(self.rest),set(range(5,11)))
  for j in self.rest:self.assertAlmostEqual(self.rest[j],rest_wavelengths(self.alt)[j],places=12)

 def test_operational_not_nominal_miri_bandpass(self):
  self.assertEqual(MRS_SUBBANDS['4C'][1],27.90)
  self.assertEqual(min_settings_cover(coverage(self.rest,0)),(3,'ABC'))
  self.assertEqual(min_settings_cover(coverage(self.rest,1.25)),(0,''))

 def test_z_1_one_ratio_only(self):
  c=coverage(self.rest,1.)
  self.assertEqual([j for j in sorted(c) if c[j]],[9,10])
  self.assertEqual(min_settings_cover(c),(1,'C'))

 def test_amplitude_invariance(self):
  a=np.array([1.2,2.5,8.9,15.]);b=np.array([2.,2.6,9.,11.])
  self.assertAlmostEqual(amplitude_free_spread(a,b,[0,1,2,3]),
                         amplitude_free_spread(a+37.4,b,[0,1,2,3]))
  self.assertAlmostEqual(amplitude_free_spread(a,b,[0,1,2,3]),
                         amplitude_free_spread(a,b+24.1,[0,1,2,3]))

 def test_logspread_is_pairwise_max(self):
  a=np.log(np.array([1,2,3,5.]));b=np.log(np.array([2,3,5,8.]))
  diff=a-b
  target=max(abs(float(diff[i]-diff[j])) for i in range(4) for j in range(i+1,4))
  self.assertAlmostEqual(amplitude_free_spread(a,b,list(range(4))),target)

 def test_profile_nesting(self):
  logs_alt,_=positive_log_powers(self.alt,1000.,1e6,0.)
  logs_std,_=positive_log_powers(self.std,1000.,1e6,0.)
  select=list(range(6))
  fixed=profile_shape(logs_alt,select,lambda t,n:positive_log_powers(self.std,t,n,0.)[0],(1000.,))
  tempfree=profile_shape(logs_alt,select,lambda t,n:positive_log_powers(self.std,t,n,0.)[0],TEMPERATURES)
  self.assertLessEqual(tempfree['spread'],fixed['spread']+1e-7)
  self.assertLessEqual(fixed['spread'],amplitude_free_spread(logs_alt,logs_std,select)+1e-7)
  self.assertAlmostEqual(tempfree['spread'],.070496875535909,delta=8e-5)

 def test_independent_global_optimization_selected_case(self):
  """Different optimizer vs grid/bracket implementation, same source physics."""
  alt,_=positive_log_powers(self.alt,4000.,1e4,0.)
  select=list(range(6))
  ours=profile_shape(alt,select,lambda t,n:positive_log_powers(self.std,t,n,0.)[0],(4000.,))
  de=differential_evolution(lambda v: amplitude_free_spread(alt,
      positive_log_powers(self.std,4000.,10**v[0],0.)[0],select),[(2.,10.)],
      tol=5e-8,atol=1e-9,seed=7,popsize=9,maxiter=120,polish=True)
  self.assertTrue(de.success)
  self.assertAlmostEqual(ours['spread'],de.fun,delta=2e-5)

 def test_positive_physical_emission(self):
  for m in [self.std,self.alt]:
   logp,p=positive_log_powers(m,4000.,1e4,.5)
   self.assertTrue(np.all(np.isfinite(logp)))
   self.assertTrue(np.all(p>0))

 def test_outputs_contract(self):
  with (ROOT/'evidence/MIRI_SOURCE_NUISANCE_PROFILE_140.csv').open() as f: rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),140)
  self.assertEqual(sum(int(x['visible_line_count'])>=2 for x in rows),120)
  self.assertEqual(sum(int(x['visible_line_count'])==0 for x in rows),20)
  for x in rows:
   self.assertLessEqual(float(x['T_and_density_profile_logspread']),float(x['fixed_T_density_profile_logspread'])+3e-7)
   self.assertLessEqual(float(x['fixed_T_density_profile_logspread']),float(x['direct_logspread'])+3e-7)

 def test_no_fake_likelihood(self):
  r=json.loads((ROOT/'evidence/MIRI_SHAPE_SUMMARY.json').read_text())
  self.assertEqual(r['source_35Hz_original'],'FAIL7/8')
  self.assertEqual(r['canonical_DAG'],'28/88')
  self.assertEqual(r['REC_physical_DAG'],'0/313')
  self.assertIn('NOT sky data',r['science_class'])
  self.assertEqual(r['R6_C9_distinct_author'],'NOT_RUN')

if __name__=='__main__': unittest.main()

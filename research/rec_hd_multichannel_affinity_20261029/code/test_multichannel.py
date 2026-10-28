#!/usr/bin/env python3
"""Targeted exact-source and same-temperature channel controls."""
import hashlib, json, sys, unittest
from pathlib import Path
import mpmath as mp
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'code'))
import multichannel as M
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(P/'inputs/lamda_hd_pinned_20261025.dat').read_bytes()
  cls.lv,cls.rad,cls.col=M.decode(cls.raw)
  cls.res=json.loads((P/'results/RESULT.json').read_text())
 def test_locked_bytes(self):self.assertEqual(hashlib.sha256(self.raw).hexdigest(),M.SRC_SHA)
 def test_corruption(self):
  with self.assertRaises(ValueError): M.decode(self.raw.replace(b'89.227931611',b'89.227931612'))
 def test_literal_counts(self):
  self.assertEqual(len(self.lv),9);self.assertEqual(len(self.rad),8);self.assertEqual([len(x['rows']) for x in self.col],[9,9])
  self.assertEqual([(x['u'],x['l']) for x in self.col[0]['rows']],[(1,0),(2,0)]+[(i,i-1) for i in range(2,9)])
 def test_historical_35Hz_not_promoted(self): self.assertEqual(self.res['original_35Hz_gate'],'FAIL_7_OF_8_PRESERVED')
 def test_unsupported_temperature_rejected(self):
  with self.assertRaises(ValueError): M.generate(self.lv,self.rad,self.col,75,1000)
 def test_source_group_identity(self):self.assertEqual([x['type'] for x in self.col],['p-H2','o-H2'])
 def test_original_cycles_nonzero(self):
  for r in self.res['rows']:
   self.assertGreater(float(r['original_source_sigma_formal_per_s']),0)
   self.assertLess(abs(float(r['synthetic_equal_energy_sigma_formal_per_s'])),1e-65)
 def test_50K_sign(self):
  r=self.res['rows'][0]
  self.assertLess(float(r['pairs'][2]['A_rad_down_col_up']),0) # gap positive
  self.assertGreater(float(r['pairs'][5]['A_rad_down_col_up']),0) # gap negative
 def test_cycle_triangle_identity(self):
  for r in self.res['rows']:
   a1=mp.mpf(r['pairs'][0]['A_rad_down_col_up']);a2=mp.mpf(r['pairs'][1]['A_rad_down_col_up'])
   self.assertLess(abs(float(mp.mpf(r['triangle_affinity_0_rad_1_rad_2_col_0'])+a1+a2)),1e-15)
 def test_no_physical_production_claim(self):self.assertEqual(self.res['status'],'PASS_SCOPED_SYNTHETIC_MARKOV_DIAGNOSTIC');self.assertFalse(self.res['REI_activation'])
if __name__=='__main__':unittest.main(verbosity=2)

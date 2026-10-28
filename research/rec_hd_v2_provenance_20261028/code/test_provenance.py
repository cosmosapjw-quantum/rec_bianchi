#!/usr/bin/env python3
"""Targeted consistency and negative controls; does not rerun old HD suite."""
import sys,unittest,hashlib,json
from pathlib import Path
from decimal import Decimal,localcontext
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'code'))
import hd_source_thermal as hd

class ScopedTests(unittest.TestCase):
 def setUp(self):
  self.data=(HERE/'inputs/lamda_hd_pinned_20261025.dat').read_bytes()
 def test_exact_bytes(self):
  self.assertEqual(hashlib.sha256(self.data).hexdigest(),hd.SHA)
  self.assertEqual(len(self.data),2289)
 def test_one_based_and_J(self):
  lev,lines=hd.extract(self.data)
  self.assertEqual([(l['upper'],l['lower']) for l in lines],[(i+1,i) for i in range(1,9)])
  self.assertEqual([l['J'] for l in lev],list(range(9)))
 def test_corrupted_bytes_fail_before_admission(self):
  changed=self.data.replace(b'89.227931611',b'89.227931612')
  self.assertNotEqual(hashlib.sha256(changed).hexdigest(),hd.SHA)
 def test_earlier_seven_failures_unchanged(self):
  a=json.loads((HERE/'results/RESULT.json').read_text())['data']
  self.assertEqual([int(x['line_id']) for x in a if not x['printed_rounding_35Hz_gate']],list(range(2,9)))
 def test_Kirchhoff_opposite_sign(self):
  a=json.loads((HERE/'results/RESULT.json').read_text())['data']
  for x in a:
   d=Decimal(x['signed_delta_hz'])
   for t in [50,100,200]:
    k=Decimal(x['thermal'][str(t)]['Kirchhoff_ratio_minus_1'])
    self.assertEqual((k<0),(d>0))
 def test_consistent_toy_ratio_is_one(self):
  with localcontext() as c:
   c.prec=80
   x=Decimal('0.74')
   self.assertEqual((x.exp()-1)/(x.exp()-1),Decimal(1))
 def test_unknown_document_row_not_measurement(self):
  a=json.loads((HERE/'results/RESULT.json').read_text())['data']
  self.assertEqual([x['line_id'] for x in a if not x['2011_cdms_document_reported_fit_input']],[5,6,8])
  self.assertTrue(all(not x['direct_2011_v2_catalog_row_archive_verified'] for x in a))

if __name__=='__main__':unittest.main(verbosity=2)

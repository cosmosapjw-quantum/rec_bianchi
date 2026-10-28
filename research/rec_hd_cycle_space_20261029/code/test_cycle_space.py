import unittest,sys,hashlib,json,copy
from pathlib import Path
import sympy as sp
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'code'))
from cycle_space import load,graph_matrices,run,decimal_source_failures,SOURCE_SHA,PRIOR151_SHA
class CycleSpaceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(HERE/'private_inputs/lamda_hd_pinned_20261025.dat').read_bytes()
  cls.lev,cls.edges=load(cls.raw)
  cls.x=json.loads((HERE/'results/RESULT.json').read_text())
 def test_original_sha(self):
  self.assertEqual(len(self.raw),2289)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
 def test_prior_sha(self):
  self.assertEqual(hashlib.sha256((HERE/'private_inputs/PR151_RESULT.json').read_bytes()).hexdigest(),PRIOR151_SHA)
 def test_26_channel_types_and_2to0(self):
  self.assertEqual({k:sum(e['kind']==k for e in self.edges) for k in ('photon','pH2','oH2')},{'photon':8,'pH2':9,'oH2':9})
  self.assertEqual(len([e for e in self.edges if e['lower']==0 and e['upper']==2]),2)
 def test_exact_incidence_and_cycles(self):
  B,Z,D,M,*_=graph_matrices(self.edges)
  self.assertEqual(B.rank(),8);self.assertEqual(Z.rank(),18);self.assertEqual(B*Z,sp.zeros(9,18))
  self.assertEqual(M.rank(),8)
 def test_source_driven_zero_chords(self):
  B,Z,D,M,*_=graph_matrices(self.edges)
  self.assertEqual(M[:8,:],sp.eye(8));self.assertEqual(M[8:,:],sp.zeros(10,8))
 def test_second_nullspace_construction(self):
  B,*_=graph_matrices(self.edges);self.assertEqual(len(B.nullspace()),18)
 def test_original_35hz_failure_preserved(self):
  f=decimal_source_failures(self.lev,self.edges);self.assertEqual([r['J_upper'] for r in f if not r['35Hz_pass']],list(range(2,9)))
 def test_byte_corruption_refused(self):
  x=self.raw.replace(b'89.227931611',b'89.227931612')
  with self.assertRaises(AssertionError):load(x)
 def test_missing_photon_edge_refused(self):
  with self.assertRaises(AssertionError):load(self.raw.replace(b'2674.98609400',b'2674.9860940'))
 def test_saved_six_points_no_full_replay(self):
  self.assertEqual(len(self.x['sample_cases']),6)
  self.assertEqual({v['T_K'] for v in self.x['sample_cases']},{50,100,200})
  self.assertEqual({v['n_pH2_each_cm3'] for v in self.x['sample_cases']},{1000,1000000})
 def test_source_model_zeros_and_closure(self):
  import decimal
  self.assertTrue(all(decimal.Decimal(v['max_zero_chord_cycle_abs'])<decimal.Decimal('1e-75') for v in self.x['sample_cases']))
  self.assertTrue(all(decimal.Decimal(v['max_cycle_closure_abs'])<decimal.Decimal('1e-75') for v in self.x['sample_cases']))
 def test_counterfactual_mathematical_zero_not_input_change(self):
  M=sp.Matrix(self.x['defect_to_cycle_map_integer'])
  self.assertEqual(M*sp.zeros(8,1),sp.zeros(18,1))
  self.assertEqual(hashlib.sha256((HERE/'private_inputs/lamda_hd_pinned_20261025.dat').read_bytes()).hexdigest(),SOURCE_SHA)
 def test_no_physical_admission(self):
  self.assertEqual(self.x['historical_CDMS_2011_version2_raw'],'NOT_ACQUIRED')
  self.assertEqual(self.x['canonical_DAG'],'28/88+0')
  self.assertFalse(self.x['REI_activation']);self.assertIsNone(self.x['H5_epsilon'])
if __name__=='__main__':unittest.main(verbosity=2)

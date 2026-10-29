import sys,unittest,copy
from pathlib import Path
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import produce_atlas as m

class HD1984Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.s=m.read_sources();cls.out=m.compute(cls.s);cls.r=cls.out['experimental_rows']
 def test_primary_five(self):
  self.assertEqual(len(self.r),5);self.assertEqual([r['experiment'] for r in self.r].count('1984'),3)
 def test_quantum_assignment(self):
  self.assertEqual([(r['uJ'],r['lJ']) for r in self.r],[(2,0),(3,1),(4,3),(6,5),(7,6)])
 def test_graph_measured(self):
  self.assertEqual((self.out['measurement_graph_rank'],self.out['measurement_graph_nullity']), (5,4))
 def test_anchor_graph(self):
  self.assertEqual((self.out['with_2011_nominal_anchor_rank'],self.out['with_2011_nominal_anchor_nullity']),(6,3))
  self.assertEqual(self.out['with_2011_nominal_anchor_components'],[[0,1,2,3,4],[5,6,7],[8]])
 def test_residual_R5(self):
  self.assertEqual(D(self.r[3]['measured_minus_2021_photon_Hz']),D('433112344.800'))
 def test_residual_R3(self):
  self.assertEqual(D(self.r[2]['measured_minus_2021_photon_Hz']),D('-28733778.400'))
 def test_residual_R6(self):
  self.assertEqual(D(self.r[4]['measured_minus_2021_photon_Hz']),D('6857.6600'))
 def test_lte_pos_monotonic(self):
  for j in (0,3,6):
   vals=[D(r['LTE_n_upper_over_lower']) for r in self.out['experimental_LTE_rows'][j:j+3]]
   self.assertTrue(0<vals[0]<vals[1]<vals[2])
 def test_photon_energy_dimension(self):
  self.assertEqual(D(self.r[3]['photon_energy_J'])/D(self.r[3]['measured_Hz']),m.H)
 def test_no_model_sigma(self):
  self.assertTrue(all(r['source_residual_is_statistical_sigma'] is False and r['source_2021_photon_sum_Hz'] for r in self.r))
 def test_2011_old_gate_preserved(self):
  self.assertEqual(self.out['old_35Hz'],'FAIL7/8_PRESERVED')
 def test_bad_input_rejected(self):
  s=copy.deepcopy(self.s);s['source/LAB_1984_ANCHORS.json']['measurements'][0]['upper_J']=5
  with self.assertRaises(ValueError):m.compute(s)
 def test_source_hash_tamper_rejected(self):
  from tempfile import TemporaryDirectory
  from shutil import copytree
  with TemporaryDirectory() as d:
   for s in m.SOURCES:
    p=Path(d)/s;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/s).read_bytes())
   f=Path(d)/'source/LAB_1984_ANCHORS.json';f.write_bytes(f.read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'SOURCE_IDENTITY_MISMATCH'):m.read_sources(d)
 def test_conditional_levels(self):
  q=self.out['conditional_lowJ_levels'];self.assertEqual(len(q),5)
  self.assertEqual(D(q[2]['difference_from_inherited_photon_cumulative_Hz']),D('-14877400'))
  self.assertEqual(D(q[3]['difference_from_inherited_photon_cumulative_Hz']),D('-45034200'))
 def test_no_fabricated_full_spectrum(self):
  self.assertEqual(self.out['missing_physical_observation_bridge_edges_given_anchor'],[[5,4],[8,7]])
  self.assertEqual(self.out['production'],'HOLD')
if __name__=='__main__':unittest.main()

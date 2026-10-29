import importlib.util
import pathlib
import sys
import unittest
from decimal import Decimal

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from cdms_v2_crosswalk import load_json,calculate, HZ_PER_CM1,ROUNDING_HALF

class TestRealCrosswalk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=load_json(ROOT/'source/CDMS2011_V2_EGY_V0_TRANSCRIPTION.json')
        bundle=ROOT/'reference/pr161/data/LAMDA_HD_SOURCE_TRANSCRIPTION.json'
        inherited=ROOT.parent/'rec_hd_nlte_20261030/data/LAMDA_HD_SOURCE_TRANSCRIPTION.json'
        cls.l=load_json(bundle if bundle.is_file() else inherited)
        cls.o=calculate(cls.c,cls.l)

    def test_shape_and_ancestry(self):
        self.assertEqual((self.o['level_count'],self.o['line_count']),(9,8))
        self.assertEqual(self.o['source_2011_v2_raw'],'NOT_ACQUIRED')

    def test_all_eight_joint_print_cells(self):
        self.assertEqual(self.o['joint_print_cell_pass_count'],8)
        for row in self.o['source_lines']:
            self.assertLessEqual(abs(Decimal(row['photon_cumulative_level_minus_egy_cm1'])),ROUNDING_HALF)

    def test_measured_residuals_preserved(self):
        self.assertEqual([Decimal(z['measured_minus_photon_Hz']) for z in self.o['measured_combinations']], [Decimal('-14877400'),Decimal('-45034200')])

    def test_no_sigma_inferred(self):
        self.assertTrue(all(z['catalog_vs_lab_sigma_significance'] is None for z in self.o['measured_combinations']))
        self.assertEqual(self.o['fit_joint_covariance'],None)

    def test_source_specific_gate_not_rewritten(self):
        self.assertEqual(self.o['old_35Hz_gate'],'FAIL7/8_UNCHANGED')
        self.assertEqual(self.o['rec_physical_dag'],'0/313_UNCHANGED')

    def test_copy_error_is_detected(self):
        import copy
        wrong=copy.deepcopy(self.c)
        wrong['levels'][4]['E_cm1']='883.163700'
        with self.assertRaises(ValueError):calculate(wrong,self.l)

    def test_exact_si(self):
        self.assertEqual(HZ_PER_CM1,Decimal('29979245800'))

    def test_print_range_not_statistical_error(self):
        for row in self.o['measured_combinations']:
            self.assertEqual(Decimal(row['max_printed_egy_combination_roundoff_Hz']),Decimal('29979.2458'))

if __name__=='__main__':unittest.main()
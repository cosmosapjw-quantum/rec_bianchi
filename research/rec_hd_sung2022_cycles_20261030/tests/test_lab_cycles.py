import copy
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal as D
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
from lab_cycles import (load_and_validate,compute,save_outputs,incidence,rank_exact,CYCLES,
                        CM_TO_HZ,ONE_MHZ)

class PhysicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=load_and_validate(HERE/'data/LAB_INPUT.json');cls.science=compute(cls.raw)
    def test_new_four_original_lines(self):
        self.assertEqual([r['nu0_cm_minus1'] for r in self.raw['line_parameters']],['89.22792','177.84141','265.24055','350.85401'])
    def test_primary_provenance(self):
        self.assertEqual(self.raw['primary_source']['doi'],'10.1016/j.jqsrt.2022.108412')
        self.assertTrue(self.raw['primary_source']['fit_error_is_not_total_systematic_uncertainty'])
    def test_prior_five_measured_edges(self):
        self.assertEqual(len(self.raw['inherited_measurements']),5)
        self.assertEqual([x['upper_J'] for x in self.raw['inherited_measurements']],[2,3,4,6,7])
    def test_graph_rank(self):
        self.assertEqual(rank_exact(incidence()),6)
        self.assertEqual(self.science['nullity'],3)
        self.assertEqual(self.science['cycle_space_dim'],3)
    def test_components(self):
        self.assertEqual(self.science['components'],[[0,1,2,3,4],[5,6,7],[8]])
    def test_cycle_independence(self):
        self.assertEqual(rank_exact(CYCLES),3)
        for row in CYCLES:
            for j in range(9):
                self.assertEqual(sum(row[i]*incidence()[i][j] for i in range(9)),0)
    def test_cycle_values_MHz(self):
        vals=[D(x['difference_MHz']) for x in self.science['cycles']]
        self.assertEqual(vals,[D('-3.921711314'),D('-17.890385768'),D('-60.258284058')])
    def test_minimax_bound(self):
        self.assertEqual(D(self.science['minimum_max_abs_lowJ_frequency_correction_MHz']),D('8.945192884'))
    def test_minimax_witness(self):
        d=[D(x) for x in self.science['nominal_minimax_correction_witness_MHz']]
        self.assertEqual(d[0]+d[1],D('-3.921711314'))
        self.assertEqual(d[1]+d[2],D('-17.890385768'))
        self.assertEqual(max(abs(x) for x in d),D('8.945192884'))
    def test_no_sigma_or_covariance(self):
        self.assertIsNone(self.science['source_experiment_joint_covariance'])
        self.assertIsNone(self.science['source_fit_joint_covariance'])
        for x in self.science['cycles']:
            self.assertIsNone(x['statistical_sigma'])
    def test_four_physical_photons(self):
        self.assertEqual(len(self.science['line_atlas']),4)
        for x in self.science['line_atlas']:
            self.assertGreater(D(x['photon_energy_J']),D(0))
            self.assertGreater(D(x['photon_wavelength_m']),D(0))
            self.assertGreater(D(x['conditional_spontaneous_power_per_upper_HD_W']),D(0))
    def test_twelve_pressure_rows(self):
        self.assertEqual(len(self.science['pressure_conditional_rows']),12)
        for r in self.science['pressure_conditional_rows']:
            self.assertGreater(D(r['H2_lorentz_HWHM_cm_minus1']),D(0))
            self.assertEqual(D(r['H2_lorentz_FWHM_cm_minus1']),2*D(r['H2_lorentz_HWHM_cm_minus1']))
    def test_negative_R3_H2_shift(self):
        r=[q for q in self.science['pressure_conditional_rows'] if q['upper_J']==4 and q['H2_partial_pressure_atm']=='1']
        self.assertEqual(len(r),1)
        self.assertEqual(D(r[0]['pressure_center_shift_MHz']),D('-0.00108')*CM_TO_HZ/ONE_MHZ)
    def test_2021_Einstein_A_provenance(self):
        self.assertTrue(all('historic_2021_A_s_minus1' in q for q in self.science['line_atlas']))
        self.assertTrue(all('S_296_cm_per_molecule' in q for q in self.science['line_atlas']))
    def test_reject_tampered_DOI(self):
        with tempfile.TemporaryDirectory() as t:
            q=copy.deepcopy(self.raw);q['primary_source']['doi']='10.fake/paper'
            f=Path(t)/'input.json';f.write_text(json.dumps(q))
            with self.assertRaises(ValueError): load_and_validate(f)
    def test_reject_source_gate_relaxation(self):
        with tempfile.TemporaryDirectory() as t:
            q=copy.deepcopy(self.raw);q['protection']['original_35Hz']='PASS'
            f=Path(t)/'input.json';f.write_text(json.dumps(q))
            with self.assertRaises(ValueError): load_and_validate(f)
    def test_reject_fabricated_raw_acquisition(self):
        with tempfile.TemporaryDirectory() as t:
            q=copy.deepcopy(self.raw);q['protection']['CDMS_2011_v2_original_raw']='ACQUIRED'
            f=Path(t)/'input.json';f.write_text(json.dumps(q))
            with self.assertRaises(ValueError): load_and_validate(f)
    def test_bytes_deterministic(self):
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            save_outputs(self.science,t1);save_outputs(self.science,t2)
            for n in ['RESULTS.json','SUNG4_SOURCE_PHYSICAL.csv','H2_PRESSURE_296K_CONDITIONAL.csv','EXPERIMENTAL_CYCLES.csv']:
                self.assertEqual((Path(t1)/n).read_bytes(),(Path(t2)/n).read_bytes())
    def test_final_production_hold(self):
        self.assertEqual(self.science['canonical_DAG'],'28/88')
        self.assertEqual(self.science['REC_physical_DAG'],'0/313')
        self.assertEqual(self.science['production'],'HOLD')
        self.assertEqual(self.science['original_35Hz'],'FAIL7/8')

if __name__=='__main__': unittest.main()

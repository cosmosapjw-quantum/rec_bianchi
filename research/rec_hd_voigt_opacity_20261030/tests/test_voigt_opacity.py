import csv,json,math,sys,tempfile,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.special import voigt_profile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from voigt_opacity import (input_data,sigma_doppler,source_params,phi,equivalent_width,atlas,
                           M_HD_KG,C_MS,KB_JK,H2_ATM,N_REFERENCE_CM2)
SOURCE=ROOT/'data'/'LAB_INPUT_PARENT_PR164.json'

class PhysicalAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=input_data(SOURCE)
        cls.tmp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.tmp.name)
        cls.result=atlas(SOURCE,cls.out)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_01_source_and_version(self):
        self.assertEqual(len(self.data['line_parameters']),4)
        self.assertEqual(self.data['primary_source']['doi'],'10.1016/j.jqsrt.2022.108412')
        self.assertEqual(self.data['protection']['canonical_DAG'],'28/88')
    def test_02_case_and_profile_counts(self):
        self.assertEqual(self.result['case_count'],36)
        self.assertEqual(self.result['profile_count'],7236)
        with (self.out/'SPECTRAL_CASES_36.csv').open() as f:self.assertEqual(len(list(csv.DictReader(f))),36)
        with (self.out/'VOIGT_PROFILE_ATLAS_7236.csv').open() as f:self.assertEqual(len(list(csv.DictReader(f))),7236)
    def test_03_exact_pressure_centers(self):
        r=self.data['line_parameters'][3]
        a=source_params(r,0.5)
        self.assertAlmostEqual(a['center_cm1'],350.85401-0.00108*0.5,places=10)
        self.assertAlmostEqual(a['lorentz_fwhm_cm1'],0.0097,places=12)
    def test_04_sigma_doppler_in_si(self):
        n=89.22792;sig=sigma_doppler(n)
        self.assertAlmostEqual(sig/n,math.sqrt(KB_JK*296/(M_HD_KG*C_MS**2)),places=15)
        self.assertGreater(sig,0)
    def test_05_normalization_of_voigt(self):
        sig=sigma_doppler(89.22792);g=0.0012
        mass=2*quad(lambda x:float(phi(x,sig,g)),0,2.0,epsabs=1e-12,limit=250)[0]
        # finite integration window omits analytic positive Lorentz wings
        self.assertGreater(mass,0.9995)
        self.assertLess(mass,1.0)
    def test_06_gaussian_limit(self):
        sig=0.0005;x=np.array([-0.001,0.0,0.001])
        exp=np.exp(-(x/sig)**2/2)/(math.sqrt(2*math.pi)*sig)
        np.testing.assert_allclose(phi(x,sig,0),exp,rtol=1e-13)
    def test_07_lorentz_limit(self):
        sig=1e-9;gamma=0.002;x=np.array([-0.001,0.0,0.001])
        exp=gamma/(math.pi*(x*x+gamma*gamma))
        np.testing.assert_allclose(phi(x,sig,gamma),exp,rtol=1e-10)
    def test_08_width_area_and_column_scaling(self):
        row=self.data['line_parameters'][1];p=source_params(row,0.1)
        a=equivalent_width(p,1e22);b=equivalent_width(p,1e23)
        self.assertAlmostEqual(b['peak_tau']/a['peak_tau'],10,places=12)
        self.assertGreater(a['profile_captured_area'],0.99)
        self.assertLess(a['profile_captured_area'],1)
        self.assertLessEqual(a['equivalent_width_window_cm1'],a['equivalent_width_upper_cm1'])
        self.assertLessEqual(a['equivalent_width_upper_cm1'],a['integrated_tau_exact_cm1']*(1+1e-9))
    def test_09_positive_tau_and_transmission(self):
        with (self.out/'VOIGT_PROFILE_ATLAS_7236.csv').open() as f:
            for r in csv.DictReader(f):
                self.assertGreaterEqual(float(r['tau']),0)
                self.assertGreater(float(r['transmission']),0)
                self.assertLessEqual(float(r['transmission']),1.0)
    def test_10_pressure_shift_sign(self):
        for i,r in enumerate(self.data['line_parameters']):
            p=source_params(r,0.5)
            self.assertEqual(math.copysign(1,p['shift_cm1']),1 if i!=3 else -1)
    def test_11_bad_source_rejected_in_optimized_python(self):
        x=json.loads(SOURCE.read_text())
        x['line_parameters'][1]['S_296_cm_per_molecule']='2.400E-27'
        with tempfile.TemporaryDirectory() as t:
            inp=Path(t)/'mutant.json';inp.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,'source measured literal'):input_data(inp)
    def test_12_bad_domain_and_units(self):
        with self.assertRaises(ValueError):sigma_doppler(-1)
        with self.assertRaises(ValueError):source_params(self.data['line_parameters'][0],0)
        with self.assertRaises(ValueError):phi(0,0,0.1)
        with self.assertRaises(ValueError):equivalent_width(source_params(self.data['line_parameters'][0],.1),0)
    def test_13_not_S_HITRAN_without_abundance_contract(self):
        self.assertIn('HITRAN_ABUNDANCE_WEIGHTED',self.result['source_S_convention'])
        self.assertNotIn('HD_COLUMN',self.result['source_S_convention'])
    def test_14_no_production_gate_mutation(self):
        p=self.result['protection']
        self.assertEqual(p['original_35Hz'],'FAIL7/8')
        self.assertEqual(p['production'],'HOLD')
        self.assertEqual(p['REC_physical_DAG'],'0/313')
        self.assertEqual(p['CDMS_2011_v2_original_raw'],'NOT_ACQUIRED')
    def test_15_a_continuum_not_new_measurement(self):
        self.assertIn('NOT_OBSERVED',self.result['science_status'])
        self.assertIsNone(self.result['uncertainty_status']['joint_covariance'])
        self.assertEqual(tuple(H2_ATM),(.01,.1,.5))
        self.assertEqual(tuple(N_REFERENCE_CM2),(1e22,1e23,1e24))

if __name__=='__main__': unittest.main()

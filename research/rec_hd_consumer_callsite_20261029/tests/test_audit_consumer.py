"""Scoped tests of pinned PR151/155 HD consumers; no stationary or IVP runs."""
import copy, hashlib, json, os, sys, unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from audit_consumer import (H, C, KB, SOURCE_SHA, MC_BLOB, FS_BLOB, exact, git_blob,
                            check_source, per_event, analytic_bath_rate, planck_self_null,
                            load_module, run)
PARENT=Path(os.getenv('REC_HD_PARENT_DIR',str(HERE/'parent')))
REPO_ROOT=HERE.parents[1]
SOURCE=Path(os.getenv('REC_HD_SOURCE_PATH',str(PARENT/'source_private/hd.dat')))
MC=Path(os.getenv('REC_HD_MULTICHANNEL_PATH',str(PARENT/'multichannel.py' if (PARENT/'multichannel.py').exists() else REPO_ROOT/'research/rec_hd_multichannel_affinity_20261029/code/multichannel.py')))
FS=Path(os.getenv('REC_HD_FIELD_SEMANTICS_PATH',str(PARENT/'field_semantics.py' if (PARENT/'field_semantics.py').exists() else REPO_ROOT/'research/rec_hd_field_semantics_20261029/field_semantics.py')))

class PureMath(unittest.TestCase):
    def test_h_si_exact(self):
        self.assertEqual(H,Fraction(662607015,10**42))
    def test_exact_source_units(self):
        self.assertEqual(per_event('1.000000000','0.000000000','29.97924580000')['nu_E_minus_nu_P_Hz'],'0/1')
    def test_per_event_sign(self):
        a=per_event('1.000000000','0.000000000','29.97924579900')
        self.assertGreater(Fraction(a['nu_E_minus_nu_P_Hz']),0)
        self.assertLess(Fraction(a['matter_plus_radiation_J_per_down_event']),0)
    def test_gauge_shift(self):
        a=per_event('90.000000000','1.000000000','2670.15287620')
        b=per_event('89.000000000','0.000000000','2670.15287620')
        self.assertEqual(a,b)
    def test_nonfinite_rejected(self):
        for s in ('NaN','Infinity','-Infinity'):
            with self.assertRaises(ValueError):exact(s)
    def test_nonpositive_frequency_rejected(self):
        with self.assertRaises(ValueError):per_event('0','0','1')
        with self.assertRaises(ValueError):per_event('1','0','-1')
    def test_bath_rate_vanishes_at_equal_frequency(self):
        import mpmath as mp
        with mp.workdps(90):
            self.assertEqual(analytic_bath_rate('0.0001',Fraction(3),Fraction(1000000000),Fraction(1000000000)),0)
    def test_self_null_any_positive_frequency(self):
        import mpmath as mp
        with mp.workdps(90):
            for n in (Fraction(1_000_000_000),Fraction(1_000_000_001),Fraction(3_000_000_000)):
                self.assertLess(abs(planck_self_null(n)),mp.mpf('1e-85'))

@unittest.skipUnless(SOURCE.exists() and MC.exists() and FS.exists(),'pinned source and parent code not restored')
class ActualPinnedConsumers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=SOURCE.read_bytes()
        cls.r=run(cls.src,MC,FS)
    def test_source_and_code_identity(self):
        self.assertEqual(hashlib.sha256(self.src).hexdigest(),SOURCE_SHA)
        self.assertEqual(git_blob(MC.read_bytes()),MC_BLOB)
        self.assertEqual(git_blob(FS.read_bytes()),FS_BLOB)
    def test_original_gate_unchanged(self):
        self.assertEqual(self.r['original_35Hz_gate'],'FAIL_7_OF_8_PRESERVED')
        self.assertEqual(len(self.r['rows']),8)
    def test_largest_absolute_energy_defect_is_J6(self):
        j=max(self.r['rows'],key=lambda r:abs(Fraction(r['matter_plus_radiation_J_per_down_event'])))['J_upper']
        self.assertEqual(j,6)
    def test_rate_formula_8(self):
        import mpmath as mp
        with mp.workdps(95):
            self.assertTrue(all(mp.mpf(r['synthetic_analytic_rate_abs_diff'])<mp.mpf('1e-78') for r in self.r['rows']))
    def test_positive_synthetic_residual_and_sign(self):
        import mpmath as mp
        for r in self.r['rows']:
            self.assertGreaterEqual(mp.mpf(r['synthetic_total_energy_residual_W_m_minus_3']),0)
    def test_mutate_only_one_photon_edge(self):
        m=self.r['metamorphic'];self.assertEqual(m['changed_radiative_edge_zero_based_indices'],[1])
        self.assertEqual(m['changed_collision_edges'],0)
        self.assertEqual(m['unchanged_other_radiative_edges'],7)
    def test_hash_mutant_rejected(self):
        s=self.src.replace(b'2674.98609400',b'2674.98609401')
        self.assertEqual(len(s),len(self.src))
        with self.assertRaisesRegex(ValueError,'IDENTITY'):check_source(s)
    def test_module_mutant_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'mutant.py';p.write_bytes(MC.read_bytes()+b'\n# source-mutant\n')
            with self.assertRaisesRegex(ValueError,'CODE_IDENTITY'):load_module(p,MC_BLOB,'mutant')
    def test_ledger_exact_consistency(self):
        for r in self.r['rows']:
            delta=Fraction(r['nu_E_minus_nu_P_Hz'])
            self.assertEqual(Fraction(r['matter_plus_radiation_J_per_down_event']),-H*delta)
    def test_policy_no_physical_promotion(self):
        self.assertEqual(self.r['canonical_DAG'],'28/88 (+0)')
        self.assertEqual(self.r['REC_physical_DAG'],'0/313 (+0)')
        self.assertIsNone(self.r['H5_epsilon'])
        self.assertEqual(self.r['production'],'HOLD')

if __name__=='__main__':unittest.main()

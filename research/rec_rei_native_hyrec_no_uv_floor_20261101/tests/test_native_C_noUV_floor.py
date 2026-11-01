"""Source-authentic HyRec2012 noUV optical floor: adversarial physical contracts."""
import csv
import gzip
import hashlib
import importlib.util
import json
import math
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
REPO=HERE.parents[1]
spec=importlib.util.spec_from_file_location("native_C_noUV_floor",HERE/"native_C_noUV_floor.py")
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)
src=mod._parent(REPO)


class OriginalHyRecNoUVPhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.info,cls.high,cls.q=src.prepare(REPO)
        cls.low=mod.real_lowz_C(REPO,src,cls.info,cls.high)
        with tempfile.TemporaryDirectory() as td:
            cls.stats=mod.compute(REPO,Path(td))
            with gzip.open(Path(td)/cls.stats["output_file"],"rt") as f:
                cls.rows=list(csv.DictReader(f))

    def test_original_C_8001_rows_and_21_native_lowz(self):
        payload=(REPO/src.NATIVE_C_GZIP_REL).read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(),src.NATIVE_C_GZIP_SHA256)
        self.assertEqual(len(gzip.decompress(payload).splitlines()),8001)
        self.assertEqual([t[0] for t in self.low],list(range(21)))
        self.assertEqual(len(self.high),1581)

    def test_no_duplicate_z20_and_1601_unique_native_z(self):
        self.assertEqual(len(self.rows),1601)
        self.assertEqual([int(float(v["zbar"])) for v in self.rows],list(range(1601)))
        self.assertEqual(self.rows[20]["source_segment"],"HYREC_C_NO_ASTRO_0_TO_20")
        self.assertEqual(self.rows[21]["source_segment"],"HYREC_C_ORIGINAL_PR187_20_TO_1600")

    def test_original_native_C_kelvin_ratio_not_kelvin(self):
        self.assertAlmostEqual(self.low[0][2],2.7255*.0079726607141,places=13)
        self.assertAlmostEqual(self.low[0][1],.000175613025657,places=15)
        self.assertAlmostEqual(self.low[20][1],self.high[0]["xe_per_H"],places=17)
        self.assertAlmostEqual(self.low[20][2],self.high[0]["Tgas_K"],places=11)

    def test_rei_recipient_density_once_z20(self):
        nH=self.q["z20_nH_rei_m3"]
        xe=self.low[-1][1]
        self.assertLess(abs(nH*xe/self.high[0]["ne_m3"]-1),3e-14)
        self.assertGreater(nH,0.)

    def test_physical_lowz_tau_simpson_against_independent_trapezoid(self):
        full=self.stats["tau_noUV_0_to_20"]
        self.assertGreater(full,0.)
        self.assertLess(abs(self.stats["tau_lowz_simpson_minus_trapezoid"]),5e-8)
        self.assertLess(abs(full-self.stats["tau_lowz_coarse_step2_simpson"]),5e-8)

    def test_lowz_frozen_electron_fraction_changes_tau(self):
        self.assertGreater(self.stats["tau_noUV_0_to_20_frozen_xe_z20_control"],
                           self.stats["tau_noUV_0_to_20"])

    def test_z20_differential_clock_source_matches_both_segments(self):
        self.assertLess(self.stats["z20_source_continuity_rate_rel"],3e-13)
        got=float(self.rows[20]["d_tau_dz"])
        self.assertLess(abs(got/self.q["kappa"][0]-1),3e-13)

    def test_tau_stitches_parent_source_without_overlap(self):
        tau20=self.stats["tau_noUV_0_to_20"]
        self.assertLess(abs(self.stats["tau_noUV_0_to_1100"]-(tau20+self.q["tau"][1080])),1e-12)
        self.assertLess(abs(self.stats["tau_noUV_0_to_1600"]-(tau20+self.q["tau"][-1])),1e-12)
        self.assertLess(self.stats["highz_tau_addition_parity_max_abs"],1e-12)

    def test_primordial_visibility_uniform_survival_factor(self):
        survival=self.stats["P_noUV_0_to_20"]
        self.assertLess(self.stats["highz_visibility_const_factor_max_abs"],1e-14)
        row=self.rows[1100]
        self.assertAlmostEqual(float(row["visibility_noUV_per_z"]),
                               survival*self.q["visibility"][1100-20],places=13)

    def test_scatter_probability_and_visibility_normalization(self):
        tau=self.stats["tau_noUV_0_to_20"]
        self.assertAlmostEqual(self.stats["noUV_scatter_probability_0_to_20"],
                               -math.expm1(-tau),places=15)
        self.assertLess(abs(self.stats["full_visibility_normalization_minus_expected"]),2e-5)

    def test_source_only_visibility_peak_unshifted(self):
        self.assertEqual(self.stats["visibility_peak_zbar_noUV"],1078)
        self.assertEqual(self.stats["new_evolved_IVPs"],0)
        self.assertEqual(self.stats["rec_H5_physical_DAG"],"0/313")

    def test_genuine_F08_S0_source_mismatch_is_quantified(self):
        v=self.stats["original_REI_F08_source_equivalence"]
        self.assertFalse(v["original_F08_same_source_and_clock_as_REC"])
        self.assertFalse(v["source_equal_material_initial_conditions"])
        self.assertFalse(v["source_equal_initial_ionizing_photons"])
        self.assertFalse(v["F08_has_physical_Friedmann_clock"])
        self.assertEqual(v["F08_OBSERVER_SKY_DIRECT_SPLICE"],"REJECTED_PHYSICAL_SOURCE_MISMATCH")
        self.assertAlmostEqual(v["F08_to_REC_ne_ratio"],277.058585917949,places=10)
        self.assertAlmostEqual(v["F08_to_REC_H_ratio"],84.49441345424103,places=11)
        self.assertGreater(v["F08_to_REC_H_ratio"],80)
        self.assertGreater(v["F08_to_REC_xe_ratio"],1000)
        self.assertGreater(v["F08_to_REC_T_ratio"],1000)
        self.assertGreater(v["F08_to_REC_ne_ratio"],100)

    def test_forged_F08_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td)/mod.SCENARIO
            d.parent.mkdir(parents=True)
            d.write_bytes((REPO/mod.SCENARIO).read_bytes()+b"\n")
            with self.assertRaises(ValueError):
                mod.source_equal_F08(Path(td),src,self.info,self.high)

    def test_source_and_acceptance_flags_never_promote(self):
        self.assertEqual(self.stats["true_REI_astrophysical_electron_history"],
                         "NOT_AVAILABLE_NOT_REPLACED")
        self.assertEqual(self.stats["source_adoption"],"NOT_ADOPTED")
        self.assertEqual(self.stats["rei_canonical_DAG"],"28/88")
        self.assertEqual(self.stats["rei_physical_fast_DAG"],"4/7")
        self.assertEqual(self.stats["original_REI_first_interval"],
                         "BLOCKED_TICK160_TO161_UNCHANGED")

    def test_new_model_byte_determinism_and_no_dynamic_metadata(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            x=mod.compute(REPO,Path(a))
            y=mod.compute(REPO,Path(b))
            self.assertEqual(x["output_sha256"],y["output_sha256"])
            self.assertEqual((Path(a)/x["output_file"]).read_bytes(),
                             (Path(b)/y["output_file"]).read_bytes())
            self.assertEqual((Path(a)/"SCIENCE_STATUS.json").read_bytes(),
                             (Path(b)/"SCIENCE_STATUS.json").read_bytes())


if __name__=="__main__":
    unittest.main()

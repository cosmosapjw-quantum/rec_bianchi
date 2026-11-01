"""Scientific contracts for REC-only z20 local Thomson ray-clock witness."""
from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
REPO=HERE.parents[1]
SPEC=importlib.util.spec_from_file_location("z20_local_receiver",HERE/"z20_local_receiver.py")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
sys.path.insert(0,str(REPO/"research/rec_rei_hyrec_primordial_screen_20261101"))
import original_hyrec_screen as origin


class TestPhysicalZ20Receiver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=mod.read_z20_shear_cases(REPO)
        cls.info,cls.rows,cls.q=origin.prepare(REPO)
        cls.qzero=next(c for c in cls.cases if c["q_ref"]==0.)

    def test_immutable_shear_source_identity(self):
        assert mod.blob_sha1((REPO/mod.SHEAR_REL).read_bytes())==mod.SHEAR_BLOB_SHA1

    def test_source_q0_opacity_exact_baseline_parity(self):
        old=self.rows[0]
        v=mod.local_clock_opacity(origin.C_M_S*origin.SIGMA_T_M2*old["ne_m3"],
                                  origin.hubble(20),0.,0.,self.qzero)
        self.assertLess(abs(v["mean_clock_dtaudln1pz"]/old["dtaudlna"]-1),2e-12)

    def test_signed_clock_is_negative_for_forward_lna(self):
        for c in self.cases:
            v=mod.local_clock_opacity(7.3e-21,origin.hubble(20),c["q_ref"],.5,c)
            self.assertEqual(v["forward_lna_dtaudln_a"],-v["mean_clock_dtaudln1pz"])
            self.assertGreater(v["ray_clock_dtaudln1pz_ray"],0.)

    def test_zero_shear_direction_independent(self):
        vals=[mod.local_clock_opacity(7.e-21,origin.hubble(20),0.,mu,self.qzero)
              ["ray_clock_dtaudln1pz_ray"] for mu in (0,.1,.5,.9,1)]
        self.assertEqual(len(set(vals)),1)

    def test_positive_q_parallel_faster_lower_opacity(self):
        c=next(c for c in self.cases if c["q_ref"]==.01)
        pa=mod.local_clock_opacity(7.e-21,origin.hubble(20),.01,1.,c)
        pe=mod.local_clock_opacity(7.e-21,origin.hubble(20),.01,0.,c)
        self.assertGreater(pa["Hray_s_inv"],pe["Hray_s_inv"])
        self.assertLess(pa["ray_clock_dtaudln1pz_ray"],
                        pe["ray_clock_dtaudln1pz_ray"])

    def test_negative_q_reverse_order(self):
        c=next(c for c in self.cases if c["q_ref"]==-.01)
        pa=mod.local_clock_opacity(7.e-21,origin.hubble(20),-.01,1.,c)
        pe=mod.local_clock_opacity(7.e-21,origin.hubble(20),-.01,0.,c)
        self.assertGreater(pa["ray_clock_dtaudln1pz_ray"],
                           pe["ray_clock_dtaudln1pz_ray"])

    def test_bianchi_H_trace_relation(self):
        for c in self.cases:
            self.assertAlmostEqual((c["H_parallel_over_H"]+
                                    2*c["H_perp_over_H"])/3,1.,places=13)

    def test_ray_energy_bianchi_zero_shear(self):
        val=mod.lrs_ray_redshift_ratio(1100,20,(.6,.8,0),(0,0,0),(0,0,0))
        self.assertAlmostEqual(val,1101/21,places=12)

    def test_ray_energy_exact_axis_exponential(self):
        delta=.03
        val=mod.lrs_ray_redshift_ratio(100,20,(0,0,1),(0,0,0),
                                        (-delta,-delta,2*delta))
        self.assertAlmostEqual(val,(101/21)*math.exp(-2*delta),places=13)

    def test_bad_direction_or_shear_trace_rejected(self):
        with self.assertRaises(ValueError):
            mod.lrs_ray_redshift_ratio(100,20,(1,1,0),(0,0,0),(0,0,0))
        with self.assertRaises(ValueError):
            mod.lrs_ray_redshift_ratio(100,20,(1,0,0),(0,0,0),(.1,0,0))

    def test_no_highz_shear_extrapolation(self):
        illegal=next(c for c in json.loads((REPO/mod.SHEAR_REL).read_text())["rows"]
                     if c["q_ref"]==-.005 and c["zbar_formal"]==600)
        with self.assertRaises(ValueError):
            mod.local_clock_opacity(7.e-21,origin.hubble(600),-.005,1.,illegal)

    def test_original_REI_baseline_electron_delta(self):
        ne=self.rows[0]["ne_m3"]
        baseline=self.info["published_rei_approximate_initial"]["electron_density_m3"]
        expected=self.info["donor_minus_baseline"]["ne_m3"]/baseline
        self.assertAlmostEqual(ne/baseline-1,expected,places=14)

    def test_output_exact_q_units_and_30_rows(self):
        with tempfile.TemporaryDirectory() as td:
            o=Path(td)
            report=mod.compute(REPO,o)
            with (o/"REC_REI_Z20_LOCAL_RAY_CLOCK_OPACITY.csv").open(newline="") as f:
                records=list(csv.DictReader(f))
            self.assertEqual(len(records),30)
            self.assertEqual(float(records[0]["q_ref"]),-.01) # true dimensionless q!
            self.assertEqual(float(records[-1]["q_ref"]),.01)
            self.assertEqual(sorted(set(float(r["mu_parallel"]) for r in records)),[0.,.5,1.])
            self.assertEqual(report["new_source_evolved_states"],0)
            self.assertEqual(report["REI_canonical"],"28/88")
            self.assertEqual(report["actual_native_REI_Thomson_CMB_LoS_receiver"],
                             "NOT_IDENTIFIED_IN_TRACKED_REI_PYTHON_SOURCE")

    def test_output_byte_determinism(self):
        with tempfile.TemporaryDirectory() as tda, tempfile.TemporaryDirectory() as tdb:
            ra=mod.compute(REPO,Path(tda))
            rb=mod.compute(REPO,Path(tdb))
            self.assertEqual(ra["csv_sha256"],rb["csv_sha256"])
            self.assertEqual((Path(tda)/"SCIENCE_STATUS.json").read_bytes(),
                             (Path(tdb)/"SCIENCE_STATUS.json").read_bytes())


if __name__=="__main__":
    unittest.main()

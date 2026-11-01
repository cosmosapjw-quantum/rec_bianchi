#!/usr/bin/env python3
"""Source-authentic Compton physics and interval tests; no owner mutation."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import compute_compton as model


class OriginalComptonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="rec194-")
        cls.out = Path(cls.tmp.name) / "data"
        cls.data = model.scientific_computation(ROOT, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_original_identity_and_count(self):
        d = self.data
        self.assertEqual(d["source_tar_sha256"], model.SOURCE_ORIGINAL_TAR)
        self.assertEqual(d["source_cells"], 46080)
        self.assertEqual(d["original_accepted_tick"], 160)
        self.assertEqual(d["official_F05_next_tick"], "161_NOT_ACCEPTED")

    def test_instantaneous_power_negative_with_correct_units(self):
        qlo, qhi = self.data["Compton_Q_erg_s_enclosure"]
        self.assertLess(qlo, qhi)
        self.assertLess(qhi, 0)
        self.assertAlmostEqual(qlo / -1.0692656716215571e39, 1, delta=3e-12)

    def test_gas_kinetic_energy_and_frozen_fraction(self):
        lo, hi = self.data["gas_kinetic_U_erg_enclosure"]
        self.assertGreater(lo, 0)
        self.assertGreater(hi, lo)
        a, b = self.data["frozen_one_tick_kinetic_energy_fraction_enclosure"]
        self.assertTrue(0 < a < b < 2e-7)
        self.assertEqual(self.data["REI_canonical_DAG"], "28/88")

    def test_thermal_equilibrium_zero_and_sign_reversal(self):
        one = np.array([2.0])
        zero = model.compton_power_interval(one, one, one, one, 2.0)
        self.assertEqual(float(zero[0][0]), 0.0)
        hot = model.compton_power_interval(one, one, 3 * one, 3 * one, 2.0)
        cold = model.compton_power_interval(one, one, 0.5 * one, 0.5 * one, 2.0)
        self.assertLess(float(hot[1][0]), 0)
        self.assertGreater(float(cold[0][0]), 0)

    def test_invalid_intervals_fail_closed(self):
        with self.assertRaises(ValueError):
            model.compton_power_interval(np.array([2.0]), np.array([1.0]),
                                         np.array([2.0]), np.array([3.0]), 2.0)
        with self.assertRaises(ValueError):
            model.compton_power_interval(np.array([1.0]), np.array([2.0]),
                                         np.array([-1.0]), np.array([3.0]), 2.0)

    def test_all_csv_rows_and_digest(self):
        path = self.out / "ORIGINAL_F05_COMPTON_46080.csv.gz"
        self.assertEqual(model.digest(path), self.data["source_rows_csv_sha256"])
        with gzip.open(path, "rt", newline="") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                self.assertEqual(int(row["node"]), count)
                self.assertLess(float(row["Compton_Q_upper_erg_s"]), 0)
                self.assertLess(float(row["frozen_tick_frac_lower"]),
                                float(row["frozen_tick_frac_upper"]))
                count += 1
        self.assertEqual(count, 46080)

    def test_cgs_alternative_formula_one_native_cell(self):
        with gzip.open(self.out / "ORIGINAL_F05_COMPTON_46080.csv.gz", "rt") as f:
            row = next(csv.DictReader(f))
        ne = float(row["N_e_upper"])
        t = float(row["T_e_upper_K"])
        tg = self.data["source_blackbody_Tgamma_K"]
        alt = (4 * model.SIGMA_T * model.C_CGS * model.A_RAD * tg**4
               * ne * model.K_B * (tg - t) / (model.M_E * model.C_CGS**2))
        got = float(row["Compton_Q_lower_erg_s"])
        self.assertAlmostEqual(alt / got, 1.0, delta=8e-15)


if __name__ == "__main__":
    unittest.main()

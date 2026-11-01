"""Original-volume native H/He Thomson medium; source/physics tests, not official F05 acceptance."""
import csv
from decimal import Decimal
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rec191_physics", ROOT / "compute_medium.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class OriginalF05MaterialMediumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.result = m.compute(ROOT, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_original_source_byte_locks(self):
        self.assertEqual(m.sha(ROOT / "source_inputs" / m.INITIAL), m.INITIAL_SHA)
        self.assertEqual(m.sha(ROOT / "source_inputs" / m.FORCING), m.FORCING_SHA)
        source, inp, z, dt = m.source_inputs(ROOT)
        self.assertEqual(m.sha(source), m.SOURCE_SHA)
        self.assertEqual(z, Decimal("5.95"))
        self.assertGreater(dt, 0)

    def test_original_source_hash_tamper_fails(self):
        with mock.patch.object(m, "INITIAL_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "VOLUME_OR_FORCING_SOURCE_DRIFT"):
                m.source_inputs(ROOT)
        with mock.patch.object(m, "FORCING_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "VOLUME_OR_FORCING_SOURCE_DRIFT"):
                m.source_inputs(ROOT)

    def test_nonconstant_forcing_fails_closed(self):
        source = ROOT / "source_inputs" / m.FORCING
        with source.open(newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fields = reader.fieldnames
        assert fields is not None
        first = next(i for i,r in enumerate(rows) if r.get("interval_index") == "0")
        rows[first]["z_mid"] = "5.96"
        with tempfile.TemporaryDirectory() as t:
            altered = Path(t) / "source.csv"
            with altered.open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
            with self.assertRaisesRegex(ValueError, "Z_NOT_CONSTANT_NATIVE_VOLUME"):
                m.force_z(altered, float.fromhex("0x1.6afb23f875d98p+39"),
                          float.fromhex("0x1.6d3fe8fed02fap+39"))

    def test_accepted_vs_preview_status_and_scope(self):
        r = self.result
        self.assertEqual(r["node_count"], 46080)
        self.assertEqual(r["accepted_history"], "160/131072")
        self.assertIn("NOT_OFFICIAL", r["source_state"])
        self.assertEqual(r["observed_LoS_tau"], "NOT_COMPUTED")
        self.assertEqual(r["observed_CMB_Stokes"], "NOT_COMPUTED")
        self.assertEqual(r["rei_canonical_DAG"], "28/88")
        self.assertEqual(r["rec_H5_physical_DAG"], "0/313")
        self.assertFalse(r["auto_next"])
        self.assertEqual(r["production"], "HOLD")

    def test_original_weighted_volume_identity(self):
        r = self.result
        z = Decimal(r["original_first_interval_z"])
        vol = Decimal(r["total_native_proper_volume_cm3"])
        weights = Decimal(r["original_native_volume_weight_sum"])
        formula = weights * m.MPC_CM**3 / (1 + z)**3
        self.assertLess(abs(vol / formula - 1), Decimal("1e-15"))
        self.assertLess(abs(weights - 1), Decimal("1e-14"))

    def test_mean_local_rate_and_clumping(self):
        r = self.result
        mean_n = [Decimal(x) for x in r["accepted_160_volume_weighted_mean_electron_density_cm3"]]
        mean_g = [Decimal(x) for x in r["accepted_160_volume_weighted_mean_Thomson_rate_s_inv"]]
        for n,g in zip(mean_n,mean_g):
            self.assertLess(abs(g / (n * m.SIGMA_T_CM2 * m.C_CM_S) - 1),
                            Decimal("5e-17"))
        c = [Decimal(x) for x in r["accepted_160_source_electron_clumping_factor"]]
        self.assertLess(c[0], c[1])
        self.assertGreater(c[0], 1)
        self.assertLess(c[1], 100)
        self.assertLess(Decimal(r["accepted_160_local_electron_density_extrema_cm3"][0]), mean_n[0])
        self.assertGreater(Decimal(r["accepted_160_local_electron_density_extrema_cm3"][1]), mean_n[1])

    def test_correlated_original_recombination_decreases_collision_rate(self):
        r = self.result
        g = [Decimal(x) for x in r["candidate_correlated_Delta_mean_Thomson_rate_s_inv"]]
        self.assertLess(g[0], g[1])
        self.assertLess(g[1], 0)
        self.assertGreater(g[0], Decimal("-1e-24"))
        self.assertEqual(r["original_worker_legacy_logT_fail"],
                         "2.1245050576368385e-4 >2e-4")

    def test_complete_real_native_density_csv(self):
        source = self.out / "SOURCE_NATIVE_THOMSON_MEDIUM_46080.csv.gz"
        self.assertEqual(m.sha(source), self.result["native_medium_csv_gzip_sha256"])
        seen = 0
        with gzip.open(source, "rt", newline="") as f:
            reader = csv.DictReader(f)
            self.assertEqual(tuple(reader.fieldnames or ()), m.FIELDS)
            for row in reader:
                self.assertEqual(int(row["node"]), seen)
                seen += 1
                if seen in (1, 1501, 46080):
                    n = Decimal(row["accepted_tick160_electron_density_lower_cm3"])
                    gamma = Decimal(row["accepted_tick160_Thomson_rate_lower_s_inv"])
                    v = Decimal(row["original_native_proper_volume_cm3"])
                    lam = Decimal(row["accepted_tick160_mean_free_path_upper_cm"])
                    self.assertGreater(v, 0)
                    self.assertGreater(gamma, 0)
                    self.assertLess(abs(gamma / (m.C_CM_S * m.SIGMA_T_CM2 * n) - 1),
                                    Decimal("5e-17"))
                    self.assertLess(abs(lam * m.SIGMA_T_CM2 * n - 1),
                                    Decimal("5e-17"))
        self.assertEqual(seen, 46080)

    def test_fresh_byte_exact_determinism(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            m.compute(ROOT, Path(a))
            m.compute(ROOT, Path(b))
            for name in ("SCIENCE_RESULT.json", "SOURCE_NATIVE_THOMSON_MEDIUM_46080.csv.gz"):
                self.assertEqual((Path(a) / name).read_bytes(), (Path(b) / name).read_bytes())

if __name__ == "__main__":
    unittest.main()

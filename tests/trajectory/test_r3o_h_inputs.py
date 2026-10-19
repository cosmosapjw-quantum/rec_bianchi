"""Pinned actual h-adapter and bounded seed-response tests; no HyRec runs."""
import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import numpy as np
import prepare_r3o_h_history as adapter
import plot_r3o_frontiers as plotting
from compare_r3n_time_grids import compare_histories, load_history

TRACE = ROOT / "research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001"


class ActualHInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = load_history(TRACE / "h_state_trace.json")
        cls.h2 = load_history(plotting.DEFAULT_H2)
        cls.receipt = json.loads((TRACE / "producer_inputs/verification.json").read_text())

    def test_actual_trace_clock_and_source_bytes(self):
        self.assertEqual(self.h.level, 0)
        self.assertEqual(self.h.global_iz.size, 105859)
        self.assertEqual(self.h.global_iz[[0, -1]].tolist(), [0, 105858])
        self.assertEqual(adapter.input_hashes(TRACE / "producer_inputs"), adapter.INPUT_SHA256)
        with np.load(TRACE / "producer_inputs/independent_source_grid.npz", allow_pickle=False) as a:
            for key in ("xe", "Tm_K"):
                self.assertEqual(self.h.values[key].tobytes(), a[key].tobytes())
                self.assertEqual(hashlib.sha256(a[key].tobytes()).hexdigest(),
                                 self.h.provenance["source_array_bytes_sha256"][key])

    def test_existing_h_and_h2_are_insufficient_levels(self):
        r = compare_histories([self.h, self.h2])
        self.assertEqual(r["status"], "INSUFFICIENT_LEVELS")
        self.assertEqual(r["levels_missing"], [2])
        self.assertEqual(r["levels_present"], [0, 1])
        self.assertFalse(r["global_coverage"])

    def test_physics_digest_and_producer_are_actual(self):
        self.assertEqual(self.h.provenance["physics_id"], self.h2.provenance["physics_id"])
        self.assertEqual(self.h.provenance["physics_id"], adapter.PHYSICS_ID)
        self.assertEqual(self.h.provenance["source_commit"], adapter.PRODUCER)
        self.assertEqual(self.h.provenance["kind"], "independent_python")
        self.assertIs(self.h.provenance["checkpoint_resampled"], False)

    def test_missing_nodewise_parity_stays_unknown(self):
        sample = self.h.sample(-math.log1p(1100.))
        with np.load(TRACE / "h_state_trace.npz", allow_pickle=False) as a:
            for key in ("xe", "Tm_K"):
                self.assertNotIn("parity_abs_" + key, a.files)
                self.assertIsNone(self.h.parity_abs[key])
                self.assertIsNone(sample["fields"][key]["parity_abs"])
                self.assertEqual(sample["fields"][key]["quantization_abs"], 0.)

    def test_only_reviewed_input_guard_regimes_are_named(self):
        self.assertTrue(np.all(self.h.regime[:29195] == "UNKNOWN"))
        self.assertTrue(np.all(self.h.regime[29195:72466] == "EMLA"))
        self.assertTrue(np.all(self.h.regime[72466:] == "PEEBLES"))
        self.assertEqual(self.h.boundary_lna,
                         tuple(adapter.X0 + adapter.grid_step(0) * k for k in (29195, 72466)))

    def test_boundary_coverage_ends_at_physical_domain(self):
        self.assertEqual(self.h.provenance["boundary_coverage_lna"],
                         [adapter.X0 + adapter.grid_step(0) * 29195, 0.])
        self.assertGreater(adapter.X0 + adapter.grid_step(0) * 105858, 0.)
        self.assertIsNotNone(self.h.sample(0.))
        self.assertEqual(self.h.sample(adapter.X0)["regime"], "UNKNOWN")

    def test_wrong_input_hash_is_rejected_without_integration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in adapter.INPUT_SHA256:
                (root / name).write_bytes(b"wrong producer bytes")
            with contextlib.redirect_stdout(io.StringIO()):
                code = adapter.main(["--raw-dir", str(root), "--evidence-dir", str(root / "out")])
            self.assertEqual(code, 2)
            self.assertIn("INPUT_HASH_MISMATCH", (root / "out/failure.json").read_text())
            self.assertFalse((root / "out/result.json").exists())

    def test_receipt_rejects_wrong_producer_or_half_step_clock(self):
        adapter.validate_receipt(self.receipt)
        for key, value in (("execution_revision", "0" * 40),
                           ("end_z", 8001. * math.exp(-adapter.grid_step(1) * 105858) - 1.)):
            r = dict(self.receipt)
            r[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                adapter.validate_receipt(r)

    def test_input_mutation_is_rejected_after_real_serialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "raw"
            shutil.copytree(TRACE / "producer_inputs", raw)
            original = adapter.check_saved_output_clock
            def mutate_after_read(path, values):
                checked = original(path, values)
                with (raw / "independent_source_grid.npz").open("ab") as f:
                    f.write(b"mutation after verified input load")
                return checked
            with mock.patch.object(adapter, "check_saved_output_clock", side_effect=mutate_after_read):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = adapter.main(["--raw-dir", str(raw), "--evidence-dir", str(root / "out")])
            self.assertEqual(code, 2)
            self.assertIn("INPUT_MUTATION_DURING_EXTRACTION", (root / "out/failure.json").read_text())
            self.assertFalse((root / "out/result.json").exists())

    def test_existing_output_directory_is_never_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            for script in (adapter, plotting):
                args = ["--evidence-dir", str(out)]
                if script is adapter:
                    args += ["--raw-dir", str(TRACE / "producer_inputs")]
                with self.subTest(script=script.__name__), self.assertRaisesRegex(ValueError, "OUTPUT_EXISTS"):
                    script.main(args)
            self.assertEqual(list(out.iterdir()), [])


class AffineMemoryProbeTests(unittest.TestCase):
    def test_exact_seed_response_and_reset_control(self):
        probe = plotting.affine_probe()
        h = probe["h"]
        self.assertEqual(probe["hyrec_integrations"], 0)
        self.assertEqual(probe["all_three_rational_response_checks"], "PASS")
        for name, case in probe["cases"].items():
            with self.subTest(case=name):
                self.assertAlmostEqual(case["observed_difference"][1], -h * case["delta_prev2"] / 4., places=14)
                self.assertLessEqual(case["max_abs_reference_discrepancy"], case["floating_comparison_allowance"])
        late = probe["cases"]["prev_plus_delta"]["observed_difference"]
        self.assertEqual(late[1], 0.)
        self.assertAlmostEqual(late[2], -h / 4., places=14)
        self.assertGreater(probe["cases"]["reset_both_to_current"]["seed_scale"], 0.)

    def test_probe_work_is_bounded(self):
        for bad in (0, 1, 33, 5210, True, 12.):
            with self.subTest(steps=bad), self.assertRaises(ValueError):
                plotting.affine_probe(bad)


if __name__ == "__main__":
    unittest.main()

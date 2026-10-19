"""Independent mathematical and adversarial contracts, not a HyRec h-sweep."""
import ctypes
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"src"))
from full_bianchi_hyrec.trajectory.time_convergence import (
    H0, X0, SOURCE_ZIP_SHA256, GridHistory, compare_histories, cubic_stencil,
    grid_size, grid_step, original_cubic, signed_triplet,
)


def fixture(level, *, coefficient=200., kind="manufactured", parity=0., n=32):
    g = np.arange(30000*2**level, (30000+n)*2**level+1)
    value = 1.+coefficient*grid_step(level)**2
    values = {"xe": np.full(g.size, value), "Tm_K": np.full(g.size, 2000.*value)}
    e = {k: None if parity is None else np.full(g.size, parity) for k in values}
    q = {k: np.zeros(g.size) for k in values}
    p = {"kind": kind, "checkpoint_resampled": False, "source_zip_sha256": SOURCE_ZIP_SHA256,
         "physics_id": "manufactured-constant-plus-h2", "q": 0, "REI_activation": False,
         "boundary_coverage_lna": [X0, 0.]}
    return GridHistory(level, g, values, e, q, np.full(g.size, "TEST"), (), p)


class CubicTests(unittest.TestCase):
    def test_exact_cubic_polynomials(self):
        nodes = np.array([-1., 0., 1., 2.])
        for power in range(4):
            for f in (-1., -.5, 0., .25, .5, 1., 1.5, 2.):
                self.assertAlmostEqual(original_cubic(nodes**power, f), f**power, places=14)

    def test_global_end_clamp_is_original(self):
        for level in (0, 1, 2):
            idx, f, _ = cubic_stencil(level, 0.)
            np.testing.assert_array_equal(idx, np.arange(grid_size(level)-4, grid_size(level)))
            self.assertTrue(1. < f < 2.)

    def test_partial_edge_is_not_clamped(self):
        g = fixture(0)
        self.assertIsNone(g.sample(X0+H0*30000))
        self.assertIsNone(g.sample(X0+H0*30032))
        self.assertIsNotNone(g.sample(X0+H0*30003.25))

    def test_absolute_weights_for_uncertainty(self):
        g = fixture(0, parity=1.)
        x = X0+H0*30003.5
        _, _, w = cubic_stencil(0, x)
        self.assertTrue(np.any(w < 0.))
        s = g.sample(x)
        self.assertAlmostEqual(s["fields"]["xe"]["parity_abs"], 1.25, places=9)
        self.assertEqual(s["fields"]["xe"]["parity_abs"], float(np.sum(np.abs(w))))

    def test_nonfinite_stencil(self):
        with self.assertRaisesRegex(ValueError, "CUBIC_NONFINITE"):
            original_cubic([1., float("nan"), 1., 1.], .5)

    def test_outside_source_domain(self):
        with self.assertRaisesRegex(ValueError, "OUTSIDE"):
            cubic_stencil(1, X0-H0)


class OriginalCInterpolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("gcc"):
            raise unittest.SkipTest("gcc unavailable; native comparison is NOT_RUN")
        cls.tmp = tempfile.TemporaryDirectory()
        d = Path(cls.tmp.name)
        source = ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
        if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_ZIP_SHA256:
            raise AssertionError("original archive identity")
        with zipfile.ZipFile(source) as z:
            for name in ("hyrectools.c", "hyrectools.h"):
                (d/name).write_bytes(z.read("HyRec/"+name))
        cls.build = ["gcc", "-std=gnu99", "-O2", "-fno-fast-math", "-ffp-contract=off",
                     "-shared", "-fPIC", str(d/"hyrectools.c"), "-lm", "-o", str(d/"interp.so")]
        subprocess.run(cls.build, check=True, capture_output=True, timeout=30)
        cls.lib = ctypes.CDLL(str(d/"interp.so"))
        cls.call = cls.lib.rec_interp1d
        cls.call.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double),
                            ctypes.c_uint, ctypes.c_double]
        cls.call.restype = ctypes.c_double

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_original_c_bit_parity_all_three_output_grids(self):
        cases = 0
        for level in (0, 1, 2):
            n, h = grid_size(level), grid_step(level)
            y = 2.+np.sin(np.arange(n)*h)
            for x in (X0, X0+.25*h, X0+h, X0+173.125*h, -.1, 0.):
                ids, f, _ = cubic_stencil(level, x)
                py = original_cubic(y[ids], f)
                c = self.call(X0, h, y.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), n, x)
                self.assertEqual(float(py).hex(), float(c).hex())
                cases += 1
        self.assertEqual(cases, 18)


class DifferenceTests(unittest.TestCase):
    def calc(self, v, e=(0., 0., 0.), q=(0., 0., 0.), **kw):
        return signed_triplet(v, e, q, scale_floor=1.e-4, **kw)

    def test_resolved_second_order(self):
        r = self.calc([1.+.01, 1.+.01/4., 1.+.01/16.])
        self.assertEqual(r["classification"], "RESOLVED_SAME_SIGN")
        self.assertAlmostEqual(r["p_observed"], 2., places=11)

    def test_observed_first_order_is_not_relabelled_second(self):
        r = self.calc([1.01, 1.005, 1.0025])
        self.assertAlmostEqual(r["p_observed"], 1., places=11)

    def test_nonmonotone(self):
        r = self.calc([1.01, 1., 1.002])
        self.assertEqual(r["classification"], "NONMONOTONE")
        self.assertIsNone(r["p_observed"])

    def test_equal_values_not_infinite_order(self):
        r = self.calc([1., 1., 1.])
        self.assertEqual(r["classification"], "ROUNDOFF_UNRESOLVED")
        self.assertIsNone(r["p_observed"])

    def test_same_h_floor_preserved(self):
        r = self.calc([1.001, 1., .9995], e=(1.e-4, 2.e-4, 3.e-4))
        self.assertAlmostEqual(r["floor01"], .003)
        self.assertAlmostEqual(r["floor12"], .005)
        self.assertEqual(r["classification"], "ROUNDOFF_UNRESOLVED")

    def test_quantization_floor_preserved(self):
        r = self.calc([1.001, 1., .9995], q=(0., 1.e-4, 0.))
        self.assertEqual(r["classification"], "ROUNDOFF_UNRESOLVED")

    def test_unknown_floor_is_not_zero(self):
        r = self.calc([1.01, 1., .9975], e=(0., None, 0.))
        self.assertEqual(r["classification"], "UNCERTAINTY_MISSING")
        self.assertIsNone(r["p_observed"])

    def test_boundary_slope_withheld(self):
        r = self.calc([1.01, 1., .9975], boundary=True)
        self.assertEqual(r["classification"], "STAGE_BOUNDARY")
        self.assertIsNone(r["p_observed"])

    def test_shared_bias_can_cancel(self):
        r = self.calc([1.01+.02, 1.01+.005, 1.01+.00125])
        self.assertAlmostEqual(r["p_observed"], 2., places=11)
        self.assertGreater(abs(1.01125-1.), .01)

    def test_nonfinite_is_rejected(self):
        with self.assertRaises(ValueError):
            self.calc([1., float("inf"), 0.])


class HistoryTests(unittest.TestCase):
    def targets(self):
        return X0+H0*np.arange(30003., 30029.)

    def test_missing_grids_fail_closed(self):
        r = compare_histories([fixture(1)])
        self.assertEqual(r["status"], "INSUFFICIENT_LEVELS")
        self.assertEqual(r["levels_missing"], [0, 2])
        self.assertFalse(r["global_coverage"])
        self.assertEqual(r["rows"], [])

    def test_narrow_domain_not_global(self):
        r = compare_histories([fixture(k) for k in range(3)], self.targets())
        self.assertEqual(r["status"], "MANUFACTURED_DIAGNOSTIC")
        self.assertFalse(r["global_coverage"])
        self.assertFalse(r["global_order_claim"])
        self.assertEqual(r["regions"]["thermal_transition"]["status"], "NO_COVERAGE")
        for row in r["rows"]:
            self.assertAlmostEqual(row["fields"]["xe"]["p_observed"], 2., places=7)

    def test_duplicate_level(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            compare_histories([fixture(1), fixture(1)])

    def test_native_c_cannot_supply_a_python_level(self):
        with self.assertRaisesRegex(ValueError, "INDEPENDENT_PYTHON"):
            fixture(0, kind="native_c")

    def test_nonmonotone_grid(self):
        g = fixture(0)
        iz = g.global_iz.copy(); iz[3] += 1
        with self.assertRaisesRegex(ValueError, "CONTIGUOUS"):
            GridHistory(0, iz, g.values, g.parity_abs, g.quantization_abs, g.regime, (), g.provenance)

    def test_resampled_checkpoint(self):
        g = fixture(0)
        p = dict(g.provenance, checkpoint_resampled=True)
        with self.assertRaisesRegex(ValueError, "RESAMPLED"):
            GridHistory(0, g.global_iz, g.values, g.parity_abs, g.quantization_abs, g.regime, (), p)

    def test_stage_spike_not_removed_from_original_max_gate(self):
        gs = [fixture(k) for k in range(3)]
        g = gs[2]
        values = {k: a.copy() for k, a in g.values.items()}; values["xe"][60] += .1
        gs[2] = GridHistory(2, g.global_iz, values, g.parity_abs, g.quantization_abs, g.regime,
                            (X0+H0*30015,), g.provenance)
        r = compare_histories(gs, self.targets())
        self.assertFalse(r["regions"]["available_domain"]["fields"]["xe"]["original_gates"]["contraction"])
        # A fine-grid boundary spike remains in the norms even when p is withheld.
        self.assertGreater(r["regions"]["stage_neighborhood"]["fields"]["xe"]["maxnorm_D12"], .09)

    def test_missing_uncertainty_withheld(self):
        r = compare_histories([fixture(k, parity=None) for k in range(3)], self.targets())
        self.assertTrue(all(s["fields"]["xe"]["classification"] == "UNCERTAINTY_MISSING" for s in r["rows"]))

    def test_refinement_identity(self):
        for bad in (True, -1, 3, 1.0):
            with self.assertRaises(ValueError): grid_step(bad)

    def test_original_hold_labels_preserved(self):
        r = compare_histories([fixture(1)])
        self.assertEqual(r["preserve"], {"U5_h": "HOLD_9_FAIL", "U5_h2": "HOLD_8_FAIL",
            "historical_budget": "CLOSED_HOLD_NOT_RESET", "REI_activation": False})

    def test_empty_decoded_stage_labels(self):
        g = fixture(0)
        for labels in (np.full(len(g.global_iz), ""), np.full(len(g.global_iz), b"", dtype="S1"),
                       np.full(len(g.global_iz), "  ")):
            with self.assertRaisesRegex(ValueError, "REGIME_LABELS"):
                GridHistory(0, g.global_iz, g.values, g.parity_abs, g.quantization_abs, labels, (), g.provenance)

    def test_unknown_boundary_coverage_withholds_order(self):
        gs = []
        for level in (0, 1, 2):
            g = fixture(level)
            p = dict(g.provenance);p.pop("boundary_coverage_lna")
            gs.append(GridHistory(level, g.global_iz, g.values, g.parity_abs, g.quantization_abs, g.regime, (), p))
        r = compare_histories(gs, [X0+H0*30001.5])
        self.assertFalse(r["rows"][0]["boundary_coverage_known"])
        self.assertEqual(r["rows"][0]["fields"]["xe"]["classification"], "BOUNDARY_COVERAGE_UNKNOWN")
        self.assertIsNone(r["rows"][0]["fields"]["xe"]["p_observed"])

    def test_boundary_just_outside_fragment_is_kept(self):
        gs = []
        for level in (0, 1, 2):
            g = fixture(level)
            gs.append(GridHistory(level, g.global_iz, g.values, g.parity_abs, g.quantization_abs,
                                  g.regime, (X0+H0*29999,), g.provenance))
        r = compare_histories(gs, [X0+H0*30001.5])
        self.assertTrue(r["rows"][0]["stage_neighborhood"])
        self.assertIsNone(r["rows"][0]["fields"]["xe"]["p_observed"])

    def test_inclusive_four_h_endpoints_explicit_and_inferred(self):
        # Late-grid subtraction cancels large terms: a few ulps of ln(a) do
        # not bound the error in constructing X0+g*h. Include the C9 example
        # and a near-z=0 case without enlarging the physical boundary window.
        for boundary_index in (30015, 100015, grid_size(0)-24):
            for inferred in (False, True):
                with self.subTest(boundary_index=boundary_index, inferred=inferred):
                    gs = []
                    for level in (0, 1, 2):
                        g = fixture(level); labels = g.regime.copy()
                        iz = g.global_iz+(boundary_index-30015)*2**level
                        if inferred: labels[15*2**level:] = "AFTER"
                        gs.append(GridHistory(level, iz, g.values, g.parity_abs, g.quantization_abs,
                            labels, () if inferred else (X0+H0*boundary_index,), g.provenance))
                    r = compare_histories(gs, X0+H0*(boundary_index+np.array([-4., 4.])))
                    self.assertTrue(all(row["stage_neighborhood"] for row in r["rows"]))
                    self.assertTrue(all(row["fields"]["xe"]["p_observed"] is None for row in r["rows"]))
                    outside = compare_histories(gs, X0+H0*(boundary_index+np.array([-4.00001, 4.00001])))
                    self.assertTrue(all(not row["stage_neighborhood"] for row in outside["rows"]))

    def test_partial_boundary_coverage_requires_halo(self):
        gs = []
        for level in (0, 1, 2):
            g = fixture(level);p = dict(g.provenance, boundary_coverage_lna=[X0+H0*30000, X0+H0*30032])
            gs.append(GridHistory(level, g.global_iz, g.values, g.parity_abs, g.quantization_abs, g.regime, (), p))
        r = compare_histories(gs, [X0+H0*30001.5, X0+H0*30016])
        self.assertFalse(r["rows"][0]["boundary_coverage_known"])
        self.assertTrue(r["rows"][1]["boundary_coverage_known"])

    def test_clamped_endpoint_reported_separately(self):
        gs = []
        for level in (0, 1, 2):
            g = fixture(level, n=4)
            iz = np.arange(grid_size(level)-len(g.global_iz), grid_size(level))
            gs.append(GridHistory(level, iz, g.values, g.parity_abs, g.quantization_abs,
                                  g.regime, (), g.provenance))
        r = compare_histories(gs, [0.])
        self.assertTrue(r["rows"][0]["clamped_stencil"])
        self.assertEqual(r["regions"]["clamped_stencil"]["points"], 1)


if __name__ == "__main__":
    unittest.main()

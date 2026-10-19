"""Delivery boundary and real saved-state adapter checks; no new trajectory."""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("r3n_cli", ROOT/"scripts/compare_r3n_time_grids.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


class SavedTraceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.p = self.d/"history.json"
        g = np.arange(60000, 60010, dtype=np.int64)
        self.arrays = {"global_iz": g, "redshift": np.array([8001.*math.exp(-cli.grid_step(1)*int(i))-1. for i in g]),
            "xe": np.full(10, .01), "Tm_K": np.full(10, 2000.), "regime": np.full(10, "TEST")}
        for k in cli.FIELD_FLOORS:
            self.arrays["parity_abs_"+k] = np.zeros(10)
            self.arrays["quantization_abs_"+k] = np.zeros(10)
        self.descriptor = {"schema": "rec.r3n.history.v1", "level": 1,
            "origin_lna": cli.X0, "dlna": cli.grid_step(1), "npz": "values.npz", "boundary_lna": [],
            "provenance": {"kind": "manufactured", "physics_id": "saved-test",
                "q": 0, "REI_activation": False, "source_zip_sha256": cli.SOURCE_ZIP_SHA256,
                "checkpoint_resampled": False}}
        self.save()

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        np.savez(self.d/"values.npz", **self.arrays)
        self.descriptor["npz_sha256"] = cli.sha(self.d/"values.npz")
        self.p.write_text(json.dumps(self.descriptor))

    def test_load_verified_roundtrip(self):
        g = cli.load_history(self.p)
        self.assertEqual(g.level, 1)
        np.testing.assert_array_equal(g.values["xe"], self.arrays["xe"])

    def test_corrupt_payload(self):
        with (self.d/"values.npz").open("ab") as f: f.write(b"mutation")
        with self.assertRaisesRegex(ValueError, "SHA_MISMATCH"):
            cli.load_history(self.p)

    def test_wrong_grid_spacing(self):
        self.descriptor["dlna"] *= 2
        self.save()
        with self.assertRaisesRegex(ValueError, "SPACING"):
            cli.load_history(self.p)

    def test_relabelled_level_with_wrong_redshift(self):
        self.descriptor["level"] = 0
        self.descriptor["dlna"] = cli.grid_step(0)
        self.save()
        with self.assertRaisesRegex(ValueError, "REDSHIFT"):
            cli.load_history(self.p)

    def test_nonfinite_uncertainty(self):
        self.arrays["parity_abs_xe"][3] = np.nan
        self.save()
        with self.assertRaisesRegex(ValueError, "UNCERTAINTY"):
            cli.load_history(self.p)

    def test_descriptor_cannot_select_external_data(self):
        self.descriptor["npz"] = "../elsewhere.npz"
        self.p.write_text(json.dumps(self.descriptor))
        with self.assertRaisesRegex(ValueError, "OUTSIDE_DESCRIPTOR"):
            cli.load_history(self.p)

    def test_physical_provenance_cannot_reuse_manufactured_id(self):
        self.descriptor["provenance"]["kind"] = "independent_python"
        self.save()
        with self.assertRaisesRegex(ValueError, "PHYSICAL_PROVENANCE"):
            cli.load_history(self.p)

    def test_require_complete_returns_dedicated_incomplete_exit(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["analyze", "--history", str(self.p), "--evidence-dir", str(self.d/"out"), "--require-complete"])
        self.assertEqual(code, 3)
        result = json.loads((self.d/"out/result.json").read_text())
        self.assertEqual(result["status"], "INSUFFICIENT_LEVELS")
        self.assertEqual(result["levels_missing"], [0, 2])

    def test_nonempty_output_preserves_existing_bytes(self):
        out = self.d/"out"; out.mkdir(); (out/"old.txt").write_text("preserve")
        with self.assertRaisesRegex(ValueError, "OUTPUT_EXISTS"):
            cli.main(["analyze", "--history", str(self.p), "--evidence-dir", str(out)])
        self.assertEqual((out/"old.txt").read_text(), "preserve")

    def test_two_invocations_cannot_share_output(self):
        barrier = threading.Barrier(2)
        out = self.d/"simultaneous"
        def invoke():
            barrier.wait()
            try:
                return cli.main(["analyze", "--history", str(self.p), "--evidence-dir", str(out)])
            except ValueError as e:
                return str(e)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: invoke(), range(2)))
        self.assertEqual(results.count(0), 1)
        self.assertEqual(results.count("OUTPUT_EXISTS_PRESERVE_PRIOR_EVIDENCE"), 1)
        self.assertEqual(json.loads((out/"execution.json").read_text())["status"], "INSUFFICIENT_LEVELS")
        self.assertFalse((out/"failure.json").exists())

    def test_even_empty_existing_output_is_not_reused(self):
        out = self.d/"empty";out.mkdir()
        with self.assertRaisesRegex(ValueError, "OUTPUT_EXISTS"):
            cli.empty_output(out)

    def test_reviewed_r3m_state_trace_when_committed(self):
        p = ROOT/"research/rec_r3n_time_convergence_20261019/real_h2_trace_003/h2_state_trace.json"
        self.assertTrue(p.is_file(), "committed reviewed h2 state trace is required")
        g = cli.load_history(p)
        self.assertEqual(g.global_iz.size, 5211)
        self.assertEqual(g.global_iz[[0, -1]].tolist(), [53179, 58389])
        result = cli.compare_histories([g])
        self.assertEqual(result["status"], "INSUFFICIENT_LEVELS")
        self.assertEqual(result["levels_missing"], [0, 2])
        self.assertEqual(g.provenance["run_location"].split(" ")[0], "owner")


if __name__ == "__main__":
    unittest.main()

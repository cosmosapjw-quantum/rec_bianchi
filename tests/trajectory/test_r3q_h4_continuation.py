"""Focused new h4 checkpoint, callback ownership and supervisor contracts."""
from pathlib import Path
import hashlib
import json
import math
import sys
from types import SimpleNamespace
import numpy as np
import unittest
from unittest import mock
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from full_bianchi_hyrec.trajectory import primordial_2012_quarter_continuation as m
from full_bianchi_hyrec.trajectory.primordial_2012_quarter_start import make_hmla_source
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from run_r3q_h4_supervised import run_owned, read_verification, worker_completed
from verify_r3q_h4_continuation import verify_capsule_source_closure, MANIFEST_RELATIVE

CP = ROOT / "research/rec_r3o_grid_frontiers_20261019/h4_start_002/python_h4_full_start.npz"
ZIP = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def physical_inputs():
    c = m.HyRec2012Cosmology()
    return m.load_frozen_start(CP), c, make_hmla_source(c, OriginalHyRecPrimitiveRateTable.from_archive(ZIP))


class R3QContracts(unittest.TestCase):
    def temp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        return Path(d.name)

    def test_frozen_checkpoint_byte_and_predictor_identity(self):
        tmp_path = self.temp()
        cp = m.load_frozen_start(CP)
        assert cp["iz"][-1] == 72900
        assert np.array_equal(cp["final_predictor"], np.array([cp["helium_rhs_dln_a"][-2:], cp["hydrogen_rhs_dln_a"][-2:]]))
        assert not cp["virtual_out"].flags.writeable
        corrupt = tmp_path / "mutated.npz"
        raw = CP.read_bytes(); corrupt.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
        with self.assertRaisesRegex(ValueError, "SHA_MISMATCH"):
            m.load_frozen_start(corrupt)


    def test_wrong_grid_rejected_before_source(self):
        cp = m.load_frozen_start(CP)
        with self.assertRaisesRegex(ValueError, "H4_COSMOLOGY_REQUIRED"):
            m.integrate_continuation(cp, HyRec2012Cosmology(), None, max_extra_accepted=1)


    def test_actual_prefix_and_callbacks_cannot_change_next_state(self):
        cp, c, source = physical_inputs()
        baseline = m.integrate_continuation(cp, c, source, max_extra_accepted=2)
        calls = []
        def observer(g, z, xh, xhe, tm, vh, lh, out):
            calls.append((g, vh.shape[1]))
            # Even deliberate read-only flag removal affects only detached copies.
            vh.flags.writeable = True; vh[:] = -999
            lh.flags.writeable = True; lh[:] = -999
            out.outgoing_virtual.flags.writeable = True
            out.outgoing_virtual[:] = -999
        def accepted(state, step, out):
            state["iz"] = -999; state["xe"] = math.nan
            step["hydrogen_rhs"] = math.nan
        r = m.integrate_continuation(cp, c, source, max_extra_accepted=2,
                                     observer=observer, on_accept=accepted)
        assert r.states == baseline.states and r.steps == baseline.steps
        for key in ("virtual_out", "average_virtual", "lyman_out", "final_predictor"):
            assert np.array_equal(getattr(r, key), getattr(baseline, key))
        assert np.array_equal(r.virtual_out[:, :8], cp["virtual_out"])
        assert len(calls) == 8 and r.states[-1]["iz"] == 72902
        assert all(g - 72892 == columns for g, columns in calls)

    def test_nonpost_helium_branch_retains_source_neutral_variable(self):
        # Deliberately forced branch contract, not a physical switch result.
        # Original history.c get_rec_next2_HHe evolves neutral xH1s in place.
        cp, c, source = physical_inputs()
        cp["post_saha"] = cp["post_saha"].copy()
        cp["post_saha"][-1] = False
        r = m.integrate_continuation(cp, c, source, max_extra_accepted=1)
        expected = float(cp["xH1s"][-1]) - m.DLNA * (
            1.25*r.steps[0]["hydrogen_rhs"] - .25*float(cp["hydrogen_rhs_dln_a"][-2]))
        assert r.full_evaluations == 1 and r.states[-1]["xH1s"] == expected
        assert r.states[-1]["xe"] == (1.-expected)+r.states[-1]["xHeII"]


    def test_bad_source_residual_never_accepts(self):
        for bad in [math.nan, math.inf, -1.e-12, 2.1e-10]:
            self.check_bad_residual(bad)

    def check_bad_residual(self, bad):
        cp, c, source = physical_inputs(); accepted = []
        patch = mock.patch.object(m, "complete_original_full_atomic", lambda _: SimpleNamespace(
            dxHII_dln_a=0., normalized_matrix_residual=bad))
        patch.start(); self.addCleanup(patch.stop)
        with self.assertRaisesRegex(ArithmeticError, "FULL_SOURCE_OR_SCHUR"):
            m.integrate_continuation(cp, c, source, max_extra_accepted=1,
                                     on_accept=lambda *args: accepted.append(args))
        assert accepted == []


    def test_closure_rejects_changed_code(self):
        tmp_path = self.temp()
        code = tmp_path / "source.py"; code.write_text("frozen\n")
        manifest = tmp_path / MANIFEST_RELATIVE
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"files": {"source.py": hashlib.sha256(code.read_bytes()).hexdigest()}}))
        assert verify_capsule_source_closure(tmp_path, CP)["verified_files"] == 1
        code.write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "SOURCE_CLOSURE"):
            verify_capsule_source_closure(tmp_path, CP)


    def test_supervisor_collects_nonzero_child_and_preserves_logs(self):
        tmp_path = self.temp()
        r = run_owned([sys.executable, "-c", "print('receipt'); raise SystemExit(7)"],
                      tmp_path, tmp_path/"out", tmp_path/"err", 2)
        assert r["returncode"] == 7 and r["process_group_owned"]
        assert (tmp_path/"out").read_text() == "receipt\n"


    def test_supervisor_kills_owned_process_group_at_wall_limit(self):
        tmp_path = self.temp()
        r = run_owned([sys.executable, "-c", "import time; time.sleep(10)"],
                      tmp_path, tmp_path/"out", tmp_path/"err", .1)
        assert r["failure"]["type"] == "TimeoutExpired"
        assert r["process_group_kill_sent"] and r["returncode"] != 0

    def test_interrupted_verification_is_a_receipt_failure(self):
        p = self.temp() / "verification.json"
        for content in ('{"status":', '[]'):
            p.write_text(content)
            worker, failure, sha = read_verification(p)
            assert worker == {} and failure is not None and len(sha) == 64
        p.unlink()
        assert read_verification(p)[1]["type"] == "FileNotFoundError"

    def test_worker_failure_cannot_be_admitted_by_success_label(self):
        process = {"returncode": 0, "failure": None}
        worker = {"status": "SMOKE_ONLY", "first_failure": {"type": "TimeoutError"}}
        assert not worker_completed(worker, process)
        worker["first_failure"] = None
        assert worker_completed(worker, process)


if __name__ == "__main__":
    unittest.main(verbosity=2)

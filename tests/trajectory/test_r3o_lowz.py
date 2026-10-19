"""Small original-C comparisons and low-z stage/memory/resource contracts.

State fixtures below are controlled inputs, not claimed physical trajectories.
The separate --mode smoke runner consumes the complete pinned actual raw U6.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
import importlib.util
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from full_bianchi_hyrec.trajectory import primordial_2012_refined_low_z as m
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("r3o_lowz_verifier_test", ROOT / "scripts/verify_r3o_lowz.py")
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


def fixture_state(iz=m.START_IZ, fraction=.995):
    c = m.HyRec2012Cosmology()
    tr = c.T0_K * (1. + c.redshift(iz))
    return m.LowZCheckpoint(iz, .0013, fraction * tr, -.0047, -.0048, -tr, -tr * 1.0001)


class RefinedLowZTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="r3o_lowz_native_")
        root = Path(cls.temporary.name)
        cls.src, cls.manifest = v.prepare_source(v.SOURCE_ZIP, root / "source")
        lib = root / "r3o_lowz.so"
        command = ["gcc", "-std=gnu99", "-O2", "-fno-fast-math", "-ffp-contract=off",
                   "-shared", "-fPIC", "-I", str(cls.src), str(v.HARNESS),
                   *[str(cls.src / f) for f in ("history.c", "hydrogen.c", "helium.c", "hyrectools.c")],
                   "-lm", "-o", str(lib)]
        result = subprocess.run(command, cwd=cls.src, capture_output=True, text=True, timeout=15)
        if result.returncode:
            raise RuntimeError(result.stderr)
        cls.oracle = v.NativeLowZ(lib, cls.src)
        cls.source = make_hmla_source(m.HyRec2012Cosmology(), OriginalHyRecPrimitiveRateTable.from_archive(v.SOURCE_ZIP))

    @classmethod
    def tearDownClass(cls):
        if v.source_tree_hashes(cls.src) != cls.manifest["compiled_members"]:
            raise AssertionError("original source copy changed during tests")
        cls.temporary.cleanup()

    def test_h2_source_end_grid_and_no_old_h_indices(self):
        assert (m.START_IZ, m.SOURCE_NZ, m.END_IZ, m.MAX_STEPS) == (58389, 211717, 211716, 153327)
        c = m.HyRec2012Cosmology()
        assert c.redshift(m.END_IZ) < 0. < c.redshift(m.END_IZ - 1)
        z0 = m.source_z0_cubic(np.array([1., 2., 3., 4.]))
        assert z0["global_iz"] == [211713, 211714, 211715, 211716]
        assert 1. < z0["fraction"] < 2.


    def test_prev2_predictor_and_two_memory_rotations(self):
        c = m.HyRec2012Cosmology()
        cp = fixture_state()
        values = iter([-.0045, -.0044])

        class Source:
            def hydrogen_rhs_ln_a(self, **kwargs):
                return next(values)

        result = m.continue_refined_low_z(cp, c, Source(), max_steps=2)
        x1 = cp.xe + m.DLNA * (1.25 * -.0045 - .25 * cp.hydrogen_prev2)
        x2 = x1 + m.DLNA * (1.25 * -.0044 - .25 * cp.hydrogen_prev)
        assert result["xe"].tolist() == [cp.xe, x1, x2]
        assert result["checkpoint"].hydrogen_prev == -.0044
        assert result["checkpoint"].hydrogen_prev2 == -.0045
        wrong = cp.xe + m.DLNA * (1.25 * -.0045 - .25 * cp.hydrogen_prev)
        assert result["xe"][1] != wrong
        assert cp == fixture_state()
        assert result["z0"] is None


    def test_rejected_candidate_preserves_original_accepted_memory(self):
        cp = fixture_state()
        events = []

        class BadSource:
            def hydrogen_rhs_ln_a(self, **kwargs):
                return 1.e6

        with self.assertRaisesRegex(ValueError, "ACCEPTED_STATE"):
            m.continue_refined_low_z(cp, m.HyRec2012Cosmology(), BadSource(), max_steps=2,
                                    on_checkpoint=events.append)
        assert events[-1]["phase"] == "EXCEPTION"
        assert events[-1]["accepted_steps"] == 0
        assert events[-1]["checkpoint"] == asdict(cp)


    def test_stop_before_rhs_has_recoverable_checkpoint(self):
        cp = fixture_state()
        events = []

        def stop(_):
            raise v.BudgetStop("test assigned work budget exhausted")

        with self.assertRaises(v.BudgetStop):
            m.continue_refined_low_z(cp, m.HyRec2012Cosmology(), self.source, max_steps=2,
                                    before_attempt=stop, on_checkpoint=events.append)
        assert [e["phase"] for e in events] == ["START", "EXCEPTION"]
        assert events[-1]["checkpoint"] == asdict(cp)


    def test_failed_comparison_retains_actual_accepted_python_step(self):
        events = []

        def reject(*_):
            raise ArithmeticError("independent comparison failed")

        with self.assertRaisesRegex(ArithmeticError, "independent comparison"):
            m.continue_refined_low_z(fixture_state(), m.HyRec2012Cosmology(), self.source,
                                    max_steps=2, on_accept=reject, on_checkpoint=events.append)
        assert events[-1]["accepted_steps"] == 1
        assert events[-1]["checkpoint"]["iz"] == m.START_IZ + 1
        assert events[-1]["checkpoint"]["hydrogen_prev2"] == fixture_state().hydrogen_prev


    def test_exact_guard_threshold_order_against_original_c(self):
        oracle = self.oracle
        c = m.HyRec2012Cosmology()
        threshold = math.floor(math.log(8.617343e-5 * c.T0_K * 8001. / .004) / m.DLNA)
        for iz in (m.START_IZ, threshold - 1, threshold, threshold + 1):
            tr = c.T0_K * (1. + c.redshift(iz))
            for tm in (math.nextafter(.1 * tr, 0.), .1 * tr, math.nextafter(.1 * tr, math.inf), .2 * tr):
                cp = replace(fixture_state(iz), Tm_K=tm)
                assert oracle.guard(cp) == m.source_stage_guard(c, c.redshift(iz), tm)


    def check_original_c_common_input_operator_and_one_step(self, iz, fraction):
        oracle = self.oracle
        c = m.HyRec2012Cosmology()
        cp = fixture_state(iz, fraction)
        cf_model, cf, ct = oracle.rhs(cp)
        result = m.continue_refined_low_z(cp, c, self.source, max_steps=1)
        assert str(result["model"][0]) == cf_model
        assert abs(float(result["hydrogen_rhs"][0]) - cf) / max(abs(cf), 1.e-13) < 3.e-10
        assert abs(float(result["thermal_rhs"][0]) - ct) / max(1., abs(ct)) < 2.e-10
        native_next, model = oracle.step(cp)
        assert model == cf_model
        v.compare_state(result["checkpoint"], native_next, {})


    def test_first_false_guard_and_absorbing_peebles(self):
        oracle = self.oracle
        c = m.HyRec2012Cosmology()

        class ForbiddenEmla:
            def hydrogen_rhs_ln_a(self, **kwargs):
                raise AssertionError("EMLA reentered after original outer loop exited")

        initial = fixture_state(139997, .09)
        first = m.continue_refined_low_z(initial, c, ForbiddenEmla(), max_steps=2)
        assert first["model"].tolist() == ["PEEBLES", "PEEBLES"]
        assert first["checkpoint"].peebles_event_iz == initial.iz
        assert first["checkpoint"].peebles_event_reason == "TM_TR_MIN"
        # Deliberate controlled input with a true current guard tests absorption.
        recovered_guard = replace(fixture_state(139999, .3),
                                  peebles_event_iz=139997, peebles_event_reason="TM_TR_MIN")
        assert oracle.guard(recovered_guard)[0]
        assert oracle.rhs(recovered_guard)[0] == "PEEBLES"
        result = m.continue_refined_low_z(recovered_guard, c, ForbiddenEmla(), max_steps=1)
        assert result["model"].tolist() == ["PEEBLES"]


    def test_transition_is_labeled_by_input_not_output_index(self):
        # Controlled Tm/Tr=.2 keeps the ratio guard true across TR_MIN.
        # This is a two-step source-guard test, not an h2 production result.
        cp = fixture_state(144930, .2)
        native_cp = cp
        compared = []

        def compare(current, candidate, step):
            nonlocal native_cp
            native_cp, model = self.oracle.step(native_cp)
            assert model == step["model"]
            v.compare_state(candidate, native_cp, {})
            compared.append((current.iz, candidate.iz, model))

        result = m.continue_refined_low_z(cp, m.HyRec2012Cosmology(), self.source,
                                         max_steps=2, on_accept=compare)
        assert compared == [(144930, 144931, "EMLA2s2p"), (144931, 144932, "PEEBLES")]
        assert result["checkpoint"].peebles_event_iz == 144931
        assert result["checkpoint"].peebles_event_reason == "TR_MIN"


    def test_standalone_native_cli_build_and_bounded_parser(self):
        binary = self.src.parent / "native_r3o_lowz_cli"
        command = ["gcc", "-std=gnu99", "-O2", "-fno-fast-math", "-ffp-contract=off",
                   "-DR3O_LOWZ_MAIN", "-I", str(self.src), str(v.HARNESS),
                   *[str(self.src / f) for f in ("history.c", "hydrogen.c", "helium.c", "hyrectools.c")],
                   "-lm", "-o", str(binary)]
        built = subprocess.run(command, cwd=self.src, capture_output=True, text=True, timeout=15)
        self.assertEqual(built.returncode, 0, built.stderr)
        cp = fixture_state(144930, .2)
        scalars = [format(getattr(cp, key), ".17g") for key in
                   ("xe", "Tm_K", "hydrogen_prev", "hydrogen_prev2", "thermal_prev", "thermal_prev2")]
        good = [str(binary), str(cp.iz), "2", "0", *scalars]
        result = subprocess.run(good, cwd=self.src, capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [line.split(",") for line in result.stdout.splitlines()]
        self.assertEqual([(p[1], p[2]) for p in rows if p[0] == "STEP"],
                         [("144931", "2"), ("144932", "0")])
        self.assertEqual(rows[-1], ["END", "BOUNDED_LOW_Z_COMPLETE", "144932"])
        for count in ("0", "9999999999999999999999999999999999999", "junk"):
            bad = subprocess.run([str(binary), str(cp.iz), count, "0", *scalars], cwd=self.src,
                                 capture_output=True, text=True, timeout=3)
            self.assertEqual(bad.returncode, 2)


    def check_original_c_global_z0_interpolation_bytes(self, tail):
        oracle = self.oracle
        expected = oracle.z0(tail)
        actual = m.source_z0_cubic(np.array(tail))["value"]
        assert np.float64(actual).tobytes() == np.float64(expected).tobytes()


    def test_no_rhs_evaluation_at_negative_z_final_output(self):
        oracle = self.oracle
        cp = fixture_state(m.END_IZ, .01)
        with self.assertRaisesRegex(ValueError, "STEP_OR_CHECKPOINT_CAP"):
            m.continue_refined_low_z(cp, m.HyRec2012Cosmology(), self.source, max_steps=1)
        with self.assertRaisesRegex(ArithmeticError, "NATIVE_STEP_FAILURE"):
            oracle.step(cp)

    def test_terminal_restart_distinguishes_missing_cubic_stencil(self):
        # Controlled Peebles states reproduce R6-P2-01; no physical late-time
        # trajectory is inferred from these six endpoint updates.
        class NoEmla:
            def hydrogen_rhs_ln_a(self, **kwargs):
                raise AssertionError("unexpected EMLA")

        for count in (1, 2, 3):
            with self.subTest(remaining_steps=count):
                cp = m.LowZCheckpoint(m.END_IZ - count, 1.e-4, .05,
                                      0., 0., -.1, -.1, 144931, "TR_MIN")
                result = m.continue_refined_low_z(
                    cp, m.HyRec2012Cosmology(), NoEmla(), max_steps=count)
                self.assertEqual(result["checkpoint"].iz, m.END_IZ)
                self.assertEqual(result["accepted_steps"], count)
                if count < 3:
                    self.assertEqual(result["status"],
                                     "SOURCE_END_REACHED_INCOMPLETE_Z0_STENCIL")
                    self.assertIsNone(result["z0"])
                else:
                    self.assertEqual(result["status"], "STOP_AT_SOURCE_Z0_CUBIC_STENCIL")
                    for field in ("xe", "Tm_K"):
                        expected = self.oracle.z0(result[field][-4:])
                        actual = result["z0"][field]["value"]
                        self.assertEqual(np.float64(actual).tobytes(),
                                         np.float64(expected).tobytes())


    def test_original_operator_sources_and_isolated_clock_patch(self):
        src, manifest = self.src, self.manifest
        changed = [p for p in manifest["original_members"]
                   if manifest["original_members"][p] != manifest["compiled_members"][p]]
        assert changed == ["hyrec_params.h"]
        assert manifest["compiled_members"]["hyrec_params.h"] == v.H2_HEADER_SHA256
        assert manifest["compiled_members"]["history.c"] == "8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976"
        with self.assertRaises(FileExistsError):
            v.prepare_source(v.SOURCE_ZIP, src)


    def test_reject_tampered_raw_and_preserve_dirty_output(self):
        self.test_temp = tempfile.TemporaryDirectory(prefix="r3o_lowz_contract_")
        self.addCleanup(self.test_temp.cleanup)
        tmp_path = Path(self.test_temp.name)
        raw = tmp_path / "raw"
        raw.mkdir()
        for name in m.R3M_FILES:
            (raw / name).write_bytes(b"not the reviewed original raw")
        with self.assertRaisesRegex(ValueError, "REVIEWED_INPUT_HASH_MISMATCH"):
            m.load_reviewed_u6_boundary(raw, v.SOURCE_ZIP)
        out = v.reserve_output(tmp_path / "evidence")
        sentinel = out / "keep"
        sentinel.write_bytes(b"prior evidence")
        with self.assertRaisesRegex(ValueError, "OUTPUT_EXISTS"):
            v.reserve_output(out)
        assert sentinel.read_bytes() == b"prior evidence"
        with self.assertRaises(FileExistsError):
            v.dump_new(sentinel, {"bad": "overwrite"})
        assert sentinel.read_bytes() == b"prior evidence"


    def check_invalid_checkpoint_is_fail_closed(self, field, value):
        with self.assertRaises(ValueError):
            replace(fixture_state(), **{field: value}).validate(m.HyRec2012Cosmology())



    def test_full_allocation_separate_from_closed_budget(self):
        good = allocation()
        assert v.validate_allocation(good, datetime.now(timezone.utc), {})["cpu_s"] == 120.
        assert m.HISTORICAL_STATUS == {"budget": "CLOSED_HOLD_NOT_RESET", "u5_original_h": "HOLD_9_FAIL",
                                       "u5_h2": "HOLD_8_FAIL", "REI_activation": False}


    def check_full_allocation_rejects_stale_or_unbound_resources(self, field, value):
        record = allocation()
        record[field] = value
        with self.assertRaises(ValueError):
            v.validate_allocation(record, datetime.now(timezone.utc), {})


    def test_measured_budget_includes_active_children(self):
        limits = {"cpu_s": 20., "wall_s": 60., "recovery_cpu_s": 3., "recovery_wall_s": 8.}
        budget = v.ResourceBudget(limits, apply_os_limits=False)
        with patch.object(v, "process_tree_cpu_s", return_value=2.), patch.object(v, "START_WALL", v.time.monotonic()):
            budget.check(live_cpu_s=14.)
            with self.assertRaisesRegex(v.BudgetStop, "AGGREGATE_CPU"):
                budget.check(live_cpu_s=15.)


    def test_current_process_live_cpu_reader_is_finite(self):
        cpu = v.live_child_cpu_s(os.getpid())
        assert math.isfinite(cpu) and cpu >= 0.


    def test_full_rejects_incomplete_or_mutated_smoke(self):
        inputs = {**m.R3M_FILES, "source_zip": m.SOURCE_ZIP_SHA256}
        record = {"status": "SMOKE_PASS_SAME_H_PENDING_REVIEW", "mode": "smoke", "accepted_steps": 16,
                  "source_code_sha256": {}, "inputs_before": inputs, "inputs_after": inputs,
                  "source_copy_unchanged": True, "code_unchanged": True, "failure": None,
                  "same_h": {"compared_steps": 16}, "historical_status": dict(m.HISTORICAL_STATUS)}
        v.validate_smoke(record, {})
        for change in ({"accepted_steps": 15}, {"inputs_after": {}}, {"code_unchanged": False},
                       {"failure": {"type": "BudgetStop"}}, {"source_code_sha256": {"wrong": "code"}}):
            with self.assertRaisesRegex(ValueError, "SMOKE_REQUIRED"):
                v.validate_smoke({**record, **change}, {})

    def test_original_c_common_input_operator_cases(self):
        for iz, fraction in ((58389, .995), (139997, .15), (139997, .09), (211715, .01)):
            with self.subTest(iz=iz, fraction=fraction):
                self.check_original_c_common_input_operator_and_one_step(iz, fraction)

    def test_original_c_z0_byte_cases(self):
        for tail in ([.0002, .00019, .00018, .00017], [1., -7., 11., 1.e-20], [1.e8, 1., -1.e8, 4.]):
            with self.subTest(tail=tail):
                self.check_original_c_global_z0_interpolation_bytes(tail)

    def test_invalid_checkpoints(self):
        for field, value in (("iz", 58389.), ("xe", float("nan")), ("hydrogen_prev2", float("inf")),
                             ("peebles_event_iz", 58389), ("peebles_event_reason", "TR_MIN")):
            with self.subTest(field=field):
                self.check_invalid_checkpoint_is_fail_closed(field, value)

    def test_invalid_allocations(self):
        for field, value in (("allocation_id", "CLOSED_OLD_COST"), ("allow_full_lowz", False),
                             ("dual_review_acknowledged", False), ("source_code_sha256", {"wrong": "code"}),
                             ("recovery_cpu_s", 0.), ("cpu_s", float("nan")),
                             ("expires_at_utc", "2020-01-01T00:00:00+00:00")):
            with self.subTest(field=field):
                self.check_full_allocation_rejects_stale_or_unbound_resources(field, value)

def allocation(code=None):
    now = datetime.now(timezone.utc)
    return {"allocation_id": "TEST_NEW_EXPLICIT_ALLOCATION", "allow_full_lowz": True,
            "parent_coordination_confirmed": True, "dual_review_acknowledged": True,
            "historical_budget_status": "CLOSED_HOLD_NOT_RESET", "source_code_sha256": code or {},
            "issued_at_utc": (now - timedelta(seconds=1)).isoformat(),
            "expires_at_utc": (now + timedelta(hours=1)).isoformat(),
            "cpu_s": 120., "wall_s": 240., "recovery_cpu_s": 10., "recovery_wall_s": 20.,
            "memory_bytes": 2 * 1024**3}



if __name__ == "__main__":
    unittest.main()

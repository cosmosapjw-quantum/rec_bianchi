"""Exercise the paired runner through real integrators with a synthetic source.

This tests orchestration, exact identity and mutation detection. It is not
an actual U5 checkpoint run; physical source snapshots are tested separately.
"""
from dataclasses import replace
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/"src"), str(ROOT/"scripts")]
from compare_r3k_u6_backends import compare_checkpoint
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory import primordial_2012_owned_u6 as owned

spec = importlib.util.spec_from_file_location(
    "r3k_test_source_controls", Path(__file__).with_name("test_owned_flrw_history.py"))
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)


def setup_case(monkeypatch):
    c = HyRec2012Cosmology()
    cp = controls.frozen_synthetic_checkpoint(c)
    source = SimpleNamespace(table=SimpleNamespace(archive_path=controls.ARCHIVE))
    calls = controls.install_source_control(monkeypatch)
    return cp, c, source, calls


def test_pair_driver_runs_both_independent_recurrences(monkeypatch):
    cp, c, source, calls = setup_case(monkeypatch)
    result = compare_checkpoint(cp, c, source, steps=3)
    assert result["status"] == "PASS_BOUNDED_BACKEND_BYTE_EQUIVALENCE"
    assert result["records"]["legacy"]["digest"] == result["records"]["owned"]["digest"]
    assert result["records"]["owned"]["digest"]["accepted_steps"] == 3
    assert len(calls) == 6
    assert result["full_U6"] == "NOT_RUN"
    assert result["same_h_original_C"] == "NOT_TESTED_BY_THIS_RUNNER"
    for invalid in (True, 0, -1, 129, 2.5):
        with pytest.raises(ValueError, match="BOUNDED_PARITY_STEPS"):
            compare_checkpoint(cp, c, source, steps=invalid)
    assert len(calls) == 6


def test_pair_driver_rejects_owned_output_corruption(monkeypatch):
    cp, c, source, _ = setup_case(monkeypatch)
    real = owned.integrate_u6_owned
    def corrupt(*args, **kwargs):
        result = real(*args, **kwargs)
        result.average_virtual[0, -1] = np.nextafter(result.average_virtual[0, -1], np.inf)
        return result
    monkeypatch.setattr(owned, "integrate_u6_owned", corrupt)
    with pytest.raises(ArithmeticError, match="BACKEND_BYTE_MISMATCH"):
        compare_checkpoint(cp, c, source, steps=3)


def test_pair_driver_rejects_caller_checkpoint_mutation(monkeypatch):
    cp, c, source, _ = setup_case(monkeypatch)
    real = owned.integrate_u6_owned
    def corrupt(checkpoint, *args, **kwargs):
        result = real(checkpoint, *args, **kwargs)
        checkpoint["virtual_out"][0, 0] = 1.
        return result
    monkeypatch.setattr(owned, "integrate_u6_owned", corrupt)
    with pytest.raises(ArithmeticError, match="INPUT_CHECKPOINT_MUTATED:owned"):
        compare_checkpoint(cp, c, source, steps=3)


def test_pair_driver_cannot_promote_an_incomplete_interval(monkeypatch):
    cp, c, source, _ = setup_case(monkeypatch)
    real = owned.integrate_u6_owned
    def incomplete(*args, **kwargs):
        result = real(*args, **kwargs)
        return replace(result, steps=result.steps[:-1])
    monkeypatch.setattr(owned, "integrate_u6_owned", incomplete)
    with pytest.raises(ArithmeticError, match="BACKEND_INCOMPLETE_BOUNDED_INTERVAL"):
        compare_checkpoint(cp, c, source, steps=3)

"""Equivalence and corruption checks, not a primordial-history validation."""
from pathlib import Path
from types import SimpleNamespace
import math
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    SOURCE_DLNA, causal_incoming_from_accepted_histories,
)
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from full_bianchi_hyrec.trajectory.owned_flrw_history import OwnedFLRWHistory
from full_bianchi_hyrec.trajectory import primordial_2012_refined_u6_rt_boundary as legacy
from full_bianchi_hyrec.trajectory.primordial_2012_owned_u6 import integrate_u6_owned
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology

ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


@pytest.fixture(scope="module")
def energies():
    return _canonical_twophoton_table(ARCHIVE).energy_eV


def histories(n):
    rng = np.random.default_rng(672)
    return (rng.normal(size=(311, n)) * 1.e-14,
            rng.normal(size=(311, n)) * 1.e-14,
            rng.normal(size=(3, n)) * 1.e-14)


def owner(energies, n=8, h=SOURCE_DLNA/2., extra=3):
    arrays = histories(n)
    obj = OwnedFLRWHistory(energies_eV=energies, z_start=1700., dlna=h,
                          virtual=arrays[0], average=arrays[1], lyman=arrays[2],
                          capacity=n+extra)
    return obj, arrays


@pytest.mark.parametrize("n", [2, 3, 17, 257])
@pytest.mark.parametrize("divisor", [1, 2, 4])
def test_all_313_values_equal_original_gather(energies, n, divisor):
    h = SOURCE_DLNA/divisor
    obj, (v, a, ly) = owner(energies, n, h)
    z = math.expm1(math.log1p(1700.)-n*h)
    ref = causal_incoming_from_accepted_histories(
        energies_eV=energies, virtual_history=v, lyman_history=ly,
        z_start=1700., iz=n, z_face=z, dlna=h, shear_q=0.)
    actual_v, actual_l = obj.incoming(z)
    assert actual_v.tobytes() == ref.virtual_distortion[0].tobytes()
    assert actual_l.tobytes() == ref.lya_lyb_incoming_distortion[0].tobytes()


def test_prefix_inputs_cannot_mutate_owned_history(energies):
    obj, arrays = owner(energies)
    before = [a.copy() for a in obj.readonly_views()]
    for a in arrays:
        a[:] = np.nan
    for a, b in zip(obj.readonly_views(), before):
        np.testing.assert_array_equal(a, b)
        assert not a.flags.writeable
        with pytest.raises(ValueError):
            a[0, 0] = 42.


def test_append_is_atomic_and_capacity_bounded(energies):
    obj, _ = owner(energies, extra=1)
    args = dict(expected_index=8, virtual=np.ones(311),
                average=np.ones(311), lyman=np.ones(3))
    with pytest.raises(ValueError, match="APPEND_SHAPE_OR_NONFINITE"):
        obj.append(**{**args, "lyman": [1., np.nan, 1.]})
    assert obj.accepted_columns == 8
    obj.append(**args)
    assert obj.accepted_columns == 9
    with pytest.raises(ValueError, match="APPEND_INDEX_OR_CAPACITY"):
        obj.append(**args)
    with pytest.raises(ValueError, match="APPEND_INDEX_OR_CAPACITY"):
        obj.append(**{**args, "expected_index": 9})


def test_face_clock_mismatch_and_bad_prefix_rejected(energies):
    obj, (v, a, ly) = owner(energies)
    with pytest.raises(ValueError, match="FACE_CLOCK_MISMATCH"):
        obj.incoming(1700.)
    v[0, 0] = np.inf
    with pytest.raises(ValueError, match="PREFIX_NONFINITE"):
        OwnedFLRWHistory(energies_eV=energies, z_start=1700., dlna=SOURCE_DLNA,
                         virtual=v, average=a, lyman=ly, capacity=9)


def test_incoming_does_not_rescan_owned_prefix(energies, monkeypatch):
    obj, _ = owner(energies, n=1024)
    old = np.isfinite
    seen_sizes = []
    def measured(x, *args, **kwargs):
        seen_sizes.append(np.size(x))
        return old(x, *args, **kwargs)
    monkeypatch.setattr(np, "isfinite", measured)
    obj.incoming(math.expm1(math.log1p(1700.)-1024*SOURCE_DLNA/2.))
    assert seen_sizes and max(seen_sizes) <= 313


def frozen_synthetic_checkpoint(c):
    xe = .005
    z = c.redshift(legacy.START_IZ)
    return {
        "state": {"iz": legacy.START_IZ, "z": z, "xH1s": 1.-xe,
                  "xHII": xe, "xHeII": 0., "xe": xe,
                  "Tm_K": c.T0_K*(1.+z)*.999, "post_saha": False,
                  "branch": "H_ONLY"},
        "rhs_h_tail": legacy.H_RHS_TAIL, "rhs_t_tail": legacy.T_RHS_TAIL,
        "event": {"synthetic_test_only": True},
        "virtual_out": np.zeros((311, legacy.PREFIX_COLUMNS)),
        "average_virtual": np.zeros((311, legacy.PREFIX_COLUMNS)),
        "lyman_out": np.zeros((3, legacy.PREFIX_COLUMNS)),
    }


def install_source_control(monkeypatch):
    calls = []
    def populate(source, **kwargs):
        calls.append(kwargs["z"])
        return SimpleNamespace(
            dxHII_dln_a=-.05, normalized_matrix_residual=1.e-15,
            outgoing_virtual=np.array(kwargs["incoming_virtual"])+1.e-20,
            average_virtual=np.array(kwargs["incoming_virtual"])*.5+1.e-20,
            outgoing_lyman=np.array([2.e-20, 3.e-20, 4.e-20]),
        )
    monkeypatch.setattr(legacy, "populate_original_full_atomic", populate)
    monkeypatch.setattr(legacy, "complete_original_full_atomic", lambda x: x)
    return calls


def test_u6_three_step_recurrence_and_fields_match_legacy(monkeypatch):
    c = HyRec2012Cosmology()
    checkpoint = frozen_synthetic_checkpoint(c)
    source = SimpleNamespace(table=SimpleNamespace(archive_path=ARCHIVE))
    install_source_control(monkeypatch)
    old = legacy.integrate_u6_rt_boundary(checkpoint, c, source, max_extra_accepted=3)
    new = integrate_u6_owned(checkpoint, c, source, max_extra_accepted=3)
    assert old.states == new.states and old.steps == new.steps
    assert old.status == new.status == "HOLD_CAP_BEFORE_RT_BOUNDARY"
    for name in ("virtual_out", "average_virtual", "lyman_out"):
        np.testing.assert_array_equal(getattr(old, name), getattr(new, name))
    assert old.full_evaluations == new.full_evaluations == 3


def test_u6_stops_before_excess_source_call(monkeypatch):
    c = HyRec2012Cosmology()
    checkpoint = frozen_synthetic_checkpoint(c)
    source = SimpleNamespace(table=SimpleNamespace(archive_path=ARCHIVE))
    calls = install_source_control(monkeypatch)
    with pytest.raises(ArithmeticError, match="FULL_SOURCE_OR_CAP"):
        integrate_u6_owned(checkpoint, c, source, max_extra_accepted=2,
                           max_full_evaluations=1)
    assert len(calls) == 1

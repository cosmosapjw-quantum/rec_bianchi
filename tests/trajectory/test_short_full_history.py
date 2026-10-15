"""Bounded HyRec FULL accepted-history integration checks (no native xe replay)."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource
from full_bianchi_hyrec.trajectory.primitive_rates import (
    OriginalHyRecPrimitiveRateTable,
)
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    populate_original_full_atomic, complete_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.short_full_history import (
    integrate_full_h_short_history,
)

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
COSMO = dict(
    h=.6735837, omega_cb=.31242079216478097,
    omega_r_h2=4.1578740068818545e-5,
    omega_de_h2=.3119234221656212,
    omega_b_h2=.02242, y_he_mass=.245, tcmb0_K=2.7255,
)


@pytest.fixture(scope="module")
def model():
    return HMLAFlrwSource(
        **COSMO, table=OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    )


def _run(model, *, steps=11, dlna=SOURCE_DLNA/2):
    return integrate_full_h_short_history(
        model, z_start=900., x_HII_start=.04,
        Tm_start_K=.98*model.tcmb0_K*901,
        steps=steps, dlna=dlna,
    )


def test_accepted_history_has_strict_causal_first_columns(model):
    hist = _run(model)
    assert hist.virtual_out.shape == (311, 11)
    assert hist.lyman_out.shape == (3, 11)
    assert np.all(np.diff(hist.z) < 0)
    assert np.all(hist.matrix_residual < 2e-10)
    assert np.all((hist.x_HII > 0) & (hist.x_HII < 1))
    assert not hist.virtual_out.flags.writeable
    assert not hist.x_HII.flags.writeable
    # Independently evaluate the initial source point with zero *prehistory*.
    native = complete_original_full_atomic(populate_original_full_atomic(
        model, z=900., xHII=.04, xe=.04,
        Tm_K=.98*model.tcmb0_K*901,
        incoming_virtual=np.zeros(311),
        incoming_lyman=np.zeros(2),
    ))
    np.testing.assert_array_equal(hist.virtual_out[:, 0],
                                  native.outgoing_virtual)
    np.testing.assert_array_equal(hist.lyman_out[:, 0],
                                  native.outgoing_lyman)
    assert hist.dx_HII_dln_a[0] == native.dxHII_dln_a
    # Stored changes are physics-generated, not a static fixture.
    assert np.any(hist.virtual_out[:, 0] != 0)
    assert np.any(hist.lyman_out[:, 0] != 0)


def test_no_future_unaccepted_photon_reads(model, monkeypatch):
    import full_bianchi_hyrec.trajectory.short_full_history as module
    original = module.causal_incoming_from_accepted_histories
    actual_indices = []

    def guarded(**kwargs):
        i = kwargs["iz"]
        assert kwargs["virtual_history"].shape == (311, i)
        assert kwargs["lyman_history"].shape == (3, i)
        assert i >= 2
        actual_indices.append(i)
        return original(**kwargs)

    monkeypatch.setattr(module, "causal_incoming_from_accepted_histories",
                        guarded)
    result = _run(model, steps=9)
    assert actual_indices == list(range(2, 9))
    np.testing.assert_allclose(
        np.diff(result.x_HII), .5*SOURCE_DLNA*result.dx_HII_dln_a[:-1],
        rtol=2e-10, atol=3e-17,
    )


def test_thermal_positive_control_and_reproducibility(model):
    h1 = _run(model, steps=9)
    h2 = _run(model, steps=9)
    np.testing.assert_array_equal(h1.x_HII, h2.x_HII)
    np.testing.assert_array_equal(h1.virtual_out, h2.virtual_out)
    assert np.all(h1.Tm_K > 0)
    assert np.all(h1.Tm_K <= model.tcmb0_K*(1+h1.z)*(1+1e-10))
    assert "MANUFACTURED" in h1.initial_boundary
    assert "FIRST_ORDER" in h1.source_mode


def test_bounded_inputs_reject_without_mutating_source(model):
    with pytest.raises(ValueError, match="3..2048"):
        _run(model, steps=2)
    with pytest.raises(ValueError, match="source physical step"):
        _run(model, dlna=SOURCE_DLNA*1.01)
    with pytest.raises(ValueError, match="starting thermodynamic"):
        integrate_full_h_short_history(
            model, z_start=900, x_HII_start=1.2,
            Tm_start_K=2000., steps=3,
        )
    with pytest.raises(ValueError, match="source experiment"):
        integrate_full_h_short_history(
            model, z_start=20, x_HII_start=.04,
            Tm_start_K=50., steps=3,
        )

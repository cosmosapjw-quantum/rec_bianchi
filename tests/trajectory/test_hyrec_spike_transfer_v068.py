import math

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.hyrec_spike_transfer import (
    OriginalHyRecSpikeTransfer,
)


def _spike() -> OriginalHyRecSpikeTransfer:
    return OriginalHyRecSpikeTransfer(
        tau_flrw=12.5,
        f_equilibrium=0.75,
        H_s_inv=4.0e-14,
    )


def test_flrw_directional_optical_depth_reduces_to_canonical_tau():
    spike = _spike()
    assert spike.directional_optical_depth(
        minus_dlognu_dt_s_inv=spike.H_s_inv
    ) == spike.tau_flrw
    assert spike.directional_optical_depth(
        minus_dlognu_dt_s_inv=-0.5 * spike.H_s_inv
    ) == 2.0 * spike.tau_flrw


def test_source_identical_jump_uses_stable_expm1_arithmetic():
    spike = OriginalHyRecSpikeTransfer(
        tau_flrw=1.0e-12,
        f_equilibrium=0.75,
        H_s_inv=4.0e-14,
    )
    result = spike.transfer(
        f_in=0.25,
        minus_dlognu_dt_s_inv=spike.H_s_inv,
    )
    expected = 0.25 + (0.75 - 0.25) * (-math.expm1(-1.0e-12))
    assert result.f_out == expected
    assert result.source_file == "HyRec/hydrogen.c"
    assert 780 in result.source_lines and 789 in result.source_lines


def test_transfer_is_a_convex_combination_for_nonnegative_optical_depth():
    spike = _spike()
    result = spike.transfer(
        f_in=0.1,
        minus_dlognu_dt_s_inv=0.25 * spike.H_s_inv,
    )
    assert 0.1 <= result.f_out <= 0.75
    assert result.transmission >= 0.0
    assert result.absorbed_fraction >= 0.0
    assert result.transmission + result.absorbed_fraction == 1.0


def test_transfer_jvp_matches_central_difference():
    spike = _spike()
    f_in = 0.21
    speed = 1.7 * spike.H_s_inv
    direction = dict(
        d_f_in=-0.17,
        d_f_equilibrium=0.23,
        d_tau_flrw=0.31,
        d_H_s_inv=-0.8e-15,
        d_minus_dlognu_dt_s_inv=0.7e-15,
    )
    analytic = spike.jvp(
        f_in=f_in,
        minus_dlognu_dt_s_inv=speed,
        **direction,
    )

    eps = 1.0e-6
    plus = OriginalHyRecSpikeTransfer(
        tau_flrw=spike.tau_flrw + eps * direction["d_tau_flrw"],
        f_equilibrium=spike.f_equilibrium + eps * direction["d_f_equilibrium"],
        H_s_inv=spike.H_s_inv + eps * direction["d_H_s_inv"],
    ).transfer(
        f_in=f_in + eps * direction["d_f_in"],
        minus_dlognu_dt_s_inv=(
            speed + eps * direction["d_minus_dlognu_dt_s_inv"]
        ),
    ).f_out
    minus = OriginalHyRecSpikeTransfer(
        tau_flrw=spike.tau_flrw - eps * direction["d_tau_flrw"],
        f_equilibrium=spike.f_equilibrium - eps * direction["d_f_equilibrium"],
        H_s_inv=spike.H_s_inv - eps * direction["d_H_s_inv"],
    ).transfer(
        f_in=f_in - eps * direction["d_f_in"],
        minus_dlognu_dt_s_inv=(
            speed - eps * direction["d_minus_dlognu_dt_s_inv"]
        ),
    ).f_out
    finite_difference = (plus - minus) / (2.0 * eps)
    assert np.isclose(analytic, finite_difference, rtol=2.0e-8, atol=2.0e-10)


def test_zero_frequency_speed_fails_closed_for_event_localization():
    with pytest.raises(ValueError, match="frequency-speed zero"):
        _spike().transfer(f_in=0.2, minus_dlognu_dt_s_inv=0.0)

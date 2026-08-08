import math

import numpy as np

from full_bianchi_hyrec.trajectory.hyrec_source_adapter import (
    IsotropicEinsteinLineSource,
    OriginalHyRecVirtualSpikeSource,
)


def test_virtual_spike_adapter_reproduces_canonical_flrw_update_for_all_tau_scales():
    tau = np.array([0.0, 1.0e-14, 1.0e-7, 0.3, 30.0])
    equilibrium = np.array([-0.2, 0.1, 0.4, 0.8, 1.2])
    incoming = np.array([0.5, -0.1, 0.2, 0.3, 0.7])
    source = OriginalHyRecVirtualSpikeSource(
        tau_flrw=tau,
        equilibrium_departure=equilibrium,
        H_s_inv=4.2e-14,
    )
    outgoing = source.apply(
        incoming=incoming,
        minus_dlognu_dt_s_inv=np.full_like(tau, source.H_s_inv),
    )
    expected = incoming + (equilibrium - incoming) * (-np.expm1(-tau))
    assert np.array_equal(outgoing, expected)
    assert source.source_file == "HyRec/hydrogen.c"
    assert set((521, 524, 525, 780, 787, 789)).issubset(source.source_lines)


def test_virtual_spike_directional_scaling_and_jvp():
    source = OriginalHyRecVirtualSpikeSource(
        tau_flrw=np.array([0.2, 1.3, 8.0]),
        equilibrium_departure=np.array([0.4, -0.2, 0.9]),
        H_s_inv=3.0e-14,
    )
    incoming = np.array([0.1, 0.3, 0.2])
    speed = np.array([1.5, -0.7, 2.2]) * source.H_s_inv
    direction = dict(
        d_incoming=np.array([0.11, -0.17, 0.05]),
        d_equilibrium_departure=np.array([-0.04, 0.13, 0.09]),
        d_tau_flrw=np.array([0.03, -0.07, 0.2]),
        d_H_s_inv=-0.4e-15,
        d_minus_dlognu_dt_s_inv=np.array([0.2, -0.1, 0.3]) * 1.0e-15,
    )
    analytic = source.jvp(incoming=incoming, minus_dlognu_dt_s_inv=speed, **direction)
    eps = 1.0e-6
    plus = OriginalHyRecVirtualSpikeSource(
        tau_flrw=source.tau_flrw + eps * direction["d_tau_flrw"],
        equilibrium_departure=(
            source.equilibrium_departure
            + eps * direction["d_equilibrium_departure"]
        ),
        H_s_inv=source.H_s_inv + eps * direction["d_H_s_inv"],
    ).apply(
        incoming=incoming + eps * direction["d_incoming"],
        minus_dlognu_dt_s_inv=(
            speed + eps * direction["d_minus_dlognu_dt_s_inv"]
        ),
    )
    minus = OriginalHyRecVirtualSpikeSource(
        tau_flrw=source.tau_flrw - eps * direction["d_tau_flrw"],
        equilibrium_departure=(
            source.equilibrium_departure
            - eps * direction["d_equilibrium_departure"]
        ),
        H_s_inv=source.H_s_inv - eps * direction["d_H_s_inv"],
    ).apply(
        incoming=incoming - eps * direction["d_incoming"],
        minus_dlognu_dt_s_inv=(
            speed - eps * direction["d_minus_dlognu_dt_s_inv"]
        ),
    )
    finite_difference = (plus - minus) / (2.0 * eps)
    assert np.allclose(analytic, finite_difference, rtol=3e-8, atol=3e-10)


def test_einstein_line_source_has_planck_lte_null_and_positive_paired_rates():
    temperature = 3000.0
    frequency = 2.4660677e15
    z = math.exp(-6.62607015e-34 * frequency / (1.380649e-23 * temperature))
    g_upper, g_lower = 3.0, 1.0
    x_lower = 0.8
    x_upper = (g_upper / g_lower) * x_lower * z
    source = IsotropicEinsteinLineSource(
        A_ul_s_inv=6.265e8,
        profile_Hz_inv=2.0e-12,
        frequency_Hz=frequency,
        nH_m3=2.5e8,
        upper_population=x_upper,
        lower_population=x_lower,
        upper_degeneracy=g_upper,
        lower_degeneracy=g_lower,
    )
    planck = z / (1.0 - z)
    action = source.occupation_action(planck)
    scale = source.emission_s_inv * (1.0 + planck)
    assert source.emission_s_inv >= 0.0
    assert source.absorption_s_inv >= 0.0
    assert abs(action) / scale < 5.0e-15
    assert source.affine_opacity_s_inv > 0.0


def test_isotropic_angular_deposition_uses_normalized_weights_without_extra_angle_factor():
    source = IsotropicEinsteinLineSource(
        A_ul_s_inv=1.0,
        profile_Hz_inv=1.0e-12,
        frequency_Hz=2.0e15,
        nH_m3=3.0e8,
        upper_population=0.2,
        lower_population=0.7,
        upper_degeneracy=3.0,
        lower_degeneracy=1.0,
    )
    weights = np.array([0.1, 0.2, 0.3, 0.4])
    occupation = np.array([0.02, 0.04, 0.06, 0.08])
    directional = source.directional_action(occupation)
    integrated = float(np.sum(weights * directional))
    expected = source.occupation_action(float(np.sum(weights * occupation)))
    assert np.isclose(integrated, expected, rtol=2e-15, atol=0.0)

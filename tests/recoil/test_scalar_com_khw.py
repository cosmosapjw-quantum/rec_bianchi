from pathlib import Path
import numpy as np
from scipy.constants import c, physical_constants

from full_bianchi_hyrec.recoil.event import scatter_elastic
from full_bianchi_hyrec.recoil.event_weight import pt_reverse_kinematics
from full_bianchi_hyrec.recoil.four_vector import (
    atom_four_momentum,
    photon_four_momentum,
)
from full_bianchi_hyrec.recoil.pair_cell_conductance import (
    dnu,
    exact_amp2,
    nu_abs,
)
from full_bianchi_hyrec.recoil.scalar_com_khw import (
    LY_ALPHA_OSCILLATOR_STRENGTH,
    RYDBERG_FREQUENCY_HZ,
    bound_oscillator_strength,
    compile_oscillator_strength_measure,
    compile_smooth_background_series,
    conditional_full_minus_provisional_mean_amplitude_squared,
    conditional_full_scalar_mean_amplitude_squared,
    conditional_provisional_mean_amplitude_squared,
    default_scalar_com_khw_model,
    denominator_reciprocity_residuals,
    direct_smooth_background,
    fixed_nucleus_length_gauge_amplitude,
    scalar_com_khw_amplitude,
    scalar_event_com_khw_amplitude,
    smooth_background_polynomial,
)

M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
NU_ALPHA = c / (1215.6701e-10)


def test_positive_bound_continuum_measure_closes_trk_and_static_alpha():
    measure = compile_oscillator_strength_measure(512, 256)
    lower_order = compile_oscillator_strength_measure(512, 128)

    assert abs(float(bound_oscillator_strength(2)) - LY_ALPHA_OSCILLATOR_STRENGTH) < 2e-15
    assert np.min(measure.oscillator_weights) > 0.0
    assert abs(measure.trk_sum - 1.0) < 8e-15
    assert abs(measure.static_polarizability_a0_cubed - 4.5) < 8e-14
    assert 0.0 < measure.tail_weight < 5e-6
    assert 0.999 < measure.tail_delta_rydberg < 1.0
    assert abs(
        lower_order.raw_continuum_quadrature_sum
        / measure.raw_continuum_quadrature_sum
        - 1.0
    ) < 2e-14


def test_fixed_nucleus_velocity_length_gauge_identity_and_ir_power():
    for fraction in (1e-3, 1e-2, 0.1, 0.5, 0.7):
        frequency = fraction * RYDBERG_FREQUENCY_HZ
        velocity = scalar_com_khw_amplitude(
            frequency, frequency, include_2p_width=False
        ).real
        length = fixed_nucleus_length_gauge_amplitude(frequency)
        assert abs(velocity - length) / abs(length) < 2e-9

    q = 2e-5
    first = abs(
        scalar_com_khw_amplitude(
            q * RYDBERG_FREQUENCY_HZ,
            q * RYDBERG_FREQUENCY_HZ,
            include_2p_width=False,
        )
    )
    second = abs(
        scalar_com_khw_amplitude(
            2.0 * q * RYDBERG_FREQUENCY_HZ,
            2.0 * q * RYDBERG_FREQUENCY_HZ,
            include_2p_width=False,
        )
    )
    assert abs(second / first - 4.0) < 2e-6
    assert abs((second / first) ** 2 - 16.0) < 2e-5


def test_compiled_smooth_background_matches_direct_positive_measure():
    model = default_scalar_com_khw_model()
    A = np.asarray([-4.0, -1.0, 0.0, 3.0]) * dnu
    B = np.asarray([2.0, 0.5, 1.5, 2.0]) * dnu
    C = 2.0 * model.measure.nu_alpha_hz + np.asarray([-3.0, 1.0, 0.0, 4.0]) * dnu
    D = -B

    production = compile_smooth_background_series(4)
    reference = compile_smooth_background_series(8)
    production_coeff = smooth_background_polynomial(A, B, C, D, series=production)
    reference_coeff = smooth_background_polynomial(A, B, C, D, series=reference)

    max_production_residual = 0.0
    max_reference_residual = 0.0
    for z_value in (-8.0, -3.0, 0.0, 2.0, 8.0):
        direct = direct_smooth_background(A, B, C, D, z_value)
        compiled_production = sum(
            production_coeff[power] * z_value**power
            for power in range(production.order + 1)
        )
        compiled_reference = sum(
            reference_coeff[power] * z_value**power
            for power in range(reference.order + 1)
        )
        max_production_residual = max(
            max_production_residual,
            float(np.max(np.abs(compiled_production / direct - 1.0))),
        )
        max_reference_residual = max(
            max_reference_residual,
            float(np.max(np.abs(compiled_reference / direct - 1.0))),
        )

    assert max_production_residual < 5e-12
    assert max_reference_residual < 8e-15


def test_relativistic_state_denominators_are_pt_reciprocal_for_recoil_event():
    atom = atom_four_momentum(M_H, np.asarray([2.0e-5, -1.0e-5, 0.5e-5]))
    photon = photon_four_momentum(
        1.00003 * NU_ALPHA, np.asarray([0.3, -0.4, 0.8])
    )
    event = scatter_elastic(atom, photon, np.asarray([-0.7, 0.2, 0.5]), M_H)
    reverse = pt_reverse_kinematics(event)

    residuals = denominator_reciprocity_residuals(
        event.P_i,
        event.k_i,
        event.k_f,
        reverse.P_i,
        reverse.k_i,
        reverse.k_f,
        M_H,
    )
    forward = scalar_event_com_khw_amplitude(
        event.P_i, event.k_i, event.k_f, M_H
    )
    backward = scalar_event_com_khw_amplitude(
        reverse.P_i, reverse.k_i, reverse.k_f, M_H
    )

    # Float64 recoil-event reconstruction is a diagnostic gate; the PR-03
    # stage also rebuilds the same event at arbitrary precision.
    assert max(residuals) < 5e-10
    assert abs(forward - backward) / max(abs(forward), abs(backward)) < 5e-10



def test_complete_minus_provisional_control_variate_is_subtraction_free():
    A = np.asarray([-4.0, -0.2, 2.5]) * dnu
    B = np.asarray([0.4, 1.2, 0.8]) * dnu
    C = 2.0 * NU_ALPHA + np.asarray([-1.0, 0.5, 3.0]) * dnu
    D = -B
    full = conditional_full_scalar_mean_amplitude_squared(A, B, C, D)
    provisional = conditional_provisional_mean_amplitude_squared(A, B, C, D)
    correction = conditional_full_minus_provisional_mean_amplitude_squared(
        A, B, C, D
    )
    assert np.max(np.abs((provisional + correction) / full - 1.0)) < 2e-14
    assert np.any(correction != 0.0)

def test_full_and_provisional_lanes_are_explicit_positive_and_nonidentical():
    nu_source = nu_abs - 3.0 * dnu
    nu_target = nu_abs + 2.0 * dnu
    full = float(exact_amp2(nu_source, nu_target, -0.8, amplitude_lane="full"))
    provisional = float(
        exact_amp2(
            nu_source,
            nu_target,
            -0.8,
            amplitude_lane="provisional_2p",
        )
    )

    assert full > 0.0
    assert provisional > 0.0
    assert 1e-10 < abs(full / provisional - 1.0) < 1e-5

    # The expensive pair re-integration is part of the PR-03 scientific
    # stage. Compact CI verifies the same full/provisional pair in the
    # immutable v0.50 production network.
    data_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "full_scalar_com_khw_v050.npz"
    )
    with np.load(data_path, allow_pickle=False) as data:
        full_pair = data["pair_moments_m3_sInv"][:3, 4, 12]
        provisional_pair = data["provisional_pair_moments_m3_sInv"][:3, 4, 12]
    assert np.all(np.isfinite(full_pair))
    assert full_pair[0] > 0.0
    relative = np.linalg.norm(full_pair - provisional_pair) / np.linalg.norm(
        provisional_pair
    )
    assert 1e-14 < relative < 1e-7

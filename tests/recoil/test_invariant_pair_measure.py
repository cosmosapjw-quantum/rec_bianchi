import numpy as np
from scipy.constants import c, h, k, physical_constants

from full_bianchi_hyrec.recoil.invariant_pair_measure import (
    invariant_pair_conductance_log,
    maxwell_boltzmann_structure_factor,
    maxwell_juttner_structure_factor,
    photon_pair_invariants,
)


M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
NU_ALPHA = c / (1215.6701e-10)
T = 3000.0


def test_relativistic_structure_factor_has_exact_thermal_reciprocity():
    nu_b = NU_ALPHA * (1.0 + 1.2e-4)
    nu_a = NU_ALPHA * (1.0 - 0.8e-4)
    mu = 0.23

    invariants = photon_pair_invariants(nu_b, nu_a, mu, M_H)
    forward = maxwell_juttner_structure_factor(
        invariants.q_dimensionless,
        invariants.delta_dimensionless,
        M_H,
        T,
    )
    reverse = maxwell_juttner_structure_factor(
        invariants.q_dimensionless,
        -invariants.delta_dimensionless,
        M_H,
        T,
    )
    expected_ratio = np.exp(
        -(h * (nu_b - nu_a)) / (k * T)
    )

    assert abs(reverse / forward / expected_ratio - 1.0) < 5e-13


def test_pair_conductance_log_is_symmetric_before_matrix_assembly():
    nu_b = NU_ALPHA * (1.0 + 7.0e-5)
    nu_a = NU_ALPHA * (1.0 - 4.0e-5)
    mu = -0.47

    forward = invariant_pair_conductance_log(
        nu_source_hz=nu_b,
        nu_target_hz=nu_a,
        mu=mu,
        mass_kg=M_H,
        temperature_K=T,
        amplitude_average=1.2345,
    )
    reverse = invariant_pair_conductance_log(
        nu_source_hz=nu_a,
        nu_target_hz=nu_b,
        mu=mu,
        mass_kg=M_H,
        temperature_K=T,
        amplitude_average=1.2345,
    )

    assert abs(forward - reverse) < 5e-13


def test_relativistic_structure_factor_reduces_to_nonrelativistic_mb():
    # Scale both photon momentum transfer and energy transfer toward zero
    # while keeping the nonrelativistic resonance coordinate fixed.
    for scale in (1e-3, 3e-4, 1e-4):
        q = scale
        delta = 0.4 * q * np.sqrt(k * T / (M_H * c**2))
        relativistic = maxwell_juttner_structure_factor(
            q, delta, M_H, T
        )
        nonrelativistic = maxwell_boltzmann_structure_factor(
            q, delta, M_H, T
        )
        assert abs(relativistic / nonrelativistic - 1.0) < 3e-4


def test_rejects_non_spacelike_photon_transfer():
    with np.testing.assert_raises(ValueError):
        maxwell_juttner_structure_factor(
            q_dimensionless=1e-6,
            delta_dimensionless=2e-6,
            mass_kg=M_H,
            temperature_K=T,
        )

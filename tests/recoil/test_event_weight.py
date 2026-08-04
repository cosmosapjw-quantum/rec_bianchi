import numpy as np
from scipy.constants import c, physical_constants

from full_bianchi_hyrec.recoil.event import scatter_elastic
from full_bianchi_hyrec.recoil.event_weight import (
    Scalar2PPoleModel,
    audit_pt_detailed_balance,
    audit_pt_detailed_balance_high_precision,
    equilibrium_conductance_log,
    invariant_2p_response_area,
    pt_reverse_kinematics,
    stable_atom_kinetic_energy,
)
from full_bianchi_hyrec.recoil.four_vector import (
    atom_four_momentum,
    photon_four_momentum,
)

M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
NU_ALPHA = c / (1215.6701e-10)
MODEL = Scalar2PPoleModel.ly_alpha()


def make_event(beta, nu_factor=1.0):
    atom = atom_four_momentum(M_H, np.asarray(beta, dtype=float))
    photon = photon_four_momentum(
        nu_factor * NU_ALPHA,
        np.array([0.3, -0.4, 0.8]),
    )
    return scatter_elastic(
        atom,
        photon,
        np.array([-0.7, 0.2, 0.5]),
        M_H,
    )


def test_pt_reverse_preserves_scalar_2p_response():
    event = make_event([0.22, -0.12, 0.09], 1.00003)
    reverse = pt_reverse_kinematics(event)

    forward_area = invariant_2p_response_area(event.P_i, event.k_i, event.k_f, M_H, MODEL)
    reverse_area = invariant_2p_response_area(reverse.P_i, reverse.k_i, reverse.k_f, M_H, MODEL)

    assert forward_area > 0.0
    assert abs(forward_area / reverse_area - 1.0) < 2e-13


def test_maxwell_juttner_equilibrium_conductance_is_pt_invariant():
    event = make_event([0.18, 0.07, -0.11], 0.99997)
    audit = audit_pt_detailed_balance(event, M_H, 3000.0, MODEL)
    high_precision = audit_pt_detailed_balance_high_precision(
        event, M_H, 3000.0, MODEL, dps=80
    )

    # Float64 is retained as a diagnostic; the narrow resonant pole can
    # amplify its last-bit detuning error.  The hard gate is independent
    # arbitrary-precision forward/reverse evaluation.
    assert abs(audit["thermal_log_residual"]) < 1e-7
    assert high_precision["response_relative"] < 1e-60
    assert abs(high_precision["thermal_log_residual"]) < 1e-60
    assert abs(high_precision["conductance_log_residual"]) < 1e-60
    assert audit["maxwell_boltzmann_log_residual"] != 0.0


def test_stable_kinetic_energy_matches_gamma_minus_one():
    beta = np.array([0.42, -0.07, 0.12])
    momentum = atom_four_momentum(M_H, beta)
    gamma = 1.0 / np.sqrt(1.0 - beta @ beta)
    expected = (gamma - 1.0) * M_H * c**2

    assert abs(stable_atom_kinetic_energy(momentum, M_H) / expected - 1.0) < 3e-15


def test_random_physical_maxwellian_events_pass_pair_balance():
    rng = np.random.default_rng(20260803)
    sigma_beta = np.sqrt(1.380649e-23 * 3000.0 / M_H) / c

    for _ in range(80):
        beta = rng.normal(size=3) * sigma_beta
        atom = atom_four_momentum(M_H, beta)
        direction_in = rng.normal(size=3)
        direction_out = rng.normal(size=3)
        photon = photon_four_momentum(
            rng.uniform(0.9999, 1.0001) * NU_ALPHA,
            direction_in,
        )
        event = scatter_elastic(atom, photon, direction_out, M_H)
        audit = audit_pt_detailed_balance(event, M_H, 3000.0, MODEL)

        assert audit["rest_frequency_in_relative"] < 2e-15
        assert audit["rest_frequency_out_relative"] < 2e-15
        assert abs(audit["conductance_log_residual"]) < 1e-8

    # A smaller independent sample receives the hard arbitrary-precision gate.
    rng = np.random.default_rng(20260804)
    for _ in range(8):
        beta = rng.normal(size=3) * sigma_beta
        atom = atom_four_momentum(M_H, beta)
        photon = photon_four_momentum(
            rng.uniform(0.9999, 1.0001) * NU_ALPHA,
            rng.normal(size=3),
        )
        event = scatter_elastic(atom, photon, rng.normal(size=3), M_H)
        audit = audit_pt_detailed_balance_high_precision(
            event, M_H, 3000.0, MODEL, dps=70
        )
        assert audit["response_relative"] < 1e-50
        assert abs(audit["conductance_log_residual"]) < 1e-50

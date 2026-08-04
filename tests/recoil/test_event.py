import numpy as np
from scipy.constants import c, h, physical_constants

from full_bianchi_hyrec.recoil.event import (
    event_residuals,
    scatter_elastic,
)
from full_bianchi_hyrec.recoil.four_vector import (
    atom_four_momentum,
    photon_four_momentum,
)


M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
NU_ALPHA = c / (1215.6701e-10)


def test_rest_atom_exact_backscatter_frequency():
    atom = atom_four_momentum(M_H, np.zeros(3))
    photon = photon_four_momentum(NU_ALPHA, np.array([0.0, 0.0, 1.0]))

    event = scatter_elastic(
        atom,
        photon,
        np.array([0.0, 0.0, -1.0]),
        M_H,
    )

    epsilon = h * NU_ALPHA / (M_H * c**2)
    expected = NU_ALPHA / (1.0 + 2.0 * epsilon)

    assert abs(event.nu_out_rest_hz / expected - 1.0) < 2e-15
    assert abs(event.mu_rest + 1.0) < 1e-15

    residuals = event_residuals(event, M_H)
    assert residuals["four_momentum_relative"] < 1e-14
    assert residuals["initial_mass_shell_relative"] < 1e-14
    assert residuals["final_mass_shell_relative"] < 2e-12
    assert residuals["incoming_null_absolute"] < 1e-68
    assert residuals["outgoing_null_absolute"] < 1e-68


def test_moving_atom_random_events_preserve_invariants():
    rng = np.random.default_rng(20260803)

    for _ in range(40):
        beta = rng.normal(size=3)
        beta *= rng.uniform(0.0, 0.45) / np.linalg.norm(beta)

        incoming_direction = rng.normal(size=3)
        outgoing_rest_direction = rng.normal(size=3)

        atom = atom_four_momentum(M_H, beta)
        photon = photon_four_momentum(
            rng.uniform(0.7, 1.4) * NU_ALPHA,
            incoming_direction,
        )
        event = scatter_elastic(
            atom,
            photon,
            outgoing_rest_direction,
            M_H,
        )
        residuals = event_residuals(event, M_H)

        assert residuals["four_momentum_relative"] < 2e-14
        assert residuals["initial_mass_shell_relative"] < 1e-14
        assert residuals["final_mass_shell_relative"] < 5e-12
        assert event.nu_out_rest_hz > 0.0

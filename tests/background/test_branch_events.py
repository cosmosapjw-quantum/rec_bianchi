import numpy as np

from full_bianchi_hyrec.background.branch_events import (
    boundary_ledger,
    piecewise_linear_roots,
)


def test_piecewise_linear_roots_finds_repeated_crossing():
    times = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    values = np.array([-1.0, 1.0, -2.0, 2.0, -1.0])
    roots = piecewise_linear_roots(times, values)

    assert np.allclose(roots, [0.5, 4.0 / 3.0, 2.5, 11.0 / 3.0])


def test_red_blue_crossing_ledger_closes_number_and_four_momentum():
    times = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    red_speed = np.array([-1.0, 1.0, -2.0, 2.0, -1.0])
    blue_speed = -0.7 * red_speed

    ledger = boundary_ledger(
        times,
        red_speed,
        blue_speed,
        interior_occupation=1.3,
        red_occupation=0.7,
        blue_occupation=0.9,
        red_photon_four=np.array([1.0, 0.0, 0.0, -1.0]),
        blue_photon_four=np.array([1.0, 0.0, 0.0, 1.0]),
    )

    assert len(ledger.red_roots) == 4
    assert len(ledger.blue_roots) == 4
    assert abs(ledger.number_residual) < 1e-14
    assert np.max(np.abs(ledger.four_momentum_residual)) < 1e-14
    assert ledger.total_absolute_flux > 0.0

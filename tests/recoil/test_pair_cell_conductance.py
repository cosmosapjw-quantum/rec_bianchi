import numpy as np

from full_bianchi_hyrec.recoil.pair_cell_conductance import (
    integrate_unordered_pair,
    pointwise_hummer_limit_ratio,
)


def test_pointwise_no_recoil_limit_matches_hummer():
    samples = [
        (-0.5, 0.5, 0.0),
        (-1.0, 1.0, -0.5),
        (1.0, 2.0, 0.7),
        (2.0, -2.0, 0.2),
    ]
    for x_target, x_source, mu in samples:
        ratio = pointwise_hummer_limit_ratio(x_target, x_source, mu)
        assert abs(ratio - 1.0) < 2e-7


def test_unordered_pair_is_orientation_independent():
    forward = integrate_unordered_pair(7, 9, lane="production")
    reverse = integrate_unordered_pair(9, 7, lane="production")
    assert np.linalg.norm(forward - reverse) / np.linalg.norm(forward) < 2e-13


def test_selected_pair_quadrature_converges():
    production = integrate_unordered_pair(4, 12, lane="production")
    reference = integrate_unordered_pair(4, 12, lane="reference")
    assert np.linalg.norm(production - reference) / np.linalg.norm(reference) < 1e-8


def test_scalar_offdiagonal_conductance_is_positive():
    for pair in ((8, 9), (7, 9), (4, 12), (0, 1), (0, 8)):
        value = integrate_unordered_pair(*pair, lane="production")
        assert value[0] > 0.0

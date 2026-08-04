import numpy as np
from scipy.constants import c, k, physical_constants

from full_bianchi_hyrec.recoil.mj_orbit_reweight import (
    mj_to_mb_log_ratio,
    reweight_symmetric_conductance,
    generator_from_conductance,
)

M_H = physical_constants['atomic mass constant'][0] * 1.00782503223
T = 3000.0


def test_mj_mb_ratio_is_reciprocity_even():
    q = 2.4e-8
    delta = 3.1e-13
    forward = mj_to_mb_log_ratio(q, delta, M_H, T)
    reverse = mj_to_mb_log_ratio(q, -delta, M_H, T)
    assert abs(forward - reverse) < 5e-13


def test_reweight_preserves_symmetry_and_positivity():
    S = np.array([[0.0, 2.0, 1.0], [2.0, 0.0, 3.0], [1.0, 3.0, 0.0]])
    factors = np.array([[1.0, 1.01, 0.99], [1.01, 1.0, 1.02], [0.99, 1.02, 1.0]])
    out = reweight_symmetric_conductance(S, factors)
    assert np.all(out >= 0.0)
    assert np.max(np.abs(out - out.T)) == 0.0


def test_generator_has_number_and_equilibrium_nulls():
    S = np.array([[0.0, 2.0, 1.0], [2.0, 0.0, 3.0], [1.0, 3.0, 0.0]])
    Pi = np.array([0.8, 1.0, 0.9])
    G = generator_from_conductance(S, Pi)
    assert np.max(np.abs(np.ones(3) @ G)) < 1e-14
    assert np.max(np.abs(G @ Pi)) < 1e-14

import numpy as np
import pytest
from scipy.constants import c, h, physical_constants

from full_bianchi_hyrec.recoil.four_vector import (
    atom_beta,
    atom_four_momentum,
    boost_four_momentum,
    inverse_boost_four_momentum,
    minkowski_dot,
    photon_four_momentum,
)


M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
NU_ALPHA = c / (1215.6701e-10)


def test_photon_four_momentum_is_null():
    direction = np.array([2.0, -1.0, 3.0])
    momentum = photon_four_momentum(NU_ALPHA, direction)

    assert abs(minkowski_dot(momentum, momentum)) < 1e-68
    assert np.isclose(np.linalg.norm(momentum[1:]) / momentum[0], 1.0)


def test_atom_four_momentum_has_mass_shell_and_recovers_beta():
    beta = np.array([0.21, -0.08, 0.13])
    momentum = atom_four_momentum(M_H, beta)

    shell = minkowski_dot(momentum, momentum)
    target = -(M_H * c) ** 2

    assert abs(shell - target) / abs(target) < 5e-15
    assert np.linalg.norm(atom_beta(momentum) - beta) < 5e-15


def test_lorentz_boost_round_trip():
    beta = np.array([0.31, 0.07, -0.11])
    photon = photon_four_momentum(
        1.37 * NU_ALPHA, np.array([1.0, 2.0, -0.5])
    )

    rest = boost_four_momentum(photon, beta)
    recovered = inverse_boost_four_momentum(rest, beta)

    assert np.linalg.norm(recovered - photon) / np.linalg.norm(photon) < 2e-15
    assert abs(minkowski_dot(rest, rest)) < 1e-68


def test_rejects_superluminal_beta():
    with pytest.raises(ValueError, match=r"\|beta\|"):
        atom_four_momentum(M_H, np.array([1.0, 0.0, 0.0]))

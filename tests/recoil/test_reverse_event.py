import numpy as np
from scipy.constants import c, physical_constants

from full_bianchi_hyrec.recoil.event import (
    reconstruct_reverse,
    reverse_residuals,
    scatter_elastic,
)
from full_bianchi_hyrec.recoil.four_vector import (
    atom_four_momentum,
    photon_four_momentum,
)


M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
NU_ALPHA = c / (1215.6701e-10)


def test_reverse_event_recovers_initial_atom_and_photon():
    atom = atom_four_momentum(M_H, np.array([0.22, -0.12, 0.09]))
    photon = photon_four_momentum(
        1.11 * NU_ALPHA, np.array([0.3, -0.4, 0.8])
    )

    forward = scatter_elastic(
        atom,
        photon,
        np.array([-0.7, 0.2, 0.5]),
        M_H,
    )
    reverse = reconstruct_reverse(forward, M_H)
    residuals = reverse_residuals(forward, reverse)

    assert residuals["photon_relative"] < 2e-11
    assert residuals["atom_relative"] < 2e-11
    assert residuals["reverse_four_momentum_relative"] < 2e-14

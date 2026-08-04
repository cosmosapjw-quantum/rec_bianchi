import numpy as np
from scipy.constants import c, physical_constants

from full_bianchi_hyrec.recoil.event import scatter_elastic
from full_bianchi_hyrec.recoil.four_force import (
    event_transfer,
    four_force,
)
from full_bianchi_hyrec.recoil.four_vector import (
    atom_four_momentum,
    photon_four_momentum,
)


M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
NU_ALPHA = c / (1215.6701e-10)


def test_same_event_transfer_cancels_exactly():
    atom = atom_four_momentum(M_H, np.zeros(3))
    photon = photon_four_momentum(NU_ALPHA, np.array([0.0, 0.0, 1.0]))
    event = scatter_elastic(
        atom, photon, np.array([1.0, 0.0, 0.0]), M_H
    )

    delta_gamma, delta_atom = event_transfer(event)

    assert np.linalg.norm(delta_gamma + delta_atom) == 0.0
    assert delta_atom[0] > 0.0


def test_four_force_uses_same_event_ledger():
    atom = atom_four_momentum(M_H, np.array([0.08, 0.02, -0.03]))
    photon = photon_four_momentum(
        0.93 * NU_ALPHA, np.array([0.4, 0.1, 0.7])
    )
    event = scatter_elastic(
        atom, photon, np.array([-0.2, 0.9, 0.3]), M_H
    )

    q_gamma, q_atom = four_force(2.5e7, event)

    assert np.linalg.norm(q_gamma + q_atom) == 0.0

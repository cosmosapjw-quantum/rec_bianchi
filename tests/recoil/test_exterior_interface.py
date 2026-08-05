import numpy as np

from full_bianchi_hyrec.recoil.exterior_interface import (
    BLUE_CELLS,
    RED_CELLS,
    assemble_scalar_interface_generator,
    exterior_pair_conductance,
    physical_equilibrium_interval_weight,
    same_event_four_force_coefficients,
)
from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC


def test_selected_exterior_pair_is_orientation_independent():
    target = RED_CELLS[-1]
    source = (float(PCC.xedges[0]), float(PCC.xedges[1]))
    forward = exterior_pair_conductance(target, source, lane="coarse", ell_max=4)
    reverse = exterior_pair_conductance(source, target, lane="coarse", ell_max=4)
    assert np.linalg.norm(forward - reverse) / np.linalg.norm(forward) < 2e-12


def test_scalar_exterior_conductance_is_positive():
    pairs = [
        (RED_CELLS[-1], (float(PCC.xedges[0]), float(PCC.xedges[1]))),
        (BLUE_CELLS[0], (float(PCC.xedges[-2]), float(PCC.xedges[-1]))),
        (RED_CELLS[0], (float(PCC.xedges[8]), float(PCC.xedges[9]))),
    ]
    for target, source in pairs:
        value = exterior_pair_conductance(target, source, lane="coarse", ell_max=2)
        assert value[0] > 0.0


def test_selected_exterior_quadrature_converges():
    target = BLUE_CELLS[1]
    source = (float(PCC.xedges[12]), float(PCC.xedges[13]))
    production = exterior_pair_conductance(
        target, source, lane="production", ell_max=3, amplitude_lane="provisional_2p"
    )
    reference = exterior_pair_conductance(
        target, source, lane="reference", ell_max=3, amplitude_lane="provisional_2p"
    )
    assert np.linalg.norm(production - reference) / np.linalg.norm(reference) < 2e-7


def test_scalar_interface_generator_preserves_number_and_thermal_state():
    interior_pi = np.asarray([2.0, 3.0])
    exterior_pi = np.asarray([5.0, 7.0])
    conductance = np.asarray([[0.4, 0.2], [0.1, 0.3]])
    generator = assemble_scalar_interface_generator(
        conductance,
        interior_pi=interior_pi,
        exterior_pi=exterior_pi,
    )
    equilibrium = np.concatenate([interior_pi, exterior_pi])
    assert np.max(np.abs(np.ones(4) @ generator)) < 1e-15
    assert np.max(np.abs(generator @ equilibrium)) < 1e-15


def test_same_event_four_force_coefficients_cancel():
    source = (float(PCC.xedges[8]), float(PCC.xedges[9]))
    target = BLUE_CELLS[0]
    photon, hydrogen = same_event_four_force_coefficients(
        target, source, lane="coarse"
    )
    assert photon.shape == (2,)
    assert np.linalg.norm(photon + hydrogen) == 0.0
    assert physical_equilibrium_interval_weight(*target) > 0.0


def test_general_interval_measure_matches_locked_interior_pair():
    target_index, source_index = 7, 9
    target = (float(PCC.xedges[target_index]), float(PCC.xedges[target_index + 1]))
    source = (float(PCC.xedges[source_index]), float(PCC.xedges[source_index + 1]))
    # This is a geometric/common-measure identity, so compact CI uses the
    # analytic provisional lane. Full-amplitude parity is closed by the
    # immutable PR-03 selected-pair audit.
    generalized = exterior_pair_conductance(
        target,
        source,
        lane="production",
        ell_max=4,
        amplitude_lane="provisional_2p",
    )
    from full_bianchi_hyrec.recoil.pair_cell_conductance import integrate_unordered_pair
    raw = integrate_unordered_pair(
        target_index,
        source_index,
        lane="production",
        ell_max=4,
        amplitude_lane="provisional_2p",
    )
    factor = 8.0 * np.pi * PCC.dnu / PCC.c**3
    locked = factor * raw
    assert np.linalg.norm(generalized - locked) / np.linalg.norm(locked) < 2e-10

import numpy as np

from full_bianchi_hyrec.recoil.same_cell_regular import (
    assemble_from_same_cell_rates,
    integrate_hummer_same_cell_audit,
    integrate_same_cell_regularized,
)


def test_scalar_regularized_same_cell_is_exactly_zero():
    value = integrate_same_cell_regularized(8, lane="production", ell_max=12)
    assert value[0] == 0.0


def test_same_cell_regularized_coefficients_are_nonpositive():
    for cell in (0, 4, 8, 12, 16):
        value = integrate_same_cell_regularized(cell, lane="production", ell_max=24)
        assert np.all(value[1:] <= 1e-18)


def test_same_cell_selected_quadrature_converges():
    cell = 0
    production = integrate_same_cell_regularized(cell, lane="production", ell_max=12)
    reference = integrate_same_cell_regularized(cell, lane="reference", ell_max=12)
    scale = np.linalg.norm(reference[1:])
    assert np.linalg.norm(production[1:] - reference[1:]) / scale < 2e-7


def test_no_recoil_hummer_same_cell_matches_v032_reference():
    data = np.load(
        "/mnt/data/Full_Bianchi_HyRec_C3B2B1C_finite_volume_ellmax_v0_32/"
        "finite_volume_legendre_kernel.npz"
    )
    gain = data["physical_gain_sInv"]
    cell = 8
    calculated = integrate_hummer_same_cell_audit(
        cell, lane="reference", ell_max=12
    )
    target = gain[:13, cell, cell] - gain[0, cell, cell]
    assert np.linalg.norm(calculated[1:] - target[1:]) / np.linalg.norm(target[1:]) < 3e-6


def test_bounded_operator_algebra_preserves_scalar_number_and_equilibrium():
    data = np.load(
        "/mnt/data/Full_Bianchi_HyRec_C3B2B1C_finite_volume_ellmax_v0_32/"
        "finite_volume_legendre_kernel.npz"
    )
    gain = data["physical_gain_sInv"][:7]
    baseline = np.zeros((7, 17))
    for cell in range(17):
        baseline[:, cell] = gain[:, cell, cell] - gain[0, cell, cell]
    assembled = assemble_from_same_cell_rates(baseline)
    operators = assembled["collision_matrices_sInv"]
    pi = assembled["equilibrium_weight_m3"]

    assert np.max(np.abs(np.ones(len(pi)) @ operators[0])) < 1e-12
    assert np.max(np.abs(operators[0] @ pi)) / (
        np.max(np.abs(operators[0])) * np.max(pi)
    ) < 1e-12
    assert np.all(np.diagonal(operators[1:], axis1=1, axis2=2) < 0.0)

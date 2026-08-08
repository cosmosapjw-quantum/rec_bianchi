from __future__ import annotations

import numpy as np

from full_bianchi_hyrec.theory.pr05c2c0_closure import (
    be_occupation,
    bose_edge_flux,
    bose_edge_pair_dissipation,
    entropy_metric_graph,
    geometric_conductance_interpolate,
    limited_linear_traces,
    piecewise_constant_transfer,
    w_orthogonal_projectors,
)


def test_bose_edge_contract_conserves_number_has_be_null_and_dissipates() -> None:
    zi, zj, conductance = 0.21, 0.13, 3.4
    fi, fj = 0.37, 0.82
    flux = bose_edge_flux(fi, fj, zi=zi, zj=zj, conductance=conductance)
    assert np.isclose(flux + bose_edge_flux(fj, fi, zi=zj, zj=zi, conductance=conductance), 0.0)
    assert bose_edge_pair_dissipation(fi, fj, zi=zi, zj=zj, conductance=conductance) <= 0.0
    assert bose_edge_flux(0.0, fj, zi=zi, zj=zj, conductance=conductance) >= 0.0

    activity = 0.7
    fi_be = be_occupation(zi, activity)
    fj_be = be_occupation(zj, activity)
    assert abs(bose_edge_flux(fi_be, fj_be, zi=zi, zj=zj, conductance=conductance)) < 1e-14


def test_geometric_interpolation_preserves_positive_reciprocal_graph_and_jvp() -> None:
    left = np.asarray([[0.0, 2.0, 4.0], [2.0, 0.0, 3.0], [4.0, 3.0, 0.0]])
    right = np.asarray([[0.0, 8.0, 1.0], [8.0, 0.0, 12.0], [1.0, 12.0, 0.0]])
    value, derivative = geometric_conductance_interpolate(left, right, fraction=0.3, coordinate_span=0.4)
    assert np.array_equal(value, value.T)
    assert np.array_equal(derivative, derivative.T)
    assert np.all(value[np.triu_indices(3, 1)] > 0.0)
    assert np.all(np.diag(value) == 0.0)

    step = 1e-7
    plus, _ = geometric_conductance_interpolate(left, right, fraction=0.3 + step, coordinate_span=0.4)
    minus, _ = geometric_conductance_interpolate(left, right, fraction=0.3 - step, coordinate_span=0.4)
    fd = (plus - minus) / (2 * step * 0.4)
    assert np.max(np.abs(fd - derivative)) / np.max(np.abs(derivative)) < 1e-8


def test_geometric_interpolation_rejects_topology_changes_inside_a_cell() -> None:
    left = np.asarray([[0.0, 1.0], [1.0, 0.0]])
    right = np.zeros((2, 2))
    try:
        geometric_conductance_interpolate(left, right, fraction=0.5, coordinate_span=1.0)
    except ValueError as error:
        assert "topology" in str(error).lower()
    else:
        raise AssertionError("active-graph topology change must fail closed")


def test_piecewise_constant_characteristic_transfer_is_positive_and_exact() -> None:
    initial = 0.12
    emissivity = np.asarray([0.4, 0.1, 0.3])
    opacity = np.asarray([2.0, 0.0, 0.7])
    dt = np.asarray([0.2, 0.4, 0.3])
    result = piecewise_constant_transfer(initial, emissivity, opacity, dt)
    assert result > 0.0

    # Independent scalar recurrence is the exact solution for piecewise constants.
    expected = initial
    for eta, chi, width in zip(emissivity, opacity, dt, strict=True):
        if chi == 0.0:
            expected += eta * width
        else:
            attenuation = np.exp(-chi * width)
            expected = attenuation * expected + eta * (1.0 - attenuation) / chi
    assert np.isclose(result, expected, rtol=2e-15, atol=0.0)


def test_entropy_metric_graph_is_psd_and_has_constant_activity_nullspace() -> None:
    conductance = np.asarray(
        [[0.0, 2.0, 1.0], [2.0, 0.0, 4.0], [1.0, 4.0, 0.0]]
    )
    equilibrium = np.asarray([0.2, 0.7, 1.1])
    mode = np.asarray([3.0, 2.0, 5.0])
    graph = entropy_metric_graph(conductance, equilibrium, mode)
    assert np.max(np.abs(graph.laplacian @ np.ones(3))) < 1e-14
    assert np.min(np.linalg.eigvalsh(graph.laplacian)) > -1e-13
    assert np.all(graph.entropy_mass > 0.0)

    projector, complement = w_orthogonal_projectors(graph.entropy_mass)
    assert np.max(np.abs(projector @ projector - projector)) < 1e-14
    assert np.max(np.abs(complement @ complement - complement)) < 1e-14
    assert np.max(np.abs(projector @ complement)) < 1e-14
    assert np.max(np.abs(complement @ np.ones(3))) < 1e-14


def test_entropy_metric_preconditioner_bound_is_stiffness_independent() -> None:
    conductance = np.asarray(
        [[0.0, 2.0, 1.0], [2.0, 0.0, 4.0], [1.0, 4.0, 0.0]]
    )
    equilibrium = np.asarray([0.2, 0.7, 1.1])
    mode = np.asarray([3.0, 2.0, 5.0])
    graph = entropy_metric_graph(conductance, equilibrium, mode)
    # A deliberately imperfect but spectrally equivalent graph approximation.
    approximate = entropy_metric_graph(1.7 * conductance, equilibrium, mode).laplacian
    W = np.diag(graph.entropy_mass)
    for stiffness in (1.0, 1e4, 1e12):
        operator = W + stiffness * graph.laplacian
        preconditioner = W + stiffness * approximate
        eigenvalues = np.linalg.eigvals(np.linalg.solve(preconditioner, operator)).real
        condition = float(np.max(eigenvalues) / np.min(eigenvalues))
        assert condition < 1.71


def test_scaled_muscl_traces_preserve_average_positivity_and_local_bounds() -> None:
    faces = np.asarray([0.0, 0.4, 1.0, 1.8, 2.5])
    averages = np.asarray([0.3, 0.5, 0.12, 0.4])
    traces = limited_linear_traces(averages, faces, epsilon=1e-14)
    assert np.min(traces.left) >= 1e-14
    assert np.min(traces.right) >= 1e-14
    centers = 0.5 * (faces[:-1] + faces[1:])
    for index in range(len(averages)):
        width_left = centers[index] - faces[index]
        width_right = faces[index + 1] - centers[index]
        reconstructed_average = (
            width_right * traces.left[index] + width_left * traces.right[index]
        ) / (width_left + width_right)
        assert np.isclose(reconstructed_average, averages[index], rtol=0.0, atol=2e-15)
        lo = max(index - 1, 0)
        hi = min(index + 2, len(averages))
        assert traces.left[index] >= np.min(averages[lo:hi]) - 1e-14
        assert traces.right[index] >= np.min(averages[lo:hi]) - 1e-14
        assert traces.left[index] <= np.max(averages[lo:hi]) + 1e-14
        assert traces.right[index] <= np.max(averages[lo:hi]) + 1e-14

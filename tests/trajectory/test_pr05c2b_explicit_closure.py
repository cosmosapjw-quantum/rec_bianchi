from __future__ import annotations

from pathlib import Path

import numpy as np

from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid, apply_nonlinear_bose_operator
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork, LineBoundaryConfig
from full_bianchi_hyrec.trajectory.explicit_full_coupling import (
    ExplicitThermodynamicNetworkFamily,
    isotropic_native_lift,
    maximum_entropy_native_lift,
    reconstruct_frequency_faces,
)
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import CoupledCollisionTransportProblem
from full_bianchi_hyrec.recoil.frequency_liouville import ConservativeFrequencyLiouville

ROOT = Path(__file__).resolve().parents[2]
NETWORK = ROOT / "data/full_scalar_com_khw_v050.npz"


def octahedral_grid() -> HarmonicGrid:
    directions = np.asarray(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ]
    )
    return HarmonicGrid.from_directions(directions, np.full(6, 1 / 6), ell_max=1)


def test_positive_angular_closures_preserve_monopole_and_report_noncanonical_momentum() -> None:
    grid = octahedral_grid()
    scalar = 0.2
    isotropic = isotropic_native_lift(scalar, grid)
    positive = maximum_entropy_native_lift(
        scalar,
        grid,
        axis=np.asarray([1.0, 0.0, 0.0]),
        reduced_flux=0.05,
    )
    negative = maximum_entropy_native_lift(
        scalar,
        grid,
        axis=np.asarray([-1.0, 0.0, 0.0]),
        reduced_flux=0.05,
    )
    assert isotropic.monopole_residual == 0.0
    assert np.linalg.norm(isotropic.momentum_vector) < 1e-15
    assert positive.minimum_occupation > 0.0
    assert abs(positive.monopole - scalar) < 2e-15
    assert abs(positive.reduced_flux - 0.05) < 2e-13
    assert np.linalg.norm(positive.momentum_vector + negative.momentum_vector) < 2e-14
    assert positive.source_identical_directional_reconstruction is False
    assert positive.classification == "EXPLICIT_NONCANONICAL_CLOSURE_UNCERTAINTY"


def test_thermodynamic_network_family_has_exact_reference_limit_and_be_null() -> None:
    reference = CollisionNetwork.from_npz(NETWORK)
    family = ExplicitThermodynamicNetworkFamily(reference)
    locked = family.compile(temperature_K=3000.0, nH_m3=2.5e8)
    assert np.array_equal(locked.network.mode_measure, reference.mode_measure)
    assert np.array_equal(locked.network.equilibrium_weight, reference.equilibrium_weight)
    assert np.array_equal(locked.network.pair_moments, reference.pair_moments)
    assert np.array_equal(locked.network.same_cell_rates, reference.same_cell_rates)
    assert locked.reference_limit_exact

    source = family.compile(temperature_K=2458.0, nH_m3=1.8e8)
    assert source.no_fitted_normalization
    assert source.source_identical_recompilation is False
    assert np.all(source.network.mode_measure > 0.0)
    assert np.all(source.network.equilibrium_weight > 0.0)
    assert np.min(source.network.pair_moments[0]) >= 0.0
    assert np.array_equal(source.network.pair_moments, np.swapaxes(source.network.pair_moments, 1, 2))

    grid = octahedral_grid()
    z = source.network.equilibrium_weight / source.network.mode_measure
    occupation = (z / (1.0 - z))[:, None] * np.ones((1, grid.n_angle))
    result = apply_nonlinear_bose_operator(
        occupation,
        mode_measure=source.network.mode_measure,
        equilibrium_weight=source.network.equilibrium_weight,
        pair_moments=source.network.pair_moments,
        same_cell_rates=source.network.same_cell_rates,
        grid=grid,
    )
    scale = max(result.gross_action_scale, 1e-300)
    assert np.max(np.abs(result.number_action)) / scale < 2e-12
    assert abs(result.number_residual) / scale < 2e-12


def _face_error(n_cell: int, method: str) -> tuple[float, bool, float]:
    faces = np.linspace(-1.0, 1.0, n_cell + 1)
    centers = 0.5 * (faces[:-1] + faces[1:])
    values = 0.8 + 0.1 * np.sin(1.7 * centers) + 0.03 * centers**2
    reconstruction = reconstruct_frequency_faces(values, faces, method=method)
    exact = 0.8 + 0.1 * np.sin(1.7 * faces[1:-1]) + 0.03 * faces[1:-1] ** 2
    # Compare both one-sided traces with the same smooth exact face value.
    error = max(
        float(np.max(np.abs(reconstruction.left_trace[1:-1] - exact))),
        float(np.max(np.abs(reconstruction.right_trace[1:-1] - exact))),
    )
    return error, reconstruction.creates_new_extrema, reconstruction.minimum_trace


def test_limited_muscl_face_reconstruction_is_positive_monotone_and_second_order() -> None:
    p0_34, p0_extrema, _ = _face_error(34, "p0")
    p0_68, _, _ = _face_error(68, "p0")
    muscl_34, muscl_extrema, min_34 = _face_error(34, "muscl")
    muscl_68, _, min_68 = _face_error(68, "muscl")
    assert p0_34 / p0_68 > 1.8
    assert muscl_34 / muscl_68 > 3.2
    assert muscl_68 < p0_68
    assert not p0_extrema
    assert not muscl_extrema
    assert min(min_34, min_68) > 0.0


def _small_problem() -> tuple[CoupledCollisionTransportProblem, np.ndarray]:
    reference = CollisionNetwork.from_npz(NETWORK)
    # Keep only three states for a cheap dense-Jacobian regression.
    index = np.asarray([0, 1, 2])
    pair = reference.pair_moments[:2][:, index][:, :, index]
    same = reference.same_cell_rates[:2, index]
    network = CollisionNetwork(
        state_intervals=reference.state_intervals[index],
        state_labels=reference.state_labels[index],
        pair_moments=pair,
        same_cell_rates=same,
        mode_measure=reference.mode_measure[index],
        equilibrium_weight=reference.equilibrium_weight[index],
        momentum_scale=reference.momentum_scale[index],
        inherited_release_policy={"test": 1},
    )
    grid = octahedral_grid()
    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=3000.0,
        x_red=float(np.min(network.state_intervals[:, 0])),
        x_blue=float(np.max(network.state_intervals[:, 1])),
    )
    transport = ConservativeFrequencyLiouville.from_network(network, reference_line=line)
    speeds = np.zeros((network.n_state + 1, grid.n_angle))
    z = network.equilibrium_weight / network.mode_measure
    old = (z / (1.0 - z))[:, None] * (1.0 + 1e-5 * grid.directions[:, 0][None, :])
    problem = CoupledCollisionTransportProblem(
        network=network,
        grid=grid,
        transport=transport,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=old[0],
        native_blue_occupation=old[-1],
        dt_s=1e3,
    )
    return problem, old


def test_chunked_batched_dense_jacobian_matches_scalar_column_assembly() -> None:
    problem, old = _small_problem()
    log_state = np.log(old)
    scalar = problem.dense_jacobian(log_state, method="scalar_columns")
    batched = problem.dense_jacobian(log_state, method="batched", chunk_size=5)
    relative = np.max(np.abs(scalar - batched)) / max(np.max(np.abs(scalar)), 1e-300)
    assert relative < 2e-13

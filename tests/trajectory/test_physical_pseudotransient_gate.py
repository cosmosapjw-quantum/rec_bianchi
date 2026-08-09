from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from full_bianchi_hyrec.background import BackgroundSnapshotSequence
from full_bianchi_hyrec.recoil.frequency_liouville import ConservativeFrequencyLiouville
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.direct_thermodynamic import load_direct_network_node
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
    CoupledCollisionTransportProblem,
)
from full_bianchi_hyrec.trajectory.physical_continuation import (
    CoupledPhysicalContinuationAdapter,
)
from full_bianchi_hyrec.trajectory.pseudotransient_continuation import (
    AcceptedContinuationState,
    PseudoTransientTolerances,
    _physical_backward_error,
    solve_pseudotransient,
)


ROOT = Path(__file__).resolve().parents[2]


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _tiny_parent(value: float) -> AcceptedContinuationState:
    return AcceptedContinuationState(
        values=np.asarray([value]),
        positive_mask=np.asarray([True]),
        accepted_history_count=1,
        history_sha256=_digest("tiny-history"),
        background_sha256=_digest("tiny-background"),
        network_sha256=_digest("tiny-network"),
        interface_sha256=_digest("tiny-interface"),
        branch_id="TINY_STIFF_SCALAR",
    )


def _z1100_bianchi_ii_adapter() -> CoupledPhysicalContinuationAdapter:
    node = load_direct_network_node(ROOT / "data/z1100_direct_network_node.npz")
    network = node.network
    with np.load(ROOT / "data/pr01c_background_snapshots_v048.npz", allow_pickle=False) as data:
        grid = HarmonicGrid.from_directions(
            data["directions"], data["angular_weights"], ell_max=3
        )
    source = parse_original_hyrec_boundary_snapshot_csv(
        ROOT
        / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
        / "pr04c_z1100.csv"
    )
    red, blue = source.boundaries
    sequence = BackgroundSnapshotSequence.from_npz(
        ROOT / "data/pr01c_background_snapshots_v048.npz",
        "Bianchi_II_large_shear",
    )
    snapshot = sequence.snapshot_at_tau(
        0.6072662349590596,
        H_s_inv_override=source.trajectory.H_s_inv,
    )
    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=node.temperature_K,
        x_red=-21.25,
        x_blue=21.25,
    )
    transport = ConservativeFrequencyLiouville.from_network(
        network,
        reference_line=line,
    )
    speeds = transport.face_speeds_from_snapshot(snapshot, grid=grid, line=line)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    parent = scalar[:, None] * (
        1.0 + 1.0e-5 * grid.directions[:, 0][None, :]
    )
    canonical_dt_s = 8.49e-5 / source.trajectory.H_s_inv
    problem = CoupledCollisionTransportProblem(
        network=network,
        grid=grid,
        transport=transport,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=red.total_occupation,
        native_blue_occupation=blue.total_occupation,
        dt_s=canonical_dt_s,
    )
    return CoupledPhysicalContinuationAdapter(problem, parent)


def test_tiny_stiff_nonroot_is_not_false_zero_iteration_convergence() -> None:
    parent = _tiny_parent(1.0e-18)
    target = 2.0e-18
    rate = 1.0e20

    def residual(state: np.ndarray) -> np.ndarray:
        return np.asarray([rate * (state[0] - target)])

    def jacobian(state: np.ndarray) -> np.ndarray:
        del state
        return np.asarray([[rate]])

    result = solve_pseudotransient(
        parent,
        residual=residual,
        jacobian=jacobian,
        mass_diagonal=np.asarray([1.0]),
        tolerances=PseudoTransientTolerances(
            physical_residual=1.0e-10,
            pseudo_backward_error=1.0e-11,
            newton_residual=1.0e-11,
            initial_pseudo_time=1.0e-20,
            minimum_pseudo_time=1.0e-24,
            maximum_outer_steps=80,
            maximum_pseudo_time=1.0e6,
        ),
    )
    assert result.converged
    assert len(result.iterations) > 0
    assert np.allclose(result.state_values, np.asarray([target]), rtol=1.0e-10)


def test_z1100_bianchi_ii_parent_fails_physical_macro_acceptance_gate() -> None:
    adapter = _z1100_bianchi_ii_adapter()
    assessment = adapter.assess(adapter.parent_occupation.ravel())
    assert assessment.gross_backward_error > 0.9
    assert assessment.number_relative_residual > 0.9
    assert assessment.convergence_metric > 0.9
    assert not assessment.passed(tolerance=1.0e-11)


def test_z1100_bianchi_ii_physical_jvp_matches_central_difference() -> None:
    adapter = _z1100_bianchi_ii_adapter()
    state = adapter.parent_occupation.ravel()
    rng = np.random.default_rng(20260809)
    relative_direction = rng.normal(size=state.size)
    relative_direction /= np.max(np.abs(relative_direction))
    direction = state * relative_direction
    analytic = adapter.jvp(state, direction)
    epsilon = 2.0e-5
    finite = (
        adapter.residual(state + epsilon * direction)
        - adapter.residual(state - epsilon * direction)
    ) / (2.0 * epsilon)
    scale = max(
        float(np.max(np.abs(analytic))),
        float(np.max(np.abs(finite))),
        1.0e-300,
    )
    relative = float(np.max(np.abs(analytic - finite))) / scale
    assert relative < 1.0e-8


def test_shifted_matrix_free_jvp_matches_pseudo_equation_difference() -> None:
    adapter = _z1100_bianchi_ii_adapter()
    old = adapter.parent_occupation.ravel()
    state = old * (1.0 + 5.0e-7)
    rng = np.random.default_rng(104729)
    relative_direction = rng.normal(size=state.size)
    relative_direction /= np.max(np.abs(relative_direction))
    direction = state * relative_direction
    pseudo_time = 1.0e-6
    analytic = adapter.shifted_jvp(
        state,
        direction,
        old_state=old,
        pseudo_time=pseudo_time,
        mass_diagonal=np.ones(state.size),
    )
    epsilon = 1.0e-5
    finite = (
        adapter.pseudo_equation(
            state + epsilon * direction,
            old_state=old,
            pseudo_time=pseudo_time,
            mass_diagonal=np.ones(state.size),
        )
        - adapter.pseudo_equation(
            state - epsilon * direction,
            old_state=old,
            pseudo_time=pseudo_time,
            mass_diagonal=np.ones(state.size),
        )
    ) / (2.0 * epsilon)
    scale = max(
        float(np.max(np.abs(analytic))),
        float(np.max(np.abs(finite))),
        1.0e-300,
    )
    relative = float(np.max(np.abs(analytic - finite))) / scale
    assert relative < 1.0e-8


def test_problem_specific_metric_can_block_generic_root_acceptance() -> None:
    parent = _tiny_parent(2.0)

    def residual(state: np.ndarray) -> np.ndarray:
        return state - 2.0

    def jacobian(state: np.ndarray) -> np.ndarray:
        del state
        return np.asarray([[1.0]])

    result = solve_pseudotransient(
        parent,
        residual=residual,
        jacobian=jacobian,
        mass_diagonal=np.asarray([1.0]),
        convergence_metric=lambda state: 1.0,
        tolerances=PseudoTransientTolerances(maximum_outer_steps=2),
    )
    assert not result.converged
    assert result.final_physical_residual == 1.0


def test_corrected_backward_error_is_invariant_to_variable_rescaling() -> None:
    physical_state = np.asarray([1.0e-18])
    physical_residual = np.asarray([-1.0e2])
    physical_jacobian = np.asarray([[1.0e20]])
    physical_error = _physical_backward_error(
        physical_residual, physical_state, physical_jacobian
    )

    unit_scale = 1.0e-18
    scaled_state = physical_state / unit_scale
    scaled_residual = physical_residual / unit_scale
    scaled_jacobian = physical_jacobian
    scaled_error = _physical_backward_error(
        scaled_residual, scaled_state, scaled_jacobian
    )

    assert np.isclose(physical_error, 1.0)
    assert np.isclose(scaled_error, physical_error, rtol=5.0e-15)


def test_shifted_linear_operator_matches_analytic_shifted_jvp() -> None:
    adapter = _z1100_bianchi_ii_adapter()
    old = adapter.parent_occupation.ravel()
    state = old * (1.0 + 2.0e-7)
    direction = state * np.linspace(-1.0, 1.0, state.size)
    mass = np.ones(state.size)
    pseudo_time = 3.0e-6
    operator = adapter.shifted_linear_operator(
        state,
        old_state=old,
        pseudo_time=pseudo_time,
        mass_diagonal=mass,
    )
    expected = adapter.shifted_jvp(
        state,
        direction,
        old_state=old,
        pseudo_time=pseudo_time,
        mass_diagonal=mass,
    )
    assert np.allclose(operator @ direction, expected, rtol=5.0e-14, atol=0.0)

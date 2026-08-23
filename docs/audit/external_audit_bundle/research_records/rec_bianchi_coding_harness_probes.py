from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import runpy

import mpmath as mp
import numpy as np
from scipy.integrate import solve_ivp

import full_bianchi_hyrec.trajectory as trajectory
from full_bianchi_hyrec.background.branch_events import piecewise_linear_roots
from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence
from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.recoil.frequency_liouville import ConservativeFrequencyLiouville
from full_bianchi_hyrec.trajectory.causal_history import (
    AcceptedRadiationHistory,
    CharacteristicHistoryGrid,
    CharacteristicInterpolationStencil,
    CharacteristicStencilSwitch,
    HistoryAppendCandidate,
)
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    BianchiCharacteristicFaceSolver,
    constant_coefficient_transfer_jvp,
)
from full_bianchi_hyrec.trajectory.entropy_preconditioner import EntropyGraphPreconditioner
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import CoupledCollisionTransportProblem
from full_bianchi_hyrec.trajectory.primitive_trajectory import audit_native_m_matrix
from full_bianchi_hyrec.trajectory.pseudotransient_continuation import (
    AcceptedContinuationState,
    ContinuationTransaction,
    PseudoTransientIteration,
    PseudoTransientResult,
    _physical_backward_error,
    project_left_nullspace,
)


ROOT = Path("/home/cosmosapjw/Dropbox/bianchi/rec_bianchi")


def emit(name: str, **payload: object) -> None:
    print(json.dumps({"probe": name, **payload}, sort_keys=True, allow_nan=False))


def exc_text(callable_) -> str:
    try:
        callable_()
    except Exception as exc:  # probe records the exact public failure class/message
        return f"{type(exc).__name__}: {exc}"
    return "NO_EXCEPTION"


def history(n: int = 2, dlna: float = 1.0e-3) -> AcceptedRadiationHistory:
    eta0 = -8.0
    return AcceptedRadiationHistory(
        grid=CharacteristicHistoryGrid(
            eta=eta0 + dlna * np.arange(n),
            source_indices=np.arange(n),
            z_start=np.exp(-eta0) - 1.0,
            dlna=dlna,
            energy_eV=np.linspace(5.0, 12.7, 311),
            source_hashes={"source": "1" * 64},
        ),
        outgoing_virtual=np.zeros((311, n)),
        outgoing_lyman=np.zeros((3, n)),
        average_virtual=np.zeros((311, n)),
        completeness="SYNTHETIC_FULL",
    )


@dataclass(frozen=True)
class Step:
    state_vector: np.ndarray
    converged: bool = True
    backward_error: float = 0.0
    algebraic_residual_relative: float = 0.0
    minimum_physical_population: float = 1.0


def candidate(parent: AcceptedRadiationHistory, values=(42.0, 43.0, 44.0)) -> HistoryAppendCandidate:
    return HistoryAppendCandidate(
        accepted_index=parent.accepted_count,
        eta=parent.grid.eta[-1] + parent.grid.dlna,
        outgoing_virtual=np.full(311, values[0]),
        outgoing_lyman=np.full(3, values[1]),
        average_virtual=np.full(311, values[2]),
        parent_sha256=parent.sha256,
    )


def context(parent: AcceptedRadiationHistory, *, state=(1.0, 2.0), step=1.0e-3,
            minimum=1.0e-3, maximum=1.0e-3, events=()) -> trajectory.AdaptiveTrajectoryContext:
    return trajectory.AdaptiveTrajectoryContext(
        eta=parent.grid.eta[-1],
        state_vector=np.asarray(state, dtype=float),
        accepted_history=parent,
        controller_step=step,
        tolerances=trajectory.AdaptiveControllerTolerances.scalar(
            size=len(state), absolute=1.0, relative=0.0,
            minimum_step=minimum, maximum_step=maximum,
        ),
        events=tuple(events),
        background_label="probe",
    )


def x2() -> None:
    parent = history()
    calls: list[tuple[float, list[float]]] = []

    def nonlinear_step(state: np.ndarray, h: float) -> Step:
        out = np.asarray(state) + h + h * h
        calls.append((h, out.tolist()))
        return Step(out)

    updated, ledger = trajectory.advance_canonical_macro_interval(
        context(parent), stepper=nonlinear_step, candidate_factory=candidate
    )
    full = nonlinear_step(np.asarray([1.0, 2.0]), 1.0e-3).state_vector
    half1 = nonlinear_step(np.asarray([1.0, 2.0]), 0.5e-3).state_vector
    half2 = nonlinear_step(half1, 0.5e-3).state_vector
    emit(
        "X2_FINE_STATE",
        returned=updated.state_vector.tolist(),
        full=full.tolist(),
        two_half=half2.tolist(),
        returned_is_full=bool(np.array_equal(updated.state_vector, full)),
        returned_is_two_half=bool(np.array_equal(updated.state_vector, half2)),
        history_tail=[
            float(updated.accepted_history.outgoing_virtual[0, -1]),
            float(updated.accepted_history.outgoing_lyman[0, -1]),
            float(updated.accepted_history.average_virtual[0, -1]),
        ],
        commit_count=ledger.commit_count,
    )

    failure_widths: list[float] = []

    def failed_step(state: np.ndarray, h: float) -> Step:
        failure_widths.append(h)
        return Step(np.array(state, copy=True), converged=False)

    failure = exc_text(
        lambda: trajectory.advance_canonical_macro_interval(
            context(parent, step=8.0e-4, minimum=1.0e-4, maximum=1.0e-3),
            stepper=failed_step,
            candidate_factory=candidate,
            maximum_attempts=3,
        )
    )
    emit("X2_FAILURE_SHRINK", widths=failure_widths, failure=failure)

    root = float(parent.grid.eta[-1] + parent.grid.dlna / 20.0)
    event = trajectory.AdaptiveEvent(
        kind=trajectory.AdaptiveEventKind.BOUNDARY_SPEED_ZERO,
        eta=root,
        label="inside-hmin",
    )
    event_failure = exc_text(
        lambda: trajectory.advance_canonical_macro_interval(
            context(parent, state=(1.0, 2.0), step=1.0e-3, minimum=1.0e-4,
                    maximum=1.0e-3, events=(event,)),
            stepper=lambda state, h: Step(np.array(state, copy=True)),
            candidate_factory=candidate,
        )
    )
    emit("X2_EVENT_INSIDE_HMIN", root=root, failure=event_failure)

    def rejected_min_step(state: np.ndarray, h: float) -> Step:
        if h > 5.0e-4:
            return Step(np.asarray(state) + 10.0, minimum_physical_population=-1.0)
        return Step(np.array(state, copy=True), minimum_physical_population=1.0)

    contamination = exc_text(
        lambda: trajectory.advance_canonical_macro_interval(
            context(parent, step=8.0e-4, minimum=1.0e-5, maximum=1.0e-3),
            stepper=rejected_min_step,
            candidate_factory=candidate,
        )
    )
    emit("X2_REJECTED_DIAGNOSTIC_CONTAMINATION", failure=contamination)

    unrepresentable = exc_text(
        lambda: trajectory.AdaptiveBackwardEulerTrial(
            state_vector=np.asarray([1.0]), converged=False,
            backward_error=math.inf, algebraic_residual_relative=math.inf,
            minimum_physical_population=-math.inf,
        )
    )
    emit("X2_UNREPRESENTABLE_FAILURE", failure=unrepresentable)


def x3() -> None:
    def integrate(event):
        return solve_ivp(
            lambda t, y: np.zeros_like(y), (0.0, 1.0), np.asarray([0.0]),
            method="DOP853", first_step=1.0, max_step=1.0,
            events=event, dense_output=True,
        )

    control = integrate(lambda t, y: t - 0.25)
    two = integrate(lambda t, y: (t - 0.25) * (t - 0.75))
    grazing = integrate(lambda t, y: (t - 0.5) ** 2)
    emit(
        "X3_SCIPY_EVENTS",
        control_roots=control.t_events[0].tolist(),
        two_simple_roots=two.t_events[0].tolist(),
        grazing_roots=grazing.t_events[0].tolist(),
        two_success=bool(two.success), grazing_success=bool(grazing.success),
        two_mesh=two.t.tolist(), grazing_mesh=grazing.t.tolist(),
    )
    emit(
        "X3_PROJECT_ROOT_HELPER",
        nowhere_zero_default=piecewise_linear_roots([0.0, 1.0], [1.0e-16, 1.0e-16]).tolist(),
        tiny_sign_tol_zero=piecewise_linear_roots([0.0, 1.0], [1.0e-200, -1.0e-200], tol=0.0).tolist(),
    )


def x4() -> None:
    mp.mp.dps = 100
    rows = []
    for chi_float in (1.0e-6, 1.0e-8, 1.0e-10, 1.0e-20):
        chi = mp.mpf(str(chi_float)); t = mp.mpf("2"); f0 = mp.mpf("0.7"); j = mp.mpf("1.3")
        transmission = mp.exp(-chi * t)
        absorbed = -mp.expm1(-chi * t)
        reference = -t * transmission * f0 + j * (t * transmission * chi - absorbed) / chi**2
        observed = constant_coefficient_transfer_jvp(
            f_initial=0.7, emissivity_s_inv=1.3, opacity_s_inv=chi_float,
            travel_time_s=2.0, d_opacity_s_inv=1.0,
        )
        relative = abs((mp.mpf(str(observed)) - reference) / reference)
        rows.append({"chi": chi_float, "observed": observed,
                     "reference": float(reference), "relative_error": float(relative)})
    emit("X4_TRANSFER_JVP", rows=rows)

    sequence = BackgroundSnapshotSequence.from_npz(
        ROOT / "data/pr01c_background_snapshots_v048.npz", "Bianchi_II_large_shear"
    )
    snapshot = sequence.snapshot_at_tau(float(0.5 * (sequence.tau[0] + sequence.tau[-1])))
    solver = BianchiCharacteristicFaceSolver(snapshot)
    result = solver.trace_to_frequency_face(
        direction_normal=np.asarray([1.0, 0.0, 0.0]),
        frequency_initial_Hz=2.0, frequency_target_Hz=2.0,
        f_initial=-7.0, emissivity_s_inv=-1.0, opacity_s_inv=-1.0,
        time_safety_factor=math.nan,
    )
    emit("X4_ZERO_DISTANCE_VALIDATION", f_face=result.f_face, step_count=result.step_count)


def make_parent(metadata=None, positive=False) -> AcceptedContinuationState:
    return AcceptedContinuationState(
        values=np.asarray([1.0]), positive_mask=np.asarray([positive]),
        accepted_history_count=1, history_sha256="1" * 64,
        background_sha256="2" * 64, network_sha256="3" * 64,
        interface_sha256="4" * 64, branch_id="probe", metadata=metadata,
    )


def x5() -> None:
    parent = make_parent(metadata={"tag": "before"})
    digest_before = parent.sha256
    parent.metadata["tag"] = "after"
    digest_after = parent.sha256
    emit("X5_MUTABLE_METADATA", before=digest_before, after=digest_after,
         changed=bool(digest_before != digest_after))

    parent = make_parent()
    fabricated = PseudoTransientResult(
        parent_sha256=parent.sha256, state_values=np.asarray([999.0]),
        converged=True, iterations=(), final_physical_residual=0.0,
        accepted_history_count=1,
    )
    committed = ContinuationTransaction(parent, fabricated).commit(history_sha256="5" * 64)
    emit("X5_FABRICATED_COMMIT", value=float(committed.values[0]),
         accepted_history_count=committed.accepted_history_count)

    inf_iteration = PseudoTransientIteration(
        outer_index=0, pseudo_time=1.0, accepted=True, physical_residual=0.0,
        pseudo_backward_error=0.0, newton_steps=1, minimum_positive_value=math.inf,
    )
    nonfinite_result = PseudoTransientResult(
        parent_sha256=parent.sha256, state_values=np.asarray([1.0]), converged=True,
        iterations=(inf_iteration,), final_physical_residual=0.0,
        accepted_history_count=1,
    )
    emit("X5_NONFINITE_RESTART", failure=exc_text(nonfinite_result.restart_bytes))

    mixed = _physical_backward_error(
        np.asarray([0.0, 1.0e-20]), np.asarray([1.0, 1.0e-18]), np.zeros((2, 2))
    )
    alone = _physical_backward_error(
        np.asarray([1.0e-20]), np.asarray([1.0e-18]), np.zeros((1, 1))
    )
    emit("X5_MIXED_SCALE", mixed=mixed, alone=alone, ratio=mixed / alone)

    null_outcomes = {}
    for scale in (1.0, 1.0e-12, 1.0e-20):
        try:
            null_outcomes[str(scale)] = project_left_nullspace(
                [1.0, 2.0], np.asarray([[scale, 0.0]])
            ).tolist()
        except Exception as exc:
            null_outcomes[str(scale)] = f"{type(exc).__name__}: {exc}"
    emit("X5_NULL_BASIS_SCALE", outcomes=null_outcomes)

    helpers = runpy.run_path(str(ROOT / "tests/trajectory/test_full_coupled_transport.py"))
    network = helpers["three_cell_network"]()
    grid = helpers["octahedral_grid"]()
    transport = ConservativeFrequencyLiouville.from_network(
        network, reference_line=helpers["LineBoundaryConfig"].lyman_alpha(
            temperature_K=3000.0, x_red=-1.5, x_blue=1.5
        )
    )
    problem = CoupledCollisionTransportProblem(
        network=network, grid=grid, transport=transport,
        face_speeds_x_s_inv=np.zeros((network.n_state + 1, grid.n_angle)),
        native_red_occupation=np.full(grid.n_angle, 0.24),
        native_blue_occupation=np.full(grid.n_angle, 0.08), dt_s=200.0,
    )
    old = np.asarray([
        [0.20, 0.18, 0.22, 0.19, 0.25, 0.17],
        [0.16, 0.17, 0.15, 0.18, 0.14, 0.19],
        [0.11, 0.13, 0.10, 0.14, 0.09, 0.15],
    ])
    inf_policy = problem.implicit_step(old, nonlinear_rtol=math.inf)
    negative_policy = problem.implicit_step(old, max_newton=-1)
    emit("X5_INVALID_POLICY", inf_converged=inf_policy.converged,
         inf_residual=inf_policy.residual_relative,
         negative_max_newton_converged=negative_policy.converged,
         negative_max_newton_iterations=negative_policy.newton_iterations)

    sigma = np.diag([1.0e-13, 0.0, 0.0])
    background = BackgroundSnapshot(
        tau=0.0, cosmic_time_s=1.0, H_s_inv=1.0e-13, q=0.5,
        sigma_s_inv=sigma, N_s_inv=np.zeros((3, 3)), A_s_inv=np.zeros(3),
        frame_rotation_s_inv=np.zeros(3), beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3), chart_id="probe", bianchi_type="I",
        constraint_residuals={"gauss": math.nan},
    )
    emit("X5_BACKGROUND_SCALE_FINITE", trace_over_H=float(np.trace(background.sigma_s_inv) / background.H_s_inv),
         gauss_is_nan=bool(math.isnan(background.constraint_residuals["gauss"])))

    matrix = np.asarray([[2.0e-16, 1.0e-16], [-1.0e-16, 2.0e-16]])
    m_audit = audit_native_m_matrix(matrix)
    graph = EntropyGraphPreconditioner.from_scalar_graph(
        conductance=np.asarray([[0.0, 1.0e-16], [0.0, 0.0]]),
        occupation=np.asarray([1.0, 1.0]), mode_measure=np.asarray([1.0, 1.0]),
        shift=1.0, stiffness=1.0,
    )
    emit("X5_STRUCTURAL_FLOORS", m_matrix=m_audit.nonsingular_m_matrix,
         positive_offdiag_fraction=0.5,
         input_graph_asymmetry_fraction=1.0,
         accepted_graph_laplacian=graph.graph_laplacian.tolist())


def x6() -> None:
    one = history(n=1)
    outcomes = {}
    for query in (one.grid.eta_start - 1.0, one.grid.eta_start, one.grid.eta_start + 1.0):
        try:
            stencil = one.grid.locate(query, accepted_count=1)
            outcomes[str(query)] = {"thermal_zero": stencil.thermal_zero,
                                    "left": stencil.left_index, "right": stencil.right_index}
        except Exception as exc:
            outcomes[str(query)] = f"{type(exc).__name__}: {exc}"

    with np.load(ROOT / "data/pr05b2_source_history_v060.npz", allow_pickle=False) as data:
        source_history = AcceptedRadiationHistory.from_npz_mapping(data)
    n = source_history.accepted_count
    floats_per_slice = (source_history.outgoing_virtual.shape[0]
                        + source_history.outgoing_lyman.shape[0]
                        + source_history.average_virtual.shape[0])
    raw_bytes = n * floats_per_slice * 8
    cumulative_copy_lower_bound = floats_per_slice * 8 * n * (n + 1) // 2
    emit("X6_HISTORY", one_slice_queries=outcomes, slices=n,
         floats_per_slice=floats_per_slice, raw_bytes=raw_bytes,
         cumulative_array_copy_lower_bound_bytes=cumulative_copy_lower_bound)

    stencil = CharacteristicInterpolationStencil(
        eta_query=0.0, eta_start=-0.0005, dlna=0.001, accepted_count=2,
        left_index=0, right_index=1, fraction=0.5,
    )
    jvp_outcomes = {}
    for scale in (1.0e-5, 1.0e-4, 1.0e-3):
        try:
            jvp_outcomes[str(scale)] = stencil.jvp(
                [1.0, 2.0], [3.0 * scale, 4.0 * scale], delta_eta=scale
            )
        except CharacteristicStencilSwitch as exc:
            jvp_outcomes[str(scale)] = f"CharacteristicStencilSwitch: {exc}"
    emit("X6_JVP_DIRECTION_SCALE", outcomes=jvp_outcomes)


if __name__ == "__main__":
    x2()
    x3()
    x4()
    x5()
    x6()

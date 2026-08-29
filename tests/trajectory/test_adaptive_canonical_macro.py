from __future__ import annotations

from dataclasses import dataclass
import hashlib
from types import SimpleNamespace

import numpy as np
import pytest

import full_bianchi_hyrec.trajectory as trajectory
import full_bianchi_hyrec.trajectory.adaptive_macro as adaptive_macro
from full_bianchi_hyrec.trajectory.causal_history import (
    AcceptedRadiationHistory,
    CharacteristicHistoryGrid,
    HistoryAppendCandidate,
)


def _history(n: int = 5, dlna: float = 1.0e-3) -> AcceptedRadiationHistory:
    eta0 = -8.0
    eta = eta0 + dlna * np.arange(n)
    virtual = np.zeros((311, n), dtype=float)
    lyman = np.zeros((3, n), dtype=float)
    average = np.zeros((311, n), dtype=float)
    return AcceptedRadiationHistory(
        grid=CharacteristicHistoryGrid(
            eta=eta,
            source_indices=np.arange(n),
            z_start=np.exp(-eta0) - 1.0,
            dlna=dlna,
            energy_eV=np.linspace(5.0, 12.7, 311),
            source_hashes={
                "HyRec_Oct2012.zip": "1" * 64,
                "HyRec/hydrogen.c": "2" * 64,
            },
        ),
        outgoing_virtual=virtual,
        outgoing_lyman=lyman,
        average_virtual=average,
        completeness="SYNTHETIC_FULL",
    )


@dataclass(frozen=True)
class _Step:
    state_vector: np.ndarray
    converged: bool
    backward_error: float
    algebraic_residual_relative: float
    minimum_physical_population: float


def _linear_step(state: np.ndarray, h: float) -> _Step:
    # Backward Euler for x'=-x; second entry is a signed departure kept unclipped.
    result = np.array(state, copy=True)
    result[0] = state[0] / (1.0 + h)
    result[1] = state[1] - 0.25 * h
    return _Step(
        state_vector=result,
        converged=True,
        backward_error=0.0,
        algebraic_residual_relative=0.0,
        minimum_physical_population=float(result[0]),
    )


def _candidate(history: AcceptedRadiationHistory) -> HistoryAppendCandidate:
    return HistoryAppendCandidate(
        accepted_index=history.accepted_count,
        eta=history.grid.eta[-1] + history.grid.dlna,
        outgoing_virtual=np.full(311, history.accepted_count * 1.0e-18),
        outgoing_lyman=np.full(3, history.accepted_count * 1.0e-19),
        average_virtual=np.full(311, -history.accepted_count * 1.0e-18),
        parent_sha256=history.sha256,
    )


def test_public_pr05c1_api_exists() -> None:
    required = {
        "AdaptiveControllerTolerances",
        "AdaptiveEvent",
        "AdaptiveEventKind",
        "AdaptiveTrajectoryContext",
        "CanonicalMacroInterval",
        "AcceptedMacrostepLedger",
        "TrajectoryRestartState",
        "advance_canonical_macro_interval",
    }
    assert required <= set(dir(trajectory))


def test_macro_interval_requires_exact_canonical_width() -> None:
    history = _history()
    good = trajectory.CanonicalMacroInterval.from_history(history)
    assert good.eta_end - good.eta_start == pytest.approx(history.grid.dlna)
    with pytest.raises(ValueError, match="canonical width"):
        trajectory.CanonicalMacroInterval(
            macro_index=history.accepted_count,
            eta_start=history.grid.eta[-1],
            eta_end=history.grid.eta[-1] + 0.5 * history.grid.dlna,
            canonical_dlna=history.grid.dlna,
            parent_history_sha256=history.sha256,
            accepted_count_before=history.accepted_count,
        )


def test_adaptive_macro_commits_once_and_rejections_do_not_mutate_history() -> None:
    history = _history()
    parent_bytes = history.to_bytes()
    context = trajectory.AdaptiveTrajectoryContext(
        eta=history.grid.eta[-1],
        state_vector=np.array([1.0, -0.1]),
        accepted_history=history,
        controller_step=0.9 * history.grid.dlna,
        tolerances=trajectory.AdaptiveControllerTolerances(
            absolute=np.array([1.0e-12, 1.0e-12]),
            relative=np.array([1.0e-10, 1.0e-10]),
            minimum_step=history.grid.dlna / 128.0,
            maximum_step=history.grid.dlna,
        ),
        background_label="toy",
    )
    updated, ledger = trajectory.advance_canonical_macro_interval(
        context,
        stepper=_linear_step,
        candidate_factory=_candidate,
    )
    assert ledger.history_count_increment == 1
    assert ledger.commit_count == 1
    assert ledger.accepted_microsteps >= 2
    assert ledger.rejected_microsteps >= 1
    assert ledger.history_before_sha256 == history.sha256
    assert updated.accepted_history.accepted_count == history.accepted_count + 1
    assert updated.accepted_history.sha256 == ledger.history_after_sha256
    assert history.to_bytes() == parent_bytes
    assert updated.state_vector[0] > 0.0
    assert updated.state_vector[1] < -0.1  # signed departure was not clipped


def test_event_is_localized_without_history_mutation_and_requires_restart() -> None:
    history = _history()
    eta0 = history.grid.eta[-1]
    root = eta0 + 0.4 * history.grid.dlna
    context = trajectory.AdaptiveTrajectoryContext(
        eta=eta0,
        state_vector=np.array([1.0, 0.0]),
        accepted_history=history,
        controller_step=history.grid.dlna,
        tolerances=trajectory.AdaptiveControllerTolerances.scalar(
            size=2,
            absolute=1.0e-8,
            relative=1.0e-6,
            minimum_step=history.grid.dlna / 256.0,
            maximum_step=history.grid.dlna,
        ),
        events=(
            trajectory.AdaptiveEvent(
                kind=trajectory.AdaptiveEventKind.BOUNDARY_SPEED_ZERO,
                eta=root,
                label="Bianchi-II-blue",
            ),
        ),
        background_label="Bianchi-II",
    )
    updated, ledger = trajectory.advance_canonical_macro_interval(
        context,
        stepper=_linear_step,
        candidate_factory=_candidate,
    )
    assert ledger.event_count == 1
    assert ledger.restart_count == 1
    assert ledger.localized_event_etas == pytest.approx((root,))
    assert ledger.history_count_increment == 1
    assert updated.accepted_history.accepted_count == history.accepted_count + 1


def test_step_doubling_rejects_when_either_half_step_fails_residual_gates() -> None:
    history = _history()
    dlna = history.grid.dlna

    def stepper(state: np.ndarray, h: float) -> _Step:
        base = _linear_step(state, h)
        half_step_is_bad = h < 0.75 * dlna
        return _Step(
            state_vector=base.state_vector,
            converged=True,
            backward_error=1.0e-6 if half_step_is_bad else 0.0,
            algebraic_residual_relative=1.0e-6 if half_step_is_bad else 0.0,
            minimum_physical_population=base.minimum_physical_population,
        )

    context = trajectory.AdaptiveTrajectoryContext(
        eta=history.grid.eta[-1],
        state_vector=np.array([1.0, 0.0]),
        accepted_history=history,
        controller_step=dlna,
        tolerances=trajectory.AdaptiveControllerTolerances.scalar(
            size=2,
            absolute=1.0,
            relative=1.0,
            minimum_step=dlna,
            maximum_step=dlna,
        ),
        background_label="half-step-residual-gate",
    )

    with pytest.raises(RuntimeError, match="minimum step"):
        trajectory.advance_canonical_macro_interval(
            context,
            stepper=stepper,
            candidate_factory=_candidate,
        )


def test_restart_roundtrip_is_byte_exact() -> None:
    history = _history()
    state = trajectory.TrajectoryRestartState(
        eta=history.grid.eta[-1],
        state_vector=np.array([0.9, -0.2]),
        accepted_history=history,
        controller_step=2.5e-4,
        background_label="VI_-1/9",
        event_generation=3,
    )
    payload = state.to_bytes()
    restored = trajectory.TrajectoryRestartState.from_bytes(payload)
    assert restored.to_bytes() == payload
    assert restored.accepted_history.to_bytes() == history.to_bytes()
    assert hashlib.sha256(payload).hexdigest() == state.sha256


def test_fixed_step_limit_accepts_the_independently_computed_fine_endpoint() -> None:
    # Production defect: the controller estimates LTE from two half steps but
    # advances with the less accurate coarse full-step endpoint.
    history = _history()
    context = trajectory.AdaptiveTrajectoryContext(
        eta=history.grid.eta[-1],
        state_vector=np.array([1.0, 0.25]),
        accepted_history=history,
        controller_step=history.grid.dlna,
        tolerances=trajectory.AdaptiveControllerTolerances.scalar(
            size=2,
            absolute=1.0,
            relative=1.0,
            minimum_step=history.grid.dlna,
            maximum_step=history.grid.dlna,
        ),
        background_label="FLRW",
    )
    updated, ledger = trajectory.advance_canonical_macro_interval(
        context,
        stepper=_linear_step,
        candidate_factory=_candidate,
    )
    half_width = 0.5 * history.grid.dlna
    expected = np.array(
        [
            1.0 / ((1.0 + half_width) * (1.0 + half_width)),
            0.25 - 0.25 * history.grid.dlna,
        ]
    )
    assert ledger.accepted_microsteps == 1
    assert ledger.rejected_microsteps == 0
    np.testing.assert_allclose(updated.state_vector, expected, rtol=0.0, atol=1.0e-15)
    coarse_x = 1.0 / (1.0 + history.grid.dlna)
    assert updated.state_vector[0] != coarse_x


def test_step_doubling_snapshots_a_reused_stage_output_buffer() -> None:
    history = _history()
    shared = np.empty(2, dtype=float)

    def reused_buffer_step(state: np.ndarray, h: float) -> _Step:
        shared[0] = state[0] / (1.0 + h)
        shared[1] = state[1] - 0.25 * h
        return _Step(shared, True, 0.0, 0.0, float(shared[0]))

    context = trajectory.AdaptiveTrajectoryContext(
        eta=history.grid.eta[-1],
        state_vector=np.array([1.0, 0.25]),
        accepted_history=history,
        controller_step=history.grid.dlna,
        tolerances=trajectory.AdaptiveControllerTolerances.scalar(
            size=2,
            absolute=1.0,
            relative=1.0,
            minimum_step=history.grid.dlna,
            maximum_step=history.grid.dlna,
        ),
        background_label="shared-stage-buffer",
    )

    updated, ledger = trajectory.advance_canonical_macro_interval(
        context,
        stepper=reused_buffer_step,
        candidate_factory=_candidate,
    )

    half_width = 0.5 * history.grid.dlna
    expected_fine = 1.0 / (1.0 + half_width) ** 2
    assert ledger.attempts[0].error_norm is not None
    assert ledger.attempts[0].error_norm > 0.0
    assert updated.state_vector[0] == pytest.approx(expected_fine, abs=1.0e-15)


def test_singular_source_trial_returns_a_finite_typed_retryable_failure() -> None:
    # Production defect: the singular-denominator branch constructs infinities
    # that its own success-result constructor immediately rejects.
    dae = SimpleNamespace(
        layout=SimpleNamespace(local_size=3),
        _electron_rate_derivatives=lambda: (2.0, 0.0),
        electron_rate_per_lna=lambda _xe, _native: 0.0,
    )
    problem = SimpleNamespace(
        dae=dae,
        registry=SimpleNamespace(active_owner="owner"),
        _incoming_for=lambda _owner: pytest.fail("singular trial evaluated dependent native data"),
    )

    outcome = trajectory.source_conditioned_backward_euler_trial(
        problem,
        np.array([1.0, 0.0, 0.0]),
        1.0,
    )

    assert isinstance(outcome, adaptive_macro.AdaptiveBackwardEulerFailure)
    assert outcome.kind is adaptive_macro.AdaptiveTrialFailureKind.RETRY_LINEAR
    assert outcome.retryable
    assert all(np.isfinite(value) for _name, value in outcome.diagnostics)

    dae._electron_rate_derivatives = lambda: (np.inf, 0.0)
    nonfinite = trajectory.source_conditioned_backward_euler_trial(
        problem,
        np.array([1.0, 0.0, 0.0]),
        1.0,
    )
    assert isinstance(nonfinite, adaptive_macro.AdaptiveBackwardEulerFailure)
    assert nonfinite.kind is adaptive_macro.AdaptiveTrialFailureKind.NONFINITE_OUTPUT
    assert all(np.isfinite(value) for _name, value in nonfinite.diagnostics)


@pytest.mark.parametrize(
    ("kind", "expected_second_width"),
    [
        ("RETRY_NONLINEAR", 0.5),
        ("RETRY_LINEAR", 0.35),
        ("RETRY_DOMAIN", 0.2),
        ("NONFINITE_OUTPUT", 0.1),
    ],
)
def test_typed_failure_short_circuits_dependent_trials_and_contracts_by_cause(
    kind: str,
    expected_second_width: float,
) -> None:
    # Production defect: a failed full trial still launches both dependent
    # half trials and zero LTE can leave the retry width unchanged.
    history = _history(dlna=1.0e-3)
    calls: list[float] = []

    def stepper(state: np.ndarray, h: float):
        calls.append(h)
        if len(calls) == 1:
            return adaptive_macro.AdaptiveBackwardEulerFailure(
                kind=adaptive_macro.AdaptiveTrialFailureKind(kind),
                message="injected retryable failure",
                diagnostics=(("trial_width", h),),
            )
        return _Step(
            state_vector=np.array(state, copy=True),
            converged=True,
            backward_error=1.0e-13,
            algebraic_residual_relative=1.0e-13,
            minimum_physical_population=0.75,
        )

    context = trajectory.AdaptiveTrajectoryContext(
        eta=history.grid.eta[-1],
        state_vector=np.array([1.0, 0.0]),
        accepted_history=history,
        controller_step=history.grid.dlna,
        tolerances=trajectory.AdaptiveControllerTolerances.scalar(
            size=2,
            absolute=1.0,
            relative=1.0,
            minimum_step=history.grid.dlna / 128.0,
            maximum_step=history.grid.dlna,
        ),
        background_label="typed-failure",
    )

    _updated, ledger = trajectory.advance_canonical_macro_interval(
        context,
        stepper=stepper,
        candidate_factory=_candidate,
    )

    assert calls[1] == pytest.approx(expected_second_width * history.grid.dlna)
    assert ledger.attempts[0].failure_kind is adaptive_macro.AdaptiveTrialFailureKind(kind)
    assert ledger.attempts[0].error_norm is None
    assert ledger.attempts[0].failure_diagnostics[0][0] == "trial_width"
    assert ledger.attempts[0].failure_diagnostics[0][1] == pytest.approx(history.grid.dlna)
    assert ledger.rejected_microsteps == 1


def test_rejected_trial_diagnostics_do_not_contaminate_accepted_extrema() -> None:
    # Production defect: extrema are updated before the acceptance branch, so
    # rejected trial diagnostics become purported production extrema.
    history = _history(dlna=1.0e-3)
    calls = 0

    def stepper(state: np.ndarray, h: float):
        nonlocal calls
        calls += 1
        if calls == 2:
            return adaptive_macro.AdaptiveBackwardEulerFailure(
                kind=adaptive_macro.AdaptiveTrialFailureKind.RETRY_DOMAIN,
                message="injected negative trial",
                diagnostics=(("minimum_population", -999.0),),
            )
        rejected_attempt = calls == 1
        return _Step(
            state_vector=np.array(state, copy=True),
            converged=True,
            backward_error=9.0e-12 if rejected_attempt else 1.0e-13,
            algebraic_residual_relative=8.0e-12 if rejected_attempt else 2.0e-13,
            minimum_physical_population=0.6 if rejected_attempt else 0.75,
        )

    context = trajectory.AdaptiveTrajectoryContext(
        eta=history.grid.eta[-1],
        state_vector=np.array([1.0, 0.0]),
        accepted_history=history,
        controller_step=history.grid.dlna,
        tolerances=trajectory.AdaptiveControllerTolerances.scalar(
            size=2,
            absolute=1.0,
            relative=1.0,
            minimum_step=history.grid.dlna / 128.0,
            maximum_step=history.grid.dlna,
        ),
        background_label="accepted-extrema",
    )

    _updated, ledger = trajectory.advance_canonical_macro_interval(
        context,
        stepper=stepper,
        candidate_factory=_candidate,
    )

    assert ledger.rejected_microsteps == 1
    assert ledger.maximum_backward_error == pytest.approx(1.0e-13)
    assert ledger.maximum_algebraic_residual == pytest.approx(2.0e-13)
    assert ledger.minimum_physical_population == pytest.approx(0.75)


def test_event_landing_may_be_smaller_than_the_ordinary_minimum_step() -> None:
    # Production defect: ordinary h_min overwrites a nearer event displacement,
    # overshooting the event and causing the next attempt to report regression.
    history = _history(dlna=1.0e-3)
    eta0 = history.grid.eta[-1]
    root = eta0 + history.grid.dlna / 20.0
    context = trajectory.AdaptiveTrajectoryContext(
        eta=eta0,
        state_vector=np.array([1.0, 0.0]),
        accepted_history=history,
        controller_step=history.grid.dlna,
        tolerances=trajectory.AdaptiveControllerTolerances.scalar(
            size=2,
            absolute=1.0,
            relative=1.0,
            minimum_step=history.grid.dlna / 10.0,
            maximum_step=history.grid.dlna,
        ),
        events=(
            trajectory.AdaptiveEvent(
                kind=trajectory.AdaptiveEventKind.BOUNDARY_SPEED_ZERO,
                eta=root,
                label="sub-hmin-event",
            ),
        ),
        background_label="event-hmin",
    )

    _updated, ledger = trajectory.advance_canonical_macro_interval(
        context,
        stepper=_linear_step,
        candidate_factory=_candidate,
    )

    event_attempts = [attempt for attempt in ledger.attempts if attempt.event_kind is not None]
    assert len(event_attempts) == 1
    assert event_attempts[0].proposed_step == pytest.approx(history.grid.dlna / 20.0)
    assert event_attempts[0].proposed_step < context.tolerances.minimum_step
    assert ledger.localized_event_etas == pytest.approx((root,))
    assert ledger.restart_count == 1

from pathlib import Path
from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (
    CollisionNetwork,
    LineBoundaryConfig,
    positive_harmonic_grid,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    parse_original_hyrec_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.primitive_trajectory import (
    PrimitiveTrajectoryProblem,
    atomic_state_from_source_snapshot,
)
from full_bianchi_hyrec.trajectory.time_dependent_native import (
    SourceIdentifiableOriginalHyRecDAE,
)

ROOT = Path(__file__).resolve().parents[2]


def _real_owner_problem(target: int = 1100):
    source = parse_original_hyrec_snapshot_csv(
        ROOT
        / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
        / f"pr04c_z{target}.csv"
    )
    rates = OriginalHyRecPrimitiveRateTable.from_archive(
        ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
    ).evaluate(
        radiation_temperature_eV_rescaled=source.TR_eV_rescaled,
        matter_to_radiation_temperature_ratio=source.TM_over_TR,
        fsR=source.fsR,
        meR=source.meR,
    )
    network = CollisionNetwork.from_npz(ROOT / "data/full_scalar_com_khw_v050.npz")
    angular = positive_harmonic_grid(12)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    atomic_state = atomic_state_from_source_snapshot(
        source,
        com_occupation=scalar[:, None] * np.ones((1, angular.n_angle)),
        beta_H=np.zeros(3),
    )
    background = BackgroundSnapshot(
        tau=-np.log1p(source.z),
        cosmic_time_s=1.0,
        H_s_inv=source.H_s_inv,
        q=0.5,
        sigma_s_inv=np.zeros((3, 3)),
        N_s_inv=np.zeros((3, 3)),
        A_s_inv=np.zeros(3),
        frame_rotation_s_inv=np.zeros(3),
        beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3),
        chart_id=f"pr05c1-test-{target}",
        bianchi_type="I",
    )
    primitive = PrimitiveTrajectoryProblem(
        background=background,
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=angular,
        line=LineBoundaryConfig.lyman_alpha(
            temperature_K=atomic_state.T_m_K, x_red=-21.25, x_blue=21.25
        ),
        interface_enabled=False,
    )
    dae = SourceIdentifiableOriginalHyRecDAE.from_primitive_problem(primitive)
    with np.load(ROOT / "data/pr05b2_source_history_v060.npz", allow_pickle=False) as data:
        history = AcceptedRadiationHistory.from_npz_mapping(data).prefix(source.iz_local)
    registry = trajectory.ScalarHistoryOwnershipRegistry(
        active_owners=(trajectory.ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK,),
        required_source_hashes=history.grid.source_hashes,
        history_schema="PR05B2_ACCEPTED_HISTORY_V1",
    )
    canonical = trajectory.ScalarHistoryOwnerSwapProblem(
        dae=dae,
        history=history,
        registry=registry,
        atomic_state=atomic_state,
    )
    typed = canonical.promote_typed(canonical.parity_audit())
    return typed, dae.source_state_vector(atomic_state), history


@pytest.mark.slow
def test_real_source_conditioned_macro_uses_typed_owner_and_commits_once() -> None:
    problem, state, history = _real_owner_problem(1100)
    state = np.array(state, copy=True)
    state[0] *= 1.00001
    dlna = history.grid.dlna
    context = trajectory.AdaptiveTrajectoryContext(
        eta=history.grid.eta[-1],
        state_vector=state,
        accepted_history=history,
        controller_step=dlna,
        tolerances=trajectory.AdaptiveControllerTolerances.scalar(
            size=state.size,
            absolute=1.0e-4,
            relative=1.0e-3,
            minimum_step=dlna,
            maximum_step=dlna,
        ),
        background_label="source-conditioned-z1100",
    )
    evaluation = problem.evaluate()

    def candidate_factory(parent: AcceptedRadiationHistory) -> HistoryAppendCandidate:
        return HistoryAppendCandidate(
            accepted_index=parent.accepted_count,
            eta=parent.grid.eta[-1] + parent.grid.dlna,
            outgoing_virtual=evaluation.outgoing_virtual,
            outgoing_lyman=evaluation.outgoing_lyman,
            average_virtual=evaluation.average_virtual,
            parent_sha256=parent.sha256,
        )

    context, ledger = trajectory.advance_canonical_macro_interval(
        context,
        stepper=lambda old, h: trajectory.source_conditioned_backward_euler_trial(
            problem, old, h
        ),
        candidate_factory=candidate_factory,
    )
    assert ledger.history_count_increment == 1
    assert ledger.commit_count == 1
    assert ledger.accepted_microsteps == 1
    assert ledger.maximum_backward_error < 1.0e-11
    assert ledger.maximum_algebraic_residual < 1.0e-11
    assert ledger.minimum_physical_population > 0.0
    assert context.accepted_history.accepted_count == history.accepted_count + 1
    restart = trajectory.TrajectoryRestartState(
        eta=context.eta,
        state_vector=context.state_vector,
        accepted_history=context.accepted_history,
        controller_step=context.controller_step,
        background_label=context.background_label,
        event_generation=context.event_generation,
    )
    assert trajectory.TrajectoryRestartState.from_bytes(restart.to_bytes()).to_bytes() == restart.to_bytes()

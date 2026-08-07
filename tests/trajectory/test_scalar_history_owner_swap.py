from __future__ import annotations

import full_bianchi_hyrec.trajectory as trajectory


def test_public_scalar_history_owner_swap_api_exists() -> None:
    required = {
        "ScalarHistoryFeedbackOwner",
        "ScalarHistoryOwnershipRegistry",
        "ScalarHistoryOwnerSwapProblem",
        "AcceptedStepTransaction",
    }
    assert required <= set(dir(trajectory))

from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.causal_history import (
    AcceptedRadiationHistory,
    CharacteristicHistoryGrid,
    HistoryAppendCandidate,
)


def _synthetic_history(n: int = 8) -> AcceptedRadiationHistory:
    eta0 = -8.0
    dlna = 1.0e-3
    eta = eta0 + dlna * np.arange(n)
    energy = np.linspace(5.0, 12.7, 311)
    virtual = np.arange(311 * n, dtype=float).reshape(311, n) * 1.0e-18
    lyman = np.arange(3 * n, dtype=float).reshape(3, n) * 1.0e-19
    average = -0.25 * virtual
    return AcceptedRadiationHistory(
        grid=CharacteristicHistoryGrid(
            eta=eta,
            source_indices=np.arange(n),
            z_start=np.exp(-eta0) - 1.0,
            dlna=dlna,
            energy_eV=energy,
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


def _candidate(history: AcceptedRadiationHistory, *, parent: str | None = None) -> HistoryAppendCandidate:
    return HistoryAppendCandidate(
        accepted_index=history.accepted_count,
        eta=history.grid.eta[-1] + history.grid.dlna,
        outgoing_virtual=np.linspace(-1.0e-13, 2.0e-13, 311),
        outgoing_lyman=np.asarray([2.0e-14, 3.0e-15, 4.0e-16]),
        average_virtual=np.linspace(-2.0e-13, 1.0e-13, 311),
        parent_sha256=history.sha256 if parent is None else parent,
    )


def test_owner_registry_requires_exactly_one_owner() -> None:
    history = _synthetic_history()
    kwargs = {
        "required_source_hashes": history.grid.source_hashes,
        "history_schema": "PR05B2_ACCEPTED_HISTORY_V1",
    }
    with pytest.raises(ValueError, match="exactly one"):
        trajectory.ScalarHistoryOwnershipRegistry(active_owners=(), **kwargs)
    with pytest.raises(ValueError, match="exactly one"):
        trajectory.ScalarHistoryOwnershipRegistry(
            active_owners=(
                trajectory.ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK,
                trajectory.ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY,
            ),
            **kwargs,
        )


def test_owner_registry_validates_schema_hashes_candidate_and_frozen_owners() -> None:
    history = _synthetic_history()
    registry = trajectory.ScalarHistoryOwnershipRegistry(
        active_owners=(trajectory.ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK,),
        required_source_hashes=history.grid.source_hashes,
        history_schema="PR05B2_ACCEPTED_HISTORY_V1",
    )
    assert registry.active_owner is trajectory.ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK
    assert registry.sobolev_owner == "CANONICAL_ORIGINAL_HYREC"
    assert registry.a1s_diffusion_owner == "CANONICAL_ORIGINAL_HYREC"
    assert registry.tvv_owner == "CANONICAL_ORIGINAL_HYREC"
    registry.validate(history, candidate=_candidate(history))

    bad_hashes = dict(history.grid.source_hashes)
    bad_hashes["HyRec/hydrogen.c"] = "3" * 64
    mismatched = trajectory.ScalarHistoryOwnershipRegistry(
        active_owners=(trajectory.ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK,),
        required_source_hashes=bad_hashes,
        history_schema="PR05B2_ACCEPTED_HISTORY_V1",
    )
    with pytest.raises(ValueError, match="source hash"):
        mismatched.validate(history)

    bad_schema = trajectory.ScalarHistoryOwnershipRegistry(
        active_owners=(trajectory.ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK,),
        required_source_hashes=history.grid.source_hashes,
        history_schema="PR05B2_ACCEPTED_HISTORY_V0",
    )
    with pytest.raises(ValueError, match="schema"):
        bad_schema.validate(history)

    with pytest.raises(ValueError, match="parent"):
        registry.validate(history, candidate=_candidate(history, parent="4" * 64))

    typed = registry.with_owner(
        trajectory.ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY
    )
    assert typed.active_owner is trajectory.ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY
    assert typed.sobolev_owner == registry.sobolev_owner
    assert typed.a1s_diffusion_owner == registry.a1s_diffusion_owner
    assert typed.tvv_owner == registry.tvv_owner

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
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
NETWORK = ROOT / "data/full_scalar_com_khw_v050.npz"
SOURCE_HISTORY = ROOT / "data/pr05b2_source_history_v060.npz"


def _real_problem(target: int = 1100):
    source = parse_original_hyrec_snapshot_csv(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
    rates = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE).evaluate(
        radiation_temperature_eV_rescaled=source.TR_eV_rescaled,
        matter_to_radiation_temperature_ratio=source.TM_over_TR,
        fsR=source.fsR,
        meR=source.meR,
    )
    network = CollisionNetwork.from_npz(NETWORK)
    angular = positive_harmonic_grid(12)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    state = atomic_state_from_source_snapshot(
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
        chart_id="pr05b3-test",
        bianchi_type="I",
    )
    primitive = PrimitiveTrajectoryProblem(
        background=background,
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=angular,
        line=LineBoundaryConfig.lyman_alpha(
            temperature_K=state.T_m_K, x_red=-21.25, x_blue=21.25
        ),
        interface_enabled=False,
    )
    dae = SourceIdentifiableOriginalHyRecDAE.from_primitive_problem(primitive)
    with np.load(SOURCE_HISTORY, allow_pickle=False) as data:
        history = AcceptedRadiationHistory.from_npz_mapping(data).prefix(source.iz_local)
    registry = trajectory.ScalarHistoryOwnershipRegistry(
        active_owners=(trajectory.ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK,),
        required_source_hashes=history.grid.source_hashes,
        history_schema="PR05B2_ACCEPTED_HISTORY_V1",
    )
    return dae, state, history, registry


@pytest.mark.slow
def test_owner_swap_requires_componentwise_parity_before_typed_promotion() -> None:
    dae, state, history, registry = _real_problem(1100)
    problem = trajectory.ScalarHistoryOwnerSwapProblem(
        dae=dae,
        history=history,
        registry=registry,
        atomic_state=state,
    )
    canonical = problem.evaluate_owner(
        trajectory.ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK
    )
    typed = problem.evaluate_owner(
        trajectory.ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY
    )
    audit = problem.parity_audit()
    assert audit.passed
    assert audit.incoming_virtual_max_abs < 3.0e-25
    assert audit.incoming_lyman_max_abs < 3.0e-25
    assert audit.native_rhs_relative < 3.0e-13
    assert audit.native_solution_relative < 5.0e-12
    assert audit.electron_rate_relative < 4.0e-13
    assert audit.outgoing_virtual_relative < 5.0e-12
    assert audit.outgoing_lyman_relative < 3.0e-12
    assert audit.average_virtual_relative < 3.0e-12
    assert audit.append_candidate_parent_equal
    assert audit.append_candidate_index_equal
    assert np.array_equal(canonical.native_rhs_s_inv, typed.native_rhs_s_inv)

    promoted = problem.promote_typed(audit)
    assert (
        promoted.registry.active_owner
        is trajectory.ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY
    )
    active = promoted.evaluate()
    assert np.array_equal(active.native_solution, typed.native_solution)
    assert promoted.registry.sobolev_owner == "CANONICAL_ORIGINAL_HYREC"
    assert promoted.registry.a1s_diffusion_owner == "CANONICAL_ORIGINAL_HYREC"
    assert promoted.registry.tvv_owner == "CANONICAL_ORIGINAL_HYREC"


@pytest.mark.slow
def test_active_owner_branch_is_live_in_the_coupled_residual() -> None:
    dae, state, history, registry = _real_problem(1100)
    canonical_problem = trajectory.ScalarHistoryOwnerSwapProblem(
        dae=dae,
        history=history,
        registry=registry,
        atomic_state=state,
    )
    typed_problem = canonical_problem.promote_typed(canonical_problem.parity_audit())
    vector = dae.source_state_vector(state)
    derivative = dae.source_derivative_vector()

    direction_virtual = np.zeros_like(history.outgoing_virtual)
    direction_lyman = np.zeros_like(history.outgoing_lyman)
    incoming = typed_problem.evaluate().incoming
    first = next(
        (query, stencil)
        for query, stencil in zip(incoming.queries, incoming.stencils, strict=True)
        if not stencil.thermal_zero
    )
    query, stencil = first
    assert stencil.left_index is not None
    if query.source_kind == "virtual":
        direction_virtual[query.source_index, stencil.left_index] = 1.0e-16
    else:
        direction_lyman[query.source_index, stencil.left_index] = 1.0e-16
    perturbed_history = history.perturb(
        outgoing_virtual_direction=direction_virtual,
        outgoing_lyman_direction=direction_lyman,
        scale=1.0,
    )

    canonical_perturbed = trajectory.ScalarHistoryOwnerSwapProblem(
        dae=dae,
        history=perturbed_history,
        registry=registry,
        atomic_state=state,
    )
    typed_perturbed = trajectory.ScalarHistoryOwnerSwapProblem(
        dae=dae,
        history=perturbed_history,
        registry=typed_problem.registry,
        atomic_state=state,
    )
    assert np.array_equal(
        canonical_problem.residual(vector, derivative),
        canonical_perturbed.residual(vector, derivative),
    )
    assert not np.array_equal(
        typed_problem.residual(vector, derivative),
        typed_perturbed.residual(vector, derivative),
    )

@pytest.mark.slow
def test_typed_owner_shifted_ijacobian_includes_fixed_history_endpoint_blocks() -> None:
    dae, state, history, registry = _real_problem(1100)
    canonical = trajectory.ScalarHistoryOwnerSwapProblem(
        dae=dae,
        history=history,
        registry=registry,
        atomic_state=state,
    )
    problem = canonical.promote_typed(canonical.parity_audit())
    rng = np.random.default_rng(61)
    local_direction = rng.normal(size=dae.layout.local_size) * 1.0e-12
    history_virtual_direction = np.zeros_like(history.outgoing_virtual)
    history_lyman_direction = np.zeros_like(history.outgoing_lyman)
    incoming = problem.evaluate().incoming
    for query, stencil in zip(incoming.queries[:16], incoming.stencils[:16], strict=True):
        if stencil.thermal_zero:
            continue
        assert stencil.left_index is not None and stencil.right_index is not None
        if query.source_kind == "virtual":
            history_virtual_direction[query.source_index, stencil.left_index] += 1.0e-16
            history_virtual_direction[query.source_index, stencil.right_index] -= 0.5e-16
        else:
            history_lyman_direction[query.source_index, stencil.left_index] += 1.0e-16
            history_lyman_direction[query.source_index, stencil.right_index] -= 0.5e-16
    error = problem.central_difference_shifted_ijacobian_error(
        state_vector=dae.source_state_vector(state),
        state_derivative=dae.source_derivative_vector(),
        local_direction=local_direction,
        outgoing_virtual_direction=history_virtual_direction,
        outgoing_lyman_direction=history_lyman_direction,
        shift=3.7,
        step=0.5,
    )
    assert error < 1.0e-8


@pytest.mark.slow
def test_typed_owner_backward_euler_is_positive_and_backward_stable() -> None:
    dae, state, history, registry = _real_problem(1100)
    canonical = trajectory.ScalarHistoryOwnerSwapProblem(
        dae=dae,
        history=history,
        registry=registry,
        atomic_state=state,
    )
    problem = canonical.promote_typed(canonical.parity_audit())
    old = np.array(dae.source_state_vector(state), copy=True)
    old[0] *= 1.0001
    result = problem.frozen_coefficient_backward_euler_step(
        old,
        delta_lna=1.0e-5,
    )
    assert result.converged
    assert result.backward_error < 1.0e-11
    assert result.algebraic_residual_relative < 1.0e-11
    assert result.minimum_physical_population > 0.0

@pytest.mark.slow
def test_accepted_step_transaction_commits_once_and_restart_rollback_are_exact() -> None:
    dae, state, history, registry = _real_problem(1100)
    canonical = trajectory.ScalarHistoryOwnerSwapProblem(
        dae=dae,
        history=history,
        registry=registry,
        atomic_state=state,
    )
    problem = canonical.promote_typed(canonical.parity_audit())
    transaction = trajectory.AcceptedStepTransaction.from_problem(
        problem,
        local_state=dae.source_state_vector(state),
        local_derivative=dae.source_derivative_vector(),
        com_restart_payload=dae.primitive_problem.restart_payload(state),
    )
    parent_bytes = history.to_bytes()
    assert transaction.status.value == "PENDING"
    assert transaction.commit_count == 0
    accepted = transaction.commit()
    assert transaction.status.value == "COMMITTED"
    assert transaction.commit_count == 1
    assert accepted.accepted_count == history.accepted_count + 1
    with pytest.raises(RuntimeError, match="finalized"):
        transaction.commit()

    payload = transaction.to_bytes()
    restored = trajectory.AcceptedStepTransaction.from_bytes(payload, problem=problem)
    assert restored.to_bytes() == payload
    assert restored.current_history.to_bytes() == accepted.to_bytes()
    assert restored.parent_history.to_bytes() == parent_bytes
    assert restored.commit_count == 1
    assert restored.com_restart_payload == transaction.com_restart_payload

    rolled_back = restored.rollback_for_event()
    assert rolled_back.to_bytes() == parent_bytes
    assert restored.status.value == "ROLLED_BACK_RESTART_REQUIRED"
    assert restored.restart_required

    rejected = trajectory.AcceptedStepTransaction.from_problem(
        problem,
        local_state=dae.source_state_vector(state),
        local_derivative=dae.source_derivative_vector(),
        com_restart_payload=dae.primitive_problem.restart_payload(state),
    )
    assert rejected.discard().to_bytes() == parent_bytes
    assert rejected.status.value == "DISCARDED"
    assert rejected.commit_count == 0
    with pytest.raises(RuntimeError, match="finalized"):
        rejected.discard()

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.pseudotransient_continuation import (
    AcceptedContinuationState,
    ContinuationTransaction,
    ContinuationTransactionStatus,
    MixedVariableTransform,
    PseudoTransientResult,
    PseudoTransientTolerances,
    project_left_nullspace,
    solve_pseudotransient,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _parent(values=(10.0, -0.25), positive_mask=(True, False)) -> AcceptedContinuationState:
    return AcceptedContinuationState(
        values=np.asarray(values, dtype=float),
        positive_mask=np.asarray(positive_mask, dtype=bool),
        accepted_history_count=7,
        history_sha256=_digest("history"),
        background_sha256=_digest("background"),
        network_sha256=_digest("network"),
        interface_sha256=_digest("interface"),
        branch_id="BIANCHI_II:BRANCH_A",
        event_index=3,
        metadata={"target_z": 1100, "lane": "II"},
    )


def test_accepted_state_hash_is_deterministic_and_provenance_sensitive() -> None:
    first = _parent()
    second = _parent()
    changed = AcceptedContinuationState(
        values=first.values,
        positive_mask=first.positive_mask,
        accepted_history_count=first.accepted_history_count,
        history_sha256=first.history_sha256,
        background_sha256=first.background_sha256,
        network_sha256=_digest("other network"),
        interface_sha256=first.interface_sha256,
        branch_id=first.branch_id,
        event_index=first.event_index,
        metadata=first.metadata,
    )
    assert first.to_bytes() == second.to_bytes()
    assert first.sha256 == second.sha256
    assert changed.sha256 != first.sha256
    with pytest.raises(ValueError):
        _parent(values=(0.0, 1.0))


def test_accepted_state_metadata_is_deeply_immutable_and_source_detached() -> None:
    metadata = {"nested": {"values": [1, 2]}, "label": "original"}
    parent = AcceptedContinuationState(
        values=np.asarray([2.0]),
        positive_mask=np.asarray([True]),
        accepted_history_count=1,
        history_sha256=_digest("history"),
        background_sha256=_digest("background"),
        network_sha256=_digest("network"),
        interface_sha256=_digest("interface"),
        branch_id="BII",
        metadata=metadata,
    )
    before = parent.sha256
    metadata["nested"]["values"].append(3)
    metadata["label"] = "mutated"
    assert parent.sha256 == before
    with pytest.raises(TypeError):
        parent.metadata["label"] = "forbidden"
    with pytest.raises(TypeError):
        parent.metadata["nested"]["new"] = 1


def test_mixed_variable_transform_roundtrip_and_jvp_diagonal() -> None:
    transform = MixedVariableTransform(np.asarray([True, False, True]))
    values = np.asarray([2.0, -3.5, 0.25])
    coordinates = transform.encode(values)
    assert np.allclose(transform.decode(coordinates), values, rtol=0.0, atol=0.0)
    assert np.allclose(
        transform.decode_jacobian_diagonal(coordinates),
        np.asarray([2.0, 1.0, 0.25]),
    )


def test_left_null_projection_is_exact_to_roundoff() -> None:
    rhs = np.asarray([1.0, 2.0, 4.0])
    left = np.asarray([[1.0, 1.0, 1.0]])
    projected = project_left_nullspace(rhs, left)
    assert abs(float((left @ projected).item())) < 1.0e-14
    assert np.allclose(projected, rhs - np.mean(rhs))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"maximum_outer_steps": True},
        {"maximum_outer_steps": 1.5},
        {"maximum_newton_steps": -1},
        {"growth_factor": float("nan")},
        {"shrink_factor": float("inf")},
    ],
)
def test_pseudotransient_policy_rejects_noncanonical_values(kwargs: dict[str, object]) -> None:
    with pytest.raises((TypeError, ValueError)):
        PseudoTransientTolerances(**kwargs)


def test_stiff_scalar_pseudotransient_converges_without_history_commit() -> None:
    parent = _parent(values=(10.0,), positive_mask=(True,))
    rate = 1.0e9
    target = 2.0

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
            maximum_outer_steps=80,
            initial_pseudo_time=1.0e-12,
            maximum_pseudo_time=1.0e6,
        ),
    )
    assert result.converged
    assert result.accepted_history_count == parent.accepted_history_count
    assert np.allclose(result.state_values, np.asarray([target]), rtol=1.0e-11)
    assert all(iteration.minimum_positive_value > 0.0 for iteration in result.iterations)


def test_nonlinear_bose_activity_root_and_restart_are_deterministic() -> None:
    parent = _parent(values=(0.2,), positive_mask=(True,))
    target_activity = 6.0

    def residual(state: np.ndarray) -> np.ndarray:
        f = state[0]
        return np.asarray([f * (1.0 + f) - target_activity])

    def jacobian(state: np.ndarray) -> np.ndarray:
        return np.asarray([[1.0 + 2.0 * state[0]]])

    settings = PseudoTransientTolerances(
        physical_residual=1.0e-11,
        pseudo_backward_error=1.0e-11,
        newton_residual=1.0e-12,
        initial_pseudo_time=0.1,
        maximum_outer_steps=80,
    )
    first = solve_pseudotransient(
        parent,
        residual=residual,
        jacobian=jacobian,
        mass_diagonal=np.asarray([1.0]),
        tolerances=settings,
    )
    second = solve_pseudotransient(
        parent,
        residual=residual,
        jacobian=jacobian,
        mass_diagonal=np.asarray([1.0]),
        tolerances=settings,
    )
    expected = 2.0
    assert first.converged
    assert np.allclose(first.state_values, np.asarray([expected]), rtol=1.0e-10)
    assert first.restart_bytes() == second.restart_bytes()
    assert first.sha256 == second.sha256


def test_signed_only_iteration_uses_none_not_infinity_and_restart_is_json_safe() -> None:
    parent = _parent(values=(2.0,), positive_mask=(False,))

    result = solve_pseudotransient(
        parent,
        residual=lambda state: state - 1.0,
        jacobian=lambda state: np.asarray([[1.0]]),
        mass_diagonal=np.asarray([1.0]),
    )
    assert result.converged
    assert result.iterations
    assert all(item.minimum_positive_value is None for item in result.iterations)
    assert result.restart_bytes()


def test_transaction_reject_rollback_are_byte_exact_and_commit_is_one_shot() -> None:
    parent = _parent(values=(2.0,), positive_mask=(True,))

    def residual(state: np.ndarray) -> np.ndarray:
        return state - 1.0

    def jacobian(state: np.ndarray) -> np.ndarray:
        del state
        return np.asarray([[1.0]])

    result = solve_pseudotransient(
        parent,
        residual=residual,
        jacobian=jacobian,
        mass_diagonal=np.asarray([1.0]),
    )
    assert result.converged

    metric = lambda state: abs(float(state[0] - 1.0))
    rejected = ContinuationTransaction(
        parent, result, admission_metric=metric, maximum_admission_residual=1.0e-10
    )
    before = parent.to_bytes()
    restored = rejected.discard()
    assert restored.to_bytes() == before
    assert rejected.status is ContinuationTransactionStatus.DISCARDED
    assert rejected.commit_count == 0

    rolled = ContinuationTransaction(
        parent, result, admission_metric=metric, maximum_admission_residual=1.0e-10
    )
    assert rolled.rollback().to_bytes() == before
    assert rolled.status is ContinuationTransactionStatus.ROLLED_BACK

    committed_transaction = ContinuationTransaction(
        parent, result, admission_metric=metric, maximum_admission_residual=1.0e-10
    )
    committed = committed_transaction.commit(
        history_sha256=_digest("history after accepted macro"),
        metadata_update={"macro_index": 7},
    )
    assert committed.accepted_history_count == parent.accepted_history_count + 1
    assert committed.parent_sha256 == parent.sha256
    assert committed_transaction.commit_count == 1
    with pytest.raises(RuntimeError):
        committed_transaction.commit(history_sha256=_digest("second commit"))


def test_transaction_recomputes_admission_metric_and_rejects_fabricated_success() -> None:
    parent = _parent(values=(2.0,), positive_mask=(True,))
    fabricated = PseudoTransientResult(
        parent_sha256=parent.sha256,
        state_values=np.asarray([999.0]),
        converged=True,
        iterations=(),
        final_physical_residual=0.0,
        accepted_history_count=parent.accepted_history_count,
    )
    transaction = ContinuationTransaction(
        parent,
        fabricated,
        admission_metric=lambda state: abs(float(state[0] - 1.0)),
        maximum_admission_residual=1.0e-10,
    )
    with pytest.raises(RuntimeError, match="independent admission metric"):
        transaction.commit(history_sha256=_digest("should not commit"))


def test_transaction_commits_only_the_exact_checked_snapshot() -> None:
    parent = _parent(values=(1.0,), positive_mask=(False,))
    result = PseudoTransientResult(
        parent_sha256=parent.sha256,
        state_values=np.asarray([1.0]),
        converged=True,
        iterations=(),
        final_physical_residual=0.0,
        accepted_history_count=parent.accepted_history_count,
    )

    def mutate_result_during_metric(candidate: np.ndarray) -> float:
        with pytest.raises(ValueError):
            candidate.setflags(write=True)
        object.__setattr__(result, "state_values", np.asarray([999.0]))
        return 0.0

    transaction = ContinuationTransaction(
        parent,
        result,
        admission_metric=mutate_result_during_metric,
        maximum_admission_residual=1.0e-12,
    )
    with pytest.raises(RuntimeError, match="identity changed during admission"):
        transaction.commit(history_sha256=_digest("toctou-history"))
    assert transaction.commit_count == 0
    assert transaction.status is ContinuationTransactionStatus.PENDING

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.pseudotransient_continuation import (
    AcceptedContinuationState,
    ContinuationTransaction,
    ContinuationTransactionStatus,
    MixedVariableTransform,
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

    rejected = ContinuationTransaction(parent, result)
    before = parent.to_bytes()
    restored = rejected.discard()
    assert restored.to_bytes() == before
    assert rejected.status is ContinuationTransactionStatus.DISCARDED
    assert rejected.commit_count == 0

    rolled = ContinuationTransaction(parent, result)
    assert rolled.rollback().to_bytes() == before
    assert rolled.status is ContinuationTransactionStatus.ROLLED_BACK

    committed_transaction = ContinuationTransaction(parent, result)
    committed = committed_transaction.commit(
        history_sha256=_digest("history after accepted macro"),
        metadata_update={"macro_index": 7},
    )
    assert committed.accepted_history_count == parent.accepted_history_count + 1
    assert committed.parent_sha256 == parent.sha256
    assert committed_transaction.commit_count == 1
    with pytest.raises(RuntimeError):
        committed_transaction.commit(history_sha256=_digest("second commit"))

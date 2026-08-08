from __future__ import annotations

import numpy as np

from full_bianchi_hyrec.trajectory.macro_evidence_integrity import (
    audit_backward_euler_parent,
)


def test_backward_euler_parent_audit_rejects_nonpositive_implied_parent() -> None:
    final = np.asarray([1.0, 2.0])
    action = np.asarray([2.0, -1.0])

    audit = audit_backward_euler_parent(final, action, dt_s=1.0)

    assert np.array_equal(audit.implied_parent, np.asarray([-1.0, 3.0]))
    assert audit.nonpositive_parent_count == 1
    assert audit.max_strictly_positive_dt_s == 0.5
    assert audit.dt_to_positivity_limit_ratio == 2.0
    assert audit.strictly_positive_parent_exists is False
    assert audit.classification == "INCONSISTENT_WITH_STRICTLY_POSITIVE_BACKWARD_EULER_PARENT"


def test_backward_euler_parent_audit_accepts_positive_implied_parent() -> None:
    final = np.asarray([[2.0, 3.0], [4.0, 5.0]])
    action = np.asarray([[1.0, -2.0], [0.0, 0.5]])

    audit = audit_backward_euler_parent(final, action, dt_s=0.25)

    assert np.all(audit.implied_parent > 0.0)
    assert audit.nonpositive_parent_count == 0
    assert audit.max_strictly_positive_dt_s == 2.0
    assert audit.dt_to_positivity_limit_ratio == 0.125
    assert audit.strictly_positive_parent_exists is True
    assert audit.classification == "CONSISTENT_WITH_A_STRICTLY_POSITIVE_BACKWARD_EULER_PARENT"


def test_backward_euler_parent_audit_requires_positive_finite_final_state_and_timestep() -> None:
    with np.testing.assert_raises(ValueError):
        audit_backward_euler_parent(np.asarray([0.0]), np.asarray([1.0]), dt_s=1.0)
    with np.testing.assert_raises(ValueError):
        audit_backward_euler_parent(np.asarray([1.0]), np.asarray([1.0]), dt_s=0.0)
    with np.testing.assert_raises(ValueError):
        audit_backward_euler_parent(np.asarray([1.0]), np.asarray([np.nan]), dt_s=1.0)

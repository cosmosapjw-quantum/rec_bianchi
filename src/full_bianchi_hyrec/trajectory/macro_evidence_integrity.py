"""Integrity audits for recorded implicit macro-step evidence.

The audit is intentionally independent of any unknown parent state.  For a
recorded backward-Euler endpoint ``f_star`` and the durable semidiscrete action
``A(f_star)``, the only compatible parent is

``f_parent = f_star - dt * A(f_star)``.

If any component of that parent is nonpositive, no strictly-positive parent can
produce the recorded endpoint under the stated timestep and operator.  This is
a necessary-condition audit, not a replacement nonlinear solver.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class BackwardEulerParentAudit:
    """Necessary positivity audit for a recorded backward-Euler endpoint."""

    implied_parent: np.ndarray
    nonpositive_parent_count: int
    implied_parent_minimum: float
    implied_parent_maximum: float
    maximum_action_abs: float
    max_strictly_positive_dt_s: float
    dt_to_positivity_limit_ratio: float
    strictly_positive_parent_exists: bool
    classification: str


def _immutable(array: np.ndarray) -> np.ndarray:
    result = np.array(array, dtype=float, copy=True)
    result.setflags(write=False)
    return result


def audit_backward_euler_parent(
    final_occupation: np.ndarray,
    action_s_inv: np.ndarray,
    *,
    dt_s: float,
) -> BackwardEulerParentAudit:
    """Audit whether a positive parent can yield a recorded implicit endpoint.

    Parameters
    ----------
    final_occupation:
        Strictly-positive endpoint occupation, dimensionless.
    action_s_inv:
        Semidiscrete right-hand side evaluated at the endpoint, in ``s^-1``.
    dt_s:
        Recorded backward-Euler timestep in seconds.
    """

    final = np.asarray(final_occupation, dtype=float)
    action = np.asarray(action_s_inv, dtype=float)
    dt = float(dt_s)
    if final.shape != action.shape:
        raise ValueError("final_occupation and action_s_inv shape mismatch")
    if final.size == 0:
        raise ValueError("final_occupation must be nonempty")
    if not np.all(np.isfinite(final)) or np.any(final <= 0.0):
        raise ValueError("final_occupation must be finite and strictly positive")
    if not np.all(np.isfinite(action)):
        raise ValueError("action_s_inv must be finite")
    if not math.isfinite(dt) or dt <= 0.0:
        raise ValueError("dt_s must be positive and finite")

    implied = final - dt * action
    nonpositive = int(np.count_nonzero(implied <= 0.0))
    positive_action = action > 0.0
    if np.any(positive_action):
        maximum_dt = float(np.min(final[positive_action] / action[positive_action]))
        ratio = dt / maximum_dt
    else:
        maximum_dt = math.inf
        ratio = 0.0
    consistent = nonpositive == 0
    classification = (
        "CONSISTENT_WITH_A_STRICTLY_POSITIVE_BACKWARD_EULER_PARENT"
        if consistent
        else "INCONSISTENT_WITH_STRICTLY_POSITIVE_BACKWARD_EULER_PARENT"
    )
    return BackwardEulerParentAudit(
        implied_parent=_immutable(implied),
        nonpositive_parent_count=nonpositive,
        implied_parent_minimum=float(np.min(implied)),
        implied_parent_maximum=float(np.max(implied)),
        maximum_action_abs=float(np.max(np.abs(action))),
        max_strictly_positive_dt_s=maximum_dt,
        dt_to_positivity_limit_ratio=float(ratio),
        strictly_positive_parent_exists=consistent,
        classification=classification,
    )


__all__ = ["BackwardEulerParentAudit", "audit_backward_euler_parent"]

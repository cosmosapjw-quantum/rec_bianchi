"""Physical-residual adapter for accepted-state pseudo-transient continuation.

This module connects the bounded pseudo-transient infrastructure to the durable
COM--KHW collision plus Bianchi frequency-transport operator.  It does not yet
claim a converged canonical macro trajectory.  Its purpose is narrower:

* expose the physical backward-Euler residual in occupation variables;
* expose an analytic matrix-free JVP in the same variables;
* enforce the existing gross-residual and photon-number acceptance gates; and
* provide the shifted pseudo-transient equation without mutating accepted
  original-HyRec history.

The adapter deliberately keeps the physical parent state immutable.  Positive
occupations are supplied to the nonlinear solver in logarithmic coordinates by
``pseudotransient_continuation.MixedVariableTransform``.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np
from scipy.sparse.linalg import LinearOperator

from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
    CoupledCollisionTransportProblem,
)


def _positive_vector(value: Sequence[float], *, size: int | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1 or (size is not None and array.size != size):
        raise ValueError("state must be a one-dimensional vector of the expected size")
    if not np.all(np.isfinite(array)) or np.any(array <= 0.0):
        raise ValueError("physical occupation must be finite and strictly positive")
    return np.array(array, dtype=float, copy=True)


@dataclass(frozen=True)
class PhysicalContinuationAssessment:
    """Problem-specific macro acceptance metrics.

    ``gross_backward_error`` is the residual normalized by all gross collision,
    transport, interface and state terms.  ``number_relative_residual`` is an
    independent conservation gate.  A macro candidate is admissible only when
    both pass; the small net-scaled diagnostic is retained but is not allowed to
    replace the componentwise gates.
    """

    net_scaled_residual: float
    gross_backward_error: float
    number_relative_residual: float
    minimum_occupation: float

    def __post_init__(self) -> None:
        for name in (
            "net_scaled_residual",
            "gross_backward_error",
            "number_relative_residual",
            "minimum_occupation",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
            object.__setattr__(self, name, value)

    @property
    def convergence_metric(self) -> float:
        return max(self.gross_backward_error, self.number_relative_residual)

    def passed(self, *, tolerance: float) -> bool:
        threshold = float(tolerance)
        if not math.isfinite(threshold) or threshold <= 0.0:
            raise ValueError("tolerance must be positive and finite")
        return bool(
            self.minimum_occupation > 0.0
            and self.gross_backward_error <= threshold
            and self.number_relative_residual <= threshold
        )


@dataclass(frozen=True)
class CoupledPhysicalContinuationAdapter:
    """Flattened physical-variable view of one coupled macro residual."""

    problem: CoupledCollisionTransportProblem
    parent_occupation: np.ndarray

    def __post_init__(self) -> None:
        parent = np.asarray(self.parent_occupation, dtype=float)
        if parent.shape != self.problem.shape:
            raise ValueError("parent_occupation shape does not match the problem")
        if not np.all(np.isfinite(parent)) or np.any(parent <= 0.0):
            raise ValueError("parent occupation must be finite and strictly positive")
        parent = np.array(parent, dtype=float, copy=True)
        parent.setflags(write=False)
        object.__setattr__(self, "parent_occupation", parent)

    @property
    def size(self) -> int:
        return int(self.parent_occupation.size)

    @property
    def shape(self) -> tuple[int, int]:
        return self.problem.shape

    def _state(self, value: Sequence[float]) -> np.ndarray:
        return _positive_vector(value, size=self.size).reshape(self.shape)

    def residual(self, state: Sequence[float]) -> np.ndarray:
        occupation = self._state(state)
        return self.problem.residual(
            np.log(occupation), self.parent_occupation
        ).ravel()

    def jvp(self, state: Sequence[float], direction: Sequence[float]) -> np.ndarray:
        occupation = self._state(state)
        delta = np.asarray(direction, dtype=float)
        if delta.shape != (self.size,) or not np.all(np.isfinite(delta)):
            raise ValueError("direction must be a finite vector matching the state")
        log_direction = delta.reshape(self.shape) / occupation
        return self.problem.residual_jvp(
            np.log(occupation), log_direction
        ).ravel()

    def assess(self, state: Sequence[float]) -> PhysicalContinuationAssessment:
        occupation = self._state(state)
        metrics = self.problem.residual_metrics(
            np.log(occupation), self.parent_occupation
        )
        return PhysicalContinuationAssessment(
            net_scaled_residual=metrics.net_scaled_residual,
            gross_backward_error=metrics.gross_backward_error,
            number_relative_residual=metrics.number_relative_residual,
            minimum_occupation=float(np.min(occupation)),
        )

    def convergence_metric(self, state: Sequence[float]) -> float:
        """Return the componentwise hard-gate metric used by continuation."""

        return self.assess(state).convergence_metric

    def pseudo_equation(
        self,
        state: Sequence[float],
        *,
        old_state: Sequence[float],
        pseudo_time: float,
        mass_diagonal: Sequence[float],
    ) -> np.ndarray:
        occupation = self._state(state).ravel()
        old = _positive_vector(old_state, size=self.size)
        mass = np.asarray(mass_diagonal, dtype=float)
        tau = float(pseudo_time)
        if mass.shape != (self.size,) or not np.all(np.isfinite(mass)) or np.any(mass < 0.0):
            raise ValueError("mass_diagonal must be finite, nonnegative, and match state")
        if not math.isfinite(tau) or tau <= 0.0:
            raise ValueError("pseudo_time must be positive and finite")
        return mass * (occupation - old) / tau + self.residual(occupation)

    def shifted_jvp(
        self,
        state: Sequence[float],
        direction: Sequence[float],
        *,
        old_state: Sequence[float],
        pseudo_time: float,
        mass_diagonal: Sequence[float],
    ) -> np.ndarray:
        # Validate old_state even though its derivative is zero: it is part of
        # the immutable pseudo-step contract.
        _positive_vector(old_state, size=self.size)
        delta = np.asarray(direction, dtype=float)
        mass = np.asarray(mass_diagonal, dtype=float)
        tau = float(pseudo_time)
        if delta.shape != (self.size,) or not np.all(np.isfinite(delta)):
            raise ValueError("direction must be finite and match state")
        if mass.shape != (self.size,) or not np.all(np.isfinite(mass)) or np.any(mass < 0.0):
            raise ValueError("mass_diagonal must be finite, nonnegative, and match state")
        if not math.isfinite(tau) or tau <= 0.0:
            raise ValueError("pseudo_time must be positive and finite")
        return mass * delta / tau + self.jvp(state, delta)

    def shifted_linear_operator(
        self,
        state: Sequence[float],
        *,
        old_state: Sequence[float],
        pseudo_time: float,
        mass_diagonal: Sequence[float],
    ) -> LinearOperator:
        occupation = self._state(state).ravel()
        old = _positive_vector(old_state, size=self.size)
        mass = np.asarray(mass_diagonal, dtype=float)
        tau = float(pseudo_time)

        def matvec(direction: np.ndarray) -> np.ndarray:
            return self.shifted_jvp(
                occupation,
                direction,
                old_state=old,
                pseudo_time=tau,
                mass_diagonal=mass,
            )

        return LinearOperator((self.size, self.size), matvec=matvec, dtype=float)


__all__ = [
    "CoupledPhysicalContinuationAdapter",
    "PhysicalContinuationAssessment",
]


def build_production_continuation_adapter(
    *,
    problem: CoupledCollisionTransportProblem,
    parent,
    requirements,
) -> CoupledPhysicalContinuationAdapter:
    """Fail-closed production entry from a provenance-locked accepted parent.

    The low-level :class:`CoupledPhysicalContinuationAdapter` constructor is
    retained for bounded operator audits.  Production code must enter through
    this factory so manufactured and operator-verification fixtures cannot be
    mistaken for accepted trajectory states.
    """

    from full_bianchi_hyrec.trajectory.accepted_parent import (
        AcceptedRadiationParent,
        ProductionParentRequirements,
    )

    if not isinstance(parent, AcceptedRadiationParent):
        raise TypeError("parent must be an AcceptedRadiationParent")
    if not isinstance(requirements, ProductionParentRequirements):
        raise TypeError("requirements must be ProductionParentRequirements")
    parent.validate_for_production(requirements)
    if parent.occupation.shape != problem.shape:
        raise ValueError("accepted parent occupation shape does not match problem")
    return CoupledPhysicalContinuationAdapter(problem, parent.occupation)


__all__.append("build_production_continuation_adapter")

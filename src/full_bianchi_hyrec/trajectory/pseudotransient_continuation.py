"""Accepted-state pseudo-transient continuation reference infrastructure.

This module is the bounded PR-05C2C1B2B1A/v0.70-P0 recovery implementation.
It deliberately does *not* connect the full Bianchi--HyRec physical residual.
Instead it supplies the transaction, positivity, restart, nullspace, and dense
pseudo-transient reference contracts needed before that coupling is attempted.

A pseudo-step is an internal nonlinear globalization step.  It never appends an
original-HyRec accepted-history slice.  Only a separately authorized macro
commit may increment ``accepted_history_count``.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import struct
from typing import Callable, Mapping, Sequence

import numpy as np


_SHA256_HEX = frozenset("0123456789abcdef")
_SCHEMA = "PR05C2C1B2B1A_ACCEPTED_CONTINUATION_STATE_V1"


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in _SHA256_HEX for character in value)


def _immutable_float_vector(value: Sequence[float], *, name: str) -> np.ndarray:
    array = np.asarray(value, dtype="<f8")
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be a finite nonempty one-dimensional vector")
    result = np.array(array, dtype="<f8", copy=True)
    result.setflags(write=False)
    return result


def _immutable_bool_vector(value: Sequence[bool], *, size: int, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.bool_)
    if array.ndim != 1 or array.size != size:
        raise ValueError(f"{name} must be a one-dimensional vector of length {size}")
    result = np.array(array, dtype=np.bool_, copy=True)
    result.setflags(write=False)
    return result


def _canonical_json_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(
        dict(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class AcceptedContinuationState:
    """Content-addressed accepted macro parent.

    ``values`` may mix strictly-positive physical variables and signed departure
    variables.  ``positive_mask`` declares which entries use logarithmic solver
    coordinates.  Provenance digests bind the state to the durable history,
    background, thermodynamic network, and interface accumulator inputs.
    """

    values: np.ndarray
    positive_mask: np.ndarray
    accepted_history_count: int
    history_sha256: str
    background_sha256: str
    network_sha256: str
    interface_sha256: str
    branch_id: str
    event_index: int = 0
    parent_sha256: str | None = None
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        values = _immutable_float_vector(self.values, name="values")
        mask = _immutable_bool_vector(
            self.positive_mask, size=values.size, name="positive_mask"
        )
        if np.any(values[mask] <= 0.0):
            raise ValueError("positive-mask state entries must be strictly positive")
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "positive_mask", mask)

        count = int(self.accepted_history_count)
        event_index = int(self.event_index)
        if count < 1 or event_index < 0:
            raise ValueError("accepted_history_count must be >=1 and event_index nonnegative")
        object.__setattr__(self, "accepted_history_count", count)
        object.__setattr__(self, "event_index", event_index)

        for name in (
            "history_sha256",
            "background_sha256",
            "network_sha256",
            "interface_sha256",
        ):
            digest = str(getattr(self, name)).lower()
            if not _is_sha256(digest):
                raise ValueError(f"{name} must be a SHA-256 hexadecimal digest")
            object.__setattr__(self, name, digest)

        parent = self.parent_sha256
        if parent is not None:
            parent = str(parent).lower()
            if not _is_sha256(parent):
                raise ValueError("parent_sha256 must be None or a SHA-256 digest")
        object.__setattr__(self, "parent_sha256", parent)

        branch = str(self.branch_id)
        if not branch:
            raise ValueError("branch_id is required")
        object.__setattr__(self, "branch_id", branch)

        metadata = {} if self.metadata is None else dict(self.metadata)
        # Validate serializability now, not at a later restart boundary.
        _canonical_json_bytes(metadata)
        object.__setattr__(self, "metadata", metadata)

    def to_bytes(self) -> bytes:
        header = {
            "schema": _SCHEMA,
            "size": int(self.values.size),
            "accepted_history_count": self.accepted_history_count,
            "history_sha256": self.history_sha256,
            "background_sha256": self.background_sha256,
            "network_sha256": self.network_sha256,
            "interface_sha256": self.interface_sha256,
            "branch_id": self.branch_id,
            "event_index": self.event_index,
            "parent_sha256": self.parent_sha256,
            "metadata": dict(self.metadata),
        }
        header_bytes = _canonical_json_bytes(header)
        return b"".join(
            (
                struct.pack("<Q", len(header_bytes)),
                header_bytes,
                self.positive_mask.astype(np.uint8, copy=False).tobytes(order="C"),
                self.values.astype("<f8", copy=False).tobytes(order="C"),
            )
        )

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.to_bytes()).hexdigest()

    def with_values(self, values: Sequence[float]) -> "AcceptedContinuationState":
        """Return an uncommitted state view with identical provenance/count."""

        return AcceptedContinuationState(
            values=np.asarray(values, dtype=float),
            positive_mask=self.positive_mask,
            accepted_history_count=self.accepted_history_count,
            history_sha256=self.history_sha256,
            background_sha256=self.background_sha256,
            network_sha256=self.network_sha256,
            interface_sha256=self.interface_sha256,
            branch_id=self.branch_id,
            event_index=self.event_index,
            parent_sha256=self.parent_sha256,
            metadata=self.metadata,
        )


@dataclass(frozen=True)
class MixedVariableTransform:
    """Log-positive / identity-signed coordinate transform."""

    positive_mask: np.ndarray

    def __post_init__(self) -> None:
        mask = np.asarray(self.positive_mask, dtype=np.bool_)
        if mask.ndim != 1 or mask.size == 0:
            raise ValueError("positive_mask must be a nonempty one-dimensional vector")
        mask = np.array(mask, copy=True)
        mask.setflags(write=False)
        object.__setattr__(self, "positive_mask", mask)

    def encode(self, values: Sequence[float]) -> np.ndarray:
        values_array = _immutable_float_vector(values, name="values")
        if values_array.size != self.positive_mask.size:
            raise ValueError("values and positive_mask sizes differ")
        if np.any(values_array[self.positive_mask] <= 0.0):
            raise ValueError("positive variables must be strictly positive")
        encoded = np.array(values_array, copy=True)
        encoded[self.positive_mask] = np.log(values_array[self.positive_mask])
        return encoded

    def decode(self, coordinates: Sequence[float]) -> np.ndarray:
        coordinates_array = _immutable_float_vector(coordinates, name="coordinates")
        if coordinates_array.size != self.positive_mask.size:
            raise ValueError("coordinates and positive_mask sizes differ")
        decoded = np.array(coordinates_array, copy=True)
        decoded[self.positive_mask] = np.exp(coordinates_array[self.positive_mask])
        if not np.all(np.isfinite(decoded)):
            raise FloatingPointError("coordinate decode produced nonfinite values")
        return decoded

    def decode_jacobian_diagonal(self, coordinates: Sequence[float]) -> np.ndarray:
        decoded = self.decode(coordinates)
        diagonal = np.ones(decoded.size, dtype=float)
        diagonal[self.positive_mask] = decoded[self.positive_mask]
        return diagonal


def project_left_nullspace(
    rhs: Sequence[float], left_null_vectors: np.ndarray | Sequence[Sequence[float]]
) -> np.ndarray:
    """Project ``rhs`` orthogonally away from known left-null vectors.

    The columns/rows supplied by callers may be non-orthonormal.  A reduced QR
    factorization constructs an orthonormal basis before projection.
    """

    vector = _immutable_float_vector(rhs, name="rhs")
    basis = np.asarray(left_null_vectors, dtype=float)
    if basis.ndim == 1:
        basis = basis.reshape(1, -1)
    if basis.ndim != 2 or basis.shape[1] != vector.size or not np.all(np.isfinite(basis)):
        raise ValueError("left_null_vectors must have shape (k, rhs.size)")
    if basis.shape[0] == 0:
        return np.array(vector, copy=True)
    # QR on transposed rows: q columns span the left-null row space.
    q, r = np.linalg.qr(basis.T, mode="reduced")
    if np.any(np.abs(np.diag(r)) <= 100.0 * np.finfo(float).eps):
        raise ValueError("left-null vectors are linearly dependent or numerically zero")
    return np.asarray(vector - q @ (q.T @ vector), dtype=float)


@dataclass(frozen=True)
class PseudoTransientTolerances:
    physical_residual: float = 1.0e-11
    pseudo_backward_error: float = 1.0e-11
    newton_residual: float = 1.0e-12
    maximum_outer_steps: int = 80
    maximum_newton_steps: int = 20
    initial_pseudo_time: float = 1.0
    minimum_pseudo_time: float = 1.0e-16
    maximum_pseudo_time: float = 1.0e16
    growth_factor: float = 2.0
    shrink_factor: float = 0.25
    minimum_line_search: float = 2.0**-20

    def __post_init__(self) -> None:
        for name in ("physical_residual", "pseudo_backward_error", "newton_residual"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be positive and finite")
            object.__setattr__(self, name, value)
        outer = int(self.maximum_outer_steps)
        newton = int(self.maximum_newton_steps)
        if outer <= 0 or newton <= 0:
            raise ValueError("iteration limits must be positive")
        object.__setattr__(self, "maximum_outer_steps", outer)
        object.__setattr__(self, "maximum_newton_steps", newton)
        minimum = float(self.minimum_pseudo_time)
        initial = float(self.initial_pseudo_time)
        maximum = float(self.maximum_pseudo_time)
        if not (0.0 < minimum <= initial <= maximum) or not all(
            math.isfinite(value) for value in (minimum, initial, maximum)
        ):
            raise ValueError("pseudo-time bounds must satisfy 0 < min <= initial <= max")
        object.__setattr__(self, "minimum_pseudo_time", minimum)
        object.__setattr__(self, "initial_pseudo_time", initial)
        object.__setattr__(self, "maximum_pseudo_time", maximum)
        growth = float(self.growth_factor)
        shrink = float(self.shrink_factor)
        line = float(self.minimum_line_search)
        if growth <= 1.0 or not (0.0 < shrink < 1.0) or not (0.0 < line <= 1.0):
            raise ValueError("controller factors are invalid")
        object.__setattr__(self, "growth_factor", growth)
        object.__setattr__(self, "shrink_factor", shrink)
        object.__setattr__(self, "minimum_line_search", line)


@dataclass(frozen=True)
class PseudoTransientIteration:
    outer_index: int
    pseudo_time: float
    accepted: bool
    physical_residual: float
    pseudo_backward_error: float
    newton_steps: int
    minimum_positive_value: float


@dataclass(frozen=True)
class PseudoTransientResult:
    parent_sha256: str
    state_values: np.ndarray
    converged: bool
    iterations: tuple[PseudoTransientIteration, ...]
    final_physical_residual: float
    accepted_history_count: int

    def __post_init__(self) -> None:
        if not _is_sha256(str(self.parent_sha256).lower()):
            raise ValueError("parent_sha256 must be a SHA-256 digest")
        object.__setattr__(self, "parent_sha256", str(self.parent_sha256).lower())
        values = _immutable_float_vector(self.state_values, name="state_values")
        object.__setattr__(self, "state_values", values)
        object.__setattr__(self, "iterations", tuple(self.iterations))
        residual = float(self.final_physical_residual)
        if not math.isfinite(residual) or residual < 0.0:
            raise ValueError("final_physical_residual must be finite and nonnegative")
        object.__setattr__(self, "final_physical_residual", residual)
        count = int(self.accepted_history_count)
        if count < 1:
            raise ValueError("accepted_history_count must be positive")
        object.__setattr__(self, "accepted_history_count", count)

    def restart_bytes(self) -> bytes:
        header = _canonical_json_bytes(
            {
                "schema": "PR05C2C1B2B1A_PSEUDOTRANSIENT_RESULT_V1",
                "parent_sha256": self.parent_sha256,
                "converged": bool(self.converged),
                "accepted_history_count": self.accepted_history_count,
                "final_physical_residual": self.final_physical_residual,
                "iterations": [iteration.__dict__ for iteration in self.iterations],
            }
        )
        return struct.pack("<Q", len(header)) + header + self.state_values.tobytes(order="C")

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.restart_bytes()).hexdigest()


ResidualFunction = Callable[[np.ndarray], np.ndarray]
JacobianFunction = Callable[[np.ndarray], np.ndarray]
ConvergenceMetricFunction = Callable[[np.ndarray], float]


def _relative_state_scale(*states: np.ndarray) -> np.ndarray:
    """Component scale without a dimensionless unit-floor.

    Occupations in the recombination problem are routinely O(1e-18).  A hard
    floor of one makes ``|J| scale`` larger than the actual operator scale by
    eighteen orders of magnitude and can falsely label a non-root as converged.
    The floor here is relative to the largest supplied state component.
    """

    arrays = tuple(np.asarray(state, dtype=float) for state in states)
    if not arrays or any(array.shape != arrays[0].shape for array in arrays):
        raise ValueError("state scales require at least one common-shape vector")
    maximum = max(float(np.max(np.abs(array), initial=0.0)) for array in arrays)
    floor = max(np.sqrt(np.finfo(float).eps) * maximum, np.finfo(float).tiny)
    components = tuple(np.abs(array) for array in arrays)
    return np.maximum.reduce(components + (np.full_like(arrays[0], floor),))


def _physical_backward_error(
    residual_vector: np.ndarray,
    state: np.ndarray,
    derivative: np.ndarray,
) -> float:
    """Normwise local backward error for a stiff nonlinear residual.

    The state scale is relative to the physical variables, not to an arbitrary
    dimensionless value of one.  This prevents tiny occupation vectors from
    receiving a fictitiously enormous ``|J|`` normalization.
    """

    state_scale = _relative_state_scale(state)
    operator_scale = np.abs(derivative) @ state_scale
    scale = np.maximum.reduce(
        (state_scale, operator_scale, np.full_like(state_scale, np.finfo(float).tiny))
    )
    return float(np.max(np.abs(residual_vector) / scale))


def _pseudo_backward_error(
    equation: np.ndarray,
    state: np.ndarray,
    old_state: np.ndarray,
    pseudo_time: float,
    mass_diagonal: np.ndarray,
    physical_residual: np.ndarray,
    derivative: np.ndarray,
) -> float:
    """Cancellation-safe normwise backward error for a pseudo-step."""

    mass_coefficient = mass_diagonal / pseudo_time
    state_scale = _relative_state_scale(state, old_state)
    linearized_scale = (
        mass_coefficient * state_scale
        + np.abs(derivative) @ state_scale
        + np.abs(physical_residual)
    )
    scale = np.maximum.reduce(
        (state_scale, linearized_scale, np.full_like(state_scale, np.finfo(float).tiny))
    )
    return float(np.max(np.abs(equation) / scale))


def solve_pseudotransient(
    parent: AcceptedContinuationState,
    *,
    residual: ResidualFunction,
    jacobian: JacobianFunction,
    mass_diagonal: Sequence[float],
    tolerances: PseudoTransientTolerances | None = None,
    convergence_metric: ConvergenceMetricFunction | None = None,
) -> PseudoTransientResult:
    """Solve a nonlinear macro residual by dense pseudo-transient continuation.

    This is an audit/reference solver.  It intentionally uses dense linear
    algebra and never commits the accepted-history count.  The returned state is
    a *candidate* tied to ``parent.sha256``.
    """

    settings = PseudoTransientTolerances() if tolerances is None else tolerances
    mass = np.asarray(mass_diagonal, dtype=float)
    if mass.shape != parent.values.shape or not np.all(np.isfinite(mass)) or np.any(mass < 0.0):
        raise ValueError("mass_diagonal must be finite, nonnegative, and match the state")
    transform = MixedVariableTransform(parent.positive_mask)
    state = np.array(parent.values, copy=True)
    pseudo_time = settings.initial_pseudo_time
    records: list[PseudoTransientIteration] = []

    initial_residual = np.asarray(residual(state), dtype=float)
    initial_derivative = np.asarray(jacobian(state), dtype=float)
    if initial_residual.shape != state.shape or not np.all(np.isfinite(initial_residual)):
        raise ValueError("residual returned invalid shape or nonfinite values")
    if initial_derivative.shape != (state.size, state.size) or not np.all(
        np.isfinite(initial_derivative)
    ):
        raise ValueError("jacobian returned invalid shape or nonfinite values")
    if convergence_metric is None:
        physical_norm = _physical_backward_error(
            initial_residual, state, initial_derivative
        )
    else:
        physical_norm = float(convergence_metric(state))
        if not math.isfinite(physical_norm) or physical_norm < 0.0:
            raise ValueError("convergence_metric must return a finite nonnegative value")
    if physical_norm <= settings.physical_residual:
        return PseudoTransientResult(
            parent_sha256=parent.sha256,
            state_values=state,
            converged=True,
            iterations=(),
            final_physical_residual=physical_norm,
            accepted_history_count=parent.accepted_history_count,
        )

    for outer in range(settings.maximum_outer_steps):
        old_state = np.array(state, copy=True)
        coordinates = transform.encode(old_state)
        newton_converged = False
        newton_count = 0
        final_backward = math.inf

        for inner in range(settings.maximum_newton_steps):
            newton_count = inner + 1
            trial_state = transform.decode(coordinates)
            physical = np.asarray(residual(trial_state), dtype=float)
            derivative = np.asarray(jacobian(trial_state), dtype=float)
            if physical.shape != state.shape or derivative.shape != (state.size, state.size):
                raise ValueError("residual/jacobian returned invalid shape")
            if not np.all(np.isfinite(physical)) or not np.all(np.isfinite(derivative)):
                raise FloatingPointError("residual/jacobian returned nonfinite values")
            mass_term = mass * (trial_state - old_state) / pseudo_time
            equation = mass_term + physical
            final_backward = _pseudo_backward_error(
                equation,
                trial_state,
                old_state,
                pseudo_time,
                mass,
                physical,
                derivative,
            )
            if final_backward <= settings.newton_residual:
                newton_converged = True
                break

            decode_diagonal = transform.decode_jacobian_diagonal(coordinates)
            shifted = derivative + np.diag(mass / pseudo_time)
            coordinate_jacobian = shifted * decode_diagonal[np.newaxis, :]
            try:
                step = np.linalg.solve(coordinate_jacobian, -equation)
            except np.linalg.LinAlgError:
                step = np.linalg.lstsq(coordinate_jacobian, -equation, rcond=None)[0]
            if not np.all(np.isfinite(step)):
                break

            base_norm = float(np.max(np.abs(equation)))
            line = 1.0
            accepted_line = False
            while line >= settings.minimum_line_search:
                candidate_coordinates = coordinates + line * step
                candidate_state = transform.decode(candidate_coordinates)
                candidate_physical = np.asarray(residual(candidate_state), dtype=float)
                candidate_mass = mass * (candidate_state - old_state) / pseudo_time
                candidate_equation = candidate_mass + candidate_physical
                candidate_norm = float(np.max(np.abs(candidate_equation)))
                if math.isfinite(candidate_norm) and candidate_norm < base_norm:
                    coordinates = candidate_coordinates
                    accepted_line = True
                    break
                line *= 0.5
            if not accepted_line:
                break

        candidate_state = transform.decode(coordinates)
        candidate_physical = np.asarray(residual(candidate_state), dtype=float)
        candidate_derivative = np.asarray(jacobian(candidate_state), dtype=float)
        if convergence_metric is None:
            candidate_physical_norm = _physical_backward_error(
                candidate_physical, candidate_state, candidate_derivative
            )
        else:
            candidate_physical_norm = float(convergence_metric(candidate_state))
            if not math.isfinite(candidate_physical_norm) or candidate_physical_norm < 0.0:
                raise ValueError(
                    "convergence_metric must return a finite nonnegative value"
                )
        minimum_positive = (
            float(np.min(candidate_state[parent.positive_mask]))
            if np.any(parent.positive_mask)
            else math.inf
        )
        improved = candidate_physical_norm < physical_norm
        accepted = bool(
            newton_converged
            and final_backward <= settings.pseudo_backward_error
            and improved
            and minimum_positive > 0.0
        )
        records.append(
            PseudoTransientIteration(
                outer_index=outer,
                pseudo_time=float(pseudo_time),
                accepted=accepted,
                physical_residual=float(candidate_physical_norm),
                pseudo_backward_error=float(final_backward),
                newton_steps=newton_count,
                minimum_positive_value=minimum_positive,
            )
        )
        if accepted:
            state = candidate_state
            physical_norm = candidate_physical_norm
            if physical_norm <= settings.physical_residual:
                return PseudoTransientResult(
                    parent_sha256=parent.sha256,
                    state_values=state,
                    converged=True,
                    iterations=tuple(records),
                    final_physical_residual=physical_norm,
                    accepted_history_count=parent.accepted_history_count,
                )
            pseudo_time = min(
                settings.maximum_pseudo_time, pseudo_time * settings.growth_factor
            )
        else:
            pseudo_time *= settings.shrink_factor
            if pseudo_time < settings.minimum_pseudo_time:
                break

    return PseudoTransientResult(
        parent_sha256=parent.sha256,
        state_values=state,
        converged=False,
        iterations=tuple(records),
        final_physical_residual=physical_norm,
        accepted_history_count=parent.accepted_history_count,
    )


class ContinuationTransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMMITTED = "COMMITTED"
    DISCARDED = "DISCARDED"
    ROLLED_BACK = "ROLLED_BACK"


class ContinuationTransaction:
    """One-shot macro transaction around a pseudo-transient candidate."""

    def __init__(
        self,
        parent: AcceptedContinuationState,
        result: PseudoTransientResult,
    ) -> None:
        if result.parent_sha256 != parent.sha256:
            raise ValueError("pseudo-transient result belongs to a different parent")
        if result.accepted_history_count != parent.accepted_history_count:
            raise ValueError("pseudo-steps may not mutate accepted-history count")
        self.parent = parent
        self.result = result
        self.status = ContinuationTransactionStatus.PENDING
        self.commit_count = 0

    def commit(
        self,
        *,
        history_sha256: str,
        interface_sha256: str | None = None,
        metadata_update: Mapping[str, object] | None = None,
    ) -> AcceptedContinuationState:
        if self.status is not ContinuationTransactionStatus.PENDING:
            raise RuntimeError("transaction is no longer pending")
        if not self.result.converged:
            raise RuntimeError("cannot commit a nonconverged pseudo-transient result")
        metadata = dict(self.parent.metadata)
        if metadata_update is not None:
            metadata.update(dict(metadata_update))
        committed = AcceptedContinuationState(
            values=self.result.state_values,
            positive_mask=self.parent.positive_mask,
            accepted_history_count=self.parent.accepted_history_count + 1,
            history_sha256=history_sha256,
            background_sha256=self.parent.background_sha256,
            network_sha256=self.parent.network_sha256,
            interface_sha256=(
                self.parent.interface_sha256
                if interface_sha256 is None
                else interface_sha256
            ),
            branch_id=self.parent.branch_id,
            event_index=self.parent.event_index,
            parent_sha256=self.parent.sha256,
            metadata=metadata,
        )
        self.status = ContinuationTransactionStatus.COMMITTED
        self.commit_count = 1
        return committed

    def discard(self) -> AcceptedContinuationState:
        if self.status is not ContinuationTransactionStatus.PENDING:
            raise RuntimeError("transaction is no longer pending")
        self.status = ContinuationTransactionStatus.DISCARDED
        return self.parent

    def rollback(self) -> AcceptedContinuationState:
        if self.status is ContinuationTransactionStatus.COMMITTED:
            raise RuntimeError("committed transactions require an external durable rollback")
        if self.status is not ContinuationTransactionStatus.PENDING:
            raise RuntimeError("transaction is no longer pending")
        self.status = ContinuationTransactionStatus.ROLLED_BACK
        return self.parent


__all__ = [
    "AcceptedContinuationState",
    "ContinuationTransaction",
    "ContinuationTransactionStatus",
    "ConvergenceMetricFunction",
    "MixedVariableTransform",
    "PseudoTransientIteration",
    "PseudoTransientResult",
    "PseudoTransientTolerances",
    "project_left_nullspace",
    "solve_pseudotransient",
]

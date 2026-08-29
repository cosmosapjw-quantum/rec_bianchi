"""Adaptive microsteps inside the canonical original-HyRec history grid.

PR-05C1 keeps the accepted radiation history on the source-identical uniform
``eta=ln(a)`` grid.  Adaptive trial steps may occur only inside one canonical
macro interval.  No trial, rejected step, or event rollback mutates the durable
history; exactly one append candidate is committed after a successful macro
endpoint.

This module is intentionally an audit/reference controller.  It accepts a
backward-Euler step callable so the same transaction and event semantics can be
verified independently of a future PETSc TS binding.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import struct
from typing import Callable, Protocol, Sequence

import numpy as np

from .causal_history import AcceptedRadiationHistory, HistoryAppendCandidate
from .history_ownership import (
    ScalarHistoryOwnerSwapProblem,
    _dynamic_rhs,
    _source_order_real_virtual_solve,
)
from .primitive_rates import LYMAN_ALPHA_ENERGY_EV


class BackwardEulerStepResult(Protocol):
    state_vector: np.ndarray
    converged: bool
    backward_error: float
    algebraic_residual_relative: float
    minimum_physical_population: float


class AdaptiveTrialFailureKind(str, Enum):
    """Closed retry classes emitted before an adaptive trial can be accepted."""

    RETRY_LTE = "RETRY_LTE"
    RETRY_NONLINEAR = "RETRY_NONLINEAR"
    RETRY_LINEAR = "RETRY_LINEAR"
    RETRY_DOMAIN = "RETRY_DOMAIN"
    NONFINITE_OUTPUT = "NONFINITE_OUTPUT"


@dataclass(frozen=True)
class AdaptiveBackwardEulerFailure:
    """Retryable trial failure with no state that can be committed.

    Diagnostics are optional named finite measurements.  In particular, an
    unavailable residual is omitted instead of being encoded as ``Inf``.
    """

    kind: AdaptiveTrialFailureKind
    message: str
    diagnostics: tuple[tuple[str, float], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", AdaptiveTrialFailureKind(self.kind))
        message = str(self.message)
        if not message:
            raise ValueError("failure message is required")
        object.__setattr__(self, "message", message)
        diagnostics: list[tuple[str, float]] = []
        names: set[str] = set()
        for raw_name, raw_value in self.diagnostics:
            name = str(raw_name)
            value = float(raw_value)
            if not name or name in names:
                raise ValueError("failure diagnostic names must be nonempty and unique")
            if not math.isfinite(value):
                raise ValueError("failure diagnostics must be finite")
            names.add(name)
            diagnostics.append((name, value))
        object.__setattr__(self, "diagnostics", tuple(diagnostics))

    @property
    def converged(self) -> bool:
        return False

    @property
    def retryable(self) -> bool:
        return True


@dataclass(frozen=True)
class AdaptiveBackwardEulerTrial:
    """Raw source-conditioned BE trial without a pre-imposed acceptance gate."""

    state_vector: np.ndarray
    converged: bool
    backward_error: float
    algebraic_residual_relative: float
    minimum_physical_population: float

    def __post_init__(self) -> None:
        vector = np.asarray(self.state_vector, dtype=float)
        if vector.ndim != 1 or vector.size == 0 or not np.all(np.isfinite(vector)):
            raise ValueError("trial state_vector must be finite and nonempty")
        vector = np.array(vector, copy=True); vector.setflags(write=False)
        object.__setattr__(self, "state_vector", vector)
        for name in ("backward_error", "algebraic_residual_relative", "minimum_physical_population"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if self.backward_error < 0.0 or self.algebraic_residual_relative < 0.0:
            raise ValueError("trial diagnostics must be nonnegative")


def source_conditioned_backward_euler_trial(
    problem: ScalarHistoryOwnerSwapProblem,
    old_state_vector: Sequence[float],
    delta_lna: float,
) -> AdaptiveBackwardEulerTrial | AdaptiveBackwardEulerFailure:
    """Evaluate the v0.61 frozen-coefficient BE formula as an adaptive trial.

    The inherited v0.61 result object intentionally refuses to represent a trial
    whose backward-error gate has not yet passed.  An adaptive controller must
    nevertheless inspect such a trial before deciding whether to reject it, so
    this function exposes the identical algebra without prematurely classifying
    the step as accepted.
    """

    old = np.asarray(old_state_vector, dtype=float)
    h = float(delta_lna)
    if old.shape != (problem.dae.layout.local_size,) or not np.all(np.isfinite(old)):
        raise ValueError("old state has invalid shape or values")
    if not math.isfinite(h) or h <= 0.0:
        raise ValueError("delta_lna must be positive and finite")
    d_rate_xe, _ = problem.dae._electron_rate_derivatives()
    d_rate_xe = float(d_rate_xe)
    if not math.isfinite(d_rate_xe):
        return AdaptiveBackwardEulerFailure(
            kind=AdaptiveTrialFailureKind.NONFINITE_OUTPUT,
            message="electron-rate derivative is nonfinite",
            diagnostics=(("delta_lna", h),),
        )
    try:
        denominator = 1.0 / h - d_rate_xe
    except OverflowError:
        denominator = math.inf
    if not math.isfinite(denominator):
        return AdaptiveBackwardEulerFailure(
            kind=AdaptiveTrialFailureKind.NONFINITE_OUTPUT,
            message="backward-Euler electron denominator is nonfinite",
            diagnostics=(("delta_lna", h), ("electron_rate_derivative", d_rate_xe)),
        )
    if denominator <= 0.0:
        return AdaptiveBackwardEulerFailure(
            kind=AdaptiveTrialFailureKind.RETRY_LINEAR,
            message="backward-Euler electron denominator is nonpositive",
            diagnostics=(("delta_lna", h), ("electron_denominator", denominator)),
        )
    incoming = problem._incoming_for(problem.registry.active_owner)
    rhs = _dynamic_rhs(problem.dae, incoming)
    native = _source_order_real_virtual_solve(problem.dae, rhs)
    intercept = problem.dae.electron_rate_per_lna(0.0, native[:2])
    xe_new = (old[0] / h + intercept) / denominator
    new = np.concatenate((np.asarray([xe_new]), native))
    derivative = np.zeros_like(new)
    derivative[0] = (new[0] - old[0]) / h
    residual = problem.residual(new, derivative)
    electron_scale = max(
        abs(float(derivative[0])),
        abs(problem.dae.electron_rate_per_lna(new[0], new[1:3])),
        1.0e-300,
    )
    native_action = problem.dae.native_matrix_s_inv @ native
    native_scale = max(float(np.max(np.abs(native_action))), float(np.max(np.abs(rhs))), 1.0e-300)
    backward = max(
        abs(float(residual[0])) / electron_scale,
        float(np.max(np.abs(residual[1:]))) / native_scale,
    )
    algebraic = float(np.max(np.abs(residual[1:]))) / native_scale
    source = problem.dae.source_snapshot
    equilibrium = np.asarray([1.0, 3.0]) * source.x1s * math.exp(
        -LYMAN_ALPHA_ENERGY_EV / source.TR_eV_rescaled
    )
    physical = native[:2] + equilibrium
    minimum = min(float(xe_new), source.x1s, float(np.min(physical)))
    if minimum <= 0.0 or not np.all(np.isfinite(new)):
        diagnostics = tuple(
            (name, value)
            for name, value in (
                ("backward_error", backward),
                ("algebraic_residual_relative", algebraic),
                ("minimum_physical_population", minimum),
            )
            if math.isfinite(value)
        )
        kind = (
            AdaptiveTrialFailureKind.RETRY_DOMAIN
            if math.isfinite(minimum)
            else AdaptiveTrialFailureKind.NONFINITE_OUTPUT
        )
        return AdaptiveBackwardEulerFailure(
            kind=kind,
            message="backward-Euler source trial left the finite physical domain",
            diagnostics=diagnostics,
        )
    return AdaptiveBackwardEulerTrial(
        state_vector=new,
        converged=True,
        backward_error=backward,
        algebraic_residual_relative=algebraic,
        minimum_physical_population=minimum,
    )


class AdaptiveEventKind(str, Enum):
    BOUNDARY_SPEED_ZERO = "BOUNDARY_SPEED_ZERO"
    CHARACTERISTIC_STENCIL_SWITCH = "CHARACTERISTIC_STENCIL_SWITCH"
    BACKGROUND_BRANCH_SWITCH = "BACKGROUND_BRANCH_SWITCH"
    OWNER_COEFFICIENT_DISCONTINUITY = "OWNER_COEFFICIENT_DISCONTINUITY"
    INVARIANT_REGION_BOUNDARY = "INVARIANT_REGION_BOUNDARY"


@dataclass(frozen=True)
class AdaptiveEvent:
    kind: AdaptiveEventKind
    eta: float
    label: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", AdaptiveEventKind(self.kind))
        eta = float(self.eta)
        if not math.isfinite(eta):
            raise ValueError("event eta must be finite")
        object.__setattr__(self, "eta", eta)
        label = str(self.label)
        if not label:
            raise ValueError("event label is required")
        object.__setattr__(self, "label", label)


@dataclass(frozen=True)
class AdaptiveControllerTolerances:
    absolute: np.ndarray
    relative: np.ndarray
    minimum_step: float
    maximum_step: float
    safety: float = 0.9
    minimum_factor: float = 0.2
    maximum_factor: float = 2.0

    def __post_init__(self) -> None:
        absolute = np.asarray(self.absolute, dtype=float)
        relative = np.asarray(self.relative, dtype=float)
        if absolute.ndim != 1 or relative.shape != absolute.shape or absolute.size == 0:
            raise ValueError("absolute and relative tolerances must be equal nonempty vectors")
        if not np.all(np.isfinite(absolute)) or not np.all(np.isfinite(relative)):
            raise ValueError("tolerances must be finite")
        if np.any(absolute <= 0.0) or np.any(relative < 0.0):
            raise ValueError("absolute tolerances must be positive and relative tolerances nonnegative")
        absolute = np.array(absolute, copy=True)
        relative = np.array(relative, copy=True)
        absolute.setflags(write=False)
        relative.setflags(write=False)
        object.__setattr__(self, "absolute", absolute)
        object.__setattr__(self, "relative", relative)
        minimum = float(self.minimum_step)
        maximum = float(self.maximum_step)
        if not math.isfinite(minimum) or not math.isfinite(maximum) or minimum <= 0.0 or maximum < minimum:
            raise ValueError("step bounds must be finite with 0 < minimum <= maximum")
        object.__setattr__(self, "minimum_step", minimum)
        object.__setattr__(self, "maximum_step", maximum)
        safety = float(self.safety)
        minimum_factor = float(self.minimum_factor)
        maximum_factor = float(self.maximum_factor)
        if not (0.0 < safety <= 1.0):
            raise ValueError("safety must lie in (0,1]")
        if not (0.0 < minimum_factor <= 1.0 <= maximum_factor):
            raise ValueError("controller factors must bracket one")
        object.__setattr__(self, "safety", safety)
        object.__setattr__(self, "minimum_factor", minimum_factor)
        object.__setattr__(self, "maximum_factor", maximum_factor)

    @classmethod
    def scalar(
        cls,
        *,
        size: int,
        absolute: float,
        relative: float,
        minimum_step: float,
        maximum_step: float,
        safety: float = 0.9,
        minimum_factor: float = 0.2,
        maximum_factor: float = 2.0,
    ) -> "AdaptiveControllerTolerances":
        count = int(size)
        if count <= 0:
            raise ValueError("size must be positive")
        return cls(
            absolute=np.full(count, float(absolute)),
            relative=np.full(count, float(relative)),
            minimum_step=minimum_step,
            maximum_step=maximum_step,
            safety=safety,
            minimum_factor=minimum_factor,
            maximum_factor=maximum_factor,
        )


@dataclass(frozen=True)
class CanonicalMacroInterval:
    macro_index: int
    eta_start: float
    eta_end: float
    canonical_dlna: float
    parent_history_sha256: str
    accepted_count_before: int

    def __post_init__(self) -> None:
        macro_index = int(self.macro_index)
        accepted_count = int(self.accepted_count_before)
        if macro_index < 0 or accepted_count < 1 or macro_index != accepted_count:
            raise ValueError("macro index must equal the pre-step accepted history count")
        object.__setattr__(self, "macro_index", macro_index)
        object.__setattr__(self, "accepted_count_before", accepted_count)
        start = float(self.eta_start)
        end = float(self.eta_end)
        dlna = float(self.canonical_dlna)
        if not all(math.isfinite(value) for value in (start, end, dlna)) or dlna <= 0.0:
            raise ValueError("macro interval values must be finite and dlna positive")
        tolerance = 64.0 * np.finfo(float).eps * max(abs(start), abs(end), abs(dlna), 1.0)
        if not math.isclose(end - start, dlna, rel_tol=0.0, abs_tol=tolerance):
            raise ValueError("macro interval does not have the exact canonical width")
        object.__setattr__(self, "eta_start", start)
        object.__setattr__(self, "eta_end", end)
        object.__setattr__(self, "canonical_dlna", dlna)
        digest = str(self.parent_history_sha256).lower()
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError("parent history hash must be SHA-256 hex")
        object.__setattr__(self, "parent_history_sha256", digest)

    @classmethod
    def from_history(cls, history: AcceptedRadiationHistory) -> "CanonicalMacroInterval":
        start = float(history.grid.eta[-1])
        return cls(
            macro_index=history.accepted_count,
            eta_start=start,
            eta_end=start + history.grid.dlna,
            canonical_dlna=history.grid.dlna,
            parent_history_sha256=history.sha256,
            accepted_count_before=history.accepted_count,
        )


@dataclass(frozen=True)
class AdaptiveMicrostepAttempt:
    eta_start: float
    eta_end: float
    proposed_step: float
    accepted: bool
    error_norm: float | None
    backward_error: float | None
    algebraic_residual_relative: float | None
    minimum_physical_population: float | None
    failure_kind: AdaptiveTrialFailureKind | None = None
    failure_diagnostics: tuple[tuple[str, float], ...] = ()
    event_kind: AdaptiveEventKind | None = None
    event_label: str | None = None

    def __post_init__(self) -> None:
        for name in ("eta_start", "eta_end", "proposed_step"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        for name in (
            "error_norm",
            "backward_error",
            "algebraic_residual_relative",
            "minimum_physical_population",
        ):
            raw_value = getattr(self, name)
            if raw_value is None:
                continue
            value = float(raw_value)
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite when present")
            object.__setattr__(self, name, value)
        if self.proposed_step <= 0.0 or self.eta_end <= self.eta_start:
            raise ValueError("microstep must advance with positive width")
        if any(
            value is not None and value < 0.0
            for value in (self.error_norm, self.backward_error, self.algebraic_residual_relative)
        ):
            raise ValueError("diagnostic residuals must be nonnegative")
        if self.accepted:
            if self.failure_kind is not None:
                raise ValueError("an accepted attempt cannot carry a failure kind")
            if self.failure_diagnostics:
                raise ValueError("an accepted attempt cannot carry failure diagnostics")
            if any(
                value is None
                for value in (
                    self.error_norm,
                    self.backward_error,
                    self.algebraic_residual_relative,
                    self.minimum_physical_population,
                )
            ):
                raise ValueError("an accepted attempt requires complete diagnostics")
            if self.minimum_physical_population is not None and self.minimum_physical_population <= 0.0:
                raise ValueError("an accepted attempt must remain strictly positive")
        else:
            if self.failure_kind is None:
                raise ValueError("a rejected attempt requires a typed failure kind")
            object.__setattr__(self, "failure_kind", AdaptiveTrialFailureKind(self.failure_kind))
        diagnostics: list[tuple[str, float]] = []
        diagnostic_names: set[str] = set()
        for raw_name, raw_value in self.failure_diagnostics:
            name = str(raw_name)
            value = float(raw_value)
            if not name or name in diagnostic_names or not math.isfinite(value):
                raise ValueError("failure diagnostics must have unique names and finite values")
            diagnostic_names.add(name)
            diagnostics.append((name, value))
        object.__setattr__(self, "failure_diagnostics", tuple(diagnostics))
        if self.event_kind is not None:
            object.__setattr__(self, "event_kind", AdaptiveEventKind(self.event_kind))
            if not self.event_label:
                raise ValueError("event label is required when event_kind is present")


@dataclass(frozen=True)
class AcceptedMacrostepLedger:
    interval: CanonicalMacroInterval
    attempts: tuple[AdaptiveMicrostepAttempt, ...]
    history_before_sha256: str
    history_after_sha256: str
    accepted_count_after: int
    commit_count: int
    restart_count: int
    localized_event_etas: tuple[float, ...]
    final_error_norm: float
    maximum_backward_error: float
    maximum_algebraic_residual: float
    minimum_physical_population: float

    @property
    def accepted_microsteps(self) -> int:
        return sum(int(attempt.accepted) for attempt in self.attempts)

    @property
    def rejected_microsteps(self) -> int:
        return sum(int(not attempt.accepted) for attempt in self.attempts)

    @property
    def event_count(self) -> int:
        return len(self.localized_event_etas)

    @property
    def history_count_increment(self) -> int:
        return self.accepted_count_after - self.interval.accepted_count_before

    def __post_init__(self) -> None:
        if not self.attempts:
            raise ValueError("macro ledger requires at least one microstep attempt")
        for name in ("history_before_sha256", "history_after_sha256"):
            digest = str(getattr(self, name)).lower()
            if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
                raise ValueError(f"{name} must be SHA-256 hex")
            object.__setattr__(self, name, digest)
        if self.history_before_sha256 != self.interval.parent_history_sha256:
            raise ValueError("macro ledger parent hash mismatch")
        if int(self.commit_count) != 1 or int(self.accepted_count_after) != self.interval.accepted_count_before + 1:
            raise ValueError("successful macro interval must commit exactly one history slice")
        if int(self.restart_count) < 0:
            raise ValueError("restart_count must be nonnegative")
        object.__setattr__(self, "commit_count", int(self.commit_count))
        object.__setattr__(self, "accepted_count_after", int(self.accepted_count_after))
        object.__setattr__(self, "restart_count", int(self.restart_count))
        roots = tuple(float(value) for value in self.localized_event_etas)
        if any(not math.isfinite(value) for value in roots):
            raise ValueError("event roots must be finite")
        object.__setattr__(self, "localized_event_etas", roots)
        for name in (
            "final_error_norm",
            "maximum_backward_error",
            "maximum_algebraic_residual",
            "minimum_physical_population",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if self.minimum_physical_population <= 0.0:
            raise ValueError("accepted macro trajectory must remain strictly positive")


@dataclass(frozen=True)
class AdaptiveTrajectoryContext:
    eta: float
    state_vector: np.ndarray
    accepted_history: AcceptedRadiationHistory
    controller_step: float
    tolerances: AdaptiveControllerTolerances
    events: tuple[AdaptiveEvent, ...] = ()
    background_label: str = "UNSPECIFIED"
    event_generation: int = 0

    def __post_init__(self) -> None:
        eta = float(self.eta)
        step = float(self.controller_step)
        if not math.isfinite(eta) or not math.isfinite(step) or step <= 0.0:
            raise ValueError("eta and controller_step must be finite and step positive")
        tolerance = 64.0 * np.finfo(float).eps * max(abs(eta), abs(self.accepted_history.grid.eta[-1]), 1.0)
        if not math.isclose(eta, float(self.accepted_history.grid.eta[-1]), rel_tol=0.0, abs_tol=tolerance):
            raise ValueError("context eta must equal the last accepted canonical history coordinate")
        state = np.asarray(self.state_vector, dtype=float)
        if state.ndim != 1 or state.size == 0 or not np.all(np.isfinite(state)):
            raise ValueError("state_vector must be a finite nonempty vector")
        if state.shape != self.tolerances.absolute.shape:
            raise ValueError("state and tolerance vectors must have the same shape")
        state = np.array(state, copy=True)
        state.setflags(write=False)
        object.__setattr__(self, "eta", eta)
        object.__setattr__(self, "controller_step", step)
        object.__setattr__(self, "state_vector", state)
        events = tuple(sorted((AdaptiveEvent(event.kind, event.eta, event.label) for event in self.events), key=lambda event: event.eta))
        if len({(event.eta, event.label) for event in events}) != len(events):
            raise ValueError("adaptive events must be unique")
        object.__setattr__(self, "events", events)
        label = str(self.background_label)
        if not label:
            raise ValueError("background_label is required")
        object.__setattr__(self, "background_label", label)
        generation = int(self.event_generation)
        if generation < 0:
            raise ValueError("event_generation must be nonnegative")
        object.__setattr__(self, "event_generation", generation)


_RESTART_MAGIC = b"PR05C1_TRAJECTORY_RESTART_V1\n"


@dataclass(frozen=True)
class TrajectoryRestartState:
    eta: float
    state_vector: np.ndarray
    accepted_history: AcceptedRadiationHistory
    controller_step: float
    background_label: str
    event_generation: int = 0

    def __post_init__(self) -> None:
        eta = float(self.eta)
        step = float(self.controller_step)
        if not math.isfinite(eta) or not math.isfinite(step) or step <= 0.0:
            raise ValueError("restart eta and controller step must be finite")
        state = np.asarray(self.state_vector, dtype=float)
        if state.ndim != 1 or state.size == 0 or not np.all(np.isfinite(state)):
            raise ValueError("restart state vector is invalid")
        state = np.array(state, dtype=float, copy=True, order="C")
        state.setflags(write=False)
        object.__setattr__(self, "eta", eta)
        object.__setattr__(self, "controller_step", step)
        object.__setattr__(self, "state_vector", state)
        label = str(self.background_label)
        if not label:
            raise ValueError("restart background label is required")
        object.__setattr__(self, "background_label", label)
        generation = int(self.event_generation)
        if generation < 0:
            raise ValueError("event_generation must be nonnegative")
        object.__setattr__(self, "event_generation", generation)

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.to_bytes()).hexdigest()

    def to_bytes(self) -> bytes:
        history = self.accepted_history.to_bytes()
        state = np.asarray(self.state_vector, dtype="<f8")
        header = {
            "schema": "PR05C1_TRAJECTORY_RESTART_V1",
            "eta": self.eta,
            "controller_step": self.controller_step,
            "background_label": self.background_label,
            "event_generation": self.event_generation,
            "history_nbytes": len(history),
            "state_shape": list(state.shape),
            "state_nbytes": int(state.nbytes),
        }
        encoded = json.dumps(header, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        payload = bytearray(_RESTART_MAGIC)
        payload.extend(struct.pack(">Q", len(encoded)))
        payload.extend(encoded)
        payload.extend(history)
        payload.extend(state.tobytes(order="C"))
        return bytes(payload)

    @classmethod
    def from_bytes(cls, payload: bytes) -> "TrajectoryRestartState":
        if not payload.startswith(_RESTART_MAGIC):
            raise ValueError("unknown PR05C1 restart payload")
        offset = len(_RESTART_MAGIC)
        if len(payload) < offset + 8:
            raise ValueError("truncated PR05C1 restart header")
        header_size = struct.unpack(">Q", payload[offset : offset + 8])[0]
        offset += 8
        header = json.loads(payload[offset : offset + header_size].decode("utf-8"))
        offset += header_size
        if header.get("schema") != "PR05C1_TRAJECTORY_RESTART_V1":
            raise ValueError("unknown PR05C1 restart schema")
        history_size = int(header["history_nbytes"])
        history_payload = payload[offset : offset + history_size]
        if len(history_payload) != history_size:
            raise ValueError("truncated PR05C1 history payload")
        offset += history_size
        state_size = int(header["state_nbytes"])
        state_payload = payload[offset : offset + state_size]
        if len(state_payload) != state_size:
            raise ValueError("truncated PR05C1 state payload")
        offset += state_size
        if offset != len(payload):
            raise ValueError("trailing bytes in PR05C1 restart payload")
        shape = tuple(int(value) for value in header["state_shape"])
        state = np.frombuffer(state_payload, dtype="<f8").reshape(shape).copy()
        return cls(
            eta=header["eta"],
            state_vector=state,
            accepted_history=AcceptedRadiationHistory.from_bytes(history_payload),
            controller_step=header["controller_step"],
            background_label=header["background_label"],
            event_generation=header["event_generation"],
        )


def _weighted_error_norm(
    old: np.ndarray,
    full: np.ndarray,
    half: np.ndarray,
    tolerances: AdaptiveControllerTolerances,
) -> float:
    scale = tolerances.absolute + tolerances.relative * np.maximum(np.abs(old), np.abs(half))
    return float(np.max(np.abs(half - full) / scale))


def _controller_factor(error_norm: float, tolerances: AdaptiveControllerTolerances) -> float:
    if error_norm <= 0.0:
        return tolerances.maximum_factor
    raw = tolerances.safety * error_norm ** -0.5
    return min(tolerances.maximum_factor, max(tolerances.minimum_factor, raw))


_FAILURE_CONTRACTION = {
    AdaptiveTrialFailureKind.RETRY_NONLINEAR: 0.5,
    AdaptiveTrialFailureKind.RETRY_LINEAR: 0.35,
    AdaptiveTrialFailureKind.RETRY_DOMAIN: 0.2,
    AdaptiveTrialFailureKind.NONFINITE_OUTPUT: 0.1,
}


def _failure_contraction(kind: AdaptiveTrialFailureKind) -> float:
    """Return a strict, LTE-independent contraction for a failed solve stage."""

    typed = AdaptiveTrialFailureKind(kind)
    if typed is AdaptiveTrialFailureKind.RETRY_LTE:
        raise ValueError("LTE retries use the error controller, not a failure contraction")
    return _FAILURE_CONTRACTION[typed]


def _finite_diagnostics(result: BackwardEulerStepResult) -> tuple[tuple[str, float], ...]:
    diagnostics: list[tuple[str, float]] = []
    for name in (
        "backward_error",
        "algebraic_residual_relative",
        "minimum_physical_population",
    ):
        try:
            value = float(getattr(result, name))
        except (AttributeError, TypeError, ValueError):
            continue
        if math.isfinite(value):
            diagnostics.append((name, value))
    return tuple(diagnostics)


def _classify_trial_failure(
    result: BackwardEulerStepResult | AdaptiveBackwardEulerFailure,
    expected_shape: tuple[int, ...],
) -> AdaptiveBackwardEulerFailure | None:
    """Validate one stage and map every retryable result to a closed class."""

    if isinstance(result, AdaptiveBackwardEulerFailure):
        return result
    try:
        vector = np.asarray(result.state_vector, dtype=float)
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("stepper returned an invalid state_vector") from exc
    if vector.shape != expected_shape:
        raise ValueError("stepper returned a state with the wrong shape")
    try:
        backward = float(result.backward_error)
        algebraic = float(result.algebraic_residual_relative)
        minimum = float(result.minimum_physical_population)
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("stepper returned invalid trial diagnostics") from exc
    if (
        not np.all(np.isfinite(vector))
        or not math.isfinite(backward)
        or not math.isfinite(algebraic)
        or not math.isfinite(minimum)
    ):
        return AdaptiveBackwardEulerFailure(
            kind=AdaptiveTrialFailureKind.NONFINITE_OUTPUT,
            message="stepper returned a nonfinite state or diagnostic",
            diagnostics=_finite_diagnostics(result),
        )
    if backward < 0.0 or algebraic < 0.0:
        raise ValueError("stepper residual diagnostics must be nonnegative")
    if not bool(result.converged):
        explicit_kind = getattr(result, "failure_kind", None)
        if explicit_kind is not None:
            kind = AdaptiveTrialFailureKind(explicit_kind)
        elif minimum <= 0.0:
            kind = AdaptiveTrialFailureKind.RETRY_DOMAIN
        else:
            kind = AdaptiveTrialFailureKind.RETRY_NONLINEAR
        if kind is AdaptiveTrialFailureKind.RETRY_LTE:
            raise ValueError("a failed solve stage cannot report RETRY_LTE")
        return AdaptiveBackwardEulerFailure(
            kind=kind,
            message="stepper reported a retryable stage failure",
            diagnostics=_finite_diagnostics(result),
        )
    if minimum <= 0.0:
        return AdaptiveBackwardEulerFailure(
            kind=AdaptiveTrialFailureKind.RETRY_DOMAIN,
            message="stepper left the strictly positive physical domain",
            diagnostics=_finite_diagnostics(result),
        )
    if backward >= 1.0e-11:
        return AdaptiveBackwardEulerFailure(
            kind=AdaptiveTrialFailureKind.RETRY_NONLINEAR,
            message="stepper failed the backward-error gate",
            diagnostics=_finite_diagnostics(result),
        )
    if algebraic >= 1.0e-11:
        return AdaptiveBackwardEulerFailure(
            kind=AdaptiveTrialFailureKind.RETRY_LINEAR,
            message="stepper failed the algebraic-residual gate",
            diagnostics=_finite_diagnostics(result),
        )
    return None


def _snapshot_completed_trial(
    result: BackwardEulerStepResult,
) -> AdaptiveBackwardEulerTrial:
    """Detach a stage before a later stepper call can reuse its buffer."""

    return AdaptiveBackwardEulerTrial(
        state_vector=np.array(result.state_vector, dtype=float, copy=True),
        converged=True,
        backward_error=float(result.backward_error),
        algebraic_residual_relative=float(result.algebraic_residual_relative),
        minimum_physical_population=float(result.minimum_physical_population),
    )


def _completed_stage_diagnostics(
    completed: Sequence[AdaptiveBackwardEulerTrial],
) -> tuple[float | None, float | None, float | None]:
    """Summarize finite completed stages for a rejected-attempt receipt only."""

    if not completed:
        return None, None, None
    return (
        max(float(result.backward_error) for result in completed),
        max(float(result.algebraic_residual_relative) for result in completed),
        min(float(result.minimum_physical_population) for result in completed),
    )


def advance_canonical_macro_interval(
    context: AdaptiveTrajectoryContext,
    *,
    stepper: Callable[
        [np.ndarray, float],
        BackwardEulerStepResult | AdaptiveBackwardEulerFailure,
    ],
    candidate_factory: Callable[[AcceptedRadiationHistory], HistoryAppendCandidate],
    maximum_attempts: int = 10000,
) -> tuple[AdaptiveTrajectoryContext, AcceptedMacrostepLedger]:
    """Advance one exact canonical macro interval with adaptive BE microsteps."""

    interval = CanonicalMacroInterval.from_history(context.accepted_history)
    eta = interval.eta_start
    state = np.array(context.state_vector, copy=True)
    h = min(max(context.controller_step, context.tolerances.minimum_step), context.tolerances.maximum_step)
    attempts: list[AdaptiveMicrostepAttempt] = []
    localized_events: list[float] = []
    restart_count = 0
    event_generation = context.event_generation
    pending_events = [event for event in context.events if interval.eta_start < event.eta <= interval.eta_end]
    event_cursor = 0
    maximum_backward = 0.0
    maximum_algebraic = 0.0
    minimum_population = math.inf
    final_error = math.inf
    endpoint_tolerance = 128.0 * np.finfo(float).eps * max(abs(interval.eta_end), 1.0)

    def record_stage_failure(
        *,
        failure: AdaptiveBackwardEulerFailure,
        completed: Sequence[BackwardEulerStepResult],
        eta_start: float,
        width: float,
        landing_event: AdaptiveEvent | None,
    ) -> float:
        backward, algebraic, minimum = _completed_stage_diagnostics(completed)
        attempts.append(
            AdaptiveMicrostepAttempt(
                eta_start=eta_start,
                eta_end=eta_start + width,
                proposed_step=width,
                accepted=False,
                error_norm=None,
                backward_error=backward,
                algebraic_residual_relative=algebraic,
                minimum_physical_population=minimum,
                failure_kind=failure.kind,
                failure_diagnostics=failure.diagnostics,
                event_kind=None if landing_event is None else landing_event.kind,
                event_label=None if landing_event is None else landing_event.label,
            )
        )
        minimum_width = context.tolerances.minimum_step
        at_ordinary_minimum = width <= minimum_width * (1.0 + 64.0 * np.finfo(float).eps)
        if at_ordinary_minimum:
            if landing_event is not None and width < minimum_width:
                raise RuntimeError("adaptive event landing failed below the ordinary minimum step")
            raise RuntimeError("adaptive microstep failed at the configured minimum step")
        return max(minimum_width, width * _failure_contraction(failure.kind))

    for _ in range(int(maximum_attempts)):
        remaining = interval.eta_end - eta
        if remaining <= endpoint_tolerance:
            eta = interval.eta_end
            break
        proposed = min(h, remaining)
        if (
            proposed < context.tolerances.minimum_step
            and remaining > context.tolerances.minimum_step + endpoint_tolerance
        ):
            proposed = context.tolerances.minimum_step
        proposed = min(proposed, remaining)
        event: AdaptiveEvent | None = None
        if event_cursor < len(pending_events):
            candidate_event = pending_events[event_cursor]
            if candidate_event.eta < eta - endpoint_tolerance:
                raise RuntimeError("adaptive event ordering regressed behind the current state")
            if candidate_event.eta <= eta + proposed + endpoint_tolerance:
                event = candidate_event
                proposed = candidate_event.eta - eta
                if proposed <= endpoint_tolerance:
                    localized_events.append(candidate_event.eta)
                    restart_count += 1
                    event_generation += 1
                    event_cursor += 1
                    h = min(h, 0.25 * interval.canonical_dlna)
                    continue
        completed: list[AdaptiveBackwardEulerTrial] = []
        full_raw = stepper(np.array(state, copy=True), proposed)
        failure = _classify_trial_failure(full_raw, state.shape)
        if failure is not None:
            h = record_stage_failure(
                failure=failure,
                completed=completed,
                eta_start=eta,
                width=proposed,
                landing_event=event,
            )
            continue
        full = _snapshot_completed_trial(full_raw)
        completed.append(full)
        first_half_raw = stepper(np.array(state, copy=True), 0.5 * proposed)
        failure = _classify_trial_failure(first_half_raw, state.shape)
        if failure is not None:
            h = record_stage_failure(
                failure=failure,
                completed=completed,
                eta_start=eta,
                width=proposed,
                landing_event=event,
            )
            continue
        first_half = _snapshot_completed_trial(first_half_raw)
        completed.append(first_half)
        second_half_raw = stepper(
            np.array(first_half.state_vector, copy=True), 0.5 * proposed
        )
        failure = _classify_trial_failure(second_half_raw, state.shape)
        if failure is not None:
            h = record_stage_failure(
                failure=failure,
                completed=completed,
                eta_start=eta,
                width=proposed,
                landing_event=event,
            )
            continue
        second_half = _snapshot_completed_trial(second_half_raw)
        completed.append(second_half)
        full_state = np.asarray(full.state_vector, dtype=float)
        half_state = np.asarray(second_half.state_vector, dtype=float)
        error = _weighted_error_norm(state, full_state, half_state, context.tolerances)
        if not math.isfinite(error):
            h = record_stage_failure(
                failure=AdaptiveBackwardEulerFailure(
                    kind=AdaptiveTrialFailureKind.NONFINITE_OUTPUT,
                    message="step-doubling produced a nonfinite LTE norm",
                ),
                completed=completed,
                eta_start=eta,
                width=proposed,
                landing_event=event,
            )
            continue
        trial_backward_error = max(
            float(full.backward_error),
            float(first_half.backward_error),
            float(second_half.backward_error),
        )
        trial_algebraic_residual = max(
            float(full.algebraic_residual_relative),
            float(first_half.algebraic_residual_relative),
            float(second_half.algebraic_residual_relative),
        )
        trial_minimum_population = min(
            float(full.minimum_physical_population),
            float(first_half.minimum_physical_population),
            float(second_half.minimum_physical_population),
        )
        accepted = bool(error <= 1.0)
        attempts.append(
            AdaptiveMicrostepAttempt(
                eta_start=eta,
                eta_end=eta + proposed,
                proposed_step=proposed,
                accepted=accepted,
                error_norm=error,
                backward_error=trial_backward_error,
                algebraic_residual_relative=trial_algebraic_residual,
                minimum_physical_population=trial_minimum_population,
                failure_kind=None if accepted else AdaptiveTrialFailureKind.RETRY_LTE,
                event_kind=None if event is None else event.kind,
                event_label=None if event is None else event.label,
            )
        )
        factor = _controller_factor(error, context.tolerances)
        if accepted:
            # The accepted production path is the higher-accuracy pair of half
            # steps.  The coarse full step remains only an LTE comparator.
            state = np.array(half_state, copy=True)
            eta += proposed
            final_error = error
            maximum_backward = max(
                maximum_backward,
                float(first_half.backward_error),
                float(second_half.backward_error),
            )
            maximum_algebraic = max(
                maximum_algebraic,
                float(first_half.algebraic_residual_relative),
                float(second_half.algebraic_residual_relative),
            )
            minimum_population = min(
                minimum_population,
                float(first_half.minimum_physical_population),
                float(second_half.minimum_physical_population),
            )
            h = min(context.tolerances.maximum_step, max(context.tolerances.minimum_step, proposed * factor))
            if event is not None and math.isclose(eta, event.eta, rel_tol=0.0, abs_tol=endpoint_tolerance):
                localized_events.append(event.eta)
                restart_count += 1
                event_generation += 1
                event_cursor += 1
                h = min(h, 0.25 * interval.canonical_dlna)
        else:
            new_h = max(context.tolerances.minimum_step, proposed * min(1.0, factor))
            if proposed <= context.tolerances.minimum_step * (1.0 + 64.0 * np.finfo(float).eps):
                if event is not None and proposed < context.tolerances.minimum_step:
                    raise RuntimeError("adaptive event landing failed below the ordinary minimum step")
                raise RuntimeError("adaptive microstep failed at the configured minimum step")
            h = new_h
    else:
        raise RuntimeError("adaptive macro interval exceeded maximum_attempts")

    if not math.isclose(eta, interval.eta_end, rel_tol=0.0, abs_tol=endpoint_tolerance):
        raise RuntimeError("adaptive macro interval did not reach the canonical endpoint")
    parent = context.accepted_history
    candidate = candidate_factory(parent)
    committed = parent.accept(candidate)
    next_step = min(context.tolerances.maximum_step, max(context.tolerances.minimum_step, h))
    updated = AdaptiveTrajectoryContext(
        eta=interval.eta_end,
        state_vector=state,
        accepted_history=committed,
        controller_step=next_step,
        tolerances=context.tolerances,
        events=tuple(event for event in context.events if event.eta > interval.eta_end + endpoint_tolerance),
        background_label=context.background_label,
        event_generation=event_generation,
    )
    ledger = AcceptedMacrostepLedger(
        interval=interval,
        attempts=tuple(attempts),
        history_before_sha256=parent.sha256,
        history_after_sha256=committed.sha256,
        accepted_count_after=committed.accepted_count,
        commit_count=1,
        restart_count=restart_count,
        localized_event_etas=tuple(localized_events),
        final_error_norm=final_error,
        maximum_backward_error=maximum_backward,
        maximum_algebraic_residual=maximum_algebraic,
        minimum_physical_population=minimum_population,
    )
    return updated, ledger


__all__ = [
    "AcceptedMacrostepLedger",
    "AdaptiveBackwardEulerFailure",
    "AdaptiveBackwardEulerTrial",
    "AdaptiveControllerTolerances",
    "AdaptiveEvent",
    "AdaptiveEventKind",
    "AdaptiveMicrostepAttempt",
    "AdaptiveTrialFailureKind",
    "AdaptiveTrajectoryContext",
    "CanonicalMacroInterval",
    "TrajectoryRestartState",
    "advance_canonical_macro_interval",
    "source_conditioned_backward_euler_trial",
]

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
) -> AdaptiveBackwardEulerTrial:
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
    incoming = problem._incoming_for(problem.registry.active_owner)
    rhs = _dynamic_rhs(problem.dae, incoming)
    native = _source_order_real_virtual_solve(problem.dae, rhs)
    d_rate_xe, _ = problem.dae._electron_rate_derivatives()
    intercept = problem.dae.electron_rate_per_lna(0.0, native[:2])
    denominator = 1.0 / h - d_rate_xe
    if denominator <= 0.0:
        return AdaptiveBackwardEulerTrial(
            state_vector=old,
            converged=False,
            backward_error=math.inf,
            algebraic_residual_relative=math.inf,
            minimum_physical_population=-math.inf,
        )
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
    return AdaptiveBackwardEulerTrial(
        state_vector=new,
        converged=bool(minimum > 0.0 and np.all(np.isfinite(new))),
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
    error_norm: float
    backward_error: float
    algebraic_residual_relative: float
    minimum_physical_population: float
    event_kind: AdaptiveEventKind | None = None
    event_label: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "eta_start",
            "eta_end",
            "proposed_step",
            "error_norm",
            "backward_error",
            "algebraic_residual_relative",
            "minimum_physical_population",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if self.proposed_step <= 0.0 or self.eta_end <= self.eta_start:
            raise ValueError("microstep must advance with positive width")
        if self.error_norm < 0.0 or self.backward_error < 0.0 or self.algebraic_residual_relative < 0.0:
            raise ValueError("diagnostic residuals must be nonnegative")
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


def advance_canonical_macro_interval(
    context: AdaptiveTrajectoryContext,
    *,
    stepper: Callable[[np.ndarray, float], BackwardEulerStepResult],
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

    for _ in range(int(maximum_attempts)):
        remaining = interval.eta_end - eta
        if remaining <= endpoint_tolerance:
            eta = interval.eta_end
            break
        proposed = min(h, remaining)
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
        if proposed < context.tolerances.minimum_step and remaining > context.tolerances.minimum_step + endpoint_tolerance:
            proposed = context.tolerances.minimum_step
        proposed = min(proposed, remaining)
        full = stepper(state, proposed)
        first_half = stepper(state, 0.5 * proposed)
        second_half = stepper(np.asarray(first_half.state_vector, dtype=float), 0.5 * proposed)
        full_state = np.asarray(full.state_vector, dtype=float)
        half_state = np.asarray(second_half.state_vector, dtype=float)
        if full_state.shape != state.shape or half_state.shape != state.shape:
            raise ValueError("stepper returned a state with the wrong shape")
        error = _weighted_error_norm(state, full_state, half_state, context.tolerances)
        converged = bool(full.converged and first_half.converged and second_half.converged)
        accepted = bool(
            converged
            and error <= 1.0
            and full.minimum_physical_population > 0.0
            and float(full.backward_error) < 1.0e-11
            and float(full.algebraic_residual_relative) < 1.0e-11
        )
        maximum_backward = max(maximum_backward, float(full.backward_error), float(first_half.backward_error), float(second_half.backward_error))
        maximum_algebraic = max(
            maximum_algebraic,
            float(full.algebraic_residual_relative),
            float(first_half.algebraic_residual_relative),
            float(second_half.algebraic_residual_relative),
        )
        minimum_population = min(
            minimum_population,
            float(full.minimum_physical_population),
            float(first_half.minimum_physical_population),
            float(second_half.minimum_physical_population),
        )
        attempts.append(
            AdaptiveMicrostepAttempt(
                eta_start=eta,
                eta_end=eta + proposed,
                proposed_step=proposed,
                accepted=accepted,
                error_norm=error,
                backward_error=max(float(full.backward_error), float(first_half.backward_error), float(second_half.backward_error)),
                algebraic_residual_relative=max(
                    float(full.algebraic_residual_relative),
                    float(first_half.algebraic_residual_relative),
                    float(second_half.algebraic_residual_relative),
                ),
                minimum_physical_population=min(
                    float(full.minimum_physical_population),
                    float(first_half.minimum_physical_population),
                    float(second_half.minimum_physical_population),
                ),
                event_kind=None if event is None else event.kind,
                event_label=None if event is None else event.label,
            )
        )
        factor = _controller_factor(error, context.tolerances)
        if accepted:
            # The full backward-Euler state is the production reference.  The
            # two-half-step state is used only for the local error estimate.
            state = np.array(full_state, copy=True)
            eta += proposed
            final_error = error
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
    "AdaptiveBackwardEulerTrial",
    "AdaptiveControllerTolerances",
    "AdaptiveEvent",
    "AdaptiveEventKind",
    "AdaptiveMicrostepAttempt",
    "AdaptiveTrajectoryContext",
    "CanonicalMacroInterval",
    "TrajectoryRestartState",
    "advance_canonical_macro_interval",
    "source_conditioned_backward_euler_trial",
]

"""Roundoff-aware bounded COM collision--transport macro solve.

This module closes one deliberately narrow numerical blocker: the 35-state,
26-direction COM collision--transport subproblem can reach a backward-Euler
root whose *net* residual is cancellation-limited in float64.  A net residual
normalized only by the tiny occupation scale therefore cannot be the sole
acceptance criterion.

The solver keeps all cancellation-amplified diagnostics visible and accepts a
candidate only when all of the following hold simultaneously:

* strict occupation positivity without clipping;
* residual backward error relative to gross forward+reverse event scales;
* an explicit floating-point roundoff bound for the residual;
* independent photon-number closure;
* energy backward error relative to gross photon-energy event scales;
* photon--atom four-force closure and nonpositive collision free energy; and
* independent pair-loop/vectorized collision parity.

The outer red/blue occupations are held at the source-derived v0.73 values.
Consequently this is a source-conditioned COM subblock root, not yet the full
atomic/native/history-coupled Bianchi--HyRec macro endpoint.

Conventions
-----------
* metric signature ``(-,+,+,+)`` inherited from the background snapshot;
* ordinary frequency in Hz;
* explicit ``c`` and ``h``;
* occupation is dimensionless;
* collision/transport actions have units ``s^-1``;
* photon-number action has units ``m^-3 s^-1``;
* energy ledger has units ``J m^-3`` over one macro interval.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import time
from typing import Sequence

import numpy as np
from scipy.constants import c, h
from scipy.sparse.linalg import LinearOperator, gmres

from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
    apply_nonlinear_bose_operator_pair_loop,
)
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
    CoupledCollisionTransportProblem,
)


def _positive_state(
    value: Sequence[float] | np.ndarray,
    *,
    shape: tuple[int, int],
    name: str,
) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != shape or not np.all(np.isfinite(array)) or np.any(array <= 0.0):
        raise ValueError(f"{name} must be finite, strictly positive, and have shape {shape}")
    return np.array(array, dtype=float, copy=True)


@dataclass(frozen=True)
class ActivityNumberRestoration:
    occupation: np.ndarray
    log_activity_shift: float
    maximum_relative_correction: float
    number_residual_m3: float
    number_relative_residual: float
    iterations: int

    def __post_init__(self) -> None:
        occupation = np.asarray(self.occupation, dtype=float)
        if occupation.ndim != 2 or not np.all(np.isfinite(occupation)) or np.any(occupation <= 0.0):
            raise ValueError("restored occupation must be finite and strictly positive")
        occupation = np.array(occupation, copy=True)
        occupation.setflags(write=False)
        object.__setattr__(self, "occupation", occupation)
        for name in (
            "log_activity_shift",
            "maximum_relative_correction",
            "number_residual_m3",
            "number_relative_residual",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if self.maximum_relative_correction < 0.0 or self.number_relative_residual < 0.0:
            raise ValueError("relative diagnostics must be nonnegative")
        if int(self.iterations) < 0:
            raise ValueError("iterations must be nonnegative")


@dataclass(frozen=True)
class RoundoffAwareMacroAssessment:
    raw_residual_inf: float
    net_scaled_residual: float
    gross_backward_error: float
    gross_equation_scale: float
    residual_roundoff_bound: float
    residual_roundoff_ratio: float
    residual_roundoff_limited: bool
    number_residual_m3: float
    number_relative_residual: float
    energy_residual_J_m3: float
    energy_net_relative_residual: float
    energy_gross_backward_error: float
    gross_energy_scale_J_m3: float
    energy_roundoff_bound_J_m3: float
    energy_roundoff_ratio: float
    energy_roundoff_limited: bool
    collision_four_force_residual: float
    collision_entropy_production: float
    minimum_occupation: float
    residual_reduction: float
    collision_gross_increment: float
    transport_gross_increment: float
    pair_loop_action_relative_residual: float | None = None
    pair_loop_four_force_gross_relative_residual: float | None = None

    def __post_init__(self) -> None:
        nonnegative = (
            "raw_residual_inf",
            "net_scaled_residual",
            "gross_backward_error",
            "gross_equation_scale",
            "residual_roundoff_bound",
            "residual_roundoff_ratio",
            "number_relative_residual",
            "energy_net_relative_residual",
            "energy_gross_backward_error",
            "gross_energy_scale_J_m3",
            "energy_roundoff_bound_J_m3",
            "energy_roundoff_ratio",
            "collision_four_force_residual",
            "minimum_occupation",
            "residual_reduction",
            "collision_gross_increment",
            "transport_gross_increment",
        )
        for name in nonnegative:
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
            object.__setattr__(self, name, value)
        for name in ("number_residual_m3", "energy_residual_J_m3", "collision_entropy_production"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        for name in (
            "pair_loop_action_relative_residual",
            "pair_loop_four_force_gross_relative_residual",
        ):
            value = getattr(self, name)
            if value is not None:
                number = float(value)
                if not math.isfinite(number) or number < 0.0:
                    raise ValueError(f"{name} must be finite and nonnegative when present")
                object.__setattr__(self, name, number)

    def passed(
        self,
        *,
        tolerance: float = 1.0e-11,
        pair_loop_tolerance: float = 1.0e-8,
        maximum_residual_reduction: float = 1.0e-8,
    ) -> bool:
        threshold = float(tolerance)
        parity = float(pair_loop_tolerance)
        reduction = float(maximum_residual_reduction)
        if not (math.isfinite(threshold) and threshold > 0.0):
            raise ValueError("tolerance must be positive and finite")
        if not (math.isfinite(parity) and parity > 0.0):
            raise ValueError("pair_loop_tolerance must be positive and finite")
        if not (math.isfinite(reduction) and reduction > 0.0):
            raise ValueError("maximum_residual_reduction must be positive and finite")
        pair_ok = (
            self.pair_loop_action_relative_residual is not None
            and self.pair_loop_four_force_gross_relative_residual is not None
            and self.pair_loop_action_relative_residual <= parity
            and self.pair_loop_four_force_gross_relative_residual <= parity
        )
        residual_ok = self.net_scaled_residual <= threshold or self.residual_roundoff_limited
        energy_ok = (
            self.energy_net_relative_residual <= threshold
            or self.energy_roundoff_limited
        )
        return bool(
            self.minimum_occupation > 0.0
            and self.gross_backward_error <= threshold
            and residual_ok
            and self.number_relative_residual <= threshold
            and self.energy_gross_backward_error <= threshold
            and energy_ok
            and self.collision_four_force_residual <= threshold
            and self.collision_entropy_production <= threshold
            and self.residual_reduction <= reduction
            and pair_ok
        )


@dataclass(frozen=True)
class SingleMacroIteration:
    iteration: int
    raw_residual_inf: float
    normalized_residual_inf: float
    gross_backward_error: float
    number_relative_residual: float
    residual_roundoff_ratio: float
    gmres_iterations: int
    damping: float


@dataclass(frozen=True)
class RoundoffAwareSingleMacroResult:
    occupation: np.ndarray
    converged: bool
    convergence_basis: str
    assessment: RoundoffAwareMacroAssessment
    iterations: tuple[SingleMacroIteration, ...]
    activity_log_shift: float
    activity_shift_max_relative: float
    total_gmres_iterations: int
    elapsed_s: float

    def __post_init__(self) -> None:
        occupation = np.asarray(self.occupation, dtype=float)
        if occupation.ndim != 2 or not np.all(np.isfinite(occupation)) or np.any(occupation <= 0.0):
            raise ValueError("result occupation must be finite and strictly positive")
        occupation = np.array(occupation, copy=True)
        occupation.setflags(write=False)
        object.__setattr__(self, "occupation", occupation)
        object.__setattr__(self, "iterations", tuple(self.iterations))


def _number_raw_and_scale(
    problem: CoupledCollisionTransportProblem,
    old_occupation: np.ndarray,
    occupation: np.ndarray,
    transport_result,
) -> tuple[float, float, float]:
    weights = np.asarray(problem.grid.weights, dtype=np.longdouble)
    measure = np.asarray(problem.network.mode_measure, dtype=np.longdouble)
    old = np.asarray(old_occupation, dtype=np.longdouble)
    new = np.asarray(occupation, dtype=np.longdouble)
    before = np.sum(measure[:, None] * old * weights[None, :])
    after = np.sum(measure[:, None] * new * weights[None, :])
    native_rate = np.sum(
        np.asarray(transport_result.native_number_action_m3_s, dtype=np.longdouble)
        * weights
    )
    residual = after - before + np.longdouble(problem.dt_s) * native_rate
    scale = max(abs(float(before)), abs(float(after)), abs(float(problem.dt_s * native_rate)), 1.0e-300)
    return float(residual), scale, abs(float(residual)) / scale


def _energy_metrics(
    problem: CoupledCollisionTransportProblem,
    old_occupation: np.ndarray,
    occupation: np.ndarray,
    collision_result,
    transport_result,
    *,
    roundoff_safety_factor: float,
) -> tuple[float, float, float, float, float, float, bool]:
    weights = np.asarray(problem.grid.weights, dtype=np.longdouble)
    order = problem.transport.sorted_indices
    frequency = np.asarray(
        problem.transport.cell_centroid_frequency_Hz, dtype=np.longdouble
    )[:, None]
    measure = np.asarray(problem.network.mode_measure[order], dtype=np.longdouble)[:, None]
    h_long = np.longdouble(str(h))
    before = np.sum(
        h_long
        * frequency
        * np.asarray(old_occupation[order], dtype=np.longdouble)
        * measure
        * weights[None, :]
    )
    after = np.sum(
        h_long
        * frequency
        * np.asarray(occupation[order], dtype=np.longdouble)
        * measure
        * weights[None, :]
    )
    collision_energy_rate = np.longdouble(str(c)) * np.longdouble(
        str(float(collision_result.Q_gamma[0]))
    )
    expected = np.longdouble(str(problem.dt_s)) * (
        np.longdouble(str(float(transport_result.com_energy_action_W_m3)))
        + collision_energy_rate
    )
    residual = after - before - expected
    net_scale = max(abs(float(before)), abs(float(after)), abs(float(expected)), 1.0e-300)

    # ``gross_action_scale`` is the angularly weighted forward+reverse photon
    # number-action scale.  Multiplication by the largest photon momentum scale
    # and c is a conservative bound on the gross collision-energy action.
    collision_gross = (
        problem.dt_s
        * c
        * float(np.max(np.abs(problem.network.momentum_scale)))
        * float(collision_result.gross_action_scale)
    )
    flux = np.asarray(transport_result.face_flux_m3_s, dtype=np.longdouble)
    photon_energy = h_long * frequency
    transport_gross_rate = np.sum(
        weights[None, :]
        * photon_energy
        * (np.abs(flux[:-1]) + np.abs(flux[1:]))
    )
    transport_gross = float(np.longdouble(problem.dt_s) * transport_gross_rate)
    gross_scale = max(
        net_scale,
        collision_gross,
        transport_gross,
        1.0e-300,
    )
    raw = abs(float(residual))
    roundoff_bound = (
        float(roundoff_safety_factor) * np.finfo(float).eps * gross_scale
    )
    return (
        float(residual),
        raw / net_scale,
        raw / gross_scale,
        gross_scale,
        roundoff_bound,
        raw / max(roundoff_bound, 1.0e-300),
        bool(raw <= roundoff_bound),
    )


def _transport_gross_occupation_increment(
    problem: CoupledCollisionTransportProblem,
    transport_result,
) -> float:
    flux = np.abs(np.asarray(transport_result.face_flux_m3_s, dtype=float))
    order = problem.transport.sorted_indices
    gross_number = flux[:-1] + flux[1:]
    occupation_rate = gross_number / problem.network.mode_measure[order, None]
    return float(problem.dt_s * np.max(occupation_rate, initial=0.0))


def _collision_gross_occupation_increment(
    problem: CoupledCollisionTransportProblem,
    collision_result,
) -> float:
    minimum_weighted_mode = float(
        np.min(
            problem.network.mode_measure[:, None]
            * problem.grid.weights[None, :]
        )
    )
    return float(
        problem.dt_s
        * float(collision_result.gross_action_scale)
        / minimum_weighted_mode
    )


def assess_roundoff_aware_macro(
    problem: CoupledCollisionTransportProblem,
    *,
    old_occupation: Sequence[float] | np.ndarray,
    occupation: Sequence[float] | np.ndarray,
    initial_raw_residual: float | None = None,
    roundoff_safety_factor: float = 128.0,
    audit_pair_loop: bool = False,
) -> RoundoffAwareMacroAssessment:
    old = _positive_state(old_occupation, shape=problem.shape, name="old_occupation")
    state = _positive_state(occupation, shape=problem.shape, name="occupation")
    if not (math.isfinite(roundoff_safety_factor) and roundoff_safety_factor >= 1.0):
        raise ValueError("roundoff_safety_factor must be finite and at least one")

    residual = problem.residual(np.log(state), old)
    raw_residual = float(np.max(np.abs(residual)))
    net_scale = max(
        float(np.max(np.abs(old))),
        float(np.max(np.abs(state))),
        1.0e-300,
    )
    collision = problem._collision(state)
    transport = problem._transport(state)
    collision_gross = _collision_gross_occupation_increment(problem, collision)
    transport_gross = _transport_gross_occupation_increment(problem, transport)
    gross_scale = max(net_scale, collision_gross, transport_gross, 1.0e-300)
    roundoff_bound = (
        float(roundoff_safety_factor) * np.finfo(float).eps * gross_scale
    )
    number_raw, _number_scale, number_relative = _number_raw_and_scale(
        problem, old, state, transport
    )
    (
        energy_raw,
        energy_net_relative,
        energy_gross_backward,
        energy_gross_scale,
        energy_roundoff_bound,
        energy_roundoff_ratio,
        energy_roundoff_limited,
    ) = _energy_metrics(
        problem,
        old,
        state,
        collision,
        transport,
        roundoff_safety_factor=float(roundoff_safety_factor),
    )
    initial = raw_residual if initial_raw_residual is None else float(initial_raw_residual)
    if not math.isfinite(initial) or initial <= 0.0:
        raise ValueError("initial_raw_residual must be positive and finite")

    pair_action_relative: float | None = None
    pair_four_gross_relative: float | None = None
    if audit_pair_loop:
        pair = apply_nonlinear_bose_operator_pair_loop(
            state,
            mode_measure=problem.network.mode_measure,
            equilibrium_weight=problem.network.equilibrium_weight,
            pair_moments=problem.network.pair_moments,
            same_cell_rates=problem.network.same_cell_rates,
            grid=problem.grid,
            photon_momentum_scale=problem.network.momentum_scale,
        )
        action_scale = max(
            float(np.max(np.abs(collision.occupation_action))),
            float(np.max(np.abs(pair.occupation_action))),
            1.0e-300,
        )
        pair_action_relative = float(
            np.max(np.abs(collision.occupation_action - pair.occupation_action))
            / action_scale
        )
        q_gross = max(
            float(collision.gross_action_scale),
            float(pair.gross_action_scale),
            1.0e-300,
        ) * float(np.max(np.abs(problem.network.momentum_scale)))
        pair_four_gross_relative = float(
            np.linalg.norm(collision.Q_gamma - pair.Q_gamma)
            / max(q_gross, 1.0e-300)
        )

    return RoundoffAwareMacroAssessment(
        raw_residual_inf=raw_residual,
        net_scaled_residual=raw_residual / net_scale,
        gross_backward_error=raw_residual / gross_scale,
        gross_equation_scale=gross_scale,
        residual_roundoff_bound=roundoff_bound,
        residual_roundoff_ratio=raw_residual / max(roundoff_bound, 1.0e-300),
        residual_roundoff_limited=bool(raw_residual <= roundoff_bound),
        number_residual_m3=number_raw,
        number_relative_residual=number_relative,
        energy_residual_J_m3=energy_raw,
        energy_net_relative_residual=energy_net_relative,
        energy_gross_backward_error=energy_gross_backward,
        gross_energy_scale_J_m3=energy_gross_scale,
        energy_roundoff_bound_J_m3=energy_roundoff_bound,
        energy_roundoff_ratio=energy_roundoff_ratio,
        energy_roundoff_limited=energy_roundoff_limited,
        collision_four_force_residual=float(
            np.linalg.norm(collision.Q_gamma + collision.Q_atom)
        ),
        collision_entropy_production=float(collision.entropy_production),
        minimum_occupation=float(np.min(state)),
        residual_reduction=raw_residual / initial,
        collision_gross_increment=collision_gross,
        transport_gross_increment=transport_gross,
        pair_loop_action_relative_residual=pair_action_relative,
        pair_loop_four_force_gross_relative_residual=pair_four_gross_relative,
    )


def _activity_shift(
    problem: CoupledCollisionTransportProblem,
    occupation: np.ndarray,
    log_shift: float,
) -> np.ndarray:
    z = problem.network.equilibrium_weight / problem.network.mode_measure
    phi = occupation / (z[:, None] * (1.0 + occupation))
    shifted_phi = math.exp(float(log_shift)) * phi
    denominator = 1.0 - z[:, None] * shifted_phi
    if np.any(denominator <= 0.0):
        raise FloatingPointError("activity restoration crossed the Bose pole")
    result = z[:, None] * shifted_phi / denominator
    if not np.all(np.isfinite(result)) or np.any(result <= 0.0):
        raise FloatingPointError("activity-restored occupation is not positive")
    return result


def restore_activity_number_ledger(
    problem: CoupledCollisionTransportProblem,
    *,
    old_occupation: Sequence[float] | np.ndarray,
    occupation: Sequence[float] | np.ndarray,
    tolerance: float = 1.0e-11,
    maximum_iterations: int = 8,
    maximum_relative_correction: float = 1.0e-8,
) -> ActivityNumberRestoration:
    old = _positive_state(old_occupation, shape=problem.shape, name="old_occupation")
    base = _positive_state(occupation, shape=problem.shape, name="occupation")
    threshold = float(tolerance)
    if not (math.isfinite(threshold) and threshold > 0.0):
        raise ValueError("tolerance must be positive and finite")
    shift = 0.0
    best_state = base
    best_raw = math.inf
    best_relative = math.inf
    used = 0
    for iteration in range(int(maximum_iterations) + 1):
        state = _activity_shift(problem, base, shift)
        transport = problem._transport(state)
        raw, _scale, relative = _number_raw_and_scale(problem, old, state, transport)
        if abs(raw) < abs(best_raw):
            best_state = state
            best_raw = raw
            best_relative = relative
        if relative <= threshold:
            used = iteration
            break
        if iteration == int(maximum_iterations):
            used = iteration
            break
        direction = state * (1.0 + state)
        transport_jvp = problem.transport.jvp(
            state,
            direction,
            face_speeds_x_s_inv=problem.face_speeds_x_s_inv,
            grid=problem.grid,
        )
        weights = np.asarray(problem.grid.weights, dtype=np.longdouble)
        measure = np.asarray(problem.network.mode_measure, dtype=np.longdouble)
        after_derivative = np.sum(
            measure[:, None]
            * np.asarray(direction, dtype=np.longdouble)
            * weights[None, :]
        )
        native_derivative = np.sum(
            np.asarray(
                -transport_jvp.face_flux_jvp_m3_s[0]
                + transport_jvp.face_flux_jvp_m3_s[-1],
                dtype=np.longdouble,
            )
            * weights
        )
        derivative = float(
            after_derivative
            + np.longdouble(problem.dt_s) * native_derivative
        )
        if not math.isfinite(derivative) or derivative == 0.0:
            break
        proposed = -raw / derivative
        accepted = False
        damping = 1.0
        for _ in range(24):
            candidate_shift = shift + damping * proposed
            candidate = _activity_shift(problem, base, candidate_shift)
            candidate_transport = problem._transport(candidate)
            candidate_raw, _candidate_scale, candidate_relative = _number_raw_and_scale(
                problem, old, candidate, candidate_transport
            )
            if abs(candidate_raw) < abs(raw) or candidate_relative <= threshold:
                shift = candidate_shift
                accepted = True
                break
            damping *= 0.5
        if not accepted:
            break
        used = iteration + 1

    correction = float(np.max(np.abs(best_state / base - 1.0)))
    if correction > float(maximum_relative_correction):
        raise FloatingPointError(
            "number-ledger activity restoration exceeded the bounded correction"
        )
    if best_relative > threshold:
        raise RuntimeError(
            f"number-ledger activity restoration failed: {best_relative}"
        )
    return ActivityNumberRestoration(
        occupation=best_state,
        log_activity_shift=shift,
        maximum_relative_correction=correction,
        number_residual_m3=best_raw,
        number_relative_residual=best_relative,
        iterations=used,
    )


def solve_roundoff_aware_single_macro(
    problem: CoupledCollisionTransportProblem,
    old_occupation: Sequence[float] | np.ndarray,
    *,
    initial_occupation: Sequence[float] | np.ndarray | None = None,
    tolerance: float = 1.0e-11,
    pair_loop_tolerance: float = 1.0e-8,
    maximum_newton_iterations: int = 8,
    gmres_rtol: float = 1.0e-10,
    gmres_restart: int = 80,
    gmres_maxiter: int = 300,
    roundoff_safety_factor: float = 128.0,
) -> RoundoffAwareSingleMacroResult:
    old = _positive_state(old_occupation, shape=problem.shape, name="old_occupation")
    initial = old if initial_occupation is None else _positive_state(
        initial_occupation, shape=problem.shape, name="initial_occupation"
    )
    reference = old
    relative_log = np.log(initial / reference)
    initial_residual = problem.residual(np.log(initial), old)
    initial_raw = float(np.max(np.abs(initial_residual)))
    if initial_raw <= 0.0:
        initial_raw = np.finfo(float).tiny
    iterations: list[SingleMacroIteration] = []
    total_gmres = 0
    started = time.perf_counter()
    final_state = initial
    activity_shift = 0.0
    activity_correction = 0.0
    convergence_basis = "not_converged"
    converged = False

    for newton_index in range(int(maximum_newton_iterations) + 1):
        state = reference * np.exp(relative_log)
        assessment = assess_roundoff_aware_macro(
            problem,
            old_occupation=old,
            occupation=state,
            initial_raw_residual=initial_raw,
            roundoff_safety_factor=roundoff_safety_factor,
            audit_pair_loop=False,
        )
        if (
            assessment.residual_roundoff_limited
            and assessment.gross_backward_error <= tolerance
            and assessment.number_relative_residual > tolerance
        ):
            restored = restore_activity_number_ledger(
                problem,
                old_occupation=old,
                occupation=state,
                tolerance=tolerance,
            )
            state = np.asarray(restored.occupation)
            relative_log = np.log(state / reference)
            activity_shift = restored.log_activity_shift
            activity_correction = restored.maximum_relative_correction
            assessment = assess_roundoff_aware_macro(
                problem,
                old_occupation=old,
                occupation=state,
                initial_raw_residual=initial_raw,
                roundoff_safety_factor=roundoff_safety_factor,
                audit_pair_loop=True,
            )
            if assessment.passed(
                tolerance=tolerance,
                pair_loop_tolerance=pair_loop_tolerance,
            ):
                final_state = state
                converged = True
                convergence_basis = (
                    "roundoff_limited_gross_backward_error_and_ledgers"
                )
                iterations.append(
                    SingleMacroIteration(
                        iteration=newton_index,
                        raw_residual_inf=assessment.raw_residual_inf,
                        normalized_residual_inf=assessment.net_scaled_residual,
                        gross_backward_error=assessment.gross_backward_error,
                        number_relative_residual=assessment.number_relative_residual,
                        residual_roundoff_ratio=assessment.residual_roundoff_ratio,
                        gmres_iterations=0,
                        damping=0.0,
                    )
                )
                break

        if newton_index == int(maximum_newton_iterations):
            final_state = state
            break

        residual = problem.residual(np.log(state), old)
        normalized = residual / reference
        size = old.size

        def matvec(flat: np.ndarray) -> np.ndarray:
            direction = np.asarray(flat, dtype=float).reshape(problem.shape)
            return (
                problem.residual_jvp(np.log(state), direction) / reference
            ).ravel()

        operator = LinearOperator((size, size), matvec=matvec, dtype=float)
        diagonal = (
            state * (1.0 + problem.dt_s * problem._approximate_loss_rate_s_inv())
            / reference
        )
        preconditioner = LinearOperator(
            (size, size),
            matvec=lambda flat: np.asarray(flat, dtype=float)
            / np.maximum(diagonal.ravel(), 1.0e-300),
            dtype=float,
        )
        counter = {"iterations": 0}

        def callback(_residual_norm: float) -> None:
            counter["iterations"] += 1

        step, info = gmres(
            operator,
            -normalized.ravel(),
            M=preconditioner,
            rtol=float(gmres_rtol),
            atol=0.0,
            restart=int(gmres_restart),
            maxiter=int(gmres_maxiter),
            callback=callback,
            callback_type="pr_norm",
        )
        total_gmres += counter["iterations"]
        if info != 0 or not np.all(np.isfinite(step)):
            final_state = state
            convergence_basis = f"gmres_failure_{info}"
            break
        step = step.reshape(problem.shape)
        base = float(np.max(np.abs(normalized)))
        accepted = False
        damping = 1.0
        for _ in range(40):
            candidate_log = relative_log + damping * step
            if np.min(candidate_log) > -700.0 and np.max(candidate_log) < 700.0:
                candidate_state = reference * np.exp(candidate_log)
                candidate_residual = problem.residual(
                    np.log(candidate_state), old
                ) / reference
                candidate_norm = float(np.max(np.abs(candidate_residual)))
                if candidate_norm < base:
                    relative_log = candidate_log
                    accepted = True
                    break
            damping *= 0.5
        iterations.append(
            SingleMacroIteration(
                iteration=newton_index,
                raw_residual_inf=assessment.raw_residual_inf,
                normalized_residual_inf=assessment.net_scaled_residual,
                gross_backward_error=assessment.gross_backward_error,
                number_relative_residual=assessment.number_relative_residual,
                residual_roundoff_ratio=assessment.residual_roundoff_ratio,
                gmres_iterations=counter["iterations"],
                damping=damping if accepted else 0.0,
            )
        )
        if not accepted:
            final_state = state
            convergence_basis = "line_search_stalled"
            break
    else:  # pragma: no cover - defensive; loop always exits above
        final_state = reference * np.exp(relative_log)

    final_assessment = assess_roundoff_aware_macro(
        problem,
        old_occupation=old,
        occupation=final_state,
        initial_raw_residual=initial_raw,
        roundoff_safety_factor=roundoff_safety_factor,
        audit_pair_loop=True,
    )
    if not converged and final_assessment.passed(
        tolerance=tolerance,
        pair_loop_tolerance=pair_loop_tolerance,
    ):
        converged = True
        convergence_basis = "roundoff_limited_gross_backward_error_and_ledgers"
    return RoundoffAwareSingleMacroResult(
        occupation=final_state,
        converged=converged,
        convergence_basis=convergence_basis,
        assessment=final_assessment,
        iterations=tuple(iterations),
        activity_log_shift=activity_shift,
        activity_shift_max_relative=activity_correction,
        total_gmres_iterations=total_gmres,
        elapsed_s=time.perf_counter() - started,
    )


__all__ = [
    "ActivityNumberRestoration",
    "RoundoffAwareMacroAssessment",
    "RoundoffAwareSingleMacroResult",
    "SingleMacroIteration",
    "assess_roundoff_aware_macro",
    "restore_activity_number_ledger",
    "solve_roundoff_aware_single_macro",
]

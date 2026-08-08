"""Positive angle-resolved transport along Bianchi characteristics.

This compatibility module preserves the accepted-history ``CharacteristicAngularSolver``
API from v0.66 and adds the frozen-background frequency-face reference API used by
v0.67/v0.68.  The two result records remain distinct because they encode different
initial-boundary-value problems.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np

from full_bianchi_hyrec.background.characteristics import (
    HydrogenFrameCharacteristic,
    aberrate_direction,
    hydrogen_frame_characteristic,
    normal_frame_characteristic,
)
from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence

Coefficient = Callable[[float, float], float]


def _zero(_: float, __: float) -> float:
    return 0.0


@dataclass(frozen=True)
class IsotropicTransferCoefficients:
    emissivity_s_inv: Coefficient
    opacity_s_inv: Coefficient

    @classmethod
    def zero(cls) -> "IsotropicTransferCoefficients":
        return cls(_zero, _zero)


@dataclass(frozen=True)
class CharacteristicFaceResult:
    occupation_face: float
    face_frequency_Hz: float
    initial_frequency_Hz: float
    initial_direction_hydrogen: np.ndarray
    face_direction_hydrogen: np.ndarray
    minimum_doppler_factor: float
    n_step: int


def _unit(value: np.ndarray) -> np.ndarray:
    vector = np.asarray(value, dtype=float)
    norm = float(np.linalg.norm(vector))
    if vector.shape != (3,) or not np.all(np.isfinite(vector)) or norm <= 0.0:
        raise ValueError("direction must be a finite nonzero three-vector")
    return vector / norm


class CharacteristicAngularSolver:
    """Second-order characteristic path plus positive formal transfer solve.

    Geometry is integrated backward from an exact face state.  The scalar
    isotropic source/opacity equation is then integrated forward on the stored
    path with a midpoint-exact constant-coefficient update.  This avoids any
    instantaneous scalar-to-angular inversion.
    """

    def __init__(self, sequence: BackgroundSnapshotSequence) -> None:
        self.sequence = sequence

    def _rhs(self, tau: float, direction_h: np.ndarray, log_frequency: float) -> tuple[np.ndarray, float, float]:
        snapshot = self.sequence.snapshot_at_tau(float(tau))
        direction_n = aberrate_direction(-snapshot.beta_H, direction_h)
        normal = normal_frame_characteristic(snapshot, direction_n)
        hydrogen = hydrogen_frame_characteristic(snapshot, normal)
        return (
            hydrogen.D0_direction_hydrogen_s_inv / snapshot.H_s_inv,
            hydrogen.R_hydrogen_s_inv / snapshot.H_s_inv,
            hydrogen.doppler_factor,
        )

    def _midpoint_geometry_step(
        self,
        tau: float,
        direction_h: np.ndarray,
        log_frequency: float,
        step: float,
    ) -> tuple[np.ndarray, float, float]:
        d0, r0, doppler0 = self._rhs(tau, direction_h, log_frequency)
        mid_direction = _unit(direction_h + 0.5 * step * d0)
        mid_log_frequency = log_frequency + 0.5 * step * r0
        dm, rm, dopplerm = self._rhs(tau + 0.5 * step, mid_direction, mid_log_frequency)
        new_direction = _unit(direction_h + step * dm)
        new_log_frequency = log_frequency + step * rm
        return new_direction, float(new_log_frequency), min(float(doppler0), float(dopplerm))

    def trace_to_face(
        self,
        *,
        tau_start: float,
        tau_end: float,
        direction_hydrogen: np.ndarray,
        face_frequency_Hz: float,
        initial_occupation: float,
        coefficients: IsotropicTransferCoefficients,
        n_step: int = 256,
    ) -> CharacteristicFaceResult:
        start = float(tau_start)
        end = float(tau_end)
        if not math.isfinite(start + end) or end <= start:
            raise ValueError("require finite tau_start < tau_end")
        if n_step < 2:
            raise ValueError("n_step must be at least two")
        face_direction = _unit(direction_hydrogen)
        face_frequency = float(face_frequency_Hz)
        occupation = float(initial_occupation)
        if face_frequency <= 0.0 or occupation < 0.0:
            raise ValueError("frequency must be positive and occupation nonnegative")

        tau = np.linspace(end, start, n_step + 1)
        direction = np.empty((n_step + 1, 3), dtype=float)
        log_frequency = np.empty(n_step + 1, dtype=float)
        direction[0] = face_direction
        log_frequency[0] = math.log(face_frequency)
        minimum_doppler = math.inf
        for index in range(n_step):
            step = float(tau[index + 1] - tau[index])
            direction[index + 1], log_frequency[index + 1], doppler = self._midpoint_geometry_step(
                float(tau[index]), direction[index], float(log_frequency[index]), step
            )
            minimum_doppler = min(minimum_doppler, doppler)
        if minimum_doppler <= 0.0:
            raise FloatingPointError("finite-tilt Doppler factor lost positivity")

        tau_forward = tau[::-1]
        log_frequency_forward = log_frequency[::-1]
        for index in range(n_step):
            left = float(tau_forward[index])
            right = float(tau_forward[index + 1])
            midpoint = 0.5 * (left + right)
            lognu = 0.5 * (log_frequency_forward[index] + log_frequency_forward[index + 1])
            frequency = math.exp(lognu)
            snapshot = self.sequence.snapshot_at_tau(midpoint)
            physical_dt = (right - left) / snapshot.H_s_inv
            eta = float(coefficients.emissivity_s_inv(midpoint, frequency))
            chi = float(coefficients.opacity_s_inv(midpoint, frequency))
            if not math.isfinite(eta + chi) or eta < 0.0 or chi < 0.0:
                raise ValueError("emissivity and opacity must be finite and nonnegative")
            if chi == 0.0:
                occupation += eta * physical_dt
            else:
                attenuation = math.exp(-chi * physical_dt)
                occupation = attenuation * occupation + eta * (-math.expm1(-chi * physical_dt)) / chi
            if occupation < 0.0 or not math.isfinite(occupation):
                raise FloatingPointError("characteristic transfer lost positivity")

        return CharacteristicFaceResult(
            occupation_face=float(occupation),
            face_frequency_Hz=face_frequency,
            initial_frequency_Hz=float(math.exp(log_frequency[-1])),
            initial_direction_hydrogen=direction[-1].copy(),
            face_direction_hydrogen=face_direction.copy(),
            minimum_doppler_factor=float(minimum_doppler),
            n_step=int(n_step),
        )

def constant_coefficient_transfer(
    *,
    f_initial: float,
    emissivity_s_inv: float,
    opacity_s_inv: float,
    travel_time_s: float,
) -> float:
    """Exact positive solution of ``df/dt = emissivity - opacity*f``."""

    f0 = float(f_initial)
    emissivity = float(emissivity_s_inv)
    opacity = float(opacity_s_inv)
    duration = float(travel_time_s)
    if not all(math.isfinite(v) for v in (f0, emissivity, opacity, duration)):
        raise ValueError("transfer inputs must be finite")
    if f0 < 0.0 or emissivity < 0.0 or opacity < 0.0 or duration < 0.0:
        raise ValueError("physical occupation, emissivity, opacity and time must be nonnegative")
    if opacity == 0.0:
        return f0 + emissivity * duration
    optical_depth = opacity * duration
    absorbed = -math.expm1(-optical_depth)
    transmission = 1.0 - absorbed
    return transmission * f0 + emissivity * absorbed / opacity


def constant_coefficient_transfer_jvp(
    *,
    f_initial: float,
    emissivity_s_inv: float,
    opacity_s_inv: float,
    travel_time_s: float,
    d_f_initial: float = 0.0,
    d_emissivity_s_inv: float = 0.0,
    d_opacity_s_inv: float = 0.0,
    d_travel_time_s: float = 0.0,
) -> float:
    """Analytic JVP of :func:`constant_coefficient_transfer`."""

    f0 = float(f_initial)
    j = float(emissivity_s_inv)
    chi = float(opacity_s_inv)
    time = float(travel_time_s)
    # Reuse validation and keep the chi=0 derivative as the analytic limit.
    constant_coefficient_transfer(
        f_initial=f0,
        emissivity_s_inv=j,
        opacity_s_inv=chi,
        travel_time_s=time,
    )
    df0 = float(d_f_initial)
    dj = float(d_emissivity_s_inv)
    dchi = float(d_opacity_s_inv)
    dtime = float(d_travel_time_s)
    if chi == 0.0:
        return (
            df0
            + time * dj
            + j * dtime
            + (-time * f0 - 0.5 * j * time**2) * dchi
        )

    optical_depth = chi * time
    transmission = math.exp(-optical_depth)
    absorbed = 1.0 - transmission
    source_factor = absorbed / chi
    dsource_dchi = (time * transmission * chi - absorbed) / chi**2
    return (
        transmission * df0
        + source_factor * dj
        + (-time * transmission * f0 + j * dsource_dchi) * dchi
        + transmission * (j - chi * f0) * dtime
    )


@dataclass(frozen=True)
class BianchiCharacteristicFaceResult:
    direction_normal: np.ndarray
    direction_hydrogen: np.ndarray
    frequency_face_Hz: float
    frequency_relative_residual: float
    f_face: float
    travel_time_s: float
    minimum_doppler_factor: float
    minimum_abs_frequency_speed_s_inv: float
    step_count: int

    def __post_init__(self) -> None:
        for name in ("direction_normal", "direction_hydrogen"):
            array = _unit(np.asarray(getattr(self, name), dtype=float))
            array.setflags(write=False)
            object.__setattr__(self, name, array)


class BianchiCharacteristicFaceSolver:
    """Frozen-background RK4 reference with frequency-face event localization."""

    def __init__(self, snapshot: BackgroundSnapshot) -> None:
        self.snapshot = snapshot

    def local_characteristic(self, direction_normal) -> HydrogenFrameCharacteristic:
        normal = normal_frame_characteristic(self.snapshot, direction_normal)
        return hydrogen_frame_characteristic(self.snapshot, normal)

    def _rhs(self, direction_normal: np.ndarray) -> tuple[np.ndarray, float, float]:
        normal = normal_frame_characteristic(self.snapshot, direction_normal)
        hydrogen = hydrogen_frame_characteristic(self.snapshot, normal)
        return (
            np.asarray(normal.D0_direction_normal_s_inv, dtype=float),
            float(hydrogen.R_hydrogen_s_inv),
            float(hydrogen.doppler_factor),
        )

    def _rk4_step(
        self,
        direction_normal: np.ndarray,
        log_frequency: float,
        dt_s: float,
    ) -> tuple[np.ndarray, float, tuple[float, ...], tuple[float, ...]]:
        n0 = _unit(direction_normal)
        dt = float(dt_s)
        k1n, k1f, d1 = self._rhs(n0)
        n2 = _unit(n0 + 0.5 * dt * k1n)
        k2n, k2f, d2 = self._rhs(n2)
        n3 = _unit(n0 + 0.5 * dt * k2n)
        k3n, k3f, d3 = self._rhs(n3)
        n4 = _unit(n0 + dt * k3n)
        k4n, k4f, d4 = self._rhs(n4)
        result_n = _unit(n0 + dt * (k1n + 2.0 * k2n + 2.0 * k3n + k4n) / 6.0)
        result_log_frequency = log_frequency + dt * (
            k1f + 2.0 * k2f + 2.0 * k3f + k4f
        ) / 6.0
        return (
            result_n,
            float(result_log_frequency),
            (float(k1f), float(k2f), float(k3f), float(k4f)),
            (d1, d2, d3, d4),
        )

    def trace_to_frequency_face(
        self,
        *,
        direction_normal,
        frequency_initial_Hz: float,
        frequency_target_Hz: float,
        f_initial: float,
        emissivity_s_inv: float = 0.0,
        opacity_s_inv: float = 0.0,
        n_steps: int = 64,
        time_safety_factor: float = 4.0,
    ) -> BianchiCharacteristicFaceResult:
        nu0 = float(frequency_initial_Hz)
        target = float(frequency_target_Hz)
        if not (
            math.isfinite(nu0)
            and math.isfinite(target)
            and nu0 > 0.0
            and target > 0.0
        ):
            raise ValueError("frequencies must be positive and finite")
        if int(n_steps) < 2:
            raise ValueError("n_steps must be at least two")
        direction = _unit(np.asarray(direction_normal, dtype=float))
        initial = self.local_characteristic(direction)
        delta_log = math.log(target / nu0)
        if delta_log == 0.0:
            return BianchiCharacteristicFaceResult(
                direction_normal=direction,
                direction_hydrogen=initial.direction_hydrogen,
                frequency_face_Hz=nu0,
                frequency_relative_residual=0.0,
                f_face=float(f_initial),
                travel_time_s=0.0,
                minimum_doppler_factor=initial.doppler_factor,
                minimum_abs_frequency_speed_s_inv=abs(initial.R_hydrogen_s_inv),
                step_count=0,
            )
        if delta_log * initial.R_hydrogen_s_inv <= 0.0:
            raise ValueError("requested frequency face is not forward-reachable")
        if initial.R_hydrogen_s_inv == 0.0:
            raise ValueError("frequency-speed zero requires event localization")

        estimated_time = delta_log / initial.R_hydrogen_s_inv
        maximum_time = float(time_safety_factor) * estimated_time
        if maximum_time <= 0.0 or not math.isfinite(maximum_time):
            raise ValueError("invalid characteristic travel-time estimate")
        dt = maximum_time / int(n_steps)
        target_log = math.log(target)
        log_frequency = math.log(nu0)
        orientation = math.copysign(1.0, delta_log)
        elapsed = 0.0
        min_doppler = initial.doppler_factor
        min_abs_speed = abs(initial.R_hydrogen_s_inv)
        previous_speed = initial.R_hydrogen_s_inv

        for step in range(1, int(n_steps) + 1):
            next_direction, next_log, speeds, dopplers = self._rk4_step(
                direction, log_frequency, dt
            )
            min_doppler = min(min_doppler, *dopplers)
            min_abs_speed = min(min_abs_speed, *(abs(item) for item in speeds))
            if min(dopplers) <= 0.0:
                raise ValueError("finite-tilt Doppler factor lost positivity")
            if any(item == 0.0 or item * previous_speed < 0.0 for item in speeds):
                raise ValueError("frequency-speed zero requires event localization")

            if orientation * (next_log - target_log) >= 0.0:
                lower = 0.0
                upper = dt
                face_direction = direction
                face_log = log_frequency
                for _ in range(64):
                    middle = 0.5 * (lower + upper)
                    candidate_direction, candidate_log, candidate_speeds, candidate_dopplers = self._rk4_step(
                        direction, log_frequency, middle
                    )
                    min_doppler = min(min_doppler, *candidate_dopplers)
                    min_abs_speed = min(
                        min_abs_speed, *(abs(item) for item in candidate_speeds)
                    )
                    if orientation * (candidate_log - target_log) >= 0.0:
                        upper = middle
                        face_direction = candidate_direction
                        face_log = candidate_log
                    else:
                        lower = middle
                event_dt = upper
                elapsed += event_dt
                frequency_face = math.exp(face_log)
                hydrogen = self.local_characteristic(face_direction)
                f_face = constant_coefficient_transfer(
                    f_initial=f_initial,
                    emissivity_s_inv=emissivity_s_inv,
                    opacity_s_inv=opacity_s_inv,
                    travel_time_s=elapsed,
                )
                return BianchiCharacteristicFaceResult(
                    direction_normal=face_direction,
                    direction_hydrogen=hydrogen.direction_hydrogen,
                    frequency_face_Hz=frequency_face,
                    frequency_relative_residual=abs(frequency_face - target) / target,
                    f_face=f_face,
                    travel_time_s=elapsed,
                    minimum_doppler_factor=min_doppler,
                    minimum_abs_frequency_speed_s_inv=min_abs_speed,
                    step_count=step,
                )

            direction = next_direction
            log_frequency = next_log
            elapsed += dt
            previous_speed = speeds[-1]

        raise ValueError("frequency face was not reached within the bounded characteristic interval")


__all__ = [
    "CharacteristicAngularSolver",
    "CharacteristicFaceResult",
    "IsotropicTransferCoefficients",
    "BianchiCharacteristicFaceResult",
    "BianchiCharacteristicFaceSolver",
    "constant_coefficient_transfer",
    "constant_coefficient_transfer_jvp",
]

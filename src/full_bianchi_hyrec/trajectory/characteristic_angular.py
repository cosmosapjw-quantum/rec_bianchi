"""Positive angle-resolved transport along exact Bianchi characteristics."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np

from full_bianchi_hyrec.background.characteristics import (
    aberrate_direction,
    hydrogen_frame_characteristic,
    normal_frame_characteristic,
)
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


__all__ = [
    "CharacteristicAngularSolver",
    "CharacteristicFaceResult",
    "IsotropicTransferCoefficients",
]

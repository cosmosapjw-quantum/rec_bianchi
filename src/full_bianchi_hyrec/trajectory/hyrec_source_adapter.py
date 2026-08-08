"""Source-locked original-HyRec virtual-bin transfer adapter.

The October-2012 FULL solver does not expose a standalone continuum opacity.
For every virtual spike it exposes an incoming distortion, an algebraic source
function and a source optical depth.  This module keeps that exact integrated
transfer map and generalizes only the frequency-drift denominator from FLRW H
to a directional hydrogen-frame redshift rate on a monotone branch.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.constants import h, k

from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    OriginalHyRecTrajectorySnapshot,
    physical_log_mode_factor_per_H,
)


@dataclass(frozen=True)
class OriginalHyRecVirtualSourceAdapter:
    source_function: np.ndarray
    tau_flrw: np.ndarray
    gamma_s_inv: np.ndarray
    mode_factor_per_H: np.ndarray
    x1s: float
    H_s_inv: float

    def __post_init__(self) -> None:
        arrays = {}
        for name in ("source_function", "tau_flrw", "gamma_s_inv", "mode_factor_per_H"):
            value = np.asarray(getattr(self, name), dtype=float)
            if value.ndim != 1 or not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must be a finite one-dimensional array")
            arrays[name] = value.copy()
        size = len(arrays["source_function"])
        if any(len(value) != size for value in arrays.values()):
            raise ValueError("source-adapter array lengths differ")
        if np.any(arrays["tau_flrw"] < 0.0) or np.any(arrays["gamma_s_inv"] <= 0.0):
            raise ValueError("optical depths/rates must be nonnegative/positive")
        if np.any(arrays["mode_factor_per_H"] <= 0.0):
            raise ValueError("mode factor must be positive")
        for name, value in arrays.items():
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        if self.x1s <= 0.0 or self.H_s_inv <= 0.0:
            raise ValueError("x1s and H must be positive")

    @classmethod
    def from_snapshot(cls, snapshot: OriginalHyRecTrajectorySnapshot) -> "OriginalHyRecVirtualSourceAdapter":
        # Use the source-locked h c constant, not CODATA h/c separately.
        # The October-2012 source rounds h c; substituting scipy.constants
        # shifts every optical depth by 2.66e-7 and breaks source parity.
        mode_factor = physical_log_mode_factor_per_H(snapshot)
        reconstructed_tau = snapshot.x1s * snapshot.Gamma_s_inv / (
            snapshot.H_s_inv * mode_factor
        )
        residual = np.max(
            np.abs(reconstructed_tau - snapshot.Dtau)
            / np.maximum(np.abs(snapshot.Dtau), 1.0e-300)
        )
        if residual > 5.0e-12:
            raise FloatingPointError(f"source tau relation failed: {residual}")
        return cls(
            source_function=snapshot.Dfeq,
            tau_flrw=snapshot.Dtau,
            gamma_s_inv=snapshot.Gamma_s_inv,
            mode_factor_per_H=mode_factor,
            x1s=float(snapshot.x1s),
            H_s_inv=float(snapshot.H_s_inv),
        )


def apply_escape_transfer(incoming: np.ndarray, source_function: np.ndarray, optical_depth: np.ndarray) -> np.ndarray:
    incoming = np.asarray(incoming, dtype=float)
    source = np.asarray(source_function, dtype=float)
    tau = np.asarray(optical_depth, dtype=float)
    if incoming.shape != source.shape or incoming.shape != tau.shape:
        raise ValueError("incoming/source/tau shape mismatch")
    if np.any(tau < 0.0) or not np.all(np.isfinite(incoming + source + tau)):
        raise ValueError("invalid source transfer inputs")
    return incoming + (source - incoming) * (-np.expm1(-tau))


def directional_optical_depth(
    adapter: OriginalHyRecVirtualSourceAdapter,
    *,
    redshift_rate_s_inv: float,
) -> np.ndarray:
    rate = float(redshift_rate_s_inv)
    if not math.isfinite(rate) or rate >= 0.0:
        raise ValueError("redshift_rate_s_inv must be finite and negative on this branch")
    return adapter.tau_flrw * adapter.H_s_inv / (-rate)


def one_photon_paired_action(
    *,
    occupation: float,
    upper_population: float,
    lower_population: float,
    degeneracy_ratio: float,
    spontaneous_rate_s_inv: float,
) -> float:
    f = float(occupation)
    xu = float(upper_population)
    xl = float(lower_population)
    g = float(degeneracy_ratio)
    A = float(spontaneous_rate_s_inv)
    if min(f, xu, xl, g, A) < 0.0 or not all(map(math.isfinite, (f, xu, xl, g, A))):
        raise ValueError("one-photon paired inputs must be finite and nonnegative")
    return A * (xu * (1.0 + f) - g * xl * f)


def one_photon_planck_null_residual(
    *, frequency_Hz: float, temperature_K: float, lower_population: float,
    degeneracy_ratio: float, spontaneous_rate_s_inv: float,
) -> float:
    z = math.exp(-h * float(frequency_Hz) / (k * float(temperature_K)))
    upper = float(lower_population) * float(degeneracy_ratio) * z
    planck = z / (1.0 - z)
    action = one_photon_paired_action(
        occupation=planck,
        upper_population=upper,
        lower_population=lower_population,
        degeneracy_ratio=degeneracy_ratio,
        spontaneous_rate_s_inv=spontaneous_rate_s_inv,
    )
    scale = max(abs(spontaneous_rate_s_inv * lower_population), 1.0e-300)
    return abs(action) / scale


__all__ = [
    "OriginalHyRecVirtualSourceAdapter",
    "apply_escape_transfer",
    "directional_optical_depth",
    "one_photon_paired_action",
    "one_photon_planck_null_residual",
]

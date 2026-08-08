"""Hydrogen-frame radiative source adapters for PR-05C2C1B.

Two objects are deliberately separated:

``OriginalHyRecVirtualSpikeSource``
    A source-identical distributional adapter for the October-2012 HyRec
    ``Dtau/Dfeq/Dfplus -> Dfminus`` update.  It acts on the signed spectral
    distortion and carries exact C-source provenance.

``IsotropicEinsteinLineSource``
    A positive paired-rate physical line model implementing the v0.65 scalar,
    unpolarized hydrogen-frame source-isotropy axiom.  It is a theory-contract
    adapter, not a claim that original HyRec stores these coefficients in this
    decomposed form.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.constants import c, h, k


HYREC_SOURCE_FILE = "HyRec/hydrogen.c"
HYREC_SPIKE_SOURCE_LINES = (521, 524, 525, 780, 781, 787, 789)


def _readonly(array: np.ndarray) -> np.ndarray:
    result = np.array(array, dtype=float, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class OriginalHyRecVirtualSpikeSource:
    """Vectorized exact adapter for the canonical virtual-spike update."""

    tau_flrw: np.ndarray
    equilibrium_departure: np.ndarray
    H_s_inv: float
    source_file: str = HYREC_SOURCE_FILE
    source_lines: tuple[int, ...] = HYREC_SPIKE_SOURCE_LINES

    def __post_init__(self) -> None:
        tau = np.asarray(self.tau_flrw, dtype=float)
        equilibrium = np.asarray(self.equilibrium_departure, dtype=float)
        if tau.ndim != 1 or equilibrium.shape != tau.shape:
            raise ValueError("tau_flrw and equilibrium_departure must be equal 1-D arrays")
        if not np.all(np.isfinite(tau)) or np.any(tau < 0.0):
            raise ValueError("tau_flrw must be finite and nonnegative")
        if not np.all(np.isfinite(equilibrium)):
            raise ValueError("equilibrium_departure must be finite")
        hubble = float(self.H_s_inv)
        if not (math.isfinite(hubble) and hubble > 0.0):
            raise ValueError("H_s_inv must be positive and finite")
        object.__setattr__(self, "tau_flrw", _readonly(tau))
        object.__setattr__(self, "equilibrium_departure", _readonly(equilibrium))
        object.__setattr__(self, "H_s_inv", hubble)

    def directional_optical_depth(
        self,
        *,
        minus_dlognu_dt_s_inv: np.ndarray,
    ) -> np.ndarray:
        speed = np.asarray(minus_dlognu_dt_s_inv, dtype=float)
        if speed.shape != self.tau_flrw.shape or not np.all(np.isfinite(speed)):
            raise ValueError("frequency-speed array must match tau_flrw and be finite")
        if np.any(speed == 0.0):
            raise ValueError("frequency-speed zero requires event localization")
        return self.tau_flrw * self.H_s_inv / np.abs(speed)

    def apply(
        self,
        *,
        incoming: np.ndarray,
        minus_dlognu_dt_s_inv: np.ndarray,
    ) -> np.ndarray:
        values = np.asarray(incoming, dtype=float)
        if values.shape != self.tau_flrw.shape or not np.all(np.isfinite(values)):
            raise ValueError("incoming must match tau_flrw and be finite")
        tau = self.directional_optical_depth(
            minus_dlognu_dt_s_inv=minus_dlognu_dt_s_inv
        )
        absorbed = -np.expm1(-tau)
        result = values + (self.equilibrium_departure - values) * absorbed
        return _readonly(result)

    def jvp(
        self,
        *,
        incoming: np.ndarray,
        minus_dlognu_dt_s_inv: np.ndarray,
        d_incoming: np.ndarray,
        d_equilibrium_departure: np.ndarray,
        d_tau_flrw: np.ndarray,
        d_H_s_inv: float,
        d_minus_dlognu_dt_s_inv: np.ndarray,
    ) -> np.ndarray:
        incoming = np.asarray(incoming, dtype=float)
        speed = np.asarray(minus_dlognu_dt_s_inv, dtype=float)
        d_incoming = np.asarray(d_incoming, dtype=float)
        d_equilibrium = np.asarray(d_equilibrium_departure, dtype=float)
        d_tau_flrw = np.asarray(d_tau_flrw, dtype=float)
        d_speed = np.asarray(d_minus_dlognu_dt_s_inv, dtype=float)
        expected = self.tau_flrw.shape
        for name, value in (
            ("incoming", incoming),
            ("speed", speed),
            ("d_incoming", d_incoming),
            ("d_equilibrium_departure", d_equilibrium),
            ("d_tau_flrw", d_tau_flrw),
            ("d_frequency_speed", d_speed),
        ):
            if value.shape != expected or not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must match tau_flrw and be finite")
        tau = self.directional_optical_depth(minus_dlognu_dt_s_inv=speed)
        transmission = np.exp(-tau)
        absorbed = -np.expm1(-tau)
        d_tau = (
            self.H_s_inv / np.abs(speed) * d_tau_flrw
            + tau * float(d_H_s_inv) / self.H_s_inv
            - tau * d_speed / speed
        )
        result = (
            transmission * d_incoming
            + absorbed * d_equilibrium
            + (self.equilibrium_departure - incoming) * transmission * d_tau
        )
        return _readonly(result)


@dataclass(frozen=True)
class IsotropicEinsteinLineSource:
    """Positive paired one-photon source in the hydrogen rest frame."""

    A_ul_s_inv: float
    profile_Hz_inv: float
    frequency_Hz: float
    nH_m3: float
    upper_population: float
    lower_population: float
    upper_degeneracy: float
    lower_degeneracy: float

    def __post_init__(self) -> None:
        positive = (
            "A_ul_s_inv",
            "profile_Hz_inv",
            "frequency_Hz",
            "nH_m3",
            "upper_degeneracy",
            "lower_degeneracy",
        )
        nonnegative = ("upper_population", "lower_population")
        for name in positive:
            value = float(getattr(self, name))
            if not (math.isfinite(value) and value > 0.0):
                raise ValueError(f"{name} must be positive and finite")
            object.__setattr__(self, name, value)
        for name in nonnegative:
            value = float(getattr(self, name))
            if not (math.isfinite(value) and value >= 0.0):
                raise ValueError(f"{name} must be nonnegative and finite")
            object.__setattr__(self, name, value)

    @property
    def phase_space_prefactor_s_inv(self) -> float:
        return c**3 * self.nH_m3 / (8.0 * math.pi * self.frequency_Hz**2)

    @property
    def emission_s_inv(self) -> float:
        return (
            self.phase_space_prefactor_s_inv
            * self.A_ul_s_inv
            * self.profile_Hz_inv
            * self.upper_population
        )

    @property
    def absorption_s_inv(self) -> float:
        return (
            self.phase_space_prefactor_s_inv
            * self.A_ul_s_inv
            * self.profile_Hz_inv
            * (self.upper_degeneracy / self.lower_degeneracy)
            * self.lower_population
        )

    @property
    def affine_opacity_s_inv(self) -> float:
        """Net coefficient in ``df/dt = emission - affine_opacity*f``."""
        return self.absorption_s_inv - self.emission_s_inv

    def occupation_action(self, occupation: float) -> float:
        value = float(occupation)
        if not (math.isfinite(value) and value >= 0.0):
            raise ValueError("occupation must be nonnegative and finite")
        return self.emission_s_inv * (1.0 + value) - self.absorption_s_inv * value

    def directional_action(self, occupation: np.ndarray) -> np.ndarray:
        values = np.asarray(occupation, dtype=float)
        if not np.all(np.isfinite(values)) or np.any(values < 0.0):
            raise ValueError("directional occupation must be nonnegative and finite")
        return _readonly(
            self.emission_s_inv * (1.0 + values)
            - self.absorption_s_inv * values
        )

    def planck_null_residual(self, *, temperature_K: float) -> float:
        temperature = float(temperature_K)
        if not (math.isfinite(temperature) and temperature > 0.0):
            raise ValueError("temperature_K must be positive and finite")
        z = math.exp(-h * self.frequency_Hz / (k * temperature))
        return self.occupation_action(z / (1.0 - z))

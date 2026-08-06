"""Byte-locked original-HyRec effective rates and analytic interpolation JVPs.

The October-2012 source uses cgs lengths and eV temperatures.  Public rate
coefficients are converted to SI while ordinary rates remain in ``s^-1``.
The source variable ``DAlpha`` is deliberately renamed ``delta_alpha`` here:
it is ``Alpha(Tm,Tr)-Alpha(Tr,Tr)``, not a temperature derivative.

The interpolation is a direct transcription of
``hydrogen.c::interpolate_rates``.  Derivatives are analytic derivatives of the
same local four-point Lagrange polynomials with respect to ``ln(Tr)`` and
``Tm/Tr``; no spline or fitted replacement is introduced.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from io import StringIO
import math
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Sequence
import zipfile

import numpy as np

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    NVIRT,
    NSUBLYA,
    safe_extract_original_hyrec_archive,
)


ALPHA_TABLE_SHA256 = "c543c755d99ba8e999450dd5cb486a3ad88d26378da0ccc8363b10418e4832bd"
R2P2S_TABLE_SHA256 = "ce914f4b552ba55ba00f7916f36b0986f19adfdb638e5aefae91f7b2d05a8112"
TWO_PHOTON_TABLE_SHA256 = "93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9"

TR_MIN_EV = 0.004
TR_MAX_EV = 0.4
N_TR = 100
TM_OVER_TR_MIN = 0.1
TM_OVER_TR_MAX = 1.0
N_TM = 40
IONIZATION_ENERGY_EV = 13.598286071938324
LYMAN_ALPHA_ENERGY_EV = 10.198714553953742
L2S_1S_S_INV = 8.2206
SAHA_COEFFICIENT_CGS = 3.016103031869581e21
CM3_TO_M3 = 1.0e-6

_ALPHA_MEMBER = "HyRec/Alpha_inf.dat"
_R_MEMBER = "HyRec/R_inf.dat"
_TWO_PHOTON_MEMBER = "HyRec/two_photon_tables.dat"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _readonly(value: Sequence[float] | np.ndarray, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains nonfinite values")
    result = np.array(array, copy=True)
    result.setflags(write=False)
    return result


def _cubic_weights_and_derivative(fraction: float) -> tuple[np.ndarray, np.ndarray]:
    f = float(fraction)
    weights = np.asarray(
        [
            f * (f - 1.0) * (2.0 - f) / 6.0,
            (1.0 + f) * (1.0 - f) * (2.0 - f) / 2.0,
            (1.0 + f) * f * (2.0 - f) / 2.0,
            (1.0 + f) * f * (f - 1.0) / 6.0,
        ],
        dtype=float,
    )
    derivative = np.asarray(
        [
            (-3.0 * f * f + 6.0 * f - 2.0) / 6.0,
            (3.0 * f * f - 4.0 * f - 1.0) / 2.0,
            (-3.0 * f * f + 2.0 * f + 2.0) / 2.0,
            (3.0 * f * f - 1.0) / 6.0,
        ],
        dtype=float,
    )
    # These are exact polynomial identities up to roundoff and are useful
    # guards against a transcription error in the source cardinal basis.
    if abs(float(np.sum(weights)) - 1.0) > 8.0e-15:
        raise ArithmeticError("cubic cardinal weights lost partition of unity")
    if abs(float(np.sum(derivative))) > 8.0e-15:
        raise ArithmeticError("cubic cardinal derivative does not sum to zero")
    return weights, derivative



def _source_dot4(values: np.ndarray, weights: np.ndarray) -> float:
    """Four-term dot product in the explicit source evaluation order."""

    return float(
        values[0] * weights[0]
        + values[1] * weights[1]
        + values[2] * weights[2]
        + values[3] * weights[3]
    )


def _stencil(
    value: float,
    minimum: float,
    maximum: float,
    count: int,
) -> tuple[int, float, float]:
    if not math.isfinite(value) or value < minimum or value > maximum:
        raise ValueError(f"value {value!r} outside [{minimum},{maximum}]")
    spacing = (maximum - minimum) / (count - 1)
    index = math.floor((value - minimum) / spacing)
    index = max(1, min(count - 3, index))
    fraction = (value - minimum) / spacing - index
    return int(index), float(fraction), float(spacing)


@dataclass(frozen=True)
class PrimitiveRateSnapshot:
    """One SI-adapted evaluation of the original-HyRec primitive rate tables."""

    radiation_temperature_eV_rescaled: float
    matter_to_radiation_temperature_ratio: float
    fsR: float
    meR: float
    alpha_m3_s: np.ndarray
    alpha_equilibrium_m3_s: np.ndarray
    delta_alpha_m3_s: np.ndarray
    beta_s_inv: np.ndarray
    R_2p2s_s_inv: float
    A1s_s_inv: np.ndarray
    A2s_s_inv: np.ndarray
    A3s3d_s_inv: np.ndarray
    A4s4d_s_inv: np.ndarray
    d_alpha_d_log_Tr_m3_s: np.ndarray
    d_alpha_d_Tm_over_Tr_m3_s: np.ndarray
    d_alpha_equilibrium_d_log_Tr_m3_s: np.ndarray
    d_delta_alpha_d_log_Tr_m3_s: np.ndarray
    d_delta_alpha_d_Tm_over_Tr_m3_s: np.ndarray
    d_beta_d_log_Tr_s_inv: np.ndarray
    d_R_2p2s_d_log_Tr_s_inv: float
    source_hashes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "radiation_temperature_eV_rescaled",
            "matter_to_radiation_temperature_ratio",
            "fsR",
            "meR",
            "R_2p2s_s_inv",
            "d_R_2p2s_d_log_Tr_s_inv",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if self.radiation_temperature_eV_rescaled <= 0.0:
            raise ValueError("radiation temperature must be positive")
        if not TM_OVER_TR_MIN <= self.matter_to_radiation_temperature_ratio <= TM_OVER_TR_MAX:
            raise ValueError("matter/radiation temperature ratio is outside source table")
        if self.fsR <= 0.0 or self.meR <= 0.0:
            raise ValueError("fsR and meR must be positive")
        if self.R_2p2s_s_inv <= 0.0:
            raise ValueError("R_2p2s must be positive")

        two_shape = (2,)
        for name in (
            "alpha_m3_s",
            "alpha_equilibrium_m3_s",
            "delta_alpha_m3_s",
            "beta_s_inv",
            "d_alpha_d_log_Tr_m3_s",
            "d_alpha_d_Tm_over_Tr_m3_s",
            "d_alpha_equilibrium_d_log_Tr_m3_s",
            "d_delta_alpha_d_log_Tr_m3_s",
            "d_delta_alpha_d_Tm_over_Tr_m3_s",
            "d_beta_d_log_Tr_s_inv",
        ):
            object.__setattr__(self, name, _readonly(getattr(self, name), two_shape, name))
        for name in ("A1s_s_inv", "A2s_s_inv", "A3s3d_s_inv", "A4s4d_s_inv"):
            object.__setattr__(self, name, _readonly(getattr(self, name), (NVIRT,), name))
        if np.any(self.alpha_m3_s <= 0.0) or np.any(self.alpha_equilibrium_m3_s <= 0.0):
            raise ValueError("recombination coefficients must be positive")
        if np.any(self.beta_s_inv <= 0.0):
            raise ValueError("photoionization rates must be positive")
        if np.any(self.A1s_s_inv < 0.0) or np.any(self.A2s_s_inv < 0.0):
            raise ValueError("two-photon rates must be nonnegative")
        hashes = {str(k): str(v) for k, v in self.source_hashes.items()}
        if any(len(value) != 64 for value in hashes.values()):
            raise ValueError("source hashes must be SHA-256 hex strings")
        object.__setattr__(self, "source_hashes", MappingProxyType(hashes))

    @property
    def value_vector_si(self) -> np.ndarray:
        vector = np.concatenate(
            (
                self.alpha_m3_s,
                self.delta_alpha_m3_s,
                self.beta_s_inv,
                np.asarray([self.R_2p2s_s_inv]),
            )
        )
        vector.setflags(write=False)
        return vector

    @property
    def derivative_log_Tr_vector_si(self) -> np.ndarray:
        vector = np.concatenate(
            (
                self.d_alpha_d_log_Tr_m3_s,
                self.d_delta_alpha_d_log_Tr_m3_s,
                self.d_beta_d_log_Tr_s_inv,
                np.asarray([self.d_R_2p2s_d_log_Tr_s_inv]),
            )
        )
        vector.setflags(write=False)
        return vector

    @property
    def derivative_Tm_over_Tr_vector_si(self) -> np.ndarray:
        vector = np.concatenate(
            (
                self.d_alpha_d_Tm_over_Tr_m3_s,
                self.d_delta_alpha_d_Tm_over_Tr_m3_s,
                np.zeros(3),
            )
        )
        vector.setflags(write=False)
        return vector


@dataclass(frozen=True)
class OriginalHyRecPrimitiveRateTable:
    """Canonical October-2012 primitive rate tables in source ordering."""

    log_alpha: np.ndarray
    log_R2p2s: np.ndarray
    two_photon_rates_s_inv: np.ndarray
    source_hashes: Mapping[str, str]
    archive_path: Path
    delta_alpha_semantics: str = "alpha(Tm,Tr)-alpha(Tr,Tr); not a derivative"

    def __post_init__(self) -> None:
        object.__setattr__(self, "log_alpha", _readonly(self.log_alpha, (2, N_TM, N_TR), "log_alpha"))
        object.__setattr__(self, "log_R2p2s", _readonly(self.log_R2p2s, (N_TR,), "log_R2p2s"))
        object.__setattr__(
            self,
            "two_photon_rates_s_inv",
            _readonly(self.two_photon_rates_s_inv, (4, NVIRT), "two_photon_rates_s_inv"),
        )
        if not np.all(np.isfinite(self.log_alpha)) or not np.all(np.isfinite(self.log_R2p2s)):
            raise ValueError("rate tables contain nonfinite entries")
        if np.any(self.two_photon_rates_s_inv < 0.0):
            raise ValueError("two-photon table contains negative rates")
        archive = Path(self.archive_path)
        if not archive.is_file():
            raise FileNotFoundError(archive)
        object.__setattr__(self, "archive_path", archive)
        hashes = MappingProxyType({str(k): str(v) for k, v in self.source_hashes.items()})
        object.__setattr__(self, "source_hashes", hashes)

    @classmethod
    def from_archive(cls, path: str | Path) -> "OriginalHyRecPrimitiveRateTable":
        archive_path = Path(path)
        with zipfile.ZipFile(archive_path) as archive:
            alpha_bytes = archive.read(_ALPHA_MEMBER)
            r_bytes = archive.read(_R_MEMBER)
            two_bytes = archive.read(_TWO_PHOTON_MEMBER)
        hashes = {
            "Alpha_inf.dat": _sha256_bytes(alpha_bytes),
            "R_inf.dat": _sha256_bytes(r_bytes),
            "two_photon_tables.dat": _sha256_bytes(two_bytes),
        }
        expected = {
            "Alpha_inf.dat": ALPHA_TABLE_SHA256,
            "R_inf.dat": R2P2S_TABLE_SHA256,
            "two_photon_tables.dat": TWO_PHOTON_TABLE_SHA256,
        }
        if hashes != expected:
            raise ValueError(f"canonical original-HyRec rate-table hash mismatch: {hashes}")

        alpha_values = np.loadtxt(StringIO(alpha_bytes.decode("ascii")), dtype=float)
        if alpha_values.shape != (N_TR, N_TM * 2):
            # np.loadtxt sees each line as two values, yielding 4000x2 for the
            # canonical file.  Flattening preserves the exact fscanf order.
            if alpha_values.shape != (N_TR * N_TM, 2):
                raise ValueError(f"unexpected Alpha_inf.dat shape {alpha_values.shape}")
        alpha_flat = np.asarray(alpha_values, dtype=float).reshape(N_TR, N_TM, 2)
        log_alpha = np.log(alpha_flat).transpose(2, 1, 0)

        r_values = np.loadtxt(StringIO(r_bytes.decode("ascii")), dtype=float)
        if r_values.shape != (N_TR,):
            raise ValueError(f"unexpected R_inf.dat shape {r_values.shape}")
        log_r = np.log(r_values)

        two = np.loadtxt(StringIO(two_bytes.decode("ascii")), dtype=float)
        if two.shape != (NVIRT, 5):
            raise ValueError(f"unexpected two_photon_tables.dat shape {two.shape}")
        rates = two[:, 1:].T.copy()
        normalization = L2S_1S_S_INV / float(np.sum(rates[1, :NSUBLYA]))
        rates[1, :NSUBLYA] *= normalization
        return cls(
            log_alpha=log_alpha,
            log_R2p2s=log_r,
            two_photon_rates_s_inv=rates,
            source_hashes=hashes,
            archive_path=archive_path,
        )

    def extract_source_tree(self, destination: str | Path) -> Path:
        safe_extract_original_hyrec_archive(self.archive_path, destination)
        return Path(destination) / "HyRec"

    def evaluate(
        self,
        *,
        radiation_temperature_eV_rescaled: float,
        matter_to_radiation_temperature_ratio: float,
        fsR: float = 1.0,
        meR: float = 1.0,
    ) -> PrimitiveRateSnapshot:
        Tr = float(radiation_temperature_eV_rescaled)
        ratio = float(matter_to_radiation_temperature_ratio)
        fsR = float(fsR)
        meR = float(meR)
        if not math.isfinite(Tr) or Tr < TR_MIN_EV or Tr > TR_MAX_EV:
            raise ValueError("radiation temperature lies outside original-HyRec table")
        if not math.isfinite(ratio) or ratio < TM_OVER_TR_MIN or ratio > TM_OVER_TR_MAX:
            raise ValueError("Tm/Tr lies outside original-HyRec table")
        if not math.isfinite(fsR) or not math.isfinite(meR) or fsR <= 0.0 or meR <= 0.0:
            raise ValueError("fsR and meR must be positive")

        i_tm, f_tm, d_tm = _stencil(
            ratio, TM_OVER_TR_MIN, TM_OVER_TR_MAX, N_TM
        )
        log_tr = math.log(Tr)
        i_tr, f_tr, d_log_tr = _stencil(
            log_tr, math.log(TR_MIN_EV), math.log(TR_MAX_EV), N_TR
        )
        w_tm, dw_tm_df = _cubic_weights_and_derivative(f_tm)
        w_tr, dw_tr_df = _cubic_weights_and_derivative(f_tr)
        dw_tm = dw_tm_df / d_tm
        dw_tr = dw_tr_df / d_log_tr

        alpha_cgs = np.zeros(2)
        alpha_eq_cgs = np.zeros(2)
        d_alpha_logtr_cgs = np.zeros(2)
        d_alpha_ratio_cgs = np.zeros(2)
        d_alpha_eq_logtr_cgs = np.zeros(2)
        alpha_scale = (fsR / meR) ** 2

        for level in range(2):
            patch = self.log_alpha[level, i_tm - 1 : i_tm + 3, i_tr - 1 : i_tr + 3]
            temp = np.asarray([_source_dot4(patch[k], w_tr) for k in range(4)])
            log_value = _source_dot4(temp, w_tm)
            dlog_dratio = _source_dot4(temp, dw_tm)
            temp_log_derivative = np.asarray(
                [_source_dot4(patch[k], dw_tr) for k in range(4)]
            )
            dlog_dlogtr = _source_dot4(temp_log_derivative, w_tm)
            alpha_cgs[level] = alpha_scale * math.exp(log_value)
            d_alpha_ratio_cgs[level] = alpha_cgs[level] * dlog_dratio
            d_alpha_logtr_cgs[level] = alpha_cgs[level] * dlog_dlogtr

            equilibrium_stencil = self.log_alpha[level, N_TM - 1, i_tr - 1 : i_tr + 3]
            log_eq = _source_dot4(equilibrium_stencil, w_tr)
            dlog_eq = _source_dot4(equilibrium_stencil, dw_tr)
            alpha_eq_cgs[level] = alpha_scale * math.exp(log_eq)
            d_alpha_eq_logtr_cgs[level] = alpha_eq_cgs[level] * dlog_eq

        delta_alpha_cgs = alpha_cgs - alpha_eq_cgs
        d_delta_logtr_cgs = d_alpha_logtr_cgs - d_alpha_eq_logtr_cgs
        d_delta_ratio_cgs = d_alpha_ratio_cgs.copy()

        factor = (
            SAHA_COEFFICIENT_CGS
            * (fsR * meR) ** 3
            * Tr
            * math.sqrt(Tr)
            * math.exp(-0.25 * IONIZATION_ENERGY_EV / Tr)
        )
        beta = alpha_eq_cgs * factor
        beta[1] /= 3.0
        dlog_factor_dlogtr = 1.5 + 0.25 * IONIZATION_ENERGY_EV / Tr
        d_beta_logtr = beta * (
            d_alpha_eq_logtr_cgs / alpha_eq_cgs + dlog_factor_dlogtr
        )

        r_stencil = self.log_R2p2s[i_tr - 1 : i_tr + 3]
        log_r = _source_dot4(r_stencil, w_tr)
        dlog_r = _source_dot4(r_stencil, dw_tr)
        r_scale = fsR**5 * meR
        R = r_scale * math.exp(log_r)
        d_R_logtr = R * dlog_r

        two_scale = fsR**8 * meR
        A = self.two_photon_rates_s_inv * two_scale
        return PrimitiveRateSnapshot(
            radiation_temperature_eV_rescaled=Tr,
            matter_to_radiation_temperature_ratio=ratio,
            fsR=fsR,
            meR=meR,
            alpha_m3_s=alpha_cgs * CM3_TO_M3,
            alpha_equilibrium_m3_s=alpha_eq_cgs * CM3_TO_M3,
            delta_alpha_m3_s=delta_alpha_cgs * CM3_TO_M3,
            beta_s_inv=beta,
            R_2p2s_s_inv=R,
            A1s_s_inv=A[0],
            A2s_s_inv=A[1],
            A3s3d_s_inv=A[2],
            A4s4d_s_inv=A[3],
            d_alpha_d_log_Tr_m3_s=d_alpha_logtr_cgs * CM3_TO_M3,
            d_alpha_d_Tm_over_Tr_m3_s=d_alpha_ratio_cgs * CM3_TO_M3,
            d_alpha_equilibrium_d_log_Tr_m3_s=d_alpha_eq_logtr_cgs * CM3_TO_M3,
            d_delta_alpha_d_log_Tr_m3_s=d_delta_logtr_cgs * CM3_TO_M3,
            d_delta_alpha_d_Tm_over_Tr_m3_s=d_delta_ratio_cgs * CM3_TO_M3,
            d_beta_d_log_Tr_s_inv=d_beta_logtr,
            d_R_2p2s_d_log_Tr_s_inv=d_R_logtr,
            source_hashes=self.source_hashes,
        )

    def central_difference_jvp_residual(
        self,
        *,
        radiation_temperature_eV_rescaled: float,
        matter_to_radiation_temperature_ratio: float,
        direction_log_Tr_and_Tm_over_Tr: Sequence[float],
        step: float = 1.0e-6,
    ) -> float:
        direction = np.asarray(direction_log_Tr_and_Tm_over_Tr, dtype=float)
        if direction.shape != (2,) or not np.all(np.isfinite(direction)):
            raise ValueError("direction must have shape (2,) and be finite")
        if step <= 0.0:
            raise ValueError("step must be positive")
        Tr = float(radiation_temperature_eV_rescaled)
        ratio = float(matter_to_radiation_temperature_ratio)
        plus = self.evaluate(
            radiation_temperature_eV_rescaled=Tr * math.exp(step * direction[0]),
            matter_to_radiation_temperature_ratio=ratio + step * direction[1],
        ).value_vector_si
        minus = self.evaluate(
            radiation_temperature_eV_rescaled=Tr * math.exp(-step * direction[0]),
            matter_to_radiation_temperature_ratio=ratio - step * direction[1],
        ).value_vector_si
        finite_difference = (plus - minus) / (2.0 * step)
        centre = self.evaluate(
            radiation_temperature_eV_rescaled=Tr,
            matter_to_radiation_temperature_ratio=ratio,
        )
        analytic = (
            direction[0] * centre.derivative_log_Tr_vector_si
            + direction[1] * centre.derivative_Tm_over_Tr_vector_si
        )
        return float(
            np.max(np.abs(finite_difference - analytic))
            / max(
                float(np.max(np.abs(finite_difference))),
                float(np.max(np.abs(analytic))),
                1.0e-300,
            )
        )


def detailed_balance_residuals(
    rates: PrimitiveRateSnapshot,
    *,
    n_H_m3: float,
    x_1s: float,
) -> np.ndarray:
    """Return relative 2s/2p recombination-photoionization Saha residuals.

    At ``Tm=Tr``, ``n_H alpha_i x_e^2 = beta_i x_i`` with
    ``x_2s=x_1s exp(-E21/Tr)`` and
    ``x_2p=3 x_1s exp(-E21/Tr)``.  The electron Saha factor is converted from
    ``cm^-3`` to ``m^-3`` before multiplying the SI recombination coefficient.
    """

    n_H = float(n_H_m3)
    x1s = float(x_1s)
    if not math.isfinite(n_H) or n_H <= 0.0:
        raise ValueError("n_H_m3 must be positive")
    if not math.isfinite(x1s) or x1s <= 0.0:
        raise ValueError("x_1s must be positive")
    Tr = rates.radiation_temperature_eV_rescaled
    saha_m3 = (
        SAHA_COEFFICIENT_CGS
        * (rates.fsR * rates.meR) ** 3
        * 1.0e6
        * Tr
        * math.sqrt(Tr)
        * math.exp(-IONIZATION_ENERGY_EV / Tr)
    )
    xe_squared = saha_m3 * x1s / n_H
    excited = np.asarray(
        [x1s, 3.0 * x1s], dtype=float
    ) * math.exp(-LYMAN_ALPHA_ENERGY_EV / Tr)
    forward = n_H * rates.alpha_equilibrium_m3_s * xe_squared
    reverse = rates.beta_s_inv * excited
    return (forward - reverse) / np.maximum(
        np.maximum(np.abs(forward), np.abs(reverse)), 1.0e-300
    )

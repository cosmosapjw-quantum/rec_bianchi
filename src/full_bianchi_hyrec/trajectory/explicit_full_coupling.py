"""Explicit noncanonical closures for PR-05C2B thermodynamic coupling.

The October-2012 original-HyRec boundary state is scalar and therefore does not
identify a directional intensity.  This module exposes positive closures with
an explicit claim downgrade, a positivity-limited face reconstruction, and a
source-temperature collision-network family that reproduces the locked v0.50
network exactly at its reference node without a fitted global normalization.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.constants import c, h, k

from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (
    CollisionNetwork,
    LineBoundaryConfig,
)


@dataclass(frozen=True)
class NativeAngularClosure:
    occupation: np.ndarray
    monopole: float
    monopole_residual: float
    momentum_vector: np.ndarray
    reduced_flux: float
    minimum_occupation: float
    source_identical_directional_reconstruction: bool
    classification: str


@dataclass(frozen=True)
class FrequencyFaceReconstruction:
    left_trace: np.ndarray
    right_trace: np.ndarray
    minimum_trace: float
    creates_new_extrema: bool
    method: str


@dataclass(frozen=True)
class ThermodynamicNetworkMember:
    network: CollisionNetwork
    temperature_K: float
    nH_m3: float
    reference_limit_exact: bool
    no_fitted_normalization: bool
    source_identical_recompilation: bool
    classification: str


def _immutable(array: np.ndarray) -> np.ndarray:
    result = np.array(array, copy=True)
    result.setflags(write=False)
    return result


def _closure_result(
    occupation: np.ndarray,
    scalar_monopole: float,
    grid: HarmonicGrid,
    *,
    classification: str,
) -> NativeAngularClosure:
    values = np.asarray(occupation, dtype=float)
    if values.shape != (grid.n_angle,):
        raise ValueError("occupation must have one value per angular node")
    if np.any(values <= 0.0) or not np.all(np.isfinite(values)):
        raise ValueError("angular closure must be finite and strictly positive")
    monopole = float(np.sum(grid.weights * values))
    residual = abs(monopole - scalar_monopole) / max(abs(scalar_monopole), 1.0e-300)
    if residual < 8.0 * np.finfo(float).eps:
        residual = 0.0
    momentum = np.sum(
        grid.weights[:, None] * values[:, None] * grid.directions,
        axis=0,
    )
    reduced = float(np.linalg.norm(momentum) / max(abs(monopole), 1.0e-300))
    return NativeAngularClosure(
        occupation=_immutable(values),
        monopole=monopole,
        monopole_residual=residual,
        momentum_vector=_immutable(momentum),
        reduced_flux=reduced,
        minimum_occupation=float(np.min(values)),
        source_identical_directional_reconstruction=False,
        classification=classification,
    )


def isotropic_native_lift(
    scalar_occupation: float,
    grid: HarmonicGrid,
) -> NativeAngularClosure:
    """Positive isotropic lift of one scalar original-HyRec occupation."""

    scalar = float(scalar_occupation)
    if not math.isfinite(scalar) or scalar <= 0.0:
        raise ValueError("scalar_occupation must be positive and finite")
    return _closure_result(
        np.full(grid.n_angle, scalar),
        scalar,
        grid,
        classification="EXPLICIT_NONCANONICAL_ISOTROPIC_CLOSURE",
    )


def maximum_entropy_native_lift(
    scalar_occupation: float,
    grid: HarmonicGrid,
    *,
    axis: np.ndarray,
    reduced_flux: float,
    max_bisection: int = 160,
) -> NativeAngularClosure:
    """Positive discrete maximum-entropy lift with a prescribed reduced flux.

    The closure is ``f_a = C exp(lambda e_a.axis)``.  It is a declared model,
    not a reconstruction of missing original-HyRec angular data.
    """

    scalar = float(scalar_occupation)
    target = float(reduced_flux)
    direction = np.asarray(axis, dtype=float)
    if not math.isfinite(scalar) or scalar <= 0.0:
        raise ValueError("scalar_occupation must be positive and finite")
    if direction.shape != (3,) or not np.all(np.isfinite(direction)):
        raise ValueError("axis must be a finite three-vector")
    norm = float(np.linalg.norm(direction))
    if norm <= 0.0:
        raise ValueError("axis must be nonzero")
    direction = direction / norm
    if not math.isfinite(target) or target < 0.0 or target >= 1.0:
        raise ValueError("reduced_flux must lie in [0,1)")
    mu = grid.directions @ direction

    def mean_mu(value: float) -> float:
        exponent = value * mu
        exponent -= float(np.max(exponent))
        weights = grid.weights * np.exp(exponent)
        return float(np.sum(weights * mu) / np.sum(weights))

    maximum = mean_mu(80.0)
    if target > maximum + 1.0e-14:
        raise ValueError("requested reduced flux is not realizable on this grid")
    lower, upper = 0.0, 80.0
    for _ in range(max_bisection):
        middle = 0.5 * (lower + upper)
        if mean_mu(middle) < target:
            lower = middle
        else:
            upper = middle
    lam = 0.5 * (lower + upper)
    exponent = lam * mu
    exponent -= float(np.max(exponent))
    shape = np.exp(exponent)
    normalization = float(np.sum(grid.weights * shape))
    occupation = scalar * shape / normalization
    return _closure_result(
        occupation,
        scalar,
        grid,
        classification="EXPLICIT_NONCANONICAL_CLOSURE_UNCERTAINTY",
    )


def _minmod(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    same_sign = left * right > 0.0
    result = np.zeros_like(left)
    result[same_sign] = np.sign(left[same_sign]) * np.minimum(
        np.abs(left[same_sign]), np.abs(right[same_sign])
    )
    return result


def reconstruct_frequency_faces(
    cell_average: np.ndarray,
    cell_faces: np.ndarray,
    *,
    method: str = "p0",
) -> FrequencyFaceReconstruction:
    """Construct one-sided finite-volume traces at every frequency face."""

    values = np.asarray(cell_average, dtype=float)
    faces = np.asarray(cell_faces, dtype=float)
    if values.ndim != 1 or faces.shape != (len(values) + 1,):
        raise ValueError("cell_average/cell_faces shape mismatch")
    if np.any(np.diff(faces) <= 0.0) or not np.all(np.isfinite(values)):
        raise ValueError("faces must increase and values must be finite")
    if np.any(values <= 0.0):
        raise ValueError("positive occupation reconstruction requires positive cells")
    centers = 0.5 * (faces[:-1] + faces[1:])
    left_trace = np.empty(len(faces), dtype=float)
    right_trace = np.empty(len(faces), dtype=float)

    if method == "p0":
        left_trace[0] = values[0]
        left_trace[1:] = values
        right_trace[:-1] = values
        right_trace[-1] = values[-1]
    elif method == "muscl":
        slope = np.zeros_like(values)
        if len(values) > 1:
            slope[0] = (values[1] - values[0]) / (centers[1] - centers[0])
            slope[-1] = (values[-1] - values[-2]) / (centers[-1] - centers[-2])
        if len(values) > 2:
            backward = (values[1:-1] - values[:-2]) / (
                centers[1:-1] - centers[:-2]
            )
            forward = (values[2:] - values[1:-1]) / (
                centers[2:] - centers[1:-1]
            )
            slope[1:-1] = _minmod(backward, forward)
        cell_left = values - slope * (centers - faces[:-1])
        cell_right = values + slope * (faces[1:] - centers)
        # Enforce local maximum principle and positivity explicitly.
        for index in range(len(values)):
            lo = max(index - 1, 0)
            hi = min(index + 2, len(values))
            lower = float(np.min(values[lo:hi]))
            upper = float(np.max(values[lo:hi]))
            cell_left[index] = np.clip(cell_left[index], lower, upper)
            cell_right[index] = np.clip(cell_right[index], lower, upper)
        left_trace[0] = cell_left[0]
        left_trace[1:-1] = cell_right[:-1]
        left_trace[-1] = cell_right[-1]
        right_trace[0] = cell_left[0]
        right_trace[1:-1] = cell_left[1:]
        right_trace[-1] = cell_right[-1]
    else:
        raise ValueError("method must be 'p0' or 'muscl'")

    creates = False
    for face in range(1, len(faces) - 1):
        lower = min(values[face - 1], values[face])
        upper = max(values[face - 1], values[face])
        if (
            left_trace[face] < lower - 1.0e-14
            or left_trace[face] > upper + 1.0e-14
            or right_trace[face] < lower - 1.0e-14
            or right_trace[face] > upper + 1.0e-14
        ):
            creates = True
            break
    return FrequencyFaceReconstruction(
        left_trace=_immutable(left_trace),
        right_trace=_immutable(right_trace),
        minimum_trace=float(min(np.min(left_trace), np.min(right_trace))),
        creates_new_extrema=creates,
        method=method,
    )


class ExplicitThermodynamicNetworkFamily:
    """Positive source-temperature closure anchored to the locked v0.50 node."""

    def __init__(
        self,
        reference: CollisionNetwork,
        *,
        reference_temperature_K: float = 3000.0,
        reference_nH_m3: float = 2.5e8,
    ) -> None:
        self.reference = reference
        self.reference_temperature_K = float(reference_temperature_K)
        self.reference_nH_m3 = float(reference_nH_m3)
        if self.reference_temperature_K <= 0.0 or self.reference_nH_m3 <= 0.0:
            raise ValueError("reference temperature and density must be positive")
        intervals = reference.state_intervals
        self._x_red = float(np.min(intervals[:, 0]))
        self._x_blue = float(np.max(intervals[:, 1]))
        ref_line = LineBoundaryConfig.lyman_alpha(
            temperature_K=self.reference_temperature_K,
            x_red=self._x_red,
            x_blue=self._x_blue,
        )
        mode, centroid, activity = self._analytic_measures(
            self.reference_temperature_K, ref_line
        )
        self._mode_calibration = reference.mode_measure / mode
        self._activity_calibration = reference.activity_weight / activity
        self._reference_centroid = centroid

    def _analytic_measures(
        self,
        temperature_K: float,
        line: LineBoundaryConfig,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        intervals = self.reference.state_intervals
        lower = line.nu_abs_Hz + intervals[:, 0] * line.Doppler_width_Hz
        upper = line.nu_abs_Hz + intervals[:, 1] * line.Doppler_width_Hz
        mode = 8.0 * math.pi * (upper**3 - lower**3) / (3.0 * c**3)
        centroid = 0.75 * (upper**4 - lower**4) / (upper**3 - lower**3)
        activity = np.exp(-h * centroid / (k * temperature_K))
        return mode, centroid, activity

    def compile(self, *, temperature_K: float, nH_m3: float) -> ThermodynamicNetworkMember:
        temperature = float(temperature_K)
        density = float(nH_m3)
        if temperature <= 0.0 or density <= 0.0 or not math.isfinite(temperature + density):
            raise ValueError("temperature_K and nH_m3 must be positive and finite")
        if temperature == self.reference_temperature_K and density == self.reference_nH_m3:
            return ThermodynamicNetworkMember(
                network=self.reference,
                temperature_K=temperature,
                nH_m3=density,
                reference_limit_exact=True,
                no_fitted_normalization=True,
                source_identical_recompilation=False,
                classification="LOCKED_V050_REFERENCE_LIMIT",
            )

        line = LineBoundaryConfig.lyman_alpha(
            temperature_K=temperature,
            x_red=self._x_red,
            x_blue=self._x_blue,
        )
        analytic_mode, centroid, analytic_activity = self._analytic_measures(
            temperature, line
        )
        mode = analytic_mode * self._mode_calibration
        activity = analytic_activity * self._activity_calibration
        equilibrium = mode * activity

        # Explicit positive conductance closure.  The density/thermal factor is
        # source-derived; endpoint equilibrium factors preserve reciprocity and
        # the exact locked reference node.  This is not a direct COM--KHW
        # recompilation and is therefore reported with an uncertainty ledger.
        global_scale = (
            density / self.reference_nH_m3
        ) * math.sqrt(self.reference_temperature_K / temperature)
        endpoint = np.sqrt(equilibrium / self.reference.equilibrium_weight)
        pair = (
            self.reference.pair_moments
            * global_scale
            * endpoint[None, :, None]
            * endpoint[None, None, :]
        )
        # Copy one triangle explicitly so reciprocity is bitwise, not merely
        # within a floating-point tolerance.
        for ell in range(pair.shape[0]):
            upper = np.triu(pair[ell])
            pair[ell] = upper + np.triu(pair[ell], 1).T
        same = self.reference.same_cell_rates * global_scale
        momentum = h * centroid / c
        network = CollisionNetwork(
            state_intervals=self.reference.state_intervals,
            state_labels=self.reference.state_labels,
            pair_moments=pair,
            same_cell_rates=same,
            mode_measure=mode,
            equilibrium_weight=equilibrium,
            momentum_scale=momentum,
            inherited_release_policy=self.reference.inherited_release_policy,
        )
        return ThermodynamicNetworkMember(
            network=network,
            temperature_K=temperature,
            nH_m3=density,
            reference_limit_exact=False,
            no_fitted_normalization=True,
            source_identical_recompilation=False,
            classification="EXPLICIT_THERMODYNAMIC_CONDUCTANCE_CLOSURE",
        )


__all__ = [
    "ExplicitThermodynamicNetworkFamily",
    "FrequencyFaceReconstruction",
    "NativeAngularClosure",
    "ThermodynamicNetworkMember",
    "isotropic_native_lift",
    "maximum_entropy_native_lift",
    "reconstruct_frequency_faces",
]

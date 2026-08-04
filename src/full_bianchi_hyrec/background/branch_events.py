"""Event-localized red/blue boundary flux on piecewise-linear speeds."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BoundaryLedger:
    red_roots: np.ndarray
    blue_roots: np.ndarray
    red_flux: float
    blue_flux: float
    delta_interior: float
    delta_red: float
    delta_blue: float
    number_residual: float
    four_momentum_residual: np.ndarray
    total_absolute_flux: float


def _validated_series(times, values, name):
    t = np.asarray(times, dtype=float)
    y = np.asarray(values, dtype=float)
    if t.ndim != 1 or y.shape != t.shape or len(t) < 2:
        raise ValueError(f"{name} must be a one-dimensional series matching times")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(y)):
        raise ValueError("times and values must be finite")
    if np.any(np.diff(t) <= 0.0):
        raise ValueError("times must be strictly increasing")
    return t, y


def piecewise_linear_roots(times, values, tol=1e-14):
    t, y = _validated_series(times, values, "values")
    roots = []
    for left_t, right_t, left_y, right_y in zip(t[:-1], t[1:], y[:-1], y[1:]):
        if abs(left_y) <= tol:
            roots.append(float(left_t))
        if left_y * right_y < 0.0:
            fraction = -left_y / (right_y - left_y)
            roots.append(float(left_t + fraction * (right_t - left_t)))
    if abs(y[-1]) <= tol:
        roots.append(float(t[-1]))
    clean = []
    for value in roots:
        if not clean or abs(value - clean[-1]) > tol * max(1.0, abs(value)):
            clean.append(value)
    return np.asarray(clean)


def _positive_linear_integral(y0, y1, duration):
    if y0 >= 0.0 and y1 >= 0.0:
        return 0.5 * duration * (y0 + y1)
    if y0 <= 0.0 and y1 <= 0.0:
        return 0.0
    fraction = -y0 / (y1 - y0)
    if y0 > 0.0:
        return 0.5 * duration * fraction * y0
    return 0.5 * duration * (1.0 - fraction) * y1


def _signed_boundary_integrals(times, speed):
    t, a = _validated_series(times, speed, "speed")
    positive = 0.0
    negative = 0.0
    for index in range(len(t) - 1):
        duration = t[index + 1] - t[index]
        positive += _positive_linear_integral(a[index], a[index + 1], duration)
        negative += _positive_linear_integral(-a[index], -a[index + 1], duration)
    return positive, negative


def boundary_ledger(
    times,
    red_speed,
    blue_speed,
    *,
    interior_occupation,
    red_occupation,
    blue_occupation,
    red_photon_four,
    blue_photon_four,
):
    t, red = _validated_series(times, red_speed, "red_speed")
    _, blue = _validated_series(times, blue_speed, "blue_speed")
    red_positive, red_negative = _signed_boundary_integrals(t, red)
    blue_positive, blue_negative = _signed_boundary_integrals(t, blue)

    # D1C convention: red outflow for a<0; blue outflow for a>0.
    flux_red = (
        red_negative * float(interior_occupation)
        - red_positive * float(red_occupation)
    )
    flux_blue = (
        blue_positive * float(interior_occupation)
        - blue_negative * float(blue_occupation)
    )
    delta_red = flux_red
    delta_blue = flux_blue
    delta_interior = -(flux_red + flux_blue)
    number_residual = delta_interior + delta_red + delta_blue

    p_red = np.asarray(red_photon_four, dtype=float)
    p_blue = np.asarray(blue_photon_four, dtype=float)
    if p_red.shape != (4,) or p_blue.shape != (4,):
        raise ValueError("photon four-vectors must have shape (4,)")
    delta_P_interior = -flux_red * p_red - flux_blue * p_blue
    delta_P_red = flux_red * p_red
    delta_P_blue = flux_blue * p_blue
    four_residual = delta_P_interior + delta_P_red + delta_P_blue

    return BoundaryLedger(
        red_roots=piecewise_linear_roots(t, red),
        blue_roots=piecewise_linear_roots(t, blue),
        red_flux=float(flux_red),
        blue_flux=float(flux_blue),
        delta_interior=float(delta_interior),
        delta_red=float(delta_red),
        delta_blue=float(delta_blue),
        number_residual=float(number_residual),
        four_momentum_residual=four_residual,
        total_absolute_flux=float(
            red_positive + red_negative + blue_positive + blue_negative
        ),
    )

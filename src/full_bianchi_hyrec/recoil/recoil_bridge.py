"""Audit the bridge between microscopic recoil and v0.33.

The v0.33 kernel is a square-root thermodynamic completion of a
symmetric finite-volume Hummer proposal.  It is deliberately distinct
from an exact recoil event.  This module quantifies that distinction.
"""
from __future__ import annotations

from functools import lru_cache
import math
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.special import erf, wofz

from full_bianchi_hyrec.artifacts import (
    V032_LEGENDRE_KERNEL,
    V033_COMPLETED_KERNEL,
)

_DEFAULT_V032 = V032_LEGENDRE_KERNEL
_DEFAULT_V033 = V033_COMPLETED_KERNEL


def rayleigh_phase(mu: np.ndarray | float) -> np.ndarray | float:
    return 0.375 * (1.0 + np.asarray(mu) ** 2)


def exact_rayleigh_recoil_moments(
    g: float,
    b_d: float,
    *,
    angular_order: int = 256,
) -> dict[str, float]:
    """Angular moments of the exact atom-rest recoil shift.

    delta x = -g(1-mu)/(1+g b_D (1-mu)).
    """
    if g <= 0.0 or b_d <= 0.0:
        raise ValueError("g and b_d must be positive")
    nodes, weights = leggauss(angular_order)
    shift = -g * (1.0 - nodes) / (
        1.0 + g * b_d * (1.0 - nodes)
    )
    phase_weight = weights * rayleigh_phase(nodes)
    return {
        "normalization": float(np.sum(phase_weight)),
        "mean_delta_x": float(np.sum(phase_weight * shift)),
        "second_delta_x": float(np.sum(phase_weight * shift**2)),
        "third_delta_x": float(np.sum(phase_weight * shift**3)),
    }


def load_v033_line_center(
    path: str | Path = _DEFAULT_V033,
) -> dict[str, float]:
    data = np.load(Path(path))
    x = np.asarray(data["x_centers"], dtype=float)
    rate = np.asarray(data["completed_rate_sInv"], dtype=float)[0]
    g = float(data["recoil_parameter_g"])
    b_d = float(data["phase_space_parameter_b"])
    line = int(np.argmin(np.abs(x)))
    delta = x[:, None] - x[None, :]
    loss = rate.sum(axis=0)
    a1 = np.sum(rate * delta, axis=0)
    a2 = np.sum(rate * delta**2, axis=0)
    return {
        "line_index": line,
        "x_center": float(x[line]),
        "g": g,
        "b_D": b_d,
        "opacity_sInv": float(loss[line]),
        "A1_x_sInv": float(a1[line]),
        "A2_x2_sInv": float(a2[line]),
        "M1_per_scattering": float(a1[line] / loss[line]),
        "M2_per_scattering": float(a2[line] / loss[line]),
    }


def classify_v033_bridge(
    v033: dict[str, float],
    exact_moments: dict[str, float],
) -> dict[str, float | str]:
    microscopic = exact_moments["mean_delta_x"]
    closure = v033["M1_per_scattering"]
    mismatch = abs(closure - microscopic) / abs(microscopic)
    return {
        "classification": (
            "GATE_INVALID_FOR_EXACT_EVENT"
            if mismatch > 1.0e-6
            else "BRIDGE_PASSES"
        ),
        "microscopic_mean_recoil": microscopic,
        "v033_mean_drift": closure,
        "relative_mismatch": float(mismatch),
        "v033_square_root_prediction": float(
            (v033["b_D"] - v033["g"])
            * v033["M2_per_scattering"]
        ),
    }


def _h_over_c(u: np.ndarray, c_value: float, a_damp: float) -> np.ndarray:
    if c_value < 1.0e-8:
        return a_damp / (
            math.sqrt(math.pi) * (u * u + a_damp * a_damp)
        )
    return np.real(wofz((u + 1j * a_damp) / c_value)) / c_value


def _gaussian_integrals(
    v_min: np.ndarray,
    v_max: np.ndarray,
    s_value: float,
    n_max: int,
) -> list[np.ndarray]:
    z_min = v_min / s_value
    z_max = v_max / s_value
    exp_min = np.exp(-z_min * z_min)
    exp_max = np.exp(-z_max * z_max)

    integrals: list[np.ndarray] = [np.empty_like(v_min) for _ in range(n_max + 1)]
    integrals[0] = (
        0.5
        * s_value
        * math.sqrt(math.pi)
        * (erf(z_max) - erf(z_min))
    )
    integrals[1] = 0.5 * s_value**2 * (exp_min - exp_max)

    for order in range(2, n_max + 1):
        boundary = (
            v_max ** (order - 1) * exp_max
            - v_min ** (order - 1) * exp_min
        )
        integrals[order] = (
            -0.5 * s_value**2 * boundary
            + 0.5
            * s_value**2
            * (order - 1)
            * integrals[order - 2]
        )
    return integrals


def _oriented_cell_moments(
    *,
    target: int,
    source: int,
    mu: float,
    x_edges: np.ndarray,
    u_nodes: np.ndarray,
    u_weights: np.ndarray,
    a_damp: float,
    g: float,
    b_d: float,
    recoil: bool,
    exact_denominator: bool,
    phase_space: bool,
    max_moment: int = 2,
) -> np.ndarray:
    x_t_lo, x_t_hi = x_edges[target], x_edges[target + 1]
    x_s_lo, x_s_hi = x_edges[source], x_edges[source + 1]
    cell_width = x_s_hi - x_s_lo

    s_value = math.sqrt(max(0.0, (1.0 - mu) / 2.0))
    c_value = math.sqrt(max(0.0, (1.0 + mu) / 2.0))

    recoil_shift = 0.0
    if recoil:
        recoil_shift = g * (1.0 - mu)
        if exact_denominator:
            recoil_shift /= 1.0 + g * b_d * (1.0 - mu)

    if phase_space:
        source_measure = (
            (1.0 + b_d * x_s_hi) ** 3
            - (1.0 + b_d * x_s_lo) ** 3
        ) / (3.0 * b_d)
    else:
        source_measure = cell_width

    if s_value < 1.0e-11:
        values = np.zeros(max_moment + 1)
        if target != source:
            return values
        nodes, weights = leggauss(160)
        x_values = (
            0.5 * (x_s_hi + x_s_lo)
            + 0.5 * cell_width * nodes
        )
        mode = (1.0 + b_d * x_values) ** 2 if phase_space else 1.0
        profile = np.real(wofz(x_values + 1j * a_damp)) / math.sqrt(math.pi)
        values[0] = float(
            np.sum(0.5 * cell_width * weights * mode * profile)
            / source_measure
        )
        return values

    u_min = 0.5 * (x_t_lo + recoil_shift + x_s_lo)
    u_max = 0.5 * (x_t_hi + recoil_shift + x_s_hi)
    breakpoints = [
        u_min,
        u_max,
        0.5 * (x_t_lo + recoil_shift + x_s_hi),
        0.5 * (x_t_hi + recoil_shift + x_s_lo),
        0.0,
    ]
    breakpoints = sorted(
        set(
            round(float(value), 15)
            for value in breakpoints
            if u_min - 1.0e-14 <= value <= u_max + 1.0e-14
        )
    )

    totals = np.zeros(max_moment + 1)
    for left, right in zip(breakpoints[:-1], breakpoints[1:]):
        if right - left < 1.0e-14:
            continue
        midpoint = 0.5 * (left + right)
        halfwidth = 0.5 * (right - left)
        u_values = midpoint + halfwidth * u_nodes
        weights = halfwidth * u_weights

        v_min = np.maximum(
            x_t_lo + recoil_shift - u_values,
            u_values - x_s_hi,
        )
        v_max = np.minimum(
            x_t_hi + recoil_shift - u_values,
            u_values - x_s_lo,
        )
        active = v_max > v_min
        if not np.any(active):
            continue

        u_active = u_values[active]
        w_active = weights[active]
        integrals = _gaussian_integrals(
            v_min[active], v_max[active], s_value, max_moment + 2
        )

        if phase_space:
            p0 = (1.0 + b_d * (u_active - recoil_shift)) * (
                1.0 + b_d * u_active
            )
            p1 = np.full_like(u_active, b_d**2 * recoil_shift)
            p2 = np.full_like(u_active, -b_d**2)
        else:
            p0 = np.ones_like(u_active)
            p1 = np.zeros_like(u_active)
            p2 = np.zeros_like(u_active)

        prefactor = _h_over_c(u_active, c_value, a_damp) / (
            math.pi * s_value
        )

        for moment in range(max_moment + 1):
            shift_polynomial = np.polynomial.polynomial.polypow(
                np.asarray([-recoil_shift, 2.0]), moment
            )
            integrated = np.zeros_like(u_active)
            for power, coefficient in enumerate(shift_polynomial):
                integrated += coefficient * (
                    p0 * integrals[power]
                    + p1 * integrals[power + 1]
                    + p2 * integrals[power + 2]
                )
            totals[moment] += float(
                np.sum(w_active * prefactor * integrated) / source_measure
            )

    return totals


def _integrate_kernel(
    *,
    x_edges: np.ndarray,
    a_damp: float,
    rate_scale: float,
    g: float,
    b_d: float,
    recoil: bool,
    exact_denominator: bool,
    phase_space: bool,
    back_order: int,
    middle_order: int,
    forward_order: int,
    u_order: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n_frequency = len(x_edges) - 1
    u_nodes, u_weights = leggauss(u_order)
    moments = np.zeros((3, n_frequency, n_frequency))

    def add_mu(mu: float, measure_weight: float) -> None:
        phase = 0.75 * (1.0 + mu * mu)
        for target in range(n_frequency):
            for source in range(n_frequency):
                moments[:, target, source] += (
                    measure_weight
                    * phase
                    * _oriented_cell_moments(
                        target=target,
                        source=source,
                        mu=mu,
                        x_edges=x_edges,
                        u_nodes=u_nodes,
                        u_weights=u_weights,
                        a_damp=a_damp,
                        g=g,
                        b_d=b_d,
                        recoil=recoil,
                        exact_denominator=exact_denominator,
                        phase_space=phase_space,
                        max_moment=2,
                    )
                )

    mu_back = -0.99
    mu_forward = 0.999

    nodes, weights = leggauss(back_order)
    c_max = math.sqrt((1.0 + mu_back) / 2.0)
    c_values = 0.5 * c_max * (nodes + 1.0)
    c_weights = 0.5 * c_max * weights
    for c_value, weight in zip(c_values, c_weights):
        mu = -1.0 + 2.0 * c_value**2
        add_mu(float(mu), float(2.0 * c_value * weight))

    nodes, weights = leggauss(middle_order)
    mu_values = (
        0.5 * (mu_forward - mu_back) * nodes
        + 0.5 * (mu_forward + mu_back)
    )
    mu_weights = 0.5 * (mu_forward - mu_back) * weights
    for mu, weight in zip(mu_values, mu_weights):
        add_mu(float(mu), float(0.5 * weight))

    nodes, weights = leggauss(forward_order)
    t_max = math.sqrt(1.0 - mu_forward)
    t_values = 0.5 * t_max * (nodes + 1.0)
    t_weights = 0.5 * t_max * weights
    for t_value, weight in zip(t_values, t_weights):
        mu = 1.0 - t_value**2
        add_mu(float(mu), float(t_value * weight))

    return tuple(rate_scale * moments[index] for index in range(3))


@lru_cache(maxsize=16)
def compute_bridge_audit(
    *,
    back_order: int = 12,
    middle_order: int = 80,
    forward_order: int = 20,
    u_order: int = 48,
    v032_path: str | Path = _DEFAULT_V032,
    v033_path: str | Path = _DEFAULT_V033,
) -> dict[str, float | str]:
    v032 = np.load(Path(v032_path))
    v033 = np.load(Path(v033_path))

    x_edges = np.asarray(v032["x_edges"], dtype=float)
    x_centers = np.asarray(v032["x_centers"], dtype=float)
    base_reference = np.asarray(v032["physical_gain_sInv"], dtype=float)[0]
    completed_reference = np.asarray(v033["completed_rate_sInv"], dtype=float)[0]
    equilibrium_weight = np.asarray(v033["dilute_equilibrium_weight_m3"], dtype=float)
    a_damp = float(v032["damping_a"])
    rate_scale = float(v032["rate_scale_sInv"])
    g = float(v033["recoil_parameter_g"])
    b_d = float(v033["phase_space_parameter_b"])

    baseline, _, _ = _integrate_kernel(
        x_edges=x_edges,
        a_damp=a_damp,
        rate_scale=rate_scale,
        g=0.0,
        b_d=0.0,
        recoil=False,
        exact_denominator=False,
        phase_space=False,
        back_order=back_order,
        middle_order=middle_order,
        forward_order=forward_order,
        u_order=u_order,
    )
    shifted, continuous_a1, continuous_a2 = _integrate_kernel(
        x_edges=x_edges,
        a_damp=a_damp,
        rate_scale=rate_scale,
        g=g,
        b_d=b_d,
        recoil=True,
        exact_denominator=True,
        phase_space=True,
        back_order=back_order,
        middle_order=middle_order,
        forward_order=forward_order,
        u_order=u_order,
    )

    line = int(np.argmin(np.abs(x_centers)))
    delta = x_centers[:, None] - x_centers[None, :]
    shifted_loss = shifted.sum(axis=0)
    shifted_cell_a1 = np.sum(shifted * delta, axis=0)
    shifted_cell_a2 = np.sum(shifted * delta**2, axis=0)

    completed_loss = completed_reference.sum(axis=0)
    completed_a1 = np.sum(completed_reference * delta, axis=0)
    completed_a2 = np.sum(completed_reference * delta**2, axis=0)

    balance = (
        shifted * equilibrium_weight[None, :]
        - shifted.T * equilibrium_weight[:, None]
    )
    balance_scale = np.max(
        np.abs(shifted * equilibrium_weight[None, :])
    )

    exact_moments = exact_rayleigh_recoil_moments(g, b_d)
    shift_mean = continuous_a1[:, line].sum() / shifted_loss[line]
    shift_second = continuous_a2[:, line].sum() / shifted_loss[line]
    v033_mean = completed_a1[line] / completed_loss[line]

    return {
        "classification": "SHIFT_ONLY_AUDIT_NOT_PRODUCTION",
        "line_index": line,
        "no_recoil_vs_v032_relative": float(
            np.linalg.norm(baseline - base_reference)
            / np.linalg.norm(base_reference)
        ),
        "shift_only_pair_balance_relative": float(
            np.max(np.abs(balance)) / (balance_scale + 1.0e-300)
        ),
        "shift_only_continuous_M1": float(shift_mean),
        "shift_only_continuous_M2": float(shift_second),
        "shift_only_cell_center_M1": float(
            shifted_cell_a1[line] / shifted_loss[line]
        ),
        "shift_only_cell_center_M2": float(
            shifted_cell_a2[line] / shifted_loss[line]
        ),
        "exact_rest_event_mean_recoil": float(
            exact_moments["mean_delta_x"]
        ),
        "v033_M1": float(v033_mean),
        "v033_M2": float(completed_a2[line] / completed_loss[line]),
        "shift_only_vs_v033_drift_relative": float(
            abs(shift_mean - v033_mean) / abs(shift_mean)
        ),
    }


@lru_cache(maxsize=32)
def compute_line_bridge_audit(
    *,
    back_order: int = 24,
    middle_order: int = 180,
    forward_order: int = 36,
    u_order: int = 96,
    v032_path: str | Path = _DEFAULT_V032,
    v033_path: str | Path = _DEFAULT_V033,
) -> dict[str, float | str]:
    """High-order line-centre audit without constructing the whole matrix."""
    v032 = np.load(Path(v032_path))
    v033 = np.load(Path(v033_path))

    x_edges = np.asarray(v032["x_edges"], dtype=float)
    x_centers = np.asarray(v032["x_centers"], dtype=float)
    base_reference = np.asarray(v032["physical_gain_sInv"], dtype=float)[0]
    completed_reference = np.asarray(v033["completed_rate_sInv"], dtype=float)[0]
    equilibrium_weight = np.asarray(v033["dilute_equilibrium_weight_m3"], dtype=float)
    a_damp = float(v032["damping_a"])
    rate_scale = float(v032["rate_scale_sInv"])
    g = float(v033["recoil_parameter_g"])
    b_d = float(v033["phase_space_parameter_b"])
    line = int(np.argmin(np.abs(x_centers)))
    n_frequency = len(x_centers)
    u_nodes, u_weights = leggauss(u_order)

    baseline_column = np.zeros(n_frequency)
    shifted_column = np.zeros(n_frequency)
    shifted_row = np.zeros(n_frequency)
    continuous_a1_column = np.zeros(n_frequency)
    continuous_a2_column = np.zeros(n_frequency)

    def add_mu(mu: float, measure_weight: float) -> None:
        phase = 0.75 * (1.0 + mu * mu)
        for target in range(n_frequency):
            baseline = _oriented_cell_moments(
                target=target,
                source=line,
                mu=mu,
                x_edges=x_edges,
                u_nodes=u_nodes,
                u_weights=u_weights,
                a_damp=a_damp,
                g=0.0,
                b_d=0.0,
                recoil=False,
                exact_denominator=False,
                phase_space=False,
                max_moment=0,
            )[0]
            forward = _oriented_cell_moments(
                target=target,
                source=line,
                mu=mu,
                x_edges=x_edges,
                u_nodes=u_nodes,
                u_weights=u_weights,
                a_damp=a_damp,
                g=g,
                b_d=b_d,
                recoil=True,
                exact_denominator=True,
                phase_space=True,
                max_moment=2,
            )
            reverse = _oriented_cell_moments(
                target=line,
                source=target,
                mu=mu,
                x_edges=x_edges,
                u_nodes=u_nodes,
                u_weights=u_weights,
                a_damp=a_damp,
                g=g,
                b_d=b_d,
                recoil=True,
                exact_denominator=True,
                phase_space=True,
                max_moment=0,
            )[0]

            prefactor = measure_weight * phase * rate_scale
            baseline_column[target] += prefactor * baseline
            shifted_column[target] += prefactor * forward[0]
            shifted_row[target] += prefactor * reverse
            continuous_a1_column[target] += prefactor * forward[1]
            continuous_a2_column[target] += prefactor * forward[2]

    mu_back = -0.99
    mu_forward = 0.999

    nodes, weights = leggauss(back_order)
    c_max = math.sqrt((1.0 + mu_back) / 2.0)
    for c_value, weight in zip(
        0.5 * c_max * (nodes + 1.0),
        0.5 * c_max * weights,
    ):
        add_mu(
            float(-1.0 + 2.0 * c_value**2),
            float(2.0 * c_value * weight),
        )

    nodes, weights = leggauss(middle_order)
    for mu, weight in zip(
        0.5 * (mu_forward - mu_back) * nodes
        + 0.5 * (mu_forward + mu_back),
        0.5 * (mu_forward - mu_back) * weights,
    ):
        add_mu(float(mu), float(0.5 * weight))

    nodes, weights = leggauss(forward_order)
    t_max = math.sqrt(1.0 - mu_forward)
    for t_value, weight in zip(
        0.5 * t_max * (nodes + 1.0),
        0.5 * t_max * weights,
    ):
        add_mu(
            float(1.0 - t_value**2),
            float(t_value * weight),
        )

    delta = x_centers - x_centers[line]
    shifted_loss = float(shifted_column.sum())
    cell_a1 = float(np.dot(shifted_column, delta))
    cell_a2 = float(np.dot(shifted_column, delta**2))
    continuous_a1 = float(continuous_a1_column.sum())
    continuous_a2 = float(continuous_a2_column.sum())

    completed_loss = float(completed_reference[:, line].sum())
    completed_a1 = float(np.dot(completed_reference[:, line], delta))
    completed_a2 = float(np.dot(completed_reference[:, line], delta**2))

    pair_lhs = shifted_column * equilibrium_weight[line]
    pair_rhs = shifted_row * equilibrium_weight
    pair_balance = float(
        np.max(np.abs(pair_lhs - pair_rhs))
        / (np.max(np.abs(pair_lhs)) + 1.0e-300)
    )

    return {
        "classification": "SHIFT_ONLY_LINE_AUDIT_NOT_PRODUCTION",
        "line_index": line,
        "no_recoil_line_column_vs_v032_relative": float(
            np.linalg.norm(baseline_column - base_reference[:, line])
            / np.linalg.norm(base_reference[:, line])
        ),
        "shift_only_pair_balance_relative": pair_balance,
        "shift_only_opacity_sInv": shifted_loss,
        "shift_only_continuous_M1": continuous_a1 / shifted_loss,
        "shift_only_continuous_M2": continuous_a2 / shifted_loss,
        "shift_only_cell_center_M1": cell_a1 / shifted_loss,
        "shift_only_cell_center_M2": cell_a2 / shifted_loss,
        "v033_M1": completed_a1 / completed_loss,
        "v033_M2": completed_a2 / completed_loss,
        "shift_only_vs_v033_drift_relative": float(
            abs(continuous_a1 / shifted_loss - completed_a1 / completed_loss)
            / abs(continuous_a1 / shifted_loss)
        ),
    }

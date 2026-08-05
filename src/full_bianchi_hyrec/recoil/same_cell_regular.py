"""Regularized same-frequency-cell angular redistribution.

The coherent-forward contribution is distributional in the raw gain
kernel.  In the collision action it appears only through

    K_ell(i,i) - K_0(i,i),

because P_ell(1)=1.  This module integrates that finite remainder
directly; it never constructs or subtracts two separately divergent
numbers.
"""
from __future__ import annotations

from functools import lru_cache
import math
from pathlib import Path

import numpy as np
from scipy.special import eval_legendre

from . import pair_cell_conductance as PCC


PRODUCTION_LANE = {
    "ob": 20,
    "om": 144,
    "of": 40,
    "nu": 32,
    "nu_pole": 80,
    "ny": 36,
    "ymax": 9.0,
}
REFERENCE_LANE = {
    "ob": 24,
    "om": 192,
    "of": 52,
    "nu": 40,
    "nu_pole": 104,
    "ny": 48,
    "ymax": 10.0,
}

# The complete-minus-provisional amplitude correction is a smooth,
# subdominant lane.  The narrow 2p pole itself is inherited from the
# durable v0.47 same-cell block, so this correction needs fewer nodes.
DELTA_PRODUCTION_LANE = {
    "ob": 12,
    "om": 64,
    "of": 18,
    "nu": 20,
    "nu_pole": 56,
    "ny": 24,
    "ymax": 9.0,
}
DELTA_REFERENCE_LANE = {
    "ob": 18,
    "om": 96,
    "of": 28,
    "nu": 28,
    "nu_pole": 80,
    "ny": 32,
    "ymax": 10.0,
}


def _data_path(name: str) -> Path:
    return Path(__file__).resolve().parents[3] / "data" / name


def _u_rule(cell: int, regular_order: int, pole_order: int):
    """Frequency-mean coordinate with a tangent split at the line pole."""
    left = float(PCC.xedges[cell])
    right = float(PCC.xedges[cell + 1])
    pole_scale = PCC.gamma / PCC.dnu
    local_half = min(0.08, 0.45 * (right - left))

    breakpoints = [left, right]
    if left < 0.0 < right:
        breakpoints += [max(left, -local_half), 0.0, min(right, local_half)]
    breakpoints = sorted(set(round(value, 15) for value in breakpoints))

    values: list[float] = []
    weights_out: list[float] = []
    for a, b in zip(breakpoints[:-1], breakpoints[1:]):
        if b - a < 1.0e-14:
            continue
        tangent = left < 0.0 < right and abs(a) <= local_half + 1e-14 and abs(b) <= local_half + 1e-14
        if tangent:
            nodes, weights = PCC.leggauss(pole_order)
            ta = math.atan(a / pole_scale)
            tb = math.atan(b / pole_scale)
            theta = 0.5 * (tb - ta) * nodes + 0.5 * (tb + ta)
            u = pole_scale * np.tan(theta)
            w = 0.5 * (tb - ta) * weights * pole_scale / np.cos(theta) ** 2
        else:
            nodes, weights = PCC.leggauss(regular_order)
            u = 0.5 * (b - a) * nodes + 0.5 * (b + a)
            w = 0.5 * (b - a) * weights
        values.extend(u.tolist())
        weights_out.extend(w.tolist())
    return np.asarray(values), np.asarray(weights_out)


def _same_cell_frequency_integral(
    cell: int,
    mu: float,
    *,
    kind: str,
    lane_parameters: dict[str, float | int],
    amplitude_lane: str = "full",
) -> float:
    """Two-cell integral using v=s*y, resolving the forward Gaussian layer."""
    s = math.sqrt(max(0.0, (1.0 - mu) / 2.0))
    if s == 0.0:
        # The regularized angular multiplier vanishes at this point, so this
        # value is never used in an integral.
        return 0.0

    left = float(PCC.xedges[cell])
    right = float(PCC.xedges[cell + 1])
    u_values, u_weights = _u_rule(
        cell,
        int(lane_parameters["nu"]),
        int(lane_parameters["nu_pole"]),
    )
    y_nodes, y_weights = PCC.leggauss(int(lane_parameters["ny"]))
    y_max_global = float(lane_parameters["ymax"])

    result = 0.0
    for u, wu in zip(u_values, u_weights):
        half_width = min(u - left, right - u)
        if half_width <= 0.0:
            continue
        y_max = min(y_max_global, half_width / s)
        if y_max <= 0.0:
            continue
        y = y_max * y_nodes
        wy = y_max * y_weights
        v = s * y
        x_target = u + v
        x_source = u - v
        nu_source = PCC.nu_abs + x_source * PCC.dnu
        nu_target = PCC.nu_abs + x_target * PCC.dnu

        boltzmann_exact = np.exp(
            -PCC.beta * PCC.h * nu_source
            + PCC.logSmj(nu_source, nu_target, mu)
        ) * nu_source * nu_target

        if kind == "exact":
            weighted = (
                PCC.const_exact
                * boltzmann_exact
                * PCC.exact_amp2(
                    nu_source,
                    nu_target,
                    mu,
                    amplitude_lane=amplitude_lane,
                )
            )
        elif kind == "amplitude_delta":
            weighted = (
                PCC.const_exact
                * boltzmann_exact
                * PCC.exact_amp2(
                    nu_source,
                    nu_target,
                    mu,
                    amplitude_lane="full_minus_provisional",
                )
            )
        elif kind in {"hummer", "correction"}:
            hummer_values = (
                np.exp(
                    -PCC.beta * PCC.h * nu_source
                    + PCC.logSmb_hummer(x_source, x_target, mu)
                )
                * nu_source**2
                * PCC.baseline_amp2(x_source, x_target, mu)
            )
            if kind == "hummer":
                weighted = PCC.const_base * hummer_values
            else:
                exact_values = boltzmann_exact * PCC.exact_amp2(
                    nu_source,
                    nu_target,
                    mu,
                    amplitude_lane=amplitude_lane,
                )
                weighted = (
                    PCC.const_exact * exact_values
                    - PCC.const_base * hummer_values
                )
        else:
            raise ValueError(
                "kind must be 'exact', 'hummer', 'correction', or "
                "'amplitude_delta'"
            )

        # dx_t dx_s = 2 du dv = 2 s du dy.
        result += 2.0 * s * wu * float(np.dot(wy, weighted))

    return result


def _angular_vector(mu: float, ell_max: int) -> np.ndarray:
    return np.asarray([eval_legendre(ell, mu) - 1.0 for ell in range(ell_max + 1)])


@lru_cache(maxsize=512)
def _integrate_same_cell_regularized_internal(
    cell: int,
    *,
    lane: str = "production",
    kind: str = "exact",
    ell_max: int = 24,
    amplitude_lane: str = "full",
) -> np.ndarray:
    """Return S_ell(i,i)-S_0(i,i) through ell_max.

    Units are the normalized conductance units used internally by
    ``pair_cell_conductance`` before the common photon-mode factor
    ``8*pi*DeltaNu_D/c^3`` is applied.
    """
    if not 0 <= cell < PCC.ncell:
        raise ValueError("cell outside the 17-cell core")
    if ell_max < 0:
        raise ValueError("ell_max must be nonnegative")
    if lane not in {"production", "reference"}:
        raise ValueError("lane must be 'production' or 'reference'")
    if kind == "amplitude_delta":
        parameters = (
            DELTA_PRODUCTION_LANE
            if lane == "production"
            else DELTA_REFERENCE_LANE
        )
    else:
        parameters = PRODUCTION_LANE if lane == "production" else REFERENCE_LANE
    total = np.zeros(ell_max + 1)

    # Backscattering endpoint: mu=-1+2c^2, (1/2)dmu=2c dc.
    nodes, weights = PCC.leggauss(int(parameters["ob"]))
    c_max = math.sqrt(0.005)
    c_values = 0.5 * c_max * (nodes + 1.0)
    c_weights = 0.5 * c_max * weights
    for c_value, weight in zip(c_values, c_weights):
        mu = -1.0 + 2.0 * c_value**2
        frequency = _same_cell_frequency_integral(
            cell, mu, kind=kind, lane_parameters=parameters,
            amplitude_lane=amplitude_lane,
        )
        phase = 0.75 * (1.0 + mu**2)
        total += 2.0 * c_value * weight * phase * _angular_vector(mu, ell_max) * frequency

    # Regular middle interval, including the exact 1/2 angular measure.
    nodes, weights = PCC.leggauss(int(parameters["om"]))
    a, b = -0.99, 0.999
    mus = 0.5 * (b - a) * nodes + 0.5 * (b + a)
    mweights = 0.25 * (b - a) * weights
    for mu, weight in zip(mus, mweights):
        frequency = _same_cell_frequency_integral(
            cell, float(mu), kind=kind, lane_parameters=parameters,
            amplitude_lane=amplitude_lane,
        )
        phase = 0.75 * (1.0 + mu**2)
        total += weight * phase * _angular_vector(float(mu), ell_max) * frequency

    # Coherent-forward endpoint: mu=1-t^2, (1/2)|dmu|=t dt.
    nodes, weights = PCC.leggauss(int(parameters["of"]))
    t_max = math.sqrt(0.001)
    t_values = 0.5 * t_max * (nodes + 1.0)
    t_weights = 0.5 * t_max * weights
    for t, weight in zip(t_values, t_weights):
        mu = 1.0 - t**2
        frequency = _same_cell_frequency_integral(
            cell, mu, kind=kind, lane_parameters=parameters,
            amplitude_lane=amplitude_lane,
        )
        phase = 0.75 * (1.0 + mu**2)
        total += t * weight * phase * _angular_vector(mu, ell_max) * frequency

    # P_0-1 is analytically zero. Avoid a numerical signed-zero floor.
    total[0] = 0.0
    return total


@lru_cache(maxsize=1)
def _locked_provisional_same_cell_rates() -> np.ndarray:
    """Durable v0.47 provisional same-cell rates through ell=24."""
    data = np.load(_data_path("far_scalar_release_v047.npz"))
    values = np.asarray(data["same_cell_rates_sInv"][:, : PCC.ncell], dtype=float)
    if values.shape[0] < 25 or values.shape[1] != PCC.ncell:
        raise ValueError("v0.47 same-cell block has an unexpected shape")
    values = values.copy()
    values.setflags(write=False)
    return values


@lru_cache(maxsize=512)
def integrate_same_cell_regularized(
    cell: int,
    *,
    lane: str = "production",
    kind: str = "exact",
    ell_max: int = 24,
    amplitude_lane: str = "full",
) -> np.ndarray:
    """Return the physical same-cell collision remainder in s^-1.

    For the exact provisional 2p kernel, use the v0.32 Hummer block as
    a common-measure control variate and integrate only the exact-minus-
    Hummer correction.  This removes the coherent-forward distribution
    before numerical quadrature.
    """
    if ell_max > 24:
        raise ValueError("durable provisional same-cell block ends at ell=24")
    reference = np.load(_data_path("hummer_same_cell_reference.npz"))
    hummer_gain = np.asarray(reference["physical_gain_sInv"])
    if ell_max >= hummer_gain.shape[0]:
        raise ValueError("Hummer reference does not contain requested ell")
    baseline = (
        hummer_gain[: ell_max + 1, cell, cell]
        - hummer_gain[0, cell, cell]
    ).copy()
    baseline[0] = 0.0
    if kind == "hummer":
        return baseline
    if kind != "exact":
        raise ValueError("public kind must be 'exact' or 'hummer'")
    if amplitude_lane not in {"full", "provisional_2p", "provisional"}:
        raise ValueError(
            "amplitude_lane must be 'full' or 'provisional_2p'"
        )

    provisional = _locked_provisional_same_cell_rates()[
        : ell_max + 1, cell
    ].copy()
    if amplitude_lane in {"provisional_2p", "provisional"}:
        provisional[0] = 0.0
        return provisional

    correction_internal = _integrate_same_cell_regularized_internal(
        cell,
        lane=lane,
        kind="amplitude_delta",
        ell_max=ell_max,
        amplitude_lane="full",
    )
    pi = PCC.physical_equilibrium_cell_weight(cell)
    common_mode_factor = 8.0 * math.pi * PCC.dnu / PCC.c**3
    correction_rate = common_mode_factor * correction_internal / pi
    result = provisional + correction_rate
    result[0] = 0.0
    return result


def integrate_hummer_same_cell_audit(
    cell: int, *, lane: str = "reference", ell_max: int = 12
) -> np.ndarray:
    """Independent numerical Hummer same-cell integral in physical rates."""
    raw = _integrate_same_cell_regularized_internal(
        cell, lane=lane, kind="hummer", ell_max=ell_max
    )
    pi = PCC.physical_equilibrium_cell_weight(cell)
    return (8.0 * math.pi * PCC.dnu / PCC.c**3) * raw / pi


def assemble_from_same_cell_rates(
    same_cell_rate_sInv: np.ndarray,
) -> dict[str, np.ndarray]:
    """Pure algebraic assembly from a precomputed regularized diagonal."""
    same_cell_rate_sInv = np.asarray(same_cell_rate_sInv, dtype=float)
    ell_count, cell_count = same_cell_rate_sInv.shape
    if cell_count != PCC.ncell or ell_count > 7:
        raise ValueError("shape must be (ell_count<=7, 17)")
    data = np.load(_data_path("offdiagonal_pair_conductance.npz"))
    rates = np.asarray(data["rates_sInv"][:ell_count]).copy()
    pi = np.asarray(data["equilibrium_weight_m3"])
    scalar_outflow = rates[0].sum(axis=0)
    matrices = rates.copy()
    for ell in range(ell_count):
        np.fill_diagonal(
            matrices[ell],
            same_cell_rate_sInv[ell] - scalar_outflow,
        )
    return {
        "collision_matrices_sInv": matrices,
        "same_cell_regularized_rate_sInv": same_cell_rate_sInv,
        "same_cell_regularized_conductance_m3_sInv": same_cell_rate_sInv * pi[None, :],
        "equilibrium_weight_m3": pi,
        "offdiagonal_scalar_outflow_sInv": scalar_outflow,
    }


@lru_cache(maxsize=8)
def assemble_bounded_harmonic_operator(
    *, ell_max: int = 6, lane: str = "production", amplitude_lane: str = "full"
) -> dict[str, np.ndarray]:
    """Combine v0.44 off-diagonal pairs with regularized same-cell action."""
    if ell_max > 6:
        raise ValueError("the inherited off-diagonal artifact is locked only through ell=6")
    same_cell = np.zeros((ell_max + 1, PCC.ncell))
    for cell in range(PCC.ncell):
        same_cell[:, cell] = integrate_same_cell_regularized(
            cell, lane=lane, kind="exact", ell_max=ell_max,
            amplitude_lane=amplitude_lane,
        )
    return assemble_from_same_cell_rates(same_cell)

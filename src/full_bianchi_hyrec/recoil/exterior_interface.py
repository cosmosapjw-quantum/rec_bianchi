"""Near-exterior resonant-scattering interface for the Ly-alpha core.

The interior science core is ``x in [-4.25, 4.25]``.  The first dynamic
near-exterior state follows the validated v0.22 adaptive wing grid out to
``|x| = 10.25``.  This module computes only interior--exterior unordered
pair conductances.  It deliberately does not add exterior--exterior or
far-wing physics.

Metric signature is (-,+,+,+).  Pair conductances are equilibrium-weighted
and are symmetric before generator assembly.
"""
from __future__ import annotations

from functools import lru_cache
import math
from typing import Iterable

import numpy as np
from scipy.special import eval_legendre

from . import pair_cell_conductance as PCC


RED_EDGES = np.asarray([-10.25, -8.25, -7.0, -6.0, -5.25, -4.75, -4.25])
BLUE_EDGES = -RED_EDGES[::-1]
RED_CELLS = tuple(
    (float(left), float(right))
    for left, right in zip(RED_EDGES[:-1], RED_EDGES[1:])
)
BLUE_CELLS = tuple(
    (float(left), float(right))
    for left, right in zip(BLUE_EDGES[:-1], BLUE_EDGES[1:])
)
EXTERIOR_CELLS = RED_CELLS + BLUE_CELLS


LANES = {
    "coarse": {
        "ob": 10,
        "om": 48,
        "of": 14,
        "nb": 16,
        "nl": 44,
        "nv": 16,
        "nf": 12,
    },
    "production": {
        "ob": 18,
        "om": 112,
        "of": 28,
        "nb": 28,
        "nl": 80,
        "nv": 26,
        "nf": 20,
    },
    "reference": {
        "ob": 28,
        "om": 176,
        "of": 44,
        "nb": 42,
        "nl": 120,
        "nv": 38,
        "nf": 30,
    },
}


def _validate_interval(interval: tuple[float, float]) -> tuple[float, float]:
    left, right = map(float, interval)
    if not np.isfinite(left) or not np.isfinite(right) or right <= left:
        raise ValueError("interval must be finite and ordered")
    if PCC.nu_abs + left * PCC.dnu <= 0.0:
        raise ValueError("frequency interval must remain positive")
    return left, right


def _interval_nodes(interval: tuple[float, float], order: int):
    left, right = _validate_interval(interval)
    nodes, weights = PCC.leggauss(order)
    return (
        0.5 * (right - left) * nodes + 0.5 * (right + left),
        0.5 * (right - left) * weights,
    )


def physical_equilibrium_interval_weight(
    left: float,
    right: float,
    *,
    order: int = 96,
) -> float:
    """Dilute isotropic equilibrium photon mode density in m^-3."""
    x, weights = _interval_nodes((left, right), order)
    nu = PCC.nu_abs + x * PCC.dnu
    integral = float(np.dot(weights, nu**2 * np.exp(-PCC.beta * PCC.h * nu)))
    return 8.0 * math.pi * PCC.dnu / PCC.c**3 * integral


def _uv_frequency_integral(
    target: tuple[float, float],
    source: tuple[float, float],
    mu: float,
    *,
    nb: int,
    nl: int,
    nv: int,
    local_half: float = 0.08,
    include_moments: bool = False,
):
    """Two-interval u-v integral with a tangent split at the line pole."""
    target_left, target_right = _validate_interval(target)
    source_left, source_right = _validate_interval(source)
    u_min = 0.5 * (target_left + source_left)
    u_max = 0.5 * (target_right + source_right)
    pole_scale = PCC.gamma / PCC.dnu

    breakpoints = [
        u_min,
        u_max,
        0.5 * (target_left + source_right),
        0.5 * (target_right + source_left),
    ]
    if u_min < 0.0 < u_max:
        width = min(local_half, 0.45 * (u_max - u_min))
        breakpoints += [max(u_min, -width), 0.0, min(u_max, width)]
    breakpoints = sorted(
        set(
            round(float(value), 15)
            for value in breakpoints
            if u_min - 1.0e-14 <= value <= u_max + 1.0e-14
        )
    )

    u_nodes: list[float] = []
    u_weights: list[float] = []
    for left, right in zip(breakpoints[:-1], breakpoints[1:]):
        if right - left < 1.0e-14:
            continue
        tangent = (
            u_min < 0.0 < u_max
            and abs(left) <= local_half + 1.0e-14
            and abs(right) <= local_half + 1.0e-14
        )
        if tangent:
            nodes, weights = PCC.leggauss(nl)
            theta_left = math.atan(left / pole_scale)
            theta_right = math.atan(right / pole_scale)
            theta = (
                0.5 * (theta_right - theta_left) * nodes
                + 0.5 * (theta_right + theta_left)
            )
            values = pole_scale * np.tan(theta)
            transformed = (
                0.5
                * (theta_right - theta_left)
                * weights
                * pole_scale
                / np.cos(theta) ** 2
            )
        else:
            nodes, weights = PCC.leggauss(nb)
            values = 0.5 * (right - left) * nodes + 0.5 * (right + left)
            transformed = 0.5 * (right - left) * weights
        u_nodes.extend(values.tolist())
        u_weights.extend(transformed.tolist())

    v_nodes, v_weights = PCC.leggauss(nv)
    scalar = 0.0
    moment = np.zeros(2)
    for u_value, u_weight in zip(u_nodes, u_weights):
        v_min = max(target_left - u_value, u_value - source_right)
        v_max = min(target_right - u_value, u_value - source_left)
        if v_max <= v_min:
            continue
        v = 0.5 * (v_max - v_min) * v_nodes + 0.5 * (v_max + v_min)
        weights = 0.5 * (v_max - v_min) * v_weights
        x_target = u_value + v
        x_source = u_value - v
        nu_source = PCC.nu_abs + x_source * PCC.dnu
        nu_target = PCC.nu_abs + x_target * PCC.dnu
        density = (
            PCC.const_exact
            * np.exp(
                -PCC.beta * PCC.h * nu_source
                + PCC.logSmj(nu_source, nu_target, mu)
            )
            * nu_source
            * nu_target
            * PCC.exact_amp2(nu_source, nu_target, mu)
        )
        scalar += 2.0 * u_weight * float(np.dot(weights, density))
        if include_moments:
            delta_p0 = PCC.h / PCC.c * (nu_target - nu_source)
            delta_parallel = PCC.h / PCC.c * (nu_target * mu - nu_source)
            moment[0] += 2.0 * u_weight * float(
                np.dot(weights, density * delta_p0)
            )
            moment[1] += 2.0 * u_weight * float(
                np.dot(weights, density * delta_parallel)
            )
    return (scalar, moment) if include_moments else scalar


def _tensor_frequency_integral(
    target: tuple[float, float],
    source: tuple[float, float],
    mu: float,
    *,
    order: int,
    include_moments: bool = False,
):
    x_source_1d, source_weights = _interval_nodes(source, order)
    x_target_1d, target_weights = _interval_nodes(target, order)
    x_source = np.broadcast_to(x_source_1d, (order, order))
    x_target = np.broadcast_to(x_target_1d[:, None], (order, order))
    weights = target_weights[:, None] * source_weights[None, :]
    nu_source = PCC.nu_abs + x_source * PCC.dnu
    nu_target = PCC.nu_abs + x_target * PCC.dnu
    density = (
        PCC.const_exact
        * np.exp(
            -PCC.beta * PCC.h * nu_source
            + PCC.logSmj(nu_source, nu_target, mu)
        )
        * nu_source
        * nu_target
        * PCC.exact_amp2(nu_source, nu_target, mu)
    )
    scalar = float(np.sum(weights * density))
    if not include_moments:
        return scalar
    delta_p0 = PCC.h / PCC.c * (nu_target - nu_source)
    delta_parallel = PCC.h / PCC.c * (nu_target * mu - nu_source)
    return scalar, np.asarray(
        [
            float(np.sum(weights * density * delta_p0)),
            float(np.sum(weights * density * delta_parallel)),
        ]
    )


def _crosses_resonance_mean(
    target: tuple[float, float], source: tuple[float, float]
) -> bool:
    u_min = 0.5 * (target[0] + source[0])
    u_max = 0.5 * (target[1] + source[1])
    return u_min < 0.0 < u_max


def _touching_intervals(
    target: tuple[float, float], source: tuple[float, float]
) -> bool:
    return abs(target[1] - source[0]) < 1.0e-14 or abs(source[1] - target[0]) < 1.0e-14


def _integrate_pair(
    target: tuple[float, float],
    source: tuple[float, float],
    *,
    lane: str,
    ell_max: int,
    include_moments: bool,
):
    if lane not in LANES:
        raise ValueError(f"unknown lane: {lane}")
    target = _validate_interval(target)
    source = _validate_interval(source)
    if max(target[0], source[0]) < min(target[1], source[1]):
        raise ValueError("pair intervals must not overlap")
    parameters = LANES[lane]
    total = np.zeros(ell_max + 1)
    pair_moment = np.zeros(2)

    def accumulate(mu: float, angular_weight: float, *, force_uv: bool = False):
        nonlocal total, pair_moment
        use_uv = force_uv or _crosses_resonance_mean(target, source) or (
            mu > 0.995 and _touching_intervals(target, source)
        )
        if use_uv:
            result = _uv_frequency_integral(
                target,
                source,
                mu,
                nb=int(parameters["nb"]),
                nl=int(parameters["nl"]),
                nv=int(parameters["nv"]),
                include_moments=include_moments,
            )
        else:
            result = _tensor_frequency_integral(
                target,
                source,
                mu,
                order=int(parameters["nf"]),
                include_moments=include_moments,
            )
        if include_moments:
            scalar, moment = result
        else:
            scalar = result
            moment = None
        phase = 0.75 * (1.0 + mu**2)
        total += (
            angular_weight
            * phase
            * np.asarray([eval_legendre(ell, mu) for ell in range(ell_max + 1)])
            * scalar
        )
        if moment is not None:
            pair_moment += angular_weight * phase * moment

    nodes, weights = PCC.leggauss(int(parameters["ob"]))
    c_max = math.sqrt(0.005)
    c_values = 0.5 * c_max * (nodes + 1.0)
    c_weights = 0.5 * c_max * weights
    for c_value, weight in zip(c_values, c_weights):
        mu = -1.0 + 2.0 * c_value**2
        accumulate(float(mu), float(2.0 * c_value * weight), force_uv=True)

    nodes, weights = PCC.leggauss(int(parameters["om"]))
    lower, upper = -0.99, 0.999
    mus = 0.5 * (upper - lower) * nodes + 0.5 * (upper + lower)
    mweights = 0.25 * (upper - lower) * weights
    for mu, weight in zip(mus, mweights):
        accumulate(float(mu), float(weight))

    nodes, weights = PCC.leggauss(int(parameters["of"]))
    t_max = math.sqrt(0.001)
    t_values = 0.5 * t_max * (nodes + 1.0)
    t_weights = 0.5 * t_max * weights
    for t_value, weight in zip(t_values, t_weights):
        mu = 1.0 - t_value**2
        accumulate(float(mu), float(t_value * weight))

    return total, pair_moment


@lru_cache(maxsize=1024)
def exterior_pair_bundle(
    target: tuple[float, float],
    source: tuple[float, float],
    *,
    lane: str = "production",
    ell_max: int = 24,
) -> tuple[np.ndarray, np.ndarray]:
    """Conductance and axisymmetric same-event transfer for one pair."""
    conductance, transfer = _integrate_pair(
        target, source, lane=lane, ell_max=ell_max, include_moments=True
    )
    common_mode_factor = 8.0 * math.pi * PCC.dnu / PCC.c**3
    return common_mode_factor * conductance, common_mode_factor * transfer


@lru_cache(maxsize=1024)
def exterior_pair_conductance(
    target: tuple[float, float],
    source: tuple[float, float],
    *,
    lane: str = "production",
    ell_max: int = 24,
) -> np.ndarray:
    """Unordered equilibrium conductance for a disjoint interval pair."""
    total, _ = _integrate_pair(
        target, source, lane=lane, ell_max=ell_max, include_moments=False
    )
    return (8.0 * math.pi * PCC.dnu / PCC.c**3) * total


@lru_cache(maxsize=512)
def same_event_four_force_coefficients(
    target: tuple[float, float],
    source: tuple[float, float],
    *,
    lane: str = "production",
) -> tuple[np.ndarray, np.ndarray]:
    """Axisymmetric conductance-weighted photon/atom transfer coefficients.

    Components are ``(Delta p^0, Delta p_parallel)`` in SI momentum units
    times the equilibrium conductance.  The parallel direction is the source
    photon direction after azimuthal averaging.
    """
    _, photon = exterior_pair_bundle(
        target, source, lane=lane, ell_max=0
    )
    return photon, -photon


def assemble_scalar_interface_generator(
    conductance: np.ndarray,
    *,
    interior_pi: np.ndarray,
    exterior_pi: np.ndarray,
) -> np.ndarray:
    """Build a scalar generator containing only interior--exterior edges.

    ``conductance[e, i]`` is one unordered equilibrium conductance between
    exterior state ``e`` and interior state ``i``.  The returned state order
    is ``[interior..., exterior...]``.
    """
    conductance = np.asarray(conductance, dtype=float)
    interior_pi = np.asarray(interior_pi, dtype=float)
    exterior_pi = np.asarray(exterior_pi, dtype=float)
    if conductance.shape != (len(exterior_pi), len(interior_pi)):
        raise ValueError("conductance shape does not match state weights")
    if np.any(conductance < 0.0) or np.any(interior_pi <= 0.0) or np.any(exterior_pi <= 0.0):
        raise ValueError("conductances must be nonnegative and weights positive")

    n_int = len(interior_pi)
    n_ext = len(exterior_pi)
    generator = np.zeros((n_int + n_ext, n_int + n_ext))
    for exterior in range(n_ext):
        e_index = n_int + exterior
        for interior in range(n_int):
            value = conductance[exterior, interior]
            generator[e_index, interior] += value / interior_pi[interior]
            generator[interior, e_index] += value / exterior_pi[exterior]
    np.fill_diagonal(generator, -generator.sum(axis=0))
    return generator


def interior_cells() -> tuple[tuple[float, float], ...]:
    return tuple(
        (float(left), float(right))
        for left, right in zip(PCC.xedges[:-1], PCC.xedges[1:])
    )

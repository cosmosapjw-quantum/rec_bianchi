"""Executable lemmas for the PR-05C2C0 mathematical/physical closure.

The routines in this module are deliberately small.  They are not a second
production solver; they encode the structural identities that every direct
thermodynamic COM--KHW compiler, characteristic angular lift, face
reconstruction, and stiff preconditioner must preserve.

Conventions
-----------
* metric signature ``(-,+,+,+)``;
* ordinary frequency in Hz;
* occupations and the activity weights ``z`` are dimensionless;
* pair conductance has the units carried by the number-rate equation;
* ``c``, ``h`` and ``k_B`` are not set to one in production formulae.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class EntropyMetricGraph:
    """Linearized reversible edge graph in entropy variables.

    ``laplacian`` is positive semidefinite and annihilates the constant
    activity mode. ``entropy_mass`` is the positive diagonal coefficient
    multiplying the entropy-variable time derivative,
    ``m_A f_A^*(1+f_A^*)``.
    """

    laplacian: np.ndarray
    entropy_mass: np.ndarray


@dataclass(frozen=True)
class LimitedLinearTraces:
    """Cell-local conservative linear traces after one common slope scaling."""

    left: np.ndarray
    right: np.ndarray
    slope: np.ndarray
    limiter: np.ndarray


def _finite_nonnegative(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return result


def be_occupation(z: float, activity: float) -> float:
    """Return ``f=q z/(1-q z)`` on the Bose--Einstein activity family."""

    weight = _finite_nonnegative(z, "z")
    q = _finite_nonnegative(activity, "activity")
    product = q * weight
    if product >= 1.0:
        raise ValueError("Bose activity requires q*z < 1")
    return product / (1.0 - product)


def bose_edge_flux(
    f_i: float,
    f_j: float,
    *,
    zi: float,
    zj: float,
    conductance: float,
) -> float:
    """Number flux into edge endpoint ``i`` from endpoint ``j``.

    The reverse endpoint receives the negative of this value when the same
    symmetric conductance is used.  The exact factorization is

    ``K (1+f_i)(1+f_j) (phi_j-phi_i)``, with
    ``phi=f/[z(1+f)]``.
    """

    fi = _finite_nonnegative(f_i, "f_i")
    fj = _finite_nonnegative(f_j, "f_j")
    zi_value = float(zi)
    zj_value = float(zj)
    K = _finite_nonnegative(conductance, "conductance")
    if zi_value <= 0.0 or zj_value <= 0.0:
        raise ValueError("activity weights must be positive")
    return K * (fj * (1.0 + fi) / zj_value - fi * (1.0 + fj) / zi_value)


def bose_edge_pair_dissipation(
    f_i: float,
    f_j: float,
    *,
    zi: float,
    zj: float,
    conductance: float,
) -> float:
    """Pair contribution to ``dF/dt`` for the bosonic relative free energy."""

    fi = float(f_i)
    fj = float(f_j)
    if fi <= 0.0 or fj <= 0.0:
        raise ValueError("free-energy variables require strictly positive occupations")
    phi_i = fi / (float(zi) * (1.0 + fi))
    phi_j = fj / (float(zj) * (1.0 + fj))
    return (math.log(phi_i) - math.log(phi_j)) * bose_edge_flux(
        fi, fj, zi=zi, zj=zj, conductance=conductance
    )


def _validate_symmetric_conductance(matrix: np.ndarray, *, name: str) -> np.ndarray:
    value = np.asarray(matrix, dtype=float)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be square")
    if not np.all(np.isfinite(value)) or np.any(value < 0.0):
        raise ValueError(f"{name} must be finite and nonnegative")
    scale = max(float(np.max(value)), 1.0)
    if np.max(np.abs(value - value.T)) > 1e-13 * scale:
        raise ValueError(f"{name} must be symmetric")
    if np.max(np.abs(np.diag(value))) > 1e-14 * scale:
        raise ValueError(f"{name} diagonal must vanish")
    return value


def geometric_conductance_interpolate(
    left: np.ndarray,
    right: np.ndarray,
    *,
    fraction: float,
    coordinate_span: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Interpolate a reversible conductance graph in logarithmic variables.

    The active graph must be fixed inside one thermodynamic interpolation
    cell.  A zero/nonzero topology change is a discrete event and therefore
    fails closed instead of being hidden under a numerical floor.

    Returns the conductance and its derivative with respect to the physical
    interpolation coordinate, not with respect to the unit-cell fraction.
    """

    a = _validate_symmetric_conductance(left, name="left conductance")
    b = _validate_symmetric_conductance(right, name="right conductance")
    if a.shape != b.shape:
        raise ValueError("conductance shapes differ")
    lam = float(fraction)
    span = float(coordinate_span)
    if not math.isfinite(lam) or lam < 0.0 or lam > 1.0:
        raise ValueError("fraction must lie in [0,1]")
    if not math.isfinite(span) or span <= 0.0:
        raise ValueError("coordinate_span must be positive")
    active_a = a > 0.0
    active_b = b > 0.0
    if not np.array_equal(active_a, active_b):
        raise ValueError("active-graph topology changes inside interpolation cell")

    value = np.zeros_like(a)
    derivative = np.zeros_like(a)
    active = active_a
    log_left = np.zeros_like(a)
    log_right = np.zeros_like(a)
    log_left[active] = np.log(a[active])
    log_right[active] = np.log(b[active])
    value[active] = np.exp((1.0 - lam) * log_left[active] + lam * log_right[active])
    derivative[active] = value[active] * (log_right[active] - log_left[active]) / span
    # Symmetrize once so reciprocity is bitwise in downstream receipts.
    upper = np.triu(value)
    value = upper + np.triu(value, 1).T
    upper_d = np.triu(derivative)
    derivative = upper_d + np.triu(derivative, 1).T
    return value, derivative


def piecewise_constant_transfer(
    initial: float,
    emissivity: np.ndarray,
    opacity: np.ndarray,
    interval: np.ndarray,
) -> float:
    """Exact formal solution of ``df/dt = eta - chi*f`` on constant segments."""

    state = _finite_nonnegative(initial, "initial occupation")
    eta = np.asarray(emissivity, dtype=float)
    chi = np.asarray(opacity, dtype=float)
    dt = np.asarray(interval, dtype=float)
    if eta.shape != chi.shape or eta.shape != dt.shape or eta.ndim != 1:
        raise ValueError("emissivity, opacity and interval must be equal 1-D arrays")
    if np.any(~np.isfinite(eta)) or np.any(eta < 0.0):
        raise ValueError("emissivity must be finite and nonnegative")
    if np.any(~np.isfinite(chi)) or np.any(chi < 0.0):
        raise ValueError("opacity must be finite and nonnegative")
    if np.any(~np.isfinite(dt)) or np.any(dt < 0.0):
        raise ValueError("intervals must be finite and nonnegative")
    for source, absorption, width in zip(eta, chi, dt, strict=True):
        if absorption == 0.0:
            state += float(source * width)
        else:
            attenuation = math.exp(-float(absorption * width))
            state = attenuation * state + float(source) * (1.0 - attenuation) / float(absorption)
    return state


def entropy_metric_graph(
    linearized_conductance: np.ndarray,
    equilibrium_occupation: np.ndarray,
    mode_measure: np.ndarray,
) -> EntropyMetricGraph:
    """Build the entropy-variable graph Laplacian and positive mass diagonal.

    ``linearized_conductance`` is the already-positive edge weight
    ``q K_AB (1+f_A^*)(1+f_B^*)``.  Its graph Laplacian is the exact collision
    linearization in activity-log variables.  The time coefficient in those
    variables is ``m_A f_A^*(1+f_A^*)``.
    """

    conductance = _validate_symmetric_conductance(
        linearized_conductance, name="linearized conductance"
    )
    equilibrium = np.asarray(equilibrium_occupation, dtype=float)
    measure = np.asarray(mode_measure, dtype=float)
    if equilibrium.shape != (len(conductance),) or measure.shape != equilibrium.shape:
        raise ValueError("equilibrium/mode-measure shape mismatch")
    if np.any(equilibrium <= 0.0) or np.any(measure <= 0.0):
        raise ValueError("equilibrium occupation and mode measure must be positive")
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    entropy_mass = measure * equilibrium * (1.0 + equilibrium)
    return EntropyMetricGraph(laplacian=laplacian, entropy_mass=entropy_mass)


def w_orthogonal_projectors(weight: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return the W-orthogonal constant-mode projector and its complement."""

    diagonal = np.asarray(weight, dtype=float)
    if diagonal.ndim != 1 or np.any(diagonal <= 0.0) or not np.all(np.isfinite(diagonal)):
        raise ValueError("weight must be a finite positive vector")
    one = np.ones(len(diagonal))
    projector = np.outer(one, diagonal) / float(np.sum(diagonal))
    return projector, np.eye(len(diagonal)) - projector


def _minmod(left: float, right: float) -> float:
    if left * right <= 0.0:
        return 0.0
    return math.copysign(min(abs(left), abs(right)), left)


def limited_linear_traces(
    cell_average: np.ndarray,
    cell_faces: np.ndarray,
    *,
    epsilon: float = 0.0,
) -> LimitedLinearTraces:
    """Conservative positivity/local-bound limited MUSCL traces.

    One common multiplier scales both traces in a cell.  Consequently the
    reconstructed linear polynomial keeps the supplied cell average exactly.
    On a fixed active limiter branch the map is differentiable; a branch switch
    is a discrete/semismooth event for the trajectory integrator.
    """

    values = np.asarray(cell_average, dtype=float)
    faces = np.asarray(cell_faces, dtype=float)
    floor = float(epsilon)
    if values.ndim != 1 or faces.shape != (len(values) + 1,):
        raise ValueError("cell_average/cell_faces shape mismatch")
    if np.any(np.diff(faces) <= 0.0):
        raise ValueError("cell faces must increase")
    if not np.all(np.isfinite(values)) or np.any(values < floor):
        raise ValueError("cell averages must be finite and above epsilon")
    centers = 0.5 * (faces[:-1] + faces[1:])
    slope = np.zeros_like(values)
    if len(values) >= 2:
        slope[0] = (values[1] - values[0]) / (centers[1] - centers[0])
        slope[-1] = (values[-1] - values[-2]) / (centers[-1] - centers[-2])
    for index in range(1, len(values) - 1):
        backward = (values[index] - values[index - 1]) / (centers[index] - centers[index - 1])
        forward = (values[index + 1] - values[index]) / (centers[index + 1] - centers[index])
        slope[index] = _minmod(float(backward), float(forward))

    limiter = np.ones_like(values)
    left_delta = slope * (faces[:-1] - centers)
    right_delta = slope * (faces[1:] - centers)
    for index in range(len(values)):
        lo = max(index - 1, 0)
        hi = min(index + 2, len(values))
        lower = max(floor, float(np.min(values[lo:hi])))
        upper = float(np.max(values[lo:hi]))
        theta = 1.0
        for delta in (left_delta[index], right_delta[index]):
            if delta < 0.0:
                theta = min(theta, (values[index] - lower) / (-delta))
            elif delta > 0.0:
                theta = min(theta, (upper - values[index]) / delta)
        limiter[index] = min(max(theta, 0.0), 1.0)
    limited_slope = limiter * slope
    left = values + limited_slope * (faces[:-1] - centers)
    right = values + limited_slope * (faces[1:] - centers)
    return LimitedLinearTraces(left=left, right=right, slope=limited_slope, limiter=limiter)

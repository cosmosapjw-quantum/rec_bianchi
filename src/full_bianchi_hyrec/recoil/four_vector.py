"""SI Lorentz four-vector primitives for metric signature (-,+,+,+).

Four-momenta use p^mu=(E/c, p_x, p_y, p_z).
"""
from __future__ import annotations

import numpy as np
from scipy.constants import c, h


def _as_vector3(value: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != (3,):
        raise ValueError(f"{name} must have shape (3,)")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array


def _unit_direction(direction: np.ndarray) -> np.ndarray:
    array = _as_vector3(direction, "direction")
    norm = float(np.linalg.norm(array))
    if norm == 0.0:
        raise ValueError("direction must be nonzero")
    return array / norm


def _validated_beta(beta: np.ndarray) -> np.ndarray:
    array = _as_vector3(beta, "beta")
    beta2 = float(array @ array)
    if beta2 >= 1.0:
        raise ValueError("|beta| must be strictly less than 1")
    return array


def minkowski_dot(p: np.ndarray, q: np.ndarray) -> float:
    p_array = np.asarray(p, dtype=float)
    q_array = np.asarray(q, dtype=float)
    if p_array.shape != (4,) or q_array.shape != (4,):
        raise ValueError("four-vectors must have shape (4,)")
    return float(-p_array[0] * q_array[0] + p_array[1:] @ q_array[1:])


def photon_four_momentum(
    nu_hz: float,
    direction: np.ndarray,
) -> np.ndarray:
    if not np.isfinite(nu_hz) or nu_hz <= 0.0:
        raise ValueError("nu_hz must be positive and finite")
    unit = _unit_direction(direction)
    scale = h * float(nu_hz) / c
    return np.concatenate(([scale], scale * unit))


def atom_four_momentum(
    mass_kg: float,
    beta: np.ndarray,
) -> np.ndarray:
    if not np.isfinite(mass_kg) or mass_kg <= 0.0:
        raise ValueError("mass_kg must be positive and finite")
    beta_array = _validated_beta(beta)
    gamma = 1.0 / np.sqrt(1.0 - beta_array @ beta_array)
    scale = gamma * float(mass_kg) * c
    return np.concatenate(([scale], scale * beta_array))


def atom_beta(momentum: np.ndarray) -> np.ndarray:
    array = np.asarray(momentum, dtype=float)
    if array.shape != (4,) or not np.all(np.isfinite(array)):
        raise ValueError("momentum must be a finite four-vector")
    if array[0] <= 0.0:
        raise ValueError("atom energy component must be positive")
    beta = array[1:] / array[0]
    return _validated_beta(beta)


def boost_four_momentum(
    momentum: np.ndarray,
    beta: np.ndarray,
) -> np.ndarray:
    """Transform a four-momentum to the frame moving with velocity beta."""
    p = np.asarray(momentum, dtype=float)
    if p.shape != (4,) or not np.all(np.isfinite(p)):
        raise ValueError("momentum must be a finite four-vector")
    b = _validated_beta(beta)
    beta2 = float(b @ b)
    if beta2 == 0.0:
        return p.copy()

    gamma = 1.0 / np.sqrt(1.0 - beta2)
    beta_dot_p = float(b @ p[1:])
    p0 = gamma * (p[0] - beta_dot_p)
    spatial = (
        p[1:]
        + (
            (gamma - 1.0) * beta_dot_p / beta2
            - gamma * p[0]
        )
        * b
    )
    return np.concatenate(([p0], spatial))


def inverse_boost_four_momentum(
    momentum_rest: np.ndarray,
    beta: np.ndarray,
) -> np.ndarray:
    """Transform from the beta-comoving frame back to the original frame."""
    return boost_four_momentum(momentum_rest, -_validated_beta(beta))

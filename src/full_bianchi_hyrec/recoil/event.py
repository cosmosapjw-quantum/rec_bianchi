"""Exact elastic photon-hydrogen recoil events."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.constants import c, h

from .four_vector import (
    atom_beta,
    boost_four_momentum,
    inverse_boost_four_momentum,
    minkowski_dot,
    photon_four_momentum,
)


@dataclass(frozen=True)
class RecoilEvent:
    P_i: np.ndarray
    k_i: np.ndarray
    P_f: np.ndarray
    k_f: np.ndarray
    P_i_initial_rest: np.ndarray
    k_i_initial_rest: np.ndarray
    P_f_initial_rest: np.ndarray
    k_f_initial_rest: np.ndarray
    nu_in_rest_hz: float
    nu_out_rest_hz: float
    mu_rest: float


def _unit(vector: np.ndarray) -> np.ndarray:
    value = np.asarray(vector, dtype=float)
    if value.shape != (3,):
        raise ValueError("direction must have shape (3,)")
    norm = float(np.linalg.norm(value))
    if norm == 0.0 or not np.isfinite(norm):
        raise ValueError("direction must be finite and nonzero")
    return value / norm


def scatter_elastic(
    P_i: np.ndarray,
    k_i: np.ndarray,
    outgoing_direction_initial_rest: np.ndarray,
    mass_kg: float,
) -> RecoilEvent:
    P_i = np.asarray(P_i, dtype=float)
    k_i = np.asarray(k_i, dtype=float)
    if P_i.shape != (4,) or k_i.shape != (4,):
        raise ValueError("P_i and k_i must be four-vectors")
    if mass_kg <= 0.0:
        raise ValueError("mass_kg must be positive")

    beta_i = atom_beta(P_i)
    k_i_rest = boost_four_momentum(k_i, beta_i)
    P_i_rest = np.array([mass_kg * c, 0.0, 0.0, 0.0])

    nu_in = c * k_i_rest[0] / h
    n_in = _unit(k_i_rest[1:])
    n_out = _unit(outgoing_direction_initial_rest)
    mu = float(np.clip(n_in @ n_out, -1.0, 1.0))

    epsilon = h * nu_in / (mass_kg * c**2)
    nu_out = nu_in / (1.0 + epsilon * (1.0 - mu))
    k_f_rest = photon_four_momentum(nu_out, n_out)

    k_f = inverse_boost_four_momentum(k_f_rest, beta_i)
    # This definition makes four-momentum conservation the event ledger.
    P_f = P_i + k_i - k_f
    P_f_rest = boost_four_momentum(P_f, beta_i)

    return RecoilEvent(
        P_i=P_i.copy(),
        k_i=k_i.copy(),
        P_f=P_f,
        k_f=k_f,
        P_i_initial_rest=P_i_rest,
        k_i_initial_rest=k_i_rest,
        P_f_initial_rest=P_f_rest,
        k_f_initial_rest=k_f_rest,
        nu_in_rest_hz=float(nu_in),
        nu_out_rest_hz=float(nu_out),
        mu_rest=mu,
    )


def event_residuals(
    event: RecoilEvent,
    mass_kg: float,
) -> dict[str, float]:
    conservation = event.P_i + event.k_i - event.P_f - event.k_f
    conservation_scale = (
        np.linalg.norm(event.P_i)
        + np.linalg.norm(event.k_i)
        + np.linalg.norm(event.P_f)
        + np.linalg.norm(event.k_f)
    )
    shell_scale = (mass_kg * c) ** 2

    return {
        "four_momentum_relative": float(
            np.linalg.norm(conservation) / conservation_scale
        ),
        "initial_mass_shell_relative": float(
            abs(minkowski_dot(event.P_i, event.P_i) + shell_scale)
            / shell_scale
        ),
        "final_mass_shell_relative": float(
            abs(minkowski_dot(event.P_f, event.P_f) + shell_scale)
            / shell_scale
        ),
        "incoming_null_absolute": abs(
            minkowski_dot(event.k_i, event.k_i)
        ),
        "outgoing_null_absolute": abs(
            minkowski_dot(event.k_f, event.k_f)
        ),
    }


def reconstruct_reverse(
    forward: RecoilEvent,
    mass_kg: float,
) -> RecoilEvent:
    beta_final = atom_beta(forward.P_f)
    original_in_final_rest = boost_four_momentum(
        forward.k_i, beta_final
    )
    reverse_outgoing_direction = _unit(original_in_final_rest[1:])

    return scatter_elastic(
        forward.P_f,
        forward.k_f,
        reverse_outgoing_direction,
        mass_kg,
    )


def reverse_residuals(
    forward: RecoilEvent,
    reverse: RecoilEvent,
) -> dict[str, float]:
    photon_scale = np.linalg.norm(forward.k_i)
    atom_scale = np.linalg.norm(forward.P_i)
    conservation = (
        reverse.P_i + reverse.k_i - reverse.P_f - reverse.k_f
    )
    conservation_scale = (
        np.linalg.norm(reverse.P_i)
        + np.linalg.norm(reverse.k_i)
        + np.linalg.norm(reverse.P_f)
        + np.linalg.norm(reverse.k_f)
    )

    return {
        "photon_relative": float(
            np.linalg.norm(reverse.k_f - forward.k_i)
            / photon_scale
        ),
        "atom_relative": float(
            np.linalg.norm(reverse.P_f - forward.P_i)
            / atom_scale
        ),
        "reverse_four_momentum_relative": float(
            np.linalg.norm(conservation) / conservation_scale
        ),
    }

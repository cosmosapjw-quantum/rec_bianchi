"""Deterministic Maxwell--Juttner reweighting of a symmetric orbit cache.

This module changes only the thermal dynamic-structure factor.  It does
not alter the COM--KHW amplitude quadrature or the finite-volume rule.
"""
from __future__ import annotations

import math
import numpy as np

from .invariant_pair_measure import (
    log_maxwell_boltzmann_structure_factor,
    log_maxwell_juttner_structure_factor,
)


def mj_to_mb_log_ratio(
    q_dimensionless: float,
    delta_dimensionless: float,
    mass_kg: float,
    temperature_K: float,
) -> float:
    """Return log(S_MJ/S_MB).

    Both structure factors obey the same endpoint-exchange affinity, so
    this ratio is even under delta -> -delta up to floating-point error.
    """
    return float(
        log_maxwell_juttner_structure_factor(
            q_dimensionless,
            delta_dimensionless,
            mass_kg,
            temperature_K,
        )
        - log_maxwell_boltzmann_structure_factor(
            q_dimensionless,
            delta_dimensionless,
            mass_kg,
            temperature_K,
        )
    )


def reweight_symmetric_conductance(
    conductance: np.ndarray,
    pair_factor: np.ndarray,
) -> np.ndarray:
    conductance = np.asarray(conductance, dtype=float)
    pair_factor = np.asarray(pair_factor, dtype=float)
    if conductance.shape != pair_factor.shape:
        raise ValueError("conductance and pair_factor must have the same shape")
    if conductance.ndim != 2 or conductance.shape[0] != conductance.shape[1]:
        raise ValueError("conductance must be square")
    if np.max(np.abs(conductance - conductance.T)) > 1e-12:
        raise ValueError("input conductance must be symmetric")
    if np.max(np.abs(pair_factor - pair_factor.T)) > 1e-12:
        raise ValueError("pair_factor must be symmetric")
    if np.any(conductance < 0.0) or np.any(pair_factor < 0.0):
        raise ValueError("conductance and pair_factor must be nonnegative")

    result = conductance * pair_factor
    np.fill_diagonal(result, 0.0)
    # Multiplication of two symmetric arrays is symmetric algebraically;
    # this assertion detects any accidental asymmetric mapping upstream.
    if np.max(np.abs(result - result.T)) > 1e-13:
        raise FloatingPointError("reweighting broke pair symmetry")
    return result


def generator_from_conductance(
    conductance: np.ndarray,
    equilibrium_weight: np.ndarray,
) -> np.ndarray:
    conductance = np.asarray(conductance, dtype=float)
    equilibrium_weight = np.asarray(equilibrium_weight, dtype=float)
    if conductance.shape != (
        len(equilibrium_weight), len(equilibrium_weight)
    ):
        raise ValueError("shape mismatch")
    if np.any(equilibrium_weight <= 0.0):
        raise ValueError("equilibrium weights must be positive")

    rate = conductance / equilibrium_weight[None, :]
    np.fill_diagonal(rate, 0.0)
    np.fill_diagonal(rate, -rate.sum(axis=0))
    return rate

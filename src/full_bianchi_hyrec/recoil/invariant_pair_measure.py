"""Lorentz-invariant photon--atom pair measure.

The primary variables are the two photon endpoints.  The final atom is
eliminated with the four-dimensional delta function, following the
standard relativistic Boltzmann collision integral.  A Breit-frame
reduction gives an analytic Maxwell--Jüttner dynamic structure factor.

Metric signature: (-,+,+,+).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.constants import c, h, k
from scipy.special import kve


@dataclass(frozen=True)
class PhotonPairInvariants:
    nu_source_hz: float
    nu_target_hz: float
    mu: float
    kappa_source: float
    kappa_target: float
    q_dimensionless: float
    delta_dimensionless: float
    spacelike_transfer_dimensionless: float


def _scaled_k2(z: float) -> float:
    value = float(kve(2, z))
    if np.isfinite(value) and value > 0.0:
        return value

    # e^z K_2(z), sufficient through recombination's z~10^9.
    return math.sqrt(math.pi / (2.0 * z)) * (
        1.0
        + 15.0 / (8.0 * z)
        + 105.0 / (128.0 * z**2)
        - 945.0 / (3072.0 * z**3)
    )


def photon_pair_invariants(
    nu_source_hz: float,
    nu_target_hz: float,
    mu: float,
    mass_kg: float,
) -> PhotonPairInvariants:
    if nu_source_hz <= 0.0 or nu_target_hz <= 0.0:
        raise ValueError("photon frequencies must be positive")
    if mass_kg <= 0.0:
        raise ValueError("mass_kg must be positive")
    if not -1.0 <= mu <= 1.0:
        raise ValueError("mu must lie in [-1,1]")

    kappa_source = h * nu_source_hz / (mass_kg * c**2)
    kappa_target = h * nu_target_hz / (mass_kg * c**2)
    q = math.sqrt(
        kappa_source**2
        + kappa_target**2
        - 2.0 * kappa_source * kappa_target * mu
    )
    delta = kappa_source - kappa_target
    transfer2 = q * q - delta * delta
    if transfer2 <= 0.0:
        raise ValueError(
            "photon momentum transfer must be spacelike; "
            "the coherent-forward distribution is handled separately"
        )

    return PhotonPairInvariants(
        nu_source_hz=float(nu_source_hz),
        nu_target_hz=float(nu_target_hz),
        mu=float(mu),
        kappa_source=float(kappa_source),
        kappa_target=float(kappa_target),
        q_dimensionless=float(q),
        delta_dimensionless=float(delta),
        spacelike_transfer_dimensionless=float(math.sqrt(transfer2)),
    )


def _gamma_min_minus_one(
    q_dimensionless: float,
    delta_dimensionless: float,
) -> float:
    q = float(q_dimensionless)
    delta = float(delta_dimensionless)
    if q <= 0.0:
        raise ValueError("q_dimensionless must be positive")
    ratio = delta / q
    if abs(ratio) >= 1.0:
        raise ValueError("the transfer must be spacelike")

    root = math.sqrt(1.0 - ratio * ratio)
    gamma_breit = 1.0 / root
    chi = q * root

    # Stable evaluation of
    # gamma_min = (q/chi)*sqrt(1+chi^2/4) - delta/2.
    sqrt_term = math.sqrt(1.0 + chi * chi / 4.0)
    sqrt_minus_one = (
        chi * chi / 4.0
    ) / (sqrt_term + 1.0)
    gamma_minus_one = (
        ratio * ratio
    ) / (root * (1.0 + root))

    return (
        gamma_breit * sqrt_minus_one
        + gamma_minus_one
        - delta / 2.0
    )


def log_maxwell_juttner_structure_factor(
    q_dimensionless: float,
    delta_dimensionless: float,
    mass_kg: float,
    temperature_K: float,
) -> float:
    """Relativistic dynamic structure factor in the v0.12 normalization.

    Let Q=k_source-k_target in units of M c.  Eliminating the final atom
    from

        d^3p/(2E) 2*pi delta(2 p.Q + Q^2)

    and evaluating the Maxwell--Jüttner weight in the Breit frame gives

        S_MJ = exp[-z(gamma_min-1)]/[2 q e^z K_2(z)].

    This normalization tends to the v0.12 Maxwell--Boltzmann structure
    factor as kT/(Mc^2), q and delta approach zero.
    """
    if mass_kg <= 0.0 or temperature_K <= 0.0:
        raise ValueError("mass and temperature must be positive")

    q = float(q_dimensionless)
    delta = float(delta_dimensionless)
    gamma_min_minus_one = _gamma_min_minus_one(q, delta)
    z = mass_kg * c**2 / (k * temperature_K)

    return (
        -z * gamma_min_minus_one
        - math.log(2.0 * q * _scaled_k2(z))
    )


def maxwell_juttner_structure_factor(
    q_dimensionless: float,
    delta_dimensionless: float,
    mass_kg: float,
    temperature_K: float,
) -> float:
    value = log_maxwell_juttner_structure_factor(
        q_dimensionless,
        delta_dimensionless,
        mass_kg,
        temperature_K,
    )
    return float(math.exp(value))


def log_maxwell_boltzmann_structure_factor(
    q_dimensionless: float,
    delta_dimensionless: float,
    mass_kg: float,
    temperature_K: float,
) -> float:
    if mass_kg <= 0.0 or temperature_K <= 0.0:
        raise ValueError("mass and temperature must be positive")
    q = float(q_dimensionless)
    delta = float(delta_dimensionless)
    if q <= 0.0:
        raise ValueError("q_dimensionless must be positive")

    theta = k * temperature_K / (mass_kg * c**2)
    return (
        -0.5 * math.log(2.0 * math.pi * theta)
        - math.log(q)
        - (delta - q * q / 2.0) ** 2
        / (2.0 * theta * q * q)
    )


def maxwell_boltzmann_structure_factor(
    q_dimensionless: float,
    delta_dimensionless: float,
    mass_kg: float,
    temperature_K: float,
) -> float:
    return float(
        math.exp(
            log_maxwell_boltzmann_structure_factor(
                q_dimensionless,
                delta_dimensionless,
                mass_kg,
                temperature_K,
            )
        )
    )


def invariant_pair_conductance_log(
    *,
    nu_source_hz: float,
    nu_target_hz: float,
    mu: float,
    mass_kg: float,
    temperature_K: float,
    amplitude_average: float,
) -> float:
    """Log of the common equilibrium conductance density.

    The photon invariant measures supply nu_source*nu_target.  The
    source Boltzmann factor and S_MJ obey exact endpoint exchange:

      S_MJ(q,-delta)=exp[-beta h(nu_s-nu_t)] S_MJ(q,delta).

    A PT-invariant positive amplitude average therefore gives an
    endpoint-symmetric conductance before matrix assembly.
    """
    if amplitude_average <= 0.0 or not np.isfinite(amplitude_average):
        raise ValueError("amplitude_average must be positive and finite")

    invariants = photon_pair_invariants(
        nu_source_hz,
        nu_target_hz,
        mu,
        mass_kg,
    )
    log_structure = log_maxwell_juttner_structure_factor(
        invariants.q_dimensionless,
        invariants.delta_dimensionless,
        mass_kg,
        temperature_K,
    )
    beta = 1.0 / (k * temperature_K)

    return float(
        math.log(nu_source_hz)
        + math.log(nu_target_hz)
        - beta * h * nu_source_hz
        + log_structure
        + math.log(amplitude_average)
    )

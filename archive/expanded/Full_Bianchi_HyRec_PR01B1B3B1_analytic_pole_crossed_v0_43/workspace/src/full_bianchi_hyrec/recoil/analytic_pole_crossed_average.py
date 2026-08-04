"""Analytic Gaussian average of the scalar COM 2p pole+crossed amplitude.

For a fixed unordered photon endpoint pair, the nonrelativistic atomic
energy delta fixes the momentum parallel to the photon transfer.  The
remaining scattering-plane momentum is a standard Gaussian variable z.
Both time-ordered 2p denominators are linear in z.  Their squared terms
and interference are therefore closed combinations of the Faddeeva
function.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.constants import c, h, k
from scipy.special import wofz


@dataclass(frozen=True)
class PoleCrossedParameters:
    q_momentum: float
    p_parallel: float
    pole_detuning_A_hz: float
    pole_slope_B_hz: float
    crossed_detuning_C_hz: float
    crossed_slope_D_hz: float
    slope_antisymmetry_relative: float
    pole_location_z: float
    pole_width_z: float
    crossed_location_z: float
    crossed_width_z: float


@dataclass(frozen=True)
class PoleCrossedAverage:
    pole: float
    crossed: float
    interference: float
    total: float
    cross_expectation: complex


def _geometry(
    nu_source_hz: float,
    nu_target_hz: float,
    mu: float,
):
    n_s = np.array([0.0, 0.0, 1.0])
    n_t = np.array([
        math.sqrt(max(0.0, 1.0 - mu * mu)),
        0.0,
        mu,
    ])
    p_s = h * nu_source_hz / c
    p_t = h * nu_target_hz / c
    q_vec = p_s * n_s - p_t * n_t
    q = float(np.linalg.norm(q_vec))
    if q == 0.0:
        raise ValueError(
            "coherent-forward distribution requires a separate limit"
        )
    q_hat = q_vec / q

    n_s_perp = n_s - float(n_s @ q_hat) * q_hat
    norm_perp = float(np.linalg.norm(n_s_perp))
    if norm_perp < 1.0e-15:
        e_t = np.array([1.0, 0.0, 0.0])
    else:
        e_t = n_s_perp / norm_perp

    return n_s, n_t, q, q_hat, e_t


def conditional_pole_crossed_parameters(
    nu_source_hz: float,
    nu_target_hz: float,
    mu: float,
    *,
    mass_kg: float,
    temperature_K: float,
    nu_internal_hz: float,
    gamma_half_width_hz: float,
) -> PoleCrossedParameters:
    if nu_source_hz <= 0.0 or nu_target_hz <= 0.0:
        raise ValueError("frequencies must be positive")
    if not -1.0 <= mu <= 1.0:
        raise ValueError("mu must lie in [-1,1]")
    if mass_kg <= 0.0 or temperature_K <= 0.0:
        raise ValueError("mass and temperature must be positive")
    if gamma_half_width_hz <= 0.0:
        raise ValueError("gamma_half_width_hz must be positive")

    n_s, n_t, q, q_hat, e_t = _geometry(
        nu_source_hz, nu_target_hz, mu
    )

    delta_e = h * (nu_source_hz - nu_target_hz)
    p_parallel = mass_kg * delta_e / q - q / 2.0
    sigma_p = math.sqrt(mass_kg * k * temperature_K)

    a_s = float(n_s @ q_hat)
    b_s = float(n_s @ e_t)
    a_t = float(n_t @ q_hat)
    b_t = float(n_t @ e_t)

    A = (
        nu_internal_hz
        - nu_source_hz
        + nu_source_hz * p_parallel * a_s / (mass_kg * c)
        + h * nu_source_hz**2 / (2.0 * mass_kg * c**2)
    )
    B = nu_source_hz * sigma_p * b_s / (mass_kg * c)

    C = (
        nu_internal_hz
        + nu_target_hz
        - nu_target_hz * p_parallel * a_t / (mass_kg * c)
        + h * nu_target_hz**2 / (2.0 * mass_kg * c**2)
    )
    D = -nu_target_hz * sigma_p * b_t / (mass_kg * c)

    slope_scale = max(abs(B), abs(D), 1.0)
    slope_residual = abs(B + D) / slope_scale

    def location_width(offset: float, slope: float):
        if abs(slope) < 1.0e-300:
            return math.nan, math.inf
        return -offset / slope, gamma_half_width_hz / abs(slope)

    pole_location, pole_width = location_width(A, B)
    crossed_location, crossed_width = location_width(C, D)

    return PoleCrossedParameters(
        q_momentum=q,
        p_parallel=p_parallel,
        pole_detuning_A_hz=A,
        pole_slope_B_hz=B,
        crossed_detuning_C_hz=C,
        crossed_slope_D_hz=D,
        slope_antisymmetry_relative=slope_residual,
        pole_location_z=pole_location,
        pole_width_z=pole_width,
        crossed_location_z=crossed_location,
        crossed_width_z=crossed_width,
    )


def gaussian_resolvent(pole: complex) -> complex:
    r"""Return E[(Z-pole)^-1] for Z~N(0,1), Im(pole)!=0.

    DLMF 7.7.2 gives the upper-half-plane representation.  The lower
    half plane is obtained by complex conjugation.
    """
    value = complex(pole)
    if value.imag > 0.0:
        return 1j * math.sqrt(math.pi / 2.0) * wofz(
            value / math.sqrt(2.0)
        )
    if value.imag < 0.0:
        return -1j * math.sqrt(math.pi / 2.0) * wofz(
            -value / math.sqrt(2.0)
        )
    raise ValueError("the Gaussian resolvent requires a non-real pole")


def gaussian_linear_inverse_mean(
    offset: complex,
    slope: float,
) -> complex:
    """Return E[(offset+slope Z)^-1] for Z~N(0,1)."""
    if abs(slope) < 1.0e-300:
        return 1.0 / offset
    pole = -offset / slope
    return gaussian_resolvent(pole) / slope


def gaussian_lorentzian_mean(
    detuning_hz: float,
    slope_hz: float,
    gamma_hz: float,
) -> float:
    """Return E[((detuning+slope Z)^2+gamma^2)^-1]."""
    if abs(slope_hz) < 1.0e-300:
        return 1.0 / (
            detuning_hz * detuning_hz + gamma_hz * gamma_hz
        )

    x_value = detuning_hz / (math.sqrt(2.0) * slope_hz)
    a_value = gamma_hz / (math.sqrt(2.0) * abs(slope_hz))
    H = float(np.real(wofz(x_value + 1j * a_value)))
    return (
        math.sqrt(math.pi)
        / (math.sqrt(2.0) * abs(slope_hz) * gamma_hz)
        * H
    )


def gaussian_product_inverse_mean(
    offset_one: complex,
    slope_one: float,
    offset_two: complex,
    slope_two: float,
) -> complex:
    r"""Return E[1/((o1+s1 Z)(o2+s2 Z))]."""
    zero_one = abs(slope_one) < 1.0e-300
    zero_two = abs(slope_two) < 1.0e-300
    if zero_one and zero_two:
        return 1.0 / (offset_one * offset_two)
    if zero_one:
        return gaussian_linear_inverse_mean(
            offset_two, slope_two
        ) / offset_one
    if zero_two:
        return gaussian_linear_inverse_mean(
            offset_one, slope_one
        ) / offset_two

    denominator = slope_one * offset_two - slope_two * offset_one
    scale = max(
        abs(slope_one * offset_two),
        abs(slope_two * offset_one),
        1.0,
    )
    if abs(denominator) < 1.0e-14 * scale:
        # This branch is not reached for the physical pole/crossed pair,
        # for which slopes are opposite and gamma>0.  Keep a clear failure
        # instead of silently losing digits.
        raise FloatingPointError("nearly coincident Gaussian poles")

    pole_one = -offset_one / slope_one
    pole_two = -offset_two / slope_two
    return (
        gaussian_resolvent(pole_one)
        - gaussian_resolvent(pole_two)
    ) / denominator


def analytic_mean_pole_crossed_amplitude_squared(
    nu_source_hz: float,
    nu_target_hz: float,
    mu: float,
    *,
    mass_kg: float,
    temperature_K: float,
    nu_internal_hz: float,
    gamma_half_width_hz: float,
    oscillator_strength: float,
) -> tuple[PoleCrossedAverage, PoleCrossedParameters]:
    parameters = conditional_pole_crossed_parameters(
        nu_source_hz,
        nu_target_hz,
        mu,
        mass_kg=mass_kg,
        temperature_K=temperature_K,
        nu_internal_hz=nu_internal_hz,
        gamma_half_width_hz=gamma_half_width_hz,
    )

    A = parameters.pole_detuning_A_hz
    B = parameters.pole_slope_B_hz
    C = parameters.crossed_detuning_C_hz
    D = parameters.crossed_slope_D_hz
    gamma = gamma_half_width_hz
    scale = -0.5 * oscillator_strength * nu_internal_hz
    scale_squared = scale * scale

    pole = scale_squared * gaussian_lorentzian_mean(A, B, gamma)
    crossed = scale_squared * gaussian_lorentzian_mean(C, D, gamma)

    # M_pole = scale/(A+Bz-i gamma)
    # M_cross = scale/(C+Dz+i gamma)
    # Hence M_pole * conj(M_cross) contains two factors with -i gamma.
    cross_expectation = gaussian_product_inverse_mean(
        complex(A, -gamma),
        B,
        complex(C, -gamma),
        D,
    )
    interference = 2.0 * scale_squared * float(np.real(cross_expectation))
    total = pole + crossed + interference

    if not np.isfinite(total) or total <= 0.0:
        raise FloatingPointError("non-positive analytic pole+crossed mean")

    return (
        PoleCrossedAverage(
            pole=float(pole),
            crossed=float(crossed),
            interference=float(interference),
            total=float(total),
            cross_expectation=complex(cross_expectation),
        ),
        parameters,
    )

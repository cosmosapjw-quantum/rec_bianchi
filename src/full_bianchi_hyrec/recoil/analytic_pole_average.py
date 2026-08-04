"""Analytic conditional Gaussian average of the scalar COM 2p pole.

Metric-independent local microphysics.  The nonrelativistic atom-energy
delta fixes the momentum parallel to the photon transfer.  The remaining
scattering-plane momentum is Gaussian and the squared Lorentzian pole
integral is a Voigt/Faddeeva function.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.constants import c, h, k
from scipy.special import wofz


@dataclass(frozen=True)
class PoleParameters:
    q_momentum: float
    p_parallel: float
    detuning_A_hz: float
    gaussian_slope_B_hz: float
    voigt_x: float
    voigt_a: float
    pole_location_t: float
    pole_width_t: float


def conditional_pole_parameters(
    nu_source_hz: float,
    nu_target_hz: float,
    mu: float,
    *,
    mass_kg: float,
    temperature_K: float,
    nu_internal_hz: float,
    gamma_half_width_hz: float,
) -> PoleParameters:
    if nu_source_hz <= 0 or nu_target_hz <= 0:
        raise ValueError('frequencies must be positive')
    if not -1.0 <= mu <= 1.0:
        raise ValueError('mu must lie in [-1,1]')
    if mass_kg <= 0 or temperature_K <= 0:
        raise ValueError('mass and temperature must be positive')

    n_s = np.array([0.0, 0.0, 1.0])
    n_t = np.array([math.sqrt(max(0.0, 1.0-mu*mu)), 0.0, mu])
    p_s = h * nu_source_hz / c
    p_t = h * nu_target_hz / c
    q_vec = p_s*n_s - p_t*n_t
    q = float(np.linalg.norm(q_vec))
    if q == 0.0:
        raise ValueError('coherent-forward distribution requires a separate limit')

    q_hat = q_vec/q
    n_perp = n_s - float(n_s@q_hat)*q_hat
    norm_perp = float(np.linalg.norm(n_perp))
    if norm_perp < 1e-15:
        e_t = np.array([1.0,0.0,0.0])
    else:
        e_t = n_perp/norm_perp

    delta_e = h*(nu_source_hz-nu_target_hz)
    p_parallel = mass_kg*delta_e/q - q/2.0
    sigma_p = math.sqrt(mass_kg*k*temperature_K)
    a_s = float(n_s@q_hat)
    b_s = float(n_s@e_t)

    A = (
        nu_internal_hz - nu_source_hz
        + nu_source_hz*p_parallel*a_s/(mass_kg*c)
        + h*nu_source_hz**2/(2.0*mass_kg*c**2)
    )
    B = nu_source_hz*sigma_p*b_s/(mass_kg*c)

    if abs(B) < 1e-300:
        voigt_x = math.copysign(math.inf, A) if A != 0 else 0.0
        voigt_a = math.inf
        location = math.nan
        width = math.inf
    else:
        voigt_x = A/(math.sqrt(2.0)*B)
        voigt_a = gamma_half_width_hz/(math.sqrt(2.0)*abs(B))
        location = -A/(math.sqrt(2.0)*B)
        width = voigt_a

    return PoleParameters(
        q_momentum=q,
        p_parallel=p_parallel,
        detuning_A_hz=A,
        gaussian_slope_B_hz=B,
        voigt_x=voigt_x,
        voigt_a=voigt_a,
        pole_location_t=location,
        pole_width_t=width,
    )


def analytic_mean_pole_amplitude_squared(
    nu_source_hz: float,
    nu_target_hz: float,
    mu: float,
    *,
    mass_kg: float,
    temperature_K: float,
    nu_internal_hz: float,
    gamma_half_width_hz: float,
    oscillator_strength: float,
) -> tuple[float, PoleParameters]:
    parameters = conditional_pole_parameters(
        nu_source_hz,nu_target_hz,mu,
        mass_kg=mass_kg,
        temperature_K=temperature_K,
        nu_internal_hz=nu_internal_hz,
        gamma_half_width_hz=gamma_half_width_hz,
    )
    scale = -0.5*oscillator_strength*nu_internal_hz
    A = parameters.detuning_A_hz
    B = parameters.gaussian_slope_B_hz
    gamma = gamma_half_width_hz

    if abs(B) < 1e-300:
        mean_inverse = 1.0/(A*A+gamma*gamma)
    else:
        H = float(np.real(wofz(parameters.voigt_x + 1j*parameters.voigt_a)))
        mean_inverse = (
            math.sqrt(math.pi)
            /(math.sqrt(2.0)*abs(B)*gamma)
            * H
        )
    return scale*scale*mean_inverse, parameters

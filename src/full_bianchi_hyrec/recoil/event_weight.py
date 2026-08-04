"""Maxwell-Juettner equilibrium conductance for scalar 2p recoil events.

This module is an event-level microreversibility audit.  It supplies a
positive scalar 2p pole+crossed Kramers-Heisenberg response and combines
it with the exact relativistic Maxwell-Juettner atom weight and dilute
photon Boltzmann factor.  It does not yet perform finite-volume
frequency-angle deposition.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.constants import c, h, k, physical_constants
from scipy.special import kv, kve

from .event import RecoilEvent
from .four_vector import (
    atom_beta,
    boost_four_momentum,
    minkowski_dot,
)


@dataclass(frozen=True)
class Scalar2PPoleModel:
    """Unresolved scalar Ly-alpha 2p pole plus its crossed denominator."""

    nu_alpha_hz: float
    A21_s_inv: float
    oscillator_strength: float

    @property
    def gamma_half_width_hz(self) -> float:
        return self.A21_s_inv / (4.0 * math.pi)

    @classmethod
    def ly_alpha(cls) -> "Scalar2PPoleModel":
        return cls(
            nu_alpha_hz=c / (1215.6701e-10),
            A21_s_inv=6.265e8,
            oscillator_strength=0.4161967179799824,
        )


@dataclass(frozen=True)
class PTKinematics:
    P_i: np.ndarray
    k_i: np.ndarray
    P_f: np.ndarray
    k_f: np.ndarray


def time_reverse_four_momentum(momentum: np.ndarray) -> np.ndarray:
    """Apply time reversal to a future-directed four-momentum."""
    value = np.asarray(momentum, dtype=float)
    if value.shape != (4,) or not np.all(np.isfinite(value)):
        raise ValueError("momentum must be a finite four-vector")
    return np.concatenate(([value[0]], -value[1:]))


def pt_reverse_kinematics(event: RecoilEvent) -> PTKinematics:
    """Return the PT-reversed event (T final -> T initial)."""
    return PTKinematics(
        P_i=time_reverse_four_momentum(event.P_f),
        k_i=time_reverse_four_momentum(event.k_f),
        P_f=time_reverse_four_momentum(event.P_i),
        k_f=time_reverse_four_momentum(event.k_i),
    )


def stable_atom_kinetic_energy(
    atom_momentum: np.ndarray,
    mass_kg: float,
) -> float:
    """Relativistic kinetic energy without subtracting two large energies."""
    momentum = np.asarray(atom_momentum, dtype=float)
    if momentum.shape != (4,) or not np.all(np.isfinite(momentum)):
        raise ValueError("atom_momentum must be a finite four-vector")
    if mass_kg <= 0.0 or not np.isfinite(mass_kg):
        raise ValueError("mass_kg must be positive and finite")

    spatial_squared = float(momentum[1:] @ momentum[1:])
    denominator = float(momentum[0] + mass_kg * c)
    return spatial_squared * c / denominator


def photon_energy(photon_momentum: np.ndarray) -> float:
    value = np.asarray(photon_momentum, dtype=float)
    if value.shape != (4,) or value[0] <= 0.0:
        raise ValueError("photon_momentum must be future directed")
    return float(c * value[0])


def rest_frame_frequency(
    atom_momentum: np.ndarray,
    photon_momentum: np.ndarray,
    mass_kg: float,
) -> float:
    """Photon frequency measured in the instantaneous atom rest frame."""
    frequency = -minkowski_dot(atom_momentum, photon_momentum) / (
        mass_kg * h
    )
    if frequency <= 0.0 or not np.isfinite(frequency):
        raise ValueError("rest-frame photon frequency must be positive")
    return float(frequency)


def rest_frame_direction(
    atom_momentum: np.ndarray,
    photon_momentum: np.ndarray,
) -> np.ndarray:
    beta = atom_beta(atom_momentum)
    photon_rest = boost_four_momentum(photon_momentum, beta)
    norm = float(np.linalg.norm(photon_rest[1:]))
    if norm == 0.0:
        raise ValueError("rest-frame photon direction is undefined")
    return photon_rest[1:] / norm


def scalar_2p_pole_crossed_amplitude(
    nu_in_rest_hz: float,
    nu_out_rest_hz: float,
    model: Scalar2PPoleModel,
) -> complex:
    """Dimensionless unresolved 2p resonant+crossed scalar response.

    This is the PR-01 audit amplitude.  PR-03 replaces it by the full
    seagull + bound + continuum COM-KHW amplitude.
    """
    gamma = model.gamma_half_width_hz
    scale = -0.5 * model.oscillator_strength * model.nu_alpha_hz
    pole = 1.0 / (
        model.nu_alpha_hz - nu_in_rest_hz - 1j * gamma
    )
    crossed = 1.0 / (
        model.nu_alpha_hz + nu_out_rest_hz + 1j * gamma
    )
    return scale * (pole + crossed)


def normalized_rayleigh_phase(mu: float) -> float:
    clipped = float(np.clip(mu, -1.0, 1.0))
    return 0.75 * (1.0 + clipped * clipped)


def invariant_2p_response_area(
    atom_initial: np.ndarray,
    photon_initial: np.ndarray,
    photon_final: np.ndarray,
    mass_kg: float,
    model: Scalar2PPoleModel,
) -> float:
    """Positive scalar KHW response per normalized solid-angle measure.

    The factor sigma_T Phi_R (nu_out*/nu_in*) |M_2p|^2 follows the
    standard Kramers-Heisenberg response convention.  It is used here as
    a common PT-invariant event response, not yet as the complete lab
    differential event rate.
    """
    nu_in = rest_frame_frequency(
        atom_initial, photon_initial, mass_kg
    )
    nu_out = rest_frame_frequency(
        atom_initial, photon_final, mass_kg
    )
    direction_in = rest_frame_direction(atom_initial, photon_initial)
    direction_out = rest_frame_direction(atom_initial, photon_final)
    mu = float(np.clip(direction_in @ direction_out, -1.0, 1.0))

    amplitude = scalar_2p_pole_crossed_amplitude(
        nu_in, nu_out, model
    )
    sigma_thomson = physical_constants["Thomson cross section"][0]
    response = (
        sigma_thomson
        * normalized_rayleigh_phase(mu)
        * (nu_out / nu_in)
        * abs(amplitude) ** 2
    )
    if response <= 0.0 or not np.isfinite(response):
        raise FloatingPointError("non-positive scalar event response")
    return float(response)


def maxwell_juttner_momentum_normalization_dimensionless(z: float) -> float:
    """Return 4 pi K_2(z)/z for q=p/(Mc) and exp[-z gamma]."""
    if z <= 0.0 or not np.isfinite(z):
        raise ValueError("z must be positive and finite")
    return float(4.0 * math.pi * kv(2, z) / z)


def log_maxwell_juttner_density(
    atom_momentum: np.ndarray,
    mass_kg: float,
    temperature_K: float,
) -> float:
    """Normalized log density with respect to d^3p.

    The exponent uses kinetic energy.  The corresponding stable
    normalization is 4 pi (Mc)^3 theta exp(z) K_2(z), where z=1/theta.
    """
    if temperature_K <= 0.0 or not np.isfinite(temperature_K):
        raise ValueError("temperature_K must be positive and finite")

    theta = k * temperature_K / (mass_kg * c**2)
    z = 1.0 / theta
    scaled_k2 = float(kve(2, z))
    if scaled_k2 <= 0.0 or not np.isfinite(scaled_k2):
        # Large-z asymptotic fallback through O(z^-2).
        scaled_k2 = math.sqrt(math.pi / (2.0 * z)) * (
            1.0 + 15.0 / (8.0 * z) + 105.0 / (128.0 * z**2)
        )

    log_normalization = (
        math.log(4.0 * math.pi)
        + 3.0 * math.log(mass_kg * c)
        + math.log(theta)
        + math.log(scaled_k2)
    )
    kinetic = stable_atom_kinetic_energy(atom_momentum, mass_kg)
    return float(-kinetic / (k * temperature_K) - log_normalization)


def equilibrium_conductance_log(
    atom_initial: np.ndarray,
    photon_initial: np.ndarray,
    photon_final: np.ndarray,
    mass_kg: float,
    temperature_K: float,
    model: Scalar2PPoleModel,
) -> float:
    response = invariant_2p_response_area(
        atom_initial,
        photon_initial,
        photon_final,
        mass_kg,
        model,
    )
    log_atom = log_maxwell_juttner_density(
        atom_initial, mass_kg, temperature_K
    )
    log_photon = -photon_energy(photon_initial) / (
        k * temperature_K
    )
    return float(log_atom + log_photon + math.log(response))


def _maxwell_boltzmann_thermal_log(
    atom_initial: np.ndarray,
    photon_initial: np.ndarray,
    mass_kg: float,
    temperature_K: float,
) -> float:
    spatial_squared = float(atom_initial[1:] @ atom_initial[1:])
    kinetic_nr = spatial_squared / (2.0 * mass_kg)
    return float(
        -(kinetic_nr + photon_energy(photon_initial))
        / (k * temperature_K)
    )


def audit_pt_detailed_balance(
    event: RecoilEvent,
    mass_kg: float,
    temperature_K: float,
    model: Scalar2PPoleModel,
) -> dict[str, float]:
    reverse = pt_reverse_kinematics(event)

    response_forward = invariant_2p_response_area(
        event.P_i, event.k_i, event.k_f, mass_kg, model
    )
    response_reverse = invariant_2p_response_area(
        reverse.P_i, reverse.k_i, reverse.k_f, mass_kg, model
    )
    response_relative = abs(response_forward - response_reverse) / (
        abs(response_forward) + abs(response_reverse)
    )

    thermal_forward = -(
        stable_atom_kinetic_energy(event.P_i, mass_kg)
        + photon_energy(event.k_i)
    ) / (k * temperature_K)
    thermal_reverse = -(
        stable_atom_kinetic_energy(reverse.P_i, mass_kg)
        + photon_energy(reverse.k_i)
    ) / (k * temperature_K)

    conductance_forward = equilibrium_conductance_log(
        event.P_i,
        event.k_i,
        event.k_f,
        mass_kg,
        temperature_K,
        model,
    )
    conductance_reverse = equilibrium_conductance_log(
        reverse.P_i,
        reverse.k_i,
        reverse.k_f,
        mass_kg,
        temperature_K,
        model,
    )

    mb_forward = _maxwell_boltzmann_thermal_log(
        event.P_i, event.k_i, mass_kg, temperature_K
    )
    mb_reverse = _maxwell_boltzmann_thermal_log(
        reverse.P_i, reverse.k_i, mass_kg, temperature_K
    )

    nu_f_in = rest_frame_frequency(
        event.P_i, event.k_i, mass_kg
    )
    nu_f_out = rest_frame_frequency(
        event.P_i, event.k_f, mass_kg
    )
    nu_r_in = rest_frame_frequency(
        reverse.P_i, reverse.k_i, mass_kg
    )
    nu_r_out = rest_frame_frequency(
        reverse.P_i, reverse.k_f, mass_kg
    )

    return {
        "response_forward_m2": response_forward,
        "response_reverse_m2": response_reverse,
        "response_relative": float(response_relative),
        "thermal_log_residual": float(thermal_forward - thermal_reverse),
        "conductance_log_residual": float(
            conductance_forward - conductance_reverse
        ),
        "maxwell_boltzmann_log_residual": float(
            mb_forward - mb_reverse
        ),
        "rest_frequency_in_relative": float(
            abs(nu_f_in - nu_r_in) / nu_f_in
        ),
        "rest_frequency_out_relative": float(
            abs(nu_f_out - nu_r_out) / nu_f_out
        ),
    }


def audit_pt_detailed_balance_high_precision(
    event: RecoilEvent,
    mass_kg: float,
    temperature_K: float,
    model: Scalar2PPoleModel,
    *,
    dps: int = 80,
):
    """Independent PT audit after reconstructing the event in mpmath.

    The float64 event supplies initial data and the chosen outgoing
    direction.  The exact recoil event and its PT reverse are then rebuilt
    at arbitrary precision, preventing a one-Hz resonance-detuning error
    from being amplified by the narrow 2p pole.
    """
    import mpmath as mp

    mp.mp.dps = int(dps)

    def mpf(value):
        return mp.mpf(repr(float(value)))

    c_mp = mpf(c)
    h_mp = mpf(h)
    k_mp = mpf(k)
    mass = mpf(mass_kg)
    temperature = mpf(temperature_K)
    nu_alpha = mpf(model.nu_alpha_hz)
    gamma_width = mpf(model.gamma_half_width_hz)
    f_osc = mpf(model.oscillator_strength)
    sigma_t = mpf(physical_constants["Thomson cross section"][0])

    def vector(values):
        return [mpf(value) for value in values]

    def dot3(a, b):
        return sum(x * y for x, y in zip(a, b))

    def norm3(a):
        return mp.sqrt(dot3(a, a))

    def unit3(a):
        norm = norm3(a)
        return [x / norm for x in a]

    def mdot(a, b):
        return -a[0] * b[0] + dot3(a[1:], b[1:])

    def boost(momentum, beta):
        beta2 = dot3(beta, beta)
        if beta2 == 0:
            return list(momentum)
        gamma = 1 / mp.sqrt(1 - beta2)
        bdotp = dot3(beta, momentum[1:])
        p0 = gamma * (momentum[0] - bdotp)
        coefficient = (
            (gamma - 1) * bdotp / beta2 - gamma * momentum[0]
        )
        spatial = [
            momentum[i + 1] + coefficient * beta[i]
            for i in range(3)
        ]
        return [p0, *spatial]

    def inverse_boost(momentum, beta):
        return boost(momentum, [-value for value in beta])

    def time_reverse(momentum):
        return [momentum[0], *[-value for value in momentum[1:]]]

    # Rebuild exact on-shell initial data from the float64 event's
    # velocity, frequency and direction, rather than promoting its
    # already-rounded four-vector components to arbitrary precision.
    event_P_i = vector(event.P_i)
    event_k_i = vector(event.k_i)
    beta_i = [
        event_P_i[index + 1] / event_P_i[0]
        for index in range(3)
    ]
    beta2 = dot3(beta_i, beta_i)
    gamma_i = 1 / mp.sqrt(1 - beta2)
    P_i = [
        gamma_i * mass * c_mp,
        *[gamma_i * mass * c_mp * value for value in beta_i],
    ]

    nu_lab = c_mp * event_k_i[0] / h_mp
    n_lab = unit3(event_k_i[1:])
    k_scale = h_mp * nu_lab / c_mp
    k_i = [k_scale, *[k_scale * value for value in n_lab]]

    k_i_rest = boost(k_i, beta_i)
    nu_in = c_mp * k_i_rest[0] / h_mp
    n_out = unit3(vector(event.k_f_initial_rest[1:]))
    n_in = unit3(k_i_rest[1:])
    mu = dot3(n_in, n_out)

    epsilon = h_mp * nu_in / (mass * c_mp**2)
    nu_out = nu_in / (1 + epsilon * (1 - mu))
    scale_out = h_mp * nu_out / c_mp
    k_f_rest = [scale_out, *[scale_out * value for value in n_out]]
    k_f = inverse_boost(k_f_rest, beta_i)
    P_f = [P_i[index] + k_i[index] - k_f[index] for index in range(4)]

    reverse_P_i = time_reverse(P_f)
    reverse_k_i = time_reverse(k_f)
    reverse_k_f = time_reverse(k_i)

    def rest_frequency(atom, photon):
        return -mdot(atom, photon) / (mass * h_mp)

    def rest_direction(atom, photon):
        beta = [atom[index + 1] / atom[0] for index in range(3)]
        photon_rest = boost(photon, beta)
        return unit3(photon_rest[1:])

    def response(atom, photon_in, photon_out):
        vin = rest_frequency(atom, photon_in)
        vout = rest_frequency(atom, photon_out)
        nin = rest_direction(atom, photon_in)
        nout = rest_direction(atom, photon_out)
        mu_local = dot3(nin, nout)
        amplitude = -mp.mpf("0.5") * f_osc * nu_alpha * (
            1 / (nu_alpha - vin - 1j * gamma_width)
            + 1 / (nu_alpha + vout + 1j * gamma_width)
        )
        phase = mp.mpf("0.75") * (1 + mu_local**2)
        return sigma_t * phase * (vout / vin) * abs(amplitude) ** 2, vin, vout

    response_f, vin_f, vout_f = response(P_i, k_i, k_f)
    response_r, vin_r, vout_r = response(
        reverse_P_i, reverse_k_i, reverse_k_f
    )

    def kinetic(atom):
        p2 = dot3(atom[1:], atom[1:])
        return p2 * c_mp / (atom[0] + mass * c_mp)

    thermal_f = -(kinetic(P_i) + c_mp * k_i[0]) / (k_mp * temperature)
    thermal_r = -(
        kinetic(reverse_P_i) + c_mp * reverse_k_i[0]
    ) / (k_mp * temperature)

    log_conductance_f = thermal_f + mp.log(response_f)
    log_conductance_r = thermal_r + mp.log(response_r)

    return {
        "response_relative": abs(response_f - response_r)
        / (abs(response_f) + abs(response_r)),
        "thermal_log_residual": thermal_f - thermal_r,
        "conductance_log_residual": log_conductance_f - log_conductance_r,
        "rest_frequency_in_relative": abs(vin_f - vin_r) / vin_f,
        "rest_frequency_out_relative": abs(vout_f - vout_r) / vout_f,
        "response_forward_m2": response_f,
        "response_reverse_m2": response_r,
    }

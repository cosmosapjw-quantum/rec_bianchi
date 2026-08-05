"""Complete scalar bound-plus-continuum COM--KHW amplitude.

Conventions
-----------
Metric signature is ``(-,+,+,+)``.  Photon and atom four-momenta use
``p^0=E/c``.  Frequencies are ordinary frequencies (Hz), not angular
frequencies, so every energy denominator has been divided by ``h``.
The scalar polarization/phase factor is kept outside the amplitude.

The p-gauge scalar amplitude is

    M = 1 - 1/2 int df(nu_s) nu_s
                    [1/D_s^- + 1/D_s^+],

where the leading one is the A^2 seagull term, the discrete and
continuum oscillator-strength measure is exact for hydrogen 1s->p in
the electric-dipole approximation, and the two denominators are the two
time orderings.  Only the unresolved 2p pole receives a natural width in
the Ly-alpha production window; all higher states are far off shell.

The production conditional Maxwellian average isolates the narrow 2p
pole/crossed pair analytically with the Faddeeva function and represents
the smooth higher-state bound+continuum background by a source-compiled
Taylor polynomial.  The polynomial is not a fitted physical model: its
coefficients are moments of the exact positive oscillator-strength
measure and are independently checked against direct state sums.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Iterable

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.constants import c, h, physical_constants
from scipy.special import wofz

from .four_vector import minkowski_dot


LY_ALPHA_WAVELENGTH_M = 1215.6701e-10
LY_ALPHA_FREQUENCY_HZ = c / LY_ALPHA_WAVELENGTH_M
LY_ALPHA_A21_S_INV = 6.265e8
LY_ALPHA_GAMMA_HALF_HZ = LY_ALPHA_A21_S_INV / (4.0 * math.pi)
LY_ALPHA_OSCILLATOR_STRENGTH = 0.4161967179799827
RYDBERG_FREQUENCY_HZ = LY_ALPHA_FREQUENCY_HZ / 0.75
STATIC_POLARIZABILITY_A0_CUBED = 4.5


def _readonly(values: np.ndarray) -> np.ndarray:
    out = np.asarray(values, dtype=float)
    out.setflags(write=False)
    return out


def bound_oscillator_strength(n: int | np.ndarray) -> np.ndarray:
    r"""Exact hydrogen 1s->np oscillator strength.

    The logarithmic form avoids overflow in ``(n-1)^(2n-4)`` and
    ``(n+1)^(2n+4)``.
    """
    value = np.asarray(n, dtype=float)
    if np.any(value < 2.0) or np.any(value != np.floor(value)):
        raise ValueError("bound principal quantum numbers must be integers >=2")
    log_f = (
        math.log(256.0 / 3.0)
        + 5.0 * np.log(value)
        + (2.0 * value - 4.0) * np.log(value - 1.0)
        - (2.0 * value + 4.0) * np.log(value + 1.0)
    )
    return np.exp(log_f)


def continuum_oscillator_strength_density(index_n: float | np.ndarray) -> np.ndarray:
    r"""Exact hydrogen 1s->continuum-p density ``df/dn``.

    Here ``n>0`` parameterizes continuum energy by
    ``Delta/Ry = 1 + 1/n^2``.  ``expm1`` preserves the small-n limit.
    """
    value = np.asarray(index_n, dtype=float)
    if np.any(value <= 0.0) or not np.all(np.isfinite(value)):
        raise ValueError("continuum index must be positive and finite")
    denominator = -np.expm1(-2.0 * math.pi * value)
    return (
        (256.0 / 3.0)
        * value**5
        / (1.0 + value**2) ** 4
        * np.exp(-4.0 * value * np.arctan2(1.0, value))
        / denominator
    )


@dataclass(frozen=True)
class OscillatorStrengthMeasure:
    """Positive finite representation of the exact 1s->p spectrum.

    Exact bound states through ``bound_n_max`` and a positive
    Gauss--Legendre continuum rule are retained.  The unresolved Rydberg
    tail is represented by one positive moment-matched node.  Its weight
    and transition energy close both the TRK sum and alpha(0)=4.5 a0^3;
    the independent raw infinite-sum/integral audit is performed by the
    PR-03 stage and is not inferred from this closure.
    """

    transition_hz: np.ndarray
    oscillator_weights: np.ndarray
    channel_code: np.ndarray
    channel_parameter: np.ndarray
    bound_n_max: int
    continuum_order: int
    tail_weight: float
    tail_delta_rydberg: float
    raw_bound_partial_sum: float
    raw_continuum_quadrature_sum: float

    @property
    def nu_alpha_hz(self) -> float:
        return float(self.transition_hz[0])

    @property
    def f_2p(self) -> float:
        return float(self.oscillator_weights[0])

    @property
    def trk_sum(self) -> float:
        return float(np.sum(self.oscillator_weights))

    @property
    def static_polarizability_a0_cubed(self) -> float:
        delta = self.transition_hz / RYDBERG_FREQUENCY_HZ
        return float(4.0 * np.sum(self.oscillator_weights / delta**2))

    @property
    def smooth_mask(self) -> np.ndarray:
        mask = np.ones(len(self.transition_hz), dtype=bool)
        mask[0] = False
        return mask


@lru_cache(maxsize=8)
def compile_oscillator_strength_measure(
    bound_n_max: int = 512,
    continuum_order: int = 256,
) -> OscillatorStrengthMeasure:
    if bound_n_max < 8:
        raise ValueError("bound_n_max must be at least 8")
    if continuum_order < 32:
        raise ValueError("continuum_order must be at least 32")

    bound_n = np.arange(2, bound_n_max + 1, dtype=float)
    bound_f = bound_oscillator_strength(bound_n)
    bound_delta = 1.0 - 1.0 / bound_n**2

    nodes, weights = leggauss(continuum_order)
    t = 0.5 * (nodes + 1.0)
    t_weight = 0.5 * weights
    continuum_n = t / (1.0 - t)
    jacobian = 1.0 / (1.0 - t) ** 2
    continuum_f_weight = (
        t_weight
        * jacobian
        * continuum_oscillator_strength_density(continuum_n)
    )
    continuum_delta = 1.0 + 1.0 / continuum_n**2

    raw_bound = float(np.sum(bound_f))
    raw_continuum = float(np.sum(continuum_f_weight))

    # Positive two-moment closure of the unresolved n>N Rydberg tail.
    tail_weight = 1.0 - raw_bound - raw_continuum
    partial_static_measure = float(
        np.sum(bound_f / bound_delta**2)
        + np.sum(continuum_f_weight / continuum_delta**2)
    )
    tail_static_measure = (
        STATIC_POLARIZABILITY_A0_CUBED / 4.0 - partial_static_measure
    )
    if tail_weight <= 0.0 or tail_static_measure <= 0.0:
        raise FloatingPointError("non-positive Rydberg-tail moment closure")
    tail_delta = math.sqrt(tail_weight / tail_static_measure)
    if not (bound_delta[-1] < tail_delta < 1.0 + 1.0e-12):
        raise FloatingPointError("Rydberg-tail effective energy is out of range")

    transition_delta = np.concatenate(
        (bound_delta, np.asarray([tail_delta]), continuum_delta)
    )
    oscillator_weights = np.concatenate(
        (bound_f, np.asarray([tail_weight]), continuum_f_weight)
    )
    # 0=exact bound state, 1=moment-matched Rydberg tail, 2=continuum node.
    channel_code = np.concatenate(
        (
            np.zeros(len(bound_n)),
            np.ones(1),
            np.full(len(continuum_n), 2.0),
        )
    )
    channel_parameter = np.concatenate(
        (bound_n, np.asarray([math.inf]), continuum_n)
    )

    measure = OscillatorStrengthMeasure(
        transition_hz=_readonly(transition_delta * RYDBERG_FREQUENCY_HZ),
        oscillator_weights=_readonly(oscillator_weights),
        channel_code=_readonly(channel_code),
        channel_parameter=_readonly(channel_parameter),
        bound_n_max=int(bound_n_max),
        continuum_order=int(continuum_order),
        tail_weight=float(tail_weight),
        tail_delta_rydberg=float(tail_delta),
        raw_bound_partial_sum=raw_bound,
        raw_continuum_quadrature_sum=raw_continuum,
    )
    if abs(measure.trk_sum - 1.0) > 8.0e-15:
        raise FloatingPointError("production measure does not close TRK")
    if abs(measure.static_polarizability_a0_cubed - 4.5) > 8.0e-14:
        raise FloatingPointError("production measure does not close alpha(0)")
    if np.min(measure.oscillator_weights) <= 0.0:
        raise FloatingPointError("oscillator-strength measure is not positive")
    return measure


@dataclass(frozen=True)
class ScalarCOMKHWModel:
    measure: OscillatorStrengthMeasure
    gamma_2p_half_hz: float = LY_ALPHA_GAMMA_HALF_HZ
    background_order: int = 4

    @classmethod
    def ly_alpha_production(cls) -> "ScalarCOMKHWModel":
        return cls(compile_oscillator_strength_measure())


@lru_cache(maxsize=8)
def default_scalar_com_khw_model() -> ScalarCOMKHWModel:
    return ScalarCOMKHWModel.ly_alpha_production()


def _stable_relativistic_kinetic_from_spatial(
    spatial_momentum: np.ndarray,
    mass_kg: float,
) -> float:
    p = np.asarray(spatial_momentum, dtype=float)
    if p.shape != (3,) or not np.all(np.isfinite(p)):
        raise ValueError("spatial momentum must be a finite 3-vector")
    p2 = float(p @ p)
    rest_energy = mass_kg * c**2
    total_energy = math.sqrt(rest_energy**2 + p2 * c**2)
    return p2 * c**2 / (total_energy + rest_energy)


def com_denominator_shifts_hz(
    atom_initial: np.ndarray,
    photon_initial: np.ndarray,
    photon_final: np.ndarray,
    mass_kg: float,
) -> tuple[float, float]:
    """Return the inherited common-mass COM kinetic shifts in Hz.

    This helper is retained for the nonrelativistic Maxwellian pair-cell
    reduction, where the internal energy is additive and the hydrogen COM
    mass is fixed.  Direct event amplitudes use
    :func:`relativistic_com_denominators_hz` instead: there every
    intermediate internal state lies on its own mass shell, which closes
    PT reciprocity for a relativistic recoil event without subtracting
    rest energies.
    """
    atom = np.asarray(atom_initial, dtype=float)
    incoming = np.asarray(photon_initial, dtype=float)
    outgoing = np.asarray(photon_final, dtype=float)
    if atom.shape != (4,) or incoming.shape != (4,) or outgoing.shape != (4,):
        raise ValueError("all momenta must be four-vectors")
    if mass_kg <= 0.0 or not np.isfinite(mass_kg):
        raise ValueError("mass_kg must be positive and finite")
    base = _stable_relativistic_kinetic_from_spatial(atom[1:], mass_kg)
    absorption = _stable_relativistic_kinetic_from_spatial(
        atom[1:] + incoming[1:], mass_kg
    )
    emission = _stable_relativistic_kinetic_from_spatial(
        atom[1:] - outgoing[1:], mass_kg
    )
    return (float((absorption - base) / h), float((emission - base) / h))


def relativistic_com_denominators_hz(
    atom_initial: np.ndarray,
    photon_initial: np.ndarray,
    photon_final: np.ndarray,
    mass_kg: float,
    transition_hz: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    r"""State-resolved relativistic COM denominators divided by ``h``.

    For an intermediate state ``s`` with rest mass
    ``M_s=M_H+h nu_s/c^2``, this evaluates

    ``D_s^- = E_s(P_i+k_i)-E_H(P_i)-h nu_i`` and
    ``D_s^+ = E_s(P_i-k_f)-E_H(P_i)+h nu_f``.

    The difference is rationalized before the photon energy is combined,
    so no two atomic rest energies are subtracted.  Momentum and energy
    conservation then imply exact forward/PT-reverse denominator equality
    state by state (up to the rounding of the supplied event).
    """
    atom = np.asarray(atom_initial, dtype=float)
    incoming = np.asarray(photon_initial, dtype=float)
    outgoing = np.asarray(photon_final, dtype=float)
    transition = np.asarray(transition_hz, dtype=float)
    if atom.shape != (4,) or incoming.shape != (4,) or outgoing.shape != (4,):
        raise ValueError("all momenta must be four-vectors")
    if transition.ndim != 1 or np.any(transition <= 0.0):
        raise ValueError("transition_hz must be a positive one-dimensional array")
    if mass_kg <= 0.0 or not np.isfinite(mass_kg):
        raise ValueError("mass_kg must be positive and finite")

    p_initial = atom[1:]
    p_absorption = p_initial + incoming[1:]
    p_emission = p_initial - outgoing[1:]
    ground_rest_energy = mass_kg * c**2
    ground_energy = math.hypot(
        ground_rest_energy, c * float(np.linalg.norm(p_initial))
    )

    excited_mass = mass_kg + h * transition / c**2
    excited_rest_energy = excited_mass * c**2
    excited_absorption = np.hypot(
        excited_rest_energy, c * float(np.linalg.norm(p_absorption))
    )
    excited_emission = np.hypot(
        excited_rest_energy, c * float(np.linalg.norm(p_emission))
    )

    mass_square_difference = (
        excited_rest_energy - ground_rest_energy
    ) * (excited_rest_energy + ground_rest_energy)
    momentum_square_initial = float(p_initial @ p_initial)
    absorption_square_difference = (
        float(p_absorption @ p_absorption) - momentum_square_initial
    ) * c**2
    emission_square_difference = (
        float(p_emission @ p_emission) - momentum_square_initial
    ) * c**2
    photon_in_energy = c * float(incoming[0])
    photon_out_energy = c * float(outgoing[0])

    absorption_sum = excited_absorption + ground_energy
    emission_sum = excited_emission + ground_energy
    dminus_energy = (
        mass_square_difference
        + absorption_square_difference
        - photon_in_energy * absorption_sum
    ) / absorption_sum
    dplus_energy = (
        mass_square_difference
        + emission_square_difference
        + photon_out_energy * emission_sum
    ) / emission_sum
    dminus = dminus_energy / h
    dplus = dplus_energy / h
    if np.any(~np.isfinite(dminus)) or np.any(~np.isfinite(dplus)):
        raise FloatingPointError("non-finite relativistic COM denominator")
    return np.asarray(dminus, dtype=float), np.asarray(dplus, dtype=float)

def scalar_com_khw_amplitude(
    nu_in_hz: float,
    nu_out_hz: float,
    shift_minus_hz: float = 0.0,
    shift_plus_hz: float = 0.0,
    *,
    model: ScalarCOMKHWModel | None = None,
    include_2p_width: bool = True,
) -> complex:
    """Evaluate the direct finite-measure scalar COM--KHW amplitude."""
    if model is None:
        model = default_scalar_com_khw_model()
    if nu_in_hz <= 0.0 or nu_out_hz <= 0.0:
        raise ValueError("photon frequencies must be positive")
    measure = model.measure
    transition = measure.transition_hz
    weights = measure.oscillator_weights
    widths = np.zeros_like(transition)
    if include_2p_width:
        widths[0] = model.gamma_2p_half_hz
    dminus = transition + shift_minus_hz - nu_in_hz - 1j * widths
    dplus = transition + shift_plus_hz + nu_out_hz + 1j * widths
    if np.any(np.abs(dminus[1:]) == 0.0) or np.any(np.abs(dplus[1:]) == 0.0):
        raise ZeroDivisionError("undamped higher-state resonance encountered")
    value = 1.0 - 0.5 * np.sum(
        weights * transition * (1.0 / dminus + 1.0 / dplus)
    )
    return complex(value)


def scalar_event_com_khw_amplitude(
    atom_initial: np.ndarray,
    photon_initial: np.ndarray,
    photon_final: np.ndarray,
    mass_kg: float,
    *,
    model: ScalarCOMKHWModel | None = None,
    include_2p_width: bool = True,
) -> complex:
    """Evaluate the state-resolved relativistic event amplitude."""
    if model is None:
        model = default_scalar_com_khw_model()
    dminus, dplus = relativistic_com_denominators_hz(
        atom_initial,
        photon_initial,
        photon_final,
        mass_kg,
        model.measure.transition_hz,
    )
    widths = np.zeros_like(dminus)
    if include_2p_width:
        widths[0] = model.gamma_2p_half_hz
    value = 1.0 - 0.5 * np.sum(
        model.measure.oscillator_weights
        * model.measure.transition_hz
        * (1.0 / (dminus - 1j * widths) + 1.0 / (dplus + 1j * widths))
    )
    return complex(value)


def fixed_nucleus_length_gauge_amplitude(
    nu_hz: float,
    *,
    model: ScalarCOMKHWModel | None = None,
) -> float:
    """TRK-rearranged zero-width elastic amplitude.

    This is the length-gauge/dynamic-polarizability form used solely for
    the gauge and infrared audit away from a discrete resonance.
    """
    if model is None:
        model = default_scalar_com_khw_model()
    transition = model.measure.transition_hz
    weights = model.measure.oscillator_weights
    denominator = transition**2 - nu_hz**2
    if np.any(denominator == 0.0):
        raise ZeroDivisionError("length-gauge audit requested at a resonance")
    return float(-nu_hz**2 * np.sum(weights / denominator))


@dataclass(frozen=True)
class SmoothBackgroundSeries:
    order: int
    absorption_coefficients: np.ndarray
    emission_coefficients: np.ndarray
    emission_center_hz: float
    direct_measure_size: int


@lru_cache(maxsize=16)
def compile_smooth_background_series(
    order: int = 8,
    bound_n_max: int = 512,
    continuum_order: int = 256,
) -> SmoothBackgroundSeries:
    if order < 2 or order > 16:
        raise ValueError("background order must lie in [2,16]")
    measure = compile_oscillator_strength_measure(
        bound_n_max, continuum_order
    )
    transition = measure.transition_hz[1:]
    weight = measure.oscillator_weights[1:]
    delta = transition - measure.nu_alpha_hz
    emission_denominator = transition + measure.nu_alpha_hz
    absorption = []
    emission = []
    for power in range(order + 1):
        sign = -0.5 * ((-1.0) ** power)
        absorption.append(
            sign * float(np.sum(weight * transition / delta ** (power + 1)))
        )
        emission.append(
            sign
            * float(
                np.sum(
                    weight * transition / emission_denominator ** (power + 1)
                )
            )
        )
    return SmoothBackgroundSeries(
        order=order,
        absorption_coefficients=_readonly(np.asarray(absorption)),
        emission_coefficients=_readonly(np.asarray(emission)),
        emission_center_hz=2.0 * measure.nu_alpha_hz,
        direct_measure_size=len(measure.transition_hz),
    )


def _compose_power_series(
    coefficients: np.ndarray,
    shift: np.ndarray,
    slope: np.ndarray,
) -> np.ndarray:
    """Coefficients in z of sum_k c_k (shift+slope*z)^k."""
    shift, slope = np.broadcast_arrays(
        np.asarray(shift, dtype=float), np.asarray(slope, dtype=float)
    )
    order = len(coefficients) - 1
    output = np.zeros((order + 1,) + shift.shape, dtype=float)
    for k_value, coefficient in enumerate(coefficients):
        for power in range(k_value + 1):
            output[power] += (
                coefficient
                * math.comb(k_value, power)
                * shift ** (k_value - power)
                * slope**power
            )
    return output


def smooth_background_polynomial(
    A_hz: np.ndarray,
    B_hz: np.ndarray,
    C_hz: np.ndarray,
    D_hz: np.ndarray,
    *,
    series: SmoothBackgroundSeries | None = None,
) -> np.ndarray:
    """Return h_m for H(z)=sum_m h_m z^m.

    ``H`` contains the seagull and every bound/continuum channel except
    the 2p pole and its crossed denominator, which remain in the exact
    Faddeeva lane.
    """
    if series is None:
        series = compile_smooth_background_series()
    absorption = _compose_power_series(
        series.absorption_coefficients, A_hz, B_hz
    )
    emission = _compose_power_series(
        series.emission_coefficients,
        np.asarray(C_hz, dtype=float) - series.emission_center_hz,
        D_hz,
    )
    result = absorption + emission
    result[0] += 1.0
    return result


def direct_smooth_background(
    A_hz: float | np.ndarray,
    B_hz: float | np.ndarray,
    C_hz: float | np.ndarray,
    D_hz: float | np.ndarray,
    z_value: float | np.ndarray,
    *,
    model: ScalarCOMKHWModel | None = None,
) -> np.ndarray:
    """Direct bound+continuum smooth background for validation."""
    if model is None:
        model = default_scalar_com_khw_model()
    A, B, C, D, z = np.broadcast_arrays(
        np.asarray(A_hz, dtype=float),
        np.asarray(B_hz, dtype=float),
        np.asarray(C_hz, dtype=float),
        np.asarray(D_hz, dtype=float),
        np.asarray(z_value, dtype=float),
    )
    transition = model.measure.transition_hz[1:]
    weight = model.measure.oscillator_weights[1:]
    delta = transition - model.measure.nu_alpha_hz
    result = np.ones(A.shape, dtype=float)
    flat_result = result.reshape(-1)
    flat_A, flat_B, flat_C, flat_D, flat_z = (
        value.reshape(-1) for value in (A, B, C, D, z)
    )
    for index in range(len(flat_result)):
        dminus = delta + flat_A[index] + flat_B[index] * flat_z[index]
        dplus = delta + flat_C[index] + flat_D[index] * flat_z[index]
        flat_result[index] -= 0.5 * float(
            np.sum(weight * transition * (1.0 / dminus + 1.0 / dplus))
        )
    return result


def _normal_moments(max_order: int) -> np.ndarray:
    output = np.zeros(max_order + 1, dtype=float)
    output[0] = 1.0
    for power in range(2, max_order + 1, 2):
        output[power] = output[power - 2] * (power - 1)
    return output


def _gaussian_resolvent_array(pole: np.ndarray) -> np.ndarray:
    p = np.asarray(pole, dtype=complex)
    output = np.empty_like(p)
    upper = p.imag > 0.0
    lower = p.imag < 0.0
    if np.any(~(upper | lower)):
        raise ValueError("Gaussian resolvent requires non-real poles")
    output[upper] = (
        1j * math.sqrt(math.pi / 2.0) * wofz(p[upper] / math.sqrt(2.0))
    )
    output[lower] = (
        -1j
        * math.sqrt(math.pi / 2.0)
        * wofz(-p[lower] / math.sqrt(2.0))
    )
    return output


def _linear_inverse_mean(offset: np.ndarray, slope: np.ndarray) -> np.ndarray:
    offset, slope = np.broadcast_arrays(
        np.asarray(offset, dtype=complex), np.asarray(slope, dtype=float)
    )
    result = np.empty(offset.shape, dtype=complex)
    zero = np.abs(slope) < 1.0e-300
    result[zero] = 1.0 / offset[zero]
    nonzero = ~zero
    if np.any(nonzero):
        pole = -offset[nonzero] / slope[nonzero]
        result[nonzero] = _gaussian_resolvent_array(pole) / slope[nonzero]
    return result


def _linear_inverse_moments(
    offset: np.ndarray,
    slope: np.ndarray,
    max_order: int,
) -> np.ndarray:
    """E[Z^m/(offset+slope Z)] with a stable far-pole branch."""
    offset, slope = np.broadcast_arrays(
        np.asarray(offset, dtype=complex), np.asarray(slope, dtype=float)
    )
    original_shape = offset.shape
    offset_flat = offset.reshape(-1)
    slope_flat = slope.reshape(-1)
    output = np.zeros((max_order + 1, offset_flat.size), dtype=complex)
    moments = _normal_moments(max_order + 32)
    zero = np.abs(slope_flat) < 1.0e-300
    if np.any(zero):
        for power in range(max_order + 1):
            output[power, zero] = moments[power] / offset_flat[zero]

    nonzero = ~zero
    if not np.any(nonzero):
        return output.reshape((max_order + 1,) + original_shape)
    far = nonzero & (np.abs(slope_flat / offset_flat) < 1.0e-3)
    near = nonzero & ~far

    if np.any(far):
        ratio = -slope_flat[far] / offset_flat[far]
        for power in range(max_order + 1):
            total = np.zeros(np.count_nonzero(far), dtype=complex)
            term = np.ones_like(total)
            # 24 terms are excessive for |s/o|<1e-3 and retain a wide
            # margin for moments through order 16.
            for extra in range(25):
                total += term * moments[power + extra]
                term *= ratio
            output[power, far] = total / offset_flat[far]

    if np.any(near):
        output[0, near] = _linear_inverse_mean(
            offset_flat[near], slope_flat[near]
        )
        for power in range(1, max_order + 1):
            output[power, near] = (
                moments[power - 1] / slope_flat[near]
                - (offset_flat[near] / slope_flat[near])
                * output[power - 1, near]
            )
    return output.reshape((max_order + 1,) + original_shape)


def _lorentzian_mean(
    detuning: np.ndarray, slope: np.ndarray, gamma: float
) -> np.ndarray:
    detuning, slope = np.broadcast_arrays(
        np.asarray(detuning, dtype=float), np.asarray(slope, dtype=float)
    )
    output = np.empty(detuning.shape, dtype=float)
    zero = np.abs(slope) < 1.0e-300
    output[zero] = 1.0 / (detuning[zero] ** 2 + gamma**2)
    nonzero = ~zero
    if np.any(nonzero):
        x = detuning[nonzero] / (math.sqrt(2.0) * slope[nonzero])
        a = gamma / (math.sqrt(2.0) * np.abs(slope[nonzero]))
        output[nonzero] = (
            math.sqrt(math.pi)
            / (math.sqrt(2.0) * np.abs(slope[nonzero]) * gamma)
            * np.real(wofz(x + 1j * a))
        )
    return output


def _product_inverse_mean(
    offset_one: np.ndarray,
    slope_one: np.ndarray,
    offset_two: np.ndarray,
    slope_two: np.ndarray,
) -> np.ndarray:
    o1, s1, o2, s2 = np.broadcast_arrays(
        np.asarray(offset_one, dtype=complex),
        np.asarray(slope_one, dtype=float),
        np.asarray(offset_two, dtype=complex),
        np.asarray(slope_two, dtype=float),
    )
    result = np.empty(o1.shape, dtype=complex)
    z1 = np.abs(s1) < 1.0e-300
    z2 = np.abs(s2) < 1.0e-300
    both = z1 & z2
    result[both] = 1.0 / (o1[both] * o2[both])
    only1 = z1 & ~z2
    result[only1] = _linear_inverse_mean(o2[only1], s2[only1]) / o1[only1]
    only2 = ~z1 & z2
    result[only2] = _linear_inverse_mean(o1[only2], s1[only2]) / o2[only2]
    regular = ~z1 & ~z2
    if np.any(regular):
        denominator = s1[regular] * o2[regular] - s2[regular] * o1[regular]
        pole1 = -o1[regular] / s1[regular]
        pole2 = -o2[regular] / s2[regular]
        result[regular] = (
            _gaussian_resolvent_array(pole1)
            - _gaussian_resolvent_array(pole2)
        ) / denominator
    return result


def conditional_full_scalar_mean_amplitude_squared(
    A_hz: np.ndarray,
    B_hz: np.ndarray,
    C_hz: np.ndarray,
    D_hz: np.ndarray,
    *,
    model: ScalarCOMKHWModel | None = None,
    series: SmoothBackgroundSeries | None = None,
) -> np.ndarray:
    """Conditional Gaussian mean of the complete scalar amplitude.

    ``A+B Z-i gamma`` and ``C+D Z+i gamma`` are the unresolved 2p
    absorption and crossed denominators.  Every other bound/continuum
    state, the seagull, and all their interference terms are included by
    the exact-measure smooth polynomial.
    """
    if model is None:
        model = default_scalar_com_khw_model()
    if series is None:
        series = compile_smooth_background_series(model.background_order)
    A, B, C, D = np.broadcast_arrays(
        np.asarray(A_hz, dtype=float),
        np.asarray(B_hz, dtype=float),
        np.asarray(C_hz, dtype=float),
        np.asarray(D_hz, dtype=float),
    )
    gamma = model.gamma_2p_half_hz
    scale = -0.5 * model.measure.f_2p * model.measure.nu_alpha_hz
    scale2 = scale * scale

    pole = scale2 * _lorentzian_mean(A, B, gamma)
    crossed = scale2 * _lorentzian_mean(C, D, gamma)
    cross = _product_inverse_mean(
        A - 1j * gamma,
        B,
        C - 1j * gamma,
        D,
    )
    resonant_squared = pole + crossed + 2.0 * scale2 * np.real(cross)

    h_coeff = smooth_background_polynomial(A, B, C, D, series=series)
    order = series.order
    pole_moments = _linear_inverse_moments(
        A - 1j * gamma, B, order
    )
    crossed_moments = _linear_inverse_moments(
        C + 1j * gamma, D, order
    )
    resonant_moments = scale * (pole_moments + crossed_moments)

    cross_background = np.zeros(A.shape, dtype=complex)
    for power in range(order + 1):
        cross_background += resonant_moments[power] * h_coeff[power]

    gaussian_moments = _normal_moments(2 * order)
    background_squared = np.zeros(A.shape, dtype=float)
    for left in range(order + 1):
        for right in range(order + 1):
            background_squared += (
                h_coeff[left]
                * h_coeff[right]
                * gaussian_moments[left + right]
            )

    total = (
        resonant_squared
        + 2.0 * np.real(cross_background)
        + background_squared
    )
    if np.any(~np.isfinite(total)) or np.any(total <= 0.0):
        raise FloatingPointError("non-positive complete conditional amplitude mean")
    return total


def conditional_full_minus_provisional_mean_amplitude_squared(
    A_hz: np.ndarray,
    B_hz: np.ndarray,
    C_hz: np.ndarray,
    D_hz: np.ndarray,
    *,
    model: ScalarCOMKHWModel | None = None,
    series: SmoothBackgroundSeries | None = None,
) -> np.ndarray:
    """Conditional complete-minus-2p response without pole subtraction.

    The correction is evaluated analytically as the resonant--smooth
    interference plus the smooth-background square.  It therefore avoids
    subtracting two nearly equal, resonance-dominated positive quantities and
    is the control-variate lane used when regenerating the v0.50 moments.
    The correction itself may have either sign; only the complete response is
    required to be positive.
    """
    if model is None:
        model = default_scalar_com_khw_model()
    if series is None:
        series = compile_smooth_background_series(model.background_order)
    A, B, C, D = np.broadcast_arrays(
        np.asarray(A_hz, dtype=float),
        np.asarray(B_hz, dtype=float),
        np.asarray(C_hz, dtype=float),
        np.asarray(D_hz, dtype=float),
    )
    gamma = model.gamma_2p_half_hz
    scale = -0.5 * model.measure.f_2p * model.measure.nu_alpha_hz
    h_coeff = smooth_background_polynomial(A, B, C, D, series=series)
    order = series.order
    pole_moments = _linear_inverse_moments(A - 1j * gamma, B, order)
    crossed_moments = _linear_inverse_moments(C + 1j * gamma, D, order)
    resonant_moments = scale * (pole_moments + crossed_moments)

    cross_background = np.zeros(A.shape, dtype=complex)
    for power in range(order + 1):
        cross_background += resonant_moments[power] * h_coeff[power]

    gaussian_moments = _normal_moments(2 * order)
    background_squared = np.zeros(A.shape, dtype=float)
    for left in range(order + 1):
        for right in range(order + 1):
            background_squared += (
                h_coeff[left]
                * h_coeff[right]
                * gaussian_moments[left + right]
            )
    correction = 2.0 * np.real(cross_background) + background_squared
    if np.any(~np.isfinite(correction)):
        raise FloatingPointError("non-finite complete-minus-provisional correction")
    return correction


def conditional_provisional_mean_amplitude_squared(
    A_hz: np.ndarray,
    B_hz: np.ndarray,
    C_hz: np.ndarray,
    D_hz: np.ndarray,
    *,
    model: ScalarCOMKHWModel | None = None,
) -> np.ndarray:
    """Separated inherited 2p pole+crossed reference lane."""
    if model is None:
        model = default_scalar_com_khw_model()
    A, B, C, D = np.broadcast_arrays(
        np.asarray(A_hz, dtype=float),
        np.asarray(B_hz, dtype=float),
        np.asarray(C_hz, dtype=float),
        np.asarray(D_hz, dtype=float),
    )
    gamma = model.gamma_2p_half_hz
    scale = -0.5 * model.measure.f_2p * model.measure.nu_alpha_hz
    scale2 = scale * scale
    cross = _product_inverse_mean(
        A - 1j * gamma, B, C - 1j * gamma, D
    )
    total = (
        scale2 * _lorentzian_mean(A, B, gamma)
        + scale2 * _lorentzian_mean(C, D, gamma)
        + 2.0 * scale2 * np.real(cross)
    )
    if np.any(~np.isfinite(total)) or np.any(total <= 0.0):
        raise FloatingPointError("non-positive provisional amplitude mean")
    return total


def invariant_full_khw_response_area(
    atom_initial: np.ndarray,
    photon_initial: np.ndarray,
    photon_final: np.ndarray,
    mass_kg: float,
    mu_rest: float,
    nu_in_rest_hz: float,
    nu_out_rest_hz: float,
    *,
    model: ScalarCOMKHWModel | None = None,
) -> float:
    """Positive scalar response using the complete COM amplitude.

    The amplitude is evaluated in the supplied event tetrad with exact
    COM shifts.  The conventional ``nu_out*/nu_in*`` phase-space factor
    uses the initial-hydrogen rest-frame frequencies supplied by the
    event layer.
    """
    amplitude = scalar_event_com_khw_amplitude(
        atom_initial,
        photon_initial,
        photon_final,
        mass_kg,
        model=model,
    )
    phase = 0.75 * (1.0 + float(np.clip(mu_rest, -1.0, 1.0)) ** 2)
    sigma_t = physical_constants["Thomson cross section"][0]
    response = (
        sigma_t
        * phase
        * (nu_out_rest_hz / nu_in_rest_hz)
        * abs(amplitude) ** 2
    )
    if response <= 0.0 or not np.isfinite(response):
        raise FloatingPointError("non-positive complete scalar event response")
    return float(response)


def denominator_reciprocity_residuals(
    forward_atom: np.ndarray,
    forward_in: np.ndarray,
    forward_out: np.ndarray,
    reverse_atom: np.ndarray,
    reverse_in: np.ndarray,
    reverse_out: np.ndarray,
    mass_kg: float,
    *,
    model: ScalarCOMKHWModel | None = None,
) -> tuple[float, float]:
    """Maximum statewise forward/PT-reverse denominator residuals."""
    if model is None:
        model = default_scalar_com_khw_model()
    forward = relativistic_com_denominators_hz(
        forward_atom,
        forward_in,
        forward_out,
        mass_kg,
        model.measure.transition_hz,
    )
    reverse = relativistic_com_denominators_hz(
        reverse_atom,
        reverse_in,
        reverse_out,
        mass_kg,
        model.measure.transition_hz,
    )
    output = []
    for left, right in zip(forward, reverse):
        scale = np.maximum.reduce(
            (np.abs(left), np.abs(right), np.ones_like(left))
        )
        output.append(float(np.max(np.abs(left - right) / scale)))
    return (output[0], output[1])


__all__ = [
    "LY_ALPHA_FREQUENCY_HZ",
    "LY_ALPHA_GAMMA_HALF_HZ",
    "LY_ALPHA_OSCILLATOR_STRENGTH",
    "RYDBERG_FREQUENCY_HZ",
    "OscillatorStrengthMeasure",
    "ScalarCOMKHWModel",
    "SmoothBackgroundSeries",
    "bound_oscillator_strength",
    "continuum_oscillator_strength_density",
    "compile_oscillator_strength_measure",
    "compile_smooth_background_series",
    "default_scalar_com_khw_model",
    "com_denominator_shifts_hz",
    "relativistic_com_denominators_hz",
    "scalar_com_khw_amplitude",
    "scalar_event_com_khw_amplitude",
    "fixed_nucleus_length_gauge_amplitude",
    "smooth_background_polynomial",
    "direct_smooth_background",
    "conditional_full_scalar_mean_amplitude_squared",
    "conditional_full_minus_provisional_mean_amplitude_squared",
    "conditional_provisional_mean_amplitude_squared",
    "invariant_full_khw_response_area",
    "denominator_reciprocity_residuals",
]

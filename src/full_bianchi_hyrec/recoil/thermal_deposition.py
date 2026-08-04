"""Maxwell--Jüttner line-centre event integration and positive deposition.

This bounded PR-01B1-B0 slice integrates one incoming Ly-alpha
frequency cell.  It uses exact PR-01A recoil kinematics, the PR-01B1-A
scalar 2p response, randomized Sobol importance sampling, and the
v0.32 no-recoil Hummer column as a common-random-number control
variate.

The output is a positive red/interior/blue deposition and a shared
equilibrium conductance star.  It is not the complete 17x17 full-angle
kernel.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from pathlib import Path

import numpy as np
from scipy.constants import c, h, k, physical_constants
from scipy.special import kve, ndtri
from scipy.stats import qmc


_M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
_NU_ALPHA = c / (1215.6701e-10)
_A21 = 6.265e8
_F12 = 0.4161967179799824
_GAMMA_HZ = _A21 / (4.0 * math.pi)
_SIGMA_T = physical_constants["Thomson cross section"][0]
_R_E = physical_constants["classical electron radius"][0]


@dataclass(frozen=True)
class DepositionConfig:
    temperature_K: float = 3000.0
    n1s_cm3: float = 250.0
    source_x_left: float = -0.25
    source_x_right: float = 0.25
    sobol_power: int = 18
    seeds: tuple[int, ...] = (1, 2, 3, 4)
    gaussian_mixture_weight: float = 0.5
    cauchy_scale_factor: float = 1.0
    cauchy_truncation_sigma: float = 12.0


@dataclass(frozen=True)
class LineCenterDepositionResult:
    x_edges: np.ndarray
    x_centers: np.ndarray
    center_index: int
    inside_rate_s_inv: np.ndarray
    red_exterior_rate_s_inv: float
    blue_exterior_rate_s_inv: float
    total_rate_s_inv: float
    total_rate_seed_std_s_inv: float
    hummer_total_rate_s_inv: float
    recoil_increment_M1_x: float
    recoil_increment_seed_std_x: float
    continuous_M1_x: float
    continuous_M2_x2: float
    maxwell_juttner_vs_mb_relative: float
    pair_balance_relative: float
    generator_left_null: float
    equilibrium_right_null: float
    photon_four_force_per_photon: np.ndarray
    hydrogen_four_force_per_photon: np.ndarray
    control_variate_column_seed_spread: float
    oscillator_area_correction: float


def _reference_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "line_center_hummer_reference.npz"


def oscillator_area_correction() -> tuple[float, float]:
    """Return the source-derived area correction and A21 implied by f12.

    The adopted natural width and oscillator strength differ at the
    5e-4 level.  Multiplying the response by A21_input/A21(f12) preserves
    the oscillator-strength area while retaining the adopted width.
    """
    a21_from_f = (
        8.0
        * math.pi**2
        * _R_E
        * _F12
        * _NU_ALPHA**2
        / (3.0 * c)
    )
    return _A21 / a21_from_f, a21_from_f


def analytic_rayleigh_recoil_mean(
    g_recoil: float,
    b_d: float,
    *,
    order: int = 512,
) -> float:
    """Exact Rayleigh-phase mean rest-frame recoil shift in Doppler units."""
    nodes, weights = np.polynomial.legendre.leggauss(order)
    probability = 3.0 / 8.0 * (1.0 + nodes * nodes)
    shift = (
        -g_recoil
        * (1.0 - nodes)
        / (1.0 + g_recoil * b_d * (1.0 - nodes))
    )
    return float(np.dot(weights, probability * shift))


def _sample_rayleigh_mu(uniform: np.ndarray) -> np.ndarray:
    """Invert F(mu)=1/2+3mu/8+mu^3/8 by Newton iteration."""
    mu = 2.0 * uniform - 1.0
    for _ in range(7):
        residual = mu**3 + 3.0 * mu + 4.0 - 8.0 * uniform
        mu -= residual / (3.0 * mu**2 + 3.0)
    return np.clip(mu, -1.0, 1.0)


def _scaled_k2_large_z(z_value: float) -> float:
    value = float(kve(2, z_value))
    if np.isfinite(value) and value > 0.0:
        return value
    return math.sqrt(math.pi / (2.0 * z_value)) * (
        1.0
        + 15.0 / (8.0 * z_value)
        + 105.0 / (128.0 * z_value**2)
    )


def _sample_seed(
    config: DepositionConfig,
    seed: int,
    reference: dict[str, np.ndarray | float | int],
):
    temperature = config.temperature_K
    mass = _M_H
    sigma_beta = math.sqrt(k * temperature / mass) / c
    b_d = math.sqrt(2.0) * sigma_beta
    delta_nu = _NU_ALPHA * b_d

    sobol = qmc.Sobol(d=6, scramble=True, seed=int(seed))
    uniform = sobol.random_base2(config.sobol_power)
    machine = np.finfo(float).eps
    uniform = np.clip(uniform, machine, 1.0 - machine)
    count = len(uniform)

    x_in = (
        config.source_x_left
        + (config.source_x_right - config.source_x_left) * uniform[:, 5]
    )
    nu_in = _NU_ALPHA + x_in * delta_nu

    beta_x = sigma_beta * ndtri(uniform[:, 1])
    beta_y = sigma_beta * ndtri(uniform[:, 2])

    resonance_center = x_in * b_d
    scale = config.cauchy_scale_factor * _GAMMA_HZ / _NU_ALPHA
    mixture = config.gaussian_mixture_weight
    gaussian_component = uniform[:, 0] < mixture
    conditional = np.empty(count)
    conditional[gaussian_component] = (
        uniform[gaussian_component, 0] / mixture
    )
    conditional[~gaussian_component] = (
        uniform[~gaussian_component, 0] - mixture
    ) / (1.0 - mixture)

    beta_z = np.empty(count)
    beta_z[gaussian_component] = (
        sigma_beta * ndtri(conditional[gaussian_component])
    )

    truncation = config.cauchy_truncation_sigma * sigma_beta
    cauchy_angle = math.atan(truncation / scale)
    beta_z[~gaussian_component] = (
        resonance_center[~gaussian_component]
        + scale
        * np.tan(
            (2.0 * conditional[~gaussian_component] - 1.0)
            * cauchy_angle
        )
    )

    beta = np.column_stack((beta_x, beta_y, beta_z))
    beta2 = np.einsum("ij,ij->i", beta, beta)
    if np.any(beta2 >= 1.0):
        raise FloatingPointError("superluminal importance sample")
    gamma = 1.0 / np.sqrt(1.0 - beta2)

    # Incoming lab direction is +z. Transform it to the atom rest frame.
    doppler_in = gamma * (1.0 - beta_z)
    nu_in_rest = doppler_in * nu_in

    coefficient = np.zeros(count)
    nonzero = beta2 > 0.0
    coefficient[nonzero] = (
        (gamma[nonzero] - 1.0)
        * beta_z[nonzero]
        / beta2[nonzero]
        - gamma[nonzero]
    )
    n_in_rest = np.zeros_like(beta)
    n_in_rest[:, 2] = 1.0
    n_in_rest += coefficient[:, None] * beta
    n_in_rest /= doppler_in[:, None]
    n_in_rest /= np.linalg.norm(n_in_rest, axis=1)[:, None]

    # Orthonormal screen basis around the rest-frame incoming direction.
    reference_axis = np.tile(np.array([1.0, 0.0, 0.0]), (count, 1))
    alternate = np.abs(n_in_rest[:, 0]) > 0.9
    reference_axis[alternate] = np.array([0.0, 1.0, 0.0])
    e1 = np.cross(n_in_rest, reference_axis)
    e1 /= np.linalg.norm(e1, axis=1)[:, None]
    e2 = np.cross(n_in_rest, e1)

    mu = _sample_rayleigh_mu(uniform[:, 3])
    azimuth = 2.0 * math.pi * uniform[:, 4]
    sine = np.sqrt(1.0 - mu * mu)
    n_out_rest = (
        mu[:, None] * n_in_rest
        + sine[:, None]
        * (
            np.cos(azimuth)[:, None] * e1
            + np.sin(azimuth)[:, None] * e2
        )
    )

    epsilon = h * nu_in_rest / (mass * c**2)
    nu_out_rest = nu_in_rest / (
        1.0 + epsilon * (1.0 - mu)
    )
    nu_out_rest_no_recoil = nu_in_rest

    beta_dot_out = np.einsum("ij,ij->i", beta, n_out_rest)
    doppler_out = gamma * (1.0 + beta_dot_out)
    nu_out = doppler_out * nu_out_rest
    nu_out_no_recoil = doppler_out * nu_out_rest_no_recoil

    coefficient_out = np.zeros(count)
    coefficient_out[nonzero] = (
        (gamma[nonzero] - 1.0)
        * beta_dot_out[nonzero]
        / beta2[nonzero]
        + gamma[nonzero]
    )
    n_out_lab = (
        n_out_rest + coefficient_out[:, None] * beta
    ) / doppler_out[:, None]
    n_out_lab /= np.linalg.norm(n_out_lab, axis=1)[:, None]

    amplitude = -0.5 * _F12 * _NU_ALPHA * (
        1.0
        / (_NU_ALPHA - nu_in_rest - 1j * _GAMMA_HZ)
        + 1.0
        / (_NU_ALPHA + nu_out_rest + 1j * _GAMMA_HZ)
    )
    amplitude_no_recoil = -0.5 * _F12 * _NU_ALPHA * (
        1.0
        / (_NU_ALPHA - nu_in_rest - 1j * _GAMMA_HZ)
        + 1.0
        / (_NU_ALPHA + nu_out_rest_no_recoil + 1j * _GAMMA_HZ)
    )

    area_correction, _ = oscillator_area_correction()
    cross_section = (
        area_correction
        * _SIGMA_T
        * (nu_out_rest / nu_in_rest)
        * np.abs(amplitude) ** 2
    )
    cross_section_no_recoil = (
        area_correction
        * _SIGMA_T
        * np.abs(amplitude_no_recoil) ** 2
    )

    # Exact Maxwell--Jüttner target density with respect to d^3 beta.
    theta = k * temperature / (mass * c**2)
    z_value = 1.0 / theta
    scaled_k2 = _scaled_k2_large_z(z_value)
    log_norm_p = (
        math.log(4.0 * math.pi)
        + 3.0 * math.log(mass * c)
        + math.log(theta)
        + math.log(scaled_k2)
    )
    kinetic = (gamma - 1.0) * mass * c**2
    log_target_beta = (
        -kinetic / (k * temperature)
        - log_norm_p
        + 3.0 * math.log(mass * c)
        + 5.0 * np.log(gamma)
    )

    log_gaussian_x = (
        -0.5 * (beta_x / sigma_beta) ** 2
        - math.log(math.sqrt(2.0 * math.pi) * sigma_beta)
    )
    log_gaussian_y = (
        -0.5 * (beta_y / sigma_beta) ** 2
        - math.log(math.sqrt(2.0 * math.pi) * sigma_beta)
    )
    gaussian_z = (
        np.exp(-0.5 * (beta_z / sigma_beta) ** 2)
        / (math.sqrt(2.0 * math.pi) * sigma_beta)
    )
    cauchy_normalization = 2.0 * cauchy_angle / math.pi
    displacement = beta_z - resonance_center
    cauchy_z = np.where(
        np.abs(displacement) <= truncation,
        scale
        / (
            math.pi * (displacement**2 + scale**2)
            * cauchy_normalization
        ),
        0.0,
    )
    proposal_z = mixture * gaussian_z + (1.0 - mixture) * cauchy_z
    log_proposal = log_gaussian_x + log_gaussian_y + np.log(proposal_z)
    mj_importance = np.exp(log_target_beta - log_proposal)

    # Maxwell--Boltzmann comparison target with respect to d^3 beta.
    mb_importance = gaussian_z / proposal_z

    # Average source-cell occupation is weighted by the photon mode density nu^2.
    lower_nu = _NU_ALPHA + config.source_x_left * delta_nu
    upper_nu = _NU_ALPHA + config.source_x_right * delta_nu
    mean_nu_squared = (
        (upper_nu**3 - lower_nu**3)
        / (3.0 * (upper_nu - lower_nu))
    )
    photon_mode_weight = nu_in**2 / mean_nu_squared

    relative_flux = c * (1.0 - beta_z)
    density_m3 = config.n1s_cm3 * 1.0e6
    common = (
        density_m3
        * relative_flux
        * photon_mode_weight
    )

    exact_weight = common * cross_section * mj_importance
    no_recoil_weight = (
        common * cross_section_no_recoil * mj_importance
    )
    mb_weight = common * cross_section * mb_importance

    x_out = (nu_out - _NU_ALPHA) / delta_nu
    x_out_no_recoil = (
        nu_out_no_recoil - _NU_ALPHA
    ) / delta_nu

    # Momentum transfer per event, p=(h nu/c)(1,n).
    incoming_direction = np.zeros_like(n_out_lab)
    incoming_direction[:, 2] = 1.0
    scale_in = h * nu_in / c
    scale_out = h * nu_out / c
    delta_photon = np.empty((count, 4))
    delta_photon[:, 0] = scale_out - scale_in
    delta_photon[:, 1:] = (
        scale_out[:, None] * n_out_lab
        - scale_in[:, None] * incoming_direction
    )

    edges = np.asarray(reference["x_edges"])
    cell_exact = np.searchsorted(edges, x_out, side="right") - 1
    cell_baseline = (
        np.searchsorted(edges, x_out_no_recoil, side="right") - 1
    )

    return {
        "exact_weight": exact_weight,
        "baseline_weight": no_recoil_weight,
        "mb_weight": mb_weight,
        "x_in": x_in,
        "x_out": x_out,
        "x_out_no_recoil": x_out_no_recoil,
        "mu_rest": mu,
        "mu_lab": n_out_lab[:, 2],
        "cell_exact": cell_exact,
        "cell_baseline": cell_baseline,
        "delta_photon": delta_photon,
    }


@lru_cache(maxsize=32)
def line_center_column(
    config: DepositionConfig = DepositionConfig(),
) -> LineCenterDepositionResult:
    if not config.seeds:
        raise ValueError("at least one Sobol seed is required")
    if not (0.0 < config.gaussian_mixture_weight < 1.0):
        raise ValueError("gaussian_mixture_weight must lie in (0,1)")

    data = np.load(_reference_path())
    reference = {
        "x_edges": np.asarray(data["x_edges"]),
        "x_centers": np.asarray(data["x_centers"]),
        "center_index": int(data["center_index"]),
        "inside_column": np.asarray(data["inside_column_sInv"]),
        "total_rate": float(data["total_rate_sInv"]),
        "Pi": np.asarray(data["equilibrium_weight_m3"]),
    }

    exterior_total = reference["total_rate"] - float(
        reference["inside_column"].sum()
    )
    baseline_red = 0.5 * exterior_total
    baseline_blue = 0.5 * exterior_total

    columns = []
    totals = []
    recoil_m1 = []
    continuous_m2 = []
    mb_totals = []
    red_rates = []
    blue_rates = []
    four_forces = []

    for seed in config.seeds:
        sample = _sample_seed(config, int(seed), reference)
        exact = sample["exact_weight"]
        baseline = sample["baseline_weight"]
        count = len(exact)

        exact_inside = (
            (sample["cell_exact"] >= 0)
            & (sample["cell_exact"] < len(reference["x_centers"]))
        )
        baseline_inside = (
            (sample["cell_baseline"] >= 0)
            & (sample["cell_baseline"] < len(reference["x_centers"]))
        )

        exact_hist = np.bincount(
            sample["cell_exact"][exact_inside],
            weights=exact[exact_inside],
            minlength=len(reference["x_centers"]),
        ) / count
        baseline_hist = np.bincount(
            sample["cell_baseline"][baseline_inside],
            weights=baseline[baseline_inside],
            minlength=len(reference["x_centers"]),
        ) / count

        columns.append(
            reference["inside_column"] + exact_hist - baseline_hist
        )
        totals.append(
            reference["total_rate"] + float(np.mean(exact - baseline))
        )

        # Common-random-number recoil increment. The no-recoil continuous
        # first moment is the control variate and is zero by the symmetric
        # Hummer line-centre reference.
        recoil_numerator = float(
            np.mean(
                exact * sample["x_out"]
                - baseline * sample["x_out_no_recoil"]
            )
        )
        recoil_m1.append(recoil_numerator / totals[-1])
        continuous_m2.append(
            float(np.mean(exact * sample["x_out"] ** 2)) / totals[-1]
        )
        mb_totals.append(float(np.mean(sample["mb_weight"])))

        exact_red = float(
            np.sum(
                exact[
                    sample["cell_exact"] < 0
                ]
            )
            / count
        )
        baseline_red_sample = float(
            np.sum(
                baseline[
                    sample["cell_baseline"] < 0
                ]
            )
            / count
        )
        red_rates.append(
            baseline_red + exact_red - baseline_red_sample
        )

        exact_blue = float(
            np.sum(
                exact[
                    sample["cell_exact"] >= len(reference["x_centers"])
                ]
            )
            / count
        )
        baseline_blue_sample = float(
            np.sum(
                baseline[
                    sample["cell_baseline"] >= len(reference["x_centers"])
                ]
            )
            / count
        )
        blue_rates.append(
            baseline_blue + exact_blue - baseline_blue_sample
        )

        four_forces.append(
            np.mean(
                exact[:, None] * sample["delta_photon"],
                axis=0,
            )
        )

    columns = np.asarray(columns)
    total_array = np.asarray(totals)
    recoil_array = np.asarray(recoil_m1)
    m2_array = np.asarray(continuous_m2)
    mb_array = np.asarray(mb_totals)
    four_force_array = np.asarray(four_forces)

    inside = columns.mean(axis=0)
    red = float(np.mean(red_rates))
    blue = float(np.mean(blue_rates))
    total = float(total_array.mean())

    if np.min(inside) < 0.0 or red < 0.0 or blue < 0.0:
        raise FloatingPointError("negative control-variate deposition")

    # Shared event conductance star: center <-> every in-domain cell.
    center = reference["center_index"]
    Pi = reference["Pi"]
    conductance = inside * Pi[center]
    reverse_rate = conductance / Pi
    pair_residual = conductance - reverse_rate * Pi
    pair_balance_relative = float(
        np.max(np.abs(pair_residual))
        / (np.max(np.abs(conductance)) + 1.0e-300)
    )

    generator = np.zeros((len(inside), len(inside)))
    for target in range(len(inside)):
        if target == center:
            continue
        generator[target, center] += inside[target]
        generator[center, target] += reverse_rate[target]
    np.fill_diagonal(generator, -generator.sum(axis=0))

    generator_left_null = float(
        np.max(np.abs(np.ones(len(inside)) @ generator))
    )
    equilibrium_right_null = float(
        np.max(np.abs(generator @ Pi))
        / (
            np.max(np.abs(generator)) * np.max(Pi)
            + 1.0e-300
        )
    )

    photon_force = four_force_array.mean(axis=0)
    hydrogen_force = -photon_force

    area_correction, _ = oscillator_area_correction()
    return LineCenterDepositionResult(
        x_edges=reference["x_edges"],
        x_centers=reference["x_centers"],
        center_index=center,
        inside_rate_s_inv=inside,
        red_exterior_rate_s_inv=red,
        blue_exterior_rate_s_inv=blue,
        total_rate_s_inv=total,
        total_rate_seed_std_s_inv=float(
            total_array.std(ddof=1) if len(total_array) > 1 else 0.0
        ),
        hummer_total_rate_s_inv=reference["total_rate"],
        recoil_increment_M1_x=float(recoil_array.mean()),
        recoil_increment_seed_std_x=float(
            recoil_array.std(ddof=1) if len(recoil_array) > 1 else 0.0
        ),
        continuous_M1_x=float(recoil_array.mean()),
        continuous_M2_x2=float(m2_array.mean()),
        maxwell_juttner_vs_mb_relative=float(
            (total - mb_array.mean()) / total
        ),
        pair_balance_relative=pair_balance_relative,
        generator_left_null=generator_left_null,
        equilibrium_right_null=equilibrium_right_null,
        photon_four_force_per_photon=photon_force,
        hydrogen_four_force_per_photon=hydrogen_force,
        control_variate_column_seed_spread=float(
            np.mean(
                [
                    np.linalg.norm(column - inside)
                    / (np.linalg.norm(inside) + 1.0e-300)
                    for column in columns
                ]
            )
        ),
        oscillator_area_correction=area_correction,
    )

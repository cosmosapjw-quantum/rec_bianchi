"""Full-frequency recoil corrections to the finite-volume Hummer kernel.

The module applies the PR-01B1-B0 exact/no-recoil common-random-number
control variate independently to every source frequency cell.  Angular
Legendre moments are tallied in the hydrogen frame.  The raw columns are
kept independent so that integrated forward/reverse detailed balance can
be audited rather than imposed.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import math

import numpy as np
from scipy.special import eval_legendre

from .thermal_deposition import DepositionConfig, _sample_seed


@dataclass(frozen=True)
class FullKernelConfig:
    temperature_K: float = 3000.0
    n1s_cm3: float = 250.0
    sobol_power: int = 16
    seeds: tuple[int, ...] = (1, 2, 3, 4)
    ell_max: int = 6
    source_cells: tuple[int, ...] | None = None
    gaussian_mixture_weight: float = 0.5
    cauchy_scale_factor: float = 1.0
    cauchy_truncation_sigma: float = 12.0


@dataclass(frozen=True)
class FullFrequencyHarmonicResult:
    x_edges: np.ndarray
    x_centers: np.ndarray
    harmonic_gain_s_inv: np.ndarray
    harmonic_seed_standard_error_s_inv: np.ndarray
    total_rate_s_inv: np.ndarray
    independent_total_rate_s_inv: np.ndarray
    total_partition_discrepancy_s_inv: np.ndarray
    total_rate_standard_error_s_inv: np.ndarray
    red_exterior_rate_s_inv: np.ndarray
    blue_exterior_rate_s_inv: np.ndarray
    recoil_increment_M1_x: np.ndarray
    recoil_increment_standard_error_x: np.ndarray
    photon_four_force_per_photon: np.ndarray
    hydrogen_four_force_per_photon: np.ndarray
    computed_source_mask: np.ndarray
    equilibrium_weight_m3: np.ndarray
    raw_pair_balance_weighted_rms: float
    raw_pair_balance_max_relative: float
    raw_pair_balance_max_significance: float
    raw_pair_balance_pair_count: int
    generator_left_null: float
    raw_equilibrium_right_null: float
    shared_conductance_equilibrium_right_null: float
    minimum_scalar_gain_s_inv: float
    maximum_deposition_residual_s_inv: float


def _reference_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "full_hummer_reference.npz"


def _histogram(values, cells, valid, n_frequency):
    return np.bincount(
        cells[valid], weights=values[valid], minlength=n_frequency
    )


def _pooled_baseline_exterior_split(
    baseline_red_seed: np.ndarray,
    baseline_blue_seed: np.ndarray,
    deterministic_outside: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Use no-recoil mirror symmetry to split deterministic outside opacity."""
    n_frequency = len(deterministic_outside)
    red = np.zeros(n_frequency)
    blue = np.zeros(n_frequency)
    red_mean = baseline_red_seed.mean(axis=1)
    blue_mean = baseline_blue_seed.mean(axis=1)

    for source in range(n_frequency):
        mirror = n_frequency - 1 - source
        red_proxy = 0.5 * (red_mean[source] + blue_mean[mirror])
        blue_proxy = 0.5 * (blue_mean[source] + red_mean[mirror])
        proxy_sum = red_proxy + blue_proxy
        if proxy_sum <= 0.0:
            fraction_red = 0.5
        else:
            fraction_red = red_proxy / proxy_sum
        red[source] = deterministic_outside[source] * fraction_red
        blue[source] = deterministic_outside[source] - red[source]
    return red, blue


@lru_cache(maxsize=16)
def full_frequency_harmonic_kernel(
    config: FullKernelConfig = FullKernelConfig(),
) -> FullFrequencyHarmonicResult:
    if config.ell_max < 0 or config.ell_max > 32:
        raise ValueError("ell_max must lie in [0,32]")
    if not config.seeds:
        raise ValueError("at least one seed is required")

    data = np.load(_reference_path())
    x_edges = np.asarray(data["x_edges"], dtype=float)
    x_centers = np.asarray(data["x_centers"], dtype=float)
    baseline_gain = np.asarray(data["physical_gain_sInv"], dtype=float)
    baseline_inside_loss = np.asarray(data["within_core_loss_sInv"], dtype=float)
    baseline_total = (
        float(data["rate_scale_sInv"])
        * np.asarray(data["cell_averaged_Voigt_profile"], dtype=float)
    )
    equilibrium = np.asarray(data["equilibrium_weight_m3"], dtype=float)
    n_frequency = len(x_centers)

    if config.ell_max >= baseline_gain.shape[0]:
        raise ValueError("reference does not contain requested ell_max")

    if config.source_cells is None:
        source_cells = tuple(range(n_frequency))
    else:
        source_cells = tuple(sorted(set(int(i) for i in config.source_cells)))
        if any(i < 0 or i >= n_frequency for i in source_cells):
            raise ValueError("source cell outside reference grid")

    n_seed = len(config.seeds)
    n_ell = config.ell_max + 1
    columns_by_seed = np.zeros((n_seed, n_ell, n_frequency, n_frequency))
    totals_by_seed = np.zeros((n_seed, n_frequency))
    recoil_by_seed = np.zeros((n_seed, n_frequency))
    exact_red_seed = np.zeros((n_frequency, n_seed))
    exact_blue_seed = np.zeros((n_frequency, n_seed))
    baseline_red_seed = np.zeros((n_frequency, n_seed))
    baseline_blue_seed = np.zeros((n_frequency, n_seed))
    four_force_by_seed = np.zeros((n_seed, n_frequency, 4))
    computed = np.zeros(n_frequency, dtype=bool)

    # Uncomputed columns remain the exact no-recoil reference. This permits
    # fast unit tests on selected source cells without changing array shape.
    for seed_index in range(n_seed):
        columns_by_seed[seed_index] = baseline_gain[:n_ell]
        totals_by_seed[seed_index] = baseline_total

    reference_for_sampler = {
        "x_edges": x_edges,
        "x_centers": x_centers,
    }

    for source in source_cells:
        computed[source] = True
        source_config = DepositionConfig(
            temperature_K=config.temperature_K,
            n1s_cm3=config.n1s_cm3,
            source_x_left=float(x_edges[source]),
            source_x_right=float(x_edges[source + 1]),
            sobol_power=config.sobol_power,
            seeds=config.seeds,
            gaussian_mixture_weight=config.gaussian_mixture_weight,
            cauchy_scale_factor=config.cauchy_scale_factor,
            cauchy_truncation_sigma=config.cauchy_truncation_sigma,
        )

        for seed_index, seed in enumerate(config.seeds):
            sample = _sample_seed(source_config, int(seed), reference_for_sampler)
            exact = sample["exact_weight"]
            baseline = sample["baseline_weight"]
            count = len(exact)
            exact_valid = (sample["cell_exact"] >= 0) & (sample["cell_exact"] < n_frequency)
            baseline_valid = (sample["cell_baseline"] >= 0) & (sample["cell_baseline"] < n_frequency)

            for ell in range(n_ell):
                angular = eval_legendre(ell, sample["mu_lab"])
                exact_hist = _histogram(
                    exact * angular, sample["cell_exact"], exact_valid, n_frequency
                ) / count
                baseline_hist = _histogram(
                    baseline * angular,
                    sample["cell_baseline"],
                    baseline_valid,
                    n_frequency,
                ) / count
                columns_by_seed[seed_index, ell, :, source] = (
                    baseline_gain[ell, :, source] + exact_hist - baseline_hist
                )

            totals_by_seed[seed_index, source] = baseline_total[source] + float(
                np.mean(exact - baseline)
            )
            recoil_numerator = float(
                np.mean(
                    exact * (sample["x_out"] - sample["x_in"])
                    - baseline * (sample["x_out_no_recoil"] - sample["x_in"])
                )
            )
            recoil_by_seed[seed_index, source] = (
                recoil_numerator / totals_by_seed[seed_index, source]
            )

            exact_red_seed[source, seed_index] = float(
                np.mean(exact * (sample["cell_exact"] < 0))
            )
            exact_blue_seed[source, seed_index] = float(
                np.mean(exact * (sample["cell_exact"] >= n_frequency))
            )
            baseline_red_seed[source, seed_index] = float(
                np.mean(baseline * (sample["cell_baseline"] < 0))
            )
            baseline_blue_seed[source, seed_index] = float(
                np.mean(baseline * (sample["cell_baseline"] >= n_frequency))
            )
            four_force_by_seed[seed_index, source] = np.mean(
                exact[:, None] * sample["delta_photon"], axis=0
            )

    harmonic_gain = columns_by_seed.mean(axis=0)
    harmonic_se = (
        columns_by_seed.std(axis=0, ddof=1) / math.sqrt(n_seed)
        if n_seed > 1
        else np.zeros_like(harmonic_gain)
    )
    total_rate = totals_by_seed.mean(axis=0)
    total_se = (
        totals_by_seed.std(axis=0, ddof=1) / math.sqrt(n_seed)
        if n_seed > 1
        else np.zeros_like(total_rate)
    )
    recoil = recoil_by_seed.mean(axis=0)
    recoil_se = (
        recoil_by_seed.std(axis=0, ddof=1) / math.sqrt(n_seed)
        if n_seed > 1
        else np.zeros_like(recoil)
    )

    # Deterministic no-recoil outside total plus QMC exact-minus-baseline split.
    baseline_outside = np.maximum(
        0.0, baseline_total - baseline_gain[0].sum(axis=0)
    )
    baseline_red, baseline_blue = _pooled_baseline_exterior_split(
        baseline_red_seed, baseline_blue_seed, baseline_outside
    )
    red = baseline_red + (exact_red_seed - baseline_red_seed).mean(axis=1)
    blue = baseline_blue + (exact_blue_seed - baseline_blue_seed).mean(axis=1)

    # The partitioned estimator is primary: every exact and no-recoil event
    # belongs to red, an interior cell, or blue.  This makes closure an
    # estimator identity.  The independently averaged total is retained as a
    # quadrature diagnostic, not used to repair any cell.
    interior_sum = harmonic_gain[0].sum(axis=0)
    independent_total = total_rate.copy()
    total_rate = interior_sum + red + blue
    total_partition_discrepancy = total_rate - independent_total

    photon_force = four_force_by_seed.mean(axis=0)
    hydrogen_force = -photon_force

    # Raw independent-column detailed-balance audit.
    raw_conductance = harmonic_gain[0] * equilibrium[None, :]
    differences = raw_conductance - raw_conductance.T
    average = 0.5 * (raw_conductance + raw_conductance.T)
    se_conductance = harmonic_se[0] * equilibrium[None, :]
    combined_se = np.sqrt(se_conductance**2 + se_conductance.T**2)
    upper = np.triu(np.ones_like(average, dtype=bool), 1)
    scale_cut = np.max(np.abs(average)) * 1.0e-10
    selected = upper & computed[:, None] & computed[None, :] & (np.abs(average) > scale_cut)
    pair_count = int(np.count_nonzero(selected))
    if pair_count:
        weighted_rms = float(
            np.linalg.norm(differences[selected])
            / (np.linalg.norm(average[selected]) + 1.0e-300)
        )
        max_relative = float(
            np.max(np.abs(differences[selected]) / (np.abs(average[selected]) + 1.0e-300))
        )
        significance = np.abs(differences[selected]) / (combined_se[selected] + 1.0e-300)
        max_significance = float(np.max(significance))
    else:
        weighted_rms = max_relative = max_significance = 0.0

    # Raw generator and an event-paired conductance reference are both stored
    # in the diagnostics. The latter is not used to hide the raw audit.
    raw_generator = harmonic_gain[0].copy()
    np.fill_diagonal(raw_generator, 0.0)
    np.fill_diagonal(raw_generator, -raw_generator.sum(axis=0))
    generator_left_null = float(np.max(np.abs(np.ones(n_frequency) @ raw_generator)))
    raw_equilibrium_null = float(
        np.max(np.abs(raw_generator @ equilibrium))
        / (np.max(np.abs(raw_generator)) * np.max(equilibrium) + 1.0e-300)
    )

    shared_conductance = 0.5 * (raw_conductance + raw_conductance.T)
    shared_rate = shared_conductance / equilibrium[None, :]
    shared_generator = shared_rate.copy()
    np.fill_diagonal(shared_generator, 0.0)
    np.fill_diagonal(shared_generator, -shared_generator.sum(axis=0))
    shared_equilibrium_null = float(
        np.max(np.abs(shared_generator @ equilibrium))
        / (np.max(np.abs(shared_generator)) * np.max(equilibrium) + 1.0e-300)
    )

    deposition_residual = interior_sum + red + blue - total_rate
    scalar_values = harmonic_gain[0, :, computed]

    return FullFrequencyHarmonicResult(
        x_edges=x_edges,
        x_centers=x_centers,
        harmonic_gain_s_inv=harmonic_gain,
        harmonic_seed_standard_error_s_inv=harmonic_se,
        total_rate_s_inv=total_rate,
        independent_total_rate_s_inv=independent_total,
        total_partition_discrepancy_s_inv=total_partition_discrepancy,
        total_rate_standard_error_s_inv=total_se,
        red_exterior_rate_s_inv=red,
        blue_exterior_rate_s_inv=blue,
        recoil_increment_M1_x=recoil,
        recoil_increment_standard_error_x=recoil_se,
        photon_four_force_per_photon=photon_force,
        hydrogen_four_force_per_photon=hydrogen_force,
        computed_source_mask=computed,
        equilibrium_weight_m3=equilibrium,
        raw_pair_balance_weighted_rms=weighted_rms,
        raw_pair_balance_max_relative=max_relative,
        raw_pair_balance_max_significance=max_significance,
        raw_pair_balance_pair_count=pair_count,
        generator_left_null=generator_left_null,
        raw_equilibrium_right_null=raw_equilibrium_null,
        shared_conductance_equilibrium_right_null=shared_equilibrium_null,
        minimum_scalar_gain_s_inv=float(np.min(scalar_values)) if scalar_values.size else 0.0,
        maximum_deposition_residual_s_inv=float(np.max(np.abs(deposition_residual[computed]))) if np.any(computed) else 0.0,
    )

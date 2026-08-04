import numpy as np
from scipy.constants import c, h, k, physical_constants

from full_bianchi_hyrec.recoil.thermal_deposition import (
    DepositionConfig,
    analytic_rayleigh_recoil_mean,
    line_center_column,
    oscillator_area_correction,
)


M_H = physical_constants["atomic mass constant"][0] * 1.00782503223
NU_ALPHA = c / (1215.6701e-10)
B_D = np.sqrt(2.0 * k * 3000.0 / M_H) / c
G_RECOIL = h * NU_ALPHA / (M_H * c**2 * B_D)


def test_oscillator_area_correction_is_source_derived():
    correction, a21_from_f = oscillator_area_correction()
    assert correction > 1.0
    assert abs(a21_from_f / 6.265e8 - 0.9994638195) < 2e-10


def test_line_center_qmc_reproduces_absolute_hummer_opacity():
    result = line_center_column(
        DepositionConfig(sobol_power=17, seeds=(1, 2))
    )
    assert abs(result.total_rate_s_inv / result.hummer_total_rate_s_inv - 1.0) < 2e-5
    assert np.all(result.inside_rate_s_inv >= 0.0)
    assert result.red_exterior_rate_s_inv >= 0.0
    assert result.blue_exterior_rate_s_inv >= 0.0
    assert abs(
        result.inside_rate_s_inv.sum()
        + result.red_exterior_rate_s_inv
        + result.blue_exterior_rate_s_inv
        - result.total_rate_s_inv
    ) < 5e-13


def test_control_variate_recovers_exact_recoil_mean():
    result = line_center_column(
        DepositionConfig(sobol_power=18, seeds=(3, 4, 5))
    )
    expected = analytic_rayleigh_recoil_mean(G_RECOIL, B_D)
    assert abs(result.continuous_M1_x - expected) / abs(expected) < 2e-5


def test_shared_conductance_has_exact_pair_balance_and_number_null():
    result = line_center_column(
        DepositionConfig(sobol_power=16, seeds=(7, 8))
    )
    assert result.pair_balance_relative < 5e-15
    assert result.generator_left_null < 5e-15
    assert result.equilibrium_right_null < 5e-15


def test_same_event_four_force_closes():
    result = line_center_column(
        DepositionConfig(sobol_power=16, seeds=(9, 10))
    )
    assert np.linalg.norm(
        result.photon_four_force_per_photon
        + result.hydrogen_four_force_per_photon
    ) == 0.0

import numpy as np

from full_bianchi_hyrec.recoil.full_harmonic_deposition import (
    FullKernelConfig,
    full_frequency_harmonic_kernel,
)


def test_full_kernel_shapes_and_positive_scalar_gain():
    result = full_frequency_harmonic_kernel(
        FullKernelConfig(
            sobol_power=11,
            seeds=(1, 2),
            ell_max=4,
            source_cells=(0, 4, 8, 12, 16),
        )
    )
    assert result.harmonic_gain_s_inv.shape == (5, 17, 17)
    assert result.total_rate_s_inv.shape == (17,)
    assert result.computed_source_mask.sum() == 5
    assert np.min(result.harmonic_gain_s_inv[0, :, result.computed_source_mask]) >= 0.0


def test_qmc_corrections_close_deposition_and_same_event_four_force():
    result = full_frequency_harmonic_kernel(
        FullKernelConfig(
            sobol_power=12,
            seeds=(3, 4),
            ell_max=2,
            source_cells=(0, 8, 16),
        )
    )
    mask = result.computed_source_mask
    closure = (
        result.harmonic_gain_s_inv[0][:, mask].sum(axis=0)
        + result.red_exterior_rate_s_inv[mask]
        + result.blue_exterior_rate_s_inv[mask]
        - result.total_rate_s_inv[mask]
    )
    assert np.max(np.abs(closure)) < 2e-10
    assert np.linalg.norm(
        result.photon_four_force_per_photon[mask]
        + result.hydrogen_four_force_per_photon[mask]
    ) == 0.0


def test_independent_columns_are_close_to_detailed_balance_within_qmc_error():
    result = full_frequency_harmonic_kernel(
        FullKernelConfig(
            sobol_power=13,
            seeds=(5, 6, 7),
            ell_max=0,
            source_cells=tuple(range(17)),
        )
    )
    assert result.raw_pair_balance_weighted_rms < 5e-3
    # The raw independent-column audit intentionally remains unsymmetrized.
    # This regression detects the current integrated microreversibility blocker.
    assert result.raw_equilibrium_right_null > 1e-6
    assert result.shared_conductance_equilibrium_right_null < 1e-12


def test_recoil_increment_has_correct_sign_and_scale():
    result = full_frequency_harmonic_kernel(
        FullKernelConfig(
            sobol_power=12,
            seeds=(8, 9),
            ell_max=0,
            source_cells=(2, 8, 14),
        )
    )
    values = result.recoil_increment_M1_x[result.computed_source_mask]
    assert np.all(values < 0.0)
    assert np.max(np.abs(values + 4.6292e-4)) < 2.5e-5

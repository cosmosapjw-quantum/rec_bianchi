from __future__ import annotations

from pathlib import Path

import numpy as np

from full_bianchi_hyrec.recoil.native_common_partition import (
    HIGH_RESOLUTION_CONFIGURATION,
    PRODUCTION_CONFIGURATION,
    cell_centre_moment_matrix,
    cell_uniform_moment_matrix,
    load_integrated_table,
    nearest_grid_distances,
    positive_moment_feasibility,
    positive_nullspace_witness,
    projectable_support_violation,
    raw_positive_moments_x,
)


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = (
    ROOT
    / "archive"
    / "inputs"
    / "original_hyrec_oct2012"
    / "HyRec_Oct2012.zip"
)
COMMON = ROOT / "data" / "hyrec_common_measure_v051.npz"
PHYSICAL = ROOT / "data" / "original_hyrec_physical_flux_v053.npz"


def test_canonical_production_and_high_resolution_tables_are_separate_lanes():
    production = load_integrated_table(ARCHIVE, PRODUCTION_CONFIGURATION)
    high_resolution = load_integrated_table(ARCHIVE, HIGH_RESOLUTION_CONFIGURATION)

    assert production.sha256 == (
        "93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9"
    )
    assert high_resolution.sha256 == (
        "db201c729a38c7919172cf080c8ba44cdf8e6b131a6eaa8adcbc9e58fd4d0c93"
    )
    assert production.values.shape == (311, 5)
    assert high_resolution.values.shape == (1493, 5)
    assert production.diffusion_indices.shape == (80,)
    assert high_resolution.diffusion_indices.shape == (300,)

    distances, _ = nearest_grid_distances(
        production.energy_eV, high_resolution.energy_eV
    )
    assert np.count_nonzero(distances == 0.0) == 0
    assert np.min(distances) >= 1.0e-6
    assert np.max(distances) > 4.0e-2


def test_both_native_diffusion_lanes_have_only_two_centres_in_v051_core():
    production = load_integrated_table(ARCHIVE, PRODUCTION_CONFIGURATION)
    high_resolution = load_integrated_table(ARCHIVE, HIGH_RESOLUTION_CONFIGURATION)
    with np.load(COMMON, allow_pickle=False) as common:
        nu_abs = float(common["nu_abs_Hz"])
        width = float(common["Doppler_width_Hz"])

    production_x = production.doppler_x(nu_abs, width)[
        production.diffusion_indices
    ]
    high_resolution_x = high_resolution.doppler_x(nu_abs, width)[
        high_resolution.diffusion_indices
    ]
    assert np.count_nonzero(np.abs(production_x) <= 4.25) == 2
    assert np.count_nonzero(np.abs(high_resolution_x) <= 4.25) == 2
    assert np.min(production_x) < -700.0
    assert np.max(production_x) > 700.0
    assert np.min(high_resolution_x) < -1100.0
    assert np.max(high_resolution_x) > 700.0


def test_full_native_physical_edge_measure_cannot_fit_the_17_cell_core():
    with np.load(COMMON, allow_pickle=False) as common, np.load(
        PHYSICAL, allow_pickle=False
    ) as physical:
        intervals = np.asarray(common["state_intervals_x"], dtype=float)
        x = (
            np.asarray(physical["frequency_Hz"], dtype=float)
            - float(common["nu_abs_Hz"])
        ) / float(common["Doppler_width_Hz"])
        flux = np.asarray(
            physical["transport_edge_flux_sInv_per_H"], dtype=float
        )

    full = raw_positive_moments_x(x, flux)
    violation, source_second, target_bound = projectable_support_violation(
        full, intervals
    )
    assert violation
    assert source_second > 1.0e8
    assert target_bound == 4.25**2

    diffusion = raw_positive_moments_x(x[100:180], flux[100:180])
    violation, source_second, _ = projectable_support_violation(
        diffusion, intervals
    )
    assert violation
    assert source_second > 2.0e4

    core = np.abs(x) <= 4.25
    assert np.count_nonzero(core) == 2
    assert flux[core].sum() / flux.sum() < 2.0e-3


def test_five_moments_do_not_identify_seventeen_positive_cell_masses():
    with np.load(COMMON, allow_pickle=False) as common:
        intervals = np.asarray(common["state_intervals_x"], dtype=float)
    matrix = cell_uniform_moment_matrix(intervals)
    witness = positive_nullspace_witness(matrix)
    assert witness.rank == 5
    assert witness.nullity == 12
    assert witness.minimum_weight > 0.0
    assert witness.moment_residual < 2.0e-13
    assert np.linalg.norm(witness.plus - witness.minus) > 1.0e-3
    assert np.allclose(matrix @ witness.plus, matrix @ witness.minus, atol=2e-13)


def test_core_two_spike_measure_is_not_representable_by_naive_fixed_cell_closures():
    with np.load(COMMON, allow_pickle=False) as common, np.load(
        PHYSICAL, allow_pickle=False
    ) as physical:
        intervals = np.asarray(common["state_intervals_x"], dtype=float)
        x = (
            np.asarray(physical["frequency_Hz"], dtype=float)
            - float(common["nu_abs_Hz"])
        ) / float(common["Doppler_width_Hz"])
        flux = np.asarray(
            physical["transport_edge_flux_sInv_per_H"], dtype=float
        )
    core = np.abs(x) <= 4.25
    audit = raw_positive_moments_x(x[core], flux[core])

    for matrix in (
        cell_centre_moment_matrix(intervals),
        cell_uniform_moment_matrix(intervals),
    ):
        feasible, weights, message = positive_moment_feasibility(
            matrix, audit.normalized_moments
        )
        assert not feasible, message
        assert weights is None


def test_pr04b2b_durable_no_go_artifact():
    import json

    artifact = (
        ROOT
        / "archive"
        / "expanded"
        / "Full_Bianchi_HyRec_PR04B2B_native_common_partition_no_go_v0_54"
    )
    ledger = json.loads((artifact / "PR04B2B_ledger.json").read_text())
    assert ledger["status"] == (
        "PASS_PR04B2B_IDENTIFIABILITY_NO_GO_PR04C_OPEN"
    )
    assert all(ledger["hard_gate_status"].values())
    assert ledger["decision"]["PR04"] == "IN_PROGRESS"
    assert ledger["decision"]["direct_native_to_17_cell_map"] == (
        "REJECTED_BY_SUPPORT_AND_IDENTIFIABILITY"
    )
    with np.load(
        ROOT / "data" / "native_common_partition_v054.npz",
        allow_pickle=False,
    ) as evidence:
        assert evidence["target_uniform_moment_matrix"].shape == (5, 17)
        assert evidence["production_energy_eV"].shape == (311,)
        assert evidence["high_resolution_energy_eV"].shape == (1493,)
        assert np.min(evidence["positive_witness_plus"]) > 0.0
        assert np.min(evidence["positive_witness_minus"]) > 0.0

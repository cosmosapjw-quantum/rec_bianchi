from __future__ import annotations

from pathlib import Path

import numpy as np

from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    parse_original_hyrec_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.hyrec_source_adapter import (
    OriginalHyRecVirtualSourceAdapter,
    apply_escape_transfer,
    directional_optical_depth,
    one_photon_paired_action,
)

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "archive" / "expanded" / "Full_Bianchi_HyRec_PR04B2A_physical_native_edge_flux_v0_53" / "ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv"


def test_virtual_source_adapter_reconstructs_source_transfer() -> None:
    snapshot = parse_original_hyrec_snapshot_csv(SNAPSHOT)
    adapter = OriginalHyRecVirtualSourceAdapter.from_snapshot(snapshot)
    reconstructed = apply_escape_transfer(snapshot.Dfplus, adapter.source_function, adapter.tau_flrw)
    expected = snapshot.Dfminus
    scale = np.maximum(np.abs(expected), 1.0e-300)
    assert np.max(np.abs(reconstructed - expected) / scale) < 8.0e-13


def test_directional_optical_depth_reduces_to_flrw_tau() -> None:
    snapshot = parse_original_hyrec_snapshot_csv(SNAPSHOT)
    adapter = OriginalHyRecVirtualSourceAdapter.from_snapshot(snapshot)
    tau = directional_optical_depth(adapter, redshift_rate_s_inv=-snapshot.H_s_inv)
    assert np.max(np.abs(tau - snapshot.Dtau) / np.maximum(snapshot.Dtau, 1.0e-300)) < 2.0e-13


def test_one_photon_paired_action_has_planck_detailed_balance_null() -> None:
    temperature_K = 3000.0
    frequency_Hz = 2.466e15
    lower_population = 0.8
    degeneracy_ratio = 3.0
    z = np.exp(-6.62607015e-34 * frequency_Hz / (1.380649e-23 * temperature_K))
    upper_population = lower_population * degeneracy_ratio * z
    planck = z / (1.0 - z)
    action = one_photon_paired_action(
        occupation=planck,
        upper_population=upper_population,
        lower_population=lower_population,
        degeneracy_ratio=degeneracy_ratio,
        spontaneous_rate_s_inv=6.25e8,
    )
    assert abs(action) < 2.0e-12

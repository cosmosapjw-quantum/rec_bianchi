from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy.constants import c, electron_volt

from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig
from full_bianchi_hyrec.recoil.original_hyrec_native import H_PLANCK_EV_S
from full_bianchi_hyrec.trajectory.physical_split_reference import (
    CLAIM,
    STATUS,
    adjacent_energy_feasibility,
    build_rec_local02_diagnostic,
)


ROOT = Path(__file__).resolve().parents[2]


def diagnostic() -> dict:
    return build_rec_local02_diagnostic(ROOT)


def test_all_eight_tracked_inputs_match() -> None:
    assert all(item["match"] for item in diagnostic()["tracked_inputs"].values())


def test_actual_35x26_occupation_and_measure_are_bound() -> None:
    value = diagnostic()["source_representation"]
    assert value["occupation_shape"] == [35, 26]
    assert value["occupation_minimum"] > 0.0
    assert value["occupation_isotropic_max_abs_residual"] == 0.0
    assert value["mode_measure_shape"] == [35]
    assert value["mode_measure_minimum_m3"] > 0.0
    assert value["directional_measure_shape"] == [35, 26]
    assert value["directional_measure_minimum_m3"] > 0.0
    assert value["parent_network_interval_max_abs_residual"] == 0.0
    assert value["scalar_history_outgoing_virtual_shape"] == [311, 7489]
    assert value["scalar_history_angular_rank"] == 1


def test_actual_source_flux_parity_is_independently_reconstructed() -> None:
    for residuals in diagnostic()["source_flux_parity_residuals"].values():
        assert max(residuals.values()) < 4.0e-13


def test_adjacent_energy_feasibility_is_proved_without_map_selection() -> None:
    certificate = diagnostic()["adjacent_energy_moment_feasibility"]
    assert certificate["classification"] == "EXPLORATORY_NONAUTHORITATIVE"
    assert certificate["map_shape"] == [35, 8]
    assert certificate["orientation"] == "B[target_com_cell,source_native_index]"
    assert certificate["feasible"]
    assert certificate["nonnegative"]
    assert certificate["number_and_energy_exact"]
    assert certificate["physical_map"] is None
    assert not certificate["physical_map_selected"]
    assert certificate["infeasible_source_columns"] == []
    assert certificate["target_energy_range_eV"][0] < 10.194417
    assert certificate["target_energy_range_eV"][1] > 10.203012
    assert certificate["max_abs_number_residual"] == 0.0
    assert certificate["max_abs_energy_residual_eV"] < 2.0e-15
    matrix = np.zeros((35, 8), dtype=float)
    for column in certificate["exploratory_sparse_witness"]:
        matrix[column["target_indices"], column["source_column"]] = column[
            "number_fractions"
        ]
    with (
        np.load(ROOT / "data/z1100_direct_network_node.npz", allow_pickle=False) as network,
        np.load(
            ROOT / "data/pr05b2_source_history_v060.npz", allow_pickle=False
        ) as history,
    ):
        locked_target_energy = (
            np.asarray(network["momentum_scale"], dtype=float) * c / electron_volt
        )
        line = LineBoundaryConfig.lyman_alpha(
            temperature_K=float(network["temperature_K"]),
            x_red=-21.25,
            x_blue=21.25,
        )
        intervals = np.asarray(network["state_intervals"])
        frequency = line.nu_abs_Hz + intervals * line.Doppler_width_Hz
        lower = frequency[:, 0]
        upper = frequency[:, 1]
        legacy_interval_centroid_energy = (
            H_PLANCK_EV_S
            * 0.75
            * (upper**4 - lower**4)
            / (upper**3 - lower**3)
        )
        source_energy = np.asarray(history["energy_eV"])[136:144]
    assert np.all(matrix >= 0.0)
    assert np.array_equal(np.sum(matrix, axis=0), np.ones(8))
    assert np.max(np.abs(locked_target_energy @ matrix - source_energy)) < 2.0e-15
    assert (
        np.max(np.abs(legacy_interval_centroid_energy - locked_target_energy))
        > 5.0e-8
    )
    assert (
        np.max(np.abs(legacy_interval_centroid_energy @ matrix - source_energy))
        > 5.0e-8
    )
    assert certificate["witness_sha256"] == hashlib.sha256(
        np.asarray(matrix, dtype="<f8").tobytes(order="C")
    ).hexdigest()
    assert diagnostic()["source_representation"][
        "source_parent_source_index_144_target_rows"
    ] == [34]
    binding = diagnostic()["target_energy_binding"]
    assert binding["source_energy_rescale"] == 1.0
    assert binding["source"] == "tracked CollisionNetwork.momentum_scale"
    assert binding["momentum_scale_units"] == "kg m s^-1"
    assert binding["physical_cell_energy_definition"] == (
        "momentum_scale*c/electron_volt"
    )
    assert binding["locked_target_energy_sha256"] == hashlib.sha256(
        np.asarray(locked_target_energy, dtype="<f8").tobytes(order="C")
    ).hexdigest()
    assert binding["source_parent_point_formula_max_abs_residual_eV"] < 2.0e-15
    assert (
        7.8e-8
        < binding[
            "source_parent_point_to_locked_owner_max_abs_difference_eV"
        ]
        < 8.0e-8
    )
    assert not binding["legacy_interval_centroid_is_authoritative"]
    assert (
        5.5e-8
        < binding[
            "legacy_interval_centroid_to_locked_owner_max_abs_difference_eV"
        ]
        < 5.6e-8
    )


def test_adjacent_energy_witness_uses_locked_momentum_scale_owner() -> None:
    certificate = diagnostic()["adjacent_energy_moment_feasibility"]
    matrix = np.zeros((35, 8), dtype=float)
    for column in certificate["exploratory_sparse_witness"]:
        matrix[column["target_indices"], column["source_column"]] = column[
            "number_fractions"
        ]
    with (
        np.load(ROOT / "data/z1100_direct_network_node.npz", allow_pickle=False) as network,
        np.load(
            ROOT / "data/pr05b2_source_history_v060.npz", allow_pickle=False
        ) as history,
    ):
        locked_target_energy = (
            np.asarray(network["momentum_scale"], dtype=float) * c / electron_volt
        )
        source_energy = np.asarray(history["energy_eV"], dtype=float)[136:144]

    np.testing.assert_allclose(
        locked_target_energy @ matrix,
        source_energy,
        rtol=0.0,
        atol=2.0e-15,
    )
    assert certificate["target_energy_range_eV"] == [
        float(np.min(locked_target_energy)),
        float(np.max(locked_target_energy)),
    ]
    binding = diagnostic()["target_energy_binding"]
    assert binding["source"] == "tracked CollisionNetwork.momentum_scale"
    assert binding["physical_cell_energy_definition"] == (
        "momentum_scale*c/electron_volt"
    )


def test_adjacent_energy_feasibility_rejects_a_source_outside_target_hull() -> None:
    with np.load(
        ROOT / "data/z1100_direct_network_node.npz",
        allow_pickle=False,
    ) as network:
        targets = (
            np.asarray(network["momentum_scale"], dtype=float) * c / electron_volt
        )
    sources = np.linspace(float(np.min(targets)), float(np.max(targets)), 8)
    sources[0] = float(np.min(targets)) - 1.0e-6
    certificate = adjacent_energy_feasibility(targets, sources)
    assert not certificate["feasible"]
    assert certificate["infeasible_source_columns"] == [0]
    assert certificate["physical_map"] is None


def test_doppler_definitions_are_reported_without_selection() -> None:
    value = diagnostic()["doppler_width_reconciliation"]
    assert value["csv_boundary_width_Hz"] > 0.0
    assert value["modern_line_boundary_width_Hz"] > 0.0
    assert 1.0e-5 < value["relative_difference"] < 1.5e-5
    assert value["selected_definition"] == "NONE_BLOCKED_NO_SILENT_SELECTION"
    assert value["direct_node_temperature_K"] == 3003.496188829631
    assert value["direct_node_network_measure_max_relative_mismatch"] < 2.0e-8
    assert 5.0e-4 < value["default_3000K_network_measure_max_relative_mismatch"] < 6.5e-4
    assert not value["default_3000K_from_network_permitted"]


def test_actual_26_direction_grid_has_explicit_face_no_go_witness() -> None:
    value = diagnostic()
    audit = value["full_coupling_identifiability"]
    witness = value["positive_nonidentifiability_witness"]
    assert audit["required_angular_rank"] == 26
    assert not audit["com_face_trace_source_defined"]
    assert audit["bounded_no_go"]
    assert witness["field_a_minimum"] > 0.0
    assert witness["field_b_minimum"] > 0.0
    assert witness["fields_distinct"]
    assert witness["weighted_mean_residual"] < 2.0e-15


def test_terminal_claim_does_not_promote_physical_split() -> None:
    value = diagnostic()
    assert value["status"] == STATUS
    assert value["claim"] == CLAIM
    assert value["blocking_conditions"] == [
        "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
    ]
    assert value["not_run"] == [
        "deposition_map_selection",
        "full_moving_map_jvp",
        "photon_and_atomic_four_force_assembly",
        "number_energy_four_force_balance",
        "thermal_and_spectral_response",
        "independent_directional_jvp",
        "restart_and_history_transactions",
        "physical_reference_tests",
    ]
    for forbidden in (
        "selected_deposition_map",
        "moving_map_jvp",
        "photon_four_force",
        "atomic_four_force",
    ):
        assert forbidden not in value

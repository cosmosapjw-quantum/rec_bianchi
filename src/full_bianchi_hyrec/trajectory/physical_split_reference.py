"""REC-LOCAL-02 source-authority diagnostic.

This module deliberately records why the currently available source inputs do
not admit a physical split-domain reference.  It does not construct a face
closure, select a Doppler convention, or supply any part of a coupled JVP.
"""
from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.constants import c, electron_volt

from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    boundary_sample_reconstruction_residuals,
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.recoil.original_hyrec_native import H_PLANCK_EV_S
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (
    audit_full_coupling_identifiability,
)


CLAIM = "NO_PASS_REC_PHYSICAL_SPLIT"
STATUS = "BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT"
CLASSIFICATION = "EXPLORATORY_NONAUTHORITATIVE"
RECEIPT_SCHEMA = "REC_LOCAL_02_SOURCE_BOUND_GATE_V2"
AUTHORITY_PROJECTION_SCHEMA = "REC_LOCAL_02_AUTHORITY_PROJECTION_V1"
DIAGNOSTIC_CONTRACT_SCHEMA = "REC_LOCAL_02_DIAGNOSTIC_CONTRACT_V1"
PORTABLE_RECEIPT_CONTRACT_SCHEMA = "REC_LOCAL_02_PORTABLE_RECEIPT_CONTRACT_V1"
PORTABLE_DIAGNOSTICS_SCHEMA = "REC_LOCAL_02_PORTABLE_DIAGNOSTICS_V1"
FREQUENCY_MOMENT_FORMULA = "CENTER_HALFWIDTH_TRACKED_X_BINARY64_V1"
DIAGNOSTIC_DECIMAL_QUANTUM = "1E-15"
DIAGNOSTIC_PATHS = {
    (
        "doppler_width_reconciliation."
        "direct_node_network_measure_max_relative_mismatch"
    ): ("1.08E-8", "1.10E-8"),
    (
        "target_energy_binding."
        "legacy_interval_centroid_to_locked_owner_max_abs_difference_eV"
    ): ("5.5E-8", "5.6E-8"),
}
NATIVE_INTERIOR_INDICES = tuple(range(136, 144))
NATIVE_INTERFACE_EDGES = ((135, 136), (143, 144))
TRACKED_INPUTS = {
    "boundary_snapshot": (
        "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55/pr04c_z1100.csv",
        "147ba6e6cfdae9c06530a0983161e769198b3bb5ad56c0c4d820b0a3f5d3e7b5",
    ),
    "original_hyrec": (
        "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip",
        "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27",
    ),
    "network": (
        "data/z1100_direct_network_node.npz",
        "e6a28194d183658a87f0974afe3f46323106382970a85338f9ce94c20c7b5736",
    ),
    "direction_grid": (
        "data/pr01c_background_snapshots_v048.npz",
        "df136bca7c120054cc45cf2b4fc2bd52acc3d60e6159b0f63c2622de03f2f03c",
    ),
    "scalar_history": (
        "data/pr05b2_source_history_v060.npz",
        "d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1",
    ),
    "source_parent": (
        "data/pr05c2c1b2b1e0_source_derived_parent_v073.npz",
        "c74a2a0e69d6d34c338d19af2f123d1eb32130ac103a68e4494a2c9542eaa958",
    ),
    "single_com_root": (
        "data/pr05c2c1b2b1e1a_single_com_macro_v074.npz",
        "b05e227e7ff8ffd64639e4a432a5789fff08cc89b8bbd63adbcec5fc2da3903c",
    ),
    "two_photon_raman": (
        "data/pr05c2c1b2a_two_photon_raman_source_v068.npz",
        "536154894ce3779cc877a04b490a6e2b4501826d98efd9a12a4a6568dd0eabad",
    ),
}


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def canonicalize_rec_local02_diagnostic(value: float) -> str:
    """Round one nonauthoritative diagnostic to the versioned decimal quantum."""

    number = float(value)
    if not math.isfinite(number):
        raise ValueError("diagnostic must be finite")
    quantized = Decimal(str(number)).quantize(
        Decimal(DIAGNOSTIC_DECIMAL_QUANTUM),
        rounding=ROUND_HALF_EVEN,
    )
    return format(quantized, "f")


def _diagnostic_contract() -> dict[str, Any]:
    return {
        "schema": DIAGNOSTIC_CONTRACT_SCHEMA,
        "formula_version": FREQUENCY_MOMENT_FORMULA,
        "dtype": "<f8",
        "constants": {
            "c_m_s_binary64_hex": float(c).hex(),
            "electron_volt_J_binary64_hex": float(electron_volt).hex(),
            "h_eV_s_binary64_hex": float(H_PLANCK_EV_S).hex(),
            "pi_binary64_hex": float(math.pi).hex(),
        },
        "operation_order": {
            "center_Hz": "fsum(nu0,((x_lo+x_hi)*0.5)*Doppler_width)",
            "halfwidth_Hz": "((x_hi-x_lo)*0.5)*Doppler_width",
            "denominator_m2": "fsum(m*m,(d*d)/3)",
            "numerator_m2": "fsum(m*m,d*d)",
            "mode_measure_m3": "(((16*pi)*d)*denominator_m2)/((c*c)*c)",
            "centroid_Hz": "(m*numerator_m2)/denominator_m2",
        },
        "reduction_order": "ascending_cell_index_python_max_v1",
        "rounding": {
            "mode": "ROUND_HALF_EVEN",
            "absolute_quantum": DIAGNOSTIC_DECIMAL_QUANTUM,
        },
        "fields": {
            path: {
                "classification": "NONAUTHORITATIVE_DIAGNOSTIC",
                "certified_interval_closed": [lower, upper],
            }
            for path, (lower, upper) in DIAGNOSTIC_PATHS.items()
        },
    }


def _value_at_path(receipt: Mapping[str, Any], path: str) -> Any:
    group, name = path.split(".", 1)
    return receipt[group][name]


def _center_halfwidth_frequency_moments(
    intervals: np.ndarray,
    line: LineBoundaryConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Return stable mode measures and centroids from tracked x intervals.

    The scalar loop is deliberate: it fixes binary64 operation and reduction
    order independently of NumPy's SIMD power dispatch.  This is a tested x86
    portability kernel, not a claim of untested cross-architecture bit identity.
    """

    x_intervals = np.asarray(intervals, dtype=np.float64)
    if x_intervals.ndim != 2 or x_intervals.shape[1] != 2:
        raise ValueError("state intervals must have shape (n_state, 2)")
    if not np.all(np.isfinite(x_intervals)):
        raise ValueError("state intervals must be finite")
    measures: list[float] = []
    centroids: list[float] = []
    nu0 = float(line.nu_abs_Hz)
    width = float(line.Doppler_width_Hz)
    speed_of_light = float(c)
    for x_lower, x_upper in x_intervals:
        lower = float(x_lower)
        upper = float(x_upper)
        if not upper > lower:
            raise ValueError("state interval upper edge must exceed lower edge")
        center = math.fsum((nu0, ((lower + upper) * 0.5) * width))
        halfwidth = ((upper - lower) * 0.5) * width
        center_squared = center * center
        halfwidth_squared = halfwidth * halfwidth
        denominator = math.fsum((center_squared, halfwidth_squared / 3.0))
        measures.append(
            (((16.0 * math.pi) * halfwidth) * denominator)
            / ((speed_of_light * speed_of_light) * speed_of_light)
        )
        centroids.append(
            (center * math.fsum((center_squared, halfwidth_squared))) / denominator
        )
    return (
        np.asarray(measures, dtype=np.float64),
        np.asarray(centroids, dtype=np.float64),
    )


def _ordered_max_abs_difference(left: np.ndarray, right: np.ndarray) -> float:
    return max(
        abs(float(left[index]) - float(right[index]))
        for index in range(len(left))
    )


def _ordered_max_relative_difference(left: np.ndarray, right: np.ndarray) -> float:
    return max(
        abs(float(left[index]) - float(right[index])) / abs(float(right[index]))
        for index in range(len(left))
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_tracked_inputs(root: Path) -> dict[str, dict[str, str | bool]]:
    """Return the fixed eight-input identity check without substituting data."""
    result: dict[str, dict[str, str | bool]] = {}
    for name, (relative, expected) in TRACKED_INPUTS.items():
        actual = sha256(root / relative)
        result[name] = {
            "path": relative,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": actual == expected,
        }
    return result


def _network_energy_coordinates_eV(
    network: Any, *, source_energy_rescale: float, portable: bool
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    locked_energy = (
        np.asarray(network["momentum_scale"], dtype=float) * c / electron_volt
    )
    temperature_K = float(network["temperature_K"])
    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=temperature_K, x_red=-21.25, x_blue=21.25
    )
    intervals = np.asarray(network["state_intervals"], dtype=float)
    if portable:
        _, physical_centroid_frequency = _center_halfwidth_frequency_moments(
            intervals, line
        )
    else:
        face_frequency = line.nu_abs_Hz + intervals * line.Doppler_width_Hz
        lower = face_frequency[:, 0]
        upper = face_frequency[:, 1]
        physical_centroid_frequency = (
            0.75 * (upper**4 - lower**4) / (upper**3 - lower**3)
        )
    point_frequency = line.nu_abs_Hz + np.mean(intervals, axis=1) * line.Doppler_width_Hz
    interval_centroid_energy = (
        H_PLANCK_EV_S
        * physical_centroid_frequency
        / float(source_energy_rescale)
    )
    point_energy = (
        H_PLANCK_EV_S * point_frequency / float(source_energy_rescale)
    )
    return locked_energy, point_energy, interval_centroid_energy


def adjacent_energy_feasibility(
    target_energy_eV: np.ndarray, source_energy_eV: np.ndarray
) -> dict[str, Any]:
    """Certificate for a nonnegative 35x8 number/energy map.

    For ``B[target, source]``, each source column is feasible exactly when its
    energy lies in the convex hull of the target COM energies.  The sparse
    two-target witness below is exploratory evidence only: it is not selected
    as a physical deposition map or promoted to source authority.
    """
    targets = np.asarray(target_energy_eV, dtype=float)
    sources = np.asarray(source_energy_eV, dtype=float)
    if targets.shape != (35,) or sources.shape != (8,):
        raise ValueError(
            "REC-LOCAL-02 requires the actual 35-state and 8-native energies"
        )
    if not np.all(np.isfinite(targets)) or not np.all(np.isfinite(sources)):
        raise ValueError("target and source energies must be finite")
    if len(np.unique(targets)) != len(targets):
        raise ValueError("target COM energies must be distinct")
    if not np.all(np.diff(sources) > 0.0):
        raise ValueError("native source energies must be strictly increasing")
    order = np.argsort(targets, kind="stable")
    sorted_targets = targets[order]
    bad = np.flatnonzero(
        (sources < sorted_targets[0]) | (sources > sorted_targets[-1])
    )
    result: dict[str, Any] = {
        "classification": CLASSIFICATION,
        "map_shape": [35, 8],
        "orientation": "B[target_com_cell,source_native_index]",
        "source_native_indices": list(NATIVE_INTERIOR_INDICES),
        "source_energy_range_eV": [float(sources[0]), float(sources[-1])],
        "target_energy_range_eV": [
            float(sorted_targets[0]),
            float(sorted_targets[-1]),
        ],
        "infeasible_source_columns": [int(index) for index in bad],
        "source_strictly_inside_target_hull": bool(
            np.all(sources > sorted_targets[0])
            and np.all(sources < sorted_targets[-1])
        ),
        "physical_map_selected": False,
        "physical_map": None,
        "native_spikes_used_as_finite_cells": False,
    }
    if bad.size:
        result.update(
            {
                "number_and_energy_exact": False,
                "nonnegative": False,
                "feasible": False,
                "reason": "source energy lies outside the target COM energy hull",
                "exploratory_sparse_witness": [],
                "witness_sha256": None,
            }
        )
        return result
    matrix = np.zeros((35, 8), dtype=float)
    sparse_witness: list[dict[str, Any]] = []
    for column, energy in enumerate(sources):
        right_sorted = int(np.searchsorted(sorted_targets, energy, side="left"))
        if right_sorted == 0:
            target_indices = [int(order[0])]
            fractions = [1.0]
        elif right_sorted == len(sorted_targets):
            target_indices = [int(order[-1])]
            fractions = [1.0]
        elif energy == sorted_targets[right_sorted]:
            target_indices = [int(order[right_sorted])]
            fractions = [1.0]
        else:
            left_sorted = right_sorted - 1
            left_energy = sorted_targets[left_sorted]
            right_energy = sorted_targets[right_sorted]
            right_fraction = (energy - left_energy) / (
                right_energy - left_energy
            )
            target_indices = [
                int(order[left_sorted]),
                int(order[right_sorted]),
            ]
            fractions = [float(1.0 - right_fraction), float(right_fraction)]
        matrix[target_indices, column] = fractions
        sparse_witness.append(
            {
                "source_column": column,
                "source_native_index": NATIVE_INTERIOR_INDICES[column],
                "target_indices": target_indices,
                "number_fractions": fractions,
            }
        )
    number_residual = np.sum(matrix, axis=0) - 1.0
    energy_residual = targets @ matrix - sources
    nonzero = matrix[matrix > 0.0]
    result.update(
        {
            "number_and_energy_exact": True,
            "nonnegative": bool(np.all(matrix >= 0.0)),
            "feasible": True,
            "reason": "all source energies lie inside the target COM energy hull",
            "max_abs_number_residual": float(np.max(np.abs(number_residual))),
            "max_abs_energy_residual_eV": float(np.max(np.abs(energy_residual))),
            "max_relative_energy_residual": float(
                np.max(np.abs(energy_residual) / sources)
            ),
            "minimum_nonzero_fraction": float(np.min(nonzero)),
            "exploratory_sparse_witness": sparse_witness,
            "witness_sha256": hashlib.sha256(
                np.asarray(matrix, dtype="<f8").tobytes(order="C")
            ).hexdigest(),
        }
    )
    return result


def _build_rec_local02_diagnostic(
    root: str | Path, *, portable: bool
) -> dict[str, Any]:
    """Evaluate only the bounded source-authority no-go gates."""
    repository = Path(root).resolve()
    hashes = verify_tracked_inputs(repository)
    if not all(bool(item["match"]) for item in hashes.values()):
        raise ValueError("fixed REC-LOCAL-02 authority input hash mismatch")

    network_path = repository / TRACKED_INPUTS["network"][0]
    grid_path = repository / TRACKED_INPUTS["direction_grid"][0]
    parent_path = repository / TRACKED_INPUTS["source_parent"][0]
    history_path = repository / TRACKED_INPUTS["scalar_history"][0]
    boundary_path = repository / TRACKED_INPUTS["boundary_snapshot"][0]
    with (
        np.load(network_path, allow_pickle=False) as network,
        np.load(grid_path, allow_pickle=False) as grid_data,
        np.load(parent_path, allow_pickle=False) as parent,
        np.load(history_path, allow_pickle=False) as history,
    ):
        directions = np.asarray(grid_data["directions"], dtype=float)
        angular_weights = np.asarray(grid_data["angular_weights"], dtype=float)
        occupation = np.asarray(parent["occupation"], dtype=float)
        scalar_occupation = np.asarray(parent["scalar_occupation"], dtype=float)
        parent_source_indices = np.asarray(parent["source_indices"], dtype=int)
        raw_momentum_scale = np.asarray(network["momentum_scale"])
        if (
            raw_momentum_scale.dtype.str != "<f8"
            or raw_momentum_scale.shape != (35,)
            or not raw_momentum_scale.flags.c_contiguous
        ):
            raise ValueError("raw momentum_scale owner layout mismatch")
        raw_momentum_scale_owner = {
            "source_key": "momentum_scale",
            "dtype": raw_momentum_scale.dtype.str,
            "shape": list(raw_momentum_scale.shape),
            "endianness": "little",
            "order": "C",
            "sha256": hashlib.sha256(
                raw_momentum_scale.tobytes(order="C")
            ).hexdigest(),
        }
        mode_measure = np.asarray(network["mode_measure_m3"], dtype=float)
        network_intervals = np.asarray(network["state_intervals"], dtype=float)
        parent_intervals = np.asarray(parent["state_intervals"], dtype=float)
        history_outgoing = np.asarray(history["outgoing_virtual"], dtype=float)
        if (
            occupation.shape != (35, 26)
            or scalar_occupation.shape != (35,)
            or mode_measure.shape != (35,)
            or directions.shape != (26, 3)
            or angular_weights.shape != (26,)
            or history_outgoing.shape != (311, 7489)
        ):
            raise ValueError("actual source parent/COM grid does not have required 35x26 shape")
        if (
            np.any(occupation <= 0.0)
            or np.any(mode_measure <= 0.0)
            or np.any(angular_weights <= 0.0)
        ):
            raise ValueError("actual source occupation and COM measure must be positive")
        interval_residual = float(np.max(np.abs(parent_intervals - network_intervals)))
        isotropy_residual = float(
            np.max(np.abs(occupation - scalar_occupation[:, None]))
        )
        directional_measure = mode_measure[:, None] * angular_weights[None, :]
        harmonic_grid = HarmonicGrid.from_directions(directions, angular_weights, ell_max=3)
        identifiability = audit_full_coupling_identifiability(harmonic_grid)
        boundary = parse_original_hyrec_boundary_snapshot_csv(boundary_path)
        source_energy_rescale = float(
            boundary.trajectory.fsR**2 * boundary.trajectory.meR
        )
        parent_point_energy = np.asarray(
            parent["target_energies_eV_rescaled"], dtype=float
        )
        (
            target_energy,
            computed_point_energy,
            computed_interval_centroid_energy,
        ) = _network_energy_coordinates_eV(
            network,
            source_energy_rescale=source_energy_rescale,
            portable=portable,
        )
        if portable:
            parent_point_formula_residual = _ordered_max_abs_difference(
                parent_point_energy, computed_point_energy
            )
            point_to_locked_owner_difference = _ordered_max_abs_difference(
                parent_point_energy, target_energy
            )
            interval_centroid_to_locked_owner_difference = (
                _ordered_max_abs_difference(
                    computed_interval_centroid_energy, target_energy
                )
            )
        else:
            parent_point_formula_residual = float(
                np.max(np.abs(parent_point_energy - computed_point_energy))
            )
            point_to_locked_owner_difference = float(
                np.max(np.abs(parent_point_energy - target_energy))
            )
            interval_centroid_to_locked_owner_difference = float(
                np.max(np.abs(computed_interval_centroid_energy - target_energy))
            )
        history_energy = np.asarray(history["energy_eV"], dtype=float)
        source_energy = history_energy[list(NATIVE_INTERIOR_INDICES)]
        feasibility = adjacent_energy_feasibility(target_energy, source_energy)
        residuals = {
            sample.side: boundary_sample_reconstruction_residuals(
                sample,
                H_s_inv=boundary.trajectory.H_s_inv,
                nH_cm3=boundary.trajectory.nH_cm3,
                TR_eV_rescaled=boundary.trajectory.TR_eV_rescaled,
                fsR=boundary.trajectory.fsR,
                meR=boundary.trajectory.meR,
                energy_grid_eV=history_energy,
            )
            for sample in boundary.boundaries
        }
        csv_width_Hz = float(
            boundary.boundaries[0].doppler_width_eV
            * source_energy_rescale
            / H_PLANCK_EV_S
        )
        node_temperature_K = float(network["temperature_K"])
        modern_line = LineBoundaryConfig.lyman_alpha(
            temperature_K=node_temperature_K, x_red=-21.25, x_blue=21.25
        )
        modern_width_Hz = modern_line.Doppler_width_Hz
        default_line = LineBoundaryConfig.lyman_alpha(
            temperature_K=3000.0, x_red=-21.25, x_blue=21.25
        )
        intervals = np.asarray(network["state_intervals"], dtype=float)
        if portable:
            default_measure, _ = _center_halfwidth_frequency_moments(
                intervals, default_line
            )
            direct_measure, _ = _center_halfwidth_frequency_moments(
                intervals, modern_line
            )
            default_measure_mismatch = _ordered_max_relative_difference(
                default_measure, mode_measure
            )
            direct_measure_mismatch = _ordered_max_relative_difference(
                direct_measure, mode_measure
            )
        else:
            default_frequency = (
                default_line.nu_abs_Hz + intervals * default_line.Doppler_width_Hz
            )
            default_measure = (
                8.0
                * np.pi
                * (default_frequency[:, 1] ** 3 - default_frequency[:, 0] ** 3)
                / (3.0 * c**3)
            )
            default_measure_mismatch = float(
                np.max(np.abs(default_measure - mode_measure) / mode_measure)
            )
            direct_frequency = (
                modern_line.nu_abs_Hz + intervals * modern_line.Doppler_width_Hz
            )
            direct_measure = (
                8.0
                * np.pi
                * (direct_frequency[:, 1] ** 3 - direct_frequency[:, 0] ** 3)
                / (3.0 * c**3)
            )
            direct_measure_mismatch = float(
                np.max(np.abs(direct_measure - mode_measure) / mode_measure)
            )
        witness_direction = directions[:, 0] - float(np.sum(angular_weights * directions[:, 0]))
        amplitude = 0.5 / float(np.max(np.abs(witness_direction)))
        field_a = 1.0 + amplitude * witness_direction
        field_b = 1.0 - amplitude * witness_direction
        weighted_a = float(np.sum(angular_weights * field_a))
        weighted_b = float(np.sum(angular_weights * field_b))
        distinct = bool(np.max(np.abs(field_a - field_b)) > 0.0)
    result = {
        "schema": (
            RECEIPT_SCHEMA if portable else "REC_LOCAL_02_SOURCE_BOUND_GATE_V1"
        ),
        "status": STATUS,
        "claim": CLAIM,
        "tracked_inputs": hashes,
        "source_representation": {
            "occupation_shape": [35, 26],
            "occupation_minimum": float(np.min(occupation)),
            "occupation_isotropic_max_abs_residual": isotropy_residual,
            "mode_measure_shape": [35],
            "mode_measure_units": "m^-3",
            "mode_measure_minimum_m3": float(np.min(mode_measure)),
            "angular_weight_sum": float(np.sum(angular_weights)),
            "directional_measure_shape": [35, 26],
            "directional_measure_minimum_m3": float(np.min(directional_measure)),
            "direction_shape": [26, 3],
            "weight_count": 26,
            "parent_network_interval_max_abs_residual": interval_residual,
            "scalar_history_outgoing_virtual_shape": [311, 7489],
            "scalar_history_angular_rank": 1,
            "native_interior_indices": list(NATIVE_INTERIOR_INDICES),
            "native_interface_edges": [list(edge) for edge in NATIVE_INTERFACE_EDGES],
            "native_spikes_define_cells": False,
            "net_source_jump_is_total_interface_crossing_flux": False,
            "source_parent_uses_index_144": bool(144 in parent_source_indices),
            "source_parent_source_index_144_target_rows": [
                int(index)
                for index in np.flatnonzero(parent_source_indices == 144)
            ],
        },
        "source_flux_parity_residuals": residuals,
        "adjacent_energy_moment_feasibility": feasibility,
        "target_energy_binding": {
            "source": "tracked CollisionNetwork.momentum_scale",
            "units": "eV",
            "source_energy_rescale": source_energy_rescale,
            "momentum_scale_units": "kg m s^-1",
            "physical_cell_energy_definition": "momentum_scale*c/electron_volt",
            "locked_target_energy_sha256": hashlib.sha256(
                np.asarray(target_energy, dtype="<f8").tobytes(order="C")
            ).hexdigest(),
            "legacy_interval_centroid_definition": (
                "H_PLANCK_EV_S*0.75*(nu_hi^4-nu_lo^4)/"
                "(nu_hi^3-nu_lo^3)/(fsR^2*meR)"
            ),
            "legacy_interval_centroid_is_authoritative": False,
            "legacy_interval_centroid_to_locked_owner_max_abs_difference_eV": (
                interval_centroid_to_locked_owner_difference
            ),
            "source_parent_point_energy_definition": (
                "point-characteristic evaluation at arithmetic x centre"
            ),
            "source_parent_point_formula_max_abs_residual_eV": (
                parent_point_formula_residual
            ),
            "source_parent_point_to_locked_owner_max_abs_difference_eV": (
                point_to_locked_owner_difference
            ),
        },
        "doppler_width_reconciliation": {
            "direct_node_temperature_K": node_temperature_K,
            "direct_node_line_x": [-21.25, 21.25],
            "csv_boundary_width_Hz": csv_width_Hz,
            "modern_line_boundary_width_Hz": modern_width_Hz,
            "difference_Hz": modern_width_Hz - csv_width_Hz,
            "relative_difference": (modern_width_Hz - csv_width_Hz)
            / csv_width_Hz,
            "relative_difference_denominator": "csv_boundary_width_Hz",
            "selected_definition": "NONE_BLOCKED_NO_SILENT_SELECTION",
            "csv_definition": "doppler_width_eV*fsR^2*meR/H_PLANCK_EV_S",
            "modern_definition": (
                "LineBoundaryConfig.lyman_alpha(temperature_K=direct-node "
                "temperature)"
            ),
            "direct_node_network_measure_max_relative_mismatch": direct_measure_mismatch,
            "default_3000K_network_measure_max_relative_mismatch": default_measure_mismatch,
            "default_3000K_from_network_permitted": False,
            "default_3000K_from_network_status": "INCOMPATIBLE_WITH_DIRECT_NODE_MEASURE",
        },
        "full_coupling_identifiability": {
            "native_history_angular_rank": identifiability.native_history_angular_rank,
            "required_angular_rank": identifiability.required_angular_rank,
            "com_face_trace_source_defined": identifiability.com_face_trace_source_defined,
            "bounded_no_go": identifiability.bounded_no_go,
        },
        "positive_nonidentifiability_witness": {
            "field_a_minimum": float(np.min(field_a)),
            "field_b_minimum": float(np.min(field_b)),
            "weighted_mean_a": weighted_a,
            "weighted_mean_b": weighted_b,
            "weighted_mean_residual": abs(weighted_a - weighted_b),
            "fields_distinct": distinct,
            "source_defined_face_reconstruction": False,
        },
        "conventions_if_unblocked": {
            "metric_signature": "(-,+,+,+)",
            "frame": "hydrogen orthonormal frame",
            "frequency": "ordinary frequency in Hz",
            "energy": "joule for physical ledgers",
            "time_variable": "eta=ln(a), d/dt=H*d/deta",
        },
        "blocking_conditions": [
            "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
        ],
        "stop_after_gate": "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
        "not_run": [
            "deposition_map_selection",
            "full_moving_map_jvp",
            "photon_and_atomic_four_force_assembly",
            "number_energy_four_force_balance",
            "thermal_and_spectral_response",
            "independent_directional_jvp",
            "restart_and_history_transactions",
            "physical_reference_tests",
        ],
    }
    if portable:
        result["classification"] = CLASSIFICATION
        result["target_energy_binding"][
            "raw_momentum_scale_owner"
        ] = raw_momentum_scale_owner
    return result


def _portable_diagnostic_values(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        path: {
            "binary64": float(_value_at_path(receipt, path)),
            "canonical_decimal": canonicalize_rec_local02_diagnostic(
                float(_value_at_path(receipt, path))
            ),
        }
        for path in DIAGNOSTIC_PATHS
    }


def _validate_portable_diagnostics(receipt: Mapping[str, Any]) -> None:
    contract = receipt.get("diagnostic_contract")
    if contract != _diagnostic_contract():
        raise ValueError("diagnostic contract mismatch")
    portable = receipt.get("portable_diagnostics")
    if not isinstance(portable, Mapping) or portable.get("schema") != (
        PORTABLE_DIAGNOSTICS_SCHEMA
    ):
        raise ValueError("portable diagnostic schema mismatch")
    values = portable.get("values")
    if not isinstance(values, Mapping) or set(values) != set(DIAGNOSTIC_PATHS):
        raise ValueError("portable diagnostic field set mismatch")
    for path, (lower_text, upper_text) in DIAGNOSTIC_PATHS.items():
        value = float(_value_at_path(receipt, path))
        record = values[path]
        if not isinstance(record, Mapping) or float(record.get("binary64")) != value:
            raise ValueError(f"portable diagnostic binary64 mismatch: {path}")
        canonical = canonicalize_rec_local02_diagnostic(value)
        if record.get("canonical_decimal") != canonical:
            raise ValueError(f"portable diagnostic canonical mismatch: {path}")
        decimal_value = Decimal(str(value))
        if not Decimal(lower_text) <= decimal_value <= Decimal(upper_text):
            raise ValueError(f"diagnostic interval failure: {path}")


def rec_local02_diagnostic_contract_sha256(receipt: Mapping[str, Any]) -> str:
    contract = receipt.get("diagnostic_contract")
    if not isinstance(contract, Mapping):
        raise ValueError("diagnostic contract is absent")
    return _canonical_sha256(contract)


def rec_local02_authority_projection(
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the portable scientific authority projection.

    Raw diagnostic floats and their canonical decimal presentations are
    deliberately excluded.  Their versioned contract and pass/fail predicate
    remain bound, so an in-range presentation drift cannot acquire authority.
    """

    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise ValueError("portable receipt schema mismatch")
    _validate_portable_diagnostics(receipt)
    feasibility = receipt["adjacent_energy_moment_feasibility"]
    binding = receipt["target_energy_binding"]
    identifiability = receipt["full_coupling_identifiability"]
    witness = receipt["positive_nonidentifiability_witness"]
    source_flux = receipt["source_flux_parity_residuals"]
    representation = receipt["source_representation"]
    doppler = receipt["doppler_width_reconciliation"]
    return {
        "schema": AUTHORITY_PROJECTION_SCHEMA,
        "receipt_schema": RECEIPT_SCHEMA,
        "status": receipt["status"],
        "claim": receipt["claim"],
        "classification": receipt["classification"],
        "tracked_inputs": receipt["tracked_inputs"],
        "owners": {
            "raw_momentum_scale": binding["raw_momentum_scale_owner"],
            "locked_target_energy": {
                "definition": binding["physical_cell_energy_definition"],
                "dtype": "<f8",
                "shape": [35],
                "order": "C",
                "sha256": binding["locked_target_energy_sha256"],
                "c_m_s_binary64_hex": float(c).hex(),
                "electron_volt_J_binary64_hex": float(electron_volt).hex(),
            },
        },
        "source_representation_contract": {
            "direction_shape": representation["direction_shape"],
            "directional_measure_shape": representation[
                "directional_measure_shape"
            ],
            "mode_measure_shape": representation["mode_measure_shape"],
            "mode_measure_units": representation["mode_measure_units"],
            "native_interface_edges": representation["native_interface_edges"],
            "native_interior_indices": representation["native_interior_indices"],
            "native_spikes_define_cells": representation[
                "native_spikes_define_cells"
            ],
            "net_source_jump_is_total_interface_crossing_flux": representation[
                "net_source_jump_is_total_interface_crossing_flux"
            ],
            "occupation_shape": representation["occupation_shape"],
            "scalar_history_angular_rank": representation[
                "scalar_history_angular_rank"
            ],
            "scalar_history_outgoing_virtual_shape": representation[
                "scalar_history_outgoing_virtual_shape"
            ],
            "source_parent_source_index_144_target_rows": representation[
                "source_parent_source_index_144_target_rows"
            ],
            "source_parent_uses_index_144": representation[
                "source_parent_uses_index_144"
            ],
            "weight_count": representation["weight_count"],
        },
        "target_energy_contract": {
            "momentum_scale_units": binding["momentum_scale_units"],
            "physical_cell_energy_definition": binding[
                "physical_cell_energy_definition"
            ],
            "source": binding["source"],
            "source_energy_rescale": binding["source_energy_rescale"],
            "source_parent_point_energy_definition": binding[
                "source_parent_point_energy_definition"
            ],
            "legacy_interval_centroid_definition": binding[
                "legacy_interval_centroid_definition"
            ],
            "legacy_interval_centroid_is_authoritative": binding[
                "legacy_interval_centroid_is_authoritative"
            ],
            "units": binding["units"],
        },
        "doppler_contract": {
            "csv_definition": doppler["csv_definition"],
            "default_3000K_from_network_permitted": doppler[
                "default_3000K_from_network_permitted"
            ],
            "default_3000K_from_network_status": doppler[
                "default_3000K_from_network_status"
            ],
            "direct_node_line_x": doppler["direct_node_line_x"],
            "modern_definition": doppler["modern_definition"],
            "relative_difference_denominator": doppler[
                "relative_difference_denominator"
            ],
            "selected_definition": doppler["selected_definition"],
        },
        "feasibility_contract": {
            "classification": feasibility["classification"],
            "map_shape": feasibility["map_shape"],
            "native_spikes_used_as_finite_cells": feasibility[
                "native_spikes_used_as_finite_cells"
            ],
            "orientation": feasibility["orientation"],
            "reason": feasibility["reason"],
            "source_native_indices": feasibility["source_native_indices"],
            "source_strictly_inside_target_hull": feasibility[
                "source_strictly_inside_target_hull"
            ],
            "infeasible_source_columns": feasibility[
                "infeasible_source_columns"
            ],
        },
        "conventions_if_unblocked": receipt["conventions_if_unblocked"],
        "invariant_predicates": {
            "tracked_inputs_all_match": all(
                bool(item["match"])
                for item in receipt["tracked_inputs"].values()
            ),
            "source_flux_parity_within_4e-13": all(
                max(float(value) for value in residuals.values()) < 4.0e-13
                for residuals in source_flux.values()
            ),
            "feasible": bool(feasibility["feasible"]),
            "nonnegative": bool(feasibility["nonnegative"]),
            "number_and_energy_exact": bool(
                feasibility["number_and_energy_exact"]
            ),
            "number_residual_exact_zero": (
                float(feasibility["max_abs_number_residual"]) == 0.0
            ),
            "energy_residual_within_2e-15_eV": (
                float(feasibility["max_abs_energy_residual_eV"]) < 2.0e-15
            ),
            "physical_map_selected": bool(feasibility["physical_map_selected"]),
            "physical_map_is_absent": feasibility["physical_map"] is None,
            "native_history_angular_rank": int(
                identifiability["native_history_angular_rank"]
            ),
            "required_angular_rank": int(identifiability["required_angular_rank"]),
            "com_face_trace_source_defined": bool(
                identifiability["com_face_trace_source_defined"]
            ),
            "bounded_no_go": bool(identifiability["bounded_no_go"]),
            "positive_fields_distinct": bool(witness["fields_distinct"]),
            "positive_fields_nonnegative": (
                float(witness["field_a_minimum"]) >= 0.0
                and float(witness["field_b_minimum"]) >= 0.0
            ),
            "positive_witness_mean_within_2e-15": (
                float(witness["weighted_mean_residual"]) < 2.0e-15
            ),
            "positive_witness_source_defined_face_reconstruction": bool(
                witness["source_defined_face_reconstruction"]
            ),
            "angular_weight_normalized_within_2e-15": (
                abs(float(representation["angular_weight_sum"]) - 1.0) < 2.0e-15
            ),
            "directional_measure_positive": (
                float(representation["directional_measure_minimum_m3"]) > 0.0
            ),
            "mode_measure_positive": (
                float(representation["mode_measure_minimum_m3"]) > 0.0
            ),
            "occupation_positive": (
                float(representation["occupation_minimum"]) > 0.0
            ),
            "occupation_isotropic_exact": (
                float(representation["occupation_isotropic_max_abs_residual"])
                == 0.0
            ),
            "parent_network_intervals_exact": (
                float(representation["parent_network_interval_max_abs_residual"])
                == 0.0
            ),
            "source_parent_point_formula_exact": (
                float(binding["source_parent_point_formula_max_abs_residual_eV"])
                == 0.0
            ),
            "diagnostic_intervals_valid": True,
        },
        "exploratory_witness_sha256": feasibility["witness_sha256"],
        "diagnostic_contract_sha256": rec_local02_diagnostic_contract_sha256(
            receipt
        ),
        "blocking_conditions": receipt["blocking_conditions"],
        "stop_after_gate": receipt["stop_after_gate"],
        "not_run": receipt["not_run"],
    }


def rec_local02_authority_sha256(receipt: Mapping[str, Any]) -> str:
    return _canonical_sha256(rec_local02_authority_projection(receipt))


def validate_rec_local02_receipt(receipt: Mapping[str, Any]) -> None:
    """Fail closed unless stored projections match fresh portable semantics."""

    _validate_portable_diagnostics(receipt)
    diagnostic_sha256 = rec_local02_diagnostic_contract_sha256(receipt)
    contract = receipt.get("receipt_contract")
    if not isinstance(contract, Mapping) or contract.get("schema") != (
        PORTABLE_RECEIPT_CONTRACT_SCHEMA
    ):
        raise ValueError("portable receipt contract mismatch")
    if set(contract) != {
        "schema",
        "authority_projection_schema",
        "authority_projection_sha256",
        "diagnostic_contract_sha256",
        "raw_receipt_sha256_role",
        "cross_architecture_bit_identity_claimed",
    }:
        raise ValueError("portable receipt contract field set mismatch")
    if contract.get("authority_projection_schema") != AUTHORITY_PROJECTION_SCHEMA:
        raise ValueError("authority projection schema mismatch")
    if contract.get("raw_receipt_sha256_role") != (
        "ARCHIVAL_PUBLICATION_SEAL_ONLY_NOT_PORTABLE_AUTHORITY"
    ):
        raise ValueError("raw receipt digest role mismatch")
    if contract.get("cross_architecture_bit_identity_claimed") is not False:
        raise ValueError("cross-architecture identity claim mismatch")
    if contract.get("diagnostic_contract_sha256") != diagnostic_sha256:
        raise ValueError("diagnostic contract digest mismatch")
    projection = rec_local02_authority_projection(receipt)
    if receipt.get("authority_projection") != projection:
        raise ValueError("authority projection mismatch")
    authority_sha256 = _canonical_sha256(projection)
    if contract.get("authority_projection_sha256") != authority_sha256:
        raise ValueError("authority projection digest mismatch")


def build_rec_local02_legacy_diagnostic(root: str | Path) -> dict[str, Any]:
    """Reproduce the V1 SIMD-sensitive artifact for forensic comparison only."""

    return _build_rec_local02_diagnostic(root, portable=False)


def build_rec_local02_diagnostic(root: str | Path) -> dict[str, Any]:
    """Build the V2 portable source-authority no-go receipt."""

    result = _build_rec_local02_diagnostic(root, portable=True)
    result["diagnostic_contract"] = _diagnostic_contract()
    result["portable_diagnostics"] = {
        "schema": PORTABLE_DIAGNOSTICS_SCHEMA,
        "values": _portable_diagnostic_values(result),
    }
    result["authority_projection"] = rec_local02_authority_projection(result)
    result["receipt_contract"] = {
        "schema": PORTABLE_RECEIPT_CONTRACT_SCHEMA,
        "authority_projection_schema": AUTHORITY_PROJECTION_SCHEMA,
        "authority_projection_sha256": _canonical_sha256(
            result["authority_projection"]
        ),
        "diagnostic_contract_sha256": rec_local02_diagnostic_contract_sha256(
            result
        ),
        "raw_receipt_sha256_role": (
            "ARCHIVAL_PUBLICATION_SEAL_ONLY_NOT_PORTABLE_AUTHORITY"
        ),
        "cross_architecture_bit_identity_claimed": False,
    }
    validate_rec_local02_receipt(result)
    return result

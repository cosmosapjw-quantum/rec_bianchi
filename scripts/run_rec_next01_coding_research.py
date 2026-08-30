#!/usr/bin/env python3
"""Materialize the REC-NEXT-01 portable-receipt and geometry-spike record."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig
from full_bianchi_hyrec.trajectory.directional_face_admission import (
    AngularQuadratureContract,
    BLOCKED_ANGULAR_FRAME_CONTRACT,
    BLOCKED_ANGULAR_REMAP_AUTHORITY,
    BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY,
    BLOCKED_FREQUENCY_SPEED_ZERO_EVENT_RESTART_CONTRACT,
    BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION,
    CLOSURE_DEFINED_DIRECTIONAL_SURROGATE_V1,
    FIXED_NODE_COUPLED,
    HYDROGEN_FRAME,
    HYDROGEN_TETRAD,
    ORDINARY_FREQUENCY_HZ,
    SOURCE_IDENTICAL_DIRECTIONAL_FACE,
    SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
    THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
    audit_directional_face_readiness,
    compute_hydrogen_frame_face_kinematics,
    compute_legacy_untagged_normal_face_kinematics,
    run_manufactured_52_ray_geometry_witness,
)
from full_bianchi_hyrec.trajectory.physical_split_reference import (
    CLAIM,
    STATUS,
    build_rec_local02_diagnostic,
    validate_rec_local02_receipt,
)


BACKGROUND = ROOT / "data/pr01c_background_snapshots_v048.npz"
NETWORK = ROOT / "data/z1100_direct_network_node.npz"
TAU0 = 0.6072662349590596
DEFAULT_OUTPUT = (
    ROOT
    / "artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_next01_coding_research"
    / "REC_NEXT_01_CODING_RESEARCH.json"
)


def _encoded(record: dict) -> bytes:
    return (
        json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")


def _semantic_projection(record: dict) -> dict:
    """Project portable decisions while leaving raw diagnostics archival."""

    if record.get("schema") != "REC_NEXT_01_CODING_RESEARCH_V1":
        raise ValueError("coding research record schema mismatch")
    phase_a = record["phase_a"]
    phase_b = record["phase_b"]
    geometry = phase_b["manufactured_geometry"]
    return {
        "schema": "REC_NEXT_01_CODING_RESEARCH_SEMANTIC_PROJECTION_V1",
        "canonical_start": record["canonical_start"],
        "phase_a": {
            "portable_receipt_contract": phase_a["portable_receipt_contract"],
            "receipt_schema": phase_a["receipt_schema"],
            "authority_projection_sha256": phase_a[
                "authority_projection_sha256"
            ],
            "diagnostic_contract_sha256": phase_a[
                "diagnostic_contract_sha256"
            ],
            "raw_momentum_scale_owner_sha256": phase_a[
                "raw_momentum_scale_owner_sha256"
            ],
            "locked_target_energy_sha256": phase_a[
                "locked_target_energy_sha256"
            ],
            "raw_receipt_sha256_role": phase_a["raw_receipt_sha256_role"],
            "cross_architecture_bit_identity_claimed": phase_a[
                "cross_architecture_bit_identity_claimed"
            ],
        },
        "phase_b": {
            "requested_authority_label": phase_b["requested_authority_label"],
            "authority_labels": phase_b["authority_labels"],
            "reserved_label": phase_b["reserved_label"],
            "spike_frame_hypothesis": phase_b["spike_frame_hypothesis"],
            "production_frame_contract_selected": phase_b[
                "production_frame_contract_selected"
            ],
            "quadrature_contract": phase_b["quadrature_contract"],
            "frame_ambiguity": phase_b["frame_ambiguity"],
            "manufactured_geometry": {
                "authority_label": geometry["authority_label"],
                "ray_count": geometry["ray_count"],
                "red_ray_count": geometry["red_ray_count"],
                "blue_ray_count": geometry["blue_ray_count"],
                "frequency_residual_within_3e-13": (
                    float(geometry["maximum_frequency_relative_residual"])
                    < 3.0e-13
                ),
                "occupation_residual_exact_zero": (
                    float(geometry["maximum_occupation_residual"]) == 0.0
                ),
                "positive_doppler_factor": (
                    float(geometry["minimum_doppler_factor"]) > 0.0
                ),
                "nonzero_frequency_speed": (
                    float(geometry["minimum_abs_frequency_speed_s_inv"]) > 0.0
                ),
                "physical_face_admitted": geometry["physical_face_admitted"],
                "blockers": geometry["blockers"],
            },
            "readiness": phase_b["readiness"],
            "production_blockers": phase_b["production_blockers"],
            "production_integration_performed": phase_b[
                "production_integration_performed"
            ],
            "physical_face_materialized": phase_b[
                "physical_face_materialized"
            ],
        },
        "status": record["status"],
        "claim": record["claim"],
        "blocking_conditions": record["blocking_conditions"],
        "not_run": record["not_run"],
    }


def _semantic_sha256(record: dict) -> str:
    encoded = json.dumps(
        _semantic_projection(record),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_record() -> dict:
    receipt = build_rec_local02_diagnostic(ROOT)
    validate_rec_local02_receipt(receipt)
    with np.load(BACKGROUND, allow_pickle=False) as data:
        directions = np.asarray(data["directions"], dtype=float)
        weights = np.asarray(data["angular_weights"], dtype=float)
    with np.load(NETWORK, allow_pickle=False) as data:
        line = LineBoundaryConfig.lyman_alpha(
            temperature_K=float(data["temperature_K"]),
            x_red=-21.25,
            x_blue=21.25,
        )
    quadrature = AngularQuadratureContract(
        directions=directions,
        weights=weights,
        frame=HYDROGEN_FRAME,
        tetrad=HYDROGEN_TETRAD,
        frequency_measure=ORDINARY_FREQUENCY_HZ,
        source_sha256=sha256(BACKGROUND),
    )

    tilted = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_VI_h_tilted_large_shear"
    )
    tilted_snapshot = tilted.snapshot_at_tau(float(tilted.tau[0]))
    tagged = compute_hydrogen_frame_face_kinematics(
        snapshot=tilted_snapshot,
        line=line,
        quadrature=quadrature,
    )
    legacy = compute_legacy_untagged_normal_face_kinematics(
        snapshot=tilted_snapshot,
        line=line,
        quadrature=quadrature,
    )
    differing = (tagged.red_inflow != legacy.red_inflow) | (
        tagged.blue_inflow != legacy.blue_inflow
    )

    bianchi_ii = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_II_large_shear"
    )
    geometry_snapshot = bianchi_ii.snapshot_at_tau(TAU0 + 8.5e-5)
    geometry = run_manufactured_52_ray_geometry_witness(
        snapshot=geometry_snapshot,
        line=line,
        quadrature=quadrature,
        logarithmic_frequency_offset=1.0e-4,
        n_steps=64,
    )
    readiness = audit_directional_face_readiness(
        source_channels=(),
        incoming_authority_present=False,
        evolution_mode=FIXED_NODE_COUPLED,
        angular_remap_contract_sha256=None,
        speed_zero_event_restart_contract_sha256=None,
    )
    return {
        "schema": "REC_NEXT_01_CODING_RESEARCH_V1",
        "canonical_start": {
            "commit": "37a943347bf319af998230bb77c6f89827feddff",
            "tree": "da1b3062bd3e115df9b55c7fef933b8f8379cd7a",
            "parent": "dd0e080400bc76d6c5e6af382717e613a9fb32f8",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "phase_a": {
            "portable_receipt_contract": "PASS",
            "receipt_schema": receipt["schema"],
            "authority_projection_sha256": receipt["receipt_contract"][
                "authority_projection_sha256"
            ],
            "diagnostic_contract_sha256": receipt["receipt_contract"][
                "diagnostic_contract_sha256"
            ],
            "raw_momentum_scale_owner_sha256": receipt[
                "target_energy_binding"
            ]["raw_momentum_scale_owner"]["sha256"],
            "locked_target_energy_sha256": receipt["target_energy_binding"][
                "locked_target_energy_sha256"
            ],
            "portable_diagnostics": receipt["portable_diagnostics"],
            "raw_receipt_sha256_role": receipt["receipt_contract"][
                "raw_receipt_sha256_role"
            ],
            "cross_architecture_bit_identity_claimed": False,
        },
        "phase_b": {
            "requested_authority_label": (
                THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1
            ),
            "authority_labels": [
                SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
                THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
                CLOSURE_DEFINED_DIRECTIONAL_SURROGATE_V1,
            ],
            "reserved_label": SOURCE_IDENTICAL_DIRECTIONAL_FACE,
            "spike_frame_hypothesis": HYDROGEN_FRAME,
            "production_frame_contract_selected": False,
            "quadrature_contract": {
                "point_count": 26,
                "frame": quadrature.frame,
                "tetrad": quadrature.tetrad,
                "frequency_measure": quadrature.frequency_measure,
                "source_sha256": quadrature.source_sha256,
                "semantic_sha256": quadrature.semantic_sha256,
            },
            "frame_ambiguity": {
                "model": "Bianchi_VI_h_tilted_large_shear",
                "tau": float(tilted.tau[0]),
                "hydrogen_frame_red_inflow_count": int(
                    np.count_nonzero(tagged.red_inflow)
                ),
                "hydrogen_frame_blue_inflow_count": int(
                    np.count_nonzero(tagged.blue_inflow)
                ),
                "legacy_normal_red_inflow_count": int(
                    np.count_nonzero(legacy.red_inflow)
                ),
                "legacy_normal_blue_inflow_count": int(
                    np.count_nonzero(legacy.blue_inflow)
                ),
                "differing_node_count": int(np.count_nonzero(differing)),
                "red_inflow_rule": "v_red > 0",
                "blue_inflow_rule": "v_blue < 0",
            },
            "manufactured_geometry": asdict(geometry),
            "readiness": asdict(readiness),
            "production_blockers": [
                BLOCKED_ANGULAR_FRAME_CONTRACT,
                BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY,
                BLOCKED_ANGULAR_REMAP_AUTHORITY,
                BLOCKED_FREQUENCY_SPEED_ZERO_EVENT_RESTART_CONTRACT,
                BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION,
                "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
            ],
            "production_integration_performed": False,
            "physical_face_materialized": False,
        },
        "status": STATUS,
        "claim": CLAIM,
        "blocking_conditions": [
            "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT"
        ],
        "not_run": receipt["not_run"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check-record", type=Path)
    arguments = parser.parse_args(argv)
    if arguments.check_record is not None:
        try:
            check_path = arguments.check_record
            if not check_path.is_absolute():
                check_path = ROOT / check_path
            stored_bytes = check_path.resolve().read_bytes()
            stored = json.loads(stored_bytes)
            fresh = build_record()
            stored_semantic_sha256 = _semantic_sha256(stored)
            fresh_semantic_sha256 = _semantic_sha256(fresh)
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            print(f"coding research record validation failed: {exc}", file=sys.stderr)
            return 2
        summary = {
            "schema": "REC_NEXT_01_CODING_RESEARCH_CHECK_V1",
            "portable_semantics_match": (
                stored_semantic_sha256 == fresh_semantic_sha256
            ),
            "stored_semantic_sha256": stored_semantic_sha256,
            "fresh_semantic_sha256": fresh_semantic_sha256,
            "stored_raw_sha256": hashlib.sha256(stored_bytes).hexdigest(),
            "fresh_raw_sha256": hashlib.sha256(_encoded(fresh)).hexdigest(),
            "raw_bytes_match": stored_bytes == _encoded(fresh),
            "raw_sha256_role": "ARCHIVAL_PUBLICATION_SEAL_ONLY",
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0 if summary["portable_semantics_match"] else 1
    output = arguments.output
    if not output.is_absolute():
        output = ROOT / output
    output = output.resolve()
    if output == ROOT:
        raise ValueError("coding-research output must be a file path")
    record = build_record()
    encoded = _encoded(record)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encoded)
    print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

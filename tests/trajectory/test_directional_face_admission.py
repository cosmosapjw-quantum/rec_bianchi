from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig


ROOT = Path(__file__).resolve().parents[2]
BACKGROUND = ROOT / "data/pr01c_background_snapshots_v048.npz"
NETWORK = ROOT / "data/z1100_direct_network_node.npz"
TAU0 = 0.6072662349590596


def admission_module():
    return importlib.import_module(
        "full_bianchi_hyrec.trajectory.directional_face_admission"
    )


def inputs():
    with np.load(BACKGROUND, allow_pickle=False) as data:
        directions = np.asarray(data["directions"], dtype=float)
        weights = np.asarray(data["angular_weights"], dtype=float)
    with np.load(NETWORK, allow_pickle=False) as data:
        line = LineBoundaryConfig.lyman_alpha(
            temperature_K=float(data["temperature_K"]),
            x_red=-21.25,
            x_blue=21.25,
        )
    return directions, weights, line


def contract():
    module = admission_module()
    directions, weights, _ = inputs()
    return module.AngularQuadratureContract(
        directions=directions,
        weights=weights,
        frame=module.HYDROGEN_FRAME,
        tetrad=module.HYDROGEN_TETRAD,
        frequency_measure=module.ORDINARY_FREQUENCY_HZ,
        source_sha256=hashlib.sha256(BACKGROUND.read_bytes()).hexdigest(),
    )


def test_tagged_hydrogen_frame_exposes_legacy_inflow_mask_ambiguity() -> None:
    module = admission_module()
    _directions, _weights, line = inputs()
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_VI_h_tilted_large_shear"
    )
    snapshot = sequence.snapshot_at_tau(float(sequence.tau[0]))

    tagged = module.compute_hydrogen_frame_face_kinematics(
        snapshot=snapshot,
        line=line,
        quadrature=contract(),
    )
    legacy = module.compute_legacy_untagged_normal_face_kinematics(
        snapshot=snapshot,
        line=line,
        quadrature=contract(),
    )

    assert np.count_nonzero(tagged.red_inflow) == 2
    assert np.count_nonzero(tagged.blue_inflow) == 24
    assert np.count_nonzero(legacy.red_inflow) == 3
    assert np.count_nonzero(legacy.blue_inflow) == 23
    differing = (tagged.red_inflow != legacy.red_inflow) | (
        tagged.blue_inflow != legacy.blue_inflow
    )
    assert np.count_nonzero(differing) == 5
    assert np.array_equal(tagged.red_inflow, tagged.red_speed_x_s_inv > 0.0)
    assert np.array_equal(tagged.blue_inflow, tagged.blue_speed_x_s_inv < 0.0)


def test_actual_grid_runs_52_manufactured_rays_without_physical_admission() -> None:
    module = admission_module()
    _directions, _weights, line = inputs()
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_II_large_shear"
    )
    snapshot = sequence.snapshot_at_tau(TAU0 + 8.5e-5)

    witness = module.run_manufactured_52_ray_geometry_witness(
        snapshot=snapshot,
        line=line,
        quadrature=contract(),
        logarithmic_frequency_offset=1.0e-4,
        n_steps=64,
    )

    assert witness.authority_label == "GEOMETRY_ONLY_MANUFACTURED"
    assert witness.ray_count == 52
    assert witness.red_ray_count == witness.blue_ray_count == 26
    assert witness.maximum_frequency_relative_residual < 3.0e-13
    assert witness.maximum_occupation_residual == 0.0
    assert len(witness.result_sha256) == 64
    assert not witness.physical_face_admitted
    assert witness.blockers == (
        module.BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY,
        module.BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION,
    )


def test_frequency_speed_zero_requires_event_contract() -> None:
    module = admission_module()
    _directions, _weights, line = inputs()
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_II_large_shear"
    )
    snapshot = sequence.snapshot_at_tau(TAU0)

    with pytest.raises(
        module.FrequencySpeedZeroEventRequired,
        match=r"frequency-speed zero.*nodes \[0, 1\].*event",
    ) as exc_info:
        module.run_manufactured_52_ray_geometry_witness(
            snapshot=snapshot,
            line=line,
            quadrature=contract(),
            logarithmic_frequency_offset=1.0e-4,
            n_steps=64,
        )
    assert exc_info.value.node_indices == (0, 1)


def test_missing_source_law_and_fixed_node_remap_fail_closed() -> None:
    module = admission_module()
    audit = module.audit_directional_face_readiness(
        source_channels=(),
        incoming_authority_present=False,
        evolution_mode="FIXED_NODE_COUPLED",
        angular_remap_contract_sha256=None,
        speed_zero_event_restart_contract_sha256=None,
    )

    assert not audit.declared_contract_complete
    assert not audit.physical_face_admitted
    assert not audit.production_integration_authorized
    assert audit.requested_authority_label == (
        "THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1"
    )
    assert module.BLOCKED_ANGULAR_FRAME_CONTRACT in audit.blockers
    assert module.BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY in audit.blockers
    assert module.BLOCKED_ANGULAR_REMAP_AUTHORITY in audit.blockers
    assert (
        module.BLOCKED_FREQUENCY_SPEED_ZERO_EVENT_RESTART_CONTRACT
        in audit.blockers
    )
    assert (
        module.BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION
        in audit.blockers
    )
    assert "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT" in audit.blockers


def test_source_manifest_rejects_missing_duplicate_units_and_hashes() -> None:
    module = admission_module()
    valid = tuple(
        module.DirectionalSourceChannel(
            name=name,
            owner_label="SOURCE_IDENTICAL_SCALAR_PRIMITIVE",
            coefficient_units="s^-1",
            source_sha256=hashlib.sha256(name.encode()).hexdigest(),
        )
        for name in module.REQUIRED_SOURCE_CHANNELS
    )
    assert module.audit_directional_source_manifest(valid)["declared_complete"]

    missing = module.audit_directional_source_manifest(valid[:-1])
    assert not missing["declared_complete"]
    assert missing["missing_channels"] == [module.REQUIRED_SOURCE_CHANNELS[-1]]

    duplicate = module.audit_directional_source_manifest((*valid, valid[0]))
    assert not duplicate["declared_complete"]
    assert duplicate["duplicate_channels"] == [valid[0].name]

    with pytest.raises(ValueError, match="units"):
        module.DirectionalSourceChannel(
            name="virtual_spike",
            owner_label="SOURCE_IDENTICAL_SCALAR_PRIMITIVE",
            coefficient_units="eV",
            source_sha256="a" * 64,
        )
    with pytest.raises(ValueError, match="SHA-256"):
        module.DirectionalSourceChannel(
            name="virtual_spike",
            owner_label="SOURCE_IDENTICAL_SCALAR_PRIMITIVE",
            coefficient_units="s^-1",
            source_sha256="not-a-hash",
        )


def test_declarations_cannot_self_promote_to_physical_authority() -> None:
    module = admission_module()
    declarations = tuple(
        module.DirectionalSourceChannel(
            name=name,
            owner_label=module.SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
            coefficient_units="s^-1",
            source_sha256=hashlib.sha256(name.encode()).hexdigest(),
        )
        for name in module.REQUIRED_SOURCE_CHANNELS
    )
    common = {
        "source_channels": declarations,
        "incoming_authority_present": True,
        "evolution_mode": module.LAGRANGIAN_SAMPLER,
        "angular_remap_contract_sha256": None,
        "speed_zero_event_restart_contract_sha256": "a" * 64,
    }

    untyped = module.audit_directional_face_readiness(
        quadrature=object(),
        **common,
    )
    assert module.BLOCKED_ANGULAR_FRAME_CONTRACT in untyped.blockers
    assert not untyped.physical_face_admitted

    declared = module.audit_directional_face_readiness(
        quadrature=contract(),
        **common,
    )
    assert declared.declared_contract_complete
    assert not declared.physical_face_admitted
    assert not declared.production_integration_authorized
    assert declared.blockers == (
        module.BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION,
    )


def test_untagged_or_wrong_frame_contract_is_rejected() -> None:
    module = admission_module()
    directions, weights, _line = inputs()
    for frame in ("", "NORMAL_ORTHONORMAL_TETRAD_V1"):
        with pytest.raises(ValueError, match=module.BLOCKED_ANGULAR_FRAME_CONTRACT):
            module.AngularQuadratureContract(
                directions=directions,
                weights=weights,
                frame=frame,
                tetrad=module.HYDROGEN_TETRAD,
                frequency_measure=module.ORDINARY_FREQUENCY_HZ,
                source_sha256="a" * 64,
            )


def test_authority_labels_are_noninterchangeable() -> None:
    module = admission_module()
    assert len(
        {
            module.SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
            module.THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
            module.CLOSURE_DEFINED_DIRECTIONAL_SURROGATE_V1,
            module.SOURCE_IDENTICAL_DIRECTIONAL_FACE,
        }
    ) == 4
    assert module.SOURCE_IDENTICAL_DIRECTIONAL_FACE not in {
        module.SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
        module.THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
        module.CLOSURE_DEFINED_DIRECTIONAL_SURROGATE_V1,
    }


def test_coding_research_runner_materializes_spike_without_promoting_face(
    tmp_path: Path,
) -> None:
    output = tmp_path / "coding-research.json"
    environment = os.environ.copy()
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_rec_next01_coding_research.py",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    record = json.loads(output.read_text(encoding="utf-8"))
    assert record["schema"] == "REC_NEXT_01_CODING_RESEARCH_V1"
    assert record["phase_a"]["portable_receipt_contract"] == "PASS"
    assert len(record["phase_a"]["authority_projection_sha256"]) == 64
    assert record["phase_b"]["frame_ambiguity"]["differing_node_count"] == 5
    assert record["phase_b"]["manufactured_geometry"]["ray_count"] == 52
    assert not record["phase_b"]["manufactured_geometry"][
        "physical_face_admitted"
    ]
    assert not record["phase_b"]["production_integration_performed"]
    assert record["claim"] == "NO_PASS_REC_PHYSICAL_SPLIT"
    assert record["blocking_conditions"] == [
        "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT"
    ]

    before = output.read_bytes()
    checked = subprocess.run(
        [
            sys.executable,
            "scripts/run_rec_next01_coding_research.py",
            "--check-record",
            str(output),
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert checked.returncode == 0, checked.stderr
    assert output.read_bytes() == before
    check_record = json.loads(checked.stdout)
    assert check_record["portable_semantics_match"]

    record["phase_b"]["physical_face_materialized"] = True
    output.write_text(
        json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    rejected = subprocess.run(
        [
            sys.executable,
            "scripts/run_rec_next01_coding_research.py",
            "--check-record",
            str(output),
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert rejected.returncode != 0
    assert not json.loads(rejected.stdout)["portable_semantics_match"]

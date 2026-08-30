from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from full_bianchi_hyrec.trajectory import physical_split_reference as reference


ROOT = Path(__file__).resolve().parents[2]
LEGACY_X86_V4_SHA256 = (
    "7bf0ebf143589b45308f5e0157a80ff842dc99783b5207748732f332a6c12912"
)
LEGACY_X86_V3_SHA256 = (
    "1ea93ca2c007209ad25ca6cafcd76d0616a9a4cc88319d56d18f43a03e930e9d"
)
HOST_LANE_UNAVAILABLE = "HOST_LANE_UNAVAILABLE"


def _dispatch_probe(*, disable_x86_v4: bool) -> dict:
    script = r'''
import hashlib
import json
from numpy._core._multiarray_umath import __cpu_features__
from full_bianchi_hyrec.trajectory.physical_split_reference import (
    build_rec_local02_diagnostic,
    build_rec_local02_legacy_diagnostic,
    validate_rec_local02_receipt,
)

legacy = build_rec_local02_legacy_diagnostic(".")
portable = build_rec_local02_diagnostic(".")
validate_rec_local02_receipt(portable)
legacy_bytes = (
    json.dumps(legacy, indent=2, sort_keys=True, allow_nan=False) + "\n"
).encode()
portable_bytes = (
    json.dumps(portable, indent=2, sort_keys=True, allow_nan=False) + "\n"
).encode()
x86_v4 = bool(__cpu_features__.get("X86_V4", False))
x86_v3 = bool(__cpu_features__.get("X86_V3", False))
forensic_lane = "X86_V4" if x86_v4 else ("X86_V3" if x86_v3 else "HOST_LANE_UNAVAILABLE")
print(json.dumps({
    "x86_v4_available": x86_v4,
    "x86_v3_available": x86_v3,
    "forensic_lane": forensic_lane,
    "legacy_sha256": hashlib.sha256(legacy_bytes).hexdigest(),
    "legacy_direct": legacy["doppler_width_reconciliation"]
        ["direct_node_network_measure_max_relative_mismatch"],
    "legacy_centroid": legacy["target_energy_binding"]
        ["legacy_interval_centroid_to_locked_owner_max_abs_difference_eV"],
    "authority_sha256": portable["receipt_contract"]
        ["authority_projection_sha256"],
    "diagnostic_contract_sha256": portable["receipt_contract"]
        ["diagnostic_contract_sha256"],
    "portable_diagnostics": portable["portable_diagnostics"],
    "portable_raw_sha256": hashlib.sha256(portable_bytes).hexdigest(),
    "number_energy_exact": portable["adjacent_energy_moment_feasibility"]
        ["number_and_energy_exact"],
    "status": portable["status"],
    "claim": portable["claim"],
}, sort_keys=True))
'''
    environment = os.environ.copy()
    if disable_x86_v4:
        environment["NPY_DISABLE_CPU_FEATURES"] = "X86_V4"
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def _set_diagnostic(receipt: dict, path: str, value: float) -> None:
    group, name = path.split(".", 1)
    receipt[group][name] = value
    receipt["portable_diagnostics"]["values"][path] = {
        "binary64": value,
        "canonical_decimal": reference.canonicalize_rec_local02_diagnostic(value),
    }


def _assert_available_legacy_fingerprint(probe: dict) -> None:
    lane = probe["forensic_lane"]
    if lane == "X86_V4":
        assert probe["x86_v4_available"] is True
        assert probe["legacy_sha256"] == LEGACY_X86_V4_SHA256
        assert probe["legacy_direct"] == 1.0881876986956445e-08
        assert probe["legacy_centroid"] == 5.545800263462297e-08
    elif lane == "X86_V3":
        assert probe["x86_v4_available"] is False
        assert probe["x86_v3_available"] is True
        assert probe["legacy_sha256"] == LEGACY_X86_V3_SHA256
        assert probe["legacy_direct"] == 1.0878134039731587e-08
        assert probe["legacy_centroid"] == 5.5440194657307984e-08
    else:
        assert lane == HOST_LANE_UNAVAILABLE
        assert probe["x86_v4_available"] is False
        assert probe["x86_v3_available"] is False


def test_portable_contract_is_dispatch_stable_and_preserves_available_legacy_fingerprints() -> None:
    native = _dispatch_probe(disable_x86_v4=False)
    x86_v4_disabled = _dispatch_probe(disable_x86_v4=True)

    assert isinstance(native["x86_v4_available"], bool)
    assert x86_v4_disabled["x86_v4_available"] is False
    _assert_available_legacy_fingerprint(native)
    _assert_available_legacy_fingerprint(x86_v4_disabled)

    assert native["authority_sha256"] == x86_v4_disabled["authority_sha256"]
    assert (
        native["diagnostic_contract_sha256"]
        == x86_v4_disabled["diagnostic_contract_sha256"]
    )
    assert (
        native["portable_diagnostics"]
        == x86_v4_disabled["portable_diagnostics"]
    )
    assert (
        native["number_energy_exact"]
        is x86_v4_disabled["number_energy_exact"]
        is True
    )
    assert native["status"] == x86_v4_disabled["status"] == reference.STATUS
    assert native["claim"] == x86_v4_disabled["claim"] == reference.CLAIM


def test_native_probe_respects_preconfigured_x86_v4_mask(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("NPY_DISABLE_CPU_FEATURES", "X86_V4")
    masked_native = _dispatch_probe(disable_x86_v4=False)

    assert masked_native["x86_v4_available"] is False
    _assert_available_legacy_fingerprint(masked_native)


def test_portable_authority_binds_raw_owner_source_and_invariants() -> None:
    receipt = reference.build_rec_local02_diagnostic(ROOT)
    reference.validate_rec_local02_receipt(receipt)

    owner = receipt["target_energy_binding"]["raw_momentum_scale_owner"]
    assert owner == {
        "source_key": "momentum_scale",
        "dtype": "<f8",
        "shape": [35],
        "endianness": "little",
        "order": "C",
        "sha256": (
            "a32194fb664491fb50ecc1f26096d6b7d03d9be153a459c1db218ce4941de409"
        ),
    }
    assert receipt["target_energy_binding"]["locked_target_energy_sha256"] == (
        "19b9b6bb3d3d0657cb71745118ea396dc3cce92ed15491c20df8a9df8d91f8c8"
    )

    mutants = []
    source = deepcopy(receipt)
    source["tracked_inputs"]["network"]["actual_sha256"] = "0" * 64
    mutants.append(source)
    owner_digest = deepcopy(receipt)
    owner_digest["target_energy_binding"]["raw_momentum_scale_owner"][
        "sha256"
    ] = "1" * 64
    mutants.append(owner_digest)
    witness = deepcopy(receipt)
    witness["adjacent_energy_moment_feasibility"]["witness_sha256"] = "2" * 64
    mutants.append(witness)
    invariant = deepcopy(receipt)
    invariant["adjacent_energy_moment_feasibility"]["physical_map_selected"] = True
    mutants.append(invariant)

    for mutant in mutants:
        with pytest.raises(ValueError, match="authority"):
            reference.validate_rec_local02_receipt(mutant)


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("source_representation", "scalar_history_angular_rank", 26),
        (
            "source_representation",
            "net_source_jump_is_total_interface_crossing_flux",
            True,
        ),
        ("target_energy_binding", "momentum_scale_units", "eV"),
    ],
)
def test_portable_authority_binds_semantic_interface_fields(
    section: str, key: str, value: object
) -> None:
    receipt = reference.build_rec_local02_diagnostic(ROOT)
    receipt[section][key] = value

    with pytest.raises(ValueError, match="authority"):
        reference.validate_rec_local02_receipt(receipt)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("raw_receipt_sha256_role", "PORTABLE_AUTHORITY"),
        ("cross_architecture_bit_identity_claimed", True),
        ("authority_projection_schema", "MUTANT"),
    ],
)
def test_receipt_contract_role_mutants_are_rejected(
    key: str, value: object
) -> None:
    receipt = reference.build_rec_local02_diagnostic(ROOT)
    receipt["receipt_contract"][key] = value

    with pytest.raises(ValueError, match="contract|role|identity|schema"):
        reference.validate_rec_local02_receipt(receipt)


def test_in_range_diagnostic_mutation_does_not_acquire_authority() -> None:
    receipt = reference.build_rec_local02_diagnostic(ROOT)
    authority = reference.rec_local02_authority_sha256(receipt)
    artifact = hashlib.sha256(
        json.dumps(receipt, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    path = (
        "doppler_width_reconciliation."
        "direct_node_network_measure_max_relative_mismatch"
    )

    in_range = deepcopy(receipt)
    _set_diagnostic(in_range, path, 1.09e-8)
    reference.validate_rec_local02_receipt(in_range)
    assert reference.rec_local02_authority_sha256(in_range) == authority
    assert hashlib.sha256(
        json.dumps(in_range, sort_keys=True, allow_nan=False).encode()
    ).hexdigest() != artifact

    out_of_range = deepcopy(receipt)
    _set_diagnostic(out_of_range, path, 2.0e-8)
    with pytest.raises(ValueError, match="diagnostic interval"):
        reference.validate_rec_local02_receipt(out_of_range)


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("diagnostic_contract", "formula_version", "MUTANT"),
        ("diagnostic_contract", "dtype", ">f8"),
        ("diagnostic_contract", "reduction_order", "MUTANT"),
    ],
)
def test_diagnostic_contract_mutants_are_rejected(
    section: str, key: str, value: str
) -> None:
    receipt = reference.build_rec_local02_diagnostic(ROOT)
    receipt[section][key] = value
    with pytest.raises(ValueError, match="diagnostic contract|authority"):
        reference.validate_rec_local02_receipt(receipt)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("dtype", ">f8"),
        ("shape", [5, 7]),
        ("endianness", "big"),
        ("order", "F"),
    ],
)
def test_raw_owner_layout_mutants_are_rejected(key: str, value: object) -> None:
    receipt = reference.build_rec_local02_diagnostic(ROOT)
    receipt["target_energy_binding"]["raw_momentum_scale_owner"][key] = value
    with pytest.raises(ValueError, match="authority"):
        reference.validate_rec_local02_receipt(receipt)


def test_diagnostic_quantum_mutant_is_rejected() -> None:
    receipt = reference.build_rec_local02_diagnostic(ROOT)
    receipt["diagnostic_contract"]["rounding"]["absolute_quantum"] = "1E-12"
    with pytest.raises(ValueError, match="diagnostic contract|authority"):
        reference.validate_rec_local02_receipt(receipt)


def test_center_halfwidth_kernel_matches_versioned_reference_values() -> None:
    receipt = reference.build_rec_local02_diagnostic(ROOT)
    assert receipt["schema"] == "REC_LOCAL_02_SOURCE_BOUND_GATE_V2"
    assert receipt["diagnostic_contract"]["formula_version"] == (
        "CENTER_HALFWIDTH_TRACKED_X_BINARY64_V1"
    )
    assert receipt["doppler_width_reconciliation"][
        "direct_node_network_measure_max_relative_mismatch"
    ] == 1.0868674430328898e-08
    assert receipt["target_energy_binding"][
        "legacy_interval_centroid_to_locked_owner_max_abs_difference_eV"
    ] == 5.539951786204256e-08


def test_runner_checks_portable_semantics_without_requiring_raw_bytes(
    tmp_path: Path,
) -> None:
    receipt = reference.build_rec_local02_diagnostic(ROOT)
    path = tmp_path / "receipt.json"
    path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    command = [
        sys.executable,
        "scripts/run_rec_local02_source_bound_gate.py",
        "--check-portable-receipt",
        str(path),
    ]
    exact = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert exact.returncode == 0, exact.stderr
    exact_summary = json.loads(exact.stdout)
    assert exact_summary["portable_authority_match"]
    assert exact_summary["diagnostic_contract_match"]

    path_key = (
        "doppler_width_reconciliation."
        "direct_node_network_measure_max_relative_mismatch"
    )
    in_range = deepcopy(receipt)
    _set_diagnostic(in_range, path_key, 1.09e-8)
    path.write_text(
        json.dumps(in_range, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    semantic = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert semantic.returncode == 0, semantic.stderr
    semantic_summary = json.loads(semantic.stdout)
    assert semantic_summary["portable_authority_match"]
    assert not semantic_summary["raw_receipt_sha256_match"]

    owner_mutant = deepcopy(receipt)
    owner_mutant["target_energy_binding"]["raw_momentum_scale_owner"][
        "sha256"
    ] = "f" * 64
    path.write_text(
        json.dumps(owner_mutant, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    rejected = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert rejected.returncode != 0
    assert "authority" in rejected.stderr

    semantic_mutant = deepcopy(receipt)
    semantic_mutant["source_representation"]["scalar_history_angular_rank"] = 26
    semantic_mutant["authority_projection"] = (
        reference.rec_local02_authority_projection(semantic_mutant)
    )
    semantic_mutant["receipt_contract"]["authority_projection_sha256"] = (
        reference.rec_local02_authority_sha256(semantic_mutant)
    )
    reference.validate_rec_local02_receipt(semantic_mutant)
    path.write_text(
        json.dumps(semantic_mutant, indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    fresh_rejected = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert fresh_rejected.returncode != 0
    fresh_summary = json.loads(fresh_rejected.stdout)
    assert not fresh_summary["portable_authority_match"]

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NAME = "Full_Bianchi_HyRec_PR05C2C1B2B1D_parent_provenance_background_provider_v0_72"
ARTIFACT = ROOT / "archive" / "expanded" / NAME


def test_v072_artifact_closes_parent_firewall_and_provider_pilot() -> None:
    metrics = json.loads((ARTIFACT / "NUMERICAL_METRICS.json").read_text())
    assert metrics["status"].startswith(
        "PASS_PR05C2C1B2B1D_PARENT_PROVENANCE_FIREWALL"
    )
    firewall = metrics["parent_firewall"]
    provider = metrics["background_provider"]
    assert firewall["operator_verification_rejected"]
    assert firewall["manufactured_rejected"]
    assert firewall["source_derived_schema_witness_accepted"]
    assert firewall["byte_round_trip_exact"]
    assert firewall["stale_history_index_rejected"]
    assert not firewall["physical_source_derived_parent_constructed"]
    assert provider["provider_pilot_passed"]
    assert provider["state_absolute_error_max"] < 1.0e-5
    assert provider["constraint_residual_absmax"] < 1.0e-11
    assert provider["Bianchi_IX_D_event_required"]
    assert provider["exceptional_tilted_VI_minus_1_over_9_fail_closed"]
    assert provider["unvalidated_family_fail_closed"]
    assert not provider["all_11_family_production_support_claimed"]


def test_v072_artifact_csv_npz_plot_and_manifest() -> None:
    firewall = list(csv.DictReader((ARTIFACT / "PARENT_PROVENANCE_FIREWALL.csv").open()))
    provider = list(csv.DictReader((ARTIFACT / "BIANCHI_II_PROVIDER_PILOT.csv").open()))
    assert len(firewall) == 3
    assert len(provider) == 3
    assert {row["production_outcome"] for row in firewall} == {"ACCEPT", "REJECT"}
    assert all(int(row["passed"]) == 1 for row in provider)

    with np.load(ARTIFACT / "pr05c2c1b2b1d_parent_provider_v072.npz") as data:
        assert data["provider_end_normalized_state"].shape == (3,)
        assert data["absolute_error"].max() < 1.0e-5
        assert data["accepted_parent_payload"].dtype == np.uint8

    assert (ARTIFACT / "BIANCHI_II_PROVIDER_PILOT.png").stat().st_size > 20_000
    manifest = {}
    for line in (ARTIFACT / "MANIFEST_SHA256.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        manifest[name] = digest
    for name, digest in manifest.items():
        assert hashlib.sha256((ARTIFACT / name).read_bytes()).hexdigest() == digest


def test_v072_artifact_compact_verifier() -> None:
    result = subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR05C2C1B2B1D.py")],
        cwd=ARTIFACT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert "PASS_PR05C2C1B2B1D_PARENT_PROVENANCE" in result.stdout

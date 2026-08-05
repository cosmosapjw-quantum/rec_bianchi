from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import pytest

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
    ORIGINAL_HYREC_PORTABLE_BINARY_SHA256,
    safe_extract_original_hyrec_archive,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    backward_euler_edge_relaxation,
    central_difference_edge_jvp_residual,
    collision_edge_flux_per_H_s,
    dense_direct_solution,
    dense_original_hyrec_matrix,
    outgoing_distortion,
    parse_original_hyrec_snapshot_csv,
    physical_log_mode_factor_per_H,
    reconstruct_equilibrium_distortion,
    relative_inf,
    same_event_energy_ledger_W_per_H,
    source_escape_factors,
    spectral_source_moments_Hz,
    stable_escape_factors,
    structural_edge_flux_per_H_s,
    structured_schur_solution,
    transport_edge_flux_per_H_s,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = (
    ROOT
    / "archive"
    / "expanded"
    / "Full_Bianchi_HyRec_PR04B2A_physical_native_edge_flux_v0_53"
)
SNAPSHOT = ARTIFACT / "ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv"
ARCHIVE = (
    ROOT
    / "archive"
    / "inputs"
    / "original_hyrec_oct2012"
    / "HyRec_Oct2012.zip"
)
INSTRUMENTER = ROOT / "scripts" / "c_harness" / "instrument_original_hyrec_pr04b2.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def snapshot():
    return parse_original_hyrec_snapshot_csv(SNAPSHOT)


def test_source_identical_snapshot_closes_physical_edge_identity(snapshot):
    mode = physical_log_mode_factor_per_H(snapshot)
    tau_from_source = (
        snapshot.x1s
        * snapshot.Gamma_s_inv
        / (snapshot.H_s_inv * mode)
    )
    assert relative_inf(snapshot.Dtau, tau_from_source) < 2e-15

    transport = transport_edge_flux_per_H_s(snapshot)
    collision = collision_edge_flux_per_H_s(snapshot)
    structural = structural_edge_flux_per_H_s(snapshot, source_branch=True)
    assert relative_inf(collision, transport) < 2e-11
    assert relative_inf(structural, transport) < 2e-11
    assert np.all(np.isfinite(transport))
    assert np.all(transport > 0.0)


def test_stable_escape_and_physical_edge_action(snapshot):
    source_probability, source_one_minus_pi, source_one_minus_exp = (
        source_escape_factors(snapshot.Dtau)
    )
    probability, one_minus_pi, one_minus_exp = stable_escape_factors(
        snapshot.Dtau
    )
    assert relative_inf(probability, source_probability) < 3e-15
    assert relative_inf(one_minus_pi, source_one_minus_pi) < 3e-15
    assert relative_inf(one_minus_exp, source_one_minus_exp) < 3e-15
    assert np.min(probability) > 0.0
    assert np.min(one_minus_pi) > 0.0
    assert np.min(one_minus_exp) > 0.0

    outgoing = outgoing_distortion(
        snapshot.Dfplus,
        snapshot.Dfeq,
        snapshot.Dtau,
        source_branch=False,
    )
    transport = transport_edge_flux_per_H_s(snapshot, outgoing=outgoing)
    structural = structural_edge_flux_per_H_s(snapshot, source_branch=False)
    assert relative_inf(structural, transport) < 2e-14


def test_dense_direct_and_schur_physical_moments(snapshot):
    matrix = dense_original_hyrec_matrix(snapshot)
    rhs = np.concatenate((snapshot.sr, snapshot.sv))
    direct = dense_direct_solution(snapshot)
    schur = structured_schur_solution(snapshot)
    assert np.linalg.norm(matrix @ direct - rhs, ord=np.inf) / np.linalg.norm(
        rhs, ord=np.inf
    ) < 5e-13
    assert relative_inf(direct, snapshot.source_solution) < 5e-13
    assert relative_inf(schur, direct) < 5e-13

    source_flux = transport_edge_flux_per_H_s(snapshot)
    source_moments = spectral_source_moments_Hz(
        source_flux, snapshot.frequency_Hz
    )
    for solution in (direct, schur):
        equilibrium = reconstruct_equilibrium_distortion(snapshot, solution)
        outgoing = outgoing_distortion(
            snapshot.Dfplus,
            equilibrium,
            snapshot.Dtau,
            source_branch=True,
        )
        flux = transport_edge_flux_per_H_s(snapshot, outgoing=outgoing)
        moments = spectral_source_moments_Hz(flux, snapshot.frequency_Hz)
        assert relative_inf(flux, source_flux) < 2e-11
        assert np.max(
            np.abs(moments - source_moments)
            / np.maximum(np.abs(source_moments), 1e-300)
        ) < 5e-11


def test_edge_jvp_implicit_positivity_and_same_event_energy(snapshot):
    rng = np.random.default_rng(20260805)
    incoming_direction = rng.normal(size=snapshot.Dfplus.size) * 1e-15
    equilibrium_direction = rng.normal(size=snapshot.Dfeq.size) * 1e-15
    assert central_difference_edge_jvp_residual(
        snapshot,
        snapshot.Dfplus,
        snapshot.Dfeq,
        incoming_direction,
        equilibrium_direction,
    ) < 1e-7

    _, _, one_minus_exp = stable_escape_factors(snapshot.Dtau)
    equilibrium_occupation = snapshot.blackbody_occupation + snapshot.Dfeq
    phase = np.sin(np.arange(snapshot.Dfplus.size) * 0.371)
    state = np.maximum(equilibrium_occupation * (1.0 + 0.45 * phase), 1e-300)
    rate = snapshot.H_s_inv * one_minus_exp
    decrement = rate * (state - equilibrium_occupation)
    dt_limit = np.min(state[decrement > 0.0] / decrement[decrement > 0.0])
    dt = 1.05 * dt_limit
    explicit = state + dt * rate * (equilibrium_occupation - state)
    implicit = backward_euler_edge_relaxation(
        snapshot, state, equilibrium_occupation, dt
    )
    assert np.min(explicit) < 0.0
    assert np.min(implicit) > 0.0

    photon, atom, total = same_event_energy_ledger_W_per_H(
        transport_edge_flux_per_H_s(snapshot), snapshot.frequency_Hz
    )
    assert np.array_equal(atom, -photon)
    assert np.count_nonzero(total) == 0


def test_pr04b2a_durable_artifact_and_fail_closed_claims():
    ledger = json.loads((ARTIFACT / "PR04B2A_ledger.json").read_text())
    assert ledger["status"] == (
        "PASS_PR04B2A_PHYSICAL_NATIVE_EDGE_FLUX_PR04B2B_OPEN"
    )
    assert all(ledger["hard_gate_status"].values())
    assert ledger["provenance"]["new_classification"] == (
        "OFFICIAL_SITE_CANONICAL_ARCHIVE_OWNER_ATTESTED_BYTE_LOCKED"
    )
    assert ledger["decision"]["native_proxy_as_photon_cell"] == "FORBIDDEN"
    assert ledger["decision"]["direct_COM_KHW_native_parity"] == (
        "OPEN_FAIL_CLOSED"
    )
    assert ledger["metrics"]["native_centres_inside_v051_core"] == 2
    assert ledger["metrics"][
        "v052_forbidden_physical_proxy_map_relative_residual"
    ] > 1e-4
    with np.load(
        ROOT / "data" / "original_hyrec_physical_flux_v053.npz",
        allow_pickle=False,
    ) as evidence:
        assert evidence["transport_edge_flux_sInv_per_H"].shape == (311,)
        assert evidence["source_spectral_moments_Hz"].shape == (5,)
        assert np.min(evidence["implicit_stress_occupation"]) > 0.0
        assert np.min(evidence["explicit_stress_occupation"]) < 0.0


def test_instrumentation_transform_is_deterministic(tmp_path):
    safe_extract_original_hyrec_archive(ARCHIVE, tmp_path)
    source = tmp_path / "HyRec" / "hydrogen.c"
    original = source.read_bytes()
    spec = importlib.util.spec_from_file_location("pr04b2_instrument", INSTRUMENTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    first = module.instrument_hydrogen_source(original.decode("utf-8"))
    assert "PR04B2_DIAGNOSTICS" in first
    with pytest.raises(ValueError):
        module.instrument_hydrogen_source(first)


@pytest.mark.slow
def test_guarded_original_hyrec_build_is_source_identical(tmp_path):
    if shutil.which("gcc") is None:
        pytest.skip("gcc unavailable")
    safe_extract_original_hyrec_archive(ARCHIVE, tmp_path)
    source = tmp_path / "HyRec"

    def compile_binary(name: str, diagnostics: bool) -> Path:
        executable = tmp_path / name
        command = [
            "gcc",
            "-std=c11",
            "-D_DEFAULT_SOURCE",
            "-O3",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
        ]
        if diagnostics:
            command.append("-DPR04B2_DIAGNOSTICS")
        command.extend(
            [
                "hyrectools.c",
                "helium.c",
                "hydrogen.c",
                "history.c",
                "hyrec.c",
                "-lm",
                "-o",
                str(executable),
            ]
        )
        subprocess.run(command, cwd=source, check=True, capture_output=True)
        return executable

    canonical = compile_binary("canonical", diagnostics=False)
    canonical_output = tmp_path / "canonical.out"
    with (source / "input.dat").open("rb") as stdin, canonical_output.open(
        "wb"
    ) as stdout:
        subprocess.run(
            [str(canonical)],
            cwd=source,
            stdin=stdin,
            stdout=stdout,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    assert _sha256(canonical) == ORIGINAL_HYREC_PORTABLE_BINARY_SHA256
    assert _sha256(canonical_output) == ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256

    subprocess.run(
        [sys.executable, str(INSTRUMENTER), str(source / "hydrogen.c")],
        cwd=ROOT,
        check=True,
    )
    guard_off = compile_binary("guard_off", diagnostics=False)
    guard_off_output = tmp_path / "guard_off.out"
    with (source / "input.dat").open("rb") as stdin, guard_off_output.open(
        "wb"
    ) as stdout:
        subprocess.run(
            [str(guard_off)],
            cwd=source,
            stdin=stdin,
            stdout=stdout,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    assert _sha256(guard_off) == _sha256(canonical)
    assert _sha256(guard_off_output) == _sha256(canonical_output)

    guard_on = compile_binary("guard_on", diagnostics=True)
    guard_on_output = tmp_path / "guard_on.out"
    snapshot_path = tmp_path / "snapshot.csv"
    environment = dict(**__import__("os").environ)
    environment["PR04B2_DIAGNOSTIC_PATH"] = str(snapshot_path)
    with (source / "input.dat").open("rb") as stdin, guard_on_output.open(
        "wb"
    ) as stdout:
        subprocess.run(
            [str(guard_on)],
            cwd=source,
            env=environment,
            stdin=stdin,
            stdout=stdout,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    assert _sha256(guard_on_output) == _sha256(canonical_output)
    parsed = parse_original_hyrec_snapshot_csv(snapshot_path)
    assert parsed.target_z == 1100.0
    assert abs(parsed.z - 1100.0) < 0.05

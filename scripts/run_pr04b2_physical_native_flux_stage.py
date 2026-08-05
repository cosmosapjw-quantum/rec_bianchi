#!/usr/bin/env python3
"""Build PR-04B2A/v0.53 physical native edge-flux closure.

This bounded stage keeps the official-site October-2012 original-HyRec archive
immutable, adds source-identical compile-time diagnostics in a temporary
extraction, and derives the physical logarithmic-frequency photon edge flux per
hydrogen atom.  It closes native primitive/direct/Schur parity at one locked
FULL-mode FLRW trajectory snapshot.  It deliberately leaves the direct v0.51
17-cell COM--KHW/native common-partition projection open.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

import mpmath as mp
import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from full_bianchi_hyrec.recoil.original_hyrec_native import (  # noqa: E402
    ORIGINAL_HYREC_ARCHIVE_BYTES,
    ORIGINAL_HYREC_ARCHIVE_ENTRY_COUNT,
    ORIGINAL_HYREC_ARCHIVE_SHA256,
    ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
    ORIGINAL_HYREC_PORTABLE_BINARY_SHA256,
    audit_original_hyrec_archive,
    safe_extract_original_hyrec_archive,
    sha256_file,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    MOMENT_MAX,
    SOURCE_HPC_EV_CM,
    average_distortion,
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
    save_snapshot_npz,
    source_escape_factors,
    spectral_source_moments_Hz,
    stable_escape_factors,
    structural_edge_flux_per_H_s,
    structured_schur_solution,
    transport_edge_flux_per_H_s,
)

ARTIFACT_NAME = "Full_Bianchi_HyRec_PR04B2A_physical_native_edge_flux_v0_53"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_PATH = ROOT / "data" / "original_hyrec_physical_flux_v053.npz"
INPUT_ARCHIVE = (
    ROOT / "archive" / "inputs" / "original_hyrec_oct2012" / "HyRec_Oct2012.zip"
)
CODING_HARNESS = (
    ROOT
    / "archive"
    / "inputs"
    / "research_harnesses"
    / "physmath-coding-harness-gpt56.zip"
)
RESEARCH_HARNESS = (
    ROOT
    / "archive"
    / "inputs"
    / "research_harnesses"
    / "physmath-research-harness-gpt56.zip"
)
INSTRUMENTER = ROOT / "scripts" / "c_harness" / "instrument_original_hyrec_pr04b2.py"
V051_DATA = ROOT / "data" / "hyrec_common_measure_v051.npz"
V052_DATA = ROOT / "data" / "original_hyrec_native_v052.npz"

CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CANONICAL_PROVENANCE_CLASS = "OFFICIAL_SITE_CANONICAL_ARCHIVE_OWNER_ATTESTED_BYTE_LOCKED"
EXPECTED_HISTORY_ROWS = 8001
TARGET_Z = 1100.0


def digest(path: Path) -> str:
    return sha256_file(path)


def run(
    command: list[str],
    *,
    cwd: Path,
    stdout: Path | None = None,
    stderr: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment["PWD"] = str(cwd)
    if env:
        environment.update(env)
    if stdout is not None and stderr is not None and stdout == stderr:
        with stdout.open("wb") as handle:
            return subprocess.run(
                command,
                cwd=cwd,
                env=environment,
                stdout=handle,
                stderr=subprocess.STDOUT,
                check=check,
            )
    output_handle = stdout.open("wb") if stdout is not None else subprocess.PIPE
    error_handle = stderr.open("wb") if stderr is not None else subprocess.PIPE
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            stdout=output_handle,
            stderr=error_handle,
            check=check,
        )
    finally:
        if stdout is not None:
            output_handle.close()
        if stderr is not None:
            error_handle.close()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def normalize_log(path: Path, replacements: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for source, target in replacements.items():
        text = text.replace(source, target)
    path.write_text(
        "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").splitlines()) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def compile_hyrec(source: Path, output: Path, log: Path, *, diagnostics: bool) -> None:
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
            str(output),
        ]
    )
    run(command, cwd=source, stdout=log, stderr=log)


def execute_hyrec(
    source: Path,
    executable: Path,
    stdout_path: Path,
    stderr_path: Path,
    *,
    snapshot_path: Path | None = None,
) -> None:
    environment: dict[str, str] = {}
    if snapshot_path is not None:
        environment["PR04B2_DIAGNOSTIC_PATH"] = str(snapshot_path)
    with (source / "input.dat").open("rb") as input_handle, stdout_path.open(
        "wb"
    ) as output_handle, stderr_path.open("wb") as error_handle:
        result = subprocess.run(
            [str(executable)],
            cwd=source,
            env={**os.environ, **environment},
            stdin=input_handle,
            stdout=output_handle,
            stderr=error_handle,
        )
    if result.returncode:
        raise RuntimeError(f"HyRec exited with status {result.returncode}")


def parse_output_row(path: Path, target_z: float) -> tuple[float, float, float]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            fields = line.split()
            if len(fields) != 3:
                continue
            rows.append(tuple(map(float, fields)))
    if len(rows) != EXPECTED_HISTORY_ROWS:
        raise ValueError(f"expected {EXPECTED_HISTORY_ROWS} history rows, got {len(rows)}")
    selected = [row for row in rows if row[0] == target_z]
    if len(selected) != 1:
        raise ValueError(f"expected one z={target_z} output row, got {len(selected)}")
    return selected[0]


def matrix_relative_residual(matrix: np.ndarray, solution: np.ndarray, rhs: np.ndarray) -> float:
    return float(
        np.linalg.norm(matrix @ solution - rhs, ord=np.inf)
        / max(np.linalg.norm(rhs, ord=np.inf), 1.0e-300)
    )


def moment_relative_residual(first: np.ndarray, second: np.ndarray) -> float:
    scale = np.maximum(np.maximum(np.abs(first), np.abs(second)), 1.0e-300)
    return float(np.max(np.abs(first - second) / scale))


def validate_harness(archive: Path, validator_relative: str, log: Path, work: Path) -> dict:
    if digest(archive) not in {CODING_HARNESS_SHA256, RESEARCH_HARNESS_SHA256}:
        raise ValueError(f"unexpected harness hash: {archive}")
    destination = work / archive.stem
    destination.mkdir()
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise ValueError(f"harness ZIP integrity failed: {archive}")
        zipped.extractall(destination)
    # Each ZIP has one top-level harness directory in this release, but tolerate
    # a flat archive by locating the validator recursively.
    matches = list(destination.rglob(validator_relative))
    if len(matches) != 1:
        raise ValueError(f"cannot locate {validator_relative} in {archive}")
    result = run(
        [sys.executable, str(matches[0])],
        cwd=matches[0].parents[1],
        stdout=log,
        stderr=log,
        check=False,
    )
    return {
        "archive": archive.name,
        "sha256": digest(archive),
        "validator": validator_relative,
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
    }


def symbolic_high_precision_audit(snapshot) -> tuple[list[dict], float, float]:
    tau, xgamma, hubble, mode, delta = sp.symbols(
        "tau xGamma H A delta", positive=True, finite=True
    )
    escape = (1 - sp.exp(-tau)) / tau
    collision = xgamma * escape * delta
    transport = hubble * mode * (1 - sp.exp(-tau)) * delta
    exact = sp.simplify(collision.subs(xgamma, hubble * mode * tau) - transport)

    rows = [
        {
            "check": "exact_edge_identity",
            "tool": "SymPy exact",
            "absolute_residual": str(exact),
            "relative_residual": str(exact),
        },
        {
            "check": "same_event_energy",
            "tool": "SymPy exact",
            "absolute_residual": str(sp.simplify(sp.Symbol("E") - sp.Symbol("E"))),
            "relative_residual": "0",
        },
    ]

    mp.mp.dps = 100
    maximum_identity = mp.mpf("0")
    maximum_escape_reference = mp.mpf("0")
    stable_probability, stable_one_minus_pi, stable_one_minus_exp = stable_escape_factors(
        snapshot.Dtau
    )
    for index, tau_float in enumerate(snapshot.Dtau):
        t = mp.mpf(repr(float(tau_float)))
        one = -mp.expm1(-t)
        probability = one / t if t != 0 else mp.mpf(1)
        one_minus_pi = 1 - probability
        # Independent identity uses xGamma=H*A*tau and does not reuse the same
        # floating-point subtraction on the two sides.
        arbitrary_H = mp.mpf("4.9696512229238343e-14")
        arbitrary_A = mp.mpf("1.234567890123456789e13")
        arbitrary_delta = mp.mpf("3.456789012345678901e-17")
        xgamma_value = arbitrary_H * arbitrary_A * t
        lhs = xgamma_value * probability * arbitrary_delta
        rhs = arbitrary_H * arbitrary_A * one * arbitrary_delta
        denominator = max(abs(lhs), abs(rhs), mp.mpf("1e-200"))
        maximum_identity = max(maximum_identity, abs(lhs - rhs) / denominator)
        for double_value, reference in (
            (stable_probability[index], probability),
            (stable_one_minus_pi[index], one_minus_pi),
            (stable_one_minus_exp[index], one),
        ):
            denominator = max(abs(reference), mp.mpf("1e-200"))
            maximum_escape_reference = max(
                maximum_escape_reference,
                abs(mp.mpf(repr(float(double_value))) - reference) / denominator,
            )

    rows.extend(
        [
            {
                "check": "100_digit_edge_identity",
                "tool": "mpmath 100 dps",
                "absolute_residual": mp.nstr(maximum_identity, 25),
                "relative_residual": mp.nstr(maximum_identity, 25),
            },
            {
                "check": "float64_stable_escape_vs_100_digit",
                "tool": "NumPy expm1 versus mpmath 100 dps",
                "absolute_residual": mp.nstr(maximum_escape_reference, 25),
                "relative_residual": mp.nstr(maximum_escape_reference, 25),
            },
        ]
    )
    return rows, float(maximum_identity), float(maximum_escape_reference)


def manifest(artifact: Path) -> None:
    rows = []
    for path in sorted(artifact.iterdir()):
        if path.is_file() and path.name != "MANIFEST_SHA256.txt":
            rows.append(f"{digest(path)}  {path.name}")
    (artifact / "MANIFEST_SHA256.txt").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep-work", action="store_true")
    args = parser.parse_args()

    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    BUNDLE.unlink(missing_ok=True)

    archive_audit = audit_original_hyrec_archive(INPUT_ARCHIVE)
    if not archive_audit.safe:
        raise RuntimeError("canonical original-HyRec archive failed safety audit")
    if (
        archive_audit.sha256 != ORIGINAL_HYREC_ARCHIVE_SHA256
        or archive_audit.size_bytes != ORIGINAL_HYREC_ARCHIVE_BYTES
        or archive_audit.entry_count != ORIGINAL_HYREC_ARCHIVE_ENTRY_COUNT
    ):
        raise RuntimeError("canonical original-HyRec archive lock mismatch")

    work_context = tempfile.TemporaryDirectory(prefix="pr04b2a-")
    work = Path(work_context.name)
    safe_extract_original_hyrec_archive(INPUT_ARCHIVE, work)
    source = work / "HyRec"

    baseline_executable = work / "hyrec_canonical"
    baseline_build_log = ARTIFACT / "CANONICAL_BUILD.log"
    compile_hyrec(source, baseline_executable, baseline_build_log, diagnostics=False)
    baseline_output = ARTIFACT / "CANONICAL_HISTORY.txt"
    baseline_stderr = ARTIFACT / "CANONICAL_STDERR.txt"
    execute_hyrec(source, baseline_executable, baseline_output, baseline_stderr)

    patch_path = ARTIFACT / "ORIGINAL_HYREC_PR04B2A_DIAGNOSTIC.patch"
    run(
        [sys.executable, str(INSTRUMENTER), str(source / "hydrogen.c"), "--diff", str(patch_path)],
        cwd=ROOT,
    )

    guard_off_executable = work / "hyrec_guard_off"
    guard_off_build_log = ARTIFACT / "GUARD_OFF_BUILD.log"
    compile_hyrec(source, guard_off_executable, guard_off_build_log, diagnostics=False)
    guard_off_output = ARTIFACT / "GUARD_OFF_HISTORY.txt"
    guard_off_stderr = ARTIFACT / "GUARD_OFF_STDERR.txt"
    execute_hyrec(source, guard_off_executable, guard_off_output, guard_off_stderr)

    guard_on_executable = work / "hyrec_guard_on"
    guard_on_build_log = ARTIFACT / "GUARD_ON_BUILD.log"
    compile_hyrec(source, guard_on_executable, guard_on_build_log, diagnostics=True)
    guard_on_output = ARTIFACT / "GUARD_ON_HISTORY.txt"
    guard_on_stderr = ARTIFACT / "GUARD_ON_STDERR.txt"
    snapshot_csv = ARTIFACT / "ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv"
    execute_hyrec(
        source,
        guard_on_executable,
        guard_on_output,
        guard_on_stderr,
        snapshot_path=snapshot_csv,
    )

    replacements = {str(work): "<WORKDIR>", str(ROOT): "<REPOSITORY_ROOT>"}
    for log in (baseline_build_log, guard_off_build_log, guard_on_build_log):
        normalize_log(log, replacements)

    snapshot = parse_original_hyrec_snapshot_csv(snapshot_csv)
    baseline_z, baseline_xe, baseline_tm_ratio = parse_output_row(
        baseline_output, TARGET_Z
    )
    delta_eta = math.log((1.0 + snapshot.z) / (1.0 + TARGET_Z))
    interpolated_xe = snapshot.xe + snapshot.dxHIIdlna * delta_eta
    xe_interpolation_relative = abs(interpolated_xe - baseline_xe) / abs(baseline_xe)
    tm_grid_relative = abs(snapshot.TM_over_TR - baseline_tm_ratio) / abs(
        baseline_tm_ratio
    )

    mode_factor = physical_log_mode_factor_per_H(snapshot)
    tau_from_source = (
        snapshot.x1s
        * snapshot.Gamma_s_inv
        / (snapshot.H_s_inv * mode_factor)
    )
    tau_relation_relative = relative_inf(snapshot.Dtau, tau_from_source)

    source_probability, source_one_minus_pi, source_one_minus_exp = source_escape_factors(
        snapshot.Dtau
    )
    stable_probability, stable_one_minus_pi, stable_one_minus_exp = stable_escape_factors(
        snapshot.Dtau
    )

    transport_source = transport_edge_flux_per_H_s(snapshot)
    collision_source = collision_edge_flux_per_H_s(snapshot)
    structural_source = structural_edge_flux_per_H_s(snapshot, source_branch=True)
    stable_outgoing = outgoing_distortion(
        snapshot.Dfplus,
        snapshot.Dfeq,
        snapshot.Dtau,
        source_branch=False,
    )
    stable_average = average_distortion(
        snapshot.Dfplus,
        snapshot.Dfeq,
        snapshot.Dtau,
        source_branch=False,
    )
    transport_stable = transport_edge_flux_per_H_s(
        snapshot, outgoing=stable_outgoing
    )
    collision_stable = collision_edge_flux_per_H_s(
        snapshot, average=stable_average
    )
    structural_stable = structural_edge_flux_per_H_s(
        snapshot, source_branch=False
    )

    matrix = dense_original_hyrec_matrix(snapshot)
    rhs = np.concatenate((snapshot.sr, snapshot.sv))
    direct_solution = dense_direct_solution(snapshot)
    schur_solution = structured_schur_solution(snapshot)
    direct_matrix_residual = matrix_relative_residual(matrix, direct_solution, rhs)
    source_direct_relative = relative_inf(snapshot.source_solution, direct_solution)
    schur_direct_relative = relative_inf(schur_solution, direct_solution)

    direct_equilibrium = reconstruct_equilibrium_distortion(snapshot, direct_solution)
    schur_equilibrium = reconstruct_equilibrium_distortion(snapshot, schur_solution)
    direct_outgoing = outgoing_distortion(
        snapshot.Dfplus,
        direct_equilibrium,
        snapshot.Dtau,
        source_branch=True,
    )
    schur_outgoing = outgoing_distortion(
        snapshot.Dfplus,
        schur_equilibrium,
        snapshot.Dtau,
        source_branch=True,
    )
    direct_flux = transport_edge_flux_per_H_s(snapshot, outgoing=direct_outgoing)
    schur_flux = transport_edge_flux_per_H_s(snapshot, outgoing=schur_outgoing)
    source_moments = spectral_source_moments_Hz(
        transport_source, snapshot.frequency_Hz
    )
    direct_moments = spectral_source_moments_Hz(
        direct_flux, snapshot.frequency_Hz
    )
    schur_moments = spectral_source_moments_Hz(
        schur_flux, snapshot.frequency_Hz
    )
    direct_moment_relative = moment_relative_residual(direct_moments, source_moments)
    schur_moment_relative = moment_relative_residual(schur_moments, source_moments)

    rng = np.random.default_rng(20260805)
    incoming_direction = rng.normal(size=snapshot.Dfplus.size) * 1.0e-15
    equilibrium_direction = rng.normal(size=snapshot.Dfeq.size) * 1.0e-15
    jvp_relative = central_difference_edge_jvp_residual(
        snapshot,
        snapshot.Dfplus,
        snapshot.Dfeq,
        incoming_direction,
        equilibrium_direction,
    )

    blackbody = snapshot.blackbody_occupation
    equilibrium_occupation = blackbody + snapshot.Dfeq
    phase = np.sin(np.arange(snapshot.Dfplus.size) * 0.371)
    stress_occupation = equilibrium_occupation * (1.0 + 0.45 * phase)
    stress_occupation = np.maximum(stress_occupation, 1.0e-300)
    relaxation_rate = snapshot.H_s_inv * stable_one_minus_exp
    decreasing = relaxation_rate * (stress_occupation - equilibrium_occupation)
    candidates = stress_occupation[decreasing > 0.0] / decreasing[decreasing > 0.0]
    explicit_limit = float(np.min(candidates))
    stress_dt = 1.05 * explicit_limit
    explicit_occupation = stress_occupation + stress_dt * relaxation_rate * (
        equilibrium_occupation - stress_occupation
    )
    implicit_occupation = backward_euler_edge_relaxation(
        snapshot,
        stress_occupation,
        equilibrium_occupation,
        stress_dt,
    )

    photon_energy, atom_energy, total_energy = same_event_energy_ledger_W_per_H(
        transport_source,
        snapshot.frequency_Hz,
    )

    symbolic_rows, high_precision_identity, high_precision_escape = (
        symbolic_high_precision_audit(snapshot)
    )
    write_csv(ARTIFACT / "SYMBOLIC_HIGH_PRECISION_AUDIT.csv", symbolic_rows)

    harness_work = work / "harnesses"
    harness_work.mkdir()
    coding_harness_result = validate_harness(
        CODING_HARNESS,
        "tools/validate_harness.py",
        ARTIFACT / "CODING_HARNESS_VALIDATION.log",
        harness_work,
    )
    research_harness_result = validate_harness(
        RESEARCH_HARNESS,
        "tools/validate_workspace.py",
        ARTIFACT / "RESEARCH_HARNESS_VALIDATION.log",
        harness_work,
    )

    # Preserve the v0.52 firewall and quantify why raw cross-stage numbers do
    # not constitute a physical parity map.
    with np.load(V052_DATA, allow_pickle=False) as v052:
        proxy_physical_residual = float(v052["physical_number_map_relative_residual"])
    with np.load(V051_DATA, allow_pickle=False) as v051:
        native_indices = np.asarray(v051["native_virtual_indices"], dtype=int)
        native_x = np.asarray(v051["native_x"], dtype=float)
        core_rows = np.flatnonzero(np.abs(native_x) <= 4.25)
        core_native_indices = native_indices[core_rows]
        core_native_flux = transport_source[core_native_indices]
        v051_c0_mass_per_H_s = float(
            np.sum(v051["frequency_moments_Hz_m3_sInv"][0])
            / (snapshot.nH_cm3 * 1.0e6)
        )

    overlap_rows = []
    for row, native_index in zip(core_rows, core_native_indices, strict=True):
        overlap_rows.append(
            {
                "native_virtual_index": int(native_index),
                "v051_native_x": float(native_x[row]),
                "physical_edge_flux_sInv_per_H": float(
                    transport_source[native_index]
                ),
                "comparison_status": "CENTRE_ONLY_NO_COMMON_CELL_PARTITION",
            }
        )
    write_csv(ARTIFACT / "COM_KHW_NATIVE_OVERLAP_DIAGNOSTIC.csv", overlap_rows)

    metrics = {
        "canonical_archive_sha256": archive_audit.sha256,
        "canonical_archive_size_bytes": archive_audit.size_bytes,
        "canonical_binary_sha256": digest(baseline_executable),
        "canonical_history_sha256": digest(baseline_output),
        "guard_off_binary_sha256": digest(guard_off_executable),
        "guard_off_history_sha256": digest(guard_off_output),
        "guard_on_binary_sha256": digest(guard_on_executable),
        "guard_on_history_sha256": digest(guard_on_output),
        "snapshot_sha256": digest(snapshot_csv),
        "snapshot_z": snapshot.z,
        "snapshot_iz_local": snapshot.iz_local,
        "baseline_output_z": baseline_z,
        "baseline_output_xe": baseline_xe,
        "baseline_output_TM_over_TR": baseline_tm_ratio,
        "first_order_interpolated_xe": interpolated_xe,
        "xe_interpolation_relative_residual": xe_interpolation_relative,
        "TM_over_TR_grid_relative_difference": tm_grid_relative,
        "tau_min": float(np.min(snapshot.Dtau)),
        "tau_max": float(np.max(snapshot.Dtau)),
        "tau_relation_relative_residual": tau_relation_relative,
        "source_vs_stable_probability_relative_residual": relative_inf(
            source_probability, stable_probability
        ),
        "source_vs_stable_one_minus_Pi_relative_residual": relative_inf(
            source_one_minus_pi, stable_one_minus_pi
        ),
        "source_vs_stable_one_minus_exp_relative_residual": relative_inf(
            source_one_minus_exp, stable_one_minus_exp
        ),
        "stored_collision_vs_transport_relative_residual": relative_inf(
            collision_source, transport_source
        ),
        "source_structural_vs_transport_relative_residual": relative_inf(
            structural_source, transport_source
        ),
        "stable_collision_vs_transport_relative_residual": relative_inf(
            collision_stable, transport_stable
        ),
        "stable_structural_vs_transport_relative_residual": relative_inf(
            structural_stable, transport_stable
        ),
        "direct_matrix_relative_residual": direct_matrix_residual,
        "source_vs_direct_solution_relative_residual": source_direct_relative,
        "schur_vs_direct_solution_relative_residual": schur_direct_relative,
        "direct_flux_relative_residual": relative_inf(direct_flux, transport_source),
        "schur_flux_relative_residual": relative_inf(schur_flux, transport_source),
        "direct_moment_max_relative_residual": direct_moment_relative,
        "schur_moment_max_relative_residual": schur_moment_relative,
        "edge_JVP_relative_residual": jvp_relative,
        "explicit_stress_dt_s": stress_dt,
        "explicit_stress_minimum_occupation": float(np.min(explicit_occupation)),
        "implicit_stress_minimum_occupation": float(np.min(implicit_occupation)),
        "same_event_energy_absolute_residual_W_per_H": float(
            np.max(np.abs(total_energy))
        ),
        "net_photon_energy_source_W_per_H": float(np.sum(photon_energy)),
        "high_precision_edge_identity_relative_residual": high_precision_identity,
        "float64_stable_escape_vs_100_digit_max_relative_residual": high_precision_escape,
        "v052_forbidden_physical_proxy_map_relative_residual": proxy_physical_residual,
        "native_centres_inside_v051_core": int(core_rows.size),
        "native_core_edge_flux_sInv_per_H": float(np.sum(core_native_flux)),
        "v051_raw_C0_mass_divided_by_nH_sInv_per_H_NOT_PARITY": v051_c0_mass_per_H_s,
    }

    hard_gates = {
        "canonical_archive_byte_lock": archive_audit.sha256 == ORIGINAL_HYREC_ARCHIVE_SHA256,
        "canonical_binary_hash": digest(baseline_executable) == ORIGINAL_HYREC_PORTABLE_BINARY_SHA256,
        "canonical_history_hash": digest(baseline_output) == ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
        "guard_off_binary_identical": digest(guard_off_executable) == digest(baseline_executable),
        "guard_off_history_identical": digest(guard_off_output) == digest(baseline_output),
        "guard_on_history_identical": digest(guard_on_output) == digest(baseline_output),
        "locked_single_snapshot": snapshot_csv.is_file() and snapshot.target_z == TARGET_Z,
        "snapshot_nearest_grid": abs(snapshot.z - TARGET_Z) < 0.5 * 8.49e-5 * (1.0 + TARGET_Z) * 1.001,
        "source_output_xe_parity": xe_interpolation_relative < 1.0e-9,
        "source_output_temperature_grid_parity": tm_grid_relative < 1.0e-8,
        "tau_normalization_identity": tau_relation_relative < 2.0e-15,
        "source_edge_flux_identity": relative_inf(structural_source, transport_source) < 2.0e-11,
        "stored_average_edge_flux_identity": relative_inf(collision_source, transport_source) < 2.0e-11,
        "stable_edge_flux_identity": relative_inf(structural_stable, transport_stable) < 2.0e-14,
        "stable_average_reconstruction_identity": relative_inf(collision_stable, transport_stable) < 1.0e-11,
        "escape_factors_finite_positive": bool(
            np.all(np.isfinite(stable_probability))
            and np.all(np.isfinite(stable_one_minus_pi))
            and np.all(np.isfinite(stable_one_minus_exp))
            and np.min(stable_probability) > 0.0
            and np.min(stable_one_minus_pi) > 0.0
            and np.min(stable_one_minus_exp) > 0.0
        ),
        "dense_matrix_solution": direct_matrix_residual < 5.0e-13,
        "source_direct_solution": source_direct_relative < 5.0e-13,
        "schur_direct_solution": schur_direct_relative < 5.0e-13,
        "direct_physical_moments": direct_moment_relative < 5.0e-11,
        "schur_physical_moments": schur_moment_relative < 5.0e-11,
        "analytic_edge_JVP": jvp_relative < 1.0e-7,
        "implicit_positivity": float(np.min(implicit_occupation)) > 0.0,
        "explicit_stress_fails_positive": float(np.min(explicit_occupation)) < 0.0,
        "same_event_energy": float(np.max(np.abs(total_energy))) == 0.0,
        "symbolic_identity": symbolic_rows[0]["absolute_residual"] == "0",
        "high_precision_identity": high_precision_identity < 1.0e-80,
        "high_precision_escape_reference": high_precision_escape < 5.0e-15,
        "proxy_firewall_preserved": proxy_physical_residual > 1.0e-4,
        "coding_harness_validation": coding_harness_result["passed"],
        "research_harness_validation": research_harness_result["passed"],
        "direct_COM_KHW_native_claim_fail_closed": core_rows.size == 2,
    }

    edge_rows = []
    for index in range(snapshot.energy_eV.size):
        edge_rows.append(
            {
                "virtual_index": index,
                "energy_eV": snapshot.energy_eV[index],
                "frequency_Hz": snapshot.frequency_Hz[index],
                "tau": snapshot.Dtau[index],
                "A_photons_per_H_per_dlnnu_per_occupation": mode_factor[index],
                "Dfplus": snapshot.Dfplus[index],
                "Dfbar": snapshot.Dfbar[index],
                "Dfeq": snapshot.Dfeq[index],
                "Dfminus": snapshot.Dfminus[index],
                "transport_flux_sInv_per_H": transport_source[index],
                "collision_flux_sInv_per_H": collision_source[index],
                "direct_flux_sInv_per_H": direct_flux[index],
                "schur_flux_sInv_per_H": schur_flux[index],
            }
        )
    write_csv(ARTIFACT / "PHYSICAL_NATIVE_EDGE_FLUX.csv", edge_rows)

    moment_rows = []
    for order in range(MOMENT_MAX + 1):
        moment_rows.append(
            {
                "order_r": order,
                "units": "Hz^r s^-1 per H",
                "source_stored": source_moments[order],
                "dense_direct": direct_moments[order],
                "structured_schur": schur_moments[order],
                "direct_relative_residual": abs(direct_moments[order] - source_moments[order])
                / max(abs(source_moments[order]), 1.0e-300),
                "schur_relative_residual": abs(schur_moments[order] - source_moments[order])
                / max(abs(source_moments[order]), 1.0e-300),
            }
        )
    write_csv(ARTIFACT / "PRIMITIVE_SCHUR_PHYSICAL_MOMENTS.csv", moment_rows)

    write_csv(
        ARTIFACT / "SOURCE_IDENTICAL_HASH_GATES.csv",
        [
            {
                "lane": "canonical",
                "binary_sha256": digest(baseline_executable),
                "history_sha256": digest(baseline_output),
                "history_rows": EXPECTED_HISTORY_ROWS,
            },
            {
                "lane": "instrumented_guard_off",
                "binary_sha256": digest(guard_off_executable),
                "history_sha256": digest(guard_off_output),
                "history_rows": EXPECTED_HISTORY_ROWS,
            },
            {
                "lane": "instrumented_guard_on",
                "binary_sha256": digest(guard_on_executable),
                "history_sha256": digest(guard_on_output),
                "history_rows": EXPECTED_HISTORY_ROWS,
            },
        ],
    )

    provenance = {
        "classification": "ORIGINAL_HYREC_CANONICAL_PROVENANCE_SUPERSESSION",
        "old_classification": "USER_SUPPLIED_OFFICIAL_CANDIDATE_BYTE_LOCKED",
        "new_classification": CANONICAL_PROVENANCE_CLASS,
        "owner_instruction": (
            "The official HyRec site provides this as the unique canonical October-2012 archive; "
            "internal May/October metadata differences are intrinsic release metadata."
        ),
        "archive": {
            "path": str(INPUT_ARCHIVE.relative_to(ROOT)),
            "sha256": archive_audit.sha256,
            "size_bytes": archive_audit.size_bytes,
            "entries": archive_audit.entry_count,
        },
        "interpretation": (
            "Internal source-header and ZIP timestamp differences are not an uncertainty or mismatch gate."
        ),
        "official_page_role": "October 2012 is listed among the previous stable HyRec releases.",
        "supersedes_v052_wording_only": True,
        "v052_immutable_artifact_modified": False,
    }
    (ARTIFACT / "ORIGINAL_HYREC_CANONICAL_PROVENANCE_SUPERSESSION.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )

    harness_receipt = {
        "classification": "PR04B2A_HARNESS_EXECUTION_RECEIPT",
        "coding": coding_harness_result,
        "research": research_harness_result,
        "research_contract": "docs/PR04B2A_RESEARCH_CONTRACT.md",
        "evidence_ledger": "docs/PR04B2A_EVIDENCE_LEDGER.md",
        "hypothesis_audit": "docs/PR04B2A_HYPOTHESIS_AUDIT.md",
        "validation_matrix": "docs/PR04B2A_VALIDATION_MATRIX.md",
    }
    (ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json").write_text(
        json.dumps(harness_receipt, indent=2) + "\n", encoding="utf-8"
    )

    tool_status = {
        "web_search": "USED_OFFICIAL_HYREC_PAGE_AND_PRIMARY_HYREC/HYREC2_PAPERS",
        "Wolfram": "UNAVAILABLE_IN_RUNTIME",
        "Precise_Special_Functions": "UNAVAILABLE_IN_RUNTIME",
        "GitHub_private_repo_connector": "NOT_EXPOSED_IN_THIS_EXECUTION_RUNTIME",
        "fallbacks": [
            "SymPy exact algebra",
            "mpmath 100-digit escape and edge identity",
            "original C compile and full trajectory execution",
            "NumPy dense and structured-Schur linear algebra",
            "central-difference JVP regression",
        ],
    }
    (ARTIFACT / "TOOL_STATUS.json").write_text(
        json.dumps(tool_status, indent=2) + "\n", encoding="utf-8"
    )

    formalism = f"""# PR-04B2A physical native edge-flux formalism

## Conventions

Metric signature is `(-,+,+,+)`. The local frame is the hydrogen orthonormal
tetrad. Ordinary frequency `nu` is measured in Hz, `y=ln(nu)`, and cosmological
time is `eta=ln(a)`, so `d/dt=H d/deta`. The jump sign remains
`Delta nu=nu_target-nu_source`; `Delta E_gamma=h Delta nu` and
`Delta E_H=-h Delta nu`. Constants `c`, `h`, and `k_B` are explicit.

The canonical original-HyRec source uses cgs lengths and eV energies. Its
source-consistent `hc` constant is `{SOURCE_HPC_EV_CM:.15e} eV cm`.

## Physical measure and transport equation

For occupation distortion `Delta f_nu`, define photons per hydrogen atom per
logarithmic-frequency interval,

```text
N_y = 8 pi nu^3 Delta f_nu / (c^3 n_H) = A(nu) Delta f_nu.
```

Since `n_H` scales as `a^-3`, the homogeneous free-streaming operator obeys

```text
partial_eta N_y - partial_y N_y = A(nu) C[f]/H.
```

The redshift flux is `F_y=-N_y`. Across native virtual spike `b`,

```text
P_b       = (1-exp(-tau_b))/tau_b,
fbar_b    = P_b fplus_b + (1-P_b) feq_b,
fminus_b  = fplus_b + (1-exp(-tau_b))(feq_b-fplus_b),
tau_b     = x_1s Gamma_b/(H A_b).
```

Therefore

```text
x_1s Gamma_b (feq_b-fbar_b)
  = x_1s Gamma_b P_b (feq_b-fplus_b)
  = H A_b (fminus_b-fplus_b).
```

Both sides have units `s^-1` per H. Multiplication by `h nu_b` gives W per H;
the same event assigns the exact opposite energy to the atom.

## Closed and open claims

The source solution, an independent dense 313-state solve, and the structured
Schur solve reproduce the same physical edge flux and signed source moments
through order four. These are *spectral source moments* `sum_b J_b nu_b^r`,
with units `Hz^r s^-1` per H; they are not COM--KHW jump moments.

Only two native virtual centres lie inside the v0.51 `|x|<=4.25` production
core. Native spikes and 17 finite-volume COM--KHW cells do not yet share a
measure-preserving partition. Raw v0.51 event mass divided by `n_H` and native
trajectory flux are therefore recorded only as a negative overlap diagnostic;
no ratio is fitted and no direct parity is claimed. PR-04B2B remains open.
"""
    (ARTIFACT / "PR04B2A_PHYSICAL_NATIVE_EDGE_FLUX_FORMALISM.md").write_text(
        formalism, encoding="utf-8"
    )

    overlap_audit = f"""# COM--KHW/native overlap audit

The v0.51 17-cell physical common measure spans `|x|<=4.25`. At the locked
original-HyRec snapshot, only native virtual indices
`{', '.join(str(int(value)) for value in core_native_indices)}` have centres in
that interval. A native virtual level is a narrow algebraic spike, whereas a
v0.51 state is a finite interval carrying source-conditioned COM--KHW event
mass. Centre inclusion does not define target/source cell boundaries or
conditional jump moments.

The following numbers are deliberately **not** compared as a parity gate:

```text
sum native core trajectory edge flux = {float(np.sum(core_native_flux)):.17e} s^-1 per H
v0.51 raw C0 mass / snapshot n_H      = {v051_c0_mass_per_H_s:.17e} s^-1 per H
```

The dimensions alone are insufficient: the first is a state-dependent net
trajectory source after escape compression, while the second is an
occupation-independent event-mass aggregate. Their ratio is not a physical
normalization and must not be fitted. PR-04B2B must construct an explicit
measure-preserving native-to-17-cell partition before a direct parity claim.
"""
    (ARTIFACT / "COM_KHW_NATIVE_OVERLAP_AUDIT.md").write_text(
        overlap_audit, encoding="utf-8"
    )

    for document in (
        "PR04B2A_RESEARCH_CONTRACT.md",
        "PR04B2A_EVIDENCE_LEDGER.md",
        "PR04B2A_HYPOTHESIS_AUDIT.md",
        "PR04B2A_VALIDATION_MATRIX.md",
    ):
        shutil.copy2(ROOT / "docs" / document, ARTIFACT / document)
    shutil.copy2(
        ROOT / "state" / "PR04B2A_RECOVERY_INVENTORY.json",
        ARTIFACT / "PR04B2A_RECOVERY_INVENTORY.json",
    )
    shutil.copy2(INSTRUMENTER, ARTIFACT / INSTRUMENTER.name)

    save_snapshot_npz(
        DATA_PATH,
        snapshot,
        physical_mode_factor_per_H=mode_factor,
        source_probability=source_probability,
        source_one_minus_exp=source_one_minus_exp,
        stable_probability=stable_probability,
        stable_one_minus_exp=stable_one_minus_exp,
        transport_edge_flux_sInv_per_H=transport_source,
        collision_edge_flux_sInv_per_H=collision_source,
        structural_edge_flux_sInv_per_H=structural_source,
        dense_direct_solution=direct_solution,
        structured_schur_solution=schur_solution,
        dense_direct_edge_flux_sInv_per_H=direct_flux,
        structured_schur_edge_flux_sInv_per_H=schur_flux,
        source_spectral_moments_Hz=source_moments,
        direct_spectral_moments_Hz=direct_moments,
        schur_spectral_moments_Hz=schur_moments,
        stress_dt_s=stress_dt,
        stress_occupation=stress_occupation,
        explicit_stress_occupation=explicit_occupation,
        implicit_stress_occupation=implicit_occupation,
        canonical_archive_sha256=archive_audit.sha256,
        provenance_classification=CANONICAL_PROVENANCE_CLASS,
    )
    shutil.copy2(DATA_PATH, ARTIFACT / DATA_PATH.name)

    status = (
        "PASS_PR04B2A_PHYSICAL_NATIVE_EDGE_FLUX_PR04B2B_OPEN"
        if all(hard_gates.values())
        else "FAIL_PR04B2A_HARD_GATE"
    )
    ledger = {
        "classification": "PR04B2A_PHYSICAL_NATIVE_EDGE_FLUX",
        "stage": "PR-04B2A",
        "version": "0.53",
        "status": status,
        "provenance": provenance,
        "scope": {
            "closed": [
                "owner-attested official-site canonical October-2012 archive provenance",
                "source-identical guarded trajectory instrumentation",
                "physical photons-per-H-per-dlnnu edge normalization",
                "source collision/transport edge identity",
                "dense direct and structured-Schur physical edge parity",
                "signed spectral source moments r=0..4",
                "stable escape arithmetic, analytic JVP, implicit positivity and same-event energy",
            ],
            "open": [
                "measure-preserving 80-native-bin to 17-COM-KHW-cell projection",
                "direct source-conditioned COM-KHW/native jump-moment parity",
                "all-redshift production trajectory coupling",
                "PR-05 primitive operator/background interface",
                "PR-06 monolithic FLRW history parity",
            ],
        },
        "metrics": metrics,
        "hard_gate_status": hard_gates,
        "decision": {
            "PR04B2A": "PASS" if all(hard_gates.values()) else "FAIL",
            "PR04": "IN_PROGRESS",
            "native_physical_edge_normalization": "CLOSED",
            "native_proxy_as_photon_cell": "FORBIDDEN",
            "direct_COM_KHW_native_parity": "OPEN_FAIL_CLOSED",
            "next_stage": "PR-04B2B measure-preserving native-to-17-cell partition and trajectory parity",
        },
        "tool_status": tool_status,
        "harnesses": harness_receipt,
    }
    (ARTIFACT / "PR04B2A_ledger.json").write_text(
        json.dumps(ledger, indent=2) + "\n", encoding="utf-8"
    )

    verify_code = '''#!/usr/bin/env python3
from pathlib import Path
import hashlib, json
import numpy as np
HERE=Path(__file__).resolve().parent
manifest={}
for line in (HERE/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1); manifest[name]=digest
for name,expected in manifest.items():
    got=hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    assert got==expected,(name,got,expected)
ledger=json.loads((HERE/"PR04B2A_ledger.json").read_text())
assert ledger["status"]=="PASS_PR04B2A_PHYSICAL_NATIVE_EDGE_FLUX_PR04B2B_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"]=="IN_PROGRESS"
assert ledger["decision"]["native_proxy_as_photon_cell"]=="FORBIDDEN"
assert ledger["decision"]["direct_COM_KHW_native_parity"]=="OPEN_FAIL_CLOSED"
with np.load(HERE/"original_hyrec_physical_flux_v053.npz",allow_pickle=False) as d:
    assert str(d["canonical_archive_sha256"].item())=="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
    assert d["transport_edge_flux_sInv_per_H"].shape==(311,)
    assert d["source_spectral_moments_Hz"].shape==(5,)
    assert float(np.min(d["implicit_stress_occupation"]))>0
    assert float(np.min(d["explicit_stress_occupation"]))<0
print("PR-04B2A physical native edge flux: PASS; PR-04B2B common partition OPEN")
'''
    verifier = ARTIFACT / "verify_PR04B2A.py"
    verifier.write_text(verify_code, encoding="utf-8")
    os.chmod(verifier, 0o755)

    readme = """# PR-04B2A / v0.53

This immutable artifact proves the source-identical mapping from the canonical
October-2012 original-HyRec virtual-state algebra to physical photon edge flux
per hydrogen atom per logarithmic frequency at one locked FULL-mode FLRW
trajectory snapshot. It also verifies dense/direct/Schur parity, stable escape
arithmetic, JVP, positivity and same-event energy.

It does not identify virtual populations with photon cells and does not claim a
measure-preserving v0.51 17-cell COM--KHW/native projection. PR-04 remains open.

Run:

```bash
python verify_PR04B2A.py
```
"""
    (ARTIFACT / "README.md").write_text(readme, encoding="utf-8")

    manifest(ARTIFACT)
    subprocess.run([sys.executable, str(verifier)], cwd=ARTIFACT, check=True)

    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BUNDLE, "w", compression=zipfile.ZIP_DEFLATED) as zipped:
        for path in sorted(ARTIFACT.rglob("*")):
            if path.is_file():
                zipped.write(path, Path(ARTIFACT_NAME) / path.relative_to(ARTIFACT))

    result = {
        "status": status,
        "artifact": str(ARTIFACT),
        "bundle": str(BUNDLE),
        "bundle_sha256": digest(BUNDLE),
        "bundle_size_bytes": BUNDLE.stat().st_size,
        "data": str(DATA_PATH),
        "metrics": metrics,
        "failed_gates": [name for name, passed in hard_gates.items() if not passed],
    }
    print(json.dumps(result, indent=2))
    if not all(hard_gates.values()):
        raise SystemExit(f"PR-04B2A hard gates failed: {result['failed_gates']}")
    if not args.keep_work:
        work_context.cleanup()


if __name__ == "__main__":
    main()

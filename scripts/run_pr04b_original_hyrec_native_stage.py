#!/usr/bin/env python3
"""Build the immutable PR-04B1/v0.52 original-HyRec native-map release."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from full_bianchi_hyrec.recoil.original_hyrec_native import (  # noqa: E402
    DIFFUSION_START,
    DIFFUSION_STOP,
    E21_EV,
    H_PLANCK_EV_S,
    NDIFF,
    NSUBLYA,
    ORIGINAL_HYREC_ARCHIVE_BYTES,
    ORIGINAL_HYREC_ARCHIVE_ENTRY_COUNT,
    ORIGINAL_HYREC_ARCHIVE_SHA256,
    ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
    ORIGINAL_HYREC_PORTABLE_BINARY_SHA256,
    audit_original_hyrec_archive,
    build_native_diffusion_network,
    central_difference_jvp_residual,
    inferred_log_cell_edges_eV,
    inferred_photon_mode_measure_m3,
    physical_number_map_residual,
    populate_original_hyrec_diffusion,
    read_two_photon_table,
    safe_extract_original_hyrec_archive,
    schur_reduce_line_centre,
    sha256_file,
)

ARTIFACT_NAME = "Full_Bianchi_HyRec_PR04B1_original_HyRec_native_map_v0_52"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
INPUT_ARCHIVE = (
    ROOT
    / "archive"
    / "inputs"
    / "original_hyrec_oct2012"
    / "HyRec_Oct2012.zip"
)
DATA_PATH = ROOT / "data" / "original_hyrec_native_v052.npz"
C3B1 = (
    ROOT
    / "archive"
    / "expanded"
    / "Full_Bianchi_HyRec_C3B1_native_sparse_block_v0_27"
)
DIFFUSION_HARNESS = (
    ROOT / "scripts" / "c_harness" / "original_hyrec_native_diffusion_harness.c"
)
FULL_HARNESS = (
    ROOT / "scripts" / "c_harness" / "original_hyrec_full_matrix_harness.c"
)


def digest(path: Path) -> str:
    return sha256_file(path)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def relative_inf(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(
        np.linalg.norm(a - b, ord=np.inf)
        / max(np.linalg.norm(b, ord=np.inf), 1e-300)
    )


def run(
    command: list[str],
    *,
    cwd: Path,
    stdout: Path | None = None,
    stderr: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    # Makefiles often read PWD rather than calling getcwd().  subprocess(cwd=)
    # does not rewrite the inherited PWD variable, so lock it explicitly.
    env["PWD"] = str(cwd)
    if stdout is not None and stderr is not None and stdout == stderr:
        with stdout.open("wb") as handle:
            return subprocess.run(
                command,
                cwd=cwd,
                env=env,
                stdout=handle,
                stderr=subprocess.STDOUT,
                check=check,
            )
    stdout_handle = stdout.open("wb") if stdout is not None else subprocess.PIPE
    stderr_handle = stderr.open("wb") if stderr is not None else subprocess.PIPE
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=stdout_handle,
            stderr=stderr_handle,
            check=check,
        )
    finally:
        if stdout is not None:
            stdout_handle.close()
        if stderr is not None:
            stderr_handle.close()


def normalize_text_receipt(path: Path, replacements: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for source, target in replacements.items():
        text = text.replace(source, target)
    normalized = text.replace("\r\n", "\n")
    lines = [line.rstrip() for line in normalized.splitlines()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def archive_inventory(path: Path) -> list[dict]:
    rows: list[dict] = []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            content = b"" if info.is_dir() else archive.read(info)
            rows.append(
                {
                    "path": info.filename,
                    "is_directory": info.is_dir(),
                    "bytes": info.file_size,
                    "compressed_bytes": info.compress_size,
                    "crc32": f"{info.CRC:08x}",
                    "modified": "%04d-%02d-%02dT%02d:%02d:%02d"
                    % info.date_time,
                    "create_system": info.create_system,
                    "sha256": "" if info.is_dir() else hashlib.sha256(content).hexdigest(),
                }
            )
    return rows


def parse_diffusion_output(path: Path) -> tuple[dict[str, float], list[dict]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    scalar = {
        line.split(",", 1)[0]: float(line.split(",", 1)[1])
        for line in lines[:3]
    }
    rows = list(csv.DictReader(lines[3:]))
    return scalar, rows


def parse_full_output(path: Path) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    meta: dict[str, float] = {}
    arrays = {
        "Trr": np.zeros((2, 2)),
        "Trv": np.zeros((2, 311)),
        "Tvr": np.zeros((2, 311)),
        "Tvv": np.zeros((3, 311)),
        "sr": np.zeros(2),
        "sv": np.zeros(311),
        "Dtau": np.zeros(311),
        "xr": np.zeros(2),
        "xv": np.zeros(311),
    }
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            key = row[0]
            if key == "META":
                meta[row[1]] = float(row[2])
            elif key == "Trr":
                arrays[key][int(row[1]), int(row[2])] = float(row[3])
            elif key in {"Trv", "Tvr", "Tvv"}:
                arrays[key][int(row[1]), int(row[2])] = float(row[3])
            else:
                arrays[key][int(row[1])] = float(row[3])
    return meta, arrays


def dense_native_matrix(arrays: dict[str, np.ndarray]) -> np.ndarray:
    matrix = np.zeros((313, 313), dtype=float)
    matrix[:2, :2] = arrays["Trr"]
    matrix[:2, 2:] = arrays["Trv"]
    matrix[2:, :2] = arrays["Tvr"].T
    matrix[2:, 2:] = np.diag(arrays["Tvv"][0])
    for b in range(311):
        if b > 0:
            matrix[2 + b, 2 + b - 1] = arrays["Tvv"][1, b]
        if b < 310:
            matrix[2 + b, 2 + b + 1] = arrays["Tvv"][2, b]
    return matrix


def structured_schur(arrays: dict[str, np.ndarray]) -> np.ndarray:
    tvv = dense_native_matrix(arrays)[2:, 2:]
    inv_tvr = np.linalg.solve(tvv, arrays["Tvr"].T)
    inv_sv = np.linalg.solve(tvv, arrays["sv"])
    teff = arrays["Trr"] - arrays["Trv"] @ inv_tvr
    seff = arrays["sr"] - arrays["Trv"] @ inv_sv
    xr = np.linalg.solve(teff, seff)
    xv = inv_sv - inv_tvr @ xr
    return np.concatenate([xr, xv])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep-work", action="store_true")
    args = parser.parse_args()

    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    BUNDLE.unlink(missing_ok=True)

    audit = audit_original_hyrec_archive(INPUT_ARCHIVE)
    if not audit.safe:
        raise RuntimeError("input archive safety audit failed")
    if audit.sha256 != ORIGINAL_HYREC_ARCHIVE_SHA256:
        raise RuntimeError("input archive SHA-256 mismatch")
    if audit.size_bytes != ORIGINAL_HYREC_ARCHIVE_BYTES:
        raise RuntimeError("input archive byte-size mismatch")
    if audit.entry_count != ORIGINAL_HYREC_ARCHIVE_ENTRY_COUNT:
        raise RuntimeError("input archive entry-count mismatch")

    inventory = archive_inventory(INPUT_ARCHIVE)
    write_csv(ARTIFACT / "ORIGINAL_HYREC_ARCHIVE_INVENTORY.csv", inventory)

    work_context = tempfile.TemporaryDirectory(prefix="pr04b1-")
    work = Path(work_context.name)
    safe_extract_original_hyrec_archive(INPUT_ARCHIVE, work)
    source = work / "HyRec"

    # Build original sources without modifying them.  The shipped Makefile asks
    # for Intel icc; the portable audit uses the same C bytes with GNU gcc.
    make_log = ARTIFACT / "ORIGINAL_MAKEFILE_ATTEMPT.log"
    make_result = run(["make"], cwd=source, stdout=make_log, stderr=make_log, check=False)
    portable = work / "hyrec_portable"
    build_log = ARTIFACT / "ORIGINAL_PORTABLE_BUILD.log"
    run(
        [
            "gcc",
            "-std=c11",
            "-D_DEFAULT_SOURCE",
            "-O3",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "hyrectools.c",
            "helium.c",
            "hydrogen.c",
            "history.c",
            "hyrec.c",
            "-lm",
            "-o",
            str(portable),
        ],
        cwd=source,
        stdout=build_log,
        stderr=build_log,
    )
    baseline_output = ARTIFACT / "ORIGINAL_BASELINE_HISTORY.txt"
    baseline_stderr = ARTIFACT / "ORIGINAL_BASELINE_STDERR.txt"
    with (source / "input.dat").open("rb") as stdin, baseline_output.open(
        "wb"
    ) as stdout, baseline_stderr.open("wb") as stderr:
        baseline = subprocess.run(
            [str(portable)], cwd=source, stdin=stdin, stdout=stdout, stderr=stderr
        )
    if baseline.returncode != 0:
        raise RuntimeError("original HyRec baseline execution failed")

    # Exact original C diffusion and full real/virtual matrix harnesses.
    diffusion_exe = work / "native_diffusion_harness"
    diffusion_build = ARTIFACT / "ORIGINAL_DIFFUSION_HARNESS_BUILD.log"
    run(
        [
            "gcc",
            "-std=c11",
            "-D_DEFAULT_SOURCE",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-I",
            str(source),
            str(DIFFUSION_HARNESS),
            str(source / "hydrogen.c"),
            str(source / "hyrectools.c"),
            "-lm",
            "-o",
            str(diffusion_exe),
        ],
        cwd=source,
        stdout=diffusion_build,
        stderr=diffusion_build,
    )
    diffusion_output = ARTIFACT / "ORIGINAL_C_DIFFUSION_3000K.csv"
    run([str(diffusion_exe), "3000"], cwd=source, stdout=diffusion_output)

    full_exe = work / "native_full_harness"
    full_build = ARTIFACT / "ORIGINAL_FULL_MATRIX_HARNESS_BUILD.log"
    run(
        [
            "gcc",
            "-std=c11",
            "-D_DEFAULT_SOURCE",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-I",
            str(source),
            str(FULL_HARNESS),
            str(source / "hydrogen.c"),
            str(source / "hyrectools.c"),
            "-lm",
            "-o",
            str(full_exe),
        ],
        cwd=source,
        stdout=full_build,
        stderr=full_build,
    )
    full_output = ARTIFACT / "ORIGINAL_C_FULL_MATRIX_REGRESSION.csv"
    run([str(full_exe)], cwd=source, stdout=full_output)

    receipt_replacements = {
        str(work): "<WORKDIR>",
        str(ROOT): "<REPOSITORY_ROOT>",
    }
    for receipt in (
        make_log,
        build_log,
        diffusion_build,
        full_build,
        baseline_stderr,
    ):
        normalize_text_receipt(receipt, receipt_replacements)

    table_path = source / "two_photon_tables.dat"
    table = read_two_photon_table(table_path)
    rates = populate_original_hyrec_diffusion(table, 3000.0)
    network = build_native_diffusion_network(rates)
    reduced = schur_reduce_line_centre(network)
    edges = inferred_log_cell_edges_eV(rates.energy_eV)
    mode_measure = inferred_photon_mode_measure_m3(edges)
    physical_map_residual = physical_number_map_residual(reduced, mode_measure)

    scalar_c, diffusion_rows = parse_diffusion_output(diffusion_output)
    c_up = np.asarray([float(row["Aup_s_inv"]) for row in diffusion_rows])
    c_down = np.asarray([float(row["Adn_s_inv"]) for row in diffusion_rows])
    active = slice(DIFFUSION_START, DIFFUSION_STOP)
    c_python_rate_residual = max(
        relative_inf(c_up, rates.Aup_s_inv[active]),
        relative_inf(c_down, rates.Adn_s_inv[active]),
        abs(scalar_c["A2p_up_s_inv"] - rates.A2p_up_s_inv)
        / rates.A2p_up_s_inv,
        abs(scalar_c["A2p_dn_s_inv"] - rates.A2p_dn_s_inv)
        / rates.A2p_dn_s_inv,
    )

    meta_c, full_c = parse_full_output(full_output)
    full_matrix = dense_native_matrix(full_c)
    rhs = np.concatenate([full_c["sr"], full_c["sv"]])
    c_solution = np.concatenate([full_c["xr"], full_c["xv"]])
    direct_solution = np.linalg.solve(full_matrix, rhs)
    schur_solution = structured_schur(full_c)
    direct_residual = relative_inf(full_matrix @ direct_solution, rhs)
    c_direct_difference = relative_inf(c_solution, direct_solution)
    schur_direct_difference = relative_inf(schur_solution, direct_solution)

    with np.load(C3B1 / "native_sparse_block_snapshot.npz", allow_pickle=False) as old:
        prior = {
            "Trr": old["Trr"],
            "Trv": old["Trv"],
            "Tvr": old["Tvr"],
            "Tvv0": old["Tvv_diag"],
            "Tvv1": old["Tvv_lower"],
            "Tvv2": old["Tvv_upper"],
            "sr": old["sr"],
            "sv": old["sv"],
            "Dtau": old["Dtau"],
            "solution": old["direct_solution"],
        }
        prior_residuals = {
            "Trr": relative_inf(full_c["Trr"], prior["Trr"]),
            "Trv": relative_inf(full_c["Trv"], prior["Trv"]),
            "Tvr": relative_inf(full_c["Tvr"], prior["Tvr"]),
            "Tvv_diag": relative_inf(full_c["Tvv"][0], prior["Tvv0"]),
            "Tvv_lower": relative_inf(full_c["Tvv"][1], prior["Tvv1"]),
            "Tvv_upper": relative_inf(full_c["Tvv"][2], prior["Tvv2"]),
            "sr": relative_inf(full_c["sr"], prior["sr"]),
            "sv": relative_inf(full_c["sv"], prior["sv"]),
            "Dtau": relative_inf(full_c["Dtau"], prior["Dtau"]),
            "solution": relative_inf(c_solution, prior["solution"]),
        }
    original_vs_prior_max = max(prior_residuals.values())

    scale = float(np.max(np.abs(network.generator_s_inv)))
    column_residual = float(
        np.max(np.abs(network.generator_s_inv.sum(axis=0))) / scale
    )
    equilibrium_residual = float(
        np.max(np.abs(network.generator_s_inv @ network.equilibrium_proxy))
        / (scale * np.max(network.equilibrium_proxy))
    )
    parity_residuals = []
    for order in range(5):
        tensor = network.proxy_moments_Hz[order]
        parity_residuals.append(
            float(
                np.max(np.abs(tensor - (-1) ** order * tensor.T))
                / max(np.max(np.abs(tensor)), 1e-300)
            )
        )
    reduced_scale = float(np.max(np.abs(reduced.generator_s_inv)))
    reduced_column_residual = float(
        np.max(np.abs(reduced.generator_s_inv.sum(axis=0))) / reduced_scale
    )
    reduced_equilibrium_residual = float(
        np.max(
            np.abs(reduced.generator_s_inv @ reduced.equilibrium_proxy)
        )
        / (reduced_scale * np.max(reduced.equilibrium_proxy))
    )

    state = network.equilibrium_proxy * (
        1.0 + 0.09 * np.sin(np.arange(network.state_count))
    )
    direction = np.cos(np.arange(network.state_count) * 0.37)
    jvp_residual = central_difference_jvp_residual(
        network.generator_s_inv, state, direction
    )
    implicit = network.backward_euler(state, 1e-3)
    implicit_minimum = float(np.min(implicit))
    implicit_number_relative = float(
        abs(np.sum(implicit) - np.sum(state)) / np.sum(state)
    )

    # Baseline checkpoints.
    baseline_rows = {}
    for line in baseline_output.read_text().splitlines():
        z, xe, tm_ratio = map(float, line.split())
        baseline_rows[int(round(z))] = (xe, tm_ratio)
    checkpoints = []
    for redshift in (2000, 1600, 1300, 1100, 900, 500, 100, 0):
        xe, ratio = baseline_rows[redshift]
        checkpoints.append(
            {
                "z": redshift,
                "xe": f"{xe:.17g}",
                "Tm_over_T0_1pz": f"{ratio:.17g}",
            }
        )
    write_csv(ARTIFACT / "ORIGINAL_BASELINE_CHECKPOINTS.csv", checkpoints)

    variable_rows = []
    for local, global_index in enumerate(range(DIFFUSION_START, DIFFUSION_STOP)):
        variable_rows.append(
            {
                "local_index": local,
                "virtual_index": global_index,
                "centre_eV": f"{rates.energy_eV[global_index]:.17g}",
                "centre_Hz": f"{rates.energy_eV[global_index] / H_PLANCK_EV_S:.17g}",
                "inferred_left_edge_eV": f"{edges[local]:.17g}",
                "inferred_right_edge_eV": f"{edges[local + 1]:.17g}",
                "inferred_mode_measure_m3": f"{mode_measure[local]:.17g}",
                "native_equilibrium_proxy": f"{network.equilibrium_proxy[local]:.17g}",
                "Aup_s_inv": f"{rates.Aup_s_inv[global_index]:.17g}",
                "Adn_s_inv": f"{rates.Adn_s_inv[global_index]:.17g}",
            }
        )
    write_csv(ARTIFACT / "NATIVE_VARIABLE_AND_MODE_MAP.csv", variable_rows)

    parity_rows = [
        {"moment_order": order, "exchange_parity_relative_residual": value}
        for order, value in enumerate(parity_residuals)
    ]
    write_csv(ARTIFACT / "NATIVE_PROXY_MOMENT_PARITY.csv", parity_rows)
    write_csv(
        ARTIFACT / "ORIGINAL_C_VS_PINNED_C3B1.csv",
        [
            {"object": name, "relative_inf_residual": value, "gate": "1e-10"}
            for name, value in prior_residuals.items()
        ],
    )

    source_conventions = [
        {
            "quantity": "native radiation variable",
            "definition": "Delta x_b = x_b - x_1s exp(-h nu_b/T_r) = x_1s Delta f_nu_b",
            "units": "dimensionless",
            "source": "technical supplement Eq. (6); hydrogen.c May-2012 revision note",
        },
        {
            "quantity": "virtual proxy",
            "definition": "x_b = x_1s f_nu_b; xv/x_1s is the average distortion in bin b",
            "units": "dimensionless",
            "source": "technical supplement; hydrogen.c lines 727-799",
        },
        {
            "quantity": "native matrix",
            "definition": "T X = s; Tvv diagonal positive and transition off-diagonals negative",
            "units": "T: s^-1, X: dimensionless, s: s^-1",
            "source": "hydrogen.c populateTS_2photon and solve_real_virt",
        },
        {
            "quantity": "time variable",
            "definition": "d/dt = H d/d ln a",
            "units": "H: s^-1",
            "source": "history.c and returned dx_e/d ln a",
        },
        {
            "quantity": "frequency convention",
            "definition": "ordinary nu=E/h; Delta nu=nu_target-nu_source",
            "units": "Hz",
            "source": "project adapter lock",
        },
        {
            "quantity": "physical spectral diagnostic",
            "definition": "(8 pi nu^3)/(c^3 n_H) Delta f_nu per log-frequency per H",
            "units": "dimensionless",
            "source": "hyrec.c PRINT_SPEC header",
        },
    ]
    write_csv(ARTIFACT / "ORIGINAL_HYREC_CONVENTION_CENSUS.csv", source_conventions)

    source_lock = {
        "classification": "PR04B1_ORIGINAL_HYREC_SOURCE_LOCK",
        "archive": {
            "path": str(INPUT_ARCHIVE.relative_to(ROOT)),
            "sha256": audit.sha256,
            "bytes": audit.size_bytes,
            "entry_count": audit.entry_count,
            "file_count": audit.file_count,
            "directory_count": audit.directory_count,
            "total_uncompressed_bytes": audit.total_uncompressed_bytes,
            "total_compressed_bytes": audit.total_compressed_bytes,
            "zip_integrity": "PASS",
            "unsafe_paths": list(audit.unsafe_paths),
            "duplicate_names": list(audit.duplicate_names),
            "symlinks": list(audit.symlinks),
        },
        "provenance": {
            "owner_supplied_filename": "HyRec_Oct2012.zip",
            "official_page_correspondence": "Official HyRec page lists an October 2012 stable release",
            "independent_official_byte_identity": "NOT_VERIFIED_IN_NETWORK_ISOLATED_RUNTIME",
            "internal_headers": "May 2012",
            "package_timestamp_evidence": "history.c and Makefile modified 2012-10-05 in ZIP metadata",
            "classification": "USER_SUPPLIED_OFFICIAL_CANDIDATE_BYTE_LOCKED",
        },
        "selected_members": {
            row["path"]: {"sha256": row["sha256"], "bytes": row["bytes"]}
            for row in inventory
            if row["path"]
            in {
                "HyRec/Makefile",
                "HyRec/history.c",
                "HyRec/hydrogen.c",
                "HyRec/hydrogen.h",
                "HyRec/hyrec_params.h",
                "HyRec/two_photon_tables.dat",
                "HyRec/readme.pdf",
                "HyRec/supplement.pdf",
            }
        },
        "build": {
            "shipped_make_returncode": make_result.returncode,
            "shipped_make_blocker": "icc unavailable in runtime" if make_result.returncode else None,
            "portable_source_byte_unchanged_build": "PASS",
            "portable_binary_sha256": digest(portable),
            "reference_runtime_binary_sha256": ORIGINAL_HYREC_PORTABLE_BINARY_SHA256,
            "baseline_exit_code": baseline.returncode,
            "baseline_output_sha256": digest(baseline_output),
            "reference_baseline_output_sha256": ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
            "baseline_output_lines": len(baseline_output.read_text().splitlines()),
        },
    }
    (ARTIFACT / "ORIGINAL_HYREC_SOURCE_LOCK.json").write_text(
        json.dumps(source_lock, indent=2) + "\n"
    )

    np.savez_compressed(
        DATA_PATH,
        classification=np.asarray("PR04B1_ORIGINAL_HYREC_NATIVE_PROXY_MAP"),
        archive_sha256=np.asarray(audit.sha256),
        source_table_sha256=np.asarray(digest(table_path)),
        temperature_K=np.asarray(3000.0),
        virtual_indices=np.arange(DIFFUSION_START, DIFFUSION_STOP),
        energy_eV=rates.energy_eV[active],
        frequency_Hz=network.frequency_Hz,
        Aup_sInv=rates.Aup_s_inv[active],
        Adn_sInv=rates.Adn_s_inv[active],
        A2p_up_sInv=np.asarray(rates.A2p_up_s_inv),
        A2p_dn_sInv=np.asarray(rates.A2p_dn_s_inv),
        native_generator_sInv=network.generator_s_inv,
        native_equilibrium_proxy=network.equilibrium_proxy,
        native_proxy_moments_Hz=network.proxy_moments_Hz,
        schur_generator_sInv=reduced.generator_s_inv,
        schur_equilibrium_proxy=reduced.equilibrium_proxy,
        inferred_energy_edges_eV=edges,
        inferred_photon_mode_measure_m3=mode_measure,
        physical_number_map_relative_residual=np.asarray(physical_map_residual),
        original_c_full_matrix=full_matrix,
        original_c_rhs=rhs,
        original_c_solution=c_solution,
        direct_solution=direct_solution,
        schur_solution=schur_solution,
    )
    shutil.copy2(DATA_PATH, ARTIFACT / DATA_PATH.name)
    shutil.copy2(DIFFUSION_HARNESS, ARTIFACT / DIFFUSION_HARNESS.name)
    shutil.copy2(FULL_HARNESS, ARTIFACT / FULL_HARNESS.name)

    hard_gates = {
        "archive_byte_lock": audit.sha256 == ORIGINAL_HYREC_ARCHIVE_SHA256,
        "archive_safe": audit.safe,
        "portable_build": baseline.returncode == 0,
        "baseline_history_hash": digest(baseline_output)
        == ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
        "source_table_matches_pinned_HYREC2": digest(table_path)
        == "93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9",
        "original_C_python_diffusion_parity": c_python_rate_residual < 3e-15,
        "original_C_full_matrix_vs_prior": original_vs_prior_max < 1e-10,
        "direct_matrix_residual": direct_residual < 5e-13,
        "original_C_direct_solution": c_direct_difference < 2e-10,
        "Schur_direct_equivalence": schur_direct_difference < 5e-13,
        "native_column_conservation": column_residual < 2e-15,
        "native_detailed_balance": equilibrium_residual < 2e-15,
        "native_moment_exchange_parity": max(parity_residuals) < 5e-15,
        "native_even_moment_positivity": bool(
            np.all(network.proxy_moments_Hz[2] >= 0.0)
            and np.all(network.proxy_moments_Hz[4] >= 0.0)
        ),
        "Schur_column_conservation": reduced_column_residual < 2e-15,
        "Schur_detailed_balance": reduced_equilibrium_residual < 2e-15,
        "analytic_JVP": jvp_residual < 2e-9,
        "implicit_positivity": implicit_minimum > 0.0,
        "implicit_proxy_number": implicit_number_relative < 5e-14,
        "physical_measure_substitution_firewall": physical_map_residual > 1e-4,
    }

    metrics = {
        "archive_sha256": audit.sha256,
        "archive_bytes": audit.size_bytes,
        "baseline_output_sha256": digest(baseline_output),
        "portable_binary_sha256": digest(portable),
        "C_python_rate_relative_residual": c_python_rate_residual,
        "original_C_vs_pinned_C3B1_max_relative_residual": original_vs_prior_max,
        "direct_matrix_relative_residual": direct_residual,
        "original_C_vs_direct_solution_relative_difference": c_direct_difference,
        "Schur_vs_direct_relative_difference": schur_direct_difference,
        "native_column_relative_residual": column_residual,
        "native_equilibrium_relative_residual": equilibrium_residual,
        "native_moment_max_exchange_parity_residual": max(parity_residuals),
        "Schur_column_relative_residual": reduced_column_residual,
        "Schur_equilibrium_relative_residual": reduced_equilibrium_residual,
        "Schur_red_to_blue_bridge_sInv": reduced.direct_bridge_red_to_blue_s_inv,
        "Schur_blue_to_red_bridge_sInv": reduced.direct_bridge_blue_to_red_s_inv,
        "analytic_JVP_relative_residual": jvp_residual,
        "implicit_minimum_proxy_state": implicit_minimum,
        "implicit_proxy_number_relative_change": implicit_number_relative,
        "inferred_physical_mode_weight_min_m3": float(np.min(mode_measure)),
        "inferred_physical_mode_weight_max_m3": float(np.max(mode_measure)),
        "physical_number_map_relative_residual": physical_map_residual,
    }

    formalism = r"""# PR-04B1 original-HyRec native primitive map

## Scope and conventions

This bounded stage byte-locks the owner-supplied `HyRec_Oct2012.zip`, compiles
its unmodified C sources, and derives the original native Ly-alpha diffusion
block.  It does **not** yet identify that algebraic proxy block with the
physical `m^-3 s^-1 Hz^r` event measure of PR-04A.

The project conventions remain

\[
 g_{\mu\nu}=(-,+,+,+),\qquad \nu=E/h,
 \qquad \Delta\nu=\nu_{\rm target}-\nu_{\rm source},
\]
\[
 \Delta E_\gamma=h\Delta\nu,\qquad
 \Delta E_{\rm H}=-h\Delta\nu .
\]

Original HyRec uses cgs lengths and eV temperatures.  Its native matrix
coefficients are in `s^-1`.

## Native variable

The technical supplement and `hydrogen.c` identify the virtual proxy as

\[
 \Delta x_b=x_b-x_{1s}e^{-h\nu_b/T_r}=x_{1s}\Delta f_{\nu_b}.
\]

`x_b` is not an atomic population and is not a photon number per cell.  The
stored spectrum is `x_v/x_1s`, the average occupation distortion in a bin.
The physical spectral diagnostic printed by original HyRec is

\[
 {8\pi\nu^3\over c^3 n_H}\Delta f_\nu
\]

per logarithmic frequency interval per hydrogen atom.

## Primitive diffusion network

For the 80 virtual bins `b=100,...,179`, original HyRec constructs
`Aup[b]=A_{b,b+1}` and `Adn[b]=A_{b,b-1}`.  The unresolved 2p line centre is an
81st proxy state.  With the matrix-generator convention

\[
 \dot x_i=\sum_j Q_{ij}x_j,
\]

all off-diagonal `Q_ij` are nonnegative and every column sums to zero.  The
reversible proxy measure is

\[
 \pi_b=e^{-E_b/T_m},\qquad
 \pi_{2p}=3e^{-E_{21}/T_m}.
\]

It obeys `Q pi=0`.  The oriented proxy moment tensor is

\[
 C^{(r)}_{ij}=\pi_j Q_{ij}(\nu_i-\nu_j)^r,
 \qquad i\ne j,
\]

with units `Hz^r s^-1`, not `m^-3 s^-1 Hz^r`, and exact exchange parity

\[
 C^{(r)}_{ji}=(-1)^r C^{(r)}_{ij}.
\]

## Exact 2p Schur elimination

Writing original HyRec's positive-diagonal matrix as `T=-Q`, the line-centre
proxy can be eliminated in the steady system:

\[
 T_{\rm eff}=T_{vv}-T_{vp}T_{pp}^{-1}T_{pv},\qquad
 Q_{\rm eff}=-T_{\rm eff}.
\]

The reduced 80-state generator remains conservative and reversible and
creates the exact red-to-blue bridge mediated by the unresolved 2p proxy.

## Physical-measure firewall

For diagnostic log-frequency edges, a physical photon mode weight is

\[
 g_b={8\pi\over 3c^3}
 \left(\nu_{b,+}^3-\nu_{b,-}^3\right).
\]

The primitive native block conserves `sum_b x_b`, whereas a physical
finite-volume photon generator would require `g^T Q=0`.  The measured nonzero
weighted-left-null residual is therefore a positive firewall result: direct
`Aup/Adn` substitution into the PR-04A physical common measure is forbidden.
The remaining PR-04B2 task must derive the escape/redshift/bin map on one
physical measure; it may not fit a multiplicative scale.
"""
    (ARTIFACT / "PR04B1_ORIGINAL_HYREC_NATIVE_FORMALISM.md").write_text(
        formalism, encoding="utf-8"
    )

    literature = """# Literature and source-role lock

- Official HyRec page: the previous stable releases include October 2012,
  May 2012 and January 2011. Original HyRec performs numerical time-dependent
  radiative transfer, including Lyman feedback, two-photon/Raman processes and
  Ly-alpha frequency diffusion.
- Ali-Haimoud & Hirata (2011), arXiv:1011.3758: full radiative transfer with
  simultaneous radiation-field, level-population and free-electron evolution.
- Lee & Ali-Haimoud (2020), arXiv:2007.14114: HYREC-2 is an effective four-level
  implementation whose Ly-alpha escape correction is computed using original
  HyRec and tabulated.

The owner-supplied ZIP is byte-locked. The official web page identifies an
October-2012 stable release, and ZIP timestamps place `history.c` and `Makefile`
on 2012-10-05. Internal C headers still say May 2012. Because this runtime did
not independently download the official binary, exact equality to the current
server-side October-2012 bytes is not claimed.
"""
    (ARTIFACT / "PR04B1_LITERATURE_LOCK.md").write_text(
        literature, encoding="utf-8"
    )

    status = (
        "PASS_PR04B1_ORIGINAL_HYREC_SOURCE_NATIVE_PROXY_MAP_PR04B2_OPEN"
        if all(hard_gates.values())
        else "FAIL_PR04B1_HARD_GATE"
    )
    ledger = {
        "classification": "PR04B1_ORIGINAL_HYREC_NATIVE_PROXY_MAP",
        "stage": "PR-04B1",
        "version": "0.52",
        "status": status,
        "scope": {
            "closed": [
                "owner-supplied October-2012 candidate byte/source lock",
                "source-byte-unchanged GNU build and baseline history",
                "exact original-C populate_Diffusion parity",
                "original-C 313-state real/virtual matrix and Schur parity",
                "81-state reversible native proxy common measure",
                "2p steady Schur elimination",
                "analytic JVP and positive conservative implicit proxy update",
                "direct physical-measure substitution firewall",
            ],
            "open": [
                "independent download equality to official October-2012 binary",
                "native redshift/escape/bin map on the physical PR-04A measure",
                "direct v0.51 event versus native primitive moment parity",
                "instrumented full-trajectory FLRW radiation snapshot parity",
            ],
        },
        "source_lock": source_lock,
        "metrics": metrics,
        "hard_gate_status": hard_gates,
        "decision": {
            "PR04B1": "PASS" if all(hard_gates.values()) else "FAIL",
            "PR04": "IN_PROGRESS",
            "native_proxy_measure": "VERIFIED_DIMENSIONLESS_REVERSIBLE_DIAGNOSTIC",
            "native_raw_rate_substitution": "FORBIDDEN",
            "physical_common_measure_parity": "OPEN_FAIL_CLOSED",
            "official_archive_byte_identity": "OWNER_INPUT_LOCKED_INDEPENDENT_REMOTE_EQUALITY_UNVERIFIED",
        },
        "tool_status": {
            "web_search": "USED_OFFICIAL_HYREC_PAGE_AND_PRIMARY_PAPERS",
            "Wolfram": "UNAVAILABLE_IN_RUNTIME",
            "Precise_Special_Functions": "UNAVAILABLE_IN_RUNTIME",
            "fallbacks": [
                "NumPy dense and Schur linear algebra",
                "original C source compiled and executed directly",
                "central-difference JVP regression",
            ],
        },
        "next_stage": {
            "name": "PR-04B2 physical native-measure and full-trajectory FLRW closure",
            "tasks": [
                "Instrument a source-identical original-HyRec trajectory to dump Dfplus, Dfminus, xv, Dtau and real/virtual blocks at a locked hydrogen-recombination redshift.",
                "Derive the logarithmic redshift-flux and escape map from the native algebraic proxy coordinate to physical photons per H per log frequency.",
                "Project the v0.51 direct COM-KHW event tensor and native primitive/Schur actions onto one physical measure without a fitted scale.",
                "Close normalization, detailed balance, photon-plus-atom energy, JVP, positivity and one full FLRW snapshot parity gate.",
            ],
        },
    }
    (ARTIFACT / "PR04B1_ledger.json").write_text(
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
ledger=json.loads((HERE/"PR04B1_ledger.json").read_text())
assert ledger["status"]=="PASS_PR04B1_ORIGINAL_HYREC_SOURCE_NATIVE_PROXY_MAP_PR04B2_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"]=="IN_PROGRESS"
assert ledger["decision"]["native_raw_rate_substitution"]=="FORBIDDEN"
with np.load(HERE/"original_hyrec_native_v052.npz",allow_pickle=False) as d:
    assert str(d["archive_sha256"].item())=="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
    assert d["native_generator_sInv"].shape==(81,81)
    assert d["schur_generator_sInv"].shape==(80,80)
    assert float(d["physical_number_map_relative_residual"])>1e-4
print("PR-04B1 original-HyRec native proxy map: PASS; PR-04B2 physical closure OPEN")
'''
    (ARTIFACT / "verify_PR04B1.py").write_text(verify_code, encoding="utf-8")
    os.chmod(ARTIFACT / "verify_PR04B1.py", 0o755)

    readme = """# PR-04B1 / v0.52

This immutable artifact byte-locks and executes the owner-supplied
October-2012 original-HyRec candidate, reproduces its native Ly-alpha
diffusion and real/virtual Schur block, and proves that its dimensionless
virtual proxy measure cannot be directly substituted for the physical PR-04A
photon common measure.

Run:

```bash
python verify_PR04B1.py
```

PR-04 remains in progress. See `PR04B1_ledger.json` for the exact open gates.
"""
    (ARTIFACT / "README.md").write_text(readme, encoding="utf-8")

    # Seal artifact. The manifest deliberately excludes itself.
    manifest_rows = []
    for path in sorted(ARTIFACT.iterdir()):
        if path.is_file() and path.name != "MANIFEST_SHA256.txt":
            manifest_rows.append(f"{digest(path)}  {path.name}")
    (ARTIFACT / "MANIFEST_SHA256.txt").write_text(
        "\n".join(manifest_rows) + "\n", encoding="utf-8"
    )
    subprocess.run([sys.executable, str(ARTIFACT / "verify_PR04B1.py")], check=True)

    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BUNDLE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ARTIFACT.rglob("*")):
            if path.is_file():
                archive.write(path, Path(ARTIFACT_NAME) / path.relative_to(ARTIFACT))

    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(ARTIFACT),
                "bundle": str(BUNDLE),
                "bundle_sha256": digest(BUNDLE),
                "data": str(DATA_PATH),
                "metrics": metrics,
            },
            indent=2,
        )
    )
    if not all(hard_gates.values()):
        failed = [name for name, passed in hard_gates.items() if not passed]
        raise SystemExit(f"PR-04B1 hard gates failed: {failed}")
    if not args.keep_work:
        work_context.cleanup()


if __name__ == "__main__":
    main()

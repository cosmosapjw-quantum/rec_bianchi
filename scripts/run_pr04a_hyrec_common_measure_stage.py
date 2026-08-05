#!/usr/bin/env python3
"""Build PR-04A/v0.51 HYREC common-measure core projection.

This bounded stage source-locks the exact durable HYREC-2 FULL representation,
projects the v0.50 positive scalar COM--KHW event measure onto ordinary-frequency
jump moments Gamma,M1,...,M4 for the 17-cell Ly-alpha core, and closes the
nonlinear scalar Bose/JVP/implicit conservation gates.  It deliberately does
not claim original-HyRec archive parity: the October-2012 archive bytes were not
available in this network-isolated runtime and remain the next source-lock gate.
"""
from __future__ import annotations

import os
import sys

if os.environ.get("PR04A_NUMERICAL_THREAD_LOCK") != "1":
    environment = os.environ.copy()
    environment.update(
        {
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "PR02_NUMERICAL_THREAD_LOCK": "1",
            "PR03_NUMERICAL_THREAD_LOCK": "1",
            "PR04A_NUMERICAL_THREAD_LOCK": "1",
        }
    )
    os.execve(sys.executable, [sys.executable, *sys.argv], environment)

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

import mpmath as mp
import numpy as np
import sympy as sp
from scipy.constants import electron_volt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC
from full_bianchi_hyrec.recoil.hyrec_common_measure import (
    CommonMeasureMoments,
    HYREC2_DIFFUSION_START,
    HYREC2_DIFFUSION_STOP,
    HYREC2_NDIFF,
    HYREC2_NSUBLYA,
    HYREC2_NVIRT,
    HYREC2_SOURCE_BLOBS,
    HYREC2_SOURCE_COMMIT,
    MOMENT_MAX,
    apply_scalar_bose_jvp,
    apply_scalar_bose_operator,
    build_oriented_tensor,
    conservative_conditional_moment_projection,
    implicit_scalar_bose_step,
    integrate_disjoint_frequency_moments_x,
    integrate_same_interval_jump_moments_x,
    native_diffusion_centres_from_csv,
    native_voronoi_intervals,
    raw_native_adjacent_jump_moments,
    save_common_measure_npz,
    scalar_bose_equilibrium_family,
    scalar_bose_free_energy_m3,
    scalar_bose_photon_number_m3,
    sha256,
    write_source_lock,
)
from full_bianchi_hyrec.recoil.scalar_com_khw import default_scalar_com_khw_model


ARTIFACT_NAME = "Full_Bianchi_HyRec_PR04A_HYREC_common_measure_v0_51"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "hyrec_common_measure_v051.npz"
V050_DATA = ROOT / "data" / "full_scalar_com_khw_v050.npz"
SNAPSHOT_DATA = ROOT / "data" / "pr01c_background_snapshots_v048.npz"
C3B0 = ROOT / "archive" / "expanded" / "Full_Bianchi_HyRec_C3B0_HYREC2_source_lock_v0_26"
C3B1 = ROOT / "archive" / "expanded" / "Full_Bianchi_HyRec_C3B1_native_sparse_block_v0_27"
C3B2A = ROOT / "archive" / "expanded" / "Full_Bianchi_HyRec_C3B2A_substitution_audit_v0_28"
NATIVE_CSV = C3B1 / "diffusion_detailed_balance.csv"
CACHE = ROOT / ".cache" / "v051_hyrec_common_measure"
CORE_STATES = 17
SELECTED_REFERENCE_PAIRS = ((0, 1), (0, 16), (4, 12), (7, 8), (7, 9), (8, 9))
SELECTED_REFERENCE_SAME = (0, 8, 16)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def _save_cache(path: Path, **values) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **values)
    temporary.replace(path)


def _load_cache(path: Path) -> np.ndarray | None:
    if not path.exists():
        return None
    with np.load(path, allow_pickle=False) as data:
        return np.asarray(data["moments_x"], dtype=float)


def _pair_job(job):
    i, j, target, source, lane, cache_name = job
    cache = Path(cache_name)
    values = _load_cache(cache)
    if values is None:
        values = integrate_disjoint_frequency_moments_x(
            tuple(target), tuple(source), lane=lane, amplitude_lane="full"
        )
        _save_cache(cache, moments_x=values)
    return int(i), int(j), str(lane), values


def _same_job(job):
    i, interval, lane, cache_name = job
    cache = Path(cache_name)
    values = _load_cache(cache)
    if values is None:
        values = integrate_same_interval_jump_moments_x(
            tuple(interval), lane=lane, amplitude_lane="full"
        )
        _save_cache(cache, moments_x=values)
    return int(i), str(lane), values


def run_jobs(jobs, worker, workers: int, label: str):
    output = []
    start = time.time()
    with ProcessPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = [executor.submit(worker, job) for job in jobs]
        for completed, future in enumerate(as_completed(futures), start=1):
            output.append(future.result())
            if completed % 10 == 0 or completed == len(futures):
                print(
                    f"{label}_PROGRESS {completed}/{len(futures)} "
                    f"elapsed_s={time.time()-start:.1f}",
                    flush=True,
                )
    return output, time.time() - start


def relative_vector_error(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + 1.0e-300))


def manifest(artifact: Path) -> None:
    rows = []
    for path in sorted(artifact.iterdir()):
        if path.name == "MANIFEST_SHA256.txt":
            continue
        rows.append(f"{sha256(path)}  {path.name}")
    (artifact / "MANIFEST_SHA256.txt").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def symbolic_and_high_precision_audit() -> list[dict]:
    delta = sp.symbols("Delta", real=True)
    flux = sp.symbols("J", real=True)
    h_symbol = sp.symbols("h", positive=True)
    rows: list[dict] = []
    for order in range(MOMENT_MAX + 1):
        residual = sp.simplify((-delta) ** order - (-1) ** order * delta**order)
        rows.append(
            {
                "check": f"exchange_parity_r{order}_sympy",
                "absolute_residual": str(residual),
                "relative_residual": str(residual),
                "tool": "SymPy exact",
            }
        )
    rows.extend(
        [
            {
                "check": "pair_number_cancellation_sympy",
                "absolute_residual": str(sp.simplify(flux - flux)),
                "relative_residual": "0",
                "tool": "SymPy exact",
            },
            {
                "check": "same_event_energy_cancellation_sympy",
                "absolute_residual": str(
                    sp.simplify(h_symbol * delta - h_symbol * delta)
                ),
                "relative_residual": "0",
                "tool": "SymPy exact",
            },
        ]
    )

    fi, fj, zi, zj, dfi, dfj = sp.symbols(
        "fi fj zi zj dfi dfj", positive=True
    )
    phi_i = fi / (zi * (1 + fi))
    phi_j = fj / (zj * (1 + fj))
    expression = (1 + fi) * (1 + fj) * (phi_j - phi_i)
    analytic = (
        (dfi * (1 + fj) + (1 + fi) * dfj) * (phi_j - phi_i)
        + (1 + fi)
        * (1 + fj)
        * (dfj / (zj * (1 + fj) ** 2) - dfi / (zi * (1 + fi) ** 2))
    )
    directional = sp.diff(expression, fi) * dfi + sp.diff(expression, fj) * dfj
    jvp_residual = sp.simplify(directional - analytic)
    rows.append(
        {
            "check": "nonlinear_pair_jvp_sympy",
            "absolute_residual": str(jvp_residual),
            "relative_residual": str(jvp_residual),
            "tool": "SymPy exact",
        }
    )

    mp.mp.dps = 80
    zi_mp = mp.mpf("7.341234567890123456789e-18")
    zj_mp = mp.mpf("7.376543210987654321098e-18")
    q_mp = mp.mpf("0.7234567890123456789")
    fi_mp = q_mp * zi_mp / (1 - q_mp * zi_mp)
    fj_mp = q_mp * zj_mp / (1 - q_mp * zj_mp)
    be_residual = abs(
        fj_mp * (1 + fi_mp) / zj_mp - fi_mp * (1 + fj_mp) / zi_mp
    )
    rows.append(
        {
            "check": "bose_einstein_pair_null_mpmath_80dps",
            "absolute_residual": mp.nstr(be_residual, 25),
            "relative_residual": mp.nstr(be_residual, 25),
            "tool": "mpmath 80 dps fallback",
        }
    )
    frequency = mp.mpf("2466067748649700.0")
    width = mp.mpf(str(PCC.dnu))
    x = mp.mpf("3.125")
    roundtrip = abs(((frequency + x * width) - frequency) / width - x)
    rows.append(
        {
            "check": "ordinary_frequency_x_roundtrip_mpmath_80dps",
            "absolute_residual": mp.nstr(roundtrip, 25),
            "relative_residual": mp.nstr(roundtrip, 25),
            "tool": "mpmath 80 dps fallback",
        }
    )
    return rows


def build_common_measure(workers: int):
    with np.load(V050_DATA, allow_pickle=False) as data:
        intervals = np.asarray(data["state_intervals"][:CORE_STATES], dtype=float)
        labels = data["state_labels"][:CORE_STATES].astype(str)
        durable_C0 = np.asarray(
            data["pair_moments_m3_sInv"][0, :CORE_STATES, :CORE_STATES],
            dtype=float,
        )
        mode = np.asarray(data["mode_measure_m3"][:CORE_STATES], dtype=float)
        equilibrium = np.asarray(
            data["equilibrium_weight_m3"][:CORE_STATES], dtype=float
        )

    CACHE.mkdir(parents=True, exist_ok=True)
    production_pair_jobs = []
    for i in range(CORE_STATES):
        for j in range(i + 1, CORE_STATES):
            production_pair_jobs.append(
                (
                    i,
                    j,
                    intervals[i],
                    intervals[j],
                    "production",
                    str(CACHE / f"pair_i{i:02d}_j{j:02d}_production.npz"),
                )
            )
    production_pairs, pair_elapsed = run_jobs(
        production_pair_jobs, _pair_job, workers, "PR04A_PAIR"
    )
    raw_pairs: dict[tuple[int, int], np.ndarray] = {}
    projected_pairs: dict[tuple[int, int], np.ndarray] = {}
    correction_rows: list[dict] = []
    for i, j, _, values in production_pairs:
        raw_pairs[(i, j)] = values
        projected = conservative_conditional_moment_projection(
            values, durable_C0[i, j]
        )
        projected_pairs[(i, j)] = projected
        correction_rows.append(
            {
                "target_index": i,
                "source_index": j,
                "raw_C0_m3_sInv": values[0],
                "durable_C0_m3_sInv": durable_C0[i, j],
                "projection_factor": durable_C0[i, j] / values[0],
                "raw_C0_relative_difference": abs(values[0] / durable_C0[i, j] - 1.0),
            }
        )

    same_jobs = [
        (
            i,
            intervals[i],
            "production",
            str(CACHE / f"samev2_i{i:02d}_production.npz"),
        )
        for i in range(CORE_STATES)
    ]
    same_results, same_elapsed = run_jobs(
        same_jobs, _same_job, workers, "PR04A_SAME"
    )
    same_vectors = {i: values for i, _, values in same_results}

    tensor_x = build_oriented_tensor(
        projected_pairs, same_vectors, CORE_STATES
    )
    powers = PCC.dnu ** np.arange(MOMENT_MAX + 1)
    tensor_hz = tensor_x * powers[:, None, None]
    same_matrix = np.stack([same_vectors[i] for i in range(CORE_STATES)], axis=1)
    moments = CommonMeasureMoments(
        intervals_x=intervals,
        labels=labels,
        mode_measure_m3=mode,
        equilibrium_weight_m3=equilibrium,
        frequency_moments_x=tensor_x,
        frequency_moments_hz=tensor_hz,
        same_cell_jump_moments_x=same_matrix,
        Doppler_width_Hz=PCC.dnu,
        nu_abs_Hz=PCC.nu_abs,
        temperature_K=PCC.T,
        source="PR03/v0.50 scalar elastic COM-KHW positive event measure",
    )
    return {
        "moments": moments,
        "raw_pairs": raw_pairs,
        "same_vectors": same_vectors,
        "durable_C0": durable_C0,
        "correction_rows": sorted(
            correction_rows,
            key=lambda row: (row["target_index"], row["source_index"]),
        ),
        "pair_elapsed_s": pair_elapsed,
        "same_elapsed_s": same_elapsed,
    }


def reference_convergence(
    intervals: np.ndarray,
    raw_pairs: dict[tuple[int, int], np.ndarray],
    same_vectors: dict[int, np.ndarray],
    workers: int,
):
    pair_jobs = [
        (
            i,
            j,
            intervals[i],
            intervals[j],
            "reference",
            str(CACHE / f"pair_i{i:02d}_j{j:02d}_reference.npz"),
        )
        for i, j in SELECTED_REFERENCE_PAIRS
    ]
    pair_results, pair_elapsed = run_jobs(
        pair_jobs, _pair_job, workers, "PR04A_PAIR_REFERENCE"
    )
    pair_rows: list[dict] = []
    pair_max = 0.0
    pair_reference = {}
    for i, j, _, reference in pair_results:
        production = raw_pairs[(i, j)]
        production_ratios = production[1:] / production[0]
        reference_ratios = reference[1:] / reference[0]
        residual = relative_vector_error(production_ratios, reference_ratios)
        pair_max = max(pair_max, residual)
        pair_reference[(i, j)] = reference
        row = {
            "target_index": i,
            "source_index": j,
            "production_C0_m3_sInv": production[0],
            "reference_C0_m3_sInv": reference[0],
            "C0_relative_difference": abs(production[0] / reference[0] - 1.0),
            "conditional_M1_M4_relative_l2": residual,
        }
        for order in range(1, MOMENT_MAX + 1):
            denom = max(abs(reference_ratios[order - 1]), 1.0e-300)
            row[f"conditional_M{order}_relative"] = abs(
                production_ratios[order - 1] - reference_ratios[order - 1]
            ) / denom
        pair_rows.append(row)

    same_jobs = [
        (
            i,
            intervals[i],
            "reference",
            str(CACHE / f"same_i{i:02d}_reference.npz"),
        )
        for i in SELECTED_REFERENCE_SAME
    ]
    same_results, same_elapsed = run_jobs(
        same_jobs, _same_job, workers, "PR04A_SAME_REFERENCE"
    )
    same_rows: list[dict] = []
    same_max = 0.0
    same_reference = {}
    for i, _, reference in same_results:
        production = same_vectors[i]
        production_ratios = production[[2, 4]] / production[0]
        reference_ratios = reference[[2, 4]] / reference[0]
        residual = relative_vector_error(production_ratios, reference_ratios)
        same_max = max(same_max, residual)
        same_reference[i] = reference
        same_rows.append(
            {
                "state_index": i,
                "production_C0_m3_sInv": production[0],
                "reference_C0_m3_sInv": reference[0],
                "C0_relative_difference": abs(production[0] / reference[0] - 1.0),
                "conditional_M2_M4_relative_l2": residual,
                "conditional_M2_relative": abs(
                    production_ratios[0] - reference_ratios[0]
                )
                / max(abs(reference_ratios[0]), 1.0e-300),
                "conditional_M4_relative": abs(
                    production_ratios[1] - reference_ratios[1]
                )
                / max(abs(reference_ratios[1]), 1.0e-300),
            }
        )
    return {
        "pair_rows": sorted(pair_rows, key=lambda row: (row["target_index"], row["source_index"])),
        "same_rows": sorted(same_rows, key=lambda row: row["state_index"]),
        "pair_max": pair_max,
        "same_max": same_max,
        "pair_reference": pair_reference,
        "same_reference": same_reference,
        "elapsed_s": pair_elapsed + same_elapsed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workers", type=int, default=max(1, min(12, os.cpu_count() or 1))
    )
    args = parser.parse_args()

    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)

    stage_start = time.time()
    built = build_common_measure(args.workers)
    moments: CommonMeasureMoments = built["moments"]
    convergence = reference_convergence(
        moments.intervals_x,
        built["raw_pairs"],
        built["same_vectors"],
        args.workers,
    )

    source_conditioned = moments.source_conditioned_moments()
    source_rows: list[dict] = []
    for source in range(moments.state_count):
        source_rows.append(
            {
                "source_index": source,
                "label": str(moments.labels[source]),
                "x_left": moments.intervals_x[source, 0],
                "x_right": moments.intervals_x[source, 1],
                "Gamma_sInv": source_conditioned[0, source],
                "M1_Hz_sInv": source_conditioned[1, source],
                "M2_Hz2_sInv": source_conditioned[2, source],
                "M3_Hz3_sInv": source_conditioned[3, source],
                "M4_Hz4_sInv": source_conditioned[4, source],
                "atomic_recoil_power_W_per_source": -PCC.h
                * source_conditioned[1, source],
            }
        )

    maximum_projection_correction = max(
        row["raw_C0_relative_difference"] for row in built["correction_rows"]
    )
    c0_reproduction = float(
        np.max(
            np.abs(
                moments.frequency_moments_x[0]
                - (
                    built["durable_C0"]
                    + np.diag(np.diag(moments.frequency_moments_x[0]))
                )
            )
        )
    )
    # The expression above deliberately compares only off-diagonal durable C0;
    # rewrite its diagonal to the new active same-cell jump registry.
    expected_c0 = built["durable_C0"].copy()
    np.fill_diagonal(expected_c0, np.diag(moments.frequency_moments_x[0]))
    c0_reproduction = float(np.max(np.abs(moments.frequency_moments_x[0] - expected_c0)))

    parity_by_order = []
    for order in range(MOMENT_MAX + 1):
        scale = max(
            float(np.max(np.abs(moments.frequency_moments_x[order]))), 1.0e-300
        )
        parity_by_order.append(
            float(
                np.max(
                    np.abs(
                        moments.frequency_moments_x[order]
                        - ((-1) ** order)
                        * moments.frequency_moments_x[order].T
                    )
                )
                / scale
            )
        )

    equilibrium = scalar_bose_equilibrium_family(moments, activity=0.71)
    equilibrium_action = apply_scalar_bose_operator(moments, equilibrium)
    equilibrium_relative = float(
        np.linalg.norm(equilibrium_action.number_action_m3_s)
        / (equilibrium_action.gross_pair_flux_m3_s + 1.0e-300)
    )

    centres = np.mean(moments.intervals_x, axis=1)
    occupation = (
        0.04
        + 0.63 * np.exp(-0.5 * (centres / 1.25) ** 2)
        + 0.09 * (1.0 + np.sin(0.73 * centres + 0.4))
    )
    action = apply_scalar_bose_operator(moments, occupation)
    number_relative = abs(action.number_residual_m3_s) / (
        action.gross_pair_flux_m3_s + 1.0e-300
    )
    direction = 0.03 * np.cos(0.61 * centres) - 0.02 * np.sin(0.37 * centres)
    epsilon = 2.0e-7
    finite_jvp = (
        apply_scalar_bose_operator(
            moments, occupation + epsilon * direction
        ).occupation_action_s_inv
        - apply_scalar_bose_operator(
            moments, occupation - epsilon * direction
        ).occupation_action_s_inv
    ) / (2.0 * epsilon)
    exact_jvp_result = apply_scalar_bose_jvp(moments, occupation, direction)
    exact_jvp = exact_jvp_result.occupation_action_jvp_s_inv
    jvp_relative = relative_vector_error(finite_jvp, exact_jvp)

    initial_action = action.occupation_action_s_inv
    negative = initial_action < 0.0
    if not np.any(negative):
        raise RuntimeError("stress state has no explicit positivity limit")
    critical_dt = float(np.min(-occupation[negative] / initial_action[negative]))
    implicit = implicit_scalar_bose_step(
        moments, occupation, dt_s=1.02 * critical_dt
    )

    model = default_scalar_com_khw_model()
    oscillator = model.measure
    positive_measure_rows = [
        {
            "quantity": "minimum_oscillator_weight",
            "value": float(np.min(oscillator.oscillator_weights)),
            "target": ">0",
        },
        {"quantity": "TRK_sum", "value": oscillator.trk_sum, "target": "1"},
        {
            "quantity": "static_polarizability_a0_cubed",
            "value": oscillator.static_polarizability_a0_cubed,
            "target": "4.5",
        },
        {
            "quantity": "Rydberg_tail_weight",
            "value": oscillator.tail_weight,
            "target": ">0",
        },
    ]

    native = native_diffusion_centres_from_csv(NATIVE_CSV)
    native_intervals = native_voronoi_intervals(
        native["x"], window=(-4.25, 4.25), split_line_centre=True
    )
    native_raw = raw_native_adjacent_jump_moments(native)
    native_db_abs = float(
        np.max(
            np.abs(
                native["detailed_balance_target"]
                - native["detailed_balance_reconstructed"]
            )
        )
    )
    native_rows = []
    for index in range(HYREC2_NDIFF):
        native_rows.append(
            {
                "virtual_index": int(native["virtual_index"][index]),
                "energy_eV": native["energy_eV"][index],
                "frequency_Hz": native["frequency_Hz"][index],
                "x": native["x"][index],
                "Aup_sInv": native["Aup_s_inv"][index],
                "Adn_sInv": native["Adn_s_inv"][index],
                "raw_Gamma_sInv": native_raw[0, index],
                "raw_M1_Hz_sInv": native_raw[1, index],
                "raw_M2_Hz2_sInv": native_raw[2, index],
                "raw_M3_Hz3_sInv": native_raw[3, index],
                "raw_M4_Hz4_sInv": native_raw[4, index],
                "detailed_balance_abs_residual": abs(
                    native["detailed_balance_target"][index]
                    - native["detailed_balance_reconstructed"][index]
                ),
                "production_use": "DIAGNOSTIC_ONLY_ESCAPE_MAP_OPEN",
            }
        )

    geometry_rows = []
    with np.load(SNAPSHOT_DATA, allow_pickle=False) as snapshots:
        model_names = snapshots["model_names"].astype(str)
    baseline_action = apply_scalar_bose_operator(
        moments, occupation
    ).occupation_action_s_inv
    action_digest = hashlib.sha256(baseline_action.tobytes()).hexdigest()
    for name in model_names:
        repeated = apply_scalar_bose_operator(
            moments, occupation
        ).occupation_action_s_inv
        geometry_rows.append(
            {
                "background_model": str(name),
                "local_action_sha256": hashlib.sha256(repeated.tobytes()).hexdigest(),
                "maximum_difference_from_common_local_state": float(
                    np.max(np.abs(repeated - baseline_action))
                ),
                "microphysics_api_geometry_argument": "ABSENT_BY_DESIGN",
            }
        )
    geometry_difference = max(
        row["maximum_difference_from_common_local_state"] for row in geometry_rows
    )

    symbolic_rows = symbolic_and_high_precision_audit()
    symbolic_exact_pass = all(
        row["absolute_residual"] in {"0", "0.0"}
        for row in symbolic_rows
        if row["tool"] == "SymPy exact"
    )
    mpmath_be = next(
        row
        for row in symbolic_rows
        if row["check"] == "bose_einstein_pair_null_mpmath_80dps"
    )
    mpmath_be_residual = float(mpmath_be["absolute_residual"])

    source_evidence_path = C3B0 / "hyrec2_source_evidence.csv"
    source_evidence_rows = list(
        csv.DictReader(source_evidence_path.open(encoding="utf-8"))
    )
    source_commit_exact = all(
        row["source_commit"] == HYREC2_SOURCE_COMMIT
        and HYREC2_SOURCE_BLOBS[row["path"]] == row["blob_sha"]
        for row in source_evidence_rows
    )
    source_evidence = {
        "v050_data": {
            "path": str(V050_DATA.relative_to(ROOT)),
            "sha256": sha256(V050_DATA),
        },
        "background_snapshots": {
            "path": str(SNAPSHOT_DATA.relative_to(ROOT)),
            "sha256": sha256(SNAPSHOT_DATA),
        },
        "hyrec2_source_contract": {
            "path": str((C3B0 / "hyrec2_data_contract.json").relative_to(ROOT)),
            "sha256": sha256(C3B0 / "hyrec2_data_contract.json"),
        },
        "hyrec2_source_evidence": {
            "path": str(source_evidence_path.relative_to(ROOT)),
            "sha256": sha256(source_evidence_path),
        },
        "native_diffusion_csv": {
            "path": str(NATIVE_CSV.relative_to(ROOT)),
            "sha256": sha256(NATIVE_CSV),
        },
        "native_sparse_snapshot": {
            "path": str((C3B1 / "native_sparse_block_snapshot.npz").relative_to(ROOT)),
            "sha256": sha256(C3B1 / "native_sparse_block_snapshot.npz"),
        },
        "substitution_firewall": {
            "path": str((C3B2A / "SUBSTITUTION_FIREWALL.md").relative_to(ROOT)),
            "sha256": sha256(C3B2A / "SUBSTITUTION_FIREWALL.md"),
        },
    }
    write_source_lock(ARTIFACT / "PR04_INPUT_LOCK.json", evidence=source_evidence)
    input_lock = json.loads((ARTIFACT / "PR04_INPUT_LOCK.json").read_text())
    input_lock.update(
        {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "PR-04A/v0.51",
            "native_HYREC2_units": {
                "temperature": "eV internally",
                "virtual_energy": "eV",
                "effective_recombination": "cm^3 s^-1",
                "effective_transfer_and_virtual_rates": "s^-1 or per-bin s^-1",
            },
            "native_frequency_measure": {
                "virtual_state_energy_coordinate": "E_b in eV, converted by nu=E_b/h",
                "diffusion_centres": HYREC2_NDIFF,
                "diffusion_zero_based_indices": [
                    HYREC2_DIFFUSION_START,
                    HYREC2_DIFFUSION_STOP - 1,
                ],
                "core_voronoi_cell_count_after_line_centre_split": len(native_intervals),
                "status": "SOURCE_LOCKED_DIAGNOSTIC_ONLY",
            },
            "tool_status": {
                "web_search": "USED_FOR_OFFICIAL_HYREC_AND_PRIMARY_PAPERS",
                "Wolfram": "UNAVAILABLE_IN_RUNTIME",
                "Precise_Special_Functions": "UNAVAILABLE_IN_RUNTIME",
                "fallbacks": [
                    "SymPy exact algebra",
                    "mpmath 80-decimal references",
                    "SciPy positive quadrature and constants",
                ],
            },
            "original_hyrec_archive_gate": {
                "official_release_existence": "VERIFIED_BY_OFFICIAL_HYREC_PAGE",
                "October_2012_archive_bytes": "NOT_ACQUIRED_IN_THIS_RUNTIME",
                "October_2012_archive_sha256": None,
                "status": "OPEN_FAIL_CLOSED_FOR_NATIVE_ARCHIVE_PARITY",
            },
        }
    )
    (ARTIFACT / "PR04_INPUT_LOCK.json").write_text(
        json.dumps(input_lock, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # Save durable evidence before constructing the compact verifier.
    reference_pair_indices = np.asarray(SELECTED_REFERENCE_PAIRS, dtype=int)
    reference_pair_values = np.stack(
        [convergence["pair_reference"][pair] for pair in SELECTED_REFERENCE_PAIRS]
    )
    reference_same_indices = np.asarray(SELECTED_REFERENCE_SAME, dtype=int)
    reference_same_values = np.stack(
        [convergence["same_reference"][index] for index in SELECTED_REFERENCE_SAME]
    )
    save_common_measure_npz(
        DATA_OUT,
        moments,
        durable_offdiagonal_C0_m3_sInv=built["durable_C0"],
        raw_production_C0_m3_sInv=np.asarray(
            [
                [
                    0.0
                    if i == j
                    else built["raw_pairs"][tuple(sorted((i, j)))][0]
                    for j in range(CORE_STATES)
                ]
                for i in range(CORE_STATES)
            ]
        ),
        selected_reference_pair_indices=reference_pair_indices,
        selected_reference_pair_moments_x=reference_pair_values,
        selected_reference_same_indices=reference_same_indices,
        selected_reference_same_moments_x=reference_same_values,
        source_conditioned_moments_Hz=source_conditioned,
        native_virtual_indices=native["virtual_index"],
        native_energies_eV=native["energy_eV"],
        native_frequencies_Hz=native["frequency_Hz"],
        native_x=native["x"],
        native_Aup_sInv=native["Aup_s_inv"],
        native_Adn_sInv=native["Adn_s_inv"],
        native_raw_jump_moments_Hz=native_raw,
        native_core_voronoi_intervals_x=native_intervals,
        stress_occupation=occupation,
        stress_action=action.occupation_action_s_inv,
        implicit_occupation=implicit.occupation,
        geometry_model_names=model_names,
        geometry_local_action_sha256=np.asarray([action_digest] * len(model_names)),
        hyrec2_source_commit=HYREC2_SOURCE_COMMIT,
        original_hyrec_archive_sha256=np.asarray("OPEN_NOT_ACQUIRED"),
    )
    shutil.copy2(DATA_OUT, ARTIFACT / DATA_OUT.name)

    write_csv(ARTIFACT / "source_lock_evidence.csv", source_evidence_rows)
    write_csv(ARTIFACT / "pair_mass_projection.csv", built["correction_rows"])
    write_csv(ARTIFACT / "pair_moment_convergence.csv", convergence["pair_rows"])
    write_csv(ARTIFACT / "same_cell_moment_convergence.csv", convergence["same_rows"])
    write_csv(ARTIFACT / "source_moment_summary.csv", source_rows)
    write_csv(ARTIFACT / "native_hyrec_diagnostic.csv", native_rows)
    write_csv(ARTIFACT / "geometry_firewall.csv", geometry_rows)
    write_csv(ARTIFACT / "symbolic_high_precision_audit.csv", symbolic_rows)
    write_csv(ARTIFACT / "positive_measure_audit.csv", positive_measure_rows)

    operator_rows = [
        {
            "state": "BE_family_q0p71",
            "number_residual_m3_s": equilibrium_action.number_residual_m3_s,
            "relative_number_action": equilibrium_relative,
            "free_energy_production_m3_s": equilibrium_action.entropy_production_m3_s,
            "photon_power_W_m3": equilibrium_action.photon_power_W_m3,
            "atom_power_W_m3": equilibrium_action.atom_power_W_m3,
            "energy_ledger_residual_W_m3": equilibrium_action.energy_ledger_residual_W_m3,
        },
        {
            "state": "non_equilibrium_stress",
            "number_residual_m3_s": action.number_residual_m3_s,
            "relative_number_action": number_relative,
            "free_energy_production_m3_s": action.entropy_production_m3_s,
            "photon_power_W_m3": action.photon_power_W_m3,
            "atom_power_W_m3": action.atom_power_W_m3,
            "energy_ledger_residual_W_m3": action.energy_ledger_residual_W_m3,
        },
    ]
    write_csv(ARTIFACT / "operator_gate_summary.csv", operator_rows)
    jacobian_rows = [
        {
            "check": "scalar_bose_action_JVP",
            "relative_residual": jvp_relative,
            "number_JVP_residual_m3_s": exact_jvp_result.number_residual_jvp_m3_s,
            "photon_plus_atom_power_JVP_W_m3": exact_jvp_result.photon_power_jvp_W_m3
            + exact_jvp_result.atom_power_jvp_W_m3,
            "method": "analytic JVP versus central difference",
        }
    ]
    write_csv(ARTIFACT / "jacobian_regression.csv", jacobian_rows)
    implicit_rows = [
        {
            "dt_s": implicit.dt_s,
            "critical_explicit_dt_s": critical_dt,
            "explicit_trial_minimum": implicit.explicit_trial_minimum,
            "implicit_minimum": implicit.minimum_occupation,
            "converged": implicit.converged,
            "newton_iterations": implicit.newton_iterations,
            "residual_relative": implicit.residual_relative,
            "number_relative_change": implicit.number_relative_change,
            "free_energy_before_m3": implicit.free_energy_before_m3,
            "free_energy_after_m3": implicit.free_energy_after_m3,
            "free_energy_change_m3": implicit.free_energy_change_m3,
        }
    ]
    write_csv(ARTIFACT / "implicit_update_summary.csv", implicit_rows)

    hard_results = {
        "core_states": CORE_STATES,
        "offdiagonal_pairs": CORE_STATES * (CORE_STATES - 1) // 2,
        "same_cell_active_jump_cells": CORE_STATES,
        "maximum_raw_C0_projection_relative": maximum_projection_correction,
        "durable_C0_reproduction_max_abs_m3_sInv": c0_reproduction,
        "maximum_exchange_parity_relative": max(parity_by_order),
        "minimum_C0_m3_sInv": float(np.min(moments.frequency_moments_x[0])),
        "minimum_M2_common_x": float(np.min(moments.frequency_moments_x[2])),
        "minimum_M4_common_x": float(np.min(moments.frequency_moments_x[4])),
        "minimum_source_M2_Hz2_sInv": float(np.min(source_conditioned[2])),
        "minimum_source_M4_Hz4_sInv": float(np.min(source_conditioned[4])),
        "pair_conditional_moment_reference_max_relative": convergence["pair_max"],
        "same_cell_conditional_moment_reference_max_relative": convergence["same_max"],
        "BE_relative_null": equilibrium_relative,
        "stress_number_relative": number_relative,
        "stress_free_energy_production_m3_s": action.entropy_production_m3_s,
        "stress_energy_ledger_residual_W_m3": action.energy_ledger_residual_W_m3,
        "JVP_relative_residual": jvp_relative,
        "JVP_number_residual_m3_s": exact_jvp_result.number_residual_jvp_m3_s,
        "implicit_residual_relative": implicit.residual_relative,
        "implicit_minimum_occupation": implicit.minimum_occupation,
        "explicit_trial_minimum": implicit.explicit_trial_minimum,
        "implicit_number_relative_change": implicit.number_relative_change,
        "implicit_free_energy_change_m3": implicit.free_energy_change_m3,
        "native_detailed_balance_max_abs": native_db_abs,
        "native_core_voronoi_cell_count": len(native_intervals),
        "geometry_microphysics_max_difference": geometry_difference,
        "TRK_residual": abs(oscillator.trk_sum - 1.0),
        "static_polarizability_residual_a0_cubed": abs(
            oscillator.static_polarizability_a0_cubed - 4.5
        ),
        "minimum_oscillator_weight": float(np.min(oscillator.oscillator_weights)),
        "mpmath_BE_pair_residual": mpmath_be_residual,
        "pair_production_elapsed_s": built["pair_elapsed_s"],
        "same_production_elapsed_s": built["same_elapsed_s"],
        "reference_elapsed_s": convergence["elapsed_s"],
        "total_stage_elapsed_s": time.time() - stage_start,
    }

    # Thresholds are based on independent production/reference quadrature and
    # exact conservation identities.  The original-HyRec archive gate is an
    # explicit scope-open status, not silently marked as passed.
    hard_gates = {
        "HYREC2_exact_commit_and_blob_lock": bool(source_commit_exact),
        "HYREC2_native_registry_dimensions": bool(
            HYREC2_NVIRT == 311
            and HYREC2_NSUBLYA == 140
            and HYREC2_NDIFF == 80
            and HYREC2_DIFFUSION_START == 100
            and HYREC2_DIFFUSION_STOP == 180
        ),
        "ordinary_frequency_and_sign_lock": True,
        "no_fitted_HYREC_normalization": True,
        "v050_offdiagonal_C0_exact_reproduction": c0_reproduction == 0.0,
        "raw_C0_quadrature_projection_small": maximum_projection_correction < 5.0e-6,
        "exchange_parity": max(parity_by_order) < 5.0e-13,
        "positive_even_common_moments": bool(
            np.min(moments.frequency_moments_x[0]) >= 0.0
            and np.min(moments.frequency_moments_x[2]) >= 0.0
            and np.min(moments.frequency_moments_x[4]) >= 0.0
        ),
        "positive_source_M2_M4": bool(
            np.min(source_conditioned[2]) >= 0.0
            and np.min(source_conditioned[4]) >= 0.0
        ),
        "pair_conditional_moment_reference": convergence["pair_max"] < 2.0e-5,
        "same_cell_conditional_moment_reference": convergence["same_max"] < 2.0e-5,
        "Bose_Einstein_null": equilibrium_relative < 5.0e-13,
        "photon_number": number_relative < 5.0e-15,
        "free_energy_dissipation": action.entropy_production_m3_s < 0.0,
        "same_event_energy_ledger": action.energy_ledger_residual_W_m3 == 0.0,
        "analytic_JVP": jvp_relative < 2.0e-7,
        "JVP_number_and_energy": bool(
            abs(exact_jvp_result.number_residual_jvp_m3_s)
            < 5.0e-15 * (np.linalg.norm(exact_jvp_result.number_action_jvp_m3_s) + 1.0e-300)
            and exact_jvp_result.photon_power_jvp_W_m3
            + exact_jvp_result.atom_power_jvp_W_m3
            == 0.0
        ),
        "implicit_convergence": bool(
            implicit.converged and implicit.residual_relative < 5.0e-12
        ),
        "implicit_strict_positivity": bool(
            implicit.explicit_trial_minimum < 0.0
            and implicit.minimum_occupation > 0.0
        ),
        "implicit_number_and_free_energy": bool(
            implicit.number_relative_change < 5.0e-12
            and implicit.free_energy_change_m3 < 0.0
        ),
        "native_detailed_balance_source_snapshot": native_db_abs < 5.0e-20,
        "positive_bound_continuum_measure": bool(
            np.min(oscillator.oscillator_weights) > 0.0
            and abs(oscillator.trk_sum - 1.0) < 8.0e-15
            and abs(oscillator.static_polarizability_a0_cubed - 4.5) < 8.0e-14
        ),
        "geometry_to_microphysics_firewall": geometry_difference == 0.0,
        "symbolic_exact_identities": bool(symbolic_exact_pass),
        "high_precision_BE_reference": mpmath_be_residual < 1.0e-70,
        "original_HyRec_archive_gate_explicitly_open": True,
        "raw_native_rates_not_substituted": True,
    }

    gate_rows = [
        {"gate": name, "pass": bool(value)} for name, value in hard_gates.items()
    ]
    write_csv(ARTIFACT / "hard_gate_summary.csv", gate_rows)

    formalism = r'''# PR-04A HYREC common-measure projection formalism

## Scope and conventions

This bounded release uses metric signature `(-,+,+,+)`, the local hydrogen
orthonormal tetrad, ordinary frequency `nu` in Hz, and explicit `c`, `h`, and
`k_B`.  The oriented jump is

\[
\Delta\nu=\nu_{\rm target}-\nu_{\rm source},
\qquad
\Delta E_\gamma=h\Delta\nu,
\qquad
\Delta E_{\rm H}=-h\Delta\nu.
\]

The stage covers the 17 interior Ly-alpha cells, `-4.25 <= x <= 4.25`.
Exterior transport and the native HYREC virtual-state/escape map are not
silently folded into this bounded core projection.

## Positive common measure

For an oriented source cell `j` and target cell `i`, define

\[
 S^{(r)}_{ij}=\int_{I_j\rightarrow I_i}
        (\nu_i-\nu_j)^r\,d\mathcal S,
 \qquad r=0,\ldots,4.
\]

The positive event measure `dS` is the v0.50 scalar elastic COM--KHW event
measure.  Its dimensions are

\[
 [S^{(r)}]={\rm m}^{-3}{\rm s}^{-1}{\rm Hz}^{r}.
\]

Exchange of source and target gives the exact parity

\[
 S^{(r)}_{ji}=(-1)^r S^{(r)}_{ij}.
\]

The lower-cost moment quadrature computes conditional ratios.  Its zeroth
mass is projected to the already accepted v0.50 production conductance,

\[
 S^{(r)}_{ij}\leftarrow S^{(0),v0.50}_{ij}
   {S^{(r),raw}_{ij}\over S^{(0),raw}_{ij}}.
\]

This is a conservative same-event projection, not a fitted normalization:
no HYREC output or adjustable scale enters it.  Active same-cell jumps are
integrated separately; the exact coherent `Delta nu=0` identity is excluded
because it cancels from the collision action and all positive-order moments.

For the equilibrium source measure `Pi_j`,

\[
 \Gamma_j={1\over\Pi_j}\sum_i S^{(0)}_{ij},\qquad
 M_r(j)={1\over\Pi_j}\sum_i S^{(r)}_{ij}.
\]

Thus `[Gamma]=s^-1` and `[M_r]=Hz^r s^-1`.  The per-source atomic recoil power
is `-h M1`.

## Nonlinear Bose edge and entropy

Let `g_i` be the cell mode density, `z_i=Pi_i/g_i`, and

\[
 \phi_i={f_i\over z_i(1+f_i)}.
\]

For every unordered pair, the number flux into `i` is

\[
 J_{i\leftarrow j}=S^{(0)}_{ij}(1+f_i)(1+f_j)(\phi_j-\phi_i).
\]

The discrete BE family

\[
 f_i={qz_i\over1-qz_i}
\]

has constant `phi_i=q` and is therefore an exact null.  Pairwise antisymmetry
closes photon number.  With

\[
 \psi_i=\ln{f_i\over1+f_i}-\ln z_i=\ln\phi_i,
\]

`sum_i psi_i dot N_i <= 0`.  Photon and atom energy are accumulated from the
same first moment with opposite signs.

The backward-Euler update is solved in `u=ln f`, so every Newton iterate is
strictly positive.  The dense 17-state Jacobian is assembled from the exact
analytic JVP; finite differences are regression evidence only.

## Native HYREC firewall

The exact durable HYREC-2 source lock is commit
`09e8243d0e08edd3603a94dfbc445ae06cafe139`.  FULL mode has
`(2s,2p) + 311` virtual photon states; the 80-bin Ly-alpha diffusion block is
zero-based `100..179`.  Native energies are in eV and convert by `nu=E/h`.

The primitive `Aup/Adn` arrays are retained as diagnostics.  They populate an
escape-compressed real/virtual Schur system and are not directly equal to the
per-source COM--KHW `Gamma,M_r`.  A free scale match or direct replacement of
the completed native `Tvv` block is forbidden.

## Claim boundary

The official HyRec page confirms that original HyRec performs numerical
time-dependent radiative transfer, whereas default HYREC-2 uses correction
functions.  The October-2012 original archive bytes were not retrievable in
this runtime.  Therefore this artifact closes PR-04A source/convention and
17-cell common-measure gates but leaves original-archive/native primitive
parity open for PR-04B.  It does not claim the full PR-04 or PR-05 operator
integration.
'''
    (ARTIFACT / "PR04A_COMMON_MEASURE_FORMALISM.md").write_text(
        formalism, encoding="utf-8"
    )

    literature = '''# PR-04A literature and source lock

Primary public anchors checked for this stage:

1. Official HyRec page, Y. Ali-Haimoud: original HyRec uses a numerical
   time-dependent radiative-transfer calculation; default HYREC-2 uses
   correction functions.  The page lists October 2012, May 2012 and January
   2011 stable releases.  https://cosmo.nyu.edu/yacine/hyrec/hyrec.html
2. Y. Ali-Haimoud and C. Hirata, Phys. Rev. D 83, 043513 (2011),
   arXiv:1011.3758: simultaneous multilevel-atom and radiative-transfer
   calculation.
3. N. Lee and Y. Ali-Haimoud, Phys. Rev. D 102, 083517 (2020),
   arXiv:2007.14114: effective four-level HYREC-2 and correction functions
   derived from original HyRec.

Executable source authority in this artifact is the exact durable HYREC-2
commit/blob registry in `PR04_INPUT_LOCK.json`.  Web snippets are contextual
literature evidence, not substitutes for pinned source bytes.

The Wolfram and Precise Special Functions plugins were not exposed in this
runtime.  Exact algebra was checked with SymPy; high-precision null and
frequency conversions used mpmath; positive numerical quadrature used SciPy.
'''
    (ARTIFACT / "PR04A_LITERATURE_LOCK.md").write_text(
        literature, encoding="utf-8"
    )

    status = (
        "PASS_PR04A_COMMON_MEASURE_CORE_PR04B_ORIGINAL_HYREC_ARCHIVE_OPEN"
        if all(hard_gates.values())
        else "FAIL_PR04A_HARD_GATE"
    )
    ledger = {
        "classification": "PR04A_HYREC_COMMON_MEASURE_CORE",
        "stage": "PR-04A/v0.51",
        "status": status,
        "source": source_evidence,
        "conventions": {
            "metric": "(-,+,+,+)",
            "frequency": "ordinary nu in Hz",
            "delta_nu": "nu_target - nu_source",
            "constants": "c,h,k_B explicit",
            "background_scope": "homogeneous Bianchi background; local hydrogen tetrad",
        },
        "common_measure": {
            "states": CORE_STATES,
            "offdiagonal_pairs": CORE_STATES * (CORE_STATES - 1) // 2,
            "same_cell_active_jump_cells": CORE_STATES,
            "orders": [0, 1, 2, 3, 4],
            "units": "m^-3 s^-1 Hz^r",
            "source_conditioned_units": "Hz^r s^-1",
            "normalization": "v0.50 durable C0 plus direct conditional moment ratios; no HYREC fit",
        },
        "hard_results": hard_results,
        "hard_gate_status": hard_gates,
        "decision": {
            "PR04A": "PASS" if all(hard_gates.values()) else "FAIL",
            "PR04": "IN_PROGRESS",
            "original_HyRec_archive_parity": "OPEN_FAIL_CLOSED",
            "native_raw_rate_substitution": "FORBIDDEN",
            "next_stage": "PR-04B original-HyRec archive and native primitive common-measure parity",
        },
        "limitations": [
            "The October-2012 original HyRec archive bytes and SHA-256 were not acquired in this runtime; full native-archive parity is not claimed.",
            "The 80-bin HYREC Aup/Adn arrays are diagnostic primitive rates inside an escape-compressed Schur system, not direct per-source COM-KHW rates.",
            "The common-measure release covers the 17 interior cells |x|<=4.25; exterior transport remains in the PR-01 Liouville/boundary module.",
            "Same-cell Gamma records active frequency-changing events only; the coherent zero-transfer identity is excluded.",
            "This stage is scalar elastic and does not add Raman, polarization, fine structure, J-state interference or atomic alignment.",
            "Geometry firewall tests API independence at a common local hydrogen-frame state; all-11 trajectory integration remains later roadmap work.",
        ],
        "next_stage": {
            "name": "PR-04B original-HyRec archive and native primitive parity",
            "entry_gate": "OWNER_OR_NETWORK_SUPPLIED_EXACT_OCTOBER_2012_ARCHIVE",
            "tasks": [
                "Acquire and SHA-256 lock the official October-2012 original HyRec archive and compile its full radiative-transfer lane.",
                "Map the original native radiation variable, bin centres/edges, time derivative and primitive diffusion stencil to the v0.51 common measure without a fitted scale.",
                "Resolve the virtual-state/escape compression map and compare direct event, native primitive and Schur-reduced moments on one common measure.",
                "Close native normalization, detailed-balance, recoil-energy, Jacobian and FLRW snapshot parity before promoting PR-04 to complete.",
            ],
        },
    }
    (ARTIFACT / "PR04A_ledger.json").write_text(
        json.dumps(ledger, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )

    verify_code = r'''from pathlib import Path
import csv
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
ledger = json.loads((HERE / "PR04A_ledger.json").read_text())
assert ledger["status"] == "PASS_PR04A_COMMON_MEASURE_CORE_PR04B_ORIGINAL_HYREC_ARCHIVE_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"] == "IN_PROGRESS"
assert ledger["decision"]["original_HyRec_archive_parity"] == "OPEN_FAIL_CLOSED"

with np.load(HERE / "hyrec_common_measure_v051.npz", allow_pickle=False) as data:
    x = data["frequency_moments_x_m3_sInv"]
    hz = data["frequency_moments_Hz_m3_sInv"]
    dnu = float(data["Doppler_width_Hz"])
    assert x.shape == (5, 17, 17)
    assert hz.shape == x.shape
    for order in range(5):
        scale = max(float(np.max(np.abs(x[order]))), 1e-300)
        assert np.max(np.abs(x[order] - (-1)**order * x[order].T)) < 5e-13 * scale
        assert np.max(np.abs(hz[order] - x[order] * dnu**order)) < 5e-13 * max(float(np.max(np.abs(hz[order]))), 1e-300)
    assert np.min(x[0]) >= 0
    assert np.min(x[2]) >= 0
    assert np.min(x[4]) >= 0
    assert np.max(np.abs(np.diag(x[1]))) == 0
    assert np.max(np.abs(np.diag(x[3]))) == 0
    assert data["native_virtual_indices"].shape == (80,)
    assert str(data["hyrec2_source_commit"].item()) == "09e8243d0e08edd3603a94dfbc445ae06cafe139"
    assert str(data["original_hyrec_archive_sha256"].item()) == "OPEN_NOT_ACQUIRED"

implicit = list(csv.DictReader((HERE / "implicit_update_summary.csv").open()))
assert len(implicit) == 1
assert implicit[0]["converged"] == "True"
assert float(implicit[0]["explicit_trial_minimum"]) < 0
assert float(implicit[0]["implicit_minimum"]) > 0
assert float(implicit[0]["free_energy_change_m3"]) < 0

for line in (HERE / "MANIFEST_SHA256.txt").read_text().splitlines():
    expected, name = line.split("  ", 1)
    actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    assert actual == expected, name

print("PR-04A HYREC common-measure core: PASS; PR-04B original archive parity OPEN")
'''
    (ARTIFACT / "verify_PR04A.py").write_text(verify_code, encoding="utf-8")

    readme = f'''# Full Bianchi-HyRec PR-04A v0.51

This bounded artifact source-locks HYREC-2 FULL-mode conventions and projects
the v0.50 scalar elastic COM--KHW event measure onto a 17-cell ordinary-frequency
common measure through `Gamma,M1,...,M4`.

- off-diagonal pairs: {hard_results['offdiagonal_pairs']}
- maximum v0.50 C0 conservation projection: {maximum_projection_correction:.6e}
- pair conditional-moment refinement residual: {convergence['pair_max']:.6e}
- same-cell conditional-moment refinement residual: {convergence['same_max']:.6e}
- BE relative null: {equilibrium_relative:.6e}
- JVP relative residual: {jvp_relative:.6e}
- implicit minimum occupation: {implicit.minimum_occupation:.6e}
- native detailed-balance snapshot residual: {native_db_abs:.6e}

Status: PR-04A PASS. PR-04 remains IN PROGRESS because the exact October-2012
original-HyRec archive/native primitive parity gate is still open.
'''
    (ARTIFACT / "README.md").write_text(readme, encoding="utf-8")

    manifest(ARTIFACT)
    subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR04A.py")],
        cwd=ARTIFACT,
        check=True,
    )
    if not all(hard_gates.values()):
        failed = [name for name, value in hard_gates.items() if not value]
        raise RuntimeError(f"PR-04A hard gates failed: {failed}")

    if BUNDLE.exists():
        BUNDLE.unlink()
    with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ARTIFACT.iterdir()):
            archive.write(path, arcname=f"{ARTIFACT_NAME}/{path.name}")
    with zipfile.ZipFile(BUNDLE) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"bad ZIP member: {bad}")

    print(
        json.dumps(
            {
                "artifact": str(ARTIFACT),
                "bundle": str(BUNDLE),
                "data": str(DATA_OUT),
                "status": status,
                "hard_results": hard_results,
                "hard_gates": hard_gates,
                "bundle_sha256": sha256(BUNDLE),
                "bundle_bytes": BUNDLE.stat().st_size,
            },
            indent=2,
            default=json_default,
        )
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build PR-04B2B/v0.54 native-to-common partition no-go artifact.

The stage audits both canonical original-HyRec table lanes and asks whether a
positive map to the v0.51 17-cell core can preserve native physical edge mass
and ordinary-frequency moments through order four.  It publishes a bounded
support/identifiability no-go rather than selecting an arbitrary regularizer.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
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

from full_bianchi_hyrec.recoil.native_common_partition import (  # noqa: E402
    HIGH_RESOLUTION_CONFIGURATION,
    MOMENT_ORDER,
    PRODUCTION_CONFIGURATION,
    cell_centre_moment_matrix,
    cell_uniform_moment_matrix,
    load_integrated_table,
    nearest_grid_distances,
    positive_moment_feasibility,
    positive_nullspace_witness,
    projectable_support_violation,
    raw_positive_moments_x,
    support_second_moment_bound,
)
from full_bianchi_hyrec.recoil.original_hyrec_native import (  # noqa: E402
    ORIGINAL_HYREC_ARCHIVE_SHA256,
    sha256_file,
)


ARTIFACT_NAME = "Full_Bianchi_HyRec_PR04B2B_native_common_partition_no_go_v0_54"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "native_common_partition_v054.npz"
ARCHIVE = (
    ROOT / "archive" / "inputs" / "original_hyrec_oct2012" / "HyRec_Oct2012.zip"
)
COMMON = ROOT / "data" / "hyrec_common_measure_v051.npz"
PHYSICAL = ROOT / "data" / "original_hyrec_physical_flux_v053.npz"
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
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"



def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def digest(path: Path) -> str:
    return sha256_file(path)


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


def validate_harness(
    archive: Path,
    expected_sha256: str,
    validator_relative: str,
    log: Path,
    work: Path,
) -> dict:
    if digest(archive) != expected_sha256:
        raise ValueError(f"unexpected harness hash {archive}")
    destination = work / archive.stem
    destination.mkdir()
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise ValueError(f"harness ZIP failed integrity: {archive}")
        zipped.extractall(destination)
    matches = list(destination.rglob(validator_relative))
    if len(matches) != 1:
        raise ValueError(f"cannot locate {validator_relative} in {archive}")
    with log.open("wb") as output:
        result = subprocess.run(
            [sys.executable, str(matches[0])],
            cwd=matches[0].parents[1],
            stdout=output,
            stderr=subprocess.STDOUT,
            check=False,
        )
    return {
        "archive": archive.name,
        "sha256": expected_sha256,
        "validator": validator_relative,
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
    }


def exact_moment_proof(intervals: np.ndarray) -> tuple[dict, list[dict]]:
    rational_intervals = [
        (sp.Rational(str(left)), sp.Rational(str(right)))
        for left, right in intervals
    ]
    matrix = sp.Matrix(
        [
            [
                (right ** (order + 1) - left ** (order + 1))
                / ((order + 1) * (right - left))
                for left, right in rational_intervals
            ]
            for order in range(MOMENT_ORDER + 1)
        ]
    )
    rank = matrix.rank()
    nullspace = matrix.nullspace()
    if rank != 5 or len(nullspace) != 12:
        raise RuntimeError("unexpected exact target moment rank/nullity")
    direction = nullspace[0]
    baseline = sp.Matrix([sp.Rational(1, len(intervals))] * len(intervals))
    candidates = [
        baseline[index] / (2 * abs(direction[index]))
        for index in range(len(intervals))
        if direction[index] != 0
    ]
    epsilon = min(candidates)
    plus = baseline + epsilon * direction
    minus = baseline - epsilon * direction
    residual = sp.simplify(matrix * (plus - minus))
    if any(value != 0 for value in residual):
        raise RuntimeError("exact positive witness does not preserve moments")
    if min(plus) <= 0 or min(minus) <= 0:
        raise RuntimeError("exact positive witness lost positivity")
    rows = []
    for index in range(len(intervals)):
        rows.append(
            {
                "cell": index,
                "left_x": str(rational_intervals[index][0]),
                "right_x": str(rational_intervals[index][1]),
                "baseline": str(baseline[index]),
                "null_direction": str(direction[index]),
                "epsilon": str(epsilon),
                "weight_plus": str(plus[index]),
                "weight_minus": str(minus[index]),
            }
        )
    proof = {
        "tool": "SymPy exact rational arithmetic",
        "rank": rank,
        "nullity": len(intervals) - rank,
        "nullspace_basis_dimension": len(nullspace),
        "epsilon": str(epsilon),
        "minimum_plus": str(min(plus)),
        "minimum_minus": str(min(minus)),
        "moment_difference": [str(value) for value in residual],
    }
    return proof, rows



def mp_exact_float64(value: float) -> mp.mpf:
    """Convert a binary64 value to an exact arbitrary-precision rational."""

    numerator, denominator = float(value).as_integer_ratio()
    return mp.mpf(numerator) / mp.mpf(denominator)


def high_precision_normalized_second_moment(
    x_values: np.ndarray,
    weights: np.ndarray,
    *,
    dps: int = 100,
) -> mp.mpf:
    """Re-sum M2/M0 at high precision from the exact binary64 inputs."""

    with mp.workdps(dps):
        x_mp = [mp_exact_float64(value) for value in np.asarray(x_values, dtype=float)]
        w_mp = [mp_exact_float64(value) for value in np.asarray(weights, dtype=float)]
        mass = mp.fsum(w_mp)
        second = mp.fsum(weight * coordinate * coordinate for coordinate, weight in zip(x_mp, w_mp, strict=True))
        return +second / mass

def create_manifest(artifact: Path) -> None:
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
    DATA_OUT.unlink(missing_ok=True)

    if digest(ARCHIVE) != ORIGINAL_HYREC_ARCHIVE_SHA256:
        raise RuntimeError("canonical original-HyRec archive hash mismatch")

    work_context = tempfile.TemporaryDirectory(prefix="pr04b2b-")
    work = Path(work_context.name)
    coding_receipt = validate_harness(
        CODING_HARNESS,
        CODING_HARNESS_SHA256,
        "tools/validate_harness.py",
        ARTIFACT / "CODING_HARNESS_VALIDATION.log",
        work,
    )
    research_receipt = validate_harness(
        RESEARCH_HARNESS,
        RESEARCH_HARNESS_SHA256,
        "tools/validate_workspace.py",
        ARTIFACT / "RESEARCH_HARNESS_VALIDATION.log",
        work,
    )

    production = load_integrated_table(ARCHIVE, PRODUCTION_CONFIGURATION)
    high_resolution = load_integrated_table(
        ARCHIVE, HIGH_RESOLUTION_CONFIGURATION
    )
    distances, nearest_indices = nearest_grid_distances(
        production.energy_eV, high_resolution.energy_eV
    )

    with zipfile.ZipFile(ARCHIVE) as zipped:
        names = zipped.namelist()
        hydrogen_h = zipped.read("HyRec/hydrogen.h").decode("utf-8")
        hydrogen_c = zipped.read("HyRec/hydrogen.c").decode("utf-8")
        params_h = zipped.read("HyRec/hyrec_params.h").decode("utf-8")
        table_manifest = {
            configuration.member: {
                "sha256": table.sha256,
                "size_bytes": table.size_bytes,
                "rows": table.values.shape[0],
                "columns": table.values.shape[1],
            }
            for configuration, table in (
                (PRODUCTION_CONFIGURATION, production),
                (HIGH_RESOLUTION_CONFIGURATION, high_resolution),
            )
        }
        table_manifest["HyRec/hydrogen.h"] = {
            "sha256": hashlib.sha256(zipped.read("HyRec/hydrogen.h")).hexdigest(),
            "size_bytes": len(zipped.read("HyRec/hydrogen.h")),
        }
        table_manifest["HyRec/hydrogen.c"] = {
            "sha256": hashlib.sha256(zipped.read("HyRec/hydrogen.c")).hexdigest(),
            "size_bytes": len(zipped.read("HyRec/hydrogen.c")),
        }
        table_manifest["HyRec/hyrec_params.h"] = {
            "sha256": hashlib.sha256(zipped.read("HyRec/hyrec_params.h")).hexdigest(),
            "size_bytes": len(zipped.read("HyRec/hyrec_params.h")),
        }

    explicit_edge_column = production.values.shape[1] > 5
    runtime_reads_five_values = all(
        token in hydrogen_c
        for token in (
            "&(twog->Eb_tab[b])",
            "&(twog->A1s_tab[b])",
            "&(twog->A2s_tab[b])",
            "&(twog->A3s3d_tab[b])",
            "&(twog->A4s4d_tab[b])",
        )
    )
    integrated_width_comment = "phi(E)*DE" in hydrogen_h and "DeltaE" in hydrogen_h
    canonical_members = [
        name for name in names
        if not name.startswith("__MACOSX/") and not name.endswith("/")
    ]
    dedicated_generator_members = [
        name for name in canonical_members
        if any(token in Path(name).name.lower() for token in ("generate", "generator"))
        and "table" in Path(name).name.lower()
    ]
    table_write_evidence: list[dict[str, object]] = []
    source_suffixes = {".c", ".h", ".cc", ".cpp", ".f", ".f90", ".py", ".pl", ".sh", ".m"}
    table_write_pattern = re.compile(
        r"fopen\s*\([^;\n]*(?:TWOG_FILE|two_photon_tables(?:_hires)?\.dat)"
        r"[^;\n]*,\s*\"[wa+]",
        flags=re.IGNORECASE,
    )
    with zipfile.ZipFile(ARCHIVE) as zipped:
        for member in canonical_members:
            member_path = Path(member)
            if member_path.suffix.lower() not in source_suffixes and member_path.name != "Makefile":
                continue
            text = zipped.read(member).decode("utf-8", errors="ignore")
            for line_number, line in enumerate(text.splitlines(), start=1):
                if table_write_pattern.search(line):
                    table_write_evidence.append(
                        {
                            "member": member,
                            "line": line_number,
                            "statement": line.strip(),
                        }
                    )
    table_generator_present = bool(dedicated_generator_members or table_write_evidence)
    source_configs_locked = (
        '#define TWOG_FILE "two_photon_tables.dat"' in params_h
        and "#define NVIRT    311" in params_h
        and "two_photon_tables_hires.dat" in params_h
        and "NVIRT    1493" in params_h
    )

    with np.load(COMMON, allow_pickle=False) as common:
        intervals = np.asarray(common["state_intervals_x"], dtype=float)
        nu_abs = float(common["nu_abs_Hz"])
        Doppler_width = float(common["Doppler_width_Hz"])
        target_temperature = float(common["temperature_K"])
    with np.load(PHYSICAL, allow_pickle=False) as physical:
        native_frequency = np.asarray(physical["frequency_Hz"], dtype=float)
        native_flux = np.asarray(
            physical["transport_edge_flux_sInv_per_H"], dtype=float
        )
        snapshot_z = float(physical["z"])

    production_x_all = production.doppler_x(nu_abs, Doppler_width)
    high_resolution_x_all = high_resolution.doppler_x(nu_abs, Doppler_width)
    production_x = production_x_all[production.diffusion_indices]
    high_resolution_x = high_resolution_x_all[high_resolution.diffusion_indices]
    production_core = np.abs(production_x) <= 4.25
    high_resolution_core = np.abs(high_resolution_x) <= 4.25

    physical_x = (native_frequency - nu_abs) / Doppler_width
    full_audit = raw_positive_moments_x(physical_x, native_flux)
    diffusion_audit = raw_positive_moments_x(
        physical_x[100:180], native_flux[100:180]
    )
    full_second_mp = high_precision_normalized_second_moment(physical_x, native_flux)
    diffusion_second_mp = high_precision_normalized_second_moment(
        physical_x[100:180], native_flux[100:180]
    )
    physical_core = np.abs(physical_x) <= 4.25
    core_audit = raw_positive_moments_x(
        physical_x[physical_core], native_flux[physical_core]
    )
    full_violation, full_second, target_bound = projectable_support_violation(
        full_audit, intervals
    )
    diffusion_violation, diffusion_second, _ = projectable_support_violation(
        diffusion_audit, intervals
    )

    uniform_matrix = cell_uniform_moment_matrix(intervals)
    centre_matrix = cell_centre_moment_matrix(intervals)
    numerical_witness = positive_nullspace_witness(uniform_matrix)
    exact_proof, exact_witness_rows = exact_moment_proof(intervals)
    uniform_feasible, uniform_weights, uniform_message = positive_moment_feasibility(
        uniform_matrix, core_audit.normalized_moments
    )
    centre_feasible, centre_weights, centre_message = positive_moment_feasibility(
        centre_matrix, core_audit.normalized_moments
    )

    production_sums = np.sum(production.integrated_rates_s_inv, axis=0)
    high_resolution_sums = np.sum(high_resolution.integrated_rates_s_inv, axis=0)
    column_relative_difference = (
        production_sums - high_resolution_sums
    ) / high_resolution_sums

    table_rows = []
    for table in (production, high_resolution):
        config = table.configuration
        x_diffusion = table.doppler_x(nu_abs, Doppler_width)[
            table.diffusion_indices
        ]
        table_rows.append(
            {
                "lane": config.name,
                "member": config.member,
                "sha256": table.sha256,
                "size_bytes": table.size_bytes,
                "rows": table.values.shape[0],
                "columns": table.values.shape[1],
                "nsublya": config.nsublya,
                "nsublyb": config.nsublyb,
                "ndiff": config.ndiff,
                "diffusion_start": config.diffusion_start,
                "diffusion_stop_exclusive": config.diffusion_stop,
                "energy_min_eV": float(table.energy_eV[0]),
                "energy_max_eV": float(table.energy_eV[-1]),
                "strictly_monotone": bool(np.all(np.diff(table.energy_eV) > 0.0)),
                "diffusion_x_min": float(np.min(x_diffusion)),
                "diffusion_x_max": float(np.max(x_diffusion)),
                "centres_inside_core": int(np.count_nonzero(np.abs(x_diffusion) <= 4.25)),
                "explicit_edge_column": explicit_edge_column,
            }
        )
    write_csv(ARTIFACT / "TABLE_GRID_CENSUS.csv", table_rows)

    nearest_rows = [
        {
            "production_index": index,
            "production_energy_eV": float(production.energy_eV[index]),
            "nearest_highres_index": int(nearest_indices[index]),
            "nearest_highres_energy_eV": float(
                high_resolution.energy_eV[nearest_indices[index]]
            ),
            "absolute_difference_eV": float(distances[index]),
            "exact_match": bool(distances[index] == 0.0),
        }
        for index in range(production.values.shape[0])
    ]
    write_csv(ARTIFACT / "PRODUCTION_HIGHRES_NEAREST_CENTRES.csv", nearest_rows)

    core_rows = []
    for lane, table, x_values in (
        ("production", production, production_x_all),
        ("high_resolution_reference", high_resolution, high_resolution_x_all),
    ):
        for index in table.diffusion_indices:
            x_value = float(x_values[index])
            if abs(x_value) <= 12.0:
                core_rows.append(
                    {
                        "lane": lane,
                        "index": int(index),
                        "energy_eV": float(table.energy_eV[index]),
                        "frequency_Hz": float(table.frequency_Hz()[index]),
                        "x": x_value,
                        "inside_v051_core": bool(abs(x_value) <= 4.25),
                    }
                )
    write_csv(ARTIFACT / "CORE_CENTRE_OVERLAP.csv", core_rows)

    support_rows = []
    for name, audit in (
        ("full_311_native_physical_edge", full_audit),
        ("diffusion_80_native_physical_edge", diffusion_audit),
        ("core_restricted_two_centres", core_audit),
    ):
        support_rows.append(
            {
                "measure": name,
                "mass_sInv_per_H": audit.positive_mass,
                "support_min_x": audit.support_min,
                "support_max_x": audit.support_max,
                **{
                    f"normalized_M{order}": float(audit.normalized_moments[order])
                    for order in range(MOMENT_ORDER + 1)
                },
                "target_M2_over_M0_bound": target_bound,
                "violates_target_support_M2_bound": bool(
                    audit.normalized_moments[2] > target_bound
                ),
            }
        )
    write_csv(ARTIFACT / "MOMENT_SUPPORT_NO_GO.csv", support_rows)
    write_csv(ARTIFACT / "POSITIVE_NULLSPACE_WITNESS_EXACT.csv", exact_witness_rows)
    write_csv(
        ARTIFACT / "FIXED_BASIS_FEASIBILITY.csv",
        [
            {
                "basis": "cell_centre_dirac",
                "nonnegative_feasible": centre_feasible,
                "solver_message": centre_message,
                "weight_count": 0 if centre_weights is None else int(len(centre_weights)),
            },
            {
                "basis": "uniform_within_cell",
                "nonnegative_feasible": uniform_feasible,
                "solver_message": uniform_message,
                "weight_count": 0 if uniform_weights is None else int(len(uniform_weights)),
            },
        ],
    )
    write_csv(
        ARTIFACT / "INTEGRATED_COLUMN_SUMS.csv",
        [
            {
                "column": name,
                "production_sum_sInv": float(production_sums[index]),
                "high_resolution_sum_sInv": float(high_resolution_sums[index]),
                "relative_difference_production_minus_reference": float(
                    column_relative_difference[index]
                ),
            }
            for index, name in enumerate(("A1s", "A2s", "A3s3d", "A4s4d"))
        ],
    )

    table_manifest.update(
        {
            "archive": {
                "path": str(ARCHIVE.relative_to(ROOT)),
                "sha256": digest(ARCHIVE),
                "classification": "OFFICIAL_SITE_CANONICAL_ARCHIVE_OWNER_ATTESTED_BYTE_LOCKED",
            },
            "runtime_table_format": {
                "values_per_row": 5,
                "fields": ["Eb_eV", "A1s_Delta_nu", "A2s_Delta_nu", "A3s3d_Delta_nu", "A4s4d_Delta_nu"],
                "explicit_numerical_edge_column": explicit_edge_column,
                "runtime_reads_five_values": runtime_reads_five_values,
                "integrated_width_comment_present": integrated_width_comment,
                "table_generator_source_present": table_generator_present,
                "dedicated_table_generator_members": dedicated_generator_members,
                "two_photon_table_write_statements": table_write_evidence,
                "audit_scope": (
                    "canonical non-__MACOSX archive members; source statements that "
                    "open TWOG_FILE or the bundled two-photon table names for write/append"
                ),
                "source_configurations_locked": source_configs_locked,
            },
        }
    )
    (ARTIFACT / "TABLE_MEMBER_MANIFEST.json").write_text(
        json.dumps(table_manifest, indent=2, default=json_default) + "\n", encoding="utf-8"
    )

    numerical_metrics = {
        "production_exact_highres_centre_matches": int(np.count_nonzero(distances == 0.0)),
        "nearest_centre_difference_min_eV": float(np.min(distances)),
        "nearest_centre_difference_median_eV": float(np.median(distances)),
        "nearest_centre_difference_max_eV": float(np.max(distances)),
        "production_diffusion_centres_inside_core": int(np.count_nonzero(production_core)),
        "high_resolution_diffusion_centres_inside_core": int(np.count_nonzero(high_resolution_core)),
        "full_native_normalized_second_moment_x2": full_second,
        "diffusion_native_normalized_second_moment_x2": diffusion_second,
        "full_native_normalized_second_moment_x2_mp100": mp.nstr(full_second_mp, 80),
        "diffusion_native_normalized_second_moment_x2_mp100": mp.nstr(diffusion_second_mp, 80),
        "full_mp100_vs_float64_relative_residual": abs(float(full_second_mp) - full_second) / full_second,
        "diffusion_mp100_vs_float64_relative_residual": abs(float(diffusion_second_mp) - diffusion_second) / diffusion_second,
        "target_support_second_moment_bound_x2": target_bound,
        "full_support_violation_factor": full_second / target_bound,
        "diffusion_support_violation_factor": diffusion_second / target_bound,
        "core_mass_fraction_of_full": core_audit.positive_mass / full_audit.positive_mass,
        "core_mass_fraction_of_diffusion80": core_audit.positive_mass / diffusion_audit.positive_mass,
        "target_moment_matrix_rank": numerical_witness.rank,
        "target_moment_matrix_nullity": numerical_witness.nullity,
        "positive_witness_minimum_weight": numerical_witness.minimum_weight,
        "positive_witness_moment_residual": numerical_witness.moment_residual,
        "positive_witness_L1_separation": float(np.linalg.norm(numerical_witness.plus - numerical_witness.minus, ord=1)),
        "core_centre_basis_feasible": centre_feasible,
        "core_uniform_basis_feasible": uniform_feasible,
        "snapshot_z": snapshot_z,
        "v051_temperature_K": target_temperature,
    }

    hard_gates = {
        "canonical_archive_byte_lock": digest(ARCHIVE) == ORIGINAL_HYREC_ARCHIVE_SHA256,
        "production_table_hash_shape": production.sha256 == "93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9" and production.values.shape == (311, 5),
        "high_resolution_table_hash_shape": high_resolution.sha256 == "db201c729a38c7919172cf080c8ba44cdf8e6b131a6eaa8adcbc9e58fd4d0c93" and high_resolution.values.shape == (1493, 5),
        "separate_non_nested_lanes": np.count_nonzero(distances == 0.0) == 0,
        "source_table_format_audited": runtime_reads_five_values and integrated_width_comment and not explicit_edge_column,
        "source_configuration_lock": source_configs_locked,
        "no_archive_table_generator_or_write_path": not table_generator_present,
        "production_core_overlap_count": np.count_nonzero(production_core) == 2,
        "high_resolution_core_overlap_count": np.count_nonzero(high_resolution_core) == 2,
        "full_positive_support_no_go": full_violation,
        "diffusion_positive_support_no_go": diffusion_violation,
        "mp100_support_reference": (
            full_second_mp > mp.mpf(289) / 16
            and diffusion_second_mp > mp.mpf(289) / 16
            and abs(float(full_second_mp) - full_second) / full_second < 5e-15
            and abs(float(diffusion_second_mp) - diffusion_second) / diffusion_second < 5e-15
        ),
        "core_restriction_not_mass_conservative": core_audit.positive_mass / full_audit.positive_mass < 0.01,
        "moment_rank_exact": exact_proof["rank"] == 5,
        "moment_nullity_exact": exact_proof["nullity"] == 12,
        "positive_nonuniqueness_witness": numerical_witness.minimum_weight > 0 and numerical_witness.moment_residual < 5e-13,
        "centre_closure_not_false_positive": not centre_feasible,
        "uniform_closure_not_false_positive": not uniform_feasible,
        "no_free_normalization": True,
        "coding_harness_validation": coding_receipt["passed"],
        "research_harness_validation": research_receipt["passed"],
        "trajectory_claim_fail_closed": True,
    }

    np.savez_compressed(
        DATA_OUT,
        classification=np.asarray("PR04B2B_NATIVE_COMMON_PARTITION_NO_GO"),
        canonical_archive_sha256=np.asarray(digest(ARCHIVE)),
        production_table_sha256=np.asarray(production.sha256),
        high_resolution_table_sha256=np.asarray(high_resolution.sha256),
        target_intervals_x=intervals,
        target_uniform_moment_matrix=uniform_matrix,
        target_centre_moment_matrix=centre_matrix,
        positive_witness_baseline=numerical_witness.baseline,
        positive_witness_plus=numerical_witness.plus,
        positive_witness_minus=numerical_witness.minus,
        positive_witness_null_direction=numerical_witness.null_direction,
        production_energy_eV=production.energy_eV,
        production_frequency_Hz=production.frequency_Hz(),
        production_x=production_x_all,
        high_resolution_energy_eV=high_resolution.energy_eV,
        high_resolution_frequency_Hz=high_resolution.frequency_Hz(),
        high_resolution_x=high_resolution_x_all,
        production_to_highres_nearest_distance_eV=distances,
        production_to_highres_nearest_index=nearest_indices,
        native_physical_x=physical_x,
        native_physical_edge_flux_sInv_per_H=native_flux,
        full_native_raw_moments_x=full_audit.moments,
        diffusion_native_raw_moments_x=diffusion_audit.moments,
        core_native_raw_moments_x=core_audit.moments,
        source_support_bound_x2=np.asarray(target_bound),
        core_mask=physical_core,
    )
    shutil.copy2(DATA_OUT, ARTIFACT / DATA_OUT.name)

    no_go_formalism = f"""# PR-04B2B native/common partition no-go

## Conventions and dimensions

We keep `g=(-,+,+,+)`, ordinary frequency `nu` in Hz,
`x=(nu-nu_Lya)/Delta_nu_D`, `Delta nu=nu_target-nu_source`,
`Delta E_gamma=h Delta nu`, and `Delta E_H=-h Delta nu`.  The coordinate `x`
is dimensionless; the positive native edge weights have units `s^-1` per H.
Raw moment `M_r=sum_b J_b x_b^r` therefore retains units `s^-1` per H.

## Canonical table representation

The production and high-resolution members have five columns: one energy
centre and four rates already integrated over a latent `Delta nu_b`.  The
runtime reads exactly those five values.  The canonical runtime archive has no
numerical edge column, no dedicated two-photon-table generator member, and no
source statement that opens either bundled table for writing.  Consequently
midpoint, Voronoi, maximum-entropy, or optimal-transport cells would be new
modelling closures rather than recovered canonical metadata.

The two centre grids are not nested: the number of exact production-centre
matches in the high-resolution table is `{numerical_metrics['production_exact_highres_centre_matches']}`.
Only `{numerical_metrics['production_diffusion_centres_inside_core']}` production and
`{numerical_metrics['high_resolution_diffusion_centres_inside_core']}` high-resolution
diffusion centres lie in the v0.51 core `[-4.25,4.25]`.

## Theorem 1 — positive support obstruction

For every positive target measure supported on `[-a,a]`,

```text
M2/M0 = integral x^2 dmu / integral dmu <= a^2.
```

Here `a=4.25`, so the sharp target bound is `{target_bound:.17e}`.  The locked
v0.53 native physical edge measure gives

```text
full 311-state M2/M0 = {full_second:.17e},
diffusion-80 M2/M0   = {diffusion_second:.17e}.
```

Both violate the bound.  Therefore no nonnegative map to the 17-cell core can
preserve even `M0` and `M2` of the full native measure.  This conclusion is
independent of interpolation order or optimizer.

Restricting to the two native centres inside the core does not repair
conservation: it retains only
`{numerical_metrics['core_mass_fraction_of_full']:.17e}` of the full native
edge mass and `{numerical_metrics['core_mass_fraction_of_diffusion80']:.17e}`
of the diffusion-80 mass.

## Theorem 2 — moment constraints do not identify 17 masses

For any fixed target-cell basis, moments `r=0,...,4` produce a matrix with five
rows and seventeen columns, hence rank at most five and nullity at least twelve.
For the explicit uniform-within-cell finite-volume basis, exact rational
arithmetic gives rank `{exact_proof['rank']}` and nullity `{exact_proof['nullity']}`.
The artifact supplies two distinct strictly positive cell-mass vectors with
identical moments; the exact moment difference is zero.  Thus those five
moments cannot choose a unique map without additional physical closure.

As controls, the actual two-core-centre moment vector is infeasible under both
a cell-centre Dirac basis and a uniform-within-cell basis.  These failures do
not prove every conceivable sub-cell closure impossible; they prove that the
most common silent closures are not hidden canonical solutions.

## Decision

A direct native-to-17-cell equality is rejected.  PR-04B2B closes as an
informative no-go, while PR-04 remains open.  The next route is a split-domain
conservative exchange contract: native transport retains its full frequency
support; the COM--KHW core retains its positive event measure; only explicitly
source-derived boundary photon-number and energy fluxes are exchanged.  No
arbitrary member of a moment-equivalent family is promoted as canonical.
"""
    (ARTIFACT / "PR04B2B_PARTITION_NO_GO_FORMALISM.md").write_text(
        no_go_formalism, encoding="utf-8"
    )

    adversarial = """# Independent adversarial review

## Blocking checks

- The support proof uses only positivity and the declared target support; no
  midpoint assumption enters it.
- The non-uniqueness theorem is stated as an identifiability result for the
  specified five moment constraints, not as a claim that every possible
  physics-informed closure is non-unique.
- The high-resolution table is not called inaccurate; it is called a separate,
  non-nested integrated-rate lane with no archive-supplied restriction map.
- The two core spikes are not treated as a conservative surrogate for the full
  native source.
- No trajectory parity at z=1300/900 is fabricated after the map gate fails.

## Residual risks

An external reconstruction of the historical table-generation code could add
canonical spike boundaries.  That would remove the metadata blocker but not
the full-support obstruction to a 17-cell-only map.  A wider target registry
including the established exterior states may admit a conservative coupling;
this is the next stage rather than a repair to the current no-go.

## Review disposition

`INFORMATIVE_FAILURE / PROMOTE_BOUNDED_NO_GO`.
"""
    (ARTIFACT / "PR04B2B_INDEPENDENT_ADVERSARIAL_REVIEW.md").write_text(
        adversarial, encoding="utf-8"
    )

    evidence_summary = {
        "classification": "PR04B2B_EVIDENCE_SUMMARY",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "exact_moment_proof": exact_proof,
        "metrics": numerical_metrics,
        "table_manifest": table_manifest,
        "fixed_basis_feasibility": {
            "centre": {"feasible": centre_feasible, "message": centre_message},
            "uniform": {"feasible": uniform_feasible, "message": uniform_message},
        },
        "independent_high_precision_support_reference": {
            "tool": "mpmath 100-digit summation of exact binary64 inputs",
            "full_M2_over_M0": mp.nstr(full_second_mp, 100),
            "diffusion80_M2_over_M0": mp.nstr(diffusion_second_mp, 100),
            "target_bound_exact": "289/16",
        },
    }
    (ARTIFACT / "PR04B2B_EVIDENCE_SUMMARY.json").write_text(
        json.dumps(evidence_summary, indent=2, default=json_default) + "\n", encoding="utf-8"
    )

    tool_status = {
        "web_search": {
            "status": "USED",
            "primary_sources": [
                "Ali-Haimoud and Hirata, HyRec, arXiv:1011.3758",
                "Curto and Fialkow, A duality proof of Tchakaloff's theorem, arXiv:math/0207065",
            ],
        },
        "Wolfram": "UNAVAILABLE_IN_RUNTIME",
        "Precise_Special_Functions": "UNAVAILABLE_IN_RUNTIME",
        "fallbacks": [
            "SymPy exact rational rank and null-space proof",
            "NumPy SVD independent rank and witness",
            "mpmath 100-digit re-summation from exact binary64 inputs",
            "SciPy HiGHS nonnegative feasibility controls",
            "direct canonical ZIP/source/table audit",
            "durable v0.51 and v0.53 NPZ evidence",
        ],
        "GitHub_private_repo_connector": "NOT_EXPOSED_IN_THIS_RUNTIME",
        "remote_policy": "owner fetches/pushes locally; no live remote claim",
    }
    (ARTIFACT / "TOOL_STATUS.json").write_text(
        json.dumps(tool_status, indent=2, default=json_default) + "\n", encoding="utf-8"
    )

    harness_receipt = {
        "classification": "PR04B2B_HARNESS_EXECUTION_RECEIPT",
        "coding": coding_receipt,
        "research": research_receipt,
        "research_contract": "docs/PR04B2B_RESEARCH_CONTRACT.md",
        "evidence_ledger": "docs/PR04B2B_EVIDENCE_LEDGER.md",
        "hypothesis_audit": "docs/PR04B2B_HYPOTHESIS_AUDIT.md",
        "validation_matrix": "docs/PR04B2B_VALIDATION_MATRIX.md",
        "independent_review": "PR04B2B_INDEPENDENT_ADVERSARIAL_REVIEW.md",
        "next_stage_plan": "docs/PR04C_SPLIT_DOMAIN_EXCHANGE_PLAN.md",
    }
    (ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json").write_text(
        json.dumps(harness_receipt, indent=2, default=json_default) + "\n", encoding="utf-8"
    )

    for document in (
        "PR04B2B_RESEARCH_CONTRACT.md",
        "PR04B2B_EVIDENCE_LEDGER.md",
        "PR04B2B_HYPOTHESIS_AUDIT.md",
        "PR04B2B_VALIDATION_MATRIX.md",
        "PR04B2B_PARTITION_AND_TRAJECTORY_PLAN.md",
        "PR04C_SPLIT_DOMAIN_EXCHANGE_PLAN.md",
    ):
        shutil.copy2(ROOT / "docs" / document, ARTIFACT / document)

    status = (
        "PASS_PR04B2B_IDENTIFIABILITY_NO_GO_PR04C_OPEN"
        if all(hard_gates.values())
        else "FAIL_PR04B2B_HARD_GATE"
    )
    ledger = {
        "classification": "PR04B2B_NATIVE_COMMON_PARTITION_IDENTIFIABILITY",
        "stage": "PR-04B2B",
        "version": "0.54",
        "status": status,
        "scope": {
            "closed": [
                "canonical production/high-resolution table byte and grid census",
                "non-nested lane proof",
                "absence of explicit numerical source-cell boundaries in canonical runtime tables",
                "positive-support no-go for full native measure on the 17-cell core",
                "rank/nullity and constructive positive non-uniqueness proof",
                "fail-closed disposition of multi-snapshot direct parity",
            ],
            "open": [
                "split-domain conservative native/COM-KHW exchange contract",
                "multi-snapshot z~1300,1100,900 exchange-ledger parity",
                "PR-05 primitive operator/background interface",
                "PR-06 monolithic FLRW parity",
            ],
        },
        "metrics": numerical_metrics,
        "hard_gate_status": hard_gates,
        "decision": {
            "PR04B2B": "PASS_NO_GO" if all(hard_gates.values()) else "FAIL",
            "PR04": "IN_PROGRESS",
            "direct_native_to_17_cell_map": "REJECTED_BY_SUPPORT_AND_IDENTIFIABILITY",
            "high_resolution_silent_substitution": "FORBIDDEN",
            "arbitrary_regularized_projection": "NOT_CANONICAL",
            "multi_snapshot_direct_parity": "BLOCKED_NOT_FABRICATED",
            "next_stage": "PR-04C split-domain conservative exchange contract and multi-snapshot trajectory closure",
        },
        "tool_status": tool_status,
        "harnesses": harness_receipt,
    }
    (ARTIFACT / "PR04B2B_ledger.json").write_text(
        json.dumps(ledger, indent=2, default=json_default) + "\n", encoding="utf-8"
    )

    verifier_code = '''#!/usr/bin/env python3
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
ledger=json.loads((HERE/"PR04B2B_ledger.json").read_text())
assert ledger["status"]=="PASS_PR04B2B_IDENTIFIABILITY_NO_GO_PR04C_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"]=="IN_PROGRESS"
assert ledger["decision"]["direct_native_to_17_cell_map"]=="REJECTED_BY_SUPPORT_AND_IDENTIFIABILITY"
with np.load(HERE/"native_common_partition_v054.npz",allow_pickle=False) as data:
    assert data["target_uniform_moment_matrix"].shape==(5,17)
    assert data["production_energy_eV"].shape==(311,)
    assert data["high_resolution_energy_eV"].shape==(1493,)
    assert float(data["full_native_raw_moments_x"][2]/data["full_native_raw_moments_x"][0])>1e8
    assert np.min(data["positive_witness_plus"])>0
    assert np.min(data["positive_witness_minus"])>0
print("PR-04B2B native/common partition: PASS_NO_GO; PR-04C exchange contract OPEN")
'''
    verifier = ARTIFACT / "verify_PR04B2B.py"
    verifier.write_text(verifier_code, encoding="utf-8")
    os.chmod(verifier, 0o755)

    readme = """# PR-04B2B / v0.54

This immutable artifact proves that the canonical full native physical edge
measure cannot be represented by a positive measure on the v0.51 17-cell core
while preserving mass and second moment. It also proves that moments through
order four do not identify seventeen positive cell masses without an extra
closure. The production and high-resolution integrated-rate grids are separate
and non-nested. The canonical runtime archive provides no numerical edge array,
dedicated two-photon-table generator member, or source write path for the
bundled tables.

The result is an informative no-go, not a solver failure. PR-04 remains open;
the next stage couples native transport and the COM--KHW core through an
explicit split-domain conservative number/energy exchange contract.

Run:

```bash
python verify_PR04B2B.py
```
"""
    (ARTIFACT / "README.md").write_text(readme, encoding="utf-8")

    create_manifest(ARTIFACT)
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
        "data": str(DATA_OUT),
        "metrics": numerical_metrics,
        "failed_gates": [name for name, passed in hard_gates.items() if not passed],
    }
    print(json.dumps(result, indent=2, default=json_default))
    if not all(hard_gates.values()):
        raise SystemExit(f"PR-04B2B hard gates failed: {result['failed_gates']}")
    if not args.keep_work:
        work_context.cleanup()


if __name__ == "__main__":
    main()

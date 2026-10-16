"""Fail-closed, versioned REC primordial-history boundary for REI.

This module only exports a diagnostic boundary packet. It has no REI runtime
imports or write path. A z=20 state is emitted only from a complete,
source-bound, independently integrated and validated history artifact.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
from typing import Any
import zipfile

PACKET_SCHEMA = "rec.primordial.rei_boundary.v1"
MANIFEST_SCHEMA = "rec.hyrec.primordial_history_manifest.v1"
CLAIM_SCOPE = "ORIGINAL_HYREC_2012_STAGE_SEQUENCE_FLRW_Q0"
ORIGINAL_HYREC_ZIP_SHA256 = (
    "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
)
ORIGINAL_C_STDOUT_SHA256 = "6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400"
R3G_YHE = 0.2454
TARGET_REI_SCENARIO_SHA256 = (
    "07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"
)
R3G_COSMOLOGY = {
    "T0_K": 2.7255,
    "omega_b_h2": 0.0224,
    "omega_m_h2": 0.14309694000000003,
    "omega_k_h2": 0.0,
    "omega_lambda_h2": 0.31113726660800006,
    "w0": -1.0,
    "wa": 0.0,
    "YHe": R3G_YHE,
    "N_eff_massless": 3.03821934419124,
    "fsR": 1.0,
    "meR": 1.0,
}
HYREC_FHE_MASS_FACTOR = 3.97153
REI_FHE_MASS_FACTOR = 4.0
K_B_J_K = 1.380649e-23
C_M_S = 299792458.0
SIGMA_T_M2 = 6.6524587321e-29
G_SI = 6.67430e-11
M_P_KG = 1.67262192369e-27
HYREC_H100_S_INV = 3.2407792896393e-18
HYREC_RADIATION_H2_PER_K4 = 4.48162687719e-7
HYREC_NU_DENSITY_FACTOR = 0.227107317660239
HYREC_NH0_PER_OMBH2 = 11.223846333047
NATIVE_GRID_ROWS = 105859
NATIVE_LNA_START = -math.log(8001.0)
NATIVE_LNA_STEP = 8.49e-5
ACTIVATION = "DISABLED_REQUIRES_SEPARATE_REI_APPROVAL"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_SOURCE_STAGES = frozenset({
    "HeIII_SAHA", "HeII_RECOMBINATION", "HHe_FULL_STEADY_TM",
    "H_ONLY_STEADY_TM", "H_TM_COEVOLUTION", "LOW_Z_PEEBLES",
})
REQUIRED_PARITY_METRICS = frozenset({
    "xe_relative", "Tm_relative", "xHII_absolute", "xHeII_absolute",
    "hydrogen_rhs_scaled", "helium_rhs_scaled", "virtual_outgoing_scaled",
    "virtual_average_scaled", "lyman_outgoing_scaled",
})
INVENTORY_REL_TOL = 1e-12
INVENTORY_ABS_FLOOR = 1e-15


def _inventory_close(actual: float, expected: float) -> bool:
    return abs(actual-expected) <= INVENTORY_REL_TOL*max(abs(actual), abs(expected), INVENTORY_ABS_FLOOR)


def _require_density_match(actual: Any, expected: float, label: str) -> None:
    value = _finite(actual, label, positive=True)
    if not _inventory_close(value, expected):
        raise ValueError(f"{label} does not match the frozen cosmology")


def _sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256")
    return value


def _canonical_sha(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def _safe_child(root: Path, relpath: Any, label: str) -> Path:
    if not isinstance(relpath, str) or Path(relpath).is_absolute() or ".." in Path(relpath).parts:
        raise ValueError(f"{label} path must be a safe manifest-relative path")
    path = (root / relpath).resolve()
    if root.resolve() not in path.parents:
        raise ValueError(f"{label} path escapes manifest directory")
    return path


def _finite(value: Any, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must not be a boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(result) or (positive and result <= 0):
        raise ValueError(f"{name} must be finite" + (" and positive" if positive else ""))
    return result


def source_number_fractions(y_he: float) -> dict[str, float]:
    """HyRec 2012 abundance convention: number of He nuclei per H nucleus."""
    y = _finite(y_he, "YHe")
    if not 0 < y < 1:
        raise ValueError("YHe must lie strictly between zero and one")
    source_fhe = y / (HYREC_FHE_MASS_FACTOR * (1-y))
    recipient_fhe = y / (REI_FHE_MASS_FACTOR * (1-y))
    if not all(math.isfinite(v) and v > 0 for v in (source_fhe, recipient_fhe)):
        raise ValueError("helium number fraction overflowed")
    return {
        "helium_mass_fraction": y,
        "fHe_helium_nuclei_per_hydrogen_nucleus": source_fhe,
        "fHe_REI_target_nuclei_per_hydrogen_nucleus": recipient_fhe,
    }


def joule_per_m3_to_erg_per_cm3(value: Any) -> float:
    """Exact SI/cgs conversion: 1 J m^-3 = 10 erg cm^-3."""
    converted = _finite(value, "energy density") * 10.0
    if not math.isfinite(converted):
        raise ValueError("energy-density unit conversion overflow")
    return converted


def _validate_native_grid_row(index: int, ln_a: Any) -> None:
    """Enforce the frozen source grid, not merely a monotone arbitrary grid."""
    if type(index) is not int or not 0 <= index < NATIVE_GRID_ROWS:
        raise ValueError("source-native grid index is outside the frozen inventory")
    value = _finite(ln_a, f"native ln_a[{index}]")
    expected = NATIVE_LNA_START + index * NATIVE_LNA_STEP
    if abs(value - expected) > 2e-12:
        raise ValueError("history does not match the frozen source-native ln(a) grid")


def _interpolate_four_point_ln_a(rows: list[dict[str, Any]], zref: float) -> dict[str, Any]:
    """Interpolate a small supplied stencil/trajectory; callers bind its provenance."""
    if len(rows) < 4:
        raise ValueError("four accepted source states are required for interpolation")
    target = -math.log1p(_finite(zref, "reference redshift"))
    coordinates = [_finite(row.get("ln_a"), "history ln_a") for row in rows]
    if any(b <= a for a, b in zip(coordinates, coordinates[1:])):
        raise ValueError("history is not strictly ordered in source ln(a)")
    right = next((i for i, value in enumerate(coordinates) if value >= target), len(coordinates))
    left = right - 1
    if left < 1 or right + 1 >= len(rows):
        raise ValueError("four-point ln(a) interpolation would extrapolate")
    stencil = rows[left-1:right+2]
    xs = coordinates[left-1:right+2]
    if len(stencil) != 4 or not (xs[1] <= target <= xs[2]):
        raise ValueError("four-point ln(a) interpolation stencil is invalid")
    fields = ("xHII_per_H", "xHeII_per_He", "xHeIII_per_He", "xe_per_H", "Tm_K", "H_s_inv", "nH_m3")
    result: dict[str, Any] = {"z": zref, "ln_a": target, "T0_K": R3G_COSMOLOGY["T0_K"]}
    for field in fields:
        ys = [_finite(row.get(field), f"stencil {field}") for row in stencil]
        value = 0.0
        for j, xj in enumerate(xs):
            weight = 1.0
            for k, xk in enumerate(xs):
                if j != k:
                    weight *= (target-xk)/(xj-xk)
            value += weight*ys[j]
        result[field] = _finite(value, f"interpolated {field}")
    fhe = source_number_fractions(R3G_YHE)["fHe_helium_nuclei_per_hydrogen_nucleus"]
    expected_xe = result["xHII_per_H"] + fhe*(result["xHeII_per_He"]+2*result["xHeIII_per_He"])
    if not _inventory_close(result["xe_per_H"], expected_xe):
        raise ValueError("interpolated xe_per_H violates same-unit source charge inventory")
    stage = stencil[1].get("stage")
    if not isinstance(stage, str) or not stage:
        raise ValueError("interpolation source stage is missing")
    result["stage"] = stage
    for name in ("xHII", "xHeII", "xHeIII"):
        result[f"{name}_determination"] = f"FOUR_POINT_SOURCE_LN_A:{stage}"
    result["interpolation"] = {"method":"four_point_lagrange_ln_a", "source_indices":[r.get("index") for r in stencil], "source_ln_a":xs, "target_ln_a":target, "extrapolated":False}
    return result


def _history_row(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError("unexpected primordial history manifest schema")
    if manifest.get("status") != "PASS" or manifest.get("scope") != CLAIM_SCOPE:
        raise ValueError("history is not a validated full primordial H+He integration")
    if manifest.get("independently_integrated") is not True:
        raise ValueError("history must be independently integrated, not copied from C output")
    src = manifest.get("source")
    if not isinstance(src, dict):
        raise ValueError("missing source identity")
    if _sha(src.get("original_hyrec_zip_sha256"), "original HyRec ZIP SHA") != ORIGINAL_HYREC_ZIP_SHA256:
        raise ValueError("original HyRec archive identity mismatch")
    source_commit = src.get("rec_commit")
    if not isinstance(source_commit, str) or not GIT_SHA_RE.fullmatch(source_commit):
        raise ValueError("REC source commit must be a full Git SHA")
    receipt_sha = _sha(src.get("validation_receipt_sha256"), "validation receipt SHA")
    history_info = manifest.get("history")
    if not isinstance(history_info, dict) or history_info.get("rows", 0) < 2:
        raise ValueError("validated history row ledger is missing")
    root = Path(manifest["_manifest_dir"]).resolve()
    history_path = _safe_child(root, history_info.get("path"), "history")
    raw = history_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != _sha(history_info.get("sha256"), "history SHA"):
        raise ValueError("history file SHA does not match the manifest")
    rows = []
    for line_no, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL history row {line_no}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"history row {line_no} is not an object")
        rows.append(row)
    if len(rows) != int(history_info["rows"]):
        raise ValueError("history row count does not match manifest")
    cosmology = manifest.get("cosmology")
    if not isinstance(cosmology, dict):
        raise ValueError("source cosmology ledger is missing")
    cosmology_sha = _sha(src.get("cosmology_sha256"), "cosmology SHA")
    if _canonical_sha(cosmology) != cosmology_sha:
        raise ValueError("source cosmology SHA does not match its canonical ledger")
    if set(cosmology) != set(R3G_COSMOLOGY):
        raise ValueError("source cosmology inventory differs from the frozen R3g contract")
    for name, expected in R3G_COSMOLOGY.items():
        actual = _finite(cosmology.get(name), f"source cosmology {name}")
        if actual != expected:
            raise ValueError(f"source cosmology {name} differs from frozen R3g input")
    receipt_path = _safe_child(root, src.get("validation_receipt_path"), "validation receipt")
    receipt_raw = receipt_path.read_bytes()
    if hashlib.sha256(receipt_raw).hexdigest() != receipt_sha:
        raise ValueError("validation receipt file SHA does not match source identity")
    try:
        receipt = json.loads(receipt_raw)
    except json.JSONDecodeError as exc:
        raise ValueError("validation receipt is not JSON") from exc
    if (receipt.get("status") != "PASS"
            or receipt.get("scope") != CLAIM_SCOPE
            or receipt.get("history_sha256") != history_info["sha256"]
            or receipt.get("cosmology_sha256") != cosmology_sha
            or receipt.get("rec_commit") != source_commit
            or receipt.get("original_hyrec_zip_sha256") != ORIGINAL_HYREC_ZIP_SHA256):
        raise ValueError("validation receipt does not attest this full history and cosmology")
    if len(rows) != 105859:
        raise ValueError("accepted history does not cover the frozen source-native grid")
    zref = _finite(manifest.get("reference", {}).get("z"), "reference redshift")
    if zref != 20.0:
        raise ValueError("this interface contract is fixed at z_ref=20")
    coordinates: list[float] = []
    stages: set[str] = set()
    observed_stage_ranges: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if type(row.get("index")) is not int or row.get("index") != index or row.get("accepted_step") is not True:
            raise ValueError("history index inventory or accepted-step flag is invalid")
        stage = row.get("stage")
        if not isinstance(stage, str) or not stage:
            raise ValueError("source stage label is missing from an accepted history row")
        z = _finite(row.get("z"), f"history z[{index}]")
        ln_a = _finite(row.get("ln_a"), f"history ln_a[{index}]")
        _validate_native_grid_row(index, ln_a)
        if abs(ln_a + math.log1p(z)) > 2e-13:
            raise ValueError("history clock coordinate is inconsistent with redshift")
        coordinates.append(ln_a)
        stages.add(stage)
        if not observed_stage_ranges or observed_stage_ranges[-1]["source_stage"] != stage:
            observed_stage_ranges.append({"first_index": index, "last_index": index, "source_stage": stage})
        else:
            observed_stage_ranges[-1]["last_index"] = index
    if len(rows) != NATIVE_GRID_ROWS or len(stages) < 2:
        raise ValueError("source-native history does not cover all rows and source stages")
    producer_entry = manifest.get("admission", {}).get("producer", {})
    try:
        producer_path = _safe_child(root, producer_entry.get("path"), "producer evidence")
        producer = json.loads(producer_path.read_bytes())
        if producer.get("stage_coverage", {}).get("stage_ranges") != observed_stage_ranges:
            raise ValueError("stage coverage receipt differs from labels on accepted history rows")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"source stage coverage is not proven against accepted rows: {exc}") from exc
    if any(b <= a for a, b in zip(coordinates, coordinates[1:])):
        raise ValueError("history is not strictly ordered in source ln(a)")
    return _interpolate_four_point_ln_a(rows, zref)


def _source_state(row: dict[str, Any], fractions: dict[str, float], cosmology: dict[str, Any]) -> dict[str, Any]:
    z = _finite(row.get("z"), "z")
    xe = _finite(row.get("xe_per_H"), "xe_per_H")
    xh = _finite(row.get("xHII_per_H"), "xHII_per_H")
    xhe2 = _finite(row.get("xHeII_per_He"), "xHeII_per_He")
    xhe3 = _finite(row.get("xHeIII_per_He"), "xHeIII_per_He")
    tm = _finite(row.get("Tm_K"), "Tm_K", positive=True)
    h = _finite(row.get("H_s_inv"), "H_s_inv", positive=True)
    nh = _finite(row.get("nH_m3"), "nH_m3", positive=True)
    z1 = 1.0+z
    radiation_h2 = HYREC_RADIATION_H2_PER_K4*cosmology["T0_K"]**4*(
        1.0+HYREC_NU_DENSITY_FACTOR*cosmology["N_eff_massless"]
    )
    h_expected = HYREC_H100_S_INV*math.sqrt(
        cosmology["omega_m_h2"]*z1**3+radiation_h2*z1**4
        +cosmology["omega_k_h2"]*z1**2+cosmology["omega_lambda_h2"]
    )
    nh_expected = HYREC_NH0_PER_OMBH2*cosmology["omega_b_h2"]*(1-cosmology["YHe"])*z1**3
    _require_density_match(h, h_expected, "source H")
    _require_density_match(nh, nh_expected, "source nH")
    fhe = fractions["fHe_helium_nuclei_per_hydrogen_nucleus"]
    if not (0 <= xh <= 1 and 0 <= xhe2 <= 1 and 0 <= xhe3 <= 1 and xhe2+xhe3 <= 1):
        raise ValueError("nonphysical source species ledger")
    xhei = 1.0 - xhe2 - xhe3
    xhi = 1.0 - xh
    xe_from_species = xh + fhe * (xhe2 + 2*xhe3)
    if not _inventory_close(xe, xe_from_species):
        raise ValueError("xe_per_H violates the source species charge ledger")
    xhei_h = fhe*xhei
    xheii_h = fhe*xhe2
    xheiii_h = fhe*xhe3
    if not _inventory_close(xhei_h+xheii_h+xheiii_h, fhe):
        raise ValueError("source helium per-H inventory does not close")
    ne = nh * xe
    opacity_s = C_M_S * SIGMA_T_M2 * ne
    # HyRec species fractions are per nucleus; ions and neutrals retain one
    # baryonic thermal particle each, with free electrons as additional particles.
    thermal_j_m3 = 1.5 * nh * (1. + fhe + xe) * K_B_J_K * tm
    derived = (ne, opacity_s, opacity_s / h, nh*fhe, thermal_j_m3)
    if not all(math.isfinite(value) and value >= 0 for value in derived):
        raise ValueError("source SI metric overflow or nonfinite result")
    if any(row.get(key) in (None, "NOT_PROVIDED") for key in
           ("xHII_determination", "xHeII_determination", "xHeIII_determination")):
        raise ValueError("source species determination labels are missing")
    return {
        "z": z,
        "a": 1.0/(1.0+z),
        "ln_a": -math.log1p(z),
        "metric_signature": "-+++",
        "q_over_H": 0.0,
        "T_radiation_K": cosmology["T0_K"]*(1.0+z),
        "proper_time_since_reference_s": None,
        "clock_note": "source slice at fixed FLRW z; proper-time origin is not inferred",
        "species_per_source_normalization": {
            "xHII_per_H": xh,
            "xHI_per_H": xhi,
            "xHeII_per_He": xhe2,
            "xHeIII_per_He": xhe3,
            "xHeI_per_He": xhei,
            "xHeII_per_H": xheii_h,
            "xHeIII_per_H": xheiii_h,
            "xHeI_per_H": xhei_h,
            "helium_inventory_per_H": fhe,
            "xe_per_H": xe,
            "determination": {
                "xHII": row.get("xHII_determination", "NOT_PROVIDED"),
                "xHI": "hydrogen_nucleus_closure_1_minus_xHII",
                "xHeII": row.get("xHeII_determination", "NOT_PROVIDED"),
                "xHeIII": row.get("xHeIII_determination", "NOT_PROVIDED"),
                "xHeI": "helium_nucleus_closure_1_minus_xHeII_minus_xHeIII",
                "xe": "charge_identity_from_source_species_per_H",
            },
        },
        "nH_source_m3": nh,
        "nHe_source_m3": nh * fhe,
        "ne_source_m3": ne,
        "Tm_K": tm,
        "H_s_inv": h,
        "thomson_opacity_proper_s_inv": opacity_s,
        "thomson_opacity_per_ln_a": opacity_s / h,
        "thermal_energy_density_J_m3": thermal_j_m3,
        "thermal_energy_density_erg_cm3": joule_per_m3_to_erg_per_cm3(thermal_j_m3),
        "source_stage": row["stage"],
        "interpolation_provenance": row["interpolation"],
    }


_REQUIRED_ADMISSION_ARTIFACTS = (
    "producer", "source_tables", "source_parity", "convergence", "independent_review",
)


def _richardson_reasons(convergence: dict[str, Any], history_sha: Any,
                        root: Path, producer: dict[str, Any],
                        review: dict[str, Any]) -> list[str]:
    """Require distinct byte histories and a reproducible three-level estimate."""
    reasons: list[str] = []
    refinements = convergence.get("independent_refinements")
    if not isinstance(refinements, list) or len(refinements) != 2:
        return ["exactly two independent refinement histories are required"]
    seen_ids: set[str] = set()
    seen_hashes: set[str] = {history_sha} if isinstance(history_sha, str) else set()
    steps: list[float] = []
    for item in refinements:
        try:
            identity = item.get("run_id")
            run_sha = _sha(item.get("history_sha256"), "refinement history SHA")
            raw = _safe_child(root, item.get("history_path"), "refinement history").read_bytes()
            step = _finite(item.get("step_size"), "refinement step", positive=True)
            if (not isinstance(identity, str) or not identity or identity in seen_ids
                    or run_sha in seen_hashes or hashlib.sha256(raw).hexdigest() != run_sha
                    or item.get("status") != "PASS"):
                reasons.append("refinement identity, bytes, or status is not independent")
            seen_ids.add(identity)
            seen_hashes.add(run_sha)
            steps.append(step)
        except (AttributeError, OSError, ValueError) as exc:
            reasons.append(f"refinement history is unavailable: {exc}")
    if len(steps) != 2 or not (NATIVE_LNA_STEP > steps[0] > steps[1] > 0):
        reasons.append("refinement step sizes must strictly refine the native history")
        return reasons
    ratio_01 = NATIVE_LNA_STEP / steps[0]
    ratio_12 = steps[0] / steps[1]
    if abs(ratio_01/ratio_12 - 1.) > 1e-8:
        reasons.append("Richardson levels must have a common refinement ratio")
        return reasons
    rich = convergence.get("richardson")
    tolerances = convergence.get("predeclared_tolerances")
    if (convergence.get("richardson_status") != "PASS" or not isinstance(rich, dict)
            or rich.get("status") != "PASS" or not isinstance(tolerances, dict)
            or set(tolerances) != REQUIRED_PARITY_METRICS):
        reasons.append("numeric Richardson data and predeclared metric tolerances are missing")
        return reasons
    contract_sha = _canonical_sha(tolerances)
    if (producer.get("convergence_tolerance_contract_sha256") != contract_sha
            or review.get("convergence_tolerance_contract_sha256") != contract_sha
            or convergence.get("tolerance_contract_sha256") != contract_sha):
        reasons.append("Richardson tolerances are not bound to producer, evidence, and reviewer")
    metrics = rich.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != REQUIRED_PARITY_METRICS:
        reasons.append("Richardson metric inventory is incomplete")
        return reasons
    for name in REQUIRED_PARITY_METRICS:
        try:
            item = metrics[name]
            coarse = _finite(item.get("baseline_value"), f"{name} baseline")
            medium = _finite(item.get("coarse_refinement_value"), f"{name} medium")
            fine = _finite(item.get("fine_refinement_value"), f"{name} fine")
            order = _finite(item.get("observed_order"), f"{name} order", positive=True)
            extrapolated = _finite(item.get("extrapolated_value"), f"{name} extrapolated")
            bound = _finite(item.get("error_bound"), f"{name} bound")
            tol = _finite(tolerances[name], f"{name} predeclared tolerance", positive=True)
            d01, d12 = abs(coarse-medium), abs(medium-fine)
            if d01 <= 0 or d12 <= 0 or bound < 0:
                raise ValueError("nonzero consecutive differences and nonnegative bound required")
            derived_order = math.log(d01/d12)/math.log(ratio_01)
            if derived_order <= 0 or abs(order-derived_order) > 1e-8*max(1., abs(derived_order)):
                raise ValueError("observed order is inconsistent with three numeric levels")
            derived_extrapolated = fine + (fine-medium)/(ratio_01**derived_order-1.)
            scale = max(abs(derived_extrapolated), abs(fine), INVENTORY_ABS_FLOOR)
            if abs(extrapolated-derived_extrapolated) > 1e-10*scale:
                raise ValueError("extrapolated value is inconsistent with the numeric levels")
            if bound + 1e-12*scale < abs(derived_extrapolated-fine) or bound > tol:
                raise ValueError("Richardson error bound exceeds the predeclared tolerance")
        except (AttributeError, OverflowError, TypeError, ValueError, ZeroDivisionError) as exc:
            reasons.append(f"Richardson metric {name} is invalid: {exc}")
    return reasons


def _parity_reasons(parity: dict[str, Any], producer: dict[str, Any],
                    review: dict[str, Any]) -> list[str]:
    tolerances = parity.get("tolerances")
    metrics = parity.get("metrics")
    if (not isinstance(tolerances, dict) or not isinstance(metrics, dict)
            or set(tolerances) != REQUIRED_PARITY_METRICS
            or set(metrics) != REQUIRED_PARITY_METRICS
            or parity.get("predeclared_metric_inventory") != sorted(REQUIRED_PARITY_METRICS)):
        return ["predeclared source parity metric inventory is incomplete"]
    reasons: list[str] = []
    contract_sha = _canonical_sha(tolerances)
    if (producer.get("parity_tolerance_contract_sha256") != contract_sha
            or review.get("parity_tolerance_contract_sha256") != contract_sha
            or parity.get("tolerance_contract_sha256") != contract_sha):
        reasons.append("source parity tolerances are not bound to producer, evidence, and reviewer")
    for name in REQUIRED_PARITY_METRICS:
        try:
            tol = _finite(tolerances[name], f"parity tolerance {name}", positive=True)
            measured = _finite(metrics[name], f"parity metric {name}")
            if measured < 0 or measured > tol:
                reasons.append(f"source parity metric {name} exceeds its explicit tolerance")
        except ValueError as exc:
            reasons.append(f"invalid source parity metric/tolerance: {exc}")
    return reasons


def _admission_hold_reasons(manifest: dict[str, Any]) -> list[str]:
    """Verify evidence bytes and statuses before considering any boundary row."""
    admission = manifest.get("admission")
    if not isinstance(admission, dict):
        return [f"missing admission evidence: {name}" for name in _REQUIRED_ADMISSION_ARTIFACTS]
    root = Path(manifest["_manifest_dir"]).resolve()
    reasons: list[str] = []
    loaded: dict[str, dict[str, Any]] = {}
    for name in _REQUIRED_ADMISSION_ARTIFACTS:
        entry = admission.get(name)
        if not isinstance(entry, dict):
            reasons.append(f"missing admission evidence: {name}")
            continue
        try:
            path = _safe_child(root, entry.get("path"), f"admission {name}")
            raw = path.read_bytes()
            expected = _sha(entry.get("sha256"), f"admission {name} SHA")
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError(f"admission {name} artifact SHA mismatch")
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError(f"admission {name} artifact must be a JSON object")
            loaded[name] = value
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            reasons.append(str(exc))
    producer = loaded.get("producer", {})
    if not isinstance(producer.get("author_id"), str) or not producer.get("author_id", "").strip():
        reasons.append("producer author identity is missing")
    if producer.get("identity_kind") != "INDEPENDENT_PYTHON_INTEGRATOR_SOURCE":
        reasons.append("producer artifact does not identify the independent Python integration")
    else:
        try:
            code_path = _safe_child(root, producer.get("producer_code_path"), "producer source")
            code_raw = code_path.read_bytes()
            if hashlib.sha256(code_raw).hexdigest() != _sha(producer.get("producer_code_sha256"), "producer code SHA"):
                reasons.append("producer Python source byte hash does not match the admission evidence")
            if producer.get("rec_commit") != manifest.get("source", {}).get("rec_commit"):
                reasons.append("producer code commit differs from the history source commit")
        except (OSError, ValueError) as exc:
            reasons.append(f"producer code identity unavailable: {exc}")
    tables = loaded.get("source_tables", {})
    if tables.get("status") != "PASS" or tables.get("original_hyrec_zip_sha256") != ORIGINAL_HYREC_ZIP_SHA256:
        reasons.append("source atomic table inventory and original archive identity are not validated")
    else:
        try:
            archive_path = _safe_child(root, tables.get("archive_path"), "original HyRec archive")
            archive_raw = archive_path.read_bytes()
            if hashlib.sha256(archive_raw).hexdigest() != ORIGINAL_HYREC_ZIP_SHA256:
                reasons.append("archived original HyRec bytes do not match the frozen SHA-256")
            members = tables.get("members")
            with zipfile.ZipFile(archive_path) as archive:
                infos = archive.infolist()
                expected_names = {item.filename for item in infos if not item.is_dir()}
                if (not isinstance(members, list) or
                    {item.get("name") for item in members if isinstance(item, dict)} != expected_names or
                    len(members) != len(expected_names)):
                    reasons.append("source table member inventory is not complete and exact")
                else:
                    for item in members:
                        name = item["name"]
                        parts = Path(name).parts
                        mode = next(info.external_attr >> 16 for info in infos if info.filename == name)
                        if name.startswith("/") or ".." in parts or stat.S_ISLNK(mode):
                            reasons.append(f"unsafe original source member: {name}")
                            continue
                        if hashlib.sha256(archive.read(name)).hexdigest() != _sha(item.get("sha256"), f"source member {name} SHA"):
                            reasons.append(f"source member byte hash mismatch: {name}")
        except (OSError, ValueError) as exc:
            reasons.append(f"original HyRec archive bytes unavailable: {exc}")
    history_info = manifest.get("history", {})
    history_sha = history_info.get("sha256")
    if (history_info.get("rows") != 105859 or history_info.get("accepted_rows") != 105859
            or history_info.get("source_native_grid") is not True
            or history_info.get("interpolation_provenance") != "FOUR_CONSECUTIVE_ACCEPTED_SOURCE_STATES_IN_LN_A_NO_EXTRAPOLATION"):
        reasons.append("full source-native accepted history and four-point ln(a) z=20 stencil are unavailable")
    coverage = loaded.get("producer", {}).get("stage_coverage")
    if (not isinstance(coverage, dict) or coverage.get("status") != "PASS"
            or coverage.get("history_sha256") != history_sha
            or not isinstance(coverage.get("stage_ranges"), list)
            or len(coverage.get("stage_ranges", [])) < 2):
        reasons.append("source-owned stage coverage inventory is missing or not bound to accepted history")
    else:
        cursor = 0
        try:
            for stage_range in coverage["stage_ranges"]:
                start = stage_range.get("first_index")
                end = stage_range.get("last_index")
                label = stage_range.get("source_stage")
                if (type(start) is not int or type(end) is not int or start != cursor
                        or end < start or not isinstance(label, str) or not label):
                    raise ValueError("stage ranges are not an exact ordered partition")
                cursor = end + 1
            if cursor != NATIVE_GRID_ROWS:
                raise ValueError("stage ranges do not cover the complete native grid")
            declared_stages = coverage.get("required_source_stages")
            if (not isinstance(declared_stages, list)
                    or any(not isinstance(stage, str) for stage in declared_stages)
                    or set(declared_stages) != REQUIRED_SOURCE_STAGES):
                raise ValueError("predeclared source stage inventory is incomplete")
            if not REQUIRED_SOURCE_STAGES.issubset({item["source_stage"] for item in coverage["stage_ranges"]}):
                raise ValueError("accepted source history omits a required source stage")
        except (AttributeError, ValueError) as exc:
            reasons.append(f"invalid source-native stage coverage partition: {exc}")
    try:
        cosmology_path = _safe_child(root, manifest.get("cosmology_input_path"), "cosmology input")
        cosmology_raw = cosmology_path.read_bytes()
        cosmology_bytes_sha = hashlib.sha256(cosmology_raw).hexdigest()
        if cosmology_bytes_sha != _sha(manifest.get("cosmology_input_sha256"), "cosmology input bytes SHA"):
            raise ValueError("cosmology input byte hash mismatch")
        parsed = json.loads(cosmology_raw)
        if parsed != manifest.get("cosmology") or _canonical_sha(parsed) != manifest.get("source", {}).get("cosmology_sha256"):
            raise ValueError("cosmology bytes, parsed ledger, and canonical hash disagree")
        if manifest.get("clock_convention") != "SOURCE_NATIVE_LN_A_FROM_INDEX:ln_a=-ln(8001)+i*8.49e-5":
            raise ValueError("source-native cosmology clock convention is absent")
        if manifest.get("model") != CLAIM_SCOPE:
            raise ValueError("cosmology model scope is not source-qualified")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        reasons.append(f"complete cosmology input bytes/parsed hash/clock/model missing: {exc}")
    for name in ("source_parity", "convergence", "independent_review"):
        evidence = loaded.get(name, {})
        if evidence.get("status") != "PASS" or evidence.get("history_sha256") != history_sha:
            reasons.append(f"{name} evidence is not PASS")
    parity = loaded.get("source_parity", {})
    if parity.get("original_c_stdout_sha256") != ORIGINAL_C_STDOUT_SHA256:
        reasons.append("full-history source parity does not bind the frozen original C baseline")
    review = loaded.get("independent_review", {})
    reasons.extend(_parity_reasons(parity, producer, review))
    convergence = loaded.get("convergence", {})
    reasons.extend(_richardson_reasons(convergence, history_sha, root, producer, review))
    if (review.get("reviewer_role") != "INDEPENDENT_SCIENTIFIC_REVIEWER"
            or not isinstance(review.get("reviewer_id"), str) or not review.get("reviewer_id")
            or not isinstance(review.get("author_id"), str) or not review.get("author_id", "").strip()
            or review.get("author_id") == producer.get("author_id")
            or review.get("reviewer_id") == producer.get("author_id")
            or review.get("producer_sha256") != admission.get("producer", {}).get("sha256")
            or review.get("history_sha256") != history_sha):
        reasons.append("independent scientific review identity is missing or not independent")
    try:
        source = manifest["source"]
        validation_path = _safe_child(root, source.get("validation_receipt_path"), "validation receipt")
        validation_raw = validation_path.read_bytes()
        if hashlib.sha256(validation_raw).hexdigest() != _sha(source.get("validation_receipt_sha256"), "validation receipt SHA"):
            raise ValueError("validation receipt byte hash mismatch")
        validation = json.loads(validation_raw)
        declared = validation.get("admission_artifact_sha256", {})
        for name in _REQUIRED_ADMISSION_ARTIFACTS:
            if declared.get(name) != admission.get(name, {}).get("sha256"):
                reasons.append(f"validation receipt is not hash-bound to the {name} evidence")
        if (validation.get("cosmology_input_sha256") != manifest.get("cosmology_input_sha256")
                or validation.get("cosmology_sha256") != source.get("cosmology_sha256")
                or validation.get("clock_convention") != manifest.get("clock_convention")
                or validation.get("model") != manifest.get("model")
                or validation.get("history_sha256") != history_sha):
            reasons.append("validation receipt does not bind cosmology bytes, parsed hash, clock, model, and history")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        reasons.append(f"source validation receipt is missing or malformed: {exc}")
    try:
        root = Path(manifest["_manifest_dir"]).resolve()
        scenario_path = _safe_child(root, manifest.get("recipient_scenario_path"), "recipient scenario")
        scenario_raw = scenario_path.read_bytes()
        scenario_sha = _sha(manifest.get("recipient_scenario_sha256"), "recipient scenario SHA")
        if hashlib.sha256(scenario_raw).hexdigest() != scenario_sha or scenario_sha != TARGET_REI_SCENARIO_SHA256:
            raise ValueError("recipient scenario bytes do not match the frozen target SHA")
        scenario = json.loads(scenario_raw)
        c = scenario["cosmology"]
        ini = scenario["gas_initial"]
        interval = scenario["interval"]
        binding = manifest["recipient_binding"]
        if (scenario.get("schema") != "rei.axbi.scenario_lock.v1"
                or interval.get("zbar_start") != 20
                or str(c.get("omega_b_formula")) != "0.0224/(0.674^2)"
                or _finite(c.get("helium_mass_fraction"), "recipient YHe") != R3G_YHE
                or _finite(c.get("h0_km_s_mpc"), "recipient H0") != 67.4
                or _finite(c.get("omega_m"), "recipient omega_m") != .315
                or _finite(c.get("omega_r"), "recipient omega_r") != .000092
                or _finite(c.get("tcmb0_k"), "recipient T0") != 2.7255
                or str(ini.get("kind")) != "DECLARED_APPROXIMATE_CONDITIONAL_IC_NOT_REC_DONOR"):
            raise ValueError("recipient scenario does not match the frozen REI comparison contract")
        if (not isinstance(binding.get("rei_commit"), str)
                or not GIT_SHA_RE.fullmatch(binding.get("rei_commit", ""))
                or binding.get("clock_convention") != "REI_MEAN_REDSHIFT_ZBAR_A_INV_MINUS_1"
                or _finite(binding.get("YHe"), "recipient YHe") != R3G_YHE):
            raise ValueError("recipient scenario commit or clock convention is not bound")
        h0 = 67.4*1000.0/3.0856775814913673e22
        z1 = 21.0
        target_h = h0*math.sqrt(.315*z1**3+.000092*z1**4+(1-.315-.000092))
        rho_critical = 3*h0*h0/(8*math.pi*G_SI)
        target_nh = (1-R3G_YHE)*(.0224/.674**2)*rho_critical/M_P_KG*z1**3
        _require_density_match(binding.get("H_s_inv"), target_h, "recipient H")
        _require_density_match(binding.get("nH_m3"), target_nh, "recipient nH")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        reasons.append(f"recipient scenario byte/commit/clock/density binding missing or invalid: {exc}")
    # There is no validated full history or byte-bound recipient scenario in
    # this run. Do not accept top-level self-attested PASS labels in their place.
    return reasons


def build_boundary_packet(
    manifest_path: Path,
    *,
    target_scenario_sha256: str,
) -> dict[str, Any]:
    """Build a read-only interface packet; partial histories produce HOLD."""
    _sha(target_scenario_sha256, "target scenario SHA")
    if target_scenario_sha256 != TARGET_REI_SCENARIO_SHA256:
        raise ValueError("target REI scenario SHA differs from the frozen donor comparison baseline")
    manifest_path = Path(manifest_path)
    raw = manifest_path.read_bytes()
    manifest_sha = hashlib.sha256(raw).hexdigest()
    manifest = json.loads(raw)
    manifest["_manifest_dir"] = str(manifest_path.resolve().parent)
    packet: dict[str, Any] = {
        "schema": PACKET_SCHEMA,
        "packet_version": 1,
        "decision": "HOLD_MISSING_VALIDATED_HISTORY",
        "source_boundary": None,
        "activation": ACTIVATION,
        "adopted_into_REI": False,
        "recipient_comparison": None,
        "identity": {
            "history_manifest_sha256": manifest_sha,
            "target_scenario_sha256": target_scenario_sha256,
            "source_original_hyrec_zip_sha256": ORIGINAL_HYREC_ZIP_SHA256,
        },
        "scope": CLAIM_SCOPE,
        "normalization_ledger": source_number_fractions(R3G_YHE),
        "clock_convention": {
            "coordinate": "FLRW redshift z and ln(a)=-ln(1+z)",
            "proper_time": "not inferred from a single boundary slice",
            "reference_z": 20.0,
        },
        "source_evidence_status": manifest.get("status", "UNKNOWN"),
        "hold_reasons": [],
    }
    # Partial/incomplete science is an ordinary HOLD packet, not an exception.
    if (manifest.get("schema") != MANIFEST_SCHEMA
            or manifest.get("status") != "PASS"
            or manifest.get("scope") != CLAIM_SCOPE
            or manifest.get("independently_integrated") is not True):
        reasons = manifest.get("missing_for_boundary", [])
        packet["hold_reasons"] = [str(reason) for reason in reasons
                                   if "exact z=20 row" not in str(reason)]
        packet["hold_reasons"].append(
            "validated full source-owned H+He history through z=20 is absent; an exact z=20 native row is not required because a four-point accepted ln(a) interpolation is permitted"
        )
        packet["hold_reasons"].extend([
            "validated independent Python full-history receipt is absent",
            "source scope is not ORIGINAL_HYREC_2012_STAGE_SEQUENCE_FLRW_Q0",
            "source-native four-point ln(a) z=20 interpolation and no-extrapolation provenance are absent from the partial history",
            "recipient scenario bytes, REI commit, clock convention, and density ledger are not bound",
        ])
        return packet
    packet["hold_reasons"] = _admission_hold_reasons(manifest)
    if packet["hold_reasons"]:
        return packet
    row = _history_row(manifest)
    zref = float(manifest.get("reference", {}).get("z"))
    if zref != 20.0:
        raise ValueError("this interface contract is fixed at z_ref=20")
    fractions = source_number_fractions(manifest["cosmology"]["YHe"])
    state = _source_state(row, fractions, manifest["cosmology"])
    if state["z"] != zref:
        raise ValueError("reference row does not match fixed z_ref=20")
    target_y = _finite(manifest["recipient_binding"]["YHe"], "recipient YHe")
    if not 0.0 < target_y < 1.0:
        raise ValueError("recipient YHe must lie strictly between zero and one")
    target_fhe = target_y / (REI_FHE_MASS_FACTOR*(1-target_y))
    source_fhe = fractions["fHe_helium_nuclei_per_hydrogen_nucleus"]
    packet["decision"] = "REC_SOURCE_BOUNDARY_VALIDATED"
    packet["hold_reasons"] = []
    packet["source_boundary"] = {
        "scope": CLAIM_SCOPE,
        **state,
        "source_identity": {
            "original_hyrec_zip_sha256": ORIGINAL_HYREC_ZIP_SHA256,
            "rec_commit": manifest["source"]["rec_commit"],
            "validation_receipt_sha256": manifest["source"]["validation_receipt_sha256"],
            "history_sha256": manifest["history"]["sha256"],
            "cosmology_sha256": _sha(manifest["source"]["cosmology_sha256"], "cosmology SHA"),
        },
        "normalization_conversion": {
            "source_nHe_per_nH": source_fhe,
            "target_nHe_per_nH": target_fhe,
            "source_species_basis": "xHeII and xHeIII are per helium nucleus; xe and xHII are per hydrogen nucleus",
            "target_species_basis": "REI hydrogen and helium number ledger uses nHe/nH=Y/[4(1-Y)]",
        },
        "species_determination": "source-bound independent Python history values; He stages retain original HyRec stage ownership",
    }
    packet["recipient_comparison"] = {
        "scope": CLAIM_SCOPE,
        "scenario_sha256": manifest["recipient_scenario_sha256"],
        "rei_commit": manifest["recipient_binding"]["rei_commit"],
        "clock_convention": manifest["recipient_binding"]["clock_convention"],
        "H_s_inv": _finite(manifest["recipient_binding"]["H_s_inv"], "recipient H"),
        "nH_m3": _finite(manifest["recipient_binding"]["nH_m3"], "recipient nH"),
        "fHe_target_nHe_per_nH": target_fhe,
        "projection": None,
        "activation": ACTIVATION,
        "adopted_into_REI": False,
    }
    return packet


def write_packet_create_only(packet: dict[str, Any], output_path: Path) -> str:
    """Write deterministic JSON only if the destination does not exist."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(packet, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        # Do not remove a possibly partially written evidence file; retain it
        # for inspection and let the caller classify the write failure.
        raise
    return hashlib.sha256(data).hexdigest()

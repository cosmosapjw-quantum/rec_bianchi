#!/usr/bin/env python3
"""Original REI F05 source-volume to Thomson *local medium* bridge.

Output is physically sourced material data, not an admitted 161 history or LOS tau.
No REI owner source / solver modification, no new IVP or photon sky.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path

import numpy as np

INITIAL = "ORIGINAL_REI_F05_initial_material_state_z6.npz"
FORCING = "ORIGINAL_REI_F05_canonical_time_resolved_forcing_nodes.csv"
INITIAL_SHA = "7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d"
FORCING_SHA = "9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268"
SOURCE_SHA = "713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d"
PARENT_HEAD = "8c0170ba7d0b8a64b2acac981720e89efdf257ec"
REI_SOURCE_HEAD = "ea8d6bf94197392c69f939f03c1673ed3afe349c"
MPC_CM = Decimal("3.085677581491367e24")
C_CM_S = Decimal("29979245800")
SIGMA_T_CM2 = Decimal("6.6524587051e-25")
NODES = 46080

FIELDS = (
    "node",
    "original_native_proper_volume_cm3",
    "accepted_tick160_electron_density_lower_cm3",
    "accepted_tick160_electron_density_upper_cm3",
    "accepted_tick160_Thomson_rate_lower_s_inv",
    "accepted_tick160_Thomson_rate_upper_s_inv",
    "accepted_tick160_mean_free_path_lower_cm",
    "accepted_tick160_mean_free_path_upper_cm",
    "candidate_tick161_electron_density_lower_cm3",
    "candidate_tick161_electron_density_upper_cm3",
    "candidate_tick161_Thomson_rate_lower_s_inv",
    "candidate_tick161_Thomson_rate_upper_s_inv",
    "candidate_correlated_DeltaThomson_rate_lower_s_inv",
    "candidate_correlated_DeltaThomson_rate_upper_s_inv",
)

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def fmt(x: Decimal) -> str:
    # A deterministic, printed 18-digit decimal result, not directed MPFR rounding.
    return format(x, ".17E")

def parent_module(root: Path):
    path = root / "research/rec_rei_f05_tick161_thomson_capacity_20261101/capacity.py"
    sp = importlib.util.spec_from_file_location("rec_190_immutable_capacity", path)
    if sp is None or sp.loader is None:
        raise FileNotFoundError("MISSING_IMMUTABLE_PARENT_CODE")
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod

def force_z(path: Path, t0: float, t1: float) -> Decimal:
    with path.open(newline="", encoding="utf-8") as f:
        original = list(csv.DictReader(f))
    if len(original) != 85:
        raise ValueError("ORIGINAL_FORCING_ROW_COUNT")
    rows = [x for x in original if x.get("interval_index") == "0"]
    rows.sort(key=lambda x: int(x["node_index"]))
    if len(rows) != 17 or [int(x["node_index"]) for x in rows] != list(range(17)):
        raise ValueError("ORIGINAL_FIRST_FORCING_NODES")
    times = [float(x["time_s"]) for x in rows]
    if not (times[0] <= t0 < t1 <= times[-1]) or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("SOURCE_PROPER_TIME_CLOCK_NOT_COVERED")
    z = [Decimal(x["z_mid"]) for x in rows]
    if not all(zz == Decimal("5.95") for zz in z):
        raise ValueError("SOURCE_Z_NOT_CONSTANT_NATIVE_VOLUME_CHANGE_REQUIRED")
    # A PCHIP interpolation of constant source data is exactly constant.
    return z[0]

def source_inputs(unit: Path):
    unit = Path(unit).resolve()
    repo = unit.parents[1]
    parent = parent_module(repo)
    source = repo / "research/rec_rei_f05_tick161_thomson_capacity_20261101/source_inputs"
    parent_src, receipt, dt = parent.locked_inputs(repo / "research/rec_rei_f05_tick161_thomson_capacity_20261101")
    if sha(parent_src) != SOURCE_SHA:
        raise ValueError("IMMUTABLE_F05_46080_SOURCE_DRIFT")
    source_npz = unit / "source_inputs" / INITIAL
    source_forcing = unit / "source_inputs" / FORCING
    if sha(source_npz) != INITIAL_SHA or sha(source_forcing) != FORCING_SHA:
        raise ValueError("ORIGINAL_F05_VOLUME_OR_FORCING_SOURCE_DRIFT")
    t0 = float.fromhex(parent.T0_HEX)
    t1 = float.fromhex(parent.T1_HEX)
    z = force_z(source_forcing, t0, t1)
    return parent_src, source_npz, z, dt

def compute(unit: Path, out: Path) -> dict:
    unit = Path(unit).resolve()
    out = Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("NO_OVERWRITE_NONEMPTY_SCIENCE_OUTPUT")
    parent_csv, input_file, z, dt = source_inputs(unit)
    with np.load(input_file, allow_pickle=False) as original:
        if len(original["W_node"]) != NODES:
            raise ValueError("ORIGINAL_SOURCE_NODE_COUNT")
        w = np.asarray(original["W_node"], dtype=np.float64)
        nh = np.asarray(original["N_HI"] + original["N_HII"], dtype=np.float64)
        nhe = np.asarray(original["N_HeI"] + original["N_HeII"] + original["N_HeIII"], dtype=np.float64)
    if (not np.isfinite(w).all() or not np.isfinite(nh).all()
            or not np.isfinite(nhe).all() or np.any(w <= 0)
            or np.any(nh <= 0) or np.any(nhe <= 0)):
        raise ValueError("ORIGINAL_NATIVE_WEIGHTS_OR_NUCLEI_NOT_POSITIVE")
    if abs(float(np.sum(w)) - 1.0) > 2e-14:
        raise ValueError("ORIGINAL_NATIVE_NODE_WEIGHT_NORMALIZATION")
    s = C_CM_S * SIGMA_T_CM2
    zvol = (Decimal(1) + z) ** 3
    temp = io.StringIO(newline="")
    writer = csv.writer(temp, lineterminator="\n")
    writer.writerow(FIELDS)
    with localcontext() as ctx:
        ctx.prec = 90
        total_v = total_ne160_lo = total_ne160_hi = Decimal(0)
        total_ne161_lo = total_ne161_hi = Decimal(0)
        total_de_lo = total_de_hi = Decimal(0)
        squared160_lo = squared160_hi = Decimal(0)
        squared161_lo = squared161_hi = Decimal(0)
        min_ne160 = Decimal("Infinity")
        max_ne160 = Decimal(0)
        min_g160 = Decimal("Infinity")
        max_g160 = Decimal(0)
        count = 0
        with gzip.open(parent_csv, "rt", encoding="ascii", newline="") as fd:
            reader = csv.DictReader(fd)
            for row in reader:
                j = int(row["node"])
                if j != count or j >= NODES:
                    raise ValueError("ORIGINAL_SOURCE_NODE_IDENTITY")
                count += 1
                if float(row["source_H_nuclei_N_lower"]) != nh[j] or float(row["source_H_nuclei_N_upper"]) != nh[j]:
                    raise ValueError("ORIGINAL_H_NUCLEI_NOT_IDENTICAL")
                if float(row["source_He_nuclei_N_lower"]) != nhe[j] or float(row["source_He_nuclei_N_upper"]) != nhe[j]:
                    raise ValueError("ORIGINAL_HE_NUCLEI_NOT_IDENTICAL")
                V = Decimal.from_float(float(w[j])) * (MPC_CM ** 3) / zvol
                e0 = [Decimal(row["tick160_electron_count_N_lower"]),
                      Decimal(row["tick160_electron_count_N_upper"])]
                e1 = [Decimal(row["tick161_preview_electron_count_N_lower"]),
                      Decimal(row["tick161_preview_electron_count_N_upper"])]
                de = [Decimal(row["tick160_to_161_delta_electron_N_lower"]),
                      Decimal(row["tick160_to_161_delta_electron_N_upper"])]
                if (V <= 0 or e0[0] <= 0 or e0[0] > e0[1] or
                        e1[0] <= 0 or e1[0] > e1[1] or de[0] > de[1]):
                    raise ValueError("ORIGINAL_ELECTRON_DENSITY_INTERVAL_INVALID")
                if de[0] > e1[1] - e0[0] or de[1] < e1[0] - e0[1]:
                    raise ValueError("SOURCE_CORRELATED_INCREMENT_DISJOINT")
                n0 = [e / V for e in e0]
                n1 = [e / V for e in e1]
                g0 = [s * n for n in n0]
                g1 = [s * n for n in n1]
                dg = [s * x / V for x in de]
                l0 = [Decimal(1) / (SIGMA_T_CM2 * n0[1]),
                      Decimal(1) / (SIGMA_T_CM2 * n0[0])]
                if any(not x.is_finite() for x in [V, *n0, *n1, *g0, *g1, *dg, *l0]):
                    raise ValueError("NONFINITE_THOMSON_MEDIUM")
                writer.writerow([j, *[fmt(x) for x in
                    [V, *n0, *g0, *l0, *n1, *g1, *dg]]])
                total_v += V
                total_ne160_lo += e0[0]
                total_ne160_hi += e0[1]
                total_ne161_lo += e1[0]
                total_ne161_hi += e1[1]
                total_de_lo += de[0]
                total_de_hi += de[1]
                squared160_lo += e0[0] * e0[0] / V
                squared160_hi += e0[1] * e0[1] / V
                squared161_lo += e1[0] * e1[0] / V
                squared161_hi += e1[1] * e1[1] / V
                min_ne160 = min(min_ne160, n0[0])
                max_ne160 = max(max_ne160, n0[1])
                min_g160 = min(min_g160, g0[0])
                max_g160 = max(max_g160, g0[1])
        if count != NODES or not (total_de_hi < 0 and total_ne160_lo > 0):
            raise ValueError("SOURCE_PHYSICAL_CELL_COUNT_OR_GLOBAL_CHANGE")
        mean_n0 = [total_ne160_lo / total_v, total_ne160_hi / total_v]
        mean_n1 = [total_ne161_lo / total_v, total_ne161_hi / total_v]
        mean_g0 = [s * n for n in mean_n0]
        mean_g1 = [s * n for n in mean_n1]
        dmean_g = [s * x / total_v for x in [total_de_lo, total_de_hi]]
        clumping0 = [squared160_lo * total_v / total_ne160_hi ** 2,
                     squared160_hi * total_v / total_ne160_lo ** 2]
        clumping1 = [squared161_lo * total_v / total_ne161_hi ** 2,
                     squared161_hi * total_v / total_ne161_lo ** 2]
        if not (clumping0[0] > 1 and clumping1[0] > 1):
            raise ValueError("ORIGINAL_PHYSICAL_ELECTRON_CLUMPING_INVALID")
        parent_repo = unit.parents[1]
        source_result = json.loads(
            (parent_repo / "research/rec_rei_f05_tick161_thomson_capacity_20261101/results/SCIENCE_RESULT.json").read_text())
        # Physically independent new volume-normalization check against the
        # already frozen total-electron Thomson cross section (same material source).
        parent_area = [Decimal(v) for v in source_result["Thomson_scattering_area_161_cm2"]]
        new_area = [v * SIGMA_T_CM2 for v in [total_ne161_lo, total_ne161_hi]]
        for actual, prior in zip(new_area, parent_area):
            if abs(actual / prior - 1) > Decimal("5e-17"):
                raise ValueError("SOURCE_THOMSON_AREA_RECONCILIATION_FAILED")
        result = {
            "schema": "REC_REI_NATIVE_F05_CELL_VOLUME_THOMSON_MEDIUM_V1",
            "source_state": "ACCEPTED_TICK160_AND_CANDIDATE_TICK161_NOT_OFFICIAL",
            "source_repo": "cosmosapjw-quantum/rei_bianchi",
            "source_pr": 352, "original_source_head": REI_SOURCE_HEAD,
            "rec_immutable_parent_head": PARENT_HEAD,
            "original_init_npz_sha256": INITIAL_SHA,
            "original_forcing_csv_sha256": FORCING_SHA,
            "original_candidate_csv_sha256": SOURCE_SHA,
            "node_count": NODES, "original_first_interval_z": str(z),
            "original_source_volume_prescription": "W_node*MPC_CM^3/(1+z_source)^3",
            "source_forcing_geometry": "ORIGINAL_F05_ISOTROPIC_VOLUME_PRESCRIPTION_NOT_BIANCHI_LOS",
            "original_proper_tick_s": fmt(dt),
            "total_native_proper_volume_cm3": fmt(total_v),
            "original_native_volume_weight_sum": fmt(sum(map(Decimal.from_float, w))),
            "accepted_160_volume_weighted_mean_electron_density_cm3": [fmt(x) for x in mean_n0],
            "candidate_161_volume_weighted_mean_electron_density_cm3": [fmt(x) for x in mean_n1],
            "accepted_160_volume_weighted_mean_Thomson_rate_s_inv": [fmt(x) for x in mean_g0],
            "candidate_161_volume_weighted_mean_Thomson_rate_s_inv": [fmt(x) for x in mean_g1],
            "candidate_correlated_Delta_mean_Thomson_rate_s_inv": [fmt(x) for x in dmean_g],
            "accepted_160_source_electron_clumping_factor": [fmt(x) for x in clumping0],
            "candidate_161_source_electron_clumping_factor": [fmt(x) for x in clumping1],
            "accepted_160_local_electron_density_extrema_cm3": [fmt(min_ne160), fmt(max_ne160)],
            "accepted_160_local_Thomson_rate_extrema_s_inv": [fmt(min_g160), fmt(max_g160)],
            "accepted_160_homogeneous_effective_mean_free_path_cm":
                [fmt(Decimal(1) / (SIGMA_T_CM2 * mean_n0[1])),
                 fmt(Decimal(1) / (SIGMA_T_CM2 * mean_n0[0]))],
            "decimal_status": "SOURCE_CONDITIONAL_DECIMAL_REPRESENTATION_NOT_FORMAL_MPFR_ENCLOSURE",
            "original_worker_legacy_logT_fail": "2.1245050576368385e-4 >2e-4",
            "rei_v2_shadow_logT": "5.387144148931529e-6 <2e-4_NOT_OFFICIALLY_ACCEPTED",
            "observed_LoS_tau": "NOT_COMPUTED",
            "observed_CMB_Stokes": "NOT_COMPUTED",
            "accepted_history": "160/131072",
            "rei_canonical_DAG": "28/88", "rei_working_DAG": "33/88",
            "rei_physical_fast_DAG": "4/7", "rec_H5_physical_DAG": "0/313",
            "canonical_delta": 0, "production": "HOLD", "auto_next": False,
        }
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "SOURCE_NATIVE_THOMSON_MEDIUM_46080.csv.gz"
    with csv_path.open("xb") as sink:
        with gzip.GzipFile(fileobj=sink, mode="wb", mtime=0, filename="", compresslevel=6) as gz:
            gz.write(temp.getvalue().encode("ascii"))
    result["native_medium_csv_gzip_sha256"] = sha(csv_path)
    (out / "SCIENCE_RESULT.json").write_text(
        json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({k:result[k] for k in [
        "accepted_160_volume_weighted_mean_electron_density_cm3",
        "accepted_160_volume_weighted_mean_Thomson_rate_s_inv",
        "accepted_160_source_electron_clumping_factor",
        "candidate_correlated_Delta_mean_Thomson_rate_s_inv",
        "native_medium_csv_gzip_sha256"]}, sort_keys=True))
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--unit-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    compute(args.unit_root, args.out)

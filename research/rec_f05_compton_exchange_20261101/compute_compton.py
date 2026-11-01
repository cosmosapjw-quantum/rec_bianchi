#!/usr/bin/env python3
"""Original accepted REI F05 H/He cell electron/temperature -> local CMB Compton budget.

Source-conditioned instantaneous physics. No time-integrated Compton energy,
Einstein-Bianchi photon rays, official F05 advancement, or production mutation.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import numpy as np

# Fixed cgs constants and explicitly CONDITIONAL isotropic blackbody at z=5.95.
C_CGS = 29979245800.0
SIGMA_T = 6.6524587051e-25
K_B = 1.380649e-16
M_E = 9.1093837139e-28
A_RAD = 7.5657e-15
T_CMB0 = 2.728
CELLS = 46080
PARENT = "research/rec_rei_f05_accepted_history_thomson_20261101"
SOURCE_ORIGINAL_TAR = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source_loader(repo: Path):
    p = repo / PARENT / "compute_accepted160.py"
    spec = importlib.util.spec_from_file_location("rec192_locked_original", p)
    if spec is None or spec.loader is None:
        raise RuntimeError("unavailable immutable REC192 source loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compton_power_interval(ne_lo, ne_hi, t_lo, t_hi, t_gamma):
    """Corner enclosure of Q=4 sigma_T a_r Tgamma^4 kB Ne (Tgamma-Te)/(me c)."""
    if not (0 < t_gamma and np.isfinite(t_gamma)):
        raise ValueError("invalid blackbody temperature")
    for a in (ne_lo, ne_hi, t_lo, t_hi):
        if np.any(~np.isfinite(a)) or np.any(a <= 0):
            raise ValueError("nonpositive or nonfinite source interval")
    if np.any(ne_lo > ne_hi) or np.any(t_lo > t_hi):
        raise ValueError("inverted source interval")
    coeff = 4 * SIGMA_T * A_RAD * t_gamma**4 * K_B / (M_E * C_CGS)
    corners = np.stack([
        coeff * ne * (t_gamma - temp)
        for ne in (ne_lo, ne_hi) for temp in (t_lo, t_hi)
    ])
    return np.min(corners, axis=0), np.max(corners, axis=0)


def scientific_computation(repo: Path, out: Path):
    repo, out = Path(repo).resolve(), Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("refuse to overwrite science output")
    loader = source_loader(repo)
    unit = repo / PARENT
    initial, states, z, t160, timeline, terminal = loader.input_sources(unit)
    if loader.TAR_SHA != SOURCE_ORIGINAL_TAR or int(z * 100) != 595:
        raise ValueError("locked original source changed")
    if terminal["status"] != "BLOCKED_MINIMUM_STEP":
        raise ValueError("original F05 terminal condition changed")
    poplo, pophi, loglo, loghi = states
    if poplo.shape != (CELLS, 5) or loglo.shape != (CELLS,):
        raise ValueError("original F05 cell dimensions changed")
    with np.load(initial, allow_pickle=False) as a:
        init = np.stack([a[k] for k in
            ("N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII")], axis=1)
    if init.shape != (CELLS, 5) or not np.isfinite(init).all():
        raise ValueError("invalid original initial species")
    n_h = init[:, 0] + init[:, 1]
    n_he = init[:, 2] + init[:, 3] + init[:, 4]
    ne_lo = poplo[:, 1] + poplo[:, 3] + 2 * poplo[:, 4]
    ne_hi = pophi[:, 1] + pophi[:, 3] + 2 * pophi[:, 4]
    t_lo, t_hi = np.exp(loglo), np.exp(loghi)
    t_gamma = T_CMB0 * (1 + float(z))
    q_lo, q_hi = compton_power_interval(ne_lo, ne_hi, t_lo, t_hi, t_gamma)
    if np.any(q_hi >= 0):
        raise ValueError("source cooling sign no longer uniformly negative")
    u_lo = 1.5 * K_B * t_lo * (n_h + n_he + ne_lo)
    u_hi = 1.5 * K_B * t_hi * (n_h + n_he + ne_hi)
    if not (np.isfinite(u_lo).all() and np.all(u_lo > 0) and
            np.all(u_lo <= u_hi)):
        raise ValueError("invalid gas kinetic energy enclosure")
    tick_seconds = float(t160) / 160
    if not tick_seconds > 0:
        raise ValueError("invalid source time measure")
    # Physics: frozen-endpoint diagnostic only; NOT the integrated actual heating.
    f_lo = -q_hi * tick_seconds / u_hi
    f_hi = -q_lo * tick_seconds / u_lo
    if np.any(f_lo < 0) or np.any(f_lo > f_hi):
        raise ValueError("invalid source conditional cooling fraction")

    out.mkdir(parents=True, exist_ok=True)
    path = out / "ORIGINAL_F05_COMPTON_46080.csv.gz"
    with path.open("xb") as sink:
        with gzip.GzipFile(fileobj=sink, mode="wb", filename="", mtime=0,
                           compresslevel=6) as g:
            with io.TextIOWrapper(g, encoding="ascii", newline="", write_through=True) as f:
                wr = csv.writer(f, lineterminator="\n")
                wr.writerow(("node", "N_e_lower", "N_e_upper", "T_e_lower_K",
                             "T_e_upper_K", "Compton_Q_lower_erg_s",
                             "Compton_Q_upper_erg_s", "U_gas_lower_erg",
                             "U_gas_upper_erg", "frozen_tick_frac_lower",
                             "frozen_tick_frac_upper"))
                for j in range(CELLS):
                    wr.writerow((j, *(format(float(a[j]), ".17e") for a in
                        (ne_lo, ne_hi, t_lo, t_hi, q_lo, q_hi, u_lo, u_hi, f_lo, f_hi))))
    def s(a): return math.fsum(map(float, a))
    qtotal = [s(q_lo), s(q_hi)]
    utotal = [s(u_lo), s(u_hi)]
    fraction = [-qtotal[1] * tick_seconds / utotal[1],
                -qtotal[0] * tick_seconds / utotal[0]]
    original_rust = json.loads((repo / "research/rec_f05_rust_native_20261101/results/RUST_SCIENCE_RESULT.json").read_text())
    for source, actual in zip(
        (original_rust["accepted_lower_total_electron"],
         original_rust["accepted_upper_total_electron"]),
        (s(ne_lo), s(ne_hi))
    ):
        if abs(source - actual) / source > 2e-14:
            raise ValueError("REC193 native Rust source electron parity failed")
    result = {
        "schema": "REC_F05_ORIGINAL_ACCEPTED_COMPTON_CMB_BATH_DIAGNOSTIC_V1",
        "source_tar_sha256": SOURCE_ORIGINAL_TAR,
        "source_initial_sha256": loader.INIT_SHA,
        "source_accepted_array_sha256": loader.ORIGINAL_ARRAY_SHA,
        "original_accepted_tick": 160,
        "total_source_ticks": 131072,
        "source_cells": CELLS,
        "source_z": float(z),
        "source_time_tick_s": tick_seconds,
        "source_accepted_history": timeline,
        "isotropic_blackbody_Tcmb0_K": T_CMB0,
        "source_blackbody_Tgamma_K": t_gamma,
        "assumptions": ["single Maxwellian electron/gas kinetic temperature",
                        "Thomson nonrelativistic Kompaneets energy exchange",
                        "isotropic blackbody Tgamma=T0(1+z) OPTIONAL_CMB_BATH",
                        "proper-source-time tick frozen at accepted160",
                        "zero new source IVPs"],
        "Compton_Q_erg_s_enclosure": qtotal,
        "gas_kinetic_U_erg_enclosure": utotal,
        "frozen_one_tick_kinetic_energy_fraction_enclosure": fraction,
        "local_T_K_enclosure": [float(np.min(t_lo)), float(np.max(t_hi))],
        "all_cells_cooling": True,
        "source_rows_csv_sha256": digest(path),
        "status": "SOURCE_CONDITIONAL_INSTANTANEOUS_PHYSICS_NOT_CONTINUOUS_COUPLED_IVP",
        "official_F05_next_tick": "161_NOT_ACCEPTED",
        "reionization_source_owner_change": False,
        "REI_canonical_DAG": "28/88",
        "REI_working_DAG": "33/88",
        "REC_H5_physical_DAG": "0/313",
        "production": "HOLD",
    }
    (out / "SCIENCE_RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in
        ("source_rows_csv_sha256", "Compton_Q_erg_s_enclosure",
         "frozen_one_tick_kinetic_energy_fraction_enclosure")}, sort_keys=True))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    scientific_computation(a.repo, a.out)

#!/usr/bin/env python3
"""Re-evaluate the saved original tick142 rays, without a new native IVP."""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import json
import sys
import numpy as np

BASE = Path(__file__).resolve().parent
OLD = BASE.parent / "rec_f08_native_thomson_polarization_20261115"
REPAIR = BASE.parent / "rec_tetrad_thomson_repair_20261116"
sys.path[:0] = [str(OLD), str(REPAIR)]
from angular_quadrupole_systematics import quadrupole_fit
from thomson_l4 import weights_l4, quadrupole
from thomson_tetrad import tetrad_grid, physical_weights

def design(n):
    return np.column_stack((np.ones(len(n)), n, n[:, 0]**2-n[:, 2]**2,
                           n[:, 1]**2-n[:, 2]**2, n[:, 0]*n[:, 1],
                           n[:, 0]*n[:, 2], n[:, 1]*n[:, 2]))

def centered_fit(n, intensity):
    coef = np.linalg.lstsq(design(n), intensity/intensity.mean()-1, rcond=None)[0]
    a,b,c,d,e = coef[4:]
    return 2*np.array([[a,c/2,d/2],[c/2,b,e/2],[d/2,e/2,-a-b]])/(15*(1+coef[0]))

def main(out):
    source = OLD / "source_inputs/ORIGINAL_NATIVE_F08_640STEP_128RAY_PHOTON_ANGLES.csv.gz"
    qfile = OLD / "source_inputs/F08_ORIGINAL_SOURCE_Q128.csv"
    q = np.loadtxt(qfile, delimiter=",", skiprows=1)[:,1:]
    with gzip.open(source, "rt") as f:
        rows = [r for r in csv.DictReader(f) if r["branch"] == "S0_BI" and
                r["model"] == "ORIGINAL_HAT" and int(r["step"]) == 142]
    if len(rows) != 128:
        raise ValueError("original 128-ray tick142 identity")
    values = np.array([float(r["original_photons_per_H"]) for r in rows])
    w2 = (1+(4/63)*(q[:,2]**2-21/64))/128
    old = quadrupole_fit(q, w2, values, design(q))
    original_report = json.loads((OLD/"results/SYSTEMATIC_RESULT.json").read_text())
    preserved = original_report["method_gate_failed_observations"][0]
    if not (old[3] >= .03 and preserved["relative_method_difference"] >= .03):
        raise ValueError("original 3 percent failure unexpectedly changed")
    q4 = quadrupole(q, weights_l4(q), values)
    qfit = centered_fit(q, values)
    H = np.array([1.01e-14,.99e-14,1e-14])
    t = float(rows[0]["proper_t_s"])
    n,J = tetrad_grid(q,H,t)
    intensity = values/J
    p4 = quadrupole(n, physical_weights(q,n,J,4), intensity)
    p6 = quadrupole(n, physical_weights(q,n,J,6), intensity)
    pfit = centered_fit(n,intensity)
    result = {
        "schema": "REC_F08_ORIGINAL_TICK142_REUSE_DIAGNOSTIC_V1",
        "original_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "original_q_sha256": hashlib.sha256(qfile.read_bytes()).hexdigest(),
        "source_rows": 128, "native_IVP_reexecutions": 0,
        "time_s": t, "source_H_per_s": H.tolist(),
        "historical_failure": preserved,
        "recomputed_old_q_l2_norm": old[0],
        "recomputed_old_q_fit_norm": old[1],
        "recomputed_old_q_absolute_difference": old[2],
        "recomputed_old_q_relative_disagreement": old[3],
        "old_threshold": .03, "old_gate": "FAIL_REPRODUCED_AND_PRESERVED",
        "q_degree4_vs_fit_relative": float(np.linalg.norm(q4-qfit)/np.linalg.norm(q4)),
        "physical_degree4_norm": float(np.linalg.norm(p4)),
        "physical_degree4_vs_fit_relative": float(np.linalg.norm(p4-pfit)/np.linalg.norm(p4)),
        "physical_degree4_vs_degree6_relative": float(np.linalg.norm(p4-p6)/np.linalg.norm(p4)),
        "interpretation": "REUSE_PR200_PHYSICAL_FRAME_AND_DEGREE4_CORRECTION; NO_RETROACTIVE_GATE_PASS",
        "canonical_DAG_delta": 0,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--out", type=Path, required=True)
    main(p.parse_args().out)

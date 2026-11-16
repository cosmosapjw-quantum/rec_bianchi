#!/usr/bin/env python3
"""Persistent polarized photon evolution through original F08 paired_runtime.

Each macro step consumes the actual two accepted native half-step audits,
advances the same Stokes state through transport/source/absorption, and then
applies an endpoint-electron Thomson Lie split.  Its I output is fed into
the next original Rust paired trial.  This is a point receiver; photon boxes
are reset on feedback and no cumulative interval certificate is asserted.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

from receiver import collision_stage, cone_diagnostics, tetrad_grid, physical_weights
from transport import advance_native_endpoint

BASE = Path(__file__).resolve().parent
DT = 625000000.0
FINAL_T = 160 * DT
SOURCE_Q_SHA = "a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92"

def require(ok, why):
    if not ok:
        raise ValueError(why)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class Bridge:
    def __init__(self, binary, geometry, log):
        self.err = Path(log).open("w")
        self.p = subprocess.Popen([str(binary), geometry], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=self.err, text=True, bufsize=1)
        self.first = self.receive()

    def receive(self):
        line = self.p.stdout.readline()
        require(bool(line), "native bridge ended without a result")
        result = json.loads(line)
        require(result.get("status") == "OK", "native paired failure: " + line[:2000])
        return result

    def step(self, dt, feedback=None):
        if feedback is None:
            request = "STEP|" + format(dt, ".17g")
        else:
            stokes, gn, gu = feedback
            values = (stokes[..., 0].T.ravel(), gn[:, 0], gu[:, 0])
            request = "FEEDBACK|" + format(dt, ".17g") + "|" + "|".join(
                ",".join(format(float(x), ".17g") for x in a) for a in values)
        self.p.stdin.write(request + "\n")
        self.p.stdin.flush()
        return self.receive()

    def close(self):
        if self.p.poll() is None:
            self.p.stdin.write("QUIT\n")
            self.p.stdin.flush()
            self.p.stdin.close()
        code = self.p.wait(timeout=20)
        self.err.close()
        require(code == 0, "native bridge exit " + str(code))

def physical_observer(stokes, gn, q, H, t):
    n, J = tetrad_grid(q, H, t)
    w = physical_weights(q, n, J, 4)
    all_s = np.concatenate((stokes, gn[None]), axis=0)
    m = all_s * (w / J)[None, :, None]
    old = all_s[..., 0].sum(axis=1)
    projected = m[..., 0].sum(axis=1)
    factor = np.divide(old, projected, out=np.zeros_like(old), where=projected > 0)
    sky = np.sum(m * factor[:, None, None], axis=0)
    total = float(sky[:, 0].sum())
    pol = np.hypot(sky[:, 1], sky[:, 2])
    qten = np.einsum("i,ia,ib->ab", sky[:, 0] - total * w, n, n) / total
    return {
        "physical_peak_linear_fraction": float(np.max(pol / sky[:, 0])),
        "physical_integrated_linear_fraction": float(pol.sum() / total),
        "physical_number_quadrupole_norm": float(np.linalg.norm(qten)),
        "physical_abs_circular_fraction": float(np.abs(sky[:, 3]).sum() / total),
    }, sky

def run_case(binary, out, geometry, steps, degree, scatter):
    name = f"{geometry}_{'thomson_l'+str(degree) if scatter else 'native_control'}_{steps}"
    case = out / name
    case.mkdir()
    started = time.perf_counter()
    bridge = Bridge(binary, geometry, case / "native_stderr.log")
    initial = bridge.first
    q = np.array(initial["q128"], float)
    nodes = np.array(initial["energy_nodes"], float)
    H = np.array(initial["h_per_s"], float)
    require(q.shape == (128, 3) and len(nodes) == 17, "original source grid")
    source_q_path = BASE.parent / "rec_f08_native_thomson_polarization_20261115/source_inputs/F08_ORIGINAL_SOURCE_Q128.csv"
    require(digest(source_q_path) == SOURCE_Q_SHA, "original source q identity")
    source_q = np.loadtxt(source_q_path, delimiter=",", skiprows=1)[:, 1:]
    require(np.max(abs(source_q - q)) < 3e-15, "native q semantics differ from preserved source")
    stokes = np.zeros((len(nodes), 128, 4))
    stokes[..., 0] = np.array(initial["photons"]).reshape(128, len(nodes)).T
    gn = np.zeros((128, 4)); gu = np.zeros((128, 4))
    gn[:, 0] = initial["lower_guard_n"]; gu[:, 0] = initial["lower_guard_u"]
    dt = FINAL_T / steps
    rows = []
    snapshots = []
    guard_ns = []; guard_us = []
    total_tau = 0.0
    total_scatter = 0.0
    max_parity = 0.0
    last = initial
    try:
        for k in range(1, steps + 1):
            native = bridge.step(dt, (stokes, gn, gu) if scatter and k > 1 else None)
            require(native["time_s"] == k * dt, "native proper clock disagreement")
            require(len(native["audits"]) == 3, "full/half/half native audits")
            # Only the two accepted half steps advance the persistent state.
            for audit in native["audits"][1:]:
                stokes, gn, gu, _ = advance_native_endpoint(stokes, gn, gu, q, H, nodes, audit)
            authoritative = np.array(native["photons"]).reshape(128, len(nodes)).T
            discrepancies = [np.abs(stokes[..., 0] - authoritative).sum(),
                             np.abs(gn[:, 0] - native["lower_guard_n"]).sum(),
                             np.abs(gu[:, 0] - native["lower_guard_u"]).sum() / 13.7]
            parity = float(max(discrepancies) / native["photon_N"])
            max_parity = max(max_parity, parity)
            if parity >= 256 * np.finfo(float).eps:
                (case / "FAILED_NATIVE_WITNESS.json").write_text(json.dumps(native) + "\n")
                (case / "FAILURE.json").write_text(json.dumps({
                    "class": "implementation_or_arithmetic", "step": k,
                    "observed_parity": parity, "criterion": 256 * np.finfo(float).eps,
                    "threshold_unchanged": True}) + "\n")
                raise ValueError(f"Stokes/native accepted-half transport parity step={k} observed={parity:.17g}")
            # Same solution, native arithmetic ordering: retain native I bytes.
            stokes[..., 0] = authoritative
            gn[:, 0] = native["lower_guard_n"]; gu[:, 0] = native["lower_guard_u"]
            stokes, gn, gu, collision = collision_stage(
                stokes, gn, gu, q, H, native["gas"], native["time_s"], dt,
                degree=degree, sigma_scale=1.0 if scatter else 0.0)
            total_tau += collision["tau"]
            total_scatter += collision["tau"] * native["photon_N"]
            obs, _ = physical_observer(stokes, gn, q, H, native["time_s"])
            floor = 13.7 * math.exp(-float(max(H)) * native["time_s"])
            forbidden = float(stokes[nodes < floor, :, 0].sum() + gn[:, 0].sum())
            row = {"geometry": geometry, "step": k, "time_s": native["time_s"],
                   "dt_s": dt, "scatter": scatter, "degree": degree,
                   "xHII": native["gas"][0], "xHeII": native["gas"][1], "xHeIII": native["gas"][2],
                   "T_K": native["temperature"], "gas_w_eV_per_H": native["gas"][3],
                   "N_photons_per_H": native["photon_N"], "U_photons_eV_per_H": native["photon_U"],
                   "source_N_per_H": native["source_n"], "absorbed_N_per_H": native["absorbed_n"],
                   "redshift_work_eV_per_H": native["redshift_work"],
                   "thermal_work_eV_per_H": native["thermal_work"],
                   "global_N_residual": native["global_N_residual"],
                   "global_E_residual": native["global_E_residual"],
                   "native_local_bound": native["local_bound"],
                   "native_public_width": native["public_width"], "native_max_ledger": native["max_ledger"],
                   "native_transport_parity_relative": parity,
                   "photon_interval_reset_count": native["photon_interval_reset_count"],
                   "forbidden_support_fraction": forbidden / native["photon_N"],
                   "tau_total": total_tau, "tau_weighted_photon_exposure_per_H": total_scatter,
                   **obs, **collision}
            rows.append(row)
            snapshots.append(stokes.copy()); guard_ns.append(gn.copy()); guard_us.append(gu.copy())
            if k in (1, steps):
                (case / f"native_witness_{k:04d}.json").write_text(json.dumps(native) + "\n")
            if k == 1 or k % 32 == 0 or k == steps:
                print(json.dumps({"case": name, "step": k,
                                  "P_over_I": obs["physical_peak_linear_fraction"],
                                  "ledger": native["max_ledger"], "parity": parity}), flush=True)
            last = native
    finally:
        bridge.close()
    with (case / "trajectory.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    np.savez_compressed(case / "stokes_history.npz", stokes=np.stack(snapshots),
                        guard_n=np.stack(guard_ns), guard_u=np.stack(guard_us),
                        nodes=nodes, q=q, H=H, dt=dt)
    summary = {
        "case": name, "original_paired_trials": steps, "original_native_endpoints": 3 * steps,
        "accepted_native_half_endpoints": 2 * steps, "persistent_polarized_steps": steps if scatter else 0,
        "physical_spectral_stokes_rows": steps * 128 * len(nodes),
        "native_transport_parity_max_relative": max_parity,
        "photon_interval_reset_count": last["photon_interval_reset_count"],
        "cumulative_interval_certificate": "NOT_CLAIMED_PHOTON_POINT_REINITIALIZATION",
        "max_native_local_bound": max(r["native_local_bound"] for r in rows),
        "max_native_public_width": max(r["native_public_width"] for r in rows),
        "max_native_ledger": max(r["native_max_ledger"] for r in rows),
        "max_global_N_residual": max(abs(r["global_N_residual"]) for r in rows),
        "max_global_E_residual": max(abs(r["global_E_residual"]) for r in rows),
        "max_collision_group_number_relative": max(r["max_group_number_relative"] for r in rows),
        "max_inverse_projection_raw_relative_drift": max(r["max_inverse_projection_raw_relative_drift"] for r in rows),
        "max_effective_extra_extinction": max(r["max_effective_extra_extinction"] for r in rows),
        "max_stokes_cone_violation_scaled": max(r["max_stokes_cone_violation_scaled"] for r in rows),
        "final": rows[-1], "wall_s": time.perf_counter() - started,
        "source_measure_adapter": "CONDITIONAL_NONLINEAR_PER_PHYSICAL_ENERGY_NORMALIZED_COLLOCATION",
        "operator_split": "ENDPOINT_NE_POST_NATIVE_LIE_SPLIT",
        "fixed_hat_support_status": "FAIL_RETAINED",
        "owner_admission": "HOLD", "canonical_DAG_delta": 0,
    }
    (case / "RESULT.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--steps", type=int, default=160)
    p.add_argument("--geometry", choices=("S0_BI", "S0_FLRW"), default="S0_BI")
    p.add_argument("--degree", type=int, choices=(4, 6), default=4)
    p.add_argument("--control", action="store_true")
    a = p.parse_args()
    require(a.steps >= 1 and a.steps <= 640, "bounded physical duration/refinement")
    a.out.mkdir(parents=True, exist_ok=True)
    summary = run_case(a.binary, a.out, a.geometry, a.steps, a.degree, not a.control)
    print(json.dumps(summary), flush=True)

if __name__ == "__main__":
    main()

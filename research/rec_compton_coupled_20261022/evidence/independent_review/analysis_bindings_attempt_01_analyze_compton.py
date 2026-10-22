"""Analyze the eight completed Compton cases without invoking an ODE."""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from scipy.integrate import simpson

import run_compton as runner
from run_compton import (UNIT, REPO, THERMAL, CASES, SEEDS, BRANCHES, SIGNED_NAMES,
                         label_for, digest, save_json, save_npz, verify_outputs)
from compton_budget import EV_J, KB_J_K, MEC2_J, SIGMA_T_C_M3_S
from analyze_collisions import analyze_case as analyze_collision_case

ENERGY_FIELDS = (
    ("photo_primary", "photo_primary_W_m3", 1),
    ("rr_kinetic", "rr_cooling_W_m3", -1),
    ("dr_kinetic", "dr_cooling_W_m3", -1),
    ("photo_absorbed", "photo_absorbed_W_m3", 1),
    ("total_escape", "total_escape_W_m3", -1),
    ("compton_selected", "compton_selected_W_m3", 1),
    ("compton_actual_hot", "compton_actual_hot_W_m3", 1),
    ("compton_planck_reference", "compton_planck_reference_W_m3", 1),
    ("compton_uv", "compton_uv_W_m3", 1),
    ("compton_uv_recoil", "compton_uv_recoil_W_m3", 1),
    ("compton_uv_thermal", "compton_uv_thermal_W_m3", 1),
)


def read_npz(path):
    with np.load(path, allow_pickle=False) as a:
        return {key: a[key].copy() for key in a.files}


def diag_map(arrays):
    return {name: arrays["diagnostics"][:, i] for i, name in enumerate(arrays["diagnostic_names"].tolist())}


def source_identity(runtime_id):
    paths = [UNIT / "code" / n for n in ("analyze_compton.py", "analyze_collisions.py")]
    files = {str(p.relative_to(UNIT)): digest(p) for p in paths}
    identity = hashlib.sha256(json.dumps(dict(files=files, runtime_identity=runtime_id),
                                        sort_keys=True).encode()).hexdigest()
    return identity, files


def no_ode(*args, **kwargs):
    raise RuntimeError("ANALYSIS_ODE_GUARD")


def run(source, output):
    start, cpu = time.perf_counter(), time.process_time()
    source, output = Path(source).resolve(), Path(output).resolve()
    if source != (UNIT / "results/compton8").resolve():
        raise ValueError("FROZEN_INPUT_CAMPAIGN_REQUIRED")
    runtime_id, runtime_files = runner.source_identity()
    lock = json.loads((source / "CAMPAIGN_LOCK.json").read_text())
    refinement = json.loads((source / "REFINEMENT.json").read_text())
    if lock["source_identity"] != runtime_id or refinement["status"] != "PASS":
        raise ValueError("CAMPAIGN_SOURCE_OR_REFINEMENT_NOT_ADMITTED")
    identity, files = source_identity(runtime_id)
    output.mkdir(parents=True, exist_ok=False)
    save_json(output / "STARTED.json", dict(started_utc=datetime.now(timezone.utc).isoformat(),
              source_identity=identity, source_files=files, runtime_identity=runtime_id,
              new_ODE_integrations=0, old_IVP_reruns=0, command=sys.argv))
    # This process only consumes immutable arrays.
    runner.solve_ivp = no_ode
    import scipy.integrate
    scipy.integrate.solve_ivp = no_ode

    inputs = runner.load_inputs()
    summaries, data, sources, table = {}, {}, [], []
    for spec in CASES:
        label = label_for(*spec)
        seed, branch, refined = spec
        folder = source / label
        receipt = json.loads((folder / "RESULT.json").read_text())
        if receipt["status"] != "COMPLETE" or receipt["source_identity"] != runtime_id:
            raise ValueError("INPUT_NOT_COMPLETE:" + label)
        verify_outputs(folder, receipt)
        current = read_npz(folder / "trajectory.npz")
        dense = read_npz(folder / "dense_1025.npz")
        old = inputs[seed]["cases"][refined]["arrays"]
        if not np.array_equal(current["x"], old["x"]) or not np.array_equal(current["initial_state"], old["initial_state"]):
            raise ValueError("MATCHED_BASELINE_GRID_OR_INITIAL_CHANGED:" + label)
        c, d, b = diag_map(current), diag_map(dense), diag_map(old)
        dx = current["raw_state"] - old["raw_state"]
        ds = current["signed_observables"] - old["signed_observables"]
        dT = current["T_K"] - old["T_K"]
        dtau = current["raw_state"][:, 61] - old["raw_state"][:, 61]
        caseout = output / label
        caseout.mkdir()
        energy_integrands = np.column_stack(
            [sign * d[field] / (d["nb_m3"] * d["H_s"] * EV_J) for _, field, sign in ENERGY_FIELDS] +
            [-d["work_J_per_baryon_per_x"] / EV_J])
        energy_names = [name for name, _, _ in ENERGY_FIELDS] + ["expansion_work"]
        energy = dict(zip(energy_names, simpson(energy_integrands, x=dense["x"], axis=0).tolist()))
        K = SIGMA_T_C_M3_S / MEC2_J
        density_replacement = -4 * K * d["ne_m3"] * KB_J_K * dense["T_K"] * (
            d["U_planck_reference_J_m3"] - d["U_gamma_actual_J_m3"])
        reference_recoil = 4 * K * d["ne_m3"] * KB_J_K * d["U_planck_reference_J_m3"] * d["T_planck_reference_K"]
        difference = d["compton_planck_reference_W_m3"] - d["compton_actual_hot_W_m3"]
        residual = difference - density_replacement - reference_recoil
        scaled = abs(residual) / np.maximum(abs(difference) + abs(density_replacement) + abs(reference_recoil), 1e-300)
        if scaled.max() > 1e-10:
            raise ValueError("SOURCE_OWNER_DECOMPOSITION_FAILED:" + label)
        collision_summary = analyze_collision_case(folder, caseout / "collisions")
        optical_increment_old = float(old["raw_state"][-1, 61] - old["raw_state"][0, 61])
        summary = dict(
            label=label, seed=seed, branch=branch, refined=refined,
            baseline_label=inputs[seed]["cases"][refined]["identity"]["label"],
            temperature_end_K=float(current["T_K"][-1]),
            baseline_temperature_end_K=float(old["T_K"][-1]),
            delta_temperature_end_K=float(dT[-1]),
            delta_temperature_end_percent=float(100 * dT[-1] / old["T_K"][-1]),
            peak_temperature_109_K=float(current["T_K"].max()),
            peak_temperature_1025_K=float(dense["T_K"].max()),
            max_abs_delta_lnT_109=float(abs(dx[:, 62]).max()),
            max_abs_delta_conditional_fraction_109=float(abs(dx[:, 40:61]).max()),
            max_abs_delta_signed_six_109=float(abs(ds).max()),
            max_abs_delta_signed_stress_only_109=float(abs(ds[:, 1:]).max()),
            signed_endpoint=current["signed_observables"][-1],
            signed_endpoint_minus_baseline=ds[-1],
            conditional_ion_fraction_endpoint=current["raw_state"][-1, 40:61],
            conditional_ion_fraction_endpoint_minus_baseline=dx[-1, 40:61],
            tau_end=float(current["raw_state"][-1, 61]), delta_tau_end=float(dtau[-1]),
            delta_tau_end_percent_of_cumulative=float(100 * dtau[-1] / old["raw_state"][-1, 61]),
            delta_tau_end_percent_of_restart_increment=float(100 * dtau[-1] / optical_increment_old),
            electron_density_end_m3=float(c["ne_m3"][-1]),
            delta_electron_density_end_m3=float(c["ne_m3"][-1] - b["ne_m3"][-1]),
            elapsed_Myr_start=float(c["elapsed_Myr"][0]), elapsed_Myr_end=float(c["elapsed_Myr"][-1]),
            primary_energy_grid="dense1025 Simpson; actual evolved path",
            energy_eV_per_baryon=energy,
            source_owner_decomposition_max_scaled=float(scaled.max()),
            source_owner_decomposition_eV_per_baryon=dict(
                density_replacement=float(simpson(density_replacement / (d["nb_m3"] * d["H_s"] * EV_J), x=dense["x"])),
                reference_recoil=float(simpson(reference_recoil / (d["nb_m3"] * d["H_s"] * EV_J), x=dense["x"]))),
            gas_integral_residual_scaled=receipt["energy_integrals"]["dense_1025"]["residual_scaled"],
            gas_integral_513_1025_delta_scaled=receipt["energy_grid_delta_scaled"],
            max_backreaction_ratio=receipt["energy_integrals"]["dense_1025"]["max_backreaction_ratio"],
            backreaction_ratio_integral=receipt["energy_integrals"]["dense_1025"]["backreaction_ratio_integral"],
            max_trace_energy_fraction=max(s["metrics"]["max_trace_energy_fraction"] for s in receipt["admission"].values()),
            collisions=collision_summary,
            runtime=dict(wall_seconds=receipt["wall_seconds"], own_cpu_seconds=receipt["own_cpu_seconds"],
                         integration_wall_seconds=receipt["integration_wall_seconds"],
                         diagnostics_and_persistence_wall_seconds=receipt["diagnostics_and_persistence_wall_seconds"],
                         nfev=receipt["nfev"], njev=receipt["njev"], nlu=receipt["nlu"],
                         accepted_nodes=receipt["accepted_nodes"]),
        )
        save_npz(caseout / "comparison_and_source_data.npz",
                 x=current["x"], z=current["z"], raw_delta_from_baseline=dx,
                 T_K=current["T_K"], baseline_T_K=old["T_K"], delta_T_K=dT,
                 ne_m3=c["ne_m3"], baseline_ne_m3=b["ne_m3"], delta_tau=dtau,
                 signed_observables=current["signed_observables"], signed_delta=ds,
                 signed_names=np.array(SIGNED_NAMES),
                 dense_x=dense["x"], dense_z=dense["z"], dense_T_K=dense["T_K"],
                 energy_names=np.array(energy_names), energy_integrands_eV_baryon_per_x=energy_integrands,
                 planck_minus_actual_W_m3=difference, energy_density_replacement_W_m3=density_replacement,
                 reference_recoil_W_m3=reference_recoil, source_owner_residual_scaled=scaled)
        save_json(caseout / "SUMMARY.json", summary)
        summaries[label] = summary
        data[label] = dict(raw=current["raw_state"], signed=current["signed_observables"], T=current["T_K"])
        sources.append(dict(label=label, receipt_sha256=digest(folder / "RESULT.json"),
                            output_bindings=receipt["outputs"], baseline=inputs[seed]["cases"][refined]["identity"]))
        table.append({k: summary[k] for k in (
            "label", "seed", "branch", "refined", "temperature_end_K", "delta_temperature_end_K",
            "delta_temperature_end_percent", "peak_temperature_1025_K", "tau_end", "delta_tau_end",
            "max_abs_delta_conditional_fraction_109", "max_abs_delta_signed_stress_only_109",
            "gas_integral_residual_scaled", "gas_integral_513_1025_delta_scaled", "max_backreaction_ratio")})

    branch_comparisons = {}
    for seed in SEEDS:
        pair = {}
        for refined in (False, True):
            a = data[label_for(seed, "actual_hot", refined)]
            b = data[label_for(seed, "planck_reference", refined)]
            dr, ds = a["raw"] - b["raw"], a["signed"] - b["signed"]
            pair["refined" if refined else "nominal"] = dict(
                actual_minus_planck_temperature_end_K=float(a["T"][-1] - b["T"][-1]),
                max_abs_delta_lnT=float(abs(dr[:, 62]).max()),
                max_abs_delta_conditional_fraction=float(abs(dr[:, 40:61]).max()),
                actual_minus_planck_tau_end=float(dr[-1, 61]), max_abs_delta_tau=float(abs(dr[:, 61]).max()),
                max_abs_delta_signed_six=float(abs(ds).max()),
                max_abs_delta_signed_stress_only=float(abs(ds[:, 1:]).max()))
        am = refinement["pairs"][seed + "_actual_hot"]["metrics"]
        pm = refinement["pairs"][seed + "_planck_reference"]["metrics"]
        map_keys = dict(lnT="max_abs_delta_lnT", tau="max_abs_delta_tau",
                        conditional_fraction="max_abs_delta_conditional_ion_fraction",
                        signed_six="max_abs_delta_signed_six", signed_stress_only="max_abs_delta_signed_stress_only")
        resolution = {}
        for name, refine_key in map_keys.items():
            key = "max_abs_delta_" + name
            observed = am[refine_key] + pm[refine_key]
            resolution[name] = dict(branch_difference=pair["refined"][key],
                                    sum_of_observed_refinement_changes=observed,
                                    exceeds_observed_refinement_changes=pair["refined"][key] > observed,
                                    interpretation="empirical finite-resolution comparison, not a rigorous or global error bound")
        pair["resolution"] = resolution
        branch_comparisons[seed] = pair
    save_json(output / "BRANCH_COMPARISONS.json", branch_comparisons)
    with (output / "CASE_SUMMARY.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    attempts = [json.loads(p.read_text()) for p in sorted((source / "execution").glob("attempt_*/FINISHED.json"))]
    summary = dict(source_identity=identity, runtime_identity=runtime_id, cases=summaries,
                   branch_comparisons=branch_comparisons, refinement=refinement,
                   new_coupled_IVPs=sum(r["new_integrations_completed"] for r in attempts),
                   total_charged_execution_wall_seconds=sum(r["wall_seconds"] for r in attempts),
                   analysis_new_ODE_integrations=0, old_IVP_reruns=0,
                   scope="finite full63 gas-temperature coupling; separate reference bath, source-ledger only radiation exchange",
                   physical_status="HOLD", production="NOT_APPROVED", global_convergence="NOT_RUN",
                   REI_activation=False, U5="CLOSED_HOLD_NOT_RESET")
    save_json(output / "SUMMARY.json", summary)
    save_json(output / "INPUTS.json", dict(runtime_identity=runtime_id, runtime_files=runtime_files, cases=sources,
              campaign_lock_sha256=digest(source / "CAMPAIGN_LOCK.json"), refinement_sha256=digest(source / "REFINEMENT.json")))
    outputs = {str(p.relative_to(output)): dict(bytes=p.stat().st_size, sha256=digest(p))
               for p in sorted(output.rglob("*")) if p.is_file()}
    final = dict(status="COMPLETE", source_identity=identity, source_files=files,
                 runtime_identity=runtime_id, outputs=outputs, new_ODE_integrations=0, old_IVP_reruns=0,
                 cases=len(summaries), wall_seconds=time.perf_counter() - start, own_cpu_seconds=time.process_time() - cpu)
    save_json(output / "RESULT.json", final)
    print(json.dumps({k: final[k] for k in ("status", "source_identity", "cases", "wall_seconds")}, indent=2))
    return final


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=UNIT / "results/compton8")
    ap.add_argument("--output", type=Path, default=UNIT / "results/analysis_v1")
    args = ap.parse_args()
    run(args.input, args.output)


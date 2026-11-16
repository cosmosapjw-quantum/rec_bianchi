#!/usr/bin/env python3
"""Summarize measured F08 receiver runs without promoting owner admission."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import numpy as np

CASES = ("S0_BI_native_control_160", "S0_BI_thomson_l4_160", "S0_BI_thomson_l6_160",
         "S0_BI_thomson_l4_320", "S0_FLRW_thomson_l4_160")

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def summarize(runs, out):
    out.mkdir(parents=True, exist_ok=True)
    results = {name: json.loads((runs/name/"RESULT.json").read_text()) for name in CASES}
    arrays = {name: np.load(runs/name/"stokes_history.npz") for name in CASES}
    comparisons = []
    for a,b,meaning in ((CASES[1],CASES[2],"degree4_vs_degree6"),
                        (CASES[1],CASES[3],"dt_vs_dt_over_2")):
        def QU(name):
            data = arrays[name]
            return data["stokes"][-1,...,1:3].sum(axis=0)+data["guard_n"][-1,:,1:3]
        u,v = QU(a),QU(b)
        P1 = results[a]["final"]["physical_peak_linear_fraction"]
        P2 = results[b]["final"]["physical_peak_linear_fraction"]
        comparisons.append({"kind":meaning,"a":a,"b":b,
                            "final_native_QU_relative_L2":float(np.linalg.norm(u-v)/np.linalg.norm(u)),
                            "final_physical_peak_P_relative":abs(P1-P2)/P1,
                            "claim":"MEASURED_SENSITIVITY_NOT_INTERVAL_ERROR_BOUND"})
    witness=[]
    for name in CASES:
        with (runs/name/"trajectory.csv").open() as f:
            rows=list(csv.DictReader(f))
        for row in rows:
            k=int(row["step"])
            if k in (1,32,64,96,128,160,320):
                witness.append({"case":name, **row})
    with (out/"WITNESS.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(witness[0]));writer.writeheader();writer.writerows(witness)
    base,feedback=results[CASES[0]]["final"],results[CASES[1]]["final"]
    result={
        "schema":"REC_F08_PERSISTENT_POLARIZED_PAIRED_POINT_EVOLUTION_V1",
        "implementation_checkpoint":"2b05ad936cd67ce3cb7a650db6ea7cf3ceb9b6a0",
        "source_pins":{
            "REC199":"c10e97ab3178c423cc7699684b33e1730d26437a",
            "REC200":"c995fb84a5523202ab429003a78d7d590b51ace9",
            "REI_owner_PR83":"c07fc7e765ce204bc3e84016cc6874612e535b86",
            "REI_canonical":"56dc609ea9b801c88d3364aed3eee140b3a20d46",
            "BASS_original_PR328":"b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6",
            "BASS_followup_PR331":"ea19c11ee3412b9fcbc8d3d07ec7c7eefcf7ddbf"},
        "original_F08_pair_input_sha256":"0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8",
        "original_paired_runtime_rs_sha256":"b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7",
        "source_locks":{"S0":12,"Rust":51,"photon":4},
        "frozen_native_gates":{"local_bound_strict":2e-4,"public_width_strict":2e-3,"max_ledger":1e-12},
        "historical_angular_gate":{"relative_disagreement":0.04152277708926094,
                                   "threshold":.03,"status":"FAIL_PRESERVED"},
        "actual_paired_trial_calls":sum(r["original_paired_trials"] for r in results.values()),
        "actual_native_endpoint_calls":sum(r["original_native_endpoints"] for r in results.values()),
        "execution_count_scope":"FIVE_COMPLETED_SCIENCE_CASES; EARLY_FAILED_INTEGRATION_ATTEMPTS_SEPARATE",
        "failed_integration_attempts":{"interface_h_key":{"paired_trials":0,"native_endpoints":0},
                                       "source_arithmetic_parity":{"paired_trials":2,"native_endpoints":6}},
        "paired_trials_including_failed_integration_attempts":2+sum(r["original_paired_trials"] for r in results.values()),
        "native_endpoints_including_failed_integration_attempts":6+sum(r["original_native_endpoints"] for r in results.values()),
        "persistent_polarized_macrosteps":sum(r["persistent_polarized_steps"] for r in results.values()),
        "all_recorded_spectral_angular_Stokes_rows":sum(r["physical_spectral_stokes_rows"] for r in results.values()),
        "cases":results,
        "comparisons":comparisons,
        "same_dt_Thomson_minus_native_control":{k:feedback[k]-base[k] for k in
            ("xHII","xHeII","xHeIII","T_K","N_photons_per_H","U_photons_eV_per_H","redshift_work_eV_per_H")},
        "interpretation":{
            "new_result":"PERSISTENT_POLARIZED_COLLISION_FEEDBACK_ACTUAL_NATIVE_EVOLUTION",
            "P_denominator":"TOTAL_INCIDENT_PLUS_SCATTERED_PHOTON_INTENSITY; NOT_SCATTERED_IN_ONLY",
            "gas_feedback_detectability":"NO_RESOLVED_MATERIAL_EFFECT_AT_REPORTED_DOUBLE_PRECISION",
            "linear_Thomson_semigroup":"EXACT_FOR_FROZEN_DEGREE4_PHYSICAL_QUADRATURE",
            "native_q_adapter":"CONDITIONAL_NONLINEAR_NORMALIZED_COLLOCATION",
            "time_discretization":"ORIGINAL_PAIRED_HALF_STEPS_THEN_ENDPOINT_NE_LIE_COLLISION",
            "guard":"TWO_POLARIZED_MOMENTS_WITH_JOINT_PSD_CHECK_NOT_ENERGY_RESOLVED",
            "photon_interval_chain":"REINITIALIZED_TO_POINT_ON_FEEDBACK; NO_CUMULATIVE_CERTIFICATE",
            "fixed_hat_support":"FAIL_RETAINED",
            "continuum_angular_convergence":"UNRESOLVED",
            "all14_interval_ledgers":"NOT_CERTIFIED",
            "full16000_original_interval":"NOT_RUN"},
        "DAG":{"REI_canonical":"28/88","REI_working":"33/88","physical_fast":"4/7","REC_H5":"0/313","all_deltas":0},
        "production":"HOLD","owner_admission":"NOT_GRANTED","auto_next":False,
        "raw_outputs":{name:{f:sha(runs/name/f) for f in ("RESULT.json","trajectory.csv","stokes_history.npz")} for name in CASES},
    }
    (out/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"paired_trials":result["actual_paired_trial_calls"],
                      "native_endpoints":result["actual_native_endpoint_calls"],
                      "comparisons":comparisons,
                      "gas_delta":result["same_dt_Thomson_minus_native_control"]}),flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--runs",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();summarize(a.runs,a.out)

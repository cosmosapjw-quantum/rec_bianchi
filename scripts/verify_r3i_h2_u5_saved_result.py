#!/usr/bin/env python3
"""Offline, create-only audit of the immutable H2 U5 NCP result.

This module reads saved trajectories and the original C oracle stream. It never
launches either trajectory executable. Full use requires independent static
review of this verifier first; --smoke-steps 1 is a local parser smoke only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import sys
import time

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from verify_r3i_h2_start import compare_state, checked_integrated_rhs_ratio, sha, PINNED_ZIP_SHA
from verify_r3i_h2_u5_thermal import (CombinedOracle, frozen_u5_original_gate,
    KB_EV_K, LINE_EV)
from r3i_u5_average_forensic import _owner, numerical_gates
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    _source_edges, causal_incoming_from_accepted_histories)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    HyRec2012Cosmology, make_hmla_source)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    _canonical_twophoton_table, populate_original_full_atomic,
    complete_original_full_atomic)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u5_thermal import (
    START_IZ, RT_IZ, PREFIX_COLUMNS, CHECKPOINT_SHA256)
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs

ARCHIVE_SHA = "8d18bd221e4cf9aa4af1e8a48eb2048ebe9c65d33dda0f9a3de17fb529823c3c"
RAW_MANIFEST_SHA = "1b45b52a799e3e2135fb3467ed73f4f1acd8cb1909cfe6c9a196174dc2fc4b60"
NPZ_SHA = "7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b"
C_STDOUT_SHA = "06d81cdd2ac840b926128cab60e3c99acc78f8794234c02f764bdeab1d626987"
LIB_SHA = "25cb1acbc6ef93a489445e4a06f55ab45eb1bc07a46d0f12a06fb2d6f2bb045f"
VERIFICATION_SHA = "73635422c000a23dc70b7fc227fcf4d35151064e60b0efeed15ba312a405956d"
STEPS = 14727
FIELDS_PER_STEP = 625
EVENT_IZ = 53177
CPU_CAP = 450
WALL_CAP = 750
PRIOR_AUDIT_SHA = "5a13fc32d6a5fe591992d3097d2679c9d9ce22ac9f1833d2107c6a273cd9fc2f"
PRIOR_LAUNCHER_TIME_SHA = "d13ecdf9e65fccede426ee0779ce5d9668da3a88d0af1f31ab2d5fd540beb28c"
PRIOR_LAUNCHER_WALL_S = 156.58
PRIOR_DIAGNOSTICS_SHA = "a9a4c640a55ecf9b1e3a69301412dacaadceebdd738380da316cf1931f151eda"
PRIOR_RAW_FAILURES_SHA = "1b5cbda932cfb068563a39abeeabfb88b7e77ae7f6c8cab3ba11cb8731b4f16d"
SMOKE_SHAS = (
    "0ba462c1113e92a7755b099dd3f13b5269fe9e5c8f7ebfc81e0143305d742fd6",
    "bc1bced471bde01e250986288a092451b59925f760efc15ee7a2b86ff731d5d5",
    "0381fac231dafff8974eb8c346c7047d39573ccc133dae0dded91c613fc4224b",
)
PRIOR_CPU_S = 120.315836
PRIOR_WALL_S = 179.17210247197


def require(cond: bool, code: str) -> None:
    if not cond:
        raise ArithmeticError(code)


def finite_number(value: str, code: str) -> float:
    result = float(value)
    require(math.isfinite(result), code)
    return result


def validate_record_order(tag: str, row: list[str], *, phase: str, i: int,
                          col: int, bin_index: int) -> tuple[str, int, int, int]:
    """Strict stream automaton; duplicates, omissions and reordered bins fail."""
    if phase == "PARAM":
        require(tag == "PARAM", "C_PARAM_ORDER")
        return "HE", i, col, bin_index
    if phase == "HE":
        if i < 36447:
            require(tag == "HE" and int(row[1]) == i, f"C_HE_ORDER:{i}")
            return "HE", i + 1, col, bin_index
        require(tag == "NODE", "C_NODE_ORDER")
        return "PREFIX", 0, 0, 0
    if phase == "PREFIX":
        want = "PV" if bin_index < 311 else "PL"
        b = bin_index if bin_index < 311 else bin_index - 311
        require(tag == want and int(row[1]) == col and int(row[2]) == b,
                f"C_PREFIX_ORDER:{col}:{bin_index}")
        bin_index += 1
        if bin_index == 314:
            bin_index = 0
            col += 1
        return ("BASE" if col == PREFIX_COLUMNS else "PREFIX"), i, col, bin_index
    if phase == "BASE":
        require(tag == "BASE", "C_BASE_ORDER")
        return "STEP", 0, col, 0
    if phase == "STEP":
        if i == EVENT_IZ-START_IZ:
            require(tag == "THERMAL_EVENT", "C_THERMAL_EVENT_MISSING")
        if tag == "THERMAL_EVENT":
            require(i == EVENT_IZ - START_IZ, "C_THERMAL_EVENT_ORDER")
            return "EVENT_STEP", i, col, 0
        require(tag == "STEP" and int(row[1]) == i and i < STEPS,
                f"C_STEP_ORDER:{i}")
        return "SPECTRUM", i, col, 0
    if phase == "EVENT_STEP":
        require(tag == "STEP" and int(row[1]) == i, "C_EVENT_STEP_ORDER")
        return "SPECTRUM", i, col, 0
    if phase == "SPECTRUM":
        want = "V" if bin_index < 311 else "A" if bin_index < 622 else "L"
        b = bin_index if bin_index < 311 else bin_index - 311 if bin_index < 622 else bin_index - 622
        require(tag == want and int(row[1]) == i and int(row[2]) == b,
                f"C_SPECTRAL_ORDER:{i}:{bin_index}")
        bin_index += 1
        if bin_index == FIELDS_PER_STEP:
            return ("END" if i + 1 == STEPS else "STEP"), i + 1, col, 0
        return "SPECTRUM", i, col, bin_index
    if phase == "END":
        require(tag == "END", "C_END_ORDER")
        return "DONE", i, col, bin_index
    raise ArithmeticError("C_TRAILING_RECORD")


def causal_link_indices(table, j: int, dlna: float = 4.245e-5) -> int:
    """Check all 311 virtual plus 2 line incoming links against accepted j."""
    _, target, source = _source_edges(table.energy_eV)
    lookback = np.log(source / target)
    require(np.all(np.isfinite(lookback)) and np.all(lookback > dlna), "CAUSAL_FREQUENCY_SPACING")
    emit = j - lookback / dlna
    active = emit >= 0.
    floor = np.floor(emit[active]).astype(np.int64)
    require(np.all(floor + 1 <= j - 1), f"CAUSAL_FUTURE_ENDPOINT:{j}")
    return len(lookback)


def thermal_latch_condition(step: int, delta: float, coupled: bool) -> bool:
    """DLNT_MAX triggers the source thermal branch once at event input."""
    if not math.isfinite(delta):
        return False
    event_step = EVENT_IZ - START_IZ
    return ((not coupled and delta < 5.e-4) if step < event_step else
            (coupled and delta >= 5.e-4) if step == event_step else coupled)


def remaining_budget(prior_cpu_s: float, prior_launcher_wall_s: float) -> tuple[int, int]:
    """Charge a prior failed audit; integer limits conservatively round down."""
    require(all(math.isfinite(v) and v >= 0. for v in
                (prior_cpu_s, prior_launcher_wall_s)), "PRIOR_COST_NONFINITE")
    cpu = min(290, math.floor(CPU_CAP-prior_cpu_s))
    wall = min(480, math.floor(WALL_CAP-prior_launcher_wall_s))
    require(cpu > 0 and wall > 0, "AUDIT_CUMULATIVE_BUDGET_EXHAUSTED")
    return cpu, wall


def verify_prior_audit(base: Path) -> dict:
    receipt = base / "full_run_001/audit.json"
    launcher_time = base / "full_run_001_time.txt"
    diagnostics = base / "full_run_001/average_diagnostics.jsonl"
    raw_failures = base / "full_run_001/average_raw_failures.jsonl"
    require(sha(receipt) == PRIOR_AUDIT_SHA and
            sha(launcher_time) == PRIOR_LAUNCHER_TIME_SHA and
            sha(diagnostics) == PRIOR_DIAGNOSTICS_SHA and
            sha(raw_failures) == PRIOR_RAW_FAILURES_SHA, "PRIOR_AUDIT_RECEIPTS_SHA")
    for n, expected in enumerate(SMOKE_SHAS, 1):
        require(sha(base / f"local_smoke_00{n}/audit.json") == expected,
                f"PRIOR_SMOKE_RECEIPT_SHA:{n}")
    data = json.loads(receipt.read_text())
    require(data["status"] == "FAIL" and
            data["first_failure"]["message"] == "THERMAL_SWITCH_CONDITION:14726" and
            data["provenance"]["archive_sha256"] == ARCHIVE_SHA and
            abs(data["resources"]["additional_cpu_s"]-109.627916) < 1.e-9,
            "PRIOR_AUDIT_RECEIPT_CONTENT")
    require("Elapsed (wall clock) time (h:mm:ss or m:ss): 2:36.58" in
            launcher_time.read_text(), "PRIOR_LAUNCHER_TIME_CONTENT")
    require("User time (seconds): 109.12" in launcher_time.read_text() and
            "System time (seconds): 1.30" in launcher_time.read_text(),
            "PRIOR_LAUNCHER_CPU_CONTENT")
    require(len(diagnostics.read_text().splitlines()) == 8 and
            len(raw_failures.read_text().splitlines()) == 8,
            "PRIOR_DIAGNOSTIC_COUNT")
    cpu, wall = remaining_budget(PRIOR_CPU_S, PRIOR_WALL_S)
    return {"prior_audit_sha256": PRIOR_AUDIT_SHA,
            "prior_launcher_time_sha256": PRIOR_LAUNCHER_TIME_SHA,
            "prior_diagnostics_sha256": PRIOR_DIAGNOSTICS_SHA,
            "prior_raw_failures_sha256": PRIOR_RAW_FAILURES_SHA,
            "prior_smoke_sha256": list(SMOKE_SHAS),
            "prior_cumulative_cpu_s": PRIOR_CPU_S,
            "prior_cumulative_wall_s": PRIOR_WALL_S,
            "remaining_cpu_limit_s": cpu, "remaining_wall_limit_s": wall}


def verify_provenance(folder: Path, archive: Path, checkpoint: Path) -> dict:
    require(sha(archive) == ARCHIVE_SHA, "RAW_ARCHIVE_SHA")
    manifest = folder / "RAW_MANIFEST.json"
    require(sha(manifest) == RAW_MANIFEST_SHA, "RAW_MANIFEST_SHA")
    data = json.loads(manifest.read_text())
    for rel in ("run_001/python_u5_thermal.npz", "run_001/native_oracle_stdout.csv",
                "run_001/liboriginal_full_source.so", "run_001/verification.json"):
        entry = data["files"][rel]
        path = folder / rel
        require(path.is_file() and path.stat().st_size == entry["bytes"] and
                sha(path) == entry["sha256"], f"RAW_MEMBER_SHA:{rel}")
    expected = {"run_001/python_u5_thermal.npz": NPZ_SHA,
                "run_001/native_oracle_stdout.csv": C_STDOUT_SHA,
                "run_001/liboriginal_full_source.so": LIB_SHA,
                "run_001/verification.json": VERIFICATION_SHA}
    require(all(data["files"][k]["sha256"] == v for k, v in expected.items()),
            "FROZEN_MEMBER_IDENTITY")
    require(sha(checkpoint) == CHECKPOINT_SHA256, "U4_CHECKPOINT_SHA")
    require(sha(ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip") ==
            PINNED_ZIP_SHA, "ORIGINAL_HYREC_ZIP_SHA")
    source_files = [rel for rel in data["files"] if rel.startswith("run_001/source_extract/HyRec/")]
    require(source_files, "EXTRACTED_SOURCE_ABSENT")
    for rel in source_files:
        path = folder / rel
        require(path.is_file() and sha(path) == data["files"][rel]["sha256"],
                f"EXTRACTED_SOURCE_SHA:{rel}")
    receipt = json.loads((folder / "run_001/verification.json").read_text())
    require(receipt["status"] == "FAIL" and
            receipt["first_failure"]["message"] ==
            "INTEGRATED_PHOTON_PARITY:i=3162:tag=A:bin=8:ratio=2.4235253635704352" and
            receipt["common_binary_sha256"] == LIB_SHA and
            receipt["python_history_sha256"] == NPZ_SHA,
            "FROZEN_FIRST_FAILURE_OR_PROVENANCE")
    require(frozen_u5_original_gate()["failures"] == 9, "OLD_U5_GATE_CHANGED")
    return {"archive_sha256": ARCHIVE_SHA, "manifest_sha256": RAW_MANIFEST_SHA,
            "checkpoint_sha256": CHECKPOINT_SHA256, "payload_members": len(data["files"])}


def load_saved(folder: Path, checkpoint: Path):
    with np.load(folder / "run_001/python_u5_thermal.npz", allow_pickle=False) as x:
        require(set(x.files) == {"states_json", "steps_json", "virtual_out",
                "average_virtual", "lyman_out"}, "SAVED_NPZ_FIELDS")
        states = [json.loads(str(v)) for v in x["states_json"]]
        steps = [json.loads(str(v)) for v in x["steps_json"]]
        v, a, l = (x[k].copy() for k in ("virtual_out", "average_virtual", "lyman_out"))
    require(len(states) == STEPS + 1 and len(steps) == STEPS and
            v.shape == (311, PREFIX_COLUMNS + STEPS) and a.shape == v.shape and
            l.shape == (3, PREFIX_COLUMNS + STEPS), "SAVED_SHAPES")
    require(all(np.all(np.isfinite(q)) for q in (v, a, l)), "SAVED_NONFINITE_SPECTRUM")
    with np.load(checkpoint, allow_pickle=False) as cp:
        require(np.array_equal(v[:, :PREFIX_COLUMNS], cp["virtual_out"]) and
                np.array_equal(a[:, :PREFIX_COLUMNS], cp["average_virtual"]) and
                np.array_equal(l[:, :PREFIX_COLUMNS], cp["lyman_out"]),
                "U4_PREFIX_MISMATCH")
        require(states[0] == json.loads(str(cp["states_json"][-1])),
                "U4_BASE_MISMATCH")
    return states, steps, v, a, l


def audit(folder: Path, checkpoint: Path, evidence: Path, *, smoke_steps: int = 0) -> dict:
    states, steps, pv, pa, pl = load_saved(folder, checkpoint)
    source_dir = folder / "run_001/source_extract/HyRec"
    c = HyRec2012Cosmology()
    rates = OriginalHyRecPrimitiveRateTable.from_archive(
        ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
    table = _canonical_twophoton_table(rates.archive_path)
    source = make_hmla_source(c, rates)
    oracle = CombinedOracle(folder / "run_001/liboriginal_full_source.so", source_dir, c)
    cv = np.full_like(pv, np.nan)
    cl = np.full_like(pl, np.nan)
    report = {"status": "HOLD_INCOMPLETE", "checked_steps": 0,
              "checked_spectral_fields": 0, "checked_causal_links": 0,
              "average_original_failures": [], "owner_diagnostics": [],
              "maxima": {k: 0. for k in ("xe", "Tm_K", "hydrogen_rhs", "thermal_rhs",
                                        "virtual", "average", "lyman", "schur_residual")}}
    phase, i, col, bpos = "PARAM", 0, 0, 0
    c_input = None
    c_step_input = None
    event_seen = False
    coupled = 0
    diagnostic_path = evidence / "average_diagnostics.jsonl"
    raw_path = evidence / "average_raw_failures.jsonl"
    with (folder / "run_001/native_oracle_stdout.csv").open() as stream, \
            diagnostic_path.open("x") as diagnoses, raw_path.open("x") as raw_failures:
        for line_no, line in enumerate(stream, 1):
            row = line.rstrip("\n").split(",")
            tag = row[0]
            phase, i_new, col, bpos = validate_record_order(
                tag, row, phase=phase, i=i, col=col, bin_index=bpos)
            if tag == "PARAM":
                require(tuple(map(int, row[1:])) == (RT_IZ, 21943, 58389), "C_GRID_PARAMS")
            elif tag == "HE":
                values = [finite_number(q, "C_HE_NONFINITE") for q in row[2:14]]
                xe, xhii, xhei, xheii, xheiii = values[1:6]
                # Source-defined species ledger; high-z HeIII includes two electrons.
                require(abs(xe - (xhii + xheii + 2*xheiii)) <= 5.e-9 and
                        abs(xhei+xheii+xheiii-c.fHe) <= 5.e-9,
                        f"C_HE_SPECIES_LEDGER:{i}")
            elif tag == "NODE":
                require(int(row[1]) == RT_IZ, "C_RT_NODE")
                for q in row[2:8]: finite_number(q, "C_NODE_NONFINITE")
            elif tag in ("PV", "PL"):
                value = finite_number(row[3], "C_PREFIX_NONFINITE")
                j, b = map(int, row[1:3])
                target = cv if tag == "PV" else cl
                py = pv if tag == "PV" else pl
                target[b, j] = value
                energy = LINE_EV[b] if tag == "PL" else table.energy_eV[b]
                z_prefix = c.redshift(RT_IZ+j)
                fbb = 1./math.expm1(float(energy)/(KB_EV_K*c.T0_K*(1.+z_prefix)))
                require(abs(value-py[b, j]) <= 1.e-7*max(abs(value), abs(py[b, j]))+1.e-10*fbb,
                        f"C_PREFIX_PARITY:{j}:{b}:{tag}")
            elif tag == "BASE":
                c_input = {"iz": int(row[1]), "z": finite_number(row[2], "C_BASE_Z"),
                           "xH1s": finite_number(row[3], "C_BASE_H1"),
                           "xHII": finite_number(row[4], "C_BASE_HII"),
                           "xHeII": finite_number(row[5], "C_BASE_HEII"),
                           "xe": finite_number(row[6], "C_BASE_XE"),
                           "Tm_K": finite_number(row[7], "C_BASE_TM"),
                           "post_saha": bool(int(row[8]))}
                compare_state(states[0], c_input, -1)
                require(np.all(np.isfinite(cv[:, :PREFIX_COLUMNS])) and
                        np.all(np.isfinite(cl[:, :PREFIX_COLUMNS])), "C_PREFIX_INCOMPLETE")
            elif tag == "THERMAL_EVENT":
                event_seen = True
                require(int(row[1]) == EVENT_IZ, "THERMAL_EVENT_INDEX")
                delta, prev2, prev = (finite_number(q, "THERMAL_EVENT_NONFINITE") for q in row[2:5])
                require(0.0005 <= delta < 0.0006, "THERMAL_EVENT_DELTA")
                py_t = [states[k]["Tm_K"] for k in range(i-3, i+1)]
                h = 4.245e-5
                require(abs((py_t[2]-py_t[0])/(2*h)-prev2)/max(1.,abs(prev2)) <= 2.e-10 and
                        abs((py_t[3]-py_t[1])/(2*h)-prev)/max(1.,abs(prev)) <= 2.e-10,
                        "THERMAL_EVENT_SEEDS")
            elif tag == "STEP":
                idx = int(row[1])
                require(idx == i and int(row[2]) == START_IZ+idx+1, "C_STEP_INDEX")
                native = {"iz": int(row[2]), "z": finite_number(row[3], "C_STEP_Z"),
                          "xH1s": finite_number(row[4], "C_STEP_H1"),
                          "xHII": finite_number(row[5], "C_STEP_HII"),
                          "xHeII": finite_number(row[6], "C_STEP_HEII"),
                          "xe": finite_number(row[7], "C_STEP_XE"),
                          "Tm_K": finite_number(row[8], "C_STEP_TM"),
                          "post_saha": bool(int(row[11]))}
                require(c_input is not None, "C_INPUT_MISSING")
                compare_state(states[idx+1], native, idx)
                step = steps[idx]
                require(abs(native["xH1s"]+native["xHII"]-1.) <= 5.e-9 and
                        abs(native["xe"]-native["xHII"]-native["xHeII"]) <= 5.e-9,
                        f"C_STEP_SPECIES_LEDGER:{idx}")
                require(step["input_iz"] == START_IZ+idx and
                        step["output_iz"] == START_IZ+idx+1 and
                        step["photon_col"] == PREFIX_COLUMNS+idx and
                        step["branch"] == states[idx]["branch"] == "H_ONLY" and
                        step["coupled"] == bool(int(row[10])) == (idx >= EVENT_IZ-START_IZ) and
                        (step["thermal_rhs"] is not None if step["coupled"] else
                         step["thermal_rhs"] is None),
                        f"STEP_STAGE_LEDGER:{idx}")
                require(abs(states[idx]["xe"]-states[idx]["xHII"]) <= 5.e-12 and
                        states[idx]["xHeII"] == 0. and not states[idx]["post_saha"],
                        f"PY_SPECIES_LEDGER:{idx}")
                delta = 1.-states[idx]["Tm_K"]/c.T0_K/(1.+states[idx]["z"])
                require(thermal_latch_condition(idx, delta, bool(step["coupled"])),
                        f"THERMAL_SWITCH_CONDITION:{idx}")
                residual = finite_number(str(step["schur_residual"]), "SCHUR_NONFINITE")
                require(0. <= residual <= 2.e-10, f"SCHUR_RESIDUAL:{idx}")
                report["maxima"]["schur_residual"] = max(report["maxima"]["schur_residual"], residual)
                report["maxima"]["hydrogen_rhs"] = max(report["maxima"]["hydrogen_rhs"],
                    checked_integrated_rhs_ratio(float(step["hydrogen_rhs"]),
                                                 finite_number(row[9], "C_H_RHS_NONFINITE"), 2.e-7, idx, "H"))
                if step["coupled"]:
                    coupled += 1
                    report["maxima"]["thermal_rhs"] = max(report["maxima"]["thermal_rhs"],
                        checked_integrated_rhs_ratio(float(step["thermal_rhs"]),
                            finite_number(row[12], "C_T_RHS_NONFINITE"), 2.e-7, idx, "T"))
                    py_t_rhs = source_thermal_rhs(c, states[idx]["xe"],
                                                 states[idx]["Tm_K"], states[idx]["z"])
                    c_t_rhs = oracle.thermal_rhs(states[idx]["xe"],
                                                 states[idx]["Tm_K"], states[idx]["z"])
                    thermal_ratio = abs(py_t_rhs-c_t_rhs)/max(1., abs(c_t_rhs))
                    require(math.isfinite(thermal_ratio) and thermal_ratio <= 2.e-10,
                            f"COMMON_INPUT_THERMAL_RHS:{idx}:{thermal_ratio}")
                    require(abs(py_t_rhs-step["thermal_rhs"])/max(1., abs(step["thermal_rhs"])) <= 2.e-10,
                            f"SAVED_THERMAL_RHS:{idx}")
                else:
                    require(math.isnan(float(row[12])), f"C_UNCOUPLED_THERMAL_SENTINEL:{idx}")
                j = PREFIX_COLUMNS+idx
                old_h_rhs = ([-0.4919330230209214, -0.45204486161530666][idx]
                             if idx < 2 else steps[idx-2]["hydrogen_rhs"])
                predicted_xe = states[idx]["xe"]+4.245e-5*(1.25*step["hydrogen_rhs"]-.25*old_h_rhs)
                require(abs(predicted_xe-states[idx+1]["xe"]) <=
                        5.e-9*max(abs(states[idx+1]["xe"]), 1.e-8),
                        f"HYDROGEN_PREDICTOR:{idx}")
                if step["coupled"]:
                    old_t_rhs = (states[idx-1]["Tm_K"]-states[idx-3]["Tm_K"])/(2*4.245e-5)
                    predicted_tm = states[idx]["Tm_K"]+4.245e-5*(1.25*step["thermal_rhs"]-.25*old_t_rhs)
                    require(abs(predicted_tm-states[idx+1]["Tm_K"]) <=
                            5.e-10*max(abs(states[idx+1]["Tm_K"]), 1.),
                            f"THERMAL_PREDICTOR:{idx}")
                report["checked_causal_links"] += causal_link_indices(table, j)
                require(np.all(np.isfinite(pv[:, :j])) and np.all(np.isfinite(pl[:, :j])),
                        f"PY_CAUSAL_HISTORY_INCOMPLETE:{idx}")
                incoming = causal_incoming_from_accepted_histories(
                    energies_eV=table.energy_eV, virtual_history=pv[:, :j],
                    lyman_history=pl[:, :j], z_start=c.redshift(RT_IZ),
                    iz=j, z_face=states[idx]["z"], dlna=4.245e-5, shear_q=0.)
                tm = states[idx]["Tm_K"]
                tr = c.T0_K*(1.+states[idx]["z"])
                if tm == tr: tm = math.nextafter(tm, 0.)
                snap = populate_original_full_atomic(source, z=states[idx]["z"],
                    xHII=states[idx]["xe"], xe=states[idx]["xe"], Tm_K=tm,
                    incoming_virtual=incoming.virtual_distortion[0],
                    incoming_lyman=incoming.lya_lyb_incoming_distortion[0])
                out = complete_original_full_atomic(snap)
                require(math.isfinite(out.normalized_matrix_residual) and
                        out.normalized_matrix_residual <= 2.e-10,
                        f"RECOMPUTED_SCHUR_RESIDUAL:{idx}")
                require(abs(out.dxHII_dln_a-step["hydrogen_rhs"])/
                        max(1., abs(step["hydrogen_rhs"])) <= 2.e-10,
                        f"SAVED_SOURCE_RHS:{idx}")
                for name, regenerated, saved, energies in (
                    ("V", out.outgoing_virtual, pv[:, j], table.energy_eV),
                    ("A", out.average_virtual, pa[:, j], table.energy_eV),
                    ("L", out.outgoing_lyman, pl[:, j], LINE_EV)):
                    fbb = 1./np.expm1(np.asarray(energies)/(KB_EV_K*tr))
                    tol = 1.e-7*np.maximum(np.abs(regenerated), np.abs(saved))+1.e-10*fbb
                    require(np.all(np.isfinite(regenerated)) and
                            np.all(np.abs(regenerated-saved) <= tol),
                            f"SAVED_SOURCE_SPECTRUM:{idx}:{name}")
                for name, floor in (("xe", 1.e-8), ("Tm_K", 1.)):
                    report["maxima"][name] = max(report["maxima"][name],
                        abs(states[idx+1][name]-native[name])/max(abs(native[name]), floor))
                c_step_input = c_input
                c_input = native
                report["checked_steps"] += 1
            elif tag in ("V", "A", "L"):
                idx, b = map(int, row[1:3])
                j = PREFIX_COLUMNS+idx
                value = finite_number(row[3], "C_SPECTRUM_NONFINITE")
                py = {"V": pv, "A": pa, "L": pl}[tag][b, j]
                if tag == "V": cv[b, j] = value
                if tag == "L": cl[b, j] = value
                energy = LINE_EV[b] if tag == "L" else table.energy_eV[b]
                fbb = 1./math.expm1(float(energy)/(KB_EV_K*c.T0_K*(1.+states[idx]["z"])))
                tol = 1.e-7*max(abs(py), abs(value))+1.e-10*fbb
                ratio = abs(py-value)/tol
                require(math.isfinite(ratio), f"SPECTRAL_RATIO_NONFINITE:{idx}:{tag}:{b}")
                if ratio > 1.:
                    require(tag == "A", f"INTEGRATED_PHOTON_PARITY:{idx}:{tag}:{b}:{ratio}")
                    require(len(report["average_original_failures"]) < 64,
                            "AVERAGE_FAILURE_CAP_64")
                    require(np.all(np.isfinite(cv[:, :j])) and np.all(np.isfinite(cl[:, :j])),
                            "C_OWNER_HISTORY_INCOMPLETE")
                    history_hashes = {
                        "python_virtual_f64le": hashlib.sha256(np.ascontiguousarray(pv[:, :j], dtype="<f8").tobytes()).hexdigest(),
                        "python_lyman_f64le": hashlib.sha256(np.ascontiguousarray(pl[:, :j], dtype="<f8").tobytes()).hexdigest(),
                        "c_virtual_f64le": hashlib.sha256(np.ascontiguousarray(cv[:, :j], dtype="<f8").tobytes()).hexdigest(),
                        "c_lyman_f64le": hashlib.sha256(np.ascontiguousarray(cl[:, :j], dtype="<f8").tobytes()).hexdigest()}
                    raw_failure = {"step": idx, "input_iz": START_IZ+idx, "bin": b,
                                   "python_raw": float(py), "c_raw": float(value),
                                   "original_gate_ratio": ratio,
                                   "original_gate_tolerance": tol,
                                   "accepted_history_sha256": history_hashes,
                                   "source_commit": "916ceddcdd0852cf290fa4691858d598a5aac12e"}
                    raw_failures.write(json.dumps(raw_failure, sort_keys=True)+"\n")
                    raw_failures.flush()
                    p = _owner("Python", states[idx], pv[:, :j], pl[:, :j], py,
                               j=j, b=b, c=c, source=source, table=table,
                               oracle=oracle, source_dir=source_dir)
                    n = _owner("C", c_step_input, cv[:, :j], cl[:, :j], value,
                               j=j, b=b, c=c, source=source, table=table,
                               oracle=oracle, source_dir=source_dir)
                    gates = numerical_gates(p, n, fbb)
                    diagnostic = {**raw_failure, "owners": [p, n], **gates}
                    diagnoses.write(json.dumps(diagnostic, sort_keys=True)+"\n")
                    diagnoses.flush()
                    require(gates["original_gate"]["status"] == "FAIL", "ORIGINAL_GATE_INCONSISTENT")
                    require(gates["decimal80_ieee_gate"]["status"] == "PASS",
                            f"ROUND_OFF_DIAGNOSTIC_HOLD:{idx}:{b}:{gates['decimal80_ieee_gate']['status']}")
                    report["average_original_failures"].append(
                        {"step": idx, "input_iz": START_IZ+idx, "bin": b, **gates})
                    require(len(report["owner_diagnostics"]) + 2 <= 128,
                            "OWNER_DIAGNOSTIC_CAP_128")
                    report["owner_diagnostics"].extend((p, n))
                report["maxima"][{"V":"virtual", "A":"average", "L":"lyman"}[tag]] = max(
                    report["maxima"][{"V":"virtual", "A":"average", "L":"lyman"}[tag]], ratio)
                report["checked_spectral_fields"] += 1
            elif tag == "END":
                require(row[1:] == ["THERMAL_EVENT_TWO_STEPS_COMPLETE", str(EVENT_IZ), "2", str(STEPS)],
                        "C_END_FIELDS")
            i = i_new
            if smoke_steps and report["checked_steps"] >= smoke_steps and phase == "STEP":
                report["status"] = "SMOKE_ONLY"
                return report
    require(phase == "DONE" and i == STEPS, "C_STREAM_TRUNCATED")
    require(event_seen and coupled == 2 and report["checked_steps"] == STEPS and
            report["checked_spectral_fields"] == STEPS*FIELDS_PER_STEP and
            report["checked_causal_links"] == STEPS*313, "FULL_COUNTS_OR_EVENT")
    require(np.all(np.isfinite(cv)) and np.all(np.isfinite(cl)), "C_OWNER_HISTORY_INCOMPLETE_END")
    report["status"] = "PASS_PENDING_INDEPENDENT_RESULT_REVIEW"
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--smoke-steps", type=int, default=0)
    parser.add_argument("--prior-evidence-dir", type=Path)
    args = parser.parse_args()
    if not 0 <= args.smoke_steps <= STEPS:
        parser.error("smoke steps outside frozen range")
    if not args.smoke_steps and args.prior_evidence_dir is None:
        parser.error("full reread requires frozen prior evidence directory")
    prior = verify_prior_audit(args.prior_evidence_dir) if args.prior_evidence_dir else None
    cpu_limit = prior["remaining_cpu_limit_s"] if prior else CPU_CAP
    wall_limit = prior["remaining_wall_limit_s"] if prior else WALL_CAP
    ev = args.evidence_dir.resolve()
    ev.mkdir(parents=True, exist_ok=False)
    affinity = sorted(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {affinity[0]})
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("AUDIT_WALL_CAP")))
    signal.alarm(wall_limit)
    start = time.monotonic()
    cpu0 = resource.getrusage(resource.RUSAGE_SELF)
    report = {"status": "FAIL", "first_failure": None,
              "mode": "SMOKE_ONLY" if args.smoke_steps else "FULL_OFFLINE_AUDIT",
              "prior_run": prior,
              "resources": {"affinity": [affinity[0]], "blas_threads": 1,
                            "address_limit_bytes": 2*1024**3, "cpu_limit_s": cpu_limit,
                            "wall_limit_s": wall_limit}}
    try:
        report["provenance"] = verify_provenance(args.input_dir, args.archive, args.checkpoint)
        report["audit"] = audit(args.input_dir, args.checkpoint, ev,
                                smoke_steps=args.smoke_steps)
        report["status"] = report["audit"]["status"]
    except BaseException as exc:
        report["first_failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        signal.alarm(0)
        cpu1 = resource.getrusage(resource.RUSAGE_SELF)
        report["resources"].update({"wall_s": time.monotonic()-start,
            "additional_cpu_s": cpu1.ru_utime+cpu1.ru_stime-cpu0.ru_utime-cpu0.ru_stime,
            "peak_rss_bytes": cpu1.ru_maxrss*1024})
        (ev / "audit.json").write_text(json.dumps(report, sort_keys=True, indent=2)+"\n")
        print(json.dumps(report, sort_keys=True))
    if report["status"] not in ("SMOKE_ONLY", "PASS_PENDING_INDEPENDENT_RESULT_REVIEW"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()

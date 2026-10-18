#!/usr/bin/env python3
"""Create-only bounded same-h U6 original-C/Python RT-boundary evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from verify_r3i_h2_start import (PINNED_SOURCE, PINNED_ZIP_SHA, sha,
    safe_extract_source, compare_state, checked_integrated_rhs_ratio)
from verify_r3i_h2_u5_thermal import CombinedOracle, KB_EV_K, LINE_EV
from verify_r3i_h2_continuation import check_one_source
from r3i_u5_average_forensic import _owner, numerical_gates
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    HyRec2012Cosmology, make_hmla_source)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import _source_edges
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u6_rt_boundary import (
    CHECKPOINT_SHA256, START_IZ, RT_IZ, PREFIX_COLUMNS, MAX_EXTRA_ACCEPTED,
    integrate_u6_rt_boundary, load_frozen_checkpoint)
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs

CPU_CAP = 110
WALL_CAP = 220
MAX_AVERAGE_FAILURES = 64
MANIFEST = ROOT/"research/rec_r3i_time_refinement_20261016/h2_u6_rt_boundary_001/SOURCE_MANIFEST_V2.json"


def process_tree_cpu_s() -> float:
    a=resource.getrusage(resource.RUSAGE_SELF)
    b=resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime


def guard_cpu(start: float, stage: str) -> int:
    remaining=CPU_CAP-(process_tree_cpu_s()-start)
    if not math.isfinite(remaining) or remaining<=1.:
        raise RuntimeError(f"U6_PROCESS_TREE_CPU_CAP:{stage}:{remaining}")
    return math.floor(remaining)


def verify_source_closure(checkpoint: Path) -> dict:
    if sha(checkpoint)!=CHECKPOINT_SHA256:
        raise ValueError("U6_CHECKPOINT_SHA")
    manifest=json.loads(MANIFEST.read_text())
    files=manifest["files"]
    for relative,digest in files.items():
        p=ROOT/relative
        if not p.is_file() or sha(p)!=digest:
            raise ValueError(f"U6_SOURCE_CLOSURE:{relative}")
    return {"manifest_sha256":sha(MANIFEST),"source_files":len(files),
            "checkpoint_sha256":CHECKPOINT_SHA256}


def causal_link_count(table, j: int) -> int:
    _,dst,src=_source_edges(table.energy_eV)
    delay=np.log(src/dst)/4.245e-5
    if not np.all(np.isfinite(delay)) or not np.all(delay>1.):
        raise ArithmeticError("U6_FREQUENCY_CAUSAL_SPACING")
    emit=j-delay
    active=emit>=0.
    if not np.all(np.floor(emit[active]).astype(np.int64)+1<=j-1):
        raise ArithmeticError(f"U6_FUTURE_PHOTON_INDEX:{j}")
    return len(delay)


def _run(cmd: list[str], cwd: Path, stdout: Path, stderr: Path,
         *, timeout: int, env: dict | None = None, cpu_start: float) -> dict:
    start = time.monotonic()
    cpu_limit=guard_cpu(cpu_start,"before_child")
    def child_limits():
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(cpu_limit,cpu_limit))
    with stdout.open("xb") as out, stderr.open("xb") as err:
        done = subprocess.run(cmd, cwd=cwd, stdout=out, stderr=err,
                              timeout=timeout, env=env, check=False,
                              preexec_fn=child_limits)
    guard_cpu(cpu_start,"after_child")
    return {"command": cmd, "returncode": done.returncode,
            "wall_s": time.monotonic()-start,
            "child_cpu_limit_s":cpu_limit,
            "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr)}


def compare_native_stream(path: Path, result, c, table, source, oracle,
                          source_dir: Path, evidence: Path,
                          guard) -> dict:
    """Audit every saved accepted field; original and shadow gates stay separate."""
    n = len(result.steps)
    cv = np.full((311, PREFIX_COLUMNS+n), np.nan)
    cl = np.full((3, PREFIX_COLUMNS+n), np.nan)
    maxima = {k: 0. for k in ("xe", "Tm_K", "hydrogen_rhs", "thermal_rhs",
                               "virtual", "average", "lyman")}
    counts = {k: 0 for k in ("PARAM", "HE", "NODE", "THERMAL_EVENT",
                             "PV", "PL", "BASE", "STEP", "V", "A", "L", "END")}
    failures = []
    c_input = None
    c_step_input = None
    end = None
    prefix_position = 0
    spectral_position = 0
    with path.open() as stream, (evidence/"average_diagnostics.jsonl").open("x") as diag, \
            (evidence/"average_raw_failures.jsonl").open("x") as raw:
        for line_no, line in enumerate(stream, 1):
            if line_no % 4096 == 0:
                guard("native_stream")
            row = line.rstrip("\n").split(",")
            tag = row[0]
            if tag not in counts:
                raise ArithmeticError(f"UNKNOWN_C_RECORD:{tag}")
            if tag == "HE" and (counts["PARAM"] != 1 or counts["NODE"]):
                raise ArithmeticError("C_HE_STAGE_ORDER")
            if tag == "NODE" and counts["HE"] != 36447:
                raise ArithmeticError("C_NODE_STAGE_ORDER")
            if tag == "THERMAL_EVENT" and (counts["NODE"] != 1 or counts["PV"]):
                raise ArithmeticError("C_EVENT_STAGE_ORDER")
            if tag in ("PV","PL") and (counts["THERMAL_EVENT"] != 1 or counts["BASE"]):
                raise ArithmeticError("C_PREFIX_STAGE_ORDER")
            if tag in ("STEP","V","A","L") and counts["BASE"] != 1:
                raise ArithmeticError("C_STEP_STAGE_ORDER")
            if tag == "END" and (counts["STEP"] != n or spectral_position != n*625):
                raise ArithmeticError("C_END_STAGE_ORDER")
            counts[tag] += 1
            if tag == "PARAM":
                if counts[tag] != 1 or tuple(map(int, row[1:])) != (RT_IZ, 21943, 58389):
                    raise ArithmeticError("C_PARAM_GRID")
            elif tag == "HE":
                if int(row[1]) != counts[tag]-1 or counts[tag] > 36447:
                    raise ArithmeticError("C_HE_ORDER")
                if any(not math.isfinite(float(q)) for q in row[2:14]):
                    raise ArithmeticError("C_HE_NONFINITE")
            elif tag == "NODE":
                if counts[tag] != 1 or int(row[1]) != RT_IZ:
                    raise ArithmeticError("C_NODE_GRID")
            elif tag == "THERMAL_EVENT":
                if counts[tag] != 1 or int(row[1]) != 53177:
                    raise ArithmeticError("C_PRIOR_THERMAL_EVENT")
                for name, value in zip(("delta", "thermal_seed_prev2", "thermal_seed_prev"), row[2:]):
                    py = result.event[name]
                    cv_value = float(value)
                    if abs(py-cv_value)/max(1., abs(cv_value)) > 2.e-10:
                        raise ArithmeticError(f"C_PRIOR_THERMAL_SEED:{name}")
            elif tag in ("PV", "PL"):
                col, b = map(int, row[1:3])
                expected_tag = "PV" if prefix_position % 314 < 311 else "PL"
                expected_col, expected_bin = divmod(prefix_position, 314)
                if expected_tag == "PL": expected_bin -= 311
                if tag != expected_tag or col != expected_col or b != expected_bin:
                    raise ArithmeticError(f"C_PREFIX_ORDER:{prefix_position}")
                value = float(row[3])
                if not math.isfinite(value): raise ArithmeticError("C_PREFIX_NONFINITE")
                (cv if tag == "PV" else cl)[b, col] = value
                py = (result.virtual_out if tag == "PV" else result.lyman_out)[b, col]
                energy = table.energy_eV[b] if tag == "PV" else LINE_EV[b]
                tr = KB_EV_K*c.T0_K*(1.+c.redshift(RT_IZ+col))
                fbb = 1./math.expm1(float(energy)/tr)
                if abs(py-value) > 1.e-7*max(abs(py),abs(value))+1.e-10*fbb:
                    raise ArithmeticError(f"C_PREFIX_PARITY:{col}:{b}:{tag}")
                prefix_position += 1
            elif tag == "BASE":
                if counts[tag] != 1 or prefix_position != PREFIX_COLUMNS*314:
                    raise ArithmeticError("C_PREFIX_INCOMPLETE_AT_BASE")
                c_input = {"iz": int(row[1]), "z": float(row[2]),
                           "xH1s": float(row[3]), "xHII": float(row[4]),
                           "xHeII": float(row[5]), "xe": float(row[6]),
                           "Tm_K": float(row[7]), "post_saha": bool(int(row[8]))}
                compare_state(result.states[0], c_input, -1)
            elif tag == "STEP":
                i = counts[tag]-1
                if (int(row[1]) != i or i >= n or int(row[2]) != START_IZ+i+1 or
                        spectral_position != i*625):
                    raise ArithmeticError(f"C_STEP_ORDER:{i}")
                native = {"iz": int(row[2]), "z": float(row[3]),
                          "xH1s": float(row[4]), "xHII": float(row[5]),
                          "xHeII": float(row[6]), "xe": float(row[7]),
                          "Tm_K": float(row[8]), "post_saha": bool(int(row[11]))}
                if c_input is None: raise ArithmeticError("C_BASE_MISSING")
                compare_state(result.states[i+1], native, i)
                step = result.steps[i]
                if (step["input_iz"] != START_IZ+i or
                        step["photon_col"] != PREFIX_COLUMNS+i or
                        not step["coupled"] or int(row[10]) != 1):
                    raise ArithmeticError(f"C_COUPLED_STAGE:{i}")
                maxima["hydrogen_rhs"] = max(maxima["hydrogen_rhs"],
                    checked_integrated_rhs_ratio(step["hydrogen_rhs"],float(row[9]),2.e-7,i,"H"))
                maxima["thermal_rhs"] = max(maxima["thermal_rhs"],
                    checked_integrated_rhs_ratio(step["thermal_rhs"],float(row[12]),2.e-7,i,"T"))
                if not 0. <= step["schur_residual"] <= 2.e-10:
                    raise ArithmeticError(f"PY_SCHUR_RESIDUAL:{i}")
                for name, floor in (("xe",1.e-8),("Tm_K",1.)):
                    maxima[name] = max(maxima[name],
                        abs(result.states[i+1][name]-native[name])/max(abs(native[name]),floor))
                c_step_input = c_input
                c_input = native
            elif tag in ("V", "A", "L"):
                i,b = map(int,row[1:3])
                expected_step, position = divmod(spectral_position,625)
                expected_tag = "V" if position < 311 else "A" if position < 622 else "L"
                expected_bin = position if position < 311 else position-311 if position < 622 else position-622
                if tag != expected_tag or i != expected_step or b != expected_bin:
                    raise ArithmeticError(f"C_SPECTRAL_ORDER:{spectral_position}")
                j = PREFIX_COLUMNS+i
                value = float(row[3])
                py = {"V":result.virtual_out,"A":result.average_virtual,
                      "L":result.lyman_out}[tag][b,j]
                if not math.isfinite(value) or not math.isfinite(py):
                    raise ArithmeticError(f"C_SPECTRUM_NONFINITE:{i}:{tag}:{b}")
                if tag == "V": cv[b,j] = value
                if tag == "L": cl[b,j] = value
                energy = LINE_EV[b] if tag == "L" else table.energy_eV[b]
                tr = KB_EV_K*c.T0_K*(1.+result.states[i]["z"])
                fbb = 1./math.expm1(float(energy)/tr)
                tol = 1.e-7*max(abs(py),abs(value))+1.e-10*fbb
                ratio = abs(py-value)/tol
                if not math.isfinite(ratio): raise ArithmeticError("C_SPECTRUM_RATIO_NONFINITE")
                if ratio > 1.:
                    if tag != "A" or len(failures) >= MAX_AVERAGE_FAILURES:
                        raise ArithmeticError(f"C_SPECTRUM_PARITY:{i}:{tag}:{b}:{ratio}")
                    if not (np.all(np.isfinite(cv[:,:j])) and np.all(np.isfinite(cl[:,:j]))):
                        raise ArithmeticError("C_OWNER_HISTORY_INCOMPLETE")
                    history_hashes={
                        "python_virtual_f64le":hashlib.sha256(np.ascontiguousarray(result.virtual_out[:,:j],dtype="<f8").tobytes()).hexdigest(),
                        "python_lyman_f64le":hashlib.sha256(np.ascontiguousarray(result.lyman_out[:,:j],dtype="<f8").tobytes()).hexdigest(),
                        "c_virtual_f64le":hashlib.sha256(np.ascontiguousarray(cv[:,:j],dtype="<f8").tobytes()).hexdigest(),
                        "c_lyman_f64le":hashlib.sha256(np.ascontiguousarray(cl[:,:j],dtype="<f8").tobytes()).hexdigest()}
                    raw_failure={"step":i,"input_iz":START_IZ+i,"bin":b,
                                 "python_raw":float(py),"c_raw":float(value),
                                 "original_gate_ratio":ratio,"accepted_history_sha256":history_hashes,
                                 "checkpoint_sha256":CHECKPOINT_SHA256,
                                 "common_binary_sha256":sha(Path(oracle.h.lib._name))}
                    raw.write(json.dumps(raw_failure,sort_keys=True)+"\n");raw.flush()
                    p = _owner("Python",result.states[i],result.virtual_out[:,:j],
                               result.lyman_out[:,:j],py,j=j,b=b,c=c,source=source,
                               table=table,oracle=oracle,source_dir=source_dir)
                    nowner = _owner("C",c_step_input,cv[:,:j],cl[:,:j],value,
                                    j=j,b=b,c=c,source=source,table=table,
                                    oracle=oracle,source_dir=source_dir)
                    gates = numerical_gates(p,nowner,fbb)
                    diagnostic = {**raw_failure,"owners":[p,nowner],**gates}
                    diag.write(json.dumps(diagnostic,sort_keys=True)+"\n")
                    diag.flush()
                    if (gates["original_gate"]["status"] != "FAIL" or
                            gates["decimal80_ieee_gate"]["status"] != "PASS"):
                        raise ArithmeticError(f"C_AVERAGE_DIAGNOSTIC_HOLD:{i}:{b}")
                    failures.append({"step":i,"bin":b,"original_gate":gates["original_gate"],
                                     "decimal80_ieee_gate":gates["decimal80_ieee_gate"]})
                maxima[{"V":"virtual","A":"average","L":"lyman"}[tag]] = max(
                    maxima[{"V":"virtual","A":"average","L":"lyman"}[tag]],ratio)
                spectral_position += 1
            elif tag == "END":
                end = {"status":row[1],"event_iz":int(row[2]),
                       "coupled":int(row[3]),"steps":int(row[4])}
    expected = {"PARAM":1,"HE":36447,"NODE":1,"THERMAL_EVENT":1,
                "PV":PREFIX_COLUMNS*311,"PL":PREFIX_COLUMNS*3,"BASE":1,
                "STEP":n,"V":n*311,"A":n*311,"L":n*3,"END":1}
    if counts != expected or spectral_position != n*625:
        raise ArithmeticError(f"C_COUNTS:{counts}:{expected}")
    if (end is None or end["status"] != result.status or end["event_iz"] != 53177 or
            end["coupled"] != n+2 or end["steps"] != n or
            not np.all(np.isfinite(cv)) or not np.all(np.isfinite(cl))):
        raise ArithmeticError(f"C_END_OR_HISTORY:{end}")
    return {"status":"PASS_PENDING_REVIEW","counts":counts,
            "spectral_fields":spectral_position,"causal_links":313*n,
            "maxima":maxima,"original_average_failures":failures,"end":end}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint",type=Path,required=True)
    ap.add_argument("--evidence-dir",type=Path,required=True)
    ap.add_argument("--max-extra-accepted",type=int,default=MAX_EXTRA_ACCEPTED)
    args = ap.parse_args()
    if not 1 <= args.max_extra_accepted <= MAX_EXTRA_ACCEPTED:
        ap.error("max-extra-accepted outside 1..5210")
    ev = args.evidence_dir.resolve()
    ev.mkdir(parents=True,exist_ok=False)
    affinity = sorted(os.sched_getaffinity(0))
    os.sched_setaffinity(0,{affinity[0]})
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU_CAP,CPU_CAP))
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("U6_WALL_CAP")))
    signal.alarm(WALL_CAP)
    start = time.monotonic(); usage0 = resource.getrusage(resource.RUSAGE_SELF)
    cpu0=process_tree_cpu_s()
    report = {"status":"FAIL","first_failure":None,
              "source_zip_sha256":PINNED_ZIP_SHA,"checkpoint_sha256":CHECKPOINT_SHA256,
              "resources":{"affinity":[affinity[0]],"blas_threads":1,
                           "address_limit_bytes":2*1024**3,
                           "cpu_limit_s":CPU_CAP,"wall_limit_s":WALL_CAP}}
    try:
        report["source_closure"]=verify_source_closure(args.checkpoint)
        cp = load_frozen_checkpoint(args.checkpoint)
        source_dir = safe_extract_source(
            ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip",
            ev/"source_extract")
        header = source_dir/"hyrec_params.h"
        before = header.read_bytes(); token=b"#define DLNA          8.49e-5"
        if before.count(token)!=1: raise ValueError("ACTIVE_DLNA_TOKEN_NOT_UNIQUE")
        header.write_bytes(before.replace(token,b"#define DLNA          (8.49e-5/2.)"))
        report["modified_source_sha256"]={name:sha(source_dir/name) for name in PINNED_SOURCE}
        harness=ROOT/"scripts/c_harness/original_hyrec_r3i_h2_u6_rt_boundary_harness.c"
        sources=[str(source_dir/name) for name in ("history.c","hydrogen.c","helium.c","hyrectools.c")]
        env=os.environ.copy()
        native=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(source_dir),
                str(harness),*sources,"-lm","-o",str(ev/"native_u6_rt")]
        report["native_build"]=_run(native,source_dir,ev/"native_build_stdout.txt",
                                     ev/"native_build_stderr.txt",timeout=60,env=env,cpu_start=cpu0)
        if report["native_build"]["returncode"]: raise RuntimeError("NATIVE_C_BUILD_FAILED")
        shared=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-DR3I_SHARED",
                "-I",str(source_dir),str(harness),*sources,"-lm","-o",str(ev/"liboriginal_full_source.so")]
        report["common_build"]=_run(shared,source_dir,ev/"common_build_stdout.txt",
                                     ev/"common_build_stderr.txt",timeout=60,env=env,cpu_start=cpu0)
        if report["common_build"]["returncode"]: raise RuntimeError("COMMON_C_BUILD_FAILED")
        report["native_binary_sha256"]=sha(ev/"native_u6_rt")
        report["common_binary_sha256"]=sha(ev/"liboriginal_full_source.so")
        c=HyRec2012Cosmology()
        rates=OriginalHyRecPrimitiveRateTable.from_archive(
            ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        table=_canonical_twophoton_table(rates.archive_path)
        source=make_hmla_source(c,rates)
        oracle=CombinedOracle(ev/"liboriginal_full_source.so",source_dir,c)
        metrics={"sampled_evaluations":0,"max_rhs_scaled":0.,
                 "max_virtual_tolerance_ratio":0.,"max_average_tolerance_ratio":0.,
                 "max_lyman_tolerance_ratio":0.,"max_thermal_rhs_scaled":0.}
        causal={"checked_links":0,"accepted_inputs":0}
        def observer(g,z,xh,tm,vh,lh,out):
            guard_cpu(cpu0,"atomic_source_observer")
            causal["checked_links"]+=causal_link_count(table,g-RT_IZ)
            causal["accepted_inputs"]+=1
            if g in (START_IZ,START_IZ+1) or (g-START_IZ)%128==0:
                j=g-RT_IZ
                check_one_source(oracle,table,j,z,xh,0.,tm,vh,lh,out,metrics)
                py=source_thermal_rhs(c,xh,tm,z)
                cv=oracle.thermal_rhs(xh,tm,z)
                ratio=abs(py-cv)/max(1.,abs(cv))
                if not math.isfinite(ratio) or ratio>2.e-10:
                    raise ArithmeticError(f"COMMON_INPUT_THERMAL_RHS:{g}:{ratio}")
                metrics["max_thermal_rhs_scaled"]=max(metrics["max_thermal_rhs_scaled"],ratio)
        result=integrate_u6_rt_boundary(cp,c,source,
            max_extra_accepted=args.max_extra_accepted,
            max_full_evaluations=args.max_extra_accepted,observer=observer)
        report["python_result"]={"status":result.status,"steps":len(result.steps),
            "full_evaluations":result.full_evaluations,"rt_stop_iz":result.rt_stop_iz}
        if causal != {"checked_links":313*len(result.steps),
                      "accepted_inputs":len(result.steps)}:
            raise ArithmeticError("U6_CAUSAL_LINK_COUNT")
        report["causal_links"]=causal
        report["common_input_sample"]={"status":"PASS",**metrics}
        np.savez_compressed(ev/"python_u6_rt.npz",
            states_json=np.array([json.dumps(s,sort_keys=True) for s in result.states]),
            steps_json=np.array([json.dumps(s,sort_keys=True) for s in result.steps]),
            virtual_out=result.virtual_out,average_virtual=result.average_virtual,
            lyman_out=result.lyman_out)
        report["python_history_sha256"]=sha(ev/"python_u6_rt.npz")
        native_env=env.copy();native_env["R3I_MAX_EXTRA_ACCEPTED"]=str(args.max_extra_accepted)
        report["native_run"]=_run([str(ev/"native_u6_rt")],source_dir,
            ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",
            timeout=120,env=native_env,cpu_start=cpu0)
        if report["native_run"]["returncode"]: raise RuntimeError("NATIVE_C_ORACLE_FAILED")
        report["same_h_parity"]=compare_native_stream(
            ev/"native_oracle_stdout.csv",result,c,table,source,oracle,source_dir,ev,
            lambda stage:guard_cpu(cpu0,stage))
        guard_cpu(cpu0,"final")
        report["status"]=("SMOKE_ONLY" if args.max_extra_accepted<MAX_EXTRA_ACCEPTED else
                          "PASS_PENDING_INDEPENDENT_REVIEW")
    except BaseException as exc:
        report["first_failure"]={"type":type(exc).__name__,"message":str(exc)}
    finally:
        signal.alarm(0)
        usage=resource.getrusage(resource.RUSAGE_SELF)
        report["resources"].update({"wall_s":time.monotonic()-start,
            "parent_cpu_s":usage.ru_utime+usage.ru_stime-usage0.ru_utime-usage0.ru_stime,
            "process_tree_cpu_s":process_tree_cpu_s()-cpu0,
            "peak_rss_bytes":usage.ru_maxrss*1024})
        (ev/"verification.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print(json.dumps(report,sort_keys=True))
    if report["status"] not in ("SMOKE_ONLY","PASS_PENDING_INDEPENDENT_REVIEW"):
        raise SystemExit(2)


if __name__=="__main__": main()

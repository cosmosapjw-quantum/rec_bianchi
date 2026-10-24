#!/usr/bin/env python3
"""Create-only, bounded same-h Python/C verification of H post-Saha exit."""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
import math
import os
os.environ.update({k:"1" for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS",
                              "MKL_NUM_THREADS","NUMEXPR_NUM_THREADS")})
from pathlib import Path
import resource
import signal
import sys
import time

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from verify_r3i_h2_start import (PINNED_SOURCE,PINNED_ZIP_SHA,FullSourceCOracle,
    check_sources,compare_state,checked_integrated_rhs_ratio,safe_extract_source,sha)
from verify_r3i_h2_continuation import (
    CPU_BUDGET_S,check_one_source,checked_cpu_budget,enforce_final_cpu_gate,
    run_capture_budgeted,select_event_sample_calls,serializable_step,
    total_process_tree_cpu_s,
)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology,make_hmla_source
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u4_exit import (
    CHECKPOINT_SHA256,MAX_EXTRA_ACCEPTED,MAX_FULL_EVALUATIONS,
    PREFIX_COLUMNS,RT_IZ,START_IZ,integrate_u4_exit,load_frozen_checkpoint,
)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table

MANIFEST=ROOT/"research/rec_r3i_time_refinement_20261016/h2_u4_post_saha_exit_001/SOURCE_MANIFEST_V2.json"
LINE_EV=(10.198714553953742,12.087365397278509,12.748393192442178)
KB_EV_K=8.617343e-5


def verify_source_closure(checkpoint:Path) -> dict:
    if sha(checkpoint)!=CHECKPOINT_SHA256:
        raise ValueError("REVIEWED_H2_CONTINUATION_CHECKPOINT_SHA_MISMATCH")
    manifest=json.loads(MANIFEST.read_text())
    for relative,digest in manifest["files"].items():
        path=ROOT/relative
        if not path.is_file() or sha(path)!=digest:
            raise ValueError(f"CAPSULE_SOURCE_CLOSURE_MISSING_OR_CHANGED:{relative}")
    return {"manifest_sha256":sha(MANIFEST),"files":len(manifest["files"]),
            "checkpoint_sha256":CHECKPOINT_SHA256}


def compare_new_native_stream(path:Path,result,c,table,guard) -> dict:
    counts={k:0 for k in ("PARAM","HE","NODE","BASE","STEP","V","A","L","EVENT")}
    maxerr={k:0. for k in ("xe","xHII","xHeII","Tm_K","hydrogen_rhs",
                              "virtual","average","lyman")}
    event=None
    with path.open() as stream:
        for line_no,line in enumerate(stream,1):
            if line_no%4096==0:guard("native_stdout_stream")
            row=line.rstrip("\n").split(",")
            tag=row[0]
            if tag not in counts:
                raise ValueError(f"UNKNOWN_NATIVE_RECORD:{tag}")
            counts[tag]+=1
            if tag=="PARAM":
                if int(row[1])!=RT_IZ or int(row[3])!=result.rt_stop_iz:
                    raise ArithmeticError(f"RT_STOP_INDEX_PARITY:C={row}:P={result.rt_stop_iz}")
                continue
            if tag=="BASE":
                native={"iz":int(row[1]),"z":float(row[2]),"xH1s":float(row[3]),
                        "xHII":float(row[4]),"xHeII":float(row[5]),"xe":float(row[6]),
                        "Tm_K":float(row[7]),"post_saha":bool(int(row[8]))}
                compare_state(result.states[0],native,-1)
                continue
            if tag in ("HE","NODE"):continue
            if tag=="STEP":
                i=int(row[1])
                if i!=counts[tag]-1 or i>=len(result.steps):
                    raise ArithmeticError(f"C_STEP_SEQUENCE:{i}")
                native={"iz":int(row[2]),"z":float(row[3]),"xH1s":float(row[4]),
                        "xHII":float(row[5]),"xHeII":float(row[6]),"xe":float(row[7]),
                        "Tm_K":float(row[8]),"post_saha":bool(int(row[11]))}
                py=result.states[i+1]
                compare_state(py,native,i)
                if py["iz"]!=START_IZ+i+1 or int(row[12])!=0:
                    raise ArithmeticError(f"C_BRANCH_OR_INDEX:{i}")
                step=result.steps[i]
                maxerr["hydrogen_rhs"]=max(maxerr["hydrogen_rhs"],
                    checked_integrated_rhs_ratio(step["hydrogen_rhs"],float(row[9]),2.e-7,i,"H"))
                for field,floor in (("xe",1.e-8),("xHII",1.e-8),("xHeII",1.),("Tm_K",1.)):
                    maxerr[field]=max(maxerr[field],abs(py[field]-native[field])/
                                      max(abs(native[field]),floor))
                continue
            if tag in ("V","A","L"):
                i,b=int(row[1]),int(row[2])
                if i>=len(result.steps):raise ArithmeticError(f"C_SPECTRUM_STEP:{i}")
                j=PREFIX_COLUMNS+i
                py={"V":result.virtual_out,"A":result.average_virtual,
                    "L":result.lyman_out}[tag][b,j]
                cv=float(row[3])
                energy=LINE_EV[b] if tag=="L" else table.energy_eV[b]
                tr=KB_EV_K*c.T0_K*(1.+c.redshift(START_IZ+i))
                fbb=1./math.expm1(energy/tr)
                tol=1.e-7*max(abs(py),abs(cv))+1.e-10*fbb
                ratio=abs(py-cv)/tol
                if not math.isfinite(ratio) or ratio>1.:
                    raise ArithmeticError(f"INTEGRATED_PHOTON_PARITY:i={i}:tag={tag}:bin={b}:ratio={ratio:.17g}")
                field={"V":"virtual","A":"average","L":"lyman"}[tag]
                maxerr[field]=max(maxerr[field],ratio)
                continue
            if tag=="EVENT":
                event={"relative_index":int(row[1]),"type":int(row[2]),
                       "steps":int(row[3])}
    n=len(result.steps)
    if counts!={"PARAM":1,"HE":36447,"NODE":1,"BASE":1,"STEP":n,"V":311*n,"A":311*n,
                "L":3*n,"EVENT":1}:
        raise ArithmeticError(f"C_ROW_COUNT:{counts}")
    expected_event=-1 if result.event is None else result.event["iz"]-START_IZ
    if event is None or event["relative_index"]!=expected_event or event["type"]!=(2 if result.event else 0):
        raise ArithmeticError(f"C_PY_EVENT_MISMATCH:C={event}:P={result.event}")
    guard("native_stdout_complete")
    return {"status":"PASS","counts":counts,"maxima":maxerr,"native_event":event}


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--checkpoint",type=Path,required=True)
    ap.add_argument("--evidence-dir",type=Path,required=True)
    ap.add_argument("--max-extra-accepted",type=int,default=MAX_EXTRA_ACCEPTED)
    args=ap.parse_args()
    if not 1<=args.max_extra_accepted<=MAX_EXTRA_ACCEPTED:
        ap.error("--max-extra-accepted must be in 1..4096")
    ev=args.evidence_dir.resolve()
    ev.mkdir(parents=True,exist_ok=False)
    t0=time.monotonic();cpu0=total_process_tree_cpu_s();usage0=resource.getrusage(resource.RUSAGE_SELF)
    affinity=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity[0]})
    report={"status":"FAIL","first_failure":None,"claim":"bounded q=0 h/2 U4 post-Saha exit only",
            "checkpoint_sha256":CHECKPOINT_SHA256,"source_zip_sha256":PINNED_ZIP_SHA,
            "source_sha256":PINNED_SOURCE,"producer_sha256":sha(ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_refined_u4_exit.py"),
            "harness_sha256":sha(ROOT/"scripts/c_harness/original_hyrec_r3i_h2_u4_exit_harness.c"),
            "old_U5_gate":"HOLD","resources":{"affinity":[affinity[0]],
            "blas_threads":1,"address_limit_bytes":2*1024**3,
            "cpu_limit_s":600,"wall_limit_s":900}}
    try:
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(600,600))
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("U4_EXIT_WALL_900S")))
        signal.alarm(900)
        report["capsule_source_closure"]=verify_source_closure(args.checkpoint)
        cp=load_frozen_checkpoint(args.checkpoint)
        source_dir=safe_extract_source(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip",ev/"source_extract")
        header=source_dir/"hyrec_params.h"
        before=header.read_bytes();token=b"#define DLNA          8.49e-5"
        if before.count(token)!=1:raise ValueError("ACTIVE_DLNA_TOKEN_NOT_UNIQUE")
        after=before.replace(token,b"#define DLNA          (8.49e-5/2.)")
        header.write_bytes(after)
        if after.replace(b"#define DLNA          (8.49e-5/2.)",token)!=before:
            raise ValueError("SOURCE_CHANGE_EXCEEDS_ONE_DLNA_TOKEN")
        report["modified_source_sha256"]={name:sha(source_dir/name) for name in PINNED_SOURCE}
        harness=ROOT/"scripts/c_harness/original_hyrec_r3i_h2_u4_exit_harness.c"
        sources=[str(source_dir/name) for name in ("history.c","hydrogen.c","helium.c","hyrectools.c")]
        env=os.environ.copy()
        native_cmd=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(source_dir),
                    str(harness),*sources,"-lm","-o",str(ev/"native_u4_exit")]
        report["native_build"]=run_capture_budgeted(native_cmd,source_dir,ev/"native_build_stdout.txt",ev/"native_build_stderr.txt",60,env,cpu0)
        if report["native_build"]["returncode"]:raise RuntimeError("NATIVE_C_BUILD_FAILED")
        shared_cmd=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-DR3I_SHARED",
                    "-I",str(source_dir),str(harness),
                    *[str(source_dir/name) for name in ("hydrogen.c","helium.c","hyrectools.c")],
                    "-lm","-o",str(ev/"liboriginal_full_source.so")]
        report["common_build"]=run_capture_budgeted(shared_cmd,source_dir,ev/"common_build_stdout.txt",ev/"common_build_stderr.txt",60,env,cpu0)
        if report["common_build"]["returncode"]:raise RuntimeError("COMMON_C_BUILD_FAILED")
        report["native_binary_sha256"]=sha(ev/"native_u4_exit")
        report["common_binary_sha256"]=sha(ev/"liboriginal_full_source.so")
        c=HyRec2012Cosmology()
        rates=OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        table=_canonical_twophoton_table(rates.archive_path)
        source=make_hmla_source(c,rates)
        oracle=FullSourceCOracle(ev/"liboriginal_full_source.so",source_dir,c)
        metrics={"sampled_evaluations":0,"max_rhs_scaled":0.,"max_virtual_tolerance_ratio":0.,
                 "max_average_tolerance_ratio":0.,"max_lyman_tolerance_ratio":0.}
        tail=[];online={};serial=0
        def observer(g,z,xh,tm,vh,lh,out):
            nonlocal serial
            checked_cpu_budget(cpu0,"atomic_source_observer")
            serial+=1
            j=g-RT_IZ
            if j in (PREFIX_COLUMNS,PREFIX_COLUMNS+1,PREFIX_COLUMNS+2) or (j-PREFIX_COLUMNS)%128==0:
                check_one_source(oracle,table,j,z,xh,0.,tm,vh,lh,out,metrics)
                online[serial]=g
            tail.append((serial,g,z,xh,tm,out))
            if len(tail)>256:del tail[0]
        def on_accept(state,step,out):
            checked_cpu_budget(cpu0,"accepted_step")
            accepted.write(json.dumps({"state":state,"step":serializable_step(step)},
                                      allow_nan=False,separators=(",",":"))+"\n")
            accepted.flush()
            part_v.write(np.asarray(out.outgoing_virtual,dtype="<f8").tobytes())
            part_a.write(np.asarray(out.average_virtual,dtype="<f8").tobytes())
            part_l.write(np.asarray(out.outgoing_lyman,dtype="<f8").tobytes())
        with ExitStack() as stack:
            accepted=stack.enter_context((ev/"python_accepted_partial.jsonl").open("x"))
            part_v=stack.enter_context((ev/"python_partial_virtual_f64le.bin").open("xb"))
            part_a=stack.enter_context((ev/"python_partial_average_f64le.bin").open("xb"))
            part_l=stack.enter_context((ev/"python_partial_lyman_f64le.bin").open("xb"))
            result=integrate_u4_exit(cp,c,source,
                max_extra_accepted=args.max_extra_accepted,
                max_full_evaluations=min(MAX_FULL_EVALUATIONS,4*args.max_extra_accepted),
                observer=observer,on_accept=on_accept)
        report["python_result"]={"status":result.status,"event":result.event,
            "extra_accepted":len(result.steps),"full_evaluations":result.full_evaluations,
            "rt_stop_iz":result.rt_stop_iz}
        if result.event:
            selected,sampling=select_event_sample_calls(tail,online,result.event["iz"])
            for _,g,z,xh,tm,out in selected:
                checked_cpu_budget(cpu0,"event_common_input")
                j=g-RT_IZ
                check_one_source(oracle,table,j,z,xh,0.,tm,
                                 result.virtual_out[:,:j],result.lyman_out[:,:j],out,metrics)
            report["event_neighborhood_sampling"]=sampling
        report["common_input_sample"]={"status":"PASS",**metrics}
        np.savez_compressed(ev/"python_u4_exit.npz",
            states_json=np.array([json.dumps(s,sort_keys=True) for s in result.states]),
            steps_json=np.array([json.dumps(serializable_step(s),sort_keys=True) for s in result.steps]),
            virtual_out=result.virtual_out,average_virtual=result.average_virtual,
            lyman_out=result.lyman_out)
        report["python_history_sha256"]=sha(ev/"python_u4_exit.npz")
        native_env=env.copy();native_env["R3I_MAX_EXTRA_ACCEPTED"]=str(args.max_extra_accepted)
        report["native_run"]=run_capture_budgeted([str(ev/"native_u4_exit")],source_dir,
            ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",600,native_env,cpu0)
        if report["native_run"]["returncode"]:raise RuntimeError("NATIVE_C_ORACLE_FAILED")
        report["same_h_parity"]=compare_new_native_stream(ev/"native_oracle_stdout.csv",result,c,table,
            lambda stage:checked_cpu_budget(cpu0,stage))
        checked_cpu_budget(cpu0,"before_final_status")
        report["status"]=("SMOKE_ONLY" if args.max_extra_accepted<MAX_EXTRA_ACCEPTED else
                          "PASS_PENDING_INDEPENDENT_REVIEW" if result.status=="EVENT_PLUS_TWO" else
                          "HOLD_CAP_BEFORE_EVENT_PLUS_TWO")
    except BaseException as exc:
        report["first_failure"]={"type":type(exc).__name__,"message":str(exc)}
        (ev/"failure.txt").write_text(f"{type(exc).__name__}: {exc}\n")
    finally:
        signal.alarm(0)
        report["partial_accepted_sha256"]={name:sha(ev/name) for name in (
            "python_accepted_partial.jsonl","python_partial_virtual_f64le.bin",
            "python_partial_average_f64le.bin","python_partial_lyman_f64le.bin") if (ev/name).is_file()}
        u1=resource.getrusage(resource.RUSAGE_SELF);children=resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu_used=total_process_tree_cpu_s()-cpu0
        report["resources"].update({"wall_s":time.monotonic()-t0,
            "parent_cpu_s":u1.ru_utime+u1.ru_stime-usage0.ru_utime-usage0.ru_stime,
            "children_cpu_s":children.ru_utime+children.ru_stime,
            "parent_peak_rss_bytes":u1.ru_maxrss*1024,"children_peak_rss_bytes":children.ru_maxrss*1024,
            "cumulative_process_tree_cpu_s":cpu_used})
        enforce_final_cpu_gate(report,cpu_used)
        (ev/"verification.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print(json.dumps(report,sort_keys=True,indent=2))
    if report["status"] not in ("SMOKE_ONLY","PASS_PENDING_INDEPENDENT_REVIEW",
                                "HOLD_CAP_BEFORE_EVENT_PLUS_TWO"):
        raise SystemExit(2)


if __name__=="__main__":main()

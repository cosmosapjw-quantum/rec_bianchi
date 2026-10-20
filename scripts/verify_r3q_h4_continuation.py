#!/usr/bin/env python3
"""R3Q independent h4 event continuation worker; invoke through its supervisor."""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
import math
import os
os.environ.update({"OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1",
                   "MKL_NUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1"})
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"scripts"))
from verify_r3i_h2_start import (PINNED_SOURCE,PINNED_ZIP_SHA,FullSourceCOracle,
    check_sources,compare_state,checked_integrated_rhs_ratio,
    safe_extract_source,sha)
from full_bianchi_hyrec.trajectory.primordial_2012_quarter_start import (
    QuarterStartCosmology as HyRec2012Cosmology, make_hmla_source)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    checked_common_input_rhs_ratio,checked_common_input_spectrum_ratio)
from verify_r3o_h4_start import prepare_source
from full_bianchi_hyrec.trajectory.primordial_2012_quarter_continuation import (
    CHECKPOINT_SHA256,MAX_EXTRA_ACCEPTED,MAX_FULL_EVALUATIONS,
    integrate_continuation,load_frozen_start)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table

LINE_EV=np.array((10.198714553953742,12.087365397278509,12.748393192442178))
KB_EV_K=8.617343e-5
CPU_BUDGET_S=600
WORK_CPU_BUDGET_S=595
WALL_DEADLINE=math.inf
MANIFEST_RELATIVE=Path("research/rec_r3q_h4_continuation_20261020/SOURCE_CLOSURE.json")


def verify_capsule_source_closure(root:Path,checkpoint:Path):
    manifest_path=root/MANIFEST_RELATIVE
    if not manifest_path.is_file():
        raise FileNotFoundError(f"CAPSULE_SOURCE_MANIFEST_MISSING:{manifest_path}")
    manifest=json.loads(manifest_path.read_text())
    files=manifest.get("files")
    if not isinstance(files,dict) or not files:
        raise ValueError("CAPSULE_SOURCE_MANIFEST_EMPTY")
    for relative,expected in files.items():
        path=root/relative
        if not path.is_file() or sha(path)!=expected:
            raise ValueError(f"CAPSULE_SOURCE_CLOSURE_MISSING_OR_CHANGED:{relative}")
    if sha(checkpoint)!=CHECKPOINT_SHA256:
        raise ValueError("CAPSULE_CHECKPOINT_SHA_MISMATCH")
    return {"manifest_sha256":sha(manifest_path),"verified_files":len(files),
            "checkpoint_sha256":CHECKPOINT_SHA256}


def total_process_tree_cpu_s():
    own=resource.getrusage(resource.RUSAGE_SELF)
    children=resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime+own.ru_stime+children.ru_utime+children.ru_stime


def checked_cpu_budget(cpu_start:float,stage:str):
    used=total_process_tree_cpu_s()-cpu_start
    if not math.isfinite(used) or used>=WORK_CPU_BUDGET_S or time.monotonic()>=WALL_DEADLINE:
        raise RuntimeError(f"CUMULATIVE_CPU_CAP:{stage}:used_s={used:.6f}")
    return WORK_CPU_BUDGET_S-used


def enforce_final_cpu_gate(report:dict,used_s:float):
    """Make a measured process-tree CPU overrun an explicit failed result."""
    if not math.isfinite(used_s) or used_s>=CPU_BUDGET_S:
        report["status"]="FAIL_CPU_CAP"
        failure={"type":"CPU_CAP","message":
                 f"CUMULATIVE_CPU_CAP:final:used_s={used_s:.6f}"}
        if report.get("first_failure") is None:
            report["first_failure"]=failure
        else:
            report["cpu_cap_failure"]=failure
    return report


def run_capture_budgeted(cmd:list[str],cwd:Path,stdout:Path,stderr:Path,
                         timeout:float,env:dict,cpu_start:float):
    remaining=checked_cpu_budget(cpu_start,"before_child")
    # A child cannot consume more than the remaining process-tree allowance.
    # floor is conservative; minimum one second is used only when at least
    # one full second remains.
    child_cpu=int(math.floor(remaining))
    if child_cpu<1:
        raise RuntimeError("CUMULATIVE_CPU_CAP_BEFORE_CHILD")
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(child_cpu,child_cpu))
    t0=time.monotonic()
    with stdout.open("xb") as out,stderr.open("xb") as err:
        done=subprocess.run(cmd,cwd=cwd,stdout=out,stderr=err,timeout=min(timeout,max(.001,WALL_DEADLINE-time.monotonic())),
                            env=env,preexec_fn=limits,check=False)
    remaining_after=checked_cpu_budget(cpu_start,"after_child")
    return {"command":cmd,"returncode":done.returncode,"wall_s":time.monotonic()-t0,
            "stdout_sha256":sha(stdout),"stderr_sha256":sha(stderr),
            "child_cpu_cap_s":child_cpu,"cumulative_cpu_remaining_s":remaining_after}


def serializable_step(step:dict)->dict:
    out={}
    branch=step.get("branch")
    for name,value in step.items():
        if name=="helium_rhs" and branch=="H_ONLY":
            if not isinstance(value,(int,float)) or not math.isnan(value):
                raise ArithmeticError("H_ONLY_HELIUM_RHS_SENTINEL_NOT_NAN")
            out[name]=None
        elif isinstance(value,(int,float)):
            if not math.isfinite(value):
                raise ArithmeticError(f"NONFINITE_ACCEPTED_STEP:{name}")
            out[name]=value
        else:
            out[name]=value
    return out


def select_event_sample_calls(tail:list,online_sampled:dict[int,int],event_g:int):
    """Choose at most 64 distinct atomic calls, counting regular samples."""
    low,high=event_g-64,event_g+2
    already={serial for serial,g in online_sampled.items() if low<=g<=high}
    if len(already)>64:
        raise ArithmeticError("EVENT_SAMPLING_CAP_ONLINE_EXCEEDED")
    eligible=[entry for entry in tail
              if low<=entry[1]<=high and entry[0] not in already]
    remaining=64-len(already)
    chosen=eligible[-remaining:] if remaining else []
    if len(already)+len(chosen)>64:
        raise ArithmeticError("EVENT_SAMPLING_CAP_EXCEEDED")
    return chosen,{"candidate_call_window":[low,high],
                   "online_calls":len(already),"new_calls":len(chosen),
                   "total_calls":len(already)+len(chosen),"limit_calls":64,
                   "status":"PASS"}


def check_one_source(oracle,source_table,j,z,xh,xhe,tm,vh,lh,out,metrics):
    cs=oracle(j,z,xh,xhe,tm,vh,lh)
    r=checked_common_input_rhs_ratio(out.dxHII_dln_a,cs["rhs"],j)
    metrics["max_rhs_scaled"]=max(metrics["max_rhs_scaled"],r)
    if r>2.e-10: raise ArithmeticError(f"COMMON_INPUT_FULL_RHS_PARITY:j={j}:ratio={r:.17g}")
    tr=KB_EV_K*oracle.c.T0_K*(1.+z)
    fbb_v=1./np.expm1(source_table.energy_eV/tr)
    fbb_l=1./np.expm1(LINE_EV/tr)
    for name,p,cv,fb in (("virtual",out.outgoing_virtual,cs["virtual"],fbb_v),
                          ("average",out.average_virtual,cs["average"],fbb_v),
                          ("lyman",out.outgoing_lyman,cs["lyman"],fbb_l)):
        ratios=checked_common_input_spectrum_ratio(p,cv,fb,j)
        val=float(np.max(ratios)); metrics[f"max_{name}_tolerance_ratio"]=max(
            metrics[f"max_{name}_tolerance_ratio"],val)
        if val>1.: raise ArithmeticError(f"COMMON_INPUT_PHOTON_PARITY:j={j}:field={name}:bin={int(np.argmax(ratios))}:ratio={val:.17g}")
    metrics["sampled_evaluations"]+=1


def compare_native_stream(path,checkpoint,result,c,table,cpu_guard=None):
    maxima={"xHII":0.,"xe":0.,"xHeII":0.,"Tm_K":0.,"hydrogen_rhs":0.,
            "helium_rhs":0.,"virtual":0.,"average":0.,"lyman":0.}
    counts={"STEP":0,"V":0,"A":0,"L":0,"HE":0,"NODE":0,"EVENT":0}
    event=None
    with path.open() as f:
        for line_number,line in enumerate(f,1):
            if cpu_guard is not None and line_number%8192==0:
                cpu_guard("native_stdout_stream")
            v=line.rstrip("\n").split(",")
            tag=v[0]
            if counts["EVENT"]:
                raise ArithmeticError("C_RECORD_AFTER_TERMINAL_EVENT")
            if tag=="HE":
                counts["HE"]+=1
                continue
            if tag=="NODE":
                counts["NODE"]+=1
                if int(v[1])!=72892: raise ArithmeticError("C_START_INDEX")
                continue
            if tag=="STEP":
                j=int(v[1]); counts[tag]+=1
                if j!=counts[tag]-1: raise ArithmeticError(f"C_STEP_SEQUENCE:{j}")
                is_he=bool(int(v[12]))
                expected=(
                    {"iz":int(checkpoint["iz"][j+1]),"z":float(checkpoint["z"][j+1]),
                     "xH1s":float(checkpoint["xH1s"][j+1]),"xHII":float(checkpoint["xHII"][j+1]),
                     "xHeII":float(checkpoint["xHeII"][j+1]),"xe":float(checkpoint["xe"][j+1]),
                     "Tm_K":float(checkpoint["Tm_K"][j+1]),"post_saha":bool(checkpoint["post_saha"][j+1])}
                    if j<8 else result.states[j-7])
                native={"iz":int(v[2]),"z":float(v[3]),"xH1s":float(v[4]),
                        "xHII":float(v[5]),"xHeII":float(v[6]),"xe":float(v[7]),
                        "Tm_K":float(v[8]),"post_saha":bool(int(v[11]))}
                compare_state(expected,native,j)
                if j>=8:
                    step=result.steps[j-8]
                    if (step["input_iz"]!=72892+j or (step["branch"]=="H_HE")!=is_he):
                        raise ArithmeticError(f"C_BRANCH_OR_INPUT_INDEX:{j}")
                    maxima["hydrogen_rhs"]=max(maxima["hydrogen_rhs"],
                        checked_integrated_rhs_ratio(step["hydrogen_rhs"],float(v[9]),2.e-7,j,"H"))
                    if is_he:
                        maxima["helium_rhs"]=max(maxima["helium_rhs"],
                            checked_integrated_rhs_ratio(step["helium_rhs"],float(v[10]),2.e-7,j,"He"))
                for k,lim,denom in (("xHII",5e-9,max(abs(native["xHII"]),1e-8)),
                                    ("xe",5e-9,max(abs(native["xe"]),1e-8)),
                                    ("xHeII",5e-10,1.),
                                    ("Tm_K",5e-10,max(abs(native["Tm_K"]),1.))):
                    maxima[k]=max(maxima[k],abs(expected[k]-native[k])/denom)
                continue
            if tag in ("V","A","L"):
                j,b=int(v[1]),int(v[2])
                bins=3 if tag=="L" else 311
                if (j,b)!=divmod(counts[tag],bins) or len(v)!=4:
                    raise ArithmeticError("C_SPECTRUM_ORDER_OR_DUPLICATE")
                counts[tag]+=1
                if j<8:
                    py={"V":checkpoint["virtual_out"],"A":checkpoint["average_virtual"],"L":checkpoint["lyman_out"]}[tag][b,j]
                else:
                    py={"V":result.virtual_out,"A":result.average_virtual,"L":result.lyman_out}[tag][b,j]
                cv=float(v[3]); z=c.redshift(72892+j)
                ev=LINE_EV[b] if tag=="L" else table.energy_eV[b]
                fbb=1./math.expm1(ev/(KB_EV_K*c.T0_K*(1.+z)))
                tol=1.e-7*max(abs(py),abs(cv))+1.e-10*fbb
                ratio=abs(py-cv)/tol
                if not math.isfinite(ratio) or ratio>1.:
                    raise ArithmeticError(f"INTEGRATED_PHOTON_PARITY:j={j}:tag={tag}:bin={b}:ratio={ratio:.17g}")
                key={"V":"virtual","A":"average","L":"lyman"}[tag]
                maxima[key]=max(maxima[key],ratio)
                continue
            if tag=="EVENT":
                counts[tag]+=1
                event={"relative_index":int(v[1]),"type":int(v[2]),"steps":int(v[3])}
                continue
            raise ValueError(f"UNKNOWN_C_RECORD:{tag}")
    n=8+len(result.steps)
    if counts!={"HE":72893,"NODE":1,"STEP":n,"V":311*n,"A":311*n,"L":3*n,"EVENT":1}:
        raise ArithmeticError(f"C_ROW_COUNT:{counts}")
    if event is None or event["steps"]!=n: raise ArithmeticError("C_EVENT_RECEIPT_MISSING_OR_COUNT")
    if cpu_guard is not None:
        cpu_guard("native_stdout_complete")
    py_event=-1 if result.event is None else result.event["iz"]-72892
    py_type=0 if result.event is None else (1 if result.event["type"]=="HELIUM_CUTOFF" else 2)
    if event["relative_index"]!=py_event or event["type"]!=py_type:
        raise ArithmeticError(f"C_PY_EVENT_MISMATCH:C={event}:P={result.event}")
    return {"status":"PASS","counts":counts,"maxima":maxima,"native_event":event}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--checkpoint",type=Path,required=True)
    ap.add_argument("--evidence-dir",type=Path,required=True)
    ap.add_argument("--mode", choices=("smoke","event"), required=True)
    ap.add_argument("--max-extra-accepted",type=int,default=16)
    ap.add_argument("--new-allocation-id", required=True)
    ap.add_argument("--supervised", action="store_true")
    args=ap.parse_args()
    if not args.supervised:
        ap.error("invoke scripts/run_r3q_h4_supervised.py")
    if not args.new_allocation_id.strip() or "CLOSED" in args.new_allocation_id.upper():
        ap.error("fresh allocation identifier required")
    if (args.mode=="smoke" and not 1<=args.max_extra_accepted<=32) or (args.mode=="event" and args.max_extra_accepted!=MAX_EXTRA_ACCEPTED):
        ap.error("smoke requires 1..32 steps; event requires 8192 cap")
    global CPU_BUDGET_S, WORK_CPU_BUDGET_S, WALL_DEADLINE
    CPU_BUDGET_S=60 if args.mode=="smoke" else 600
    WORK_CPU_BUDGET_S=CPU_BUDGET_S-5
    wall_budget=180 if args.mode=="smoke" else 900
    WALL_DEADLINE=time.monotonic()+wall_budget-12
    if not (1<=args.max_extra_accepted<=MAX_EXTRA_ACCEPTED):
        ap.error("--max-extra-accepted must be in 1..8192")
    ev=args.evidence_dir.resolve()
    ev.mkdir(parents=True,exist_ok=False)
    start=time.monotonic(); u0=resource.getrusage(resource.RUSAGE_SELF)
    cpu_start=total_process_tree_cpu_s()
    aff=sorted(os.sched_getaffinity(0)); os.sched_setaffinity(0,{aff[0]})
    report={"status":"FAIL","first_failure":None,"claim":"bounded q=0 h/4 continuation only",
            "checkpoint_sha256":CHECKPOINT_SHA256,
            "new_allocation_id":args.new_allocation_id, "mode":args.mode,
            "historical_budget":"CLOSED_HOLD_NOT_RESET", "rei_activation":False,
            "python_h_h2_h4_convergence":"HOLD_REQUIRES_MATCHED_COMPLETE_HISTORIES",
            "scientific_admission":"HOLD_PENDING_INDEPENDENT_REVIEW",
            "source_zip_sha256":PINNED_ZIP_SHA,"source_sha256":PINNED_SOURCE,
            "producer_sha256":sha(ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_continuation.py"),
            "harness_sha256":sha(ROOT/"scripts/c_harness/original_hyrec_r3q_h4_continuation_harness.c"),
            "resources":{"affinity":[aff[0]],"blas_threads":1,"address_limit_bytes":2*1024**3,
                         "cpu_limit_s":CPU_BUDGET_S,"wall_limit_s":wall_budget,
                         "recovery_cpu_s_within_total":5,"recovery_wall_s_within_total":12},"old_U5_gate":"HOLD"}
    try:
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        current=resource.getrusage(resource.RUSAGE_SELF)
        cap=math.ceil(current.ru_utime+current.ru_stime+CPU_BUDGET_S)
        resource.setrlimit(resource.RLIMIT_CPU,(cap,cap+1))
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("R3Q_CONTINUATION_WORK_WALL_LIMIT")))
        signal.alarm(wall_budget-12)
        report["capsule_source_closure"]=verify_capsule_source_closure(ROOT,args.checkpoint)
        checkpoint=load_frozen_start(args.checkpoint)
        source_dir, original_manifest=prepare_source(
            ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip",ev/"source_extract")
        (ev/"original_source_manifest.json").write_text(json.dumps(original_manifest,sort_keys=True,indent=2)+"\n")
        report["modified_source_sha256"]={k:sha(source_dir/k) for k in PINNED_SOURCE}
        harness=ROOT/"scripts/c_harness/original_hyrec_r3q_h4_continuation_harness.c"
        sources=[str(source_dir/k) for k in ("history.c","hydrogen.c","helium.c","hyrectools.c")]
        ccmd=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(source_dir),str(harness),
              *sources,"-lm","-o",str(ev/"native_h4_continuation")]
        report["native_build"]=run_capture_budgeted(ccmd,source_dir,ev/"native_build_stdout.txt",ev/"native_build_stderr.txt",60,os.environ.copy(),cpu_start)
        if report["native_build"]["returncode"]: raise RuntimeError("NATIVE_C_BUILD_FAILED")
        report["native_binary_sha256"]=sha(ev/"native_h4_continuation")
        sharedcmd=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-DR3Q_SHARED",
                   "-I",str(source_dir),str(harness),*[str(source_dir/k) for k in ("hydrogen.c","helium.c","hyrectools.c")],
                   "-lm","-o",str(ev/"liboriginal_full_source.so")]
        report["common_build"]=run_capture_budgeted(sharedcmd,source_dir,ev/"common_build_stdout.txt",ev/"common_build_stderr.txt",60,os.environ.copy(),cpu_start)
        if report["common_build"]["returncode"]: raise RuntimeError("COMMON_C_BUILD_FAILED")
        report["common_binary_sha256"]=sha(ev/"liboriginal_full_source.so")
        c=HyRec2012Cosmology()
        rates=OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        table=_canonical_twophoton_table(rates.archive_path)
        source=make_hmla_source(c,rates)
        oracle=FullSourceCOracle(ev/"liboriginal_full_source.so",source_dir,c)
        metrics={"sampled_evaluations":0,"max_rhs_scaled":0.,"max_virtual_tolerance_ratio":0.,
                 "max_average_tolerance_ratio":0.,"max_lyman_tolerance_ratio":0.}
        tail=[]
        online_sampled={}
        evaluation_serial=0
        def observer(g,z,xh,xhe,tm,vh,lh,out):
            nonlocal evaluation_serial
            checked_cpu_budget(cpu_start,"atomic_source_observer")
            evaluation_serial+=1
            j=g-72892
            if j in (8,9,10) or (j-8)%128==0:
                check_one_source(oracle,table,j,z,xh,xhe,tm,vh,lh,out,metrics)
                online_sampled[evaluation_serial]=g
            tail.append((evaluation_serial,g,z,xh,xhe,tm,out))
            if len(tail)>256: del tail[0]
        def on_accept(state,step,out):
            checked_cpu_budget(cpu_start,"accepted_step")
            obj={"state":state,"step":serializable_step(step)}
            accepted.write(json.dumps(obj,allow_nan=False,separators=(",",":"))+"\n")
            accepted.flush()
            partial_virtual.write(np.asarray(out.outgoing_virtual,dtype="<f8").tobytes())
            partial_average.write(np.asarray(out.average_virtual,dtype="<f8").tobytes())
            partial_lyman.write(np.asarray(out.outgoing_lyman,dtype="<f8").tobytes())
        with ExitStack() as files:
            accepted=files.enter_context((ev/"python_accepted_partial.jsonl").open("x"))
            partial_virtual=files.enter_context((ev/"python_partial_virtual_f64le.bin").open("xb"))
            partial_average=files.enter_context((ev/"python_partial_average_f64le.bin").open("xb"))
            partial_lyman=files.enter_context((ev/"python_partial_lyman_f64le.bin").open("xb"))
            result=integrate_continuation(checkpoint,c,source,
                max_extra_accepted=args.max_extra_accepted,
                max_full_evaluations=min(MAX_FULL_EVALUATIONS,4*args.max_extra_accepted),
                observer=observer,on_accept=on_accept)
        report["partial_accepted_sha256"]={k:sha(ev/k) for k in (
            "python_accepted_partial.jsonl","python_partial_virtual_f64le.bin",
            "python_partial_average_f64le.bin","python_partial_lyman_f64le.bin")}
        report["python_result"]={"status":result.status,"event":result.event,
            "extra_accepted":len(result.steps),"full_evaluations":result.full_evaluations,
            "max_species_ledger_residual":result.ledger_max}
        # The observer retained actual evaluated atomic states; compare the
        # final event neighborhood on the same accepted history, without C
        # history entering Python evolution.
        if result.event:
            event_g=result.event["iz"]
            chosen,event_sampling=select_event_sample_calls(tail,online_sampled,event_g)
            for serial,g,z,xh,xhe,tm,out in chosen:
                checked_cpu_budget(cpu_start,"event_common_input")
                j=g-72892
                check_one_source(oracle,table,j,z,xh,xhe,tm,
                                 result.virtual_out[:,:j],result.lyman_out[:,:j],out,metrics)
            report["event_neighborhood_sampling"]=event_sampling
        report["common_input_sample"]={"status":"PASS",**metrics}
        np.savez_compressed(ev/"python_continuation.npz",
            states_json=np.array([json.dumps(s,sort_keys=True) for s in result.states]),
            steps_json=np.array([json.dumps(serializable_step(s),sort_keys=True,allow_nan=False)
                                 for s in result.steps]),
            virtual_out=result.virtual_out,average_virtual=result.average_virtual,
            lyman_out=result.lyman_out, final_predictor=result.final_predictor,
            dlna=np.array(8.49e-5/4),parent_checkpoint_sha256=np.array(CHECKPOINT_SHA256),
            source_zip_sha256=np.array(PINNED_ZIP_SHA),rei_activation=np.array(False))
        report["python_history_sha256"]=sha(ev/"python_continuation.npz")
        native_env=os.environ.copy()
        if args.max_extra_accepted<MAX_EXTRA_ACCEPTED:
            native_env["R3Q_MAX_EXTRA_ACCEPTED"]=str(args.max_extra_accepted)
        else:
            native_env.pop("R3Q_MAX_EXTRA_ACCEPTED",None)
        run=run_capture_budgeted([str(ev/"native_h4_continuation")],source_dir,
            ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",600,native_env,cpu_start)
        report["native_run"]=run
        if run["returncode"]: raise RuntimeError("NATIVE_C_ORACLE_FAILED")
        report["same_h_parity"]=compare_native_stream(
            ev/"native_oracle_stdout.csv",checkpoint,result,c,table,
            cpu_guard=lambda stage:checked_cpu_budget(cpu_start,stage))
        report["closure_after"]=verify_capsule_source_closure(ROOT,args.checkpoint)
        checked_cpu_budget(cpu_start,"after_all_validation")
        if args.max_extra_accepted<MAX_EXTRA_ACCEPTED:
            report["status"]="SMOKE_ONLY"
        elif result.status!="EVENT_PLUS_TWO":
            report["status"]="HOLD_CAP_BEFORE_EVENT_PLUS_TWO"
        else:
            report["status"]="PASS_PENDING_INDEPENDENT_REVIEW"
        checked_cpu_budget(cpu_start,"before_final_status")
    except BaseException as exc:
        report["status"]="FAIL"
        report["first_failure"]={"type":type(exc).__name__,"message":str(exc)}
        (ev/"failure.txt").write_text(f"{type(exc).__name__}: {exc}\n")
    finally:
        signal.alarm(0)
        report["partial_accepted_sha256"]={k:sha(ev/k) for k in (
            "python_accepted_partial.jsonl","python_partial_virtual_f64le.bin",
            "python_partial_average_f64le.bin","python_partial_lyman_f64le.bin") if (ev/k).is_file()}
        u1=resource.getrusage(resource.RUSAGE_SELF)
        children=resource.getrusage(resource.RUSAGE_CHILDREN)
        final_cpu=total_process_tree_cpu_s()-cpu_start
        report["resources"].update({"wall_s":time.monotonic()-start,
            "parent_cpu_s":u1.ru_utime+u1.ru_stime-u0.ru_utime-u0.ru_stime,
            "parent_peak_rss_bytes":u1.ru_maxrss*1024,
            "children_cpu_s":children.ru_utime+children.ru_stime,
            "children_peak_rss_bytes":children.ru_maxrss*1024,
            "cumulative_process_tree_cpu_s":final_cpu})
        enforce_final_cpu_gate(report,final_cpu)
        (ev/"verification.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print(json.dumps({"status":report["status"],"first_failure":report["first_failure"]},sort_keys=True))
    if report["status"] not in ("PASS_PENDING_INDEPENDENT_REVIEW","HOLD_CAP_BEFORE_EVENT_PLUS_TWO","SMOKE_ONLY"):
        raise SystemExit(2)

if __name__=="__main__": main()

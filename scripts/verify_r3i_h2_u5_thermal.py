#!/usr/bin/env python3
"""Create-only bounded original-C/Python h/2 thermal-switch evidence."""
from __future__ import annotations

import argparse
import ctypes
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
    compare_state,checked_integrated_rhs_ratio,safe_extract_source,sha)
from verify_r3i_h2_continuation import (
    checked_cpu_budget,enforce_final_cpu_gate,run_capture_budgeted,
    total_process_tree_cpu_s,check_one_source)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    HyRec2012Cosmology,make_hmla_source)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u5_thermal import (
    CHECKPOINT_SHA256,MAX_EXTRA_ACCEPTED,MAX_FULL_EVALUATIONS,PREFIX_COLUMNS,
    RT_IZ,START_IZ,integrate_u5_thermal,load_frozen_checkpoint)
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from r3i_u5_average_forensic import preserve_failure

MANIFEST=ROOT/"research/rec_r3i_time_refinement_20261016/h2_u5_thermal_start_001/SOURCE_MANIFEST_V3.json"
LINE_EV=(10.198714553953742,12.087365397278509,12.748393192442178)
KB_EV_K=8.617343e-5


def verify_closure(checkpoint:Path) -> dict:
    if sha(checkpoint)!=CHECKPOINT_SHA256:
        raise ValueError("REVIEWED_H2_U4_CHECKPOINT_SHA_MISMATCH")
    manifest=json.loads(MANIFEST.read_text())
    for relative,digest in manifest["files"].items():
        path=ROOT/relative
        if not path.is_file() or sha(path)!=digest:
            raise ValueError(f"CAPSULE_SOURCE_CLOSURE_MISSING_OR_CHANGED:{relative}")
    return {"manifest_sha256":sha(MANIFEST),"files":len(manifest["files"]),
            "checkpoint_sha256":CHECKPOINT_SHA256}


def frozen_u5_original_gate() -> dict:
    path=ROOT/"research/rec_r3g_primordial_20261016/thermal_transition_001/U5_SCOPED_REVIEW.json"
    data=json.loads(path.read_text())
    if (data.get("original_average_gate")!="HOLD_ORIGINAL_TOLERANCE_NOT_MET" or
            data.get("original_verification_status")!="FAIL" or
            data.get("checks",{}).get("cross_history_average_failures")!=9):
        raise ValueError("FROZEN_U5_ORIGINAL_GATE_CHANGED")
    return {"status":"HOLD_ORIGINAL_TOLERANCE_NOT_MET","failures":9,
            "source_receipt_sha256":sha(path)}


class CombinedOracle:
    def __init__(self,shared:Path,source_dir:Path,c:HyRec2012Cosmology):
        self.h=FullSourceCOracle(shared,source_dir,c)
        self.c=c
        fn=ctypes.CDLL(str(shared)).rec_dTmdlna
        fn.argtypes=[ctypes.c_double]*7
        fn.restype=ctypes.c_double
        self.tfn=fn
    def __call__(self,*args):
        return self.h(*args)
    @property
    def c(self): return self._c
    @c.setter
    def c(self,value): self._c=value
    def thermal_rhs(self,xe,tm,z):
        tr=KB_EV_K*self.c.T0_K*(1.+z)
        return self.tfn(xe,tm,tr/KB_EV_K,self.c.hubble_s(z),
                        self.c.fHe,self.c.fsR,self.c.meR)


def compare_native_stream(path:Path,result,c,table,guard,forensic_callback=None) -> dict:
    counts={k:0 for k in ("PARAM","HE","NODE","BASE","STEP","V","A","L",
                           "PV","PL","THERMAL_EVENT","END")}
    maxima={k:0. for k in ("xe","Tm_K","hydrogen_rhs","thermal_rhs",
                           "virtual","average","lyman")}
    native_event=None
    native_end=None
    n=len(result.steps)
    native_input=None
    c_inputs=[]
    c_virtual=np.full((311,PREFIX_COLUMNS+n),np.nan)
    c_lyman=np.full((3,PREFIX_COLUMNS+n),np.nan)
    with path.open() as stream:
        for line_no,line in enumerate(stream,1):
            if line_no%4096==0:guard("native_stdout_stream")
            row=line.rstrip("\n").split(",")
            tag=row[0]
            if tag not in counts:raise ValueError(f"UNKNOWN_NATIVE_RECORD:{tag}")
            counts[tag]+=1
            if tag=="PARAM":
                if int(row[1])!=RT_IZ or int(row[3])!=result.rt_stop_iz:
                    raise ArithmeticError(f"RT_STOP_INDEX_PARITY:{row}")
            elif tag=="BASE":
                native={"iz":int(row[1]),"z":float(row[2]),"xH1s":float(row[3]),
                        "xHII":float(row[4]),"xHeII":float(row[5]),"xe":float(row[6]),
                        "Tm_K":float(row[7]),"post_saha":bool(int(row[8]))}
                compare_state(result.states[0],native,-1)
                native_input=native
            elif tag in ("PV","PL"):
                col,b=int(row[1]),int(row[2])
                if not 0<=col<PREFIX_COLUMNS:raise ArithmeticError(f"C_PREFIX_INDEX:{col}")
                target=c_virtual if tag=="PV" else c_lyman
                if not 0<=b<target.shape[0] or math.isfinite(target[b,col]):
                    raise ArithmeticError(f"C_PREFIX_DUPLICATE:{tag}:{col}:{b}")
                target[b,col]=float(row[3])
            elif tag=="THERMAL_EVENT":
                native_event={"input_iz":int(row[1]),"delta":float(row[2]),
                    "thermal_seed_prev2":float(row[3]),"thermal_seed_prev":float(row[4])}
                if result.event is None or native_event["input_iz"]!=result.event["input_iz"]:
                    raise ArithmeticError(f"THERMAL_EVENT_INDEX_PARITY:{native_event}:{result.event}")
                for name in ("delta","thermal_seed_prev2","thermal_seed_prev"):
                    p=float(result.event[name]);v=native_event[name]
                    if abs(p-v)/max(1.,abs(v))>2.e-10:
                        raise ArithmeticError(f"THERMAL_EVENT_SEED_PARITY:{name}:{p}:{v}")
            elif tag=="STEP":
                i=int(row[1])
                if i!=counts[tag]-1 or i>=n:raise ArithmeticError(f"C_STEP_SEQUENCE:{i}")
                native={"iz":int(row[2]),"z":float(row[3]),"xH1s":float(row[4]),
                        "xHII":float(row[5]),"xHeII":float(row[6]),"xe":float(row[7]),
                        "Tm_K":float(row[8]),"post_saha":bool(int(row[11]))}
                if native_input is None:raise ArithmeticError("C_BASE_MISSING")
                c_inputs.append(native_input)
                native_input=native
                py=result.states[i+1]
                compare_state(py,native,i)
                step=result.steps[i]
                if step["coupled"]!=bool(int(row[10])):
                    raise ArithmeticError(f"THERMAL_BRANCH_PARITY:{i}")
                maxima["hydrogen_rhs"]=max(maxima["hydrogen_rhs"],
                    checked_integrated_rhs_ratio(step["hydrogen_rhs"],float(row[9]),2.e-7,i,"H"))
                if step["coupled"]:
                    t_ratio=checked_integrated_rhs_ratio(step["thermal_rhs"],float(row[12]),
                                                          2.e-7,i,"T")
                    maxima["thermal_rhs"]=max(maxima["thermal_rhs"],t_ratio)
                for field,floor in (("xe",1.e-8),("Tm_K",1.)):
                    maxima[field]=max(maxima[field],abs(py[field]-native[field])/
                                      max(abs(native[field]),floor))
            elif tag in ("V","A","L"):
                i,b=int(row[1]),int(row[2])
                if i>=n:raise ArithmeticError(f"C_SPECTRUM_STEP:{i}")
                j=PREFIX_COLUMNS+i
                py={"V":result.virtual_out,"A":result.average_virtual,
                    "L":result.lyman_out}[tag][b,j]
                cv=float(row[3])
                if tag in ("V","L"):
                    target=c_virtual if tag=="V" else c_lyman
                    if math.isfinite(target[b,j]):
                        raise ArithmeticError(f"C_SPECTRUM_DUPLICATE:{tag}:{i}:{b}")
                    target[b,j]=cv
                energy=LINE_EV[b] if tag=="L" else table.energy_eV[b]
                tr=KB_EV_K*c.T0_K*(1.+c.redshift(START_IZ+i))
                fbb=1./math.expm1(energy/tr)
                tol=1.e-7*max(abs(py),abs(cv))+1.e-10*fbb
                ratio=abs(py-cv)/tol
                if not math.isfinite(ratio) or ratio>1.:
                    if tag=="A" and forensic_callback is not None:
                        if i>=len(c_inputs) or not (np.all(np.isfinite(c_virtual[:,:j])) and
                                                    np.all(np.isfinite(c_lyman[:,:j]))):
                            raise ArithmeticError(f"C_CAUSAL_PREFIX_INCOMPLETE_AT_FAILURE:{i}:{b}")
                        forensic_callback(i,b,c_inputs[i],c_virtual[:,:j],
                                          c_lyman[:,:j],py,cv)
                    raise ArithmeticError(f"INTEGRATED_PHOTON_PARITY:i={i}:tag={tag}:bin={b}:ratio={ratio:.17g}")
                maxima[{"V":"virtual","A":"average","L":"lyman"}[tag]]=max(
                    maxima[{"V":"virtual","A":"average","L":"lyman"}[tag]],ratio)
            elif tag=="END":
                native_end={"status":row[1],"event_iz":int(row[2]),
                            "coupled":int(row[3]),"steps":int(row[4])}
    expected={"PARAM":1,"HE":36447,"NODE":1,"BASE":1,"STEP":n,
              "V":311*n,"A":311*n,"L":3*n,"PV":311*PREFIX_COLUMNS,
              "PL":3*PREFIX_COLUMNS,"THERMAL_EVENT":int(result.event is not None),"END":1}
    if counts!=expected:raise ArithmeticError(f"C_ROW_COUNT:{counts}:{expected}")
    if (native_end is None or native_end["steps"]!=n or
            native_end["status"]!=result.status or
            native_end["event_iz"]!=(result.event["input_iz"] if result.event else -1)):
        raise ArithmeticError(f"C_END_PARITY:{native_end}:{result.status}:{result.event}")
    guard("native_stdout_complete")
    return {"status":"PASS","counts":counts,"maxima":maxima,
            "native_event":native_event,"native_end":native_end}


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--checkpoint",type=Path,required=True)
    ap.add_argument("--evidence-dir",type=Path,required=True)
    ap.add_argument("--max-extra-accepted",type=int,default=MAX_EXTRA_ACCEPTED)
    args=ap.parse_args()
    if not 1<=args.max_extra_accepted<=MAX_EXTRA_ACCEPTED:
        ap.error("max-extra-accepted outside frozen 1..20000")
    ev=args.evidence_dir.resolve();ev.mkdir(parents=True,exist_ok=False)
    t0=time.monotonic();cpu0=total_process_tree_cpu_s();usage0=resource.getrusage(resource.RUSAGE_SELF)
    affinity=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity[0]})
    report={"status":"FAIL","first_failure":None,
            "claim":"bounded original HyRec q=0 h/2 U5 thermal start only",
            "checkpoint_sha256":CHECKPOINT_SHA256,"source_zip_sha256":PINNED_ZIP_SHA,
            "source_sha256":PINNED_SOURCE,
            "producer_sha256":sha(ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_refined_u5_thermal.py"),
            "harness_sha256":sha(ROOT/"scripts/c_harness/original_hyrec_r3i_h2_u5_thermal_harness.c"),
            "old_U5_gate":frozen_u5_original_gate(),
            "resources":{"affinity":[affinity[0]],"blas_threads":1,
                         "address_limit_bytes":2*1024**3,"cpu_limit_s":600,"wall_limit_s":900}}
    try:
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(600,600))
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("U5_WALL_900S")))
        signal.alarm(900)
        report["capsule_source_closure"]=verify_closure(args.checkpoint)
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
        harness=ROOT/"scripts/c_harness/original_hyrec_r3i_h2_u5_thermal_harness.c"
        sources=[str(source_dir/name) for name in ("history.c","hydrogen.c","helium.c","hyrectools.c")]
        env=os.environ.copy()
        native=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(source_dir),
                str(harness),*sources,"-lm","-o",str(ev/"native_u5_thermal")]
        report["native_build"]=run_capture_budgeted(native,source_dir,ev/"native_build_stdout.txt",
                                                       ev/"native_build_stderr.txt",60,env,cpu0)
        if report["native_build"]["returncode"]:raise RuntimeError("NATIVE_C_BUILD_FAILED")
        shared=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-DR3I_SHARED",
                "-I",str(source_dir),str(harness),*sources,"-lm","-o",str(ev/"liboriginal_full_source.so")]
        report["common_build"]=run_capture_budgeted(shared,source_dir,ev/"common_build_stdout.txt",
                                                       ev/"common_build_stderr.txt",60,env,cpu0)
        if report["common_build"]["returncode"]:raise RuntimeError("COMMON_C_BUILD_FAILED")
        report["native_binary_sha256"]=sha(ev/"native_u5_thermal")
        report["common_binary_sha256"]=sha(ev/"liboriginal_full_source.so")
        c=HyRec2012Cosmology()
        rates=OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        table=_canonical_twophoton_table(rates.archive_path)
        source=make_hmla_source(c,rates)
        oracle=CombinedOracle(ev/"liboriginal_full_source.so",source_dir,c)
        metrics={"sampled_evaluations":0,"max_rhs_scaled":0.,
                 "max_virtual_tolerance_ratio":0.,"max_average_tolerance_ratio":0.,
                 "max_lyman_tolerance_ratio":0.,"max_thermal_rhs_scaled":0.}
        tail=[]
        thermal_event_input=None
        forced_thermal_samples=[]
        identities={"source_zip_sha256":PINNED_ZIP_SHA,
            "modified_source_sha256":report["modified_source_sha256"],
            "native_binary_sha256":report["native_binary_sha256"],
            "common_binary_sha256":report["common_binary_sha256"],
            "python_producer_sha256":report["producer_sha256"],
            "checkpoint_sha256":CHECKPOINT_SHA256}
        def average_failure(j,b,py_state,c_state,py_vh,py_lh,c_vh,c_lh,py_raw,c_raw):
            report["new_average_forensic"]=preserve_failure(ev,j=j,b=b,
                python_state=py_state,c_state=c_state,
                py_vh=py_vh,py_lh=py_lh,c_vh=c_vh,c_lh=c_lh,
                py_raw=float(py_raw),c_raw=float(c_raw),c=c,source=source,
                table=table,oracle=oracle,source_dir=source_dir,
                source_identities=identities)
        def observer(g,z,xh,tm,vh,lh,out):
            nonlocal thermal_event_input
            checked_cpu_budget(cpu0,"atomic_source_observer")
            j=g-RT_IZ
            delta=1.-tm/c.T0_K/(1.+z)
            if thermal_event_input is None and delta>=5.e-4:
                thermal_event_input=g
            forced=thermal_event_input is not None and g in (thermal_event_input,thermal_event_input+1)
            if forced or j in (PREFIX_COLUMNS,PREFIX_COLUMNS+1) or (j-PREFIX_COLUMNS)%128==0:
                try:
                    check_one_source(oracle,table,j,z,xh,0.,tm,vh,lh,out,metrics)
                except ArithmeticError as exc:
                    message=str(exc)
                    if "field=average:bin=" in message:
                        b=int(message.rsplit(":bin=",1)[1].split(":",1)[0])
                        cref=oracle(j,z,xh,0.,tm,vh,lh)
                        state={"iz":g,"z":z,"xe":xh,"Tm_K":tm}
                        average_failure(j,b,state,state,vh,lh,vh,lh,
                                        out.average_virtual[b],cref["average"][b])
                    raise
                py=source_thermal_rhs(c,xh,tm,z);cv=oracle.thermal_rhs(xh,tm,z)
                ratio=abs(py-cv)/max(1.,abs(cv))
                if not math.isfinite(ratio) or ratio>2.e-10:
                    raise ArithmeticError(f"COMMON_INPUT_THERMAL_RHS_PARITY:{g}:{ratio}")
                metrics["max_thermal_rhs_scaled"]=max(metrics["max_thermal_rhs_scaled"],ratio)
                if forced:
                    forced_thermal_samples.append({"input_iz":g,"python_rhs":py,
                        "original_c_rhs":cv,"scaled_ratio":ratio})
            tail.append((g,z,xh,tm,out))
            if len(tail)>128:del tail[0]
        def on_accept(state,step,out):
            checked_cpu_budget(cpu0,"accepted_step")
            accepted.write(json.dumps({"state":state,"step":step},allow_nan=False,separators=(",",":"))+"\n")
            accepted.flush()
            part_v.write(np.asarray(out.outgoing_virtual,dtype="<f8").tobytes())
            part_a.write(np.asarray(out.average_virtual,dtype="<f8").tobytes())
            part_l.write(np.asarray(out.outgoing_lyman,dtype="<f8").tobytes())
        with ExitStack() as stack:
            accepted=stack.enter_context((ev/"python_accepted_partial.jsonl").open("x"))
            part_v=stack.enter_context((ev/"python_partial_virtual_f64le.bin").open("xb"))
            part_a=stack.enter_context((ev/"python_partial_average_f64le.bin").open("xb"))
            part_l=stack.enter_context((ev/"python_partial_lyman_f64le.bin").open("xb"))
            result=integrate_u5_thermal(cp,c,source,
                max_extra_accepted=args.max_extra_accepted,
                max_full_evaluations=min(MAX_FULL_EVALUATIONS,args.max_extra_accepted),
                observer=observer,on_accept=on_accept)
        report["python_result"]={"status":result.status,"event":result.event,
            "extra_accepted":len(result.steps),"full_evaluations":result.full_evaluations,
            "rt_stop_iz":result.rt_stop_iz}
        if result.event:
            expected=[result.event["input_iz"],result.event["input_iz"]+1]
            if [v["input_iz"] for v in forced_thermal_samples]!=expected:
                raise ArithmeticError(f"THERMAL_EVENT_BOTH_INPUTS_NOT_SAMPLED:{forced_thermal_samples}")
        report["forced_thermal_rhs_samples"]=forced_thermal_samples
        if result.event:
            for g,z,xh,tm,out in tail:
                if result.event["input_iz"]-64 <= g <= result.event["input_iz"]+1:
                    j=g-RT_IZ
                    vh=result.virtual_out[:,:j];lh=result.lyman_out[:,:j]
                    try:
                        check_one_source(oracle,table,j,z,xh,0.,tm,vh,lh,out,metrics)
                    except ArithmeticError as exc:
                        message=str(exc)
                        if "field=average:bin=" in message:
                            b=int(message.rsplit(":bin=",1)[1].split(":",1)[0])
                            cref=oracle(j,z,xh,0.,tm,vh,lh)
                            state={"iz":g,"z":z,"xe":xh,"Tm_K":tm}
                            average_failure(j,b,state,state,vh,lh,vh,lh,
                                            out.average_virtual[b],cref["average"][b])
                        raise
        report["common_input_sample"]={"status":"PASS",**metrics}
        np.savez_compressed(ev/"python_u5_thermal.npz",
            states_json=np.array([json.dumps(s,sort_keys=True) for s in result.states]),
            steps_json=np.array([json.dumps(s,sort_keys=True) for s in result.steps]),
            virtual_out=result.virtual_out,average_virtual=result.average_virtual,
            lyman_out=result.lyman_out)
        report["python_history_sha256"]=sha(ev/"python_u5_thermal.npz")
        native_env=env.copy();native_env["R3I_MAX_EXTRA_ACCEPTED"]=str(args.max_extra_accepted)
        report["native_run"]=run_capture_budgeted([str(ev/"native_u5_thermal")],source_dir,
            ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",600,native_env,cpu0)
        if report["native_run"]["returncode"]:raise RuntimeError("NATIVE_C_ORACLE_FAILED")
        def integrated_average_failure(i,b,c_state,c_vh,c_lh,pval,cval):
            py_state=result.states[i]
            j=PREFIX_COLUMNS+i
            average_failure(j,b,py_state,c_state,
                result.virtual_out[:,:j],result.lyman_out[:,:j],
                c_vh,c_lh,pval,cval)
        report["same_h_parity"]=compare_native_stream(ev/"native_oracle_stdout.csv",result,c,table,
            lambda stage:checked_cpu_budget(cpu0,stage),integrated_average_failure)
        checked_cpu_budget(cpu0,"before_final_status")
        report["status"]=("SMOKE_ONLY" if args.max_extra_accepted<MAX_EXTRA_ACCEPTED and
                          result.status=="HOLD_CAP_BEFORE_THERMAL_EVENT_PLUS_TWO" else
                          "PASS_PENDING_INDEPENDENT_REVIEW" if result.status=="THERMAL_EVENT_TWO_STEPS_COMPLETE" else
                          result.status)
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
                                "HOLD_CAP_BEFORE_THERMAL_EVENT_PLUS_TWO"):
        raise SystemExit(2)


if __name__=="__main__":main()

#!/usr/bin/env python3
"""Source-native R3g U6 H+Tm FULL continuation and original-C RT oracle."""
from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time
import traceback
from pathlib import Path

os.environ.update({k:"1" for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS")})
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from full_bianchi_hyrec.trajectory.primordial_2012_full_thermal_continuation import (
    START_J,END_J,EXTRA_ACCEPTED,SAMPLE_J,START_GLOBAL_IZ,END_GLOBAL_IZ,
    U5_STOP_NPZ_SHA256,U5_STOP_JSON_SHA256,U5_ORIGINAL_VERIFICATION_SHA256,
    U5_SCOPED_AUDIT_SHA256,sha256,load_admitted_u5_stop,continue_full_thermal_to_rt,
)
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from verify_r3g_continuation import (safe_source,zip_member_hashes,PINNED_ZIP_SHA,
    PINNED_SOURCE,compare_state,load_u2_verifier)
from verify_r3g_hydrogen_transition import save_checkpoint
from verify_r3g_thermal_transition import CombinedOracle

BASE_REVISION="766023946a2219530d58e66eb8bc306dd89071a9"
U6_FILES=(
 "src/full_bianchi_hyrec/trajectory/primordial_2012_full_thermal_continuation.py",
 "scripts/verify_r3g_full_thermal_continuation.py",
 "scripts/c_harness/original_hyrec_full_thermal_to_rt_harness.c",
 "tests/trajectory/test_primordial_2012_full_thermal_continuation.py",
)


def child_limits_u6() -> None:
    """Lower inherited limits without ever raising a hard limit in preexec."""
    for kind,cap in ((resource.RLIMIT_AS,2*1024**3),(resource.RLIMIT_CPU,270)):
        soft,hard=resource.getrlimit(kind)
        finite=[cap]
        if soft!=resource.RLIM_INFINITY: finite.append(soft)
        if hard!=resource.RLIM_INFINITY: finite.append(hard)
        target=min(finite)
        resource.setrlimit(kind,(target,target))


def run_capture_u6(cmd,cwd,stdout,stderr,timeout,env):
    started=time.monotonic()
    with Path(stdout).open("xb") as out,Path(stderr).open("xb") as err:
        proc=subprocess.run(cmd,cwd=cwd,stdout=out,stderr=err,timeout=timeout,
                            env=env,preexec_fn=child_limits_u6,check=False)
    return {"command":cmd,"returncode":proc.returncode,
            "wall_s":time.monotonic()-started,
            "stdout_sha256":sha256(stdout),"stderr_sha256":sha256(stderr)}


def parse_native(path:Path) -> dict:
    """Parse only U6 records into bounded fixed arrays; discard U1-U5 replay."""
    n=EXTRA_ACCEPTED
    rows=np.full((n,11),np.nan); v=np.full((n,311),np.nan)
    a=np.full((n,311),np.nan); l=np.full((n,3),np.nan)
    seen=np.zeros((n,3),dtype=np.int16)
    node=end=None
    with path.open() as stream:
        for lineno,line in enumerate(stream,1):
            f=line.rstrip("\n").split(","); tag=f[0]
            if tag=="U6NODE":
                if node is not None or len(f)!=11: raise ValueError("C_U6_DUPLICATE_OR_BAD_NODE")
                node=[float(x) for x in f[1:]]
            elif tag=="U6STEP":
                if len(f)!=12: raise ValueError(f"C_U6_STEP_GRAMMAR:{lineno}")
                j=int(f[1]); k=j-START_J
                if not (0<=k<n) or math.isfinite(rows[k,0]): raise ValueError(f"C_U6_STEP_INDEX:{j}")
                rows[k]=[float(x) for x in f[1:]]
            elif tag in ("V","A","L"):
                j=int(f[1]); k=j-START_J
                if 0<=k<n:
                    b=int(f[2]); channel={"V":0,"A":1,"L":2}[tag]
                    target=(v,a,l)[channel]
                    if not 0<=b<target.shape[1] or math.isfinite(target[k,b]):
                        raise ValueError(f"C_U6_SPECTRUM_DUPLICATE_OR_BIN:{j}:{tag}:{b}")
                    target[k,b]=float(f[3]); seen[k,channel]+=1
            elif tag=="U6END":
                if end is not None or len(f)!=4: raise ValueError("C_U6_END_GRAMMAR")
                end=(f[1],int(f[2]),int(f[3]))
            elif tag in {"META","NODE","STEP","END","U4NODE","U4STEP","U4END",
                         "U5NODE","U5STEP","U5EVENT","U5END"}:
                continue
            else: raise ValueError(f"C_UNKNOWN_RECORD:{lineno}:{tag}")
    if node is None or end is None or int(node[0])!=START_J or int(node[1])!=START_GLOBAL_IZ:
        raise ValueError("C_U6_NODE_OR_END_MISSING")
    count=end[2]
    if not (0<=count<=n and int(np.sum(np.isfinite(rows[:,0])))==count and
            np.array_equal(rows[:count,0].astype(int),np.arange(START_J,START_J+count)) and
            np.all(seen[:count]==(311,311,3))):
        raise ValueError("C_U6_ROW_OR_SPECTRUM_COUNT")
    for array in (rows[:count],v[:count],a[:count],l[:count]):
        if not np.all(np.isfinite(array)): raise ValueError("C_U6_NONFINITE")
    return {"node":node,"end":end,"rows":rows[:count],"virtual":v[:count],
            "average":a[:count],"lyman":l[:count]}


def validate_manifest(path:Path) -> dict:
    m=json.loads(path.read_text())
    if not m.get("controller_verified") or m.get("base_revision")!=BASE_REVISION:
        raise ValueError("U6_EXECUTION_MANIFEST_BASE_MISMATCH")
    for name,want in (("u5_stop_npz_sha256",U5_STOP_NPZ_SHA256),
                      ("u5_stop_json_sha256",U5_STOP_JSON_SHA256),
                      ("u5_original_verification_sha256",U5_ORIGINAL_VERIFICATION_SHA256),
                      ("u5_scoped_audit_sha256",U5_SCOPED_AUDIT_SHA256),
                      ("source_zip_sha256",PINNED_ZIP_SHA)):
        if m.get(name)!=want: raise ValueError(f"U6_EXECUTION_MANIFEST_INPUT_MISMATCH:{name}")
    if m.get("u6_files_sha256")!={k:sha256(ROOT/k) for k in U6_FILES}:
        raise ValueError("U6_EXECUTION_MANIFEST_CODE_MISMATCH")
    if not isinstance(m.get("execution_revision"),str) or len(m["execution_revision"])!=40:
        raise ValueError("U6_EXECUTION_REVISION_MISSING")
    return m


def main() -> int:
    p=argparse.ArgumentParser(); modes=p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight",action="store_true"); modes.add_argument("--execute",action="store_true")
    p.add_argument("--evidence-dir",type=Path,required=True)
    p.add_argument("--u5-stop-npz",type=Path,required=True)
    p.add_argument("--u5-stop-json",type=Path,required=True)
    p.add_argument("--u5-original-verification",type=Path,required=True)
    p.add_argument("--u5-scoped-audit",type=Path,required=True)
    p.add_argument("--u5-scoped-admission",type=Path,required=True)
    p.add_argument("--execution-manifest",type=Path)
    p.add_argument("--source-dir",type=Path)
    p.add_argument("--max-extra-accepted",type=int,default=EXTRA_ACCEPTED)
    args=p.parse_args()
    if not 1<=args.max_extra_accepted<=EXTRA_ACCEPTED: raise SystemExit("U6_ACCEPTED_CAP_INVALID")
    if args.execute and args.execution_manifest is None: raise SystemExit("U6_EXECUTION_MANIFEST_REQUIRED")
    ev=args.evidence_dir.resolve(); ev.mkdir(parents=True,exist_ok=False)
    report={"status":"INCOMPLETE","first_failure":None,"limits":{
        "extra_accepted_max":2604,"full_evaluations_max":2604,"common_input_max":14,
        "address_space_bytes":2*1024**3,"cpu_s":270,"wall_s":300,
        "native_oracle_s":60,"build_s":30}}
    try:
        checkpoint,boundary=load_admitted_u5_stop(args.u5_stop_npz,args.u5_stop_json,
            args.u5_original_verification,args.u5_scoped_audit,args.u5_scoped_admission)
        report["start"]={"j":START_J,"global_iz":int(checkpoint["global_iz"][-1]),
            "z":float(checkpoint["z"][-1]),"xe":float(checkpoint["xe"][-1]),
            "Tm_K":float(checkpoint["Tm_K"][-1]),"photon_columns":checkpoint["virtual_out"].shape[1],
            "thermal_prev":boundary["thermal_prev"],"thermal_prev2":boundary["thermal_prev2"]}
        report["u5_admission_sha256"]=boundary["admission_sha256"]
        if args.preflight:
            report["status"]="PREFLIGHT_ONLY"; return 0
        validate_manifest(args.execution_manifest)
        report["execution_manifest_sha256"]=sha256(args.execution_manifest)
        with (ev/"controller_execution_manifest.json").open("xb") as out:
            out.write(args.execution_manifest.read_bytes())
        src=safe_source(args.source_dir,ev)
        report["source_zip_sha256"]=PINNED_ZIP_SHA
        report["source_sha256"]={k:sha256(src/k) for k in PINNED_SOURCE}
        with (ev/"source_manifest.json").open("x") as out:
            json.dump({"source_zip_sha256":PINNED_ZIP_SHA,"source_members":zip_member_hashes(),
                "source_c":report["source_sha256"],"u5_stop_npz_sha256":U5_STOP_NPZ_SHA256,
                "u5_scoped_admission_sha256":boundary["admission_sha256"],
                "u6_files_sha256":{k:sha256(ROOT/k) for k in U6_FILES}},out,sort_keys=True,indent=2)
            out.write("\n")
        os.chdir(src)
        cpu=min(os.sched_getaffinity(0)); os.sched_setaffinity(0,{cpu}); report["affinity"]=[cpu]
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(270,270))
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("U6_WALL_LIMIT_300S")))
        signal.alarm(300)
        c=HyRec2012Cosmology()
        table=OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        source=make_hmla_source(c,table)
        common_cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-I",str(src),
                   str(ROOT/"scripts/c_harness/original_hyrec_full_source_harness.c"),
                   str(src/"hydrogen.c"),str(src/"hyrectools.c"),"-lm","-o",str(ev/"liboriginal_full_source.so")]
        report["common_build"]=run_capture_u6(common_cc,src,ev/"common_build_stdout.txt",ev/"common_build_stderr.txt",30,os.environ.copy())
        if report["common_build"]["returncode"]: raise RuntimeError("U6_COMMON_C_BUILD_FAILED")
        thermal_cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-I",str(src),
                    str(src/"history.c"),str(src/"hydrogen.c"),str(src/"helium.c"),str(src/"hyrectools.c"),
                    "-lm","-o",str(ev/"liboriginal_history.so")]
        report["thermal_build"]=run_capture_u6(thermal_cc,src,ev/"thermal_build_stdout.txt",ev/"thermal_build_stderr.txt",30,os.environ.copy())
        if report["thermal_build"]["returncode"]: raise RuntimeError("U6_THERMAL_C_BUILD_FAILED")
        native_cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(src),
                   str(ROOT/"scripts/c_harness/original_hyrec_full_thermal_to_rt_harness.c"),
                   str(src/"history.c"),str(src/"hydrogen.c"),str(src/"helium.c"),str(src/"hyrectools.c"),
                   "-lm","-o",str(ev/"native_u6_oracle")]
        report["native_build"]=run_capture_u6(native_cc,src,ev/"native_build_stdout.txt",ev/"native_build_stderr.txt",30,os.environ.copy())
        if report["native_build"]["returncode"]: raise RuntimeError("U6_NATIVE_C_BUILD_FAILED")
        report["native_binary_sha256"]=sha256(ev/"native_u6_oracle")
        report["native_run"]=run_capture_u6([str(ev/"native_u6_oracle"),str(args.max_extra_accepted)],
            src,ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",60,os.environ.copy())
        if report["native_run"]["returncode"]: raise RuntimeError("U6_NATIVE_C_ORACLE_FAILED")
        native=parse_native(ev/"native_oracle_stdout.csv")
        report["native_c_stdout_sha256"]=sha256(ev/"native_oracle_stdout.csv")
        start=native["node"]
        if (int(start[1])!=START_GLOBAL_IZ or
                abs(start[2]-float(checkpoint["z"][-1]))>2e-12 or
                abs(start[4]-float(checkpoint["xe"][-1]))/max(1e-8,abs(start[4]))>5e-9 or
                abs(start[5]-float(checkpoint["Tm_K"][-1]))/max(1.,abs(start[5]))>5e-10):
            raise ArithmeticError("U6_C_PY_START_STATE_PARITY")
        for got,want,name in ((start[6],float(checkpoint["hydrogen_rhs_dln_a"][-1]),"h_prev"),
                              (start[7],float(checkpoint["hydrogen_rhs_dln_a"][-2]),"h_prev2"),
                              (start[8],boundary["thermal_prev"],"t_prev"),
                              (start[9],boundary["thermal_prev2"],"t_prev2")):
            if abs(got-want)/max(1.,abs(got))>2e-8:
                raise ArithmeticError(f"U6_C_PY_START_MEMORY_PARITY:{name}")
        h_oracle=load_u2_verifier().FullSourceCOracle(ev/"liboriginal_full_source.so",src,c)
        oracle=CombinedOracle(h_oracle,ev/"liboriginal_history.so",c)
        result=continue_full_thermal_to_rt(checkpoint,boundary,c,source,
            common_input_oracle=oracle,max_extra_accepted=args.max_extra_accepted,
            checkpoint_callback=lambda payload:save_checkpoint(ev,payload))
        n=result["accepted_extra"]
        if n!=native["end"][2] or result["status"]!=native["end"][0]:
            raise ArithmeticError("U6_C_PY_END_STATUS_OR_COUNT_PARITY")
        state_max={k:0. for k in ("xH1s","xHII","xe","xHeII","Tm_K")}
        h_max=t_max=hm_max=tm_max=0.; h_rec_max=t_rec_max=0.
        spec_max={k:0. for k in ("virtual","average","lyman")}
        spec_fail={k:0 for k in spec_max}; spec_first={k:[] for k in spec_max}
        table2=load_u2_verifier()._canonical_twophoton_table(table.archive_path)
        for k in range(n):
            j=START_J+k; crow=native["rows"][k]
            pyrow={"iz":int(result["nodes"]["global_iz"][j+1]),
                "z":float(result["nodes"]["z"][j+1]),
                "xH1s":float(result["nodes"]["xH1s"][j+1]),
                "xHII":float(result["nodes"]["xHII"][j+1]),
                "xHeII":float(result["nodes"]["xHeII"][j+1]),
                "xe":float(result["nodes"]["xe"][j+1]),
                "Tm_K":float(result["nodes"]["Tm_K"][j+1]),"post_saha":False}
            cref={"iz":int(crow[1]),"z":crow[2],"xH1s":crow[3],"xHII":crow[4],
                  "xHeII":0.,"xe":crow[4],"Tm_K":crow[5],"post_saha":False}
            errors=compare_state(pyrow,cref,j)
            for name,val in errors.items():state_max[name]=max(state_max[name],val)
            p_h=float(result["nodes"]["xe"][j])+SOURCE_DLNA*(
                1.25*float(result["hydrogen_rhs_dln_a"][j])-
                .25*float(result["hydrogen_rhs_dln_a"][j-2]))
            p_t=float(result["nodes"]["Tm_K"][j])+SOURCE_DLNA*(
                1.25*float(result["thermal_rhs_dln_a"][j])-
                .25*float(result["thermal_rhs_dln_a"][j-2]))
            h_rec=abs(p_h-pyrow["xe"]); t_rec=abs(p_t-pyrow["Tm_K"])
            if h_rec>2e-15 or t_rec>2e-12:
                raise ArithmeticError(f"U6_PYTHON_STEP_RECURRENCE:{j}:{h_rec}:{t_rec}")
            h_rec_max=max(h_rec_max,h_rec); t_rec_max=max(t_rec_max,t_rec)
            c_prev_x=float(start[4]) if k==0 else float(native["rows"][k-1,4])
            c_prev_t=float(start[5]) if k==0 else float(native["rows"][k-1,5])
            c_hprev2=float(start[7]) if k==0 else float(start[6]) if k==1 else float(native["rows"][k-2,6])
            c_tprev2=float(start[9]) if k==0 else float(start[8]) if k==1 else float(native["rows"][k-2,7])
            c_hpred=c_prev_x+SOURCE_DLNA*(1.25*float(crow[6])-.25*c_hprev2)
            c_tpred=c_prev_t+SOURCE_DLNA*(1.25*float(crow[7])-.25*c_tprev2)
            if abs(c_hpred-float(crow[4]))>2e-15 or abs(c_tpred-float(crow[5]))>2e-12:
                raise ArithmeticError(f"U6_C_STEP_RECURRENCE:{j}")
            for name,pyv,cv,lim in (("h",result["hydrogen_rhs_dln_a"][j],crow[6],2e-7),
                ("t",result["thermal_rhs_dln_a"][j],crow[7],2e-8),
                ("hm",result["hydrogen_rhs_dln_a"][j-1],crow[8],2e-8),
                ("tm",result["thermal_prev_after"][j],crow[9],2e-8),
                ("tm2",result["thermal_prev2_after"][j],crow[10],2e-8)):
                d=abs(float(pyv)-float(cv))/max(1.,abs(float(cv)))
                if not math.isfinite(d) or d>lim: raise ArithmeticError(f"U6_C_PY_MEMORY_OR_RHS:{j}:{name}:{d}")
                if name=="h":h_max=max(h_max,d)
                elif name=="t":t_max=max(t_max,d)
                elif name=="hm":hm_max=max(hm_max,d)
                else:tm_max=max(tm_max,d)
            tr=8.617343e-5*c.T0_K*(1+float(result["nodes"]["z"][j]))
            fbbv=1/np.expm1(table2.energy_eV/tr)
            fbbl=1/np.expm1(np.array((10.198714553953742,12.087365397278509,12.748393192442178))/tr)
            for name,pv,cv,bb in (("virtual",result["virtual_out"][:,j],native["virtual"][k],fbbv),
                ("average",result["average_virtual"][:,j],native["average"][k],fbbv),
                ("lyman",result["lyman_out"][:,j],native["lyman"][k],fbbl)):
                tol=1e-7*np.maximum(np.abs(pv),np.abs(cv))+1e-10*bb
                ratio=np.abs(pv-cv)/tol
                if not np.all(np.isfinite(ratio)): raise ArithmeticError(f"U6_NONFINITE_PHOTON_RATIO:{j}:{name}")
                spec_max[name]=max(spec_max[name],float(np.max(ratio)))
                failed=np.flatnonzero(ratio>1)
                if failed.size:
                    spec_fail[name]+=len(failed)
                    for b in failed[:max(0,32-len(spec_first[name]))]:spec_first[name].append([j,int(b),float(ratio[b])])
        if spec_fail["virtual"] or spec_fail["lyman"]:
            raise ArithmeticError(f"U6_VIRTUAL_OR_LYMAN_PHOTON_PARITY:{spec_first}")
        if n==EXTRA_ACCEPTED and (int(result["nodes"]["global_iz"][-1])!=END_GLOBAL_IZ or
                                  len(result["samples"])!=len(SAMPLE_J)):
            raise ArithmeticError("U6_RT_STOP_OR_SAMPLE_COUNT")
        report.update({"status":result["status"] if not spec_fail["average"] else
                       "HOLD_ORIGINAL_AVERAGE_PHOTON_PARITY",
            "physics_progress_status":result["status"],"accepted_extra":n,
            "python_full_evaluations":result["full_evaluations"],
            "end_global_iz":int(result["nodes"]["global_iz"][-1]),
            "end_z":float(result["nodes"]["z"][-1]),
            "state_max_scaled":state_max,"hydrogen_rhs_max_scaled":h_max,
            "thermal_rhs_max_scaled":t_max,"hydrogen_memory_max_scaled":hm_max,
            "thermal_memory_max_scaled":tm_max,"spectrum_max_tolerance_ratio":spec_max,
            "hydrogen_recurrence_max_absolute":h_rec_max,
            "thermal_recurrence_max_absolute":t_rec_max,
            "matrix_residual_max":float(np.max(result["matrix_residual"][START_J:START_J+n])),
            "spectrum_failure_count":spec_fail,"spectrum_first_failures":spec_first,
            "common_input_sample_j":result["samples"],"common_input_max":result["common_max"],
            "checkpoint_count":len(list(ev.glob("checkpoint_*.npz"))),
            "claim_ceiling":"bounded q=0 original HyRec H+Tm FULL until RT input; no EMLA continuation, full primordial history, Bianchi, REI or CMB claim"})
    except BaseException as exc:
        report["status"]=str(exc) if str(exc).startswith("HOLD_NEXT_STAGE_REQUIRED") else "FAIL"
        report["first_failure"]={"type":type(exc).__name__,"message":str(exc),"traceback":traceback.format_exc()}
    finally:
        report["resource"]={"self_user_cpu_s":resource.getrusage(resource.RUSAGE_SELF).ru_utime,
            "self_system_cpu_s":resource.getrusage(resource.RUSAGE_SELF).ru_stime,
            "self_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "child_user_cpu_s":resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime,
            "child_system_cpu_s":resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime}
        with (ev/"verification.json").open("x") as out:
            json.dump(report,out,sort_keys=True,indent=2); out.write("\n")
        print(json.dumps(report,sort_keys=True))
    return 0 if report["status"] in {"PREFLIGHT_ONLY","STOP_BEFORE_EMLA2S2P_RT_BOUNDARY"} else 1

if __name__=="__main__":raise SystemExit(main())

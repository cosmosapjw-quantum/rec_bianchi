#!/usr/bin/env python3
"""Bounded U7 EMLA2s2p continuation against one original HyRec C replay."""
from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import resource
import signal
import sys
import traceback
from pathlib import Path

os.environ.update({k:"1" for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS")})
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from full_bianchi_hyrec.trajectory.primordial_2012_emla_to_z20 import (
    START_J,START_GLOBAL_IZ,END_J,END_GLOBAL_IZ,EXTRA_ACCEPTED,SAMPLE_J,
    U6_STOP_NPZ_SHA256,U6_STOP_JSON_SHA256,U6_VERIFICATION_SHA256,
    U6_C_STDOUT_SHA256,U6_ADMISSION_SHA256,sha256,source_z20_cubic,
    load_admitted_u6_stop,continue_emla_to_z20,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA
from verify_r3g_continuation import safe_source,zip_member_hashes,PINNED_ZIP_SHA,PINNED_SOURCE,compare_state
from verify_r3g_full_thermal_continuation import run_capture_u6
from verify_r3g_hydrogen_transition import save_checkpoint

U7_FILES=(
 "src/full_bianchi_hyrec/trajectory/primordial_2012_emla_to_z20.py",
 "scripts/verify_r3g_emla_to_z20.py",
 "scripts/c_harness/original_hyrec_emla_to_z20_harness.c",
 "tests/trajectory/test_primordial_2012_emla_to_z20.py",
)


def parse_native(path:Path, expected:int=EXTRA_ACCEPTED)->dict:
    rows=np.full((expected,15),np.nan)
    node=end=z20=None
    with path.open() as stream:
        for lineno,line in enumerate(stream,1):
            f=line.rstrip("\n").split(","); tag=f[0]
            if tag=="U7NODE":
                if node is not None or len(f)!=10: raise ValueError("U7_C_NODE_GRAMMAR")
                node=[float(x) for x in f[1:]]
            elif tag=="U7STEP":
                if len(f)!=17 or f[16]!="EMLA2s2p": raise ValueError(f"U7_C_STEP_MODEL_OR_GRAMMAR:{lineno}:{len(f)}")
                j=int(f[1]);k=j-START_J
                if not 0<=k<expected or math.isfinite(rows[k,0]):raise ValueError("U7_C_STEP_INDEX")
                rows[k]=[float(x) for x in f[1:16]]
            elif tag=="U7Z20":
                if z20 is not None or len(f)!=5:raise ValueError("U7_C_Z20_GRAMMAR")
                z20=[float(x) for x in f[1:]]
            elif tag=="U7END":
                if end is not None or len(f)!=4:raise ValueError("U7_C_END_GRAMMAR")
                end=(f[1],int(f[2]),int(f[3]))
            elif tag in {"META","NODE","STEP","END","V","A","L","U4NODE","U4STEP","U4END",
                         "U5NODE","U5STEP","U5EVENT","U5END","U6NODE","U6STEP","U6END"}:
                continue
            else:raise ValueError(f"U7_C_UNKNOWN_RECORD:{lineno}:{tag}")
    if node is None or end is None or int(node[0])!=START_J or int(node[1])!=START_GLOBAL_IZ:
        raise ValueError("U7_C_BOUNDARY_MISSING")
    n=end[2]
    if not (0<=n<=expected and end[1]==START_J+n and
            np.array_equal(rows[:n,0].astype(int),np.arange(START_J,START_J+n)) and
            np.all(np.isfinite(rows[:n])) and np.all(np.isnan(rows[n:]))):
        raise ValueError("U7_C_STEP_COUNT_OR_FINITE")
    if n==EXTRA_ACCEPTED:
        if z20 is None or int(z20[2])!=69997 or end[0]!="STOP_AT_Z20_CUBIC_STENCIL":
            raise ValueError("U7_C_Z20_STENCIL_MISSING")
    elif z20 is not None:raise ValueError("U7_C_EARLY_Z20")
    return {"node":node,"rows":rows[:n],"end":end,"z20":z20}


class CommonOracle:
    def __init__(self,library:Path,c:HyRec2012Cosmology):
        self.lib=ctypes.CDLL(str(library));self.c=c
        self.h=self.lib.rec_r3g_u7_emla_rhs
        self.h.argtypes=[ctypes.c_double]*7;self.h.restype=ctypes.c_double
        self.t=self.lib.rec_r3g_u7_thermal_rhs
        self.t.argtypes=[ctypes.c_double]*7;self.t.restype=ctypes.c_double
        self.h_calls=0;self.t_calls=0
    def __call__(self,j,z,xe,tm):
        self.h_calls+=1
        tr=self.c.T0_K*(1+z)
        return self.h(xe,tm,tr,1e-6*self.c.nH0_m3*(1+z)**3,
                      self.c.hubble_s(z),self.c.fsR,self.c.meR)
    def thermal_rhs(self,xe,tm,z):
        self.t_calls+=1
        tr=self.c.T0_K*(1+z)
        return self.t(xe,tm,tr,self.c.hubble_s(z),self.c.fHe,self.c.fsR,self.c.meR)


def validate_manifest(path:Path)->dict:
    m=json.loads(path.read_text())
    for name,want in (("u6_stop_npz_sha256",U6_STOP_NPZ_SHA256),
                      ("u6_stop_json_sha256",U6_STOP_JSON_SHA256),
                      ("u6_verification_sha256",U6_VERIFICATION_SHA256),
                      ("u6_c_stdout_sha256",U6_C_STDOUT_SHA256),
                      ("u6_admission_sha256",U6_ADMISSION_SHA256),
                      ("source_zip_sha256",PINNED_ZIP_SHA)):
        if m.get(name)!=want:raise ValueError(f"U7_MANIFEST_INPUT_SHA:{name}")
    if not m.get("controller_verified") or m.get("u7_files_sha256")!={k:sha256(ROOT/k) for k in U7_FILES}:
        raise ValueError("U7_MANIFEST_CODE_OR_CONTROLLER")
    if not isinstance(m.get("execution_revision"),str) or len(m["execution_revision"])!=40:
        raise ValueError("U7_MANIFEST_REVISION")
    return m


def main()->int:
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight",action="store_true");mode.add_argument("--execute",action="store_true")
    p.add_argument("--evidence-dir",type=Path,required=True)
    p.add_argument("--u6-stop-npz",type=Path,required=True)
    p.add_argument("--u6-stop-json",type=Path,required=True)
    p.add_argument("--u6-verification",type=Path,required=True)
    p.add_argument("--u6-c-stdout",type=Path,required=True)
    p.add_argument("--u6-admission",type=Path,required=True)
    p.add_argument("--execution-manifest",type=Path)
    p.add_argument("--source-dir",type=Path)
    p.add_argument("--max-extra-accepted",type=int,default=EXTRA_ACCEPTED)
    args=p.parse_args()
    if not 1<=args.max_extra_accepted<=EXTRA_ACCEPTED:raise SystemExit("U7_ACCEPTED_CAP_INVALID")
    if args.execute and args.execution_manifest is None:raise SystemExit("U7_MANIFEST_REQUIRED")
    ev=args.evidence_dir.resolve();ev.mkdir(parents=True,exist_ok=False)
    report={"task":"R3G-U7-EMLA-TO-Z20-001","status":"INCOMPLETE","first_failure":None,
      "limits":{"emla_evaluations":EXTRA_ACCEPTED,"common_input":32,"cpu_s":270,"wall_s":300,
                "as_bytes":2*1024**3,"c_build_s":30,"c_replay_s":60},
      "historic_u5_original_verification":"FAIL","historic_u5_average_gate":"HOLD_ORIGINAL_TOLERANCE_NOT_MET",
      "temporal_refinement":"NOT_RUN","rei_activation":False}
    try:
        cp,boundary=load_admitted_u6_stop(args.u6_stop_npz,args.u6_stop_json,
            args.u6_verification,args.u6_c_stdout,args.u6_admission)
        report["start"]={"j":START_J,"global_iz":int(cp["global_iz"][-1]),
          "z":float(cp["z"][-1]),"xe":float(cp["xe"][-1]),"Tm_K":float(cp["Tm_K"][-1]),
          "u6_stop_npz_sha256":U6_STOP_NPZ_SHA256,"u6_admission_sha256":U6_ADMISSION_SHA256}
        if args.preflight:
            report["status"]="PREFLIGHT_ONLY";return 0
        m=validate_manifest(args.execution_manifest)
        report["execution_revision"]=m["execution_revision"]
        with (ev/"controller_execution_manifest.json").open("xb") as out:out.write(args.execution_manifest.read_bytes())
        src=safe_source(args.source_dir,ev);report["source_zip_sha256"]=PINNED_ZIP_SHA
        with (ev/"source_manifest.json").open("x") as out:
            json.dump({"source_zip_sha256":PINNED_ZIP_SHA,"source_members":zip_member_hashes(),
              "source_c":{k:sha256(src/k) for k in PINNED_SOURCE},
              "u7_files_sha256":m["u7_files_sha256"]},out,sort_keys=True,indent=2);out.write("\n")
        os.chdir(src)
        cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu});report["affinity"]=[cpu]
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(270,270))
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("U7_WALL_LIMIT_300S")))
        signal.alarm(300)
        c=HyRec2012Cosmology()
        table=OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        source=make_hmla_source(c,table)
        cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(src),
          str(ROOT/"scripts/c_harness/original_hyrec_emla_to_z20_harness.c"),
          *[str(src/f) for f in ("history.c","hydrogen.c","helium.c","hyrectools.c")],"-lm"]
        report["native_build"]=run_capture_u6(cc+["-o",str(ev/"native_u7_oracle")],src,
            ev/"native_build_stdout.txt",ev/"native_build_stderr.txt",30,os.environ.copy())
        if report["native_build"]["returncode"]:raise RuntimeError("U7_C_BUILD_FAILED")
        shared=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-I",str(src),
          str(ROOT/"scripts/c_harness/original_hyrec_emla_to_z20_harness.c"),
          *[str(src/f) for f in ("history.c","hydrogen.c","helium.c","hyrectools.c")],"-lm"]
        report["common_build"]=run_capture_u6(shared+["-o",str(ev/"libu7_emla.so")],src,
            ev/"common_build_stdout.txt",ev/"common_build_stderr.txt",30,os.environ.copy())
        if report["common_build"]["returncode"]:raise RuntimeError("U7_COMMON_BUILD_FAILED")
        report["native_binary_sha256"]=sha256(ev/"native_u7_oracle")
        report["common_binary_sha256"]=sha256(ev/"libu7_emla.so")
        report["native_run"]=run_capture_u6([str(ev/"native_u7_oracle"),str(args.max_extra_accepted)],src,
            ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",60,os.environ.copy())
        if report["native_run"]["returncode"]:raise RuntimeError("U7_C_REPLAY_FAILED")
        native=parse_native(ev/"native_oracle_stdout.csv",args.max_extra_accepted)
        report["native_c_stdout_sha256"]=sha256(ev/"native_oracle_stdout.csv")
        start=native["node"]
        if (abs(start[2]-float(cp["z"][-1]))>2e-12 or
            abs(start[3]-float(cp["xe"][-1]))/max(abs(start[3]),1e-8)>5e-9 or
            abs(start[4]-float(cp["Tm_K"][-1]))/max(abs(start[4]),1.)>5e-10):
            raise ArithmeticError("U7_C_PY_START_STATE")
        for label,pv,cv in (("hprev",boundary["hydrogen_prev"],start[5]),
                            ("hprev2",boundary["hydrogen_prev2"],start[6]),
                            ("tprev",boundary["thermal_prev"],start[7]),
                            ("tprev2",boundary["thermal_prev2"],start[8])):
            if abs(pv-cv)/max(1,abs(cv))>2e-8:raise ArithmeticError(f"U7_C_PY_START_MEMORY:{label}")
        oracle=CommonOracle(ev/"libu7_emla.so",c)
        result=continue_emla_to_z20(cp,boundary,c,source,common_input_oracle=oracle,
            checkpoint_callback=lambda payload:save_checkpoint(ev,payload),
            max_extra_accepted=args.max_extra_accepted)
        n=result["accepted_extra"]
        if n!=native["end"][2] or result["status"]!=native["end"][0]:
            raise ArithmeticError("U7_C_PY_STATUS_OR_COUNT")
        maxima={k:0. for k in ("xe","xHII","xH1s","Tm_K","hydrogen_rhs","thermal_rhs",
                               "hydrogen_memory","thermal_memory","hydrogen_recurrence","thermal_recurrence")}
        for k,crow in enumerate(native["rows"]):
            j=START_J+k
            cnext={"iz":int(crow[11]),"z":crow[12],"xH1s":1-crow[13],"xHII":crow[13],
                   "xHeII":0.,"xe":crow[13],"Tm_K":crow[14],"post_saha":False}
            pnext={"iz":int(result["nodes"]["global_iz"][j+1]),"z":float(result["nodes"]["z"][j+1]),
                   "xH1s":float(result["nodes"]["xH1s"][j+1]),"xHII":float(result["nodes"]["xHII"][j+1]),
                   "xHeII":0.,"xe":float(result["nodes"]["xe"][j+1]),
                   "Tm_K":float(result["nodes"]["Tm_K"][j+1]),"post_saha":False}
            errs=compare_state(pnext,cnext,j)
            for key in ("xe","xHII","xH1s","Tm_K"):maxima[key]=max(maxima[key],errs[key])
            if int(crow[1])!=j+18223 or abs(crow[2]-float(result["nodes"]["z"][j]))>2e-12:
                raise ArithmeticError(f"U7_C_INPUT_CLOCK:{j}")
            for name,pv,cv,lim in (("hydrogen_rhs",result["hydrogen_rhs_dln_a"][j],crow[5],2e-7),
               ("thermal_rhs",result["thermal_rhs_dln_a"][j],crow[6],2e-8),
               ("hydrogen_memory",result["hydrogen_rhs_dln_a"][j-1],crow[7],2e-8),
               ("hydrogen_memory",result["hydrogen_rhs_dln_a"][j-2],crow[8],2e-8),
               ("thermal_memory",result["thermal_rhs_dln_a"][j-1],crow[9],2e-8),
               ("thermal_memory",result["thermal_rhs_dln_a"][j-2],crow[10],2e-8)):
                d=abs(float(pv)-float(cv))/max(1.,abs(float(cv)))
                if not math.isfinite(d) or d>lim:raise ArithmeticError(f"U7_C_PY_RHS_OR_MEMORY:{j}:{name}:{d}")
                maxima[name]=max(maxima[name],d)
            for name,arr,old,deriv,old2,cold,cderiv,cold2,cnextval,lim in (
                ("hydrogen_recurrence",result["nodes"]["xe"],float(result["nodes"]["xe"][j]),
                 float(result["hydrogen_rhs_dln_a"][j]),float(result["hydrogen_rhs_dln_a"][j-2]),
                 crow[3],crow[5],crow[8],crow[13],2e-15),
                ("thermal_recurrence",result["nodes"]["Tm_K"],float(result["nodes"]["Tm_K"][j]),
                 float(result["thermal_rhs_dln_a"][j]),float(result["thermal_rhs_dln_a"][j-2]),
                 crow[4],crow[6],crow[10],crow[14],2e-12)):
                pred=old+SOURCE_DLNA*(1.25*deriv-.25*old2)
                cpred=cold+SOURCE_DLNA*(1.25*cderiv-.25*cold2)
                d=max(abs(pred-float(arr[j+1])),abs(cpred-cnextval))
                if d>lim:raise ArithmeticError(f"U7_STEP_RECURRENCE:{j}:{name}:{d}")
                maxima[name]=max(maxima[name],d)
        if oracle.h_calls!=len(result["samples"]) or oracle.t_calls!=len(result["samples"]):
            raise ArithmeticError("U7_COMMON_INPUT_CALL_ACCOUNTING")
        if n==EXTRA_ACCEPTED:
            if int(result["nodes"]["global_iz"][-1])!=END_GLOBAL_IZ or result["samples"]!=list(SAMPLE_J):
                raise ArithmeticError("U7_STOP_OR_SAMPLES")
            pxe=source_z20_cubic(result["nodes"]["xe"])["value"]
            ptm=source_z20_cubic(result["nodes"]["Tm_K"])["value"]
            cxe,ctm=native["z20"][:2]
            xe_err=abs(pxe-cxe)/max(abs(cxe),1e-8)
            tm_err=abs(ptm-ctm)/max(abs(ctm),1.)
            report["z20"]={"python_xe":pxe,"python_Tm_K":ptm,"original_c_xe":cxe,
                "original_c_Tm_K":ctm,"xe_relative_error":xe_err,"Tm_relative_error":tm_err,
                "source_cubic_global_i":int(native["z20"][2]),"source_fraction":native["z20"][3]}
            if xe_err>5e-9 or tm_err>5e-10:raise ArithmeticError("U7_Z20_CUBIC_PARITY")
            with (ev/"candidate_rei_donor.json").open("x") as out:
                json.dump(result["candidate_donor"],out,sort_keys=True,indent=2);out.write("\n")
        report.update({"status":result["status"],"accepted_extra":n,
          "emla_evaluations":result["emla_evaluations"],"stop_failure":result["failure"],
          "end_global_iz":int(result["nodes"]["global_iz"][-1]),"end_z":float(result["nodes"]["z"][-1]),
          "maxima":maxima,"common_input_max":result["common_max"],
          "common_input_sample_j":result["samples"],"common_h_calls":oracle.h_calls,
          "common_thermal_calls":oracle.t_calls,"checkpoint_count":len(list(ev.glob("checkpoint_*.npz"))),
          "claim_ceiling":"q=0 source EMLA H+Tm to z20; temporal refinement and REI activation NOT_RUN"})
    except BaseException as exc:
        report["status"]=str(exc) if str(exc).startswith("HOLD_NEXT_STAGE_REQUIRED") else "FAIL"
        report["first_failure"]={"type":type(exc).__name__,"message":str(exc),"traceback":traceback.format_exc()}
    finally:
        report["resource"]={"self_user_cpu_s":resource.getrusage(resource.RUSAGE_SELF).ru_utime,
          "self_system_cpu_s":resource.getrusage(resource.RUSAGE_SELF).ru_stime,
          "self_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          "child_user_cpu_s":resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime,
          "child_system_cpu_s":resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime}
        with (ev/"verification.json").open("x") as out:json.dump(report,out,sort_keys=True,indent=2);out.write("\n")
        print(json.dumps(report,sort_keys=True))
    return 0 if report["status"] in {"PREFLIGHT_ONLY","STOP_AT_Z20_CUBIC_STENCIL",
       "BOUNDED_EMLA_INTERVAL_COMPLETE_BEFORE_Z20_STENCIL"} else 1


if __name__=="__main__":raise SystemExit(main())

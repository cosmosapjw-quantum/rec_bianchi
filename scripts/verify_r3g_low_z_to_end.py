#!/usr/bin/env python3
"""Verify independent U8 low-z HyRec H+Tm against original C production."""
from __future__ import annotations

import argparse
import ctypes
import gzip
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
from full_bianchi_hyrec.trajectory.primordial_2012_low_z_to_end import (
    START_J,START_GLOBAL_IZ,END_J,END_GLOBAL_IZ,EXTRA_ACCEPTED,SOURCE_NZ,SOURCE_IZH0,
    U7_STOP_NPZ_SHA256,U7_STOP_JSON_SHA256,U7_VERIFICATION_SHA256,
    U7_C_STDOUT_SHA256,U7_ADMISSION_SHA256,U1_ACCEPTED_ROWS_SHA256,U1_VERIFICATION_SHA256,
    sha256,source_emla_table_guard,source_interp1d,assemble_full_source_grid,
    load_admitted_u7_stop,continue_low_z_to_end,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA
from verify_r3g_continuation import safe_source,zip_member_hashes,PINNED_ZIP_SHA,PINNED_SOURCE,compare_state
from verify_r3g_full_thermal_continuation import run_capture_u6
from verify_r3g_hydrogen_transition import save_checkpoint

U8_FILES=(
 "src/full_bianchi_hyrec/trajectory/primordial_2012_low_z_to_end.py",
 "scripts/verify_r3g_low_z_to_end.py",
 "scripts/c_harness/original_hyrec_low_z_to_end_harness.c",
 "tests/trajectory/test_primordial_2012_low_z_to_end.py",
)
BASELINE_GZIP=ROOT/"research/rec_r3c_rei_bridge_20261015/HYREC_ORIGINAL_REI_MATCHED_STDOUT.gz"
BASELINE_GZIP_SHA256="cfd1a7293431e4410e7ec597acc793d6b56e2d1f4eb5cd13ed3f48aaef4e26fb"
BASELINE_STDOUT_SHA256="6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400"


def regenerated_baseline_byte_status(observed_sha256:str)->str:
    """Classify generated text identity separately from numerical agreement."""
    return ("BYTE_IDENTITY_MATCH" if observed_sha256==BASELINE_STDOUT_SHA256
            else "BYTE_IDENTITY_MISMATCH")


def parse_native(path:Path,expected:int=EXTRA_ACCEPTED)->dict:
    rows=np.full((expected,17),np.nan);models=[None]*expected
    node=event=end=production=None;prod_nodes={};outputs=np.full((8001,4),np.nan)
    baseline=[]
    with path.open() as stream:
        for lineno,line in enumerate(stream,1):
            f=line.rstrip("\n").split(",");tag=f[0]
            if tag=="U8NODE":
                if node is not None or len(f)!=10:raise ValueError("U8_C_NODE_GRAMMAR")
                node=[float(x) for x in f[1:]]
            elif tag=="U8STEP":
                if len(f)!=19 or f[12] not in {"EMLA2s2p","PEEBLES"}:
                    raise ValueError(f"U8_C_STEP_MODEL_OR_GRAMMAR:{lineno}:{len(f)}")
                j=int(f[1]);k=j-START_J
                if not 0<=k<expected or models[k] is not None:raise ValueError("U8_C_STEP_INDEX")
                rows[k]=[float(x) for x in f[1:12]+f[13:19]]
                models[k]=f[12]
            elif tag=="U8EVENT":
                if event is not None or len(f)!=7:raise ValueError("U8_C_EVENT_GRAMMAR")
                event={"j":int(f[1]),"global_iz":int(f[2]),"z":float(f[3]),
                       "reason":f[4],"tr_rescaled_eV":float(f[5]),"Tm_Tr_ratio":float(f[6])}
            elif tag=="U8END":
                if end is not None or len(f)!=6:raise ValueError("U8_C_END_GRAMMAR")
                end=(f[1],int(f[2]),int(f[3]),int(f[4]),f[5])
            elif tag=="U8PRODUCTION":
                if production is not None or len(f)!=3:raise ValueError("U8_C_PRODUCTION_GRAMMAR")
                production=(int(f[1]),int(f[2]))
            elif tag=="U8PRODNODE":
                if len(f)!=4:raise ValueError("U8_C_PRODNODE_GRAMMAR")
                iz=int(f[1])
                if iz in prod_nodes:raise ValueError("U8_C_PRODNODE_DUPLICATE")
                prod_nodes[iz]=(float(f[2]),float(f[3]))
            elif tag=="U8OUT":
                if len(f)!=5:raise ValueError("U8_C_OUTPUT_GRAMMAR")
                z=float(f[1]);i=8000-int(z)
                if not 0<=i<8001 or z!=float(8000-i) or math.isfinite(outputs[i,0]):
                    raise ValueError("U8_C_OUTPUT_INDEX")
                outputs[i]=[float(x) for x in f[1:]]
            elif tag=="U8BASELINE":
                if len(f)!=2:raise ValueError("U8_C_BASELINE_GRAMMAR")
                baseline.append(f[1]+"\n")
            elif tag in {"META","NODE","STEP","END","V","A","L","U4NODE","U4STEP","U4END",
                         "U5NODE","U5STEP","U5EVENT","U5END","U6NODE","U6STEP","U6END",
                         "U7NODE","U7STEP","U7END","U7Z20"}:
                continue
            else:raise ValueError(f"U8_C_UNKNOWN_RECORD:{lineno}:{tag}")
    if node is None or end is None or int(node[0])!=START_J or int(node[1])!=START_GLOBAL_IZ:
        raise ValueError("U8_C_START_OR_END_MISSING")
    n=end[2]
    if not (0<=n<=expected and end[1]==START_J+n and all(x is not None for x in models[:n]) and
            all(x is None for x in models[n:]) and np.all(np.isfinite(rows[:n])) and
            np.all(np.isnan(rows[n:])) and np.array_equal(rows[:n,0].astype(int),np.arange(START_J,START_J+n))):
        raise ValueError("U8_C_STEP_COUNT_OR_FINITE")
    if (event is None)!=(end[3]==-1):raise ValueError("U8_C_EVENT_END_CONTRADICTION")
    if event is not None and (event["global_iz"]!=end[3] or event["reason"]!=end[4]):
        raise ValueError("U8_C_EVENT_END_MISMATCH")
    if n==EXTRA_ACCEPTED:
        if (end[0]!="STOP_AT_SOURCE_Z0_CUBIC_STENCIL" or production!=(SOURCE_NZ,end[3]) or
                not np.all(np.isfinite(outputs)) or len(baseline)!=8001 or
                set(prod_nodes)!={START_GLOBAL_IZ,event["global_iz"],END_GLOBAL_IZ}):
            raise ValueError("U8_C_PRODUCTION_OR_OUTPUT_MISSING")
    elif production is not None or baseline or np.any(np.isfinite(outputs)):
        raise ValueError("U8_C_EARLY_PRODUCTION")
    return {"node":node,"rows":rows[:n],"models":models[:n],"event":event,
            "end":end,"production":production,"production_nodes":prod_nodes,
            "outputs":outputs,"baseline":"".join(baseline)}


class CommonOracle:
    def __init__(self,library:Path,c:HyRec2012Cosmology):
        self.lib=ctypes.CDLL(str(library));self.c=c
        self.h=self.lib.rec_r3g_u8_hydrogen_rhs
        self.h.argtypes=[ctypes.c_int]+[ctypes.c_double]*7;self.h.restype=ctypes.c_double
        self.t=self.lib.rec_r3g_u7_thermal_rhs
        self.t.argtypes=[ctypes.c_double]*7;self.t.restype=ctypes.c_double
        self.h_calls=self.t_calls=0
    def __call__(self,model,iz,z,xe,tm):
        self.h_calls+=1
        return self.h(2 if model=="EMLA2s2p" else 0,xe,tm,self.c.T0_K*(1+z),
                      1e-6*self.c.nH0_m3*(1+z)**3,self.c.hubble_s(z),self.c.fsR,self.c.meR)
    def thermal_rhs(self,xe,tm,z):
        self.t_calls+=1
        return self.t(xe,tm,self.c.T0_K*(1+z),self.c.hubble_s(z),
                      self.c.fHe,self.c.fsR,self.c.meR)


def validate_manifest(path:Path)->dict:
    m=json.loads(path.read_text())
    for key,want in (("u7_stop_npz_sha256",U7_STOP_NPZ_SHA256),
                     ("u7_stop_json_sha256",U7_STOP_JSON_SHA256),
                     ("u7_verification_sha256",U7_VERIFICATION_SHA256),
                     ("u7_c_stdout_sha256",U7_C_STDOUT_SHA256),
                     ("u7_admission_sha256",U7_ADMISSION_SHA256),
                     ("u1_rows_sha256",U1_ACCEPTED_ROWS_SHA256),
                     ("u1_verification_sha256",U1_VERIFICATION_SHA256),
                     ("baseline_gzip_sha256",BASELINE_GZIP_SHA256),
                     ("source_zip_sha256",PINNED_ZIP_SHA)):
        if m.get(key)!=want:raise ValueError(f"U8_MANIFEST_INPUT_SHA:{key}")
    if not m.get("controller_verified") or m.get("u8_files_sha256")!={k:sha256(ROOT/k) for k in U8_FILES}:
        raise ValueError("U8_MANIFEST_CODE_OR_CONTROLLER")
    if not isinstance(m.get("execution_revision"),str) or len(m["execution_revision"])!=40:
        raise ValueError("U8_MANIFEST_REVISION")
    return m


def main()->int:
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight",action="store_true");mode.add_argument("--execute",action="store_true")
    p.add_argument("--evidence-dir",type=Path,required=True)
    p.add_argument("--u7-stop-npz",type=Path,required=True)
    p.add_argument("--u7-stop-json",type=Path,required=True)
    p.add_argument("--u7-verification",type=Path,required=True)
    p.add_argument("--u7-c-stdout",type=Path,required=True)
    p.add_argument("--u7-admission",type=Path,required=True)
    p.add_argument("--u1-rows",type=Path,required=True)
    p.add_argument("--u1-verification",type=Path,required=True)
    p.add_argument("--execution-manifest",type=Path)
    p.add_argument("--source-dir",type=Path)
    p.add_argument("--max-extra-accepted",type=int,default=EXTRA_ACCEPTED)
    args=p.parse_args()
    if not 1<=args.max_extra_accepted<=EXTRA_ACCEPTED:raise SystemExit("U8_ACCEPTED_CAP_INVALID")
    if args.execute and args.execution_manifest is None:raise SystemExit("U8_MANIFEST_REQUIRED")
    ev=args.evidence_dir.resolve();ev.mkdir(parents=True,exist_ok=False)
    report={"task":"R3G-U8-LOW-Z-TO-END-001","status":"INCOMPLETE","first_failure":None,
      "limits":{"production_updates":EXTRA_ACCEPTED,"production_h_calls":EXTRA_ACCEPTED,
                "production_t_calls":EXTRA_ACCEPTED,"common_input_max_each":32,
                "cpu_s":270,"wall_s":300,"as_bytes":2*1024**3,"c_build_s":30,"c_replay_s":60},
      "historic_u5_original_verification":"FAIL","historic_u5_average_gate":"HOLD_ORIGINAL_TOLERANCE_NOT_MET",
      "temporal_refinement":"NOT_RUN","rei_activation":False}
    try:
        cp,boundary=load_admitted_u7_stop(args.u7_stop_npz,args.u7_stop_json,
            args.u7_verification,args.u7_c_stdout,args.u7_admission)
        if sha256(args.u1_rows)!=U1_ACCEPTED_ROWS_SHA256 or sha256(args.u1_verification)!=U1_VERIFICATION_SHA256:
            raise ValueError("U8_U1_PREFIX_SHA_MISMATCH")
        if sha256(BASELINE_GZIP)!=BASELINE_GZIP_SHA256:raise ValueError("U8_BASELINE_GZIP_SHA_MISMATCH")
        report["start"]={"j":START_J,"global_iz":int(cp["global_iz"][-1]),
          "z":float(cp["z"][-1]),"xe":float(cp["xe"][-1]),"Tm_K":float(cp["Tm_K"][-1]),
          "u7_admission_sha256":U7_ADMISSION_SHA256}
        if args.preflight:
            report["status"]="PREFLIGHT_ONLY";return 0
        m=validate_manifest(args.execution_manifest)
        report["execution_revision"]=m["execution_revision"]
        with (ev/"controller_execution_manifest.json").open("xb") as out:out.write(args.execution_manifest.read_bytes())
        src=safe_source(args.source_dir,ev)
        with (ev/"source_manifest.json").open("x") as out:
            json.dump({"source_zip_sha256":PINNED_ZIP_SHA,"source_members":zip_member_hashes(),
              "source_c":{k:sha256(src/k) for k in PINNED_SOURCE},
              "u8_files_sha256":m["u8_files_sha256"]},out,sort_keys=True,indent=2);out.write("\n")
        os.chdir(src)
        cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu});report["affinity"]=[cpu]
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(270,270))
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("U8_WALL_LIMIT_300S")))
        signal.alarm(300)
        c=HyRec2012Cosmology()
        table=OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        source=make_hmla_source(c,table)
        cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(src),
            str(ROOT/"scripts/c_harness/original_hyrec_low_z_to_end_harness.c"),
            *[str(src/f) for f in ("history.c","hydrogen.c","helium.c","hyrectools.c")],"-lm"]
        report["native_build"]=run_capture_u6(cc+["-o",str(ev/"native_u8_oracle")],src,
            ev/"native_build_stdout.txt",ev/"native_build_stderr.txt",30,os.environ.copy())
        if report["native_build"]["returncode"]:raise RuntimeError("U8_NATIVE_C_BUILD_FAILED")
        shared=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-I",str(src),
            str(ROOT/"scripts/c_harness/original_hyrec_low_z_to_end_harness.c"),
            *[str(src/f) for f in ("history.c","hydrogen.c","helium.c","hyrectools.c")],"-lm"]
        report["common_build"]=run_capture_u6(shared+["-o",str(ev/"libu8_source.so")],src,
            ev/"common_build_stdout.txt",ev/"common_build_stderr.txt",30,os.environ.copy())
        if report["common_build"]["returncode"]:raise RuntimeError("U8_COMMON_C_BUILD_FAILED")
        report["native_binary_sha256"]=sha256(ev/"native_u8_oracle")
        report["common_binary_sha256"]=sha256(ev/"libu8_source.so")
        report["native_run"]=run_capture_u6([str(ev/"native_u8_oracle"),str(args.max_extra_accepted)],src,
            ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",60,os.environ.copy())
        if report["native_run"]["returncode"]:raise RuntimeError("U8_NATIVE_C_REPLAY_FAILED")
        native=parse_native(ev/"native_oracle_stdout.csv",args.max_extra_accepted)
        report["native_c_stdout_sha256"]=sha256(ev/"native_oracle_stdout.csv")
        start=native["node"]
        if (abs(start[2]-float(cp["z"][-1]))>2e-12 or
            abs(start[3]-float(cp["xe"][-1]))/max(abs(start[3]),1e-8)>5e-9 or
            abs(start[4]-float(cp["Tm_K"][-1]))/max(abs(start[4]),1.)>5e-10):
            raise ArithmeticError("U8_C_PY_START_STATE")
        for label,pv,cv in (("hprev",boundary["hydrogen_prev"],start[5]),
                            ("hprev2",boundary["hydrogen_prev2"],start[6]),
                            ("tprev",boundary["thermal_prev"],start[7]),
                            ("tprev2",boundary["thermal_prev2"],start[8])):
            if abs(pv-cv)/max(1.,abs(cv))>2e-8:raise ArithmeticError(f"U8_START_MEMORY:{label}")
        oracle=CommonOracle(ev/"libu8_source.so",c)
        result=continue_low_z_to_end(cp,boundary,c,source,common_input_oracle=oracle,
            checkpoint_callback=lambda payload:save_checkpoint(ev,payload),
            max_extra_accepted=args.max_extra_accepted)
        n=result["accepted_extra"]
        if n!=native["end"][2] or result["status"]!=native["end"][0]:
            raise ArithmeticError("U8_C_PY_END_STATUS_OR_COUNT")
        if ((result["event"] is None)!=(native["event"] is None) or
            result["event"] is not None and any(result["event"][key]!=native["event"][key]
                for key in ("j","global_iz","reason"))):
            raise ArithmeticError("U8_C_PY_STAGE_EVENT")
        maxima={k:0. for k in ("xe","xHII","xH1s","Tm_K","H_rhs","T_rhs",
                                "H_memory","T_memory","H_recurrence","T_recurrence")}
        for k,crow in enumerate(native["rows"]):
            j=START_J+k;model=result["models"][k]
            if native["models"][k]!=model or int(crow[1])!=j+SOURCE_IZH0:
                raise ArithmeticError(f"U8_C_PY_MODEL_OR_CLOCK:{j}")
            zin=float(result["nodes"]["z"][j]);xin=float(result["nodes"]["xe"][j]);tin=float(result["nodes"]["Tm_K"][j])
            if (abs(zin-crow[2])>2e-12 or abs(xin-crow[3])/max(abs(crow[3]),1e-8)>5e-9 or
                    abs(tin-crow[4])/max(abs(crow[4]),1.)>5e-10):
                raise ArithmeticError(f"U8_C_PY_INPUT_STATE:{j}")
            guard,reason=source_emla_table_guard(c,zin,tin)
            if (model=="EMLA2s2p" and not guard) or (model=="PEEBLES" and
                    result["event"] is not None and j==result["event"]["j"] and guard):
                raise ArithmeticError(f"U8_PY_STAGE_GUARD:{j}")
            pyrow={"iz":int(result["nodes"]["global_iz"][j+1]),
                   "z":float(result["nodes"]["z"][j+1]),
                   "xH1s":float(result["nodes"]["xH1s"][j+1]),
                   "xHII":float(result["nodes"]["xHII"][j+1]),
                   "xHeII":0.,"xe":float(result["nodes"]["xe"][j+1]),
                   "Tm_K":float(result["nodes"]["Tm_K"][j+1]),"post_saha":False}
            cref={"iz":int(crow[13]),"z":crow[14],"xH1s":1-crow[15],
                  "xHII":crow[15],"xHeII":0.,"xe":crow[15],"Tm_K":crow[16],"post_saha":False}
            errs=compare_state(pyrow,cref,j)
            for key in ("xe","xHII","xH1s","Tm_K"):maxima[key]=max(maxima[key],errs[key])
            for label,pv,cv,lim in (("H_rhs",result["hydrogen_rhs_dln_a"][j],crow[5],2e-7),
                ("T_rhs",result["thermal_rhs_dln_a"][j],crow[6],2e-8),
                ("H_memory",result["hydrogen_rhs_dln_a"][j-1],crow[7],2e-8),
                ("H_memory",result["hydrogen_rhs_dln_a"][j-2],crow[8],2e-8),
                ("T_memory",result["thermal_rhs_dln_a"][j-1],crow[9],2e-8),
                ("T_memory",result["thermal_rhs_dln_a"][j-2],crow[10],2e-8)):
                d=abs(float(pv)-float(cv))/max(1.,abs(float(cv)))
                if not math.isfinite(d) or d>lim:raise ArithmeticError(f"U8_C_PY_RHS_OR_MEMORY:{j}:{label}:{d}")
                maxima[label]=max(maxima[label],d)
            for label,old,deriv,old2,new,cold,cderiv,cold2,cnew in (
                ("H_recurrence",xin,float(result["hydrogen_rhs_dln_a"][j]),
                 float(result["hydrogen_rhs_dln_a"][j-2]),pyrow["xe"],crow[3],crow[5],crow[8],crow[15]),
                ("T_recurrence",tin,float(result["thermal_rhs_dln_a"][j]),
                 float(result["thermal_rhs_dln_a"][j-2]),pyrow["Tm_K"],crow[4],crow[6],crow[10],crow[16])):
                pred=old+SOURCE_DLNA*(1.25*deriv-.25*old2)
                cpred=cold+SOURCE_DLNA*(1.25*cderiv-.25*cold2)
                if pred!=new or cpred!=cnew:raise ArithmeticError(f"U8_SOURCE_RECURRENCE:{j}:{label}")
        if oracle.h_calls!=len(result["common_sample_globals"]) or oracle.t_calls!=len(result["common_sample_globals"]):
            raise ArithmeticError("U8_COMMON_SAMPLE_CALL_ACCOUNTING")
        if n==EXTRA_ACCEPTED:
            if (int(result["nodes"]["global_iz"][-1])!=END_GLOBAL_IZ or
                    result["attempted_evaluations"]!=EXTRA_ACCEPTED or result["event"] is None):
                raise ArithmeticError("U8_SOURCE_END_OR_EVENT")
            assembled=assemble_full_source_grid(args.u1_rows,args.u1_verification,result["nodes"])
            with (ev/"independent_source_grid.npz").open("xb") as out:np.savez_compressed(out,**assembled)
            errors={"xe":0.,"Tm_K":0.,"Tm_Tr_ratio":0.}
            with (ev/"independent_integer_z_history.csv").open("x") as out:
                out.write("z,xe,Tm_K,Tm_Tr_ratio\n")
                for i,crow in enumerate(native["outputs"]):
                    z=8000-i
                    px=source_interp1d(assembled["xe"],float(z))["value"]
                    pt=source_interp1d(assembled["Tm_K"],float(z))["value"]
                    pr=pt/c.T0_K/(1+z)
                    out.write(f"{z},{px:.17g},{pt:.17g},{pr:.17g}\n")
                    for key,pv,cv,lim,den in (("xe",px,crow[1],5e-9,max(abs(crow[1]),1e-8)),
                        ("Tm_K",pt,crow[2],5e-10,max(abs(crow[2]),1.)),
                        ("Tm_Tr_ratio",pr,crow[3],5e-10,max(abs(crow[3]),1e-8))):
                        d=abs(pv-cv)/den
                        if not math.isfinite(d) or d>lim:raise ArithmeticError(f"U8_8001_OUTPUT:{z}:{key}:{d}")
                        errors[key]=max(errors[key],d)
            with (ev/"native_baseline_stdout.txt").open("x") as out:out.write(native["baseline"])
            report["native_baseline_stdout_sha256"]=sha256(ev/"native_baseline_stdout.txt")
            report["regenerated_baseline_byte_status"]=regenerated_baseline_byte_status(
                report["native_baseline_stdout_sha256"])
            with gzip.open(BASELINE_GZIP,"rb") as stream:
                import hashlib
                h=hashlib.sha256()
                for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
            if h.hexdigest()!=BASELINE_STDOUT_SHA256:raise ValueError("U8_BASELINE_DECOMPRESS_SHA")
            for iz,(cx,ct) in native["production_nodes"].items():
                j=iz-SOURCE_IZH0
                px=float(result["nodes"]["xe"][j]);pt=float(result["nodes"]["Tm_K"][j])
                if abs(px-cx)/max(abs(cx),1e-8)>5e-9 or abs(pt-ct)/max(abs(ct),1.)>5e-10:
                    raise ArithmeticError(f"U8_C_PRODUCTION_NODE:{iz}")
            report["integer_z_8001_max_relative"]=errors
            report["z0"]={"python_xe":result["z0"]["xe"]["value"],
                          "python_Tm_K":result["z0"]["Tm_K"]["value"],
                          "c_xe":float(native["outputs"][-1,1]),
                          "c_Tm_K":float(native["outputs"][-1,2]),
                          "source_clamped_fraction":result["z0"]["xe"]["fraction"]}
            report["independent_source_grid_sha256"]=sha256(ev/"independent_source_grid.npz")
            report["independent_integer_z_history_sha256"]=sha256(ev/"independent_integer_z_history.csv")
        report.update({"status":result["status"],"accepted_extra":n,
          "attempted_evaluations":result["attempted_evaluations"],"emla_updates":result["models"].count("EMLA2s2p"),
          "peebles_updates":result["models"].count("PEEBLES"),"event":result["event"],
          "stop_failure":result["failure"],"end_global_iz":int(result["nodes"]["global_iz"][-1]),
          "end_z":float(result["nodes"]["z"][-1]),"maxima":maxima,
          "common_input_max":result["common_max"],
          "common_sample_globals":result["common_sample_globals"],
          "common_h_calls":oracle.h_calls,"common_thermal_calls":oracle.t_calls,
          "checkpoint_count":len(list(ev.glob("checkpoint_*.npz"))),
          "claim_ceiling":"q=0 original HyRec source-clock H+Tm to z0; U5 spectra and temporal refinement remain HOLD; REI disabled"})
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
    return 0 if report["status"] in {"PREFLIGHT_ONLY","STOP_AT_SOURCE_Z0_CUBIC_STENCIL",
      "BOUNDED_LOW_Z_INTERVAL_COMPLETE_BEFORE_SOURCE_END"} else 1


if __name__=="__main__":raise SystemExit(main())

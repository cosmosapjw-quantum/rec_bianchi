#!/usr/bin/env python3
"""Bounded U5 original HyRec thermal-switch C/Python parity verifier."""
from __future__ import annotations
import argparse
import ctypes
import json
import math
import os
import re
import resource
import signal
import sys
import traceback
from pathlib import Path

os.environ.update({"OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1","MKL_NUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1"})
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import (
    START_J,MAX_EXTRA_ACCEPTED,U4_STOP_NPZ_SHA256,U4_STOP_JSON_SHA256,
    U4_VERIFICATION_SHA256,sha256,load_reviewed_u4_stop,continue_thermal_transition,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from verify_r3g_continuation import safe_source,zip_member_hashes,PINNED_ZIP_SHA,PINNED_SOURCE,run_capture,compare_state,compare_spectra,load_u2_verifier
from verify_r3g_hydrogen_transition import save_checkpoint

BASE_REVISION="9a2ca205b981abee004844826596c27d443776b5"
U5_FILES=(
 "src/full_bianchi_hyrec/trajectory/primordial_2012_thermal_transition.py",
 "scripts/verify_r3g_thermal_transition.py",
 "scripts/c_harness/original_hyrec_thermal_transition_harness.c",
 "tests/trajectory/test_primordial_2012_thermal_transition.py",
)

def parse_native(path:Path):
    node=event=end=None; steps={}; spectra={"V":{},"A":{},"L":{}}
    def finite(token,kind):
        v=float(token)
        if not math.isfinite(v): raise ValueError(f"C_NONFINITE:{kind}")
        return v
    with path.open() as stream:
        for line_no,line in enumerate(stream,1):
            f=line.rstrip("\n").split(","); tag=f[0]
            if tag=="U5NODE":
                if node is not None or len(f)!=9: raise ValueError("C_U5_NODE_GRAMMAR")
                node={"iz":int(f[1]),"z":finite(f[2],"node.z"),"xH1s":finite(f[3],"node.xH1s"),
                      "xHII":finite(f[4],"node.xHII"),"xHeII":finite(f[5],"node.xHeII"),
                      "xe":finite(f[6],"node.xe"),"Tm_K":finite(f[7],"node.Tm_K"),
                      "post_saha":int(f[8])}
            elif tag=="U5EVENT":
                if event is not None or len(f)!=5: raise ValueError("C_U5_EVENT_GRAMMAR")
                event={"j":int(f[1]),"delta":finite(f[2],"event.delta"),
                       "prev2":finite(f[3],"event.prev2"),"prev":finite(f[4],"event.prev")}
            elif tag=="U5STEP":
                if len(f)!=14: raise ValueError(f"C_U5_STEP_GRAMMAR:{line_no}:{len(f)}")
                j=int(f[1]);
                if j in steps: raise ValueError("C_U5_DUPLICATE_STEP")
                trhs=float(f[8])
                if f[9]=="1": trhs=finite(f[8],"step.thermal_rhs")
                elif f[9]!="0" or not math.isnan(trhs): raise ValueError("C_U5_THERMAL_BRANCH_GRAMMAR")
                if f[9]=="0" and not (math.isnan(float(f[12])) and math.isnan(float(f[13]))):
                    raise ValueError("C_U5_STEADY_MEMORY_GRAMMAR")
                steps[j]={"j":j,"iz":int(f[2]),"z":finite(f[3],"step.z"),
                          "xH1s":finite(f[4],"step.xH1s"),"xHII":finite(f[5],"step.xe"),
                          "xHeII":0.,"xe":finite(f[5],"step.xe"),"Tm_K":finite(f[6],"step.Tm_K"),
                          "hydrogen_rhs":finite(f[7],"step.hydrogen_rhs"),
                          "thermal_rhs":trhs,"coupled":f[9]=="1","post_saha":False,
                          "h_prev":finite(f[10],"step.h_prev"),"h_prev2":finite(f[11],"step.h_prev2"),
                          "t_prev":finite(f[12],"step.t_prev") if f[9]=="1" else float("nan"),
                          "t_prev2":finite(f[13],"step.t_prev2") if f[9]=="1" else float("nan")}
            elif tag in spectra:
                if len(f)!=4: raise ValueError("C_SPECTRUM_GRAMMAR")
                j=int(f[1]); b=int(f[2]); v=finite(f[3],f"{tag}.spectrum")
                if j>=START_J:
                    if b in spectra[tag].get(j,{}): raise ValueError("C_DUPLICATE_SPECTRUM_BIN")
                    spectra[tag].setdefault(j,{})[b]=v
            elif tag=="U5END":
                if end is not None or len(f)!=5: raise ValueError("C_U5_END_GRAMMAR")
                end=(f[1],int(f[2]),int(f[3]),int(f[4]))
            elif tag in {"META","NODE","STEP","U4NODE","U4STEP","U4END","END"}:
                continue
            else: raise ValueError(f"C_UNKNOWN_RECORD:{line_no}:{tag}")
    if node is None or end is None: raise ValueError("C_U5_MISSING_RECORD")
    if node["iz"]!=19227 or node["post_saha"]!=0 or node["xHeII"]!=0.:
        raise ValueError("C_U5_SOURCE_START_MISMATCH")
    if sorted(steps)!=list(range(START_J,START_J+len(steps))):
        raise ValueError("C_U5_STEP_INDEX_SEQUENCE")
    for j in steps:
        for tag,n in (("V",311),("A",311),("L",3)):
            if set(spectra[tag].get(j,{}))!=set(range(n)):
                raise ValueError(f"C_U5_SPECTRUM_INCOMPLETE:{j}:{tag}")
    if end[3]!=len(steps): raise ValueError("C_U5_END_COUNT")
    if end[0]=="THERMAL_EVENT_TWO_STEPS_COMPLETE":
        if event is None or end[1]!=event["j"] or end[2]!=2:
            raise ValueError("C_U5_FALSE_EVENT_SUCCESS")
    elif event is not None and end[0]=="BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED":
        raise ValueError("C_U5_FALSE_BOUNDED_SUCCESS")
    return node,event,steps,spectra,end

class CombinedOracle:
    def __init__(self,h_oracle,thermal_lib:Path,c:HyRec2012Cosmology):
        self.h=h_oracle; self.c=c
        fn=ctypes.CDLL(str(thermal_lib)).rec_dTmdlna
        fn.argtypes=[ctypes.c_double]*7; fn.restype=ctypes.c_double
        self.tfn=fn
    def __call__(self,*args): return self.h(*args)
    def thermal_rhs(self,xe,tm,z):
        return self.tfn(xe,tm,self.c.T0_K*(1.+z),self.c.hubble_s(z),
                        self.c.fHe,self.c.fsR,self.c.meR)

def validate_manifest(path:Path):
    m=json.loads(path.read_text())
    if m.get("controller_verified") is not True or m.get("base_revision")!=BASE_REVISION:
        raise ValueError("EXECUTION_MANIFEST_BASE_OR_CONTROLLER_MISMATCH")
    if m.get("source_zip_sha256")!=PINNED_ZIP_SHA:
        raise ValueError("EXECUTION_MANIFEST_SOURCE_MISMATCH")
    for key,want in (("u4_stop_npz_sha256",U4_STOP_NPZ_SHA256),
                     ("u4_stop_json_sha256",U4_STOP_JSON_SHA256),
                     ("u4_verification_sha256",U4_VERIFICATION_SHA256)):
        if m.get(key)!=want: raise ValueError(f"EXECUTION_MANIFEST_CHECKPOINT_MISMATCH:{key}")
    if m.get("u5_files_sha256")!={k:sha256(ROOT/k) for k in U5_FILES}:
        raise ValueError("EXECUTION_MANIFEST_U5_CODE_MISMATCH")
    if not re.fullmatch(r"[0-9a-f]{40}",m.get("execution_revision","")):
        raise ValueError("EXECUTION_MANIFEST_REVISION_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}",m.get("capsule_manifest_sha256","")):
        raise ValueError("EXECUTION_MANIFEST_CAPSULE_INVALID")
    return m

def main():
    p=argparse.ArgumentParser(); m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--preflight",action="store_true"); m.add_argument("--execute",action="store_true")
    p.add_argument("--evidence-dir",type=Path,required=True)
    p.add_argument("--u4-stop-npz",type=Path,required=True)
    p.add_argument("--u4-stop-json",type=Path,required=True)
    p.add_argument("--u4-verification",type=Path,required=True)
    p.add_argument("--execution-manifest",type=Path)
    p.add_argument("--source-dir",type=Path)
    p.add_argument("--max-extra-accepted",type=int,default=MAX_EXTRA_ACCEPTED)
    a=p.parse_args()
    if not 1<=a.max_extra_accepted<=MAX_EXTRA_ACCEPTED: raise SystemExit("INVALID_EXTRA_ACCEPTED_CAP")
    if a.execute and a.execution_manifest is None: raise SystemExit("EXECUTION_MANIFEST_REQUIRED")
    ev=a.evidence_dir.resolve(); ev.mkdir(parents=True,exist_ok=False)
    report={"status":"INCOMPLETE","first_failure":None,"limits":{"extra_accepted_max":8192,
      "full_evaluations_max":8320,"common_input_max":64,"address_space_bytes":2*1024**3,
      "cpu_s":540,"wall_s":600,"native_oracle_s":60,"build_s":30}}
    try:
        checkpoint=load_reviewed_u4_stop(a.u4_stop_npz,a.u4_stop_json,a.u4_verification)
        report["start"]={"j":START_J,"iz":int(checkpoint["global_iz"][-1]),
           "z":float(checkpoint["z"][-1]),"xe":float(checkpoint["xe"][-1]),
           "Tm_K":float(checkpoint["Tm_K"][-1]),"post_saha":bool(checkpoint["post_saha"][-1]),
           "accepted_photon_columns":int(checkpoint["virtual_out"].shape[1])}
        if a.preflight:
            report["status"]="PREFLIGHT_ONLY"; return 0
        validate_manifest(a.execution_manifest)
        report["execution_manifest_sha256"]=sha256(a.execution_manifest)
        with (ev/"controller_execution_manifest.json").open("xb") as out:
            out.write(a.execution_manifest.read_bytes())
        src=safe_source(a.source_dir,ev)
        report["source_zip_sha256"]=PINNED_ZIP_SHA
        report["source_sha256"]={k:sha256(src/k) for k in PINNED_SOURCE}
        with (ev/"source_manifest.json").open("x") as out:
            json.dump({"source_zip_sha256":PINNED_ZIP_SHA,"source_members":zip_member_hashes(),
                "source_c":report["source_sha256"],"u4_checkpoint":U4_STOP_NPZ_SHA256,
                "u5_files_sha256":{k:sha256(ROOT/k) for k in U5_FILES}},out,sort_keys=True,indent=2)
            out.write("\n")
        os.chdir(src)
        affinity=sorted(os.sched_getaffinity(0)); os.sched_setaffinity(0,{affinity[0]})
        report["affinity"]=[affinity[0]]
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(540,540))
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("U5_WALL_LIMIT_600S")))
        signal.alarm(600)
        c=HyRec2012Cosmology()
        table=OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        source=make_hmla_source(c,table)
        common_cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-I",str(src),
          str(ROOT/"scripts/c_harness/original_hyrec_full_source_harness.c"),
          str(src/"hydrogen.c"),str(src/"hyrectools.c"),"-lm","-o",str(ev/"liboriginal_full_source.so")]
        report["common_build"]=run_capture(common_cc,src,ev/"common_build_stdout.txt",ev/"common_build_stderr.txt",30,os.environ.copy())
        if report["common_build"]["returncode"]: raise RuntimeError("COMMON_C_BUILD_FAILED")
        t_cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-I",str(src),
          str(src/"history.c"),str(src/"hydrogen.c"),str(src/"helium.c"),str(src/"hyrectools.c"),
          "-lm","-o",str(ev/"liboriginal_history.so")]
        report["thermal_build"]=run_capture(t_cc,src,ev/"thermal_build_stdout.txt",ev/"thermal_build_stderr.txt",30,os.environ.copy())
        if report["thermal_build"]["returncode"]: raise RuntimeError("THERMAL_C_BUILD_FAILED")
        native_cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(src),
          str(ROOT/"scripts/c_harness/original_hyrec_thermal_transition_harness.c"),
          str(src/"history.c"),str(src/"hydrogen.c"),str(src/"helium.c"),str(src/"hyrectools.c"),
          "-lm","-o",str(ev/"native_u5_oracle")]
        report["native_build"]=run_capture(native_cc,src,ev/"native_build_stdout.txt",ev/"native_build_stderr.txt",30,os.environ.copy())
        if report["native_build"]["returncode"]: raise RuntimeError("NATIVE_C_BUILD_FAILED")
        report["native_binary_sha256"]=sha256(ev/"native_u5_oracle")
        report["native_run"]=run_capture([str(ev/"native_u5_oracle"),str(a.max_extra_accepted)],
          src,ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",60,os.environ.copy())
        if report["native_run"]["returncode"]: raise RuntimeError("NATIVE_C_U5_ORACLE_FAILED")
        node,event,steps,spectra,cend=parse_native(ev/"native_oracle_stdout.csv")
        report["native_c_stdout_sha256"]=sha256(ev/"native_oracle_stdout.csv")
        compare_state({"iz":int(checkpoint["global_iz"][-1]),"z":float(checkpoint["z"][-1]),
          "xH1s":float(checkpoint["xH1s"][-1]),"xHII":float(checkpoint["xHII"][-1]),
          "xHeII":float(checkpoint["xHeII"][-1]),"xe":float(checkpoint["xe"][-1]),
          "Tm_K":float(checkpoint["Tm_K"][-1]),"post_saha":False},node,START_J)
        horacle=load_u2_verifier().FullSourceCOracle(ev/"liboriginal_full_source.so",src,c)
        oracle=CombinedOracle(horacle,ev/"liboriginal_history.so",c)
        result=continue_thermal_transition(checkpoint,c,source,common_input_oracle=oracle,
             max_extra_accepted=a.max_extra_accepted,checkpoint_callback=lambda x:save_checkpoint(ev,x))
        state_max={k:0. for k in ("xH1s","xHII","xe","xHeII","Tm_K")}
        rhs_max=0.; thermal_max=0.; spectra_max={"virtual":0.,"average":0.,"lyman":0.}
        twog=load_u2_verifier()._canonical_twophoton_table(table.archive_path)
        rows=[]
        for j in range(START_J,START_J+result["accepted_extra"]):
            crow=steps.get(j)
            if crow is None: raise ArithmeticError(f"C_MISSING_STEP:j={j}")
            n=j+1; py={k:(bool(result["nodes"][k][n]) if k=="post_saha" else
                 int(result["nodes"][k][n]) if k=="global_iz" else float(result["nodes"][k][n]))
                 for k in ("global_iz","z","xH1s","xHII","xHeII","xe","Tm_K","post_saha")}
            py["iz"]=py.pop("global_iz")
            err=compare_state(py,crow,j)
            for k,v in err.items(): state_max[k]=max(state_max[k],v)
            if crow["coupled"]!=(result["event_j"] is not None and j>=result["event_j"]):
                raise ArithmeticError(f"C_PY_THERMAL_BRANCH_PARITY:j={j}")
            hr=abs(float(result["hydrogen_rhs_dln_a"][j])-crow["hydrogen_rhs"])/max(1.,abs(crow["hydrogen_rhs"]))
            if not math.isfinite(hr) or hr>2e-7: raise ArithmeticError(f"INTEGRATED_H_RHS_PARITY:j={j}:scaled={hr}")
            rhs_max=max(rhs_max,hr)
            if abs(float(result["hydrogen_rhs_dln_a"][j])-crow["h_prev"])/max(1.,abs(crow["h_prev"]))>2e-8:
                raise ArithmeticError(f"H_MEMORY_PREV_PARITY:j={j}")
            hprev2=float(result["hydrogen_rhs_dln_a"][j-1])
            if abs(hprev2-crow["h_prev2"])/max(1.,abs(crow["h_prev2"]))>2e-8:
                raise ArithmeticError(f"H_MEMORY_PREV2_PARITY:j={j}")
            if crow["coupled"]:
                trr=abs(float(result["thermal_rhs_dln_a"][j])-crow["thermal_rhs"])/max(1.,abs(crow["thermal_rhs"]))
                if not math.isfinite(trr) or trr>2e-8: raise ArithmeticError(f"INTEGRATED_T_RHS_PARITY:j={j}:scaled={trr}")
                thermal_max=max(thermal_max,trr)
                for name,field in (("thermal_prev_after","t_prev"),("thermal_prev2_after","t_prev2")):
                    v=abs(float(result[name][j])-crow[field])/max(1.,abs(crow[field]))
                    if not math.isfinite(v) or v>2e-8:
                        raise ArithmeticError(f"T_MEMORY_PARITY:j={j}:field={field}:scaled={v}")
            elif not math.isnan(float(result["thermal_rhs_dln_a"][j])):
                raise ArithmeticError(f"UNEXPECTED_THERMAL_RHS:j={j}")
            tr_ev=8.617343e-5*c.T0_K*(1.+float(result["nodes"]["z"][j]))
            fbbv=1./np.expm1(twog.energy_eV/tr_ev)
            fbbl=1./np.expm1(np.array((10.198714553953742,12.087365397278509,12.748393192442178))/tr_ev)
            for name,arr,tag,bb,numbins in (("virtual",result["virtual_out"][:,j],"V",fbbv,311),
                   ("average",result["average_virtual"][:,j],"A",fbbv,311),
                   ("lyman",result["lyman_out"][:,j],"L",fbbl,3)):
                ref=np.array([spectra[tag][j][b] for b in range(numbins)])
                spectra_max[name]=max(spectra_max[name],compare_spectra(arr,ref,bb,j,name))
            rows.append(py)
        if len(steps)!=result["accepted_extra"] or cend[0]!=result["status"] or cend[2]!=result["branch_steps_after_event"]:
            raise ArithmeticError("C_PY_END_STATUS_OR_COUNT_PARITY")
        if (event is None)!=(result["thermal_seeds"] is None): raise ArithmeticError("C_PY_EVENT_PRESENCE_PARITY")
        if event is not None:
            if event["j"]!=result["event_j"] or cend[1]!=event["j"]:
                raise ArithmeticError("C_PY_EVENT_INDEX_PARITY")
            for k in ("delta","prev2","prev"):
                v=abs(float(result["thermal_seeds"][k])-event[k])/max(1.,abs(event[k]))
                if not math.isfinite(v) or v>2e-8: raise ArithmeticError(f"C_PY_THERMAL_SEED_PARITY:{k}:{v}")
        with (ev/"python_accepted_rows.jsonl").open("x") as out:
            for row in rows: out.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n")
        report.update({"status":result["status"],"accepted_extra":result["accepted_extra"],
          "python_full_evaluations":result["full_evaluations"],"event_j":result["event_j"],
          "branch_steps_after_event":result["branch_steps_after_event"],
          "native_c_event":event,"native_c_end":cend,"thermal_seeds":result["thermal_seeds"],
          "state_max_scaled":state_max,"hydrogen_rhs_max_scaled":rhs_max,"thermal_rhs_max_scaled":thermal_max,
          "spectrum_max_tolerance_ratio":spectra_max,"common_input_sample_j":result["samples"],
          "common_input_max":result["common_max"],"python_rows_sha256":sha256(ev/"python_accepted_rows.jsonl"),
          "checkpoint_count":len(list(ev.glob("checkpoint_*.npz"))),
          "claim_ceiling":"bounded q=0 original HyRec H-only thermal transition; no full primordial Python history or Bianchi/CMB claim"})
    except BaseException as exc:
        report["status"]=str(exc) if str(exc).startswith("HOLD_NEXT_STAGE_REQUIRED") else "FAIL"
        report["first_failure"]={"type":type(exc).__name__,"message":str(exc),"traceback":traceback.format_exc()}
    finally:
        report["resource"]={"self_user_cpu_s":resource.getrusage(resource.RUSAGE_SELF).ru_utime,
          "self_system_cpu_s":resource.getrusage(resource.RUSAGE_SELF).ru_stime,
          "self_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          "child_user_cpu_s":resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime,
          "child_system_cpu_s":resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime}
        with (ev/"verification.json").open("x") as out: json.dump(report,out,sort_keys=True,indent=2); out.write("\n")
        print(json.dumps(report,sort_keys=True))
    return 0 if report["status"] in {"PREFLIGHT_ONLY","THERMAL_EVENT_TWO_STEPS_COMPLETE"} else 1
if __name__=="__main__": raise SystemExit(main())

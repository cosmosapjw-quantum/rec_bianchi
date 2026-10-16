#!/usr/bin/env python3
"""Verify bounded U4 independent H-only post-Saha transition against HyRec C."""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import resource
import signal
import sys
import time
import traceback
from pathlib import Path

os.environ.update({"OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1",
                   "MKL_NUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1"})
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_BASE_REVISION="7a85032a32bd2d593b9622331c85c6da1b1e179d"
U4_FILES=(
    "src/full_bianchi_hyrec/trajectory/primordial_2012_hydrogen_transition.py",
    "scripts/verify_r3g_hydrogen_transition.py",
    "scripts/c_harness/original_hyrec_hydrogen_transition_harness.c",
    "tests/trajectory/test_primordial_2012_hydrogen_transition.py",
)
sys.path.insert(0,str(ROOT/"src"))
from full_bianchi_hyrec.trajectory.primordial_2012_hydrogen_transition import (
    START_J, MAX_EXTRA_ACCEPTED, U3_STOP_NPZ_SHA256, U3_STOP_JSON_SHA256,
    U3_VERIFICATION_SHA256, sha256, load_reviewed_u3_stop, continue_hydrogen_steady,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from verify_r3g_continuation import (
    safe_source, zip_member_hashes, PINNED_ZIP_SHA, PINNED_SOURCE,
    run_capture, compare_state, compare_spectra, load_u2_verifier,
)


def parse_native(path: Path):
    def finite(token: str, field: str) -> float:
        value=float(token)
        if not math.isfinite(value): raise ValueError(f"C_NONFINITE:{field}")
        return value
    def flag(token: str, field: str) -> bool:
        if token not in {"0","1"}: raise ValueError(f"C_NONBOOLEAN_FLAG:{field}")
        return token=="1"
    meta=node=end=None; steps={}; v={}; a={}; l={}
    with path.open() as stream:
        for lineno,line in enumerate(stream,1):
            f=line.rstrip("\n").split(","); tag=f[0]
            if tag=="META":
                if meta is not None or len(f)!=4: raise ValueError("C_META_GRAMMAR")
                meta={"izH0":int(f[1]),"nzrt":int(f[2]),"zH0":finite(f[3],"zH0")}
            elif tag=="U4NODE":
                if node is not None or len(f)!=9: raise ValueError("C_U4_NODE_GRAMMAR")
                node={"iz":int(f[1]),"z":finite(f[2],"node.z"),"xH1s":finite(f[3],"node.xH1s"),
                      "xHII":finite(f[4],"node.xHII"),"xHeII":finite(f[5],"node.xHeII"),
                      "xe":finite(f[6],"node.xe"),"Tm_K":finite(f[7],"node.Tm_K"),
                      "post_saha":flag(f[8],"node.post_saha")}
            elif tag=="U4STEP":
                if len(f)!=11: raise ValueError(f"C_U4_STEP_GRAMMAR:{lineno}:{len(f)}")
                j=int(f[1]);
                if j in steps: raise ValueError("C_U4_DUPLICATE_STEP")
                steps[j]={"j":j,"iz":int(f[2]),"z":finite(f[3],"step.z"),
                    "xH1s":finite(f[4],"step.xH1s"),"xHII":finite(f[5],"step.xHII"),
                    "xHeII":0.,"xe":finite(f[6],"step.xe"),
                    "Tm_K":finite(f[7],"step.Tm_K"),"hydrogen_rhs":finite(f[8],"step.hydrogen_rhs"),
                    "post_saha":flag(f[9],"step.post_saha"),
                    "post_saha_crossed":flag(f[10],"step.post_saha_crossed")}
            elif tag in {"V","A","L"}:
                if len(f)!=4: raise ValueError("C_SPECTRUM_GRAMMAR")
                j=int(f[1]); b=int(f[2]); val=finite(f[3],f"{tag}.spectrum")
                if j>=START_J:
                    target={"V":v,"A":a,"L":l}[tag]
                    if b in target.get(j,{}): raise ValueError("C_DUPLICATE_SPECTRUM_BIN")
                    target.setdefault(j,{})[b]=val
            elif tag=="U4END":
                if end is not None or len(f)!=5: raise ValueError("C_U4_END_GRAMMAR")
                end=(f[1],int(f[2]),int(f[3]),int(f[4]))
            elif tag in {"NODE","STEP"}:
                continue  # upstream native C replay; never a Python input
            else:
                raise ValueError(f"C_UNKNOWN_RECORD:{lineno}:{tag}")
    if meta is None or node is None or end is None: raise ValueError("C_U4_MISSING_RECORD")
    if meta["izH0"]!=18223 or meta["nzrt"]!=10972 or node["iz"]!=18605:
        raise ValueError("C_U4_SOURCE_STAGE_IDENTITY")
    if not math.isclose(meta["zH0"],1702.072263548342,rel_tol=0.,abs_tol=1e-12):
        raise ValueError("C_U4_ZH0_MISMATCH")
    if sorted(steps)!=list(range(START_J,START_J+len(steps))):
        raise ValueError("C_U4_STEP_INDEX_SEQUENCE")
    for j in steps:
        if steps[j]["iz"]!=18223+j+1: raise ValueError("C_U4_SOURCE_GRID")
        for m,n in ((v,311),(a,311),(l,3)):
            if set(m.get(j,{}))!=set(range(n)): raise ValueError(f"C_U4_SPECTRUM_INCOMPLETE:{j}")
    if end[3]!=len(steps) or end[1] not in (0,1) or end[2] not in (0,1,2):
        raise ValueError("C_U4_END_COUNT_OR_FLAGS")
    if end[0]=="EVENT_TWO_STEPS_COMPLETE" and (end[1],end[2])!=(1,2):
        raise ValueError("C_U4_FALSE_EVENT_SUCCESS")
    if end[0]=="BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED" and (end[1],end[2])!=(0,0):
        raise ValueError("C_U4_FALSE_BOUNDED_SUCCESS")
    return meta,node,steps,v,a,l,end


def save_checkpoint(evidence: Path, payload: dict):
    index=len(list(evidence.glob("checkpoint_*.json")))
    phase=str(payload["phase"]).lower(); stem=f"checkpoint_{index:04d}_{phase}"
    arrays={k:v for k,v in payload.items() if isinstance(v,np.ndarray)}
    other={k:v for k,v in payload.items() if not isinstance(v,np.ndarray)}
    with (evidence/(stem+".npz")).open("xb") as out: np.savez_compressed(out,**arrays)
    other["npz_sha256"]=sha256(evidence/(stem+".npz"))
    with (evidence/(stem+".json")).open("x") as out:
        json.dump(other,out,sort_keys=True,indent=2); out.write("\n")


def validate_execution_manifest(path: Path) -> dict:
    record=json.loads(Path(path).read_text())
    if record.get("controller_verified") is not True:
        raise ValueError("EXECUTION_MANIFEST_NOT_CONTROLLER_VERIFIED")
    if record.get("base_revision")!=EXPECTED_BASE_REVISION:
        raise ValueError("EXECUTION_MANIFEST_BASE_REVISION_MISMATCH")
    if record.get("source_zip_sha256")!=PINNED_ZIP_SHA:
        raise ValueError("EXECUTION_MANIFEST_SOURCE_ZIP_MISMATCH")
    if record.get("u3_stop_npz_sha256")!=U3_STOP_NPZ_SHA256 or \
            record.get("u3_stop_json_sha256")!=U3_STOP_JSON_SHA256 or \
            record.get("u3_verification_sha256")!=U3_VERIFICATION_SHA256:
        raise ValueError("EXECUTION_MANIFEST_U3_CHECKPOINT_MISMATCH")
    revision=record.get("execution_revision","")
    capsule=record.get("capsule_manifest_sha256","")
    if not re.fullmatch(r"[0-9a-f]{40}",revision) or revision==EXPECTED_BASE_REVISION:
        raise ValueError("EXECUTION_MANIFEST_REVISION_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}",capsule):
        raise ValueError("EXECUTION_MANIFEST_CAPSULE_INVALID")
    actual={k:sha256(ROOT/k) for k in U4_FILES}
    if record.get("u4_files_sha256")!=actual:
        raise ValueError("EXECUTION_MANIFEST_U4_CODE_MISMATCH")
    return record


def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight",action="store_true")
    mode.add_argument("--execute",action="store_true")
    ap.add_argument("--evidence-dir",type=Path,required=True)
    ap.add_argument("--u3-stop-npz",type=Path,required=True)
    ap.add_argument("--u3-stop-json",type=Path,required=True)
    ap.add_argument("--u3-verification",type=Path,required=True)
    ap.add_argument("--execution-manifest",type=Path)
    ap.add_argument("--source-dir",type=Path)
    ap.add_argument("--max-extra-accepted",type=int,default=MAX_EXTRA_ACCEPTED)
    args=ap.parse_args()
    if not 1<=args.max_extra_accepted<=MAX_EXTRA_ACCEPTED:
        raise SystemExit("INVALID_EXTRA_ACCEPTED_CAP")
    if args.execute and args.execution_manifest is None:
        raise SystemExit("EXECUTION_MANIFEST_REQUIRED")
    ev=args.evidence_dir.resolve(); ev.mkdir(parents=True,exist_ok=False)
    started=time.monotonic(); usage0=resource.getrusage(resource.RUSAGE_SELF)
    report={"status":"FAIL","scope":"U4 H-only steady-temperature bounded transition",
        "first_failure":None,"u3_stop_npz_sha256_expected":U3_STOP_NPZ_SHA256,
        "u3_stop_json_sha256_expected":U3_STOP_JSON_SHA256,
        "u3_verification_sha256_expected":U3_VERIFICATION_SHA256,
        "limits":{"extra_accepted_max":args.max_extra_accepted,"full_evaluations_max":8192,
                  "common_input_max":64,"address_space_bytes":2*1024**3,
                  "cpu_s":540,"wall_s":600,"native_oracle_s":60,"build_s":30}}
    try:
        checkpoint=load_reviewed_u3_stop(args.u3_stop_npz,args.u3_stop_json,args.u3_verification)
        report["start"]={"j":382,"iz":int(checkpoint["global_iz"][-1]),
            "z":float(checkpoint["z"][-1]),"xe":float(checkpoint["xe"][-1]),
            "Tm_K":float(checkpoint["Tm_K"][-1]),"post_saha":bool(checkpoint["post_saha"][-1]),
            "accepted_photon_columns":int(checkpoint["virtual_out"].shape[1]),
            "h_rhs_f381":float(checkpoint["hydrogen_rhs_dln_a"][-1]),
            "h_rhs_f380":float(checkpoint["hydrogen_rhs_dln_a"][-2])}
        if args.preflight:
            report["status"]="PREFLIGHT_ONLY"; return 0
        manifest=validate_execution_manifest(args.execution_manifest)
        report["execution_manifest_sha256"]=sha256(args.execution_manifest)
        with (ev/"controller_execution_manifest.json").open("xb") as out:
            out.write(args.execution_manifest.read_bytes())
        src=safe_source(args.source_dir,ev)
        report["source_zip_sha256"]=PINNED_ZIP_SHA
        report["source_sha256"]={k:sha256(src/k) for k in PINNED_SOURCE}
        with (ev/"source_manifest.json").open("x") as out:
            json.dump({"source_zip_sha256":PINNED_ZIP_SHA,
                "source_members":zip_member_hashes(),"source_c":report["source_sha256"],
                "u3_checkpoint":U3_STOP_NPZ_SHA256,
                "u4_python_sha256":sha256(ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_hydrogen_transition.py"),
                "u4_c_harness_sha256":sha256(ROOT/"scripts/c_harness/original_hyrec_hydrogen_transition_harness.c"),
                "u4_verifier_sha256":sha256(Path(__file__))},out,sort_keys=True,indent=2)
            out.write("\n")
        os.chdir(src)
        affinity=sorted(os.sched_getaffinity(0)); os.sched_setaffinity(0,{affinity[0]})
        report["affinity"]=[affinity[0]]
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(540,540))
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("U4_WALL_LIMIT_600S")))
        signal.alarm(600)
        c=HyRec2012Cosmology()
        table=OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        source=make_hmla_source(c,table)
        common_cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-I",str(src),
            str(ROOT/"scripts/c_harness/original_hyrec_full_source_harness.c"),
            str(src/"hydrogen.c"),str(src/"hyrectools.c"),"-lm","-o",str(ev/"liboriginal_full_source.so")]
        report["common_build"]=run_capture(common_cc,src,ev/"common_build_stdout.txt",ev/"common_build_stderr.txt",30,os.environ.copy())
        if report["common_build"]["returncode"]: raise RuntimeError("COMMON_C_BUILD_FAILED")
        native_cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(src),
            str(ROOT/"scripts/c_harness/original_hyrec_hydrogen_transition_harness.c"),
            str(src/"history.c"),str(src/"hydrogen.c"),str(src/"helium.c"),
            str(src/"hyrectools.c"),"-lm","-o",str(ev/"native_u4_oracle")]
        report["native_build"]=run_capture(native_cc,src,ev/"native_build_stdout.txt",ev/"native_build_stderr.txt",30,os.environ.copy())
        if report["native_build"]["returncode"]: raise RuntimeError("NATIVE_C_BUILD_FAILED")
        report["native_binary_sha256"]=sha256(ev/"native_u4_oracle")
        report["native_run"]=run_capture([str(ev/"native_u4_oracle"),str(args.max_extra_accepted)],
            src,ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",60,os.environ.copy())
        if report["native_run"]["returncode"]: raise RuntimeError("NATIVE_C_U4_ORACLE_FAILED")
        meta,node,steps,cv,ca,cl,cend=parse_native(ev/"native_oracle_stdout.csv")
        report["native_c_stdout_sha256"]=sha256(ev/"native_oracle_stdout.csv")
        compare_state({"iz":int(checkpoint["global_iz"][-1]),"z":float(checkpoint["z"][-1]),
            "xH1s":float(checkpoint["xH1s"][-1]),"xHII":float(checkpoint["xHII"][-1]),
            "xHeII":float(checkpoint["xHeII"][-1]),"xe":float(checkpoint["xe"][-1]),
            "Tm_K":float(checkpoint["Tm_K"][-1]),"post_saha":bool(checkpoint["post_saha"][-1])},node,0)
        oracle=load_u2_verifier().FullSourceCOracle(ev/"liboriginal_full_source.so",src,c)
        result=continue_hydrogen_steady(checkpoint,c,source,common_input_oracle=oracle,
            max_extra_accepted=args.max_extra_accepted,
            checkpoint_callback=lambda payload:save_checkpoint(ev,payload))
        state_max={k:0. for k in ("xH1s","xHII","xe","xHeII","Tm_K")}
        rhs_max=0.; spectrum_max={k:0. for k in ("virtual","average","lyman")}
        rows=[]; event_j=None
        twog=load_u2_verifier()._canonical_twophoton_table(table.archive_path)
        for j in range(START_J,START_J+result["accepted_extra"]):
            crow=steps.get(j)
            if crow is None: raise ArithmeticError(f"C_MISSING_STEP:j={j}")
            n=j+1; py={k:(bool(result["nodes"][k][n]) if k=="post_saha" else
                         int(result["nodes"][k][n]) if k=="global_iz" else
                         float(result["nodes"][k][n]))
                    for k in ("global_iz","z","xH1s","xHII","xHeII","xe","Tm_K","post_saha")}
            py["iz"]=py.pop("global_iz")
            errors=compare_state(py,crow,j)
            if not all(math.isfinite(v) for v in errors.values()):
                raise ArithmeticError(f"NONFINITE_INTEGRATED_STATE_ERROR:j={j}")
            for k,v in errors.items(): state_max[k]=max(state_max[k],v)
            crossed=bool(result["nodes"]["post_saha"][j]) and not bool(result["nodes"]["post_saha"][n])
            if crossed!=crow["post_saha_crossed"]: raise ArithmeticError(f"POST_SAHA_EVENT_FLAG_PARITY:j={j}")
            if crossed and event_j is None: event_j=n
            hscaled=abs(float(result["hydrogen_rhs_dln_a"][j])-crow["hydrogen_rhs"])/max(1.,abs(crow["hydrogen_rhs"]))
            if not math.isfinite(hscaled): raise ArithmeticError(f"NONFINITE_INTEGRATED_RHS_ERROR:j={j}")
            rhs_max=max(rhs_max,hscaled)
            if hscaled>2e-7: raise ArithmeticError(f"INTEGRATED_H_RHS_PARITY:j={j}:scaled={hscaled}")
            tr_ev=8.617343e-5*c.T0_K*(1.+float(result["nodes"]["z"][j]))
            fbbv=1./np.expm1(twog.energy_eV/tr_ev)
            fbbl=1./np.expm1(np.array((10.198714553953742,12.087365397278509,12.748393192442178))/tr_ev)
            for name,arr,map0,fb,numbins in (("virtual",result["virtual_out"][:,j],cv,fbbv,311),
                ("average",result["average_virtual"][:,j],ca,fbbv,311),
                ("lyman",result["lyman_out"][:,j],cl,fbbl,3)):
                ref=np.array([map0[j][b] for b in range(numbins)])
                spectrum_max[name]=max(spectrum_max[name],compare_spectra(arr,ref,fb,j,name))
            rows.append(py)
        if len(steps)!=result["accepted_extra"]: raise ArithmeticError("ACCEPTED_COUNT_PARITY")
        if cend[0]!=result["status"] or cend[2]!=result["branch_steps_after_event"] or event_j!=result["event_j"]:
            raise ArithmeticError(f"END_STATUS_OR_EVENT_PARITY:C={cend}:Python={result['status']}")
        with (ev/"python_accepted_rows.jsonl").open("x") as out:
            for row in rows: out.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n")
        report.update({"status":result["status"],"native_c_stage_metadata":meta,
            "native_c_end":cend,"accepted_extra":result["accepted_extra"],
            "python_full_evaluations":result["full_evaluations"],"event_j":result["event_j"],
            "branch_steps_after_event":result["branch_steps_after_event"],
            "state_max_scaled":state_max,"hydrogen_rhs_max_scaled":rhs_max,
            "spectrum_max_tolerance_ratio":spectrum_max,
            "common_input_sample_j":result["samples"],"common_input_max":result["common_max"],
            "python_rows_sha256":sha256(ev/"python_accepted_rows.jsonl"),
            "checkpoint_count":len(list(ev.glob("checkpoint_*.npz"))),
            "claim_ceiling":"bounded q=0 original HyRec H-only stage; no full primordial Python history or Bianchi/CMB claim"})
    except BaseException as exc:
        typed=str(exc)
        report["status"]=typed if typed.startswith("HOLD_NEXT_STAGE_REQUIRED") else "FAIL"
        report["first_failure"]={"type":type(exc).__name__,"message":str(exc),
                                 "traceback":traceback.format_exc()}
        with (ev/"first_failure.json").open("x") as out:
            json.dump(report["first_failure"],out,sort_keys=True,indent=2); out.write("\n")
    finally:
        signal.alarm(0)
        usage=resource.getrusage(resource.RUSAGE_SELF)
        report["resources"]={"wall_s":time.monotonic()-started,
            "parent_cpu_s":(usage.ru_utime+usage.ru_stime)-(usage0.ru_utime+usage0.ru_stime),
            "parent_peak_rss_bytes":usage.ru_maxrss*1024}
        with (ev/"verification.json").open("x") as out:
            json.dump(report,out,sort_keys=True,indent=2); out.write("\n")
    return 0 if report["status"] in ("EVENT_TWO_STEPS_COMPLETE","PREFLIGHT_ONLY") else 2

if __name__=="__main__": raise SystemExit(main())

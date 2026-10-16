#!/usr/bin/env python3
"""Verify bounded Python helium stages against original unmodified helium.c."""
from __future__ import annotations
import argparse, ctypes, hashlib, json, math, os, resource, shutil, subprocess, time, zipfile
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
SOURCE_ZIP=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
EXPECTED={"history.c":"8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976",
          "helium.c":"1db7a9845e1f5a3052153bf94c1b98bf908cf16715641cbd14c810e5df6a5ece"}
sys.path.insert(0,str(ROOT/"src"))
from full_bianchi_hyrec.trajectory.primordial_2012_helium import (  # noqa:E402
    HyRec2012Cosmology,helium_rhs,integrate_helium_stages)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    cap=2*1024**3
    old_soft,old_hard=resource.getrlimit(resource.RLIMIT_AS)
    soft=cap if old_soft==resource.RLIM_INFINITY else min(old_soft,cap)
    hard=cap if old_hard==resource.RLIM_INFINITY else min(old_hard,cap)
    resource.setrlimit(resource.RLIMIT_AS,(soft,hard))
    wall_start=time.perf_counter()
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path)
    ap.add_argument("--source-dir",type=Path,default=Path(os.environ["HYREC2012_SOURCE_DIR"]) if os.environ.get("HYREC2012_SOURCE_DIR") else None,
                    help="verified extracted original HyRec source; default extracts pinned repository ZIP")
    ap.add_argument("--evidence-dir",type=Path,default=ROOT/"research/rec_r3g_helium_stage_20261016/oracle_001",
                    help="create-only directory retaining original C stdout/stderr and run metadata")
    args=ap.parse_args()
    if args.evidence_dir.exists(): raise SystemExit("EVIDENCE_DIR_EXISTS; choose a new immutable evidence directory")
    args.evidence_dir.mkdir(parents=True,exist_ok=False)
    ORIGINAL=args.source_dir.resolve() if args.source_dir else None
    if ORIGINAL is not None and not ORIGINAL.is_dir():
        raise SystemExit("SOURCE_DIR_NOT_FOUND")
    if ORIGINAL is None:
        if sha(SOURCE_ZIP)!="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27":
            raise SystemExit("SOURCE_ZIP_SHA_MISMATCH")
        ORIGINAL=args.evidence_dir/"source"
        ORIGINAL.mkdir()
        with zipfile.ZipFile(SOURCE_ZIP) as zf:
            for name in ("history.c","helium.c","helium.h","hyrec_params.h","hydrogen.c","hydrogen.h","hyrectools.c","hyrectools.h","history.h"):
                member="HyRec/"+name
                info=zf.getinfo(member)
                if info.file_size<=0 or info.file_size>50_000_000 or Path(info.filename).is_absolute() or ".." in Path(info.filename).parts:
                    raise SystemExit("UNSAFE_SOURCE_MEMBER:"+member)
                (ORIGINAL/name).write_bytes(zf.read(info))
    for name,digest in EXPECTED.items():
        p=ORIGINAL/name
        if sha(p)!=digest: raise SystemExit(f"SOURCE_SHA_MISMATCH:{name}")
    csrc=ROOT/"scripts/c_harness/original_hyrec_helium_stage_harness.c"
    env={**os.environ,"OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1","MKL_NUM_THREADS":"1",
         "NUMEXPR_NUM_THREADS":"1","PYTHONHASHSEED":"0"}
    prefix=["prlimit","--as=2147483648","--"] if shutil.which("prlimit") else []
    binary=args.evidence_dir/"helium_stage_oracle"
    native_sources=["history.c","hydrogen.c","helium.c","hyrectools.c"]
    cmd=[*prefix,"gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(ORIGINAL),str(csrc),*(str(ORIGINAL/n) for n in native_sources),"-lm","-o",str(binary)]
    build=subprocess.run(cmd,capture_output=True,text=True,timeout=60,env=env)
    (args.evidence_dir/"oracle_build_stderr.txt").write_text(build.stderr)
    if build.returncode: raise RuntimeError("C_ORACLE_BUILD_FAILED: "+build.stderr[-2000:])
    binary_sha=sha(binary)
    run=subprocess.run([*prefix,str(binary)],capture_output=True,text=True,timeout=30,check=False,env=env)
    (args.evidence_dir/"oracle_stdout.txt").write_text(run.stdout)
    (args.evidence_dir/"oracle_stderr.txt").write_text(run.stderr)
    if run.returncode: raise RuntimeError(f"C_ORACLE_EXIT_{run.returncode}; raw stderr retained at {args.evidence_dir/'oracle_stderr.txt'}")
    shared=args.evidence_dir/"liboriginal_helium.so"
    shared_cmd=[*prefix,"gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-I",str(ORIGINAL),str(ORIGINAL/"helium.c"),"-lm","-o",str(shared)]
    shared_build=subprocess.run(shared_cmd,capture_output=True,text=True,timeout=30,env=env)
    if shared_build.returncode: raise RuntimeError("C_RATE_LIBRARY_BUILD_FAILED: "+shared_build.stderr[-2000:])
    c_lib=ctypes.CDLL(str(shared))
    c_rate=c_lib.rec_helium_dxHeIIdlna
    c_rate.argtypes=[ctypes.c_double]*9; c_rate.restype=ctypes.c_double
    crows=[]
    for ln,line in enumerate(run.stdout.splitlines()):
        f=line.split()
        if len(f)!=15: raise RuntimeError(f"C_ORACLE_BAD_ROW:{ln}:{line}")
        crows.append((int(f[0]),*map(float,f[1:13]),int(f[13]),int(f[14])))
    py=integrate_helium_stages();
    if len(crows)!=len(py.iz): raise RuntimeError(f"ROW_COUNT_MISMATCH:{len(crows)}:{len(py.iz)}")
    py_rows=args.evidence_dir/"python_accepted_rows.jsonl"
    with py_rows.open("x") as f:
        for i in range(len(py.iz)):
            rec={"index":py.iz[i],"z":py.z[i],"xe":py.xe[i],"xHII":py.xHII[i],"xHeI":py.xHeI[i],
                 "xHeII":py.xHeII[i],"xHeIII":py.xHeIII[i],"Tm_K":py.Tm_K[i],
                 "helium_rhs_dln_a":py.helium_rhs_dln_a[i],"stage":py.stage[i],
                 "update_method":py.update_method[i],"post_saha_for_next_step":py.post_saha[i]}
            f.write(json.dumps(rec,separators=(",",":"))+"\n")
    maxabs={k:0.0 for k in ("z","xe","xHII","xHeI","xHeII","xHeIII","Tm_K")}
    maxrel={k:0.0 for k in maxabs}
    first_failure=None; max_common_rhs_abs=0.; max_common_rhs_scaled=0.; common_rhs_failure=None
    max_traj_rhs_abs=0.; max_traj_rhs_scaled=0.; first_traj_rhs=None
    for i,(row,idx) in enumerate(zip(crows,py.iz)):
        ci,z,xe,xhii,xhei,xheii,xheiii,tm,rhs,zin,h_in,xh1_in,xheii_in,method,post=row
        if ci!=idx: raise RuntimeError(f"INDEX_BOUNDARY_MISMATCH:{i}:{ci}:{idx}")
        numeric=(z,xe,xhii,xhei,xheii,xheiii,tm,rhs,zin,h_in,xh1_in,xheii_in)
        if not all(math.isfinite(v) for v in numeric): raise RuntimeError(f"NONFINITE_C_STATE:{i}")
        py_numeric=(py.z[i],py.xe[i],py.xHII[i],py.xHeI[i],py.xHeII[i],py.xHeIII[i],py.Tm_K[i],py.helium_rhs_dln_a[i])
        if not all(math.isfinite(v) for v in py_numeric): raise RuntimeError(f"NONFINITE_PYTHON_STATE:{i}")
        if py.stage[i]!="HeIII_SAHA":
            c_map=c_rate(xh1_in,xheii_in,HyRec2012Cosmology().nH0_m3,HyRec2012Cosmology().T0_K,
                         HyRec2012Cosmology().fHe,h_in,zin,1.0,1.0)
            p_map=helium_rhs(HyRec2012Cosmology(),xh1_in,xheii_in,h_in,zin)
            map_abs=abs(c_map-p_map); map_scaled=map_abs/max(1.,abs(c_map))
            max_common_rhs_abs=max(max_common_rhs_abs,map_abs); max_common_rhs_scaled=max(max_common_rhs_scaled,map_scaled)
            if map_scaled>2e-10 and common_rhs_failure is None:
                common_rhs_failure={"index":i,"C_source_rate":c_map,"Python_rate_same_inputs":p_map,
                    "xHeII":xheii_in,"xH1s":xh1_in,"z":zin,"H_s_inv":h_in,"scaled_difference":map_scaled}
            traj_delta=abs(rhs-py.helium_rhs_dln_a[i]); traj_scaled=traj_delta/max(1.,abs(rhs))
            max_traj_rhs_abs=max(max_traj_rhs_abs,traj_delta); max_traj_rhs_scaled=max(max_traj_rhs_scaled,traj_scaled)
            if traj_scaled>2e-10 and first_traj_rhs is None:
                first_traj_rhs={"index":i,"C_rhs_at_source_input_state":rhs,
                    "Python_rhs_at_its_own_input_state":py.helium_rhs_dln_a[i],"absolute_difference":traj_delta,
                    "scaled_difference":traj_scaled,"C_input":{"xHeII":xheii_in,"xH1s":xh1_in,"z":zin,"H_s_inv":h_in},
                    "classification":"trajectory state sensitivity diagnostic; direct common-input map checked separately"}
        expected_method={"SAHA_ALGEBRAIC":-1,"POST_SAHA":1,"SOURCE_PREDICTOR":0}[py.update_method[i]]
        if method!=expected_method: raise RuntimeError(f"UPDATE_METHOD_MISMATCH:{i}:C={method}:Python={expected_method}")
        vals={"z":(z,py.z[i]),"xe":(xe,py.xe[i]),"xHII":(xhii,py.xHII[i]),
              "xHeI":(xhei,py.xHeI[i]),"xHeII":(xheii,py.xHeII[i]),"xHeIII":(xheiii,py.xHeIII[i]),"Tm_K":(tm,py.Tm_K[i]),
              }
        for k,(a,b) in vals.items():
            d=abs(a-b); maxabs[k]=max(maxabs[k],d); maxrel[k]=max(maxrel[k],d/max(1.0,abs(a)))
            if d/max(1.0,abs(a)) > 2e-12 and first_failure is None:
                first_failure={"kind":"PARITY_TOLERANCE","quantity":k,"index":i,"C":a,"Python":b,
                    "absolute_difference":d,"scaled_difference":d/max(1.0,abs(a)),
                    "limit":2e-12}
                break
        if bool(post)!=py.post_saha[i]: raise RuntimeError(f"NEXT_STEP_POST_SAHA_MISMATCH:{i}")
        if abs(xhii+xheii+2*xheiii-xe)>5e-13: raise RuntimeError(f"ELECTRON_LEDGER:{i}")
        if abs(xhei+xheii+xheiii-HyRec2012Cosmology().fHe)>5e-13: raise RuntimeError(f"HELIUM_LEDGER:{i}")
    limits={"z":2e-12,"xe":2e-12,"xHII":2e-12,"xHeI":2e-12,"xHeII":2e-12,"xHeIII":2e-12,"Tm_K":2e-12}
    first_ode=next((i for i,m in enumerate(py.update_method) if m=="SOURCE_PREDICTOR"),None)
    source_members={n:sha(ORIGINAL/n) for n in native_sources+["history.h","hydrogen.h","helium.h","hyrectools.h","hyrec_params.h"]}
    py_rows_sha=sha(py_rows)
    self_use=resource.getrusage(resource.RUSAGE_SELF)
    child_use=resource.getrusage(resource.RUSAGE_CHILDREN)
    report={"status":"PASS" if first_failure is None and common_rhs_failure is None else "FAIL","scope":"HeIII Saha + HeII->HeI through izH0; H Saha closure; Tm steady-state",
      "source_sha256":EXPECTED,"supporting_source_sha256":source_members,"c_compiler_command":cmd,"c_binary_sha256":binary_sha,"c_shared_library_command":shared_cmd,
      "resources":{"wall_limit_s_each_child":60,"address_space_limit_bytes":2147483648 if prefix else "NOT_ENFORCED_PRLIMIT_UNAVAILABLE",
        "parent_RLIMIT_AS_bytes":[soft,hard],"parent_peak_rss_bytes":self_use.ru_maxrss*1024,
        "largest_child_peak_rss_bytes":child_use.ru_maxrss*1024,"parent_cpu_s":self_use.ru_utime+self_use.ru_stime,
        "children_cpu_s":child_use.ru_utime+child_use.ru_stime,"wall_s":time.perf_counter()-wall_start,
        "OMP_NUM_THREADS":1,"OPENBLAS_NUM_THREADS":1,"MKL_NUM_THREADS":1},
      "rows":len(crows),"izH0":py.iz[-1],"z_at_izH0":py.z[-1],"first_actual_source_predictor_update_index":first_ode,
      "max_abs_difference":maxabs,"max_scaled_difference_d_over_max_1_abs_C":maxrel,"acceptance_scaled_max":limits,
      "first_failure":first_failure,"compared_rows":len(crows),
      "trajectory_rhs_diagnostic":{"max_abs_difference":max_traj_rhs_abs,"max_scaled_difference":max_traj_rhs_scaled,"first_discrepancy":first_traj_rhs,"interpretation":"This is trajectory-to-trajectory RHS comparison at slightly different binary64 states; not the common-input RHS map gate."},
      "common_input_rhs_map_parity":{"max_abs_difference":max_common_rhs_abs,"max_scaled_difference":max_common_rhs_scaled,"limit":2e-10,"first_failure":common_rhs_failure,"shared_library_sha256":sha(shared)},
      "python_accepted_rows":{"path":str(py_rows),"rows":len(py.iz),"sha256":py_rows_sha},
      "raw_oracle":{"stdout_path":str(args.evidence_dir/"oracle_stdout.txt"),"stdout_sha256":sha(args.evidence_dir/"oracle_stdout.txt"),"stderr_path":str(args.evidence_dir/"oracle_stderr.txt"),"stderr_sha256":sha(args.evidence_dir/"oracle_stderr.txt")},
      "source_stage_boundaries":{"HeIII_Saha_indices":[0,next(i for i,s in enumerate(py.stage) if s!="HeIII_SAHA")-1],"HeII_HeI_start_index":next(i for i,s in enumerate(py.stage) if s!="HeIII_SAHA"),"end_inclusive_izH0":py.iz[-1]},
      "independence_limit":"Python stages are independently computed; C output is used only as oracle. No H FULL evolution or full-history claim."}
    payload=json.dumps(report,sort_keys=True,indent=2)+"\n"
    (args.evidence_dir/"verification.json").write_text(payload)
    if args.output: args.output.write_text(payload)
    print(payload,end="")
    if first_failure is not None or common_rhs_failure is not None: raise SystemExit(2)

if __name__=="__main__": main()

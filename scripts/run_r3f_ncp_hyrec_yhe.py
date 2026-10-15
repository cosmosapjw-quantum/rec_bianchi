"""Original HyRec 2012 H+He FULL, finite-difference helium-input sensitivity.

Runs an unmodified, SHA-pinned native C solver on separate source inputs.
Only Python standard library, GCC and (optionally) prlimit are required.
Not a Bianchi high-z prediction or an REI native simulation.

Scientific derivative means d/dY_He of the FLRW HyRec source result with fixed
omega_b h^2, omega_c+b h^2, radiation budget, T0, and other input parameters.
It includes the change of n_H with Y_He; xe=n_e/n_H is NOT n_e itself.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
REFERENCE = ROOT / "research/rec_r3c_rei_bridge_20261015/HYREC_ORIGINAL_REI_MATCHED_STDOUT.gz"
SOURCE_SHA = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
BASELINE_STDOUT_SHA = "6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400"
REI_SCENARIO_SHA = "07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"
# Literal October-2012 source parameters already used in REC PR94.
PARAMS = dict(T0_K=2.7255, omega_b_h2=0.0224,
              omega_cb_h2=0.14309694000000003, omega_k_h2=0.0,
              omega_lambda_h2=0.31113726660800006,
              w0=-1.0, wa=0.0, YHe=0.2454,
              N_eff_massless_equivalent=3.03821934419124)
STEP = 0.000125
SOURCE_MEMBERS = (
    "hyrec.c", "history.c", "hydrogen.c", "helium.c", "hyrectools.c",
    "hydrogen.h", "helium.h", "history.h", "hyrectools.h", "hyrec_params.h",
    "Alpha_inf.dat", "R_inf.dat", "two_photon_tables.dat",
)
C_SOURCES = ("hyrec.c", "history.c", "hydrogen.c", "helium.c", "hyrectools.c")
SAMPLE_Z = (1600, 1100, 900, 600, 100, 20, 4)
DERIVATIVE_Z = tuple(range(20, 1601))
CENTRAL_INDICES = (-4, -2, -1, 0, 1, 2, 4)
SOURCE_GCC_FLAGS = ("-std=gnu99", "-O3", "-fno-fast-math")


def source_input(yhe: float) -> str:
    """Identical byte-oriented stdin formatting to REC PR94's source owner."""
    if not math.isfinite(yhe) or not 0.0 < yhe < 0.5:
        raise ValueError("source helium mass fraction outside validation domain")
    p = {**PARAMS, "YHe": yhe}
    return ("{T0_K:.16g}\n{omega_b_h2:.16g}\n{omega_cb_h2:.16g}\n"
            "{omega_k_h2:.16g}\n{omega_lambda_h2:.16g}\n"
            "{w0:.16g} {wa:.16g}\n{YHe:.16g}\n"
            "{N_eff_massless_equivalent:.16g}\n").format(**p)


def checked_source_copy(target: Path) -> Path:
    """Extract only named original members; no user-controlled archive paths."""
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SOURCE_SHA:
        raise RuntimeError("IMMUTABLE_SOURCE_SHA_MISMATCH")
    target.mkdir(mode=0o700, parents=True, exist_ok=False)
    with zipfile.ZipFile(SOURCE) as zf:
        for name in SOURCE_MEMBERS:
            member = "HyRec/" + name
            record = zf.getinfo(member)
            if record.file_size <= 0 or record.file_size > 50_000_000:
                raise RuntimeError("INVALID_SOURCE_MEMBER_SIZE: " + member)
            (target / name).write_bytes(zf.read(member))
    return target


def build_native(source_dir: Path, binary: Path) -> dict:
    cmd = ("gcc", *SOURCE_GCC_FLAGS,
           *(str(source_dir / name) for name in C_SOURCES), "-lm", "-o", str(binary))
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
    if p.returncode or not binary.is_file():
        raise RuntimeError("ORIGINAL_C_BUILD_FAILED: " + p.stderr[-900:])
    return {"compiler": "gcc", "flags": list(SOURCE_GCC_FLAGS),
            "compiler_version": subprocess.run(["gcc", "--version"], capture_output=True,
                                                text=True, check=True).stdout.splitlines()[0],
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "source_sha256": SOURCE_SHA}


def parse_history(stdout: bytes, yhe: float) -> list[tuple[float, float]]:
    """Validate all 8001 original-C redshift, electron and thermal records."""
    lines = stdout.decode("ascii").splitlines()
    if len(lines) != 8001:
        raise ValueError(f"ORIGINAL_C_ROW_COUNT_INVALID: {len(lines)}")
    f_he = yhe / ((1-yhe)*3.97153)
    rows: list[tuple[float,float]] = []
    for index, line in enumerate(lines):
        fields = line.split()
        if len(fields) != 3:
            raise ValueError(f"ORIGINAL_C_COLUMN_COUNT_INVALID: {index}")
        z, x_e, t_over_tr = map(float, fields)
        if (not all(map(math.isfinite, (z, x_e, t_over_tr)))
            or z != 8000-index
            or x_e <= 0 or x_e > 1+2*f_he+0.002
            or not (0 < t_over_tr < 1.00001)):
            raise ValueError(f"ORIGINAL_C_PHYSICAL_OR_CLOCK_DOMAIN_ERROR: {index}")
        rows.append((x_e, t_over_tr))
    return rows


def original_case(binary: Path, source_dir: Path, index: int,
                  *, wall_limit: int, address_limit_gib: int,
                  include_curve: bool=False) -> dict:
    yhe = PARAMS["YHe"] + index*STEP
    input_text = source_input(yhe)
    cmd = [str(binary)]
    if shutil.which("prlimit"):
        cmd = ["prlimit", "--as="+str(address_limit_gib*(1024**3)), "--", *cmd]
    start = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=source_dir, input=input_text.encode("ascii"),
                           capture_output=True, timeout=wall_limit,
                           env={**os.environ, "OMP_NUM_THREADS":"1", "OPENBLAS_NUM_THREADS":"1"})
        if p.returncode:
            raise RuntimeError(f"C_EXIT_{p.returncode}: {p.stderr[-250:]!r}")
        if len(p.stdout)>2_000_000:
            raise RuntimeError("ORIGINAL_C_STDOUT_OVER_BUDGET")
        rows = parse_history(p.stdout, yhe)
        samples = {}
        for z in SAMPLE_Z:
            x, tr = rows[8000-z]
            samples[str(z)] = {"xe_per_H":x, "Tm_K":tr*PARAMS["T0_K"]*(1+z)}
        result = {"index":index,"YHe":yhe,"source_input_sha256":hashlib.sha256(input_text.encode()).hexdigest(),
                  "source_stdout_sha256":hashlib.sha256(p.stdout).hexdigest(),
                  "z_slices":samples,"rows":8001,"elapsed_s":time.perf_counter()-start,"status":"PASS"}
        if include_curve:
            result["curve"] = {str(z):[rows[8000-z][0],rows[8000-z][1]*PARAMS["T0_K"]*(1+z)]
                               for z in DERIVATIVE_Z}
        return result
    except (ValueError,TimeoutError,subprocess.TimeoutExpired,RuntimeError,UnicodeError) as e:
        return {"index":index,"YHe":yhe,"status":"ERROR","error_type":type(e).__name__,
                "error_message":str(e)[:500],"elapsed_s":time.perf_counter()-start}


def semantic_baseline_check(reference_raw: bytes, current_raw: bytes, yhe:float) -> dict:
    previous = parse_history(reference_raw,yhe)
    current = parse_history(current_raw,yhe)
    worst_x, worst_t = 0.,0.
    for (x,t),(ref_x,ref_t) in zip(current,previous):
        worst_x=max(worst_x,abs(x-ref_x)/max(abs(ref_x),1e-12))
        worst_t=max(worst_t,abs(t-ref_t)/max(abs(ref_t),1e-12))
    return {"reference_stdout_sha256":hashlib.sha256(reference_raw).hexdigest(),
            "current_stdout_sha256":hashlib.sha256(current_raw).hexdigest(),
            "byte_identical":reference_raw==current_raw,
            "max_rel_xe":worst_x,"max_rel_Tm_over_Tr":worst_t,
            "science_equivalent":worst_x<=1e-9 and worst_t<=1e-9}


def central_difference(rows:dict[int,dict],quantity: str,z: int,delta_index: int)->float:
    v=lambda i: rows[i]["z_slices"][str(z)][quantity]
    h=STEP*delta_index
    return (v(delta_index)-v(-delta_index))/(2*h)


def richardson(rows:dict[int,dict],quantity:str,z:int)->dict:
    # First derivative with symmetric 2nd order central differences at h,2h,4h.
    d1=central_difference(rows,quantity,z,1)
    d2=central_difference(rows,quantity,z,2)
    d4=central_difference(rows,quantity,z,4)
    r12=(4*d1-d2)/3
    r24=(4*d2-d4)/3
    value=rows[0]["z_slices"][str(z)][quantity]
    return {"value":value,"D_h":d1,"D_2h":d2,"D_4h":d4,
            "richardson_h_2h":r12,"richardson_2h_4h":r24,
            "richardson_difference_abs":abs(r12-r24),
            "relative_4th_order_consistency":abs(r12-r24)/max(abs(r12),abs(r24),1e-30)}


def derivative_curve(rows:dict[int,dict],out:Path):
    with out.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["zbar","xe0_per_H","Tm0_K","dxe_dYhe_Richardson",
                                    "dTm_K_dYhe_Richardson","source_dln_nH_dYhe",
                                    "source_dln_ne_dYhe"])
        for z in DERIVATIVE_Z:
            val=lambda i,k:rows[i]["curve"][str(z)][k]
            def dd(k):
                d1=(val(1,k)-val(-1,k))/(2*STEP)
                d2=(val(2,k)-val(-2,k))/(4*STEP)
                return (4*d1-d2)/3
            x0,t0=val(0,0),val(0,1)
            dx,dt=dd(0),dd(1)
            w.writerow([z,x0,t0,dx,dt,-1/(1-PARAMS["YHe"]),dx/x0-1/(1-PARAMS["YHe"])])


def execute(*,output_dir:Path,mode:str,workers:int,address_limit_gib:int=2,
            wall_limit_s:int=120) -> dict:
    """No work on NCP launched by this function until invoked explicitly."""
    if mode not in ("smoke","local","ncp"):
        raise ValueError("mode must be smoke/local/ncp")
    cpu=len(os.sched_getaffinity(0)) if hasattr(os,"sched_getaffinity") else os.cpu_count() or 1
    if not 1<=workers<=min(cpu,48) or workers*address_limit_gib>112:
        raise ValueError("unacceptable per-host requested CPU/memory envelope")
    if not 30<=wall_limit_s<=900:
        raise ValueError("unbounded original-C process wall request")
    if mode=="ncp" and (cpu<48 or not shutil.which("prlimit")):
        raise RuntimeError("NCP PREFLIGHT requires >=48 CPU affinity and prlimit executable")
    indices = list(CENTRAL_INDICES) if mode=="smoke" else list(range(-24,25)) if mode=="local" else list(range(-48,49))
    output_dir.mkdir(parents=True,exist_ok=True)
    if any(output_dir.iterdir()):
        raise FileExistsError("CREATE_ONLY_OUTPUT_DIR_REQUIRED")
    started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="rec_r3f_original_hyrec_") as td:
        tmp=Path(td)
        source_dir=checked_source_copy(tmp/"HyRec")
        binary=tmp/"original_hyrec_2012"
        build=build_native(source_dir,binary)
        # Independent persisted source oracle: same native C input generated again.
        raw_ref=gzip.decompress(REFERENCE.read_bytes())
        if hashlib.sha256(raw_ref).hexdigest()!=BASELINE_STDOUT_SHA:
            raise RuntimeError("PR94_BASELINE_SOURCE_OUTPUT_SHA_DRIFT")
        baseline_input=source_input(PARAMS["YHe"])
        baseline=subprocess.run([str(binary)],input=baseline_input.encode(),cwd=source_dir,
                                capture_output=True,timeout=wall_limit_s,check=True)
        comparison=semantic_baseline_check(raw_ref,baseline.stdout,PARAMS["YHe"])
        if not comparison["science_equivalent"]:
            raise RuntimeError("SOURCE_BASELINE_SCIENCE_EQUIVALENCE_GATE_FAIL")
        sample_subset=[-4,-2,-1,0,1,2,4]
        t0=time.perf_counter()
        control_serial=[original_case(binary,source_dir,j,wall_limit=wall_limit_s,
                       address_limit_gib=address_limit_gib) for j in sample_subset]
        serial_seconds=time.perf_counter()-t0
        t0=time.perf_counter()
        with cf.ThreadPoolExecutor(max_workers=min(workers,len(sample_subset))) as pool:
            control_parallel=list(pool.map(lambda j:original_case(binary,source_dir,j,
                  wall_limit=wall_limit_s,address_limit_gib=address_limit_gib), sample_subset))
        parallel_seconds=time.perf_counter()-t0
        if any(a["status"]!="PASS" or b["status"]!="PASS" or
               a["source_stdout_sha256"]!=b["source_stdout_sha256"]
               for a,b in zip(control_serial,control_parallel)):
            raise RuntimeError("C_BYTE_IDENTICAL_SERIAL_PARALLEL_GATE_FAIL")
        t0=time.perf_counter()
        with cf.ThreadPoolExecutor(max_workers=workers) as pool:
            futures=[pool.submit(original_case,binary,source_dir,j,
                                 wall_limit=wall_limit_s,address_limit_gib=address_limit_gib,
                                 include_curve=(j in CENTRAL_INDICES)) for j in indices]
            results=[future.result() for future in cf.as_completed(futures)]
        scientific_wall=time.perf_counter()-t0
    results.sort(key=lambda o:o["index"])
    failures=[r for r in results if r["status"]!="PASS"]
    by_index={r["index"]:r for r in results if r["status"]=="PASS"}
    derivative_summaries={}
    if all(i in by_index for i in CENTRAL_INDICES):
        for z in SAMPLE_Z:
            derivative_summaries[str(z)]={key:richardson(by_index,key,z)
                                           for key in ("xe_per_H","Tm_K")}
        derivative_curve(by_index,output_dir/"SOURCE_DERIVATIVES_Z20_1600.csv")
    report={"schema":"rec.r3f.native_hyrec_yhe.v1", "mode":mode,"status":
            "PASS_NATIVE_SOURCE_YHE_SCAN" if not failures else "FAIL_NATIVE_SOURCE_YHE_SCAN",
            "timestamp_utc":__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "host":os.uname().nodename,"cpu_affinity":cpu,"workers":workers,
            "per_case_address_limit_GiB":address_limit_gib,"per_case_wall_limit_s":wall_limit_s,
            "science_cases":len(indices),"science_cases_passed":len(results)-len(failures),
            "failures":failures,"source_sha256":SOURCE_SHA,"build":build,
            "source_reference_comparison":comparison,
            "source_inputs_fixed_except_YHe":{k:v for k,v in PARAMS.items() if k!="YHe"},
            "base_YHe":PARAMS["YHe"],"delta_YHe_unit":STEP,
            "range_YHe":[PARAMS["YHe"]+min(indices)*STEP,
                          PARAMS["YHe"]+max(indices)*STEP],
            "serial_control_seconds":serial_seconds,"parallel_control_seconds":parallel_seconds,
            "controlled_speedup":serial_seconds/parallel_seconds,
            "science_wall_seconds":scientific_wall,"total_elapsed_seconds":time.perf_counter()-started,
            "derivatives":derivative_summaries,"cases":results,
            "scientific_scope":"FULL native 2012 H+He FLRW YHe source-input partial sensitivity at fixed other parameters",
            "nH_response_rule":"nH proportional to (1-YHe) at fixed omega_bh2; derivative xe/nH not derivative ne",
            "not_rei_solver":True,"not_nonzero_Bianchi_q":True,
            "claim_gate":"SOURCE_REAL_C_FULL_HISTORY_LOCAL_OR_NCP_EXECUTED_NOT_NATIVE_REI"}
    # Keep a restore-grade provenance result even for partial failures.
    (output_dir/"RUN.json").write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n")
    with (output_dir/"CASE_SUMMARY.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["index","YHe","status","z20_xe","z20_Tm_K","z900_xe","z1100_xe","stdout_sha256"])
        for r in results:
            s=r.get("z_slices",{})
            w.writerow([r["index"],r["YHe"],r["status"],
                        s.get("20",{}).get("xe_per_H"),s.get("20",{}).get("Tm_K"),
                        s.get("900",{}).get("xe_per_H"),s.get("1100",{}).get("xe_per_H"),
                        r.get("source_stdout_sha256")])
    digest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in output_dir.iterdir() if f.is_file()}
    (output_dir/"SHA256_MANIFEST.json").write_text(json.dumps(digest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ("status","host","science_cases_passed",
             "science_cases","science_wall_seconds","controlled_speedup")},indent=2))
    if failures:
        raise SystemExit(1)
    return report


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("smoke","local","ncp"),default="smoke")
    ap.add_argument("--workers",type=int,default=4)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--address-limit-gib",type=int,default=2)
    ap.add_argument("--wall-limit-s",type=int,default=120)
    options=ap.parse_args()
    execute(output_dir=options.output_dir,mode=options.mode,
            workers=options.workers,address_limit_gib=options.address_limit_gib,
            wall_limit_s=options.wall_limit_s)

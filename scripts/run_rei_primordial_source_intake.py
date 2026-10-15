"""Rebuild original HyRec2012 FULL at matched REI q=0 cosmology.

Runs the real original 2012 C H+He primordial solver in an isolated
temporary extraction, under 1- and 2-process source parameter scans. The
numerical histories are true native C output, not REC's unfinished R3c
self-consistent Python history or native REI evolution.

Usage:
 PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 \\
    scripts/run_rei_primordial_source_intake.py \\
    --scenario /path/to/rei_bianchi/research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json \\
    --output-dir research/rec_r3c_rei_bridge_20261015
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import tempfile
import time
import zipfile

import numpy as np

from full_bianchi_hyrec.trajectory.rei_initial_boundary import (
    REIConditionalIC,construct_rei_matched_donor,shear_extrapolation_guard,
    K_B_J_K,C_M_S,SIGMA_T_M2,
)

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SOURCE_SHA256="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
MEMBERS=("hyrec.c","history.c","hydrogen.c","helium.c","hyrectools.c",
         "hydrogen.h","helium.h","history.h","hyrectools.h",
         "hyrec_params.h","Alpha_inf.dat","R_inf.dat",
         "two_photon_tables.dat")


def _input_text(params:dict)->str:
    return ("{T0_K:.16g}\n{omega_b_h2:.16g}\n{omega_cb_h2:.16g}\n"
            "{omega_k_h2:.16g}\n{omega_lambda_h2:.16g}\n"
            "{w0:.16g} {wa:.16g}\n{YHe:.16g}\n"
            "{N_eff_massless_equivalent:.16g}\n").format(**params)


def _run_once(binary: Path, source_dir: Path, param:dict, label:str)->dict:
    text=_input_text(param)
    started=time.perf_counter()
    proc=subprocess.run([str(binary)],input=text,text=True,
                        cwd=source_dir,capture_output=True,timeout=180,
                        env={**os.environ,"OMP_NUM_THREADS":"1",
                             "OPENBLAS_NUM_THREADS":"1"})
    elapsed=time.perf_counter()-started
    if proc.returncode:
        raise RuntimeError(f"original HyRec native {label} exit={proc.returncode}: {proc.stderr[-1500:]}")
    output=proc.stdout.encode("ascii")
    records=np.loadtxt(io.StringIO(proc.stdout))
    if (records.shape!=(8001,3)
        or not np.all(records[:,0]==np.arange(8000.,-1.,-1.))
        or np.any(records[:,1]<0)
        or np.any(records[:,2]<=0)):
        raise RuntimeError(f"untrusted original HyRec output {label} shape/domain")
    return {
        "name":label,"parameter":param,
        "data":records,
        "raw":output,
        "native_stdout_sha256":hashlib.sha256(output).hexdigest(),
        "input_sha256":hashlib.sha256(text.encode()).hexdigest(),
        "elapsed_s":elapsed,
        "stderr_sha256":hashlib.sha256(proc.stderr.encode()).hexdigest(),
        "exit_code":proc.returncode,
    }


def _native_build(temporary: Path):
    with zipfile.ZipFile(ORIGINAL_ARCHIVE) as z:
        for name in MEMBERS:
            z.extract("HyRec/"+name,temporary)
    native=temporary/"HyRec"
    binary=temporary/"hyrec_original_rei_matched"
    cmd=["gcc","-std=gnu99","-O3","-fno-fast-math"]
    cmd +=[str(native/f) for f in ("hyrec.c","history.c","hydrogen.c","helium.c","hyrectools.c")]
    cmd +=["-lm","-o",str(binary)]
    proc=subprocess.run(cmd,capture_output=True,text=True)
    if proc.returncode:
        raise RuntimeError("source build failed: "+proc.stderr[-2000:])
    return native,binary,cmd,hashlib.sha256(binary.read_bytes()).hexdigest()


def _vector_history_benchmark(z:np.ndarray,xe:np.ndarray,tm:np.ndarray,
                              ic:REIConditionalIC):
    """Compare postprocessing only; physical native-HyRec integration excluded."""
    ns=ic.densities_at(0)["nH_REI_m3"]
    nh=ns*(1+z)**3
    H0=100*ic.h*1e5/3.0856775814913673e24
    def vector():
        H=H0*np.sqrt(ic.omega_m*(1+z)**3
             +ic.omega_r*(1+z)**4+ic.omega_lambda)
        electron=xe*nh
        tauprime=C_M_S*SIGMA_T_M2*electron/H
        uth=1.5*nh*K_B_J_K*tm*(1+ic.f_he_rei+xe)
        return np.column_stack((electron,tauprime,uth))
    def scalar():
        result=np.empty((len(z),3))
        for j,(zz,xx,tt) in enumerate(zip(z,xe,tm)):
            nhj=ns*(1+zz)**3
            Hj=H0*math.sqrt(ic.omega_m*(1+zz)**3
                          +ic.omega_r*(1+zz)**4+ic.omega_lambda)
            result[j]=[xx*nhj,C_M_S*SIGMA_T_M2*xx*nhj/Hj,
                        1.5*nhj*K_B_J_K*tt*(1+ic.f_he_rei+xx)]
        return result
    a=vector();b=scalar()
    relative=np.max(np.abs(a-b)/np.maximum(np.maximum(abs(a),abs(b)),1e-100))
    if relative>1e-12:raise ArithmeticError(f"postprocess precision mismatch {relative}")
    clocks={}
    for label,fn,nloops in [("scalar",scalar,10),("vector",vector,80)]:
        ts=[]
        for _ in range(4):
            t=time.perf_counter()
            for _ in range(nloops): fn()
            ts.append((time.perf_counter()-t)/nloops)
        clocks[label]={"median_s_per_call":statistics.median(ts),"all_s_per_call":ts}
    return a,{
        "comparison":"same float64 background/thermal/electron observables",
        "rows":len(z),
        "max_rel_difference":float(relative),
        "scalar_s":clocks["scalar"]["median_s_per_call"],
        "numpy_vector_s":clocks["vector"]["median_s_per_call"],
        "speedup_postprocess_only":
            clocks["scalar"]["median_s_per_call"]/clocks["vector"]["median_s_per_call"],
        "scope":"native C source evolution NOT included",
    }


def _plot_histories(outdir:Path,z:np.ndarray,xe:np.ndarray,tm:np.ndarray,
                    ic:REIConditionalIC):
    # Native history is broad; present a meaningful physically supported
    # pre-reionization slice (source q0 only) in two separate clean plots.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    valid=(z>=20)&(z<=1600)
    for col,label,filename in [
        (xe,"Free-electron fraction n_e/n_H (HyRec FULL)","hyrec_rei_bridge_xe.png"),
        (tm,"Matter temperature T_m [K] (HyRec FULL)","hyrec_rei_bridge_Tgas.png"),
    ]:
        fig,ax=plt.subplots(figsize=(7.4,4.4))
        ax.plot(z[valid],col[valid],lw=1.5,label="Original HyRec FULL, REI-matched FLRW")
        ax.scatter([20.],[ic.actual_electron_fraction if col is xe else ic.Tgas_K],
                   s=24,label="REI conditional z=20 baseline")
        ax.set_xlabel("Mean FLRW redshift zbar")
        ax.set_ylabel(label)
        ax.set_xlim(20,1600)
        ax.set_yscale("log")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(outdir/filename,dpi=155)
        plt.close(fig)


def run(*,scenario:Path,output_dir:Path)->dict:
    if hashlib.sha256(ORIGINAL_ARCHIVE.read_bytes()).hexdigest()!=SOURCE_SHA256:
        raise ValueError("original Oct2012 source archive byte authority mismatch")
    ic=REIConditionalIC.from_scenario(scenario)
    params=ic.matched_hyrec2012_parameters()
    output_dir.mkdir(parents=True,exist_ok=True)
    # Physically distinct helium mass fraction variations (0.2 percentage
    # point step). Do NOT call these an uncertainty posterior or an empirical
    # constraint; the run also changes the hydrogen baryon number.
    scan=[("REI_MATCHED_CENTRAL",params),
          ("Y_HE_MINUS_0P002",{**params,"YHe":params["YHe"]-.002}),
          ("Y_HE_PLUS_0P002",{**params,"YHe":params["YHe"]+.002})]
    with tempfile.TemporaryDirectory(prefix="rec_rei_orig_hyrec_") as temp:
        native,binary,cmd,bin_hash=_native_build(Path(temp))
        sequential=[_run_once(binary,native,pr,name) for name,pr in scan]
        start=time.perf_counter()
        with ThreadPoolExecutor(max_workers=2) as pool:
            parallel=list(pool.map(lambda job:_run_once(binary,native,job[1],job[0]),scan))
        parallel_wall=time.perf_counter()-start
        sequential_total=sum(v["elapsed_s"] for v in sequential)
        hashes_equal=[(a["native_stdout_sha256"]==b["native_stdout_sha256"])
                     for a,b in zip(sequential,parallel)]
        if not all(hashes_equal):
            raise AssertionError("parallel original C history byte parity failed")
        central=sequential[0]
        raw=central["raw"]
        raw_sha=central["native_stdout_sha256"]
        compressed=gzip.compress(raw,compresslevel=7,mtime=0)
        (output_dir/"HYREC_ORIGINAL_REI_MATCHED_STDOUT.gz").write_bytes(compressed)
        a=central["data"]
        z=a[:,0]
        xe=a[:,1]
        tm=a[:,2]*ic.tcmb0_K*(1+z)
        bound=construct_rei_matched_donor(
            ic,source_z=z,source_xe=xe,source_Tr_ratio=a[:,2],
            native_source_sha256=raw_sha,
        )
        # Reference histories are native-source C FLRW, no reionization.
        selected=(z>=20)&(z<=1600)
        derived,bench=_vector_history_benchmark(z[selected],xe[selected],
                                                tm[selected],ic)
        native_history=np.column_stack((z[selected],xe[selected],tm[selected],derived))
        np.savetxt(output_dir/"HYREC_FLRW_Z20_TO_1600.csv",native_history,
             delimiter=",",fmt="%.15e",
             header="zbar,xe_per_H,Tgas_K,ne_m3,dtaudlna,u_th_J_m3",comments="")
        _plot_histories(output_dir,z,xe,tm,ic)
        shear=shear_extrapolation_guard(ic)
        (output_dir/"SHEAR_BACK_EXTRAPOLATION.json").write_text(
            json.dumps(shear,indent=2,sort_keys=True)+"\n")
        (output_dir/"REI_CONDITIONAL_BOUNDARY.json").write_text(
            json.dumps(bound,indent=2,sort_keys=True)+"\n")
        variants=[]
        for item in sequential:
            dat=item["data"]
            pos=int(np.flatnonzero(dat[:,0]==20.)[0])
            variants.append({
                "label":item["name"],"YHe_mass":item["parameter"]["YHe"],
                "x_e_z20":float(dat[pos,1]),
                "Tgas_K_z20":float(dat[pos,2]*ic.tcmb0_K*21),
                "stdout_sha256":item["native_stdout_sha256"],
                "input_sha256":item["input_sha256"],
                "wall_s":item["elapsed_s"],
            })
        sensitivity={
            "schema":"rec.rei.recombination_YHe_variation.v1",
            "model":"same q0 original 2012 FULL H+He, YHe +/-0.002 with consistent H number density",
            "not_a_probability_posterior":True,
            "rows":variants,
        }
        (output_dir/"HELIUM_INPUT_SENSITIVITY.json").write_text(
            json.dumps(sensitivity,indent=2,sort_keys=True)+"\n")
        receipt={
            "schema":"rec.rei.native_source_execution.v1",
            "source_zip_sha256":SOURCE_SHA256,
            "raw_original_C_build_command":cmd,
            "compiled_original_binary_sha256":bin_hash,
            "scenario_sha256":ic.scenario_sha256,
            "source_inputs":params,
            "matched_rad_h2":ic.omega_r*ic.h**2,
            "matched_massless_Neff":params["N_eff_massless_equivalent"],
            "target_ic_consistency":"FLRW H(z) exactly density matched in nominal source convention; slight nH0 and fHe normalization differences explicitly disclosed",
            "native_C_output_rows":len(a),
            "native_C_stdout_sha256":raw_sha,
            "raw_output_gzip_sha256":hashlib.sha256(compressed).hexdigest(),
            "two_worker_parallel_bit_identical":all(hashes_equal),
            "all_three_source_case_shas_match":hashes_equal,
            "serial_sum_wall_s":sequential_total,
            "two_worker_total_wall_s":parallel_wall,
            "two_worker_speedup_vs_sum":sequential_total/parallel_wall,
            "source_variants":variants,
            "derived_observables_vectorization":bench,
            "status":"PASS_SCOPED_NATIVE_C_REFERENCE_AND_CONDITIONAL_REI_BOUNDARY",
            "no_REI_production_change":True,
            "no_local_codex":True,
            "complete_self_evolved_REC_FULL_History":"NOT_COMPUTED",
            "scientific_admission":"REI_CONDITIONAL_IC_COMPARISON_ONLY",
        }
        (output_dir/"SOURCE_EXECUTION_RECEIPT.json").write_text(
            json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":receipt["status"],
        "x_e_rei":ic.actual_electron_fraction,
        "T_rei_K":ic.Tgas_K,
        "x_e_hyrec":bound["hyrec_full_conditional_projection"]["electron_fraction_per_H"],
        "T_hyrec_K":bound["hyrec_full_conditional_projection"]["temperature_K"],
        "delta":bound["donor_minus_baseline"],
        "N_eff_matched":receipt["matched_massless_Neff"],
        "three_runs_serial_sum_s":receipt["serial_sum_wall_s"],
        "three_runs_parallel_wall_s":receipt["two_worker_total_wall_s"],
        "postprocess":bench,
        "output_dir":str(output_dir),
    },indent=2))
    return receipt


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--scenario",required=True,type=Path)
    ap.add_argument("--output-dir",required=True,type=Path)
    a=ap.parse_args()
    run(scenario=a.scenario,output_dir=a.output_dir)

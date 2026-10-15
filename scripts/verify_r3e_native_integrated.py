"""Independent native-C vs Python REC FULL *accepted-history* trajectories.

The C oracle calls original archived hydrogen.c::rec_HMLA_2photon_dxHIIdlna
each step with its OWN prior virtual/Lyman output, independently advances its
HII state, and uses a separately expressed positive thermal update.
Python simultaneously evolves its OWN history via PR95 short_full_history.
Neither integrator reads reference/other-trajectory xe or spectral output.

Physics scope: q=0, H-only, initially neutral helium, synthetic zero
spectral distortion before z_start, Euler chemistry + BE Compton temperature.
The original HyRec C production integrator uses a different, higher-order
time method and an earlier physical H/He recombination epoch; this is a
controlled C-source trajectory oracle, NOT primordial-history parity.
"""
from __future__ import annotations

import ctypes
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import time
import zipfile

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import NVIRT
from full_bianchi_hyrec.trajectory.hmla_flrw import (
    COMPTON_GAMMA_PER_T4_S_INV_K4, HMLAFlrwSource, KB_NATIVE_EV_K,
)
from full_bianchi_hyrec.trajectory.primitive_rates import (
    OriginalHyRecPrimitiveRateTable,
)
from full_bianchi_hyrec.trajectory.short_full_history import (
    integrate_full_h_short_history,
)


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
ORIGINAL_SHA = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
WRAPPER = ROOT/"scripts/c_harness/original_hyrec_persistent_history_harness.c"
COSMO = dict(h=.6735837,omega_cb=.31242079216478097,
             omega_r_h2=4.1578740068818545e-5,
             omega_de_h2=.3119234221656212,omega_b_h2=.02242,
             y_he_mass=.245,tcmb0_K=2.7255)
MEMBERS = ("hydrogen.c","hydrogen.h","hyrectools.c","hyrectools.h",
           "hyrec_params.h","Alpha_inf.dat","R_inf.dat",
           "two_photon_tables.dat")


def compile_unmodified_native(tmp: Path) -> tuple[Path,Path,dict]:
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()!=ORIGINAL_SHA:
        raise ValueError("original HyRec C source archive SHA drift")
    with zipfile.ZipFile(ARCHIVE) as z:
        for item in MEMBERS:
            z.extract("HyRec/"+item,tmp)
    native = tmp/"HyRec"
    so = tmp/"r3e_native_full.so"
    cmd = ["gcc","-std=gnu99","-O3","-fno-fast-math","-shared",
           "-fPIC","-ffunction-sections","-fdata-sections",
           "-Wl,--gc-sections","-I",str(native),
           str(native/"hydrogen.c"),str(native/"hyrectools.c"),
           str(WRAPPER),"-lm","-o",str(so)]
    t0=time.perf_counter()
    build=subprocess.run(cmd,check=True,capture_output=True,text=True)
    return so,native,{"source_archive_sha256":ORIGINAL_SHA,
                      "wrapper_sha256":hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
                      "binary_sha256":hashlib.sha256(so.read_bytes()).hexdigest(),
                      "compile_seconds":time.perf_counter()-t0,
                      "command":cmd,"compiler_stderr":build.stderr[-900:]}


@contextmanager
def _cwd(where):
    old=Path.cwd()
    try:
        os.chdir(where)
        yield
    finally:
        os.chdir(old)


def _source_model():
    return HMLAFlrwSource(
        **COSMO,table=OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE))


def _c_row_views(arr: np.ndarray):
    """Zero-copy true **double pointer table into entire fixed-capacity rows."""
    ptr=ctypes.POINTER(ctypes.c_double)
    if not arr.flags.c_contiguous or arr.dtype!=np.float64 or arr.ndim!=2:
        raise ValueError("C source histories need C-contiguous float64 rows")
    return (ptr*arr.shape[0])(
        *(arr[j].ctypes.data_as(ptr) for j in range(arr.shape[0])))


def _native_independent_series(
    *, so:Path,native:Path,source:HMLAFlrwSource,
    z_start:float,x_start:float,T_start_K:float,steps:int
) -> dict:
    if not 3<=steps<=2048 or not 0<x_start<1:
        raise ValueError("invalid native bounded test")
    lib=ctypes.CDLL(str(so))
    ptr=ctypes.POINTER(ctypes.c_double)
    rows=ctypes.POINTER(ptr)
    step=lib.rec_r3e_original_native_rhs_persistent
    step.argtypes=[ctypes.c_double]*7+[ctypes.c_uint,ctypes.c_double]+[rows]*3
    step.restype=ctypes.c_double
    virtual=np.zeros((NVIRT,steps),dtype=np.float64,order="C")
    lyman=np.zeros((3,steps),dtype=np.float64,order="C")
    avg=np.zeros((NVIRT,steps),dtype=np.float64,order="C")
    pv,pl,pa=(_c_row_views(v) for v in (virtual,lyman,avg))
    xe=np.zeros(steps,dtype=np.float64)
    temperature=np.zeros(steps,dtype=np.float64)
    rhs=np.zeros(steps,dtype=np.float64)
    eta0=-math.log1p(z_start)
    z=np.expm1(-(eta0+np.arange(steps)*SOURCE_DLNA))
    z[0]=z_start
    xe[0]=x_start
    temperature[0]=T_start_K
    with _cwd(native):
        for i in range(steps):
            zi=float(z[i])
            H,nH_m3=source.cosmology(zi)
            Tr=source.tcmb0_K*(1+zi)
            rhs[i]=float(step(
                float(xe[i]),float(xe[i]),nH_m3*1.e-6,H,
                KB_NATIVE_EV_K*float(temperature[i]),KB_NATIVE_EV_K*Tr,
                float(z_start),int(i),zi,pv,pl,pa))
            if not (np.isfinite(rhs[i])
                    and np.all(np.isfinite(virtual[:,i]))
                    and np.all(np.isfinite(lyman[:,i]))
                    and np.all(np.isfinite(avg[:,i]))):
                raise FloatingPointError(f"original-C nonfinite at {i}")
            if i<steps-1:
                next_x=xe[i]+SOURCE_DLNA*rhs[i]
                if not 0<next_x<1 or not math.isfinite(next_x):
                    raise FloatingPointError(f"native-C independent chemistry step {i} invalid")
                xe[i+1]=next_x
                # The same thermodynamic operator but independently evaluated,
                # never using the Python trajectory's matter temperature.
                z_next=float(z[i+1])
                next_H,_=source.cosmology(z_next)
                Tr_next=source.tcmb0_K*(1+z_next)
                a=(COMPTON_GAMMA_PER_T4_S_INV_K4*Tr_next**4*next_x
                   /((1+next_x+source.f_he)*next_H))
                next_temperature=(temperature[i]+SOURCE_DLNA*a*Tr_next)/(
                    1+SOURCE_DLNA*(2+a))
                if not (0<next_temperature<=Tr_next*(1+1e-10)):
                    raise FloatingPointError(f"native-C thermal bound at {i}")
                temperature[i+1]=next_temperature
    return {"z":z,"xe":xe,"Tm_K":temperature,"rhs":rhs,
            "virtual":virtual,"lyman":lyman,"average_virtual":avg}


def _comparison(a: np.ndarray,b: np.ndarray) -> dict:
    """Global normalized infinity norm; strictly no arbitrary tiny floors."""
    x=np.asarray(a,dtype=float);y=np.asarray(b,dtype=float)
    if x.shape!=y.shape or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise AssertionError("nonfinite or unequal oracle arrays")
    d=float(np.max(np.abs(x-y)))
    scale=max(float(np.max(np.abs(x))),float(np.max(np.abs(y))))
    return {"max_abs":d,"max_rel_global":d/scale if scale>0 else 0.,
            "reference_scale":scale,"shape":list(x.shape)}


def paired_full_history_case(*, so:Path,native:Path,
                             z_start:float=900.,x_start:float=.04,
                             Tm_fraction:float=.98,steps:int=65) -> dict:
    """Two independently evolved photon/electron trajectories, same source Δln a."""
    source=_source_model()
    tm=Tm_fraction*source.tcmb0_K*(1+z_start)
    t0=time.perf_counter()
    python=integrate_full_h_short_history(
        source,z_start=z_start,x_HII_start=x_start,
        Tm_start_K=tm,steps=steps,dlna=SOURCE_DLNA)
    py_s=time.perf_counter()-t0
    t1=time.perf_counter()
    cnative=_native_independent_series(
        so=so,native=native,source=source,
        z_start=z_start,x_start=x_start,T_start_K=tm,steps=steps)
    c_s=time.perf_counter()-t1
    comparisons={
        "xe":_comparison(cnative["xe"],python.x_HII),
        "Tm_K":_comparison(cnative["Tm_K"],python.Tm_K),
        "dx_dln_a":_comparison(cnative["rhs"],python.dx_HII_dln_a),
        "virtual_out":_comparison(cnative["virtual"],python.virtual_out),
        "lyman_out":_comparison(cnative["lyman"],python.lyman_out),
    }
    return {
        "case":{"z_start":z_start,"x_HII_start":x_start,
                "Tm_over_Tr_start":Tm_fraction,"steps":steps,
                "dlna":SOURCE_DLNA},
        "parallel_independent_c_chemistry_photons":True,
        "shared_background_H_nH_and_thermochemistry":True,
        "python_wall_s":py_s,"native_c_wall_s":c_s,
        "comparisons":comparisons,
        "python_final_x":float(python.x_HII[-1]),
        "native_final_x":float(cnative["xe"][-1]),
        "max_python_schur_residual":float(max(python.matrix_residual)),
    }


def run_one(*, z:float=900., x:float=.04, ratio:float=.98,
            steps:int=65) -> dict:
    if not (3<=steps<=2048):
        raise ValueError("steps exceeds finite accepted-H-only contract")
    with tempfile.TemporaryDirectory(prefix="rec_r3e_paired_native_") as temporary:
        so,native,build=compile_unmodified_native(Path(temporary))
        case=paired_full_history_case(
            so=so,native=native,z_start=z,x_start=x,
            Tm_fraction=ratio,steps=steps)
    worst=max(v["max_rel_global"] for v in case["comparisons"].values())
    return {
        "schema":"rec.r3e.native_C_vs_Python_accepted_history.v1",
        "source":"original unmodified HyRec 2012 hydrogen.c + Python independent FULL Schur",
        "compilation":build,"experiment":case,
        "worst_global_relative":worst,
        "source_native_step":SOURCE_DLNA,
        "pass_threshold":1e-7,
        "status":"PASS_SOURCE_FULL_HISTORY_PARITY" if worst<1e-7 else "FAIL",
        "not_original_production_integrator":True,
        "no_physical_primordial_prehistory":True,
    }


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--z",type=float,default=900.)
    ap.add_argument("--x",type=float,default=.04)
    ap.add_argument("--ratio",type=float,default=.98)
    ap.add_argument("--steps",type=int,default=65)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    result=run_one(z=args.z,x=args.x,ratio=args.ratio,steps=args.steps)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],
          "worst_global_relative":result["worst_global_relative"],
          "case":result["experiment"]["case"],
          "comparisons":result["experiment"]["comparisons"]},indent=2))
    if result["status"]!="PASS_SOURCE_FULL_HISTORY_PARITY":
        raise SystemExit(1)

#!/usr/bin/env python3
"""Rebuild and run three pinned *upstream* primordial recombination baselines.

No network, package installation, or changes to an upstream code checkout.
Requirements: gcc, gfortran, original HyRec2012 ZIP already in REC, a clone
of nanoomlee/HYREC-2 at 09e8243..., and lukashergt/recfast at b34efc0....

All inputs and outputs are written into a new empty private evidence folder;
the native full curves never masquerade as native REC coupled solver output.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import time

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    ORIGINAL_HYREC_ARCHIVE_SHA256,safe_extract_original_hyrec_archive,
)

ROOT=Path(__file__).resolve().parents[1]
HYREC2_SHA="09e8243d0e08edd3603a94dfbc445ae06cafe139"
RECFAST_SHA="b34efc0f409050a980be5deca7d016a01bd13631"
ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
h=.6735837
T0=2.7255
OMEGA_B=.0494142797907188
OMEGA_CB=.31242079216478097
YHE=.245
N_EFF=3.0


def _sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _code_lock(path:Path,expected:str)->str:
    p=subprocess.run(["git","-C",str(path),"rev-parse","HEAD"],
        capture_output=True,text=True,timeout=10)
    if p.returncode or p.stdout.strip()!=expected:
        raise ValueError(f"upstream source Git hash mismatch at {path}; expected {expected}")
    return p.stdout.strip()


def _compile(cmd,cwd:Path,name:str):
    p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=60)
    (cwd/(name+".build.stdout")).write_text(p.stdout)
    (cwd/(name+".build.stderr")).write_text(p.stderr)
    if p.returncode:
        raise RuntimeError(f"{name} source build returned {p.returncode}: {p.stderr[-1000:]}")


def _run_native(binary:Path,out:Path,input_path:Path,output_file:str,kind:str):
    start=time.perf_counter()
    with input_path.open("rb") as fh:
        p=subprocess.run([str(binary)],cwd=out,stdin=fh,capture_output=True,timeout=60)
    elapsed=time.perf_counter()-start
    (out/"STDOUT.log").write_bytes(p.stdout)
    (out/"STDERR.log").write_bytes(p.stderr)
    if p.returncode:
        raise RuntimeError(f"{kind} upstream execution failed {p.returncode}")
    output=out/output_file
    if not output.is_file():raise FileNotFoundError(output)
    raw=output.read_bytes()
    if not raw or len(raw.splitlines())<500:
        raise ValueError(f"{kind} output is too short to be a cosmological history")
    return {"code":kind,"command":[binary.name],
            "process_returncode":p.returncode,"elapsed_seconds":elapsed,
            "stdin_sha256":_sha(input_path),
            "output_file":str(output.relative_to(out.parent)),
            "output_sha256":hashlib.sha256(raw).hexdigest(),
            "output_size_bytes":len(raw),"output_rows":len(raw.splitlines())}


def execute(hyrec2_repo:Path,recfast_repo:Path,outdir:Path):
    if outdir.exists() and any(outdir.iterdir()):
        raise ValueError("output directory not empty; refusing overwrite")
    if not ARCHIVE.is_file() or _sha(ARCHIVE)!=ORIGINAL_HYREC_ARCHIVE_SHA256:
        raise ValueError("original HyRec 2012 immutable source archive missing or changed")
    _code_lock(hyrec2_repo,HYREC2_SHA)
    _code_lock(recfast_repo,RECFAST_SHA)
    for cmd in ("gcc","gfortran"):
        if not shutil.which(cmd):raise FileNotFoundError(f"{cmd} required")
    outdir.mkdir(parents=True,exist_ok=True)
    rad=4.48162687719e-7*T0**4*(1.+.227107317660239*N_EFF)
    obh2=OMEGA_B*h*h
    cbh2=OMEGA_CB*h*h
    deh2=h*h-cbh2-rad
    omega_de=deh2/h**2

    # Source's order-specific input parsing is verified by 25 fields.
    raw=(hyrec2_repo/"input.dat").read_text().split("=====")[0]
    lines=[q.strip() for q in raw.splitlines() if q.strip()]
    if len(lines)!=25:raise ValueError("unexpected upstream HyRec-2 input schema")
    for i,value in {
        0:h,1:T0,2:OMEGA_B,3:OMEGA_CB,4:0.,
        6:0,7:0.,8:0.,9:0.,10:YHE,11:N_EFF,12:1.,13:1.,
    }.items():
        lines[i]=str(value)
    input_h2=outdir/"hyrec2.input"
    input_h2.write_text("\n".join(lines)+"\n")

    input_orig=outdir/"hyrec2012.input"
    input_orig.write_text("\n".join([
       str(T0),str(obh2),str(cbh2),"0",str(deh2),"-1 0",
       str(YHE),str(N_EFF),"1","1"])+"\n")
    input_rf=outdir/"recfast.input"
    input_rf.write_text("\n".join([
       "matched_recfast.out",
       f"{OMEGA_B:.17g} {OMEGA_CB-OMEGA_B:.17g} {omega_de:.17g}",
       f"{h*100:.17g} {T0:.17g} {YHE:.17g}","1","6"])+"\n")

    for folder in ("HyRec2_2020","HyRec_2012_FULL","RECFAST_1.7"):
        (outdir/folder).mkdir()
    h2=outdir/"HyRec2_2020"
    for data in hyrec2_repo.glob("*.dat"):
        if data.name not in ("input.dat","output_xe.dat"):
            (h2/data.name).symlink_to(data.resolve())
    _compile(["gcc","-std=gnu11","-O2","-w",*
              [str(hyrec2_repo/q) for q in ("hyrectools.c","helium.c",
                "hydrogen.c","history.c","energy_injection.c","hyrec.c")],
              "-lm","-o",str(h2/"hyrec_ref")],h2,"hyrec2")

    orig=outdir/"HyRec_2012_FULL"
    extr=outdir/"original_2012_source"
    safe_extract_original_hyrec_archive(ARCHIVE,extr)
    parent=extr/"HyRec"
    for data in parent.glob("*.dat"):
        (orig/data.name).symlink_to(data.resolve())
    _compile(["gcc","-std=gnu11","-O2","-w",*
               [str(parent/q) for q in ("hyrectools.c","helium.c",
                                       "hydrogen.c","history.c","hyrec.c")],
               "-lm","-o",str(orig/"hyrec_ref")],orig,"hyrec2012")

    rf=outdir/"RECFAST_1.7"
    _compile(["gfortran","-O2","-ffree-line-length-none","-cpp",
              str(recfast_repo/"src/recfast.f08"),"-o",str(rf/"recfast_ref")],rf,"recfast")

    records={}
    records["HyRec2_2020"]=_run_native(h2/"hyrec_ref",h2,input_h2,"output_xe.dat","HyRec2_2020")
    records["HyRec_2012_FULL"]=_run_native(
      orig/"hyrec_ref",orig,input_orig,"STDOUT.log","HyRec_2012_FULL")
    records["RECFAST_1.7"]=_run_native(
      rf/"recfast_ref",rf,input_rf,"matched_recfast.out","RECFAST_1.7")
    for kind,row in records.items():
        row["note"]=(
         "HyRec2012 col3=Tm/(T0*(1+z)), HyRec2 col3=Tm[K], RECFAST only z,xe"
        )
    (outdir/"REFERENCE_EXECUTION.json").write_text(json.dumps(records,indent=2)+"\n")
    parameters={
        "h":h,"H0_km_s_Mpc":100*h,
        "Omega_b":OMEGA_B,"Omega_cb":OMEGA_CB,"Omega_cdm":OMEGA_CB-OMEGA_B,
        "Omega_lambda_for_massless_neutrino_flat":omega_de,
        "T0_K":T0,"Y_He_mass_fraction":YHE,
        "N_eff_massless":N_EFF,"neutrino_mass_eV":0.,
        "Omega_r_h2":rad,"Omega_b_h2":obh2,"Omega_cb_h2":cbh2,"Omega_de_h2":deh2,
        "source_2012":ORIGINAL_HYREC_ARCHIVE_SHA256,
        "source_hyrec2":HYREC2_SHA,"source_recfast":RECFAST_SHA,
        "input_sha256":{i.name:_sha(i) for i in (input_h2,input_orig,input_rf)},
        "approximation":"Common FLRW h, densities, helium and N_eff=3 massless; RECFAST modern 1.7 effective-three-level physics is not a carbon copy of HyRec FULL."
    }
    (outdir/"COSMOLOGY.json").write_text(json.dumps(parameters,indent=2)+"\n")
    print(json.dumps({"cosmology":parameters,"records":records},indent=2))
    return records


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--hyrec2-repo",type=Path,required=True)
    a.add_argument("--recfast-repo",type=Path,required=True)
    a.add_argument("--outdir",type=Path,required=True)
    v=a.parse_args()
    execute(v.hyrec2_repo.resolve(),v.recfast_repo.resolve(),v.outdir.resolve())


if __name__=="__main__":
    main()

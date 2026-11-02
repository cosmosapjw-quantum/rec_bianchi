#!/usr/bin/env python3
"""Real original 46k-cell F05 V2 H/He Thomson kernel vs physical volume continuation.

This source-conditional REC calculation compares two explicitly distinct
models. It does NOT modify REI original source, certify tick161 or create sky tau.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,subprocess,sys
from pathlib import Path
import numpy as np

REC_PARENT = "832551b69801eea008daf2c8cf19881c28649075"
REI_ORIGINAL_HEAD = "fab9429140038974a98f3ad3212036b0227e600e"
REI_V2_OWNER_HEAD = "a09ea7b999c90a692de07c74352f835707e65838"
ORIGINAL_TAR_SHA = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
ORIGINAL_KERNEL_SHA = "579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
SOURCE_V2_SHA = "c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
SRC_Z = 5.95
MPC_CM = 3.085677581491367e24
SIGMA_T_CM2 = 6.6524587051e-25
C_CM_S = 29979245800.0
N = 46080
COLS = (
  "node","source_proper_volume_cm3",
  "Ne160_lower","Ne160_upper","Ne161V2_lower","Ne161V2_upper",
  "Gamma160_lower_s_inv","Gamma160_upper_s_inv",
  "Gamma161_frozen_lower_s_inv","Gamma161_frozen_upper_s_inv",
  "Gamma161_expanded_lower_s_inv","Gamma161_expanded_upper_s_inv",
  "delta_chem_lower_s_inv","delta_chem_upper_s_inv",
  "delta_geometry_lower_s_inv","delta_geometry_upper_s_inv",
  "delta_total_lower_s_inv","delta_total_upper_s_inv",
)
def digest(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()
def must(ok,label):
    if not ok:raise ValueError("REC197_F05_"+label)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    must(spec is not None and spec.loader is not None,"SOURCE_MODULE_UNAVAILABLE")
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m
    spec.loader.exec_module(m)
    return m
def fsum(x):return float(math.fsum(map(float,np.asarray(x).ravel())))
def electron(lo,hi):
    must(lo.shape==hi.shape==(N,5),"SOURCE_SPECIES_SHAPE")
    l=lo[:,1]+lo[:,3]+2*lo[:,4]
    u=hi[:,1]+hi[:,3]+2*hi[:,4]
    must(np.all(l>0) and np.all(u>=l) and np.isfinite(u).all(),"SOURCE_ELECTRON_CONE")
    return l,u
def source_status(repo,rei):
    must(subprocess.run(["git","-C",str(repo),"merge-base","--is-ancestor",
                         REC_PARENT,"HEAD"],capture_output=True).returncode==0,
         "REC_PARENT_HISTORY_DRIFT")
    must(subprocess.check_output(["git","-C",str(rei),"rev-parse","HEAD"],
         text=True).strip()==REI_ORIGINAL_HEAD,"REI_SOURCE_HEAD_DRIFT")
def model_forcing(original):
    source=load("rec197_original_source_adapter",
                original/"research/rei_f05_owner_original64_rust_20261101/execute_original64.py")
    must(digest(source.ARCHIVE)==ORIGINAL_TAR_SHA,"REI_ORIGINAL_ARCHIVE_SHA")
    worker=source.module("rec197_original_owner_worker",source.A/"attempt_worker.py")
    must(digest(worker.KERNEL_PATH)==ORIGINAL_KERNEL_SHA,"ORIGINAL_KERNEL_SHA")
    worker.jax_guard.install_if_missing()
    kernel=worker._kernel()
    # Only original forcing, no run_step or any updated original state.
    model=kernel.rim.ReducedIntervalModel.from_repo(original)
    return model
def run(rec:Path,rei:Path,candidate:Path,out:Path):
    rec,rei,candidate,out=(Path(p).resolve() for p in (rec,rei,candidate,out))
    must(not out.exists(),"REFUSE_OUTPUT_OVERWRITE")
    source_status(rec,rei)
    must(digest(candidate)==SOURCE_V2_SHA,"V2_REAL_SOURCE_BYTE_SHA")
    # Owner-locked original accepted source, NOT a reconstructed guess of t160.
    u=rec/"research/rec_rei_f05_accepted_history_thomson_20261101"
    loader=load("rec197_accepted160",u/"compute_accepted160.py")
    must(loader.TAR_SHA==ORIGINAL_TAR_SHA,"ACCEPTED_SOURCE_SHA")
    _init,accepted,z,t160,history,terminal=loader.input_sources(u)
    must(abs(float(z)-SRC_Z)<2e-13 and terminal["status"]=="BLOCKED_MINIMUM_STEP",
         "ORIGINAL_ACCEPTED_TERMINAL")
    must([r["right_tick"] for r in history]==[64,128,160],"ACCEPTED_TICK_CHAIN")
    lo0,hi0,tlo0,thi0=accepted
    with np.load(candidate,allow_pickle=False) as s:
        source_arrs=(
            ("source_parent_population_lower",lo0),
            ("source_parent_population_upper",hi0),
            ("source_parent_logT_lower",tlo0),
            ("source_parent_logT_upper",thi0))
        for key,orig in source_arrs:
            must(np.array_equal(s[key],orig),"SOURCE_REAL_ACCEPTED_PARENT_"+key)
        lo1=s["population_lower"].copy()
        hi1=s["population_upper"].copy()
        tlo1=s["log_temperature_lower"].copy()
        thi1=s["log_temperature_upper"].copy()
    must(tlo1.shape==thi1.shape==(N,),"V2_TEMPERATURE_SHAPE")
    must(np.all(thi1>=tlo1) and np.isfinite(thi1).all(),
         "V2_TEMPERATURE_CONE")
    Ne0lo,Ne0hi=electron(lo0,hi0)
    Ne1lo,Ne1hi=electron(lo1,hi1)
    dt=float(t160)/160.0
    must(0<dt<1e11 and np.isfinite(dt),"SOURCE_MICROTICK_CLOCK")
    source_model=model_forcing(rei)
    F0=source_model.forcing_bounds(float(t160),float(t160))
    F1=source_model.forcing_bounds(float(t160)+dt,float(t160)+dt)
    z0,z1=[(float(f.z.lo),float(f.z.hi)) for f in (F0,F1)]
    must(all(abs(v-SRC_Z)<2e-13 for v in (*z0,*z1)),
         "FROZEN_SOURCE_Z_MISMATCH")
    v0lo=np.asarray(F0.volume_cm3.lo,dtype=np.float64)
    v0hi=np.asarray(F0.volume_cm3.hi,dtype=np.float64)
    v1lo=np.asarray(F1.volume_cm3.lo,dtype=np.float64)
    v1hi=np.asarray(F1.volume_cm3.hi,dtype=np.float64)
    must(v0lo.shape==v0hi.shape==(N,),"REAL_VOLUME_SHAPE")
    must(np.array_equal(v0lo,v1lo) and np.array_equal(v0hi,v1hi),
         "SOURCE_VOLUME_NOT_FROZEN")
    must(np.isfinite(v0lo).all() and np.all(v0lo>0) and np.all(v0hi>=v0lo),
         "SOURCE_VOLUME_CONE")
    Hlo=max(float(F0.hubble_s_inv.lo),float(F1.hubble_s_inv.lo))
    Hhi=min(float(F0.hubble_s_inv.hi),float(F1.hubble_s_inv.hi))
    # F0,F1 identical in frozen source. Intersection tightens same H.
    must(0<Hlo<=Hhi,"SOURCE_HUBBLE_RANGE")
    f_lo=math.exp(-3*Hhi*dt)
    f_hi=math.exp(-3*Hlo*dt)
    must(0<f_lo<=f_hi<1,"EXPANSION_FACTOR_SIGN")
    with np.load(rec/"research/rec_rei_f05_native_thomson_medium_20261101/source_inputs/ORIGINAL_REI_F05_initial_material_state_z6.npz",allow_pickle=False) as q:
        W=np.asarray(q["W_node"],dtype=np.float64)
    source_vol=W * (MPC_CM/(1+SRC_Z))**3
    max_vol_relative=float(np.max(np.abs(source_vol-v0lo)/v0lo))
    must(max_vol_relative < 5e-13,"SOURCE_W_VOLUME_CONSISTENCY")
    factor=SIGMA_T_CM2*C_CM_S
    G0lo,G0hi=factor*Ne0lo/v0hi,factor*Ne0hi/v0lo
    G1Flo,G1Fhi=factor*Ne1lo/v0hi,factor*Ne1hi/v0lo
    G1Elo,G1Ehi=f_lo*G1Flo,f_hi*G1Fhi
    chemlo,chemhi=G1Flo-G0hi,G1Fhi-G0lo
    geomlo,geomhi=(f_lo-1)*G1Fhi,(f_hi-1)*G1Flo
    totlo,tothi=G1Elo-G0hi,G1Ehi-G0lo
    arrays=(Ne0lo,Ne0hi,Ne1lo,Ne1hi,G0lo,G0hi,G1Flo,G1Fhi,
            G1Elo,G1Ehi,chemlo,chemhi,geomlo,geomhi,totlo,tothi)
    must(all(np.isfinite(a).all() and a.shape==(N,) for a in arrays),
         "SOURCE_COLLISION_NUMERIC_NONFINITE")
    must(all(np.all(a<=b) for a,b in
        ((G0lo,G0hi),(G1Flo,G1Fhi),(G1Elo,G1Ehi),
         (chemlo,chemhi),(geomlo,geomhi),(totlo,tothi))),
         "COLLISION_INTERVAL_ORDER")
    must(np.all(geomhi<0),"EXPANSION_CONDITIONAL_NEGATIVE")
    # The exact additive model identity is captured by interval inclusion,
    # not requiring distinct interval enclosures to share precise endpoints.
    numerical_eps=4e-15*np.maximum(abs(totlo),np.maximum(abs(tothi),G0hi))
    must(np.all(chemlo+geomlo <= totlo+numerical_eps) and
         np.all(chemhi+geomhi >= tothi-numerical_eps),
         "PHYSICAL_ADDITIVE_DECOMPOSITION_CONTAINS_TOTAL")
    cats={}
    for key,a,b in (("native_chemistry",chemlo,chemhi),
                    ("with_expansion",totlo,tothi)):
        cats[key]={"definite_increase":int(np.sum(a>0)),
                   "definite_decrease":int(np.sum(b<0)),
                   "undetermined":int(np.sum((a<=0)&(b>=0)))}
        must(sum(cats[key].values())==N,"COMPLETE_SIGN_CLASSES_"+key)
    flips=int(np.sum((chemlo>0)&(tothi<0)))
    # Volume-weighted mean opacity is based on ORIGINAL volume,
    # not an unphysical arithmetic cell average across tiny W cells.
    Vtotlo,Vtothi=fsum(v0lo),fsum(v0hi)
    def mean(l,u):
        return [factor*fsum(l)/Vtothi,factor*fsum(u)/Vtotlo]
    av0=mean(Ne0lo,Ne0hi)
    av1f=mean(Ne1lo,Ne1hi)
    av1e=[av1f[0]*f_lo,av1f[1]*f_hi]
    prior=json.loads((rec/"research/rec_f05_accepted_trajectory_20261102/results/SCIENCE_RESULT.json").read_text())
    recgamma=prior["point_physics"]["160"]["volume_mean_Gamma_s_inv"]
    must(all(abs(a-b)/max(abs(b),1e-300)<2e-13 for a,b in zip(av0,recgamma)),
         "REC195_SOURCE_GAMMA160_PARITY")
    out.mkdir(parents=True)
    p=out/"ORIGINAL_F05_V2_THOMSON_GEOMETRY_46080.csv.gz"
    with p.open("xb") as file:
      with gzip.GzipFile(fileobj=file,filename="",mode="wb",mtime=0,compresslevel=6) as gz:
       with io.TextIOWrapper(gz,encoding="ascii",newline="",write_through=True) as fp:
        w=csv.writer(fp,lineterminator="\n")
        w.writerow(COLS)
        for j in range(N):
            w.writerow((j,format(float(v0lo[j]),".17e"),
              *(format(float(a[j]),".17e") for a in arrays)))
    result={
      "schema":"REC197_REI_ORIGINAL_F05_V2_CONDITIONAL_THOMSON_GEOMETRY_V1",
      "owner_rec_parent_head":REC_PARENT,
      "source_rei_original_head":REI_ORIGINAL_HEAD,
      "source_rei_v2_head":REI_V2_OWNER_HEAD,
      "original_tar_sha256":ORIGINAL_TAR_SHA,
      "original_kernel_sha256":ORIGINAL_KERNEL_SHA,
      "v2_npz_sha256":SOURCE_V2_SHA,
      "accepted_original_ticks":[0,64,128,160],
      "owner_accepted_tick161":False,
      "v2_candidate_status":"NONAUTHORITATIVE_V2_SHADOW",
      "native_source_frozen_z_interval":list(z0),
      "native_source_H_s_inv_interval":[Hlo,Hhi],
      "native_source_frozen_volume_over_microtick":True,
      "native_source_max_W_volume_relative_discrepancy":max_vol_relative,
      "source_microtick_seconds":dt,
      "conditional_geometry":"OPTIONAL_THETA_EQUALS_3H_EXPANDING_MATERIAL_CELL_NOT_ORIGINAL_SOURCE_ADOPTION",
      "expansion_volume_inverse_factor_interval":[f_lo,f_hi],
      "conditional_geometry_relative_Gamma_change_interval":[f_lo-1,f_hi-1],
      "cells":N,
      "volume_weighted_Gamma160_s_inv":av0,
      "volume_weighted_Gamma161_frozen_s_inv":av1f,
      "volume_weighted_Gamma161_expanded_s_inv":av1e,
      "volume_weighted_frozen_chem_delta_s_inv":[av1f[0]-av0[1],av1f[1]-av0[0]],
      "volume_weighted_expanding_total_delta_s_inv":[av1e[0]-av0[1],av1e[1]-av0[0]],
      "physical_sign_classes":cats,
      "chem_increase_to_geometry_decrease_strict_cells":flips,
      "source_csv_sha256":digest(p),
      "science_status":"DERIVED_SOURCE_CONDITIONAL_V2_MATERIAL_THOMSON_COLLISION_NOT_LOS_TAU",
      "physical_realizations":1,
      "source_original_26event_reintegrated":False,
      "source_original_rei_modified":False,
      "REI_canonical_DAG":"28/88",
      "REI_working_DAG":"33/88",
      "REI_physical_fast_DAG":"4/7",
      "REC_H5_physical_DAG":"0/313",
      "production":"HOLD",
    }
    (out/"SCIENCE_RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in (
        "source_csv_sha256","conditional_geometry_relative_Gamma_change_interval",
        "volume_weighted_Gamma160_s_inv","volume_weighted_Gamma161_frozen_s_inv",
        "volume_weighted_Gamma161_expanded_s_inv","physical_sign_classes",
        "chem_increase_to_geometry_decrease_strict_cells")},sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--rec",required=True,type=Path)
    p.add_argument("--rei",required=True,type=Path)
    p.add_argument("--candidate",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.rec,a.rei,a.candidate,a.out)

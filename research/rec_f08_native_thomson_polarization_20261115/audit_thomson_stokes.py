#!/usr/bin/env python3
"""Independent tensor-coherency audit of actual original F08 native Thomson source.

Physical-check path is deliberately different from producer's spin phase
matrices. Read 81920 source ray records and directly form two linear
polarization coherency intensities in outgoing tangent frame.
No original BASS runtime re-execution needed for this audit.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path
import numpy as np

Q_SHA="a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92"
CAPTURE_SHA="70ea9b3b4ffbe6b0b25c15a17182c3170b0f96fdb5d42209f90bff27d0bbe2a1"
NATIVE_SHA="75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"
DT=625000000.0
N=128
RATE=29979245800.0*6.6524587051e-25
BRANCHES=("S0_BI","S0_FLRW")
MODES=("CHARACTERISTIC","ORIGINAL_HAT")
COLS=("native_unscattered_photons_per_H","native_unscattered_energy_eV_per_H",
      "quadrupole_exact_projected_photons_per_H",
      "quadrupole_exact_projected_energy_eV_per_H",
      "Thomson_scattering_in_photons_per_H",
      "Thomson_scattering_in_energy_eV_per_H",
      "Thomson_delta_photons_per_H","Thomson_delta_energy_eV_per_H",
      "generated_Q_photons_per_H","generated_U_photons_per_H",
      "generated_Q_energy_eV_per_H","generated_U_energy_eV_per_H")
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def fail(condition,label):
 if not condition:raise AssertionError("REC199_C9_INDEPENDENT_"+label)
def fsum(v):return float(math.fsum(map(float,np.asarray(v).ravel())))
def source(unit):
 src=Path(unit)/"source_inputs"
 f=src/"F08_ORIGINAL_SOURCE_Q128.csv"
 cap=src/"ORIGINAL_NATIVE_F08_640STEP_128RAY_PHOTON_ANGLES.csv.gz"
 lock=json.loads((src/"NATIVE_CAPTURE_RESULT.json").read_text())
 fail(sha(f)==Q_SHA,"Q_SOURCE_BYTE")
 fail(sha(cap)==CAPTURE_SHA,"NATIVE_81920_BYTE")
 fail(lock["original_native_runs"]==640 and
      lock["source_native_640_output_sha256"]==NATIVE_SHA,"NATIVE_640_REPLAY")
 with f.open(newline="") as inp:
  rows=list(csv.DictReader(inp))
 fail(len(rows)==N,"Q128")
 q=np.array([[float(r[k]) for k in ("qx","qy","qz")]
             for r in rows],dtype=float)
 fail(all(int(r["ray"])==i for i,r in enumerate(rows)),"Q_ORDER")
 return q,cap
def weights(q):
 # Deliberately derive the l2-corrected weights from numerical raw q,
 # not the producer's hardcoded alpha=4/63.
 z=q[:,2]
 mu2=float(np.mean(z*z))
 mu4=float(np.mean(z**4))
 alpha=(1/3-mu2)/(mu4-mu2*mu2)
 w=(1+alpha*(z*z-mu2))/len(q)
 fail(w.min()>0,"POSITIVE_Q")
 M=q.T@(w[:,None]*q)
 fail(abs(fsum(w)-1)<5e-15 and
      np.max(np.abs(M-np.eye(3)/3))<4e-15,"ANGLE_L0_L2")
 return w,alpha
def compare(a,b,reference,tag):
 fail(math.isfinite(a) and math.isfinite(b) and
      abs(a-b)<1e-12*max(reference,abs(a),abs(b),1e-300),
      "SOURCE_SCATTER_FORMULA_"+tag)
def audit(unit:Path,results:Path,output:Path):
 unit,results,output=map(Path,(unit,results,output))
 fail(not output.exists(),"REFUSE_OVERWRITE")
 q,sourcepath=source(unit)
 w,alpha=weights(q)
 mu=q@q.T
 expected=("S0_BI","CHARACTERISTIC")
 sr=json.loads((results/"SCIENCE_RESULT.json").read_text())
 native_file=results/"NATIVE_F08_THOMSON_81920_ANGULAR_STOKES_SOURCE.csv.gz"
 stage_file=results/"NATIVE_F08_THOMSON_640_PHYSICAL_STAGE_BUDGET.csv.gz"
 fail(sha(native_file)==sr["source_ang_stokes_csv_sha256"],
      "PUBLISHED_ANGULAR_SOURCE_HASH")
 fail(sha(stage_file)==sr["source_stage_budget_csv_sha256"],
      "PUBLISHED_STAGE_HASH")
 fail(sr["source_original_81920_angle_capture_sha256"]==CAPTURE_SHA and
      sr["source_original_native_640step_sha256"]==NATIVE_SHA,
      "PUBLISHED_SOURCE_AUTHORITY")
 fail(sr["original_REI_F08_paired_runtime_owner"]=="HOLD" and
      sr["original_Rust_native_gas_updated_with_Thomson_scattering"] is False,
      "FALSE_OWNER_PROMOTION")
 with gzip.open(sourcepath,"rt",newline="") as f:
  original=list(csv.DictReader(f))
 with gzip.open(native_file,"rt",newline="") as f:
  published=list(csv.DictReader(f))
 with gzip.open(stage_file,"rt",newline="") as f:
  budgets=list(csv.DictReader(f))
 fail(len(original)==len(published)==640*N and len(budgets)==640,
      "ALL_ACTUAL_SOURCE_DATA")
 report={"total_ray_checks":0,"source_stage_count":0,
         "max_relative_to_scattered_intensity_IQU_discrepancy":0.0,
         "max_relative_to_total_original_photons_angular_number_mismatch":0.0,
         "maximum_source_linear_polarization_over_scattered_in":0.0,
         "max_flrw_source_polarization_fraction":0.0,
         "model_source_scattering_events_per_H":{},
         "native_original_640_source_sha256":NATIVE_SHA}
 for s in range(640):
  a=s*N;b=(s+1)*N
  orig=original[a:b];out=published[a:b]
  stage=budgets[s]
  name=(orig[0]["branch"],orig[0]["model"])
  fail(name[0] in BRANCHES and name[1] in MODES,"SOURCE_MODEL")
  k=int(orig[0]["step"])
  fail(k==s%160+1 and all(int(r["step"])==k for r in orig),
       "NATIVE_PROPER_STEP")
  t=k*DT
  p=float(orig[0]["thomson_probability_one_source_tick"])
  ne=float(orig[0]["native_gas_ne_cm3"])
  xe=float(orig[0]["native_gas_xe_per_H"])
  nh=float(orig[0]["native_gas_nH_cm3"])
  original_H=(1.01e-14,9.9e-15,1e-14) if name[0]=="S0_BI" else (1e-14,)*3
  theta=math.fsum(original_H)
  fail(abs(nh-(1e-4*math.exp(-theta*t)))<3e-14*nh,"SOURCE_NH_TIME")
  fail(abs(ne-nh*xe)<5e-14*ne,"SOURCE_NE_FROM_HHE")
  fail(abs(p-(-math.expm1(-RATE*ne*DT)))<4e-15*p,"NATIVE_PROPER_COLLISION")
  photons=np.array([float(r["original_photons_per_H"]) for r in orig])
  energies=np.array([float(r["original_energy_eV_per_H"]) for r in orig])
  fail(np.min(photons)>=0 and np.min(energies)>=0 and
       all(int(r["ray"])==i for i,r in enumerate(orig)),"SOURCE_RAY_ORDER")
  def proj(v):
   init=fsum(v)
   y=v*w*N
   return y*(init/fsum(y))
  pn=proj(photons)
  pe=proj(energies)
  dN=np.array([float(r["Thomson_delta_photons_per_H"]) for r in out])
  dE=np.array([float(r["Thomson_delta_energy_eV_per_H"]) for r in out])
  P_Q=np.array([float(r["generated_Q_photons_per_H"]) for r in out])
  P_U=np.array([float(r["generated_U_photons_per_H"]) for r in out])
  E_Q=np.array([float(r["generated_Q_energy_eV_per_H"]) for r in out])
  E_U=np.array([float(r["generated_U_energy_eV_per_H"]) for r in out])
  scatN=np.array([float(r["Thomson_scattering_in_photons_per_H"]) for r in out])
  scatE=np.array([float(r["Thomson_scattering_in_energy_eV_per_H"]) for r in out])
  for i,n in enumerate(q):
   # Independent tangent frame geometry (not producer's cross product).
   sxy=math.hypot(float(n[0]),float(n[1]))
   ea=np.array([n[2]*n[0]/sxy,n[2]*n[1]/sxy,-sxy])
   eb=np.array([-n[1]/sxy,n[0]/sxy,0.])
   A=q@ea;B=q@eb
   # Direct photon density-coherency 2x2: J_ab ∝ (delta_ab-(ea.qin)(eb.qin)).
   Jaa=p*.75*w[i]*fsum(pn*(1-A*A))
   Jbb=p*.75*w[i]*fsum(pn*(1-B*B))
   Jab=-p*.75*w[i]*fsum(pn*A*B)
   JaE=p*.75*w[i]*fsum(pe*(1-A*A))
   JbE=p*.75*w[i]*fsum(pe*(1-B*B))
   JabE=-p*.75*w[i]*fsum(pe*A*B)
   number_in=Jaa+Jbb; energy_in=JaE+JbE
   # Scale tiny Q/U discrepancies by incident scattered intensity, not Q itself.
   for label,x,y,scale in (
       ("I",scatN[i],number_in,number_in),
       ("Q",P_Q[i],Jaa-Jbb,number_in),
       ("U",P_U[i],2*Jab,number_in),
       ("E",scatE[i],energy_in,energy_in),
       ("Q_E",E_Q[i],JaE-JbE,energy_in),
       ("U_E",E_U[i],2*JabE,energy_in),
       ("dN",dN[i],number_in-p*pn[i],number_in),
       ("dE",dE[i],energy_in-p*pe[i],energy_in),
       ("Pn",float(out[i]["quadrupole_exact_projected_photons_per_H"]),pn[i],pn[i]),
       ("Pe",float(out[i]["quadrupole_exact_projected_energy_eV_per_H"]),pe[i],pe[i])):
    compare(x,y,scale,label)
    if label in ("I","Q","U","E","Q_E","U_E"):
     report["max_relative_to_scattered_intensity_IQU_discrepancy"]=max(
       report["max_relative_to_scattered_intensity_IQU_discrepancy"],
       abs(x-y)/max(scale,1e-300))
   fail(number_in>=0 and energy_in>=0 and
        math.hypot(P_Q[i],P_U[i])<=number_in*(1+1e-12),
        "STOKES_COHERENCY_PSD")
  fail(abs(fsum(dN))<1e-12*p*fsum(pn) and
       abs(fsum(dE))<1e-12*p*fsum(pe),"CONSERVATIVE_REDISRIBUTION")
  expected_events=p*fsum(photons)
  compare(float(stage["expected_scattering_events_per_H"]),expected_events,
          expected_events,"NATIVE_EVENT_TOTAL")
  compare(float(stage["max_fraction_polarization_of_scattered_in_photons"]),
          float(np.max(np.hypot(P_Q,P_U)/scatN)),1,"SOURCE_POL_FRACTION")
  if name[0]=="S0_FLRW":
   fail(float(np.max(np.hypot(P_Q,P_U)/scatN))<1e-12,"FLRW_ISOTROPIC_SOURCE_POL_ZERO")
  report["maximum_source_linear_polarization_over_scattered_in"]=max(
       report["maximum_source_linear_polarization_over_scattered_in"],
       float(np.max(np.hypot(P_Q,P_U)/scatN)))
  if name[0]=="S0_FLRW":
   report["max_flrw_source_polarization_fraction"]=max(
       report["max_flrw_source_polarization_fraction"],
       float(np.max(np.hypot(P_Q,P_U)/scatN)))
  report["model_source_scattering_events_per_H"][name[0]+"_"+name[1]]=(
       report["model_source_scattering_events_per_H"].get(name[0]+"_"+name[1],0.0)+expected_events)
  report["source_stage_count"]+=1
  report["total_ray_checks"]+=N
 fail(report["source_stage_count"]==640 and report["total_ray_checks"]==81920,
      "PHYSICAL_ROW_COUNT")
 for key,summary in sr["model_results"].items():
  compare(report["model_source_scattering_events_per_H"][key],
          summary["source_expected_scattering_events_per_H_sum"],
          summary["source_expected_scattering_events_per_H_sum"],
          "GLOBAL_TOTAL_SCATTER_EVENT_SOURCE")
 fail(sr["REI_canonical_DAG"]=="28/88" and sr["REC_H5_physical_DAG"]=="0/313"
      and sr["production"]=="HOLD","FALSE_CANONICAL_PROMOTION")
 report.update({
  "schema":"REC199_SOURCE_F08_REAL_640_NATIVE_STAGES_INDEPENDENT_TENSOR_COHERENCY_AUDIT_V1",
  "scattering_csv_sha256":sha(native_file),
  "physical_event_stage_sha256":sha(stage_file),
  "original_ray_capture_sha256":CAPTURE_SHA,
  "angular_quadrature_original_qz2":21/64,
  "moment_exact_weight_alpha":alpha,
  "original_BASS_F08_source":"PRESERVED",
  "original_Einstein_constrained_metric":"NOT_SUPPLIED",
  "true_polarized_Boltzmann_trajectory":"NOT_RUN",
  "original_Rust_feedback_from_Thomson":"NOT_RUN",
  "original_REI_F08_paired_runtime":"HOLD",
  "REI_canonical_DAG":"28/88",
  "REC_H5_physical_DAG":"0/313",
 })
 output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":"81920_ORIGINAL_SOURCE_SCATTER_STOKES_AUDIT_PASS",
     "stages":640,"rows":report["total_ray_checks"],
     "max_PhysicalIQU_error":report["max_relative_to_scattered_intensity_IQU_discrepancy"],
     "max_BI_polarization":report["maximum_source_linear_polarization_over_scattered_in"],
     "max_FLRW":report["max_flrw_source_polarization_fraction"]},sort_keys=True),flush=True)
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--unit",required=True,type=Path)
 p.add_argument("--results",required=True,type=Path)
 p.add_argument("--audit",required=True,type=Path)
 a=p.parse_args()
 audit(a.unit,a.results,a.audit)

#!/usr/bin/env python3
"""Original native REI F08 S0 photons -> Thomson I,Q,U single-scatter sources.

Uses actual 640 native Rust stage angular photon-survivor fields from
BASS #328 restored and rerun byte-identical. No owner source or gas update.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math
from pathlib import Path
import numpy as np

N=128
STEPS=160
DT=625000000.0
C_SIGMA=29979245800.0*6.6524587051e-25
ANGULAR_CAPTURE_SHA="70ea9b3b4ffbe6b0b25c15a17182c3170b0f96fdb5d42209f90bff27d0bbe2a1"
Q_SHA="a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92"
NATIVE_BASS_SHA="75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"
MODELS=(("S0_BI","CHARACTERISTIC"),("S0_BI","ORIGINAL_HAT"),
        ("S0_FLRW","CHARACTERISTIC"),("S0_FLRW","ORIGINAL_HAT"))
HEAD=("branch","model","step","proper_t_s","ray",
      "native_unscattered_photons_per_H","native_unscattered_energy_eV_per_H",
      "quadrupole_exact_projected_photons_per_H",
      "quadrupole_exact_projected_energy_eV_per_H",
      "Thomson_scattering_in_photons_per_H",
      "Thomson_scattering_in_energy_eV_per_H",
      "Thomson_delta_photons_per_H","Thomson_delta_energy_eV_per_H",
      "generated_Q_photons_per_H","generated_U_photons_per_H",
      "generated_Q_energy_eV_per_H","generated_U_energy_eV_per_H",
      "single_scattering_probability",
      "proper_ne_cm_inv3","electron_temperature_K")
STAGES=("branch","model","step","proper_t_s","source_photons_per_H",
        "source_energy_eV_per_H","single_scattering_probability",
        "expected_scattering_events_per_H","expected_scattered_energy_eV_per_H",
        "max_absolute_delta_photons_per_H","max_absolute_delta_energy_eV_per_H",
        "sum_delta_N_per_H","sum_delta_energy_eV_per_H",
        "max_source_linear_polarization_per_H",
        "max_fraction_polarization_of_scattered_in_photons",
        "max_source_linear_energy_polarization_eV_per_H",
        "quadrupole_tensor_frobenius",
        "source_ray_photons_projection_L1_relative",
        "source_ray_energy_projection_L1_relative",
        "raw_equal_weight_phase_max_artificial_polarization_ratio")
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for a in iter(lambda:f.read(1<<20),b""):h.update(a)
 return h.hexdigest()
def must(ok,msg):
 if not ok:raise AssertionError("REC199_SOURCE_THOMSON_"+msg)
def fsum(x):return float(math.fsum(map(float,np.asarray(x).ravel())))
def source_q(unit):
 path=unit/"source_inputs/F08_ORIGINAL_SOURCE_Q128.csv"
 must(sha(path)==Q_SHA,"ORIGINAL_RAY_SHA")
 with path.open(newline="") as f:
  rows=list(csv.DictReader(f))
 must(len(rows)==N,"ORIGINAL_Q128_COUNT")
 q=np.zeros((N,3),dtype=np.float64)
 for i,r in enumerate(rows):
  must(int(r["ray"])==i,"Q128_ORDER")
  q[i]=[float(r[k]) for k in ("qx","qy","qz")]
 must(np.max(np.abs(np.sum(q*q,axis=1)-1))<3e-15,"Q_UNIT_NORM")
 return q
def kernel(q):
 """Source-specific positive quadrupole exact phase quadrature and Stokes matrices."""
 z=q[:,2]; z2=z*z
 must(abs(float(np.mean(z2))-21/64)<2e-15,"ORIGINAL_Q_MOMENT2")
 must(abs(float(np.mean(z2*z2))-777/4096)<2e-15,"ORIGINAL_Q_MOMENT4")
 weights=(1+(4/63)*(z2-21/64))/N
 must(np.all(weights>0) and abs(fsum(weights)-1)<3e-15,"POSITIVE_L0_WEIGHTS")
 M=q.T@(weights[:,None]*q)
 must(np.max(np.abs(M-np.eye(3)/3))<3e-15,"MOMENT_EXACT_L2")
 mu=q@q.T
 phase=.75*weights[:,None]*(1+mu*mu)
 must(np.min(phase)>0,"POSITIVE_PHASE")
 must(np.max(np.abs(np.sum(phase,axis=0)-1))<4e-15,"PHOTON_NUMBER_COLUMN_STOCHASTIC")
 must(np.max(np.abs(phase@weights-weights))<3e-15,"ISOTROPIC_FIXED_POINT")
 e_phi=np.zeros_like(q)
 e_phi[:,0]=-q[:,1]
 e_phi[:,1]=q[:,0]
 e_phi/=np.linalg.norm(e_phi,axis=1)[:,None]
 e_theta=np.cross(e_phi,q)
 must(np.max(np.abs(np.sum(e_theta*e_phi,axis=1)))<3e-15,"TETRAD_ORTHOGONAL")
 must(np.max(np.abs(np.linalg.norm(e_theta,axis=1)-1))<3e-15,"TETRAD_UNIT")
 A=e_phi@q.T
 B=e_theta@q.T
 qmat=.75*weights[:,None]*(A*A-B*B)
 umat=-1.5*weights[:,None]*(A*B)
 # Native q midpoint quadrature **without** l2 correction leaks
 # false spin polarization into an isotropic, unpolarized field.
 rawI=.75/N*(1+mu*mu)
 rawQ=.75/N*(A*A-B*B)
 rawU=-1.5/N*A*B
 iso=np.full(N,1/N)
 raw_ratio=np.max(np.hypot(rawQ@iso,rawU@iso)/(rawI@iso))
 must(.004<raw_ratio<.006,"ORIGINAL_RAW_SPIN_LEAKAGE_NEGATIVE_CONTROL")
 must(np.max(np.hypot(qmat@weights,umat@weights))<3e-15,"ISOTROPIC_ZERO_POLARIZATION")
 return weights,phase,qmat,umat,float(raw_ratio),M
def project(native,weights):
 native=np.asarray(native,dtype=np.float64)
 must(native.shape==(N,) and np.isfinite(native).all() and
      np.all(native>=0),"SOURCE_PHOTON_SPECTRUM")
 total=fsum(native)
 must(total>0,"POSITIVE_NATIVE_SOURCE_PHOTONS")
 estimate=native*(weights*N)
 normalization=total/fsum(estimate)
 projected=estimate*normalization
 must(np.min(projected)>=0 and abs(fsum(projected)-total)<=
      5e-14*max(total,1e-100),"SOURCE_NUMBER_PROJECTION_CONSERVES")
 L1=fsum(np.abs(projected-native))/total
 return projected,total,L1
def scatter_step(q,geom,source):
 weights,P,Qmat,Umat,raw_ratio,M=geom
 nativeN=np.asarray([float(r["original_photons_per_H"]) for r in source],dtype=float)
 nativeE=np.asarray([float(r["original_energy_eV_per_H"]) for r in source],dtype=float)
 n,ntot,nL1=project(nativeN,weights)
 e,etot,eL1=project(nativeE,weights)
 p=float(source[0]["thomson_probability_one_source_tick"])
 ne=float(source[0]["native_gas_ne_cm3"])
 temp=float(source[0]["native_gas_T_K"])
 must(math.isfinite(p) and 0<p<1e-7 and ne>0 and temp>0,"SOURCE_PHOTON_CLOCK_RATE")
 must(abs(p-(-math.expm1(-C_SIGMA*ne*DT)))<4e-18,"SOURCE_NATIVE_GAMMA")
 for j,r in enumerate(source):
  must(int(r["ray"])==j and
      float(r["thomson_probability_one_source_tick"])==p and
      float(r["native_gas_ne_cm3"])==ne and
      float(r["native_gas_T_K"])==temp,"ALL_RAYS_IDENTICAL_SOURCE_TIME")
 scatteredN=p*(P@n); scatteredE=p*(P@e)
 deltaN=scatteredN-p*n; deltaE=scatteredE-p*e
 outN=n+deltaN; outE=e+deltaE
 qN=p*(Qmat@n);uN=p*(Umat@n)
 qE=p*(Qmat@e);uE=p*(Umat@e)
 must(np.min(outN)>=0 and np.min(outE)>=0,"POSITIVE_POST_SCATTER")
 must(abs(fsum(deltaN))<1e-12*p*ntot and
      abs(fsum(deltaE))<1e-12*p*etot,"THOMSON_NUMBER_ENERGY_LEDGER")
 must(np.max(np.hypot(qN,uN)-scatteredN)<1e-12*max(float(np.max(scatteredN)),1e-300),
      "THOMSON_PHOTON_STOKES_PSD")
 must(np.max(np.hypot(qE,uE)-scatteredE)<1e-12*max(float(np.max(scatteredE)),1e-300),
      "THOMSON_ENERGY_STOKES_PSD")
 tensor=(q.T@(n[:,None]*q))/ntot-np.eye(3)/3
 relativeP=float(np.max(np.hypot(qN,uN)/scatteredN))
 stage={
  "source_photons_per_H":ntot,"source_energy_eV_per_H":etot,
  "single_scattering_probability":p,
  "expected_scattering_events_per_H":p*ntot,
  "expected_scattered_energy_eV_per_H":p*etot,
  "max_absolute_delta_photons_per_H":float(np.max(np.abs(deltaN))),
  "max_absolute_delta_energy_eV_per_H":float(np.max(np.abs(deltaE))),
  "sum_delta_N_per_H":fsum(deltaN),
  "sum_delta_energy_eV_per_H":fsum(deltaE),
  "max_source_linear_polarization_per_H":float(np.max(np.hypot(qN,uN))),
  "max_fraction_polarization_of_scattered_in_photons":relativeP,
  "max_source_linear_energy_polarization_eV_per_H":float(np.max(np.hypot(qE,uE))),
  "quadrupole_tensor_frobenius":float(np.linalg.norm(tensor)),
  "source_ray_photons_projection_L1_relative":nL1,
  "source_ray_energy_projection_L1_relative":eL1,
  "raw_equal_weight_phase_max_artificial_polarization_ratio":raw_ratio
 }
 arrays=(nativeN,nativeE,n,e,scatteredN,scatteredE,deltaN,deltaE,
         qN,uN,qE,uE)
 return stage,arrays
def write_gzip_header(path,headers):
 fd=path.open("xb")
 gz=gzip.GzipFile(fileobj=fd,mode="wb",filename="",mtime=0,compresslevel=6)
 writer=io.TextIOWrapper(gz,encoding="ascii",newline="",write_through=True)
 out=csv.writer(writer,lineterminator="\n")
 out.writerow(headers)
 return fd,gz,writer,out
def run(unit:Path,outdir:Path):
 unit,outdir=Path(unit),Path(outdir)
 must(not outdir.exists(),"NO_RESULT_OVERWRITE")
 data=unit/"source_inputs"
 capture=data/"ORIGINAL_NATIVE_F08_640STEP_128RAY_PHOTON_ANGLES.csv.gz"
 meta=json.loads((data/"NATIVE_CAPTURE_RESULT.json").read_text())
 must(sha(capture)==ANGULAR_CAPTURE_SHA and
      meta["source_native_640_output_sha256"]==NATIVE_BASS_SHA and
      meta["original_native_runs"]==640,"ORIGINAL_NATIVE_SOURCE_LOCK")
 q=source_q(unit); geom=kernel(q)
 outdir.mkdir(parents=True)
 output=outdir/"NATIVE_F08_THOMSON_81920_ANGULAR_STOKES_SOURCE.csv.gz"
 stageout=outdir/"NATIVE_F08_THOMSON_640_PHYSICAL_STAGE_BUDGET.csv.gz"
 fd,gz,t,writer=write_gzip_header(output,HEAD)
 stage_records=[]
 ntotal=0
 last=None
 current=[]
 def flush():
  nonlocal ntotal
  if not current:return
  b,m,step=last
  must(len(current)==N,"SOURCE_128_RAYS_PER_STAGE")
  for j,r in enumerate(current):
   must(r["branch"]==b and r["model"]==m and
        int(r["step"])==step and
        float(r["proper_t_s"])==step*DT and int(r["ray"])==j,
        "SOURCE_ORIGINAL_CLOCK_ORDER")
  rec,arrays=scatter_step(q,geom,current)
  st=[b,m,step,step*DT]+[rec[k] for k in STAGES[4:]]
  stage_records.append(st)
  for j in range(N):
   source_values=[b,m,step,step*DT,j]
   phys=[float(arr[j]) for arr in arrays]
   p=float(current[j]["thomson_probability_one_source_tick"])
   ne=float(current[j]["native_gas_ne_cm3"])
   temp=float(current[j]["native_gas_T_K"])
   row=source_values+phys+[p,ne,temp]
   must(len(row)==len(HEAD),"OUTPUT_ROW_SCHEMA")
   writer.writerow([x if isinstance(x,str) or isinstance(x,int)
                   else format(float(x),".17e") for x in row])
   ntotal+=1
 try:
  with gzip.open(capture,"rt",newline="") as f:
   for r in csv.DictReader(f):
    key=(r["branch"],r["model"],int(r["step"]))
    if last!=key:
     flush()
     current=[]
     last=key
    current.append(r)
  flush()
 finally:
  t.flush();t.close();gz.close();fd.close()
 must(ntotal==4*STEPS*N and len(stage_records)==4*STEPS,
      "MISSING_ORIGINAL_SOURCE_640_STAGES")
 with stageout.open("xb") as fd2:
  with gzip.GzipFile(fileobj=fd2,mode="wb",filename="",mtime=0,compresslevel=6) as gz2:
   with io.TextIOWrapper(gz2,encoding="ascii",newline="",write_through=True) as f2:
    w=csv.writer(f2,lineterminator="\n")
    w.writerow(STAGES)
    for row in stage_records:
     w.writerow([x if isinstance(x,str) or isinstance(x,int)
         else format(float(x),".17e") for x in row])
 summaries={}
 for b,m in MODELS:
  rows=[r for r in stage_records if r[0]==b and r[1]==m]
  must(len(rows)==STEPS and [r[2] for r in rows]==list(range(1,STEPS+1)),
       "UNMATCHED_NATIVE_SOURCE_STEPS")
  indices={n:i for i,n in enumerate(STAGES)}
  def maxfield(name):return max(float(r[indices[name]]) for r in rows)
  def sumfield(name):return math.fsum(float(r[indices[name]]) for r in rows)
  summary={
   "source_native_original_steps":STEPS,
   "source_numerical_photons_per_H_end":float(rows[-1][indices["source_photons_per_H"]]),
   "native_scattering_probability_per_step_minmax":[minfield("single_scattering_probability",rows,indices),maxfield("single_scattering_probability")],
   "source_expected_scattering_events_per_H_sum":sumfield("expected_scattering_events_per_H"),
   "source_expected_scattered_energy_eV_per_H_sum":sumfield("expected_scattered_energy_eV_per_H"),
   "source_peak_polarization_fraction_scattered_in":maxfield("max_fraction_polarization_of_scattered_in_photons"),
   "source_last_step_polarization_fraction_scattered_in":float(rows[-1][indices["max_fraction_polarization_of_scattered_in_photons"]]),
   "source_max_P_photons_per_H":maxfield("max_source_linear_polarization_per_H"),
   "source_last_step_P_photons_per_H":float(rows[-1][indices["max_source_linear_polarization_per_H"]]),
   "source_max_quadrupole_tensor_frobenius":maxfield("quadrupole_tensor_frobenius"),
   "source_max_projection_N_L1":maxfield("source_ray_photons_projection_L1_relative"),
   "source_Thomson_sums_conserve_to":max(abs(float(r[indices["sum_delta_N_per_H"]])) for r in rows),
   }
  summaries[b+"_"+m]=summary
 w,P,Qmat,Umat,raw_ratio,matrix=geom
 result={
  "schema":"REC199_SOURCE_NATIVE_F08_S0_THOMSON_SPIN2_EVENT_V1",
  "source_original_BASS_head":"b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6",
  "source_original_REI_F08_pair_sha256":"0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8",
  "source_original_native_640step_sha256":NATIVE_BASS_SHA,
  "source_original_81920_angle_capture_sha256":ANGULAR_CAPTURE_SHA,
  "source_original_q128_sha256":Q_SHA,
  "source_native_actual_Rust_stages":640,
  "source_physics_actual_angular_rows":ntotal,
  "source_actual_photon_angles":N,
  "source_proper_dt_s":DT,
  "real_source_models":[list(x) for x in MODELS],
  "collision_weight_scheme":"POSITIVE_QUADRUPOLE_EXACT_L2_Q128",
  "original_native_equal_angle_z2":21/64,
  "native_unmodified_raw_isotropic_false_polar_fraction":raw_ratio,
  "corrected_moment_tensor":[list(map(float,row)) for row in matrix],
  "corrected_weights_minmax":[float(np.min(w)),float(np.max(w))],
  "phase_column_stochastic_max_abs":float(np.max(np.abs(np.sum(P,axis=0)-1))),
  "phase_isotropic_fixedpoint_max_abs":float(np.max(np.abs(P@w-w))),
  "spin_isotropic_null_max_abs":float(np.max(np.hypot(Qmat@w,Umat@w))),
  "single_scattering_is_post_original_absorption_Lie_split":True,
  "original_Rust_native_source_modified":False,
  "original_Rust_native_gas_updated_with_Thomson_scattering":False,
  "original_single_scatter_first_order_source_only":True,
  "Thomson_kn_and_electron_thermal_corrections":"NOT_APPLIED",
  "true_polarized_photon_Boltzmann_trajectory":"NOT_COMPUTED",
  "original_REI_F08_paired_runtime_owner":"HOLD",
  "source_original_F05_26event_gas_used":False,
  "model_results":summaries,
  "source_ang_stokes_csv_sha256":sha(output),
  "source_stage_budget_csv_sha256":sha(stageout),
  "REI_canonical_DAG":"28/88",
  "REI_working_DAG":"33/88",
  "PhysicalFast_DAG":"4/7",
  "REC_H5_physical_DAG":"0/313",
  "production":"HOLD",
 }
 summaryfile=outdir/"SCIENCE_RESULT.json"
 summaryfile.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":"REAL_ORIGINAL_81920_PHOTONS_THOMSON_AND_SPIN_SOURCE_PASS",
        "sha_angles":result["source_ang_stokes_csv_sha256"],
        "sha_stages":result["source_stage_budget_csv_sha256"],
        "raw_fake_polar_ratio":raw_ratio,
        "models":{k:{"pmax":v["source_peak_polarization_fraction_scattered_in"],
                     "pend":v["source_last_step_polarization_fraction_scattered_in"],
                     "scatcount":v["source_expected_scattering_events_per_H_sum"]}
                   for k,v in summaries.items()}},sort_keys=True),flush=True)
 return result
def minfield(name,rows,indices):return min(float(r[indices[name]]) for r in rows)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--unit",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args();run(args.unit,args.out)

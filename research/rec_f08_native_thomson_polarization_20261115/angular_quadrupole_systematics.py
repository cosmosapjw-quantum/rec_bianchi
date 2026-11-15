#!/usr/bin/env python3
"""Independently fit the actual original F08 angular photon l=2 tensor.

Compare native-ray positive quadrupole-exact quadrature against least-squares
l≤2 harmonic reconstruction. Finite original q angular representation
systematic estimate; NOT a rigorous continuum angular convergence bound.
"""
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path
import numpy as np
SOURCE="70ea9b3b4ffbe6b0b25c15a17182c3170b0f96fdb5d42209f90bff27d0bbe2a1"
Q="a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92"
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def check(cond,msg):
 if not cond:raise AssertionError("REC199_ANGULAR_SENSITIVITY_"+msg)
def quadrupole_fit(q,weights,native,X):
 I=128*native
 wc=weights*I
 Qweight=(q.T@(wc[:,None]*q))/np.sum(wc)-np.eye(3)/3
 v=np.linalg.lstsq(X,I,rcond=None)[0]
 i0,a,b,c,d,e=v[0],v[4],v[5],v[6],v[7],v[8]
 S=np.array([[a,c/2,d/2],[c/2,b,e/2],[d/2,e/2,-a-b]])
 Qls=2*S/(15*i0)
 diff=float(np.linalg.norm(Qweight-Qls))
 norm=float(np.linalg.norm(Qweight))
 return norm,float(np.linalg.norm(Qls)),diff,diff/max(norm,1e-300)
def run(unit,out):
 unit,out=Path(unit),Path(out)
 if out.exists():raise FileExistsError("NO_HARMONIC_OVERWRITE")
 src=unit/"source_inputs"
 qfile=src/"F08_ORIGINAL_SOURCE_Q128.csv"
 photon=src/"ORIGINAL_NATIVE_F08_640STEP_128RAY_PHOTON_ANGLES.csv.gz"
 check(sha(qfile)==Q and sha(photon)==SOURCE,"ORIGINAL_SOURCE_BYTE")
 with qfile.open() as f:
  q=np.array([[float(r[k]) for k in ("qx","qy","qz")]
      for r in csv.DictReader(f)],dtype=float)
 z=q[:,2]
 weights=(1+(4/63)*(z*z-21/64))/128
 check(np.max(np.abs(q.T@(weights[:,None]*q)-np.eye(3)/3))<4e-15,"L2_QUADRUPOLE")
 X=np.column_stack((np.ones(len(q)),q,q[:,0]**2-q[:,2]**2,
   q[:,1]**2-q[:,2]**2,q[:,0]*q[:,1],q[:,0]*q[:,2],q[:,1]*q[:,2]))
 rows=[]
 with gzip.open(photon,"rt") as f:
  for r in csv.DictReader(f):rows.append(r)
 check(len(rows)==640*128,"NATIVE_SOURCE_RAY_COUNT")
 models={}
 data=[]
 anomalies=[]
 for k in range(640):
  stage=rows[k*128:(k+1)*128]
  b,mode,t=stage[0]["branch"],stage[0]["model"],int(stage[0]["step"])
  n=np.array([float(r["original_photons_per_H"]) for r in stage],dtype=float)
  e=np.array([float(r["original_energy_eV_per_H"]) for r in stage],dtype=float)
  check(np.min(n)>0 and np.min(e)>0,"POSITIVE_NATIVE_PHOTONS")
  nums=quadrupole_fit(q,weights,n,X)
  ens=quadrupole_fit(q,weights,e,X)
  data.append({"branch":b,"model":mode,"step":t,
       "source_number_quadrupole_weighted":nums[0],
       "source_number_quadrupole_l2fit":nums[1],
       "source_number_quadrupole_absolute_diff":nums[2],
       "source_number_quadrupole_relative_method_diff":nums[3],
       "source_energy_quadrupole_weighted":ens[0],
       "source_energy_quadrupole_l2fit":ens[1],
       "source_energy_quadrupole_absolute_diff":ens[2],
       "source_energy_quadrupole_relative_method_diff":ens[3]})
  key=b+"_"+mode
  models.setdefault(key,[]).append(data[-1])
 for name,stages in models.items():
  check(len(stages)==160,"FULL_SOURCE_STEP_COUNT")
  if name.startswith("S0_BI"):
   for st in stages:
    for channel in ("number","energy"):
     amplitude=st["source_"+channel+"_quadrupole_weighted"]
     relative=st["source_"+channel+"_quadrupole_relative_method_diff"]
     if amplitude>1e-12 and relative>=.03:
      anomalies.append({"source_model":name,"step":st["step"],
          "observable":channel,
          "quadrupole_frobenius":amplitude,
          "absolute_method_difference":st["source_"+channel+"_quadrupole_absolute_diff"],
          "relative_method_difference":relative,
          "predeclared_three_percent_gate":"FAIL"})
  else:
   for st in stages:
    check(st["source_number_quadrupole_weighted"]<5e-14 and
          st["source_energy_quadrupole_weighted"]<5e-14,
          "FLRW_FALSE_QUADRUPOLE")
 summary={}
 for name,stages in models.items():
  tail=stages[-1]
  summary[name]={
   "at_step160_number_weighted_quadrupole":tail["source_number_quadrupole_weighted"],
   "at_step160_number_harmonic_l2_quadrupole":tail["source_number_quadrupole_l2fit"],
   "at_step160_number_relative_angular_method_difference":
      tail["source_number_quadrupole_relative_method_diff"],
   "max_number_relative_angular_method_difference":max(s["source_number_quadrupole_relative_method_diff"]
       for s in stages if s["source_number_quadrupole_weighted"]>1e-12)
       if name.startswith("S0_BI") else None,
   "at_step160_energy_relative_angular_method_difference":
      tail["source_energy_quadrupole_relative_method_diff"],
   "max_energy_relative_angular_method_difference":max(s["source_energy_quadrupole_relative_method_diff"]
       for s in stages if s["source_energy_quadrupole_weighted"]>1e-12)
       if name.startswith("S0_BI") else None,
  }
 out.mkdir(parents=True)
 import io
 p=out/"ORIGINAL_F08_NATIVE_640_STAGE_ANGULAR_QUADRUPOLE_SENSITIVITY.csv.gz"
 with p.open("xb") as f:
  with gzip.GzipFile(fileobj=f,filename="",mode="wb",mtime=0,compresslevel=6) as gz:
   with io.TextIOWrapper(gz,encoding="ascii",newline="",write_through=True) as fp:
    w=csv.DictWriter(fp,fieldnames=list(data[0]),lineterminator="\n")
    w.writeheader()
    for row in data:
     w.writerow({k:(v if isinstance(v,(str,int)) else format(v,".17e")) for k,v in row.items()})
 result={"schema":"REC199_NATIVE_ORIGINAL_F08_ANGULAR_QUADRUPOLE_HARMONIC_COMPARE_V1",
   "original_source_capture_sha256":SOURCE,"original_q128_sha256":Q,
   "source_native_stage_count":640,"original_rei_BASS_source":"F08_S0_ONLY",
   "comparison_method":"SOURCE_Q_L2_WEIGHTED_VERSUS_INDEPENDENT_LSQ_FIT",
   "harmonic_fitting_lmax":2,
   "method_systematic_is_heuristic_not_a_rigorous_spherical_quadrature_error_bound":True,
   "per_stage_csv_sha256":sha(p),"models":summary,
   "predeclared_three_percent_method_gate":"FAIL" if anomalies else "PASS",
   "method_gate_failed_observations":anomalies,
   "scientific_interpretation":"MEASURED_FINITE_ANGULAR_REPRESENTATION_SENSITIVITY_NOT_CERTIFIED_SYSTEMATIC_ERROR",
   "REI_canonical_DAG":"28/88","REC_H5_DAG":"0/313"}
 (out/"SYSTEMATIC_RESULT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":"REAL_F08_640_L2_METHOD_DIAGNOSTIC_REPORTED",
      "source_csv":result["per_stage_csv_sha256"],
      "predeclared_three_percent_method_gate":result["predeclared_three_percent_method_gate"],
      "exceptions":anomalies,
      "models":summary},sort_keys=True),flush=True)
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--unit",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();run(a.unit,a.out)

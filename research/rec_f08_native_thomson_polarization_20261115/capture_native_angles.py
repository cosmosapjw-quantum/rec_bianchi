#!/usr/bin/env python3
"""Read-only instrumented re-execution of original REI F08 S0 native Rust stages.

Records angle/energy resolved photon survivors emitted by the real BASS
continuous_s0 original code. No change to original Rust/gas step result.
"""
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,pathlib,subprocess,sys
import numpy as np

N=128; STEPS=160; DT=625000000.
DONOR_SHA="75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"
REI_PAIR="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
ORIGINAL_BASS_HEAD="b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6"
EXPECTED_Q_SHA="a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92"
C_SIGMA=29979245800.0*6.6524587051e-25
MODES=(("S0_BI","CHARACTERISTIC"),("S0_BI","ORIGINAL_HAT"),
       ("S0_FLRW","CHARACTERISTIC"),("S0_FLRW","ORIGINAL_HAT"))
FIELDS=("branch","model","step","proper_t_s","ray",
        "original_photons_per_H","original_energy_eV_per_H",
        "native_gas_xe_per_H","native_gas_T_K",
        "native_gas_nH_cm3","native_gas_ne_cm3","thomson_probability_one_source_tick")
def sha(path):
 h=hashlib.sha256()
 with pathlib.Path(path).open("rb") as f:
  for a in iter(lambda:f.read(1<<20),b""):h.update(a)
 return h.hexdigest()
def must(condition,msg):
 if not condition:raise AssertionError("REC199_ORIGINAL_NATIVE_CAPTURE_"+msg)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 must(spec is not None and spec.loader is not None,"SOURCE_MODULE")
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return m
def xe(gas):
 xh,xhe,xhe3=gas["x"]
 must(0<=xh<=1 and 0<=xhe<=1 and 0<=xhe3<=1 and xhe+xhe3<=1,
      "NATIVE_HHE_PHYSICAL_CONE")
 return xh+.083*(xhe+2*xhe3)
def cmp_num(a,b,name,rtol=2e-12):
 # Native donor numerical identity, not byte-level RNG identity.
 must(math.isfinite(a) and math.isfinite(b) and abs(a-b) <=
      rtol*max(abs(a),abs(b),1e-300),name)
def run(recovered,out,rust):
 recovered,out,rust=map(pathlib.Path,(recovered,out,rust))
 must(not out.exists(),"NO_OVERWRITE")
 research=recovered/"research"
 unit=research/"bass_rei_f08_s0_continuous_native_20261102"
 code=unit/"continuous_s0.py"
 donor=unit/"results/SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz"
 must(sha(donor)==DONOR_SHA,"ORIGINAL_BASS_DONOR_SHA")
 must(rust.is_file(),"RUST_SOURCE_BINARY_NOT_BUILT")
 driver=load("rec199_true_bass_continuous",code)
 sys.path.insert(0,str(unit))
 must(driver.BASE_HEAD=="4984b42a9ed4025e4b3f20a3a61355a448e522ab",
      "SOURCE_NATIVE_OWNER_PARENT")
 must(driver.SOURCE_REI_F08_PAIR==REI_PAIR,"ORIGINAL_F08_SOURCE_PAIR")
 must(driver.DT==DT and driver.CHECKPOINTS[-1]==STEPS,"ORIGINAL_SOURCE_CLOCK")
 from audit_continuous import original_source_locks
 must(original_source_locks()==[12,51,4],"SOURCE_67_BYTE_LOCKS")
 oldfn=driver.native_one
 out.mkdir(parents=True)
 native=out/"native_original_replayed"
 cp=out/"ORIGINAL_NATIVE_F08_640STEP_128RAY_PHOTON_ANGLES.csv.gz"
 groups={}
 completed=0
 with cp.open("xb") as fh:
  with gzip.GzipFile(fileobj=fh,mode="wb",filename="",mtime=0,compresslevel=6) as z:
   with io.TextIOWrapper(z,encoding="ascii",newline="",write_through=True) as f:
    w=csv.writer(f,lineterminator="\n")
    w.writerow(FIELDS)
    def instrument(exe,inp,output,stage,items):
     nonlocal completed
     b,mode=MODES[completed//STEPS]
     k=completed%STEPS+1
     must(abs(stage["t0"]-(k-1)*DT)<1e-4,"SOURCE_STAGE_CLOCK")
     result=oldfn(exe,inp,output,stage,items)
     must(len(result["survived"])==len(items),"NATIVE_PACKET_SURVIVOR_COUNT")
     n=np.zeros(N,dtype=np.float64)
     u=np.zeros(N,dtype=np.float64)
     for (idx,E,original_count),remaining in zip(items,result["survived"]):
      q=int(idx if mode=="CHARACTERISTIC" else idx[1])
      must(0<=q<N and original_count>=0 and remaining>=0 and E>0,
           "ORIGINAL_NATIVE_PHOTON_DOMAIN")
      n[q]+=remaining
      u[q]+=remaining*E
     t=k*DT
     x=xe(result["gas"])
     nh=float(stage["nh"])
     ne=nh*x
     p=-math.expm1(-C_SIGMA*ne*DT)
     must(math.isfinite(ne) and ne>0 and 0<p<1e-5,"NATIVE_THOMSON_RATE")
     for j in range(N):
      w.writerow((b,mode,k,format(t,".17e"),j,
        format(n[j],".17e"),format(u[j],".17e"),
        format(x,".17e"),format(float(result["temp"]),".17e"),
        format(nh,".17e"),format(ne,".17e"),format(p,".17e")))
     groups[(b,mode,k)]={"photons":float(math.fsum(n)),
                          "energy":float(math.fsum(u)),
                          "xe":x,"T":float(result["temp"]),
                          "stage_native_root_residual":result["residual"],
                          "p":p}
     completed+=1
     if k in (1,64,128,160):
      print("SOURCE_NATIVE_STAGE",b,mode,k,
            "N",groups[(b,mode,k)]["photons"],
            "T",result["temp"],"p",p,flush=True)
     return result
    driver.native_one=instrument
    try:
     output=driver.solve(STEPS,native,rust)
    finally:
     driver.native_one=oldfn
 must(completed==len(MODES)*STEPS and len(groups)==640,
      "ORIGINAL_640_NATIVE_STAGES_MISSING")
 must(output["physical_trajectory_rows"]==640 and
      output["original_rei_F08_pair"]==REI_PAIR,"NATIVE_640_SOURCE_RESULT")
 # Independently compare all original 640 gas+photon stage outputs with
 # BASS #328 byte-locked historical source receipt, not synthetic resets.
 with gzip.open(donor,"rt",newline="") as inp:
  old=list(csv.DictReader(inp))
 must(len(old)==640,"DONOR_640_LOCK")
 maximum={}
 for row in old:
  b=row["branch"];mode=row["model"];k=int(row["step"])
  rec=groups[(b,mode,k)]
  for name,a,bval in (
      ("photon_N",rec["photons"],float(row["N_photons_per_H"])),
      ("photon_U",rec["energy"],float(row["U_photons_ev_per_H"])),
      ("gas_T",rec["T"],float(row["T_K"])),
      ("gas_xe",rec["xe"],float(row["xHII"])+.083*(float(row["xHeII"])+2*float(row["xHeIII"])))):
   maximum[name]=max(maximum.get(name,0),abs(a-bval)/max(abs(a),abs(bval),1e-300))
   cmp_num(a,bval,name)
 # source true source output may be byte identical in fully comparable
 # runtime, but do not assert it if binary float dependencies differ.
 result={
  "schema":"REC199_REAL_REI_F08_S0_ALL128_ANGULAR_SURVIVORS_V1",
  "original_BASS_source_head":ORIGINAL_BASS_HEAD,
  "original_REI_F08_S0_pair_sha256":REI_PAIR,
  "original_BASS_640row_donor_sha256":DONOR_SHA,
  "original_native_Rust_executable_sha256":sha(rust),
  "original_native_source_locks":{"S0":12,"Rust":51,"photon":4},
  "original_native_runs":640,
  "true_native_source_photon_stage_rows":640*N,
  "source_proper_dt_s":DT,
  "source_original_gas_and_photons_replayed":True,
  "source_native_640_output_sha256":output["trajectory_sha256"],
  "max_relative_source_donor_discrepancies":maximum,
  "original_source_angular_survivors_sha256":sha(cp),
  "original_native_is_modified":False,
  "production":"HOLD","REI_canonical_DAG":"28/88",
  "REC_H5_physical_DAG":"0/313"
 }
 (out/"NATIVE_CAPTURE_RESULT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":"ORIGINAL_SOURCE_640_STAGES_81920_RAY_ROWS_PASS",
   "capture_sha":result["original_source_angular_survivors_sha256"],
   "native_photon_replay_sha":output["trajectory_sha256"],
   "donor_comparison":maximum},sort_keys=True),flush=True)
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--recovered",type=pathlib.Path,required=True)
 p.add_argument("--out",type=pathlib.Path,required=True)
 p.add_argument("--rust",type=pathlib.Path,required=True)
 a=p.parse_args();run(a.recovered,a.out,a.rust)

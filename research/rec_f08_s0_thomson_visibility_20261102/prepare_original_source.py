#!/usr/bin/env python3
"""Freeze exact pre-existing original REI F08 S0 BASS native gas and 128 q directions.

Reads donor BASS #328 source and its original source locks; no source mutation.
Research source data, not original F05.
"""
import argparse,csv,hashlib,importlib.util,json,pathlib,shutil,subprocess,sys
import numpy as np

BASS_HEAD="b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6"
DONOR_SHA="75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"
F08_PAIR="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def prepare(root:pathlib.Path,out:pathlib.Path):
 root=root.resolve();out=out.resolve()
 assert not out.exists() or not any(out.iterdir()),"REFUSE_NONEMPTY_INPUT_DIR"
 assert subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()==BASS_HEAD
 research=root/"research"
 unit=research/"bass_rei_f08_s0_continuous_native_20261102"
 donor=unit/"results/SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz"
 assert sha(donor)==DONOR_SHA
 summary=json.loads((unit/"results/RESULT.json").read_text())
 assert summary["trajectory_sha256"]==DONOR_SHA
 assert summary["original_rei_F08_pair"]==F08_PAIR
 assert summary["physical_trajectory_rows"]==640 and summary["steps_per_model"]==160
 sys.path.insert(0,str(research/"bass_rei_f08_s0_remap_support_20261101"))
 from spectral_support import original_checkpoint
 sys.path.insert(0,str(research/"bass_rei_f08_s0_source_photon_thomson_20261101"))
 from s0_source_photon_thomson import source_histories
 sys.path.insert(0,str(unit))
 from audit_continuous import original_source_locks
 assert original_source_locks()==[12,51,4]
 refs={b:original_checkpoint(b) for b in ("S0_BI","S0_FLRW")}
 q=np.asarray(refs["S0_BI"]["qhat"],dtype=np.float64)
 assert q.shape==(128,3) and np.array_equal(q,refs["S0_FLRW"]["qhat"])
 assert np.max(abs(np.sum(q*q,axis=1)-1))<3e-15
 histories=source_histories()
 H={b:list(map(float,histories[b].H)) for b in ("S0_BI","S0_FLRW")}
 assert H["S0_BI"]==[1.01e-14,9.9e-15,1e-14]
 assert H["S0_FLRW"]==[1e-14,1e-14,1e-14]
 out.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(donor,out/"F08_ORIGINAL_NATIVE_GAS_640.csv.gz")
 qp=out/"F08_ORIGINAL_SOURCE_Q128.csv"
 with qp.open("x",newline="",encoding="ascii") as f:
  w=csv.writer(f,lineterminator="\n")
  w.writerow(["ray","qx","qy","qz"])
  for i,xyz in enumerate(q):
   w.writerow([i,*[format(float(x),".17e") for x in xyz]])
 manifest={
 "schema":"REC198_ORIGINAL_F08_S0_NATIVE_REI_PHOTON_HHE_DONOR_V1",
 "bass_donor_repo":"cosmosapjw-quantum/BASS",
 "bass_donor_pr":328,"bass_donor_head":BASS_HEAD,
 "original_rei_F08_source_pair_sha256":F08_PAIR,
 "bass_donor_trajectory_sha256":DONOR_SHA,
 "frozen_trajectory_sha256":sha(out/"F08_ORIGINAL_NATIVE_GAS_640.csv.gz"),
 "original_source_q128_sha256":sha(qp),
 "donor_original_source_lock_counts":{"S0":12,"Rust":51,"photon_checkpoint":4},
 "source_proper_dt_s":625000000.0,
 "original_source_initial_nH_cm3":1e-4,
 "original_source_initial_HII":0.9,
 "original_source_initial_HeII":0.3,
 "original_source_initial_HeIII":0.6,
 "original_source_He_H_number":0.083,
 "H_per_s":H,
 "directions":128,
 "steps_per_model":160,
 "source_original_F08_owner_admission":"HOLD",
 "source_BASS_native_driver":"RESEARCH_ONLY_NOT_ORIGINAL_INTERVAL_CERTIFIED_OWNER",
 "original_F05_26event_source":"EXPLICITLY_NOT_USED",
 "source_data_is_public_and_physical":"ONE_BASS_SELF_EVOLVED_PHOTON_GAS_TRAJECTORY_PER_BACKGROUND_AND_SPECTRAL_MODEL"
 }
 (out/"SOURCE_AUTHORITY.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"donor_csv_sha":DONOR_SHA,"q_sha":manifest["original_source_q128_sha256"],
                   "H":H,"source_locks":[12,51,4],"gas_rows":640},sort_keys=True))
 return manifest
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--bass",required=True,type=pathlib.Path)
 p.add_argument("--out",required=True,type=pathlib.Path)
 a=p.parse_args();prepare(a.bass,a.out)

#!/usr/bin/env python3
"""Restore and byte-lock the real original BASS #328 F08 S0 native Rust photon gas.

Original BASS archive is preserved; output is isolated private recovery tree.
"""
import argparse,hashlib,io,json,pathlib,zipfile
BASS_INNER="dc48688e734838a0933fabe97025d7c354ccd972a03ecb8ca6e33be5460e0673"
DONOR="75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"
PAIR="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
GROUPS=(
 ("s0","bass_rei_f08_s0_source_photon_thomson_20261101/source_inputs","ORIGIN_SHA256SUMS.txt",12),
 ("rust","bass_rei_f08_native_hhe_firststage_20261101/original_rei_rust","original_source_sha256.txt",51),
 ("photon","bass_rei_f08_s0_remap_support_20261101/source_inputs","LOCKED_CHECKPOINT_SHA256SUMS.txt",4),
)
def sha(data):
 if isinstance(data,bytes):return hashlib.sha256(data).hexdigest()
 h=hashlib.sha256()
 with pathlib.Path(data).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def restore(archive,out):
 archive,out=pathlib.Path(archive),pathlib.Path(out)
 if out.exists():raise FileExistsError("REC199_NO_OVERWRITE_ORIGINAL_SOURCE_RECOVERY")
 with zipfile.ZipFile(archive) as outer:
  expected={}
  for line in outer.read("MANIFEST.sha256").decode().splitlines():
   a,b=line.split(maxsplit=1);expected[b]=a
  key="payload/BASS_REI_F08_S0_CONTINUOUS_NATIVE_HHE_20261102.zip"
  inner=outer.read(key)
  assert sha(inner)==expected[key]==BASS_INNER
  with zipfile.ZipFile(io.BytesIO(inner)) as z:
   assert z.testzip() is None and len(z.namelist())==106
   for name in z.namelist():
    p=pathlib.PurePosixPath(name)
    assert not p.is_absolute() and ".." not in p.parts
   out.mkdir(parents=True)
   z.extractall(out)
 research=out/"research"
 evidence={}
 for label,relative,manifest,n_expected in GROUPS:
  root=research/relative
  lines=(root/manifest).read_text().splitlines()
  assert len(lines)==n_expected,(label,len(lines))
  for line in lines:
   digest,name=line.split(maxsplit=1)
   assert sha(root/name)==digest,(label,name)
  evidence[label]=n_expected
 donor=research/"bass_rei_f08_s0_continuous_native_20261102/results/SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz"
 assert sha(donor)==DONOR
 summary=json.loads((research/"bass_rei_f08_s0_continuous_native_20261102/results/RESULT.json").read_text())
 assert summary["trajectory_sha256"]==DONOR
 assert summary["original_rei_F08_pair"]==PAIR
 assert summary["physical_trajectory_rows"]==640
 result={
 "schema":"REC199_F08_S0_ORIGINAL_BASS_SOURCE_RECOVERY_V1",
 "outer_archived_zip_sha256":sha(archive),
 "inner_source_zip_sha256":BASS_INNER,
 "original_BASS_donor_head":"b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6",
 "original_REI_F08_S0_pair_sha256":PAIR,
 "original_native_gas_640_sha256":DONOR,
 "original_source_locked_files":evidence,
 "original_source_modified":False,
 "original_Rust_full_640stage_execution":"NOT_RUN_YET",
 "REI_canonical_DAG":"28/88",
 "REC_H5_DAG":"0/313"
 }
 (out/"RECOVERY_RECEIPT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":"ORIGINAL_SOURCE_RESTORED_67_LOCKS_PASS",
                    "source_sha":BASS_INNER,"files":evidence,
                    "orig640":DONOR,"tree":str(out)},sort_keys=True),flush=True)
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--archive",required=True)
 p.add_argument("--out",required=True)
 a=p.parse_args()
 restore(a.archive,a.out)

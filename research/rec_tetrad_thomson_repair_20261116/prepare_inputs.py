#!/usr/bin/env python3
"""Restore this optional estimator's local inputs from the pinned parent PR files.

No downloading, no source mutation, no native simulation. The raw photon array is
already inherited from REC199; this change does not publish a second copy.
"""
from pathlib import Path
import argparse,hashlib,shutil
B=Path(__file__).resolve().parent
SOURCES={
 'F08_ORIGINAL_SOURCE_Q128.csv':'a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92',
 'ORIGINAL_NATIVE_F08_640STEP_128RAY_PHOTON_ANGLES.csv.gz':'70ea9b3b4ffbe6b0b25c15a17182c3170b0f96fdb5d42209f90bff27d0bbe2a1',
 'science_scenario_v1.json':'c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=B.parent/'rec_f08_native_thomson_polarization_20261115/source_inputs');a=p.parse_args()
 dest=B/'rec199/source_inputs';dest.mkdir(parents=True,exist_ok=True)
 for name,expected in SOURCES.items():
  source=(B/'source_inputs'/name) if name=='science_scenario_v1.json' else a.source_dir/name
  if digest(source)!=expected:raise ValueError('pinned source hash mismatch: '+name)
  target=dest/name
  if target.exists() and digest(target)!=expected:raise ValueError('refuse to overwrite different existing input: '+name)
  if not target.exists():shutil.copyfile(source,target)
 print('Three pinned inputs available; no source mutation or native replay.')
if __name__=='__main__':main()

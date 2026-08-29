#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FILES={"PACKAGE.json","BASS_TRANSFER_MATRIX.json","REC_REI_INTERFACE_BRIDGE.json","WORK_UNITS.json","IMPLEMENTATION_PLAN.md","CODEX_HANDOFF.md","validate_package.py"}
HEAD="4cd2c7bff00ca91c57997d7e6e1ff4c67f7fccd3"
TREE="3f8731cfab9c9493fcdaa18d855d95768eee1d47"
BRANCH="audit/ode-four-loop-external-audit-20260823"
BLOBS={
"src/full_bianchi_hyrec/trajectory/dynamic_macro_ownership.py":"a196840d164aa7497b27178c1a38ca0f9627c426",
"docs/PR05C2C1B2B1E1C_SPLIT_DOMAIN_REPLACEMENT_PLAN.md":"585b2474b4a98733637b98cf3678d8b86a0db27c",
"archive/expanded/Full_Bianchi_HyRec_PR05C2C1B2B1E1B0_dynamic_macro_ownership_no_go_v0_75/NUMERICAL_METRICS.json":"f38e08e54b899f50adc708078d517d716243d7a2"}
def fail(x): raise SystemExit("FAIL: "+x)
def dig(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(repo,*args):
 p=subprocess.run(["git","--no-replace-objects",*args],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 if p.returncode: fail("git "+" ".join(args)+": "+p.stderr.strip())
 return p.stdout.removesuffix("\n")
def local():
 entries={}
 for line in (ROOT/"MANIFEST.sha256").read_text().splitlines():
  if line.strip():
   d,n=line.split(maxsplit=1)
   if n in entries: fail("duplicate manifest entry")
   entries[n]=d
 if set(entries)!=FILES: fail("manifest closure")
 for n,d in entries.items():
  if dig(ROOT/n)!=d: fail("digest "+n)
 p=json.loads((ROOT/"PACKAGE.json").read_text())
 if p["package_id"]!="REC-BIANCHI-SPLIT-DOMAIN-BOOTSTRAP-20260829-R2": fail("package id")
 if p["exact_next_action"]!="REC-SPLIT-01_GENUINE_RED": fail("next action")
 if p["publication"]["base_head"]!=HEAD: fail("base head")
 if p["bass_method_transfer"]["claims_used"]!=["PASS_RF04_SCALAR_RAW_SLICE_PROOF","NO_PASS_RF04"]: fail("BASS transfer")
 b=json.loads((ROOT/"REC_REI_INTERFACE_BRIDGE.json").read_text())
 if b["rei_current_policy"]["silent_surrogate"]!="FORBIDDEN": fail("surrogate firewall")
def live(repo_arg):
 repo=Path(git(repo_arg,"rev-parse","--show-toplevel"))
 if git(repo,"rev-parse","--verify","refs/remotes/origin/"+BRANCH)!=HEAD: fail("audit branch moved")
 if git(repo,"rev-parse",HEAD+"^{tree}")!=TREE: fail("audit tree")
 for path,blob in BLOBS.items():
  if git(repo,"rev-parse",HEAD+":"+path)!=blob: fail("source blob "+path)
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--live",action="store_true");ap.add_argument("--repo",default=".");a=ap.parse_args()
 local()
 if a.live: live(Path(a.repo))
 print(json.dumps({"status":"PASS","package_id":"REC-BIANCHI-SPLIT-DOMAIN-BOOTSTRAP-20260829-R2","exact_next_action":"REC-SPLIT-01_GENUINE_RED","claim":"NO_FULL_DYNAMIC_MACRO","live":a.live},sort_keys=True))

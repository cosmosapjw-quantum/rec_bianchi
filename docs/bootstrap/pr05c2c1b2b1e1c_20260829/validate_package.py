#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,hashlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PACKAGE="REC-PR05C2C1B2B1E1C-AUDIT-RECOVERY-20260829-R2"
BASE="5a09f3797210284f83a1a1adb0e0092d1ac48475"; BASE_TREE="4002915ad851afc2ab71f94a882cc99d81748062"
AUDIT="4cd2c7bff00ca91c57997d7e6e1ff4c67f7fccd3"; AUDIT_TREE="3f8731cfab9c9493fcdaa18d855d95768eee1d47"
LEAVES={"src/full_bianchi_hyrec/recoil/nonlinear_bose_release.py": "912ca95df45b513aa6a8dd3c053a5823c1365f9b", "src/full_bianchi_hyrec/recoil/nonlinear_bose_runtime.py": "b77baa30f2dd98078e278cc6e29ee46f520f921b", "src/full_bianchi_hyrec/trajectory/adaptive_macro.py": "c8657fd2942b497bc794991005085bf6be80011a", "src/full_bianchi_hyrec/trajectory/causal_history.py": "144b2f908ffef0332e4dc1b8e0378ce63f5b1e26", "src/full_bianchi_hyrec/trajectory/characteristic_angular.py": "15979c93e8c7305ac9c3a178d6e095a21d12ef4d", "src/full_bianchi_hyrec/trajectory/pseudotransient_continuation.py": "96ce437d69fe5bc64e0ad65c78c49b1ab30deb7f", "tests/recoil/test_nonlinear_bose_release.py": "cb6c847ebe42afc9d17870329972a194298031bd", "tests/recoil/test_nonlinear_bose_runtime.py": "f85657b5ada849d8b3d3dc9f09c4a930240da092", "tests/trajectory/test_adaptive_canonical_macro.py": "adcc6d5deeabe1341333fe4f416f6f534e785f64", "tests/trajectory/test_causal_characteristic_history.py": "01bd4a2c41a87033840fead9be9e87f4efd24930", "tests/trajectory/test_characteristic_angular_solver.py": "63295005a5f4ee9e5efa182ed86a821b91af1ae0", "tests/trajectory/test_full_coupled_transport.py": "57b09121e7b2e19afd98fea8656fdff7a0e14b25", "tests/trajectory/test_pseudotransient_continuation.py": "ee5ba96bac6ab3d29160bfeb07692f1c0936651d"}
FILES={"PACKAGE.json","CODEX_HANDOFF.md","validate_package.py"}
def fail(x): raise SystemExit("FAIL: "+x)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(repo,*args):
 p=subprocess.run(["git","--no-replace-objects",*args],cwd=repo,text=True,
  stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 if p.returncode: fail("git "+" ".join(args)+": "+p.stderr.strip())
 return p.stdout.removesuffix("\n")
def local():
 entries={}
 for line in (ROOT/"MANIFEST.sha256").read_text().splitlines():
  if line.strip():
   d,n=line.split(maxsplit=1)
   if n in entries: fail("duplicate manifest")
   entries[n]=d
 if set(entries)!=FILES: fail("manifest closure")
 for n,d in entries.items():
  if sha(ROOT/n)!=d: fail("digest "+n)
 p=json.loads((ROOT/"PACKAGE.json").read_text())
 if p["package_id"]!=PACKAGE: fail("package id")
 if p["state"]["exact_next_action"]!="PR05C2C1B2B1E1C_BOOTSTRAP_RED": fail("next action")
 if p["extraction"]["blob_sha1"]!=LEAVES: fail("leaf map")
def live(repoarg):
 repo=Path(git(repoarg,"rev-parse","--show-toplevel"))
 if git(repo,"rev-parse",BASE+"^{tree}")!=BASE_TREE: fail("base tree")
 if git(repo,"rev-parse",AUDIT+"^{tree}")!=AUDIT_TREE: fail("audit tree")
 for path,blob in LEAVES.items():
  if git(repo,"rev-parse",AUDIT+":"+path)!=blob: fail("audit leaf "+path)
  if git(repo,"rev-parse","HEAD:"+path)!=blob: fail("extracted leaf "+path)
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--live",action="store_true");ap.add_argument("--repo",default=".");a=ap.parse_args()
 local()
 if a.live: live(Path(a.repo))
 print(json.dumps({"status":"PASS","package_id":PACKAGE,"leaf_count":len(LEAVES),
 "exact_next_action":"PR05C2C1B2B1E1C_BOOTSTRAP_RED","claim":"NO_PASS_SPLIT_DOMAIN_REPLACEMENT","live":a.live},sort_keys=True))

#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

AUDIT_HEAD='4cd2c7bff00ca91c57997d7e6e1ff4c67f7fccd3'
AUDIT_TREE='3f8731cfab9c9493fcdaa18d855d95768eee1d47'
PKG_BRANCH='agent/plans/rec-split-domain-bootstrap-20260829-r1'
PKG_PREFIX='docs/bootstrap/rec_split_domain_bootstrap_20260829/'
HYREC_SHA='48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27'
ROOT=Path(__file__).resolve().parent

def fail(msg): raise SystemExit('FAIL: '+msg)
def git(repo,*args):
 p=subprocess.run(['git','--no-replace-objects',*args],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 if p.returncode: fail('git '+' '.join(args)+': '+p.stderr.strip())
 return p.stdout.strip()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def local():
 for name in ['PACKAGE.json','REC_REI_INTERFACE_BRIDGE.json','WORK_UNITS.json','BASS_TRANSFER_MATRIX.json']:
  json.loads((ROOT/name).read_text())
 package=json.loads((ROOT/'PACKAGE.json').read_text())
 units=json.loads((ROOT/'WORK_UNITS.json').read_text())
 if package['audit_source']['head']!=AUDIT_HEAD or package['audit_source']['tree']!=AUDIT_TREE: fail('audit identity')
 if units['exact_next_action']!='REC-BOOT-00': fail('next action')
 if package['claims']['current']!='HOLD_BEFORE_SPLIT_DOMAIN_REPLACEMENT': fail('claim boundary')
def live(repo_arg):
 repo=Path(git(repo_arg,'rev-parse','--show-toplevel'))
 pkg=git(repo,'rev-parse','--verify','refs/remotes/origin/'+PKG_BRANCH)
 audit=git(repo,'rev-parse','--verify','refs/remotes/origin/audit/ode-four-loop-external-audit-20260823')
 if audit!=AUDIT_HEAD or git(repo,'rev-parse',audit+'^{tree}')!=AUDIT_TREE: fail('audit ref moved')
 base=git(repo,'merge-base','refs/remotes/origin/main',pkg)
 changed=git(repo,'diff','--name-only',base+'..'+pkg).splitlines()
 if not changed or any(not p.startswith(PKG_PREFIX) for p in changed): fail('package changed-path closure')
 archive=repo/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
 if not archive.is_file() or sha(archive)!=HYREC_SHA: fail('canonical HyRec archive')
 print(json.dumps({'status':'PASS','package_head':pkg,'implementation_base':base,'changed_paths':len(changed),'exact_next_action':'REC-BOOT-00'}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--live',action='store_true');ap.add_argument('--repo',default='.')
 a=ap.parse_args();local();
 if a.live: live(a.repo)
 else: print(json.dumps({'status':'PASS','exact_next_action':'REC-BOOT-00','live':False}))

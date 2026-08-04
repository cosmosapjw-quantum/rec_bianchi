#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--quick',action='store_true')
    ap.add_argument('--all',action='store_true')
    ap.add_argument('--scientific',action='store_true')
    args=ap.parse_args()
    state=json.loads((ROOT/'state/PROJECT_STATE.json').read_text())
    assert state['current_durable_stage']['artifact'].endswith('v0_45')
    index=json.loads((ROOT/'state/BUNDLE_INDEX.json').read_text())
    missing=[]; bad=[]
    for row in index:
        p=ROOT/'archive/bundles'/row['bundle']
        if not p.exists(): missing.append(row['bundle']); continue
        if sha(p)!=row['sha256']: bad.append(row['bundle'])
        if args.all:
            with zipfile.ZipFile(p) as zf:
                member=zf.testzip()
                if member: bad.append(f"{row['bundle']}:{member}")
    assert not missing, missing
    assert not bad, bad
    if args.all or args.scientific:
        command=[sys.executable,'-m','pytest','-q']
        if not args.scientific:
            command += ['-m','not slow']
        cp=subprocess.run(command,cwd=ROOT)
        if cp.returncode: raise SystemExit(cp.returncode)
    print(json.dumps({'status':'PASS','bundle_count':len(index),'mode':'scientific' if args.scientific else ('all' if args.all else 'quick')}))
if __name__=='__main__': main()

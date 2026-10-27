#!/usr/bin/env python3
"""Restore exact omitted immutable input NPZ from the full S0 ZIP, locally only."""
import argparse,hashlib,json,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--s0',type=Path,required=True);p.add_argument('--unit-root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();u=a.unit_root.resolve();m=json.loads((u/'delivery/INPUT_RESTORE_MAPPING.json').read_text());b=a.s0.read_bytes()
if hashlib.sha256(b).hexdigest()!=m['full_S0']['sha256'] or len(b)!=m['full_S0']['bytes']:raise SystemExit('S0 byte identity mismatch')
with zipfile.ZipFile(a.s0) as z:
 if z.testzip() is not None:raise SystemExit('S0 CRC failure')
 for e in m['binary_inputs']:
  dst=u/e['local_unit_path'];v=z.read(e['S0_member'])
  if len(v)!=e['bytes'] or hashlib.sha256(v).hexdigest()!=e['sha256']:raise SystemExit('Input identity mismatch: '+e['local_unit_path'])
  if dst.exists():
   if dst.read_bytes()!=v:raise SystemExit('Refusing to overwrite different existing input: '+str(dst))
  else:dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(v)
  print(e['local_unit_path']+' VERIFIED')
print('PASS: five immutable NPZ inputs restored/verified; no scientific calculation or network operation')

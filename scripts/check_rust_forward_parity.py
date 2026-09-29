#!/usr/bin/env python3
"""Check raw Rust fixed-source outputs against independent frozen references.

Default invokes Cargo once and preserves the exact input/output/exit receipt.
--self-test exercises this Python checker only; it NEVER certifies Rust parity.
No runtime dependency is added to the Python package defaults.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/rust_forward'
TOLERANCE = 4096 * sys.float_info.epsilon
SCHEMA = 'REC_HE_OBSERVABLES_V2'


class VerificationError(ValueError):
    """An input, output, schema, execution, or numerical check failed."""


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def finite_number(x: object) -> bool:
    return type(x) in (int,float) and math.isfinite(x)


def compare_component(actual: float, expected: float, reference_gross: float,
                      tol: float = TOLERANCE) -> bool:
    if not all(finite_number(x) for x in (actual,expected,reference_gross,tol)):
        return False
    if reference_gross < 0 or tol < 0:
        return False
    if reference_gross == 0:
        return actual == expected
    limit = tol * reference_gross
    return math.isfinite(limit) and abs(actual-expected) <= limit


def load_json(raw: bytes | str) -> object:
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise VerificationError(f'duplicate JSON key: {k}')
            d[k]=v
        return d
    def constant(s):raise VerificationError(f'nonstandard JSON numeric token: {s}')
    try:
        obj=json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
    except (ValueError,UnicodeError) as exc:
        raise VerificationError(f'malformed/nonfinite JSON: {exc}') from exc
    def walk(v):
        if isinstance(v,float) and not math.isfinite(v):raise VerificationError('nonfinite JSON float')
        if isinstance(v,list):
            for x in v:walk(x)
        elif isinstance(v,dict):
            for x in v.values():walk(x)
    walk(obj)
    return obj


def compare_document(actual: object, reference: object) -> dict:
    if not isinstance(actual,dict) or set(actual)!={'schema','records'} or actual['schema']!=SCHEMA:
        raise VerificationError('invalid observable document schema')
    if not isinstance(reference,dict) or reference.get('schema')!=SCHEMA:
        raise VerificationError('invalid reference schema')
    ar=actual['records'];rr=reference.get('records')
    if not isinstance(ar,list) or not isinstance(rr,list) or len(ar)!=len(rr):
        raise VerificationError('record count mismatch')
    ids=set();components=0;errors=0;max_scaled=0.
    for a,r in zip(ar,rr):
        if not isinstance(a,dict) or set(a)!={'id','status','values','tags'}:
            raise VerificationError('record fields missing or unexpected')
        if a['id']!=r['id'] or not isinstance(a['id'],str) or a['id'] in ids:
            raise VerificationError('record identity/order mismatch')
        ids.add(a['id'])
        if a['status']!=r['status'] or a['tags']!=r['tags']:
            raise VerificationError(f"{a['id']}: error branch/measure tag mismatch")
        if not isinstance(a['tags'],dict) or not isinstance(a['values'],dict) or set(a['values'])!=set(r['values']):
            raise VerificationError(f"{a['id']}: values schema mismatch")
        if set(r['values'])!=set(r['scales']):raise VerificationError('reference scale keys mismatch')
        if a['status']!='ok':
            if a['values'] or a['tags']:raise VerificationError('error record must not contain partial output')
            errors+=1
        for key,want in r['values'].items():
            got=a['values'][key];scale=r['scales'][key]
            if not isinstance(got,list) or len(got)!=len(want):raise VerificationError(f'{a["id"]}.{key}: shape mismatch')
            for index,(x,y) in enumerate(zip(got,want)):
                if not compare_component(x,y,scale):
                    raise VerificationError(f'{a["id"]}.{key}[{index}]: actual={x!r}, expected={y!r}, reference_gross={scale!r}')
                components+=1
                if scale>0:max_scaled=max(max_scaled,abs(x-y)/scale)
    return {'records':len(ar),'numeric_components':components,'expected_error_records':errors,'max_reference_scaled_difference':max_scaled,'tolerance':TOLERANCE}


def run_process(command: list[str], stdin: bytes, evidence: Path,
                label: str, timeout: float = 120., max_output_bytes: int = 2_000_000) -> bytes:
    """Capture real bytes before interpreting exit or output. Never synthesize logs."""
    evidence.mkdir(parents=True,exist_ok=True)
    prefix=evidence/label
    if prefix.with_suffix('.process.json').exists():raise VerificationError('receipt path already exists')
    prefix.with_suffix('.stdin.bin').write_bytes(stdin)
    started=dt.datetime.now(dt.UTC).isoformat();clock=time.monotonic()
    code=None;failure=None;out=b'';err=b'';proc=None
    try:
        proc=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=(os.name=='posix'))
        out,err=proc.communicate(stdin,timeout=timeout);code=proc.returncode
    except subprocess.TimeoutExpired:
        failure='TIMEOUT'
        if os.name=='posix':os.killpg(proc.pid,signal.SIGKILL)
        else:proc.kill()
        out,err=proc.communicate();code=proc.returncode
    except OSError as exc:
        failure='EXECUTION_FAILED';err=str(exc).encode()
    prefix.with_suffix('.stdout.bin').write_bytes(out);prefix.with_suffix('.stderr.bin').write_bytes(err)
    rec={'command':command,'cwd':str(ROOT),'start_utc':started,'end_utc':dt.datetime.now(dt.UTC).isoformat(),'elapsed_seconds':time.monotonic()-clock,'exit':code,'execution_failure':failure,'stdin_sha256':digest(stdin),'stdout_sha256':digest(out),'stderr_sha256':digest(err),'stdout_bytes':len(out),'stderr_bytes':len(err),'label':label}
    prefix.with_suffix('.process.json').write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
    if failure or code!=0:raise VerificationError(f'{label}: {failure or "NONZERO_EXIT"}; exit={code}')
    if len(out)>max_output_bytes:raise VerificationError(f'{label}: output size limit')
    return out


def read_contract():
    lock=load_json((FIXTURES/'task6_reference_lock.json').read_bytes())
    for name,expected in lock['sha256'].items():
        if Path(name).name!=name:raise VerificationError('invalid lock filename')
        if digest((FIXTURES/name).read_bytes())!=expected:raise VerificationError(f'fixture/reference identity mismatch: {name}')
    acceptance=load_json((FIXTURES/'acceptance_task6.json').read_bytes())
    if acceptance['tolerance']!=TOLERANCE:raise VerificationError('registered tolerance changed')
    inputs=load_json((FIXTURES/'source_inputs_task6.json').read_bytes())
    reference=load_json((FIXTURES/'reference_values_v2.json').read_bytes())
    if len(inputs['cases'])>acceptance['max_cases']:raise VerificationError('input record limit')
    return inputs,reference,acceptance,lock


def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-test',action='store_true',help='Python harness tests only, no Rust invocation')
    ap.add_argument('--evidence-dir',type=Path)
    args=ap.parse_args(argv)
    evid=args.evidence_dir or ROOT/'docs/forward/rust-20260922/local_returns'/('task6-'+dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8])
    evid.mkdir(parents=True,exist_ok=False)
    try:
        inputs,reference,acceptance,lock=read_contract()
        sys.path.insert(0,str(FIXTURES))
        if args.self_test:
            from test_harness_task6 import run_suite
            report=run_suite(evid,inputs,reference)
            report['status']='SELF_TEST_PASS_NOT_RUST_PARITY'
        else:
            from input_wire_v2 import encode
            wire=encode(inputs)
            if len(wire)>acceptance['max_input_bytes']:raise VerificationError('wire input limit')
            command=['cargo','run','--manifest-path',str(ROOT/'rust/rec_microphysics/Cargo.toml'),'--locked','--example','eval_fixture','--quiet']
            raw=run_process(command,wire,evid,'rust_fixture',max_output_bytes=acceptance['max_output_bytes'])
            report=compare_document(load_json(raw),reference)
            report['status']='PASS_FIXED_INPUT_PARITY_ONLY'
            report['scope']='251 frozen finite cases; not full T4, not a recombination trajectory'
        report['reference_lock_sha256']=digest((FIXTURES/'task6_reference_lock.json').read_bytes())
        report['evidence_directory']=str(evid)
        (evid/'result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
        print(json.dumps(report,allow_nan=False,sort_keys=True));return 0
    except (VerificationError,OSError,KeyError,TypeError,ValueError) as exc:
        report={'status':'FAIL','phase':'SELF_TEST' if args.self_test else 'LOCAL_PARITY','detail':str(exc)}
        (evid/'result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
        print(json.dumps(report,allow_nan=False),file=sys.stderr);return 1


if __name__=='__main__':
    raise SystemExit(main())

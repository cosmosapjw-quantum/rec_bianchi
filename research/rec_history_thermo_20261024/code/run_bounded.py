"""Bounded launcher; no scientific imports or source evaluations in parent.

Commands after root authorization:
 python code/run_bounded.py primary --authorization evidence/execution/RUN_READY.json
 python code/run_bounded.py figures --authorization evidence/execution/FIGURES_READY.json

Each invocation is standalone and records inclusive self+child CPU, execution
wall, wait4 process-scope rusage, environment and hashes. There are no retries.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback

UNIT=Path(__file__).resolve().parents[1]
THREAD_KEYS=['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS']


def hashes():
    paths=[]
    for folder in ['code','inputs','vendor']:
        paths.extend(p for p in (UNIT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.extend(UNIT/name for name in ['THEORY.md','FROZEN_CONTRACT.md','ARITHMETIC_ADDENDUM.md'])
    return {str(p.relative_to(UNIT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)}


def usage(r):
    return {'user_cpu_seconds':r.ru_utime,'system_cpu_seconds':r.ru_stime,
            'cpu_seconds':r.ru_utime+r.ru_stime,'peak_rss_KiB':r.ru_maxrss,
            'rss_scope':'getrusage/wait4 process-scope highwater, not live namespace aggregate'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['primary','figures'])
    ap.add_argument('--authorization',required=True);args=ap.parse_args()
    auth_path=UNIT/args.authorization
    auth=json.loads(auth_path.read_text())
    if auth.get('unit')!='REC-HISTORY-THERMO01' or auth.get('action')!=args.mode or auth.get('decision')!='RUN_READY':
        raise ValueError('ROOT_EXECUTION_AUTHORIZATION_MISSING')
    # Child 39+parent1 for primary, child9+parent1 for figures are conservative
    # inclusive caps. Parent limit is installed before hashing/child launch.
    cpu=40 if args.mode=='primary' else 10
    wall=120 if args.mode=='primary' else 30
    resource.setrlimit(resource.RLIMIT_CPU,(1,cpu-1))
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    start=time.monotonic();r0=resource.getrusage(resource.RUSAGE_SELF)
    before=hashes()
    expected=auth.get('source_snapshot')
    if expected is None or expected!=before:
        raise ValueError('ROOT_AUTHORIZED_SNAPSHOT_MISMATCH')
    out=UNIT/'evidence/execution'/args.mode
    out.mkdir(parents=True,exist_ok=False)
    (out/'HASHES_BEFORE.json').write_text(json.dumps(before,indent=2)+'\n')
    env=os.environ.copy();env.update({k:'1' for k in THREAD_KEYS});env['PYTHONDONTWRITEBYTECODE']='1'
    command=[sys.executable,str(UNIT/'code'/('primary.py' if args.mode=='primary' else 'figures.py'))]
    record={'unit':'REC-HISTORY-THERMO01','mode':args.mode,'command':command,'cwd':str(UNIT),
            'authorization_path':str(auth_path.relative_to(UNIT)),
            'authorization_sha256':hashlib.sha256(auth_path.read_bytes()).hexdigest(),
            'thread_environment':{k:env[k] for k in THREAD_KEYS},'thread_limit':1,
            'inclusive_cpu_cap_seconds':cpu,'execution_wall_cap_seconds':wall,'address_space_bytes':1024**3,
            'child_cpu_limit_seconds':cpu-1,'parent_cpu_limit_seconds':1,
            'parent_pre_fork_hard_limit':cpu-1,
            'execution_wall_origin':'after authorization parsing, before input/code hashing and child launch',
            'requested_model':'gpt-6.1-sol','requested_reasoning':'high','observed_model':None,
            'automatic_retries':0,'providerIO_or_packaging_included':False}
    (out/'COMMAND.json').write_text(json.dumps(record,indent=2)+'\n')
    def limits():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU,(cpu-1,cpu-1))
        resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
        try:
            p=subprocess.Popen(command,cwd=UNIT,env=env,stdout=stdout,stderr=stderr,preexec_fn=limits)
        except Exception as e:
            record.update(status='ENVIRONMENT_START_FAILURE',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),
                          execution_wall_seconds=time.monotonic()-start,parent_rusage=usage(resource.getrusage(resource.RUSAGE_SELF)),
                          hashes_unchanged=before==hashes(),child_started=False)
            (out/'EXECUTION_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n')
            raise
        resource.setrlimit(resource.RLIMIT_CPU,(1,1))
        timed_out=False;status=None;child_usage=None
        while status is None:
            pid,st,ru=os.wait4(p.pid,os.WNOHANG)
            if pid:
                status=st;child_usage=ru;break
            if time.monotonic()-start>=wall-1:
                timed_out=True;os.killpg(p.pid,signal.SIGKILL)
                _,status,child_usage=os.wait4(p.pid,0);break
            time.sleep(.05)
        p.returncode=os.waitstatus_to_exitcode(status)
    after=hashes()
    (out/'HASHES_AFTER.json').write_text(json.dumps(after,indent=2)+'\n')
    r1=resource.getrusage(resource.RUSAGE_SELF)
    inclusive_cpu=r1.ru_utime+r1.ru_stime+child_usage.ru_utime+child_usage.ru_stime
    record.update(exit_code=p.returncode,timed_out=timed_out,execution_wall_seconds=time.monotonic()-start,
                  inclusive_cpu_seconds=inclusive_cpu,parent_rusage=usage(r1),child_rusage=usage(child_usage),
                  hashes_unchanged=before==after,
                  cap_compliance=inclusive_cpu<=cpu and time.monotonic()-start<=wall)
    (out/'EXECUTION_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2),flush=True)
    return p.returncode if record['hashes_unchanged'] and record['cap_compliance'] else 3


if __name__=='__main__':
    sys.exit(main())

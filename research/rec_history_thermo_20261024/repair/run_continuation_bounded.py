"""One continuation,10 inclusive CPU/30wall; original code/raw stay immutable."""
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


def snapshot():
    original=json.loads((UNIT/'evidence/execution/PREPARED_SOURCE_SNAPSHOT.json').read_text())['source_snapshot']
    result={}
    for name,expected in original.items():
        b=(UNIT/name).read_bytes();observed={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
        if observed!=expected:
            raise ValueError('ORIGINAL_23_IDENTITY_CHANGED:'+name)
        result[name]=observed
    paths=[UNIT/'repair/continuation.py',UNIT/'repair/run_continuation_bounded.py',
           UNIT/'evidence/ROOT_SERIALIZATION_CONTINUATION_DECISION.md',
           UNIT/'environment/EXECUTION_ENVIRONMENT.json']
    paths.extend(p for p in (UNIT/'results/primary001').iterdir() if p.is_file())
    for p in sorted(paths):
        b=p.read_bytes();result[str(p.relative_to(UNIT))]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    return dict(sorted(result.items()))


def usage(r):
    return {'user_cpu_seconds':r.ru_utime,'system_cpu_seconds':r.ru_stime,
            'cpu_seconds':r.ru_utime+r.ru_stime,'peak_rss_KiB':r.ru_maxrss,
            'rss_scope':'wait4/getrusage process-scope highwater; no live aggregate claim'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--authorization',required=True);args=ap.parse_args()
    auth_path=UNIT/args.authorization;auth=json.loads(auth_path.read_text())
    if auth.get('unit')!='REC-HISTORY-THERMO01' or auth.get('action')!='continuation' or auth.get('decision')!='RUN_READY':
        raise ValueError('ROOT_CONTINUATION_RUN_READY_MISSING')
    resource.setrlimit(resource.RLIMIT_CPU,(1,9))
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    start=time.monotonic();before=snapshot()
    if before!=auth.get('source_snapshot'):
        raise ValueError('AUTHORIZED_CONTINUATION_SNAPSHOT_MISMATCH')
    out=UNIT/'evidence/execution/continuation'
    out.mkdir(parents=True,exist_ok=False)
    (out/'HASHES_BEFORE.json').write_text(json.dumps(before,indent=2)+'\n')
    env=os.environ.copy();env.update({k:'1' for k in THREAD_KEYS});env['PYTHONDONTWRITEBYTECODE']='1'
    expected_pythonpath=str(UNIT/'environment/deps')
    if env.get('PYTHONPATH')!=expected_pythonpath:
        raise ValueError('EXPLICIT_ISOLATED_PYTHONPATH_REQUIRED')
    command=[sys.executable,str(UNIT/'repair/continuation.py')]
    record={'unit':'REC-HISTORY-THERMO01','mode':'continuation','command':command,'cwd':str(UNIT),
            'authorization_path':str(auth_path.relative_to(UNIT)),
            'authorization_sha256':hashlib.sha256(auth_path.read_bytes()).hexdigest(),
            'thread_environment':{k:env[k] for k in THREAD_KEYS},'PYTHONPATH':env['PYTHONPATH'],
            'PYTHONDONTWRITEBYTECODE':env['PYTHONDONTWRITEBYTECODE'],
            'inclusive_cpu_cap_seconds':10,'execution_wall_cap_seconds':30,'address_space_bytes':1024**3,
            'parent_cpu_limit_seconds':1,'parent_pre_fork_hard_limit':9,'child_cpu_limit_seconds':9,
            'execution_wall_origin':'after authorization parsing, before hashing/child launch',
            'large_RHS_local_ceiling':12,'large_RHS_cumulative_ceiling':25,'prior_large_RHS':13,
            'small_RHS_ceiling':16,'requested_model':'gpt-6.1-sol','requested_reasoning':'high','observed_model':None,
            'automatic_retries':0,'providerIO_or_packaging_included':False}
    (out/'COMMAND.json').write_text(json.dumps(record,indent=2)+'\n')
    def limits():
        os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(9,9))
        resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
        try:
            p=subprocess.Popen(command,cwd=UNIT,env=env,stdout=stdout,stderr=stderr,preexec_fn=limits)
        except Exception as e:
            record.update(status='ENVIRONMENT_START_FAILURE',error_type=type(e).__name__,error=str(e),
                          traceback=traceback.format_exc(),execution_wall_seconds=time.monotonic()-start,
                          parent_rusage=usage(resource.getrusage(resource.RUSAGE_SELF)),child_started=False,
                          hashes_unchanged=before==snapshot())
            (out/'EXECUTION_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n')
            raise
        resource.setrlimit(resource.RLIMIT_CPU,(1,1))
        timed_out=False;status=None;child_usage=None
        while status is None:
            pid,st,ru=os.wait4(p.pid,os.WNOHANG)
            if pid:
                status=st;child_usage=ru;break
            if time.monotonic()-start>=29:
                timed_out=True;os.killpg(p.pid,signal.SIGKILL)
                _,status,child_usage=os.wait4(p.pid,0);break
            time.sleep(.05)
        p.returncode=os.waitstatus_to_exitcode(status)
    after=snapshot();(out/'HASHES_AFTER.json').write_text(json.dumps(after,indent=2)+'\n')
    parent_usage=resource.getrusage(resource.RUSAGE_SELF)
    cpu=parent_usage.ru_utime+parent_usage.ru_stime+child_usage.ru_utime+child_usage.ru_stime
    wall=time.monotonic()-start
    record.update(exit_code=p.returncode,timed_out=timed_out,inclusive_cpu_seconds=cpu,
                  execution_wall_seconds=wall,parent_rusage=usage(parent_usage),child_rusage=usage(child_usage),
                  hashes_unchanged=before==after,cap_compliance=cpu<=10 and wall<=30)
    (out/'EXECUTION_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2),flush=True)
    return p.returncode if record['hashes_unchanged'] and record['cap_compliance'] else 3


if __name__=='__main__':
    sys.exit(main())

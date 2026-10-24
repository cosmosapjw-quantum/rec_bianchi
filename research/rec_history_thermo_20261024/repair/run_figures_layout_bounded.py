"""One formatting-only child,5inclusiveCPU/25wall, no original-byte changes."""
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
        b=(UNIT/name).read_bytes();actual={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
        if actual!=expected:
            raise ValueError('ORIGINAL_23_IDENTITY_CHANGED:'+name)
        result[name]=actual
    paths=[UNIT/'repair/figures_layout.py',UNIT/'repair/run_figures_layout_bounded.py',
           UNIT/'evidence/ROOT_FIGURE_LAYOUT_DECISION.md',UNIT/'environment/EXECUTION_ENVIRONMENT.json']
    for folder in ['results/primary001','results/continuation001','results/figures001']:
        paths.extend(p for p in (UNIT/folder).iterdir() if p.is_file())
    for p in sorted(paths):
        b=p.read_bytes();result[str(p.relative_to(UNIT))]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    return dict(sorted(result.items()))


def usage(r):
    return {'user_cpu_seconds':r.ru_utime,'system_cpu_seconds':r.ru_stime,
            'cpu_seconds':r.ru_utime+r.ru_stime,'peak_rss_KiB':r.ru_maxrss,
            'rss_scope':'getrusage/wait4 process-scope highwater, not live aggregate'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--authorization',required=True);args=ap.parse_args()
    apath=UNIT/args.authorization;auth=json.loads(apath.read_text())
    if auth.get('unit')!='REC-HISTORY-THERMO01' or auth.get('action')!='figure_layout' or auth.get('decision')!='RUN_READY':
        raise ValueError('ROOT_FIGURE_LAYOUT_RUN_READY_MISSING')
    resource.setrlimit(resource.RLIMIT_CPU,(1,4));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    start=time.monotonic();before=snapshot()
    if before!=auth.get('source_snapshot'):
        raise ValueError('AUTHORIZED_LAYOUT_SNAPSHOT_MISMATCH')
    out=UNIT/'evidence/execution/figures_layout';out.mkdir(parents=True,exist_ok=False)
    (out/'HASHES_BEFORE.json').write_text(json.dumps(before,indent=2)+'\n')
    env=os.environ.copy();env.update({k:'1' for k in THREAD_KEYS});env['PYTHONDONTWRITEBYTECODE']='1'
    if env.get('PYTHONPATH')!=str(UNIT/'environment/deps'):
        raise ValueError('EXPLICIT_PYTHONPATH_REQUIRED')
    command=[sys.executable,str(UNIT/'repair/figures_layout.py')]
    record={'unit':'REC-HISTORY-THERMO01','mode':'figure_layout','command':command,'cwd':str(UNIT),
            'authorization_path':str(apath.relative_to(UNIT)),'authorization_sha256':hashlib.sha256(apath.read_bytes()).hexdigest(),
            'thread_environment':{k:env[k] for k in THREAD_KEYS},'PYTHONPATH':env['PYTHONPATH'],
            'PYTHONDONTWRITEBYTECODE':env['PYTHONDONTWRITEBYTECODE'],
            'inclusive_cpu_cap_seconds':5,'execution_wall_cap_seconds':25,'address_space_bytes':1024**3,
            'parent_cpu_limit_seconds':1,'parent_pre_fork_hard_limit':4,'child_cpu_limit_seconds':4,
            'execution_wall_origin':'after authorization parsing, before snapshot hashes and child launch',
            'figure_process_count_amendment':'second and final presentation process; unchanged10CPU/30wall total figure allowance',
            'first_figure_cpu_seconds':4.240177,'first_figure_wall_seconds':4.219067001002259,
            'source_evaluations':0,'linear_solves':0,'automatic_retries':0,
            'requested_model':'gpt-6.1-sol','observed_model':None,'providerIO_or_packaging_included':False}
    (out/'COMMAND.json').write_text(json.dumps(record,indent=2)+'\n')
    def limits():
        os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(4,4));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
        try:
            p=subprocess.Popen(command,cwd=UNIT,env=env,stdout=stdout,stderr=stderr,preexec_fn=limits)
        except Exception as e:
            record.update(status='ENVIRONMENT_START_FAILURE',error=str(e),traceback=traceback.format_exc(),
                          parent_rusage=usage(resource.getrusage(resource.RUSAGE_SELF)),
                          execution_wall_seconds=time.monotonic()-start,hashes_unchanged=before==snapshot())
            (out/'EXECUTION_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n');raise
        resource.setrlimit(resource.RLIMIT_CPU,(1,1))
        status=None;timed_out=False;child_usage=None
        while status is None:
            pid,st,ru=os.wait4(p.pid,os.WNOHANG)
            if pid:
                status=st;child_usage=ru;break
            if time.monotonic()-start>=24:
                timed_out=True;os.killpg(p.pid,signal.SIGKILL);_,status,child_usage=os.wait4(p.pid,0);break
            time.sleep(.05)
        p.returncode=os.waitstatus_to_exitcode(status)
    after=snapshot();(out/'HASHES_AFTER.json').write_text(json.dumps(after,indent=2)+'\n')
    parent_usage=resource.getrusage(resource.RUSAGE_SELF)
    cpu=parent_usage.ru_utime+parent_usage.ru_stime+child_usage.ru_utime+child_usage.ru_stime
    wall=time.monotonic()-start
    record.update(exit_code=p.returncode,timed_out=timed_out,inclusive_cpu_seconds=cpu,execution_wall_seconds=wall,
                  parent_rusage=usage(parent_usage),child_rusage=usage(child_usage),hashes_unchanged=before==after,
                  cap_compliance=cpu<=5 and wall<=25,
                  cumulative_figure_cpu_seconds=4.240177+cpu,
                  cumulative_figure_execution_wall_seconds=4.219067001002259+wall)
    (out/'EXECUTION_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2),flush=True)
    return p.returncode if record['hashes_unchanged'] and record['cap_compliance'] else 3


if __name__=='__main__':
    sys.exit(main())

"""Frozen one-shot child execution with CPU, wall and address-space ceilings."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['primary','controls'],required=True)
    p.add_argument('--cpu-seconds',type=int,required=True)
    p.add_argument('--wall-seconds',type=int,required=True)
    p.add_argument('--memory-mib',type=int,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if sys.version_info[:2] != (3,12): raise RuntimeError('frozen Python3.12 runtime')
    frozen={'primary':(90,180,2048),'controls':(60,120,2048)}
    if (args.cpu_seconds,args.wall_seconds,args.memory_mib) != frozen[args.mode]:
        raise ValueError('execution limits differ from frozen command')
    args.output.mkdir(parents=True,exist_ok=False)
    code=Path(__file__).resolve().parent
    env=os.environ.copy()
    for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS',
              'VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'): env[k]='1'
    env['PYTHONHASHSEED']='0'
    env['MPLCONFIGDIR']=str((args.output/'matplotlib_config').resolve())
    child=[sys.executable,str(code/'native_reference.py'),'--mode',args.mode,'--output',str(args.output)]
    source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(code.glob('*.py'))}
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(args.cpu_seconds,args.cpu_seconds))
        n=args.memory_mib*1024*1024
        resource.setrlimit(resource.RLIMIT_AS,(n,n))
        if hasattr(os,'sched_getaffinity'):
            available=os.sched_getaffinity(0)
            os.sched_setaffinity(0,{min(available)})
    start=time.monotonic(); before=resource.getrusage(resource.RUSAGE_CHILDREN)
    started=datetime.now(timezone.utc).isoformat()
    timed_out=False; exit_code=None
    with (args.output/'stdout.txt').open('x') as out,(args.output/'stderr.txt').open('x') as err:
        proc=subprocess.Popen(child,env=env,stdout=out,stderr=err,preexec_fn=limits,start_new_session=True)
        try: exit_code=proc.wait(timeout=args.wall_seconds)
        except subprocess.TimeoutExpired:
            timed_out=True
            os.killpg(proc.pid,signal.SIGKILL)
            exit_code=proc.wait()
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'schema':'REC_H5_NATIVE_REFERENCE_RUN_V1','mode':args.mode,
             'wrapper_argv':sys.argv,'child_argv':child,'cwd':os.getcwd(),'started_utc':started,
             'finished_utc':datetime.now(timezone.utc).isoformat(),'exit_code':exit_code,
             'wall_timeout':timed_out,'wall_seconds':time.monotonic()-start,
             'cpu_user_seconds':after.ru_utime-before.ru_utime,
             'cpu_system_seconds':after.ru_stime-before.ru_stime,
             'cpu_seconds':after.ru_utime-before.ru_utime+after.ru_stime-before.ru_stime,
             'max_rss_kib':after.ru_maxrss,'limits':{'cpu_seconds':args.cpu_seconds,
             'wall_seconds':args.wall_seconds,'address_space_bytes':args.memory_mib*1024*1024,'threads':1},
             'python_version':sys.version,'python_executable':sys.executable,'platform':platform.platform(),
             'production_precision':80,'independent_precision':140,'code_sha256':source_hashes,
             'thread_environment':{k:env[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
                 'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','PYTHONHASHSEED')},
             'requested_implementation_tier':'lower-tier gpt-6.1-sol',
             'observed_runtime_model_identity':'NOT_EXPOSED; no verification claimed'}
    with (args.output/'RUN_RECEIPT.json').open('x') as f:
        json.dump(receipt,f,indent=2,sort_keys=True); f.write('\n')
    print(json.dumps(receipt,sort_keys=True))
    raise SystemExit(0 if exit_code == 0 and not timed_out else 1)

if __name__ == '__main__': main()

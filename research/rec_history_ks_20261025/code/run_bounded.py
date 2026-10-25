"""Frozen single-attempt child resource boundary and raw failure preservation."""
import argparse, json, os, resource, subprocess, sys, time
from pathlib import Path
from common import UNIT,defaults,files,identity,save

def main():
    p=argparse.ArgumentParser();t,h,q=defaults()
    p.add_argument('--thermo',type=Path,default=t);p.add_argument('--history',type=Path,default=h);p.add_argument('--query-map',type=Path,default=q)
    p.add_argument('--label',default='primary001');args=p.parse_args()
    ready=UNIT/'evidence/RUN_READY.json'
    if not ready.exists() or json.loads(ready.read_text()).get('authorization')!='RUN_READY': raise RuntimeError('ROOT_RUN_READY_REQUIRED')
    ev=UNIT/'evidence/execution'/args.label;ev.mkdir(parents=True,exist_ok=False)
    out=UNIT/'results'/args.label
    if out.exists(): raise RuntimeError('NO_RETRY_OR_OVERWRITE')
    before={name:identity(path) for name,path in files(args.thermo,args.history,args.query_map).items()};save(ev/'HASHES_BEFORE.json',before)
    env=os.environ.copy()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):env[key]='1'
    command=[sys.executable,str(UNIT/'code/primary.py'),'--thermo',str(args.thermo),'--history',str(args.history),'--query-map',str(args.query_map),'--out',str(out)]
    limits={'cpu_seconds_inclusive':45,'wall_seconds':135,'rlimit_as_bytes':1073741824,'blas_threads':1,'large_rhs_cap':639,'small_rhs_cap':12,'new_ivp':0,'native_runtime':0,'automatic_retries':0}
    save(ev/'COMMAND.json',{'argv':command,'limits':limits,'thread_env':{k:env[k] for k in env if k.endswith('_NUM_THREADS') or k=='VECLIB_MAXIMUM_THREADS'}})
    def constrain():
        resource.setrlimit(resource.RLIMIT_CPU,(45,45));resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    initial=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();timed_out=False
    with (ev/'stdout.txt').open('wb') as stdout,(ev/'stderr.txt').open('wb') as stderr:
        child=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr,preexec_fn=constrain)
        try: code=child.wait(timeout=135)
        except subprocess.TimeoutExpired:timed_out=True;child.kill();code=child.wait()
    final=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'returncode':code,'timed_out':timed_out,'wall_seconds':time.monotonic()-start,'child_user_cpu_seconds':final.ru_utime-initial.ru_utime,'child_system_cpu_seconds':final.ru_stime-initial.ru_stime,'child_inclusive_cpu_seconds':final.ru_utime+final.ru_stime-initial.ru_utime-initial.ru_stime,'child_max_rss_kib':final.ru_maxrss,'limits':limits,'partial_results_preserved':True,'raw_stdout_stderr_preserved':True,'requested_model':'gpt-6.1-sol','observed_model':None}
    save(ev/'EXECUTION_RECEIPT.json',receipt)
    save(ev/'HASHES_AFTER.json',{name:identity(path) for name,path in files(args.thermo,args.history,args.query_map).items()})
    print(json.dumps(receipt));return code if code>=0 else 1
if __name__=='__main__':sys.exit(main())

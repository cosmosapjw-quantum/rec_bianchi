"""Single initial PB01 child, hard resource boundary, no automatic retry."""
import json,os,resource,subprocess,sys,time
from pathlib import Path
from common import UNIT,used_files,identity,save

def main():
 ready=UNIT/'evidence/RUN_READY.json'
 if not ready.is_file() or json.loads(ready.read_text()).get('authorization')!='RUN_READY':raise RuntimeError('ROOT_RUN_READY_REQUIRED_AFTER_PREEXEC_AND_ACTUAL_S0_S1')
 ev=UNIT/'evidence/execution/primary001';out=UNIT/'results/primary001'
 if ev.exists() or out.exists():raise RuntimeError('SINGLE_ATTEMPT_NO_RETRY_NO_OVERWRITE')
 ev.mkdir(parents=True)
 save(ev/'HASHES_BEFORE.json',{k:identity(p) for k,p in used_files().items()})
 env=os.environ.copy()
 threadkeys=('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')
 for key in threadkeys:env[key]='1'
 command=[sys.executable,str(UNIT/'code/primary.py'),'--out',str(out)]
 limits={'cpu_seconds':30,'wall_seconds':90,'RLIMIT_AS_bytes':1073741824,'threads':1,'operator_action_cap':256,'event_action_cap':512,'linear_RHS':0,'solves':0,'inverses':0,'source_coefficient_rebuilds':0,'native':0,'IVP':0,'automatic_retry':False}
 save(ev/'COMMAND.json',{'argv':command,'limits':limits,'thread_environment':{k:env[k] for k in threadkeys}})
 def boundary():
  resource.setrlimit(resource.RLIMIT_CPU,(30,30));resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 start=time.monotonic();initial=resource.getrusage(resource.RUSAGE_CHILDREN);timed=False
 with (ev/'stdout.txt').open('wb') as stdout,(ev/'stderr.txt').open('wb') as stderr:
  child=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr,preexec_fn=boundary)
  try:code=child.wait(timeout=90)
  except subprocess.TimeoutExpired:timed=True;child.kill();code=child.wait()
 final=resource.getrusage(resource.RUSAGE_CHILDREN)
 receipt={'returncode':code,'timed_out':timed,'child_wall_seconds':time.monotonic()-start,'child_user_cpu_seconds':final.ru_utime-initial.ru_utime,'child_system_cpu_seconds':final.ru_stime-initial.ru_stime,'child_inclusive_cpu_seconds':final.ru_utime+final.ru_stime-initial.ru_utime-initial.ru_stime,'child_maxRSS_KiB':final.ru_maxrss,'limits':limits,'raw_partial_results_preserved':True,'requested_model':'gpt-6.1-sol','observed_model':None}
 save(ev/'EXECUTION_RECEIPT.json',receipt);save(ev/'HASHES_AFTER.json',{k:identity(p) for k,p in used_files().items()});print(json.dumps(receipt));return code if code>=0 else 1
if __name__=='__main__':sys.exit(main())

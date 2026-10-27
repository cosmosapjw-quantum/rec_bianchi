"""One primary or saved-data figure child; no retry and no overwrite."""
import json,os,resource,subprocess,sys,time
from pathlib import Path
THREADS=('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')
for key in THREADS:os.environ[key]='1'
from common import UNIT,save,source_snapshot

def main():
 mode=sys.argv[1] if len(sys.argv)>1 else 'primary'
 if mode not in ('primary','figures'):raise ValueError('MODE')
 ready=UNIT/'evidence/RUN_READY.json'
 if not ready.exists() or json.loads(ready.read_text()).get('authorization')!='RUN_READY':raise RuntimeError('ROOT_RUN_READY_REQUIRED')
 expected=json.loads((UNIT/'evidence/execution/C5_PREEXECUTION.json').read_text())['files']
 current=source_snapshot()
 if current!=expected:raise RuntimeError('C5_FROZEN_SOURCE_OR_INPUT_CHANGED')
 attempt='primary001' if mode=='primary' else 'figures001';ev=UNIT/'evidence/execution'/attempt
 out=UNIT/('results/primary001' if mode=='primary' else 'figures/figures001')
 if ev.exists() or out.exists():raise RuntimeError('SINGLE_ATTEMPT_NO_RETRY_NO_OVERWRITE')
 if mode=='figures':
  s=UNIT/'results/primary001/SUMMARY.json'
  if not s.exists() or json.loads(s.read_text()).get('status')!='PASS_CONTROLLED_PROPAGATION_PARTIAL':raise RuntimeError('PRIMARY_PASS_REQUIRED_FOR_FIGURES')
 ev.mkdir(parents=True);save(ev/'SOURCE_SNAPSHOT_BEFORE.json',current)
 cpu,wall=(40,120) if mode=='primary' else (10,30)
 command=[sys.executable,str(UNIT/('code/primary.py' if mode=='primary' else 'code/figures.py')),str(out)]
 limits=dict(cpu_seconds=cpu,wall_seconds=wall,address_space_bytes=1073741824,threads=1,ordinary_roots_cap=17528 if mode=='primary' else 0,decimal_roots_cap=96 if mode=='primary' else 0,matvec_cap=5 if mode=='primary' else 0,interval_action_cap=1 if mode=='primary' else 0,new_RHS=0,IVP=0,solves=0,automatic_retry=False)
 save(ev/'COMMAND.json',dict(argv=command,limits=limits,thread_environment={k:os.environ[k] for k in THREADS}))
 def boundary():
  resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu));resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 start=time.monotonic();initial=resource.getrusage(resource.RUSAGE_CHILDREN);own=resource.getrusage(resource.RUSAGE_SELF);timed=False
 with (ev/'stdout.txt').open('wb') as stdout,(ev/'stderr.txt').open('wb') as stderr:
  child=subprocess.Popen(command,env=os.environ.copy(),stdout=stdout,stderr=stderr,preexec_fn=boundary)
  try:code=child.wait(timeout=wall)
  except subprocess.TimeoutExpired:timed=True;child.kill();code=child.wait()
 end=resource.getrusage(resource.RUSAGE_CHILDREN);ownend=resource.getrusage(resource.RUSAGE_SELF)
 receipt=dict(mode=mode,returncode=code,timed_out=timed,execution_wall_seconds=time.monotonic()-start,child_user_cpu_seconds=end.ru_utime-initial.ru_utime,child_system_cpu_seconds=end.ru_stime-initial.ru_stime,child_inclusive_cpu_seconds=end.ru_utime+end.ru_stime-initial.ru_utime-initial.ru_stime,runner_cpu_seconds=ownend.ru_utime+ownend.ru_stime-own.ru_utime-own.ru_stime,child_highwaterRSS_KiB=end.ru_maxrss,limits=limits,preserved_completed_prefix=True,observed_runtime_model=None,remote_IO_cost='SEPARATE_UNKNOWN_NOT_ZERO')
 after=source_snapshot();save(ev/'SOURCE_SNAPSHOT_AFTER.json',after);receipt['identity_unchanged']=after==current
 save(ev/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,sort_keys=True));return code if code>=0 else 1
if __name__=='__main__':sys.exit(main())

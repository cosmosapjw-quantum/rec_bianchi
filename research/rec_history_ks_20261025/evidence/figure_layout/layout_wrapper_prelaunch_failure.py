"""Root-authorized one-shot saved-result rendering resource wrapper."""
import hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
WORK=Path(__file__).resolve().parents[1];UNIT=WORK/'research/rec_history_ks_20261025'
ev=UNIT/'evidence/execution/figures001';ev.mkdir(parents=True,exist_ok=False)
out=UNIT/'results/figures001'
if out.exists():raise RuntimeError('CORRECTED_FIGURE_ALREADY_EXISTS_NO_OVERWRITE')
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def hashes():
    return {str(p.relative_to(UNIT)):{'bytes':len(p.read_bytes()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for d in ('code','tests') for p in sorted((UNIT/d).glob('*')) if p.is_file()}
before=hashes();save(ev/'HASHES_BEFORE.json',before)
env=os.environ.copy()
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):env[k]='1'
limits={'cpu_seconds':7,'wall_seconds':25,'rlimit_as_bytes':1073741824,'blas_threads':1,'source_evaluation':0,'large_rhs':0,'small_rhs':0,'new_ivp':0,'native_runtime':0,'automatic_retries':0}
command=[sys.executable,str(UNIT/'evidence/figure_layout/figures_layout002.py'),'--results',str(UNIT/'results/primary001'),'--out',str(out)]
save(ev/'COMMAND.json',{'argv':command,'limits':limits,'thread_environment':{k:env[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')}})
def constrain():
    resource.setrlimit(resource.RLIMIT_CPU,(7,7));resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
initial=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();timed=False
with (ev/'stdout.txt').open('wb') as stdout,(ev/'stderr.txt').open('wb') as stderr:
    p=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr,preexec_fn=constrain)
    try:code=p.wait(timeout=25)
    except subprocess.TimeoutExpired:timed=True;p.kill();code=p.wait()
final=resource.getrusage(resource.RUSAGE_CHILDREN);after=hashes();save(ev/'HASHES_AFTER.json',after)
receipt={'returncode':code,'timed_out':timed,'wall_seconds':time.monotonic()-start,'child_user_cpu_seconds':final.ru_utime-initial.ru_utime,'child_system_cpu_seconds':final.ru_stime-initial.ru_stime,'child_inclusive_cpu_seconds':final.ru_utime+final.ru_stime-initial.ru_utime-initial.ru_stime,'child_max_rss_kib':final.ru_maxrss,'limits':limits,'source_hashes_unchanged':before==after,'first_outputs_preserved':True}
save(ev/'EXECUTION_RECEIPT.json',receipt)
assets={str(p.relative_to(UNIT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.glob('*')) if p.is_file()} if out.exists() else {}
save(ev/'FIRST_ASSET_IDENTITIES.json',assets)
print(json.dumps(receipt));print(json.dumps(assets));sys.exit(code if code>=0 else 1)

"""One new thermal-unit execution with exact recorded resource usage."""
import argparse,pathlib,os,sys,time,resource,signal,json,hashlib,platform
ROOT=pathlib.Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();output=pathlib.Path(args.output).resolve()
    if output.exists() or (ROOT/'RESOURCE_LEDGER.json').exists():raise RuntimeError('create-only primary attempt exists')
    command=[sys.executable,str(ROOT/'tests.py'),'--output',str(output)]
    manifest={'argv':command,'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')},'input_metadata_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.json')},'python':sys.version,'platform':platform.platform(),'limits':{'cumulative_child_CPU_seconds':8,'wall_seconds':30,'address_space_bytes':256*1024**2,'threads':1,'workers':1},'prior_budgets':'SEPARATE_NO_TRANSFER','attempt':'primary1'}
    (ROOT/'PREEXECUTION.json').write_text(json.dumps(manifest,indent=2)+'\n')
    before=resource.getrusage(resource.RUSAGE_SELF);started=time.monotonic();pid=os.fork()
    if pid==0:
        os.setsid();resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(8,8))
        for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
        for fd,label in [(1,'stdout'),(2,'stderr')]:
            f=os.open(str(ROOT/('primary.'+label+'.log')),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.dup2(f,fd);os.close(f)
        os.execv(sys.executable,command)
    timed=False
    while True:
        done,status,use=os.wait4(pid,os.WNOHANG)
        if done:break
        if time.monotonic()-started>30:
            os.killpg(pid,signal.SIGKILL);done,status,use=os.wait4(pid,0);timed=True;break
        time.sleep(.005)
    end=resource.getrusage(resource.RUSAGE_SELF);wall=time.monotonic()-started;cpu=use.ru_utime+use.ru_stime;exitcode=os.waitstatus_to_exitcode(status)
    ledger={'argv':command,'attempt':'primary1','exit_status':exitcode,'timeout':timed,'child_CPU_user_seconds':use.ru_utime,'child_CPU_system_seconds':use.ru_stime,'cumulative_child_CPU_seconds':cpu,'wall_seconds':wall,'child_maxrss_KiB':use.ru_maxrss,'runner_self_CPU_seconds':end.ru_utime+end.ru_stime-before.ru_utime-before.ru_stime,'host_overhead':'UNKNOWN_NOT_MEASURED','budget_seconds':8,'wall_limit_seconds':30,'AS_limit_bytes':256*1024**2,'workers':1,'threads':1,'historical_budget_transfer':False,'resource_checks_pass':exitcode==0 and not timed and cpu<=8}
    (ROOT/'RESOURCE_LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');print(json.dumps(ledger));sys.exit(0 if ledger['resource_checks_pass'] else 1)
if __name__=='__main__':main()

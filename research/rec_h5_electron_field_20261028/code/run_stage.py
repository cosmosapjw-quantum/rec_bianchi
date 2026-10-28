"""Public bounded C6/C7/C8 entry. Invoke only after root stage authorization."""
from pathlib import Path
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
EXEC=ROOT/'execution'
REMOTE_CPU=.06227
TOTAL_CPU=60.
LIMIT_BYTES=512*1024**2
THREAD_VARS=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')

def store(path,value):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temporary.replace(path)

def family_cpu(root_pid,expected_starttime):
    """Observed Linux live-family + waited-descendant CPU, tick-resolution guard."""
    records={}
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():continue
        try:
            fields=(path/'stat').read_text().rsplit(')',1)[1].split()
            records[int(path.name)]={'pid':int(path.name),'ppid':int(fields[1]),'starttime':int(fields[19]),
                                    'utime':int(fields[11]),'stime':int(fields[12]),'cutime':int(fields[13]),'cstime':int(fields[14])}
        except (OSError,ValueError,IndexError):continue
    if root_pid not in records or records[root_pid]['starttime']!=expected_starttime:
        raise RuntimeError('PROC_ROOT_IDENTITY_NOT_VISIBLE_OR_CHANGED')
    selected={root_pid}
    while True:
        expanded=selected|{pid for pid,row in records.items() if row['ppid'] in selected}
        if expanded==selected:break
        selected=expanded
    sample=[records[pid] for pid in sorted(selected) if pid in records]
    cpu=sum(sum(row[k] for k in ('utime','stime','cutime','cstime')) for row in sample)/os.sysconf('SC_CLK_TCK')
    return cpu,sample

def journal_counts(directory):
    path=directory/'CALL_JOURNAL.jsonl';entered=set();returned=set();known=0
    if path.exists():
        for line in path.read_text().splitlines():
            try:row=json.loads(line)
            except json.JSONDecodeError:continue
            if row['event']=='API_ENTER':entered.add(row['attempt'])
            elif row['event']=='API_RETURN':returned.add(row['attempt']);known+=row['native_kernel_calls']
    return {'native_kernel_calls_known':known,'unfinished_API_attempts_unknown':len(entered-returned)}

def run_child(stage,allocation,ledger,state):
    planned={'C6':2,'C7':132,'C8_VALIDATE':9,'C8_PLOTS':0}[stage]
    if ledger.get('unfinished_API_attempts_unknown',0):raise RuntimeError('UNRESOLVED_NATIVE_CALL_COUNT_STOP_FOR_ASTRA')
    if ledger.get('native_kernel_calls_known',0)+planned>146:raise RuntimeError('INITIAL_NATIVE_CALL_CAP_WOULD_BE_EXCEEDED')
    spent=REMOTE_CPU+sum(x['actual_child_cpu_s'] for x in ledger['attempts'])
    available=TOTAL_CPU-spent
    stage_paid=sum(x['actual_child_cpu_s'] for x in ledger['attempts'] if x.get('charge_stage',x['stage'])==stage)
    allocation_remaining=allocation-stage_paid
    cap=min(allocation_remaining,available)
    if cap<=.05:raise RuntimeError('NO_REMAINING_CUMULATIVE_CPU')
    i=1
    while (EXEC/f'{stage}_attempt{i:03d}').exists():i+=1
    directory=EXEC/f'{stage}_attempt{i:03d}';directory.mkdir()
    command=[sys.executable,str(ROOT/'code/stage_worker.py'),stage,str(directory)]
    environment=os.environ.copy();environment.update({k:'1' for k in THREAD_VARS})
    environment['PYTHONDONTWRITEBYTECODE']='1';environment['MPLCONFIGDIR']=str(directory/'matplotlib_config')
    def limits():
        os.setsid()
        hard=max(1,math.ceil(cap))
        resource.setrlimit(resource.RLIMIT_CPU,(hard,hard))
        resource.setrlimit(resource.RLIMIT_AS,(LIMIT_BYTES,LIMIT_BYTES))
        raw=Path('/proc/self/stat').read_text()
        fields=raw.rsplit(')',1)[1].split()
        identity={'namespace_pid':os.getpid(),'namespace_ppid':os.getppid(),'proc_pid':int(raw.split(' ',1)[0]),
                  'proc_ppid':int(fields[1]),'proc_starttime':int(fields[19]),'proc_self_stat':raw}
        with (directory/'PROC_IDENTITY.json').open('x') as f:json.dump(identity,f,indent=2)
    receipt={'stage':stage,'charge_stage':stage,'command':command,'cwd':str(ROOT),'allocation_cpu_s':allocation,
             'stage_actual_cpu_already_paid_s':stage_paid,'stage_allocation_remaining_before_cpu_s':allocation_remaining,
             'remaining_total_before_cpu_s':available,'clipped_family_cpu_cap_s':cap,
             'RLIMIT_CPU_per_process_seconds':max(1,math.ceil(cap)),'RLIMIT_AS_bytes':LIMIT_BYTES,'wall_cap_s':30,'single_thread_environment':{k:environment[k] for k in THREAD_VARS},
             'resource_scope':'Authoritative wait4 and killpg use Popen namespace PID. /proc family guard uses child-reported /proc/self PID with matching starttime; no subtraction of unrelated historical counters. Tick-resolution guard, not an exact mathematical aggregate CPU limiter.',
             'parent_network_model_metadata_packaging_cost':'UNKNOWN_NOT_ZERO'}
    with (directory/'COMMAND.json').open('x') as f:json.dump(receipt,f,indent=2)
    started=time.monotonic();max_observed=0.;reason=None;identity=None;max_family_sample=[]
    with (directory/'stdout.txt').open('xb') as stdout,(directory/'stderr.txt').open('xb') as stderr:
        child=subprocess.Popen(command,cwd=ROOT,env=environment,stdout=stdout,stderr=stderr,preexec_fn=limits)
        while True:
            pid,status,usage=os.wait4(child.pid,os.WNOHANG)
            if pid:break
            if identity is None:
                identity=json.loads((directory/'PROC_IDENTITY.json').read_text())
                if identity['namespace_pid']!=child.pid:reason='NAMESPACE_PID_IDENTITY_MISMATCH'
            try:
                observed,sample=family_cpu(identity['proc_pid'],identity['proc_starttime'])
                if observed>=max_observed:max_observed=observed;max_family_sample=sample
            except RuntimeError:
                pid,status,usage=os.wait4(child.pid,os.WNOHANG)
                if pid:break
                reason='PROC_PID_STARTTIME_IDENTITY_MISMATCH';observed=0.
            if time.monotonic()-started>=30:reason='WALL_LIMIT'
            elif observed>=max(0.,cap-.03):reason='OBSERVED_PROCESS_FAMILY_CPU_LIMIT'
            if reason:
                try:os.killpg(child.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                _,status,usage=os.wait4(child.pid,0);break
            time.sleep(.01)
        child.returncode=os.waitstatus_to_exitcode(status)
        try:os.killpg(child.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    actual=usage.ru_utime+usage.ru_stime
    if identity is None and (directory/'PROC_IDENTITY.json').exists():identity=json.loads((directory/'PROC_IDENTITY.json').read_text())
    result_path=directory/'RESULT.json'
    result=json.loads(result_path.read_text()) if result_path.exists() else None
    counts=journal_counts(directory)
    passed=child.returncode==0 and reason is None and actual<=cap and spent+actual<=TOTAL_CPU and result is not None and result.get('pass') is True
    passed=passed and ledger.get('native_kernel_calls_known',0)+counts['native_kernel_calls_known']<=146
    record={**receipt,'directory':str(directory),'result':str(result_path) if result_path.exists() else None,'returncode':child.returncode,'watchdog_reason':reason,
            'wall_s':time.monotonic()-started,'actual_child_user_s':usage.ru_utime,'actual_child_system_s':usage.ru_stime,'actual_child_cpu_s':actual,
            'max_RSS_KiB':usage.ru_maxrss,'popen_namespace_pid':child.pid,'proc_identity':identity,
            'max_observed_family_cpu_s':max_observed,'max_family_cpu_sample':max_family_sample,'pass':passed,**counts}
    with (directory/'RESOURCE_RECEIPT.json').open('x') as f:json.dump(record,f,indent=2)
    ledger['attempts'].append(record)
    ledger['local_actual_cpu_s']=sum(x['actual_child_cpu_s'] for x in ledger['attempts'])
    ledger['total_known_scientific_cpu_s']=REMOTE_CPU+ledger['local_actual_cpu_s']
    ledger['remaining_known_cpu_s']=TOTAL_CPU-ledger['total_known_scientific_cpu_s']
    ledger['native_kernel_calls_known']=sum(x['native_kernel_calls_known'] for x in ledger['attempts'])
    ledger['unfinished_API_attempts_unknown']=sum(x['unfinished_API_attempts_unknown'] for x in ledger['attempts'])
    charges={}
    for attempt in ledger['attempts']:
        key=attempt.get('charge_stage',attempt['stage']);charges[key]=charges.get(key,0.)+attempt['actual_child_cpu_s']
    ledger['actual_cpu_by_charge_stage_s']=charges
    ledger['C6_actual_cpu_paid_s']=charges.get('C6',0.)
    ledger['C6_initial_allocation_remaining_s']=10.-charges.get('C6',0.)
    store(EXEC/'RESOURCE_LEDGER.json',ledger)
    state[stage]={'pass':passed,'result':record['result'],'resource_receipt':str(directory/'RESOURCE_RECEIPT.json')}
    store(EXEC/'STAGE_STATUS.json',state)
    print(json.dumps({'stage':stage,'pass':passed,'actual_child_cpu_s':actual,'known_total_scientific_cpu_s':ledger['total_known_scientific_cpu_s'],**counts}),flush=True)
    if not passed:raise RuntimeError('STAGE_FAILURE_PRESERVED_STOP_FOR_ASTRA:'+str(directory))

def main():
    if len(sys.argv)!=2 or sys.argv[1] not in ('C6','C7','C8'):raise SystemExit('usage: python3 code/run_stage.py C6|C7|C8')
    stage=sys.argv[1];EXEC.mkdir(exist_ok=True)
    lp=EXEC/'RESOURCE_LEDGER.json';sp=EXEC/'STAGE_STATUS.json'
    ledger=json.loads(lp.read_text()) if lp.exists() else {'schema':'ELECTRON_FIELD01_CUMULATIVE_RESOURCE_LEDGER_V1','total_cap_cpu_s':60.,'prior_remote_Wolfram_reported_cpu_s':REMOTE_CPU,'local_initial_remaining_cpu_s':59.93773,'attempts':[],
                 'old_or_foreign_budgets':'UNCHANGED_CLOSED_NONTRANSFERABLE','unknown_parent_network_model_costs':'UNKNOWN_NOT_ZERO'}
    state=json.loads(sp.read_text()) if sp.exists() else {}
    if stage=='C7' and not state.get('C6',{}).get('pass'):raise RuntimeError('C6_NOT_PASS')
    if stage=='C8' and not state.get('C7',{}).get('pass'):raise RuntimeError('C7_NOT_PASS')
    if stage=='C6':run_child('C6',10.,ledger,state)
    elif stage=='C7':run_child('C7',20.,ledger,state)
    else:
        run_child('C8_VALIDATE',20.,ledger,state)
        run_child('C8_PLOTS',10.,ledger,state)
        state['C8']={'pass':True,'validation':state['C8_VALIDATE'],'plots':state['C8_PLOTS']};store(sp,state)

if __name__=='__main__':main()

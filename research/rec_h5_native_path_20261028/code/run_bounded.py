"""One fixed research stage per invocation; no automatic retries or progression."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import signal
import subprocess
import sys
import time
from common import UNIT,REPO,check,dump,sha,verify_locks

CAPS={'build001':(30,60),'capture001':(60,120),'analysis001':(60,120),
      'controls001':(30,60),'figures001':(20,60)}

def copied_inputs(locks):
    required={'input.dat','Alpha_inf.dat','R_inf.dat','two_photon_tables.dat'}
    expected={Path(row['path']).name:row['sha256'] for row in locks['original_members']
              if Path(row['path']).name in required}
    check(set(expected)==required,'COPIED_NATIVE_INPUT_LOCKS_MISSING')
    actual={}
    for name,wanted in sorted(expected.items()):
        path=UNIT/'build/source'/name
        check(path.is_file(),'COPIED_NATIVE_INPUT_MISSING:'+name)
        observed=sha(path)
        check(observed==wanted,'COPIED_NATIVE_INPUT_MISMATCH:'+name)
        actual[name]={'path':str(path),'sha256':observed,'expected_sha256':wanted}
    return actual

def worker(mode,output):
    if mode=='build001':
        source=UNIT/'build/source'
        if not source.exists():
            from instrument import generate
            source=generate()
        generation=json.loads((UNIT/'build/SOURCE_GENERATION.json').read_text())
        for name,expected in generation['instrumented_files'].items():
            check(sha(source/name)==expected,'GENERATED_SOURCE_CHANGED:'+name)
        for name in ('capture_support.c','capture_support.h'):
            check(sha(source/name)==sha(UNIT/'code'/name),'CAPTURE_SUPPORT_COPY_CHANGED')
        actual_copied_inputs=copied_inputs(verify_locks())
        dump(output/'COPIED_NATIVE_INPUTS.json',actual_copied_inputs)
        compiler=shutil.which('gcc');check(compiler is not None,'GCC_NOT_FOUND')
        command=[compiler,'-std=c11','-D_DEFAULT_SOURCE','-O3','-Wall','-Wextra','-Wpedantic',
            '-DREC_H5_NATIVE_PATH_CAPTURE','hyrectools.c','helium.c','hydrogen.c','history.c','hyrec.c','capture_support.c',
            '-lm','-o',str(UNIT/'build/native_capture')]
        version=subprocess.run([compiler,'--version'],capture_output=True,text=True,check=True).stdout
        dump(output/'BUILD_COMMAND.json',{'argv':command,'cwd':str(source),'compiler_version':version,
             'observation_diff_sha256':sha(UNIT/'build/INSTRUMENTATION.diff'),
             'copied_native_inputs':actual_copied_inputs})
        with (output/'compiler.stdout.txt').open('x') as out,(output/'compiler.stderr.txt').open('x') as err:
            result=subprocess.run(command,cwd=source,stdout=out,stderr=err,check=False)
        check(result.returncode==0,'NATIVE_BUILD_FAILED')
        dump(output/'SUMMARY.json',{'status':'PASS','native_builds':1,'native_runs':0,'executable_sha256':sha(UNIT/'build/native_capture')})
        return
    if mode=='analysis001':
        from analyze import run
    elif mode=='controls001':
        from controls import run
    elif mode=='figures001':
        from plot_results import run
    else:raise ValueError('unknown worker mode')
    print(json.dumps(run(output),sort_keys=True))

def proc_group_cpu(pgid):
    # Sum own and already-reaped-child times over current group members.
    # Reaped descendants disappear, with their CPU transferred to parent cutime.
    ticks=os.sysconf('SC_CLK_TCK');total=0
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            text=(p/'stat').read_text();tail=text[text.rfind(')')+2:].split()
            if int(tail[2])==pgid:total+=sum(int(tail[k]) for k in (11,12,13,14))
        except (FileNotFoundError,ProcessLookupError,PermissionError,ValueError):continue
    return total/ticks

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=CAPS)
    p.add_argument('--worker',choices=CAPS);p.add_argument('--output',type=Path)
    args=p.parse_args();check(sys.version_info[:2]==(3,12),'PYTHON312_REQUIRED')
    if args.worker:
        check(args.output is not None,'WORKER_OUTPUT_REQUIRED');worker(args.worker,args.output);return
    check(args.mode is not None,'MODE_REQUIRED')
    mode=args.mode;cpu,wall=CAPS[mode];start_cpu=time.process_time();start=time.monotonic()
    output=UNIT/'results'/mode;output.mkdir(parents=True,exist_ok=False)
    started=datetime.now(timezone.utc).isoformat();locks=verify_locks()
    code_hashes={f.name:sha(f) for f in sorted((UNIT/'code').glob('*')) if f.is_file()}
    env=os.environ.copy()
    thread_keys=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS')
    for key in thread_keys:env[key]='1'
    env['PYTHONHASHSEED']='0';env['MPLCONFIGDIR']=str(output/'matplotlib_config')
    stdin=None;cwd=REPO;actual_copied_inputs=None;executable_sha256=None
    if mode=='build001' and (UNIT/'build/source').is_dir():actual_copied_inputs=copied_inputs(locks)
    if mode=='capture001':
        check((UNIT/'results/build001/SUMMARY.json').is_file(),'BUILD_DEPENDENCY_MISSING')
        build_summary=json.loads((UNIT/'results/build001/SUMMARY.json').read_text())
        check(build_summary['status']=='PASS','BUILD_DEPENDENCY_NOT_PASS')
        executable_sha256=sha(UNIT/'build/native_capture')
        check(executable_sha256==build_summary['executable_sha256'],'CAPTURE_EXECUTABLE_BUILD_IDENTITY_MISMATCH')
        actual_copied_inputs=copied_inputs(locks)
        dump(output/'COPIED_NATIVE_INPUTS.json',actual_copied_inputs)
        raw=output/'raw';raw.mkdir()
        context=json.loads((REPO/locks['retained_dependencies']['source_context']['path']).read_text())
        selected={5127}
        for row in context['queries']:selected.update((row['cell'],row['cell']+1))
        (raw/'SELECTED_SLOTS.txt').write_text(''.join(str(i)+'\n' for i in sorted(selected)))
        env['REC_H5_CAPTURE_DIR']=str(raw);cwd=UNIT/'build/source'
        stdin=(cwd/'input.dat').open('rb');command=[str(UNIT/'build/native_capture')]
    else:
        dependency={'analysis001':'capture001','controls001':'analysis001','figures001':'analysis001'}.get(mode)
        if dependency:check((UNIT/'results'/dependency/'SUMMARY.json').is_file() if dependency!='capture001' else (UNIT/'results/capture001/raw/CAPTURE_SUMMARY.json').is_file(),'MODE_DEPENDENCY_MISSING')
        command=[sys.executable,str(Path(__file__).resolve()),'--worker',mode,'--output',str(output)]
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
        if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    before=resource.getrusage(resource.RUSAGE_CHILDREN);timeout=False;cpu_stop=False;max_observed_cpu=0
    with (output/'stdout.txt').open('x') as out,(output/'stderr.txt').open('x') as err:
        proc=subprocess.Popen(command,cwd=cwd,env=env,stdin=stdin,stdout=out,stderr=err,preexec_fn=limits,start_new_session=True)
        while proc.poll() is None:
            elapsed=time.monotonic()-start;groupcpu=proc_group_cpu(proc.pid);max_observed_cpu=max(max_observed_cpu,groupcpu)
            if elapsed>=wall or groupcpu>=cpu:
                timeout=elapsed>=wall;cpu_stop=groupcpu>=cpu
                os.killpg(proc.pid,signal.SIGKILL);break
            try:proc.wait(timeout=.1)
            except subprocess.TimeoutExpired:pass
        exit_code=proc.wait()
    if stdin:stdin.close()
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    child_user=after.ru_utime-before.ru_utime;child_system=after.ru_stime-before.ru_stime
    wrapper_cpu=time.process_time()-start_cpu;total_cpu=child_user+child_system+wrapper_cpu
    lock_after=verify_locks()
    check(lock_after==locks,'IMMUTABLE_INPUT_METADATA_CHANGED')
    if mode=='capture001' and exit_code==0:
        dump(output/'SUMMARY.json',{'status':'PASS','native_trajectories':1,
            'raw_capture_summary':json.loads((output/'raw/CAPTURE_SUMMARY.json').read_text())})
    receipt={'schema':'REC_H5_NATIVE_PATH_BOUNDED_RUN_V1','mode':mode,'wrapper_argv':sys.argv,'child_argv':command,
        'cwd':str(cwd),'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
        'exit_code':exit_code,'wall_timeout':timeout,'aggregate_cpu_watchdog_stop':cpu_stop,
        'max_watched_process_group_cpu_s':max_observed_cpu,'inclusive_child_cpu_s':child_user+child_system,
        'child_user_cpu_s':child_user,'child_system_cpu_s':child_system,'wrapper_cpu_s':wrapper_cpu,
        'inclusive_stage_cpu_s':total_cpu,'wall_s':time.monotonic()-start,'peak_child_rss_kib':after.ru_maxrss,
        'limits':{'cpu_s':cpu,'wall_s':wall,'child_address_space_bytes':1024**3,'threads':1},
        'thread_environment':{key:env[key] for key in (*thread_keys,'PYTHONHASHSEED')},
        'code_sha256':code_hashes,'locked_input_snapshot':locks,'input_recheck':'PASS',
        'copied_native_inputs':actual_copied_inputs,'native_executable_sha256':executable_sha256,
        'python_version':sys.version,'platform':platform.platform(),'requested_executor':'lower-tier coding implementer',
        'runtime_model_identity':'NOT_EXPOSED_NOT_CLAIMED_VERIFIED'}
    dump(output/'RUN_RECEIPT.json',receipt);print(json.dumps(receipt,sort_keys=True))
    check(exit_code==0 and not timeout and not cpu_stop and total_cpu<=cpu,'BOUNDED_STAGE_FAILURE_PRESERVED')

if __name__=='__main__':main()

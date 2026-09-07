"""Local-only bounded target-grid runner with external process capture.

No Actions, installs, network requests, Git writes, or old test-suite replay.
The worker and renderer are separate; a test PASS is not a fitted convergence
order, physical-source admission, or a full solver result.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import csv
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REL='docs/research/rec_target_grid_refinement_20260907'
BASE='59dafbd34bc21b1b885c716b7b8cc899636bbd60'
BASE_TREE='c0d6a862567e111cfe92a6fd5a3c30051180e38e'
IDS=['test_01_common_measure_and_nested_partition','test_02_exact_quadratic_error_witness',
     'test_03_affine_and_odd_equilibria_and_nodal_entropy','test_04_weak_split_and_second_order_bounds',
     'test_05_independent_nonlinear_discrete_jvp','test_06_measure_blindness_and_packet_mutation']


def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args],text=True,timeout=30).strip()


def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def csvwrite(path,rows):
    if not rows:return
    with path.open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def manifest(out):
    files=sorted(p for p in out.rglob('*') if p.is_file() and p!=out/'SHA256SUMS')
    (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(out).as_posix()+'\n' for p in files),encoding='utf-8')


class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.per_id=[]
    def addSuccess(self,t):super().addSuccess(t);self.per_id.append({'id':t.id(),'outcome':'PASS'})
    def addFailure(self,t,e):super().addFailure(t,e);self.per_id.append({'id':t.id(),'outcome':'FAIL'})
    def addError(self,t,e):super().addError(t,e);self.per_id.append({'id':t.id(),'outcome':'ERROR'})
    def addSkip(self,t,why):super().addSkip(t,why);self.per_id.append({'id':t.id(),'outcome':'SKIP','reason':why})


def table_contrasts(rows):
    key=lambda row:tuple(row[k] for k in ('case','direction','read_kind','level','power'))
    base={key(x):x for x in rows if x['table']=='base'}
    output=[]
    for high in (x for x in rows if x['table']=='hires'):
        low=base[key(high)]
        output.append(dict(case=high['case'],direction=high['direction'],read_kind=high['read_kind'],
            level=high['level'],power=high['power'],nodes=high['nodes'],
            target_table_difference=high['M']-low['M'],
            direct_table_difference=high['reference_M']-low['reference_M'],
            target_error_difference=high['error']-low['error'],
            target_jvp_table_difference=high['dM']-low['dM'],
            direct_jvp_table_difference=high['reference_dM']-low['reference_dM'],
            target_jvp_error_difference=high['jvp_error']-low['jvp_error']))
    return output


def worker(out):
    out.mkdir(parents=True,exist_ok=False)
    report={'classification':'SETUP_OR_EXECUTION_FAILED','claim':'NO_PASS_REC_PHYSICAL_SPLIT',
            'physical_source_authenticated':False,'provider_admitted':False,
            'old_suites_replayed':False,'visual_audit':'NOT_PERFORMED','plots_generated':0}
    rc=2
    try:
        report['source_commit']=git('rev-parse','HEAD');report['source_tree']=git('rev-parse','HEAD^{tree}')
        import refinement as model
        import test_refinement as tests
        import numpy,scipy,mpmath
        report['environment']={m.__name__:{'version':m.__version__,'path':m.__file__} for m in (numpy,scipy,mpmath)}
        report['environment']['python']={'version':sys.version,'executable':sys.executable}
        report['pinned_source_blobs']={p:blob(ROOT/p) for p in model.PINS}
        if report['pinned_source_blobs']!=model.PINS:raise RuntimeError('changed immutable dependency')
        with (out/'unittest.log').open('w',encoding='utf-8') as handle:
            result=unittest.TextTestRunner(stream=handle,verbosity=2,resultclass=Result).run(
                unittest.defaultTestLoader.loadTestsFromTestCase(tests.Checks))
        report['tests']={'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
                         'skips':len(result.skipped),'per_id':result.per_id}
        report['observations']=tests.OBS
        for filename,rows in [('WEAK_MOMENTS.csv',tests.WEAK_ROWS),('STATE_MOMENTS.csv',tests.STATE_ROWS),
                              ('JVP_REFERENCE.csv',tests.JVP_ROWS),('BIN_SAMPLES.csv',tests.BIN_ROWS),
                              ('ATOMIC_TABLE_CONTRAST.csv',table_contrasts(tests.WEAK_ROWS))]:
            csvwrite(out/filename,rows)
        actual=[x['id'].rsplit('.',1)[-1] for x in result.per_id]
        okay=result.wasSuccessful() and not result.skipped and sorted(actual)==sorted(IDS) and result.testsRun==6
        report['pinned_source_blobs_after']={p:blob(ROOT/p) for p in model.PINS}
        okay=okay and report['pinned_source_blobs_after']==model.PINS
        report['classification']='PASS_BOUNDED_TARGET_GRID_DIAGNOSTIC' if okay else 'FAIL_TARGET_GRID_DIAGNOSTIC'
        report['empirical_convergence_order']='NOT_AUTOMATICALLY_CERTIFIED_BY_TEST_PASS'
        rc=0 if okay else 1
    except Exception:
        report['traceback']=traceback.format_exc()
    report['exit_code']=rc
    dump(out/'RESULT.json',report);manifest(out)
    print(json.dumps({'classification':report['classification'],'exit_code':rc,'tests':report.get('tests')},ensure_ascii=False))
    return rc


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--expected-source')
    parser.add_argument('--worker',action='store_true')
    parser.add_argument('--timeout',type=float,default=1200.)
    args=parser.parse_args();out=args.out.resolve()
    if out==ROOT or ROOT in out.parents:parser.error('output must be outside source worktree')
    if os.name!='posix' or os.environ.get('GITHUB_ACTIONS','').lower()=='true':
        parser.error('local POSIX execution only; GitHub Actions prohibited')
    if args.worker:return worker(out)
    if not args.expected_source or not 0<args.timeout<=3600:parser.error('expected-source and bounded timeout required')
    out.mkdir(parents=True,exist_ok=False)
    receipt={'classification':'PREFLIGHT_FAILED','started_utc':datetime.now(timezone.utc).isoformat(),
             'returncode':None,'timed_out':False,'claim':'NO_PASS_REC_PHYSICAL_SPLIT',
             'github_actions_used':False,'old_suites_replayed':False,'plots_generated':0,'visual_audit':'NOT_PERFORMED'}
    process=None;rc=2;start=time.monotonic()
    try:
        receipt['source_commit']=git('rev-parse','HEAD');receipt['source_tree']=git('rev-parse','HEAD^{tree}')
        if receipt['source_commit']!=args.expected_source:raise RuntimeError('unexpected execution commit')
        if git('rev-parse',BASE+'^{tree}')!=BASE_TREE:raise RuntimeError('base tree mismatch')
        git('merge-base','--is-ancestor',BASE,'HEAD')
        if git('status','--porcelain','--untracked-files=all'):raise RuntimeError('clean committed source required')
        changed=git('diff','--name-only',BASE,'HEAD').splitlines();receipt['changed_paths']=changed
        if any(not p.startswith(REL+'/') for p in changed):raise RuntimeError('change outside research scope')
        receipt['own_source_blobs']={p.name:blob(p) for p in HERE.glob('*.py')}
        command=[sys.executable,'-B',str(Path(__file__).resolve()),'--worker','--out',str(out/'payload')]
        receipt.update(argv=command,cwd=str(ROOT),classification='RUNNING')
        dump(out/'PROCESS.json',receipt)
        environment=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
            process=subprocess.Popen(command,cwd=ROOT,env=environment,stdout=stdout,stderr=stderr,start_new_session=True)
            receipt['pid']=process.pid
            dump(out/'PROCESS.json',receipt)
            try:process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                receipt['timed_out']=True
                try:os.killpg(process.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:os.killpg(process.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    process.wait()
        receipt['returncode']=process.returncode
        receipt['classification']='TIMED_OUT' if receipt['timed_out'] else 'EXITED'
        dump(out/'PROCESS.json',receipt)
        report=json.loads((out/'payload/RESULT.json').read_text(encoding='utf-8'))
        tests=report.get('tests',{});ids=[x.get('id','').rsplit('.',1)[-1] for x in tests.get('per_id',[])]
        good=(process.returncode==0 and not receipt['timed_out'] and report.get('exit_code')==0
              and report.get('classification')=='PASS_BOUNDED_TARGET_GRID_DIAGNOSTIC'
              and tests.get('run')==6 and sorted(ids)==sorted(IDS)
              and all(tests.get(k)==0 for k in ('failures','errors','skips'))
              and all(x.get('outcome')=='PASS' for x in tests.get('per_id',[]))
              and report.get('source_commit')==receipt['source_commit']
              and report.get('source_tree')==receipt['source_tree']
              and report.get('physical_source_authenticated') is False and report.get('provider_admitted') is False
              and report.get('claim')==receipt['claim'])
        receipt['final_git_status']=git('status','--porcelain','--untracked-files=all')
        receipt['own_source_blobs_after']={p.name:blob(p) for p in HERE.glob('*.py')}
        good=good and not receipt['final_git_status'] and receipt['own_source_blobs_after']==receipt['own_source_blobs']
        receipt['result_contract_ok']=bool(good);rc=0 if good else 1
    except BaseException:
        receipt['traceback']=traceback.format_exc()
        if process is not None and process.poll() is None:
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            process.wait()
        if process is not None:receipt['returncode']=process.poll()
    receipt.update(wrapper_exit_code=rc,elapsed_seconds=time.monotonic()-start,
                   finished_utc=datetime.now(timezone.utc).isoformat())
    dump(out/'PROCESS.json',receipt);manifest(out)
    print(json.dumps(receipt,ensure_ascii=False))
    return rc


if __name__=='__main__':raise SystemExit(main())

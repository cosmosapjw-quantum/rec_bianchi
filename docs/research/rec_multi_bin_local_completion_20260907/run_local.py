"""Local-only supervisor for the existing PR79 study and its supplement.

No installation, network request, Git write or Actions call. Outputs and raw
process logs stay outside the clean worktree. Authored is not executed.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = '2e3b73972ee298d44efdfb10016e314f58b0bada'
BASE_TREE = '471442ce757fde701340729cd1abde281fd0db01'
OLD = 'docs/research/rec_multi_bin_affinity_20260907'
NEW = 'docs/research/rec_multi_bin_local_completion_20260907'
PROTECTED = ['src','tests','archive','.github/workflows',
             'docs/research/rec_2s_base_hires_response',
             'docs/research/rec_affinity_compatibility_20260907',
             'docs/research/rec_fixed_map_single_field_jvp_20260907']
EXPECTED = {
    'original': ['test_01_original_tables_and_fixed_partition',
                 'test_02_binwise_affinity_and_both_normalizations',
                 'test_03_common_population_aggregate_counterexample',
                 'test_04_composite_jvp_against_independent_nonlinear_primal',
                 'test_05_finite_nonthermal_null_and_its_tangent',
                 'test_06_multi_bin_linearized_metric_and_rank',
                 'test_07_invalid_input_and_no_mutation'],
    'supplement': ['test_01_full_left_kernel_and_energy_dependence',
                   'test_02_actual_count_source_and_density_direction',
                   'test_03_stationary_manifold_and_four_right_null_vectors',
                   'test_04_missing_photon_axes_against_independent_primal'],
}
SCRIPTS = {'original':OLD+'/run_study.py','supplement':NEW+'/verify_nullspace.py'}


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def git(record, *args) -> str:
    command = ['git','-C',str(ROOT),*args]
    p = subprocess.run(command,capture_output=True,text=True,timeout=30)
    record.setdefault('git_reads',[]).append({'argv':command,'returncode':p.returncode,
                                             'stdout':p.stdout,'stderr':p.stderr})
    if p.returncode:
        raise RuntimeError('Git read failed: '+repr(args))
    return p.stdout.strip()


def check_result(lane: str, report, actual_rc) -> bool:
    if not isinstance(report,dict):
        return False
    tests = report.get('tests')
    if not isinstance(tests,dict):
        return False
    per_id = tests.get('per_id')
    if not isinstance(per_id,list) or not all(isinstance(x,dict) for x in per_id):
        return False
    if not all(isinstance(x.get('id'),str) for x in per_id):
        return False
    ids = [x['id'].rsplit('.',1)[-1] for x in per_id]
    return (actual_rc == 0 and report.get('exit_code') == 0
            and tests.get('run') == len(EXPECTED[lane])
            and all(tests.get(k) == 0 for k in ('failures','errors','skips'))
            and sorted(ids) == sorted(EXPECTED[lane])
            and all(x.get('outcome') == 'PASS' for x in per_id)
            and report.get('claim') == 'NO_PASS_REC_PHYSICAL_SPLIT'
            and report.get('physical_source_authenticated') is False
            and report.get('provider_admitted') is False)


def stop_process_group(process) -> None:
    if process.poll() is None:
        try:
            os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def execute(lane: str, out: Path, python: str, timeout: float, identity: dict) -> dict:
    lane_dir = out/lane
    lane_dir.mkdir()
    payload = lane_dir/'payload'
    command = [python,'-B',str(ROOT/SCRIPTS[lane]),'--out',str(payload)]
    receipt = {'lane':lane,'argv':command,'cwd':str(ROOT),
               'source_commit':identity['source_commit'],'source_tree':identity['source_tree'],
               'started_utc':datetime.now(timezone.utc).isoformat(),
               'status':'NOT_STARTED','returncode':None,'timed_out':False}
    dump(lane_dir/'PROCESS.json',receipt)
    started = time.monotonic()
    process = None
    environment = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(out/'matplotlib_cache'))
    try:
        with (lane_dir/'stdout.log').open('wb') as stdout, (lane_dir/'stderr.log').open('wb') as stderr:
            process = subprocess.Popen(command,cwd=ROOT,env=environment,stdout=stdout,stderr=stderr,
                                       start_new_session=True)
            receipt.update(status='RUNNING',pid=process.pid)
            dump(lane_dir/'PROCESS.json',receipt)
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                receipt['timed_out'] = True
                stop_process_group(process)
            receipt['status'] = 'TIMED_OUT' if receipt['timed_out'] else 'EXITED'
    except BaseException:
        receipt['launch_or_capture_exception'] = traceback.format_exc()
        receipt['status'] = 'PROCESS_OR_CAPTURE_ERROR'
        if process is not None:
            stop_process_group(process)
    finally:
        if process is not None:
            receipt['returncode'] = process.poll()
        receipt['wall_seconds'] = time.monotonic()-started
        receipt['finished_utc'] = datetime.now(timezone.utc).isoformat()
        # Preserve actual process disposition before interpreting child JSON.
        dump(lane_dir/'PROCESS.json',receipt)
    report = None
    try:
        report = json.loads((payload/'RESULT.json').read_text(encoding='utf-8'))
    except (OSError,ValueError):
        receipt['result_read_error'] = traceback.format_exc()
    receipt['result_contract_ok'] = check_result(lane,report,receipt['returncode']) and not receipt['timed_out']
    if lane == 'original' and isinstance(report,dict):
        receipt['result_contract_ok'] = receipt['result_contract_ok'] and (
            report.get('source_commit') == identity['source_commit']
            and report.get('source_tree') == identity['source_tree'])
        receipt['plot_generated'] = report.get('plot_generated',False)
        receipt['plot_error'] = report.get('plot_error')
    dump(lane_dir/'PROCESS.json',receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--expected-source',required=True)
    parser.add_argument('--python',default=sys.executable)
    parser.add_argument('--only',choices=('all','original','supplement'),default='all')
    parser.add_argument('--timeout',type=float,default=1200.)
    args = parser.parse_args()
    out = args.out.resolve()
    if out == ROOT or ROOT in out.parents:
        parser.error('output must be outside the Git worktree')
    if not 0 < args.timeout <= 3600:
        parser.error('timeout must be in (0,3600] seconds per lane')
    out.mkdir(parents=True,exist_ok=False)
    record = {'classification':'PREFLIGHT_NOT_COMPLETED','base':BASE,'base_tree':BASE_TREE,
              'github_actions_used':False,'claim':'NO_PASS_REC_PHYSICAL_SPLIT',
              'physical_source_authenticated':False,'provider_admitted':False,
              'visual_audit':'NOT_PERFORMED','lanes':[]}
    rc = 2
    try:
        if os.name != 'posix' or os.environ.get('GITHUB_ACTIONS','').lower() == 'true':
            raise RuntimeError('local POSIX execution only; GitHub Actions is prohibited')
        record['source_commit'] = git(record,'rev-parse','HEAD')
        record['source_tree'] = git(record,'rev-parse','HEAD^{tree}')
        if record['source_commit'] != args.expected_source:
            raise RuntimeError('actual checkout differs from --expected-source')
        if git(record,'rev-parse',BASE+'^{tree}') != BASE_TREE:
            raise RuntimeError('PR79 base-tree mismatch')
        git(record,'merge-base','--is-ancestor',BASE,'HEAD')
        if git(record,'status','--porcelain','--untracked-files=all'):
            raise RuntimeError('execution worktree must be clean and committed')
        git(record,'diff','--exit-code',BASE,'HEAD','--',*PROTECTED)
        changed = git(record,'diff','--name-only',BASE,'HEAD').splitlines()
        if any(not (p.startswith(OLD+'/') or p.startswith(NEW+'/')) for p in changed):
            raise RuntimeError('change outside the two bounded research directories')
        record['changed_paths'] = changed
        record['source_files'] = {p:git(record,'rev-parse','HEAD:'+p) for p in
            [OLD+'/study.py',OLD+'/test_study.py',OLD+'/run_study.py',NEW+'/verify_nullspace.py',NEW+'/run_local.py']}
        record['classification'] = 'PREFLIGHT_COMPLETE_EXECUTION_PENDING'
        dump(out/'LOCAL_RETURN.json',record)
        selected = ['original','supplement'] if args.only == 'all' else [args.only]
        for lane in selected:
            receipt = execute(lane,out,args.python,args.timeout,record)
            record['lanes'].append(receipt)
            dump(out/'LOCAL_RETURN.json',record)
            if not receipt['result_contract_ok']:
                break
        record['final_status'] = git(record,'status','--porcelain','--untracked-files=all')
        ok = len(record['lanes']) == len(selected) and all(x['result_contract_ok'] for x in record['lanes'])
        ok = ok and not record['final_status']
        record['classification'] = ('PASS_BOUNDED_LOCAL_MULTI_BIN_AND_NULLSPACE' if args.only == 'all'
                                    else 'PASS_SELECTED_LOCAL_LANE_NOT_FULL_CLOSEOUT') if ok else 'FAIL_OR_INCOMPLETE_LOCAL_RESEARCH'
        rc = 0 if ok else 1
    except Exception:
        record['classification'] = 'PREFLIGHT_OR_CAPTURE_FAILED'
        record['traceback'] = traceback.format_exc()
    record['wrapper_exit_code'] = rc
    dump(out/'LOCAL_RETURN.json',record)
    members = sorted(p for p in out.rglob('*') if p.is_file() and 'matplotlib_cache' not in p.parts)
    (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(out))+'\n'
                                       for p in members),encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())

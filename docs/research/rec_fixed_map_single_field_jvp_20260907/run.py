"""고정 연구 checker. 성공·실패·실행 소스와 원본 component identity를 기록한다."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PINS={
 'src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py':'26ddc41e24fadf0bdd19f1924e1a429d602d9c19',
 'src/full_bianchi_hyrec/trajectory/com_source_deposition.py':'a3662cf399f14b7148d880266825be12baf934a0'}

def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()

def blob(p):
    b=p.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

class TrackedResult(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.per_id=[]
    def addSuccess(self,test):super().addSuccess(test);self.per_id.append({'id':test.id(),'outcome':'PASS'})
    def addFailure(self,test,err):super().addFailure(test,err);self.per_id.append({'id':test.id(),'outcome':'FAIL'})
    def addError(self,test,err):super().addError(test,err);self.per_id.append({'id':test.id(),'outcome':'ERROR'})
    def addSkip(self,test,reason):super().addSkip(test,reason);self.per_id.append({'id':test.id(),'outcome':'SKIP','reason':reason})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    r={'classification':'NOT_COMPLETED','claim':'NO_PASS_REC_PHYSICAL_SPLIT',
       'physical_source_authenticated':False,'provider_admitted':False,
       'original_bass_replayed':False,'production_changed':False,'visual_audit':'NOT_PERFORMED'}
    rc=2
    try:
        r.update(source_commit=git('rev-parse','HEAD'),source_tree=git('rev-parse','HEAD^{tree}'),
                 source_parent=git('rev-parse','HEAD^'),workflow_sha=os.getenv('GITHUB_WORKFLOW_SHA'),
                 command=[sys.executable,*sys.argv],cwd=os.getcwd(),initial_status=git('status','--porcelain'))
        r['source_blobs']={p:blob(ROOT/p) for p in PINS}
        if r['source_blobs']!=PINS:raise RuntimeError('관측 대상 원본 blob 불일치')
        if r['initial_status']:raise RuntimeError('실행 checkout이 깨끗하지 않음')
        import numpy as np
        import scipy
        import mpmath
        import sympy
        import test_composite as tests
        import composite_probe as model
        r['environment']={'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
                         'sympy':sympy.__version__,'mpmath':mpmath.__version__}
        r['original_module_paths']={c.__name__:sys.modules[c.__module__].__file__ for c in
              (model.PhysicalTwoPhotonRamanBin,model.COMSourceDepositionPlan)}
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.Checks)
        with (out/'unittest.log').open('w',encoding='utf-8') as h:
            result=unittest.TextTestRunner(stream=h,verbosity=2,resultclass=TrackedResult).run(suite)
        r['tests']={'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
                    'skips':len(result.skipped),'per_id':result.per_id}
        r['observations']=tests.OBSERVATIONS
        r['final_status']=git('status','--porcelain')
        r['core_blobs_unchanged']=all(blob(ROOT/p)==v for p,v in PINS.items())
        good=result.wasSuccessful() and result.testsRun==10 and not result.skipped
        good=good and not r['final_status'] and r['core_blobs_unchanged']
        rc=0 if good else 1
        r['classification']='PASS_BOUNDED_FIXED_MAP_SINGLE_FIELD_COMPOSITE_JVP' if good else 'FAIL_FIXED_MAP_SINGLE_FIELD_COMPOSITE_JVP'
    except Exception:
        r['classification']='SETUP_OR_EXECUTION_FAILED';r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.monotonic()-start;r['exit_code']=rc
    (out/'RESULT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    files=sorted(p for p in out.iterdir() if p.is_file())
    (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files),encoding='utf-8')
    print('RESULT_BEGIN');print(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False));print('RESULT_END')
    if (out/'unittest.log').exists():print((out/'unittest.log').read_text(encoding='utf-8'))
    return rc

if __name__=='__main__':raise SystemExit(main())

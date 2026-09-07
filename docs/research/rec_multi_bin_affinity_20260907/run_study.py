"""고정 소스 실행·원본 수치·출력·그림을 분리하여 보존한다."""
from __future__ import annotations
import argparse
import csv
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


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()


def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def csvwrite(path,rows):
    if not rows:return
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


class Result(unittest.TextTestResult):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.per_id=[]
    def addSuccess(self,t):super().addSuccess(t);self.per_id.append({'id':t.id(),'outcome':'PASS'})
    def addFailure(self,t,e):super().addFailure(t,e);self.per_id.append({'id':t.id(),'outcome':'FAIL'})
    def addError(self,t,e):super().addError(t,e);self.per_id.append({'id':t.id(),'outcome':'ERROR'})
    def addSkip(self,t,why):super().addSkip(t,why);self.per_id.append({'id':t.id(),'outcome':'SKIP','reason':why})


def plot(out,tests):
    import math
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import study as m
    data=[]
    fig,ax=plt.subplots(figsize=(7,4.3),layout='constrained')
    for t in tests.TABLES:
        r=m.compose(t,m.state(),kind='log_control')
        ax.plot(t['ut'],r['delta'],'.' if t['label']=='base' else 'x',ms=3,label=t['label']+' log-read')
    ax.set(xlabel='Tracked photon energy / E21',ylabel='Read affinity minus scatter affinity',
           title='Fixed five-node manufactured photon state')
    ax.legend();fig.savefig(out/'bin_affinity.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.3),layout='constrained')
    delta=tests.OBS['construction']['effective_defects']
    etas=np.linspace(-2*max(delta.values()),max(delta.values())/2,81)
    for t in tests.TABLES:
        for kind,ls in [('chi','-'),('log_control','--')]:
            r=m.compose(t,m.state(),kind=kind);n=t['n'];ft=r['legs'][:n];fc=r['legs'][n:]
            P=math.fsum(t['normalized']*(1+ft)*(1+fc));Q=math.fsum(t['normalized']*ft*fc)
            values=[]
            for eta in etas:
                rho=math.exp(float(eta)-2);xg=(9/16)/(1+rho)
                sigma=float(eta)*xg*(rho*P-Q)
                values.append(sigma)
                data.append({'table':t['label'],'read':kind,'eta':float(eta),'entropy_per_H_kB_s':sigma,
                             'role':'analytic aggregate at fixed manufactured thermal nodal state'})
            ax.plot(etas,values,linestyle=ls,label=t['label']+' '+kind)
    ax.axhline(0,linewidth=.7);ax.axvline(tests.ETA,linestyle=':',linewidth=.8)
    ax.set(xlabel='eta = log(x_upper / x_ground) + 2',ylabel='Entropy / (N_H k_B) per second',
           title='Number/energy conservation does not fix entropy compatibility')
    ax.legend();fig.savefig(out/'aggregate_entropy.png',dpi=160);plt.close(fig)
    csvwrite(out/'ENTROPY_CURVE.csv',data)
    return matplotlib.__version__


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    r={'classification':'NOT_COMPLETED','claim':'NO_PASS_REC_PHYSICAL_SPLIT',
       'physical_source_authenticated':False,'provider_admitted':False,
       'original_bass_replayed':False,'previous_studies_replayed':False,
       'visual_audit':'NOT_PERFORMED','plot_generated':False}
    start=time.monotonic();rc=2
    try:
        import study as model
        r.update(source_commit=git('rev-parse','HEAD'),source_tree=git('rev-parse','HEAD^{tree}'),
                 source_parent=git('rev-parse','HEAD^'),workflow_sha=os.getenv('GITHUB_WORKFLOW_SHA'),
                 command=[sys.executable,*sys.argv],cwd=os.getcwd(),initial_status=git('status','--porcelain'))
        r['source_blobs']={p:blob(ROOT/p) for p in model.PINS}
        if r['source_blobs']!=model.PINS or r['initial_status']:
            raise RuntimeError('원본 바이트 또는 clean 실행 전제 불일치')
        import numpy,scipy,mpmath,sympy
        import test_study as tests
        r['environment']={'python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,
                          'mpmath':mpmath.__version__,'sympy':sympy.__version__}
        r['original_module_paths']={c.__name__:sys.modules[c.__module__].__file__ for c in
                                   (model.PhysicalTwoPhotonRamanBin,model.COMSourceDepositionPlan)}
        with (out/'unittest.log').open('w',encoding='utf-8') as h:
            res=unittest.TextTestRunner(stream=h,verbosity=2,resultclass=Result).run(
                unittest.defaultTestLoader.loadTestsFromTestCase(tests.Checks))
        r['tests']={'run':res.testsRun,'failures':len(res.failures),'errors':len(res.errors),
                    'skips':len(res.skipped),'per_id':res.per_id}
        r['observations']=tests.OBS
        csvwrite(out/'BIN_DIAGNOSTICS.csv',tests.BINS)
        csvwrite(out/'CASE_SUMMARY.csv',tests.OBS.get('cases',[]))
        csvwrite(out/'JVP_COMPARISON.csv',tests.OBS.get('jvp',{}).get('rows',[]))
        if res.wasSuccessful() and res.testsRun==7 and not res.skipped:
            try:
                r['environment']['matplotlib']=plot(out,tests);r['plot_generated']=True
            except Exception:
                r['plot_error']=traceback.format_exc()
        r['final_status']=git('status','--porcelain')
        r['source_blobs_after']={p:blob(ROOT/p) for p in model.PINS}
        good=res.wasSuccessful() and res.testsRun==7 and not res.skipped and not r['final_status']
        good=good and r['source_blobs_after']==model.PINS
        rc=0 if good else 1
        r['classification']='PASS_BOUNDED_MULTI_BIN_AFFINITY_JVP' if good else 'FAIL_MULTI_BIN_AFFINITY_JVP'
    except Exception:
        r['classification']='SETUP_OR_EXECUTION_FAILED';r['traceback']=traceback.format_exc()
    r['exit_code']=rc;r['elapsed_seconds']=time.monotonic()-start
    dump(out/'RESULT.json',r)
    summary=dict(r);obs=r.get('observations',{})
    summary['observations']={k:v for k,v in obs.items() if k not in ('cases','jvp','linearization')}
    summary['observations']['jvp']={k:v for k,v in obs.get('jvp',{}).items() if k!='rows'}
    summary['observations']['linearization']=[{k:v for k,v in x.items() if k!='count_jacobian'} for x in obs.get('linearization',[])]
    dump(out/'SUMMARY.json',summary)
    files=sorted(p for p in out.iterdir() if p.is_file())
    (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files),encoding='ascii')
    print('SUMMARY_BEGIN');print(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False));print('SUMMARY_END')
    if (out/'unittest.log').exists():print((out/'unittest.log').read_text(encoding='utf-8'))
    print((out/'SHA256SUMS').read_text())
    return rc

if __name__=='__main__':raise SystemExit(main())

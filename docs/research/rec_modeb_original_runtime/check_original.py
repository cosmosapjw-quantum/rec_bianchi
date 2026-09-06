"""고정 원본 API 실행. 제조 진단과 물리 입력 인증을 구분한다."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import traceback
import unittest
from fractions import Fraction as F
from types import SimpleNamespace

BASS_REF = '9d1c702ddf58549a06b29965a3d1b790a0c23159'
REC_BASE = '823cf1c25abda5343be6020bbf0b5bedb131fc3e'
PINS = {
    'bass:bianchi/q/modeb.py': '4df8421ab81459a448fff174286a03d1d38423c3',
    'bass:_rustcore/src/kinetic/radial.rs': 'ec946fced75e80201d516d1368c77eee87afd5b2',
    'bass:_rustcore/src/kinetic/comoving.rs': 'a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84',
    'rec:src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py': '26ddc41e24fadf0bdd19f1924e1a429d602d9c19',
    'rec:src/full_bianchi_hyrec/trajectory/com_source_deposition.py': 'a3662cf399f14b7148d880266825be12baf934a0',
}
parser = argparse.ArgumentParser()
parser.add_argument('--bass', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
OUT = args.out.resolve()
OUT.mkdir(parents=True, exist_ok=True)
REC = Path(__file__).resolve().parents[3]
BASS = args.bass.resolve()
result = {'classification': 'NOT_COMPLETED', 'commands': [], 'checks': {},
          'physical_source_authenticated': False, 'provider_admitted': False,
          'claim': 'NO_PASS_REC_PHYSICAL_SPLIT', 'visual_audit': 'NOT_PERFORMED'}

def command(argv, name, cwd=None):
    p = subprocess.run([str(x) for x in argv], cwd=cwd, text=True, capture_output=True, timeout=120)
    (OUT/(name+'.stdout')).write_text(p.stdout, encoding='utf-8')
    (OUT/(name+'.stderr')).write_text(p.stderr, encoding='utf-8')
    result['commands'].append({'argv':[str(x) for x in argv], 'cwd':str(cwd or Path.cwd()),
                               'exit_code':p.returncode, 'stdout':name+'.stdout', 'stderr':name+'.stderr'})
    if p.returncode:
        raise RuntimeError(f'{name}: exit={p.returncode}: {p.stderr[:500]}')
    return p.stdout.strip()

def git(root, *a):
    return subprocess.check_output(['git','-C',str(root),*a], text=True).strip()

def blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def save():
    (OUT/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    paths = sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
    (OUT/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in paths),encoding='utf-8')

try:
    result['source_commit'] = git(REC,'rev-parse','HEAD')
    result['source_tree'] = git(REC,'rev-parse','HEAD^{tree}')
    result['source_parent'] = git(REC,'rev-parse','HEAD^')
    result['workflow_sha'] = os.environ.get('GITHUB_WORKFLOW_SHA')
    result['trigger'] = os.environ.get('GITHUB_EVENT_NAME')
    if git(BASS,'rev-parse','HEAD') != BASS_REF:
        raise ValueError('BASS 고정 source 불일치')
    command(['git','-C',REC,'merge-base','--is-ancestor',REC_BASE,'HEAD'],'rec_ancestry')
    result['source_blobs'] = {}
    for key, expected in PINS.items():
        owner, path = key.split(':',1)
        actual = blob((BASS if owner=='bass' else REC)/path)
        result['source_blobs'][key] = actual
        if actual != expected:
            raise ValueError(f'원본 바이트 불일치: {key}')
    result['initial_status'] = {'rec':git(REC,'status','--porcelain'), 'bass':git(BASS,'status','--porcelain')}
    if any(result['initial_status'].values()):
        raise ValueError('격리 checkout이 처음부터 깨끗하지 않음')
    import numpy as np
    import scipy
    import sympy as sp
    import mpmath as mp
    mp.mp.dps = 80
    sys.path[:0] = [str(REC/'src'),str(BASS)]
    from bianchi.q.modeb import ModeBState
    from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import PhysicalTwoPhotonRamanBin
    from full_bianchi_hyrec.trajectory.com_source_deposition import COMSourceDepositionPlan
    result['environment'] = {'python':sys.version, 'numpy':np.__version__, 'scipy':scipy.__version__,
                             'sympy':sp.__version__, 'mpmath':mp.__version__}
    result['python_module_paths'] = {
        'ModeBState':sys.modules[ModeBState.__module__].__file__,
        'PhysicalTwoPhotonRamanBin':sys.modules[PhysicalTwoPhotonRamanBin.__module__].__file__,
        'COMSourceDepositionPlan':sys.modules[COMSourceDepositionPlan.__module__].__file__}
    result['rustc'] = command(['rustc','--version','--verbose'],'rustc_version')
    template = Path(__file__).with_name('radial_driver.rs.in').read_text(encoding='utf-8')
    driver = OUT/'radial_driver.rs'
    driver.write_text(template.replace('__RADIAL_PATH__',str(BASS/'_rustcore/src/kinetic/radial.rs')),encoding='utf-8')
    binary = OUT/'radial_driver'
    command(['rustc','--edition=2021','-O',driver,'-o',binary],'rust_compile')
    raw = command([binary],'rust_run')
    rows = [json.loads(line) for line in raw.splitlines()]
    if len(rows)!=8:
        raise ValueError('원본 Rust의 예상8개 호출 행 누락')
    result['native_radial_rows'] = rows
    EPS = np.finfo(float).eps
    TOL = 128*EPS
    E0 = 2.0**-60
    H_PLANCK = 6.62607015e-34
    pair = PhysicalTwoPhotonRamanBin('two_photon',1.0,3*E0/H_PLANCK,E0/H_PLANCK,
                                     2*E0/H_PLANCK,1/16,1/2,1.0)

    class Checks(unittest.TestCase):
        def close(self, actual, expected):
            self.assertTrue(math.isfinite(float(actual)))
            self.assertLessEqual(abs(float(actual)-float(expected)),TOL*max(1,abs(float(expected))))

        def test_01_exact_log_time_jvp(self):
            f,eta,k,H=F(2),F(1,4),F(3,4),F(4)
            df,de,dk,dhlog=F(1,8),F(1,2),F(-1,4),F(1,8)
            C=eta*(1+f)-k*f
            dC=(1+f)*de-f*dk+(eta-k)*df
            G=C/(H*f)
            dG=dC/(H*f)-G*(df/f+dhlog)
            self.assertEqual((C,dC,G,dG),(F(-3,4),F(31,16),F(-3,32),F(133,512)))
            ff,ee,kk,hh,dff,dee,dkk,dhh=sp.symbols('f e k h df de dk dh',positive=True)
            expr=(ee*(1+ff)-kk*ff)/(hh*ff)
            exact=sum(sp.diff(expr,x)*dx for x,dx in [(ff,dff),(ee,dee),(kk,dkk),(hh,dhh)])
            chain=((1+ff)*dee-ff*dkk+(ee-kk)*dff)/(hh*ff)-expr*(dff/ff+dhh/hh)
            self.assertEqual(sp.cancel(exact-chain),0)
            result['checks']['log_time']={'C':str(C),'dC':str(dC),'G':str(G),'dG':str(dG),'symbolic_residual':0}

        def test_02_actual_modeb_layout(self):
            # 크기만 제공하는 객체. native sphere나 물리 구적 인증은 아니다.
            shape = SimpleNamespace(n=2)
            y=np.log(np.array([1,2,4,8,16,32],dtype=float))
            state=ModeBState(shape,n_p=3,lnq_min=0.,lnq_max=math.log(4),lnf=y.copy())
            packed=state.pack()
            self.assertEqual(packed.shape,(31,))
            np.testing.assert_array_equal(packed[25:],y)
            other=ModeBState(shape,n_p=3,lnq_min=0.,lnq_max=math.log(4))
            other.set_from(packed)
            np.testing.assert_array_equal(other.pack(),packed)
            np.testing.assert_allclose(other.q(),[1,2,4],rtol=TOL,atol=0)
            self.assertEqual(other.lnf.reshape(2,3)[1,0],y[3])
            result['checks']['modeb']={'pack_length':31,'photon_offset':25,'layout':'angle_major',
                                      'native_sphere':False,'evolve_called':False,'module_called':True}

        def test_03_original_radial_order2(self):
            for row in rows[:2]:
                self.assertEqual(row['offsets'],[-1,0])
                self.assertEqual(row['weights'],[0.5,0.5])
                self.assertEqual(row['indices'],[0,1])
                self.assertTrue(row['tail_equal'])
            self.close(rows[0]['value'],2)
            self.close(rows[1]['value'],mp.mpf(1)/mp.sqrt(15))
            result['checks']['radial2']={'powerlaw':rows[0]['value'],'planck_read':rows[1]['value'],
                                        'reference':mp.nstr(1/mp.sqrt(15),60),'original_rust_called':True}

        def test_04_actual_paired_api(self):
            exact=pair.net_action(1.,1/3)
            approx=pair.net_action(1.,rows[1]['value'])
            reference=(1-3/mp.sqrt(15))/8
            self.close(exact,0)
            self.close(approx,reference)
            self.assertGreater(approx,0)
            Fwd,Rev=pair.paired_rates(companion_occupation=1.,tracked_occupation=rows[1]['value'])
            jt=pair.jvp(companion_occupation=1.,tracked_occupation=rows[1]['value'],
                         d_integrated_rate_s_inv=0.,d_upper_population=0.,d_ground_population=0.,
                         d_companion_occupation=0.,d_tracked_occupation=1.)
            self.close(jt,-3/8)
            result['checks']['paired']={'exact_planck_net':exact,'interpolated_net':approx,'forward':Fwd,'reverse':Rev,
                                        'tracked_partial':jt,'reference':mp.nstr(reference,60),'units':'H^-1 s^-1'}

        def test_05_original_order8_roundoff(self):
            observations=[]
            for row in rows[2:]:
                w=list(map(mp.mpf,row['weights']));y=list(map(mp.mpf,row['input_y']))
                ref=mp.fsum(a*b for a,b in zip(w,y))
                scale=mp.fsum(abs(a*b) for a,b in zip(w,y))
                nops=2*len(w)+2
                bound=mp.mpf(nops)*mp.mpf(float(EPS))/(1-mp.mpf(nops)*mp.mpf(float(EPS)))*scale
                residual=abs(mp.mpf(row['ln_value'])-ref)
                self.assertLessEqual(residual,bound)
                self.assertTrue(row['tail_equal'])
                exact=1/mp.expm1(mp.log(2)*row['q'])
                observations.append({'n':row['n'],'q':row['q'],'occupation':row['value'],
                    'planck_approximation_error':float(mp.mpf(row['value'])-exact),
                    'log_dot_roundoff':float(residual),'roundoff_bound':float(bound),
                    'approximation_tolerance_gate':False})
            result['checks']['order8']=observations

        def test_06_geometry_and_measure(self):
            M=sp.diag(2,1,sp.Rational(1,2))
            sx=sp.sqrt((M*sp.Matrix([1,0,0])).dot(M*sp.Matrix([1,0,0])))
            sz=sp.sqrt((M*sp.Matrix([0,0,1])).dot(M*sp.Matrix([0,0,1])))
            self.assertEqual((2/sx,2/sz),(1,4))
            s,p,q,w,d=sp.symbols('s p q w d',positive=True)
            self.assertEqual(sp.cancel(w*d/s**3*(p*s*q)**3-w*d*p**3*q**3),0)
            result['checks']['geometry']={'q_x':1,'q_z':4,'number_jacobian_residual':0,
                                          'actual_SI_scale_selected':False,'geometry_native_called':False}

        def test_07_read_scatter_exact_counterexamples(self):
            A=(F(1),F(1,4));L=(F(1,2),F(1,2));E=(F(1),F(4));B=(F(2,3),F(1,3))
            self.assertEqual(sum(A),F(5,4))
            self.assertEqual(sum(e*l for e,l in zip(E,L)),F(5,2))
            self.assertEqual(sum(B),1)
            self.assertEqual(sum(e*b for e,b in zip(E,B)),2)
            # 연구상의 충분조건만 확인한다. 생산 보간법을 추가하지 않는다.
            value=1/mp.expm1(mp.mpf(2)*mp.log(2))
            self.close(value,F(1,3))
            result['checks']['scatter_algebra']={'Jacobian_sum':'5/4','log_weight_energy':'5/2',
                                                 'manufactured_energy_fractions':['2/3','1/3'],
                                                 'new_interpolation_selected':False}

        def test_08_actual_com_conservation_does_not_restore_null(self):
            gamma=pair.net_action(1.,rows[1]['value'])
            plan=COMSourceDepositionPlan(np.array([1.,2.]),E0*np.array([1.,4.]),E0*np.array([2.,1.]),
                np.array([[2/3,1.],[1/3,0.]]),np.array([1.]),np.array([[0.,0.,1.]]),
                'manufactured_measure_only','manufactured_map_only')
            C=plan.apply(np.array([gamma,gamma]),1.)[:,0]
            number=float(plan.mode_measure_m3@C)
            energy=float((plan.cell_energy_J/E0*plan.mode_measure_m3)@C)
            self.close(number,2*gamma)
            self.close(energy,3*gamma)
            self.assertGreater(number,0)
            result['checks']['com']={'occupation_rate':C.tolist(),'number_per_H_s':number,
                                     'energy_in_E0_per_H_s':energy,'actual_core_called':True,
                                     'physical_map_selected':False}

    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    with (OUT/'unittest.log').open('w',encoding='utf-8') as stream:
        outcome=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    result['tests']={'run':outcome.testsRun,'failures':len(outcome.failures),'errors':len(outcome.errors),
                      'skipped':len(outcome.skipped)}
    result['post_status']={'rec':git(REC,'status','--porcelain'),'bass':git(BASS,'status','--porcelain')}
    result['unchanged_original_blobs']=all(blob((BASS if key.startswith('bass:') else REC)/key.split(':',1)[1])==sha for key,sha in PINS.items())
    ok=outcome.wasSuccessful() and outcome.testsRun==8 and not outcome.skipped
    ok=ok and result['unchanged_original_blobs'] and not any(result['post_status'].values())
    result['classification']='PASS_BOUNDED_ORIGINAL_MODEB_RUNTIME_DIAGNOSTIC' if ok else 'FAIL_BOUNDED_ORIGINAL_MODEB_RUNTIME_DIAGNOSTIC'
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(7,4.4))
        display_floor=1e-18
        zero_points=[]
        for q in (1.,2.):
            obs=[r for r in result['checks'].get('order8',[]) if r['q']==q]
            ax.semilogy([r['n'] for r in obs],[max(abs(r['planck_approximation_error']),display_floor) for r in obs],marker='o',label=f'q={q:g}')
            for r in obs:
                if r['planck_approximation_error']==0.:
                    zero_points.append({'n':r['n'],'q':q,'observed_error':0.})
                    ax.annotate('0 (shown at display floor)',(r['n'],display_floor),
                                xytext=(-8,12),textcoords='offset points',ha='right',fontsize=9)
        ax.set_xlabel(r'$n_q$')
        ax.set_ylabel(r'$|f_{\mathrm{interp}}-f_{\mathrm{exact}}|$')
        ax.set_title(r'$K=8$; display floor $10^{-18}$')
        ax.legend();fig.tight_layout();fig.savefig(OUT/'native_order8_error.png',dpi=150);plt.close(fig)
        result['plot_generated']=True
        result['plot_display']={'floor':display_floor,'zero_points':zero_points,
                                'numerical_results_modified':False}
    except Exception as exc:
        result['plot_generated']=False;result['plot_error']=repr(exc)
    result['exit_code']=0 if ok else 1
except Exception:
    result['classification']='EXECUTION_SETUP_OR_RUN_FAILED'
    result['exception']=traceback.format_exc()
    result['exit_code']=2
finally:
    save()
    print('RESULT_BEGIN')
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print('RESULT_END')
    print((OUT/'unittest.log').read_text(encoding='utf-8') if (OUT/'unittest.log').exists() else 'NO_TEST_LOG')
sys.exit(result['exit_code'])

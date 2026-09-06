"""REC 원본 함수와 독립 대수만 실행한다. BASS 원본 실행을 대체하지 않는다."""
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

p=argparse.ArgumentParser()
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[3]
r={'classification':'NOT_COMPLETED','checks':{},'original_bass_radial_calls':0,
   'original_modeb_calls':0,'full_original_diagnostic_pass':False,
   'physical_source_authenticated':False,'provider_admitted':False,
   'claim':'NO_PASS_REC_PHYSICAL_SPLIT','plots_generated':0,'independent_review':False}
pins={
 'src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py':'26ddc41e24fadf0bdd19f1924e1a429d602d9c19',
 'src/full_bianchi_hyrec/trajectory/com_source_deposition.py':'a3662cf399f14b7148d880266825be12baf934a0'}
def git(*args):
 return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def save():
 (out/'RESULT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 files=sorted(x for x in out.iterdir() if x.is_file() and x.name!='SHA256SUMS')
 (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+x.name+'\n' for x in files),encoding='utf-8')
try:
 r.update(source_commit=git('rev-parse','HEAD'),source_tree=git('rev-parse','HEAD^{tree}'),
          source_parent=git('rev-parse','HEAD^'),workflow_sha=os.getenv('GITHUB_WORKFLOW_SHA'),
          trigger=os.getenv('GITHUB_EVENT_NAME'),initial_status=git('status','--porcelain'))
 r['source_blobs']={path:blob(root/path) for path in pins}
 if r['source_blobs']!=pins or r['initial_status']:
  raise RuntimeError('고정 REC 원본 또는 격리 checkout 불일치')
 import numpy as np
 import scipy
 import sympy as s
 import mpmath as mp
 mp.mp.dps=80
 sys.path.insert(0,str(root/'src'))
 from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import PhysicalTwoPhotonRamanBin as Pair
 from full_bianchi_hyrec.trajectory.com_source_deposition import COMSourceDepositionPlan as Plan
 r['environment']={'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
                   'sympy':s.__version__,'mpmath':mp.__version__}
 r['module_paths']={c.__name__:sys.modules[c.__module__].__file__ for c in (Pair,Plan)}
 tol=128*np.finfo(float).eps
 E0=2.0**-60;hp=6.62607015e-34
 pair=Pair('two_photon',1.,3*E0/hp,E0/hp,2*E0/hp,1/16,1/2,1.)
 # 독립 폐형식 입력이다. 원본 Rust 보간 출력으로 표시하지 않는다.
 fi=float(1/mp.sqrt(15));gamma_ref=(1-3/mp.sqrt(15))/8
 def make_plan(Es=None):
  return Plan(np.array([1.,2.]),E0*np.array([1.,4.]),
              E0*np.array([2.,1.]) if Es is None else Es,
              np.array([[2/3,1.],[1/3,0.]]),np.array([1.]),np.array([[0.,0.,1.]]),
              'manufactured_only','manufactured_only')
 class Checks(unittest.TestCase):
  def close(self,x,y):
   self.assertTrue(math.isfinite(float(x)))
   self.assertLessEqual(abs(float(x)-float(y)),tol*max(1,abs(float(y))))
  def test_01_log_time_and_chain(self):
   f,e,k,H=F(2),F(1,4),F(3,4),F(4)
   df,de,dk,dlogH=F(1,8),F(1,2),F(-1,4),F(1,8)
   C=e*(1+f)-k*f;dC=(1+f)*de-f*dk+(e-k)*df
   G=C/(H*f);dG=dC/(H*f)-G*(df/f+dlogH)
   self.assertEqual((C,dC,G,dG),(F(-3,4),F(31,16),F(-3,32),F(133,512)))
   ff,ee,kk,hh=s.symbols('f eta kappa H',positive=True)
   dff,dee,dkk,dhh=s.symbols('df deta dkappa dH',real=True)
   expr=(ee*(1+ff)-kk*ff)/(hh*ff)
   derivative=sum(s.diff(expr,x)*dx for x,dx in [(ff,dff),(ee,dee),(kk,dkk),(hh,dhh)])
   chain=((1+ff)*dee-ff*dkk+(ee-kk)*dff)/(hh*ff)-expr*(dff/ff+dhh/hh)
   self.assertEqual(s.cancel(derivative-chain),0)
   r['checks']['log_time']={'C':str(C),'dC':str(dC),'G':str(G),'dG':str(dG),'sympy_residual':0}
  def test_02_original_paired_rate(self):
   exact=pair.net_action(1.,1/3);observed=pair.net_action(1.,fi)
   self.close(exact,0);self.close(observed,gamma_ref);self.assertGreater(observed,0)
   forward,reverse=pair.paired_rates(companion_occupation=1.,tracked_occupation=fi)
   r['checks']['paired']={'exact_planck_net':exact,'closed_form_input':fi,'net_from_closed_form_input':observed,
                         'reference':mp.nstr(gamma_ref,70),'forward':forward,'reverse':reverse,
                         'input_origin':'INDEPENDENT_CLOSED_FORM_NOT_RUST_OUTPUT','units':'H^-1 s^-1'}
  def test_03_original_paired_jvp(self):
   values=[]
   for fc,ft,dc,dt in [(1.,1/3,0.,1.),(1.,fi,1.,0.),(.5,2.,.25,-.125)]:
    actual=pair.jvp(companion_occupation=fc,tracked_occupation=ft,d_integrated_rate_s_inv=0.,
     d_upper_population=0.,d_ground_population=0.,d_companion_occupation=dc,d_tracked_occupation=dt)
    cc,tt,dcc,dtt=map(mp.mpf,(fc,ft,dc,dt))
    ref=mp.mpf(1)/16*((1+tt)*dcc+(1+cc)*dtt)-mp.mpf(1)/2*(tt*dcc+cc*dtt)
    self.close(actual,ref)
    values.append({'fc':fc,'ft':ft,'dfc':dc,'dft':dt,'actual':actual,'residual':float(mp.mpf(actual)-ref)})
   r['checks']['paired_jvp']=values
  def test_04_original_com_two_leg_ledger(self):
   g=pair.net_action(1.,fi);plan=make_plan();C=plan.apply([g,g],1.)[:,0]
   number=float(plan.mode_measure_m3@C);energy=float((plan.cell_energy_J/E0*plan.mode_measure_m3)@C)
   self.close(number,2*g);self.close(energy,3*g);self.assertGreater(number,0)
   with self.assertRaises(ValueError):
    make_plan(E0*np.array([5.,1.]))
   r['checks']['com']={'occupation_action_s_inv':C.tolist(),'number_per_H_s':number,
                     'energy_in_E0_per_H_s':energy,'atom_plus_photon_energy_in_E0_per_H_s':energy-3*g,
                     'out_of_hull_map_rejected':True,'physical_map_selected':False}
  def test_05_geometry_and_read_scatter(self):
   self.assertEqual((F(2)/2,F(2)/F(1,2)),(F(1),F(4)))
   self.assertEqual(sum([F(1),F(1,4)]),F(5,4))
   self.assertEqual(F(1,2)+4*F(1,2),F(5,2))
   ss,pp,qq,ww,dd=s.symbols('s p q w d',positive=True)
   self.assertEqual(s.cancel(ww*dd/ss**3*(pp*ss*qq)**3-ww*dd*pp**3*qq**3),0)
   r['checks']['geometry_algebra']={'same_energy_q':[1,4],'Jacobian_sum':'5/4','log_weight_energy':'5/2',
                                  'number_measure_cancellation':0,'bass_function_called':False}
  def test_06_conditional_entropy_identity(self):
   xu,xg,fc,ft,aa=s.symbols('xu xg fc ft a',positive=True)
   fw=aa*xu*(1+fc)*(1+ft);rv=aa*xg*fc*ft
   affinity=s.log(xu/xg)+s.log((1+fc)/fc)+s.log((1+ft)/ft)
   residual=s.simplify(s.expand_log(s.log(fw/rv)-affinity,force=True))
   self.assertEqual(residual,0)
   cases=[]
   for N in [(mp.mpf(1),mp.mpf(1)/15),(mp.mpf(2),mp.mpf(1)/8),(mp.mpf(1)/2,mp.mpf(1)/4)]:
    chi=[mp.log1p(1/x) for x in N]
    ct=mp.mpf(2)/3*chi[0]+mp.mpf(1)/3*chi[1];cc=chi[0]
    ftm=1/mp.expm1(ct);fcm=1/mp.expm1(cc)
    fp=mp.mpf(1)/16*(1+fcm)*(1+ftm);rp=mp.mpf(1)/2*fcm*ftm
    g=fp-rp;aff=mp.log(mp.mpf(1)/8)+ct+cc
    sigma=g*aff
    self.assertGreaterEqual(sigma,0)
    self.assertLess(abs(sigma-g*mp.log(fp/rp)),mp.mpf('1e-75'))
    cases.append({'nodes':[str(x) for x in N],'gamma':mp.nstr(g,50),'entropy_rate_over_kB_nH':mp.nstr(sigma,50)})
   r['checks']['entropy_condition']={'symbolic_affinity_residual':0,'manufactured_cases':cases,
                                    'production_reconstruction_changed':False}
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
 with (out/'unittest.log').open('w',encoding='utf-8') as h:
  tests=unittest.TextTestRunner(stream=h,verbosity=2).run(suite)
 r['tests']={'run':tests.testsRun,'failures':len(tests.failures),'errors':len(tests.errors),'skips':len(tests.skipped)}
 r['post_status']=git('status','--porcelain')
 r['unchanged_original_blobs']=all(blob(root/p)==v for p,v in pins.items())
 ok=tests.wasSuccessful() and tests.testsRun==6 and not tests.skipped and not r['post_status'] and r['unchanged_original_blobs']
 r['classification']='PARTIAL_REC_API_AND_MATH_VERIFIED_BASS_AUTH_BLOCKED' if ok else 'REC_PARTIAL_DIAGNOSTIC_FAILED'
 r['exit_code']=0 if ok else 1
except Exception:
 r['classification']='REC_PARTIAL_SETUP_FAILED';r['traceback']=traceback.format_exc();r['exit_code']=2
finally:
 save();print('RESULT_BEGIN');print(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False));print('RESULT_END')
 if (out/'unittest.log').exists():print((out/'unittest.log').read_text(encoding='utf-8'))
sys.exit(r['exit_code'])

"""Independent small finite mathematical-background oracle (no native solver)."""
from __future__ import annotations
import json,math,sys
from pathlib import Path
from interval_reference import PrescribedBackground,A_REF,A_END,H0,OMEGA_M,OMEGA_R,OMEGA_LAMBDA
import mpmath as mp
mp.mp.dps=55
D=lambda a:mp.mpf(float(a))
hr=D(H0)*mp.sqrt(D(OMEGA_M)/D(A_REF)**3+D(OMEGA_R)/D(A_REF)**4+D(OMEGA_LAMBDA))
q_cases=[(0.,False),(.005,False),(-.005,False),(.01,False),(-.01,False),(.01,True)]
windows=[(A_REF, A_REF+1.0e-10),(.051,.051+1e-7),(.11,.111),(.198,A_END),(A_REF,A_END)]
records=[]
for n in (1024,2048):
  for q,same_h in q_cases:
    bg=PrescribedBackground(q,n,same_h)
    for a1,a2 in windows:
      obs=bg.interval(a1,a2)
      L1=mp.log(D(a1)/D(A_REF));L2=mp.log(D(a2)/D(A_REF))
      slope=D(q)*hr
      def factors(L):
        a=D(A_REF)*mp.exp(L)
        hf=D(H0)*mp.sqrt(D(OMEGA_M)/a**3+D(OMEGA_R)/a**4+D(OMEGA_LAMBDA))
        s=slope*mp.exp(-3*L)
        h=hf if same_h else mp.sqrt(hf*hf+s*s)
        return 1/h,s/h
      dt=mp.quad(lambda L:factors(L)[0],[L1,L2]);db=mp.quad(lambda L:factors(L)[1],[L1,L2])
      ed=float(abs((D(obs.delta_t_s)-dt)/dt))
      eb=0. if q==0 else float(abs((D(obs.delta_b)-db)/db))
      records.append({'n':n,'q':q,'same_h':same_h,'a1':a1,'a2':a2,'dt_relative':ed,'db_relative':eb,'oracle_kind':'mpmath_55dps_exact_binary64_inputs'})
summary={'cases':len(q_cases),'mesh_levels':[1024,2048],'window_count':len(windows),'rows':len(records),'max_dt_relative':max(x['dt_relative'] for x in records),'max_db_relative':max(x['db_relative'] for x in records),'limit':1e-9,'pass_numeric_scope':all(x['dt_relative']<1e-9 and x['db_relative']<1e-9 for x in records),'interpretation':'Sampled mathematical F/sF integration only; not native bit parity, source/chemistry dynamics, or rigorous roundoff bound'}
root=Path(__file__).parent.parent
(root/'evidence/NUMERIC_RESULT.json').write_text(json.dumps(summary,indent=2))
(root/'evidence/NUMERIC_ROWS.json').write_text(json.dumps(records,indent=2))
print(json.dumps(summary,indent=2))
sys.exit(0 if summary['pass_numeric_scope'] else 2)

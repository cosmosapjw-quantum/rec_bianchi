"""Finite component checks against independent high-precision local quadrature."""
from pathlib import Path
import sys,math,csv,json,time,struct
from fractions import Fraction
import mpmath as mp
from increment_clock import Background,RateHermite,local_width
mp.mp.dps=65
ROOT=Path(__file__).resolve().parents[1]

def oracle(bg,a,b):
    A=mp.mpf(a);B=mp.mpf(b);ar=mp.mpf(bg.a_ref);h0=mp.mpf(bg.h0)
    om,orr,ol,q=map(mp.mpf,(bg.omega_m,bg.omega_r,bg.omega_lambda,bg.q))
    sr=q*h0*mp.sqrt(om/ar**3+orr/ar**4+ol)
    span=mp.log(B/A)
    def fun(v,kind):
        av=A*mp.exp(span*v)
        hf2=h0*h0*(om/av**3+orr/av**4+ol)
        sv=sr*(ar/av)**3
        H=mp.sqrt(hf2+(0 if bg.same_h else sv*sv))
        return span*(1 if kind=='t' else sv)/H
    return mp.quad(lambda v:fun(v,'t'),[0,1]),mp.quad(lambda v:fun(v,'b'),[0,1])

def matrix():
    start=time.monotonic();rows=[];configs=[]
    cases=[(0,False),(.005,False),(-.005,False),(.01,False),(-.01,False),(.01,True)]
    for q,same_h in cases:
        bg=Background(q=q,same_h=same_h)
        tables={n:RateHermite(bg,n) for n in [1024,2048]}
        span=local_width(bg.a_ref,bg.a_end);intervals=[]
        for j in range(9):
            a=bg.a_ref if j==0 else bg.a_end if j==8 else bg.a_ref*math.exp(span*j/8)
            for d in [1e-14,1e-12,1e-10,1e-8,1e-6,1e-4,.005]:
                pair=(a,a*math.exp(d)) if j<8 else (a*math.exp(-d),a)
                intervals.append(('anchor',*pair))
        for j in [1,511,1023]:
            knot=tables[1024].knots[j]
            intervals.append(('straddle',math.nextafter(knot,0.),math.nextafter(knot,math.inf)))
        intervals.append(('adjacent',.1,math.nextafter(.1,math.inf)))
        for kind,a,b in intervals:
            t_ref,b_ref=oracle(bg,a,b)
            for n,table in tables.items():
                dt,db=table.increment(a,b)
                et=float(abs(mp.mpf(dt)/t_ref-1))
                eb=0. if b_ref==0 else float(abs(mp.mpf(db)/b_ref-1))
                rows.append({'q':q,'same_h':same_h,'n':n,'kind':kind,'a1':a,'a2':b,'a1_hex':a.hex(),'a2_hex':b.hex(),'actual_dL':local_width(a,b),'dt_s':dt,'db':db,'reference_dt_s':mp.nstr(t_ref,70),'reference_db':mp.nstr(b_ref,70),'relative_dt_error':et,'relative_db_error':eb,'ideal_interpolation_relative_bound':table.ideal_relative_bound})
                assert et<1e-9 and eb<1e-9,rows[-1]
        for n,table in tables.items():
            Hstar=Fraction(14351,10000*n)
            eps=Fraction(30537,384)*Hstar**4/(1-3*Hstar)
            assert table.max_cell_width<float(Hstar)
            configs.append({'q':q,'same_h':same_h,'n':n,'node_count':len(table.knots),'max_cell_h':table.max_cell_width,'minimum_Bernstein_control_s':table.minimum_bernstein_control,'rational_h_upper':str(Hstar),'rational_ideal_error_bound':str(eps),'rational_ideal_error_bound_float':float(eps),'floating_evaluation_bound':'NOT_PROVED; measured separately'})
    results=ROOT/'results';results.mkdir(exist_ok=True)
    with (results/'interval_comparison.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    witness={}
    a,b=[struct.unpack('d',struct.pack('Q',v))[0] for v in [4587023449039406616,4587023449040092879]]
    t_ref,b_ref=oracle(Background(),a,b)
    for n in [1024,2048]:
        dt,db=RateHermite(Background(),n).increment(a,b)
        witness[str(n)]={'dt_s':dt,'relative_error':float(abs(mp.mpf(dt)/t_ref-1))}
    witness.update({'a1':a,'a2':b,'high_precision_dt_s':mp.nstr(t_ref,70),'inherited_native_direct_subtraction_s':844944.204474639,'inherited_native_relative_discrepancy':2.081667562769951e-7,'inherited_stable_primitive_table_s':844944.3803639701,'prior_stable_diagnostic_already_passed':True,'control_note':'Native values inherited from directly read review, not rerun; new method has its own mathematical representation.'})
    summary={'cases':6,'levels':[1024,2048],'intervals_per_case':67,'rows':len(rows),'observed_max_relative_dt_error':max(r['relative_dt_error'] for r in rows),'observed_max_relative_db_error':max(r['relative_db_error'] for r in rows),'component_limit_relative':1e-9,'maxima_by_level':{str(n):{'dt':max(r['relative_dt_error'] for r in rows if r['n']==n),'db':max(r['relative_db_error'] for r in rows if r['n']==n)} for n in [1024,2048]},'wall_s':time.monotonic()-start,'mpmath_version':mp.__version__,'mpmath_dps':65,'oracle_kind':'independent high-precision local quadrature; not a directed interval enclosure','production_solver_runs':0,'full_history_claim':'NOT_ISSUED','first_old_failure_reproduced_as_input':witness,'node_preparation':configs}
    (results/'NUMERICAL_SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':matrix()

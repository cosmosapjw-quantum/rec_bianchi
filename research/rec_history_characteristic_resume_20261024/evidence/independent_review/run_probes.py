"""Six frozen independent review rows. Execute only after explicit root GO.

Run via code/run_bounded.py --cpu 6 --wall 15 review001 python
evidence/independent_review/run_probes.py. No numerical calls at import setup
beyond dependency initialization. Uses direct independent analytic references.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
    os.environ[key]='1'
import json, sys, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'code'))
import characteristic_adapter as A
import mpmath as mp
mp.mp.dps=80
M=mp.mpf

def check(actual,expected,relative=False):
    err=abs(M(float(actual))-expected)
    scale=max(abs(expected),M('1e-300')) if relative else max(M(1),abs(expected),abs(M(float(actual))))
    limit=M('8e-12' if relative else '5e-9')*scale+(M(float.fromhex('0x0.0000000000001p-1022')) if relative else 0)
    row={'actual':float(actual),'expected':mp.nstr(expected,82),'absolute_error':mp.nstr(err,82),'limit':mp.nstr(limit,82)}
    assert err<=limit, row
    return row

def rejection(fn,expected):
    try:fn()
    except ValueError as exc:
        assert str(exc)==expected,(str(exc),expected)
        return {'expected':expected,'observed':str(exc)}
    raise AssertionError('EXPECTED_REJECTION '+expected)

def probe(k):
    if k==1:
        r=A.crossing([1,0,0],[0,0,0],1)
        return {'adapter_calls':2,'guard':rejection(lambda:A.crossing_jvp(r,dlam=-1e308,deta_t=1e308),'NONFINITE_INPUT')}
    if k==2:
        r=A.crossing([1,0,0],[-.5,.2,.3],2)
        j=A.crossing_jvp(r,dn=[0,1e-3,0])
        expected=M(1e-3)*mp.exp((1+M(.2))*4-2)
        return {'adapter_calls':2,'checks':[check(j['ddelta'],M(0)),check(j['dns'][0],M(0)),check(j['dns'][1],expected),check(j['dns'][2],M(0))]}
    if k==3:
        r=A.crossing([0,-1,0],[.25,-.5,.25],.4)
        j=A.crossing_jvp(r,db=[-.1,.2,-.1])
        expected=-(M(.4)/M(.5))*M(.2)/M(.5)
        return {'adapter_calls':2,'checks':[check(j['ddelta'],expected),check(j['dqt'],M(.2))]+[check(x,M(0)) for x in j['dns']]}
    if k==4:
        xt=2.;lam=.3;delta=.3+2e-13;dlx=.04;dl=.07;dd=-.02
        r=A.reference(xt,lam,delta,dlx,dl,dd)
        xs=M(xt)*mp.exp(M(lam)-M(delta));ws=mp.exp(-xs);wt=mp.exp(-M(xt))
        offset=ws-wt;jvp=M(xt)*wt*M(dlx)-xs*ws*(M(dlx)+M(dl)-M(dd))
        return {'adapter_calls':1,'checks':[check(r['offset'],offset,True),check(r['doffset'],jvp,True)]}
    if k==5:
        guard=rejection(lambda:A.strict_interpolation(0.,.125,[.2,.3,.4],3,-.001),'HISTORY_RETAINED_DOMAIN')
        st=A.strict_interpolation(0.,.125,[.2,.3,.4],3,.125,0.)
        assert st['k']==1 and st['at_knot'] and not st['thermal'] and st['value']==.3
        return {'adapter_calls':2,'guard':guard,'fixed_cell':st}
    if k==6:
        return {'adapter_calls':1,'guard':rejection(lambda:A.error_envelope(e_H=None,K_eta=.03,K_n=.02,eps_F=1e-8,e_arithmetic=1e-13,a_min=.8,a_max=1.2,qt=1,tau=.2,H_t=1e-13),'MISSING_ERROR_INPUT')}

def main():
    out=Path(__file__).resolve().parent/'probe_results'
    out.mkdir(exist_ok=False)
    rows=[]
    with (out/'raw_rows.jsonl').open('x') as stream:
        for k in range(1,7):
            try:row={'id':f'P{k}','status':'PASS','details':probe(k)}
            except Exception as exc:row={'id':f'P{k}','status':'FAIL','exception':str(exc),'traceback':traceback.format_exc()}
            rows.append(row);stream.write(json.dumps(row,allow_nan=False)+'\n');stream.flush()
            print(row['id'],row['status'],flush=True)
            if row['status']=='FAIL':break
    passed=len(rows)==6 and all(r['status']=='PASS' for r in rows)
    summary={'status':'PASS_SCOPED' if passed else 'FAIL','rows_saved':len(rows),'planned_rows':6,'mp_dps':80,'adapter_calls_successful_rows':sum(r.get('details',{}).get('adapter_calls',0) for r in rows),'old_replays':0,'IVP':0,'native_runtime':0}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    return 0 if passed else 1
if __name__=='__main__':sys.exit(main())

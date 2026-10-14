#!/usr/bin/env python3
"""Read-only reproduction of the bounded native-step clock diagnostic.

Requires mpmath and separately available ORIGINAL native history CSVs. Does not
run any solver or change source/config/STATE/checkpoints. All outputs are new files
in a previously absent directory. SHA-256 binds the three exact observed inputs.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,time
from pathlib import Path
import mpmath as mp

CASES={
 "ZERO":("flrw","ZERO_composed_001",0.0,312238,"4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f"),
 "SHEAR_PLUS":("paired","SHEAR_PLUS",0.01,200001,"1f29ed5dd6a7cc0588eceb9cc8748a3f3ab78e94c482f3758fd585f8910c1587"),
 "SHEAR_MINUS":("paired","SHEAR_MINUS",-0.01,200001,"1bf53b7b8e2477e3288f42591efd682ea77b96a7b1628904909ea57860ab36a6")
}

def sample_indices(end: int) -> set[int]:
    fixed={1,2,3,4,5,10,20,100,1000,6000,30000,60000,100000,150000,190000,199999,200000,220000,250000,300000,end}
    fixed|={max(1,round(end*k/20)) for k in range(1,20)}
    return {i for i in fixed if 1<=i<=end}

def read_selected_case(repo:Path, name:str) -> tuple[list[tuple],dict]:
    folder,run,q,n_expected,digest_expected=CASES[name]
    path=repo/'research/axbi_goal_20261014/runs'/folder/'32d11e733155'/run/'history.csv'
    st_before=path.stat();h=hashlib.sha256();pairs=[];prev=None
    required=sample_indices(n_expected-1)
    with path.open('rb') as f:
        first=f.readline();h.update(first);columns=next(csv.reader([first.decode().strip()]))
        a_col=columns.index('a');t_col=columns.index('time_s');q_col=columns.index('q_ref');id_col=columns.index('case_id')
        count=0
        for count,line in enumerate(f, start=1):
            h.update(line);r=next(csv.reader([line.decode().strip()]))
            a=float(r[a_col]);t=float(r[t_col]);qq=float(r[q_col]);assert r[id_col]==name and qq==q
            if prev is not None and a<=prev[0]:raise ValueError('non-increasing saved a')
            if prev is not None and t<=prev[1]:raise ValueError('non-increasing saved clock')
            if count-1 in required:
                assert prev is not None
                pairs.append((name,count-1,prev[0],a,prev[1],t,q))
            prev=(a,t)
    st_after=path.stat()
    if (st_before.st_size,st_before.st_mtime_ns)!=(st_after.st_size,st_after.st_mtime_ns):raise ValueError('input changed mid-read')
    if count!=n_expected or h.hexdigest()!=digest_expected:raise ValueError('wrong frozen history identity')
    return pairs,{'name':name,'sha256':h.hexdigest(),'rows':count,'bytes':st_before.st_size,'selected':len(pairs)}

def local_integral(a1:float,a2:float,q:float):
    # Source expressions evaluated once as binary64 then promoted exactly to mpf.
    ar=1./21.;h0=67.4*1e5/3.0856775814913673e24;om=.315;orr=9.2e-5;ol=1.-om-orr
    hr=h0*math.sqrt(om/ar**3+orr/ar**4+ol)
    mpf=lambda x:mp.mpf(float(x))
    A=mpf(a1);B=mpf(a2);H0,Om,Or,Ol,Ar,Hr=map(mpf,(h0,om,orr,ol,ar,hr))
    s=mpf(q)*Hr;dL=mp.log(B/A)
    def F(x):
        a=A*mp.exp(x)
        return 1/mp.sqrt(H0**2*(Om/a**3+Or/a**4+Ol)+s*s*(Ar/a)**6)
    return mp.quad(F,[0,dL]),dL

def run(repo:Path,out:Path):
    if out.exists():raise FileExistsError('never overwrite research output')
    if not repo.is_dir():raise ValueError('repository root not found')
    start=time.monotonic();inputs=[];pairs=[]
    for name in CASES:
        p,identity=read_selected_case(repo,name);pairs.extend(p);inputs.append(identity)
    mp.mp.dps=60;table=[]
    for name,i,a1,a2,t1,t2,q in pairs:
        ref,dL=local_integral(a1,a2,q)
        obs=(mp.mpf(float(t2-t1))-ref)/ref
        native_dL=math.log(a2/(1./21.))-math.log(a1/(1./21.))
        stable_dL=math.log1p((a2-a1)/a1)
        pred=native_dL/stable_dL-1.
        table.append({'case':name,'index':i,'a1':a1,'a2':a2,'saved_dt_s':t2-t1,
                      'reference_dt_s':mp.nstr(ref,36),'reference_dL':mp.nstr(dL,36),
                      'observed_relative_error':float(obs),'native_log_relative_predictor':pred,
                      'observed_minus_predictor':float(obs)-pred})
    gate=1e-8;fails=[x for x in table if abs(x['observed_relative_error'])>gate]
    worst=max(table,key=lambda x:abs(x['observed_relative_error']))
    summary={'scope':'finite source-bound saved-step diagnostic','inputs':inputs,
             'selected':len(table),'exceeds_1e-8':len(fails),'worst':worst,
             'max_abs_predictor_residual_on_exceedances':max(abs(x['observed_minus_predictor']) for x in fails),
             'runtime_wall_seconds':time.monotonic()-start,'mpmath_dps':60,
             'scientific_admission':'NOT_ISSUED','new_solver_runs':0}
    out.mkdir(parents=True)
    with (out/'SAMPLED_STEPS_REPRODUCED.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
    (out/'SAMPLED_STEPS_REPRODUCED.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();run(a.repo_root,a.out)

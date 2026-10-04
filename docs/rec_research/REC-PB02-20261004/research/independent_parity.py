#!/usr/bin/env python3
"""E2: unmodified author C vs native Rust; Decimal event-algebra oracle."""
import argparse, csv, io, itertools, json, subprocess
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 70
D = lambda x: Decimal(str(x))

def rows(exe, args, inputs, separator):
    result = subprocess.run([str(exe), *args], input='\n'.join(separator.join(map(str,r)) for r in inputs)+'\n', text=True, capture_output=True, check=True)
    return list(csv.DictReader(io.StringIO(result.stdout)))

def main():
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--upstream',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    plan=json.loads(Path(__file__).with_name('PARITY_EXPERIMENT_PLAN.json').read_text())
    g=plan['source_grid']; grid=list(itertools.product(g['T_K'],g['nH_cm3'],g['H_s'],g['xp']))
    native=rows(a.native,['source'],[(t,n*1e6,h,x,0) for t,n,h,x in grid],',')
    upstream=rows(a.upstream,[],grid,' ')
    assert len(native)==len(upstream)==plan['source_points']
    records=[];failures=[]; maximum={}
    def check(name,error,limit,point):
        maximum[name]=max(maximum.get(name,0.0),error)
        if error>limit:failures.append({'check':name,'point':point,'error':error,'threshold':limit})
    for i,(inp,n,c) in enumerate(zip(grid,native,upstream)):
        record={'point':i,'T_K':inp[0],'nH_cm3':inp[1],'H_s':inp[2],'xp':inp[3]}
        for nk,ck,factor in [('alpha_b_m3_s','alpha_cm3_s',1e6),('beta_p_s','beta_p_s',1),('r_alpha_s','r_alpha_s',1),('c_factor','c',1)]:
            nv=float(n[nk])*factor; cv=float(c[ck]); err=abs(nv-cv)/max(abs(cv),1e-300)
            check(nk,err,2e-12,i);record[nk+'_relative_error']=err
        t,nh,h,x=inp; cf=float(c['c']); alpha=float(c['alpha_cm3_s']);beta=float(c['beta_p_s']);b=float(n['b_lya'])
        scale=cf*(nh*alpha*x*x+beta*(1-x)*b)
        err=abs(float(n['peebles_dt'])-float(c['dxp_dt_s']))/max(scale,1e-300)
        check('source_rhs_flux_scaled',err,2e-12,i);record['rhs_flux_scaled_error']=err
        records.append(record)
    s=plan['shell_grid']; shell=list(itertools.product(s['betaP_s'],s['B'],s['state_xp_x2']))
    sn=rows(a.native,['frozen'],[(s['nH_m3'],s['alphaB_m3_s'],beta,s['Lambda_s'],s['Ralpha_s'],b,*state) for beta,b,state in shell],',')
    assert len(sn)==plan['shell_points']
    shell_records=[]
    for i,((bp,b,(xp,x2)),n) in enumerate(zip(shell,sn)):
        beta,B,x,y=D(bp),D(b),D(xp),D(x2); x1=1-x-y
        nh,alpha,lam,r=map(D,[s['nH_m3'],s['alphaB_m3_s'],s['Lambda_s'],s['Ralpha_s']])
        bs=beta/4; decay=(lam+3*r)/4; C=decay/(bs+decay)
        events=[nh*alpha*x*x,bs*y,decay*y,4*decay*x1*B]
        # Independent four-event stoichiometric columns in (xp,x2,x1).
        stoich=[(-1,1,0),(1,-1,0),(0,-1,1),(0,1,-1)]
        expected=[sum(D(v[j])*e for v,e in zip(stoich,events)) for j in range(3)]
        scale=max(sum(abs(e) for e in events),D('1e-290'))
        fields=['dxp_dt','dx2_dt','dx1_dt'];rec={'point':i,'betaP_s':bp,'B':b,'xp':xp,'x2':x2}
        for key,value in zip(fields,expected):
            err=float(abs(D(n[key])-value)/scale);check('decimal_'+key,err,2e-12,i);rec[key+'_scaled_error']=err
        cons=float(abs(sum(D(n[k]) for k in fields))/scale);check('decimal_conservation',cons,2e-12,i)
        reduced=-C*(events[0]-beta*(1-x)*B)
        defect=expected[0]-reduced
        # Include reduced forward/reverse scale when subtracting the retained RHS.
        ds=scale+abs(C*events[0])+abs(C*beta*(1-x)*B)
        for key,value in [('peebles_dt',reduced),('defect_direct',defect),('defect_reconstructed',defect)]:
            err=float(abs(D(n[key])-value)/ds);check('decimal_'+key,err,2e-12,i);rec[key+'_scaled_error']=err
        shell_records.append(rec)
    a.out.mkdir(parents=True,exist_ok=True)
    for name,data in [('upstream_native_parity.csv',records),('decimal_shell_parity.csv',shell_records)]:
        with (a.out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    result={'id':'E2-INDEPENDENT-PARITY','status':'PASS' if not failures else 'FAIL','source_points':len(grid),'decimal_shell_points':len(shell),'maximum_errors':maximum,'failures':failures,'limitations':plan['interpretation'],'native_executable':str(a.native),'upstream_executable':str(a.upstream),'oracle_precision_decimal_digits':70}
    (a.out/'INDEPENDENT_PARITY_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return bool(failures)

if __name__=='__main__': raise SystemExit(main())

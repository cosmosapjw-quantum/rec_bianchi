"""Three-case, source-bound parity diagnostics on original accepted neighbours.

This module never calls an evolution solver or writes an owner's STATE/DAG.
The parity values refer to the represented affine paths, not to certified true
solutions. Unknown evolution/interpolation errors remain None.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, sys, time
from decimal import Decimal, localcontext
from pathlib import Path
from parent_clock import NativeSeries, decimal_at

CASES=('ZERO','SHEAR_PLUS','SHEAR_MINUS')
FIELDS=('x_HII','x_HeII','x_HeIII','temperature_K','xe','ne_proper_cm3',
        'J0_photon_u_eV_per_H','J2_photon_u_eV_per_H')

def parity(x0:float,xp:float,xm:float)->tuple[float,float]:
    """Even contrast subtracts the baseline; odd contrast has no baseline."""
    if any(not math.isfinite(x) for x in (x0,xp,xm)):
        raise ValueError('nonfinite parity operand')
    e=.5*((xp-x0)+(xm-x0));o=.5*(xp-xm)
    if not math.isfinite(e+o):raise ValueError('parity overflow')
    return e,o

def parity_error(e0:float|None,ep:float|None,em:float|None)->dict:
    """Deterministic conditional propagation of supplied effective error bounds.

    A missing baseline bound affects only the even contrast. The caller owns
    trajectory, interpolation, inverse-clock and arithmetic error validity.
    """
    for e in (e0,ep,em):
        if e is not None and (not math.isfinite(e) or e<0):raise ValueError('error domain')
    odd=None if ep is None or em is None else .5*(ep+em)
    return {'even':None if e0 is None or odd is None else e0+odd,'odd':odd}

def density_parity(nE:float,nO:float,xE:float,xO:float)->tuple[float,float]:
    if any(not math.isfinite(v) for v in (nE,nO,xE,xO)):raise ValueError('nonfinite density')
    return nE*xE+nO*xO,nE*xO+nO*xE

def validate_configs(configs:dict)->float:
    if set(configs)!=set(CASES):raise ValueError('three explicit cases required')
    def value(v):
        if v in ('true','false'):return v=='true'
        try:return float(v)
        except (TypeError,ValueError):return v
    parsed={n:{k:value(v) for k,v in c.items()} for n,c in configs.items()}
    q=parsed['SHEAR_PLUS'].get('q_ref')
    if not isinstance(q,float) or not math.isfinite(q) or q<=0:raise ValueError('positive amplitude')
    if parsed['ZERO'].get('q_ref')!=0 or parsed['SHEAR_MINUS'].get('q_ref')!=-q:
        raise ValueError('signed amplitude mismatch')
    common={k:v for k,v in parsed['ZERO'].items() if k!='q_ref'}
    for n in CASES:
        if {k:v for k,v in parsed[n].items() if k!='q_ref'}!=common:
            raise ValueError('non-shear configuration differs')
    return q

def compare_query(cases:dict,L:float,t_common:float,field:str)->dict:
    atL={n:s.at('L',field,L) for n,s in cases.items()}
    att={n:s.at('time_s',field,t_common) for n,s in cases.items()}
    clocks={n:s.at('L','time_s',L).value for n,s in cases.items()}
    eL,oL=parity(*(atL[n].value for n in CASES))
    et,ot=parity(*(att[n].value for n in CASES))
    same_clock=clocks['SHEAR_PLUS']==clocks['SHEAR_MINUS']
    clock=atL['ZERO'].value-att['ZERO'].value
    # Same-clock identity also requires the common query to represent that event.
    tol=64*sys.float_info.epsilon*max(abs(t_common),abs(clocks['SHEAR_PLUS']),1.)
    applicable=same_clock and abs(t_common-clocks['SHEAR_PLUS'])<=tol
    return {'even_L':eL,'odd_L':oL,'even_t':et,'odd_t':ot,
            'zero_clock_transport':clock,
            'even_clock_residual':et-eL-clock if applicable else None,
            'odd_clock_residual':ot-oL if applicable else None,
            'signed_clock_equal_at_L':same_clock,'signed_clock_identity_applicable':applicable,
            'signed_delta_time_s':clocks['SHEAR_PLUS']-clocks['SHEAR_MINUS'],
            'reference_time_at_L':clocks['ZERO'],'plus_time_at_L':clocks['SHEAR_PLUS'],
            'minus_time_at_L':clocks['SHEAR_MINUS'],'common_time_s':t_common,
            'values_L':{n:v.value for n,v in atL.items()},
            'values_t':{n:v.value for n,v in att.items()},
            'brackets_L':{n:[v.left_id,v.right_id,v.weight] for n,v in atL.items()},
            'brackets_t':{n:[v.left_id,v.right_id,v.weight] for n,v in att.items()}}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def load_case(root:Path,name:str,manifest:dict)->NativeSeries:
    p=root/'inputs'/name
    for f,digest in manifest['cases'][name]['inputs'].items():
        if sha(p/f)!=digest:raise ValueError('immutable input mismatch: '+name+'/'+f)
    rows=list(csv.DictReader((p/'native_rows.csv').open()))
    ids=json.loads((p/'native_row_indices.json').read_text())
    if len(ids)!=len(rows) or len(rows)!=manifest['cases'][name]['selected_rows']:
        raise ValueError('selected-row count')
    expected_q=manifest['cases'][name]['q_ref']
    if any(r['case_id']!=name or float(r['q_ref'])!=expected_q for r in rows):
        raise ValueError('selected-case identity')
    names=tuple(f for f in FIELDS if f!='xe')+('nH_proper_cm3',)
    f={n:[float(r[n]) for r in rows] for n in names}
    if any(n<=0 for n in f['nH_proper_cm3']):raise ValueError('hydrogen density domain')
    f['xe']=[ne/nh for ne,nh in zip(f['ne_proper_cm3'],f['nH_proper_cm3'])]
    return NativeSeries(ids,[math.log(float(r['a'])) for r in rows],
                        [float(r['time_s']) for r in rows],f)

def verify_input_manifest(root:Path)->None:
    binding=json.loads((root/'INPUT_MANIFEST.json').read_text())
    for name,obj in binding['files'].items():
        p=root/name
        if p.stat().st_size!=obj['bytes'] or sha(p)!=obj['sha256']:
            raise ValueError('frozen intake bytes: '+name)

def analyze(root:Path,output:Path)->dict:
    start=time.monotonic();verify_input_manifest(root)
    if output.exists():raise FileExistsError('output must be new')
    output.mkdir(parents=True)
    manifest=json.loads((root/'SOURCE_INTAKE.json').read_text())
    configs={n:dict(s.split('=',1) for s in (root/'inputs'/n/'config.cfg').read_text().splitlines() if '=' in s) for n in CASES}
    q=validate_configs(configs)
    ids={manifest['cases'][n]['inputs']['source_identity.txt'] for n in CASES}
    if len(ids)!=1:raise ValueError('source identity differs')
    cases={n:load_case(root,n,manifest) for n in CASES}
    queries=json.loads((root/'inputs/QUERIES.json').read_text())
    criterion=4096*sys.float_info.epsilon
    rows=[];endpoint={};maxerr=0.;maxclock=0.;clock_applicable=0
    with localcontext() as ctx:
        ctx.prec=80
        for query in queries:
            L=query['L'];tc=query['t_common'];dL=Decimal.from_float(L);dt=Decimal.from_float(tc)
            for field in FIELDS:
                out=compare_query(cases,L,tc,field)
                d_atL={n:decimal_at(s,'L',field,dL) for n,s in cases.items()}
                d_att={n:decimal_at(s,'time_s',field,dt) for n,s in cases.items()}
                deL=(d_atL['SHEAR_PLUS']+d_atL['SHEAR_MINUS'])/2-d_atL['ZERO']
                doL=(d_atL['SHEAR_PLUS']-d_atL['SHEAR_MINUS'])/2
                det=(d_att['SHEAR_PLUS']+d_att['SHEAR_MINUS'])/2-d_att['ZERO']
                dot=(d_att['SHEAR_PLUS']-d_att['SHEAR_MINUS'])/2
                oracle={'even_L':deL,'odd_L':doL,'even_t':det,'odd_t':dot}
                scale=max(sum(abs(float(v)) for v in (*d_atL.values(),*d_att.values())),1e-100)
                err=max(abs(out[k]-float(v)) for k,v in oracle.items())/scale
                if err>criterion:raise ArithmeticError('decimal parity mismatch')
                maxerr=max(maxerr,err)
                if out['signed_clock_identity_applicable']:
                    clock_applicable+=1
                    cres=max(abs(out['odd_clock_residual']),abs(out['even_clock_residual']))/scale
                    maxclock=max(maxclock,cres)
                    if cres>criterion:raise ArithmeticError('same-clock parity identity')
                row={'kind':query['kind'],'frozen_grid_index':query['j'],'ln_a':L,'zbar':math.exp(-L)-1,
                     'field':field,**out,'odd_L_decimal80':str(doL),'even_L_decimal80':str(deL),
                     'odd_t_decimal80':str(dot),'even_t_decimal80':str(det),'arithmetic_scaled_error':err,
                     'history_error':None,'interpolation_error':None,'even_error':None,'odd_error':None,
                     'result_class':'PARTIAL_THREE_CASE_DIAGNOSTIC_UNRESOLVED'}
                rows.append(row)
                if query['j'] is None:endpoint[field]=row
    with (output/'parity_comparison.csv').open('x',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    with (output/'parity_endpoint.csv').open('x',newline='') as f:
        keys=('field','zbar','common_time_s','even_L','odd_L','zero_clock_transport','even_t','odd_t','history_error','interpolation_error')
        wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows({k:v[k] for k in keys} for v in endpoint.values())
    sample={field:{key:max(abs(r[key]) for r in rows if r['field']==field and r['kind']=='FROZEN_GRID') for key in ('even_L','odd_L','even_t','odd_t')} for field in FIELDS}
    result={'run_id':'REC_SIGNED_R7_20261014','stage':'R7_PARTIAL_DISCRIMINANT',
            'scope':'New terminal negative-shear input plus frozen ZERO/PLUS; no new solver',
            'source_head':manifest['head'],'amplitude':q,'cases':manifest['cases'],
            'query_count':len(queries),'rows':len(rows),'fields':list(FIELDS),
            'covered_frozen_indices':[a['j'] for a in queries if a['j'] is not None],
            'omitted_frozen_indices':manifest['omitted_grid_indices'],
            'native_signed_L_identical':manifest['native_signed_L_identical'],
            'native_signed_clock_identical':manifest['native_signed_clock_identical'],
            'clock_identity_applicable_rows':clock_applicable,
            'max_gross_scaled_arithmetic_error':maxerr,'max_gross_scaled_clock_identity_error':maxclock,
            'arithmetic_criterion':criterion,'endpoint':endpoint,'sampled_max_abs':sample,
            'physical_evolution_error':None,'physical_interpolation_error':None,
            'five_case_coefficients':None,'half_amplitude_scaling':None,
            'scientific_admission':'NOT_ISSUED','production_solver_runs':0,
            'native_subagent':'NOT_RUN','independent_agent_review':'NOT_RUN',
            'wall_s':time.monotonic()-start,'code_sha256':sha(Path(__file__)),
            'table_sha256':sha(output/'parity_comparison.csv')}
    (output/'SUMMARY.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({'rows':len(rows),'max_arithmetic':maxerr,'max_clock':maxclock,
                      'endpoint':{k:{f:v[f] for f in ('even_L','odd_L','even_t','odd_t')} for k,v in endpoint.items()}},indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();analyze(args.root,args.output)

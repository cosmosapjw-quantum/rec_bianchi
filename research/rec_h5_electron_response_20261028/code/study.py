"""Independent saved-data validation and one primary incoming-response study.

The validation matrix is assembled by original (row,column) coordinates.
This file does not load any native library, producer, or predecessor validator.
"""
import copy
from decimal import Decimal as D, localcontext
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import incoming_response as ir

ROOT = Path(__file__).resolve().parents[1]
EPS = D.from_float(2.0**-52)
ZERO = D(0)
GATE = D('1e-60')


def js(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False, default=str) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs():
    manifest = json.loads((ROOT / 'INPUT_MANIFEST.json').read_text())
    for item in manifest['files']:
        path = ROOT / item['path']
        if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError('input bytes changed: ' + item['path'])
    records = []
    for path in sorted((ROOT / 'inputs/execution/C7_attempt001').glob('PRIMARY_*.jsonl')):
        records += [json.loads(line) for line in path.read_text().splitlines()]
    controls = [json.loads(line) for line in
                (ROOT / 'inputs/execution/C8_VALIDATE_attempt001/NATIVE_CONTROLS_000.jsonl').read_text().splitlines()]
    if len(records) != 132 or [r['index'] for r in records] != list(range(132)):
        raise ValueError('132 ordered primary writers required')
    if len({(r['call_id'], r['slot']) for r in records}) != 132:
        raise ValueError('duplicate writer binding')
    if len(controls) != 9 or {(r['index'], r['control']) for r in controls} != {
            (i, name) for i in (0, 66, 131) for name in ('zero', 'signed_negative', 'doubled')}:
        raise ValueError('saved control set differs')
    return records, controls


def coordinates(record):
    """Original M coordinates; transpose is applied by swapping coordinates."""
    o = record['output']
    f = lambda x: D.from_float(float.fromhex(x))
    entries = []
    for i in range(2):
        for j in range(2):
            entries.append((i, j, f(o['A'][i][j])))
        for b in range(311):
            entries.append((i, 2+b, f(o['B'][i][b])))
            entries.append((2+b, i, f(o['C'][i][b])))
    for b in range(311):
        entries.append((2+b, 2+b, f(o['V'][0][b])))
        if b:
            entries.append((2+b, 1+b, f(o['V'][1][b])))
        if b < 310:
            entries.append((2+b, 3+b, f(o['V'][2][b])))
    return entries


def independent_residual(record, vector, rhs, transpose=False):
    rows = [[] for _ in range(313)]
    for i, j, a in coordinates(record):
        if transpose:
            i, j = j, i
        rows[i].append(a * vector[j])
    products = [sum(row, ZERO) for row in rows]
    signed = [a-b for a, b in zip(products, rhs)]
    scales = [sum(map(abs, row), ZERO)+abs(b) for row, b in zip(rows, rhs)]
    norm = [abs(r)/s if s else (ZERO if not r else D('Infinity'))
            for r, s in zip(signed, scales)]
    return signed, max(norm), norm.index(max(norm)), products


def scalar_scale(p):
    return sum((p.nH*(abs(p.s*p.x1*p.dalpha[i])+abs(p.alpha[i]*p.delta))
                +abs(p.saved_state[i]*p.beta[i]) for i in range(2)), ZERO)/p.H


def source_direction(p, direction, coefficients):
    result = [ZERO]*313
    for b in range(311):
        result[2+b] = coefficients[b]*direction[b]
    result[1] = coefficients[311]*direction[311]
    result[0] = coefficients[312]*direction[312]
    return result


def test_contract(records, controls, out):
    r = records[0]
    original = hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
    p = ir.parse_record(r)
    response = ir.response(p)
    q = ir.scalar_row(p)
    lam = list(map(D, response['lambda313']))
    signed, residual, _, _ = independent_residual(r, lam, q, True)
    checks = {'independent_adjoint_residual': residual <= GATE}
    checks['nonmutation'] = original == hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
    invalid = {}
    changes = {
        'foreign_source': lambda x: x.update(source_sha256='0'*64),
        'wrong_binding': lambda x: x.update(call_id=x['call_id']+1),
        'wrong_phase': lambda x: x['output']['actual_input'].update(phase='H_FULL'),
        'wrong_units': lambda x: x['output']['actual_input'].update(units='SI'),
        'wrong_shape': lambda x: x['output']['V'][0].pop(),
        'nonfinite': lambda x: x['output']['actual_input']['incoming_virtual'].__setitem__(0, 'inf'),
    }
    for name, change in changes.items():
        malformed = copy.deepcopy(r)
        change(malformed)
        try:
            ir.parse_record(malformed)
        except (ValueError, KeyError) as err:
            invalid[name] = {'rejected': True, 'error': str(err)}
        else:
            invalid[name] = {'rejected': False}
    checks['six_invalid_cases'] = all(v['rejected'] for v in invalid.values())
    known = tuple(D((j % 7)-3)/7 for j in range(313))
    known_tests = []
    for transpose in (False, True):
        _, _, _, rhs = independent_residual(r, known, [ZERO]*313, transpose)
        recovered, _ = ir.solve_block(p, rhs, transpose=transpose)
        error = max(abs(a-b) for a, b in zip(known, recovered))
        known_tests.append({'transpose': transpose, 'scaled_error': error, 'pass': error <= GATE})
    checks['known_solution_both_orientations'] = all(t['pass'] for t in known_tests)
    changed = list(lam)
    changed[0] += max(abs(changed[0]), D(1))/100
    _, changed_res, _, _ = independent_residual(r, changed, q, True)
    checks['changed_adjoint_rejected'] = changed_res > GATE
    # Wrong same-index band swap is tested against the true original transpose.
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
    entries = coordinates(r)
    ii, jj, vv = [], [], []
    for a, b, v in entries:
        if a>=2 and b>=2 and a!=b:
            continue
        ii.append(b); jj.append(a); vv.append(float(v))
    for b in range(311):
        if b:
            ii.append(2+b);jj.append(1+b);vv.append(float(p.V[2][b]))
        if b<310:
            ii.append(2+b);jj.append(3+b);vv.append(float(p.V[1][b]))
    bad = spsolve(coo_matrix((vv,(ii,jj)),shape=(313,313)).tocsc(), np.array(list(map(float,q))))
    _, bad_res, _, _ = independent_residual(r, list(map(D.from_float,bad)),q,True)
    checks['same_index_transpose_rejected'] = bad_res > D('1e-10')
    # Source mapping negative control uses an actual doubled incoming control.
    c = next(x for x in controls if x['index']==0 and x['control']=='doubled')
    cp = ir.parse_record(c)
    du = [a-b for a,b in zip(cp.incoming,p.incoming)]
    gc = list(map(D,response['G_coefficients313']))
    mapped = source_direction(p,du,gc)
    mapped[0],mapped[1] = mapped[1],mapped[0]
    ds = [a-b for a,b in zip(cp.saved_source,p.saved_source)]
    scale = sum(map(abs,cp.saved_source),ZERO)+sum(map(abs,p.saved_source),ZERO)+sum(map(abs,mapped),ZERO)
    mismatch = sum((abs(a-b) for a,b in zip(ds,mapped)),ZERO)/scale
    checks['swapped_lyman_source_rejected'] = mismatch > 512*EPS
    result = {'checks': checks, 'invalid_cases': invalid, 'known_solution':known_tests,
              'wrong_transpose_residual':bad_res,'changed_adjoint_residual':changed_res,
              'swapped_lyman_forcing_mismatch':mismatch,'new_native_calls':0,
              'pass':all(checks.values())}
    js(out/'RESULT.json', result)
    return result['pass']


def primary(records, out):
    output = []
    failures = []
    for r in records:
        result = ir.response(r)
        p = ir.parse_record(r)
        _, norm, worst, _ = independent_residual(r,list(map(D,result['lambda313'])),ir.scalar_row(p),True)
        result['independent_residual'] = {'maximum':str(norm),'worst_row':worst}
        result['z'] = str(p.z)
        output.append(result)
        if norm > GATE:
            failures.append({'index':r['index'],'residual':str(norm)})
    for start in range(0,len(output),20):
        path=out/f'RESPONSE_{start:03d}_{min(start+19,131):03d}.jsonl'
        path.write_text(''.join(json.dumps(x,allow_nan=False)+'\n' for x in output[start:start+20]))
    summary = {
        'count':len(output),'incoming_coefficients_per_point':313,
        'total_response_coefficients':len(output)*313,
        'max_independent_adjoint_residual':str(max(D(x['independent_residual']['maximum']) for x in output)),
        'j1_min':str(min(D(x['j1_norm']) for x in output)),
        'j1_max':str(max(D(x['j1_norm']) for x in output)),
        'negative_J_count':sum(D(v)<0 for x in output for v in x['j313']),
        'zero_J_count':sum(D(v)==0 for x in output for v in x['j313']),
        'new_native_calls':0,'failures':failures,'pass':not failures,
    }
    js(out/'RESULT.json',summary)
    return summary['pass']


def get_responses():
    paths=sorted((ROOT/'execution/C7_attempt001').glob('RESPONSE_*.jsonl'))
    results=[json.loads(line) for path in paths for line in path.read_text().splitlines()]
    if len(results)!=132 or [x['index'] for x in results]!=list(range(132)):
        raise ValueError('missing or reordered saved primary responses')
    return results


def validation(records,controls,out,override=None,model='real'):
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
    responses=get_responses() if override is None else override
    precision=[]; scipy_checks=[]; reciprocity=[]; bridges=[]
    for i in (0,66,131):
        p=ir.parse_record(records[i]); old=responses[i]
        high=ir.response(p,precision=120)
        if model=='prefix':
            with localcontext() as high_context:
                high_context.prec=120
                high_g=ir.prefix_coefficients(p,120)
                high['j313']=[str(g*D(high['lambda313'][row])) for row,g in zip(ir.SOURCE_ROWS,high_g)]
        j80=list(map(D,old['j313']));j120=list(map(D,high['j313']))
        error=max(abs(a-b) for a,b in zip(j80,j120))/max(D(1),max(map(abs,j120)))
        precision.append({'index':i,'scaled_J_difference_80_120':str(error),'pass':error<=GATE})
        entries=coordinates(records[i]);ii,jj,vv=zip(*entries)
        mat=coo_matrix((list(map(float,vv)),(ii,jj)),shape=(313,313)).tocsc()
        q=ir.scalar_row(p);q64=np.asarray(list(map(float,q)))
        la64=spsolve(mat.T.tocsc(),q64)
        coeff=list(map(D,old['G_coefficients313']))
        refs=[D.from_float(float(la64[row]))*g for row,g in zip(ir.SOURCE_ROWS,coeff)]
        comparison=max(abs(a-b) for a,b in zip(j80,refs))/max(D(1),max(map(abs,j80)))
        _,nr,_,_=independent_residual(records[i],list(map(D.from_float,la64)),q,True)
        scipy_checks.append({'index':i,'scaled_response_difference':str(comparison),
                             'normalized_backward_residual':str(nr),'pass':comparison<=D('1e-10')})
        for direction_name in ('Ly0','Ly1','alternating_virtual'):
            direction=[ZERO]*313
            if direction_name=='Ly0':direction[311]=D(1)
            elif direction_name=='Ly1':direction[312]=D(1)
            else:
                for b in range(311):direction[b]=D(1 if b%2==0 else -1)
            rhs=source_direction(p,direction,coeff)
            primal,_=ir.solve_block(p,rhs)
            _,pr,_,_=independent_residual(records[i],primal,rhs,False)
            expected=sum((a*b for a,b in zip(j80,direction)),ZERO)
            actual=sum((a*b for a,b in zip(q,primal)),ZERO)
            scale=max(D(1),sum((abs(a*b) for a,b in zip(j80,direction)),ZERO),abs(actual))
            reciprocal=abs(actual-expected)/scale
            independent=spsolve(mat,np.asarray(list(map(float,rhs))))
            independent_value=sum((a*D.from_float(float(b)) for a,b in zip(q,independent)),ZERO)
            double_error=abs(independent_value-expected)/scale
            reciprocity.append({'index':i,'direction':direction_name,'Decimal_primal_residual':str(pr),
                'scaled_Decimal_reciprocity':str(reciprocal),'scaled_SciPy_primal_difference':str(double_error),
                'pass':pr<=GATE and reciprocal<=GATE and double_error<=D('1e-10')})
    fixed_keys=['A','B','C','V','Beta','H','nH','s','x1','Alpha','DAlpha','Delta','Dtau']
    for cr in controls:
        i=cr['index'];br=records[i];rp=responses[i]
        binding=all(cr['output'][key]==br['output'][key] for key in fixed_keys)
        binding=binding and cr['call_id']==br['call_id'] and cr['slot']==br['slot'] and cr['call']==br['call']
        if not binding:raise ValueError('fixed coefficient control binding failed')
        p=ir.parse_record(br);cp=ir.parse_record(cr)
        lam=list(map(D,rp['lambda313']));j=list(map(D,rp['j313']));g=list(map(D,rp['G_coefficients313']))
        du=[a-b for a,b in zip(cp.incoming,p.incoming)]
        gdu=source_direction(p,du,g)
        ds=[a-b for a,b in zip(cp.saved_source,p.saved_source)]
        eg=[a-b for a,b in zip(ds,gdu)]
        gs=sum(map(abs,cp.saved_source),ZERO)+sum(map(abs,p.saved_source),ZERO)+sum(map(abs,gdu),ZERO)
        gnorm=sum(map(abs,eg),ZERO)/gs if gs else (ZERO if not any(eg) else D('Infinity'))
        row_scales=[abs(a)+abs(b)+abs(c) for a,b,c in zip(cp.saved_source,p.saved_source,gdu)]
        row_mismatch=[abs(e)/s if s else ZERO if e==0 else D('Infinity') for e,s in zip(eg,row_scales)]
        q=ir.scalar_row(p);d=ir.scalar_constant(p)
        rb,_,_,_=independent_residual(br,p.saved_state,p.saved_source)
        rc,_,_,_=independent_residual(cr,cp.saved_state,cp.saved_source)
        rl,_,_,_=independent_residual(br,lam,q,True)
        eb=p.saved_FH-(d+sum((a*b for a,b in zip(q,p.saved_state)),ZERO))
        ec=cp.saved_FH-(d+sum((a*b for a,b in zip(q,cp.saved_state)),ZERO))
        terms={
            'scalar_rounding':ec-eb,
            'source_reconstruction':sum((a*b for a,b in zip(lam,eg)),ZERO),
            'saved_solve_residual':sum((a*(b-c) for a,b,c in zip(lam,rc,rb)),ZERO),
            'adjoint_residual':-sum((a*(b-c) for a,b,c in zip(rl,cp.saved_state,p.saved_state)),ZERO),
        }
        observed=cp.saved_FH-p.saved_FH
        predicted=sum((a*b for a,b in zip(j,du)),ZERO)
        gap=observed-predicted
        closure=abs(gap-sum(terms.values(),ZERO))/max(D(1),sum(map(abs,terms.values()),ZERO),abs(gap))
        threshold=512*EPS*(scalar_scale(p)+scalar_scale(cp))
        bridges.append({'index':i,'control':cr['control'],'binding':binding,
            'observed_DeltaFH':str(observed),'predicted_J_du':str(predicted),'observed_minus_predicted':str(gap),
            'FH_bridge_threshold':str(threshold),'FH_bridge_pass':abs(gap)<=threshold,
            'G_L1_normalized_mismatch':str(gnorm),'G_bridge_threshold':str(512*EPS),'G_bridge_pass':gnorm<=512*EPS,
            'G_worst_row_normalized_mismatch':str(max(row_mismatch)), 'G_worst_row':row_mismatch.index(max(row_mismatch)),
            'difference_terms':{k:str(v) for k,v in terms.items()},'scaled_identity_closure':str(closure),
            'pass':gnorm<=512*EPS and abs(gap)<=threshold and closure<=GATE})
    result={'model':model,'precision':precision,'independent_SciPy_adjoint':scipy_checks,'primal_reciprocity':reciprocity,
        'saved_native_bridges':bridges,'control_direction_rank':'1 per representative point; 3 distinct points; not 313 native column tests',
        'new_native_calls':0,'pass':all(x['pass'] for group in [precision,scipy_checks,reciprocity,bridges] for x in group)}
    js(out/'RESULT.json',result)
    return result['pass']


def native_prefix_comparison(records,controls,out):
    old=get_responses()
    new=[];parity=[];diagnostics=[]
    for record in records+controls:
        p=ir.parse_record(record)
        actual=ir.reconstructed_source64(p)
        expected=record['output']['sr']+record['output']['sv']
        bad=[i for i,(a,b) in enumerate(zip(actual,expected))
             if struct.pack('>d',a)!=struct.pack('>d',float.fromhex(b))]
        parity.append({'index':p.index,'control':record.get('control','primary'),
                       'equal':313-len(bad),'total':313,'mismatched_rows':bad,'pass':not bad})
    for record, previous in zip(records,old):
        p=ir.parse_record(record);lam=list(map(D,previous['lambda313']))
        gc=ir.prefix_coefficients(p)
        jj=[g*lam[row] for row,g in zip(ir.SOURCE_ROWS,gc)]
        item=dict(previous)
        item.update(model='native-prefix-lift frozen real coefficient model',
                    j313=list(map(str,jj)),G_coefficients313=list(map(str,gc)),
                    j1_norm=str(sum(map(abs,jj),ZERO)),
                    incoming_response_Ju=str(sum((a*b for a,b in zip(jj,p.incoming)),ZERO)),
                    adjoint_reused_from='execution/C7_attempt001')
        new.append(item)
    # Diagnose the original bridge's worst rows without changing its data.
    failed=json.loads((ROOT/'execution/C8_attempt001/RESULT.json').read_text())
    for i in (0,66,131):
        row=next(x['G_worst_row'] for x in failed['saved_native_bridges'] if x['index']==i)
        b=row-2;p=ir.parse_record(records[i]);tau=p.tau[b]
        pi=(D(1)-(-tau).exp())/tau if tau>ir.TAU_SWITCH else D(1)-tau/2+tau*tau/6
        prefixes,_=ir.native_prefix_data(p)
        native_pi=D.from_float(prefixes[b][1])
        stable_pi=D.from_float(-math.expm1(-float(tau))/float(tau)) if tau else D(1)
        diagnostics.append({'index':i,'source_row':row,'virtual_bin':b,'tau':str(tau),
            'pi_real':str(pi),'pi_native_reconstruction':str(native_pi),
            'pi_expm1_diagnostic':str(stable_pi),
            'relative_native_pi_error':str((native_pi-pi)/pi),
            'relative_expm1_pi_error':str((stable_pi-pi)/pi),
            'production_source_changed':False})
    for start in range(0,len(new),20):
        # Save only changed response data; lambda and all M/q evidence are reused.
        fields=['schema','index','call_id','slot','source_sha256','model','precision','incoming_order',
                'j313','G_coefficients313','G_source_rows313','j1_norm','incoming_response_Ju','adjoint_reused_from','new_native_calls']
        rows=[{key:item[key] for key in fields} for item in new[start:start+20]]
        (out/f'PREFIX_RESPONSE_{start:03d}_{min(start+19,131):03d}.jsonl').write_text(
            ''.join(json.dumps(row)+'\n' for row in rows))
    summary={'model':'prefix','records':132,'coefficients':41316,
        'source_entry_parity_equal':sum(x['equal'] for x in parity),'source_entry_parity_total':len(parity)*313,
        'source_records_parity':sum(x['pass'] for x in parity),'source_records_total':len(parity),
        'source_parity_details':parity,'cancellation_diagnostics':diagnostics,
        'j1_min':str(min(D(x['j1_norm']) for x in new)),'j1_max':str(max(D(x['j1_norm']) for x in new)),
        'max_relative_J_change_from_real':str(max(max(abs(D(a)-D(b)) for a,b in zip(x['j313'],y['j313']))/
            max(D(1),max(abs(D(v)) for v in x['j313'])) for x,y in zip(old,new))),
        'all_132_adjoint_solutions_reused':True,'new_native_calls':0,
        'pass':all(x['pass'] for x in parity)}
    js(out/'MODEL_SUMMARY.json',summary)
    valid=validation(records,controls,out,override=new,model='prefix')
    return summary['pass'] and valid


def plots(records,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    original_responses=get_responses()
    responses=copy.deepcopy(original_responses)
    for path in sorted((ROOT/'execution/C8_NATIVE_attempt001').glob('PREFIX_RESPONSE_*.jsonl')):
        for line in path.read_text().splitlines():
            row=json.loads(line);responses[row['index']].update(row)
    vals=np.asarray([[float(x) for x in row['j313']] for row in responses])
    l1=np.abs(vals).sum(axis=1)
    virtual=np.abs(vals[:,:311]).sum(axis=1)
    z=np.array([float(row['z']) for row in responses])
    residual=np.array([float(row['independent_residual']['maximum']) for row in responses])
    order=np.argsort(z)
    fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    for values,label in [(l1,'Total'),(virtual,'Virtual bins'),(abs(vals[:,311]),'Ly alpha incoming'),(abs(vals[:,312]),'Ly beta incoming')]:
        axes[0,0].plot(z[order],values[order],label=label)
    axes[0,0].set_yscale('log');axes[0,0].set_xlabel('Saved writer redshift z')
    axes[0,0].set_ylabel('Point response norm / component magnitude');axes[0,0].legend(fontsize=8)
    for i in (0,66,131):axes[0,1].plot(np.arange(311),np.abs(vals[i,:311]),label=f'writer {i}')
    axes[0,1].set_yscale('log');axes[0,1].set_xlabel('Virtual incoming bin b');axes[0,1].set_ylabel('|J_b|');axes[0,1].legend()
    axes[1,0].plot(np.arange(132),residual)
    axes[1,0].axhline(1e-60,color='tab:red',ls='--',label='Frozen 1e-60 gate')
    axes[1,0].set_yscale('log');axes[1,0].set_xlabel('Writer index');axes[1,0].set_ylabel('Independent normalized adjoint residual');axes[1,0].legend()
    data=json.loads((ROOT/'execution/C8_NATIVE_attempt001/RESULT.json').read_text())['saved_native_bridges']
    gap=np.array([abs(float(x['observed_minus_predicted'])) for x in data]);tol=np.array([float(x['FH_bridge_threshold']) for x in data])
    axes[1,1].scatter(np.arange(9),gap,label='Saved native / model response discrepancy')
    axes[1,1].scatter(np.arange(9),tol,marker='_',s=130,label='Frozen bridge threshold')
    axes[1,1].set_yscale('log');axes[1,1].set_xticks(range(9),[f"{x['index']}:{x['control'][0]}" for x in data],rotation=45)
    axes[1,1].set_ylabel('|DeltaFH - J dot du|');axes[1,1].legend(fontsize=7)
    for ax in axes.flat:ax.grid(alpha=.2)
    fig.suptitle('REC: fixed-point incoming response, 132 saved writers\nNative-prefix coefficient model; no whole-domain physical bound',fontsize=13)
    fig.savefig(out/'incoming_response.png',dpi=160)
    fig.savefig(out/'incoming_response.pdf')
    plt.close(fig)
    original=json.loads((ROOT/'execution/C8_attempt001/RESULT.json').read_text())['saved_native_bridges']
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
    axes[0].scatter(range(9),[float(x['G_L1_normalized_mismatch']) for x in original],label='Exact-formula G: 7 of 9 fail',marker='x',s=60)
    axes[0].scatter(range(9),[float(x['G_L1_normalized_mismatch']) for x in data],label='Native-prefix G',marker='o')
    axes[0].axhline(float(512*EPS),ls='--',color='tab:red',label='Unchanged 512 eps64 gate')
    axes[0].set_yscale('log');axes[0].set_xticks(range(9),[f"{x['index']}:{x['control'][0]}" for x in data],rotation=45)
    axes[0].set_ylabel('Normalized source-forcing mismatch');axes[0].legend(fontsize=8)
    diagnostic=json.loads((ROOT/'execution/C8_NATIVE_attempt001/MODEL_SUMMARY.json').read_text())['cancellation_diagnostics']
    axes[1].scatter(range(3),[abs(float(x['relative_native_pi_error'])) for x in diagnostic],label='Original subtraction order',marker='x',s=60)
    axes[1].scatter(range(3),[abs(float(x['relative_expm1_pi_error'])) for x in diagnostic],label='expm1 diagnostic',marker='o')
    axes[1].set_yscale('log');axes[1].set_xticks(range(3),[f"writer {x['index']}, bin {x['virtual_bin']}" for x in diagnostic])
    axes[1].set_ylabel('Relative transmission-factor error');axes[1].legend(fontsize=8,loc='center right')
    for ax in axes:ax.grid(alpha=.2)
    fig.suptitle('Preserved real-model bridge failure and source-prefix comparison\nSaved source is unchanged; expm1 is diagnostic only')
    fig.savefig(out/'source_bridge_comparison.png',dpi=160)
    fig.savefig(out/'source_bridge_comparison.pdf')
    plt.close(fig)
    rows=['index,call_id,slot,z,j1_norm,virtual_j1,Ly0,Ly1,adjoint_residual']
    for r in responses:
        values=list(map(D,r['j313']))
        rows.append(','.join(map(str,[r['index'],r['call_id'],r['slot'],r['z'],r['j1_norm'],sum(map(abs,values[:311]),ZERO),values[311],values[312],r['independent_residual']['maximum']])))
    (out/'response_summary.csv').write_text('\n'.join(rows)+'\n')
    js(out/'RESULT.json',{'pass':True,'figures':['incoming_response.png','incoming_response.pdf','source_bridge_comparison.png','source_bridge_comparison.pdf'],'saved_results_only':True,'new_native_calls':0})
    return True


def main():
    stage,out=sys.argv[1],Path(sys.argv[2])
    records,controls=load_inputs()
    with localcontext() as context:
        context.prec=80
        if stage=='C6':passed=test_contract(records,controls,out)
        elif stage=='C7':passed=primary(records,out)
        elif stage=='C8':passed=validation(records,controls,out)
        elif stage=='C8_NATIVE':passed=native_prefix_comparison(records,controls,out)
        elif stage=='PLOTS':passed=plots(records,out)
        else:raise ValueError('unknown stage')
    load_inputs()  # bytes and binding unchanged after numerical work
    print(json.dumps({'stage':stage,'pass':passed,'new_native_calls':0}))
    if not passed:raise SystemExit(2)


if __name__=='__main__':main()

"""Complete unreached C/D/E/F from immutable primary outputs, no13-RHS replay.

Preparation only until separate root continuation RUN_READY. JSON conversion
changes NumPy scalar representation only; criteria and source arithmetic stay.
"""
from pathlib import Path
import sys
import json
import traceback
import hashlib
import numpy as np
from scipy.linalg import lu_factor,lu_solve

UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT/'code'))
from inputs import load
from source import build,matrices,outputs,parameters,E21,EV_J
from scalar import Dual,split
from primary import metric,roundoff_identity
from controls import run as controls

PRIMARY=UNIT/'results/primary001'
OUT=UNIT/'results/continuation001'
RHS=0
EPS=np.finfo(float).eps


def json_scalar(value):
    if isinstance(value,np.generic):
        return value.item()
    raise TypeError('Unsupported JSON value: '+type(value).__name__)


def dump(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False,default=json_scalar)+'\n')


def read_npz(name):
    with np.load(PRIMARY/name,allow_pickle=False) as f:
        return {k:f[k].copy() for k in f.files}


def raw_hashes():
    return {str(p.relative_to(UNIT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in sorted(PRIMARY.iterdir()) if p.is_file()}


def solve(M,b):
    global RHS
    count=1 if b.ndim==1 else b.shape[1]
    if RHS+count>12 or 13+RHS+count>25:
        raise RuntimeError('CONTINUATION_OR_CUMULATIVE_LARGE_RHS_CAP')
    RHS+=count
    return lu_solve(lu_factor(M,check_finite=True),b,check_finite=True)


def saved_backward(residual,gross):
    ratio=np.zeros_like(gross)
    np.divide(np.abs(residual),gross,out=ratio,where=gross!=0)
    zeros_ok=bool(np.all(residual[gross==0]==0))
    return {'max_componentwise_residual':float(np.max(ratio)),
            'zero_gross_exact':zeros_ok,'pass':zeros_ok and float(np.max(ratio))<=1024*EPS,
            'method':'Saved primary residual/gross arrays; no matrix solve or residual recomputation'}


def main():
    OUT.mkdir(parents=True,exist_ok=False)
    before=raw_hashes();dump('PRIMARY_RAW_HASHES_BEFORE.json',before)
    base=read_npz('BASE_COEFFICIENTS.npz');der=read_npz('COEFFICIENT_DERIVATIVES.npz')
    analytic=read_npz('ANALYTIC_RESPONSE.npz');complex_result=read_npz('COMPLEX_RESPONSE.npz')
    saved=read_npz('BACKWARD_RESIDUALS.npz')
    A=json.loads((PRIMARY/'LITERAL_PARITY.json').read_text())
    B=json.loads((PRIMARY/'COMPLEX_COMPARISON.json').read_text())
    C={'primal':saved_backward(saved['primal_residual'],saved['primal_gross']),
       'tangent':saved_backward(saved['tangent_residual'],saved['tangent_gross'])}
    dump('BACKWARD_RESIDUALS.json',C)
    X=analytic['X'];DX=analytic['dX'];theta=base['theta']
    doutput={k[2:]:v for k,v in analytic.items() if k.startswith('d_')}
    cs_out={k[4:]:v for k,v in complex_result.items() if k.startswith('out_')}
    ownership=json.loads((PRIMARY/'BRANCH_OWNERSHIP.json').read_text())['signature']
    ownership=tuple(tuple(x) for x in ownership)
    data=load(UNIT);u=data['incoming']
    if not np.array_equal(theta,data['theta']):
        raise ValueError('SAVED_PRIMITIVE_BASE_IDENTITY')
    identities={}
    identities['electron_M_exact_zero']={'pass':bool(np.all(der['M'][...,0]==0))}
    identities['electron_source']=roundoff_identity(der['s'][:2,0]-theta[4]*base['Alpha']*theta[1],
                                         np.abs(der['s'][:2,0])+np.abs(theta[4]*base['Alpha']*theta[1]))
    identities['electron_virtual_source_zero']={'pass':bool(np.all(der['s'][2:,0]==0))}
    identities['common_nH_H_M']=roundoff_identity(der['M'][...,4]+der['M'][...,5],np.abs(der['M'][...,4])+np.abs(der['M'][...,5]))
    common_source=der['s'][:,4]+der['s'][:,5]
    expected=np.r_[theta[4]*base['Alpha']*theta[0]*theta[1],np.zeros(311)]
    identities['common_nH_H_source']=roundoff_identity(common_source-expected,
          np.abs(der['s'][:,4])+np.abs(der['s'][:,5])+np.abs(expected))
    identities['energy_pair']=roundoff_identity(doutput['radiation_energy']+doutput['atomic_energy'],
          np.abs(doutput['radiation_energy'])+np.abs(doutput['atomic_energy']))
    identities['energy_number']=roundoff_identity(doutput['radiation_energy']-E21*EV_J*doutput['R_gamma'],
          np.abs(doutput['radiation_energy'])+np.abs(E21*EV_J*doutput['R_gamma']))
    pure={k:v[...,0]+v[...,1] for k,v in doutput.items()}
    pureX=DX[:,0]+DX[:,1]
    pure_cs={k:v[...,0]+v[...,1] for k,v in cs_out.items()}
    identities['pure_H_derivative']={k:metric(pure[k],pure_cs[k]) for k in pure}
    identities['pure_H_derivative']['pass']=all(metric(pure[k],pure_cs[k])['normalized_error']<=2e-8 for k in pure)
    seed=np.eye(6)[0]
    restricted_theta=[Dual(theta[i],seed if i<2 else np.zeros(6)) for i in range(6)]
    restricted=build(restricted_theta,data,ownership=ownership)
    _,restricted_der=matrices(restricted)
    restricted_out={k:split(v)[1][...,0] for k,v in outputs(restricted,
                      [Dual(X[i],pureX[i]*seed) for i in range(313)],u).items()}
    pure_checks={}
    for k in ['M','s','T','P']:
        direct=restricted_der[k][...,0]
        pure_checks['coefficient_'+k]=roundoff_identity(direct-der[k][...,0]-der[k][...,1],
                                   np.abs(direct)+np.abs(der[k][...,0])+np.abs(der[k][...,1]))
    for k in pure:
        pure_checks['output_'+k]=roundoff_identity(restricted_out[k]-doutput[k][...,0]-doutput[k][...,1],
                         np.abs(restricted_out[k])+np.abs(doutput[k][...,0])+np.abs(doutput[k][...,1]))
    pr=base['M']@pureX+np.einsum('ij,j->i',der['M'][...,0]+der['M'][...,1],X)-der['s'][:,0]-der['s'][:,1]
    pg=np.abs(base['M'])@np.abs(pureX)+(np.abs(der['M'][...,0])+np.abs(der['M'][...,1]))@np.abs(X)+np.abs(der['s'][:,0])+np.abs(der['s'][:,1])
    pure_checks['implicit_residual']=roundoff_identity(pr,pg)
    identities['pure_H_restricted_512eps']={'checks':pure_checks,'pass':all(x['pass'] for x in pure_checks.values()),
                                           'additional_large_RHS':0}
    np.savez(OUT/'PURE_H_RESPONSE.npz',state=pureX,**pure)
    dump('IDENTITIES.json',identities)
    fd=[];fd_saved={}
    for i,direction in enumerate([np.array([.1,-.2,.3,-.1,.2,-.3]),np.array([.2,.2,-.1,.1,-.3,.2])]):
        pred={k:np.tensordot(v,direction,axes=(-1,0)) for k,v in doutput.items()}
        accepted=False
        for h in [1e-6,5e-7,2.5e-7]:
            pair=[];crossed=False;reason=None
            try:
                for sign in [1,-1]:
                    fb=build(parameters(theta,sign*h*direction),data,ownership=ownership)
                    fv,_=matrices(fb);fx=solve(fv['M'],fv['s'])
                    pair.append({k:split(v)[0] for k,v in outputs(fb,fx,u).items()})
            except ValueError as e:
                crossed=True;reason=str(e)
            if crossed:
                fd.append({'direction':i,'step':h,'refused':True,'reason':reason,'pass':False});continue
            got={k:(pair[0][k]-pair[1][k])/(2*h) for k in pred}
            metrics={k:metric(got[k],pred[k]) for k in pred}
            ok=all(metrics[k]['normalized_error']<=2e-5 for k in ['outgoing','F','R_gamma'])
            accepted|=ok
            fd.append({'direction':i,'coordinates':direction.tolist(),'step':h,'refused':False,'metrics':metrics,'pass':ok})
            for k,v in got.items():
                fd_saved[str(i)+'_'+str(h)+'_'+k]=v
        fd.append({'direction_summary':i,'at_least_one_step_pass':accepted})
    np.savez(OUT/'MIXED_FINITE_DIFFERENCES.npz',**fd_saved)
    E={'records':fd,'pass':all(x['at_least_one_step_pass'] for x in fd if 'direction_summary' in x),
       'interpretation':'Three points do not establish asymptotic convergence; retain worsening and all refusals.'}
    dump('MIXED_FINITE_DIFFERENCES.json',E)
    F=controls();dump('CONTROLS.json',F)
    reported={'unit':'REC-HISTORY-THERMO01','method':'Projection of already loaded saved analytic arrays; no new source evaluation or solve',
              'axes':['xe','xHII','lnTR','lnTM','lnnH','lnH'],
              'base':{k:analytic[k] for k in ['F','R_gamma','radiation_energy','atomic_energy']},
              'six_axis_derivatives':{k:doutput[k].tolist() for k in ['F','R_gamma','radiation_energy','atomic_energy']},
              'outgoing_lines':{str(row):{'base':analytic['outgoing'][row],
                         'six_axis_derivative':doutput['outgoing'][row].tolist(),
                         'pure_H_derivative':pure['outgoing'][row]} for row in [311,312,313]},
              'pure_H_derivatives':{k:pure[k] for k in ['F','R_gamma','radiation_energy','atomic_energy']},
              'units':{'F':'dxHII/d ln a','R_gamma':'m^-3 s^-1',
                       'radiation_energy':'J m^-3 s^-1','atomic_energy':'J m^-3 s^-1',
                       'outgoing_lines':'dimensionless signed Wien departure',
                       'derivatives':'per dimensionless primitive increment'},'physical_epsilon':None}
    # read_npz returns zero-dimensional NumPy arrays for scalar saved values.
    # This is an explicit scalar projection, not a generic array JSON fallback.
    reported['base']={k:v.item() for k,v in reported['base'].items()}
    dump('REPORTED_VALUES.json',reported)
    after=raw_hashes();dump('PRIMARY_RAW_HASHES_AFTER.json',after)
    summary={'unit':'REC-HISTORY-THERMO01','status':'CONTINUATION_COMPLETE_AWAITING_ASTRA',
             'original_primary_invocation':'Failed serialization, retained as failed; never rewritten as successful',
             'criteria':{'A_literal_reconstruction':all(x['pass'] for x in A.values()),'B_complex':B['pass'],
                         'C_backward':C['primal']['pass'] and C['tangent']['pass'],
                         'D_identities':all(x['pass'] for x in identities.values()),'E_mixedFD':E['pass'],'F_controls':F['pass']},
             'A_evidence':'results/primary001/LITERAL_PARITY.json','B_evidence':'results/primary001/COMPLEX_COMPARISON.json',
             'primary_raw_hashes_unchanged':before==after,'original_large_RHS':13,'continuation_large_RHS':RHS,
             'cumulative_large_RHS':13+RHS,'large_RHS_ceiling':25,
             'small_numerical_RHS':F['small_RHS_including_exact_rational'],'escape_probes':F['escape_probe_count'],
             'new_base_tangent_complex_solves':0,'restricted_seed_source_builds':1,
             'native_runtime':0,'new_IVP':0,'old_replay':0,'physical_epsilon':None,'production':'NOT_APPROVED',
             'requested_model':'gpt-6.1-sol','observed_model':None}
    a_largest=max((v.get('normalized_error',0),k) for k,v in A.items())
    b_largest=max((v['normalized_error'],section,k,v['axis'])
                  for section in ['coefficients','outputs'] for k,rows in B[section].items() for v in rows)
    fd_rows=[x for x in fd if 'metrics' in x]
    summary['diagnostic_counts_and_maxima']={
        'A_block_count':len(A),'A_largest':{'normalized_error':a_largest[0],'block':a_largest[1]},
        'B_largest_named_coefficient_or_output':{'normalized_error':b_largest[0],'section':b_largest[1],
                                                'block':b_largest[2],'axis':b_largest[3]},
        'B_overall_max_including_state':B['max_normalized_error'],
        'C_saved_primal_components':int(saved['primal_residual'].size),
        'C_saved_tangent_components':int(saved['tangent_residual'].size),
        'C_max_componentwise_residual':max(C['primal']['max_componentwise_residual'],C['tangent']['max_componentwise_residual']),
        'D_identity_groups':len(identities),'D_restricted_seed_checks':len(pure_checks),
        'D_restricted_max_absolute_error':max(x['max_absolute_error'] for x in pure_checks.values()),
        'E_endpoint_RHS':RHS,'E_direction_count':2,'E_steps_recorded':len([x for x in fd if 'step' in x]),
        'E_max_normalized_outgoing_error':max((x['metrics']['outgoing']['normalized_error'] for x in fd_rows),default=None),
        'F_manufactured_count':len(F['manufactured']),'F_small_RHS':F['small_RHS_including_exact_rational'],
        'F_manufactured_max_normalized_error':max(x['normalized_derivative_error'] for x in F['manufactured']),
        'F_escape_probe_count':F['escape_probe_count'],
        'F_escape_max_derivative_absolute_error':max(max(x['p_prime_absolute_error'],x['A_prime_absolute_error']) for x in F['escape_probes']),
        'F_refusal_count':len(F['refusal_controls'])}
    summary['all_prescribed_checks_pass']=all(summary['criteria'].values()) and before==after
    if not summary['all_prescribed_checks_pass']:
        summary['status']='FINDING_RETURN_TO_ASTRA'
    dump('SUMMARY.json',summary)
    print(json.dumps(summary,indent=2,allow_nan=False,default=json_scalar),flush=True)
    return 0 if summary['all_prescribed_checks_pass'] else 2


if __name__=='__main__':
    try:
        sys.exit(main())
    except Exception as e:
        OUT.mkdir(parents=True,exist_ok=True)
        dump('EXCEPTION.json',{'status':'FINDING_RETURN_TO_ASTRA','type':type(e).__name__,'message':str(e),
                              'continuation_large_RHS_used':RHS,'cumulative_large_RHS_used':13+RHS,
                              'traceback':traceback.format_exc()})
        raise

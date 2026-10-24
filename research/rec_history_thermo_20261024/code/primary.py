"""Exactly one newly reconstructed local six-axis primary, no trajectory.

Invoke only through run_bounded.py after root RUN_READY authorization. Every
scientific computation, including controls and source loading, is in this child.
"""
import json
import sys
import traceback
from pathlib import Path
import numpy as np
from scipy.linalg import lu_factor,lu_solve
from inputs import load
from scalar import Dual,split
from source import build,matrices,outputs,parameters,AXES,E21,EV_J
from controls import run as controls

UNIT=Path(__file__).resolve().parents[1]
OUT=UNIT/'results/primary001'
EPS=np.finfo(float).eps
RHS=0


def dump(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def solve(M,b):
    global RHS
    count=1 if b.ndim==1 else b.shape[1]
    if RHS+count>25:
        raise RuntimeError('LARGE_RHS_CAP')
    RHS+=count
    # A fresh factorization for a genuinely different complex/FD matrix.
    return lu_solve(lu_factor(M,check_finite=True),b,check_finite=True)


def metric(a,b):
    a=np.asarray(a);b=np.asarray(b)
    error=float(np.max(np.abs(a-b)))
    scale=max(float(np.max(np.abs(a))),float(np.max(np.abs(b))),1e-280)
    return {'absolute_error':error,'scale':scale,'normalized_error':error/scale,
            'both_exact_zero':bool(np.all(a==0) and np.all(b==0))}


def parity_metric(a,b):
    m=metric(a,b);m['scale']=max(float(np.max(np.abs(b))),1e-280)
    m['normalized_error']=m['absolute_error']/m['scale'];m['pass']=m['normalized_error']<=5e-9
    return m


def backward(M,X,s,dM=None,dX=None,ds=None):
    if dX is None:
        residual=M@X-s;gross=np.abs(M)@np.abs(X)+np.abs(s)
    else:
        residual=M@dX+np.einsum('ijk,j->ik',dM,X)-ds
        gross=np.abs(M)@np.abs(dX)+np.einsum('ijk,j->ik',np.abs(dM),np.abs(X))+np.abs(ds)
    ratio=np.zeros_like(gross)
    np.divide(np.abs(residual),gross,out=ratio,where=gross!=0)
    zeros_ok=bool(np.all(residual[gross==0]==0))
    return {'max_componentwise_residual':float(np.max(ratio)),
            'zero_gross_exact':zeros_ok,'pass':zeros_ok and float(np.max(ratio))<=1024*EPS},residual,gross


def roundoff_identity(residual,gross):
    residual=np.asarray(residual);gross=np.asarray(gross)
    return {'max_absolute_error':float(np.max(np.abs(residual))),
            'max_gross':float(np.max(gross)),
            'pass':bool(np.all(np.abs(residual)<=512*EPS*gross))}


def flatten_outputs(out):
    return np.r_[out['outgoing'],out['F'],out['R_gamma']]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    data=load(UNIT)
    if not np.array_equal(data['energy'],data['virtual'][:,0]):
        raise ValueError('ENERGY_SOURCE_SNAPSHOT_IDENTITY')
    theta=data['theta'];u=data['incoming'];X0=data['prepared']['X0']
    # A1 literal parity, zero linear solves. Keep its arrays and diagnostics.
    literal=build(parameters(theta),data,literal=True)
    lv,ld=matrices(literal)
    lo={k:split(v)[0] for k,v in outputs(literal,X0,u).items()}
    reference={'M':data['prepared']['M'],'s':data['prepared']['source'],
               'Trr':data['Trr'],'Trv':data['Trv'],'Tvr':data['Tvr'],'Tvv':data['Tvv'],
               'sr':data['real_rows'][:,1],'sv':data['virtual'][:,7],
               'tau':data['virtual'][:,5],'Alpha':data['real_rows'][:,2],
               'DAlpha':data['real_rows'][:,3],'Beta':data['real_rows'][:,4],
               'Aup':data['virtual'][:,9],'Adn':data['virtual'][:,10],
               'gamma':data['virtual'][:,11],'p':data['virtual'][:,12],
               'A2p_up':data['meta']['A2p_up_sInv'],'A2p_dn':data['meta']['A2p_dn_sInv']}
    parity={k:parity_metric(lv[k],v) for k,v in reference.items()}
    native_out=np.r_[data['virtual'][:,3],[data['meta']['Dfminus_Lya'],data['meta']['Dfminus_Lyb'],data['meta']['Dfminus_Lyg']]]
    parity['outgoing_at_stored_X0']=parity_metric(lo['outgoing'],native_out)
    parity['F_at_stored_X0']=parity_metric(lo['F'],data['meta']['dxHIIdlna'])
    parity['structural_zeros']={'pass':all(bool(np.all(lv[k][v==0]==0)) for k,v in reference.items() if np.asarray(v).ndim>0)}
    np.savez(OUT/'LITERAL_PARITY.npz',**{k:np.asarray(v) for k,v in lv.items()},**{'out_'+k:v for k,v in lo.items()})
    dump('LITERAL_PARITY.json',parity)
    # All scientific derivatives below use the consistent stable evaluation.
    blocks=build(parameters(theta,dual=True),data)
    base,der=matrices(blocks)
    dump('BRANCH_OWNERSHIP.json',{'axes':AXES,'signature':blocks['ownership'],
         'native_tau_threshold':1e-6,'transparent_threshold':1e-30,'representation_threshold':.03})
    np.savez(OUT/'BASE_COEFFICIENTS.npz',**base)
    np.savez(OUT/'COEFFICIENT_DERIVATIVES.npz',**der)
    X=solve(base['M'],base['s'])
    tangent_rhs=der['s']-np.einsum('ijk,j->ik',der['M'],X)
    DX=solve(base['M'],tangent_rhs)
    out_d=outputs(blocks,[Dual(X[i],DX[i]) for i in range(313)],u)
    output={};doutput={}
    for k,v in out_d.items():
        output[k],doutput[k]=split(v)
    np.savez(OUT/'ANALYTIC_RESPONSE.npz',X=X,dX=DX,tangent_rhs=tangent_rhs,
             **output,**{'d_'+k:v for k,v in doutput.items()})
    gaps={k:metric(base[k],lv[k]) for k in base}
    # At stored X0 isolates the evaluation change; solved stable output is separate.
    stable_stored={k:split(v)[0] for k,v in outputs(build(parameters(theta),data),X0,u).items()}
    gaps['observables_at_stored_X0']={k:metric(stable_stored[k],lo[k]) for k in lo}
    gaps['new_stable_solved_vs_stored_native_outgoing']=metric(output['outgoing'],native_out)
    dump('NATIVE_STABLE_GAPS.json',gaps)
    # Independent complex-step: plain complex values, shared source equations.
    cs_der={k:np.zeros_like(v) for k,v in der.items()}
    cs_out={k:np.zeros_like(v) for k,v in doutput.items()}
    cs_X=np.zeros_like(DX)
    for axis in range(6):
        shift=np.zeros(6,dtype=complex);shift[axis]=1e-20j
        cb=build(parameters(theta,shift),data,ownership=blocks['ownership'])
        cv,_=matrices(cb)
        cx=solve(cv['M'],cv['s'])
        co={k:split(v)[0] for k,v in outputs(cb,cx,u).items()}
        for k in cs_der:
            cs_der[k][...,axis]=np.imag(cv[k])/1e-20
        for k in cs_out:
            cs_out[k][...,axis]=np.imag(co[k])/1e-20
        cs_X[:,axis]=np.imag(cx)/1e-20
    np.savez(OUT/'COMPLEX_RESPONSE.npz',X_derivative=cs_X,
             **{'coef_'+k:v for k,v in cs_der.items()},**{'out_'+k:v for k,v in cs_out.items()})
    comparison={'coefficients':{},'outputs':{},'state':[]}
    for k in der:
        comparison['coefficients'][k]=[dict(axis=AXES[j],**metric(der[k][...,j],cs_der[k][...,j])) for j in range(6)]
    for k in doutput:
        comparison['outputs'][k]=[dict(axis=AXES[j],**metric(doutput[k][...,j],cs_out[k][...,j])) for j in range(6)]
    comparison['state']=[dict(axis=AXES[j],**metric(DX[:,j],cs_X[:,j])) for j in range(6)]
    component=[]
    for j in range(6):
        scale=max(float(np.max(np.abs(doutput['outgoing'][:,j]))),float(np.max(np.abs(cs_out['outgoing'][:,j]))),1e-280)
        for row in [0,139,140,270,310,311,312,313]:
            component.append({'axis':AXES[j],'row':row,'analytic':float(doutput['outgoing'][row,j]),
                  'complex':float(cs_out['outgoing'][row,j]),'absolute_error':float(abs(doutput['outgoing'][row,j]-cs_out['outgoing'][row,j])),
                  'column_scale':scale,'column_normalized_error':float(abs(doutput['outgoing'][row,j]-cs_out['outgoing'][row,j])/scale)})
        for key in ['F','R_gamma']:
            component.append({'axis':AXES[j],'row':key,'analytic':float(doutput[key][j]),'complex':float(cs_out[key][j]),
                  **metric(doutput[key][j],cs_out[key][j])})
    comparison['selected_components']=component
    errors=[x['normalized_error'] for section in ['coefficients','outputs'] for group in comparison[section].values() for x in group]
    errors += [x['normalized_error'] for x in comparison['state']]
    comparison['max_normalized_error']=max(errors);comparison['pass']=max(errors)<=2e-8
    dump('COMPLEX_COMPARISON.json',comparison)
    bp,rp,gp=backward(base['M'],X,base['s'])
    bt,rt,gt=backward(base['M'],X,base['s'],der['M'],DX,der['s'])
    np.savez(OUT/'BACKWARD_RESIDUALS.npz',primal_residual=rp,primal_gross=gp,tangent_residual=rt,tangent_gross=gt)
    dump('BACKWARD_RESIDUALS.json',{'primal':bp,'tangent':bt})
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
    # Independent restricted seeding: xe and xHII share one physical direction.
    # This rebuilds coefficients, but reuses X and ambient pureX: zero new RHS.
    seed=np.eye(6)[0]
    restricted_theta=[Dual(theta[i],seed if i<2 else np.zeros(6)) for i in range(6)]
    restricted=build(restricted_theta,data,ownership=blocks['ownership'])
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
    # Mixed finite differences: two directions * three steps * two RHS =12.
    fd=[];saved={}
    for i,direction in enumerate([np.array([.1,-.2,.3,-.1,.2,-.3]),np.array([.2,.2,-.1,.1,-.3,.2])]):
        pred={k:np.tensordot(v,direction,axes=(-1,0)) for k,v in doutput.items()}
        accepted=False
        for h in [1e-6,5e-7,2.5e-7]:
            pair=[];crossed=False;reason=None
            try:
                for sign in [1,-1]:
                    fb=build(parameters(theta,sign*h*direction),data,ownership=blocks['ownership'])
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
                saved[str(i)+'_'+str(h)+'_'+k]=v
        fd.append({'direction_summary':i,'at_least_one_step_pass':accepted})
    np.savez(OUT/'MIXED_FINITE_DIFFERENCES.npz',**saved)
    dump('MIXED_FINITE_DIFFERENCES.json',{'records':fd,'pass':all(x['at_least_one_step_pass'] for x in fd if 'direction_summary' in x),
        'interpretation':'Three points do not establish asymptotic convergence; retain worsening and all refusals.'})
    control=controls();dump('CONTROLS.json',control)
    summary={'unit':'REC-HISTORY-THERMO01','status':'DIAGNOSTICS_COMPLETE_AWAITING_ASTRA',
             'criteria':{'A_literal_reconstruction':all(x['pass'] for x in parity.values()),
                         'B_complex':comparison['pass'],'C_backward':bp['pass'] and bt['pass'],
                         'D_identities':all(x['pass'] for x in identities.values()),
                         'E_mixedFD':all(x['at_least_one_step_pass'] for x in fd if 'direction_summary' in x),
                         'F_controls':control['pass']},
             'large_system_RHS':RHS,'large_system_RHS_ceiling':25,
             'small_RHS_including_exact_rational':control['small_RHS_including_exact_rational'],
             'escape_probe_count':control['escape_probe_count'],
             'source_model':'stable evaluation of native piecewise real equations; A1 separate literal parity',
             'actual_physical_epsilon':None,'physical_completion_percent':None,'production':'NOT_APPROVED',
             'new_IVP':0,'native_runtime':0,'old_replay':0,'requested_model':'gpt-6.1-sol','observed_model':None}
    summary['all_prescribed_checks_pass']=all(summary['criteria'].values())
    if not summary['all_prescribed_checks_pass']:
        summary['status']='FINDING_RETURN_TO_ASTRA'
    dump('SUMMARY.json',summary)
    print(json.dumps(summary,indent=2,allow_nan=False),flush=True)
    return 0 if summary['all_prescribed_checks_pass'] else 2


if __name__=='__main__':
    try:
        sys.exit(main())
    except Exception as e:
        OUT.mkdir(parents=True,exist_ok=True)
        dump('EXCEPTION.json',{'status':'FINDING_RETURN_TO_ASTRA','type':type(e).__name__,'message':str(e),
                              'large_RHS_used':RHS,'traceback':traceback.format_exc()})
        raise

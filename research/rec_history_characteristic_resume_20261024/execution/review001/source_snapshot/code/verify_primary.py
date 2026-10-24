"""One frozen 127-row primary; stops at first failure, no repair or old replay."""
import os
for _key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[_key]='1'
import argparse,json,math,sys,traceback,hashlib
from pathlib import Path
import numpy as np
import characteristic_adapter as A
import independent_reference as I
mp=I.mp
R=Path(__file__).resolve().parents[1]
COUNTS={}


def serial(x):
    if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v) for v in x]
    if isinstance(x,np.ndarray):return serial(x.tolist())
    if isinstance(x,(np.floating,np.integer)):return serial(x.item())
    if isinstance(x,mp.mpf):return mp.nstr(x,82)
    if isinstance(x,float) and not math.isfinite(x):return str(x)
    return x


def check(actual,expected,gate=5e-12,label='value',scale_mode='scaled',floor=0.):
    aa=I.M(float(actual));ee=I.M(expected);error=abs(aa-ee)
    scale=max(I.M(1),abs(aa),abs(ee)) if scale_mode=='scaled' else max(abs(ee),I.M('1e-300'))
    limit=I.M(gate)*scale+I.M(floor)
    row=dict(label=label,actual=float(actual),expected=mp.nstr(ee,82),absolute_error=mp.nstr(error,40),scale=mp.nstr(scale,40),limit=mp.nstr(limit,40),regime=scale_mode,pass_check=bool(error<=limit))
    if not row['pass_check']:raise AssertionError(json.dumps(row))
    return row


def arrays(a,e,gate=5e-12,label='vector'):
    return [check(x,y,gate,f'{label}_{i}') for i,(x,y) in enumerate(zip(a,e))]


def field_input(c):
    times=c['eta0']+c['h']*np.arange(c['iz']);coef=np.asarray(c['coefficient_base'])[:,None]+np.asarray(c['coefficient_slopes'])[:,None]*times
    dcoef=np.repeat(np.asarray(c['coefficient_data_tangent'])[:,None],c['iz'],axis=1)
    return coef,dcoef


def composite_args(c):
    co,dco=field_input(c)
    return dict(n=c['n'],b=c['b'],lam=c['lam'],eta_t=c['eta_t'],xt=c['xt'],eta0=c['eta0'],h=c['h'],coeff=co,iz=c['iz'],xr_p=c['xr_p'],x1s=c['x1s'],tau=c['tau'],nH_cm3=c['nH_cm3'],H_t=c['H_t'],dn=c['dn'],db=c['db'],dlam=c['dlam'],deta_t=c['deta_t'],dlnxt=c['dlnxt'],dcoeff=dco,dxr_p=c['dxr_p'],dx1s=c['dx1s'],dtau=c['dtau'])


def run_guard(name):
    expected={
      'direction_shape':'DIRECTION_SHAPE','direction_unit':'DIRECTION_UNIT','direction_nonfinite':'NONFINITE_INPUT','shear_trace':'SHEAR_TRACE','rate_nonpositive':'NONPOSITIVE_RATE','negative_lambda':'NEGATIVE_LOGRATIO','lambda_nonfinite':'NONFINITE_INPUT','nontangent':'NONTANGENT_DIRECTION','tangent_trace':'SHEAR_TANGENT_TRACE','tangent_overflow':'TANGENT_TRANSFORM_OVERFLOW','before_prefix':'HISTORY_RETAINED_DOMAIN','short_prefix':'HISTORY_RETAINED_DOMAIN','exclusive_endpoint':'HISTORY_RETAINED_DOMAIN','negative_absolute':'NEGATIVE_ABSOLUTE_OCCUPATION','knot_tangent':'NONSMOOTH_QUERY','missing_bound':'MISSING_ERROR_INPUT'}[name]
    try:
        if name=='direction_shape':A.crossing([1,0],[0,0,0],1)
        elif name=='direction_unit':A.crossing([2,0,0],[0,0,0],1)
        elif name=='direction_nonfinite':A.crossing([float('nan'),0,0],[0,0,0],1)
        elif name=='shear_trace':A.crossing([1,0,0],[.1,.1,.1],1)
        elif name=='rate_nonpositive':A.crossing([1,0,0],[-1,.5,.5],1)
        elif name=='negative_lambda':A.crossing([1,0,0],[0,0,0],-1)
        elif name=='lambda_nonfinite':A.crossing([1,0,0],[0,0,0],float('inf'))
        elif name=='nontangent':A.crossing_jvp(A.crossing([1,0,0],[0,0,0],1),dn=[1,0,0])
        elif name=='tangent_trace':A.crossing_jvp(A.crossing([1,0,0],[0,0,0],1),db=[1,0,0])
        elif name=='tangent_overflow':A.crossing_jvp(A.crossing([1,0,0],[-.9,.45,.45],100),dn=[0,1,0])
        elif name=='before_prefix':A.strict_interpolation(0.,.1,[1,2,3],3,-.01)
        elif name=='short_prefix':A.strict_interpolation(0.,.1,[1],1,0.)
        elif name=='exclusive_endpoint':A.strict_interpolation(0.,.1,[1,2,3],3,.2)
        elif name=='negative_absolute':A.HB.boundary(-2.,.1,1.,.2,reference_occupation=1.)
        elif name=='knot_tangent':A.strict_interpolation(0.,.125,[1,2,3],3,.125,1.)
        elif name=='missing_bound':A.error_envelope(e_H=None,K_eta=1,K_n=1,eps_F=1e-8,e_arithmetic=0,a_min=1,a_max=1,qt=1,tau=.2,H_t=1)
    except ValueError as exc:
        if str(exc)!=expected:raise AssertionError(f'WRONG_GUARD {name}: {exc}, expected {expected}')
        return dict(expected_exception=expected,observed_exception=str(exc),detected=True)
    raise AssertionError('GUARD_NOT_TRIGGERED '+name)


def actual_rows():
    p=R/'inputs/h4_numpy16_python_continuation.npz';assert hashlib.sha256(p.read_bytes()).hexdigest()=='b2489168155ad1a18a887a880eb0ca90376be5506c3c61d6bf06e9e70007c54c'
    with np.load(p,allow_pickle=False) as z:
        v=z['virtual_out'].copy();l=z['lyman_out'].copy();h=float(z['dlna'])
    assert v.shape==(311,24) and l.shape==(3,24) and h==2.1225e-5
    return np.concatenate([v,l],axis=0)


def run(c,data):
    g=c['group'];checks=[];details={};COUNTS[g]=COUNTS.get(g,0)+1
    if g=='root':
        r=A.crossing(c['n'],c['b'],c['lam'],c['eta_t']);ref=I.cross(c['n'],c['b'],c['lam'],c['eta_t']);checks+=[check(r['delta'],ref['delta'],label='root_delta'),check(r['eta_s'],ref['eta_s'],label='eta_s')];checks+=arrays(r['ns'],ref['ns'],label='source_direction');checks.append(check(np.dot(r['ns'],r['ns']),1,label='norm'));checks.append(check(r['residual'],0,label='root_residual'))
        # Killing relation in source-normalized form, never direct exp(Lambda).
        for i in range(3):
            predicted=mp.mpf(c['n'][i])*mp.exp((1+mp.mpf(c['b'][i]))*mp.mpf(r['delta'])-mp.mpf(c['lam']))
            checks.append(check(r['ns'][i],predicted,label=f'Killing_component_{i}'))
        if c['b'][0]==c['b'][1]:
            # Existing LRS C9 law at the returned delay, independent closed form.
            a=[1+mp.mpf(v) for v in c['b']];v=I.vec(c['n']);D=mp.sqrt(sum(vv*vv*mp.exp(2*aa*mp.mpf(r['delta'])) for vv,aa in zip(v,a)))
            checks+=arrays(r['ns'],[vv*mp.exp(aa*mp.mpf(r['delta']))/D for vv,aa in zip(v,a)],label='LRS_C9_Killing')
        details=dict(delta=r['delta'],flrw_delta=c['lam'],source_direction=r['ns'],residual=r['residual'],root_kind=r['root_kind'],bracket=r['bracket'])
    elif g=='tangent':
        r=A.crossing(c['n'],c['b'],c['lam'],c['eta_t']);j=A.crossing_jvp(r,c['dn'],c['db'],c['dlam'],c['deta_t']);ref=I.cross_difference(c)
        for k in ['ddelta','deta_s','dqt']:checks.append(check(j[k],ref[k],5e-9,k))
        checks+=arrays(j['dns'],ref['dns'],5e-9,'dns');details={'jvp':j,'fd_step':c['fd_step']}
    elif g=='wien':
        r=A.reference(c['xt'],c['lam'],c['delta'],c['dlnxt'],c['dlam'],c['ddelta']);ref=I.offset(c['xt'],c['lam'],c['delta'])
        checks.append(check(r['offset'],ref['offset'],c['relative_gate'],'Wien_difference','relative_reference_floor',c['absolute_floor']))
        refj=I.M(c['xt'])*ref['wt']*I.M(c['dlnxt'])-ref['xws']*(I.M(c['dlnxt'])+I.M(c['dlam'])-I.M(c['ddelta']))
        checks.append(check(r['doffset'],refj,c['relative_gate'],'Wien_jvp','relative_reference_floor',c['absolute_floor']))
        checks.append(check(r['offset']+r['wt'],ref['ws'],label='absolute_f_preservation'));details=r
    elif g=='composite':
        r=A.compose(**composite_args(c));ref=I.composite(c);j=I.composite_difference(c)
        for k in ['din','outgoing','absolute_in']:checks.append(check(r[k],ref[k],label=k))
        checks.append(check(r['ddin'],j['din'],5e-9,'din_JVP'));checks.append(check(r['dout'],j['outgoing'],5e-9,'outgoing_JVP'))
        checks.append(check(r['ledger']['R'],ref['rate'],label='single_event_number_ledger'));checks.append(check(r['ledger']['radiation_J_m3_s'],ref['energy'],label='single_event_energy_ledger'));checks.append(check(r['ledger']['atomic_internal_J_m3_s']+r['ledger']['radiation_J_m3_s'],0,label='local_energy_balance'))
        assert r['ledger']['extra_radiation_source']==0
        details={'eta_s':r['crossing']['eta_s'],'delta':r['crossing']['delta'],'Wien_offset':r['reference']['offset'],'din':r['din'],'outgoing':r['outgoing'],'ddin':r['ddin'],'dout':r['dout'],'ledger':r['ledger'],'fixed_cell':r['field']['k']}
    elif g=='actual':
        eta0=-math.log(8001)+c['g0']*c['h'];eta=eta0+c['h']*(c['cell']+c['alpha']);row=data[c['channel']];st=A.strict_interpolation(eta0,c['h'],row,c['iz'],eta)
        pos=(I.M(eta)-I.M(eta0))/I.M(c['h']);k=int(mp.floor(pos));alpha=pos-k;ref=(1-alpha)*I.M(float(row[k]))+alpha*I.M(float(row[k+1]))
        assert k==c['cell'];checks.append(check(st['value'],ref,64*np.finfo(float).eps,'actual_scalar_interpolation'))
        details={'channel':c['channel'],'cell':k,'alpha':st['alpha'],'eta':eta,'z':math.exp(-eta)-1,'eta0':eta0,'endpoint':eta0+c['h']*23,'value':st['value'],'left':float(row[k]),'right':float(row[k+1]),'clock':'photon_input_g_not_accepted_state_g_plus_one','ADM01_fixed_face_coverage':'0/313','M2':None,'independent_uncertainty':None}
    elif g=='guard':details=run_guard(c['guard'])
    elif g=='envelope':
        r=A.crossing(c['n'],c['b'],c['lam']);bound=A.error_envelope(**{k:c[k] for k in ['e_H','K_eta','K_n','eps_F','e_arithmetic','qt','tau','H_t']},a_min=min(r['a']),a_max=max(r['a']))
        exact=I.cross(c['n'],c['b'],c['lam']);d=exact['delta']+I.M(c['root_perturbation_fraction'])*I.M(bound['e_delta']);n=I.vec(c['n']);aa=[1+I.M(x) for x in c['b']];gg=[nn*mp.exp(a*d) for nn,a in zip(n,aa)];ns=I.direction(gg)
        true=.1+I.M('.03')*(-exact['delta'])+I.M('.02')*exact['ns'][0]+I.offset(c['xt'],c['lam'],exact['delta'])['offset']
        approx=I.M('.1')+I.M('.03')*(-d)+I.M('.02')*ns[0]+I.offset(c['xt'],c['lam'],d)['offset']+I.M(c['e_H'])/2
        error=abs(approx-true);ein=I.M(bound['e_in']);assert error<=ein,'ENVELOPE_INPUT'
        T=mp.exp(-I.M(c['tau'])/I.M(c['qt']));Afrac=1-T;number=I.M('1.3988697202667691e22')*I.M(c['H_t'])*I.M(c['qt'])*Afrac*error;energy=I.M('10.198714553953742')*I.M('1.602176634e-19')*number
        assert T*error<=I.M(bound['e_out']) and number<=I.M(bound['e_number']) and energy<=I.M(bound['e_energy']),'ENVELOPE_PROPAGATION'
        details={'bounds':bound,'independent_error':mp.nstr(error,80),'out_error':mp.nstr(T*error,80),'number_error':mp.nstr(number,80),'energy_error':mp.nstr(energy,80),'analytic_field':'H=.1+.03*eta+.02*n_x; K_eta=.03,K_n=.02 valid globally','tube_displacement':mp.nstr(d-exact['delta'],80),'sampled_M2_used':False}
    elif g=='defect':
        if c['defect']=='FLRW_delay_in_shear':
            ref=I.cross([.36,.48,.8],[.35,-.1,-.25],.7);bad=I.M(.7);error=abs(ref['delta']-bad);threshold=I.M('5e-12')*max(1,abs(ref['delta']))
        elif c['defect']=='omit_Wien_offset':
            ref=I.cross([.36,.48,.8],[.35,-.1,-.25],.7);error=abs(I.offset(1,.7,ref['delta'])['offset']);threshold=I.M('5e-12')
        else:
            eta0=-math.log(8001)+72892*2.1225e-5;eta=eta0+2.1225e-5*10.5;st=A.strict_interpolation(eta0,2.1225e-5,data[140],24,eta);bad=A.strict_interpolation(eta0+2.1225e-5,2.1225e-5,data[140],24,eta)
            # Defect detector is the frozen photon-clock identity and stencil,
            # not an assertion that all tiny occupation differences exceed unit-scale tolerance.
            error=abs(st['k']-bad['k']);threshold=0
        assert error>threshold,'DELIBERATE_DEFECT_NOT_DETECTED';details={'detected':True,'error':str(error),'threshold':str(threshold),'detector':'clock_and_fixed_cell_identity' if c['defect']=='photon_clock_plus_one' else 'independent_physical_reference'}
    return {'id':c['id'],'group':g,'status':'PASS','checks':checks,'details':details,'condition':c}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    plan=json.loads((R/'inputs/CASE_PLAN.json').read_text());assert plan['case_count']==127;data=actual_rows();rows=[];status='PASS_SCOPED';failure=None
    with (out/'raw_rows.jsonl').open('x') as stream:
        for c in plan['case_rows']:
            try:row=run(c,data)
            except Exception as exc:
                row={'id':c['id'],'group':c['group'],'status':'FAIL','condition':c,'exception':str(exc),'traceback':traceback.format_exc()};status='FAIL';failure=row
            clean=serial(row);rows.append(clean);stream.write(json.dumps(clean,allow_nan=False)+'\n');stream.flush();print(c['id'],row['status'],flush=True)
            if failure:break
    summary={'unit':'REC-HISTORY-02R','result':status,'planned_cases':plan['case_counts'],'case_invocations_started':COUNTS,'rows_saved':len(rows),'checks_saved':sum(len(x.get('checks',[])) for x in rows),'first_failure':failure,'mp_dps':80,'fd_step':plan['fd_step'],'root_bisection_iterations':300,'heldout_independent_probes':0,'native_runtime':0,'IVP':0,'dense_RHS':0,'old_replays':0,'actual_history_calibration':'INPUT_DEPENDENT_UNCALIBRATED','actual_h4_ADM01_face_coverage':'0/313','actual_M2':None,'parent_REC_HISTORY':'PARTIAL','first_failure_policy':'STOP_NO_AUTOREPAIR'}
    (out/'SUMMARY.json').write_text(json.dumps(serial(summary),indent=2,allow_nan=False)+'\n');return 0 if failure is None else 1
if __name__=='__main__':sys.exit(main())

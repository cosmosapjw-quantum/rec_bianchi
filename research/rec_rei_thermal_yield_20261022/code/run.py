"""One-command THERM01 execution, cache verification and finite validation.

Exactly six nominal plus two validation IVPs. Plotting reads cached raw outputs.
No donor campaign/test dispatch is imported. Run with one numerical thread.
"""
from __future__ import annotations
import os
# Thread limits are set before numerical-library imports in this entry point.
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from thermal import ROOT,XEND,ThermalSystem,lift34,KB
from checks import run_checks

SCHEMA='therm01.dynamic34.full63.v1'
BASE=dict(Sigma_F=.15,matter_A=.6,radiation_A=.15,T0_K=1000.,Emax_eV=60.,uv_multiplier=1.)
CASES={
 'thermal_iso60':dict(BASE,Sigma_F=0.,matter_A=0.,radiation_A=0.),
 'thermal_split60':dict(BASE),
 'thermal_opposed60':dict(BASE,radiation_A=-.15),
 'thermal_split40':dict(BASE,Emax_eV=40.),
 'thermal_warm60':dict(BASE,T0_K=5000.),
 'thermal_uv_off':dict(BASE,T0_K=10000.,uv_multiplier=0.),
 'thermal_split60_tight34':dict(BASE),
 'thermal_split60_oracle63':dict(BASE)}


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False,
        default=lambda value:value.item() if isinstance(value,np.generic) else str(value))+'\n')
def identity(case):
    sources={str(p.relative_to(ROOT)):digest(p) for p in (
        ROOT/'code/thermal.py',ROOT/'code/run.py',ROOT/'FROZEN_CONTRACT.md',
        ROOT/'vendor/rei_pr220/code/compact_system.py',ROOT/'vendor/rei_pr220/provenance/DONOR_IDENTITY.json')}
    config=dict(CASES[case],id=case,samples=193,x_end=XEND,method='BDF',
                rtol=2e-10 if case.endswith('tight34') else 2e-8,
                atol_divisor=100 if case.endswith('tight34') else 1,
                full63=case.endswith('oracle63'),max_step=.025,dense_output=True)
    payload=dict(schema=SCHEMA,sources=sources,config=config)
    payload['sha256']=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return payload


def quadrature(system,solution,grid):
    out={};samples={}
    for order in (8,16):
        nodes,weights=leggauss(order);intervals=[];all_x=[];all_states=[]
        for a,b in zip(grid[:-1],grid[1:]):
            if time.perf_counter()-system.started>180:raise TimeoutError('THERM01 quadrature cooperative180s ceiling')
            xs=(a+b)/2+(b-a)/2*nodes
            states=solution.sol(xs)
            values=np.array([system.ledger_integrand(float(x),states[:,j]) for j,x in enumerate(xs)])
            intervals.append((b-a)/2*(weights@values))
            all_x.extend(xs);all_states.append(states.T)
        out[order]=np.vstack((np.zeros(3),np.cumsum(intervals,axis=0)))
        samples[order]=(np.array(all_x),np.vstack(all_states))
    return out,samples


def run_case(name):
    ident=identity(name);directory=ROOT/'data'/name;directory.mkdir(parents=True,exist_ok=True)
    result_path=directory/'RESULT.json';raw=directory/'trajectory.npz'
    if result_path.exists():
        old=json.loads(result_path.read_text())
        if old['identity']['sha256']!=ident['sha256']:raise RuntimeError('SOURCE_CONFIG_IDENTITY_CHANGED:'+name)
        if old['status']!='PASS':raise RuntimeError('PRESERVED_FAILED_CASE_REQUIRES_ROOT_DECISION:'+name)
        if digest(raw)!=old['raw_sha256']:raise RuntimeError('RAW_IDENTITY_CHANGED:'+name)
        print(name+': CACHE_VERIFIED',flush=True);return old
    if raw.exists():raise RuntimeError('preserved raw without receipt: '+name)
    result=dict(schema=SCHEMA,id=name,status='FAIL',identity=ident,gates={},
        environment=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),
             numerical_threads=1,requested_role='native lower-tier mechanical executor',
             observed_model_identity='not exposed by runtime'),
        statuses=dict(Physical='HOLD',REC_U5='HOLD_9_FAIL/HOLD_8_FAIL',closure='CLOSED_HOLD_NOT_RESET',
             global_convergence='NOT_RUN',production='NOT_APPROVED',REI_activation=False))
    started=time.perf_counter()
    try:
        c=ident['config'];system=ThermalSystem(c,full=c['full63']);grid=np.linspace(0,XEND,193)
        atol=np.r_[np.full(40,2e-11),np.full(21,2e-10),2e-11,2e-6]/c['atol_divisor']
        if not c['full63']:
            from thermal import restrict63
            atol=restrict63(atol)
        solution=solve_ivp(system.rhs,(0,XEND),system.y0,method='BDF',rtol=c['rtol'],atol=atol,
            t_eval=grid,max_step=.025,dense_output=True)
        # Preserve every returned solver point even if a finite gate fails.
        np.savez_compressed(directory/'solver_return.npz',x=solution.t,raw_state=solution.y.T)
        if not solution.success or solution.y.shape!=(system.size,193):
            raise RuntimeError('BDF incomplete: '+solution.message)
        full_state=solution.y if c['full63'] else lift34(solution.y)
        Y=full_state[40:61].T*system.scale
        histories=[system.diagnostics(float(x),solution.y[:,i]) for i,x in enumerate(grid)]
        obs=np.array([h.pop('signed_observables') for h in histories]);names=list(histories[0])
        diagnostics=np.array([[h[k] for k in names] for h in histories]);D={k:diagnostics[:,i] for i,k in enumerate(names)}
        totals=D['epsilon_total_J'];quad,samples=quadrature(system,solution,grid)
        residual=totals-totals[0]-quad[16][:,0]+quad[16][:,1]+quad[16][:,2]
        denom=np.maximum.reduce((np.full(193,abs(totals[0])),abs(totals),np.sum(abs(quad[16]),axis=1)))
        energy_normalized=abs(residual)/denom
        quad_difference=np.max(abs(quad[8]-quad[16]),axis=1)/denom
        isotope_errors={}
        for isotope,indices in system.atomic.isotope_groups.items():
            expected=float(system.atomic.initial_Y[list(indices)].sum())
            isotope_errors[isotope]=float(np.max(abs(Y[:,indices].sum(axis=1)-expected))/system.scale[indices[0]])
        minimum=float(np.min(full_state[40:61]));baryon=float(np.max(abs(Y@system.atomic.A-1)))
        number=float(max(np.max(abs(full_state[13]-1)),np.max(abs(full_state[31]-1))))
        tensor=float(np.max(abs(obs[:,3]-obs[:,1]-obs[:,2])))
        gates=dict(full_interval_193=bool(solution.t[-1]==XEND and len(solution.t)==193),
             finite=bool(np.isfinite(solution.y).all() and np.isfinite(diagnostics).all()),
             minimum_isotope_fraction=minimum>=-2e-8,
             isotope_inventory=max(isotope_errors.values())<2e-7,baryon_error=baryon<2e-8,
             nonnegative_electrons=float(D['ne_m3'].min())>=0,
             temperature_domain=bool(D['T_K'].min()>=100 and D['T_K'].max()<=1e6 and
                 system.min_trial_T>=100 and system.max_trial_T<=1e6),
             tau_nondecreasing=float(np.min(np.diff(full_state[61])))>=-2e-10,
             number_monopoles=number<2e-9,einstein=float(D['einstein_residual'].max())<2e-13,
             signed_tensor_sum=tensor<2e-16,trace_energy_fraction=float(D['trace_energy_fraction'].max())<1e-5,
             zero_n_T=bool(np.all(full_state[40+np.array([0,5,6])]==0) and np.all(D['decay_max']==0)),
             dense_integrated_energy=float(energy_normalized.max())<3e-6,
             GL8_GL16_difference=float(quad_difference.max())<3e-6)
        np.savez_compressed(raw,x=grid,z=21*np.exp(-grid)-1,raw_state=solution.y.T,
            full63_state=full_state.T,Y=Y,scaled_populations=full_state[40:61].T,
            signed_observables=obs,diagnostics=diagnostics,diagnostic_names=np.array(names),
            species_names=np.array(system.atomic.names),A=system.atomic.A,q=system.atomic.q,
            isotope_scales=system.scale,initial_Y=system.atomic.initial_Y,
            ledger_GL8=quad[8],ledger_GL16=quad[16],ledger_residual_J=residual,
            ledger_denominator_J=denom,ledger_normalized_residual=energy_normalized,
            ledger_GL_difference=quad_difference,
            dense_GL8_x=samples[8][0],dense_GL8_state=samples[8][1],
            dense_GL16_x=samples[16][0],dense_GL16_state=samples[16][1])
        result.update(status='PASS' if all(gates.values()) else 'FAIL',gates=gates,raw_sha256=digest(raw),
            solver_return_sha256=digest(directory/'solver_return.npz'),nfev=solution.nfev,njev=solution.njev,nlu=solution.nlu,
            rhs_calls=system.nrhs,min_scaled_population=minimum,isotope_errors=isotope_errors,baryon_error=baryon,
            number_monopole_error=number,tensor_sum_error=tensor,
            max_einstein_residual=float(D['einstein_residual'].max()),max_trace_energy_fraction=float(D['trace_energy_fraction'].max()),
            T_range_K=[float(D['T_K'].min()),float(D['T_K'].max())],
            trial_T_range_K=[system.min_trial_T,system.max_trial_T],final_T_K=float(D['T_K'][-1]),
            final_tau=float(D['tau_T'][-1]),max_energy_residual=float(energy_normalized.max()),
            max_GL_difference=float(quad_difference.max()),solver_message=solution.message)
    except Exception as error:
        result.update(error=str(error),traceback=traceback.format_exc())
    result['wall_seconds']=time.perf_counter()-started;dump(result_path,result)
    print(name+': '+result['status']+' '+str(round(result['wall_seconds'],3))+'s',flush=True)
    if result['status']!='PASS':raise RuntimeError('THERM01 finite case failed; preserved '+str(result_path))
    return result


def comparisons():
    nominal=np.load(ROOT/'data/thermal_split60/trajectory.npz')
    ni={k:i for i,k in enumerate(nominal['diagnostic_names'])};rows={}
    for case in ('thermal_split60_tight34','thermal_split60_oracle63'):
        other=np.load(ROOT/'data'/case/'trajectory.npz');oi={k:i for i,k in enumerate(other['diagnostic_names'])}
        tn=nominal['diagnostics'][:,ni['T_K']];to=other['diagnostics'][:,oi['T_K']]
        values=dict(max_relative_T=float(np.max(abs(tn-to)/np.maximum(abs(tn),abs(to)))),
            max_charge_fraction_absolute=float(np.max(abs(nominal['scaled_populations']-other['scaled_populations']))),
            max_tau_absolute=float(np.max(abs(nominal['diagnostics'][:,ni['tau_T']]-other['diagnostics'][:,oi['tau_T']]))),
            max_signed_normalized_absolute=float(np.max(abs(nominal['signed_observables']-other['signed_observables']))))
        values['gates']=dict(T=values['max_relative_T']<3e-5,fractions=values['max_charge_fraction_absolute']<3e-5,
            tau=values['max_tau_absolute']<3e-7,signed=values['max_signed_normalized_absolute']<3e-7)
        values['status']='PASS' if all(values['gates'].values()) else 'FAIL';rows[case]=values
    dump(ROOT/'results/VALIDATION_COMPARISONS.json',rows)
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checks',action='store_true');parser.add_argument('--run',action='store_true')
    parser.add_argument('--plot',action='store_true');args=parser.parse_args()
    if not any(vars(args).values()):args.checks=args.run=args.plot=True
    if args.checks or args.run:
        checks=run_checks(ROOT/'evidence/UNIT_CHECKS.json')
        print('NEW_UNIT_CHECKS: '+checks['status'],flush=True)
        if checks['status']!='PASS':return 1
    if args.run:
        science_started=time.perf_counter();receipts=[]
        for name in CASES:
            if time.perf_counter()-science_started>1200:raise TimeoutError('THERM01 total science1200s ceiling')
            receipts.append(run_case(name))
        comparison=comparisons()
        success=all(r['status']=='PASS' for r in receipts) and all(r['status']=='PASS' for r in comparison.values())
        dump(ROOT/'results/SCIENCE_SUMMARY.json',dict(status='PASS' if success else 'FAIL',unique_new_IVPs=8,
            case_ids=list(CASES),case_receipts=[str(Path('data')/n/'RESULT.json') for n in CASES],
            comparisons=comparison,total_execution_wall_seconds=time.perf_counter()-science_started,
            scope='finite representative checks; global convergence NOT_RUN',
            physical='HOLD',production='NOT_APPROVED',REI_activation=False))
        if not success:return 1
    if args.plot:
        from plot import make_figures
        make_figures()
    return 0

if __name__=='__main__':raise SystemExit(main())

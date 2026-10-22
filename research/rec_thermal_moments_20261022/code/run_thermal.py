"""Run the frozen eight distinct thermal restarts, preserving every receipt.

python code/run_thermal.py --execute
Already completed configurations are reused only with matching local source,
source-table and donor identities. Old REC126 is input, never an execution job.
"""
from __future__ import annotations

import os
for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_name]='1'
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import sys
import time
import traceback
import numpy as np
import scipy
from scipy.integrate import solve_ivp, simpson

from thermal_system import ThermalSystem, UNIT, DONOR, thermal_uv

CASES=('s00_m02_r02','s03_m03_r03','s04_m04_r04','s02_m04_r01')
PAIRS=('s03_m03_r03','s04_m04_r04')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path,value):
    with Path(path).open('x') as f:
        json.dump(value,f,indent=2,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else str(v))
        f.write('\n')


def source_identity():
    manifest=json.loads((UNIT/'provenance/PARENT_SOURCE_LOCK.json').read_text())
    repo=UNIT.parents[1]
    for row in manifest['files']:
        p=repo/row['path']
        if p.stat().st_size != row['bytes'] or digest(p) != row['sha256']:
            raise ValueError('PARENT_SOURCE_CHANGED:'+row['path'])
    runtime_modules=('run_thermal.py','thermal_system.py','thermal_sources.py','recombination_moments.py')
    files=[*(UNIT/'code'/name for name in runtime_modules),
           *sorted((UNIT/'data').glob('*')),
           UNIT/'provenance/MAO_SOURCE_LOCK.json',UNIT/'provenance/PARENT_SOURCE_LOCK.json']
    table={str(p.relative_to(UNIT)):digest(p) for p in files if p.is_file()}
    return hashlib.sha256(json.dumps(table,sort_keys=True).encode()).hexdigest(),table


def one_case(case,closure,refined,out,identity,source_files,campaign_deadline):
    label=case+'_'+closure+('_refined' if refined else '_nominal')
    dest=out/label
    donor=DONOR/'results/pilot_v2/cases'/case
    rec=json.loads((donor/'RESULT.json').read_text())
    parent_receipt_sha=digest(donor/'RESULT.json')
    parent_file=donor/'trajectory.npz'
    parent_sha=digest(parent_file)
    if parent_sha != rec['outputs']['trajectory.npz']['sha256']:
        raise ValueError('DONOR_TRAJECTORY_CHANGED:'+case)
    if (dest/'RESULT.json').exists():
        saved=json.loads((dest/'RESULT.json').read_text())
        if (saved['status']=='COMPLETE' and saved['source_identity']==identity
                and saved['donor_sha256']==parent_sha
                and saved['donor_receipt_sha256']==parent_receipt_sha
                and digest(dest/'trajectory.npz')==saved['trajectory_sha256']):
            return dict(label=label,state='complete_reused',result=saved)
        raise ValueError('EXISTING_RESULT_IDENTITY_MISMATCH:'+label)
    if dest.exists():
        raise FileExistsError('Preserve partial/failed case; choose new output root:'+str(dest))
    dest.mkdir(parents=True)
    start=time.perf_counter(); cpu=time.process_time()
    deadline=min(start+240.,campaign_deadline)
    def check_deadline():
        if time.perf_counter()>deadline:
            raise TimeoutError('cooperative case/campaign wall limit')
    base=dict(label=label,source_identity=identity,source_files=source_files,
              started_utc=datetime.now(timezone.utc).isoformat(),
              donor_sha256=parent_sha,donor=str(parent_file.relative_to(DONOR)),
              donor_receipt_sha256=parent_receipt_sha,
              donor_commit='ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7',
              rr_closure=closure,refined=refined)
    save_json(dest/'STARTED.json',base)
    try:
        with np.load(parent_file,allow_pickle=False) as old:
            index=int(np.argmin(abs(old['z']-8)))
            x=old['x'][index:].copy(); start62=old['raw_state'][index].copy()
            scales=old['isotope_scales'].copy(); initial_Y=old['initial_Y'].copy()
        if np.any(start62[[40,45,46]] != 0):
            raise ValueError('NUCLEAR_ENERGY_OWNER_MISSING: initial n/T')
        y0=np.r_[start62,math.log(thermal_uv(float(x[0]))[0])]
        check_deadline()
        config=dict(rec['config'],_case_wall_seconds=max(.001,deadline-time.perf_counter()))
        model=ThermalSystem(config,closure)
        def diagnostic(xx,yy):
            check_deadline()
            return model.thermal_diagnostics(xx,yy)
        factor=.1 if refined else 1.
        atol=factor*np.r_[np.full(40,2e-11),np.full(21,2e-10),2e-11,2e-10]
        sol=solve_ivp(model.rhs,(float(x[0]),float(x[-1])),y0,method='BDF',jac=model.jac,
                      t_eval=x,rtol=2e-8*factor,atol=atol,max_step=.0125 if refined else .025,
                      dense_output=True)
        if not sol.success or sol.y.shape!=(63,len(x)):
            raise RuntimeError('THERMAL_INTEGRATION_FAILED:'+sol.message)
        Y=sol.y[40:61].T*scales
        T=np.exp(sol.y[62])
        rows=[diagnostic(float(xx),sol.y[:,i]) for i,xx in enumerate(x)]
        names=list(rows[0]); diag=np.array([[r[n] for n in names] for r in rows])
        signed=np.array([model.geometry.normalized(float(xx),sol.y[:40,i]) for i,xx in enumerate(x)])
        inherited=[]; constraints=[]
        for i,xx in enumerate(x):
            check_deadline()
            inherited.append(model.diagnostics(float(xx),sol.y[:,i]))
            field=model.geometry.fields(float(xx),sol.y[:40,i])
            lhs=3*field['H']**2
            rhs=3*model.geometry.source.h0**2*(field['dust_energy_norm']+
                field['massive_energy_norm']+field['rad_energy_norm']+model.geometry.source.omega_lambda)+3*field['s']**2
            constraints.append(abs(lhs-rhs)/lhs)
        inherited_names=[n for n in inherited[0] if n!='signed_observables']
        inherited_diag=np.array([[r[n] for n in inherited_names] for r in inherited])
        angular_min=min(min(r[n] for r in inherited) for n in
            ('min_photon_angular_weight','min_neutrino_angular_weight',
             'min_photon_number_angular_weight','min_neutrino_number_angular_weight'))
        trace_max=max(r['trace_energy_fraction'] for r in inherited)
        isotope_errors={name:float(np.max(abs(Y[:,indices].sum(axis=1)-initial_Y[list(indices)].sum()))/scales[indices[0]])
                        for name,indices in model.atomic.isotope_groups.items()}
        # Independent quadrature of a conserved gas energy, on dense solution
        # samples. No additional ODE is integrated to create the diagnostic.
        integrals={}
        for count in (513,1025):
            gx=np.linspace(x[0],x[-1],count); gy=sol.sol(gx)
            vals=np.array([[d['gas_energy_source_J_per_baryon_per_x'],d['work_J_per_baryon_per_x'],
                            (abs(d['photo_absorbed_W_m3'])+abs(d['total_escape_W_m3']))/(d['nb_m3']*d['H_s'])]
                           for d in (diagnostic(float(xx),gy[:,i]) for i,xx in enumerate(gx))])
            de=rows[-1]['gas_energy_J_per_baryon']-rows[0]['gas_energy_J_per_baryon']
            net=float(simpson(vals[:,0]-vals[:,1],x=gx))
            throughput=float(simpson(vals[:,2]+abs(vals[:,1]),x=gx))
            integrals[str(count)]=dict(delta_energy_J_per_baryon=de,integrated_net_J_per_baryon=net,
                                      throughput_J_per_baryon=throughput,
                                      residual_scaled=abs(de-net)/max(throughput,1e-300))
        energy_grid_delta=abs(integrals['1025']['integrated_net_J_per_baryon']-integrals['513']['integrated_net_J_per_baryon'])/integrals['1025']['throughput_J_per_baryon']
        gates=dict(endpoint=bool(x[-1]==math.log(7)),finite=bool(np.isfinite(sol.y).all() and np.isfinite(diag).all()),
                   temperature_domain=bool(np.all((T>=100)&(T<=1e6))),
                   population_positivity=bool(np.min(sol.y[40:61])>=-2e-8),
                   isotope_conservation=max(isotope_errors.values())<2e-7,
                   baryon_conservation=bool(np.max(abs(Y@model.atomic.A-1))<2e-8),
                   zero_n_T=bool(np.all(Y[:,[0,5,6]]==0)),
                   ne_nonnegative=bool(np.all(diag[:,names.index('ne_m3')]>=0)),
                   monotone_tau=bool(np.min(np.diff(sol.y[61]))>=-2e-10),
                   number_monopoles=bool(max(np.max(abs(sol.y[13]-1)),np.max(abs(sol.y[31]-1)))<2e-9),
                   einstein_constraint=max(constraints)<2e-13,
                   tensor_sum=bool(np.max(abs(signed[:,3]-signed[:,1]-signed[:,2]))<2e-16),
                   finite_angular_positivity=angular_min>-2e-7,
                   trace_energy_small=trace_max<1e-5,
                   source_energy=bool(np.max(diag[:,names.index('source_energy_residual')])<5e-12),
                   integrated_energy=integrals['1025']['residual_scaled']<3e-4,
                   source_unchanged=all(digest(UNIT/p)==sha for p,sha in source_files.items()),
                   donor_unchanged=digest(parent_file)==parent_sha and digest(donor/'RESULT.json')==parent_receipt_sha)
        np.savez_compressed(dest/'trajectory.npz',x=x,z=21*np.exp(-x)-1,raw_state=sol.y.T,Y=Y,
                            T_K=T,diagnostics=diag,diagnostic_names=np.array(names),
                            inherited_diagnostics=inherited_diag,inherited_diagnostic_names=np.array(inherited_names),
                            signed_observables=signed,isotope_scales=scales,initial_Y=initial_Y,
                            initial_state=y0,source_index=index)
        result=dict(base,status='COMPLETE' if all(gates.values()) else 'GATE_FAIL',
                    gates=gates,start_index=index,start_z=float(21*math.exp(-x[0])-1),end_z=float(21*math.exp(-x[-1])-1),
                    samples=len(x),rtol=2e-8*factor,max_step=.0125 if refined else .025,
                    initial_state_sha256=hashlib.sha256(y0.tobytes()).hexdigest(),
                    trajectory_sha256=digest(dest/'trajectory.npz'),
                    trajectory_bytes=(dest/'trajectory.npz').stat().st_size,
                    isotope_errors=isotope_errors,max_baryon_error=float(np.max(abs(Y@model.atomic.A-1))),
                    max_einstein_constraint=max(constraints),min_finite_angular_weight=angular_min,
                    max_trace_energy_fraction=trace_max,
                    min_scaled_population=float(np.min(sol.y[40:61])),temperature_min_K=float(T.min()),
                    temperature_max_K=float(T.max()),temperature_end_K=float(T[-1]),tau_end=float(sol.y[61,-1]),
                    energy_integrals=integrals,energy_grid_delta_scaled=energy_grid_delta,
                    nfev=sol.nfev,njev=sol.njev,nlu=sol.nlu,rhs_calls=model.nrhs,jac_calls=model.njac,
                    solver_message=sol.message,wall_seconds=time.perf_counter()-start,
                    own_cpu_seconds=time.process_time()-cpu,
                    environment=dict(python=sys.version.split()[0],numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform()))
        save_json(dest/'RESULT.json',result)
        if not all(gates.values()):
            raise RuntimeError('FINITE_GATE_FAILED:'+','.join(k for k,v in gates.items() if not v))
        return dict(label=label,state='new_complete',result=result)
    except Exception as exc:
        save_json(dest/'FAILED.json',dict(base,status='FAILED',error=repr(exc),traceback=traceback.format_exc(),
                                      wall_seconds=time.perf_counter()-start,own_cpu_seconds=time.process_time()-cpu))
        raise


def run(output):
    identity,files=source_identity()
    specs=[(case,'mao2017',False) for case in CASES]
    specs += [(case,'mao2017',True) for case in PAIRS]
    specs += [(case,'rate_derivative',False) for case in PAIRS]
    started=time.perf_counter(); outcomes=[]
    output.mkdir(parents=True,exist_ok=True)
    for case,closure,refined in specs:
        if time.perf_counter()-started>1200:
            raise TimeoutError('new finite campaign1200s wall exhausted; preserve completed cases')
        row=one_case(case,closure,refined,output,identity,files,started+1200.)
        outcomes.append(row)
        print(json.dumps({k:row['result'][k] for k in ('label','status','temperature_end_K','wall_seconds')}),flush=True)
    receipt=dict(source_identity=identity,new_integrations=sum(r['state']=='new_complete' for r in outcomes),
                 reused=sum(r['state']=='complete_reused' for r in outcomes),old_IVP_reruns=0,
                 wall_seconds=time.perf_counter()-started,
                 results=[dict(label=r['label'],state=r['state']) for r in outcomes])
    name='CAMPAIGN_'+str(time.time_ns())+'.json'
    save_json(output/name,receipt)
    return receipt


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true')
    ap.add_argument('--output',type=Path,default=UNIT/'results/thermal8')
    args=ap.parse_args()
    if not args.execute:
        print('Planned8 distinct thermal restarts; use --execute. Old126 reruns0.')
    else:
        print(json.dumps(run(args.output),indent=2))

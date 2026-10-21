"""One named, data-only recovery of the first completed trajectory.

The failed JSON report is preserved. No solver, RHS, or Jacobian is called.
Only the JSON serialization helper changed; exact AST equivalence and all
other scientific input hashes are required before migrating this one case.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import time

import numpy as np

from coupled import CoupledSystem,ROOT,atomic_json,SCHEMA
from run_pilot import freeze,case_identity,digest,valid_completion


def main():
    old=ROOT/'results/pilot'
    new=ROOT/'results/pilot_v2'
    contract=json.loads((ROOT/'evidence/OUTPUT_RECOVERY_CONTRACT.json').read_text())
    assert contract['changed_AST_nodes']==['atomic_json']
    before=json.loads((old/'FROZEN.json').read_text())
    after=freeze(ROOT,ROOT/'data/CAMPAIGN.json')
    changed=[k for k in before['files'] if before['files'][k]!=after['files'].get(k)]
    assert changed==['code/coupled.py'],changed
    assert set(before['files'])==set(after['files'])
    assert before['configs']==after['configs']
    cid='s00_m02_r02'
    config=next(c for c in after['configs'] if c['case_id']==cid)
    source=old/'cases'/cid/'trajectory.npz'
    assert (source.parent/'RUNNER_FAILED.json').exists()
    assert not (source.parent/'RESULT.json').exists()
    data=np.load(source,allow_pickle=False)
    x=data['x'];raw=data['raw_state'];Y=data['Y'];obs=data['signed_observables']
    diag=data['diagnostics'];names=data['diagnostic_names'].tolist()
    assert raw.shape==(193,62) and Y.shape==(193,21) and diag.shape[0]==193
    idx={k:i for i,k in enumerate(names)}
    system=CoupledSystem(config)
    expected_initial=system.y0
    assert np.array_equal(raw[0],expected_initial)
    max_diag=0.;constraint=[]
    for j,xx in enumerate(x):
        # Saved-state diagnostics only: no re-integration or RHS evaluation.
        row=system.diagnostics(float(xx),raw[j])
        oo=row.pop('signed_observables')
        actual=np.array([row[k] for k in names])
        max_diag=max(max_diag,float(np.max(abs(actual-diag[j])/(1+abs(diag[j])))))
        assert np.allclose(oo,obs[j],rtol=0,atol=2e-16)
        f=system.geometry.fields(float(xx),raw[j,:40])
        src=system.geometry.source
        lhs=3*f['H']**2
        rhs=3*src.h0**2*(f['dust_energy_norm']+f['massive_energy_norm']+
                        f['rad_energy_norm']+src.omega_lambda)+3*f['s']**2
        constraint.append(float(abs(lhs-rhs)/lhs))
    assert system.nrhs==system.njac==0
    isotope_errors={}
    for name,indices in system.atomic.isotope_groups.items():
        nominal=system.atomic.initial_Y[list(indices)].sum()
        isotope_errors[name]=float(np.max(abs(Y[:,indices].sum(axis=1)-nominal))/system.scale[indices[0]])
    baryon_error=float(np.max(abs(Y@system.atomic.A-1)))
    min_scaled=float(np.min(data['scaled_populations']))
    number_error=float(max(np.max(abs(raw[:,13]-1)),np.max(abs(raw[:,31]-1))))
    target=np.array([config['Sigma_F'],config['P_m_initial_target'],config['P_r_initial_target']])
    axis_error=float(np.max(abs(obs[0,:3]-target)))
    angle_names=['min_photon_angular_weight','min_neutrino_angular_weight',
                 'min_photon_number_angular_weight','min_neutrino_number_angular_weight']
    gates=dict(full_interval_and_samples=bool(x[0]==0 and abs(x[-1]-math.log(7))<1e-15 and len(x)==193),
        initial_physical_axes=axis_error<2e-12,
        finite=bool(np.isfinite(raw).all() and np.isfinite(diag).all()),
        population_positivity=min_scaled>=-2e-8,
        isotope_scaled_conservation=max(isotope_errors.values())<2e-7,
        baryon_conservation=baryon_error<2e-8,
        nonnegative_electrons=bool(np.min(diag[:,idx['ne_m3']])>=0),
        number_monopoles=number_error<2e-9,
        monotone_optical_depth=bool(np.min(np.diff(raw[:,61]))>=-2e-10),
        einstein_constraint=max(constraint)<2e-13,
        tensor_sum=bool(np.max(abs(obs[:,3]-obs[:,1]-obs[:,2]))<2e-16),
        finite_angular_positivity=bool(min(np.min(diag[:,idx[k]]) for k in angle_names)>-2e-7),
        trace_energy_small=bool(np.max(diag[:,idx['trace_energy_fraction']])<1e-5))
    if not all(gates.values()):raise ValueError('saved science gates fail: '+str(gates))
    assert max_diag<2e-14
    old_identity=case_identity(before,config);new_identity=case_identity(after,config)
    directory=new/'cases'/cid
    directory.mkdir(parents=True,exist_ok=False)
    atomic_json(new/'FROZEN.json',after)
    shutil.copyfile(source,directory/'trajectory.npz')
    assert digest(source)==digest(directory/'trajectory.npz')
    outputs={'trajectory.npz':{'bytes':source.stat().st_size,'sha256':digest(source)}}
    recovery=dict(status='DATA_ONLY_RECOVERED',source_case='results/pilot/cases/'+cid,
        original_execution_identity=old_identity,compatible_delivery_identity=new_identity,
        original_source_commit='a949529872eb5ba0e20c7e206fe893e5d544e48c',
        contract='evidence/OUTPUT_RECOVERY_CONTRACT.json',changed_files=changed,
        byte_identical_npz=True,new_ODE_solves=0,rhs_calls=0,jac_calls=0,
        saved_state_diagnostic_evaluations=193,max_scaled_saved_diagnostic_difference=max_diag,
        actual_solver_counters='UNKNOWN_REPORT_SERIALIZATION_FAILED',
        original_failure_preserved=True)
    result=dict(schema=SCHEMA,status='COMPLETE',config=config,
        scientific_identity_sha256=new_identity,execution_identity_sha256=old_identity,
        outputs=outputs,gates=gates,recovery=recovery,
        nfev=None,njev=None,nlu=None,wall_seconds=None,
        samples=193,x_end=float(x[-1]),z_end=float(data['z'][-1]),
        initial_signed_observables=obs[0].tolist(),final_signed_observables=obs[-1].tolist(),
        min_scaled_population=min_scaled,baryon_error=baryon_error,
        initial_axis_error=axis_error,isotope_scaled_errors=isotope_errors,
        number_monopole_error=number_error,max_einstein_constraint=max(constraint),
        max_trace_energy_fraction=float(np.max(diag[:,idx['trace_energy_fraction']])),
        final_tau_T=float(raw[-1,61]),
        physical_scope='same conditional pilot; recovered stored outputs without a new IVP')
    atomic_json(directory/'RECOVERY.json',recovery)
    atomic_json(directory/'RESULT.json',result)
    atomic_json(directory/'COMPLETE.json',dict(identity=new_identity,
        result_sha256=digest(directory/'RESULT.json'),outputs=outputs,
        status='DATA_ONLY_RECOVERY_COMPATIBLE_IO_FIX'))
    assert valid_completion(directory,new_identity)
    atomic_json(ROOT/'evidence/OUTPUT_RECOVERY_RECEIPT.json',recovery)
    print(json.dumps(dict(recovery=recovery,gates=gates),indent=2))

if __name__=='__main__':main()

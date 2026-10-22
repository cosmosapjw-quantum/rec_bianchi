"""Thermal forcing of the126 immutable REC119 saved trajectories.

This entry point never imports an ODE integrator or calls an RHS to advance a
state. It verifies stored byte identities, prepares the193 temperature/rate
nodes once, and evaluates thermal and chemical energy ledgers on saved Y.
Signed external heating is retained: negative Qext means a required external
sink under the selected optically thin retained-process closure.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
DONOR = UNIT.parent/'rec_rei_hheli_sandbox_20261021'
sys.path.insert(0,str(DONOR/'code'))
from atomic_network import AtomicNetwork
from thermal_sources import ThermalSources

KB = 1.380649e-23
EV = 1.602176634e-19
MYR_S = 31557600e6
PARENT_COMMIT = 'ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7'
REPRESENTATIVE = 's03_m03_r03'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json_new(path,value):
    with Path(path).open('x') as stream:
        json.dump(value,stream,indent=2,allow_nan=False)
        stream.write('\n')


def sources():
    paths = [Path(__file__), UNIT/'code/thermal_sources.py',
             UNIT/'code/recombination_moments.py',
             UNIT/'data/mao2017_selected.json', UNIT/'data/mao2017_calc.dat',
             UNIT/'data/mao2017_pars.dat', UNIT/'provenance/MAO_SOURCE_LOCK.json',
             DONOR/'code/atomic_network.py',DONOR/'data/atomic_coefficients.json',
             DONOR/'data/atomic_model.json']
    return [{'path':str(p.relative_to(UNIT.parent)),
             'bytes':p.stat().st_size,'sha256':sha256(p)} for p in paths]


def declared_cases():
    result = []
    for folder,cohort,count in (('pilot_v2','main',125),('control','opacity_control',1)):
        base = DONOR/'results'/folder
        frozen = json.loads((base/'FROZEN.json').read_text())
        configs = frozen['configs']
        if len(configs)!=count:
            raise ValueError('unexpected frozen cohort count')
        ordered = sorted(configs,key=lambda row:row['case_id'])
        for config in ordered:
            case_id = config['case_id']
            path = base/'cases'/case_id
            result.append((path,cohort,case_id))
    if len({(cohort,case_id) for _,cohort,case_id in result})!=126:
        raise ValueError('duplicate cohort identity')
    return result


def load_verified(case_path,cohort,case_id):
    result_path = case_path/'RESULT.json'
    result = json.loads(result_path.read_text())
    complete_path = case_path/'COMPLETE.json'
    complete = json.loads(complete_path.read_text())
    if result['status']!='COMPLETE' or result['config']['case_id']!=case_id:
        raise ValueError('case is not the named completed IVP')
    if sha256(result_path)!=complete['result_sha256']:
        raise ValueError('RESULT hash differs from COMPLETE receipt')
    if result['scientific_identity_sha256']!=complete['identity']:
        raise ValueError('scientific identity mismatch')
    path = case_path/'trajectory.npz'
    declared = result['outputs']['trajectory.npz']
    actual = {'bytes':path.stat().st_size,'sha256':sha256(path)}
    if actual!=declared or actual!=complete['outputs']['trajectory.npz']:
        raise ValueError('trajectory bytes mismatch declared RESULT/COMPLETE')
    if not all(result['gates'].values()):
        raise ValueError('inherited finite gate is not PASS')
    if result['config']['uv_cutoff_eV']!=200.:
        raise ValueError('heterogeneous UV contract in donor cohort')
    with np.load(path,allow_pickle=False) as data:
        arrays = {name:data[name].copy() for name in data.files}
    if arrays['raw_state'].shape!=(193,62) or arrays['Y'].shape!=(193,21):
        raise ValueError('unexpected parent trajectory shape')
    if np.any(arrays['Y'][:,[0,5,6]]!=0):
        raise ValueError('nuclear energy owner missing for nonzero n/T')
    if not np.array_equal(arrays['Y'],arrays['raw_state'][:,40:61]
                           *arrays['isotope_scales'][None,:]):
        raise ValueError('stored native abundance does not match scaled state')
    receipt = dict(cohort=cohort,case_id=case_id,
        path=str(path.relative_to(UNIT.parent)),**actual,
        result_sha256=complete['result_sha256'],complete_sha256=sha256(complete_path),
        scientific_identity_sha256=complete['identity'])
    return arrays,receipt


def prepare_nodes(x,atomic,primary,alternative):
    z = 21*np.exp(-x)-1
    tanh = np.tanh((7-z)/.8)
    uv = .5*(1+tanh)
    temperature = 100+11900*uv
    tdx = 11900*.5*(1-tanh*tanh)*(1+z)/.8
    # Match donor scalar math.tanh evaluation exactly where its low-UV tail
    # is near machine precision; vector libm differences matter there.
    for i,value in enumerate(x):
        zz = 21*math.exp(-float(value))-1
        tt = math.tanh((7-zz)/.8)
        uv[i] = .5*(1+tt)
        temperature[i] = 100+11900*uv[i]
        tdx[i] = 11900*.5*(1-tt*tt)*(1+zz)/.8
    rates = [atomic.rates(float(t),float(q)) for t,q in zip(temperature,uv)]
    coeff_p = [primary.coefficients(float(t)) for t in temperature]
    coeff_a = [alternative.coefficients(float(t)) for t in temperature]
    return dict(x=x,z=z,T=temperature,uv=uv,Tdx=tdx,
        G0=np.stack([r['G0'] for r in rates]),
        Gne=np.stack([r['Gne'] for r in rates]),
        alpha=np.stack([r['rr_m3_s']+r['dr_m3_s'] for r in rates]),
        Lrr_p=np.stack([c['rr_loss_J_m3_s'] for c in coeff_p]),
        Lrr_a=np.stack([c['rr_loss_J_m3_s'] for c in coeff_a]),
        Ldr=np.stack([c['dr_loss_J_m3_s'] for c in coeff_p]))


def integrate_energy_per_baryon(power,H,nb,x):
    integrand = power/(nb*H*EV)
    # This is quadrature of the stored193 nodes, not a continuous-error bound.
    total = float(np.trapezoid(integrand,x=x))
    coarse = float(np.trapezoid(integrand[::2],x=x[::2]))
    return total,coarse


def one_case(data,receipt,prepared,atomic,primary):
    x = prepared['x']
    if not np.array_equal(data['x'],x):
        raise ValueError('saved epoch grids differ')
    index = {str(k):i for i,k in enumerate(data['diagnostic_names'])}
    diagnostics = data['diagnostics']
    get = lambda name: diagnostics[:,index[name]]
    nb,H = get('nb_m3'),get('H')
    if np.any(nb<=0) or np.any(H<=0):
        raise ValueError('invalid baryon density or H')
    T,uv = prepared['T'],prepared['uv']
    if not np.array_equal(T,get('T_K')) or not np.array_equal(uv,get('uv_scale')):
        raise ValueError('prescribed T/UV parent profile mismatch')
    Y = data['Y']
    ne = nb*(Y@atomic.q)
    ne_error = np.max(abs(ne-get('ne_m3'))/np.maximum(abs(ne),1e-300))
    if ne_error>3e-14:
        raise ValueError('stored electron density differs from charge count')
    w = 1+atomic.q
    eta = Y@w
    F = np.einsum('tij,tj->ti',prepared['G0'],Y)
    F += ne[:,None]*np.einsum('tij,tj->ti',prepared['Gne'],Y)
    F += Y@atomic.decay_matrix.T
    particle_rate = F@w
    ion_source = nb*(F@atomic.ionization_energy_J)
    absorption = nb*uv*(Y@atomic._absorbed_W)
    photoheat = nb*uv*(Y@atomic._primary_W)
    core = nb*uv*(Y@atomic._core_W)
    cooling_p = nb*ne*np.sum(Y*prepared['Lrr_p'],axis=1)
    cooling_a = nb*ne*np.sum(Y*prepared['Lrr_a'],axis=1)
    dr = nb*ne*np.sum(Y*prepared['Ldr'],axis=1)
    binding = nb*ne*np.sum(Y*prepared['alpha']
                          *primary.downward_binding_J[None,:],axis=1)
    qkin_p = photoheat-cooling_p-dr
    qkin_a = photoheat-cooling_a-dr
    qrequired = (1.5*KB*nb*eta*H*(prepared['Tdx']+2*T)
                 +1.5*KB*T*nb*particle_rate)
    qext_p = qrequired-qkin_p
    qext_a = qrequired-qkin_a
    escape_p = core+binding+cooling_p+dr
    escape_a = core+binding+cooling_a+dr
    source_denom = abs(absorption)+abs(escape_p)+abs(qkin_p)+abs(ion_source)
    source_error = abs(absorption-escape_p-qkin_p-ion_source)/np.maximum(source_denom,1e-300)
    # Independent pre-existing diagnostic ledger includes the ionization
    # reservoir. It must recover the same external thermal forcing.
    inherited_net = get('net_required_gas_input_W_m3')
    ext_from_old = inherited_net+escape_p-get('photo_absorbed_W_m3')
    ext_from_old_a = inherited_net+escape_a-get('photo_absorbed_W_m3')
    compare_denom = (abs(qrequired)+abs(qkin_p)+abs(inherited_net)
                     +abs(escape_p)+abs(absorption))
    comparison_error = np.maximum(abs(qext_p-ext_from_old),abs(qext_a-ext_from_old_a))
    comparison_error /= np.maximum(compare_denom,1e-300)
    if float(source_error.max())>=5e-12 or float(comparison_error.max())>=5e-12:
        raise ValueError('source/parent energy ledger disagreement')
    rows = dict(elapsed_Myr=get('elapsed_s')/MYR_S,T_K=T,H_s=H,nb_m3=nb,
                ne_m3=ne,Qext_W_m3=qext_p,Qext_rate_derivative_W_m3=qext_a,
                Qrequired_W_m3=qrequired,photo_primary_W_m3=photoheat,
                photo_absorbed_W_m3=absorption,rr_cooling_W_m3=cooling_p,
                rr_cooling_rate_derivative_W_m3=cooling_a,dr_cooling_W_m3=dr,
                core_escape_W_m3=core,total_escape_W_m3=escape_p,
                binding_escape_W_m3=binding,kinetic_net_W_m3=qkin_p,
                ion_source_W_m3=ion_source,source_residual=source_error,
                inherited_ledger_residual=comparison_error)
    if not all(np.all(np.isfinite(a)) for a in rows.values()):
        raise ValueError('nonfinite postprocessing result')
    summary = dict(case_id=receipt['case_id'],cohort=receipt['cohort'],
        Qext_min_W_m3=float(qext_p.min()),Qext_max_W_m3=float(qext_p.max()),
        Qext_negative_saved_nodes=int(np.count_nonzero(qext_p<0)),
        source_residual_max=float(source_error.max()),
        inherited_ledger_residual_max=float(comparison_error.max()),
        electron_reconstruction_rel_error=float(ne_error))
    for name,arr in [('Qext',qext_p),('Qext_rate_derivative',qext_a),
                     ('photo_primary',photoheat),('rr_cooling',cooling_p),
                     ('dr_cooling',dr),('core_escape',core),('Qrequired',qrequired)]:
        fine,coarse = integrate_energy_per_baryon(arr,H,nb,x)
        summary[name+'_eV_per_baryon'] = fine
        summary[name+'_trap193_minus97_eV_per_baryon'] = fine-coarse
    # Positive and negative integrals are explicitly additional sign-resolved
    # diagnostics; the scientific signed Qext array above is never clipped.
    summary['Qext_positive_part_eV_per_baryon'] = integrate_energy_per_baryon(
        np.maximum(qext_p,0.),H,nb,x)[0]
    summary['Qext_negative_part_eV_per_baryon'] = integrate_energy_per_baryon(
        np.minimum(qext_p,0.),H,nb,x)[0]
    return rows,summary


def main():
    start = time.perf_counter()
    output = UNIT/'results/saved126'
    receipt_path = UNIT/'evidence/SAVED126_POSTPROCESS.json'
    current_sources = sources()
    if receipt_path.exists():
        old = json.loads(receipt_path.read_text())
        if old.get('status')!='COMPLETE' or old.get('source_files')!=current_sources:
            raise FileExistsError('existing saved126 evidence has another source identity')
        for row in old['outputs']:
            path = UNIT/row['path']
            if path.stat().st_size!=row['bytes'] or sha256(path)!=row['sha256']:
                raise ValueError('saved postprocessing artifact changed')
        print(json.dumps({'status':'COMPLETE_REUSED','old_IVP_reruns':0,
                          'postprocessing_reexecuted':False}))
        return 0
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('partial saved126 outputs exist; preserve before new run')
    output.mkdir(parents=True,exist_ok=True)
    atomic = AtomicNetwork()
    primary = ThermalSources(atomic,'mao2017')
    alternative = ThermalSources(atomic,'rate_derivative')
    cohorts = declared_cases()
    all_rows,case_summaries,inputs = [],[],[]
    prepared = None
    for path,cohort,case_id in cohorts:
        data,receipt = load_verified(path,cohort,case_id)
        if prepared is None:
            prepared = prepare_nodes(data['x'],atomic,primary,alternative)
        rows,summary = one_case(data,receipt,prepared,atomic,primary)
        all_rows.append(rows)
        case_summaries.append(summary)
        inputs.append(receipt)
    names = list(all_rows[0])
    stacked = {name:np.stack([row[name] for row in all_rows]) for name in names}
    case_ids = [row['case_id'] for row in inputs]
    cohort_names = [row['cohort'] for row in inputs]
    np.savez_compressed(output/'histories.npz',case_ids=np.array(case_ids),
        cohort=np.array(cohort_names),x=prepared['x'],z=prepared['z'],
        field_names=np.array(names),**stacked)
    with (output/'ENDPOINTS.csv').open('x',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=list(case_summaries[0]))
        writer.writeheader();writer.writerows(case_summaries)
    representative_index = case_ids.index(REPRESENTATIVE)
    representative_rows = all_rows[representative_index]
    with (output/'REPRESENTATIVE.csv').open('x',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=['case_id','x','z']+names)
        writer.writeheader()
        for i,(xx,zz) in enumerate(zip(prepared['x'],prepared['z'])):
            writer.writerow(dict(case_id=REPRESENTATIVE,x=float(xx),z=float(zz),
                                 **{name:float(representative_rows[name][i]) for name in names}))
    main_rows = [row for row in case_summaries if row['cohort']=='main']
    control_rows = [row for row in case_summaries if row['cohort']=='opacity_control']
    main_q = stacked['Qext_W_m3'][:125]
    summary = dict(schema='rec.saved126.thermal.budget.v1',status='COMPLETE',
        parent_commit=PARENT_COMMIT,main_case_count=125,opacity_control_count=1,
        samples_per_case=193,main_saved_nodes=125*193,total_saved_nodes=126*193,
        new_IVPs=0,old_IVP_reruns=0,
        precomputation=dict(temperature_nodes=193,rate_matrix_preparations=193,
                            moment_nodes_per_closure=193),
        interpretation='Qext=required thermal input minus primary photoelectron '
                       'heating plus RR/DR kinetic cooling. Negative Qext is a '
                       'required sink, not an invalid population.',
        quadrature='Trapezoid on193 stored x nodes of Q/(nb H); eV per baryon. '
                   '193-minus97 coarsening difference is reported, not a '
                   'continuous-time error certificate.',
        main=dict(Qext_min_W_m3=float(main_q.min()),Qext_max_W_m3=float(main_q.max()),
            negative_saved_nodes=int(np.count_nonzero(main_q<0)),
            net_external_eV_per_baryon_range=[min(r['Qext_eV_per_baryon'] for r in main_rows),
                                              max(r['Qext_eV_per_baryon'] for r in main_rows)],
            net_derivative_closure_eV_per_baryon_range=[min(r['Qext_rate_derivative_eV_per_baryon'] for r in main_rows),
                                                       max(r['Qext_rate_derivative_eV_per_baryon'] for r in main_rows)],
            max_absolute_trap193_minus97_eV_per_baryon=max(abs(r['Qext_trap193_minus97_eV_per_baryon']) for r in main_rows)),
        representative=case_summaries[representative_index],opacity_control=control_rows[0],
        gates=dict(trajectory_declared_hashes=True,complete_result_hashes=True,
            source_energy_residual_below5e12=bool(stacked['source_residual'].max()<5e-12),
            old_diagnostic_ledger_agrees_below5e12=bool(stacked['inherited_ledger_residual'].max()<5e-12),
            nuclear_flux_zero=True,finite=True),
        source_residual_max=float(stacked['source_residual'].max()),
        old_ledger_residual_max=float(stacked['inherited_ledger_residual'].max()),
        physical_scope='Conditional prompt radiative escape, Maxwellian/common T, '
                       'Mao-factor hybrid plus unchanged number rates. Original '
                       'thermal history remains prescribed; no new dynamics.',
        retained_holds=dict(physical='HOLD',production='NOT_APPROVED',
                            global_convergence='NOT_RUN',REI_activation=False))
    write_json_new(output/'SUMMARY.json',summary)
    write_json_new(output/'INPUTS.json',dict(parent_commit=PARENT_COMMIT,files=inputs))
    output_paths = sorted(p for p in output.iterdir() if p.is_file())
    receipt = dict(schema='rec.saved126.thermal.postprocess.receipt.v1',
        status='COMPLETE',parent_commit=PARENT_COMMIT,
        command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 code/postprocess_saved.py',
        source_files=current_sources,source_unchanged_after=current_sources==sources(),
        main_cases=125,control_cases=1,stored_nodes=126*193,new_IVPs=0,old_IVP_reruns=0,
        source_residual_max=summary['source_residual_max'],
        old_ledger_residual_max=summary['old_ledger_residual_max'],
        raw_integrity='126 trajectory byte sizes and SHA256 matched both RESULT '
                      'and COMPLETE; RESULT SHA256 matched COMPLETE. Historical '
                      'failed/recovered duplicate paths were not added as cases.',
        outputs=[dict(path=str(p.relative_to(UNIT)),bytes=p.stat().st_size,sha256=sha256(p))
                 for p in output_paths],
        environment=dict(python=sys.version.split()[0],numpy=np.__version__,platform=platform.platform()),
        wall_s=time.perf_counter()-start)
    write_json_new(receipt_path,receipt)
    print(json.dumps({'status':'COMPLETE','main_cases':125,'control_cases':1,
        'stored_nodes':126*193,'new_IVPs':0,'wall_s':receipt['wall_s'],
        'external_energy_range_eV_per_baryon':summary['main']['net_external_eV_per_baryon_range'],
        'negative_Qext_nodes':summary['main']['negative_saved_nodes'],
        'source_residual_max':summary['source_residual_max'],
        'old_ledger_residual_max':summary['old_ledger_residual_max']}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())

"""Evaluate omitted sources on eight immutable saved trajectories; no ODE.

python code/postprocess_omitted.py --output results/budget_v1
Outputs are create-only. Every coefficient, support mask and quadrature
integrand is retained so later verification requires no trajectory replay.
"""
from __future__ import annotations
import os
for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_name]='1'
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
import time
import numpy as np
import scipy
from scipy.integrate import simpson, cumulative_trapezoid
from scipy.constants import sigma as STEFAN_BOLTZMANN

UNIT=Path(__file__).resolve().parents[1]
THERMAL=UNIT.parent/'rec_thermal_moments_20261022'
DONOR=UNIT.parent/'rec_rei_hheli_sandbox_20261021'
sys.path.insert(0,str(THERMAL/'code'))
from run_thermal import source_identity as thermal_source_identity
from atomic_network import AtomicNetwork
from geometry import cosmology
from coupled import thermal_uv, THOMSON
from collisional_budget import CollisionalBudget
from compton_budget import (hot_electron_power, planck_reference_power,
    dilute_spectrum_power, uv_reference_moments, fixed_path_logT_forcing,
    C_M_S, KB_J_K, EV_J, MEC2_J, SIGMA_T_C_M3_S, A_RAD_J_M3_K4, constants)

EXPECTED_THERMAL_ID='dfd2ca42b7fb768f3e31e5a7cc3ab64a4aa8b422ef0c5b79b8852043b197ff2e'
CASE4=('s00_m02_r02','s03_m03_r03','s04_m04_r04','s02_m04_r01')
PAIR2=('s03_m03_r03','s04_m04_r04')
EXPECTED_LABELS=sorted([c+'_mao2017_nominal' for c in CASE4]+
    [c+'_mao2017_refined' for c in PAIR2]+[c+'_rate_derivative_nominal' for c in PAIR2])
PROCESS_NAMES=('photo_primary','rr_kinetic','dr_kinetic','adiabatic_work',
    'compton_hot_cmb','compton_planck_reference','compton_uv',
    'ci_kinetic','ci_binding','ce_HI','ce_HeII',
    'added_kinetic_primary','added_total_gas_primary')
FORCING_NAMES=('compton_hot_cmb','compton_planck_reference','compton_uv',
    'ci_full','ci_energy_only','ci_particle_only','ce_HI','ce_HeII','added_primary')
COEFFICIENT_NAMES=('CI_HI','CI_HeI','CI_HeII','CE_HI','CE_HeII')


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path,value):
    def conversion(v):
        if isinstance(v,np.ndarray): return v.tolist()
        if isinstance(v,np.generic): return v.item()
        if isinstance(v,Path): return str(v)
        raise TypeError(type(v).__name__)
    with Path(path).open('x') as f:
        json.dump(value,f,indent=2,allow_nan=False,default=conversion)
        f.write('\n')


def runtime_identity():
    files=[UNIT/'code'/n for n in ('postprocess_omitted.py','compton_budget.py','collisional_budget.py')]
    files+=sorted(p for p in (UNIT/'data').rglob('*') if p.is_file())
    table={str(p.relative_to(UNIT)):digest(p) for p in files}
    identity=hashlib.sha256(json.dumps(table,sort_keys=True).encode()).hexdigest()
    return identity,table


def integrate_saved(x,values,valid_nodes=None):
    """Retained-grid integrals and conservative support classification."""
    x=np.asarray(x);v=np.asarray(values)
    if x.ndim!=1 or v.shape!=x.shape or len(x)!=109 or np.any(np.diff(x)<=0):
        raise ValueError('expected109 increasing saved nodes')
    if not np.all(np.isfinite(v)): raise ValueError('nonfinite integrand')
    pieces=.5*(v[:-1]+v[1:])*np.diff(x)
    supported=np.ones(len(x)-1,dtype=bool) if valid_nodes is None else (
        np.asarray(valid_nodes[:-1],dtype=bool)&np.asarray(valid_nodes[1:],dtype=bool))
    trap=float(np.sum(pieces));coarse=float(np.trapezoid(v[::2],x=x[::2]))
    simp=float(simpson(v,x=x))
    return dict(trapezoid_109=trap,trapezoid_55=coarse,simpson_109=simp,
                coarse_minus_primary=coarse-trap,simpson_minus_primary=simp-trap,
                supported_intervals=int(supported.sum()),total_intervals=len(x)-1,
                supported_interval_contribution=float(np.sum(pieces[supported])),
                continuation_or_boundary_contribution=float(np.sum(pieces[~supported])),
                absolute_throughput=float(np.sum(.5*(np.abs(v[:-1])+np.abs(v[1:]))*np.diff(x))))


def _support_for(process,valid):
    if process in ('ci_kinetic','ci_binding','ci_full','ci_energy_only','ci_particle_only'):
        return np.all(valid[:,:3],axis=1)
    if process=='ce_HI': return valid[:,3]
    if process=='ce_HeII': return valid[:,4]
    if process in ('added_kinetic_primary','added_primary'): return np.all(valid,axis=1)
    if process=='added_total_gas_primary': return np.all(valid[:,3:],axis=1)
    return None


def run(output):
    start=time.perf_counter();cpu=time.process_time()
    identity,source_files=runtime_identity()
    old_identity,old_source_files=thermal_source_identity()
    if old_identity!=EXPECTED_THERMAL_ID: raise ValueError('OLD_SOURCE_IDENTITY_CHANGED')
    if not np.isclose(THOMSON,SIGMA_T_C_M3_S,rtol=2e-15,atol=0):
        raise ValueError('THOMSON_OWNER_MISMATCH')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    save_json(output/'STARTED.json',dict(started_utc=datetime.now(timezone.utc).isoformat(),
        source_identity=identity,source_files=source_files,thermal_identity=old_identity,
        command=sys.argv,scope='saved8 fixed-path source budget',new_ODE_integrations=0))
    atomic=AtomicNetwork();collision=CollisionalBudget(atomic)
    cosmo,background=cosmology()
    u_gamma0=(4*STEFAN_BOLTZMANN/C_M_S)*background['Tcmb0_K']**4
    uv_m=uv_reference_moments(atomic.photon_energy_eV,atomic.photon_flux_bins_base,
                            atomic.photon_bin_edges_eV,atomic.uv_config['number_power_index'])
    labels=sorted(p.parent.name for p in (THERMAL/'results/thermal8').glob('*/RESULT.json'))
    if labels!=EXPECTED_LABELS: raise ValueError('SAVED8_INVENTORY_CHANGED')
    inputs=[];summaries={};arrays={};csvrows=[]
    for label in labels:
        case_start=time.perf_counter()
        folder=THERMAL/'results/thermal8'/label
        receipt=json.loads((folder/'RESULT.json').read_text())
        source=folder/'trajectory.npz';sha=digest(source)
        if (receipt['status']!='COMPLETE' or receipt['source_identity']!=old_identity or
                receipt['source_files']!=old_source_files or sha!=receipt['trajectory_sha256'] or
                source.stat().st_size!=receipt['trajectory_bytes']):
            raise ValueError('SAVED8_IDENTITY_CHANGED:'+label)
        inputs.append(dict(label=label,trajectory=str(source.relative_to(THERMAL)),
            bytes=source.stat().st_size,sha256=sha,receipt_sha256=digest(folder/'RESULT.json')))
        with np.load(source,allow_pickle=False) as a:
            x=a['x'].copy();z=a['z'].copy();T=a['T_K'].copy();Y=a['Y'].copy()
            raw=a['raw_state'].copy();diag=a['diagnostics'].copy()
            names=a['diagnostic_names'].tolist();initial=a['initial_Y'].copy()
            scales=a['isotope_scales'].copy()
        if (raw.shape!=(109,63) or Y.shape!=(109,21) or not np.all(np.isfinite(raw)) or
                not np.allclose(Y,raw[:,40:61]*scales,rtol=3e-15,atol=0) or
                not np.allclose(T,np.exp(raw[:,62]),rtol=3e-15,atol=0) or
                np.any(Y<0) or np.any(Y[:,[0,5,6]]!=0)):
            raise ValueError('SAVED_STATE_CONTRACT:'+label)
        d={n:diag[:,i] for i,n in enumerate(names)}
        H=d['H_s'];nb=d['nb_m3'];ne=d['ne_m3'];eta=d['gas_particles_per_baryon']
        aa=cosmo.aref*np.exp(x);Tref=background['Tcmb0_K']/aa
        Ug=u_gamma0*raw[:,4]/aa**4;Uref=A_RAD_J_M3_K4*Tref**4
        n=109;Q=np.zeros((n,len(PROCESS_NAMES)));F=np.zeros((n,len(FORCING_NAMES)))
        coeff=np.zeros((n,5));valid=np.zeros((n,5),dtype=bool);underflow=valid.copy()
        ci_dY=np.zeros((n,21));particle=np.zeros(n);ci_balance=np.zeros(n)
        ci_gradient=np.zeros(n);particle_balance=np.zeros(n)
        uv_scale=np.zeros(n);UVU=np.zeros(n);UVM=np.zeros(n);ci_photo_ratio=np.zeros((n,3))
        for j in range(n):
            r=collision.evaluate(Y[j],float(T[j]),float(nb[j]),allow_extrapolation=True)
            if (not np.isclose(r['ne_m3'],ne[j],rtol=3e-14,atol=1e-30) or
                    not np.isclose((1+atomic.q)@Y[j],eta[j],rtol=3e-14,atol=0)):
                raise ValueError('DENSITY_OWNER_MISMATCH:'+label)
            coeff[j]=[r['coefficients'][key] for key in COEFFICIENT_NAMES]
            valid[j]=[r['validity'][key]['in_validated_domain'] for key in COEFFICIENT_NAMES]
            underflow[j]=[r['validity'][key]['underflow_to_zero'] for key in COEFFICIENT_NAMES]
            ci_dY[j]=r['dY_dt'];particle[j]=r['particle_source']
            ci_gradient[j]=r['ci_binding_gradient_W_m3']
            particle_balance[j]=abs(r['particle_source_residual_s'])/max(abs(particle[j]),1e-300)
            ci_balance[j]=abs(r['ci_gradient_residual_W_m3'])/max(
                abs(r['ci_kinetic_W_m3'])+abs(r['ci_binding_gradient_W_m3']),1e-300)
            uv_scale[j]=thermal_uv(float(x[j]))[1]
            UVU[j]=uv_scale[j]*uv_m['U_J_m3'];UVM[j]=uv_scale[j]*uv_m['M_J2_m3']
            # CE charge-state ownership is explicit and excludes He I metastables.
            ce_hi=nb[j]*ne[j]*float(Y[j,[1,3,5]].sum())*coeff[j,3]
            ce_he=nb[j]*ne[j]*float(Y[j,[8,11]].sum())*coeff[j,4]
            if not np.isclose(ce_hi+ce_he,r['ce_cooling_W_m3'],rtol=3e-14,atol=1e-300):
                raise ValueError('CE_CHANNEL_OWNER_MISMATCH')
            q=dict(photo_primary=d['photo_primary_W_m3'][j],rr_kinetic=-d['rr_cooling_W_m3'][j],
                dr_kinetic=-d['dr_cooling_W_m3'][j],
                adiabatic_work=-nb[j]*H[j]*d['work_J_per_baryon_per_x'][j],
                compton_hot_cmb=hot_electron_power(ne[j],T[j],Ug[j]),
                compton_planck_reference=planck_reference_power(ne[j],T[j],Tref[j]),
                compton_uv=dilute_spectrum_power(ne[j],T[j],UVU[j],UVM[j]),
                ci_kinetic=r['ci_kinetic_W_m3'],ci_binding=r['ci_binding_W_m3'],
                ce_HI=-ce_hi,ce_HeII=-ce_he)
            q['added_kinetic_primary']=sum(q[k] for k in ('compton_hot_cmb','compton_uv','ci_kinetic','ce_HI','ce_HeII'))
            q['added_total_gas_primary']=q['added_kinetic_primary']+q['ci_binding']
            Q[j]=[q[k] for k in PROCESS_NAMES]
            f={k:fixed_path_logT_forcing(q[k],0,H[j],T[j],nb[j],eta[j])
               for k in ('compton_hot_cmb','compton_planck_reference','compton_uv','ce_HI','ce_HeII')}
            f['ci_full']=fixed_path_logT_forcing(q['ci_kinetic'],particle[j],H[j],T[j],nb[j],eta[j])
            f['ci_energy_only']=fixed_path_logT_forcing(q['ci_kinetic'],0,H[j],T[j],nb[j],eta[j])
            f['ci_particle_only']=-particle[j]/(H[j]*eta[j])
            f['added_primary']=sum(f[k] for k in ('compton_hot_cmb','compton_uv','ci_full','ce_HI','ce_HeII'))
            F[j]=[f[k] for k in FORCING_NAMES]
            for k,index in enumerate((1,10,11)):
                photo=uv_scale[j]*atomic._photo_s[index]
                if photo<=0: raise ValueError('CI/photo diagnostic requires positive UV at saved nodes')
                ci_photo_ratio[j,k]=ne[j]*coeff[j,k]/photo
        if np.max(ci_balance)>1e-13: raise ValueError('CI_BINDING_BALANCE_FAILED')
        if np.max(particle_balance)>1e-13: raise ValueError('CI_PARTICLE_BALANCE_FAILED')
        energy_integrands=Q/(nb[:,None]*H[:,None]*EV_J)
        E={p:integrate_saved(x,energy_integrands[:,k],_support_for(p,valid)) for k,p in enumerate(PROCESS_NAMES)}
        D={p:integrate_saved(x,F[:,k],_support_for(p,valid)) for k,p in enumerate(FORCING_NAMES)}
        thermal_energy=1.5*KB_J_K*T*eta/EV_J
        ce_peak=int(np.argmax(-F[:,FORCING_NAMES.index('ce_HI')]))
        comp_peak=int(np.argmax(-F[:,FORCING_NAMES.index('compton_hot_cmb')]))
        summary=dict(label=label,input_trajectory_sha256=sha,saved_nodes=n,
            elapsed_clock='proper Myr since donor z20; not cosmic age or time since restart',
            z_start=float(z[0]),z_end=float(z[-1]),T_min_K=float(T.min()),T_max_K=float(T.max()),
            energy_eV_per_baryon=E,fixed_path_logT_forcing=D,
            source_support={p:dict(valid_nodes=int(valid[:,k].sum()),continuation_nodes=int((~valid[:,k]).sum()),
                underflow_nodes=int(underflow[:,k].sum())) for k,p in enumerate(COEFFICIENT_NAMES)},
            ci_binding_balance_max_scaled=float(ci_balance.max()),
            ci_particle_balance_max_scaled=float(particle_balance.max()),
            max_CI_to_photo_rate_HI_HeI_HeII=ci_photo_ratio.max(axis=0),
            photon_energy_ratio_actual_to_FLRW=dict(min=float(raw[:,4].min()),max=float(raw[:,4].max())),
            max_theta_e=float(np.max(KB_J_K*T/MEC2_J)),
            thermal_energy_endpoint_eV_per_baryon=float(thermal_energy[-1]),
            max_abs_compton_hot_forcing=float(abs(F[:,FORCING_NAMES.index('compton_hot_cmb')]).max()),
            max_abs_ce_HI_forcing=float(abs(F[:,FORCING_NAMES.index('ce_HI')]).max()),
            max_compton_hot_forcing_z=float(z[comp_peak]),max_ce_HI_forcing_z=float(z[ce_peak]),
            wall_seconds=time.perf_counter()-case_start)
        caseout=output/label;caseout.mkdir()
        np.savez_compressed(caseout/'budget.npz',x=x,z=z,T_K=T,Y=Y,H_s=H,nb_m3=nb,ne_m3=ne,eta=eta,
            elapsed_Myr=d['elapsed_Myr'],photon_energy_monopole=raw[:,4],photon_number_monopole=raw[:,13],
            U_gamma_actual_J_m3=Ug,U_gamma_planck_reference_J_m3=Uref,T_planck_reference_K=Tref,
            UV_scale=uv_scale,UV_energy_J_m3=UVU,UV_recoil_moment_J2_m3=UVM,
            process_names=np.array(PROCESS_NAMES),Q_W_m3=Q,energy_integrand_eV_baryon_per_x=energy_integrands,
            energy_cumulative_eV_baryon=cumulative_trapezoid(energy_integrands,x=x,axis=0,initial=0),
            forcing_names=np.array(FORCING_NAMES),fixed_path_logT_forcing_per_x=F,
            fixed_path_logT_forcing_cumulative=cumulative_trapezoid(F,x=x,axis=0,initial=0),
            coefficient_names=np.array(COEFFICIENT_NAMES),coefficients_SI=coeff,
            in_published_accuracy_domain=valid,underflow_to_zero=underflow,
            ci_dY_dt=ci_dY,ci_particle_source_per_baryon_s=particle,ci_balance_scaled=ci_balance,
            ci_binding_gradient_W_m3=ci_gradient,ci_particle_balance_scaled=particle_balance,
            ci_available_mask=r['ci_available_mask'],ci_unavailable_mask=r['ci_unavailable_mask'],
            ce_available_mask=r['ce_available_mask'],ce_unavailable_mask=r['ce_unavailable_mask'],
            ci_photo_ratio_HI_HeI_HeII=ci_photo_ratio,thermal_energy_eV_baryon=thermal_energy)
        save_json(caseout/'SUMMARY.json',summary);summaries[label]=summary
        arrays[label]=dict(E=E,D=D,Q=Q,F=F)
        for p in PROCESS_NAMES:
            csvrows.append(dict(label=label,process=p,**E[p]))
    save_json(output/'INPUTS.json',dict(thermal_source_identity=old_identity,
        thermal_source_files=old_source_files,trajectories=inputs,old_IVP_reruns=0,new_ODE_integrations=0))
    with (output/'ENERGY_BUDGETS.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    pairs={}
    for case in PAIR2:
        base=case+'_mao2017_nominal'
        for typ,other in (('refinement',case+'_mao2017_refined'),('RR_trajectory_alternative',case+'_rate_derivative_nominal')):
            pairs[case+'_'+typ]=dict(base=base,other=other,
                energy_delta_eV_per_baryon={p:arrays[other]['E'][p]['trapezoid_109']-arrays[base]['E'][p]['trapezoid_109'] for p in PROCESS_NAMES},
                forcing_integral_delta={p:arrays[other]['D'][p]['trapezoid_109']-arrays[base]['D'][p]['trapezoid_109'] for p in FORCING_NAMES},
                max_abs_forcing_difference={p:float(np.max(abs(arrays[other]['F'][:,k]-arrays[base]['F'][:,k]))) for k,p in enumerate(FORCING_NAMES)})
    final_identity,final_files=runtime_identity()
    if final_identity!=identity or final_files!=source_files: raise ValueError('POSTPROCESS_SOURCE_CHANGED_DURING_RUN')
    for row in inputs:
        if digest(THERMAL/row['trajectory'])!=row['sha256']: raise ValueError('INPUT_MUTATED_DURING_RUN')
    final=dict(status='COMPLETE_SCOPED_FIXED_PATH_BUDGET',source_identity=identity,source_files=source_files,
        thermal_source_identity=old_identity,constants=constants(),UV_reference=uv_m,
        distinct_saved_trajectories=8,saved_states=872,new_ODE_integrations=0,old_IVP_reruns=0,
        cases=summaries,pair_comparisons=pairs,
        model_scope=dict(CMB='hot thermal term on actual energy monopole; full recoil/induced term unresolved',
            Planck='separate isotropic Planck reference; not reconstructed actual spectrum',
            UV='inherited5–200eV bins; dilute first-order Thomson/nonrelativistic exchange',
            CI='HG97 H/He with native isotope equality, inherited binding owner, continuation flagged',
            CE='HG97 H I/He II prompt radiative escape; no He I metastable or Li CE',
            forcing='direct fixed-path RHS integral, not solved temperature response'),
        physical='HOLD',production='NOT_APPROVED',global_convergence='NOT_RUN',REI_activation=False,
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
            platform=platform.platform(),numerical_threads=1),
        wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,
        max_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    save_json(output/'SUMMARY.json',final)
    files={str(p.relative_to(output)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(output.rglob('*')) if p.is_file()}
    save_json(output/'RESULT.json',dict(status='COMPLETE',source_identity=identity,files=files,
        finished_utc=datetime.now(timezone.utc).isoformat(),new_ODE_integrations=0,old_IVP_reruns=0))
    print(json.dumps(dict(status=final['status'],output=str(output),source_identity=identity,
        saved_states=872,wall_seconds=final['wall_seconds'],new_ODE_integrations=0),indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=UNIT/'results/budget_v1')
    args=ap.parse_args();run(args.output)

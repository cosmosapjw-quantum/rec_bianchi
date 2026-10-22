"""Independent v2 plot-array/CSV bindings; no renderer or model calls."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
from scipy.integrate import simpson, cumulative_trapezoid

U=Path(__file__).resolve().parents[2]
F=U/'figures/v2'; A=U/'results/analysis_v1'; R=U/'results/compton8'
SEEDS=('s03_m03_r03','s04_m04_r04')
EV=1.602176634e-19

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
    with np.load(p,allow_pickle=False) as a:return {k:a[k].copy() for k in a.files}
def diag(a):return {k:a['diagnostics'][:,j] for j,k in enumerate(a['diagnostic_names'])}
def metrics(a,b):
    y=a['raw_state']-b['raw_state'];s=a['signed_observables'][:,1:]-b['signed_observables'][:,1:]
    return np.array([abs(y[:,62]).max(),abs(y[:,40:61]).max(),abs(y[:,61]).max(),abs(s).max()])

def main():
    manifest=json.loads((F/'FIGURE_MANIFEST.json').read_text())
    assert manifest['plotter_sha256']==sha(U/'code/plot_compton.py')
    assert manifest['runtime_identity']=='c89f576e2c7f15a0a1d0d3f96ce72de516245cbb83b5d4fbaeede342a76e86ac'
    assert manifest['source_identity']=='f824bdead1ce75b94f5102764184ea8dee2db71ecc06296dc7fa2ac9d71708c3'
    for p,row in manifest['inputs'].items():
        assert Path(p).stat().st_size==row['bytes'] and sha(p)==row['sha256']
    for p,row in manifest['outputs'].items():
        assert (F/p).stat().st_size==row['bytes'] and sha(F/p)==row['sha256']
    data=load(F/'plot_data.npz');summary=json.loads((A/'SUMMARY.json').read_text());expected={};tables={}
    tables['01_temperature_curves.csv']=[];tables['02_energy_budget.csv']=[];tables['02_gas_balance_curves.csv']=[];tables['02_gas_balance_endpoints.csv']=[];tables['03_branch_vs_refinement.csv']=[]
    modeled=('photo_primary','rr_kinetic','dr_kinetic','compton_selected','compton_uv','expansion_work')
    omitted=('ci_kinetic','ci_binding','ce_HI','ce_HeII')
    maxima=[];balance_delta=0.
    for seed in SEEDS:
        label=seed+'_actual_hot_refined'
        h=load(A/label/'comparison_and_source_data.npz');p=load(A/(seed+'_planck_reference_refined')/'comparison_and_source_data.npz')
        vals=dict(x=h['x'],z=h['z'],baseline_T_K=h['baseline_T_K'],actual_hot_T_K=h['T_K'],planck_reference_T_K=p['T_K'],actual_hot_delta_percent=100*(h['T_K']/h['baseline_T_K']-1),planck_reference_delta_percent=100*(p['T_K']/h['baseline_T_K']-1))
        for k,v in vals.items():expected['temperature_'+seed+'_'+k]=v
        for j in range(len(h['x'])):tables['01_temperature_curves.csv'].append(dict(seed=seed,**{k:float(v[j]) for k,v in vals.items()}))
        cs=summary['cases'][label]
        mv=np.array([cs['energy_eV_per_baryon'][k] for k in modeled]);expected['energy_'+seed+'_modeled_names']=np.array(modeled);expected['energy_'+seed+'_modeled_Simpson1025_eV_baryon']=mv
        for k,v in zip(modeled,mv):tables['02_energy_budget.csv'].append(dict(seed=seed,owner='included in actual_hot RHS',process=k,component='total',rule='Simpson1025',energy_eV_baryon=float(v)))
        support=np.array([cs['collisions']['energy_eV_per_baryon'][k]['supported_interval_contribution'] for k in omitted]);cont=np.array([cs['collisions']['energy_eV_per_baryon'][k]['continuation_or_boundary_contribution'] for k in omitted])
        collision=load(A/label/'collisions/collisions_dense_1025.npz')
        for k,v in dict(names=np.array(omitted),supported=support,continuation=cont,total=support+cont,support_mask=collision['in_published_accuracy_domain'],coefficient_names=collision['coefficient_names']).items():expected['collision_'+seed+'_'+k]=v
        for j,k in enumerate(omitted):
            for comp,vec in (('supported_intervals',support),('continuation_or_boundary',cont)):
                tables['02_energy_budget.csv'].append(dict(seed=seed,owner='omitted diagnostic; not actual CI/CE exchange',process=k,component=comp,rule='positive-weight trapezoid1025',energy_eV_baryon=float(vec[j])))
        for n in (513,1025):
            a=load(R/label/f'dense_{n}.npz');d=diag(a);x=a['x'];delta=d['gas_energy_J_per_baryon']-d['gas_energy_J_per_baryon'][0]
            # Rebuild the cumulative numerator and final normalization from
            # diagnostic source/work terms, rather than copying plotter output.
            net=d['gas_energy_source_J_per_baryon_per_x']-d['work_J_per_baryon_per_x']
            through=(abs(d['photo_absorbed_W_m3'])+abs(d['total_escape_W_m3'])+abs(d['compton_selected_W_m3'])+abs(d['compton_uv_W_m3']))/(d['nb_m3']*d['H_s'])+abs(d['work_J_per_baryon_per_x'])
            cumulative=cumulative_trapezoid(net,x=x,initial=0);normal=float(simpson(through,x=x));ni=float(simpson(net,x=x));res=(delta-cumulative)/normal;end=float((delta[-1]-ni)/normal)
            for k,v in dict(x=x,z=a['z'],delta_energy_eV_baryon=delta/EV,cumulative_net_eV_baryon=cumulative/EV,residual_scaled=res,endpoint_Simpson_residual_scaled=np.array(end)).items():expected[f'balance_{seed}_{n}_'+k]=v
            tables['02_gas_balance_endpoints.csv'].append(dict(seed=seed,nodes=n,normalization='Simpson absolute throughput on same grid',signed_Simpson_residual_scaled=end,absolute_Simpson_residual_scaled=abs(end),endpoint_delta_energy_eV_baryon=float(delta[-1]/EV),endpoint_net_input_Simpson_eV_baryon=ni/EV,absolute_throughput_Simpson_eV_baryon=normal/EV))
            for j in range(len(x)):tables['02_gas_balance_curves.csv'].append(dict(seed=seed,nodes=n,x=float(x[j]),z=float(a['z'][j]),delta_energy_eV_baryon=float(delta[j]/EV),cumulative_net_trapezoid_eV_baryon=float(cumulative[j]/EV),signed_residual_over_final_throughput=float(res[j])))
        states=[load(R/(seed+'_'+br+'_'+tol)/'trajectory.npz') for br,tol in [('actual_hot','nominal'),('actual_hot','refined'),('planck_reference','nominal'),('planck_reference','refined')]]
        hn,hr,pn,pr=states;v=np.column_stack([metrics(hr,pr),metrics(hn,hr),metrics(pn,pr),metrics(hn,hr)+metrics(pn,pr)]);maxima.append(v)
        for j,name in enumerate(('lnT','conditional_fraction','tau','signed_stress_only')):
            tables['03_branch_vs_refinement.csv'].append(dict(seed=seed,metric=name,refined_branch_difference=float(v[j,0]),actual_hot_nominal_refined_change=float(v[j,1]),planck_nominal_refined_change=float(v[j,2]),sum_of_observed_refinement_changes=float(v[j,3]),branch_exceeds_sum=bool(v[j,0]>v[j,3]),scope='maxima on 109 saved comparison nodes; finite observed changes, not rigorous error bounds'))
    expected.update(comparison_seeds=np.array(SEEDS),comparison_metrics=np.array(['lnT','conditional_fraction','tau','signed_stress_only']),comparison_series=np.array(['refined_branch_difference','actual_hot_refinement','planck_reference_refinement','sum_refinements']),comparison_maxima=np.array(maxima))
    assert set(data)==set(expected) and len(data)==58
    for k,v in expected.items():
        assert data[k].shape==v.shape,k
        if v.dtype.kind in 'USb':assert np.array_equal(data[k],v),k
        elif k.startswith('balance_') and ('residual' in k):
            err=float(np.max(abs(data[k]-v)));balance_delta=max(balance_delta,err);assert err<2e-14,(k,err)
        else:assert np.allclose(data[k],v,rtol=5e-13,atol=1e-15),k
    counts={}
    for name,rows in tables.items():
        actual=list(csv.DictReader((F/name).open(newline='')));assert len(actual)==len(rows),name;counts[name]=len(rows)
        for got,want in zip(actual,rows):
            assert set(got)==set(want),name
            for k,v in want.items():
                if isinstance(v,(str,bool)):assert got[k]==str(v),(name,k)
                elif 'residual' in k:assert abs(float(got[k])-v)<2e-14,(name,k)
                else:assert np.isclose(float(got[k]),v,rtol=5e-13,atol=1e-15),(name,k)
    print(json.dumps(dict(status='PASS_FIGURE_DATA_BINDINGS',manifest_sha256=sha(F/'FIGURE_MANIFEST.json'),plotter_sha256=manifest['plotter_sha256'],input_files_checked=len(manifest['inputs']),output_files_checked=len(manifest['outputs']),npz_arrays_checked=len(data),csv_rows_checked=counts,max_absolute_independent_balance_roundoff=balance_delta,new_ODE_runs=0,render_runs=0,visual_check='Actual v2 PNGs separately inspected at original resolution by this independent reviewer; no data or layout blocker observed.'),indent=2))

if __name__=='__main__':main()

"""Finite source-owned input admission. No integrator, native runtime or solve."""
from __future__ import annotations
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key]='1'
import argparse,ast,csv,hashlib,json,math,sys
from pathlib import Path
import numpy as np

EPS=np.finfo(float).eps
ROOT=Path(__file__).resolve().parent
KB_NATIVE=8.617343e-5
E21,E31,E41=10.198714553953742,12.087365397278509,12.748393192442178

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def json_write(path,obj):
    with Path(path).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def native_routing(energies):
    """Independent literal loops from fplus_from_fminus, not its Python adapter."""
    ans=[]
    for j in range(311):
        if j==139:source,es=311,E21
        elif j==270:source,es=312,E31
        elif j==310:source,es=313,E41
        else:source,es=j+1,float(energies[j+1])
        ans.append((j,source,float(energies[j]),es))
    ans.extend([(311,140,E21,float(energies[140])),(312,271,E31,float(energies[271]))])
    return ans

def classify_cell(eta,eta0,h,n_available):
    """Strict native data domain; an absent retained sample is never thermalized."""
    if n_available<2:return {'status':'INSUFFICIENT_PREFIX','k':None,'alpha':None}
    if eta<eta0:return {'status':'BEFORE_RETAINED_PREFIX','k':None,'alpha':None}
    if eta>=eta0+h*(n_available-1):return {'status':'AT_OR_AFTER_STRICT_ENDPOINT','k':None,'alpha':None}
    p=(eta-eta0)/h;k=math.floor(p);a=p-k
    if k<0 or k+1>=n_available:raise ValueError('ROUNDING_CELL_OUT_OF_RANGE')
    return {'status':'COVERED_RETAINED_CELL','k':k,'alpha':a}

def source_defaults(path):
    tree=ast.parse(Path(path).read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='HyRec2012Cosmology')
    return {n.target.id:ast.literal_eval(n.value) for n in cls.body if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name)}

def load_snapshot(path):
    meta={};energy={}
    with Path(path).open() as f:
        for r in csv.reader(f):
            if r and r[0]=='META':meta[r[1]]=float(r[2])
            elif r and r[0]=='VIRTUAL':energy[int(r[1])]=float(r[2])
    if sorted(energy)!=list(range(311)):raise ValueError('TARGET_ENERGY_SCHEMA')
    return meta,np.array([energy[j] for j in range(311)])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inputs',default='inputs/INPUTS.json');parser.add_argument('--output',default='results/primary001')
    args=parser.parse_args(); manifest=json.loads((ROOT/args.inputs).read_text())
    out=ROOT/args.output;out.mkdir(parents=True,exist_ok=False)
    checks=[]
    check_stream=(out/'checks.jsonl').open('x')
    raw_stream=(out/'candidate_queries.jsonl').open('x')
    def ck(name,passed,**info):
        row=dict(id=name,passed=bool(passed),**info);checks.append(row)
        check_stream.write(json.dumps(row,allow_nan=False)+'\n');check_stream.flush()
        if not passed:raise AssertionError(json.dumps(row))
    for item in manifest['support_files']:
        path=ROOT/item['local_path'];ck('source_identity:'+item['local_path'],sha(path)==item['sha256'])
    meta,energies=load_snapshot(ROOT/manifest['snapshot'])
    table=np.loadtxt(ROOT/manifest['energy_table'])
    ck('native_energy_grid_byte_equivalence_in_binary64',np.array_equal(energies,table[:,0]),maximum_absolute_difference=float(np.max(np.abs(energies-table[:,0]))))
    params=source_defaults(ROOT/manifest['cosmology_source'])
    fixture_tokens=(ROOT/manifest['canonical_input']).read_text().split()
    fixture=dict(zip(['T0_K','omega_b_h2','omega_m_h2','omega_k_h2','omega_de_h2','w0','wa','YHe','N_eff','fsR','meR'],map(float,fixture_tokens)))
    zt=meta['z'];etat=-math.log1p(zt)
    t0=meta['TR_eV_rescaled']*meta['fsR']**2*meta['meR']/(KB_NATIVE*(1+zt))
    nh0=meta['nH_cm3']*1e6/(1+zt)**3
    target_nh_fixture=11.223846333047*fixture['omega_b_h2']*(1-fixture['YHe'])
    candidate_nh=11.223846333047*params['omega_b_h2']*(1-params['YHe'])
    ck('target_T0_matches_native_fixture',abs(t0-fixture['T0_K'])<=64*EPS*max(1,abs(t0)),implied_K=t0)
    ck('target_nH0_matches_native_fixture',abs(nh0-target_nh_fixture)<=64*EPS*max(1,abs(nh0)),implied_per_m3=nh0)
    physical=dict(target_implied_T0_K=t0,target_implied_nH0_m3=nh0,target_fixture=fixture,candidate_parameters=params,
        candidate_nH0_m3=candidate_nh,T0_relative_difference=(params['T0_K']-t0)/t0,nH0_relative_difference=(candidate_nh-nh0)/nh0,
        classification='PHYSICAL_PARAMETER_MISMATCH',error_calibration_admitted=False)
    ck('cosmology_mismatch_detected',params['T0_K']!=t0 and abs(candidate_nh-nh0)>64*EPS)
    routes=native_routing(energies);ck('313_source_owned_routes',len(routes)==313)
    queries=[]
    for dest,source,et,es in routes:
        zsp1=(1+zt)*es/et
        queries.append(dict(target=dest,source=source,target_E_eV=et,source_E_eV=es,z_source=zsp1-1,eta_source=-math.log(zsp1)))
    json_write(out/'queries.json',queries)
    all_rows=[];candidates=[];values={}
    for spec in manifest['histories']:
        path=ROOT/spec['local_path'];ck('input_sha:'+spec['id'],sha(path)==spec['sha256'])
        with np.load(path,allow_pickle=False) as data:
            v=data['virtual_out'];ly=data['lyman_out'];states=[json.loads(s) for s in data['states_json']];steps=[json.loads(s) for s in data['steps_json']]
            n=v.shape[1];h=spec['h'];g0=spec['global_photon_origin']
            ck('shape:'+spec['id'],v.shape==(311,spec['columns']) and ly.shape==(3,spec['columns']))
            ck('finite_outgoing:'+spec['id'],np.isfinite(v).all() and np.isfinite(ly).all())
            ck('state_step_count:'+spec['id'],len(states)==len(steps)+1)
            ck('clock_mapping:'+spec['id'],all(s['photon_col']==s['input_iz']-g0 and s['output_iz']==s['input_iz']+1 for s in steps))
            ck('step_sequence:'+spec['id'],all(s['input_iz']==states[j]['iz'] and s['output_iz']==states[j+1]['iz'] for j,s in enumerate(steps)))
            ck('last_photon_before_last_state:'+spec['id'],states[-1]['iz']==g0+n and steps[-1]['photon_col']==n-1)
            clock_errors=[abs(s['z']-(8001*math.exp(-h*s['iz'])-1))/max(1,abs(s['z'])) for s in states]
            ck('state_clock_roundoff:'+spec['id'],max(clock_errors)<=64*EPS,maximum_scaled_error=max(clock_errors))
            if 'dlna' in data:ck('embedded_h:'+spec['id'],float(data['dlna'])==h)
            if 'source_zip_sha256' in data:ck('embedded_source:'+spec['id'],str(data['source_zip_sha256'])==manifest['source_zip_sha256'])
            if 'rei_activation' in data:ck('activation_false:'+spec['id'],not bool(data['rei_activation']))
            z0=8001*math.exp(-h*g0)-1;eta0=-math.log1p(z0)
            knots=eta0+h*np.arange(n);ncausal=int(np.searchsorted(knots,etat,side='left'));nknown=min(n,ncausal)
            counts={};one_values={}
            for q in queries:
                cell=classify_cell(q['eta_source'],eta0,h,nknown)
                row=dict(candidate=spec['id'],**q,**cell)
                if cell['k'] is not None:
                    k=cell['k'];alpha=cell['alpha'];arr=v[q['source']] if q['source']<311 else ly[q['source']-311]
                    left,right=float(arr[k]),float(arr[k+1]);val=(1-alpha)*left+alpha*right
                    ck('strict_causal_bracket:'+spec['id']+':'+str(q['target']),float(knots[k+1])<etat)
                    row.update(left_value=left,right_value=right,interpolated_departure=val,eta_left=float(knots[k]),eta_right=float(knots[k+1]),global_left=g0+k,global_right=g0+k+1)
                    one_values[q['target']]=val
                row.update(physical_reference_admitted=False,error_upper_bound=None)
                counts[cell['status']]=counts.get(cell['status'],0)+1;all_rows.append(row)
                raw_stream.write(json.dumps(row,allow_nan=False)+'\n');raw_stream.flush()
            values[spec['id']]=one_values
            candidates.append(dict(id=spec['id'],sha256=spec['sha256'],columns=n,h=h,global_origin=g0,last_photon_global=g0+n-1,last_state_global=states[-1]['iz'],
                eta0=eta0,eta0_additive=-math.log(8001)+g0*h,eta_last=float(knots[-1]),
                z_first=z0,z_last=math.expm1(-float(knots[-1])),face_causal_columns=nknown,
                coverage_counts=counts,data_identity='PASS',source_code_and_energy_grid='MATCHED',physical_domain='PARAMETER_MISMATCH',
                endpoint_error=None,curvature_upper_bound=None,independent_reference_uncertainty=None,error_calibration='NOT_ADMITTED',
                producer_gate=spec['producer_gate']))
    raw_stream.close();check_stream.close()
    shared=sorted(set(values['h2_u4']) & set(values['h4_r3q_event']))
    comparisons=[dict(target=j,h2=values['h2_u4'][j],h4=values['h4_r3q_event'][j],absolute_discrepancy=abs(values['h2_u4'][j]-values['h4_r3q_event'][j]),status='RAW_DISCREPANCY_NOT_ERROR_BOUND') for j in shared]
    summary=dict(unit='REC-HISTORY-ADM01',selected_stage='R1_R2_INPUT_ADMISSION_WITH_FINITE_SUPPORT',
        result='SOURCE_DOMAIN_RESOLVED_PHYSICAL_ERROR_ADMISSION_HELD',face=dict(z=zt,eta=etat),
        query_count=len(queries),candidate_query_count=len(all_rows),query_z_min=min(q['z_source'] for q in queries),query_z_max=max(q['z_source'] for q in queries),
        candidates=candidates,physical_domain=physical,shared_h2_u4_h4_queries=len(shared),cross_grid_comparisons=comparisons,
        h5_actual_history_calibration='INPUT_DEPENDENT_UNCALIBRATED',parent_REC_HISTORY='PARTIAL',
        new_IVP=0,native_runtime=0,dense_solves=0,old_campaign_replay=0,old_boundary_replay=0,checks_passed=len(checks),checks_failed=0)
    json_write(out/'checks.json',checks);json_write(out/'SUMMARY.json',summary)
    print(json.dumps({k:summary[k] for k in ['result','query_count','candidate_query_count','query_z_min','query_z_max','checks_passed','shared_h2_u4_h4_queries']},indent=2))

if __name__=='__main__':main()

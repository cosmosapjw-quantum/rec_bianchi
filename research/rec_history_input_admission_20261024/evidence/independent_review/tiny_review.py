"""Three finite independent checks; no primary replay, integrator or native call."""
import json, math, hashlib, os
from pathlib import Path
import numpy as np

U=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent
summary=json.loads((U/'results/primary001/SUMMARY.json').read_text())
rows=[json.loads(x) for x in (U/'results/primary001/candidate_queries.jsonl').read_text().splitlines()]
manifest=json.loads((U/'inputs/INPUTS.json').read_text())
results=[]

# P1: saved evidence shape, null uncertainty, and independent interval endpoints.
counts={}
for r in rows:
    counts.setdefault(r['candidate'],{}).setdefault(r['status'],0)
    counts[r['candidate']][r['status']]+=1
assert len(rows)==1252
assert all(r['error_upper_bound'] is None and r['physical_reference_admitted'] is False for r in rows)
intervals=[]
for c in summary['candidates']:
    origin=-math.log(8001)+c['global_origin']*c['h']
    assert abs(origin-c['eta0']) < 2e-15
    assert c['last_state_global']==c['last_photon_global']+1
    assert c['coverage_counts']==counts[c['id']]
    intervals.append({'candidate':c['id'],'eta_first':origin,'eta_last_photon':origin+(c['columns']-1)*c['h'],'last_state_is_not_photon':True})
results.append({'probe':'P1_saved_evidence_and_interval_endpoints','passed':True,'counts':counts,'intervals':intervals,'all_error_bounds_null':True})

# P2: three selected rows only, independently derived interpolation and causal cap.
chosen=[min((r for r in rows if r['candidate']=='h2_u5'),key=lambda r:r['eta_source']),
        max((r for r in rows if r['candidate']=='h2_u5'),key=lambda r:r['eta_source']),
        next(r for r in rows if r['candidate']=='h2_u5' and r['target']==139)]
spec=next(c for c in manifest['histories'] if c['id']=='h2_u5')
h=spec['h']; g0=spec['global_photon_origin']; eta0=-math.log(8001)+g0*h
face=summary['face']['eta']; causal=math.ceil((face-eta0)/h)
assert causal==10277
checked=[]
with np.load(U/spec['local_path'],allow_pickle=False) as a:
    v=a['virtual_out']; ly=a['lyman_out']
    for r in chosen:
        z=(1+summary['face']['z'])*r['source_E_eV']/r['target_E_eV']-1
        eta=-math.log1p(z)
        q=(eta-eta0)/h; k=math.floor(q); alpha=q-k
        arr=v[r['source']] if r['source']<311 else ly[r['source']-311]
        value=(1-alpha)*float(arr[k])+alpha*float(arr[k+1])
        assert k==r['k'] and abs(alpha-r['alpha'])<5e-11
        assert eta0+(k+1)*h<face and k+1<causal
        assert float(arr[k])==r['left_value'] and float(arr[k+1])==r['right_value']
        assert abs(value-r['interpolated_departure'])<=max(1e-290,abs(value)*1e-11)
        checked.append({'target':r['target'],'source':r['source'],'k':k,'alpha':alpha,'value':value,'strict_past_margin':face-(eta0+(k+1)*h)})
    states=[json.loads(str(x)) for x in a['states_json']]
results.append({'probe':'P2_three_selected_U5_cells','passed':True,'face_causal_columns':causal,'selected_rows':checked})

# P3: actual U5 event/state gives T0 without assuming dataclass defaults.
receipt=json.loads((U/'provenance/U5_ORIGINAL_VERIFICATION.json').read_text())
event=receipt['python_result']['event']
s=next(x for x in states if x['iz']==event['input_iz'])
inferred_T0=s['Tm_K']/((1+s['z'])*(1-event['delta']))
assert abs(inferred_T0-2.7255)<2e-14
assert abs(inferred_T0-summary['physical_domain']['target_implied_T0_K'])>0.0024
results.append({'probe':'P3_actual_U5_event_T0','passed':True,'input_iz':s['iz'],'state_Tm_K':s['Tm_K'],'state_z':s['z'],'recorded_delta':event['delta'],'inferred_T0_K':inferred_T0,'target_T0_K':summary['physical_domain']['target_implied_T0_K'],'nH0_from_this_probe':'NOT_IDENTIFIED','interpretation':'Actual U5 temperature mismatch established; full default parameter tuple is a distinct provenance obligation.'})

report={'probe_count':3,'probes':results,'old_primary_replay':0,'new_IVP':0,'native_runtime':0,'full313_query_recomputation':0,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'threads':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']}}
(out/'PROBE_RESULTS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps(report,indent=2,allow_nan=False))

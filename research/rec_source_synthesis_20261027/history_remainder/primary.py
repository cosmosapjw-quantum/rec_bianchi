"""One bounded constructive verification pass on the original fixed history."""
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from controls import run_controls
from remainder import PiecewiseLinear

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
HISTORY = RESEARCH/'rec_history_geometry_response_20261026/inputs/history.npz'
CONTEXT = RESEARCH/'program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json'
LOCKS = [(HISTORY,35239470,'d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1'),
         (CONTEXT,220122,'5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8'),
         (HERE.parent/'CODING_CONTRACT.md',8546,'7dd2e930cad8bf919a9dbbf90a0426f76ea00eaf6eabf16f3d677b8726d1364e')]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(value):
    if isinstance(value,F):
        return {'exact':str(value),'display':float(value)}
    if isinstance(value,dict):
        return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):
        return [encode(v) for v in value]
    return value


def save_json(path, value):
    path.write_text(json.dumps(encode(value), indent=2, sort_keys=True, allow_nan=False)+'\n')


def save_csv(path, rows):
    flat=[]
    for row in rows:
        item={}
        for key,value in row.items():
            if isinstance(value,F):
                item[key+'_exact']=str(value)
                item[key+'_display']=float(value)
            elif isinstance(value,(list,tuple,dict)):
                item[key]=json.dumps(encode(value),sort_keys=True,separators=(',',':'))
            else:
                item[key]=value
        flat.append(item)
    fields=list(dict.fromkeys(k for row in flat for k in row))
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader();writer.writerows(flat)


def exact_hex(value):
    return F(float.fromhex(value))


def bind_and_run(out):
    identities=[]
    for path,size,digest in LOCKS:
        data=path.read_bytes()
        actual=hashlib.sha256(data).hexdigest()
        require(len(data)==size and actual==digest,'IMMUTABLE_SOURCE_MISMATCH:'+str(path))
        identities.append(dict(path=str(path),bytes=size,sha256=actual,relation='BYTE_IDENTITY'))
    context=json.loads(CONTEXT.read_text())
    meta=context['source_identity'];queries=context['queries']
    require(context['schema']=='REC_H5_FIXED_QUERY_CONTEXT_V1','CONTEXT_SCHEMA')
    require(context['clock']=='eta=ln(a)' and context['history_channel_unit']=='dimensionless_occupation_departure','CLOCK_OR_UNIT')
    require(context['native_reference']=='original_HyRec_native_Wien_departure_fixed_source_T0','NATIVE_REFERENCE')
    require(meta['repository']=='cosmosapjw-quantum/rec_bianchi' and meta['prefix']==5127 and meta['query_count']==313,'SOURCE_METADATA')
    require(meta['history_sha256']==LOCKS[0][2] and meta['history_bytes']==LOCKS[0][1],'CONTEXT_HISTORY_IDENTITY')
    require(meta['active_endpoint_slots']==626 and meta['fsR']==1 and meta['meR']==1,'ORIGINAL_METADATA')
    require(len(queries)==meta['query_count'] and sorted(r['source_index'] for r in queries)==list(range(1,314)),'SOURCE_PERMUTATION')
    with np.load(HISTORY,allow_pickle=False) as archive:
        eta=archive['eta'];h=F(float(archive['dlna']));prefix=meta['prefix']
        virtual=archive['outgoing_virtual'];lyman=archive['outgoing_lyman']
        require(virtual.shape==(311,len(eta)) and lyman.shape==(3,len(eta)),'SOURCE_CHANNEL_SHAPES')
        require(np.array_equal(archive['source_indices'],np.arange(len(eta))),'ORIGINAL_TIME_INDICES')
        require(eta.dtype==np.dtype('float64') and virtual.dtype==np.dtype('float64') and lyman.dtype==np.dtype('float64'),'BINARY64_INPUT')
        require(h>0 and len(eta)>=prefix and np.all(np.isfinite(eta[:prefix])),'GRID_METADATA')
        require([float(eta[0]).hex(),float(eta[prefix-1]).hex()]==context['eta_prefix_domain_hex'],'STORED_DOMAIN_WITNESS')
        archive_metadata={key:archive[key].tolist() for key in ['schema','completeness','z_start','source_hash_keys','source_hash_values']}
        t0=F(float(eta[0]));knots=tuple(t0+k*h for k in range(prefix))
        clock=[dict(k=k,stored_eta=F(float(eta[k])),native_real_knot=knots[k],
                    stored_minus_native_real=F(float(eta[k]))-knots[k]) for k in range(prefix)]
        rows=[];chords=[];bindings=[];skips=[]
        for j,witness in enumerate(queries):
            require(witness['incoming_index']==j,'INCOMING_ORDER')
            source=witness['source_index'];cell=witness['cell'];q=exact_hex(witness['query_hex'])
            array=virtual[source] if source<virtual.shape[0] else lyman[source-virtual.shape[0]]
            p=PiecewiseLinear(knots,lambda k:F(float(array[k])),sample_count=prefix)
            require(p.cell(q)==cell,'EXACT_NATIVE_GRID_CELL_MISMATCH:'+str(j))
            require(knots[cell]<q<knots[cell+1],'QUERY_NOT_STRICT_CELL_INTERIOR')
            for key,value in [('eta_left_hex',eta[cell]),('eta_right_hex',eta[cell+1]),
                              ('sample_left_hex',array[cell]),('sample_right_hex',array[cell+1])]:
                require(float(value).hex()==witness[key],'FROZEN_WITNESS_MISMATCH:'+key+':'+str(j))
            left_stored,right_stored=F(float(eta[cell])),F(float(eta[cell+1]))
            geometric_alpha=(q-left_stored)/(right_stored-left_stored)
            require(geometric_alpha==F(witness['geometric_alpha_exact']),'GEOMETRIC_ALPHA_WITNESS')
            geometric=(1-geometric_alpha)*p.sample(cell)+geometric_alpha*p.sample(cell+1)
            nominal=exact_hex(witness['nominal_incoming_hex']);native=p.value(q)
            require(abs(nominal-geometric)==F(witness['anchor_representation_radius_exact']),'OLD_ANCHOR_WITNESS')
            require((q-left_stored)*(right_stored-q)/2==F(witness['pointwise_curvature_coefficient_exact']),'OLD_CURVATURE_COEFFICIENT_WITNESS')
            binding=dict(incoming_index=j,source_index=source,cell=cell,query=q,
                         source_channel='outgoing_virtual' if source<311 else 'outgoing_lyman',
                         channel_row=source if source<311 else source-311,native_real_value=native,
                         frozen_rounded_native_alpha_hex=witness['native_alpha_hex'],
                         stored_nominal=nominal,stored_geometric_value=geometric,
                         nominal_minus_native_real=nominal-native,native_real_anchor_radius=abs(nominal-native),
                         nominal_minus_stored_geometric=nominal-geometric,
                         preserved_stored_geometric_anchor_radius=abs(nominal-geometric),
                         native_real_minus_stored_geometric=native-geometric,
                         left_clock_difference=left_stored-knots[cell],right_clock_difference=right_stored-knots[cell+1])
            bindings.append(binding)
            targets=[('within_left',(q+knots[cell])/2),('within_right',(q+knots[cell+1])/2)]
            adjacent={}
            for side,k in [('left',cell-1),('right',cell+1)]:
                if 0<=k<len(knots)-1:
                    target=(knots[k]+knots[k+1])/2
                    targets.append(('cross_'+side,target));adjacent[side]=target
                else:
                    skips.append(dict(incoming_index=j,source_index=source,cell=cell,case='cross_'+side,status='SKIP_CAUSAL_PREFIX'))
                    adjacent[side]=(q+knots[cell if side=='left' else cell+1])/2
            for label,target in targets:
                result=p.retime(q,target)
                require(result['direct']==result['signed'],'RETIME_EXACT_EQUALITY:'+str(j)+':'+label)
                require(abs(result['direct'])<=result['bound'],'RETIME_BOUND:'+str(j)+':'+label)
                require(not label.startswith('within') or result['direct']==0,'WITHIN_CELL_ZERO')
                rows.append(dict(incoming_index=j,source_index=source,cell=cell,case=label,status='PASS',
                                 query=q,target=target,**result,
                                 dropped_jump_mutation='DETECTED' if result['direct']!=0 else 'NOT_APPLICABLE_ZERO_REMAINDER',
                                 cancellation_ratio=None if result['bound']==0 else abs(result['direct'])/result['bound']))
            a,b=adjacent['left'],adjacent['right'];result=p.chord(a,q,b)
            require(result['direct']==result['signed'],'CHORD_PEANO_EXACT_EQUALITY:'+str(j))
            require(abs(result['direct'])<=result['bound'],'CHORD_BOUND:'+str(j))
            chords.append(dict(incoming_index=j,source_index=source,cell=cell,a=a,query=q,b=b,
                               left_fallback=(cell==0),right_fallback=(cell==len(knots)-2),status='PASS',**result,
                               cancellation_ratio=None if result['bound']==0 else abs(result['direct'])/result['bound']))
    for name,data in [('retimings',rows),('chords',chords),('bindings',bindings),('clock_differences',clock),('skips',skips)]:
        save_json(out/(name+'.json'),data);save_csv(out/(name+'.csv'),data)
    counts={label:sum(r['case']==label for r in rows) for label in sorted({r['case'] for r in rows})}
    summary=dict(schema='REC_NATIVE_REAL_REMAINDER_V1',status='PASS',
                 interpretation='Exact represented native-real history identities; distinct from rounded native C and stored-geometric reconstruction.',
                 source_order=['outgoing_virtual','outgoing_lyman'],source_identities=identities,
                 original_context_metadata={k:v for k,v in context.items() if k!='queries'},archive_metadata=archive_metadata,
                 native_source_reference='research/rec_history_thermo_20261024/vendor/hydrogen.c::interp_Dfnu lines633–652',
                 query_count=len(bindings),verified_exact_grid_cells=len(bindings),prefix=prefix,
                 grid=dict(eta0=t0,dlna=h,final_excluded_endpoint=knots[-1]),
                 executed_retimings=len(rows),retiming_counts=counts,executed_chords=len(chords),skipped_retimings=len(skips),
                 max_abs_retiming_remainder=max(abs(r['direct']) for r in rows),
                 max_retiming_absolute_jump_bound=max(r['bound'] for r in rows),
                 max_abs_chord_remainder=max(abs(r['direct']) for r in chords),
                 max_chord_absolute_jump_bound=max(r['bound'] for r in chords),
                 actual_dropped_jump_mutations_detected=sum(r['direct']!=0 for r in rows),
                 zero_actual_crossing_remainders=sum(r['case'].startswith('cross') and r['direct']==0 for r in rows),
                 max_abs_clock_difference=max(abs(r['stored_minus_native_real']) for r in clock),
                 max_native_real_anchor_radius=max(r['native_real_anchor_radius'] for r in bindings),
                 max_preserved_geometric_anchor_radius=max(r['preserved_stored_geometric_anchor_radius'] for r in bindings),
                 physical_epsilon=None,physical_bound_coverage='0/313',physical_bound_query_count=0,
                 global_physical_completion=None,L4_ready=False,REI_activation=False,
                 historical_operators='Context only; no native, RHS, IVP, Ks, GEO roots or matvecs executed.')
    save_json(out/'summary.json',summary)
    print(json.dumps(encode(summary),sort_keys=True,allow_nan=False))


def main():
    out=HERE/'results'/'primary001'
    out.mkdir(parents=True,exist_ok=False)
    controls=run_controls()
    save_json(out/'controls.json',controls)
    print('TARGETED_CONTROLS_PASS',len(controls),flush=True)
    bind_and_run(out)


if __name__=='__main__':
    main()

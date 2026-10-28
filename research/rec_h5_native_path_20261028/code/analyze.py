"""Saved native capture only: finite parity, event joins, exact affine paths."""
import csv
from fractions import Fraction
import json
from pathlib import Path
import struct
import sys
from common import (UNIT,REPO,EPS,PHYSICAL,check,dump,sha,verify_locks,read_jsonl,
    f64,exact,rational,validate_index,validate_phase,ordered_calls,final_writers,
    required_writer,validate_route,affine,recurrence,density_units)

def compare_scalar(new,old,label):
    n,o=exact(new),exact(old);difference=abs(n-o);scale=max(abs(n),abs(o))
    check(difference<=512*EPS*scale if scale else difference==0,'SOURCE_PARITY:'+label)
    return {'label':label,'new_hex':f64(new).hex(),'old_hex':f64(old).hex(),
            'absolute_difference':rational(difference),'relative_difference':rational(difference/scale) if scale else '0/1'}

def initializer(row,nodes):
    n=row['next_global'];indices=row['source_global_indices']
    check(indices==[n-1,n-2,n-3,n-4],'INITIALIZATION_INDEX_MISMATCH')
    for k,i in enumerate(indices,1):
        if i in nodes:
            field='Tm_K' if row['component']=='Tm_K' else 'xe'
            check(exact(row['x_n_minus'+str(k)])==exact(nodes[i][field]),'INITIALIZATION_SAMPLE_MISMATCH')
    residuals={}
    for memory,left,right,sub in [('prev',1,3,'subtract_prev'),('prev2',2,4,'subtract_prev2')]:
        x,y,h,subtract,observed=(exact(row[k]) for k in ('x_n_minus'+str(left),'x_n_minus'+str(right),'h',sub,memory))
        value=(x-y)/2/h-subtract
        gross=abs(observed)+(abs(x)+abs(y))/2/abs(h)+abs(subtract)
        residual=observed-value
        check(abs(residual)<=64*EPS*gross if gross else residual==0,'INITIALIZATION_ROUNDING')
        residuals[memory]={'residual':rational(residual),'gross':rational(gross)}
    return {'component':row['component'],'next_global':n,'classification':'SOURCE_SECANT_INITIALIZATION_NOT_RHS','memories':residuals}

def array_parity(raw,old,output):
    import numpy as np
    summaries={};total_failures=0
    with (output/'ALL_NONBITWISE_POSITIONS.jsonl').open('x') as log:
        for name in ('outgoing_virtual','outgoing_lyman','average_virtual'):
            a,b=raw[name],old[name]
            check(a.shape==b.shape,'SOURCE_ARRAY_SHAPE:'+name)
            check(np.all(np.isfinite(a)) and np.all(np.isfinite(b)),'NONFINITE_SOURCE_ARRAY:'+name)
            bit=(a.view(np.uint64)==b.view(np.uint64))
            d=np.abs(a-b);scale=np.maximum(np.abs(a),np.abs(b));rel=np.divide(d,scale,out=np.zeros_like(d),where=scale!=0)
            changed=np.argwhere(~bit);fails=0
            for channel,slot in changed:
                n,o=Fraction.from_float(float(a[channel,slot])),Fraction.from_float(float(b[channel,slot]))
                delta=abs(n-o);gross=max(abs(n),abs(o));passed=delta<=512*EPS*gross if gross else delta==0
                if not passed:fails+=1
                log.write(json.dumps({'field':name,'channel':int(channel),'slot':int(slot),
                    'new':float(a[channel,slot]).hex(),'old':float(b[channel,slot]).hex(),
                    'abs_difference':rational(delta),'relative_difference':rational(delta/gross) if gross else '0/1',
                    'within_512eps':passed},sort_keys=True)+'\n')
            summaries[name]={'shape':list(a.shape),'elements':int(a.size),'bitwise_equal':int(np.sum(bit)),
                'nonbitwise_count':int(len(changed)),'max_absolute_difference':float(np.max(d)),
                'max_relative_difference':float(np.max(rel)),'failed_positions':fails}
            total_failures+=fails
    dump(output/'SOURCE_PARITY.json',{'status':'PASS' if not total_failures else 'FAIL','epsilon_exact':'1/'+str(2**52),
        'factor':512,'arrays':summaries,'all_nonbitwise_records':'ALL_NONBITWISE_POSITIONS.jsonl'})
    check(total_failures==0,'RETAINED_PHOTON_PARITY_FAILURE')
    return summaries

def run(output):
    import numpy as np
    locks=verify_locks();deps=locks['retained_dependencies'];capture=UNIT/'results/capture001/raw'
    params=json.loads((capture/'PARAMETERS.json').read_text())
    complete=json.loads((capture/'CAPTURE_SUMMARY.json').read_text())
    check(complete['complete_native_program'] and complete['global_calls']<=200000 and complete['detailed_calls']<=40000,'INCOMPLETE_CAPTURE')
    context=json.loads((REPO/deps['source_context']['path']).read_text())
    reference=json.loads((REPO/deps['prior_reference_packet']['path']).read_text())
    check(len(context['queries'])==len(reference['reference_bounds'])==313,'313_RETAINED_ROWS')
    check(exact(params['T0_K'])==exact(context['source_identity']['T0_K_hex']),'T0_IDENTITY')
    check(params['fsR']==params['meR']==1 and exact(params['h'])==Fraction.from_float(8.49e-5),'NATIVE_PARAMETERS')
    nodes=read_jsonl(capture/'COMMITTED.jsonl');calls=read_jsonl(capture/'CALLS.jsonl');writes=read_jsonl(capture/'WRITES.jsonl')
    recs=read_jsonl(capture/'RECURRENCE.jsonl');seeds=read_jsonl(capture/'INITIALIZATION.jsonl')
    ordered_calls(calls);ordered_calls(writes);byid={c['id']:c for c in calls}
    for c in calls:
        validate_index(c['global'],c['slot'],params['izH0']);validate_phase(c['phase'])
        for key in ('z','xe','xHII','nH_cm3','H_s_inv','TM_eV','TR_eV','dxHII_deta'):f64(c[key])
        check(exact(c['fsR'])==exact(c['meR'])==1,'CALL_MODEL_CONSTANT_IDENTITY')
    check(len(calls)==complete['detailed_calls'],'DETAILED_CALL_COUNT')
    check(len(writes)==complete['full_write_events'],'FULL_WRITE_COUNT')
    node_map={};global_nodes={}
    for row in nodes:
        validate_index(row['global'],row['local'],params['izH0']);validate_phase(row['phase'])
        check(row['local'] not in node_map,'DUPLICATE_COMMITTED_NODE')
        f64(row['xe']);f64(row['Tm_K']);node_map[row['local']]=row;global_nodes[row['global']]=row
    check(all(i in node_map for i in range(-4,7489)),'COMMITTED_WINDOW_MISSING')
    writers=final_writers(writes,calls)
    stored_writers=json.loads((capture/'LAST_WRITERS.json').read_text())
    for i in range(7489):check(stored_writers[i]==(writers[i]['id'] if i in writers else 0),'LAST_WRITER_TABLE_MISMATCH')
    dtype='<f8' if params['little_endian'] else '>f8'
    raw={}
    for key,channels in [('outgoing_virtual',311),('average_virtual',311),('outgoing_lyman',3)]:
        data=np.fromfile(capture/(key+'.f64'),dtype=dtype)
        check(data.size==channels*7489,'RAW_PREFIX_SHAPE:'+key)
        raw[key]=data.reshape(channels,7489)
    energy=np.fromfile(capture/'energy_eV.f64',dtype=dtype)
    with np.load(REPO/deps['history_npz']['path'],allow_pickle=False) as old:
        check(np.array_equal(energy,old['energy_eV']),'ENERGY_IDENTITY')
        parity=array_parity(raw,old,output)
    selected={5127}
    for r in context['queries']:selected.update([r['cell'],r['cell']+1])
    qss=read_jsonl(capture/'QSS_WRITES.jsonl');qmap={}
    for q in qss:
        check(q['slot'] in selected,'UNSELECTED_QSS_EXPORT')
        check(q['id'] in byid and q['slot']==byid[q['id']]['slot'],'QSS_CALL_JOIN')
        check(q['id'] not in qmap,'DUPLICATE_QSS_CALL')
        for field,count in [('real',2),('virtual',311),('incoming_virtual',311),('incoming_lyman',2),('outgoing_virtual',311),('outgoing_lyman',3),('average_virtual',311)]:
            check(len(q[field])==count,'QSS_SHAPE:'+field)
            for x in q[field]:f64(x)
        qmap[q['id']]=q
    selected_writes=[w for w in writes if w['slot'] in selected]
    check({w['id'] for w in selected_writes}==set(qmap),'EVERY_SELECTED_WRITE_QSS')
    check([w['id'] for w in selected_writes]==[q['id'] for q in qss],'SELECTED_QSS_EVENT_ORDER')
    for i in selected:
        w=required_writer(writers,i);q=qmap[w['id']]
        for field in ('outgoing_virtual','outgoing_lyman','average_virtual'):
            observed=np.array([f64(x) for x in q[field]],dtype=np.float64)
            check(np.array_equal(observed.view(np.uint64),raw[field][:,i].astype(np.float64).view(np.uint64)),'QSS_FINAL_ARRAY_JOIN')
    target=required_writer(writers,5127);tc=byid[target['id']];tq=qmap[target['id']]
    meta={};virtual={};real={}
    with (REPO/deps['target_native_csv']['path']).open(newline='') as f:
        for r in csv.reader(f):
            if r[0]=='META':meta[r[1]]=r[2]
            elif r[0]=='VIRTUAL':virtual[int(r[1])]=r
            elif r[0]=='REAL':real[int(r[1])]=r
    check(int(meta['iz_local'])==5127,'TARGET_INDEX')
    target_checks=[]
    for field,csvkey in [('z','z'),('xe','xe'),('xHII','xHII'),('nH_cm3','nH_cm3'),('H_s_inv','H_sInv'),('dxHII_deta','dxHIIdlna')]:
        target_checks.append(compare_scalar(tc[field],float(meta[csvkey]),field))
    for field,csvkey in [('coefficient_TM_eV','TM_eV_rescaled'),('coefficient_TR_eV','TR_eV_rescaled')]:
        target_checks.append(compare_scalar(target[field],float(meta[csvkey]),field))
    for i,r in virtual.items():
        check(Fraction.from_float(float(r[2]))==Fraction.from_float(float(energy[i])),'TARGET_ENERGY_IDENTITY')
        for field,k in [('incoming_virtual',3),('average_virtual',4),('outgoing_virtual',5),('virtual',8)]:
            target_checks.append(compare_scalar(tq[field][i],float(r[k]),field+':'+str(i)))
    for i,r in real.items():target_checks.append(compare_scalar(tq['real'][i],float(r[2]),'real:'+str(i)))
    for i,key in enumerate(('Dfminus_Lya','Dfminus_Lyb','Dfminus_Lyg')):
        target_checks.append(compare_scalar(tq['outgoing_lyman'][i],float(meta[key]),key))
    dump(output/'TARGET_PARITY.json',{'status':'PASS','target_local':5127,'last_writer_call_id':target['id'],'checks':target_checks,
        'temperature_view':'Actual FULL coefficient temperatures; dispatcher values separately retained'})
    recurrence_results=[]
    for r in recs:
        validate_phase(r['phase']);validate_index(r['global_in'],r['local_in'],params['izH0'])
        result=recurrence(r)
        if r['call_id']:
            check(r['call_id'] in byid and byid[r['call_id']]['slot']==r['local_in'],'RECURRENCE_CALL_JOIN')
            check(exact(r['current'])==exact(byid[r['call_id']]['dxHII_deta']) if r['component']!='Tm_K' else True,'ACTUAL_RHS_OPERAND_JOIN')
        recurrence_results.append({**r,**result})
    init_results=[initializer(r,global_nodes) for r in seeds]
    dump(output/'RECURRENCE_DIAGNOSTICS.json',{'classification':'DISCRETE_ARITHMETIC_NOT_ODE_DEFECT','records':recurrence_results,'initialization':init_results})
    rows=[];writer_fields=('xe','xHII','TM_eV','TR_eV','H_s_inv','nH_cm3')
    committed_fields=('xe','Tm_K','xH1s','xHII','xHeII')
    for original,ref in zip(context['queries'],reference['reference_bounds']):
        validate_route(original,ref['binding'])
        k=original['cell'];check(k in node_map and k+1 in node_map,'H5_COMMITTED_ENDPOINT')
        a,b,q=(exact(original[key]) for key in ('eta_left_hex','eta_right_hex','query_hex'))
        alpha=Fraction(original['geometric_alpha_exact']);views={};endpoint_ids=[]
        for slot in (k,k+1):endpoint_ids.append(required_writer(writers,slot)['id'])
        for view,fields in [('writer',writer_fields),('committed',committed_fields)]:
            fields_out={}
            for field in fields:
                l,r=(byid[endpoint_ids[0]],byid[endpoint_ids[1]]) if view=='writer' else (node_map[k],node_map[k+1])
                if l.get(field) is None or r.get(field) is None:
                    fields_out[field]=None;continue
                fields_out[field]=affine(a,b,q,exact(l[field]),exact(r[field]),alpha)
            views[view]=fields_out
        rows.append({'binding':original,'endpoint_local_indices':[k,k+1],
            'endpoint_global_indices':[node_map[k]['global'],node_map[k+1]['global']],
            'final_writer_ids':endpoint_ids,'committed_nodes':[node_map[k],node_map[k+1]],
            'final_writer_calls':[byid[x] for x in endpoint_ids],
            'final_writer_coefficient_temperatures':[writers[k],writers[k+1]],
            'fields':views,'clock':'unchanged stored H5 geometric endpoint/query; native z retained separately',
            'geometric_alpha_exact':rational(alpha)})
    packet={'schema':'REC_H5_NATIVE_EXACT_AFFINE_PATH_V1','unit_id':'REC-H5-NATIVE-PATH01','queries':rows,
        'query_count':313,'endpoint_references':626,'unique_selected_times':len(selected),
        'source_context_sha256':deps['source_context']['sha256'],'prior_reference_sha256':deps['prior_reference_packet']['sha256'],
        'common_field_view':'actual dispatcher input at final FULL writer; coefficient TM/TR separately labelled',
        'QSS_vector_semantics':'native real/virtual departures, not absolute populations; real[0]=2s,real[1]=2p; virtual=x1s*Dfnu',
        'physical_coverage':'0/313',**PHYSICAL,'H6':'OPEN','H7':'OPEN','L4':False,'REI_activation':False}
    dump(output/'EXACT_AFFINE_PATH_PACKET.json',packet)
    plot_nodes=[];T0=f64(params['T0_K']);kN=float(8.617343e-5)
    for i,n in sorted(node_map.items()):
        w=writers.get(i);c=byid[w['id']] if w else None
        plot_nodes.append({'local':i,'xe':f64(n['xe']),'Tm_ratio':f64(n['Tm_K'])/(T0*(1+f64(n['z']))),
            'phase':n['phase'],'writer_id':w['id'] if w else None,'writer_role':c['site'] if c else None,
            'writer_xe_delta':f64(c['xe'])-f64(n['xe']) if c else None,
            'writer_Tm_delta':f64(c['TM_eV'])/kN-f64(n['Tm_K']) if c else None})
    plot_recur=[{'component':r['component'],'local_in':r['local_in'],'rho':r['rho'],'gross':r.get('gross'),'normalized':r.get('normalized')} for r in recurrence_results if r['integrated']]
    dump(output/'PLOT_DATA.json',{'nodes':plot_nodes,'queries':[{'incoming_index':r['binding']['incoming_index'],'fields':r['fields']} for r in rows],
        'recurrences':plot_recur,'physical_coverage':'0/313','units':{'Tm_ratio':'dimensionless','writer_xe_delta':'dimensionless',
        'writer_Tm_delta':'K','rho':'native component units','normalized':'abs(rho)/gross'},
        'temperature_delta_note':'dispatcher TM_eV divided by native kN only for descriptive plot, not an actual native argument'})
    domains={}
    for field in writer_fields:
        vals=[(exact(c[field]),c['slot'],c['id']) for c in calls]
        low=min(vals);high=max(vals)
        domains[field]={'minimum':rational(low[0]),'minimum_slot':low[1],'minimum_call':low[2],
                       'maximum':rational(high[0]),'maximum_slot':high[1],'maximum_call':high[2]}
    normalization=[Fraction(r['normalized']) for r in recurrence_results if r['integrated']]
    summary={'status':'PASS','native_calls_global':complete['global_calls'],'native_calls_detailed':len(calls),
        'full_write_events':len(writes),'committed_rows':len(nodes),'retained_photon_rows':7489,
        'query_rows':313,'endpoint_references':626,'selected_time_slots':len(selected),'selected_qss_records':len(qss),
        'recurrence_records':len(recs),'integrated_recurrence_records':len(normalization),
        'post_saha_records':sum(not r['integrated'] for r in recs),'initializer_records':len(seeds),
        'max_abs_rho_over_gross':rational(max(normalization,default=Fraction(0))),
        'recurrence_limit_exact':rational(64*EPS),'source_parity':parity,'target_checks':len(target_checks),
        'domains':domains,'physical_coverage':'0/313',**PHYSICAL,'H6':'OPEN','H7':'OPEN','L4':False,'REI_activation':False}
    dump(output/'SUMMARY.json',summary)
    return summary

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    print(json.dumps(run(args.output),sort_keys=True))

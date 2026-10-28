"""Worker invoked only by the bounded public stage entry after authorization."""
from pathlib import Path
import copy
import json
import math
import os
import shutil
import subprocess
import sys
import traceback
from runtime import ROOT,P_KEYS,PointAPI,bind_inputs,check,check_bound_identity,dump,load,number,read_parts,require_point,result_record,sha,verify_inputs,write_parts

def active_result(stage):
    state=load(ROOT/'execution/STAGE_STATUS.json')
    check(state.get(stage,{}).get('pass') is True,'PRIOR_STAGE_NOT_PASS:'+stage)
    return load(state[stage]['result'])

def build(outdir):
    from generate_observed import generate
    builddir=outdir/'build';generate(ROOT,builddir)
    compiler=shutil.which('gcc');check(compiler is not None,'GCC_NOT_FOUND')
    version=subprocess.run([compiler,'--version'],capture_output=True,text=True,check=True).stdout
    library=builddir/'libelectron_field.so'
    args=[compiler,'-std=c11','-D_DEFAULT_SOURCE','-O3','-Wall','-Wextra','-Wpedantic','-fno-fast-math','-ffp-contract=off','-fPIC','-shared',
          '-I'+str(ROOT/'inputs/original/HyRec'),'-I'+str(ROOT/'code'),str(ROOT/'inputs/original/HyRec/hyrectools.c'),
          str(builddir/'hydrogen_observed.c'),str(ROOT/'code/electron_field.c'),'-lm','-o',str(library)]
    dump(builddir/'BUILD_COMMAND.json',{'argv':args,'cwd':str(ROOT),'compiler_version':version})
    with (builddir/'compiler.stdout.txt').open('xb') as stdout,(builddir/'compiler.stderr.txt').open('xb') as stderr:
        result=subprocess.run(args,cwd=ROOT,stdout=stdout,stderr=stderr)
    check(result.returncode==0,'COMPILER_FAILED')
    receipt={'library':str(library),'library_sha256':sha(library),'compiler_path':compiler,'compiler_version':version,'argv':args,
             'generated_source_sha256':sha(builddir/'hydrogen_observed.c'),'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'code').iterdir()) if p.suffix in ('.py','.c','.h')},
             'native_table_initializations':0,'native_kernel_calls':0}
    dump(builddir/'BUILD_RECEIPT.json',receipt)
    active=ROOT/'build';active.mkdir(exist_ok=True)
    temporary=active/'ACTIVE_BUILD.tmp'
    temporary.write_text(json.dumps({'receipt':str(builddir/'BUILD_RECEIPT.json')}))
    temporary.replace(active/'ACTIVE_BUILD.json')
    return receipt

def c6(outdir):
    checks=verify_inputs();compiled=build(outdir)
    points,binding=bind_inputs(outdir/'binding')
    invalid=[];valid=[]
    base=points[0]
    with PointAPI(outdir/'CALL_JOURNAL.jsonl') as api:
        tests=[('units',{'units':'SI_K'}),('coefficient_origin',{'temperature_origin':'coefficient'}),
               ('phase',{'phase':'H_HE'}),('model',{'model':2}),('helium',{'helium_neutral':0}),('source',{'source_sha256':'0'*64})]
        original=[number(base['call'][k]) for k in P_KEYS]
        for name,index,value in [('species',0,original[0]*.9),('fsR',6,2.),('meR',7,2.),('Hzero',3,0.),('nHzero',2,0.),('TMzero',4,0.),('TRzero',5,0.),('xHIIone',1,1.),('negative_xe',0,-1.),('ratio',4,original[5]*2.),('TRtable',5,.001),('nonfinite',4,float('nan'))]:
            values=original.copy();values[index]=value;tests.append((name,{'p':values}))
        tests.extend([('incoming_shape',{'incoming':[]}),('lyman_shape',{'lyman':[]}),('scalar_shape',{'p':original[:-1]}),
                      ('incoming_nonfinite',{'incoming':[float('inf')]+[0.]*310})])
        for name,args in tests:
            result=api.evaluate(base,**args)
            invalid.append({'case':name,'status':result['status'],'kernel_calls':result['kernel_calls'],'input_nonmutation':result['input_nonmutation'],'table_nonmutation':result['table_nonmutation']})
            check(result['status']!=0 and result['kernel_calls']==0 and result['input_nonmutation'] and result['table_nonmutation'],'INVALID_CONTRACT_NOT_REJECTED:'+name)
        for field in ['call_id','slot']:
            mutated=copy.deepcopy(base);mutated[field]+=1
            try:check_bound_identity(mutated)
            except ValueError:invalid.append({'case':'wrong_'+field,'pre_native_rejected':True,'kernel_calls':0})
            else:raise ValueError('WRONG_BINDING_ACCEPTED:'+field)
        output=api.evaluate(base);require_point(output)
        from independent_validate import validate_record
        original_result=result_record(base,output)
        parity=validate_record(original_result)
        check(parity['pass'],'C6_BASELINE_PARITY_OR_RESIDUAL')
        valid.append(original_result)
        iv=[-number(x) for x in base['qss']['incoming_virtual']]
        ily=[-number(x) for x in base['qss']['incoming_lyman']]
        signed=api.evaluate(base,incoming=iv,lyman=ily);require_point(signed)
        signed_result=result_record(base,signed);signed_result['control']='signed_negative_incoming'
        valid.append(signed_result)
        check(api.kernel_calls==2 and len(invalid)<=24,'C6_CALL_CAP')
        calls=api.kernel_calls
    dump(outdir/'INVALID_CONTROLS.json',invalid)
    parts=write_parts(outdir,'VALID_CONTROLS',valid)
    dump(outdir/'BASELINE_NUMERICAL_CHECK.json',parity)
    return {'pass':True,'stage':'C6','build':compiled,'binding':binding,'input_identity_files':len(checks),'valid_controls':2,'invalid_controls':len(invalid),
            'native_kernel_calls':calls,'table_initializations':1,'valid_control_parts':parts,'no_history_integration':True}

def c7(outdir):
    verify_inputs();prior=active_result('C6')
    points=list(read_parts(prior['binding']['parts']));check(len(points)==132,'PRIMARY_INPUT_COUNT')
    records=[]
    with PointAPI(outdir/'CALL_JOURNAL.jsonl') as api:
        for point in points:
            output=api.evaluate(point);require_point(output)
            check(number(output['coefficient_TM_eV'])==number(point['temperatures']['coefficient_TM_eV']) and number(output['coefficient_TR_eV'])==number(point['temperatures']['coefficient_TR_eV']),'PRIMARY_COEFFICIENT_TEMPERATURE')
            records.append(result_record(point,output))
            print(json.dumps({'point_complete':point['index'],'native_calls':api.kernel_calls}),flush=True)
        check(api.kernel_calls==132,'PRIMARY_EXACT_132')
    parts=write_parts(outdir,'PRIMARY',records)
    return {'pass':True,'stage':'C7','records':132,'native_kernel_calls':132,'table_initializations':1,'parts':parts,'query_mapping':prior['binding']['mapping'],
            'numerical_acceptance':'PENDING_C8_AUTHORITATIVE_DECIMAL80','physical_coverage':'0/313'}

def c8(outdir):
    verify_inputs();primary=active_result('C7');base=list(read_parts(primary['parts']))
    from independent_validate import validate_all,validate_record
    summary=validate_all(base,outdir/'independent')
    check(summary['pass'],'C8_AUTHORITATIVE_PARITY_RESIDUAL_OR_MUTATION_FAILURE')
    points=list(read_parts(active_result('C6')['binding']['parts']))
    controls=[];responses=[]
    with PointAPI(outdir/'CALL_JOURNAL.jsonl') as api:
        for index in (0,66,131):
            point=points[index];results={}
            for name,factor in [('zero',0.),('signed_negative',-1.),('doubled',2.)]:
                iv=[factor*number(x) for x in point['qss']['incoming_virtual']]
                ily=[factor*number(x) for x in point['qss']['incoming_lyman']]
                output=api.evaluate(point,incoming=iv,lyman=ily);require_point(output)
                record=result_record(point,output);record['control']=name
                validation=validate_record(record)
                check(validation['residual_pass'],'C8_CONTROL_BLOCK_RESIDUAL:'+name)
                record['control_residual']=validation;record['control_parity_reference_not_applicable']=True
                controls.append(record);results[name]=output['FH']
            original=base[index]['output']['FH']
            response={name:number(value)-number(original) for name,value in results.items()}
            check(any(value!=0. for value in response.values()),'LOST_INCOMING_DEPENDENCE_CONTROL')
            responses.append({'index':index,'original_FH':original,'control_FH':results,'FH_change_from_saved_primary':{k:v.hex() for k,v in response.items()},
                              'affine_second_difference_observed':(number(results['doubled'])-2*number(original)+number(results['zero'])).hex(),
                              'affinity_tolerance_gate':'NOT_ADDED; observed supplement only','physical_interpretation':'signed source algebra controls, not physical spectrum positivity'})
        check(api.kernel_calls==9 and api.kernel_calls<=12,'C8_CONTROL_CALL_CAP')
    parts=write_parts(outdir,'NATIVE_CONTROLS',controls)
    dump(outdir/'INCOMING_RESPONSES.json',responses)
    return {'pass':True,'stage':'C8_VALIDATE','validation':summary,'native_kernel_calls':9,'table_initializations':1,'native_control_parts':parts,
            'precision_indices':[0,66,131],'saved_output_mutations':['B_C_swap','band_swap','changed_solution'],'physical_coverage':'0/313'}

def plots(outdir):
    primary=active_result('C7');records=list(read_parts(primary['parts']))
    validation=active_result('C8_VALIDATE')
    from independent_validate import plot_all
    paths=plot_all(records,validation['validation'],outdir/'figures')
    return {'pass':True,'stage':'C8_PLOTS','paths':paths,'native_kernel_calls':0,'table_initializations':0,'data_source':'saved primary and independent validation only'}

if __name__=='__main__':
    stage=sys.argv[1];outdir=Path(sys.argv[2]).resolve()
    try:
        result={'C6':c6,'C7':c7,'C8_VALIDATE':c8,'C8_PLOTS':plots}[stage](outdir)
        dump(outdir/'RESULT.json',result)
        print(json.dumps({'result':str(outdir/'RESULT.json'),'pass':result['pass']}),flush=True)
    except BaseException as error:
        dump(outdir/'FAILURE.json',{'stage':stage,'type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc(),
                                  'native_call_count':'See actual CALL_JOURNAL; unfinished API_ENTER is unknown, not zero'})
        traceback.print_exc();raise

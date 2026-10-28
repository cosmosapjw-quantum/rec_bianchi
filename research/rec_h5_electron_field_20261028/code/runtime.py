"""Source locks, saved-record binding and ctypes boundary; no implicit execution."""
from pathlib import Path
import contextlib
import copy
import ctypes as C
import hashlib
import json
import math
import os
import struct

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='94b454c75b51f7c7af38126510cec609f5d7cfb2eb69ca78a491def54b31791c'
P_KEYS=('xe','xHII','nH_cm3','H_s_inv','TM_eV','TR_eV','fsR','meR')
EPS=2.0**-52

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text())
def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode()
    if len(data)>=5*1024**2: raise ValueError('OUTPUT_FILE_5MIB_LIMIT:'+str(path))
    with path.open('xb') as stream: stream.write(data)
def check(condition,reason):
    if not condition: raise ValueError(reason)
def number(value):
    check(isinstance(value,str),'HEX_STRING_REQUIRED')
    x=float.fromhex(value);check(math.isfinite(x),'NONFINITE_SAVED_INPUT');return x
def write_parts(directory,prefix,records):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    names=[];batch=[];size=0
    for record in records:
        row=(json.dumps(record,separators=(',',':'),allow_nan=False)+'\n').encode()
        check(len(row)<4*1024**2,'SINGLE_RAW_RECORD_TOO_LARGE')
        if size+len(row)>4*1024**2 and batch:
            name=directory/f'{prefix}_{len(names):03d}.jsonl'
            with name.open('xb') as f:f.write(b''.join(batch))
            names.append(str(name));batch=[];size=0
        batch.append(row);size+=len(row)
    if batch:
        name=directory/f'{prefix}_{len(names):03d}.jsonl'
        with name.open('xb') as f:f.write(b''.join(batch))
        names.append(str(name))
    return names
def read_parts(names):
    for name in names:
        with Path(name).open() as f:
            for line in f:
                if line.strip():yield json.loads(line)

def verify_inputs():
    manifest=load(ROOT/'inputs/SOURCE_MANIFEST.json')
    check(manifest['source_archive']['sha256']==SOURCE_SHA,'FOREIGN_SOURCE_ARCHIVE')
    check(manifest['file_count']==len(manifest['files'])==16,'INPUT_MANIFEST_SHAPE')
    checks=[]
    for item in manifest['files']:
        path=ROOT/item['path']; actual=sha(path)
        check(path.stat().st_size==item['bytes'] and actual==item['sha256'],'IMMUTABLE_INPUT_MISMATCH:'+item['path'])
        checks.append({'path':item['path'],'bytes':item['bytes'],'sha256':actual})
    check(sha(ROOT/'inputs/original/HyRec/hydrogen.c')=='421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b','ORIGINAL_HYDROGEN_MISMATCH')
    check(sha(ROOT/'inputs/native_path.json')=='c76b6794ed9ac028206da113f260e303cc821655a2a68b7e98a5309e5f280bf5','NATIVE_PATH_MISMATCH')
    return checks

def indexed_records(path):
    result={}
    with Path(path).open() as f:
        for line in f:
            row=json.loads(line);key=(row['id'],row['slot'])
            check(key not in result,'DUPLICATE_RECORD_KEY:'+str(key));result[key]=row
    return result

def check_bound_identity(point):
    check(point['call_id']==point['call']['id'] and point['slot']==point['call']['slot'],'CALL_ID_SLOT_BOUNDARY')
    check(point['call_id']==point['qss']['id']==point['temperatures']['id'],'FOREIGN_WRITER_ID')
    check(point['slot']==point['qss']['slot']==point['temperatures']['slot'],'FOREIGN_WRITER_SLOT')

def bind_inputs(outdir):
    outdir=Path(outdir);verify_inputs()
    capture=ROOT/'inputs/capture002'
    slots=[int(x) for x in (capture/'SELECTED_SLOTS.txt').read_text().split()]
    check(len(slots)==len(set(slots))==132,'SELECTED_SLOTS_132')
    check(slots==sorted(slots),'SELECTED_SLOT_ORDER')
    last=load(capture/'LAST_WRITERS.json')
    parameters=load(capture/'PARAMETERS.json')
    calls=indexed_records(capture/'CALLS.jsonl');qss=indexed_records(capture/'QSS_WRITES.jsonl');writes=indexed_records(capture/'WRITES.jsonl')
    points=[]
    for index,slot in enumerate(slots):
        check(0<=slot<len(last),'LAST_WRITER_SLOT_DOMAIN')
        key=(last[slot],slot)
        check(key in calls and key in qss and key in writes,'MISSING_FINAL_WRITER:'+str(key))
        call=calls[key]; vector=qss[key]; temps=writes[key]
        check(call['global']==parameters['izH0']+slot,'CALL_GLOBAL_LOCAL_INDEX')
        check(call['model']==3 and call['phase']=='H_STEADY','PRIMARY_MODEL_PHASE')
        p=[number(call[k]) for k in P_KEYS]
        check(p[0]==p[1] and p[6]==p[7]==1.,'PRIMARY_SPECIES_PARAMETERS')
        check(p[2]>0 and p[3]>0 and p[4]>0 and p[5]>0 and 0<=p[1]<1,'PRIMARY_SCALAR_DOMAIN')
        for field,size in [('real',2),('virtual',311),('incoming_virtual',311),('incoming_lyman',2),('outgoing_virtual',311),('outgoing_lyman',3),('average_virtual',311)]:
            check(len(vector[field])==size,'QSS_SHAPE:'+field)
            for value in vector[field]:number(value)
        check(number(temps['coefficient_TR_eV'])==p[5]/(p[6]*p[6]*p[7]),'COEFFICIENT_TR_PROVENANCE')
        tm=(p[4]/p[5])*(p[5]/(p[6]*p[6]*p[7]))
        check(number(temps['coefficient_TM_eV'])==tm,'COEFFICIENT_TM_ROUNDTRIP')
        point={'index':index,'call_id':key[0],'slot':slot,'call':call,'qss':vector,'temperatures':temps,
               'source_sha256':SOURCE_SHA,'units':'native_cm3_s_eV_eta','temperature_origin':'dispatcher','helium_neutral':True}
        check_bound_identity(point);points.append(point)
    path=load(ROOT/'inputs/native_path.json')
    check(path['query_count']==len(path['queries'])==313 and path['endpoint_references']==626 and path['unique_selected_times']==132,'NATIVE_QUERY_SHAPE')
    check(path['physical_coverage']=='0/313' and path['L4'] is False and path['REI_activation'] is False,'PHYSICAL_CEILING')
    by_slot={p['slot']:p for p in points};mapping=[]
    for i,query in enumerate(path['queries']):
        endpoints=query['endpoint_local_indices'];ids=query['final_writer_ids']
        check(len(endpoints)==len(ids)==len(query['final_writer_calls'])==len(query['final_writer_coefficient_temperatures'])==2,'ENDPOINT_SHAPE')
        refs=[]
        for j,slot in enumerate(endpoints):
            check(slot in by_slot,'UNBOUND_ENDPOINT_SLOT')
            point=by_slot[slot]
            check(ids[j]==point['call_id'],'ENDPOINT_WRITER_ID')
            check(query['endpoint_global_indices'][j]==point['call']['global'],'ENDPOINT_GLOBAL_INDEX')
            check(query['committed_nodes'][j]['global']==point['call']['global'] and query['committed_nodes'][j]['local']==slot,'COMMITTED_ENDPOINT_INDICES')
            check(query['final_writer_calls'][j]==point['call'],'ENDPOINT_CALL_BYTE_VALUE_BINDING')
            check(query['final_writer_coefficient_temperatures'][j]==point['temperatures'],'ENDPOINT_COEFFICIENT_PROVENANCE')
            check(query['committed_nodes'][j]['helium_neutral'] is True,'ENDPOINT_HELIUM_SCOPE')
            refs.append(point['index'])
        check(query['geometric_alpha_exact']==query['binding']['geometric_alpha_exact'],'EXACT_ALPHA_BINDING')
        mapping.append({'query_index':i,'binding':copy.deepcopy(query['binding']),'geometric_alpha_exact':query['geometric_alpha_exact'],
                        'endpoint_local_indices':copy.deepcopy(endpoints),'endpoint_global_indices':copy.deepcopy(query['endpoint_global_indices']),
                        'final_writer_ids':copy.deepcopy(ids),'point_indices':refs,'geometric_xe_affine_slope_exact':query['fields']['committed']['xe']['slope'],
                        'clock':query['clock'],'interpretation':'Source-point references only; no whole-cell field/defect admission'})
    names=write_parts(outdir,'BOUND_INPUTS',points)
    dump(outdir/'QUERY_MAPPING.json',mapping)
    summary={'pass':True,'points':132,'queries':313,'endpoint_references':sum(len(q['point_indices']) for q in mapping),'parts':names,
             'mapping':str(outdir/'QUERY_MAPPING.json'),'source_sha256':SOURCE_SHA,'new_point_calls':0}
    dump(outdir/'BINDING.json',summary)
    return points,summary

class Diagnostics(C.Structure):
    _fields_=[('events',C.c_int),('zero',C.c_int),('nonfinite',C.c_int),('overflow',C.c_int),('min_abs',C.c_double),('schur',C.c_double),('values',C.c_double*472),('kinds',C.c_int*472),('indices',C.c_int*472)]
class Output(C.Structure):
    _fields_=[('status',C.c_int),('kernel_calls',C.c_int),('diagnostics',Diagnostics)]+[(n,C.c_double) for n in ['FH','coefficient_TM_eV','coefficient_TR_eV','s','x1','Delta','H','nH']]+[
      ('xr',C.c_double*2),('xv',C.c_double*311),('A',(C.c_double*2)*2),('B',(C.c_double*311)*2),('C',(C.c_double*311)*2),('V',(C.c_double*311)*3),
      ('sr',C.c_double*2),('sv',C.c_double*311),('Dtau',C.c_double*311),('Alpha',C.c_double*2),('DAlpha',C.c_double*2),('Beta',C.c_double*2)]
def hex_values(values):
    return [hex_values(v) if isinstance(v,C.Array) else float(v).hex() for v in values]

class PointAPI:
    def __init__(self,journal):
        receipt_path=Path(load(ROOT/'build/ACTIVE_BUILD.json')['receipt'])
        build=load(receipt_path)
        check(sha(build['library'])==build['library_sha256'],'SHARED_LIBRARY_IDENTITY')
        for path,digest in build['code_sha256'].items():check(sha(ROOT/path)==digest,'C5_CODE_IDENTITY:'+path)
        self.lib=C.CDLL(build['library'])
        self.lib.ef_context_new.restype=C.c_void_p
        self.lib.ef_context_free.argtypes=[C.c_void_p]
        self.lib.ef_tables_count.restype=C.c_size_t
        self.lib.ef_tables_copy.argtypes=[C.c_void_p,C.POINTER(C.c_double),C.c_size_t]
        self.lib.ef_evaluate.argtypes=[C.c_void_p,C.POINTER(C.c_double),C.c_size_t,C.POINTER(C.c_double),C.c_size_t,C.POINTER(C.c_double),C.c_size_t,C.c_int,C.c_char_p,C.c_int,C.c_char_p,C.c_char_p,C.c_char_p,C.POINTER(Output)]
        self.lib.ef_evaluate.restype=C.c_int
        previous=Path.cwd()
        try:
            os.chdir(ROOT/'inputs/original/HyRec');self.context=self.lib.ef_context_new()
        finally:os.chdir(previous)
        check(bool(self.context),'TABLE_CONTEXT_ALLOCATION')
        self.journal=Path(journal);self.kernel_calls=0;self.api_calls=0;self.table_initializations=1
        self.initial_tables=self.tables()
        self.identity={'source_archive_sha256':SOURCE_SHA,'build_receipt':str(receipt_path),'build_receipt_sha256':sha(receipt_path),
                       'library_sha256':build['library_sha256'],'source_manifest_sha256':sha(ROOT/'inputs/SOURCE_MANIFEST.json'),
                       'initialized_tables_sha256':hashlib.sha256(self.initial_tables).hexdigest()}
    def tables(self):
        count=self.lib.ef_tables_count();array=(C.c_double*count)()
        check(self.lib.ef_tables_copy(self.context,array,count)==0,'TABLE_SNAPSHOT')
        return bytes(array)
    def event(self,value):
        with self.journal.open('a') as f:f.write(json.dumps(value,separators=(',',':'))+'\n');f.flush()
    def evaluate(self,point,*,p=None,incoming=None,lyman=None,**labels):
        check_bound_identity(point)
        p=p if p is not None else [number(point['call'][k]) for k in P_KEYS]
        incoming=incoming if incoming is not None else [number(v) for v in point['qss']['incoming_virtual']]
        lyman=lyman if lyman is not None else [number(v) for v in point['qss']['incoming_lyman']]
        arrays=[(C.c_double*len(v))(*v) for v in [p,incoming,lyman]]
        before=[bytes(v) for v in arrays];table_before=self.tables()
        flags={'model':point['call']['model'],'phase':point['call']['phase'],'helium_neutral':int(point['helium_neutral']),
               'units':point['units'],'temperature_origin':point['temperature_origin'],'source_sha256':point['source_sha256']};flags.update(labels)
        self.api_calls+=1;attempt=self.api_calls
        self.event({'event':'API_ENTER','attempt':attempt,'call_id':point['call_id'],'slot':point['slot'],'potential_native_calls':1})
        out=Output()
        status=self.lib.ef_evaluate(self.context,arrays[0],len(p),arrays[1],len(incoming),arrays[2],len(lyman),flags['model'],flags['phase'].encode(),flags['helium_neutral'],flags['units'].encode(),flags['temperature_origin'].encode(),flags['source_sha256'].encode(),C.byref(out))
        self.kernel_calls+=out.kernel_calls
        self.event({'event':'API_RETURN','attempt':attempt,'status':status,'native_kernel_calls':out.kernel_calls,'cumulative_native_calls':self.kernel_calls})
        result={'status':status,'kernel_calls':out.kernel_calls,'input_nonmutation':before==[bytes(v) for v in arrays],
                'table_nonmutation':table_before==self.tables()==self.initial_tables,
                'identity':self.identity,
                'actual_input':{'P_keys':list(P_KEYS),'P':[float(x).hex() for x in p],
                                'incoming_virtual':[float(x).hex() for x in incoming],
                                'incoming_lyman':[float(x).hex() for x in lyman],**flags}}
        if out.kernel_calls:
            for key in ['FH','coefficient_TM_eV','coefficient_TR_eV','s','x1','Delta','H','nH']:result[key]=float(getattr(out,key)).hex()
            result['Fe']=result['FH'];result['electron_scope']='FULL_H_STEADY_He_neutral_xe_equals_xHII'
            for key in ['xr','xv','A','B','C','V','sr','sv','Dtau','Alpha','DAlpha','Beta']:result[key]=hex_values(getattr(out,key))
            d=out.diagnostics
            result['diagnostics']={'events':d.events,'zero':d.zero,'nonfinite':d.nonfinite,'overflow':d.overflow,'min_abs':float(d.min_abs).hex(),'schur':float(d.schur).hex(),
                                   'values':hex_values(d.values[:min(d.events,472)]),'kinds':list(d.kinds[:min(d.events,472)]),'indices':list(d.indices[:min(d.events,472)])}
        dump(self.journal.parent/'api_raw'/f'API_{attempt:03d}.json',{'call_id':point['call_id'],'slot':point['slot'],'output':result})
        return result
    def close(self):
        if self.context:self.lib.ef_context_free(self.context);self.context=None
    def __enter__(self):return self
    def __exit__(self,*unused):self.close()

def result_record(point,output):
    return {'index':point['index'],'call_id':point['call_id'],'slot':point['slot'],'call':point['call'],
            'saved':{'FH':point['call']['dxHII_deta'],'xr':point['qss']['real'],'xv':point['qss']['virtual'],
                     'coefficient_TM_eV':point['temperatures']['coefficient_TM_eV'],'coefficient_TR_eV':point['temperatures']['coefficient_TR_eV']},
            'output':output,'source_sha256':SOURCE_SHA}

def require_point(output):
    check(output['status']==0 and output['kernel_calls']==1,'POINT_STATUS')
    check(output['input_nonmutation'] and output['table_nonmutation'],'POINT_NONMUTATION')
    d=output['diagnostics'];check(d['events']==472 and d['zero']==d['nonfinite']==d['overflow']==0,'ACTUAL_NATIVE_DIVISORS')

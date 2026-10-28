"""Source identities and exact finite-record validators; no native imports."""
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

UNIT=Path(__file__).resolve().parents[1]
REPO=UNIT.parents[1]
EPS=Fraction(1,2**52)
PHASES={'HEIII_SAHA','HE_ONLY','H_HE','H_STEADY','H_TM','LOW_PEEBLES'}
PHYSICAL={k:None for k in ('physical_query_bounds','full_state_K','physical_M2','physical_defect',
    'stability_L','positive_uniform_ode_tube','initial_error','physical_epsilon','physical_outgoing_bound')}

def check(ok,message):
    if not ok: raise ValueError(message)

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def dump(p,obj):
    with Path(p).open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')

def read_jsonl(p):
    with Path(p).open() as f:return [json.loads(line) for line in f if line.strip()]

def f64(v):
    x=float.fromhex(v) if isinstance(v,str) else float(v)
    check(math.isfinite(x),'NONFINITE_REQUIRED_STATE')
    return x

def exact(v):return Fraction.from_float(f64(v))
def rational(v):return str(v.numerator)+'/'+str(v.denominator)

def verify_locks():
    lock=json.loads((UNIT/'inputs/INPUT_LOCKS.json').read_text())
    rows=[lock['canonical_archive'],*lock['original_members'],*lock['retained_dependencies'].values()]
    for row in rows:
        check(sha(REPO/row['path'])==row['sha256'],'BAD_IMMUTABLE_SOURCE_HASH:'+row['path'])
    return lock

def validate_hash(observed,expected):check(observed==expected,'BAD_IMMUTABLE_SOURCE_HASH')
def validate_index(global_index,local_index,izH0):check(global_index-local_index==izH0,'WRONG_GLOBAL_LOCAL_INDEX')
def validate_phase(phase):check(phase in PHASES,'UNKNOWN_PHASE')

def ordered_calls(calls):
    ids=[r['id'] for r in calls]
    check(len(set(ids))==len(ids),'DUPLICATE_CALL_ID')
    check(all(b>a for a,b in zip(ids,ids[1:])),'REVERSED_CALL_ORDER')

def final_writers(writes,calls):
    byid={r['id']:r for r in calls};writers={}
    for w in writes:
        check(w['id'] in byid,'MISSING_WRITER_CALL')
        c=byid[w['id']]
        check(w['slot']==c['slot'],'WRITER_SLOT_MISMATCH')
        check(c['model']==3,'NON_FULL_WRITER')
        writers[w['slot']]=w
    return writers

def required_writer(writers,slot):
    check(slot in writers,'MISSING_REQUIRED_FINAL_WRITER')
    return writers[slot]

def validate_route(row,original):
    check(row['source_index']==original['source_index'] and row['incoming_index']==original['incoming_index'],'CHANGED_QUERY_ROUTE')

def affine(a,b,q,left,right,alpha=None):
    check(a<b,'NONPOSITIVE_CELL_DENOMINATOR')
    check(a<q<b,'OUTSIDE_QUERY')
    t=(q-a)/(b-a)
    if alpha is not None:check(t==alpha,'CHANGED_EXACT_QUERY_ALPHA')
    value=(1-t)*left+t*right
    slope=(right-left)/(b-a)
    check(left+(a-a)*slope==left and left+(b-a)*slope==right,'AFFINE_ENDPOINT_IDENTITY')
    check(min(left,right)<=value<=max(left,right),'AFFINE_CONVEX_HULL')
    return {'left':rational(left),'right':rational(right),'query':rational(value),'slope':rational(slope),
            'min':rational(min(left,right)),'max':rational(max(left,right))}

def recurrence(row):
    for k in ('current','prev','prev2','after_prev','after_prev2'):
        check(k in row,'OMITTED_PREV2' if k=='prev2' else 'MISSING_RECURRENCE_OPERAND:'+k)
    check(exact(row['after_prev'])==exact(row['current']) and exact(row['after_prev2'])==exact(row['prev']),'MEMORY_SHIFT_MISMATCH')
    if not row['integrated']:
        return {'classification':'POST_SAHA_NOT_RECURRENCE','rho':None,'memory_shift_pass':True}
    for k in ('xin','xout','current','prev','prev2','after_prev','after_prev2','h'):
        check(k in row,'OMITTED_PREV2' if k=='prev2' else 'MISSING_RECURRENCE_OPERAND:'+k)
    x,y,h,F,P2=(exact(row[k]) for k in ('xin','xout','h','current','prev2'))
    sigma=row['sigma']
    check(sigma==(-1 if row['component']=='xH1s' else 1),'NEUTRAL_H_WRONG_SIGN')
    rho=y-x-h*sigma*(Fraction(5,4)*F-Fraction(1,4)*P2)
    gross=abs(x)+abs(y)+abs(h)*(Fraction(5,4)*abs(F)+Fraction(1,4)*abs(P2))
    check(abs(rho)<=64*EPS*gross if gross else rho==0,'RECURRENCE_RESIDUAL')
    check(exact(row['after_prev'])==F and exact(row['after_prev2'])==exact(row['prev']),'MEMORY_SHIFT_MISMATCH')
    return {'classification':'DISCRETE_ARITHMETIC_ONLY','memory_shift_pass':True,'rho':rational(rho),'gross':rational(gross),
            'normalized':rational(abs(rho)/gross) if gross else '0/1'}

def density_units(cm3,m3):
    a,b=exact(cm3)*1000000,exact(m3)
    check(abs(a-b)<=512*EPS*max(abs(a),abs(b)) if (a or b) else a==b,'DENSITY_UNIT_MISMATCH')

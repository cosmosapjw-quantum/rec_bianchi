"""Eighteen frozen small-record controls; no native/RHS or prior producer import."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import common as C


def recurrence_fixture(neutral=False):
    # All inputs are dyadic and exact in binary64. Independent hand result:
    # h*(5*2/4-(-2)/4)=(1/8)*3=3/8; prev=1 is distinct from prev2=-2.
    return dict(component='xH1s' if neutral else 'xe', sigma=-1 if neutral else 1,
                integrated=True, xin=0.5 if neutral else 10.0,
                xout=0.125 if neutral else 10.375, current=2.0,
                prev=1.0, prev2=-2.0, after_prev=2.0, after_prev2=1.0, h=0.125)


def cases():
    correct = recurrence_fixture()
    omitted = deepcopy(correct); omitted.pop('prev2')
    wrong_memory = deepcopy(correct); wrong_memory['prev2'] = wrong_memory['prev']
    wrong_sign = recurrence_fixture(neutral=True); wrong_sign['sigma'] = 1
    calls = [{'id':7,'slot':17,'model':3,'role':'committed_input'},
             {'id':8,'slot':17,'model':3,'role':'post_saha_plus'},
             {'id':9,'slot':17,'model':3,'role':'post_saha_minus'}]
    writes = [{'id':r['id'],'slot':17} for r in calls]
    expected_hash = hashlib.sha256(b'fixed manufactured canonical bytes\n').hexdigest()
    changed_hash = hashlib.sha256(b'changed manufactured canonical bytes\n').hexdigest()

    def post_saha():
        fixture = {**recurrence_fixture(neutral=True), 'integrated':False,
                   'phase':'H_HE','update_kind':'post_saha','xout':0.375}
        value = C.recurrence(fixture)
        if value != {'classification':'POST_SAHA_NOT_RECURRENCE','rho':None,
                     'memory_shift_pass':True}:
            raise AssertionError('POST_SAHA_WAS_GIVEN_A_RECURRENCE')
        return value

    def overwrite():
        C.ordered_calls(calls)
        selected = C.required_writer(C.final_writers(writes,calls),17)
        if selected['id'] != 9:
            raise AssertionError('WRONG_FINAL_WRITER')
        return {'selected_call_id':selected['id'],'selected_role':calls[-1]['role'],
                'overwritten_call_ids':[7,8], 'committed_input_is_not_final_writer':True}

    def affine_identity():
        a,b,q = Fraction(-3),Fraction(-1),Fraction(-5,2)
        left,right,alpha = Fraction(3),Fraction(-1),Fraction(1,4)
        value = C.affine(a,b,q,left,right,alpha)
        # Independent known affine function u(t)=-2t-3.
        if Fraction(value['query'])!=2 or Fraction(value['slope'])!=-2:
            raise AssertionError('KNOWN_AFFINE_VALUE_OR_SLOPE')
        if left+(a-a)*(-2)!=3 or left+(b-a)*(-2)!=-1:
            raise AssertionError('KNOWN_ENDPOINT_IDENTITIES')
        if not Fraction(-1)<=Fraction(value['query'])<=3:
            raise AssertionError('KNOWN_CONVEX_HULL')
        return {**value,'alpha':'1/4','independent_function':'u(t)=-2*t-3'}

    return [
        ('bad_immutable_source_hash','BAD_IMMUTABLE_SOURCE_HASH',
         lambda:C.validate_hash(changed_hash,expected_hash),
         {'expected_sha256':expected_hash,'changed_sha256':changed_hash}),
        ('wrong_global_local_index','WRONG_GLOBAL_LOCAL_INDEX',
         lambda:C.validate_index(105,6,100),{'global':105,'local':6,'izH0':100}),
        ('nonpositive_cell_denominator','NONPOSITIVE_CELL_DENOMINATOR',
         lambda:C.affine(Fraction(2),Fraction(1),Fraction(3,2),Fraction(4),Fraction(7)),
         {'a':'2','b':'1','q':'3/2'}),
        ('outside_query','OUTSIDE_QUERY',
         lambda:C.affine(Fraction(0),Fraction(1),Fraction(5,4),Fraction(4),Fraction(7)),
         {'a':'0','b':'1','q':'5/4'}),
        ('unknown_phase','UNKNOWN_PHASE',lambda:C.validate_phase('INVENTED_PHASE'),
         {'phase':'INVENTED_PHASE'}),
        ('duplicate_call_id','DUPLICATE_CALL_ID',
         lambda:C.ordered_calls([{'id':21},{'id':21}]),{'ids':[21,21]}),
        ('reversed_call_order','REVERSED_CALL_ORDER',
         lambda:C.ordered_calls([{'id':23},{'id':22}]),{'ids':[23,22]}),
        ('missing_required_final_writer','MISSING_REQUIRED_FINAL_WRITER',
         lambda:C.required_writer({17:{'id':7,'slot':17}},18),
         {'available_slot':17,'required_slot':18}),
        ('writer_slot_mismatch','WRITER_SLOT_MISMATCH',
         lambda:C.final_writers([{'id':7,'slot':18}],calls),
         {'call_id':7,'call_slot':17,'write_slot':18}),
        ('changed_query_route','CHANGED_QUERY_ROUTE',
         lambda:C.validate_route({'incoming_index':139,'source_index':140},
                                 {'incoming_index':139,'source_index':311}),
         {'incoming_index':139,'source_expected':311,'source_corrupted':140}),
        ('omitted_previous2','OMITTED_PREV2',lambda:C.recurrence(omitted),
         {'row':omitted,'correct_increment':'3/8'}),
        ('previous_instead_of_previous2','RECURRENCE_RESIDUAL',
         lambda:C.recurrence(wrong_memory),
         {'row':wrong_memory,'correct_increment':'3/8','corrupted_increment':'9/32',
          'independent_nonzero_residual':'3/32'}),
        ('nonfinite_required_state','NONFINITE_REQUIRED_STATE',lambda:C.f64('inf'),
         {'required_state':'inf'}),
        ('density_cm3_m3_mismatch','DENSITY_UNIT_MISMATCH',
         lambda:C.density_units(2.0,2.0),
         {'nH_cm3':'2','required_nH_m3':'2000000','corrupted_nH_m3':'2'}),
        ('neutral_h_wrong_sign','NEUTRAL_H_WRONG_SIGN',lambda:C.recurrence(wrong_sign),
         {'row':wrong_sign,'correct_signed_increment':'-3/8',
          'wrong_sign_independent_residual':'-3/4'}),
        ('post_saha_separate_from_recurrence',None,post_saha,
         {'integrated':False,'valid_memory_shift':True,
          'xin':'1/2','xout':'3/8','ODE_recurrence_deliberately_not_satisfied':True}),
        ('legitimate_overwrite_selects_last_writer',None,overwrite,
         {'calls':calls,'writes':writes,'expected_last_writer':9}),
        ('exact_affine_endpoint_query_and_hull',None,affine_identity,
         {'a':'-3','b':'-1','q':'-5/2','left':'3','right':'-1','alpha':'1/4'}),
    ]


def run(output:Path):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    rows=[]; planned=cases()
    if len(planned)!=18:
        raise ValueError('FROZEN_CONTROL_COUNT')
    with (output/'CONTROL_ROWS.jsonl').open('x') as stream:
        for index,(name,expected,operation,fixture) in enumerate(planned,1):
            row={'index':index,'name':name,'fixture':fixture,
                 'expected_refusal':expected,'scope':'manufactured finite-record control'}
            try:
                try:
                    observed=operation()
                except ValueError as exc:
                    if expected is None or str(exc)!=expected:
                        raise
                    row.update(observed_refusal=str(exc),result='PASS')
                else:
                    if expected is not None:
                        raise AssertionError('EXPECTED_REFUSAL_NOT_RAISED:'+expected)
                    row.update(observed=observed,result='PASS')
            except Exception as exc:
                row.update(result='FAIL',error=type(exc).__name__+':'+str(exc))
                rows.append(row);stream.write(json.dumps(row,allow_nan=False)+'\n');stream.flush()
                C.dump(output/'CONTROLS.json',{'status':'FAIL','rows':rows,'planned':18})
                raise
            rows.append(row);stream.write(json.dumps(row,allow_nan=False)+'\n');stream.flush()
    summary={'status':'PASS','planned':18,'passed':len(rows),'failed':0,
             'negative_refusal_controls':15,'positive_controls':3,'native_runs':0,'RHS_calls':0,
             'previous_scientific_replays':0,'physical':dict(C.PHYSICAL),
             'physical_coverage':'0/313','H6':'OPEN','H7':'OPEN','L4_ready':False,'REI_activation':False}
    C.dump(output/'CONTROLS.json',{'summary':summary,'rows':rows})
    C.dump(output/'SUMMARY.json',summary)
    return summary

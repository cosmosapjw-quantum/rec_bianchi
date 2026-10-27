#!/usr/bin/env python3
"""Prepare additive return/status and a single byte-local DAG pointer; never publish."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import time

CENTRAL='research/orchestration_expansion_20261025'
NODE='REC-H5-DEFECT-BOUND01'
KEY='owner_return_native_reference01_20261027'
RETURN=CENTRAL+'/returns/REC_H5_NATIVE_REFERENCE01_20261027.json'
STATUS=CENTRAL+'/status/REC_H5_NATIVE_REFERENCE01_20261027.json'


def enc(v):
    return (json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()


def sha(b): return hashlib.sha256(b).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dag',type=Path,required=True,help='fresh complete DAG bytes at expected HEAD')
    ap.add_argument('--dag-sha256',required=True)
    ap.add_argument('--expected-head',required=True)
    ap.add_argument('--science-commit',required=True)
    ap.add_argument('--decision',type=Path,required=True)
    ap.add_argument('--decision-sha256',required=True)
    ap.add_argument('--central-completed',type=int,required=True,help='root count bound to fresh owner ledger')
    ap.add_argument('--out',type=Path,required=True,help='new assembly directory')
    args=ap.parse_args(); cpu0=time.process_time()
    for name in ('expected_head','science_commit'):
        if not re.fullmatch('[0-9a-f]{40}',getattr(args,name)): ap.error(name+' requires actual SHA')
    raw=args.dag.read_bytes(); db=args.decision.read_bytes()
    if sha(raw)!=args.dag_sha256 or sha(db)!=args.decision_sha256:
        raise ValueError('root-bound source bytes mismatch')
    original=json.loads(raw);decision=json.loads(db)
    if not decision or len(original['nodes'])!=88 or len(original['integration_edges'])!=17:
        raise ValueError('nonempty root decision and original88nodes/17edges required')
    if not 0<=args.central_completed<=88: ap.error('invalid actual count')
    nodes=original['nodes']; target=next(n for n in nodes if n['id']==NODE)
    if KEY in target: raise ValueError('return pointer exists; root must resolve existing observation')
    pointer={'source_file':'returns/REC_H5_NATIVE_REFERENCE01_20261027.json',
             'source_repository':'cosmosapjw-quantum/rec_bianchi',
             'source_commit':args.science_commit,'count_increment':0}
    # Locate nodes via JSON decoder; splice only this node's added sibling key.
    text=raw.decode('utf-8');decoder=json.JSONDecoder();pos=text.index('{')+1
    # Locate the top-level nodes value, skipping whole nested preimages.
    while True:
        while text[pos].isspace() or text[pos]==',': pos+=1
        if text[pos]=='}': raise ValueError('top-level nodes array absent')
        name,pos=decoder.raw_decode(text,pos)
        while text[pos].isspace(): pos+=1
        if text[pos]!=':': raise ValueError('invalid top-level member')
        pos+=1
        while text[pos].isspace(): pos+=1
        if name=='nodes':
            if text[pos]!='[': raise ValueError('nodes is not an array')
            pos+=1;break
        _,pos=decoder.raw_decode(text,pos)
    found=None
    while True:
        while text[pos].isspace() or text[pos]==',': pos+=1
        if text[pos]==']': break
        obj,end=decoder.raw_decode(text,pos)
        if obj.get('id')==NODE: found=(pos,end); break
        pos=end
    if found is None: raise ValueError('target node absent')
    left,right=found; node_text=text[left:right]
    opening=node_text[:-1].rstrip()
    addition=json.dumps(KEY)+': '+json.dumps(pointer,ensure_ascii=False)
    patched_node=opening+',\n      '+addition+'\n    }'
    patched=(text[:left]+patched_node+text[right:]).encode()
    after=json.loads(patched); restored=deepcopy(after)
    next(n for n in restored['nodes'] if n['id']==NODE).pop(KEY)
    if restored!=original: raise ValueError('change outside one added node sibling')
    if not patched.startswith(text[:left].encode()) or not patched.endswith(text[right:].encode()):
        raise ValueError('unchanged DAG byte complement mismatch')
    owner_return={'schema':'REC_H5_NATIVE_REFERENCE01_CENTRAL_RETURN_V1',
                  'central_base':args.expected_head,'science_commit':args.science_commit,
                  'parent_node':NODE,'root_decision':decision,
                  'root_decision_sha256':sha(db),'count_increment':0,
                  'counts':{'central_completed':args.central_completed,'total':88,'this_unit_increment':0},
                  'physical_H5_bound_coverage':'0/313','physical_epsilon':None,
                  'full_state_K':None,'physical_M2':None,'L4_ready':False,
                  'scope':'Actual313 native deterministic reference/representation bounds; physical history defect/stability/tube obligations retain their own providers.',
                  'historical_budgets':'PRESERVED_NO_RESET_OR_TRANSFER'}
    status={'schema':'REC_H5_NATIVE_REFERENCE01_SCOPED_STATUS_V1','source_file':'returns/REC_H5_NATIVE_REFERENCE01_20261027.json',
            'source_commit':args.science_commit,'parent_status':'UNCHANGED','count_increment':0,
            'central_base':args.expected_head,'central_completed':args.central_completed,'total':88,
            'physical_epsilon':None,'physical_bound_coverage':'0/313','L4_ready':False}
    payloads={CENTRAL+'/DAG.json':patched,RETURN:enc(owner_return),STATUS:enc(status)}
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False); entries=[];manifest=[]
    for rel,data in payloads.items():
        p=out/'patch_tree'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        entries.append({'path':rel,'mode':'100644','type':'blob','content':data.decode()})
        manifest.append({'path':rel,'bytes':len(data),'sha256':sha(data)})
    (out/'CENTRAL_TREE_ENTRIES.json').write_bytes(enc(entries))
    (out/'CENTRAL_PATCH_MANIFEST.json').write_bytes(enc(manifest))
    receipt={'schema':'REC_H5_NATIVE_REFERENCE01_CENTRAL_PREPARATION_V1','expected_head':args.expected_head,
             'base_DAG_sha256':sha(raw),'science_commit':args.science_commit,'changed_node':NODE,
             'only_added_sibling':KEY,'all88contracts_dependencies_budgets_other_fields':'STRUCTURALLY_IDENTICAL',
             'all17edges_and_non_node_fields':'STRUCTURALLY_IDENTICAL','unchanged_DAG_byte_complement':True,
             'CURRENT_STATUS_json':'NOT_MODIFIED','counts_preserved':args.central_completed,
             'increment':0,'files':3,'science_runs':0,'Git_writes':0,
             'metadata_CPU_s':time.process_time()-cpu0,'startup_tail_tool_LLM_CPU':'UNKNOWN_NOT_ZERO',
             'remote_freshness':'ROOT_MUST_RECHECK_HEAD_BEFORE_EXPECTED_SHA_NON_FORCE_UPDATE'}
    (out/'CENTRAL_PREPARATION_RECEIPT.json').write_bytes(enc(receipt));print(json.dumps(receipt))


if __name__=='__main__': main()

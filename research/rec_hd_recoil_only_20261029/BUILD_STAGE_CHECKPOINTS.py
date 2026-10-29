"""Build retrospective, fully inspectable stage checkpoint objects and manifests.

This does not claim stages' computations took place at ZIP creation times; captures
already-executed objective evidence with correct independent-audit statuses.
"""
from __future__ import annotations
from pathlib import Path
import json,hashlib,zipfile,os
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
out=R/'stages';out.mkdir(exist_ok=True)
stages=[f'R{i}' for i in range(1,11)]+[f'C{i}' for i in range(1,11)]
notes={
 'R1':'Scientific target: can free molecular recoil account for existing exact source frequency differences?',
 'R2':'Reused pinned public PR156 source-tuple evidence and official archived 2011 v2 directory; original bytes remain missing',
 'R3':'Metric, frequency, rest-frame, rest-mass bound, sign, units and caveats fixed',
 'R4':'Emission/absorption two-body exact alternatives, medium/fit/frame hypotheses retained',
 'R5':'Exact photon energy, recoil frequency bound, 3-sector energy balance derived',
 'R6':'Same-context scientific review; native independent author NOT_RUN',
 'R7':'Actual stateless Wolfram mass-shell verification, exact Fraction checks',
 'R8':'Recoil-only model excluded as sole cause for J2–8 under M>=2u; no global no-go',
 'R9':'Source-locked computational contract with typed provenance and untouched 35Hz gate',
 'R10':'Theory closure and durable proof, source, scope and handoff',
 'C1':'Output/test acceptance pinned to original PR156 source-field tuple subset',
 'C2':'Math-to-implementation map and source checks',
 'C3':'Fraction exact arithmetic and rest-mass envelopes, controlled long-double crosscheck',
 'C4':'Single-host short bounded plan; no IVP, native physics or full suite',
 'C5':'Runnable code, scientific output and figure generation',
 'C6':'21 Python normal + 21 -O PASS; compileall',
 'C7':'Scientific mass-shell and three-sector check, not physical/experimental validation',
 'C8':'C++ 8 lines/24 values vs exact high-precision, figure directly inspected, no speedup',
 'C9':'Same-context code review; distinct-author native review NOT_RUN',
 'C10':'Draft release, stage ZIPs, delivery receipts and next thread handoff'
}
results=[];done=0
for st in stages:
 accepted=st not in ('R6','C9')
 if accepted: done+=1
 result={
   'schema':'REC_HD_RECOIL_STAGE_CHECKPOINT_V1', 'stage':st,
   'stage_work_provenance':'RETROSPECTIVE_CHECKPOINT_AFTER_RESEARCH_EXECUTION; not contemporaneous step-by-step computational run',
   'status':'COMPLETE_SCOPED' if accepted else 'PARTIAL_NATIVE_DISTINCT_AUTHOR_NOT_RUN',
   'stage_objective_result':notes[st],
   'new_unit_completed_so_far':done,'new_unit_total':20,
   'central_DAG':{'completed':28,'total':88,'delta':0},
   'REC_physical_DAG':{'completed':0,'total':313,'delta':0},
   'parent_PR157_HEAD':'e209cd0180c8bf199fc476c37e3cbf8d50394b6c',
   'source_blob':'5a99c9e31604347cf756abb4ab3ea1a134238e0d',
   'frozen_35Hz':'FAIL_7_OF_8', 'production':'HOLD',
   'new_genuine_physical_node_count':0,
   'checkpoints_are_real_time_stage_completion_claim':False,
 }
 payload=(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
 (out/(st+'.json')).write_bytes(payload)
 paths=['data/PR156_SELECTED_FREQUENCIES.json','evidence/RESULT.json','THEORY_KO.md','NEXT_NODE_CONTRACT.json']
 if st.startswith('C'):paths+=['CODING_KO.md','src/recoil.py','src/recoil_crosscheck.cpp','tests/test_recoil.py','evidence/UNITTEST.log','evidence/UNITTEST_O.log','evidence/CPP_STDERR.log']
 entries={'STAGE.json':payload}
 for p in paths:entries[p]=(R/p).read_bytes()
 manifest={'schema':'REC_HD_STAGE_BUNDLE_MANIFEST_V1','stage':st,'members':{p:{'size':len(b),'sha256':hashlib.sha256(b).hexdigest()} for p,b in sorted(entries.items())}}
 entries['STAGE_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
 zname=out/(f'REC_HD_RECOIL_{st}_20261029.zip')
 with zipfile.ZipFile(zname,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for name,b in sorted(entries.items()):z.writestr(name,b)
 with zipfile.ZipFile(zname) as z:
  assert z.testzip() is None
  for name,x in manifest['members'].items():assert hashlib.sha256(z.read(name)).hexdigest()==x['sha256']
 result['stage_ZIP']={'name':zname.name,'size':zname.stat().st_size,'sha256':hashlib.sha256(zname.read_bytes()).hexdigest(),'crc_and_manifest':'PASS'}
 results.append(result)
ledger={'schema':'REC_HD_RECOIL_STAGE_LEDGER_V1','track_order':'R1-R10 then C1-C10','units_count':20,'scoped_complete':done,'scoped_partial':len(stages)-done,
        'source_snapshot':'Public pinned PR156 field triples, no new raw input',
        'stage_ZIPs_are_retrospective_snapshots':True,'stage_Git_and_cloud_ack_require_live_receipts':True,
        'central_DAG':'28/88','REC_physical_DAG':'0/313','statuses':results}
(R/'STAGE_LEDGER.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'stages':len(results),'complete':done,'partial':len(results)-done,'sizes_bytes':sum(x['stage_ZIP']['size'] for x in results)},indent=2))

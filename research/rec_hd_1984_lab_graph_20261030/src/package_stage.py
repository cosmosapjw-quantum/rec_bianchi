"""Deterministic retrospective stage evidence, not claims of 20 temporal separate experiments."""
import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1]
summary={
 'R1':'Lock experiment-first question, source/gate preservation and new 1984 lab scope',
 'R2':'Read 1984 publisher primary abstract and existing 2022 lab papers, PR161/162 evidence',
 'R3':'Distinguish primary measurement, historical catalog, model fields, assumed LTE, unqualified covariance',
 'R4':'Construct nine-level measured incidence graph with five measured constraints and optional nominal 1-0 anchor',
 'R5':'Derive graph rank 5/6, identify missing bridges, produce measured frequency photon and LTE formulas',
 'R6':'Independent different-author science review NOT_RUN; Wolfram method-level same-author only',
 'R7':'Wolfram exact rank nullspace and numerical LTE/Hz identity verified on current source literals',
 'R8':'Admit three authentic 1984 measured lines as scoped evidence; preserve all original production gates',
 'R9':'Write self-contained physical derivation, source role and dimension-consistent computational interface',
 'R10':'Create durable source-locked scientific handoff; auto-next false',
 'C1':'Pin PR162 archive, PR161 source transcription, 1984 and 2022 literal measured inputs',
 'C2':'Map measured wavenumber/Hz to source photon and CDMS energies/Einstein-A fields',
 'C3':'Implement exact SI conversion, Decimal exp, incidence graph Fraction elimination',
 'C4':'Bound computation to five lab edges, nine levels, 3 temperatures and 3 figures',
 'C5':'Implement real physical data 5-row atlas, 3-row photon fields, 9 LTE rows, conditional partial levels',
 'C6':'Execute 15/15 Python unittest normal and optimized, compileall; repair initial CSV field union error',
 'C7':'Validate units, quantum assignments, positivity, low-J conditional levels and source tamper negative cases',
 'C8':'Check exact rank/Decimal precision and preserve model uncertainty unknown; no speculative speedup',
 'C9':'Independent different-author implementation review NOT_RUN; no promotion from same-author Wolfram checks',
 'C10':'Archive and publish source, measured data, code and validation with gated next-thread handoff'
}
stages=[];n=0
for i,key in enumerate(summary):
 flag=(key in {'R6','C9'}); n+=0 if flag else 1
 data={'schema':'REC_HD_1984_LAB_GRAPH_STAGE_V1','stage':key,'status':'PARTIAL_DIFFERENT_AUTHOR_NOT_RUN' if flag else 'COMPLETE_SCOPED',
 'stage_summary':summary[key],'cumulative_scoped_completed':n,'scoped_total':20,
 'canonical_DAG':'28/88','REC_physical_DAG':'0/313','canonical_completed_delta':0,'REC_physical_completed_delta':0,
 'new_1984_measured_lines':3,'old_measured_2022_combinations_reused':2,
 'primary_code_test':'15/15 normal and 15/15 -O PASS' if key.startswith('C') and int(key[1:])>=6 else 'STAGE_NOT_NEW_TEST_RUN',
 'physical_source_original_gate':'35Hz FAIL7/8 UNCHANGED','production':'HOLD',
 'timestamp_semantics':'RETROSPECTIVE_STAGE_EVIDENCE_NOT_CONTEMPORANEOUS_WORK_EVENT',
 'stage_Library_upload_receipt':'CHECK_SEPARATELY','stage_Git_commit_receipt':'CHECK_SEPARATELY','stage_Drive_upload_receipt':'CHECK_SEPARATELY'}
 file=P/'stages'/f'{key}.json';file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 stages.append({'stage':key,'status':data['status'],'scope_complete':n,'path':str(file.relative_to(P)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bytes':file.stat().st_size})
ledger={'schema':'REC_HD_1984_LAB_GRAPH_STAGE_LEDGER_V1','retrospective_stage_notes':True,'created_after_science_and_tests':True,'stage_count':20,'complete_scoped':18,'partial_different_author':['R6','C9'],'stages':stages,'canonical_DAG':'28/88','REC_physical_DAG':'0/313','actual_new_laboratory_measurement_edges':3,'actual_new_physical_LTE_rows':9,'native_subagent':'NOT_RUN_NO_NATIVE_DELEGATION_TOOL'}
(P/'STAGE_LEDGER.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
# Freeze complete archive manifest excluding itself: recursive SHA of all present tangible evidence, no historical sources modified.
files=sorted(x for x in P.rglob('*') if x.is_file() and '__pycache__' not in str(x) and x.name!='MANIFEST_SHA256.json' and 'delivery' not in x.parts)
manifest={'schema':'REC_HD_1984_LAB_GRAPH_MANIFEST_V1','entries':{str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(P/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
files=sorted(x for x in P.rglob('*') if x.is_file() and '__pycache__' not in str(x) and 'delivery' not in x.parts)
out=P.parent/'REC_HD_1984_LAB_GRAPH_20261030_SOURCE.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  info=zipfile.ZipInfo(str(p.relative_to(P)),(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,p.read_bytes())
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert all(hashlib.sha256(z.read(k)).hexdigest()==v for k,v in manifest['entries'].items())
print('PATH',out,'BYTES',out.stat().st_size,'SHA256',hashlib.sha256(out.read_bytes()).hexdigest(),'MEMBERS',len(files),'MANIFEST',len(manifest['entries']))

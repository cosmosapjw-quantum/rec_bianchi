"""Create-only immutable experiment source archive and 20 retrospective stage snapshots."""
import hashlib,json,zipfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PREV=Path('/mnt/data/REC_HD_LAB_COMBINATION_20261029/REC_HD_LAB_COMBINATION_20261029_SOURCE.zip')
PREVSHA='d9a920979e73c81e378670874952b06e76811fa81f3b669d153d43febf60ce51'
assert hashlib.sha256(PREV.read_bytes()).hexdigest()==PREVSHA
SRC=ROOT/'sources/PR160_PARENT_SOURCE_IMMUTABLE.zip'
if not SRC.exists(): shutil.copyfile(PREV,SRC)
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==PREVSHA
S=(ROOT/'data/LAMDA_HD_SOURCE_TRANSCRIPTION.json').read_bytes(); source_sha=hashlib.sha256(S).hexdigest()
stages=[f'R{i}' for i in range(1,11)]+[f'C{i}' for i in range(1,11)]
objectives={
'R1':'Lock physical objective, immutable PR160, canonical DAG and no promotion',
'R2':'Read 2021 official LAMDA real 9-level 8-radiative 54-collision fields and actual 2022 lab context',
'R3':'Separate source-transcribed inputs, previous original byte pin, source gate, physical assumptions',
'R4':'Construct two-level J1 and full-nine physical model alternatives',
'R5':'Prove positive J1 two-level nonLTE cooling and exact ortho-fraction invariance',
'R6':'Independent distinct-author scientific review unavailable; same-context signs/units checked',
'R7':'Execute Wolfram symbolic/numeric J1 half-density/orthofraction and 2021 actual source gap',
'R8':'Classify J1 source-gated part vs full9 source-unqualified diagnostics',
'R9':'Write model equations, units, source data and owner limitations',
'R10':'Preserve theory evidence and next CDMS/owner action',
'C1':'Freeze 63+63 prescribed model grid and unchanged source gate',
'C2':'Map source channels 9 levels, 8 A, 18 H2 coll channels, 54 numeric entries to generator',
'C3':'Design generator, detailed balance and no-CMB optically-thin stationary solve',
'C4':'Bound data generation and stage/phase backup publication',
'C5':'Implement source-guarded J1/full9, CSV exports and science plots',
'C6':'Run actual 22 standard & optimized unittests; repair cancellation test; compileall',
'C7':'Verify J1 energy ledger and 9level independent physical meaning limits',
'C8':'Independent mpmath 80-digit 63x9 and 3 plots; no speed/production benchmark',
'C9':'Different-author independent code review NOT_RUN',
'C10':'Build source archive, output tables, immutable parent, Git/Drive/Library handoff'}
partial={'R6':'PARTIAL_DIFFERENT_AUTHOR_NOT_RUN','C9':'PARTIAL_DIFFERENT_AUTHOR_NOT_RUN'}
paths=[];done=0
(ROOT/'stages').mkdir(exist_ok=True)
for stage in stages:
 if stage not in partial:done+=1
 state={
 'schema':'REC_HD_NONLTE_R_C_STAGE_EVIDENCE_V1','date_kst':'2026-10-30',
 'stage':stage,'status':partial.get(stage,'COMPLETE_SCOPED'),
 'objective':objectives[stage], 'cumulative_scoped_completed':done,
 'scoped_total':20,'canonical_DAG':{'completed':28,'total':88,'delta':0},
 'REC_physical_DAG':{'completed':0,'total':313,'delta':0},
 'auxiliary_research_DAG':{'completed':1,'total':2,'does_not_promote_canonical':True},
 'parent_PR160_HEAD':'0a8a0bcf740da6e4a2acda9d4fd071f7ed8e2691',
 'source_transcription_SHA256':source_sha,
 'original_LAMDA_byte_retrieval': 'NOT_RUN',
 'CDMS_2011_v2_raw':'NOT_ACQUIRED','original_35Hz':'FAIL7_OF8',
 'production':'HOLD','native_subagent':'NOT_RUN',
 'provenance':'RETROSPECTIVE_AFTER_SCIENCE_EXECUTION_NOT_CONTEMPORANEOUS_20_SCIENCE_RUNS',
 'Git_published':'NOT_YET_AT_STAGE_CREATION', 'Google_Drive_uploaded':'NOT_YET_AT_STAGE_CREATION',
 'Dropbox_binary_uploaded':False}
 (ROOT/'stages'/f'{stage}.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
 paths.append(stage)
status={'schema':'REC_HD_NONLTE_RC_STAGE_LEDGER_V1','date_kst':'2026-10-30','scoped_completed':done,'scoped_total':20,'statuses':{x:('COMPLETE_SCOPED' if x not in partial else partial[x]) for x in stages},'status_stage_files':paths,'new_auxiliary':'1/2','central':'28/88','REC_physical':'0/313','all_stage_files_retrospective':True,'current_stage_Git_Drive_Dropbox_receipts':'LATER_DETACHED'}
(ROOT/'STAGE_LEDGER.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
checkpoints=[
('S0_SOURCE','9+8+54 source-visible input transcribed; raw bytes unavailable, source gate immutable'),
('S1_THEORY','J1 2level formula, ortho derivative identically zero, Wolfram independently verifies'),
('S2_CODE','63+63 models, 54 rate rows, 504 photon rows, Python 22/22 normal -O'),
('S3_VALIDATION','mpmath80 63/63, plots 3 inspected, auxiliary 1/2, physical HOLD')]
for s,msg in checkpoints:
 obj={'schema':'REC_HD_NONLTE_REAL_PHASE_CHECKPOINT_V1','stage':s,'objective_evidence':msg,'source_transcription_sha256':source_sha,'canonical_DAG':'28/88','REC_physical_DAG':'0/313','auxiliary':'1/2','actual_create_time':'2026-10-30 late packaging AFTER related work; not contemporaneous point-in-time experimental checkpoint'}
 (ROOT/'checkpoints'/f'{s}.json').write_text(json.dumps(obj,indent=2)+'\n')
exclude={'MANIFEST_SHA256.json'}
files=sorted(x for x in ROOT.rglob('*') if x.is_file() and '/__pycache__/' not in str(x) and x.suffix not in ('.pyc',) and x.name not in exclude and not x.name.endswith('.zip') or False)
# include one immutable parent .zip explicitly; avoid the output zip itself
files=[x for x in files if x.name != 'REC_HD_NONLTE_20261030_SOURCE.zip']
parent=ROOT/'sources/PR160_PARENT_SOURCE_IMMUTABLE.zip'
if parent not in files: files.append(parent)
files=sorted(set(files))
manifest={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files}
(ROOT/'MANIFEST_SHA256.json').write_text(json.dumps({'schema':'REC_HD_NONLTE_MANIFEST_V1','files':manifest},indent=2)+'\n')
out=ROOT/'REC_HD_NONLTE_20261030_SOURCE.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for x in files+[ROOT/'MANIFEST_SHA256.json']:
  z.write(x,str(x.relative_to(ROOT)))
with zipfile.ZipFile(out,'r') as z:
 assert z.testzip() is None
 inside=json.loads(z.read('MANIFEST_SHA256.json'))['files']
 assert all(hashlib.sha256(z.read(k)).hexdigest()==v for k,v in inside.items())
 assert z.read('sources/PR160_PARENT_SOURCE_IMMUTABLE.zip')==PREV.read_bytes()
print(json.dumps({'source_zip':out.name,'size':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'members':len(files)+1,'manifest_entries':len(manifest),'RC_done':done,'RC_total':len(stages),'parent_sha':PREVSHA},indent=2))
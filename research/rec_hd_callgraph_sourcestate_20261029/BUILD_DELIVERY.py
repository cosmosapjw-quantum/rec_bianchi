"""Deterministic, create-only source+stage archive builder for scoped HD research.

The R/C stage archives are explicitly *retrospective snapshot bundles* generated
at closure. They do not prove 20 different historical execution timestamps.
"""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parent
STAGES=['R'+str(i) for i in range(1,11)]+['C'+str(i) for i in range(1,11)]
PARTIAL={'R6':'PARTIAL_DIFFERENT_AUTHOR_NOT_RUN',
         'C7':'PARTIAL_PRIVATE_OWNER_RUNTIME_NOT_RUN',
         'C8':'PARTIAL_SYNTHETIC_ONLY_NO_PRODUCTION_BENCH',
         'C9':'PARTIAL_DIFFERENT_AUTHOR_NOT_RUN'}
OBJECTIVES={
 'R1':'Freeze latest PR158 parent and one question',
 'R2':'CDMS 2011 archive and cross-repo source survey, raw bytes missing',
 'R3':'Typed execution graph and source-state physics distinction',
 'R4':'Finite path-cut theorem construction',
 'R5':'Guard-cut proof and source-state counterexample',
 'R6':'Same-context audit; distinct-author review not run',
 'R7':'Finite graph Wolfram and Python exhaustive check',
 'R8':'Scoped source-only scientific claim and no production admission',
 'R9':'Computation-ready finite graph cut and state equality contract',
 'R10':'Theory report and independent honest limits',
 'C1':'Pin selected owner, native He and REI pathways',
 'C2':'Inspect original firewall and code policy',
 'C3':'Define AST, graph and source byte contracts',
 'C4':'Construct conservative static witness and test protocol',
 'C5':'Implement source-state and guard graph tools',
 'C6':'Run 14 Python normal/-O and compileall tests',
 'C7':'Actual owner private raw and full local module not mounted',
 'C8':'Generate/inspect synthetic graph; real performance not measured',
 'C9':'Independent different author code review not run',
 'C10':'Freeze reports, tests, stage ZIPs, source ZIP and handoff',
}
INPUTS=['THEORY_KO.md','CODING_KO.md','REPORT_KO.md','SOURCE_SURVEY.json',
        'src/guard_graph.py','src/run_guard_audit.py','tests/test_guard_graph.py',
        'evidence/CALLGRAPH_RESULT.json','evidence/PYTHON_TESTS.log',
        'evidence/PYTHON_OPT_TESTS.log','evidence/RUN.log','HANDOFF_NEXT_THREAD_KO.md']
ALL_SOURCE=INPUTS+['evidence/GUARD_TOPOLOGY.png']
def sha(b):return hashlib.sha256(b).hexdigest()
def jsonbytes(x):return (json.dumps(x,indent=2,ensure_ascii=False,sort_keys=True)+'\n').encode('utf-8')
def zipwrite(z,n,data):
 info=zipfile.ZipInfo(n,date_time=(2026,10,29,12,0,0))
 info.compress_type=zipfile.ZIP_DEFLATED
 info.external_attr=0o644<<16
 z.writestr(info,data)

def write_archive(path,items):
 if path.exists(): raise FileExistsError(path)
 with zipfile.ZipFile(path,'x') as z:
  for name,data in sorted(items.items()):zipwrite(z,name,data)
 with zipfile.ZipFile(path) as z:
  bad=z.testzip()
  if bad:raise AssertionError(f'CRC failed: {bad}')
 return {'name':path.name,'size_bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'CRC':'PASS'}

def main():
 for name in ALL_SOURCE:
  assert (ROOT/name).is_file(),name
 stage_count=0;entries=[]
 for stage in STAGES:
  if stage not in PARTIAL:stage_count+=1
  data={name:(ROOT/name).read_bytes() for name in INPUTS}
  status={'schema':'REC_HD_CALLGRAPH_STAGE_V1', 'unit':'REC_HD_CALLGRAPH_SOURCESTATE01',
    'stage':stage,'objective':OBJECTIVES[stage],
    'stage_status':PARTIAL.get(stage,'COMPLETE_SCOPED'),
    'scoped_done_at_retrospective_order':stage_count,'scoped_total':20,
    'central_DAG':'28/88 (+0)','REC_physical_DAG':'0/313 (+0)',
    'parent_final_head':'ee78d209281c28ad7b8a9fe04a1634da80b7ad54',
    'retrospective_snapshot_not_time_of_step_computation':True,
    'publisher_upload_ack':'NOT_RUN_AT_STAGE_ARCHIVE_CREATION',
    'independent_author_review':'NOT_RUN',
    'physical':'HOLD'}
  (ROOT/'stages'/f'{stage}.json').write_bytes(jsonbytes(status))
  data['stage_status.json']=jsonbytes(status)
  data['FILE_SHA256.json']=jsonbytes({n:{'sha256':sha(d),'bytes':len(d)} for n,d in data.items()})
  archive=write_archive(ROOT/'stages'/f'REC_HD_CALLGRAPH_{stage}_20261029.zip',data)
  entries.append({'stage':stage,'status':status['stage_status'],
       'done':stage_count,'total':20,'objective':OBJECTIVES[stage],
       'local_snapshot':archive,'git_published':'NOT_VERIFIED',
       'drive_uploaded':'NOT_VERIFIED','dropbox_binary_uploaded':'NOT_VERIFIED',
       'canonical_DAG':'28/88','REC_physical_DAG':'0/313'})
 assert stage_count==16
 ledger={'schema':'REC_HD_CALLGRAPH_STAGE_LEDGER_V1',
         'unit':'REC_HD_CALLGRAPH_SOURCESTATE01',
         'source':'PRECOMPUTED_THIS_TURN_SOURCE_AND_RESULTS',
         'stage_snapshot_type':'RETROSPECTIVE_BUNDLES_NOT_TEMPORAL_SEPARATE_RESEARCH_EXECUTIONS',
         'stage_order':STAGES,'scoped_completed':16,'scoped_total':20,
         'partial':['R6','C7','C8','C9'],'canonical_DAG':'28/88 (+0)',
         'REC_physical_DAG':'0/313 (+0)',
         'production':'HOLD','entries':entries}
 (ROOT/'STAGE_LEDGER.json').write_bytes(jsonbytes(ledger))
 masterfiles=ALL_SOURCE+['STAGE_LEDGER.json','BUILD_DELIVERY.py']
 items={name:(ROOT/name).read_bytes() for name in masterfiles}
 for ent in entries:
  stage=ent['stage'];p=ROOT/'stages'/f'{stage}.json'; q=ROOT/'stages'/f'REC_HD_CALLGRAPH_{stage}_20261029.zip'
  items['stages/'+p.name]=p.read_bytes();items['stages/'+q.name]=q.read_bytes()
 items['MANIFEST.json']=jsonbytes({'schema':'REC_HD_CALLGRAPH_IMMUTABLE_ARCHIVE_MANIFEST_V1',
    'files':{n:{'sha256':sha(d),'bytes':len(d)} for n,d in items.items()},
    'parent':'ee78d209281c28ad7b8a9fe04a1634da80b7ad54',
    'private_LAMDA_or_CDMS_raw_included':False,
    'stage_archives_retrospective':True,'production':'HOLD'})
 master=write_archive(ROOT/'REC_HD_CALLGRAPH_SOURCESTATE01_20261029_FULL.zip',items)
 (ROOT/'delivery'/'LOCAL_ARCHIVE_ACK.json').write_bytes(jsonbytes({
   'schema':'REC_HD_CALLGRAPH_LOCAL_ARCHIVE_ACK_V1','master':master,
   'stage_files':len(entries),'stages_sha_crc_pass':len(entries),
   'current_source_git_published':'NOT_YET','cloud_upload':'NOT_YET',
   'canonical_DAG':'28/88 (+0)','REC_physical_DAG':'0/313 (+0)'}))
 print(json.dumps({'scoped_completed':stage_count,'stages':len(entries),'master':master},ensure_ascii=False))
if __name__=='__main__':main()

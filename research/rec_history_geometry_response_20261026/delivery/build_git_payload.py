#!/usr/bin/env python3
"""Prepare local Git connector payloads; performs no network access or Git mutation."""
import argparse,hashlib,json,shutil
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--unit-root',type=Path,default=Path(__file__).resolve().parents[1]);P.add_argument('--output',type=Path,required=True);P.add_argument('--decision-receipt',default=None);P.add_argument('--text-only',action='store_true');a=P.parse_args();u=a.unit_root.resolve();out=a.output.resolve()
if out.exists():raise SystemExit('Refusing existing output; choose a new snapshot directory')
prefix='research/rec_history_geometry_response_20261026/'
def info(b):return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()}
ident=json.loads((u/'inputs/SOURCE_IDENTITIES.json').read_text());entries=[];omitted=[];total_binary=0
for p in sorted(u.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc' or p.name=='S1_AUTHORIZED_LOCAL_ARCHIVE_RECEIPT.json':continue
 rel=p.relative_to(u).as_posix();b=p.read_bytes();i=info(b)
 if rel.startswith('inputs/') and p.suffix=='.npz':
  frozen=ident['files'][p.name]
  assert i['bytes']==frozen['bytes'] and i['sha256']==frozen['sha256'],rel
  if p.name=='history.npz':
   assert i['git_blob_sha1']=='de43b1a2642fa0aa049abbfd1b0a7d775d684b1b'
   entries.append({'repo_path':prefix+rel,'mode':'100644','type':'blob',**i,'source':'REUSE_EXISTING_BASE_BLOB_NO_UPLOAD'})
  else:omitted.append({'repo_path':prefix+rel,**i,'reason':'IMMUTABLE_INPUT_NOT_PRESENT_IN_BASE; RESTORE_FROM_FULL_S0; DO_NOT_UPLOAD_BINARY'})
  continue
 try:b.decode('utf-8');encoding='utf-8'
 except UnicodeDecodeError:encoding='base64'
 if encoding=='base64' and a.text_only:
  omitted.append({'repo_path':prefix+rel,**i,'reason':'COMPACT_OUTPUT_BINARY_RESTORE_FROM_FINAL_FULL_ZIP','final_archive_member':prefix+rel,'final_archive':'REC_HISTORY_GEO01_S2_FULL_PORTABLE_20261026.zip'});continue
 if encoding=='base64':
  if not (rel.startswith('results/') or rel.startswith('figures/')):raise SystemExit('Unclassified binary '+rel)
  if len(b)>2*1024*1024:raise SystemExit('Unexpected large output '+rel)
  total_binary+=len(b)
  if total_binary>16*1024*1024:raise SystemExit('New result/figure binary budget exceeded')
 entries.append({'repo_path':prefix+rel,'mode':'100644','type':'blob',**i,'source':'LOCAL_PAYLOAD','encoding':encoding,'relative_payload_path':prefix+rel})
for e in entries:
 if e['source']=='LOCAL_PAYLOAD':
  dst=out/'files'/e['relative_payload_path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(u/e['repo_path'].removeprefix(prefix),dst)
  assert info(dst.read_bytes())['sha256']==e['sha256']
plan={'schema':'GEO01_PORTABLE_GIT_PUBLICATION_PAYLOAD_V1','status':'PREPARED_LOCAL_ONLY_NOT_PUBLISHED','scientific_admission':'PENDING_ROOT_DECISION' if a.decision_receipt is None else {'explicit_root_receipt':a.decision_receipt,'requires_manual_review_before_publication':True},'repository':'cosmosapjw-quantum/rec_bianchi','branch':'research/rec-history-geometry-response-20261026','base_commit':'4a8e541030ee2cbd02e26ba671083b705d309d49','base_tree':'a937d4c5c75dea9023008aec3070fd2cbd2cabba','current_ref_observation':'NO_ACK_BRANCH_CREATION; ACTUAL_REF_HTTP404','remote_writes_performed':0,'entries':entries,'omitted_immutable_binary_inputs':omitted,'text_only':a.text_only,'compact_new_binary_bytes':total_binary,'restore_mapping':prefix+'delivery/INPUT_RESTORE_MAPPING.json','publication_sequence':['Re-read repository actual base and target ref; root reconcile any movement or parallel owner changes','If still absent create authorized new branch at pinned base; otherwise use observed expected SHA','Create missing blobs from exact local bytes; base64 binary content only for compact NEW results/figures; reuse existing history blob SHA','Create tree against verified actual base tree, add owned unit entries only; create commit; update target ref with expected-SHA and force=false','Read back actual HEAD/tree and verify all expected owned path blob identities and sizes before claiming publication','Open/update draft PR only after root result decision; no merge or activation','Central reconciliation is a separate repository and expected-SHA operation; preserve all other owners and pending gates']}
out.mkdir(parents=True,exist_ok=True)
if a.text_only:
 tree_entries=[]
 for e in entries:
  item={'path':e['repo_path'],'mode':'100644','type':'blob'}
  if e['source']=='REUSE_EXISTING_BASE_BLOB_NO_UPLOAD':item['sha']=e['git_blob_sha1']
  else:item['content']=(out/'files'/e['relative_payload_path']).read_text()
  tree_entries.append(item)
 (out/'TEXT_ONLY_TREE_ENTRIES.json').write_text(json.dumps(tree_entries,ensure_ascii=False)+'\n')
(out/'GIT_PUBLICATION_PAYLOAD.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'output':str(out),'entries':len(entries),'local_payloads':sum(e['source']=='LOCAL_PAYLOAD' for e in entries),'reused_history_blobs':1,'omitted_binary_files':len(omitted),'new_binary_bytes':total_binary,'remote_writes':0},indent=2))

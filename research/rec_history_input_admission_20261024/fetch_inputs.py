"""Read-only immutable input download; scientific computations are separate."""
import hashlib,json,time,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE='https://raw.githubusercontent.com/cosmosapjw-quantum/rec_bianchi/93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa/'
FILES=[
 ('h2_u4.npz','research/rec_r3i_time_refinement_20261016/h2_u4_post_saha_exit_001/ncp_run_001/python_u4_exit.npz',9645700,'7ad1476c78d08218e42ac616dc43d03dd8eb232c44bfb66a8f20a237dcce6943','f8e52e123f1e80234f221f0eec371746884225ec'),
 ('h4_r3q_event.npz','research/rec_r3q_h4_continuation_20261020/ncp_event_001/python_continuation.npz',7390437,'7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9','d91967045a484c5d164edf6c051e01dab57f7dbc')]

def main():
 (ROOT/'inputs').mkdir(exist_ok=True)
 records=[]
 for name,path,size,sha,blob in FILES:
  target=ROOT/'inputs'/name
  begin=time.monotonic()
  if target.exists():
   data=target.read_bytes();method='existing_local_bytes'
  else:
   with urllib.request.urlopen(BASE+path,timeout=45) as response:
    data=response.read(size+1)
   method='GET_immutable_GitHub_raw'
  actual=hashlib.sha256(data).hexdigest()
  git=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if len(data)!=size or actual!=sha or git!=blob:
   raise RuntimeError(f'INPUT_IDENTITY_MISMATCH {name}')
  if not target.exists():
   with target.open('xb') as output:output.write(data)
  records.append(dict(path=path,local_path='inputs/'+name,sha256=actual,git_blob=git,bytes=len(data),method=method,wall_seconds=time.monotonic()-begin))
 (ROOT/'INPUT_TRANSFER_RECEIPT.json').write_text(json.dumps(records,indent=2)+'\n')
 print(json.dumps(records,indent=2))

if __name__=='__main__':main()

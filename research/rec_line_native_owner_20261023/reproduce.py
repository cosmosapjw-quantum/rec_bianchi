"""Reproduce LINE02 only in a new copy; delivered results are immutable."""
from pathlib import Path
import argparse,hashlib,os,shutil,subprocess,sys,tempfile
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');a=ap.parse_args()
 root=Path(__file__).resolve().parent
 target=Path(tempfile.mkdtemp(prefix='rec_line02_repro_'))/'unit'
 shutil.copytree(root,target,ignore=shutil.ignore_patterns('results','figures','evidence','__pycache__','*.pyc'))
 (target/'results').mkdir();(target/'figures').mkdir()
 expected={'inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv':'3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7','vendor/original_hyrec_physical_flux.py':'37e00dd8224ddd4d5cec7b2b78c689893996e499b944f38302c5dcc104b61e9f','code/escape_moments.py':'f8a91ddad8833d4c0079025af81fb8df4b9423da3d87a8363093603922da0c2e','vendor/hyrec_spike_transfer.py':'3d03c35299d529ecaac66f40f5fc78f14ec3099c057005762f112250ee19add9'}
 for name,sha in expected.items():
  if hashlib.sha256((target/name).read_bytes()).hexdigest()!=sha:raise ValueError('immutable input mismatch:'+name)
 print('Fresh unit:',target,flush=True)
 if a.prepare_only:
  print('Input verification PASS; scientific execution NOT_RUN');return
 env=os.environ.copy()
 for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[name]='1'
 done=subprocess.run([sys.executable,'code/run_line02.py'],cwd=target,env=env,timeout=180)
 raise SystemExit(done.returncode)
if __name__=='__main__':main()


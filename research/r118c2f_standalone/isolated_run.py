"""Self-contained test using only REC Python source, REC executable and
an archive containing the exact three immutable atomic table members.
No source C code, original history, v050 network, BASS, or HyRec executable
in the staged input tree. This is an isolated input/cwd test, not an OS
security sandbox. Native binary itself is built by the REC crate."""
import argparse,pathlib,shutil,zipfile,json,hashlib,os,subprocess,sys
P=pathlib.Path
p=argparse.ArgumentParser();p.add_argument('--rec',type=P,required=True);p.add_argument('--binary',type=P,required=True);p.add_argument('--out',type=P,required=True);a=p.parse_args()
root=a.out.resolve();root.mkdir(exist_ok=False);rec=a.rec.resolve()
shutil.copytree(rec/'src',root/'src',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
binary=root/'rec_live_line';shutil.copy2(a.binary,binary)
src=rec/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip';table=root/'atomic_rates.zip'
members=['HyRec/Alpha_inf.dat','HyRec/R_inf.dat','HyRec/two_photon_tables.dat']
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
with zipfile.ZipFile(src) as z,zipfile.ZipFile(table,'x',compression=zipfile.ZIP_DEFLATED) as o:
    for n in members:o.writestr(n,z.read(n))
with zipfile.ZipFile(table) as z:
    assert z.namelist()==members
    hashes={n:hashlib.sha256(z.read(n)).hexdigest() for n in members}
env=dict(os.environ,PYTHONPATH=str(root/'src'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',RAYON_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
# Instrument subprocess launch and explicit path I/O through a Python
# audit hook. No filesystem sandbox claim; whitelist the only executable
# the standalone pipeline invokes and the sole source data archive.
driver=root/'driver.py'
driver.write_text("""import sys,os,pathlib,runpy
root=pathlib.Path(__file__).resolve().parent
def guard(event,args):
    if event=='subprocess.Popen':
        assert pathlib.Path(args[0]).resolve()==root/'rec_live_line',(event,args[0])
    if event=='open':
        try:p=pathlib.Path(args[0]).resolve()
        except (TypeError,ValueError):return
        if p.suffix in ('.npz','.zip','.tsv','.json','.dat','.case','.txt'):
            if 'site-packages' not in str(p) and not p.is_relative_to(root):
                raise RuntimeError('external data read: '+str(p))
sys.addaudithook(guard)
sys.argv=sys.argv[1:]
runpy.run_module('full_bianchi_hyrec.standalone_line',run_name='__main__')
""")
cmd=[sys.executable,str(driver),'standalone_line','--rates',str(table),'--binary',str(binary),'--out',str(root/'result'),'--subcells','4','--workers','4','--duration','100','--steps','4','--initial','radiation','--exterior']
proc=subprocess.run(cmd,cwd=root,env=env,capture_output=True,text=True,timeout=240)
(root/'stdout.txt').write_text(proc.stdout);(root/'stderr.txt').write_text(proc.stderr)
if proc.returncode:raise RuntimeError(proc.stderr)
r=json.loads((root/'result/RECEIPT.json').read_text())
receipt=dict(status='PASS_ISOLATED_INPUT_TREE',scope='REC HMLA + source compiler + scalar live line',command=cmd,table_members=hashes,table_archive_sha256=sha(table),binary_sha256=sha(binary),result_receipt_sha256=sha(root/'result/RECEIPT.json'),source_state=r['state'],audit='Python audit hook: external data reads denied; subprocess executable restricted to REC native bin',result_hashes=r['hashes'])
(root/'ISOLATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],r['state'],flush=True)

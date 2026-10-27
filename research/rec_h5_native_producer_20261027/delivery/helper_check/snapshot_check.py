#!/usr/bin/env python3
"""Single mechanical dummy snapshot check; no scientific execution."""
import hashlib,json,os,resource,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(5,6))
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
start=time.perf_counter()
helper=Path(__file__).resolve().parents[1]/'prepare_stage.py'
owned='research/rec_h5_native_producer_20261027'
with tempfile.TemporaryDirectory(prefix='rec_h5_packaging_') as temp:
    root=Path(temp); repo=root/'repo'; unit=repo/owned
    (unit/'stages').mkdir(parents=True)
    sources={
      owned+'/stages/R1.json':b'{"stage":"R1","authored_by":"dummy-parent"}\n',
      owned+'/exact.py':b'# exact CRLF\r\nx = 1\r\n',
      owned+'/large.csv':b'x'*(2*1024*1024+1),
      owned+'/figure.pdf':b'%PDF-dummy\x00\xff',
      owned+'/nul.txt':b'not transferable\x00',
      owned+'/lamda_hd_live.dat':b'external dummy input',
      owned+'/archive.zip':b'archive exact dummy',
      owned+'/cache/__pycache__/dummy.pyc':b'known cache dummy'}
    for relative,data in sources.items():
      p=repo/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    command=[sys.executable,str(helper),'R1',owned,'--source-head','d6dbe39a4923439547c01695d9020ba39367ea90','--repo',str(repo),'--workspace',str(root),'--git-exclude',owned+'/exact.py']
    completed=subprocess.run(command,text=True,capture_output=True,check=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
    report=json.loads(completed.stdout)
    manifest=json.loads(Path(report['manifest']).read_text())
    payload=json.loads(Path(report['payload']).read_text())
    binaries=json.loads(Path(report['binary_manifest']).read_text())['files']
    cache=owned+'/cache/__pycache__/dummy.pyc'
    with zipfile.ZipFile(report['archive']) as z:
      assert set(z.namelist())==set(sources)-{cache}|{'SNAPSHOT_MANIFEST.json'}
      assert all(z.read(p)==b for p,b in sources.items() if p!=cache)
    assert {r['path'] for r in manifest['files']}==set(sources)-{cache}
    assert {r['path'] for r in payload}=={owned+'/stages/R1.json'}
    assert len(manifest['omitted'])==1 and manifest['omitted'][0]['path']==cache
    assert len(binaries)==5
    assert next(r for r in binaries if r['path'].endswith('lamda_hd_live.dat'))['git_blob_allowed'] is False
    assert manifest['provider_status']=='PREPARED_ONLY_NO_ACK_INFERRED'
    result={'scope':'single dummy snapshot: exact CRLF/source, >2MiB, figure, NUL binary, raw LAMDA, archive, Git-only exclusion, known cache','status':'PASS','source_baseline':'research/rec_source_synthesis_20261027/delivery/prepare_stage.py','helper_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'helper_report':{k:v for k,v in report.items() if k in ('packaging_cpu_s','packaging_wall_s','packaging_max_rss_kib','files','git_files','binary_artifact_count','omitted_count','zip_crc_and_manifest_sha')},'test_plus_child_cpu_s':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime+resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime,'wall_s':time.perf_counter()-start,'max_rss_kib':max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss),'threads':1,'memory_cap_bytes':512*1024**2,'scientific_execution':False,'remote_mutations':False,'unmeasured_preparation_and_receipt_tail':'UNKNOWN_NOT_ZERO'}
    (Path(__file__).parent/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

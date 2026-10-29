from pathlib import Path
import json,zipfile,hashlib
p=Path(__file__).resolve().parent
b=p.parent/'REC_HD_RECOIL_ONLY_BOUND_SOURCE_20261029.zip'
files={}
for f in p.rglob('*'):
 if not f.is_file():continue
 if '__pycache__' in f.parts or f.suffix=='.pyc' or f.name=='recoil_crosscheck':continue
 if f.name=='MANIFEST_SHA256.json':continue
 files[str(f.relative_to(p))]=f.read_bytes()
for f in p.parent.glob('REC_HD_*20261029.zip'):
 if f.name==b.name:continue
 if f.name not in ('REC_HD_CDMS_V2_SOURCE_RECON_20261029.zip','REC_HD_NATIVE_POLICY_FIREWALL_20261029.zip'):continue
 files['predecessor/'+f.name]=f.read_bytes()
manifest={'schema':'REC_HD_RECOIL_SOURCE_V1','note':'Frozen public selected source fields and prior non-CDMS source-only ZIPs; NO original private LAMDA/CDMS raw bytes',
'members':{name:{'sha256':hashlib.sha256(v).hexdigest(),'size':len(v)} for name,v in sorted(files.items())}}
(p/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
files['MANIFEST_SHA256.json']=(p/'MANIFEST_SHA256.json').read_bytes()
with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for name,content in sorted(files.items()):z.writestr(name,content)
with zipfile.ZipFile(b) as z:
 assert z.testzip() is None
 for name,x in manifest['members'].items():
  raw=z.read(name)
  assert len(raw)==x['size'] and hashlib.sha256(raw).hexdigest()==x['sha256'],name
h=hashlib.sha256(b.read_bytes()).hexdigest()
(b.parent/(b.name+'.sha256')).write_text(f'{h}  {b.name}\n')
print(json.dumps({'file':str(b),'size':b.stat().st_size,'sha256':h,'members':len(files),'CRC_manifest':'PASS'}))

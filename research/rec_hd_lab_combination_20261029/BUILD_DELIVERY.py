"""Create immutable original-source-inclusive archive with a content manifest.

No on-line source downloaded here; all source roles stay explicit.
"""
from __future__ import annotations
from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parent
ZIP_NAME='REC_HD_LAB_COMBINATION_20261029_SOURCE.zip'
EXCLUDE={'BUILD_DELIVERY.py'}  # script itself included explicitly below

def digest(data):return hashlib.sha256(data).hexdigest()

def build():
    files={p.relative_to(ROOT).as_posix():p.read_bytes() for p in ROOT.rglob('*') if p.is_file() and p.suffix not in ('.pyc',) and '__pycache__' not in p.parts and p.name!=ZIP_NAME and p.parent!=ROOT/'delivery' and '.DS_Store' not in p.name}
    assert len(files)>=40 and 'sources/PR159_PARENT_SOURCE_IMMUTABLE.zip' in files
    assert digest(files['sources/PR159_PARENT_SOURCE_IMMUTABLE.zip'])=='cdcbfbd1f5249ccdaf5d8a108d490431701febffbb3e6433e9c711e3ad8d035e'
    manifest={'schema':'REC_HD_LAB_IMMUTABLE_SOURCE_MANIFEST_V1','entries':{k:{'sha256':digest(v),'bytes':len(v)} for k,v in sorted(files.items())},'no_CDMS_2011_v2_original_raw':True,'no_LAMDA_2021_original_raw':True,'original_parent_included_byte_identical':True}
    files['MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    out=ROOT/ZIP_NAME
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,contents in sorted(files.items()):
            zi=zipfile.ZipInfo(name,date_time=(2026,10,29,12,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o644<<16
            z.writestr(zi,contents,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        m=json.loads(z.read('MANIFEST.json'))
        for name,e in m['entries'].items():assert digest(z.read(name))==e['sha256'] and len(z.read(name))==e['bytes']
    return {'source_zip':out.name,'bytes':out.stat().st_size,'sha256':digest(out.read_bytes()),'entries':len(files),'payload_sha_pass':len(files)-1,'crc':'PASS'}

if __name__=='__main__':print(json.dumps(build(),indent=2))

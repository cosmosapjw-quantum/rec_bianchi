"""Fetch byte-authentic official source bytes in a network-capable environment.

No request is made on import. No substitute version is accepted. Destination is
local only; this script does not modify remote repos or production inputs.
"""
import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]

def fetch(path: Path, names: list[str]):
    lock=json.loads((HERE/'input/ORIGINAL_SOURCE_LOCK.json').read_text())['model_sources']
    path.mkdir(parents=True,exist_ok=True)
    out=[]
    for name in names:
        ent=lock[name]
        p=path/name
        if p.exists():
            bb=p.read_bytes()
        else:
            with urllib.request.urlopen(ent['url'],timeout=60) as response:
                bb=response.read()
        actual=hashlib.sha256(bb).hexdigest()
        if actual!=ent['sha256'] or len(bb)!=ent['size_bytes']:
            raise ValueError(f'Authenticity failed {name}: size={len(bb)} SHA256={actual}')
        if 'md5' in ent and hashlib.md5(bb).hexdigest()!=ent['md5']:
            raise ValueError(f'Official MD5 mismatch: {name}')
        if not p.exists():p.write_bytes(bb)
        out.append({'name':name,'sha256':actual,'bytes':len(bb),'path':str(p)})
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=HERE/'source_originals_downloaded')
    ap.add_argument('--names',nargs='+',help='One or more exact keys in input/ORIGINAL_SOURCE_LOCK.json')
    args=ap.parse_args()
    keys=args.names or list(json.loads((HERE/'input/ORIGINAL_SOURCE_LOCK.json').read_text())['model_sources'])
    print(json.dumps(fetch(args.out,keys),indent=2))

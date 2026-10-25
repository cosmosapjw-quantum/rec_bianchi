"""Serialization, exact immutable source binding, and portable path resolution."""
from pathlib import Path
import hashlib, json, sys
import numpy as np
UNIT=Path(__file__).resolve().parents[1]
WORK=UNIT.parents[1]

def serial(value):
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, Path): return str(value)
    raise TypeError(type(value).__name__)

def save(path, obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,default=serial,allow_nan=False)+'\n')

def identity(path):
    p=Path(path); data=p.read_bytes()
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

def defaults():
    sibling=UNIT.parent/'rec_history_thermo_20261024'
    thermo=sibling if sibling.is_dir() else WORK/'inputs/thermo_s2/research/rec_history_thermo_20261024'
    return thermo,WORK/'inputs/pr05b2_source_history_v060.npz',WORK/'inputs/thermo_s2/baseline/research/rec_history_response_20261024/results/primary001/QUERY_RESPONSE_COEFFICIENTS.csv'

def files(thermo,history,query):
    paths={}
    snap=json.loads((thermo/'evidence/execution/PREPARED_SOURCE_SNAPSHOT.json').read_text())
    for name in snap['source_snapshot']: paths['thermo/'+name]=thermo/name
    retained=json.loads((thermo/'inputs/INPUT_IDENTITIES.json').read_text())
    for item in retained['files']: paths['thermo/'+item['path']]=thermo/item['path']
    for name in ('inputs/INPUT_IDENTITIES.json','code/source.py','code/scalar.py','code/inputs.py','results/primary001/BASE_COEFFICIENTS.npz','results/primary001/ANALYTIC_RESPONSE.npz','provenance/source_intake/SOURCE_HISTORY_PROVENANCE.json','provenance/source_intake/ORIGINAL_NATIVE_HISTORY_LEAD.json'):
        paths['thermo/'+name]=thermo/name
    paths.update({'history':history,'query_map':query})
    for p in sorted((UNIT/'code').glob('*.py')): paths['unit/code/'+p.name]=p
    for p in sorted((UNIT/'tests').glob('*.py')): paths['unit/tests/'+p.name]=p
    return paths

def verify(thermo,history,query):
    expected=json.loads((UNIT/'inputs/EXACT_IDENTITIES.json').read_text())
    snap=json.loads((thermo/'evidence/execution/PREPARED_SOURCE_SNAPSHOT.json').read_text())
    if snap['canonical_snapshot_sha256']!='adddf7381edfb7d670025c651cf813594107a260acce308702f33b1d415fad54': raise ValueError('CANONICAL_23_SNAPSHOT_IDENTITY')
    for name,item in snap['source_snapshot'].items():
        if identity(thermo/name)!=item: raise ValueError('CANONICAL_23_MEMBER:'+name)
    actual={name:identity(p) for name,p in files(thermo,history,query).items()}
    if actual!=expected['files']: raise ValueError('EXACT_SOURCE_OR_INPUT_IDENTITY_MISMATCH')
    sys.path.insert(0,str(thermo/'code'))
    import inputs as retained_inputs
    retained_inputs.verify_inputs(thermo)
    return retained_inputs.load(thermo),actual

"""Deterministic value-only generated copy. Original source is never changed."""
from pathlib import Path
import difflib
import hashlib
import json

ORIGINAL_SHA='421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b'

def generate(unit, out=None):
    unit=Path(unit)
    original=unit/'inputs/original/HyRec/hydrogen.c'
    source=original.read_bytes()
    assert hashlib.sha256(source).hexdigest()==ORIGINAL_SHA,'IMMUTABLE_HYDROGEN_MISMATCH'
    changes=[
      (b'#include "hydrogen.h"',b'#include "hydrogen.h"\n#include "observer.h"'),
      (b'     alpha[0] = updiag[0] / diag[0];',b'     ef_observe(1, 0, diag[0]);\n     alpha[0] = updiag[0] / diag[0];'),
      (b'         denom = diag[i] - dndiag[i] * alpha[i-1];',b'         denom = diag[i] - dndiag[i] * alpha[i-1];\n         ef_observe(2, i, denom);'),
      (b'   det = Trr_new[0][0] * Trr_new[1][1] - Trr_new[0][1] * Trr_new[1][0];',b'   det = Trr_new[0][0] * Trr_new[1][1] - Trr_new[0][1] * Trr_new[1][0];\n   ef_observe(4, 0, det);')]
    result=source
    for before,after in changes:
        assert result.count(before)==1,'SOURCE_OBSERVER_ANCHOR_MISMATCH'
        result=result.replace(before,after)
    restored=result
    for before,after in reversed(changes):
        assert restored.count(after)==1
        restored=restored.replace(after,before)
    assert restored==source,'OBSERVER_REMOVAL_NOT_EXACT'
    out=Path(out) if out is not None else unit/'build'
    out.mkdir(parents=True,exist_ok=True)
    (out/'hydrogen_observed.c').write_bytes(result)
    patch=''.join(difflib.unified_diff(source.decode().splitlines(True),result.decode().splitlines(True),fromfile='inputs/original/HyRec/hydrogen.c',tofile='build/hydrogen_observed.c'))
    (out/'OBSERVATION.diff').write_text(patch)
    receipt={'original_sha256':ORIGINAL_SHA,'generated_sha256':hashlib.sha256(result).hexdigest(),'native_body_value_hooks':3,'observation_header_insertions':1,'removing_insertions_restores_original_bytes':True,'original_bytes':len(source),'generated_bytes':len(result),'extra_native_solves':0}
    (out/'GENERATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt

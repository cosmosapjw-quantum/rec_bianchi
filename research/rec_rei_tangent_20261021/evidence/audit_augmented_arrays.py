"""Small independent layout and initial-map checks. No solve_ivp call."""
import os
import sys
import hashlib
import json
import math
from pathlib import Path

os.environ['OPENBLAS_NUM_THREADS'] = '1'
sys.dont_write_bytecode = True
root = Path('/workspace/scratch/36ad4bc67b35/rec_bianchi/research/rec_rei_tangent_20261021')
sys.path.insert(0, str(root / 'code'))
import numpy as np
from augmented import SEED_SCALES, default_grid
from owner_model import make_model
from tangent_core import TangentOperator

z = np.arange(120, dtype=float).reshape(40, 3)/31
combined = np.r_[np.arange(40, dtype=float), (z*SEED_SCALES).reshape(-1)]
restored = combined[40:].reshape(40, 3)/SEED_SCALES
sol_y = np.stack([combined, combined*2, combined*3], axis=1)
t = sol_y[40:].T.reshape(3, 40, 3)/SEED_SCALES
checks = {
    'initial_vector_shape_160': combined.shape == (160,),
    'single_sample_column_roundtrip': bool(np.allclose(restored, z, rtol=2e-16, atol=0)),
    'multi_sample_column_roundtrip': bool(np.allclose(t, np.stack([z, 2*z, 3*z]), rtol=3e-16, atol=0)),
    'default_grid_153_strict_samples': len(default_grid()) == 153 and bool(np.all(np.diff(default_grid()) > 0)),
    'default_join_120': bool(default_grid()[120] == math.log(21/5)),
    'default_endpoint_log7': bool(default_grid()[-1] == math.log(7)),
    'number_indices': [4+9, 4+3*9],
    'unscaled_atol_terms': (3e-13/SEED_SCALES).tolist(),
    'models': [],
    'new_ODE_solves': 0,
    'benchmark': 0,
    'review_helper_correction': 'First inline helper completed array/model calculations but JSON serialization failed on numpy.bool_. Explicit Python bool conversion fixes only reviewer evidence serialization; no product code or scientific solve was involved.',
}
manifest = json.loads((root/'inputs/NCP_TANGENT_CASES.json').read_text())
for row in manifest['cases']:
    model, seed = make_model(*row['axes'])
    p = TangentOperator(model).prepare(0, model.initial_state())
    checks['models'].append({
        'id': row['id'], 'axes': row['axes'],
        'A': seed.amplitude, 'k': seed.radiation_seed,
        'inside_parameter_domain': -1 < seed.amplitude < 2 and abs(seed.radiation_seed) < .5,
        'number_monopoles_initial': model.initial_state()[[13,31]].tolist(),
        'number_monopole_tangent_initial': seed.initial_tangents[[13,31]].tolist(),
        'initial_signed_observables': p.observables_signed[:3].tolist(),
        'initial_observable_seed_identity_error': float(np.max(abs(p.observable_jvp(seed.initial_tangents, seed.amplitude_gradient)[:3]-np.eye(3)))),
    })
checks['file_sha256'] = {n: hashlib.sha256((root/n).read_bytes()).hexdigest() for n in (
    'code/augmented.py', 'code/verify_wiring.py', 'inputs/NCP_TANGENT_CASES.json')}
assert all(checks[n] for n in ('initial_vector_shape_160','single_sample_column_roundtrip',
    'multi_sample_column_roundtrip','default_grid_153_strict_samples','default_join_120','default_endpoint_log7'))
assert all(m['inside_parameter_domain'] and m['initial_observable_seed_identity_error'] < 5e-11 for m in checks['models'])
out = Path(__file__).with_name('C9_AUGMENTED_ARRAY_CHECKS.json')
out.write_text(json.dumps(checks, indent=2)+'\n')
print(json.dumps(checks, indent=2))

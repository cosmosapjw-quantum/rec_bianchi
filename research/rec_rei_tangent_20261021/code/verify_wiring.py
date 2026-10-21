"""One small synthetic parent/augmented pair; no historical case rerun."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import time

import numpy as np
from scipy.integrate import solve_ivp

from augmented import integrate_case
from owner_model import make_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    receipt_path = args.output/'TINY_WIRING.json'
    if receipt_path.exists():
        raise FileExistsError('Preserve existing wiring receipt; select a new diagnostic output.')
    axes = (.002, .00007, -.0002)
    grid = np.array([0., .00005, .0001])
    model, _ = make_model(*axes)
    started = time.monotonic()
    parent = solve_ivp(model.rhs, (0., float(grid[-1])), model.initial_state(),
                       method='DOP853', rtol=3e-11, atol=3e-13, t_eval=grid)
    parent_wall = time.monotonic()-started
    parent_reached = bool(parent.success and np.array_equal(parent.t, grid)
                          and parent.y.shape == (40, len(grid)))
    if not parent_reached:
        receipt = {'status': 'FAIL_PARENT', 'new_ODE_solves': 1,
                   'parent_IVP': {'success': bool(parent.success),
                                  'message': str(parent.message),
                                  'nfev': int(parent.nfev), 'worker_wall_s': parent_wall},
                   'parent_state_scaled_difference': None,
                   'checks': {'parent_reached_requested_grid': False},
                   'new_augmented_IVP': 0}
        receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False)+'\n')
        print(json.dumps(receipt, indent=2, allow_nan=False))
        return 1
    arrays, receipt = integrate_case(axes, grid)
    difference = float(np.max(abs(arrays['raw_y']-parent.y.T)/(1+abs(parent.y.T))))
    receipt['parent_IVP'] = {'success': bool(parent.success), 'nfev': int(parent.nfev),
                             'worker_wall_s': parent_wall}
    receipt['parent_state_scaled_difference'] = difference
    receipt['checks']['parent_IVP_success'] = bool(parent.success)
    receipt['checks']['parent_state_agreement'] = difference <= 2e-11
    receipt['status'] = 'PASS_SCOPED_WIRING' if all(receipt['checks'].values()) else 'FAIL'
    receipt['new_ODE_solves'] = 2
    receipt['scope'] = 'synthetic interior seed, x0 to1e-4, 3 output nodes; no z20to2 sensitivity solve'
    np.savez_compressed(args.output/'TINY_WIRING.npz', **arrays, parent_raw_y=parent.y.T)
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False)+'\n')
    print(json.dumps(receipt, indent=2, allow_nan=False))
    return 0 if receipt['status']=='PASS_SCOPED_WIRING' else 1


if __name__ == '__main__':
    raise SystemExit(main())

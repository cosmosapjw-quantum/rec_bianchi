"""Three scaled forward tangents of the pinned 40-state collisionless RHS.

The new 160-state IVP carries the parent state and three derivative columns.
The optional NCP run uses new interior seeds; it does not enqueue the old pilot.
"""
from __future__ import annotations

import math
import platform
import resource
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from owner_model import make_model, verify_source
from tangent_core import TangentOperator

SEED_SCALES = np.array([.1, .0003, .001])
SEED_SCALES.flags.writeable = False


def default_grid():
    """The historical redshift output grid, applied to a new augmented IVP."""
    join = math.log(21 / 5)
    return np.r_[np.linspace(0., join, 121), np.linspace(join, math.log(7), 33)[1:]]


def integrate_case(axes, x_grid=None, rtol=3e-11, atol=3e-13, case_seconds=120.):
    """Return scientific arrays and a truthful scoped execution receipt.

    V[:,j] = dy/dtheta_j * SEED_SCALES[j] is integrated. Equal absolute
    tolerances then refer to a natural finite perturbation scale, not to
    derivatives with very different magnitudes. Returned derivatives are
    unscaled. This is solver local error control, not a global error bound.
    """
    started = time.monotonic()
    cpu_start = time.process_time()
    if not all(math.isfinite(v) and v > 0 for v in (rtol, atol, case_seconds)):
        raise ValueError('POSITIVE_FINITE_SOLVER_TOLERANCE_AND_BUDGET_REQUIRED')
    model, seed = make_model(*axes)
    op = TangentOperator(model)
    raw_grid = default_grid() if x_grid is None else np.asarray(x_grid)
    if np.iscomplexobj(raw_grid):
        raise ValueError('REAL_TIME_GRID_REQUIRED')
    grid = np.asarray(raw_grid, dtype=float)
    if (grid.ndim != 1 or len(grid) < 2 or not np.isfinite(grid).all()
            or grid[0] != 0 or not np.all(np.diff(grid) > 0)
            or grid[-1] > math.log(7)):
        raise ValueError('STRICT_TIME_GRID_FROM_ZERO_TO_AT_MOST_LOG7_REQUIRED')
    initial = np.r_[model.initial_state(),
                    (seed.initial_tangents * SEED_SCALES).reshape(-1)]
    a_direction = seed.amplitude_gradient * SEED_SCALES
    calls = 0

    def rhs(x, combined):
        nonlocal calls
        calls += 1
        if time.monotonic() - started > case_seconds:
            raise TimeoutError('TANGENT_CASE_TIME_BUDGET_EXHAUSTED')
        prepared = op.prepare(x, combined[:40])
        response = prepared.jvp(combined[40:].reshape(40, 3), a_direction)
        return np.r_[prepared.rhs, response.reshape(-1)]

    sol = solve_ivp(rhs, (0., float(grid[-1])), initial, method='DOP853',
                    rtol=rtol, atol=atol, t_eval=grid)
    reached = bool(sol.success and np.array_equal(sol.t, grid))
    if not reached:
        raise RuntimeError('TANGENT_IVP_DID_NOT_REACH_REQUESTED_GRID:' + sol.message)
    state = sol.y[:40].T.copy()
    scaled = sol.y[40:].T.reshape(len(grid), 40, 3).copy()
    tangent = scaled / SEED_SCALES
    observed, observed_tangent, local_rhs_error = [], [], []
    for i, x in enumerate(grid):
        prepared = op.prepare(float(x), state[i])
        observed.append(prepared.observables_signed)
        observed_tangent.append(prepared.observable_jvp(tangent[i], seed.amplitude_gradient))
        if i in (0, len(grid)-1):
            original = model.rhs(float(x), state[i])
            local_rhs_error.append(float(np.max(abs(original-prepared.rhs)/(1+abs(original)))))
    observed = np.stack(observed)
    observed_tangent = np.stack(observed_tangent)
    checks = {
        'solver_success_and_requested_grid': reached,
        'finite_state_and_tangents': bool(np.isfinite(sol.y).all()),
        'finite_observables_and_tangents': bool(np.isfinite(observed).all()
                                              and np.isfinite(observed_tangent).all()),
        'initial_signed_axes': bool(np.max(abs(observed[0, :3]-np.array(seed.axes))) <= 5e-12),
        'initial_observable_seed_identity': bool(np.max(abs(observed_tangent[0, :3]-np.eye(3))) <= 5e-11),
        'signed_component_sum': bool(np.array_equal(observed[:, 3], observed[:, 1]+observed[:, 2])),
        'tangent_component_sum': bool(np.array_equal(observed_tangent[:, 3], observed_tangent[:, 1]+observed_tangent[:, 2])),
        'number_monopoles': bool(np.max(abs(state[:, [13,31]]-1.)) <= 5e-11),
        'number_monopole_tangents': bool(np.max(abs(tangent[:, [13,31]])) <= 5e-10),
        'inert_thermal_coordinate': bool(np.array_equal(state[:, 3], np.zeros(len(grid)))),
        'original_RHS_at_start_and_end': bool(max(local_rhs_error) <= 2e-13),
    }
    arrays = {
        'axes': np.asarray(seed.axes), 'x': grid, 'z': 21*np.exp(-grid)-1,
        'raw_y': state, 'state_tangent': tangent, 'scaled_state_tangent': scaled,
        'seed_scales': SEED_SCALES, 'amplitude_gradient': seed.amplitude_gradient,
        'observables_signed': observed, 'observables_norm': abs(observed),
        'observable_tangent_signed': observed_tangent,
    }
    receipt = {
        'schema': 'rec.tangent.execution.v1',
        'status': 'COMPLETED' if all(checks.values()) else 'FAILED_VALIDATION',
        'axes': list(seed.axes), 'checks': checks,
        'source_commit': verify_source(), 'method': 'DOP853', 'rtol': rtol, 'atol': atol,
        'seed_scales': SEED_SCALES.tolist(), 'state_size': 40, 'augmented_size': 160,
        'epochs': len(grid), 'x_interval': [0., float(grid[-1])],
        'redshift_interval': [20., float(arrays['z'][-1])],
        'nfev': int(sol.nfev), 'prepared_rhs_calls': calls,
        'max_start_end_rhs_scaled_difference': max(local_rhs_error),
        'worker_wall_s': time.monotonic()-started, 'worker_cpu_s': time.process_time()-cpu_start,
        'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'new_augmented_IVP': 1, 'benchmark': 0,
        'physical': 'HOLD', 'global_convergence': 'NOT_RUN', 'production': 'NOT_APPROVED',
    }
    return arrays, receipt

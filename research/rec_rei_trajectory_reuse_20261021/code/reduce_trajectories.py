#!/usr/bin/env python3
"""Read-only, source-bound anchored comparison at common redshift; no IVP."""
from __future__ import annotations
import os
for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
              'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_name] = '1'
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import resource
import time
import numpy as np

SIGMAS = (0., .0003, .001, .003, .01, .03, .1)
MATTER = (-.0003, -.0001, 0., .0001, .0003)
RADIATION = (-.001, -.0003, 0., .0003, .001)
FIELDS = ('S_F_signed', 'P_m_F_signed', 'P_r_F_signed')
SOURCE_COMMIT = '3b85dedce84d37b3e165da00685a8a984950aafe'
MANIFEST_SHA256 = '4f7e599ad9f082be59cbe2203a8b55b7bd9cb21fec9fde55a41afe53b9444853'
KAPPA_T = 8 * math.pi * 6.67430e-11 / 299792458.**2


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def coordinate(config):
    return (float(config['Sigma_F_i']), float(config.get('P_m_i', 0.)),
            float(config.get('P_r_i', config['Pi_F_signed_i'])))


def reconstruct(axes, values):
    """Only nominal m=0 or r=0 rows can feed the predictor.

    axes:(case,3); values:(case,epoch,observable). Full Cartesian grids with
    a zero anchor on both component axes are required. No norm is used here.
    """
    if np.iscomplexobj(axes) or np.iscomplexobj(values):
        raise ValueError('REAL_INPUT_REQUIRED')
    axes = np.asarray(axes, dtype=float)
    values = np.asarray(values, dtype=float)
    if axes.ndim != 2 or axes.shape[1] != 3 or values.ndim != 3 or len(values) != len(axes):
        raise ValueError('INVALID_SHAPE')
    if not np.isfinite(axes).all() or not np.isfinite(values).all():
        raise ValueError('NONFINITE_INPUT')
    keys = [tuple(row) for row in axes]
    if len(set(keys)) != len(keys):
        raise ValueError('DUPLICATE_COORDINATE')
    unique = [sorted(set(axes[:, j])) for j in range(3)]
    if 0. not in unique[1] or 0. not in unique[2]:
        raise ValueError('MISSING_ZERO_ANCHOR')
    if set(keys) != set(itertools.product(*unique)):
        raise ValueError('INCOMPLETE_CARTESIAN_GRID')
    support = (axes[:, 1] == 0.) | (axes[:, 2] == 0.)
    # Copy just the support. Mixed stored values never enter prediction.
    lookup = {key: values[i].copy() for i, key in enumerate(keys) if support[i]}
    predicted = np.stack([lookup[s, m, 0.] + lookup[s, 0., r] - lookup[s, 0., 0.]
                          for s, m, r in keys])
    # Axis responses are exactly reused, avoiding a needless rounded x+y-y.
    predicted[support] = values[support]
    return predicted, support


def load_snapshot(root: Path):
    """Check frozen receipts and project only the required observables."""
    base = root / 'z2_extension/results'
    manifest_path = base / 'MANIFEST.json'
    if sha(manifest_path) != MANIFEST_SHA256:
        raise ValueError('UPSTREAM_MANIFEST_IDENTITY_MISMATCH')
    manifest = read_json(manifest_path)
    expected = list(itertools.product(SIGMAS, MATTER, RADIATION))
    chosen = {}
    for case in manifest['cases']:
        c = case['config']
        key = coordinate(c)
        if c['guard'] or key not in expected:
            continue
        if key in chosen:
            raise ValueError('DUPLICATE_NOMINAL_CASE')
        chosen[key] = case
    if set(chosen) != set(expected):
        raise ValueError('PRIMARY_GRID_MISSING')
    arrays, ids, records, elapsed = [], [], [], []
    common_x = common_a = common_signature = None
    max_initial = np.zeros(3)
    max_norm = max_stress = 0.
    raw_bytes = 0
    for key in expected:
        case = chosen[key]
        c = case['config']
        case_id = case['id']
        if len(case_id) != 64 or any(ch not in '0123456789abcdef' for ch in case_id):
            raise ValueError('INVALID_CASE_ID')
        folder = base / 'cases' / case_id
        result, inp = read_json(folder/'RESULT.json'), read_json(folder/'INPUT.json')
        if result['status'] != 'COMPLETED' or result['exit'] != 0 or not all(result['checks'].values()):
            raise ValueError('UPSTREAM_CASE_NOT_ACCEPTED:' + case_id)
        if result['config'] != c or inp != case or result['id'] != case_id:
            raise ValueError('CONFIG_RECEIPT_MISMATCH:' + case_id)
        raw = folder/'raw.npz'
        raw_hash = sha(raw)
        if raw_hash != result['raw_sha256'] or raw.stat().st_size != result['raw_bytes']:
            raise ValueError('RAW_IDENTITY_MISMATCH:' + case_id)
        signature = {k: c[k] for k in ('source_commit', 'source_sha256', 'ellmax',
            'radial_cells', 'angular_cells', 'subcell_gauss_order', 'mass_fraction',
            'mass_over_Tref', 'ne_source', 'solver')}
        if c['source_commit'] != SOURCE_COMMIT or c['ellmax'] != 8 or c['ne_source'] is not None:
            raise ValueError('PHYSICS_SCOPE_MISMATCH')
        if common_signature is None:
            common_signature = signature
            for name, expected_hash in c['source_sha256'].items():
                if sha(root/'vendor'/name) != expected_hash:
                    raise ValueError('PHYSICAL_SOURCE_BYTES_MISMATCH:' + name)
        elif common_signature != signature:
            raise ValueError('MIXED_CLOSURE_OR_RESOLUTION')
        with np.load(raw, allow_pickle=False) as d:
            x, a = d['x'], d['a']
            if x.shape != (153,) or d['raw_y'].shape != (40, 153):
                raise ValueError('STATE_SHAPE_MISMATCH')
            for name in ('x', 'a', 'H', 's', 'elapsed_proper_s', 'P_m', 'P_r',
                         'P_total', 'Sigma_F', 'Pi_matter_J_m3',
                         'Pi_gamma_J_m3', 'Pi_nu_J_m3'):
                field = d[name]
                if field.shape != (153,) or np.iscomplexobj(field) or not np.isfinite(field).all():
                    raise ValueError('INVALID_REAL_FINITE_FIELD:' + name)
            if np.iscomplexobj(d['raw_y']) or not np.isfinite(d['raw_y']).all():
                raise ValueError('INVALID_REAL_FINITE_STATE')
            if not np.all(a > 0.) or not np.all(d['H'] > 0.):
                raise ValueError('NONPOSITIVE_A_OR_H')
            if x[0] != 0. or not np.all(np.diff(x) > 0.) or x[120] != math.log(21/5) or x[-1] != math.log(7):
                raise ValueError('TIME_GRID_MISMATCH')
            if common_x is None:
                common_x, common_a = x.copy(), a.copy()
            elif not np.array_equal(x, common_x) or not np.array_equal(a, common_a):
                raise ValueError('UNALIGNED_REDSHIFT_GRID')
            H, s = d['H'], d['s']
            y = np.stack((math.sqrt(6)*s/H, d['P_m'], d['P_r']), axis=-1)
            if not np.isfinite(y).all() or not np.all(H > 0):
                raise ValueError('NONFINITE_OR_NONEXPANDING')
            if not np.array_equal(d['P_total'], d['P_m']+d['P_r']):
                raise ValueError('SIGNED_TOTAL_MISMATCH')
            p = np.stack((d['Pi_matter_J_m3'], d['Pi_gamma_J_m3']+d['Pi_nu_J_m3']), axis=-1)
            normalization_error = float(np.max(abs(y[:, 1:] - math.sqrt(6)*KAPPA_T*p/H[:, None]**2)))
            norm_error = float(np.max(abs(abs(y[:, 0]) - d['Sigma_F'])))
            if max(normalization_error, norm_error) > 5e-12:
                raise ValueError('OBSERVER_NORMALIZATION_MISMATCH')
            initial_error = abs(y[0]-key)
            if max(initial_error) > 5e-12:
                raise ValueError('INITIAL_COORDINATE_MISMATCH')
            max_initial = np.maximum(max_initial, initial_error)
            max_norm, max_stress = max(max_norm, norm_error), max(max_stress, normalization_error)
            arrays.append(y)
            elapsed.append(d['elapsed_proper_s'].copy())
        ids.append(case_id)
        raw_bytes += raw.stat().st_size
        records.append({'case_id': case_id, 'nominal': list(key), 'raw_sha256': raw_hash,
            'raw_bytes': raw.stat().st_size, 'input_sha256': sha(folder/'INPUT.json'),
            'result_sha256': sha(folder/'RESULT.json'), 'prefix_raw_sha256': case['prefix_raw_sha256']})
    meta = {'schema': 'rec.trajectory.input_projection.v1', 'physical_source': common_signature,
        'manifest_sha256': MANIFEST_SHA256, 'cases': records, 'selected_raw_bytes': raw_bytes,
        'max_initial_realization_error': dict(zip(FIELDS, max_initial.tolist())),
        'max_signed_to_saved_norm_difference': max_norm, 'max_SI_stress_normalization_difference': max_stress,
        'clock': 'common x=ln(a/a_ref), not common elapsed proper time', 'source_root_at_ingest': str(root.resolve())}
    return np.asarray(expected), np.stack(arrays), common_x, 1/common_a-1, np.asarray(ids), np.stack(elapsed), meta


def metric(actual, predicted, axes, z, support):
    error = actual-predicted
    idx = np.flatnonzero(~support)
    e = abs(error[idx])
    i, j = np.unravel_index(np.argmax(e), e.shape)
    case = int(idx[i])
    return {'max_abs_difference': float(e[i, j]), 'max_at_nominal': axes[case].tolist(),
        'max_at_z': float(z[j]), 'max_at_epoch': int(j), 'rms_difference': float(np.sqrt(np.mean(e**2))),
        'endpoint_max_abs_difference': float(e[:, -1].max()),
        'signal_peak_abs': float(abs(actual[idx]).max()),
        'max_difference_over_global_signal_peak': float(e.max()/max(abs(actual[idx]).max(), np.finfo(float).tiny))}


def analyze(axes, actual, x, z, ids, elapsed, meta, output: Path):
    predicted, support = reconstruct(axes, actual)
    total, ptotal = actual[..., 1]+actual[..., 2], predicted[..., 1]+predicted[..., 2]
    results = {name: metric(actual[..., j], predicted[..., j], axes, z, support)
               for j, name in enumerate(FIELDS)}
    results['P_total_F_signed'] = metric(total, ptotal, axes, z, support)
    results['Pi_total_F_norm'] = metric(abs(total), abs(ptotal), axes, z, support)
    signed_error = abs(total-ptotal)
    norm_error = abs(abs(total)-abs(ptotal))
    slack = signed_error-norm_error
    if float(slack.min()) < -64*np.finfo(float).eps*max(1., float(abs(total).max())):
        raise ValueError('REVERSE_TRIANGLE_FAILURE')
    output.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(output/'TRAJECTORY_ANALYSIS.npz', axes=axes, actual=actual,
        predicted=predicted, x=x, z=z, support=support, case_ids=ids,
        elapsed_proper_s=elapsed, field_names=np.array(FIELDS))
    write_json(output/'INPUT_PROJECTION.json', meta)
    zero_s = axes[:, 0] == 0
    cancelling = zero_s & (axes[:, 1] != 0) & (axes[:, 1]+axes[:, 2] == 0)
    cancellation = [{'case_id': str(ids[i]), 'nominal': axes[i].tolist(),
        'initial_actual': actual[i, 0].tolist(), 'endpoint_actual': actual[i, -1].tolist(),
        'endpoint_total_signed': float(total[i, -1]), 'endpoint_total_norm': float(abs(total[i, -1])),
        'endpoint_prediction': predicted[i, -1].tolist(),
        'max_total_signed_discrepancy': float(abs(total[i]-ptotal[i]).max())} for i in np.flatnonzero(cancelling)]
    summary = {'schema': 'rec.trajectory.analysis.v1', 'status': 'RETROSPECTIVE_STORED_TRAJECTORY_COMPARISON',
        'cases': len(axes), 'support_cases': int(support.sum()), 'mixed_cases': int((~support).sum()),
        'epochs': len(x), 'all_case_epochs': int(len(axes)*len(x)),
        'mixed_case_epochs': int((~support).sum()*len(x)), 'z_initial': float(z[0]), 'z_final': float(z[-1]),
        'join_epoch': 120, 'new_ODE_runs': 0, 'new_NCP_jobs': 0, 'new_benchmarks': 0,
        'fit_coefficients': 0, 'interpolated_samples': 0, 'metrics': results,
        'min_reverse_triangle_slack': float(slack.min()), 'zero_shear_initial_cancellation': cancellation,
        'endpoint_elapsed_s_range': [float(elapsed[:, -1].min()), float(elapsed[:, -1].max())],
        'component_norm_convention': 'full Frobenius; half = full/sqrt(2)',
        'physical': 'HOLD', 'global_convergence': 'NOT_RUN', 'production': 'NOT_APPROVED',
        'same_case_pending_queue': 0, 'performance': 'NOT_MEASURED',
        'meaning': 'Stored discrepancies include parameter interaction and numerical/calibration differences; no ODE error bound.'}
    write_json(output/'SUMMARY.json', summary)
    with gzip.open(output/'MIXED_TRAJECTORY_COMPARISON.csv.gz', 'wt', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['case_id','S_F_i','P_m_F_i','P_r_F_i','epoch','z'] +
            [p+n for n in FIELDS for p in ('actual_', 'predicted_', 'difference_')] +
            ['actual_P_total_F_signed','predicted_P_total_F_signed','actual_Pi_total_F_norm','predicted_Pi_total_F_norm'])
        for i in np.flatnonzero(~support):
            for t in range(len(x)):
                row = [str(ids[i]), *axes[i].tolist(), t, float(z[t])]
                for j in range(3): row.extend((actual[i,t,j], predicted[i,t,j], actual[i,t,j]-predicted[i,t,j]))
                writer.writerow(row+[total[i,t],ptotal[i,t],abs(total[i,t]),abs(ptotal[i,t])])
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path, help='New directory; existing outputs are never overwritten.')
    args = parser.parse_args()
    begin_wall, begin_cpu = time.monotonic(), time.process_time()
    source_hash = sha(Path(__file__))
    data = load_snapshot(args.snapshot)
    summary = analyze(*data, args.output)
    write_json(args.output/'EXECUTION.json', {'command': __import__('sys').argv, 'exit': 0,
        'source_sha256': source_hash, 'wall_s': time.monotonic()-begin_wall,
        'process_cpu_s': time.process_time()-begin_cpu,
        'process_lifetime_maxrss_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'timer_scope': 'main after imports, includes input verification/projection/analysis/output; no baseline comparison',
        'numpy': np.__version__, 'python': __import__('sys').version, 'physical_integrations': 0})
    print(json.dumps({'cases': summary['cases'], 'support': summary['support_cases'],
        'mixed': summary['mixed_cases'], 'epochs': summary['epochs'], 'metrics': summary['metrics']}, indent=2))


if __name__ == '__main__':
    main()

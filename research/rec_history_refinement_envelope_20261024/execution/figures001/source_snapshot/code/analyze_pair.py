"""One actual 314x759 stored-history comparison under the frozen contract."""
import argparse
import csv
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from envelope import cell_arrays, tolerance, query_direct, query_decomposed, evaluate_closure, physical_bounds, half, SUB

ROOT = Path(__file__).resolve().parents[1]
PLAN_SHA = '6711a193e553cf684e74d42d12bc3e76ec6ff72a842a5e72e023cf990976d154'
MASKS = {'startup_origin': (0, 7), 'post_startup': (8, 758),
         'continuation_before_event': (8, 757), 'event_straddling': (758, 758)}


def save_json(p, data):
    p.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def load_plan(path):
    b = path.read_bytes()
    if hashlib.sha256(b).hexdigest() != PLAN_SHA:
        raise ValueError('FROZEN_CASE_PLAN_IDENTITY')
    plan = json.loads(b)
    source = json.loads((ROOT/plan['source_binding']['candidate_manifest']).read_text())
    if source['source_head'] != plan['parent_commit']:
        raise ValueError('SOURCE_HEAD_BINDING')
    for role, info in plan['inputs'].items():
        meta = source['pair'][role]
        if meta['sha256'] != info['sha256'] or meta['git_blob'] != info['git_blob']:
            raise ValueError('SOURCE_PAIR_IDENTITY')
    common = source['common_source']
    expected = plan['source_binding']
    if common['archive_sha256'] != expected['original_archive_sha256']:
        raise ValueError('SOURCE_ARCHIVE_BINDING')
    if common['cosmology']['T0_K'] != expected['T0_K'] or common['cosmology']['nH0_m3'] != expected['nH0_m3']:
        raise ValueError('SOURCE_COSMOLOGY_BINDING')
    if 'FLRW scalar source frame' not in common['frame']:
        raise ValueError('SOURCE_FRAME_BINDING')
    identity = json.loads((ROOT/expected['producer_identity']).read_text())
    if len(identity) != 4 or not all(v['match'] and v['current_sha256'] == v['receipt_sha256'] for v in identity):
        raise ValueError('PRODUCER_RECEIPT_BINDING')
    if source['pair']['coarse']['h'] != 2*source['pair']['fine']['h']:
        raise ValueError('STEP_RATIO')
    if source['pair']['coarse']['g0']*source['pair']['coarse']['h'] != source['pair']['fine']['g0']*source['pair']['fine']['h']:
        raise ValueError('ETA_ORIGIN')
    return plan, source


def load_pair(plan):
    arrays = []
    for role, n in [('coarse', 761), ('fine', 1519)]:
        info = plan['inputs'][role]
        p = ROOT/info['path']
        b = p.read_bytes()
        if len(b) != info['bytes'] or hashlib.sha256(b).hexdigest() != info['sha256']:
            raise ValueError('ORIGINAL_INPUT_BYTE_IDENTITY_'+role)
        with np.load(p, allow_pickle=False) as z:
            v, l = z['virtual_out'], z['lyman_out']
            if v.shape != (311, n) or l.shape != (3, n):
                raise ValueError('OUTGOING_SHAPES_'+role)
            if v.dtype != np.float64 or l.dtype != np.float64 or not np.isfinite(v).all() or not np.isfinite(l).all():
                raise ValueError('FINITE_BINARY64_'+role)
            if role == 'fine' and (float(z['dlna']) != plan['grid']['fine_step'] or str(z['source_zip_sha256']) != plan['source_binding']['original_archive_sha256'] or bool(z['rei_activation'])):
                raise ValueError('EMBEDDED_FINE_METADATA')
            arrays.append(np.concatenate([v, l], axis=0))
    # The unused last coarse column is retained in the input package, never compared.
    return arrays[0][:, :760], arrays[1]


def exact_direct(c0, c1, f0, fh, f1, u):
    """Independent direct interpolants, using exact rationals from stored values."""
    coarse = (1-u)*Q.from_float(float(c0)) + u*Q.from_float(float(c1))
    if u <= Q(1, 2):
        fine = (1-2*u)*Q.from_float(float(f0)) + 2*u*Q.from_float(float(fh))
    else:
        fine = (2-2*u)*Q.from_float(float(fh)) + (2*u-1)*Q.from_float(float(f1))
    return coarse-fine


def oracle_checks(c, f, result, plan):
    rows, bounds = [], []
    worst = {'ratio': 0.0, 'channel': None, 'cell': None, 'u': None, 'path': None}
    for k in plan['oracle']['channels']:
        for m in plan['oracle']['cells']:
            vals = (c[k, m], c[k, m+1], f[k, 2*m], f[k, 2*m+1], f[k, 2*m+2])
            tol = float(tolerance(*map(np.asarray, vals)))
            exacts = []
            for text in plan['oracle']['u_rational']:
                u = Q(text)
                exact = exact_direct(*vals, u)
                x = m+float(u)
                direct = float(query_direct(c[k:k+1], f[k:k+1], x, closure=True)[0])
                decomp = float(query_decomposed(c[k:k+1], f[k:k+1], x, closure=True)[0])
                errors = {'direct': abs(Q.from_float(direct)-exact), 'decomposed': abs(Q.from_float(decomp)-exact)}
                ok = all(e <= Q.from_float(tol) for e in errors.values()) and abs(direct-decomp) <= tol
                for name, error in errors.items():
                    ratio = float(error/Q.from_float(tol))
                    if ratio >= worst['ratio']:
                        worst = {'ratio': ratio, 'channel': k, 'cell': m, 'u': text, 'path': name}
                rows.append({'channel': k, 'cell': m, 'u': text, 'direct': direct, 'decomposed': decomp,
                             'exact_numerator': str(exact.numerator), 'exact_denominator': str(exact.denominator),
                             'direct_error': float(errors['direct']), 'decomposed_error': float(errors['decomposed']),
                             'tolerance': tol, 'pass': ok})
                if u in [Q(0), Q(1, 2), Q(1)]:
                    exacts.append(abs(exact))
            exact_b = max(exacts)
            low, high = float(result['B_lower'][k, m]), float(result['B_upper'][k, m])
            ok = Q.from_float(low) <= exact_b <= Q.from_float(high)
            bounds.append({'channel': k, 'cell': m, 'B_lower': low, 'B_upper': high,
                           'exact_B_numerator': str(exact_b.numerator), 'exact_B_denominator': str(exact_b.denominator), 'pass': ok})
    return {'points': rows, 'cell_bounds': bounds, 'worst_error_tolerance_ratio': worst,
            'point_count': len(rows), 'cell_count': len(bounds),
            'all_pass': all(r['pass'] for r in rows+bounds)}


def synthetic_controls():
    rows = []
    def check(name, condition):
        rows.append({'name': name, 'pass': bool(condition)})
    def one(c, f):
        return cell_arrays(np.array([c], dtype='float64'), np.array([f], dtype='float64'))
    check('constant exact agreement', one([3, 3], [3, 3, 3])['B'][0, 0] == 0)
    check('affine exact agreement', one([1, 5], [1, 3, 5])['B'][0, 0] == 0)
    check('quadratic detail fsecond H2/8', one([0, 1], [0, .25, 1])['delta'][0, 0] == 2/8)
    a = one([1, 1], [0, 0, 0])
    check('nonzero nodal zero detail', a['B'][0, 0] == 1 and a['delta'][0, 0] == 0)
    a = one([0, 0], [1, 0, 1])
    check('midpoint cancellation', a['Dmid'][0, 0] == 0 and a['E0'][0, 0] == -1 and a['delta'][0, 0] == 1)
    a = one([-1, 1], [0, 0, 0])
    check('sign changing difference', a['Dmid'][0, 0] == 0 and a['B'][0, 0] == 1)
    a = one([0, 0], [0, 0, 0])
    check('zero scale no floor', a['B'][0, 0] == 0 and a['tolerance'][0, 0] == 8*SUB)
    for i, (c, f) in enumerate([([0, SUB], [SUB, 0, 0]), ([-SUB, SUB], [0, SUB, -SUB]), ([0, 0], [0, 0, 0])]):
        a = one(c, f)
        b = max(abs(exact_direct(*[float(v) for v in [c[0], c[1], f[0], f[1], f[2]]], u)) for u in [Q(0), Q(1, 2), Q(1)])
        check('subnormal interval '+str(i), Q.from_float(float(a['B_lower'][0, 0])) <= b <= Q.from_float(float(a['B_upper'][0, 0])))
    # Explicit normal-to-subnormal witness distinguishes gradual underflow
    # from a flush-to-zero arithmetic environment.
    minimum_normal = float(np.finfo(np.float64).tiny)
    exact_normal_half = Q.from_float(minimum_normal)/2
    normal_half = minimum_normal*0.5
    lo, hi = half((np.asarray(minimum_normal), np.asarray(minimum_normal)))
    check('minimum normal divided2 Fraction exact witness',
          normal_half != 0 and Q.from_float(normal_half) == exact_normal_half
          and Q.from_float(float(lo)) <= exact_normal_half <= Q.from_float(float(hi)))
    # The exact half of the least subnormal is unrepresentable; the widened
    # zero result must still enclose this strictly positive rational.
    exact_subnormal_half = Q.from_float(float(SUB))/2
    lo, hi = half((np.asarray(SUB), np.asarray(SUB)))
    check('minimum subnormal divided2 Fraction enclosure',
          exact_subnormal_half > 0 and float(SUB)*0.5 == 0
          and Q.from_float(float(lo)) <= exact_subnormal_half <= Q.from_float(float(hi)))
    c, f = np.zeros((1, 760)), np.zeros((1, 1519))
    for name, action in [
        ('reject nonfinite data', lambda: one([0, float('nan')], [0, 0, 0])),
        ('reject incomplete domain shape', lambda: one([0, 0, 0], [0, 0, 0])),
        ('reject nonfinite query', lambda: query_direct(c, f, float('nan'))),
        ('reject negative query', lambda: query_direct(c, f, -1)),
        ('reject operational x759', lambda: query_direct(c, f, 759)),
        ('reject prefix length below2', lambda: query_direct(c, f, 0, coarse_prefix=1)),
        ('reject unavailable face prefix', lambda: query_direct(c, f, 5, coarse_prefix=5)),
        ('reject interval overflow', lambda: one([np.finfo(float).max, np.finfo(float).max], [-np.finfo(float).max, 0, 0]))]:
        try:
            action()
        except (ValueError, FloatingPointError):
            check(name, True)
        else:
            check(name, False)
    check('coordinate zero is admitted', float(query_direct(c, f, 0)[0]) == 0)
    check('closure endpoint witness admitted', float(evaluate_closure(c, f, 759)[0]) == 0)
    check('absent physical reference unavailable', physical_bounds(1) == {'status': 'UNAVAILABLE', 'lower': None, 'upper': None})
    conditional = physical_bounds(-2, .5)
    check('conditional physical reference outward', conditional == {'status': 'CONDITIONAL', 'lower': float(np.nextafter(1.5, -np.inf)), 'upper': float(np.nextafter(2.5, np.inf))})
    conditional = physical_bounds(1, 2**-54)
    check('conditional physical reference Fraction rounding witness',
          Q.from_float(conditional['lower']) <= Q(1)-Q(1, 2**54)
          and Q.from_float(conditional['upper']) >= Q(1)+Q(1, 2**54))
    return rows


def channel_summary(c, f, a, out):
    scale = np.maximum(np.max(np.abs(c), axis=1), np.max(np.abs(f), axis=1))
    mapping = [('virtual_out', k) if k < 311 else ('lyman_out', k-311) for k in range(314)]
    eta0, h = -math.log(8001)+36446*4.245e-5, 4.245e-5
    rows = []
    for mask, (first, last) in MASKS.items():
        for k, (field, index) in enumerate(mapping):
            slab = a['B'][k, first:last+1]
            m = first+int(np.argmax(slab))
            knot = int(np.argmax(np.abs(a['witnesses'][k, m])))
            u = knot/2
            eta = eta0+(m+u)*h
            b = float(a['B'][k, m])
            rows.append({'channel': k, 'field': field, 'field_index': index, 'mask': mask,
                         'B_max': b, 'B_upper_max': float(np.max(a['B_upper'][k, first:last+1])),
                         'nodal_max': float(max(np.max(np.abs(a['E0'][k, first:last+1])), np.max(np.abs(a['E1'][k, first:last+1])))),
                         'fine_detail_max': float(np.max(np.abs(a['delta'][k, first:last+1]))),
                         'history_scale': float(scale[k]), 'normalized_discrepancy': b/float(scale[k]) if scale[k] != 0 else 0.0,
                         'normalization_status': 'ZERO_SCALE_EXACT_ZERO' if scale[k] == 0 else 'DESCRIPTIVE',
                         'argmax_cell': m, 'argmax_u': u, 'argmax_eta': eta, 'argmax_z': math.exp(-eta)-1})
    with (out/'PER_CHANNEL.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return mapping, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = ROOT/args.out
    out.mkdir(parents=True, exist_ok=False)
    plan, source = load_plan(ROOT/args.contract)
    controls = synthetic_controls()
    # A deliberately changed frozen metadata plan must fail before array reads.
    altered = out/'REJECTED_METADATA_CONTROL.json'
    bad = dict(plan)
    bad['grid'] = dict(plan['grid'], ratio=3)
    save_json(altered, bad)
    try:
        load_plan(altered)
    except ValueError:
        controls.append({'name': 'reject mismatched contract metadata', 'pass': True})
    else:
        controls.append({'name': 'reject mismatched contract metadata', 'pass': False})
    save_json(out/'SYNTHETIC_CONTROLS.json', controls)
    if not all(r['pass'] for r in controls):
        raise AssertionError('SYNTHETIC_CONTROL_FAILURE')
    c, f = load_pair(plan)
    a = cell_arrays(c, f)
    oracle = oracle_checks(c, f, a, plan)
    save_json(out/'FRACTION_ORACLE.json', oracle)
    midpoint_ok = bool(np.all(np.abs(a['midpoint_residual']) <= a['tolerance']))
    ratios = np.abs(a['midpoint_residual'])/a['tolerance']
    worst = np.unravel_index(int(np.argmax(ratios)), ratios.shape)
    mapping, rows = channel_summary(c, f, a, out)
    raw = {k: v for k, v in a.items()}
    raw.update({'channel_field': np.array([v[0] for v in mapping]), 'channel_field_index': np.array([v[1] for v in mapping]),
                'coarse': c, 'fine': f, 'cell_index': np.arange(759), 'channel_index': np.arange(314)})
    for mask, (lo, hi) in MASKS.items():
        raw['mask_'+mask] = (np.arange(759) >= lo) & (np.arange(759) <= hi)
    np.savez_compressed(out/'RAW_COMPARISON.npz', **raw)
    passed = midpoint_ok and oracle['all_pass'] and oracle['point_count'] == 350 and oracle['cell_count'] == 70
    summary = {'unit_id': 'REC-HISTORY-REFINE01', 'status': 'PASS_ARITHMETIC_CHECKS_PENDING_ASTRA_REVIEW' if passed else 'FAILED_ACCEPTANCE_RETURN_TO_ASTRA',
               'channel_count': 314, 'cell_count': 759, 'channel_cells': int(a['B'].size), 'witness_count': int(a['witnesses'].size),
               'input_sha256': {k: v['sha256'] for k, v in plan['inputs'].items()}, 'case_plan_sha256': PLAN_SHA,
               'controls_pass': all(r['pass'] for r in controls), 'oracle_points': 350, 'oracle_cells': 70,
               'oracle_all_pass': oracle['all_pass'], 'midpoint_all_pass': midpoint_ok,
               'worst_midpoint_residual_tolerance': {'channel': int(worst[0]), 'cell': int(worst[1]), 'ratio': float(ratios[worst]), 'residual': float(a['midpoint_residual'][worst]), 'tolerance': float(a['tolerance'][worst])},
               'oracle_worst': oracle['worst_error_tolerance_ratio'],
               'measured_global_B_max': float(np.max(a['B'])), 'measured_global_B_upper_max': float(np.max(a['B_upper'])),
               'mask_maxima': {name: max(r['B_max'] for r in rows if r['mask'] == name) for name in MASKS},
               'physical_reference': physical_bounds(0), 'eps_ref': None, 'endpoint_uncertainty': None, 'physical_M2': None,
               'absolute_physical_bounds': None, 'convergence_order': None, 'original_target_coverage': '0/313',
               'physical_goal_completion_percent': None, 'physical_status': 'HOLD', 'production': 'NOT_APPROVED', 'REI_activation': False,
               'interpretation': 'Exact stored binary64 interpolant discrepancy enclosure; no absolute physical error or global convergence claim.',
               'startup_caveat': 'Continuation mask retains propagated startup effects; no mechanism isolation.',
               'event_cell': 758, 'operational_domain': '[0,759)', 'closure_witness_domain': '[0,759]',
               'global_convergence': 'NOT_RUN', 'trajectory_generations': 0, 'rhs_calls': 0}
    save_json(out/'SUMMARY.json', summary)
    print(json.dumps(summary, indent=2, allow_nan=False))
    if not passed:
        raise AssertionError('SUBSTANTIVE_ACCEPTANCE_FAILURE')


if __name__ == '__main__':
    main()

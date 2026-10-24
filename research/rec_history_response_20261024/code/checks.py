"""Predeclared independent exact arithmetic checks; called only in primary."""
from fractions import Fraction as F
import math
import numpy as np
import interval as iv
from source_response import certify


def rational(x):
    return F.from_float(float(x))


def encoded(x):
    return {'numerator': str(x.numerator), 'denominator': str(x.denominator)}


def probes(a, b, bound):
    """32 maximum: fixed 24 edge/line entries plus 8 largest certified magnitudes."""
    nr, nc = bound[0].shape
    rows = [0, 1, 139, 140, 270, 271, 310, nr-1]
    cols = [0, 311, nc-1]
    selected = list(dict.fromkeys((min(i, nr-1), min(j, nc-1)) for i in rows for j in cols))
    magnitude = np.maximum(np.abs(bound[0]), np.abs(bound[1]))
    # Stable deterministic flatten-index tie break; no matrix recomputation.
    order = np.argsort(-magnitude.ravel(), kind='stable')
    for k in order:
        ij = tuple(map(int, np.unravel_index(k, magnitude.shape)))
        if ij not in selected:
            selected.append(ij)
        if len(selected) == 32:
            break
    records = []
    for i, j in selected:
        exact = sum((rational(a[i, k])*rational(b[k, j]) for k in range(a.shape[1])), F(0))
        lo, hi = bound[0][i, j], bound[1][i, j]
        records.append({'row': i, 'column': j, 'exact': encoded(exact),
                        'lower': float(lo), 'upper': float(hi),
                        'pass': rational(lo) <= exact <= rational(hi)})
    return records


def inverse_exact(matrix):
    n = len(matrix)
    a = [[F(x) for x in row]+[F(int(i == j)) for j in range(n)] for i, row in enumerate(matrix)]
    for c in range(n):
        pivot = next(i for i in range(c, n) if a[i][c])
        a[c], a[pivot] = a[pivot], a[c]
        q = a[c][c]; a[c] = [x/q for x in a[c]]
        for r in range(n):
            if r != c:
                q = a[r][c]; a[r] = [x-q*y for x, y in zip(a[r], a[c])]
    return [row[n:] for row in a]


TOYS = [
    [[1, 0], [0, 1]],
    [[3, 1], [1, 2]],
    [[4, -1, 0], [1, 3, 1], [0, 1, 2]],
    [[5, 1, 0, -1], [1, 4, -1, 0], [0, 1, 3, 1], [-1, 0, 1, 4]],
]


def controls():
    records = []
    def enclosed(name, exact, interval):
        valid = rational(interval[0]) <= exact <= rational(interval[1])
        records.append({'name': name, 'exact': encoded(exact),
                        'lower': float(interval[0]), 'upper': float(interval[1]), 'pass': valid})
    enclosed('zero_add', F(0), iv.add(iv.point(0), iv.point(0)))
    enclosed('identity_product', F(7), iv.mul(iv.point(1), iv.point(7)))
    enclosed('cancellation_dot', F(1), tuple(x[0, 0] for x in iv.point_dot(np.array([[2.0**53, 1, -2.0**53]]), np.ones((3, 1)))))
    mn = np.finfo(float).tiny; ms = np.nextafter(0.0, 1.0)
    enclosed('min_normal_half', rational(mn)/2, iv.mul(iv.point(mn), iv.point(0.5)))
    enclosed('min_subnormal_half', rational(ms)/2, iv.mul(iv.point(ms), iv.point(0.5)))
    interval = iv.mul((np.array(-2.), np.array(3.)), (np.array(-4.), np.array(5.)))
    enclosed('signed_interval_min', F(-12), interval)
    enclosed('signed_interval_max', F(15), interval)
    reject = [
        ('nonfinite', lambda: iv.point(float('nan'))),
        ('infinite', lambda: iv.point(float('inf'))),
        ('overflow', lambda: iv.mul(iv.point(np.finfo(float).max), iv.point(2.))),
        ('negative_epsilon', lambda: iv.box_weights(iv.point(np.eye(2)), [-1, 0])),
        ('nonfinite_epsilon', lambda: iv.box_weights(iv.point(np.eye(2)), [math.nan, 0])),
        ('epsilon_shape', lambda: iv.box_weights(iv.point(np.eye(2)), [0])),
    ]
    for name, action in reject:
        try:
            action()
        except (ValueError, FloatingPointError) as exc:
            records.append({'name': name, 'pass': True, 'refusal': str(exc)})
        else:
            records.append({'name': name, 'pass': False})
    summary, _ = certify(np.eye(2), np.eye(2), np.eye(2), np.zeros((2, 2)), np.eye(2), np.zeros((2, 2)))
    records.append({'name': 'unverified_inverse_rho_ge_1', 'pass': summary['status'] == 'CERTIFICATE_FAILURE_RHO', 'observed': summary})
    toys = []
    for idx, raw in enumerate(TOYS):
        exact_inverse = inverse_exact(raw)
        M = np.array(raw, dtype=float)
        Z = np.array([[float(x) for x in row] for row in exact_inverse])
        n = len(raw)
        # Candidate floats come from exact inversion; no extra numerical solve.
        status, arrays = certify(M, np.eye(n), np.eye(n), np.zeros((n, n)), Z, Z)
        good = status['status'].startswith('CERTIFIED') and all(
            rational(arrays['Klo'][i, j]) <= exact_inverse[i][j] <= rational(arrays['Khi'][i, j])
            for i in range(n) for j in range(n))
        toys.append({'manufactured': True, 'index': idx, 'matrix': raw,
                     'exact_inverse': [[encoded(x) for x in row] for row in exact_inverse],
                     'certificate': status, 'pass': good})
    return {'controls': records, 'manufactured_toys': toys,
            'pass': all(x['pass'] for x in records+toys), 'tiny_exact_systems': 4}


def parity(f, B, T, P):
    n = np.arange(313, dtype=float)
    directions = [np.ones(313), (-1.)**n, np.sin(n+1.), np.cos((n+1.)/7.)]
    records = []
    factor = 512*np.finfo(float).eps
    for index, u in enumerate(directions):
        x = directions[(index+1) % 4]
        for name, represented, imperative, gross in [
            ('source_increment', B@u, f.source_increment(u), np.abs(B)@np.abs(u)),
            ('outgoing', T@x+P@u, f.outgoing(x, u), np.abs(T)@np.abs(x)+np.abs(P)@np.abs(u)),
        ]:
            if name == 'outgoing':
                gross[:311] += 2*np.abs(u[:311])
            residual = np.abs(represented-imperative)
            allowed = factor*gross
            records.append({'direction': index, 'operation': name, 'pass': bool(np.all(residual <= allowed)),
                            'gross_scale': gross.tolist(), 'absolute_difference': residual.tolist(),
                            'allowed_512eps_gross': allowed.tolist(), 'additive_floor': None})
    return {'directions': ['ones', 'alternating', 'sin_index_plus_one', 'cos_index_plus_one_over_seven'],
            'records': records, 'pass': all(x['pass'] for x in records)}

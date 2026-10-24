"""Elementary outward binary64 intervals; no BLAS dot is a certificate.

Assumes round-to-nearest, correctly rounded basic arithmetic, gradual underflow.
Endpoints represent exact real binary64 numbers. Nonfinite endpoints refuse.
"""
import numpy as np


class CertificateFailure(ValueError):
    pass


def finite(*values):
    if not all(np.all(np.isfinite(x)) for x in values):
        raise CertificateFailure('NONFINITE_OR_OVERFLOW')


def down(x):
    finite(x)
    y = np.nextafter(x, -np.inf)
    finite(y)
    return y


def up(x):
    finite(x)
    y = np.nextafter(x, np.inf)
    finite(y)
    return y


def point(x):
    x = np.asarray(x, dtype=np.float64)
    finite(x)
    return x.copy(), x.copy()


def valid(a):
    finite(*a)
    if np.any(a[0] > a[1]):
        raise CertificateFailure('REVERSED_INTERVAL')


def add(a, b):
    valid(a); valid(b)
    with np.errstate(over='ignore', invalid='ignore'):
        return down(a[0] + b[0]), up(a[1] + b[1])


def neg(a):
    valid(a)
    return -a[1], -a[0]


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    valid(a); valid(b)
    with np.errstate(over='ignore', invalid='ignore', under='ignore'):
        products = [a[i] * b[j] for i in (0, 1) for j in (0, 1)]
    finite(*products)
    return down(np.minimum.reduce(products)), up(np.maximum.reduce(products))


def positive_div_upper(numerator, denominator_lower):
    finite(numerator, denominator_lower)
    if np.any(numerator < 0) or np.any(denominator_lower <= 0):
        raise CertificateFailure('POSITIVE_DIVISION_DOMAIN')
    with np.errstate(over='ignore', under='ignore'):
        return up(numerator / denominator_lower)


def abs_bounds(a):
    valid(a)
    lo, hi = a
    amin = np.where((lo <= 0) & (hi >= 0), 0.0, np.minimum(np.abs(lo), np.abs(hi)))
    return amin, np.maximum(np.abs(lo), np.abs(hi))


def sum_bounds(a, axis=-1):
    valid(a)
    lo = np.moveaxis(np.asarray(a[0]), axis, -1)
    hi = np.moveaxis(np.asarray(a[1]), axis, -1)
    lower = np.zeros(lo.shape[:-1]); upper = lower.copy()
    for k in range(lo.shape[-1]):
        lower = down(lower + lo[..., k])
        upper = up(upper + hi[..., k])
    return lower, upper


def point_dot(a, b):
    """Exact point-coefficient dot enclosure, elementary outer-product order."""
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    finite(a, b)
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
        raise CertificateFailure('DOT_SHAPE')
    lower = np.zeros((a.shape[0], b.shape[1])); upper = lower.copy()
    for k in range(a.shape[1]):
        with np.errstate(over='ignore', invalid='ignore', under='ignore'):
            term = a[:, k, None] * b[None, k, :]
        lower = down(lower + down(term))
        upper = up(upper + up(term))
    return lower, upper


def box_weights(interval, epsilon=None):
    lo, hi = abs_bounds(interval)
    if epsilon is None:
        return {'status': 'INPUT_DEPENDENT_UNCALIBRATED', 'epsilon': None, 'bound': None}
    epsilon = np.asarray(epsilon, dtype=float)
    if epsilon.shape != (hi.shape[1],) or not np.all(np.isfinite(epsilon)) or np.any(epsilon < 0):
        raise ValueError('INVALID_EPSILON')
    weighted = mul((lo, hi), point(epsilon))
    lower, upper = sum_bounds(weighted)
    return {'status': 'CONDITIONAL_ON_SUPPLIED_BOX', 'epsilon': epsilon.tolist(),
            'lower': np.maximum(0, lower).tolist(), 'bound': upper.tolist()}

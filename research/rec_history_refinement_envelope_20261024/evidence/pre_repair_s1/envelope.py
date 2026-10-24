"""Stored-table comparison only; no trajectory or recombination solver."""
import math
import numpy as np

EPS = np.finfo(np.float64).eps
SUB = np.nextafter(np.float64(0), np.float64(1))


def finite64(a):
    a = np.asarray(a)
    if a.dtype != np.dtype('float64') or not np.isfinite(a).all():
        raise ValueError('FINITE_BINARY64_REQUIRED')
    return a


def tolerance(c0, c1, f0, fh, f1):
    scale = np.maximum.reduce([np.abs(c0), np.abs(c1), np.abs(f0), np.abs(fh), np.abs(f1)])
    return (64 * EPS) * scale + 8 * SUB


def outward(lo, hi):
    lo = np.nextafter(lo, -np.inf)
    hi = np.nextafter(hi, np.inf)
    if not np.isfinite(lo).all() or not np.isfinite(hi).all():
        raise ValueError('INTERVAL_OVERFLOW')
    return lo, hi


def subtract(a, b):
    return outward(a[0] - b[1], a[1] - b[0])


def add(a, b):
    return outward(a[0] + b[0], a[1] + b[1])


def half(a):
    return outward(a[0] * 0.5, a[1] * 0.5)


def abs_interval(a):
    lo, hi = a
    low = np.where((lo <= 0) & (hi >= 0), 0.0, np.minimum(np.abs(lo), np.abs(hi)))
    return low, np.maximum(np.abs(lo), np.abs(hi))


def cell_arrays(c, f):
    c, f = finite64(c), finite64(f)
    if c.ndim != 2 or f.ndim != 2 or c.shape[0] != f.shape[0] or f.shape[1] != 2*c.shape[1]-1:
        raise ValueError('NESTED_SHAPES_REQUIRED')
    c0, c1 = c[:, :-1], c[:, 1:]
    f0, fh, f1 = f[:, :-2:2], f[:, 1::2], f[:, 2::2]
    with np.errstate(over='raise', invalid='raise', under='ignore'):
        e0, e1 = c0-f0, c1-f1
        detail = 0.5*f0 + 0.5*f1 - fh
        mid = 0.5*c0 + 0.5*c1 - fh
        decomposed_mid = 0.5*e0 + 0.5*e1 + detail
        residual = mid - decomposed_mid
        witnesses = np.stack([e0, mid, e1], axis=-1)
        bound = np.max(np.abs(witnesses), axis=-1)
        intervals = [subtract((c0, c0), (f0, f0)),
                     subtract(add(half((c0, c0)), half((c1, c1))), (fh, fh)),
                     subtract((c1, c1), (f1, f1))]
        abs_bounds = [abs_interval(v) for v in intervals]
        low = np.maximum.reduce([v[0] for v in abs_bounds])
        high = np.maximum.reduce([v[1] for v in abs_bounds])
    for a in [e0, e1, detail, mid, residual, bound, low, high]:
        if not np.isfinite(a).all():
            raise ValueError('ARITHMETIC_NONFINITE')
    return {'E0': e0, 'E1': e1, 'delta': detail, 'Dmid': mid,
            'midpoint_residual': residual, 'B': bound, 'B_lower': low,
            'B_upper': high, 'witnesses': witnesses,
            'tolerance': tolerance(c0, c1, f0, fh, f1)}


def _coordinate(c, f, x, coarse_prefix, fine_prefix, closure):
    if not math.isfinite(x) or x < 0:
        raise ValueError('QUERY_DOMAIN')
    end = min(c.shape[1]-1, (f.shape[1]-1)//2)
    if x > end or (x == end and not closure):
        raise ValueError('QUERY_UPPER_EXCLUSIVE')
    if end < 1 or coarse_prefix < 2 or fine_prefix < 2:
        raise ValueError('INSUFFICIENT_PREFIX')
    if coarse_prefix > c.shape[1] or fine_prefix > f.shape[1]:
        raise ValueError('PREFIX_EXCEEDS_STORAGE')
    m = min(int(math.floor(x)), end-1)
    u = x-m
    # Prefix belongs to this face. Emission coordinates need not be >=2.
    # Both bracketing samples must be in the committed prefix.
    j = 2*m + (1 if u >= 0.5 else 0)
    if closure and x == end:
        j = 2*m+1
    if m+1 >= coarse_prefix or j+1 >= fine_prefix:
        raise ValueError('INSUFFICIENT_PREFIX')
    return m, u, j


def query_direct(c, f, x, coarse_prefix=None, fine_prefix=None, *, closure=False):
    c, f = finite64(c), finite64(f)
    pc = c.shape[1] if coarse_prefix is None else coarse_prefix
    pf = f.shape[1] if fine_prefix is None else fine_prefix
    m, u, j = _coordinate(c, f, x, pc, pf, closure)
    v = 2*(x-j/2)
    return ((1-u)*c[:, m] + u*c[:, m+1]) - ((1-v)*f[:, j] + v*f[:, j+1])


def query_decomposed(c, f, x, coarse_prefix=None, fine_prefix=None, *, closure=False):
    c, f = finite64(c), finite64(f)
    pc = c.shape[1] if coarse_prefix is None else coarse_prefix
    pf = f.shape[1] if fine_prefix is None else fine_prefix
    m, u, _ = _coordinate(c, f, x, pc, pf, closure)
    # The decomposition uses all three fine knots; require its own prefix.
    if 2*m+2 >= pf:
        raise ValueError('INSUFFICIENT_DECOMPOSITION_PREFIX')
    e0 = c[:, m]-f[:, 2*m]
    e1 = c[:, m+1]-f[:, 2*m+2]
    d = 0.5*f[:, 2*m] + 0.5*f[:, 2*m+2] - f[:, 2*m+1]
    return (1-u)*e0 + u*e1 + (2*min(u, 1-u))*d


def evaluate_closure(c, f, x):
    """Closed-domain witness path; not an operational incoming-history query."""
    return query_direct(c, f, x, closure=True)


def physical_bounds(discrepancy, eps_ref=None):
    if eps_ref is None:
        return {'status': 'UNAVAILABLE', 'lower': None, 'upper': None}
    if not math.isfinite(eps_ref) or eps_ref < 0 or not math.isfinite(discrepancy):
        raise ValueError('FINITE_NONNEGATIVE_REFERENCE_ERROR_REQUIRED')
    return {'status': 'CONDITIONAL', 'lower': max(0.0, abs(discrepancy)-eps_ref),
            'upper': abs(discrepancy)+eps_ref}


def physical_cell_upper(b_upper, eps_ref_cell=None):
    if eps_ref_cell is None:
        return {'status': 'UNAVAILABLE', 'upper': None}
    if not math.isfinite(b_upper) or b_upper < 0 or not math.isfinite(eps_ref_cell) or eps_ref_cell < 0:
        raise ValueError('FINITE_NONNEGATIVE_CELL_REFERENCE_ERROR_REQUIRED')
    upper = float(np.nextafter(b_upper+eps_ref_cell, np.inf))
    if not math.isfinite(upper):
        raise ValueError('PHYSICAL_BOUND_OVERFLOW')
    return {'status': 'CONDITIONAL', 'upper': upper}

"""Conditional ODE envelope arithmetic, exact rational endpoints.

No native trajectory, physical defect, model discrepancy, or scientific admission
is manufactured here. Input bounds must be established over the declared tube.
Python's arbitrary-precision integers and Fraction are the arithmetic trust base.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
from math import isfinite
from typing import Iterable, Sequence

Scalar = int | float | str | Q

def rational(value: Scalar) -> Q:
    """Floats mean their exact represented binary64 value; strings mean rationals."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Q)):
        raise ValueError("finite rational scalar required")
    if isinstance(value, float) and not isfinite(value):
        raise ValueError("nonfinite input")
    try:
        return Q(value)
    except (ValueError, ZeroDivisionError, OverflowError) as error:
        raise ValueError("finite rational scalar required") from error

@dataclass(frozen=True)
class Interval:
    lo: Q
    hi: Q

    def __post_init__(self) -> None:
        object.__setattr__(self, "lo", rational(self.lo))
        object.__setattr__(self, "hi", rational(self.hi))
        if self.lo > self.hi:
            raise ValueError("reversed interval")

    @staticmethod
    def point(value: Scalar) -> Interval:
        q = rational(value)
        return Interval(q, q)

    def __add__(self, other: Interval) -> Interval:
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __mul__(self, other: Interval) -> Interval:
        corners = [x*y for x in (self.lo, self.hi) for y in (other.lo, other.hi)]
        return Interval(min(corners), max(corners))

    def scale(self, value: Scalar) -> Interval:
        return self * Interval.point(value)

    def outward(self, bits: int) -> Interval:
        """Absolute dyadic grid. This widens endpoints by less than 2**(-bits)."""
        if isinstance(bits, bool) or not isinstance(bits, int) or not 64 <= bits <= 512:
            raise ValueError("precision bits must be an integer in [64,512]")
        scale = 1 << bits
        a, b = self.lo * scale, self.hi * scale
        return Interval(Q(a.numerator // a.denominator, scale),
                        Q(-((-b.numerator) // b.denominator), scale))

    def record(self) -> dict[str, str]:
        return {"lo": str(self.lo), "hi": str(self.hi)}

    @property
    def width(self) -> Q:
        return self.hi - self.lo


def exp_phi1(x: Scalar, bits: int = 128) -> tuple[Interval, Interval, dict]:
    """Enclose exp(x) and integral_0^1 exp(x*s) ds, for |x| <= 32.

    Taylor remainders use a geometric majorant on |z|<=1/2. Scaling identities
    are applied with outward dyadic rounding. No floating transcendental call.
    """
    x = rational(x)
    Interval.point(0).outward(bits)  # Validate precision before any work.
    if abs(x) > 32:
        raise ValueError("declared arithmetic domain |mu*h| <= 32 exceeded")
    if x == 0:
        return Interval.point(1), Interval.point(1), {"terms": 1, "doublings": 0}
    z, doublings = x, 0
    while abs(z) > Q(1, 2):
        z /= 2
        doublings += 1
    t, sp, se, n = Q(1), Q(1), Q(1), 0
    target = Q(1, 1 << (bits + 20))
    while True:
        # t = z**n/n!, se=sum_0^n t_k, sp=sum_0^n t_k/(k+1).
        first_exp = abs(t*z/Q(n+1))
        tail_exp = first_exp/(1-abs(z)/Q(n+2))
        first_phi = first_exp/Q(n+2)
        tail_phi = first_phi/(1-abs(z)/Q(n+3))
        if max(tail_exp, tail_phi) <= target:
            break
        n += 1
        if n > 256:
            raise ArithmeticError("Taylor term cap exceeded")
        t *= z/Q(n)
        se += t
        sp += t/Q(n+1)
    e = Interval(se-tail_exp, se+tail_exp).outward(bits)
    phi = Interval(sp-tail_phi, sp+tail_phi).outward(bits)
    for _ in range(doublings):
        old_e = e
        phi = ((old_e + Interval.point(1))*phi).scale(Q(1,2)).outward(bits)
        e = (old_e*old_e).outward(bits)
    return e, phi, {"terms": n+1, "doublings": doublings}

@dataclass(frozen=True)
class Envelope:
    endpoint: Interval
    uniform_upper: Q
    bits: int
    arithmetic: dict


def envelope(e0: Scalar, defect: Scalar, mu: Scalar, duration: Scalar,
             bits: int = 128) -> Envelope:
    """For nonnegative e0,D,h, r'=mu*r+D. Includes the full segment maximum."""
    e0, defect, mu, h = map(rational, (e0, defect, mu, duration))
    if min(e0, defect, h) < 0:
        raise ValueError("negative error, defect, or duration")
    if mu == 0 or h == 0:
        Interval.point(0).outward(bits)
        result = Interval.point(e0+defect*h) if mu == 0 else Interval.point(e0)
        return Envelope(result, max(e0, result.hi), bits, {"exact_limit": True})
    ex, phi, work = exp_phi1(mu*h, bits)
    result = ex.scale(e0) + phi.scale(defect*h)
    return Envelope(result, max(e0, result.hi), bits, work)


def _weights(values: Sequence[Scalar]) -> tuple[Q, ...]:
    w = tuple(map(rational, values))
    if not w or any(v <= 0 for v in w):
        raise ValueError("nonempty positive fixed weights required")
    return w


def weighted_log_norm_upper(jacobian: Sequence[Sequence[Interval]],
                            weights: Sequence[Scalar]) -> Q:
    """Exact box upper for max_i(A_ii + sum_{j!=i}|A_ij|s_j/s_i)."""
    w = _weights(weights)
    if len(jacobian) != len(w) or any(len(row) != len(w) for row in jacobian):
        raise ValueError("Jacobian/weight shape mismatch")
    if any(not isinstance(a, Interval) for row in jacobian for a in row):
        raise ValueError("Jacobian entries must be intervals")
    return max(row[i].hi + sum(max(abs(a.lo), abs(a.hi))*w[j]/w[i]
                              for j, a in enumerate(row) if j != i)
               for i, row in enumerate(jacobian))


def box_margin(path_ranges: Sequence[Interval], lower: Sequence[Scalar | None],
               upper: Sequence[Scalar | None], weights: Sequence[Scalar]) -> Q:
    """Radius to a declared physical box in the FIXED weighted infinity norm.

    Supplied path ranges must cover the whole segment. None means no constraint
    on that side, not a physical zero. At least one constrained side is required.
    """
    w = _weights(weights)
    if not (len(path_ranges) == len(lower) == len(upper) == len(w)):
        raise ValueError("box/weight shape mismatch")
    margins = []
    for i, path in enumerate(path_ranges):
        if not isinstance(path, Interval):
            raise ValueError("path range must be an interval")
        lo = None if lower[i] is None else rational(lower[i])
        hi = None if upper[i] is None else rational(upper[i])
        if lo is not None and hi is not None and lo >= hi:
            raise ValueError("empty physical box")
        if lo is not None:
            margins.append((path.lo-lo)/w[i])
        if hi is not None:
            margins.append((hi-path.hi)/w[i])
    if not margins:
        raise ValueError("no declared physical box constraint")
    return min(margins)


def linear_observable_gain(coefficients: Sequence[Scalar],
                           weights: Sequence[Scalar]) -> Q:
    w = _weights(weights)
    a = tuple(map(rational, coefficients))
    if len(a) != len(w):
        raise ValueError("observable/weight shape mismatch")
    return sum(abs(ai)*wi for ai, wi in zip(a, w))


def evaluate_segment(*, e0: Scalar, numerical_defect: Scalar,
                     model_discrepancy: Scalar, mu: Scalar,
                     duration: Scalar, path_ranges: Sequence[Interval],
                     lower: Sequence[Scalar | None], upper: Sequence[Scalar | None],
                     weights: Sequence[Scalar], verified_tube_radius: Scalar,
                     bits: int = 128) -> dict:
    """Conditional algebra only; does not authenticate a supplied physical bound.

    Strict inclusion is required in BOTH the derivative-bound tube and the
    physical box. Actual H5 certificate fields intentionally remain null.
    """
    d, m, rho = map(rational, (numerical_defect, model_discrepancy, verified_tube_radius))
    if min(d, m) < 0 or rho <= 0:
        raise ValueError("invalid defect/model/tube bound")
    result = envelope(e0, d+m, mu, duration, bits)
    margin = box_margin(path_ranges, lower, upper, weights)
    inside = result.uniform_upper < min(rho, margin)
    return {
        "status": "CONDITIONAL_ALGEBRA_PASS" if inside else "TUBE_NOT_CLOSED",
        "endpoint_radius": result.endpoint.record(),
        "uniform_radius_upper": str(result.uniform_upper),
        "physical_box_margin": str(margin),
        "verified_tube_radius_as_supplied": str(rho),
        "physical_epsilon": None, "physical_outgoing_bound": None,
        "physical_M2": None, "actual_H5_coverage": "0/313",
        "L4_ready": False, "REI_activation": False,
        "conditions": "actual F, fixed norm, whole-tube Jacobian and defect, initial/model bounds and path provenance must be supplied and reviewed separately"
    }

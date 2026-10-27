"""Exact represented-history identities; no claim about the physical history.

Every input is a rational number or an exactly convertible finite binary64.
The represented causal domain excludes the final knot.  Values at that knot
exist as samples but cannot be queried.  No native C execution is performed.
"""
from bisect import bisect_left, bisect_right
from fractions import Fraction
import math


def rational(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("NONFINITE_INPUT")
    try:
        return Fraction(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("INVALID_RATIONAL_INPUT") from exc


class PiecewiseLinear:
    """Finite rational interpolant, with a strict causal right endpoint.

    Nonuniform grids are supported. A lazy sample callable is useful for a
    narrow local read of a large immutable binary64 history.
    """

    def __init__(self, knots, values, *, sample_count=None):
        self.knots = tuple(map(rational, knots))
        if len(self.knots) < 2 or any(a >= b for a, b in zip(self.knots, self.knots[1:])):
            raise ValueError("KNOTS_NOT_STRICTLY_INCREASING")
        if callable(values):
            if sample_count != len(self.knots):
                raise ValueError("SAMPLE_COUNT_MISMATCH")
            self._sample = values
        else:
            samples = tuple(map(rational, values))
            if len(samples) != len(self.knots):
                raise ValueError("SAMPLE_COUNT_MISMATCH")
            self._sample = samples.__getitem__
        self._cache = {}

    def sample(self, k):
        if k not in self._cache:
            self._cache[k] = rational(self._sample(k))
        return self._cache[k]

    def check(self, x):
        x = rational(x)
        if not self.knots[0] <= x < self.knots[-1]:
            raise ValueError("OUTSIDE_CAUSAL_DOMAIN")
        return x

    def cell(self, x):
        return bisect_right(self.knots, self.check(x)) - 1

    def cell_slope(self, k):
        if not 0 <= k < len(self.knots)-1:
            raise ValueError("EXTERIOR_DERIVATIVE")
        return (self.sample(k+1)-self.sample(k))/(self.knots[k+1]-self.knots[k])

    def value(self, x):
        x = self.check(x)
        k = self.cell(x)
        return self.sample(k)+(x-self.knots[k])*self.cell_slope(k)

    def directional_slope(self, x, direction):
        x = self.check(x)
        if direction == 0:
            raise ValueError("ZERO_DIRECTION_HAS_NO_DERIVATIVE_REQUEST")
        k = bisect_right(self.knots, x)-1 if direction > 0 else bisect_left(self.knots, x)-1
        return self.cell_slope(k)

    def jump(self, k):
        if not 0 < k < len(self.knots)-1:
            raise ValueError("NOT_AN_INTERIOR_KNOT")
        return self.cell_slope(k)-self.cell_slope(k-1)

    def retime(self, q, target):
        q, target = self.check(q), self.check(target)
        d = target-q
        if d == 0:
            return dict(step=d, direct=Fraction(0), signed=Fraction(0), bound=Fraction(0),
                        directional_slope=None, jump_terms=[])
        slope = self.directional_slope(q, d)
        direct = self.value(target)-self.value(q)-d*slope
        lo, hi = min(q, target), max(q, target)
        terms = []
        for k in range(bisect_right(self.knots, lo), bisect_left(self.knots, hi)):
            weight = target-self.knots[k] if d > 0 else self.knots[k]-target
            terms.append((k, weight, self.jump(k)))
        signed = sum((w*j for _, w, j in terms), Fraction(0))
        bound = sum((w*abs(j) for _, w, j in terms), Fraction(0))
        return dict(step=d, direct=direct, signed=signed, bound=bound,
                    directional_slope=slope, jump_terms=terms)

    def chord(self, a, x, b):
        a, x, b = self.check(a), self.check(x), self.check(b)
        if not a < x < b:
            raise ValueError("CHORD_REQUIRES_A_LT_X_LT_B")
        linear = ((b-x)*self.value(a)+(x-a)*self.value(b))/(b-a)
        direct = self.value(x)-linear
        terms = []
        for k in range(bisect_right(self.knots, a), bisect_left(self.knots, b)):
            t = self.knots[k]
            kernel = (t-a)*(b-x)/(b-a) if t <= x else (x-a)*(b-t)/(b-a)
            terms.append((k, kernel, self.jump(k)))
        signed = -sum((g*j for _, g, j in terms), Fraction(0))
        bound = sum((g*abs(j) for _, g, j in terms), Fraction(0))
        return dict(direct=direct, signed=signed, bound=bound, jump_terms=terms)

"""Directed Decimal intervals; precision and elementary rounding are contract inputs."""
from decimal import (Decimal, Context, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN,
                     InvalidOperation, DivisionByZero, Overflow, Underflow, Subnormal)
from fractions import Fraction

PRECISION = 80

def context(rounding):
    c = Context(prec=PRECISION, rounding=rounding, Emin=-999999, Emax=999999)
    for signal in (InvalidOperation, DivisionByZero, Overflow, Underflow, Subnormal):
        c.traps[signal] = True
    return c

DOWN, UP, NEAR = (context(r) for r in (ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN))

def valid(x):
    if not x.is_finite() or x.is_subnormal(NEAR):
        raise ValueError('nonfinite or subnormal Decimal')
    return x

def op(c, name, *args):
    c.clear_flags()
    result = valid(getattr(c, name)(*args))
    if any(c.flags[s] for s in (InvalidOperation, DivisionByZero, Overflow, Underflow, Subnormal)):
        raise ValueError('forbidden Decimal signal')
    return result

class I:
    def __init__(self, lo, hi=None):
        self.lo, self.hi = valid(Decimal(lo)), valid(Decimal(lo if hi is None else hi))
        if self.lo > self.hi:
            raise ValueError('reversed interval')

    @classmethod
    def exact(cls, x):
        if isinstance(x, cls): return x
        if isinstance(x, float): x = Fraction.from_float(x)
        if isinstance(x, Fraction):
            n, d = Decimal(x.numerator), Decimal(x.denominator)
            return cls(op(DOWN, 'divide', n, d), op(UP, 'divide', n, d))
        return cls(x)

    def __add__(self, other):
        v = I.exact(other)
        return I(op(DOWN, 'add', self.lo, v.lo), op(UP, 'add', self.hi, v.hi))
    __radd__ = __add__

    def __neg__(self): return I(self.hi.copy_negate(), self.lo.copy_negate())
    def __sub__(self, other): return self + (-I.exact(other))
    def __rsub__(self, other): return I.exact(other) + (-self)

    def __mul__(self, other):
        v = I.exact(other)
        pairs = [(a, b) for a in (self.lo, self.hi) for b in (v.lo, v.hi)]
        return I(min(op(DOWN, 'multiply', a, b) for a, b in pairs),
                 max(op(UP, 'multiply', a, b) for a, b in pairs))
    __rmul__ = __mul__

    def __truediv__(self, other):
        v = I.exact(other)
        if v.lo <= 0 <= v.hi: raise ValueError('division interval contains zero')
        reciprocal = I(op(DOWN, 'divide', Decimal(1), v.hi),
                       op(UP, 'divide', Decimal(1), v.lo))
        return self * reciprocal
    def __rtruediv__(self, other): return I.exact(other) / self

    def __abs__(self):
        if self.lo >= 0: return self
        if self.hi <= 0: return -self
        return I(0, max(self.lo.copy_abs(), self.hi.copy_abs()))

    def elementary(self, name):
        if name == 'ln' and self.lo <= 0: raise ValueError('ln domain')
        if name == 'sqrt' and self.lo < 0: raise ValueError('sqrt domain')
        def endpoint(x, lower):
            # Astra clarification before execution: use exact known identities
            # at each endpoint, including endpoints of non-singleton intervals.
            if (name == 'ln' and x == 1) or (name == 'sqrt' and x == 0):
                return Decimal(0)
            if name == 'exp' and x == 0: return Decimal(1)
            rounded = op(NEAR, name, x)
            return valid(NEAR.next_minus(rounded) if lower else NEAR.next_plus(rounded))
        # Python Decimal exp, ln and sqrt are correctly rounded HALF_EVEN.
        # One adjacent representable number on each side encloses exact values.
        return I(endpoint(self.lo, True), endpoint(self.hi, False))
    def exp(self): return self.elementary('exp')
    def ln(self): return self.elementary('ln')
    def sqrt(self): return self.elementary('sqrt')
    def expm1(self): return self.exp() - 1
    def contains(self, x): return self.lo <= x <= self.hi
    def overlaps(self, v): return self.lo <= v.hi and v.lo <= self.hi
    def packed(self): return {'lo': str(self.lo), 'hi': str(self.hi)}

def imax(values): return I(max(v.lo for v in values), max(v.hi for v in values))

def derivatives(x):
    w = (-x).exp()
    return w, -x*w, (x*x-x)*w, (-x*x*x+3*x*x-x)*w

def envelopes(xa, xb):
    if xa.lo <= 0 or xa.lo > xb.hi: raise ValueError('positive ordered x domain')
    rm, rp = (3-I(5).sqrt())/2, (3+I(5).sqrt())/2
    first = [abs(derivatives(xa)[1]), abs(derivatives(xb)[1])]
    second = [abs(derivatives(xa)[2]), abs(derivatives(xb)[2])]
    first_lower = [v.lo for v in first]
    second_lower = [v.lo for v in second]
    included = []
    span = I(xa.lo, xb.hi)
    for label, critical, order in [('x=1', I(1), 1), ('r_minus', rm, 2), ('r_plus', rp, 2)]:
        if span.overlaps(critical):
            candidate = abs(derivatives(critical)[order])
            (first if order == 1 else second).append(candidate)
            # Overlap licenses an upper candidate only. An interval lower
            # endpoint for the true supremum needs a proved interior point.
            if xa.hi <= critical.lo and critical.hi <= xb.lo:
                (first_lower if order == 1 else second_lower).append(candidate.lo)
            included.append(label)
    monotone = xa.lo > rp.hi
    if monotone:
        first, second = [abs(derivatives(xa)[1])], [abs(derivatives(xa)[2])]
        first_lower, second_lower = [first[0].lo], [second[0].lo]
    return I(max(first_lower),max(v.hi for v in first)), I(max(second_lower),max(v.hi for v in second)), included, monotone

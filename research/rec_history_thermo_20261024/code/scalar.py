"""Six-axis forward arithmetic; complex oracle never instantiates Dual.

Only scalar elementary operations are differentiated. There is no derivative
of a matrix solver here: the implicit equation is differentiated explicitly.
"""
import math
import cmath
import numpy as np


class Dual:
    __slots__ = ('v', 'd')
    def __init__(self, value, derivative=None):
        self.v = float(value)
        self.d = np.zeros(6) if derivative is None else np.asarray(derivative, dtype=float)
        if self.d.shape != (6,):
            raise ValueError('DUAL_SHAPE')
    def __add__(self, other):
        return Dual(self.v + real(other), self.d + tangent(other))
    __radd__ = __add__
    def __neg__(self):
        return Dual(-self.v, -self.d)
    def __sub__(self, other):
        return self + (-other)
    def __rsub__(self, other):
        return -self + other
    def __mul__(self, other):
        return Dual(self.v * real(other), self.d * real(other) + self.v * tangent(other))
    __rmul__ = __mul__
    def __truediv__(self, other):
        v = real(other)
        return Dual(self.v / v, (self.d - (self.v/v) * tangent(other)) / v)
    def __rtruediv__(self, other):
        return Dual(real(other), tangent(other)) / self
    def __pow__(self, power):
        return Dual(self.v**power, power * self.v**(power-1) * self.d)


def real(x):
    return x.v if isinstance(x, Dual) else float(np.real(x))


def tangent(x):
    return x.d if isinstance(x, Dual) else np.zeros(6)


def exp(x):
    if isinstance(x, Dual):
        v = math.exp(x.v)
        return Dual(v, v*x.d)
    return cmath.exp(x) if np.iscomplexobj(x) else math.exp(x)


def expm1(x):
    if isinstance(x, Dual):
        return Dual(math.expm1(x.v), math.exp(x.v)*x.d)
    return np.expm1(x).item() if np.iscomplexobj(x) else math.expm1(x)


def log(x):
    if isinstance(x, Dual):
        return Dual(math.log(x.v), x.d/x.v)
    return cmath.log(x) if np.iscomplexobj(x) else math.log(x)


def split(values):
    """Convert scalar list/object array to value array and six tangent axes."""
    a = np.asarray(values, dtype=object)
    complex_mode = any(np.iscomplexobj(x) for x in a.flat if not isinstance(x, Dual))
    v = np.zeros(a.shape, dtype=complex if complex_mode else float)
    d = np.zeros(a.shape+(6,))
    for i in np.ndindex(a.shape):
        x = a[i]
        if isinstance(x, Dual):
            v[i], d[i] = x.v, x.d
        else:
            v[i] = x
    return v, d

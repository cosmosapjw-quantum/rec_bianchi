"""Isolated positive-rate Hermite interval oracle for a frozen LRS Bianchi-I background.

SCOPED RESEARCH REFERENCE, NOT a production solver or native driver patch.
Default parameter values reproduce the *mathematical expressions* of the AXBI
background; binary64 reassociation is not claimed to preserve native bit identity.
Both dt and db integrate the same interpolated F(L)=1/H(L); s(L) is exact in
this prescribed homogeneous family. No production state, source, or checkpoint I/O.
"""
from __future__ import annotations
from dataclasses import dataclass
import bisect
import math

A_REF = 1.0/21.0
A_END = 0.2
H0 = 67.4 * 1e5 / 3.0856775814913673e24
OMEGA_M = 0.315
OMEGA_R = 9.2e-5
OMEGA_LAMBDA = 1.0 - OMEGA_M - OMEGA_R


@dataclass(frozen=True)
class IntervalResult:
    a1: float
    a2: float
    delta_l: float
    delta_t_s: float
    delta_b: float
    cells_crossed: int


def _moments(z: float) -> tuple[float, float, float, float]:
    """Return M_n(z)=int_0^1 y^n exp(-z y)dy for n=0..3.

    Positive small z is the only production-relevant part of this proof harness.
    Uses the entire Taylor series with a deterministic term cutoff. This is not
    a directed-rounding numerical enclosure.
    """
    if not math.isfinite(z) or z < 0 or z > 0.1:
        raise ValueError("moment argument outside independently validated small-z domain")
    result=[]
    for n in range(4):
        term = 1.0
        parts = []
        for k in range(22):
            parts.append(term/(n+k+1))
            term *= -z/(k+1)
        result.append(math.fsum(parts))
    return tuple(result)


def _cubic_coeff(f0: float, f1: float, df0: float, df1: float, h: float):
    d=f1-f0
    return (f0, h*df0, 3*d-h*(2*df0+df1), -2*d+h*(df0+df1))


def _eval_segment(coeff, u: float, v: float, h: float, s_left: float):
    """Integrals over [u,u+v] in a cell of width h, using no cumulative subtraction."""
    if not(0 <= u <= 1 and 0 <= v and u+v <= 1+5e-12 and h > 0):
        raise ValueError("invalid Hermite segment")
    c0,c1,c2,c3=coeff
    a0=((c3*u+c2)*u+c1)*u+c0
    a1=v*(c1+2*c2*u+3*c3*u*u)
    a2=v*v*(c2+3*c3*u)
    a3=v*v*v*c3
    dx=h*v
    dt=dx*math.fsum((a0,a1/2.0,a2/3.0,a3/4.0))
    m=_moments(3*dx)
    db=0.0 if s_left==0.0 else dx*s_left*math.fsum((a0*m[0],a1*m[1],a2*m[2],a3*m[3]))
    return dt,db


class PrescribedBackground:
    """Immutable source-bound mathematical background and local reference table."""
    def __init__(self, q_ref: float, cells:int=1024, same_h:bool=False):
        if not math.isfinite(q_ref): raise ValueError("nonfinite signed shear")
        if cells not in (1024,2048): raise ValueError("only frozen prototype meshes")
        self.q_ref=float(q_ref);self.cells=cells;self.same_h=bool(same_h)
        self.l_end=math.log(A_END/A_REF)
        self.h=self.l_end/cells
        self.s_ref=q_ref*self.h_flrw(A_REF)
        self.c0=H0**2*OMEGA_LAMBDA
        self.c3=H0**2*OMEGA_M/A_REF**3
        self.c4=H0**2*OMEGA_R/A_REF**4
        self.c6=0.0 if same_h else self.s_ref**2
        self._coeff=[]
        self._a_knots=[]
        for j in range(cells+1):
            L=j*self.h
            self._a_knots.append(A_REF if j==0 else A_END if j==cells else A_REF*math.exp(L))
        if not all(b>a for a,b in zip(self._a_knots,self._a_knots[1:])):
            raise ValueError("non-increasing binary64 knots")
        for j in range(cells):
            l0=j*self.h;l1=(j+1)*self.h
            f0,d0=self.rate_and_slope(l0)
            f1,d1=self.rate_and_slope(l1)
            self._coeff.append(_cubic_coeff(f0,f1,d0,d1,self.h))

    @staticmethod
    def h_flrw(a:float)->float:
        return H0*math.sqrt(OMEGA_M/a**3+OMEGA_R/a**4+OMEGA_LAMBDA)

    def rate_and_slope(self,L:float):
        e3=math.exp(-3*L);e4=math.exp(-4*L);e6=math.exp(-6*L)
        terms=(self.c0,self.c3*e3,self.c4*e4,self.c6*e6)
        S=math.fsum(terms)
        if not S>0:raise ValueError("nonpositive H squared")
        F=1/math.sqrt(S)
        moment=math.fsum((3*terms[1],4*terms[2],6*terms[3]))/S
        return F,0.5*moment*F

    def interval(self,a1:float,a2:float)->IntervalResult:
        if not (math.isfinite(a1) and math.isfinite(a2) and A_REF<=a1<a2<=A_END):
            raise ValueError("nonfinite, reversed, or outside chosen physical domain")
        dl=math.log1p((a2-a1)/a1)
        if dl<=0:raise ValueError("collapsed increment")
        idx=max(0,min(self.cells-1,bisect.bisect_right(self._a_knots,a1)-1))
        curr=a1
        dt_list=[];db_list=[];counts=0
        while curr<a2:
            if idx>=self.cells: raise ValueError("end of domain without interval completion")
            node=self._a_knots[idx]
            right=min(a2,self._a_knots[idx+1])
            if right<=curr: raise ValueError("grid interval stagnation")
            # Local coordinates are formed from actual binary64 supplied scale factors.
            # Avoid subtraction of independently computed cumulative logarithms.
            u=math.log1p((curr-node)/node)/self.h
            v=math.log1p((right-curr)/curr)/self.h
            if not(0. <= u <= 1.): raise ValueError("out-of-cell interpolation coordinate")
            if u+v>1+1e-10: raise ValueError("inconsistent knot geometry")
            if v<=0: raise ValueError("nonpositive local cell coordinate")
            s_left=self.s_ref*(A_REF/curr)**3
            dt,db=_eval_segment(self._coeff[idx],u,v,self.h,s_left)
            if not dt>0:raise ValueError("nonpositive clock increment")
            dt_list.append(dt);db_list.append(db);counts+=1
            curr=right;idx+=1
            if counts>self.cells+1:raise ValueError("oversized cell traversal")
        return IntervalResult(a1,a2,dl,math.fsum(dt_list),math.fsum(db_list),counts)


def photon_map(mu_initial:float,delta_l:float,delta_b:float):
    """Exact kinematic moment map for a collisionless null ray, not scattering."""
    if not(all(math.isfinite(v) for v in (mu_initial,delta_l,delta_b)) and abs(mu_initial)<=1):
        raise ValueError("invalid ray or geometry")
    ep=math.exp(2*delta_b);ez=math.exp(-4*delta_b)
    R=math.sqrt(ep*(1-mu_initial*mu_initial)+ez*mu_initial*mu_initial)
    mu_final=mu_initial*math.sqrt(ez)/R
    return {'energy_ratio':math.exp(-delta_l)*R,'mu_final':mu_final,'solid_angle_jacobian':R**-3}


def ideal_error(h:float)->float:
    if not h>=0:raise ValueError("invalid h")
    return 30537*math.exp(3*h)*h**4/384


def conditional_clock_bound(ideal_relative:float,node_relative:float,local_eval_relative:float,N:int)->float:
    if N<1 or min(ideal_relative,node_relative,local_eval_relative)<0:
        raise ValueError("invalid bound components")
    unit=2.0**-53
    k=(N-1)*unit
    if k>=1:raise ValueError("roundoff standard model inapplicable")
    # The local floating-evaluation relative bound is with respect to the
    # ideal computed polynomial increment, not the unknown exact integral.
    # Its interaction with interpolation/node error cannot be omitted.
    eta_poly=ideal_relative+node_relative
    eta=eta_poly+(1+eta_poly)*local_eval_relative
    return eta+(1+eta)*k/(1-k)

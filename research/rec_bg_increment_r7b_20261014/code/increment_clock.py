"""Research-only positive rate-Hermite clock/shear increments.

The ideal-arithmetic interpolation bound is not a bound on Python/libm rounding
or a chemistry history. No production solver is imported or launched.
"""
from __future__ import annotations
from dataclasses import dataclass
from bisect import bisect_right
import math

def local_width(a:float,b:float)->float:
    """Logarithmic width of the actual supplied binary64 endpoints."""
    if not(math.isfinite(a) and math.isfinite(b) and 0<a<b):
        raise ValueError('ENDPOINT_DOMAIN_OR_ORDER')
    return math.log1p((b-a)/a)

@dataclass(frozen=True)
class Background:
    h0:float=67.4*1e5/3.0856775814913673e24
    omega_m:float=.315
    omega_r:float=9.2e-5
    omega_lambda:float=1-.315-9.2e-5
    q:float=0.
    same_h:bool=False
    a_ref:float=1/21
    a_end:float=.2
    def __post_init__(self):
        vals=(self.h0,self.omega_m,self.omega_r,self.omega_lambda,self.q,self.a_ref,self.a_end)
        if not all(map(math.isfinite,vals)) or self.h0<=0 or self.a_ref<=0 or self.a_end<=self.a_ref:
            raise ValueError('MODEL_DOMAIN')
        if min(self.omega_m,self.omega_r,self.omega_lambda)<0 or self.omega_m+self.omega_r+self.omega_lambda<=0:
            raise ValueError('DENSITY_DOMAIN')
    def hf(self,a:float)->float:
        return self.h0*math.sqrt(self.omega_m/a**3+self.omega_r/a**4+self.omega_lambda)
    def shear(self,a:float)->float:
        return self.q*self.hf(self.a_ref)*(self.a_ref/a)**3
    def integrand(self,a:float)->tuple[float,float]:
        """F=dt/dln(a) [s], F' [s], exact analytic slope in real arithmetic."""
        if not(math.isfinite(a) and self.a_ref<=a<=self.a_end):raise ValueError('SCALE_DOMAIN')
        hf=self.hf(a);s=self.shear(a);h=hf if self.same_h else math.hypot(hf,s)
        terms=(self.h0**2*self.omega_lambda,self.h0**2*self.omega_m/a**3,
               self.h0**2*self.omega_r/a**4,0. if self.same_h else s*s)
        m1=math.fsum(p*c for p,c in zip((0,3,4,6),terms))/(h*h)
        f=1/h
        return f,.5*m1*f

def exp_moment(k:int,z:float)->float:
    """Integral_0^1 u^k exp(-z*u) du, 13 terms for 0<=z<.1.

    The omitted ideal series has magnitude at most z^13/(13!*(14+k)).
    Floating evaluation is separately checked, not interval certified.
    """
    if k not in range(4) or not(0<=z<.1):raise ValueError('MOMENT_DOMAIN')
    term=1.;terms=[]
    for n in range(13):
        terms.append(term/(n+k+1));term*=-z/(n+1)
    return math.fsum(terms)

class RateHermite:
    """Immutable-model local integrator; uses no cumulative clock subtraction.

    One F interpolant serves dt and db=s(a)*dt. Algebraic H and shear remain
    background functions; no independent b-rate or H interpolation is used.
    """
    def __init__(self,background:Background,intervals:int=1024):
        if not isinstance(intervals,int) or intervals<64 or intervals>65536:raise ValueError('GRID_DOMAIN')
        self._background=background
        ar,ae=background.a_ref,background.a_end
        span=local_width(ar,ae)
        self.knots=tuple(ar if i==0 else ae if i==intervals else ar*math.exp(span*i/intervals) for i in range(intervals+1))
        self.cells=[];controls=[]
        fd=[background.integrand(a) for a in self.knots]
        for i in range(intervals):
            h=local_width(self.knots[i],self.knots[i+1]);f0,d0=fd[i];f1,d1=fd[i+1]
            if h>=1/3:raise ValueError('CELL_WIDTH_DOMAIN')
            df=f1-f0
            c=(f0,h*d0,3*df-h*(2*d0+d1),-2*df+h*(d0+d1))
            bc=(f0,f0+h*d0/3,f1-h*d1/3,f1)
            if min(bc)<=0:raise ValueError('BERNSTEIN_POSITIVITY')
            self.cells.append((h,c));controls.extend(bc)
        self.cells=tuple(self.cells)
        self.minimum_bernstein_control=min(controls)
        self.max_cell_width=max(h for h,c in self.cells)
        h=self.max_cell_width
        self.ideal_relative_bound=30537*math.exp(3*h)*h**4/384
    @property
    def background(self)->Background:
        """Read-only binding; the model cannot be replaced with stale coefficients."""
        return self._background

    def increment(self,a:float,b:float)->tuple[float,float]:
        local_width(a,b)
        bg=self.background
        if a<bg.a_ref or b>bg.a_end:raise ValueError('SCALE_DOMAIN')
        tparts=[];bparts=[];left=a
        j=min(bisect_right(self.knots,left)-1,len(self.cells)-1)
        while left<b:
            right=min(b,self.knots[j+1]);h,c=self.cells[j]
            x=0. if left==self.knots[j] else math.log1p((left-self.knots[j])/self.knots[j])/h
            dL=local_width(left,right);du=dL/h
            c0,c1,c2,c3=c
            p=(c0+x*(c1+x*(c2+x*c3)),
               c1+x*(2*c2+3*x*c3),c2+3*x*c3,c3)
            terms=(p[0],p[1]*du,p[2]*du*du,p[3]*du**3)
            dt=dL*math.fsum(terms[k]/(k+1) for k in range(4))
            db=bg.shear(left)*dL*math.fsum(terms[k]*exp_moment(k,3*dL) for k in range(4))
            if not(math.isfinite(dt) and math.isfinite(db) and dt>0):raise ArithmeticError('INCREMENT_DOMAIN')
            tparts.append(dt);bparts.append(db)
            left=right;j+=1
        return math.fsum(tparts),math.fsum(bparts)

def photon_step(dL:float,db:float,mu:float)->tuple[float,float,float]:
    """Return ln(E2/E1), final direction cosine, dOmega2/dOmega1.

    mu is the initial local direction. Geometric optics, non-tilted Bianchi I.
    c,hbar,k_B remain physical constants; all ratios below are dimensionless.
    """
    if not all(map(math.isfinite,(dL,db,mu))) or abs(mu)>1 or abs(db)>.1:
        raise ValueError('PHOTON_DOMAIN')
    if abs(mu)==1:return -dL-2*db,mu,math.exp(6*db)
    if mu==0:return -dL+db,0.,math.exp(-3*db)
    z=(1-mu*mu)*math.expm1(2*db)+mu*mu*math.expm1(-4*db)
    logR=.5*math.log1p(z)
    return -dL+logR,mu*math.exp(-2*db-logR),math.exp(-3*logR)

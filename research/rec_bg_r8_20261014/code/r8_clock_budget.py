"""REC-BG-R8: conditional clock/error budgets, NOT native trajectory validation.

All bounds assume a prescribed positive H^2=sum C_p exp(-pL), p in {0,3,4,6},
C_p >=0 and exact Hermite endpoint values/slopes unless node error is explicit.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

K4 = 30537
UNIT_ROUNDOFF = 2.0 ** -53
FROZEN_RELATIVE_INCREMENT_GATE = 1e-9


def hermite_basis(u: float) -> tuple[float, float, float, float]:
    if not 0 <= u <= 1: raise ValueError("u must be in [0,1]")
    return (2*u**3-3*u*u+1, u*(1-u)**2, -2*u**3+3*u*u, u*u*(u-1))


def ideal_hermite_relative_error(h: float) -> float:
    if not (0 <= h < 1 and math.isfinite(h)):
        raise ValueError("h must be finite and in [0,1)")
    return (K4/384.0) * math.exp(3*h) * h**4


def gamma_n(additions: int, u: float = UNIT_ROUNDOFF) -> float:
    if additions < 0 or not 0 < u < 1 or additions*u >= 1:
        raise ValueError("invalid accumulation envelope")
    x=additions*u
    return x/(1-x)


def conditional_global_relative_error(increment_error:float, positive_addends:int) -> float:
    """Bound for positive increments each computed with relative <= increment_error;
    sequential rounded summation, n-1 rounded additions. No node or math-lib bound
    is supplied implicitly.
    """
    if not (0 <= increment_error < 1) or positive_addends < 1:
        raise ValueError("invalid conditional input")
    gamma=gamma_n(positive_addends-1)
    return increment_error + (1+increment_error)*gamma


def rate_data_relative_error(h:float, error_value:float, error_slope:float,
                             minimum_rate_value:float) -> float:
    """Exact Hermite interpolation perturbation only; units [F]=[F']=seconds.
    Sup |Fnode error|<=error_value and |F'node error|<=error_slope.
    """
    if min(error_value,error_slope) < 0 or minimum_rate_value <= 0:
        raise ValueError("signed or unphysical errors")
    if not math.isfinite(minimum_rate_value): raise ValueError("nonfinite minimum")
    return ideal_hermite_relative_error(h)+(error_value+h*error_slope/4)/minimum_rate_value


def native_span_minus_stable_relative(a1:float,a2:float,a_ref:float=1/21) -> float:
    if not (0<a_ref<=a1<a2 and all(map(math.isfinite,(a1,a2,a_ref)))):
        raise ValueError("incorrect ordered background interval")
    native=math.log(a2/a_ref)-math.log(a1/a_ref)
    stable=math.log1p((a2-a1)/a1)
    return native/stable-1


def optical_integrand_delta(nH:float, F:float, xe:float,
                             deltaF:float, deltaXe:float) -> tuple[float,float,float]:
    """δ(nH F xe) exact split with nH fixed at matched L;
    absolute Compton opacity prefactor sigma_T*c is deliberately external.
    """
    if nH<=0 or F<=0: raise ValueError("positive hydrogen density/clock needed")
    ion=nH*F*deltaXe
    clock=nH*xe*deltaF
    cross=nH*deltaF*deltaXe
    return ion,clock,cross


def baryon_density_at_scale(nH_ref:float,a_ref:float,a:float) -> float:
    if min(nH_ref,a_ref,a)<=0:raise ValueError("positive baryon/cosmology inputs")
    return nH_ref*(a_ref/a)**3


def r8_frozen_budget() -> dict:
    """Illustrative ideal 1024/2048 node-only bound at 312237 positive increments;
    not a measured full-history numerical error bar.
    """
    eps_1024=431751417531032299779/1401457724289449984000000000000
    eps_2048=431751417531032299779/22470660862741839872000000000000
    n=312237
    tend=42794891441558000.0
    g=gamma_n(n-1)
    return {"N_increments":n,"t_end_saved_s":tend,"gamma_n_minus_1":g,
            "theorem_only":{str(N):{"ideal_relative":eps,
            "conditional_global_relative":conditional_global_relative_error(eps,n),
            "conditional_global_abs_s":conditional_global_relative_error(eps,n)*tend}
            for N,eps in [(1024,eps_1024),(2048,eps_2048)]},
            "required_unknowns":["endpoint F and F' evaluation errors", "stable integration floating roundoff", "same-interval source/chemistry numerical convergence", "actual native method adoption and call-site coverage"]}


if __name__ == "__main__":
    import json
    print(json.dumps(r8_frozen_budget(),indent=2,ensure_ascii=False))

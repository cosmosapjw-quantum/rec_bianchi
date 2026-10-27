"""Synthetic conditional defect stability calculations; not REC-H5 physical certificate."""
from math import exp, expm1, isfinite

def constant_envelope(e0, defect, mu, duration):
    if not all(isfinite(x) for x in (e0, defect, mu, duration)):
        raise ValueError("nonfinite")
    if e0 < 0 or defect < 0 or duration < 0:
        raise ValueError("negative bound/time")
    if mu == 0:
        return e0 + defect * duration
    return e0 * exp(mu * duration) + defect * expm1(mu * duration) / mu

def tube_status(approx_min, radius):
    if not all(isfinite(x) for x in (approx_min, radius)) or radius < 0:
        raise ValueError("invalid tube")
    return "CONDITIONAL_POSITIVE" if approx_min > radius else "UNRESOLVED"

if __name__ == "__main__":
    from math import exp
    assert abs(constant_envelope(.01,.02,0,2)-.05)<1e-15
    assert abs(constant_envelope(0,.02,-2,10)-.01*(1-exp(-20)))<1e-15
    assert abs(constant_envelope(.01,0,1,2)-.01*exp(2))<1e-15
    assert tube_status(.2,.1)=="CONDITIONAL_POSITIVE"
    assert tube_status(.1,.1)=="UNRESOLVED"
    for args in [(-1,0,0,1),(0,-1,0,1),(0,0,0,-1)]:
        try: constant_envelope(*args)
        except ValueError: pass
        else: raise AssertionError(args)
    print("7 synthetic conditional checks PASS; physical H5 NOT_RUN")

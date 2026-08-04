import math
import numpy as np
from scipy.integrate import quad

from full_bianchi_hyrec.recoil.analytic_pole_crossed_average import (
    analytic_mean_pole_crossed_amplitude_squared,
    conditional_pole_crossed_parameters,
    gaussian_resolvent,
)

M=1.673532840653473e-27
T=3000.0
NU_I=2466067545792234.0
NU_A=2466067559187777.0
DNU=57874121512.55733
GAMMA=49855285.92353622
F=0.4161967179799824


def test_gaussian_resolvent_matches_direct_complex_integral():
    for pole in [1.2+0.3j, -2.1+0.02j, 0.7-0.4j, -1.3-0.01j]:
        direct = quad(
            lambda z: (
                math.exp(-z*z/2)/math.sqrt(2*math.pi)/(z-pole)
            ).real,
            -14,14,epsabs=1e-12,epsrel=1e-12,limit=500,
        )[0] + 1j*quad(
            lambda z: (
                math.exp(-z*z/2)/math.sqrt(2*math.pi)/(z-pole)
            ).imag,
            -14,14,epsabs=1e-12,epsrel=1e-12,limit=500,
        )[0]
        assert abs(gaussian_resolvent(pole)/direct-1) < 2e-13


def test_crossed_slope_is_opposite_to_pole_slope():
    p=conditional_pole_crossed_parameters(
        NU_A-3*DNU,NU_A+1*DNU,0.5,
        mass_kg=M,temperature_K=T,nu_internal_hz=NU_I,
        gamma_half_width_hz=GAMMA,
    )
    scale=max(abs(p.pole_slope_B_hz),abs(p.crossed_slope_D_hz),1.0)
    assert abs(p.pole_slope_B_hz+p.crossed_slope_D_hz)/scale < 5e-15


def test_analytic_pole_crossed_matches_direct_gaussian_integral():
    cases=[
        (NU_A-3*DNU,NU_A+1*DNU,0.5),
        (NU_A-4*DNU,NU_A-4*DNU,-1.0),
        (NU_A+2*DNU,NU_A-1*DNU,-0.7071067811865476),
        (NU_A+4*DNU,NU_A-4*DNU,0.816496580927726),
    ]
    for nu_s,nu_t,mu in cases:
        components,p=analytic_mean_pole_crossed_amplitude_squared(
            nu_s,nu_t,mu,
            mass_kg=M,temperature_K=T,nu_internal_hz=NU_I,
            gamma_half_width_hz=GAMMA,oscillator_strength=F,
        )
        scale=-0.5*F*NU_I
        A=p.pole_detuning_A_hz; B=p.pole_slope_B_hz
        C=p.crossed_detuning_C_hz; D=p.crossed_slope_D_hz
        integrand=lambda z: (
            math.exp(-z*z/2)/math.sqrt(2*math.pi)
            * abs(scale*(
                1/(A+B*z-1j*GAMMA)
                +1/(C+D*z+1j*GAMMA)
            ))**2
        )
        points=[]
        if abs(B)>0:
            z0=-A/B
            if -14<z0<14: points.append(z0)
        direct=quad(
            integrand,-14,14,points=points or None,
            epsabs=2e-8,epsrel=3e-11,limit=800,
        )[0]
        assert abs(components.total/direct-1) < 5e-10
        assert abs(components.total-(components.pole+components.crossed+components.interference)) < 5e-12*components.total


def test_collinear_case_is_finite():
    components,p=analytic_mean_pole_crossed_amplitude_squared(
        NU_A-4*DNU,NU_A-4*DNU,-1.0,
        mass_kg=M,temperature_K=T,nu_internal_hz=NU_I,
        gamma_half_width_hz=GAMMA,oscillator_strength=F,
    )
    assert p.pole_slope_B_hz == 0.0
    assert p.crossed_slope_D_hz == 0.0
    assert components.total > 0.0
    assert math.isfinite(components.total)

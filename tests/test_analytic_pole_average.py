import math
import numpy as np
from scipy.integrate import quad
from full_bianchi_hyrec.recoil.analytic_pole_average import analytic_mean_pole_amplitude_squared

M=1.673532840653473e-27
T=3000.0
NU_I=2466067545792234.0
NU_A=2466067559187777.0
DNU=57874121512.55733
GAMMA=49855285.92353622
F=0.4161967179799824

def test_cache_anchor():
    value, p = analytic_mean_pole_amplitude_squared(
        NU_A-4*DNU,NU_A+1*DNU,0.5,
        mass_kg=M,temperature_K=T,nu_internal_hz=NU_I,
        gamma_half_width_hz=GAMMA,oscillator_strength=F)
    assert value > 0
    assert math.isfinite(p.pole_width_t)

def test_numeric_gaussian_integral():
    nu_s=NU_A-3*DNU; nu_t=NU_A+1*DNU; mu=0.5
    value,p=analytic_mean_pole_amplitude_squared(
        nu_s,nu_t,mu,mass_kg=M,temperature_K=T,nu_internal_hz=NU_I,
        gamma_half_width_hz=GAMMA,oscillator_strength=F)
    C=-0.5*F*NU_I
    A=p.detuning_A_hz; B=p.gaussian_slope_B_hz
    integrand=lambda z: math.exp(-z*z/2)/math.sqrt(2*math.pi)*C*C/((A+B*z)**2+GAMMA**2)
    points=[] if not math.isfinite(p.pole_location_t) else [math.sqrt(2)*p.pole_location_t]
    direct=quad(integrand,-14,14,points=points or None,epsabs=1e-8,epsrel=2e-11,limit=600)[0]
    assert abs(value/direct-1)<3e-10

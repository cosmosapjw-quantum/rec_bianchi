"""C7 exact finite-time source and collisionless null-ray checks using REAL REC operators.

This is prescribed (normal-comoving) LRS Bianchi I, not a native HyRec run.
"""
from __future__ import annotations
import math

import numpy as np
import pytest

from full_bianchi_hyrec.background import (
    AxisymmetricBianchiIBackground, FiniteBianchiIIncrement,
    axisymmetric_photon_map, normal_frame_characteristic
)
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    CharacteristicAngularSolver, IsotropicTransferCoefficients,
    constant_coefficient_transfer
)

F0=0.0015
EM=3.0e-20
CHI=4.0e-17
FACE_NU=2.4e15


def _fixture(q=0.01, samples=65, *, same_h=False):
    model=AxisymmetricBianchiIBackground(q_ref=q,same_h=same_h)
    a1,a2=model.a_ref,0.1
    span=model.interval(a1,a2)
    sequence=model.snapshots(np.linspace(0.0,span.delta_l,samples))
    return model,sequence,span


def _expected(model,span):
    return constant_coefficient_transfer(
        f_initial=F0,emissivity_s_inv=EM,
        opacity_s_inv=CHI,travel_time_s=span.delta_t_s,
    )


def _run(seq,source=None,n_step=64,em=EM,chi=CHI,f0=F0):
    solver=CharacteristicAngularSolver(seq,interval_source=source)
    mu=0.43
    phi=0.7
    n=np.array([
        math.sqrt(1-mu*mu)*math.cos(phi),
        math.sqrt(1-mu*mu)*math.sin(phi),mu
    ])
    res=solver.trace_to_face(
        tau_start=float(seq.tau[0]),tau_end=float(seq.tau[-1]),
        direction_hydrogen=n,face_frequency_Hz=FACE_NU,
        initial_occupation=f0,
        coefficients=IsotropicTransferCoefficients(
            lambda tau,nu:em,lambda tau,nu:chi
        ),n_step=n_step,
    )
    return res,mu,n


@pytest.mark.parametrize("q,same_h", [
    (0.0,False),(0.01,False),(-0.01,False),(0.005,True)
])
def test_finite_interval_clock_closes_actual_transfer_source(q,same_h):
    model,seq,span=_fixture(q,same_h=same_h)
    res,_,_=_run(seq,source=model,n_step=64)
    true=_expected(model,span)
    assert res.occupation_face>0
    assert abs(res.occupation_face/true-1)<5e-12


def test_previous_midpoint_duration_is_observably_less_accurate():
    model,seq,span=_fixture()
    new,_,_=_run(seq,source=model,n_step=64)
    old,_,_=_run(seq,source=None,n_step=64)
    exact=_expected(model,span)
    assert abs(new.occupation_face/exact-1)<5e-12
    assert abs(old.occupation_face/exact-1)>1e-8
    assert abs(new.occupation_face-exact)<abs(old.occupation_face-exact)/1000


def test_bianchi_photon_null_invariant_under_existing_characteristic_solver():
    model,seq,span=_fixture(samples=1025)
    res,mu_final,face_vec=_run(seq,source=model,n_step=512,em=0.0,chi=0.0)
    backwards=axisymmetric_photon_map(
        mu_final,
        FiniteBianchiIIncrement(0.1,model.a_ref,
        -span.delta_l,-span.delta_t_s,-span.delta_b,1)
    )
    nu_initial=FACE_NU*backwards["energy_ratio"]
    assert abs(res.initial_frequency_Hz/nu_initial-1)<1e-8
    assert abs(res.initial_direction_hydrogen[2]-backwards["mu_final"])<1e-8
    assert abs(res.occupation_face/F0-1)<1e-13
    # Translation Killing momenta K_i=a*exp(beta_i)*nu*n_i remain constant.
    n1=res.initial_direction_hydrogen
    p1=model.a_ref*np.array([math.exp(-model.b_ref),math.exp(-model.b_ref),math.exp(2*model.b_ref)])*nu_initial*n1
    n2=face_vec
    b2=model.point(0.1).b
    p2=0.1*np.array([math.exp(-b2),math.exp(-b2),math.exp(2*b2)])*FACE_NU*n2
    assert np.linalg.norm(p2-p1)/np.linalg.norm(p1)<1e-8


def test_local_characteristic_is_derivative_of_analytic_finite_ray_map():
    model=AxisymmetricBianchiIBackground(q_ref=0.01)
    a=0.08
    point=model.point(a)
    # The snapshot is the actual package geometry, not manufactured tensors.
    seq=model.snapshots(np.array([0.,math.log(a/model.a_ref)]))
    snapshot=seq.snapshot_at_tau(seq.tau[-1])
    mu=0.41
    direction=np.array([math.sqrt(1-mu**2),0.0,mu])
    native=normal_frame_characteristic(snapshot,direction)
    Lspeed=(native.R_normal_s_inv/point.H_s_inv)
    direction_speed=native.D0_direction_normal_s_inv[2]/point.H_s_inv
    assert abs(Lspeed+1.0+(point.s_s_inv/point.H_s_inv)*(3*mu*mu-1.0))<1e-13
    assert abs(direction_speed+3*(point.s_s_inv/point.H_s_inv)*mu*(1-mu*mu))<1e-13


def test_provider_identity_and_anchor_fail_closed():
    m,seq,_=_fixture()
    with pytest.raises(ValueError,match="identity|source"):
        CharacteristicAngularSolver(seq,interval_source=AxisymmetricBianchiIBackground(q_ref=-0.01))
    with pytest.raises(ValueError,match="identity|source|Bianchi"):
        # Same curve family but different numerical method identity is excluded.
        CharacteristicAngularSolver(seq,interval_source=AxisymmetricBianchiIBackground(q_ref=0.01,cells=2048))


def test_flrw_baryon_and_adiabatic_temperature_scalings():
    model,seq,span=_fixture(q=0.0)
    for a in (model.a_ref,0.06,0.1):
        pt=model.point(a)
        b=pt.b
        volume=(a*math.exp(-b))**2*(a*math.exp(2*b))
        assert math.isclose(volume,a**3,rel_tol=4e-15)
        n0=0.2
        n=n0*(model.a_ref/a)**3
        assert abs(n*volume/(n0*model.a_ref**3)-1)<4e-15
        T0=100
        T=T0*(model.a_ref/a)**2
        assert abs(T*a*a/(T0*model.a_ref**2)-1)<4e-15


def test_exact_stationary_source_and_no_opacity_limits():
    model,seq,_=_fixture(q=-0.01)
    f=0.0011
    for chi,j in ((0.0,0.0),(2e-17,2e-17*f)):
        out,_,_=_run(seq,source=model,n_step=64,em=j,chi=chi,f0=f)
        assert abs(out.occupation_face/f-1)<5e-12

def test_bound_interval_source_rejects_internal_snapshot_tampering():
    from dataclasses import replace

    model, seq, _ = _fixture(samples=65)
    h = np.array(seq.H_s_inv, copy=True)
    h[h.size // 2] *= 1.02
    # The declared model hash stays unchanged: this deliberately tests whether
    # the actual numerical snapshot array is checked, not just its metadata.
    counterfeit = replace(seq, H_s_inv=h)
    with pytest.raises(ValueError, match="mismatch|source|identity"):
        CharacteristicAngularSolver(counterfeit, interval_source=model)


def test_genuine_Bianchi_background_Hamiltonian_and_shear_decay():
    model=AxisymmetricBianchiIBackground(q_ref=0.01)
    cosmology=model.cosmology
    href=cosmology.hubble_flrw(model.a_ref)
    for a in (model.a_ref,0.061,0.1,model.a_end):
        pt=model.point(a)
        sigma2=pt.s_s_inv**2
        Hf=cosmology.hubble_flrw(a)
        assert abs((pt.H_s_inv**2-Hf**2-sigma2)/pt.H_s_inv**2)<1e-14
        assert abs((pt.s_s_inv/(0.01*href))/(model.a_ref/a)**3-1)<1e-14
        assert abs(-1-pt.deceleration_q+(.5*(3*cosmology.omega_m/a**3 +4*cosmology.omega_r/a**4 + 6*(.01*href/cosmology.h0_per_s)**2*(model.a_ref/a)**6)*cosmology.h0_per_s**2)/(pt.H_s_inv**2))<1e-12


def test_actual_nonstationary_source_tracks_independent_proper_time_ode():
    from scipy.integrate import solve_ivp

    model, seq, span = _fixture(samples=513)
    m = model.cosmology
    Href=m.hubble_flrw(model.a_ref)

    def source(eta):
        return 3e-20*(1+0.1*math.sin(3*eta)), 4e-17*(1+0.03*math.cos(eta))

    def rhs(eta, y):
        a=model.a_ref*math.exp(eta)
        s=model.q_ref*Href*(model.a_ref/a)**3
        H=math.sqrt(m.hubble_flrw(a)**2+s**2)
        j,chi=source(eta)
        return [(j-chi*y[0])/H]

    ref=solve_ivp(rhs,(0,span.delta_l),[F0],
                  method="DOP853",rtol=2e-12,atol=2e-16)
    assert ref.success
    target=float(ref.y[0,-1])

    values=[]
    for steps in (64,128,256):
        solver=CharacteristicAngularSolver(seq,interval_source=model)
        mu=.43
        n=np.array([math.sqrt(1-mu*mu),0.,mu])
        out=solver.trace_to_face(
           tau_start=0.,tau_end=span.delta_l,
           direction_hydrogen=n,face_frequency_Hz=FACE_NU,
           initial_occupation=F0,coefficients=IsotropicTransferCoefficients(
             emissivity_s_inv=lambda tau,nu:source(tau)[0],
             opacity_s_inv=lambda tau,nu:source(tau)[1]
           ),n_step=steps)
        values.append(abs(out.occupation_face-target))
    assert values[0]>values[1]>values[2]
    assert values[0]/values[1]>3.4
    assert values[1]/values[2]>3.2
    assert values[2]/target<5e-7

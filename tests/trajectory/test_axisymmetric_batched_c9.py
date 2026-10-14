"""C9: exact Bianchi-I rays with batched source integration.

Tests compare the new vectorized, analytic-null-map option with independent
continuum invariants and the existing positive characteristic reference.
"""
from __future__ import annotations

import math
import numpy as np
import pytest
from scipy.integrate import solve_ivp

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground
from full_bianchi_hyrec.trajectory.axisymmetric_batched import (
    AxisymmetricBianchiIBatchSolver, BatchIsotropicCoefficients,
)
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    CharacteristicAngularSolver, IsotropicTransferCoefficients,
    constant_coefficient_transfer,
)


def _case(q=0.01, sample_nodes=257):
    m = AxisymmetricBianchiIBackground(q_ref=q)
    final_L = math.log(.1 / m.a_ref)
    seq = m.snapshots(np.linspace(0., final_L, sample_nodes))
    return m,seq,final_L


def _rays(count):
    mu=np.linspace(-0.99,.99,count,dtype=float)
    phi=np.linspace(0., 9.1,count)
    transverse=np.sqrt(1-mu*mu)
    return np.column_stack((transverse*np.cos(phi),transverse*np.sin(phi),mu))


@pytest.mark.parametrize("q", [0., .01, -.01])
def test_vectorized_geodesic_exact_killing_momentum_and_liouville(q):
    m,seq,end=_case(q)
    dirs=_rays(53)
    nu_face=np.linspace(1e14,2.4e15,53)
    f0=np.linspace(1e-12,.9,53)
    solver=AxisymmetricBianchiIBatchSolver(seq,m)
    out=solver.trace_many_to_face(
        tau_start=0.,tau_end=end,
        face_directions=dirs,face_frequency_Hz=nu_face,
        initial_occupation=f0,
        coefficients=BatchIsotropicCoefficients.zero(),
        n_step=64,chunk_size=19,
    )
    assert np.allclose(out.occupation_face,f0,rtol=0,atol=0)
    assert np.max(abs(np.linalg.norm(out.initial_direction_normal,axis=1)-1))<6e-15
    assert np.max(abs(np.linalg.norm(out.face_direction_normal,axis=1)-1))<6e-15
    delta_b=m.interval_log(0.,end).delta_b
    pface=.1*np.array([math.exp(-delta_b),math.exp(-delta_b),math.exp(2*delta_b)])[None,:] * nu_face[:,None]*dirs
    pstart=m.a_ref*nu_face[:,None]*0
    pstart=m.a_ref*out.initial_frequency_Hz[:,None]*out.initial_direction_normal
    residual=np.linalg.norm(pface-pstart,axis=1)/np.linalg.norm(pface,axis=1)
    assert np.max(residual)<3e-13
    assert out.n_step==64
    assert out.method_identity.startswith("rec_lrs_bi_exact_Ki_batch")


@pytest.mark.parametrize("q", [0.,+.01,-.01])
def test_stiff_positive_exact_constant_source_and_flrw(q):
    m,seq,end=_case(q)
    dirs=_rays(31)
    n=len(dirs)
    kappa=1e-15
    source_level=.32
    out=AxisymmetricBianchiIBatchSolver(seq,m).trace_many_to_face(
        tau_start=0,tau_end=end,face_directions=dirs,
        face_frequency_Hz=2.4e15,initial_occupation=np.linspace(0.001,.8,n),
        coefficients=BatchIsotropicCoefficients(lambda t,nu:kappa*source_level,
                                                lambda t,nu:kappa),
        n_step=32,
    )
    dt=m.interval_log(0,end).delta_t_s
    expected=np.array([constant_coefficient_transfer(f_initial=f,
       emissivity_s_inv=kappa*source_level,opacity_s_inv=kappa,
       travel_time_s=dt) for f in np.linspace(.001,.8,n)])
    assert np.max(abs(out.occupation_face-expected))<3e-13
    assert np.all(out.occupation_face>=0)
    assert np.all(out.initial_frequency_Hz>0)
    if q==0:
        assert np.max(abs(out.initial_direction_normal-dirs))<3e-14
        assert np.max(abs(out.initial_frequency_Hz/(2.4e15*math.exp(end))-1))<5e-15


def test_batch_scalar_original_transfer_agree_at_fixed_accuracy():
    m,seq,end=_case()
    dirs=_rays(9)
    coeff=BatchIsotropicCoefficients(
        lambda tau,nu:3e-20*(1+0.2*np.sin(2*tau)+0.02*(nu/2.4e15)),
        lambda tau,nu:4e-17*(1+0.1*np.cos(tau)+0.04*(nu/2.4e15)),
    )
    batch=AxisymmetricBianchiIBatchSolver(seq,m).trace_many_to_face(
        tau_start=0,tau_end=end,face_directions=dirs,
        face_frequency_Hz=2.4e15,initial_occupation=.0015,
        coefficients=coeff,n_step=128,chunk_size=4,
    )
    for i in (0,3,7):
        scalar=CharacteristicAngularSolver(seq,interval_source=m).trace_to_face(
            tau_start=0,tau_end=end,direction_hydrogen=dirs[i],
            face_frequency_Hz=2.4e15,initial_occupation=.0015,
            coefficients=IsotropicTransferCoefficients(
                lambda t,nu:float(coeff.emissivity_s_inv(t,nu)),
                lambda t,nu:float(coeff.opacity_s_inv(t,nu))),
            n_step=128)
        assert abs(batch.occupation_face[i]/scalar.occupation_face-1)<5e-7
        # Exact-Killing batch ray geometry improves the midpoint scalar path.
        assert abs(batch.initial_frequency_Hz[i]/scalar.initial_frequency_Hz-1)<3e-8


def test_parallel_chunks_agree_with_serial_and_partial_tail():
    m,seq,end=_case()
    dirs=_rays(61)
    coeff=BatchIsotropicCoefficients(
        lambda t,nu:3e-20*(1.+0.13*np.sin(t)+0.001*(nu/2.4e15)),
        lambda t,nu:4e-17*(1.+0.03*np.cos(3*t)+0.001*(nu/2.4e15)),
        thread_safe=True,
    )
    solver=AxisymmetricBianchiIBatchSolver(seq,m)
    kwargs=dict(tau_start=0.,tau_end=end,face_directions=dirs,
      face_frequency_Hz=np.linspace(1e14,3e15,len(dirs)),
      initial_occupation=np.linspace(.0001,.03,len(dirs)),
      coefficients=coeff,n_step=67,chunk_size=13)
    one=solver.trace_many_to_face(workers=1,**kwargs)
    four=solver.trace_many_to_face(workers=4,**kwargs)
    np.testing.assert_array_equal(one.occupation_face,four.occupation_face)
    np.testing.assert_array_equal(one.initial_frequency_Hz,four.initial_frequency_Hz)
    np.testing.assert_array_equal(one.initial_direction_normal,four.initial_direction_normal)


def test_parallel_requires_thread_safe_callbacks():
    m,seq,end=_case()
    with pytest.raises(ValueError,match="thread|pure"):
        AxisymmetricBianchiIBatchSolver(seq,m).trace_many_to_face(
            tau_start=0,tau_end=end,face_directions=_rays(4),
            face_frequency_Hz=2.4e15,initial_occupation=.001,
            coefficients=BatchIsotropicCoefficients.zero(),
            n_step=8,workers=2,
        )


@pytest.mark.parametrize("broken", ["direction","frequency","occupation","callback"])
def test_batch_rejects_bad_inputs_and_unphysical_coefficients(broken):
    m,seq,end=_case()
    rays=_rays(4)
    nu=np.full(4,2.4e15)
    f0=np.full(4,0.01)
    coef=BatchIsotropicCoefficients.zero()
    if broken=="direction":rays[0]=np.array([0.,0.,0.])
    if broken=="frequency":nu[0]=-1.
    if broken=="occupation":f0[1]=-0.1
    if broken=="callback":
        coef=BatchIsotropicCoefficients(
          lambda t,nu:np.full(len(nu),0.001),
          lambda t,nu:np.array([-1.0]+[0.]*(len(nu)-1)))
    with pytest.raises((ValueError,FloatingPointError)):
        AxisymmetricBianchiIBatchSolver(seq,m).trace_many_to_face(
           tau_start=0.,tau_end=end,face_directions=rays,
           face_frequency_Hz=nu,initial_occupation=f0,
           coefficients=coef,n_step=8)


def test_model_source_identity_cannot_be_cross_wired():
    m,seq,_=_case()
    with pytest.raises(ValueError,match="identity|source"):
        AxisymmetricBianchiIBatchSolver(seq,AxisymmetricBianchiIBackground(q_ref=-.01))


@pytest.mark.parametrize("chunk", [1, 3, 1024])
def test_serial_chunk_size_changes_only_memory_not_math(chunk):
    m,seq,end=_case(q=-.005)
    rays=_rays(17)
    solver=AxisymmetricBianchiIBatchSolver(seq,m)
    kwargs=dict(tau_start=0.,tau_end=end,face_directions=rays,
      face_frequency_Hz=np.linspace(1e14,2.8e15,len(rays)),
      initial_occupation=np.linspace(.001,.02,len(rays)),
      coefficients=BatchIsotropicCoefficients(
          lambda t,nu:3e-20*(1+.03*(nu/2.4e15)),
          lambda t,nu:4e-17*(1+.04*(nu/2.4e15))),n_step=81)
    a=solver.trace_many_to_face(chunk_size=chunk,workers=1,**kwargs)
    b=solver.trace_many_to_face(chunk_size=17,workers=1,**kwargs)
    np.testing.assert_array_equal(a.occupation_face,b.occupation_face)
    np.testing.assert_array_equal(a.initial_frequency_Hz,b.initial_frequency_Hz)


def test_nonzero_source_anchor_and_partial_range_momentum():
    m=AxisymmetricBianchiIBackground(q_ref=.01)
    stop=math.log(.1/m.a_ref)
    anchor=.417
    seq=m.snapshots(np.linspace(anchor,anchor+stop,257),eta_anchor=anchor)
    lo=anchor+.13
    hi=anchor+.61
    dirs=_rays(9)
    bat=AxisymmetricBianchiIBatchSolver(seq,m)
    out=bat.trace_many_to_face(tau_start=lo,tau_end=hi,
         face_directions=dirs,face_frequency_Hz=2.4e15,
         initial_occupation=.0013,coefficients=BatchIsotropicCoefficients.zero(),
         n_step=72,chunk_size=4)
    B=m.interval_log(lo-anchor,hi-anchor).delta_b
    # Conserved spatial momenta including the earlier nonzero shear background.
    bstart=m.interval_log(0.,lo-anchor).delta_b
    bend=bstart+B
    astart=m.a_ref*math.exp(lo-anchor)
    aend=m.a_ref*math.exp(hi-anchor)
    pstart=astart*np.array([math.exp(-bstart),math.exp(-bstart),math.exp(2*bstart)])[None,:] * out.initial_frequency_Hz[:,None]*out.initial_direction_normal
    pend=aend*np.array([math.exp(-bend),math.exp(-bend),math.exp(2*bend)])[None,:] * (2.4e15*dirs)
    assert np.max(np.linalg.norm(pstart-pend,axis=1)/np.linalg.norm(pend,axis=1))<5e-13


def test_dynamic_frequency_dependent_source_converges_to_independent_ivp():
    m,seq,end=_case(q=0.,sample_nodes=257)
    j=lambda t,nu:3e-20*(1+.2*np.sin(3*t)+.05*(nu/2.4e15))
    chi=lambda t,nu:4e-17*(1+.02*np.cos(t)+.03*(nu/2.4e15))
    model=m
    def ode(L,y):
        nu=2.4e15*math.exp(end-L)
        f=1./model.cosmology.hubble_flrw(model.a_ref*math.exp(L))
        return [f*(float(j(L,nu))-float(chi(L,nu))*y[0])]
    ref=solve_ivp(ode,(0.,end),[.0015],method='DOP853',rtol=3e-13,atol=2e-16)
    assert ref.success
    errors=[]
    solver=AxisymmetricBianchiIBatchSolver(seq,m)
    for nstep in (64,128,256):
        got=solver.trace_many_to_face(
          tau_start=0.,tau_end=end,face_directions=_rays(1),
          face_frequency_Hz=2.4e15,initial_occupation=.0015,
          coefficients=BatchIsotropicCoefficients(j,chi),n_step=nstep)
        errors.append(abs(got.occupation_face[0]-float(ref.y[0,-1])))
    assert errors[0]>errors[1]>errors[2]
    assert errors[0]/errors[1]>3.3
    assert errors[1]/errors[2]>3.2


def test_bounded_shared_log_geometry_cache_reuses_identical_event_grid():
    m,seq,end=_case()
    solver=AxisymmetricBianchiIBatchSolver(seq,m)
    a=solver._prepare_geometry(0.,end,64)
    b=solver._prepare_geometry(0.,end,64)
    assert a is b
    assert not a["dt"].flags.writeable
    assert not a["middle_b_face"].flags.writeable
    assert solver.cached_geometry_count <= 4
    # Different resolutions cannot inherit the same numerical method payload.
    c=solver._prepare_geometry(0.,end,128)
    assert c is not a
    assert solver.cached_geometry_count == 2


def test_cached_geometry_is_immutable_and_callbacks_remain_live():
    m,seq,end=_case()
    solver=AxisymmetricBianchiIBatchSolver(seq,m)
    geometry=solver._prepare_geometry(0.,end,64)
    with pytest.raises(TypeError):
        geometry["dt"]=np.zeros_like(geometry["dt"])
    with pytest.raises(ValueError):
        geometry["dt"][0]=0.
    calls=[]
    source={'emission':2e-20}
    c=BatchIsotropicCoefficients(
       lambda t,nu:(calls.append(t) or source['emission']),
       lambda t,nu:1e-17)
    kwargs=dict(tau_start=0.,tau_end=end,face_directions=_rays(7),
           face_frequency_Hz=2.4e15,initial_occupation=.001,
           coefficients=c,n_step=64)
    first=solver.trace_many_to_face(**kwargs)
    source['emission']=4e-20
    second=solver.trace_many_to_face(**kwargs)
    assert len(calls)==2*64
    assert np.all(second.occupation_face>first.occupation_face)
    assert solver._prepare_geometry(0.,end,64) is geometry


def test_cache_capacity_stays_small_without_ray_history_matrix():
    m,seq,end=_case()
    solver=AxisymmetricBianchiIBatchSolver(seq,m)
    for n in (8,16,32,64,128,256,512,1024):
        solver._prepare_geometry(0.,end,n)
        assert solver.cached_geometry_count<=4


@pytest.mark.parametrize("opacity", [0.,1e-19,1e-15,1e-8])
def test_batch_transparent_to_optically_thick_frozen_transfer(opacity):
    m,seq,end=_case()
    solver=AxisymmetricBianchiIBatchSolver(seq,m)
    ratio=.4
    emissivity=opacity*ratio if opacity>0 else 0.
    result=solver.trace_many_to_face(
       tau_start=0.,tau_end=end,face_directions=_rays(15),
       face_frequency_Hz=2.4e15,initial_occupation=.01,
       coefficients=BatchIsotropicCoefficients(
            lambda t,nu:emissivity,lambda t,nu:opacity),
       n_step=64)
    dt=m.interval_log(0,end).delta_t_s
    expected=.01 if opacity==0 else .01*math.exp(-opacity*dt)+ratio*(-math.expm1(-opacity*dt))
    assert np.all(result.occupation_face>=0.)
    assert np.max(abs(result.occupation_face-expected))<3e-13


@pytest.mark.parametrize("q,same_h", [(0.,False),(.01,False),(-.01,False),(.005,True)])
def test_batch_killing_energy_against_independent_70_digit_shear_quadrature(q,same_h):
    import mpmath as mp

    model=AxisymmetricBianchiIBackground(q_ref=q,same_h=same_h)
    end=math.log(.1/model.a_ref)
    seq=model.snapshots(np.linspace(0,end,129))
    dirs=_rays(7)
    nu=np.linspace(1.1e14,3e15,7)
    answer=AxisymmetricBianchiIBatchSolver(seq,model).trace_many_to_face(
        tau_start=0.,tau_end=end,face_directions=dirs,
        face_frequency_Hz=nu,initial_occupation=.001,
        coefficients=BatchIsotropicCoefficients.zero(),n_step=63)
    mp.mp.dps=70
    cc=model.cosmology
    h0=mp.mpf(float(cc.h0_per_s))
    om=mp.mpf(float(cc.omega_m));orr=mp.mpf(float(cc.omega_r))
    ol=mp.mpf(float(cc.omega_lambda));ar=mp.mpf(float(model.a_ref))
    sref=mp.mpf(float(model._s_ref))
    stop=mp.mpf(float(end))
    def shear_rate(x):
        a=ar*mp.exp(x)
        s=sref*mp.exp(-3*x)
        Hf=h0*mp.sqrt(om/a**3+orr/a**4+ol)
        H=Hf if same_h else mp.sqrt(Hf**2+s**2)
        return s/H
    exact_b=float(mp.quad(shear_rate,[0,stop]))
    b=-exact_b
    expperp=math.exp(b);expax=math.exp(-2*b)
    r=np.sqrt(expperp**2*np.sum(dirs[:,:2]**2,axis=1)+expax**2*dirs[:,2]**2)
    exact_freq=nu*math.exp(end)*r
    exact_mu=dirs[:,2]*expax/r
    assert np.max(abs(answer.initial_frequency_Hz/exact_freq-1))<1e-12
    assert np.max(abs(answer.initial_direction_normal[:,2]-exact_mu))<1e-12

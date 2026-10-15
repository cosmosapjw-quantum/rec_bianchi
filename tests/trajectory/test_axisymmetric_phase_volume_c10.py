"""C10 ray phase-space conservation: exact LRS Bianchi-I map and moments."""
from __future__ import annotations
import math
import numpy as np
import mpmath as mp
import pytest
from numpy.polynomial.legendre import leggauss

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground
from full_bianchi_hyrec.trajectory.axisymmetric_phase_space import (
    axisymmetric_phase_space_map,
)


def _grid(n=96):
    mus,weights=leggauss(n)
    directions=np.column_stack((
        np.sqrt(1-mus**2),np.zeros_like(mus),mus,
    ))
    return directions,weights


@pytest.mark.parametrize("q",[-.01,-.005,0.,.005,.01])
def test_exact_photon_number_jacobian_and_normalization(q):
    m=AxisymmetricBianchiIBackground(q_ref=q)
    l1=0.; l2=math.log(.1/m.a_ref)
    directions,weights=_grid()
    result=axisymmetric_phase_space_map(m,l1,l2,directions)
    assert result.method_identity=="rec_lrs_bi_killing_phase_volume_v1"
    assert result.energy_initial_over_face.shape==(len(directions),)
    assert np.max(abs(result.cubic_phase_space_normalized-1))<4e-14
    # This is the full-sky change-of-variables formula:
    # dOmega_initial/dOmega_face=R^-3, so the angular integral is 4pi.
    assert abs(np.dot(weights,result.solid_angle_initial_over_face)/2-1)<4e-14
    assert np.max(abs(np.linalg.norm(result.initial_directions,axis=1)-1))<4e-14
    if q==0:
        np.testing.assert_allclose(result.energy_initial_over_face,np.exp(l2-l1),rtol=2e-15)
        np.testing.assert_array_equal(result.solid_angle_initial_over_face,np.ones(len(directions)))


@pytest.mark.parametrize("q",[-.01,+.01])
def test_energy_density_anisotropy_matches_70_digit_moment(q):
    m=AxisymmetricBianchiIBackground(q_ref=q)
    l1=0.; l2=math.log(.1/m.a_ref)
    dirs,weights=_grid()
    sample=axisymmetric_phase_space_map(m,l1,l2,dirs)
    # Isotropic initial f(E_initial) -> energy density scales as
    # (a1/a2)^4 times full-sky average of R^-4.
    measured=float(np.dot(weights,np.power(sample.solid_angle_initial_over_face,4/3))/2)
    B=-m.interval_log(l1,l2).delta_b
    mp.mp.dps=75
    bb=mp.mpf(B)
    oracle=mp.quad(lambda x:(mp.exp(2*bb)*(1-x*x)+mp.exp(-4*bb)*x*x)**(-2),[-1,1])/2
    assert abs(measured-float(oracle))<2e-14
    asym=1+8/5*B*B+16/21*B**3+8/35*B**4
    assert abs(measured-asym)<1e-11
    assert abs(measured-1)>1e-6


def test_ultrashort_log_shear_retains_anisotropy_below_one_ulp_energy():
    m=AxisymmetricBianchiIBackground(q_ref=.01)
    tiny=1e-14
    # Physical shear is nonzero even if sqrt(1 + tiny) rounds to one.
    dirs=np.array([[1.,0.,0.],[0.,0.,1.]])
    result=axisymmetric_phase_space_map(m,0.,tiny,dirs)
    B=-m.interval_log(0.,tiny).delta_b
    assert B<0
    assert result.log_R[0] !=0
    assert result.log_R[1] !=0
    assert abs(result.log_R[0]/B-1)<1e-12
    assert abs(result.log_R[1]/B+2)<1e-12


def test_phase_space_map_matches_real_batch_solver_nonzero_anchor():
    from full_bianchi_hyrec.trajectory.axisymmetric_batched import (
      AxisymmetricBianchiIBatchSolver,BatchIsotropicCoefficients,
    )
    m=AxisymmetricBianchiIBackground(q_ref=.005)
    delta=math.log(.1/m.a_ref)
    start_anchor=.31
    seq=m.snapshots(np.linspace(start_anchor,start_anchor+delta,129),
                    eta_anchor=start_anchor)
    dirs,_=_grid(21)
    nu=np.linspace(1e13,3e15,len(dirs))
    result=AxisymmetricBianchiIBatchSolver(seq,m).trace_many_to_face(
      tau_start=start_anchor,tau_end=start_anchor+delta,
      face_directions=dirs,face_frequency_Hz=nu,
      initial_occupation=.005,coefficients=BatchIsotropicCoefficients.zero(),n_step=63)
    moment=axisymmetric_phase_space_map(m,0.,delta,dirs)
    assert np.max(abs(result.initial_frequency_Hz/(nu*moment.energy_initial_over_face)-1))<2e-13
    assert np.max(abs(result.initial_direction_normal-moment.initial_directions))<3e-13


@pytest.mark.parametrize("bad",[
    np.array([[0.,0.,0.]]),
    np.array([[math.nan,0.,1.]]),
    np.array([[1.,2.]]),
    np.array([]),
])
def test_phase_map_rejects_invalid_ray_data(bad):
    m=AxisymmetricBianchiIBackground(q_ref=.01)
    with pytest.raises(ValueError):
        axisymmetric_phase_space_map(m,0.,.1,bad)


def test_phase_map_rejects_reverse_or_out_of_domain_log_interval():
    m=AxisymmetricBianchiIBackground(q_ref=.01)
    directions,_=_grid(8)
    for l1,l2 in [(0.,0.),(.2,.1),(-.1,.2),(.2,5.),(float("nan"),.1)]:
        with pytest.raises(ValueError):
            axisymmetric_phase_space_map(m,l1,l2,directions)


@pytest.mark.parametrize("q",[0.,-.01,.01])
def test_prepared_phase_space_source_binding_and_repeat_identical(q):
    from full_bianchi_hyrec.trajectory.axisymmetric_phase_space import (
        prepare_axisymmetric_phase_space_map,
    )
    model=AxisymmetricBianchiIBackground(q_ref=q)
    end=math.log(.1/model.a_ref)
    rays,_=_grid(41)
    kernel=prepare_axisymmetric_phase_space_map(model,0.,end)
    assert kernel.model_source_sha256==model.source_sha256
    a=kernel.map(rays)
    b=kernel.map(rays)
    direct=axisymmetric_phase_space_map(model,0.,end,rays)
    np.testing.assert_array_equal(a.energy_initial_over_face,b.energy_initial_over_face)
    np.testing.assert_array_equal(a.energy_initial_over_face,direct.energy_initial_over_face)
    np.testing.assert_array_equal(a.solid_angle_initial_over_face,direct.solid_angle_initial_over_face)
    assert not a.log_R.flags.writeable
    with pytest.raises(ValueError):
        a.log_R[0]=0.

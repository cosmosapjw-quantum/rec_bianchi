"""C8 numerical stability: independent coordinate and source-transport controls.

Prescribed LRS Bianchi I only. These tests intentionally distinguish short
representable logarithmic intervals from intervals reconstructed via exp().
"""
from __future__ import annotations
import math
import numpy as np
import pytest

from full_bianchi_hyrec.background import AxisymmetricBianchiIBackground
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    CharacteristicAngularSolver,
    IsotropicTransferCoefficients,
    constant_coefficient_transfer,
)


def _tiny_solver(span=1.0e-14, q=0.01):
    model=AxisymmetricBianchiIBackground(q_ref=q)
    # Even where each small ray substep has identical rounded physical a,
    # the original provided tau steps remain strictly increasing.
    seq=model.snapshots(np.linspace(0,span,5))
    return model,seq,CharacteristicAngularSolver(seq,interval_source=model)


@pytest.mark.parametrize("span", [1e-14, 2e-15, 1e-15])
def test_ultrashort_physical_clock_is_not_lost_by_scale_round_trip(span):
    model,seq,solver=_tiny_solver(span)
    source=IsotropicTransferCoefficients(
        emissivity_s_inv=lambda tau,nu:6e-4,
        opacity_s_inv=lambda tau,nu:3e-3,
    )
    assert solver._clock_step(0.,span/64,seq.snapshot_at_tau(0.5*span/64))>0
    result=solver.trace_to_face(
        tau_start=0.,tau_end=span,
        direction_hydrogen=np.array([0.2,-0.3,0.93]),
        face_frequency_Hz=1.5e15,initial_occupation=0.15,
        coefficients=source,n_step=64,
    )
    F0,_=model._rate_slope(0.)
    target=constant_coefficient_transfer(
        f_initial=0.15,emissivity_s_inv=6e-4,
        opacity_s_inv=3e-3,travel_time_s=span*F0,
    )
    assert result.occupation_face>0
    assert abs(result.occupation_face-target)<1e-12


@pytest.mark.parametrize("q", [0.,0.005,-0.005,0.01,-0.01])
def test_direct_log_interval_agrees_with_previous_scale_factor_api(q):
    model=AxisymmetricBianchiIBackground(q_ref=q)
    for l1,l2 in ((0.,1e-7),(.02,.02001),(.05,.1),(.27,.31),
                  (0.,math.log(.1/model.a_ref))):
        from_log=model.interval_log(l1,l2)
        a1=model.a_ref*math.exp(l1)
        a2=model.a_ref*math.exp(l2)
        from_scale=model.interval(a1,a2)
        assert from_log.delta_t_s>0
        assert abs(from_log.delta_t_s/from_scale.delta_t_s-1)<5e-9
        if q==0:
            assert from_log.delta_b==0. and from_scale.delta_b==0.
        else:
            assert abs(from_log.delta_b/from_scale.delta_b-1)<5e-9


def test_log_interval_composition_across_cells():
    m=AxisymmetricBianchiIBackground(q_ref=0.01)
    l0,l1,l2=.025,.31,.42
    whole=m.interval_log(l0,l2)
    left=m.interval_log(l0,l1)
    right=m.interval_log(l1,l2)
    assert abs((left.delta_t_s+right.delta_t_s)/whole.delta_t_s-1)<5e-13
    assert abs((left.delta_b+right.delta_b)/whole.delta_b-1)<5e-13


def test_one_ulp_log_interval_is_strictly_positive():
    m=AxisymmetricBianchiIBackground(q_ref=-.01)
    left=.05
    right=math.nextafter(left,math.inf)
    tiny=m.interval_log(left,right)
    assert tiny.delta_l==right-left>0
    assert tiny.delta_t_s>0
    assert tiny.delta_b<0


@pytest.mark.parametrize("inputs",[(0.,0.),(.2,.1),(-1e-5,.1),(.2,4.),(float("nan"),.1)])
def test_log_interval_rejects_invalid_or_collapsed_bounds(inputs):
    m=AxisymmetricBianchiIBackground(q_ref=.01)
    with pytest.raises(ValueError):
        m.interval_log(*inputs)


def test_stiff_exact_equilibrium_positive_and_no_overflow():
    m=AxisymmetricBianchiIBackground(q_ref=0.01)
    inc=m.interval(m.a_ref,.1)
    seq=m.snapshots(np.linspace(0.,inc.delta_l,65))
    out=CharacteristicAngularSolver(seq,interval_source=m).trace_to_face(
        tau_start=0.,tau_end=inc.delta_l,
        direction_hydrogen=np.array([0.,0.,1.]),
        face_frequency_Hz=2.4e15,initial_occupation=.5,
        coefficients=IsotropicTransferCoefficients(
            emissivity_s_inv=lambda tau,nu:4e-11,
            opacity_s_inv=lambda tau,nu:1e-10,
        ),
        n_step=128,
    )
    assert out.occupation_face>0
    assert abs(out.occupation_face-.4)<1e-14


def test_new_source_clock_method_is_explicitly_versioned():
    m,seq,bound=_tiny_solver(1e-12)
    assert bound.source_clock_method_identity == "rec_lrs_bianchi_i_positive_rate_hermite_log_interval_v1"
    assert m.interval_log(0.,1e-12).method_identity == bound.source_clock_method_identity
    previous=CharacteristicAngularSolver(seq)
    assert previous.source_clock_method_identity == "rec_legacy_midpoint_H_per_step"
    assert previous.interval_source is None

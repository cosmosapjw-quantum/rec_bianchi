"""October 2012 original FULL hydrogen instantaneous atomic/radiation owner.

No unverified replacement of 311 algebraic virtual levels by ODE states.
All numerical source data are source-locked and source units checked.
"""
from __future__ import annotations
import math
from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    START_DIFF,STOP_DIFF,NVIRT,
    populate_original_full_atomic,complete_original_full_atomic,
    _original_escape_factors,
)
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    causal_incoming_from_accepted_histories,SOURCE_DLNA,
)

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
COSMO=dict(h=.6735837,omega_cb=.31242079216478097,
    omega_r_h2=4.1578740068818545e-5,
    omega_de_h2=.3119234221656212,omega_b_h2=.02242,
    y_he_mass=.245,tcmb0_K=2.7255)


@pytest.fixture(scope="module")
def model():
    return HMLAFlrwSource(
        **COSMO, table=OriginalHyRecPrimitiveRateTable.from_archive(SOURCE)
    )


def _problem(model,z=900.,x=.04,ratio=.98):
    incoming=np.linspace(2e-11,4e-11,NVIRT)
    return populate_original_full_atomic(
        model,z=z,xHII=x,xe=x,Tm_K=model.tcmb0_K*(1+z)*ratio,
        incoming_virtual=incoming,incoming_lyman=np.array([1e-11,2e-11]),
    )


def test_source_matrix_has_exact_algebraic_roles_and_sparse_diffusion(model):
    s=_problem(model)
    assert s.Trr.shape==(2,2)
    assert s.Tvr.shape==(2,311)
    assert s.Trv.shape==(2,311)
    assert s.Tvv.shape==(3,311)
    assert np.all(s.Tvv[0]>0)
    assert np.all(s.Dtau>=0)
    assert np.all(s.Tvr<=0) and np.all(s.Trv<=0)
    assert np.all(s.Tvv[1]<=0) and np.all(s.Tvv[2]<=0)
    # 311 virtual bins, but tridiagonal offdiagonals are only within 80
    # diffusion bins. Original source b=139/140 has zero inter-wing link.
    assert not np.any(s.Tvv[1,:START_DIFF+1])
    assert not np.any(s.Tvv[2,:START_DIFF])
    assert not np.any(s.Tvv[1,STOP_DIFF:])
    assert not np.any(s.Tvv[2,STOP_DIFF-1:])
    assert s.Tvv[1,LYA_BELOW:=139]<0
    assert s.Tvv[2,LYA_ABOVE:=140]<0
    assert s.Tvv[2,139]==0 and s.Tvv[1,140]==0
    assert not s.Tvv.flags.writeable


def test_algebraic_residual_and_atom_to_radiation_one_step(model):
    for z,x,ratio in [(650.,.002,.95),(900.,.04,.98),(1200.,.45,.999),
                      (1450.,.97,.99999)]:
        s=_problem(model,z,x,ratio)
        result=complete_original_full_atomic(s)
        assert result.normalized_matrix_residual < 1e-11
        assert np.all(np.isfinite(result.outgoing_virtual))
        assert np.all(np.isfinite(result.outgoing_lyman))
        assert np.all(np.isfinite(result.average_virtual))
        assert math.isfinite(result.dxHII_dln_a)
        assert not result.outgoing_virtual.flags.writeable
        assert not result.virtual_departures.flags.writeable


def test_source_logical_domains_and_immutable_input(model):
    s=_problem(model)
    raw=np.linspace(2e-11,4e-11,NVIRT)
    # Input pollution after the fact must not change the source snapshot.
    snap=populate_original_full_atomic(
        model,z=900.,xHII=.04,xe=.04,Tm_K=model.tcmb0_K*901*.98,
        incoming_virtual=raw,incoming_lyman=[1e-11,2e-11])
    original=snap.incoming_virtual.copy()
    raw[:]=999
    np.testing.assert_array_equal(snap.incoming_virtual,original)
    with pytest.raises(ValueError,match="xHII"):
        populate_original_full_atomic(
            model,z=900.,xHII=-.1,xe=.04,Tm_K=2500,
            incoming_virtual=np.zeros(311),incoming_lyman=np.zeros(2))
    with pytest.raises(ValueError,match="table"):
        populate_original_full_atomic(
            model,z=2200,xHII=.5,xe=.5,Tm_K=5000,
            incoming_virtual=np.zeros(311),incoming_lyman=np.zeros(2))


def test_native_source_small_tau_formula_has_no_spurious_floor():
    t=np.array([0.,1e-30,1e-12,1e-6,1.00001e-6,.002,10.,500.])
    p,s=_original_escape_factors(t)
    assert p[0]==s[0]==0.
    assert np.all(p[1:]>=0) and np.all(s[1:]>=0)
    np.testing.assert_allclose(p[:4],.5*t[:4]-t[:4]**2/6,
                               rtol=0,atol=0)
    assert s[-1]==1 and p[-1]==1-1/t[-1]
    with pytest.raises(ValueError):
        _original_escape_factors(np.array([-.1]))


def test_accepted_history_read_is_separate_from_algebraic_source(model):
    # One physical z=900 point with actual earlier accepted 311+3 history.
    # The expected input is not an external xe(z) reference curve.
    from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import (
        OriginalHyRecTwoPhotonRamanTable
    )
    table=OriginalHyRecTwoPhotonRamanTable.from_archive(SOURCE)
    z=900.;iz=80
    zstart=math.expm1(math.log1p(z)+iz*SOURCE_DLNA)
    hist=np.zeros((311,iz))
    ly=np.zeros((3,iz))
    incoming=causal_incoming_from_accepted_histories(
        energies_eV=table.energy_eV,virtual_history=hist,
        lyman_history=ly,z_start=zstart,iz=iz,z_face=z)
    s=populate_original_full_atomic(
        model,z=z,xHII=.04,xe=.04,
        Tm_K=model.tcmb0_K*(1+z)*.98,
        incoming_virtual=incoming.virtual_distortion[0],
        incoming_lyman=incoming.lya_lyb_incoming_distortion[0])
    result=complete_original_full_atomic(s)
    assert np.max(abs(incoming.virtual_distortion))==0
    assert np.max(abs(incoming.lya_lyb_incoming_distortion))==0
    assert np.all(np.isfinite(result.outgoing_virtual))
    assert np.all(np.isfinite(result.outgoing_lyman))
    assert result.source_mode.endswith("NOT_TRAJECTORY")


@pytest.mark.slow
def test_true_unmodified_original_2012_C_full_source_and_outgoing_parity():
    from verify_full_atomic_native import run
    result=run()
    assert result["source_state_count"]==4
    assert result["max_scaled_relative_across_fields"]<1e-8
    assert result["status"]=="PASS_SOURCE_POINT_PARITY"


def test_continuum_escape_stability_is_distinct_from_native_bit_parity():
    import mpmath as mp
    from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
        accurate_escape_factors,
    )
    tau=np.array([0.,1e-12,1.00001e-6,1.2532105263115493e-6,
                  .0001,.01,.025,.03,.1,1.,20.,500.])
    native,_=_original_escape_factors(tau)
    improved,survive=accurate_escape_factors(tau)
    mp.mp.dps=75
    reference=np.array([
        0 if z==0 else float(
            1+(mp.expm1(-mp.mpf(float(z)))/mp.mpf(float(z))))
        for z in tau
    ])
    assert np.max(np.abs(improved-reference)/np.maximum(
        reference,1e-300))<5e-13
    assert abs(native[3]-reference[3]) / reference[3]>1e-6
    assert np.all(improved>=0)
    assert np.all(survive>=0)
    with pytest.raises(ValueError):
        accurate_escape_factors([-1.,0.])

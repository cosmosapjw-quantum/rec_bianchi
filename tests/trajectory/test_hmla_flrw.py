"""Scoped q=0 source-faithful HyRec2012 EMLA2s2p local hydrogen dynamics.

Physics accepted by these tests:
- original source α2s/2p, β2s/2p, R2p2s
- stable generalized C2s/C2p, Lyα Sobolev and Λ2s1s
- neutral-helium hydrogen-only q=0 + Compton/adiabatic Tm
No full Lyα frequency diffusion, HeII/III evolution, atomic macro owner
closure or production REI acceptance is implied.
"""
from __future__ import annotations
from dataclasses import replace
import math
from pathlib import Path
import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.hmla_flrw import (
    HMLAFlrwSource,integrate_hmla_hydrogen,
    IONIZATION_ENERGY_EV,KB_NATIVE_EV_K,
)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable

ROOT=Path(__file__).resolve().parents[2]
ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
COSMO={
 "h":.6735837,"omega_cb":.31242079216478097,
 "omega_r_h2":4.1578740068818545e-05,
 "omega_de_h2":.3119234221656212,
 "omega_b_h2":.022420000000000002,
 "y_he_mass":.245,"tcmb0_K":2.7255
}
@pytest.fixture(scope="module")
def src():
    return HMLAFlrwSource(
        **COSMO,
        table=OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE),
    )


def test_primordial_source_has_Saha_initial_and_independent_postSaha_correction(src):
    z=1600
    saha=src.saha_initial_hii(z)
    post=src.hydrogen_post_saha_initial(z)
    assert abs(saha-.9943708480958812)<4e-12
    assert abs(post-.9944061343157344)<4e-10
    assert post>saha
    Tr=KB_NATIVE_EV_K*src.tcmb0_K*(1+z)
    H,nH=src.cosmology(z)
    S=(3.016103031869581e21*Tr**1.5*math.exp(-IONIZATION_ENERGY_EV/Tr))/(nH*1e-6)
    assert abs(saha*saha/(1-saha)/S-1)<2e-12
    # Post-Saha is a SOURCE-Jacobian calculation, not a fit to C output.


def test_original_HMLA_source_equilibrium_and_helium_electron_support(src):
    for z in (650,900,1200,1600):
        x=src.saha_initial_hii(z)
        T=src.tcmb0_K*(1+z)
        s=src.hydrogen_rhs_ln_a(z=z,x_HII=x,x_e=x,Tm_K=T)
        assert abs(s)<2e-4
        helium=src.hydrogen_rhs_ln_a(
            z=z,x_HII=x,x_e=x+src.f_he*.1,Tm_K=T)
        assert math.isfinite(helium) and helium!=s
    with pytest.raises(ValueError,match="hydrogen"):
        src.hydrogen_rhs_ln_a(z=1100,x_HII=1,x_e=1,Tm_K=3000)


def test_cooling_compton_temperature_preserves_dimension_and_stationary_balance(src):
    for z in (1600,1200,800,600):
        x=src.saha_initial_hii(z)
        Tr=src.tcmb0_K*(1+z)
        Tm=src.initial_Tm_steady_K(z,x)
        assert 0<Tm<Tr
        v=src.thermal_rhs_ln_a(z,x,Tm)
        assert abs((v+Tm)/Tm)<2e-10


def test_actual_local_hydrogen_plus_thermal_trajectory_is_physical(src):
    r=integrate_hmla_hydrogen(src,points=69,rtol=2e-7,atol=2e-9)
    assert len(r.z)==69
    assert np.all(np.diff(r.z)<0)
    assert np.all(np.diff(r.x_HII)<0)
    assert np.all(r.x_HII>=0) and np.all(r.x_HII<=1)
    assert np.all(r.Tm_K>0)
    assert np.all(r.Tm_K<=src.tcmb0_K*(1+r.z)*(1+1e-10))
    assert 0.00085<r.x_HII[-1]<0.00105
    assert 1600==pytest.approx(r.z[0],abs=1e-8)
    assert r.source_mode=="REC_HMLA2s2p_H_ONLY_PLUS_TM_NOT_FULL"
    assert not r.z.flags.writeable and not r.x_HII.flags.writeable


def test_numerical_tolerance_refinement_does_not_explain_one_percent_full_model_difference(src):
    coarse=integrate_hmla_hydrogen(src,points=68,rtol=1e-6,atol=1e-8)
    tight=integrate_hmla_hydrogen(src,points=68,rtol=2e-9,atol=2e-11)
    residual=np.max(np.abs(coarse.x_HII/tight.x_HII-1))
    assert residual<1e-4
    assert abs(coarse.Tm_K[-1]/tight.Tm_K[-1]-1)<2e-6


def test_source_scope_rejects_missing_physical_domains(src):
    bads=[
       dict(z=1100,x_HII=-.01,x_e=.4,Tm_K=3000),
       dict(z=1100,x_HII=.4,x_e=.3,Tm_K=3000),
       dict(z=1100,x_HII=.4,x_e=.4,Tm_K=-1),
       dict(z=2000,x_HII=.9,x_e=.9,Tm_K=4000),
    ]
    for b in bads:
        with pytest.raises(ValueError):
            src.hydrogen_rhs_ln_a(**b)
    with pytest.raises(ValueError,match="scientific integration"):
        integrate_hmla_hydrogen(src,z_initial=600,z_final=1600)
    with pytest.raises(ValueError,match="linear regime"):
        src.hydrogen_post_saha_initial(650)


@pytest.mark.slow
def test_actual_original_2012_C_HMLA_rhs_matches_this_python_96_state_grid():
    from verify_hmla_native_rhs import run
    r=run()
    assert r["samples"]==96
    assert r["max_scaled_relative_difference"]<3e-10
    assert "NOT FULL" in r["scope"]


@pytest.mark.parametrize("z,ratio",[ (700.,.9),(900.,.998),(1100.,.9999),(1400.,.99999)])
def test_vectorized_hmla_shared_temperature_source_matches_scalar(src,z,ratio):
    x=np.linspace(.01,.998,53)
    xe=x+.2*src.f_he
    Tm=src.tcmb0_K*(1+z)*ratio
    batch=src.hydrogen_rhs_ln_a_many(z=z,x_HII=x,x_e=xe,Tm_K=Tm)
    scalar=np.array([src.hydrogen_rhs_ln_a(z=z,x_HII=float(a),x_e=float(b),Tm_K=Tm)
              for a,b in zip(x,xe)])
    assert batch.shape==x.shape
    assert not batch.flags.writeable
    # Same original physical rate and time, only vectorized Schur update.
    assert np.max(np.abs(batch-scalar)/np.maximum(np.abs(scalar),1e-15))<2e-12


def test_vectorized_hmla_rejects_false_helium_and_shape(src):
    for x,xe in (
        ([.5,.9],[.2,.9]),([.5,.9],[.5]),
        ([-.3,.9],[-.3,.9]),([.5,1.],[.5,1.]),
    ):
        with pytest.raises(ValueError):
            src.hydrogen_rhs_ln_a_many(
                z=1100.,x_HII=np.array(x),x_e=np.array(xe),
                Tm_K=3000,
            )

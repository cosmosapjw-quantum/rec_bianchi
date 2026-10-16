from __future__ import annotations

from types import SimpleNamespace
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.primordial_2012_full_start import (
    MAX_FULL_EVALUATIONS,N_ACCEPTED,FullStartHistory,
    source_native_derivative_seeds,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import (
    DLNA,HyRec2012Cosmology,
)

_VERIFIER_PATH=Path(__file__).resolve().parents[2]/"scripts/verify_r3g_full_start.py"
_SPEC=importlib.util.spec_from_file_location("r3g_full_start_verifier",_VERIFIER_PATH)
_VERIFIER=importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_VERIFIER)


def test_u1_output_row_rhs_maps_to_native_input_derivative_seed():
    # At row i the U1 RHS was evaluated at input i-1; exercise the exact
    # boundary-index map used by history.c's two-derivative predictor.
    start=5
    h=DLNA
    xe=np.array([.8,.7,.6,.5,.4,.3])
    rhs=np.array([0.,1.,2.,3.,4.,5.])
    fake=SimpleNamespace(iz=tuple(range(start+1)),xe=xe,
                         helium_rhs_dln_a=rhs)
    got=source_native_derivative_seeds(fake,start)
    assert got[0]==rhs[start]       # f_He(i0-1)
    assert got[1]==rhs[start-1]     # f_He(i0-2)
    assert got[2]==pytest.approx((xe[start]-xe[start-2])/(2*h)-rhs[start])
    assert got[3]==pytest.approx((xe[start-1]-xe[start-3])/(2*h)-rhs[start-1])


def test_full_start_receipt_shapes_encode_eight_columns_nine_states():
    n=N_ACCEPTED+1
    history=FullStartHistory(
        iz=np.arange(18223,18223+n),z=np.linspace(1702,1701,n),
        xH1s=np.full(n,1.e-4),xHII=np.full(n,.9999),
        xHeII=np.full(n,2.e-4),xe=np.full(n,1.0001),
        Tm_K=np.full(n,4600.),helium_rhs_dln_a=np.zeros(N_ACCEPTED),
        hydrogen_rhs_dln_a=np.zeros(N_ACCEPTED),post_saha=np.ones(n,dtype=bool),
        virtual_out=np.zeros((311,N_ACCEPTED)),
        average_virtual=np.zeros((311,N_ACCEPTED)),
        lyman_out=np.zeros((3,N_ACCEPTED)),matrix_residual=np.zeros(N_ACCEPTED),
        full_evaluations=32,
    )
    assert history.iz.shape==(9,)
    assert history.virtual_out.shape==(311,8)
    assert history.average_virtual.shape==(311,8)
    assert history.lyman_out.shape==(3,8)
    assert not history.xe.flags.writeable
    with pytest.raises(ValueError,match="eight accepted input RHS"):
        FullStartHistory(
            iz=np.arange(n),z=np.linspace(1702,1701,n),
            xH1s=np.full(n,1.e-4),xHII=np.full(n,.9999),
            xHeII=np.full(n,2.e-4),xe=np.full(n,1.0001),
            Tm_K=np.full(n,4600.),helium_rhs_dln_a=np.zeros(n),
            hydrogen_rhs_dln_a=np.zeros(N_ACCEPTED),post_saha=np.ones(n,dtype=bool),
            virtual_out=np.zeros((311,N_ACCEPTED)),
            average_virtual=np.zeros((311,N_ACCEPTED)),
            lyman_out=np.zeros((3,N_ACCEPTED)),matrix_residual=np.zeros(N_ACCEPTED),
            full_evaluations=32,
        )


def test_full_evaluation_cap_is_enforced_in_receipt_shape():
    n=N_ACCEPTED+1
    with pytest.raises(ValueError,match="FULL atomic evaluation cap"):
        FullStartHistory(
            iz=np.arange(n),z=np.linspace(1702,1701,n),
            xH1s=np.full(n,1.e-4),xHII=np.full(n,.9999),
            xHeII=np.full(n,2.e-4),xe=np.full(n,1.0001),
            Tm_K=np.full(n,4600.),helium_rhs_dln_a=np.zeros(N_ACCEPTED),
            hydrogen_rhs_dln_a=np.zeros(N_ACCEPTED),post_saha=np.ones(n,dtype=bool),
            virtual_out=np.zeros((311,N_ACCEPTED)),
            average_virtual=np.zeros((311,N_ACCEPTED)),
            lyman_out=np.zeros((3,N_ACCEPTED)),matrix_residual=np.zeros(N_ACCEPTED),
            full_evaluations=MAX_FULL_EVALUATIONS+1,
        )


def test_integrated_photon_verifier_rejects_swapped_virtual_average_channels():
    # A regression in the native V/A labels must fail even when both arrays
    # have valid lengths and finite values.
    py_v=np.zeros(311); py_a=np.ones(311); py_l=np.zeros(3)
    fbb_v=np.full(311,1.e-12); fbb_l=np.full(3,1.e-12)
    with pytest.raises(ArithmeticError,match="species=virtual"):
        _VERIFIER.compare_photon_spectra(
            py_v,py_a,py_l,py_a,py_v,py_l,fbb_v,fbb_l,step=0)

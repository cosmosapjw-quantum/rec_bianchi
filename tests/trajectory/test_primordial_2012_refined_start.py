"""Frozen h2 clock and causal boundary regressions, without physical runs."""
from types import SimpleNamespace
import io
import math
from pathlib import Path
import zipfile

import numpy as np
import pytest
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    DLNA,HyRec2012Cosmology,integrate_full_start_eight,saha_heii,
    source_native_derivative_seeds,checked_common_input_rhs_ratio,
    checked_common_input_spectrum_ratio,
)
from scripts.verify_r3i_h2_start import (
    compare_state,compare_photon_spectra,checked_integrated_rhs_ratio,parse_native,
)
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    _source_edges,causal_incoming_from_accepted_histories,
)


def energies():
    archive=Path(__file__).resolve().parents[2]/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
    with zipfile.ZipFile(archive) as z:
        return np.loadtxt(io.BytesIO(z.read('HyRec/two_photon_tables.dat')))[:,0]


def incoming(j,zface=None,v=None):
    c=HyRec2012Cosmology(); z0=c.redshift(c.izH0)
    return causal_incoming_from_accepted_histories(
        energies_eV=energies(),virtual_history=np.ones((311,j)) if v is None else v,
        lyman_history=np.ones((3,j)),z_start=z0,iz=j,dlna=DLNA,
        z_face=c.redshift(c.izH0+j) if zface is None else zface)


def test_h2_source_floor_index_and_seed_clock():
    c=HyRec2012Cosmology()
    assert DLNA==8.49e-5/2
    assert c.izH0==36446
    assert c.redshift(0)==8000
    xe=np.array([.8,.7,.6,.5,.4,.3]); rhs=np.arange(6.)
    fake=SimpleNamespace(iz=range(6),xe=xe,helium_rhs_dln_a=rhs)
    he,he2,h,h2=source_native_derivative_seeds(fake,5)
    assert (he,he2)==(5,4)
    assert h==(xe[5]-xe[3])/(2*DLNA)-he
    assert h2==(xe[4]-xe[2])/(2*DLNA)-he2


def test_heii_saha_source_multiply_order_at_first_rhs_failure():
    # Fixed same-input original-C scalar results at run_002's post-Saha endpoint.
    # The central one-ulp xHeII discrepancy amplified the near-equilibrium RHS.
    c=HyRec2012Cosmology(); z=4153.806612354785
    a=1+z
    assert (c.nH0_m3*a*a*a).hex()=="0x1.95845b22d144ap+33"
    z_values=(math.nextafter(z,-math.inf),z,math.nextafter(z,math.inf))
    native_hex=("0x1.4f65c1fdbd1f9p-4","0x1.4f65c1fdbd1f9p-4",
                "0x1.4f65c1fdbd1fap-4")
    assert tuple(saha_heii(c,q).hex() for q in z_values)==native_hex


def test_coarse_checkpoint_is_refused_before_atomic_work():
    fake=SimpleNamespace(iz=[18223],z=[HyRec2012Cosmology().redshift(36446)])
    with pytest.raises(ValueError,match='frozen izH0'):
        integrate_full_start_eight(fake,HyRec2012Cosmology(),None)


def test_j2_h2_no_active_links_and_all_313_original_edges():
    src,_,_= _source_edges(energies())
    assert src.shape==(313,)
    assert (src[139],src[270],src[310],src[311],src[312])==(311,312,313,140,271)
    result=incoming(2)
    assert not np.any(result.virtual_distortion)
    assert not np.any(result.lya_lyb_incoming_distortion)


def test_first_active_edge_respects_committed_two_neighbor_interval():
    src,target,emit=_source_edges(energies())
    first=math.ceil(float(np.min(np.log(emit/target)))/DLNA)
    before=incoming(first-1); result=incoming(first)
    assert not np.any(before.virtual_distortion)
    assert not np.any(before.lya_lyb_incoming_distortion)
    z0=HyRec2012Cosmology().redshift(36446); eta0=-math.log1p(z0)
    active=result.retarded_eta>=eta0
    assert np.any(active)
    index=(result.retarded_eta[active]-eta0)/DLNA
    k=np.floor(index).astype(int); theta=index-k
    assert np.all(k>=0) and np.all(k+1<=first-1)
    assert np.all((theta>=0)&(theta<=1))
    assert np.all(result.retarded_eta[active]<eta0+DLNA*(first-1))


def test_forged_future_read_and_nan_past_are_rejected():
    c=HyRec2012Cosmology()
    with pytest.raises(ValueError,match='current/unaccepted future'):
        incoming(2,zface=c.redshift(c.izH0+10))
    v=np.ones((311,3)); v[1,1]=np.nan
    with pytest.raises(ValueError,match='history shapes invalid'):
        incoming(3,v=v)


@pytest.mark.parametrize('bad',(math.nan,math.inf,-math.inf))
def test_state_and_common_rhs_reject_nonfinite_operands(bad):
    state={'xHII':.5,'xe':.6,'xHeII':.1,'Tm_K':3000.,'z':2000.,
           'xH1s':.5,'iz':3,'post_saha':False}
    for name in ('xHII','xe','xHeII','Tm_K','z','xH1s'):
        altered={**state,name:bad}
        with pytest.raises(ArithmeticError,match='INDEPENDENT_HISTORY_NONFINITE'):
            compare_state(altered,state,3)
        with pytest.raises(ArithmeticError,match='INDEPENDENT_HISTORY_NONFINITE'):
            compare_state(state,altered,3)
    with pytest.raises(ArithmeticError,match='COMMON_INPUT_FULL_RHS_NONFINITE'):
        checked_common_input_rhs_ratio(bad,1.,0)
    with pytest.raises(ArithmeticError,match='COMMON_INPUT_FULL_RHS_NONFINITE'):
        checked_common_input_rhs_ratio(1.,bad,0)


@pytest.mark.parametrize('bad',(math.nan,math.inf,-math.inf))
def test_photon_comparators_reject_nonfinite_operands(bad):
    py=np.ones(311); cs=np.ones(311); fb=np.ones(311)
    for position in range(3):
        arrays=[py.copy(),cs.copy(),fb.copy()]
        arrays[position][0]=bad
        with pytest.raises(ArithmeticError,match='COMMON_INPUT_PHOTON_NONFINITE'):
            checked_common_input_spectrum_ratio(*arrays,0)
        with pytest.raises(ArithmeticError,match='INTEGRATED_PHOTON_NONFINITE'):
            compare_photon_spectra(arrays[0],py,np.ones(3),arrays[1],cs,
                                   np.ones(3),arrays[2],fb[:3],0)


def test_photon_comparators_reject_zero_tolerance():
    zero=np.zeros(311)
    with pytest.raises(ArithmeticError,match='COMMON_INPUT_PHOTON_INVALID_TOLERANCE'):
        checked_common_input_spectrum_ratio(zero,zero,zero,0)
    with pytest.raises(ArithmeticError,match='INTEGRATED_PHOTON_INVALID_TOLERANCE'):
        compare_photon_spectra(zero,zero,np.ones(3),zero,zero,np.ones(3),
                               zero,np.ones(3),0)


def test_finite_operands_cannot_hide_overflowed_ratios():
    with pytest.raises(ArithmeticError,match='COMMON_INPUT_FULL_RHS_NONFINITE_RATIO'):
        checked_common_input_rhs_ratio(-1.e308,1.e308,0)
    py=np.full(311,-1.e308); cs=np.full(311,1.e308); fb=np.ones(311)
    with np.errstate(over='ignore'):
        with pytest.raises(ArithmeticError,match='COMMON_INPUT_PHOTON_NONFINITE_RATIO'):
            checked_common_input_spectrum_ratio(py,cs,fb,0)
        with pytest.raises(ArithmeticError,match='INTEGRATED_PHOTON_NONFINITE_RATIO'):
            compare_photon_spectra(py,cs,np.ones(3),cs,cs,np.ones(3),fb,fb[:3],0)


@pytest.mark.parametrize('bad',(math.nan,math.inf,-math.inf))
@pytest.mark.parametrize('species',('H','He'))
def test_integrated_rhs_rejects_nonfinite_python_and_c(bad,species,tmp_path):
    for py,cs in ((bad,1.),(1.,bad)):
        with pytest.raises(ArithmeticError,match='INDEPENDENT_RHS_NONFINITE'):
            checked_integrated_rhs_ratio(py,cs,2.e-7,3,species)
    fields=['STEP','3','36450','2500','.5','.5','.05','.55','3000','1.','1.','0']
    fields[9 if species=='H' else 10]=str(bad)
    path=tmp_path/'oracle.csv'; path.write_text(','.join(fields)+'\n')
    with pytest.raises(RuntimeError,match='C_ORACLE_STEP_NONFINITE_RHS'):
        parse_native(path)


def test_integrated_rhs_rejects_invalid_limit_and_overflow():
    for bad_limit in (math.nan,math.inf,-math.inf,0.,-1.):
        with pytest.raises(ArithmeticError,match='INDEPENDENT_RHS_NONFINITE'):
            checked_integrated_rhs_ratio(1.,1.,bad_limit,3,'H')
    with np.errstate(over='ignore'):
        with pytest.raises(ArithmeticError,match='INDEPENDENT_RHS_NONFINITE_RATIO'):
            checked_integrated_rhs_ratio(-1.e308,1.e308,2.e-7,3,'H')

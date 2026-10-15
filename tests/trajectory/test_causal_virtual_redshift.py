"""Causal history interpolation + exact prescribed LRS Killing redshift.

The native-C oracle is compiled from the raw Oct2012 archive, not a
translated Python implementation, and is never used as REC output.
"""
from __future__ import annotations
import ctypes
from functools import lru_cache
import io
import math
from pathlib import Path
import subprocess
import tempfile
import zipfile

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    SOURCE_DLNA, SOURCE_LINES_EV, SOURCE_N_VIRTUAL,
    _retarded_lookback, _source_edges, safe_constant_shear_dlna,
    causal_incoming_from_accepted_histories,
)

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
C_WRAPPER = ROOT/"scripts/c_harness/original_hyrec_causal_fplus_harness.c"


@lru_cache(maxsize=1)
def virtual_energies():
    # The exact unmodified physical frequency grid from the October-2012
    # source archive: no constructed or fitted bin edges.
    with zipfile.ZipFile(ARCHIVE) as zf:
        table=np.loadtxt(io.BytesIO(zf.read("HyRec/two_photon_tables.dat")))
    assert table.shape == (SOURCE_N_VIRTUAL, 5)
    result = np.array(table[:,0], copy=True)
    result.setflags(write=False)
    return result


def native_history(iz, mus=(0.0,)):
    t = np.arange(iz, dtype=float)
    e = np.arange(311, dtype=float)
    m = np.array(mus, dtype=float)
    virtual = 1e-7*(1+e[None,:,None]/250) * (
        1+.23*m[:,None,None]+t[None,None,:]/1200
    )
    lines = 1e-8*(1+np.arange(3)[None,:,None]/5) * (
        1+.37*m[:,None,None]-t[None,None,:]/2200
    )
    return np.ascontiguousarray(virtual),np.ascontiguousarray(lines)


def face_z(z_start, iz, dlna=SOURCE_DLNA):
    return math.expm1(math.log1p(z_start)-iz*dlna)


def test_source_photon_history_index_and_shapes():
    src, eface, esrc = _source_edges(virtual_energies())
    assert src.shape == (313,)
    assert src[139] == 311 and src[270] == 312 and src[310] == 313
    assert src[311] == 140 and src[312] == 271
    assert np.all(esrc > eface)
    e = virtual_energies()
    with pytest.raises(ValueError, match="ordering"):
        _source_edges(np.linspace(10.25, 12.5,311))


def _compile_source_native(tmp):
    with zipfile.ZipFile(ARCHIVE) as zf:
        for name in ("hydrogen.c","hydrogen.h","hyrectools.c",
                     "hyrectools.h","hyrec_params.h"):
            zf.extract("HyRec/"+name, tmp)
    src = tmp/"HyRec"
    so = tmp/"librec_native_fplus.so"
    cmd = ["gcc","-std=gnu99","-O2","-shared","-fPIC",
           "-ffunction-sections","-fdata-sections","-fvisibility=hidden",
           "-Wl,--gc-sections","-I",str(src),
           str(src/"hydrogen.c"),str(src/"hyrectools.c"),
           str(C_WRAPPER),"-lm","-o",str(so)]
    subprocess.run(cmd,check=True,capture_output=True,text=True)
    lib = ctypes.CDLL(str(so))
    p = ctypes.POINTER(ctypes.c_double)
    fn = lib.rec_r3_native_fplus
    fn.argtypes = [p,p,p,ctypes.c_uint,ctypes.c_double,
                   ctypes.c_double,p,p]
    fn.restype = None
    return fn


@pytest.mark.slow
def test_native_original_C_Full_fplus_311bin_and_2Lyman_parity():
    with tempfile.TemporaryDirectory(prefix="rec_native_fplus_") as d:
        fn = _compile_source_native(Path(d))
        energies = np.ascontiguousarray(virtual_energies())
        for iz in (2, 40, 200):
            virtual, lyman = native_history(iz)
            v = np.ascontiguousarray(virtual[0])
            ly = np.ascontiguousarray(lyman[0])
            zstart=1600.0
            zface=face_z(zstart,iz)
            py = causal_incoming_from_accepted_histories(
                energies_eV=energies,virtual_history=v,
                lyman_history=ly,z_start=zstart,
                z_face=zface,iz=iz,
            )
            vc = np.empty(311,dtype=float)
            lc = np.empty(2,dtype=float)
            def ptr(a):
                return a.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
            fn(ptr(energies),ptr(v),ptr(ly),iz,zstart,zface,
               ptr(vc),ptr(lc))
            np.testing.assert_allclose(py.virtual_distortion[0],vc,
                                       atol=2e-18,rtol=2e-11)
            np.testing.assert_allclose(py.lya_lyb_incoming_distortion[0],lc,
                                       atol=2e-18,rtol=2e-11)


@pytest.mark.parametrize("q",[-0.05,-0.015,0,0.007,0.04])
def test_exact_Killing_energy_lookback_and_mu_sign(q):
    rng = np.random.default_rng(124)
    d_true = rng.uniform(1e-4,.3,800)
    mf = rng.uniform(-1,1,800)
    B=-q*d_true
    logR = B+.5*np.log1p(mf*mf*np.expm1(-6*B))
    ratio = d_true+logR
    recovered, mi, rec_R = _retarded_lookback(ratio,mf,q)
    np.testing.assert_allclose(recovered,d_true,rtol=2e-11,atol=2e-13)
    np.testing.assert_allclose(rec_R,logR,atol=2e-13)
    assert np.max(np.abs(mi))<=1+1e-14
    if q==0:
        np.testing.assert_array_equal(mi,mf)


def test_angular_and_time_affine_interpolation_and_geometric_blackbody():
    e = virtual_energies()
    n=640
    mus=np.linspace(-1,1,17)
    vh,lh=native_history(n,mus)
    for q in (-.015,.018):
        step=safe_constant_shear_dlna(e,shear_q=q)
        zface=face_z(1600.,n,step)
        out=causal_incoming_from_accepted_histories(
            energies_eV=e,virtual_history=vh,lyman_history=lh,
            z_start=1600.,z_face=zface,
            mu_face=np.linspace(-1,1,45),
            mu_grid=mus,iz=n,shear_q=q,dlna=step,
            radiation_T_face_K=2.7255*(1+zface)
        )
        assert out.virtual_distortion.shape==(45,311)
        assert out.lya_lyb_incoming_distortion.shape==(45,2)
        assert not out.virtual_distortion.flags.writeable
        assert np.any(out.geometric_planck_correction!=0)
        # Native accepted histories are affine in time and in mu, and
        # bilinear interpolation must return this manufactured exact value.
        src,_,_=_source_edges(e)
        tindex=(out.retarded_eta+math.log1p(1600.))/step
        factor=(1+src[None,:]/250.) * (
            1+.23*out.emission_mu+tindex/1200
        )
        # virtual rows <311 and 3 line boundary rows use different law
        oracle=np.where(src[None,:]<311, 1e-7*factor,
            1e-8*(1+(src[None,:]-311)/5.)*
            (1+.37*out.emission_mu-tindex/2200))
        expected=oracle+out.geometric_planck_correction
        np.testing.assert_allclose(
            np.concatenate((out.virtual_distortion,
                            out.lya_lyb_incoming_distortion),axis=1),
            expected,atol=8e-20,rtol=2e-11
        )


def test_geometric_planck_source_from_zero_initial_distortion():
    iz=512
    e=virtual_energies()
    q=.03
    step=safe_constant_shear_dlna(e,shear_q=q)
    z=face_z(1600.,iz,step)
    mus=np.linspace(-1,1,9)
    v=np.zeros((len(mus),311,iz))
    ly=np.zeros((len(mus),3,iz))
    rays=np.array([-1.,0.,1.])
    out=causal_incoming_from_accepted_histories(
        energies_eV=e,virtual_history=v,lyman_history=ly,
        z_start=1600.,z_face=z,iz=iz,mu_grid=mus,mu_face=rays,
        shear_q=q,radiation_T_face_K=2.7255*(1+z),
        dlna=step,
    )
    # q>0: transverse expansion is faster -> R<1 -> positive
    # anisotropic Planck distortion; z-axis has opposite sign.
    assert out.geometric_planck_correction[1,100]>0
    assert out.geometric_planck_correction[0,100]<0
    assert out.geometric_planck_correction[2,100]<0
    assert np.max(np.abs(out.virtual_distortion-
                         out.geometric_planck_correction[:,:311]))==0


def test_fail_closed_unaccepted_history_and_undefined_bianchi_prehistory():
    e=virtual_energies()
    iz=80
    v,ly=native_history(iz)
    with pytest.raises(ValueError,match="future"):
        causal_incoming_from_accepted_histories(
            energies_eV=e,virtual_history=v[0],lyman_history=ly[0],
            z_start=1600,z_face=face_z(1600,iz+150),iz=iz)
    n=17
    v,ly=native_history(iz,np.linspace(-1,1,n))
    with pytest.raises(ValueError,match="before"):
        causal_incoming_from_accepted_histories(
            energies_eV=e,virtual_history=v,lyman_history=ly,
            z_start=1600,z_face=1600,iz=iz,
            mu_grid=np.linspace(-1,1,n),mu_face=(.25,),
            shear_q=.02,radiation_T_face_K=3000)
    with pytest.raises(ValueError,match="directional redshift"):
        _retarded_lookback(np.array([.1]),np.array([0.]),-.6)


def test_native_flrw_history_step_is_not_causal_in_bianchi_direction():
    iz=512
    e=virtual_energies()
    q=.03
    mus=np.linspace(-1,1,17)
    v,ly=native_history(iz,mus)
    # The native FLRW frequency spacing is slightly wider than source DLNA,
    # but Bianchi parallel/anti-parallel transport has faster redshift.
    with pytest.raises(ValueError,match="unaccepted future"):
        causal_incoming_from_accepted_histories(
            energies_eV=e,virtual_history=v,lyman_history=ly,
            z_start=1600,z_face=face_z(1600,iz),iz=iz,
            mu_grid=mus,mu_face=(-1.,0.,1.),shear_q=q,
            radiation_T_face_K=2.7255*(1+face_z(1600,iz))
        )
    good=safe_constant_shear_dlna(e,shear_q=q)
    assert good<SOURCE_DLNA
    z=face_z(1600,iz,good)
    ok=causal_incoming_from_accepted_histories(
        energies_eV=e,virtual_history=v,lyman_history=ly,
        z_start=1600,z_face=z,iz=iz,
        mu_grid=mus,mu_face=(-1.,0.,1.),shear_q=q,
        radiation_T_face_K=2.7255*(1+z),dlna=good
    )
    assert np.all(np.isfinite(ok.virtual_distortion))


def test_first_order_geometric_Planck_quadrupole_with_zero_monopole():
    from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
        _planck_difference
    )
    mu, wg=np.polynomial.legendre.leggauss(96)
    p2=(3*mu*mu-1)/2
    x=25.0
    duration=.03
    result=[]
    for q in (.004,.002):
        B=-q*duration
        logR=B+.5*np.log1p(mu*mu*np.expm1(-6*B))
        df=_planck_difference(np.array(x),logR)
        monopole=0.5*float(np.dot(wg,df))
        quadrupole=2.5*float(np.dot(wg,p2*df))
        theoretical=-2*q*duration*x*math.exp(x)/(math.expm1(x)**2)
        assert abs(quadrupole/theoretical-1)<8e-4
        assert abs(monopole)<abs(quadrupole)*.01
        result.append((monopole,quadrupole))
    # Expected monopole O(q^2) vs quadrupole O(q)
    assert abs(result[0][0]/result[1][0]-4)<.025
    assert abs(result[0][1]/result[1][1]-2)<.003


def test_independent_prior_rec_phase_volume_map_agrees_with_q_characteristic():
    # Cross-module regression against independent C10 exact Killing map.
    from full_bianchi_hyrec.trajectory.axisymmetric_phase_space import (
        PreparedAxisymmetricPhaseVolume,
    )
    for q in (-.035,.024):
        d=.025
        mu=np.linspace(-.98,.98,61)
        directions=np.column_stack((
            np.sqrt(1-mu*mu),np.zeros_like(mu),mu
        ))
        old=PreparedAxisymmetricPhaseVolume(
            model_source_sha256="independent_c10_test",
            l_initial=0.0,l_face=d,
            delta_b_initial_minus_face=-q*d,delta_l=d,
        ).map(directions)
        ratio=np.log(old.energy_initial_over_face)
        recovered, emitted_mu, log_R=_retarded_lookback(ratio,mu,q)
        np.testing.assert_allclose(recovered,d,rtol=0,atol=4e-14)
        np.testing.assert_allclose(
            emitted_mu,old.initial_directions[:,2],rtol=2e-12,atol=4e-14)
        np.testing.assert_allclose(log_R,ratio-d,rtol=0,atol=4e-14)
        np.testing.assert_allclose(
            old.cubic_phase_space_normalized,1.0,
            rtol=5e-14,atol=5e-14)

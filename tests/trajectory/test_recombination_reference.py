"""Scientific reference-contract tests for upstream primordial recombination sources.

The fixtures are sampled from three actually compiled, source-identified,
massless-neutrino, no-reionization FLRW reference binaries, NOT a local REC
full-chemistry trajectory. Tests forbid unbound cosmology and implicit
xe/HII or matter-temperature unit conversions.
"""
from __future__ import annotations

from dataclasses import replace
import csv
import hashlib
from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.recombination_reference import (
    PrimordialReferenceHistory,RecombinationReferenceKind,
    compare_primordial_references,original_hyrec_atomic_table_supported_redshift,
)

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"research/rec_hyrec_reference_20261015/reference"
SOURCE_COSMO_SHA="f"*64


def _compact():
    with (BASE/"REFERENCE_SAMPLES.csv").open(newline="") as fh:
        rows=list(csv.DictReader(fh))
    assert len(rows)==14
    z=np.array([float(x["z"]) for x in rows[::-1]])
    histories={}
    for kind,source in (
        (RecombinationReferenceKind.HYREC_2012,"HyRec_2012_FULL"),
        (RecombinationReferenceKind.HYREC2_2020,"HyRec2_2020"),
        (RecombinationReferenceKind.RECFAST_17,"RECFAST_1.7"),
    ):
        temp=None if kind is RecombinationReferenceKind.RECFAST_17 else np.array(
            [float(row["Tm_K_"+source]) for row in rows[::-1]]
        )
        histories[source]=PrimordialReferenceHistory(
            kind=kind,redshift=z,
            xe_per_hydrogen=np.array([float(row["xe_"+source]) for row in rows[::-1]]),
            matter_temperature_K=temp,y_he_mass=.245,cmb_temperature_K=2.7255,
            source_identity=source,cosmology_sha256=SOURCE_COSMO_SHA,
            input_sha256="a"*64,output_sha256="b"*64,
        )
    return histories


def test_actual_three_code_samples_are_physically_normalized():
    h=_compact()
    assert all(len(r.redshift)==14 for r in h.values())
    for x in h.values():
        assert x.xe_per_hydrogen[0]>x.xe_per_hydrogen[-1]
        assert x.xe_per_hydrogen[0]>1.0  # helium can make xe>1!
        assert x.xe_per_hydrogen[-1]>0
        assert not x.xe_per_hydrogen.flags.writeable
        assert abs(x.helium_number_ratio-.0817)<.0001
    a=h["HyRec_2012_FULL"].evaluate(np.array([1100.]))[0]
    b=h["HyRec2_2020"].evaluate(np.array([1100.]))[0]
    c=h["RECFAST_1.7"].evaluate(np.array([1100.]))[0]
    assert abs(b/a-1)<1e-4
    assert abs(c/a-1)<.003


def test_reference_comparison_cannot_be_labeled_full_rec_native_history():
    h=_compact()
    x=compare_primordial_references(
        h["HyRec_2012_FULL"],h["HyRec2_2020"],
        z_min=600.,z_max=1600.,step=100.,
    )
    assert x["classification"]=="REFERENCE_TO_REFERENCE_ONLY_NOT_CURRENT_REC_SOLVER"
    assert x["scientific_admission"]=="REFERENCE_CODES_ONLY"
    assert x["maximum_abs_relative_xe_difference"]<.00012
    y=compare_primordial_references(
        h["HyRec_2012_FULL"],h["RECFAST_1.7"],
        z_min=600,z_max=1600,step=100)
    assert y["max_relative_matter_temperature"]["status"]=="NOT_AVAILABLE_UPSTREAM"


def test_cosmology_mismatch_is_rejected_even_if_T0_and_Y_he_match():
    h=_compact()
    mismatch=replace(h["HyRec2_2020"],cosmology_sha256="0"*64)
    with pytest.raises(ValueError,match="cosmology"):
        compare_primordial_references(h["HyRec_2012_FULL"],mismatch,
                                      z_min=600,z_max=1500)


def test_temperature_and_xe_conventions_cannot_be_swapped_silently(tmp_path):
    original=tmp_path/"old_HyRec.txt"
    z=np.arange(25.,10.,-1.)
    original.write_text("\n".join(
        f"{u} {0.0002+u*1e-7} 0.5" for u in z
    )+"\n")
    obj=PrimordialReferenceHistory.from_native_output(
      original,kind=RecombinationReferenceKind.HYREC_2012,
      y_he_mass=.245,cmb_temperature_K=2.7255,
      cosmology_sha256=SOURCE_COSMO_SHA,
      source_identity="HyRec original C",input_sha256="a"*64)
    np.testing.assert_allclose(obj.evaluate(np.array([13.,18.]),property="T_m_K"),
        .5*2.7255*(1+np.array([13.,18.])),rtol=2e-15)
    with pytest.raises(ValueError):
        PrimordialReferenceHistory.from_native_output(
            original,kind=RecombinationReferenceKind.RECFAST_17,
            y_he_mass=.245,cmb_temperature_K=2.7255,
            cosmology_sha256=SOURCE_COSMO_SHA,
            source_identity="modern RECFAST",input_sha256="a"*64)


@pytest.mark.parametrize("query", [[3.],[3001.],[float("nan")]])
def test_cannot_silently_extrapolate_reference_history(query):
    ref=_compact()["HyRec2_2020"]
    with pytest.raises(ValueError):
        ref.evaluate(query)


def test_recfast_does_not_supply_matter_temperature():
    ref=_compact()["RECFAST_1.7"]
    with pytest.raises(ValueError,match="not present"):
        ref.evaluate([1100.],property="T_m_K")


def test_original_hyrec_atomic_table_temperature_redshift_domain():
    low,high=original_hyrec_atomic_table_supported_redshift(cmb_temperature_K=2.7255)
    assert 16<low<17 and 1701<high<1704
    assert not low<=4<=high
    assert low<=1100<=high
    # These are table interpolation limits, not claims about full-ionization
    # history physics or the ability to evolve arbitrary Bianchi models.


def test_negative_or_too_large_electron_fraction_rejected():
    h=_compact()["HyRec_2012_FULL"]
    xe=np.array(h.xe_per_hydrogen,copy=True)
    xe[0]=-0.0001
    with pytest.raises(ValueError,match="electron"):
        replace(h,xe_per_hydrogen=xe)
    xe[0]=2.
    with pytest.raises(ValueError,match="electron"):
        replace(h,xe_per_hydrogen=xe)


def test_corrupted_output_file_cannot_claim_real_native_data(tmp_path):
    fname=tmp_path/"upstream.dat"
    fname.write_bytes(b"\n".join(b"1 0.3 1" for _ in range(20)))
    with pytest.raises(ValueError,match="redshift"):
        PrimordialReferenceHistory.from_native_output(
            fname,kind=RecombinationReferenceKind.HYREC2_2020,
            y_he_mass=.245,cmb_temperature_K=2.7255,
            cosmology_sha256=SOURCE_COSMO_SHA,
            source_identity="HyRec 2",input_sha256="a"*64)


def test_electron_fraction_species_ledger_is_not_hydrogen_only():
    from full_bianchi_hyrec.trajectory.recombination_reference import (
        electron_fraction_from_species,
    )
    f_he=.245/(3.97153*(1-.245))
    assert electron_fraction_from_species(
       x_HII=1.,x_HeII_per_nH=0.,x_HeIII_per_nH=f_he,
       helium_number_per_hydrogen=f_he)==pytest.approx(1+2*f_he)
    assert electron_fraction_from_species(
       x_HII=1.,x_HeII_per_nH=f_he,x_HeIII_per_nH=0.,
       helium_number_per_hydrogen=f_he)==pytest.approx(1+f_he)
    # Same xe does NOT fix individual H and He species abundances.
    a=electron_fraction_from_species(
       x_HII=.5,x_HeII_per_nH=.04,x_HeIII_per_nH=.0,
       helium_number_per_hydrogen=f_he)
    b=electron_fraction_from_species(
       x_HII=.48,x_HeII_per_nH=.02,x_HeIII_per_nH=.02,
       helium_number_per_hydrogen=f_he)
    assert a==pytest.approx(b)
    assert a==pytest.approx(.54)


def test_he_abundance_conservation_rejects_false_species_normalization():
    from full_bianchi_hyrec.trajectory.recombination_reference import (
        electron_fraction_from_species,
    )
    f_he=.245/(3.97153*(1-.245))
    for values in (
       dict(x_HII=1.1,x_HeII_per_nH=0.,x_HeIII_per_nH=0.),
       dict(x_HII=.5,x_HeII_per_nH=.5,x_HeIII_per_nH=0.),
       dict(x_HII=.5,x_HeII_per_nH=f_he,x_HeIII_per_nH=f_he),
       dict(x_HII=-.1,x_HeII_per_nH=0.,x_HeIII_per_nH=0.),
    ):
        with pytest.raises(ValueError):
            electron_fraction_from_species(
               helium_number_per_hydrogen=f_he,**values)


def test_current_rec_flrw_background_matches_hyrec_H_of_z_and_H_number():
    import json
    from full_bianchi_hyrec.trajectory.recombination_reference import (
        hyrec_source_equivalent_flrw_background,
        hyrec_source_hubble_per_s,
        hyrec_source_hydrogen_number_density_m3,
    )
    source=json.loads((BASE/"REFERENCE_INTERCOMPARISON.json").read_text())
    c=source["source_locked_flrw_cosmology"]
    args=dict(h=c["h"],omega_cb=c["Omega_cb"],
              omega_r_h2=c["Omega_r_h2"],omega_de_h2=c["Omega_de_h2"])
    model=hyrec_source_equivalent_flrw_background(**args)
    assert model.q_ref==0.
    assert model.same_h is False
    for z in (3000.,2500.,2000.,1700.,1600.,1100.,800.,600.):
        a=1./(1.+z)
        point=model.point(a)
        ref=hyrec_source_hubble_per_s(z=z,**args)
        assert abs(point.H_s_inv/ref-1.)<2e-13
        assert point.s_s_inv==0.
        actual_nH=hyrec_source_hydrogen_number_density_m3(
            z=z,omega_b_h2=c["Omega_b_h2"],y_he_mass=c["Y_He_mass_fraction"]
        )
        original_HyRec2012_nH0=11.223846333047*c["Omega_b_h2"]*(1.-c["Y_He_mass_fraction"])
        hyrec2_cgs_nH0=11.223846333047e-6*c["Omega_b_h2"]*(1.-c["Y_He_mass_fraction"])
        assert actual_nH==pytest.approx(original_HyRec2012_nH0*(1.+z)**3,rel=1e-14)
        assert actual_nH==pytest.approx(hyrec2_cgs_nH0*1e6*(1.+z)**3,rel=1e-14)
    first=model.interval_log(0.,np.log(model.a_end/model.a_ref))
    assert first.delta_t_s>0.
    assert first.delta_b==0.


def test_reference_background_rejects_cosmology_domain_leakage():
    from full_bianchi_hyrec.trajectory.recombination_reference import (
        hyrec_source_equivalent_flrw_background,
        hyrec_source_hubble_per_s,
    )
    for kw in (dict(h=-1.,omega_cb=.3,omega_r_h2=.00004,omega_de_h2=.3),
               dict(h=.673,omega_cb=.3,omega_r_h2=-.01,omega_de_h2=.3),
               dict(h=.673,omega_cb=.3,omega_r_h2=.00004,omega_de_h2=.3,
                    z_start=20.,z_end=3000.)):
        with pytest.raises(ValueError):
            hyrec_source_equivalent_flrw_background(**kw)
    with pytest.raises(ValueError):
        hyrec_source_hubble_per_s(z=-1,h=.673,
               omega_cb=.3,omega_r_h2=.00004,omega_de_h2=.3)


def test_hyrec_flat_background_rejects_mismatched_hubble_density_closure():
    from full_bianchi_hyrec.trajectory.recombination_reference import (
        hyrec_source_equivalent_flrw_background,
    )
    with pytest.raises(ValueError,match="density closure"):
        hyrec_source_equivalent_flrw_background(
            h=.6735837,omega_cb=.31242079216478097,
            omega_r_h2=4.1578740068818545e-5,
            omega_de_h2=.30,z_start=3000,z_end=600,
        )

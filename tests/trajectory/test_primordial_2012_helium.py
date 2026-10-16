from __future__ import annotations
import math
import pytest

from full_bianchi_hyrec.trajectory.primordial_2012_helium import (
    HyRec2012Cosmology, integrate_helium_stages, saha_heii_iii,
)


def test_source_identity_grid_and_he_stage_boundaries():
    c=HyRec2012Cosmology()
    h=integrate_helium_stages(c)
    first_heii=h.stage.index("HeII_RECOMBINATION")
    assert c.izH0==18223
    assert h.iz==(tuple(range(c.izH0+1)))
    assert h.stage[:first_heii]==("HeIII_SAHA",)*first_heii
    assert h.stage[first_heii]=="HeII_RECOMBINATION"
    assert h.update_method[first_heii]=="POST_SAHA"
    assert next(i for i,m in enumerate(h.update_method) if m=="SOURCE_PREDICTOR")==12084
    assert h.z[-1]==pytest.approx(1702.072263548342,abs=2e-12)


def test_species_ledgers_and_finite_physical_states():
    c=HyRec2012Cosmology()
    h=integrate_helium_stages(c)
    for i in range(len(h.iz)):
        assert all(math.isfinite(v) for v in (h.xe[i],h.xHII[i],h.xHeI[i],h.xHeII[i],h.xHeIII[i],h.Tm_K[i],h.helium_rhs_dln_a[i]))
        assert min(h.xHII[i],h.xHeI[i],h.xHeII[i],h.xHeIII[i])>=0
        assert abs(h.xHII[i]+h.xHeII[i]+2*h.xHeIII[i]-h.xe[i])<5e-13
        assert abs(h.xHeI[i]+h.xHeII[i]+h.xHeIII[i]-c.fHe)<5e-13
        assert h.Tm_K[i]>0


def test_saha_helium_output_domain_and_invalid_inputs():
    c=HyRec2012Cosmology()
    xe,x3=saha_heii_iii(c,c.redshift(0))
    assert xe==pytest.approx(1+c.fHe+x3,abs=2e-15)
    with pytest.raises(ValueError):
        HyRec2012Cosmology(YHe=0.0)
    with pytest.raises(ValueError):
        HyRec2012Cosmology(T0_K=float("nan"))

"""Canonical-input integration checks. Not executed by the host component suite.

Run on the authenticated clone; the inherited exact CSV is required, no skip.
These test native-reference restart attribution, not physical COM deposition.
"""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
import pytest
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import parse_original_hyrec_boundary_snapshot_csv
from full_bianchi_hyrec.trajectory.context_bound_split import ContextBoundSplitDomainReplacement as SplitDomainReplacement

SOURCE = (Path(__file__).resolve().parents[2] /
          'archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55/pr04c_z1100.csv')


@pytest.fixture(scope='module')
def case():
    assert SOURCE.is_file(), 'canonical snapshot unavailable; do not synthesize a substitute'
    parsed = parse_original_hyrec_boundary_snapshot_csv(SOURCE)
    instance = SplitDomainReplacement.from_snapshot(parsed.trajectory, parsed.boundaries[0].doppler_width_eV)
    return instance, instance.restart_record()


def test_canonical_v2_restart_roundtrip(case):
    instance,record=case
    restored=instance.state_from_restart_record(json.loads(json.dumps(record,allow_nan=False)))
    np.testing.assert_array_equal(restored.full_state,np.asarray(record['full_state']))
    assert record['schema']=='rec-split-domain-restart/v2'
    assert record['representation']=='NATIVE_PROXY_ALGEBRA_ONLY_NOT_PHYSICAL_COM'


@pytest.mark.parametrize('name',['doppler_width_eV','fsR','meR','nH_cm3','H_s_inv','energy_eV','matrix'])
def test_canonical_context_mutation_is_rejected_before_restore(case,name):
    instance,record=case
    if name=='doppler_width_eV':
        changed=replace(instance,doppler_width_eV=instance.doppler_width_eV*1.000001)
    elif name=='matrix':
        a=instance._full_matrix.copy();a[0,0]=np.nextafter(a[0,0],np.inf)
        changed=replace(instance,_full_matrix=a)
    elif name=='energy_eV':
        a=instance.snapshot.energy_eV.copy();a[0]=np.nextafter(a[0],np.inf)
        changed=replace(instance,snapshot=replace(instance.snapshot,energy_eV=a))
    else:
        changed=replace(instance,snapshot=replace(instance.snapshot,**{name:getattr(instance.snapshot,name)*1.000001}))
    with pytest.raises(ValueError,match='scientific context'):
        changed.state_from_restart_record(record)


def test_canonical_legacy_record_is_rejected(case):
    instance,record=case
    legacy=dict(record,schema='rec-split-domain-restart/v1')
    legacy.pop('scientific_context');legacy.pop('scientific_context_sha256')
    with pytest.raises(ValueError,match='schema'):
        instance.state_from_restart_record(legacy)

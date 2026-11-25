import numpy as np
from pathlib import Path
from full_bianchi_hyrec.trajectory.atomic_point_transfer import point_partition,audit_source
from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import OriginalHyRecTwoPhotonRamanTable
from full_bianchi_hyrec.recoil.calibrated_source import owner_cells
ARCHIVE=Path(__file__).resolve().parents[1]/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
def test_actual_spike_support_and_positive_number_energy_deposit():
    tab=OriginalHyRecTwoPhotonRamanTable.from_archive(ARCHIVE)
    for sub in (1,4):
        x,idx,P,det=point_partition(tab.energy_eV,owner_cells(),sub)
        assert list(idx)==list(range(136,144))
        assert np.min(P)>=0
        assert np.max(abs(P.sum(axis=0)-1))<1e-14
        assert np.max(abs(x@P-det))<1e-13
def test_exact_native_edge_partition_and_2s_detailed_balance():
    a=audit_source(ARCHIVE,2999.967,3000.,.85,1e-16,4)
    assert a["native_inside"]==6 and a["native_cross"]==2 and a["native_centre"]==2
    assert a["native_reassembly_relative"]<1e-14
    assert a["thermal_null_relative"]<1e-13
    assert a["source_number_residual"]<1e-13 and a["source_energy_residual"]<1e-13

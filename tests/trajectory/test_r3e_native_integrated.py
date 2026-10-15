"""Original HyRec2012 C vs independently evolved REC Python photon histories."""
from __future__ import annotations

from pathlib import Path
import sys

# CI invokes bare `pytest -q`; scripts/ is intentionally not an installed package.
# Bind the exact repository scripts directory for this source-oracle test only.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import numpy as np
import pytest

from verify_r3e_native_integrated import (
    ARCHIVE, ORIGINAL_SHA, _c_row_views,
    compile_unmodified_native, paired_full_history_case, run_one,
)


def test_C_pointer_history_in_place_alias_and_no_copy():
    a=np.zeros((3,7),dtype=np.float64,order="C")
    pp=_c_row_views(a)
    pp[1][3]=4.5
    assert a[1,3]==4.5
    a[2,5]=-7.
    assert pp[2][5]==-7.
    with pytest.raises(ValueError, match="contiguous"):
        _c_row_views(a[:,::2])


def test_pinned_original_source_and_independently_generated_history():
    assert ARCHIVE.is_file()
    data=run_one(steps=33,z=900.,x=.04,ratio=.98)
    assert data["compilation"]["source_archive_sha256"]==ORIGINAL_SHA
    assert data["status"]=="PASS_SOURCE_FULL_HISTORY_PARITY"
    assert data["experiment"]["parallel_independent_c_chemistry_photons"]
    assert data["experiment"]["shared_background_H_nH_and_thermochemistry"]
    assert data["not_original_production_integrator"]
    assert data["no_physical_primordial_prehistory"]
    errors=data["experiment"]["comparisons"]
    assert errors["virtual_out"]["shape"]==[311,33]
    assert errors["lyman_out"]["shape"]==[3,33]
    assert all(0<=errors[k]["max_rel_global"]<1e-7 for k in errors)
    assert data["experiment"]["native_final_x"]<.04
    assert data["experiment"]["python_final_x"]<.04


def test_source_step_shape_thermo_domain_and_native_full_history(tmp_path):
    so,native,receipt=compile_unmodified_native(tmp_path)
    case=paired_full_history_case(
        so=so,native=native,z_start=900.,x_start=.05,
        Tm_fraction=.985,steps=19)
    assert case["max_python_schur_residual"]<2e-10
    assert case["comparisons"]["virtual_out"]["max_rel_global"]<1e-7
    assert case["comparisons"]["xe"]["max_rel_global"]<1e-7
    assert receipt["binary_sha256"] and so.is_file()


def test_source_hash_guard_disallows_unauthorized_replacement(tmp_path,monkeypatch):
    import verify_r3e_native_integrated as module
    counterfeit=tmp_path/"counterfeit.zip"
    counterfeit.write_bytes(b"untrusted C source")
    monkeypatch.setattr(module,"ARCHIVE",counterfeit)
    with pytest.raises(ValueError,match="SHA drift"):
        compile_unmodified_native(tmp_path)

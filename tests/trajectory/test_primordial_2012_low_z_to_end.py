"""Bounded U8 source clock, low-z switch, interpolation and guard tests."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from full_bianchi_hyrec.trajectory.primordial_2012_low_z_to_end import (
    START_J,END_J,START_GLOBAL_IZ,END_GLOBAL_IZ,EXTRA_ACCEPTED,SOURCE_NZ,
    SOURCE_Z0_FRACTION,source_interp1d,source_z0_clamped_cubic,
    source_emla_table_guard,peebles_rhs_ln_a,load_admitted_u7_stop,
    continue_low_z_to_end,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs

SPEC=importlib.util.spec_from_file_location("u8_verify",ROOT/"scripts/verify_r3g_low_z_to_end.py")
V=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def _fixture(tm=9.3):
    c=HyRec2012Cosmology();j=START_J
    cp={"global_iz":np.arange(18223,18223+j+1,dtype=int),
        "z":np.array([c.redshift(i) for i in range(18223,18223+j+1)]),
        "xe":np.full(j+1,.00021),"Tm_K":np.full(j+1,tm),
        "xHII":np.full(j+1,.00021),"xH1s":np.full(j+1,.99979),
        "xHeII":np.zeros(j+1),"post_saha":np.zeros(j+1,dtype=bool),
        "hydrogen_rhs_dln_a":np.full(j,-2.5e-5),
        "thermal_rhs_dln_a":np.full(j,-18.)}
    boundary={"hydrogen_prev":-2.5e-5,"hydrogen_prev2":-2.51e-5,
              "thermal_prev":-18.,"thermal_prev2":-18.1}
    return c,cp,boundary


def test_source_end_and_clamped_cubic_fraction():
    assert (START_GLOBAL_IZ,END_GLOBAL_IZ,EXTRA_ACCEPTED,SOURCE_NZ)==(69999,105858,35859,105859)
    assert 1<SOURCE_Z0_FRACTION<2
    c=HyRec2012Cosmology()
    assert c.redshift(END_GLOBAL_IZ)<0<c.redshift(END_GLOBAL_IZ-1)
    # The final negative-z grid node is used for z0 interpolation, never RHS.
    y=np.arange(END_J+1,dtype=float)
    result=source_z0_clamped_cubic(y)
    assert result["source_globals"]==[105855,105856,105857,105858]
    assert result["value"]==pytest.approx(105856-18223+SOURCE_Z0_FRACTION,abs=2e-10)


def test_generic_source_interpolation_clamps_both_ends():
    y=np.arange(SOURCE_NZ,dtype=float)
    first=source_interp1d(y,8000.)
    last=source_interp1d(y,0.)
    assert first["clamped_index"]==1 and first["fraction"]==pytest.approx(-1)
    assert first["value"]==pytest.approx(0,abs=1e-12)
    assert last["clamped_index"]==105856 and last["fraction"]==pytest.approx(SOURCE_Z0_FRACTION)
    assert last["value"]==pytest.approx(math.log(8001.)/8.49e-5,abs=2e-10)
    with pytest.raises(ValueError,match="DOMAIN"):source_interp1d(y,-.01)


def test_pinned_u7_loader_rejects_tampering(tmp_path):
    files=[tmp_path/f"input{i}" for i in range(5)]
    for f in files:f.write_text("not pinned")
    with pytest.raises(ValueError,match="U7_PINNED_INPUT_SHA_MISMATCH"):
        load_admitted_u7_stop(*files)


def test_peebles_rhs_finite_at_low_z_and_table_guard_reason():
    c=HyRec2012Cosmology()
    assert math.isfinite(peebles_rhs_ln_a(c,0.,.0001,.02))
    assert source_emla_table_guard(c,20.,9.3)==(True,None)
    assert source_emla_table_guard(c,20.,5.)==(False,"TM_TR_MIN")
    assert source_emla_table_guard(c,0.,.02)==(False,"TR_MIN")


def test_first_false_guard_absorbing_peebles_and_no_emla_call():
    c,cp,boundary=_fixture(tm=5.)
    class EmlaForbidden:
        def hydrogen_rhs_ln_a(self,**kwargs):raise AssertionError("EMLA after event")
    class Oracle:
        def __call__(self,model,iz,z,xe,tm):
            assert model=="PEEBLES"
            return peebles_rhs_ln_a(c,z,xe,tm)
        def thermal_rhs(self,xe,tm,z):return source_thermal_rhs(c,xe,tm,z)
    receipts=[]
    r=continue_low_z_to_end(cp,boundary,c,EmlaForbidden(),common_input_oracle=Oracle(),
        checkpoint_callback=receipts.append,max_extra_accepted=2)
    assert r["accepted_extra"]==2 and r["attempted_evaluations"]==2
    assert r["models"]==["PEEBLES","PEEBLES"]
    assert r["event"]["global_iz"]==START_GLOBAL_IZ
    assert r["event"]["reason"]=="TM_TR_MIN"
    assert any(x["phase"]=="PEEBLES_EVENT" for x in receipts)
    assert r["hydrogen_prev2"]==pytest.approx(r["hydrogen_rhs_dln_a"][-2])


def test_rejected_candidate_preserves_accepted_memories():
    c,cp,boundary=_fixture()
    class Huge:
        def hydrogen_rhs_ln_a(self,**kwargs):return -1e8
    class Oracle:
        def __call__(self,*args):raise AssertionError("rejected input not sampled")
        def thermal_rhs(self,*args):raise AssertionError("rejected input not sampled")
    receipts=[]
    r=continue_low_z_to_end(cp,boundary,c,Huge(),common_input_oracle=Oracle(),
        checkpoint_callback=receipts.append,max_extra_accepted=1)
    assert r["status"]=="HOLD_NEXT_STAGE_REQUIRED:LOW_Z_ACCEPTED_STATE_DOMAIN"
    assert r["accepted_extra"]==0 and r["attempted_evaluations"]==1
    for key in ("hydrogen_prev","hydrogen_prev2","thermal_prev","thermal_prev2"):
        assert r[key]==boundary[key] and receipts[-1][key]==boundary[key]
    assert receipts[-1]["failure"]["candidate_j"]==START_J+1


def test_parser_rejects_unexpected_model_or_nonfinite(tmp_path):
    path=tmp_path/"native.csv"
    path.write_text("U8NODE,51776,69999,19.99,0.00021,9.3,-.000025,-.0000251,-18,-18.1\n"
                    "U8STEP,51776,69999,19.99,0.00021,9.3,nan,-18,-.000025,-.0000251,-18,-18.1,EMLA2s2p,.0049,.16,70000,19.98,.0002,9.29\n"
                    "U8END,BOUNDED_LOW_Z_INTERVAL_COMPLETE_BEFORE_SOURCE_END,51777,1,-1,NONE\n")
    with pytest.raises(ValueError,match="STEP_COUNT_OR_FINITE"):V.parse_native(path,1)
    text=path.read_text().replace("EMLA2s2p","UNKNOWN")
    path.write_text(text)
    with pytest.raises(ValueError,match="STEP_MODEL_OR_GRAMMAR"):V.parse_native(path,1)


def test_manifest_rejects_missing_frozen_inputs(tmp_path):
    path=tmp_path/"manifest.json";path.write_text("{}")
    with pytest.raises(ValueError,match="U8_MANIFEST_INPUT_SHA"):V.validate_manifest(path)


def test_regenerated_text_sha_mismatch_is_separate_from_numeric_gate():
    assert V.regenerated_baseline_byte_status(V.BASELINE_STDOUT_SHA256)=="BYTE_IDENTITY_MATCH"
    assert V.regenerated_baseline_byte_status("0"*64)=="BYTE_IDENTITY_MISMATCH"

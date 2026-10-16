"""Cheap U7 clock, admission, recurrence, and C record guard tests."""
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from full_bianchi_hyrec.trajectory.primordial_2012_emla_to_z20 import (
    START_J,END_J,END_GLOBAL_IZ,EXTRA_ACCEPTED,SAMPLE_J,
    load_admitted_u6_stop,source_cubic_weights,source_z20_cubic,continue_emla_to_z20,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology

SPEC=importlib.util.spec_from_file_location("u7_verify",ROOT/"scripts/verify_r3g_emla_to_z20.py")
V=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def test_source_clock_cubic_and_fixed_samples():
    assert (START_J,END_J,END_GLOBAL_IZ,EXTRA_ACCEPTED)==(10972,51776,69999,40804)
    assert len(SAMPLE_J)==25 and SAMPLE_J[-3:]==(51773,51774,51775)
    weights=source_cubic_weights(.37)
    assert sum(weights)==pytest.approx(1,abs=1e-15)
    y=np.arange(END_J+1,dtype=float)
    result=source_z20_cubic(y)
    assert result["source_globals"]==[69996,69997,69998,69999]
    assert result["value"]==pytest.approx((result["index"]-18223)+result["fraction"],abs=2e-11)


def test_missing_or_tampered_admission_rejected(tmp_path):
    files=[tmp_path/f"input{i}" for i in range(5)]
    for f in files:f.write_bytes(b"not pinned")
    with pytest.raises(ValueError,match="U6_PINNED_INPUT_SHA_MISMATCH"):
        load_admitted_u6_stop(*files)


def test_native_parser_rejects_missing_rows_and_nonfinite(tmp_path):
    p=tmp_path/"c.csv"
    p.write_text("U7NODE,10972,29195,669,0.001,1822,1,2,3,4\n"
                 "U7STEP,10972,29195,669,0.001,1822,nan,1,2,3,4,5,29196,668,0.001,1821,EMLA2s2p\n"
                 "U7END,BOUNDED_EMLA_INTERVAL_COMPLETE_BEFORE_Z20_STENCIL,10973,1\n")
    with pytest.raises(ValueError,match="U7_C_STEP_COUNT_OR_FINITE"):
        V.parse_native(p,1)


def test_manifest_requires_frozen_code_and_input(tmp_path):
    path=tmp_path/"manifest.json";path.write_text("{}")
    with pytest.raises(ValueError,match="U7_MANIFEST_INPUT_SHA"):
        V.validate_manifest(path)


def test_common_oracle_signature_and_thermal_source(tmp_path):
    # Parse fixture tests remain independent of a compiled native source.
    assert callable(V.CommonOracle)
    assert HyRec2012Cosmology().izH0==18223
    assert math.isfinite(HyRec2012Cosmology().redshift(END_GLOBAL_IZ))


def _synthetic_boundary(tm=1800.):
    c=HyRec2012Cosmology();j=START_J
    cp={"global_iz":np.arange(18223,18223+j+1,dtype=int),
        "z":np.array([c.redshift(i) for i in range(18223,18223+j+1)]),
        "xe":np.full(j+1,.0013),"Tm_K":np.full(j+1,tm),
        "xHII":np.full(j+1,.0013),"xH1s":np.full(j+1,.9987),
        "xHeII":np.zeros(j+1),"post_saha":np.zeros(j+1,dtype=bool),
        "hydrogen_rhs_dln_a":np.full(j,-.004),
        "thermal_rhs_dln_a":np.full(j,-1800.)}
    boundary={"hydrogen_prev":-.004,"hydrogen_prev2":-.006,
              "thermal_prev":-1800.,"thermal_prev2":-1900.}
    return c,cp,boundary


def test_one_step_carries_both_source_derivative_memories():
    c,cp,boundary=_synthetic_boundary()
    class Source:
        def hydrogen_rhs_ln_a(self,**kwargs):return -.005
    class Oracle:
        def __call__(self,*args):return -.005
        def thermal_rhs(self,*args):
            from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs
            return source_thermal_rhs(c,args[0],args[1],args[2])
    r=continue_emla_to_z20(cp,boundary,c,Source(),common_input_oracle=Oracle(),max_extra_accepted=1)
    h=8.49e-5
    assert r["accepted_extra"]==1
    assert r["nodes"]["xe"][-1]==pytest.approx(.0013+h*(1.25*(-.005)-.25*(-.006)),abs=1e-18)
    assert r["hydrogen_prev2"]==pytest.approx(-.004)
    assert r["hydrogen_prev"]==pytest.approx(-.005)
    assert r["thermal_prev2"]==pytest.approx(-1800.)


def test_rejected_candidate_retains_last_accepted_state_and_memories():
    c,cp,boundary=_synthetic_boundary()
    class Source:
        def hydrogen_rhs_ln_a(self,**kwargs):return -1e8
    class Oracle:
        def __call__(self,*args):return -1e8
        def thermal_rhs(self,xe,tm,z):
            from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs
            return source_thermal_rhs(c,xe,tm,z)
    receipts=[]
    r=continue_emla_to_z20(cp,boundary,c,Source(),common_input_oracle=Oracle(),
                            max_extra_accepted=1,checkpoint_callback=receipts.append)
    assert r["status"]=="HOLD_NEXT_STAGE_REQUIRED:EMLA_ACCEPTED_STATE_DOMAIN"
    assert r["accepted_extra"]==0 and r["emla_evaluations"]==1
    assert r["hydrogen_prev"]==boundary["hydrogen_prev"]
    assert r["hydrogen_prev2"]==boundary["hydrogen_prev2"]
    assert r["thermal_prev"]==boundary["thermal_prev"]
    assert r["thermal_prev2"]==boundary["thermal_prev2"]
    assert r["nodes"]["xe"][-1]==.0013
    assert receipts[-1]["phase"]=="STOP"
    assert receipts[-1]["emla_evaluations_attempted"]==1
    assert receipts[-1]["failure"]["candidate_j"]==START_J+1
    assert receipts[-1]["hydrogen_prev"]==boundary["hydrogen_prev"]


def test_thermal_guard_keeps_same_typed_c_and_python_status(tmp_path):
    c,cp,boundary=_synthetic_boundary(tm=100.)
    class Uncalled:
        def hydrogen_rhs_ln_a(self,**kwargs):raise AssertionError("guard must run first")
        def __call__(self,*args):raise AssertionError("guard must run first")
        def thermal_rhs(self,*args):raise AssertionError("guard must run first")
    oracle=Uncalled()
    r=continue_emla_to_z20(cp,boundary,c,Uncalled(),common_input_oracle=oracle,max_extra_accepted=1)
    status="HOLD_NEXT_STAGE_REQUIRED:THERMAL_TABLE_OR_RATIO_BOUNDARY"
    assert r["status"]==status and r["accepted_extra"]==0 and r["emla_evaluations"]==0
    path=tmp_path/"c.csv"
    path.write_text(f"U7NODE,10972,29195,669,0.0013,100,-0.004,-0.006,-1800,-1900\n"
                    f"U7END,{status},10972,0\n")
    assert V.parse_native(path,1)["end"][0]==r["status"]
    assert status in (ROOT/"scripts/c_harness/original_hyrec_emla_to_z20_harness.c").read_text()

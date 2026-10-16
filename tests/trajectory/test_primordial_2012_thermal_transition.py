"""Cheap U5 admission checks; pytest does not run a primordial trajectory."""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src")); sys.path.insert(0,str(ROOT/"scripts"))
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import (
 START_J,U4_STOP_NPZ_SHA256,U4_STOP_JSON_SHA256,U4_VERIFICATION_SHA256,
 load_reviewed_u4_stop,continue_thermal_transition,classify_stop_status,
 source_thermal_rhs,sha256,
)
from verify_r3g_thermal_transition import parse_native

def test_frozen_u4_checkpoint_identity_required(tmp_path):
    a=tmp_path/"stop.npz"; b=tmp_path/"stop.json"; c=tmp_path/"verification.json"
    a.write_bytes(b"wrong"); b.write_text("{}"); c.write_text("{}")
    with pytest.raises(ValueError,match="REVIEWED_U4_IDENTITY_MISMATCH"):
        load_reviewed_u4_stop(a,b,c)

def test_oracle_and_cap_required_before_state_access():
    with pytest.raises(ValueError,match="COMMON_INPUT_C_ORACLE_REQUIRED"):
        continue_thermal_transition({},None,None,common_input_oracle=None)
    class Oracle:
        def __call__(self,*a): return None
        def thermal_rhs(self,*a): return None
    with pytest.raises(ValueError,match="EXTRA_ACCEPTED_CAP_INVALID"):
        continue_thermal_transition({},None,None,common_input_oracle=Oracle(),max_extra_accepted=8193)

def test_mid_event_cap_is_hold():
    s="BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED"
    assert classify_stop_status(s,1200,1)=="HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE"
    assert classify_stop_status(s,None,0)==s

def test_source_thermal_guard_and_finite_coupling():
    c=HyRec2012Cosmology(); z=1500.; tr=c.T0_K*(1.+z)
    assert source_thermal_rhs(c,.9,tr,z)==-tr
    assert source_thermal_rhs(c,.9,tr/(1.+0.5e-10),z)==-tr
    rhs=source_thermal_rhs(c,.9,tr*.999,z)
    assert math.isfinite(rhs) and rhs != -tr

def test_parser_rejects_false_event_success(tmp_path):
    p=tmp_path/"c.csv"
    p.write_text("U5NODE,19227,1562.918035636796,0.0123134991084828,0.9876865008915172,0,0.9876865008915172,4262.453568037749,0\n"
      "U5END,THERMAL_EVENT_TWO_STEPS_COMPLETE,-1,2,0\n")
    with pytest.raises(ValueError,match="C_U5_FALSE_EVENT_SUCCESS"):
        parse_native(p)

@pytest.mark.skipif(not os.getenv("R3G_U4_STOP_DIR"),reason="reviewed U4 raw is external to Git")
def test_actual_reviewed_u4_checkpoint(tmp_path):
    d=Path(os.environ["R3G_U4_STOP_DIR"])
    a=d/"checkpoint_0007_stop.npz"; b=d/"checkpoint_0007_stop.json"; c=d/"verification.json"
    assert (sha256(a),sha256(b),sha256(c)) == (
      U4_STOP_NPZ_SHA256,U4_STOP_JSON_SHA256,U4_VERIFICATION_SHA256)
    node=load_reviewed_u4_stop(a,b,c)
    assert node["global_iz"].shape==(START_J+1,)
    assert node["virtual_out"].shape==(311,START_J)
    bad=tmp_path/"bad.npz"; bad.write_bytes(a.read_bytes()+b"x")
    with pytest.raises(ValueError,match="REVIEWED_U4_IDENTITY_MISMATCH"):
        load_reviewed_u4_stop(bad,b,c)

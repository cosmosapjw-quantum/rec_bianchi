"""Cheap U4 admission checks; no primordial trajectory is run by pytest."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"scripts"))
from full_bianchi_hyrec.trajectory.primordial_2012_hydrogen_transition import (
    START_J, U3_STOP_NPZ_SHA256, U3_STOP_JSON_SHA256,
    U3_VERIFICATION_SHA256, sha256, load_reviewed_u3_stop,
    continue_hydrogen_steady, classify_stop_status,
)
from verify_r3g_hydrogen_transition import parse_native


def test_frozen_u3_checkpoint_identity_is_required(tmp_path):
    a=tmp_path/"stop.npz"; b=tmp_path/"stop.json"; c=tmp_path/"verification.json"
    a.write_bytes(b"not the reviewed checkpoint")
    b.write_text(json.dumps({"phase":"STOP","accepted_extra":374}))
    c.write_text(json.dumps({"status":"EVENT_TWO_STEPS_COMPLETE"}))
    with pytest.raises(ValueError,match="REVIEWED_U3_IDENTITY_MISMATCH"):
        load_reviewed_u3_stop(a,b,c)


def test_execution_requires_independent_common_input_oracle():
    with pytest.raises(ValueError,match="COMMON_INPUT_C_ORACLE_REQUIRED"):
        continue_hydrogen_steady({},None,None,common_input_oracle=None)


def test_cap_rejected_before_source_or_state_access():
    with pytest.raises(ValueError,match="EXTRA_ACCEPTED_CAP_INVALID"):
        continue_hydrogen_steady({},None,None,common_input_oracle=lambda *a:None,
                                 max_extra_accepted=2049)


def test_cap_mid_event_is_typed_hold_not_no_event_completion():
    bounded="BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED"
    assert classify_stop_status(bounded,383,0)=="HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE"
    assert classify_stop_status(bounded,383,1)=="HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE"
    assert classify_stop_status(bounded,None,0)==bounded
    assert classify_stop_status("HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY",383,0)=="HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY"


def test_native_parser_rejects_false_success(tmp_path):
    p=tmp_path/"native.csv"
    p.write_text("META,18223,10972,1702.072263548342\n"
                 "U4NODE,18605,1647.72462398495,0.0020742,0.9979258,0,0.9979258,4493.59429403,1\n"
                 "U4END,EVENT_TWO_STEPS_COMPLETE,0,2,0\n")
    with pytest.raises(ValueError,match="C_U4_FALSE_EVENT_SUCCESS"):
        parse_native(p)


@pytest.mark.parametrize(("body","reason"),[
    ("U4NODE,18605,nan,0.002,0.998,0,0.998,4493,1\n","C_NONFINITE:node.z"),
    ("U4NODE,18605,1647.7,0.002,0.998,0,0.998,4493,2\n","C_NONBOOLEAN_FLAG:node.post_saha"),
    ("U4NODE,18605,1647.7,0.002,0.998,0,0.998,4493,1\n"
     "U4STEP,382,18606,1647.5,0.002,0.998,0.998,4492,inf,1,0\n",
     "C_NONFINITE:step.hydrogen_rhs"),
    ("U4NODE,18605,1647.7,0.002,0.998,0,0.998,4493,1\n"
     "V,382,0,-inf\n","C_NONFINITE:V.spectrum"),
])
def test_native_parser_rejects_nonfinite_and_invalid_flags(tmp_path,body,reason):
    p=tmp_path/"bad_native.csv"
    p.write_text("META,18223,10972,1702.072263548342\n"+body+
                 "U4END,BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED,0,0,0\n")
    with pytest.raises(ValueError,match=reason): parse_native(p)


@pytest.mark.skipif(not os.getenv("R3G_U3_STOP_DIR"),reason="reviewed U3 raw is external to Git")
def test_actual_reviewed_u3_accepts_only_its_exact_bytes(tmp_path):
    src=Path(os.environ["R3G_U3_STOP_DIR"])
    npz=src/"checkpoint_0374_stop.npz"
    side=src/"checkpoint_0374_stop.json"
    verified=src/"verification.json"
    assert (sha256(npz),sha256(side),sha256(verified)) == (
        U3_STOP_NPZ_SHA256,U3_STOP_JSON_SHA256,U3_VERIFICATION_SHA256)
    a=load_reviewed_u3_stop(npz,side,verified)
    assert a["global_iz"].shape==(START_J+1,)
    assert a["virtual_out"].shape==(311,START_J)
    assert a["hydrogen_rhs_dln_a"].shape==(START_J,)
    damaged=tmp_path/"damaged.npz"
    damaged.write_bytes(npz.read_bytes()+b"x")
    with pytest.raises(ValueError,match="REVIEWED_U3_IDENTITY_MISMATCH"):
        load_reviewed_u3_stop(damaged,side,verified)

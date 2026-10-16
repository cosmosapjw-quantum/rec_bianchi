"""Bounded U6 RT-stage contract checks; no primordial trajectory rerun."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.primordial_2012_full_thermal_continuation import (
    START_J, END_J, START_GLOBAL_IZ, END_GLOBAL_IZ, EXTRA_ACCEPTED, SAMPLE_J,
    U5_STOP_NPZ_SHA256, U5_SCOPED_AUDIT_SHA256, require_scoped_admission,
    continue_full_thermal_to_rt,
)

SCRIPT=Path(__file__).resolve().parents[2]/"scripts/verify_r3g_full_thermal_continuation.py"
sys.path.insert(0,str(SCRIPT.parent))
spec=importlib.util.spec_from_file_location("verify_r3g_full_thermal_continuation",SCRIPT)
verify=importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def test_exact_original_rt_boundary_and_fixed_common_samples():
    assert (START_J,END_J,START_GLOBAL_IZ,END_GLOBAL_IZ,EXTRA_ACCEPTED)==(8368,10972,26591,29195,2604)
    assert SAMPLE_J==(8368,8369,8624,8880,9136,9392,9648,9904,10160,10416,10672,10928,10970,10971)
    assert len(SAMPLE_J)==len(set(SAMPLE_J))==14
    assert all(START_J<=j<END_J for j in SAMPLE_J)


def test_scoped_admission_is_required_and_cannot_promote_original_fail(tmp_path):
    path=tmp_path/"admission.json"
    path.write_text(json.dumps({"decision":"SCOPED_PASS",
        "reviewed_audit_sha256":U5_SCOPED_AUDIT_SHA256,
        "reviewed_u5_stop_sha256":U5_STOP_NPZ_SHA256,
        "original_verification_status":"PASS",
        "original_average_gate":"PASS"}))
    with pytest.raises(ValueError,match="U5_SCOPED_ADMISSION_MISSING_OR_MISMATCH"):
        require_scoped_admission(path)
    path.write_text(json.dumps({"decision":"SCOPED_PASS",
        "reviewed_audit_sha256":U5_SCOPED_AUDIT_SHA256,
        "reviewed_u5_stop_sha256":U5_STOP_NPZ_SHA256,
        "original_verification_status":"FAIL",
        "original_average_gate":"HOLD_ORIGINAL_TOLERANCE_NOT_MET"}))
    assert require_scoped_admission(path)["decision"]=="SCOPED_PASS"


def test_one_step_c_stdout_parser_keeps_u6_only(tmp_path):
    p=tmp_path/"oracle.csv"
    rows=["META,18223,10972,1702.0","U5END,THERMAL_EVENT_TWO_STEPS_COMPLETE,8366,2,7364",
          "U6NODE,8368,26591,1000,0.5,0.5,2500,-1,-2,-3,-4",
          "U6STEP,8368,26592,999,0.51,0.49,2499,-1.1,-2.1,-1,-2.1,-3"]
    rows += [f"V,8368,{b},0" for b in range(311)]
    rows += [f"A,8368,{b},0" for b in range(311)]
    rows += [f"L,8368,{b},0" for b in range(3)]
    rows += ["U6END,BOUNDED_INTERVAL_COMPLETE_BEFORE_RT,8369,1"]
    p.write_text("\n".join(rows)+"\n")
    got=verify.parse_native(p)
    assert got["rows"].shape==(1,11)
    assert got["end"]==("BOUNDED_INTERVAL_COMPLETE_BEFORE_RT",8369,1)
    assert np.all(got["virtual"]==0)


def test_u6_rejects_unreviewed_or_oversized_work():
    with pytest.raises(ValueError,match="U6_ACCEPTED_CAP_INVALID"):
        continue_full_thermal_to_rt({}, {}, None, None,
            common_input_oracle=lambda *_:None,max_extra_accepted=EXTRA_ACCEPTED+1)
    with pytest.raises(ValueError,match="U6_COMMON_INPUT_C_ORACLE_REQUIRED"):
        continue_full_thermal_to_rt({}, {}, None, None,
            common_input_oracle=lambda *_:None,max_extra_accepted=1)

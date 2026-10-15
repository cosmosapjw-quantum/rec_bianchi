"""Checks pinned PR94 donor against real PR150 configuration source text."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from full_bianchi_hyrec.trajectory.rei_donor_config_audit import (
    audit_rei_donor_config,
)

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"research/rec_r3d_full_short_20261015"
PR94=ROOT/"research/rec_r3c_rei_bridge_20261015/REI_DONOR_CANDIDATE_OPTIN_ONLY.json"
SNAPSHOT=REPORT/"REI_PR150_DONOR_CONFIG_READONLY.cfg"
PR150_GIT_BLOB_SHA="d9dcdbb4b33ebfe89f6c1322cba2a83a7bab15a6"


def test_pr150_read_only_config_blob_identity_and_rec_donor_gate():
    content=SNAPSHOT.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()
    assert blob==PR150_GIT_BLOB_SHA
    packet=json.loads(PR94.read_text())
    result=audit_rei_donor_config(packet,content.decode("utf8"))
    assert result["source_rei_scenario_sha256"] == (
        "07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"
    )
    assert result["source_donor_x_HII"]==.000210349192936
    assert result["source_donor_Tgas_K"]==9.306042400380866
    assert result["decision"].endswith("NOT_NATIVE_REI_RESULT")


@pytest.mark.parametrize("key,old,new",[
    ("ionization","initial_x_hii=0.000210349192936","initial_x_hii=0.00020"),
    ("temperature","initial_temperature_k=9.306042400380866","initial_temperature_k=8.09"),
    ("shear","q_ref=0.0","q_ref=0.02"),
    ("end_zbar","end_zbar=4.0","end_zbar=3.0"),
])
def test_donor_rejects_unintended_recipient_drift(key,old,new):
    packet=json.loads(PR94.read_text())
    content=SNAPSHOT.read_text()
    assert old in content
    with pytest.raises(ValueError):
        audit_rei_donor_config(packet,content.replace(old,new))


def test_activation_and_duplicate_cfg_owner_fail_closed():
    packet=json.loads(PR94.read_text())
    content=SNAPSHOT.read_text()
    packet["activation"]="ADOPTED_WITHOUT_REI_RUN"
    with pytest.raises(ValueError,match="activation"):
        audit_rei_donor_config(packet,content)
    packet["activation"]="DISABLED_REQUIRES_SEPARATE_REI_SENSITIVITY_CAMPAIGN"
    with pytest.raises(ValueError,match="duplicate"):
        audit_rei_donor_config(packet,content+"q_ref=0.0\n")

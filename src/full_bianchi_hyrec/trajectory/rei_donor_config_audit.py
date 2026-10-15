"""Read-only contract audit for the existing REC PR94 -> REI PR150 donor.

No REI write, output launch, or automatic opt-in. This is only a testable
handoff constraint, not primordial spectral or reionization evolution.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Mapping


def audit_rei_donor_config(packet: Mapping, config_text: str) -> dict:
    """Check independent REI cfg against immutable typed REC donor packet."""
    if packet.get("schema") != "rei.conditional.primordial_donor_candidate.v1":
        raise ValueError("unknown source REC donor schema")
    if packet.get("activation") != "DISABLED_REQUIRES_SEPARATE_REI_SENSITIVITY_CAMPAIGN":
        raise ValueError("REC donor activation silently changed")
    if packet.get("adopted_into_original_REI_scenario") is not False:
        raise ValueError("REI source scenario must remain unchanged")
    if packet.get("model") != "ORIGINAL_HYREC_2012_FULL_H_HE_FLRW_Q0_CONDITIONAL":
        raise ValueError("source model does not identify original q0 HyRec")
    signature = packet.get("source_rei_scenario_sha256")
    if not isinstance(signature,str) or not re.fullmatch("[0-9a-f]{64}",signature):
        raise ValueError("source REI scenario identity missing")
    expected = packet["candidate_initial_gas"]
    for name in ("x_HII","x_HeII","x_HeIII","Tgas_K","electron_fraction_xe_per_H"):
        if not math.isfinite(float(expected[name])):
            raise ValueError("nonfinite donor species or temperature")
    if not (expected["x_HeII"] == expected["x_HeIII"] == 0.
            and expected["electron_fraction_xe_per_H"] == expected["x_HII"]
            and 0 < expected["x_HII"] < 1 and expected["Tgas_K"] > 0):
        raise ValueError("neutral-helium conditional projection mismatch")
    params={}
    for line in config_text.splitlines():
        line=line.split("#",1)[0].strip()
        if not line:
            continue
        if line.count("=")!=1:
            raise ValueError("unexpected REI config syntax")
        key,value=map(str.strip,line.split("=",1))
        if not key or key in params or not value:
            raise ValueError("empty/duplicate REI config parameter")
        params[key]=value
    for key in ("initial_x_hii","initial_temperature_k","q_ref","end_zbar"):
        if key not in params:
            raise ValueError(f"missing REI cfg field {key}")
    x=float(params["initial_x_hii"])
    temperature=float(params["initial_temperature_k"])
    q=float(params["q_ref"])
    endpoint=float(params["end_zbar"])
    if not all(map(math.isfinite,(x,temperature,q,endpoint))):
        raise ValueError("invalid nonfinite REI cfg field")
    if (x != expected["x_HII"] or temperature != expected["Tgas_K"]):
        raise ValueError("REI config does not match source full-HyRec donor")
    if q != 0. or endpoint != 4.0:
        raise ValueError("this is q0 zbar20-to-4 REI donor check only")
    return {
        "schema":"rec.r3d.rei_cfg_read_only_gate.v1",
        "config_sha256":hashlib.sha256(config_text.encode("utf-8")).hexdigest(),
        "source_rei_scenario_sha256":signature,
        "source_donor_x_HII":x,
        "source_donor_Tgas_K":temperature,
        "scope":"Q0_CONDITIONAL_ZERO_IONIZING_PHOTONS_NOT_ADOPTED",
        "decision":"MATCHES_UNLAUNCHED_REI_CONFIG_NOT_NATIVE_REI_RESULT",
    }

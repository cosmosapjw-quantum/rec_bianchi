#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
metrics=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert metrics["status"]=='PASS_PR05C2C1B2B1D_PARENT_PROVENANCE_FIREWALL_BIANCHI_II_PROVIDER_PILOT_R3_OPEN'
firewall=metrics["parent_firewall"]
provider=metrics["background_provider"]
assert firewall["operator_verification_rejected"]
assert firewall["manufactured_rejected"]
assert firewall["byte_round_trip_exact"]
assert firewall["stale_history_index_rejected"]
assert not firewall["physical_source_derived_parent_constructed"]
assert provider["provider_pilot_passed"]
assert provider["state_absolute_error_max"]<1.0e-5
assert provider["constraint_residual_absmax"]<1.0e-11
assert provider["archive_hash_locked"]
assert provider["class_a_source_hash_locked"]
assert provider["type_ix_D_source_hash_locked"]
assert provider["Bianchi_IX_D_event_required"]
assert provider["exceptional_tilted_VI_minus_1_over_9_fail_closed"]
assert provider["unvalidated_family_fail_closed"]
assert not provider["all_11_family_production_support_claimed"]
assert len(list(csv.DictReader((ROOT/"PARENT_PROVENANCE_FIREWALL.csv").open())))==3
assert len(list(csv.DictReader((ROOT/"BIANCHI_II_PROVIDER_PILOT.csv").open())))==3
with np.load(ROOT/"pr05c2c1b2b1d_parent_provider_v072.npz") as data:
    assert data["provider_end_normalized_state"].shape==(3,)
    assert data["accepted_parent_payload"].dtype==np.uint8
manifest={}
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1); manifest[name]=digest
for name,digest in manifest.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(metrics["status"])

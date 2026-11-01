#!/usr/bin/env python3
"""Independent original REC#192 Decimal-output vs native-Rust source science parity.

Byte identity: original input TAR/NPZ/forcing, Rust produced science file on replay.
Scientific equivalence: fixed source binary64 vs Python Decimal.from_float sums.
Cancellation-sensitive endpoint differences use a physically relevant parent scale.
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

N=46080
RUST_HEAD="REC_ORIGINAL_F05_RUST_HHE_ACCEPTED_MATERIAL_V1"
ORACLE_SHA="9509bc02e9f4c45dc91ec66b997a829819125562c81d46d1d15594cd2902b545"
SOURCE_CSV_SHA="4ecf6d930a4f1d6ef5d8c6e8b3cde60ece4df906c8bc87a59be679b5fecb449f"
NPZ_SHA="7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d"
TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def close(a,b,rel=1e-13):
    return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=rel*max(abs(a),abs(b),1e-300)

def run(root,rust_dir,binary, report):
    root=Path(root).resolve()
    rust_dir=Path(rust_dir).resolve()
    old=root/"research/rec_rei_f05_accepted_history_thomson_20261101"
    source=root/"research/rec_rei_f05_native_thomson_medium_20261101/source_inputs"
    old_csv=old/"results/ORIGINAL_ACCEPTED_F05_THOMSON_CHANGE_46080.csv.gz"
    old_json=old/"results/SCIENCE_RESULT.json"
    rust_csv=rust_dir/"RUST_ACCEPTED_F05_MATERIAL_46080.csv"
    rust_json=rust_dir/"RUST_SCIENCE_RESULT.json"
    original_npz=source/"ORIGINAL_REI_F05_initial_material_state_z6.npz"
    original_tar=old/"source_inputs/ORIGINAL_REI_F05_FIRST_INTERVAL_ACCEPTED160.tar.gz"
    for p,expected in [(old_csv,SOURCE_CSV_SHA),(old_json,ORACLE_SHA),
                       (original_npz,NPZ_SHA),(original_tar,TAR_SHA)]:
        if sha(p)!=expected:
            raise ValueError("IMMUTABLE_ORIGINAL_SOURCE_OR_PYTHON_ORACLE_SHA_MISMATCH:"+str(p))
    old_meta=json.loads(old_json.read_text())
    new_meta=json.loads(rust_json.read_text())
    if new_meta["schema"]!=RUST_HEAD or new_meta["official_accepted_tick"]!=160 or new_meta["source_physical_cells"]!=N:
        raise ValueError("RUST_HHE_PHYSICAL_SOURCE_OWNER_OR_SCOPE_MISMATCH")
    pairs=[
        ("initial_global_electron_number","initial_total_electron"),
        ("initial_volume_mean_Thomson_rate_s_inv","initial_mean_Thomson_rate_s_inv"),
        ("initial_electron_clumping","initial_electron_clumping"),
    ]
    summary_errs={}
    for a,b in pairs:
        v=float(old_meta[a]);w=float(new_meta[b])
        if not close(v,w,1e-13):
            raise AssertionError("RUST_SCALAR_SOURCE_PARITY_FAILURE:"+a)
        summary_errs[a]=abs(w-v)/abs(v)
    interval_pairs=[
        ("accepted160_global_electron_number","accepted_lower_total_electron","accepted_upper_total_electron",1e-13),
        ("accepted160_volume_mean_Thomson_rate_s_inv","accepted_lower_mean_Thomson_rate_s_inv","accepted_upper_mean_Thomson_rate_s_inv",1e-13),
        ("accepted160_electron_clumping","accepted_lower_electron_clumping","accepted_upper_electron_clumping",1e-13),
        ("accepted_0_to_160_Delta_mean_Thomson_rate_s_inv","accepted_lower_delta_mean_Thomson_rate_s_inv","accepted_upper_delta_mean_Thomson_rate_s_inv",1e-10),
    ]
    for old_key,lo_key,hi_key,scale in interval_pairs:
        for observed,oracle in zip([new_meta[lo_key],new_meta[hi_key]],old_meta[old_key]):
            v=float(oracle);w=float(observed)
            if not close(v,w,scale):
                raise AssertionError("RUST_AGGREGATE_PARITY_FAILURE:"+old_key+":"+str(v)+":"+str(w))
            summary_errs[old_key]=max(summary_errs.get(old_key,0),abs(v-w)/abs(v))
    expected_signs=old_meta["source_native_electron_change_classes"]
    actual_signs=dict(definite_gain=new_meta["definite_gain_cells"],definite_loss=new_meta["definite_loss_cells"],sign_ambiguous=new_meta["ambiguous_cells"])
    if expected_signs!=actual_signs:
        raise AssertionError("RUST_ACTUAL_CELL_SIGN_COUNTS_MISMATCH")
    maximum_base_normalized=0.0
    maximum_large_field_relative=0.0
    near_zero_fields=set()
    count=0
    with gzip.open(old_csv,"rt",newline="") as a, rust_csv.open("r",newline="") as b:
        rec=csv.DictReader(a)
        native=csv.DictReader(b)
        if rec.fieldnames!=native.fieldnames:
            raise AssertionError("RUST_VS_SOURCE_PHYSICAL_FIELD_SCHEMA")
        for arow,brow in zip(rec,native):
            if arow["node"]!=brow["node"]!=str(count):
                raise AssertionError("RUST_SOURCE_NODE_ID_DRIFT:"+str(count))
            if arow["accepted_electron_change_sign_class"]!=brow["accepted_electron_change_sign_class"]:
                raise AssertionError("RUST_SOURCE_PER_NODE_SIGN_DRIFT:"+str(count))
            gamma0=float(arow["accepted_tick0_Thomson_rate_s_inv"])
            h0=float(arow["accepted_initial_H_electron_N"])
            he0=float(arow["accepted_initial_He_electron_N"])
            for field in rec.fieldnames[1:-1]:
                a0=float(arow[field]);b0=float(brow[field])
                if "DeltaThomson" in field:
                    # Endpoint rate differences can be tiny from cancellation.
                    base=max(abs(gamma0),abs(a0),abs(b0))
                    near_zero_fields.add(field)
                elif "DeltaH_electron" in field:
                    base=max(abs(h0),abs(a0),abs(b0))
                    near_zero_fields.add(field)
                elif "DeltaHe_electron" in field:
                    base=max(abs(he0),abs(a0),abs(b0))
                    near_zero_fields.add(field)
                else:
                    base=max(abs(a0),abs(b0))
                    if base>0:maximum_large_field_relative=max(maximum_large_field_relative,abs(a0-b0)/base)
                if not (math.isfinite(a0) and math.isfinite(b0)):
                    raise AssertionError("NONFINITE_RUST_SOURCE_ROW:"+field)
                if abs(a0-b0)>2e-13*max(base,1e-300):
                    raise AssertionError("RUST_VS_ORIGINAL_ROW_PHYSICS_MISMATCH row="+str(count)+" field="+field)
                maximum_base_normalized=max(maximum_base_normalized,abs(a0-b0)/max(base,1e-300))
            count+=1
        if count!=N:
            raise AssertionError("RUST_ORIGINAL_SOURCE_ROWS_NOT_46080")
    # Actively check the fail-closed immutable input SHA logic without changing original data.
    with tempfile.TemporaryDirectory(prefix="rust_f05_bad_source_") as d:
        p=Path(d)
        inp=p/"research/rec_rei_f05_native_thomson_medium_20261101/source_inputs"
        inp.mkdir(parents=True)
        bad=bytearray(original_npz.read_bytes())
        bad[0]^=0x01
        (inp/"ORIGINAL_REI_F05_initial_material_state_z6.npz").write_bytes(bad)
        (inp/"ORIGINAL_REI_F05_canonical_time_resolved_forcing_nodes.csv").symlink_to(
            source/"ORIGINAL_REI_F05_canonical_time_resolved_forcing_nodes.csv")
        other=p/"research/rec_rei_f05_accepted_history_thomson_20261101/source_inputs"
        other.mkdir(parents=True)
        (other/"ORIGINAL_REI_F05_FIRST_INTERVAL_ACCEPTED160.tar.gz").symlink_to(original_tar)
        failed=subprocess.run([str(binary),str(p),str(p/"should_not_exist")],text=True,capture_output=True)
        if failed.returncode==0 or "BYTE_SOURCE_SHA_DRIFT" not in failed.stderr:
            raise AssertionError("RUST_MUTATED_IMMUTABLE_INITIAL_SOURCE_NOT_REJECTED:"+failed.stderr[:400])
    result={
      "schema":"REC_RUST_F05_CROSS_LANGUAGE_SCIENTIFIC_PARITY_V1",
      "original_source_accepted_endpoints":"0_AND_160_ONLY",
      "original_source_rows_checked":count,
      "source_byte_identities":"PASS",
      "source_rust_cell_sign_mismatch":0,
      "parent_python_science_sha256":sha(old_json),
      "original_python_physical_csv_sha256":sha(old_csv),
      "rust_science_sha256":sha(rust_json),
      "rust_physical_csv_sha256":sha(rust_csv),
      "worst_relative_error_noncancellation_fields":format(maximum_large_field_relative,".17e"),
      "worst_source_scale_normalized_absolute_error":format(maximum_base_normalized,".17e"),
      "max_summary_relative_errors":{k:format(v,".17e") for k,v in sorted(summary_errs.items())},
      "cancellation_scaled_fields":sorted(near_zero_fields),
      "negative_original_npz_byte_tamper":"PASS_REJECTED",
      "science_status":"SOURCE_CONDITIONAL_NUMERICALLY_EQUIVALENT_NOT_BYTE_IDENTICAL_TO_DECIMAL",
      "reintegration_status":"RUST_SOURCE_PHYSICS_CONSUMER_NOT_ORIGINAL_REI_F05_SOLVER",
      "DAG_REI":"28/88_DELTA0","DAG_REC_H5":"0/313_DELTA0",
      "official_accepted_tick":"160/131072",
      "auto_next":False
    }
    report=Path(report)
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",required=True,type=Path)
    p.add_argument("--rust-output",required=True,type=Path)
    p.add_argument("--rust-binary",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    a=p.parse_args()
    run(a.repo,a.rust_output,a.rust_binary,a.report)

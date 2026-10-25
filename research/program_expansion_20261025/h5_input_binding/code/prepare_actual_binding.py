"""Read only the necessary immutable PB01/KS01 S2 members and bind H5 inputs.

The original computations are not replayed. The outer archive identity was
already checked by the current controller recovery; selected members are
checked against its manifest and the previously pinned input identities.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import io
import json
import resource
import time
from pathlib import Path
import zipfile

import numpy as np

from h5_bounds import evaluate_files, validate_context


OUTER_SHA = "b43ec958374bb8ba97073c46355dc26131a64261cd5004fa64e65c6565da00d1"
OUTER_BYTES = 69336495
KS_SHA = "3a67f3e1e40d39f8833bf9481e483593929ab9fc2c38451dae8e9ed4a7042301"
HISTORY_SHA = "d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1"
K_SHA = "b8fcc82b91514b4b86848a727af2a3fe2c6990a07bc38a2205e0cf887799f64e"
ADMISSION_SHA = "a92f5a906dab13ed126f6813ad827913c8007097b7457cbd4eaa9dee8673a3a1"
PB_BASE = "research/rec_history_pullback_20261025/"
KS_BASE = "research/rec_history_ks_20261025/"


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def identity(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def member(archive, name, manifest=None, expected=None):
    data = archive.read(name)
    actual = identity(data)
    if manifest is not None:
        row = manifest[name]
        if actual != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            raise ValueError("SELECTED_ARCHIVE_MEMBER_MISMATCH:" + name)
    if expected is not None and actual["sha256"] != expected:
        raise ValueError("PINNED_INPUT_BYTE_MISMATCH:" + name)
    return data, {"member": name, **actual}


def prepare(archive_path: Path, unit: Path, materialized: Path):
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    materialized.mkdir(parents=True, exist_ok=True)
    (unit / "results").mkdir(exist_ok=True)
    (unit / "evidence").mkdir(exist_ok=True)
    selected = {}
    if archive_path.stat().st_size != OUTER_BYTES:
        raise ValueError("OUTER_ARCHIVE_SIZE_MISMATCH")
    with zipfile.ZipFile(archive_path) as outer:
        manifest = {x["path"]: x for x in json.loads(outer.read("PAYLOAD_MANIFEST.json"))["files"]}
        chart_bytes, selected["native_chart"] = member(
            outer, PB_BASE + "results/primary001/NATIVE_CHART_CONSTANTS.npz", manifest)
        witness_bytes, selected["query_witnesses"] = member(
            outer, PB_BASE + "results/primary001/QUERY_WITNESSES.json", manifest)
        ks_bytes, selected["KS01_S2"] = member(
            outer, "delivery/recovery001/KS01_S2_RECOVERED.zip", manifest, KS_SHA)
    with zipfile.ZipFile(io.BytesIO(ks_bytes)) as ks:
        history_bytes, selected["original_history"] = member(
            ks, "inputs/pr05b2_source_history_v060.npz", expected=HISTORY_SHA)
        interval_bytes, selected["Ks_intervals"] = member(
            ks, KS_BASE + "results/primary001/CERTIFICATE_ARRAYS.npz", expected=K_SHA)
        admission_bytes, selected["accepted_queries"] = member(
            ks, KS_BASE + "results/primary001/HISTORY_ADMISSION.json", expected=ADMISSION_SHA)
        cert_bytes, selected["Ks_certificate"] = member(
            ks, KS_BASE + "results/primary001/CERTIFICATE.json",
            expected="d0ec7649d58a9556f2f9d08894cafc65bfc674cc336243155da5204ec5fa889c")
    del ks_bytes
    # Preserve selected actual bytes in the recovery directory, outside Git.
    raw = {"NATIVE_CHART_CONSTANTS.npz": chart_bytes,
           "QUERY_WITNESSES.json": witness_bytes,
           "pr05b2_source_history_v060.npz": history_bytes,
           "CERTIFICATE_ARRAYS.npz": interval_bytes,
           "HISTORY_ADMISSION.json": admission_bytes,
           "CERTIFICATE.json": cert_bytes}
    for name, content in raw.items():
        path = materialized / name
        if path.exists() and path.read_bytes() != content:
            raise ValueError("RECOVERY_TARGET_ALREADY_DIFFERS:" + name)
        if not path.exists():
            path.write_bytes(content)
    chart = np.load(io.BytesIO(chart_bytes), allow_pickle=False)
    history = np.load(io.BytesIO(history_bytes), allow_pickle=False)
    intervals = np.load(io.BytesIO(interval_bytes), allow_pickle=False)
    admitted, witnesses = json.loads(admission_bytes), json.loads(witness_bytes)
    certificate = json.loads(cert_bytes)
    eta = history["eta"]
    history_values = np.vstack((history["outgoing_virtual"], history["outgoing_lyman"]))
    q, source, alpha = chart["query"], chart["source"], chart["alpha"]
    slots = chart["active_slots"]
    if len(q) != 313 or slots.shape != (626, 2) or len(set(map(tuple, slots))) != 626:
        raise ValueError("ACTUAL_SUPPORT_SHAPE")
    if not np.array_equal(np.sort(source), np.arange(1, 314)):
        raise ValueError("ACTUAL_SOURCE_PERMUTATION")
    klo, khi = intervals["Klo"], intervals["Khi"]
    if klo.shape != (314, 313) or khi.shape != klo.shape:
        raise ValueError("KS_INTERVAL_SHAPE")
    if not np.all(np.isfinite(klo)) or not np.all(np.isfinite(khi)) or np.any(klo > khi):
        raise ValueError("KS_INTERVAL_ORDER")
    if len(admitted["records"]) != 313 or len(witnesses) != 313:
        raise ValueError("ACTUAL_QUERY_WITNESS_COUNT")
    if admitted["payload"] != {"bytes": 35239470, "sha256": HISTORY_SHA}:
        raise ValueError("ACTUAL_HISTORY_BINDING")
    rows = []
    repr_fractions = []
    widths = []
    for j, (witness, record) in enumerate(zip(witnesses, admitted["records"])):
        k, s = record["cell"], int(source[j])
        if (witness["incoming_index"], witness["source_index"], witness["cell"]) != (j, s, k):
            raise ValueError("PB01_QUERY_CELL_OWNER")
        if (record["incoming_index"], record["source_index"]) != (j, s):
            raise ValueError("KS01_QUERY_OWNER")
        if not np.array_equal(slots[2*j:2*j+2], [(s, k), (s, k+1)]):
            raise ValueError("ACTUAL_ENDPOINT_SLOTS")
        if k + 1 >= 5127 or q[j] != record["eta_emit"]:
            raise ValueError("ACTUAL_QUERY_PREFIX_OR_CLOCK")
        yl, yr = chart["left"][j], chart["right"][j]
        if yl != history_values[s, k] or yr != history_values[s, k+1]:
            raise ValueError("ACTUAL_ENDPOINT_BYTES")
        if float(alpha[j]) != witness["native_fraction"]:
            raise ValueError("ACTUAL_NATIVE_FRACTION")
        nominal = chart["stored_incoming"][j]
        if nominal != record["stored"] or nominal != witness["stored_base"]:
            raise ValueError("ACTUAL_NOMINAL_INPUT")
        l, r, query = map(lambda x: F(float(x)), (eta[k], eta[k+1], q[j]))
        a = (query - l) / (r - l)
        if not 0 < a < 1:
            raise ValueError("ACTUAL_QUERY_GEOMETRIC_INTERIOR")
        anchor = abs(F(float(nominal)) - ((1-a)*F(float(yl)) + a*F(float(yr))))
        rows.append({"incoming_index": j, "source_index": s, "cell": k,
                     "eta_left_hex": float(eta[k]).hex(),
                     "eta_right_hex": float(eta[k+1]).hex(),
                     "query_hex": float(q[j]).hex(),
                     "sample_left_hex": float(yl).hex(),
                     "sample_right_hex": float(yr).hex(),
                     "nominal_incoming_hex": float(nominal).hex(),
                     "native_alpha_hex": float(alpha[j]).hex(),
                     "geometric_alpha_exact": str(a),
                     "anchor_representation_radius_exact": str(anchor),
                     "pointwise_curvature_coefficient_exact": str((query-l)*(r-query)/2)})
        repr_fractions.append(anchor)
        widths.append(r-l)
    context = {
        "schema": "REC_H5_FIXED_QUERY_CONTEXT_V1",
        "source_identity": {
            "repository": "cosmosapjw-quantum/rec_bianchi",
            "PB01_final_commit": "ea89c97abeb7a663a813f00e9aadddaf0b32a6a9",
            "KS01_final_commit": "f9edbfe7b56ad002f1b7fb35d4c5aec4970682a4",
            "history_sha256": HISTORY_SHA, "history_bytes": 35239470,
            "z_hex": float(1099.9986525171403).hex(),
            "T0_K_hex": float(2.728).hex(),
            "nH0_m3_hex": float(0.18745798773143102).hex(),
            "fsR": 1, "meR": 1, "prefix": 5127,
            "query_count": 313, "active_endpoint_slots": 626,
            "Ks_intervals_sha256": K_SHA},
        "clock": "eta=ln(a)",
        "native_reference": "original_HyRec_native_Wien_departure_fixed_source_T0",
        "history_channel_unit": "dimensionless_occupation_departure",
        "eta_prefix_domain_hex": [float(eta[0]).hex(), float(eta[5126]).hex()],
        "fixed_query_scope": "Source-represented binary64 coordinates; physical retiming uncertainty is H6/H7/PB01, not inferred here",
        "represented_anchor_definition": "abs(stored_nominal - exact_geometric_linear_interpolation_of_stored_endpoints)",
        "operator": {"shape": [314, 313], "intervals_identity": selected["Ks_intervals"],
                     "certificate_identity": selected["Ks_certificate"],
                     "norm_upper_reused": certificate["norm_upper"],
                     "inverse_defect_rho_reused": certificate["rho"],
                     "rho_semantics": "matrix inverse residual; not ODE defect or physical tube radius",
                     "evaluation_this_unit": "entrywise interval bytes/shape/order read; no certificate rebuild or matvec"},
        "queries": rows}
    validate_context(context)
    context_path = unit / "inputs" / "SOURCE_CONTEXT.json"
    dump(context_path, context)
    packet = {
        "schema": "REC_H5_BOUND_INPUT_PACKET_V1",
        "source_identity": context["source_identity"],
        "context_sha256": hashlib.sha256(context_path.read_bytes()).hexdigest(),
        "clock": "eta=ln(a)", "native_reference": context["native_reference"],
        "query_policy": "fixed_represented_binary64_queries",
        "enclosure_kind": "continuous_source_ode_tube",
        "state_enclosure": None, "query_bounds": None, "proof_artifacts": [],
        "physical_epsilon": None,
        "input_status": "ACTUAL_313_QUERY_ENDPOINT_OPERATOR_BINDING_COMPLETE_PHYSICAL_BOUNDS_MISSING",
        "required_producer_artifacts": {
            "F_and_G": "Original-source continuous reconstruction, exact state/norm definitions, native departure G and same-clock derivative mapping",
            "state_bounds": "Initial error e0; whole-domain defect d, model discrepancy b, stability L and uniform open tube radius rho with bootstrap/existence proof",
            "history_bounds": "For all 313 bound cells: K_left/right, reference and endpoint representation radii, ess-sup whole-cell M2 and regularity evidence",
            "observable": "Owner error allocation and nonlinear/source remainder; separate from candidate arithmetic"}}
    packet_path = unit / "inputs" / "ACTUAL_BOUND_INPUTS.json"
    dump(packet_path, packet)
    consumed = evaluate_files(context_path, packet_path)
    dump(unit / "results" / "ACTUAL_BOUND_CONSUMPTION.json", consumed)
    summary = {
        "status": "PASS_ACTUAL_SOURCE_QUERY_ENDPOINT_OPERATOR_BINDING",
        "source_history_recovered": selected["original_history"],
        "actual_queries": 313, "actual_distinct_endpoint_slots": 626,
        "actual_query_bound_input_coverage": 0,
        "Ks_interval_shape": [314, 313],
        "anchor_representation_radius_max_exact": str(max(repr_fractions)),
        "anchor_representation_radius_max_float_for_display": float(max(repr_fractions)),
        "anchor_representation_nonzero_queries": sum(x != 0 for x in repr_fractions),
        "eta_cell_width_min_exact": str(min(widths)),
        "eta_cell_width_max_exact": str(max(widths)),
        "physical_epsilon": None, "physical_H5_status": "INPUT_DEPENDENT_UNCALIBRATED",
        "new_rhs": 0, "new_ivp": 0, "new_native": 0,
        "old_matrix_rebuild": 0, "old_campaign_replay": 0,
        "source_context_sha256": packet["context_sha256"],
        "conditional_theory": "PASS_DERIVED_SCOPED reused; representation anchor added explicitly"}
    dump(unit / "results" / "SOURCE_BINDING_SUMMARY.json", summary)
    receipt = {
        "outer_archive": {"path": str(archive_path), "bytes": OUTER_BYTES,
                          "sha256": OUTER_SHA,
                          "whole_sha_status": "REUSED_CURRENT_ROOT_DOWNLOAD_VERIFICATION"},
        "selected_members": selected,
        "materialized_directory": str(materialized),
        "readback_status": "Selected necessary members hash-checked, no full archive member replay",
        "io_and_binding_inclusive_cpu_seconds": time.process_time() - start_cpu,
        "io_and_binding_inclusive_wall_seconds": time.perf_counter() - start_wall,
        "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "source_relocation_only": True,
        "scientific_replay_count": 0}
    dump(unit / "evidence" / "SELECTIVE_RECOVERY_AND_BINDING.json", receipt)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--materialized", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.archive, args.unit, args.materialized)

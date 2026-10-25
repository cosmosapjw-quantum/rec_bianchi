"""Only H5-R3: distinguish a safe-tube radius lower bound from an upper bound.

The manufactured certificate is an interface control, never an actual H5 proof.
Each invocation is capped by the pre-existing finding-closure freeze.
"""
from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import sys
import tempfile
import time

REVIEW = Path(__file__).resolve().parent
EVIDENCE = REVIEW / "evidence/h5_tube_radius"


def main() -> None:
    mode = sys.argv[1]
    if mode not in ("before", "after"):
        raise ValueError("mode must be before or after")
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
    signal.alarm(30)
    started = time.perf_counter()
    code = (EVIDENCE / "h5_bounds_before.py" if mode == "before" else
            REVIEW.parent / "h5_input_binding/code/h5_bounds.py")
    digest = hashlib.sha256(code.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location("h5_tube_direction_control", code)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def upper(value):
        return {"upper": str(value), "proof_refs": ["manufactured"]}

    def lower(value):
        return {"lower": str(value), "proof_refs": ["manufactured"]}

    context = {
        "schema": "REC_H5_FIXED_QUERY_CONTEXT_V1",
        "source_identity": {"query_count": 1, "active_endpoint_slots": 2,
                            "prefix": 2, "history_sha256": "MANUFACTURED_ONLY"},
        "native_reference": "MANUFACTURED_G=x",
        "queries": [{"incoming_index": 0, "source_index": 1, "cell": 0,
                     "eta_left_hex": (0.0).hex(), "eta_right_hex": (1.0).hex(),
                     "query_hex": (0.5).hex(), "sample_left_hex": (0.0).hex(),
                     "sample_right_hex": (0.0).hex(),
                     "nominal_incoming_hex": (0.0).hex(),
                     "geometric_alpha_exact": "1/2",
                     "anchor_representation_radius_exact": "0"}],
    }
    controls = []
    with tempfile.TemporaryDirectory(prefix="rec_h5_radius_review_") as tmp:
        proof_root = Path(tmp)
        proof = proof_root / "manufactured_only.txt"
        proof.write_text("MANUFACTURED INTERFACE CONTROL ONLY: x'=0, reconstruction=0, "
                         "initial error=1/2, d=L=0, G=x, K=1, M2=0. "
                         "No actual H5 physical approval.\n")
        packet = {
            "schema": "REC_H5_BOUND_INPUT_PACKET_V1",
            "source_identity": copy.deepcopy(context["source_identity"]),
            "clock": "eta=ln(a)", "native_reference": context["native_reference"],
            "query_policy": "fixed_represented_binary64_queries",
            "enclosure_kind": "continuous_source_ode_tube",
            "proof_artifacts": [{"id": "manufactured", "path": proof.name,
                                 "sha256": hashlib.sha256(proof.read_bytes()).hexdigest()}],
            "state_enclosure": {
                "norm": {"kind": "fixed_weighted_infinity", "coordinates": [
                    {"name": "x", "unit": "1", "scale": "1"}]},
                "reconstruction": "continuous_piecewise_absolutely_continuous",
                "bound_support": "whole_eta_domain_ess_sup",
                "tube_definition": "uniform_open_scaled_radius_about_reconstruction",
                "state_proof_refs": ["manufactured"],
                "orientation": 1, "eta_origin": "0", "eta_domain": ["0", "1"],
                "initial_error": upper("1/2"), "defect": upper(0),
                "stability_L": upper(0), "tube_radius": upper(1),
                "model_discrepancy": upper(0)},
            "query_bounds": [{"incoming_index": 0, "source_index": 1, "cell": 0,
                              "curvature_support": "ess_sup_whole_cell",
                              "regularity": "C2", "K_left": upper(1),
                              "K_right": upper(1), "reference_left": upper(0),
                              "reference_right": upper(0),
                              "endpoint_representation_left": upper(0),
                              "endpoint_representation_right": upper(0),
                              "curvature_M2": upper(0)}],
        }

        def evaluate(radius):
            p = copy.deepcopy(packet)
            p["state_enclosure"]["tube_radius"] = radius
            return module.evaluate_candidate(context, p, proof_root=proof_root)

        def rejected(name, radius):
            try:
                evaluate(radius)
            except module.BoundInputError as error:
                controls.append({"name": name, "status": "PASS_REFUSAL",
                                 "reason": str(error)})
            else:
                raise AssertionError(name + " was incorrectly accepted")

        if mode == "before":
            result = evaluate(upper(1))
            assert result["status"] == "CONDITIONAL_BOUND_CANDIDATE_REVIEW_REQUIRED"
            assert Fraction(result["state_error_upper_max"]) == Fraction(1, 2)
            assert Fraction(result["tube_margin_lower"]) == Fraction(1, 2)
            assert result["physical_epsilon"] is None
            controls.append({"name": "upper_only_radius_incorrectly_accepted",
                             "status": "ORIGINAL_FINDING_REPRODUCED",
                             "state_error_upper": "1/2", "radius_upper": "1",
                             "reported_tube_margin_lower": result["tube_margin_lower"],
                             "counterexample_certified_safe_radius": "1/10",
                             "physical_epsilon": None})
        else:
            rejected("upper_only_cannot_certify_safe_radius", upper(1))
            rejected("strict_equality_not_inside_open_tube", lower("1/2"))
            rejected("smaller_safe_radius_not_rescued_by_an_upper", {
                "lower": "1/4", "upper": "1", "proof_refs": ["manufactured"]})
            rejected("zero_safe_radius_refused", lower(0))
            rejected("unreferenced_safe_radius_refused", {"lower": "3/4", "proof_refs": []})
            result = evaluate(lower("3/4"))
            assert result["status"] == "CONDITIONAL_BOUND_CANDIDATE_REVIEW_REQUIRED"
            assert Fraction(result["state_error_upper_max"]) == Fraction(1, 2)
            assert Fraction(result["tube_margin_lower"]) == Fraction(1, 4)
            assert result["physical_epsilon"] is None
            assert result["physical_outgoing_bound"] is None
            controls.append({"name": "certified_lower_radius_strictly_contains_error",
                             "status": "PASS_CONDITIONAL_ONLY", "radius_lower": "3/4",
                             "state_error_upper": "1/2", "tube_margin_lower": "1/4",
                             "physical_epsilon": None, "physical_outgoing_bound": None})

    elapsed = time.perf_counter() - started
    usage = resource.getrusage(resource.RUSAGE_SELF)
    report = {
        "schema": "REC_H5_TUBE_RADIUS_INDEPENDENT_CONTROL_V1",
        "finding": "H5-R3", "mode": mode,
        "status": "REPRODUCED_ORIGINAL_P1" if mode == "before" else "PASS_BOUNDED_CLOSURE",
        "code_sha256": digest, "controls": controls,
        "process_cpu_seconds": usage.ru_utime + usage.ru_stime,
        "inner_wall_seconds": elapsed, "maximum_RSS_KiB": usage.ru_maxrss,
        "cpu_cap_seconds": 5, "wall_cap_seconds": 30,
        "address_space_cap_bytes": 1 << 30, "threads": 1,
        "new_IVP": 0, "new_RHS": 0, "full_suite_replays": 0,
    }
    output = EVIDENCE / ("ORIGINAL_REPRODUCTION.json" if mode == "before" else "CLOSURE.json")
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

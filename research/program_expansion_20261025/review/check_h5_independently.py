"""Independent raw-query binding readback and conditional-bound controls.

Only selected stored source values and small exact algebra are evaluated.
No forward solve, RHS, old matrix regeneration or physical bound is executed.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("unit", type=Path)
    parser.add_argument("selected_raw", type=Path)
    parser.add_argument("hd_module", type=Path)
    parser.add_argument("hd_source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    start = time.perf_counter()
    import numpy as np
    module_path = args.unit/"code/h5_bounds.py"
    h5 = load(module_path, "reviewed_h5")
    context_path = args.unit/"inputs/SOURCE_CONTEXT.json"
    packet_path = args.unit/"inputs/ACTUAL_BOUND_INPUTS.json"
    context = json.loads(context_path.read_bytes())
    packet = json.loads(packet_path.read_bytes())
    actual = h5.evaluate_files(context_path, packet_path)
    assert actual["physical_epsilon"] is None
    assert actual["conditional_epsilon"] is None
    assert actual["physical_outgoing_bound"] is None
    assert actual["status"] == "BLOCKED_ACTUAL_BOUND_INPUTS"
    assert actual["actual_query_count"] == 313
    assert actual["bound_input_query_coverage"] == 0
    assert packet["state_enclosure"] is None and packet["query_bounds"] is None
    assert packet["proof_artifacts"] == []
    raw_path = args.selected_raw/"pr05b2_source_history_v060.npz"
    digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    assert digest == "d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1"
    assert raw_path.stat().st_size == 35239470
    history = np.load(raw_path, allow_pickle=False)
    eta = history["eta"]
    virtual, lyman = history["outgoing_virtual"], history["outgoing_lyman"]
    chart = np.load(args.selected_raw/"NATIVE_CHART_CONSTANTS.npz", allow_pickle=False)
    intervals_path = args.selected_raw/"CERTIFICATE_ARRAYS.npz"
    assert hashlib.sha256(intervals_path.read_bytes()).hexdigest() == context["source_identity"]["Ks_intervals_sha256"]
    intervals = np.load(intervals_path, allow_pickle=False)
    assert intervals["Klo"].shape == (314, 313) == intervals["Khi"].shape
    assert np.all(intervals["Klo"] <= intervals["Khi"])
    rows = context["queries"]
    worst = max(range(len(rows)), key=lambda i: F(rows[i]["anchor_representation_radius_exact"]))
    selected = sorted(set((0, 156, 312, worst)))
    readback = []
    for i in selected:
        row = rows[i]
        cell, channel = row["cell"], row["source_index"]
        storage = virtual if channel < virtual.shape[0] else lyman
        storage_channel = channel if storage is virtual else channel-virtual.shape[0]
        left, right = float(eta[cell]), float(eta[cell+1])
        query = float(chart["query"][i])
        yl, yr = float(storage[storage_channel, cell]), float(storage[storage_channel, cell+1])
        nominal = float(chart["stored_incoming"][i])
        expected_hex = {"eta_left_hex": left.hex(), "eta_right_hex": right.hex(),
                        "query_hex": query.hex(), "sample_left_hex": yl.hex(),
                        "sample_right_hex": yr.hex(), "nominal_incoming_hex": nominal.hex()}
        assert all(row[key] == value for key, value in expected_hex.items())
        a = (F(query)-F(left))/(F(right)-F(left))
        represented = abs(F(nominal)-((1-a)*F(yl)+a*F(yr)))
        assert represented == F(row["anchor_representation_radius_exact"])
        assert F(row["pointwise_curvature_coefficient_exact"]) == (F(query)-F(left))*(F(right)-F(query))/2
        readback.append({"incoming_index": i, "source_index": channel, "cell": cell,
                         "actual_source_hex_fields_match": True,
                         "exact_representation_radius": str(represented)})
    # Sharp interpolation case and degenerate exponent limit are exact controls.
    assert h5.interpolation_upper("0", "1/2", "1", "0", "0", "2") == F(1, 4)
    assert h5.interpolation_upper("0", "0", "1", "1/7", "9", "2") == F(1, 7)
    assert h5.gronwall_upper("1/7", "3/11", "0", "2/3") == F(1, 7)+F(3, 11)*F(2, 3)
    exponential_controls = []
    for x in (F(0), F(1, 10**20), F(1), F(37, 3), F(127, 2), F(64)):
        upper = h5.exp_upper(x)
        upper_token = h5.decimal_bound_token(upper, upper=True)
        lower_token = h5.decimal_bound_token(upper, upper=False)
        assert F(lower_token) <= upper <= F(upper_token)
        assert len(upper_token) < 100
        json.dumps({"bound": upper_token}, allow_nan=False)
        with localcontext() as dc:
            dc.prec = 90
            expected = (Decimal(x.numerator)/Decimal(x.denominator)).exp()
            observed = Decimal(upper.numerator)/Decimal(upper.denominator)
            assert observed >= expected or abs(observed-expected) <= Decimal("1e-85")*max(1, expected)
        exponential_controls.append({"x": str(x), "bound_positive": upper >= 1,
                                     "outward_serialization_containment": "PASS_EXACT",
                                     "upper_decimal_token": upper_token,
                                     "numeric_comparison_to_Decimal90": "PASS"})
    # This closure checks only the changed HD Decimal-context dependency.
    hd = load(args.hd_module, "reviewed_hd_final")
    data = hd.load_hd(args.hd_source)
    selected_rates = ((2, 1, 2, 100), (3, 1, 3, 50), (3, 8, 9, 50))
    with localcontext() as dc:
        dc.prec = 80
        high = [data.upward_rate(*parameters) for parameters in selected_rates]
    with localcontext() as dc:
        dc.prec = 4
        low = [data.upward_rate(*parameters) for parameters in selected_rates]
    assert high == low
    for line in range(2, 9):
        try:
            hd.require_energy_frequency_bridge(data, line)
        except hd.UnsupportedDomain:
            pass
        else:
            raise AssertionError("source-inconsistent line was admitted to the energy bridge")
    assert hd.require_energy_frequency_bridge(data, 1).id == 1
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result = {"schema": "REC_H5_INDEPENDENT_CHECK_V1", "status": "PASS_SCOPED_IMPLEMENTATION_AND_ACTUAL_BINDING",
              "reviewed_h5_code_sha256": hashlib.sha256(module_path.read_bytes()).hexdigest(),
              "reviewed_HD_final_code_sha256": hashlib.sha256(args.hd_module.read_bytes()).hexdigest(),
              "source_context_sha256": hashlib.sha256(context_path.read_bytes()).hexdigest(),
              "original_history_sha256": digest,
              "selected_original_source_readbacks": readback,
              "actual_bound_input_coverage": "0/313",
              "physical_epsilon": None, "physical_outgoing_bound": None,
              "sharp_quadratic_and_endpoint_controls": "PASS_EXACT",
              "zero_L_Gronwall_control": "PASS_EXACT", "exponential_controls": exponential_controls,
              "exp_upper_theory_scope": "Positive Taylor sum plus geometric remainder; implementation comparisons do not replace that proof",
              "HD_context_repair_closure": {"precision_4_equals_80": True,
                    "selected_parameters": selected_rates, "actual_rates": high,
                    "energy_bridge_pass_line": 1, "energy_bridge_refused_lines": list(range(2, 9))},
              "new_RHS": 0, "new_IVP": 0, "old_matrix_rebuild": 0,
              "command_argv": sys.argv,
              "resource": {"process_cpu_seconds": usage.ru_utime+usage.ru_stime,
                           "execution_wall_seconds": time.perf_counter()-start,
                           "max_RSS_KiB": usage.ru_maxrss}}
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "source_readback_indices": selected,
                      "resource": result["resource"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

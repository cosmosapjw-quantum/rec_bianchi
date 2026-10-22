"""Independent raw-profile -> CSV/summary -> plot-data binding for C2.

The final PNG appearance is reviewed separately by actual image viewing.
This script performs no profiling, scientific-driver import, or integration.
"""
from __future__ import annotations
import os
for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[k] = "1"
import time
START = time.perf_counter()
import csv
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import numpy as np

OUT = Path(__file__).resolve().parent
UNIT = OUT.parents[1]
BASE = UNIT / "evidence/profile/attempt_001"
HASHES = {}


def sha(path):
    path = Path(path)
    value = hashlib.sha256(path.read_bytes()).hexdigest()
    HASHES[str(path.relative_to(UNIT))] = value
    return value


def read(path):
    sha(path)
    return json.loads(path.read_text())


def close(a, b):
    assert math.isclose(a, b, rel_tol=3e-14, abs_tol=1e-14), (a, b)


def key(row):
    return row["file"], row["line"], row["name"]


summary = read(UNIT / "results/SUMMARY.json")
for entry in summary["evidence"]:
    assert sha(UNIT / entry["path"]) == entry["sha256"]
with np.load(UNIT / "figures/v2/PLOT_DATA.npz", allow_pickle=False) as p:
    plot = {name: p[name].copy() for name in p.files}
aggregate = defaultdict(lambda: defaultdict(float))
total_self = 0.0
all_unnested = True
for j, label in enumerate(plot["case_labels"]):
    result = read(BASE / label / "RESULT.json")
    item = summary["baseline_latency"][j]
    assert item["label"] == label
    for phase in ("gather", "collision"):
        latency = np.array([row[phase]["wall_seconds"] * 1000 / 64 for row in result["unprofiled_repeats"]])
        assert latency.tobytes() == plot["baseline_" + phase + "_ms"][j].tobytes()
        assert latency.tolist() == item[phase + "_ms_per_state"]
        assert float(np.median(latency)) == item[phase + "_median_ms_per_state"]
        profile = read(BASE / label / ("GATHER_PROFILE.json" if phase == "gather" else "COLLISION_PROFILE.json"))
        for row in profile["functions"]:
            for field in ("total_calls", "primitive_calls", "self_seconds", "cumulative_seconds"):
                aggregate[(phase, *key(row))][field] += row[field]
        if phase == "gather":
            total_self += profile["profiler_total_self_seconds"]
            targets = [key(next(row for row in profile["functions"] if row["file"].endswith(suffix) and row["name"] == name)) for suffix, name in (("thermal_sources.py", "evaluate"), ("code/geometry.py", "fields"), ("atomic_network.py", "evaluate"))]
            children = defaultdict(set)
            for edge in profile["caller_edges"]:
                children[key(edge["caller"])].add(key(edge["callee"]))
            for target in targets:
                pending, seen = list(children[target]), set()
                while pending:
                    node = pending.pop()
                    if node in seen:
                        continue
                    seen.add(node)
                    pending.extend(children[node] - seen)
                assert not (set(targets) - {target}) & seen, (label, target)
close(total_self, summary["profiled_gather_total_self_seconds"])
targets = (("thermal_sources.py", "evaluate"), ("code/geometry.py", "fields"), ("atomic_network.py", "evaluate"))
computed = []
for suffix, name in targets:
    rows = [v for (phase, file, line, function), v in aggregate.items() if phase == "gather" and file.endswith(suffix) and function == name]
    assert len(rows) == 1
    computed.append(rows[0]["cumulative_seconds"])
computed.append(total_self - sum(computed))
for i, value in enumerate(computed):
    close(value, summary["disjoint_subtrees"][i]["cumulative_seconds"])
    close(100 * value / total_self, plot["cost_percent"][i])
    close(100 * value / total_self, summary["disjoint_subtrees"][i]["percent"])
assert plot["cost_labels"].tolist() == [g["group"] for g in summary["disjoint_subtrees"]]
csv_path = UNIT / "results/FUNCTION_PROFILE.csv"
sha(csv_path)
with csv_path.open() as f:
    csv_rows = list(csv.DictReader(f))
assert len(csv_rows) == len(aggregate)
for row in csv_rows:
    expected = aggregate[(row["phase"], row["file"], int(row["line"]), row["name"])]
    for name in ("total_calls", "primitive_calls", "self_seconds", "cumulative_seconds"):
        close(float(row[name]), expected[name])
    close(float(row["calls_per_saved_state"]), expected["total_calls"] / 512)
probe_start = read(UNIT / "evidence/timing_order_probe/STARTED.json")
probe_result = read(UNIT / "evidence/timing_order_probe/RESULT.json")
probe_finish = read(UNIT / "evidence/timing_order_probe/FINISHED.json")
for k in ("script", "profile_harness", "baseline_receipt"):
    p = UNIT.parents[1] / probe_start[k]["path"]
    assert sha(p) == probe_start[k]["sha256"]
assert [row["resolution"] for row in probe_result["measured"]] == probe_start["schedule"] == ["refined", "nominal", "nominal", "refined", "refined", "nominal"]
assert probe_result["status"] == probe_finish["status"] == "PASS_TARGETED_ORDER_PROBE"
assert all(row["gather_exact"] and row["collision_exact"] for row in probe_result["measured"])
assert probe_result["new_IVPs"] == 0 and probe_result["IVP_attempts"] == []
probe_ranges = {}
for resolution in ("nominal", "refined"):
    values = [row["gather"]["wall_seconds"] * 1000 / 64 for row in probe_result["measured"] if row["resolution"] == resolution]
    probe_ranges[resolution] = [min(values), max(values)]
for directory in (UNIT / "figures", UNIT / "figures/v2"):
    manifest = read(directory / "FIGURE_MANIFEST.json")
    for row in manifest["files"]:
        p = directory / row["filename"]
        assert p.stat().st_size == row["bytes"] and sha(p) == row["sha256"]
v1 = read(UNIT / "figures/FIGURE_MANIFEST.json")
v2 = read(UNIT / "figures/v2/FIGURE_MANIFEST.json")
assert v1["input_summary_sha256"] == sha(UNIT / "results/SUMMARY.json")
assert v1["plot_script_sha256"] == sha(UNIT / "code/summarize_profile.py")
assert v2["repair_script_sha256"] == sha(UNIT / "code/render_latency_v2.py")
assert v2["predecessor_manifest_sha256"] == sha(UNIT / "figures/FIGURE_MANIFEST.json")
for name in ("PLOT_DATA.npz", "baseline_cost_attribution.png", "baseline_cost_attribution.pdf"):
    assert sha(UNIT / "figures" / name) == sha(UNIT / "figures/v2" / name)
for name in ("C2_SCOPE.md", "FORMULA_CODE_MAP_KO.md", "REPORT_KO.md", "NEXT_STAGE_C3.md", "FIGURE_CAPTIONS_KO.md", "code/profile_saved_diagnostics.py", "code/probe_timing_variation.py"):
    sha(UNIT / name)
elapsed = time.perf_counter() - START
record = dict(status="PASS_INDEPENDENT_FINAL_ARTIFACT_BINDING", command=[sys.executable, str(Path(__file__).relative_to(UNIT.parents[1]))],
              active_wall_seconds=elapsed, profiled_diagnostic_total_self_seconds=total_self,
              disjoint_cumulative_seconds=computed, disjoint_percent=plot["cost_percent"].tolist(),
              caller_graph_targets_pairwise_non_nested=True, aggregate_function_rows_checked=len(csv_rows),
              latency_values_reconstructed=48, order_probe_ranges_ms_per_state=probe_ranges,
              v1_v2_plot_data_byte_identity=True, files_checked_sha256=HASHES,
              final_png_visual_check="Actual viewing completed separately; see REVIEW_KO.md and REVIEW.json",
              new_IVPs=0, old_IVP_reruns=0, candidate_speedup_verified=False)
with (OUT / "FINAL_ARTIFACT_CHECK.json").open("x") as stream:
    json.dump(record, stream, indent=2, sort_keys=True); stream.write("\n")
print(f"ARTIFACT_CHECK_PASS latency_values=48 aggregate_rows={len(csv_rows)} caller_subtrees_non_nested=True v1_v2_plot_data_byte_equal=True")
print("PROFILE_COST_PASS total_self=" + str(total_self) + " percentages=" + json.dumps(plot["cost_percent"].tolist()))
print("PROBE_RANGES_MS_PER_STATE " + json.dumps(probe_ranges, sort_keys=True))
print(f"FINAL_ARTIFACT_CHECK_PASS active_wall_seconds={elapsed:.9f} IVPs=0")

"""Aggregate immutable C2 measurements and render source-bound figures."""
from __future__ import annotations

import os
for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"
import csv
import hashlib
import json
from pathlib import Path
import statistics
import time
START = time.perf_counter()
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

UNIT = Path(__file__).resolve().parents[1]
ROOT = UNIT/"evidence/profile/attempt_001"
RESULTS = UNIT/"results"
FIGURES = UNIT/"figures"


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def save_csv(path, rows):
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    RESULTS.mkdir(exist_ok=False)
    FIGURES.mkdir(exist_ok=False)
    base = read(ROOT/"SUMMARY.json")
    if base["status"] != "PASS_C2_BASELINE_PROFILE":
        raise ValueError("BASELINE_NOT_PASSED")
    states = base["states_total"]
    timings, latency, functions, evidence = [], [], {}, []
    profiles = {"gather": [], "collision": []}
    for case in base["case_results"]:
        label = case["label"]
        result = read(ROOT/label/"RESULT.json")
        evidence.append(ROOT/label/"RESULT.json")
        r = dict(label=label)
        for phase in profiles:
            values = []
            for repeat in result["unprofiled_repeats"]:
                timing = repeat[phase]
                values.append(timing["wall_seconds"]*1000/64)
                timings.append(dict(case=label, repeat=repeat["repeat"], phase=phase, states=64,
                                    wall_seconds=timing["wall_seconds"], cpu_seconds=timing["cpu_seconds"],
                                    wall_ms_per_state=timing["wall_seconds"]*1000/64))
            r[phase+"_ms_per_state"] = values
            r[phase+"_median_ms_per_state"] = statistics.median(values)
            pp = ROOT/label/("GATHER_PROFILE.json" if phase == "gather" else "COLLISION_PROFILE.json")
            prof = read(pp)
            evidence.append(pp)
            profiles[phase].append(prof)
            for row in prof["functions"]:
                key = (phase, row["file"], row["line"], row["name"])
                target = functions.setdefault(key, dict(phase=phase, file=row["file"], line=row["line"], name=row["name"],
                            total_calls=0, primitive_calls=0, self_seconds=0.0, cumulative_seconds=0.0))
                for column in ("total_calls", "primitive_calls", "self_seconds", "cumulative_seconds"):
                    target[column] += row[column]
        latency.append(r)
    function_rows = sorted(functions.values(), key=lambda row: (row["phase"], -row["self_seconds"]))
    for row in function_rows:
        row["calls_per_saved_state"] = row["total_calls"]/states
    save_csv(RESULTS/"FUNCTION_PROFILE.csv", function_rows)
    save_csv(RESULTS/"BASELINE_TIMINGS.csv", timings)
    def find(phase, suffix, name):
        candidates = [r for r in function_rows if r["phase"] == phase and r["file"].endswith(suffix) and r["name"] == name]
        if len(candidates) != 1:
            raise ValueError("AMBIGUOUS_PROFILE_FUNCTION:"+suffix+":"+name)
        return candidates[0]
    targets = [
        ("Geometry.fields", "/code/geometry.py", "fields", 7),
        ("PreparedCanonicalMoments.moments", "/prepared_moments.py", "moments", 7),
        ("AtomicNetwork.evaluate", "/atomic_network.py", "evaluate", 3),
        ("AtomicNetwork.rates", "/atomic_network.py", "rates", 3),
        ("ThermalSources.evaluate", "/thermal_sources.py", "evaluate", 2),
        ("ThermalSources.coefficients", "/thermal_sources.py", "coefficients", 2),
        ("RecombinationMoments.evaluate", "/recombination_moments.py", "evaluate", 2),
        ("ComptonFull63.compton_terms", "/compton_system.py", "compton_terms", 3),
        ("Geometry.normalized", "/code/geometry.py", "normalized", 2),
        ("Legendre Vandermonde", "/legendre.py", "legvander", 1),
        ("Mao factor", "/thermal_sources.py", "mao_factor", 26),
    ]
    counts = []
    for label, suffix, name, expected in targets:
        r = find("gather", suffix, name)
        if r["total_calls"] != expected*states:
            raise ValueError("STATIC_DYNAMIC_CALL_COUNT_MISMATCH:"+label)
        counts.append(dict(function=label, measured_calls=r["total_calls"], states=states,
                           measured_calls_per_state=r["calls_per_saved_state"], static_expected_per_state=expected,
                           self_seconds=r["self_seconds"], cumulative_seconds=r["cumulative_seconds"]))
    save_csv(RESULTS/"CALL_COUNTS.csv", counts)
    total = sum(p["profiler_total_self_seconds"] for p in profiles["gather"])
    groups = []
    for label, suffix, name in (("Thermal sources", "/thermal_sources.py", "evaluate"),
                                ("Geometry fields", "/code/geometry.py", "fields"),
                                ("Atomic network", "/atomic_network.py", "evaluate")):
        r = find("gather", suffix, name)
        groups.append(dict(group=label, cumulative_seconds=r["cumulative_seconds"], percent=100*r["cumulative_seconds"]/total,
                           calls_per_state=r["calls_per_saved_state"]))
    other = total-sum(r["cumulative_seconds"] for r in groups)
    if other < 0:
        raise ValueError("OVERLAPPING_PROFILE_GROUPS")
    groups.append(dict(group="Other", cumulative_seconds=other, percent=100*other/total, calls_per_state=""))
    save_csv(RESULTS/"DISJOINT_SUBTREE_TIMES.csv", groups)
    probe = read(UNIT/"evidence/timing_order_probe/RESULT.json")
    probe_rows = [dict(order=r["order"], resolution=r["resolution"], phase=phase,
                       wall_seconds=r[phase]["wall_seconds"], cpu_seconds=r[phase]["cpu_seconds"],
                       wall_ms_per_state=r[phase]["wall_seconds"]*1000/64)
                  for r in probe["measured"] for phase in ("gather", "collision")]
    save_csv(RESULTS/"ORDER_PROBE_TIMINGS.csv", probe_rows)
    prior = read(ROOT/"FINISHED.json")["active_wall_seconds"]+read(UNIT/"evidence/timing_order_probe/FINISHED.json")["active_wall_seconds"]
    extra_inputs = [ROOT/"CORPUS_MANIFEST.json", ROOT/"INPUT_MANIFEST.json", ROOT/"SUMMARY.json", ROOT/"FINISHED.json",
                    UNIT/"evidence/timing_order_probe/RESULT.json", UNIT/"evidence/timing_order_probe/FINISHED.json"]
    summary = dict(status="COMPLETE_C2_MEASUREMENT_AGGREGATION", selected_stage="C2", states=states, cases=8,
                   equal_gather_fields_per_case=16, equal_collision_point_fields_per_case=34,
                   profiled_gather_total_self_seconds=total, disjoint_subtrees=groups,
                   disjoint_scope="Geometry.fields, AtomicNetwork.evaluate and ThermalSources.evaluate are sibling cost regions on this gather path; ThermalSources receives the already evaluated network. Their inclusive times do not nest each other. Other is residual self time. Nested rows in FUNCTION_PROFILE.csv must not be summed.",
                   baseline_latency=latency, measured_call_counts=counts,
                   numerical_compute_wall_seconds_before_aggregation=prior,
                   new_IVPs=0, candidate_implementation=False, speedup_measured=False,
                   timing_caveat="Same-state timings vary substantially and the order probe moves the large delay to nominal as well. No stable physical-branch/resolution latency ordering or system-level cause is established.",
                   inherited_scientific_status=dict(physical="HOLD", production="NOT_APPROVED", global_convergence="NOT_RUN", REI_activation=False, U5="CLOSED"),
                   evidence=[dict(path=str(p.relative_to(UNIT)), sha256=sha(p)) for p in evidence+extra_inputs])
    save_json(RESULTS/"SUMMARY.json", summary)
    plt.rcParams.update({"font.size":8.5, "axes.titlesize":9.5, "axes.labelsize":8.5,
                         "xtick.labelsize":8, "ytick.labelsize":8.5, "legend.fontsize":8,
                         "pdf.fonttype":42, "ps.fonttype":42, "savefig.dpi":300})
    # Both figures are authored at 90 mm width; enlarging to double-column is safe.
    fig, ax = plt.subplots(figsize=(90/25.4, 135/25.4), layout="constrained")
    labels = []
    for i, row in enumerate(latency):
        label = row["label"]
        labels.append(label[1:3]+" "+("hot" if "actual_hot" in label else "ref")+" "+("R" if label.endswith("refined") else "N"))
        for phase, color, shift in (("gather", "#226B8A", -.14), ("collision", "#C16B22", .14)):
            values = row[phase+"_ms_per_state"]
            y = i+shift
            ax.plot([min(values), max(values)], [y,y], color=color, lw=1)
            ax.scatter(values, [y]*3, color=color, s=13, alpha=.7,
                       label=("Diagnostics" if phase == "gather" else "CI/CE") if i == 0 else None)
            ax.plot(row[phase+"_median_ms_per_state"], y, "|", color=color, markersize=10, markeredgewidth=1.8)
    ax.set_yticks(range(8), labels)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(.4, 40)
    ax.set_xticks([.5, 1, 3, 10, 30], ["0.5", "1", "3", "10", "30"])
    ax.set_xlabel("Wall time per saved state (ms; log)")
    ax.set_title("Baseline latency\n64 states / case; three repetitions", pad=10)
    ax.grid(axis="x", alpha=.2)
    ax.legend(loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES/("baseline_latency."+ext))
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(90/25.4, 88/25.4), layout="constrained")
    y = np.arange(len(groups))
    values = [row["percent"] for row in groups]
    ax.barh(y, values, color=["#267C72", "#226B8A", "#79558C", "#999999"], height=.58)
    ax.set_yticks(y, [row["group"].replace(" ","\n",1) for row in groups])
    ax.invert_yaxis()
    ax.set_xlim(0, 50)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    for i, value in enumerate(values):
        ax.text(value+1, i, f"{value:.1f}%", ha="left", va="center", fontsize=8.5)
    ax.set_xlabel("Share of profiled diagnostic time (%)")
    ax.set_title("Baseline cost attribution\n512 saved states; disjoint call subtrees", pad=9)
    ax.grid(axis="x", alpha=.15)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES/("baseline_cost_attribution."+ext))
    plt.close(fig)
    np.savez_compressed(FIGURES/"PLOT_DATA.npz",
        baseline_gather_ms=np.array([r["gather_ms_per_state"] for r in latency]),
        baseline_collision_ms=np.array([r["collision_ms_per_state"] for r in latency]),
        case_labels=np.array([r["label"] for r in latency]),
        cost_labels=np.array([r["group"] for r in groups]), cost_percent=np.array(values))
    save_json(FIGURES/"FIGURE_MANIFEST.json", dict(
        input_summary_sha256=sha(RESULTS/"SUMMARY.json"), plot_script_sha256=sha(__file__),
        nominal_width_mm=90, double_column_policy="enlarge the same vector PDF, not shrink a double-column layout",
        files=[dict(filename=p.name, bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(FIGURES.iterdir()) if p.is_file()],
        figure_status="RENDERED_REQUIRES_ACTUAL_VISUAL_REVIEW"))
    save_json(RESULTS/"AGGREGATION_RECEIPT.json", dict(status="PASS", active_wall_seconds=time.perf_counter()-START,
            prior_active_numerical_wall_seconds=prior, budget_cap_seconds=600, new_IVPs=0,
            result_summary_sha256=sha(RESULTS/"SUMMARY.json")))
    print(json.dumps(dict(status="COMPLETE_C2_AGGREGATION", subtrees=groups, numerical_wall_seconds=prior)), flush=True)


if __name__ == "__main__":
    main()

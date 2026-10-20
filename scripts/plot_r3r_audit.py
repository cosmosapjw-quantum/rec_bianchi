#!/usr/bin/env python3
"""Generate scientific R3R audit plots from a passing source-bound receipt.

This reads saved measurements and binary64 traces only.  It performs no
integration or benchmark.  Output files are create-only; visual review is a
separate required step and is not claimed by successful plot generation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import statistics
import subprocess
import sys
import time


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def identity(path):
    return {"path": str(path.resolve()), "bytes": path.stat().st_size,
            "sha256": sha256(path)}


def install_limits():
    for kind, cap in ((resource.RLIMIT_AS, 2*1024**3), (resource.RLIMIT_CPU, 60)):
        soft, hard = resource.getrlimit(kind)
        hard = cap if hard == resource.RLIM_INFINITY else min(hard, cap)
        soft = hard if soft == resource.RLIM_INFINITY else min(soft, hard)
        resource.setrlimit(kind, (soft, hard))

    def deadline(_signal, _frame):
        raise TimeoutError("R3R_PLOT_WORK_WALL_LIMIT")

    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 168.)


def validate_inputs(args, np):
    receipt = json.loads(args.benchmark.read_text())
    if receipt.get("status") != "PASS_SAVED_STREAM_AUDIT_ONLY":
        raise ValueError("R3R_PLOT_REQUIRES_PASSING_BENCHMARK")
    source = receipt["source"]["source_commit_sha"]
    if source != args.expected_source_sha:
        raise ValueError(f"R3R_PLOT_SOURCE_MISMATCH:{source}:{args.expected_source_sha}")
    lane = receipt["lane_binary64_trace"]
    if lane["status"] != "PASS" or lane["lanes"] != 25000 or lane["differing_binary64_lanes"] != 0:
        raise ValueError("R3R_PLOT_REQUIRES_PASSING_ACTUAL32_LANE_TRACE")
    if lane["identity"]["verdict"]["counts"]["STEP"] != 40:
        raise ValueError("R3R_PLOT_EXPECTED_8_PREFIX_PLUS_32_NEW_STEPS")
    if lane["native_byteorder"] not in ("little", "big"):
        raise ValueError("R3R_PLOT_UNKNOWN_TRACE_BYTEORDER")
    dtype = np.dtype("<f8" if lane["native_byteorder"] == "little" else ">f8")
    traces, input_files, contents = {}, {"benchmark": identity(args.benchmark)}, {}
    for backend in ("scalar", "numpy"):
        # Resolve beside the receipt, so an intact archived output directory
        # remains usable after relocation from its original absolute path.
        path = args.benchmark.parent / f"lane_ratios_{backend}.f64native.bin"
        info = identity(path)
        expected = lane["traces"][backend]
        if info["bytes"] != expected["bytes"] or info["sha256"] != expected["sha256"]:
            raise ValueError(f"R3R_PLOT_TRACE_HASH_MISMATCH:{backend}")
        if info["bytes"] != 8*lane["lanes"]:
            raise ValueError(f"R3R_PLOT_TRACE_SIZE:{backend}")
        contents[backend] = path.read_bytes()
        traces[backend] = np.frombuffer(contents[backend], dtype=dtype)
        if np.any(~np.isfinite(traces[backend])) or np.any(traces[backend] < 0.) or np.any(traces[backend] > 1.):
            raise ValueError(f"R3R_PLOT_TRACE_OUTSIDE_ACCEPTED_DOMAIN:{backend}")
        input_files[backend] = info
    differing = sum(contents["scalar"][i:i+8] != contents["numpy"][i:i+8]
                    for i in range(0, len(contents["scalar"]), 8))
    if differing != lane["differing_binary64_lanes"]:
        raise ValueError(f"R3R_PLOT_BINARY64_EQUIVALENCE_CHANGED:{differing}")
    measured = [row for row in receipt["trials"] if row["phase"] == "measured"]
    rounds = sorted({row["round"] for row in measured})
    if not 1 <= len(rounds) <= 5 or rounds != list(range(len(rounds))):
        raise ValueError("R3R_PLOT_ROUND_COUNT_OR_ORDER")
    for index in rounds:
        pair = [row for row in measured if row["round"] == index]
        if len(pair) != 2 or {row["backend"] for row in pair} != {"legacy", "r3r_numpy"}:
            raise ValueError(f"R3R_PLOT_INCOMPLETE_PAIR:{index}")
        expected_order = ["legacy", "r3r_numpy"] if index % 2 == 0 else ["r3r_numpy", "legacy"]
        if [row["backend"] for row in sorted(pair, key=lambda row: row["position"])] != expected_order:
            raise ValueError(f"R3R_PLOT_PAIR_ORDER:{index}")
        for row in pair:
            if any(not math.isfinite(row[key]) or row[key] <= 0. for key in ("cpu_s", "wall_s")):
                raise ValueError("R3R_PLOT_NONPOSITIVE_OR_NONFINITE_COST")
            if row["identity"] != lane["identity"]:
                raise ValueError("R3R_PLOT_TIMED_VERDICT_TRACE_MISMATCH")
    medians = {}
    rss = {}
    for backend in ("legacy", "r3r_numpy"):
        rows = [row for row in measured if row["backend"] == backend]
        medians[backend] = {key: statistics.median(row[key] for row in rows)
                            for key in ("cpu_s", "wall_s")}
        for key, value in medians[backend].items():
            if value != receipt["summary"]["backends"][backend]["median_"+key]:
                raise ValueError("R3R_PLOT_MEDIAN_RECEIPT_MISMATCH")
        process = receipt["fresh_process_rss"][backend]
        result = process["result"]
        if (process["returncode"] != 0 or result["status"] != "PASS" or
                result["source"]["source_commit_sha"] != source or
                result["trial"]["identity"] != lane["identity"]):
            raise ValueError(f"R3R_PLOT_RSS_RECEIPT_MISMATCH:{backend}")
        value = result["peak_rss_bytes"]
        if type(value) is not int or value <= 0:
            raise ValueError(f"R3R_PLOT_RSS_INVALID:{backend}")
        rss[backend] = value
    return {"receipt": receipt, "source": source, "traces": traces, "inputs": input_files,
            "differing_lanes": differing, "measured": measured, "rounds": rounds,
            "medians": medians, "rss": rss}


def render_figures(data, output_dir, plt, np):
    context = f"R3R saved R3Q 32-step stream audit | source {data['source'][:12]} | warm cache"
    colors = {"legacy": "#005AB5", "r3r_numpy": "#DC3220"}
    labels = {"legacy": "Frozen scalar audit", "r3r_numpy": "R3R NumPy audit"}
    styles = {"legacy": ("o", "-"), "r3r_numpy": ("s", "--")}
    files = {}

    def save(fig, name, footer):
        fig.suptitle(context, fontsize=11, y=.98)
        fig.text(.015, .012, footer, fontsize=8, va="bottom")
        fig.tight_layout(rect=(0., .105, 1., .91))
        for extension in ("png", "pdf", "svg"):
            path = output_dir / f"{name}.{extension}"
            if path.exists():
                raise FileExistsError(path)
            metadata = {"Title": name.replace("_", " "), "Creator": "REC R3R saved-evidence plot"}
            if extension == "pdf":
                metadata.update({"CreationDate": None, "ModDate": None})
            fig.savefig(path, dpi=200, metadata=metadata)
            files[path.name] = identity(path)
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12., 4.8))
    for axis, key, title in zip(axes, ("cpu_s", "wall_s"), ("CPU cost per complete audit", "Wall time per complete audit")):
        ymax = 0.
        for backend in ("legacy", "r3r_numpy"):
            rows = sorted((row for row in data["measured"] if row["backend"] == backend),
                          key=lambda row: row["round"])
            values = [row[key] for row in rows]
            median = data["medians"][backend][key]
            marker, linestyle = styles[backend]
            axis.plot([row["round"]+1 for row in rows], values, marker=marker,
                      linestyle=linestyle, color=colors[backend], linewidth=1.4,
                      label=f"{labels[backend]}: median {median:.4g} s")
            axis.axhline(median, linestyle=":", linewidth=.9, color=colors[backend], alpha=.75)
            ymax = max(ymax, *values)
        axis.set(title=title, xlabel="Paired round", ylabel="Seconds", ylim=(0., 1.18*ymax))
        axis.set_xticks([index+1 for index in data["rounds"]])
        axis.grid(alpha=.2)
        axis.legend(fontsize=8, loc="best")
    save(fig, "audit_cost",
         "Open, parsing, allocations, callbacks and verdict are timed. Warmups and ratio tracing are excluded.\n"
         "Order alternates by pair; dotted lines are medians. These are saved-stream audit costs; production speedup is not measured.")

    scalar = data["traces"]["scalar"]
    candidate = data["traces"]["numpy"]
    lane = np.arange(1, len(scalar)+1)
    zeros = int(np.count_nonzero(scalar == 0.))
    max_ratio = float(np.max(scalar))
    fig, axis = plt.subplots(figsize=(12., 4.8))
    axis.scatter(lane, scalar, s=2., linewidths=0., alpha=.55, color=colors["legacy"],
                 rasterized=True, label="Original scalar ratio; R3R bytes identical")
    axis.axhline(1., color="#8C510A", linestyle="--", linewidth=1.2, label="Acceptance boundary R = 1")
    axis.set_yscale("symlog", linthresh=1.e-12, linscale=1.)
    axis.set(xlim=(1, len(scalar)), ylim=(0., 1.5), xlabel="Spectral lane in encounter order",
             ylabel="Normalized absolute mismatch R", title="All 25,000 same-h photon tolerance ratios")
    axis.grid(alpha=.2)
    axis.legend(fontsize=8, loc="upper right")
    axis.text(.015, .97, f"Exact zero ratios: {zeros:,}\nMaximum R: {max_ratio:.8g}",
              transform=axis.transAxes, va="top", fontsize=9,
              bbox={"facecolor": "white", "edgecolor": ".8", "alpha": .9})
    save(fig, "photon_ratio_residual",
         "R = |Python - native C| / [1e-7 max(|Python|, |native C|) + 1e-10 fBB]. All lanes are plotted without subsampling.\n"
         "The symlog axis is linear below 1e-12; exact zeros remain zero. No data floor, clipping, or replacement is applied.")

    difference = candidate-scalar
    if np.any(difference != 0.):
        raise ValueError("R3R_PLOT_NONZERO_DIFFERENCE_AFTER_BYTE_GATE")
    fig, axis = plt.subplots(figsize=(12., 4.8))
    axis.scatter(lane, difference, s=2., linewidths=0., alpha=.65,
                 color="#008837", rasterized=True)
    axis.set(xlim=(1, len(scalar)), ylim=(-1., 1.), xlabel="Spectral lane in encounter order",
             ylabel="R3R ratio minus scalar ratio", title="Binary64 ratio equivalence across every lane")
    axis.set_yticks([0.])
    axis.grid(axis="x", alpha=.2)
    axis.text(.5, .8, f"Differing binary64 lanes: {data['differing_lanes']:,} / {len(scalar):,}\n"
              "Every plotted difference is exactly 0.0", transform=axis.transAxes,
              ha="center", va="center", fontsize=12)
    save(fig, "binary64_equivalence",
         "Equivalence is checked from both complete native binary64 traces, independently of maximum-ratio agreement.\n"
         "Only zero is marked on the vertical axis. Empty vertical space is display padding, not an error tolerance.")

    fig, axis = plt.subplots(figsize=(9., 4.8))
    backends = ("legacy", "r3r_numpy")
    values = [data["rss"][backend]/1024**2 for backend in backends]
    bars = axis.bar([labels[backend] for backend in backends], values,
                    color=[colors[backend] for backend in backends], width=.55)
    axis.set(ylabel="Peak resident memory (MiB)", ylim=(0., max(values)*1.2),
             title="Fresh-process peak RSS: one independent process per backend")
    axis.grid(axis="y", alpha=.2)
    axis.set_axisbelow(True)
    for bar, value in zip(bars, values):
        axis.annotate(f"{value:.3f} MiB", (bar.get_x()+bar.get_width()/2, bar.get_height()),
                      xytext=(0, 5), textcoords="offset points", ha="center", fontsize=10)
    save(fig, "fresh_process_memory",
         "Absolute process-lifetime peak RSS includes interpreter, imports, provenance hashing and loaded inputs.\n"
         "It is not an incremental comparator allocation measurement. MiB = 1,048,576 bytes; the axis begins at zero.")
    return files, {"lanes": len(scalar), "differing_binary64_lanes": data["differing_lanes"],
                   "exact_zero_ratios": zeros, "max_ratio": max_ratio,
                   "max_ratio_float_hex": max_ratio.hex(),
                   "ratio_axis": {"type": "symlog", "linear_threshold": 1.e-12,
                                  "data_floor_applied": False, "subsampling": False},
                   "equivalence_axis": {"marked_y_values": [0.], "display_padding": [-1., 1.],
                                        "padding_is_tolerance": False},
                   "rss_bytes": data["rss"], "measured_medians": data["medians"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument("--expected-source-sha", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    if len(args.expected_source_sha) != 40 or any(c not in "0123456789abcdef" for c in args.expected_source_sha):
        parser.error("--expected-source-sha must be a full lowercase source commit SHA")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    result = {"schema": "REC_R3R_SCIENTIFIC_PLOT_GENERATION_V1", "status": "RUNNING",
              "command": [sys.executable, *sys.argv], "created_utc": datetime.now(timezone.utc).isoformat(),
              "generator_source": identity(Path(__file__).resolve()), "visual_review": "NOT_RUN",
              "solver_integrations": 0, "benchmark_trials": 0}
    try:
        install_limits()
        os.environ.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                           "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"})
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10., "svg.hashsalt": "REC_R3R_AUDIT"})
        data = validate_inputs(args, np)
        result["inputs"] = data["inputs"]
        result["benchmark_source_commit_sha"] = data["source"]
        result["files"], result["display_and_data"] = render_figures(data, args.output_dir, plt, np)
        for item in result["inputs"].values():
            if sha256(Path(item["path"])) != item["sha256"]:
                raise ValueError("R3R_PLOT_INPUT_CHANGED_DURING_GENERATION")
        result["environment"] = {"python": sys.version, "numpy": np.__version__, "matplotlib": matplotlib.__version__,
                                 "rlimit_as": list(resource.getrlimit(resource.RLIMIT_AS)),
                                 "rlimit_cpu": list(resource.getrlimit(resource.RLIMIT_CPU))}
        result["status"] = "PASS_GENERATED_PENDING_VISUAL_REVIEW"
    except BaseException as exc:
        result["status"] = "FAIL"
        result["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        result["resources"] = {"cpu_s_since_process_start": usage.ru_utime+usage.ru_stime,
                               "wall_s_since_main_start": time.monotonic()-start,
                               "process_peak_rss_bytes": int(usage.ru_maxrss if sys.platform == "darwin" else usage.ru_maxrss*1024)}
        with (args.output_dir / "PLOT_GENERATION.json").open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
    print(json.dumps({"status": result["status"], "receipt": str(args.output_dir / "PLOT_GENERATION.json")}, sort_keys=True))
    return 0 if result["status"] == "PASS_GENERATED_PENDING_VISUAL_REVIEW" else 1


if __name__ == "__main__":
    raise SystemExit(main())

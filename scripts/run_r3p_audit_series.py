#!/usr/bin/env python3
"""Run the declared, serial R3P saved-data audit comparison; no integration."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_r3o_rust import Budget, dump_new, finalize_resource_record, sha256

PLAN = ROOT / "research/rec_r3p_exact_acceleration_20261020/BENCHMARK_PLAN.json"
EQUALITY_KEYS = ("verdict", "verdict_sha256", "native_array_sha256", "diagnostic_sha256")


def source_hashes():
    names = ("run_r3p_audit_series.py", "benchmark_r3p_audit.py",
             "r3p_stream_audit.py", "r3p_rust_audit.py", "build_r3p_rust.py",
             "build_r3o_rust.py", "verify_r3i_h2_u6_rt_boundary.py")
    paths = [ROOT / "scripts" / n for n in names] + [PLAN]
    paths += list((ROOT / "rust/rec-stream-audit/src").glob("*.rs"))
    return {str(p.relative_to(ROOT)): sha256(p) for p in paths}


def summarize(samples):
    """Descriptive paired results; the observed range is not a confidence bound."""
    groups = {}
    by_round = {(s["round"], s["configuration"]): s for s in samples}
    for name in ("legacy", "cached", "rust1", "rust2", "rust4"):
        rows = [s for s in samples if s["configuration"] == name]
        metrics = {key: {"median": statistics.median([s[key] for s in rows]),
                         "min": min(s[key] for s in rows),
                         "max": max(s[key] for s in rows)}
                   for key in ("audit_cpu_s", "audit_wall_s", "total_cpu_s",
                               "total_wall_s", "peak_rss_bytes")}
        ratios = {key: [by_round[(s["round"], "legacy")][key] / s[key] for s in rows]
                  for key in ("audit_cpu_s", "audit_wall_s")}
        groups[name] = {"samples": len(rows), "metrics": metrics,
                       "paired_legacy_over_candidate": {
                           k: {"values": v, "median": statistics.median(v),
                               "observed_min": min(v), "observed_max": max(v)}
                           for k, v in ratios.items()}}
    return groups


def run(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    plan = json.loads(PLAN.read_text())
    caps = plan["series_caps"]
    budget = Budget(out, cpu_s=caps["process_tree_cpu_s"], wall_s=caps["wall_s"],
                    memory_bytes=caps["memory_bytes"])
    report = {"schema": "rec.r3p.audit-series.v1", "status": "FAILED",
              "new_physical_steps": 0, "samples": [], "plan": plan,
              "source_sha256": source_hashes(), "build_receipt_sha256": sha256(args.build),
              "equality_keys": list(EQUALITY_KEYS), "statistics": "DESCRIPTIVE_3_ROUND_OBSERVED_RANGE_ONLY"}
    dump_new(out / "plan.json", plan)
    baseline = None
    exit_code = 2
    try:
        env = os.environ.copy()
        for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
            env[key] = "1"
        with (out / "progress.jsonl").open("x") as progress:
            for i, order in enumerate(plan["rounds"]):
                for name in order:
                    if source_hashes() != report["source_sha256"]:
                        raise RuntimeError("R3P_SOURCE_CHANGED_DURING_SERIES")
                    if sha256(args.build) != report["build_receipt_sha256"]:
                        raise RuntimeError("R3P_BUILD_RECEIPT_CHANGED_DURING_SERIES")
                    label = f"round{i}_{name}"
                    sample_dir = out / label
                    backend = "rust" if name.startswith("rust") else name
                    threads = int(name[-1]) if backend == "rust" else 1
                    cmd = [sys.executable, "-B", ROOT / "scripts/benchmark_r3p_audit.py",
                           "--raw", args.raw.resolve(), "--checkpoint", args.checkpoint.resolve(),
                           "--output", sample_dir, "--backend", backend,
                           "--threads", str(threads), "--cpus", str(plan["affinity_cpus"]),
                           "--block-columns", str(plan["rust_block_columns"]),
                           "--build", args.build.resolve()]
                    budget.run(cmd, cwd=ROOT, env=env, label=label)
                    sample = json.loads((sample_dir / "result.json").read_text())
                    if sample["status"] != "AUDIT_COMPLETED_PENDING_DIFFERENTIAL_REVIEW":
                        raise RuntimeError(f"R3P_SAMPLE_FAILED:{label}")
                    if baseline is None:
                        if name != "legacy":
                            raise RuntimeError("R3P_PLAN_REQUIRES_FIRST_LEGACY")
                        baseline = sample
                    same = {k: sample[k] == baseline[k] for k in EQUALITY_KEYS}
                    if not all(same.values()):
                        raise ArithmeticError(f"R3P_DIFFERENTIAL_MISMATCH:{label}:{same}")
                    if (sample["affinity"] != baseline["affinity"]
                            or sample["input_sha256"] != baseline["input_sha256"]
                            or sample["source_sha256"] != baseline["source_sha256"]):
                        raise RuntimeError(f"R3P_UNMATCHED_CONTEXT:{label}")
                    sample.update(round=i, configuration=name, equality=same,
                                  result_sha256=sha256(sample_dir / "result.json"))
                    report["samples"].append(sample)
                    line = {k: sample[k] for k in ("round", "configuration", "audit_cpu_s", "audit_wall_s", "equality", "result_sha256")}
                    progress.write(json.dumps(line, sort_keys=True) + "\n")
                    progress.flush()
                    os.fsync(progress.fileno())
                    print(json.dumps(line, sort_keys=True), flush=True)
            if source_hashes() != report["source_sha256"]:
                raise RuntimeError("R3P_SOURCE_CHANGED_AFTER_SERIES")
        report["summary"] = summarize(report["samples"])
        report["status"] = "PASS_SAVED_AUDIT_DIFFERENTIAL_AND_MATCHED_MEASUREMENT"
        exit_code = 0
    except BaseException as exc:
        report["first_failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        report["commands"] = budget.commands
        exit_code = finalize_resource_record(report, budget, exit_code, "AUDIT_SERIES")
        dump_new(out / "series.json", report)
    return report, exit_code


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("raw", "checkpoint", "build", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    report, code = run(p.parse_args())
    print(json.dumps({k: report.get(k) for k in ("status", "process_tree_cpu_s", "wall_s", "first_failure")}, sort_keys=True))
    raise SystemExit(code)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Plot hash-bound R3S dummy scheduler evidence within its existing allocation.

This does not run pytest, an NCP campaign, a solver, or a scientific benchmark.
The optional prior plotting receipt carries a failed/rendering attempt forward;
the same charge receipt cannot be consumed again in a fresh output directory.
"""
from __future__ import annotations

import resource
import time
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
CPU_S, WALL_S, MEMORY_BYTES = 60., 180., 2 * 1024**3
RESERVE_CPU_S, RESERVE_WALL_S = 2., 3.
ENVELOPE = {"cpu_s": CPU_S, "wall_s": WALL_S, "per_process_as_bytes": MEMORY_BYTES}
LABEL = "SYNTHETIC SCHEDULER CONTRACT\nNOT NCP / SOLVER SPEEDUP"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def number(value):
    require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
            "INVALID_NONNEGATIVE_FINITE_MEASUREMENT")
    return float(value)


def read_json(data):
    def invalid(value):
        raise ValueError("NONFINITE_JSON:" + value)
    return json.loads(data, parse_constant=invalid)


def write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def lower(kind, requested):
    soft, hard = resource.getrlimit(kind)
    hard = requested if hard == resource.RLIM_INFINITY else min(hard, requested)
    soft = hard if soft == resource.RLIM_INFINITY else min(soft, hard)
    resource.setrlimit(kind, (soft, hard))


class Ledger:
    def __init__(self, prior_cpu, prior_wall):
        self.prior_cpu, self.prior_wall = number(prior_cpu), number(prior_wall)
        # Linux starttime is rounded down to clock ticks. Charging from process
        # birth conservatively includes interpreter startup and every import.
        stat = Path("/proc/self/stat").read_text().rsplit(") ", 1)[1].split()
        self.process_birth_boot_s = int(stat[19]) / os.sysconf("SC_CLK_TCK")
        self.inherited = {"cpu": list(resource.getrlimit(resource.RLIMIT_CPU)),
                          "as": list(resource.getrlimit(resource.RLIMIT_AS))}
        self.check()
        lower(resource.RLIMIT_CPU, max(1, math.floor(CPU_S - self.prior_cpu)))
        lower(resource.RLIMIT_AS, MEMORY_BYTES)
        soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
        work_soft = max(1, math.floor(CPU_S - self.prior_cpu - RESERVE_CPU_S))
        resource.setrlimit(resource.RLIMIT_CPU, (min(soft, work_soft), hard))
        signal.signal(signal.SIGXCPU, self.expired)
        signal.signal(signal.SIGALRM, self.expired)
        signal.setitimer(signal.ITIMER_REAL, WALL_S - self.wall() - RESERVE_WALL_S)

    def expired(self, *_):
        # A consumed work alarm must immediately leave a kernel-enforced final
        # deadline in place, including while an exception unwinds or fsync waits.
        self.final_hard_wall()
        raise TimeoutError("R3S_PLOT_EXISTING_ALLOCATION_WORK_RESERVE_REACHED")

    def cpu(self):
        own = resource.getrusage(resource.RUSAGE_SELF)
        child = resource.getrusage(resource.RUSAGE_CHILDREN)
        return self.prior_cpu + own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime

    def wall(self):
        return self.prior_wall + time.clock_gettime(time.CLOCK_BOOTTIME) - self.process_birth_boot_s

    def check(self):
        require(self.cpu() < CPU_S - RESERVE_CPU_S and self.wall() < WALL_S - RESERVE_WALL_S,
                "R3S_PLOT_EXISTING_ALLOCATION_EXHAUSTED")

    def final_hard_wall(self):
        # Final serialization/fsync has the reserved interval, not an unlimited
        # wall interval after disabling the work alarm.
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
        signal.setitimer(signal.ITIMER_REAL, max(.001, WALL_S - self.wall()))


class BoundInputs:
    def __init__(self, directory, manifest, budget):
        self.directory, self.manifest, self.budget = directory, manifest, budget
        self.observed = {}

    def canonical(self, relative):
        path = PurePosixPath(relative)
        require(not path.is_absolute() and ".." not in path.parts
                and str(path) == relative, "UNSAFE_EVIDENCE_PATH")
        current = self.directory
        for part in path.parts:
            current = current / part
            require(not current.is_symlink(), "SYMLINK_EVIDENCE_ALIAS")
        require(current.resolve().is_relative_to(self.directory), "EVIDENCE_ESCAPES_INPUT_ROOT")
        return current

    def read(self, relative):
        self.budget.check()
        require(relative in self.manifest and re.fullmatch(r"[0-9a-f]{64}", self.manifest[relative]),
                "EVIDENCE_NOT_BOUND_BY_VALIDATION:" + relative)
        path = self.canonical(relative)
        require(path.is_file() and path.stat().st_size <= 32 * 1024**2, "EVIDENCE_SIZE_OR_TYPE")
        data = path.read_bytes()
        require(digest(data) == self.manifest[relative], "EVIDENCE_SHA256_MISMATCH:" + relative)
        self.observed[relative] = {"bytes": len(data), "sha256": digest(data)}
        self.budget.check()
        return data

    def check_after(self):
        for relative in tuple(self.observed):
            self.read(relative)


def git(args, budget, commands):
    budget.check()
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False,
                            timeout=min(10., WALL_S - budget.wall() - RESERVE_WALL_S))
    commands.append({"command": ["git", *args], "exit_code": result.returncode,
                     "stdout_sha256": digest(result.stdout), "stderr_sha256": digest(result.stderr),
                     "stdout": result.stdout.decode("utf-8", "replace"),
                     "stderr": result.stderr.decode("utf-8", "replace")})
    require(result.returncode == 0, "PLOTTING_SOURCE_GIT_READ_FAILED")
    budget.check()
    return result.stdout


def source_binding(commit, validated, budget, commands):
    require(git(["rev-parse", "HEAD"], budget, commands).decode().strip() == commit,
            "PLOTTING_HEAD_MISMATCH")
    script = Path(__file__).resolve()
    relative = str(script.relative_to(ROOT))
    entry = git(["ls-tree", "-z", commit, "--", relative], budget, commands)
    require(entry.endswith(b"\0") and entry.count(b"\0") == 1, "PLOT_CODE_NOT_IN_FIXED_COMMIT")
    meta, name = entry[:-1].split(b"\t", 1)
    mode, kind, blob = meta.decode().split()
    content = script.read_bytes()
    actual_blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    require(kind == "blob" and name.decode() == relative and actual_blob == blob,
            "PLOT_CODE_FIXED_BLOB_MISMATCH")
    # The renderer may be committed after validation. Keep the identities
    # distinct and require the actual validated source closure to stay exact.
    for path, record in validated["files"].items():
        candidate = ROOT / path
        require(candidate.resolve().is_relative_to(ROOT) and not candidate.is_symlink(),
                "VALIDATED_SOURCE_PATH_UNSAFE")
        require(digest(candidate.read_bytes()) == record["sha256"], "VALIDATED_SOURCE_CHANGED:" + path)
        budget.check()
    return {"plotting_commit": commit,
            "plotting_tree": git(["rev-parse", commit + "^{tree}"], budget, commands).decode().strip(),
            "plot_code_path": relative, "plot_code_sha256": digest(content), "plot_code_git_blob": blob,
            "plot_code_git_mode": mode, "validation_commit": validated["commit"],
            "validation_tree": validated["tree"], "validated_source_files": len(validated["files"])}


def successful_case(inputs, expected_campaign_sha):
    candidates, ignored_aliases = [], []
    for relative in sorted(inputs.manifest):
        if PurePosixPath(relative).name != "events.jsonl":
            continue
        try:
            inputs.canonical(relative)
        except ValueError as error:
            if str(error) == "SYMLINK_EVIDENCE_ALIAS":
                ignored_aliases.append(relative)
                continue
            raise
        events = [read_json(line) for line in inputs.read(relative).splitlines() if line.strip()]
        starts = [event for event in events if event.get("event") == "job_started"]
        ends = [event for event in events if event.get("event") == "job_terminal"]
        if len(starts) != 3 or len(ends) != 3 or sum(e.get("exclusive") is True for e in starts) != 1:
            continue
        ids = [event["job"] for event in starts]
        require(len(set(ids)) == 3 and all(re.fullmatch(r"[A-Za-z0-9_.-]+", key) for key in ids),
                "DUPLICATE_OR_INVALID_DUMMY_JOB")
        require(all(type(event.get("exclusive")) is bool for event in starts), "DUMMY_ROLE_MISSING")
        start_by_id, end_by_id = {e["job"]: e for e in starts}, {e["job"]: e for e in ends}
        require(set(end_by_id) == set(ids), "DUMMY_EVENT_IDENTITIES_DIFFER")
        case_root = PurePosixPath(relative).parent
        driver_path = str(case_root.parent / "driver.stdout.json")
        driver = read_json(inputs.read(driver_path))
        require(driver["failure"] is None and driver["all_owned_descendants_reaped"] is True
                and driver["new_solver_integrations"] == 0 and driver["timed_scientific_benchmark_trials"] == 0
                and driver["source_sha256"] == expected_campaign_sha, "SUCCESSFUL_SYNTHETIC_DRIVER_REQUIRED")
        jobs = []
        for key in ids:
            choices = [str(case_root / key / "TERMINAL.json"), str(case_root / "jobs" / key / "TERMINAL.json")]
            choices = [path for path in choices if path in inputs.manifest]
            require(len(choices) == 1, "DUMMY_TERMINAL_LAYOUT_AMBIGUOUS")
            raw = inputs.read(choices[0])
            terminal = read_json(raw)
            require(terminal["job"] == key and terminal["status"] == "complete"
                    and terminal["returncode"] == 0 and terminal == driver["jobs"][key]
                    and end_by_id[key]["receipt_sha256"] == digest(raw), "DUMMY_TERMINAL_BINDING_FAILED")
            start, finish = number(terminal["started_monotonic_s"]), number(terminal["terminal_monotonic_s"])
            require(finish > start, "NONPOSITIVE_DUMMY_LIFETIME")
            jobs.append({"id": key, "exclusive": start_by_id[key]["exclusive"], "start_s": start,
                         "finish_s": finish, "cpu_s": number(terminal["cpu_s"]),
                         "wall_s": number(terminal["wall_s"]),
                         "polled_tree_rss_bytes": number(terminal["max_polled_process_tree_rss_bytes"]),
                         "start_event_s": number(start_by_id[key]["monotonic_s"]),
                         "terminal_event_s": number(end_by_id[key]["monotonic_s"]),
                         "terminal_path": choices[0], "terminal_sha256": digest(raw)})
        independent = [job for job in jobs if not job["exclusive"]]
        exclusive = next(job for job in jobs if job["exclusive"])
        require(len(independent) == 2 and all(job["terminal_event_s"] < exclusive["start_event_s"]
                                            for job in independent), "EXCLUSIVE_BARRIER_NOT_OBSERVED")
        overlap = min(j["finish_s"] for j in independent) - max(j["start_s"] for j in independent)
        require(overlap > 0, "INDEPENDENT_SUPERVISOR_INTERVALS_DO_NOT_OVERLAP")
        candidates.append({"events_path": relative, "driver_stdout_path": driver_path,
                           "jobs": sorted(jobs, key=lambda job: job["start_s"]),
                           "independent_supervisor_interval_overlap_s": overlap})
    require(len(candidates) == 1, "EXPECTED_ONE_CANONICAL_SUCCESSFUL_SYNTHETIC_CASE")
    return {**candidates[0], "ignored_symlink_aliases": ignored_aliases,
            "interpretation": "Supervisor lifetimes of sleeping dummy jobs; no CPU parallel-efficiency or solver speedup claim"}


def render(case, out, budget, source):
    budget.check()
    os.environ["MPLCONFIGDIR"] = str(out / "matplotlib-cache")
    os.environ["MPLBACKEND"] = "Agg"
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[name] = "1"
    import matplotlib
    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt
    budget.check()
    jobs = case["jobs"]
    origin = min(job["start_s"] for job in jobs)
    labels = [job["id"] + (" · exclusive" if job["exclusive"] else " · independent") for job in jobs]
    colors = ["#D55E00" if job["exclusive"] else "#0072B2" for job in jobs]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none"})
    figure = plt.figure(figsize=(11.5, 7.5))
    grid = figure.add_gridspec(2, 2, height_ratios=(1.1, 1))
    timeline, cpu, rss = figure.add_subplot(grid[0, :]), figure.add_subplot(grid[1, 0]), figure.add_subplot(grid[1, 1])
    figure.suptitle(LABEL, fontsize=17, fontweight="bold", color="#8B1E1E", y=.98)
    for index, job in enumerate(jobs):
        timeline.barh(index, job["finish_s"] - job["start_s"], left=job["start_s"] - origin,
                      height=.58, color=colors[index])
    timeline.set_yticks(range(len(jobs)), labels)
    timeline.invert_yaxis()
    timeline.set_xlabel("Elapsed seconds from first supervisor start")
    timeline.set_title("Actual recorded supervisor lifetimes", loc="left", fontsize=12)
    for axis, field, divisor, title, unit in ((cpu, "cpu_s", 1., "Charged job CPU", "CPU seconds"),
                                             (rss, "polled_tree_rss_bytes", 1024**2, "Sampled process-tree RSS", "MiB")):
        values = [job[field] / divisor for job in jobs]
        axis.bar(range(len(jobs)), values, color=colors, width=.6)
        axis.set_xticks(range(len(jobs)), [job["id"] for job in jobs])
        axis.set_ylabel(unit)
        axis.set_title(title, loc="left", fontsize=12)
        axis.set_ylim(0, max(values + [.001]) * 1.3)
        for index, value in enumerate(values):
            annotation = "no live sample" if field == "polled_tree_rss_bytes" and value == 0 else f"{value:.4g}"
            axis.annotate(annotation, (index, value), xytext=(0, 5), textcoords="offset points", ha="center", fontsize=9)
    for axis in (timeline, cpu, rss):
        for side in ("top", "right"):
            axis.spines[side].set_visible(False)
        axis.grid(axis="x" if axis is timeline else "y", color="#D9DDE2", linewidth=.6)
        axis.set_axisbelow(True)
    figure.text(.02, .06, "Sleeping dummy commands. Intervals include guardian/setup/closeout; RSS is sampled, not an exact aggregate peak.", fontsize=9)
    figure.text(.02, .025, "Validation source: " + source["validation_commit"][:12] + "  |  No NCP execution or solver timing represented.", fontsize=9)
    figure.subplots_adjust(top=.79, bottom=.17, left=.15, right=.98, hspace=.62, wspace=.3)
    files = []
    try:
        for extension in ("png", "pdf", "svg"):
            budget.check()
            destination = out / ("synthetic_scheduler_contract." + extension)
            require(not destination.exists(), "FIGURE_ALREADY_EXISTS")
            figure.savefig(destination, dpi=170, facecolor="white", bbox_inches="tight")
            budget.check()
            files.append({"path": destination.name, "bytes": destination.stat().st_size,
                          "sha256": digest(destination.read_bytes())})
    finally:
        plt.close(figure)
    return {"figure_count": 1, "files": files, "matplotlib_version": matplotlib.__version__,
            "visual_inspection": "NOT_RUN_REQUIRES_DIRECT_REVIEW", "display_label": LABEL}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validation-dir", type=Path, required=True)
    ap.add_argument("--validation-sha256", required=True)
    ap.add_argument("--expected-commit", required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--prior-receipt", type=Path)
    ap.add_argument("--prior-sha256")
    args = ap.parse_args()
    require(re.fullmatch(r"[0-9a-f]{40}", args.expected_commit), "FULL_PLOTTING_COMMIT_REQUIRED")
    require(re.fullmatch(r"[0-9a-f]{64}", args.validation_sha256), "FULL_VALIDATION_SHA256_REQUIRED")
    lower(resource.RLIMIT_AS, MEMORY_BYTES)
    lower(resource.RLIMIT_CPU, 60)
    validation_dir = args.validation_dir.resolve(strict=True)
    validation_path = validation_dir / "validation.json"
    require(not validation_path.is_symlink() and validation_path.stat().st_size <= 32 * 1024**2,
            "INVALID_VALIDATION_RECEIPT_FILE")
    validation_bytes = validation_path.read_bytes()
    require(digest(validation_bytes) == args.validation_sha256, "VALIDATION_RECEIPT_SHA256_MISMATCH")
    validation = read_json(validation_bytes)
    require(validation["status"] == "COMPLETED_SCOPED" and validation["source_input_identity"] == "UNCHANGED"
            and validation["total_envelope"] == ENVELOPE and validation["NCP_execution"] == "NOT_RUN"
            and validation["new_scientific_integrations"] == 0, "SCOPED_LOCAL_VALIDATION_REQUIRED")
    allocation = validation["allocation_id"]
    require(re.fullmatch(r"REC_R3S_LOCAL_VALIDATION_[A-Z0-9_]+", allocation), "INVALID_EXISTING_ALLOCATION")
    charge, charge_sha = validation, args.validation_sha256
    require(bool(args.prior_receipt) == bool(args.prior_sha256), "PRIOR_RECEIPT_AND_SHA_REQUIRED_TOGETHER")
    if args.prior_receipt:
        raw = args.prior_receipt.read_bytes()
        require(digest(raw) == args.prior_sha256, "PRIOR_PLOT_SHA256_MISMATCH")
        charge = read_json(raw)
        require(charge["schema"] == "rec.r3s.local-plotting.v1" and charge["allocation_charge_committed"] is True
                and charge["allocation_id"] == allocation and charge["total_envelope"] == ENVELOPE
                and charge["validation_sha256"] == args.validation_sha256
                and number(charge["process_tree_cpu_s"]) >= number(validation["process_tree_cpu_s"])
                and number(charge["wall_s"]) >= number(validation["wall_s"]), "PRIOR_PLOT_ALLOCATION_MISMATCH")
        charge_sha = args.prior_sha256
    budget = Ledger(charge["process_tree_cpu_s"], charge["wall_s"])
    out = args.output_dir.resolve()
    require(out != ROOT and ROOT not in out.parents and out != validation_dir and validation_dir not in out.parents,
            "PLOT_OUTPUT_MUST_BE_OUTSIDE_SOURCE_AND_RAW_INPUT")
    out.mkdir(parents=True, exist_ok=False)
    sys.dont_write_bytecode = True
    record = {"schema": "rec.r3s.local-plotting.v1", "status": "HOLD", "allocation_id": allocation,
              "allocation_charge_committed": False, "total_envelope": ENVELOPE,
              "validation_sha256": args.validation_sha256, "validation_dir": str(validation_dir),
              "charge_receipt_sha256": charge_sha, "prior_cpu_s": charge["process_tree_cpu_s"],
              "prior_wall_s": charge["wall_s"], "command": [sys.executable, *sys.argv],
              "first_failure": None, "source_commands": [], "new_scientific_integrations": 0,
              "new_REC_benchmark_trials": 0, "NCP_execution": "NOT_RUN", "inherited_limits": budget.inherited}
    inputs = BoundInputs(validation_dir, validation["evidence_sha256"], budget)
    saved_fds, code = [os.dup(1), os.dup(2)], 2
    with (out / "work.stdout.log").open("xb") as stdout, (out / "work.stderr.log").open("xb") as stderr:
        try:
            sys.stdout.flush(); sys.stderr.flush()
            os.dup2(stdout.fileno(), 1); os.dup2(stderr.fileno(), 2)
            registry = ROOT.parent / "rec_r3s_plot_allocation_registry"
            registry.mkdir(exist_ok=True)
            claim_path = registry / (allocation + "_" + charge_sha + ".json")
            write_new(claim_path, {"allocation_id": allocation, "charge_receipt_sha256": charge_sha,
                                  "validation_sha256": args.validation_sha256, "output_dir": str(out),
                                  "expected_plotting_commit": args.expected_commit})
            record.update(allocation_charge_committed=True, allocation_claim=str(claim_path))
            before = read_json(inputs.read("SOURCE_BEFORE.json"))
            after = read_json(inputs.read("SOURCE_AFTER.json"))
            require(before == after and before["commit"] == validation["source_commit"]
                    and before["tree"] == validation["source_tree"], "VALIDATION_SOURCE_CLOSURE_MISMATCH")
            binding = source_binding(args.expected_commit, before, budget, record["source_commands"])
            record["source"] = binding
            case = successful_case(inputs, before["files"]["scripts/run_r3s_ncp_campaign.py"]["sha256"])
            write_new(out / "PLOT_DATA.json", {"scope": LABEL, "case": case, "source": binding})
            print(json.dumps({"event": "canonical_synthetic_case_selected", "path": case["events_path"]}))
            record["figures"] = render(case, out, budget, binding)
            inputs.check_after()
            require(digest(validation_path.read_bytes()) == args.validation_sha256, "VALIDATION_CHANGED_DURING_PLOT")
            require(source_binding(args.expected_commit, before, budget, record["source_commands"]) == binding,
                    "PLOTTING_SOURCE_CHANGED")
            record["source_input_identity"] = "UNCHANGED"
            record["plot_data_sha256"] = digest((out / "PLOT_DATA.json").read_bytes())
            budget.check()
            record["status"], code = "COMPLETED_SYNTHETIC_PLOTS_PENDING_VISUAL_REVIEW", 0
            print(json.dumps({"event": "figures_written", "figure_count": 1, "formats": ["png", "pdf", "svg"]}))
        except BaseException as error:
            budget.final_hard_wall()
            record["first_failure"] = {"type": type(error).__name__, "message": str(error)}
            print(json.dumps(record["first_failure"]), file=sys.stderr)
        finally:
            sys.stdout.flush(); sys.stderr.flush()
            os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
            for target, saved in enumerate(saved_fds, 1):
                os.dup2(saved, target); os.close(saved)
    record["input_raw"] = inputs.observed
    for channel in ("stdout", "stderr"):
        path = out / ("work." + channel + ".log")
        record[channel] = {"path": path.name, "sha256": digest(path.read_bytes()),
                           "scope": "FD_CAPTURE_AFTER_RECEIPT_BINDING_THROUGH_FINAL_WORK_AND_SOURCE_READBACK"}
    if budget.cpu() >= CPU_S - RESERVE_CPU_S or budget.wall() >= WALL_S - RESERVE_WALL_S:
        record["status"], code = "HOLD_RESOURCE_RESERVE", 2
    record.update(process_tree_cpu_s=budget.cpu(), wall_s=budget.wall(), exit_code=code,
                  effective_limits={"cpu": list(resource.getrlimit(resource.RLIMIT_CPU)),
                                    "as": list(resource.getrlimit(resource.RLIMIT_AS))},
                  python=sys.version, executable=sys.executable,
                  environment={"uname": list(os.uname()), "byteorder": sys.byteorder},
                  affinity=sorted(os.sched_getaffinity(0)),
                  max_self_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                  max_reaped_child_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
                  memory_scope="PER_PROCESS_RLIMIT_AS_AND_RUSAGE_PEAKS; NO_EXACT_AGGREGATE_RSS_CLAIM",
                  measurement_scope="PRIOR_LEDGER_PLUS_COMPLETE_PLOT_PROCESS_AND_REAPED_GIT_CHILDREN_INCLUDING_IMPORTS_HASHING_AND_LOG_FSYNC",
                  wall_accounting="Prior active intervals plus current Linux process age from boot start ticks; editing pauses excluded",
                  final_write_reserve={"cpu_s": RESERVE_CPU_S, "wall_s": RESERVE_WALL_S},
                  measurement_excludes="Final plotting.json serialization/fsync and terminal summary, covered by reserve")
    record["new_execution_cpu_s"] = record["process_tree_cpu_s"] - budget.prior_cpu
    record["new_execution_wall_s"] = record["wall_s"] - budget.prior_wall
    budget.final_hard_wall()
    write_new(out / "plotting.json", record)
    print(json.dumps({"status": record["status"], "exit_code": code, "allocation_id": allocation,
                      "receipt": str(out / "plotting.json"), "process_tree_cpu_s": record["process_tree_cpu_s"],
                      "wall_s": record["wall_s"]}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

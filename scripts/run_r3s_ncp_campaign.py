#!/usr/bin/env python3
"""Finite R3S platform campaign; --plan never launches jobs.

Only the two existing R3R trace contracts, saved-stream benchmark, and matched
16-step public pilots are executable. Historical completed campaigns and
unimplemented h4/global/REI nodes cannot become executable through JSON edits.
"""
from __future__ import annotations

import time
MODULE_ENTRY_WALL = time.monotonic()

import argparse
import ctypes
from dataclasses import dataclass
import fcntl
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import signal
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/rec_r3s_ncp_campaign_20261021/CAMPAIGN.json"
CPU_S, WALL_S, MEMORY_BYTES = 60., 180., 2 * 1024**3
RESERVE_CPU_S, RESERVE_WALL_S = 5., 12.
HOST_MEMORY_RESERVE = MEMORY_BYTES
ALLOCATION_REGISTRY = ROOT.parent / "rec_r3s_allocation_registry"
FROZEN = "research/rec_r3q_h4_continuation_20261020/SOURCE_CLOSURE.json"
CASE_NAMES = {
    "trace_original": "test_actual_all_lane_binary64_bytes_separate_from_maxima",
    "trace_interleaved": "test_valid_arbitrary_per_tag_interleaving_and_ordered_lane_trace",
}
CATALOG = {
    "trace_original": {"depends_on": [], "exclusive": False},
    "trace_interleaved": {"depends_on": [], "exclusive": False},
    "saved_stream_benchmark": {"depends_on": list(CASE_NAMES), "exclusive": True},
    "h4_legacy16": {"depends_on": list(CASE_NAMES), "exclusive": True},
    "h4_numpy16": {"depends_on": ["h4_legacy16"], "exclusive": True},
}
RAW_SHA256 = {
    "native_oracle_stdout.csv": "3f1ab809f7fec021aeccba45c5ab887a82872e66e108e15c4bcb6df14ebb803d",
    "python_continuation.npz": "a83f0831c1fb82e2e7d28c85551587671f7aaa0fe3816ff7c4d01953f24c1216",
    "verification.json": "b7b9247a9bf5a98884a85a8248cc9b7b30135782b76d2a98c76acb34f7037427",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def log_event(path, event):
    event = {"monotonic_s": time.monotonic(), **event}
    with Path(path).open("a") as stream:
        stream.write(json.dumps(event, sort_keys=True, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def lower_pair(inherited, cap):
    soft, hard = inherited
    hard = cap if hard == resource.RLIM_INFINITY else min(hard, cap)
    soft = hard if soft == resource.RLIM_INFINITY else min(soft, hard)
    return soft, hard


def total_cpu():
    own = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime


def enable_subreaper():
    """Keep new-session descendants owned even after their leader exits."""
    require(hasattr(signal, "pidfd_send_signal"), "PIDFD_SIGNAL_UNAVAILABLE")
    libc = ctypes.CDLL(None, use_errno=True)
    require(libc.prctl(36, 1, 0, 0, 0) == 0, "LINUX_CHILD_SUBREAPER_UNAVAILABLE")
    actual = ctypes.c_int()
    require(libc.prctl(37, ctypes.byref(actual), 0, 0, 0) == 0 and actual.value == 1,
            "LINUX_CHILD_SUBREAPER_NOT_ENABLED")


def install_lower_limits():
    records = {"inherited": {}, "effective": {}}
    for name, kind, cap in (("cpu", resource.RLIMIT_CPU, 60),
                            ("address_space", resource.RLIMIT_AS, MEMORY_BYTES)):
        before = resource.getrlimit(kind)
        resource.setrlimit(kind, lower_pair(before, cap))
        records["inherited"][name] = list(before)
        records["effective"][name] = list(resource.getrlimit(kind))
    return records


def cpu_set(text):
    values = set()
    for token in text.split(","):
        require(re.fullmatch(r"\d+(?:-\d+)?", token) is not None, "INVALID_CPU_LIST")
        bounds = [int(x) for x in token.split("-")]
        low, high = bounds[0], bounds[-1]
        require(0 <= low <= high <= 65535, "INVALID_CPU_RANGE")
        values.update(range(low, high + 1))
    return sorted(values)


def cgroup_limits(directory, mount):
    """Minimum applicable ancestor limits, including remaining memory."""
    directory, mount = Path(directory).resolve(), Path(mount).resolve()
    require(directory.is_relative_to(mount), "CGROUP_OUTSIDE_MOUNT")
    records, cpu_caps, memory_remaining = [], [], []
    current = directory
    while True:
        item = {"path": str(current)}
        cpu = current / "cpu.max"
        if cpu.is_file():
            quota, period = cpu.read_text().split()
            require(int(period) > 0, "INVALID_CGROUP_CPU_PERIOD")
            item["cpu_max"] = [quota, int(period)]
            if quota != "max":
                require(int(quota) > 0, "INVALID_CGROUP_CPU_QUOTA")
                cpu_caps.append(int(quota) / int(period))
        maximum = current / "memory.max"
        if maximum.is_file():
            limit = maximum.read_text().strip()
            item["memory_max"] = limit
            if limit != "max":
                usage = int((current / "memory.current").read_text())
                require(int(limit) >= 0 and usage >= 0, "INVALID_CGROUP_MEMORY")
                memory_remaining.append(max(0, int(limit) - usage))
                item["memory_current"] = usage
        records.append(item)
        if current == mount:
            break
        current = current.parent
    return {"ancestors": records, "cpu_quota_cores": min(cpu_caps) if cpu_caps else None,
            "memory_remaining_bytes": min(memory_remaining) if memory_remaining else None}


def hardware():
    require(sys.platform.startswith("linux"), "LINUX_NCP_REQUIRED")
    mem = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        name, value = line.split(":", 1)
        if name in ("MemTotal", "MemAvailable"):
            mem[name] = int(value.split()[0]) * 1024
    require(set(mem) == {"MemTotal", "MemAvailable"}, "MEMORY_OBSERVATION_MISSING")
    cgroup_rows = Path("/proc/self/cgroup").read_text().splitlines()
    unified = next((line.split(":", 2)[2] for line in cgroup_rows
                    if line.startswith("0::")), None)
    require(not cgroup_rows or all(line.startswith("0::") for line in cgroup_rows),
            "CGROUP_V1_OR_HYBRID_UNSUPPORTED_FAIL_CLOSED")
    cg = {"ancestors": [], "cpu_quota_cores": None, "memory_remaining_bytes": None}
    if unified is not None:
        mounts = [line.split(" - ", 1) for line in Path("/proc/self/mountinfo").read_text().splitlines()]
        candidates = [parts[0].split() for parts in mounts if parts[1].split()[0] == "cgroup2"]
        require(bool(candidates), "CGROUP2_MOUNT_UNRESOLVED")
        fields = candidates[0]
        mount_root, mount_path = Path(fields[3]), Path(fields[4])
        require(Path(unified).is_relative_to(mount_root), "CGROUP2_PATH_UNRESOLVED")
        directory = mount_path / Path(unified).relative_to(mount_root)
        require(directory.is_dir(), "CGROUP2_CURRENT_DIRECTORY_UNRESOLVED")
        cg = cgroup_limits(directory, mount_path)
    affinity = sorted(os.sched_getaffinity(0))
    effective_cpus = len(affinity)
    if cg["cpu_quota_cores"] is not None:
        effective_cpus = min(effective_cpus, math.floor(cg["cpu_quota_cores"]))
    available = mem["MemAvailable"]
    if cg["memory_remaining_bytes"] is not None:
        available = min(available, cg["memory_remaining_bytes"])
    return {"hostname": platform.node(), "logical_cpus": os.cpu_count(), "affinity": affinity,
            "effective_cpu_slots": effective_cpus, "memory_total_bytes": mem["MemTotal"],
            "memory_available_bytes": mem["MemAvailable"], "effective_memory_available_bytes": available,
            "cgroup": cg, "python": sys.version, "executable": sys.executable,
            "load_average": list(os.getloadavg()), "kernel": platform.release(), "machine": platform.machine(),
            "limits": {"cpu": list(resource.getrlimit(resource.RLIMIT_CPU)),
                       "address_space": list(resource.getrlimit(resource.RLIMIT_AS))},
            "scope": "CURRENT_OBSERVATION; CPU_OWNERSHIP_REQUIRES_CALLER_ASSIGNED_CPU_IDS"}


def validate_host(observed, expected_host, assigned):
    require(bool(expected_host) and observed["hostname"] == expected_host, "NCP_HOST_IDENTITY_MISMATCH")
    require(observed["logical_cpus"] >= 64 and observed["memory_total_bytes"] >= 128_000_000_000,
            "NCP_64_CPU_128_GB_TARGET_NOT_OBSERVED")
    require(assigned and set(assigned).issubset(observed["affinity"]), "CPU_ASSIGNMENT_OUTSIDE_AFFINITY")
    slots = min(len(assigned), observed["effective_cpu_slots"])
    memory_slots = max(0, (observed["effective_memory_available_bytes"] - HOST_MEMORY_RESERVE) // MEMORY_BYTES)
    require(slots > 0 and memory_slots > 0, "NO_EFFECTIVE_CPU_OR_MEMORY_CAPACITY")
    return min(slots, memory_slots)


def memory_capacity(observed, capacity):
    # Reserve every active/new job in full from current availability. No RSS
    # credit: shared pages make summed RSS unsuitable as reclaimable memory.
    slots = max(0, (observed["effective_memory_available_bytes"] - HOST_MEMORY_RESERVE) // MEMORY_BYTES)
    return min(capacity, observed["effective_cpu_slots"], slots)


def git(*argv):
    result = subprocess.run(["git", *argv], cwd=ROOT, capture_output=True, check=False, timeout=10)
    require(result.returncode == 0, "GIT_IDENTITY_FAILURE")
    return result.stdout


def bind_source(expected):
    require(re.fullmatch(r"[0-9a-f]{40}", expected or "") is not None, "FULL_SOURCE_SHA_REQUIRED")
    require(git("rev-parse", "HEAD").decode().strip() == expected, "SOURCE_HEAD_MISMATCH")
    entries = {}
    for row in git("ls-tree", "-rz", expected).split(b"\0"):
        if row:
            prefix, name = row.split(b"\t", 1)
            mode, kind, blob = prefix.decode().split()
            entries[name.decode()] = (mode, kind, blob)
    frozen = json.loads((ROOT / FROZEN).read_text())
    manifest = json.loads(MANIFEST.read_text())
    names = set(frozen["files"]) | set(manifest["source_paths"]) | {
        str(MANIFEST.relative_to(ROOT)), FROZEN, "scripts/run_r3s_ncp_campaign.py"}
    hashes = {}
    for name in sorted(names):
        path = ROOT / name
        require(not Path(name).is_absolute() and ".." not in Path(name).parts
                and path.is_file() and not path.is_symlink(), "UNSAFE_OR_MISSING_SOURCE_PATH:" + name)
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        entry = entries.get(name)
        require(entry is not None and entry[1:] == ("blob", blob), "SOURCE_NOT_FIXED_GIT:" + name)
        hashes[name] = hashlib.sha256(data).hexdigest()
        if name in frozen["files"]:
            require(hashes[name] == frozen["files"][name], "FROZEN_SOURCE_CHANGED:" + name)
    return {"commit": expected, "tree": git("rev-parse", expected + "^{tree}").decode().strip(),
            "files_sha256": hashes, "manifest_sha256": sha(MANIFEST)}


def validate_dag(nodes):
    require(isinstance(nodes, list), "DAG_NODES_REQUIRED")
    by_id = {node["id"]: node for node in nodes}
    require(len(by_id) == len(nodes), "DUPLICATE_DAG_ID")
    visiting, visited = set(), set()
    def visit(key):
        require(key in by_id, "UNKNOWN_DAG_DEPENDENCY:" + key)
        require(key not in visiting, "DAG_CYCLE")
        if key in visited:
            return
        node = by_id[key]
        require(node["status"] in ("complete_reused", "ready", "blocked"), "UNKNOWN_DAG_STATUS")
        if node["status"] == "ready":
            require(key in CATALOG and node.get("depends_on", []) == CATALOG[key]["depends_on"],
                    "UNALLOWLISTED_READY_JOB:" + key)
        if key in CATALOG:
            require(node.get("exclusive") == CATALOG[key]["exclusive"], "TIMING_BARRIER_CHANGED:" + key)
        visiting.add(key)
        for dependency in node.get("depends_on", []):
            visit(dependency)
        visiting.remove(key)
        visited.add(key)
    for key in by_id:
        visit(key)
    return by_id


def selected_jobs(nodes, requested):
    by_id = validate_dag(nodes)
    selected = set()
    def add(key):
        require(key in CATALOG and key in by_id, "NONEXECUTABLE_JOB_REQUESTED:" + key)
        require(by_id[key]["status"] == "ready", "JOB_NOT_READY:" + key)
        selected.add(key)
        for parent in CATALOG[key]["depends_on"]:
            if by_id[parent]["status"] != "complete_reused":
                add(parent)
    for key in requested:
        add(key)
    return [key for key in CATALOG if key in selected]


def input_hashes(raw_dir, needed):
    if not needed:
        return {}
    require(raw_dir is not None, "SAVED_FULL_STREAM_INPUT_DIRECTORY_REQUIRED")
    result = {}
    for name, expected in RAW_SHA256.items():
        path = raw_dir / name
        require(path.is_file() and not path.is_symlink() and sha(path) == expected,
                "SAVED_STREAM_INPUT_SHA_MISMATCH:" + name)
        result[str(path.resolve())] = expected
    return result


@dataclass(frozen=True)
class Job:
    id: str
    argv: tuple[str, ...]
    directory: Path
    depends_on: tuple[str, ...] = ()
    exclusive: bool = False


def make_job(key, directory, source, allocation, raw_dir):
    require(key in CATALOG, "UNALLOWLISTED_COMMAND")
    prefix = [sys.executable, "-B", "-X", "pycache_prefix=" + str(directory / "pycache")]
    if key in CASE_NAMES:
        argv = prefix + ["-m", "pytest", "-q", "-p", "no:cacheprovider",
            "tests/test_r3r_stream_audit.py::" + CASE_NAMES[key],
            "--basetemp=" + str(directory / "pytest-temp"),
            "-o", "tmp_path_retention_policy=all", "--junitxml=" + str(directory / "tests.xml")]
    elif key == "saved_stream_benchmark":
        argv = prefix + [str(ROOT / "scripts/benchmark_r3r_stream_audit.py"), "--source-sha", source,
            "--native-stream", str(raw_dir / "native_oracle_stdout.csv"),
            "--python-result", str(raw_dir / "python_continuation.npz"),
            "--verification", str(raw_dir / "verification.json"), "--rounds", "5", "--warmups", "1",
            "--output-dir", str(directory / "run")]
    else:
        backend = "legacy" if key == "h4_legacy16" else "numpy"
        argv = prefix + [str(ROOT / "scripts/run_r3r_h4_supervised.py"), "--expected-commit", source,
            "--new-allocation-id", allocation + "_" + key, "--evidence-dir", str(directory / "run"),
            "--backend", backend, "--steps", "16"]
    return Job(key, tuple(argv), directory, tuple(CATALOG[key]["depends_on"]), CATALOG[key]["exclusive"])


def choose_ready(pending, running, completed, capacity):
    if any(job.exclusive for job in running) or capacity <= len(running):
        return []
    ready = [job for job in pending if set(job.depends_on).issubset(completed)]
    exclusive = [job for job in ready if job.exclusive]
    if exclusive:
        return [] if running else exclusive[:1]
    return ready[:capacity - len(running)]


BOOTSTRAP = r"""
import json, os, resource, signal, sys, time
started=time.monotonic()
request=json.loads(sys.argv[1])
record={"inherited":{},"effective":{},"cpu_id":request["cpu_id"]}
for name,kind,cap in (("cpu",resource.RLIMIT_CPU,60),("address_space",resource.RLIMIT_AS,2*1024**3)):
    soft,hard=resource.getrlimit(kind); record["inherited"][name]=[soft,hard]
    hard=cap if hard==resource.RLIM_INFINITY else min(cap,hard)
    soft=hard if soft==resource.RLIM_INFINITY else min(soft,hard)
    resource.setrlimit(kind,(soft,hard)); record["effective"][name]=list(resource.getrlimit(kind))
os.sched_setaffinity(0,{request["cpu_id"]})
def deadline(_signal,_frame):
    raise TimeoutError("R3S_GUARDIAN_WORK_DEADLINE")
signal.signal(signal.SIGALRM,deadline)
signal.signal(signal.SIGTERM,deadline)
signal.setitimer(signal.ITIMER_REAL,168.)
with open(request["limits_receipt"],"x") as out:
    json.dump(record,out,sort_keys=True); out.write("\n"); out.flush(); os.fsync(out.fileno())
sys.path.insert(0,request["scripts"])
import run_r3s_ncp_campaign as campaign
raise SystemExit(campaign.run_guardian(request,started))
"""


def file_hashes(directory):
    return {str(p.relative_to(directory)): sha(p) for p in sorted(directory.rglob("*"))
            if p.is_file() and not p.is_symlink() and "pycache" not in p.parts}


def verify_job(job):
    if job.id in CASE_NAMES:
        cases = ET.parse(job.directory / "tests.xml").getroot().findall(".//testcase")
        require(len(cases) == 1 and cases[0].get("name") == CASE_NAMES[job.id]
                and not any(cases[0].find(tag) is not None for tag in ("failure", "error", "skipped")),
                "PLATFORM_CONTRACT_NOT_PASSED")
        traces = list((job.directory / "pytest-temp").rglob("trace.stdout.json"))
        require(len(traces) == 1, "RAW_CHILD_TRACE_MISSING")
        trace = json.loads(traces[0].read_text())["trace"]
        require(trace["status"] == "PASS" and trace["lanes"] == 25000
                and trace["differing_binary64_lanes"] == 0, "PLATFORM_LANE_GATE")
        return {"verdict": "PASS_SCOPED", "existing_contracts_revalidated": 1, "new_integrations": 0}
    if job.id == "saved_stream_benchmark":
        receipt = json.loads((job.directory / "run/benchmark.json").read_text())
        require(receipt["status"] == "PASS", "SAVED_AUDIT_BENCHMARK_NOT_PASSED")
        return {"verdict": "PASS_SCOPED", "new_integrations": 0,
                "scope": "WARM_CACHE_SAVED_STREAM_AUDIT_ONLY"}
    if job.id.startswith("h4_"):
        binding = json.loads((job.directory / "run/R3R_BINDING.json").read_text())
        worker = json.loads((job.directory / "run/worker/verification.json").read_text())
        require(binding["source_identity"] == "UNCHANGED" and binding["exit_code"] == 0
                and worker["status"] == "SMOKE_ONLY" and worker["first_failure"] is None
                and worker["python_result"]["extra_accepted"] == 16
                and worker["same_h_parity"]["status"] == "PASS"
                and worker["common_input_sample"]["status"] == "PASS", "PILOT_CONTRACT_NOT_PASSED")
        return {"verdict": "PASS_SCOPED", "new_accepted_steps": 16,
                "physical_validity": "HOLD", "production_readiness": "NOT_APPROVED"}
    return {"verdict": "TEST_DUMMY_ONLY"}


def local_signal_pid(outer_pid, own_status, child_status, caller_pid):
    """Select the caller's namespace level, never the child's innermost PID."""
    def ns_ids(status):
        row = next((line.split()[1:] for line in status.splitlines() if line.startswith("NSpid:")), None)
        return None if row is None else [int(value) for value in row]
    own, child = ns_ids(own_status), ns_ids(child_status)
    if own is None or child is None:
        require(own is None and child is None, "PID_NAMESPACE_METADATA_INCOMPLETE")
        own_outer = next(int(line.split()[1]) for line in own_status.splitlines() if line.startswith("Pid:"))
        require(own_outer == caller_pid, "PID_NAMESPACE_MAPPING_UNVERIFIED")
        return outer_pid
    require(own and own[-1] == caller_pid and len(child) >= len(own)
            and child[0] == outer_pid, "PID_NAMESPACE_MAPPING_MISMATCH")
    return child[len(own) - 1]


def proc_children(pid, proc_root=Path("/proc")):
    """Union all TID children; fall back to a PPID scan if the interface is absent."""
    children = set()
    tasks = proc_root / str(pid) / "task"
    missing = False
    try:
        tids = list(tasks.iterdir())
    except FileNotFoundError:
        tids, missing = [], True
    for tid in tids:
        try:
            children.update(int(value) for value in (tid / "children").read_text().split())
        except FileNotFoundError:
            missing = True
    if missing:
        for entry in proc_root.iterdir():
            if not entry.name.isdigit():
                continue
            try:
                fields = (entry / "stat").read_text().rsplit(") ", 1)[1].split()
            except (FileNotFoundError, ProcessLookupError):
                continue
            if int(fields[1]) == pid:
                children.add(int(entry.name))
    return sorted(children)


def live_usage(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()
        ticks = sum(int(fields[i]) for i in (11, 12, 13, 14))
        rss = int(fields[21]) * os.sysconf("SC_PAGE_SIZE")
    except (FileNotFoundError, ProcessLookupError):
        return 0., 0
    used = ticks / os.sysconf("SC_CLK_TCK")
    for child in proc_children(pid):
        c, r = live_usage(child)
        used += c; rss += r
    return used, rss


def procfs_child_pid(namespace_pid):
    own_status = Path("/proc/self/status").read_text()
    own = int(Path("/proc/self/stat").read_text().split(" ", 1)[0])
    for child in proc_children(own):
        try:
            actual = local_signal_pid(child, own_status, Path(f"/proc/{child}/status").read_text(), os.getpid())
            if actual == namespace_pid:
                return child
        except (FileNotFoundError, ProcessLookupError):
            pass
    return None


def procfd_stat(fd):
    part = os.open("stat", os.O_RDONLY | os.O_CLOEXEC, dir_fd=fd)
    with os.fdopen(part) as stream:
        return stream.read().rsplit(") ", 1)[1].split()


def child_snapshot(procfs_pid, support):
    """Open stable descriptors for immediate owned children only.

    Killing/reaping leaders reparents further descendants to this subreaper;
    cleanup repeats until no children remain. A direct PPID check against this
    still-living caller precedes signaling through the same descriptor.
    """
    result = []
    try:
        for pid in support.proc_children(procfs_pid):
            fd = None
            try:
                fd = os.open(f"/proc/{pid}", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
                fields = procfd_stat(fd)
                require(int(fields[1]) == procfs_pid, "CHILD_PARENT_IDENTITY_CHANGED")
                result.append((fd, pid, procfs_pid))
                fd = None
            except (FileNotFoundError, ProcessLookupError):
                pass
            finally:
                if fd is not None:
                    os.close(fd)
    except BaseException:
        for fd, _pid, _parent in result:
            os.close(fd)
        raise
    return result


def kill_snapshot(snapshot):
    try:
        for fd, _outer_pid, parent in snapshot:
            try:
                fields = procfd_stat(fd)
                require(int(fields[1]) == parent, "SIGNAL_TARGET_PARENT_CHANGED")
                signal.pidfd_send_signal(fd, signal.SIGKILL, None, 0)
            except (FileNotFoundError, ProcessLookupError):
                pass
    finally:
        for fd, _pid, _parent in snapshot:
            os.close(fd)


def reap_available():
    result = []
    while True:
        try:
            pid, status, usage = os.wait4(-1, os.WNOHANG)
        except ChildProcessError:
            break
        if not pid:
            break
        result.append((pid, status, usage))
    return result


def cleanup_children(own_procfs, support, deadline):
    """Subreaper ownership survives leader exit and descendant setsid()."""
    reaped = []
    while True:
        children = child_snapshot(own_procfs, support)
        kill_snapshot(children)
        reaped.extend(reap_available())
        if not support.proc_children(own_procfs):
            reaped.extend(reap_available())
            return reaped
        require(time.monotonic() < deadline, "OWNED_DESCENDANT_CLEANUP_UNRESOLVED")
        time.sleep(.01)


def run_guardian(request, started):
    """One bounded guardian per job; no project/numerical import precedes limits."""
    support = sys.modules[__name__]
    enable_subreaper()
    libc = ctypes.CDLL(None, use_errno=True)
    require(libc.prctl(1, signal.SIGTERM, 0, 0, 0) == 0, "PARENT_DEATH_SIGNAL_UNAVAILABLE")
    require(os.getppid() == request["parent_pid"], "CAMPAIGN_PARENT_ALREADY_EXITED")
    own_procfs = int(Path("/proc/self/stat").read_text().split(" ", 1)[0])
    process = None
    failure, leader_exit, orphan_reaps, max_rss = None, None, [], 0
    try:
        process = subprocess.Popen(request["argv"], cwd=ROOT, env=os.environ.copy(), start_new_session=True)
        while True:
            for pid, status, _usage in reap_available():
                if pid == process.pid:
                    leader_exit = process.returncode = os.waitstatus_to_exitcode(status)
                else:
                    orphan_reaps.append(pid)
            descendants = support.proc_children(own_procfs)
            if leader_exit is not None:
                require(not descendants and not orphan_reaps, "JOB_LEADER_LEFT_OWNED_DESCENDANTS")
                break
            live_cpu, rss = 0., 0
            for pid in descendants:
                c, r = support.live_usage(pid)
                live_cpu += c; rss += r
            max_rss = max(max_rss, rss)
            require(total_cpu() + live_cpu < CPU_S - 4., "JOB_AGGREGATE_CPU_WORK_CAP")
            require(time.monotonic() - started < WALL_S - 12., "JOB_WALL_WORK_CAP")
            require(rss <= MEMORY_BYTES, "JOB_AGGREGATE_RSS_CAP")
            time.sleep(.025)
        require(leader_exit == 0, "JOB_COMMAND_NONZERO_EXIT")
    except BaseException as exc:
        failure = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.)
        try:
            extra = cleanup_children(own_procfs, support, min(started + WALL_S - 3., time.monotonic() + 3.))
            for pid, status, _usage in extra:
                if process is not None and pid == process.pid:
                    leader_exit = process.returncode = os.waitstatus_to_exitcode(status)
                else:
                    orphan_reaps.append(pid)
        except Exception as exc:
            failure = {"type": type(exc).__name__, "message": str(exc)}
    receipt = {"status": "PASS" if failure is None else "HOLD", "command_exit_code": leader_exit,
        "failure": failure, "reaped_adopted_descendant_pids": orphan_reaps,
        "subreaper_enabled": True, "all_owned_descendants_reaped": not support.proc_children(own_procfs),
        "cpu_s": total_cpu(), "wall_s": time.monotonic() - started,
        "max_polled_command_tree_rss_bytes": max_rss,
        "scope": "GUARDIAN_AND_ALL_REAPED_DESCENDANTS; FINAL_RECEIPT_WRITE_RESERVED"}
    write_new(Path(request["guardian_receipt"]), receipt)
    return 0 if failure is None and receipt["all_owned_descendants_reaped"] else 2


def allocation_claim(identity, resume):
    """An allocation ID cannot be moved to a new output directory to reset spend."""
    ALLOCATION_REGISTRY.mkdir(parents=True, exist_ok=True)
    path = ALLOCATION_REGISTRY / (identity["allocation_id"] + ".json")
    if resume:
        require(path.is_file() and json.loads(path.read_text()) == identity, "ALLOCATION_REGISTRY_IDENTITY_MISMATCH")
    else:
        require(not path.exists(), "ALLOCATION_ALREADY_RESERVED_USE_ORIGINAL_RESUME")
        write_new(path, identity)
    return path


def checked_costs(record, previous=(0., 0.)):
    values = record["cumulative_cpu_s"], record["cumulative_wall_s"]
    require(all(isinstance(value, (float, int)) and not isinstance(value, bool)
                and math.isfinite(value) and value >= 0 for value in values), "INVALID_PRIOR_RESOURCE_COST")
    require(all(value >= old for value, old in zip(values, previous)), "NONMONOTONE_PRIOR_RESOURCE_COST")
    return values


def stable_environment(observed):
    return {key: observed[key] for key in
            ("hostname", "logical_cpus", "memory_total_bytes", "python", "executable", "kernel", "machine")}


def runtime_identity(test_pythonpath=None):
    """Read distribution/binary identity without importing NumPy or pytest."""
    search = ([str(test_pythonpath.resolve())] if test_pythonpath else []) + sys.path
    packages = {}
    for distribution in importlib.metadata.distributions(path=search):
        name = distribution.metadata.get("Name", "").lower()
        if name not in ("numpy", "pytest") or name in packages:
            continue
        files = {}
        for item in distribution.files or ():
            relative = str(item)
            if relative.endswith((".so", "/METADATA")) or relative in ("numpy/__init__.py", "pytest/__init__.py"):
                path = Path(distribution.locate_file(item)).resolve()
                files[str(path)] = sha(path)
        packages[name] = {"version": distribution.version, "metadata_and_binary_sha256": files}
    compiler = shutil.which("cc")
    return {"python_binary_sha256": sha(Path(sys.executable).resolve()), "packages": packages,
            "cc": None if compiler is None else {"path": str(Path(compiler).resolve()), "sha256": sha(compiler)},
            "scope": "PYTHON_BINARY; NUMPY_PYTEST_DISTRIBUTION_METADATA_AND_COMPILED_BINARIES; CC_BINARY"}


def resume_records(directory, expected_header):
    header = json.loads((directory / "CAMPAIGN.json").read_text())
    require(header == expected_header, "RESUME_IDENTITY_HOST_CPUS_OR_BUDGET_MISMATCH")
    starts = sorted(directory.glob("attempt_*.STARTED.json"))
    terminals = sorted(directory.glob("attempt_*.TERMINAL.json"))
    require([p.name.replace("STARTED", "TERMINAL") for p in starts] == [p.name for p in terminals],
            "RESUME_UNCLOSED_ATTEMPT_PRESERVE_ACTIVE_OR_UNKNOWN_WORK")
    costs = (0., 0.)
    for start_path, terminal_path in zip(starts, terminals):
        start, terminal = json.loads(start_path.read_text()), json.loads(terminal_path.read_text())
        require((start["prior_cpu_s"], start["prior_wall_s"]) == costs
                and start["allocation_id"] == header["allocation_id"]
                and terminal["allocation_id"] == header["allocation_id"]
                and start["source"] == header["source"] and terminal["source"] == header["source"],
                "RESUME_ATTEMPT_CHAIN_MISMATCH")
        costs = checked_costs(terminal, costs)
    completed, blocked = {}, {}
    for key in header["selected"]:
        path = directory / "jobs" / key / "TERMINAL.json"
        if path.exists():
            receipt = json.loads(path.read_text())
            require(receipt["job"] == key and receipt["status"] in ("complete", "blocked"),
                    "RESUME_JOB_IDENTITY_INVALID")
            for name, digest in receipt["files_sha256"].items():
                target = path.parent / name
                require(target.resolve().is_relative_to(path.parent.resolve()) and not target.is_symlink()
                        and sha(target) == digest, "RESUME_OUTPUT_HASH_MISMATCH")
            (completed if receipt["status"] == "complete" else blocked)[key] = receipt
        elif path.parent.exists():
            blocked[key] = {"status": "blocked", "reason": "PARTIAL_JOB_DIRECTORY_PRESERVED"}
    return len(starts) + 1, *costs, completed, blocked


def arm_deadline(remaining):
    require(math.isfinite(remaining) and remaining > 0., "CAMPAIGN_WALL_RESERVE_ALREADY_EXHAUSTED")
    old = signal.getitimer(signal.ITIMER_REAL)[0]
    def expired(_signal, _frame):
        raise TimeoutError("R3S_CAMPAIGN_WALL_DEADLINE")
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, min(old, remaining) if old > 0. else remaining)


def host_intake(path, observed, source_sha, selected, assigned, verified_resume_completed=()):
    """Read the current authorized REC result/session inventory; never infer it."""
    require(path is not None and path.is_file(), "CURRENT_HOST_RESULT_INTAKE_REQUIRED")
    receipt = json.loads(path.read_text())
    require(receipt.get("schema") == "rec.r3s.current-host-intake.v1"
            and receipt["hostname"] == observed["hostname"]
            and receipt["source_commit"] == source_sha
            and receipt["assigned_cpu_ids"] == assigned
            and set(selected).issubset(receipt["examined_job_ids"]), "HOST_INTAKE_IDENTITY_MISMATCH")
    age = time.time() - receipt["observed_unix_s"]
    require(math.isfinite(age) and 0. <= age <= 600., "HOST_INTAKE_NOT_CURRENT")
    duplicate = set(selected).intersection(receipt["matching_completed_job_ids"]) - set(verified_resume_completed)
    require(not duplicate,
            "MATCHING_COMPLETED_PLATFORM_JOB_MUST_BE_REUSED")
    require(not set(assigned).intersection(receipt["busy_cpu_ids"]), "ASSIGNED_CPU_CONFLICT_IN_CURRENT_INTAKE")
    require(bool(receipt["inventory_files_sha256"]), "HOST_INTAKE_RAW_EVIDENCE_MISSING")
    for name, expected in receipt["inventory_files_sha256"].items():
        require(Path(name).is_file() and sha(name) == expected, "HOST_INTAKE_RAW_HASH_MISMATCH")
    return {"path": str(path.resolve()), "sha256": sha(path), "receipt": receipt}


def execute_jobs(jobs, out, assigned_cpus, capacity, env, campaign_cpu, campaign_wall,
                 prior_cpu=0., prior_wall=0., already_complete=None):
    """Single-thread scheduler. Each job has a separate bounded subreaper."""
    start_cpu, start_wall = total_cpu(), time.monotonic()
    support = sys.modules[__name__]
    enable_subreaper()
    own_procfs = int(Path("/proc/self/stat").read_text().split(" ", 1)[0])
    require(not support.proc_children(own_procfs), "EXISTING_CHILD_PROCESS_OWNERSHIP_UNKNOWN")
    pending, active = list(jobs), {}
    completed = dict(already_complete or {})
    results = {}
    events = out / "events.jsonl"
    failure = None
    try:
        while pending or active:
            current_cpu = prior_cpu + total_cpu() - start_cpu
            current_wall = prior_wall + time.monotonic() - start_wall
            require(current_cpu < campaign_cpu - RESERVE_CPU_S
                    and current_wall < campaign_wall - RESERVE_WALL_S, "CAMPAIGN_RESERVE_REACHED")
            observation = hardware()
            live_capacity = memory_capacity(observation, capacity)
            launch = choose_ready(pending, [v["job"] for v in active.values()], set(completed), live_capacity)
            for job in launch:
                before_setup = total_cpu()
                started = time.monotonic()
                used = {v["cpu_id"] for v in active.values()}
                cpu_id = next(cpu for cpu in assigned_cpus if cpu not in used)
                job.directory.mkdir(parents=True, exist_ok=False)
                (job.directory / "pycache").mkdir()
                (job.directory / "guardian_pycache").mkdir()
                request = {"argv": list(job.argv), "cpu_id": cpu_id, "parent_pid": os.getpid(),
                    "scripts": str(ROOT / "scripts"), "limits_receipt": str(job.directory / "LIMITS.json"),
                    "guardian_receipt": str(job.directory / "GUARDIAN.json")}
                stdout = (job.directory / "stdout.log").open("xb")
                stderr = (job.directory / "stderr.log").open("xb")
                try:
                    process = subprocess.Popen([sys.executable, "-B", "-X",
                        "pycache_prefix=" + str(job.directory / "guardian_pycache"),
                        "-c", BOOTSTRAP, json.dumps(request)], cwd=ROOT, env=env,
                        stdout=stdout, stderr=stderr, start_new_session=True)
                except BaseException:
                    stdout.close(); stderr.close()
                    raise
                active[process.pid] = {"job": job, "process": process, "cpu_id": cpu_id,
                    "started": started, "procfs_pid": None, "max_rss": 0,
                    "stdout": stdout, "stderr": stderr, "failure": None,
                    "setup_cpu_s": total_cpu() - before_setup}
                pending.remove(job)
                log_event(events, {"event": "job_started", "job": job.id, "pid": process.pid,
                    "cpu_id": cpu_id, "exclusive": job.exclusive, "command": list(job.argv)})
            live_cpu = 0.
            for pid, state in list(active.items()):
                process, job = state["process"], state["job"]
                finished, status, usage = os.wait4(pid, os.WNOHANG)
                if not finished:
                    if state["procfs_pid"] is None:
                        state["procfs_pid"] = support.procfs_child_pid(pid)
                    if state["procfs_pid"] is None:
                        require(time.monotonic() - state["started"] <= 1., "CHILD_PID_MAPPING_UNRESOLVED")
                        continue
                    cpu_used, rss = support.live_usage(state["procfs_pid"])
                    live_cpu += cpu_used
                    state["max_rss"] = max(state["max_rss"], rss)
                    require(cpu_used < CPU_S - 2. and time.monotonic() - state["started"] < WALL_S - 3.
                            and rss <= MEMORY_BYTES, "PER_JOB_RESOURCE_RESERVE_REACHED:" + job.id)
                    continue
                process.returncode = os.waitstatus_to_exitcode(status)
                state["stdout"].close(); state["stderr"].close()
                before_closeout = total_cpu()
                verdict = guardian = None
                try:
                    require(process.returncode == 0, "JOB_GUARDIAN_NONZERO_EXIT")
                    guardian = json.loads((job.directory / "GUARDIAN.json").read_text())
                    require(guardian["status"] == "PASS" and guardian["all_owned_descendants_reaped"],
                            "JOB_DESCENDANT_OR_RESOURCE_FAILURE")
                    verdict = verify_job(job)
                except Exception as exc:
                    state["failure"] = f"{type(exc).__name__}: {exc}"
                files = file_hashes(job.directory)
                used_cpu = usage.ru_utime + usage.ru_stime + state["setup_cpu_s"] + total_cpu() - before_closeout
                elapsed = time.monotonic() - state["started"]
                if used_cpu >= CPU_S - 2. or elapsed >= WALL_S - 3.:
                    state["failure"] = "JOB_CLOSEOUT_RESOURCE_RESERVE_REACHED"
                receipt = {"job": job.id, "status": "complete" if state["failure"] is None else "blocked",
                    "command": list(job.argv), "returncode": process.returncode, "failure": state["failure"],
                    "cpu_s": used_cpu, "wall_s": elapsed, "cpu_affinity": [state["cpu_id"]],
                    "started_monotonic_s": state["started"], "terminal_monotonic_s": time.monotonic(),
                    "max_polled_process_tree_rss_bytes": state["max_rss"],
                    "completed_wait4_ru_maxrss_bytes": int(usage.ru_maxrss) * 1024,
                    "memory_scope": "50MS_POLLED_TREE_RSS_AND_WAIT4_PEAK; NOT_EXACT_AGGREGATE_PEAK",
                    "resource_scope": "GUARDIAN_AND_REAPED_DESCENDANTS_PLUS_PARENT_SETUP_AND_CLOSEOUT",
                    "limits": {"cpu_s": CPU_S, "wall_s": WALL_S, "per_process_as_bytes": MEMORY_BYTES},
                    "verdict": verdict, "guardian": guardian, "files_sha256": files}
                write_new(job.directory / "TERMINAL.json", receipt)
                results[job.id] = receipt
                if receipt["status"] == "complete":
                    completed[job.id] = receipt
                del active[pid]
                log_event(events, {"event": "job_terminal", "job": job.id, "status": receipt["status"],
                                   "receipt_sha256": sha(job.directory / "TERMINAL.json")})
            # A guardian hard exit may reparent unobserved/new-session work to
            # this subreaper. Abort the campaign and retain/clean all owned work.
            known = {state["procfs_pid"] for state in active.values() if state["procfs_pid"] is not None}
            for state in active.values():
                if state["procfs_pid"] is None:
                    state["procfs_pid"] = support.procfs_child_pid(state["process"].pid)
                    if state["procfs_pid"] is not None:
                        known.add(state["procfs_pid"])
            require(set(support.proc_children(own_procfs)).issubset(known), "UNEXPECTED_ADOPTED_JOB_DESCENDANT")
            require(prior_cpu + total_cpu() - start_cpu + live_cpu < campaign_cpu - RESERVE_CPU_S,
                    "CAMPAIGN_LIVE_PROCESS_TREE_CPU_CAP")
            if pending and not active and not choose_ready(pending, [], set(completed), live_capacity):
                for job in pending:
                    results[job.id] = {"status": "blocked", "reason": "DEPENDENCY_OR_CURRENT_RESOURCE_GATE"}
                break
            if active:
                time.sleep(.05)
    except BaseException as exc:
        failure = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        try:
            reaped = cleanup_children(own_procfs, support, time.monotonic() + 3.)
            for pid, status, _usage in reaped:
                if pid in active:
                    active[pid]["process"].returncode = os.waitstatus_to_exitcode(status)
        except Exception as exc:
            failure = {"type": type(exc).__name__, "message": str(exc)}
        for state in active.values():
            state["stdout"].close(); state["stderr"].close()
    return {"jobs": results, "failure": failure,
            "all_owned_descendants_reaped": not support.proc_children(own_procfs),
            "cumulative_cpu_s": prior_cpu + total_cpu() - start_cpu,
            "cumulative_wall_s": prior_wall + time.monotonic() - start_wall,
            "measurement_scope": "CALLER_CHARGED_PREFLIGHT_PLUS_EXECUTOR_AND_ALL_REAPED_DESCENDANTS"}


def matched_outputs(out):
    paths = [out / "jobs" / key / "run/worker" for key in ("h4_legacy16", "h4_numpy16")]
    files = ("native_oracle_stdout.csv", "python_partial_average_f64le.bin",
             "python_partial_virtual_f64le.bin", "python_partial_lyman_f64le.bin", "python_accepted_partial.jsonl")
    comparison = {name: [sha(path / name) for path in paths] for name in files}
    require(all(old == new for old, new in comparison.values()), "MATCHED_PILOT_RAW_BYTES_DIFFER")
    arrays = []
    for path in paths:
        with zipfile.ZipFile(path / "python_continuation.npz") as archive:
            require(len(archive.namelist()) == len(set(archive.namelist())), "DUPLICATE_NPZ_MEMBER")
            arrays.append({name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()})
    require(arrays[0] == arrays[1], "MATCHED_PILOT_NPY_MEMBER_BYTES_DIFFER")
    return {"status": "PASS_SCOPED", "raw_sha256_pairs": comparison, "npy_members_sha256": arrays[0],
            "scope": "SAME16_STEPS_RAW_AND_NPY_BYTES; NO_GLOBAL_CONVERGENCE_OR_PRODUCTION_APPROVAL"}


def main(argv=None):
    # Public execution uses absolute process CPU, including interpreter/module
    # initialization. Helper imports used by tests do not reset their caller.
    start_cpu = 0. if argv is None else total_cpu()
    start_wall = MODULE_ENTRY_WALL if argv is None else time.monotonic()
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--run", action="store_true")
    ap.add_argument("--expected-commit")
    ap.add_argument("--allocation-id")
    ap.add_argument("--expected-host")
    ap.add_argument("--cpu-ids")
    ap.add_argument("--host-intake", type=Path)
    ap.add_argument("--raw-dir", type=Path)
    ap.add_argument("--test-pythonpath", type=Path)
    ap.add_argument("--evidence-dir", type=Path)
    ap.add_argument("--campaign-cpu-seconds", type=float)
    ap.add_argument("--campaign-wall-seconds", type=float)
    ap.add_argument("--jobs", default=",".join(CATALOG))
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args(argv)
    limits = None
    if args.run:
        # Before source/input reads or project imports. --plan is read-only and
        # never changes the caller's limits, signal handlers or affinity.
        limits = install_lower_limits()
        require(args.campaign_wall_seconds is not None and math.isfinite(args.campaign_wall_seconds)
                and 0. < args.campaign_wall_seconds <= len(CATALOG) * WALL_S + RESERVE_WALL_S,
                "FINITE_EXPLICIT_CAMPAIGN_WALL_ALLOCATION_REQUIRED")
        prior_wall_hint = 0.
        if args.resume and args.evidence_dir:
            terminals = sorted(args.evidence_dir.glob("attempt_*.TERMINAL.json"))
            if terminals:
                _cpu_hint, prior_wall_hint = checked_costs(json.loads(terminals[-1].read_text()))
        arm_deadline(args.campaign_wall_seconds - prior_wall_hint - 3. - (time.monotonic() - start_wall))
    manifest = json.loads(MANIFEST.read_text())
    selected = selected_jobs(manifest["nodes"], args.jobs.split(","))
    expected_cpu = len(selected) * CPU_S + RESERVE_CPU_S
    expected_wall = len(selected) * WALL_S + RESERVE_WALL_S
    plan = {"schema": "rec.r3s.campaign-plan.v1", "status": "PLAN_ONLY_NO_EXECUTION",
        "selected": selected, "nodes": manifest["nodes"], "maximum_ready_correctness_width": 2,
        "timed_jobs_exclusive": True, "target_hardware": "64_CPU_128_GB_NOT_ASSUMED_OBSERVED",
        "required_campaign_cpu_s": expected_cpu, "required_campaign_wall_s": expected_wall,
        "per_job": {"cpu_s": CPU_S, "wall_s": WALL_S, "address_space_bytes": MEMORY_BYTES},
        "scientific_holds": manifest["scientific_holds"], "gate_errors": []}
    source = inputs = observation = None
    try:
        source = bind_source(args.expected_commit or git("rev-parse", "HEAD").decode().strip())
        plan["source"] = source
    except Exception as exc:
        plan["gate_errors"].append("SOURCE:" + str(exc))
    try:
        observation = hardware(); plan["hardware_observed"] = observation
    except Exception as exc:
        plan["gate_errors"].append("HARDWARE:" + str(exc))
    try:
        inputs = input_hashes(args.raw_dir, "saved_stream_benchmark" in selected)
    except Exception as exc:
        plan["gate_errors"].append("INPUT:" + str(exc))
    if not args.run:
        plan["run_prerequisites"] = ["fixed committed source", "fresh current-host REC result/session intake",
            "verified 64 CPU/128 GB host", "explicit available CPU IDs", "selected-job sum allocation",
            "full saved raw inputs when benchmark selected", "create-only evidence and allocation registry"]
        print(json.dumps(plan, sort_keys=True, indent=2, allow_nan=False))
        return 0
    require(not plan["gate_errors"], "PREFLIGHT_BLOCKED:" + ";".join(plan["gate_errors"]))
    require(args.expected_commit and args.evidence_dir and args.cpu_ids, "RUN_IDENTITY_OUTPUT_CPU_ASSIGNMENT_REQUIRED")
    require(re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", args.allocation_id or "") is not None
            and "CLOSED" not in args.allocation_id.upper(), "NEW_EXPLICIT_ALLOCATION_ID_REQUIRED")
    require(args.campaign_cpu_seconds == expected_cpu and args.campaign_wall_seconds == expected_wall,
            "EXACT_SELECTED_JOB_SUM_AND_RESERVE_ALLOCATION_REQUIRED")
    assigned = cpu_set(args.cpu_ids)
    capacity = validate_host(observation, args.expected_host, assigned)
    runtime = runtime_identity(args.test_pythonpath)
    require("numpy" in runtime["packages"], "NUMPY_RUNTIME_UNAVAILABLE")
    require(not set(selected).intersection(CASE_NAMES) or "pytest" in runtime["packages"], "PYTEST_RUNTIME_UNAVAILABLE")
    require(not any(key.startswith("h4_") for key in selected) or runtime["cc"] is not None,
            "PILOT_C_COMPILER_UNAVAILABLE")
    out = args.evidence_dir.resolve()
    require(not out.is_relative_to(ROOT), "CAMPAIGN_OUTPUT_MUST_BE_OUTSIDE_FIXED_REPOSITORY")
    header = {"source": source, "allocation_id": args.allocation_id, "selected": selected,
        "inputs": inputs, "environment": stable_environment(observation), "runtime": runtime, "assigned_cpu_ids": assigned,
        "campaign_cpu_s": expected_cpu, "campaign_wall_s": expected_wall,
        "per_job_limits": {"cpu_s": CPU_S, "wall_s": WALL_S, "per_process_as_bytes": MEMORY_BYTES},
        "scope": "NEW_PLATFORM_ONLY; COMPLETED_HISTORICAL_CAMPAIGNS_REUSED"}
    identity = {**header, "evidence_directory": str(out)}
    completed, blocked = {}, {}
    prior_cpu = prior_wall = 0.
    attempt = 1
    if args.resume:
        attempt, prior_cpu, prior_wall, completed, blocked = resume_records(out, header)
    # Only hash-verified completions from this exact source/input/host/allocation
    # may bypass duplicate rejection. They are omitted from the execution queue.
    intake = host_intake(args.host_intake, observation, args.expected_commit, selected, assigned, completed)
    require(prior_cpu + total_cpu() - start_cpu < expected_cpu - RESERVE_CPU_S
            and prior_wall + time.monotonic() - start_wall < expected_wall - RESERVE_WALL_S,
            "PRIOR_ALLOCATION_RESERVE_EXHAUSTED")
    allocation_claim(identity, args.resume)
    if not args.resume:
        out.mkdir(parents=True, exist_ok=False)
        (out / "jobs").mkdir()
        write_new(out / "CAMPAIGN.json", header)
    # The persistent host lock coordinates this R3S controller only. Other
    # research lanes remain under the explicitly observed CPU ownership gate.
    host_lock = ALLOCATION_REGISTRY / (hashlib.sha256(args.expected_host.encode()).hexdigest() + ".lock")
    with host_lock.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        prefix = out / f"attempt_{attempt:04d}"
        write_new(prefix.with_suffix(".STARTED.json"), {"allocation_id": args.allocation_id,
            "pid": os.getpid(), "prior_cpu_s": prior_cpu, "prior_wall_s": prior_wall,
            "source": source, "host": observation, "host_intake": intake, "controller_limits": limits,
            "campaign_attempt_started_monotonic_s": start_wall})
        log_event(out / "events.jsonl", {"event": "campaign_attempt_started", "attempt": attempt,
            "allocation_id": args.allocation_id, "started_monotonic_s": start_wall,
            "prior_cpu_s": prior_cpu, "prior_wall_s": prior_wall})
        env = os.environ.copy()
        env.update({name: "1" for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                                          "NUMEXPR_NUM_THREADS", "RAYON_NUM_THREADS", "PYTEST_DISABLE_PLUGIN_AUTOLOAD")})
        env.pop("PYTEST_ADDOPTS", None); env.pop("PYTEST_PLUGINS", None)
        env.pop("PYTHONPATH", None)
        if args.test_pythonpath:
            env["PYTHONPATH"] = str(args.test_pythonpath.resolve())
        jobs = [make_job(key, out / "jobs" / key, args.expected_commit, args.allocation_id, args.raw_dir)
                for key in selected if key not in completed and key not in blocked]
        sys.dont_write_bytecode = True
        cache = out / f"supervisor_pycache_{attempt:04d}"; cache.mkdir()
        sys.pycache_prefix = str(cache)
        arm_deadline(expected_wall - prior_wall - (time.monotonic() - start_wall) - 3.)
        result = execute_jobs(jobs, out, assigned, capacity, env, expected_cpu, expected_wall,
            prior_cpu + total_cpu() - start_cpu, prior_wall + time.monotonic() - start_wall, completed)
        result["complete_reused"] = sorted(completed)
        result["previous_failed_or_partial_jobs"] = blocked
        try:
            require(bind_source(args.expected_commit) == source, "FINAL_SOURCE_CHANGED")
            require(input_hashes(args.raw_dir, "saved_stream_benchmark" in selected) == inputs, "FINAL_INPUT_CHANGED")
            require(stable_environment(hardware()) == header["environment"], "FINAL_HOST_ENVIRONMENT_CHANGED")
            require(runtime_identity(args.test_pythonpath) == runtime, "FINAL_RUNTIME_IDENTITY_CHANGED")
            successful = set(completed) | {key for key, value in result["jobs"].items() if value["status"] == "complete"}
            if {"h4_legacy16", "h4_numpy16"}.issubset(successful):
                result["matched_pilots"] = matched_outputs(out)
            require(set(selected).issubset(successful) and result["failure"] is None
                    and result["all_owned_descendants_reaped"], "CAMPAIGN_INCOMPLETE_OR_BLOCKED")
            result["status"] = "COMPLETED_SCOPED"
        except Exception as exc:
            result["status"] = "HOLD"
            result["closeout_failure"] = {"type": type(exc).__name__, "message": str(exc)}
        result["scientific_holds"] = manifest["scientific_holds"]
        result["source"] = source
        result["allocation_id"] = args.allocation_id
        log_event(out / "events.jsonl", {"event": "campaign_attempt_terminal", "attempt": attempt,
            "status": result["status"], "started_monotonic_s": start_wall,
            "terminal_monotonic_s": time.monotonic()})
        try:
            result["files_sha256"] = file_hashes(out)
            result["file_hash_inventory_complete"] = True
        except BaseException as exc:
            result["status"] = "HOLD_FINAL_HASHING"
            result["file_hash_inventory_complete"] = False
            result["file_hashing_failure"] = {"type": type(exc).__name__, "message": str(exc)}
        # Include preflight, setup, subprocesses and the complete final hashing
        # pass. The final small receipt retains at least 2 CPU / 3 wall reserve.
        result["cumulative_cpu_s"] = prior_cpu + total_cpu() - start_cpu
        result["cumulative_wall_s"] = prior_wall + time.monotonic() - start_wall
        result["resource_scope"] = "PREFLIGHT_THROUGH_FINAL_FILE_HASHING; FINAL_RECEIPT_WRITE_RESERVED"
        result["receipt_reserve"] = {"cpu_s": 2., "wall_s": 3.}
        if result["cumulative_cpu_s"] >= expected_cpu - 2. or result["cumulative_wall_s"] >= expected_wall - 3.:
            result["status"] = "HOLD_RESOURCE_BUDGET"
        write_new(prefix.with_suffix(".TERMINAL.json"), result)
        signal.setitimer(signal.ITIMER_REAL, 0.)
        print(json.dumps({"status": result["status"], "receipt": str(prefix.with_suffix(".TERMINAL.json")),
                          "allocation_id": args.allocation_id}, sort_keys=True))
        return 0 if result["status"] == "COMPLETED_SCOPED" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"status": "BLOCKED", "type": type(error).__name__, "message": str(error)}), file=sys.stderr)
        raise SystemExit(2)

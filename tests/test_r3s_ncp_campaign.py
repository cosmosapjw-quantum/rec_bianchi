"""R3S orchestration contracts; no solver, numerical trace or timed benchmark.

Process-tree cases execute only short dummy programs in fresh, lower-limited
children. They do not change the long-lived pytest parent's resource limits,
subreaper state, signal handlers or process ownership.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_r3s_ncp_campaign as campaign


@pytest.fixture
def nodes():
    return json.loads(campaign.MANIFEST.read_text())["nodes"]


@pytest.mark.parametrize("inherited,cap,expected", [
    ((-1, -1), 60, (60, 60)), ((30, 60), 60, (30, 60)),
    ((10, 20), 60, (10, 20)), ((60, -1), 20, (20, 20)),
    ((0, -1), 60, (0, 60)), ((1024, 2048), 4096, (1024, 2048)),
])
def test_limits_only_lower(inherited, cap, expected):
    assert campaign.lower_pair(inherited, cap) == expected


@pytest.mark.parametrize("value", ["", "0-", "2-1", "0,,1", "-1", "0;echo", "65536"])
def test_cpu_assignment_rejects_malformed(value):
    with pytest.raises(ValueError):
        campaign.cpu_set(value)


def test_cpu_assignment_normalizes_duplicates():
    assert campaign.cpu_set("5,2-4,3") == [2, 3, 4, 5]


def test_cgroup_minimum_ancestor_quota_and_remaining_memory(tmp_path):
    parent, child = tmp_path / "cgroup", tmp_path / "cgroup/team/job"
    child.mkdir(parents=True)
    for path, cpu, maximum, current in [(parent, "200000 100000", 10_000, 4_000),
            (parent / "team", "max 100000", 8_000, 5_000), (child, "400000 100000", 20_000, 1_000)]:
        (path / "cpu.max").write_text(cpu)
        (path / "memory.max").write_text(str(maximum))
        (path / "memory.current").write_text(str(current))
    result = campaign.cgroup_limits(child, parent)
    assert result["cpu_quota_cores"] == 2.
    assert result["memory_remaining_bytes"] == 3_000
    assert len(result["ancestors"]) == 3


def test_cgroup_escape_rejected(tmp_path):
    with pytest.raises(ValueError, match="CGROUP_OUTSIDE_MOUNT"):
        campaign.cgroup_limits(tmp_path, tmp_path / "mount")


def test_cgroup_v1_is_not_treated_as_unlimited(monkeypatch):
    original = Path.read_text
    def read(path, *args, **kwargs):
        if str(path) == "/proc/meminfo":
            return "MemTotal: 134217728 kB\nMemAvailable: 120000000 kB\n"
        if str(path) == "/proc/self/cgroup":
            return "2:cpu,cpuacct:/limited\n3:memory:/limited\n"
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", read)
    with pytest.raises(ValueError, match="CGROUP_V1_OR_HYBRID"):
        campaign.hardware()


def host():
    return {"hostname": "verified-ncp", "logical_cpus": 64, "memory_total_bytes": 128_000_000_000,
            "affinity": [2, 3, 4, 5], "effective_cpu_slots": 4,
            "effective_memory_available_bytes": 20 * 1024**3}


@pytest.mark.parametrize("change,assigned,message", [
    ({"hostname": "other-device"}, [2], "IDENTITY"),
    ({"logical_cpus": 16}, [2], "TARGET_NOT_OBSERVED"),
    ({}, [0], "OUTSIDE_AFFINITY"),
    ({"effective_cpu_slots": 0}, [2], "NO_EFFECTIVE"),
    ({"effective_memory_available_bytes": 1024}, [2], "NO_EFFECTIVE"),
])
def test_host_target_and_actual_capacity_are_separate(change, assigned, message):
    with pytest.raises(ValueError, match=message):
        campaign.validate_host({**host(), **change}, "verified-ncp", assigned)


def test_memory_reserves_whole_active_allowances_without_rss_credit():
    observed = {**host(), "effective_memory_available_bytes": 5 * 1024**3}
    assert campaign.memory_capacity(observed, 2) == 1
    assert campaign.choose_ready([campaign.Job("b", (), Path("b"))],
        [campaign.Job("a", (), Path("a"))], set(), 1) == []


def test_fixed_catalogue_blocks_new_commands_and_changed_barriers(nodes, tmp_path):
    wrong = deepcopy(nodes)
    wrong.append({"id": "full5210", "status": "ready", "depends_on": []})
    with pytest.raises(ValueError, match="UNALLOWLISTED"):
        campaign.validate_dag(wrong)
    next(node for node in nodes if node["id"] == "saved_stream_benchmark")["exclusive"] = False
    with pytest.raises(ValueError, match="TIMING_BARRIER_CHANGED"):
        campaign.validate_dag(nodes)
    with pytest.raises(ValueError, match="UNALLOWLISTED_COMMAND"):
        campaign.make_job("full5210", tmp_path, "a" * 40, "allocation", None)


def test_cycle_and_duplicate_nodes_fail_closed():
    with pytest.raises(ValueError, match="DAG_CYCLE"):
        campaign.validate_dag([{"id": "a", "status": "blocked", "depends_on": ["b"]},
                               {"id": "b", "status": "blocked", "depends_on": ["a"]}])
    with pytest.raises(ValueError, match="DUPLICATE"):
        campaign.validate_dag([{"id": "a"}, {"id": "a"}])


def test_blocked_rust_does_not_block_numpy_frontier(nodes):
    selected = campaign.selected_jobs(nodes, ["h4_numpy16"])
    assert selected == ["trace_original", "trace_interleaved", "h4_legacy16", "h4_numpy16"]
    with pytest.raises(ValueError, match="NONEXECUTABLE"):
        campaign.selected_jobs(nodes, ["R3O_vigilode_platform_build"])


def test_timed_frontier_is_an_exclusive_barrier(tmp_path):
    ordinary = campaign.Job("ordinary", (), tmp_path)
    timed = campaign.Job("timed", (), tmp_path, (), True)
    assert campaign.choose_ready([ordinary, timed], [ordinary], set(), 64) == []
    assert campaign.choose_ready([ordinary, timed], [], set(), 64) == [timed]
    assert campaign.choose_ready([ordinary], [timed], set(), 64) == []
    dependent = campaign.Job("dependent", (), tmp_path, ("failed",))
    assert campaign.choose_ready([dependent], [], set(), 64) == []


def test_wrong_source_sha_fails_before_source_reads(monkeypatch):
    monkeypatch.setattr(campaign, "git", lambda *args: b"b" * 40 + b"\n")
    with pytest.raises(ValueError, match="SOURCE_HEAD_MISMATCH"):
        campaign.bind_source("a" * 40)


def test_plan_never_launches_jobs_or_changes_limits(nodes, tmp_path, monkeypatch, capsys):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"nodes": nodes, "scientific_holds": {"REI_activation": False}}))
    monkeypatch.setattr(campaign, "MANIFEST", manifest)
    monkeypatch.setattr(campaign, "bind_source", lambda sha: {"commit": sha})
    monkeypatch.setattr(campaign, "hardware", host)
    def forbidden(*args, **kwargs):
        raise AssertionError("plan attempted execution or mutation")
    monkeypatch.setattr(campaign.subprocess, "Popen", forbidden)
    monkeypatch.setattr(campaign.resource, "setrlimit", forbidden)
    monkeypatch.setattr(campaign, "execute_jobs", forbidden)
    assert campaign.main(["--plan", "--expected-commit", "a" * 40]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["status"] == "PLAN_ONLY_NO_EXECUTION"
    assert (plan["required_campaign_cpu_s"], plan["required_campaign_wall_s"]) == (305., 912.)


def test_caught_deadline_keeps_original_hard_end_and_cannot_rearm_reserve(monkeypatch):
    clock, handlers, timers = [100.], {}, []
    monkeypatch.setattr(campaign.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(campaign.signal, "getitimer", lambda kind: (8., 0.))
    monkeypatch.setattr(campaign.signal, "signal", lambda kind, handler: handlers.__setitem__(kind, handler))
    monkeypatch.setattr(campaign.signal, "setitimer", lambda kind, value: timers.append((kind, value)))
    deadline = campaign.arm_deadline(10.)
    assert (deadline.work_end, deadline.hard_end) == (105., 108.)
    clock[0] = 105.
    with pytest.raises(TimeoutError):
        handlers[campaign.signal.SIGALRM](campaign.signal.SIGALRM, None)
    assert deadline.exhausted
    assert handlers[campaign.signal.SIGALRM] == campaign.signal.SIG_DFL
    assert timers[-1] == (campaign.signal.ITIMER_REAL, 3.)
    old_timers = list(timers)
    clock[0] = 106.
    with pytest.raises(TimeoutError):
        campaign.arm_deadline(1000., deadline)
    assert deadline.hard_end == 108. and timers == old_timers


def test_timeout_in_final_identity_skips_all_later_optional_work(monkeypatch):
    clock, handlers, timers, called = [100.], {}, [], []
    monkeypatch.setattr(campaign.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(campaign.signal, "getitimer", lambda kind: (0., 0.))
    monkeypatch.setattr(campaign.signal, "signal", lambda kind, handler: handlers.__setitem__(kind, handler))
    monkeypatch.setattr(campaign.signal, "setitimer", lambda kind, value: timers.append((kind, value)))
    deadline = campaign.arm_deadline(10.)
    def interrupted_identity():
        called.append("identity_started")
        clock[0] = 110.
        deadline.expired()
    # A broad closeout handler can catch the first exception, but the durable
    # gate must reject every subsequent expensive callback before it starts.
    try:
        campaign.before_deadline(deadline, interrupted_identity)
    except Exception:
        pass
    for name in ("bind_source", "input_hashes", "runtime_identity", "matched_outputs", "full_file_hashes"):
        with pytest.raises(TimeoutError):
            campaign.before_deadline(deadline, lambda label=name: called.append(label))
    assert called == ["identity_started"]
    assert deadline.exhausted and deadline.hard_end == 113.
    assert handlers[campaign.signal.SIGALRM] == campaign.signal.SIG_DFL
    assert timers[-1] == (campaign.signal.ITIMER_REAL, 3.)


def test_allocation_id_cannot_move_to_fresh_output(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign, "ALLOCATION_REGISTRY", tmp_path / "registry")
    identity = {"allocation_id": "new-platform-001", "evidence_directory": str(tmp_path / "one")}
    campaign.allocation_claim(identity, False)
    with pytest.raises(ValueError, match="ALLOCATION_ALREADY_RESERVED"):
        campaign.allocation_claim({**identity, "evidence_directory": str(tmp_path / "two")}, False)
    with pytest.raises(ValueError, match="REGISTRY_IDENTITY"):
        campaign.allocation_claim({**identity, "evidence_directory": str(tmp_path / "two")}, True)
    campaign.allocation_claim(identity, True)


@pytest.mark.parametrize("values", [(float("nan"), 2.), (2., float("inf")), (-1., 2.), (True, 2.)])
def test_resume_nonfinite_or_negative_cost_is_rejected(values):
    with pytest.raises(ValueError, match="INVALID_PRIOR_RESOURCE_COST"):
        campaign.checked_costs(dict(zip(("cumulative_cpu_s", "cumulative_wall_s"), values)))


def test_resume_cost_must_be_monotone():
    with pytest.raises(ValueError, match="NONMONOTONE"):
        campaign.checked_costs({"cumulative_cpu_s": 1., "cumulative_wall_s": 3.}, (2., 2.))


def test_resume_host_cpu_budget_and_unclosed_attempt_are_gates(tmp_path):
    header = {"source": {"commit": "a" * 40}, "allocation_id": "one", "selected": [],
        "environment": {"hostname": "ncp"}, "assigned_cpu_ids": [2, 3], "campaign_cpu_s": 125.}
    campaign.write_new(tmp_path / "CAMPAIGN.json", header)
    for key, value in [("environment", {"hostname": "other"}), ("assigned_cpu_ids", [3, 4]),
                       ("campaign_cpu_s", 180.)]:
        with pytest.raises(ValueError, match="RESUME_IDENTITY"):
            campaign.resume_records(tmp_path, {**header, key: value})
    campaign.write_new(tmp_path / "attempt_0001.STARTED.json", {})
    with pytest.raises(ValueError, match="UNCLOSED"):
        campaign.resume_records(tmp_path, header)


def test_resume_reuses_completed_output_and_rejects_tamper(tmp_path):
    header = {"source": {"commit": "a" * 40}, "allocation_id": "one", "selected": ["trace_original"]}
    campaign.write_new(tmp_path / "CAMPAIGN.json", header)
    path = tmp_path / "jobs/trace_original"; path.mkdir(parents=True)
    (path / "raw.json").write_text('{"passed": true}\n')
    campaign.write_new(path / "TERMINAL.json", {"job": "trace_original", "status": "complete",
        "files_sha256": {"raw.json": campaign.sha(path / "raw.json")}})
    assert "trace_original" in campaign.resume_records(tmp_path, header)[3]
    (path / "raw.json").write_text('{"passed": false}\n')
    with pytest.raises(ValueError, match="OUTPUT_HASH"):
        campaign.resume_records(tmp_path, header)


def test_host_intake_allows_only_verified_same_campaign_resume_completion(tmp_path, monkeypatch):
    raw = tmp_path / "host_inventory.json"; raw.write_text('{"observed": true}\n')
    receipt = tmp_path / "intake.json"
    receipt.write_text(json.dumps({"schema": "rec.r3s.current-host-intake.v1", "hostname": "verified-ncp",
        "source_commit": "a" * 40, "observed_unix_s": 1000., "assigned_cpu_ids": [2, 3],
        "examined_job_ids": ["trace_original", "trace_interleaved"],
        "matching_completed_job_ids": ["trace_original"], "busy_cpu_ids": [],
        "inventory_files_sha256": {str(raw): campaign.sha(raw)}}))
    monkeypatch.setattr(campaign.time, "time", lambda: 1001.)
    selected = ["trace_original", "trace_interleaved"]
    with pytest.raises(ValueError, match="MUST_BE_REUSED"):
        campaign.host_intake(receipt, host(), "a" * 40, selected, [2, 3])
    assert campaign.host_intake(receipt, host(), "a" * 40, selected, [2, 3],
                                {"trace_original"})["sha256"] == campaign.sha(receipt)


def test_namespace_mapping_selects_callers_level():
    own = "Pid:\t12345\nNSpid:\t12345\t77\n"
    child = "Pid:\t20000\nNSpid:\t20000\t321\t1\n"
    assert campaign.local_signal_pid(20000, own, child, 77) == 321
    with pytest.raises(ValueError, match="MAPPING_MISMATCH"):
        campaign.local_signal_pid(20000, own, "NSpid:\t20000\n", 77)


def test_pidfd_signal_remains_bound_after_numeric_pid_reuse(monkeypatch):
    sent, closed = [], []
    monkeypatch.setattr(campaign, "procfd_stat", lambda fd: ["S", "123"])
    monkeypatch.setattr(campaign.signal, "pidfd_send_signal", lambda fd, sig, info, flags: sent.append((fd, sig)))
    monkeypatch.setattr(campaign.os, "close", closed.append)
    monkeypatch.setattr(campaign.os, "kill", lambda *args: pytest.fail("numeric PID signal is forbidden"))
    # The numerical ID is intentionally unrelated; signaling uses only the
    # already-open stable descriptor and its bound parent identity.
    campaign.kill_snapshot([(91, 999999, 123)])
    assert sent == [(91, campaign.signal.SIGKILL)] and closed == [91]


def test_all_tid_children_are_visible(tmp_path):
    for tid, children in [(100, "201\n"), (101, "202 201\n")]:
        task = tmp_path / f"100/task/{tid}"; task.mkdir(parents=True)
        (task / "children").write_text(children)
    assert campaign.proc_children(100, tmp_path) == [201, 202]


def test_missing_task_interface_uses_ppid_scan(tmp_path):
    path = tmp_path / "202"; path.mkdir()
    (path / "stat").write_text("202 (child) S 100 0 0\n")
    assert campaign.proc_children(100, tmp_path) == [202]


DUMMY_DRIVER = r'''
import resource, signal, sys, time
for kind, cap in ((resource.RLIMIT_CPU, 60), (resource.RLIMIT_AS, 2*1024**3)):
    soft, hard = resource.getrlimit(kind)
    hard = cap if hard == resource.RLIM_INFINITY else min(hard, cap)
    soft = hard if soft == resource.RLIM_INFINITY else min(soft, hard)
    resource.setrlimit(kind, (soft, hard))
def timeout(_signal, _frame):
    raise TimeoutError("R3S_DUMMY_DRIVER_WALL_CAP")
signal.signal(signal.SIGALRM, timeout); signal.setitimer(signal.ITIMER_REAL, 168.)
import hashlib, json, os
from pathlib import Path
request = json.loads(sys.argv[1]); root = Path(request["root"])
assert hashlib.sha256((root/"scripts/run_r3s_ncp_campaign.py").read_bytes()).hexdigest() == request["source_sha256"]
sys.path.insert(0, str(root/"scripts"))
import run_r3s_ncp_campaign as c
out = Path(request["out"]); out.mkdir()
assigned = sorted(os.sched_getaffinity(0))[:2]
assert len(assigned) == 2, "DUMMY_CONCURRENCY_REQUIRES_TWO_AVAILABLE_AFFINITY_IDS"
c.hardware = lambda: {"effective_memory_available_bytes": 16*1024**3, "effective_cpu_slots": 2}
scenario = request["scenario"]
def job(name, code, depends=(), exclusive=False):
    return c.Job(name, (sys.executable, "-B", "-c", code), out/name, depends, exclusive)
if scenario == "parallel_and_barrier":
    jobs = [job("a", "import time; time.sleep(.2)"), job("b", "import time; time.sleep(.2)"),
            job("timed", "import time; time.sleep(.05)", ("a", "b"), True)]
elif scenario == "leader_leaves_new_session":
    code = "import subprocess,sys; subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(5)'],start_new_session=True)"
    jobs = [job("orphan", code)]
else:
    code = "import subprocess,sys,os,signal,time; subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(5)'],start_new_session=True); os.kill(os.getppid(),signal.SIGKILL); time.sleep(5)"
    jobs = [job("guardian_killed", code)]
result = c.execute_jobs(jobs,out,assigned,2,os.environ.copy(),60.,180.)
assert hashlib.sha256((root/"scripts/run_r3s_ncp_campaign.py").read_bytes()).hexdigest() == request["source_sha256"]
result["source_sha256"] = request["source_sha256"]
result["events"] = [json.loads(line) for line in (out/"events.jsonl").read_text().splitlines()]
result["new_solver_integrations"] = 0; result["timed_scientific_benchmark_trials"] = 0
signal.setitimer(signal.ITIMER_REAL, 0.)
print(json.dumps(result,sort_keys=True))
'''


@pytest.mark.parametrize("scenario", ["parallel_and_barrier", "leader_leaves_new_session", "guardian_killed"])
def test_actual_dummy_process_ownership_in_fresh_child(scenario, tmp_path):
    cache = tmp_path / "fresh-cache"; cache.mkdir()
    source_sha = hashlib.sha256(Path(campaign.__file__).read_bytes()).hexdigest()
    request = {"root": str(ROOT), "out": str(tmp_path / "run"), "scenario": scenario, "source_sha256": source_sha}
    before = (resource.getrlimit(resource.RLIMIT_CPU), resource.getrlimit(resource.RLIMIT_AS))
    command = [sys.executable, "-B", "-X", "pycache_prefix=" + str(cache), "-c", DUMMY_DRIVER,
               json.dumps(request, sort_keys=True)]
    stdout, stderr = tmp_path / "driver.stdout.json", tmp_path / "driver.stderr.log"
    with stdout.open("xb") as out, stderr.open("xb") as err:
        done = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err, timeout=175, check=False)
    assert done.returncode == 0, (done.returncode, stderr.read_text(), stdout.read_text())
    assert stderr.read_bytes() == b""
    assert before == (resource.getrlimit(resource.RLIMIT_CPU), resource.getrlimit(resource.RLIMIT_AS))
    result = json.loads(stdout.read_text())
    assert result["all_owned_descendants_reaped"] is True
    assert result["cumulative_cpu_s"] < 58. and result["cumulative_wall_s"] < 177.
    assert result["source_sha256"] == source_sha
    if scenario == "parallel_and_barrier":
        assert result["failure"] is None
        assert all(job["status"] == "complete" for job in result["jobs"].values())
        events = result["events"]
        first_terminal = next(i for i, event in enumerate(events) if event["event"] == "job_terminal")
        assert {event["job"] for event in events[:first_terminal] if event["event"] == "job_started"} == {"a", "b"}
        timed_start = next(event["monotonic_s"] for event in events if event["event"] == "job_started" and event["job"] == "timed")
        assert all(event["monotonic_s"] < timed_start for event in events if event["event"] == "job_terminal" and event["job"] in ("a", "b"))
    else:
        assert any(job["status"] == "blocked" for job in result["jobs"].values()) or result["failure"] is not None

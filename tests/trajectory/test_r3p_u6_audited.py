"""Cheap runner contracts with synthetic files and fake numerical collaborators.

No integration, archive extraction, compiler, native library, benchmark, git
mutation, or resource-limit change is executed by these tests.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import run_r3p_u6_audited as runner
import r3p_stream_audit as scalar
import r3p_rust_audit as rust_adapter
import run_r3p_u6_supervised as supervisor
from run_r3j_u6_owned import EXTRA_FILES as OWNER_FILES


def put(root, name, value=b"synthetic source fixture\n"):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)
    return path


def sha(value):
    return hashlib.sha256(value).hexdigest()


@pytest.fixture
def tree(tmp_path, monkeypatch):
    root = tmp_path / "checkout"
    names = set(OWNER_FILES) | set(runner.profiled.EXTRA_FILES) | set(runner.EXTRA_FILES)
    names |= set(runner.BUILD_FILES) | {f"{runner.CRATE}/src/lib.rs", f"{runner.CRATE}/src/tests.rs"}
    for name in names:
        put(root, name)
    vendor = put(root, runner.VENDOR_ARCHIVE, b"synthetic vendor archive; never extracted")
    put(root, runner.VENDOR_META, json.dumps({
        "schema": "rec.r3p.registry-vendor.v1", "file": runner.VENDOR_ARCHIVE,
        "sha256": runner.file_sha256(vendor), "bytes": vendor.stat().st_size,
        "cargo_lock_sha256": runner.file_sha256(root / runner.CRATE / "Cargo.lock"),
    }).encode())
    checkpoint = put(tmp_path, "original-u5.npz", b"synthetic checkpoint; never loaded")
    archive = put(root, runner.SOURCE_ZIP, b"synthetic source ZIP; never extracted")
    monkeypatch.setattr(runner, "CHECKPOINT_SHA256", runner.file_sha256(checkpoint))
    monkeypatch.setattr(runner, "SOURCE_ZIP_SHA256", runner.file_sha256(archive))
    frozen_files = {runner.FROZEN_CONTRACT, runner.SOURCE_ZIP}
    frozen_files |= {f"restored_extra_files/dependency_{i}.bin" for i in range(107)}
    for name in frozen_files - {runner.SOURCE_ZIP}:
        put(root, name)
    manifest = {"node": "H2_U6_RT_BOUNDARY", "checkpoint_sha256": runner.CHECKPOINT_SHA256,
                "files": {name: runner.file_sha256(root / name) for name in sorted(frozen_files)}}
    manifest_path = put(root, runner.FROZEN_MANIFEST, json.dumps(manifest).encode())
    monkeypatch.setattr(runner, "FROZEN_MANIFEST_SHA256", runner.file_sha256(manifest_path))
    state = SimpleNamespace(root=root, checkpoint=checkpoint, archive=archive,
                            head="a"*40, dirty=False, untracked=set(), git_calls=[])

    def git(command, **kwargs):
        assert command[:3] == ["git", "-C", str(root)]
        state.git_calls.append(command[3:])
        args = command[3:]
        if args == ["rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(command, 0, state.head + "\n", "")
        if args == ["diff", "--quiet", "HEAD", "--"]:
            if state.dirty:
                raise subprocess.CalledProcessError(1, command)
        elif args[:3] == ["ls-files", "--error-unmatch", "--"]:
            if state.untracked.intersection(args[3:]):
                raise subprocess.CalledProcessError(1, command)
        else:
            raise AssertionError(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(runner.subprocess, "run", git)
    state.binding = runner.bind_audited_source(root, state.head)
    library = put(tmp_path, "libsynthetic.so", b"not executable; never loaded")
    state.build_record = {"schema": "rec.r3p.audit-build.v1", "status": "BUILT",
        "exit_code": 0, "new_physical_runs": 0,
        "source_sha256": state.binding["rust_build_source_sha256"],
        "vendor_sha256": state.binding["vendor"]["sha256"],
        "library": str(library), "library_sha256": runner.file_sha256(library)}
    state.build = put(tmp_path, "build.json", json.dumps(state.build_record).encode())
    return state


def cli():
    return ["--checkpoint", "u5.npz", "--evidence-dir", "new-evidence",
            "--expected-commit", "a"*40, "--new-allocation-id", "bounded-smoke-001"]


def test_cli_defaults_and_boundaries():
    args = runner.parse_args(cli())
    assert (args.mode, args.steps, args.audit_backend, args.build) == ("smoke", 16, "cached", None)
    assert args.history_container == "stored"
    assert args.source_zip == runner.ROOT / runner.SOURCE_ZIP
    assert runner.step_count("pilot", 1) == 1
    assert runner.step_count("pilot", 128) == 128
    args = runner.parse_args(cli() + ["--audit-backend", "rust", "--build", "build.json",
                                     "--mode", "pilot", "--pilot-steps", "128"])
    assert args.steps == 128 and args.build == Path("build.json")


@pytest.mark.parametrize("options", [
    ["--mode", "full"], ["--pilot-steps", "0"], ["--pilot-steps", "129"],
    ["--audit-backend", "rust"], ["--build", "build.json"],
    ["--block-columns", "65"], ["--block-columns", "0"],
    ["--expected-commit", "HEAD"], ["--new-allocation-id", "bad/id"],
    ["--h", "0.0001"], ["--threads", "4"],
])
def test_cli_rejects_unbounded_or_incomplete_options(options):
    with pytest.raises(SystemExit) as exc:
        runner.parse_args(cli() + options)
    assert exc.value.code == 2


@pytest.mark.parametrize("steps", [True, 0, -1, 129, 5210, 1.5])
def test_programmatic_execution_cannot_bypass_step_bound(steps):
    with pytest.raises(ValueError, match="R3P_STEPS_1_TO_128"):
        runner.validate_options(steps=steps, backend="cached", build=None,
                                block_columns=32, allocation_id="test", container="stored")


def test_binding_covers_old_extras_new_sources_vendor_and_frozen_manifest(tree):
    binding = tree.binding
    expected = (set(OWNER_FILES) | set(runner.profiled.EXTRA_FILES) | set(runner.EXTRA_FILES)
                | set(binding["rust_build_source_sha256"]) | {runner.VENDOR_ARCHIVE, runner.FROZEN_MANIFEST})
    assert set(binding["additional_source_sha256"]) == expected
    tracked = set(tree.git_calls[-1][3:])
    assert tracked == expected
    assert not any(name.startswith("restored_extra_files/") for name in tracked)
    assert binding["frozen_v6"]["source_files"] == 109
    assert binding["frozen_v6"]["contract_sha256"] == runner.file_sha256(tree.root / runner.FROZEN_CONTRACT)


@pytest.mark.parametrize("fault", ["commit", "dirty", "untracked", "manifest", "vendor", "lock"])
def test_source_binding_rejects_changed_or_unpublished_inputs(tree, fault):
    expected_commit = tree.head
    if fault == "commit":
        expected_commit = "b"*40
    elif fault == "dirty":
        tree.dirty = True
    elif fault == "untracked":
        tree.untracked.add("scripts/run_r3p_u6_audited.py")
    elif fault == "manifest":
        (tree.root / runner.FROZEN_MANIFEST).write_bytes(b"{}")
    elif fault == "vendor":
        (tree.root / runner.VENDOR_ARCHIVE).write_bytes(b"changed")
    else:
        (tree.root / runner.CRATE / "Cargo.lock").write_bytes(b"changed")
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        runner.bind_audited_source(tree.root, expected_commit)


def test_external_source_zip_preserves_every_frozen_dependency(tree, tmp_path):
    external = put(tmp_path, "elsewhere/HyRec.zip", tree.archive.read_bytes())
    tree.archive.unlink()
    result = runner.verify_frozen_closure(tree.root, tree.checkpoint, external)
    assert result == {"manifest_sha256": runner.FROZEN_MANIFEST_SHA256,
                      "source_files": 109, "checkpoint_sha256": runner.CHECKPOINT_SHA256}
    missing = "restored_extra_files/dependency_37.bin"
    (tree.root / missing).unlink()
    with pytest.raises(ValueError, match=f"U6_SOURCE_CLOSURE:{missing}"):
        runner.verify_frozen_closure(tree.root, tree.checkpoint, external)


@pytest.mark.parametrize("fault,label", [("checkpoint", "U6_CHECKPOINT_SHA"),
    ("archive", "SOURCE_ZIP_SHA_MISMATCH"), ("contract", "U6_SOURCE_CLOSURE")])
def test_original_inputs_and_frozen_contract_cannot_be_replaced(tree, fault, label):
    path = tree.root / runner.FROZEN_CONTRACT if fault == "contract" else getattr(tree, fault)
    path.write_bytes(b"different input")
    with pytest.raises((ValueError, RuntimeError), match=label):
        runner.verify_frozen_closure(tree.root, tree.checkpoint, tree.archive)


def test_successful_build_is_hash_verified_without_loading_or_compiling(tree):
    result = runner.verify_build_receipt(tree.build, tree.binding, tree.root)
    assert result["library"] == tree.build_record["library"]
    assert result["receipt_sha256"] == runner.file_sha256(tree.build)
    assert result["vendor_sha256"] == tree.binding["vendor"]["sha256"]


@pytest.mark.parametrize("fault", ["schema", "status", "exit", "physical", "missing_source",
    "extra_source", "source_mutation", "vendor_receipt", "library_mutation", "resource_failure"])
def test_build_receipt_requires_complete_matching_successful_identity(tree, fault):
    record = dict(tree.build_record)
    if fault == "schema": record["schema"] = "unrelated"
    elif fault == "status": record["status"] = "FAILED"
    elif fault == "exit": record["exit_code"] = 2
    elif fault == "physical": record["new_physical_runs"] = 1
    elif fault == "missing_source": record["source_sha256"] = {}
    elif fault == "extra_source": record["source_sha256"] = {**record["source_sha256"], "../unbound.py": "0"*64}
    elif fault == "source_mutation": (tree.root / runner.CRATE / "src/lib.rs").write_bytes(b"mutated")
    elif fault == "vendor_receipt": record["vendor_sha256"] = "0"*64
    elif fault == "library_mutation": Path(record["library"]).write_bytes(b"mutated")
    elif fault == "resource_failure": record["resource_failure"] = "over budget"
    tree.build.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="R3P_BUILD"):
        runner.verify_build_receipt(tree.build, tree.binding, tree.root)


def fake_verifier(root):
    v = SimpleNamespace(ROOT=root, CPU_CAP=60, WALL_CAP=180, np=np,
                        CHECKPOINT_SHA256=runner.CHECKPOINT_SHA256, START_IZ=53179,
                        RT_IZ=36446, PREFIX_COLUMNS=16733, MAX_EXTRA_ACCEPTED=5210)
    for name in ("verify_source_closure", "load_frozen_checkpoint", "safe_extract_source",
                 "make_hmla_source", "CombinedOracle", "compare_native_stream",
                 "check_one_source", "causal_link_count", "_run", "integrate_u6_rt_boundary"):
        setattr(v, name, lambda *args, **kwargs: None)
    v.OriginalHyRecPrimitiveRateTable = SimpleNamespace(from_archive=lambda path: path)
    return v


@pytest.fixture
def launch(tree, tmp_path, monkeypatch):
    v = fake_verifier(tree.root)
    ev = tmp_path / "run"
    state = SimpleNamespace(verifier=v, evidence=ev, events=[], result={"status": "PASS_PENDING_REVIEW"},
                            error=None, mutate=None, close_error=None, prefix=None)
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda pid: {4})
    # R3L's runtime metadata may otherwise invoke uname through subprocess;
    # this fixture deliberately permits only the read-only git protocol fake.
    monkeypatch.setattr(runner.profiled.platform, "platform", lambda: "synthetic runner test platform")

    class Prefix:
        def __init__(self, library, *, threads, block_columns):
            assert state.events[-1] == "audit"
            assert library == tree.build_record["library"]
            assert threads == 1 and block_columns == 32
            state.events.append("pool_created")
            state.prefix = self
            self.stats = {"calls": 1, "threads": threads, "block_columns": block_columns}

        def close(self):
            state.events.append("pool_closed")
            if state.close_error:
                raise state.close_error

    def compare(*args, **kwargs):
        state.events.append(("compare", kwargs))
        if state.error:
            raise state.error
        return state.result

    monkeypatch.setattr(rust_adapter, "PrefixAuditor", Prefix)
    monkeypatch.setattr(scalar, "compare_native_stream", compare)
    monkeypatch.setattr(scalar, "causal_link_count", lambda table, j: 313)
    v.safe_extract_source = lambda archive, dest: state.events.append(("extract", archive))

    def owner(*args, **kwargs):
        assert kwargs == {"max_extra_accepted": 16, "max_full_evaluations": 16}
        state.events.append("owned_integrator")

    def main():
        assert sys.argv[-2:] == ["--max-extra-accepted", "16"]
        ev.mkdir()
        (ev / "python_accepted_partial.jsonl").write_text("synthetic partial evidence\n")
        assert v.verify_source_closure(tree.checkpoint)["source_files"] == 109
        v.safe_extract_source(tree.root / runner.SOURCE_ZIP, ev / "extract")
        assert v.OriginalHyRecPrimitiveRateTable.from_archive(tree.root / runner.SOURCE_ZIP) == tree.archive.resolve()
        v.integrate_u6_rt_boundary("checkpoint", "cosmology", "source",
                                  max_extra_accepted=16, max_full_evaluations=16)
        assert v.causal_link_count(None, 16733) == 313
        state.events.append("audit")
        try:
            result = v.compare_native_stream("no real stream")
        except BaseException:
            (ev / "verification.json").write_text(json.dumps({"status": "FAIL"}))
            raise
        assert result is state.result
        (ev / "verification.json").write_text(json.dumps({"status": "SMOKE_ONLY",
            "python_result": {"steps": 16}, "same_h_parity": result}))
        if state.mutate:
            state.mutate()

    v.main = main
    state.original_bindings = vars(v).copy()
    state.original_argv = sys.argv[:]

    def run(backend="cached"):
        return runner.execute(v, owner, checkpoint=tree.checkpoint, source_zip=tree.archive,
                              evidence=ev, steps=16, binding=tree.binding, allocation_id="test-smoke",
                              backend=backend, build=tree.build if backend == "rust" else None)

    state.run = run
    return state


@pytest.mark.parametrize("backend", ["cached", "rust"])
def test_reuses_profiled_owner_and_restores_bindings_with_durable_receipts(launch, tree, backend):
    result = launch.run(backend)
    assert result["execution_status"] == "returned"
    assert result["identity_status"] == "UNCHANGED"
    assert result["verification"]["status"] == "SMOKE_ONLY"
    assert result["full_run_admission"] == "UNAVAILABLE_SMOKE_PILOT_ONLY"
    assert result["dlna"] == 4.245e-5 and result["REI_activation"] is False
    assert result["historical_status"] == {"h_U5": "HOLD_9_FAIL", "h2_U5": "HOLD_8_FAIL",
                                            "allocation": "CLOSED_HOLD_NOT_RESET"}
    assert result["limits_scope"] == "INNER_FROZEN_VERIFIER_REQUESTED_LIMITS_CLAMPED_TO_INHERITED_LIMITS"
    assert "PROGRAMMATIC_EXECUTE_IS_WORKER_ONLY" in result["whole_launch_budget_scope"]
    assert vars(launch.verifier) == launch.original_bindings
    assert sys.argv == launch.original_argv
    profile = json.loads((launch.evidence.parent / "run.r3l_profile.json").read_text())
    rows = [json.loads(line) for line in (launch.evidence.parent / "run.r3l_phases.jsonl").read_text().splitlines()]
    assert rows[0]["source"]["r3p_inputs"] == result["inputs_before"]
    assert rows[0]["source"]["r3p_audit"]["backend"] == backend
    assert profile["requested_steps"] == 16
    assert {"owned_integration", "native_stream_validation", "causal_link_count"} <= set(profile["timings"]["phases"])
    assert json.loads((launch.evidence.parent / "run.r3p_execution.json").read_text()) == result
    call = next(event for event in launch.events if isinstance(event, tuple) and event[0] == "compare")
    if backend == "rust":
        assert call[1] == {"prefix_auditor": launch.prefix}
        assert launch.events.index("pool_created") > launch.events.index("owned_integrator")
        assert launch.events[-1] == "pool_closed"
        assert result["audit_statistics"]["prefix"]["threads"] == 1
        contract = result["audit"]["input_contract"]
        assert contract["grammar"] == "EXACTLY_FOUR_ASCII_COMMA_SEPARATED_FIELDS_PV_OR_PL"
        assert contract["temperature_and_energy"] == "FINITE_AND_STRICTLY_POSITIVE"
        assert contract["tolerance"] == "FINITE" and contract["stricter_than_legacy"] is True
        assert contract["earliest_logical_failure"] == "WITHIN_THE_BOUNDED_BLOCK_DELIVERED_TO_RUST_ONLY"
        assert "RESOURCE_TRANSPORT_SIZE_AND_GUARD_ABORTS" in contract["abort_priority"]
    else:
        assert call[1] == {} and launch.prefix is None


@pytest.mark.parametrize("error", [SystemExit(2), KeyboardInterrupt(), ArithmeticError("first numerical failure")])
def test_first_failure_partial_bytes_and_all_bindings_survive(launch, error):
    launch.error = error
    with pytest.raises(type(error)) as caught:
        launch.run()
    assert caught.value is error
    assert vars(launch.verifier) == launch.original_bindings and sys.argv == launch.original_argv
    assert (launch.evidence / "python_accepted_partial.jsonl").read_text() == "synthetic partial evidence\n"
    result = json.loads((launch.evidence.parent / "run.r3p_execution.json").read_text())
    assert result["execution_status"] == "failed" and result["first_failure"]["type"] == type(error).__name__
    assert (launch.evidence.parent / "run.r3l_profile.json").is_file()


def test_rust_close_failure_does_not_replace_first_numerical_failure(launch):
    launch.error = ArithmeticError("first numerical failure")
    launch.close_error = RuntimeError("close failed")
    with pytest.raises(ArithmeticError) as caught:
        launch.run("rust")
    assert caught.value is launch.error
    assert "pool_closed" in launch.events
    assert any("Secondary Rust prefix close failure" in note for note in caught.value.__notes__)
    assert vars(launch.verifier) == launch.original_bindings


def test_rust_pool_refuses_broader_affinity_without_instantiating(launch, monkeypatch):
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda pid: {4, 5})
    with pytest.raises(ValueError, match="FROZEN_SINGLE_CPU_AFFINITY"):
        launch.run("rust")
    assert launch.prefix is None
    assert vars(launch.verifier) == launch.original_bindings


@pytest.mark.parametrize("fault", ["checkpoint", "source", "build"])
def test_closeout_identity_mutation_fails_without_promoting_verifier_status(launch, tree, fault):
    if fault == "checkpoint":
        launch.mutate = lambda: tree.checkpoint.write_bytes(b"mutated")
    elif fault == "source":
        launch.mutate = lambda: setattr(tree, "dirty", True)
    else:
        launch.mutate = lambda: tree.build.write_text(tree.build.read_text() + " ")
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        launch.run("rust" if fault == "build" else "cached")
    result = json.loads((launch.evidence.parent / "run.r3p_execution.json").read_text())
    assert result["execution_status"] == "failed"
    assert result["verification"]["status"] == "SMOKE_ONLY"
    assert vars(launch.verifier) == launch.original_bindings


@pytest.mark.parametrize("suffix", ["", ".r3p_execution.json", ".r3l_profile.json", ".r3l_phases.jsonl"])
def test_create_only_refuses_existing_artifacts_before_any_call(launch, suffix):
    path = launch.evidence.parent / (launch.evidence.name + suffix)
    path.write_bytes(b"preserve")
    with pytest.raises(FileExistsError, match="CREATE_ONLY"):
        launch.run()
    assert path.read_bytes() == b"preserve" and launch.events == []


def test_receipt_save_error_preserves_original_failure_and_profile(launch, monkeypatch):
    launch.error = SystemExit(2)

    def unavailable(*args):
        raise OSError("receipt disk error")

    monkeypatch.setattr(runner, "dump_new", unavailable)
    with pytest.raises(SystemExit) as caught:
        launch.run()
    assert caught.value is launch.error
    assert any("runner_receipt_save" in note for note in caught.value.__notes__)
    assert (launch.evidence.parent / "run.r3l_profile.json").is_file()
    assert vars(launch.verifier) == launch.original_bindings


@pytest.mark.parametrize("field,value", [("CPU_CAP", 61), ("WALL_CAP", 181),
    ("CHECKPOINT_SHA256", "other"), ("START_IZ", 53180), ("PREFIX_COLUMNS", 16734)])
def test_frozen_caps_and_original_u5_contract_cannot_drift(tree, field, value):
    v = fake_verifier(tree.root)
    setattr(v, field, value)
    with pytest.raises(ValueError, match="LEGACY_RESOURCE_CAP_DRIFT|R3P_FROZEN_H2_U5_CONTRACT"):
        runner.validate_verifier(v)


def test_archive_redirect_is_scoped_and_rejects_unexpected_paths(tree):
    v = fake_verifier(tree.root)
    original = vars(v).copy()
    statistics = {}
    with pytest.raises(ValueError, match="UNEXPECTED_SOURCE_ARCHIVE_REQUEST"):
        with runner.audit_bindings(v, source_zip=tree.archive, backend="cached", build_info=None,
                                   binding=tree.binding, block_columns=32, statistics=statistics):
            assert v.OriginalHyRecPrimitiveRateTable is not original["OriginalHyRecPrimitiveRateTable"]
            v.safe_extract_source("unrelated.zip", "destination")
    assert vars(v) == original


@pytest.mark.parametrize("inherited,requested,expected", [
    ((58, 59), (60, 60), (58, 59)), ((17, 18), (60, 60), (17, 18)),
    ((20, 59), (60, 60), (20, 59)), ((-1, -1), (60, 60), (60, 60)),
    ((58, 59), (5, 5), (5, 5)), ((58, 59), (-1, -1), (58, 59)),
])
def test_frozen_cpu_request_never_raises_inherited_limits(inherited, requested, expected):
    calls, statistics = [], {}
    module = SimpleNamespace(RLIMIT_CPU=0, RLIMIT_AS=1, RLIM_INFINITY=-1,
                             getrlimit=lambda kind: inherited,
                             setrlimit=lambda kind, pair: calls.append((kind, pair)))
    proxy = runner.InheritedResourceLimits(module, statistics)
    proxy.setrlimit(module.RLIMIT_CPU, requested)
    assert calls == [(0, expected)]
    assert statistics["resource_limits"][0] == {
        "resource": "CPU", "requested": list(requested),
        "inherited": list(inherited), "applied": list(expected)}


def test_resource_proxy_is_scoped_and_restored_even_after_entry_failure(tree):
    v = fake_verifier(tree.root)
    v.resource = resource
    with pytest.raises(RuntimeError, match="synthetic failure"):
        with runner.audit_bindings(v, source_zip=tree.archive, backend="cached", build_info=None,
                                   binding=tree.binding, block_columns=32, statistics={}):
            assert isinstance(v.resource, runner.InheritedResourceLimits)
            assert v.resource.getrusage is resource.getrusage
            raise RuntimeError("synthetic failure")
    assert v.resource is resource


def supervised_args(tmp_path):
    return SimpleNamespace(evidence_dir=tmp_path / "run", expected_commit="a"*40,
                           steps=16, new_allocation_id="synthetic-bounded-test")


def test_real_budget_child_accepts_frozen_60_request_under_lower_inherited_limit(tmp_path, monkeypatch):
    """One tiny Python child; no C/Rust loading, hash intake or physical work."""
    args = supervised_args(tmp_path)
    worker_receipt = tmp_path / "run.r3p_execution.json"
    child = "\n".join([
        "import sys, json, resource",
        f"sys.path.insert(0, {str(ROOT / 'scripts')!r})",
        "from run_r3p_u6_audited import InheritedResourceLimits",
        "before = resource.getrlimit(resource.RLIMIT_CPU)",
        "stats = {}",
        "InheritedResourceLimits(resource, stats).setrlimit(resource.RLIMIT_CPU, (60, 60))",
        "after = resource.getrlimit(resource.RLIMIT_CPU)",
        f"with open({str(worker_receipt)!r}, 'x') as out:",
        "    json.dump({'before':before, 'after':after, 'stats':stats}, out)",
    ])
    monkeypatch.setattr(supervisor, "worker_command", lambda argv: [sys.executable, "-B", "-c", child])
    original_resource = supervisor.budget_support.resource
    record, code = supervisor.supervise(args, [])
    assert code == 0 and record["status"] == "WORKER_RETURNED_WITHIN_SUPERVISED_BUDGET"
    state = json.loads(worker_receipt.read_text())
    assert state["before"][1] < 60
    assert state["after"] == state["before"]
    assert record["limits"] == {"cpu_s": 60., "wall_s": 180., "memory_bytes": 2*1024**3}
    assert record["memory_scope"] == {
        "address_space": "PER_PROCESS_RLIMIT_AS",
        "rss": "POLLED_WORKER_AND_DESCENDANT_RSS",
        "supervisor_rss_in_polled_total": False,
        "exact_aggregate_parent_plus_children_memory": False}
    assert record["final_receipt_write_reserve"] == {"cpu_s": 2., "wall_s": 3.}
    assert record["commands"][0]["returncode"] == 0
    assert supervisor.budget_support.resource is original_resource
    saved = json.loads((tmp_path / "run.r3p_supervision/supervision.json").read_text())
    assert saved == record


def test_supervisor_retains_worker_failure_and_restores_budget_module(tmp_path, monkeypatch):
    args = supervised_args(tmp_path)
    original_resource = supervisor.budget_support.resource

    class FailedBudget(supervisor.Budget):
        def run(self, *args, **kwargs):
            assert isinstance(supervisor.budget_support.resource, runner.InheritedResourceLimits)
            raise RuntimeError("synthetic complete-worker budget failure")

    monkeypatch.setattr(supervisor, "Budget", FailedBudget)
    record, code = supervisor.supervise(args, [])
    assert code == 2
    assert record["first_failure"]["message"] == "synthetic complete-worker budget failure"
    assert supervisor.budget_support.resource is original_resource
    assert (tmp_path / "run.r3p_supervision/supervision.json").is_file()


def test_supervisor_accounts_preflight_and_closeout_in_existing_receipt_reserve(tmp_path, monkeypatch):
    args = supervised_args(tmp_path)
    used = [0.]
    monkeypatch.setattr(supervisor.budget_support, "cpu", lambda: used[0])
    worker_receipt = tmp_path / "run.r3p_execution.json"
    worker_receipt.write_text("synthetic worker receipt")

    class CloseoutBudget(supervisor.Budget):
        def run(self, *args, **kwargs):
            # Includes source/input preflight, work and worker closeout; no
            # real CPU is consumed by this deterministic boundary fixture.
            used[0] = 58.25

    monkeypatch.setattr(supervisor, "Budget", CloseoutBudget)
    record, code = supervisor.supervise(args, [], start_clock=(0., supervisor.time.monotonic()))
    assert code == 2 and record["status"] == "FAILED"
    assert record["process_tree_cpu_s"] == 58.25
    assert "INCLUDING_RECEIPT_RESERVE" in record["resource_failure"]
    assert "INCLUDING_PREFLIGHT_AND_CLOSEOUT" in record["limits_scope"]


def test_both_public_commands_route_to_supervisor_before_numerical_imports():
    import ast
    module = ast.parse((ROOT / "scripts/run_r3p_u6_audited.py").read_text())
    dispatch = next(node for node in module.body if isinstance(node, ast.If))
    assert "run_r3p_u6_supervised" in ast.unparse(dispatch)
    numerical_import = next(node for node in module.body if isinstance(node, ast.Import)
                            and node.names[0].name == "run_r3l_u6_profiled")
    assert dispatch.lineno < numerical_import.lineno
    assert "scripts/run_r3p_u6_supervised.py" in runner.EXTRA_FILES

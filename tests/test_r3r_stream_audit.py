"""Replay-only differential and adversarial contracts for R3R spectral batching.

No solver, oracle build, or new physical trajectory is run.  The retained
actual32 fixture compacts only ignored HE payload and preserves every record
position and all non-HE bytes.  Set REC_R3R_ACTUAL32_WORKER_DIR to exercise the
unmodified verification-linked CSV as an additional local regression.
"""
from collections import deque
from copy import deepcopy
import gzip
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import warnings

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import verify_r3q_h4_continuation as baseline

ORIGINAL_COMPARE = baseline.compare_native_stream
import r3r_stream_audit as optimized
import benchmark_r3r_stream_audit as benchmark

FIXTURE = ROOT / "tests/fixtures/r3r_actual32"
CP = ROOT / "research/rec_r3o_grid_frontiers_20261019/h4_start_002/python_h4_full_start.npz"
ZIP = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def digest(content):
    return hashlib.sha256(content).hexdigest()


@pytest.fixture(scope="module")
def actual(tmp_path_factory):
    manifest = json.loads((FIXTURE / "MANIFEST.json").read_text())
    for name, identity in manifest["fixture_files"].items():
        content = (FIXTURE / name).read_bytes()
        assert len(content) == identity["bytes"]
        assert digest(content) == identity["sha256"]
    raw = gzip.decompress((FIXTURE / "native_stream.csv.gz").read_bytes())
    assert digest(raw) == manifest["uncompressed_replay"]["sha256"]
    assert len(raw) == manifest["uncompressed_replay"]["bytes"]
    rows = raw.splitlines(keepends=True)
    assert len(rows) == manifest["original_and_fixture_lines"]
    retained = b"".join(line for line in rows if line != b"HE\n")
    assert digest(retained) == manifest["retained_non_he_sha256"]
    folder = tmp_path_factory.mktemp("r3r_actual32")
    path = folder / "native_stream.csv"
    path.write_bytes(raw)
    inputs = benchmark.load_inputs(CP, FIXTURE / "python_continuation.npz", ZIP,
                                   manifest["python_event"])
    return SimpleNamespace(manifest=manifest, path=path, inputs=inputs,
                           lines=raw.decode("ascii").splitlines(keepends=True))


def run_compare(function, path, inputs, *, hook=None, block_rows=512):
    checkpoint, result, c, table = inputs
    # The source table carries an immutable mappingproxy provenance object;
    # the comparator consumes only its binary64 energy array.
    working = (deepcopy(checkpoint), deepcopy(result), deepcopy(c),
               SimpleNamespace(energy_eV=table.energy_eV.copy()))
    guards, stats = [], {}

    def guard(label):
        guards.append(label)
        if hook is not None:
            hook(working, label, len(guards))

    options = {"block_rows": block_rows, "stats": stats} if function is optimized.compare_native_stream else {}
    try:
        verdict = function(path, *working, guard, **options)
    except Exception as exc:
        return SimpleNamespace(error=(type(exc).__name__, str(exc)), identity=None,
                               guards=guards, stats=stats, inputs=working)
    return SimpleNamespace(error=None, identity=benchmark.verdict_identity(verdict, guards),
                           guards=guards, stats=stats, inputs=working)


def differential(path, inputs, *, hook=None, block_rows=512):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        old = run_compare(ORIGINAL_COMPARE, path, inputs, hook=hook)
        new = run_compare(optimized.compare_native_stream, path, inputs,
                          hook=hook, block_rows=block_rows)
    assert new.error == old.error
    assert new.identity == old.identity
    assert new.guards == old.guards
    return old, new


def tiny_inputs(py=0., *, energy=1.):
    checkpoint = {key: np.zeros((bins, 8), dtype=np.float64) for key, bins in
                  (("virtual_out", 311), ("average_virtual", 311), ("lyman_out", 3))}
    checkpoint["virtual_out"][0, 0] = py
    result = SimpleNamespace(steps=(), states=(), event=None)

    class Cosmology:
        T0_K = 2.7255

        def redshift(self, _iz):
            return 1000.

    return checkpoint, result, Cosmology(), SimpleNamespace(energy_eV=np.full(311, energy))


def write_stream(tmp_path, content):
    path = tmp_path / "native.csv"
    path.write_text(content)
    return path


TRACE_CHILD = r"""
import resource, signal, sys, time
started = time.monotonic()
inherited, effective = {}, {}
for name, kind, cap in (("cpu", resource.RLIMIT_CPU, 60),
                         ("address_space", resource.RLIMIT_AS, 2*1024**3)):
    soft, hard = resource.getrlimit(kind)
    inherited[name] = [soft, hard]
    hard = cap if hard == resource.RLIM_INFINITY else min(hard, cap)
    soft = hard if soft == resource.RLIM_INFINITY else min(soft, hard)
    resource.setrlimit(kind, (soft, hard))
    effective[name] = list(resource.getrlimit(kind))
def deadline(_signum, _frame):
    raise TimeoutError("R3R_TRACE_TEST_WORK_WALL_LIMIT")
signal.signal(signal.SIGALRM, deadline)
signal.setitimer(signal.ITIMER_REAL, 168.)
import hashlib, json
from pathlib import Path
request = json.loads(sys.argv[1])
def check_inputs():
    for name, expected in request["sha256"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != expected:
            raise ValueError("TRACE_TEST_INPUT_HASH_MISMATCH:"+name)
check_inputs()
root = Path(request["root"])
sys.path[:0] = [str(root/"scripts"), str(root/"src")]
import benchmark_r3r_stream_audit as audit
inputs = audit.load_inputs(Path(request["checkpoint"]), Path(request["python_result"]),
                           Path(request["source_archive"]), request["event"])
trace = audit.trace_lane_ratios(Path(request["native_stream"]), inputs, 512)
check_inputs()
audit.check_budget("independent_trace_test_complete")
result = {"trace": trace, "input_sha256": request["sha256"],
          "inputs_before_after": "UNCHANGED", "inherited_limits": inherited,
          "effective_limits": effective, "cpu_s": audit.total_cpu_s(),
          "wall_s": time.monotonic()-started, "pycache_prefix": sys.pycache_prefix,
          "dont_write_bytecode": sys.dont_write_bytecode}
signal.setitimer(signal.ITIMER_REAL, 0.)
print(json.dumps(result, sort_keys=True, allow_nan=False))
"""


def trace_in_fresh_process(actual, native_stream, tmp_path):
    """Allocate a new bounded replay process; retain the unchanged CLI guard."""
    folder = tmp_path / "independent_lane_trace"
    folder.mkdir()
    cache = folder / "empty_pycache"
    cache.mkdir()
    assert not any(cache.iterdir())
    result_path = FIXTURE / "python_continuation.npz"
    expected = {
        str(native_stream): digest(native_stream.read_bytes()),
        str(result_path): actual.manifest["fixture_files"]["python_continuation.npz"]["sha256"],
        str(CP): actual.manifest["checkpoint_sha256"],
        str(ZIP): actual.manifest["source_zip_sha256"],
    }
    request = {"root": str(ROOT), "native_stream": str(native_stream),
               "python_result": str(result_path), "checkpoint": str(CP),
               "source_archive": str(ZIP), "event": actual.manifest["python_event"],
               "sha256": expected}
    command = [sys.executable, "-B", "-X", f"pycache_prefix={cache}", "-c",
               TRACE_CHILD, json.dumps(request, sort_keys=True)]
    stdout, stderr = folder/"trace.stdout.json", folder/"trace.stderr.log"
    with stdout.open("xb") as out, stderr.open("xb") as err:
        done = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err, timeout=180, check=False)
    assert done.returncode == 0, (done.returncode, stderr.read_text(), stdout.read_text())
    assert stderr.read_bytes() == b""
    response = json.loads(stdout.read_text())
    assert response["inputs_before_after"] == "UNCHANGED"
    assert response["input_sha256"] == expected
    assert response["pycache_prefix"] == str(cache)
    assert response["dont_write_bytecode"] is True
    assert response["cpu_s"] < 55. and response["wall_s"] < 168.
    for name, cap in (("cpu", 60), ("address_space", 2*1024**3)):
        assert all(0 <= value <= cap for value in response["effective_limits"][name])
        for before, after in zip(response["inherited_limits"][name], response["effective_limits"][name]):
            assert before == -1 or after <= before
    return response["trace"]


def test_opt_in_signature_and_source_are_preserved():
    assert baseline.compare_native_stream is ORIGINAL_COMPARE
    signature = inspect.signature(optimized.compare_native_stream)
    parameters = list(signature.parameters.values())
    assert signature.replace(parameters=parameters[:-2]) == inspect.signature(ORIGINAL_COMPARE)
    assert [(parameter.name, parameter.kind) for parameter in parameters[-2:]] == [
        ("block_rows", inspect.Parameter.KEYWORD_ONLY), ("stats", inspect.Parameter.KEYWORD_ONLY)]


@pytest.mark.parametrize("block_rows", [1, 7, 512, 625])
def test_actual_retained_stream_full_verdict_bits_and_guards(actual, block_rows):
    before = benchmark.arrays_identity(actual.inputs)
    old, new = differential(actual.path, actual.inputs, block_rows=block_rows)
    assert old.error is None
    assert old.identity["verdict"] == actual.manifest["expected_same_h_parity"]
    assert old.guards == ["native_stdout_stream"] * (len(actual.lines)//8192) + ["native_stdout_complete"]
    assert new.stats["spectral_rows"] == 25000
    assert new.stats["max_buffered_rows"] <= block_rows
    assert new.stats["max_planck_cache_entries"] <= 314
    assert new.stats["guard_calls"] == new.stats["cache_invalidations"] == len(old.guards)
    assert new.stats["numpy_working_payload_bound_bytes"] == 60*block_rows
    assert benchmark.arrays_identity(new.inputs) == before
    assert benchmark.arrays_identity(actual.inputs) == before


def test_actual_unmodified_raw_when_supplied(actual):
    directory = os.environ.get("REC_R3R_ACTUAL32_WORKER_DIR")
    if directory is None:
        pytest.skip("unmodified actual32 CSV is externally preserved; retained-record fixture is always tested")
    folder = Path(directory)
    for name, identity in actual.manifest["original_files"].items():
        content = (folder / name).read_bytes()
        assert len(content) == identity["bytes"]
        assert digest(content) == identity["sha256"]
    old, _ = differential(folder / "native_oracle_stdout.csv", actual.inputs)
    assert old.error is None
    assert old.identity["verdict"] == actual.manifest["expected_same_h_parity"]


def test_actual_all_lane_binary64_bytes_separate_from_maxima(actual, tmp_path, monkeypatch):
    # General CI can reach this case after earlier pytest work has spent its
    # process budget.  That spent parent allowance must remain spent.
    monkeypatch.setattr(benchmark, "total_cpu_s", lambda: 92.44)
    monkeypatch.setattr(benchmark, "START_WALL", benchmark.time.monotonic()-181.)
    with pytest.raises(RuntimeError, match="R3R_REPLAY_BUDGET"):
        benchmark.check_budget("previous_pytest_work")
    trace = trace_in_fresh_process(actual, actual.path, tmp_path)
    with pytest.raises(RuntimeError, match="R3R_REPLAY_BUDGET"):
        benchmark.check_budget("parent_allowance_remains_spent")
    assert trace["status"] == "PASS"
    assert trace["lanes"] == 25000
    assert trace["differing_binary64_lanes"] == 0
    assert trace["traces"]["scalar"]["sha256"] == trace["traces"]["numpy"]["sha256"]
    assert trace["traces"]["scalar"]["bytes"] == 200000


def test_valid_arbitrary_per_tag_interleaving_and_ordered_lane_trace(actual, tmp_path):
    fields = {tag: deque() for tag in ("V", "A", "L")}
    controls, terminal = [], []
    for line in actual.lines:
        tag = line.split(",", 1)[0].rstrip("\n")
        if tag in fields:
            fields[tag].append(line)
        elif tag == "EVENT":
            terminal.append(line)
        else:
            controls.append(line)
    # Each tag retains its original (j, b) sequence.  L can lead far ahead of
    # V/A, and every STEP is already present; neither is forbidden by baseline.
    mixed = []
    while any(fields.values()):
        for tag in ("L", "A", "V", "V", "A"):
            if fields[tag]:
                mixed.append(fields[tag].popleft())
    path = write_stream(tmp_path, "".join(controls + mixed + terminal))
    old, new = differential(path, actual.inputs)
    assert old.error is None
    assert old.identity["verdict"] == actual.manifest["expected_same_h_parity"]
    assert new.stats["max_buffered_rows"] <= 512
    trace = trace_in_fresh_process(actual, path, tmp_path)
    assert trace["lanes"] == 25000 and trace["differing_binary64_lanes"] == 0


@pytest.mark.parametrize("later", ["V,0,1,broken\n", "V,0,2,0\n", "BAD\n", ""])
def test_earlier_numeric_failure_precedes_later_parse_order_control_or_eof(tmp_path, later):
    path = write_stream(tmp_path, "V,0,0,1\n" + later)
    old, new = differential(path, tiny_inputs())
    assert old.error[0] == "ArithmeticError"
    assert old.error[1].startswith("INTEGRATED_PHOTON_PARITY:j=0:tag=V:bin=0:ratio=")
    assert new.stats["scalar_replay_blocks"] == 1


@pytest.mark.parametrize("later,expected", [
    ("V,0,1,broken\n", "ValueError"),
    ("V,0,2,0\n", "ArithmeticError"),
    ("UNKNOWN\n", "ValueError"),
    ("V,0\n", "IndexError"),
])
def test_accepted_pending_prefix_preserves_later_input_exception(tmp_path, later, expected):
    old, _ = differential(write_stream(tmp_path, "V,0,0,0\n" + later), tiny_inputs())
    assert old.error[0] == expected


def test_pending_failure_is_flushed_before_guard_call(tmp_path):
    path = write_stream(tmp_path, "HE\n"*8190 + "V,0,0,1\nHE\n")
    old, _ = differential(path, tiny_inputs())
    assert old.error[1].startswith("INTEGRATED_PHOTON_PARITY")
    assert old.guards == []


def test_guard_exception_precedes_record_at_8192(tmp_path):
    path = write_stream(tmp_path, "HE\n"*8190 + "V,0,0,0\nBAD\n")

    def fail(_inputs, _label, _count):
        raise RuntimeError("CALLBACK_RESOURCE_CAP")

    old, _ = differential(path, tiny_inputs(), hook=fail)
    assert old.error == ("RuntimeError", "CALLBACK_RESOURCE_CAP")
    assert old.guards == ["native_stdout_stream"]


def test_guard_mutation_invalidates_planck_and_array_references(tmp_path):
    inputs = tiny_inputs(energy=4.)
    inputs[0]["average_virtual"][0, 0] = 1.
    after_fbb = 1./math.expm1(1./(baseline.KB_EV_K*5.451*1001.))
    native = .5e-10*after_fbb
    path = write_stream(tmp_path, "HE\n"*8190 + f"V,0,0,0\nA,0,0,{native:.17g}\n")

    def mutate(working, _label, count):
        assert count == 1
        checkpoint, _, c, table = working
        c.T0_K = 5.451
        table.energy_eV = np.ones(311)
        checkpoint["average_virtual"] = np.zeros((311, 8))

    old, new = differential(path, inputs, hook=mutate)
    # Reaching the final count diagnostic proves the post-guard row passed.
    assert old.error[1].startswith("C_ROW_COUNT:")
    assert old.guards == ["native_stdout_stream"]
    assert new.stats["scalar_planck_calls"] == 2
    assert new.stats["cache_invalidations"] == 1


def test_eof_guard_reads_live_event_and_keeps_failure_order(actual):
    def mutate(working, label, _count):
        if label == "native_stdout_complete":
            working[1].event = {"iz": 72893, "type": "HELIUM_CUTOFF"}

    old, _ = differential(actual.path, actual.inputs, hook=mutate)
    assert old.error[1].startswith("C_PY_EVENT_MISMATCH:")
    assert old.guards[-1] == "native_stdout_complete"


@pytest.mark.parametrize("py,native", [
    (math.nan, 0.), (0., math.nan), (math.inf, math.inf), (math.inf, 0.),
    (0., math.inf), (-math.inf, math.inf), (0., 0.), (-0., 0.), (-0., -0.),
    (1., np.nextafter(1., 2.)), (np.finfo(float).max, np.finfo(float).max),
    (np.finfo(float).max, -np.finfo(float).max),
    (np.finfo(float).tiny, 0.), (np.nextafter(0., 1.), 0.),
])
def test_exceptional_and_extreme_binary64_first_failure(tmp_path, py, native):
    path = write_stream(tmp_path, f"V,0,0,{native:.17g}\n")
    old, _ = differential(path, tiny_inputs(py))
    assert old.error[0] == "ArithmeticError"
    assert old.error[1].startswith(("INTEGRATED_PHOTON_PARITY:", "C_ROW_COUNT:"))


def test_same_tolerance_boundary_neighbors(tmp_path):
    inputs = tiny_inputs(1.)
    c, table = inputs[2:]
    fbb = 1./math.expm1(table.energy_eV[0]/(baseline.KB_EV_K*c.T0_K*1001.))
    boundary = (1.+1.e-10*fbb)/(1.-1.e-7)
    failures = []
    for cv in (np.nextafter(boundary, -math.inf), boundary, np.nextafter(boundary, math.inf)):
        path = write_stream(tmp_path, f"V,0,0,{cv:.17g}\n")
        old, _ = differential(path, inputs)
        failures.append(old.error[1].split(":", 1)[0])
    assert "C_ROW_COUNT" in failures and "INTEGRATED_PHOTON_PARITY" in failures


@pytest.mark.parametrize("policy,py,native", [
    ({"over": "raise"}, np.finfo(float).max, -np.finfo(float).max),
    ({"invalid": "raise"}, math.inf, math.inf),
    ({"under": "raise"}, np.finfo(float).tiny, 0.),
    ({"all": "raise"}, 1., np.nextafter(1., 2.)),
])
def test_nondefault_float_error_policy_uses_original_scalar_semantics(tmp_path, policy, py, native):
    path = write_stream(tmp_path, f"V,0,0,{native:.17g}\n")
    with np.errstate(**policy):
        old, new = differential(path, tiny_inputs(py))
    assert old.error is not None
    assert new.stats["scalar_replay_blocks"] == 1


def test_custom_float_error_callback_preserves_scalar_calls(tmp_path):
    path = write_stream(tmp_path, f"V,0,0,{-np.finfo(float).max:.17g}\n")
    results = []
    for function in (ORIGINAL_COMPARE, optimized.compare_native_stream):
        callbacks = []
        previous = np.geterrcall()
        try:
            np.seterrcall(lambda error, flag: callbacks.append((error, flag)))
            with np.errstate(over="call"):
                result = run_compare(function, path, tiny_inputs(np.finfo(float).max))
            results.append((result.error, callbacks))
        finally:
            np.seterrcall(previous)
    assert results[0] == results[1]
    assert results[0][1] == [("overflow", 2)]


@pytest.mark.parametrize("line", ["HE\n", "HE,ignored,payload\n", "HE\r\n", "HE \n", " HE\n", "HE\t\n"])
def test_he_fastpath_recognizes_only_original_exact_tag(tmp_path, line):
    old, _ = differential(write_stream(tmp_path, line), tiny_inputs())
    if line in ("HE\n", "HE,ignored,payload\n", "HE\r\n"):
        assert old.error[1].startswith("C_ROW_COUNT:")
    else:
        assert old.error[1].startswith("UNKNOWN_C_RECORD:")


@pytest.mark.parametrize("rows", [0, 626, -1, True, 1.5])
def test_buffer_request_cannot_exceed_bound(tmp_path, rows):
    with pytest.raises(ValueError, match="R3R_BLOCK_ROWS_1_TO_625"):
        optimized.compare_native_stream(tmp_path / "unopened.csv", *tiny_inputs(), block_rows=rows)


def test_benchmark_requires_bounded_rounds_and_full_source_sha():
    common = ["--source-sha", "0"*40, "--native-stream", "unused.csv", "--python-result", "unused.npz",
              "--verification", "unused.json", "--output-dir", "unused-output"]
    with pytest.raises(SystemExit):
        benchmark.parse_args(common + ["--rounds", "6"])
    with pytest.raises(SystemExit):
        benchmark.parse_args(common + ["--source-sha", "short"])
    assert benchmark.parse_args(common + ["--rounds", "5"]).rounds == 5

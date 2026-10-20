"""Receipt-gated ABI/adapter checks; saved ratios and real/synthetic prefix.

Run with R3P_BUILD_RECEIPT=/absolute/path/to/build.json. These tests never build
Rust, download a toolchain, integrate physics, or execute benchmark repetitions.
The ratio subset and parent-extracted prefix slices are actual saved data;
malformed prefix controls use bounded synthetic rows.
"""
import ctypes as ct
import gzip
import importlib
import json
import math
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import benchmark_r3p_ratio as ratio
import r3p_rust_audit as binding

pytestmark = pytest.mark.skipif(
    not os.environ.get("R3P_BUILD_RECEIPT"),
    reason="set R3P_BUILD_RECEIPT to an actual validated parent build receipt")
FIXTURE = ROOT / "tests/fixtures/r3p_ratio/actual_v_subset.npz"
NO_ROW = ct.c_size_t(-1).value
SENTINEL = -987654321.125


@pytest.fixture(scope="module")
def library():
    # A present but stale/bad receipt is a failure, never a skip.
    return binding.library_from_build(Path(os.environ["R3P_BUILD_RECEIPT"]))


@pytest.fixture
def auditor(library):
    with binding.PrefixAuditor(library) as value:
        yield value


@pytest.fixture(scope="module")
def saved_ratios():
    arrays, record = ratio.load_fixture(FIXTURE, FIXTURE.with_suffix(".json"))
    with np.load(FIXTURE, allow_pickle=False) as data:
        expected, indices = data["scalar_ratio"], data["source_indices"]
    return arrays, expected, indices, record


@pytest.fixture(scope="module")
def saved_prefix():
    folder = ROOT / "tests/fixtures/r3p_prefix"
    manifest = json.loads((folder / "MANIFEST.json").read_text())
    assert manifest["schema"] == "rec.r3p.real-prefix-fixture.v1"
    assert manifest["prefix_fields"] == 24 * 314
    assert manifest["block_starts"] == [0, 8000, 16725]
    for name, digest in manifest["files"].items():
        assert binding.sha256(folder / name) == digest
    with np.load(folder / "prefix.npz", allow_pickle=False) as data:
        arrays = {name: data[name] for name in data.files}
    assert arrays["py"].shape == arrays["native"].shape == (24, 314)
    assert arrays["tr"].shape == arrays["columns"].shape == (24,)
    assert arrays["energies"].shape == (314,)
    assert arrays["block_starts"].tolist() == manifest["block_starts"]
    lines = gzip.decompress((folder / "prefix.csv.gz").read_bytes()).splitlines(keepends=True)
    assert len(lines) == manifest["prefix_fields"]
    return arrays, lines


def bits_equal(a, b):
    assert np.asarray(a).shape == np.asarray(b).shape
    ratio.require_bitwise_equal(np.asarray(a).ravel(), np.asarray(b).ravel())


def prefix_case(columns=2, start=17):
    py = ((np.arange(columns * 314, dtype=np.float64) % 29) - 14.) * 2.**-45
    py = py.reshape(columns, 314)
    py[0, 0], py[0, 1] = -0., np.nextafter(0., 1.)
    lines = []
    for col in range(columns):
        for slot in range(314):
            tag, b = ("PV", slot) if slot < 311 else ("PL", slot - 311)
            lines.append(f"{tag},{start + col},{b},{py[col, slot]:.17e}\n")
    return SimpleNamespace(py=py, tr=np.full(columns, .23),
                           energies=np.linspace(.1, 2., 314), lines=lines,
                           start=start, columns=columns)


def text(case):
    return "".join(case.lines).encode("utf-8")


def audit(auditor, case):
    return auditor.audit_block(text(case), case.start, case.py, case.tr, case.energies)


def change_value(case, row, value):
    fields = case.lines[row].rstrip("\n").split(",")
    fields[3] = value
    case.lines[row] = ",".join(fields) + "\n"


def enough_cpus(threads):
    available = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (os.cpu_count() or 1)
    if available < threads:
        pytest.skip(f"{threads} threads require that many available affinity CPUs")


def test_actual_fixture_provenance_and_size(saved_ratios):
    arrays, expected, indices, record = saved_ratios
    meta = record["provenance"]
    assert sum(p.stat().st_size for p in FIXTURE.parent.iterdir() if p.is_file()) < 1024**2
    assert len(expected) == len(indices) == record["lanes"] == 623
    assert indices.tolist() == sorted(set(range(0, 9952, 16)) | {9951})
    assert len(set((indices // 311).tolist())) == 32
    assert meta["source"]["npz_sha256"] == "83c1099a8fe6862d6e241d675c2077c53492ededcdd7d81050b01b46640296b9"
    assert meta["source"]["lanes"] == 9952
    assert set(meta["source"]["upstream_input_sha256_as_recorded"]) == {
        "native_oracle_stdout.csv", "python_u6_rt.npz", "verification.json"}
    for name, a in zip(("py", "native", "fbb"), arrays):
        assert ratio.array_record(a) == meta["arrays"][name]
        assert not a.flags.writeable
    assert ratio.array_record(indices) == meta["arrays"]["source_indices"]
    assert ratio.array_record(expected) == meta["arrays"]["scalar_ratio"]


def test_actual_ratios_three_backends_bitwise(auditor, saved_ratios):
    arrays, expected, _, _ = saved_ratios
    before = [ratio.array_record(a) for a in arrays]
    for method in (ratio.scalar_ratios, ratio.numpy_ratios, auditor.ratios):
        ratio.require_bitwise_equal(expected, method(*arrays), method.__name__)
    assert [ratio.array_record(a) for a in arrays] == before
    assert auditor.stats["calls"] == 0  # Ratio ABI does not audit prefix records.


def test_ratio_zero_extremes_tail_and_noncontracted_arithmetic(auditor):
    # These values exercise separated products/addition, plus an odd tail and
    # exact zero. They are synthetic arithmetic controls, not physical data.
    p = np.array([0x3f173319dfa58020, 0x3fe5b6ec805e091c, 0x40772267b481082c,
                  0, 0x8000000000000000], dtype=np.uint64).view(np.float64)
    c = np.zeros(5, dtype=np.float64)
    b = np.array([0x3e6985e9b3839a75, 0x3e462f148b6f8a7f, 0x4006d4ed63a276f6,
                  0x3ff0000000000000, 0x3ff0000000000000], dtype=np.uint64).view(np.float64)
    tol_bits = (0x3da37614ed943052, 0x3e723729cda8f6a9, 0x3f03681c9ddc682d)
    for i, expected in enumerate(tol_bits):
        tol = 1.e-7 * max(abs(float(p[i])), abs(float(c[i]))) + 1.e-10 * float(b[i])
        assert np.array([tol]).view(np.uint64)[0] == expected
    expected = ratio.scalar_ratios(p, c, b)
    assert (expected[:3] > 1.).all()  # A ratio kernel is not a parity gate.
    assert (expected[3:].view(np.uint64) == 0).all()
    bits_equal(expected, ratio.numpy_ratios(p, c, b))
    bits_equal(expected, auditor.ratios(p, c, b))
    # Noncontiguous inputs are copied by the adapter, preserving every lane.
    bits_equal(expected[::2], auditor.ratios(p[::2], c[::2], b[::2]))
    empty = np.array([], dtype=np.float64)
    assert auditor.ratios(empty, empty, empty).shape == (0,)


def test_ratio_negative_controls(auditor):
    report = ratio.negative_controls({"scalar": ratio.scalar_ratios,
                                     "numpy": ratio.numpy_ratios, "rust": auditor.ratios})
    assert all(len(report[k]) == 6 for k in ratio.BACKENDS)
    assert report["one_ulp"] == report["signed_zero"] == "rejected"
    with pytest.raises(AssertionError, match="NONFINITE"):
        ratio.require_bitwise_equal(np.array([np.nan]), np.array([np.nan]))


@pytest.mark.parametrize("bad", ["dtype", "shape", "length", "ndim"])
def test_ratio_adapter_rejects_bad_arrays(auditor, bad):
    p = np.ones(3)
    c, b = p.copy(), p.copy()
    if bad == "dtype":
        p = p.astype(np.float32)
    elif bad == "shape":
        b = b[:-1]
    elif bad == "length":
        p = c = b = np.ones(ratio.MAX_LANES + 1)
    else:
        p = c = b = np.ones((1, 3))
    with pytest.raises(ValueError, match="R3P_(F64|RATIO)_SHAPE"):
        auditor.ratios(p, c, b)


def test_matched_plan_is_fixed_and_balanced():
    plan = ratio.make_plan(9952)
    assert plan["timed_calls_per_backend"] == 6 * 64
    assert plan["timed_lanes_per_backend"] == 9952 * 6 * 64
    assert plan["ratio_execution_threads"] == 1
    assert not plan["pool_used_by_ratio"] and not plan["adaptive_repeats"]
    for name in ratio.BACKENDS:
        assert sum(order.count(name) for order in plan["schedule"]) == 6
        for position in range(3):
            assert sum(order[position] == name for order in plan["schedule"]) == 2
    for kwargs in ({"repeats": 257}, {"trials": 4}, {"warmups": -1}, {"threads": 3}):
        with pytest.raises(ValueError, match="R3P_RATIO_PLAN"):
            ratio.make_plan(9952, **kwargs)
    with pytest.raises(ValueError, match="WORK_CAP"):
        ratio.make_plan(20096, repeats=256, trials=12)


def test_ratio_cpu_budget_respects_inherited_limits():
    unlimited = ratio.resource.RLIM_INFINITY
    assert ratio.remaining_cpu_budget(30., 2., (unlimited, unlimited)) == 30.
    assert ratio.remaining_cpu_budget(30., 2., (8, 10)) == 5.
    assert ratio.remaining_cpu_budget(30., 2., (unlimited, 10)) == 7.
    assert ratio.remaining_cpu_budget(1., 2., (8, 10)) == 1.
    with pytest.raises(RuntimeError, match="INHERITED_CPU_BUDGET_EXHAUSTED"):
        ratio.remaining_cpu_budget(30., 9.5, (10, 10))


def test_benchmark_preparation_failure_has_receipt_without_timing_methods(tmp_path):
    build = tmp_path / "invalid_build.json"
    build.write_text(json.dumps({"schema": "wrong", "status": "BUILT"}))
    args = SimpleNamespace(cpu_cap=30., wall_cap=120., fixture=FIXTURE,
                           provenance=FIXTURE.with_suffix(".json"), build=build,
                           output=tmp_path / "failure.json", repeats=64, trials=6,
                           warmups=2, threads=1)
    with pytest.raises(ValueError, match="R3P_BUILD_NOT_SUCCESSFUL"):
        ratio.run(args)
    receipt = json.loads(args.output.read_text())
    assert receipt["status"] == "FAILED" and receipt["phase"] == "preparation"
    assert receipt["samples"] == []
    assert receipt["failure"]["message"] == "R3P_BUILD_NOT_SUCCESSFUL"
    assert receipt["observed_elapsed"]["cpu_seconds"] >= 0.
    before = args.output.read_bytes()
    with pytest.raises(ValueError, match="R3P_BUILD_NOT_SUCCESSFUL"):
        ratio.run(args)
    assert args.output.read_bytes() == before  # Failure handling is create-only.


@pytest.mark.parametrize("kind", ["npz_sha", "input_raw_sha", "schema"])
def test_fixture_loader_fails_closed(tmp_path, kind):
    metadata = json.loads(FIXTURE.with_suffix(".json").read_text())
    if kind == "npz_sha":
        metadata["fixture_sha256"] = "0" * 64
    elif kind == "input_raw_sha":
        metadata["arrays"]["py"]["raw_sha256"] = "0" * 64
    else:
        metadata["schema"] = "unknown"
    altered = tmp_path / "altered_provenance.json"
    altered.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="R3P_RATIO_(FIXTURE_SHA|INPUT_RAW_SHA|PROVENANCE_SCHEMA)"):
        ratio.load_fixture(FIXTURE, altered)


@pytest.mark.parametrize("kind", ["missing_source", "changed_library", "schema", "vendor_sha"])
def test_build_receipt_fails_closed(library, tmp_path, kind):
    report = json.loads(Path(os.environ["R3P_BUILD_RECEIPT"]).read_text())
    if kind == "missing_source":
        report["source_sha256"].pop("rust/rec-stream-audit/src/lib.rs")
        error = "SOURCE_CLOSURE_CHANGED_OR_INCOMPLETE"
    elif kind == "changed_library":
        changed = tmp_path / "changed_library.so"
        # A private altered copy is hashed and rejected before any CDLL load.
        data = bytearray(Path(library).read_bytes())
        data[-1] ^= 1
        changed.write_bytes(data)
        report["library"] = str(changed)
        error = "LIBRARY_CHANGED"
    elif kind == "schema":
        report["schema"] = "rec.r3p.audit-build.v0"
        error = "BUILD_NOT_SUCCESSFUL"
    else:
        report["vendor_sha256"] = "0" * 64
        error = "VENDOR_CHANGED"
    path = tmp_path / "build.json"
    path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match=error):
        binding.library_from_build(path)


@pytest.mark.parametrize("threads", [1, 2, 4])
def test_prefix_valid_pool_reuse_and_input_bits(library, threads):
    enough_cpus(threads)
    case = prefix_case(3)
    before = [a.copy() for a in (case.py, case.tr, case.energies)]
    # CRLF, permitted value whitespace, signed indices, and a missing final LF.
    case.lines = [line.rstrip("\n") + " \t\r\n" for line in case.lines]
    case.lines[0] = case.lines[0].replace(",17,0,", ", +17 , +0 ,")
    case.lines[-1] = case.lines[-1].rstrip("\r\n")
    with binding.PrefixAuditor(library, threads=threads) as auditor:
        handle = auditor.handle
        for _ in range(2):
            bits_equal(case.py, audit(auditor, case))
            assert auditor.handle == handle
        assert auditor.stats["calls"] == 2
        assert auditor.stats["validated_columns"] == 6
        assert auditor.stats["attempted_records"] == 6 * 314
        assert auditor.stats["max_array_scratch_bytes"] == 2 * case.py.nbytes + case.tr.nbytes + case.energies.nbytes
    for a, original in zip((case.py, case.tr, case.energies), before):
        bits_equal(a, original)


@pytest.mark.parametrize("threads", [1, 2, 4])
@pytest.mark.parametrize("block", [0, 1, 2], ids=["initial", "middle", "final"])
def test_actual_prefix_matches_native_bits_and_original_scalar_gate(library, saved_prefix, threads, block):
    enough_cpus(threads)
    arrays, lines = saved_prefix
    first = block * 8
    start = int(arrays["block_starts"][block])
    py, native = arrays["py"][first:first + 8], arrays["native"][first:first + 8]
    tr, energies = arrays["tr"][first:first + 8], arrays["energies"]
    block_lines = lines[first * 314:(first + 8) * 314]
    before = [ratio.array_record(a) for a in (py, native, tr, energies)]
    parsed = np.empty_like(native)
    # Independent Python scalar transcription of compare_native_stream's
    # prefix gate. Native parsing, order, finiteness and libm expm1 are checked
    # before comparing the Rust result's bits to the authenticated native NPZ.
    for row, line in enumerate(block_lines):
        col, slot = divmod(row, 314)
        fields = line.decode("ascii").strip().split(",")
        assert len(fields) == 4
        assert fields[0] == ("PV" if slot < 311 else "PL")
        assert int(fields[1]) == start + col == int(arrays["columns"][first + col])
        assert int(fields[2]) == (slot if slot < 311 else slot - 311)
        value, pv = float(fields[3]), float(py[col, slot])
        temperature, energy = float(tr[col]), float(energies[slot])
        assert math.isfinite(value) and math.isfinite(pv)
        assert math.isfinite(temperature) and temperature > 0.
        assert math.isfinite(energy) and energy > 0.
        fbb = 1. / math.expm1(energy / temperature)
        tol = 1.e-7 * max(abs(pv), abs(value)) + 1.e-10 * fbb
        assert math.isfinite(tol)
        assert not abs(pv - value) > tol
        parsed[col, slot] = value
    bits_equal(parsed, native)
    with binding.PrefixAuditor(library, threads=threads, block_columns=8) as auditor:
        actual = auditor.audit_block(b"".join(block_lines), start, py, tr, energies)
        bits_equal(actual, native)
        assert auditor.stats["validated_columns"] == 8
        assert auditor.stats["attempted_records"] == 8 * 314
    assert [ratio.array_record(a) for a in (py, native, tr, energies)] == before


@pytest.mark.parametrize("kind", ["fields", "missing_field", "tag", "column", "bin",
                                  "fractional_index", "overflow_index", "float", "nan", "inf", "utf8"])
def test_prefix_malformed_and_nonfinite_records(auditor, kind):
    case, row = prefix_case(), 7
    fields = case.lines[row].strip().split(",")
    if kind == "fields":
        fields.append("extra")
    elif kind == "missing_field":
        fields.pop()
    elif kind == "tag":
        fields[0] = "V"
    elif kind == "column":
        fields[1] = str(case.start + 1)
    elif kind == "bin":
        fields[2] = str(row + 1)
    elif kind == "fractional_index":
        fields[1] = "17.0"
    elif kind == "overflow_index":
        fields[1] = "9" * 40
    else:
        fields[3] = {"float": "bad", "nan": "NaN", "inf": "Infinity", "utf8": "BAD_UTF8"}[kind]
    case.lines[row] = ",".join(fields) + "\n"
    payload = text(case).replace(b"BAD_UTF8", b"\xff")
    position = case.start * 314 + row
    if kind in ("nan", "inf"):
        error = "^C_PREFIX_NONFINITE$"
    elif kind == "float":
        error = f"^R3P_RUST_PREFIX:13:{position}:4$"
    elif kind == "utf8":
        error = f"^R3P_RUST_PREFIX:21:{position}:0$"
    else:
        error = f"^C_PREFIX_ORDER:{position}$"
    with pytest.raises(ArithmeticError, match=error):
        auditor.audit_block(payload, case.start, case.py, case.tr, case.energies)
    assert auditor.stats["attempted_records"] == row + 1 + 314
    assert auditor.stats["validated_columns"] == 0


@pytest.mark.parametrize("kind,code", [("python_nan", 15), ("tr_zero", 16), ("tr_nan", 16),
                                       ("energy_zero", 17), ("energy_inf", 17)])
def test_prefix_numeric_input_gates(auditor, kind, code):
    case = prefix_case(1)
    if kind == "python_nan":
        case.py[0, 0] = np.nan
    elif kind.startswith("tr_"):
        case.tr[0] = 0. if kind == "tr_zero" else np.nan
    else:
        case.energies[0] = 0. if kind == "energy_zero" else np.inf
    error = "C_PREFIX_NONFINITE" if code == 15 else f"R3P_RUST_PREFIX:{code}:"
    with pytest.raises(ArithmeticError, match=error):
        audit(auditor, case)
    assert auditor.stats["attempted_records"] == 1


def test_prefix_exact_tolerance_and_zero_tolerance(auditor):
    case = prefix_case(1)
    case.py.fill(0.)
    case.tr.fill(1.)
    case.energies.fill(1.)
    for row in range(314):
        change_value(case, row, "0")
    threshold = np.array([0x3dcffe98461a10da], dtype=np.uint64).view(np.float64)[0]
    fbb = 1. / math.expm1(1.)
    assert float(threshold) == 1.e-7 * float(threshold) + 1.e-10 * fbb
    change_value(case, 7, f"{threshold:.17e}")
    assert audit(auditor, case)[0, 7] == threshold
    change_value(case, 7, f"{np.nextafter(threshold, math.inf):.17e}")
    with pytest.raises(ArithmeticError, match="C_PREFIX_PARITY:17:7:PV"):
        audit(auditor, case)
    change_value(case, 7, "0")
    case.tr.fill(np.nextafter(0., 1.))  # energy/Tr=+inf -> fbb=0, finite tol=0.
    bits_equal(case.py, audit(auditor, case))


@pytest.mark.parametrize("threads", [1, 2, 4])
def test_prefix_first_failure_and_speculative_work(library, threads):
    enough_cpus(threads)
    case = prefix_case(4, start=41)
    case.py[0, 83] = 12345.
    case.lines[314 + 11] = case.lines[314 + 11].replace("PV,42,11,", "PV,999,11,")
    case.tr[2] = np.nan
    with binding.PrefixAuditor(library, threads=threads) as auditor:
        for repeat in range(2):
            with pytest.raises(ArithmeticError, match="^C_PREFIX_PARITY:41:83:PV$"):
                audit(auditor, case)
            # Every column attempts work until its own first failure, even at
            # threads=1: 84 + 12 + 1 + 314. Error selection uses ordered rows.
            assert auditor.stats["attempted_records"] == (repeat + 1) * 411
        assert auditor.stats["validated_columns"] == auditor.stats["validated_records"] == 0


@pytest.mark.parametrize("kind", ["dtype", "py_shape", "tr_shape", "energy_shape",
                                  "empty", "columns", "start", "text_type"])
def test_adapter_metadata_gates_before_ffi(auditor, kind):
    case = prefix_case(1)
    payload = text(case)
    if kind == "dtype":
        case.py = case.py.astype(np.float32)
    elif kind == "py_shape":
        case.py = case.py[:, :-1]
    elif kind == "tr_shape":
        case.tr = np.ones(2)
    elif kind == "energy_shape":
        case.energies = case.energies[:-1]
    elif kind == "empty":
        case.py = np.empty((0, 314))
    elif kind == "columns":
        case.py = np.zeros((65, 314))
    elif kind == "start":
        case.start = -1
    else:
        payload = payload.decode()
    with pytest.raises(ValueError, match="R3P_"):
        auditor.audit_block(payload, case.start, case.py, case.tr, case.energies)
    assert auditor.stats["calls"] == auditor.stats["attempted_records"] == 0


def test_closed_handle_and_double_close(auditor):
    case = prefix_case(1)
    auditor.close()
    auditor.close()
    assert auditor.handle is None
    with pytest.raises(RuntimeError, match="^R3P_AUDITOR_CLOSED$"):
        audit(auditor, case)
    assert auditor.stats["calls"] == 0


class StatusGuard(ct.Structure):
    _fields_ = [("before", ct.c_uint64), ("status", binding.RecStatus), ("after", ct.c_uint64)]


def raw_prefix(auditor, case, **overrides):
    storage = np.full(case.py.size + 2, SENTINEL)
    wrapper = StatusGuard(0x123456789abcdef0, binding.RecStatus(-99, 123, -88, 456),
                          0xfedcba9876543210)
    args = dict(handle=auditor.handle, text=text(case), text_len=len(text(case)),
                start=case.start, columns=case.columns, py=binding._ptr(case.py), py_len=case.py.size,
                tr=binding._ptr(case.tr), tr_len=case.tr.size, energies=binding._ptr(case.energies),
                energies_len=case.energies.size, native=binding._ptr(storage[1:-1]), native_len=case.py.size,
                status=ct.cast(ct.byref(wrapper, StatusGuard.status.offset), ct.POINTER(binding.RecStatus)))
    args.update(overrides)
    code = auditor.lib.rec_prefix_audit(*args.values())
    assert storage[0] == storage[-1] == SENTINEL
    assert wrapper.before == 0x123456789abcdef0 and wrapper.after == 0xfedcba9876543210
    return code, wrapper.status, storage


def test_c_abi_layout_and_output_canaries(auditor):
    assert ct.sizeof(ct.c_size_t) == 8  # This receipt targets x86_64 Linux.
    assert ct.sizeof(binding.RecStatus) == 32
    assert [getattr(binding.RecStatus, n).offset for n in ("code", "row", "detail", "processed_rows")] == [0, 8, 16, 24]
    case = prefix_case(2)
    code, status, storage = raw_prefix(auditor, case)
    assert code == status.code == 0 and status.row == NO_ROW
    assert status.processed_rows == 628
    bits_equal(storage[1:-1], case.py.ravel())
    assert auditor.lib.rec_prefix_new(0) is None
    assert auditor.lib.rec_prefix_new(5) is None
    auditor.lib.rec_prefix_free(None)


@pytest.mark.parametrize("override,code,detail", [
    ({"columns": 65}, 3, 3), ({"text_len": 4194305}, 3, 2), ({"start": NO_ROW}, 3, 4),
    ({"py_len": 627}, 2, 5), ({"tr_len": 0}, 2, 6), ({"energies_len": 313}, 2, 7),
    ({"native_len": 627}, 2, 8), ({"handle": None}, 1, 1), ({"text": None}, 1, 2),
    ({"py": None}, 1, 5), ({"tr": None}, 1, 6), ({"energies": None}, 1, 7),
    ({"native": None}, 1, 8),
])
def test_c_abi_rejects_metadata_without_buffer_writes(auditor, override, code, detail):
    case = prefix_case(2)
    original = case.py.copy()
    result, status, storage = raw_prefix(auditor, case, **override)
    assert result == status.code == code
    assert status.row == NO_ROW and status.detail == detail and status.processed_rows == 0
    assert (storage == SENTINEL).all()
    bits_equal(case.py, original)


def test_c_abi_overlap_alignment_and_null_status(auditor):
    case = prefix_case(1)
    before = case.py.copy()
    code, status, storage = raw_prefix(auditor, case, native=binding._ptr(case.py))
    assert code == 5 and status.code == -99  # Overlap suppresses status writes.
    assert (storage == SENTINEL).all()
    bits_equal(case.py, before)
    code, status, storage = raw_prefix(auditor, case, status=None)
    assert code == 1 and status.code == -99 and (storage == SENTINEL).all()
    buffer = ct.create_string_buffer(case.py.nbytes + 8)
    unaligned = ct.cast(ct.byref(buffer, 1), ct.POINTER(ct.c_double))
    code, status, storage = raw_prefix(auditor, case, py=unaligned)
    assert code == status.code == 4 and status.detail == 5
    assert (storage == SENTINEL).all()


def test_ratio_c_abi_caps_alias_and_output_canaries(auditor):
    p, c, b = np.arange(1., 6.), np.zeros(5), np.ones(5)
    before = p.copy()
    output = np.full(7, SENTINEL)
    call = auditor.lib.rec_ratio_batch
    ptr = binding._ptr
    assert call(0, None, None, None, None) == 0
    assert call(20097, None, None, None, None) == 3
    assert call(5, None, ptr(c), ptr(b), ptr(output[1:-1])) == 1
    assert (output == SENTINEL).all()
    assert call(5, ptr(p), ptr(c), ptr(b), ptr(p)) == 5
    bits_equal(p, before)
    buffer = ct.create_string_buffer(48)
    unaligned = ct.cast(ct.byref(buffer, 1), ct.POINTER(ct.c_double))
    assert call(5, unaligned, ptr(c), ptr(b), ptr(output[1:-1])) == 4
    assert (output == SENTINEL).all()
    assert call(5, ptr(p), ptr(c), ptr(b), ptr(output[1:-1])) == 0
    assert output[0] == output[-1] == SENTINEL
    bits_equal(output[1:-1], ratio.scalar_ratios(p, c, b))


class CountingRows:
    def __init__(self, lines, start=4030):
        self.iterator = enumerate(lines, start)
        self.consumed = 0

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self.iterator)
        self.consumed += 1
        return value


@pytest.fixture
def hook_case(monkeypatch):
    legacy = importlib.import_module("verify_r3i_h2_u6_rt_boundary")

    def make(columns=7):
        monkeypatch.setattr(legacy, "PREFIX_COLUMNS", columns)
        case = prefix_case(columns, start=0)
        case.legacy = legacy

        class Cosmology:
            T0_K = 2.7255

            def __init__(self):
                self.calls = 0

            def redshift(self, iz):
                self.calls += 1
                return 1000. - .001 * (iz - legacy.RT_IZ)

        case.c = Cosmology()
        case.result = SimpleNamespace(virtual_out=case.py[:, :311].T.copy(),
                                      lyman_out=case.py[:, 311:].T.copy())
        case.table = SimpleNamespace(energy_eV=np.linspace(2., 12.74, 311))
        case.cv = np.full((311, columns + 2), np.nan)
        case.cl = np.full((3, columns + 2), np.nan)
        return case

    return make


def call_hook(auditor, case, guard, *, lines=None, start=4030):
    rows = CountingRows(case.lines + ["BASE,not-consumed\n"] if lines is None else lines, start)
    first = next(rows)
    result = auditor(first=first, rows=rows, result=case.result, c=case.c, table=case.table,
                     cv=case.cv, cl=case.cl, guard=guard)
    return result, rows


def test_prefix_hook_guards_scratch_and_scalar_tr(library, hook_case, monkeypatch):
    case = hook_case(17)
    guards, tr_blocks = [], []
    with binding.PrefixAuditor(library, block_columns=5) as auditor:
        real_audit = auditor.audit_block

        def capture(payload, start, py, tr, energies):
            tr_blocks.append(tr.copy())
            assert py.shape[0] <= 5 and py.flags.c_contiguous
            assert energies.shape == (314,)
            return real_audit(payload, start, py, tr, energies)

        monkeypatch.setattr(auditor, "audit_block", capture)
        counts, rows = call_hook(auditor, case, guards.append)
        assert counts == {"PV": 17 * 311, "PL": 17 * 3, "prefix_position": 17 * 314}
        assert rows.consumed == 17 * 314
        assert next(rows)[1] == "BASE,not-consumed\n"
        expected_guards = []
        for start in range(0, 17, 5):
            expected_guards.append("native_stream_rust_block")
            for line_no in range(4030 + start * 314, 4030 + min(start + 5, 17) * 314):
                if line_no % 4096 == 0:
                    expected_guards.append("native_stream")
            expected_guards.append("native_stream_rust_block_done")
        assert guards == expected_guards
        assert auditor.stats["guard_checks"] == len(guards)
        assert auditor.stats["calls"] == 4
        assert auditor.stats["validated_columns"] == 17
        assert auditor.stats["attempted_records"] == 17 * 314
        assert auditor.stats["max_array_scratch_bytes"] == 2 * 5 * 314 * 8 + 5 * 8 + 314 * 8
        assert auditor.stats["max_text_bytes"] <= 4194304
    expected_tr = np.array([case.legacy.KB_EV_K * case.c.T0_K * (1. + (1000. - .001 * col))
                            for col in range(17)])
    bits_equal(np.concatenate(tr_blocks), expected_tr)
    assert case.c.calls == 17
    bits_equal(case.cv[:, :17], case.result.virtual_out)
    bits_equal(case.cl[:, :17], case.result.lyman_out)
    assert np.isnan(case.cv[:, 17:]).all() and np.isnan(case.cl[:, 17:]).all()


def test_failed_prefix_block_is_not_committed(library, hook_case):
    case = hook_case(7)
    change_value(case, 3 * 314 + 9, "1")
    with binding.PrefixAuditor(library, threads=1, block_columns=3) as auditor:
        with pytest.raises(ArithmeticError, match="^C_PREFIX_PARITY:3:9:PV$"):
            call_hook(auditor, case, lambda _: None)
        assert auditor.stats["calls"] == 2
        assert auditor.stats["validated_columns"] == 3
        assert auditor.stats["attempted_records"] == 3 * 314 + 10 + 2 * 314
    bits_equal(case.cv[:, :3], case.result.virtual_out[:, :3])
    bits_equal(case.cl[:, :3], case.result.lyman_out[:, :3])
    assert np.isnan(case.cv[:, 3:]).all() and np.isnan(case.cl[:, 3:]).all()


@pytest.mark.parametrize("early_bad", [False, True])
def test_eof_preserves_earlier_ordered_failure(library, hook_case, early_bad):
    case = hook_case(2)
    if early_bad:
        change_value(case, 7, "1")
    with binding.PrefixAuditor(library, block_columns=2) as auditor:
        error = "^C_PREFIX_PARITY:0:7:PV$" if early_bad else "^C_PREFIX_ORDER:12$"
        with pytest.raises(ArithmeticError, match=error):
            call_hook(auditor, case, lambda _: None, lines=case.lines[:12])
        assert auditor.stats["calls"] == 1
        assert auditor.stats["attempted_records"] == (8 if early_bad else 12)
    assert np.isnan(case.cv).all() and np.isnan(case.cl).all()


@pytest.mark.parametrize("abort_label", ["native_stream_rust_block", "native_stream"])
def test_guard_abort_before_ffi_preserves_histories(library, hook_case, abort_label):
    case = hook_case(2)

    def guard(label):
        if label == abort_label:
            raise RuntimeError("TEST_GUARD_ABORT")

    with binding.PrefixAuditor(library, block_columns=2) as auditor:
        with pytest.raises(RuntimeError, match="TEST_GUARD_ABORT"):
            call_hook(auditor, case, guard)
        assert auditor.stats["calls"] == auditor.stats["attempted_records"] == 0
        assert auditor.stats["guard_checks"] == (0 if abort_label == "native_stream_rust_block" else 1)
    assert np.isnan(case.cv).all() and np.isnan(case.cl).all()
    assert case.c.calls == 0


def test_prefix_hook_cumulative_text_cap_before_append(library, hook_case):
    case = hook_case(1)
    padding = " " * (4194304 // 2)
    lines = [line.rstrip("\n") + padding + "\n" for line in case.lines[:2]]
    rows = CountingRows(lines + ["must not be consumed\n"], start=100)
    first = next(rows)
    with binding.PrefixAuditor(library, block_columns=1) as auditor:
        with pytest.raises(ValueError, match="^R3P_TEXT_BYTES_LIMIT$"):
            auditor(first=first, rows=rows, result=case.result, c=case.c, table=case.table,
                    cv=case.cv, cl=case.cl, guard=lambda _: None)
        assert auditor.stats["calls"] == auditor.stats["attempted_records"] == 0
    assert rows.consumed == 2 and case.c.calls == 0
    assert np.isnan(case.cv).all() and np.isnan(case.cl).all()

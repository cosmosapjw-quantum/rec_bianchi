"""Bounded synthetic differential audits; no integration or performance loop.

The frozen comparator is the reference. Its full 36,447-row HE preamble is
retained; both modules receive a short synthetic photon-prefix count.
"""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect
import json
import math
from pathlib import Path
import struct
import sys
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import verify_r3i_h2_u6_rt_boundary as legacy

ORIGINAL_COMPARE = legacy.compare_native_stream
ORIGINAL_CAUSAL = legacy.causal_link_count
import r3p_stream_audit as optimized


class SyntheticCosmology:
    T0_K = 2.7255

    def __init__(self):
        self.redshift_calls = 0

    def redshift(self, iz):
        self.redshift_calls += 1
        return 1000. - .001 * (iz - legacy.RT_IZ)


@pytest.fixture(scope="module")
def he_rows():
    return tuple("HE," + str(i) + "," + ",".join(["0"] * 14)
                 for i in range(36447))


@pytest.fixture
def make_case(monkeypatch, he_rows):
    def build(n=3, prefix=3):
        monkeypatch.setattr(legacy, "PREFIX_COLUMNS", prefix)
        monkeypatch.setattr(optimized, "PREFIX_COLUMNS", prefix)
        c = SyntheticCosmology()
        rng = np.random.default_rng(20261020)
        virtual = rng.uniform(-1.e-13, 1.e-13, (311, prefix+n))
        average = rng.uniform(-2.e-13, 2.e-13, (311, prefix+n))
        lyman = rng.uniform(-3.e-13, 3.e-13, (3, prefix+n))
        virtual[0, 0] = -0.
        virtual[1, 0] = np.nextafter(0., 1.)
        virtual[0, prefix] = -0.
        average[0, prefix] = np.nextafter(0., 1.)
        states = []
        for i in range(n+1):
            xe = .005 - i*1.e-7
            states.append({
                "iz": legacy.START_IZ+i, "z": c.redshift(legacy.START_IZ+i),
                "xH1s": 1.-xe, "xHII": xe, "xHeII": 0., "xe": xe,
                "Tm_K": 2500.-i*.01, "post_saha": False, "branch": "H_ONLY",
            })
        steps = [{
            "input_iz": legacy.START_IZ+i, "output_iz": legacy.START_IZ+i+1,
            "photon_col": prefix+i, "coupled": True, "branch": "H_ONLY",
            "hydrogen_rhs": -.05-i*1.e-4, "thermal_rhs": -2200.-i,
            "schur_residual": 1.e-15,
        } for i in range(n)]
        event = {"delta": .0005000545426558922,
                 "thermal_seed_prev2": -2295.1209635684745,
                 "thermal_seed_prev": -2295.028818021708}
        result = SimpleNamespace(
            states=states, steps=steps, event=event, virtual_out=virtual,
            average_virtual=average, lyman_out=lyman,
            status="HOLD_CAP_BEFORE_RT_BOUNDARY",
        )
        table = SimpleNamespace(energy_eV=np.linspace(2., 12.74, 311))

        def state_fields(state, perturb=False):
            return [
                state["iz"], state["z"], state["xH1s"], state["xHII"],
                state["xHeII"], state["xe"]*(1.+1.e-12 if perturb else 1.),
                state["Tm_K"]*(1.+1.e-13 if perturb else 1.),
            ]

        def row(*values):
            return ",".join(str(v) for v in values)

        lines = [row("PARAM", legacy.RT_IZ, 21943, 58389), *he_rows,
                 row("NODE", legacy.RT_IZ, *([0]*7)),
                 row("THERMAL_EVENT", 53177, *event.values())]
        for col in range(prefix):
            for tag, array in (("PV", virtual), ("PL", lyman)):
                for b in range(array.shape[0]):
                    lines.append(row(tag, col, b, float(array[b, col])*(1.+2.e-9)))
        lines.append(row("BASE", *state_fields(states[0]), 0))
        for i, step in enumerate(steps):
            lines.append(row(
                "STEP", i, *state_fields(states[i+1], perturb=True),
                step["hydrogen_rhs"]*(1.+1.e-10), 1, 0,
                step["thermal_rhs"]*(1.+1.e-10)))
            for tag, array in (("V", virtual), ("A", average), ("L", lyman)):
                for b in range(array.shape[0]):
                    lines.append(row(tag, i, b, float(array[b, prefix+i])*(1.+3.e-9)))
        lines.append(row("END", result.status, 53177, n+2, n))
        c.redshift_calls = 0
        return SimpleNamespace(c=c, table=table, result=result, lines=lines)
    return build


def fingerprint(value):
    """Compare every returned float's bits and scalar type, including -0."""
    if isinstance(value, (float, np.floating)):
        return type(value).__name__, struct.pack(">d", value)
    if isinstance(value, dict):
        return tuple((k, fingerprint(v)) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return tuple(fingerprint(v) for v in value)
    return value


def run_case(module, case, folder, hook=None, prefix_auditor=None):
    folder.mkdir()
    path = folder / "synthetic_stream.csv"
    path.write_text("\n".join(case.lines) + "\n")
    evidence = folder / "evidence"
    evidence.mkdir()
    binary = folder / "synthetic_unexecuted_oracle.so"
    binary.write_bytes(b"SYNTHETIC FORENSIC HASH FIXTURE; NEVER EXECUTED")
    inputs = SimpleNamespace(c=deepcopy(case.c), table=deepcopy(case.table),
                             result=deepcopy(case.result))
    oracle = SimpleNamespace(h=SimpleNamespace(lib=SimpleNamespace(_name=str(binary))))
    guards = []

    def guard(label):
        guards.append(label)
        if hook:
            hook(inputs, len(guards))

    metrics = error = None
    options = {} if prefix_auditor is None else {"prefix_auditor": prefix_auditor}
    try:
        metrics = module.compare_native_stream(
            path, inputs.result, inputs.c, inputs.table, None, oracle,
            folder, evidence, guard, **options)
    except Exception as exc:
        error = type(exc).__name__, str(exc)
    return SimpleNamespace(
        metrics=metrics, error=error, guards=guards, inputs=inputs,
        diagnostics=(evidence/"average_diagnostics.jsonl").read_bytes(),
        raw=(evidence/"average_raw_failures.jsonl").read_bytes(),
    )


def differential(case, tmp_path, hook=None):
    old = run_case(legacy, case, tmp_path/"legacy", hook)
    new = run_case(optimized, case, tmp_path/"optimized", hook)
    assert new.error == old.error
    assert fingerprint(new.metrics) == fingerprint(old.metrics)
    assert new.guards == old.guards
    assert new.raw == old.raw
    assert new.diagnostics == old.diagnostics
    return old, new


def position(case, prefix):
    return next(i for i, line in enumerate(case.lines) if line.startswith(prefix))


def field(case, prefix, index, value):
    at = position(case, prefix)
    row = case.lines[at].split(",")
    row[index] = str(value)
    case.lines[at] = ",".join(row)


def test_import_is_opt_in_and_signatures_match():
    assert legacy.compare_native_stream is ORIGINAL_COMPARE
    assert legacy.causal_link_count is ORIGINAL_CAUSAL
    signature = inspect.signature(optimized.compare_native_stream)
    parameters = list(signature.parameters.values())
    assert signature.replace(parameters=parameters[:-1]) == inspect.signature(ORIGINAL_COMPARE)
    assert parameters[-1].name == "prefix_auditor"
    assert parameters[-1].kind == inspect.Parameter.KEYWORD_ONLY
    assert parameters[-1].default is None
    assert inspect.signature(optimized.causal_link_count) == inspect.signature(ORIGINAL_CAUSAL)


def test_optional_prefix_callback_consumes_shared_iterator_without_double_count(
        make_case, tmp_path):
    case = make_case()
    calls = []

    def fake_prefix(*, first, rows, result, c, table, cv, cl, guard):
        # A protocol fake, not a numerical substitute for the parent's auditor.
        assert iter(rows) is rows
        assert cv.shape == (311, 6) and cl.shape == (3, 6)
        assert np.all(np.isnan(cv)) and np.all(np.isnan(cl))
        assert result.virtual_out.shape == cv.shape
        assert c.T0_K == case.c.T0_K
        assert np.array_equal(table.energy_eV, case.table.energy_eV)
        calls.append(first)
        for pos in range(optimized.PREFIX_COLUMNS*314):
            line_no, line = first if pos == 0 else next(rows)
            if pos and line_no % 4096 == 0:
                guard("native_stream")
            tag, col, b, value = line.rstrip("\n").split(",")
            expected_col, expected_bin = divmod(pos, 314)
            expected_tag = "PV" if expected_bin < 311 else "PL"
            if expected_tag == "PL":
                expected_bin -= 311
            assert (tag, int(col), int(b)) == (expected_tag, expected_col, expected_bin)
            (cv if tag == "PV" else cl)[int(b), int(col)] = float(value)
        return {"PV": 311*optimized.PREFIX_COLUMNS, "PL": 3*optimized.PREFIX_COLUMNS,
                "prefix_position": 314*optimized.PREFIX_COLUMNS}

    old = run_case(legacy, case, tmp_path/"legacy")
    new = run_case(optimized, case, tmp_path/"optimized", prefix_auditor=fake_prefix)
    assert old.error is new.error is None
    assert fingerprint(old.metrics) == fingerprint(new.metrics)
    assert old.raw == new.raw == old.diagnostics == new.diagnostics == b""
    assert old.guards == new.guards  # This fake retains scalar guard timing.
    assert len(calls) == 1
    first_at = position(case, "PV,0,0,")
    assert calls[0] == (first_at+1, case.lines[first_at]+"\n")


def test_prefix_callback_failure_propagates_without_fallback(make_case, tmp_path):
    calls = []

    def fail(**kwargs):
        calls.append(kwargs["first"])
        raise ArithmeticError("SYNTHETIC_PREFIX_AUDITOR_FAILURE")

    result = run_case(optimized, make_case(), tmp_path/"optimized", prefix_auditor=fail)
    assert result.error == ("ArithmeticError", "SYNTHETIC_PREFIX_AUDITOR_FAILURE")
    assert len(calls) == 1
    assert result.raw == result.diagnostics == b""


@pytest.mark.parametrize("n", [1, 3, 5])
def test_valid_multi_index_metrics_and_diagnostic_bytes_match(make_case, tmp_path, n):
    case = make_case(n=n)
    old, new = differential(case, tmp_path)
    assert old.error is None
    assert new.metrics["spectral_fields"] == 625*n
    assert new.metrics["causal_links"] == 313*n
    assert new.metrics["counts"]["HE"] == 36447
    assert new.metrics["original_average_failures"] == []
    assert new.raw == new.diagnostics == b""
    assert new.guards == ["native_stream"]*(len(case.lines)//4096)
    for name in ("virtual_out", "average_virtual", "lyman_out"):
        assert getattr(new.inputs.result, name).tobytes() == getattr(case.result, name).tobytes()


def test_scalar_cache_reduces_repeated_evaluations_without_changing_metrics(
        make_case, tmp_path, monkeypatch):
    case = make_case()
    calls = []
    scalar_expm1 = math.expm1

    def measured(value):
        calls.append(value)
        return scalar_expm1(value)

    monkeypatch.setattr(optimized, "math", SimpleNamespace(
        isfinite=math.isfinite, expm1=measured))
    old, new = differential(case, tmp_path)
    assert old.error is None
    # This fixture has no guard between a V group and its A group.
    assert len(calls) == 314*3 + 314*3
    assert old.inputs.c.redshift_calls == 314*3
    assert new.inputs.c.redshift_calls <= 3 + len(new.guards)


MALFORMED = (
    "unknown", "param_grid", "he_duplicate", "he_nan", "node_index",
    "event_nan", "prefix_bin", "prefix_duplicate", "prefix_nan", "prefix_short",
    "prefix_truncated", "base_duplicate", "step_duplicate", "step_rhs_nan",
    "step_short", "spectrum_index", "spectrum_bin", "spectrum_duplicate",
    "spectrum_missing", "spectrum_nan", "spectrum_short", "spectrum_truncated",
    "end_duplicate", "end_status", "end_missing", "two_errors",
)


@pytest.mark.parametrize("mutation", MALFORMED)
def test_malformed_first_failure_and_partial_diagnostics_match(
        make_case, tmp_path, mutation):
    case = make_case()
    if mutation == "unknown":
        case.lines[0] = "BOGUS,0"
    elif mutation == "param_grid":
        field(case, "PARAM,", 2, 21942)
    elif mutation == "he_duplicate":
        case.lines.insert(3, case.lines[2])
    elif mutation == "he_nan":
        field(case, "HE,1,", 2, "nan")
    elif mutation == "node_index":
        field(case, "NODE,", 1, legacy.RT_IZ+1)
    elif mutation == "event_nan":
        field(case, "THERMAL_EVENT,", 3, "nan")
    elif mutation in ("prefix_bin", "two_errors"):
        field(case, "PV,0,1,", 2, 0)
        if mutation == "two_errors":
            field(case, "V,2,1,", 3, "nan")
    elif mutation == "prefix_duplicate":
        at = position(case, "PV,1,0,")
        case.lines.insert(at+1, case.lines[at])
    elif mutation == "prefix_nan":
        field(case, "PL,1,0,", 3, "nan")
    elif mutation == "prefix_short":
        case.lines[position(case, "PV,0,2,")] = "PV,0,2"
    elif mutation == "prefix_truncated":
        del case.lines[position(case, "PV,1,0,"):]
    elif mutation == "base_duplicate":
        at = position(case, "BASE,")
        case.lines.insert(at+1, case.lines[at])
    elif mutation == "step_duplicate":
        at = position(case, "STEP,1,")
        case.lines.insert(at+1, case.lines[at])
    elif mutation == "step_rhs_nan":
        field(case, "STEP,1,", 9, "nan")
    elif mutation == "step_short":
        at = position(case, "STEP,1,")
        case.lines[at] = ",".join(case.lines[at].split(",")[:9])
    elif mutation == "spectrum_index":
        field(case, "A,1,0,", 1, 0)
    elif mutation == "spectrum_bin":
        field(case, "A,1,1,", 2, 0)
    elif mutation == "spectrum_duplicate":
        at = position(case, "A,1,0,")
        case.lines.insert(at+1, case.lines[at])
    elif mutation == "spectrum_missing":
        del case.lines[position(case, "V,1,0,")]
    elif mutation == "spectrum_nan":
        field(case, "A,1,7,", 3, "nan")
    elif mutation == "spectrum_short":
        case.lines[position(case, "L,1,1,")] = "L,1,1"
    elif mutation == "spectrum_truncated":
        del case.lines[position(case, "A,2,0,"):]
    elif mutation == "end_duplicate":
        case.lines.append(case.lines[-1])
    elif mutation == "end_status":
        field(case, "END,", 1, "WRONG_STATUS")
    elif mutation == "end_missing":
        case.lines.pop()
    old, _ = differential(case, tmp_path)
    assert old.error is not None


@pytest.mark.parametrize("name,value", [
    ("virtual_out", math.nan), ("virtual_out", math.inf),
    ("virtual_out", -math.inf), ("lyman_out", math.nan),
])
def test_documented_python_prefix_nonfinite_rejection(make_case, tmp_path, name, value):
    case = make_case()
    getattr(case.result, name)[0, 0] = value
    old = run_case(legacy, case, tmp_path/"legacy")
    new = run_case(optimized, case, tmp_path/"optimized")
    assert old.error is None  # Recorded material correction of legacy behavior.
    assert new.error == ("ArithmeticError", "C_PREFIX_NONFINITE")
    assert new.raw == new.diagnostics == b""


def test_guard_first_failure_and_cadence_match(make_case, tmp_path):
    def abort(inputs, calls):
        if calls == 2:
            raise RuntimeError("SYNTHETIC_CPU_GUARD")
    old, new = differential(make_case(), tmp_path, abort)
    assert old.error == ("RuntimeError", "SYNTHETIC_CPU_GUARD")
    assert len(new.guards) == 2


@pytest.mark.parametrize("replace_array", [False, True])
def test_guard_mutation_invalidates_bounded_temperature_and_va_caches(
        make_case, tmp_path, replace_array):
    # Line 40960 lies inside V for step 2; A must not reuse pre-guard values.
    case = make_case(prefix=10)
    assert case.lines[40959].startswith("V,2,")

    def mutate(inputs, calls):
        if calls == 10:
            inputs.c.T0_K *= 1.001
            inputs.table.energy_eV[0] *= 1.001
            inputs.result.states[2]["z"] *= 1.0000001
            if replace_array:
                inputs.result.average_virtual = inputs.result.average_virtual.copy()
                inputs.result.average_virtual[20, 12] = math.nan

    old, _ = differential(case, tmp_path, mutate)
    if replace_array:
        assert old.error == ("ArithmeticError", "C_SPECTRUM_NONFINITE:2:A:20")
    else:
        assert old.error is None


@pytest.fixture
def forensic_hooks(monkeypatch):
    def install(gate_status="PASS", owner_error=False):
        def owner(label, state, virtual, lyman, value, *, j, b, **kwargs):
            if owner_error:
                raise RuntimeError("SYNTHETIC_FORENSIC_FAILURE")
            return {"owner": label, "state_iz": state["iz"], "raw": float(value),
                    "j": j, "bin": b, "columns": virtual.shape[1]}

        def gates(p, c, fbb):
            return {"original_gate": {"status": "FAIL"},
                    "decimal80_ieee_gate": {"status": gate_status}, "fbb": fbb}

        for module in (legacy, optimized):
            monkeypatch.setattr(module, "_owner", owner)
            monkeypatch.setattr(module, "numerical_gates", gates)
    return install


@pytest.mark.parametrize("gate_status,owner_error", [
    ("PASS", False), ("FAIL", False), ("PASS", True),
])
def test_average_forensic_output_and_first_failure_match(
        make_case, tmp_path, forensic_hooks, gate_status, owner_error):
    forensic_hooks(gate_status, owner_error)
    case = make_case()
    field(case, "A,0,2,", 3, 1.e-6)
    field(case, "A,2,5,", 3, 2.e-6)
    old, new = differential(case, tmp_path)
    raw = [json.loads(line) for line in new.raw.splitlines()]
    assert len(raw) == (2 if gate_status == "PASS" and not owner_error else 1)
    if gate_status == "PASS" and not owner_error:
        assert old.error is None
        assert len(new.metrics["original_average_failures"]) == 2
        for row in map(json.loads, new.diagnostics.splitlines()):
            assert [o["owner"] for o in row["owners"]] == ["Python", "C"]
            assert all(o["state_iz"] == legacy.START_IZ+row["step"] for o in row["owners"])
    else:
        assert old.error is not None


def test_original_64_average_failure_limit_is_preserved(make_case, tmp_path, forensic_hooks):
    forensic_hooks()
    case = make_case()
    first = position(case, "A,0,0,")
    for b in range(65):
        case.lines[first+b] = f"A,0,{b},1e-6"
    old, new = differential(case, tmp_path)
    assert old.error[1].startswith("C_SPECTRUM_PARITY:0:A:64:")
    assert len(new.raw.splitlines()) == len(new.diagnostics.splitlines()) == 64


@pytest.fixture
def energy_table():
    optimized._cached_causal_geometry.cache_clear()
    energy = np.interp(np.arange(311), [0, 139, 140, 270, 271, 310],
                       [2., 10.19, 10.21, 12.08, 12.10, 12.74])
    yield SimpleNamespace(energy_eV=energy)
    optimized._cached_causal_geometry.cache_clear()


@pytest.mark.parametrize("j", [0, 1, 2, 17, 16733, 18000, 21942])
def test_causal_geometry_matches_all_original_per_step_checks(energy_table, j):
    assert optimized.causal_link_count(energy_table, j) == legacy.causal_link_count(energy_table, j) == 313


def test_causal_cache_is_value_bound_and_four_entry_bounded(energy_table, monkeypatch):
    calls = []
    original = optimized._source_edges

    def observed(energy):
        calls.append(energy.tobytes())
        return original(energy)

    monkeypatch.setattr(optimized, "_source_edges", observed)
    assert optimized.causal_link_count(energy_table, 16733) == 313
    assert optimized.causal_link_count(deepcopy(energy_table), 21942) == 313
    assert len(calls) == 1
    for i in range(6):
        energy_table.energy_eV[0] = 2.+(i+1)*1.e-8
        assert optimized.causal_link_count(energy_table, 16733) == legacy.causal_link_count(energy_table, 16733)
    assert len(calls) == 7
    assert optimized._cached_causal_geometry.cache_info().currsize == 4


@pytest.mark.parametrize("mutation", ["nan", "shape", "spacing", "order"])
def test_causal_cache_cannot_hide_mutated_invalid_energy(energy_table, mutation):
    assert optimized.causal_link_count(energy_table, 16733) == 313
    if mutation == "nan":
        energy_table.energy_eV[1] = math.nan
    elif mutation == "shape":
        energy_table.energy_eV = energy_table.energy_eV.reshape(1, 311)
    elif mutation == "spacing":
        energy_table.energy_eV[1] = np.nextafter(energy_table.energy_eV[0], math.inf)
    else:
        energy_table.energy_eV[1] = energy_table.energy_eV[0]
    failures = []
    for module in (legacy, optimized):
        with pytest.raises((ValueError, ArithmeticError)) as raised:
            module.causal_link_count(energy_table, 16733)
        failures.append((type(raised.value), str(raised.value)))
    assert failures[0] == failures[1]


def test_geometry_is_owned_and_cannot_be_made_writeable(energy_table):
    geometry = optimized.CausalGeometry.from_energies(energy_table.energy_eV)
    before = geometry.delays.tobytes()
    energy_table.energy_eV[:] = math.nan
    assert geometry.delays.tobytes() == before
    with pytest.raises(ValueError):
        geometry.delays[0] = 0.
    with pytest.raises(ValueError):
        geometry.delays.setflags(write=True)
    with pytest.raises(FrozenInstanceError):
        geometry.delays = np.zeros(313)
    for bad in (math.nan, math.inf, 1.):
        corrupted = np.full(313, bad)
        with pytest.raises(ArithmeticError, match="U6_FREQUENCY_CAUSAL_SPACING"):
            optimized.CausalGeometry(corrupted)(16733)


def test_cached_geometry_still_checks_future_indices_each_call(energy_table, monkeypatch):
    assert optimized.causal_link_count(energy_table, 16733) == 313
    floor = np.floor
    # Inject an impossible index computation to exercise the live guard.
    monkeypatch.setattr(np, "floor", lambda values: floor(values)+1.e6)
    for module in (legacy, optimized):
        with pytest.raises(ArithmeticError, match="U6_FUTURE_PHOTON_INDEX:16733"):
            module.causal_link_count(energy_table, 16733)

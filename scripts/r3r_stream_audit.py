"""Opt-in, bounded spectral batching for the frozen R3Q native-stream audit.

The reference is ``verify_r3q_h4_continuation.compare_native_stream``.  This
module does not advance a physical state or change any tolerance.  It keeps
the reference's per-tag ordering (including arbitrary V/A/L interleaving),
control-record path, synchronous CPU-guard boundaries and first failure.

The independent-lane arithmetic is the R3P ratio operator: subtract/abs,
two separately rounded products, their sum, then division.  Scalar libm
``expm1`` and its original input-expression ordering remain unchanged.  No
vector transcendental, FMA, reduction of signed values, or new dependency is
introduced.  Healthy finite maxima can be reduced because max selects an
existing value and every accepted ratio is finite.

Input arrays, the cosmology, and energy table must be stable between the
reference's synchronous ``cpu_guard`` calls.  They may change at those calls:
pending rows are checked first, caches are invalidated, and subsequent rows
read live inputs.  The usual source cosmology has a pure ``redshift`` method.
Concurrent external mutation and side effects on each scalar redshift read
are outside this contract.  The scientific inputs are binary64 arrays.

Rows are buffered only after their scalar metadata, array access, float
parsing and Planck computation succeed.  Before a later parse/metadata/read
exception is propagated, all earlier pending rows are checked, so an earlier
numeric failure keeps priority.  Buffers are also drained before control
rows, before every original guard, and at EOF.  On exceptional vector results
the entire pending block is replayed in scalar order for the exact reference
diagnostic and its scalar floating-point behavior.  Non-default floating
error handlers use scalar replay directly.  Stats, when requested, are
separate from the unchanged verdict and describe array payload, not RSS.
The equivalence contract covers verdicts and exception class/message; warning
stack locations and warning emission timing are not promised.  CPU guards
keep their record schedule, while a measured budget outcome can change when
the amount of computation changes.
"""
from __future__ import annotations

import math

import numpy as np

import verify_r3q_h4_continuation as baseline


MAX_BLOCK_ROWS = 625
DEFAULT_BLOCK_ROWS = 512
_FIELD = {"V": "virtual", "A": "average", "L": "lyman"}
_CODE = {"V": 0, "A": 1, "L": 2}


def compare_native_stream(path, checkpoint, result, c, table, cpu_guard=None,
                          *, block_rows=DEFAULT_BLOCK_ROWS, stats=None):
    """Return the reference verdict, using at most ``block_rows`` pending rows.

    ``stats`` may be a caller-owned dict for optional implementation telemetry;
    it is never inserted into the scientific verdict.  Rows are scalar-parsed
    in source order.  All NumPy arithmetic uses separate binary64 ufuncs.
    """
    if type(block_rows) is not int or not 1 <= block_rows <= MAX_BLOCK_ROWS:
        raise ValueError("R3R_BLOCK_ROWS_1_TO_625")
    if stats is not None and not isinstance(stats, dict):
        raise TypeError("R3R_STATS_DICT_REQUIRED")
    info = {"block_rows": block_rows, "flushes": 0,
            "spectral_rows": 0, "max_buffered_rows": 0,
            "scalar_replay_blocks": 0, "scalar_planck_calls": 0,
            "planck_cache_hits": 0, "max_planck_cache_entries": 0,
            "guard_calls": 0, "cache_invalidations": 0,
            "numpy_buffer_payload_bytes": block_rows * (3 * 8 + 1),
            "numpy_working_payload_bound_bytes": block_rows * 60,
            "payload_scope": "NumPy data only; excludes Python objects and RSS"}
    maxima = {"xHII": 0., "xe": 0., "xHeII": 0., "Tm_K": 0.,
              "hydrogen_rhs": 0., "helium_rhs": 0.,
              "virtual": 0., "average": 0., "lyman": 0.}
    counts = {"STEP": 0, "V": 0, "A": 0, "L": 0,
              "HE": 0, "NODE": 0, "EVENT": 0}
    event = None
    py_values = np.empty(block_rows, dtype=np.float64)
    native_values = np.empty(block_rows, dtype=np.float64)
    blackbody_values = np.empty(block_rows, dtype=np.float64)
    tag_codes = np.empty(block_rows, dtype=np.uint8)
    pending = []
    cached_j = None
    cached_denominator = None
    planck_cache = [None] * 314
    planck_entries = 0
    prefix_arrays = result_arrays = None
    planck_calls = cache_hits = max_planck_entries = 0

    def publish_stats():
        if stats is not None:
            info["spectral_rows"] = counts["V"] + counts["A"] + counts["L"]
            info["scalar_planck_calls"] = planck_calls
            info["planck_cache_hits"] = cache_hits
            info["max_planck_cache_entries"] = max_planck_entries
            stats.update(info)

    def invalidate_cache():
        nonlocal cached_j, cached_denominator, planck_cache, planck_entries
        nonlocal prefix_arrays, result_arrays
        cached_j = None
        cached_denominator = None
        planck_cache = [None] * 314
        planck_entries = 0
        prefix_arrays = result_arrays = None
        info["cache_invalidations"] += 1

    def scalar_rows(rows, p, native, bb):
        for i, (j, b, tag) in enumerate(rows):
            py, cv, fbb = p[i], float(native[i]), float(bb[i])
            tol = 1.e-7 * max(abs(py), abs(cv)) + 1.e-10 * fbb
            ratio = abs(py-cv) / tol
            if not math.isfinite(ratio) or ratio > 1.:
                raise ArithmeticError(
                    f"INTEGRATED_PHOTON_PARITY:j={j}:tag={tag}:bin={b}:ratio={ratio:.17g}")
            key = _FIELD[tag]
            maxima[key] = max(maxima[key], ratio)

    def flush():
        nonlocal pending
        if not pending:
            return
        # Remove the pending reference before any calculation can fail.  The
        # outer exception drain then cannot replay this failed block twice.
        rows, pending = pending, []
        n = len(rows)
        info["flushes"] += 1
        info["max_buffered_rows"] = max(info["max_buffered_rows"], n)
        p, native, bb = (a[:n] for a in
                         (py_values, native_values, blackbody_values))
        error_policy = np.geterr()
        scalar_policy = (error_policy["under"] != "ignore" or any(
            error_policy[key] not in ("ignore", "warn")
            for key in ("over", "divide", "invalid")))
        if scalar_policy:
            info["scalar_replay_blocks"] += 1
            scalar_rows(rows, p, native, bb)
            return
        # A failed vector block is replayed below, so scalar warnings/errors
        # come from its first actual failing row, as in the reference.
        with np.errstate(all="ignore"):
            ratio = np.subtract(p, native)
            np.abs(ratio, out=ratio)
            denominator = np.abs(p)
            native_abs = np.abs(native)
            np.maximum(denominator, native_abs, out=denominator)
            del native_abs
            np.multiply(denominator, 1.e-7, out=denominator)
            absolute_term = np.multiply(bb, 1.e-10)
            np.add(denominator, absolute_term, out=denominator)
            np.divide(ratio, denominator, out=ratio)
            del denominator, absolute_term
            failed = np.logical_or(~np.isfinite(ratio), ratio > 1.)
        if np.any(failed):
            info["scalar_replay_blocks"] += 1
            scalar_rows(rows, p, native, bb)
            return
        del failed
        for tag, code in _CODE.items():
            selected = ratio[tag_codes[:n] == code]
            if selected.size:
                key = _FIELD[tag]
                maxima[key] = max(maxima[key], np.max(selected))

    def guard(label):
        flush()
        invalidate_cache()
        info["guard_calls"] += 1
        cpu_guard(label)

    try:
        with path.open() as f:
            for line_number, line in enumerate(f, 1):
                if cpu_guard is not None and line_number % 8192 == 0:
                    guard("native_stdout_stream")
                if counts["EVENT"]:
                    raise ArithmeticError("C_RECORD_AFTER_TERMINAL_EVENT")
                # The frozen comparator only counts HE rows and ignores all
                # their fields.  Recognize exactly its tag without allocating
                # a split list for every already-reviewed helium record.
                if line.startswith("HE,") or line == "HE\n" or line == "HE":
                    flush()
                    counts["HE"] += 1
                    continue
                v = line.rstrip("\n").split(",")
                tag = v[0]
                if tag not in _FIELD:
                    flush()
                if tag == "HE":
                    counts["HE"] += 1
                    continue
                if tag == "NODE":
                    counts["NODE"] += 1
                    if int(v[1]) != 72892:
                        raise ArithmeticError("C_START_INDEX")
                    continue
                if tag == "STEP":
                    j = int(v[1]); counts[tag] += 1
                    if j != counts[tag]-1:
                        raise ArithmeticError(f"C_STEP_SEQUENCE:{j}")
                    is_he = bool(int(v[12]))
                    expected = (
                        {"iz": int(checkpoint["iz"][j+1]),
                         "z": float(checkpoint["z"][j+1]),
                         "xH1s": float(checkpoint["xH1s"][j+1]),
                         "xHII": float(checkpoint["xHII"][j+1]),
                         "xHeII": float(checkpoint["xHeII"][j+1]),
                         "xe": float(checkpoint["xe"][j+1]),
                         "Tm_K": float(checkpoint["Tm_K"][j+1]),
                         "post_saha": bool(checkpoint["post_saha"][j+1])}
                        if j < 8 else result.states[j-7])
                    native = {"iz": int(v[2]), "z": float(v[3]),
                              "xH1s": float(v[4]), "xHII": float(v[5]),
                              "xHeII": float(v[6]), "xe": float(v[7]),
                              "Tm_K": float(v[8]), "post_saha": bool(int(v[11]))}
                    baseline.compare_state(expected, native, j)
                    if j >= 8:
                        step = result.steps[j-8]
                        if (step["input_iz"] != 72892+j or
                                (step["branch"] == "H_HE") != is_he):
                            raise ArithmeticError(f"C_BRANCH_OR_INPUT_INDEX:{j}")
                        maxima["hydrogen_rhs"] = max(maxima["hydrogen_rhs"],
                            baseline.checked_integrated_rhs_ratio(
                                step["hydrogen_rhs"], float(v[9]), 2.e-7, j, "H"))
                        if is_he:
                            maxima["helium_rhs"] = max(maxima["helium_rhs"],
                                baseline.checked_integrated_rhs_ratio(
                                    step["helium_rhs"], float(v[10]), 2.e-7, j, "He"))
                    for key, lim, denom in (
                            ("xHII", 5e-9, max(abs(native["xHII"]), 1e-8)),
                            ("xe", 5e-9, max(abs(native["xe"]), 1e-8)),
                            ("xHeII", 5e-10, 1.),
                            ("Tm_K", 5e-10, max(abs(native["Tm_K"]), 1.))):
                        maxima[key] = max(maxima[key], abs(expected[key]-native[key])/denom)
                    continue
                if tag in _FIELD:
                    j, b = int(v[1]), int(v[2])
                    bins = 3 if tag == "L" else 311
                    if (j, b) != divmod(counts[tag], bins) or len(v) != 4:
                        raise ArithmeticError("C_SPECTRUM_ORDER_OR_DUPLICATE")
                    counts[tag] += 1
                    if j < 8:
                        if prefix_arrays is None:
                            prefix_arrays = {"V": checkpoint["virtual_out"],
                                             "A": checkpoint["average_virtual"],
                                             "L": checkpoint["lyman_out"]}
                        py = prefix_arrays[tag][b, j]
                    else:
                        if result_arrays is None:
                            result_arrays = {"V": result.virtual_out,
                                             "A": result.average_virtual,
                                             "L": result.lyman_out}
                        py = result_arrays[tag][b, j]
                    cv = float(v[3])
                    if cached_j != j:
                        cached_j = j
                        z = c.redshift(72892+j)
                        cached_denominator = baseline.KB_EV_K*c.T0_K*(1.+z)
                        planck_cache = [None] * 314
                        planck_entries = 0
                    cache_key = b+311 if tag == "L" else b
                    fbb = planck_cache[cache_key]
                    if fbb is None:
                        ev = baseline.LINE_EV[b] if tag == "L" else table.energy_eV[b]
                        fbb = 1./math.expm1(ev/cached_denominator)
                        planck_cache[cache_key] = fbb
                        planck_calls += 1
                        planck_entries += 1
                        max_planck_entries = max(max_planck_entries, planck_entries)
                    else:
                        cache_hits += 1
                    i = len(pending)
                    py_values[i], native_values[i], blackbody_values[i] = py, cv, fbb
                    tag_codes[i] = _CODE[tag]
                    pending.append((j, b, tag))
                    if len(pending) == block_rows:
                        flush()
                    continue
                if tag == "EVENT":
                    counts[tag] += 1
                    event = {"relative_index": int(v[1]), "type": int(v[2]),
                             "steps": int(v[3])}
                    continue
                raise ValueError(f"UNKNOWN_C_RECORD:{tag}")
        flush()
        n = 8+len(result.steps)
        if counts != {"HE": 72893, "NODE": 1, "STEP": n,
                      "V": 311*n, "A": 311*n, "L": 3*n, "EVENT": 1}:
            raise ArithmeticError(f"C_ROW_COUNT:{counts}")
        if event is None or event["steps"] != n:
            raise ArithmeticError("C_EVENT_RECEIPT_MISSING_OR_COUNT")
        if cpu_guard is not None:
            guard("native_stdout_complete")
        py_event = -1 if result.event is None else result.event["iz"]-72892
        py_type = 0 if result.event is None else (
            1 if result.event["type"] == "HELIUM_CUTOFF" else 2)
        if event["relative_index"] != py_event or event["type"] != py_type:
            raise ArithmeticError(f"C_PY_EVENT_MISMATCH:C={event}:P={result.event}")
        return {"status": "PASS", "counts": counts, "maxima": maxima,
                "native_event": event}
    except BaseException:
        # The current error may be from a *later* malformed row or a failed
        # iterator read.  Earlier buffered numerical failures own precedence.
        flush()
        raise
    finally:
        publish_stats()

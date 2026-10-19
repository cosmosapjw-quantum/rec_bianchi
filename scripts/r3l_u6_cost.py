"""Lossless U6 history storage and nested process-tree phase measurements.

This module has no atomic, thermal or transport equations. It records costs;
neither a fit nor an allocation label grants permission for a full U6 run.
"""
from __future__ import annotations

from contextlib import contextmanager
from functools import wraps
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import time

import numpy as np

HISTORY_FIELDS = frozenset(("states_json", "steps_json", "virtual_out",
                            "average_virtual", "lyman_out"))
CLOCK_FIELDS = ("parent_cpu_s", "children_cpu_s", "wall_s")


def clock_snapshot():
    own = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"parent_cpu_s": own.ru_utime + own.ru_stime,
            "children_cpu_s": child.ru_utime + child.ru_stime,
            "wall_s": time.perf_counter()}


def _delta(end, start):
    values = {key: end[key] - start[key] for key in CLOCK_FIELDS}
    if any(not math.isfinite(v) or v < 0 for v in values.values()):
        raise ValueError("NONMONOTONE_OR_NONFINITE_PHASE_CLOCK")
    return values


class PhaseLedger:
    """Inclusive and exclusive times; nested phases are never summed twice.

    RUSAGE_CHILDREN includes reaped children. The verifier's subprocess.run
    calls wait for their children, so build/run boundaries include that CPU.
    Coarse phase starts/ends are flushed; hot callbacks are aggregated only.
    """

    def __init__(self, stream, *, clock=clock_snapshot):
        self.stream, self.clock = stream, clock
        self.start = self.clock()
        self.phases, self.stack = {}, []
        self.serial = 0
        self.profiling_errors = []
        self.accounting_valid = True

    def emit(self, value):
        self.stream.write(json.dumps(value, sort_keys=True, allow_nan=False) + "\n")
        self.stream.flush()
        os.fsync(self.stream.fileno())

    @contextmanager
    def measure(self, phase, *, durable=True):
        frame = {"start": self.clock(), "children": dict.fromkeys(CLOCK_FIELDS, 0.)}
        self.serial += 1
        ident = self.serial
        self.stack.append(frame)
        status, failure, primary = "completed", None, None
        try:
            if durable:
                self.emit({"event": "start", "phase": phase, "id": ident})
            yield
        except BaseException as exc:
            primary = exc
            status = "failed"
            failure = {"type": type(exc).__name__, "message": str(exc)}
            raise
        finally:
            # Stack cleanup must happen even if timing or journal I/O fails.
            self.stack.pop()
            try:
                elapsed = _delta(self.clock(), frame["start"])
                exclusive = {key: elapsed[key] - frame["children"][key]
                             for key in CLOCK_FIELDS}
                for key, value in exclusive.items():
                    tol = 64 * np.finfo(float).eps * max(1., elapsed[key])
                    if value < -tol:
                        raise ArithmeticError("PHASE_CHILD_TIME_EXCEEDS_PARENT")
                    exclusive[key] = max(0., value)
                if self.stack:
                    for key in CLOCK_FIELDS:
                        self.stack[-1]["children"][key] += elapsed[key]
                row = self.phases.setdefault(phase, {
                    "calls": 0, "failed_calls": 0,
                    "inclusive": dict.fromkeys(CLOCK_FIELDS, 0.),
                    "exclusive": dict.fromkeys(CLOCK_FIELDS, 0.)})
                row["calls"] += 1
                row["failed_calls"] += int(status == "failed")
                for kind, values in (("inclusive", elapsed), ("exclusive", exclusive)):
                    for key in CLOCK_FIELDS:
                        row[kind][key] += values[key]
                if durable:
                    self.emit({"event": "end", "phase": phase, "id": ident,
                               "status": status, "inclusive": elapsed,
                               "exclusive": exclusive, "failure": failure})
            except BaseException as diagnostic:
                self.accounting_valid = False
                detail = {"phase": phase, "type": type(diagnostic).__name__,
                          "message": str(diagnostic)}
                self.profiling_errors.append(detail)
                if primary is None:
                    raise
                # Keep the actual source/runtime failure, including SystemExit.
                primary.add_note("Secondary phase profiling failure: " + repr(detail))

    def wrap(self, phase, fn, *, durable=True):
        @wraps(fn)
        def measured(*args, **kwargs):
            with self.measure(phase, durable=durable):
                return fn(*args, **kwargs)
        return measured

    def summary(self):
        if self.stack:
            raise RuntimeError("PHASE_STILL_RUNNING")
        total = _delta(self.clock(), self.start)
        charged = {key: sum(row["exclusive"][key] for row in self.phases.values())
                   for key in CLOCK_FIELDS}
        residual = {key: total[key] - charged[key] for key in CLOCK_FIELDS}
        if any(v < -1.e-9 for v in residual.values()):
            raise ArithmeticError("PHASE_ACCOUNTING_OVERCOUNT")
        return {"phases": self.phases, "measured_interval": total,
                "exclusive_sum": charged, "unattributed": residual,
                "accounting_status": "VALID" if self.accounting_valid else "INVALID_PROFILING_ERROR",
                "profiling_errors": list(self.profiling_errors),
                "process_tree_cpu_s": total["parent_cpu_s"] + total["children_cpu_s"],
                "cpu_at_interval_entry_s": self.start["parent_cpu_s"] + self.start["children_cpu_s"],
                "scope": "phase costs within the launched verifier; includes reaped children; "
                         "ends at this summary clock sample, before profile closeout; "
                         "nested inclusive times must not be added together",
                "excluded_tail": ["profile receipt read/hash/write/fsync", "final journal/console output",
                                  "backup transfer and recovery"]}


def write_stored_history(file, **arrays):
    """Write the same five NPY payloads with ZIP_STORED, without dtype casts.

    Only the NPZ container encoding changes. The file digest is intentionally
    distinct; downstream receipts must record the new digest. No pickle or
    caller-array mutation is allowed. A failed partial file is preserved.
    """
    if set(arrays) != HISTORY_FIELDS:
        raise ValueError("U6_HISTORY_FIELDS")
    checked = {key: np.asarray(value) for key, value in arrays.items()}
    if any(value.dtype.hasobject for value in checked.values()):
        raise ValueError("U6_HISTORY_OBJECT_DTYPE")
    path = Path(file)
    if path.suffix != ".npz":
        raise ValueError("U6_HISTORY_NPZ_SUFFIX")
    with path.open("xb") as stream:
        np.savez(stream, **checked)
        stream.flush()
        os.fsync(stream.fileno())


class HistoryNumpyProxy:
    """Module-local adapter: other importers keep the original NumPy module."""
    def __init__(self, module, ledger, container):
        if container not in ("compressed", "stored"):
            raise ValueError("HISTORY_CONTAINER")
        self.module, self.ledger, self.container = module, ledger, container

    def __getattr__(self, name):
        return getattr(self.module, name)

    def savez_compressed(self, file, *args, **kwargs):
        with self.ledger.measure("history_write"):
            if self.container == "compressed":
                return self.module.savez_compressed(file, *args, **kwargs)
            if args:
                raise ValueError("NAMED_U6_HISTORY_FIELDS_REQUIRED")
            return write_stored_history(file, **kwargs)


@contextmanager
def instrument_verifier(verifier, owned_integrator, ledger, *, container="compressed"):
    """Inject the already-tested owner, measure phases, then restore bindings."""
    if verifier.CPU_CAP != 60 or verifier.WALL_CAP != 180:
        raise ValueError("LEGACY_RESOURCE_CAP_DRIFT")
    originals = {}

    def replace(name, value):
        originals[name] = getattr(verifier, name)
        setattr(verifier, name, value)

    try:
        for name, label in (("verify_source_closure", "source_closure"),
                            ("load_frozen_checkpoint", "checkpoint_load"),
                            ("safe_extract_source", "original_source_extract"),
                            ("make_hmla_source", "python_source_setup"),
                            ("CombinedOracle", "common_oracle_setup"),
                            ("compare_native_stream", "native_stream_validation")):
            replace(name, ledger.wrap(label, getattr(verifier, name)))
        for name in ("check_one_source", "causal_link_count"):
            replace(name, ledger.wrap(name, getattr(verifier, name), durable=False))

        native_run = verifier._run

        def measured_native(cmd, cwd, stdout, stderr, **kwargs):
            labels = {"native_build_stdout.txt": "native_build",
                      "common_build_stdout.txt": "common_build",
                      "native_oracle_stdout.csv": "native_run"}
            label = labels.get(Path(stdout).name, "native_subprocess")
            with ledger.measure(label):
                return native_run(cmd, cwd, stdout, stderr, **kwargs)
        replace("_run", measured_native)

        def measured_integrator(*args, **kwargs):
            for name in ("on_attempt", "observer", "on_accept"):
                fn = kwargs.get(name)
                if fn is not None:
                    kwargs[name] = ledger.wrap("callback_" + name, fn, durable=False)
            with ledger.measure("owned_integration"):
                return owned_integrator(*args, **kwargs)
        replace("integrate_u6_rt_boundary", measured_integrator)
        replace("np", HistoryNumpyProxy(verifier.np, ledger, container))
        yield
    finally:
        for name, value in reversed(tuple(originals.items())):
            setattr(verifier, name, value)


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

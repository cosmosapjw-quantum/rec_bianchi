"""Bounded Rust/Rayon audit of immutable saved photon prefix columns.

This adapter changes verification work only.  It neither calls the physical C
operator nor advances a photon history.  Scalar libm and every prefix field are
retained.  A failed block is discarded; its earliest bad row is reported.
"""
from __future__ import annotations

import ctypes as ct
import hashlib
import json
import math
import os
from pathlib import Path
import threading

import numpy as np


class RecStatus(ct.Structure):
    _fields_ = [("code", ct.c_int32), ("row", ct.c_size_t),
                ("detail", ct.c_int32), ("processed_rows", ct.c_size_t)]


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def library_from_build(path):
    """Reject changed executable or source; a compiler receipt is not a PASS."""
    from build_r3p_rust import source_hashes
    report = json.loads(Path(path).read_text())
    if report.get("schema") != "rec.r3p.audit-build.v1" or report.get("status") != "BUILT":
        raise ValueError("R3P_BUILD_NOT_SUCCESSFUL")
    root = Path(__file__).resolve().parents[1]
    if report.get("source_sha256") != source_hashes():
        raise ValueError("R3P_BUILD_SOURCE_CLOSURE_CHANGED_OR_INCOMPLETE")
    vendor = json.loads((root / "rust/REC_STREAM_AUDIT_VENDOR.json").read_text())
    if (report.get("vendor_sha256") != vendor["sha256"]
            or sha256(root / vendor["file"]) != vendor["sha256"]):
        raise ValueError("R3P_BUILD_VENDOR_CHANGED")
    library = Path(report["library"]).resolve()
    if sha256(library) != report["library_sha256"]:
        raise ValueError("R3P_BUILD_LIBRARY_CHANGED")
    return library


def _f64(value, shape=None):
    a = np.asarray(value)
    if a.dtype != np.dtype("float64") or (shape is not None and a.shape != shape):
        raise ValueError("R3P_F64_SHAPE")
    return np.ascontiguousarray(a)


def _ptr(array):
    return array.ctypes.data_as(ct.POINTER(ct.c_double))


class PrefixAuditor:
    """Own a local pool; thread count is explicit and bounded by CPU affinity."""

    def __init__(self, library, *, threads=1, block_columns=32):
        affinity = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (os.cpu_count() or 1)
        if type(threads) is not int or not 1 <= threads <= min(4, affinity):
            raise ValueError("R3P_THREADS_1_TO_MIN4_AFFINITY")
        if type(block_columns) is not int or not 1 <= block_columns <= 64:
            raise ValueError("R3P_BLOCK_COLUMNS_1_TO_64")
        self.library = Path(library).resolve()
        self.lib = ct.CDLL(str(self.library))
        self.lib.rec_prefix_new.argtypes = [ct.c_size_t]
        self.lib.rec_prefix_new.restype = ct.c_void_p
        self.lib.rec_prefix_free.argtypes = [ct.c_void_p]
        self.lib.rec_prefix_free.restype = None
        double = ct.POINTER(ct.c_double)
        self.lib.rec_prefix_audit.argtypes = [ct.c_void_p, ct.c_char_p, ct.c_size_t,
            ct.c_size_t, ct.c_size_t, double, ct.c_size_t, double, ct.c_size_t,
            double, ct.c_size_t, double, ct.c_size_t, ct.POINTER(RecStatus)]
        self.lib.rec_prefix_audit.restype = ct.c_int
        self.lib.rec_ratio_batch.argtypes = [ct.c_size_t, double, double, double, double]
        self.lib.rec_ratio_batch.restype = ct.c_int
        self.handle = self.lib.rec_prefix_new(threads)
        if not self.handle:
            raise RuntimeError("R3P_RUST_POOL_CREATION_FAILED")
        self.threads, self.block_columns = threads, block_columns
        self.lock = threading.Lock()
        self.stats = {"calls": 0, "validated_columns": 0, "validated_records": 0,
                      "attempted_records": 0, "guard_checks": 0, "threads": threads,
                      "block_columns": block_columns, "max_text_bytes": 0,
                      "max_array_scratch_bytes": 0}

    def close(self):
        with self.lock:
            if self.handle:
                self.lib.rec_prefix_free(self.handle)
                self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def audit_block(self, text, start_col, py, tr, energies):
        """Return parsed native columns. No output is committed on failure."""
        if not isinstance(text, bytes) or not 0 < len(text) <= 4194304:
            raise ValueError("R3P_TEXT_BYTES_LIMIT")
        if type(start_col) is not int or not 0 <= start_col <= 2**53:
            raise ValueError("R3P_START_COLUMN")
        py = _f64(py)
        if py.ndim != 2 or py.shape[1] != 314 or not 1 <= len(py) <= 64:
            raise ValueError("R3P_BLOCK_SHAPE")
        n = len(py)
        tr, energies = _f64(tr, (n,)), _f64(energies, (314,))
        native = np.empty_like(py)
        status = RecStatus()
        with self.lock:
            if not self.handle:
                raise RuntimeError("R3P_AUDITOR_CLOSED")
            code = self.lib.rec_prefix_audit(self.handle, text, len(text), start_col, n,
                _ptr(py), py.size, _ptr(tr), tr.size, _ptr(energies), energies.size,
                _ptr(native), native.size, ct.byref(status))
        self.stats["calls"] += 1
        self.stats["attempted_records"] += int(status.processed_rows)
        self.stats["max_text_bytes"] = max(self.stats["max_text_bytes"], len(text))
        self.stats["max_array_scratch_bytes"] = max(self.stats["max_array_scratch_bytes"],
            py.nbytes + native.nbytes + tr.nbytes + energies.nbytes)
        if code:
            position = start_col * 314 + int(status.row)
            if code == 19:
                col, slot = divmod(position, 314)
                tag, b = ("PV", slot) if slot < 311 else ("PL", slot-311)
                raise ArithmeticError(f"C_PREFIX_PARITY:{col}:{b}:{tag}")
            if code in (14, 15):
                raise ArithmeticError("C_PREFIX_NONFINITE")
            if code in (10, 11, 12, 20):
                raise ArithmeticError(f"C_PREFIX_ORDER:{position}")
            raise ArithmeticError(f"R3P_RUST_PREFIX:{code}:{position}:{status.detail}")
        self.stats["validated_columns"] += n
        self.stats["validated_records"] += n * 314
        return native

    def ratios(self, py, native, fbb):
        """Independent-lane SIMD candidate; this does not apply a parity gate."""
        p, c, b = (_f64(x) for x in (py, native, fbb))
        if p.ndim != 1 or p.shape != c.shape or p.shape != b.shape or len(p) > 20096:
            raise ValueError("R3P_RATIO_SHAPE")
        out = np.empty_like(p)
        code = self.lib.rec_ratio_batch(len(p), _ptr(p), _ptr(c), _ptr(b), _ptr(out))
        if code:
            raise ArithmeticError(f"R3P_RUST_RATIO:{code}")
        return out

    def __call__(self, *, first, rows, result, c, table, cv, cl, guard):
        from verify_r3i_h2_u6_rt_boundary import PREFIX_COLUMNS, RT_IZ, KB_EV_K, LINE_EV
        p = PREFIX_COLUMNS
        if (result.virtual_out.shape[0] != 311 or result.lyman_out.shape[0] != 3
                or result.virtual_out.shape[1] < p or result.lyman_out.shape[1] < p
                or cv.shape[0] != 311 or cl.shape[0] != 3 or cv.shape[1] < p or cl.shape[1] < p):
            raise ValueError("R3P_PREFIX_HISTORY_SHAPE")
        energies = np.concatenate((np.asarray(table.energy_eV, dtype=np.float64),
                                   np.asarray(LINE_EV, dtype=np.float64)))
        pending = first
        for start in range(0, p, self.block_columns):
            count = min(self.block_columns, p-start)
            lines = []
            text_chars = 0
            # Retain the old line-number watchdog and additionally guard every
            # bounded batch. Guard timing is intentionally not a performance
            # invariant; numerical row order and first bad record are invariant.
            guard("native_stream_rust_block")
            self.stats["guard_checks"] += 1
            for _ in range(count*314):
                if pending is not None:
                    line_no, line = pending
                    pending = None
                else:
                    try:
                        line_no, line = next(rows)
                    except StopIteration:
                        # Let the ordered Rust parser inspect earlier records
                        # before reporting the missing row.  An eager EOF error
                        # here would hide an earlier numerical failure.
                        break
                if line_no % 4096 == 0:
                    guard("native_stream")
                    self.stats["guard_checks"] += 1
                text_chars += len(line)
                if text_chars > 4194304:
                    raise ValueError("R3P_TEXT_BYTES_LIMIT")
                lines.append(line)
            if not lines:
                raise ArithmeticError("C_PREFIX_INCOMPLETE_AT_BASE")
            py = np.empty((count,314), dtype=np.float64)
            py[:,:311] = result.virtual_out[:,start:start+count].T
            py[:,311:] = result.lyman_out[:,start:start+count].T
            tr = np.fromiter((KB_EV_K*c.T0_K*(1.+c.redshift(RT_IZ+col))
                              for col in range(start,start+count)), dtype=np.float64, count=count)
            native = self.audit_block("".join(lines).encode("utf-8"), start, py, tr, energies)
            cv[:,start:start+count] = native[:,:311].T
            cl[:,start:start+count] = native[:,311:].T
            guard("native_stream_rust_block_done")
            self.stats["guard_checks"] += 1
        return {"PV":p*311, "PL":p*3, "prefix_position":p*314}

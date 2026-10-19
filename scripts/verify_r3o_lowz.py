#!/usr/bin/env python3
"""Bounded h2 low-z verifier and allocation-gated production runner.

preflight reads identities only. smoke performs at most 32 new low-z steps.
full requires a current explicit allocation and a same-code 16+ step smoke.
The source capsule need not be a git checkout; content identity is recorded.
"""
from __future__ import annotations

import argparse
import ctypes
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback
import zipfile

START_WALL = time.monotonic()
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from full_bianchi_hyrec.trajectory.primordial_2012_refined_low_z import (
    DLNA, END_IZ, HISTORICAL_STATUS, MAX_STEPS, R3M_FILES, SOURCE_NZ,
    SOURCE_ZIP_SHA256, START_IZ, HyRec2012Cosmology, LowZCheckpoint,
    continue_refined_low_z, input_hashes, load_reviewed_u6_boundary, sha256,
    source_stage_guard, source_z0_cubic,
)
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable

SOURCE_ZIP = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
HARNESS = ROOT / "scripts/c_harness/original_hyrec_r3o_lowz_harness.c"
H2_HEADER_SHA256 = "e83d8031975c0a64cdb45a2b8ba03a4a0a75c85fac5cf2437aadc915e25751bf"
PARENT_HEAD = "23e0a3a6c439a1f015aa8f7380f4eedf0b569df7"
STATE_TOLERANCES = {"xe": 5.e-9, "Tm_K": 5.e-10}
RHS_TOLERANCES = {"hydrogen_rhs": 3.e-10, "thermal_rhs": 2.e-10}


def dump_new(path: Path, data) -> None:
    with Path(path).open("x") as stream:
        json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def reserve_output(path: Path) -> Path:
    path = Path(path).absolute()
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise ValueError("R3O_OUTPUT_EXISTS_PRESERVE_PRIOR_EVIDENCE") from exc
    return path


def source_tree_hashes(src: Path) -> dict:
    result = {}
    for path in sorted(Path(src).rglob("*")):
        if path.is_symlink():
            raise ValueError("R3O_SOURCE_SYMLINK")
        if path.is_file():
            result[path.relative_to(src).as_posix()] = sha256(path)
    return result


def prepare_source(archive: Path, dest: Path) -> tuple[Path, dict]:
    """Extract into a new directory; only the copied source clock is changed."""
    if sha256(archive) != SOURCE_ZIP_SHA256:
        raise ValueError("R3O_ORIGINAL_SOURCE_ZIP_HASH")
    Path(dest).mkdir(parents=True, exist_ok=False)
    original = {}
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            rel = Path(info.filename)
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError("R3O_UNSAFE_SOURCE_MEMBER")
            if info.is_dir() or not rel.parts or rel.parts[0] != "HyRec":
                continue
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("R3O_SOURCE_ARCHIVE_SYMLINK")
            data = zf.read(info)
            sub = Path(*rel.parts[1:])
            path = Path(dest) / sub
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(data)
            original[sub.as_posix()] = hashlib.sha256(data).hexdigest()
    if source_tree_hashes(dest) != original:
        raise ValueError("R3O_EXTRACTED_SOURCE_MISMATCH")
    header = Path(dest) / "hyrec_params.h"
    before = header.read_bytes()
    old = b"#define DLNA          8.49e-5"
    new = b"#define DLNA          (8.49e-5/2.)"
    if before.count(old) != 1:
        raise ValueError("R3O_SOURCE_CLOCK_PATCH_COUNT")
    after = before.replace(old, new)
    if after.replace(new, old) != before or hashlib.sha256(after).hexdigest() != H2_HEADER_SHA256:
        raise ValueError("R3O_SOURCE_CLOCK_PATCH_IDENTITY")
    header.write_bytes(after)  # isolated, newly created copy only
    modified = source_tree_hashes(dest)
    if {k for k in modified if modified[k] != original[k]} != {"hyrec_params.h"}:
        raise ValueError("R3O_UNEXPECTED_SOURCE_MODIFICATION")
    return Path(dest), {"source_zip_sha256": SOURCE_ZIP_SHA256,
                        "original_members": original, "compiled_members": modified,
                        "change": "hyrec_params.h DLNA only: (8.49e-5/2.)"}


def code_hashes() -> dict:
    """Hash imported project sources, this runner, and its native harness."""
    paths = {Path(__file__).resolve(), HARNESS.resolve()}
    for module in list(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename:
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT / "src") and path.suffix == ".py":
                paths.add(path)
    return {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted(paths)}


def process_tree_cpu_s() -> float:
    own = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime


def live_child_cpu_s(pid: int) -> float:
    """Linux accounting for this launched compiler and its live descendants.

    RUSAGE_CHILDREN sees the compiler only after wait(); include its already
    reaped children (cutime/cstime) and currently live children while polling.
    """
    try:
        stat = Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()
        ticks = sum(int(stat[i]) for i in (11, 12, 13, 14))
        children = Path(f"/proc/{pid}/task/{pid}/children").read_text().split()
    except FileNotFoundError:
        return 0.
    return ticks / os.sysconf("SC_CLK_TCK") + sum(live_child_cpu_s(int(p)) for p in children)


class BudgetStop(RuntimeError):
    pass


class ResourceBudget:
    """Measured aggregate CPU + wall budget, retaining explicit recovery time."""

    def __init__(self, limits: dict, *, apply_os_limits=True):
        self.limits = limits
        self.work_cpu = limits["cpu_s"] - limits["recovery_cpu_s"]
        self.work_wall = limits["wall_s"] - limits["recovery_wall_s"]
        if apply_os_limits:
            memory = int(limits["memory_bytes"])
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            if hard != resource.RLIM_INFINITY:
                memory = min(memory, hard)
            resource.setrlimit(resource.RLIMIT_AS, (memory, hard))
            soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
            cpu = math.ceil(limits["cpu_s"])
            if hard != resource.RLIM_INFINITY:
                cpu = min(cpu, hard)
            resource.setrlimit(resource.RLIMIT_CPU, (cpu, hard))
            signal.signal(signal.SIGXCPU, self._signal)
            signal.signal(signal.SIGALRM, self._signal)
            signal.setitimer(signal.ITIMER_REAL, max(.001, self.work_wall - (time.monotonic() - START_WALL)))

    @staticmethod
    def _signal(signum, frame):
        raise BudgetStop(f"R3O_RESOURCE_SIGNAL:{signum}")

    def check(self, *_, live_cpu_s=0.):
        if process_tree_cpu_s() + live_cpu_s >= self.work_cpu:
            raise BudgetStop("R3O_AGGREGATE_CPU_WORK_LIMIT")
        if time.monotonic() - START_WALL >= self.work_wall:
            raise BudgetStop("R3O_WALL_WORK_LIMIT")

    def compile(self, command: list[str], cwd: Path, out: Path, err: Path) -> dict:
        self.check()
        remaining = max(1, math.ceil(self.work_cpu - process_tree_cpu_s()))
        before = process_tree_cpu_s()
        wall = time.monotonic()

        def child_limits():
            resource.setrlimit(resource.RLIMIT_CPU, (remaining, remaining + 1))

        with out.open("xb") as stdout, err.open("xb") as stderr:
            process = subprocess.Popen(command, cwd=cwd, stdout=stdout, stderr=stderr,
                                       start_new_session=True, preexec_fn=child_limits)
            try:
                while process.poll() is None:
                    self.check(live_cpu_s=live_child_cpu_s(process.pid))
                    time.sleep(.025)
            except BaseException:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise
        result = {"command": command, "returncode": process.returncode,
                  "wall_s": time.monotonic() - wall,
                  "process_tree_cpu_s": process_tree_cpu_s() - before,
                  "child_cpu_limit_s": remaining,
                  "stdout_sha256": sha256(out), "stderr_sha256": sha256(err)}
        self.check()
        if process.returncode != 0:
            raise RuntimeError(f"R3O_NATIVE_BUILD_FAILED:{process.returncode}")
        return result


def validate_allocation(record: dict, now: datetime, code: dict) -> dict:
    """A new allocation is separate from the closed historical budget."""
    identifier = record.get("allocation_id")
    if (not isinstance(identifier, str) or not identifier.strip() or
            "CLOSED" in identifier.upper() or record.get("allow_full_lowz") is not True or
            record.get("parent_coordination_confirmed") is not True or
            record.get("dual_review_acknowledged") is not True or
            record.get("historical_budget_status") != "CLOSED_HOLD_NOT_RESET" or
            record.get("source_code_sha256") != code):
        raise ValueError("R3O_CURRENT_ALLOCATION_OR_CODE_BINDING_REQUIRED")
    try:
        issued = datetime.fromisoformat(record["issued_at_utc"].replace("Z", "+00:00"))
        expires = datetime.fromisoformat(record["expires_at_utc"].replace("Z", "+00:00"))
        if issued.tzinfo is None or expires.tzinfo is None or not issued <= now < expires:
            raise ValueError("expired or future allocation")
        limits = {k: float(record[k]) for k in ("cpu_s", "wall_s", "recovery_cpu_s", "recovery_wall_s")}
        limits["memory_bytes"] = int(record["memory_bytes"])
        if (not all(math.isfinite(v) for v in limits.values()) or
                not 0. < limits["recovery_cpu_s"] < limits["cpu_s"] or
                not 0. < limits["recovery_wall_s"] < limits["wall_s"] or
                not 256 * 1024**2 <= limits["memory_bytes"] <= 16 * 1024**3 or
                limits["wall_s"] > (expires - now).total_seconds()):
            raise ValueError("invalid resource allocation")
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("R3O_INVALID_OR_EXPIRED_ALLOCATION") from exc
    return limits


def validate_smoke(record: dict, code: dict) -> None:
    if (record.get("status") != "SMOKE_PASS_SAME_H_PENDING_REVIEW" or
            record.get("mode") != "smoke" or not 16 <= record.get("accepted_steps", 0) <= 32 or
            record.get("source_code_sha256") != code or
            record.get("inputs_before") != {**R3M_FILES, "source_zip": SOURCE_ZIP_SHA256} or
            record.get("inputs_after") != record.get("inputs_before") or
            record.get("source_copy_unchanged") is not True or
            record.get("code_unchanged") is not True or record.get("failure") is not None or
            record.get("same_h", {}).get("compared_steps") != record.get("accepted_steps") or
            record.get("historical_status") != HISTORICAL_STATUS):
        raise ValueError("R3O_SAME_CODE_REVIEWABLE_SMOKE_REQUIRED")


class NativeLowZ:
    def __init__(self, library: Path, source_dir: Path):
        self.library = ctypes.CDLL(str(Path(library).resolve()))
        self.init = self.library.rec_r3o_lowz_init
        self.init.argtypes = []
        self.init.restype = ctypes.c_int
        old = Path.cwd()
        try:
            os.chdir(source_dir)
            status = self.init()
        finally:
            os.chdir(old)
        if status:
            raise RuntimeError(f"R3O_NATIVE_INIT:{status}")
        self.step_func = self.library.rec_r3o_lowz_step
        self.step_func.argtypes = [ctypes.c_long, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
        self.step_func.restype = ctypes.c_int
        self.rhs_func = self.library.rec_r3o_lowz_rhs
        self.rhs_func.argtypes = [ctypes.c_long, ctypes.c_int, ctypes.c_double, ctypes.c_double,
                                  ctypes.POINTER(ctypes.c_double)]
        self.rhs_func.restype = ctypes.c_int
        self.guard_func = self.library.rec_r3o_lowz_guard
        self.guard_func.argtypes = [ctypes.c_double, ctypes.c_double]
        self.guard_func.restype = ctypes.c_int
        self.interp_func = self.library.rec_r3o_lowz_z0
        self.interp_func.argtypes = [ctypes.POINTER(ctypes.c_double)]
        self.interp_func.restype = ctypes.c_double
        self.library.rec_r3o_lowz_dlna.restype = ctypes.c_double
        self.library.rec_r3o_lowz_nz.restype = ctypes.c_long
        if self.library.rec_r3o_lowz_dlna() != DLNA or self.library.rec_r3o_lowz_nz() != SOURCE_NZ:
            raise ValueError("R3O_NATIVE_GRID_IDENTITY")
        self.c = HyRec2012Cosmology()

    def guard(self, cp: LowZCheckpoint) -> tuple[bool, str | None]:
        reason = self.guard_func(self.c.redshift(cp.iz), cp.Tm_K)
        if reason not in (0, 1, 2):
            raise ValueError("R3O_NATIVE_GUARD_FAILURE")
        return reason == 0, {0: None, 1: "TR_MIN", 2: "TM_TR_MIN"}[reason]

    def rhs(self, cp: LowZCheckpoint) -> tuple[str, float, float]:
        out = (ctypes.c_double * 2)()
        model = self.rhs_func(cp.iz, int(cp.peebles_event_iz is not None), cp.xe, cp.Tm_K, out)
        if model not in (0, 2) or not all(math.isfinite(x) for x in out):
            raise ArithmeticError(f"R3O_NATIVE_RHS_FAILURE:{model}")
        return ("EMLA2s2p" if model == 2 else "PEEBLES"), out[0], out[1]

    def step(self, cp: LowZCheckpoint) -> tuple[LowZCheckpoint, str]:
        cp.validate(self.c)
        if cp.iz >= END_IZ:
            raise ArithmeticError("R3O_NATIVE_STEP_FAILURE:SOURCE_END_OUTPUT_ONLY")
        state = (ctypes.c_double * 6)(cp.xe, cp.Tm_K, cp.hydrogen_prev,
                                     cp.hydrogen_prev2, cp.thermal_prev, cp.thermal_prev2)
        guard, reason = self.guard(cp)
        model = self.step_func(cp.iz, int(cp.peebles_event_iz is not None), state)
        if model not in (0, 2):
            raise ArithmeticError(f"R3O_NATIVE_STEP_FAILURE:{model}")
        event, why = cp.peebles_event_iz, cp.peebles_event_reason
        if event is None and not guard:
            event, why = cp.iz, reason
        result = LowZCheckpoint(cp.iz + 1, *state, event, why)
        result.validate(self.c)
        return result, "EMLA2s2p" if model == 2 else "PEEBLES"

    def z0(self, tail) -> float:
        values = np.asarray(tail, dtype=float)
        if values.shape != (4,) or not np.all(np.isfinite(values)):
            raise ValueError("R3O_NATIVE_Z0_TAIL")
        result = self.interp_func((ctypes.c_double * 4)(*values))
        if not math.isfinite(result):
            raise ArithmeticError("R3O_NATIVE_Z0_NONFINITE")
        return result


def compare_state(py: LowZCheckpoint, native: LowZCheckpoint, maxima: dict) -> None:
    if (py.iz != native.iz or py.peebles_event_iz != native.peebles_event_iz or
            py.peebles_event_reason != native.peebles_event_reason):
        raise ArithmeticError("R3O_NATIVE_PY_STAGE_OR_GRID_MISMATCH")
    for field, limit in STATE_TOLERANCES.items():
        pv, cv = getattr(py, field), getattr(native, field)
        ratio = abs(pv - cv) / max(abs(cv), 1.e-8 if field == "xe" else 1.)
        maxima[field] = max(maxima.get(field, 0.), ratio)
        if not math.isfinite(ratio) or ratio > limit:
            raise ArithmeticError(f"R3O_SAME_H_STATE:{field}:{py.iz}:{ratio}")
    for field in ("hydrogen_prev", "hydrogen_prev2", "thermal_prev", "thermal_prev2"):
        ratio = abs(getattr(py, field) - getattr(native, field)) / max(1., abs(getattr(native, field)))
        maxima[field] = max(maxima.get(field, 0.), ratio)
        if not math.isfinite(ratio) or ratio > 2.e-8:
            raise ArithmeticError(f"R3O_SAME_H_MEMORY:{field}:{py.iz}:{ratio}")


def run(args) -> int:
    ev = reserve_output(args.evidence_dir)
    report = {"schema": "rec.r3o.lowz.v1", "status": "INCOMPLETE", "mode": args.mode,
              "parent_head": PARENT_HEAD, "source_identity_kind": "content-addressed source capsule or checkout",
              "failure": None, "historical_status": dict(HISTORICAL_STATUS),
              "independent_review": "NOT_RUN_PARENT_REQUIRED", "full_U6": "REUSED_PR107",
              "h_h2_h4_convergence": "NOT_RUN", "Bianchi_REI_CMB_admission": False,
              "source_code_sha256": code_hashes(), "accepted_steps": 0}
    native_cp = None
    latest = None
    sequence = 0
    src = None
    source_record = None
    budget = None
    extra_inputs = {}
    ledger = None
    exit_code = 2
    c = HyRec2012Cosmology()
    native_states = []
    sampled = []
    maxima = {}
    common = {"hydrogen_rhs": 0., "thermal_rhs": 0.}

    def checkpoint(record):
        nonlocal latest, sequence
        latest = record
        report["accepted_steps"] = record["accepted_steps"]
        sealed = {**record, "schema": "rec.r3o.lowz.checkpoint.v1",
                  "native_checkpoint": asdict(native_cp) if native_cp else None,
                  "source_code_sha256": report["source_code_sha256"],
                  "inputs_sha256": report.get("inputs_before"),
                  "historical_status": dict(HISTORICAL_STATUS)}
        path = ev / f"checkpoint_{sequence:05d}.json"
        dump_new(path, sealed)
        report["last_checkpoint"] = {"path": path.name, "sha256": sha256(path)}
        sequence += 1

    try:
        if args.mode == "full":
            if args.allocation_json is None or args.smoke_verification is None:
                raise ValueError("R3O_FULL_REQUIRES_CURRENT_ALLOCATION_AND_SMOKE")
            for path in (args.allocation_json, args.smoke_verification):
                if path.is_symlink():
                    raise ValueError("R3O_CONTROL_INPUT_SYMLINK")
                extra_inputs[str(path.resolve())] = sha256(path)
            allocation = json.loads(args.allocation_json.read_text())
            limits = validate_allocation(allocation, datetime.now(timezone.utc), report["source_code_sha256"])
            smoke = json.loads(args.smoke_verification.read_text())
            validate_smoke(smoke, report["source_code_sha256"])
            report["allocation"] = allocation
            report["smoke_receipt_sha256"] = sha256(args.smoke_verification)
            count = MAX_STEPS
        else:
            limits = {"cpu_s": 20., "wall_s": 60., "memory_bytes": 2 * 1024**3,
                      "recovery_cpu_s": 3., "recovery_wall_s": 8.}
            count = args.steps
            if type(count) is not int or not 1 <= count <= 32:
                raise ValueError("R3O_SMOKE_CAP_1_TO_32")
        report["limits"] = limits
        budget = ResourceBudget(limits)
        report["inputs_before"] = input_hashes(args.raw_dir, args.source_zip)
        boundary = load_reviewed_u6_boundary(args.raw_dir, args.source_zip)
        budget.check()
        py_cp = boundary["python"]
        native_cp = boundary["native"]
        native_states = [native_cp]
        report["start"] = {"python": asdict(py_cp), "native": asdict(native_cp)}
        report["end_contract"] = {"start_iz": START_IZ, "source_nz": SOURCE_NZ,
                                  "end_iz": END_IZ, "production_steps": MAX_STEPS, "dlna": DLNA,
                                  "last_z": c.redshift(END_IZ), "last_rhs_z": c.redshift(END_IZ - 1)}
        compare_state(py_cp, native_cp, maxima)
        checkpoint({"phase": "INPUT_VERIFIED", "checkpoint": asdict(py_cp),
                    "accepted_steps": 0, "state_tail": [asdict(py_cp)], "failure": None})
        if args.mode == "preflight":
            report["status"] = "PREFLIGHT_ONLY"
            exit_code = 0
        else:
            src, source_record = prepare_source(args.source_zip, ev / "source_h2")
            dump_new(ev / "source_manifest.json", source_record)
            command = [args.cc, "-std=gnu99", "-O2", "-fno-fast-math", "-ffp-contract=off",
                       "-shared", "-fPIC", "-I", str(src), str(HARNESS),
                       *[str(src / name) for name in ("history.c", "hydrogen.c", "helium.c", "hyrectools.c")],
                       "-lm", "-o", str(ev / "liboriginal_r3o_lowz.so")]
            report["native_build"] = budget.compile(command, src, ev / "build_stdout.txt", ev / "build_stderr.txt")
            report["native_binary_sha256"] = sha256(ev / "liboriginal_r3o_lowz.so")
            oracle = NativeLowZ(ev / "liboriginal_r3o_lowz.so", src)
            source = make_hmla_source(c, OriginalHyRecPrimitiveRateTable.from_archive(args.source_zip))
            ledger = (ev / "accepted_pairs.jsonl").open("x", buffering=1)

            def accepted(current, candidate, step):
                nonlocal native_cp
                before_native = native_cp
                native_cp, native_model = oracle.step(native_cp)
                native_states.append(native_cp)
                entry = {"python": asdict(candidate), "native": asdict(native_cp), "step": step}
                # Retain actual pair before any verification can fail.
                ledger.write(json.dumps(entry, sort_keys=True, allow_nan=False) + "\n")
                n = candidate.iz - START_IZ
                if n <= 2 or n % 4096 == 0 or candidate.peebles_event_iz == current.iz:
                    ledger.flush()
                    os.fsync(ledger.fileno())
                if step["model"] != native_model:
                    raise ArithmeticError("R3O_NATIVE_PY_MODEL_SEQUENCE")
                compare_state(candidate, native_cp, maxima)
                # Fixed cadence plus transition-neighbour coverage: actual inputs.
                if (n <= 3 or n % 4096 == 0 or n == count or
                        candidate.peebles_event_iz in (current.iz, current.iz - 1) or
                        native_cp.peebles_event_iz != before_native.peebles_event_iz):
                    if oracle.guard(current) != source_stage_guard(c, c.redshift(current.iz), current.Tm_K):
                        raise ArithmeticError("R3O_COMMON_GUARD_ORDER")
                    model, fh, ft = oracle.rhs(current)
                    if model != step["model"]:
                        raise ArithmeticError("R3O_COMMON_INPUT_MODEL")
                    for key, value, floor in (("hydrogen_rhs", fh, 1.e-13), ("thermal_rhs", ft, 1.)):
                        py_value = step[key]
                        scale = max(abs(value), abs(py_value), floor) if key == "hydrogen_rhs" else max(1., abs(value))
                        ratio = abs(py_value - value) / scale
                        common[key] = max(common[key], ratio)
                        if not math.isfinite(ratio) or ratio > RHS_TOLERANCES[key]:
                            raise ArithmeticError(f"R3O_COMMON_INPUT_RHS:{key}:{current.iz}:{ratio}")
                    sampled.append(current.iz)

            result = continue_refined_low_z(py_cp, c, source, max_steps=count,
                                           before_attempt=budget.check, on_accept=accepted,
                                           on_checkpoint=checkpoint)
            report["accepted_steps"] = result["accepted_steps"]
            report["python_status"] = result["status"]
            arrays = {k: v for k, v in result.items() if isinstance(v, np.ndarray)}
            arrays.update({"native_xe": np.array([s.xe for s in native_states]),
                           "native_Tm_K": np.array([s.Tm_K for s in native_states])})
            with (ev / "python_native_lowz.npz").open("xb") as stream:
                np.savez_compressed(stream, **arrays)
            report["history_sha256"] = sha256(ev / "python_native_lowz.npz")
            if args.mode == "full":
                if (result["status"] != "STOP_AT_SOURCE_Z0_CUBIC_STENCIL" or
                        len(native_states) != MAX_STEPS + 1 or result["z0"] is None or
                        result["checkpoint"].peebles_event_iz is None):
                    raise ValueError("R3O_FULL_SOURCE_END_OR_PEEBLES_EVENT_MISSING")
                z0 = {}
                for key, limit in STATE_TOLERANCES.items():
                    value = result["z0"][key]["value"]
                    native_value = oracle.z0([getattr(s, key) for s in native_states[-4:]])
                    common_value = oracle.z0(result[key][-4:])
                    # Same-input interpolation should reproduce operation order.
                    if np.float64(value).tobytes() != np.float64(common_value).tobytes():
                        raise ArithmeticError(f"R3O_Z0_COMMON_INPUT_BYTE_PARITY:{key}")
                    ratio = abs(value - native_value) / max(abs(native_value), 1.e-8 if key == "xe" else 1.)
                    if not math.isfinite(ratio) or ratio > limit:
                        raise ArithmeticError(f"R3O_Z0_INDEPENDENT_SAME_H:{key}")
                    z0[key] = {"python": value, "native": native_value, "scaled": ratio,
                               "common_input_bytes": "MATCH", "stencil": result["z0"][key]}
                report["z0"] = z0
                report["status"] = "FULL_LOWZ_SAME_H_PASS_PENDING_DUAL_REVIEW"
            else:
                report["status"] = "SMOKE_PASS_SAME_H_PENDING_REVIEW"
            exit_code = 0
    except BaseException as exc:
        report["status"] = "HOLD_RESOURCE_LIMIT" if isinstance(exc, BudgetStop) else "FAILED"
        report["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        with (ev / "exception.txt").open("x") as stream:
            traceback.print_exc(file=stream)
        exit_code = 3 if isinstance(exc, BudgetStop) else 2
    finally:
        # Resource recovery reserve pays for checkpoint/ledger closure + readback.
        signal.setitimer(signal.ITIMER_REAL, 0.)
        if ledger is not None:
            ledger.flush()
            os.fsync(ledger.fileno())
            ledger.close()
        report["same_h"] = {"compared_steps": max(0, len(native_states) - 1),
                            "maxima": maxima, "state_tolerances": STATE_TOLERANCES,
                            "common_input_maxima": common, "rhs_tolerances": RHS_TOLERANCES,
                            "common_input_globals": sampled}
        try:
            if "inputs_before" in report:
                report["inputs_after"] = input_hashes(args.raw_dir, args.source_zip)
                if report["inputs_after"] != report["inputs_before"]:
                    raise ValueError("R3O_INPUT_MUTATION_DURING_EXECUTION")
            report["code_unchanged"] = code_hashes() == report["source_code_sha256"]
            if not report["code_unchanged"]:
                raise ValueError("R3O_CODE_MUTATION_DURING_EXECUTION")
            if src is not None:
                report["source_copy_unchanged"] = source_tree_hashes(src) == source_record["compiled_members"]
                if not report["source_copy_unchanged"]:
                    raise ValueError("R3O_COMPILED_SOURCE_MUTATION")
            if "native_binary_sha256" in report and sha256(ev / "liboriginal_r3o_lowz.so") != report["native_binary_sha256"]:
                raise ValueError("R3O_NATIVE_BINARY_MUTATION")
            if any(sha256(Path(p)) != digest for p, digest in extra_inputs.items()):
                raise ValueError("R3O_ALLOCATION_OR_SMOKE_INPUT_MUTATION")
        except BaseException as exc:
            report["before_mutation_failure"] = report["failure"]
            report["status"] = "FAILED_INPUT_OR_CODE_MUTATION"
            report["failure"] = {"type": type(exc).__name__, "message": str(exc)}
            exit_code = 2
        report["resources"] = {"process_tree_cpu_s": process_tree_cpu_s(),
                               "wall_s": time.monotonic() - START_WALL,
                               "peak_parent_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                               "peak_child_rss_bytes": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
                               "address_limit_bytes": resource.getrlimit(resource.RLIMIT_AS)[0]}
        if budget is not None:
            if (report["resources"]["process_tree_cpu_s"] > budget.limits["cpu_s"] or
                    report["resources"]["wall_s"] > budget.limits["wall_s"]):
                report["status"] = "FAILED_TOTAL_RESOURCE_CAP"
                exit_code = 3
        dump_new(ev / "verification.json", report)
    print(json.dumps({"status": report["status"], "accepted_steps": report["accepted_steps"],
                      "verification": str(ev / "verification.json"), "resources": report["resources"]}, sort_keys=True))
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "smoke", "full"), required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--source-zip", type=Path, default=SOURCE_ZIP)
    parser.add_argument("--steps", type=int, default=16, help="smoke only, 1..32")
    parser.add_argument("--allocation-json", type=Path)
    parser.add_argument("--smoke-verification", type=Path)
    parser.add_argument("--cc", default="gcc")
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())

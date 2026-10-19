#!/usr/bin/env python3
"""Produce and compare independent h4 primordial starts under a small budget.

Examples (fresh output paths required):
  python scripts/verify_r3o_h4_start.py --mode helium --evidence-dir OUT/he_001
  python scripts/verify_r3o_h4_start.py --mode start --steps 8 --evidence-dir OUT/start_001

No checkpoint argument exists. C trajectory output is reference data only.
The CLI never invokes Git, cloud services or production beyond eight FULL steps.
"""
from __future__ import annotations

import argparse
import ctypes
from dataclasses import asdict
import difflib
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time
import traceback
import zipfile

os.environ.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                   "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"})
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from full_bianchi_hyrec.trajectory import primordial_2012_quarter_start as h4
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from verify_r3i_h2_start import (
    PINNED_SOURCE, FullSourceCOracle, compare_state, compare_photon_spectra,
    checked_integrated_rhs_ratio,
)

ZIP = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
H4_SOURCE_FILES = (
    "src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_start.py",
    "scripts/verify_r3o_h4_start.py",
    "scripts/c_harness/original_hyrec_r3o_h4_start_harness.c",
)
DEPENDENCIES = H4_SOURCE_FILES + (
    "src/full_bianchi_hyrec/trajectory/primordial_2012_refined_start.py",
    "src/full_bianchi_hyrec/trajectory/causal_virtual_redshift.py",
    "src/full_bianchi_hyrec/trajectory/full_2012_atomic_source.py",
    "src/full_bianchi_hyrec/trajectory/hmla_flrw.py",
    "src/full_bianchi_hyrec/trajectory/primitive_rates.py",
    "src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py",
    "src/full_bianchi_hyrec/trajectory/recombination_reference.py",
    "src/full_bianchi_hyrec/recoil/original_hyrec_native.py",
    "scripts/verify_r3i_h2_start.py",
    "scripts/c_harness/original_hyrec_full_source_harness.c",
)


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def json_new(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, sort_keys=True, indent=2, allow_nan=False)
        f.write("\n")


def prepare_source(archive: Path, destination: Path):
    """Hash every original member and publish the exact single-token diff."""
    if sha(archive) != h4.PINNED_ZIP_SHA256:
        raise ValueError("ORIGINAL_SOURCE_ZIP_SHA_MISMATCH")
    destination.mkdir(parents=True, exist_ok=False)
    hashes = {}
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            rel = Path(info.filename)
            mode = info.external_attr >> 16
            if rel.is_absolute() or ".." in rel.parts or (mode & 0o170000) == 0o120000:
                raise ValueError(f"unsafe original ZIP member {info.filename}")
            if not info.is_dir():
                hashes[info.filename] = hashlib.sha256(zf.read(info)).hexdigest()
        zf.extractall(destination)
    src = destination / "HyRec"
    for name, expected in PINNED_SOURCE.items():
        if sha(src/name) != expected:
            raise ValueError(f"ORIGINAL_SOURCE_MEMBER_SHA_MISMATCH:{name}")
    header = src / "hyrec_params.h"
    before = header.read_bytes()
    old = b"#define DLNA          8.49e-5"
    new = b"#define DLNA          (8.49e-5/4.)"
    if before.count(old) != 1:
        raise ValueError("active original DLNA token is not unique")
    after = before.replace(old, new)
    if after.replace(new, old) != before:
        raise ValueError("source diff exceeds one active DLNA token")
    header.write_bytes(after)
    expected_after = dict(hashes)
    expected_after["HyRec/hyrec_params.h"] = hashlib.sha256(after).hexdigest()
    actual = {name: sha(destination/name) for name in hashes}
    if actual != expected_after:
        raise ValueError("extracted source change exceeds one DLNA token")
    manifest = {
        "zip_sha256": h4.PINNED_ZIP_SHA256, "original_member_sha256": hashes,
        "modified_member_sha256": actual, "changed_members": ["HyRec/hyrec_params.h"],
        "exact_diff": "".join(difflib.unified_diff(
            before.decode().splitlines(keepends=True), after.decode().splitlines(keepends=True),
            fromfile="original/HyRec/hyrec_params.h", tofile="temporary/HyRec/hyrec_params.h")),
    }
    return src, manifest


def parse_native(path: Path, steps: int):
    """Require complete native rows, exact indices and a terminal receipt."""
    meta = None; node = None; done = None; helium = []; memories = {}; states = []
    spectra = {tag: {} for tag in ("V", "A", "L")}
    with Path(path).open() as handle:
        for lineno, line in enumerate(handle, 1):
            f = line.rstrip("\n").split(","); tag = f[0]
            if done is not None:
                raise ValueError("C_OUTPUT_AFTER_DONE")
            if tag == "META" and len(f) == 5 and meta is None and lineno == 1:
                meta = (float(f[1]), int(f[2]), int(f[3]), int(f[4]))
                if meta[0] != h4.DLNA or meta[1] != h4.SOURCE_INDEX_START or meta[2] <= steps or meta[3] != steps:
                    raise ValueError("C_H4_GRID_IDENTITY")
            elif tag == "HE" and len(f) == 16:
                if node is not None or int(f[1]) != len(helium):
                    raise ValueError("C_HE_ORDER")
                values = list(map(float, f[2:14])); method = int(f[14]); post = int(f[15])
                if not all(map(math.isfinite, values)) or method not in (-1, 0, 1) or post not in (0, 1):
                    raise ValueError("C_HE_NONFINITE_OR_FLAGS")
                helium.append(values + [method, post])
            elif tag in ("NODE", "STEP") and len(f) == (9 if tag == "NODE" else 12):
                offset = 1 if tag == "NODE" else 2
                if tag == "NODE":
                    if node is not None:
                        raise ValueError("C_DUPLICATE_NODE")
                    expected_index = h4.SOURCE_INDEX_START
                else:
                    if node is None or int(f[1]) != len(states) or len(states) >= steps:
                        raise ValueError("C_STEP_ORDER")
                    expected_index = h4.SOURCE_INDEX_START+len(states)+1
                names = ("z", "xH1s", "xHII", "xHeII", "xe", "Tm_K")
                row = {"iz": int(f[offset]), **dict(zip(names, map(float, f[offset+1:offset+7])))}
                post = int(f[-1]); row["post_saha"] = bool(post)
                if row["iz"] != expected_index or post not in (0, 1) or not all(math.isfinite(row[k]) for k in names):
                    raise ValueError("C_STATE_GRID_NONFINITE_OR_FLAG")
                if tag == "NODE":
                    node = row
                else:
                    row.update(hydrogen_rhs=float(f[9]), helium_rhs=float(f[10]))
                    if not all(math.isfinite(row[k]) for k in ("hydrogen_rhs", "helium_rhs")):
                        raise ValueError("C_RHS_NONFINITE")
                    states.append(row)
            elif tag in spectra and len(f) == 4:
                j, b = int(f[1]), int(f[2]); value = float(f[3]); count = 3 if tag == "L" else 311
                if not 0 <= j < steps or not 0 <= b < count or not math.isfinite(value) or (j, b) in spectra[tag]:
                    raise ValueError("C_SPECTRUM_NONFINITE_DUPLICATE_OR_INDEX")
                spectra[tag][j, b] = value
            elif tag == "MEM" and len(f) == 6:
                j = int(f[1]); values = np.array(list(map(float, f[2:]))).reshape(2, 2)
                if not -1 <= j < steps or j in memories or not np.all(np.isfinite(values)):
                    raise ValueError("C_MEMORY_NONFINITE_DUPLICATE_OR_INDEX")
                memories[j] = values
            elif tag == "DONE" and len(f) == 4:
                done = (int(f[1]), int(f[2]), float(f[3]))
            else:
                raise ValueError(f"C_UNKNOWN_OR_MALFORMED_RECORD:{lineno}:{tag}")
    if (meta is None or node is None or done != (h4.SOURCE_INDEX_START+1, steps, h4.DLNA)
            or len(helium) != h4.SOURCE_INDEX_START+1 or len(states) != steps
            or set(memories) != set(range(-1, steps))):
        raise ValueError("C_INCOMPLETE_START_RECEIPT")
    arrays = {}
    for tag, values in spectra.items():
        count = 3 if tag == "L" else 311
        if len(values) != steps*count:
            raise ValueError("C_INCOMPLETE_SPECTRUM")
        arrays[tag] = np.array([[values[j, b] for j in range(steps)] for b in range(count)])
    return {"meta": meta, "node": node, "steps": states, "helium": np.array(helium),
            "memories": memories, "spectra": arrays}


class Budget:
    def __init__(self, cpu, wall):
        self.cpu_limit = cpu; self.wall_limit = wall; self.started = time.monotonic()
        self.initial_cpu = self.cpu()
        # Recovery is part of this allowance, never a new allocation.
        self.recovery_cpu = min(2., .15*cpu)
        self.recovery_wall = min(5., .15*wall)

    @staticmethod
    def cpu():
        a = resource.getrusage(resource.RUSAGE_SELF); b = resource.getrusage(resource.RUSAGE_CHILDREN)
        return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime

    def check(self, *, total=False):
        cpu_limit = self.cpu_limit if total else self.cpu_limit-self.recovery_cpu
        wall_limit = self.wall_limit if total else self.wall_limit-self.recovery_wall
        if self.cpu()-self.initial_cpu >= cpu_limit:
            raise TimeoutError("H4_LOCAL_TOTAL_CPU_LIMIT")
        if time.monotonic()-self.started >= wall_limit:
            raise TimeoutError("H4_LOCAL_WALL_LIMIT")

    def run(self, command, cwd, prefix):
        self.check(); before = self.cpu(); started = time.monotonic()
        remaining_cpu = max(1, math.ceil(self.cpu_limit-self.recovery_cpu-(self.cpu()-self.initial_cpu)))
        remaining_wall = min(45., self.wall_limit-self.recovery_wall-(started-self.started))
        out = prefix.with_suffix(".stdout"); err = prefix.with_suffix(".stderr")
        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
            resource.setrlimit(resource.RLIMIT_CPU, (remaining_cpu, remaining_cpu+1))
        process = None; failure = None
        try:
            with out.open("xb") as so, err.open("xb") as se:
                process = subprocess.Popen(command, cwd=cwd, stdout=so, stderr=se,
                                           preexec_fn=limits, start_new_session=True)
                process.wait(timeout=remaining_wall)
        except BaseException as exc:
            failure = exc
        finally:
            if process is not None and (failure is not None or process.returncode):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
        record = {"command": list(map(str, command)), "returncode": None if process is None else process.returncode,
                  "cpu_s_including_children": self.cpu()-before,
                  "wall_s": time.monotonic()-started,
                  "stdout_sha256": sha(out), "stderr_sha256": sha(err),
                  "process_group_owned": True,
                  "failure": None if failure is None else {"type": type(failure).__name__, "message": str(failure)}}
        json_new(prefix.with_suffix(".json"), record)
        if failure is not None:
            raise failure
        self.check()
        if process.returncode:
            raise RuntimeError(f"NATIVE_SUBPROCESS_FAILED:{prefix.name}:{process.returncode}")
        return record


def compare_helium(helium, native, c, shared, budget):
    rows = native["helium"]
    names = ("z", "xe", "xHII", "xHeI", "xHeII", "xHeIII", "Tm_K")
    errors = {}
    for k, name in enumerate(names):
        py = np.array(getattr(helium, name))
        diff = np.abs(py-rows[:, k]) / np.maximum(1., np.abs(rows[:, k]))
        if not np.all(np.isfinite(diff)) or np.max(diff) > 2.e-12:
            raise ArithmeticError(f"H4_HE_STATE:{name}:{np.max(diff):.17g}")
        errors[name] = float(np.max(diff))
    methods = np.array([{"SAHA_ALGEBRAIC": -1, "POST_SAHA": 1, "SOURCE_PREDICTOR": 0}[x]
                        for x in helium.update_method])
    if not np.array_equal(methods, rows[:, 12]) or not np.array_equal(helium.post_saha, rows[:, 13]):
        raise ArithmeticError("H4_HE_STAGE_OR_POST_SAHA_FLAGS")
    for value in (np.array(helium.xHII)+helium.xHeII+2*np.array(helium.xHeIII)-helium.xe,
                  np.array(helium.xHeI)+helium.xHeII+np.array(helium.xHeIII)-c.fHe):
        if np.max(np.abs(value)) > 5.e-13:
            raise ArithmeticError("H4_HE_PARTICLE_LEDGER")
    lib = ctypes.CDLL(str(shared)); rate = lib.rec_helium_dxHeIIdlna
    rate.argtypes = [ctypes.c_double]*9; rate.restype = ctypes.c_double
    common = trajectory = 0.
    for i in np.flatnonzero(methods != -1):
        if int(i) % 512 == 0:
            budget.check()
        rhs, zin, H, x1, he = map(float, rows[i, 7:12])
        cs = rate(x1, he, c.nH0_m3, c.T0_K, c.fHe, H, zin, 1., 1.)
        py = h4.helium_rhs(c, x1, he, H, zin)
        common = max(common, checked_integrated_rhs_ratio(py, cs, 2.e-10, int(i), "He_common"))
        trajectory = max(trajectory, checked_integrated_rhs_ratio(
            float(helium.helium_rhs_dln_a[i]), rhs, 2.e-10, int(i), "He_trajectory"))
    return {"status": "PASS", "rows": len(rows), "max_state_scaled_max1": errors,
            "max_rhs_common_scaled_max1": common, "max_rhs_trajectory_scaled_max1": trajectory,
            "stage_counts": {name: helium.stage.count(name) for name in sorted(set(helium.stage))}}


def save_npz_new(path, data):
    with Path(path).open("xb") as out:
        np.savez_compressed(out, **data)
    return sha(path)


def compare_full(result, native, c, table):
    errors = {k: 0. for k in ("xHII", "xe", "xHeII", "Tm_K", "H_rhs", "He_rhs")}
    photons = {k: 0. for k in ("virtual", "average", "lyman")}
    for j, row in enumerate([native["node"]]+native["steps"]):
        py = {"iz": int(result.iz[j]), "post_saha": bool(result.post_saha[j]),
              **{k: float(getattr(result, k)[j]) for k in ("z", "xH1s", "xHII", "xHeII", "xe", "Tm_K")}}
        compare_state(py, row, j)
        for name in ("xHII", "xe", "xHeII", "Tm_K"):
            scale = 1. if name == "xHeII" else max(abs(row[name]), 1. if name == "Tm_K" else 1.e-8)
            errors[name] = max(errors[name], abs(py[name]-row[name])/scale)
    for j, row in enumerate(native["steps"]):
        for key, values, field in (("H_rhs", result.hydrogen_rhs_dln_a, "hydrogen_rhs"),
                                   ("He_rhs", result.helium_rhs_dln_a, "helium_rhs")):
            errors[key] = max(errors[key], checked_integrated_rhs_ratio(float(values[j]), row[field], 2.e-7, j, key))
        tr = h4.KB_NATIVE_EV_K*c.T0_K*(1.+float(result.z[j]))
        fbbv = 1./np.expm1(table.energy_eV/tr)
        fbbl = 1./np.expm1(np.array((10.198714553953742, 12.087365397278509, 12.748393192442178))/tr)
        p = compare_photon_spectra(
            result.virtual_out[:, j], result.average_virtual[:, j], result.lyman_out[:, j],
            native["spectra"]["V"][:, j], native["spectra"]["A"][:, j], native["spectra"]["L"][:, j],
            fbbv, fbbl, j,
        )
        for k in p:
            photons[k] = max(photons[k], p[k])
    memory_max = 0.
    for j, cs in native["memories"].items():
        if j == -1:
            py = result.initial_predictor
        else:
            prev2 = result.initial_predictor[:, 1] if j == 0 else np.array([
                result.helium_rhs_dln_a[j-1], result.hydrogen_rhs_dln_a[j-1]])
            py = np.column_stack((prev2, [result.helium_rhs_dln_a[j], result.hydrogen_rhs_dln_a[j]]))
        for av, bv in zip(py.ravel(), cs.ravel()):
            memory_max = max(memory_max, checked_integrated_rhs_ratio(float(av), float(bv), 2.e-7, j, "memory"))
    return {"status": "PASS", "nodes": len(result.iz), "columns": len(result.iz)-1,
            "max_state_and_rhs_error": errors, "max_photon_tolerance_ratio": photons,
            "max_memory_scaled_max1": memory_max, "max_matrix_residual": float(np.max(result.matrix_residual))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--mode", choices=("helium", "start"), default="start")
    parser.add_argument("--steps", type=int, default=8, choices=range(1, 9))
    parser.add_argument("--cpu-seconds", type=int, default=20, choices=range(1, 31))
    parser.add_argument("--wall-seconds", type=int, default=60, choices=range(1, 181))
    args = parser.parse_args()
    ev = args.evidence_dir.resolve()
    try:
        ev.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.exit(2, "EVIDENCE_DIR_EXISTS: use a fresh output path\n")
    budget = Budget(args.cpu_seconds, args.wall_seconds)
    before = {name: sha(ROOT/name) for name in DEPENDENCIES}
    initial_zip = sha(ZIP)
    report = {"schema": h4.HISTORY_SCHEMA, "status": "RUNNING", "mode": args.mode,
              "steps_requested": args.steps if args.mode == "start" else 0,
              "dlna": h4.DLNA, "dlna_hex": h4.DLNA.hex(), "izH0": h4.SOURCE_INDEX_START,
              "python_state_origin": "independent Python h4 source equations from z=8000",
              "checkpoint_input": None, "C_trajectory_state_imported": False,
              "source_zip_sha256": initial_zip, "producer_and_dependency_sha256": before,
              "scientific_admission": "HOLD_PENDING_INDEPENDENT_REVIEW",
              "python_h_h2_h4_convergence": "NOT_RUN", "rei_activation": False,
              "historical_U5": {"h": "HOLD_9_FAIL", "h2": "HOLD_8_FAIL"},
              "historical_budget": "CLOSED_HOLD_NOT_RESET",
              "resource_allowance": {"local_total_cpu_s": args.cpu_seconds, "wall_s": args.wall_seconds,
                                     "recovery_cpu_s_within_total": budget.recovery_cpu,
                                     "recovery_wall_s_within_total": budget.recovery_wall,
                                     "address_space_bytes": 2*1024**3, "threads": 1},
              "runtime": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
                          "platform": platform.platform(), "execution_location": "caller host; see environment"},
              "command": [sys.executable]+sys.argv, "first_failure": None}
    json_new(ev/"STARTED.json", report)
    for name in H4_SOURCE_FILES:
        p = ev/"producer_snapshot"/name; p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("xb") as handle:
            handle.write((ROOT/name).read_bytes())
    src = None; source_manifest = None
    try:
        affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else []
        if affinity:
            os.sched_setaffinity(0, {affinity[0]})
        report["runtime"]["cpu_affinity"] = affinity[:1]
        resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
        current = resource.getrusage(resource.RUSAGE_SELF)
        cap = math.ceil(current.ru_utime+current.ru_stime+args.cpu_seconds)
        resource.setrlimit(resource.RLIMIT_CPU, (cap, cap+1))
        def interrupted(*_):
            raise TimeoutError("H4_LOCAL_PROCESS_RESOURCE_LIMIT")
        signal.signal(signal.SIGALRM, interrupted); signal.signal(signal.SIGXCPU, interrupted)
        signal.alarm(args.wall_seconds)
        src, source_manifest = prepare_source(ZIP, ev/"source_extract")
        json_new(ev/"source_manifest.json", source_manifest)
        compiler = subprocess.run(["gcc", "--version"], capture_output=True, text=True, check=True, timeout=5)
        report["runtime"]["compiler"] = compiler.stdout.splitlines()[0]
        flags = ["gcc", "-std=gnu99", "-O2", "-fno-fast-math", "-I", str(src)]
        cfile = ROOT/"scripts/c_harness/original_hyrec_r3o_h4_start_harness.c"
        sources = [str(cfile)]+[str(src/f) for f in ("history.c", "hydrogen.c", "helium.c", "hyrectools.c")]
        report["native_build"] = budget.run(flags+sources+["-lm", "-o", str(ev/"native_h4_start")], src, ev/"native_build")
        report["shared_build"] = budget.run(flags+["-shared", "-fPIC", "-DR3O_H4_SHARED"]+sources+
                                            ["-lm", "-o", str(ev/"libh4_original_source.so")], src, ev/"shared_build")
        steps = args.steps if args.mode == "start" else 0
        report["native_run"] = budget.run([str(ev/"native_h4_start"), str(steps)], src, ev/"native_oracle")
        native = parse_native(ev/"native_oracle.stdout", steps)
        c = h4.QuarterStartCosmology()
        report["cosmology"] = asdict(c)
        start = time.monotonic(); cpu = budget.cpu()
        helium = h4.integrate_helium_stages(c, check_budget=budget.check)
        report["python_helium_runtime"] = {"wall_s": time.monotonic()-start, "cpu_s": budget.cpu()-cpu}
        he_data = {name: np.asarray(getattr(helium, name)) for name in (
            "iz", "z", "xe", "xHII", "xHeI", "xHeII", "xHeIII", "Tm_K", "helium_rhs_dln_a",
            "stage", "update_method", "post_saha")}
        he_data.update(dlna=h4.DLNA, source_zip_sha256=h4.PINNED_ZIP_SHA256)
        report["python_helium_sha256"] = save_npz_new(ev/"python_h4_helium.npz", he_data)
        report["helium_parity"] = compare_helium(helium, native, c, ev/"libh4_original_source.so", budget)
        initial = h4.source_native_derivative_seeds(helium)
        for av, bv in zip(initial.ravel(), native["memories"][-1].ravel()):
            checked_integrated_rhs_ratio(float(av), float(bv), 2.e-10, -1, "initial_memory")
        report["initial_predictor"] = {"status": "PASS", "rows": ["He", "H"], "columns": ["prev2", "prev"],
                                       "input_global_indices": [c.izH0-2, c.izH0-1], "values": initial.tolist()}
        if steps:
            rates = OriginalHyRecPrimitiveRateTable.from_archive(ZIP)
            table = _canonical_twophoton_table(rates.archive_path)
            source = h4.make_hmla_source(c, rates)
            oracle = FullSourceCOracle(ev/"libh4_original_source.so", src, c)
            start = time.monotonic(); cpu = budget.cpu()
            result = h4.integrate_full_start(helium, c, source, accepted_steps=steps,
                                              common_input_oracle=oracle, check_budget=budget.check)
            report["python_full_runtime"] = {"wall_s": time.monotonic()-start, "cpu_s": budget.cpu()-cpu}
            data = {name: getattr(result, name) for name in result.__dataclass_fields__}
            data.update(source_zip_sha256=h4.PINNED_ZIP_SHA256, schema=h4.HISTORY_SCHEMA,
                        rei_activation=False, checkpoint_resampled=False,
                        predictor_input_global_indices=np.array([int(result.iz[-1])-2, int(result.iz[-1])-1]))
            report["python_full_sha256"] = save_npz_new(ev/"python_h4_full_start.npz", data)
            report["integrated_parity"] = compare_full(result, native, c, table)
            report["common_input_parity"] = {"status": "PASS", **oracle.metrics}
            report["full_evaluations"] = result.full_evaluations
            report["accepted_end_global_index"] = int(result.iz[-1])
            report["final_predictor"] = result.final_predictor.tolist()
            report["photon_prefix"] = {"committed_columns": steps, "virtual_per_column": 311,
                                       "average_per_column": 311, "lyman_per_column": 3,
                                       "ownership": "columns 0..steps-1 from accepted input states; trial outputs discarded"}
        budget.check()
        report["status"] = "PASS_SAME_H_START" if steps else "PASS_SAME_H_HELIUM"
    except Exception as exc:
        report["status"] = "FAIL"
        report["first_failure"] = {"type": type(exc).__name__, "message": str(exc)}
        with (ev/"failure.txt").open("x") as handle:
            handle.write(traceback.format_exc())
    finally:
        signal.alarm(0)
        after = {name: sha(ROOT/name) for name in DEPENDENCIES}
        report["input_mutation_check"] = {"status": "PASS" if after == before and sha(ZIP) == initial_zip else "FAIL",
                                           "dependency_sha256_after": after, "zip_sha256_after": sha(ZIP)}
        if source_manifest is not None:
            actual = {name: sha(ev/"source_extract"/name) for name in source_manifest["modified_member_sha256"]}
            report["temporary_source_after_run_matches_manifest"] = actual == source_manifest["modified_member_sha256"]
        if (report["input_mutation_check"]["status"] != "PASS"
                or report.get("temporary_source_after_run_matches_manifest") is False):
            report["status"] = "FAIL"
            if report["first_failure"] is None:
                report["first_failure"] = {"type": "InputMutation", "message": "producer/source changed during execution"}
        report["artifacts"] = {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)}
                               for p in ev.iterdir() if p.is_file() and p.name != "verification.json"}
        # Includes final input, extracted source, and artifact readback. An
        # earlier numerical PASS cannot override exhausted total resources.
        report["resources"] = {"wall_s": time.monotonic()-budget.started,
                               "cpu_s_including_children": budget.cpu()-budget.initial_cpu,
                               "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                               "children_peak_rss_bytes": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,
                               "measurement_scope": "through required input/source/artifact hashes; before final receipt serialization"}
        try:
            budget.check(total=True)
        except TimeoutError as exc:
            report["status"] = "FAIL_RESOURCE_LIMIT"
            report["resource_failure"] = {"type": type(exc).__name__, "message": str(exc)}
            if report["first_failure"] is None:
                report["first_failure"] = report["resource_failure"]
        json_new(ev/"verification.json", report)
        print(json.dumps({"status": report["status"], "evidence_dir": str(ev),
                          "first_failure": report["first_failure"], "resources": report["resources"]}, indent=2))
    return 0 if report["status"].startswith("PASS_SAME_H_") else 2


if __name__ == "__main__":
    raise SystemExit(main())

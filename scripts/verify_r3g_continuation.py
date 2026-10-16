#!/usr/bin/env python3
"""Verify the bounded R3G-U3 continuation against unmodified HyRec 2012 C.

This runner is intentionally opt-in because it performs the new science
integration. It consumes the exact independently reviewed U2 producer,
receipt, and accepted checkpoint; no C history is used as Python input.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
import traceback
import zipfile
from pathlib import Path

os.environ.update({"OMP_NUM_THREADS":"1", "OPENBLAS_NUM_THREADS":"1",
                   "MKL_NUM_THREADS":"1", "NUMEXPR_NUM_THREADS":"1"})

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from full_bianchi_hyrec.trajectory.primordial_2012_continuation import (  # noqa:E402
    MAX_EXTRA_ACCEPTED, REVIEWED_U2_CHECKPOINT_SHA256,
    REVIEWED_U2_PRODUCER_SHA256, REVIEWED_U2_RECEIPT_SHA256,
    U2_ACCEPTED_STEPS, ContinuationCheckpoint, continue_full_hhe, load_reviewed_u2_checkpoint,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import (  # noqa:E402
    HyRec2012Cosmology,
)
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import (  # noqa:E402
    make_hmla_source,
)
from full_bianchi_hyrec.trajectory.primitive_rates import (  # noqa:E402
    OriginalHyRecPrimitiveRateTable,
)

PINNED_ZIP_SHA = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
PINNED_SOURCE = {
    "history.c":"8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976",
    "helium.c":"1db7a9845e1f5a3052153bf94c1b98bf908cf16715641cbd14c810e5df6a5ece",
    "hydrogen.c":"421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b",
    "hyrec_params.h":"cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2",
}
BASE_REPOSITORY_REVISION = "140f0e67e2a880fc6d40d298e3bfff0de229f7df"
PINNED_ZH0 = 1702.072263548342
NVIRT = 311
U3_TRACKED_FILES = (
    "src/full_bianchi_hyrec/trajectory/primordial_2012_continuation.py",
    "scripts/c_harness/original_hyrec_continuation_harness.c",
    "scripts/verify_r3g_continuation.py",
    "tests/trajectory/test_primordial_2012_continuation.py",
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_u2_verifier():
    path = ROOT / "scripts/verify_r3g_full_start.py"
    spec = importlib.util.spec_from_file_location("r3g_full_start_verifier", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def safe_source(source_dir: Path | None, evidence: Path) -> Path:
    archive = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
    if sha(archive) != PINNED_ZIP_SHA:
        raise RuntimeError("ORIGINAL_SOURCE_ZIP_SHA_MISMATCH")
    if source_dir is not None:
        src = source_dir.resolve()
    else:
        target = evidence / "source_extract"
        target.mkdir(exist_ok=False)
        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():
                member = Path(info.filename)
                if member.is_absolute() or ".." in member.parts:
                    raise RuntimeError(f"UNSAFE_SOURCE_MEMBER:{info.filename}")
            zf.extractall(target)
        src = target / "HyRec"
    if not src.is_dir():
        raise RuntimeError("ORIGINAL_SOURCE_DIR_MISSING")
    # Compare the complete relevant HyRec tree (including rate tables and all
    # headers), not just a small source-file subset.
    with zipfile.ZipFile(archive) as zf:
        expected = {}
        for info in zf.infolist():
            path = Path(info.filename)
            if path.is_absolute() or ".." in path.parts:
                raise RuntimeError(f"UNSAFE_SOURCE_MEMBER:{info.filename}")
            if not info.is_dir() and path.parts[0] == "HyRec":
                expected[str(Path(*path.parts[1:]))] = hashlib.sha256(zf.read(info)).hexdigest()
    actual = {}
    for path in src.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"SOURCE_CAPSULE_SYMLINK_FORBIDDEN:{path}")
        if path.is_file():
            actual[path.relative_to(src).as_posix()] = sha(path)
    if actual != expected:
        absent = sorted(set(expected)-set(actual))
        extra = sorted(set(actual)-set(expected))
        changed = sorted(k for k in set(expected)&set(actual) if expected[k] != actual[k])
        raise RuntimeError(f"ORIGINAL_SOURCE_COMPLETE_TREE_MISMATCH:missing={absent}:extra={extra}:changed={changed}")
    got = {name: actual.get(name) for name in PINNED_SOURCE}
    if got != PINNED_SOURCE:
        raise RuntimeError(f"ORIGINAL_SOURCE_MEMBER_SHA_MISMATCH:{got!r}")
    return src


def zip_member_hashes() -> dict[str, str]:
    archive = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
    if sha(archive) != PINNED_ZIP_SHA:
        raise RuntimeError("ORIGINAL_SOURCE_ZIP_SHA_MISMATCH")
    result = {}
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            member = Path(info.filename)
            if member.is_absolute() or ".." in member.parts:
                raise RuntimeError(f"UNSAFE_SOURCE_MEMBER:{info.filename}")
            if not info.is_dir():
                result[info.filename] = hashlib.sha256(zf.read(info)).hexdigest()
    return result


def validate_execution_manifest(path: Path) -> dict:
    """Require controller-frozen revision/capsule identity for any run."""
    record = json.loads(Path(path).read_text())
    if record.get("controller_verified") is not True:
        raise RuntimeError("CONTROLLER_EXECUTION_MANIFEST_NOT_VERIFIED")
    if record.get("base_revision") != BASE_REPOSITORY_REVISION:
        raise RuntimeError("EXECUTION_MANIFEST_BASE_REVISION_MISMATCH")
    execution = record.get("execution_revision", "")
    capsule = record.get("capsule_manifest_sha256", "")
    if not re.fullmatch(r"[0-9a-f]{40,64}", execution) or execution == BASE_REPOSITORY_REVISION:
        raise RuntimeError("EXECUTION_MANIFEST_REVISION_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", capsule):
        raise RuntimeError("EXECUTION_MANIFEST_CAPSULE_SHA_INVALID")
    if record.get("source_zip_sha256") != PINNED_ZIP_SHA:
        raise RuntimeError("EXECUTION_MANIFEST_SOURCE_ZIP_MISMATCH")
    expected = {relative: sha(ROOT / relative) for relative in U3_TRACKED_FILES}
    if record.get("u3_files_sha256") != expected:
        raise RuntimeError("EXECUTION_MANIFEST_U3_FILE_HASH_MISMATCH")
    return {**record, "manifest_sha256":sha(Path(path))}


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (540, 540))


def run_capture(cmd, cwd, stdout, stderr, timeout, env):
    started = time.monotonic()
    with Path(stdout).open("xb") as out, Path(stderr).open("xb") as err:
        proc = subprocess.run(cmd, cwd=cwd, stdout=out, stderr=err, timeout=timeout,
                              env=env, preexec_fn=child_limits, check=False)
    return {"command":cmd, "returncode":proc.returncode,
            "wall_s":time.monotonic()-started,
            "stdout_sha256":sha(stdout), "stderr_sha256":sha(stderr)}


def parse_native(path: Path):
    node = None; meta = None; steps = {}; virtual = {}; average = {}; lines = {}; end = None
    with path.open() as stream:
        for line_no, line in enumerate(stream, 1):
            f = line.rstrip("\n").split(",")
            if f[0] == "META":
                if meta is not None or len(f) != 4:
                    raise RuntimeError(f"C_META_RECORD_MALFORMED:{line_no}")
                meta = {"izH0":int(f[1]),"nzrt":int(f[2]),"zH0":float(f[3])}
            elif f[0] == "NODE":
                if node is not None or len(f) != 9:
                    raise RuntimeError(f"C_NODE_RECORD_MALFORMED:{line_no}")
                node = {"iz":int(f[1]),"z":float(f[2]),"xH1s":float(f[3]),
                        "xHII":float(f[4]),"xHeII":float(f[5]),"xe":float(f[6]),
                        "Tm_K":float(f[7]),"post_saha":bool(int(f[8]))}
            elif f[0] == "STEP":
                if len(f) != 17:
                    raise RuntimeError(f"C_STEP_RECORD_MALFORMED:{line_no}")
                j = int(f[1])
                if j in steps:
                    raise RuntimeError(f"C_DUPLICATE_STEP:{j}")
                steps[j] = {"j":j,"iz":int(f[2]),"z":float(f[3]),
                    "xH1s":float(f[4]),"xHII":float(f[5]),"xHeII":float(f[6]),
                    "xe":float(f[7]),"Tm_K":float(f[8]),
                    "hydrogen_rhs":float(f[9]),"helium_rhs":float(f[10]),
                    "post_saha":bool(int(f[11])),"event_before":int(f[12]),
                    "helium_cutoff_crossed":bool(int(f[13])),
                    "hydrogen_post_saha_off_crossed":bool(int(f[14])),
                    "source_branch_input_h_only":bool(int(f[15])),
                    "source_branch_output_h_only":bool(int(f[16]))}
            elif f[0] in {"V", "A", "L"}:
                if len(f) != 4:
                    raise RuntimeError(f"C_SPECTRUM_RECORD_MALFORMED:{line_no}")
                j, b, val = int(f[1]), int(f[2]), float(f[3])
                target = {"V":virtual,"A":average,"L":lines}[f[0]]
                if b in target.get(j, {}):
                    raise RuntimeError(f"C_DUPLICATE_SPECTRUM_BIN:{f[0]}:{j}:{b}")
                if not math.isfinite(val):
                    raise RuntimeError(f"C_NONFINITE_SPECTRUM:{f[0]}:{j}:{b}")
                target.setdefault(j, {})[b] = val
            elif f[0] == "END":
                if end is not None:
                    raise RuntimeError("C_DUPLICATE_END_RECORD")
                end = f[1:]
            else:
                raise RuntimeError(f"C_UNKNOWN_RECORD:{line_no}:{f[0]}")
    if node is None or meta is None or end is None:
        raise RuntimeError("C_ORACLE_MISSING_META_NODE_OR_END")
    if (not math.isfinite(meta["zH0"]) or
            not math.isclose(meta["zH0"], PINNED_ZH0, rel_tol=0.0, abs_tol=1.e-12)):
        raise RuntimeError("C_ZH0_MISMATCH")
    if meta["izH0"] != 18223 or meta["nzrt"] <= 0:
        raise RuntimeError("C_META_INDEX_OR_END_INVALID")
    if not all(math.isfinite(float(v)) for v in node.values()
               if isinstance(v, (float, int))):
        raise RuntimeError("C_NODE_NONFINITE_OR_MISSING")
    if any(not all(math.isfinite(float(v)) for v in row.values()
                   if isinstance(v, (float, int))) for row in steps.values()):
        raise RuntimeError("C_STEP_NONFINITE")
    validate_end_fields(end, len(steps))
    if sorted(steps) != list(range(8, 8 + len(steps))):
        raise RuntimeError("C_STEP_INDEX_SEQUENCE_INVALID")
    if any(steps[j]["iz"] != node["iz"] + (j - 7) for j in steps):
        raise RuntimeError("C_STEP_SOURCE_GRID_INVALID")
    for j in steps:
        for label, series, n in (("V",virtual,NVIRT),("A",average,NVIRT),("L",lines,3)):
            if set(series.get(j, {})) != set(range(n)):
                raise RuntimeError(f"C_INCOMPLETE_SPECTRUM:{label}:{j}")
    return meta, node, steps, virtual, average, lines, end


def validate_end_fields(end: list[str], accepted_steps: int) -> dict[str, int | str]:
    statuses = {"EVENT_TWO_STEPS_COMPLETE", "BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED",
                "HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY",
                "HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY",
                "HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE"}
    if len(end) != 5 or end[0] not in statuses:
        raise ValueError("C_END_GRAMMAR_INVALID")
    first_flags, cumulative_flags, after, total = map(int, end[1:])
    if (first_flags not in (0, 1, 2, 3) or cumulative_flags not in (0, 1, 2, 3)
            or first_flags & ~cumulative_flags or not 0 <= after <= 2):
        raise ValueError("C_END_EVENT_FIELDS_INVALID")
    if total != accepted_steps + U2_ACCEPTED_STEPS:
        raise ValueError("C_END_ACCEPTED_COUNT_MISMATCH")
    if end[0] == "EVENT_TWO_STEPS_COMPLETE" and (first_flags == 0 or after != 2):
        raise ValueError("C_END_FALSE_EVENT_SUCCESS")
    if end[0] == "BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED" and (first_flags != 0 or after != 0):
        raise ValueError("C_END_FALSE_NO_EVENT_STATUS")
    return {"status":end[0], "first_event_flags":first_flags,
            "cumulative_crossing_flags":cumulative_flags,
            "branch_steps_after_event":after, "total_accepted_columns":total}


def compare_source_branch(py_input: bool, py_output: bool, c_input: bool,
                          c_output: bool, row: int) -> None:
    if bool(py_input) != bool(c_input):
        raise ArithmeticError(f"SOURCE_INPUT_BRANCH_PARITY row={row}")
    if bool(py_output) != bool(c_output):
        raise ArithmeticError(f"SOURCE_OUTPUT_BRANCH_PARITY row={row}")


def compare_state(py, c, row: int):
    limits = {"xH1s":5.e-9,"xHII":5.e-9,"xe":5.e-9,"xHeII":5.e-10,"Tm_K":5.e-10}
    maxima = {}
    for key, limit in limits.items():
        floor = 1.e-8 if key in ("xH1s", "xHII", "xe") else 1.0
        diff = abs(float(py[key])-float(c[key]))/max(abs(float(c[key])), floor)
        maxima[key] = diff
        if diff > limit:
            raise ArithmeticError(f"INTEGRATED_STATE_PARITY row={row} field={key} scaled={diff:.17g} limit={limit:.17g}")
    if int(py["iz"]) != int(c["iz"]):
        raise ArithmeticError(f"INTEGRATED_INDEX_PARITY row={row}")
    if not math.isclose(float(py["z"]), float(c["z"]), rel_tol=0.0, abs_tol=2.e-12):
        raise ArithmeticError(f"INTEGRATED_REDSHIFT_PARITY row={row}")
    if bool(py["post_saha"]) != bool(c["post_saha"]):
        raise ArithmeticError(f"INTEGRATED_POST_SAHA_PARITY row={row}")
    return maxima


def compare_spectra(p, c, fbb, step, name):
    p = np.asarray(p, dtype=float); c = np.asarray(c, dtype=float); fbb = np.asarray(fbb, dtype=float)
    tol = 1.e-7*np.maximum(np.abs(p), np.abs(c)) + 1.e-10*fbb
    ratio = np.abs(p-c)/tol
    if p.shape != c.shape or not np.all(np.isfinite(ratio)) or np.any(ratio > 1.):
        bad = int(np.flatnonzero((~np.isfinite(ratio)) | (ratio > 1.))[0])
        raise ArithmeticError(f"INTEGRATED_PHOTON_PARITY row={step} channel={name} bin={bad}")
    return float(np.max(ratio))


def save_checkpoint(evidence: Path, payload: dict):
    phase = str(payload["phase"])
    count = int(payload["accepted_extra"])
    tag = f"checkpoint_{count:04d}_{phase.lower()}"
    npz = evidence / f"{tag}.npz"
    meta = evidence / f"{tag}.json"
    with npz.open("xb") as out:
        np.savez_compressed(out, **{k:v for k,v in payload.items()
                                  if isinstance(v, np.ndarray)})
    record = {k:v for k,v in payload.items() if not isinstance(v, np.ndarray)}
    record["npz_sha256"] = sha(npz)
    with meta.open("x") as out:
        json.dump(record, out, sort_keys=True, indent=2); out.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="run the bounded U3 integration")
    ap.add_argument("--evidence-dir", type=Path, required=True)
    ap.add_argument("--source-dir", type=Path)
    ap.add_argument("--execution-manifest", type=Path,
                    help="controller-generated verified revision and capsule manifest")
    ap.add_argument("--checkpoint-npz", type=Path, default=ROOT/"research/rec_r3g_primordial_20261016/full_start_011/python_accepted_history.npz")
    ap.add_argument("--u2-receipt", type=Path, default=ROOT/"research/rec_r3g_primordial_20261016/full_start_011/verification.json")
    ap.add_argument("--u2-producer", type=Path, default=ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_full_start.py")
    ap.add_argument("--max-extra-accepted", type=int, default=MAX_EXTRA_ACCEPTED)
    args = ap.parse_args()
    if not args.execute:
        raise SystemExit("SCIENCE_RUN_NOT_STARTED: pass --execute only after U3 review and frozen manifest")
    if args.execution_manifest is None:
        raise SystemExit("SCIENCE_RUN_NOT_STARTED: --execution-manifest is required")
    execution_manifest = validate_execution_manifest(args.execution_manifest)
    ev = args.evidence_dir.resolve()
    ev.mkdir(parents=True, exist_ok=False)
    with (ev/"controller_execution_manifest.json").open("xb") as out:
        out.write(args.execution_manifest.read_bytes())
    usage0 = resource.getrusage(resource.RUSAGE_SELF)
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else []
    if affinity:
        os.sched_setaffinity(0, {affinity[0]})
    report = {"status":"FAIL", "scope":"source-native bounded U3 continuation only",
              "u2_producer_sha256_expected":REVIEWED_U2_PRODUCER_SHA256,
              "u2_receipt_sha256_expected":REVIEWED_U2_RECEIPT_SHA256,
              "u2_checkpoint_sha256_expected":REVIEWED_U2_CHECKPOINT_SHA256,
              "source_zip_sha256_expected":PINNED_ZIP_SHA,
              "limits":{"extra_accepted_max":args.max_extra_accepted,
                  "python_full_evaluations_max":8192,"address_space_bytes":2*1024**3,
                  "cpu_s":540,"wall_s":600,"cpu_affinity":affinity[:1],
                  "OMP_NUM_THREADS":1,"OPENBLAS_NUM_THREADS":1},
              "first_failure":None}
    report["execution_manifest_sha256"] = execution_manifest["manifest_sha256"]
    started = time.monotonic()
    try:
        checkpoint = load_reviewed_u2_checkpoint(args.checkpoint_npz,args.u2_receipt,args.u2_producer)
        report["u2_endpoint"] = checkpoint.endpoint
        src = safe_source(args.source_dir, ev)
        report["original_source_sha256"] = {k:sha(src/k) for k in PINNED_SOURCE}
        manifest = {
            "base_repository_revision":BASE_REPOSITORY_REVISION,
            "execution_revision":execution_manifest["execution_revision"],
            "controller_execution_manifest_sha256":execution_manifest["manifest_sha256"],
            "source_capsule_manifest_sha256":execution_manifest["capsule_manifest_sha256"],
            "original_zip_sha256":PINNED_ZIP_SHA,
            "original_source_member_sha256":report["original_source_sha256"],
            "original_zip_member_sha256":zip_member_hashes(),
            "u2_producer_sha256":sha(args.u2_producer),
            "u2_review_receipt_sha256":sha(args.u2_receipt),
            "u2_checkpoint_npz_sha256":sha(args.checkpoint_npz),
            "u3_python_source_sha256":sha(ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_continuation.py"),
            "u3_native_harness_sha256":sha(ROOT/"scripts/c_harness/original_hyrec_continuation_harness.c"),
            "u3_verifier_sha256":sha(Path(__file__).resolve()),
            "claim_ceiling":"q=0 original HyRec H+He bounded continuation; no self-consistent Bianchi or CMB prediction",
        }
        with (ev/"source_manifest.json").open("x") as out:
            json.dump(manifest,out,sort_keys=True,indent=2); out.write("\n")
        report["manifest_sha256"] = sha(ev/"source_manifest.json")
        os.chdir(src)
        # Enforce runtime caps only after Python/NumPy imports are complete.
        resource.setrlimit(resource.RLIMIT_AS, (2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU, (540,540))
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("U3_WALL_LIMIT_600S")))
        signal.alarm(600)
        u2v = load_u2_verifier()
        c = HyRec2012Cosmology()
        rate_table = OriginalHyRecPrimitiveRateTable.from_archive(
            ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        source = make_hmla_source(c, rate_table)
        cc = ["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-I",str(src),
              str(ROOT/"scripts/c_harness/original_hyrec_full_source_harness.c"),
              str(src/"hydrogen.c"),str(src/"hyrectools.c"),"-lm","-o",str(ev/"liboriginal_full_source.so")]
        report["common_input_build"] = run_capture(cc,src,ev/"common_build_stdout.txt",
            ev/"common_build_stderr.txt",30,os.environ.copy())
        if report["common_input_build"]["returncode"]:
            raise RuntimeError("COMMON_INPUT_C_BUILD_FAILED")
        report["common_input_binary_sha256"] = sha(ev/"liboriginal_full_source.so")
        native_cc = ["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(src),
            str(ROOT/"scripts/c_harness/original_hyrec_continuation_harness.c"),
            str(src/"history.c"),str(src/"hydrogen.c"),str(src/"helium.c"),
            str(src/"hyrectools.c"),"-lm","-o",str(ev/"native_continuation_oracle")]
        report["native_build"] = run_capture(native_cc,src,ev/"native_build_stdout.txt",
            ev/"native_build_stderr.txt",30,os.environ.copy())
        if report["native_build"]["returncode"]:
            raise RuntimeError("NATIVE_C_BUILD_FAILED")
        report["native_binary_sha256"] = sha(ev/"native_continuation_oracle")
        report["native_run"] = run_capture([str(ev/"native_continuation_oracle"),str(args.max_extra_accepted)],
            src,ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",60,os.environ.copy())
        if report["native_run"]["returncode"]:
            raise RuntimeError("NATIVE_C_CONTINUATION_FAILED")
        cmeta,node_c,csteps,cv,ca,cl,cend = parse_native(ev/"native_oracle_stdout.csv")
        if cmeta["izH0"] != 18223 or cmeta["nzrt"] <= 0:
            raise RuntimeError(f"SOURCE_STAGE_INDEX_MISMATCH:{cmeta!r}")
        report["original_c_stage_metadata"] = cmeta
        endpoint = checkpoint.endpoint
        compare_state(endpoint,node_c,0)
        report["native_c_step_rows"] = len(csteps)
        report["native_c_end"] = cend
        report["native_c_stdout_sha256"] = sha(ev/"native_oracle_stdout.csv")
        oracle = u2v.FullSourceCOracle(ev/"liboriginal_full_source.so",src,c)
        result = continue_full_hhe(
            checkpoint,c,source,common_input_oracle=oracle,
            max_extra_accepted=args.max_extra_accepted,
            rt_limit_relative_index=cmeta["nzrt"],
            checkpoint_callback=lambda payload: save_checkpoint(ev,payload))
        row_records=[]; state_max={k:0. for k in ("xH1s","xHII","xe","xHeII","Tm_K")}
        rhs_max={"hydrogen_scaled":0.,"helium_scaled":0.}
        spectrum_max={k:0. for k in ("virtual","average","lyman")}
        event_mask_before = 0
        first_event_mask = 0
        for i in range(1,result.accepted_extra+1):
            pyrow={"iz":int(result.iz[8+i]),"z":float(result.z[8+i]),
                "xH1s":float(result.xH1s[8+i]),"xHII":float(result.xHII[8+i]),
                "xHeII":float(result.xHeII[8+i]),"xe":float(result.xe[8+i]),
                "Tm_K":float(result.Tm_K[8+i]),"post_saha":bool(result.post_saha[8+i])}
            crow=csteps.get(7+i)
            if crow is None:
                raise ArithmeticError(f"C_MISSING_ACCEPTED_ROW:{7+i}")
            errors=compare_state(pyrow,crow,i)
            compare_source_branch(result.source_branch_h_only[7+i],
                result.source_branch_h_only[8+i],
                crow["source_branch_input_h_only"],
                crow["source_branch_output_h_only"],i)
            if bool(result.helium_cutoff_crossed[8+i]) != crow["helium_cutoff_crossed"]:
                raise ArithmeticError(f"HELIUM_CROSSING_FLAG_PARITY row={i}")
            if bool(result.hydrogen_post_saha_off_crossed[8+i]) != crow["hydrogen_post_saha_off_crossed"]:
                raise ArithmeticError(f"HYDROGEN_CROSSING_FLAG_PARITY row={i}")
            if int(crow["event_before"]) != event_mask_before:
                raise ArithmeticError(f"EVENT_BEFORE_PARITY row={i}")
            row_crossing_mask = ((1 if result.helium_cutoff_crossed[8+i] else 0) |
                                 (2 if result.hydrogen_post_saha_off_crossed[8+i] else 0))
            if first_event_mask == 0 and row_crossing_mask:
                first_event_mask = row_crossing_mask
            event_mask_before |= row_crossing_mask
            for k,v in errors.items(): state_max[k]=max(state_max[k],v)
            col=7+i
            for label, py_rhs, c_rhs in (
                ("hydrogen_scaled",float(result.hydrogen_rhs_dln_a[col]),float(crow["hydrogen_rhs"])),
                ("helium_scaled",float(result.helium_rhs_dln_a[col]),float(crow["helium_rhs"]))):
                scaled=abs(py_rhs-c_rhs)/max(1.,abs(c_rhs))
                rhs_max[label]=max(rhs_max[label],scaled)
                if scaled>2.e-7:
                    raise ArithmeticError(f"INTEGRATED_TRAJECTORY_RHS_PARITY row={i} field={label} scaled={scaled:.17g}")
            zface=float(result.z[8+i-1])
            tr_ev=8.617343e-5*c.T0_K*(1.+zface)
            table=u2v._canonical_twophoton_table(rate_table.archive_path)
            fbbv=1./np.expm1(table.energy_eV/tr_ev)
            line_e=np.array((10.198714553953742,12.087365397278509,12.748393192442178))
            fbbl=1./np.expm1(line_e/tr_ev)
            for key, arr, map0, fb, bins in (
                ("virtual",result.virtual_out[:,col],cv,fbbv,NVIRT),
                ("average",result.average_virtual[:,col],ca,fbbv,NVIRT),
                ("lyman",result.lyman_out[:,col],cl,fbbl,3)):
                cs=np.array([map0[col][b] for b in range(bins)])
                ratio=compare_spectra(arr,cs,fb,col,key)
                spectrum_max[key]=max(spectrum_max[key],ratio)
            row_records.append(pyrow)
        with (ev/"python_accepted_rows.jsonl").open("x") as out:
            for row in row_records:
                out.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n")
        end_fields = validate_end_fields(cend,len(csteps))
        expected_event = str(cend[0])
        expected_flags = int(end_fields["first_event_flags"])
        expected_cumulative = int(end_fields["cumulative_crossing_flags"])
        expected_py = ({0:"NONE",1:"HELIUM_CUTOFF",2:"HYDROGEN_POST_SAHA_OFF",
                        3:"HELIUM_CUTOFF+HYDROGEN_POST_SAHA_OFF"}.get(expected_flags))
        if expected_py is None:
            raise RuntimeError("C_END_EVENT_FLAGS_INVALID")
        if result.event != expected_py:
            raise ArithmeticError(f"EVENT_PARITY:C={expected_event}:Python={result.event}")
        if (result.status != expected_event and not
                (result.status.startswith("HOLD_NEXT_STAGE_REQUIRED") and
                 expected_event == "EVENT_TWO_STEPS_COMPLETE" and
                 result.branch_steps_after_event == 2)):
            raise ArithmeticError(f"END_STATUS_PARITY:C={expected_event}:Python={result.status}")
        if first_event_mask != expected_flags:
            raise ArithmeticError("END_FIRST_EVENT_FLAGS_PARITY")
        if event_mask_before != expected_cumulative:
            raise ArithmeticError("END_CUMULATIVE_CROSSING_FLAGS_PARITY")
        if result.branch_steps_after_event != int(end_fields["branch_steps_after_event"]):
            raise ArithmeticError("END_BRANCH_STEP_COUNT_PARITY")
        if int(end_fields["total_accepted_columns"]) != result.accepted_extra + 8:
            raise ArithmeticError("END_ACCEPTED_TOTAL_PARITY")
        if len(csteps) != result.accepted_extra:
            raise ArithmeticError("ACCEPTED_STEP_COUNT_MISMATCH")
        report.update({"status":result.status,"scope":"independent Python continuation from reviewed U2 j=8; source-native q=0 interval",
            "python_accepted_extra":result.accepted_extra,"python_full_evaluations":result.full_evaluations,
            "event":result.event,"branch_steps_after_event":result.branch_steps_after_event,
            "integrated_state_parity":{"max_scaled_or_absolute":state_max,
                "limits":{"xH1s_xHII_xe_scaled":5e-9,"xHeII_abs":5e-10,"Tm_relative":5e-10}},
            "integrated_trajectory_rhs_parity":{"max_scaled":rhs_max,"limit":2e-7},
            "integrated_photon_parity":{"max_tolerance_ratio":spectrum_max,
                "limit":"abs(C-P)<=1e-7*max(abs(C),abs(P))+1e-10*fBB"},
            "common_input_sample_ledger":{"count":result.common_input_evaluations,
                "columns":list(result.common_input_sample_columns),"max_rhs_scaled":result.common_input_max_rhs_scaled,
                "max_virtual_tolerance_ratio":result.common_input_max_virtual_ratio,
                "max_average_tolerance_ratio":result.common_input_max_average_ratio,
                "max_lyman_tolerance_ratio":result.common_input_max_lyman_ratio,
                "limit":64},
            "endpoint_diagnostic":{"column":result.endpoint_diagnostic_column,
                "hydrogen_rhs_dln_a":result.endpoint_diagnostic_rhs,
                "matrix_residual":result.endpoint_diagnostic_matrix_residual,
                "committed_as_trajectory_column":False},
            "python_rows_sha256":sha(ev/"python_accepted_rows.jsonl"),
            "checkpoint_count":len(list(ev.glob("checkpoint_*.npz"))),
            "independence_limit":"This is a bounded q=0 original HyRec H+He input-history continuation; it does not establish a self-consistent Bianchi recombination or CMB prediction."})
        report["first_failure"] = None
    except BaseException as exc:
        typed = str(exc)
        report["status"] = (typed if typed.startswith(("BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED",
                          "HOLD_NEXT_STAGE_REQUIRED")) else "FAIL")
        report["first_failure"] = {"type":type(exc).__name__,"message":str(exc),
                                    "traceback":traceback.format_exc()}
        with (ev/"first_failure.json").open("x") as out:
            json.dump(report["first_failure"],out,sort_keys=True,indent=2); out.write("\n")
    finally:
        signal.alarm(0)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        report["resources"] = {"wall_s":time.monotonic()-started,
            "parent_cpu_s":(usage.ru_utime+usage.ru_stime)-(usage0.ru_utime+usage0.ru_stime),
            "parent_peak_rss_bytes":usage.ru_maxrss*1024,
            "allowed_affinity":affinity[:1],"OMP_NUM_THREADS":1,"OPENBLAS_NUM_THREADS":1,
            "address_space_limit_bytes":2*1024**3,"cpu_limit_s":540,"wall_limit_s":600}
        report["artifact_sha256"] = {p.name:sha(p) for p in ev.iterdir() if p.is_file()}
        with (ev/"verification.json").open("x") as out:
            json.dump(report,out,sort_keys=True,indent=2); out.write("\n")
    print(json.dumps(report,sort_keys=True,indent=2))
    return 0 if report["status"] == "EVENT_TWO_STEPS_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())

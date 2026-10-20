#!/usr/bin/env python3
"""Source-bound, opt-in U6 smoke/pilot with cached or prebuilt Rust auditing.

Default: 16 original-h2 steps from the frozen original U5 checkpoint. Both
accepted steps and source evaluations are bounded by 128; there is no full
mode, allocation creation, checkpoint conversion, grid option, or Rust build.
The public CLI delegates to run_r3p_u6_supervised.py before numerical imports.
Its unchanged R3O Budget encloses this complete worker, including source/input
binding and closeout, within 60 CPU / 180 wall seconds / 2 GiB with a receipt
reserve. R3L supplies owned integration, original same-h C, durable partial
evidence and phase accounting. Programmatic main/execute remain worker APIs;
their inner limits alone do not establish a whole-launch budget.

New sources must be committed at --expected-commit. Frozen V6 dependencies,
including separately restored data files, are authenticated by their original
hashes, not by whether git tracks them. --source-zip changes only the location
of the identical pinned ZIP, including its V6 closure entry. The original
verifier/manifest and all imported bindings are restored or left untouched.
"""
from __future__ import annotations

# Keep the public command supervised before importing NumPy or worker helpers.
# The supervisor imports this module by its canonical name to call main() in
# a child; no public CLI flag or inherited environment marker disables it.
if __name__ == "__main__":
    from run_r3p_u6_supervised import main as supervised_main
    raise SystemExit(supervised_main())

import argparse
from contextlib import contextmanager
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "RAYON_NUM_THREADS"):
    os.environ[_key] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

import run_r3l_u6_profiled as profiled
from r3l_u6_cost import file_sha256

FROZEN_MANIFEST = "research/rec_r3i_time_refinement_20261016/h2_u6_rt_boundary_001/SOURCE_MANIFEST_V6.json"
FROZEN_MANIFEST_SHA256 = "f02f4e0b39dfafbb7656704cee59b8d95c976e9b55e840141d333be15b452585"
FROZEN_CONTRACT = "research/rec_r3i_time_refinement_20261016/h2_u6_rt_boundary_001/CONTRACT.json"
CHECKPOINT_SHA256 = "7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b"
SOURCE_ZIP = "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SOURCE_ZIP_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
VENDOR_META = "rust/REC_STREAM_AUDIT_VENDOR.json"
VENDOR_ARCHIVE = "rust/vendor/rec-stream-audit-registry-20261020.tar.gz"
CRATE = "rust/rec-stream-audit"
EXTRA_FILES = (
    "scripts/run_r3p_u6_audited.py", "scripts/run_r3p_u6_supervised.py",
    "scripts/r3p_stream_audit.py",
    "scripts/r3p_rust_audit.py", "scripts/build_r3p_rust.py",
    "tests/trajectory/test_r3p_u6_audited.py",
    "tests/trajectory/test_r3p_stream_audit.py",
)
BUILD_FILES = (
    f"{CRATE}/Cargo.toml", f"{CRATE}/Cargo.lock",
    f"{CRATE}/include/rec_stream_audit.h", f"{CRATE}/tests/abi_smoke.c",
    "scripts/build_r3p_rust.py", "scripts/build_r3o_rust.py", VENDOR_META,
)


def _json_bytes(path):
    data = Path(path).read_bytes()

    def reject(token):
        raise ValueError(f"R3P_JSON_NONFINITE:{token}")

    return json.loads(data, parse_constant=reject), hashlib.sha256(data).hexdigest()


def frozen_manifest(root):
    manifest, digest = _json_bytes(Path(root) / FROZEN_MANIFEST)
    if (digest != FROZEN_MANIFEST_SHA256 or manifest.get("node") != "H2_U6_RT_BOUNDARY"
            or manifest.get("checkpoint_sha256") != CHECKPOINT_SHA256
            or len(manifest.get("files", {})) != 109
            or manifest["files"].get(SOURCE_ZIP) != SOURCE_ZIP_SHA256
            or FROZEN_CONTRACT not in manifest["files"]):
        raise ValueError("R3P_FROZEN_V6_MANIFEST_IDENTITY")
    return manifest


def rust_source_hashes(root):
    """The complete source set emitted by the separate R3P build command."""
    root = Path(root)
    sources = sorted((root / CRATE).rglob("*.rs"))
    if root / CRATE / "src/lib.rs" not in sources:
        raise ValueError("R3P_RUST_SOURCE_MISSING")
    paths = {str(p.relative_to(root)) for p in sources} | set(BUILD_FILES)
    return {name: file_sha256(root / name) for name in sorted(paths)}


def vendor_binding(root):
    root = Path(root)
    meta, _ = _json_bytes(root / VENDOR_META)
    archive = root / VENDOR_ARCHIVE
    digest = file_sha256(archive)
    if (meta.get("schema") != "rec.r3p.registry-vendor.v1"
            or meta.get("file") != VENDOR_ARCHIVE or meta.get("sha256") != digest
            or meta.get("bytes") != archive.stat().st_size
            or meta.get("cargo_lock_sha256") != file_sha256(root / CRATE / "Cargo.lock")):
        raise ValueError("R3P_VENDOR_OR_LOCK_IDENTITY")
    return {"path": VENDOR_ARCHIVE, "sha256": digest,
            "cargo_lock_sha256": meta["cargo_lock_sha256"]}


def bind_audited_source(root, expected_commit):
    root = Path(root).resolve()
    binding = profiled.bind_profile_source(root, expected_commit)
    manifest = frozen_manifest(root)
    rust_sources = rust_source_hashes(root)
    vendor = vendor_binding(root)
    names = sorted(set(binding["additional_source_sha256"]) | set(EXTRA_FILES)
                   | set(rust_sources) | {VENDOR_ARCHIVE, FROZEN_MANIFEST})
    # Frozen restored data remain manifest-bound; every executable adapter,
    # build source and vendor archive must itself belong to the exact commit.
    subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", "--", *names],
                   capture_output=True, text=True, check=True, timeout=10)
    binding["additional_source_sha256"] = {
        name: file_sha256(root / name) for name in names}
    binding["rust_build_source_sha256"] = rust_sources
    binding["vendor"] = vendor
    binding["frozen_v6"] = {
        "manifest": FROZEN_MANIFEST, "manifest_sha256": FROZEN_MANIFEST_SHA256,
        "contract": FROZEN_CONTRACT, "contract_sha256": manifest["files"][FROZEN_CONTRACT],
        "source_files": len(manifest["files"]), "checkpoint_sha256": CHECKPOINT_SHA256}
    return binding


def input_binding(checkpoint, source_zip):
    result = {name: {"path": str(Path(path).resolve()), "sha256": file_sha256(path)}
              for name, path in (("checkpoint", checkpoint), ("source_zip", source_zip))}
    if result["checkpoint"]["sha256"] != CHECKPOINT_SHA256:
        raise ValueError("U6_CHECKPOINT_SHA")
    if result["source_zip"]["sha256"] != SOURCE_ZIP_SHA256:
        raise RuntimeError("SOURCE_ZIP_SHA_MISMATCH")
    return result


def verify_frozen_closure(root, checkpoint, source_zip):
    """Same V6 checks and return fields, with only the ZIP location selectable."""
    root = Path(root)
    input_binding(checkpoint, source_zip)
    manifest = frozen_manifest(root)
    for relative, digest in manifest["files"].items():
        path = Path(source_zip) if relative == SOURCE_ZIP else root / relative
        if not path.is_file() or file_sha256(path) != digest:
            raise ValueError(f"U6_SOURCE_CLOSURE:{relative}")
    return {"manifest_sha256": FROZEN_MANIFEST_SHA256,
            "source_files": len(manifest["files"]), "checkpoint_sha256": CHECKPOINT_SHA256}


def verify_build_receipt(path, binding, root=ROOT):
    """Authenticate a complete successful receipt; never compile or load code."""
    path = Path(path).resolve()
    report, receipt_sha = _json_bytes(path)
    if (report.get("schema") != "rec.r3p.audit-build.v1" or report.get("status") != "BUILT"
            or report.get("exit_code") != 0 or report.get("new_physical_runs") != 0
            or report.get("first_failure") or report.get("resource_failure")):
        raise ValueError("R3P_BUILD_NOT_SUCCESSFUL")
    expected = binding["rust_build_source_sha256"]
    if (report.get("source_sha256") != expected or rust_source_hashes(root) != expected
            or report.get("vendor_sha256") != binding["vendor"]["sha256"]
            or vendor_binding(root) != binding["vendor"]):
        raise ValueError("R3P_BUILD_COMPLETE_SOURCE_BINDING")
    library = Path(report["library"]).resolve()
    if not library.is_file() or file_sha256(library) != report.get("library_sha256"):
        raise ValueError("R3P_BUILD_LIBRARY_CHANGED")
    return {"receipt": str(path), "receipt_sha256": receipt_sha,
            "library": str(library), "library_sha256": report["library_sha256"],
            "vendor_sha256": report["vendor_sha256"]}


def step_count(mode, pilot_steps=128):
    if mode not in ("smoke", "pilot"):
        raise ValueError("R3P_SMOKE_OR_PILOT_ONLY")
    if type(pilot_steps) is not int or not 1 <= pilot_steps <= 128:
        raise ValueError("BOUNDED_PILOT_STEPS_1_TO_128")
    return 16 if mode == "smoke" else pilot_steps


def validate_options(*, steps, backend, build, block_columns, allocation_id, container):
    if type(steps) is not int or not 1 <= steps <= 128:
        raise ValueError("R3P_STEPS_1_TO_128")
    if backend not in ("cached", "rust"):
        raise ValueError("R3P_AUDIT_BACKEND")
    if (backend == "rust") != (build is not None):
        raise ValueError("R3P_BUILD_REQUIRED_ONLY_FOR_RUST")
    if type(block_columns) is not int or not 1 <= block_columns <= 64:
        raise ValueError("R3P_BLOCK_COLUMNS_1_TO_64")
    if container not in ("stored", "compressed"):
        raise ValueError("HISTORY_CONTAINER")
    if not isinstance(allocation_id, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", allocation_id) is None:
        raise ValueError("R3P_EXISTING_BOUNDED_ALLOCATION_ID_REQUIRED")


def validate_verifier(verifier):
    from full_bianchi_hyrec.trajectory import primordial_2012_refined_u6_rt_boundary as original
    if verifier.CPU_CAP != 60 or verifier.WALL_CAP != 180:
        raise ValueError("LEGACY_RESOURCE_CAP_DRIFT")
    if (original.DLNA != 4.245e-5 or verifier.CHECKPOINT_SHA256 != CHECKPOINT_SHA256
            or (verifier.START_IZ, verifier.RT_IZ, verifier.PREFIX_COLUMNS,
                verifier.MAX_EXTRA_ACCEPTED) != (53179, 36446, 16733, 5210)):
        raise ValueError("R3P_FROZEN_H2_U5_CONTRACT")


class InheritedResourceLimits:
    """Module-local proxy: a frozen setrlimit request may only lower limits.

    Budget.run gives the child a remaining-allowance hard CPU limit that can
    already be below 60. Clamp both requested limits to the inherited limits,
    including in native child preexec callbacks, without changing frozen code.
    """
    def __init__(self, module, statistics):
        self.module, self.statistics = module, statistics

    def __getattr__(self, name):
        return getattr(self.module, name)

    def setrlimit(self, kind, limits):
        if kind not in (self.module.RLIMIT_CPU, self.module.RLIMIT_AS):
            return self.module.setrlimit(kind, limits)
        inherited = self.module.getrlimit(kind)

        def minimum(*values):
            finite = [v for v in values if v != self.module.RLIM_INFINITY]
            return min(finite) if finite else self.module.RLIM_INFINITY

        hard = minimum(limits[1], inherited[1])
        soft = minimum(limits[0], inherited[0], hard)
        self.module.setrlimit(kind, (soft, hard))
        self.statistics.setdefault("resource_limits", []).append({
            "resource": "CPU" if kind == self.module.RLIMIT_CPU else "AS",
            "requested": list(limits), "inherited": list(inherited),
            "applied": [soft, hard]})


@contextmanager
def audit_bindings(verifier, *, source_zip, backend, build_info, binding,
                   block_columns, statistics):
    """Scoped module-local injection; R3L separately restores its instrumentation."""
    import r3p_stream_audit as scalar
    originals = {}
    root = Path(verifier.ROOT)
    source_zip = Path(source_zip).resolve()
    original_extract = verifier.safe_extract_source
    original_rates = verifier.OriginalHyRecPrimitiveRateTable

    def replace(name, value):
        originals[name] = getattr(verifier, name)
        setattr(verifier, name, value)

    def selected_archive(requested):
        if Path(requested).resolve() != (root / SOURCE_ZIP).resolve():
            raise ValueError("R3P_UNEXPECTED_SOURCE_ARCHIVE_REQUEST")
        return source_zip

    def extract(requested, dest):
        return original_extract(selected_archive(requested), dest)

    def rates(requested):
        return original_rates.from_archive(selected_archive(requested))

    @wraps(scalar.compare_native_stream)
    def compare(*args, **kwargs):
        if backend == "cached":
            return scalar.compare_native_stream(*args, **kwargs)
        # Construct the pool here, after frozen main() pins the calling thread
        # to one CPU. Constructing it before main would leak broader affinity.
        if hasattr(os, "sched_getaffinity") and len(os.sched_getaffinity(0)) != 1:
            raise ValueError("R3P_RUST_REQUIRES_FROZEN_SINGLE_CPU_AFFINITY")
        if verify_build_receipt(build_info["receipt"], binding, root) != build_info:
            raise ValueError("R3P_BUILD_CHANGED_BEFORE_AUDIT")
        from r3p_rust_audit import PrefixAuditor
        prefix = PrefixAuditor(build_info["library"], threads=1, block_columns=block_columns)
        primary = None
        try:
            return scalar.compare_native_stream(*args, **kwargs, prefix_auditor=prefix)
        except BaseException as exc:
            primary = exc
            raise
        finally:
            statistics["prefix"] = dict(prefix.stats)
            try:
                prefix.close()
            except BaseException as exc:
                if primary is None:
                    raise
                primary.add_note(f"Secondary Rust prefix close failure: {type(exc).__name__}: {exc}")

    try:
        replace("compare_native_stream", compare)
        replace("causal_link_count", scalar.causal_link_count)
        replace("verify_source_closure", lambda checkpoint: verify_frozen_closure(root, checkpoint, source_zip))
        replace("safe_extract_source", extract)
        # The primitive-rate class itself is never modified for other importers.
        replace("OriginalHyRecPrimitiveRateTable", SimpleNamespace(from_archive=rates))
        if hasattr(verifier, "resource"):
            replace("resource", InheritedResourceLimits(verifier.resource, statistics))
        yield
    finally:
        for name, value in reversed(tuple(originals.items())):
            setattr(verifier, name, value)


def dump_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def execute(verifier, owned_integrator, *, checkpoint, source_zip, evidence,
            steps, binding, allocation_id, backend="cached", build=None,
            block_columns=32, container="stored"):
    validate_options(steps=steps, backend=backend, build=build, block_columns=block_columns,
                     allocation_id=allocation_id, container=container)
    validate_verifier(verifier)
    root, evidence = Path(verifier.ROOT), Path(evidence).resolve()
    receipt = evidence.parent / (evidence.name + ".r3p_execution.json")
    profile_path = evidence.parent / (evidence.name + ".r3l_profile.json")
    journal = evidence.parent / (evidence.name + ".r3l_phases.jsonl")
    if any(path.exists() for path in (evidence, receipt, profile_path, journal)):
        raise FileExistsError("CREATE_ONLY_R3P_EVIDENCE_ALREADY_EXISTS")
    evidence.parent.mkdir(parents=True, exist_ok=True)
    settings = {"backend": backend, "rust_threads": 1 if backend == "rust" else None,
                "block_columns": block_columns if backend == "rust" else None,
                "cached_causal_geometry": True,
                "guard_timing": "ORIGINAL_SCALAR_4096_LINES" if backend == "cached" else
                                "RUST_BOUNDED_CHUNKS_PLUS_4096_LINES_SEPARATE_FROM_SCALAR",
                "python_prefix_nonfinite": "REJECT_C_PREFIX_NONFINITE"}
    settings["input_contract"] = (
        {"grammar": "EXACTLY_FOUR_ASCII_COMMA_SEPARATED_FIELDS_PV_OR_PL",
         "indices": "CANONICAL_ASCII_UNSIGNED_DECIMAL",
         "temperature_and_energy": "FINITE_AND_STRICTLY_POSITIVE",
         "tolerance": "FINITE", "stricter_than_legacy": True,
         "legacy_trailing_fields_and_incidental_exception_types": "NOT_PRESERVED",
         "earliest_logical_failure": "WITHIN_THE_BOUNDED_BLOCK_DELIVERED_TO_RUST_ONLY",
         "abort_priority": "RESOURCE_TRANSPORT_SIZE_AND_GUARD_ABORTS_MAY_PRECEDE_UNDELIVERED_ROW_ERRORS"}
        if backend == "rust" else
        {"grammar": "LEGACY_SCALAR_WITH_DOCUMENTED_PYTHON_PREFIX_NONFINITE_REJECTION",
         "earliest_logical_failure": "ORIGINAL_SCALAR_RECORD_ORDER_AND_GUARD_BOUNDARIES"})
    statistics = {}
    report = {"schema": "rec.r3p.u6-audited-run.v1", "execution_status": "failed",
              "source": binding, "audit": settings, "requested_steps": steps,
              "start": "ORIGINAL_FROZEN_H2_U5", "dlna": 4.245e-5,
              "REI_activation": False, "allocation_id": allocation_id,
              "historical_status": {"h_U5": "HOLD_9_FAIL", "h2_U5": "HOLD_8_FAIL",
                                    "allocation": "CLOSED_HOLD_NOT_RESET"},
              "full_run_admission": "UNAVAILABLE_SMOKE_PILOT_ONLY",
              "scientific_status": "READ_ORIGINAL_VERIFICATION_RECEIPT",
              "limits": {"max_steps": 128, "cpu_s": 60, "wall_s": 180,
                         "address_bytes": 2*1024**3, "cpu_affinity_count": 1},
              "limits_scope": "INNER_FROZEN_VERIFIER_REQUESTED_LIMITS_CLAMPED_TO_INHERITED_LIMITS",
              "whole_launch_budget_scope": "PUBLIC_CLI_REQUIRES_SEPARATE_SUPERVISOR_RECEIPT;_PROGRAMMATIC_EXECUTE_IS_WORKER_ONLY",
              "supervisor_receipt": str(evidence.parent / (evidence.name + ".r3p_supervision") / "supervision.json"),
              "history_container": container, "first_failure": None}
    primary, secondary = None, []

    def failure(stage, error):
        nonlocal primary
        detail = {"stage": stage, "type": type(error).__name__, "message": str(error)}
        if primary is None:
            primary = (error, error.__traceback__)
            report["first_failure"] = detail
        else:
            secondary.append(detail)

    try:
        if bind_audited_source(root, binding["commit"]) != binding:
            raise ValueError("R3P_SOURCE_CHANGED_BEFORE_RUN")
        report["inputs_before"] = input_binding(checkpoint, source_zip)
        build_info = None if backend == "cached" else verify_build_receipt(build, binding, root)
        report["build"] = build_info
        launch_binding = {**binding, "r3p_audit": settings, "r3p_build": build_info,
                          "r3p_inputs": report["inputs_before"]}
        with audit_bindings(verifier, source_zip=source_zip, backend=backend,
                            build_info=build_info, binding=binding,
                            block_columns=block_columns, statistics=statistics):
            profile = profiled.execute(
                verifier, owned_integrator, checkpoint=checkpoint, evidence=evidence,
                steps=steps, binding=launch_binding, allocation_id=allocation_id,
                container=container)
        report["execution_status"] = "returned"
        report["verification"] = profile.get("verification")
    except BaseException as exc:
        failure("launch_or_verifier", exc)
    finally:
        report["audit_statistics"] = statistics
        for stage, check in (
            ("source_closeout", lambda: bind_audited_source(root, binding["commit"]) == binding),
            ("input_closeout", lambda: input_binding(checkpoint, source_zip) == report.get("inputs_before")),
            ("frozen_v6_closeout", lambda: bool(verify_frozen_closure(root, checkpoint, source_zip))),
        ):
            try:
                if not check():
                    raise ValueError(f"R3P_IDENTITY_CHANGED:{stage}")
            except BaseException as exc:
                failure(stage, exc)
        if backend == "rust" and report.get("build") is not None:
            try:
                if verify_build_receipt(build, binding, root) != report["build"]:
                    raise ValueError("R3P_BUILD_CHANGED_DURING_RUN")
            except BaseException as exc:
                failure("build_closeout", exc)
        try:
            report["profile"] = {"path": str(profile_path), "sha256": file_sha256(profile_path)} if profile_path.is_file() else None
        except BaseException as exc:
            failure("profile_receipt_hash", exc)
        report["execution_status"] = "failed" if primary else "returned"
        report["identity_status"] = "UNCHANGED" if not primary and not secondary else "READ_FAILURES"
        report["closeout_errors"] = secondary
        try:
            dump_new(receipt, report)
        except BaseException as exc:
            failure("runner_receipt_save", exc)
    if primary is not None:
        for detail in secondary:
            primary[0].add_note("Secondary R3P closeout failure: " + repr(detail))
        raise primary[0].with_traceback(primary[1])
    return report


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--source-zip", type=Path, default=ROOT / SOURCE_ZIP)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--new-allocation-id", required=True,
                        help="identifier of an already-valid bounded allowance; creates no allocation")
    parser.add_argument("--mode", choices=("smoke", "pilot"), default="smoke")
    parser.add_argument("--pilot-steps", type=int, default=128)
    parser.add_argument("--audit-backend", choices=("cached", "rust"), default="cached")
    parser.add_argument("--build", type=Path, help="existing build.json from the separate offline builder; required for rust")
    parser.add_argument("--block-columns", type=int, default=32)
    parser.add_argument("--history-container", choices=("stored", "compressed"), default="stored")
    args = parser.parse_args(argv)
    try:
        args.steps = step_count(args.mode, args.pilot_steps)
        validate_options(steps=args.steps, backend=args.audit_backend, build=args.build,
                         block_columns=args.block_columns, allocation_id=args.new_allocation_id,
                         container=args.history_container)
        if re.fullmatch(r"[0-9a-f]{40}", args.expected_commit) is None:
            raise ValueError("EXACT_SOURCE_COMMIT_REQUIRED")
    except ValueError as exc:
        parser.error(str(exc))
    return args


def main(argv=None):
    args = parse_args(argv)
    binding = bind_audited_source(ROOT, args.expected_commit)
    import verify_r3i_h2_u6_rt_boundary as verifier
    from full_bianchi_hyrec.trajectory.primordial_2012_owned_u6 import integrate_u6_owned
    report = execute(verifier, integrate_u6_owned, checkpoint=args.checkpoint,
                     source_zip=args.source_zip, evidence=args.evidence_dir,
                     steps=args.steps, binding=binding, allocation_id=args.new_allocation_id,
                     backend=args.audit_backend, build=args.build,
                     block_columns=args.block_columns, container=args.history_container)
    print(json.dumps(report, sort_keys=True, allow_nan=False))

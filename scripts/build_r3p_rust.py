#!/usr/bin/env python3
"""Offline, source-bound build of the bounded R3P audit library and ABI tests."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_r3o_rust import Budget, dump_new, finalize_resource_record, sha256


def source_hashes():
    crate = ROOT / "rust/rec-stream-audit"
    files = sorted(crate.rglob("*.rs")) + [crate/"Cargo.toml", crate/"Cargo.lock",
        crate/"include/rec_stream_audit.h", crate/"tests/abi_smoke.c",
        ROOT/"scripts/build_r3p_rust.py", ROOT/"scripts/build_r3o_rust.py",
        ROOT/"rust/REC_STREAM_AUDIT_VENDOR.json"]
    return {str(p.relative_to(ROOT)):sha256(p) for p in files}


def build(output, rust_bin_dir=None):
    out = Path(output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    budget = Budget(out, cpu_s=90., wall_s=180., memory_bytes=2*1024**3)
    report = {"schema":"rec.r3p.audit-build.v1", "status":"FAILED",
              "source_sha256":source_hashes(), "new_physical_runs":0,
              "cpu_cap_s":90., "wall_cap_s":180., "memory_bytes":2*1024**3}
    exit_code = 2
    try:
        env = os.environ.copy()
        if rust_bin_dir is not None:
            env["PATH"] = str(Path(rust_bin_dir).resolve()) + os.pathsep + env.get("PATH", "")
        for key in ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC_WRAPPER",
                    "RUSTC_WORKSPACE_WRAPPER", "RUSTDOCFLAGS"):
            env.pop(key, None)
        rustc, cargo = shutil.which("rustc", path=env.get("PATH")), shutil.which("cargo", path=env.get("PATH"))
        if not rustc or not cargo:
            raise RuntimeError("R3P_RUST_TOOLCHAIN_REQUIRED")
        version = subprocess.check_output([rustc,"--version"], env=env, text=True, timeout=10).strip()
        if not version.startswith("rustc 1.94.1 "):
            raise ValueError("R3P_REPRODUCIBLE_RUST_1_94_1_REQUIRED")
        report["rustc"] = version
        report["cargo"] = subprocess.check_output([cargo,"--version"], env=env, text=True, timeout=10).strip()
        meta = json.loads((ROOT/"rust/REC_STREAM_AUDIT_VENDOR.json").read_text())
        archive = ROOT / meta["file"]
        if sha256(archive) != meta["sha256"] or sha256(ROOT/"rust/rec-stream-audit/Cargo.lock") != meta["cargo_lock_sha256"]:
            raise ValueError("R3P_VENDOR_OR_LOCK_IDENTITY")
        report["vendor_sha256"] = meta["sha256"]
        with tarfile.open(archive) as tar:
            for m in tar.getmembers():
                p = Path(m.name)
                if p.is_absolute() or ".." in p.parts or not p.parts or p.parts[0] != "registry-vendor" or not (m.isfile() or m.isdir()):
                    raise ValueError("R3P_UNSAFE_VENDOR_MEMBER")
            tar.extractall(out, filter="data")
        work = out / "work"
        shutil.copytree(ROOT/"rust/rec-stream-audit", work)
        (work/".cargo").mkdir()
        config = '[source.crates-io]\nreplace-with="vendored-sources"\n[source.vendored-sources]\ndirectory='+json.dumps(str(out/"registry-vendor"))+'\n'
        (work/".cargo/config.toml").write_text(config)
        env.update(CARGO_HOME=str(out/"cargo-home"), CARGO_TARGET_DIR=str(out/"target"),
                   CARGO_BUILD_JOBS="1", CARGO_NET_OFFLINE="true", RUSTC=rustc,
                   CARGO_INCREMENTAL="0", RAYON_NUM_THREADS="1")
        budget.run([cargo,"test","--release","--locked","--offline","--lib"], cwd=work, env=env, label="rust_tests")
        budget.run([cargo,"rustc","--release","--locked","--offline","--lib","--","--emit=llvm-ir,asm,link"], cwd=work, env=env, label="rust_build")
        lib = out/"target/release/librec_stream_audit.so"
        if not lib.is_file():
            raise RuntimeError("R3P_LIBRARY_MISSING")
        compiler = shutil.which("cc")
        if not compiler:
            raise RuntimeError("R3P_C_COMPILER_REQUIRED")
        binary = out/"abi_smoke"
        budget.run([compiler,"-std=c11","-Wall","-Wextra","-Werror","-ffp-contract=off",
                    str(work/"tests/abi_smoke.c"),"-I",str(work/"include"),"-L",str(lib.parent),
                    "-lrec_stream_audit","-lm","-Wl,-rpath,"+str(lib.parent),"-o",str(binary)],
                   cwd=work, env=env, label="abi_build")
        budget.run([binary], cwd=work, env=env, label="abi_test")
        if source_hashes() != report["source_sha256"]:
            raise RuntimeError("R3P_INPUT_MUTATED_DURING_BUILD")
        report.update(status="BUILT", library=str(lib), library_sha256=sha256(lib),
                      abi_binary_sha256=sha256(binary), commands=budget.commands)
        report["compiler_artifacts"] = {str(p.relative_to(out)):sha256(p)
            for ext in ("*.ll","*.s") for p in sorted((out/"target/release/deps").glob(ext))}
        exit_code = 0
    except BaseException as exc:
        report.update(status="FAILED", first_failure={"type":type(exc).__name__,"message":str(exc)}, commands=budget.commands)
    finally:
        exit_code = finalize_resource_record(report,budget,exit_code,"R3P_BUILD")
        dump_new(out/"build.json", report)
    return report, exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rust-bin-dir", type=Path)
    args = parser.parse_args()
    report, code = build(args.output,args.rust_bin_dir)
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    raise SystemExit(code)


if __name__ == "__main__":
    main()

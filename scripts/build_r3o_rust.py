#!/usr/bin/env python3
"""Bounded, create-only build of the R3O Rust caller; no numerical campaign.

Default: source Cargo build with private home/target; --registry-vendor makes it
offline. --reuse-deps links the
new caller to authenticated, read-only prior dependencies, not an old executable.
Neither path downloads a toolchain or edits a cache or existing HyRec source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import traceback

sys.dont_write_bytecode = True
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "RAYON_NUM_THREADS"):
    os.environ[_key] = "1"
ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "rust/rec-hyrec-vigilode"
SOURCE_META = ROOT / "rust/VIGILODE_SOURCE.json"
VENDOR = ROOT / "rust/vendor-vigilode-a21d573"
COMMIT = "a21d573980f66fe02891bd216153443b5352f921"
ORIGINAL_ZIP = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def reserve(path):
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=False)
    return p


def cpu():
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def live_usage(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()
        ticks = sum(int(fields[i]) for i in (11, 12, 13, 14))
        rss = int(fields[21]) * os.sysconf("SC_PAGE_SIZE")
        children = Path(f"/proc/{pid}/task/{pid}/children").read_text().split()
    except (FileNotFoundError, ProcessLookupError):
        return 0., 0
    used = ticks / os.sysconf("SC_CLK_TCK")
    for child in children:
        c, r = live_usage(int(child))
        used += c
        rss += r
    return used, rss


def procfs_child_pid(namespace_pid):
    """Map Popen's PID to the PID namespace mounted at /proc.

    This host exposes outer PIDs in /proc while getpid/Popen return inner PIDs.
    Reading /proc/<Popen.pid> would otherwise inspect an unrelated host process.
    Only the launcher's own child list is searched, never a machine-wide scan.
    """
    own = int(Path("/proc/self/stat").read_text().split(" ",1)[0])
    children = Path(f"/proc/{own}/task/{own}/children").read_text().split()
    for child in children:
        try:
            status = Path(f"/proc/{child}/status").read_text().splitlines()
        except FileNotFoundError:
            continue
        nspid = next((line.split()[1:] for line in status if line.startswith("NSpid:")), [])
        if (nspid and int(nspid[-1]) == namespace_pid) or (not nspid and own == os.getpid() and int(child) == namespace_pid):
            return int(child)
    return None


class Budget:
    """Aggregate CPU/wall monitor, process-group kill, and retained command logs."""
    def __init__(self, directory, cpu_s=240., wall_s=480., memory_bytes=3*1024**3):
        self.directory = Path(directory)
        self.cpu_s, self.wall_s, self.memory_bytes = cpu_s, wall_s, memory_bytes
        self.start_cpu, self.start_wall = cpu(), time.monotonic()
        self.commands = []

    def check(self, child_cpu=0., rss=0):
        if cpu()-self.start_cpu+child_cpu > self.cpu_s-2.:
            raise RuntimeError("R3O_AGGREGATE_CPU_CAP")
        if time.monotonic()-self.start_wall > self.wall_s-3.:
            raise RuntimeError("R3O_WALL_CAP")
        if rss > self.memory_bytes:
            raise RuntimeError("R3O_AGGREGATE_CHILD_RSS_CAP")

    def run(self, command, *, cwd, env, label, expected=(0,)):
        self.check()
        before, wall = cpu(), time.monotonic()
        log = self.directory / label
        remaining = max(1, math.ceil(self.cpu_s-(cpu()-self.start_cpu)-2.))
        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (self.memory_bytes, self.memory_bytes))
            resource.setrlimit(resource.RLIMIT_CPU, (remaining, remaining+1))
        process = None
        procfs_pid = None
        failure = None
        max_rss = 0
        with log.with_suffix(".stdout.log").open("xb") as out, log.with_suffix(".stderr.log").open("xb") as err:
            try:
                process = subprocess.Popen([str(x) for x in command], cwd=cwd, env=env,
                    stdout=out, stderr=err, start_new_session=True, preexec_fn=limits)
                while process.poll() is None:
                    if procfs_pid is None:
                        procfs_pid = procfs_child_pid(process.pid)
                    if procfs_pid is None:
                        if time.monotonic()-wall > 1.:
                            raise RuntimeError("R3O_PROCFS_CHILD_PID_UNRESOLVED")
                        ccpu,rss=0.,0
                    else:
                        ccpu, rss = live_usage(procfs_pid)
                    max_rss = max(max_rss, rss)
                    self.check(ccpu, rss)
                    time.sleep(.05)
            except BaseException as exc:
                failure = f"{type(exc).__name__}: {exc}"
                if process is not None and process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        result = {"command": [str(x) for x in command], "cwd": str(cwd),
            "returncode": None if process is None else process.returncode,
            "wall_s": time.monotonic()-wall, "process_tree_cpu_s": cpu()-before,
            "max_polled_process_tree_rss_bytes": max_rss or None,
            "pid_namespace_mapping":{"popen_pid":None if process is None else process.pid,"procfs_pid":procfs_pid},"failure": failure,
            "stdout": str(log.with_suffix(".stdout.log")), "stderr": str(log.with_suffix(".stderr.log")),
            "stdout_sha256": sha256(log.with_suffix(".stdout.log")),
            "stderr_sha256": sha256(log.with_suffix(".stderr.log"))}
        self.commands.append(result)
        dump_new(log.with_suffix(".execution.json"), result)
        if failure or result["returncode"] not in expected:
            raise RuntimeError(f"R3O_COMMAND_FAILED:{label}:{result['returncode']}:{failure}")
        self.check()
        return result


def own_code_hashes():
    paths = list(PACKAGE.rglob("*.rs")) + [PACKAGE/"Cargo.toml", PACKAGE/"Cargo.lock"]
    paths += [p for p in (PACKAGE/"fixtures").glob("*") if p.is_file()]
    paths += [ROOT/"scripts/build_r3o_rust.py", ROOT/"scripts/verify_r3o_rust.py",
        ROOT/"scripts/c_harness/original_hyrec_r3o_rust_bridge.c",
        ROOT/"scripts/c_harness/original_hyrec_r3o_lowz_harness.c",
        ROOT/"tests/trajectory/test_r3o_rust.py"]
    # Imported numerical and source-preparation code participates in the seal.
    paths += [ROOT/"scripts/verify_r3o_lowz.py"]
    paths += list((ROOT/"src/full_bianchi_hyrec/trajectory").glob("*.py"))
    return {str(p.relative_to(ROOT)): sha256(p) for p in sorted(set(paths)) if p.is_file()}


def ensure_vigilode():
    meta = json.loads(SOURCE_META.read_text())
    if meta["commit"] != COMMIT or meta["numerical_source_changes"]:
        raise ValueError("R3O_VIGILODE_PIN_OR_NUMERICAL_EDIT")
    archive = ROOT / meta["archive"]["path"]
    if sha256(archive) != meta["archive"]["sha256"]:
        raise ValueError("R3O_VIGILODE_ARCHIVE_HASH")
    expected = {x["path"]: x["sha256"] for x in meta["selected_upstream_files"]}
    expected["Cargo.upstream.toml"] = expected["Cargo.toml"]
    expected["Cargo.toml"] = meta["packaging_only_changes"][0]["packaged_sha256"]
    if not VENDOR.exists():
        # NCP compile preparation authorized by the pinned source handoff.
        # Validate every member before a single source file is materialized.
        with tarfile.open(archive, "r:gz") as tf:
            members = tf.getmembers()
            actual = {}
            for m in members:
                rel = Path(m.name)
                if not m.isfile() or rel.is_absolute() or ".." in rel.parts or rel.parts[0] != VENDOR.name:
                    raise ValueError("R3O_VIGILODE_UNSAFE_ARCHIVE_MEMBER")
                key = Path(*rel.parts[1:]).as_posix()
                if key in actual:
                    raise ValueError("R3O_VIGILODE_DUPLICATE_MEMBER")
                data = tf.extractfile(m).read()
                actual[key] = hashlib.sha256(data).hexdigest()
            if actual != expected:
                raise ValueError("R3O_VIGILODE_ARCHIVE_MEMBER_IDENTITY")
            VENDOR.mkdir(parents=True, exist_ok=False)
            for m in members:
                target = VENDOR.parent / m.name
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(tf.extractfile(m).read())
    observed = {}
    for p in VENDOR.rglob("*"):
        if p.is_symlink():
            raise ValueError("R3O_VIGILODE_SYMLINK")
        if p.is_file():
            observed[p.relative_to(VENDOR).as_posix()] = sha256(p)
    if observed != expected:
        raise ValueError("R3O_VIGILODE_MATERIALIZED_MEMBER_IDENTITY")
    return {"metadata_sha256": sha256(SOURCE_META), "archive_sha256": sha256(archive),
            "archive_path": str(archive), "source_path": str(VENDOR), "members": observed,
            "upstream_commit": COMMIT, "packaging_only_changes": meta["packaging_only_changes"]}


def check_reuse(deps, prior_source, source_record):
    """Use source-matched libraries with one coherent recorded Cargo profile."""
    deps, prior_source = Path(deps).resolve(), Path(prior_source).resolve()
    for key, digest in source_record["members"].items():
        if key == "Cargo.toml":
            continue
        original = "Cargo.toml" if key == "Cargo.upstream.toml" else key
        if sha256(prior_source/original) != digest:
            raise ValueError(f"R3O_REUSED_LIBRARY_SOURCE_MISMATCH:{key}")
    names = {"rodas5p_core": "f51eeb2f0ddc1bdb", "rodas5p_integrators": "078a9260a490d2a9",
             "serde": "19072e2f0126ac40", "serde_json": "c01bc2f455e40147"}
    externs = {}
    fingerprints = {}
    selected = {}
    for name, suffix in names.items():
        lib = deps/f"lib{name}-{suffix}.rlib"
        fingerprint = deps.parent/".fingerprint"/f"{name.replace('_','-') if name.startswith('rodas5p') else name}-{suffix}"/f"lib-{name}.json"
        info = json.loads(fingerprint.read_text())
        if info["profile"] != 6011240845988990581 or info["rustflags"] != []:
            raise ValueError("R3O_REUSE_PROFILE")
        if name == "serde_json" and "float_roundtrip" not in info["features"]:
            raise ValueError("R3O_FLOAT_ROUNDTRIP_REQUIRED")
        if name == "rodas5p_integrators" and json.loads(info["features"]) != ["default"]:
            raise ValueError("R3O_DEFAULT_VIGILODE_FEATURES_REQUIRED")
        externs[name] = str(lib)
        fingerprints[str(fingerprint)] = sha256(fingerprint)
        selected[name] = fingerprint
    # Cargo records each dependency edge using the child's little-endian u64
    # fingerprint. Resolve that graph, not merely similarly named cache files.
    index = {}
    for fp in (deps.parent/".fingerprint").glob("*/lib-*.json"):
        marker = fp.with_suffix("")
        if not marker.is_file():
            continue
        try:
            value = int.from_bytes(bytes.fromhex(marker.read_text().strip()), "little")
            name = fp.stem.removeprefix("lib-")
            index[(name,value)] = fp
        except ValueError:
            continue
    visited = set()
    edges = []
    def walk(fp):
        if fp in visited:return
        visited.add(fp)
        info=json.loads(fp.read_text())
        fingerprints[str(fp)]=sha256(fp)
        fingerprints[str(fp.with_suffix(""))]=sha256(fp.with_suffix(""))
        for _,name,_,expected in info["deps"]:
            if name=="build_script_build":
                continue  # not a linked Rust library; source scripts are sealed separately
            child=index.get((name,expected))
            if child is None:
                raise ValueError(f"R3O_REUSE_UNRESOLVED_DEPENDENCY_EDGE:{fp.parent.name}:{name}:{expected}")
            if name in selected and child!=selected[name]:
                raise ValueError(f"R3O_REUSE_MIXED_DEPENDENCY_SET:{name}")
            suffix=child.parent.name.rsplit("-",1)[1]
            candidates=[deps/f"lib{name}-{suffix}.rlib",deps/f"lib{name}-{suffix}.so"]
            payload=next((p for p in candidates if p.is_file()),None)
            if payload is None:
                raise ValueError(f"R3O_REUSE_MISSING_DEPENDENCY_PAYLOAD:{name}")
            edges.append({"parent":fp.parent.name,"dependency":name,"cargo_fingerprint":expected,
                "child":child.parent.name,"payload":str(payload),"payload_sha256":sha256(payload)})
            walk(child)
    for fp in selected.values():walk(fp)
    # Authenticate every potentially linked dependency, including faer 0.24.4.
    files = {str(p): sha256(p) for p in sorted(deps.iterdir()) if p.suffix in (".rlib", ".so")}
    files.update(fingerprints)
    return externs, {"kind": "NEW_CALLER_WITH_READ_ONLY_SOURCE_MATCHED_DEPENDENCIES",
        "prior_source": str(prior_source), "deps": str(deps), "files_before": files,
        "dependency_compile_commit":"8a8bd409b1d96c7b7421f496d229e119fd3d284e",
        "requested_source_commit":COMMIT,"dependency_libraries_recompiled_here":False,
        "coherent_dependency_edges_verified":edges,
        "source_relation": "BYTE_IDENTITY of selected Rust source/manifests/fixtures; root packaging adjustment excluded",
        "prior_benchmark_times_reused": False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-zip", type=Path, default=ORIGINAL_ZIP)
    ap.add_argument("--rust-bin-dir", type=Path, default=os.environ.get("REC_RUST_BIN"))
    ap.add_argument("--registry-vendor", type=Path, default=os.environ.get("REC_CARGO_VENDOR"))
    ap.add_argument("--reuse-deps", type=Path)
    ap.add_argument("--reuse-source", type=Path)
    args = ap.parse_args()
    ev = reserve(args.output)
    budget = Budget(ev)
    report = {"schema": "rec.r3o.rust-build.v1", "status": "FAILED", "command": sys.argv,
        "limits": {"cpu_s": 240., "wall_s": 480., "memory_bytes": 3*1024**3, "jobs": 1},
        "source_path": None, "numerics": "NOT_RUN"}
    exit_code = 2
    try:
        # Freeze all authored code/fixtures before Cargo can inspect the package.
        if not (PACKAGE/"Cargo.lock").is_file():
            raise ValueError("R3O_COMMITTED_CARGO_LOCK_REQUIRED")
        report["code_before"] = own_code_hashes()
        sys.path.insert(0, str(ROOT/"scripts"))
        from verify_r3o_lowz import prepare_source, source_tree_hashes
        report["vigilode"] = ensure_vigilode()
        src, manifest = prepare_source(args.source_zip.resolve(), ev/"source_h2")
        report["source_path"] = str(src)
        report["original_source"] = manifest
        dump_new(ev/"source_manifest.json", manifest)
        env = dict(os.environ)
        if args.rust_bin_dir:
            env["PATH"] = str(args.rust_bin_dir.resolve())+os.pathsep+env.get("PATH", "")
        rustc = shutil.which("rustc", path=env.get("PATH"))
        cargo = shutil.which("cargo", path=env.get("PATH"))
        if not rustc or not cargo:
            raise ValueError("R3O_EXISTING_RUST_TOOLCHAIN_REQUIRED_NO_DOWNLOAD")
        toolchain = budget.run([rustc, "-Vv"], cwd=ROOT, env=env, label="rustc_version")
        version = Path(toolchain["stdout"]).read_text()
        if "release: 1.94.1" not in version:
            raise ValueError("R3O_RUST_1_94_1_REQUIRED")
        report["rustc_version"] = version
        report["toolchain_hashes"] = {rustc:sha256(rustc), cargo:sha256(cargo)}
        home = reserve(ev/"cargo_home")
        target = reserve(ev/"target")
        registry = args.registry_vendor
        if registry is not None and not registry.is_dir():
            raise ValueError("R3O_OFFLINE_REGISTRY_VENDOR_NOT_FOUND")
        if args.reuse_deps and registry is None:
            raise ValueError("R3O_REUSE_ROUTE_REQUIRES_OFFLINE_REGISTRY_VENDOR")
        offline = ["--offline"] if registry is not None else []
        config = ('[source.crates-io]\nreplace-with = "r3o-vendor"\n[source.r3o-vendor]\ndirectory = '+json.dumps(str(registry.resolve()))+'\n[net]\noffline = true\n' if registry is not None else '')+'[build]\njobs = 1\n'
        (home/"config.toml").write_text(config)
        env.update(CARGO_HOME=str(home), CARGO_TARGET_DIR=str(target), REC_HYREC2012_SRC=str(src),
                   CARGO_BUILD_JOBS="1", CARGO_INCREMENTAL="0", RUSTC=rustc)
        for key in ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER"):
            env.pop(key, None)
        budget.run([cargo,"metadata","--locked","--format-version","1","--no-deps",*offline,"--manifest-path",PACKAGE/"Cargo.toml"],
                   cwd=PACKAGE, env=env, label="cargo_locked_metadata")
        if own_code_hashes() != report["code_before"]:
            raise ValueError("R3O_CODE_OR_LOCK_MUTATION_DURING_CARGO_PREFLIGHT")
        report["environment"] = {k:env[k] for k in ("CARGO_HOME","CARGO_TARGET_DIR","REC_HYREC2012_SRC","CARGO_BUILD_JOBS","CARGO_INCREMENTAL","RUSTC")}
        if args.reuse_deps:
            if not args.reuse_source:
                raise ValueError("R3O_REUSE_SOURCE_REQUIRED")
            externs, reuse = check_reuse(args.reuse_deps,args.reuse_source,report["vigilode"])
            report["dependency_reuse"] = reuse
            # Execute the same build.rs as Cargo; it invokes cc/ar serially.
            build_driver = target/"r3o-build-script"
            budget.run([rustc,"--edition=2024",PACKAGE/"build.rs","-o",build_driver], cwd=PACKAGE,env=env,label="compile_build_rs")
            native = reserve(target/"native")
            build_env = dict(env, CARGO_MANIFEST_DIR=str(PACKAGE), OUT_DIR=str(native))
            budget.run([build_driver],cwd=PACKAGE,env=build_env,label="native_build")
            binary = target/"rec-hyrec-vigilode"
            cmd = [rustc,"--edition=2024","--crate-name","rec_hyrec_vigilode",PACKAGE/"src/main.rs",
                "-C","opt-level=2","-C","codegen-units=1","-C","panic=abort","-C","debuginfo=0",
                "-C","link-arg=-fuse-ld=lld","-C","link-arg=-Wl,--threads=1","-C","link-arg=-Wl,--lto-O0",
                "-L",f"dependency={args.reuse_deps.resolve()}","-L",f"native={native}","-l","static=rec_hyrec2012","-l","m"]
            for name, path in externs.items():
                cmd += ["--extern",f"{name}={path}"]
            cmd += ["-o",binary]
            budget.run(cmd,cwd=PACKAGE,env=env,label="rust_caller_build")
            report["build_mode"] = "REBUILD_C_BRIDGE_AND_RUST_CALLER_WITH_SOURCE_MATCHED_RLIBS"
        else:
            if shutil.disk_usage(ev).free < 900*1024**2:
                raise RuntimeError("R3O_FULL_CARGO_BUILD_DISK_HEADROOM_BELOW_900_MIB")
            budget.run([cargo,"build","--locked",*offline,"--release","-j1","--manifest-path",PACKAGE/"Cargo.toml"],
                       cwd=PACKAGE,env=env,label="cargo_build")
            binary = target/"release/rec-hyrec-vigilode"
            report["build_mode"] = "FRESH_OFFLINE_CARGO_BUILD" if offline else "FRESH_CARGO_BUILD"
        report["binary"] = str(binary)
        report["binary_sha256"] = sha256(binary)
        report["binary_bytes"] = binary.stat().st_size
        report["status"] = "BUILD_PASS"
        exit_code = 0
    except BaseException as exc:
        report["failure"] = {"type":type(exc).__name__,"message":str(exc)}
        with (ev/"exception.txt").open("x") as stream:
            traceback.print_exc(file=stream)
    finally:
        try:
            if "code_before" in report:
                report["code_after"] = own_code_hashes()
                if report["code_after"] != report["code_before"]:
                    raise ValueError("R3O_CODE_MUTATION_DURING_BUILD")
            if report.get("source_path"):
                report["source_after"] = source_tree_hashes(Path(report["source_path"]))
                if report["source_after"] != report["original_source"]["compiled_members"]:
                    raise ValueError("R3O_C_SOURCE_MUTATION")
            if "vigilode" in report and ensure_vigilode() != report["vigilode"]:
                raise ValueError("R3O_VIGILODE_MUTATION")
            if "dependency_reuse" in report:
                before = report["dependency_reuse"]["files_before"]
                after = {p:sha256(p) for p in before}
                report["dependency_reuse"]["files_after"] = after
                if after != before:
                    raise ValueError("R3O_REUSED_DEPENDENCY_MUTATION")
            if "binary" in report:
                report["binary_after_sha256"] = sha256(report["binary"])
                if report["binary_after_sha256"] != report["binary_sha256"]:
                    raise ValueError("R3O_BINARY_MUTATION")
        except BaseException as exc:
            report["identity_failure"] = str(exc)
            report["status"] = "FAILED"
            exit_code = 2
        report["commands"] = budget.commands
        report["process_tree_cpu_s"] = cpu()-budget.start_cpu
        report["wall_s"] = time.monotonic()-budget.start_wall
        if report["process_tree_cpu_s"]>240. or report["wall_s"]>480.:
            report["status"]="FAILED"
            report["resource_failure"]="R3O_TOTAL_BUILD_BUDGET"
            exit_code=2
        report["exit_code"] = exit_code
        dump_new(ev/"build.json",report)
        print(json.dumps({k:report.get(k) for k in ("status","binary","binary_sha256","process_tree_cpu_s","wall_s","failure","identity_failure")}))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

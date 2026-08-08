#!/usr/bin/env python3
"""Run the scientific pytest tier with one fresh interpreter per slow file.

The repository's slow tests load several independent SciPy/BLAS-heavy kernels.
Running every node in a separate interpreter is deterministic but needlessly
expensive; running all slow tests in one interpreter can stall during extension
module teardown.  This runner keeps the isolation boundary at the test-file
level, disables third-party pytest plugin autoloading, and pins numerical
thread pools to one thread.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import sys
from typing import Mapping, NamedTuple

ROOT = Path(__file__).resolve().parents[1]
BLAS_THREAD_VARIABLES = (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "BLIS_NUM_THREADS",
)
RECEIPT_SCHEMA = "REC_BIANCHI_SCIENTIFIC_FILE_RECEIPT_V1"
RECEIPT_DIR = Path(".cache/scientific_test_receipts")


def _scientific_input_paths(root: Path) -> list[Path]:
    """Return the computational files that invalidate slow-test receipts."""
    paths: set[Path] = set()
    for relative in (
        "src",
        "tests/recoil",
        "tests/trajectory",
        "archive/inputs",
        "archive/expanded",
        "data",
    ):
        base = root / relative
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            paths.add(path)

    for relative in ("pyproject.toml", "tests/conftest.py"):
        path = root / relative
        if path.is_file():
            paths.add(path)

    scripts = root / "scripts"
    if scripts.is_dir():
        excluded = {
            "bootstrap_sandbox.sh",
            "check_commit_range_whitespace.py",
            "check_hyrec_binary_hash_policy.py",
            "check_imports.py",
            "check_remote_state.py",
            "export_git_bundle_delivery.py",
        }
        for path in scripts.iterdir():
            if not path.is_file() or path.name in excluded:
                continue
            if path.suffix in {".py", ".sh"}:
                paths.add(path)

    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def scientific_input_fingerprint(root: Path = ROOT) -> str:
    """Hash every scientific code, test, canonical-input and evidence file."""
    digest = hashlib.sha256()
    for path in _scientific_input_paths(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def _receipt_path(root: Path, test_file: str) -> Path:
    token = hashlib.sha256(test_file.encode("utf-8")).hexdigest()[:16]
    stem = Path(test_file).stem
    return root / RECEIPT_DIR / f"{token}_{stem}.json"


def _receipt_log_path(root: Path, test_file: str) -> Path:
    return _receipt_path(root, test_file).with_suffix(".log")


def write_scientific_receipt(
    *,
    root: Path,
    test_file: str,
    nodes: list[str],
    fingerprint: str,
    elapsed_seconds: float,
    output: str = "",
) -> Path:
    """Atomically record one slow-file PASS against a scientific fingerprint."""
    receipt_path = _receipt_path(root, test_file)
    log_path = _receipt_log_path(root, test_file)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(output, encoding="utf-8")
    payload = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "scientific_input_fingerprint": fingerprint,
        "test_file": test_file,
        "nodes": list(nodes),
        "node_count": len(nodes),
        "elapsed_seconds": float(elapsed_seconds),
        "python": sys.version.split()[0],
        "environment": {
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            **{name: "1" for name in BLAS_THREAD_VARIABLES},
        },
        "log": log_path.relative_to(root).as_posix(),
        "log_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
    }
    temporary = receipt_path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(receipt_path)
    return receipt_path


def valid_scientific_receipt(
    *,
    root: Path,
    test_file: str,
    nodes: list[str],
    fingerprint: str,
) -> bool:
    receipt_path = _receipt_path(root, test_file)
    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    if payload.get("schema") != RECEIPT_SCHEMA or payload.get("status") != "PASS":
        return False
    if payload.get("scientific_input_fingerprint") != fingerprint:
        return False
    if payload.get("test_file") != test_file or payload.get("nodes") != nodes:
        return False
    log_path = root / str(payload.get("log", ""))
    if not log_path.is_file():
        return False
    output = log_path.read_text(encoding="utf-8")
    return hashlib.sha256(output.encode("utf-8")).hexdigest() == payload.get(
        "log_sha256"
    )




class ScientificRunResult(NamedTuple):
    slow_files: tuple[str, ...]
    slow_nodes: tuple[str, ...]
    fast_suite_ran: bool

    @property
    def slow_file_count(self) -> int:
        return len(self.slow_files)

    @property
    def slow_test_count(self) -> int:
        return len(self.slow_nodes)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "slow_files": list(self.slow_files),
            "slow_nodes": list(self.slow_nodes),
            "fast_suite_ran": self.fast_suite_ran,
            "slow_file_count": self.slow_file_count,
            "slow_test_count": self.slow_test_count,
            "status": "PASS",
        }


def parse_slow_collection(text: str) -> tuple[list[str], list[str]]:
    """Return ordered unique files and the exact collected slow node IDs."""
    nodes: list[str] = []
    files: list[str] = []
    seen_files: set[str] = set()
    for raw_line in text.splitlines():
        node_id = raw_line.strip()
        if "::" not in node_id:
            continue
        nodes.append(node_id)
        test_file = node_id.split("::", 1)[0]
        if test_file not in seen_files:
            seen_files.add(test_file)
            files.append(test_file)
    return files, nodes


def scientific_environment(
    base: Mapping[str, str] | None = None,
    *,
    root: Path = ROOT,
) -> dict[str, str]:
    """Build a deterministic environment for SciPy/BLAS-heavy pytest runs."""
    env = dict(os.environ if base is None else base)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    for variable in BLAS_THREAD_VARIABLES:
        env[variable] = "1"

    source_dir = str(root / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        source_dir if not existing else os.pathsep.join((source_dir, existing))
    )
    return env


def _run_checked(
    command: list[str],
    *,
    root: Path,
    env: Mapping[str, str],
    timeout: float,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            cwd=root,
            env=dict(env),
            timeout=timeout,
            check=False,
            text=True,
            capture_output=capture_output,
        )
    except subprocess.TimeoutExpired as exc:
        rendered = " ".join(command)
        raise RuntimeError(
            f"scientific test subprocess timed out after {timeout:g}s: {rendered}"
        ) from exc

    if result.returncode:
        if capture_output:
            sys.stderr.write(result.stdout or "")
            sys.stderr.write(result.stderr or "")
        raise subprocess.CalledProcessError(result.returncode, command)
    return result


def _nodes_for_file(nodes: list[str], test_file: str) -> list[str]:
    prefix = f"{test_file}::"
    return [node for node in nodes if node.startswith(prefix)]


def run_scientific_file(
    *,
    root: Path,
    test_file: str,
    nodes: list[str],
    fingerprint: str,
    timeout: float = 300.0,
) -> Path:
    """Run one slow test file and persist a fingerprint-bound PASS receipt."""
    env = scientific_environment(root=root)
    started = time.perf_counter()
    result = _run_checked(
        [sys.executable, "-m", "pytest", "-q", "-m", "slow", test_file],
        root=root,
        env=env,
        timeout=timeout,
        capture_output=True,
    )
    elapsed = time.perf_counter() - started
    output = (result.stdout or "") + (result.stderr or "")
    sys.stdout.write(output)
    return write_scientific_receipt(
        root=root,
        test_file=test_file,
        nodes=_nodes_for_file(nodes, test_file),
        fingerprint=fingerprint,
        elapsed_seconds=elapsed,
        output=output,
    )


def run_scientific(
    *,
    root: Path = ROOT,
    timeout_per_file: float = 300.0,
    collection_timeout: float = 120.0,
    fast_timeout: float = 300.0,
) -> ScientificRunResult:
    """Run every slow file in isolation, then the aggregate non-slow tier."""
    env = scientific_environment(root=root)
    collection = _run_checked(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-m", "slow"],
        root=root,
        env=env,
        timeout=collection_timeout,
        capture_output=True,
    )
    files, nodes = parse_slow_collection(collection.stdout)
    if not nodes:
        raise RuntimeError("scientific mode found no slow tests")

    fingerprint = scientific_input_fingerprint(root)
    for test_file in files:
        file_nodes = _nodes_for_file(nodes, test_file)
        if valid_scientific_receipt(
            root=root,
            test_file=test_file,
            nodes=file_nodes,
            fingerprint=fingerprint,
        ):
            print(f"[scientific] receipt PASS: {test_file}", flush=True)
            continue
        print(f"[scientific] slow file: {test_file}", flush=True)
        run_scientific_file(
            root=root,
            test_file=test_file,
            nodes=nodes,
            fingerprint=fingerprint,
            timeout=timeout_per_file,
        )

    print("[scientific] fast aggregate: -m not slow", flush=True)
    _run_checked(
        [sys.executable, "-m", "pytest", "-q", "-m", "not slow"],
        root=root,
        env=env,
        timeout=fast_timeout,
    )
    return ScientificRunResult(
        slow_files=tuple(files),
        slow_nodes=tuple(nodes),
        fast_suite_ran=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--timeout-per-file", type=float, default=300.0)
    parser.add_argument("--collection-timeout", type=float, default=120.0)
    parser.add_argument("--fast-timeout", type=float, default=300.0)
    parser.add_argument(
        "--run-file",
        action="append",
        default=[],
        help="run and receipt one slow test file; may be repeated",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    if args.run_file:
        env = scientific_environment(root=root)
        collection = _run_checked(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "-m", "slow"],
            root=root,
            env=env,
            timeout=args.collection_timeout,
            capture_output=True,
        )
        files, nodes = parse_slow_collection(collection.stdout)
        fingerprint = scientific_input_fingerprint(root)
        for test_file in args.run_file:
            if test_file not in files:
                raise SystemExit(f"not a collected slow test file: {test_file}")
            print(f"[scientific] receipt run: {test_file}", flush=True)
            path = run_scientific_file(
                root=root,
                test_file=test_file,
                nodes=nodes,
                fingerprint=fingerprint,
                timeout=args.timeout_per_file,
            )
            print(path.relative_to(root).as_posix())
        return

    result = run_scientific(
        root=root,
        timeout_per_file=args.timeout_per_file,
        collection_timeout=args.collection_timeout,
        fast_timeout=args.fast_timeout,
    )
    print(json.dumps(result.to_json_dict(), sort_keys=True))


if __name__ == "__main__":
    main()

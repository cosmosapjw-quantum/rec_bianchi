#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--scientific", action="store_true")
    args = parser.parse_args()

    state = json.loads((ROOT / "state/PROJECT_STATE.json").read_text())
    current_artifact = state["current_durable_stage"]["artifact"]
    expanded = ROOT / "archive" / "expanded" / current_artifact
    assert expanded.is_dir(), current_artifact
    current_ledger = list(expanded.glob("*_ledger.json"))
    assert current_ledger, f"missing current ledger in {expanded}"

    index = json.loads((ROOT / "state/BUNDLE_INDEX.json").read_text())
    missing: list[str] = []
    bad: list[str] = []
    for row in index:
        path = ROOT / "archive" / "bundles" / row["bundle"]
        if not path.exists():
            missing.append(row["bundle"])
            continue
        if sha256(path) != row["sha256"]:
            bad.append(row["bundle"])
        if args.all:
            with zipfile.ZipFile(path) as archive:
                member = archive.testzip()
                if member:
                    bad.append(f"{row['bundle']}:{member}")
    assert not missing, missing
    assert not bad, bad

    current_bundle_name = f"{current_artifact}.zip"
    assert any(row["bundle"] == current_bundle_name for row in index)
    assert (ROOT / "state/PATCH_BASE.json").exists()
    for script in ("check_remote_state.py", "export_patch_series.py"):
        assert (ROOT / "scripts" / script).exists()

    # Run the current artifact's own compact verifier when present.
    verifiers = sorted(expanded.glob("verify_*.py"))
    for verifier in verifiers:
        result = subprocess.run([sys.executable, str(verifier)], cwd=expanded)
        if result.returncode:
            raise SystemExit(result.returncode)

    scientific_slow_files: list[str] = []
    scientific_env = os.environ.copy()
    for variable in (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "BLIS_NUM_THREADS",
    ):
        scientific_env[variable] = "1"
    if args.scientific:
        # Run slow files in fresh processes *before* the aggregate fast lane.
        # The resonant common-measure quadrature can otherwise finish its test
        # body but stall during interpreter teardown after the aggregate suite
        # has initialized several SciPy/BLAS extension modules.  Slow-first
        # ordering plus file isolation preserves identical numerical coverage
        # and gives every expensive process a clean extension-module lifecycle.
        collection = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--collect-only",
                "-q",
                "-m",
                "slow",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=scientific_env,
            timeout=120,
        )
        if collection.returncode:
            sys.stderr.write(collection.stdout)
            sys.stderr.write(collection.stderr)
            raise SystemExit(collection.returncode)
        for line in collection.stdout.splitlines():
            node_id = line.strip()
            if "::" not in node_id:
                continue
            test_file = node_id.split("::", 1)[0]
            if test_file not in scientific_slow_files:
                scientific_slow_files.append(test_file)
        assert scientific_slow_files, "scientific mode found no slow tests"

        for test_file in scientific_slow_files:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "-m",
                    "slow",
                    test_file,
                ],
                cwd=ROOT,
                env=scientific_env,
                timeout=300,
            )
            if result.returncode:
                raise SystemExit(result.returncode)

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-m", "not slow"],
            cwd=ROOT,
            env=scientific_env,
            timeout=300,
        )
        if result.returncode:
            raise SystemExit(result.returncode)
    elif args.all:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-m", "not slow"],
            cwd=ROOT,
        )
        if result.returncode:
            raise SystemExit(result.returncode)

    mode = "scientific" if args.scientific else ("all" if args.all else "quick")
    print(
        json.dumps(
            {
                "status": "PASS",
                "bundle_count": len(index),
                "current_artifact": current_artifact,
                "mode": mode,
                "scientific_slow_file_count": len(scientific_slow_files),
            }
        )
    )


if __name__ == "__main__":
    main()

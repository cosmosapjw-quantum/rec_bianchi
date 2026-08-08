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

from scientific_test_runner import run_scientific, scientific_environment

ROOT = Path(__file__).resolve().parents[1]


def repository_test_environment() -> dict[str, str]:
    """Deterministic one-thread environment for the aggregate fast suite."""
    return scientific_environment(root=ROOT)


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

    policy = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_hyrec_binary_hash_policy.py")],
        cwd=ROOT,
    )
    if policy.returncode:
        raise SystemExit(policy.returncode)

    whitespace_policy = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_commit_range_whitespace.py")],
        cwd=ROOT,
    )
    if whitespace_policy.returncode:
        raise SystemExit(whitespace_policy.returncode)

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
    for script in ("check_remote_state.py", "export_git_bundle_delivery.py"):
        assert (ROOT / "scripts" / script).exists()

    # Run the current artifact's own compact verifier when present.
    verifiers = sorted(expanded.glob("verify_*.py"))
    for verifier in verifiers:
        result = subprocess.run([sys.executable, str(verifier)], cwd=expanded)
        if result.returncode:
            raise SystemExit(result.returncode)

    scientific_slow_files: list[str] = []
    scientific_slow_nodes: list[str] = []
    if args.scientific:
        scientific_result = run_scientific(root=ROOT)
        scientific_slow_files = list(scientific_result.slow_files)
        scientific_slow_nodes = list(scientific_result.slow_nodes)
    elif args.all:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-m", "not slow"],
            cwd=ROOT,
            env=repository_test_environment(),
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
                "scientific_slow_test_count": len(scientific_slow_nodes),
            }
        )
    )


if __name__ == "__main__":
    main()

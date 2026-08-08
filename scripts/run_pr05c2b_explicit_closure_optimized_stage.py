#!/usr/bin/env python3
"""Verify and deterministically repack recovered PR-05C2B/v0.64 evidence.

The expensive nine-lane macro solve and direct COM--KHW selected-pair audit were
completed before a runtime interruption.  Their immutable artifact survived and
is treated as a durable scientific cache.  This script validates every cached
byte, checks the current optimized operator implementation through the compact
artifact verifier, and reproduces the deterministic ZIP without rerunning the
multi-minute cold quadrature lane.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "Full_Bianchi_HyRec_PR05C2B_explicit_closure_optimized_macro_v0_64"
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"
DATA = ROOT / "data" / "pr05c2b_explicit_closure_optimized_v064.npz"
STATUS = (
    "PASS_EXPLICIT_CLOSURE_WITH_UNCERTAINTY_"
    "OPTIMIZED_CANONICAL_MACRO_REFERENCE_PR05C2C_NEXT"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_manifest() -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in (EXPANDED / "MANIFEST_SHA256.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        rows[name] = digest
    return rows


def validate_expanded() -> None:
    manifest = read_manifest()
    for name, digest in manifest.items():
        path = EXPANDED / name
        if not path.is_file() or sha256(path) != digest:
            raise RuntimeError(f"artifact manifest mismatch: {name}")
    metrics = json.loads((EXPANDED / "NUMERICAL_METRICS.json").read_text())
    if metrics.get("status") != STATUS:
        raise RuntimeError("unexpected PR-05C2B status")
    result = subprocess.run(
        [sys.executable, str(EXPANDED / "verify_PR05C2B.py")],
        cwd=EXPANDED,
        check=False,
    )
    if result.returncode:
        raise SystemExit(result.returncode)
    cached = EXPANDED / "pr05c2b_explicit_closure_optimized_v064.npz"
    if not DATA.is_file() or sha256(DATA) != sha256(cached):
        raise RuntimeError("public PR-05C2B NPZ differs from immutable artifact")


def deterministic_zip(source: Path, output: Path) -> None:
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(str(path.relative_to(source)), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cold",
        action="store_true",
        help=(
            "refuse silent cold recomputation: the direct selected-pair and "
            "nine-macro workers require the dedicated PR-05C2C compiler"
        ),
    )
    args = parser.parse_args()
    if args.cold:
        raise SystemExit(
            "Cold direct-network recompilation is intentionally not part of "
            "v0.64 recovery; use docs/PR05C2C_DIRECT_NETWORK_NATIVE_ANGULAR_PLAN.md."
        )
    validate_expanded()
    with tempfile.TemporaryDirectory(prefix="pr05c2b-repack-") as temporary:
        rebuilt = Path(temporary) / BUNDLE.name
        deterministic_zip(EXPANDED, rebuilt)
        if sha256(rebuilt) != sha256(BUNDLE):
            raise RuntimeError("deterministic PR-05C2B bundle reproduction mismatch")
    print(STATUS)
    print(f"artifact_sha256={sha256(BUNDLE)}")
    print(f"data_sha256={sha256(DATA)}")


if __name__ == "__main__":
    main()

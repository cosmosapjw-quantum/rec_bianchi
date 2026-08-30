#!/usr/bin/env python3
"""Fail-closed intake for the REC-LOCAL-01 bootstrap recovery package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath


HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[2]
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
R2_PREFIX = "docs/bootstrap/rec_split_domain_bootstrap_20260829"


def fail(message: str) -> None:
    raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    process = subprocess.run(
        ["git", "--no-replace-objects", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
        check=False,
    )
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        fail("git " + " ".join(args) + ": " + detail)
    if binary:
        return process.stdout
    return process.stdout.decode("utf-8").removesuffix("\n")


def manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="ascii").splitlines(), start=1
    ):
        if not line:
            continue
        try:
            expected, name = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"malformed manifest line {line_number}") from error
        candidate = PurePosixPath(name)
        if (
            not HEX64.fullmatch(expected)
            or candidate.is_absolute()
            or "." in candidate.parts
            or ".." in candidate.parts
            or str(candidate) != name
        ):
            fail(f"unsafe manifest entry: {name}")
        if name in entries:
            fail(f"duplicate manifest entry: {name}")
        entries[name] = expected
    if not entries:
        fail("empty manifest")
    return entries


def require_commit(repo: Path, oid: str, label: str) -> None:
    if not HEX40.fullmatch(oid):
        fail(label + " commit identity is malformed")
    if git(repo, "cat-file", "-t", oid) != "commit":
        fail(label + " commit identity mismatch")
    if git(repo, "rev-parse", "--verify", oid) != oid:
        fail(label + " commit identity mismatch")


def validate_local(root: Path) -> tuple[dict, dict]:
    root = root.resolve()
    entries = manifest(HERE / "MANIFEST.sha256")
    for name, expected in entries.items():
        path = root / name
        if (
            path.is_symlink()
            or not path.is_file()
            or not path.resolve().is_relative_to(root)
        ):
            fail("missing or unsafe delivery path: " + name)
        if digest(path.read_bytes()) != expected:
            fail("delivery digest mismatch: " + name)

    contract = json.loads((HERE / "CONTRACT.json").read_text(encoding="utf-8"))
    forensic = json.loads(
        (HERE / "KNOWN_INVALID_R2.json").read_text(encoding="utf-8")
    )
    if set(entries) != set(contract["delivery_paths"]):
        fail("delivery closure mismatch")
    if contract["claim"] != "NO_PASS_REC_PHYSICAL_SPLIT":
        fail("scientific claim changed")
    if contract["exact_next_action"] != "REC-LOCAL-01_EVIDENCE_ADMISSION":
        fail("next action changed")
    if forensic["classification"] != {
        "object_class": "CLASS_2_DETERMINISTIC_GENERATED_EVIDENCE",
        "status": "PROVENANCE_REBIND_REQUIRED",
        "packaging_validity": "FAIL_STALE_INNER_MANIFEST",
        "continuation_identity_effect": "NONE",
        "scientific_result_validity_effect": "NONE",
    }:
        fail("R2 classification changed")
    return contract, forensic


def validate_live(repo: Path, contract: dict, forensic: dict) -> None:
    repo = Path(git(repo, "rev-parse", "--show-toplevel"))
    rebind = contract["followthrough_rebind"]
    require_commit(repo, rebind["commit"], "followthrough")
    if git(repo, "rev-parse", rebind["commit"] + "^{tree}") != rebind["tree"]:
        fail("followthrough rebind tree mismatch")
    manifest_path = "research/continuation_20260830/MANIFEST.sha256"
    if git(repo, "rev-parse", rebind["commit"] + ":" + manifest_path) != rebind[
        "manifest_blob_sha1"
    ]:
        fail("followthrough manifest blob mismatch")
    rebind_bytes = git(
        repo, "cat-file", "blob", rebind["commit"] + ":" + manifest_path,
        binary=True,
    )
    if digest(rebind_bytes) != rebind["manifest_sha256"]:
        fail("followthrough manifest SHA-256 mismatch")

    source = forensic["source"]
    known = contract["known_invalid_r2"]
    if known["source_commit"] != source["commit"]:
        fail("R2 commit identity mismatch")
    if known["source_tree"] != source["tree"]:
        fail("R2 source tree contract mismatch")
    if known["package_subtree"] != source["package_subtree"]:
        fail("R2 package subtree contract mismatch")
    if known["source_manifest_blob_sha1"] != source["manifest_blob_sha1"]:
        fail("R2 source manifest contract mismatch")
    commit = known["source_commit"]
    require_commit(repo, commit, "R2")
    if git(repo, "rev-parse", commit + "^{tree}") != source["tree"]:
        fail("R2 source tree mismatch")
    if git(repo, "rev-parse", commit + ":" + R2_PREFIX) != source[
        "package_subtree"
    ]:
        fail("R2 package subtree mismatch")
    source_manifest_path = R2_PREFIX + "/MANIFEST.sha256"
    if git(repo, "rev-parse", commit + ":" + source_manifest_path) != source[
        "manifest_blob_sha1"
    ]:
        fail("R2 source manifest blob mismatch")
    source_manifest = git(
        repo, "cat-file", "blob", commit + ":" + source_manifest_path,
        binary=True,
    )
    if digest(source_manifest) != source["manifest_sha256"]:
        fail("R2 source manifest SHA-256 mismatch")

    source_entries = manifest_bytes(source_manifest)
    stale = {}
    for name, expected in source_entries.items():
        actual_bytes = git(
            repo, "cat-file", "blob", commit + ":" + R2_PREFIX + "/" + name,
            binary=True,
        )
        actual = digest(actual_bytes)
        if actual != expected:
            stale[name] = {"manifest_sha256": expected, "actual_sha256": actual}
    declared = {
        name: {
            "manifest_sha256": item["manifest_sha256"],
            "actual_sha256": item["actual_sha256"],
        }
        for name, item in forensic["mismatches"].items()
    }
    if stale != declared:
        fail("R2 mismatch set differs from forensic record")

    rebound = manifest(HERE / "R2_REBOUND_MANIFEST.sha256")
    if set(rebound) != set(source_entries):
        fail("R2 sidecar closure mismatch")
    for name, expected in rebound.items():
        actual = digest(
            git(
                repo,
                "cat-file",
                "blob",
                commit + ":" + R2_PREFIX + "/" + name,
                binary=True,
            )
        )
        if actual != expected:
            fail("R2 sidecar digest mismatch: " + name)


def manifest_bytes(data: bytes) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in data.decode("ascii").splitlines():
        if line:
            expected, name = line.split(maxsplit=1)
            entries[name] = expected
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--repo", type=Path)
    arguments = parser.parse_args()
    contract, forensic = validate_local(arguments.root)
    rebind = "NOT_RUN"
    if arguments.repo is not None:
        validate_live(arguments.repo, contract, forensic)
        rebind = "PASS_EXACT_PREIMAGE_SIDECAR"
    print(
        json.dumps(
            {
                "claim": contract["claim"],
                "files": len(contract["delivery_paths"]),
                "next": contract["exact_next_action"],
                "r2_rebind": rebind,
                "status": "PASS_RECOVERY_PACKAGE_INTAKE_ONLY",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, UnicodeError, ValueError, subprocess.SubprocessError) as error:
        parser = argparse.ArgumentParser()
        parser.exit(2, "FAIL_RECOVERY_PACKAGE: " + str(error) + "\n")

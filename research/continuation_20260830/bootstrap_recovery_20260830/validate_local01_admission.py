#!/usr/bin/env python3
"""Admit preserved REC-LOCAL-01 evidence without rerunning or rewriting it."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath


HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
EXPECTED_EVIDENCE = {
    "canonical_context_restart_passed": 9,
    "component_context_deposition_passed": 27,
    "affected_restart_selectors_passed": 2,
    "affected_restart_selectors_deselected": 8,
    "component_mutants_detected": 4,
    "component_mutant_assertion_failures_each": 1,
    "component_mutant_collection_errors_each": 0,
    "rehashed_context_mutations_detected": 8,
    "all_rejected_before_parent_restore": True,
}
EXPECTED_ENVIRONMENT = {
    "python": "3.12.3",
    "numpy": "2.4.2",
    "scipy": "1.17.0",
    "pytest": "9.1.1",
}
EXPECTED_RECOVERY = {
    "original_status": "STOP_INVALID",
    "classification": "HISTORICAL_R2_PACKAGING_REPRODUCIBILITY_FAILURE",
    "r2_sidecar_rebind": "PASS",
    "followthrough_rebind": "PASS",
}


def fail(message: str) -> None:
    raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", "--no-replace-objects", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
        check=False,
    )
    if process.returncode:
        fail("git " + " ".join(args) + ": " + process.stderr.strip())
    return process.stdout.removesuffix("\n")


def require_file(path: Path, label: str) -> Path:
    path = path.resolve()
    if path.is_symlink() or not path.is_file():
        fail(label + " is missing or unsafe")
    return path


def safe_relative(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if (
        not name
        or path.is_absolute()
        or "." in path.parts
        or ".." in path.parts
        or str(path) != name
    ):
        fail("unsafe copied evidence path: " + name)
    return path


def validate(arguments: argparse.Namespace) -> dict[str, object]:
    admission_path = require_file(arguments.admission, "admission")
    receipt = require_file(arguments.receipt, "source receipt")
    inventory = require_file(arguments.inventory, "preservation inventory")
    evidence_root = arguments.evidence_root.resolve()
    source_worktree = arguments.source_worktree.resolve()
    if not evidence_root.is_dir() or evidence_root.is_symlink():
        fail("evidence root is missing or unsafe")
    if not source_worktree.is_dir() or source_worktree.is_symlink():
        fail("source worktree is missing or unsafe")

    admission = json.loads(admission_path.read_text(encoding="utf-8"))
    if "__REQUIRED" in json.dumps(admission, sort_keys=True):
        fail("admission still contains template placeholders")
    if admission.get("schema") != "rec-local01-canonical-context-admission/v1":
        fail("admission schema mismatch")
    if admission.get("status") != (
        "PASS_REC_LOCAL01_EVIDENCE_ADMITTED_NOT_PHYSICAL_SPLIT"
    ):
        fail("admission status mismatch")
    if admission.get("claim") != "NO_PASS_REC_PHYSICAL_SPLIT":
        fail("scientific claim changed")
    if admission.get("next") != (
        "REC-LOCAL-02_SOURCE_BOUND_PHYSICAL_DEPOSITION_AND_FULL_JVP"
    ):
        fail("next action changed")

    source_receipt = admission["source_receipt"]
    if source_receipt.get("absolute_path") != str(receipt):
        fail("source receipt path mismatch")
    if not HEX64.fullmatch(str(source_receipt.get("sha256", ""))):
        fail("source receipt digest is malformed")
    if sha256(receipt) != source_receipt["sha256"]:
        fail("source receipt digest mismatch")

    source = admission["source_worktree"]
    if source.get("absolute_path") != str(source_worktree):
        fail("source worktree path mismatch")
    if not HEX40.fullmatch(str(source.get("head", ""))) or not HEX40.fullmatch(
        str(source.get("tree", ""))
    ):
        fail("source worktree Git identity is malformed")
    if git(source_worktree, "rev-parse", "HEAD") != source["head"]:
        fail("source worktree HEAD mismatch")
    if git(source_worktree, "rev-parse", "HEAD^{tree}") != source["tree"]:
        fail("source worktree tree mismatch")
    if git(source_worktree, "branch", "--show-current") != source["branch"]:
        fail("source worktree branch mismatch")
    if not HEX64.fullmatch(str(source.get("preservation_inventory_sha256", ""))):
        fail("preservation inventory digest is malformed")
    if sha256(inventory) != source["preservation_inventory_sha256"]:
        fail("preservation inventory digest mismatch")

    evidence = admission["evidence"]
    copied = evidence.get("copied_paths")
    copied_hashes = evidence.get("copied_path_sha256")
    if not isinstance(copied, list) or len(copied) != 6 or len(set(copied)) != 6:
        fail("exactly six unique evidence paths are required")
    if not isinstance(copied_hashes, dict) or set(copied_hashes) != set(copied):
        fail("copied evidence hash closure mismatch")
    receipt_copies = 0
    for name in copied:
        relative = safe_relative(name)
        expected = copied_hashes[name]
        if not HEX64.fullmatch(str(expected)):
            fail("copied evidence digest is malformed: " + name)
        path = evidence_root / relative
        if (
            path.is_symlink()
            or not path.is_file()
            or not path.resolve().is_relative_to(evidence_root)
        ):
            fail("copied evidence is missing or unsafe: " + name)
        actual = sha256(path)
        if actual != expected:
            fail("copied evidence digest mismatch: " + name)
        if actual == source_receipt["sha256"]:
            receipt_copies += 1
    if receipt_copies != 1:
        fail("exactly one copied receipt preimage is required")

    for key, expected in EXPECTED_EVIDENCE.items():
        if evidence.get(key) != expected:
            fail("local01 evidence count mismatch: " + key)
    if admission.get("environment") != EXPECTED_ENVIRONMENT:
        fail("local01 environment mismatch")
    if admission.get("bootstrap_recovery") != EXPECTED_RECOVERY:
        fail("bootstrap recovery disposition mismatch")

    return {
        "claim": admission["claim"],
        "evidence_files": len(copied),
        "next": admission["next"],
        "status": admission["status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--source-worktree", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(validate(arguments), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, TypeError, UnicodeError, ValueError) as error:
        parser = argparse.ArgumentParser()
        parser.exit(2, "FAIL_LOCAL01_ADMISSION: " + str(error) + "\n")

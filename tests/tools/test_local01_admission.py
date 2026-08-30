from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]
VALIDATOR = (
    REPOSITORY
    / "research"
    / "continuation_20260830"
    / "bootstrap_recovery_20260830"
    / "validate_local01_admission.py"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(tmp_path: Path) -> tuple[list[str], Path]:
    source = tmp_path / "preserved-local01"
    source.mkdir()
    subprocess.run(
        ["git", "init", "-qb", "local01-fixture"], cwd=source, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "local01@example.invalid"],
        cwd=source,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "local01 fixture"],
        cwd=source,
        check=True,
    )
    (source / "tracked.txt").write_text("preserved\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=source, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=source, check=True)
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source, text=True
    ).strip()
    tree = subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=source, text=True
    ).strip()

    receipt = source / "REC_LOCAL_01_CANONICAL_CONTEXT_INTEGRATION.json"
    receipt.write_text('{"status":"STOP_INVALID"}\n', encoding="utf-8")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    paths = ["receipt.json", *(f"mutation_{index}.json" for index in range(1, 6))]
    (evidence / paths[0]).write_bytes(receipt.read_bytes())
    for index, name in enumerate(paths[1:], start=1):
        (evidence / name).write_text(
            json.dumps({"mutant": index}) + "\n", encoding="utf-8"
        )

    inventory = tmp_path / "preservation_inventory.txt"
    inventory.write_text("read-only inventory\n", encoding="utf-8")
    admission = {
        "schema": "rec-local01-canonical-context-admission/v1",
        "status": "PASS_REC_LOCAL01_EVIDENCE_ADMITTED_NOT_PHYSICAL_SPLIT",
        "source_receipt": {
            "absolute_path": str(receipt.resolve()),
            "sha256": sha256(receipt),
        },
        "source_worktree": {
            "absolute_path": str(source.resolve()),
            "branch": "local01-fixture",
            "head": head,
            "tree": tree,
            "preservation_inventory_sha256": sha256(inventory),
        },
        "evidence": {
            "copied_paths": paths,
            "copied_path_sha256": {
                name: sha256(evidence / name) for name in paths
            },
            "canonical_context_restart_passed": 9,
            "component_context_deposition_passed": 27,
            "affected_restart_selectors_passed": 2,
            "affected_restart_selectors_deselected": 8,
            "component_mutants_detected": 4,
            "component_mutant_assertion_failures_each": 1,
            "component_mutant_collection_errors_each": 0,
            "rehashed_context_mutations_detected": 8,
            "all_rejected_before_parent_restore": True,
        },
        "environment": {
            "python": "3.12.3",
            "numpy": "2.4.2",
            "scipy": "1.17.0",
            "pytest": "9.1.1",
        },
        "bootstrap_recovery": {
            "original_status": "STOP_INVALID",
            "classification": "HISTORICAL_R2_PACKAGING_REPRODUCIBILITY_FAILURE",
            "r2_sidecar_rebind": "PASS",
            "followthrough_rebind": "PASS",
        },
        "claim": "NO_PASS_REC_PHYSICAL_SPLIT",
        "next": "REC-LOCAL-02_SOURCE_BOUND_PHYSICAL_DEPOSITION_AND_FULL_JVP",
    }
    admission_path = tmp_path / "admission.json"
    admission_path.write_text(
        json.dumps(admission, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    command = [
        sys.executable,
        str(VALIDATOR),
        "--admission",
        str(admission_path),
        "--receipt",
        str(receipt),
        "--evidence-root",
        str(evidence),
        "--inventory",
        str(inventory),
        "--source-worktree",
        str(source),
    ]
    return command, receipt


def test_admission_binds_receipt_copies_inventory_and_preserved_worktree(
    tmp_path: Path,
) -> None:
    command, _ = fixture(tmp_path)

    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "claim": "NO_PASS_REC_PHYSICAL_SPLIT",
        "evidence_files": 6,
        "next": "REC-LOCAL-02_SOURCE_BOUND_PHYSICAL_DEPOSITION_AND_FULL_JVP",
        "status": "PASS_REC_LOCAL01_EVIDENCE_ADMITTED_NOT_PHYSICAL_SPLIT",
    }


def test_admission_rejects_receipt_bytes_changed_after_inventory(
    tmp_path: Path,
) -> None:
    command, receipt = fixture(tmp_path)
    receipt.write_text('{"status":"changed"}\n', encoding="utf-8")

    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 2
    assert "source receipt digest mismatch" in result.stderr

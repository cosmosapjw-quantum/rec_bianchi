from __future__ import annotations

import json
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPOSITORY = Path(__file__).resolve().parents[2]
PACKAGE = (
    REPOSITORY
    / "research"
    / "continuation_20260830"
    / "bootstrap_recovery_20260830"
)


def rewrite_manifest_digest(root: Path, relative_name: str) -> None:
    manifest = root / PACKAGE.relative_to(REPOSITORY) / "MANIFEST.sha256"
    target = root / relative_name
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    lines = manifest.read_text(encoding="ascii").splitlines()
    suffix = "  " + relative_name
    replaced = [
        digest + suffix if line.endswith(suffix) else line for line in lines
    ]
    assert replaced != lines
    manifest.write_text("\n".join(replaced) + "\n", encoding="ascii")


def copied_package_root(tmp_path: Path) -> Path:
    root = tmp_path / "root"
    target = root / PACKAGE.relative_to(REPOSITORY)
    target.parent.mkdir(parents=True)
    shutil.copytree(PACKAGE, target)
    return root


def run_copied_validator(root: Path) -> subprocess.CompletedProcess[str]:
    validator = root / PACKAGE.relative_to(REPOSITORY) / "validate_package.py"
    return subprocess.run(
        [
            sys.executable,
            str(validator),
            "--root",
            str(root),
            "--repo",
            str(REPOSITORY),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_recovery_package_rebinds_r2_without_promoting_the_scientific_claim() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PACKAGE / "validate_package.py"),
            "--root",
            str(REPOSITORY),
            "--repo",
            str(REPOSITORY),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {
        "claim": "NO_PASS_REC_PHYSICAL_SPLIT",
        "files": 11,
        "next": "REC-LOCAL-01_EVIDENCE_ADMISSION",
        "r2_rebind": "PASS_EXACT_PREIMAGE_SIDECAR",
        "status": "PASS_RECOVERY_PACKAGE_INTAKE_ONLY",
    }


def test_fetch_and_validate_runs_only_read_only_package_gates() -> None:
    result = subprocess.run(
        [
            "bash",
            str(PACKAGE / "FETCH_AND_VALIDATE.sh"),
            "--repo",
            str(REPOSITORY),
        ],
        cwd=REPOSITORY,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    lines = [json.loads(line) for line in result.stdout.splitlines()]
    assert [line["status"] for line in lines] == [
        "PASS_DELIVERY_INTAKE_ONLY",
        "PASS_RECOVERY_PACKAGE_INTAKE_ONLY",
    ]
    final_line = lines[-1]
    assert final_line["status"] == "PASS_RECOVERY_PACKAGE_INTAKE_ONLY"
    assert final_line["claim"] == "NO_PASS_REC_PHYSICAL_SPLIT"


@pytest.mark.parametrize("section", ["followthrough_rebind", "known_invalid_r2"])
def test_live_validation_rejects_a_tree_oid_substituted_for_a_commit(
    tmp_path: Path, section: str
) -> None:
    root = copied_package_root(tmp_path)
    contract_path = root / PACKAGE.relative_to(REPOSITORY) / "CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if section == "followthrough_rebind":
        contract[section]["commit"] = contract[section]["tree"]
    else:
        contract[section]["source_commit"] = contract[section]["source_tree"]
    contract_path.write_text(
        json.dumps(contract, indent=2) + "\n", encoding="utf-8"
    )
    rewrite_manifest_digest(
        root,
        "research/continuation_20260830/bootstrap_recovery_20260830/CONTRACT.json",
    )

    result = run_copied_validator(root)

    assert result.returncode == 2
    assert "commit identity mismatch" in result.stderr


def test_live_validation_rejects_a_sidecar_with_a_deleted_member(
    tmp_path: Path,
) -> None:
    root = copied_package_root(tmp_path)
    sidecar_relative = (
        "research/continuation_20260830/bootstrap_recovery_20260830/"
        "R2_REBOUND_MANIFEST.sha256"
    )
    sidecar = root / sidecar_relative
    lines = sidecar.read_text(encoding="ascii").splitlines()
    sidecar.write_text("\n".join(lines[:-1]) + "\n", encoding="ascii")
    rewrite_manifest_digest(root, sidecar_relative)

    result = run_copied_validator(root)

    assert result.returncode == 2
    assert "R2 sidecar closure mismatch" in result.stderr


def test_live_validation_rejects_a_wrong_followthrough_tree(tmp_path: Path) -> None:
    root = copied_package_root(tmp_path)
    contract_path = root / PACKAGE.relative_to(REPOSITORY) / "CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract["followthrough_rebind"]["tree"] = "0" * 40
    contract_path.write_text(
        json.dumps(contract, indent=2) + "\n", encoding="utf-8"
    )
    rewrite_manifest_digest(
        root,
        "research/continuation_20260830/bootstrap_recovery_20260830/CONTRACT.json",
    )

    result = run_copied_validator(root)

    assert result.returncode == 2
    assert "followthrough rebind tree mismatch" in result.stderr


def test_live_validation_rejects_a_changed_sidecar_digest(tmp_path: Path) -> None:
    root = copied_package_root(tmp_path)
    sidecar_relative = (
        "research/continuation_20260830/bootstrap_recovery_20260830/"
        "R2_REBOUND_MANIFEST.sha256"
    )
    sidecar = root / sidecar_relative
    lines = sidecar.read_text(encoding="ascii").splitlines()
    replacement = ("0" if lines[0][0] != "0" else "1") + lines[0][1:]
    sidecar.write_text(
        "\n".join([replacement, *lines[1:]]) + "\n", encoding="ascii"
    )
    rewrite_manifest_digest(root, sidecar_relative)

    result = run_copied_validator(root)

    assert result.returncode == 2
    assert "R2 sidecar digest mismatch: PACKAGE.json" in result.stderr

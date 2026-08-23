#!/usr/bin/env python3
"""Build the complete external-audit artifact bundle without running tests."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
).resolve()
BUNDLE_ROOT = REPO_ROOT / "docs/audit/external_audit_bundle"
RECORDS_ROOT = BUNDLE_ROOT / "research_records"
INPUTS_ROOT = BUNDLE_ROOT / "provenance_inputs"
ARCHIVES_ROOT = BUNDLE_ROOT / "harness_run_archives"
MANIFEST_PATH = BUNDLE_ROOT / "RESEARCH_ARTIFACT_MANIFEST.json"

TARGET_BRANCH = "audit/ode-four-loop-external-audit-20260823"

RESEARCH_RECORDS = (
    ("/tmp/rec_bianchi_stiff_dae_research.md", "GENERATED_RESEARCH_OUTPUT"),
    ("/tmp/rec_bianchi_physics_research_record.md", "GENERATED_RESEARCH_OUTPUT"),
    ("/tmp/rec_bianchi_independent_numerical_research.md", "GENERATED_RESEARCH_OUTPUT"),
    ("/tmp/rec_bianchi_physseed_research_record.md", "GENERATED_RESEARCH_OUTPUT"),
    ("/tmp/rec_bianchi_coding_harness_probes.py", "GENERATED_RESEARCH_OUTPUT"),
    ("/tmp/rec_bianchi_seed_inventory.py", "GENERATED_RESEARCH_OUTPUT"),
    ("/tmp/rec_bianchi_algoseed_coding_research_record.md", "GENERATED_RESEARCH_OUTPUT"),
    (
        "/tmp/rec_bianchi_algorithm_independent_review_receipt.md",
        "GENERATED_RESEARCH_OUTPUT",
    ),
    ("/tmp/apply_patch_append_probe.txt", "UNCERTAIN_NONAUTHORITATIVE"),
)

PROVENANCE_INPUTS = (
    "/home/cosmosapjw/Dropbox/physmath-research-harness-gpt56.zip",
    "/home/cosmosapjw/Dropbox/physmath-coding-harness-gpt56.zip",
)

HARNESS_WORKSPACES = (
    ("/tmp/physmath-harness.UV5aHJBT", "GENERATED_HARNESS_WORKSPACE"),
    ("/tmp/physmath-coding-harness.7QK1j2WY", "GENERATED_HARNESS_WORKSPACE"),
    ("/tmp/physmath-research-harness.Y0fN2j", "UNCERTAIN_UNTOUCHED_EXTRACTION"),
    ("/tmp/physmath-coding-harness.QjZLaE", "UNCERTAIN_UNTOUCHED_EXTRACTION"),
)

REPOSITORY_PAYLOAD = (
    "src/full_bianchi_hyrec/recoil/nonlinear_bose_release.py",
    "src/full_bianchi_hyrec/recoil/nonlinear_bose_runtime.py",
    "src/full_bianchi_hyrec/trajectory/adaptive_macro.py",
    "src/full_bianchi_hyrec/trajectory/causal_history.py",
    "src/full_bianchi_hyrec/trajectory/characteristic_angular.py",
    "src/full_bianchi_hyrec/trajectory/pseudotransient_continuation.py",
    "tests/recoil/test_nonlinear_bose_release.py",
    "tests/recoil/test_nonlinear_bose_runtime.py",
    "tests/trajectory/test_adaptive_canonical_macro.py",
    "tests/trajectory/test_causal_characteristic_history.py",
    "tests/trajectory/test_characteristic_angular_solver.py",
    "tests/trajectory/test_full_coupled_transport.py",
    "tests/trajectory/test_pseudotransient_continuation.py",
    "docs/audit/ODE_SOLVER_FOUR_LOOP_FINAL_REPORT_20260823.md",
    "docs/audit/ODE_SOLVER_FOUR_LOOP_RUN_DATA_20260823.json",
    "scripts/run_ode_solver_four_loop_audit.py",
    "docs/audit/external_audit_bundle/build_external_audit_bundle.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_regular_file(path: Path) -> None:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"required regular file is missing or unsafe: {path}")


def file_metadata(path: Path) -> dict[str, Any]:
    require_regular_file(path)
    stat = path.stat()
    return {
        "bytes": stat.st_size,
        "mode": oct(stat.st_mode & 0o7777),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "sha256": sha256(path),
    }


def committed_path(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def copy_with_receipt(source_text: str, target_dir: Path, role: str) -> dict[str, Any]:
    source = Path(source_text)
    require_regular_file(source)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    shutil.copy2(source, target)
    source_meta = file_metadata(source)
    target_meta = file_metadata(target)
    if source_meta["bytes"] != target_meta["bytes"] or source_meta["sha256"] != target_meta["sha256"]:
        raise RuntimeError(f"copy verification failed: {source} -> {target}")
    return {
        "classification": role,
        "original_path": str(source),
        "committed_path": committed_path(target),
        **target_meta,
    }


def iter_workspace_entries(source: Path) -> list[Path]:
    entries: list[Path] = []
    for root, dirnames, filenames in os.walk(source, followlinks=False):
        dirnames.sort()
        filenames.sort()
        root_path = Path(root)
        entries.extend(root_path / name for name in dirnames)
        entries.extend(root_path / name for name in filenames)
    return sorted(entries, key=lambda path: path.relative_to(source).as_posix())


def archive_workspace(source_text: str, classification: str) -> dict[str, Any]:
    source = Path(source_text)
    if not source.is_dir() or source.is_symlink():
        raise RuntimeError(f"required workspace is missing or unsafe: {source}")
    ARCHIVES_ROOT.mkdir(parents=True, exist_ok=True)
    archive = ARCHIVES_ROOT / f"{source.name}.tar"
    entries = iter_workspace_entries(source)
    member_receipts: list[dict[str, Any]] = []
    with tarfile.open(archive, "w", format=tarfile.PAX_FORMAT) as handle:
        handle.add(source, arcname=source.name, recursive=False)
        for path in entries:
            relative = path.relative_to(source)
            archive_name = (Path(source.name) / relative).as_posix()
            if path.is_symlink():
                member_receipts.append(
                    {
                        "archive_member": archive_name,
                        "kind": "symlink",
                        "link_target": os.readlink(path),
                    }
                )
            elif path.is_dir():
                member_receipts.append(
                    {"archive_member": archive_name, "kind": "directory"}
                )
            elif path.is_file():
                member_receipts.append(
                    {
                        "archive_member": archive_name,
                        "kind": "file",
                        **file_metadata(path),
                    }
                )
            else:
                raise RuntimeError(f"unsupported workspace entry: {path}")
            handle.add(path, arcname=archive_name, recursive=False)

    expected_names = {source.name} | {
        (Path(source.name) / path.relative_to(source)).as_posix() for path in entries
    }
    with tarfile.open(archive, "r") as handle:
        archived_names = {member.name.rstrip("/") for member in handle.getmembers()}
    if archived_names != expected_names:
        missing = sorted(expected_names - archived_names)
        extra = sorted(archived_names - expected_names)
        raise RuntimeError(f"archive inventory mismatch for {source}: missing={missing}, extra={extra}")

    file_count = sum(item["kind"] == "file" for item in member_receipts)
    symlink_count = sum(item["kind"] == "symlink" for item in member_receipts)
    return {
        "classification": classification,
        "original_path": str(source),
        "committed_path": committed_path(archive),
        "archive_format": "uncompressed POSIX pax tar",
        "archive_root": source.name,
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": sha256(archive),
        "file_count": file_count,
        "directory_count": sum(item["kind"] == "directory" for item in member_receipts),
        "symlink_count": symlink_count,
        "members": member_receipts,
    }


def ignored_artifacts() -> list[dict[str, Any]]:
    raw = subprocess.check_output(
        ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z"],
        cwd=REPO_ROOT,
    )
    paths = sorted(item.decode() for item in raw.split(b"\0") if item)
    receipts: list[dict[str, Any]] = []
    for relative in paths:
        path = REPO_ROOT / relative
        require_regular_file(path)
        receipts.append(
            {
                "classification": "GENERATED_RUNTIME_RECEIPT_OR_CACHE",
                "committed_path": relative,
                **file_metadata(path),
            }
        )
    return receipts


def repository_payload() -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for relative in REPOSITORY_PAYLOAD:
        path = REPO_ROOT / relative
        receipts.append(
            {
                "classification": "IMPLEMENTATION_OR_AUDIT_PAYLOAD",
                "committed_path": relative,
                **file_metadata(path),
            }
        )
    return receipts


def main() -> None:
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=REPO_ROOT, text=True
    ).strip()
    if branch != TARGET_BRANCH:
        raise RuntimeError(f"wrong branch: expected {TARGET_BRANCH}, found {branch}")

    for directory in (RECORDS_ROOT, INPUTS_ROOT, ARCHIVES_ROOT):
        directory.mkdir(parents=True, exist_ok=True)

    records = [
        copy_with_receipt(source, RECORDS_ROOT, classification)
        for source, classification in RESEARCH_RECORDS
    ]
    inputs = [
        copy_with_receipt(source, INPUTS_ROOT, "USER_INPUT_PROVENANCE")
        for source in PROVENANCE_INPUTS
    ]
    workspaces = [
        archive_workspace(source, classification)
        for source, classification in HARNESS_WORKSPACES
    ]
    ignored = ignored_artifacts()
    payload = repository_payload()

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "manifest_scope": "rec_bianchi ODE-solver four-loop external-audit handoff",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git": {
            "target_branch": TARGET_BRANCH,
            "pre_handoff_head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
            ).strip(),
            "pre_handoff_tree": subprocess.check_output(
                ["git", "rev-parse", "HEAD^{tree}"], cwd=REPO_ROOT, text=True
            ).strip(),
        },
        "claim_boundaries": {
            "tests_during_packaging": "NOT_RUN_BY_EXPLICIT_USER_INSTRUCTION",
            "prior_local_audit": "PASS; see docs/audit/ODE_SOLVER_FOUR_LOOP_RUN_DATA_20260823.json",
            "independent_review_verdict": "REWORK; preserved from the preceding independent review",
            "review_gate": "PENDING_EXTERNAL_REVIEW",
            "scientific_and_program_status": "HOLD",
        },
        "research_records": records,
        "harness_workspaces": workspaces,
        "provenance_inputs": inputs,
        "repository_payload": payload,
        "ignored_runtime_artifacts": ignored,
        "summary": {
            "authoritative_research_record_count": sum(
                item["classification"] == "GENERATED_RESEARCH_OUTPUT" for item in records
            ),
            "uncertain_loose_tmp_count": sum(
                item["classification"] == "UNCERTAIN_NONAUTHORITATIVE" for item in records
            ),
            "harness_workspace_count": len(workspaces),
            "harness_member_file_count": sum(item["file_count"] for item in workspaces),
            "provenance_input_count": len(inputs),
            "repository_payload_count_excluding_manifest": len(payload),
            "ignored_artifact_count": len(ignored),
            "ignored_artifact_bytes": sum(item["bytes"] for item in ignored),
        },
        "explicit_exclusions": [
            {
                "classification": "PREEXISTING_OR_UNRELATED",
                "paths": [
                    "/tmp/physmit_inventory_check.txt",
                    "/tmp/mac-math-findings.tsv",
                    "/tmp/mac-algo-findings.tsv",
                    "/tmp/mac-code-remedies.tsv",
                    "/tmp/rabbit-*",
                    "/tmp/rei-*",
                    "/tmp/pytest-of-cosmosapjw/",
                    "/tmp/hook_outputs/",
                ],
                "reason": "Mechanically inspected as other-project or framework runtime material, not generated by the rec_bianchi four-loop research.",
            },
            {
                "classification": "EPHEMERAL_GOVERNANCE_NOT_RESEARCH_OUTPUT",
                "paths": ["/tmp/rec_bianchi_external_audit_push_contract.json"],
                "reason": "Bounded-work control file; deleted after closeout and deliberately not committed.",
            },
            {
                "classification": "DELETED_UNRECOVERABLE",
                "paths": ["/tmp/rec_bianchi_four_loop_impl_contract.json"],
                "reason": "Prior ephemeral bounded-work contract was already deleted before this packaging turn and is not reconstructed.",
            },
        ],
        "manifest_self_reference": {
            "committed_path": committed_path(MANIFEST_PATH),
            "note": "The manifest cannot contain its own SHA-256 without recursion; its committed Git blob and commit tree provide the immutable self-identity after commit.",
        },
        "completeness_ceiling": [
            "Deleted or automatically cleaned temporary files cannot be recovered from the live filesystem.",
            "Terminal stdout and subagent messages that were never persisted as files cannot be attached as standalone raw files.",
            "Shared /tmp provenance cannot be proven from filename alone; all plausible rec_bianchi items were included, with uncertain items explicitly classified.",
            "Harness workspaces are attached as complete tar archives; every live member is enumerated and hashed above.",
        ],
    }

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_manifest = MANIFEST_PATH.with_suffix(".json.tmp")
    temporary_manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_manifest, MANIFEST_PATH)
    print(
        json.dumps(
            {
                "manifest": committed_path(MANIFEST_PATH),
                "manifest_bytes": MANIFEST_PATH.stat().st_size,
                "manifest_sha256": sha256(MANIFEST_PATH),
                "summary": manifest["summary"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

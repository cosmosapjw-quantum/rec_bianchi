#!/usr/bin/env python3
"""Provision the exact nonauthoritative REC-NEXT-03 Lean/xAct inputs.

This is an explicitly network-enabled *setup* phase for a local Codex job,
not a formal-evidence execution.  It writes only to a caller-selected path
outside every Git worktree.  The later ``run_rec_next03_formal_contracts.py
--run-all`` command remains network-isolated and refuses to resolve or update
dependencies.

The provisioner deliberately uses an already-installed ``elan`` launcher to
install exactly ``leanprover/lean4:v4.33.0`` into its own ELAN_HOME, then runs
``lake update`` only in a newly created external workspace copied from the
checked-in REC-NEXT-03 Lean sources.  It verifies the resolved mathlib commit,
clean checkout, canonical origin, xAct archive seal, and source-byte identity
before publishing a setup receipt.  It never writes under the repository,
never alters a PR, and never changes any scientific authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Mapping, Sequence

from run_rec_next03_formal_contracts import (
    FORMAL_ROOT,
    MATHLIB_COMMIT,
    MATHLIB_GIT_URL,
    MATHLIB_TAG,
    REPOSITORY_ROOT,
    XACT_ARCHIVE_SHA256,
    _git_container,
    _is_within,
    _lakefile_mathlib_requirement,
    _lean_source_identity,
    _load_json_text,
    _manifest_mathlib_entry,
    _workspace_symlink_errors,
)


SCHEMA = "rec-next03-formal-provision/v1"
AUTHORITY = "NONAUTHORITATIVE_TOOLCHAIN_PROVISION"
LEAN_TOOLCHAIN = "leanprover/lean4:v4.33.0"


class ProvisionError(ValueError):
    """Raised when a bounded provisioning contract fails closed."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True) + "\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise ProvisionError(f"refusing to overwrite temporary receipt: {temporary}")
    temporary.write_text(_canonical_json(value), encoding="ascii")
    os.replace(temporary, path)


def _require_external_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if _is_within(root, REPOSITORY_ROOT):
        raise ProvisionError("--toolchain-root must be outside the repository worktree")
    container = _git_container(root)
    if container is not None:
        raise ProvisionError(f"--toolchain-root must be outside every Git worktree: {container}")
    return root


def _run(
    *, label: str, command: Sequence[str], cwd: Path, env: Mapping[str, str], logs_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    logs_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = logs_dir / f"{label}.stdout.log"
    stderr_path = logs_dir / f"{label}.stderr.log"
    if stdout_path.exists() or stderr_path.exists():
        raise ProvisionError(f"provision log already exists for {label!r}")
    try:
        completed = subprocess.run(
            list(command), cwd=cwd, env=dict(env), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout_seconds, check=False,
        )
        exit_code: int | None = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        exit_code = None
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        timed_out = True
    except OSError as exc:
        exit_code = 127
        stdout = b""
        stderr = str(exc).encode("utf-8", errors="replace")
        timed_out = False
    stdout_path.write_bytes(stdout)
    stderr_path.write_bytes(stderr)
    return {
        "command": list(command),
        "exit_code": exit_code,
        "stderr_log": stderr_path.relative_to(logs_dir.parent).as_posix(),
        "stdout_log": stdout_path.relative_to(logs_dir.parent).as_posix(),
        "timed_out": timed_out,
    }


def _read_stdout(step: Mapping[str, Any], logs_dir: Path) -> str:
    relative = step.get("stdout_log")
    if not isinstance(relative, str):
        return ""
    try:
        return (logs_dir.parent / relative).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _exact_executable_from_stdout(step: Mapping[str, Any], logs_dir: Path, *, label: str) -> Path:
    if step.get("exit_code") != 0 or step.get("timed_out"):
        raise ProvisionError(f"{label} did not resolve successfully")
    lines = [line.strip() for line in _read_stdout(step, logs_dir).splitlines() if line.strip()]
    if len(lines) != 1:
        raise ProvisionError(f"{label} must emit exactly one executable path")
    executable = Path(lines[0]).resolve()
    if not executable.is_file():
        raise ProvisionError(f"{label} resolved a non-file: {executable}")
    return executable


def _xact_archive_identity(raw: str) -> dict[str, Any]:
    archive = Path(raw).expanduser().resolve()
    if not archive.is_file():
        raise ProvisionError("--xact-archive must identify a regular file")
    observed = _sha256(archive)
    if observed != XACT_ARCHIVE_SHA256:
        raise ProvisionError("xAct archive SHA-256 does not match the exact lock")
    return {"path": str(archive), "sha256": observed, "verified": True}


def _workspace_validation(workspace: Path) -> dict[str, Any]:
    expected_identity = _lean_source_identity(FORMAL_ROOT / "lean")
    actual_identity = _lean_source_identity(workspace)
    errors: list[str] = []
    if expected_identity is None or actual_identity != expected_identity:
        errors.append("checked-in and provisioned Lean source bytes differ")
    errors.extend(_workspace_symlink_errors(workspace))
    manifest_path = workspace / "lake-manifest.json"
    mathlib = workspace / ".lake" / "packages" / "mathlib"
    manifest_entry: dict[str, Any] | None = None
    if not manifest_path.is_file() or not mathlib.is_dir():
        errors.append("workspace lacks lake-manifest.json or materialized mathlib checkout")
    else:
        try:
            manifest_payload = _load_json_text(
                manifest_path.read_text(encoding="utf-8"), source=str(manifest_path)
            )
            manifest_entry, manifest_error = _manifest_mathlib_entry(manifest_payload)
            lakefile_entry, lakefile_error = _lakefile_mathlib_requirement(
                (workspace / "lakefile.toml").read_text(encoding="utf-8")
            )
            if manifest_error:
                errors.append(manifest_error)
            if lakefile_error:
                errors.append(lakefile_error)
            if manifest_entry is None or lakefile_entry is None:
                errors.append("mathlib manifest/lakefile identity did not resolve")
        except (OSError, ValueError) as exc:
            errors.append(f"unable to parse materialized Lake identity: {exc}")
    git_details: dict[str, str | None] = {"head": None, "origin": None, "status": None}
    if mathlib.is_dir():
        for key, command in (
            ("head", ("git", "-C", str(mathlib), "rev-parse", "HEAD")),
            ("origin", ("git", "-C", str(mathlib), "remote", "get-url", "origin")),
            ("status", ("git", "-C", str(mathlib), "status", "--porcelain")),
        ):
            completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if completed.returncode != 0:
                errors.append(f"mathlib Git {key} query failed")
            else:
                git_details[key] = completed.stdout.decode("utf-8", errors="replace").strip()
        if git_details["head"] != MATHLIB_COMMIT:
            errors.append("mathlib HEAD does not match the locked commit")
        if git_details["origin"] != MATHLIB_GIT_URL:
            errors.append("mathlib origin does not match the canonical URL")
        if git_details["status"] != "":
            errors.append("mathlib checkout is not clean")
    return {
        "errors": sorted(set(errors)),
        "lean_source_sha256": actual_identity,
        "manifest_entry": manifest_entry,
        "mathlib_git": git_details,
        "status": "PASS" if not errors else "FAIL",
        "workspace": str(workspace),
    }


def _provision(*, root: Path, xact_archive: str, elan_raw: str | None, timeout_seconds: int) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    logs_dir = root / "provision-logs"
    workspace = root / "lean-workspace"
    staging = root / "lean-workspace.staging"
    if staging.exists() or staging.is_symlink():
        raise ProvisionError("a preserved incomplete staging workspace exists; choose a new toolchain root")
    xact = _xact_archive_identity(xact_archive)
    existing = _workspace_validation(workspace) if workspace.is_dir() else None
    if existing is not None and existing["status"] == "PASS":
        return {
            "admission_allowed": False,
            "authority": AUTHORITY,
            "blockers_resolved": [],
            "mode": "PROVISION",
            "provisioned": False,
            "reason": "existing exact Lean workspace and xAct archive seal already verify",
            "schema": SCHEMA,
            "scientific_claim": "NO_PASS_REC_PHYSICAL_SPLIT",
            "scientific_terminal": "BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
            "status": "PASS",
            "toolchain_root": str(root),
            "workspace": existing,
            "xact_archive": xact,
        }
    if workspace.exists() or workspace.is_symlink():
        raise ProvisionError("existing Lean workspace is not exact; preserve it and choose a new toolchain root")
    elan_candidate = Path(elan_raw).expanduser() if elan_raw else shutil.which("elan")
    if elan_candidate is None:
        raise ProvisionError("ENVIRONMENT_GAP_ELAN_LAUNCHER_NOT_FOUND")
    elan = Path(elan_candidate).resolve()
    if not elan.is_file():
        raise ProvisionError("--elan must identify an executable file")
    env = os.environ.copy()
    env.update(
        {
            "ELAN_HOME": str(root / "elan"),
            "LAKE_ARTIFACT_CACHE": "false",
            "LAKE_NO_CACHE": "1",
            "LAKE_RESTORE_ARTIFACTS": "0",
        }
    )
    source = FORMAL_ROOT / "lean"
    shutil.copytree(source, staging, symlinks=True)
    install_step = _run(
        label="elan-toolchain-install", command=(str(elan), "toolchain", "install", LEAN_TOOLCHAIN),
        cwd=staging, env=env, logs_dir=logs_dir, timeout_seconds=timeout_seconds,
    )
    if install_step["exit_code"] != 0 or install_step["timed_out"]:
        raise ProvisionError("exact Lean toolchain installation failed; inspect preserved provision logs")
    lake_lookup = _run(
        label="elan-which-lake", command=(str(elan), "which", "lake"), cwd=staging,
        env=env, logs_dir=logs_dir, timeout_seconds=timeout_seconds,
    )
    lake = _exact_executable_from_stdout(lake_lookup, logs_dir, label="elan which lake")
    lean_lookup = _run(
        label="elan-which-lean", command=(str(elan), "which", "lean"), cwd=staging,
        env=env, logs_dir=logs_dir, timeout_seconds=timeout_seconds,
    )
    lean = _exact_executable_from_stdout(lean_lookup, logs_dir, label="elan which lean")
    lean_version = _run(
        label="lean-version", command=(str(lean), "--version"), cwd=staging,
        env=env, logs_dir=logs_dir, timeout_seconds=timeout_seconds,
    )
    if lean_version["exit_code"] != 0 or "4.33.0" not in _read_stdout(lean_version, logs_dir):
        raise ProvisionError("installed Lean runtime is not the required 4.33.0 lane")
    update_step = _run(
        label="lake-update", command=(str(lake), "update"), cwd=staging,
        env=env, logs_dir=logs_dir, timeout_seconds=timeout_seconds,
    )
    if update_step["exit_code"] != 0 or update_step["timed_out"]:
        raise ProvisionError("Lake dependency materialization failed; inspect preserved provision logs")
    validation = _workspace_validation(staging)
    if validation["status"] != "PASS":
        raise ProvisionError("materialized Lean workspace failed exact identity validation")
    staging.rename(workspace)
    return {
        "admission_allowed": False,
        "authority": AUTHORITY,
        "blockers_resolved": [],
        "elan": {"executable": str(elan), "home": str(root / "elan")},
        "lean": {"executable": str(lean), "toolchain": LEAN_TOOLCHAIN},
        "mode": "PROVISION",
        "provision_steps": [install_step, lake_lookup, lean_lookup, lean_version, update_step],
        "provisioned": True,
        "schema": SCHEMA,
        "scientific_claim": "NO_PASS_REC_PHYSICAL_SPLIT",
        "scientific_terminal": "BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
        "status": "PASS",
        "toolchain_root": str(root),
        "workspace": _workspace_validation(workspace),
        "xact_archive": xact,
    }


def _plan(root: Path, xact_archive: str, elan_raw: str | None) -> dict[str, Any]:
    return {
        "admission_allowed": False,
        "authority": AUTHORITY,
        "blockers_resolved": [],
        "elan_candidate": str(Path(elan_raw).expanduser()) if elan_raw else shutil.which("elan"),
        "mode": "PLAN",
        "planned_network_operations": [
            f"elan toolchain install {LEAN_TOOLCHAIN}",
            "lake update in a new external lean-workspace only",
        ],
        "repository_mutations": [],
        "schema": SCHEMA,
        "scientific_claim": "NO_PASS_REC_PHYSICAL_SPLIT",
        "scientific_terminal": "BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
        "status": "PLAN_ONLY",
        "toolchain_root": str(root),
        "xact_archive": _xact_archive_identity(xact_archive),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--provision", action="store_true")
    parser.add_argument("--toolchain-root", required=True)
    parser.add_argument("--xact-archive", required=True)
    parser.add_argument("--elan")
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout_seconds <= 0:
        raise SystemExit("--timeout-seconds must be positive")
    try:
        root = _require_external_root(args.toolchain_root)
        if args.plan:
            report = _plan(root, args.xact_archive, args.elan)
        elif args.check:
            report = {
                "admission_allowed": False,
                "authority": AUTHORITY,
                "blockers_resolved": [],
                "mode": "CHECK",
                "schema": SCHEMA,
                "scientific_claim": "NO_PASS_REC_PHYSICAL_SPLIT",
                "scientific_terminal": "BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
                "status": "PASS",
                "toolchain_root": str(root),
                "workspace": _workspace_validation(root / "lean-workspace"),
                "xact_archive": _xact_archive_identity(args.xact_archive),
            }
            if report["workspace"]["status"] != "PASS":
                report["status"] = "ENVIRONMENT_GAP"
        else:
            if not args.allow_network:
                raise ProvisionError("--provision requires explicit --allow-network")
            report = _provision(
                root=root, xact_archive=args.xact_archive, elan_raw=args.elan,
                timeout_seconds=args.timeout_seconds,
            )
        if args.provision and isinstance(report, dict):
            _write_json(root / "provision-receipt.json", report)
    except (OSError, ProvisionError, ValueError) as exc:
        report = {
            "admission_allowed": False,
            "authority": AUTHORITY,
            "blockers_resolved": [],
            "errors": [str(exc)],
            "schema": SCHEMA,
            "scientific_claim": "NO_PASS_REC_PHYSICAL_SPLIT",
            "scientific_terminal": "BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT / SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT",
            "status": "ENVIRONMENT_GAP",
        }
    sys.stdout.write(_canonical_json(report))
    return 0 if report.get("status") in {"PASS", "PLAN_ONLY"} else 69


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed verification for the source-controlled Julia environment.

The byte layer binds Project.toml and Manifest.toml to SHA-256 values in the
REC-NEXT-03 OJI contract.  The semantic layer separately binds the Julia
version, manifest format, project hash, and the UUID/version/git-tree-sha1
triples of the load-bearing direct dependencies.  Keeping both layers means
that rehashing a semantically mutated manifest cannot make it admissible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        value = tomllib.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a TOML table")
    return value


def _manifest_package(
    manifest: dict[str, Any], package: str, errors: list[str]
) -> dict[str, Any] | None:
    deps = manifest.get("deps")
    if not isinstance(deps, dict):
        errors.append("Manifest.toml missing deps table")
        return None
    raw = deps.get(package)
    if not isinstance(raw, list) or len(raw) != 1 or not isinstance(raw[0], dict):
        errors.append(
            f"Manifest.toml must contain exactly one [[deps.{package}]] table"
        )
        return None
    return raw[0]


def _string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _compare(
    errors: list[str], *, label: str, observed: str | None, expected: str | None
) -> None:
    if observed != expected:
        errors.append(f"{label}: expected {expected!r}, observed {observed!r}")


def _receipt_template(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "stage_id": None if contract is None else contract.get("stage_id"),
        "authority_effect": "NONE",
        "status": "FAIL",
        "project_sha256": None,
        "manifest_sha256": None,
        "julia_version": None,
        "manifest_format": None,
        "project_hash": None,
        "packages": {},
        "errors": [],
    }


def verify(
    *, contract_path: Path, project_path: Path, manifest_path: Path
) -> dict[str, Any]:
    errors: list[str] = []
    contract: dict[str, Any] | None = None
    receipt = _receipt_template()

    try:
        contract = _load_json(contract_path)
        receipt = _receipt_template(contract)
    except Exception as exc:  # fail closed and still emit a machine receipt
        errors.append(f"contract parse failure: {exc}")

    try:
        project_sha256 = _sha256(project_path)
        project = _load_toml(project_path)
        receipt["project_sha256"] = project_sha256
    except Exception as exc:
        project_sha256 = None
        project = {}
        errors.append(f"Project.toml read/parse failure: {exc}")

    try:
        manifest_sha256 = _sha256(manifest_path)
        manifest = _load_toml(manifest_path)
        receipt["manifest_sha256"] = manifest_sha256
    except Exception as exc:
        manifest_sha256 = None
        manifest = {}
        errors.append(f"Manifest.toml read/parse failure: {exc}")

    lock = None if contract is None else contract.get("julia_environment_lock")
    if not isinstance(lock, dict):
        errors.append("CONTRACT.json missing julia_environment_lock object")
        lock = {}

    expected_project_sha = _string(lock.get("project_sha256"))
    expected_manifest_sha = _string(lock.get("manifest_sha256"))
    if expected_project_sha is None or HEX64.fullmatch(expected_project_sha) is None:
        errors.append("contract project_sha256 must be a lowercase 64-hex digest")
    if expected_manifest_sha is None or HEX64.fullmatch(expected_manifest_sha) is None:
        errors.append("contract manifest_sha256 must be a lowercase 64-hex digest")

    if project_sha256 != expected_project_sha:
        errors.append(
            "Project.toml SHA-256 mismatch: "
            f"expected {expected_project_sha!r}, observed {project_sha256!r}"
        )
    if manifest_sha256 != expected_manifest_sha:
        errors.append(
            "Manifest.toml SHA-256 mismatch: "
            f"expected {expected_manifest_sha!r}, observed {manifest_sha256!r}"
        )

    julia_version = _string(manifest.get("julia_version"))
    manifest_format = _string(manifest.get("manifest_format"))
    project_hash = _string(manifest.get("project_hash"))
    receipt["julia_version"] = julia_version
    receipt["manifest_format"] = manifest_format
    receipt["project_hash"] = project_hash

    expected_julia_version = _string(lock.get("julia_version"))
    expected_manifest_format = _string(lock.get("manifest_format"))
    expected_project_hash = _string(lock.get("project_hash"))

    if expected_julia_version is None or SEMVER.fullmatch(expected_julia_version) is None:
        errors.append("contract julia_version must be an exact semantic version")
    if expected_manifest_format is None:
        errors.append("contract manifest_format must be a string")
    if expected_project_hash is None or HEX40.fullmatch(expected_project_hash) is None:
        errors.append("contract project_hash must be a lowercase 40-hex digest")

    _compare(
        errors,
        label="Julia version mismatch",
        observed=julia_version,
        expected=expected_julia_version,
    )
    _compare(
        errors,
        label="manifest_format mismatch",
        observed=manifest_format,
        expected=expected_manifest_format,
    )
    _compare(
        errors,
        label="project_hash mismatch",
        observed=project_hash,
        expected=expected_project_hash,
    )

    project_deps = project.get("deps")
    if not isinstance(project_deps, dict):
        errors.append("Project.toml missing deps table")
        project_deps = {}

    expected_packages = lock.get("required_packages")
    if not isinstance(expected_packages, dict) or not expected_packages:
        errors.append("contract required_packages must be a non-empty object")
        expected_packages = {}

    observed_packages: dict[str, Any] = {}
    for package, raw_pin in sorted(expected_packages.items()):
        if not isinstance(package, str) or not isinstance(raw_pin, dict):
            errors.append(f"invalid required package pin for {package!r}")
            continue

        expected_uuid = _string(raw_pin.get("uuid"))
        expected_version = _string(raw_pin.get("version"))
        expected_tree = _string(raw_pin.get("git_tree_sha1"))
        if expected_uuid is None or UUID.fullmatch(expected_uuid) is None:
            errors.append(f"{package} contract UUID is malformed")
        if expected_version is None or SEMVER.fullmatch(expected_version) is None:
            errors.append(f"{package} contract version is not exact semver")
        if expected_tree is None or HEX40.fullmatch(expected_tree) is None:
            errors.append(f"{package} contract git-tree-sha1 is malformed")

        project_uuid = _string(project_deps.get(package))
        _compare(
            errors,
            label=f"{package} Project.toml UUID mismatch",
            observed=project_uuid,
            expected=expected_uuid,
        )

        entry = _manifest_package(manifest, package, errors)
        if entry is None:
            observed_packages[package] = None
            continue

        observed_uuid = _string(entry.get("uuid"))
        observed_version = _string(entry.get("version"))
        observed_tree = _string(entry.get("git-tree-sha1"))
        observed_packages[package] = {
            "uuid": observed_uuid,
            "version": observed_version,
            "git_tree_sha1": observed_tree,
        }

        _compare(
            errors,
            label=f"{package} UUID mismatch",
            observed=observed_uuid,
            expected=expected_uuid,
        )
        _compare(
            errors,
            label=f"{package} version mismatch",
            observed=observed_version,
            expected=expected_version,
        )
        _compare(
            errors,
            label=f"{package} git-tree-sha1 mismatch",
            observed=observed_tree,
            expected=expected_tree,
        )

    receipt["packages"] = observed_packages
    receipt["errors"] = errors
    receipt["status"] = "PASS" if not errors else "FAIL"
    return receipt


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    receipt = verify(
        contract_path=args.contract,
        project_path=args.project,
        manifest_path=args.manifest,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

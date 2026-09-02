#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_version(manifest: dict, package: str) -> str | None:
    entry = manifest.get("deps", {}).get(package)
    if isinstance(entry, list) and entry:
        entry = entry[0]
    if not isinstance(entry, dict):
        return None
    value = entry.get("version")
    return value if isinstance(value, str) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    lock_path = Path(args.lock)
    project_path = Path(args.project)
    manifest_path = Path(args.manifest)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    project = tomllib.loads(project_path.read_text(encoding="utf-8"))
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))

    observed_project_sha = sha256(project_path)
    observed_manifest_sha = sha256(manifest_path)
    observed_versions = {
        package: package_version(manifest, package)
        for package in lock["packages"]
    }

    checks = {
        "authority_effect_none": lock.get("authority_effect") == "NONE",
        "julia_version": manifest.get("julia_version") == lock["julia_version"],
        "project_sha256": observed_project_sha == lock["project_sha256"],
        "manifest_sha256": observed_manifest_sha == lock["manifest_sha256"],
        "direct_project_dependencies": set(project.get("deps", {})) == {"Nemo", "Symbolics"},
        "package_versions": observed_versions == lock["packages"],
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "1.0.0",
        "stage_id": lock["stage_id"],
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "observed": {
            "julia_version": manifest.get("julia_version"),
            "project_sha256": observed_project_sha,
            "manifest_sha256": observed_manifest_sha,
            "package_versions": observed_versions,
        },
        "expected": {
            "julia_version": lock["julia_version"],
            "project_sha256": lock["project_sha256"],
            "manifest_sha256": lock["manifest_sha256"],
            "package_versions": lock["packages"],
        },
        "authority_effect": "NONE",
        "claim_boundary": lock["claim_boundary"],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

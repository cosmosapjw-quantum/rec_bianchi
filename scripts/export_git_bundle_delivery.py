#!/usr/bin/env python3
"""Export self-contained Git bundle deliveries and an integrity receipt.

The feature bundle carries a dedicated delivery ref at the requested target and
all objects needed to fetch it without an external prerequisite.  Consumers
inspect the receipt's ordered ``feature_commits`` and cherry-pick that range
onto their freshly fetched integration branch.  The full bundle carries all
repository refs for disaster recovery.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def run_git(repo: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed ({result.returncode}):\n"
            f"{result.stdout}{result.stderr}"
        )
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolved_commit(repo: Path, revision: str) -> str:
    return run_git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}").stdout.strip()


def verify_bundle(repo: Path, path: Path) -> str:
    result = run_git(repo, "bundle", "verify", str(path), check=False)
    if result.returncode:
        raise RuntimeError(
            f"git bundle verify failed for {path}:\n{result.stdout}{result.stderr}"
        )
    return "PASS"


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base", required=True, help="exclusive feature base commit")
    parser.add_argument("--ref", default="HEAD", help="target revision")
    parser.add_argument("--version", required=True, help="filename version token")
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    repo = args.repo.resolve()
    if not (repo / ".git").exists() and run_git(repo, "rev-parse", "--git-dir", check=False).returncode:
        raise RuntimeError(f"not a Git repository: {repo}")
    if run_git(repo, "status", "--porcelain").stdout.strip():
        raise RuntimeError("refusing bundle export from a dirty working tree")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.version):
        raise ValueError("version may contain only letters, digits, dot, underscore and hyphen")

    base = resolved_commit(repo, args.base)
    target = resolved_commit(repo, args.ref)
    if run_git(repo, "merge-base", "--is-ancestor", base, target, check=False).returncode:
        raise RuntimeError("base is not an ancestor of target")
    feature_commits = [
        line
        for line in run_git(repo, "rev-list", "--reverse", f"{base}..{target}").stdout.splitlines()
        if line
    ]
    if not feature_commits:
        raise RuntimeError("feature range is empty")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    full_bundle = output / f"rec_bianchi_{args.version}_full.bundle"
    feature_bundle = output / f"rec_bianchi_{args.version}_feature.bundle"
    receipt_path = output / f"rec_bianchi_{args.version}_bundle_receipt.json"
    for path in (full_bundle, feature_bundle, receipt_path):
        path.unlink(missing_ok=True)

    delivery_ref = f"refs/heads/delivery/{args.version}"
    run_git(repo, "update-ref", delivery_ref, target)
    try:
        run_git(repo, "bundle", "create", str(feature_bundle), delivery_ref)
    finally:
        run_git(repo, "update-ref", "-d", delivery_ref, check=False)
    run_git(repo, "bundle", "create", str(full_bundle), "--all")

    feature_verify = verify_bundle(repo, feature_bundle)
    full_verify = verify_bundle(repo, full_bundle)
    receipt = {
        "classification": "GIT_BUNDLE_DELIVERY_RECEIPT",
        "repository": str(repo),
        "version": args.version,
        "base_commit": base,
        "target_commit": target,
        "delivery_ref": delivery_ref,
        "feature_commits": feature_commits,
        "feature_bundle": {
            "path": str(feature_bundle),
            "size_bytes": feature_bundle.stat().st_size,
            "sha256": sha256(feature_bundle),
        },
        "full_bundle": {
            "path": str(full_bundle),
            "size_bytes": full_bundle.stat().st_size,
            "sha256": sha256(full_bundle),
        },
        "feature_bundle_verify": feature_verify,
        "full_bundle_verify": full_verify,
        "apply_policy": (
            "fetch delivery ref, inspect ordered feature_commits, cherry-pick them "
            "onto a fresh integration branch; never force-push shared history"
        ),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - command-line error boundary
        print(f"bundle export failed: {exc}", file=sys.stderr)
        raise SystemExit(1)

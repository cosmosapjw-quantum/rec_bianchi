#!/usr/bin/env python3
"""Verify SHA-256 manifests against a worktree or an immutable Git tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath


DIGEST = re.compile(r"[0-9a-f]{64}")


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(
        path.read_text(encoding="ascii").splitlines(), start=1
    ):
        if not line:
            continue
        try:
            digest, name = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"malformed manifest line {line_number}") from error
        candidate = PurePosixPath(name)
        if (
            not DIGEST.fullmatch(digest)
            or not name
            or candidate.is_absolute()
            or "." in candidate.parts
            or ".." in candidate.parts
            or str(candidate) != name
        ):
            raise ValueError(f"unsafe manifest path on line {line_number}: {name}")
        if name in seen:
            raise ValueError(f"duplicate manifest path: {name}")
        seen.add(name)
        entries.append((digest, name))
    if not entries:
        raise ValueError("empty manifest")
    return entries


def verify_worktree(root: Path, entries: list[tuple[str, str]]) -> None:
    root = root.resolve()
    for expected, name in entries:
        path = root / name
        if (
            path.is_symlink()
            or not path.is_file()
            or not path.resolve().is_relative_to(root)
        ):
            raise ValueError(f"missing or unsafe payload path: {name}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"digest mismatch: {name}")


def git_blob(repo: Path, revision: str, name: str) -> bytes:
    process = subprocess.run(
        ["git", "--no-replace-objects", "cat-file", "blob", f"{revision}:{name}"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
        check=False,
    )
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"missing Git payload path: {name}: {detail}")
    return process.stdout


def verify_git(
    repo: Path,
    revision: str,
    prefix: PurePosixPath,
    entries: list[tuple[str, str]],
) -> None:
    for expected, name in entries:
        source_name = str(prefix / name) if str(prefix) != "." else name
        actual = hashlib.sha256(git_blob(repo, revision, source_name)).hexdigest()
        if actual != expected:
            raise ValueError(f"digest mismatch: {name}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="mode", required=True)

    worktree = subparsers.add_parser("worktree")
    worktree.add_argument("--root", type=Path, required=True)
    worktree.add_argument("--manifest", type=Path, required=True)

    git = subparsers.add_parser("git")
    git.add_argument("--repo", type=Path, required=True)
    git.add_argument("--revision", required=True)
    git.add_argument("--prefix", type=PurePosixPath, default=PurePosixPath())
    git.add_argument("--manifest", type=Path, required=True)
    return root


def main() -> int:
    arguments = parser().parse_args()
    entries = parse_manifest(arguments.manifest)
    if arguments.mode == "worktree":
        verify_worktree(arguments.root, entries)
        source = str(arguments.root.resolve())
    else:
        verify_git(arguments.repo, arguments.revision, arguments.prefix, entries)
        source = f"{arguments.revision}:{arguments.prefix}"
    print(
        json.dumps(
            {"files": len(entries), "source": source, "status": "PASS"},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser().exit(2, f"FAIL_MANIFEST_BINDING: {error}\n")

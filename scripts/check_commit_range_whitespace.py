#!/usr/bin/env python3
"""Fail when feature commits or pending source edits contain whitespace errors.

Evidence logs under ``state/*.log`` are excluded from the committed-range check
because they preserve third-party command output verbatim. Source, tests,
scripts, documentation and structured state remain covered.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


DEFAULT_EXCLUDES = ("state/*.log",)


def _git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def _load_feature_base(repo: Path) -> str:
    path = repo / "state/PATCH_BASE.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read feature base from {path}: {exc}") from exc
    for key in ("feature_exclusive_base_commit", "feature_exclusive_base"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate:
            result = _git(repo, "rev-parse", "--verify", f"{candidate}^{{commit}}")
            if result.returncode:
                raise RuntimeError(
                    f"feature base {candidate!r} is not a local commit:\n"
                    f"{result.stdout}{result.stderr}"
                )
            return result.stdout.strip()
    raise RuntimeError(f"{path} lacks feature_exclusive_base_commit")


def _pathspec(excludes: tuple[str, ...]) -> list[str]:
    return [".", *(f":(exclude){item}" for item in excludes)]


def check_repository(
    repo: Path,
    *,
    base: str | None = None,
    excludes: tuple[str, ...] = DEFAULT_EXCLUDES,
) -> dict[str, object]:
    repo = repo.resolve()
    base_commit = base or _load_feature_base(repo)
    pathspec = _pathspec(excludes)
    commands = {
        "committed_feature_range": [
            "diff",
            "--check",
            f"{base_commit}...HEAD",
            "--",
            *pathspec,
        ],
        "staged_changes": ["diff", "--cached", "--check", "--", *pathspec],
        "unstaged_changes": ["diff", "--check", "--", *pathspec],
    }
    failures: dict[str, str] = {}
    for name, arguments in commands.items():
        result = _git(repo, *arguments)
        if result.returncode:
            failures[name] = (result.stdout + result.stderr).strip()
    return {
        "status": "PASS" if not failures else "FAIL",
        "repository": str(repo),
        "feature_base": base_commit,
        "head": _git(repo, "rev-parse", "HEAD").stdout.strip(),
        "excluded_evidence_logs": list(excludes),
        "checks": list(commands),
        "failures": failures,
    }


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base", help="override state/PATCH_BASE.json feature base")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    try:
        receipt = check_repository(args.repo, base=args.base)
    except Exception as exc:  # noqa: BLE001 - command-line validation boundary
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if receipt["status"] != "PASS":
        for name, output in receipt["failures"].items():
            print(f"\n[{name}]\n{output}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

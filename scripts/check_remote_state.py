#!/usr/bin/env python3
"""Inspect local Git state and, when possible, the configured remote refs.

This command never writes credentials into Git configuration or URLs.  It is
safe to run in offline sandboxes: network/authentication failure is recorded in
a JSON receipt rather than being misreported as a synchronized remote.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def run_git(args: list[str], *, env: dict[str, str] | None = None, timeout: int = 30):
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def git_output(args: list[str]) -> str:
    result = run_git(args)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def https_from_github_ssh(url: str) -> str | None:
    prefix = "git@github.com:"
    if not url.startswith(prefix):
        return None
    return "https://github.com/" + url[len(prefix) :]


def remote_environment(token: str | None):
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    helper = None
    if token:
        directory = tempfile.TemporaryDirectory(prefix="rec-bianchi-askpass-")
        helper = directory
        path = Path(directory.name) / "askpass.sh"
        path.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  *Username*) printf '%s\\n' 'x-access-token' ;;\n"
            "  *Password*) printf '%s\\n' \"$GITHUB_REC_BIANCHI_TOKEN\" ;;\n"
            "  *) exit 1 ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        env["GIT_ASKPASS"] = str(path)
    return env, helper


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "state" / "REMOTE_CHECK_LATEST.json",
    )
    parser.add_argument("--require-access", action="store_true")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    local_head = git_output(["rev-parse", "HEAD"])
    local_tree = git_output(["rev-parse", "HEAD^{tree}"])
    branch = git_output(["branch", "--show-current"])
    origin = git_output(["remote", "get-url", "origin"])
    dirty_lines = git_output(["status", "--porcelain"]).splitlines()

    candidates: list[tuple[str, str]] = [("configured", origin)]
    https = https_from_github_ssh(origin)
    if https and shutil.which("ssh") is None:
        candidates.append(("https-fallback", https))

    token = os.environ.get("GITHUB_REC_BIANCHI_TOKEN")
    env, helper = remote_environment(token)
    remote_refs: dict[str, str] = {}
    attempts = []
    selected_transport = None
    for transport, url in candidates:
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--heads", "--tags", url],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            attempts.append(
                {
                    "transport": transport,
                    "url": url,
                    "returncode": result.returncode,
                    "stderr": result.stderr.strip(),
                }
            )
            if result.returncode == 0:
                selected_transport = transport
                for line in result.stdout.splitlines():
                    sha, ref = line.split(maxsplit=1)
                    remote_refs[ref] = sha
                break
        except subprocess.TimeoutExpired:
            attempts.append(
                {
                    "transport": transport,
                    "url": url,
                    "returncode": None,
                    "stderr": "timeout",
                }
            )
    if helper is not None:
        helper.cleanup()

    remote_main = remote_refs.get("refs/heads/main")
    remote_accessible = selected_transport is not None
    remote_matches_local = remote_main == local_head if remote_main else False

    receipt = {
        "classification": "REMOTE_REPOSITORY_CHECK",
        "checked_at_utc": now.isoformat(),
        "checked_at_kst": now.astimezone(ZoneInfo("Asia/Seoul")).isoformat(),
        "repository_root": str(ROOT),
        "origin": origin,
        "local": {
            "branch": branch,
            "head": local_head,
            "tree": local_tree,
            "dirty": bool(dirty_lines),
            "dirty_paths": dirty_lines,
        },
        "remote": {
            "accessible": remote_accessible,
            "selected_transport": selected_transport,
            "main_sha": remote_main,
            "matches_local_head": remote_matches_local,
            "ref_count": len(remote_refs),
            "refs": remote_refs,
            "attempts": attempts,
        },
        "patch_base_policy": (
            "Use remote main when it is accessible and locally known as an ancestor; "
            "otherwise use state/PATCH_BASE.json and state the uncertainty."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if args.require_access and not remote_accessible:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

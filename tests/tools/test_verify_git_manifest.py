from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]
VERIFIER = REPOSITORY / "tools" / "verify_git_manifest.py"


def run_verifier(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFIER), *(str(arg) for arg in args)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_worktree_mode_rejects_a_stale_digest(tmp_path: Path) -> None:
    payload = tmp_path / "payload.txt"
    payload.write_bytes(b"actual payload\n")
    stale = hashlib.sha256(b"different payload\n").hexdigest()
    manifest = tmp_path / "MANIFEST.sha256"
    manifest.write_text(f"{stale}  payload.txt\n", encoding="ascii")

    result = run_verifier(
        "worktree", "--root", tmp_path, "--manifest", manifest
    )

    assert result.returncode == 2
    assert "digest mismatch: payload.txt" in result.stderr


def test_git_mode_reads_committed_bytes_not_a_dirty_worktree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        ["git", "config", "user.email", "manifest-test@example.invalid"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "manifest test"], cwd=repo, check=True
    )
    payload = repo / "payload.txt"
    payload.write_bytes(b"committed payload\n")
    subprocess.run(["git", "add", "payload.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repo, check=True)

    digest = hashlib.sha256(b"committed payload\n").hexdigest()
    manifest = tmp_path / "MANIFEST.sha256"
    manifest.write_text(f"{digest}  payload.txt\n", encoding="ascii")
    payload.write_bytes(b"dirty worktree payload\n")

    result = run_verifier(
        "git",
        "--repo",
        repo,
        "--revision",
        "HEAD",
        "--manifest",
        manifest,
    )

    assert result.returncode == 0, result.stderr
    assert '"status": "PASS"' in result.stdout
    assert '"files": 1' in result.stdout


def test_manifest_rejects_parent_traversal(tmp_path: Path) -> None:
    manifest = tmp_path / "MANIFEST.sha256"
    digest = hashlib.sha256(b"outside\n").hexdigest()
    manifest.write_text(f"{digest}  ../outside.txt\n", encoding="ascii")

    result = run_verifier(
        "worktree", "--root", tmp_path, "--manifest", manifest
    )

    assert result.returncode == 2
    assert "unsafe manifest path" in result.stderr

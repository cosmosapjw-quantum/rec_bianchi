from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts/check_commit_range_whitespace.py"


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Whitespace Policy Test")
    _git(repo, "config", "user.email", "noreply@example.invalid")
    (repo / "sample.py").write_text("x = 1\n")
    _git(repo, "add", "sample.py")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "state").mkdir()
    (repo / "state/PATCH_BASE.json").write_text(
        json.dumps({"feature_exclusive_base_commit": base}) + "\n"
    )
    return repo, base


def _run_checker(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--repo", str(repo)],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def test_checker_rejects_whitespace_in_committed_feature_range(tmp_path: Path) -> None:
    repo, _ = _init_repo(tmp_path)
    (repo / "sample.py").write_text("x = 1\n\n")
    _git(repo, "add", "sample.py", "state/PATCH_BASE.json")
    _git(repo, "commit", "-q", "-m", "bad feature")

    result = _run_checker(repo)

    assert result.returncode != 0
    assert "sample.py" in result.stdout + result.stderr
    assert "new blank line at EOF" in result.stdout + result.stderr


def test_checker_ignores_recorded_state_logs_but_checks_source(tmp_path: Path) -> None:
    repo, _ = _init_repo(tmp_path)
    (repo / "state/evidence.log").write_text("captured output with spaces   \n")
    _git(repo, "add", "state/PATCH_BASE.json", "state/evidence.log")
    _git(repo, "commit", "-q", "-m", "evidence log")

    result = _run_checker(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert '"status": "PASS"' in result.stdout


def test_checker_rejects_uncommitted_source_whitespace(tmp_path: Path) -> None:
    repo, _ = _init_repo(tmp_path)
    _git(repo, "add", "state/PATCH_BASE.json")
    _git(repo, "commit", "-q", "-m", "lock base")
    (repo / "sample.py").write_text("x = 1  \n")

    result = _run_checker(repo)

    assert result.returncode != 0
    assert "sample.py" in result.stdout + result.stderr
    assert "trailing whitespace" in result.stdout + result.stderr


def test_known_immutable_generated_csv_is_excluded_but_new_csv_is_checked(tmp_path: Path) -> None:
    repo, _ = _init_repo(tmp_path)
    frozen = repo / "research/rec_r10_c8_20261015/C8_REFINEMENT.csv"
    frozen.parent.mkdir(parents=True)
    frozen.write_bytes(b"x,y\r\n1,2\r\n")
    _git(repo, "add", "state/PATCH_BASE.json", str(frozen.relative_to(repo)))
    _git(repo, "commit", "-q", "-m", "preserve original CSV bytes")
    result = _run_checker(repo)
    assert result.returncode == 0, result.stdout + result.stderr

    new_csv = repo / "research/new_scenario/output.csv"
    new_csv.parent.mkdir(parents=True)
    new_csv.write_bytes(b"x,y\r\n1,2\r\n")
    _git(repo, "add", str(new_csv.relative_to(repo)))
    _git(repo, "commit", "-q", "-m", "unregistered artifact is still checked")
    result = _run_checker(repo)
    assert result.returncode != 0
    assert "research/new_scenario/output.csv" in result.stdout + result.stderr


def test_normal_python_and_markdown_source_still_have_strict_whitespace_gate(tmp_path: Path) -> None:
    repo, _ = _init_repo(tmp_path)
    markdown = repo / "research/current/README.md"
    markdown.parent.mkdir(parents=True)
    markdown.write_text("ordinary scientific source must be clean  \n")
    _git(repo, "add", "state/PATCH_BASE.json", str(markdown.relative_to(repo)))
    _git(repo, "commit", "-q", "-m", "bad source")
    result = _run_checker(repo)
    assert result.returncode != 0
    assert "research/current/README.md" in result.stdout + result.stderr

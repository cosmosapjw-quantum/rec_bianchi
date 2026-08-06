from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/export_git_bundle_delivery.py"


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_bundle_exporter_creates_verified_full_and_feature_bundles(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Bundle Test")
    _git(repo, "config", "user.email", "bundle@example.invalid")
    (repo / "base.txt").write_text("base\n")
    _git(repo, "add", "base.txt")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "feature.txt").write_text("feature\n")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-q", "-m", "feature")
    feature = _git(repo, "rev-parse", "HEAD")

    output = tmp_path / "out"
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            str(repo),
            "--base",
            base,
            "--ref",
            "HEAD",
            "--version",
            "vtest",
            "--output-dir",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    full = output / "rec_bianchi_vtest_full.bundle"
    patch = output / "rec_bianchi_vtest_feature.bundle"
    receipt = json.loads((output / "rec_bianchi_vtest_bundle_receipt.json").read_text())
    assert full.is_file() and patch.is_file()
    assert receipt["feature_commits"] == [feature]
    assert receipt["base_commit"] == base
    assert receipt["target_commit"] == feature
    assert receipt["full_bundle_verify"] == "PASS"
    assert receipt["feature_bundle_verify"] == "PASS"
    _git(repo, "bundle", "verify", str(full))
    _git(repo, "bundle", "verify", str(patch))

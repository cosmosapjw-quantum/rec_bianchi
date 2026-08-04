#!/usr/bin/env python3
"""Export binary-safe Git patches from a declared base to current HEAD."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(args: list[str], *, binary: bool = False):
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=not binary,
        check=True,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT.parent / "rec_bianchi_patches",
    )
    args = parser.parse_args()

    base_state = json.loads((ROOT / "state" / "PATCH_BASE.json").read_text())
    base = args.base or base_state["base_commit"]
    head = git(["rev-parse", "HEAD"]).stdout.strip()
    git(["cat-file", "-e", f"{base}^{{commit}}"])
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, head], cwd=ROOT
    ).returncode == 0
    if not ancestor:
        raise SystemExit(f"base {base} is not an ancestor of HEAD {head}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"rec_bianchi_{base[:8]}_to_{head[:8]}"
    mbox = args.output_dir / f"{stem}.mbox"
    diff = args.output_dir / f"{stem}.patch"

    mbox.write_bytes(
        git(
            ["format-patch", "--binary", "--stdout", f"{base}..{head}"],
            binary=True,
        ).stdout
    )
    diff.write_bytes(
        git(
            ["diff", "--binary", "--full-index", f"{base}..{head}"],
            binary=True,
        ).stdout
    )

    commits = git(["log", "--reverse", "--format=%H%x09%s", f"{base}..{head}"]).stdout.splitlines()
    receipt = {
        "classification": "GIT_PATCH_EXPORT_RECEIPT",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": "cosmosapjw-quantum/rec_bianchi",
        "base": base,
        "head": head,
        "commit_count": len(commits),
        "commits": commits,
        "files": {
            mbox.name: {"sha256": sha256(mbox), "bytes": mbox.stat().st_size},
            diff.name: {"sha256": sha256(diff), "bytes": diff.stat().st_size},
        },
        "apply": {
            "mbox": f"git am --3way {mbox.name}",
            "diff": f"git apply --3way --index {diff.name}",
        },
        "warning": (
            "Apply only when the declared base is in local history. If remote main "
            "has diverged, fetch it first and use git am --3way on a feature branch."
        ),
    }
    receipt_path = args.output_dir / f"{stem}.receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mbox": str(mbox), "diff": str(diff), "receipt": str(receipt_path)}, indent=2))


if __name__ == "__main__":
    main()

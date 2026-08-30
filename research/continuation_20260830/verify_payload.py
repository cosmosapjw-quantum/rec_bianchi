#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from pathlib import Path, PurePosixPath

REL = Path("research/continuation_20260830")
HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[1]


def git(repo: Path, *args: str) -> str:
    run = subprocess.run(
        ["git", "--no-replace-objects", *args], cwd=repo,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45
    )
    if run.returncode:
        raise ValueError("git " + " ".join(args) + ": " + run.stderr.strip())
    return run.stdout.removesuffix("\n")


def validate(root: Path, repo: Path | None = None) -> dict:
    root = root.resolve()
    directory = root / REL
    entries: dict[str, str] = {}
    for line in (directory / "MANIFEST.sha256").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        path = PurePosixPath(name)
        if (not re.fullmatch(r"[0-9a-f]{64}", digest) or path.is_absolute()
                or ".." in path.parts or str(path) != name or name in entries):
            raise ValueError("unsafe or duplicate manifest entry")
        target = root / path
        if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
            raise ValueError("missing or unsafe payload path: " + name)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError("payload byte mismatch: " + name)
        entries[name] = digest

    contract = json.loads((directory / "CONTRACT.json").read_text())
    if set(entries) != set(contract["delivery_paths"]):
        raise ValueError("delivery closure mismatch")
    if contract["claim"] != "NO_PASS_REC_PHYSICAL_SPLIT":
        raise ValueError("claim boundary changed")
    if contract["exact_next_action"] != "REC-LOCAL-01_CANONICAL_CONTEXT_INTEGRATION":
        raise ValueError("next action changed")

    checked = 0
    if repo is not None:
        base = contract["base"]
        blocked = contract["blocked_scientific_source"]
        partial = contract["superseded_partial_branch"]
        for item, label in ((base, "base"), (blocked, "blocked source"), (partial, "partial")):
            if git(repo, "rev-parse", item["commit"] + "^{tree}") != item["tree"]:
                raise ValueError(label + " tree mismatch")
        source_path = contract["component"]["path"]
        if git(repo, "rev-parse", partial["commit"] + ":" + source_path) != contract["component"]["source_blob_sha1"]:
            raise ValueError("partial source blob mismatch")
        checked = 4

    return {
        "status": "PASS_DELIVERY_INTAKE_ONLY",
        "files": len(entries),
        "source_objects": "CHECKED" if repo is not None else "NOT_RUN",
        "source_objects_checked": checked,
        "claim": contract["claim"],
        "next": contract["exact_next_action"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--repo", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.root, args.repo), sort_keys=True))
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(2, "FAIL_PAYLOAD_CHECK: " + str(error) + "\n")

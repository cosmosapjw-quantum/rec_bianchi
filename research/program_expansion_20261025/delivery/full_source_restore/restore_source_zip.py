#!/usr/bin/env python3
"""Verify binary ZIP parts and optionally restore the exact original ZIP.

Python standard library only. No extraction and no scientific calculation.

Verify without writing a second ZIP:
    python3 restore_source_zip.py --verify-only

Restore after downloading this script, PARTS_MANIFEST.json and every part:
    python3 restore_source_zip.py --output /path/to/restored_source.zip

Existing output files are never overwritten. Each part and the concatenation
must match their recorded byte counts and SHA256 values before publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

CHUNK_BYTES = 1024 * 1024


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "REC_HD_H5_BINARY_ZIP_PARTS_V1":
        raise ValueError("UNSUPPORTED_PARTS_MANIFEST_SCHEMA")
    source = manifest["original_zip"]
    if Path(source["name"]).name != source["name"]:
        raise ValueError("ORIGINAL_ZIP_NAME_MUST_BE_A_BASENAME")
    parts = manifest["parts"]
    if not parts or [p["index"] for p in parts] != list(range(1, len(parts) + 1)):
        raise ValueError("PART_SEQUENCE_INVALID")
    names = [p["name"] for p in parts]
    if len(set(names)) != len(names) or any(Path(n).name != n for n in names):
        raise ValueError("PART_NAMES_INVALID")
    if sum(p["bytes"] for p in parts) != source["bytes"]:
        raise ValueError("MANIFEST_PART_BYTES_DO_NOT_SUM_TO_ORIGINAL")
    return manifest


def verify_stream(manifest: dict, parts_dir: Path, destination=None) -> dict:
    whole = hashlib.sha256()
    total = 0
    verified = []
    for part in manifest["parts"]:
        digest = hashlib.sha256()
        count = 0
        with (parts_dir / part["name"]).open("rb") as handle:
            for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
                digest.update(chunk)
                whole.update(chunk)
                count += len(chunk)
                if destination is not None:
                    destination.write(chunk)
        if count != part["bytes"]:
            raise ValueError("PART_SIZE_MISMATCH:" + part["name"])
        if digest.hexdigest() != part["sha256"]:
            raise ValueError("PART_SHA256_MISMATCH:" + part["name"])
        total += count
        verified.append({"index": part["index"], "name": part["name"],
                         "bytes": count, "sha256": digest.hexdigest()})
    source = manifest["original_zip"]
    if total != source["bytes"]:
        raise ValueError("WHOLE_ZIP_SIZE_MISMATCH")
    if whole.hexdigest() != source["sha256"]:
        raise ValueError("WHOLE_ZIP_SHA256_MISMATCH")
    return {"status": "PASS_PARTS_AND_WHOLE_ZIP_IDENTITY",
            "original_zip_name": source["name"], "whole_bytes": total,
            "whole_sha256": whole.hexdigest(), "parts": verified}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path,
                        default=Path(__file__).resolve().with_name("PARTS_MANIFEST.json"))
    parser.add_argument("--parts-dir", type=Path,
                        help="Defaults to the manifest directory")
    parser.add_argument("--verify-only", action="store_true",
                        help="Stream and verify all parts without producing another ZIP")
    parser.add_argument("--output", type=Path,
                        help="Destination ZIP; defaults to original basename beside manifest")
    args = parser.parse_args()
    start = time.perf_counter()
    manifest = load_manifest(args.manifest)
    parts_dir = args.parts_dir or args.manifest.resolve().parent
    if args.verify_only:
        if args.output is not None:
            parser.error("--output cannot be used with --verify-only")
        result = verify_stream(manifest, parts_dir)
        result["mode"] = "VERIFY_ONLY_NO_ZIP_CREATED"
    else:
        output = args.output or args.manifest.resolve().parent / manifest["original_zip"]["name"]
        if output.exists():
            raise FileExistsError("OUTPUT_ALREADY_EXISTS:" + str(output))
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", dir=output.parent,
                                             prefix=output.name + ".partial.",
                                             delete=False) as handle:
                temporary = Path(handle.name)
                result = verify_stream(manifest, parts_dir, handle)
                handle.flush()
                os.fsync(handle.fileno())
            # Atomic creation refuses an output created by another process too.
            os.link(temporary, output)
            temporary.unlink()
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        result["mode"] = "RESTORED_AND_VERIFIED"
        result["output"] = str(output.resolve())
    result["wall_seconds"] = time.perf_counter() - start
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("RESTORE_FAILED: " + str(error), file=sys.stderr)
        sys.exit(1)

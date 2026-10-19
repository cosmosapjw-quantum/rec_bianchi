#!/usr/bin/env python3
"""Extract the reviewed U5 NPZ and make a transfer capsule below 256 MiB.

The 308 MB original raw archive stays authoritative and is never rewritten.
Only a regular, SHA-matched checkpoint member is exported. No ODE is run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import zipfile

RAW_SHA256 = "8d18bd221e4cf9aa4af1e8a48eb2048ebe9c65d33dda0f9a3de17fb529823c3c"
CHECKPOINT_SHA256 = "7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b"
MEMBER_BASENAME = "python_u5_thermal.npz"
MAX_TRANSFER_BYTES = 256 * 1024**2


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_checkpoint(archive, destination, *, expected_raw_sha=RAW_SHA256,
                       expected_checkpoint_sha=CHECKPOINT_SHA256,
                       transfer_limit=MAX_TRANSFER_BYTES):
    archive, destination = Path(archive).resolve(), Path(destination).resolve()
    if sha256(archive) != expected_raw_sha:
        raise ValueError("ORIGINAL_U5_RAW_SHA_MISMATCH")
    if destination.exists():
        raise FileExistsError("CREATE_ONLY_U5_RECOVERY_EXISTS")
    destination.mkdir(parents=True)
    report = {"schema": "rec.r3l.u5-recovery-capsule.v1", "status": "FAIL",
              "original_raw_sha256": expected_raw_sha,
              "original_raw_bytes": archive.stat().st_size,
              "checkpoint_sha256": expected_checkpoint_sha,
              "full_U6": "NOT_RUN", "new_integrations": 0, "first_failure": None}
    primary = None
    try:
        with tarfile.open(archive, "r:*") as source:
            candidates = []
            for member in source.getmembers():
                path = PurePosixPath(member.name)
                if path.is_absolute() or ".." in path.parts or "\\" in member.name:
                    raise ValueError("UNSAFE_RAW_MEMBER_PATH")
                if path.name == MEMBER_BASENAME:
                    if not member.isfile():
                        raise ValueError("CHECKPOINT_MEMBER_NOT_REGULAR")
                    candidates.append(member)
            if len(candidates) != 1:
                raise ValueError("CHECKPOINT_MEMBER_NOT_UNIQUE")
            member = candidates[0]
            if not 0 < member.size < transfer_limit - 65536:
                raise ValueError("CHECKPOINT_TRANSFER_SIZE")
            checkpoint = destination / MEMBER_BASENAME
            count, digest = 0, hashlib.sha256()
            with source.extractfile(member) as inp, checkpoint.open("xb") as out:
                for chunk in iter(lambda: inp.read(1024 * 1024), b""):
                    count += len(chunk)
                    if count > member.size:
                        raise ValueError("CHECKPOINT_MEMBER_SIZE")
                    digest.update(chunk); out.write(chunk)
            if count != member.size or digest.hexdigest() != expected_checkpoint_sha:
                raise ValueError("REVIEWED_U5_CHECKPOINT_SHA_MISMATCH")
            report.update({"checkpoint_member": member.name,
                           "checkpoint_bytes": count,
                           "checkpoint_path": MEMBER_BASENAME})
        manifest = {key: value for key, value in report.items() if key not in ("status", "first_failure")}
        manifest["status"] = "SHA_VERIFIED_CHECKPOINT_EXTRACTED_NO_SCIENTIFIC_RERUN"
        encoded = json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n"
        capsule = destination / "REC_R3L_REVIEWED_U5_CHECKPOINT.zip"
        with capsule.open("xb") as stream, zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as z:
            z.write(checkpoint, MEMBER_BASENAME)
            z.writestr("MANIFEST.json", encoded)
        if capsule.stat().st_size >= transfer_limit:
            raise ValueError("RECOVERY_CAPSULE_TOO_LARGE")
        with zipfile.ZipFile(capsule) as z, z.open(MEMBER_BASENAME) as stream:
            h = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(chunk)
            if h.hexdigest() != expected_checkpoint_sha:
                raise ValueError("CAPSULE_CHECKPOINT_READBACK_MISMATCH")
        report.update({"status": "PASS_CHECKPOINT_CAPSULE_ONLY", "capsule": capsule.name,
                       "capsule_bytes": capsule.stat().st_size, "capsule_sha256": sha256(capsule),
                       "transfer_limit_bytes": transfer_limit})
    except BaseException as exc:
        primary = exc
        report["first_failure"] = {"type": type(exc).__name__, "message": str(exc)}
        raise
    finally:
        try:
            (destination / "RECOVERY_RECEIPT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        except BaseException as diagnostic:
            if primary is None:
                raise
            primary.add_note(f"Secondary recovery receipt failure: {type(diagnostic).__name__}: {diagnostic}")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args(argv)
    print(json.dumps(extract_checkpoint(args.archive, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()

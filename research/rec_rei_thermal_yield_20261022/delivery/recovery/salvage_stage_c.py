#!/usr/bin/env python3
"""Inspect the pinned incomplete Stage C ZIP; extract only on explicit request.

Default: read-only verification and a concise JSON result on stdout.
--write-reports: write ARCHIVE_DIAGNOSIS.json and ARCHIVE_DIAGNOSIS.md beside this script.
--extract-to DIR: write verified payloads at their expected relative paths. Existing
regular files must be byte-identical; a differing file or symlink aborts preflight.
No network, scientific imports, ODE execution, or replacement of the source ZIP.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import zipfile
import zlib
from collections import Counter
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
ARCHIVE_SHA256 = "c1b672434d6259d2079362e1ee5484e7a9b45bc8e8514230ca38da3c0ff21489"
ARCHIVE_PREFIX = "rec_rei_thermal_yield_20261022/"
ORIGINAL_RECORDED_BYTES = 12_583_886
PUBLISHED_SCIENCE_COMMIT = "d562d03415e37488cd4b5444488c77555260e0fb"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def safe_relative(path: str) -> PurePosixPath:
    pure = PurePosixPath(path)
    if (not path or pure.is_absolute() or ".." in pure.parts or "\\" in path
            or str(pure) != path or "\x00" in path):
        raise ValueError(f"Unsafe or noncanonical relative path: {path!r}")
    return pure


def inspect(archive: Path, expected_path: Path):
    raw = archive.read_bytes()
    if sha256(raw) != ARCHIVE_SHA256:
        raise ValueError("Archive SHA256 differs from the pinned recovery input")
    expected_raw = expected_path.read_bytes()
    expected_rows = json.loads(expected_raw)
    expected = {row["path"]: row for row in expected_rows}
    if len(expected) != len(expected_rows):
        raise ValueError("Duplicate expected relative paths")
    for path in expected:
        safe_relative(path)

    pos = 0
    records = []
    payloads = {}
    boundary = None
    while pos < len(raw):
        if len(raw) - pos < 30:
            boundary = {"kind": "partial_local_header", "offset": pos,
                        "available_bytes": len(raw) - pos}
            break
        values = struct.unpack_from("<4s5H3I2H", raw, pos)
        sig, version, flags, method, mtime, mdate, crc, csize, usize, nlen, xlen = values
        if sig != b"PK\x03\x04":
            boundary = {"kind": "non_local_header", "offset": pos,
                        "signature_hex": sig.hex()}
            break
        name_end = pos + 30 + nlen
        data_start = name_end + xlen
        if data_start > len(raw):
            boundary = {"kind": "partial_local_name_or_extra", "offset": pos,
                        "required_data_start": data_start}
            break
        name = raw[pos + 30:name_end].decode("utf-8" if flags & 0x800 else "cp437")
        if not name.startswith(ARCHIVE_PREFIX):
            raise ValueError(f"Unexpected archive prefix: {name}")
        path = name[len(ARCHIVE_PREFIX):]
        safe_relative(path)
        if path in payloads:
            raise ValueError(f"Duplicate local member: {path}")
        if flags & ~0x800:
            raise ValueError(f"Unsupported/encrypted/data-descriptor flags {flags}: {path}")
        if csize == 0xFFFFFFFF or usize == 0xFFFFFFFF:
            raise ValueError(f"ZIP64 local member requires a different parser: {path}")
        data_end = data_start + csize
        record = {
            "path": path, "archive_path": name,
            "local_header_offset": pos, "data_start_offset": data_start,
            "data_end_offset_exclusive": data_end,
            "header_plus_name_extra_bytes": data_start - pos,
            "compressed_bytes": csize, "header_uncompressed_bytes": usize,
            "method": method, "flags": flags,
            "header_crc32_hex": f"{crc:08x}",
        }
        if data_end > len(raw):
            record["complete"] = False
            records.append(record)
            boundary = {"kind": "partial_member_data", "offset": pos,
                        "path": path, "available_compressed_bytes": len(raw) - data_start,
                        "required_compressed_bytes": csize}
            break
        packed = raw[data_start:data_end]
        if method == 0:
            data = packed
            stream_eof, unused, unconsumed = True, 0, 0
        elif method == 8:
            decoder = zlib.decompressobj(-15)
            data = decoder.decompress(packed) + decoder.flush()
            stream_eof = decoder.eof
            unused = len(decoder.unused_data)
            unconsumed = len(decoder.unconsumed_tail)
        else:
            raise ValueError(f"Unsupported compression method {method}: {path}")
        computed_sha = sha256(data)
        computed_git = git_blob_sha1(data)
        computed_crc = zlib.crc32(data) & 0xFFFFFFFF
        row = expected.get(path)
        checks = {
            "deflate_or_stored_stream_complete": bool(stream_eof and not unused and not unconsumed),
            "local_header_uncompressed_length_match": len(data) == usize,
            "local_header_crc32_match": computed_crc == crc,
            "listed_in_expected": row is not None,
            "expected_length_match": row is not None and len(data) == row["bytes"],
            "expected_sha256_match": row is not None and computed_sha == row["sha256"],
            "expected_git_blob_sha1_match": row is not None and computed_git == row["git_sha"],
        }
        record.update({
            "complete": True, "uncompressed_bytes": len(data),
            "computed_crc32_hex": f"{computed_crc:08x}",
            "sha256": computed_sha, "git_blob_sha1": computed_git,
            "expected_binary": row["binary"] if row is not None else None,
            "checks": checks, "all_checks_pass": all(checks.values()),
        })
        records.append(record)
        payloads[path] = data
        pos = data_end

    if boundary is None:
        boundary = {"kind": "exact_eof_after_complete_local_member", "offset": pos,
                    "trailing_bytes": len(raw) - pos}
    missing = [row for row in expected_rows if row["path"] not in payloads]
    binary_expected = [row for row in expected_rows if row["binary"]]
    binary_records = [row for row in records if row.get("expected_binary")]
    failures = [row["path"] for row in records if not row.get("all_checks_pass", False)]
    try:
        with zipfile.ZipFile(archive) as reader:
            zipfile_result = {"opened": True, "reported_members": len(reader.infolist())}
    except Exception as error:
        zipfile_result = {"opened": False, "exception": type(error).__name__, "message": str(error)}

    signature_locations = {}
    for label, signature in (("last_eocd_signature", b"PK\x05\x06"),
                             ("last_central_header_signature", b"PK\x01\x02")):
        location = raw.rfind(signature)
        containers = [row["path"] for row in records
                      if row["data_start_offset"] <= location < row["data_end_offset_exclusive"]]
        signature_locations[label] = {"offset": location, "inside_member_data": containers}

    all_binary_pass = (len(binary_records) == len(binary_expected)
                       and all(row["all_checks_pass"] for row in binary_records))
    report = {
        "schema": "THERM01_STAGE_C_ARCHIVE_DIAGNOSIS_V1",
        "review_kind": "bounded_read_only_archive_delivery_recovery",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PARTIAL_ARCHIVE_COMPLETE_EXPECTED_BINARY_SET" if all_binary_pass and not failures else "ARCHIVE_PAYLOAD_CHECK_FAILURE",
        "input": {
            "archive": str(archive.resolve()), "bytes": len(raw), "sha256": sha256(raw),
            "original_recorded_archive_bytes": ORIGINAL_RECORDED_BYTES,
            "byte_count_shortfall_vs_original_record": ORIGINAL_RECORDED_BYTES - len(raw),
            "expected_payload_list": str(expected_path.resolve()),
            "expected_payload_list_sha256": sha256(expected_raw),
            "expected_payload_list_basis": "Parent-provided 147-payload recovery plan; each present payload checked against its expected byte length, SHA256, and Git blob SHA1",
            "parent_reported_published_science_commit": PUBLISHED_SCIENCE_COMMIT,
            "published_commit_independently_fetched_by_this_review": False,
        },
        "counts": {
            "expected_payloads": len(expected_rows), "parsed_complete_members": len(payloads),
            "all_checks_pass_members": sum(row.get("all_checks_pass", False) for row in records),
            "expected_payloads_absent": len(missing),
            "expected_binary_payloads": len(binary_expected),
            "binary_payloads_present_and_matching": sum(row["all_checks_pass"] for row in binary_records),
            "npz_payloads_present_and_matching": sum(row["all_checks_pass"] for row in binary_records if row["path"].endswith(".npz")),
            "png_payloads_present_and_matching": sum(row["all_checks_pass"] for row in binary_records if row["path"].endswith(".png")),
            "pdf_payloads_present_and_matching": sum(row["all_checks_pass"] for row in binary_records if row["path"].endswith(".pdf")),
            "payload_identity_failures": len(failures),
            "missing_expected_uncompressed_bytes": sum(row["bytes"] for row in missing),
        },
        "boundary": boundary,
        "last_complete_member": records[-1] if records else None,
        "top_level_central_directory_observed": False,
        "top_level_eocd_observed": False,
        "embedded_signature_locations": signature_locations,
        "standard_zipfile_open": zipfile_result,
        "all_22_binary_science_payloads_complete_and_expected_byte_identical": all_binary_pass,
        "missing_expected_categories": dict(Counter(row["path"].split("/")[0] for row in missing)),
        "missing_relative_paths": [row["path"] for row in missing],
        "missing_expected_payloads": missing,
        "failed_relative_paths": failures,
        "members": records,
        "interpretation": [
            "The downloaded byte extent ends exactly after the 85th complete local-file record; it has no parsed top-level central directory or end-of-central-directory record.",
            "Every present payload passed decompression/stream termination, local CRC32, local length, expected length, expected SHA256, and expected Git blob SHA1 checks.",
            "The 22 expected binary science payloads (16 NPZ, 3 PNG, 3 PDF) are all present and byte-identical to the parent-provided expected identities.",
            "The 62 missing paths are absent relative to the 147-payload recovery plan. This review does not assert that every recovery-plan metadata file necessarily belonged to the originally finalized ZIP.",
            "The file is structurally incomplete as a top-level ZIP. These local bytes do not establish whether the cause was premature snapshot/upload, later truncation, or another delivery/finalization failure.",
            "No byte comparison to a separately available finalized original archive was possible in this review; payload identity is established independently for the 85 present members.",
        ],
        "actions_performed": ["Read source archive and expected plan", "Parse sequential local headers", "Decompress complete member data in memory", "Compute CRC32/SHA256/Git blob SHA1", "Write authorized diagnosis files only when requested"],
        "actions_not_performed": ["Extract scientific unit", "Modify source archive", "Rerun ODE or scientific test suites", "Mutate remote storage or Git", "Change scientific scope or gates"],
        "archive_unchanged_check_sha256": sha256(archive.read_bytes()),
        "scope_preserved": {
            "new_ode_executions_in_this_review": 0,
            "REC126_REI129_warm729_reruns": 0,
            "historical_REI_first_failure_raw": "local-only preservation scope unchanged",
            "Physical": "HOLD", "REC_U5": "HOLD",
            "global_convergence": "NOT_RUN", "production": "NOT_APPROVED",
            "REI_activation": False,
        },
    }
    return report, payloads


def markdown(report: dict) -> str:
    count = report["counts"]
    last = report["last_complete_member"]
    text = [
        "# THERM01 Stage C archive diagnosis", "",
        "**Result: all 22 binary science files are complete and byte-identical to the expected identities. The downloaded top-level ZIP is incomplete.**", "",
        "This bounded recovery review parsed the existing remote bytes without extracting or modifying the scientific unit. It performed no ODE or historical campaign rerun.", "",
        "## Input and byte boundary", "",
        f"- Downloaded archive: `{report['input']['archive']}`",
        f"- Bytes: **{report['input']['bytes']:,}**; original recorded archive length: **{ORIGINAL_RECORDED_BYTES:,}**; difference: **{report['input']['byte_count_shortfall_vs_original_record']:,} bytes**.",
        f"- SHA256: `{ARCHIVE_SHA256}` (unchanged after review).",
        f"- Expected recovery plan: **{count['expected_payloads']} payloads**, SHA256 `{report['input']['expected_payload_list_sha256']}`.",
        f"- Exact EOF: byte offset **{report['boundary']['offset']:,}**, immediately after complete member `{last['path']}`.",
        f"- Last member local header: **{last['local_header_offset']:,}**; compressed data span: **[{last['data_start_offset']:,}, {last['data_end_offset_exclusive']:,})**; compressed length: **{last['compressed_bytes']:,}**; uncompressed length: **{last['uncompressed_bytes']:,}**.",
        "- No top-level central directory or EOCD was encountered in the sequential parse. Embedded `PK` signatures occur inside member data and are not a top-level archive footer.",
        f"- Standard ZIP reader result: `{report['standard_zipfile_open']}`.", "",
        "## Payload verification", "",
        "| Check | Result |", "|---|---:|",
        f"| Complete local members | {count['parsed_complete_members']} |",
        f"| Decompression / CRC32 / local and expected lengths / expected SHA256 / Git blob SHA1 all pass | {count['all_checks_pass_members']} |",
        f"| Identity failures | {count['payload_identity_failures']} |",
        f"| Expected binary science files present and matching | {count['binary_payloads_present_and_matching']} / {count['expected_binary_payloads']} |",
        f"| NPZ / PNG / PDF present and matching | {count['npz_payloads_present_and_matching']} / {count['png_payloads_present_and_matching']} / {count['pdf_payloads_present_and_matching']} |",
        f"| Expected recovery-plan paths absent | {count['expected_payloads_absent']} |", "",
        "The complete binary set includes `solver_return.npz` and `trajectory.npz` for all eight THERM01 cases, plus all three PNG/PDF figure pairs. This is byte preservation evidence; it is not a new scientific execution or a new physics acceptance decision.", "",
        "## Interpretation and recovery limits", "",
        "The observed file is a structurally incomplete ZIP ending at a complete local-member boundary. These bytes do not identify whether an upload captured an unfinalized archive, a later process truncated bytes, or another delivery failure occurred. The review does not infer an upload cause. No separately available finalized original ZIP was compared, so whole-original-archive identity is not asserted.", "",
        "The absent set is measured against the parent-provided 147-payload recovery plan: 2 plot-source CSVs, 59 vendor files, and 1 delivery metadata file. A recovery-plan metadata file need not have belonged to the original finalized archive. Present payload hashes independently match that plan.", "",
        "The optional helper extracts only after every present payload verifies and the destination passes a preflight. Existing regular files must be byte-identical; differing files or symlinks abort. Missing payloads remain missing and must be restored from the independently pinned source. Extraction was **not** run by this review.", "",
        "```bash",
        "python3 recovery/salvage_stage_c.py --extract-to /absolute/path/to/restored/unit",
        "```", "",
        "## Missing relative paths", "",
    ]
    text += [f"- `{path}`" for path in report["missing_relative_paths"]]
    text += ["", "## Scope and gates", "",
             "REC126, REI129, warm729 and previous completed calculations were not rerun. The REI first-failure raw remains within its original local-only preservation scope. Physical/REC U5 HOLD, global convergence NOT_RUN, production NOT_APPROVED and REI_activation=false are unchanged. The prior THERM01 finite acceptance and its source/process limitations are neither broadened nor recomputed by this delivery diagnosis.", "",
             "Per-member offsets, CRC32 results, byte counts, SHA256 values, Git blob SHA1 values, and all 62 missing expected records are in `ARCHIVE_DIAGNOSIS.json`.", ""]
    return "\n".join(text)


def extract_verified(destination: Path, report: dict, payloads: dict[str, bytes]) -> dict:
    if report["counts"]["payload_identity_failures"]:
        raise ValueError("Refusing extraction because a parsed payload failed verification")
    # Check lexical ancestors before resolve: resolving first could conceal a symlink.
    destination = destination.absolute()
    for parent in (destination, *destination.parents):
        if parent.is_symlink():
            raise ValueError(f"Symlink destination/ancestor refused: {parent}")
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"Destination ancestor is not a directory: {parent}")
    destination = destination.resolve()
    writes = []
    identical = []
    for relative, data in payloads.items():
        target = destination.joinpath(*safe_relative(relative).parts)
        for node in (target, *target.parents):
            if node == destination.parent:
                break
            if node.is_symlink():
                raise ValueError(f"Symlink member/ancestor refused: {node}")
            if node != target and node.exists() and not node.is_dir():
                raise ValueError(f"Member ancestor is not a directory: {node}")
        if target.exists():
            if not target.is_file() or target.read_bytes() != data:
                raise ValueError(f"Existing destination differs; no files written: {target}")
            identical.append(relative)
        else:
            writes.append((target, data))
    # No extraction mutations occur until every source and destination passes.
    for target, data in writes:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(data)
        if target.read_bytes() != data:
            raise OSError(f"Post-write byte verification failed: {target}")
    return {"destination": str(destination), "new_files_written": len(writes),
            "existing_identical_files": len(identical),
            "verified_payloads": len(payloads),
            "missing_relative_paths": report["missing_relative_paths"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT / "REMOTE_STAGE_C.zip")
    parser.add_argument("--expected", type=Path, default=ROOT / "EXPECTED_STAGE_C_PAYLOADS.json")
    parser.add_argument("--write-reports", action="store_true")
    parser.add_argument("--extract-to", type=Path)
    args = parser.parse_args()
    report, payloads = inspect(args.archive, args.expected)
    if args.write_reports:
        (ROOT / "ARCHIVE_DIAGNOSIS.json").write_text(json.dumps(report, indent=2) + "\n")
        (ROOT / "ARCHIVE_DIAGNOSIS.md").write_text(markdown(report))
    result = {"status": report["status"], "counts": report["counts"],
              "boundary": report["boundary"],
              "source_archive_sha256": report["input"]["sha256"],
              "extraction_performed": False}
    if args.extract_to is not None:
        result["extraction"] = extract_verified(args.extract_to, report, payloads)
        result["extraction_performed"] = True
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

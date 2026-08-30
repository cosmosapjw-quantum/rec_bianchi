#!/usr/bin/env python3
"""Write the deterministic REC-LOCAL-02 source-authority no-go record."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from full_bianchi_hyrec.trajectory.physical_split_reference import (
    build_rec_local02_diagnostic,
    validate_rec_local02_receipt,
)


DEFAULT_DESTINATION = (
    ROOT
    / "artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local02"
    / "REC_LOCAL_02_EXECUTION.json"
)


def _encoded(result: dict) -> bytes:
    return (
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")


def _check_portable_receipt(path: Path) -> int:
    try:
        stored_bytes = path.read_bytes()
        stored = json.loads(stored_bytes)
        validate_rec_local02_receipt(stored)
        fresh = build_rec_local02_diagnostic(ROOT)
        validate_rec_local02_receipt(fresh)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f"portable receipt validation failed: {exc}", file=sys.stderr)
        return 2
    stored_contract = stored["receipt_contract"]
    fresh_contract = fresh["receipt_contract"]
    fresh_bytes = _encoded(fresh)
    summary = {
        "schema": "REC_LOCAL_02_PORTABLE_RECEIPT_CHECK_V1",
        "portable_authority_match": (
            stored_contract["authority_projection_sha256"]
            == fresh_contract["authority_projection_sha256"]
        ),
        "diagnostic_contract_match": (
            stored_contract["diagnostic_contract_sha256"]
            == fresh_contract["diagnostic_contract_sha256"]
        ),
        "stored_authority_projection_sha256": stored_contract[
            "authority_projection_sha256"
        ],
        "fresh_authority_projection_sha256": fresh_contract[
            "authority_projection_sha256"
        ],
        "stored_diagnostic_contract_sha256": stored_contract[
            "diagnostic_contract_sha256"
        ],
        "fresh_diagnostic_contract_sha256": fresh_contract[
            "diagnostic_contract_sha256"
        ],
        "stored_raw_receipt_sha256": hashlib.sha256(stored_bytes).hexdigest(),
        "fresh_raw_receipt_sha256": hashlib.sha256(fresh_bytes).hexdigest(),
        "raw_receipt_sha256_match": stored_bytes == fresh_bytes,
        "raw_receipt_sha256_role": (
            "ARCHIVAL_PUBLICATION_SEAL_ONLY_NOT_PORTABLE_AUTHORITY"
        ),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if (
        summary["portable_authority_match"]
        and summary["diagnostic_contract_match"]
    ) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--check-portable-receipt", type=Path)
    arguments = parser.parse_args(argv)
    if arguments.check_portable_receipt is not None:
        return _check_portable_receipt(arguments.check_portable_receipt)

    result = build_rec_local02_diagnostic(ROOT)
    validate_rec_local02_receipt(result)
    destination = arguments.output
    if not destination.is_absolute():
        destination = ROOT / destination
    destination = destination.resolve()
    if destination == ROOT:
        raise ValueError("receipt output must be a file path")
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = _encoded(result)
    destination.write_bytes(encoded)
    print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

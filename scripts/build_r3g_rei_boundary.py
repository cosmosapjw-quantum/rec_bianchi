#!/usr/bin/env python3
"""Build a create-only, fail-closed R3g REI boundary packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from full_bianchi_hyrec.trajectory.primordial_rei_interface import (  # noqa: E402
    build_boundary_packet,
    write_packet_create_only,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-manifest", type=Path, required=True)
    parser.add_argument("--target-scenario-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = build_boundary_packet(
        args.history_manifest,
        target_scenario_sha256=args.target_scenario_sha256,
    )
    digest = write_packet_create_only(packet, args.output)
    print(json.dumps({"decision": packet["decision"], "output": str(args.output), "sha256": digest}, sort_keys=True))
    return 0 if packet["decision"] == "REC_SOURCE_BOUNDARY_VALIDATED" else 2


if __name__ == "__main__":
    raise SystemExit(main())

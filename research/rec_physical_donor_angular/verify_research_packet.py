#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_BENCHMARKS = {
    "SMOOTH_QUADRUPOLE",
    "FINITE_BOOST_PATTERN",
    "NARROW_POSITIVE_BEAM",
    "HALF_RANGE_INFLOW_MASK",
    "SIGNED_DISTORTION",
    "REPOSITORY_BIANCHI_FACE_MASK",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    packet = args.packet
    audit = json.loads((packet / "ANGULAR_DONOR_AUDIT.json").read_text())
    receipt = json.loads((packet / "RECEIPT.json").read_text())

    if audit["status"] != "PASS_RESEARCH_AUDIT_NO_PHYSICAL_ADMISSION":
        fail("audit status")
    if audit["authority_effect"] != "NONE_RESEARCH_ONLY":
        fail("authority effect")
    decisions = audit["decisions"]
    if decisions["physical_face_admitted"] is not False:
        fail("physical face self-promotion")
    if decisions["provider_export_authorized"] is not False:
        fail("provider self-promotion")
    if decisions["fixed_26_state_authority_rejected"] is not True:
        fail("fixed 26-vector was not rejected as state authority")

    current = audit["current_rule"]
    if current["point_count"] != 26:
        fail("current point count")
    if current["cubature"]["exact_through_total_degree"] < 5:
        fail("current quadrature fails unexpectedly low polynomial degree")
    if current["l4_full_column_rank"] is not True:
        fail("current grid cannot support the expected L=4 sampling subspace")
    if current["l5_full_column_rank"] is not False:
        fail("26 points incorrectly claimed to span all 36 L<=5 modes")

    benchmarks = {row["benchmark"] for row in audit["grid_benchmarks"]}
    missing = REQUIRED_BENCHMARKS - benchmarks
    if missing:
        fail(f"missing benchmarks: {sorted(missing)}")
    families = {row["family"] for row in audit["grid_benchmarks"]}
    if not {"REPOSITORY_CURRENT", "LEBEDEV", "FIBONACCI_EQUAL_WEIGHT", "GAUSS_LEGENDRE_X_FOURIER"}.issubset(families):
        fail("grid-family coverage")

    if not audit["repository_face_benchmark"].get("available", False):
        fail(f"repository face benchmark unavailable: {audit['repository_face_benchmark']}")

    positive_pn = [row for row in audit["pn_benchmarks"] if row["positive_benchmark"]]
    if not positive_pn:
        fail("no positive PN realizability probes")
    if not any(row["mean_negative_solid_angle_fraction"] > 0 for row in positive_pn):
        fail("PN negativity stress never activated")

    survivor = audit["survivor"]
    if survivor["current_26_is_physical_donor_authority"] is not False:
        fail("survivor promotes fixed 26-vector")
    if "HYBRID" not in survivor["architecture"]:
        fail("survivor is not the selected hybrid architecture")

    if receipt["audit_semantic_sha256"] == "" or len(receipt["audit_semantic_sha256"]) != 64:
        fail("receipt hash")
    if receipt["physical_face_admitted"] is not False:
        fail("receipt physical admission")

    print(json.dumps({
        "status": "PASS",
        "current_point_count": current["point_count"],
        "identified_lebedev_order": current["identified_lebedev_order"],
        "exact_through_degree": current["cubature"]["exact_through_total_degree"],
        "l4_full_rank": current["l4_full_column_rank"],
        "l5_full_rank": current["l5_full_column_rank"],
        "benchmark_count": len(benchmarks),
        "grid_family_count": len(families),
        "fixed_26_state_authority_rejected": True,
        "claim_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

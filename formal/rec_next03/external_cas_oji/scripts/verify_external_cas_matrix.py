#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--receipts-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    receipts: dict[str, dict] = {}
    for path in Path(args.receipts_root).rglob("receipt.json"):
        receipt = json.loads(path.read_text(encoding="utf-8"))
        engine = receipt.get("engine")
        if engine in receipts:
            raise SystemExit(f"duplicate engine receipt: {engine}")
        receipts[engine] = receipt

    errors: list[str] = []
    required = contract["required_engines"]
    if sorted(receipts) != sorted(required):
        errors.append(f"receipt engine set mismatch: {sorted(receipts)}")

    identity_coverage: dict[str, list[str]] = defaultdict(list)
    mutation_coverage: dict[str, list[str]] = defaultdict(list)
    core_engines: list[str] = []
    for engine in required:
        receipt = receipts.get(engine)
        if receipt is None:
            continue
        expected = contract["engine_contracts"][engine]
        if receipt.get("status") != "PASS":
            errors.append(f"{engine} status is not PASS")
        if receipt.get("authority_effect") != "NONE":
            errors.append(f"{engine} changed authority")
        if receipt.get("independence_class") != expected["independence_class"]:
            errors.append(f"{engine} independence class mismatch")
        if not receipt.get("version"):
            errors.append(f"{engine} has no version receipt")
        if not receipt.get("package_hashes"):
            errors.append(f"{engine} has no package hashes")
        observed_ids = set(receipt.get("identities", []))
        observed_mutations = set(receipt.get("mutations", []))
        missing_ids = set(expected["required_identities"]) - observed_ids
        missing_mutations = set(expected["required_mutations"]) - observed_mutations
        if missing_ids:
            errors.append(f"{engine} missing identities {sorted(missing_ids)}")
        if missing_mutations:
            errors.append(f"{engine} missing mutations {sorted(missing_mutations)}")
        for identity in observed_ids:
            identity_coverage[identity].append(engine)
        for mutation in observed_mutations:
            mutation_coverage[mutation].append(engine)
        if expected["counts_as_independent_algebra_core"]:
            core_engines.append(engine)

    minimum_cores = contract["aggregate_acceptance"]["minimum_independent_algebra_cores"]
    if len(core_engines) < minimum_cores:
        errors.append(f"only {len(core_engines)} independent algebra cores")
    if len({receipts[e]["independence_class"] for e in core_engines if e in receipts}) != len(core_engines):
        errors.append("independent cores do not have distinct implementation classes")

    for identity in contract["identity_catalog"]:
        if not identity_coverage.get(identity):
            errors.append(f"identity {identity} has zero execution coverage")
    for identity in contract["aggregate_acceptance"][
        "critical_identities_covered_by_both_independent_cores"
    ]:
        if not set(core_engines).issubset(identity_coverage.get(identity, [])):
            errors.append(f"identity {identity} is not covered by both independent cores")
    minimum_mutation_axes = contract["aggregate_acceptance"][
        "minimum_execution_axes_per_mutation"
    ]
    for mutation in contract["mutation_catalog"]:
        if len(set(mutation_coverage.get(mutation, []))) < minimum_mutation_axes:
            errors.append(
                f"mutation {mutation} has only {sorted(set(mutation_coverage.get(mutation, [])))}"
            )

    result = {
        "schema_version": "1.0.0",
        "stage_id": contract["stage_id"],
        "status": "PASS" if not errors else "FAIL",
        "required_engines": required,
        "independent_algebra_cores": sorted(core_engines),
        "identity_coverage": {k: sorted(v) for k, v in sorted(identity_coverage.items())},
        "mutation_coverage": {k: sorted(v) for k, v in sorted(mutation_coverage.items())},
        "errors": errors,
        "authority_effect": "NONE",
        "claim_boundary": contract["claim_boundary"],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
VALID_TRIGGERS = {"pull_request", "push"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--receipts-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-source-head-sha", required=True)
    parser.add_argument("--expected-workflow-sha", required=True)
    parser.add_argument("--expected-trigger", required=True)
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
    if not GIT_SHA_RE.fullmatch(args.expected_source_head_sha):
        errors.append("expected source_head_sha is not a lowercase 40-hex Git SHA")
    if not GIT_SHA_RE.fullmatch(args.expected_workflow_sha):
        errors.append("expected workflow_sha is not a lowercase 40-hex Git SHA")
    if args.expected_trigger not in VALID_TRIGGERS:
        errors.append(f"unsupported expected trigger: {args.expected_trigger}")
    if (
        args.expected_trigger == "pull_request"
        and args.expected_source_head_sha == args.expected_workflow_sha
    ):
        errors.append(
            "pull_request expected provenance conflates the PR head with the "
            "synthetic workflow merge revision"
        )
    if (
        args.expected_trigger == "push"
        and args.expected_source_head_sha != args.expected_workflow_sha
    ):
        errors.append(
            "push expected provenance requires identical source-head and workflow SHAs"
        )

    required = contract["required_engines"]
    if sorted(receipts) != sorted(required):
        errors.append(f"receipt engine set mismatch: {sorted(receipts)}")

    identity_coverage: dict[str, list[str]] = defaultdict(list)
    mutation_coverage: dict[str, list[str]] = defaultdict(list)
    core_engines: list[str] = []
    observed_source_heads: set[str] = set()
    observed_workflow_shas: set[str] = set()
    observed_triggers: set[str] = set()

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
        if "source_sha" in receipt:
            errors.append(f"{engine} contains forbidden legacy source_sha field")

        source_head_sha = receipt.get("source_head_sha")
        workflow_sha = receipt.get("workflow_sha")
        trigger = receipt.get("trigger")
        if not isinstance(source_head_sha, str) or not GIT_SHA_RE.fullmatch(
            source_head_sha
        ):
            errors.append(f"{engine} has invalid source_head_sha")
        else:
            observed_source_heads.add(source_head_sha)
            if source_head_sha != args.expected_source_head_sha:
                errors.append(
                    f"{engine} source_head_sha mismatch: {source_head_sha} != "
                    f"{args.expected_source_head_sha}"
                )
        if not isinstance(workflow_sha, str) or not GIT_SHA_RE.fullmatch(workflow_sha):
            errors.append(f"{engine} has invalid workflow_sha")
        else:
            observed_workflow_shas.add(workflow_sha)
            if workflow_sha != args.expected_workflow_sha:
                errors.append(
                    f"{engine} workflow_sha mismatch: {workflow_sha} != "
                    f"{args.expected_workflow_sha}"
                )
        if trigger not in VALID_TRIGGERS:
            errors.append(f"{engine} has invalid trigger: {trigger}")
        else:
            observed_triggers.add(trigger)
            if trigger != args.expected_trigger:
                errors.append(
                    f"{engine} trigger mismatch: {trigger} != {args.expected_trigger}"
                )

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

    if observed_source_heads != {args.expected_source_head_sha}:
        errors.append(
            "source_head_sha receipt set is not the single expected exact source: "
            f"{sorted(observed_source_heads)}"
        )
    if observed_workflow_shas != {args.expected_workflow_sha}:
        errors.append(
            "workflow_sha receipt set is not the single expected execution revision: "
            f"{sorted(observed_workflow_shas)}"
        )
    if observed_triggers != {args.expected_trigger}:
        errors.append(
            "trigger receipt set is not the single expected workflow event: "
            f"{sorted(observed_triggers)}"
        )

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
                f"mutation {mutation} has only "
                f"{sorted(set(mutation_coverage.get(mutation, [])))}"
            )

    result = {
        "schema_version": "1.1.0",
        "stage_id": contract["stage_id"],
        "status": "PASS" if not errors else "FAIL",
        "required_engines": required,
        "independent_algebra_cores": sorted(core_engines),
        "identity_coverage": {k: sorted(v) for k, v in sorted(identity_coverage.items())},
        "mutation_coverage": {k: sorted(v) for k, v in sorted(mutation_coverage.items())},
        "provenance": {
            "source_head_sha": args.expected_source_head_sha,
            "workflow_sha": args.expected_workflow_sha,
            "trigger": args.expected_trigger,
            "receipt_source_head_shas": sorted(observed_source_heads),
            "receipt_workflow_shas": sorted(observed_workflow_shas),
            "receipt_triggers": sorted(observed_triggers),
        },
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

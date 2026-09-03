#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

IDENTITY_RE = re.compile(r"^IDENTITY\s+(I\d{2})\s+PASS\s*$", re.MULTILINE)
MUTATION_RE = re.compile(r"^MUTATION\s+(M\d{2})\s+DETECTED\s*$", re.MULTILINE)
STATUS_RE = re.compile(r"^STATUS\s+(PASS|FAIL)\s*$", re.MULTILINE)
SHA_RE = re.compile(r"^([0-9a-f]{64})\s+(.+?)\s*$", re.MULTILINE)
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
VALID_TRIGGERS = {"pull_request", "push"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--hashes", required=True)
    parser.add_argument("--engine-exit-code", required=True, type=int)
    parser.add_argument("--source-head-sha", required=True)
    parser.add_argument("--workflow-sha", required=True)
    parser.add_argument("--trigger", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    engine_contract = contract["engine_contracts"][args.engine]
    log_text = Path(args.log).read_text(encoding="utf-8", errors="replace")
    version_text = Path(args.version).read_text(encoding="utf-8", errors="replace").strip()
    hashes_text = Path(args.hashes).read_text(encoding="utf-8", errors="replace")

    identities = sorted(set(IDENTITY_RE.findall(log_text)))
    mutations = sorted(set(MUTATION_RE.findall(log_text)))
    status_markers = STATUS_RE.findall(log_text)
    package_hashes = [
        {"sha256": digest, "artifact": name.strip()}
        for digest, name in SHA_RE.findall(hashes_text)
    ]

    missing_identities = sorted(set(engine_contract["required_identities"]) - set(identities))
    missing_mutations = sorted(set(engine_contract["required_mutations"]) - set(mutations))
    errors: list[str] = []
    if args.engine_exit_code != 0:
        errors.append(f"engine exit code {args.engine_exit_code}")
    if status_markers != ["PASS"]:
        errors.append(f"expected one STATUS PASS marker, observed {status_markers}")
    if missing_identities:
        errors.append(f"missing identities: {missing_identities}")
    if missing_mutations:
        errors.append(f"missing mutations: {missing_mutations}")
    if not version_text:
        errors.append("empty version receipt")
    if not package_hashes:
        errors.append("no package or lock SHA-256 receipts")
    if not GIT_SHA_RE.fullmatch(args.source_head_sha):
        errors.append("source_head_sha is not a lowercase 40-hex Git SHA")
    if not GIT_SHA_RE.fullmatch(args.workflow_sha):
        errors.append("workflow_sha is not a lowercase 40-hex Git SHA")
    if args.trigger not in VALID_TRIGGERS:
        errors.append(f"unsupported workflow trigger: {args.trigger}")
    if args.trigger == "pull_request" and args.source_head_sha == args.workflow_sha:
        errors.append(
            "pull_request provenance requires the exact PR head to be distinct "
            "from the synthetic workflow merge revision"
        )
    if args.trigger == "push" and args.source_head_sha != args.workflow_sha:
        errors.append(
            "push provenance requires source_head_sha and workflow_sha to be identical"
        )

    provenance_relation = (
        "PULL_REQUEST_HEAD_DISTINCT_FROM_WORKFLOW_REVISION"
        if args.trigger == "pull_request" and args.source_head_sha != args.workflow_sha
        else "DIRECT_PUSH_COMMIT"
    )

    receipt = {
        "schema_version": "1.1.0",
        "stage_id": contract["stage_id"],
        "engine": args.engine,
        "status": "PASS" if not errors else "FAIL",
        "engine_exit_code": args.engine_exit_code,
        "source_head_sha": args.source_head_sha,
        "workflow_sha": args.workflow_sha,
        "trigger": args.trigger,
        "provenance_relation": provenance_relation,
        "independence_class": engine_contract["independence_class"],
        "counts_as_independent_algebra_core": engine_contract[
            "counts_as_independent_algebra_core"
        ],
        "identities": identities,
        "mutations": mutations,
        "missing_identities": missing_identities,
        "missing_mutations": missing_mutations,
        "version": version_text,
        "package_hashes": package_hashes,
        "errors": errors,
        "authority_effect": "NONE",
        "claim_boundary": contract["claim_boundary"],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

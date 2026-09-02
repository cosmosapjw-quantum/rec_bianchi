#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregate", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    aggregate = json.loads(Path(args.aggregate).read_text(encoding="utf-8"))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    identities = sorted(aggregate["identity_coverage"])
    mutations = sorted(aggregate["mutation_coverage"])
    identity_counts = [len(set(aggregate["identity_coverage"][key])) for key in identities]
    mutation_counts = [len(set(aggregate["mutation_coverage"][key])) for key in mutations]

    with (output / "coverage.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["kind", "id", "execution_axis_count"])
        writer.writerows(("identity", key, count) for key, count in zip(identities, identity_counts))
        writer.writerows(("mutation", key, count) for key, count in zip(mutations, mutation_counts))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(identities, identity_counts)
    ax.set_ylabel("Execution axes reporting PASS")
    ax.set_title("REC-NEXT-03 external CAS identity coverage")
    ax.set_ylim(0, max(identity_counts + [1]) + 0.7)
    for index, value in enumerate(identity_counts):
        ax.text(index, value + 0.05, str(value), ha="center")
    fig.tight_layout()
    fig.savefig(output / "identity_coverage.png", dpi=180)
    fig.savefig(output / "identity_coverage.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.bar(mutations, mutation_counts)
    ax.set_ylabel("Execution axes detecting mutation")
    ax.set_title("REC-NEXT-03 hostile-mutation coverage")
    ax.set_ylim(0, max(mutation_counts + [1]) + 0.7)
    for index, value in enumerate(mutation_counts):
        ax.text(index, value + 0.05, str(value), ha="center")
    fig.tight_layout()
    fig.savefig(output / "mutation_coverage.png", dpi=180)
    fig.savefig(output / "mutation_coverage.svg")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

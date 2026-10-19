#!/usr/bin/env python3
"""Plot retained method differences. This script performs no ODE integration."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = args.primary.read_bytes()
    source = json.loads(data)
    d = source["diagnostic"]
    if (d["classification"] != "EXPLORATORY_METHOD_COMPARISON"
            or d["same_algorithm_parity"] is not False
            or d["production_admission"] is not False):
        raise ValueError("EXPECTED_SEPARATE_EXPLORATORY_DIAGNOSTIC")
    rows = d["comparisons_with_python_fixed_h2"]
    if len(rows) != source["input"]["steps"]+1 or any(r["admission_test"] is not False for r in rows):
        raise ValueError("INCOMPLETE_OR_MISCLASSIFIED_COMPARISON")
    x = [r["tau"]/source["h2"] for r in rows]
    y = [[r["scaled_state_residual"][j] for r in rows] for j in (0, 1)]
    if any(not math.isfinite(v) or v < 0 for line in y for v in line):
        raise ValueError("INVALID_RETAINED_DIFFERENCE")
    args.output.mkdir(parents=True, exist_ok=False)
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    for values, label, color in zip(y, ("Electron fraction xe", "Matter temperature Tm"),
                                    ("#225ea8", "#d95f0e")):
        ax.semilogy(x, values, "o-", label=label, color=color,
                    linewidth=1.8, markersize=4)
    ax.axhline(1., color="#9c2525", linestyle="--", linewidth=1.3,
               label="Original same-h threshold (reference only)")
    ax.set(xlabel="Accepted output index after U6 boundary (tau / h2)",
           ylabel="RODAS5P vs Python fixed h2 / frozen same-h tolerance",
           title="VigilODE method diagnostic: same C operator, different integrator",
           xlim=(-.3, len(rows)-.7), ylim=(1.e-7, 5.))
    ax.grid(alpha=.2, which="both")
    ax.legend(loc="lower right", frameon=True)
    fig.text(.5, .025,
             f"Rust original predictor vs original C: {6*len(rows)} scalar byte checks MATCH.\n"
             "RODAS5P is exploratory; these differences do not establish convergence or production equivalence.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .09, 1, 1))
    for suffix in ("png", "pdf"):
        fig.savefig(args.output/f"r3o_rust_method_difference.{suffix}", dpi=150)
    plt.close(fig)
    if args.primary.read_bytes() != data:
        raise ValueError("INPUT_MUTATED_DURING_PLOT")
    record = {"schema": "rec.r3o.rust-figure.v1", "primary_sha256": hashlib.sha256(data).hexdigest(),
              "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "new_numerical_steps": 0, "max_ratio": [max(v) for v in y],
              "output_rows": len(rows), "classification": d["classification"],
              "files": {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                        for p in sorted(args.output.iterdir())}}
    (args.output/"figure.json").write_text(json.dumps(record, indent=2)+"\n")
    print(json.dumps(record))


if __name__ == "__main__":
    main()

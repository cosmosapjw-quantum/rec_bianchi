#!/usr/bin/env python3
"""Small analytic-ODE controls for the ORIGINAL predictor; no HyRec integration."""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
import numpy as np
from full_bianchi_hyrec.trajectory.time_convergence import (
    H0, X0, SOURCE_ZIP_SHA256, GridHistory, compare_histories, grid_step,
)


def integrate_manufactured(level, *, wrong_lag=False, shared_bias=0.):
    """y'=-200y, y(0)=1+bias; analytic past for the SAME initial condition."""
    h = grid_step(level)
    n = 64*2**level
    y = 1.+shared_bias
    prev2, prev = -200.*y*math.exp(400.*h), -200.*y*math.exp(200.*h)
    states = [y]
    for _ in range(n):
        current = -200.*y
        y += h*(1.25*current-.25*(prev if wrong_lag else prev2))
        prev2, prev = prev, current
        states.append(y)
    return np.asarray(states)


def history(level, values):
    g = np.arange(30000*2**level, 30000*2**level+len(values), dtype=np.int64)
    v = {"xe": values, "Tm_K": 2000.*values}
    zeros = {k: np.zeros(len(g)) for k in v}
    p = {"kind": "manufactured", "checkpoint_resampled": False,
         "q": 0, "REI_activation": False, "source_zip_sha256": SOURCE_ZIP_SHA256,
         "physics_id": "analytic_y_prime_minus_200_y",
         "boundary_coverage_lna": [X0, 0.],
         "uncertainty_basis": "synthetic mathematical control; no physical same-h C run"}
    return GridHistory(level, g, v, zeros, zeros, np.full(len(g), "MANUFACTURED"), (), p)


def run(out: Path, *, plots=True):
    try:
        out.mkdir(parents=True, exist_ok=False)
    except FileExistsError as e:
        raise ValueError("OUTPUT_EXISTS_PRESERVE_PRIOR_EVIDENCE") from e
    start_cpu, start_wall = time.process_time(), time.monotonic()
    targets = X0+H0*np.arange(30003., 30063.)
    results, diagnostics = {}, {}
    exact_final = math.exp(-200.*64.*H0)
    for label, options in (("original_prev2", {}), ("mutated_prev1", {"wrong_lag": True}),
                            ("shared_checkpoint_bias", {"shared_bias": .01})):
        arrays = [integrate_manufactured(k, **options) for k in (0, 1, 2)]
        diag = compare_histories([history(k, a) for k, a in enumerate(arrays)], targets)
        errors = [abs(float(a[-1])-exact_final) for a in arrays]
        ps = [r["fields"]["xe"]["p_observed"] for r in diag["rows"]
              if r["fields"]["xe"]["p_observed"] is not None]
        results[label] = {"endpoint_absolute_error": errors,
            "endpoint_error_order": [math.log2(errors[i]/errors[i+1]) for i in (0, 1)],
            "median_observed_difference_order": float(np.median(ps)),
            "original_numeric_gate_status": diag["regions"]["available_domain"]["status"],
            "scope": "MANUFACTURED_CONTROL_NOT_RECOMBINATION"}
        diagnostics[label] = diag
    # Probe the independent characteristic polynomial, not a HyRec Jacobian.
    stability = {}
    for z in (-2.1, -2., -1.9, -.1, 0.):
        roots = np.roots([1., -1.-1.25*z, 0., .25*z])
        stability[str(z)] = {"roots": [[float(r.real), float(r.imag)] for r in roots],
                             "max_modulus": float(max(abs(roots)))}
    checks = {
        "original_endpoint_order_near_2": all(1.9 < p < 2.1 for p in results["original_prev2"]["endpoint_error_order"]),
        "wrong_memory_order_near_1": all(.9 < p < 1.1 for p in results["mutated_prev1"]["endpoint_error_order"]),
        "common_bias_survives_h_refinement": min(results["shared_checkpoint_bias"]["endpoint_absolute_error"]) > .009*exact_final,
        "common_bias_hidden_from_signed_order": abs(results["shared_checkpoint_bias"]["median_observed_difference_order"]-
                                                    results["original_prev2"]["median_observed_difference_order"]) < 1.e-6,
        "scalar_minus_1p9_inside": stability["-1.9"]["max_modulus"] < 1.,
        "scalar_minus_2p1_outside": stability["-2.1"]["max_modulus"] > 1.,
    }
    result = {"schema": "rec.r3n.predictor-probes.v1", "status": "PASS_SCOPED" if all(checks.values()) else "FAIL",
              "model": "dy/ds=-200y; s=ln(a)-ln(a_start); exact same-grid -h,-2h derivatives; biased case starts from y(0)=1.01 instead of 1",
              "step_sizes": [grid_step(k) for k in (0, 1, 2)], "steps": [64, 128, 256],
              "new_physical_integrations": 0, "three_grid_recombination": "NOT_RUN",
              "cases": results, "scalar_stability_probe": stability, "checks": checks}
    if plots:
        os.environ.setdefault("MPLCONFIGDIR", str(out.resolve()/"mpl_cache"))
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.3), constrained_layout=True)
        colors = {"original_prev2": "#176d9c", "mutated_prev1": "#bf5228", "shared_checkpoint_bias": "#7957a4"}
        labels = {"original_prev2": "Original f[n-2] memory", "mutated_prev1": "Mutation: f[n-1] memory", "shared_checkpoint_bias": "Original + shared 1% initial bias"}
        for name, record in results.items():
            ax[0].loglog([1., .5, .25], record["endpoint_absolute_error"], "o-", label=labels[name], color=colors[name])
            rs = diagnostics[name]["rows"]
            ax[1].plot([(r["lna"]-(X0+H0*30000))/(64*H0) for r in rs],
                       [r["fields"]["xe"]["p_observed"] for r in rs], color=colors[name], label=labels[name])
        ax[0].set(xlabel="h / original h", ylabel="Endpoint error vs exp(-200 s)", title="Actual analytic-ODE executions")
        ax[0].invert_xaxis(); ax[0].legend(fontsize=8)
        ax[1].set(xlabel="Fraction of test interval", ylabel="Signed-difference order", title="Shared bias is invisible to Richardson differences")
        for a in ax: a.grid(True, which="both", alpha=.2)
        fig.suptitle("Manufactured controls only — no recombination convergence claim", fontsize=11)
        with (out/"R3N_NUMERICAL_PROBES.png").open("xb") as f:
            fig.savefig(f, format="png", dpi=170)
        with (out/"R3N_NUMERICAL_PROBES.pdf").open("xb") as f:
            fig.savefig(f, format="pdf")
        plt.close(fig)
    result["cpu_s"] = time.process_time()-start_cpu
    result["wall_s"] = time.monotonic()-start_wall
    with (out/"result.json").open("x") as f:
        f.write(json.dumps(result, indent=2, allow_nan=False)+"\n")
    with (out/"diagnostics.json").open("x") as f:
        f.write(json.dumps(diagnostics, indent=2, allow_nan=False)+"\n")
    print(json.dumps(result, indent=2))
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence-dir", type=Path, required=True)
    p.add_argument("--no-plots", action="store_true")
    a = p.parse_args(argv)
    return 0 if run(a.evidence_dir, plots=not a.no_plots)["status"] == "PASS_SCOPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

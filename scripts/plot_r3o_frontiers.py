#!/usr/bin/env python3
"""A bounded affine predictor-memory probe, attached to actual R3O inputs.

The ODE below is a manufactured scalar diagnostic, not a recombination run.
Saved original-h and R3M h2 states are only loaded and compared for coverage.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
from compare_r3n_time_grids import compare_histories, dump, empty_output, grid_step, load_history, sha

DEFAULT_H = ROOT / "research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/h_state_trace.json"
DEFAULT_H2 = ROOT / "research/rec_r3n_time_convergence_20261019/real_h2_trace_003/h2_state_trace.json"


def affine_probe(steps: int = 12) -> dict:
    if type(steps) is not int or not 2 <= steps <= 32:
        raise ValueError("BOUNDED_PROBE_REQUIRES_2_TO_32_STEPS")
    h, lam, forcing, y0 = grid_step(1), -200., 100., 1.
    equilibrium = -forcing / lam
    exact = lambda k: equilibrium + (y0 - equilibrium) * math.exp(lam * h * k)
    rhs = lambda y: lam * y + forcing
    prev2, prev = rhs(exact(-2)), rhs(exact(-1))

    def evolve(seed2, seed1):
        state, old2, old1 = y0, seed2, seed1
        states = [state]
        for _ in range(steps):
            current = rhs(state)
            state = state + h * (1.25 * current - .25 * old2)
            old2, old1 = old1, current
            states.append(state)
        return np.array(states)

    baseline = evolve(prev2, prev)
    cases = {}
    settings = {"prev2_plus_delta": (1., 0.), "prev_plus_delta": (0., 1.),
                "reset_both_to_current": (rhs(y0) - prev2, rhs(y0) - prev)}
    for name, (delta2, delta1) in settings.items():
        mutated = evolve(prev2 + delta2, prev + delta1)
        observed = mutated - baseline
        # Independent exact rational solution for the affine difference equation.
        hh, ll = Fraction(h), Fraction(lam)
        alpha = 1 + Fraction(5, 4) * hh * ll
        errors = [Fraction(0), -hh * Fraction(delta2) / 4]
        errors.append(alpha * errors[1] - hh * Fraction(delta1) / 4)
        for k in range(2, steps):
            errors.append(alpha * errors[k] - hh * ll * errors[k - 2] / 4)
        predicted = np.array([float(x) for x in errors])
        discrepancy = float(np.max(np.abs(observed - predicted)))
        allowed = 64. * np.finfo(float).eps * max(1., float(np.max(np.abs(mutated))))
        if discrepancy > allowed:
            raise ArithmeticError("AFFINE_MEMORY_RESPONSE_DISAGREES_WITH_RATIONAL_REFERENCE")
        cases[name] = {"delta_prev2": delta2, "delta_prev": delta1,
                       "seed_scale": max(abs(delta2), abs(delta1)),
                       "state": mutated.tolist(), "observed_difference": observed.tolist(),
                       "rational_predicted_difference": predicted.tolist(),
                       "max_abs_reference_discrepancy": discrepancy, "floating_comparison_allowance": allowed,
                       "first_step_expected": -h * delta2 / 4.,
                       "second_step_expected": float(alpha) * (-h * delta2 / 4.) - h * delta1 / 4.}
    return {"kind": "manufactured_affine_scalar", "equation": "dy/dln(a) = lambda*y + forcing",
            "h": h, "lambda": lam, "forcing": forcing, "y0": y0, "steps": steps,
            "seed_order": ["prev2 owns -2", "prev owns -1"],
            "baseline_seeds": {"prev2": prev2, "prev": prev},
            "baseline": baseline.tolist(), "exact_ode": [exact(k) for k in range(steps + 1)],
            "cases": cases, "all_three_rational_response_checks": "PASS",
            "hyrec_integrations": 0, "interpretation": "Finite-step seed-memory response; no physical time-convergence admission"}


def draw_probe(probe: dict, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "legend.fontsize": 8,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 1, figsize=(3.54, 5.5), layout="constrained")
    step = np.arange(probe["steps"] + 1)
    for name, label, color, marker in (("prev2_plus_delta", "prev2 + delta", "#2166ac", "o"),
                                        ("prev_plus_delta", "prev + delta", "#b35806", "s")):
        case = probe["cases"][name]
        values = np.array(case["observed_difference"]) / (probe["h"] * case["seed_scale"])
        axes[0].plot(step, values, color=color, marker=marker, markersize=3.4, label=label)
    axes[0].set_title("(a) One memory entry perturbed", loc="left")
    axes[0].legend(loc="upper right", frameon=False)
    case = probe["cases"]["reset_both_to_current"]
    scale = probe["h"] * case["seed_scale"]
    axes[1].plot(step, np.array(case["rational_predicted_difference"]) / scale,
                 color="0.25", linewidth=1.5, label="Rational response")
    axes[1].plot(step, np.array(case["observed_difference"]) / scale,
                 color="#762a83", marker="o", markerfacecolor="none", linestyle="none",
                 markersize=4.2, label="Computed difference")
    axes[1].set_title("(b) Both memories reset to current RHS", loc="left")
    axes[1].legend(loc="upper right", frameon=False)
    for ax in axes:
        ax.axhline(0., color="0.7", linewidth=.7)
        ax.set_xlabel("Accepted scalar updates")
        ax.set_ylabel("State difference / (h × seed scale)")
        ax.set_xticks(np.arange(0, probe["steps"] + 1, 2))
        ax.grid(alpha=.18)
    for extension in ("png", "pdf"):
        with (out / ("predictor_memory_seed_response." + extension)).open("xb") as f:
            fig.savefig(f, format=extension, dpi=200)
    plt.close(fig)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--h-history", type=Path, default=DEFAULT_H)
    parser.add_argument("--h2-history", type=Path, default=DEFAULT_H2)
    args = parser.parse_args(argv)
    empty_output(args.evidence_dir)
    started = time.monotonic()
    try:
        descriptors = [args.h_history, args.h2_history]
        before = {str(p.resolve()): sha(p) for p in descriptors}
        histories = [load_history(p) for p in descriptors]
        coverage = compare_histories(histories)
        if coverage["status"] != "INSUFFICIENT_LEVELS" or coverage["levels_missing"] != [2]:
            raise ValueError("EXPECTED_REUSED_H_AND_H2_ONLY")
        probe = affine_probe()
        dump(args.evidence_dir / "probe.json", probe)
        dump(args.evidence_dir / "h_h2_coverage.json", coverage)
        draw_probe(probe, args.evidence_dir)
        if {str(p.resolve()): sha(p) for p in descriptors} != before:
            raise ValueError("INPUT_DESCRIPTOR_MUTATION_DURING_PROBE")
        result = {"status": "AFFINE_MEMORY_PROBE_PASS", "scalar_trajectories": 4,
                  "updates_per_trajectory": probe["steps"], "new_hyrec_integrations": 0,
                  "reference": "exact rational affine difference response",
                  "max_abs_reference_discrepancy": max(c["max_abs_reference_discrepancy"] for c in probe["cases"].values()),
                  "h_h2_comparison": coverage["status"], "levels_missing": [2],
                  "h_nodewise_C_parity": "UNKNOWN", "h2_full_lowz_153327": "NOT_RUN",
                  "h4_eight_step_start": "EXISTING_IMPLEMENTATION_EVIDENCE_PENDING_PARENT_DUAL_REVIEW",
                  "preserve": coverage["preserve"], "descriptor_sha256": before,
                  "scientific_admission": "NOT_ESTABLISHED_BY_PROBE"}
        dump(args.evidence_dir / "result.json", result)
        code = 0
    except Exception as e:
        result = {"status": "PROBE_OR_INPUT_ERROR", "error": str(e)}
        dump(args.evidence_dir / "failure.json", {"type": type(e).__name__, "message": str(e)})
        code = 2
    record = {"command": sys.argv if argv is None else argv, "exit_code": code,
              "status": result["status"], "cpu_process_s": time.process_time(),
              "wall_s": time.monotonic() - started, "python": sys.version, "numpy": np.__version__,
              "location": "caller environment; parent receipt identifies actual sandbox run",
              "files": {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)}
                        for p in sorted(args.evidence_dir.iterdir()) if p.is_file()}}
    dump(args.evidence_dir / "execution.json", record)
    print(json.dumps({"status": result["status"], "exit_code": code,
                      "cpu_process_s": record["cpu_process_s"]}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

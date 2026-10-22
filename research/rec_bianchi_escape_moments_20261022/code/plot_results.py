#!/usr/bin/env python3
"""Render at most three figures from saved ANGULAR01 measurements; no quadratures."""
from __future__ import annotations

import os
for _angular_thread_option in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_angular_thread_option] = "1"
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np


UNIT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_csv(path, rows):
    with path.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def positive_plot(values):
    values = np.asarray(values, dtype=float)
    return np.where(values > 0.0, values, np.nan)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", default="attempt_001")
    args = parser.parse_args()
    result_dir = UNIT / "results" / args.attempt
    summary = json.loads((result_dir / "study_summary.json").read_text())
    decision_path = result_dir / "FINAL_DECISION.json"
    decision = json.loads(decision_path.read_text()) if decision_path.exists() else None
    accepted = summary["status"] == "PASS" or (
        decision is not None and decision["status"] == "PASS"
        and decision["source_grid_sha256"] == digest(result_dir / "grid.csv")
        and decision["accepted_grid_points"] == 405)
    if not accepted or summary["grid_points_completed"] != 405:
        raise RuntimeError("Final figures require completed 405-point measurements and their bound acceptance record")
    with (result_dir / "grid.csv").open(newline="") as handle:
        raw = list(csv.DictReader(handle))
    names = list(dict.fromkeys(row["spectrum"] for row in raw))
    groups = {name: [row for row in raw if row["spectrum"] == name] for name in names}
    output = UNIT / "figures" / args.attempt
    output.mkdir(parents=True, exist_ok=False)
    tables = result_dir / "plotted_data"
    tables.mkdir(exist_ok=False)
    scalar_rows, tensor_rows, branch_rows = [], [], []
    for row in raw:
        name, t = row["spectrum"], float(row["t"])
        mean = float(row["B128"])
        log_bound = float(row["log_thick_relative_B_bound"])
        bound = math.exp(log_bound) if log_bound < 709.0 else math.inf
        scalar_rows.append({"spectrum": name, "t": t,
                            "scalar_suppression": float(row["scalar_suppression"]),
                            "thick_scalar_relative_error": abs(float(row["thick_B_absolute_defect"])) / mean,
                            "analytic_relative_bound": bound if bound > 0.0 and math.isfinite(bound) else None,
                            "log_analytic_relative_bound": log_bound,
                            "representation": "LOG_ONLY" if bound == 0.0 or not math.isfinite(bound) else "FLOAT_APPROXIMATION"})
        tensor_rows.append({"spectrum": name, "t": t,
                            "Q_F_over_B": float(row["Q_F_over_B"]),
                            "Qxx": float(row["Qxx"]), "Qyy": float(row["Qyy"]), "Qzz": float(row["Qzz"]),
                            "thick_Q_F_over_B_limit": (2.0 / 15.0) * math.sqrt(sum(float(row[k]) ** 2 for k in ("lambda_1", "lambda_2", "lambda_3"))),
                            "LRS_signed_a2": 7.5 * float(row["Qzz"]) / mean if row["lrs_s"] else None,
                            "LRS_s": float(row["lrs_s"]) if row["lrs_s"] else None})
        branch_rows.append({"spectrum": name, "t": t, "qmin": float(row["qmin"]),
                            "qmax": float(row["qmax"]), "tau_min": t / float(row["qmax"]),
                            "auto_eligible": row["auto_eligible"] == "True", "method": row["auto_method"],
                            "threshold_tau_min": math.log1p(1.0e8),
                            "threshold_t": float(row["qmax"]) * math.log1p(1.0e8),
                            "log_analytic_relative_bound": log_bound})
    scalar_csv, tensor_csv, branch_csv = tables / "physical_bounds.csv", tables / "surviving_tensor.csv", tables / "branch_map.csv"
    save_csv(scalar_csv, scalar_rows)
    save_csv(tensor_csv, tensor_rows)
    save_csv(branch_csv, branch_rows)
    plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.25,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "figure.constrained_layout.use": True, "pdf.fonttype": 42})
    palette = plt.get_cmap("tab10")
    colors = {name: palette(i) for i, name in enumerate(names)}
    labels = {"isotropic": "Isotropic", "LRS_m0p8": "LRS s=-0.8", "LRS_m0p2": "LRS s=-0.2",
              "LRS_p0p2": "LRS s=0.2", "LRS_p0p8": "LRS s=0.8", "LRS_p1p8": "LRS s=1.8",
              "triaxial_A": "Triaxial A", "triaxial_B": "Triaxial B", "triaxial_C": "Triaxial C"}
    created = []

    def save_figure(fig, name):
        for suffix in ("png", "pdf"):
            path = output / (name + "." + suffix)
            fig.savefig(path, dpi=170, metadata={"Creator": "ANGULAR01 saved-data renderer"})
            created.append(path)
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6))
    selected = ("LRS_m0p8", "LRS_p0p8", "LRS_p1p8", "triaxial_C")
    for name in selected:
        rows = [r for r in scalar_rows if r["spectrum"] == name]
        t = [r["t"] for r in rows]
        axes[0].semilogx(t, [r["scalar_suppression"] for r in rows], color=colors[name], label=labels[name])
        axes[1].loglog(t, positive_plot([r["thick_scalar_relative_error"] for r in rows]), color=colors[name], label=labels[name])
        axes[1].loglog(t, positive_plot([r["analytic_relative_bound"] or 0.0 for r in rows]), color=colors[name], linestyle="--", alpha=0.75)
    axes[0].set(xlabel=r"Mean optical-depth parameter $t=C/H$", ylabel=r"$[\beta_{\rm iso}(t)-B]/\beta_{\rm iso}(t)$",
                title="Finite-depth scalar suppression", xlim=(1.0e-8, 1.0e3))
    axes[0].legend(fontsize=9)
    axes[1].axhline(1.0e-8, color="black", linestyle=":", label="AUTO target")
    axes[1].set(xlabel=r"$t=C/H$", ylabel=r"$|1/t-B|/B$", title="Measured defect and analytic upper bound",
                xlim=(0.1, 1.0e3), ylim=(1.0e-17, 20.0))
    axes[1].text(0.03, 0.04, "Solid: saved quadrature comparison\nDashed: analytic truncation bound\nZero/underflow values are not plotted", transform=axes[1].transAxes, fontsize=8,
                 bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"})
    fig.suptitle("ANGULAR01 — supplied local isotropic-source operator")
    save_figure(fig, "physical_bounds")

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6))
    for name in names[1:]:
        rows = [r for r in tensor_rows if r["spectrum"] == name]
        t = [r["t"] for r in rows]
        axes[0].semilogx(t, [r["Q_F_over_B"] for r in rows], color=colors[name], label=labels[name])
        axes[0].plot([100.0, 1000.0], [rows[0]["thick_Q_F_over_B_limit"]] * 2,
                     linestyle="--", color=colors[name], linewidth=1.1)
        if name.startswith("LRS"):
            axes[1].semilogx(t, [r["LRS_signed_a2"] for r in rows], color=colors[name], label=labels[name])
            axes[1].plot([100.0, 1000.0], [rows[0]["LRS_s"]] * 2,
                         linestyle="--", color=colors[name], linewidth=1.1)
    axes[0].set(xlabel=r"$t=C/H$", ylabel=r"$\|Q\|_F/B$", title="Escape quadrupole survives the thick limit", xlim=(1.0e-8, 1.0e3))
    axes[0].legend(fontsize=8, ncol=2)
    axes[1].axhline(0.0, color="black", linewidth=0.6)
    axes[1].set(xlabel=r"$t=C/H$", ylabel=r"$5\langle P_2\beta\rangle/B=7.5\,Q_{zz}/B$",
                title="Signed LRS amplitude tends to s", xlim=(1.0e-8, 1.0e3))
    axes[1].legend(fontsize=8)
    fig.suptitle("Probability moments; no stress tensor or cosmological history is inferred")
    save_figure(fig, "surviving_tensor")

    fig, ax = plt.subplots(figsize=(11.0, 5.1))
    matrix = np.array([[int(r["auto_eligible"]) for r in branch_rows if r["spectrum"] == name] for name in names])
    log_t = np.log10([float(r["t"]) for r in groups[names[0]]])
    edges = np.r_[log_t[0] - 0.125, 0.5 * (log_t[:-1] + log_t[1:]), log_t[-1] + 0.125]
    cmap = ListedColormap(["#edf2f7", "#197a78"])
    ax.pcolormesh(edges, np.arange(len(names) + 1) - 0.5, matrix,
                  cmap=cmap, norm=BoundaryNorm([-0.5, 0.5, 1.5], cmap.N), shading="flat")
    boundaries = [math.log10(next(r["threshold_t"] for r in branch_rows if r["spectrum"] == name)) for name in names]
    ax.plot(boundaries, np.arange(len(names)), "o", color="#e28522", markersize=5,
             label=r"Analytic boundary $t=q_{\max}\log(1+1/\epsilon)$")
    ax.set(yticks=np.arange(len(names)), yticklabels=[labels[name] for name in names],
           xlabel=r"$\log_{10}(t)$", title=r"AUTO branch map, $\epsilon=10^{-8}$",
           xlim=(log_t[0] - 0.125, log_t[-1] + 0.125), ylim=(-0.5, len(names) - 0.5))
    ax.grid(False)
    ax.legend(loc="upper left", fontsize=9)
    fig.text(0.5, 0.005, "Light: finite quadrature branch  |  Teal: analytic thick truncation gate met\n405 fixed parameter points; no IVPs; finite differences do not certify quadrature error", ha="center", fontsize=9)
    save_figure(fig, "branch_map")
    files = [scalar_csv, tensor_csv, branch_csv, *created]
    manifest = {"unit": "ANGULAR01", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "source_grid": {"path": str((result_dir / "grid.csv").relative_to(UNIT)), "sha256": digest(result_dir / "grid.csv"), "rows": len(raw)},
                "renderer_sha256": digest(__file__), "figure_count": 3,
                "initial_study_status": summary["status"],
                "final_decision_sha256": digest(decision_path) if decision_path.exists() else None,
                "new_quadratures": 0, "new_IVPs": 0,
                "files": [{"path": str(p.relative_to(UNIT)), "bytes": p.stat().st_size, "sha256": digest(p)} for p in files],
                "plotting_notes": ["All plotted arrays are preserved as CSV.", "Nonpositive log-axis values are omitted rather than clipped to an artificial floor.", "Analytic truncation bounds are not interval certificates for floating arithmetic."]}
    (result_dir / "PLOT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"figure_count": 3, "files": len(files), "source_rows": len(raw), "output": str(output)}))


if __name__ == "__main__":
    main()

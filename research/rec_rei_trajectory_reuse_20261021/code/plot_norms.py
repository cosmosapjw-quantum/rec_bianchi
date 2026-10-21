#!/usr/bin/env python3
"""Display the requested nonnegative Sigma/Pi norms from saved trajectories.

No IVP, fit, parameter interpolation, floor, or jitter is used.  The total
stress is the absolute value of the signed matter-plus-radiation sum.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


BASE = Path(__file__).resolve().parents[1]
LINTHRESH = 1e-10
ENDPOINT_SIGMA_LINTHRESH = 1e-6
INK = "#263647"
HISTORY_COLORS = ("#777777", "#0072B2", "#D55E00", "#009E73", "#A751A6")
GRID_COLORS = ("#4C4C4C", "#332288", "#88CCEE", "#44AA99", "#DDCC77", "#CC6677", "#882255")


def case_index(axes: np.ndarray, values: tuple[float, float, float]) -> int:
    found = np.flatnonzero(np.all(np.isclose(axes, values, rtol=0, atol=1e-15), axis=1))
    if len(found) != 1:
        raise ValueError(f"Expected one nominal case at {values}; found {len(found)}")
    return int(found[0])


def norm_axis(ax: plt.Axes, coordinate: str, upper: float) -> None:
    """Retain actual zero and roundoff-sized values in a declared linear region."""
    limit = max(float(upper) * 1.6, LINTHRESH * 2.0)
    ticks = [0.0] + [10.0**power for power in range(-10, 1, 2) if 10.0**power <= limit]
    if coordinate == "x":
        # A wider declared linear region spreads the resolved endpoint cloud
        # while retaining its zero/roundoff baseline without moving any point.
        limit = 10.0 ** np.ceil(np.log10(max(float(upper) * 1.15, ENDPOINT_SIGMA_LINTHRESH * 2)))
        ticks = [0.0] + [10.0**power for power in range(-6, 1) if 10.0**power <= limit]
        ax.set_xscale("symlog", linthresh=ENDPOINT_SIGMA_LINTHRESH, linscale=0.7)
        ax.set_xlim(0.0, limit)
        ax.set_xticks(ticks)
    else:
        ax.set_yscale("symlog", linthresh=LINTHRESH, linscale=0.7)
        ax.set_ylim(0.0, limit)
        ax.set_yticks(ticks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=BASE / "results" / "TRAJECTORY_ANALYSIS.npz")
    parser.add_argument("--output-dir", type=Path, default=BASE / "figures")
    args = parser.parse_args()
    with np.load(args.input, allow_pickle=False) as stored:
        axes = stored["axes"].copy()
        actual = stored["actual"].copy()
        z = stored["z"].copy()
    if axes.shape != (175, 3) or actual.shape != (175, 153, 3) or z.shape != (153,):
        raise ValueError("Expected 175 nominal triples, 153 epochs, and 3 signed channels")
    if not all(np.isfinite(array).all() for array in (axes, actual, z)):
        raise ValueError("Nonfinite stored data")
    if not np.allclose(z[[0, -1]], [20.0, 2.0], rtol=0, atol=1e-12):
        raise ValueError("Expected the stored z=20 to z=2 interval")
    levels = np.unique(axes[:, 0])
    if len(levels) != 7 or any(np.count_nonzero(axes[:, 0] == level) != 25 for level in levels):
        raise ValueError("Expected 7 initial-shear slices with 25 endpoints each")

    # actual channels are signed S_F, P_m,F, P_r,F, respectively.
    sigma = np.abs(actual[:, :, 0])
    pi_m = np.abs(actual[:, :, 1])
    pi_r = np.abs(actual[:, :, 2])
    pi_total = np.abs(actual[:, :, 1] + actual[:, :, 2])
    histories = (sigma, pi_m, pi_r)
    selected = (
        ((0.0, 0.0, 0.0), "Baseline", "-", None, None),
        ((0.0, 3e-4, 0.0), r"Matter: $(+3,\,0)$", "-", None, None),
        ((0.0, 0.0, 3e-4), r"Radiation: $(0,\,+3)$", "-", None, None),
        ((0.0, 3e-4, -3e-4), r"Opposed: $(+3,\,-3)$", "--", "o", (10, 28)),
        ((0.0, -3e-4, 3e-4), r"Opposed: $(-3,\,+3)$", "-.", "^", (21, 28)),
    )
    indices = [case_index(axes, selection[0]) for selection in selected]
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10, "axes.labelsize": 11,
        "axes.titlesize": 11.5, "text.color": INK, "axes.labelcolor": INK,
        "axes.edgecolor": "#8B97A4", "xtick.color": INK, "ytick.color": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.axisbelow": True, "grid.color": "#E1E6EB", "grid.linewidth": 0.7,
        "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.facecolor": "white",
    })
    fig = plt.figure(figsize=(15.0, 10.8), facecolor="white")
    fig.text(0.075, 0.976, "LRS Bianchi I pilot: shear and stress norms",
             ha="left", va="top", fontsize=19, fontweight="bold")
    fig.text(0.075, 0.939,
             "Non-tilted  |  collisionless, fixed L=8  |  full Frobenius normalization  |  preliminary stored trajectories",
             ha="left", va="top", fontsize=11, color="#526577")
    lefts = (0.075, 0.385, 0.695)
    top_axes = [fig.add_axes([left, 0.55, 0.265, 0.25]) for left in lefts]
    bottom_axes = [fig.add_axes([left, 0.18, 0.265, 0.23]) for left in lefts]
    top_titles = (
        r"(a) $\Sigma_{\rm F}=|S_{\rm F}^{\rm s}|$",
        r"(b) $\Pi_{m,\rm F}=|P_{m,\rm F}^{\rm s}|$",
        r"(c) $\Pi_{r,\rm F}=|P_{r,\rm F}^{\rm s}|$",
    )
    history_handles = []
    for channel, (ax, values) in enumerate(zip(top_axes, histories)):
        for idx, color, selection in zip(indices, HISTORY_COLORS, selected):
            _, label, linestyle, marker, markevery = selection
            line, = ax.plot(z, values[idx], color=color, lw=1.9, ls=linestyle,
                            marker=marker, markevery=markevery, markersize=3.6,
                            markerfacecolor="white", markeredgewidth=0.85, label=label)
            if channel == 0:
                history_handles.append(line)
        norm_axis(ax, "y", float(values[indices].max()))
        ax.set_xlim(20.0, 2.0)
        ax.set_xticks([20, 12, 4, 2])
        ax.axvline(4.0, color="#8B97A4", lw=1.0, ls=(0, (3, 3)))
        ax.grid(True)
        ax.set_xlabel(r"Mean redshift $z$ ($20\rightarrow2$)")
        ax.set_ylabel("Norm (dimensionless)")
        ax.set_title(top_titles[channel], loc="left", pad=10)
    fig.legend(handles=history_handles, loc="upper left", bbox_to_anchor=(0.072, 0.905),
               ncols=3, frameon=False, fontsize=10, handlelength=3.1, columnspacing=2.5,
               title=r"Histories: $\Sigma_{{\rm F},i}=0$; initial $(P_{m,i},P_{r,i})$ in units of $10^{-4}$",
               title_fontsize=10.5)

    grid_handles = [Line2D([], [], marker="o", ls="none", color=color, markersize=6,
                           label=f"{level:g}") for level, color in zip(levels, GRID_COLORS)]
    fig.legend(handles=grid_handles, loc="upper left", bbox_to_anchor=(0.072, 0.49),
               ncols=7, frameon=False, fontsize=10, handletextpad=0.4, columnspacing=2.0,
               title=r"Endpoints at $z=2$: all 175 cases; colour denotes initial $\Sigma_{{\rm F},i}$",
               title_fontsize=10.5)
    endpoint_values = (pi_m[:, -1], pi_r[:, -1], pi_total[:, -1])
    bottom_titles = ("(d) Matter endpoint", "(e) Radiation endpoint", "(f) Total-stress endpoint")
    bottom_ylabels = (r"$\Pi_{m,\rm F}$", r"$\Pi_{r,\rm F}$",
                      r"$\Pi_{{\rm tot},\rm F}=|P_m+P_r|$")
    for ax, values, title, ylabel in zip(bottom_axes, endpoint_values, bottom_titles, bottom_ylabels):
        for level, color in zip(levels, GRID_COLORS):
            mask = axes[:, 0] == level
            ax.scatter(sigma[mask, -1], values[mask], c=color, s=25, alpha=0.78,
                       edgecolors="white", linewidths=0.35, clip_on=False, zorder=3)
        norm_axis(ax, "x", float(sigma[:, -1].max()))
        norm_axis(ax, "y", float(values.max()))
        ax.set_xlabel(r"$\Sigma_{\rm F}$ at $z=2$")
        ax.set_ylabel(ylabel + r" at $z=2$")
        ax.set_title(title, loc="left", pad=10)
        ax.grid(True)
    fig.text(0.075, 0.048,
             "Norm axes use symlog: linear near zero, logarithmic above. Thresholds: y=10⁻¹⁰; endpoint Sigma x=10⁻⁶. No floor or jitter.\n"
             "Overlaps are retained; total stress uses the signed sum before its norm. Source: REI PR147 3b85dedce84d, stored Lane B; no new ODE.\n"
             "Comparisons use common mean redshift, with case-dependent proper time. Dashed line: z=4 continuation join. Physical admission remains HOLD.",
             ha="left", va="bottom", fontsize=9.3, color="#526577", linespacing=1.6)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for extension in ("png", "pdf"):
        output = args.output_dir / f"05_norm_evolution_and_endpoint_pilot.{extension}"
        fig.savefig(output, dpi=190, bbox_inches="tight", pad_inches=0.16)
        outputs.append(str(output))
    plt.close(fig)
    print(json.dumps({"input": str(args.input.resolve()), "artifacts": outputs,
                      "cases": 175, "epochs": 153,
                      "norm_axis_linthresh": {"y": LINTHRESH, "endpoint_sigma_x": ENDPOINT_SIGMA_LINTHRESH},
                      "total_norm_formula": "abs(P_m_signed + P_r_signed)",
                      "new_ODE_runs": 0, "new_benchmarks": 0}, indent=2))


if __name__ == "__main__":
    main()

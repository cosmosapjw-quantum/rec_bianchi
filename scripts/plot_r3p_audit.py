#!/usr/bin/env python3
"""Plot actual saved-audit observations, without confidence-interval claims."""
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--comparison", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    d = json.loads(a.comparison.read_text())
    if d["status"] != "PASS_ALL_15_DIFFERENTIAL_WITH_DISCLOSED_RESOURCE_REPAIR":
        raise ValueError("R3P_PLOT_REQUIRES_COMPLETED_DIFFERENTIAL")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    names = ["legacy", "cached", "rust1", "rust2", "rust4"]
    labels = ["Legacy Python", "Cached Python", "Rust · 1 thread", "Rust · 2 threads", "Rust · 4 threads"]
    colors = ["#606975", "#3A8EAA", "#775BA3", "#775BA3", "#775BA3"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 5.5), sharex=True)
    for ax, key, title in zip(axes, ["audit_cpu_s", "audit_wall_s"], ["Audit CPU time", "Audit wall time"]):
        for i, name in enumerate(names):
            rows = [s for s in d["samples"] if s["configuration"] == name]
            vals = [s[key] for s in rows]
            ax.bar(i, np.median(vals), color=colors[i], alpha=.22, width=.65, zorder=1)
            ax.vlines(i, min(vals), max(vals), color=colors[i], linewidth=2)
            for j, s in enumerate(rows):
                ax.scatter(i + (j-1)*.09, s[key], color=colors[i], s=40,
                           marker="^" if s.get("resource_repair_continuation") else "o", zorder=3)
            ax.text(i, max(vals)+.7, f"{np.median(vals):.2f}", ha="center", fontsize=10)
        ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
        ax.set_ylabel("Seconds")
        ax.set_xticks(range(5), labels, rotation=20, ha="right")
        ax.set_ylim(0, 27)
        ax.grid(axis="y", color="#CBD0D6", alpha=.4)
        ax.set_axisbelow(True)
    fig.suptitle("R3P · exact verification of saved R3M output", x=.065, ha="left", fontsize=17, fontweight="bold")
    fig.text(.065, .89, "8,510,412 prefix/spectral fields + control records per audit; 15/15 identical verdicts and native-array hashes", fontsize=10)
    fig.text(.065, .07, "Bars: median of 3 observations. Whiskers: observed range, not a confidence interval. Triangle: missing sample completed after resource-limit repair.", fontsize=9)
    fig.text(.065, .035, "CSV parsing, allocation and checks included; setup separate. No new physical integration or production speedup is measured in this figure.", fontsize=9)
    fig.subplots_adjust(left=.065, right=.985, top=.81, bottom=.24, wspace=.22)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".pdf"):
        out = a.output.with_suffix(suffix)
        if out.exists():
            raise FileExistsError(out)
        fig.savefig(out, dpi=220, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()

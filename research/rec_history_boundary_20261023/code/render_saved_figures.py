"""Repair one figure's tick layout using preserved primary rows only.

No adapter, oracle, mpmath, solver, or primary harness is imported. The six
selected depths are displayed at categorical positions, explicitly labelled
as non-proportional spacing. The original results and PNGs remain untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import time

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "results/attempt001"
EPS64 = 2.0**-52


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results/figure_repair001")
    args = parser.parse_args()
    out = args.output.resolve()
    start_wall = time.perf_counter()
    start_cpu = time.process_time()

    source = PRIMARY / "raw_cases.jsonl"
    raw_bytes = source.read_bytes()
    rows = [row for line in raw_bytes.decode().splitlines()
            if line.strip() and (row := json.loads(line))["group"] == "local"]
    tau_values = sorted({row["tau"] for row in rows})
    q_values = (0.6, 1.0, 1.4)
    drives = ("emission", "absorption", "equilibrium")
    if len(rows) != 54 or len(tau_values) != 6:
        raise ValueError("expected the preserved 54 controls at six selected optical depths")
    if tau_values[:5] != [0.0, 1e-10, 0.3, 2.0, 30.0]:
        raise ValueError("stored optical-depth selection differs from the frozen primary")
    expected_keys = {(tau, q, drive) for tau in tau_values for q in q_values for drive in drives}
    by_key = {(row["tau"], row["q"], row["drive"]): row for row in rows}
    if len(by_key) != 54 or set(by_key) != expected_keys:
        raise ValueError("stored local controls contain missing or duplicate selections")
    if out == PRIMARY.resolve() or PRIMARY.resolve() in out.parents:
        raise ValueError("figure repair must use a separate directory from the original primary")
    out.mkdir(parents=True, exist_ok=False)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.22})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.25, top=0.82, wspace=0.25)
    positions = tuple(range(1, 7))
    position_of = dict(zip(tau_values, positions))
    native_mantissa, native_exponent = f"{tau_values[-1]:.3e}".split("e")
    native_label = rf"${float(native_mantissa):g}\times 10^{{{int(native_exponent)}}}$" + "\n(native)"
    labels = ["0", r"$10^{-10}$", "0.3", "2", "30", native_label]
    colors = {0.6: "#2673B8", 1.0: "#D17A1D", 1.4: "#258E60"}
    for q in q_values:
        selected = [by_key[(tau, q, "emission")] for tau in tau_values]
        axes[0].plot(positions, [row["absorbed_fraction"] for row in selected],
                     "o-", color=colors[q], linewidth=1.6, markersize=5, label=f"q = {q:g}")
    axes[0].set(title="Transferred fraction", ylabel=r"$1-e^{-\tau/q}$", ylim=(-0.03, 1.05))
    axes[0].legend(loc="lower right", framealpha=0.95)

    # Horizontal offsets expose overlapping saved controls. They carry no
    # optical-depth meaning and stay within each categorical sample position.
    q_offsets = {0.6: -0.18, 1.0: 0.0, 1.4: 0.18}
    drive_offsets = {"emission": -0.04, "absorption": 0.0, "equilibrium": 0.04}
    markers = {"emission": "o", "absorption": "s", "equilibrium": "^"}
    for q in q_values:
        for drive in drives:
            selected = [by_key[(tau, q, drive)] for tau in tau_values]
            x = [position_of[row["tau"]] + q_offsets[q] + drive_offsets[drive] for row in selected]
            y = [row["scaled_outgoing_error"] / EPS64 for row in selected]
            axes[1].scatter(x, y, color=colors[q], marker=markers[drive],
                            s=29, alpha=0.75, linewidths=0.5, edgecolors="white")
    axes[1].axhline(128.0, color="#AA3030", linestyle="--", linewidth=1.3)
    axes[1].annotate("Frozen arithmetic limit: 128", xy=(3.5, 128.0), xytext=(0, -5),
                     textcoords="offset points", ha="center", va="top", color="#AA3030", fontsize=9)
    axes[1].set(title="Outgoing arithmetic error: all 54 controls",
                ylabel=r"Error / (gross scale $\times\epsilon_{64}$)", ylim=(-4.0, 138.0))
    legend_handles = [Line2D([0], [0], marker=markers[drive], linestyle="none",
                            color="0.35", markersize=5, label=drive.capitalize()) for drive in drives]
    axes[1].legend(handles=legend_handles, loc="center", ncols=1, framealpha=0.95, fontsize=9)

    for ax in axes:
        ax.set_xticks(positions, labels)
        ax.set_xlim(0.5, 6.5)
        ax.set_xlabel(r"Selected optical depth $\tau$", labelpad=8)
        ax.tick_params(axis="x", labelsize=10)
    fig.suptitle("Local finite boundary: preserved primary controls and 80-digit reference", fontsize=13, y=0.95)
    fig.text(0.5, 0.105, "Selected optical depths; horizontal spacing is not proportional. Offsets separate overlapping controls.",
             ha="center", va="center", fontsize=9)
    fig.text(0.5, 0.063, f"Native optical-depth sample = {tau_values[-1]:.17g}. All values are read from the original saved rows.",
             ha="center", va="center", fontsize=9)
    fig.text(0.5, 0.025, "Figure-format repair only: no new scientific cases or numerical-oracle executions.",
             ha="center", va="center", fontsize=9, color="0.3")
    output_png = out / "history_boundary_controls.png"
    fig.savefig(output_png, dpi=160)
    plt.close(fig)

    receipt = {
        "operation": "figure_format_repair",
        "reason": "original symlog tick crowding and negative automatic x limits",
        "source": str(source.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "source_local_rows_reused": len(rows),
        "selected_optical_depths": tau_values,
        "horizontal_axis": "six categorical selected samples; spacing not proportional",
        "original_primary_png_sha256": sha256(PRIMARY / "history_boundary_controls.png"),
        "unchanged_interpolation_png_sha256": sha256(PRIMARY / "history_interpolation_bounds.png"),
        "renderer_sha256": sha256(__file__),
        "output_png": output_png.name,
        "output_png_sha256": sha256(output_png),
        "new_scientific_cases": 0,
        "dense_rhs_solves": 0,
        "numerical_oracle_executions": 0,
        "old_LINE02_reruns": 0,
        "original_results_modified": False,
        "cpu_self_seconds": time.process_time() - start_cpu,
        "wall_seconds": time.perf_counter() - start_wall,
        "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "controller_note": "root adds inclusive rendering cost to the existing cumulative execution ledger",
    }
    (out / "RENDER_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()

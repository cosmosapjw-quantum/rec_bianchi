"""Plot the saved HD diagnostic JSON only; no adapter or physics execution."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.input.read_bytes()
    saved = json.loads(source)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.output_dir / "hd_source_diagnostics"
    for suffix in (".png", ".pdf", ".json"):
        if stem.with_suffix(suffix).exists():
            raise FileExistsError(stem.with_suffix(suffix))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titlesize": 12, "axes.labelsize": 10,
                         "xtick.labelsize": 9, "ytick.labelsize": 9,
                         "pdf.fonttype": 42, "ps.fonttype": 42,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(13.7, 5.2), gridspec_kw={"width_ratios": [1.05, 1.1, 1.05]})
    a, b, c = axes
    gaps = saved["frequency_gap_Hz"]
    ids = [r["line_id"] for r in gaps]
    values = [float(r["absolute_gap_Hz"]) for r in gaps]
    gate = float(saved["catalog_rounding_gate_Hz"])
    for line_id, value in zip(ids, values):
        failed = value > gate
        a.bar(line_id, value, color="0.82" if failed else "0.25", edgecolor="black",
              linewidth=0.8, hatch="///" if failed else None, width=0.68)
    a.axhline(gate, color="black", linestyle="--", linewidth=1.1)
    a.text(1.0, gate * 1.35, "fixed gate: 35 Hz", fontsize=9, va="bottom",
           bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})
    a.set_yscale("log")
    a.set_ylim(1, 8e6)
    a.set_xticks(ids)
    a.set_xlabel("Source radiative line ID")
    a.set_ylabel(r"$|c\,100\,\Delta E_{\rm cm^{-1}}-\nu_{\rm cat}|$  [Hz]")
    a.set_title("A  Level–frequency consistency", loc="left", pad=12)
    a.legend(handles=[Patch(facecolor="0.25", edgecolor="black", label="within gate (1/8)"),
                      Patch(facecolor="0.82", edgecolor="black", hatch="///", label="source discrepancy (7/8)")],
             loc="upper left", fontsize=8.5, frameon=False)
    a.grid(axis="y", which="major", color="0.85", linewidth=0.6)
    a.set_axisbelow(True)

    tolerance = saved["float_residual_tolerance"]
    db = [r["normalized_reverse_residual"] for r in saved["detailed_balance"]]
    lte = [r["normalized_Kirchhoff_residual"] for r in saved["Kirchhoff"]]
    floor = 1e-5
    all_values = db + lte
    for offset, group, marker, fill in ((0, db, "o", "0.25"), (len(db), lte, "s", "white")):
        indices = np.arange(offset + 1, offset + len(group) + 1)
        ratios = np.array(group, dtype=float) / tolerance
        positive = ratios > 0
        b.scatter(indices[positive], ratios[positive], s=19, marker=marker,
                  edgecolors="black", facecolors=fill, linewidths=0.65)
        b.scatter(indices[~positive], np.full(sum(~positive), floor), s=24, marker="v",
                  edgecolors="black", facecolors="none", linewidths=0.7)
    b.axhline(1, color="black", linestyle="--", linewidth=1.1)
    b.text(1, 1.18, r"gate: $128\epsilon_{64}$", fontsize=9, va="bottom")
    b.axvline(len(db) + 0.5, color="0.6", linestyle=":", linewidth=0.8)
    b.set_yscale("log")
    b.set_ylim(floor / 2, 2.5)
    b.set_xlim(-1, len(all_values) + 2)
    b.set_xticks([1, 27, 54, 78])
    b.set_xlabel("Saved check index (54 DB + 24 LTE)")
    b.set_ylabel(r"Normalized residual / $(128\epsilon_{64})$")
    b.set_title("B  Separate thermal identities", loc="left", pad=12)
    zeros = sum(value == 0 for value in all_values)
    b.legend(handles=[Line2D([], [], marker="o", linestyle="none", color="black", markersize=4, label="detailed balance"),
                      Line2D([], [], marker="s", linestyle="none", color="black", markerfacecolor="white", markersize=4, label="Kirchhoff (LTE)"),
                      Line2D([], [], marker="v", linestyle="none", color="black", markerfacecolor="none", markersize=4, label=f"exact zero ({zeros}); display floor")],
             loc="upper left", bbox_to_anchor=(0, 0.84), fontsize=8, frameon=False)
    b.grid(axis="y", which="major", color="0.85", linewidth=0.6)
    b.set_axisbelow(True)

    pairs = list(dict.fromkeys((r["upper"], r["lower"]) for r in saved["detailed_balance"]))
    temperatures = ["50", "100", "200"]
    columns = [(collider, temperature) for collider in (2, 3) for temperature in temperatures]
    covered = {(r["upper"], r["lower"], r["collider_id"], r["temperature_K"]) for r in saved["detailed_balance"]}
    for row, pair in enumerate(pairs):
        for col, (collider, temperature) in enumerate(columns):
            exists = (*pair, collider, temperature) in covered
            c.scatter(col, row, marker="s", s=125, facecolors="0.2" if exists else "white", edgecolors="black", linewidths=0.7)
    c.axvline(2.5, color="black", linestyle=":", linewidth=0.9)
    c.set_xlim(-0.65, 5.65)
    c.set_ylim(len(pairs) - 0.45, -0.8)
    c.set_xticks(range(6), ["50", "100", "200", "50", "100", "200"])
    c.set_yticks(range(len(pairs)), [f"{upper-1} → {lower-1}" for upper, lower in pairs])
    c.set_xlabel("Tabulated collision temperature [K]")
    c.set_ylabel(r"Supplied downward pair, $J_u\to J_l$")
    c.text(1, -0.55, "para-H₂", ha="center", va="center", fontsize=10)
    c.text(4, -0.55, "ortho-H₂", ha="center", va="center", fontsize=10)
    c.set_title("C  Collider identities and support", loc="left", pad=12)
    c.tick_params(axis="both", length=0)
    for spine in c.spines.values():
        spine.set_visible(False)

    fig.suptitle("Pinned LAMDA HD: source discrepancy and verified adapter scope", fontsize=15, y=0.98)
    fig.text(0.05, 0.075,
             "Original 2289-byte source preserved.  No temperature interpolation/extrapolation or p/o-H₂ mixing.  Missing pairs stay missing.",
             fontsize=9, ha="left")
    fig.text(0.05, 0.035,
             "Panel B uses separate level-energy DB and photon-energy LTE conventions.  Its small residuals do not resolve panel A.  Exact-zero markers are not upper bounds.",
             fontsize=8.7, ha="left")
    fig.subplots_adjust(left=0.065, right=0.985, bottom=0.23, top=0.85, wspace=0.4)
    fig.savefig(stem.with_suffix(".png"), dpi=190)
    fig.savefig(stem.with_suffix(".pdf"))
    plt.close(fig)
    manifest = {"schema": "REC_HD_SAVED_DIAGNOSTIC_FIGURE_V1", "input": str(args.input),
                "input_sha256": hashlib.sha256(source).hexdigest(),
                "plot_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "data_evaluation": "SAVED_JSON_ONLY", "new_adapter_or_science_execution": 0,
                "matplotlib_version": matplotlib.__version__, "panel_A_failures": sum(v > gate for v in values),
                "panel_B_exact_zero_residuals": zeros, "panel_B_display_floor_in_tolerance_units": floor,
                "panel_B_positive_values_clipped": False, "panel_C_supplied_entries": len(covered),
                "files": {suffix[1:]: {"bytes": stem.with_suffix(suffix).stat().st_size,
                "sha256": hashlib.sha256(stem.with_suffix(suffix).read_bytes()).hexdigest()} for suffix in (".png", ".pdf")}}
    stem.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Plot the stored REI LRS trajectories and the REC anchored-axis comparison.

This module does no integration, parameter/time interpolation, fitting, or
performance testing.  Lines only connect stored samples for display.
The three channels are signed full-Frobenius LRS coordinates.  Their absolute
values are norms; the total stress norm is abs(P_m + P_r), never abs(P_m)+abs(P_r).
All case comparisons use the same stored mean-redshift slices, not equal proper
times.  A small reconstruction residual is not an ODE error estimate.

Example::

    python code/plot_trajectories.py \
        --input results/TRAJECTORY_ANALYSIS.npz --output-dir figures
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import ScalarFormatter
import numpy as np


BASE = Path(__file__).resolve().parents[1]
FIELDS = (
    r"Signed shear $S_{\rm F}^{\rm s}$",
    r"Signed matter $P_{m,\rm F}^{\rm s}$",
    r"Signed radiation $P_{r,\rm F}^{\rm s}$",
)
FIELD_SYMBOLS = (
    r"S_{\rm F}^{\rm s}",
    r"P_{m,\rm F}^{\rm s}",
    r"P_{r,\rm F}^{\rm s}",
)
INK = "#263647"
GRID = "#E1E6EB"
COLORS = ("#777777", "#0072B2", "#D55E00", "#009E73", "#A751A6")
JOIN_Z = 4.0


def load_data(path: Path) -> dict[str, np.ndarray]:
    """Read and check the declared finite-grid plotting contract."""
    keys = ("axes", "actual", "predicted", "x", "z", "support", "case_ids")
    with np.load(path, allow_pickle=False) as archive:
        missing = set(keys) - set(archive.files)
        if missing:
            raise ValueError(f"Missing fields: {sorted(missing)}")
        data = {name: np.array(archive[name], copy=True) for name in keys}
    expected = {
        "axes": (175, 3),
        "actual": (175, 153, 3),
        "predicted": (175, 153, 3),
        "x": (153,),
        "z": (153,),
        "support": (175,),
        "case_ids": (175,),
    }
    for name, shape in expected.items():
        if data[name].shape != shape:
            raise ValueError(f"{name}: expected {shape}, got {data[name].shape}")
        if name not in ("case_ids", "support") and not np.isfinite(data[name]).all():
            raise ValueError(f"{name} contains nonfinite values")
    if data["support"].dtype.kind != "b":
        raise ValueError("support must be a Boolean array")
    axes = data["axes"]
    expected_support = (axes[:, 1] == 0.0) | (axes[:, 2] == 0.0)
    if data["support"].sum() != 63 or not np.array_equal(data["support"], expected_support):
        raise ValueError("Expected exactly 63 nominal axis-support cases")
    if len(np.unique(axes, axis=0)) != 175 or len(np.unique(data["case_ids"])) != 175:
        raise ValueError("Nominal coordinates and case identities must be unique")
    if not (np.diff(data["x"]) > 0).all() or not (np.diff(data["z"]) < 0).all():
        raise ValueError("Stored epochs must increase in x and decrease in redshift")
    if not np.allclose(data["z"][[0, -1]], [20.0, 2.0], rtol=0, atol=1e-12):
        raise ValueError("Expected the stored z=20 to z=2 trajectory window")
    if np.count_nonzero(np.isclose(data["z"], JOIN_Z, rtol=0, atol=1e-12)) != 1:
        raise ValueError("Expected one stored z=4 join sample")
    return data


def case_index(axes: np.ndarray, coordinates: tuple[float, float, float]) -> int:
    """Select by nominal configuration coordinates, never near-zero output data."""
    matches = np.flatnonzero(np.all(np.isclose(axes, coordinates, rtol=0, atol=1e-15), axis=1))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one nominal case at {coordinates}, found {len(matches)}")
    return int(matches[0])


def configure_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "axes.edgecolor": "#8B97A4",
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "lines.linewidth": 2.0,
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def style_redshift_axis(ax: plt.Axes, *, xlabel: bool = False) -> None:
    ax.set_xlim(20.0, 2.0)
    ax.set_xticks([20, 16, 12, 8, 4, 2])
    ax.axvline(JOIN_Z, color="#8B97A4", lw=1.1, ls=(0, (3, 3)), zorder=1)
    ax.grid(True, alpha=0.9)
    if xlabel:
        ax.set_xlabel(r"Mean redshift $z$  (evolution $20\,\rightarrow\,2$)")


def add_heading(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.085, 0.975, title, ha="left", va="top", fontsize=17, fontweight="bold")
    fig.text(0.085, 0.938, subtitle, ha="left", va="top", fontsize=10.5, color="#526577")


def save_figure(fig: plt.Figure, output: Path, stem: str) -> list[str]:
    paths = []
    for ext in ("png", "pdf"):
        path = output / f"{stem}.{ext}"
        fig.savefig(path, dpi=190, bbox_inches="tight", pad_inches=0.16)
        paths.append(str(path))
    plt.close(fig)
    return paths


def plot_evolution(data: dict[str, np.ndarray], output: Path) -> list[str]:
    selections = (
        ((0.0, 0.0, 0.0), "Baseline", "-"),
        ((0.0, 3e-4, 0.0), r"Matter: $(+3,\,0)$", "-"),
        ((0.0, 0.0, 3e-4), r"Radiation: $(0,\,+3)$", "-"),
        ((0.0, 3e-4, -3e-4), r"Opposed: $(+3,\,-3)$", "--"),
        ((0.0, -3e-4, 3e-4), r"Opposed: $(-3,\,+3)$", "-."),
    )
    fig, axes = plt.subplots(3, 1, figsize=(10.8, 10.0), sharex=True)
    fig.subplots_adjust(left=0.12, right=0.975, top=0.785, bottom=0.12, hspace=0.16)
    add_heading(
        fig,
        "LRS Bianchi I: separate sector histories",
        r"Non-tilted; $S_{{\rm F},i}=0$  |  collisionless, fixed $L=8$  |  full Frobenius normalization",
    )
    handles = []
    for color, (coordinates, label, linestyle) in zip(COLORS, selections):
        idx = case_index(data["axes"], coordinates)
        for channel, ax in enumerate(axes):
            line, = ax.plot(data["z"], 1e4 * data["actual"][idx, :, channel],
                            color=color, linestyle=linestyle, label=label,
                            lw=1.6 if coordinates == (0.0, 0.0, 0.0) else 2.0)
            if channel == 0:
                handles.append(line)
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.115, 0.897),
               ncols=3, frameon=False, fontsize=10, handlelength=2.8,
               columnspacing=1.7, labelspacing=0.8,
               title=r"Initial $(P_{m,\rm F}^{\rm s},\,P_{r,\rm F}^{\rm s})$ in units of $10^{-4}$",
               title_fontsize=10)
    for channel, ax in enumerate(axes):
        ax.axhline(0, color="#98A3AD", lw=0.7, zorder=0)
        ax.set_ylabel(f"{FIELDS[channel]}\n" + r"[$10^{-4}$]")
        ax.text(0.985, 0.93, f"({chr(97 + channel)})", transform=ax.transAxes,
                ha="right", va="top", fontweight="bold", fontsize=10)
        style_redshift_axis(ax, xlabel=channel == 2)
        ax.margins(y=0.14)
    axes[0].text(JOIN_Z + 0.15, 0.98, r"$z=4$ join", transform=axes[0].get_xaxis_transform(),
                 ha="right", va="top", fontsize=9, color="#647687")
    fig.text(0.12, 0.022,
             "153 saved epochs; curves connect stored samples. The dashed vertical line marks the continuation join.\n"
             "Comparison at common mean redshift, with case-dependent proper time. Preliminary; physical admission remains HOLD.",
             ha="left", va="bottom", fontsize=9, color="#526577", linespacing=1.5)
    return save_figure(fig, output, "01_signed_sector_evolution_z20_z2")


def plot_endpoint_grid(data: dict[str, np.ndarray], output: Path) -> list[str]:
    shear_levels = (0.0, 0.003, 0.1)
    groups = []
    values = []
    for shear in shear_levels:
        mask = np.isclose(data["axes"][:, 0], shear, rtol=0, atol=1e-15)
        if mask.sum() != 25:
            raise ValueError(f"Expected 25 endpoint cases at S_i={shear}")
        group = np.flatnonzero(mask)
        baseline = case_index(data["axes"], (shear, 0.0, 0.0))
        endpoint = data["actual"][group, -1, :].copy()
        endpoint[:, 0] -= data["actual"][baseline, -1, 0]
        groups.append(group)
        values.append(endpoint)
    value_array = np.stack(values, axis=0)
    maxima = np.max(np.abs(value_array), axis=(0, 1))
    norms = [colors.Normalize(vmin=-float(maximum or 1.0), vmax=float(maximum or 1.0))
             for maximum in maxima]
    fig = plt.figure(figsize=(12.0, 10.7))
    grid = fig.add_gridspec(3, 4, width_ratios=(1, 1, 1, 0.055),
                           left=0.10, right=0.92, top=0.85, bottom=0.13,
                           wspace=0.22, hspace=0.26)
    add_heading(
        fig,
        r"Finite-grid endpoint responses at $z=2$",
        r"25 actual points per slice; true nonuniform stress coordinates  |  signed full-Frobenius quantities",
    )
    row_labels = (
        r"Shear response $\Delta S_{\rm F}^{\rm s}$",
        r"Matter $P_{m,\rm F}^{\rm s}$",
        r"Radiation $P_{r,\rm F}^{\rm s}$",
    )
    m_ticks = np.array([-3, -1, 0, 1, 3])
    r_ticks = np.array([-10, -3, 0, 3, 10])
    for channel in range(3):
        mappable = None
        for column, (shear, group) in enumerate(zip(shear_levels, groups)):
            ax = fig.add_subplot(grid[channel, column])
            mappable = ax.scatter(
                1e4 * data["axes"][group, 1], 1e4 * data["axes"][group, 2],
                c=value_array[column, :, channel], norm=norms[channel], cmap="RdBu_r",
                s=138, marker="o", linewidths=0.65, edgecolors="#34485C", zorder=3,
            )
            ax.set_xlim(-3.7, 3.7)
            ax.set_ylim(-11.9, 11.9)
            ax.set_xticks(m_ticks)
            ax.set_yticks(r_ticks)
            ax.grid(True, alpha=0.9)
            if channel == 0:
                ax.set_title(r"$S_{{\rm F},i}=" + f"{shear:g}" + "$", pad=10, fontweight="bold")
            if channel == 2:
                ax.set_xlabel(r"Initial $P_{m,\rm F}^{\rm s}$ [$10^{-4}$]")
            else:
                ax.tick_params(labelbottom=False)
            if column == 0:
                ax.set_ylabel(r"Initial $P_{r,\rm F}^{\rm s}$ [$10^{-4}$]")
            else:
                ax.tick_params(labelleft=False)
            ax.text(0.035, 1.025, f"({chr(97 + channel * 3 + column)})",
                    transform=ax.transAxes, va="bottom", fontsize=9, fontweight="bold")
        color_ax = fig.add_subplot(grid[channel, 3])
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((0, 0))
        colorbar = fig.colorbar(mappable, cax=color_ax, format=formatter)
        colorbar.set_label(row_labels[channel], labelpad=11)
        colorbar.ax.tick_params(labelsize=9)
        colorbar.outline.set_linewidth(0.6)
    fig.text(0.10, 0.035,
             r"$\Delta S_{\rm F}^{\rm s}=S_{\rm F}^{\rm s}(S_i,P_{m,i},P_{r,i};z=2)-S_{\rm F}^{\rm s}(S_i,0,0;z=2)$. "
             "Each row shares one symmetric color scale.\n"
             "No interpolation or unsampled surface. Collisionless fixed L=8, common redshift with case-dependent proper time; preliminary.",
             ha="left", va="bottom", fontsize=9, color="#526577", linespacing=1.6)
    return save_figure(fig, output, "02_finite_grid_endpoint_response_z2")


def plot_reconstruction_residual(data: dict[str, np.ndarray], output: Path) -> list[str]:
    residual = np.abs(data["actual"][~data["support"]] - data["predicted"][~data["support"]])
    median, p95 = np.quantile(residual, [0.5, 0.95], axis=0)
    maximum = residual.max(axis=0)
    fig, axes = plt.subplots(3, 1, figsize=(10.8, 10.0), sharex=True)
    fig.subplots_adjust(left=0.13, right=0.975, top=0.78, bottom=0.17, hspace=0.28)
    add_heading(
        fig,
        "Anchored-axis reconstruction along the full history",
        r"63 axis-support trajectories reconstruct 112 mixed cases  |  153 epochs  |  collisionless, fixed $L=8$",
    )
    fig.text(0.13, 0.875,
             r"$\widehat F(S_i,m_i,r_i;z)=F(S_i,m_i,0;z)+F(S_i,0,r_i;z)-F(S_i,0,0;z)$",
             ha="left", va="top", fontsize=12)
    handles = []
    for channel, ax in enumerate(axes):
        ax.fill_between(data["z"], median[:, channel], p95[:, channel],
                        color="#56B4E9", alpha=0.16, linewidth=0)
        ax.fill_between(data["z"], p95[:, channel], maximum[:, channel],
                        color="#8E7CC3", alpha=0.12, linewidth=0)
        for curve, label, color, linestyle in (
            (maximum, "Maximum", INK, "-"),
            (p95, "95th percentile", "#8661A5", "--"),
            (median, "Median", "#0072B2", "-"),
        ):
            line, = ax.plot(data["z"], curve[:, channel], label=label,
                            color=color, linestyle=linestyle, lw=1.9)
            if channel == 0:
                handles.append(line)
        # Symmetric-log has an explicit linear region at zero: no floor, clipping,
        # or invented nonzero samples are introduced into the stored differences.
        ax.set_yscale("symlog", linthresh=1e-18, linscale=0.7)
        upper = max(float(maximum[:, channel].max()) * 2.0, 2e-18)
        ax.set_ylim(bottom=0, top=upper)
        ax.set_yticks([0.0] + [10.0**power for power in range(-18, 1, 3)
                              if 10.0**power <= upper])
        ax.set_ylabel(rf"$|{FIELD_SYMBOLS[channel]}-\widehat{{{FIELD_SYMBOLS[channel]}}}|$")
        ax.text(0.016, 1.035, f"({chr(97 + channel)})  {FIELDS[channel]}",
                transform=ax.transAxes, va="bottom", fontsize=10)
        ax.text(0.995, 1.035, f"Maximum over stored history: {maximum[:, channel].max():.2e}",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=9, color="#526577")
        style_redshift_axis(ax, xlabel=channel == 2)
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.125, 0.836),
               ncols=3, frameon=False, fontsize=10, handlelength=3.0, columnspacing=2.8)
    fig.text(0.13, 0.032,
             "Absolute differences of saved trajectories; quantiles are across the 112 mixed cases at each stored epoch.\n"
             "Vertical scale: logarithmic above 10⁻¹⁸, linear down to zero; no display floor. Dashed vertical line: z=4 join.\n"
             "Common redshift is not common proper time. Preliminary reconstruction comparison, not an ODE or convergence error bound.",
             ha="left", va="bottom", fontsize=9, color="#526577", linespacing=1.5)
    return save_figure(fig, output, "03_mixed_trajectory_absolute_residual")


def plot_cancellation(data: dict[str, np.ndarray], output: Path) -> list[str]:
    idx = case_index(data["axes"], (0.0, 3e-4, -3e-4))
    actual_parts = data["actual"][idx, :, 1:3]
    predicted_parts = data["predicted"][idx, :, 1:3]
    # The signed sum must be formed before taking its norm.
    actual_total_norm = np.abs(actual_parts[:, 0] + actual_parts[:, 1])
    predicted_total_norm = np.abs(predicted_parts[:, 0] + predicted_parts[:, 1])
    norm_difference = np.abs(actual_total_norm - predicted_total_norm)
    component_residual_bound = np.abs(actual_parts - predicted_parts).sum(axis=1)
    fig, axes = plt.subplots(2, 1, figsize=(10.8, 8.9), sharex=True)
    fig.subplots_adjust(left=0.13, right=0.975, top=0.77, bottom=0.18, hspace=0.35)
    add_heading(
        fig,
        "Cancellation requires the signed sector sum",
        r"Initial $(S_i,P_{m,i},P_{r,i})=(0,+3,-3)\times10^{-4}$  |  collisionless, fixed $L=8$  |  Frobenius",
    )
    handles = []
    for curve, label, color, linestyle in (
        (actual_parts[:, 0], r"Signed matter $P_m$", "#0072B2", "-"),
        (actual_parts[:, 1], r"Signed radiation $P_r$", "#D55E00", "-"),
        (actual_total_norm, r"Total norm $|P_m+P_r|$", INK, "-"),
        (np.abs(actual_parts).sum(axis=1), r"Sector-norm sum $|P_m|+|P_r|$", "#999999", "--"),
    ):
        line, = axes[0].plot(data["z"], 1e4 * curve, color=color,
                             linestyle=linestyle, label=label, lw=2.1)
        handles.append(line)
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.125, 0.875),
               ncols=2, frameon=False, fontsize=10, handlelength=2.8,
               columnspacing=2.5, labelspacing=0.9)
    axes[0].set_ylabel(r"Signed coordinates and norms [$10^{-4}$]")
    axes[0].axhline(0, color="#98A3AD", lw=0.7)
    axes[0].text(0.015, 1.035, "(a) Saved sector histories and their total norm",
                 transform=axes[0].transAxes, va="bottom", fontsize=10)
    axes[0].margins(y=0.15)
    axes[1].plot(data["z"], component_residual_bound, color="#999999", ls="--", lw=1.8,
                 label=r"Algebraic bound $|R_m|+|R_r|$")
    axes[1].plot(data["z"], norm_difference, color="#8661A5", lw=2.0,
                 label=r"Stored norm difference $|\Pi_{\rm tot}-\widehat\Pi_{\rm tot}|$")
    axes[1].set_yscale("symlog", linthresh=1e-18, linscale=0.7)
    upper = max(2.0 * float(component_residual_bound.max()), 2e-18)
    axes[1].set_ylim(0, upper)
    axes[1].set_yticks([0.0] + [10.0**power for power in range(-18, 1, 3)
                               if 10.0**power <= upper])
    axes[1].set_ylabel("Absolute stored-data difference")
    axes[1].text(0.015, 1.035, "(b) Actual versus axis-reconstructed total norm",
                 transform=axes[1].transAxes, va="bottom", fontsize=10)
    axes[1].legend(loc="lower center", bbox_to_anchor=(0.50, 0.035), frameon=False, fontsize=9)
    axes[1].text(0.50, 0.27, "The two curves coincide at this plotted scale.",
                 transform=axes[1].transAxes, ha="center", fontsize=8.5, color="#647687")
    for channel, ax in enumerate(axes):
        style_redshift_axis(ax, xlabel=channel == 1)
    fig.text(0.13, 0.030,
             "All stress coordinates use full Frobenius normalization. The sector-norm sum is a bound, not the total norm.\n"
             "Lower panel: logarithmic above 10⁻¹⁸, linear to zero; no display floor. Dashed vertical line: z=4 continuation join.\n"
             "Common redshift, case-dependent proper time. Preliminary saved-data comparison; neither an ODE error nor a physical validation.",
             ha="left", va="bottom", fontsize=9, color="#526577", linespacing=1.5)
    return save_figure(fig, output, "04_signed_cancellation_and_total_norm")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=BASE / "results" / "TRAJECTORY_ANALYSIS.npz")
    parser.add_argument("--output-dir", "--output", dest="output_dir", type=Path,
                        default=BASE / "figures")
    args = parser.parse_args()
    data = load_data(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    configure_style()
    artifacts = []
    artifacts.extend(plot_evolution(data, args.output_dir))
    artifacts.extend(plot_endpoint_grid(data, args.output_dir))
    artifacts.extend(plot_reconstruction_residual(data, args.output_dir))
    artifacts.extend(plot_cancellation(data, args.output_dir))
    print(json.dumps({
        "input": str(args.input.resolve()),
        "artifacts": artifacts,
        "nominal_cases": 175,
        "axis_support": 63,
        "mixed_cases": 112,
        "saved_epochs": 153,
        "normalization": "signed full Frobenius",
        "comparison_clock": "common mean redshift; case-dependent proper time",
        "new_ODE_executions": 0,
        "physical_admission": "HOLD",
    }, indent=2))


if __name__ == "__main__":
    main()

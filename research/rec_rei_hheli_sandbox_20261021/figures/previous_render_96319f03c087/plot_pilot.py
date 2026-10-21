#!/usr/bin/env python3
"""Plot only hash-verified, completed H/He/Li pilot trajectories; no solver import."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "rec_hheli_matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPECIES = ("n", "H1I", "H1II", "DI", "DII", "TI", "TII", "He3I", "He3II", "He3III",
           "He4I", "He4II", "He4III", "Li6I", "Li6II", "Li6III", "Li6IV", "Li7I", "Li7II", "Li7III", "Li7IV")
MASS = np.array([1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 6, 6, 6, 6, 7, 7, 7, 7])
CHARGE = np.array([0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3])
GROUPS = [(r"${}^{1}\mathrm{H}$", [1, 2]), (r"$\mathrm{D}$", [3, 4]),
          (r"${}^{3}\mathrm{He}$", [7, 8, 9]), (r"${}^{4}\mathrm{He}$", [10, 11, 12]),
          (r"${}^{6}\mathrm{Li}$", [13, 14, 15, 16]), (r"${}^{7}\mathrm{Li}$", [17, 18, 19, 20])]
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7")
SCOPE = "Conditional prescribed T / UV; test-fluid baryons | Physical HOLD"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def checked(condition, reason):
    if not condition:
        raise ValueError(reason)


def relative_file(root, name):
    path = (root / name).resolve()
    path.relative_to(root.resolve())
    return path


def load_cases(source):
    frozen_path = source / "FROZEN.json"
    if not frozen_path.is_file():
        raise ValueError("No frozen campaign at input; no figures generated")
    frozen = read_json(frozen_path)
    checked(hashlib.sha256(canonical(frozen["files"])).hexdigest() == frozen["base_identity"], "invalid frozen source identity")
    cases, missing = [], []
    seen = set()
    for config in frozen["configs"]:
        case_id = config["case_id"]
        checked(case_id not in seen, "duplicate frozen case ID")
        seen.add(case_id)
        directory = relative_file(source / "cases", case_id)
        if not (directory / "COMPLETE.json").is_file():
            status = "NOT_COMPLETED"
            if (directory / "RESULT.json").is_file():
                status = str(read_json(directory / "RESULT.json").get("status", "UNKNOWN"))
            missing.append({"case_id": case_id, "status": status, "plotted": False})
            continue
        done, result = read_json(directory / "COMPLETE.json"), read_json(directory / "RESULT.json")
        identity = hashlib.sha256(canonical({"base": frozen["base_identity"], "config": config})).hexdigest()
        checked(done["identity"] == result["scientific_identity_sha256"] == identity, case_id + ": identity mismatch")
        checked(result["status"] == "COMPLETE" and result["schema"] == "rec.rei.hheli.coupled62.v1", case_id + ": not a completed coupled62 case")
        checked(result["gates"] and all(v is True for v in result["gates"].values()), case_id + ": failed scientific gate")
        checked(result["config"] == config, case_id + ": result config mismatch")
        checked(sha(directory / "RESULT.json") == done["result_sha256"], case_id + ": RESULT hash mismatch")
        checked(done["outputs"] == result["outputs"] and "trajectory.npz" in done["outputs"], case_id + ": output manifest mismatch")
        for name, row in done["outputs"].items():
            path = relative_file(directory, name)
            checked(path.stat().st_size == row["bytes"] and sha(path) == row["sha256"], case_id + ": output byte mismatch")
        with np.load(directory / "trajectory.npz", allow_pickle=False) as saved:
            data = {name: saved[name].copy() for name in saved.files}
        metrics = validate_arrays(data, config)
        cases.append({"id": case_id, "config": config, "data": data, "identity": identity,
                      "result_sha256": done["result_sha256"], "npz_sha256": done["outputs"]["trajectory.npz"]["sha256"], "checks": metrics})
    checked(bool(cases), "No hash-verified completed trajectories; no figures generated")
    checked(all(np.array_equal(c["data"]["x"], cases[0]["data"]["x"]) for c in cases), "different saved time grids cannot form one envelope")
    return cases, {"source": str(source.resolve()), "frozen_sha256": sha(frozen_path),
                   "base_identity": frozen["base_identity"], "planned_cases": len(frozen["configs"]),
                   "completed_plotted": len(cases), "unplotted": missing}


def validate_arrays(data, config):
    count = 193
    shapes = {"x": (count,), "z": (count,), "raw_state": (count, 62), "Y": (count, 21),
              "scaled_populations": (count, 21), "signed_observables": (count, 6), "observables_norm": (count, 6),
              "initial_Y": (21,), "isotope_scales": (21,), "A": (21,), "q": (21,), "species_names": (21,)}
    for name, shape in shapes.items():
        checked(name in data and data[name].shape == shape, "invalid array shape: " + name)
        if data[name].dtype.kind not in "US":
            checked(np.isfinite(data[name]).all() and not np.iscomplexobj(data[name]), "nonfinite or complex array: " + name)
    x, z = data["x"], data["z"]
    checked(int(config.get("samples", 193)) == count and abs(float(config.get("x_end", math.log(7))) - math.log(7)) < 2e-14, "partial or non-contract time grid")
    checked(np.allclose(x, np.linspace(0, math.log(7), count), rtol=0, atol=2e-14), "saved x is not the 193-node full interval")
    checked(np.all(np.diff(z) < 0) and abs(z[0] - 20) < 1e-12 and abs(z[-1] - 2) < 1e-12, "redshift must decrease from 20 to 2")
    checked(np.allclose(z, 21 * np.exp(-x) - 1, rtol=0, atol=1e-12), "x/redshift correspondence mismatch")
    checked(tuple(data["species_names"].tolist()) == SPECIES, "21-state species order mismatch")
    checked(np.array_equal(data["A"], MASS) and np.array_equal(data["q"], CHARGE), "isotope mass/charge mapping mismatch")
    checked(np.all(data["isotope_scales"] > 0), "invalid isotope scaling")
    checked(np.array_equal(data["scaled_populations"], data["raw_state"][:, 40:61]), "raw/scaled population mismatch")
    checked(np.array_equal(data["Y"], data["scaled_populations"] * data["isotope_scales"]), "physical/scaled population mismatch")
    checked(np.allclose(data["Y"][0], data["initial_Y"], rtol=2e-14, atol=1e-30), "initial population mismatch")
    obs = data["signed_observables"]
    total_error = float(np.max(abs(obs[:, 3] - obs[:, 1] - obs[:, 2])))
    radiation_error = float(np.max(abs(obs[:, 2] - obs[:, 4] - obs[:, 5])))
    checked(total_error < 2e-16 and radiation_error < 2e-16, "signed tensor component sum mismatch")
    checked(np.array_equal(data["observables_norm"], np.abs(obs)), "norm must follow signed tensor addition")
    names = data["diagnostic_names"].tolist()
    checked(data["diagnostic_names"].ndim == 1 and len(set(names)) == len(names), "invalid diagnostic names")
    checked(data["diagnostics"].shape == (count, len(names)) and np.isfinite(data["diagnostics"]).all(), "invalid diagnostics shape or value")
    required = {"H", "elapsed_s", "nb_m3", "ne_m3", "T_K", "uv_scale", "tau_T", "trace_energy_fraction",
                "net_required_gas_input_W_m3", "photo_absorbed_W_m3", "bath_minus_escape_W_m3", "unresolved_core_W_m3"}
    checked(required.issubset(names), "missing coupling diagnostic")
    ne = data["diagnostics"][:, names.index("ne_m3")]
    nb = data["diagnostics"][:, names.index("nb_m3")]
    checked(np.allclose(ne, nb * (data["Y"] @ CHARGE), rtol=2e-12, atol=1e-30), "electron abundance/opacity diagnostic mismatch")
    checked(np.min(ne) >= 0, "negative accepted electron density")
    elapsed = data["diagnostics"][:, names.index("elapsed_s")]
    h = data["diagnostics"][:, names.index("H")]
    checked(elapsed[1] > 0 and np.all(h > 0), "invalid time/Hubble normalization")
    href = data["raw_state"][1, 0] / elapsed[1]
    sigma = math.sqrt(6) * href * data["raw_state"][:, 2] / h
    checked(np.allclose(obs[:, 0], sigma, rtol=5e-14, atol=1e-16), "Frobenius shear normalization mismatch")
    target = np.array([config["Sigma_F"], config["P_m_initial_target"], config["P_r_initial_target"]])
    checked(np.allclose(obs[0, :3], target, rtol=2e-9, atol=2e-12), "physical initial-axis target mismatch")
    return {"tensor_sum_max_abs": total_error, "radiation_sum_max_abs": radiation_error,
            "initial_axis_max_abs_difference": float(np.max(abs(obs[0, :3] - target))), "samples": count,
            "min_scaled_population": float(data["scaled_populations"].min()),
            "max_baryon_inventory_error": float(np.max(abs(data["Y"] @ MASS - 1)))}


def diagnostic(case, name):
    data = case["data"]
    return data["diagnostics"][:, data["diagnostic_names"].tolist().index(name)]


def seed(case):
    return case["data"]["signed_observables"][0, :3]


def seed_label(case):
    s, m, r = seed(case)
    return rf"$(\Sigma_0,\widetilde\Pi_{{m0}},\widetilde\Pi_{{r0}})=({s:.3g},{m:.2g},{r:.2g})$"


def representative(cases, desired=(.15, .0005, .0006)):
    scale = np.array([.6, .001, .0012])
    return min(cases, key=lambda c: np.linalg.norm((seed(c) - desired) / scale))


def decorate_axis(ax, xlabel="Redshift z"):
    ax.set_xlabel(xlabel)
    if xlabel == "Redshift z":
        ax.set_xlim(20, 2)
        ax.set_xticks([20, 16, 12, 8, 4, 2])
    ax.grid(alpha=.2, linewidth=.6)
    ax.tick_params(labelsize=10)


def header(fig, title, context, note):
    fig.suptitle(title, x=.5, y=.989, fontsize=17, fontweight="semibold")
    fig.text(.5, .95, f"{context['completed_plotted']}/{context['planned_cases']} completed cases | {note}", ha="center", fontsize=10.5)
    fig.text(.5, .017, SCOPE, ha="center", fontsize=10, color="#4b4b4b")


def export(fig, output, stem):
    paths = []
    for suffix in ("png", "pdf"):
        path = output / f"{stem}.{suffix}"
        fig.savefig(path, dpi=175, facecolor="white", metadata={"Title": stem})
        paths.append({"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha(path)})
    plt.close(fig)
    return paths


def plot_evolution(cases, context, output):
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 9.5))
    fig.subplots_adjust(left=.09, right=.96, top=.87, bottom=.25, hspace=.42, wspace=.27)
    values = np.stack([c["data"]["observables_norm"][:, :4] for c in cases])
    z = cases[0]["data"]["z"]
    chosen = []
    for target in ((0, 0, 0), (.15, .0005, .0006), (.6, .001, .0012), (.15, -.0005, .0012)):
        case = representative(cases, target)
        if case["id"] not in {c["id"] for c in chosen}:
            chosen.append(case)
    labels = [r"$\Sigma_F=\|\sigma\|_F/H$", r"$\Pi_m=\kappa_t\|\pi_m\|_F/H^2$",
              r"$\Pi_r=\kappa_t\|\pi_\gamma+\pi_\nu\|_F/H^2$", r"$\Pi_{m+r}=\kappa_t\|\pi_m+\pi_r\|_F/H^2$"]
    for index, ax in enumerate(axes.flat):
        ax.fill_between(z, values[:, :, index].min(0), values[:, :, index].max(0), color="#90AFC4", alpha=.28)
        ax.plot(z, np.median(values[:, :, index], axis=0), color="#1b1b1b", linewidth=2)
        for case, color in zip(chosen, COLORS):
            ax.plot(z, case["data"]["observables_norm"][:, index], color=color, linewidth=1.35)
        ax.set_yscale("symlog", linthresh=1e-5 if index == 0 else 1e-8, linscale=.45)
        ax.set_ylim(bottom=0)
        ax.set_ylabel(labels[index], fontsize=11)
        decorate_axis(ax)
    handles = [Patch(facecolor="#90AFC4", alpha=.35, label="Min-max of completed cases"),
               Line2D([], [], color="#1b1b1b", lw=2, label="Median of completed cases")]
    handles += [Line2D([], [], color=color, lw=1.6, label=seed_label(c)) for c, color in zip(chosen, COLORS)]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .075), ncol=2, frameon=False, fontsize=9.5)
    header(fig, "LRS Bianchi I: shear and separate stress evolution", context,
           "Frobenius norms; signed components added before total norm")
    return export(fig, output, "01_shear_stress_evolution")


def cell_edges(values):
    values = np.asarray(values, dtype=float)
    if len(values) == 1:
        width = max(abs(values[0]) * .1, .1)
        return np.array([values[0] - width, values[0] + width])
    mid = .5 * (values[1:] + values[:-1])
    return np.r_[2 * values[0] - mid[0], mid, 2 * values[-1] - mid[-1]]


def plot_sweep(cases, context, output):
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 10))
    fig.subplots_adjust(left=.09, right=.93, bottom=.13, top=.87, hspace=.47, wspace=.40)
    initial = np.stack([seed(c) for c in cases])
    final = np.stack([c["data"]["signed_observables"][-1] for c in cases])
    coloring = SymLogNorm(linthresh=.003, vmin=0, vmax=max(.6, initial[:, 0].max()), base=10)
    for column, index in enumerate((1, 2)):
        ax = axes[0, column]
        points = ax.scatter(abs(final[:, 0]), final[:, index], c=initial[:, 0], cmap="viridis", norm=coloring,
                            s=38, edgecolors="white", linewidths=.35, alpha=.85)
        ax.axhline(0, color="#777777", linewidth=.8)
        ax.set_xscale("symlog", linthresh=1e-5, linscale=.4)
        ax.set_yscale("symlog", linthresh=1e-8, linscale=.4)
        ax.set_title("Matter endpoint" if index == 1 else "Radiation endpoint", fontsize=12)
        ax.set_ylabel(r"Signed $\widetilde\Pi_m(z=2)$" if index == 1 else r"Signed $\widetilde\Pi_r(z=2)$")
        decorate_axis(ax, r"$\Sigma_F(z=2)$")
        fig.colorbar(points, ax=ax, pad=.025, fraction=.055).set_label(r"Initial $\Sigma_{F,0}$")
    sigma_values = sorted({c["config"]["Sigma_F"] for c in cases})
    fixed = min(sigma_values, key=lambda v: abs(v - .15))
    subset = [c for c in cases if c["config"]["Sigma_F"] == fixed]
    # Frozen physical axes are used; absent completed nodes remain masked.
    all_configs = read_json(Path(context["source"]) / "FROZEN.json")["configs"]
    m_values = sorted({c["P_m_initial_target"] for c in all_configs})
    r_values = sorted({c["P_r_initial_target"] for c in all_configs})
    z = cases[0]["data"]["z"]
    epochs = [int(np.argmin(abs(z - 8))), len(z) - 1]
    grids = []
    for epoch in epochs:
        grid = np.full((len(r_values), len(m_values)), np.nan)
        for case in subset:
            m, r = case["config"]["P_m_initial_target"], case["config"]["P_r_initial_target"]
            grid[r_values.index(r), m_values.index(m)] = case["data"]["signed_observables"][epoch, 3]
        grids.append(grid)
    vmax = max(float(np.nanmax(abs(grid))) for grid in grids)
    vmax = max(vmax, 1e-14)
    heat_norm = SymLogNorm(linthresh=max(1e-12, vmax * 1e-3), vmin=-vmax, vmax=vmax, base=10)
    cmap = plt.get_cmap("RdBu_r").copy(); cmap.set_bad("#dddddd")
    for column, (grid, epoch) in enumerate(zip(grids, epochs)):
        ax = axes[1, column]
        mesh = ax.pcolormesh(cell_edges(np.array(m_values) * 1e3), cell_edges(np.array(r_values) * 1e3),
                             np.ma.masked_invalid(grid), cmap=cmap, norm=heat_norm, shading="flat", edgecolors="white", linewidth=.7)
        ax.set_title(rf"$\Sigma_{{F,0}}={fixed:g}$ slice at saved $z={z[epoch]:.3f}$", fontsize=12)
        ax.set_xticks(np.array(m_values) * 1e3); ax.set_yticks(np.array(r_values) * 1e3)
        ax.set_xlabel(r"Initial signed $\widetilde\Pi_{m0}\times 10^3$")
        ax.set_ylabel(r"Initial signed $\widetilde\Pi_{r0}\times 10^3$")
        fig.colorbar(mesh, ax=ax, pad=.025, fraction=.055).set_label(r"Signed $\widetilde\Pi_{m+r}(z)$")
    header(fig, "Physical three-axis parameter sweep", context,
           r"Initial $\Sigma_F\in[0,0.6]$; independent matter / radiation signed stresses")
    fig.text(.5, .065, "Scatter: every completed case. Cells: finite saved nodes; grey denotes an uncompleted node. No interpolation.",
             ha="center", fontsize=9)
    return export(fig, output, "02_physical_parameter_sweep")


def plot_ions(cases, context, output):
    case = representative(cases)
    data, z = case["data"], case["data"]["z"]
    fig, axes = plt.subplots(3, 2, figsize=(12.7, 12.0))
    fig.subplots_adjust(left=.08, right=.97, bottom=.12, top=.85, hspace=.43, wspace=.22)
    for ax, (label, indices) in zip(axes.flat, GROUPS):
        inventory = float(data["initial_Y"][indices].sum())
        checked(inventory > 0, "cannot form charge fractions of a zero-inventory isotope")
        fractions = data["Y"][:, indices] / inventory
        for charge, color in enumerate(COLORS[:len(indices)]):
            ax.plot(z, fractions[:, charge], color=color, linewidth=1.7, linestyle=("-", "--", "-.", ":")[charge])
        ax.set_yscale("symlog", linthresh=1e-10, linscale=.45)
        ax.set_ylim(min(-1e-12, 1.2 * fractions.min()), max(1.05, 1.02 * fractions.max()))
        ax.set_ylabel("Charge fraction")
        ax.set_title(f"{label}  |  initial nuclei / baryon = {inventory:.3g}", fontsize=11)
        decorate_axis(ax)
    fig.legend(handles=[Line2D([], [], color=COLORS[k], linestyle=("-", "--", "-.", ":")[k], lw=1.8,
                               label=f"{('I', 'II', 'III', 'IV')[k]} (charge {k}+)" if k else "I (neutral)") for k in range(4)],
               loc="upper center", bbox_to_anchor=(.5, .925), ncol=4, frameon=False, fontsize=10)
    header(fig, "Every retained H / He / Li ionic state", context, case["id"] + " | " + seed_label(case))
    zero = float(np.max(abs(data["Y"][:, [0, 5, 6]])))
    fig.text(.5, .065, f"n and T initial inventories = 0; max saved abundance = {zero:.2g} per baryon. No populated decay history is implied.", ha="center", fontsize=9.5)
    fig.text(.5, .041, "Fractions use the initial isotope inventory; values are not clipped or renormalized. Symlog linear band: |fraction| <= 1e-10.", ha="center", fontsize=9)
    return export(fig, output, "03_all_isotope_ion_fractions"), case["id"]


def envelope(ax, cases, name, color="#0072B2"):
    values = np.stack([diagnostic(c, name) for c in cases])
    z = cases[0]["data"]["z"]
    ax.fill_between(z, values.min(0), values.max(0), color=color, alpha=.16)
    ax.plot(z, np.median(values, axis=0), color=color, lw=1.7)


def plot_coupling(cases, context, output):
    case = representative(cases)
    z = case["data"]["z"]
    fig, axes = plt.subplots(3, 2, figsize=(12.8, 12.9))
    fig.subplots_adjust(left=.10, right=.91, top=.87, bottom=.19, hspace=.64, wspace=.37)
    ax = axes[0, 0]
    envelope(ax, cases, "ne_m3")
    ax.plot(z, diagnostic(case, "ne_m3"), color="#D55E00", lw=1.2, ls="--")
    ax.set_yscale("log"); ax.set_ylabel(r"Proper $n_e$ [m$^{-3}$]")
    ax.set_title("Electrons supplied by the evolving ion network", fontsize=11)
    ax = axes[0, 1]
    ax.plot(z, diagnostic(case, "T_K"), color="#D55E00", lw=1.8)
    ax.set_ylabel("Prescribed gas T [K]", color="#A84300"); ax.set_yscale("log")
    uv = ax.twinx(); uv.plot(z, diagnostic(case, "uv_scale"), color="#0072B2", lw=1.6, ls="--")
    uv.set_ylabel("Prescribed UV scale Q", color="#0072B2"); uv.set_ylim(-.03, 1.03)
    ax.set_title("External temperature and UV inputs", fontsize=11)
    ax = axes[1, 0]
    envelope(ax, cases, "tau_T")
    ax.plot(z, diagnostic(case, "tau_T"), color="#D55E00", lw=1.2, ls="--")
    ax.set_ylabel(r"Accumulated Thomson $\tau_T$")
    ax.set_title("Opacity uses the same evolving electron density", fontsize=11)
    ax = axes[1, 1]
    for index, color, label, style in ((4, "#D55E00", r"Photons $\widetilde\Pi_\gamma$", "-"),
                                       (5, "#0072B2", r"Neutrinos $\widetilde\Pi_\nu$", "--"),
                                       (2, "#222222", r"Sum $\widetilde\Pi_r$", ":")):
        ax.plot(z, case["data"]["signed_observables"][:, index], color=color, label=label, ls=style, lw=1.5)
    ax.set_yscale("symlog", linthresh=1e-8, linscale=.45); ax.set_ylabel("Signed normalized stress")
    ax.set_title("Photon scattering; collisionless neutrinos", fontsize=11)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.28), ncol=2, frameon=False, fontsize=9)
    ax = axes[2, 0]
    envelope(ax, cases, "trace_energy_fraction")
    ax.axhline(1e-5, color="#777777", ls=":", lw=1.2)
    ax.set_yscale("log"); ax.set_ylabel(r"$(u_{\rm th}+u_{\rm ion}+u_{\rm UV})/\rho_{\rm crit}(t)$")
    ax.set_title("Test-fluid energy diagnostic; dotted gate = 1e-5", fontsize=11)
    ax = axes[2, 1]
    fields = [("net_required_gas_input_W_m3", "Required net gas input", "#222222", "-"),
              ("photo_absorbed_W_m3", "Absorbed UV power", "#D55E00", "--"),
              ("bath_minus_escape_W_m3", "Bath minus escape", "#0072B2", "-."),
              ("unresolved_core_W_m3", "Li I core excitation ledger", "#CC79A7", ":")]
    maximum = max(float(np.max(abs(diagnostic(case, name)))) for name, *_ in fields)
    for name, label, color, style in fields:
        ax.plot(z, diagnostic(case, name), label=label, color=color, ls=style, lw=1.5)
    ax.set_yscale("symlog", linthresh=max(1e-60, maximum * 1e-12), linscale=.45)
    ax.set_ylabel(r"Power density [W m$^{-3}$]"); ax.set_title("Energy bookkeeping for the imposed gas path", fontsize=11)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.29), ncol=2, frameon=False, fontsize=8.8)
    for ax in axes.flat:
        decorate_axis(ax)
    header(fig, "Atomic-opacity coupling and retained energy diagnostics", context, "Representative " + case["id"])
    fig.text(.5, .098, "Envelopes: completed-case min-max and median. Dashed orange electron / opacity curve: representative case.", ha="center", fontsize=9)
    fig.text(.5, .070, "Absorption and unresolved core energy are bookkeeping terms. They do not specify thermal deposition or Auger yields.", ha="center", fontsize=9)
    fig.text(.5, .045, "The finite energy-ratio check supports the stated test-fluid comparison; global convergence remains NOT_RUN.", ha="center", fontsize=9)
    return export(fig, output, "04_atomic_opacity_energy_diagnostics")


def captions(context, selected):
    return f'''# Figure captions — conditional preliminary pilot

These figures use **{context['completed_plotted']} hash-verified completed cases out of {context['planned_cases']} planned cases**. The case loader verifies the frozen scientific identity, COMPLETE → RESULT → trajectory byte hashes, the full 193-node redshift interval, species order, Frobenius normalization, signed component sums, and electron abundance consistency. Uncompleted cases do not contribute to envelopes or points. Their sweep cells remain blank.

## 01 — Shear and separate stress evolution

All curves are saved trajectories from z=20 to z=2. Shading gives the min–max of completed cases and the black line their median; this is a sampled parameter envelope, not an uncertainty interval or an error bound. Colored curves identify actual initial physical coordinates. The plotted norms are Sigma_F=sqrt(6)|s|/H and Pi_A=sqrt(6) kappa_t |p_A|/H², with kappa_t=8 pi G/c² for energy-density stresses. Signed matter and radiation components are added before taking the total norm. Half-contraction values equal Frobenius values divided by sqrt(2). Symlog axes retain zeros.

## 02 — Physical three-axis sweep

Each endpoint scatter point is one completed case at z=2. The horizontal coordinate is final Sigma_F, the vertical coordinate is signed matter or radiation stress, and color gives initial Sigma_F. The lower panels show signed total stress at the nearest saved node to z=8 and at z=2 on a fixed initial-Sigma slice. Their axis coordinates are initial physical signed Pi_m and Pi_r, not amplitude coefficients A_m/A_r. The actual saved redshift and slice value appear in the titles. Cells are discrete samples without interpolation; grey cells have no completed result.

## 03 — All retained ionic states

Representative case: `{selected}`. Each curve is the saved number abundance divided by that isotope's initial total inventory. No clipping or instantaneous renormalization is applied. H1 and D have charges 0–1; He3 and He4 have charges 0–2; Li6 and Li7 have charges 0–3, including Li IV. The shared electronic rates across isotopes are an explicit elemental-electronic-equality approximation. The frozen pilot has zero initial neutron and tritium inventory; their saved zero-population status is annotated rather than displayed as active histories. Symlog axes show trace ionic fractions and retain exact zero.

## 04 — Opacity and energy bookkeeping

The same evolving 21-state ion populations supply n_e for the photon Thomson operator and optical-depth integral. Neutrinos remain collisionless. Gas temperature and optically thin UV are prescribed external functions, and the baryonic gas is isotropic. Thermal, ionization, and external-UV energies are retained as test-fluid diagnostics; their energy ratio is not fed back into the Einstein background. Required net gas input, absorbed UV power, bath-minus-escape, and Li I core excitation remain distinct. Neutral-Li inner-shell events use the explicitly assumed single-step charge yield; neither these figures nor the absorption coefficients determine Auger branching or a heating yield.

**Scope:** conditional prescribed T/UV preliminary model; Physical HOLD; global convergence NOT_RUN; production NOT_APPROVED. Existing REC U5 HOLD is unchanged. These plots do not constitute a fully closed thermal, radiation-transfer, or photonuclear calculation.
'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "results/pilot")
    parser.add_argument("--output", type=Path, default=ROOT / "figures")
    args = parser.parse_args(argv)
    cases, context = load_cases(args.input)
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.bbox": None, "pdf.fonttype": 42})
    artifacts = plot_evolution(cases, context, args.output)
    artifacts += plot_sweep(cases, context, args.output)
    paths, selected = plot_ions(cases, context, args.output)
    artifacts += paths
    artifacts += plot_coupling(cases, context, args.output)
    caption = args.output / "CAPTIONS.md"
    caption.write_text(captions(context, selected))
    artifacts.append({"path": str(caption.resolve()), "bytes": caption.stat().st_size, "sha256": sha(caption)})
    receipt = {"status": "BUILT_FROM_VERIFIED_SAVED_TRAJECTORIES", "new_ODE": 0, "new_NCP": 0,
               "plot_code_sha256": sha(Path(__file__)), "context": context, "representative_case": selected,
               "case_evidence": [{k: v for k, v in c.items() if k != "data"} for c in cases], "artifacts": artifacts,
               "visual_review": "PENDING_DIRECT_VIEW", "physical": "HOLD", "global_convergence": "NOT_RUN"}
    evidence = ROOT / "evidence/PLOT_BUILD.json"
    if evidence.exists():
        old = evidence.with_name("PLOT_BUILD_PREVIOUS_" + sha(evidence)[:12] + ".json")
        if not old.exists():
            old.write_bytes(evidence.read_bytes())
    evidence.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"completed_plotted": len(cases), "planned": context["planned_cases"], "artifacts": artifacts}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print("PLOT_INPUT_REJECTED: " + str(error), file=sys.stderr)
        raise SystemExit(2)

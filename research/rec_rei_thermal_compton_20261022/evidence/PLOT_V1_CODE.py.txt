"""Data-only THERM02 figures and exact CSV sources; no science imports.

``make_figures()`` reads the eight finished trajectory NPZs and optional
retained THERM01 baselines. It never instantiates a physics system, solves
an ODE, re-evaluates an RHS, or interpolates one history onto another.
All differences use the common saved x grid. Signed values remain signed.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
EV_J = 1.602176634e-19
CASES = (
    "t02_split_mao_off",
    "t02_split_mao_hot",
    "t02_split_mao_planck",
    "t02_split_derivative_planck",
    "t02_iso_mao_planck",
    "t02_split_mao_hot_tight34",
    "t02_split_mao_planck_tight34",
    "t02_split_mao_planck_oracle63",
)
OFF, HOT, PLANCK, DERIVATIVE, ISO, HOT_TIGHT, PLANCK_TIGHT, ORACLE = CASES
BASELINES = ("thermal_split60", "thermal_iso60")
OBSERVABLES = ("Sigma_F", "Pi_matter", "Pi_radiation", "Pi_total",
               "Pi_gamma", "Pi_nu")
LEDGER_NAMES = ("absorption", "escape", "adiabatic_work",
                "CMB_or_reference", "UV_Compton")
BRANCH_LABELS = {
    OFF: "Mao hybrid / Compton off",
    HOT: "Mao / actual-photon hot term + UV",
    PLANCK: "Mao / external Planck bath + UV",
    "thermal_split60": "Prior derivative / Compton off",
}
COLORS = {OFF: "#3d3d3d", HOT: "#0072b2", PLANCK: "#d55e00",
          "thermal_split60": "#9a9a9a"}
STYLES = {OFF: "-.", HOT: "--", PLANCK: "-", "thermal_split60": ":"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass
class History:
    name: str
    path: Path
    raw_sha256: str
    data: dict
    diagnostics: dict
    receipt_path: Path | None

    @property
    def x(self):
        return self.data["x"]

    @property
    def z(self):
        return self.data["z"]

    @property
    def electrons(self):
        # This observable is the current electron abundance per baryon.
        # It does not assume a particular species-index layout.
        return self.diagnostics["ne_m3"] / self.diagnostics["nb_m3"]


def _load(path, name, *, baseline=False):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Finished trajectory required: {path}")
    receipt_path = path.with_name("RESULT.json")
    raw_hash = digest(path)
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt.get("status") != "PASS":
            raise ValueError(f"Refusing a non-PASS result: {name}")
        expected = receipt.get("raw_sha256")
        if expected is not None and expected != raw_hash:
            raise ValueError(f"Trajectory hash disagrees with RESULT.json: {name}")
    else:
        raise FileNotFoundError(f"Finished-result receipt required: {receipt_path}")
    with np.load(path, allow_pickle=False) as archive:
        data = {key: archive[key].copy() for key in archive.files}
    required = {"x", "z", "diagnostics", "diagnostic_names", "Y",
                "scaled_populations", "signed_observables", "ledger_GL8",
                "ledger_GL16", "ledger_normalized_residual",
                "ledger_denominator_J", "ledger_GL_difference"}
    if not baseline:
        required.add("ledger_abs_GL16")
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Incomplete plot input {name}: {missing}")
    x, z = data["x"], data["z"]
    if (x.ndim != 1 or z.shape != x.shape or len(x) < 2 or
            not np.isfinite(x).all() or not np.isfinite(z).all() or
            not np.all(np.diff(x) > 0)):
        raise ValueError(f"Invalid saved comparison grid: {name}")
    n = len(x)
    names = [str(key) for key in data["diagnostic_names"]]
    if (len(set(names)) != len(names) or
            data["diagnostics"].shape != (n, len(names))):
        raise ValueError(f"Diagnostic name/array mismatch: {name}")
    diagnostics = {key: data["diagnostics"][:, i]
                   for i, key in enumerate(names)}
    for key in ("T_K", "nb_m3", "ne_m3", "tau_T", "epsilon_total_J"):
        if key not in diagnostics or not np.isfinite(diagnostics[key]).all():
            raise ValueError(f"Missing/nonfinite diagnostic {key}: {name}")
    if np.any(diagnostics["nb_m3"] <= 0) or np.any(diagnostics["T_K"] <= 0):
        raise ValueError(f"Invalid temperature/baryon density: {name}")
    ledger_width = 3 if baseline else 5
    for key, shape in (("Y", (n, 21)), ("scaled_populations", (n, 21)),
                       ("signed_observables", (n, 6)),
                       ("ledger_GL8", (n, ledger_width)),
                       ("ledger_GL16", (n, ledger_width))):
        if data[key].shape != shape or not np.isfinite(data[key]).all():
            raise ValueError(f"Invalid {key} array: {name}")
    for key in ("ledger_normalized_residual", "ledger_denominator_J",
                "ledger_GL_difference"):
        if data[key].shape != (n,) or not np.isfinite(data[key]).all():
            raise ValueError(f"Invalid {key} vector: {name}")
    if not baseline:
        if data["ledger_abs_GL16"].shape != (n, 5):
            raise ValueError(f"Invalid absolute-throughput ledger: {name}")
        if not np.isfinite(data["ledger_abs_GL16"]).all():
            raise ValueError(f"Nonfinite absolute-throughput ledger: {name}")
    return History(name, path, raw_hash, data, diagnostics, receipt_path)


def _same_grid(a, b):
    if not np.array_equal(a.x, b.x) or not np.array_equal(a.z, b.z):
        raise ValueError(f"Plot comparisons need identical saved grids: {a.name}, {b.name}")


def _difference(lhs, rhs):
    _same_grid(lhs, rhs)
    return {
        "relative_T": (lhs.diagnostics["T_K"] - rhs.diagnostics["T_K"])
                      / rhs.diagnostics["T_K"],
        "electron_abundance": lhs.electrons - rhs.electrons,
        "tau_T": lhs.diagnostics["tau_T"] - rhs.diagnostics["tau_T"],
        **{key: lhs.data["signed_observables"][:, i]
           - rhs.data["signed_observables"][:, i]
           for i, key in enumerate(OBSERVABLES)},
    }


def _csv(path, columns):
    names = list(columns)
    arrays = [np.asarray(columns[key]) for key in names]
    if not arrays or any(a.ndim != 1 or len(a) != len(arrays[0]) for a in arrays):
        raise ValueError(f"Unequal plotting CSV column lengths: {path}")
    with Path(path).open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(names)
        # 17 significant digits retain round-trip identity of float64 data.
        writer.writerows([format(float(value), ".17g") for value in row]
                         for row in zip(*arrays))


def _export_history(root, history):
    d, diag = history.data, history.diagnostics
    columns = {"x": history.x, "z": history.z}
    columns.update({"diagnostic_" + key: value for key, value in diag.items()})
    columns["electron_abundance_ne_over_nb"] = history.electrons
    for key in ("Y", "scaled_populations", "signed_observables"):
        labels = OBSERVABLES if key == "signed_observables" else range(21)
        for i, label in enumerate(labels):
            columns[f"{key}_{label}"] = d[key][:, i]
    for method in ("ledger_GL8", "ledger_GL16", "ledger_abs_GL16"):
        if method in d:
            for i in range(d[method].shape[1]):
                columns[f"{method}_{LEDGER_NAMES[i]}_J_per_baryon"] = d[method][:, i]
    for key in ("ledger_residual_J", "ledger_denominator_J",
                "ledger_normalized_residual", "ledger_GL_difference"):
        if key in d:
            columns[key] = d[key]
    epsilon_change = diag["epsilon_total_J"] - diag["epsilon_total_J"][0]
    columns["delta_epsilon_total_eV_per_baryon"] = epsilon_change / EV_J
    for i in range(d["ledger_GL16"].shape[1]):
        sign = -1. if i in (1, 2) else 1.
        columns[f"signed_gas_{LEDGER_NAMES[i]}_eV_per_baryon"] = (
            sign * d["ledger_GL16"][:, i] / EV_J)
    path = root / "results" / f"PLOT_DATA_{history.name}.csv"
    _csv(path, columns)
    return path


def _axis_redshift(ax, x):
    redshifts = np.array([20., 10., 7., 5., 3., 2.])
    positions = np.log(21. / (1. + redshifts))
    selected = (positions >= x[0] - 1e-12) & (positions <= x[-1] + 1e-12)
    ax.set_xlim(x[0], x[-1])
    ax.set_xticks(positions[selected], [f"{z:g}" for z in redshifts[selected]])
    ax.set_xlabel("Redshift z  (time increases to the right)")


def _positive_display(values):
    # Only logarithmic display is masked; CSVs retain exact zeros and signs.
    a = np.asarray(values)
    return np.where(a > 0, a, np.nan)


def _signed_scale(ax, values, *, floor=1e-16, fraction=1e-5):
    peak = max((float(np.max(np.abs(v))) for v in values), default=0.)
    linear = max(floor, peak * fraction)
    ax.set_yscale("symlog", linthresh=linear, linscale=1.)
    ax.axhline(0., color="#8a8a8a", lw=.65, zorder=0)
    ax.text(.02, .02, f"Signed symlog; linear below {linear:.1e}",
            transform=ax.transAxes, fontsize=7.4, color="#505050",
            va="bottom", bbox={"facecolor": "white", "alpha": .8, "edgecolor": "none"})
    return linear


def _save(root, fig, stem):
    paths = []
    for suffix in ("png", "pdf"):
        path = root / "figures" / f"{stem}.{suffix}"
        fig.savefig(path, dpi=190 if suffix == "png" else None,
                    bbox_inches="tight", facecolor="white")
        paths.append(path)
    plt.close(fig)
    return paths


def _thermal_figure(root, histories, differences):
    fig, axes = plt.subplots(3, 2, figsize=(12.8, 12.), layout="constrained")
    physical = [OFF, HOT, PLANCK]
    if "thermal_split60" in histories:
        physical.insert(0, "thermal_split60")
    for name in physical:
        h = histories[name]
        kw = dict(color=COLORS[name], ls=STYLES[name], lw=1.9,
                  label=BRANCH_LABELS[name])
        axes[0, 0].plot(h.x, h.diagnostics["T_K"], **kw)
        axes[1, 0].plot(h.x, h.electrons, **kw)
        axes[2, 0].plot(h.x, h.diagnostics["tau_T"], **kw)
    axes[0, 0].set_yscale("log")
    axes[0, 0].set_ylabel("Gas temperature [K]")
    axes[1, 0].set_ylabel(r"Electron abundance $n_e/n_b$")
    axes[2, 0].set_ylabel(r"Thomson optical depth $\tau_T$")
    axes[0, 0].set_title("Current-state thermal and ionic evolution")
    axes[0, 0].legend(fontsize=8, loc="upper left")
    comparisons = [
        ("hot_minus_off", "Hot + UV − off (Mao)", "#0072b2", "-"),
        ("planck_minus_hot", "External Planck − actual hot (Mao)", "#d55e00", "-"),
        ("derivative_minus_mao_planck", "Derivative − Mao (external Planck)", "#009e73", "--"),
    ]
    if "mao_off_minus_prior_derivative_off" in differences:
        comparisons.insert(0, ("mao_off_minus_prior_derivative_off",
                               "Mao − prior derivative (off)", "#aa4499", ":"))
    keys = ("relative_T", "electron_abundance", "tau_T")
    labels = (r"Signed $\Delta T/T_{\rm right\ case}$",
              r"Signed $\Delta(n_e/n_b)$", r"Signed $\Delta\tau_T$")
    x = histories[PLANCK].x
    for row, (key, label) in enumerate(zip(keys, labels)):
        values = []
        for pair, title, color, style in comparisons:
            y = differences[pair][key]
            values.append(y)
            axes[row, 1].plot(x, y, label=title, color=color, ls=style, lw=1.7)
        _signed_scale(axes[row, 1], values)
        axes[row, 1].set_ylabel(label)
    axes[0, 1].set_title("Changes from the explicitly named right-hand case")
    axes[0, 1].legend(fontsize=7.8, loc="upper left")
    for ax in axes.flat:
        _axis_redshift(ax, x)
    fig.suptitle("THERM02 · source and bath changes in the coupled gas\n"
                 "21 populations; prescribed 5–60 eV smooth continuum; conditional RR cooling",
                 fontsize=13)
    return _save(root, fig, "01_temperature_ionization_opacity")


def _energy_figure(root, histories):
    fig, axes = plt.subplots(2, 2, figsize=(13., 9.5), layout="constrained")
    term_colors = ("#009e73", "#cc79a7", "#7a5600", "#0072b2", "#d55e00")
    term_styles = ("--", "-.", ":", "-", "--")
    term_labels = (r"$+I_{\rm abs}$", r"$-I_{\rm escape}$",
                   r"$-I_{\rm work}$", r"$+I_{\rm C}$", r"$+I_{\rm UV,C}$")
    all_energy = []
    for name in (HOT, PLANCK):
        h = histories[name]
        all_energy.extend(h.data["ledger_GL16"].T / EV_J)
    common_peak = max(float(np.max(np.abs(v))) for v in all_energy)
    common_linear = max(1e-8, common_peak * 1e-6)
    for ax, name, title in zip(axes[0], (HOT, PLANCK), (
            "Actual grey photons: hot term + external UV",
            "External Planck bath + external UV")):
        h = histories[name]
        change = (h.diagnostics["epsilon_total_J"]
                  - h.diagnostics["epsilon_total_J"][0]) / EV_J
        ax.plot(h.x, change, color="#111111", lw=2.2,
                label=r"$\Delta\epsilon_{\rm gas}$")
        for i, (label, color, style) in enumerate(zip(term_labels, term_colors, term_styles)):
            sign = -1. if i in (1, 2) else 1.
            ax.plot(h.x, sign * h.data["ledger_GL16"][:, i] / EV_J,
                    color=color, ls=style, lw=1.6, label=label)
        _signed_scale(ax, [np.array([common_peak])], floor=common_linear, fraction=0.)
        ax.set_ylabel("Signed gas-energy contribution [eV / baryon]")
        ax.set_title(title, fontsize=10)
        ax.legend(ncol=2, fontsize=8, loc="upper left")
    ax = axes[1, 0]
    for name, color, label in ((HOT, COLORS[HOT], "actual hot"),
                               (PLANCK, COLORS[PLANCK], "external Planck")):
        h = histories[name]
        ax.plot(h.x, _positive_display(h.data["ledger_normalized_residual"]),
                color=color, lw=1.8, label=label + " ledger residual")
        ax.plot(h.x, _positive_display(h.data["ledger_GL_difference"]),
                color=color, ls=":", lw=1.4, label=label + " GL8–GL16")
    ax.axhline(3e-6, color="#a50f15", ls="--", lw=1., label="Frozen 3 × 10⁻⁶ gate")
    ax.set_yscale("log")
    ax.set_ylabel("Normalized absolute residual / quadrature change")
    ax.set_title("Absolute throughput integrated before normalization", fontsize=10)
    ax.legend(ncol=2, fontsize=7.8, loc="lower right")
    ax = axes[1, 1]
    for name, field, label, color, style in (
            (HOT, "compton_over_HUgamma", r"Hot / actual $H U_\gamma$", COLORS[HOT], "-"),
            (PLANCK, "compton_over_HUref", r"Planck / external $H U_{\rm ref}$", COLORS[PLANCK], "-"),
            (PLANCK, "compton_over_HUgamma", r"Planck / actual $H U_\gamma$ (scale only)", "#6b4c9a", "--")):
        h = histories[name]
        if field not in h.diagnostics:
            raise ValueError(f"Missing exchange-ratio diagnostic {field}: {name}")
        ax.plot(h.x, _positive_display(h.diagnostics[field]),
                color=color, ls=style, lw=1.7, label=label)
    ax.set_yscale("log")
    ax.set_ylabel(r"$|Q_{\rm C}|/(H U)$ with the labelled energy owner")
    ax.set_title("Measured exchange scale; no backreaction error bound", fontsize=10)
    ax.legend(fontsize=7.9, loc="best")
    for ax in axes.flat:
        _axis_redshift(ax, histories[PLANCK].x)
    fig.suptitle("THERM02 · signed gas ledger and separately owned radiation baths\n"
                 "Bath debits are passive; photon / Einstein backreaction remains omitted",
                 fontsize=13)
    return _save(root, fig, "02_signed_energy_transfer")


def _stress_figure(root, histories, differences):
    fig, axes = plt.subplots(3, 2, figsize=(12.8, 12.), layout="constrained")
    h = histories[PLANCK]
    for i, label, color, style in ((1, "Collisionless massive matter", "#d55e00", "-"),
                                    (2, "Photons + neutrinos", "#0072b2", "--"),
                                    (3, "Signed sum", "#111111", "-")):
        axes[0, 0].plot(h.x, h.data["signed_observables"][:, i],
                        label=label, color=color, ls=style, lw=1.8)
    axes[0, 0].axhline(0., color="#8a8a8a", lw=.7)
    axes[0, 0].set_ylabel("Signed normalized anisotropic stress")
    axes[0, 0].set_title("Split seed · Mao / external Planck branch")
    axes[0, 0].legend(fontsize=8)
    for name, label, color, style in ((PLANCK, "Split seed", "#111111", "-"),
                                     (ISO, "Isotropic seed", "#aa4499", "--")):
        s = histories[name]
        axes[0, 1].plot(s.x, s.data["signed_observables"][:, 0],
                       label=label, color=color, ls=style, lw=1.8)
    axes[0, 1].axhline(0., color="#8a8a8a", lw=.7)
    axes[0, 1].set_ylabel(r"Signed shear $\Sigma_F$")
    axes[0, 1].set_title("Common Mao / external Planck source")
    axes[0, 1].legend(fontsize=8)
    pairs = (
        ("planck_minus_hot", "External Planck − actual hot", "#d55e00", "-", 2.),
        ("hot_tight_minus_nominal", "Hot tight34 − nominal", "#0072b2", "--", 1.4),
        ("planck_tight_minus_nominal", "Planck tight34 − nominal", "#111111", ":", 1.4),
        ("planck_oracle_minus_nominal", "Planck full63 − compact34", "#7b7b7b", "-.", 1.2),
    )
    for ax, key, title in zip(axes[1:].flat,
                             ("Pi_matter", "Pi_radiation", "Pi_total", "Sigma_F"),
                             ("Matter", "Radiation", "Signed total stress", "Shear")):
        values = []
        for pair, label, color, style, width in pairs:
            y = differences[pair][key]
            values.append(y)
            ax.plot(h.x, y, label=label, color=color, ls=style, lw=width)
        _signed_scale(ax, values, floor=1e-18)
        ax.set_ylabel("Signed difference (same normalization)")
        ax.set_title(title)
    axes[1, 0].legend(fontsize=7.7, loc="best")
    for ax in axes.flat:
        _axis_redshift(ax, h.x)
    fig.suptitle("THERM02 · signed sources and finite branch discrimination\n"
                 "Observed tight / full63 changes are comparisons, not global error bounds",
                 fontsize=13)
    return _save(root, fig, "03_signed_stress_branch_changes")


def make_figures(root=None):
    """Build three PNG/PDF pairs and CSV/hash provenance from finished data.

    The eight frozen THERM02 cases must each have a PASS RESULT.json and
    trajectory.npz. Optional copied THERM01 baselines stay separately named.
    Return the JSON-serializable manifest; write only figures/* and
    results/PLOT_DATA_* inside the specified unit.
    """
    root = ROOT if root is None else Path(root).resolve()
    histories = {name: _load(root / "data" / name / "trajectory.npz", name)
                 for name in CASES}
    for name in BASELINES:
        path = root / "baseline" / name / "trajectory.npz"
        if path.exists():
            histories[name] = _load(path, name, baseline=True)
    for history in histories.values():
        _same_grid(histories[PLANCK], history)
    pairs = {
        "hot_minus_off": (HOT, OFF),
        "planck_minus_hot": (PLANCK, HOT),
        "derivative_minus_mao_planck": (DERIVATIVE, PLANCK),
        "iso_minus_split_planck": (ISO, PLANCK),
        "hot_tight_minus_nominal": (HOT_TIGHT, HOT),
        "planck_tight_minus_nominal": (PLANCK_TIGHT, PLANCK),
        "planck_oracle_minus_nominal": (ORACLE, PLANCK),
    }
    if "thermal_split60" in histories:
        pairs["mao_off_minus_prior_derivative_off"] = (OFF, "thermal_split60")
    if "thermal_iso60" in histories:
        pairs["iso_mao_planck_minus_prior_derivative_off"] = (ISO, "thermal_iso60")
    differences = {key: _difference(histories[lhs], histories[rhs])
                   for key, (lhs, rhs) in pairs.items()}
    (root / "figures").mkdir(exist_ok=True)
    (root / "results").mkdir(exist_ok=True)
    outputs = [_export_history(root, history) for history in histories.values()]
    columns = {"x": histories[PLANCK].x, "z": histories[PLANCK].z}
    for pair, fields in differences.items():
        for key, values in fields.items():
            columns[f"{pair}__{key}"] = values
    difference_path = root / "results" / "PLOT_DATA_signed_comparisons.csv"
    _csv(difference_path, columns)
    outputs.append(difference_path)
    style = {"font.family": "DejaVu Sans", "font.size": 9.5,
             "axes.grid": True, "grid.alpha": .2,
             "axes.spines.top": False, "axes.spines.right": False,
             "axes.titlepad": 8, "legend.framealpha": .9,
             "savefig.facecolor": "white", "pdf.fonttype": 42}
    with plt.rc_context(style):
        outputs += _thermal_figure(root, histories, differences)
        outputs += _energy_figure(root, histories)
        outputs += _stress_figure(root, histories, differences)
    manifest = {
        "schema": "THERM02_DATA_ONLY_PLOTS_v1",
        "plot_code_sha256": digest(Path(__file__)),
        "frozen_contract_sha256": digest(root / "FROZEN_CONTRACT.md"),
        "new_science_runs_for_plotting": 0,
        "ODE_calls_for_plotting": 0,
        "case_ids": list(CASES),
        "retained_baseline_ids": [name for name in BASELINES if name in histories],
        "inputs": {name: {"path": str(h.path.relative_to(root)),
                          "sha256": h.raw_sha256,
                          "result_receipt_sha256": digest(h.receipt_path)}
                   for name, h in histories.items()},
        "comparison_definitions": {key: {"left": lhs, "right": rhs,
                                          "relative_T_denominator": rhs}
                                   for key, (lhs, rhs) in pairs.items()},
        "comparison_peaks_absolute": {
            pair: {key: float(np.max(np.abs(value))) for key, value in fields.items()}
            for pair, fields in differences.items()},
        "outputs": {str(path.relative_to(root)): {"sha256": digest(path),
                                                  "bytes": path.stat().st_size}
                    for path in outputs},
        "notes": [
            "Read saved NPZs only; no physics module import, RHS evaluation or integration.",
            "All case comparisons use exactly equal saved x and z grids; no interpolation.",
            "CSV floating values have 17 significant digits for float64 round trips.",
            "Signed curves retain signs. Log-only display masks exact zeros; CSVs retain them.",
            "Energy signs are +absorption, -escape, -work, +CMB/reference, +UV Compton.",
            "Actual-grey hot exchange and external Planck exchange are alternative owners.",
            "Bath ledger debits do not implement photon or Einstein backreaction.",
            "Observed numerical differences are finite comparisons, not global error bounds.",
            "THERM01 copied baselines remain a separate completed cohort.",
        ],
        "flags": {"Physical": "HOLD", "REC_U5": "HOLD",
                  "global_convergence": "NOT_RUN", "production": "NOT_APPROVED",
                  "REI_activation": False},
    }
    manifest_path = root / "results" / "PLOT_DATA_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"DATA-ONLY FIGURES: 3 PNG + 3 PDF; {len(histories) + 1} exact CSVs; "
          f"manifest={manifest_path}", flush=True)
    return manifest


if __name__ == "__main__":
    make_figures()

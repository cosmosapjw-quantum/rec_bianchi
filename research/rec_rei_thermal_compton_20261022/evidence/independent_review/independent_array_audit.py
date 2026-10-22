"""One bounded, data-only THERM02 review calculation.

No THERM02 or donor Python module is imported. No rate, RHS or ODE is called.
The retained five-source quadrature is reconstructed with SciPy Legendre
weights and math.fsum, independently of the runner's NumPy/einsum/cumsum path.
All writes stay in this review directory.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
from scipy.constants import sigma as STEFAN_BOLTZMANN
from scipy.special import roots_legendre

ROOT = Path("/workspace/scratch/a6dfe82cc85f/repos/rec_bianchi/research/rec_rei_thermal_compton_20261022")
OUT = Path(__file__).resolve().parent
BASE = ROOT / "vendor/therm01/vendor/rei_pr220/vendor/rec_hheli"
CASES = (
    "t02_split_mao_off", "t02_split_mao_hot", "t02_split_mao_planck",
    "t02_split_derivative_planck", "t02_iso_mao_planck",
    "t02_split_mao_hot_tight34", "t02_split_mao_planck_tight34",
    "t02_split_mao_planck_oracle63",
)
OBS = ("Sigma_F", "Pi_matter", "Pi_radiation", "Pi_total", "Pi_gamma", "Pi_nu")
LEDGER = ("absorption", "escape", "adiabatic_work", "CMB_or_reference", "UV_Compton")
Q = np.array([0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3])
Z = np.array([0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3])
A = np.array([1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 6, 6, 6, 6, 7, 7, 7, 7])
GROUPS = ((0,), (1, 2), (3, 4), (5, 6), (7, 8, 9), (10, 11, 12),
          (13, 14, 15, 16), (17, 18, 19, 20))
KB, EV, C = 1.380649e-23, 1.602176634e-19, 299792458.
ME, HP, SIGMA = 9.1093837139e-31, 6.62607015e-34, 6.6524587051e-29
K = SIGMA / (ME * C)
ARAD = 8 * math.pi**5 * KB**4 / (15 * HP**3 * C**3)
failures = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(condition, message):
    if not condition:
        failures.append(message)


def maximum(value):
    return float(np.max(np.abs(value)))


def rel(a, b, floor=1e-300):
    return maximum((np.asarray(a) - b) / np.maximum(np.maximum(abs(np.asarray(a)), abs(np.asarray(b))), floor))


def archive(path):
    with np.load(path, allow_pickle=False) as f:
        return {k: f[k].copy() for k in f.files}


def diagnostics(a):
    return {str(k): a["diagnostics"][:, i] for i, k in enumerate(a["diagnostic_names"])}


def lift(states):
    if states.shape[1] == 63:
        return states
    check(states.shape[1] == 34, "unexpected compact state width")
    geometry = [0, 1, 2] + [s + k for s in (4, 13, 22, 31) for k in (0, 2, 4, 6, 8)]
    select = geometry + [40 + k for k in (1, 2, 10, 11, 12, 17, 18, 19, 20)] + [61, 62]
    full = np.zeros((len(states), 63))
    full[:, select] = states
    for target, source in ((3, 1), (4, 2), (7, 10), (8, 11), (9, 12),
                           (13, 17), (14, 18), (15, 19), (16, 20)):
        full[:, 40 + target] = full[:, 40 + source]
    return full


def integrate(grid, values, order):
    nodes, weights = roots_legendre(order)
    values = values.reshape(len(grid) - 1, order, -1)
    half = np.diff(grid) / 2
    integrated, throughput = [], []
    for i, v in enumerate(values):
        integrated.append([half[i] * math.fsum(float(weights[j] * v[j, k]) for j in range(order))
                           for k in range(v.shape[1])])
        throughput.append([half[i] * math.fsum(float(weights[j] * abs(v[j, k])) for j in range(order))
                           for k in range(v.shape[1])])
    def accumulated(rows):
        n = len(rows[0])
        return np.array([[0.] * n] + [[math.fsum(row[k] for row in rows[:i]) for k in range(n)]
                                     for i in range(1, len(rows) + 1)])
    return accumulated(integrated), accumulated(throughput), nodes


def finite_scope(states, x, raw):
    full = lift(states)
    Y = full[:, 40:61] * raw["isotope_scales"]
    xe = Y @ Q
    eta = Y.sum(axis=1) + xe
    T = 2 * full[:, 62] / (3 * eta)
    isotope_error = max(maximum(Y[:, list(g)].sum(axis=1) - raw["initial_Y"][list(g)].sum())
                        / raw["isotope_scales"][g[0]] for g in GROUPS)
    result = dict(count=len(x), finite=bool(np.isfinite(full).all()),
        minimum_scaled_population=float(full[:, 40:61].min()),
        baryon_max_abs=maximum(Y @ A - 1), isotope_max_scaled=isotope_error,
        electron_abundance_min=float(xe.min()), T_min_K=float(T.min()), T_max_K=float(T.max()),
        minimum_tau_increment=float(np.diff(full[:, 61]).min()),
        number_monopole_max_abs=max(maximum(full[:, 13] - 1), maximum(full[:, 31] - 1)),
        absent_n_tritium_exact_zero=bool(np.all(full[:, [40, 45, 46]] == 0)))
    return result


def main():
    started = time.perf_counter()
    report = dict(kind="one bounded independent retained-array audit", source_python_imports=0,
                  RHS_calls=0, cosmological_IVPs=0, old_suite_runs=0, reviewer_calculation_count=1,
                  command="OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python /workspace/scratch/a6dfe82cc85f/thermal02_work/independent_review/independent_array_audit.py",
                  source_hashes={}, cases={}, comparisons={}, branch_resolution={}, CSV_bindings={})
    for p in ("FROZEN_CONTRACT.md", "THEORY.md", "code/coupled_thermal.py", "code/checks.py",
              "code/run.py", "code/plot.py", "provenance/REUSED_FILES.json",
              "evidence/PRE_ODE_CHECKS.json", "evidence/RUNNER_STATIC_CHECKS.json"):
        report["source_hashes"][p] = sha(ROOT / p)
    manifest = json.loads((ROOT / "provenance/REUSED_FILES.json").read_text())
    for row in manifest["files"]:
        content = (ROOT / row["path"]).read_bytes()
        check(len(content) == row["bytes"] and hashlib.sha256(content).hexdigest() == row["sha256"],
              "retained input identity: " + row["path"])
        blob = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
        check(blob == row["git_blob_sha"], "retained Git blob identity: " + row["path"])
    report["retained_input_files_verified"] = len(manifest["files"])

    coefficients = json.loads((BASE / "data/atomic_coefficients.json").read_text())
    binding = np.array([math.fsum(coefficients["photo_VF1996"][f"{z}:{q}"]["Eth_eV"]
                                 for q in range(int(charge))) * EV for z, charge in zip(Z, Q)])
    histories, diag, receipts = {}, {}, {}
    for name in CASES:
        directory = ROOT / "data" / name
        receipt = json.loads((directory / "RESULT.json").read_text())
        receipts[name] = receipt
        check(receipt["status"] == "PASS", "case PASS receipt: " + name)
        for relative, record in receipt["artifacts"].items():
            p = directory / relative
            check(p.stat().st_size == record["bytes"] and sha(p) == record["sha256"],
                  "case artifact binding: " + name + "/" + relative)
        for p, recorded_hash in receipt["identity"]["sources"].items():
            check(sha(ROOT / p) == recorded_hash, "case execution source binding: " + name + "/" + p)
        a = archive(directory / "trajectory.npz")
        returned = archive(directory / "solver_return.npz")
        histories[name], diag[name] = a, diagnostics(a)
        d = diag[name]
        x = a["x"]
        check(x.shape == (193,) and np.array_equal(x, np.linspace(0., math.log(7), 193)), "saved193 grid: " + name)
        check(np.array_equal(a["q"], Q) and np.array_equal(a["A"], A), "species charge/baryon layout: " + name)
        check(np.array_equal(returned["x"], a["accepted_x"]) and np.array_equal(returned["raw_state"], a["accepted_raw_state"]), "accepted BDF raw identity: " + name)
        full = lift(a["raw_state"])
        check(np.array_equal(full, a["full63_state"]), "explicit independent compact lift: " + name)
        Y = full[:, 40:61] * a["isotope_scales"]
        check(np.array_equal(Y, a["Y"]), "population abundance scaling: " + name)
        eta = Y.sum(axis=1) + Y @ Q
        T = 2 * full[:, 62] / (3 * eta)
        energy = KB * full[:, 62] + Y @ binding
        record = dict(raw_sha256=sha(directory / "trajectory.npz"), artifact_bindings=len(receipt["artifacts"]),
                      T_reconstruction_relative=rel(T, d["T_K"]), energy_reconstruction_relative=rel(energy, d["epsilon_total_J"]),
                      finite_state_scopes={}, ledger={}, source={})
        check(record["T_reconstruction_relative"] < 3e-14, "temperature from raw energy and eta: " + name)
        check(record["energy_reconstruction_relative"] < 3e-14, "thermal plus binding store: " + name)
        scale = np.exp(x) / 21
        U_actual = (4 * STEFAN_BOLTZMANN / C) * 2.7255**4 * full[:, 4] / scale**4
        branch = receipt["identity"]["config"]["cmb_branch"]
        Uref = ARAD * (2.7255 / scale)**4 if branch == "planck_reference" else np.zeros(len(x))
        qc = np.zeros(len(x)) if branch == "off" else (-4 * K * d["ne_m3"] * KB * T * U_actual
             if branch == "actual_hot" else 4 * K * d["ne_m3"] * KB * Uref * (2.7255 / scale - T))
        quv = np.zeros(len(x)) if branch == "off" else K * d["ne_m3"] * (d["M_uv_J2_m3"] - 4 * KB * T * d["U_uv_J_m3"])
        record["source"] = dict(U_actual_relative=rel(U_actual, d["U_gamma_J_m3"]), U_reference_relative=rel(Uref, d["U_ref_J_m3"]),
            Q_C_relative=rel(qc / d["nb_m3"], d["compton_W_baryon"]), Q_UV_relative=rel(quv / d["nb_m3"], d["uv_compton_W_baryon"]),
            actual_ratio_relative=rel(abs(qc) / (d["H_s"] * U_actual), d["compton_over_HUgamma"]))
        check(max(record["source"].values()) < 5e-13, "independent direct Compton owners and units: " + name)
        scopes = (("saved193", a["raw_state"], x), ("accepted_BDF_nodes", returned["raw_state"], returned["x"]),
                  ("dense_GL8", a["dense_GL8_state"], a["dense_GL8_x"]),
                  ("dense_GL16", a["dense_GL16_state"], a["dense_GL16_x"]))
        for label, states, coords in scopes:
            s = finite_scope(states, coords, a)
            record["finite_state_scopes"][label] = s
            check(s["finite"] and s["minimum_scaled_population"] >= -2e-8 and s["baryon_max_abs"] < 2e-8
                  and s["isotope_max_scaled"] < 2e-7 and s["electron_abundance_min"] >= 0
                  and s["T_min_K"] >= 100 and s["T_max_K"] <= 1e6 and s["minimum_tau_increment"] >= -2e-10
                  and s["number_monopole_max_abs"] < 2e-9 and s["absent_n_tritium_exact_zero"], "retained state physical gates: " + name + "/" + label)
            check(s["count"] == receipt["physical_scopes"][label]["metrics"]["sample_count"], "declared sample count: " + name + "/" + label)
        reconstructed = {}
        for order in (8, 16):
            integral, throughput, nodes = integrate(x, a[f"dense_GL{order}_integrands"], order)
            reconstructed[order] = (integral, throughput)
            expected_x = ((x[:-1] + x[1:])[:, None] / 2 + np.diff(x)[:, None] / 2 * nodes).ravel()
            denom = a["ledger_denominator_J"][:, None]
            signed_error = maximum((integral - a[f"ledger_GL{order}"]) / denom)
            absolute_error = maximum((throughput - a[f"ledger_abs_GL{order}"]) / denom)
            ratios, _absratios, _nodes = integrate(x, a[f"dense_GL{order}_exchange_ratios"], order)
            ratio_error = rel(ratios, a[f"exchange_ratio_integrals_GL{order}"], 1e-30)
            record["ledger"][f"GL{order}"] = dict(signed_reconstruction_normalized=signed_error,
                absolute_reconstruction_normalized=absolute_error, nodes_max_abs=maximum(expected_x - a[f"dense_GL{order}_x"]),
                exchange_integral_reconstruction_relative=ratio_error)
            check(max(signed_error, absolute_error, ratio_error) < 5e-13, "independent retained quadrature: " + name + f"/GL{order}")
        i16, abs16 = reconstructed[16]
        denominator = np.maximum(np.maximum(abs(energy), abs(energy[0])), abs16.sum(axis=1))
        residual = energy - energy[0] - i16 @ np.array([1., -1., -1., 1., 1.])
        normalized = abs(residual) / denominator
        index = int(normalized.argmax())
        gl_difference = np.max(abs(reconstructed[8][0] - i16), axis=1) / denominator
        abs_difference = np.max(abs(reconstructed[8][1] - abs16), axis=1) / denominator
        record["energy"] = dict(max_normalized_residual=float(normalized[index]), peak_index=index, peak_z=float(a["z"][index]),
             margin_fraction=float(1 - normalized[index] / 3e-6), max_GL_difference=float(gl_difference.max()),
             max_absolute_GL_difference=float(abs_difference.max()), residual_array_disagreement=maximum(normalized - a["ledger_normalized_residual"]),
             denominator_relative_disagreement=rel(denominator, a["ledger_denominator_J"]))
        check(maximum(normalized - a["ledger_normalized_residual"]) < 5e-13, "ledger residual raw/record agreement: " + name)
        check(rel(denominator, a["ledger_denominator_J"]) < 5e-13, "absolute-throughput denominator: " + name)
        check(float(normalized.max()) < 3e-6 and float(gl_difference.max()) < 3e-6 and float(abs_difference.max()) < 3e-6, "independent integrated-energy gates: " + name)
        check(abs(float(normalized.max()) - receipt["max_energy_residual"]) < 5e-13, "energy result maximum binding: " + name)
        record["reported_wall_seconds"] = receipt["wall_seconds"]
        report["cases"][name] = record

    comparison_receipt = json.loads((ROOT / "results/VALIDATION_COMPARISONS.json").read_text())
    for nominal, other in ((CASES[1], CASES[5]), (CASES[2], CASES[6]), (CASES[2], CASES[7])):
        a, b = histories[nominal], histories[other]
        da, db = diag[nominal], diag[other]
        values = dict(max_relative_T=maximum((da["T_K"] - db["T_K"]) / np.maximum(abs(da["T_K"]), abs(db["T_K"]))),
            max_charge_fraction_absolute=maximum(a["scaled_populations"] - b["scaled_populations"]),
            max_tau_absolute=maximum(da["tau_T"] - db["tau_T"]),
            max_signed_normalized_absolute=maximum(a["signed_observables"] - b["signed_observables"]))
        for key, value in values.items():
            check(value == comparison_receipt[other][key], "refinement receipt binding: " + other + "/" + key)
        check(values["max_relative_T"] < 3e-5 and values["max_charge_fraction_absolute"] < 3e-5
              and values["max_tau_absolute"] < 3e-7 and values["max_signed_normalized_absolute"] < 3e-7,
              "retained refinement gates: " + other)
        report["comparisons"][other] = values

    def observables(name):
        a, d = histories[name], diag[name]
        return dict(T_K=d["T_K"], electron_abundance=d["ne_m3"] / d["nb_m3"], tau=d["tau_T"],
                    charge_fractions=a["scaled_populations"], **{key: a["signed_observables"][:, j] for j, key in enumerate(OBS)})
    hot, planck, ht, pt = [observables(CASES[j]) for j in (1, 2, 5, 6)]
    for key in hot:
        signal = maximum(planck[key] - hot[key])
        rh, rp = maximum(ht[key] - hot[key]), maximum(pt[key] - planck[key])
        report["branch_resolution"][key] = dict(signal_max_abs=signal, hot_refinement_max_abs=rh,
            planck_refinement_max_abs=rp, exceeds_both_observed_refinements=bool(signal > rh and signal > rp),
            interpretation="finite supremum comparison only; not a pointwise or global error bound")

    # Exact plot-data provenance is a file/array binding, not a new simulation.
    plot_manifest = json.loads((ROOT / "results/PLOT_DATA_MANIFEST.json").read_text())
    for name, entry in plot_manifest["inputs"].items():
        check(sha(ROOT / entry["path"]) == entry["sha256"], "plot raw binding: " + name)
        if name not in histories:
            histories[name] = archive(ROOT / entry["path"])
            diag[name] = diagnostics(histories[name])
    for relative, entry in plot_manifest["outputs"].items():
        check(sha(ROOT / relative) == entry["sha256"] and (ROOT / relative).stat().st_size == entry["bytes"], "plot output binding: " + relative)
    for name, a in histories.items():
        d = diag[name]
        expected = dict(x=a["x"], z=a["z"], **{"diagnostic_" + k: v for k, v in d.items()})
        expected["electron_abundance_ne_over_nb"] = d["ne_m3"] / d["nb_m3"]
        for key in ("Y", "scaled_populations", "signed_observables"):
            labels = OBS if key == "signed_observables" else range(21)
            expected.update({f"{key}_{label}": a[key][:, j] for j, label in enumerate(labels)})
        for key in ("ledger_GL8", "ledger_GL16", "ledger_abs_GL16"):
            if key in a:
                expected.update({f"{key}_{LEDGER[j]}_J_per_baryon": a[key][:, j] for j in range(a[key].shape[1])})
        for key in ("ledger_residual_J", "ledger_denominator_J", "ledger_normalized_residual", "ledger_GL_difference"):
            if key in a:
                expected[key] = a[key]
        expected["delta_epsilon_total_eV_per_baryon"] = (d["epsilon_total_J"] - d["epsilon_total_J"][0]) / EV
        for j in range(a["ledger_GL16"].shape[1]):
            expected[f"signed_gas_{LEDGER[j]}_eV_per_baryon"] = (-1. if j in (1, 2) else 1.) * a["ledger_GL16"][:, j] / EV
        path = ROOT / "results" / f"PLOT_DATA_{name}.csv"
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream)
            columns = {key: [] for key in reader.fieldnames}
            for row in reader:
                for key, value in row.items():
                    columns[key].append(float(value))
        check(set(columns) == set(expected), "plot CSV column coverage: " + name)
        for key in expected:
            check(np.array_equal(np.array(columns[key]), expected[key]), "plot CSV float64 binding: " + name + "/" + key)
        report["CSV_bindings"][name] = dict(rows=len(a["x"]), columns=len(columns), exact_float64=True)

    comparison_path = ROOT / "results/PLOT_DATA_signed_comparisons.csv"
    expected = dict(x=histories[CASES[2]]["x"], z=histories[CASES[2]]["z"])
    for pair, definition in plot_manifest["comparison_definitions"].items():
        left, right = definition["left"], definition["right"]
        da, db = diag[left], diag[right]
        a, b = histories[left], histories[right]
        fields = dict(relative_T=(da["T_K"] - db["T_K"]) / db["T_K"],
            electron_abundance=da["ne_m3"] / da["nb_m3"] - db["ne_m3"] / db["nb_m3"],
            tau_T=da["tau_T"] - db["tau_T"],
            **{key: a["signed_observables"][:, j] - b["signed_observables"][:, j] for j, key in enumerate(OBS)})
        expected.update({pair + "__" + key: value for key, value in fields.items()})
        for key, value in fields.items():
            check(maximum(value) == plot_manifest["comparison_peaks_absolute"][pair][key],
                  "plot comparison maximum binding: " + pair + "/" + key)
    with comparison_path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        columns = {key: [] for key in reader.fieldnames}
        for row in reader:
            for key, value in row.items():
                columns[key].append(float(value))
    check(set(columns) == set(expected), "comparison CSV column coverage")
    for key in expected:
        check(np.array_equal(np.array(columns[key]), expected[key]), "comparison CSV float64 binding: " + key)
    report["CSV_bindings"]["signed_comparisons"] = dict(rows=193, columns=len(columns), exact_float64=True)

    summary = json.loads((ROOT / "results/SCIENCE_SUMMARY.json").read_text())
    report["cohort"] = dict(ids=list(CASES), receipts=len(receipts),
        accepted_BDF_nodes=sum(r["accepted_nodes"] for r in receipts.values()),
        summed_case_seconds=math.fsum(r["wall_seconds"] for r in receipts.values()),
        reported_cumulative_seconds=summary["cumulative_science_seconds"],
        unique_completed=summary["unique_completed_new_cohort_IVPs"],
        new_this_invocation=summary["new_IVPs_this_invocation"], old_IVPs=summary["old_campaign_IVPs_executed"])
    check(set(summary["case_ids"]) == set(CASES) and summary["unique_completed_new_cohort_IVPs"] == 8
          and 0 <= summary["new_IVPs_this_invocation"] <= 8
          and summary["cached_IVPs_this_invocation"] + summary["new_IVPs_this_invocation"] == 8
          and summary["old_campaign_IVPs_executed"] == 0,
          "exactly-eight cohort summary")
    check(all(r["wall_seconds"] < 180 for r in receipts.values()) and summary["cumulative_science_seconds"] < 1200,
          "reported cooperative budget")
    report["elapsed_seconds"] = time.perf_counter() - started
    report["failures"] = failures
    report["status"] = "PASS" if not failures else "FAIL"
    report["exit_code"] = 0 if not failures else 1
    (OUT / "INDEPENDENT_ARRAY_AUDIT.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2, allow_nan=False))
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())

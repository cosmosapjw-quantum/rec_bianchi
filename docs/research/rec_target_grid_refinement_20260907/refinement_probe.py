"""Research-only fixed-table target-grid probe. Authored, not executed here."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import traceback

import numpy as np
import mpmath as mp

BASE = "59dafbd34bc21b1b885c716b7b8cc899636bbd60"
NEW = "docs/research/rec_target_grid_refinement_20260907"
OLD = "docs/research/rec_multi_bin_affinity_20260907/study.py"
OLD_BLOB = "f1ad5926de6090e8317961c6cc58914cfd5c8ba3"
SIZES = (5, 9, 17, 33, 65, 129)
POWERS = (0, 1, 2, 4)
CASES = ("curved_emission", "curved_absorption", "affine_balance")
EPS = 2.0**-30
TOL = 4096 * np.finfo(float).eps
NH, DNH = 8.0, 2.0


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def scaled(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    require(a.shape == b.shape, "comparison shape mismatch")
    require(np.isfinite(a).all() and np.isfinite(b).all(),
            "nonfinite comparison")
    return float(np.max(np.abs(a - b) / (1 + np.abs(b))))


def close(a, b, label):
    require(scaled(a, b) <= TOL, label)


def dump(path, obj):
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def save_csv(path, rows):
    if rows:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, timeout=30
    ).strip()


def file_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode() + b"\0" + data
    ).hexdigest()


def load_prior(root):
    require(file_blob(root / OLD) == OLD_BLOB, "PR79 source changed")
    spec = importlib.util.spec_from_file_location("rec_pr79_fixed", root / OLD)
    require(spec is not None and spec.loader is not None, "module loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    for name, expected in module.PINS.items():
        require(file_blob(root / name) == expected, "protected input: " + name)
    return module


def parameters(case):
    require(case in CASES, "unknown state")
    alpha = 0.0 if case == "affine_balance" else 0.25
    ratio = {
        "curved_emission": 1 / 8,
        "curved_absorption": 1 / 32,
        "affine_balance": math.exp(-2.5),
    }[case]
    xg = (9 / 16) / (1 + ratio)
    return alpha, ratio * xg, xg


def field(u, alpha):
    return 0.5 + 1.5 * u + alpha * u * (1 - u)


def perturbation(u):
    return u * (1 - u) / 8 + (2 * u - 1) / 16


def grid(prior, table, size, measure_scale=1.0):
    u = np.linspace(EPS, 1 - EPS, size)
    lengths = np.diff(u)
    mu = 20 / (1 - 2 * EPS) * (
        np.r_[0.0, lengths] + np.r_[lengths, 0.0]
    ) / 2
    mu *= measure_scale
    B = prior.weights(u, table["us"])
    L = prior.weights(u, table["us"], logarithmic=True)
    plan = prior.COMSourceDepositionPlan(
        mu, prior.E21_J * u, prior.E21_J * table["us"], B,
        np.array([1.0]), np.array([[0.0, 0.0, 1.0]]),
        "RESEARCH_UNIFORM_HAT_MASS_NOT_PHYSICAL",
        "RESEARCH_LINEAR_ENERGY_PARTITION",
    )
    return u, mu, B, L, plan


def original_api(prior, table, g, case, kind):
    u, mu, B, L, plan = g
    alpha, xu, xg = parameters(case)
    chi = field(u, alpha)
    dchi = perturbation(u)
    f = 1 / np.expm1(chi)

    if kind == "chi":
        read_chi = B.T @ chi
        legs = 1 / np.expm1(read_chi)
        dlegs = -legs * (1 + legs) * (B.T @ dchi)
    elif kind == "log_control":
        y = -np.log(np.expm1(chi))
        legs = np.exp(L.T @ y)
        dlegs = legs * (L.T @ (-(1 + f) * dchi))
        read_chi = np.log1p(1 / legs)
    else:
        raise ValueError("unknown read operator")

    n = table["n"]
    gamma, dgamma, activity = [], [], []
    for b, rate in enumerate(table["normalized"]):
        pair = prior.PhysicalTwoPhotonRamanBin(
            "two_photon", float(rate),
            prior.E21_J / prior.H_PLANCK,
            prior.E21_J * float(table["us"][n + b]) / prior.H_PLANCK,
            prior.E21_J * float(table["us"][b]) / prior.H_PLANCK,
            float(xu), float(xg), 1.0,
        )
        fc, ft = float(legs[n + b]), float(legs[b])
        forward, reverse = pair.paired_rates(
            companion_occupation=fc, tracked_occupation=ft
        )
        gamma.append(pair.net_action(fc, ft))
        dgamma.append(pair.jvp(
            companion_occupation=fc, tracked_occupation=ft,
            d_integrated_rate_s_inv=float(rate / 8),
            d_upper_population=1 / 64,
            d_ground_population=-1 / 32,
            d_companion_occupation=float(dlegs[n + b]),
            d_tracked_occupation=float(dlegs[b]),
        ))
        activity.append(forward + reverse)

    gamma, dgamma = np.array(gamma), np.array(dgamma)
    C = plan.apply(np.r_[gamma, gamma], NH)[:, 0]
    dC = plan.jvp(
        np.r_[gamma, gamma], np.r_[dgamma, dgamma], NH, DNH
    )[:, 0]
    count = mu * C / NH
    dcount = mu / NH * (dC - C * DNH / NH)
    psi = np.array([u**p for p in POWERS])
    q = psi @ B
    W = q[:, :n] + q[:, n:]
    affinity = math.log(xu / xg) + (B.T @ chi)[:n] + (B.T @ chi)[n:]
    read_affinity = math.log(xu / xg) + read_chi[:n] + read_chi[n:]
    sigma = float(count @ chi + math.fsum(gamma) * math.log(xu / xg))

    return {
        "gamma": gamma, "dgamma": dgamma, "C": C,
        "moment": psi @ count, "dmoment": psi @ dcount, "W": W,
        "sigma": sigma, "activity": math.fsum(activity),
        "affinity_defect": read_affinity - affinity,
    }


def independent_rates(table, nodes, matrix, kind, case):
    """Independent nonlinear primal, then high-precision central differences.

    matrix=None evaluates the continuous state at the original source energies.
    Otherwise it lifts the actual binary64 read weights, without calling APIs.
    """
    alpha, xu, xg = parameters(case)
    stencils = None if matrix is None else [
        [(int(i), float(matrix[i, s]))
         for i in np.flatnonzero(matrix[:, s])]
        for s in range(matrix.shape[1])
    ]

    def primal(theta):
        x = [mp.mpf(float(v)) for v in nodes]
        chi = [field(v, mp.mpf(alpha)) + theta * perturbation(v) for v in x]
        if stencils is None:
            legs = [1 / mp.expm1(v) for v in chi]
        else:
            values = chi if kind == "chi" else [-mp.log(mp.expm1(v)) for v in chi]
            read = [
                mp.fsum(mp.mpf(w) * values[i] for i, w in stencil)
                for stencil in stencils
            ]
            legs = ([1 / mp.expm1(v) for v in read]
                    if kind == "chi" else [mp.exp(v) for v in read])
        upper = mp.mpf(xu) + theta / 64
        ground = mp.mpf(xg) - theta / 32
        n = table["n"]
        return [
            mp.mpf(float(rate)) * (1 + theta / 8) * (
                upper * (1 + legs[b]) * (1 + legs[n + b])
                - ground * legs[b] * legs[n + b]
            )
            for b, rate in enumerate(table["normalized"])
        ]

    def evaluate(dps, power):
        with mp.workdps(dps):
            h = mp.mpf(2)**(-power)
            p, plus, minus = primal(mp.mpf(0)), primal(h), primal(-h)
            return p, [(a - b) / (2 * h) for a, b in zip(plus, minus)]

    p80, d80 = evaluate(80, 32)
    p120, d120 = evaluate(120, 32)
    _, fine = evaluate(120, 36)
    with mp.workdps(120):
        precision = max(
            abs(a - b) / (1 + abs(b))
            for a, b in zip(p80 + d80, p120 + d120)
        )
        step = max(abs(a - b) / (1 + abs(b)) for a, b in zip(d120, fine))
        require(precision < mp.mpf("1e-60"), "reference precision disagreement")
        require(step < mp.mpf("1e-16"), "reference step disagreement")
        info = {"precision_80_120": mp.nstr(precision, 24),
                "step_32_36": mp.nstr(step, 24)}
    return np.array(p120, float), np.array(fine, float), info


def render_saved_csv(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with (out / "MOMENTS.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for column in ("absolute_error", "absolute_jvp_error"):
        for width in (90, 180):
            fig, ax = plt.subplots(
                figsize=(width / 25.4, 0.8 * width / 25.4),
                layout="constrained",
            )
            for table in ("base", "hires"):
                for kind, style in (("chi", "-o"), ("log_control", "--x")):
                    selected = [
                        r for r in rows if r["table"] == table
                        and r["read"] == kind and r["case"] == "curved_emission"
                        and int(r["power"]) == 2
                    ]
                    ax.plot([int(r["nodes"]) - 1 for r in selected],
                            [float(r[column]) for r in selected],
                            style, label=table + " " + kind, markersize=3)
            ax.set_xscale("log", base=2)
            ax.set_yscale("symlog", linthresh=1e-16)
            ax.set_xlabel("Target intervals")
            ax.set_ylabel(column.replace("_", " ") + " [s$^{-1}$]")
            ax.legend(fontsize=6 if width == 90 else 8)
            fig.savefig(out / f"{column}_{width}mm.png", dpi=200)
            plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root, out = args.repo.resolve(), args.out.resolve()
    if out == root or root in out.parents:
        parser.error("output must be outside the worktree")
    out.mkdir(parents=True, exist_ok=False)
    rows, references, oracle_checks = [], [], []
    report = {
        "classification": "NOT_COMPLETED",
        "claim": "NO_PASS_REC_PHYSICAL_SPLIT",
        "physical_source_authenticated": False, "provider_admitted": False,
        "old_tests_replayed": False, "visual_audit": "NOT_PERFORMED",
    }
    rc = 2
    try:
        require(os.environ.get("GITHUB_ACTIONS", "").lower() != "true",
                "GitHub Actions execution prohibited")
        git(root, "merge-base", "--is-ancestor", BASE, "HEAD")
        require(not git(root, "status", "--porcelain"), "clean checkout required")
        changed = git(root, "diff", "--name-only", BASE, "HEAD").splitlines()
        require(all(p.startswith(NEW + "/") for p in changed), "scope violation")
        script = Path(__file__).resolve()
        require(script == root / NEW / "refinement_probe.py", "script location")
        require(file_blob(script) == git(root, "rev-parse", "HEAD:" + NEW
                                        + "/refinement_probe.py"),
                "executed script is not committed")
        report.update(
            source_commit=git(root, "rev-parse", "HEAD"),
            source_tree=git(root, "rev-parse", "HEAD^{tree}"),
            script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
            environment={"python": sys.version, "numpy": np.__version__,
                         "mpmath": mp.__version__},
        )
        prior = load_prior(root)
        tables, _ = prior.load_tables()
        report["phase"] = "NUMERICAL_DIAGNOSTICS"

        for table in tables:
            n, us = table["n"], table["us"]
            Wr = np.array([us[:n]**p + us[n:]**p for p in POWERS])
            for case in CASES:
                gr, dgr, ref_info = independent_rates(table, us, None, "chi", case)
                Mr, dMr = Wr @ gr, Wr @ dgr
                references.append({
                    "table": table["label"], "case": case,
                    "moments": Mr.tolist(), "jvp": dMr.tolist(), **ref_info,
                })
                alpha, xu, xg = parameters(case)

                for size in SIZES:
                    g = grid(prior, table, size)
                    u, mu, B, L, _ = g
                    h = float(np.max(np.diff(u)))
                    close(math.fsum(mu), 20.0, "common total measure")
                    close(float(mu @ u), 10.0, "common first measure moment")
                    require(np.all(mu > 0), "positive mass weights")
                    j = np.clip(np.searchsorted(u, us, side="right") - 1,
                                0, size - 2)
                    quadratic = (us - u[j]) * (u[j + 1] - us)
                    close(B.T @ (u*u) - us*us, quadratic, "quadratic fixture")
                    close(B.T @ field(u, alpha) - field(us, alpha),
                          -alpha * quadratic, "chi interpolation fixture")

                    for kind in ("chi", "log_control"):
                        r = original_api(prior, table, g, case, kind)
                        close(r["moment"], r["W"] @ r["gamma"], "COM weak form")
                        close(r["dmoment"], r["W"] @ r["dgamma"], "COM weak JVP")
                        close(r["moment"][:2],
                              [2 * math.fsum(r["gamma"]), math.fsum(r["gamma"])],
                              "number/energy ledger")

                        if case == "curved_emission" and size in (9, 129):
                            go, dgo, info = independent_rates(
                                table, u, B if kind == "chi" else L, kind, case
                            )
                            close(r["gamma"], go, "independent discrete primal")
                            close(r["dgamma"], dgo, "independent discrete JVP")
                            oracle_checks.append({
                                "table": table["label"], "nodes": size, "read": kind,
                                "primal_error": scaled(r["gamma"], go),
                                "jvp_error": scaled(r["dgamma"], dgo), **info,
                            })

                        dg, ddg = r["gamma"] - gr, r["dgamma"] - dgr
                        dW = r["W"] - Wr
                        terms = (Wr @ dg, dW @ gr, dW @ dg)
                        dterms = (Wr @ ddg, dW @ dgr, dW @ ddg)
                        close(r["moment"] - Mr, sum(terms), "error decomposition")
                        close(r["dmoment"] - dMr, sum(dterms), "JVP decomposition")

                        bounds = np.full(4, np.nan)
                        if kind == "chi":
                            fmax = 1 / math.expm1(0.5)
                            rate_bound = (
                                2 * math.fsum(table["normalized"])
                                * (xu + abs(xu - xg) * fmax)
                                * fmax * (1 + fmax) * h*h * (2*alpha) / 8
                            )
                            bounds = (2 * rate_bound + h*h / 4
                                      * np.array([0., 0., 2., 12.])
                                      * math.fsum(abs(gr)))
                            require(np.all(np.abs(r["moment"] - Mr)
                                           <= bounds + TOL * (1 + np.abs(Mr))),
                                    "conditional chi weak bound")
                            close(r["affinity_defect"], np.zeros(n),
                                  "matched affinity")
                            require(r["sigma"] >= -TOL * (1 + r["activity"]),
                                    "chi entropy sign")

                        if case == "curved_emission" and size == 17:
                            shadow = grid(prior, table, size, measure_scale=2)
                            C2 = shadow[-1].apply(
                                np.r_[r["gamma"], r["gamma"]], NH
                            )[:, 0]
                            close(2*C2, r["C"], "measure inverse scaling")
                            psi = np.array([u**p for p in POWERS])
                            close(psi @ (shadow[1] * C2 / NH), r["moment"],
                                  "weak moment cannot authenticate measure")

                        for k, power in enumerate(POWERS):
                            rows.append({
                                "table": table["label"], "case": case, "read": kind,
                                "nodes": size, "h_grid": h, "power": power,
                                "moment": float(r["moment"][k]),
                                "reference": float(Mr[k]),
                                "jvp": float(r["dmoment"][k]),
                                "reference_jvp": float(dMr[k]),
                                "absolute_error": float(abs(r["moment"][k]-Mr[k])),
                                "absolute_jvp_error": float(abs(r["dmoment"][k]-dMr[k])),
                                "read_error": float(terms[0][k]),
                                "scatter_error": float(terms[1][k]),
                                "cross_error": float(terms[2][k]),
                                "read_jvp_error": float(dterms[0][k]),
                                "scatter_jvp_error": float(dterms[1][k]),
                                "cross_jvp_error": float(dterms[2][k]),
                                "chi_bound": float(bounds[k]) if kind == "chi" else "",
                                "entropy_rate": r["sigma"],
                                "peak_C": float(np.max(abs(r["C"]))),
                            })

        require(len(rows) == 288 and len(oracle_checks) == 8, "coverage census")
        require(not git(root, "status", "--porcelain"), "worktree mutation")
        report.update(classification="COMPLETED_BOUNDED_WEAK_DIAGNOSTIC",
                      rows=len(rows), oracle_comparisons=len(oracle_checks),
                      convergence_interpretation="REQUIRES_RESULT_AND_PLOT_REVIEW")
        rc = 0
    except Exception:
        report.update(classification="FAILED_OR_BLOCKED",
                      traceback=traceback.format_exc())

    save_csv(out / "MOMENTS.csv", rows)
    dump(out / "DIRECT_REFERENCES.json", references)
    dump(out / "ORACLE_CHECKS.json", oracle_checks)
    if rc == 0:
        try:
            render_saved_csv(out)
            report["plot_generation"] = "COMPLETED_NOT_VISUALLY_REVIEWED"
        except Exception:
            report["plot_generation"] = "FAILED"
            report["plot_traceback"] = traceback.format_exc()
    report["script_exit_code"] = rc
    dump(out / "RESULT.json", report)
    print(json.dumps(report, ensure_ascii=False, allow_nan=False))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

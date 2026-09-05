#!/usr/bin/env python3
"""One frozen two-table scalar response comparison; never a production provider."""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import zipfile

import mpmath as mp
import numpy as np
from scipy.constants import electron_volt, h, hbar, k
import sympy as sp

from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import (
    A2S_THRESHOLD_EV, L2S_1S_S_INV,
    OriginalHyRecTwoPhotonRamanTable, PhysicalTwoPhotonRamanBin,
)

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PREFIX = str(HERE.relative_to(ROOT)) + "/"
DELIVERY = "f27b1ee0d6189ac49ccabe7c22db29bfa8da61ed"
TREE = "fae19f554a75daef1aa52ad022b9a512c1701ecd"
ARCHIVE = "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
ARCHIVE_SHA = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
MEMBERS = {
    "HyRec/two_photon_tables.dat": "93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9",
    "HyRec/two_photon_tables_hires.dat": "db201c729a38c7919172cf080c8ba44cdf8e6b131a6eaa8adcbc9e58fd4d0c93",
    "HyRec/hyrec_params.h": "cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2",
    "HyRec/hydrogen.c": "421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b",
    "HyRec/hydrogen.h": "e89a3a447928cbe31dc273c11c4a8bc7f7a8e297be4a11270e453c101f96ccba",
    "HyRec/readme.pdf": "457815c1daa6c20d9ab18c05648e2736eee1a8a417cdcf5533d804207c8b7524",
}
OBS = ["S", "1", "u", "u^2", "window"]
EPS = np.finfo(float).eps


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def csv_write(path, rows):
    with Path(path).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def exact_float(x):
    """Lift the actual binary64 value, never its short decimal display."""
    n, d = float(x).as_integer_ratio()
    return mp.mpf(n) / d


def mp_text(x):
    return mp.nstr(x, mp.mp.dps, strip_zeros=False)


def ratio(x, scale):
    return abs(x) / scale if scale > 0 else None


def field(u, lam, alpha):
    g = u * (1.0 - u)
    f = 1.0 / math.expm1(lam * u + alpha * g)
    return f, -g * f * (1.0 + f)


def weights(ut, uc, exp):
    return [1, 2, ut + uc, ut**2 + uc**2,
            exp(-((ut - Fraction(3, 4)) * 32)**2)
            + exp(-((uc - Fraction(3, 4)) * 32)**2)]


def parse_table(data, nvirt):
    tokens = [line.split() for line in data.decode("ascii").splitlines() if line.strip()]
    if len(tokens) != nvirt or any(len(row) != 5 for row in tokens):
        raise ValueError("unsupported table shape; no reshape or padding")
    values = np.array([[float(v) for v in row] for row in tokens], dtype=float)
    if not np.all(np.isfinite(values)) or np.any(values[:, 1:] < 0):
        raise ValueError("nonfinite or negative rate")
    if np.any(np.diff(values[:, 0]) <= 0):
        raise ValueError("energies must be strictly increasing")
    return tokens, values


@dataclass
class Table:
    label: str
    config: dict
    tokens: list
    values: np.ndarray
    normalized: np.ndarray
    factor: float


def inputs(out):
    assert git("rev-parse", DELIVERY + "^{tree}") == TREE
    assert git("rev-parse", DELIVERY + "^") == "708a9b419a193713240ff3aaa674e6e612ddfb2b"
    assert git("rev-parse", DELIVERY + "^^{tree}") == "b6bab967316518f48d3da9b7f192ff03241fd61f"
    for file, blob in {
        "WORK_THREAD_PROMPT_KO.md": "8773b73b970992df9815f11111dc207d2e2fc167",
        "LOCAL_CODEX_PROMPT_KO.md": "9bdd6961c9bcb7ee35ee9944e36a6f7aa46c4faf",
    }.items():
        assert git("rev-parse", DELIVERY + ":docs/research/rec_2s_approved_three_lane_20260905/" + file) == blob
    assert not git("status", "--porcelain"), "commit source before executing"
    subprocess.run(["git", "merge-base", "--is-ancestor", DELIVERY, "HEAD"], cwd=ROOT, check=True)
    changed = git("diff", "--name-only", DELIVERY, "HEAD").splitlines()
    assert changed and all(p.startswith(PREFIX) for p in changed)
    b = (ROOT / ARCHIVE).read_bytes()
    assert sha(b) == ARCHIVE_SHA
    with zipfile.ZipFile(ROOT / ARCHIVE) as z:
        members = {name: z.read(name) for name in MEMBERS}
    for name, data in members.items():
        assert sha(data) == MEMBERS[name], name
    header = members["HyRec/hyrec_params.h"].decode()
    configs = {}
    for label, commented in [("base", False), ("hires", True)]:
        lines = [s for s in header.splitlines()
                 if bool(s.startswith("/* #define")) == commented]
        config = {}
        for name in ["TWOG_FILE", "NSUBLYA", "NSUBLYB", "NVIRT", "NDIFF", "DLNA"]:
            found = [re.search(r"#define\s+" + name + r"\s+(\S+)", s) for s in lines]
            vals = [m.group(1) for m in found if m]
            assert len(vals) == 1, (label, name, vals)
            config[name] = vals[0].strip('"') if name == "TWOG_FILE" else float(vals[0]) if name == "DLNA" else int(vals[0])
        configs[label] = config
    hydrogen_h = members["HyRec/hydrogen.h"].decode()
    e21_token = re.search(r"#define E21\s+(\S+)", hydrogen_h).group(1)
    norm_token = re.search(r"#define L2s1s\s+(\S+)", hydrogen_h).group(1)
    assert float(e21_token) == A2S_THRESHOLD_EV
    assert float(norm_token) == L2S_1S_S_INV
    c = members["HyRec/hydrogen.c"].decode()
    for snippet in ["fA = fopen(TWOG_FILE", "b < NVIRT", "&(twog->A2s_tab[b])",
                    "b < NSUBLYA; b++) L2s1s_current += twog->A2s_tab[b]",
                    "twog->A2s_tab[b] *= L2s1s/L2s1s_current"]:
        assert snippet in c, snippet
    readme_pdf = out / "readme.pdf"
    readme_pdf.write_bytes(members["HyRec/readme.pdf"])
    command = ["/usr/bin/pdftotext", "-layout", str(readme_pdf), str(out / "readme.txt")]
    p = subprocess.run(command, capture_output=True, text=True)
    dump(out / "README_COMMAND.json", {"argv": command, "exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr})
    p.check_returncode()
    readme = (out / "readme.txt").read_text()
    assert "automatically normalized" in readme
    assert "higher accuracy tables and integration parameters" in readme
    excerpts = []
    for member, start, end in [("HyRec/hyrec_params.h", 39, 73),
                               ("HyRec/hydrogen.c", 266, 300),
                               ("HyRec/hydrogen.h", 24, 38),
                               ("HyRec/hydrogen.h", 93, 100)]:
        ls = members[member].decode().splitlines()
        excerpts.append(member + "\n" + "\n".join(f"{i+1}: {ls[i]}" for i in range(start-1, min(end, len(ls)))))
    (out / "SOURCE_SETTINGS_EXCERPTS.txt").write_text("\n\n".join(excerpts) + "\n")
    loader = OriginalHyRecTwoPhotonRamanTable.from_archive(ROOT / ARCHIVE)
    tables, metadata = [], {}
    for label, cfg in configs.items():
        tokens, values = parse_table(members["HyRec/" + cfg["TWOG_FILE"]], cfg["NVIRT"])
        n = cfg["NSUBLYA"]
        assert np.all(values[:n, 0] > A2S_THRESHOLD_EV / 2)
        assert np.all(values[:n, 0] < A2S_THRESHOLD_EV)
        assert np.all(values[n:, 0] > A2S_THRESHOLD_EV)
        assert np.all(values[:n, 2] > 0)
        raw_sum = float(np.sum(values[:n, 2]))
        factor = L2S_1S_S_INV / raw_sum
        normalized = values[:, 1:].T.copy()
        normalized[1, :n] *= factor
        if label == "base":
            assert np.array_equal(values[:, 0], loader.energy_eV)
            assert np.array_equal(normalized, loader.integrated_rates_s_inv)
            normalized = loader.integrated_rates_s_inv
        tables.append(Table(label, cfg, tokens, values, normalized[1], factor))
        with mp.workdps(120):
            raw_dec = mp.fsum(mp.mpf(t[2]) for t in tokens[:n])
            decimal_factor = mp.mpf(norm_token) / raw_dec
            dec_normalized_sum = mp.fsum(mp.mpf(t[2])*decimal_factor for t in tokens[:n])
            decimal = {"raw_sum": mp_text(raw_dec), "factor": mp_text(decimal_factor),
                       "normalized_sum": mp_text(dec_normalized_sum)}
        metadata[label] = {"configuration": cfg, "selected_2s_bins": n,
                           "raw_A2s_all_rows_sum_including_Raman": float(np.sum(values[:, 2])),
                           "raw_2s_sum_numpy": raw_sum,
                           "raw_2s_sum_fsum": math.fsum(values[:n, 2]),
                           "raw_2s_sum_sequential_float": sum(map(float, values[:n, 2])),
                           "normalization_factor_binary64": factor,
                           "normalized_2s_sum_numpy": float(np.sum(normalized[1, :n])),
                           "normalized_2s_sum_fsum": math.fsum(normalized[1, :n]),
                           "decimal_120": decimal,
                           "base_loader_exact_parity": True if label == "base" else None,
                           "row_shape": list(values.shape)}
    identity = {"archive": {"path": ARCHIVE, "sha256": ARCHIVE_SHA},
                "members": {n: {"sha256": sha(d), "bytes": len(d)} for n, d in members.items()},
                "E21_eV_token": e21_token, "L2s1s_s_inv_token": norm_token,
                "tables": metadata, "changed_from_delivery": changed,
                "unchanged_subtrees": {p: git("rev-parse", "HEAD:" + p) for p in ["src", "tests", "archive"]},
                "normalization_authority": "hydrogen.c:276-290 applies TWOG_FILE, NVIRT, NSUBLYA to both configurations; hydrogen.h:38; readme pages 1,3,4",
                "source_line_evidence": "SOURCE_SETTINGS_EXCERPTS.txt"}
    dump(out / "INPUTS.json", identity)
    return tables, identity


def symbolic():
    aa, xg, xu, ec, et, q, gc, gt, ut, w = sp.symbols("a xg xu ec et q gc gt ut w")
    fc, ft = 1/(ec-1), 1/(et-1)
    dc, dt = -gc*fc*(1+fc), -gt*ft*(1+ft)
    paired = aa*(xu*(1+fc)*(1+ft)-xg*fc*ft)
    chain = aa*((xu*(1+ft)-xg*ft)*dc + (xu*(1+fc)-xg*fc)*dt)
    stable = aa*xg*fc*ft*(q-1)
    derivative = gc*ec*sp.diff(stable, ec) + gt*et*sp.diff(stable, et) + (gc+gt)*q*sp.diff(stable, q)
    sub = {xu: xg*q/(ec*et)}
    residuals = {
        "single_field_stable": paired.subs(sub)-stable,
        "alpha_chain_both_legs": chain.subs(sub)-derivative,
        "lte_value": stable.subs(q, 1),
        "lte_alpha_direction": derivative.subs(q, 1)-aa*xg*fc*ft*(gc+gt),
        "weak_alpha": w*(chain.subs(sub)-derivative),
        "weak_number": (1+1)*stable-2*stable,
        "weak_energy": (ut+1-ut)*stable-stable,
        "weak_quadratic": (ut**2+(1-ut)**2)*stable-(1-2*ut*(1-ut))*stable,
    }
    return {name: str(sp.cancel(r)) for name, r in residuals.items()}


def api_case(table, lam, alpha, normalized):
    bins = []
    xg, xu = 0.5, 0.5*math.exp(-lam)
    for i in range(table.config["NSUBLYA"]):
        et = float(table.values[i, 0]); ec = A2S_THRESHOLD_EV - et
        ut, uc = et/A2S_THRESHOLD_EV, ec/A2S_THRESHOLD_EV
        ft, dft = field(ut, lam, alpha); fc, dfc = field(uc, lam, alpha)
        rate = float(table.normalized[i] if normalized else table.values[i, 2])
        source = PhysicalTwoPhotonRamanBin("two_photon", rate,
            A2S_THRESHOLD_EV*electron_volt/h, ec*electron_volt/h, et*electron_volt/h, xu, xg, 1.0)
        plus, minus = source.paired_rates(companion_occupation=fc, tracked_occupation=ft)
        net = source.net_action(fc, ft)
        tangent = source.jvp(companion_occupation=fc, tracked_occupation=ft,
            d_integrated_rate_s_inv=0., d_upper_population=0., d_ground_population=0.,
            d_companion_occupation=dfc, d_tracked_occupation=dft)
        dscale = rate*(abs(xu*dfc*(1+ft)) + abs(xu*(1+fc)*dft)
                       + abs(xg*dfc*ft) + abs(xg*fc*dft))
        bins.append({"bin": i, "Et_eV": et, "Ec_eV": ec, "ut": ut, "uc": uc,
            "nu_t_Hz": source.tracked_frequency_Hz, "nu_c_Hz": source.companion_frequency_Hz,
            "a_s_inv": rate, "xg": xg, "xu": xu, "fc": fc, "ft": ft, "dfc": dfc, "dft": dft,
            "A_plus": plus, "A_minus": minus, "Gamma": net, "dGamma_dalpha": tangent,
            "jvp_component_scale": dscale, "weights": weights(ut, uc, math.exp)})
    return bins


def reference(table, bins, lam, alpha_string, normalized, dps, e21_token, norm_token):
    """Independent scalar sums for exact API arguments and original decimal tokens."""
    with mp.workdps(dps):
        alpha_q = Fraction(alpha_string)
        alpha = mp.mpf(alpha_q.numerator)/alpha_q.denominator
        xg = mp.mpf(1)/2; xu = xg*mp.exp(-lam)
        e21 = mp.mpf(e21_token)
        factor = mp.mpf(norm_token)/mp.fsum(mp.mpf(t[2]) for t in table.tokens[:len(bins)]) if normalized else mp.mpf(1)
        exact_rows, decimal_rows = [], []
        maxima = {"bin_api_value_scaled": mp.mpf(0), "bin_api_jvp_scaled": mp.mpf(0),
                  "stable_direct_value_scaled": mp.mpf(0), "stable_direct_jvp_scaled": mp.mpf(0)}
        for b, tokens in zip(bins, table.tokens):
            a, upper, ground, fc, ft, dc, dt = [exact_float(b[n]) for n in ["a_s_inv", "xu", "xg", "fc", "ft", "dfc", "dft"]]
            plus = a*upper*(1+fc)*(1+ft); minus = a*ground*fc*ft
            net = plus-minus
            dn = a*((upper*(1+ft)-ground*ft)*dc + (upper*(1+fc)-ground*fc)*dt)
            ds = a*(abs(upper*(1+ft)*dc)+abs(ground*ft*dc)+abs(upper*(1+fc)*dt)+abs(ground*fc*dt))
            maxima["bin_api_value_scaled"] = max(maxima["bin_api_value_scaled"], abs(exact_float(b["Gamma"])-net)/(plus+minus))
            maxima["bin_api_jvp_scaled"] = max(maxima["bin_api_jvp_scaled"], abs(exact_float(b["dGamma_dalpha"])-dn)/ds)
            exact_rows.append((net, dn, plus, minus, ds, list(map(exact_float, b["weights"]))))
            ut = mp.mpf(tokens[0])/e21; uc = 1-ut
            gt, gc = ut*(1-ut), uc*(1-uc)
            ft = 1/mp.expm1(lam*ut+alpha*gt); fc = 1/mp.expm1(lam*uc+alpha*gc)
            dc, dt = -gc*fc*(1+fc), -gt*ft*(1+ft)
            a = mp.mpf(tokens[2])*factor
            qminus1 = mp.expm1(alpha*(gc+gt))
            net = a*xg*fc*ft*qminus1
            dn = a*xg*((dc*ft+fc*dt)*qminus1 + fc*ft*(gc+gt)*mp.exp(alpha*(gc+gt)))
            plus, minus = a*xu*(1+fc)*(1+ft), a*xg*fc*ft
            direct_d = a*((xu*(1+ft)-xg*ft)*dc + (xu*(1+fc)-xg*fc)*dt)
            ds = a*(abs(xu*(1+ft)*dc)+abs(xg*ft*dc)+abs(xu*(1+fc)*dt)+abs(xg*fc*dt))
            maxima["stable_direct_value_scaled"] = max(maxima["stable_direct_value_scaled"], abs(net-(plus-minus))/(plus+minus))
            maxima["stable_direct_jvp_scaled"] = max(maxima["stable_direct_jvp_scaled"], abs(dn-direct_d)/ds)
            wt = [mp.mpf(1), mp.mpf(2), ut+uc, ut**2+uc**2,
                  mp.exp(-((ut-mp.mpf(3)/4)*32)**2)+mp.exp(-((uc-mp.mpf(3)/4)*32)**2)]
            decimal_rows.append((net, dn, plus, minus, ds, wt))
        result = []
        for j in range(len(OBS)):
            row = {}
            for label, data in [("api_inputs_exact", exact_rows), ("decimal_tokens", decimal_rows)]:
                for key, idx in [("value", 0), ("jvp", 1), ("plus", 2), ("minus", 3), ("jvp_scale", 4)]:
                    row[label + "_" + key] = mp_text(mp.fsum(b[idx]*b[5][j] for b in data))
            result.append(row)
        return result, {k: mp_text(v) for k, v in maxima.items()}


class Checks:
    def __init__(self):
        self.rows = []

    def bound(self, name, value, limit, context):
        value, limit = float(value), float(limit)
        self.rows.append({"name": name, **context, "value": value, "limit": limit,
                          "passed": math.isfinite(value) and value <= limit})


def compare_case(table, lam, alpha_s, mode, identity, limits, checks):
    alpha = float(Fraction(alpha_s)); normalized = mode == "normalized"
    bins = api_case(table, lam, alpha, normalized)
    refs, ref_rows = {}, []
    context = {"table": table.label, "lambda": lam, "alpha": alpha_s, "mode": mode}
    for dps in [80, 120]:
        refs[dps], maxima = reference(table, bins, lam, alpha_s, normalized, dps,
                                     identity["E21_eV_token"], identity["L2s1s_s_inv_token"])
        for name, val in maxima.items():
            limit = limits["api_value_positive_scale_eps"]*EPS if name == "bin_api_value_scaled" else limits["api_jvp_component_scale_eps"]*EPS if name == "bin_api_jvp_scaled" else float(limits["mp_stable_direct_scaled"])
            checks.bound(name, val, limit, {**context, "dps": dps})
        ref_rows.extend({**context, "observable": ob, "dps": dps, **r} for ob, r in zip(OBS, refs[dps]))
    rows = []
    with mp.workdps(120):
        for j, ob in enumerate(OBS):
            r = refs[120][j]
            val = math.fsum(b["Gamma"]*b["weights"][j] for b in bins)
            jvp = math.fsum(b["dGamma_dalpha"]*b["weights"][j] for b in bins)
            plus = math.fsum(b["A_plus"]*b["weights"][j] for b in bins)
            minus = math.fsum(b["A_minus"]*b["weights"][j] for b in bins)
            scale = plus+minus
            ds = math.fsum(b["jvp_component_scale"]*b["weights"][j] for b in bins)
            val_error = abs(exact_float(val)-mp.mpf(r["api_inputs_exact_value"]))
            jvp_error = abs(exact_float(jvp)-mp.mpf(r["api_inputs_exact_jvp"]))
            c = {**context, "observable": ob}
            checks.bound("aggregate_api_value", val_error/scale, limits["api_value_positive_scale_eps"]*EPS, c)
            checks.bound("aggregate_api_jvp", jvp_error/ds, limits["api_jvp_component_scale_eps"]*EPS, c)
            for path in ["api_inputs_exact", "decimal_tokens"]:
                for quantity in ["value", "jvp", "plus", "minus", "jvp_scale"]:
                    key = path+"_"+quantity
                    ref_scale = mp.mpf(r[path+"_jvp_scale"]) if quantity in ["jvp", "jvp_scale"] else mp.mpf(r[path+"_plus"])+mp.mpf(r[path+"_minus"])
                    checks.bound("mp80_120_"+key, abs(mp.mpf(refs[80][j][key])-mp.mpf(r[key]))/ref_scale,
                                 float(limits["mp80_mp120_scaled"]), c)
            if alpha == 0:
                checks.bound("lte_api_null", abs(val)/scale, limits["lte_positive_scale_eps"]*EPS, c)
                checks.bound("lte_decimal_null", abs(mp.mpf(r["decimal_tokens_value"])), 0., c)
                checks.bound("lte_alpha_nonzero_positive", 0. if mp.mpf(r["decimal_tokens_jvp"]) > 0 else 1., 0., c)
            rows.append({**c, "value_API_per_H_s": val, "alpha_JVP_API_per_H_s": jvp,
                "A_plus": plus, "A_minus": minus, "positive_scale": scale, "jvp_component_scale": ds,
                "abs_net_over_positive": ratio(val, scale), "cancellation_fraction": 1-abs(val)/scale if scale else None,
                "API_exact_abs_residual": float(val_error), "API_exact_scaled_residual": float(val_error/scale),
                "API_JVP_exact_abs_residual": float(jvp_error), "API_JVP_exact_scaled_residual": float(jvp_error/ds),
                "decimal120_value": r["decimal_tokens_value"], "decimal120_alpha_JVP": r["decimal_tokens_jvp"],
                "decimal120_positive_scale": mp_text(mp.mpf(r["decimal_tokens_plus"])+mp.mpf(r["decimal_tokens_minus"])),
                "API_minus_decimal120": mp_text(exact_float(val)-mp.mpf(r["decimal_tokens_value"])),
                "API_JVP_minus_decimal120": mp_text(exact_float(jvp)-mp.mpf(r["decimal_tokens_jvp"]))})
    s = rows[0]["value_API_per_H_s"]; ds = rows[0]["alpha_JVP_API_per_H_s"]
    for quantity, fieldname in [(s, "value_API_per_H_s"), (ds, "alpha_JVP_API_per_H_s")]:
        scale = rows[0]["positive_scale"] if fieldname.startswith("value") else rows[0]["jvp_component_scale"]
        for idx, multiplier in [(1, 2), (2, 1)]:
            checks.bound("accounting_"+fieldname+"_"+OBS[idx], abs(rows[idx][fieldname]-multiplier*quantity)/scale,
                         limits["accounting_positive_scale_eps"]*EPS, context)
    photon_energy = math.fsum((b["Et_eV"]*electron_volt+b["Ec_eV"]*electron_volt)*b["Gamma"] for b in bins)
    checks.bound("photon_atomic_energy_balance", abs(photon_energy-A2S_THRESHOLD_EV*electron_volt*s)/(A2S_THRESHOLD_EV*electron_volt*rows[0]["positive_scale"]),
                 limits["accounting_positive_scale_eps"]*EPS, context)
    ledger = {**context, "S": s, "dx_upper_dt": -s, "dx_ground_dt": s,
              "photon_number_rate": rows[1]["value_API_per_H_s"],
              "photon_energy_J_per_H_s": photon_energy,
              "atomic_energy_J_per_H_s": -A2S_THRESHOLD_EV*electron_volt*s,
              "alpha_JVP_S": ds}
    output_bins = []
    for b in bins:
        output_bins.append({**context, **{k: v for k, v in b.items() if k != "weights"},
                            **{"weight_"+o: v for o, v in zip(OBS, b["weights"])}})
    return rows, ref_rows, output_bins, ledger


def differences(rows):
    index = {(r["table"], r["lambda"], r["alpha"], r["mode"], r["observable"]): r for r in rows}
    output = []
    with mp.workdps(120):
        for key, b in index.items():
            if key[0] != "base":
                continue
            hi = index[("hires", *key[1:])]
            scale = (mp.mpf(b["decimal120_positive_scale"])+mp.mpf(hi["decimal120_positive_scale"]))/2
            d = mp.mpf(hi["decimal120_value"])-mp.mpf(b["decimal120_value"])
            dj = mp.mpf(hi["decimal120_alpha_JVP"])-mp.mpf(b["decimal120_alpha_JVP"])
            output.append({"lambda": key[1], "alpha": key[2], "mode": key[3], "observable": key[4],
                "base_decimal120": b["decimal120_value"], "hires_decimal120": hi["decimal120_value"],
                "delta_hires_minus_base": mp_text(d), "absolute_difference": mp_text(abs(d)),
                "mean_positive_scale": mp_text(scale), "absolute_difference_over_mean_positive": mp_text(abs(d)/scale) if scale else None,
                "alpha_JVP_difference": mp_text(dj), "abs_alpha_JVP_difference_over_mean_positive": mp_text(abs(dj)/scale) if scale else None,
                "API_difference": hi["value_API_per_H_s"]-b["value_API_per_H_s"],
                "API_alpha_JVP_difference": hi["alpha_JVP_API_per_H_s"]-b["alpha_JVP_API_per_H_s"]})
    return output


def plots(out, rows, delta):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})
    for mode in ["raw", "normalized"]:
        fig, axes = plt.subplots(2, 4, figsize=(15, 6), constrained_layout=True)
        for col, ob in enumerate(OBS[1:]):
            for table, linestyle in [("base", "--"), ("hires", "-")]:
                for lam, color in [(2, "#0072B2"), (8, "#D55E00"), (32, "#009E73")]:
                    rr = [r for r in rows if r["table"] == table and r["lambda"] == lam and r["mode"] == mode and r["observable"] == ob]
                    xs = [float(Fraction(r["alpha"])) for r in rr]
                    for row, quantity in enumerate(["decimal120_value", "decimal120_alpha_JVP"]):
                        axes[row, col].plot(xs, [float(r[quantity]) for r in rr], linestyle, color=color,
                            marker="o" if table == "base" else "x", label=f"{table}, lambda={lam}")
                        axes[row, col].set_yscale("symlog", linthresh=1e-16)
                        axes[row, col].set_xlabel("alpha (dimensionless)")
                        axes[row, col].grid(alpha=.2)
            axes[0, col].set_title("phi="+ob)
        axes[0, 0].set_ylabel("J[phi] per H per s")
        axes[1, 0].set_ylabel("dJ[phi]/dalpha per H per s")
        axes[0, 0].legend(fontsize=7)
        fig.suptitle(f"{mode}: base NVIRT=311 / 2s=140; hires NVIRT=1493 / 2s=408\nDecimal-token reference, 120 digits; identical field and populations; symlog axes")
        fig.savefig(out / f"responses_{mode}.png", dpi=160); plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)
    for col, mode in enumerate(["raw", "normalized"]):
        for ob, color in [("1", "#555555"), ("u", "#0072B2"), ("u^2", "#D55E00"), ("window", "#009E73")]:
            rr = [r for r in delta if r["mode"] == mode and r["observable"] == ob]
            x = np.arange(len(rr))
            for row, name in enumerate(["absolute_difference", "absolute_difference_over_mean_positive"]):
                axes[row, col].plot(x, [float(r[name]) for r in rr], "o-", label="phi="+ob, color=color)
                axes[row, col].set_yscale("symlog", linthresh=1e-20)
                axes[row, col].set_xticks(x, [f"{r['lambda']},{r['alpha']}" for r in rr], rotation=40, fontsize=7)
                axes[row, col].set_xlabel("(lambda, alpha)"); axes[row, col].grid(alpha=.2)
        axes[0, col].set_title(mode); axes[0, col].legend(fontsize=8)
    axes[0, 0].set_ylabel("|hires - base| per H per s")
    axes[1, 0].set_ylabel("|difference| / mean positive rate scale")
    fig.suptitle("Two discrete measures: base 140 vs hires 408 2s bins\n120-digit decimal path; LTE zeros retained; no closeness acceptance tolerance")
    fig.savefig(out / "base_hires_differences.png", dpi=160); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
    for table, color in [("base", "#0072B2"), ("hires", "#D55E00")]:
        rr = [r for r in rows if r["table"] == table]
        for ax, name, title in zip(axes, ["API_exact_scaled_residual", "API_JVP_exact_scaled_residual"],
                                  ["API value / positive scale", "API alpha JVP / derivative component scale"]):
            ax.scatter(np.arange(len(rr)), [r[name] for r in rr], s=10, label=table, alpha=.65, color=color)
            ax.set_yscale("symlog", linthresh=1e-20); ax.set_title(title)
            ax.set_xlabel("all raw + normalized case/observable rows"); ax.grid(alpha=.2); ax.legend()
    axes[0].set_ylabel("absolute residual / positive scale (dimensionless)")
    fig.suptitle("Arithmetic check: existing binary64 API vs exact-input 120-digit scalar reference\nSeparate from table-resolution differences")
    fig.savefig(out / "reference_residuals.png", dpi=160); plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT), "execution output must be outside Git worktree"
    out.mkdir(parents=True, exist_ok=False)
    started = time.time()
    cases = json.loads((HERE / "CASES.json").read_text())
    assert cases["lambda"] == [2, 8, 32] and cases["alpha"] == ["-1/8", "0", "1/8"]
    assert cases["test_functions"] == OBS[1:] and cases["precisions_dps"] == [80, 120]
    tables, identity = inputs(out)
    checks = Checks()
    sym = symbolic()
    dump(out / "SYMPY.json", {"residuals": sym, "version": sp.__version__, "module_path": sp.__file__})
    for name, residual in sym.items():
        checks.bound("symbolic_"+name, 0 if residual == "0" else 1, 0, {})
    checks.bound("h_equals_2pi_hbar", abs(2*math.pi*hbar-h)/h, 4*EPS, {})
    rows, refs, bins, ledgers = [], [], [], []
    for table in tables:
        for mode in ["raw", "normalized"]:
            for lam in cases["lambda"]:
                for alpha in cases["alpha"]:
                    print(f"RUN table={table.label} mode={mode} lambda={lam} alpha={alpha}", flush=True)
                    r, f, b, l = compare_case(table, lam, alpha, mode, identity, cases["roundoff_limits"], checks)
                    rows.extend(r); refs.extend(f); bins.extend(b); ledgers.append(l)
    delta = differences(rows)
    for name, data in [("RESPONSES.csv", rows), ("REFERENCES.csv", refs), ("BIN_API_INPUTS_OUTPUTS.csv", bins),
                       ("BASE_HIRES_DIFFERENCES.csv", delta), ("NUMBER_ENERGY_LEDGER.csv", ledgers)]:
        csv_write(out / name, data)
    dump(out / "CHECKS.json", checks.rows)
    plots(out, rows, delta)
    failures = [r for r in checks.rows if not r["passed"]]
    result = {
        "task": cases["task"],
        "status": "PASS_BOUNDED_BASE_HIRES_SINGLE_FIELD_RESPONSE_RESEARCH" if not failures else "BLOCKED_RESEARCH_CHECK_FAILURE",
        "claim": "NO_PASS_REC_PHYSICAL_SPLIT", "physical_inputs_authenticated": False, "provider_admitted": False,
        "continuous_convergence_certified": False, "B": None, "mu": None,
        "delivery_commit": DELIVERY, "delivery_tree": TREE,
        "tested_source_commit": git("rev-parse", "HEAD"), "tested_source_tree": git("rev-parse", "HEAD^{tree}"),
        "source_parent": git("rev-parse", "HEAD^"), "branch": git("branch", "--show-current"),
        "source_worktree": str(ROOT), "command_argv": [sys.executable, *sys.argv],
        "environment": {"python_executable": sys.executable, "python_version": sys.version, "platform": platform.platform(),
                        "numpy": {"version": np.__version__, "path": np.__file__},
                        "mpmath": {"version": mp.__version__, "path": mp.__file__},
                        "sympy": {"version": sp.__version__, "path": sp.__file__}},
        "constants": {"origin": "scipy.constants, same source used by existing paired API tests/stage scripts",
                      "electron_volt_J": electron_volt, "h_J_s": h, "hbar_J_s": hbar, "k_J_per_K": k,
                      "E21_eV_binary64": A2S_THRESHOLD_EV, "nu21_Hz": A2S_THRESHOLD_EV*electron_volt/h,
                      "manufactured_temperature_K": {str(l): A2S_THRESHOLD_EV*electron_volt/(k*l) for l in cases["lambda"]}},
        "input_identity": identity, "cases_sha256": sha((HERE / "CASES.json").read_bytes()),
        "coverage": {"field_cases": 9, "test_functions": 4, "tables": 2, "coefficient_modes": 2,
                     "table_mode_cases": len(ledgers), "response_rows_including_S": len(rows),
                     "reference_rows_two_precisions": len(refs), "bin_API_evaluations": len(bins),
                     "base_hires_difference_rows_including_S": len(delta), "new_symbolic_identities": len(sym),
                     "check_records": len(checks.rows), "failed_check_records": len(failures),
                     "historical_checks_counted": 0},
        "roundoff_limits": cases["roundoff_limits"], "failures": failures,
        "max_API_value_scaled_residual": max(r["API_exact_scaled_residual"] for r in rows),
        "max_API_JVP_scaled_residual": max(r["API_JVP_exact_scaled_residual"] for r in rows),
        "limits": ["two fixed discrete measures only; no continuous order or error upper bound",
                   "1 and u are dependent accounting checks", "decimal tokens do not certify table uncertainty",
                   "source C sequential floating-point normalization not replayed", "no physical map, evolution, angles or provider"],
        "not_run": ["prior O1/O2/O3 checkers and five pytest", "whole repository suite", "native C/history", "Rust/JAX/BASS", "Sage/Singular/Lean/xAct"],
        "duration_s": time.time()-started,
        "visual_inspection": "PENDING_HOST_READBACK", "optional_Wolfram": "SEPARATE_RECORDED_COMMAND",
    }
    dump(out / "RESULT.json", result)
    print(json.dumps({"status": result["status"], "coverage": result["coverage"], "failures": failures}, indent=2), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

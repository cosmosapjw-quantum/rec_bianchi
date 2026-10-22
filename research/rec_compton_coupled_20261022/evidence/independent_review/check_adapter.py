"""Independent saved-state algebra/Jacobian audit. No IVP is executed.

Reviewer wrote neither runtime nor author tests. This program reconstructs
the power and caloric identities from the frozen formulas and differentiates
the complete public RHS. It writes only JSON to stdout.
"""
from __future__ import annotations

import os
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np

UNIT = Path(__file__).resolve().parents[2]
RESEARCH = UNIT.parent
THERMAL = RESEARCH / "rec_thermal_moments_20261022"
DONOR = RESEARCH / "rec_rei_hheli_sandbox_20261021"
sys.path.insert(0, str(UNIT / "code"))
from compton_system import ComptonFull63
from thermal_system import ThermalSystem, thermal_uv

KB = 1.380649e-23
C = 299792458.0
HPLANCK = 6.62607015e-34
EV = 1.602176634e-19
K = 6.6524587051e-29 / (9.1093837139e-31 * C)
ARAD = 8 * math.pi**5 * KB**4 / (15 * HPLANCK**3 * C**3)
BRANCHES = ("actual_hot", "planck_reference")
SEEDS = ("s03_m03_r03", "s04_m04_r04")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(left, right, floor=1e-300):
    return abs(float(left) - float(right)) / max(abs(float(left)), abs(float(right)), floor)


def check(condition, label):
    if not condition:
        raise AssertionError(label)


def numerical_column(fun, y, column, epsilon=4e-6):
    h = epsilon * max(1.0, abs(float(y[column])))
    def value(k):
        trial = y.copy()
        trial[column] += k * h
        return np.asarray(fun(trial))
    if column == 3 and y[column] - 2*h < -1e-12:
        return (-25*value(0) + 48*value(1) - 36*value(2) + 16*value(3) - 3*value(4)) / (12*h)
    return (value(-2) - 8*value(-1) + 8*value(1) - value(2)) / (12*h)


def reconstruct(system, x, y, branch):
    """Use raw bin flux and physical populations, without adapter diagnostics."""
    field = system.geometry.fields(x, y[:40])
    Y = y[40:61] * system.scale
    X = float(system.atomic.q @ Y)
    eta = float((1 + system.atomic.q) @ Y)
    nb = system.geometry.baryon_number_density(x)
    ne = nb * X
    T = math.exp(float(y[62]))
    U = system.geometry.source.rhocrit_j_m3 * system.geometry.model.omega_gamma * y[4] / field["a"]**4
    Tr = 2.7255 / field["a"]
    Ur = ARAD * Tr**4
    energies = system.atomic.photon_energy_eV * EV
    flux = system.atomic.photon_flux_bins_base * thermal_uv(x)[1]
    Uv = math.fsum(float(f*e) for f, e in zip(flux, energies)) / C
    Mv = math.fsum(float(f*e*e) for f, e in zip(flux, energies)) / C
    Qh = -4*K*ne*KB*T*U
    Qr = 4*K*ne*KB*Ur*(Tr-T)
    Qv = K*ne*(Mv-4*KB*T*Uv)
    Q = (Qh if branch == "actual_hot" else Qr) + Qv
    g = 2*Q / (3*KB*T*nb*eta*field["H"])
    return dict(field=field, Y=Y, X=X, eta=eta, nb=nb, ne=ne, T=T,
                U=U, Tr=Tr, Ur=Ur, Uv=Uv, Mv=Mv, Qh=Qh, Qr=Qr, Qv=Qv, Q=Q, g=g)


def main():
    started = time.perf_counter()
    source_paths = [UNIT / "FROZEN_CONTRACT.md", UNIT / "THEORY_KO.md",
                    UNIT / "code/compton_system.py", UNIT / "code/test_compton_system.py",
                    UNIT / "evidence/COMPTON_SYSTEM_TESTS.json", Path(__file__)]
    source_paths += [THERMAL / "code" / n for n in ("thermal_system.py", "thermal_sources.py", "recombination_moments.py")]
    source_paths += [DONOR / "code" / n for n in ("coupled.py", "geometry.py", "atomic_network.py")]
    source_paths += [DONOR / "vendor" / n for n in ("baseline/canonical_fv.py", "baseline/species_hierarchy.py", "baseline/lrs_boltzmann.py", "tangent/tangent_core.py", "he31/prepared_moments.py")]
    source_paths += [RESEARCH / "rec_thermal_omitted_budget_20261022/code/compton_budget.py"]
    source_before = {str(p.relative_to(RESEARCH)): sha(p) for p in source_paths}
    report = dict(schema="rec.compton.independent.adapter_checks.v1", status="IN_PROGRESS",
                  reviewer="compton_independent_review; authored none of reviewed runtime or author tests",
                  environment=dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform()),
                  source_hashes_before=source_before, inputs={}, algebra=[], full_jacobians=[], hubble_gradients=[], neutral_limits=[])
    for seed in SEEDS:
        config_path = DONOR / "results/pilot_v2/cases" / seed / "RESULT.json"
        directory = THERMAL / "results/thermal8" / (seed + "_mao2017_nominal")
        receipt_path = directory / "RESULT.json"
        receipt = json.loads(receipt_path.read_text())
        npz_path = directory / "trajectory.npz"
        check(sha(npz_path) == receipt["trajectory_sha256"], seed + " input hash")
        with np.load(npz_path, allow_pickle=False) as data:
            xs, ys = data["x"].copy(), data["raw_state"].copy()
        config = dict(json.loads(config_path.read_text())["config"], _case_wall_seconds=60.)
        parent = ThermalSystem(config, "mao2017")
        report["inputs"][seed] = dict(config_sha256=sha(config_path), trajectory_sha256=sha(npz_path),
                                     receipt_sha256=sha(receipt_path), states=[0, 54, 108], shape=list(ys.shape))
        for branch in BRANCHES:
            system = ComptonFull63(config, branch)
            for index in (0, 54, 108):
                x, y = float(xs[index]), ys[index].copy()
                r = reconstruct(system, x, y, branch)
                d = system.sample(x, y)
                rhs = system.rhs(x, y)
                inherited_rhs = parent.rhs(x, y)
                check(np.array_equal(rhs[:62], inherited_rhs[:62]), "unchanged first62 RHS")
                check(np.array_equal(y[[40, 45, 46]], np.zeros(3)), "physical native n/T exactly zero")
                power_errors = {key: relative(d[key], r[oracle]) for key, oracle in (
                    ("compton_actual_hot_W_m3", "Qh"), ("compton_planck_reference_W_m3", "Qr"),
                    ("compton_uv_W_m3", "Qv"), ("U_gamma_actual_J_m3", "U"),
                    ("U_uv_J_m3", "Uv"), ("M_uv_J2_m3", "Mv"))}
                check(max(power_errors.values()) < 3e-14, "independent raw-bin powers")
                g_error = abs(system.compton_logT_rhs(x, y)-r["g"]) / max(1., abs(r["g"]))
                rhs_error = abs(rhs[62]-inherited_rhs[62]-r["g"]) / max(1., abs(r["g"]))
                check(max(g_error, rhs_error) < 3e-13, "power-to-logT conversion")
                grad_energy = np.zeros(63)
                grad_energy[40:61] = (1.5*KB*r["T"]*(1+system.atomic.q)+system.atomic.ionization_energy_J)*system.scale
                grad_energy[62] = 1.5*KB*r["T"]*r["eta"]
                energy_derivative = float(grad_energy @ rhs)
                energy_source = (d["photo_absorbed_W_m3"] - d["total_escape_W_m3"] + r["Q"]) / (r["nb"]*r["field"]["H"])
                energy_expected = energy_source - 3*KB*r["T"]*r["eta"]
                energy_scale = abs(energy_source)+abs(3*KB*r["T"]*r["eta"])
                energy_error = abs(energy_derivative-energy_expected) / max(energy_scale, 1e-300)
                check(energy_error < 5e-12, "caloric first law including binding and particle change")
                ledger = math.fsum((d["kinetic_net_without_compton_W_m3"]+r["Q"]+d["ion_source_W_m3"],
                                   -(r["Qh"] if branch == "actual_hot" else r["Qr"]),
                                   -d["photo_absorbed_W_m3"]-r["Qv"], d["total_escape_W_m3"]))
                ledger_scale = math.fsum(abs(v) for v in (d["gas_energy_source_W_m3"], d["compton_bath_source_W_m3"],
                                                        d["uv_bath_source_W_m3"], d["escaped_radiation_source_W_m3"]))
                ledger_error = abs(ledger)/max(ledger_scale, 1e-300)
                check(ledger_error < 5e-12, "independent source ledger")
                report["algebra"].append(dict(seed=seed, index=index, branch=branch, power_relative_errors=power_errors,
                                              logT_scaled_error=g_error, RHS_addition_scaled_error=rhs_error,
                                              energy_throughput_scaled_error=energy_error, ledger_scaled_error=ledger_error,
                                              inherited_first62_rhs_exact=True, neutron_tritium_exact_zero=True))
            # Four whole 63-by-63 checks, with the parent source identity kept.
            index = 54 if seed == SEEDS[0] else 0
            x, y = float(xs[index]), ys[index].copy()
            analytic = system.jac(x, y)
            numeric = np.column_stack([numerical_column(lambda trial: system.rhs(x, trial), y, j) for j in range(63)])
            scaled = abs(analytic-numeric)/np.maximum(1., np.maximum(abs(analytic), abs(numeric)))
            worst = tuple(int(i) for i in np.unravel_index(np.argmax(scaled), scaled.shape))
            check(float(scaled.max()) < 3e-6, "complete 63x63 Jacobian")
            inherited_jac = parent.jac(x, y)
            check(np.array_equal(analytic[:62], inherited_jac[:62]), "unchanged first62 Jacobian rows")
            report["full_jacobians"].append(dict(seed=seed, index=index, branch=branch, columns=63,
                max_entry_scaled_error=float(scaled.max()), worst_row=worst[0], worst_column=worst[1],
                analytic_at_worst=float(analytic[worst]), numeric_at_worst=float(numeric[worst]),
                per_column_max_scaled_error=np.max(scaled, axis=0).tolist(), inherited_first62_jacobian_rows_exact=True))
            # The composition derivative at exactly neutral X=0 must remain finite.
            neutral = ys[54].copy()
            for group in system.atomic.isotope_groups.values():
                ii = np.asarray(group, dtype=int)
                inventory = float(np.sum(neutral[40+ii]*system.scale[ii]))
                neutral[40+ii] = 0.
                neutral[40+ii[0]] = inventory/system.scale[ii[0]]
            xn = float(xs[54])
            row = system.compton_jacobian_row(xn, neutral)
            check(system.compton_logT_rhs(xn, neutral) == 0., "neutral gas power")
            errors = []
            for column in range(40, 61):
                numerical = float(numerical_column(lambda trial: system.compton_logT_rhs(xn, trial), neutral, column))
                errors.append(abs(row[column]-numerical)/max(1., abs(row[column]), abs(numerical)))
            check(max(errors) < 3e-6, "neutral composition derivative")
            report["neutral_limits"].append(dict(seed=seed, branch=branch, logT_source=0., checked_columns=21,
                                                 max_scaled_error=max(errors), nonzero_composition_derivative=bool(np.any(row[40:61]))))
        # d ln H derived by numerical differentiation of the owned Hamiltonian.
        x, y = float(xs[54]), ys[54].copy()
        f = parent.geometry.fields(x, y[:40])
        H = f["H"]
        expected = {1: -3*parent.geometry.source.h0**2*f["Pi_matter_norm"]/H**2,
                    2: parent.geometry.source.href**2*y[2]/H**2,
                    4: parent.geometry.source.h0**2*parent.geometry.model.omega_gamma/(2*H**2*f["a"]**4),
                    22: parent.geometry.source.h0**2*parent.geometry.model.omega_nu/(2*H**2*f["a"]**4)}
        errors = {}
        for column, value in expected.items():
            numerical = float(numerical_column(lambda trial: parent.geometry.fields(x, trial[:40])["H"], y, column, 1e-5))/H
            errors[str(column)] = dict(analytic=value, numerical=numerical, absolute_error=abs(value-numerical))
        check(max(v["absolute_error"] for v in errors.values()) < 1e-9, "Hamiltonian H derivatives")
        report["hubble_gradients"].append(dict(seed=seed, index=54, columns=errors))
    after = {str(p.relative_to(RESEARCH)): sha(p) for p in source_paths}
    report.update(status="PASS_SCOPED", source_hashes_after=after, source_unchanged=after == source_before,
                  wall_seconds=time.perf_counter()-started,
                  thresholds=dict(full_Jacobian_entry_scaled=3e-6, source_energy_scaled=5e-12),
                  finite_difference=dict(step=4e-6, order=4, normalization="max(1, abs(analytic entry), abs(numeric entry))",
                                         boundary="forward stencil only for inherited coordinate3 u>=0"),
                  execution=dict(new_ODE_runs=0, old_full_suite_reruns=0),
                  limitations=["Finite saved-state checks support implementation preflight, not new trajectory results.",
                               "No independent reconstruction of actual photon recoil or induced spectrum was attempted.",
                               "Whole-RHS finite differences include smooth signed species trials; physical admission is separate.",
                               "Driver and campaign results are outside this adapter receipt."])
    check(after == source_before, "reviewed source identity stable during check")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

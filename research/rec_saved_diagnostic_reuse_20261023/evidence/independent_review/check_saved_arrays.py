"""Independent C2 read-only arithmetic and evidence checks; no science imports.

This reviewer script reads immutable files and retained arrays only.  It does
not call the profiling harness, scientific adapters, an IVP, or old test suites.
"""
from __future__ import annotations

import os
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
import time
START = time.perf_counter()
import ast
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
import numpy as np

OUT = Path(__file__).resolve().parent
STAGE = OUT.parents[1]
REPO = STAGE.parents[1]
OLD = REPO / "research/rec_compton_coupled_20261022"
ATTEMPT = STAGE / "evidence/profile/attempt_001"
SOURCE_HEAD = "40f7cf12b509377350e9a16da461e8ef97cdcb62"
SOURCE_TREE = "a136dea6c4ade8c6be442843800d0eb1458caa5f"
GATHER_FIELDS = ("x", "z", "raw_state", "Y", "T_K", "diagnostics", "diagnostic_names",
                 "inherited_diagnostics", "inherited_diagnostic_names", "signed_observables",
                 "signed_observable_names", "isotope_scales", "initial_Y", "integrand_names",
                 "integrands_J_per_baryon_per_x", "einstein_constraint")
checked = {}


def digest(path):
    path = Path(path)
    answer = hashlib.sha256(path.read_bytes()).hexdigest()
    checked[str(path.relative_to(REPO))] = answer
    return answer


def read_json(path):
    digest(path)
    return json.loads(Path(path).read_text())


def read_npz(path):
    digest(path)
    with np.load(path, allow_pickle=False) as source:
        return {name: source[name].copy() for name in source.files}


def exact(a, b, name):
    assert a.shape == b.shape and a.dtype == b.dtype, name + ":shape_or_dtype"
    assert a.tobytes(order="C") == b.tobytes(order="C"), name + ":array_bytes"


def close(a, b, name, rtol=3e-14, atol=1e-300):
    # Existing saved-array checks use this arithmetic tolerance; it is not a
    # replacement or relaxation of any original scientific admission gate.
    assert np.allclose(a, b, rtol=rtol, atol=atol), name


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def independently_selected(a, c):
    reasons = {}
    def add(index, reason):
        reasons.setdefault(int(index), []).append(reason)
    n = len(a["x"])
    add(0, "left_endpoint"); add(n - 1, "right_endpoint")
    add(int(np.argmax(a["T_K"])), "temperature_peak")
    names = list(a["diagnostic_names"])
    for name in ("source_energy_residual", "photo_rr_dr_source_energy_residual",
                 "transfer_ledger_residual_scaled", "compton_backreaction_ratio"):
        add(int(np.argmax(np.abs(a["diagnostics"][:, names.index(name)]))), "max_abs:" + name)
    for column, name in enumerate(c["coefficient_names"]):
        for i in range(n - 1):
            if bool(c["in_published_accuracy_domain"][i, column]) != bool(c["in_published_accuracy_domain"][i+1, column]):
                add(i, "fit_boundary_left:" + str(name)); add(i+1, "fit_boundary_right:" + str(name))
    for name in ("coefficient_underflow_to_zero", "ci_channel_power_underflow_to_zero", "ce_channel_power_underflow_to_zero"):
        for i in range(n - 1):
            if tuple(c[name][i]) != tuple(c[name][i+1]):
                add(i, "underflow_boundary_left:" + name); add(i+1, "underflow_boundary_right:" + name)
    mandatory = sorted(reasons)
    assert len(mandatory) <= 64 and n == 1025
    # Independent nearest-neighbour sweep instead of the harness's distance matrix.
    while len(reasons) < 64:
        selected = sorted(reasons)
        distances = [min(abs(i-j) for j in selected) for i in range(n)]
        add(distances.index(max(distances)), "uniform_maximin_fill")
    indices = np.array(sorted(reasons), dtype=np.int64)
    return indices, mandatory, {str(i): reasons[i] for i in indices}


def node_support(name, valid):
    if name in ("ci_kinetic", "ci_binding", "ci_total_gas", "ci_energy_only", "ci_particle_only", "ci_full"):
        return valid[:, 0] & valid[:, 1] & valid[:, 2]
    if name == "ce_HI":
        return valid[:, 3]
    if name == "ce_HeII":
        return valid[:, 4]
    if name in ("included_collision_kinetic", "included_collision_total"):
        return valid[:, 0] & valid[:, 1] & valid[:, 2] & valid[:, 3] & valid[:, 4]
    if name == "included_collision_total_gas":
        return valid[:, 3] & valid[:, 4]
    return None


def profile_count(profile, suffix, name):
    rows = [r for r in profile["functions"] if r["file"].endswith(suffix) and r["name"] == name]
    assert len(rows) == 1, (suffix, name, len(rows))
    return rows[0]["total_calls"]


head, tree = subprocess.check_output(["git", "rev-parse", "HEAD", "HEAD^{tree}"], cwd=REPO, text=True).splitlines()
assert (head, tree) == (SOURCE_HEAD, SOURCE_TREE)
subprocess.run(["git", "diff", "--exit-code", "HEAD"], cwd=REPO, check=True, capture_output=True)
manifest = read_json(ATTEMPT / "INPUT_MANIFEST.json")
corpus = read_json(ATTEMPT / "CORPUS_MANIFEST.json")
start = read_json(ATTEMPT / "STARTED.json")
finish = read_json(ATTEMPT / "FINISHED.json")
summary = read_json(ATTEMPT / "SUMMARY.json")
for key in ("script", "scope"):
    row = start[key]
    assert digest(REPO / row["path"]) == row["sha256"]
assert digest(OLD / "NEXT_UNIT_CONTRACT.md") == "02d7b778142ea35402110f042373cae7e4e2b5987039a0b3d32cc93318dafded"
for key in ("source_files", "collision_source_files"):
    for name, expected in manifest[key].items():
        assert digest(REPO / name) == expected, name
for row in manifest["files"]:
    path = REPO / row["path"]
    assert path.stat().st_size == row["bytes"] and digest(path) == row["sha256"], str(path)
    if "raw_state_shape" in row:
        with np.load(path, allow_pickle=False) as saved:
            raw, x = saved["raw_state"], saved["x"]
            assert list(raw.shape) == row["raw_state_shape"] == [len(x), 63]
            assert np.isfinite(raw).all() and np.isfinite(x).all() and (np.diff(x) > 0).all()
thermal = REPO / "research/rec_thermal_moments_20261022"
omitted = REPO / "research/rec_thermal_omitted_budget_20261022"
donor = REPO / "research/rec_rei_hheli_sandbox_20261021"
parent_lock = read_json(thermal / "provenance/PARENT_SOURCE_LOCK.json")
for row in parent_lock["files"]:
    path = REPO / row["path"]
    assert path.stat().st_size == row["bytes"] and digest(path) == row["sha256"]
thermal_table = {str(Path(name).relative_to(thermal.relative_to(REPO))): sha for name, sha in manifest["source_files"].items() if name.startswith(str(thermal.relative_to(REPO)) + "/")}
omitted_table = {str(Path(name).relative_to(omitted.relative_to(REPO))): sha for name, sha in manifest["source_files"].items() if name.startswith(str(omitted.relative_to(REPO)) + "/")}
tid = hashlib.sha256(json.dumps(thermal_table, sort_keys=True).encode()).hexdigest()
oid = hashlib.sha256(json.dumps(omitted_table, sort_keys=True).encode()).hexdigest()
runtime = hashlib.sha256(canonical(dict(files=manifest["source_files"], thermal_identity=tid, omitted_identity=oid))).hexdigest()
cid = hashlib.sha256(canonical(dict(files=manifest["collision_source_files"], coupled_runtime_identity=runtime))).hexdigest()
assert runtime == manifest["runtime_identity"] == "c89f576e2c7f15a0a1d0d3f96ce72de516245cbb83b5d4fbaeede342a76e86ac"
assert cid == manifest["collision_source_identity"]
assert finish["status"] == summary["status"] == "PASS_C2_BASELINE_PROFILE"
assert finish["IVP_attempts"] == summary["IVP_attempts"] == [] and finish["new_IVPs"] == 0
assert finish["active_wall_seconds"] < 600 and start["numerical_threads"] == start["numerical_workers"] == 1
print(f"SOURCE_PASS head={head} tree={tree} runtime={runtime} collision={cid}")

# Read constants as literals from their source owner without importing the code.
constant_tree = ast.parse((omitted / "code/compton_budget.py").read_text())
constants = {n.targets[0].id: ast.literal_eval(n.value) for n in constant_tree.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Constant)}
kb, ev = constants["KB_J_K"], constants["EV_J"]
K = constants["SIGMA_T_M2"] * constants["C_M_S"] / (constants["ME_KG"] * constants["C_M_S"]**2)
ar = 8 * math.pi**5 * kb**4 / (15 * constants["H_J_S"]**3 * constants["C_M_S"]**3)
atomic_tree = ast.parse((donor / "code/atomic_network.py").read_text())
native = {}
for node in ast.walk(atomic_tree):
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Attribute) and node.targets[0].attr in ("q", "Z", "A") and isinstance(node.value, ast.Call):
        native[node.targets[0].attr] = np.array(ast.literal_eval(node.value.args[0]))
coefficients = read_json(donor / "data/atomic_coefficients.json")
energy = np.zeros(21)
for group in ((0,), (1,2), (3,4), (5,6), (7,8,9), (10,11,12), (13,14,15,16), (17,18,19,20)):
    cumulative = 0.0
    for i in group:
        energy[i] = cumulative * ev
        if native["Z"][i] and native["q"][i] < native["Z"][i]:
            cumulative += coefficients["photo_VF1996"][f'{native["Z"][i]}:{native["q"][i]}']["Eth_eV"]
fit = read_json(omitted / "data/HG97_COLLISIONAL_SOURCE.json")
cases = []
expected_counts = (("code/thermal_system.py", "point", 192), ("code/geometry.py", "fields", 448),
                   ("code/atomic_network.py", "evaluate", 192), ("code/atomic_network.py", "rates", 192),
                   ("code/thermal_sources.py", "evaluate", 128), ("code/thermal_sources.py", "coefficients", 128),
                   ("code/recombination_moments.py", "evaluate", 128), ("code/compton_system.py", "compton_terms", 192),
                   ("code/compton_system.py", "_compton_state", 192), ("code/coupled.py", "thermal_uv", 384),
                   ("code/geometry.py", "baryon_number_density", 384), ("code/geometry.py", "normalized", 128),
                   ("legendre.py", "legvander", 64), ("prepared_moments.py", "moments", 448),
                   ("code/thermal_sources.py", "mao_factor", 1664))
for label, selection in sorted(corpus.items()):
    result = read_json(ATTEMPT / label / "RESULT.json")
    receipt = read_json(OLD / "results/compton8" / label / "RESULT.json")
    assert receipt["status"] == "COMPLETE" and receipt["source_identity"] == runtime
    assert receipt["source_files"] == manifest["source_files"] and all(receipt["gates"].values())
    assert hashlib.sha256(canonical(receipt["specification"])).hexdigest() == receipt["case_identity"]
    a = read_npz(OLD / "results/compton8" / label / "dense_1025.npz")
    oldc = read_npz(OLD / "results/analysis_v1" / label / "collisions/collisions_dense_1025.npz")
    assert str(a["compton_branch"]) == receipt["specification"]["branch"]
    assert hashlib.sha256(a["initial_state"].tobytes()).hexdigest() == receipt["specification"]["initial_state_sha256"]
    assert str(oldc["input_trajectory_sha256"]) == receipt["outputs"]["dense_1025.npz"]["sha256"]
    assert str(oldc["collision_source_identity"]) == cid
    output_path = ATTEMPT / label / "PROFILED_OUTPUTS.npz"
    assert digest(output_path) == result["retained_outputs"]["sha256"] and output_path.stat().st_size == result["retained_outputs"]["bytes"]
    p = read_npz(output_path)
    idx, mandatory, reasons = independently_selected(a, oldc)
    exact(idx, p["selected_indices"], label + ":indices")
    assert idx.tolist() == selection["selected_indices"] and mandatory == selection["mandatory_indices"] and reasons == selection["reasons"]
    assert hashlib.sha256(a["raw_state"][idx].tobytes()).hexdigest() == selection["exact_state_sha256"]
    assert hashlib.sha256(a["x"][idx].tobytes()).hexdigest() == selection["x_sha256"]
    for name in GATHER_FIELDS:
        expected = a[name][idx] if a[name].ndim and a[name].shape[0] == 1025 else a[name]
        exact(p["gather__" + name], expected, label + ":gather:" + name)
    c = {name.removeprefix("collision__"): value for name, value in p.items() if name.startswith("collision__")}
    collision_equal = 0
    for name, value in c.items():
        if "cumulative" in name or name.endswith("_supported_intervals"):
            continue
        expected = oldc[name][idx] if oldc[name].ndim and oldc[name].shape[0] == 1025 else oldc[name]
        exact(value, expected, label + ":collision:" + name)
        collision_equal += 1
    d = dict(zip(p["gather__diagnostic_names"], p["gather__diagnostics"].T))
    x, Y, T = p["gather__x"], p["gather__Y"], p["gather__T_K"]
    nb, ne, H, eta = (d[name] for name in ("nb_m3", "ne_m3", "H_s", "gas_particles_per_baryon"))
    close(ne, nb * (Y @ native["q"]), label + ":electron_owner")
    close(eta, Y @ (1 + native["q"]), label + ":particle_owner")
    close(d["gas_energy_J_per_baryon"], 1.5 * kb * T * eta + Y @ energy, label + ":gas_energy")
    close(d["work_J_per_baryon_per_x"], 3 * kb * T * eta, label + ":work")
    branch = str(a["compton_branch"])
    selected_name = "compton_actual_hot_W_m3" if branch == "actual_hot" else "compton_planck_reference_W_m3"
    exact(d["compton_selected_W_m3"], d[selected_name], label + ":exclusive_branch")
    close(d["compton_actual_hot_W_m3"], -4 * K * ne * kb * T * d["U_gamma_actual_J_m3"], label + ":actual_hot")
    close(d["compton_planck_reference_W_m3"], 4 * K * ne * kb * d["U_planck_reference_J_m3"] * (d["T_planck_reference_K"] - T), label + ":planck")
    close(d["U_planck_reference_J_m3"], ar * d["T_planck_reference_K"]**4, label + ":planck_energy")
    close(d["T_planck_reference_K"], 2.7255 * 21 * np.exp(-x), label + ":planck_temperature")
    close(d["compton_uv_W_m3"], K * ne * (d["M_uv_J2_m3"] - 4 * kb * T * d["U_uv_J_m3"]), label + ":uv_power")
    exact(d["gas_energy_source_W_m3"], d["kinetic_net_W_m3"] + d["ion_source_W_m3"], label + ":gas_ledger_1")
    exact(d["gas_source_from_radiation_W_m3"], d["photo_absorbed_W_m3"] - d["total_escape_W_m3"] + d["compton_total_W_m3"], label + ":gas_ledger_2")
    stores = np.column_stack((d["gas_energy_source_W_m3"], -d["compton_selected_W_m3"], -d["photo_absorbed_W_m3"] - d["compton_uv_W_m3"], d["total_escape_W_m3"]))
    residual = np.array([math.fsum(row) for row in stores])
    throughput = np.array([math.fsum(abs(v) for v in row) for row in stores])
    exact(d["transfer_ledger_residual_W_m3"], residual, label + ":transfer_residual")
    exact(d["transfer_ledger_residual_scaled"], abs(residual) / np.maximum(throughput, 1e-300), label + ":transfer_scaled")
    close(d["gas_energy_source_J_per_baryon_per_x"], d["gas_source_from_radiation_W_m3"] / (nb * H), label + ":per_baryon_conversion")
    valid = np.column_stack([((T >= fit[kind]["published_temperature_range_K"][0]) & (T <= fit[kind]["published_temperature_range_K"][1])) for kind in ("CI", "CI", "CI", "CE", "CE")])
    exact(c["in_published_accuracy_domain"], valid, label + ":fit_domain")
    exact(c["analytic_continuation"], ~valid, label + ":continuation")
    assert c["ci_unavailable_mask"][[13,14,15,17,18,19]].all() and c["ce_unavailable_mask"][[7,10,13,14,15,17,18,19]].all()
    close(c["ci_binding_gradient_W_m3"], nb * (c["ci_dY_dt"] @ energy), label + ":binding_gradient")
    close(c["ci_particle_source_per_baryon_s"], c["ci_dY_dt"] @ native["q"], label + ":particle_gradient")
    q = dict(zip(c["process_names"], c["Q_W_m3"].T))
    f = dict(zip(c["forcing_names"], c["fixed_path_logT_forcing_per_x"].T))
    close(-q["ce_HI"] - q["ce_HeII"], nb * ne * (Y[:, [1,3,5]].sum(axis=1) * c["coefficients_SI"][:,3] + Y[:, [8,11]].sum(axis=1) * c["coefficients_SI"][:,4]), label + ":ce_targets")
    close(f["ci_full"], 2 * q["ci_kinetic"] / (3 * kb * T * nb * H * eta) - c["ci_particle_source_per_baryon_s"] / (H * eta), label + ":ci_full_forcing")
    close(c["energy_integrand_eV_baryon_per_x"], c["Q_W_m3"] / (nb[:,None] * H[:,None] * ev), label + ":collision_units")
    for category, names, values, cumulative in (("energy", c["process_names"], c["energy_integrand_eV_baryon_per_x"], c["energy_cumulative_trapezoid_eV_baryon"]), ("forcing", c["forcing_names"], c["fixed_path_logT_forcing_per_x"], c["fixed_path_logT_forcing_cumulative_trapezoid"])):
        pieces = (values[:-1] + values[1:]) * (0.5 * np.diff(x)[:,None])
        close(cumulative, np.vstack((np.zeros(values.shape[1]), np.cumsum(pieces, axis=0))), label + ":subset_cumulative:" + category)
        for k, name in enumerate(names):
            support = node_support(name, valid)
            mask = np.ones(len(x)-1, dtype=bool) if support is None else support[1:] & support[:-1]
            exact(c[category + "_supported_intervals"][:,k], mask, label + ":interval:" + str(name))
            entry = result["subset_collision_summary"]["energy_eV_per_baryon" if category == "energy" else "fixed_path_logT_forcing"][str(name)]
            close(entry["trapezoid"], pieces[:,k].sum(), label + ":subset_trapezoid:" + str(name))
            assert entry["total_intervals"] == 63
            if support is not None:
                assert entry["supported_intervals"] == int(mask.sum())
                close(entry["supported_interval_contribution"], pieces[mask,k].sum(), label + ":supported_integral:" + str(name))
    gp = read_json(ATTEMPT / label / "GATHER_PROFILE.json")
    cp = read_json(ATTEMPT / label / "COLLISION_PROFILE.json")
    for suffix, name, count in expected_counts:
        assert profile_count(gp, suffix, name) == count, (label, suffix, name)
    for suffix, name, count in (("collisional_budget.py", "evaluate", 64), ("collisional_budget.py", "coefficients", 64), ("analyze_collisions.py", "integrate_retained", 19)):
        assert profile_count(cp, suffix, name) == count
    for profile in (gp, cp):
        close(math.fsum(row["self_seconds"] for row in profile["functions"]), profile["profiler_total_self_seconds"], label + ":self_time_sum", rtol=3e-14, atol=1e-14)
        assert all(row["cumulative_seconds"] + 1e-15 >= row["self_seconds"] >= 0 for row in profile["functions"])
        assert not any(row["name"] in ("solve_ivp", "odeint", "BDF", "Radau", "RK45", "RK23", "DOP853", "LSODA") for row in profile["functions"])
    assert not any(row["file"].endswith(("geometry.py", "atomic_network.py")) for row in cp["functions"])
    cases.append(dict(label=label, selected_points=64, gather_byte_equal_fields=len(GATHER_FIELDS), collision_byte_equal_fields=collision_equal, mandatory_points=len(mandatory), independent_gas_sum_unequal_points=int(np.count_nonzero(d["gas_energy_source_W_m3"] != d["gas_source_from_radiation_W_m3"])), transfer_residual_max=float(np.max(abs(residual)/np.maximum(throughput,1e-300))), subset_masks_and_trapezoids_checked=True, static_call_counts_confirmed=True))
    print(f"CASE_PASS {label} points=64 gather_byte_equal={len(GATHER_FIELDS)} collision_byte_equal={collision_equal} masks=19 call_counts=18")
assert len(cases) == 8 and summary["states_total"] == 512
subprocess.run(["git", "diff", "--exit-code", "HEAD"], cwd=REPO, check=True, capture_output=True)
elapsed = time.perf_counter() - START
record = dict(status="PASS_INDEPENDENT_SAVED_ARRAY_CHECK", selected_stage="C2", source_head=head, source_tree=tree,
              runtime_identity=runtime, collision_identity=cid, command=[sys.executable, str(Path(__file__).relative_to(REPO))],
              active_wall_seconds=elapsed, cases=cases, files_checked_sha256=checked, new_IVPs=0, old_IVP_reruns=0,
              science_driver_imports=0, tolerances=dict(identical_arrays="dtype/shape and C-order byte equality", independent_formula_arithmetic="rtol=3e-14, atol=1e-300; inherited saved-array arithmetic criterion", timing_sums="rtol=3e-14, atol=1e-14"),
              scope="512 selected points, source and retained-array arithmetic only; no candidate/full-grid/scientific-promotion verdict")
with (OUT / "SAVED_ARRAY_CHECK.json").open("x") as stream:
    json.dump(record, stream, indent=2, sort_keys=True); stream.write("\n")
print(f"REVIEW_CHECK_PASS cases=8 states=512 IVPs=0 science_driver_imports=0 active_wall_seconds={elapsed:.9f}")

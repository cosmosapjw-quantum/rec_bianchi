"""Source-bound H/He CI/CE diagnostics on the new Compton trajectories.

``analyze_case(case_dir, output_dir)`` reads the receipt-bound comparison109,
dense513 and dense1025 arrays and writes a create-only, reproducible budget.
It never evolves a state. CI/CE remain omitted from the new coupled RHS;
these are fixed-path source integrals on that newly evolved path, not an
actual CI/CE energy exchange or a solved temperature correction.

HG97 fit support, analytic continuation, unavailable channels, and numerical
underflow have distinct fields. Interval support means both retained endpoints
are in the published domain; it does not certify the unsampled interior.
"""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import traceback

import numpy as np
import scipy
from scipy.integrate import simpson, cumulative_trapezoid

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
OMITTED = UNIT.parent / "rec_thermal_omitted_budget_20261022"
DONOR = UNIT.parent / "rec_rei_hheli_sandbox_20261021"
for _path in (OMITTED / "code", DONOR / "code"):
    if str(_path) not in sys.path:
        sys.path.append(str(_path))

import atomic_network as atomic_module
import collisional_budget as collision_module
import compton_budget as constants_module
from atomic_network import AtomicNetwork
from collisional_budget import CollisionalBudget
from compton_budget import EV_J, KB_J_K

PINNED_PROVIDER_FILES = {
    "code/collisional_budget.py": "39aa8e56021dfd764af867803c654d7452e5f2aa0d104258bbcfecbe10b6d252",
    "code/compton_budget.py": "a4338f76e81f34b3af1c13340c9df40140471f6ce5512bb720efa6061082a567",
    "data/HG97_COLLISIONAL_SOURCE.json": "09e3079eccba39c0e8c905c7eb1ac2e3eff2770a2c3a536697fc36d8ccadf2c5",
}
GRID_FILES = {"comparison_109": ("trajectory.npz", 109),
              "dense_513": ("dense_513.npz", 513),
              "dense_1025": ("dense_1025.npz", 1025)}
COEFFICIENT_NAMES = ("CI_HI", "CI_HeI", "CI_HeII", "CE_HI", "CE_HeII")
PROCESS_NAMES = ("photo_primary", "rr_kinetic", "dr_kinetic", "expansion_work",
                 "compton_selected", "compton_uv", "ci_kinetic", "ci_binding",
                 "ci_total_gas", "ce_HI", "ce_HeII", "included_collision_kinetic",
                 "included_collision_total_gas")
FORCING_NAMES = ("ci_energy_only", "ci_particle_only", "ci_full", "ce_HI", "ce_HeII",
                 "included_collision_total")


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _json_value(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def _save_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    with temporary.open("xb") as stream:
        stream.write((json.dumps(value, indent=2, allow_nan=False, default=_json_value) + "\n").encode())
        stream.flush()
        os.fsync(stream.fileno())
    os.link(temporary, path)
    temporary.unlink()


def _save_npz(path, arrays):
    path = Path(path)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    with temporary.open("xb") as stream:
        np.savez_compressed(stream, **arrays)
        stream.flush()
        os.fsync(stream.fileno())
    os.link(temporary, path)
    temporary.unlink()


def _source_identity(runtime_identity):
    for module, expected in ((collision_module, OMITTED / "code/collisional_budget.py"),
                             (constants_module, OMITTED / "code/compton_budget.py"),
                             (atomic_module, DONOR / "code/atomic_network.py")):
        if Path(module.__file__).resolve() != expected.resolve():
            raise ValueError("COLLISION_IMPORT_OWNER_CHANGED:" + module.__name__)
    files = {str(Path(__file__).resolve().relative_to(REPO)): _digest(__file__)}
    for name, expected in PINNED_PROVIDER_FILES.items():
        path = OMITTED / name
        actual = _digest(path)
        if actual != expected:
            raise ValueError("IMMUTABLE_COLLISION_SOURCE_CHANGED:" + name)
        files[str(path.relative_to(REPO))] = actual
    # The coupled runtime identity independently verifies its inherited atomic
    # source locks. Also retain the actual imported number-network module hash.
    path = Path(atomic_module.__file__).resolve()
    files[str(path.relative_to(REPO))] = _digest(path)
    value = dict(files=files, coupled_runtime_identity=runtime_identity)
    identity = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return identity, files


def integrate_retained(x, values, valid_nodes=None):
    """Signed integral with positive trapezoid weights and a separate Simpson value."""
    x, values = np.asarray(x, dtype=float), np.asarray(values, dtype=float)
    if (x.ndim != 1 or values.shape != x.shape or len(x) < 3
            or not np.isfinite(x).all() or not np.isfinite(values).all()
            or np.any(np.diff(x) <= 0)):
        raise ValueError("FINITE_INCREASING_RETAINED_GRID_REQUIRED")
    dx = np.diff(x)
    pieces = .5 * (values[:-1] + values[1:]) * dx
    absolute_pieces = .5 * (abs(values[:-1]) + abs(values[1:])) * dx
    positive = np.maximum(values, 0.)
    negative = np.minimum(values, 0.)
    if valid_nodes is None:
        supported = np.ones(len(x) - 1, dtype=bool)
    else:
        valid_nodes = np.asarray(valid_nodes)
        if valid_nodes.shape != x.shape or valid_nodes.dtype.kind != "b":
            raise ValueError("BOOLEAN_NODE_SUPPORT_MASK_REQUIRED")
        supported = valid_nodes[:-1] & valid_nodes[1:]
    trap, simp = float(pieces.sum()), float(simpson(values, x=x))
    return dict(
        trapezoid=trap, simpson=simp, simpson_minus_trapezoid=simp-trap,
        positive_part_trapezoid=float(np.sum(.5*(positive[:-1]+positive[1:])*dx)),
        negative_part_trapezoid=float(np.sum(.5*(negative[:-1]+negative[1:])*dx)),
        absolute_throughput_trapezoid=float(absolute_pieces.sum()),
        fit_support_applicable=valid_nodes is not None,
        supported_intervals=int(supported.sum()) if valid_nodes is not None else None,
        total_intervals=len(x)-1,
        supported_interval_contribution=float(pieces[supported].sum()) if valid_nodes is not None else None,
        continuation_or_boundary_contribution=float(pieces[~supported].sum()) if valid_nodes is not None else None,
        supported_absolute_throughput=float(absolute_pieces[supported].sum()) if valid_nodes is not None else None,
        continuation_or_boundary_absolute_throughput=float(absolute_pieces[~supported].sum()) if valid_nodes is not None else None,
    )


def _support_for(name, valid):
    if name in ("ci_kinetic", "ci_binding", "ci_total_gas", "ci_energy_only", "ci_particle_only", "ci_full"):
        return np.all(valid[:, :3], axis=1)
    if name == "ce_HI":
        return valid[:, 3]
    if name == "ce_HeII":
        return valid[:, 4]
    if name in ("included_collision_kinetic", "included_collision_total"):
        return np.all(valid, axis=1)
    if name == "included_collision_total_gas":
        # CI is an internal kinetic-to-binding transfer, so the total gas loss
        # consists only of the two included CE channels.
        return np.all(valid[:, 3:], axis=1)
    return None


def _read_grid(path, count, atomic, initial_state):
    with np.load(path, allow_pickle=False) as data:
        a = {name: data[name].copy() for name in data.files}
    x, raw, Y, T = a["x"], a["raw_state"], a["Y"], a["T_K"]
    if (x.shape != (count,) or raw.shape != (count, 63) or Y.shape != (count, 21)
            or T.shape != (count,) or not np.isfinite(x).all() or not np.isfinite(raw).all()
            or np.any(np.diff(x) <= 0) or np.any(Y < 0) or np.any(Y[:, [0, 5, 6]] != 0)
            or not np.array_equal(a["isotope_scales"], atomic.scales)
            or not np.array_equal(a["initial_state"], initial_state)
            or not np.allclose(Y, raw[:, 40:61]*atomic.scales, rtol=3e-15, atol=0)
            or not np.allclose(T, np.exp(raw[:, 62]), rtol=3e-15, atol=0)
            or not np.allclose(a["z"], 21*np.exp(-x)-1, rtol=3e-15, atol=0)):
        raise ValueError("COLLISION_SAVED_STATE_CONTRACT:" + path.name)
    names = a["diagnostic_names"].tolist()
    if len(names) != len(set(names)) or a["diagnostics"].shape != (count, len(names)):
        raise ValueError("COLLISION_DIAGNOSTIC_SCHEMA:" + path.name)
    d = {name: a["diagnostics"][:, i] for i, name in enumerate(names)}
    if not np.isfinite(a["diagnostics"]).all():
        raise ValueError("NONFINITE_SAVED_DIAGNOSTICS:" + path.name)
    for name in ("H_s", "nb_m3", "gas_particles_per_baryon"):
        if np.any(d[name] <= 0):
            raise ValueError("NONPOSITIVE_SAVED_OWNER:" + name)
    if not np.allclose(d["ne_m3"], d["nb_m3"]*(Y@atomic.q), rtol=3e-14, atol=1e-30):
        raise ValueError("SAVED_ELECTRON_OWNER_CHANGED")
    if not np.allclose(d["gas_particles_per_baryon"], Y@(1+atomic.q), rtol=3e-14, atol=0):
        raise ValueError("SAVED_PARTICLE_OWNER_CHANGED")
    return a, d


def _evaluate_grid(a, d, atomic, collision):
    x, Y, T = a["x"], a["Y"], a["T_K"]
    H, nb, ne, eta = (d[name] for name in ("H_s", "nb_m3", "ne_m3", "gas_particles_per_baryon"))
    n, nci, nce = len(x), len(collision.ci_specs), len(collision.ce_specs)
    coeff = np.zeros((n, 5))
    valid, underflow = np.zeros((n, 5), dtype=bool), np.zeros((n, 5), dtype=bool)
    ci_dY = np.zeros((n, 21))
    particle, gradient, balance, charge_balance = (np.zeros(n) for _ in range(4))
    baryon_balance, isotope_balance = np.zeros(n), np.zeros(n)
    ci_event, ci_volume, ci_binding = (np.zeros((n, nci)) for _ in range(3))
    ci_event_under, ci_volume_under, ci_power_under = (np.zeros((n, nci), dtype=bool) for _ in range(3))
    ce_power, ce_under = np.zeros((n, nce)), np.zeros((n, nce), dtype=bool)
    Q, F = np.zeros((n, len(PROCESS_NAMES))), np.zeros((n, len(FORCING_NAMES)))
    final = None
    for j in range(n):
        r = collision.evaluate(Y[j], float(T[j]), float(nb[j]), allow_extrapolation=True)
        coeff[j] = [r["coefficients"][name] for name in COEFFICIENT_NAMES]
        valid[j] = [r["validity"][name]["in_validated_domain"] for name in COEFFICIENT_NAMES]
        underflow[j] = [r["validity"][name]["underflow_to_zero"] for name in COEFFICIENT_NAMES]
        ci_dY[j], particle[j], gradient[j] = r["dY_dt"], r["particle_source"], r["ci_binding_gradient_W_m3"]
        balance[j] = abs(r["ci_gradient_residual_W_m3"])/max(abs(r["ci_kinetic_W_m3"])+abs(gradient[j]), 1e-300)
        charge_balance[j] = abs(r["particle_source_residual_s"])/max(abs(particle[j]), 1e-300)
        baryon_balance[j] = abs(atomic.A@r["dY_dt"])/max(float(np.sum(abs(atomic.A*r["dY_dt"]))), 1e-300)
        isotope_balance[j] = max(abs(float(r["dY_dt"][list(indices)].sum()))/
                                 max(float(np.sum(abs(r["dY_dt"][list(indices)]))), 1e-300)
                                 for indices in atomic.isotope_groups.values())
        for k, row in enumerate(r["ci_channels"]):
            ci_event[j, k], ci_volume[j, k], ci_binding[j, k] = (row[name] for name in
                ("event_rate_per_baryon_s", "event_rate_m3_s", "binding_W_m3"))
            ci_event_under[j, k], ci_volume_under[j, k], ci_power_under[j, k] = (row[name] for name in
                ("event_underflow_to_zero", "volume_underflow_to_zero", "power_underflow_to_zero"))
        for k, row in enumerate(r["ce_channels"]):
            ce_power[j, k], ce_under[j, k] = row["cooling_W_m3"], row["power_underflow_to_zero"]
        ce_hi = sum(row["cooling_W_m3"] for row in r["ce_channels"] if row["process"] == "CE_HI")
        ce_he = sum(row["cooling_W_m3"] for row in r["ce_channels"] if row["process"] == "CE_HeII")
        # Independently compare the explicit charge-state targets with provider
        # channel aggregation; no HeI metastable or Li proxy is introduced.
        check_ce = nb[j]*ne[j]*(Y[j, [1, 3, 5]].sum()*coeff[j, 3]+Y[j, [8, 11]].sum()*coeff[j, 4])
        if not np.isclose(ce_hi+ce_he, check_ce, rtol=3e-14, atol=1e-300):
            raise ValueError("CE_CHARGE_STATE_OWNER_MISMATCH")
        q = dict(photo_primary=d["photo_primary_W_m3"][j], rr_kinetic=-d["rr_cooling_W_m3"][j],
                 dr_kinetic=-d["dr_cooling_W_m3"][j], expansion_work=-nb[j]*H[j]*d["work_J_per_baryon_per_x"][j],
                 compton_selected=d["compton_selected_W_m3"][j], compton_uv=d["compton_uv_W_m3"][j],
                 ci_kinetic=r["ci_kinetic_W_m3"], ci_binding=r["ci_binding_W_m3"],
                 ci_total_gas=r["ci_kinetic_W_m3"]+r["ci_binding_W_m3"], ce_HI=-ce_hi, ce_HeII=-ce_he)
        q["included_collision_kinetic"] = q["ci_kinetic"]+q["ce_HI"]+q["ce_HeII"]
        q["included_collision_total_gas"] = q["ci_total_gas"]+q["ce_HI"]+q["ce_HeII"]
        Q[j] = [q[name] for name in PROCESS_NAMES]
        energy_factor = 2/(3*KB_J_K*T[j]*nb[j]*H[j]*eta[j])
        f = dict(ci_energy_only=energy_factor*q["ci_kinetic"],
                 ci_particle_only=-particle[j]/(H[j]*eta[j]),
                 ce_HI=energy_factor*q["ce_HI"], ce_HeII=energy_factor*q["ce_HeII"])
        f["ci_full"] = f["ci_energy_only"]+f["ci_particle_only"]
        f["included_collision_total"] = f["ci_full"]+f["ce_HI"]+f["ce_HeII"]
        F[j] = [f[name] for name in FORCING_NAMES]
        final = r
    if not np.isfinite(Q).all() or not np.isfinite(F).all():
        raise ValueError("NONFINITE_COLLISION_BUDGET")
    closure_max = dict(binding_gradient=float(balance.max()), particle=float(charge_balance.max()),
                       baryon=float(baryon_balance.max()), isotope=float(isotope_balance.max()))
    if max(closure_max.values()) > 1e-13:
        raise ValueError("COLLISION_CONSERVATION_RESIDUAL:" + json.dumps(closure_max))
    E = Q/(nb[:, None]*H[:, None]*EV_J)
    energy = {name: integrate_retained(x, E[:, k], _support_for(name, valid)) for k, name in enumerate(PROCESS_NAMES)}
    forcing = {name: integrate_retained(x, F[:, k], _support_for(name, valid)) for k, name in enumerate(FORCING_NAMES)}
    ci = final["ci_channels"]
    ce = final["ce_channels"]
    arrays = dict(
        x=x, z=a["z"], T_K=T, Y=Y, isotope_scales=a["isotope_scales"],
        H_s=H, nb_m3=nb, ne_m3=ne, gas_particles_per_baryon=eta,
        elapsed_Myr=d["elapsed_Myr"], tau_T=a["raw_state"][:, 61],
        initial_state=a["initial_state"], species_names=np.array(atomic.names),
        coefficient_names=np.array(COEFFICIENT_NAMES), coefficient_units=np.array(["m3/s"]*3+["J m3/s"]*2),
        coefficients_SI=coeff, coefficient_available=np.ones(5, dtype=bool),
        in_published_accuracy_domain=valid, analytic_continuation=~valid, coefficient_underflow_to_zero=underflow,
        ci_available_mask=final["ci_available_mask"], ci_unavailable_mask=final["ci_unavailable_mask"],
        ce_available_mask=final["ce_available_mask"], ce_unavailable_mask=final["ce_unavailable_mask"],
        ci_dY_dt=ci_dY, ci_particle_source_per_baryon_s=particle,
        ci_binding_gradient_W_m3=gradient, ci_binding_gradient_residual_scaled=balance,
        ci_particle_residual_scaled=charge_balance, ci_baryon_residual_scaled=baryon_balance,
        ci_isotope_residual_scaled=isotope_balance,
        ci_channel_isotopes=np.array([r["isotope"] for r in ci]),
        ci_channel_processes=np.array([r["process"] for r in ci]),
        ci_channel_lower_indices=np.array([r["lower_index"] for r in ci]),
        ci_channel_upper_indices=np.array([r["upper_index"] for r in ci]),
        ci_channel_chi_J=np.array([r["chi_J"] for r in ci]),
        ci_channel_rate_threshold_K=np.array([r["rate_threshold_K"] for r in ci]),
        ci_channel_chi_over_rate_threshold_minus_one=np.array([r["chi_over_HG_threshold_minus_one"] for r in ci]),
        ci_channel_event_per_baryon_s=ci_event, ci_channel_event_m3_s=ci_volume,
        ci_channel_kinetic_W_m3=-ci_binding, ci_channel_binding_W_m3=ci_binding,
        ci_channel_event_underflow_to_zero=ci_event_under, ci_channel_volume_underflow_to_zero=ci_volume_under,
        ci_channel_power_underflow_to_zero=ci_power_under, ci_escape_W_m3=np.zeros(n),
        ce_channel_isotopes=np.array([r["isotope"] for r in ce]),
        ce_channel_processes=np.array([r["process"] for r in ce]),
        ce_channel_target_indices=np.array([r["target_index"] for r in ce]),
        ce_channel_cooling_W_m3=ce_power, ce_channel_power_underflow_to_zero=ce_under,
        process_names=np.array(PROCESS_NAMES), Q_W_m3=Q, energy_integrand_eV_baryon_per_x=E,
        energy_cumulative_trapezoid_eV_baryon=cumulative_trapezoid(E, x=x, axis=0, initial=0),
        forcing_names=np.array(FORCING_NAMES), fixed_path_logT_forcing_per_x=F,
        fixed_path_logT_forcing_cumulative_trapezoid=cumulative_trapezoid(F, x=x, axis=0, initial=0),
    )
    for category, names in (("energy", PROCESS_NAMES), ("forcing", FORCING_NAMES)):
        node_masks = [_support_for(name, valid) for name in names]
        arrays[category+"_fit_support_applicable"] = np.array([m is not None for m in node_masks])
        arrays[category+"_supported_intervals"] = np.column_stack(
            [np.ones(n-1, dtype=bool) if m is None else m[:-1]&m[1:] for m in node_masks])
    summary = dict(
        samples=n, z_start=float(a["z"][0]), z_end=float(a["z"][-1]),
        T_min_K=float(T.min()), T_max_K=float(T.max()),
        elapsed_Myr_start=float(d["elapsed_Myr"][0]), elapsed_Myr_end=float(d["elapsed_Myr"][-1]),
        energy_eV_per_baryon=energy, fixed_path_logT_forcing=forcing,
        source_support={name: dict(valid_nodes=int(valid[:, k].sum()), continuation_nodes=int((~valid[:, k]).sum()),
                                  coefficient_underflow_nodes=int(underflow[:, k].sum()))
                        for k, name in enumerate(COEFFICIENT_NAMES)},
        event_and_power_underflow=dict(ci_event=int(ci_event_under.sum()), ci_volume=int(ci_volume_under.sum()),
                                      ci_power=int(ci_power_under.sum()), ce_power=int(ce_under.sum())),
        conservation_max_scaled=closure_max,
        max_abs_fixed_path_forcing={name: float(abs(F[:, k]).max()) for k, name in enumerate(FORCING_NAMES)},
        unavailable=final["unavailable"],
    )
    return arrays, summary


def analyze_case(case_dir, output_dir):
    """Evaluate only supplied, source-verified new saved states; no ODE calls."""
    start, cpu = time.perf_counter(), time.process_time()
    case_dir, output_dir = Path(case_dir).resolve(), Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    _save_json(output_dir / "STARTED.json", dict(
        started_utc=datetime.now(timezone.utc).isoformat(), case_dir=str(case_dir),
        command=sys.argv, scope="new Compton-path omitted H/He CI/CE diagnostics", new_ODE_integrations=0))
    try:
        # Import the frozen driver only to verify identities and output bindings.
        # Neither its solver nor any full-system constructor is invoked here.
        import run_compton as runner
        runtime_id, runtime_files = runner.source_identity()
        identity, source_files = _source_identity(runtime_id)
        receipt_path = case_dir / "RESULT.json"
        receipt_sha = _digest(receipt_path)
        receipt = json.loads(receipt_path.read_text())
        if (receipt["status"] != "COMPLETE" or receipt["source_identity"] != runtime_id
                or receipt["source_files"] != runtime_files or not receipt["gates"]
                or not all(receipt["gates"].values())):
            raise ValueError("NEW_COUPLED_CASE_NOT_SOURCE_BOUND_COMPLETE")
        runner.verify_outputs(case_dir, receipt)
        atomic = AtomicNetwork(uv_cutoff_eV=receipt["specification"]["config"].get("uv_cutoff_eV", 200))
        collision = CollisionalBudget(atomic)
        with np.load(case_dir / "trajectory.npz", allow_pickle=False) as data:
            initial_state = data["initial_state"].copy()
        if hashlib.sha256(initial_state.tobytes()).hexdigest() != receipt["specification"]["initial_state_sha256"]:
            raise ValueError("COUPLED_INITIAL_VECTOR_HASH_CHANGED")
        grids, summaries, grid_states = {}, {}, {}
        for name, (filename, count) in GRID_FILES.items():
            a, d = _read_grid(case_dir / filename, count, atomic, initial_state)
            arrays, summary = _evaluate_grid(a, d, atomic, collision)
            arrays.update(input_trajectory_sha256=np.array(receipt["outputs"][filename]["sha256"]),
                          input_runtime_identity=np.array(runtime_id), collision_source_identity=np.array(identity))
            _save_npz(output_dir / ("collisions_"+name+".npz"), arrays)
            summaries[name] = summary
            grids[name] = dict(filename=filename, **receipt["outputs"][filename])
            grid_states[name] = dict(x=a["x"], raw=a["raw_state"])
        dense, half = grid_states["dense_1025"], grid_states["dense_513"]
        if not np.array_equal(dense["x"][::2], half["x"]):
            raise ValueError("DENSE_GRID_NESTING_CHANGED")
        if not np.allclose(dense["raw"][::2], half["raw"], rtol=3e-14, atol=1e-15):
            raise ValueError("DENSE_SHARED_STATE_MISMATCH")
        if any(g["x"][0] != dense["x"][0] or g["x"][-1] != dense["x"][-1] for g in grid_states.values()):
            raise ValueError("COLLISION_GRID_ENDPOINT_MISMATCH")
        differences = {}
        for other in ("dense_513", "comparison_109"):
            differences["dense_1025_minus_"+other] = {
                category: {name: {rule: summaries["dense_1025"][category][name][rule]-summaries[other][category][name][rule]
                                  for rule in ("trapezoid", "simpson")}
                           for name in names}
                for category, names in (("energy_eV_per_baryon", PROCESS_NAMES), ("fixed_path_logT_forcing", FORCING_NAMES))}
        if _source_identity(runtime_id) != (identity, source_files) or runner.source_identity() != (runtime_id, runtime_files):
            raise ValueError("COLLISION_SOURCE_CHANGED_DURING_ANALYSIS")
        if _digest(receipt_path) != receipt_sha:
            raise ValueError("COUPLED_RECEIPT_CHANGED_DURING_ANALYSIS")
        runner.verify_outputs(case_dir, receipt)
        summary = dict(
            status="COMPLETE_SCOPED_NEW_PATH_COLLISION_BUDGET", label=receipt["label"],
            coupled_runtime_identity=runtime_id, source_identity=identity, source_files=source_files,
            input_receipt_sha256=receipt_sha, input_grids=grids, grids=summaries,
            primary_grid="dense_1025", primary_support_partition_rule="positive-weight trapezoid; both retained interval endpoints in HG97 range",
            energy_eV_per_baryon=summaries["dense_1025"]["energy_eV_per_baryon"],
            fixed_path_logT_forcing=summaries["dense_1025"]["fixed_path_logT_forcing"],
            grid_differences=differences,
            shared_dense_state_max_abs_difference=float(abs(dense["raw"][::2]-half["raw"]).max()),
            elapsed_clock="proper Myr since donor z20; cumulative clock is not reset at the restart",
            scope="CI/CE remain omitted in the ODE; evaluated sources and forcing on the new Compton path are diagnostic, not actual exchange or solved response",
            unavailable=summaries["dense_1025"]["unavailable"],
            source_application=collision.source["application"],
            continuation="all five analytic fits evaluated with explicit allow_extrapolation=True; outside-range nodes have no published accuracy claim",
            support_scope="classification uses retained endpoints only; intervals touching an unsupported endpoint are continuation/boundary; no continuum support guarantee",
            units=dict(energy="eV per baryon", power="W/m3", forcing="delta lnT derivative per x", CI_dY_dt="per baryon per second"),
            new_ODE_integrations=0, old_IVP_reruns=0, physical="HOLD", production="NOT_APPROVED", global_convergence="NOT_RUN", REI_activation=False,
            environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, numerical_threads=1),
            wall_seconds=time.perf_counter()-start, cpu_seconds=time.process_time()-cpu)
        _save_json(output_dir / "SUMMARY.json", summary)
        outputs = {p.name: dict(bytes=p.stat().st_size, sha256=_digest(p))
                   for p in sorted(output_dir.iterdir()) if p.is_file()}
        _save_json(output_dir / "RESULT.json", dict(status="COMPLETE", source_identity=identity,
                    coupled_runtime_identity=runtime_id, input_receipt_sha256=receipt_sha, outputs=outputs,
                    new_ODE_integrations=0, old_IVP_reruns=0))
        return summary
    except Exception as exc:
        _save_json(output_dir / "FAILED.json", dict(status="FAILED", error=repr(exc), traceback=traceback.format_exc(),
                    wall_seconds=time.perf_counter()-start, cpu_seconds=time.process_time()-cpu,
                    preserved_files=sorted(p.name for p in output_dir.iterdir() if p.is_file()), new_ODE_integrations=0))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze_case(args.case_dir, args.output_dir)
    print(json.dumps(dict(status=result["status"], label=result["label"], new_ODE_integrations=0)))

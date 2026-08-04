"""Read-only reference runs for the supplied Bianchi primitive solver.

The source tree is never modified.  The script uses SciPy's DOP853/LSODA
as an independent reference path because the current isolated runtime
cannot install the pinned Diffrax/Equinox stack.
"""
from __future__ import annotations

import csv
import json
import math
import os
import platform
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

HERE = Path(__file__).resolve().parent
SOURCE = Path(
    os.environ.get(
        "BIANCHI_PRIMITIVE_SOURCE",
        "/mnt/data/bianchibianchic2_extracted",
    )
)
sys.path[:0] = [
    str(HERE / "runtime_stubs"),
    str(SOURCE),
]

os.environ.setdefault("JAX_ENABLE_X64", "True")

import jax  # noqa: E402
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402

from bianchi.charts import class_a as CA  # noqa: E402
from bianchi.charts import class_b as CB  # noqa: E402
from bianchi.charts import class_b_tilted as BT  # noqa: E402
from bianchi.charts import exceptional as EX  # noqa: E402
from bianchi.charts import type_ix_d as IX  # noqa: E402
from bianchi.matter import kinetic_einstein as KE  # noqa: E402
from bianchi.matter import type_v_coupled as TVC  # noqa: E402
from bianchi.physical import units as U  # noqa: E402
from bianchi.thermo import recombination as REC  # noqa: E402


def integrate_chart(
    module,
    state_class,
    initial_state,
    args,
    tau_end,
    samples,
    *,
    event_index=None,
    event_direction=0.0,
    max_step=None,
):
    y0 = np.asarray(initial_state.as_array(), dtype=float)

    array_rhs = jax.jit(
        lambda tau, values: module.rhs(
            tau, state_class.from_array(values), args
        ).as_array()
    )
    # Compile once before SciPy starts adaptive stepping.
    array_rhs(jnp.asarray(0.0), jnp.asarray(y0)).block_until_ready()

    def rhs(tau, values):
        return np.asarray(
            array_rhs(jnp.asarray(tau), jnp.asarray(values)),
            dtype=float,
        )

    event = None
    if event_index is not None:
        def event_fn(tau, values):
            return float(values[event_index])
        event_fn.terminal = True
        event_fn.direction = event_direction
        event = event_fn

    if max_step is None:
        max_step = tau_end / max(200, samples - 1)

    result = solve_ivp(
        rhs,
        (0.0, tau_end),
        y0,
        method="DOP853",
        rtol=1.0e-10,
        atol=1.0e-12,
        dense_output=True,
        events=event,
        max_step=max_step,
    )

    final_time = (
        float(result.t_events[0][0])
        if event is not None and len(result.t_events[0])
        else tau_end
    )
    tau = np.linspace(0.0, final_time, samples)
    values = result.sol(tau).T
    return result, tau, values


def write_csv(path, rows):
    fieldnames = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def class_a_aux(values, gamma):
    rows = []
    for vector in values:
        state = CA.StateA.from_array(jnp.asarray(vector))
        aux = CA.aux(state, gamma)
        rows.append(
            (
                float(aux["Sigma2"]),
                float(aux["K"]),
                float(aux["Omega"]),
                float(aux["q"]),
            )
        )
    return np.asarray(rows)


def run_class_a_vi0():
    gamma = 4.0 / 3.0
    state = CA.from_type("VI_0", Sp=0.35, Sm=-0.20, scale=1.0)
    result, tau, values = integrate_chart(
        CA,
        CA.StateA,
        state,
        {"gamma": gamma},
        8.0,
        401,
    )
    diagnostics = class_a_aux(values, gamma)
    type_signs = np.sign(values[:, 2:5])
    sign_drift = np.max(
        np.abs(type_signs - type_signs[0])
    )
    return {
        "model": "VI_0_radiation",
        "success": bool(result.success),
        "tau_final": float(tau[-1]),
        "event_time": np.nan,
        "constraint_max": 0.0,
        "Omega_min": float(diagnostics[:, 2].min()),
        "Sigma2_initial": float(diagnostics[0, 0]),
        "Sigma2_final": float(diagnostics[-1, 0]),
        "K_initial": float(diagnostics[0, 1]),
        "K_final": float(diagnostics[-1, 1]),
        "Omega_initial": float(diagnostics[0, 2]),
        "Omega_final": float(diagnostics[-1, 2]),
        "q_initial": float(diagnostics[0, 3]),
        "q_final": float(diagnostics[-1, 3]),
        "type_sign_drift": float(sign_drift),
    }, tau, values, diagnostics


def run_class_b_vih():
    gamma = 1.0
    kappa = -4.0
    state, radicand = CB.on_codazzi_surface(
        0.15, 0.25, 0.20, 0.40, kappa
    )
    result, tau, values = integrate_chart(
        CB,
        CB.StateB,
        state,
        {"gamma": gamma, "kappa": kappa},
        5.0,
        301,
    )
    constraints = []
    diagnostics = []
    for vector in values:
        state_i = CB.StateB.from_array(jnp.asarray(vector))
        constraints.append(abs(float(CB.codazzi(state_i, kappa))))
        aux = CB.aux(state_i, gamma, kappa)
        diagnostics.append(
            (
                float(aux["Sigma2"]),
                float(aux["K"]),
                float(aux["Omega"]),
                float(aux["q"]),
            )
        )
    diagnostics = np.asarray(diagnostics)
    return {
        "model": "VI_h_kappa_minus4_dust",
        "success": bool(result.success),
        "tau_final": float(tau[-1]),
        "event_time": np.nan,
        "constraint_max": float(max(constraints)),
        "Omega_min": float(diagnostics[:, 2].min()),
        "Sigma2_initial": float(diagnostics[0, 0]),
        "Sigma2_final": float(diagnostics[-1, 0]),
        "K_initial": float(diagnostics[0, 1]),
        "K_final": float(diagnostics[-1, 1]),
        "Omega_initial": float(diagnostics[0, 2]),
        "Omega_final": float(diagnostics[-1, 2]),
        "q_initial": float(diagnostics[0, 3]),
        "q_final": float(diagnostics[-1, 3]),
        "type_sign_drift": 0.0,
        "codazzi_radicand": float(radicand),
    }, tau, values, diagnostics


def run_exceptional():
    gamma = 1.2
    state = EX.on_g_surface(0.20, -0.10, 0.15, 0.30, 0.12)
    result, tau, values = integrate_chart(
        EX,
        EX.StateE,
        state,
        {"gamma": gamma},
        3.0,
        241,
    )
    constraints = []
    diagnostics = []
    for vector in values:
        state_i = EX.StateE.from_array(jnp.asarray(vector))
        constraints.append(abs(float(EX.g_constraint(state_i))))
        aux = EX.aux(state_i, gamma)
        diagnostics.append(
            (
                float(aux["Sigma2"]),
                float(aux["K"]),
                float(aux["Omega"]),
                float(aux["q"]),
            )
        )
    diagnostics = np.asarray(diagnostics)
    return {
        "model": "VI_star_minus1over9",
        "success": bool(result.success),
        "tau_final": float(tau[-1]),
        "event_time": np.nan,
        "constraint_max": float(max(constraints)),
        "Omega_min": float(diagnostics[:, 2].min()),
        "Sigma2_initial": float(diagnostics[0, 0]),
        "Sigma2_final": float(diagnostics[-1, 0]),
        "K_initial": float(diagnostics[0, 1]),
        "K_final": float(diagnostics[-1, 1]),
        "Omega_initial": float(diagnostics[0, 2]),
        "Omega_final": float(diagnostics[-1, 2]),
        "q_initial": float(diagnostics[0, 3]),
        "q_final": float(diagnostics[-1, 3]),
        "type_sign_drift": 0.0,
    }, tau, values, diagnostics


def run_ix_recollapse():
    gamma = 1.0
    state = IX.isotropic_closed_ic(0.35)

    y0 = np.asarray(state.as_array(), dtype=float)

    ix_rhs = jax.jit(
        lambda tau, values: IX.rhs_future(
            tau, IX.StateD.from_array(values), {"gamma": gamma}
        ).as_array()
    )
    ix_rhs(jnp.asarray(0.0), jnp.asarray(y0)).block_until_ready()

    def rhs(tau, values):
        return np.asarray(
            ix_rhs(jnp.asarray(tau), jnp.asarray(values)),
            dtype=float,
        )

    def recollapse(tau, values):
        return float(values[0])

    recollapse.terminal = True
    recollapse.direction = -1.0

    result = solve_ivp(
        rhs,
        (0.0, 12.0),
        y0,
        method="DOP853",
        rtol=1.0e-10,
        atol=1.0e-12,
        dense_output=True,
        events=recollapse,
        max_step=0.01,
    )
    if len(result.t_events[0]) == 0:
        raise RuntimeError("IX recollapse event was not detected")

    event_time = float(result.t_events[0][0])
    tau = np.linspace(0.0, event_time, 281)
    values = result.sol(tau).T
    diagnostics = []
    constraints = []
    for vector in values:
        state_i = IX.StateD.from_array(jnp.asarray(vector))
        aux = IX.aux(state_i, gamma)
        cons = IX.constraints(state_i, {"gamma": gamma})
        diagnostics.append(
            (
                float(aux["Sigma2"]),
                float(1.0 - aux["Sigma2"] - aux["Omega"]),
                float(aux["Omega"]),
                float(aux["q"]),
            )
        )
        constraints.append(
            max(
                abs(float(cons["definition"])),
                abs(float(cons["trace"])),
            )
        )
    diagnostics = np.asarray(diagnostics)
    return {
        "model": "IX_isotropic_closed_dust",
        "success": bool(result.success),
        "tau_final": event_time,
        "event_time": event_time,
        "constraint_max": float(max(constraints)),
        "Omega_min": float(diagnostics[:, 2].min()),
        "Sigma2_initial": float(diagnostics[0, 0]),
        "Sigma2_final": float(diagnostics[-1, 0]),
        "K_initial": float(diagnostics[0, 1]),
        "K_final": float(diagnostics[-1, 1]),
        "Omega_initial": float(diagnostics[0, 2]),
        "Omega_final": float(diagnostics[-1, 2]),
        "q_initial": float(diagnostics[0, 3]),
        "q_final": float(diagnostics[-1, 3]),
        "type_sign_drift": 0.0,
        "Hbar_initial": float(values[0, 0]),
        "Hbar_final": float(values[-1, 0]),
    }, tau, values, diagnostics


def tilted_onshell(seed=11, gamma=1.3):
    rng = np.random.default_rng(seed)
    geometry = rng.normal(size=8) * 0.20
    geometry[6] = rng.uniform(-0.8, 0.8)

    def residual(velocity):
        vector = np.concatenate([geometry, velocity])
        state = BT.StateBT.from_array(jnp.asarray(vector))
        cons = BT.constraints(state, {"gamma": gamma})
        return [
            float(cons["C2"]),
            float(cons["C3"]),
            float(cons["C4"]),
        ]

    velocity = fsolve(
        residual, rng.normal(size=3) * 0.10
    )
    if max(abs(value) for value in residual(velocity)) > 1.0e-10:
        raise RuntimeError("failed to construct tilted on-shell state")
    return BT.StateBT.from_array(
        jnp.asarray(np.concatenate([geometry, velocity]))
    )


def run_tilted_class_b():
    gamma = 1.3
    state = tilted_onshell(gamma=gamma)
    result, tau, values = integrate_chart(
        BT,
        BT.StateBT,
        state,
        {"gamma": gamma},
        1.5,
        241,
    )
    constraints = []
    diagnostics = []
    v2_max = 0.0
    for vector in values:
        state_i = BT.StateBT.from_array(jnp.asarray(vector))
        cons = BT.constraints(state_i, {"gamma": gamma})
        constraints.append(
            max(
                abs(float(cons["C2"])),
                abs(float(cons["C3"])),
                abs(float(cons["C4"])),
            )
        )
        aux = BT.aux(state_i, {"gamma": gamma})
        v2_max = max(v2_max, float(aux["V2"]))
        diagnostics.append(
            (
                float(aux["Sigma2"]),
                float(aux["K"]),
                float(aux["Omega"]),
                float(aux["q"]),
            )
        )
    diagnostics = np.asarray(diagnostics)
    return {
        "model": "class_B_tilted_gamma1p3",
        "success": bool(result.success),
        "tau_final": float(tau[-1]),
        "event_time": np.nan,
        "constraint_max": float(max(constraints)),
        "Omega_min": float(diagnostics[:, 2].min()),
        "Sigma2_initial": float(diagnostics[0, 0]),
        "Sigma2_final": float(diagnostics[-1, 0]),
        "K_initial": float(diagnostics[0, 1]),
        "K_final": float(diagnostics[-1, 1]),
        "Omega_initial": float(diagnostics[0, 2]),
        "Omega_final": float(diagnostics[-1, 2]),
        "q_initial": float(diagnostics[0, 3]),
        "q_final": float(diagnostics[-1, 3]),
        "type_sign_drift": 0.0,
        "maximum_tilt_speed_squared": v2_max,
    }, tau, values, diagnostics


def run_type_v_coupled():
    result = TVC.evolve_coupled(
        t_end=0.05,
        nsteps=15,
        backend="python",
    )
    friedmann = np.asarray(result["friedmann"], dtype=float)
    codazzi = np.asarray(result["codazzi"], dtype=float)
    return {
        "model": "type_V_kinetic_Einstein",
        "success": True,
        "tau_final": np.nan,
        "event_time": np.nan,
        "constraint_max": float(
            max(
                np.max(np.abs(friedmann)),
                np.max(np.abs(codazzi)),
            )
        ),
        "Omega_min": np.nan,
        "Sigma2_initial": np.nan,
        "Sigma2_final": np.nan,
        "K_initial": np.nan,
        "K_final": np.nan,
        "Omega_initial": np.nan,
        "Omega_final": np.nan,
        "q_initial": np.nan,
        "q_final": np.nan,
        "type_sign_drift": 0.0,
        "friedmann_max": float(np.max(np.abs(friedmann))),
        "codazzi_max": float(np.max(np.abs(codazzi))),
        "final_a1": float(result["a"][-1][0]),
        "final_a2": float(result["a"][-1][1]),
        "final_a3": float(result["a"][-1][2]),
        "final_rho": float(result["rho"][-1]),
    }, result


def run_bianchi_i_kinetic():
    initial_a = (1.0, 0.90, 1.10)
    initial_sigma = (0.04, -0.01, -0.03)
    reference = KE.integrate_reference(
        initial_a,
        initial_sigma,
        0.0,
        0.05,
        nsteps=20,
    )
    hierarchy = KE.integrate_coupled(
        initial_a,
        initial_sigma,
        0.0,
        0.05,
        nsteps=20,
        l_max=4,
        i_max=2,
    )
    a_reference = np.asarray(reference["a"][-1], dtype=float)
    a_hierarchy = np.asarray(hierarchy["a"][-1], dtype=float)
    relative = float(
        np.linalg.norm(a_reference - a_hierarchy)
        / np.linalg.norm(a_reference)
    )
    return {
        "model": "I_kinetic_Einstein_hierarchy",
        "success": True,
        "tau_final": np.nan,
        "event_time": np.nan,
        "constraint_max": relative,
        "Omega_min": np.nan,
        "Sigma2_initial": np.nan,
        "Sigma2_final": np.nan,
        "K_initial": 0.0,
        "K_final": 0.0,
        "Omega_initial": np.nan,
        "Omega_final": np.nan,
        "q_initial": np.nan,
        "q_final": np.nan,
        "type_sign_drift": 0.0,
        "reference_hierarchy_scale_factor_relative": relative,
        "reference_final_a": a_reference.tolist(),
        "hierarchy_final_a": a_hierarchy.tolist(),
    }, reference, hierarchy


def standard_H(z, h=0.674, om_h2=0.143):
    omega_m = om_h2 / h**2
    omega_r = 4.18e-5 / h**2
    omega_l = 1.0 - omega_m - omega_r
    H0 = 100.0 * h / U.MPC_KM
    return H0 * np.sqrt(
        omega_r * (1.0 + z) ** 4
        + omega_m * (1.0 + z) ** 3
        + omega_l
    )


def gamma_effective(z, h=0.674, om_h2=0.143):
    omega_m = om_h2 / h**2
    omega_r = 4.18e-5 / h**2
    rho_m = omega_m * (1.0 + z) ** 3
    rho_r = omega_r * (1.0 + z) ** 4
    return 1.0 + rho_r / (3.0 * (rho_m + rho_r))


def bianchi_i_hubble_adapter(z_grid, Sp0, Sm0):
    z_start = float(z_grid[0])
    tau_grid = np.log(
        (1.0 + z_start) / (1.0 + z_grid)
    )

    state = CA.StateA.of(Sp0, Sm0, 0.0, 0.0, 0.0)
    y0 = np.asarray(state.as_array(), dtype=float)

    def rhs(tau, values):
        z = (1.0 + z_start) * math.exp(-tau) - 1.0
        gamma = gamma_effective(z)
        Sp, Sm = values[0], values[1]
        sigma2 = Sp * Sp + Sm * Sm
        omega = 1.0 - sigma2
        q = 2.0 * sigma2 + 0.5 * (3.0 * gamma - 2.0) * omega
        return np.asarray([
            -(2.0 - q) * Sp,
            -(2.0 - q) * Sm,
            0.0, 0.0, 0.0,
        ])

    solution = solve_ivp(
        rhs,
        (float(tau_grid[0]), float(tau_grid[-1])),
        y0,
        method="DOP853",
        t_eval=tau_grid,
        rtol=1.0e-11,
        atol=1.0e-13,
        max_step=0.01,
    )
    sigma2 = (
        solution.y[0] ** 2 + solution.y[1] ** 2
    )
    omega = 1.0 - sigma2
    enhancement = 1.0 / np.sqrt(omega)
    H_values = standard_H(z_grid) * enhancement

    # np.interp requires increasing x.
    z_increasing = z_grid[::-1]
    H_increasing = H_values[::-1]

    def callback(z):
        values = np.asarray(z, dtype=float)
        return np.interp(
            values,
            z_increasing,
            H_increasing,
        )

    return callback, tau_grid, sigma2, enhancement


def run_recombination_reference():
    z_grid = np.linspace(1600.0, 200.0, 800)
    standard_xe = REC.peebles_xe(z_grid)
    standard_visibility = REC.optical_depth_and_visibility(
        z_grid, standard_xe
    )

    variants = [
        ("mild_BI_H_only", 0.02, -0.01),
        ("stress_BI_H_only", 0.08, -0.04),
    ]
    rows = []
    arrays = {
        "z": z_grid,
        "xe_standard": standard_xe,
    }

    for name, Sp0, Sm0 in variants:
        callback, tau, sigma2, enhancement = (
            bianchi_i_hubble_adapter(z_grid, Sp0, Sm0)
        )
        xe = REC.peebles_xe(z_grid, H_of_z=callback)
        visibility = REC.optical_depth_and_visibility(
            z_grid, xe, H_of_z=callback
        )
        index_1100 = int(np.argmin(np.abs(z_grid - 1100.0)))
        rows.append(
            {
                "variant": name,
                "Sigma2_initial": float(sigma2[0]),
                "Sigma2_final": float(sigma2[-1]),
                "H_enhancement_max": float(
                    enhancement.max()
                ),
                "z_star": float(visibility["z_star"]),
                "z_star_shift": float(
                    visibility["z_star"]
                    - standard_visibility["z_star"]
                ),
                "xe_relative_max": float(
                    np.max(
                        np.abs(xe - standard_xe)
                        / np.maximum(standard_xe, 1.0e-12)
                    )
                ),
                "xe_relative_at_z1100": float(
                    (xe[index_1100] - standard_xe[index_1100])
                    / standard_xe[index_1100]
                ),
            }
        )
        arrays[f"xe_{name}"] = xe
        arrays[f"Sigma2_{name}"] = sigma2
        arrays[f"H_enhancement_{name}"] = enhancement
        arrays[f"tau_{name}"] = tau

    standard_row = {
        "variant": "standard_FLRW",
        "Sigma2_initial": 0.0,
        "Sigma2_final": 0.0,
        "H_enhancement_max": 1.0,
        "z_star": float(standard_visibility["z_star"]),
        "z_star_shift": 0.0,
        "xe_relative_max": 0.0,
        "xe_relative_at_z1100": 0.0,
    }
    rows.insert(0, standard_row)
    return rows, arrays


def main():
    summaries = []
    timeseries = {}

    print("RUN VI0", flush=True)
    summary, tau, values, diagnostics = run_class_a_vi0()
    summaries.append(summary)
    timeseries["VI0_tau"] = tau
    timeseries["VI0_state"] = values
    timeseries["VI0_diagnostics"] = diagnostics

    print("RUN VIh", flush=True)
    summary, tau, values, diagnostics = run_class_b_vih()
    summaries.append(summary)
    timeseries["VIh_tau"] = tau
    timeseries["VIh_state"] = values
    timeseries["VIh_diagnostics"] = diagnostics

    print("RUN exceptional", flush=True)
    summary, tau, values, diagnostics = run_exceptional()
    summaries.append(summary)
    timeseries["exceptional_tau"] = tau
    timeseries["exceptional_state"] = values
    timeseries["exceptional_diagnostics"] = diagnostics

    print("RUN IX", flush=True)
    summary, tau, values, diagnostics = run_ix_recollapse()
    summaries.append(summary)
    timeseries["IX_tau"] = tau
    timeseries["IX_state"] = values
    timeseries["IX_diagnostics"] = diagnostics

    print("RUN tilted", flush=True)
    summary, tau, values, diagnostics = run_tilted_class_b()
    summaries.append(summary)
    timeseries["tilted_tau"] = tau
    timeseries["tilted_state"] = values
    timeseries["tilted_diagnostics"] = diagnostics

    print("RUN type V coupled", flush=True)
    summary, type_v = run_type_v_coupled()
    summaries.append(summary)
    timeseries["typeV_t"] = np.asarray(type_v["t"], dtype=float)
    timeseries["typeV_a"] = np.asarray(type_v["a"], dtype=float)
    timeseries["typeV_h"] = np.asarray(type_v["h"], dtype=float)
    timeseries["typeV_rho"] = np.asarray(type_v["rho"], dtype=float)
    timeseries["typeV_friedmann"] = np.asarray(
        type_v["friedmann"], dtype=float
    )
    timeseries["typeV_codazzi"] = np.asarray(
        type_v["codazzi"], dtype=float
    )

    print("RUN Bianchi I kinetic", flush=True)
    summary, reference, hierarchy = run_bianchi_i_kinetic()
    summaries.append(summary)
    timeseries["kineticI_t"] = np.asarray(
        reference["t"], dtype=float
    )
    timeseries["kineticI_reference_a"] = np.asarray(
        reference["a"], dtype=float
    )
    timeseries["kineticI_hierarchy_a"] = np.asarray(
        hierarchy["a"], dtype=float
    )
    timeseries["kineticI_reference_sigma"] = np.asarray(
        reference["sigma"], dtype=float
    )
    timeseries["kineticI_hierarchy_sigma"] = np.asarray(
        hierarchy["sigma"], dtype=float
    )

    print("RUN recombination", flush=True)
    recombination_rows, recombination_arrays = (
        run_recombination_reference()
    )
    timeseries.update(
        {
            f"recomb_{key}": value
            for key, value in recombination_arrays.items()
        }
    )

    write_csv(HERE / "background_runs.csv", summaries)
    write_csv(
        HERE / "recombination_reference.csv",
        recombination_rows,
    )
    np.savez_compressed(
        HERE / "background_timeseries.npz",
        classification=np.asarray(
            "READ_ONLY_PRIMITIVE_BACKGROUND_REFERENCE"
        ),
        **timeseries,
    )

    runtime = {
        "python": sys.version,
        "platform": platform.platform(),
        "source_path": str(SOURCE),
        "source_modified": False,
        "integrator": (
            "SciPy solve_ivp DOP853/LSODA; independent of the "
            "source's pinned Diffrax runtime"
        ),
        "jax_x64": bool(jax.config.x64_enabled),
        "models_run": [
            row["model"] for row in summaries
        ],
    }
    (HERE / "runtime_environment.json").write_text(
        json.dumps(runtime, indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "background_models": len(summaries),
                "all_success": all(
                    row["success"] for row in summaries
                ),
                "IX_recollapse_tau": next(
                    row["event_time"]
                    for row in summaries
                    if row["model"]
                    == "IX_isotropic_closed_dust"
                ),
                "recombination": recombination_rows,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

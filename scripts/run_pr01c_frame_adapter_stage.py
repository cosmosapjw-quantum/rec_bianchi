#!/usr/bin/env python3
"""PR-01C: primitive Bianchi BackgroundSnapshot and frame-adapter closure.

The script extracts the user-supplied primitive solver read-only, evolves
three representative homogeneous backgrounds, maps them to the stable
BackgroundSnapshot interface, and verifies exact finite-tilt frequency/
direction characteristics plus event-localized red/blue boundary flux.
"""
from __future__ import annotations

import csv
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Any
import zipfile

import numpy as np
from scipy.constants import c, k, physical_constants
from scipy.integrate import quad, solve_ivp

ROOT = Path(__file__).resolve().parents[1]
SRC_TARBALL = ROOT / "archive" / "inputs" / "bianchibianchic2.tar.gz"
ARTIFACT_NAME = "Full_Bianchi_HyRec_PR01C_background_frame_adapter_v0_48"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "pr01c_background_snapshots_v048.npz"

sys.path.insert(0, str(ROOT / "src"))

from full_bianchi_hyrec.background.adapters import (  # noqa: E402
    class_a_snapshot,
    exceptional_snapshot,
    tilted_class_b_snapshot,
)
from full_bianchi_hyrec.background.branch_events import (  # noqa: E402
    boundary_ledger,
    piecewise_linear_roots,
)
from full_bianchi_hyrec.background.characteristics import (  # noqa: E402
    aberrate_direction,
    doppler_coordinate_speed,
    doppler_factor,
    hydrogen_frame_characteristic,
    normal_frame_characteristic,
)




def json_default(value: Any):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"not JSON serializable: {type(value)!r}")

def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0].keys()), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def install_equinox_stub(directory: Path) -> None:
    text = '''from __future__ import annotations
from dataclasses import dataclass, field as dc_field, fields

def field(*, converter=None, **kwargs):
    metadata=dict(kwargs.pop("metadata", {}) or {})
    metadata["converter"]=converter
    return dc_field(metadata=metadata, **kwargs)

class Module:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        dataclass(eq=False, repr=True)(cls)
    def __post_init__(self):
        for item in fields(self):
            converter=item.metadata.get("converter")
            if converter is not None:
                object.__setattr__(self,item.name,converter(getattr(self,item.name)))

def filter_jit(fn=None, **kwargs):
    return (lambda function:function) if fn is None else fn
'''
    (directory / "equinox.py").write_text(text, encoding="utf-8")


def lebedev_26() -> tuple[np.ndarray, np.ndarray]:
    directions: list[np.ndarray] = []
    weights: list[float] = []
    for axis in range(3):
        for sign in (-1.0, 1.0):
            vector = np.zeros(3)
            vector[axis] = sign
            directions.append(vector)
            weights.append(1.0 / 21.0)
    for zero_axis in range(3):
        indices = [value for value in range(3) if value != zero_axis]
        for sign_1 in (-1.0, 1.0):
            for sign_2 in (-1.0, 1.0):
                vector = np.zeros(3)
                vector[indices[0]] = sign_1 / np.sqrt(2.0)
                vector[indices[1]] = sign_2 / np.sqrt(2.0)
                directions.append(vector)
                weights.append(4.0 / 105.0)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                directions.append(np.array([sx, sy, sz]) / np.sqrt(3.0))
                weights.append(9.0 / 280.0)
    return np.asarray(directions), np.asarray(weights)


def five_point(function, step: float = 2.0e-5):
    return (
        function(-2.0 * step)
        - 8.0 * function(-step)
        + 8.0 * function(step)
        - function(2.0 * step)
    ) / (12.0 * step)


def import_primitive(source: Path, stub: Path):
    os.environ.setdefault("JAX_ENABLE_X64", "True")
    sys.path[:0] = [str(stub), str(source)]
    import jax

    jax.config.update("jax_enable_x64", True)
    import jax.numpy as jnp
    from bianchi.charts import class_a as CA
    from bianchi.charts import class_b_tilted as BT
    from bianchi.charts import exceptional as EX

    return jax, jnp, CA, BT, EX


def compiled_chart(jax, jnp, module, state_class, args, kind, constraint_names):
    if kind in {"class_a", "exceptional"}:
        rhs = jax.jit(
            lambda value: module.rhs(
                0.0, state_class.from_array(value), args
            ).as_array()
        )
        q = jax.jit(
            lambda value: module.aux(
                state_class.from_array(value), args["gamma"]
            )["q"]
        )
        omega = jax.jit(
            lambda value: module.aux(
                state_class.from_array(value), args["gamma"]
            )["Omega"]
        )
    else:
        rhs = jax.jit(
            lambda value: module.rhs(
                0.0, state_class.from_array(value), args
            ).as_array()
        )
        q = jax.jit(
            lambda value: module.aux(
                state_class.from_array(value), args
            )["q"]
        )
        omega = jax.jit(
            lambda value: module.aux(
                state_class.from_array(value), args
            )["Omega"]
        )
    constraints = jax.jit(
        lambda value: jnp.stack(
            [
                module.constraints(state_class.from_array(value), args)[name]
                for name in constraint_names
            ]
        )
    )
    return rhs, q, omega, constraints


def integrate_model(jnp, spec: dict[str, Any]) -> dict[str, Any]:
    initial = np.asarray(spec["initial_state"], dtype=float)
    rhs_jit = spec["rhs_jit"]
    q_jit = spec["q_jit"]
    n_state = len(initial)
    H0 = float(spec["H0_s_inv"])
    y0 = np.concatenate([initial, [math.log(H0), 0.0]])

    # Compile before scipy enters the callback loop.
    rhs_jit(jnp.asarray(initial)).block_until_ready()
    q_jit(jnp.asarray(initial)).block_until_ready()

    def rhs_augmented(tau, values):
        state = jnp.asarray(values[:n_state])
        derivative = np.asarray(rhs_jit(state), dtype=float)
        q_value = float(q_jit(state))
        H = math.exp(float(values[n_state]))
        return np.concatenate(
            [derivative, [-(1.0 + q_value), 1.0 / H]]
        )

    tau = np.linspace(0.0, spec["tau_end"], spec["samples"])
    solution = solve_ivp(
        rhs_augmented,
        (0.0, spec["tau_end"]),
        y0,
        method="DOP853",
        t_eval=tau,
        rtol=2.0e-10,
        atol=2.0e-12,
        max_step=0.025,
    )
    if not solution.success:
        raise RuntimeError(f"{spec['model']} integration failed: {solution.message}")
    return {
        "tau": solution.t,
        "state": solution.y[:n_state].T,
        "H": np.exp(solution.y[n_state]),
        "time": solution.y[n_state + 1],
        "success": solution.success,
    }


def snapshot_from_spec(jnp, spec, tau, state, H, cosmic_time):
    derivative = np.asarray(spec["rhs_jit"](jnp.asarray(state)), dtype=float)
    q_value = float(spec["q_jit"](jnp.asarray(state)))
    constraint_values = np.asarray(
        spec["constraint_jit"](jnp.asarray(state)), dtype=float
    )
    residuals = {
        name: float(value)
        for name, value in zip(spec["constraint_names"], constraint_values)
    }
    if spec["kind"] == "class_a":
        snapshot = class_a_snapshot(
            state,
            q=q_value,
            H_s_inv=H,
            tau=tau,
            cosmic_time_s=cosmic_time,
            bianchi_type=spec["bianchi_type"],
            constraint_residuals=residuals,
        )
    elif spec["kind"] == "tilted_class_b":
        snapshot = tilted_class_b_snapshot(
            state,
            derivative,
            q=q_value,
            H_s_inv=H,
            tau=tau,
            cosmic_time_s=cosmic_time,
            bianchi_type=spec["bianchi_type"],
            constraint_residuals=residuals,
        )
    else:
        snapshot = exceptional_snapshot(
            state,
            q=q_value,
            H_s_inv=H,
            tau=tau,
            cosmic_time_s=cosmic_time,
            constraint_residuals=residuals,
        )
    return snapshot, derivative, q_value, residuals


def frame_direct_residual(snapshot, direction):
    normal = normal_frame_characteristic(snapshot, direction)
    hydrogen = hydrogen_frame_characteristic(snapshot, normal)
    H = snapshot.H_s_inv
    beta_tau = snapshot.D0_beta_H_s_inv / H
    direction_tau = normal.D0_direction_normal_s_inv / H
    R_tau = normal.R_normal_s_inv / H

    direct_direction_tau = five_point(
        lambda delta_tau: aberrate_direction(
            snapshot.beta_H + delta_tau * beta_tau,
            (
                normal.direction_normal + delta_tau * direction_tau
            )
            / np.linalg.norm(
                normal.direction_normal + delta_tau * direction_tau
            ),
        )
    )
    direct_log_frequency_tau = five_point(
        lambda delta_tau: (
            R_tau * delta_tau
            + math.log(
                doppler_factor(
                    snapshot.beta_H + delta_tau * beta_tau,
                    (
                        normal.direction_normal + delta_tau * direction_tau
                    )
                    / np.linalg.norm(
                        normal.direction_normal + delta_tau * direction_tau
                    ),
                )
            )
        )
    )
    direction_residual = np.linalg.norm(
        direct_direction_tau
        - hydrogen.D0_direction_hydrogen_s_inv / H
    )
    frequency_residual = abs(
        direct_log_frequency_tau - hydrogen.R_hydrogen_s_inv / H
    )
    return frequency_residual, direction_residual


def quad_boundary_flux(times, speed, interior, exterior, boundary):
    """Independent segment-local quadrature of a piecewise-linear flux.

    The physical time coordinate can be O(10^15 s).  Integrating each
    segment on u in [0,1] avoids the roundoff floor produced by a global
    quadrature over that large coordinate and exposes every sign change.
    """
    times = np.asarray(times, dtype=float)
    speed = np.asarray(speed, dtype=float)
    total = 0.0

    for left_t, right_t, left_a, right_a in zip(
        times[:-1], times[1:], speed[:-1], speed[1:]
    ):
        duration = float(right_t - left_t)

        def integrand(unit_time):
            value = (1.0 - unit_time) * left_a + unit_time * right_a
            if boundary == "red":
                return (
                    max(-value, 0.0) * interior
                    - max(value, 0.0) * exterior
                )
            return (
                max(value, 0.0) * interior
                - max(-value, 0.0) * exterior
            )

        points = None
        if left_a * right_a < 0.0:
            points = [float(-left_a / (right_a - left_a))]
        segment = quad(
            integrand,
            0.0,
            1.0,
            points=points,
            epsabs=1.0e-14,
            epsrel=1.0e-13,
            limit=40,
        )[0]
        total += duration * segment

    return total


def naive_fixed_branch(times, speed, interior, exterior, boundary):
    midpoint = 0.5 * (times[0] + times[-1])
    sign_value = float(np.interp(midpoint, times, speed))
    integral = float(np.trapezoid(speed, times))
    if boundary == "red":
        return -integral * (interior if sign_value < 0.0 else exterior)
    return integral * (interior if sign_value > 0.0 else exterior)


def main() -> None:
    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)

    tar_sha = hashlib.sha256(SRC_TARBALL.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="pr01c-primitive-") as temporary:
        temporary_path = Path(temporary)
        source = temporary_path / "primitive"
        source.mkdir()
        with tarfile.open(SRC_TARBALL, "r:gz") as archive:
            archive.extractall(source, filter="data")
        stub = temporary_path / "stub"
        stub.mkdir()
        install_equinox_stub(stub)
        jax, jnp, CA, BT, EX = import_primitive(source, stub)

        gamma_class_b = 1.3
        class_b_initial = np.array(
            [
                0.047263345448383266,
                -0.13068711037018685,
                -0.10326588584797336,
                -0.6103668456599639,
                0.4499268456802255,
                0.4360414680093072,
                -0.33754594814094285,
                0.27345164668191535,
                0.5843727596613002,
                -0.02720216873057657,
                -0.25294437479734344,
            ]
        )
        N = class_b_initial[5]
        lam = class_b_initial[6]
        A = class_b_initial[7]
        h_group = -A**2 / (3.0 * (1.0 - lam**2) * N**2)

        Sp, Sm, S2, Nm, A_exc = 0.65, -0.05, 0.1, 0.35, 0.08
        Sx = (Sp + np.sqrt(3.0) * Sm) * A_exc / Nm
        exceptional_initial = np.array([Sp, Sm, S2, Sx, Nm, A_exc])

        raw_specs = [
            {
                "model": "Bianchi_II_large_shear",
                "kind": "class_a",
                "module": CA,
                "state_class": CA.StateA,
                "initial_state": np.array([0.7, 0.08, 0.55, 0.0, 0.0]),
                "args": {"gamma": 4.0 / 3.0},
                "constraint_names": ["gauss", "Omega_negative"],
                "bianchi_type": "II",
                "tau_end": 2.5,
                "samples": 241,
                "H0_s_inv": 5.0e-14,
            },
            {
                "model": "Bianchi_VI_h_tilted_large_shear",
                "kind": "tilted_class_b",
                "module": BT,
                "state_class": BT.StateBT,
                "initial_state": class_b_initial,
                "args": {"gamma": gamma_class_b, "h": h_group},
                "constraint_names": ["C1", "C2", "C3", "C4", "C5"],
                "bianchi_type": "VI_h",
                "tau_end": 1.5,
                "samples": 241,
                "H0_s_inv": 5.0e-14,
            },
            {
                "model": "Bianchi_VI_minus_1_over_9_exceptional",
                "kind": "exceptional",
                "module": EX,
                "state_class": EX.StateE,
                "initial_state": exceptional_initial,
                "args": {"gamma": 1.2},
                "constraint_names": ["g", "Omega_negative"],
                "bianchi_type": "VI_-1/9",
                "tau_end": 2.0,
                "samples": 241,
                "H0_s_inv": 5.0e-14,
            },
        ]

        specs = []
        for spec in raw_specs:
            rhs, q, omega, constraints = compiled_chart(
                jax,
                jnp,
                spec["module"],
                spec["state_class"],
                spec["args"],
                spec["kind"],
                spec["constraint_names"],
            )
            specs.append(
                {
                    **spec,
                    "rhs_jit": rhs,
                    "q_jit": q,
                    "omega_jit": omega,
                    "constraint_jit": constraints,
                }
            )

        directions, angular_weights = lebedev_26()
        temperature = 3000.0
        nu_abs = c / (1215.6701e-10)
        hydrogen_mass = (
            physical_constants["atomic mass constant"][0]
            * 1.00782503223
        )
        Doppler_width = nu_abs * np.sqrt(
            2.0 * k * temperature / hydrogen_mass
        ) / c
        x_red, x_blue = -10.25, 10.25

        arrays: dict[str, np.ndarray] = {
            "directions": directions,
            "angular_weights": angular_weights,
        }
        model_rows = []
        branch_rows = []
        frame_rows = []
        constraint_rows = []
        all_collision_actions = []

        collision_file = ROOT / "data" / "far_scalar_release_v047.npz"
        collision_sha = hashlib.sha256(collision_file.read_bytes()).hexdigest()
        collision_data = np.load(collision_file)
        scalar_generator = np.asarray(collision_data["scalar_generator_sInv"])
        equilibrium_weight = np.asarray(collision_data["equilibrium_weight_m3"])
        random_state = np.linspace(0.8, 1.2, scalar_generator.shape[0])
        collision_action = scalar_generator @ random_state
        collision_left = float(
            np.max(np.abs(np.ones(scalar_generator.shape[0]) @ scalar_generator))
            / np.max(np.abs(scalar_generator))
        )
        collision_right = float(
            np.max(np.abs(scalar_generator @ equilibrium_weight))
            / (
                np.max(np.abs(scalar_generator))
                * np.max(np.abs(equilibrium_weight))
            )
        )

        max_frame_frequency = 0.0
        max_frame_direction = 0.0
        max_number_residual = 0.0
        max_four_residual = 0.0
        min_root_count = 10**9
        max_constraint_global = 0.0

        for spec in specs:
            trajectory = integrate_model(jnp, spec)
            snapshots = []
            derivatives = []
            q_values = []
            constraints_series = []
            for tau, state, H, cosmic_time in zip(
                trajectory["tau"],
                trajectory["state"],
                trajectory["H"],
                trajectory["time"],
            ):
                snapshot, derivative, q_value, residuals = snapshot_from_spec(
                    jnp, spec, tau, state, H, cosmic_time
                )
                snapshots.append(snapshot)
                derivatives.append(derivative)
                q_values.append(q_value)
                constraints_series.append(
                    [residuals[name] for name in spec["constraint_names"]]
                )
            derivatives = np.asarray(derivatives)
            q_values = np.asarray(q_values)
            constraints_series = np.asarray(constraints_series)

            normal_R = np.zeros((len(snapshots), len(directions)))
            hydrogen_R = np.zeros_like(normal_R)
            direction_H = np.zeros((len(snapshots), len(directions), 3))
            red_speed = np.zeros_like(normal_R)
            blue_speed = np.zeros_like(normal_R)

            for time_index, snapshot in enumerate(snapshots):
                for direction_index, direction in enumerate(directions):
                    normal = normal_frame_characteristic(snapshot, direction)
                    hydrogen = hydrogen_frame_characteristic(snapshot, normal)
                    normal_R[time_index, direction_index] = normal.R_normal_s_inv
                    hydrogen_R[time_index, direction_index] = (
                        hydrogen.R_hydrogen_s_inv
                    )
                    direction_H[time_index, direction_index] = (
                        hydrogen.direction_hydrogen
                    )
                    red_speed[time_index, direction_index] = doppler_coordinate_speed(
                        hydrogen.R_hydrogen_s_inv,
                        x_red,
                        nu_abs_Hz=nu_abs,
                        Doppler_width_Hz=Doppler_width,
                    )
                    blue_speed[time_index, direction_index] = doppler_coordinate_speed(
                        hydrogen.R_hydrogen_s_inv,
                        x_blue,
                        nu_abs_Hz=nu_abs,
                        Doppler_width_Hz=Doppler_width,
                    )

            selected_time_indices = np.unique(
                np.linspace(0, len(snapshots) - 1, 9, dtype=int)
            )
            selected_direction_indices = [0, 1, 6, 8, 9, 16, 20, 24]
            model_frame_frequency = 0.0
            model_frame_direction = 0.0
            for time_index in selected_time_indices:
                for direction_index in selected_direction_indices:
                    frequency_residual, direction_residual = frame_direct_residual(
                        snapshots[time_index], directions[direction_index]
                    )
                    model_frame_frequency = max(
                        model_frame_frequency, frequency_residual
                    )
                    model_frame_direction = max(
                        model_frame_direction, direction_residual
                    )
                    frame_rows.append(
                        {
                            "model": spec["model"],
                            "time_index": int(time_index),
                            "direction_index": int(direction_index),
                            "frequency_residual_normalized": frequency_residual,
                            "direction_residual_normalized": direction_residual,
                        }
                    )
            max_frame_frequency = max(max_frame_frequency, model_frame_frequency)
            max_frame_direction = max(max_frame_direction, model_frame_direction)

            root_counts = np.array(
                [
                    len(
                        piecewise_linear_roots(
                            trajectory["time"], red_speed[:, index]
                        )
                    )
                    for index in range(len(directions))
                ]
            )
            maximum_roots = int(root_counts.max())
            candidate_indices = np.flatnonzero(root_counts == maximum_roots)
            chosen_direction = int(
                candidate_indices[
                    np.argmax(
                        np.ptp(
                            hydrogen_R[:, candidate_indices]
                            / trajectory["H"][:, None],
                            axis=0,
                        )
                    )
                ]
            )
            min_root_count = min(min_root_count, maximum_roots)

            middle = len(snapshots) // 2
            nH = direction_H[middle, chosen_direction]
            red_frequency_ratio = (
                nu_abs + x_red * Doppler_width
            ) / nu_abs
            blue_frequency_ratio = (
                nu_abs + x_blue * Doppler_width
            ) / nu_abs
            p_red = red_frequency_ratio * np.concatenate(([1.0], nH))
            p_blue = blue_frequency_ratio * np.concatenate(([1.0], nH))
            ledger = boundary_ledger(
                trajectory["time"],
                red_speed[:, chosen_direction],
                blue_speed[:, chosen_direction],
                interior_occupation=1.3,
                red_occupation=0.7,
                blue_occupation=0.9,
                red_photon_four=p_red,
                blue_photon_four=p_blue,
            )
            reference_red = quad_boundary_flux(
                trajectory["time"],
                red_speed[:, chosen_direction],
                1.3,
                0.7,
                "red",
            )
            reference_blue = quad_boundary_flux(
                trajectory["time"],
                blue_speed[:, chosen_direction],
                1.3,
                0.9,
                "blue",
            )
            localized_residual = max(
                abs(ledger.red_flux - reference_red),
                abs(ledger.blue_flux - reference_blue),
            )
            localized_scale = max(
                abs(reference_red), abs(reference_blue), 1.0e-300
            )
            localized_relative = localized_residual / localized_scale
            naive_red = naive_fixed_branch(
                trajectory["time"],
                red_speed[:, chosen_direction],
                1.3,
                0.7,
                "red",
            )
            naive_blue = naive_fixed_branch(
                trajectory["time"],
                blue_speed[:, chosen_direction],
                1.3,
                0.9,
                "blue",
            )
            naive_relative = max(
                abs(naive_red - reference_red),
                abs(naive_blue - reference_blue),
            ) / localized_scale

            constraint_max = float(np.max(np.abs(constraints_series)))
            max_constraint_global = max(max_constraint_global, constraint_max)
            beta_norm = np.array(
                [np.linalg.norm(snapshot.beta_H) for snapshot in snapshots]
            )
            sigma2 = np.array(
                [
                    np.trace(snapshot.sigma_s_inv @ snapshot.sigma_s_inv)
                    / (6.0 * snapshot.H_s_inv**2)
                    for snapshot in snapshots
                ]
            )
            mixed_times = int(
                np.sum(
                    (hydrogen_R.min(axis=1) < 0.0)
                    & (hydrogen_R.max(axis=1) > 0.0)
                )
            )

            model_rows.append(
                {
                    "model": spec["model"],
                    "bianchi_type": spec["bianchi_type"],
                    "chart": snapshots[0].chart_id,
                    "trajectory_success": bool(trajectory["success"]),
                    "tau_final": float(trajectory["tau"][-1]),
                    "cosmic_time_final_s": float(trajectory["time"][-1]),
                    "H_initial_s^-1": float(trajectory["H"][0]),
                    "H_final_s^-1": float(trajectory["H"][-1]),
                    "Omega_min": float(
                        min(
                            float(spec["omega_jit"](jnp.asarray(state)))
                            for state in trajectory["state"]
                        )
                    ),
                    "Sigma2_max": float(sigma2.max()),
                    "tilt_speed_max": float(beta_norm.max()),
                    "constraint_max": constraint_max,
                    "R_H_over_H_min": float(
                        np.min(hydrogen_R / trajectory["H"][:, None])
                    ),
                    "R_H_over_H_max": float(
                        np.max(hydrogen_R / trajectory["H"][:, None])
                    ),
                    "mixed_sign_time_count": mixed_times,
                    "selected_direction": chosen_direction,
                    "selected_root_count": maximum_roots,
                    "frame_frequency_residual": model_frame_frequency,
                    "frame_direction_residual": model_frame_direction,
                }
            )
            branch_rows.append(
                {
                    "model": spec["model"],
                    "direction_index": chosen_direction,
                    "direction_x": float(directions[chosen_direction, 0]),
                    "direction_y": float(directions[chosen_direction, 1]),
                    "direction_z": float(directions[chosen_direction, 2]),
                    "red_root_count": len(ledger.red_roots),
                    "blue_root_count": len(ledger.blue_roots),
                    "red_roots_tau_or_time": ";".join(
                        f"{value:.16e}" for value in ledger.red_roots
                    ),
                    "blue_roots_tau_or_time": ";".join(
                        f"{value:.16e}" for value in ledger.blue_roots
                    ),
                    "localized_flux_relative_residual": localized_relative,
                    "naive_fixed_branch_relative_error": naive_relative,
                    "number_residual": ledger.number_residual,
                    "four_momentum_residual": float(
                        np.max(np.abs(ledger.four_momentum_residual))
                    ),
                    "total_absolute_flux": ledger.total_absolute_flux,
                }
            )
            for time_index, (tau, residual_values) in enumerate(
                zip(trajectory["tau"], constraints_series)
            ):
                row = {
                    "model": spec["model"],
                    "time_index": time_index,
                    "tau": float(tau),
                }
                row.update(
                    {
                        name: float(value)
                        for name, value in zip(
                            spec["constraint_names"], residual_values
                        )
                    }
                )
                constraint_rows.append(row)

            max_number_residual = max(
                max_number_residual, abs(ledger.number_residual)
            )
            max_four_residual = max(
                max_four_residual,
                float(np.max(np.abs(ledger.four_momentum_residual))),
            )
            all_collision_actions.append(collision_action.copy())

            prefix = spec["model"]
            arrays[f"{prefix}_tau"] = trajectory["tau"]
            arrays[f"{prefix}_cosmic_time_s"] = trajectory["time"]
            arrays[f"{prefix}_state"] = trajectory["state"]
            arrays[f"{prefix}_H_s_inv"] = trajectory["H"]
            arrays[f"{prefix}_q"] = q_values
            arrays[f"{prefix}_sigma_s_inv"] = np.asarray(
                [snapshot.sigma_s_inv for snapshot in snapshots]
            )
            arrays[f"{prefix}_N_s_inv"] = np.asarray(
                [snapshot.N_s_inv for snapshot in snapshots]
            )
            arrays[f"{prefix}_A_s_inv"] = np.asarray(
                [snapshot.A_s_inv for snapshot in snapshots]
            )
            arrays[f"{prefix}_frame_rotation_s_inv"] = np.asarray(
                [snapshot.frame_rotation_s_inv for snapshot in snapshots]
            )
            arrays[f"{prefix}_beta_H"] = np.asarray(
                [snapshot.beta_H for snapshot in snapshots]
            )
            arrays[f"{prefix}_D0_beta_H_s_inv"] = np.asarray(
                [snapshot.D0_beta_H_s_inv for snapshot in snapshots]
            )
            arrays[f"{prefix}_constraints"] = constraints_series
            arrays[f"{prefix}_normal_R_s_inv"] = normal_R
            arrays[f"{prefix}_hydrogen_R_s_inv"] = hydrogen_R
            arrays[f"{prefix}_direction_H"] = direction_H
            arrays[f"{prefix}_red_speed_s_inv"] = red_speed
            arrays[f"{prefix}_blue_speed_s_inv"] = blue_speed

        collision_actions = np.asarray(all_collision_actions)
        collision_model_difference = float(
            np.max(np.abs(collision_actions - collision_actions[0]))
        )
        arrays["collision_action_reference"] = collision_action
        arrays["collision_equilibrium_weight"] = equilibrium_weight
        arrays["model_names"] = np.asarray([row["model"] for row in model_rows])

        write_csv(ARTIFACT / "background_model_summary.csv", model_rows)
        write_csv(ARTIFACT / "branch_event_summary.csv", branch_rows)
        write_csv(ARTIFACT / "frame_adapter_regression.csv", frame_rows)
        # Constraint rows have chart-dependent fields; normalize union columns.
        constraint_names_union = [
            "model", "time_index", "tau", "gauss", "Omega_negative",
            "C1", "C2", "C3", "C4", "C5", "g",
        ]
        normalized_constraint_rows = [
            {name: row.get(name, "") for name in constraint_names_union}
            for row in constraint_rows
        ]
        write_csv(ARTIFACT / "constraint_trajectory.csv", normalized_constraint_rows)
        np.savez_compressed(ARTIFACT / "background_frame_snapshots.npz", **arrays)
        np.savez_compressed(DATA_OUT, **arrays)

        v047_ledger = json.loads(
            (
                ROOT
                / "archive"
                / "expanded"
                / "Full_Bianchi_HyRec_PR01B1B3B3B1_far_scalar_release_v0_47"
                / "PR01B1B3B3B1_ledger.json"
            ).read_text(encoding="utf-8")
        )
        inherited_collision_four = float(
            v047_ledger["hard_results"]["four_force_residual_max"]
        )

        hard_gates = {
            "primitive_trajectory_success": all(
                row["trajectory_success"] for row in model_rows
            ),
            "representative_types": {
                row["bianchi_type"] for row in model_rows
            } == {"II", "VI_h", "VI_-1/9"},
            "primitive_constraints": max_constraint_global < 2.0e-8,
            "finite_tilt_frame_frequency": max_frame_frequency < 2.0e-8,
            "finite_tilt_frame_direction": max_frame_direction < 2.0e-8,
            "turning_event_localization": min_root_count >= 1,
            "branch_quadrature": max(
                row["localized_flux_relative_residual"] for row in branch_rows
            ) < 1.0e-10,
            "boundary_number": max_number_residual < 1.0e-12,
            "boundary_four_momentum": max_four_residual < 1.0e-11,
            "local_collision_unchanged": collision_model_difference == 0.0,
            "inherited_scalar_collision": all(
                value
                for key, value in v047_ledger["hard_gate_status"].items()
                if key not in {"exterior_exterior_collision", "PR01C_background_adapter"}
            ),
            "total_four_force": max(
                max_four_residual, inherited_collision_four
            ) < 1.0e-11,
        }

        hard_gates = {key: bool(value) for key, value in hard_gates.items()}

        formalism = r'''# PR-01C BackgroundSnapshot frame-adapter closure

## Stable interface

The local recombination and Ly-alpha collision kernel receives physical
orthonormal-frame data only:

\[
\mathcal B=
\{H,q,\sigma_{ab},N_{ab},A_a,R_a,
\beta_{\rm H}^a,D_0\beta_{\rm H}^a\}.
\]

All rates are in s^-1. Primitive chart state classes are confined to the
adapter layer.

## Normal-frame photon characteristic

For a unit direction \(e^a\),

\[
\mathcal R_n=D_0\ln\nu_n
=-H-\sigma_{ab}e^ae^b,
\]

\[
\begin{aligned}
D_0e^a={}&
-\left(\sigma^a{}_be^b
-e^a\sigma_{bc}e^be^c\right)
+(R\times e)^a
\\
&-\left[\mathcal P^a(e)
-e^ae_b\mathcal P^b(e)\right],
\end{aligned}
\]

\[
\mathcal P^a(e)
=A^a-(A\cdot e)e^a
+\epsilon^a{}_{bc}e^b(N e)^c.
\]

## Exact hydrogen-frame adapter

\[
\mathcal D_{\rm H}
=\Gamma_{\rm H}(1-\beta_{\rm H}\cdot e_n),
\]

\[
\nu_{\rm H}=\mathcal D_{\rm H}\nu_n,
\]

\[
\boxed{
\mathcal R_{\rm H}
=\mathcal R_n+D_0\ln\mathcal D_{\rm H}
},
\]

\[
D_0\ln\mathcal D_{\rm H}
=\Gamma_{\rm H}^2\beta_{\rm H}\cdot D_0\beta_{\rm H}
-
\frac{
D_0\beta_{\rm H}\cdot e_n
+\beta_{\rm H}\cdot D_0e_n
}{1-\beta_{\rm H}\cdot e_n}.
\]

The aberration and its derivative are evaluated at finite tilt; no
small-beta expansion is used.

## Chart lifts

### Bianchi II / class A

\[
\Sigma_{ab}=\mathrm{diag}
(-2\Sigma_+,\Sigma_++\sqrt3\Sigma_-,
\Sigma_+-\sqrt3\Sigma_-),
\]

\[
N_{ab}=\mathrm{diag}(N_1,N_2,N_3),
\quad A_a=R_a=0.
\]

### Tilted class B / Hervik gauge

\[
N_{ab}=
\begin{pmatrix}
0&0&0\\
0&\sqrt3\lambda N&\sqrt3N\\
0&\sqrt3N&\sqrt3\lambda N
\end{pmatrix},
\quad
A_a=(A,0,0),
\]

\[
R_a=(\sqrt3\lambda\Sigma_-,
-\sqrt3\Sigma_{13},
\sqrt3\Sigma_{12}).
\]

The chart tilt is used as \(\beta_{\rm H}\), with
\(D_0\beta_{\rm H}=H\beta_{\rm H}'\).

### Exceptional VI_-1/9 / HHW gauge

\[
\Sigma_{13}=\Sigma_2,
\quad\Sigma_{23}=\Sigma_\times,
\quad\Sigma_{12}=0,
\]

\[
N_{22}=2\sqrt3N_-,
\quad N_{23}=3A,
\quad N_{33}=0,
\]

\[
R_a=(-\sqrt3\Sigma_\times,-\sqrt3\Sigma_2,0).
\]

This lift was independently closed against the primitive general-chart
RHS before release.

## Moving Doppler boundary

For \(x=(\nu_{\rm H}-\nu_{\rm abs})/\Delta\nu_D\),

\[
\mathcal A
=\frac{\nu_{\rm H}\mathcal R_{\rm H}-D_0\nu_{\rm abs}}
{\Delta\nu_D}
-xD_0\ln\Delta\nu_D-D_0x_{\rm boundary}.
\]

Every zero of \(\mathcal A_{R/B,q}\) splits the timestep and changes the
upwind trace. The piecewise-linear regression integrates each branch
exactly and closes the combined interior/red/blue number and
four-momentum ledger.

## Microphysics firewall

The v0.47 collision conductance, Bose action and same-event four-force
are consumed without any geometry argument. Bianchi dependence enters
only through the characteristic and boundary-speed adapter.
'''
        (ARTIFACT / "PR01C_FRAME_ADAPTER_FORMALISM.md").write_text(
            formalism, encoding="utf-8"
        )

        ledger = {
            "classification": "PR01C_BACKGROUND_FRAME_ADAPTER_CLOSURE",
            "stage": "PR-01C",
            "status": "PASS_PR01_COMPLETE",
            "source": {
                "primitive_archive": str(SRC_TARBALL.relative_to(ROOT)),
                "primitive_archive_sha256": tar_sha,
                "collision_artifact": "PR01B1-B3B3B1/v0.47",
                "collision_data_sha256": collision_sha,
            },
            "models": model_rows,
            "hard_results": {
                "maximum_primitive_constraint": max_constraint_global,
                "maximum_frame_frequency_residual": max_frame_frequency,
                "maximum_frame_direction_residual": max_frame_direction,
                "minimum_selected_root_count": min_root_count,
                "maximum_branch_quadrature_relative": max(
                    row["localized_flux_relative_residual"]
                    for row in branch_rows
                ),
                "minimum_naive_fixed_branch_error": min(
                    row["naive_fixed_branch_relative_error"]
                    for row in branch_rows
                ),
                "maximum_number_residual": max_number_residual,
                "maximum_boundary_four_momentum_residual": max_four_residual,
                "collision_action_model_difference": collision_model_difference,
                "collision_left_null_relative": collision_left,
                "collision_right_null_relative": collision_right,
                "inherited_collision_four_force": inherited_collision_four,
            },
            "hard_gate_status": hard_gates,
            "decision": {
                "PR01C": "PASS",
                "PR01": "COMPLETE",
                "local_collision_microphysics": "UNCHANGED",
                "next_PR": "PR-02 nonlinear anisotropic Bose collision production integration",
            },
            "limitations": [
                "The representative class-A and exceptional primitive charts are non-tilted; finite tilt is exercised by the tilted class-B trajectory.",
                "This is a smoke/regression closure, not the all-11 end-to-end sweep assigned to PR-10.",
                "The collision amplitude remains the provisional unresolved scalar 2p pole+crossed model; full bound+continuum KHW physics is PR-03.",
                "Exterior-exterior collisions remain assigned to the boundary/Liouville module as locked in v0.47.",
            ],
            "next_stage": {
                "name": "PR-02 nonlinear anisotropic Bose collision production integration",
                "tasks": [
                    "Promote the v0.47 nonlinear Bose edge action from mock fields to the BackgroundSnapshot adaptive L=12/20/24 runtime interface.",
                    "Add positivity-preserving implicit updates and analytic/JVP Jacobian tests.",
                    "Run finite-tilt, nonlinear-shear and crossing stress states with full BE/number/entropy/four-force gates.",
                ],
            },
        }
        (ARTIFACT / "PR01C_ledger.json").write_text(
            json.dumps(ledger, indent=2, default=json_default) + "\n", encoding="utf-8"
        )

        verify_code = r'''from pathlib import Path
import csv
import json
import numpy as np

HERE=Path(__file__).resolve().parent
ledger=json.loads((HERE/"PR01C_ledger.json").read_text())
assert ledger["status"] == "PASS_PR01_COMPLETE"
assert all(ledger["hard_gate_status"].values())

models=list(csv.DictReader((HERE/"background_model_summary.csv").open()))
assert {row["bianchi_type"] for row in models} == {"II","VI_h","VI_-1/9"}
assert all(int(row["selected_root_count"]) >= 1 for row in models)

data=np.load(HERE/"background_frame_snapshots.npz")
assert data["directions"].shape == (26,3)
assert len(data["model_names"]) == 3
print("PR-01C background frame adapter: PASS")
'''
        (ARTIFACT / "verify_PR01C.py").write_text(
            verify_code, encoding="utf-8"
        )
        subprocess.run([sys.executable, str(ARTIFACT / "verify_PR01C.py")], check=True)

        readme = f'''# Full Bianchi-HyRec PR-01C v0.48

This artifact closes the chart-independent BackgroundSnapshot and exact
finite-tilt hydrogen-frame characteristic for three primitive trajectories.

- maximum primitive constraint: {max_constraint_global:.6e}
- maximum normalized frame-frequency residual: {max_frame_frequency:.6e}
- maximum normalized frame-direction residual: {max_frame_direction:.6e}
- minimum selected root count: {min_root_count}
- maximum boundary number residual: {max_number_residual:.6e}
- maximum total four-force residual: {max(max_four_residual,inherited_collision_four):.6e}

Status: PR-01 COMPLETE. Next: PR-02 nonlinear anisotropic Bose collision.
'''
        (ARTIFACT / "README.md").write_text(readme, encoding="utf-8")

        manifest_lines = []
        for path in sorted(ARTIFACT.iterdir()):
            if path.name == "MANIFEST_SHA256.txt":
                continue
            manifest_lines.append(
                f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}"
            )
        (ARTIFACT / "MANIFEST_SHA256.txt").write_text(
            "\n".join(manifest_lines) + "\n", encoding="utf-8"
        )
        if BUNDLE.exists():
            BUNDLE.unlink()
        with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(ARTIFACT.iterdir()):
                archive.write(path, arcname=f"{ARTIFACT_NAME}/{path.name}")
        with zipfile.ZipFile(BUNDLE) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise RuntimeError(f"bad ZIP member: {bad}")

        print(
            json.dumps(
                {
                    "artifact": str(ARTIFACT),
                    "bundle": str(BUNDLE),
                    "data": str(DATA_OUT),
                    "hard_results": ledger["hard_results"],
                    "hard_gates": hard_gates,
                    "bundle_sha256": hashlib.sha256(BUNDLE.read_bytes()).hexdigest(),
                },
                indent=2,
                default=json_default,
            )
        )


if __name__ == "__main__":
    main()

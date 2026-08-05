#!/usr/bin/env python3
"""Generate the bounded PR-02 nonlinear Bose production artifact.

The expensive full-network Newton/JVP regressions deliberately run with one
BLAS thread.  The operator consists of many small contractions; unrestricted
thread spawning is slower and makes recovery receipts machine-dependent.
"""
from __future__ import annotations

import os
import sys

# Some Python installations import a BLAS-linked extension from site startup,
# before this script reaches NumPy.  Re-exec once with the lock already in the
# process environment so the full-network receipt remains fast and stable.
if os.environ.get("PR02_NUMERICAL_THREAD_LOCK") != "1":
    environment = os.environ.copy()
    environment.update(
        {
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "PR02_NUMERICAL_THREAD_LOCK": "1",
        }
    )
    os.execve(sys.executable, [sys.executable, *sys.argv], environment)

import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import zipfile

import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
    apply_nonlinear_bose_jvp,
    apply_nonlinear_bose_operator,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (
    ADAPTIVE_GRID_ORDER,
    BoseCollisionRuntime,
    CollisionNetwork,
    LineBoundaryConfig,
    implicit_residual_jvp,
)


ARTIFACT_NAME = "Full_Bianchi_HyRec_PR02_nonlinear_bose_runtime_v0_49"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "pr02_nonlinear_bose_runtime_v049.npz"
COLLISION_DATA = ROOT / "data" / "far_scalar_release_v047.npz"
SNAPSHOT_DATA = ROOT / "data" / "pr01c_background_snapshots_v048.npz"

MODEL_META = {
    "Bianchi_II_large_shear": ("class_a", "II"),
    "Bianchi_VI_h_tilted_large_shear": ("class_b_tilted", "VI_h"),
    "Bianchi_VI_minus_1_over_9_exceptional": (
        "exceptional_VI",
        "VI_-1/9",
    ),
}

SCENARIOS = (
    {
        "name": "finite_or_mixed_tilt",
        "model": "Bianchi_VI_h_tilted_large_shear",
        "snapshot_index": 100,
        "expected_policy": "finite_or_mixed_tilt",
        "expected_ell_max": 12,
    },
    {
        "name": "nonlinear_even_shear",
        "model": "Bianchi_II_large_shear",
        "snapshot_index": 70,
        "expected_policy": "nonlinear_even_shear",
        "expected_ell_max": 20,
    },
    {
        "name": "directional_crossing",
        "model": "Bianchi_II_large_shear",
        "snapshot_index": 0,
        "expected_policy": "directional_crossing",
        "expected_ell_max": 24,
    },
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)


def snapshot_record(data, model: str, index: int) -> BackgroundSnapshot:
    chart, bianchi_type = MODEL_META[model]
    return BackgroundSnapshot(
        tau=data[f"{model}_tau"][index],
        cosmic_time_s=data[f"{model}_cosmic_time_s"][index],
        H_s_inv=data[f"{model}_H_s_inv"][index],
        q=data[f"{model}_q"][index],
        sigma_s_inv=data[f"{model}_sigma_s_inv"][index],
        N_s_inv=data[f"{model}_N_s_inv"][index],
        A_s_inv=data[f"{model}_A_s_inv"][index],
        frame_rotation_s_inv=data[f"{model}_frame_rotation_s_inv"][index],
        beta_H=data[f"{model}_beta_H"][index],
        D0_beta_H_s_inv=data[f"{model}_D0_beta_H_s_inv"][index],
        chart_id=chart,
        bianchi_type=bianchi_type,
    )


def be_family(network: CollisionNetwork, maximum: float) -> np.ndarray:
    activity = network.activity_weight
    chemical_activity = maximum / (1.0 + maximum) / float(np.max(activity))
    return chemical_activity * activity / (1.0 - chemical_activity * activity)


def normalized(profile: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return profile / float(np.dot(weights, profile))


def runtime_occupation(name, state, network: CollisionNetwork) -> np.ndarray:
    """Deterministic collision-substep stress field from runtime characteristics.

    These fields are not claimed to be solutions of the coupled Liouville
    problem.  They are positive, nonlinear anisotropic states used to exercise
    the production collision update at an actual v0.48 BackgroundSnapshot.
    """

    base = be_family(network, 0.7)
    centers = network.centers
    weights = state.grid.weights

    if name == "finite_or_mixed_tilt":
        log_doppler = np.log(state.doppler_factor)
        log_doppler -= float(np.dot(weights, log_doppler))
        angular = normalized(np.exp(-1.2 * log_doppler), weights)
        spectral = 1.0 + 0.04 * np.cos(centers / 3.7)
        return base[:, None] * spectral[:, None] * angular[None, :]

    if name == "nonlinear_even_shear":
        normalized_shear = state.snapshot.sigma_s_inv / state.snapshot.H_s_inv
        shear_projection = np.einsum(
            "ai,ij,aj->a",
            state.direction_normal,
            normalized_shear,
            state.direction_normal,
        )
        shear_projection -= float(np.dot(weights, shear_projection))
        angular = normalized(np.exp(1.1 * shear_projection), weights)
        spectral = 1.0 + 0.06 * np.exp(-0.5 * (centers / 2.0) ** 2)
        return base[:, None] * spectral[:, None] * angular[None, :]

    if name == "directional_crossing":
        drift = state.R_hydrogen_s_inv / state.snapshot.H_s_inv
        drift /= max(float(np.max(np.abs(drift))), 1e-300)
        coupled = (
            np.tanh(centers[:, None] / 1.2)
            * np.tanh(2.0 * drift)[None, :]
        )
        return base[:, None] * np.exp(0.25 * coupled)

    raise ValueError(name)


def relative_number_residual(result) -> float:
    return abs(float(result.number_residual)) / (
        float(result.gross_action_scale) + 1e-300
    )


def exact_jvp_regression(occupation, state, network: CollisionNetwork):
    angle_index = np.arange(state.grid.n_angle, dtype=float)
    perturbation = occupation * 0.03 * np.sin(
        network.centers[:, None] / 3.1 + 0.017 * angle_index[None, :]
    )
    kwargs = {
        "mode_measure": network.mode_measure,
        "equilibrium_weight": network.equilibrium_weight,
        "pair_moments": network.pair_moments,
        "same_cell_rates": network.same_cell_rates,
        "grid": state.grid,
    }
    exact = apply_nonlinear_bose_jvp(occupation, perturbation, **kwargs)
    epsilon = 1e-4
    plus = apply_nonlinear_bose_operator(
        occupation + epsilon * perturbation,
        **kwargs,
    ).occupation_action
    minus = apply_nonlinear_bose_operator(
        occupation - epsilon * perturbation,
        **kwargs,
    ).occupation_action
    finite_difference = (plus - minus) / (2.0 * epsilon)
    relative = float(
        np.linalg.norm(exact.occupation_action_jvp - finite_difference)
        / (np.linalg.norm(finite_difference) + 1e-300)
    )
    number_scale = float(
        np.sum(
            np.abs(exact.number_action_jvp)
            * state.grid.weights[None, :]
        )
    )
    number_relative = abs(float(exact.number_residual_jvp)) / (
        number_scale + 1e-300
    )
    return exact, finite_difference, relative, number_relative


def implicit_jvp_regression(occupation, state, network, dt_s):
    angle_index = np.arange(state.grid.n_angle, dtype=float)
    direction = 0.025 * np.cos(
        network.centers[:, None] / 2.4 + 0.013 * angle_index[None, :]
    )
    exact = implicit_residual_jvp(
        occupation,
        direction,
        dt_s=dt_s,
        network=network,
        grid=state.grid,
    )
    old = 0.97 * occupation
    kwargs = {
        "mode_measure": network.mode_measure,
        "equilibrium_weight": network.equilibrium_weight,
        "pair_moments": network.pair_moments,
        "same_cell_rates": network.same_cell_rates,
        "grid": state.grid,
    }

    def residual(log_occupation):
        field = np.exp(log_occupation)
        action = apply_nonlinear_bose_operator(
            field,
            **kwargs,
        ).occupation_action
        return field - old - dt_s * action

    epsilon = 1e-4
    log_field = np.log(occupation)
    finite_difference = (
        residual(log_field + epsilon * direction)
        - residual(log_field - epsilon * direction)
    ) / (2.0 * epsilon)
    relative = float(
        np.linalg.norm(exact - finite_difference)
        / (np.linalg.norm(finite_difference) + 1e-300)
    )
    return exact, finite_difference, relative


def high_precision_checks() -> list[dict]:
    mp.mp.dps = 80

    f = mp.mpf("0.37")
    z = mp.mpf("0.23")
    q = mp.mpf("0.61")
    df = mp.mpf("-0.047")
    dq = mp.mpf("0.013")

    def delta(epsilon):
        shifted_f = f + epsilon * df
        shifted_q = q + epsilon * dq
        phi = shifted_f / (z * (1 + shifted_f))
        return (1 + shifted_f) * (phi - shifted_q)

    derivative_reference = mp.diff(delta, mp.mpf("0"))
    derivative_analytic = df / z - q * df - dq * (1 + f)
    derivative_relative = abs(derivative_reference - derivative_analytic) / max(
        abs(derivative_reference), mp.mpf("1e-100")
    )

    beta = mp.mpf("0.37")
    gamma = 1 / mp.sqrt(1 - beta**2)
    normal_to_hydrogen = mp.matrix(
        [[gamma, -gamma * beta], [-gamma * beta, gamma]]
    )
    hydrogen_to_normal = mp.matrix(
        [[gamma, gamma * beta], [gamma * beta, gamma]]
    )
    identity_residual = max(
        abs(value)
        for value in (
            hydrogen_to_normal * normal_to_hydrogen - mp.eye(2)
        )
    )

    z_a = mp.mpf("0.2")
    z_b = mp.mpf("0.31")
    activity = mp.mpf("0.7")
    f_a = activity * z_a / (1 - activity * z_a)
    f_b = activity * z_b / (1 - activity * z_b)
    be_pair_residual = abs(
        (1 + f_a) * f_b / z_b - f_a * (1 + f_b) / z_a
    )

    return [
        {
            "check": "activity_reference_derivative_mpmath_80dps",
            "absolute_residual": mp.nstr(
                abs(derivative_reference - derivative_analytic), 20
            ),
            "relative_residual": mp.nstr(derivative_relative, 20),
        },
        {
            "check": "lorentz_inverse_mpmath_80dps",
            "absolute_residual": mp.nstr(identity_residual, 20),
            "relative_residual": mp.nstr(identity_residual, 20),
        },
        {
            "check": "bose_einstein_pair_null_mpmath_80dps",
            "absolute_residual": mp.nstr(be_pair_residual, 20),
            "relative_residual": mp.nstr(be_pair_residual, 20),
        },
    ]


def manifest(artifact: Path) -> None:
    rows = []
    for path in sorted(artifact.iterdir()):
        if path.name == "MANIFEST_SHA256.txt":
            continue
        rows.append(f"{sha256(path)}  {path.name}")
    (artifact / "MANIFEST_SHA256.txt").write_text(
        "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    BUNDLE.parent.mkdir(parents=True, exist_ok=True)

    network = CollisionNetwork.from_npz(COLLISION_DATA)
    runtime = BoseCollisionRuntime(network)
    boundary = LineBoundaryConfig.lyman_alpha()

    policy_rows: list[dict] = []
    operator_rows: list[dict] = []
    implicit_rows: list[dict] = []
    jacobian_rows: list[dict] = []
    edge_rows: list[dict] = []
    evidence: dict[str, np.ndarray] = {
        "scenario_names": np.asarray([row["name"] for row in SCENARIOS]),
        "state_labels": network.state_labels,
        "state_intervals": network.state_intervals,
        "mode_measure": network.mode_measure,
        "equilibrium_weight": network.equilibrium_weight,
        "momentum_scale": network.momentum_scale,
    }

    maximum_be_relative = 0.0
    maximum_number_relative = 0.0
    maximum_boundary_number_relative = 0.0
    maximum_jvp_relative = 0.0
    maximum_jvp_number_relative = 0.0
    maximum_implicit_jvp_relative = 0.0
    maximum_four_force_hydrogen = 0.0
    maximum_four_force_normal = 0.0
    maximum_frame_roundtrip = 0.0
    minimum_boundary_fraction = math.inf
    maximum_gram_residual = 0.0
    minimum_grid_weight = math.inf
    maximum_implicit_residual = 0.0
    maximum_implicit_number_change = 0.0
    minimum_implicit_occupation = math.inf
    maximum_explicit_trial_minimum = -math.inf
    maximum_entropy_production = -math.inf
    maximum_free_energy_change = -math.inf

    with np.load(SNAPSHOT_DATA, allow_pickle=False) as snapshot_data:
        prepared_records = []
        for spec in SCENARIOS:
            snapshot = snapshot_record(
                snapshot_data,
                spec["model"],
                spec["snapshot_index"],
            )
            state = runtime.prepare(snapshot, boundary=boundary)
            occupation = runtime_occupation(spec["name"], state, network)
            result = runtime.evaluate(state, occupation)

            be = be_family(network, 1.0)
            be_occupation = np.repeat(
                be[:, None],
                state.grid.n_angle,
                axis=1,
            )
            be_result = apply_nonlinear_bose_operator(
                be_occupation,
                mode_measure=network.mode_measure,
                equilibrium_weight=network.equilibrium_weight,
                pair_moments=network.pair_moments,
                same_cell_rates=network.same_cell_rates,
                grid=state.grid,
                photon_momentum_scale=network.momentum_scale,
            )
            be_relative = float(
                np.max(np.abs(be_result.number_action))
                / (be_result.gross_action_scale + 1e-300)
            )

            jvp, jvp_fd, jvp_relative, jvp_number_relative = (
                exact_jvp_regression(occupation, state, network)
            )

            action = result.full_action.occupation_action
            negative = action < 0.0
            if not np.any(negative):
                raise RuntimeError(f"{spec['name']} has no positivity-limiting mode")
            explicit_critical_dt = float(
                np.min(-occupation[negative] / action[negative])
            )
            dt_s = 1.02 * explicit_critical_dt
            implicit = runtime.implicit_step(state, occupation, dt_s=dt_s)

            implicit_jvp_exact = np.empty((0, 0))
            implicit_jvp_fd = np.empty((0, 0))
            implicit_jvp_relative = math.nan
            if spec["name"] == "finite_or_mixed_tilt":
                (
                    implicit_jvp_exact,
                    implicit_jvp_fd,
                    implicit_jvp_relative,
                ) = implicit_jvp_regression(
                    occupation,
                    state,
                    network,
                    dt_s,
                )
                maximum_implicit_jvp_relative = max(
                    maximum_implicit_jvp_relative,
                    implicit_jvp_relative,
                )

            full_number_relative = relative_number_residual(result.full_action)
            boundary_number_relative = relative_number_residual(
                result.boundary_action
            )
            full_norm = float(np.linalg.norm(result.full_action.occupation_action))
            boundary_norm = float(
                np.linalg.norm(result.boundary_action.occupation_action)
            )
            boundary_fraction = boundary_norm / (full_norm + 1e-300)

            policy_rows.append(
                {
                    "scenario": spec["name"],
                    "model": spec["model"],
                    "snapshot_index": spec["snapshot_index"],
                    "bianchi_type": snapshot.bianchi_type,
                    "chart_id": snapshot.chart_id,
                    "tau": snapshot.tau,
                    "H_s_inv": snapshot.H_s_inv,
                    "beta_norm": state.policy.beta_norm,
                    "normalized_shear_squared": (
                        state.policy.normalized_shear_squared
                    ),
                    "selected_policy": state.policy.policy,
                    "ell_max": state.policy.ell_max,
                    "lebedev_order": ADAPTIVE_GRID_ORDER[state.policy.ell_max],
                    "angle_count": state.grid.n_angle,
                    "minimum_weight": float(np.min(state.grid.weights)),
                    "gram_residual": state.grid.gram_residual,
                    "red_directional_crossing": (
                        state.policy.red_directional_crossing
                    ),
                    "blue_directional_crossing": (
                        state.policy.blue_directional_crossing
                    ),
                    "characteristic_crossing": (
                        state.policy.characteristic_crossing
                    ),
                    "frame_roundtrip_residual": (
                        state.frame_roundtrip_residual
                    ),
                    "R_H_over_H_min": float(
                        np.min(state.R_hydrogen_s_inv) / snapshot.H_s_inv
                    ),
                    "R_H_over_H_max": float(
                        np.max(state.R_hydrogen_s_inv) / snapshot.H_s_inv
                    ),
                    "policy_match": (
                        state.policy.policy == spec["expected_policy"]
                        and state.policy.ell_max == spec["expected_ell_max"]
                    ),
                }
            )
            operator_rows.append(
                {
                    "scenario": spec["name"],
                    "minimum_occupation": float(np.min(occupation)),
                    "maximum_occupation": float(np.max(occupation)),
                    "action_infinity_norm_s_inv": float(
                        np.max(np.abs(result.full_action.occupation_action))
                    ),
                    "gross_action_scale": result.full_action.gross_action_scale,
                    "BE_action_relative": be_relative,
                    "number_residual": result.full_action.number_residual,
                    "number_residual_relative": full_number_relative,
                    "entropy_free_energy_production": (
                        result.full_action.entropy_production
                    ),
                    "boundary_action_norm": boundary_norm,
                    "boundary_to_full_action_norm": boundary_fraction,
                    "boundary_number_residual": (
                        result.boundary_action.number_residual
                    ),
                    "boundary_number_residual_relative": (
                        boundary_number_relative
                    ),
                    "four_force_hydrogen_residual": (
                        result.four_force_hydrogen_residual
                    ),
                    "four_force_normal_residual": (
                        result.four_force_normal_residual
                    ),
                }
            )
            implicit_rows.append(
                {
                    "scenario": spec["name"],
                    "explicit_critical_dt_s": explicit_critical_dt,
                    "implicit_dt_s": dt_s,
                    "explicit_trial_minimum": (
                        implicit.explicit_trial_minimum
                    ),
                    "implicit_minimum": implicit.minimum_occupation,
                    "converged": implicit.converged,
                    "newton_iterations": implicit.newton_iterations,
                    "total_gmres_iterations": (
                        implicit.total_gmres_iterations
                    ),
                    "residual_relative": implicit.residual_relative,
                    "number_before": implicit.number_before,
                    "number_after": implicit.number_after,
                    "number_relative_change": (
                        implicit.number_relative_change
                    ),
                    "free_energy_before": implicit.free_energy_before,
                    "free_energy_after": implicit.free_energy_after,
                    "free_energy_change": implicit.free_energy_change,
                }
            )
            jacobian_rows.append(
                {
                    "scenario": spec["name"],
                    "test": "collision_action_exact_JVP",
                    "central_difference_epsilon": 1e-4,
                    "relative_residual": jvp_relative,
                    "number_left_null_relative": jvp_number_relative,
                }
            )
            if math.isfinite(implicit_jvp_relative):
                jacobian_rows.append(
                    {
                        "scenario": spec["name"],
                        "test": "log_backward_euler_residual_JVP",
                        "central_difference_epsilon": 1e-4,
                        "relative_residual": implicit_jvp_relative,
                        "number_left_null_relative": "",
                    }
                )

            for group, value in result.boundary_group_number_action.items():
                edge_rows.append(
                    {
                        "scenario": spec["name"],
                        "group": group,
                        "boundary_number_action": value,
                    }
                )

            prefix = spec["name"]
            evidence[f"{prefix}_directions_hydrogen"] = state.direction_hydrogen
            evidence[f"{prefix}_directions_normal"] = state.direction_normal
            evidence[f"{prefix}_weights"] = state.grid.weights
            evidence[f"{prefix}_doppler_factor"] = state.doppler_factor
            evidence[f"{prefix}_R_hydrogen_s_inv"] = state.R_hydrogen_s_inv
            evidence[f"{prefix}_red_speed_s_inv"] = state.red_speed_s_inv
            evidence[f"{prefix}_blue_speed_s_inv"] = state.blue_speed_s_inv
            evidence[f"{prefix}_occupation"] = occupation
            evidence[f"{prefix}_full_action_s_inv"] = (
                result.full_action.occupation_action
            )
            evidence[f"{prefix}_boundary_action_s_inv"] = (
                result.boundary_action.occupation_action
            )
            evidence[f"{prefix}_jvp_exact_s_inv"] = (
                jvp.occupation_action_jvp
            )
            evidence[f"{prefix}_jvp_finite_difference_s_inv"] = jvp_fd
            evidence[f"{prefix}_implicit_occupation"] = implicit.occupation
            evidence[f"{prefix}_Q_gamma_hydrogen"] = result.full_action.Q_gamma
            evidence[f"{prefix}_Q_atom_hydrogen"] = result.full_action.Q_atom
            evidence[f"{prefix}_Q_gamma_normal"] = result.Q_gamma_normal
            evidence[f"{prefix}_Q_atom_normal"] = result.Q_atom_normal
            if implicit_jvp_exact.size:
                evidence[f"{prefix}_implicit_jvp_exact"] = implicit_jvp_exact
                evidence[f"{prefix}_implicit_jvp_finite_difference"] = (
                    implicit_jvp_fd
                )

            prepared_records.append((snapshot, state))
            maximum_be_relative = max(maximum_be_relative, be_relative)
            maximum_number_relative = max(
                maximum_number_relative,
                full_number_relative,
            )
            maximum_boundary_number_relative = max(
                maximum_boundary_number_relative,
                boundary_number_relative,
            )
            maximum_jvp_relative = max(maximum_jvp_relative, jvp_relative)
            maximum_jvp_number_relative = max(
                maximum_jvp_number_relative,
                jvp_number_relative,
            )
            maximum_four_force_hydrogen = max(
                maximum_four_force_hydrogen,
                result.four_force_hydrogen_residual,
            )
            maximum_four_force_normal = max(
                maximum_four_force_normal,
                result.four_force_normal_residual,
            )
            maximum_frame_roundtrip = max(
                maximum_frame_roundtrip,
                state.frame_roundtrip_residual,
            )
            minimum_boundary_fraction = min(
                minimum_boundary_fraction,
                boundary_fraction,
            )
            maximum_gram_residual = max(
                maximum_gram_residual,
                state.grid.gram_residual,
            )
            minimum_grid_weight = min(
                minimum_grid_weight,
                float(np.min(state.grid.weights)),
            )
            maximum_implicit_residual = max(
                maximum_implicit_residual,
                implicit.residual_relative,
            )
            maximum_implicit_number_change = max(
                maximum_implicit_number_change,
                implicit.number_relative_change,
            )
            minimum_implicit_occupation = min(
                minimum_implicit_occupation,
                implicit.minimum_occupation,
            )
            maximum_explicit_trial_minimum = max(
                maximum_explicit_trial_minimum,
                implicit.explicit_trial_minimum,
            )
            maximum_entropy_production = max(
                maximum_entropy_production,
                result.full_action.entropy_production,
            )
            maximum_free_energy_change = max(
                maximum_free_energy_change,
                implicit.free_energy_change,
            )

        # Geometry firewall: force one common hydrogen-frame grid and field.
        firewall_actions = []
        firewall_specs = (
            ("Bianchi_II_large_shear", 70),
            ("Bianchi_VI_h_tilted_large_shear", 100),
            ("Bianchi_VI_minus_1_over_9_exceptional", 100),
        )
        common_occupation = None
        for model, index in firewall_specs:
            snapshot = snapshot_record(snapshot_data, model, index)
            state = runtime.prepare(snapshot, force_ell_max=12)
            if common_occupation is None:
                base = be_family(network, 0.25)
                angular = 1.0 + 0.08 * state.grid.directions[:, 2]
                common_occupation = base[:, None] * angular[None, :]
            firewall_actions.append(
                runtime.evaluate(
                    state,
                    common_occupation,
                ).full_action.occupation_action
            )

    firewall_stack = np.asarray(firewall_actions)
    geometry_collision_difference = float(
        np.max(np.abs(firewall_stack - firewall_stack[0]))
    )
    evidence["geometry_firewall_actions"] = firewall_stack

    precision_rows = high_precision_checks()
    maximum_high_precision_residual = max(
        float(row["relative_residual"]) for row in precision_rows
    )

    hard_results = {
        "maximum_BE_action_relative": maximum_be_relative,
        "maximum_number_residual_relative": maximum_number_relative,
        "maximum_boundary_number_residual_relative": (
            maximum_boundary_number_relative
        ),
        "maximum_entropy_free_energy_production": maximum_entropy_production,
        "minimum_boundary_to_full_action_norm": minimum_boundary_fraction,
        "maximum_collision_JVP_relative": maximum_jvp_relative,
        "maximum_collision_JVP_number_left_null_relative": (
            maximum_jvp_number_relative
        ),
        "maximum_implicit_residual_JVP_relative": (
            maximum_implicit_jvp_relative
        ),
        "minimum_grid_weight": minimum_grid_weight,
        "maximum_harmonic_gram_residual": maximum_gram_residual,
        "maximum_frame_roundtrip_residual": maximum_frame_roundtrip,
        "maximum_implicit_residual_relative": maximum_implicit_residual,
        "maximum_implicit_number_relative_change": (
            maximum_implicit_number_change
        ),
        "minimum_implicit_occupation": minimum_implicit_occupation,
        "maximum_explicit_trial_minimum": maximum_explicit_trial_minimum,
        "maximum_free_energy_change": maximum_free_energy_change,
        "maximum_four_force_hydrogen_residual": (
            maximum_four_force_hydrogen
        ),
        "maximum_four_force_normal_residual": maximum_four_force_normal,
        "geometry_collision_action_difference": (
            geometry_collision_difference
        ),
        "maximum_mpmath_80dps_reference_residual": (
            maximum_high_precision_residual
        ),
    }

    hard_gates = {
        "runtime_BackgroundSnapshot_connection": all(
            row["policy_match"] for row in policy_rows
        ),
        "adaptive_L12_L20_L24_policy": {
            (row["selected_policy"], int(row["ell_max"]))
            for row in policy_rows
        }
        == {
            ("finite_or_mixed_tilt", 12),
            ("nonlinear_even_shear", 20),
            ("directional_crossing", 24),
        },
        "positive_weight_grids": minimum_grid_weight > 0.0,
        "harmonic_analysis_exactness": maximum_gram_residual < 5e-12,
        "frame_roundtrip": maximum_frame_roundtrip < 2e-13,
        "Bose_Einstein_null": maximum_be_relative < 2e-14,
        "photon_number": maximum_number_relative < 1e-13,
        "boundary_edge_number": maximum_boundary_number_relative < 1e-13,
        "stimulated_boundary_edge_active": minimum_boundary_fraction > 1e-8,
        "entropy_free_energy_dissipation": maximum_entropy_production <= 0.0,
        "analytic_collision_JVP": maximum_jvp_relative < 2e-8,
        "collision_JVP_number_left_null": (
            maximum_jvp_number_relative < 1e-12
        ),
        "analytic_implicit_residual_JVP": (
            maximum_implicit_jvp_relative < 2e-8
        ),
        "implicit_convergence": all(
            row["converged"] for row in implicit_rows
        )
        and maximum_implicit_residual < 5e-10,
        "implicit_positivity": minimum_implicit_occupation > 0.0,
        "explicit_stress_fails_positivity": all(
            row["explicit_trial_minimum"] < 0.0 for row in implicit_rows
        ),
        "implicit_number": maximum_implicit_number_change < 5e-12,
        "implicit_free_energy": maximum_free_energy_change < 0.0,
        "total_four_force_hydrogen": maximum_four_force_hydrogen < 1e-12,
        "total_four_force_normal": maximum_four_force_normal < 1e-12,
        "local_microphysics_firewall": geometry_collision_difference == 0.0,
        "independent_high_precision_reference": (
            maximum_high_precision_residual < 1e-60
        ),
    }
    hard_gates = {key: bool(value) for key, value in hard_gates.items()}
    if not all(hard_gates.values()):
        failed = [key for key, value in hard_gates.items() if not value]
        raise RuntimeError(f"PR-02 hard gates failed: {failed}")

    write_csv(ARTIFACT / "runtime_policy_summary.csv", policy_rows)
    write_csv(ARTIFACT / "operator_gate_summary.csv", operator_rows)
    write_csv(ARTIFACT / "implicit_update_summary.csv", implicit_rows)
    write_csv(ARTIFACT / "jacobian_regression.csv", jacobian_rows)
    write_csv(ARTIFACT / "edge_flux_ledger.csv", edge_rows)
    write_csv(ARTIFACT / "independent_reference_checks.csv", precision_rows)
    np.savez_compressed(
        ARTIFACT / "nonlinear_bose_runtime_evidence.npz",
        **evidence,
    )
    np.savez_compressed(DATA_OUT, **evidence)

    formalism = r'''# PR-02 nonlinear anisotropic Bose collision production integration

## Scope and conventions

Metric signature is \((-,+,+,+)\). Physical constants are not set to one;
`BackgroundSnapshot` rates are in s\(^{-1}\), and the Ly-alpha boundary
adapter retains \(c\), \(h\), and \(k_B\) in the surrounding physical
model. This PR closes the scalar collision substep only. It does not yet replace
the provisional scalar 2p pole+crossed amplitude; that is PR-03.

## Frequency-angle state and exact BE family

For frequency cell \(i\), hydrogen-frame angular node \(q\), mode measure
\(g_i>0\), and equilibrium measure \(\pi_i>0\), define

\[
 z_i=\frac{\pi_i}{g_i},\qquad
 \phi_{iq}=\frac{f_{iq}}{z_i(1+f_{iq})}.
\]

Every isotropic Bose-Einstein activity family

\[
 f_i^{\rm BE}=\frac{a z_i}{1-a z_i}
\]

has constant \(\phi=a\) and is an exact null of the discrete pair action.

## Activity-reference-subtracted edge flux

Let \(K_{ij}^{(\ell)}=K_{ji}^{(\ell)}\) be the inherited v0.47
conductance moments and let \(\mathcal K_{ij}\star\) denote their zonal
harmonic convolution. A common angular activity

\[
 a_\star=\frac{1}{N_\nu}
 \sum_i\sum_q w_q\phi_{iq}
\]

is subtracted before convolution. With

\[
 \Delta_i=(1+f_i)(\phi_i-a_\star),
\]

the pair contribution is evaluated as

\[
 C^N_i=(1+f_i)
 \left[\mathcal K_{ij}\star\Delta_j
 -(\phi_i-a_\star)
  \mathcal K_{ij}\star(1+f_j)\right],
\]

plus the symmetric \(j\)-equation. This is algebraically identical to the
stimulated gain-minus-loss form, but avoids subtracting two large nearly equal
terms near equilibrium. Pair symmetry closes the discrete photon-number left
null.

The boundary-only diagnostic retains exactly the interior-to-near/far pairs and
sets same-cell terms to zero. Exterior-to-exterior collisions remain in the
Liouville/boundary module, as locked in v0.47.

## Positive harmonic-exact angular grids

The runtime policies are fixed to

* \(L=12\): finite or mixed tilt, SciPy Lebedev order 29, 302 nodes;
* \(L=20\): nonlinear even shear, order 41, 590 nodes;
* \(L=24\): directional red/blue crossing, order 53, 974 nodes.

All weights are positive. The discrete analysis matrices satisfy
\(\|AS-I\|_\infty<5\times10^{-12}\) in the released evidence. The order
and point-count mapping follows the SciPy `lebedev_rule` registry.

## BackgroundSnapshot runtime adapter

The grid directions are hydrogen-frame directions \(e_H\). They are inverse
aberrated to \(e_n\), passed through the PR-01 normal-frame characteristic,
and mapped back with the exact finite-tilt adapter. Geometry determines
\(\mathcal D_H\), \(R_H=D_0\ln\nu_H\), direction flow, and red/blue
boundary speeds. It is not an argument of the local conductance/amplitude
operator. A common forced-grid field therefore produces bitwise-identical local
collision actions for Bianchi II, tilted VI_h, and exceptional VI_-1/9.

## Exact JVP

For a perturbation \(\delta f\),

\[
 \delta\phi_i=
 \frac{\delta f_i}{z_i(1+f_i)^2},
 \qquad
 \delta a_\star=
 \frac{1}{N_\nu}\sum_{iq}w_q\delta\phi_{iq},
\]

and the stable derivative of \(\Delta_i\) is

\[
 \boxed{
 \delta\Delta_i=
 \frac{\delta f_i}{z_i}
 -a_\star\delta f_i
 -(1+f_i)\delta a_\star
 }.
\]

The production JVP differentiates each harmonic convolution analytically. No
finite-difference Jacobian enters Newton-GMRES. Central differences are retained
only as regression evidence.

## Positivity-preserving implicit collision update

The backward-Euler residual is

\[
 \mathcal R(f^{n+1})=
 f^{n+1}-f^n-\Delta t\,C[f^{n+1}]=0.
\]

Newton variables are \(u=\ln f\), so every accepted iterate has
\(f=e^u>0\). The matrix-free action is

\[
 D_u\mathcal R[\delta u]
 =f\,\delta u
 -\Delta t\,DC[f][f\,\delta u].
\]

No clipping and no post-step number renormalization are used. The released
stress timestep is 1.02 times the first explicit-Euler positivity limit; explicit
Euler is negative in every lane while the converged implicit fields remain
strictly positive. Number conservation follows from the collision left null and
residual closure. Discrete free-energy decrease is tested for the released
states; it is not asserted here as a theorem for arbitrary timestep and field.

## Thermodynamic and four-force ledgers

The number and free-energy functionals are

\[
 N_\gamma=\sum_{iq}g_iw_q f_{iq},
\]

\[
 \mathcal F=\sum_{iq}g_iw_q
 \left[f\ln f-(1+f)\ln(1+f)-f\ln z_i\right].
\]

The reported `entropy_free_energy_production` is

\[
 \dot{\mathcal F}=\sum_{iq}w_q
 \left[\ln\frac{f}{1+f}-\ln z_i\right]C^N_{iq}
 \le 0.
\]

Photon and atom four-force contributions are accumulated from the same event
with opposite sign and then Lorentz-transformed independently from the hydrogen
tetrad to the normal tetrad. Their sum vanishes in both frames.

## Independent references and limitations

The high-precision receipt uses 80-digit `mpmath` checks for the stable activity
derivative, Lorentz inverse, and BE pair null because no Wolfram or Precise
Special Functions connector was exposed in this runtime. The full JVP is also
checked against central differences on every production lane.

Numerical design references used for context:

1. SciPy documentation for `scipy.integrate.lebedev_rule` and its order/node registry.
2. Markowich and Pareschi, *Fast conservative and entropic numerical methods for the Boson Boltzmann equation*, arXiv:1009.2748.
3. Hu, Li, and Pareschi, *Asymptotic-preserving exponential methods for the quantum Boltzmann equation with high-order accuracy*, arXiv:1310.7658.
4. Zhang, Shen, and Hu, *SAV-based entropy-dissipative schemes for a class of kinetic equations*, arXiv:2408.16105.

The released stress occupations are deterministic collision-substep regression
states built from actual BackgroundSnapshot characteristics. They are not
claimed to be solutions of the coupled Liouville plus recombination system.
'''
    (ARTIFACT / "PR02_NONLINEAR_BOSE_RUNTIME_FORMALISM.md").write_text(
        formalism,
        encoding="utf-8",
    )

    ledger = {
        "classification": "PR02_NONLINEAR_ANISOTROPIC_BOSE_PRODUCTION",
        "stage": "PR-02",
        "status": "PASS_PR02_COMPLETE",
        "source": {
            "collision_data": str(COLLISION_DATA.relative_to(ROOT)),
            "collision_data_sha256": sha256(COLLISION_DATA),
            "background_snapshot_data": str(SNAPSHOT_DATA.relative_to(ROOT)),
            "background_snapshot_data_sha256": sha256(SNAPSHOT_DATA),
            "inherited_collision_artifact": "PR01B1-B3B3B1/v0.47",
            "inherited_background_artifact": "PR01C/v0.48",
        },
        "scenarios": policy_rows,
        "hard_results": hard_results,
        "hard_gate_status": hard_gates,
        "decision": {
            "PR02": "PASS",
            "PR02_status": "COMPLETE",
            "local_collision_microphysics": "UNCHANGED",
            "next_PR": "PR-03 full scalar COM-KHW amplitude",
        },
        "limitations": [
            "The stress occupations are collision-substep regression fields, not solutions of the coupled Liouville plus recombination system.",
            "The amplitude is still the provisional unresolved scalar 2p pole+crossed model; full bound, continuum, seagull and interference terms are PR-03.",
            "Exterior-exterior collisions remain assigned to the boundary/Liouville module as locked in v0.47.",
            "The total atom four-force is the same-event counterterm of the inherited scalar collision event; PR-03 upgrades the physical amplitude, not this conservation architecture.",
            "This stage exercises three adaptive runtime lanes, not the all-11 automated sweep assigned to PR-10.",
        ],
        "next_stage": {
            "name": "PR-03 full scalar COM-KHW amplitude",
            "tasks": [
                "Replace the provisional unresolved scalar 2p pole+crossed amplitude by the complete scalar bound+continuum COM-KHW construction.",
                "Include seagull and interference terms with explicit gauge and reciprocity audits.",
                "Regenerate pair conductance moments and rerun PR-01/PR-02 conservation, BE, entropy and implicit-update regressions.",
            ],
        },
    }
    (ARTIFACT / "PR02_ledger.json").write_text(
        json.dumps(ledger, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )

    verify_code = r'''from pathlib import Path
import csv
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
ledger = json.loads((HERE / "PR02_ledger.json").read_text())
assert ledger["status"] == "PASS_PR02_COMPLETE"
assert all(ledger["hard_gate_status"].values())

policies = list(csv.DictReader((HERE / "runtime_policy_summary.csv").open()))
assert {(row["selected_policy"], int(row["ell_max"])) for row in policies} == {
    ("finite_or_mixed_tilt", 12),
    ("nonlinear_even_shear", 20),
    ("directional_crossing", 24),
}
assert all(float(row["minimum_weight"]) > 0 for row in policies)

implicit = list(csv.DictReader((HERE / "implicit_update_summary.csv").open()))
assert all(float(row["explicit_trial_minimum"]) < 0 for row in implicit)
assert all(float(row["implicit_minimum"]) > 0 for row in implicit)
assert all(float(row["free_energy_change"]) < 0 for row in implicit)

data = np.load(HERE / "nonlinear_bose_runtime_evidence.npz")
assert set(data["scenario_names"].tolist()) == {
    "finite_or_mixed_tilt",
    "nonlinear_even_shear",
    "directional_crossing",
}

for line in (HERE / "MANIFEST_SHA256.txt").read_text().splitlines():
    expected, name = line.split("  ", 1)
    actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    assert actual == expected, name

print("PR-02 nonlinear Bose production runtime: PASS")
'''
    (ARTIFACT / "verify_PR02.py").write_text(verify_code, encoding="utf-8")

    readme = f'''# Full Bianchi-HyRec PR-02 v0.49

This artifact connects the nonlinear stimulated Bose collision network to
runtime `BackgroundSnapshot` states and closes the positive-grid, exact-JVP,
implicit-positivity, BE, number, free-energy and same-event four-force gates.

- maximum BE action relative residual: {maximum_be_relative:.6e}
- maximum number residual relative: {maximum_number_relative:.6e}
- maximum collision JVP residual: {maximum_jvp_relative:.6e}
- maximum implicit residual: {maximum_implicit_residual:.6e}
- minimum implicit occupation: {minimum_implicit_occupation:.6e}
- maximum free-energy change: {maximum_free_energy_change:.6e}
- geometry-to-microphysics action difference: {geometry_collision_difference:.6e}

Status: PR-02 COMPLETE. Next: PR-03 full scalar COM-KHW amplitude.
'''
    (ARTIFACT / "README.md").write_text(readme, encoding="utf-8")

    manifest(ARTIFACT)
    subprocess.run(
        [sys.executable, str(ARTIFACT / "verify_PR02.py")],
        check=True,
        cwd=ARTIFACT,
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
                "hard_results": hard_results,
                "hard_gates": hard_gates,
                "bundle_sha256": sha256(BUNDLE),
            },
            indent=2,
            default=json_default,
        )
    )


if __name__ == "__main__":
    main()

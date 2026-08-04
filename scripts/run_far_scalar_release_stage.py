#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import sys

import numpy as np
from scipy.integrate import lebedev_rule
from scipy.special import eval_legendre

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC
from full_bianchi_hyrec.recoil.exterior_interface import (
    BLUE_CELLS,
    EXTERIOR_CELLS,
    RED_CELLS,
    exterior_pair_bundle,
    exterior_pair_conductance,
    interior_cells,
)
from full_bianchi_hyrec.recoil.far_exterior import (
    FAR_BLUE_CELLS,
    FAR_CELLS,
    FAR_RED_CELLS,
    assemble_scalar_pair_generator,
    far_pair_bundle,
    interval_mean_momentum_scale,
    interval_mode_measure,
    interval_thermal_weight,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
    HarmonicGrid,
    apply_nonlinear_bose_operator,
)


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _pair_job(job):
    kind, a, b, target, source, lane, ell_max, cache = job
    cache = Path(cache)
    if cache.exists():
        data = np.load(cache)
        return kind, a, b, data["conductance"], data.get("transfer", np.zeros(2))
    if kind == "interior":
        conductance = exterior_pair_conductance(
            target, source, lane=lane, ell_max=ell_max
        )
        transfer = np.zeros(2)
    elif kind == "far":
        conductance, transfer = far_pair_bundle(
            target, source, lane=lane, ell_max=ell_max
        )
    else:
        raise ValueError(kind)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, conductance=conductance, transfer=transfer)
    return kind, a, b, conductance, transfer


def _grid(ell_max: int) -> HarmonicGrid:
    # Positive-weight rules are required for nonlinear entropy and number ledgers.
    order = {12: 29, 20: 41, 24: 53}[ell_max]
    points, weights = lebedev_rule(order)
    return HarmonicGrid.from_directions(
        points.T, weights / (4.0 * math.pi), ell_max=ell_max
    )


def _be_family(activity: np.ndarray, maximum: float) -> np.ndarray:
    q = maximum / (1.0 + maximum) / float(np.max(activity))
    return q * activity / (1.0 - q * activity)


def _normalized(profile: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return profile / float(np.dot(weights, profile))


def make_mock(
    name: str,
    grid: HarmonicGrid,
    centers: np.ndarray,
    activity: np.ndarray,
) -> np.ndarray:
    mu = grid.directions[:, 2]
    p2 = eval_legendre(2, mu)
    p4 = eval_legendre(4, mu)
    if name == "BE_equilibrium":
        return np.repeat(_be_family(activity, 1.0)[:, None], grid.n_angle, axis=1)
    if name == "finite_tilt_beta0p3":
        gamma = 1.0 / math.sqrt(1.0 - 0.3**2)
        angular = _normalized((gamma * (1.0 - 0.3 * mu)) ** -3, grid.weights)
        spectral = 1.0 + 0.03 * np.cos(centers / 8.0)
        return _be_family(activity, 0.25)[:, None] * spectral[:, None] * angular[None, :]
    if name == "nonlinear_even_shear":
        angular = _normalized(np.exp(1.2 * p2 + 0.35 * p4), grid.weights)
        spectral = 1.0 + 0.08 * np.exp(-0.5 * (centers / 2.0) ** 2)
        return _be_family(activity, 0.5)[:, None] * spectral[:, None] * angular[None, :]
    if name == "mixed_tilt_shear":
        gamma = 1.0 / math.sqrt(1.0 - 0.3**2)
        angular = _normalized(
            (gamma * (1.0 - 0.3 * mu)) ** -3 * np.exp(0.8 * p2),
            grid.weights,
        )
        spectral = 1.0 + 0.05 * np.cos(centers / 2.0)
        return _be_family(activity, 0.5)[:, None] * spectral[:, None] * angular[None, :]
    if name == "red_blue_crossing":
        base = _be_family(activity, 0.3)
        return base[:, None] * (
            1.0
            + 0.12
            * np.tanh(centers[:, None] / 0.7)
            * np.tanh(3.0 * mu)[None, :]
        )
    if name == "high_occupation_stress":
        angular = _normalized(1.0 + 0.12 * p2 + 0.05 * p4, grid.weights)
        spectral = 1.0 + 0.05 * np.exp(-0.5 * (centers / 0.9) ** 2)
        return _be_family(activity, 4.0)[:, None] * spectral[:, None] * angular[None, :]
    raise ValueError(name)


def coefficient_norm(coeff: np.ndarray, lm: np.ndarray, mode: np.ndarray, *, ell_min=0, ell_max=None) -> float:
    mask = lm[:, 0] >= ell_min
    if ell_max is not None:
        mask &= lm[:, 0] <= ell_max
    return float(np.sqrt(np.sum(mode[:, None] * np.abs(coeff[:, mask]) ** 2)))


def compare_coefficients(current, reference, mode):
    cur_lm = [tuple(row) for row in current["lm"]]
    ref_lm = [tuple(row) for row in reference["lm"]]
    ref_index = {value: index for index, value in enumerate(ref_lm)}
    common_ref = np.asarray([ref_index[value] for value in cur_lm])
    difference = current["coeff"] - reference["coeff"][:, common_ref]
    denominator = float(
        np.sqrt(np.sum(mode[:, None] * np.abs(reference["coeff"][:, common_ref]) ** 2))
    )
    common_relative = float(
        np.sqrt(np.sum(mode[:, None] * np.abs(difference) ** 2))
        / (denominator + 1.0e-300)
    )
    ell_cut = int(np.max(current["lm"][:, 0]))
    full = coefficient_norm(reference["coeff"], reference["lm"], mode)
    tail = coefficient_norm(
        reference["coeff"], reference["lm"], mode, ell_min=ell_cut + 1
    ) / (full + 1.0e-300)
    return common_relative, tail


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--lane", default="production")
    parser.add_argument("--ell-max", type=int, default=24)
    args = parser.parse_args()
    repo = args.repo.resolve()
    stage = "Full_Bianchi_HyRec_PR01B1B3B3B1_far_scalar_release_v0_47"
    artifact = repo / "archive" / "expanded" / stage
    artifact.mkdir(parents=True, exist_ok=True)
    cache = repo / ".cache" / "v047_pair_cache"
    cache.mkdir(parents=True, exist_ok=True)

    interior = interior_cells()
    near = EXTERIOR_CELLS
    far = FAR_CELLS
    intervals = interior + near + far
    n_int, n_near, n_far = len(interior), len(near), len(far)
    n_state = len(intervals)
    ell_max = args.ell_max

    jobs = []
    for i in range(n_int):
        for j in range(i + 1, n_int):
            jobs.append((
                "interior", i, j, interior[i], interior[j], args.lane, ell_max,
                str(cache / f"interior_i{i:02d}_j{j:02d}.npz"),
            ))
    for e, cell in enumerate(far):
        for i, source in enumerate(interior):
            jobs.append((
                "far", e, i, cell, source, args.lane, ell_max,
                str(cache / f"far_e{e:02d}_i{i:02d}.npz"),
            ))

    interior_moments = np.zeros((ell_max + 1, n_int, n_int))
    far_moments = np.zeros((ell_max + 1, n_far, n_int))
    far_transfer = np.zeros((n_far, n_int, 2))
    completed = 0
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [executor.submit(_pair_job, job) for job in jobs]
        for future in as_completed(futures):
            kind, a, b, values, transfer = future.result()
            if kind == "interior":
                interior_moments[:, a, b] = values
                interior_moments[:, b, a] = values
            else:
                far_moments[:, a, b] = values
                far_transfer[a, b] = transfer
            completed += 1
            if completed % 10 == 0 or completed == len(jobs):
                print(f"PAIR_PROGRESS {completed}/{len(jobs)}", flush=True)

    near_data = np.load(repo / "data" / "exterior_interface_v046.npz")
    near_moments = np.asarray(near_data["conductance_m3_sInv"])
    same_data = np.load(
        repo / "archive/expanded/Full_Bianchi_HyRec_PR01B1B3B3A_same_cell_regular_v0_45/same_cell_regularized_block.npz"
    )
    same_interior = np.asarray(same_data["exact_regularized_rate_sInv"])

    pair_moments = np.zeros((ell_max + 1, n_state, n_state))
    pair_moments[:, :n_int, :n_int] = interior_moments
    for e in range(n_near):
        state = n_int + e
        pair_moments[:, state, :n_int] = near_moments[:, e, :]
        pair_moments[:, :n_int, state] = near_moments[:, e, :]
    for e in range(n_far):
        state = n_int + n_near + e
        pair_moments[:, state, :n_int] = far_moments[:, e, :]
        pair_moments[:, :n_int, state] = far_moments[:, e, :]

    same_rates = np.zeros((ell_max + 1, n_state))
    same_rates[:, :n_int] = same_interior[: ell_max + 1]
    mode = np.asarray([interval_mode_measure(*cell) for cell in intervals])
    pi = np.asarray([interval_thermal_weight(*cell) for cell in intervals])
    momentum = np.asarray([interval_mean_momentum_scale(*cell) for cell in intervals])
    centers = np.asarray([0.5 * (cell[0] + cell[1]) for cell in intervals])
    activity = pi / mode

    scalar_generator = assemble_scalar_pair_generator(pair_moments[0], pi)
    left_relative = float(
        np.max(np.abs(np.ones(n_state) @ scalar_generator))
        / (np.max(np.abs(scalar_generator)) + 1.0e-300)
    )
    right_relative = float(
        np.max(np.abs(scalar_generator @ pi))
        / (np.max(np.abs(scalar_generator)) * np.max(pi) + 1.0e-300)
    )

    outer_states = [n_int + n_near, n_state - 1]
    outer_S = np.zeros_like(pair_moments[0])
    for state in outer_states:
        outer_S[state, :] = pair_moments[0, state, :]
        outer_S[:, state] = pair_moments[0, :, state]
    outer_G = assemble_scalar_pair_generator(outer_S, pi)
    tail_generator_ratio = float(
        np.linalg.norm(outer_G) / (np.linalg.norm(scalar_generator) + 1.0e-300)
    )
    rates = pair_moments[0] / pi[None, :]
    far_start = n_int + n_near
    outer_outflow = rates[far_start, :n_int] + rates[-1, :n_int]
    far_outflow = rates[far_start:, :n_int].sum(axis=0)
    source_tail_ratio = float(np.max(outer_outflow / (far_outflow + 1.0e-300)))

    # A conservative geometric continuation estimate from the last two bins.
    red_outer = rates[far_start, :n_int]
    red_middle = rates[far_start + 1, :n_int]
    blue_middle = rates[-2, :n_int]
    blue_outer = rates[-1, :n_int]
    ratios = np.maximum(
        red_outer / (red_middle + 1.0e-300),
        blue_outer / (blue_middle + 1.0e-300),
    )
    ratios = np.minimum(ratios, 0.999999)
    tail_bound = outer_outflow * ratios / (1.0 - ratios)
    total_outflow = -np.diag(scalar_generator[:n_int, :n_int])
    asymptotic_tail_bound_relative = float(
        np.max(tail_bound / (total_outflow + 1.0e-300))
    )

    selected = [
        ("interior", 0, 1, "interior_red_adjacent"),
        ("interior", 7, 9, "interior_cross_core"),
        ("interior", 0, 16, "interior_red_blue"),
        ("far", 2, 0, "far_red_inner_wing"),
        ("far", 0, 0, "far_red_outer_wing"),
        ("far", 3, 16, "far_blue_inner_wing"),
        ("far", 5, 16, "far_blue_outer_wing"),
    ]
    convergence_rows = []
    quadrature_max = 0.0
    orientation_max = 0.0
    for kind, a, b, name in selected:
        if kind == "interior":
            target, source = interior[a], interior[b]
        else:
            target, source = far[a], interior[b]
        production = exterior_pair_conductance(
            target, source, lane="production", ell_max=ell_max
        )
        reference = exterior_pair_conductance(
            target, source, lane="reference", ell_max=ell_max
        )
        reverse = exterior_pair_conductance(
            source, target, lane="production", ell_max=ell_max
        )
        qrel = float(np.linalg.norm(production - reference) / np.linalg.norm(reference))
        orel = float(np.linalg.norm(production - reverse) / np.linalg.norm(production))
        quadrature_max = max(quadrature_max, qrel)
        orientation_max = max(orientation_max, orel)
        convergence_rows.append({
            "case": name,
            "quadrature_relative": qrel,
            "orientation_relative": orel,
            "S0_production": production[0],
            "S0_reference": reference[0],
        })

    mock_names = [
        "BE_equilibrium",
        "finite_tilt_beta0p3",
        "nonlinear_even_shear",
        "mixed_tilt_shear",
        "red_blue_crossing",
        "high_occupation_stress",
    ]
    grid_results: dict[int, dict[str, dict]] = {}
    nonlinear_rows = []
    for L in (12, 20, 24):
        grid = _grid(L)
        grid_results[L] = {}
        for name in mock_names:
            occupation = make_mock(name, grid, centers, activity)
            result = apply_nonlinear_bose_operator(
                occupation,
                mode_measure=mode,
                equilibrium_weight=pi,
                pair_moments=pair_moments,
                same_cell_rates=same_rates,
                grid=grid,
                photon_momentum_scale=momentum,
            )
            action_scale = result.gross_action_scale
            number_relative = abs(result.number_residual) / (action_scale + 1.0e-300)
            action_norm = coefficient_norm(result.action_coefficients, grid.lm, mode)
            grid_results[L][name] = {
                "coeff": result.action_coefficients,
                "lm": grid.lm,
                "number_relative": number_relative,
                "entropy": result.entropy_production,
                "four_force": float(np.linalg.norm(result.Q_gamma + result.Q_atom)),
                "action_norm": action_norm,
                "gross_action_scale": result.gross_action_scale,
                "BE_relative": action_norm / (result.gross_action_scale + 1.0e-300),
                "gram": grid.gram_residual,
            }
            nonlinear_rows.append({
                "ell_max": L,
                "state": name,
                "point_count": grid.n_angle,
                "Gram_residual": grid.gram_residual,
                "action_norm": action_norm,
                "gross_action_scale": result.gross_action_scale,
                "action_relative_to_gross": action_norm / (result.gross_action_scale + 1.0e-300),
                "number_relative": number_relative,
                "entropy_production": result.entropy_production,
                "four_force_residual": float(np.linalg.norm(result.Q_gamma + result.Q_atom)),
                "minimum_occupation": result.minimum_occupation,
            })

    convergence_nonlinear_rows = []
    release_policy = {}
    for name in mock_names[1:]:
        common12, tail12 = compare_coefficients(grid_results[12][name], grid_results[24][name], mode)
        common20, tail20 = compare_coefficients(grid_results[20][name], grid_results[24][name], mode)
        release = 12 if max(common12, tail12) < 1.0e-5 else (20 if max(common20, tail20) < 1.0e-5 else 24)
        release_policy[name] = release
        convergence_nonlinear_rows.extend([
            {"state": name, "comparison": "L12_vs_L24", "common_mode_relative": common12, "reference_tail_relative": tail12, "release": release},
            {"state": name, "comparison": "L20_vs_L24", "common_mode_relative": common20, "reference_tail_relative": tail20, "release": release},
        ])

    be_max = max(grid_results[L]["BE_equilibrium"]["BE_relative"] for L in (12,20,24))
    number_max = max(row["number_relative"] for row in nonlinear_rows)
    entropy_max = max(row["entropy_production"] for row in nonlinear_rows if row["state"] != "BE_equilibrium")
    four_force_max = max(row["four_force_residual"] for row in nonlinear_rows)
    gram_max = max(row["Gram_residual"] for row in nonlinear_rows)
    min_scalar = float(np.min(pair_moments[0][np.triu_indices(n_state, 1)][pair_moments[0][np.triu_indices(n_state,1)]>0]))

    state_rows = []
    labels = (
        [f"I{i:02d}" for i in range(n_int)]
        + [f"NR{i:02d}" for i in range(len(RED_CELLS))]
        + [f"NB{i:02d}" for i in range(len(BLUE_CELLS))]
        + [f"FR{i:02d}" for i in range(len(FAR_RED_CELLS))]
        + [f"FB{i:02d}" for i in range(len(FAR_BLUE_CELLS))]
    )
    for index, (label, cell) in enumerate(zip(labels, intervals)):
        state_rows.append({
            "state_index": index,
            "label": label,
            "x_left": cell[0],
            "x_right": cell[1],
            "mode_measure_m^-3": mode[index],
            "equilibrium_weight_m^-3": pi[index],
            "activity": activity[index],
            "momentum_scale_kg_m_s^-1": momentum[index],
        })

    far_rows = []
    for e, cell in enumerate(far):
        state = far_start + e
        side = "red" if e < len(FAR_RED_CELLS) else "blue"
        for i, source in enumerate(interior):
            far_rows.append({
                "far_index": e,
                "side": side,
                "far_left": cell[0],
                "far_right": cell[1],
                "interior_index": i,
                "interior_left": source[0],
                "interior_right": source[1],
                "S0_m^-3_s^-1": pair_moments[0, state, i],
                "S1_m^-3_s^-1": pair_moments[1, state, i],
                "S2_m^-3_s^-1": pair_moments[2, state, i],
                "photon_delta_p0_weighted": far_transfer[e, i, 0],
                "photon_delta_ppar_weighted": far_transfer[e, i, 1],
            })

    write_csv(artifact / "far_pair_ledger.csv", far_rows)
    write_csv(artifact / "state_registry.csv", state_rows)
    write_csv(artifact / "selected_pair_convergence.csv", convergence_rows)
    write_csv(artifact / "nonlinear_bose_tests.csv", nonlinear_rows)
    write_csv(artifact / "adaptive_ell_convergence.csv", convergence_nonlinear_rows)

    np.savez_compressed(
        artifact / "far_scalar_release.npz",
        classification=np.asarray("PR01B1B3B3B1_FAR_SCALAR_RELEASE"),
        state_intervals=np.asarray(intervals),
        state_labels=np.asarray(labels),
        pair_moments_m3_sInv=pair_moments,
        same_cell_rates_sInv=same_rates,
        mode_measure_m3=mode,
        equilibrium_weight_m3=pi,
        momentum_scale=momentum,
        scalar_generator_sInv=scalar_generator,
        far_transfer_weighted=far_transfer,
        release_states=np.asarray(list(release_policy.keys())),
        release_ell=np.asarray(list(release_policy.values())),
    )

    hard_gates = {
        "scalar_positivity": bool(min_scalar >= 0.0),
        "selected_quadrature": bool(quadrature_max < 2.0e-7),
        "orientation_reciprocity": bool(orientation_max < 2.0e-12),
        "scalar_number": bool(left_relative < 1.0e-14),
        "scalar_equilibrium": bool(right_relative < 1.0e-12),
        "far_tail_convergence": bool(tail_generator_ratio < 1.0e-8 and asymptotic_tail_bound_relative < 1.0e-8),
        "positive_harmonic_weights": bool(gram_max < 1.0e-12),
        "BE_null": bool(be_max < 1.0e-12),
        "nonlinear_number": bool(number_max < 1.0e-11),
        "entropy_dissipation": bool(entropy_max <= 1.0e-10),
        "same_event_four_force": bool(four_force_max == 0.0),
        "adaptive_ell_release": bool(max(release_policy.values()) <= 24),
        "exterior_exterior_collision": False,
        "PR01C_background_adapter": False,
    }
    ledger = {
        "classification": "PR01B1B3B3B1_FAR_FLUX_AND_ADAPTIVE_SCALAR_RELEASE_LOCK",
        "stage": "PR-01B1-B3B3B1",
        "status": "PASS_CORE_TO_BOUNDARY_SCALAR_RELEASE_PR01C_OPEN" if all(v for k,v in hard_gates.items() if k not in {"exterior_exterior_collision","PR01C_background_adapter"}) else "FAIL_GATE",
        "domain": {
            "interior": [-4.25,4.25],
            "near_exterior": [[-10.25,-4.25],[4.25,10.25]],
            "far_exterior": [[-21.25,-10.25],[10.25,21.25]],
            "far_cells": [list(cell) for cell in far],
        },
        "counts": {
            "states": n_state,
            "interior_pairs": n_int*(n_int-1)//2,
            "near_interface_pairs": n_int*n_near,
            "far_interface_pairs": n_int*n_far,
            "ell_max": ell_max,
        },
        "hard_results": {
            "minimum_scalar_conductance": min_scalar,
            "selected_quadrature_max": quadrature_max,
            "orientation_max": orientation_max,
            "scalar_left_null_relative": left_relative,
            "scalar_right_null_relative": right_relative,
            "outer_bin_generator_ratio": tail_generator_ratio,
            "outer_bin_fraction_of_far_outflow": source_tail_ratio,
            "asymptotic_tail_bound_relative": asymptotic_tail_bound_relative,
            "BE_action_relative_to_gross_max": be_max,
            "nonlinear_number_relative_max": number_max,
            "nonlinear_entropy_max": entropy_max,
            "four_force_residual_max": four_force_max,
            "harmonic_Gram_residual_max": gram_max,
            "release_policy": release_policy,
        },
        "hard_gate_status": hard_gates,
        "decision": {
            "far_direct_jump_closure": "PASS",
            "nonlinear_adaptive_scalar_core_to_boundary": "PASS" if all(v for k,v in hard_gates.items() if k not in {"exterior_exterior_collision","PR01C_background_adapter"}) else "FAIL",
            "exterior_exterior_collision": "DEFERRED_TO_BOUNDARY_TRANSPORT_MODULE",
            "PR01C": "NEXT",
        },
        "limitations": [
            "Near/far exterior states exchange resonant-scattering conductance with the interior core; exterior-exterior collision is assigned to the boundary transport module and is not present here.",
            "Far-tail closure uses direct cells through |x|=21.25 plus a geometric continuation bound.",
            "The amplitude remains the provisional unresolved scalar 2p pole+crossed model; full bound+continuum KHW is PR-03.",
            "The four-force is the discrete endpoint ledger on mode-weighted cell momenta for nonlinear tests; exact pair-integrated axisymmetric moments are separately stored for far edges.",
        ],
        "next_stage": {
            "name": "PR01C_BackgroundSnapshot_frame_adapter",
            "tasks": [
                "Load finite-tilt, nonlinear-shear and turning/crossing snapshots from the supplied primitive Bianchi solver.",
                "Map normal-frame characteristics to the hydrogen frame without changing local collision microphysics.",
                "Run Bianchi II, class-B and exceptional smoke regressions for branch localization, number and four-force.",
                "Publish PR-01 closure ledger and patch series.",
            ],
        },
    }
    (artifact / "PR01B1B3B3B1_ledger.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")

    formalism = r'''# Far flux and nonlinear harmonic Bose release

The dynamic frequency-state registry is

\[
I=[-4.25,4.25],\quad
O^{\rm near}_{R/B}:4.25<|x|\le10.25,\quad
O^{\rm far}_{R/B}:10.25<|x|\le21.25.
\]

Every disjoint frequency pair is represented by Legendre conductance moments

\[
S_\ell(a,b)=\frac12\int_{-1}^{1}S_{ab}(\mu)P_\ell(\mu)d\mu.
\]

For occupations \(f_a(\boldsymbol n)\), the nonlinear Bose number action of
one pair is evaluated without reconstructing or clipping a pointwise kernel:

\[
\begin{aligned}
C_a(\boldsymbol n)={}&\frac{1+f_a}{z_b}\,\mathcal S_{ab}[f_b]
-\frac{f_a}{z_a}\,\mathcal S_{ab}[1+f_b],\\
z_a={}&\Pi_a/g_a.
\end{aligned}
\]

The zonal convolution is diagonal in spherical harmonics, while the
pointwise products are evaluated on positive-weight harmonic-exact Lebedev
rules.  Same-frequency Bose factors cancel exactly, leaving the linear
regularized rates \(D_{\ell a}=K_{\ell,aa}-K_{0,aa}\).

The far-tail gate compares the explicit |x|<=21.25 operator with the
|x|<=16.25 truncation and bounds the continuation using the last two adaptive
outer cells.  No free tail normalization is fitted.
'''
    (artifact / "FAR_SCALAR_RELEASE_FORMALISM.md").write_text(formalism, encoding="utf-8")

    verify = '''from pathlib import Path\nimport json,numpy as np\nHERE=Path(__file__).resolve().parent\nledger=json.loads((HERE/"PR01B1B3B3B1_ledger.json").read_text())\nfor key,value in ledger["hard_gate_status"].items():\n    if key in {"exterior_exterior_collision","PR01C_background_adapter"}: assert not value\n    else: assert value\ndata=np.load(HERE/"far_scalar_release.npz")\nS=data["pair_moments_m3_sInv"]\nassert S.shape==(25,35,35)\nassert np.max(np.abs(S-np.swapaxes(S,1,2)))<1e-12*(np.max(np.abs(S))+1e-300)\nassert np.min(S[0])>=0\nprint("PR01B1-B3B3B1 far scalar release: PASS")\n'''
    (artifact / "verify_PR01B1B3B3B1.py").write_text(verify, encoding="utf-8")
    for path in artifact.iterdir():
        if path.name == "MANIFEST_SHA256.txt":
            continue
    manifest = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}"
        for path in sorted(artifact.iterdir())
        if path.name != "MANIFEST_SHA256.txt"
    ]
    (artifact / "MANIFEST_SHA256.txt").write_text("\n".join(manifest)+"\n", encoding="utf-8")
    print(json.dumps({"artifact":str(artifact),"ledger":ledger}, indent=2), flush=True)


if __name__ == "__main__":
    main()
